#!/usr/bin/env python3
"""Cases for scripts/copy-baseline.py's archive check: a clean run and each archive it must refuse.

The copy script is loaded as a module and never run as __main__. Each case calls its main() on a
fresh temporary tree: a fake repository root, a fake unpacked 9.9.9 folder holding LICENSE and its
SHA256SUMS, and a gzip tar archive built here with tarfile. The module's ROOT, VERSION, UPSTREAM,
ARCHIVE_SHA256, SUMS_SHA256, RUNTIME and BUILD_TOOLS are patched for each case. The clean run must
copy LICENSE and write a pin naming the archive's digest. Every refusal must return 1, or exit 2
for a missing --archive, print its reason without an exception escaping main(), and leave a
pre-existing site/assets/baseline/ untouched, with no pin written and nothing copied.

Standard library only. No network. Every file is written under one tempfile.mkdtemp() directory
per case, removed in a finally, and no bytecode is written for the loaded script.
"""
import contextlib
import hashlib
import importlib.util
import io
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS.parent / "scripts" / "copy-baseline.py"
VERSION = "9.9.9"
MEMBER = f"{VERSION}/SHA256SUMS"
DEST = Path("site") / "assets" / "baseline"
PIN = Path(".baseline") / "pin.toml"
LICENSE = b"Fixture licence text for the copy-baseline cases.\n"
MARKER = b"A copy from an earlier run, which a refusal must leave in place.\n"
DATE = "2026-11-13"


