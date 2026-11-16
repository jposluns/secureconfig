#!/usr/bin/env python3
"""The export gate: the only door to a public export, and it fails closed.

The gate judges a staged tree that the export tool assembled. Any error, unknown file or
scanner failure refuses the whole export: a check that cannot run to completion is a failure,
never a pass. It prints one ok or FAIL line per check, each finding on a FAIL line of its own
before its check's line, and writes the per-check verdicts into the record the caller names
with --verdicts, for the receipt the export tool keeps privately.

THE CHECKS. Every one fails closed.

  G1 allowlist     Every staged file is matched by exactly one copy or render line of
                   export/public-allowlist.txt. A file no line matches, a file a deny line of
                   export/private-paths.txt matches, a file two lines match, and a required
                   line that matches no staged file each refuse.
  G2 file hygiene  A symbolic link, a non-regular file, any .git entry, a path that leaves the
                   allowlist's path characters or holds a . or .. segment, an unreadable file,
                   and a mode other than 0644, or 0755 where the input tree's same path is
                   0755, each refuse.
  G3 publishable   A hit of export/public-markers.txt in a staged text file refuses, outside
     markers       the exact rows of export/public-exceptions.tsv; a stale row refuses too.
  G4 protected     Full mode only. A hit of a protected term or a private marker in a staged
     terms and     path name or in file contents refuses, outside the exact rows of the private
     private       exceptions list. Text is scanned as UTF-8 lines. A binary file is scanned in
     markers       its UTF-8, UTF-16LE and UTF-16BE readings (font name tables use UTF-16), and
                   the tEXt, zTXt and iTXt chunks of a PNG are decoded and scanned. No finding
                   prints a term, a private marker or a private-list line: it names the list
                   and the entry's line number, and a printed path is masked where it matches.
  G5 private       (a) Every relative Markdown link, every root-relative link in a staged site
     references    page and every github.com/<owner>/secureconfig blob, raw or tree link on
                   main must name a staged path. (b) Any github.com/<owner>/secureconfig link
                   to pull, commit, compare or actions refuses. (c) Full mode only: a run of 12
                   or more hexadecimal characters that prefixes, or holds, a commit id of the
                   private repository (git rev-list --all, read privately) refuses; the finding
                   never prints the characters.
  G6 drift         Full mode only. Each staged file a render line matches must equal the
                   independent fresh render the caller supplies with --fresh; each staged file
                   a copy line matches must equal its bytes in the input tree; and VERSION must
                   equal plugin/plugin.json's version.
  G7 completeness  Every file a required line matches is present and non-empty, and README.md,
                   LICENSE, NOTICE, VERSION and CHANGELOG.md are staged. Every counted guide of
                   the input tree (the staged tree in public-only mode) has a root copy and a
                   plugin reference copy. When archives are staged under site/downloads/, each
                   one's SHA-256 is listed in releases/SHA256SUMS, and every latest rule of
                   site/_redirects is a 302 to a staged versioned archive.
  G8 binaries      Full mode only. Every staged file under site/assets/baseline/ hashes to its
                   entry in the input tree's .baseline/pin.toml; a compressed font (.woff or
                   .woff2) crosses only as one of those pinned files, since this gate cannot
                   scan inside its compression; and every member of a staged zip archive is
                   scanned as G4 scans a file.

TWO MODES.

  Full mode        --staged DIR --input DIR --fresh DIR [--private-dir DIR]. Reads the export
                   lists from the input tree and the private lists as tools/export_lists.py
                   --check-private reads them, with two checks on top: the private directory
                   must grant no group or other permission at all, and must lie outside the
                   staged and input trees as well as this repository. The only mode that can
                   approve an export.
  Public-only      --staged DIR --public-only. Runs G1 (without the private paths, which the
                   public tree does not carry), G2, G3, G5a, G5b and G7, reading the public
                   lists from the staged tree itself, so a public check needs no private input.
                   It never approves an export, whatever it finds.

WHAT THE SCANS READ. A staged file is text when it holds no NUL byte and decodes as UTF-8;
every other file is a binary. The marker, link and hexadecimal scans read text files; binaries
are scanned for protected terms in the three encodings above, through their PNG text chunks,
and through their zip members. The Markdown link scan is this tool's own line scanner over the
same inline, definition, code-span and fence shapes scripts/build-llms-full.sh rewrites; it is
not the pinned CommonMark parser, which is not in the standard library, so a link form only
that parser sees is caught at build time, not here.

Exit 0 when every check that ran passed, 1 on a finding, 2 when an input cannot be read, the
private directory or a list is refused, or the verdicts file cannot be created. Nothing is
written anywhere but the --verdicts file, which is created new (never overwritten), mode 0600.
"""
import argparse
import hashlib
import io
import json
import os
import posixpath
import re
import stat
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path
from urllib.parse import unquote

