#!/usr/bin/env python3
"""Cases for check_baseline_pin.py: each defect the pin gate exists to catch, run against a copy.

Every failing case starts from a copy of the real pin and the real copied files, makes 1 change
and asserts that the gate exits 1 with a message naming the defect; the pristine copy must pass.
A case whose change no longer applies RAISES, so a renamed file cannot turn a case into a run of
the pristine tree. The cases added in QA round 1 of #1182 hold the pin to the copy script's version,
digests and RUNTIME list, and keep excluded template material out whether pinned or not.
"""
import hashlib
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


def pinned(name, data):
    """Copy a file into the folder and pin it with its true digest."""
    def mutate(d):
        target = d / DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        with open(d / PIN, "a", encoding="utf-8") as f:
            f.write(f'"assets/baseline/{name}" = "{hashlib.sha256(data).hexdigest()}"\n')
    return mutate


def edit_pin_line(prefix):
    """Remove the pin line that starts with prefix."""
    def mutate(d):
        lines = (d / PIN).read_text(encoding="utf-8").splitlines(keepends=True)
        kept = [line for line in lines if not line.startswith(prefix)]
        if len(kept) != len(lines) - 1:
            raise AssertionError(f"pin line {prefix!r} no longer matches")
        (d / PIN).write_text("".join(kept), encoding="utf-8")
    return mutate


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
    ("a pin with no version", edit_pin('version = "1.5.0"', 'release = "1.5.0"'), 1,
     "no version"),
    ("a pin that is not TOML", edit_pin("[files]", "[files"), 1, "not valid TOML"),
    # QA round 1 of #1182: the pin must be the copy script's, and excluded material stays out.
    ("a pin at another version than the copy script's",
     lambda d: (edit_pin('version = "1.5.0"', 'version = "1.3.1"')(d),
                edit_pin("/baseline/1.5.0/", "/baseline/1.3.1/")(d)), 1, "copy-baseline.py copies 1.5.0"),
    ("an upstream URL for another version", edit_pin("/baseline/1.5.0/", "/baseline/1.3.1/"), 1,
     "is not the URL of version 1.5.0"),
    ("another archive digest", edit_pin('archive_sha256 = "d', 'archive_sha256 = "0'), 1,
     "archive_sha256 is"),
    ("a copied, pinned file outside the copy script's list",
     pinned("extra.js", b"(function(){})();\n"), 1, "not in scripts/copy-baseline.py's RUNTIME list"),
    ("a copied, pinned reference page", pinned("reference/landing.html", b"<!doctype html>\n"), 1,
     "excludes from the copy"),
    ("a copied, pinned gen_palettes.py", pinned("gen_palettes.py", b"print()\n"), 1,
     "excludes from the copy"),
    ("a copied, unpinned tools/measure.js",
     lambda d: ((d / DEST / "tools").mkdir(), (d / DEST / "tools" / "measure.js").write_text("x", encoding="utf-8")),
     1, "excludes from the copy"),
    ("a RUNTIME file neither copied nor pinned",
     lambda d: (edit_pin_line('"assets/baseline/rail.js" =')(d), (d / DEST / "rail.js").unlink()), 1,
     "does not pin rail.js"),
    ("the pristine copy", None, 0, "match baseline 1.5.0"),
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
