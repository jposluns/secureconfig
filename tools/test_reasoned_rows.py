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
 11. fence-aware parsing: a fenced `# comment` in a Verify section does not end it, so a
     later reasoned marker is still detected.
 12. fence-aware parsing: a fenced `## Verify` example (under Setup) does not open a
     Verify section, so a reasoned marker inside it is not detected.
 13. both-sided filename boundary: hiredis.md/not-redis.md/redis.md_backup/redis.md-old
     do not clear the redis.md gap; a backticked `redis.md` and a trailing-comma
     `redis.md,` do.
 14. the Verify heading's own title is scanned: `## Verify (reasoned)` is detected even
     when the body carries no marker.
 15. ATX heading parsing (CommonMark): a Verify heading indented up to 3 spaces still
     opens a section, and an empty `##` heading closes one.
 16. fence tightening (via _markdown.Fences): a 4+-space-indented ``` and a backtick
     fence carrying a backtick in its info string do NOT open a fence that hides a later
     Verify section.
 17. right filename boundary: a dot-run continuation (redis.md..bak / redis.md._backup /
     redis.md.-old) does not clear the redis.md gap.
 18. Markdown line endings only: a U+2028/U+2029 inside a Verify paragraph does not fake a
     heading that ends the section; a CRLF guide parses normally; a U+2028 inside a backlog
     row does not split the row.
 19. allowlisted filename edges: a basename touching `+`, `~`, a non-ASCII letter, or an
     embedded or unbalanced underscore does not clear the redis.md gap.
 20. emphasis and link forms (`_redis.md_`, `__redis.md__`, `**redis.md**`,
     `[redis.md](redis.md)`, `redis.md#verify`, `(redis.md)`) DO clear the gap.
 21. closing fence (shared _markdown.Fences): a ``` followed by a non-breaking space does
     not close the block; one followed by spaces and a tab does.
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
        shutil.copy(TOOL.parent / "_markdown.py", d / "tools" / "_markdown.py")
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
    #    The fixture gives CONTRIBUTING.md a real Verify section CONTAINING the marker and
    #    no backlog row, so the ONLY reason it is not a gap is the meta exclusion:
    #    replacing that exclusion with `if True:` would make this case fail (non-vacuous).
    rc, out = run({"CONTRIBUTING.md": "# Contributing\n\n## Verify\n\n"
                                      "This check is reasoned rather than run.\n"})
    check("5: a reasoned Verify in an excluded meta-file is not a guide "
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

    # 11. Fix E, fence-aware heading parsing. A Verify section whose fenced code block
    #     contains a `# comment` line (a level-1 ATX heading if fences were ignored)
    #     followed by a later reasoned marker STILL detects the marker: the fenced `#`
    #     must not prematurely end the section.
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\n"
                               "```sh\n# run this check\necho hi\n```\n\n"
                               "The output above is reasoned about rather than asserted.\n"})
    check("11: a fenced `#` in a Verify section does not end it; a later reasoned marker "
          f"is still a gap (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 12. Fix E, the other direction. A `## Verify` that appears only INSIDE a fenced
    #     code block (an example under a Setup section) does NOT open a Verify section,
    #     so a reasoned marker within that fenced example is not detected: not a gap.
    rc, out = run({"redis.md": "# Redis\n\n## Setup\n\n"
                               "```md\n## Verify\n\nThis is reasoned, not run.\n```\n\n"
                               "Run the setup steps.\n"})
    check("12: a fenced `## Verify` example does not open a Verify section "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 13. Fix F, both-sided complete-filename boundary. A demonstrate row naming a
    #     DIFFERENT complete file that merely embeds "redis.md" as a substring on either
    #     side must NOT clear the redis.md gap; a leading backtick and a trailing comma
    #     around the real basename DO clear it.
    for bad in ("hiredis.md", "not-redis.md", "redis.md_backup", "redis.md-old"):
        rc, out = run({"redis.md": REASONED_GUIDE},
                      todo=f"- [ ] 1.1 Demonstrate {bad}\n")
        check(f"13-neg: 'Demonstrate {bad}' does not clear the redis.md gap "
              f"(rc={rc}, out={out!r})",
              rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
              and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate the reasoned Verify in `redis.md`\n")
    check("13-pos-backtick: a backticked `redis.md` clears the gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate redis.md, then move on\n")
    check("13-pos-comma: a trailing-comma 'redis.md,' clears the gap "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 14. Fix G, the Verify heading's own title is scanned. A `## Verify (reasoned)`
    #     heading whose body carries neither the marker nor a row is a gap on the
    #     strength of the marker in the heading title alone.
    rc, out = run({"redis.md": "# Redis\n\n## Verify (reasoned)\n\n"
                               "Run the check and read the output.\n"})
    check("14: a marker in the Verify heading title (`## Verify (reasoned)`) is detected "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 15. ATX heading parsing (CommonMark). 15a: a Verify heading indented up to 3 spaces
    #     still opens a section, so a reasoned marker under it is detected. 15b: an empty
    #     `##` heading (same level) closes the Verify section, so a later reasoned marker
    #     in the appendix that follows is outside Verify and is not a gap.
    rc, out = run({"redis.md": "# Redis\n\n   ## Verify\n\n"
                               "This check is reasoned rather than run.\n"})
    check("15a: a Verify heading indented 3 spaces opens a Verify section "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nRun the check and read the "
                               "output.\n\n##\n\nThis appendix is reasoned about.\n"})
    check("15b: an empty `##` heading closes the Verify section, so a later reasoned "
          f"marker is outside it (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 16. Fence tightening via _markdown.Fences. 16a: a fence indented 4+ spaces is NOT an
    #     opening fence, so a `## Verify` heading after it is not swallowed and its
    #     reasoned marker is detected. 16b: a backtick fence whose info string contains a
    #     backtick is NOT an opening fence, so a following `## Verify` is still recognized.
    rc, out = run({"redis.md": "# Redis\n\n## Setup\n\n    ```\n\n## Verify\n\n"
                               "This check is reasoned rather than run.\n"})
    check("16a: a 4-space-indented ``` does not open a fence hiding a later Verify "
          f"section (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": "# Redis\n\n## Setup\n\n```example with a `backtick`\n\n"
                               "## Verify\n\nThis check is reasoned rather than run.\n"})
    check("16b: a backtick fence with a backtick in its info string does not open a "
          f"fence hiding a later Verify section (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 17. Right filename boundary rejects dot-run continuations. A demonstrate row naming
    #     a dot-run continuation of the basename must NOT clear the redis.md gap.
    for bad in ("redis.md..bak", "redis.md._backup", "redis.md.-old"):
        rc, out = run({"redis.md": REASONED_GUIDE},
                      todo=f"- [ ] 1.1 Demonstrate {bad}\n")
        check(f"17: 'Demonstrate {bad}' does not clear the redis.md gap "
              f"(rc={rc}, out={out!r})",
              rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
              and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 18. Markdown line endings only. 18a/18b: a U+2028 or U+2029 inside the Verify
    #     paragraph is NOT a line break, so the "## Notes" text after it is not a heading
    #     that closes the section early, and the later reasoned marker is still inside
    #     Verify (splitlines() would have hidden it). 18c: a CRLF guide parses as ordinary
    #     lines. 18d: a U+2028 inside a backlog row does not split "Demonstrate" from the
    #     basename, so the row still clears the gap.
    for sep, label in (("\u2028", "18a-U+2028"), ("\u2029", "18b-U+2029")):
        rc, out = run({"redis.md": "# Redis\n\n## Verify\n\nRun the check." + sep
                                   + "## Notes\n\nThis check is reasoned rather than run.\n"})
        check(f"{label}: a separator inside a paragraph does not fake a heading that ends "
              f"the Verify section (rc={rc}, out={out!r})",
              rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
              and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": "# Redis\r\n\r\n## Verify\r\n\r\n"
                               "This check is reasoned rather than run.\r\n"})
    check(f"18c: a CRLF guide parses as ordinary lines (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)
    rc, out = run({"redis.md": REASONED_GUIDE},
                  todo="- [ ] 1.1 Demonstrate\u2028redis.md\n")
    check(f"18d: a U+2028 inside a backlog row does not split the row (rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 19. Allowlisted filename edges. A basename touching `+`, `~`, a non-ASCII letter, or
    #     an embedded or unbalanced underscore is part of a longer token naming a
    #     different file, so it does NOT clear the redis.md gap.
    for bad in ("archive+redis.md", "redis.md~", "\u00e9redis.md", "redis.md\u00e9",
                "my_redis.md", "_redis.md", "_redis.md_backup"):
        rc, out = run({"redis.md": REASONED_GUIDE},
                      todo=f"- [ ] 1.1 Demonstrate {bad}\n")
        check(f"19: 'Demonstrate {bad}' does not clear the redis.md gap "
              f"(rc={rc}, out={out!r})",
              rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
              and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    # 20. Emphasis and link forms around the real basename DO clear the gap.
    for good in ("_redis.md_", "__redis.md__", "**redis.md**", "[redis.md](redis.md)",
                 "redis.md#verify", "(redis.md)"):
        rc, out = run({"redis.md": REASONED_GUIDE},
                      todo=f"- [ ] 1.1 Demonstrate {good}\n")
        check(f"20: 'Demonstrate {good}' clears the redis.md gap (rc={rc}, out={out!r})",
              rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)

    # 21. Closing fence (shared _markdown.Fences). 21a: only spaces or tabs may follow a
    #     closing run, so a ``` followed by a non-breaking space is fence CONTENT, not a
    #     close; the `## Verify` after it stays inside the still-open block, so it is not a
    #     gap. 21b: a ``` followed by spaces and a tab DOES close, so the Verify section
    #     after it is parsed and its reasoned marker is a gap.
    rc, out = run({"redis.md": "# Redis\n\n## Setup\n\n```sh\necho hi\n```\u00a0\n\n"
                               "## Verify\n\nThis check is reasoned rather than run.\n"})
    check("21a: a closing fence followed by a non-breaking space does not close the block "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW" not in out and "0 reasoned guide" in out)
    rc, out = run({"redis.md": "# Redis\n\n## Setup\n\n```sh\necho hi\n```  \t\n\n"
                               "## Verify\n\nThis check is reasoned rather than run.\n"})
    check("21b: a closing fence followed by spaces and a tab closes the block "
          f"(rc={rc}, out={out!r})",
          rc == 0 and "REASONED-ROW: redis.md has a reasoned Verify step" in out
          and "1 reasoned guide(s) without a demonstration row (1 new" in out)

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of 21 reasoned-row self-test cases failed")
        return 1
    print("PASS: 21 of 21 reasoned-row self-test cases passed (matching TODO/DONE "
          "demonstration rows clear the gap; an untracked reasoned guide is a gap and "
          "reddens --strict; a non-reasoned guide, a reasoned Verify in a meta-file, "
          "and the substrings 'unreasoned'/'reasonedness'/'reasoning'/'reasonable' are "
          "not gaps; `_reasoned_`/`__reasoned__` emphasis IS detected; 'reasoned' only "
          "in non-Verify prose is not a gap; a suffix-continuation backlog token "
          "(redis.md.bak / redis.mdx) does not clear the redis.md gap while a "
          "trailing-period 'redis.md.' does; a baselined gap is grandfathered; a fenced "
          "`#` does not end a Verify section and a fenced `## Verify` does not open one; "
          "a both-sided filename boundary rejects hiredis.md/not-redis.md/redis.md_backup"
          "/redis.md-old; a marker in the Verify heading title is detected; an ATX "
          "heading indented up to 3 spaces or with an empty title is parsed correctly; a "
          "4-space-indented or backtick-info fence does not hide a Verify section; a "
          "dot-run filename continuation does not clear the gap; a Unicode line separator "
          "neither fakes a heading nor splits a backlog row; a basename beside +, ~, a "
          "non-ASCII letter or a stray underscore does not clear the gap while balanced "
          "emphasis and link forms do; and a non-breaking space after a closing fence "
          "does not close it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