try:
    import tomllib
except ImportError:  # an older interpreter: G8 then refuses rather than skipping the pin
    tomllib = None

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import export_lists as lists  # noqa: E402  one definition of the list formats
from _markdown import Fences  # noqa: E402  one definition of a fenced code block
from _verify_sections import counted_guides  # noqa: E402  one definition of the guide set

ROOT = TOOLS.parent

CHECKS = (
    ("G1", "allowlist"),
    ("G2", "file hygiene"),
    ("G3", "publishable markers"),
    ("G4", "protected terms and private markers"),
    ("G5", "private references"),
    ("G6", "drift"),
    ("G7", "completeness"),
    ("G8", "binaries"),
)
# The checks public-only mode runs; G5 runs without its commit-prefix part there.
PUBLIC_ONLY_CHECKS = ("G1", "G2", "G3", "G5", "G7")

# The files section 3 of the fleet spec names; each must be staged and non-empty.
NAMED_REQUIRED = ("README.md", "LICENSE", "NOTICE", "VERSION", "CHANGELOG.md")
REFERENCES = "plugin/skills/secureconfig/references"

# The modes a staged file may carry: 0644, or 0755 where the input's same path is 0755.
PLAIN_MODE, EXEC_MODE = 0o644, 0o755

# The link shapes of G5, over one line of text. The inline and definition shapes are the ones
# scripts/build-llms-full.sh rewrites, so the two tools read the same targets.
INLINE = re.compile(r"(\]\([ \t]*)(?:<([^<>\n]*)>|([^\s<>()]+)(?=[ \t]|\)))")
DEFINE = re.compile(r"^([ \t>]*(?:(?:[-+*]|\d{1,9}[.)])[ \t]+)*\[[^\]]+\]:[ \t]*)(?:<([^<>\n]*)>|(\S+))")
KEEP = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|#)")
TICKS = re.compile(r"`+")
REPO_LINK = re.compile(
    r"(?i)\bhttps?://(?:www\.)?github\.com/[A-Za-z0-9-]+/secureconfig/(blob|raw|tree)/main/"
    r"([A-Za-z0-9._+@%/-]*)")
HISTORY_LINK = re.compile(r"(?i)github\.com/[A-Za-z0-9-]+/secureconfig/(?:pull|commit|compare|actions)(?:/|\b)")
SITE_URL = re.compile(r"""(?i)\b(?:href|src)\s*=\s*["'](/[^"'#?]*)""")
HEX_RUN = re.compile(r"[0-9a-fA-F]{12,}")
# A versioned archive name, the only target a latest redirect may name.
ARCHIVE_NAME = re.compile(r"secureconfig(?:-plugin)?-1\.0\.[1-9][0-9]*\.zip")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The most bytes one zTXt or iTXt chunk, or all of one zip's members, may decompress to; more
# refuses the file rather than scanning it partially.
CHUNK_LIMIT = 10 * 1024 * 1024
ZIP_LIMIT = 256 * 1024 * 1024

MASK = "[…]"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_text(data):
    """A staged file is text when it holds no NUL byte and decodes as UTF-8."""
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def text_lines(text):
    """The lines of a text file, numbered from 1; a final LF ends the last line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return list(enumerate(parts, 1))


def walk_tree(root):
    """({relative path: mode} for the regular files, [directory paths], [findings]) under root,
    over lstat, following no symbolic link. A finding is recorded for a symbolic link, another
    non-regular entry, an entry that cannot be listed or read, and a path that leaves the
    allowlist's path characters, which covers any .git entry, control character and .. segment."""
    files, dirs, findings = {}, [], []
    pending = [root]
    while pending:
        folder = pending.pop()
        try:
            with os.scandir(folder) as scan:
                entries = sorted(scan, key=lambda entry: entry.name)
        except OSError as exc:
            rel = os.path.relpath(folder, root).replace(os.sep, "/")
            findings.append(f"{rel}: the directory cannot be listed ({lists.os_reason(exc)})")
            continue
        for entry in entries:
            rel = os.path.relpath(entry.path, root).replace(os.sep, "/")
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as exc:
                findings.append(f"{rel}: cannot be examined ({lists.os_reason(exc)})")
                continue
            if stat.S_ISLNK(info.st_mode):
                findings.append(f"{rel}: is a symbolic link; the export carries regular files only")
                continue
            problem = lists.path_problem(rel, "exact")
            if problem:
                findings.append(f"{rel!r}: {problem}")
                continue
            if stat.S_ISDIR(info.st_mode):
                dirs.append(rel)
                pending.append(entry.path)
            elif stat.S_ISREG(info.st_mode):
                files[rel] = stat.S_IMODE(info.st_mode)
            else:
                findings.append(f"{rel}: is not a regular file or a directory")
    return files, dirs, findings


