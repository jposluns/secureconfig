#!/usr/bin/env python3
"""Cases for tools/export_gate.py, the export gate.

Every case builds its own synthetic fixture under TMPDIR: an input tree with its own small
export lists, a staged tree, a fresh-render tree, a private directory holding one synthetic
protected term (a made-up word, never a real one) and one synthetic private marker, and a
throwaway git repository whose only commit stands in for the private history. No case reads
the repository's real lists, and no fixture holds a real term.

MUTATIONS, each expected to refuse. An extra staged file, a symbolic link, a hard-linked
file, a file a deny line matches, and a publishable record identifier. The synthetic
protected term in text, in an NFKC-normalizable spelling, interleaved with zero-width
spaces, in a path name, in UTF-16 bytes at
an even and at an odd offset, in a PNG zTXt chunk, in inflated PNG image data, in an
identified zlib stream, and in a zlib stream nested past the depth bound. The term in a zip
member, behind a duplicated zip member name, in a member of a nested zip, and in and before
a zip's unexplained byte spans. A stale public
exception; a relative link, a blob/main link and a root-relative site link to unstaged
paths; a pull/ link and a commits/ link. A planted 12-hex commit prefix, one in fullwidth
characters, a fullwidth pull link, a fullwidth record identifier, a commit id embedded in a
longer hexadecimal run, an empty --history, a shallow and a partial clone as --history, and
a --history below the top of its repository. A commit id, a record identifier, a pull link
and a link naming no member, each in a zip text member. A
drifted render, a VERSION that does not equal plugin/plugin.json, a missing required file, a
*-latest.zip file, and a latest redirect whose 302 names an unstaged archive. A 0755 file in
public-only mode or one whose input copy is not 0755; --history in public-only mode. The
private marker in a UTF-16 binary
and in a zip member's name; gzip content staged or inside a zip; archives nested past the
depth bound; a mismatched baseline pin. An unreadable staged file (a FIFO stands in when the
suite runs as root, which chmod 0 cannot stop), a scanner that raises, and a verdicts path
inside the staged tree. A private directory with mode 0755, and one inside the input tree.
The round-3 review's gaps: the term in a zip staged under a non-.zip admitted name, gzip at
a nonzero byte offset of a binary and inside an uncompressed tar, a fullwidth term in a zip
member name, a term and a commit id interleaved with combining marks, a commit id as a
staged file name and as a zip member name, and a member named .zip that no zip reader can
open. A FIFO at a compared input path, as the baseline
pin and as a list file, each run as a gate subprocess under a timeout, so a regression that
hangs fails instead of blocking the suite. A streamed zip64 archive, whose data descriptors
carry 8-byte sizes, passes clean.
The round-4 review's gaps: a staged name holding the term and a commit-id run, a term hidden
by combining marks in a staged name, and a marker hit in a staged name, each masked in every
finding; gzip content in a PNG ancillary chunk; a history link, a publishable marker and a
commit id in a zip archive comment; the term in a nested zip's extra field; and lzip content
by signature. Stray signature bytes whose formats' header fields do not validate pass, a real
embedded gzip stream refuses, two staged names differing only by case refuse, and so does a
case variant of a denied path. A file that grows between the walk and its read must take its
receipt size and hash from the same read. A homoglyph spelling of the term crosses, pinning
the limit DISCLOSED LIMITS names.

Clean full and public-only runs pass, as does a
pinned site/assets/baseline/ font; a zip member name with a control character is escaped in
the output; the public-only case shows that mode never approves an export and skips G4, G6
and G8; a verdicts file is written once, never overwritten, and lists every staged path with
its size and SHA-256. No output of any case may hold the synthetic term or the planted commit
prefix.

Nothing here reads the network. The only subprocesses are git, on the throwaway fixture
repositories, and the gate itself, for the FIFO cases that must be able to time out. Exit 0
ok, 1 on a finding.
"""
import contextlib
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import warnings
import zipfile
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import export_gate  # noqa: E402

TERM = "qoxviblat"  # a synthetic protected term: a made-up word, in no real list
MARKER_HIT = "internal-store.invalid/abc"  # a hit of the synthetic private marker
PNG_SIG = b"\x89PNG\r\n\x1a\n"

README = b"# README\n\nKeep row 1.2 here as an allowed example.\n"
EXCEPTED_LINE = b"Keep row 1.2 here as an allowed example."
GUIDE = b"# guide-one\n\nsee [link](README.md) for more\n"
REFERENCE = b"# guide-one\n\nreference copy\n"
ZIP_PATH = "site/downloads/secureconfig-1.0.5.zip"

ALLOWLIST = b"""# synthetic allowlist
copy\tREADME.md\trequired
copy\tLICENSE\trequired
copy\tguide-one.md\trequired
copy\tplugin/skills/secureconfig/references/guide-one.md\trequired
copy\tsite/index.html\trequired
copy\texport/public-allowlist.txt\trequired
copy\texport/public-markers.txt\trequired
copy\texport/public-exceptions.tsv\trequired
copy\tnotes/*.md\toptional
copy\tassets/*.bin\toptional
copy\timages/*.png\toptional
copy\tsite/_redirects\toptional
copy\tsite/downloads/secureconfig-1.0.5.zip\toptional
copy\tsite/assets/baseline/*.woff2\toptional
copy\treleases/SHA256SUMS\toptional
render\tVERSION\trequired
render\tCHANGELOG.md\trequired
render\tNOTICE\trequired
render\tplugin/plugin.json\trequired
"""
PRIVATE_PATHS = b"""# synthetic private paths
deny\tnotes.txt
deny\texport/FORMAT.md\toptional
deny\t**/*-latest.zip\toptional
"""
MARKERS = b"id-row\t\\brow [0-9]+\\.[0-9]+\\b\n"
RENDERED = {
    "VERSION": b"1.0.5\n",
    "CHANGELOG.md": b"# Changelog\n\n## 2026-01-01\n\n- a synthetic entry\n",
    "NOTICE": b"a synthetic notice\n",
    "plugin/plugin.json": b'{"name": "secureconfig", "version": "1.0.5"}\n',
}


