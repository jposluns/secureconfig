#!/usr/bin/env python3
"""Cases for check_security_txt.py: the real file passes, and each defect it names fails.

Each case copies the real gate into a throwaway tree, writes site/.well-known/security.txt (the
real file, or a mutation of it) and runs the gate as a subprocess, so what is under test is the
shipped entry point. A must-fail case names a substring its finding must carry, and every case
checks the exit status, the ok line on a pass and a FAIL line on a refusal. Removing any one check
from the gate turns at least one case red.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
REAL = (ROOT / "site" / ".well-known" / "security.txt").read_bytes().decode("utf-8")
FIELDS = (("Contact", "mailto:jeff@posluns.ca"),
          ("Expires", "2030-10-31T00:00:00Z"),
          ("Encryption", "https://posluns.ca/security/pgp-key.txt"),
          ("Policy", "https://posluns.ca/security/"),
          ("Preferred-Languages", "en, fr"),
          ("Canonical", "https://secureconfig.ai/.well-known/security.txt"))


def run(content=REAL, setup=None):
    """Run the real gate against a tree holding `content` (str or bytes, or None for no file)."""
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        shutil.copy(TOOLS / "check_security_txt.py", d / "tools" / "check_security_txt.py")
        (d / "site" / ".well-known").mkdir(parents=True)
        if content is not None:
            data = content if isinstance(content, bytes) else content.encode("utf-8")
            (d / "site" / ".well-known" / "security.txt").write_bytes(data)
        if setup is not None:
            setup(d)
        r = subprocess.run([sys.executable, "-I", "-B", "tools/check_security_txt.py"], cwd=d,
                           capture_output=True, text=True, timeout=20)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def symlinked(d):
    target = d / "site" / ".well-known" / "real.txt"
    target.write_text(REAL, encoding="utf-8")
    (d / "site" / ".well-known" / "security.txt").symlink_to("real.txt")


def directory(d):
    (d / "site" / ".well-known" / "security.txt").mkdir()


def legacy(d):
    (d / "site" / "security.txt").write_text(REAL, encoding="utf-8")


# (description, content, setup, expected substring for a refusal or None for a pass)
CASES = [
    ("the real file", REAL, None, None),
    ("the real file with a comment and a blank line", "# Security contact\n\n" + REAL, None, None),
    ("the six fields in another order", "".join(f"{n}: {v}\n" for n, v in reversed(FIELDS)),
     None, None),
    ("no file at all", None, None, "is missing"),
    ("the file as a symbolic link", None, symlinked, "symbolic link"),
    ("a directory where the file belongs", None, directory, "not a regular file"),
    ("a second copy at the legacy /security.txt", REAL, legacy, "site/security.txt exists"),
    ("bytes that are not UTF-8", REAL.encode("utf-8") + b"\xff\n", None, "as UTF-8"),
    ("a byte order mark", "﻿" + REAL, None, "byte order mark"),
    ("CRLF line endings", REAL.replace("\n", "\r\n"), None, "control character"),
    ("a NUL byte", REAL.replace("Policy", "Pol\x00icy", 1), None, "control character"),
    ("no LF after the last line", REAL.rstrip("\n"), None, "does not end with LF"),
    ("a field with no space after the colon",
     REAL.replace("Policy: ", "Policy:", 1), None, "not a blank line"),
    ("a field indented", REAL.replace("Policy: ", " Policy: ", 1), None, "not a blank line"),
    ("trailing whitespace on a value", REAL.replace("en, fr", "en, fr ", 1), None,
     "not a blank line"),
    ("an extra field the owner did not set", REAL + "Hiring: https://posluns.ca/jobs/\n", None,
     "carries the field Hiring"),
    ("a field name in other capitals", REAL.replace("Contact:", "contact:", 1), None,
     "carries the Contact field 0 times"),
    ("a duplicated field", REAL + "Contact: mailto:jeff@posluns.ca\n", None,
     "carries the Contact field 2 times"),
]
for name, value in FIELDS:
    CASES.append((f"the {name} field removed",
                  REAL.replace(f"{name}: {value}\n", "", 1), None,
                  f"carries the {name} field 0 times"))
    CASES.append((f"the {name} field changed",
                  REAL.replace(f"{name}: {value}\n", f"{name}: {value}x\n", 1), None,
                  f"sets {name} to"))
CASES.append(("Canonical on another host",
              REAL.replace("https://secureconfig.ai/", "https://secureconfig.example/", 1), None,
              "sets Canonical to"))
CASES.append(("Expires a year earlier", REAL.replace("2030-10-31", "2029-10-31", 1), None,
              "sets Expires to"))


def main() -> int:
    failures = []
    for desc, content, setup, expected in CASES:
        if content is not None and expected is not None and content == REAL and setup is None:
            failures.append(f"{desc}: the mutation did not change the real file")
            continue
        rc, out = run(content, setup)
        if rc != (0 if expected is None else 1):
            failures.append(f"{desc}: expected the gate to {'pass' if expected is None else 'fail'}"
                            f", exit {rc}: {out!r}")
        elif expected is not None and expected not in out:
            failures.append(f"{desc}: expected a finding containing {expected!r}: {out!r}")
        elif expected is None and ("  FAIL  " in out or not out.startswith("ok    ")):
            failures.append(f"{desc}: a pass must print one ok line and no FAIL line: {out!r}")
        elif expected is not None and not out.startswith("FAIL  "):
            failures.append(f"{desc}: a refusal must print a FAIL line: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} recorded cases for the security.txt gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
