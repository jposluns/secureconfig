#!/usr/bin/env python3
"""The export gate: the only door to a public export, and it fails closed.

The gate judges a staged tree that the export tool assembled. Any error, unknown file or
scanner failure refuses the whole export: a check that cannot run to completion is a failure,
never a pass. It prints one ok or FAIL line per check, each finding on a FAIL line of its own
before its check's line, and writes the per-check verdicts and the staged file list into the
record the caller names with --verdicts, for the receipt the export tool keeps privately.

THE CHECKS. Every one fails closed.

  G1 allowlist     Every staged file is matched by exactly one copy or render line of
                   export/public-allowlist.txt. A file no line matches, a file a deny line of
                   export/private-paths.txt matches, a file two lines match, and a required
                   line that matches no staged file each refuse.
  G2 file hygiene  A symbolic link, a non-regular file, a file with more than one hard link
                   (a second name could swap the judged bytes), any .git entry, a path that
                   leaves the allowlist's path characters or holds a . or .. segment, an
                   unreadable file, and a mode other than 0644, or 0755 where the input tree's
                   same path is 0755, each refuse. Public-only mode has no input tree, so
                   there only 0644 passes.
  G3 publishable   A hit of export/public-markers.txt in a staged text file refuses, outside
     markers       the exact rows of export/public-exceptions.tsv; a stale row refuses too.
                   Each line is scanned as written and in a folded copy: NFKC-normalized with
                   every Unicode format character (category Cf, such as U+200B) and every
                   combining mark (category Mn, such as U+0335) removed (see DISCLOSED LIMITS
                   for the homoglyphs folding cannot reach).
  G4 protected     Full mode only. A hit of a protected term or a private marker in a staged
     terms and     path name or in file contents refuses, outside the exact rows of the private
     private       exceptions list. Text is scanned as UTF-8 lines, each also in the folded
     markers       copy G3 above describes. A binary file's raw bytes are searched for each
                   term's UTF-8, UTF-16LE and UTF-16BE encodings at any byte offset (case
                   variants per character, no word boundary, so the byte search is broader than
                   the text scan). Its decoded UTF-8, UTF-16LE and UTF-16BE readings, each
                   UTF-16 one at both byte alignments, are scanned for the private markers and,
                   folded, for the terms. The tEXt, zTXt and iTXt chunks of a PNG are
                   decoded and scanned, and its image data is inflated and scanned as bytes.
                   Any zlib stream the gate identifies (by its two header bytes and a
                   successful inflate) is inflated and scanned the same way, nested at most two
                   levels down; an identified stream or PNG image data nested deeper refuses
                   rather than crossing unscanned, as a too-deep archive does.
                   No finding prints a term, a private marker or a private-list
                   line: it names the list and the entry's line number, a printed path is
                   masked where it matches, and a control character in any printed name is
                   escaped, so a crafted name cannot forge an output line.
  G5 private       (a) Every relative Markdown link, every root-relative link in a staged site
     references    page and every github.com/<owner>/secureconfig blob, raw or tree link on
                   main must name a staged path. (b) Any github.com/<owner>/secureconfig link
                   to pull, commit, commits, compare or actions refuses. (c) Full mode only: a
                   run of 12 or more hexadecimal characters in a text file, in a staged path
                   name or in an archive member name that names, or holds at any offset, the
                   first 12 characters of a commit id of the private repository (git rev-list
                   --all, read privately) refuses; the finding never prints the characters,
                   and a printed path is shown folded with every such run masked.
                   The repository-link, history-link, site-link and
                   hexadecimal scans read each line as written and in its folded copy; the
                   relative Markdown targets are read as written (see DISCLOSED LIMITS). The
                   gate refuses a --history directory that is not the top level of its own
                   repository (it never walks up into an enclosing checkout), a shallow clone
                   and a partial (promisor-remote) clone, whose commit lists can be incomplete,
                   and a history that lists no commits.
  G6 drift         Full mode only. Each staged file a render line matches must equal the
                   independent fresh render the caller supplies with --fresh; each staged file
                   a copy line matches must equal its bytes in the input tree; and VERSION must
                   equal plugin/plugin.json's version. Each comparison, like every read of a
                   list or pin from a tree, opens only a regular file, with O_NOFOLLOW and
                   O_NONBLOCK: a symbolic link, FIFO, socket or device at a compared path
                   refuses at once rather than hanging the gate.
  G7 completeness  Every file a required line matches is present and non-empty, and README.md,
                   LICENSE, NOTICE, VERSION and CHANGELOG.md are staged. Every counted guide of
                   the input tree (the staged tree in public-only mode) has a root copy and a
                   plugin reference copy. When archives are staged under site/downloads/, each
                   one's SHA-256 is listed in releases/SHA256SUMS, and every latest rule of
                   site/_redirects is a 302 to a staged versioned archive.
  G8 binaries      Full mode only. Every staged file under site/assets/baseline/ hashes to its
                   entry in the input tree's .baseline/pin.toml. A staged file or an archive
                   member is opened as a zip archive when its name ends in .zip or its content
                   identifies one (the local-header signature at offset 0, or an end-of-
                   central-directory record zipfile can read), whatever it is named; one
                   either reading identifies that cannot be scanned to its end refuses. Every
                   member of such an archive,
                   read by its central directory entry so a duplicated member name
                   hides nothing, is scanned as G4 scans a file (though the exact exceptions
                   never apply inside an archive), and member names are scanned, as written
                   and folded, for terms, private markers and commit ids. A text member also
                   gets the
                   publishable-marker scan (no exception applies inside an archive), the
                   history, repository and commit scans, and, when it is Markdown or HTML, the
                   link-target checks, resolved against the archive's own members. A member
                   that is itself a zip is scanned the same
                   way, at most two archive levels below a staged archive and at most ZIP_LIMIT
                   inflated bytes in all; past either bound the archive refuses. Every byte of
                   a staged archive must be explained by a member entry, the central directory,
                   an end record or the archive comment: an unexplained span is scanned as G4
                   scans bytes and refuses the archive. A member's data descriptor must hold
                   the central directory's CRC and sizes, 8 bytes per size when the member's
                   local zip64 extra field is present, else 4; a descriptor that does not
                   match refuses. Any other
                   staged file or archive member the gate identifies as compressed content it
                   cannot scan inside (gzip, compress, bzip2, xz, zstandard, lzip, lzma,
                   brotli, 7z, rar, or a .woff or .woff2 font, by name suffix or, for a
                   binary that is not a PNG or a zip, by a known signature at any byte
                   offset) refuses, unless it is a staged site/assets/baseline/
                   file, which crosses only against its pin.

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
                   It takes no --input, --fresh, --private-dir or --history, and it never
                   approves an export, whatever it finds.

WHAT THE SCANS READ. A staged file is text when it holds no NUL byte and decodes as UTF-8;
every other file is a binary. The marker, link and hexadecimal scans read text files, each
line as written and, except for the relative Markdown targets, in its folded copy. Binaries
are scanned for terms and private markers as G4 above says, through their PNG text chunks and
inflated image data, through any zlib stream the gate identifies, and, when name or content
identifies a zip, through their zip
members, whose text members also get the marker, link and commit scans. The Markdown link
scan is this tool's own line scanner over the same inline,
definition, code-span and fence shapes scripts/build-llms-full.sh rewrites; it is not the
pinned CommonMark parser, which is not in the standard library, so a link form only that
parser sees is caught at build time, not here.

DISCLOSED LIMITS. A root-relative url(...) in a staged CSS file is not scanned here; the
build's scripts/build-llms-full.sh scans CSS links at build time. The blob, raw and tree link
rule is pinned to main, so such a link naming another branch is not matched here, while a
commit-pinned link falls to G5c. The hexadecimal scan reads text files, archive text members,
staged path names and archive member names; a commit id buried in a binary's bytes alone is
not matched. The relative Markdown targets are read from each line as written, not from its
folded copy: a link whose brackets need normalization is not a link to any renderer, and a
target spelled in such characters matches no staged path, so the raw scan already refuses it.
The history-link rule matches pull, commit, commits, compare and actions; an issues or
releases link is not matched, since the public repository may legitimately name its own. A
term inside a longer word is found in a binary's bytes but not in a text line or a path name,
which keep the word boundary export/FORMAT.md sets for terms. A latest redirect may name only
a 1.0-series versioned archive; a later series refuses until the pattern here is widened,
which fails closed. The zlib
identification needs the two header bytes, so a raw deflate stream with no header, and a
compressed format this gate does not know, are not found, which is why identified compressed
content the gate cannot read refuses, and why a staged archive's unexplained byte spans
refuse. Folding strips format characters and combining marks and applies NFKC, but a
homoglyph, a letter from another script that NFKC does not fold to the listed spelling,
still defeats a literal term, marker or hexadecimal list; that is an inherent limit of
matching literal spellings. Each staged file is read and judged whole in memory, and a large
archive is scanned member by member within ZIP_LIMIT and ZIP_DEPTH, so a huge input costs
minutes and memory but stays bounded; a MemoryError refuses like any other
error. Inflated image bytes are searched for encoded terms
only: a term shown as drawn glyphs in the pixels is a picture, not text, and no byte scan can
read it.

Exit 0 when every check that ran passed, 1 on a finding, 2 when an input cannot be read, the
private directory or a list is refused, or the verdicts file cannot be created. A check that
is refused while it runs, such as G5 on a refused history, records its refusal as a finding
and exits 1. Nothing is written anywhere but the --verdicts file, which is created new (never
overwritten), mode 0600, and records the mode, the approval, the per-check verdicts and every
staged path with its size and the SHA-256 of its judged bytes (null for a file that could not
be read, which itself refuses the export).
"""
import argparse
import collections
import errno
import hashlib
import io
import json
import os
import posixpath
import re
import stat
import subprocess
import sys
import unicodedata
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
HISTORY_LINK = re.compile(r"(?i)github\.com/[A-Za-z0-9-]+/secureconfig/(?:pull|commits?|compare|actions)(?:/|\b)")
SITE_URL = re.compile(r"""(?i)\b(?:href|src)\s*=\s*["'](/[^"'#?]*)""")
HEX_RUN = re.compile(r"[0-9a-fA-F]{12,}")
# A versioned archive name, the only target a latest redirect may name; pinned to the 1.0
# series, so a redirect to a later series refuses until this is widened, which fails closed.
ARCHIVE_NAME = re.compile(r"secureconfig(?:-plugin)?-1\.0\.[1-9][0-9]*\.zip")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# The most bytes one compressed chunk or identified stream, or all of one file's identified
# streams, may inflate to; more refuses the file rather than scanning it partially.
CHUNK_LIMIT = 10 * 1024 * 1024
# The most bytes the members of one staged archive and everything nested in it may inflate to.
ZIP_LIMIT = 256 * 1024 * 1024
# How many archive levels below a staged archive are scanned; a zip nested deeper refuses.
ZIP_DEPTH = 2
# How many levels of inflated content (PNG image data, identified zlib streams) are scanned.
STREAM_DEPTH = 2
# The most identified zlib streams scanned in one blob; more refuses the file.
MAX_STREAMS = 32

