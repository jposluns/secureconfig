#!/usr/bin/env python3
"""Parse and check the export lists.

THE FILES IN THIS REPOSITORY (export/FORMAT.md documents every format in full):

  export/public-allowlist.txt   copy and render lines: every path the export may publish.
  export/private-paths.txt      deny lines: every tracked path that stays private. It never
                                leaves this repository, so the public allowlist names public
                                paths only.
  export/public-markers.txt     ID<TAB>REGEX: generic shapes of private-record citations.
  export/public-exceptions.tsv  PATH<TAB>LINE<TAB>SHA256<TAB>REF<TAB>REASON: exact lines of
                                public files where a publishable marker is allowed.

THE PRIVATE LISTS are never committed. They are read, never written, from the directory given
with --private-dir, by default DEFAULT_PRIVATE_DIR, which this tool never creates:

  protected-terms.txt  one literal term per line, matched case-insensitively at word boundaries.
  private-markers.txt  ID<TAB>REGEX, as export/public-markers.txt.
  exceptions.tsv       as export/public-exceptions.tsv; REF may also be term:TERM.

Nothing read from a private list is printed: a finding in one names its file and line number
and the rule it breaks, and a pass prints counts and each list's SHA-256.

Every list is UTF-8 with LF line endings, no byte order mark, no carriage return and no control
or format character other than the tab that separates fields, and its last line ends in LF. A
line that is empty or starts with # is a comment; a line of whitespace alone is refused.

PATTERNS. A copy or render PATH is an exact path, or a narrow glob: one * in the last segment,
under a fixed directory, ending in a fixed suffix that holds a dot and a file type. A deny
PATTERN may also hold ** as a whole segment, which matches any number of segments (at least one
when it ends the pattern), and one * in any segment. A * matches one or more characters other
than /, and none that starts a name with a dot. Paths and patterns hold only ASCII letters,
digits and . _ + @ - and never a . or .. segment, an empty segment or a .git segment. Matching
is case-sensitive.

MODES.

  --check          Parse the four files under export/ and hold them to the checkout: every
                   tracked path (git ls-files) matches exactly one copy or render line, or a deny
                   line and no copy or render line; every line of the allowlist and of the
                   private paths matches at least one tracked path; every guide, and each of the
                   three public export files, has its own exact copy line; every publishable
                   marker compiles; and every public exception names a copied file whose line
                   still has the recorded SHA-256 and still holds a hit of the marker it names.
  --check-private  Refuse the private directory unless it is an absolute path that is not a
                   symbolic link, outside the repository, owned by the effective user and not
                   group- or world-writable, holding the three lists as regular 0600 files
                   owned by that user. Then parse them, and check each private exception that
                   names a copied file against the checkout. An exception that names a rendered
                   file can only be checked on the staged tree, so it is counted and left.

Exit 0 when every check passes, 1 on a finding, 2 when an input cannot be read, git cannot list
the tracked files, or the private directory or one of its lists is refused. Nothing is written.
"""
import argparse
import collections
import hashlib
import os
import re
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from _verify_sections import counted_guides  # noqa: E402  one definition of the guide set

ROOT = TOOLS.parent
# The default private directory. The private lists live outside every checkout.
DEFAULT_PRIVATE_DIR = "/opt/secureconfig/private/export/"

ALLOWLIST = "export/public-allowlist.txt"
PRIVATE_PATHS = "export/private-paths.txt"
PUBLIC_MARKERS = "export/public-markers.txt"
PUBLIC_EXCEPTIONS = "export/public-exceptions.tsv"
# The files the public repository carries so its own checks can run.
PUBLIC_EXPORT_FILES = (ALLOWLIST, PUBLIC_MARKERS, PUBLIC_EXCEPTIONS)

TERMS = "protected-terms.txt"
PRIVATE_MARKERS = "private-markers.txt"
PRIVATE_EXCEPTIONS = "exceptions.tsv"
PRIVATE_FILES = (TERMS, PRIVATE_MARKERS, PRIVATE_EXCEPTIONS)

PUBLISH_KINDS = ("copy", "render")
NEEDS = ("required", "optional")
SEGMENT = re.compile(r"[A-Za-z0-9._+@-]+")
GLOB_SUFFIX = re.compile(r"[A-Za-z0-9._+@-]*\.[A-Za-z0-9]+")
MARKER_ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
SHA256_HEX = re.compile(r"[0-9a-f]{64}")
LINE_NUMBER = re.compile(r"[1-9][0-9]*")