class Tree:
    """The staged tree: its files, directories, hygiene findings and cached contents."""

    def __init__(self, root):
        self.root = Path(root)
        self.files, self.dirs, self.findings = walk_tree(str(self.root))
        self.data = {}
        self.unreadable = set()
        for rel in sorted(self.files):
            try:
                self.data[rel] = (self.root / rel).read_bytes()
            except OSError as exc:
                self.unreadable.add(rel)
                self.findings.append(f"{rel}: cannot be read ({lists.os_reason(exc)}); an "
                                     f"unscanned file refuses the export")

    def text(self, rel):
        """The decoded text of one readable staged file, or None for a binary."""
        return is_text(self.data[rel])


def strip_spans(line):
    """The line with every code span (paired equal-length backtick runs) blanked out, so a
    link-shaped string inside one is not read as a link."""
    runs = list(TICKS.finditer(line))
    out, pos, index = [], 0, 0
    while index < len(runs):
        length = len(runs[index].group(0))
        close = next((j for j in range(index + 1, len(runs))
                      if len(runs[j].group(0)) == length), None)
        if close is None:
            index += 1
            continue
        out.append(line[pos:runs[index].start()])
        out.append(" " * (runs[close].end() - runs[index].start()))
        pos, index = runs[close].end(), close + 1
    out.append(line[pos:])
    return "".join(out)


def markdown_targets(text):
    """(line number, target) for each inline link or image target and each link reference
    definition in some Markdown, outside fenced code blocks and code spans."""
    fences = Fences()
    for number, line in text_lines(text):
        if fences.feed(line) or fences.inside:
            continue
        bare = strip_spans(line)
        for match in INLINE.finditer(bare):
            yield number, match.group(2) if match.group(2) is not None else match.group(3)
        match = DEFINE.match(bare)
        if match:
            yield number, match.group(2) if match.group(2) is not None else match.group(3)


