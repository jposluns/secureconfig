#!/usr/bin/env python3
"""Check site/.well-known/security.txt against the owner's six W3 fields, offline.

WHY: secureconfig.ai serves `/.well-known/security.txt` (RFC 9116) from this repository, and the
owner has switched off Cloudflare's own security.txt feature (his decision of 2026-11-03, the same
for all six project sites). He fixed the fields and their values. A wrong mailbox, a mistyped
policy URL or a dropped Expires field would send a reporter nowhere, and nothing else in the suite
reads the file, so this gate compares it with the values recorded in EXPECTED.

WHAT IT CHECKS, reading the file as strict UTF-8:

  - the file is a regular file at site/.well-known/security.txt, not a symbolic link, and there is
    no second copy at site/security.txt, the legacy location, which could drift from this one;
  - it has no byte order mark, no CR and no other control character except tab and LF, and its
    last line ends with LF;
  - every line is blank, a comment starting with `#`, or one field written `Name: value`, with the
    name in ASCII letters, digits and hyphens, one space after the colon, and a value that neither
    starts nor ends with whitespace;
  - it carries each of the six fields in EXPECTED exactly once, spelled with EXPECTED's capitals,
    each with exactly the value EXPECTED records, and no other field. Canonical is this file's own
    URL on the site's host.

WHAT IT DOES NOT CHECK: whether the live domain serves the file, under which Content-Type, or at
all, since Cloudflare Pages' handling of a dot-directory is checked on the live domain after a
deploy; whether the mailbox, the key or the policy page exist; and whether Expires lies in the
future, because a gate that reads the clock is not deterministic. The value is 2030-10-31, which
the owner chose; RFC 9116 recommends an Expires less than a year in the future, and the owner's
value does not follow that recommendation. A digitally signed file would fail the line rules
above; this one is not signed.

Exit 0 with one ok line, or 1 with one FAIL line per finding.
"""
import re
import stat
import sys
from pathlib import Path

SITE = Path("site")
FILE = SITE / ".well-known" / "security.txt"
LEGACY = SITE / "security.txt"
HOST = "secureconfig.ai"
# The owner's W3 fields and values (2026-11-03), in the order the file writes them.
EXPECTED = (
    ("Contact", "mailto:jeff@posluns.ca"),
    ("Expires", "2030-10-31T00:00:00Z"),
    ("Encryption", "https://posluns.ca/security/pgp-key.txt"),
    ("Policy", "https://posluns.ca/security/"),
    ("Preferred-Languages", "en, fr"),
    ("Canonical", f"https://{HOST}/.well-known/security.txt"),
)
FIELD = re.compile(r"([A-Za-z0-9-]+): (\S(?:.*\S)?)")
# Every C0 control character except tab and LF, and DEL. CR is among them.
CONTROL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def check(root):
    """Every finding for the security.txt under `root`, as display strings."""
    path = root / FILE
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return [f"{FILE} is missing; the site serves no security.txt"]
    except OSError as exc:
        return [f"cannot inspect {FILE}: {exc}"]
    if stat.S_ISLNK(mode):
        return [f"{FILE} is a symbolic link; ship the file itself, so what is checked is what is "
                f"served"]
    if not stat.S_ISREG(mode):
        return [f"{FILE} is not a regular file"]
    try:
        text = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read {FILE} as UTF-8: {exc}"]

    findings = []
    try:
        (root / LEGACY).lstat()
    except FileNotFoundError:
        pass
    except OSError as exc:
        findings.append(f"cannot inspect {LEGACY}: {exc}")
    else:
        findings.append(f"{LEGACY} exists beside {FILE}; keep the one file at /.well-known/, so two "
                        f"copies cannot drift apart")
    if text.startswith("﻿"):
        findings.append(f"{FILE} starts with a byte order mark")
    if CONTROL.search(text):
        findings.append(f"{FILE} carries a CR or another control character other than tab and LF")
    if not text.endswith("\n"):
        findings.append(f"{FILE} does not end with LF")

    seen = {}
    for number, line in enumerate(text.split("\n"), 1):
        if not line.strip() or line.startswith("#"):
            continue
        m = FIELD.fullmatch(line)
        if m is None:
            findings.append(f"{FILE}:{number} is not a blank line, a # comment or one field "
                            f"written `Name: value`")
        else:
            seen.setdefault(m.group(1), []).append((number, m.group(2)))
    for name, value in EXPECTED:
        got = seen.pop(name, [])
        if len(got) != 1:
            findings.append(f"{FILE} carries the {name} field {len(got)} times; it must carry it "
                            f"exactly once, as {name}: {value}")
        elif got[0][1] != value:
            findings.append(f"{FILE}:{got[0][0]} sets {name} to {got[0][1]!r}; the owner's value is "
                            f"{value!r}")
    for name, got in sorted(seen.items()):
        findings.append(f"{FILE}:{got[0][0]} carries the field {name}, which is not one of the six "
                        f"this gate records ({', '.join(n for n, _ in EXPECTED)})")
    return findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = check(root)
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    {FILE} carries exactly the owner's {len(EXPECTED)} fields with their values "
          f"({', '.join(n for n, _ in EXPECTED)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
