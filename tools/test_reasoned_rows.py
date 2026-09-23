#!/usr/bin/env python3
"""Cases for check_reasoned_rows.py, run against throwaway repositories.

Every case builds a temporary repository -- its own tools/, guides and backlog -- and
runs the real gate as a subprocess against it, so nothing here touches the real repo
files and the gate's own root resolution (`parents[1]` of the tool) is exercised end to
end rather than mocked.

The seven cases mirror the proposal:
  1. reasoned guide + a matching TODO "Demonstrate ... <guide>" row -> not a gap.
  2. reasoned guide + only a DONE.md demonstration row -> not a gap.
  3. reasoned guide + no row anywhere -> gap, and --strict exits 1.
  4. a guide that only DEMONSTRATES (never says "reasoned") + no row -> not a gap.
  5. a "reasoned" mention in a meta-file (CONTRIBUTING.md) -> ignored, not a guide.
  6. a reasoned gap listed in the baseline -> reported grandfathered, --strict exits 0.
  7. word boundary: "reasoning"/"reasonable" but not "reasoned" -> not detected.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "check_reasoned_rows.py"


def run(files, todo="", done="", baseline=None, flags=()):
    """Build a throwaway repo from the given files and run the real gate. (exit, output).

    `files` maps a root-level filename to its text (guides plus any meta files). `todo`
    and `done` are the backlog bodies (omit a key by leaving it empty -- an empty string
    still writes the file, which the missing-file robustness is covered separately). A
    non-None `baseline` writes tools/reasoned_row_baseline.txt.
    """
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        shutil.copy(TOOL, d / "tools" / "check_reasoned_rows.py")
        for name, body in files.items():
            (d / name).write_text(body, encoding="utf-8")
        (d / "TODO.md").write_text(todo, encoding="utf-8")
        (d / "DONE.md").write_text(done, encoding="utf-8")
        if baseline is not None:
            (d / "tools" / "reasoned_row_baseline.txt").write_text(baseline, encoding="utf-8")
        r = subprocess.run([sys.executable, "tools/check_reasoned_rows.py", *flags],
                           cwd=d, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


REASONED_GUIDE = "# Redis\n\n## Verify\n\nThis check is reasoned rather than run.\n"
PLAIN_GUIDE = "# Redis\n\n## Verify\n\nRun the check and read the output.\n"


def main() -> int:
    failures = []

    def check(desc, cond):
        if not cond:
            failures.append(desc)

    # 1. reasoned guide + a matching TODO "Demonstrate ... <guide>" row -> not a gap.
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate the reasoned Verify in redis.md\n")
    check("1: matching TODO demonstrate row should clear the gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 2. reasoned guide + only a DONE.md demonstration row -> not a gap.
    rc, out = run({"redis.md": REASONED_GUIDE},
                  done="- [x] 1.1 Demonstration recorded for redis.md\n")
    check("2: a DONE.md demonstration row should clear the gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 3. reasoned guide + no row anywhere -> gap; and --strict exits 1.
    rc, out = run({"redis.md": REASONED_GUIDE})
    check("3a: an untracked reasoned guide is a gap in advisory mode "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": REASONED_GUIDE}, flags=("--strict",))
    check("3b: --strict exits 1 on a new untracked reasoned guide "
          f"(rc={rc}, out={out!r})",
          rc == 1 and "FAIL" in out and "REASONED-ROW: redis.md" in out)

    # 4. a guide that only DEMONSTRATES (never says "reasoned") + no row -> not a gap.
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nThis step is demonstrated live.\n"})
    check("4: a guide with no reasoned step is not a gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 5. a "reasoned" mention in a meta-file (CONTRIBUTING.md) -> ignored, not a guide.
    rc, out = run({"CONTRIBUTING.md": "A Verify step may be reasoned rather than run.\n"})
    check("5: a reasoned mention in an excluded meta-file is not a guide "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 6. a reasoned gap listed in the baseline -> grandfathered; --strict exits 0.
    rc, out = run({"redis.md": REASONED_GUIDE}, baseline="redis.md\n")
    check("6a: a baselined gap is reported grandfathered in advisory mode "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW (baseline, grandfathered): redis.md" in out
          and "REASONED-ROW: redis.md" not in out
          and "1 reasoned guide(s) without a demonstration row (0 new, 1 grandfathered)" in out)
    rc, out = run({"redis.md": REASONED_GUIDE}, baseline="# comment\nredis.md\n",
                  flags=("--strict",))
    check("6b: --strict exits 0 when the only gap is grandfathered "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "PASS" in out
          and "REASONED-ROW (baseline, grandfathered): redis.md" in out)

    # 7. word boundary: "reasoning"/"reasonable" but not "reasoned" -> not detected.
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nApply reasoning; it is reasonable.\n"})
    check("7: 'reasoning'/'reasonable' without 'reasoned' is not detected "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of 7 reasoned-row self-test cases failed")
        return 1
    print("PASS: 7 of 7 reasoned-row self-test cases passed (matching TODO/DONE "
          "demonstration rows clear the gap; an untracked reasoned guide is a gap and "
          "reddens --strict; a non-reasoned guide, a reasoned mention in a meta-file, "
          "and 'reasoning'/'reasonable' are not gaps; a baselined gap is grandfathered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