Entry = collections.namedtuple("Entry", "line kind pattern need source regex")
Marker = collections.namedtuple("Marker", "line ident regex")
Term = collections.namedtuple("Term", "line text regex")
ExceptionRow = collections.namedtuple("ExceptionRow", "line path number digest ref reason")


class Refused(Exception):
    """An input that cannot be read, or a private directory or list that is refused (exit 2)."""


def split_lines(data, name):
    """([(line number, text)] for the entries of a list file, [findings]).

    Comments (empty lines and lines starting with #) are left out. A file that is not LF-ended
    UTF-8 yields no lines and one finding."""
    if data.startswith(b"\xef\xbb\xbf"):
        return [], [f"{name}: starts with a byte order mark"]
    if b"\r" in data:
        return [], [f"{name}: holds a carriage return; every line ends in LF alone"]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [f"{name}: is not UTF-8 (byte {exc.start})"]
    if text and not text.endswith("\n"):
        return [], [f"{name}: its last line does not end in LF"]
    lines, findings = [], []
    for number, line in enumerate(text.split("\n")[:-1], 1):
        if any(char != "\t" and unicodedata.category(char) in ("Cc", "Cf", "Zl", "Zp")
               for char in line):
            findings.append(f"{name}:{number}: holds a control or format character")
        elif line == "" or line.startswith("#"):
            continue
        elif not line.strip():
            findings.append(f"{name}:{number}: holds whitespace alone")
        else:
            lines.append((number, line))
    return lines, findings


def path_problem(path, kind):
    """Why PATH is not a valid PATTERN for a KIND line ("exact" for an exact path), or None."""
    if not path:
        return "is empty"
    if path.startswith("/"):
        return "is absolute"
    if path.endswith("/"):
        return "ends in /"
    segments = path.split("/")
    for segment in segments:
        if segment == "":
            return "has an empty segment"
        if segment in (".", ".."):
            return "has a . or .. segment"
        if segment == ".git":
            return "names .git"
        if segment == "**":
            if kind != "deny":
                return "uses **, which only a deny line may"
            continue
        if "**" in segment:
            return "uses ** inside a segment; ** is a whole segment"
        if segment.count("*") > 1:
            return "has more than one * in a segment"
        if "*" in segment and kind == "exact":
            return "is a glob where an exact path is needed"
        rest = segment.replace("*", "")
        if rest and not SEGMENT.fullmatch(rest):
            return "holds a character other than an ASCII letter, a digit or . _ + @ -"
    if kind == "deny" and all(segment == "**" for segment in segments):
        return "denies every path"
    if kind in PUBLISH_KINDS and "*" in path:
        if path.count("*") > 1:
            return "has more than one *"
        if len(segments) < 2:
            return "is a glob at the repository root; name each root file exactly"
        if "*" not in segments[-1]:
            return "has its * outside the last segment"
        if not GLOB_SUFFIX.fullmatch(segments[-1].split("*", 1)[1]):
            return "has no fixed suffix after its *, such as .md"
    return None


def pattern_regex(pattern):
    """The compiled full-path match of a valid pattern."""
    out = []
    segments = pattern.split("/")
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        if segment == "**":
            out.append("[^/]+(?:/[^/]+)*" if last else "(?:[^/]+/)*")
            continue
        if "*" in segment:
            before, after = segment.split("*", 1)
            star = "[^/]+" if before else "[^/.][^/]*"
            out.append(re.escape(before) + star + re.escape(after))
        else:
            out.append(re.escape(segment))
        if not last:
            out.append("/")
    return re.compile("".join(out))