def read_commits(history):
    """Every commit id of the private repository, lowercased; Refused when git cannot list
    them, since an unknown history leaves G5 unable to answer."""
    try:
        result = subprocess.run(["git", "rev-list", "--all"], cwd=history, check=True,
                                capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise lists.Refused("git cannot list the private repository's commits "
                            f"({type(exc).__name__})") from exc
    return [line.strip().lower() for line in result.stdout.decode("ascii", "replace").split("\n")
            if line.strip()]


def png_texts(data):
    """The decoded text of each tEXt, zTXt and iTXt chunk of a PNG; ValueError for a PNG this
    parser cannot read to the end, which refuses the file."""
    out, pos = [], len(PNG_SIGNATURE)
    while True:
        if pos + 8 > len(data):
            raise ValueError("truncated chunk header")
        length = int.from_bytes(data[pos:pos + 4], "big")
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if len(chunk) != length or pos + 12 + length > len(data):
            raise ValueError("truncated chunk")
        if ctype == b"tEXt":
            out.append(chunk.decode("latin-1", "replace"))
        elif ctype == b"zTXt":
            keyword, _, rest = chunk.partition(b"\x00")
            out.append(keyword.decode("latin-1", "replace"))
            out.append(decompress(rest[1:]).decode("latin-1", "replace"))
        elif ctype == b"iTXt":
            keyword, _, rest = chunk.partition(b"\x00")
            out.append(keyword.decode("latin-1", "replace"))
            if len(rest) < 2:
                raise ValueError("truncated iTXt chunk")
            compressed = rest[0] == 1
            language, _, rest = rest[2:].partition(b"\x00")
            translated, _, body = rest.partition(b"\x00")
            out.append(language.decode("latin-1", "replace"))
            out.append(translated.decode("utf-8", "replace"))
            out.append((decompress(body) if compressed else body).decode("utf-8", "replace"))
        pos += 12 + length
        if ctype == b"IEND":
            if pos != len(data):
                raise ValueError("bytes after IEND")
            return out


def decompress(data):
    """Inflate one compressed chunk, refusing one that inflates past CHUNK_LIMIT."""
    inflater = zlib.decompressobj()
    out = inflater.decompress(data, CHUNK_LIMIT)
    if inflater.unconsumed_tail:
        raise ValueError("a compressed chunk inflates past the limit")
    return out


def verify_rows(rows, pattern_of, tree, name, show):
    """({(path, line number, casefolded REF)} for the rows whose line still matches, [findings
    for the stale rows]). A row names its file in the staged tree; with show false no finding
    quotes a path."""
    allowed, findings = set(), []
    for row in rows:
        where = f"{name}:{row.line}"
        target = f"{row.path}:{row.number}" if show else "the line it names"
        if row.path not in tree.files or row.path in tree.unreadable:
            findings.append(f"{where}: stale: {target} is not a readable staged file")
            continue
        data = tree.data[row.path]
        rows_lines = data.split(b"\n")
        if data.endswith(b"\n"):
            rows_lines.pop()
        if row.number > len(rows_lines):
            findings.append(f"{where}: stale: {target} is past the end of the file")
            continue
        raw = rows_lines[row.number - 1:row.number]
        if lists.line_sha256(raw[0]) != row.digest:
            findings.append(f"{where}: stale: {target} no longer has the recorded SHA-256")
            continue
        if not pattern_of(row.ref).search(raw[0].decode("utf-8", "replace")):
            findings.append(f"{where}: stale: what it names no longer matches {target}")
            continue
        allowed.add((row.path, row.number, row.ref.casefold()))
    return allowed, findings


class Gate:
    """One run of the gate over one staged tree."""

    def __init__(self, staged, input_dir=None, fresh=None, private=None, history=None):
        self.full = input_dir is not None
        self.staged = Tree(staged)
        self.input_dir = Path(input_dir) if input_dir else None
        self.fresh = Path(fresh) if fresh else None
        self.history = history
        self.findings = {check: [] for check, _ in CHECKS}
        self.ran = set()
        self.terms, self.private_markers, self.private_rows = [], [], []
        lists_root = self.input_dir if self.full else self.staged.root
        self.publish, parse1 = lists.parse_paths(
            lists.read_repo_file(lists_root, lists.ALLOWLIST), lists.ALLOWLIST,
            lists.PUBLISH_KINDS)
        self.findings["G1"] += parse1
        self.deny = None
        if self.full:
            self.deny, parse2 = lists.parse_paths(
                lists.read_repo_file(lists_root, lists.PRIVATE_PATHS), lists.PRIVATE_PATHS,
                ("deny",))
            self.findings["G1"] += parse2
        self.markers, parse3 = lists.parse_markers(
            lists.read_repo_file(lists_root, lists.PUBLIC_MARKERS), lists.PUBLIC_MARKERS,
            allow_empty=False)
        self.findings["G3"] += parse3
        self.rows, parse4 = lists.parse_exceptions(
            lists.read_repo_file(lists_root, lists.PUBLIC_EXCEPTIONS), lists.PUBLIC_EXCEPTIONS,
            {marker.ident for marker in self.markers})
        self.findings["G3"] += parse4
        if self.full:
            self.load_private(private)

    def load_private(self, private):
        """Read and parse the private lists, as tools/export_lists.py --check-private reads
        them, refusing a private directory with any group or other permission or one inside
        the staged or input tree. Parse findings quote no content."""
        dir_fd = lists.open_private_dir(private, ROOT)
        try:
            if os.fstat(dir_fd).st_mode & 0o077:
                raise lists.Refused("the private directory grants group or other permissions; "
                                    "the gate needs it closed to its owner alone")
            real = os.path.realpath(private.rstrip("/") or "/")
            for other in (self.staged.root, self.input_dir):
                tree_real = os.path.realpath(other)
                if os.path.commonpath([real, tree_real]) in (real, tree_real):
                    raise lists.Refused("the private directory is inside the staged or input "
                                        "tree, or holds it")
            data = {name: lists.read_private(dir_fd, name) for name in lists.PRIVATE_FILES}
        finally:
            os.close(dir_fd)
        self.terms, finds1 = lists.parse_terms(data[lists.TERMS])
        self.private_markers, finds2 = lists.parse_markers(
            data[lists.PRIVATE_MARKERS], lists.PRIVATE_MARKERS, allow_empty=True, show=False)
        self.private_rows, finds3 = lists.parse_exceptions(
            data[lists.PRIVATE_EXCEPTIONS], lists.PRIVATE_EXCEPTIONS,
            {marker.ident for marker in self.private_markers},
            {term.text.casefold() for term in self.terms}, show=False)
        self.findings["G4"] += finds1 + finds2 + finds3

    def mask(self, text):
        """The text with every protected-term and private-marker match replaced, so no finding
        prints one, wherever it came from."""
        for term in self.terms:
            text = term.regex.sub(MASK, text)
        for marker in self.private_markers:
            text = marker.regex.sub(MASK, text)
        return text

    def run(self, check, body):
        """Run one check so that an unexpected exception refuses the export as a finding that
        names only the exception's type, which can quote nothing."""
        self.ran.add(check)
        try:
            body()
        except Exception as exc:  # noqa: BLE001  a scanner failure refuses, never passes
            self.findings[check].append(f"the check stopped on an unexpected "
                                        f"{type(exc).__name__}, which refuses the export")

    def g1(self):
        matched = {entry.line: 0 for entry in self.publish}
        for rel in sorted(self.staged.files):
            allow = [entry for entry in self.publish if entry.regex.fullmatch(rel)]
            denied = [entry for entry in (self.deny or []) if entry.regex.fullmatch(rel)]
            for entry in allow:
                matched[entry.line] += 1
            if denied:
                self.findings["G1"].append(
                    f"{rel}: matched by the deny line {lists.PRIVATE_PATHS}:{denied[0].line}; "
                    f"it stays private")
            if not allow and not denied:
                self.findings["G1"].append(f"{rel}: no line of {lists.ALLOWLIST} matches it; "
                                           f"an unknown file refuses the export")
            elif len(allow) > 1:
                numbers = ", ".join(str(entry.line) for entry in allow)
                self.findings["G1"].append(f"{rel}: matched by {len(allow)} lines of "
                                           f"{lists.ALLOWLIST} ({numbers})")
        for entry in self.publish:
            if entry.need == "required" and not matched[entry.line]:
                self.findings["G1"].append(
                    f"{lists.ALLOWLIST}:{entry.line}: {entry.kind} {entry.pattern!r} matches "
                    f"no staged file; a missing required file refuses the export")

    def g2(self):
        self.findings["G2"] += self.staged.findings
        for rel, mode in sorted(self.staged.files.items()):
            if mode == PLAIN_MODE:
                continue
            input_mode = None
            if self.full:
                try:
                    info = os.lstat(self.input_dir / rel)
                    if stat.S_ISREG(info.st_mode):
                        input_mode = stat.S_IMODE(info.st_mode)
                except OSError:
                    input_mode = None
            allowed = mode == EXEC_MODE and (input_mode == EXEC_MODE or not self.full)
            if not allowed:
                self.findings["G2"].append(
                    f"{rel}: has mode {mode:04o}; a staged file is 0644, or 0755 when the "
                    f"input tree's file is 0755")

    def g3(self):
        allowed, stale = verify_rows(
            self.rows, lambda ref: {m.ident: m.regex for m in self.markers}[ref[len("marker:"):]],
            self.staged, lists.PUBLIC_EXCEPTIONS, show=True)
        self.findings["G3"] += stale
        for rel in sorted(self.staged.data):
            text = self.staged.text(rel)
            if text is None:
                continue
            for number, line in text_lines(text):
                for marker in self.markers:
                    if marker.regex.search(line) and \
                            (rel, number, f"marker:{marker.ident}") not in allowed:
                        self.findings["G3"].append(
                            f"{rel}:{number}: holds a hit of the publishable marker "
                            f"{marker.ident} with no matching exception")

    def private_pattern(self, ref):
        if ref.startswith("marker:"):
            return {m.ident: m.regex for m in self.private_markers}[ref[len("marker:"):]]
        return lists.term_regex(ref[len("term:"):])

    def scan_private_text(self, where, rel, text, allowed):
        """Scan decoded text for terms and private markers, honouring the exact exceptions
        when the text is a numbered line of a staged file (where > 0)."""
        for number, line in text_lines(text) if where == "lines" else ((0, text),):
            for term in self.terms:
                if term.regex.search(line) and \
                        (rel, number, f"term:{term.text.casefold()}") not in allowed:
                    place = f"{rel}:{number}" if number else rel
                    self.findings["G4"].append(
                        f"{self.mask(place)}: holds term {term.line} of {lists.TERMS}")
            for marker in self.private_markers:
                if marker.regex.search(line) and \
                        (rel, number, f"marker:{marker.ident}") not in allowed:
                    place = f"{rel}:{number}" if number else rel
                    self.findings["G4"].append(
                        f"{self.mask(place)}: holds a hit of private marker {marker.line} of "
                        f"{lists.PRIVATE_MARKERS}")

    def g4(self):
        allowed, stale = verify_rows(self.private_rows, self.private_pattern, self.staged,
                                     lists.PRIVATE_EXCEPTIONS, show=False)
        self.findings["G4"] += stale
        for rel in sorted(self.staged.files) + sorted(self.staged.dirs):
            for term in self.terms:
                if term.regex.search(rel):
                    self.findings["G4"].append(f"{self.mask(rel)}: the path's name holds term "
                                               f"{term.line} of {lists.TERMS}")
            for marker in self.private_markers:
                if marker.regex.search(rel):
                    self.findings["G4"].append(
                        f"{self.mask(rel)}: the path's name holds a hit of private marker "
                        f"{marker.line} of {lists.PRIVATE_MARKERS}")
        for rel in sorted(self.staged.data):
            data = self.staged.data[rel]
            text = self.staged.text(rel)
            if text is not None:
                self.scan_private_text("lines", rel, text, allowed)
            else:
                self.scan_binary(rel, data)

    def scan_binary(self, rel, data, member=""):
        """Scan one binary: its three decoded readings for terms, its UTF-8 reading for the
        private markers, and its PNG text chunks for both."""
        place = f"{rel}!{member}" if member else rel
        for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
            reading = data.decode(encoding, "replace")
            for term in self.terms:
                if term.regex.search(reading):
                    self.findings["G4"].append(
                        f"{self.mask(place)}: its {encoding} reading holds term {term.line} "
                        f"of {lists.TERMS}")
            if encoding == "utf-8":
                for marker in self.private_markers:
                    if marker.regex.search(reading):
                        self.findings["G4"].append(
                            f"{self.mask(place)}: its {encoding} reading holds a hit of "
                            f"private marker {marker.line} of {lists.PRIVATE_MARKERS}")
        if data.startswith(PNG_SIGNATURE):
            try:
                texts = png_texts(data)
            except (ValueError, zlib.error):
                self.findings["G4"].append(f"{self.mask(place)}: a PNG whose chunks cannot be "
                                           f"read to the end; an unscanned file refuses")
                return
            for chunk in texts:
                self.scan_private_text("chunk", place, chunk, set())

    def g5(self):
        files, dirs = self.staged.files, set(self.staged.dirs)

        def staged_path(path, want_dir):
            if want_dir:
                return path in dirs
            return path in files or path in dirs
        for rel in sorted(self.staged.data):
            text = self.staged.text(rel)
            if text is None:
                continue
            if rel.endswith(".md"):
                for number, target in markdown_targets(text):
                    if KEEP.match(target) or not target:
                        continue
                    path = target.partition("#")[0]
                    if not path:
                        continue
                    joined = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
                    if path.startswith("/") or joined == ".." or joined.startswith("../"):
                        self.findings["G5"].append(f"{rel}:{number}: the link {target!r} "
                                                   f"leaves the staged tree")
                    elif not staged_path(joined, path.endswith("/")):
                        self.findings["G5"].append(f"{rel}:{number}: the link {target!r} "
                                                   f"names no staged path")
            for number, line in text_lines(text):
                for match in REPO_LINK.finditer(line):
                    route, raw = match.group(1).lower(), unquote(match.group(2))
                    path = raw.rstrip("/")
                    bad = not path or ".." in path.split("/")
                    if bad or not staged_path(path, route == "tree"):
                        self.findings["G5"].append(
                            f"{rel}:{number}: a {route}/main link into this project names no "
                            f"staged {'directory' if route == 'tree' else 'file'}")
                if HISTORY_LINK.search(line):
                    self.findings["G5"].append(f"{rel}:{number}: holds a link into the "
                                               f"development history (pull, commit, compare "
                                               f"or actions)")
                if rel.startswith("site/") and rel.endswith(".html"):
                    for match in SITE_URL.finditer(line):
                        target = match.group(1)
                        resolved = "site" + (target + "index.html" if target.endswith("/")
                                             else target)
                        if resolved not in files:
                            self.findings["G5"].append(
                                f"{rel}:{number}: the root-relative link {target!r} names no "
                                f"staged site path")
        if self.full:
            commits = read_commits(self.history)
            prefixes = {}
            for commit in commits:
                prefixes.setdefault(commit[:12], []).append(commit)
            for rel in sorted(self.staged.data):
                text = self.staged.text(rel)
                if text is None:
                    continue
                for number, line in text_lines(text):
                    for match in HEX_RUN.finditer(line):
                        run = match.group(0).lower()
                        hits = prefixes.get(run[:12], ())
                        if any(c.startswith(run) or run.startswith(c) for c in hits):
                            self.findings["G5"].append(
                                f"{rel}:{number}: holds a run of {len(run)} hexadecimal "
                                f"characters that names a commit of the private repository")

    def g6(self):
        for rel in sorted(self.staged.data):
            entries = [entry for entry in self.publish if entry.regex.fullmatch(rel)]
            if len(entries) != 1:
                continue  # G1 already refused this file
            source = self.fresh if entries[0].kind == "render" else self.input_dir
            kind = "fresh render" if entries[0].kind == "render" else "input tree"
            path = source / rel
            try:
                if path.is_symlink():
                    raise OSError("it is a symbolic link")
                expected = path.read_bytes()
            except OSError:
                self.findings["G6"].append(f"{rel}: the {kind} has no readable file to compare "
                                           f"against; unverifiable drift refuses the export")
                continue
            if expected != self.staged.data[rel]:
                self.findings["G6"].append(f"{rel}: does not equal the {kind}")
        version = self.staged.data.get("VERSION")
        manifest = self.staged.data.get("plugin/plugin.json")
        if version is not None and manifest is not None:
            try:
                declared = json.loads(manifest.decode("utf-8"))["version"]
            except (UnicodeDecodeError, ValueError, KeyError, TypeError):
                declared = None
            if declared is None or version.decode("utf-8", "replace").strip() != declared:
                self.findings["G6"].append("VERSION does not equal plugin/plugin.json's "
                                           "version")

    def g7(self):
        for name in NAMED_REQUIRED:
            if name not in self.staged.files:
                self.findings["G7"].append(f"{name}: is not staged")
        for entry in self.publish:
            if entry.need != "required":
                continue
            for rel in self.staged.files:
                if entry.regex.fullmatch(rel) and len(self.staged.data.get(rel, b"x")) == 0:
                    self.findings["G7"].append(f"{rel}: is empty; a required file must have "
                                               f"content")
        guides_root = self.input_dir if self.full else self.staged.root
        for guide in counted_guides(Path(guides_root)):
            if guide not in self.staged.files:
                self.findings["G7"].append(f"{guide}: a counted guide with no staged root copy")
            if f"{REFERENCES}/{guide}" not in self.staged.files:
                self.findings["G7"].append(f"{guide}: a counted guide with no staged plugin "
                                           f"reference copy")
        sums = None
        if "releases/SHA256SUMS" in self.staged.data:
            sums = set()
            for line in self.staged.data["releases/SHA256SUMS"].decode("utf-8",
                                                                       "replace").split("\n"):
                fields = line.split()
                if fields:
                    sums.add(fields[0].lower())
        for rel in sorted(self.staged.data):
            if rel.startswith("site/downloads/") and rel.endswith(".zip"):
                if sums is None:
                    self.findings["G7"].append(f"{rel}: staged with no releases/SHA256SUMS to "
                                               f"list it")
                elif sha256(self.staged.data[rel]) not in sums:
                    self.findings["G7"].append(f"{rel}: its SHA-256 is not listed in "
                                               f"releases/SHA256SUMS")
        if "site/_redirects" in self.staged.data:
            text = self.staged.data["site/_redirects"].decode("utf-8", "replace")
            for number, line in text_lines(text):
                line = line.strip()
                if not line or line.startswith("#") or "-latest" not in line.split()[0]:
                    continue
                fields = line.split()
                target = fields[1] if len(fields) == 3 else ""
                ok = (len(fields) == 3 and fields[2] == "302" and target.startswith("/")
                      and ARCHIVE_NAME.fullmatch(posixpath.basename(target)) is not None
                      and "site" + target in self.staged.files)
                if not ok:
                    self.findings["G7"].append(
                        f"site/_redirects:{number}: a latest rule must be a 302 to a staged "
                        f"versioned archive")

    def g8(self):
        baseline = sorted(rel for rel in self.staged.files
                          if rel.startswith("site/assets/baseline/"))
        fonts = sorted(rel for rel in self.staged.files
                       if rel.lower().endswith((".woff", ".woff2")))
        if baseline or fonts:
            pins = self.read_pin()
            for rel in baseline:
                key = rel[len("site/"):]
                if pins is None:
                    break
                if pins.get(key) != sha256(self.staged.data.get(rel, b"")):
                    self.findings["G8"].append(f"{rel}: does not hash to its entry in the "
                                               f"input tree's .baseline/pin.toml")
            for rel in fonts:
                if rel not in baseline:
                    self.findings["G8"].append(f"{rel}: a compressed font outside the pinned "
                                               f"template files; this gate cannot scan inside "
                                               f"its compression, so only a pinned copy crosses")
        for rel in sorted(self.staged.data):
            if rel.lower().endswith(".zip"):
                self.scan_zip(rel, self.staged.data[rel])

    def read_pin(self):
        """{path relative to site/: sha256} from the input tree's .baseline/pin.toml, or None
        with a finding when it cannot be read, which refuses every pinned comparison."""
        if tomllib is None:
            self.findings["G8"].append(".baseline/pin.toml: this interpreter cannot parse "
                                       "TOML, so the pin cannot be checked")
            return None
        try:
            pin = tomllib.loads((self.input_dir / ".baseline" / "pin.toml")
                                .read_text(encoding="utf-8"))
            table = pin["files"]
            return {key: str(value) for key, value in table.items()}
        except (OSError, UnicodeError, KeyError, TypeError, tomllib.TOMLDecodeError):
            self.findings["G8"].append(".baseline/pin.toml: the input tree's pin cannot be "
                                       "read, so the template files cannot be verified")
            return None

    def scan_zip(self, rel, data):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                total = 0
                for info in archive.infolist():
                    total += info.file_size
                    if total > ZIP_LIMIT:
                        raise ValueError("the archive inflates past the limit")
                    member = archive.read(info.filename)
                    for term in self.terms:
                        if term.regex.search(info.filename):
                            self.findings["G4"].append(
                                f"{self.mask(rel)}!: a member name holds term {term.line} of "
                                f"{lists.TERMS}")
                    text = is_text(member)
                    if text is not None:
                        self.scan_private_text("chunk", f"{rel}!{info.filename}", text, set())
                    else:
                        self.scan_binary(rel, member, member=info.filename)
        except Exception:  # noqa: BLE001  a zip the scanner cannot finish refuses the export
            self.findings["G8"].append(f"{self.mask(rel)}: an archive this gate cannot scan "
                                       f"to the end refuses the export")

    def execute(self, public_only):
        bodies = {"G1": self.g1, "G2": self.g2, "G3": self.g3, "G4": self.g4, "G5": self.g5,
                  "G6": self.g6, "G7": self.g7, "G8": self.g8}
        for check, _ in CHECKS:
            if public_only and check not in PUBLIC_ONLY_CHECKS:
                continue
            self.run(check, bodies[check])


def write_verdicts(path, record, staged):
    """Write the per-check verdicts as one new JSON file, mode 0600, never overwriting and
    never inside the staged tree."""
    real = os.path.realpath(path)
    staged_real = os.path.realpath(staged)
    if os.path.commonpath([real, staged_real]) == staged_real:
        raise lists.Refused("the verdicts file would land inside the staged tree")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
    except OSError as exc:
        raise lists.Refused(f"the verdicts file cannot be created "
                            f"({lists.os_reason(exc)})") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=1, sort_keys=True)
        handle.write("\n")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else [str(arg) for arg in argv]
    quiet = any(arg.startswith(lists.PRIVATE_ARGUMENTS) for arg in argv)
    parser = lists.QuietParser(description="The export gate over a staged tree.",
                               allow_abbrev=False, quiet=quiet)
    parser.add_argument("--staged", required=True, help="the staged tree to judge")
    parser.add_argument("--input", default=None, help="the input tree the export was built "
                                                      "from (full mode)")
    parser.add_argument("--fresh", default=None, help="an independent fresh render of every "
                                                      "rendered file (full mode)")
    parser.add_argument("--private-dir", default=None,
                        help=f"the directory holding the private lists (read only); without "
                             f"it, ${lists.PRIVATE_DIR_ENV} when set, else the built-in default")
    parser.add_argument("--history", default=str(ROOT),
                        help="the private repository whose commits no staged hex run may name "
                             "(default: the one holding this tool)")
    parser.add_argument("--verdicts", default=None,
                        help="write the per-check verdicts to this new file for the receipt")
    parser.add_argument("--public-only", action="store_true",
                        help="run only the checks that need no private input; this mode never "
                             "approves an export")
    args = parser.parse_args(argv)
    try:
        if args.public_only:
            if args.input or args.fresh or args.private_dir:
                raise lists.Refused("--public-only takes no --input, --fresh or --private-dir")
            gate = Gate(args.staged)
        else:
            if not args.input or not args.fresh:
                raise lists.Refused("full mode needs --input and --fresh; a drift check "
                                    "without them cannot pass")
            for name, value in (("staged", args.staged), ("input", args.input),
                                ("fresh", args.fresh)):
                if not os.path.isdir(value):
                    raise lists.Refused(f"the {name} tree is not a directory")
            private = lists.private_directory(args.private_dir, os.environ)
            gate = Gate(args.staged, args.input, args.fresh, private, args.history)
        gate.execute(args.public_only)
        total = 0
        verdicts = {}
        for check, title in CHECKS:
            label = f"{check} {title}"
            if check not in gate.ran:
                print(f"  SKIP  {label}: not run in public-only mode, which never approves "
                      f"an export")
                verdicts[check] = {"status": "SKIP", "findings": 0}
                continue
            found = gate.findings[check]
            for finding in found:
                print(f"  FAIL  {check} {gate.mask(finding)}")
            total += len(found)
            if found:
                print(f"  FAIL  {label}: {len(found)} finding"
                      f"{'' if len(found) == 1 else 's'}")
            else:
                print(f"  ok    {label}: no findings")
            verdicts[check] = {"status": "FAIL" if found else "ok", "findings": len(found)}
        approved = not args.public_only and total == 0
        record = {"mode": "public-only" if args.public_only else "full",
                  "approved": approved, "checks": verdicts,
                  "staged_files": len(gate.staged.files)}
        if args.verdicts:
            write_verdicts(args.verdicts, record, args.staged)
        if total:
            print(f"  FAIL  export gate: refused ({total} finding"
                  f"{'' if total == 1 else 's'})")
            return 1
        if approved:
            print(f"  ok    export gate: every check passed over {len(gate.staged.files)} "
                  f"staged files; the export may proceed")
        else:
            print(f"  ok    export gate (public-only): the public checks passed over "
                  f"{len(gate.staged.files)} staged files; this mode never approves an export")
        return 0
    except lists.Refused as exc:
        print(f"  FAIL  {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001
        # A traceback could quote what a private list or a staged file holds.
        print(f"  FAIL  the export gate stopped on an unexpected {type(exc).__name__}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
