#!/usr/bin/env python3
"""Cases for tools/export_gate.py, the export gate.

Every case builds its own synthetic fixture under TMPDIR: an input tree with its own small
export lists, a staged tree, a fresh-render tree, a private directory holding one synthetic
protected term (a made-up word, never a real one) and one synthetic private marker, and a
throwaway git repository whose only commit stands in for the private history. No case reads
the repository's real lists, and no fixture holds a real term.

MUTATIONS, each expected to refuse. An extra staged file, a symbolic link, a hard-linked
file, a file a deny line matches, and a publishable record identifier. The synthetic
protected term in text, in an NFKC-normalizable spelling, in a path name, in UTF-16 bytes at
an even and at an odd offset, in a PNG zTXt chunk, in inflated PNG image data, in an
identified zlib stream, in a zip member and in a member of a nested zip. A stale public
exception; a relative link, a blob/main link and a root-relative site link to unstaged
paths; a pull/ link. A planted 12-hex commit prefix, a commit id embedded in a longer
hexadecimal run, an empty --history, and a --history below the top of its repository. A
drifted render, a VERSION that does not equal plugin/plugin.json, a missing required file, a
*-latest.zip file, and a latest redirect whose 302 names an unstaged archive. A 0755 file in
public-only mode or one whose input copy is not 0755. The private marker in a UTF-16 binary
and in a zip member's name; gzip content staged or inside a zip; archives nested past the
depth bound; a mismatched baseline pin. An unreadable staged file (a FIFO stands in when the
suite runs as root, which chmod 0 cannot stop), a scanner that raises, and a verdicts path
inside the staged tree. A private directory with mode 0755, and one inside the input tree.

Clean full and public-only runs pass, as does a
pinned site/assets/baseline/ font; a zip member name with a control character is escaped in
the output; the public-only case shows that mode never approves an export and skips G4, G6
and G8; a verdicts file is written once, never overwritten, and lists every staged path with
its size and SHA-256. No output of any case may hold the synthetic term or the planted commit
prefix.

Nothing here reads the network. The only subprocess is git, on the throwaway fixture
repositories. Exit 0 ok, 1 on a finding.
"""
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
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
    """A throwaway git repository with one deterministic commit; its id and its path."""
    hist = Path(base) / "history"
    hist.mkdir()
    env = git_env(base)
    (hist / "file.txt").write_text("fixture\n", encoding="utf-8")
    for command in (["git", "init", "-q"], ["git", "add", "."],
                    ["git", "commit", "-q", "-m", "fixture"]):
        subprocess.run(command, cwd=hist, env=env, check=True, capture_output=True, timeout=60)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=hist, env=env, check=True,
                          capture_output=True, timeout=60)
    return head.stdout.decode("ascii").strip(), str(hist)


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
    case("a protected term in a path name", code, out, 1, "the path's name holds term", "[…]")

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

    shutil.rmtree(base, ignore_errors=True)
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {count} recorded cases for the export gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
