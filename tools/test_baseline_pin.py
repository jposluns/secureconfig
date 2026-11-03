#!/usr/bin/env python3
"""Cases for check_baseline_pin.py: each defect the pin gate exists to catch, run against a copy.

Every failing case starts from a copy of the real pin and the real copied files, makes 1 change
and asserts that the gate exits 1 with a message naming the defect; the pristine copy must pass.
A case whose change no longer applies RAISES, so a renamed file cannot turn a case into a run of
the pristine tree.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
DEST = Path("site") / "draft" / "assets" / "baseline"
PIN = Path(".baseline") / "pin.toml"


def run(mutate=None):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / DEST, d / DEST)
        (d / PIN).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / PIN, d / PIN)
        if mutate is not None:
            mutate(d)
        r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "check_baseline_pin.py"),
                            "--root", str(d)], capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edit_pin(old, new):
    def mutate(d):
        text = (d / PIN).read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"pin mutation {old!r} no longer matches")
        (d / PIN).write_text(text.replace(old, new, 1), encoding="utf-8")
    return mutate


def one_byte(d):
    target = d / DEST / "baseline.css"
    data = bytearray(target.read_bytes())
    data[-1] ^= 1
    target.write_bytes(bytes(data))


def link(d):
    os.symlink("baseline.css", d / DEST / "linked.css")


CASES = [
    ("one byte changed in a copied stylesheet", one_byte, 1, "differs from its pin"),
    ("an extra unpinned file in the copy folder",
     lambda d: (d / DEST / "extra.css").write_text("p{}", encoding="utf-8"), 1, "is not pinned"),
    ("a pinned file deleted", lambda d: (d / DEST / "copy.js").unlink(), 1, "pinned but missing"),
    ("a symbolic link in the copy folder", link, 1, "symbolic link"),
    ("a pin that escapes the folder",
     edit_pin('"assets/baseline/copy.js" =', '"assets/baseline/../copy.js" ='), 1,
     "not a plain relative path"),
    ("a pin that is not a digest",
     edit_pin('"assets/baseline/copy.js" = "', '"assets/baseline/copy.js" = "x'), 1, "not a SHA-256"),
    ("a pin key outside assets/baseline/", edit_pin('"assets/baseline/copy.js" =', '"copy.js" ='), 1,
     "is not under assets/baseline/"),
    ("a pin with no version", edit_pin('version = "1.3.1"', 'release = "1.3.1"'), 1,
     "no version"),
    ("a pin that is not TOML", edit_pin("[files]", "[files"), 1, "not valid TOML"),
    ("the pristine copy", None, 0, "match baseline 1.3.1"),
]


def main():
    failures = []
    for desc, mutate, want, expected in CASES:
        rc, out = run(mutate)
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} baseline pin cases ({len(CASES) - 1} refusals and the pristine copy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
