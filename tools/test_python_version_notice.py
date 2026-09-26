#!/usr/bin/env python3
"""Exercise the suite's real advisory block; every outcome must preserve its fail flag."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = 'echo "== local Python release matches CI =="'
END = 'echo "== the Python-version notice still reports without failing =="'


def main():
    suite = (ROOT / "tools/run_all_checks.sh").read_text(encoding="utf-8")
    if suite.count(START) != 1 or suite.count(END) != 1:
        print("  FAIL  cannot locate the Python-version notice block")
        return 1
    block = suite.split(START, 1)[1].split(END, 1)[0]
    # Use the same python3 the shell block will invoke, even if this test was launched
    # with a different interpreter. Do not hard-code CI's current pin.
    running = subprocess.check_output(
        ["python3", "-c", "import sys; print(sys.version.split()[0])"], text=True).strip()
    exact_release = re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", running) is not None
    pin = f'      PYTHON_VERSION: "{running}"\n'.encode()
    other = "0.0.0" if running != "0.0.0" else "0.0.1"
    other_pin = f'      PYTHON_VERSION: "{other}"\n'.encode()
    differs = f"  SKIP  python3 {running} differs from CI's pinned PYTHON_VERSION {other}"
    cases = [
        ("different release", f'      PYTHON_VERSION: "{other}"\n'.encode(),
         f"  SKIP  python3 {running} differs from CI's pinned PYTHON_VERSION {other}", ""),
        ("missing pin", b"env:\n", "found 0 PYTHON_VERSION keys and 0 pin lines", ""),
        # A key inside a YAML comment still counts. This is intended fail-closed behaviour:
        # a false SKIP on this advisory notice is harmless, a false ok is not.
        ("comment only", b'# PYTHON_VERSION: "1.2.3"\n',
         "found 1 PYTHON_VERSION keys and 0 pin lines", ""),
        ("comment beside pin", b'# PYTHON_VERSION: "1.2.3"\n' + other_pin,
         "found 2 PYTHON_VERSION keys and 1 pin lines", ""),
        ("malformed pin", b'  PYTHON_VERSION: "1.2"\n',
         "found 1 PYTHON_VERSION keys and 0 pin lines", ""),
        ("single quotes", b"  PYTHON_VERSION: '1.2.3'\n",
         "found 1 PYTHON_VERSION keys and 0 pin lines", ""),
        ("duplicate pins", other_pin + other_pin,
         "found 2 PYTHON_VERSION keys and 2 pin lines", ""),
        ("mixed duplicate", other_pin + b"  PYTHON_VERSION: broken\n",
         "found 2 PYTHON_VERSION keys and 1 pin lines", ""),
        ("flow-mapping second pin", other_pin + b'    env: {PYTHON_VERSION: "1.2.3"}\n',
         "found 2 PYTHON_VERSION keys and 1 pin lines", ""),
        ("flow mapping, quoted key", other_pin + b'    env: {"PYTHON_VERSION": "1.2.3"}\n',
         "found 2 PYTHON_VERSION keys and 1 pin lines", ""),
        # References are not pins and must not count.
        ("expression reference", other_pin
         + b"          python-version: ${{ env.PYTHON_VERSION }}\n", differs, ""),
        ("shell references", other_pin
         + b'          run: echo "$PYTHON_VERSION ${PYTHON_VERSION}"\n', differs, ""),
        ("missing workflow", None, "cannot read .github/workflows/checks.yml", ""),
        ("invalid encoding", b"\xff", "cannot read .github/workflows/checks.yml", ""),
        ("unavailable interpreter", pin, "python3 did not complete",
         "python3() { return 127; }\n"),
    ]
    for name, key in (
        ("spaced key", "PYTHON_VERSION :"),
        ("single-quoted key", "'PYTHON_VERSION':"),
        ("double-quoted key", '"PYTHON_VERSION":'),
        ("single-quoted spaced key", "'PYTHON_VERSION' :"),
        ("double-quoted spaced key", '"PYTHON_VERSION" :'),
    ):
        for indent in ("", "  ", "        "):
            alternate = f'{indent}{key} "{running}"\n'.encode()
            label = f"{name}, indent={len(indent)}"
            cases.extend([
                (label, alternate, "found 1 PYTHON_VERSION keys and 0 pin lines", ""),
                (f"duplicate {label}", other_pin + alternate,
                 "found 2 PYTHON_VERSION keys and 1 pin lines", ""),
            ])
    if exact_release:
        cases.extend([
            ("matching release", pin,
             f"  ok    python3 {running} matches CI's pinned PYTHON_VERSION", ""),
            ("matching pin, expression reference",
             pin + b"          python-version: ${{ env.PYTHON_VERSION }}\n",
             f"  ok    python3 {running} matches CI's pinned PYTHON_VERSION", ""),
            ("matching pin, shell references",
             pin + b'          run: echo "$PYTHON_VERSION ${PYTHON_VERSION}"\n',
             f"  ok    python3 {running} matches CI's pinned PYTHON_VERSION", ""),
        ])
    else:
        cases.append(("non-release pin refused", pin,
                      "found 1 PYTHON_VERSION keys and 0 pin lines", ""))
    failures = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        workflow = root / ".github/workflows/checks.yml"
        workflow.parent.mkdir(parents=True)
        for name, content, expected, setup in cases:
            if content is None:
                workflow.unlink(missing_ok=True)
            else:
                workflow.write_bytes(content)
            for initial in (0, 1):
                result = subprocess.run(
                    ["bash", "-c", f"set -uo pipefail\nfail={initial}\n" + setup
                     + block + '\nexit "$fail"\n'],
                    cwd=root, capture_output=True, text=True)
                output = result.stdout + result.stderr
                prefix = "  ok    " if expected.startswith("  ok    ") else "  SKIP  "
                if (result.returncode != initial or expected not in output
                        or not result.stdout.startswith(prefix)
                        or "  FAIL  " in output):
                    failures.append(f"{name}, fail={initial}: exit {result.returncode}: {output!r}")
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {len(cases) * 2} recorded cases for the Python-version notice")
    return 0


if __name__ == "__main__":
    sys.exit(main())
