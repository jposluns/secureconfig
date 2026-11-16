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
with --private-dir, or else by the SECURECONFIG_EXPORT_PRIVATE environment variable, or else
DEFAULT_PRIVATE_DIR. This tool never creates that directory:

  protected-terms.txt  one literal term per line, matched case-insensitively at word boundaries.
  private-markers.txt  ID<TAB>REGEX, as export/public-markers.txt, for shapes that would
                       disclose something if published, such as links into the private paths.
  exceptions.tsv       as export/public-exceptions.tsv; REF may also be term:TERM.

Nothing read from a private list, and no part of the private directory's path, is printed: a
finding in one names its file and the rule it breaks, with the line number for a line or the
byte offset of the first byte that is not UTF-8, never a message or warning of the regular
expression compiler, which can quote or locate the pattern. A pass prints counts and each list's
SHA-256, and an unexpected error in --check-private prints only its type. When an argument
starts with --priv or --check-p, a prefix of --private-dir or --check-private, a usage error
prints the usage and a fixed message and repeats no argument, in either mode.

Every list is UTF-8 with LF line endings, no byte order mark, no carriage return and no control
or format character other than the tab that separates fields, and its last line ends in LF.
Fields are separated by single tabs, so no field holds a tab. A line that is empty or starts
with # is a comment; a line of whitespace alone is refused.

PATTERNS. A copy or render PATH is an exact path, or a narrow glob: one * in the last segment,
under a fixed directory, ending in a fixed suffix that holds a dot and a file type. A deny
PATTERN may also hold ** as a whole segment, which matches any number of segments (at least one
when it ends the pattern), and one * in any segment. A * matches one or more characters other
than /, and none that starts a name with a dot. Paths and patterns hold only ASCII letters,
digits and . _ + @ - and never a . or .. segment, an empty segment or a .git segment. Matching
is case-sensitive.

NEED. A copy or render line ends in a NEED, and a deny line may: required (the default on a
deny line) means the line must match at least one tracked path, and optional means it may match
none, for a path that is not in the checkout yet.

MODES.

  --check          Parse the four files under export/ and hold them to the checkout: every
                   tracked path (git ls-files) matches exactly one copy or render line, or
                   exactly one deny line and no copy or render line; every tracked path a copy
                   or render line matches is a regular file whose name keeps to the path
                   characters above; every required line of the allowlist and of the private
                   paths matches at least one tracked path; every tracked guide, and each of the
                   three public export files, has its own exact copy line, marked required; no
                   copy or render line can match a path that a deny line matches; every
                   publishable marker compiles without a compiler warning and can never match
                   an empty string; and every public exception names a copied file whose line
                   still has the recorded SHA-256 and still holds a hit of the marker it names.
  --check-private  Open the private directory once, without following a symbolic link, and
                   refuse it unless it is an absolute path outside the repository, owned by the
                   effective user and not group- or world-writable. Read each of the three lists
                   through that open directory, without following a symbolic link, and refuse it
                   unless it is a regular 0600 file owned by that user. Then parse them, and check
                   each private exception that names a copied file against the checkout. An
                   exception that names a rendered file can only be checked on the staged tree,
                   which this tool does not build, so it is counted and not checked. Last, for
                   each deny line, build a path it keeps private (each ** and * written as x)
                   and the two links of LINK_FORMS to that path, and fail the deny line unless
                   some private marker finds each link.

