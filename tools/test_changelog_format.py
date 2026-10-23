#!/usr/bin/env python3
"""Exercise recorded CHANGELOG format cases through the shipped gate on throwaway trees.

Each rule has a failing fixture and a passing twin that differs only in the defect, so a
case fails when its check is removed rather than passing for another reason. The last case
records what the gate does NOT model, so this file cannot quietly start claiming it.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

OK = "  ok    CHANGELOG.md: "


def log(*sections):
    """A changelog: the title and a preamble on lines 1 to 4, then each section as given."""
    return "# Changelog\n\nPreamble.\n\n" + "".join(sections)


def day(date, bullet="- A change (#1)\n"):
    """One well-formed dated section of four lines: heading, blank line, bullet, blank line."""
    return f"## {date}\n\n{bullet}\n"


def case(changelog, expected=0, needle=OK, *, also=(), absent=(), missing=False):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        if not missing:
            if isinstance(changelog, bytes):
                (root / "CHANGELOG.md").write_bytes(changelog)
            else:
                (root / "CHANGELOG.md").write_bytes(changelog.encode("utf-8"))
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(TOOLS / "check_changelog_format.py"), str(root)],
            capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        assert result.returncode == expected, (result.returncode, expected, output)
        for text in (needle, *also):
            assert text in output, (text, output)
        for text in absent:
            assert text not in output, (text, output)
        if expected == 0:
            assert "  FAIL  " not in output, output
        return 1


def main():
    count = 0
    try:
        # Clean: dated sections newest first, each heading followed by a blank line,
        # including an older section that opens with a `###` subheading.
        count += case(log(day("2026-10-23"), day("2026-10-22"),
                          "## 2026-09-13\n\n### Added\n\n- A change (#1)\n"),
                      needle=OK + "3 dated headings from 2026-10-23 to 2026-09-13, each "
                                  "followed by a blank line, strictly descending, no date repeated")

        # Rule 1, a blank line after each dated heading: the row 3.45 defect, a bullet
        # directly under the heading, and its normalized twin.
        count += case(log(day("2026-10-23"), "## 2026-09-19\n- A change (#1)\n"), expected=1,
                      needle="  FAIL  CHANGELOG.md:9: `## 2026-09-19` is not followed by a "
                             "blank line (line 10 is '- A change (#1)')",
                      absent=("strictly descending", "repeats"))
        count += case(log(day("2026-10-23"), "## 2026-09-19\n\n- A change (#1)\n"))
        # A line holding only spaces or tabs is not an empty line.
        count += case(log("## 2026-09-19\n \n- A change (#1)\n"), expected=1,
                      needle="CHANGELOG.md:5: `## 2026-09-19` is not followed by a blank line "
                             "(line 6 is ' ')")
        count += case(log("## 2026-09-19\n\t\n- A change (#1)\n"), expected=1,
                      needle="(line 6 is '\\t')")
        # A dated heading on the last line, with or without a final LF, has no blank line after it.
        count += case(log(day("2026-10-23"), "## 2026-09-19\n"), expected=1,
                      needle="CHANGELOG.md:9: `## 2026-09-19` is the last line; a blank line "
                             "must follow it")
        count += case(log(day("2026-10-23"), "## 2026-09-19"), expected=1,
                      needle="CHANGELOG.md:9: `## 2026-09-19` is the last line")
        # Every violation is listed, one line each, as the six row 3.45 headings would be.
        count += case(log("## 2026-09-15\n- A (#1)\n", "## 2026-09-14\n- B (#2)\n"), expected=1,
                      needle="CHANGELOG.md:5: `## 2026-09-15` is not followed by a blank line",
                      also=("CHANGELOG.md:7: `## 2026-09-14` is not followed by a blank line",))

        # Rule 2, strictly descending: an older date above a newer one fails, reported
        # against the heading directly above, and the same two dates in order pass.
        count += case(log(day("2026-09-13"), day("2026-09-14")), expected=1,
                      needle="  FAIL  CHANGELOG.md:9: `## 2026-09-14` is newer than "
                             "`## 2026-09-13` at line 5; dated headings must be strictly "
                             "descending",
                      absent=("repeats", "not followed"))
        count += case(log(day("2026-09-14"), day("2026-09-13")))
        # One misplaced date gives one finding: the comparison is with the heading above.
        count += case(log(day("2026-10-23"), day("2026-10-20"), day("2026-10-22"),
                          day("2026-10-21")), expected=1,
                      needle="CHANGELOG.md:13: `## 2026-10-22` is newer than `## 2026-10-20` "
                             "at line 9",
                      absent=("CHANGELOG.md:17:",))
        # Dates compare as dates across a year boundary, and trailing spaces or tabs keep a
        # line a dated heading, as `latest_change()` reads it, so it is still ordered.
        count += case(log(day("2027-01-01"), day("2026-12-31")))
        count += case(log("## 2026-09-14 \t\n\n- A (#1)\n\n", day("2026-09-15")), expected=1,
                      needle="CHANGELOG.md:9: `## 2026-09-15` is newer than `## 2026-09-14` "
                             "at line 5")

        # Rule 3, one heading per date: an adjacent repeat is reported once, as a repeat,
        # and its twin with distinct dates passes.
        count += case(log(day("2026-09-14"), day("2026-09-14")), expected=1,
                      needle="  FAIL  CHANGELOG.md:9: `## 2026-09-14` repeats the date of "
                             "line 5; each date has one heading",
                      absent=("strictly descending",))
        count += case(log(day("2026-09-15"), day("2026-09-14")))
        # A repeat further down is also out of order, and both findings are printed.
        count += case(log(day("2026-10-23"), day("2026-10-22"), day("2026-10-23")), expected=1,
                      needle="CHANGELOG.md:13: `## 2026-10-23` repeats the date of line 5",
                      also=("CHANGELOG.md:13: `## 2026-10-23` is newer than `## 2026-10-22` "
                            "at line 9",))

        # A dated heading must name a calendar date.
        count += case(log(day("2026-02-30")), expected=1,
                      needle="CHANGELOG.md:5: `## 2026-02-30` is not a calendar date")
        count += case(log(day("2026-13-01")), expected=1,
                      needle="`## 2026-13-01` is not a calendar date")

        # A line that opens like a dated heading but is not exactly one fails, so a
        # malformed heading cannot drop out of the three rules.
        for line in ("### 2026-09-14", "# 2026-09-14", "##2026-09-14", "## 2026-9-14",
                     "## 2026-09-14 (late)", "## 2026-09-14\r", "   ## 2026-09-14",
                     "##\t2026-09-14"):
            count += case(log(day("2026-10-23"), line + "\n\n- A (#1)\n"), expected=1,
                          needle=f"CHANGELOG.md:9: {line!r} opens like a dated heading but "
                                 "is not exactly `## YYYY-MM-DD`")
        # Headings that do not open with a date are not dated headings and are not checked.
        count += case(log("## Unreleased\n- pending\n", day("2026-09-14"),
                          "### Added\n- A (#1)\n"),
                      needle=OK + "1 dated heading from 2026-09-14 to 2026-09-14")
        # A changelog saved with CRLF endings fails on every dated heading rather than
        # passing with its headings unread.
        count += case(log(day("2026-10-23"), day("2026-10-22")).replace("\n", "\r\n"),
                      expected=1,
                      needle="CHANGELOG.md:5: '## 2026-10-23\\r' opens like a dated heading",
                      also=("CHANGELOG.md:9: '## 2026-10-22\\r' opens like a dated heading",))

        # Fail closed: no dated heading, an empty file, a missing file, or one not UTF-8.
        count += case("# Changelog\n\n- nothing dated\n", expected=1,
                      needle="  FAIL  CHANGELOG.md: no dated `## YYYY-MM-DD` heading was found")
        count += case("", expected=1, needle="no dated `## YYYY-MM-DD` heading was found")
        count += case(None, expected=2, needle="  FAIL  cannot check CHANGELOG.md:",
                      missing=True)
        count += case(log(day("2026-09-14")).encode("utf-8") + b"\xff\n", expected=2,
                      needle="  FAIL  cannot check CHANGELOG.md: 'utf-8' codec can't decode")

        # Known limit, recorded so this file cannot quietly claim otherwise: fenced blocks
        # are not modelled, so a dated heading line inside one is checked as a heading.
        # This over-flags rather than under-flags.
        count += case(log(day("2026-10-23"), "```text\n## 2026-10-24\n```\n\n",
                          day("2026-10-22")), expected=1,
                      needle="CHANGELOG.md:10: `## 2026-10-24` is not followed by a blank line",
                      also=("CHANGELOG.md:10: `## 2026-10-24` is newer than `## 2026-10-23` "
                            "at line 5",))
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  changelog-format gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the changelog-format gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
