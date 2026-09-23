#!/usr/bin/env python3
"""Cases for check_reasoned_rows.py, run against throwaway repositories.

Every case builds a temporary repository -- its own tools/, guides and backlog -- and
runs the real gate as a subprocess against it, so nothing here touches the real repo
files and the gate's own root resolution (`parents[1]` of the tool) is exercised end to
end rather than mocked.

The cases mirror the proposal:
  1. reasoned guide + a matching TODO "Demonstrate ... <guide>" row -> not a gap.
  2. reasoned guide + only a DONE.md demonstration row -> not a gap.
  3. reasoned guide + no row anywhere -> gap, and --strict exits 1.
  4. a guide that only DEMONSTRATES (never says "reasoned") + no row -> not a gap.
  5. a "reasoned" mention in a meta-file (CONTRIBUTING.md) -> ignored, not a guide.
  6. a reasoned gap listed in the baseline -> reported grandfathered, --strict exits 0.
  7. marker boundary: substrings ("unreasoned"/"reasonedness"/"reasoning"/"reasonable")
     are not the word, so a Verify section carrying only them is not detected.
  8. Markdown emphasis: `_reasoned_`/`__reasoned__` in a Verify section IS detected.
  9. scope: "reasoned" only in non-Verify prose (a demonstrated Verify) -> not a gap.
 10. complete-filename backlog match: `redis.md.bak`/`redis.mdx` do not clear the
     redis.md gap; a trailing-period `redis.md.` does.
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

    # 7. marker boundary: fixtures CONTAIN the substring "reasoned" yet are not the word.
    #    "unreasoned"/"reasonedness" (plus "reasoning"/"reasonable") in a Verify section
    #    must NOT be detected -- removing the boundary would wrongly match them.
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\n"
                               "This is unreasoned; its reasonedness and reasoning are "
                               "reasonable.\n"})
    check("7: substrings 'unreasoned'/'reasonedness'/'reasoning'/'reasonable' are not "
          f"the marker (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 8. Markdown emphasis: `_reasoned_`/`__reasoned__` in a Verify section IS detected.
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nThe check is _reasoned_ here.\n"})
    check("8a: a `_reasoned_` marker in a Verify section is a gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nThe check is __reasoned__ here.\n"})
    check("8b: a `__reasoned__` marker in a Verify section is a gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 9. scope: "reasoned" only in non-Verify prose -> not a gap. The intro reasons, but
    #    the Verify section is fully demonstrated (no "reasoned" marker inside it).
    rc, out = run({"redis.md": "# Redis\n\nThis intro is reasoned about at length.\n\n"
                               "## Verify\n\nRun the check and read the output.\n"})
    check("9: 'reasoned' only in non-Verify prose is not a gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 10. complete-filename backlog match (Fix C). A reasoned redis.md with a demonstrate
    #     row that names a DIFFERENT complete file (redis.md.bak / redis.mdx) is STILL a
    #     gap; a trailing-period "redis.md." clears it.
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate redis.md.bak\n")
    check("10a: 'Demonstrate redis.md.bak' does not clear the redis.md gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate redis.mdx\n")
    check("10b: 'Demonstrate redis.mdx' does not clear the redis.md gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate redis.md.\n")
    check("10c: a trailing-period 'Demonstrate redis.md.' clears the gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of 10 reasoned-row self-test cases failed")
        return 1
    print("PASS: 10 of 10 reasoned-row self-test cases passed (matching TODO/DONE "
          "demonstration rows clear the gap; an untracked reasoned guide is a gap and "
          "reddens --strict; a non-reasoned guide, a reasoned mention in a meta-file, "
          "and the substrings 'unreasoned'/'reasonedness'/'reasoning'/'reasonable' are "
          "not gaps; `_reasoned_`/`__reasoned__` emphasis IS detected; 'reasoned' only "
          "in non-Verify prose is not a gap; a suffix-continuation backlog token "
          "(redis.md.bak / redis.mdx) does not clear the redis.md gap while a "
          "trailing-period 'redis.md.' does; a baselined gap is grandfathered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