Exit 0 when every check passes, 1 on a finding, 2 when an input cannot be read, git cannot list
the tracked files, the private directory or one of its lists is refused, or --check-private
stops on an unexpected error. Nothing is written.
"""
import argparse
import collections
import errno
import hashlib
import os
import re
import stat
import subprocess
import sys
import unicodedata
import warnings
from pathlib import Path

# The re module's own pattern parser, used to find a pattern's shortest match. The re module has
# no public call for that width; if this private module changes, shortest_match fails and the
# marker is refused, never accepted.
try:
    from re import _parser as regex_parser
except ImportError:  # Python before 3.11
    import sre_parse as regex_parser

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from _verify_sections import counted_guides  # noqa: E402  one definition of the guide set

ROOT = TOOLS.parent
# The default private directory. The private lists live outside every checkout.
DEFAULT_PRIVATE_DIR = "/opt/secureconfig/private/export/"
# The environment variable that names the private directory when --private-dir is not given.
PRIVATE_DIR_ENV = "SECURECONFIG_EXPORT_PRIVATE"

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
# The links --check-private builds into a path each deny line keeps private; the private markers
# must find each of them. The owner is synthetic and the ref has no /.
LINK_FORMS = (("a github.com blob", "https://github.com/example-org/secureconfig/blob/main/{}"),
              ("a raw.githubusercontent.com",
               "https://raw.githubusercontent.com/example-org/secureconfig/main/{}"))
# The prefixes of --private-dir and --check-private that put a usage error in quiet mode, since
# an argument that starts with one, even a misspelled option, may carry the private path.
PRIVATE_ARGUMENTS = ("--priv", "--check-p")

PUBLISH_KINDS = ("copy", "render")
NEEDS = ("required", "optional")
# The git modes of a regular file, the only kind of tracked path the export publishes.
REGULAR_MODES = ("100644", "100755")
GIT_MODE_NAMES = {"120000": "a symbolic link", "160000": "a submodule"}
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


def os_reason(exc):
    """The operating system's message for exc, which holds no path, or else its type name."""
    if isinstance(exc, OSError) and exc.strerror:
        return exc.strerror
    return type(exc).__name__


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


def name_meets(name, before, after):
    """Whether the segment glob BEFORE*AFTER matches the literal segment NAME."""
    return (len(name) > len(before) + len(after) and name.startswith(before)
            and name.endswith(after) and (before != "" or not name.startswith(".")))


def segments_meet(first, second):
    """Whether two segments of valid patterns, each a literal or one * with a fixed prefix and
    suffix, match at least one common name."""
    if "*" not in first and "*" not in second:
        return first == second
    if "*" not in first:
        first, second = second, first
    before1, after1 = first.split("*", 1)
    if "*" not in second:
        return name_meets(second, before1, after1)
    before2, after2 = second.split("*", 1)
    if not (before1.startswith(before2) or before2.startswith(before1)):
        return False
    if not (after1.endswith(after2) or after2.endswith(after1)):
        return False
    # The common name is the longer prefix, one character that is neither / nor a dot, and the
    # longer suffix. A * after an empty prefix never starts a name with a dot.
    start = max(before1, before2, key=len)
    return not (start.startswith(".") and (before1 == "" or before2 == ""))


def patterns_meet(first, second):
    """Whether a valid pattern with no ** (FIRST) and a valid deny pattern (SECOND) match at least
    one common path: an exact answer, not a sample."""
    left, right = first.split("/"), second.split("/")

    def meet(i, j):
        if j == len(right):
            return i == len(left)
        if right[j] == "**":
            if j == len(right) - 1:
                return i < len(left)
            return any(meet(k, j + 1) for k in range(i, len(left) + 1))
        return i < len(left) and segments_meet(left[i], right[j]) and meet(i + 1, j + 1)

    return meet(0, 0)


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
        wanted = (2, 3) if kind == "deny" else (3, 4)
        if len(fields) not in wanted:
            findings.append(f"{where}: a {kind} line has {len(fields)} tab-separated fields, "
                            f"not {' or '.join(map(str, wanted))}")
            continue
        pattern = fields[1]
        problem = path_problem(pattern, kind)
        if problem:
            findings.append(f"{where}: the pattern {pattern!r} {problem}")
            continue
        need = fields[2] if len(fields) > 2 else "required"
        if need not in NEEDS:
            findings.append(f"{where}: the need {need!r} is not required or optional")
            continue
        source = None
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
    # An exact path that a glob of the same file also matches would be published twice, or kept
    # private by two deny lines.
    for entry in entries:
        if "*" in entry.pattern:
            continue
        for other in entries:
            if other is not entry and other.regex.fullmatch(entry.pattern):
                findings.append(f"{name}:{entry.line}: {entry.pattern!r} is also matched by "
                                f"line {other.line}")
    return entries, findings


