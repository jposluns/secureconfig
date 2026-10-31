#!/usr/bin/env python3
"""Exercise recorded TODO.md row cases through the shipped gate on throwaway trees.

Each failing fixture has a passing twin that differs only in the defect, so a case fails
when its check is removed rather than passing for another reason. The joined-row cases use
the shape #71 committed. The last cases record what the gate does NOT model, so this file
cannot quietly start claiming it.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

OK = "  ok    TODO.md: "

# Lines 1 to 6: a title, a band heading and a banded table's header.
HEAD = ("# TODO\n\n## Priority 2: Deepen existing guides\n\n"
        "| ID | Item | Tags |\n| --- | --- | --- |\n")
ROW_A = "| 1.13 | `devops-uis.md`: add a GitLab CE section (M, S) [2 families] | `[enhance]` |"
ROW_B = "| 1.19 | `web-exposure.md`: directory listing is never covered (M, XS) | `[enhance]` |"
ROW_C = "| 1.20 | `ruby.md`: Sidekiq Web is mounted with no constraint (M, XS) | `[enhance]` |"


def todo(*lines):
    return HEAD + "".join(line + "\n" for line in lines)


def case(text, expected=0, needle=OK, *, also=(), absent=(), missing=False):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        if not missing:
            data = text if isinstance(text, bytes) else text.encode("utf-8")
            (root / "TODO.md").write_bytes(data)
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(TOOLS / "check_todo_rows.py"), str(root)],
            capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        assert result.returncode == expected, (result.returncode, expected, output)
        for item in (needle, *also):
            assert item in output, (item, output)
        for item in absent:
            assert item not in output, (item, output)
        if expected == 0:
            assert "  FAIL  " not in output, output
        return 1


def main():
    count = 0
    try:
        # Clean: one row per line, and the twin of every joined case below.
        count += case(todo(ROW_A, ROW_B),
                      needle=OK + "2 backlog rows, no line holding more than one row start")

        # The #71 shape: the second row's opening pipe follows the first row's closing pipe.
        count += case(todo(ROW_A + ROW_B, ROW_C), expected=1,
                      needle="  FAIL  TODO.md:7: this line holds 2 backlog row starts "
                             "(1.13, 1.19); each row needs its own line",
                      absent=("TODO.md:8:",))
        # One pipe shared by the end of one row and the start of the next.
        count += case(todo(ROW_A + ROW_B[1:]), expected=1,
                      needle="TODO.md:7: this line holds 2 backlog row starts (1.13, 1.19)")
        # A space between the two rows.
        count += case(todo(ROW_A + " " + ROW_B), expected=1,
                      needle="TODO.md:7: this line holds 2 backlog row starts (1.13, 1.19)")
        # Three rows on one line are one finding naming all three.
        count += case(todo(ROW_A + ROW_B + ROW_C), expected=1,
                      needle="TODO.md:7: this line holds 3 backlog row starts "
                             "(1.13, 1.19, 1.20)")
        # Every joined line is reported.
        count += case(todo(ROW_A + ROW_B, ROW_C, ROW_C + ROW_A), expected=1,
                      needle="TODO.md:7: this line holds 2", also=("TODO.md:9: this line holds 2",),
                      absent=("TODO.md:8:",))
        count += case(todo(ROW_A, ROW_B, ROW_C),
                      needle=OK + "3 backlog rows, no line holding more than one row start")

        # Ids named in an item's prose are not row starts, nor is the Blocked upstream shape.
        count += case(todo("| 3.50 | Extend the gate of row 3.6 and DONE 1.320 to DONE.md "
                           "(L, S) | `[gap]` |",
                           "| 3.6 | Activate the AIQT hooks (L, S) | the guardrails "
                           "versioning work |"),
                      needle=OK + "2 backlog rows")
        # A table with no rows yet still passes.
        count += case(todo(), needle=OK + "0 backlog rows")

        # Fail closed: no table header, a missing file, and a file that is not UTF-8.
        count += case("# TODO\n\nNothing tabled.\n", expected=1,
                      needle="  FAIL  TODO.md: no `| ID |` table header was found")
        count += case(None, expected=2, needle="  FAIL  cannot check TODO.md:", missing=True)
        count += case(todo(ROW_A).encode("utf-8") + b"\xff\n", expected=2,
                      needle="  FAIL  cannot check TODO.md: 'utf-8' codec can't decode")

        # Known limit: a row start inside a code span counts, which over-flags.
        count += case(todo("| 3.50 | Quote `| 1.2 |` in a table (L, XS) | `[gap]` |"),
                      expected=1,
                      needle="TODO.md:7: this line holds 2 backlog row starts (3.50, 1.2)")
        # Known limit: a row joined onto a line that is not a row leaves one row start there,
        # and it passes.
        count += case(todo("Next ids: **1.389**." + ROW_A),
                      needle=OK + "0 backlog rows")
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  TODO-row gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the TODO-row gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
