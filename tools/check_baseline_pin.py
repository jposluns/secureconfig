#!/usr/bin/env python3
"""Check that the copied site template files match their pin in .baseline/pin.toml.

WHY: the draft site publishes the shared template's runtime files (stylesheets, fonts, the copy
script, logos and marks) copied byte for byte from a published baseline version. A copied file
that is edited, replaced or added to stops being the version every family site shares, and nothing
in a diff of a minified stylesheet or a font says so. This gate fails if any file under the copy
folder differs from its pinned SHA-256.

WHAT IT CHECKS, offline, with the standard library only:

  - .baseline/pin.toml parses as TOML and carries a `version`, an `upstream` URL, the package's
    `sha256sums_sha256`, and a `[files]` table mapping each copied file's path, relative to
    site/draft/ and so starting with assets/baseline/ (the baseline README's form), to a
    64-character SHA-256;
  - every pinned path is a plain relative path inside the copy folder (no `..`, no absolute path,
    no backslash);
  - every pinned file exists as a regular file and hashes to its pin;
  - every entry under the destination is a regular file or directory (no symbolic link, which the
    walk never follows) and every file is pinned exactly once;
  - the pin is the copy script's: its version, its upstream URL for that version and its 2
    provenance digests equal scripts/copy-baseline.py's VERSION, ARCHIVE_SHA256 and SUMS_SHA256,
    and the pinned set is exactly that script's RUNTIME list;
  - nothing pinned or present is material the baseline README keeps out of a site's copy:
    reference/, tools/, gen_palettes.py, contrast-report.txt, SHA256SUMS and the documents
    (every .md other than NOTICE.md and marks/NOTICE.md).

WHAT IT DOES NOT PROVE: that the pin is the published version. scripts/copy-baseline.py checks the
package's SHA256SUMS against the published digest at copy time; this gate checks that nothing has
changed since. It also says nothing about a site/draft/assets/site.css, which would be the site's own file.

Exit 0 when every file matches, 1 on a finding, 2 when the pin or the folder cannot be read.
Usage: python3 -I -B tools/check_baseline_pin.py [--root <repository root>]
"""
import argparse
import hashlib
import importlib.util
import re
import stat
import sys
import tomllib
from pathlib import Path, PurePosixPath

PIN = Path(".baseline") / "pin.toml"
DEST = "site/draft/assets/baseline"
KEY_PREFIX = "assets/baseline/"
HEX64 = re.compile(r"[0-9a-f]{64}")