# Compressed content the gate cannot scan inside, by name suffix and, for a binary, by a
# leading signature searched at any byte offset. zip and PNG are not here: the gate opens
# both and accounts for every byte, so their compressed innards may hold signature-like
# bytes without naming an unscannable blob.
COMPRESSED_SUFFIXES = (
    (".gz", "gzip"), (".tgz", "gzip"), (".bz2", "bzip2"), (".tbz2", "bzip2"),
    (".xz", "xz"), (".txz", "xz"), (".zst", "zstandard"), (".br", "brotli"),
    (".lz", "lzip"), (".lzma", "lzma"), (".7z", "7z"), (".rar", "rar"),
    (".woff", "compressed font"), (".woff2", "compressed font"))
COMPRESSED_SIGNATURES = (
    (b"\x1f\x8b", "gzip"), (b"\x1f\x9d", "compress"), (b"BZh", "bzip2"),
    (b"\xfd7zXZ\x00", "xz"), (b"\x28\xb5\x2f\xfd", "zstandard"),
    (b"7z\xbc\xaf\x27\x1c", "7z"), (b"Rar!\x1a\x07", "rar"),
    (b"wOFF", "compressed font"), (b"wOF2", "compressed font"))

# The two header bytes that can open a zlib stream: a deflate CMF (low nibble 8, window up to
# 32 KiB) and a FLG that makes the pair a multiple of 31.
ZLIB_HEADERS = re.compile(b"|".join(
    re.escape(bytes((cmf, flg))) for cmf in range(0x08, 0x80, 0x10)
    for flg in range(256) if ((cmf << 8) | flg) % 31 == 0))