def overlap_findings(publish, deny):
    """A copy or render line that can match a path a deny line matches. The answer is exact:
    for a glob it holds for every name the glob can match, tracked or not."""
    findings = []
    for entry in publish:
        for other in deny:
            if patterns_meet(entry.pattern, other.pattern):
                findings.append(f"{ALLOWLIST}:{entry.line}: {entry.kind} {entry.pattern!r} can "
                                f"match a path that the deny line {PRIVATE_PATHS}:{other.line} "
                                f"also matches")
                break
    return findings


def shortest_match(source):
    """The fewest characters a match of the compiled pattern SOURCE can span, as the re module's
    own parser works it out, or None when it cannot be worked out, so the pattern is refused. A
    warning the parser raises as an exception is passed on."""
    try:
        return regex_parser.parse(source).getwidth()[0]
    except Warning:
        raise
    except Exception:  # noqa: BLE001  any other failure leaves the width unknown
        return None


def compile_marker(source):
    """(compiled pattern, shortest match) for SOURCE. Every warning raised while it compiles and
    parses SOURCE is raised as an exception, so none is printed. shortest_match parses SOURCE
    again, which re does not cache, so a parser warning is raised even when re.compile returns a
    pattern it compiled earlier."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        compiled = re.compile(source)
        return compiled, shortest_match(source)


def parse_markers(data, name, allow_empty, show=True):
    """([Marker], [findings]) for a marker file; with show false no finding quotes the file or
    passes on a compiler message or warning, which can quote or locate the pattern."""
    lines, findings = split_lines(data, name)
    markers, seen = [], {}
    for number, line in lines:
        where = f"{name}:{number}"
        fields = line.split("\t")
        if len(fields) != 2:
            findings.append(f"{where}: is not ID<TAB>REGEX: it has {len(fields)} tab-separated "
                            f"fields, not 2")
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
            compiled, width = compile_marker(source)
        except Warning as exc:
            detail = f" ({exc})" if show else ""
            findings.append(f"{where}: the regular expression compiler warns about the "
                            f"pattern{detail}")
            continue
        except (re.error, OverflowError, RecursionError, ValueError) as exc:
            detail = f" ({exc.msg})" if show and isinstance(exc, re.error) else ""
            findings.append(f"{where}: the pattern does not compile{detail}")
            continue
        if width is None:
            findings.append(f"{where}: the shortest match of the pattern cannot be worked out, "
                            f"so it is refused")
            continue
        if width == 0:
            findings.append(f"{where}: the pattern can match an empty string, so it would hit "
                            f"every line")
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
                    raise OSError(errno.ELOOP, "it is a symbolic link")
                data = path.read_bytes()
            except OSError as exc:
                cache[row.path] = exc
            else:
                lines = data.split(b"\n")
                cache[row.path] = lines[:-1] if data.endswith(b"\n") else lines
        lines = cache[row.path]
        if isinstance(lines, OSError):
            shown = f" {row.path}" if show else " the file it names"
            findings.append(f"{where}: cannot read{shown} ({os_reason(lines)})")
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
    """{path: git mode} for the tracked paths of the checkout at root, as git ls-files --stage
    lists them; Refused when git cannot list them."""
    try:
        result = subprocess.run(["git", "ls-files", "-z", "--stage"], cwd=root, check=True,
                                capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refused(f"git cannot list the tracked files under {root} ({exc})") from exc
    modes = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        head, tab, name = record.partition(b"\t")
        fields = head.split(b" ")
        if not tab or not name or len(fields) != 3:
            raise Refused("git ls-files --stage printed a record this tool cannot read")
        modes[os.fsdecode(name)] = fields[0].decode("ascii", "replace")
    return modes


def check_tree(publish, deny, paths, guides, modes=None):
    """Findings for the allowlist and the private paths held to the tracked paths. modes, when
    given, maps each path to its git mode, and a published path must be a regular file."""
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
        elif len(denied) > 1:
            lines = ", ".join(str(entry.line) for entry in denied)
            findings.append(f"{path}: kept private by {len(denied)} deny lines of "
                            f"{PRIVATE_PATHS} ({lines}); keep each private path under one line")
        if allow:
            where = f"{allow[0].kind} line {ALLOWLIST}:{allow[0].line}"
            problem = path_problem(path, "exact")
            if problem:
                findings.append(f"{path!r}: published by the {where}, but the path {problem}")
            if modes is not None and modes.get(path) not in REGULAR_MODES:
                mode = modes.get(path)
                kind = GIT_MODE_NAMES.get(mode, f"git mode {mode}")
                findings.append(f"{path!r}: published by the {where}, but it is {kind}, not a "
                                f"regular file")
    for name, entries in ((ALLOWLIST, publish), (PRIVATE_PATHS, deny)):
        for entry in entries:
            if entry.need == "required" and not matched[(entry.kind == "deny", entry.line)]:
                findings.append(f"{name}:{entry.line}: {entry.kind} {entry.pattern!r} matches "
                                f"no tracked path; mark it optional if the path is not in the "
                                f"checkout yet")
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
        raise Refused(f"cannot read {relative} ({os_reason(exc)})") from exc


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
    modes = tracked_paths(root)
    paths = sorted(modes)
    try:
        # Only a tracked guide needs a line: an untracked Markdown file is not published.
        guides = [guide for guide in counted_guides(Path(root)) if guide in modes]
    except OSError as exc:
        raise Refused(f"cannot list the guides ({os_reason(exc)})") from exc
    if not findings:
        findings += check_tree(publish, deny, paths, guides, modes)
        by_id = {marker.ident: marker.regex for marker in markers}
        for row in rows:
            if not copied(publish, row.path):
                findings.append(f"{PUBLIC_EXCEPTIONS}:{row.line}: names {row.path}, which no "
                                f"copy line exports; this check holds exceptions to copied "
                                f"files only")
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
          f"or kept private by exactly one of the {len(deny)} deny lines, every required line "
          f"matches a tracked path, each of the {len(guides)} tracked guides has its own copy "
          f"line, {len(markers)} publishable markers compile, and {len(rows)} public exceptions "
          f"match their lines")
    return 0


def open_private_dir(text, root):
    """A descriptor of the private directory, opened once without following a symbolic link;
    Refused unless the directory passes every check. No message names the path."""
    if not os.path.isabs(text):
        raise Refused("the private directory is not an absolute path")
    # Opening a path that ends in / would follow a symbolic link.
    path = text.rstrip("/") or "/"
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except FileNotFoundError:
        raise Refused("the private directory does not exist, so the private lists were not "
                      "supplied") from None
    except OSError as exc:
        # The open is already refused; lstat only words the message.
        try:
            info = os.lstat(path)
        except OSError:
            info = None
        if info is not None and stat.S_ISLNK(info.st_mode):
            raise Refused("the private directory is a symbolic link") from None
        if info is not None and not stat.S_ISDIR(info.st_mode):
            raise Refused("the private directory is not a directory") from None
        raise Refused(f"the private directory cannot be opened ({os_reason(exc)})") from None
    try:
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode):
            raise Refused("the private directory is not a directory")
        if info.st_uid != os.geteuid():
            raise Refused("the private directory is not owned by the user running this tool")
        if info.st_mode & 0o022:
            raise Refused("the private directory is group- or world-writable")
        real, repo = os.path.realpath(path), os.path.realpath(root)
        try:
            named = os.stat(real)
        except OSError:
            named = None
        if named is None or (named.st_dev, named.st_ino) != (info.st_dev, info.st_ino):
            raise Refused("the private directory changed while it was checked")
        if os.path.commonpath([real, repo]) in (real, repo):
            raise Refused("the private directory is inside the repository worktree, or holds it")
    except BaseException:
        os.close(fd)
        raise
    return fd


def read_private(dir_fd, name):
    """The bytes of one private list, opened through the open private directory without
    following a symbolic link; Refused unless it is a regular 0600 file owned by the effective
    user."""
    try:
        # O_NONBLOCK keeps a FIFO from stalling the open; the type check below refuses it.
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=dir_fd)
    except FileNotFoundError:
        raise Refused(f"the private directory has no {name}") from None
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise Refused(f"{name} is not a regular file") from None
        raise Refused(f"cannot open {name} ({os_reason(exc)})") from None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise Refused(f"{name} is not a regular file")
        if info.st_uid != os.geteuid():
            raise Refused(f"{name} is not owned by the user running this tool")
        if stat.S_IMODE(info.st_mode) != 0o600:
            raise Refused(f"{name} has mode {stat.S_IMODE(info.st_mode):04o}, not 0600")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(fd)
    return b"".join(chunks)


def link_path(pattern):
    """A path the deny PATTERN matches: each ** and each * written as the name x."""
    return pattern.replace("**", "x").replace("*", "x")


def link_findings(deny, markers):
    """A deny line for which no private marker finds one of the LINK_FORMS links into a path it
    keeps private. No finding quotes a marker."""
    findings = []
    for entry in deny:
        for label, form in LINK_FORMS:
            link = form.format(link_path(entry.pattern))
            if not any(marker.regex.search(link) for marker in markers):
                findings.append(f"{PRIVATE_PATHS}:{entry.line}: no private marker finds {label} "
                                f"link into a path this deny line keeps private")
    return findings


def run_check_private(root, directory):
    dir_fd = open_private_dir(directory, root)
    try:
        data = {name: read_private(dir_fd, name) for name in PRIVATE_FILES}
    finally:
        os.close(dir_fd)
    publish, f1 = parse_paths(read_repo_file(root, ALLOWLIST), ALLOWLIST, PUBLISH_KINDS)
    deny, f5 = parse_paths(read_repo_file(root, PRIVATE_PATHS), PRIVATE_PATHS, ("deny",))
    terms, f2 = parse_terms(data[TERMS])
    markers, f3 = parse_markers(data[PRIVATE_MARKERS], PRIVATE_MARKERS, allow_empty=True,
                                show=False)
    rows, f4 = parse_exceptions(data[PRIVATE_EXCEPTIONS], PRIVATE_EXCEPTIONS,
                                {marker.ident for marker in markers},
                                {term.text.casefold() for term in terms}, show=False)
    findings = f1 + f5 + f2 + f3 + f4
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
        findings += link_findings(deny, markers)
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    private lists: {len(terms)} protected terms, {len(markers)} private markers "
          f"and {len(rows)} exceptions parse; {len(checked)} exceptions match their lines in "
          f"the checkout and {len(rows) - len(checked)} name rendered files, which this tool "
          f"does not check; the private markers find both links into each of the {len(deny)} "
          f"deny lines")
    for name in PRIVATE_FILES:
        print(f"        {name} sha256 {hashlib.sha256(data[name]).hexdigest()}")
    return 0


def private_directory(given, environ):
    """The private directory: --private-dir when given, else the environment variable when it is
    set (even to an empty value, which is then refused), else DEFAULT_PRIVATE_DIR."""
    if given is not None:
        return given
    if PRIVATE_DIR_ENV in environ:
        return environ[PRIVATE_DIR_ENV]
    return DEFAULT_PRIVATE_DIR


class QuietParser(argparse.ArgumentParser):
    """An argument parser whose usage error, when quiet, prints the usage and a fixed message and
    repeats no argument, since an argument may be the private directory's path."""

    def __init__(self, *args, quiet=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiet = quiet

    def error(self, message):
        if not self.quiet:
            super().error(message)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: the arguments do not parse; with --check-private or "
                     f"--private-dir no argument is repeated\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else [str(arg) for arg in argv]
    # Abbreviations are off, so --check-private runs only when an argument names it in full, and
    # any argument that starts with --priv or --check-p makes a usage error quiet in either mode.
    quiet = any(arg.startswith(PRIVATE_ARGUMENTS) for arg in argv)
    parser = QuietParser(description="Parse and check the export lists.", allow_abbrev=False,
                         quiet=quiet)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true",
                      help="hold the files under export/ to the tracked paths of the checkout")
    mode.add_argument("--check-private", action="store_true",
                      help="parse and check the private lists, printing no list content")
    parser.add_argument("--private-dir", default=None,
                        help=f"the directory holding the private lists (read only); without "
                             f"it, ${PRIVATE_DIR_ENV} when set, else the built-in default")
    parser.add_argument("--root", default=str(ROOT),
                        help="the checkout to check (default: the one holding this tool)")
    args = parser.parse_args(argv)
    try:
        if args.check:
            return run_check(args.root)
        return run_check_private(args.root, private_directory(args.private_dir, os.environ))
    except Refused as exc:
        print(f"  FAIL  {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001
        if args.check:
            raise
        # A traceback could quote what a private list holds, so only the type is printed.
        print(f"  FAIL  --check-private stopped on an unexpected {type(exc).__name__}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