def write(root, rel, data, mode=0o644):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    os.chmod(path, mode)
    return path


def chunk(ctype, data):
    crc = zlib.crc32(ctype + data) & 0xFFFFFFFF
    return len(data).to_bytes(4, "big") + ctype + data + crc.to_bytes(4, "big")


def png(ztxt=None, pixels=b"\x00\x00"):
    ihdr = chunk(b"IHDR", (1).to_bytes(4, "big") + (1).to_bytes(4, "big") + b"\x08\x00\x00\x00\x00")
    body = b""
    if ztxt is not None:
        body += chunk(b"zTXt", b"Comment\x00\x00" + zlib.compress(ztxt.encode("latin-1")))
    idat = chunk(b"IDAT", zlib.compress(pixels))
    return PNG_SIG + ihdr + body + idat + chunk(b"IEND", b"")


def zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)
    return buffer.getvalue()


def git_env(base):
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(base),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-01-01T00:00:00 +0000",
            "GIT_COMMITTER_DATE": "2026-01-01T00:00:00 +0000"}


def make_history(base):
    """A throwaway git repository with two deterministic commits, so a depth-one clone of it
    is genuinely shallow; its head id and its path. The repository allows filtered fetches so
    a partial clone of it can be built."""
    hist = Path(base) / "history"
    hist.mkdir()
    env = git_env(base)
    (hist / "file.txt").write_text("fixture\n", encoding="utf-8")
    for command in (["git", "init", "-q"], ["git", "add", "."],
                    ["git", "commit", "-q", "-m", "fixture"]):
        subprocess.run(command, cwd=hist, env=env, check=True, capture_output=True, timeout=60)
    (hist / "file.txt").write_text("fixture two\n", encoding="utf-8")
    for command in (["git", "add", "."], ["git", "commit", "-q", "-m", "fixture two"],
                    ["git", "config", "uploadpack.allowfilter", "true"]):
        subprocess.run(command, cwd=hist, env=env, check=True, capture_output=True, timeout=60)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=hist, env=env, check=True,
                          capture_output=True, timeout=60)
    return head.stdout.decode("ascii").strip(), str(hist)


def make_clone(base, source, target, *options):
    """A clone of the fixture repository over file://, so --depth and --filter act as they
    would against a remote; its path."""
    out = Path(base) / target
    subprocess.run(["git", "clone", "-q", *options, "file://" + str(source), str(out)],
                   env=git_env(base), check=True, capture_output=True, timeout=60)
    return str(out)


def make_empty_history(base):
    """A throwaway git repository with no commits at all."""
    hist = Path(base) / "empty-history"
    hist.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=hist, env=git_env(base), check=True,
                   capture_output=True, timeout=60)
    return str(hist)


class Fixture:
    """One synthetic fixture: input, staged, fresh, private, and the shared history."""

    def __init__(self, base, history):
        self.base = Path(tempfile.mkdtemp(dir=base))
        self.input = self.base / "input"
        self.staged = self.base / "staged"
        self.fresh = self.base / "fresh"
        self.private = self.base / "private"
        self.history = history
        row = (b"README.md\t3\t" + hashlib.sha256(EXCEPTED_LINE).hexdigest().encode("ascii")
               + b"\tmarker:id-row\tan allowed example line\n")
        exceptions = b"# synthetic public exceptions\n" + row
        for tree in (self.input, self.staged):
            write(tree, "README.md", README)
            write(tree, "LICENSE", b"a synthetic licence\n")
            write(tree, "guide-one.md", GUIDE)
            write(tree, "plugin/skills/secureconfig/references/guide-one.md", REFERENCE)
            write(tree, "site/index.html", b'<a href="/index.html">home</a>\n')
            write(tree, "export/public-allowlist.txt", ALLOWLIST)
            write(tree, "export/public-markers.txt", MARKERS)
            write(tree, "export/public-exceptions.tsv", exceptions)
        write(self.input, "export/private-paths.txt", PRIVATE_PATHS)
        for rel, data in RENDERED.items():
            write(self.staged, rel, data)
            write(self.fresh, rel, data)
        self.private.mkdir()
        os.chmod(self.private, 0o700)
        write(self.private, "protected-terms.txt", TERM.encode("ascii") + b"\n", 0o600)
        write(self.private, "private-markers.txt",
              b"store-path\tinternal-store\\.invalid/[a-z]+\n", 0o600)
        write(self.private, "exceptions.tsv", b"# none\n", 0o600)

    def args(self, verdicts=None, history=None):
        out = ["--staged", str(self.staged), "--input", str(self.input),
               "--fresh", str(self.fresh), "--private-dir", str(self.private),
               "--history", history or self.history]
        if verdicts:
            out += ["--verdicts", verdicts]
        return out

    def both(self, rel, data):
        """Write one file into the staged and the input tree, so only the scan under test
        fires, not the copy-drift check."""
        write(self.staged, rel, data)
        write(self.input, rel, data)

    def append_guide(self, text):
        self.both("guide-one.md", GUIDE + text.encode("utf-8"))

    def stage_zip(self, data):
        """Stage one archive with its SHA-256 listed, so only the archive scan fires."""
        self.both(ZIP_PATH, data)
        digest = hashlib.sha256(data).hexdigest()
        self.both("releases/SHA256SUMS", f"{digest}  {ZIP_PATH}\n".encode("ascii"))

    def pin_baseline(self, rel, data, digest=None):
        """Stage one site/assets/baseline/ file and pin it in the input tree."""
        self.both(rel, data)
        digest = digest or hashlib.sha256(data).hexdigest()
        write(self.input, ".baseline/pin.toml",
              f'[files]\n"{rel[len("site/"):]}" = "{digest}"\n'.encode("ascii"))


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = export_gate.main(argv)
    return code, out.getvalue()


