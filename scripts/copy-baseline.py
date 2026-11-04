#!/usr/bin/env python3
"""Copy the shared site template's runtime files into the site and write the pin.

Usage: python3 -I -B scripts/copy-baseline.py --from <unpacked baseline version folder> --date <YYYY-MM-DD>

The folder is a verified copy of https://posluns.ca/baseline/<version>/ (its SHA256SUMS checked
against the published digest before this runs). This script checks every file it copies against
that SHA256SUMS, refuses on any mismatch, copies only the runtime and licence files the site
publishes (RUNTIME below) byte for byte into site/assets/baseline/ and the build tools the site
runs but never serves (BUILD_TOOLS below) into .baseline/, and writes .baseline/pin.toml with the
version and each copied file's SHA-256. tools/check_baseline_pin.py then fails if a copied file
ever differs from the pin. Never edit a copied file: a new baseline version is 1 pull request that
reruns this script and commits the result.

Standard library only. No network.
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path("site") / "assets" / "baseline"
PIN = Path(".baseline") / "pin.toml"
VERSION = "1.8.0"
UPSTREAM = f"https://posluns.ca/baseline/{VERSION}/"
# The archive's digest in https://posluns.ca/baseline/SHA256SUMS, and the digest of the version's
# SHA256SUMS in https://posluns.dev/hashes.txt (the template owner's 1.8.0 notice of 2026-11-04).
ARCHIVE_SHA256 = "958a148bf896a4274dc294f230d792e035835eae7d4f8844f8bbcda6ab843197"
SUMS_SHA256 = "e365054b9fd156413cc1581561e43157b587a064bc2e74386faee770ab2ba1ef"
# Pin keys are paths relative to the site root (site/), as the baseline README shows them.
KEY_PREFIX = "assets/baseline/"
# The runtime and licence files the site publishes. The reference pages, tools/measure.js,
# gen_palettes.py, site-palette.example.css, the documentation and the scripts no page loads
# (select.js, search.js, matrix.js) are not copied. Every page loads scheme.js (baseline 1.6.0).
RUNTIME = (
    "LICENSE", "NOTICE.md",
    "baseline.css", "palettes.css", "fonts.css", "copy.js", "rail.js", "scheme.js",
    "fonts/dancing-script-LICENSE.txt", "fonts/dancing-script-latin-wght-normal.woff2",
    "fonts/jetbrains-mono-LICENSE.txt", "fonts/jetbrains-mono-latin-wght-italic.woff2",
    "fonts/jetbrains-mono-latin-wght-normal.woff2",
    "fonts/newsreader-LICENSE.txt", "fonts/newsreader-latin-wght-italic.woff2",
    "fonts/newsreader-latin-wght-normal.woff2",
    "fonts/public-sans-LICENSE.txt", "fonts/public-sans-latin-wght-italic.woff2",
    "fonts/public-sans-latin-wght-normal.woff2",
    "logos/secureconfig.svg", "logos/secureconfig-mono.svg", "logos/secureconfig-favicon.svg",
    "logos/secureconfig-card.svg", "logos/secureconfig-touch.png",
    "logos/opfiles.svg", "logos/auditthis.svg", "logos/cleanlanguage.svg", "logos/aiqt.svg",
    "logos/grclibrary.svg",
    "marks/NOTICE.md", "marks/github-invertocat-black.svg", "marks/github-invertocat-white.svg",
    "marks/linkedin-in-bug.png", "marks/orcid-id.svg",
)
# The build tools the site copies and pins but never serves, package path to repository path; the
# pin keys them by the repository path, as the baseline README shows (SPECIFICATION section 4).
BUILD_TOOLS = {"tools/check_palette.py": ".baseline/check_palette.py"}
HEADER = """\
# Shared site template baseline pin, read by tools/check_baseline_pin.py.
#
# The files under site/assets/baseline/ and .baseline/check_palette.py are copied byte for byte
# from the baseline package at the upstream URL below by scripts/copy-baseline.py, which checked
# each one against the package's SHA256SUMS. Never edit a copied file. A new baseline version is
# 1 pull request that reruns the copy script and commits the copied files and this pin together.
"""


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_sums(folder):
    sums = {}
    for line in (folder / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, sep, name = line.partition("  ")
        if not sep or len(digest) != 64:
            raise ValueError(f"SHA256SUMS line is not in sha256sum form: {line!r}")
        sums[name] = digest
    return sums


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="source", required=True, type=Path)
    ap.add_argument("--date", required=True, help="the copy date, YYYY-MM-DD, recorded in the pin")
    args = ap.parse_args(argv)
    src = args.source
    if sha256(src / "SHA256SUMS") != SUMS_SHA256:
        print(f"  FAIL  {src / 'SHA256SUMS'} is not the published {VERSION} SHA256SUMS")
        return 1
    sums = read_sums(src)
    pins = {}
    for name in (*RUNTIME, *BUILD_TOOLS):
        if name not in sums:
            print(f"  FAIL  {name} is not listed in the package's SHA256SUMS")
            return 1
        if sha256(src / name) != sums[name]:
            print(f"  FAIL  {src / name} differs from the package's SHA256SUMS")
            return 1
        pins[name] = sums[name]
    dest = ROOT / DEST
    if dest.exists():
        shutil.rmtree(dest)
    for name in RUNTIME:
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / name, target)
    for name, repo_path in BUILD_TOOLS.items():
        target = ROOT / repo_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / name, target)
    lines = [HEADER, f'version = "{VERSION}"', f'upstream = "{UPSTREAM}"',
             f'archive_sha256 = "{ARCHIVE_SHA256}"', f'sha256sums_sha256 = "{SUMS_SHA256}"',
             f'copied = "{args.date}"', "",
             "# Paths under assets/baseline/ are relative to site/; the build tools' paths are",
             "# relative to the repository root.", "[files]"]
    lines += [f'"{KEY_PREFIX}{name}" = "{pins[name]}"' for name in sorted(RUNTIME)]
    lines += [f'"{BUILD_TOOLS[name]}" = "{pins[name]}"' for name in sorted(BUILD_TOOLS)]
    (ROOT / PIN).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / PIN).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ok    copied {len(RUNTIME)} files into {DEST} and {len(BUILD_TOOLS)} build tool into "
          f".baseline/, and wrote {PIN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