def load():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("copy_baseline_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sums_bytes(files):
    """A SHA256SUMS in sha256sum form for files, a mapping of name to bytes."""
    return "".join(f"{digest(data)}  {name}\n" for name, data in files.items()).encode("utf-8")


def build_tar(members):
    """A gzip tar archive's bytes; members maps a name to bytes, or to None for a directory entry."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.mtime = 0
            if data is None:
                info.type = tarfile.DIRTYPE
                info.mode = 0o755
                tar.addfile(info)
            else:
                info.size = len(data)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def fixture(base):
    """The fake root, the unpacked folder, its SHA256SUMS bytes and the good archive's bytes."""
    root = base / "root"
    root.mkdir()
    folder = base / "unpacked" / VERSION
    folder.mkdir(parents=True)
    (folder / "LICENSE").write_bytes(LICENSE)
    sums = sums_bytes({"LICENSE": LICENSE})
    (folder / "SHA256SUMS").write_bytes(sums)
    good = build_tar({VERSION: None, MEMBER: sums, f"{VERSION}/LICENSE": LICENSE})
    return {"base": base, "root": root, "folder": folder, "sums": sums, "good": good}


def argv_for(fx, archive):
    return ["--archive", str(archive), "--from", str(fx["folder"]), "--date", DATE]


def archive_case(make, patch_digest=True):
    """Write the archive make(fx) returns; ARCHIVE_SHA256 is its digest, or the good one's."""
    def prepare(fx):
        data = make(fx)
        archive = fx["base"] / f"baseline-{VERSION}.tar.gz"
        archive.write_bytes(data)
        return argv_for(fx, archive), str(archive), digest(data if patch_digest else fx["good"])
    return prepare


def missing_archive_file(fx):
    archive = fx["base"] / "no-such-baseline.tar.gz"
    return argv_for(fx, archive), str(archive), digest(fx["good"])


def no_archive_argument(fx):
    return ["--from", str(fx["folder"]), "--date", DATE], "--archive", digest(fx["good"])


# (description, prepare, expected result, text the output must hold besides the archive path).
# prepare(fx) returns the argv, the text naming the archive and the ARCHIVE_SHA256 to patch in.
CASES = [
    ("a clean run", archive_case(lambda fx: fx["good"]), 0, "  ok    copied 1 files"),
    ("no --archive argument", no_archive_argument, 2, "the following arguments are required"),
    ("an archive with one trailing byte added",
     archive_case(lambda fx: fx["good"] + b"\0", patch_digest=False), 1,
     f"is not the published baseline-{VERSION}.tar.gz"),
    ("an archive path that does not exist", missing_archive_file, 1, "cannot read the archive"),
    ("a file with the patched digest that is not gzip",
     archive_case(lambda fx: b"This is not a gzip tar archive.\n"), 1,
     "is not a readable gzip tar archive"),
    ("the first half of the good archive",
     archive_case(lambda fx: fx["good"][:len(fx["good"]) // 2]), 1,
     "is not a readable gzip tar archive"),
    (f"a gzip tar with no {MEMBER}",
     archive_case(lambda fx: build_tar({VERSION: None, f"{VERSION}/LICENSE": LICENSE})), 1,
     f"has no member {MEMBER}"),
    (f"a gzip tar whose {MEMBER} is a directory",
     archive_case(lambda fx: build_tar({VERSION: None, MEMBER: None})), 1,
     "but not as a regular file"),
    (f"a gzip tar whose {MEMBER} differs from the folder's",
     archive_case(lambda fx: build_tar({VERSION: None,
                                        MEMBER: sums_bytes({"LICENSE": LICENSE + b"x"}),
                                        f"{VERSION}/LICENSE": LICENSE})), 1,
     f"differs from {MEMBER}"),
]


def tree(root):
    """Every path under root, mapped to its bytes for a file and to None for a directory."""
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*"))}


def run(module, prepare, want, expected):
    """Run one case on a fresh tree; return a list of problems, empty when the case holds."""
    base = Path(tempfile.mkdtemp())
    try:
        fx = fixture(base)
        argv, names_archive, archive_sha256 = prepare(fx)
        root = fx["root"]
        module.ROOT = root
        module.VERSION = VERSION
        module.UPSTREAM = f"https://example.invalid/baseline/{VERSION}/"
        module.ARCHIVE_SHA256 = archive_sha256
        module.SUMS_SHA256 = digest(fx["sums"])
        module.RUNTIME = ("LICENSE",)
        module.BUILD_TOOLS = {}
        if want != 0:
            (root / DEST).mkdir(parents=True)
            (root / DEST / "marker.txt").write_bytes(MARKER)
        before = tree(root)
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = module.main(argv)
        except SystemExit as exc:
            rc = exc.code
        except Exception as exc:  # noqa: BLE001  an escaping exception is itself the failure
            return [f"an exception escaped main(): {type(exc).__name__}: {exc}"]
        stdout, stderr = out.getvalue(), err.getvalue()
        problems = []
        if rc != want:
            problems.append(f"expected {want}, got {rc!r}: {stdout + stderr!r}")
        if "Traceback (most recent call last):" in stdout + stderr:
            problems.append(f"a traceback was printed: {stdout + stderr!r}")
        if want == 0:
            if expected not in stdout:
                problems.append(f"expected stdout to hold {expected!r}: {stdout!r}")
            copied = root / DEST / "LICENSE"
            if not copied.is_file() or copied.read_bytes() != LICENSE:
                problems.append("LICENSE was not copied byte for byte")
            line = f'archive_sha256 = "{archive_sha256}"'
            pin = root / PIN
            if not pin.is_file() or line not in pin.read_text(encoding="utf-8").splitlines():
                problems.append(f"{PIN} does not hold {line!r}")
            return problems
        # A refusal: its text on stdout (argparse's on stderr), and the fake root left as it was.
        shown = stderr if want == 2 else stdout
        if want == 1 and "  FAIL  " not in stdout:
            problems.append(f"expected a FAIL line on stdout: {stdout!r}")
        for text in (expected, names_archive):
            if text not in shown:
                problems.append(f"expected the output to hold {text!r}: {shown!r}")
        if tree(root) != before:
            problems.append(f"the fake root changed: {sorted(before)} became {sorted(tree(root))}")
        if (root / PIN).exists():
            problems.append(f"{PIN} was written")
        if (root / DEST / "LICENSE").exists():
            problems.append("LICENSE was copied")
        return problems
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    module = load()
    failures = []
    for desc, prepare, want, expected in CASES:
        problems = run(module, prepare, want, expected)
        if problems:
            failures += [f"{desc}: {p}" for p in problems]
        else:
            print(f"  ok    {desc}: {'refused' if want else 'copied'} (result {want})")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    refusals = sum(1 for case in CASES if case[2] != 0)
    print(f"  ok    {len(CASES)} copy-baseline archive cases ({refusals} refusals that left the "
          f"fake root untouched, and 1 clean run)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