def parse_paths(data, name, kinds):
    """([Entry], [findings]) for the public allowlist (kinds copy and render) or the private
    paths (kind deny)."""
    lines, findings = split_lines(data, name)
    entries, seen = [], {}
    for number, line in lines:
        where = f"{name}:{number}"
        fields = line.split("\t")
        kind = fields[0]
        if kind not in kinds:
            findings.append(f"{where}: the kind {kind!r} is not {' or '.join(kinds)} "
                            f"in this file")
            continue
        wanted = (2,) if kind == "deny" else (3, 4)
        if len(fields) not in wanted:
            findings.append(f"{where}: a {kind} line has {len(fields)} tab-separated fields, "
                            f"not {' or '.join(map(str, wanted))}")
            continue
        pattern = fields[1]
        problem = path_problem(pattern, kind)
        if problem:
            findings.append(f"{where}: the pattern {pattern!r} {problem}")
            continue
        need = source = None
        if kind != "deny":
            need = fields[2]
            if need not in NEEDS:
                findings.append(f"{where}: the need {need!r} is not required or optional")
                continue
            if len(fields) == 4:
                source = fields[3]
                if kind != "render":
                    findings.append(f"{where}: only a render line names a source")
                    continue
                if "*" in pattern:
                    findings.append(f"{where}: a render line with a source names one exact path")
                    continue
                problem = path_problem(source, "exact")
                if problem:
                    findings.append(f"{where}: the source {source!r} {problem}")
                    continue
        if pattern in seen:
            findings.append(f"{where}: repeats the pattern of line {seen[pattern]}")
            continue
        seen[pattern] = number
        entries.append(Entry(number, kind, pattern, need, source, pattern_regex(pattern)))
    if not entries and not findings:
        findings.append(f"{name}: has no entries")
    # An exact path that a glob of the same file also matches would be published twice.
    for entry in entries:
        if "*" in entry.pattern:
            continue
        for other in entries:
            if other is not entry and other.kind != "deny" and other.regex.fullmatch(entry.pattern):
                findings.append(f"{name}:{entry.line}: {entry.pattern!r} is also matched by "
                                f"line {other.line}")
    return entries, findings


def overlap_findings(publish, deny):
    """A copy or render line that a deny line covers: the exact path, or for a glob a name it
    matches, is denied."""
    findings = []
    for entry in publish:
        sample = entry.pattern.replace("*", "x")
        for other in deny:
            if other.regex.fullmatch(sample):
                findings.append(f"{ALLOWLIST}:{entry.line}: {entry.kind} {entry.pattern!r} is "
                                f"covered by the deny line {PRIVATE_PATHS}:{other.line}")
                break
    return findings


def parse_markers(data, name, allow_empty, show=True):
    """([Marker], [findings]) for a marker file; with show false no finding quotes the file."""
    lines, findings = split_lines(data, name)
    markers, seen = [], {}
    for number, line in lines:
        where = f"{name}:{number}"
        fields = line.split("\t", 1)
        if len(fields) != 2:
            findings.append(f"{where}: is not ID<TAB>REGEX")
            continue
        ident, source = fields
        if not MARKER_ID.fullmatch(ident):
            shown = f" {ident!r}" if show else ""
            findings.append(f"{where}: the id{shown} is not lowercase ASCII letters and digits "
                            f"in words joined by single hyphens")
            continue
        if ident in seen:
            findings.append(f"{where}: repeats the id of line {seen[ident]}")
            continue
        try:
            compiled = re.compile(source)
        except re.error as exc:
            findings.append(f"{where}: the pattern does not compile ({exc.msg})")
            continue
        if compiled.match(""):
            findings.append(f"{where}: the pattern matches the empty string")
            continue
        seen[ident] = number
        markers.append(Marker(number, ident, compiled))
    if not markers and not findings and not allow_empty:
        findings.append(f"{name}: has no markers")
    return markers, findings


def term_regex(term):
    """A protected term matched case-insensitively at word boundaries."""
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)


def parse_terms(data, name=TERMS):
    """([Term], [findings]) for the protected-terms list. No finding quotes a term."""
    lines, findings = split_lines(data, name)
    terms, seen = [], {}
    for number, line in lines:
        where = f"{name}:{number}"
        if "\t" in line:
            findings.append(f"{where}: holds a tab")
            continue
        if line != line.strip():
            findings.append(f"{where}: has leading or trailing whitespace")
            continue
        key = line.casefold()
        if key in seen:
            findings.append(f"{where}: repeats the term of line {seen[key]}, ignoring case")
            continue
        seen[key] = number
        terms.append(Term(number, line, term_regex(line)))
    if not terms and not findings:
        findings.append(f"{name}: has no terms")
    return terms, findings