MASK = "[…]"

FileInfo = collections.namedtuple("FileInfo", "mode size nlink")


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


def folded(text):
    """The folded copy of text when it differs, else None, so each scan can read a spelling
    that normalization or invisible characters would hide, without scanning unchanged text
    twice. Folding removes every Unicode format character (category Cf, such as U+200B) and
    every combining mark (category Mn, such as U+0335), NFKC-normalizes what remains, and
    removes the combining marks a compatibility decomposition introduces. A homoglyph from
    another script survives NFKC: DISCLOSED LIMITS names that residue of a literal list."""
    kept = "".join(ch for ch in text if unicodedata.category(ch) not in ("Cf", "Mn"))
    normalized = unicodedata.normalize("NFKC", kept)
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return normalized if normalized != text else None


def hex_hits(line, prefixes):
    """The lengths of the hexadecimal runs of 12 or more characters in the line, read as
    written and folded, that name or hold one of the commit prefixes, each length once."""
    fold = folded(line)
    lengths = set()
    for copy in (line,) if fold is None else (line, fold):
        for match in HEX_RUN.finditer(copy):
            run = match.group(0).lower()
            if any(run[i:i + 12] in prefixes for i in range(len(run) - 11)):
                lengths.add(len(run))
    return sorted(lengths)


def printable(text):
    """The text with every character that is not printable (control and format characters
    among them) written as its backslash escape, so a crafted name cannot forge a line of
    this gate's output."""
    return "".join(ch if ch == " " or ch.isprintable() else repr(ch)[1:-1] for ch in text)


def term_byte_patterns(text):
    """[(encoding, compiled bytes pattern)] matching the term's encoded bytes at any byte
    offset: each character as itself and its single-character lower, upper and casefolded
    variants, with no word boundary, which only widens what the text scan refuses."""
    out = []
    for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
        groups = []
        for char in text:
            variants = {char} | {v for v in (char.lower(), char.upper(), char.casefold())
                                 if len(v) == 1}
            encoded = sorted({v.encode(encoding) for v in variants})
            if len(encoded) == 1:
                groups.append(re.escape(encoded[0]))
            else:
                groups.append(b"(?:" + b"|".join(re.escape(v) for v in encoded) + b")")
        out.append((encoding, re.compile(b"".join(groups))))
    return out


def is_zip_content(data):
    """Whether DATA identifies a zip archive by content alone: the local-header signature at
    offset 0, or an end-of-central-directory record zipfile can read. A hit only sends the
    bytes to the zip scan, which refuses whatever it cannot read to the end."""
    return data.startswith(b"PK\x03\x04") or zipfile.is_zipfile(io.BytesIO(data))


def compressed_kind(name, data):
    """A label when NAME or DATA identifies compressed content this gate cannot scan inside,
    else None. A known leading signature is searched at any byte offset of a binary, so a
    blob embedded after a header, or inside a container such as a tar, is found, not only one
    at offset 0. zip and PNG are never identified here: the gate opens both and accounts for
    every byte. The signatures are
    read only on a binary, so text that happens to hold one is not refused."""
    lowered = name.lower()
    for suffix, label in COMPRESSED_SUFFIXES:
        if lowered.endswith(suffix):
            return label
    if (is_text(data) is None and not data.startswith(PNG_SIGNATURE)
            and not is_zip_content(data)):
        for magic, label in COMPRESSED_SIGNATURES:
            if data.find(magic) >= 0:
                return label
    return None


def zlib_streams(data):
    """The inflated bytes of each zlib stream the gate identifies in data: a valid two-byte
    header followed by bytes that inflate. ValueError when the streams inflate past
    CHUNK_LIMIT in all or number more than MAX_STREAMS, which refuses the file rather than
    scanning it partially. A truncated stream yields what it inflated before it stopped."""
    out, pos, budget = [], 0, CHUNK_LIMIT
    view = memoryview(data)
    step = 1 << 16
    while True:
        match = ZLIB_HEADERS.search(data, pos)
        if match is None:
            return out
        start = match.start()
        inflater = zlib.decompressobj()
        produced = bytearray()
        for offset in range(start, len(data), step):
            try:
                produced += inflater.decompress(view[offset:offset + step],
                                                budget - len(produced) + 1)
            except zlib.error:
                break
            if len(produced) > budget:
                raise ValueError("the identified streams inflate past the limit")
            if inflater.eof:
                break
        if produced:
            if len(out) >= MAX_STREAMS:
                raise ValueError("more identified streams than the gate scans")
            out.append(bytes(produced))
            budget -= len(produced)
        pos = start + 1


