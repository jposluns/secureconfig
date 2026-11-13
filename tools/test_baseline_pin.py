#!/usr/bin/env python3
"""Cases for check_baseline_pin.py: each defect the pin gate exists to catch, run against a copy.

Every failing case starts from a copy of the real pin and the real copied files, makes 1 change
and asserts that the gate exits 1 with a message naming the defect; the pristine copy must pass.
A case whose change no longer applies RAISES, so a renamed file cannot turn a case into a run of
the pristine tree. The cases added in QA round 1 of #1182 hold the pin to the copy script's version,
digests and RUNTIME list, and keep excluded template material out whether pinned or not. The
baseline 1.6.0 cases hold .baseline/check_palette.py, the copied palette gate, to its pin. The cases
added in QA round 1 of #1190 refuse a .baseline/ that is a symbolic link or not a directory, a
pin.toml that is a link, and any other entry in .baseline/ (a file, a subdirectory, a link). The
baseline 1.8.0 cases hold .baseline/check_overflow.js, the copied overflow check, to its pin. The
baseline 1.13.0 cases hold .baseline/build_card.js and its fonts under .baseline/card-fonts/ to
their pins, admit .baseline/card-fonts only as a real directory holding pinned tools and nothing
else, admit the site's own .baseline/site-card.toml only as a regular file, and refuse the 1.11.3
Dancing Script woff2 left behind unpinned.
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
DEST = Path("site") / "assets" / "baseline"
PIN = Path(".baseline") / "pin.toml"
PALETTE_GATE = Path(".baseline") / "check_palette.py"
OVERFLOW_CHECK = Path(".baseline") / "check_overflow.js"
CARD_BUILDER = Path(".baseline") / "build_card.js"
CARD_FONTS = Path(".baseline") / "card-fonts"
SITE_CARD = Path(".baseline") / "site-card.toml"


def run(mutate=None):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / DEST, d / DEST)
        # The whole real .baseline/: the pin, every pinned build tool and the site's card data.
        shutil.copytree(ROOT / ".baseline", d / ".baseline", symlinks=True)
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


def flip(relative):
    """Change the last byte of the file at relative under the copy."""
    def mutate(d):
        target = d / relative
        data = bytearray(target.read_bytes())
        data[-1] ^= 1
        target.write_bytes(bytes(data))
    return mutate


def one_byte(d):
    flip(DEST / "baseline.css")(d)


def card_fonts_link(d):
    (d / CARD_FONTS).rename(d / "real-card-fonts")
    os.symlink("../real-card-fonts", d / CARD_FONTS, target_is_directory=True)


def site_card_link(d):
    (d / SITE_CARD).rename(d / ".baseline" / "saved-card.toml")
    os.symlink("saved-card.toml", d / SITE_CARD)


def site_card_dir(d):
    (d / SITE_CARD).unlink()
    (d / SITE_CARD).mkdir()


def link(d):
    os.symlink("baseline.css", d / DEST / "linked.css")


def palette_gate_byte(d):
    target = d / PALETTE_GATE
    data = bytearray(target.read_bytes())
    data[-1] ^= 1
    target.write_bytes(bytes(data))


def overflow_check_byte(d):
    target = d / OVERFLOW_CHECK
    data = bytearray(target.read_bytes())
    data[-1] ^= 1
    target.write_bytes(bytes(data))


def palette_gate_link(d):
    (d / PALETTE_GATE).rename(d / ".baseline" / "saved.py")
    os.symlink("saved.py", d / PALETTE_GATE)


def baseline_link(d):
    (d / ".baseline").rename(d / "real-baseline")
    os.symlink("real-baseline", d / ".baseline", target_is_directory=True)


def pin_link(d):
    (d / PIN).rename(d / ".baseline" / "saved.toml")
    os.symlink("saved.toml", d / PIN)


def baseline_extra(name, data=b"x\n"):
    """Write another file into .baseline/, in a subdirectory as named."""
    def mutate(d):
        target = d / ".baseline" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return mutate


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
    ("a pin with no version", edit_pin('version = "1.13.0"', 'release = "1.13.0"'), 1,
     "no version"),
    ("a pin that is not TOML", edit_pin("[files]", "[files"), 1, "not valid TOML"),
    # QA round 1 of #1182: the pin must be the copy script's, and excluded material stays out.
    ("a pin at another version than the copy script's",
     lambda d: (edit_pin('version = "1.13.0"', 'version = "1.3.1"')(d),
                edit_pin("/baseline/1.13.0/", "/baseline/1.3.1/")(d)), 1, "copy-baseline.py copies 1.13.0"),
    ("an upstream URL for another version", edit_pin("/baseline/1.13.0/", "/baseline/1.3.1/"), 1,
     "is not the URL of version 1.13.0"),
    ("another archive digest", edit_pin('archive_sha256 = "e', 'archive_sha256 = "0'), 1,
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
    # Baseline 1.6.0: the palette gate is copied to .baseline/ and pinned by its repository path.
    ("one byte changed in .baseline/check_palette.py", palette_gate_byte, 1,
     ".baseline/check_palette.py differs from its pin"),
    ("the palette gate deleted", lambda d: (d / PALETTE_GATE).unlink(), 1,
     ".baseline/check_palette.py is pinned but missing"),
    ("the palette gate replaced by a symbolic link", palette_gate_link, 1,
     ".baseline/check_palette.py is pinned but is not a regular file"),
    ("the palette gate's pin line removed", edit_pin_line('".baseline/check_palette.py" ='), 1,
     "does not pin .baseline/check_palette.py"),
    ("another .baseline/ file pinned",
     edit_pin('".baseline/check_palette.py" =', '".baseline/other.py" ='), 1,
     "is not under assets/baseline/"),
    # QA round 1 of #1190: .baseline/ is a real directory holding only the pin and the build tool.
    (".baseline/ replaced by a symbolic link to a good copy", baseline_link, 1,
     ".baseline is a symbolic link"),
    (".baseline/ replaced by a file", lambda d: (shutil.rmtree(d / ".baseline"),
                                                (d / ".baseline").write_text("x", encoding="utf-8")),
     1, ".baseline is not a directory"),
    ("pin.toml replaced by a symbolic link", pin_link, 1, ".baseline/pin.toml is not a regular file"),
    ("another file in .baseline/", baseline_extra("notes.txt"), 1,
     ".baseline/notes.txt is not .baseline/pin.toml, .baseline/site-card.toml or a pinned build tool"),
    ("a second copy of the palette gate in .baseline/",
     baseline_extra("check_palette_old.py", (ROOT / PALETTE_GATE).read_bytes()), 1,
     ".baseline/check_palette_old.py is not"),
    ("a subdirectory with a file in .baseline/", baseline_extra("sub/check_palette.py"), 1,
     ".baseline/sub/check_palette.py is not"),
    ("a __pycache__ folder in .baseline/",
     baseline_extra("__pycache__/check_palette.cpython-311.pyc"), 1, ".baseline/__pycache__ is not"),
    ("a symbolic link in .baseline/",
     lambda d: os.symlink("check_palette.py", d / ".baseline" / "palette.py"), 1,
     ".baseline/palette.py is not"),
    # Baseline 1.8.0: the overflow check is copied to .baseline/ and pinned like the palette gate.
    ("one byte changed in .baseline/check_overflow.js", overflow_check_byte, 1,
     ".baseline/check_overflow.js differs from its pin"),
    ("the overflow check deleted", lambda d: (d / OVERFLOW_CHECK).unlink(), 1,
     ".baseline/check_overflow.js is pinned but missing"),
    ("the overflow check's pin line removed", edit_pin_line('".baseline/check_overflow.js" ='), 1,
     "does not pin .baseline/check_overflow.js"),
    # Baseline 1.13.0: the card builder and its fonts are copied to .baseline/ and pinned; the
    # site's own card data file is admitted unpinned, as a regular file only.
    ("one byte changed in .baseline/build_card.js", flip(CARD_BUILDER), 1,
     ".baseline/build_card.js differs from its pin"),
    ("one byte changed in a card font", flip(CARD_FONTS / "Inter-Bold.otf"), 1,
     ".baseline/card-fonts/Inter-Bold.otf differs from its pin"),
    ("a card font deleted", lambda d: (d / CARD_FONTS / "Inter-Regular.otf").unlink(), 1,
     ".baseline/card-fonts/Inter-Regular.otf is pinned but missing"),
    ("a card font's pin line removed", edit_pin_line('".baseline/card-fonts/Inter-ExtraBold.otf" ='), 1,
     "does not pin .baseline/card-fonts/Inter-ExtraBold.otf"),
    ("an extra file in .baseline/card-fonts/", baseline_extra("card-fonts/Extra.otf"), 1,
     ".baseline/card-fonts/Extra.otf is not"),
    (".baseline/card-fonts replaced by a symbolic link to a good copy", card_fonts_link, 1,
     ".baseline/card-fonts is not a real directory"),
    ("the template's card example copied into .baseline/",
     baseline_extra("site-card.example.toml", b'site = "secureconfig"\n'), 1,
     ".baseline/site-card.example.toml is not"),
    ("no .baseline/site-card.toml", lambda d: (d / SITE_CARD).unlink(), 0, "match baseline 1.13.0"),
    (".baseline/site-card.toml replaced by a symbolic link", site_card_link, 1,
     ".baseline/site-card.toml is not a regular file"),
    (".baseline/site-card.toml replaced by a directory", site_card_dir, 1,
     ".baseline/site-card.toml is not a regular file"),
    ("the 1.11.3 Dancing Script woff2 left behind unpinned",
     lambda d: (d / DEST / "fonts" / "dancing-script-latin-wght-normal.woff2").write_bytes(b"wOF2"), 1,
     "fonts/dancing-script-latin-wght-normal.woff2 is not pinned"),
    ("the pristine copy", None, 0, "match baseline 1.13.0"),
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
    refusals = sum(1 for case in CASES if case[2] != 0)
    print(f"  ok    {len(CASES)} baseline pin cases ({refusals} refusals and {len(CASES) - refusals} "
          f"accepted trees, the pristine copy among them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