def parse_exceptions(data, name, marker_ids, terms=None, show=True):
    """([ExceptionRow], [findings]) for an exceptions file. REF is marker:ID for an id in
    marker_ids, or, when terms (a set of casefolded terms) is given, term:TERM for one of them.
    With show false no finding quotes the file."""
    lines, findings = split_lines(data, name)
    rows, seen = [], {}
    for number, line in lines:
        where = f"{name}:{number}"
        fields = line.split("\t")
        if len(fields) != 5:
            findings.append(f"{where}: has {len(fields)} tab-separated fields, not 5 "
                            f"(PATH, LINE, SHA256, REF, REASON)")
            continue
        path, line_text, digest, ref, reason = fields
        problem = path_problem(path, "exact")
        if problem:
            shown = f" {path!r}" if show else ""
            findings.append(f"{where}: the path{shown} {problem}")
            continue
        if not LINE_NUMBER.fullmatch(line_text):
            findings.append(f"{where}: the line is not a whole number from 1, without leading zeros")
            continue
        if not SHA256_HEX.fullmatch(digest):
            findings.append(f"{where}: the SHA-256 is not 64 lowercase hexadecimal characters")
            continue
        if ref.startswith("marker:"):
            if ref[len("marker:"):] not in marker_ids:
                findings.append(f"{where}: names a marker id its marker file does not hold")
                continue
        elif ref.startswith("term:"):
            if terms is None:
                findings.append(f"{where}: a public exception cannot name a term")
                continue
            if ref[len("term:"):].casefold() not in terms:
                findings.append(f"{where}: names a term the protected-terms list does not hold")
                continue
        else:
            findings.append(f"{where}: the reference is neither marker:ID nor term:TERM")
            continue
        if not reason.strip() or reason != reason.strip():
            findings.append(f"{where}: the reason is empty or has leading or trailing whitespace")
            continue
        key = (path, int(line_text), ref.casefold())
        if key in seen:
            findings.append(f"{where}: repeats the exception of line {seen[key]}")
            continue
        seen[key] = number
        rows.append(ExceptionRow(number, path, int(line_text), digest, ref, reason))
    return rows, findings


def line_sha256(raw):
    """The SHA-256 an exception records: of the line's bytes, without its LF."""
    return hashlib.sha256(raw).hexdigest()


def verify_exceptions(rows, name, root, pattern_of, show=True):
    """Findings for each exception whose line is gone, changed, or no longer holds a hit of
    what it names. pattern_of maps a REF to its compiled pattern."""
    findings, cache = [], {}
    for row in rows:
        where = f"{name}:{row.line}"
        target = f"{row.path}:{row.number}" if show else "the line it names"
        if row.path not in cache:
            path = Path(root) / row.path
            try:
                if path.is_symlink():
                    raise OSError("it is a symbolic link")
                data = path.read_bytes()
            except OSError as exc:
                cache[row.path] = exc
            else:
                lines = data.split(b"\n")
                cache[row.path] = lines[:-1] if data.endswith(b"\n") else lines
        lines = cache[row.path]
        if isinstance(lines, OSError):
            shown = f" {row.path}" if show else " the file it names"
            findings.append(f"{where}: cannot read{shown} ({lines.strerror or lines})")
            continue
        if row.number > len(lines):
            findings.append(f"{where}: stale: {target} is past the end of the file")
            continue
        raw = lines[row.number - 1]
        if line_sha256(raw) != row.digest:
            findings.append(f"{where}: stale: {target} no longer has the recorded SHA-256")
            continue
        if not pattern_of(row.ref).search(raw.decode("utf-8", "replace")):
            findings.append(f"{where}: stale: what it names no longer matches {target}")
    return findings