def read_regular(path):
    """The bytes of PATH, opened with O_NOFOLLOW and O_NONBLOCK and read only when fstat
    shows a regular file, so a symbolic link, FIFO, socket or device raises an OSError at
    once instead of blocking the gate; every caller turns that into its refusal."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(errno.EINVAL, "it is not a regular file")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
    finally:
        os.close(fd)


def read_list(root, relative):
    """One list file of a tree, read as read_regular reads it; Refused, quoting no content,
    when it is absent, unreadable or not a regular file."""
    try:
        return read_regular(os.path.join(str(root), relative))
    except OSError as exc:
        raise lists.Refused(f"cannot read {relative} ({lists.os_reason(exc)})") from exc


def walk_tree(root):
    """({relative path: FileInfo} for the regular files, [directory paths], [findings]) under
    root, over lstat, following no symbolic link. A finding is recorded for a symbolic link,
    another non-regular entry, an entry that cannot be listed or read, and a path that leaves
    the allowlist's path characters, which covers any .git entry, control character and ..
    segment."""
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
                files[rel] = FileInfo(stat.S_IMODE(info.st_mode), info.st_size, info.st_nlink)
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
                self.data[rel] = read_regular(self.root / rel)
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
    """Every commit id of the private repository, lowercased. Refused when git cannot read
    the history, when the history directory is not the top level of its own repository (this
    gate never walks up into an enclosing checkout), or when it lists no commits. A shallow
    clone and a partial (promisor-remote) clone are refused too, since their commit lists
    can be incomplete. Each refusal leaves G5 unable to answer, and no message prints the
    path."""
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=history, check=True,
                             capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise lists.Refused("git cannot name the top level of the --history directory "
                            f"({type(exc).__name__})") from exc
    toplevel = top.stdout.decode("utf-8", "replace").strip()
    if not toplevel or os.path.realpath(toplevel) != os.path.realpath(history):
        raise lists.Refused("the --history directory is not the top level of its own "
                            "repository; this gate does not read an enclosing checkout")
    try:
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=history,
                                 check=True, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise lists.Refused("git cannot say whether the history is shallow "
                            f"({type(exc).__name__})") from exc
    if shallow.stdout.decode("ascii", "replace").strip() != "false":
        raise lists.Refused("the history is a shallow clone, whose commit list is incomplete; "
                            "a partial history cannot answer the commit check")
    try:
        promisor = subprocess.run(
            ["git", "config", "--get-regexp",
             r"^(remote\..*\.(promisor|partialclonefilter)|extensions\.partialclone)$"],
            cwd=history, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise lists.Refused("git cannot read the history's clone configuration "
                            f"({type(exc).__name__})") from exc
    if promisor.returncode != 1:
        raise lists.Refused("the history is a partial clone (a promisor remote or partial-"
                            "clone filter is configured), or its configuration cannot be "
                            "read; a history that may be missing objects cannot answer the "
                            "commit check")
    try:
        result = subprocess.run(["git", "rev-list", "--all"], cwd=history, check=True,
                                capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise lists.Refused("git cannot list the private repository's commits "
                            f"({type(exc).__name__})") from exc
    commits = [line.strip().lower() for line in result.stdout.decode("ascii", "replace").split("\n")
               if line.strip()]
    if not commits:
        raise lists.Refused("the history lists no commits; an empty history cannot answer "
                            "the commit check")
    return commits


def png_parts(data):
    """(decoded text of each tEXt, zTXt and iTXt chunk, inflated image data) of a PNG;
    ValueError for a PNG this parser cannot read and inflate to the end, which refuses the
    file."""
    out, image, pos = [], [], len(PNG_SIGNATURE)
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
        elif ctype == b"IDAT":
            image.append(chunk)
        pos += 12 + length
        if ctype == b"IEND":
            if pos != len(data):
                raise ValueError("bytes after IEND")
            return out, decompress(b"".join(image)) if image else b""


def decompress(data):
    """Inflate one complete compressed stream, refusing one that inflates past CHUNK_LIMIT
    or does not reach its end."""
    inflater = zlib.decompressobj()
    out = inflater.decompress(data, CHUNK_LIMIT)
    if inflater.unconsumed_tail:
        raise ValueError("a compressed chunk inflates past the limit")
    if not inflater.eof:
        raise ValueError("a compressed chunk does not reach its end")
    return out


def zip_gaps(data, archive):
    """[(start, end)] for the byte spans of an open archive's raw data that no member entry
    (its local header, compressed data and data descriptor), central directory record, zip64
    end record, end record or archive comment explains, worked out from the central
    directory's offsets and sizes. A data descriptor's size fields are 8 bytes each when the
    member's local header carries a zip64 extra field, else 4, and the descriptor must hold
    the central directory's CRC and sizes, so it can hide nothing. ValueError for a layout
    this parser cannot account for,
    which refuses the archive."""
    spans = []
    for info in archive.infolist():
        start = info.header_offset
        if data[start:start + 4] != b"PK\x03\x04" or start + 30 > len(data):
            raise ValueError("a member is not where the central directory says")
        name_len = int.from_bytes(data[start + 26:start + 28], "little")
        extra_len = int.from_bytes(data[start + 28:start + 30], "little")
        end = start + 30 + name_len + extra_len + info.compress_size
        if info.flag_bits & 0x08:
            if data[end:end + 4] == b"PK\x07\x08":
                end += 4
            extra = data[start + 30 + name_len:start + 30 + name_len + extra_len]
            zip64, cursor = False, 0
            while cursor + 4 <= len(extra):
                if int.from_bytes(extra[cursor:cursor + 2], "little") == 0x0001:
                    zip64 = True
                cursor += 4 + int.from_bytes(extra[cursor + 2:cursor + 4], "little")
            width = 8 if zip64 else 4
            bound = (1 << (8 * width)) - 1
            wanted = ((info.CRC & 0xFFFFFFFF).to_bytes(4, "little")
                      + (info.compress_size & bound).to_bytes(width, "little")
                      + (info.file_size & bound).to_bytes(width, "little"))
            if data[end:end + len(wanted)] != wanted:
                raise ValueError("a data descriptor does not hold the central directory's "
                                 "crc and sizes")
            end += 4 + 2 * width
        if end > len(data):
            raise ValueError("a member runs past the end of the archive")
        spans.append((start, end))
    pos = archive.start_dir
    for _ in archive.infolist():
        if data[pos:pos + 4] != b"PK\x01\x02":
            raise ValueError("a central directory record is not where its offset says")
        name_len = int.from_bytes(data[pos + 28:pos + 30], "little")
        extra_len = int.from_bytes(data[pos + 30:pos + 32], "little")
        comment_len = int.from_bytes(data[pos + 32:pos + 34], "little")
        pos += 46 + name_len + extra_len + comment_len
    if data[pos:pos + 4] == b"PK\x06\x06":
        pos += 12 + int.from_bytes(data[pos + 4:pos + 12], "little")
        if data[pos:pos + 4] != b"PK\x06\x07":
            raise ValueError("a zip64 end record has no locator")
        pos += 20
    if data[pos:pos + 4] != b"PK\x05\x06":
        raise ValueError("the end record does not follow the central directory")
    comment_len = int.from_bytes(data[pos + 20:pos + 22], "little")
    spans.append((archive.start_dir, min(pos + 22 + comment_len, len(data))))
    spans.sort()
    gaps, covered = [], 0
    for start, end in spans:
        if start > covered:
            gaps.append((covered, start))
        covered = max(covered, end)
    if covered < len(data):
        gaps.append((covered, len(data)))
    return gaps


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
        self.staged_dirs = set(self.staged.dirs)
        self.input_dir = Path(input_dir) if input_dir else None
        self.fresh = Path(fresh) if fresh else None
        self.history = history
        self.commit_prefixes = None
        self.findings = {check: [] for check, _ in CHECKS}
        self.ran = set()
        self.terms, self.private_markers, self.private_rows = [], [], []
        self.term_bytes = []
        lists_root = self.input_dir if self.full else self.staged.root
        self.publish, parse1 = lists.parse_paths(
            read_list(lists_root, lists.ALLOWLIST), lists.ALLOWLIST,
            lists.PUBLISH_KINDS)
        self.findings["G1"] += parse1
        self.deny = None
        if self.full:
            self.deny, parse2 = lists.parse_paths(
                read_list(lists_root, lists.PRIVATE_PATHS), lists.PRIVATE_PATHS,
                ("deny",))
            self.findings["G1"] += parse2
        self.markers, parse3 = lists.parse_markers(
            read_list(lists_root, lists.PUBLIC_MARKERS), lists.PUBLIC_MARKERS,
            allow_empty=False)
        self.findings["G3"] += parse3
        self.rows, parse4 = lists.parse_exceptions(
            read_list(lists_root, lists.PUBLIC_EXCEPTIONS), lists.PUBLIC_EXCEPTIONS,
            {marker.ident for marker in self.markers})
        self.findings["G3"] += parse4
        if self.full:
            self.load_private(private)
            self.term_bytes = [(term, term_byte_patterns(term.text)) for term in self.terms]

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
        """Run one check so that a refusal while it runs becomes a finding (a Refused message
        is a fixed string or an OS reason, never content) and an unexpected exception refuses
        the export as a finding that names only the exception's type, which can quote
        nothing."""
        self.ran.add(check)
        try:
            body()
        except lists.Refused as exc:
            self.findings[check].append(str(exc))
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
        for rel, info in sorted(self.staged.files.items()):
            if info.nlink > 1:
                self.findings["G2"].append(
                    f"{rel}: has {info.nlink} hard links; a second name could swap the "
                    f"judged bytes, so only a singly linked file crosses")
            if info.mode == PLAIN_MODE:
                continue
            input_mode = None
            if self.full:
                try:
                    status = os.lstat(self.input_dir / rel)
                    if stat.S_ISREG(status.st_mode):
                        input_mode = stat.S_IMODE(status.st_mode)
                except OSError:
                    input_mode = None
            if not (info.mode == EXEC_MODE and input_mode == EXEC_MODE):
                self.findings["G2"].append(
                    f"{rel}: has mode {info.mode:04o}; a staged file is 0644, or 0755 when "
                    f"the input tree's same path is 0755, so without an input tree only "
                    f"0644 passes")

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
                fold = folded(line)
                for marker in self.markers:
                    hit = marker.regex.search(line) or (
                        fold is not None and marker.regex.search(fold))
                    if hit and (rel, number, f"marker:{marker.ident}") not in allowed:
                        self.findings["G3"].append(
                            f"{rel}:{number}: holds a hit of the publishable marker "
                            f"{marker.ident} with no matching exception")

    def private_pattern(self, ref):
        if ref.startswith("marker:"):
            return {m.ident: m.regex for m in self.private_markers}[ref[len("marker:"):]]
        return lists.term_regex(ref[len("term:"):])

    def scan_private_text(self, where, rel, text, allowed):
        """Scan decoded text, and its NFKC-normalized copy where that differs, for terms and
        private markers, honouring the exact exceptions when the text is a numbered line of a
        staged file (where > 0)."""
        for number, line in text_lines(text) if where == "lines" else ((0, text),):
            fold = folded(line)
            for term in self.terms:
                hit = term.regex.search(line) or (fold is not None and term.regex.search(fold))
                if hit and (rel, number, f"term:{term.text.casefold()}") not in allowed:
                    place = f"{rel}:{number}" if number else rel
                    self.findings["G4"].append(
                        f"{self.mask(place)}: holds term {term.line} of {lists.TERMS}")
            for marker in self.private_markers:
                hit = marker.regex.search(line) or (
                    fold is not None and marker.regex.search(fold))
                if hit and (rel, number, f"marker:{marker.ident}") not in allowed:
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
        """Scan one binary, as the module docstring's G4 entry says."""
        place = f"{rel}!{member}" if member else rel
        self.scan_bytes(place, data, STREAM_DEPTH)

    def scan_bytes(self, place, data, depth):
        """Scan one blob of bytes: each term's encoded bytes at any offset, the decoded
        readings (both UTF-16 alignments) for private markers and folded term variants, a
        PNG's text chunks and inflated image data, and every identified zlib stream, following
        inflated content at most depth more levels down; image data or an identified stream
        past that depth refuses rather than crossing unscanned."""
        masked = self.mask(place)
        for term, patterns in self.term_bytes:
            for encoding, pattern in patterns:
                if pattern.search(data):
                    self.findings["G4"].append(
                        f"{masked}: its bytes hold term {term.line} of {lists.TERMS} in its "
                        f"{encoding} encoding")
                    break
        seen = set()
        for encoding, readings in (
                ("utf-8", (data.decode("utf-8", "replace"),)),
                ("utf-16-le", (data.decode("utf-16-le", "replace"),
                               data[1:].decode("utf-16-le", "replace"))),
                ("utf-16-be", (data.decode("utf-16-be", "replace"),
                               data[1:].decode("utf-16-be", "replace")))):
            for reading in readings:
                fold = folded(reading)
                for marker in self.private_markers:
                    if ("marker", marker.line) in seen:
                        continue
                    if marker.regex.search(reading) or (
                            fold is not None and marker.regex.search(fold)):
                        seen.add(("marker", marker.line))
                        self.findings["G4"].append(
                            f"{masked}: its {encoding} reading holds a hit of private marker "
                            f"{marker.line} of {lists.PRIVATE_MARKERS}")
                if fold is None:
                    continue
                for term in self.terms:
                    if ("term", term.line) not in seen and term.regex.search(fold):
                        seen.add(("term", term.line))
                        self.findings["G4"].append(
                            f"{masked}: an NFKC-normalized {encoding} reading holds term "
                            f"{term.line} of {lists.TERMS}")
        if data.startswith(PNG_SIGNATURE):
            try:
                texts, image = png_parts(data)
            except (ValueError, zlib.error):
                self.findings["G4"].append(f"{masked}: a PNG whose chunks cannot be read and "
                                           f"inflated to the end; an unscanned file refuses")
                return
            for chunk in texts:
                self.scan_private_text("chunk", place, chunk, set())
            if image:
                if depth:
                    self.scan_bytes(place, image, depth - 1)
                else:
                    self.findings["G4"].append(f"{masked}: holds PNG image data nested past "
                                               f"the depth this gate follows; an unscanned "
                                               f"stream refuses")
        try:
            streams = zlib_streams(data)
        except ValueError:
            self.findings["G4"].append(f"{masked}: holds compressed streams this gate "
                                       f"cannot inflate within its bounds; an unscanned "
                                       f"file refuses")
            return
        if streams and not depth:
            self.findings["G4"].append(f"{masked}: holds an identified compressed stream "
                                       f"nested past the depth this gate follows; an "
                                       f"unscanned stream refuses")
            return
        for stream in streams:
            self.scan_bytes(place, stream, depth - 1)

    def staged_path(self, path, want_dir):
        """Whether path names a staged file or directory (a directory alone with want_dir)."""
        if want_dir:
            return path in self.staged_dirs
        return path in self.staged.files or path in self.staged_dirs

    def g5(self):
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
                    elif not self.staged_path(joined, path.endswith("/")):
                        self.findings["G5"].append(f"{rel}:{number}: the link {target!r} "
                                                   f"names no staged path")
            for number, line in text_lines(text):
                fold = folded(line)
                copies = (line,) if fold is None else (line, fold)
                targets = {(match.group(1).lower(), unquote(match.group(2)))
                           for copy in copies for match in REPO_LINK.finditer(copy)}
                for route, raw in sorted(targets):
                    path = raw.rstrip("/")
                    bad = not path or ".." in path.split("/")
                    if bad or not self.staged_path(path, route == "tree"):
                        self.findings["G5"].append(
                            f"{rel}:{number}: a {route}/main link into this project names no "
                            f"staged {'directory' if route == 'tree' else 'file'}")
                if any(HISTORY_LINK.search(copy) for copy in copies):
                    self.findings["G5"].append(f"{rel}:{number}: holds a link into the "
                                               f"development history (pull, commit, commits, "
                                               f"compare or actions)")
                if rel.startswith("site/") and rel.endswith(".html"):
                    links = {match.group(1) for copy in copies
                             for match in SITE_URL.finditer(copy)}
                    for target in sorted(links):
                        resolved = "site" + (target + "index.html" if target.endswith("/")
                                             else target)
                        if resolved not in self.staged.files:
                            self.findings["G5"].append(
                                f"{rel}:{number}: the root-relative link {target!r} names no "
                                f"staged site path")
        if self.full:
            prefixes = {commit[:12] for commit in read_commits(self.history)}
            self.commit_prefixes = prefixes
            for rel in sorted(self.staged.files) + sorted(self.staged.dirs):
                lengths = hex_hits(rel, prefixes)
                if lengths:
                    shown = HEX_RUN.sub(MASK, folded(rel) or rel)
                    for length in lengths:
                        self.findings["G5"].append(
                            f"{shown}: the path's name holds a run of {length} hexadecimal "
                            f"characters that names or holds a commit of the private "
                            f"repository")
            for rel in sorted(self.staged.data):
                text = self.staged.text(rel)
                if text is None:
                    continue
                for number, line in text_lines(text):
                    for length in hex_hits(line, prefixes):
                        self.findings["G5"].append(
                            f"{rel}:{number}: holds a run of {length} hexadecimal "
                            f"characters that names or holds a commit of the private "
                            f"repository")

    def g6(self):
        for rel in sorted(self.staged.data):
            entries = [entry for entry in self.publish if entry.regex.fullmatch(rel)]
            if len(entries) != 1:
                continue  # G1 already refused this file
            source = self.fresh if entries[0].kind == "render" else self.input_dir
            kind = "fresh render" if entries[0].kind == "render" else "input tree"
            path = source / rel
            try:
                expected = read_regular(path)
            except OSError:
                self.findings["G6"].append(f"{rel}: the {kind} has no readable regular file "
                                           f"to compare against; unverifiable drift refuses "
                                           f"the export")
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
        if baseline:
            pins = self.read_pin()
            for rel in baseline:
                if pins is None:
                    break
                if pins.get(rel[len("site/"):]) != sha256(self.staged.data.get(rel, b"")):
                    self.findings["G8"].append(f"{rel}: does not hash to its entry in the "
                                               f"input tree's .baseline/pin.toml")
        for rel in sorted(self.staged.data):
            data = self.staged.data[rel]
            if rel.lower().endswith(".zip") or is_zip_content(data):
                self.scan_zip(rel, data)
                continue
            kind = compressed_kind(rel, data)
            if kind and not rel.startswith("site/assets/baseline/"):
                self.findings["G8"].append(
                    f"{rel}: holds {kind} content this gate cannot scan inside; only a "
                    f"pinned site/assets/baseline/ file crosses compressed")

    def read_pin(self):
        """{path relative to site/: sha256} from the input tree's .baseline/pin.toml, or None
        with a finding when it cannot be read, which refuses every pinned comparison."""
        if tomllib is None:
            self.findings["G8"].append(".baseline/pin.toml: this interpreter cannot parse "
                                       "TOML, so the pin cannot be checked")
            return None
        try:
            pin = tomllib.loads(read_regular(self.input_dir / ".baseline" / "pin.toml")
                                .decode("utf-8"))
            table = pin["files"]
            return {key: str(value) for key, value in table.items()}
        except (OSError, UnicodeError, KeyError, TypeError, tomllib.TOMLDecodeError):
            self.findings["G8"].append(".baseline/pin.toml: the input tree's pin cannot be "
                                       "read, so the template files cannot be verified")
            return None

    def scan_member_text(self, rel, name, text, names, folders):
        """The content checks a staged text file gets, over one text member of a staged
        archive: the publishable markers (G3; no exception applies inside an archive), the
        history and repository link scans, and the commit scan (G5c). A Markdown or HTML
        member also gets the link-target checks, resolved against the archive's own members.
        G8 opens archives in full mode alone, so these member scans run there alone."""
        place = self.mask(f"{rel}!{name}")
        lowered = name.lower()
        either = names | folders
        if lowered.endswith(".md"):
            for number, target in markdown_targets(text):
                if KEEP.match(target) or not target:
                    continue
                path = target.partition("#")[0]
                if not path:
                    continue
                joined = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
                if path.startswith("/") or joined == ".." or joined.startswith("../"):
                    self.findings["G5"].append(f"{place}:{number}: the link {target!r} "
                                               f"leaves the archive")
                elif joined not in (folders if path.endswith("/") else either):
                    self.findings["G5"].append(f"{place}:{number}: the link {target!r} "
                                               f"names no member of the archive")
        if self.commit_prefixes is None:
            self.findings["G5"].append(f"{place}: the commit scan over this member did not "
                                       f"run because the history was refused; an unscanned "
                                       f"member refuses")
        html = lowered.endswith((".html", ".htm"))
        for number, line in text_lines(text):
            fold = folded(line)
            copies = (line,) if fold is None else (line, fold)
            for marker in self.markers:
                if any(marker.regex.search(copy) for copy in copies):
                    self.findings["G3"].append(
                        f"{place}:{number}: holds a hit of the publishable marker "
                        f"{marker.ident}; no exception applies inside an archive")
            if any(HISTORY_LINK.search(copy) for copy in copies):
                self.findings["G5"].append(f"{place}:{number}: holds a link into the "
                                           f"development history (pull, commit, commits, "
                                           f"compare or actions)")
            targets = {(match.group(1).lower(), unquote(match.group(2)))
                       for copy in copies for match in REPO_LINK.finditer(copy)}
            for route, raw in sorted(targets):
                path = raw.rstrip("/")
                if (not path or ".." in path.split("/")
                        or not self.staged_path(path, route == "tree")):
                    self.findings["G5"].append(
                        f"{place}:{number}: a {route}/main link into this project names no "
                        f"staged {'directory' if route == 'tree' else 'file'}")
            if html:
                links = {match.group(1) for copy in copies
                         for match in SITE_URL.finditer(copy)}
                for target in sorted(links):
                    resolved = target + "index.html" if target.endswith("/") else target
                    if resolved.lstrip("/") not in names:
                        self.findings["G5"].append(
                            f"{place}:{number}: the root-relative link {target!r} names no "
                            f"member of the archive")
            if self.commit_prefixes is not None:
                for length in hex_hits(line, self.commit_prefixes):
                    self.findings["G5"].append(
                        f"{place}:{number}: holds a run of {length} hexadecimal characters "
                        f"that names or holds a commit of the private repository")

    def scan_zip(self, rel, data, depth=ZIP_DEPTH, budget=None):
        """Scan one staged archive. Every byte span its central directory does not explain
        is scanned as bytes and refuses the archive. Every member name is scanned, as
        written and folded, for terms, private markers and commit ids. Every member, read by
        its central
        directory entry so a duplicated name hides nothing, is scanned as G4 scans a file, a
        text member also with the marker, link and commit scans a staged text file gets, and
        a member whose name or content identifies a zip the same way, at most ZIP_DEPTH
        archive levels below the staged archive
        and ZIP_LIMIT inflated bytes in all. A member identified as other compressed content
        refuses, and so does an archive this gate cannot scan to the end, past either bound
        or on any error."""
        if budget is None:
            budget = [ZIP_LIMIT]
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                infos = archive.infolist()
                names, folders = set(), set()
                for info in infos:
                    segments = info.filename.rstrip("/").split("/")
                    if info.filename.endswith("/"):
                        folders.add("/".join(segments))
                    else:
                        names.add(info.filename)
                    for index in range(1, len(segments)):
                        folders.add("/".join(segments[:index]))
                for start, end in zip_gaps(data, archive):
                    self.scan_bytes(f"{rel}!(unattributed bytes)", data[start:end],
                                    STREAM_DEPTH)
                    self.findings["G8"].append(
                        f"{self.mask(rel)}: holds {end - start} bytes at offset {start} that "
                        f"no member, directory record or archive comment explains; bytes the "
                        f"gate cannot attribute refuse the export")
                for info in infos:
                    budget[0] -= max(info.file_size, 0)
                    if budget[0] < 0:
                        raise ValueError("the archive inflates past the limit")
                    member = archive.read(info)
                    budget[0] -= max(len(member) - info.file_size, 0)
                    if budget[0] < 0:
                        raise ValueError("the archive inflates past the limit")
                    name = info.filename
                    name_fold = folded(name)
                    name_copies = (name,) if name_fold is None else (name, name_fold)
                    for term in self.terms:
                        if any(term.regex.search(copy) for copy in name_copies):
                            self.findings["G4"].append(
                                f"{self.mask(rel)}!: a member name holds term {term.line} of "
                                f"{lists.TERMS}")
                    for marker in self.private_markers:
                        if any(marker.regex.search(copy) for copy in name_copies):
                            self.findings["G4"].append(
                                f"{self.mask(rel)}!: a member name holds a hit of private "
                                f"marker {marker.line} of {lists.PRIVATE_MARKERS}")
                    if self.commit_prefixes is not None:
                        for length in hex_hits(name, self.commit_prefixes):
                            self.findings["G5"].append(
                                f"{self.mask(rel)}!: a member name holds a run of {length} "
                                f"hexadecimal characters that names or holds a commit of "
                                f"the private repository")
                    if name.lower().endswith(".zip") or is_zip_content(member):
                        if depth == 0:
                            raise ValueError("archives nest past the depth limit")
                        self.scan_zip(f"{rel}!{name}", member, depth - 1, budget)
                        continue
                    kind = compressed_kind(name, member)
                    if kind:
                        self.findings["G8"].append(
                            f"{self.mask(rel)}!{self.mask(name)}: a member holds {kind} "
                            f"content this gate cannot scan inside; no compressed member "
                            f"crosses")
                        continue
                    text = is_text(member)
                    if text is not None:
                        self.scan_private_text("chunk", f"{rel}!{name}", text, set())
                        self.scan_member_text(rel, name, text, names, folders)
                    else:
                        self.scan_binary(rel, member, member=name)
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
    parser.add_argument("--history", default=None,
                        help="the private repository whose commits no staged hex run may name "
                             "(full mode; default: the one holding this tool)")
    parser.add_argument("--verdicts", default=None,
                        help="write the per-check verdicts to this new file for the receipt")
    parser.add_argument("--public-only", action="store_true",
                        help="run only the checks that need no private input; this mode never "
                             "approves an export")
    args = parser.parse_args(argv)
    try:
        if args.public_only:
            if args.input or args.fresh or args.private_dir or args.history is not None:
                raise lists.Refused("--public-only takes no --input, --fresh, --private-dir "
                                    "or --history")
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
            history = args.history if args.history is not None else str(ROOT)
            gate = Gate(args.staged, args.input, args.fresh, private, history)
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
                print(f"  FAIL  {check} {printable(gate.mask(finding))}")
            total += len(found)
            if found:
                print(f"  FAIL  {label}: {len(found)} finding"
                      f"{'' if len(found) == 1 else 's'}")
            else:
                print(f"  ok    {label}: no findings")
            verdicts[check] = {"status": "FAIL" if found else "ok", "findings": len(found)}
        approved = not args.public_only and total == 0
        files = {rel: {"size": info.size,
                       "sha256": (sha256(gate.staged.data[rel])
                                  if rel in gate.staged.data else None)}
                 for rel, info in sorted(gate.staged.files.items())}
        record = {"mode": "public-only" if args.public_only else "full",
                  "approved": approved, "checks": verdicts, "files": files,
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
        print(f"  FAIL  {printable(str(exc))}")
        return 2
    except Exception as exc:  # noqa: BLE001
        # A traceback could quote what a private list or a staged file holds.
        print(f"  FAIL  the export gate stopped on an unexpected {type(exc).__name__}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
