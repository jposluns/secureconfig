#!/usr/bin/env python3
"""Exercise the suite's actual secrets block against readable and denied paths."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = 'echo "== no committed secrets =="'
END = 'echo "== secrets scan fails closed on read errors =="'


def main():
    suite = (ROOT / "tools/run_all_checks.sh").read_text(encoding="utf-8")
    assert suite.count(START) == suite.count(END) == 1, "cannot locate secrets block"
    block = suite.split(START, 1)[1].split(END, 1)[0]
    # Reuse the shipped reporting functions and fail flag as well as the scan.
    reporting = suite.split("fail=0\n", 1)[1].split("\n# Root-level", 1)[0]
    token = "ghp_" + "A" * 36
    cases = [
        ("clean", {"clean.txt": "clean\n"}, (), False, "no private keys"),
        ("git excluded", {".git/hidden": token}, (), False, "no private keys"),
        ("untracked secret", {"local.txt": token}, (), True, "./local.txt:1:"),
        ("ignored secret", {".gitignore": "ignored/\n", "ignored/key": token},
         (), True, "./ignored/key:1:"),
        ("site secret", {"site/key": token}, (), True, "./site/key:1:"),
        ("plugin secret", {"plugin/key": token}, (), True, "./plugin/key:1:"),
        ("unreadable file", {"locked.txt": "clean\n"}, ("locked.txt",),
         True, "./locked.txt: Permission denied"),
        ("unreadable directory", {"locked/hidden": "clean\n"}, ("locked",),
         True, "./locked: Permission denied"),
        ("hits and read error", {"local.txt": token, "locked/hidden": "clean\n"},
         ("locked",), True, "./locked: Permission denied"),
    ]
    count = 0
    for label, files, blocked, fails, needle in cases:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            modes = []
            try:
                for name in blocked:
                    path = root / name
                    modes.append((path, path.stat().st_mode))
                    path.chmod(0)
                    try:
                        if path.is_dir():
                            list(path.iterdir())
                        else:
                            path.read_bytes()
                    except PermissionError:
                        pass
                    else:
                        raise AssertionError(f"fixture is still readable: {name}")
                for initial in (0, 1):
                    result = subprocess.run(
                        ["bash", "-c", f"set -uo pipefail\nfail={initial}\n"
                         + reporting + block + '\nexit "$fail"\n'],
                        cwd=root, capture_output=True, text=True, timeout=30,
                        env={**os.environ, "LC_ALL": "C"},
                    )
                    output = result.stdout + result.stderr
                    assert result.returncode == int(fails or initial), (label, output)
                    assert needle in output, (label, output)
                    assert ("  FAIL  " in output) == fails, (label, output)
                    assert ("  ok    " in output) == (not fails), (label, output)
                    if blocked:
                        assert "cannot complete secrets scan (grep exit 2)" in output, output
                    count += 1
            finally:
                for path, mode in reversed(modes):
                    path.chmod(mode)
    print(f"  ok    {count} recorded cases for the secrets scan")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  secrets scan self-test: {exc}")
        sys.exit(1)
