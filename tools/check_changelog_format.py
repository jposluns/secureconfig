#!/usr/bin/env python3
"""Check the dated headings in CHANGELOG.md: a blank line after each, newest first, one per date.

WHAT THIS CATCHES: TODO row 3.45 records a `## YYYY-MM-DD` heading without a blank line
after it slipping through on 2026-10-23, and six older headings, for 2026-09-19 to
2026-09-14, lacked the blank line too. Nothing checked the file's dated headings, though
`latest_change()` in tools/version_basis.py reads the newest of them as the calendar bound
for every guide's `checked` field, and the file is read newest first. A date out of order,
or a second heading for one date, splits a day's changes across two places.

WHAT IT CHECKS, reading CHANGELOG.md as LF-separated lines:

- a dated heading is a line that is exactly `## YYYY-MM-DD`, with trailing spaces or tabs
  allowed, the shape `latest_change()` reads, so the two gates agree on which lines are
  dated headings;
- the line after each dated heading is empty; a line holding only spaces or tabs is not,
  and neither is the end of the file;
- each dated heading names a calendar date older than the dated heading above it, so the
  headings are strictly descending;
- no date has two headings;
- a line that opens like a dated heading but is not exactly one fails, so a malformed
  heading cannot drop out of the three checks above. "Opens like" means up to three
  spaces, one or more `#`, optional spaces or tabs, then four digits and a hyphen, which
  covers `### 2026-09-14`, `##2026-09-14`, `## 2026-9-14`, `## 2026-09-14 (late)` and a
  heading ending in CR, so a CRLF-saved changelog fails on every dated heading;
- a changelog with no dated heading fails rather than passing vacuously.

An out-of-order heading is reported against the dated heading directly above it, so one
misplaced date yields one finding. Two adjacent headings for one date are reported as a
repeat only; a repeat further down is also out of order, and both findings are printed.

WHY A SEPARATE GATE rather than more checks in tools/check_changelog_prs.py: that gate reads
the git history and fails on a shallow clone by design, and its self-test builds throwaway
repositories. This one reads one file, so it answers the same way in any checkout, and a
history error cannot hide a format finding, or the reverse.

WHAT IT DOES NOT CHECK: fenced code blocks are not modelled, so a dated heading line inside
one is checked as a heading; that over-flags rather than under-flags, and CHANGELOG.md had
no fenced block when this gate was added. It does not check the bullets under a heading,
their order, the older `###` subheadings, whether a date is the UTC date its changes landed
(the changelog's preamble says headings before 2026-09-27 were not held to one timezone),
or whether a date is in the future, which would need a clock this gate does not read.

Deterministic and offline: it reads CHANGELOG.md only. A missing or non-UTF-8 file is an
error, not a pass.
"""
import datetime
import re
import sys
from pathlib import Path

CHANGELOG = "CHANGELOG.md"

# The dated-heading shape `latest_change()` in tools/version_basis.py reads.
HEADING = re.compile(r"## ([0-9]{4}-[0-9]{2}-[0-9]{2})[ \t]*")

# A line that opens like a dated heading. One that is not exactly a HEADING is a finding,
# so a malformed date heading cannot escape the blank-line, order and repeat checks.
LOOKS_DATED = re.compile(r" {0,3}#+[ \t]*[0-9]{4}-")


def check(lines):
    """Every finding for the given lines, as (line number, message), and the dated headings."""
    findings = []
    headings = []
    first_line = {}
    previous = None
    for number, line in enumerate(lines, 1):
        match = HEADING.fullmatch(line)
        if not match:
            if LOOKS_DATED.match(line):
                findings.append((number, f"{line!r} opens like a dated heading but is not "
                                         "exactly `## YYYY-MM-DD`"))
            continue
        date = match.group(1)
        if number == len(lines):
            findings.append((number, f"`## {date}` is the last line; a blank line must follow it"))
        elif lines[number] != "":
            findings.append((number, f"`## {date}` is not followed by a blank line "
                                     f"(line {number + 1} is {lines[number][:60]!r})"))
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            findings.append((number, f"`## {date}` is not a calendar date"))
            continue
        headings.append(date)
        if date in first_line:
            findings.append((number, f"`## {date}` repeats the date of line {first_line[date]}; "
                                     "each date has one heading"))
        else:
            first_line[date] = number
        if previous is not None and date > previous[1]:
            findings.append((number, f"`## {date}` is newer than `## {previous[1]}` at line "
                                     f"{previous[0]}; dated headings must be strictly descending"))
        previous = (number, date)
    return findings, headings


def main(argv):
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    try:
        text = (root / CHANGELOG).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot check {CHANGELOG}: {exc}")
        return 2
    # Split on LF alone, and drop the empty string after a final LF, which is not a line.
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    findings, headings = check(lines)
    if not headings and not findings:
        findings.append((None, "no dated `## YYYY-MM-DD` heading was found"))
    if findings:
        for number, message in findings:
            location = f"{CHANGELOG}:{number}" if number else CHANGELOG
            print(f"  FAIL  {location}: {message}")
        return 1
    plural = "" if len(headings) == 1 else "s"
    print(f"  ok    {CHANGELOG}: {len(headings)} dated heading{plural} from {headings[0]} to "
          f"{headings[-1]}, each followed by a blank line, strictly descending, no date repeated")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
