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

WHAT IT CHECKS: it reads every pin from tools/requirements-gates.txt, never from this
file, through `parser_lock_pins()` in tools/check_verify_marking.py, the lock reader that
`gate_parser()` there uses, so it refuses exactly the locks `gate_parser()` refuses: a line
that is not a hashed pin, a package pinned twice, and a lock whose pins are not exactly
markdown-it-py and mdurl. It imports `markdown_it` and compares `markdown_it.__version__`
with the markdown-it-py pin. After that import succeeds, it compares the installed version
of both packages the lock pins through `importlib.metadata.version`, as `gate_parser()`
does. A match prints one `ok` line and exits 0. A mismatch, a missing package or a failed
import or metadata lookup prints one FAIL line naming the interpreter, the package and
version it found and the pin, says that it is a host problem, not a code finding, names the
fix and exits 2. An unreadable lock, or one `gate_parser()` would refuse, also exits 2 with
one FAIL line, which says so instead, naming what the lock holds and the rule it breaks,
because the lock is a file in this checkout and the host fix would not repair it.

WHAT IT DOES NOT CHECK: it compares versions only, so an install whose version strings
match the pin but whose files are damaged passes here and fails in the gates. Under `-I`,
PYTHONPATH and the user site directory are ignored, so a parser reachable only through
either is reported as missing even where a gate run without `-I` would find it.

Deterministic and offline: it reads one file, imports tools/check_verify_marking.py for
its lock reader and `markdown_it` for its version, and reads installed distribution
metadata.
"""
import sys
from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path

# Under -I the script's directory is not on sys.path; check_verify_marking.py adds it the
# same way for its own helpers.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_verify_marking import (  # noqa: E402
    PARSER_LOCK_RULE, ParserLockError, parser_lock_pins)

LOCK = Path(__file__).resolve().with_name("requirements-gates.txt")
LOCK_NAME = "tools/requirements-gates.txt"
PACKAGE = "markdown-it-py"
PREFIX = "gate parser preflight: "
FIX = ("this is a host problem, not a code finding, and the suite ran no other gate; "
       "fix: python3 -m venv DIR, then DIR/bin/python3 -m pip install --require-hashes "
       f"--only-binary :all: -r {LOCK_NAME}, then put DIR/bin first on PATH and rerun")
LOCK_FIX = (f"{LOCK_NAME} is part of this checkout, so restore it from main or make it "
            "readable; the suite ran no other gate")


class PinError(ValueError):
    """The lock cannot be read, or is one gate_parser() refuses."""


def pinned_versions(lock=LOCK):
    """Return {package: version} for the lock's pins, markdown-it-py and mdurl, in lock order,
    or raise PinError."""
    try:
        text = Path(lock).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PinError(f"cannot read {LOCK_NAME}: {exc}") from exc
    try:
        return parser_lock_pins(text)
    except ParserLockError as exc:
        raise PinError(f"cannot parse {LOCK_NAME} as gate_parser() in "
                       f"tools/check_verify_marking.py does: it has {exc.found}; that reader "
                       f"refuses it ({exc}) because {PARSER_LOCK_RULE}") from exc


def pinned_version(lock=LOCK):
    """Return the markdown-it-py version the lock pins, or raise PinError."""
    return pinned_versions(lock)[PACKAGE]


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


def metadata_text(package, metadata_source):
    """Return (installed version or None, what was found, as the line reports it)."""
    try:
        found = metadata_source(package)
    except PackageNotFoundError:
        return None, f"no {package} distribution metadata"
    except Exception as exc:  # A damaged dist-info can raise anything.
        return None, f"a failed metadata lookup for {package} ({type(exc).__name__}: {exc})"
    if not isinstance(found, str):
        return None, f"a failed metadata lookup for {package} (version is {found!r})"
    if package == PACKAGE:
        return found, f"{PACKAGE} distribution metadata {found}"
    return found, f"{package} {found}"


def preflight(lock=LOCK, version_source=installed_version, interpreter=None,
              metadata_source=distribution_version):
    """Return (exit status, the one line to print)."""
    where = f"python3 at {interpreter or sys.executable or 'an unknown path'}"
    found, found_line = found_text(version_source)
    try:
        pins = pinned_versions(lock)
    except PinError as exc:
        return 2, (f"  FAIL  {PREFIX}{where} has {found_line}, but the pinned version is "
                   f"unknown: {exc}; {LOCK_FIX}")
    wanted = pins[PACKAGE]
    if found != wanted:
        return 2, (f"  FAIL  {PREFIX}{where} has {found_line}, but {LOCK_NAME} pins "
                   f"{wanted}; {FIX}")
    matched = [found_line]
    for package, pinned in pins.items():
        installed, text = metadata_text(package, metadata_source)
        if installed != pinned:
            return 2, (f"  FAIL  {PREFIX}{where} has {text}, but {LOCK_NAME} pins "
                       f"{pinned}; {FIX}")
        if package != PACKAGE:
            matched.append(text)
    return 0, f"  ok    {PREFIX}{where} has {' and '.join(matched)}, as {LOCK_NAME} pins"


def main():
    status, line = preflight()
    print(line.replace("\n", " ").replace("\r", " "))
    return status


if __name__ == "__main__":
    sys.exit(main())