def run_gate(argv, timeout=60):
    """Run the gate as its own process, so a regression that hangs on a special file fails
    by timeout instead of blocking the suite."""
    command = [sys.executable, "-I", "-B", str(TOOLS / "export_gate.py"), *argv]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "the gate did not finish before the timeout"
    return done.returncode, done.stdout + done.stderr


def streamed_zip64(payload):
    """A zip written to an unseekable stream with force_zip64, so every member carries a
    data descriptor with 8-byte sizes, as streaming writers produce."""
    collected = io.BytesIO()

    class Stream(io.RawIOBase):
        def writable(self):
            return True

        def write(self, blob):
            return collected.write(blob)

    with zipfile.ZipFile(Stream(), "w", zipfile.ZIP_DEFLATED) as archive:
        with archive.open("notes.txt", mode="w", force_zip64=True) as handle:
            handle.write(payload)
    return collected.getvalue()


def tar_bytes(name, payload):
    """One uncompressed tar holding one member."""
    collected = io.BytesIO()
    with tarfile.open(fileobj=collected, mode="w") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))
    return collected.getvalue()


def zip64_with_sector(sector):
    """A zip whose zip64 end-of-central-directory record carries an extensible data sector
    holding SECTOR; zipfile ignores the sector, and the gate must still scan it."""
    base = zip_bytes([("notes.txt", b"plain")])
    eocd = base.rfind(b"PK\x05\x06")
    entries = int.from_bytes(base[eocd + 10:eocd + 12], "little")
    cd_size = int.from_bytes(base[eocd + 12:eocd + 16], "little")
    cd_offset = int.from_bytes(base[eocd + 16:eocd + 20], "little")
    head = base[:cd_offset + cd_size]
    z64 = (b"PK\x06\x06" + (44 + len(sector)).to_bytes(8, "little")
           + (45).to_bytes(2, "little") + (45).to_bytes(2, "little")
           + (0).to_bytes(4, "little") + (0).to_bytes(4, "little")
           + entries.to_bytes(8, "little") + entries.to_bytes(8, "little")
           + cd_size.to_bytes(8, "little") + cd_offset.to_bytes(8, "little") + sector)
    loc = (b"PK\x06\x07" + (0).to_bytes(4, "little")
           + (cd_offset + cd_size).to_bytes(8, "little") + (1).to_bytes(4, "little"))
    end = (b"PK\x05\x06" + (0).to_bytes(4, "little")
           + entries.to_bytes(2, "little") + entries.to_bytes(2, "little")
           + cd_size.to_bytes(4, "little") + cd_offset.to_bytes(4, "little")
           + (0).to_bytes(2, "little"))
    return head + z64 + loc + end


def local_header_fixed(payload):
    """A zip whose first local header carries PAYLOAD across its fixed time, date, CRC and
    size fields, which the reader takes from the central directory; the gate must scan these
    bytes, not only the member name and extra field."""
    data = bytearray(zip_bytes([("notes.txt", b"plain content here")]))
    data[14:14 + len(payload)] = payload  # inside the 16-byte fixed window at offset 10..26
    return bytes(data)


