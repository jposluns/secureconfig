#!/usr/bin/env python3
"""Preflight for tools/run_all_checks.sh: this python3 carries the pinned gate parser.

WHY: several gates parse Markdown with markdown-it-py at the version pinned in
tools/requirements-gates.txt and refuse any other release. On a host whose python3 has
another release, each of those gates printed its own FAIL line and traceback
(`ParserUnavailable: markdown-it-py installed 3.0.0, pinned 4.2.0`), which read like
code findings, so a red local run could be mistaken for a red tree. CI installs the pin
before the suite runs and is not affected. This check runs first, under the same
`python3 -I -B` form that the parser gates and CI's parser assertion use, and turns that
host state into one line and exit status 2, before any other gate runs.

WHAT IT CHECKS: it reads the markdown-it-py pin from tools/requirements-gates.txt, never
from this file, imports `markdown_it` and compares `markdown_it.__version__` with the pin.
A match prints one `ok` line and exits 0. A mismatch, a missing package or a failed import
prints one FAIL line naming the interpreter, what it found and the pin, says that it is a
host problem, not a code finding, names the fix and exits 2. An unreadable or unparsable
lock also exits 2 with one FAIL line, which says so instead, because the lock is a file in
this checkout and the host fix would not repair it.

WHAT IT DOES NOT CHECK: mdurl, the parser's runtime dependency, is pinned in the same lock
and checked by the gates themselves, not here, so a mismatched mdurl still reaches them.
It compares the module's `__version__`, not the distribution metadata that
`gate_parser()` in tools/check_verify_marking.py reads; the two agree for an ordinary
install. Under `-I`, PYTHONPATH and the user site directory are ignored, so a parser
reachable only through either is reported as missing even where a gate run without `-I`
would find it.

Deterministic and offline: it reads one file and imports one module.
"""
import re
import sys
from pathlib import Path

LOCK = Path(__file__).resolve().with_name("requirements-gates.txt")
LOCK_NAME = "tools/requirements-gates.txt"
PACKAGE = "markdown-it-py"
# The lock-line shape gate_parser() in tools/check_verify_marking.py accepts.
PIN_RE = re.compile(r"([a-z][a-z0-9-]*)==([0-9.]+) --hash=sha256:[0-9a-f]{64}")
PREFIX = "gate parser preflight: "
FIX = ("this is a host problem, not a code finding, and the suite ran no other gate; "
       "fix: python3 -m venv DIR, then DIR/bin/python3 -m pip install --require-hashes "
       f"--only-binary :all: -r {LOCK_NAME}, then put DIR/bin first on PATH and rerun")
LOCK_FIX = (f"{LOCK_NAME} is part of this checkout, so restore it from main or make it "
            "readable; the suite ran no other gate")


class PinError(ValueError):
    """The lock cannot be read, or does not pin markdown-it-py exactly once."""


def pinned_version(lock=LOCK):
    """Return the markdown-it-py version the lock pins, or raise PinError."""
    try:
        text = Path(lock).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PinError(f"cannot read {LOCK_NAME}: {exc}") from exc
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise PinError(f"cannot parse {LOCK_NAME} line {number}: {line!r}")
        if match[1] == PACKAGE:
            found.append(match[2])
    if len(found) != 1:
        raise PinError(f"cannot parse {LOCK_NAME}: expected one {PACKAGE} pin, "
                       f"found {len(found)}")
    return found[0]


def installed_version():
    """Import the parser the gates import and return its own version string."""
    import markdown_it
    return markdown_it.__version__


def found_text(version_source):
    """Return (version or None, what was found, as the line reports it)."""
    try:
        found = version_source()
    except ModuleNotFoundError as exc:
        if exc.name == "markdown_it":
            return None, f"no {PACKAGE} (markdown_it is not installed)"
        return None, f"a failed import of markdown_it ({type(exc).__name__}: {exc})"
    except Exception as exc:  # A broken install can raise anything on import.
        return None, f"a failed import of markdown_it ({type(exc).__name__}: {exc})"
    if not isinstance(found, str):
        return None, f"a failed import of markdown_it (__version__ is {found!r})"
    return found, f"{PACKAGE} {found}"


def preflight(lock=LOCK, version_source=installed_version, interpreter=None):
    """Return (exit status, the one line to print)."""
    where = f"python3 at {interpreter or sys.executable or 'an unknown path'}"
    found, found_line = found_text(version_source)
    try:
        wanted = pinned_version(lock)
    except PinError as exc:
        return 2, (f"  FAIL  {PREFIX}{where} has {found_line}, but the pinned version is "
                   f"unknown: {exc}; {LOCK_FIX}")
    if found == wanted:
        return 0, f"  ok    {PREFIX}{where} has {found_line}, as {LOCK_NAME} pins"
    return 2, f"  FAIL  {PREFIX}{where} has {found_line}, but {LOCK_NAME} pins {wanted}; {FIX}"


def main():
    status, line = preflight()
    print(line.replace("\n", " ").replace("\r", " "))
    return status


if __name__ == "__main__":
    sys.exit(main())