def tracked_paths(root):
    """The tracked paths of the checkout at root, as git ls-files lists them; Refused when git
    cannot list them."""
    try:
        result = subprocess.run(["git", "ls-files", "-z", "--cached"], cwd=root, check=True,
                                capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refused(f"git cannot list the tracked files under {root} ({exc})") from exc
    return sorted({os.fsdecode(name) for name in result.stdout.split(b"\0") if name})


def check_tree(publish, deny, paths, guides):
    """Findings for the allowlist and the private paths held to the tracked paths."""
    findings = []
    matched = collections.Counter()
    for path in paths:
        allow = [entry for entry in publish if entry.regex.fullmatch(path)]
        denied = [entry for entry in deny if entry.regex.fullmatch(path)]
        for entry in allow + denied:
            matched[(entry.kind == "deny", entry.line)] += 1
        if not allow and not denied:
            findings.append(f"{path}: tracked, but no line of {ALLOWLIST} or {PRIVATE_PATHS} "
                            f"matches it; add a copy, render or deny line")
        elif allow and denied:
            findings.append(f"{path}: matched by the deny line {PRIVATE_PATHS}:{denied[0].line} "
                            f"and the {allow[0].kind} line {ALLOWLIST}:{allow[0].line}")
        elif len(allow) > 1:
            lines = ", ".join(str(entry.line) for entry in allow)
            findings.append(f"{path}: matched by {len(allow)} lines of {ALLOWLIST} ({lines}); "
                            f"the export publishes each path from one line")
    for name, entries in ((ALLOWLIST, publish), (PRIVATE_PATHS, deny)):
        for entry in entries:
            if not matched[(entry.kind == "deny", entry.line)]:
                findings.append(f"{name}:{entry.line}: {entry.kind} {entry.pattern!r} matches "
                                f"no tracked path")
    exact = {entry.pattern: entry for entry in publish
             if entry.kind == "copy" and "*" not in entry.pattern}
    for path in list(guides) + list(PUBLIC_EXPORT_FILES):
        entry = exact.get(path)
        if entry is None or entry.need != "required":
            findings.append(f"{path}: needs its own exact copy line in {ALLOWLIST}, marked "
                            f"required")
    return findings


def copied(publish, path):
    """Whether a copy line of the allowlist matches path."""
    return any(entry.kind == "copy" and entry.regex.fullmatch(path) for entry in publish)


def read_repo_file(root, relative):
    try:
        return (Path(root) / relative).read_bytes()
    except OSError as exc:
        raise Refused(f"cannot read {relative} ({exc.strerror or exc})") from exc


def load_public(root):
    """The parsed public files and the private paths: (publish, deny, markers, rows, findings)."""
    publish, f1 = parse_paths(read_repo_file(root, ALLOWLIST), ALLOWLIST, PUBLISH_KINDS)
    deny, f2 = parse_paths(read_repo_file(root, PRIVATE_PATHS), PRIVATE_PATHS, ("deny",))
    markers, f3 = parse_markers(read_repo_file(root, PUBLIC_MARKERS), PUBLIC_MARKERS,
                                allow_empty=False)
    rows, f4 = parse_exceptions(read_repo_file(root, PUBLIC_EXCEPTIONS), PUBLIC_EXCEPTIONS,
                                {marker.ident for marker in markers})
    findings = f1 + f2 + f3 + f4
    if not f1 and not f2:
        findings += overlap_findings(publish, deny)
    return publish, deny, markers, rows, findings


def run_check(root):
    publish, deny, markers, rows, findings = load_public(root)
    paths = tracked_paths(root)
    try:
        guides = counted_guides(Path(root))
    except OSError as exc:
        raise Refused(f"cannot list the guides ({exc.strerror or exc})") from exc
    if not findings:
        findings += check_tree(publish, deny, paths, guides)
        by_id = {marker.ident: marker.regex for marker in markers}
        for row in rows:
            if not copied(publish, row.path):
                findings.append(f"{PUBLIC_EXCEPTIONS}:{row.line}: names {row.path}, which no "
                                f"copy line exports; a rendered file is checked on the staged "
                                f"tree")
        findings += verify_exceptions([row for row in rows if copied(publish, row.path)],
                                      PUBLIC_EXCEPTIONS, root,
                                      lambda ref: by_id[ref[len("marker:"):]])
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    kinds = collections.Counter(entry.kind for entry in publish)
    print(f"  ok    export lists: all {len(paths)} tracked paths are published by exactly one of "
          f"the {len(publish)} allowlist lines ({kinds['copy']} copy, {kinds['render']} render) "
          f"or kept private by the {len(deny)} deny lines, every line matches a tracked path, "
          f"each of the {len(guides)} guides has its own copy line, {len(markers)} publishable "
          f"markers compile, and {len(rows)} public exceptions match their lines")
    return 0


def private_dir_problem(text, root):
    """Why the private directory is refused, or None."""
    if not os.path.isabs(text):
        return "is not an absolute path"
    # lstat of a path ending in / would follow a symbolic link.
    path = text.rstrip("/") or "/"
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return "does not exist, so the private lists were not supplied"
    except OSError as exc:
        return f"cannot be read ({exc.strerror or exc})"
    if stat.S_ISLNK(info.st_mode):
        return "is a symbolic link"
    if not stat.S_ISDIR(info.st_mode):
        return "is not a directory"
    if info.st_uid != os.geteuid():
        return "is not owned by the user running this tool"
    if info.st_mode & 0o022:
        return "is group- or world-writable"
    real, repo = os.path.realpath(path), os.path.realpath(root)
    if os.path.commonpath([real, repo]) in (real, repo):
        return "is inside the repository worktree, or holds it"
    return None


def read_private(directory, name):
    """The bytes of one private list; Refused unless it is a regular 0600 file owned by the
    effective user, read without following a symbolic link."""
    path = os.path.join(directory.rstrip("/") or "/", name)
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        raise Refused(f"the private directory has no {name}") from None
    except OSError as exc:
        raise Refused(f"cannot read {name} ({exc.strerror or exc})") from None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise Refused(f"{name} is not a regular file")
    if info.st_uid != os.geteuid():
        raise Refused(f"{name} is not owned by the user running this tool")
    if stat.S_IMODE(info.st_mode) != 0o600:
        raise Refused(f"{name} has mode {stat.S_IMODE(info.st_mode):04o}, not 0600")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise Refused(f"cannot open {name} ({exc.strerror or exc})") from None
    try:
        opened = os.fstat(fd)
        if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
            raise Refused(f"{name} changed while it was opened")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(fd)
    return b"".join(chunks)


def run_check_private(root, directory):
    problem = private_dir_problem(directory, root)
    if problem:
        raise Refused(f"the private directory {problem}")
    data = {name: read_private(directory, name) for name in PRIVATE_FILES}
    publish, f1 = parse_paths(read_repo_file(root, ALLOWLIST), ALLOWLIST, PUBLISH_KINDS)
    terms, f2 = parse_terms(data[TERMS])
    markers, f3 = parse_markers(data[PRIVATE_MARKERS], PRIVATE_MARKERS, allow_empty=True,
                                show=False)
    rows, f4 = parse_exceptions(data[PRIVATE_EXCEPTIONS], PRIVATE_EXCEPTIONS,
                                {marker.ident for marker in markers},
                                {term.text.casefold() for term in terms}, show=False)
    findings = f1 + f2 + f3 + f4
    checked = []
    if not findings:
        for row in rows:
            if copied(publish, row.path):
                checked.append(row)
            elif not any(entry.regex.fullmatch(row.path) for entry in publish):
                findings.append(f"{PRIVATE_EXCEPTIONS}:{row.line}: names a path the allowlist "
                                f"does not publish")
        by_id = {marker.ident: marker.regex for marker in markers}

        def pattern_of(ref):
            if ref.startswith("marker:"):
                return by_id[ref[len("marker:"):]]
            return term_regex(ref[len("term:"):])

        findings += verify_exceptions(checked, PRIVATE_EXCEPTIONS, root, pattern_of, show=False)
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    private lists: {len(terms)} protected terms, {len(markers)} private markers "
          f"and {len(rows)} exceptions parse; {len(checked)} exceptions match their lines in "
          f"the checkout and {len(rows) - len(checked)} name rendered files, checked on the "
          f"staged tree")
    for name in PRIVATE_FILES:
        print(f"        {name} sha256 {hashlib.sha256(data[name]).hexdigest()}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Parse and check the export lists.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true",
                      help="hold the files under export/ to the tracked paths of the checkout")
    mode.add_argument("--check-private", action="store_true",
                      help="parse and check the private lists, printing no list content")
    parser.add_argument("--private-dir", default=DEFAULT_PRIVATE_DIR,
                        help="the directory holding the private lists (read only)")
    parser.add_argument("--root", default=str(ROOT),
                        help="the checkout to check (default: the one holding this tool)")
    args = parser.parse_args(argv)
    try:
        if args.check:
            return run_check(args.root)
        return run_check_private(args.root, args.private_dir)
    except Refused as exc:
        print(f"  FAIL  {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