def main():
    failures = []
    count = 0
    base = tempfile.mkdtemp()
    commit, history = make_history(base)
    empty_history = make_empty_history(base)

    def case(name, code, out, want_code, *needles, absent=()):
        nonlocal count
        count += 1
        problems = []
        if code != want_code:
            problems.append(f"exit {code}, wanted {want_code}")
        for needle in needles:
            if needle not in out:
                problems.append(f"missing {needle!r}")
        for needle in (TERM, commit[:12], *absent):
            if needle in out:
                problems.append(f"output holds {needle!r}")
        if problems:
            failures.append(f"{name}: {'; '.join(problems)}\n---- output ----\n{out}")

    # Clean full run: every check passes, the verdicts record approves and lists every file.
    fixture = Fixture(base, history)
    verdicts = str(fixture.base / "verdicts.json")
    code, out = run(fixture.args(verdicts))
    case("a clean full run", code, out, 0, "ok    G1", "ok    G2", "ok    G3", "ok    G4",
         "ok    G5", "ok    G6", "ok    G7", "ok    G8", "the export may proceed")
    count += 1
    try:
        record = json.loads(Path(verdicts).read_text(encoding="utf-8"))
        if record["approved"] is not True or record["mode"] != "full" or any(
                entry["status"] != "ok" for entry in record["checks"].values()):
            failures.append(f"the clean verdicts record should approve: {record!r}")
        wanted = {"size": len(README), "sha256": hashlib.sha256(README).hexdigest()}
        if record["files"]["README.md"] != wanted:
            failures.append(f"the record's README.md entry is {record['files']['README.md']!r},"
                            f" wanted {wanted!r}")
        if len(record["files"]) != record["staged_files"] or "VERSION" not in record["files"]:
            failures.append(f"the record must list every staged path: {record!r}")
    except (OSError, ValueError, KeyError) as exc:
        failures.append(f"the verdicts file cannot be read back: {exc}")

    # The verdicts file is created once; a second run must refuse to overwrite it.
    code, out = run(fixture.args(verdicts))
    case("a verdicts file that already exists", code, out, 2, "verdicts file cannot be created")

    # A verdicts path inside the staged tree is refused before anything is written.
    code, out = run(fixture.args(str(fixture.staged / "v.json")))
    case("a verdicts path inside the staged tree", code, out, 2, "inside the staged tree")

    # Public-only mode runs without private input and can never approve an export.
    public_verdicts = str(fixture.base / "public-verdicts.json")
    code, out = run(["--staged", str(fixture.staged), "--public-only",
                     "--verdicts", public_verdicts])
    case("a clean public-only run", code, out, 0, "SKIP  G4", "SKIP  G6", "SKIP  G8",
         "never approves an export", absent=("the export may proceed",))
    count += 1
    record = json.loads(Path(public_verdicts).read_text(encoding="utf-8"))
    if record["approved"] is not False or record["mode"] != "public-only":
        failures.append(f"a public-only verdicts record must never approve: {record!r}")

    code, out = run(["--staged", str(fixture.staged), "--public-only",
                     "--input", str(fixture.input)])
    case("public-only with --input", code, out, 2, "--public-only takes no")

    fixture = Fixture(base, history)
    write(fixture.staged, "extra.bin", b"\x00odd bytes")
    code, out = run(fixture.args())
    case("an extra staged file", code, out, 1, "extra.bin", "no line of")

    fixture = Fixture(base, history)
    os.symlink("README.md", fixture.staged / "link.md")
    code, out = run(fixture.args())
    case("a symbolic link", code, out, 1, "symbolic link")

    fixture = Fixture(base, history)
    os.link(fixture.staged / "README.md", fixture.base / "second-name")
    code, out = run(fixture.args())
    case("a hard-linked staged file", code, out, 1, "hard links")

    fixture = Fixture(base, history)
    write(fixture.staged, "notes.txt", b"kept private\n")
    code, out = run(fixture.args())
    case("a deny-matched file", code, out, 1, "deny line")

    fixture = Fixture(base, history)
    fixture.append_guide("as row 3.4 records\n")
    code, out = run(fixture.args())
    case("a record identifier", code, out, 1, "publishable marker id-row")

    fixture = Fixture(base, history)
    fixture.append_guide(f"the name {TERM} appears\n")
    code, out = run(fixture.args())
    case("a protected term in text", code, out, 1, "protected-terms.txt")

    fixture = Fixture(base, history)
    fullwidth = "".join(chr(ord(ch) + 0xFEE0) for ch in TERM)
    fixture.append_guide(f"the name {fullwidth} appears\n")
    code, out = run(fixture.args())
    case("a fullwidth (NFKC) spelling of the term", code, out, 1, "holds term",
         absent=(fullwidth,))

    fixture = Fixture(base, history)
    fixture.both(f"notes/{TERM}.md", b"plain\n")
    code, out = run(fixture.args())
    case("a protected term in a path name", code, out, 1, "the path's name holds term", "[...]")

    fixture = Fixture(base, history)
    fixture.both("assets/font16.bin", b"\x00\xff" + TERM.encode("utf-16-le") + b"\x00\xfe")
    code, out = run(fixture.args())
    case("a protected term in UTF-16 bytes", code, out, 1, "in its utf-16-le encoding")

    fixture = Fixture(base, history)
    fixture.both("assets/odd16.bin", b"\x00" + TERM.encode("utf-16-le"))
    code, out = run(fixture.args())
    case("a UTF-16 term at an odd byte offset", code, out, 1, "in its utf-16-le encoding")

    fixture = Fixture(base, history)
    fixture.both("assets/mark16.bin", b"\x00\xff" + f"see {MARKER_HIT}".encode("utf-16-le"))
    code, out = run(fixture.args())
    case("a private marker in a UTF-16 binary", code, out, 1,
         "utf-16-le reading holds a hit of private marker", absent=("internal-store",))

    fixture = Fixture(base, history)
    fixture.both("assets/mark8.bin", b"\x00\xff" + f"see {MARKER_HIT}".encode("utf-8"))
    code, out = run(fixture.args())
    case("a private marker in a UTF-8 binary", code, out, 1,
         "utf-8 reading holds a hit of private marker", absent=("internal-store",))

    fixture = Fixture(base, history)
    fixture.both("images/card.png", png(ztxt=f"made with {TERM}"))
    code, out = run(fixture.args())
    case("a protected term in a PNG zTXt chunk", code, out, 1, "holds term")

    fixture = Fixture(base, history)
    fixture.both("images/pixels.png", png(pixels=b"\x00" + TERM.encode("ascii")))
    code, out = run(fixture.args())
    case("a protected term in inflated PNG image data", code, out, 1,
         "in its utf-8 encoding")

    fixture = Fixture(base, history)
    fixture.both("assets/blob.bin", b"\x00\xfe" + zlib.compress(f"hide {TERM} now".encode()))
    code, out = run(fixture.args())
    case("a protected term in an identified zlib stream", code, out, 1,
         "in its utf-8 encoding")

    fixture = Fixture(base, history)
    fixture.both("assets/opaque.bin", b"\x1f\x8b\x08\x04" + bytes(16))
    code, out = run(fixture.args())
    case("gzip content staged outside the baseline", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([("notes.txt", f"has {TERM} inside")]))
    code, out = run(fixture.args())
    case("a protected term in a zip member", code, out, 1, "holds term")

    fixture = Fixture(base, history)
    inner = zip_bytes([("n.txt", f"deep {TERM} here")])
    fixture.stage_zip(zip_bytes([("inner.zip", inner)]))
    code, out = run(fixture.args())
    case("a protected term in a nested zip", code, out, 1, "holds term")

    fixture = Fixture(base, history)
    z4 = zip_bytes([("f.txt", "plain")])
    z3 = zip_bytes([("z4.zip", z4)])
    z2 = zip_bytes([("z3.zip", z3)])
    fixture.stage_zip(zip_bytes([("z2.zip", z2)]))
    code, out = run(fixture.args())
    case("archives nested past the depth bound", code, out, 1, "cannot scan to the end")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([("blob.gz", b"\x1f\x8b\x08opaque")]))
    code, out = run(fixture.args())
    case("a compressed zip member", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    forged = "x\n  ok    G9 forged: no findings"
    fixture.stage_zip(zip_bytes([(forged, f"see {MARKER_HIT} here")]))
    code, out = run(fixture.args())
    case("a zip member name with a newline", code, out, 1,
         "\\n  ok    G9 forged", "holds a hit of private marker",
         absent=("\n  ok    G9 forged",))

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([(f"{MARKER_HIT}.txt", "plain")]))
    code, out = run(fixture.args())
    case("a zip member name with a marker hit", code, out, 1,
         "a member name holds a hit of private marker", absent=("internal-store",))

    fixture = Fixture(base, history)
    fixture.pin_baseline("site/assets/baseline/brand.woff2", b"wOF2\x00synthetic-font")
    code, out = run(fixture.args())
    case("a pinned baseline font crosses", code, out, 0, "ok    G8",
         "the export may proceed")

    fixture = Fixture(base, history)
    fixture.pin_baseline("site/assets/baseline/brand.woff2", b"wOF2\x00synthetic-font",
                         digest="0" * 64)
    code, out = run(fixture.args())
    case("a baseline file that misses its pin", code, out, 1,
         "does not hash to its entry")

    fixture = Fixture(base, history)
    stale = README.replace(EXCEPTED_LINE, b"Keep row 1.2 here but changed.")
    fixture.both("README.md", stale)
    code, out = run(fixture.args())
    case("a stale public exception", code, out, 1, "stale")

    fixture = Fixture(base, history)
    fixture.append_guide("see [m](missing.md)\n")
    code, out = run(fixture.args())
    case("a relative link to an unstaged file", code, out, 1, "names no staged path")

    fixture = Fixture(base, history)
    fixture.append_guide("see https://github.com/example-owner/secureconfig/blob/main/missing.md now\n")
    code, out = run(fixture.args())
    case("a blob/main link to an unstaged file", code, out, 1, "names no staged file")

    fixture = Fixture(base, history)
    fixture.both("site/index.html", b'<a href="/missing.html">x</a>\n')
    code, out = run(fixture.args())
    case("a root-relative link to an unstaged site path", code, out, 1,
         "names no staged site path")

    fixture = Fixture(base, history)
    fixture.append_guide("see https://github.com/example-owner/secureconfig/pull/7 now\n")
    code, out = run(fixture.args())
    case("a pull link", code, out, 1, "development history")

    fixture = Fixture(base, history)
    fixture.append_guide(f"an id {commit[:12]} planted\n")
    code, out = run(fixture.args())
    case("a planted commit prefix", code, out, 1,
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    fixture.append_guide(f"a run 0{commit} embeds an id\n")
    code, out = run(fixture.args())
    case("a commit id embedded in a longer hex run", code, out, 1,
         "hexadecimal characters that names or holds a commit", absent=(commit,))

    fixture = Fixture(base, history)
    code, out = run(fixture.args(history=empty_history))
    case("a history with no commits", code, out, 1, "lists no commits")

    fixture = Fixture(base, history)
    sub = Path(history) / "sub"
    sub.mkdir(exist_ok=True)
    code, out = run(fixture.args(history=str(sub)))
    case("a history below its repository's top level", code, out, 1, "not the top level")

    # The round-2 review's gaps, each expected to refuse.
    fixture = Fixture(base, history)
    code, out = run(fixture.args(history=make_clone(base, history, "shallow-history",
                                                    "--depth", "1")))
    case("a shallow clone as the history", code, out, 1, "shallow clone")

    fixture = Fixture(base, history)
    code, out = run(fixture.args(history=make_clone(base, history, "partial-history",
                                                    "--filter=blob:none")))
    case("a partial clone as the history", code, out, 1, "partial clone")

    fixture = Fixture(base, history)
    wide_commit = "".join(chr(ord(ch) + 0xFEE0) for ch in commit[:12])
    fixture.append_guide(f"an id {wide_commit} planted\n")
    code, out = run(fixture.args())
    case("a fullwidth commit id", code, out, 1,
         "hexadecimal characters that names or holds a commit", absent=(wide_commit,))

    fixture = Fixture(base, history)
    wide_pull = "".join(chr(ord(ch) + 0xFEE0) for ch in
                        "github.com/example-owner/secureconfig/pull/7")
    fixture.append_guide(f"see {wide_pull} now\n")
    code, out = run(fixture.args())
    case("a fullwidth pull link", code, out, 1, "development history")

    fixture = Fixture(base, history)
    wide_row = "".join("　" if ch == " " else chr(ord(ch) + 0xFEE0) for ch in "row 3.4")
    fixture.append_guide(f"as {wide_row} records\n")
    code, out = run(fixture.args())
    case("a fullwidth record identifier", code, out, 1, "publishable marker id-row")

    fixture = Fixture(base, history)
    hidden = "​".join(TERM)
    fixture.append_guide(f"the name {hidden} appears\n")
    code, out = run(fixture.args())
    case("a term hidden by zero-width spaces", code, out, 1, "holds term", absent=(hidden,))

    fixture = Fixture(base, history)
    fixture.append_guide("see https://github.com/example-owner/secureconfig/commits/main now\n")
    code, out = run(fixture.args())
    case("a commits link", code, out, 1, "development history")

    fixture = Fixture(base, history)
    buffer = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # the duplicate member name is the point of the case
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("x.txt", f"has {TERM} inside")
            archive.writestr("x.txt", "clean")
    fixture.stage_zip(buffer.getvalue())
    code, out = run(fixture.args())
    case("a term behind a duplicated member name", code, out, 1, "holds term")

    fixture = Fixture(base, history)
    deep = zlib.compress(zlib.compress(zlib.compress(f"hide {TERM} now".encode())))
    fixture.both("assets/deep.bin", b"\x00\xfe" + deep)
    code, out = run(fixture.args())
    case("a stream nested past the depth bound", code, out, 1,
         "nested past the depth this gate follows")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([("notes.txt", f"an id {commit[:12]} planted")]))
    code, out = run(fixture.args())
    case("a commit id in a zip member", code, out, 1,
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([("notes.txt", "as row 3.4 records")]))
    code, out = run(fixture.args())
    case("a record identifier in a zip member", code, out, 1, "publishable marker id-row",
         "no exception applies inside an archive")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes(
        [("doc.md", "see https://github.com/example-owner/secureconfig/pull/7 now")]))
    code, out = run(fixture.args())
    case("a pull link in a zip member", code, out, 1, "development history")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([("doc.md", "see [m](missing.md) now")]))
    code, out = run(fixture.args())
    case("a member link naming no member", code, out, 1, "names no member of the archive")

    fixture = Fixture(base, history)
    packer = zlib.compressobj(wbits=-15)  # raw deflate, which no byte scan can identify
    fixture.stage_zip(packer.compress(f"hide {TERM} now".encode()) + packer.flush()
                      + zip_bytes([("notes.txt", "plain")]))
    code, out = run(fixture.args())
    case("unexplained bytes before a zip's first member", code, out, 1,
         "no member, directory record or archive comment explains")

    fixture = Fixture(base, history)
    fixture.stage_zip(f"<{TERM}>".encode("ascii") + zip_bytes([("notes.txt", "plain")]))
    code, out = run(fixture.args())
    case("a term in a zip's unexplained bytes", code, out, 1, "its bytes hold term",
         "archive comment explains")

    fixture = Fixture(base, history)
    code, out = run(["--staged", str(fixture.staged), "--public-only", "--history", history])
    case("public-only with --history", code, out, 2, "--public-only takes no")

    fixture = Fixture(base, history)
    write(fixture.staged, "NOTICE", b"a drifted notice\n")
    code, out = run(fixture.args())
    case("a drifted render", code, out, 1, "does not equal the fresh render")

    fixture = Fixture(base, history)
    write(fixture.staged, "VERSION", b"1.0.6\n")
    write(fixture.fresh, "VERSION", b"1.0.6\n")
    code, out = run(fixture.args())
    case("a VERSION that is not plugin/plugin.json's", code, out, 1,
         "VERSION does not equal plugin/plugin.json's")

    fixture = Fixture(base, history)
    (fixture.staged / "LICENSE").unlink()
    code, out = run(fixture.args())
    case("a missing required file", code, out, 1, "matches no staged file", "is not staged")

    fixture = Fixture(base, history)
    write(fixture.staged, "site/downloads/secureconfig-latest.zip",
          zip_bytes([("a.txt", "plain content")]))
    code, out = run(fixture.args())
    case("a latest archive", code, out, 1, "deny line")

    fixture = Fixture(base, history)
    fixture.both("site/_redirects",
                 b"/downloads/secureconfig-latest.zip /downloads/secureconfig-1.0.9.zip 302\n")
    code, out = run(fixture.args())
    case("a 302 to an unstaged archive", code, out, 1, "latest rule")

    fixture = Fixture(base, history)
    os.chmod(fixture.staged / "guide-one.md", 0o755)
    code, out = run(fixture.args())
    case("a 0755 file whose input copy is 0644", code, out, 1, "has mode 0755")

    fixture = Fixture(base, history)
    os.chmod(fixture.staged / "README.md", 0o755)
    code, out = run(["--staged", str(fixture.staged), "--public-only"])
    case("a 0755 file in public-only mode", code, out, 1, "has mode 0755")

    fixture = Fixture(base, history)
    if os.geteuid() == 0:
        (fixture.staged / "LICENSE").unlink()
        os.mkfifo(fixture.staged / "LICENSE")
        code, out = run(fixture.args())
        case("an unreadable file (a FIFO under root)", code, out, 1, "not a regular file")
    else:
        os.chmod(fixture.staged / "LICENSE", 0o000)
        code, out = run(fixture.args())
        case("an unreadable file", code, out, 1, "cannot be read")

    fixture = Fixture(base, history)
    saved = export_gate.Gate.g3
    export_gate.Gate.g3 = lambda self: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        code, out = run(fixture.args())
    finally:
        export_gate.Gate.g3 = saved
    case("a scanner that raises", code, out, 1, "unexpected RuntimeError", absent=("boom",))

    fixture = Fixture(base, history)
    os.chmod(fixture.private, 0o755)
    code, out = run(fixture.args())
    case("a private directory with mode 0755", code, out, 2, "group or other",
         absent=(str(fixture.private),))

    fixture = Fixture(base, history)
    inside = fixture.input / "private"
    shutil.copytree(fixture.private, inside)
    os.chmod(inside, 0o700)
    for name in ("protected-terms.txt", "private-markers.txt", "exceptions.tsv"):
        os.chmod(inside / name, 0o600)
    code, out = run(["--staged", str(fixture.staged), "--input", str(fixture.input),
                     "--fresh", str(fixture.fresh), "--private-dir", str(inside),
                     "--history", history])
    case("a private directory inside the input tree", code, out, 2,
         "inside the staged or input tree", absent=(str(inside),))

    # The round-3 review's gaps, each expected to refuse, and its false refusal, now passing.
    fixture = Fixture(base, history)
    fixture.both("images/evil.png", zip_bytes([("notes.txt", f"has {TERM} inside")]))
    code, out = run(fixture.args())
    case("a zip staged under a non-.zip admitted name", code, out, 1, "holds term")

    fixture = Fixture(base, history)
    fixture.both("assets/offset.bin", b"\x00\x01\x02\x03\x1f\x8b\x08\x00" + bytes(12))
    code, out = run(fixture.args())
    case("gzip at a nonzero offset of a binary", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    fixture.both("assets/box.bin", tar_bytes("inner.gz", b"\x1f\x8b\x08\x00" + bytes(8)))
    code, out = run(fixture.args())
    case("gzip inside an uncompressed tar", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    (fixture.input / "README.md").unlink()
    os.mkfifo(fixture.input / "README.md")
    code, out = run_gate(fixture.args())
    case("a FIFO at a compared input path", code, out, 1, "no readable regular file")

    fixture = Fixture(base, history)
    fixture.pin_baseline("site/assets/baseline/brand.woff2", b"wOF2\x00synthetic-font")
    pin = fixture.input / ".baseline" / "pin.toml"
    pin.unlink()
    os.mkfifo(pin)
    code, out = run_gate(fixture.args())
    case("a FIFO as the baseline pin", code, out, 1, "pin cannot be read")

    fixture = Fixture(base, history)
    allowlist_path = fixture.input / "export" / "public-allowlist.txt"
    allowlist_path.unlink()
    os.mkfifo(allowlist_path)
    code, out = run_gate(fixture.args())
    case("a FIFO as a list file", code, out, 2, "cannot read export/public-allowlist.txt")

    fixture = Fixture(base, history)
    fixture.stage_zip(streamed_zip64(b"plain streamed content"))
    code, out = run(fixture.args())
    case("a streamed zip64 archive", code, out, 0, "the export may proceed")

    fixture = Fixture(base, history)
    wide_name = "".join(chr(ord(ch) + 0xFEE0) for ch in TERM) + ".txt"
    fixture.stage_zip(zip_bytes([(wide_name, "plain")]))
    code, out = run(fixture.args())
    case("a fullwidth term in a member name", code, out, 1, "a member name holds term",
         absent=(wide_name,))

    fixture = Fixture(base, history)
    marked = "̵".join(TERM)
    fixture.append_guide(f"the name {marked} appears\n")
    code, out = run(fixture.args())
    case("a term interleaved with combining marks", code, out, 1, "holds term",
         absent=(marked,))

    fixture = Fixture(base, history)
    marked_commit = "̵".join(commit[:12])
    fixture.append_guide(f"an id {marked_commit} planted\n")
    code, out = run(fixture.args())
    case("a commit id interleaved with combining marks", code, out, 1,
         "hexadecimal characters that names or holds a commit", absent=(marked_commit,))

    fixture = Fixture(base, history)
    fixture.both(f"notes/{commit[:12]}.md", b"plain\n")
    code, out = run(fixture.args())
    case("a commit id as a staged file name", code, out, 1,
         "the path's name holds a run of 12 hexadecimal")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip_bytes([(f"{commit[:12]}.txt", "plain")]))
    code, out = run(fixture.args())
    case("a commit id as a zip member name", code, out, 1,
         "a member name holds a run of 12 hexadecimal")

    fixture = Fixture(base, history)
    packer = zlib.compressobj(wbits=-15)  # raw deflate: not a zip, whatever the name says
    fixture.stage_zip(zip_bytes(
        [("inner.zip", packer.compress(f"hide {TERM} now".encode()) + packer.flush())]))
    code, out = run(fixture.args())
    case("a member named .zip that is not a zip", code, out, 1, "cannot scan to the end")

    # The round-4 review's gaps, each expected to refuse with nothing echoed, and its false
    # refusal shown never to start; the homoglyph case pins the disclosed limit.
    fixture = Fixture(base, history)
    fixture.both(f"notes/{TERM}-{commit[:12]}.md", b"plain\n")
    code, out = run(fixture.args())
    case("a term and a commit id in one staged name", code, out, 1,
         "the path's name holds term",
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    marked_name = "notes/" + "̵".join(TERM) + ".md"
    write(fixture.staged, marked_name, b"plain\n")
    code, out = run(fixture.args())
    case("a term hidden by combining marks in a staged name", code, out, 1,
         "holds a character other than", absent=(marked_name,))

    fixture = Fixture(base, history)
    fixture.both("notes/internal-store.invalid/abc.md", b"plain\n")
    code, out = run(fixture.args())
    case("a marker hit in a staged name", code, out, 1,
         "the path's name holds a hit of private marker", absent=("internal-store",))

    fixture = Fixture(base, history)
    smuggled = gzip.compress(f"hide {TERM} now".encode(), mtime=0)
    ihdr = chunk(b"IHDR", (1).to_bytes(4, "big") + (1).to_bytes(4, "big")
                 + b"\x08\x00\x00\x00\x00")
    sneaky = (PNG_SIG + ihdr + chunk(b"prIv", smuggled)
              + chunk(b"IDAT", zlib.compress(b"\x00\x00")) + chunk(b"IEND", b""))
    fixture.both("images/holder.png", sneaky)
    code, out = run(fixture.args())
    case("gzip content in a PNG ancillary chunk", code, out, 1,
         "a PNG chunk outside the image data holds gzip content")

    fixture = Fixture(base, history)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("notes.txt", "plain")
        archive.comment = (f"see github.com/example-owner/secureconfig/pull/7 and row 3.4 "
                           f"and an id {commit[:12]} here").encode("ascii")
    fixture.stage_zip(buffer.getvalue())
    code, out = run(fixture.args())
    case("a link, a marker and a commit id in a zip archive comment", code, out, 1,
         "development history", "publishable marker id-row",
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    payload = f"hold {TERM} here".encode()
    info = zipfile.ZipInfo("doc.txt")
    info.extra = (0xCAFE).to_bytes(2, "little") + len(payload).to_bytes(2, "little") + payload
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(info, "plain")
    fixture.stage_zip(zip_bytes([("inner.zip", buffer.getvalue())]))
    code, out = run(fixture.args())
    case("a term in a nested zip's extra field", code, out, 1, "its bytes hold term")

    fixture = Fixture(base, history)
    stray = (b"\x00\xff\x1f\x8b\x55\x66" + b"BZh9stray!" + b"wOFFabcdefgh"
             + b"\x00\x1f\x9d\xff" + bytes(6))
    fixture.both("assets/stray.bin", stray)
    code, out = run(fixture.args())
    case("stray signature bytes without their formats' header fields", code, out, 0,
         "the export may proceed")

    fixture = Fixture(base, history)
    fixture.both("assets/embedded.bin",
                 b"\x00\xfe" + gzip.compress(b"an embedded stream", mtime=0))
    code, out = run(fixture.args())
    case("a real gzip stream embedded in a binary", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    fixture.both("assets/lz.bin", b"\x00\xfeLZIP\x01\x12" + bytes(10))
    code, out = run(fixture.args())
    case("lzip content identified by its signature", code, out, 1,
         "lzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    fixture.both("notes/Case.md", b"plain\n")
    fixture.both("notes/case.md", b"plain\n")
    code, out = run(fixture.args())
    case("two staged names differing only by case", code, out, 1,
         "differ only by case or Unicode normalization")

    fixture = Fixture(base, history)
    write(fixture.staged, "Notes.txt", b"kept private\n")
    code, out = run(fixture.args())
    case("a case variant of a denied path", code, out, 1,
         "a case or normalization variant of the path matches the deny line")

    # The round-5 review's gaps: three zip regions the central directory explains but hands to
    # no scanner. A private commit id in the zip64 end record's extensible data sector or in a
    # local header's fixed fields, and a gzip-compressed term in that sector, each crossed with
    # approval before the fix; each must now refuse with nothing echoed.
    fixture = Fixture(base, history)
    fixture.stage_zip(zip64_with_sector(b"SEC-" + commit[:12].encode("ascii") + b"-SEC"))
    code, out = run(fixture.args())
    case("a commit id in a zip64 end record's data sector", code, out, 1,
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    fixture.stage_zip(zip64_with_sector(gzip.compress(f"hide {TERM} now".encode(), mtime=0)))
    code, out = run(fixture.args())
    case("a gzip term in a zip64 end record's data sector", code, out, 1,
         "gzip content this gate cannot scan inside")

    fixture = Fixture(base, history)
    fixture.stage_zip(local_header_fixed(commit[:12].encode("ascii")))
    code, out = run(fixture.args())
    case("a commit id in a local header's fixed fields", code, out, 1,
         "hexadecimal characters that names or holds a commit")

    fixture = Fixture(base, history)
    tampered_verdicts = str(fixture.base / "tampered-verdicts.json")
    grown = fixture.staged / "README.md"
    suffix = b"appended after the walk recorded the size\n"
    original_read = export_gate.read_regular

    def appended(path):
        data = original_read(path)
        return data + suffix if Path(path) == grown else data

    export_gate.read_regular = appended
    try:
        code, out = run(fixture.args(tampered_verdicts))
    finally:
        export_gate.read_regular = original_read
    case("a file that grows between the walk and its read", code, out, 1,
         "does not equal the input tree")
    count += 1
    record = json.loads(Path(tampered_verdicts).read_text(encoding="utf-8"))
    judged = README + suffix
    wanted = {"size": len(judged), "sha256": hashlib.sha256(judged).hexdigest()}
    if record["files"]["README.md"] != wanted:
        failures.append(f"the receipt must take the size and the hash from the same read of "
                        f"the judged bytes: {record['files']['README.md']!r}, wanted {wanted!r}")

    fixture = Fixture(base, history)
    homoglyph = TERM.replace("o", "о", 1)  # Cyrillic о: the homoglyph limit DISCLOSED LIMITS names
    fixture.append_guide(f"the name {homoglyph} appears\n")
    code, out = run(fixture.args())
    case("a homoglyph spelling crosses, pinning the disclosed limit", code, out, 0,
         "the export may proceed")

    shutil.rmtree(base, ignore_errors=True)
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {count} recorded cases for the export gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
