#!/usr/bin/env python3
"""Check that no line of TODO.md holds more than one backlog table row.

WHAT THIS CATCHES: finding F-TODO-ROW-CONCATENATION. Each row of a banded table in TODO.md
starts with its id cell, such as `| 3.6 |`, and is one physical line. When the line break
between two rows is lost, the second row's id cell lands on the first row's line, and
Markdown renders both as one row whose last cell carries the whole second row. Pull request
#71 (commit 4396e7cc) committed exactly that: the line for row 1.13 ended with its Tags cell
and then `|| 1.19 |` and the whole of row 1.19, until #72 deleted the joined tail when it
closed row 1.19.

WHAT IT CHECKS, reading TODO.md as LF-separated lines:

- a row start is a pipe, optional spaces or tabs, an id (digits, a dot, digits), optional
  spaces or tabs, and a pipe. Starts are counted overlapping, so a pipe that both ends one
  row and opens the next counts for both;
- a line holding two or more row starts is a finding, reported once with every id it holds;
- the file must hold at least one `| ID |` table header, so a reformatted file fails closed
  rather than passing with no table read.

WHAT IT DOES NOT CHECK: Markdown structure is not modelled. A row start inside a code span or
a fenced block, or one after an escaped pipe, counts, which over-flags; no line of TODO.md
did that when this gate was added. A row joined onto a line that is not a row, such as prose,
a heading or a table header, leaves one row start on that line and passes. It does not check
DONE.md, id series, id uniqueness, the Next ids line or the (severity, effort) pair.

Deterministic and offline: it reads TODO.md only. A missing or non-UTF-8 file is an error,
not a pass.
"""
import re
import sys
from pathlib import Path

TODO = "TODO.md"

# A row start, matched inside a lookahead so that overlapping starts are all found.
ROW_START = re.compile(r"(?=\|[ \t]*([0-9]+\.[0-9]+)[ \t]*\|)")
# A line that opens with a row start: one backlog row.
ROW_LINE = re.compile(r" {0,3}\|[ \t]*[0-9]+\.[0-9]+[ \t]*\|")
# A banded table's header row.
HEADER = re.compile(r" {0,3}\|[ \t]*ID[ \t]*\|")


def check(lines):
    """Every finding as (line number, message), the number of row lines, and header count."""
    findings = []
    rows = 0
    headers = 0
    for number, line in enumerate(lines, 1):
        if HEADER.match(line):
            headers += 1
        if ROW_LINE.match(line):
            rows += 1
        ids = ROW_START.findall(line)
        if len(ids) > 1:
            findings.append((number, f"this line holds {len(ids)} backlog row starts "
                                     f"({', '.join(ids)}); each row needs its own line"))
    return findings, rows, headers


def report(text):
    """Print the gate's result for the text of TODO.md and return its exit status."""
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    findings, rows, headers = check(lines)
    if not headers:
        findings.append((None, "no `| ID |` table header was found, so no backlog table "
                               "was read"))
    if findings:
        for number, message in findings:
            location = f"{TODO}:{number}" if number else TODO
            print(f"  FAIL  {location}: {message}")
        return 1
    plural = "" if rows == 1 else "s"
    print(f"  ok    {TODO}: {rows} backlog row{plural}, no line holding more than one row start")
    return 0


def main(argv):
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    try:
        text = (root / TODO).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot check {TODO}: {exc}")
        return 2
    return report(text)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