def copy_script():
    """scripts/copy-baseline.py beside this gate, imported for its VERSION, digests and RUNTIME."""
    path = Path(__file__).resolve().parents[1] / "scripts" / "copy-baseline.py"
    spec = importlib.util.spec_from_file_location("copy_baseline", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def excluded(name):
    """True for a path the baseline README keeps out of a site's copy."""
    parts = PurePosixPath(name).parts
    base = parts[-1] if parts else ""
    return (bool(parts) and parts[0] in ("reference", "tools")
            or base in ("gen_palettes.py", "contrast-report.txt", "SHA256SUMS")
            or (base.lower().endswith(".md") and name not in ("NOTICE.md", "marks/NOTICE.md")))


def walk(folder):
    """(relative posix path, mode) for every entry under folder, over lstat, following no link."""
    out, pending = [], [folder]
    while pending:
        path = pending.pop()
        mode = path.lstat().st_mode
        if path != folder:
            out.append((path.relative_to(folder).as_posix(), mode))
        if stat.S_ISDIR(mode):
            pending.extend(sorted(path.iterdir(), reverse=True))
    return out


def check(root):
    """(exit status, lines to print)."""
    try:
        pin = tomllib.loads((root / PIN).read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        return 2, [f"  FAIL  cannot read {PIN}: {exc}"]
    except tomllib.TOMLDecodeError as exc:
        return 1, [f"  FAIL  {PIN} is not valid TOML: {exc}"]
    findings = []
    for key in ("version", "upstream", "sha256sums_sha256"):
        if not isinstance(pin.get(key), str) or not pin[key].strip():
            findings.append(f"{PIN} has no {key} string")
    if isinstance(pin.get("sha256sums_sha256"), str) and not HEX64.fullmatch(pin["sha256sums_sha256"]):
        findings.append(f"{PIN} sha256sums_sha256 is not a 64-character lower-case hex digest")
    keyed = pin.get("files")
    if not isinstance(keyed, dict) or not keyed:
        findings.append(f"{PIN} has no [files] table")
        keyed = {}
    # Keys are paths relative to site/draft/ (the baseline README's form), so each starts with
    # assets/baseline/; the checks below read them relative to the copy folder.
    files = {}
    for key, digest in keyed.items():
        if not key.startswith(KEY_PREFIX):
            findings.append(f"{PIN} pins {key!r}, which is not under {KEY_PREFIX}")
            continue
        files[key[len(KEY_PREFIX):]] = digest
    # The pin must be the copy script's: the same version and provenance, and exactly its RUNTIME
    # list, so a file the script never copies (a reference page, a tool) cannot be pinned in.
    copy = copy_script()
    if pin.get("version") != copy.VERSION:
        findings.append(f"{PIN} names version {pin.get('version')!r}; scripts/copy-baseline.py "
                        f"copies {copy.VERSION}")
    elif pin.get("upstream") != f"https://posluns.ca/baseline/{pin['version']}/":
        findings.append(f"{PIN} names upstream {pin.get('upstream')!r}, which is not the URL of "
                        f"version {pin['version']}")
    for key, want in (("archive_sha256", copy.ARCHIVE_SHA256), ("sha256sums_sha256", copy.SUMS_SHA256)):
        if pin.get(key) != want:
            findings.append(f"{PIN} {key} is {pin.get(key)!r}; scripts/copy-baseline.py records {want}")
    for name in sorted(files):
        if excluded(name):
            findings.append(f"{PIN} pins {name}, which the baseline README excludes from the copy "
                            f"(reference/, tools/, gen_palettes.py, contrast-report.txt and the "
                            f"documents other than the NOTICE.md files)")
        elif name not in copy.RUNTIME:
            findings.append(f"{PIN} pins {name}, which is not in scripts/copy-baseline.py's RUNTIME list")
    for name in sorted(set(copy.RUNTIME) - set(files)):
        findings.append(f"{PIN} does not pin {name}, which scripts/copy-baseline.py copies")
    dest = root / DEST
    for name, digest in sorted(files.items()):
        pure = PurePosixPath(name)
        if (not name or "\\" in name or pure.is_absolute() or ".." in pure.parts
                or pure.as_posix() != name):
            findings.append(f"{PIN} pins {name!r}, which is not a plain relative path inside {DEST}")
            continue
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            findings.append(f"{PIN} pins {name} to {digest!r}, which is not a SHA-256 hex digest")
            continue
        target = dest / name
        try:
            mode = target.lstat().st_mode
        except FileNotFoundError:
            findings.append(f"{DEST}/{name} is pinned but missing")
            continue
        except OSError as exc:
            return 2, [f"  FAIL  cannot read {DEST}/{name}: {exc}"]
        if not stat.S_ISREG(mode):
            findings.append(f"{DEST}/{name} is pinned but is not a regular file")
            continue
        try:
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
        except OSError as exc:
            return 2, [f"  FAIL  cannot read {DEST}/{name}: {exc}"]
        if actual != digest:
            findings.append(f"{DEST}/{name} differs from its pin (sha256 {actual}, pinned "
                            f"{digest}); a copied baseline file must never be edited")
    try:
        mode = dest.lstat().st_mode
    except OSError as exc:
        return 2, [f"  FAIL  cannot read {DEST}: {exc}"]
    if not stat.S_ISDIR(mode):
        findings.append(f"{DEST} is not a directory")
        entries = []
    else:
        try:
            entries = walk(dest)
        except OSError as exc:
            return 2, [f"  FAIL  cannot walk {DEST}: {exc}"]
    for name, mode in entries:
        if stat.S_ISLNK(mode):
            findings.append(f"{DEST}/{name} is a symbolic link; the copy holds regular files only")
        elif excluded(name) and name not in files:
            findings.append(f"{DEST}/{name} is material the baseline README excludes from the "
                            f"copy (reference/, tools/, gen_palettes.py, contrast-report.txt and "
                            f"the documents other than the NOTICE.md files)")
        elif stat.S_ISREG(mode) and name not in files:
            findings.append(f"{DEST}/{name} is not pinned in {PIN}; the copy folder holds only "
                            f"files copied from the baseline package")
        elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            findings.append(f"{DEST}/{name} is not a regular file or directory")
    if findings:
        return 1, [f"  FAIL  {f}" for f in findings]
    return 0, [f"  ok    {len(files)} files under {DEST} match baseline {pin['version']} as "
               f"pinned in {PIN}"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    status, lines = check(args.root)
    for line in lines:
        print(line)
    return status


if __name__ == "__main__":
    sys.exit(main())
