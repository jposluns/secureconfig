#!/usr/bin/env python3
"""Hold the line on guides whose Verify step reasons but that no backlog row demonstrates.

CONTRIBUTING's rule 5 lets a guide's Verify step REASON about why a check is correct
instead of only running a command, and a reasoned Verify is exactly the case a human
should still watch a demonstration of, because the reasoning -- not an executed
command -- is doing the load-bearing work. This gate catches a guide that carries a
reasoned Verify step but that no DEMONSTRATION backlog row (in TODO.md or DONE.md)
tracks, so the intent to actually demonstrate it does not silently fall off the plan.

This is the reasoned-row gate. It is ADVISORY-first: the default mode prints every gap
and always exits 0, so it can never turn the offline suite red while the ratchet is
being seeded. `--strict` is the shape a future, Architect-gated blocking wire would
use; it is not wired into tools/run_all_checks.sh here.

WHAT COUNTS AS A GUIDE. Every top-level `*.md` in the repository root, scanned
non-recursively, EXCEPT the meta-file exclude set (CONTRIBUTING.md, SECURITY.md,
CLAUDE.md, AGENTS.md, CHANGELOG.md, README.sources.md, TODO.md, DONE.md, DECISIONS.md,
PENDING-DECISIONS.md, controls-reference.md), which mirrors run_all_checks.sh's
not_a_guide(). README.md is NOT excluded: it is held to the guide contract. The
exclusion is what removes the definitional uses of "reasoned" -- CONTRIBUTING and
DECISIONS describe the rule-5 marker itself -- so that in the guides that remain the
word appears only as the Verify marker.

THE REASONED DETECTOR AND ITS KNOWN BLIND SPOT. A guide "has a reasoned Verify step"
iff the word "reasoned" (case-insensitive) appears INSIDE a Verify section of the guide.
The word boundary excludes only ASCII letters and digits, so Markdown emphasis around
the word still matches -- `_reasoned_`, `__reasoned__`, `**REASONED**`, `(reasoned)`,
`REASONED:` all count -- while a longer word does not: `unreasoned`, `reasonedness`,
`reasoning`, `reasonable` are NOT the marker. A Verify section begins at any ATX heading
whose title matches the word "verify" and runs to the next heading of the same or a
shallower level (or end of file), so it captures a `## Verify` section with its `###`
subsections and each per-tool `### Verify` subsection in a catalogue guide. Text outside
every Verify section is ignored, so the word used in an intro or rationale does not
trip the gate. It does not catch a guide that reasons in its Verify step without ever
writing the word "reasoned": the gate's guarantee is only over the corpus's own
convention, where the word IS the marker; it is a tracking aid, not an adversarial
classifier, and a guide that reasons under another phrasing is out of scope by design.

THE DEMONSTRATION-ROW DETECTOR. A guide is "tracked" iff at least one line in TODO.md
OR DONE.md carries the case-insensitive word "demonstrate" or "demonstration" AND names
the guide's basename as a COMPLETE filename token (for example `redis.md`), where the
match is not followed by another filename character -- so `redis.md` matches
`Demonstrate redis.md` or a trailing-period `redis.md.` but not `redis.md.bak` or
`redis.mdx`. A creation-or-deepen row that names the guide but does not say
"demonstrate" does not count: the point is a row that commits to demonstrating the
reasoned step, not merely one that mentions the file.

THE BASELINE RATCHET. An optional `tools/reasoned_row_baseline.txt` (one guide basename
per line; blank lines and `#` comments ignored) grandfathers known pre-existing gaps:
a listed guide is still reported, flagged `(baseline, grandfathered)`, but does not
cause a non-zero `--strict` exit. This mirrors check_pinned_citations.py's ratchet. An
absent baseline file is treated as empty, so the ratchet starts unseeded and seeding it
is a deliberate `--write-baseline` step a human takes once.

Everything is offline and reads files as UTF-8. Nothing is written except under
`--write-baseline`.
"""
import argparse
import re
import sys
from pathlib import Path

# Root-level Markdown that is not a guide: the adapters, the changelogs, the backlog,
# and the contributor/decision records whose prose defines the "reasoned" marker. This
# set mirrors the canonical not_a_guide() case list in tools/run_all_checks.sh exactly,
# so the two agree on what counts as a guide. Note README.md is NOT excluded (the suite
# treats it as guide-contract) and neither README.md nor controls-reference.md carries
# the whole-word "reasoned" marker.
META_EXCLUDE = frozenset({
    "CONTRIBUTING.md", "SECURITY.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md",
    "README.sources.md", "TODO.md", "DONE.md", "DECISIONS.md",
    "PENDING-DECISIONS.md", "controls-reference.md",
})

# The rule-5 Verify marker. The boundary excludes only ASCII letters/digits, so Markdown
# emphasis (_reasoned_, **REASONED**) still matches while "reasoning"/"unreasoned" do not.
REASONED = re.compile(r"(?i)(?<![A-Za-z0-9])reasoned(?![A-Za-z0-9])")
# A backlog row that commits to demonstrating: the whole word "demonstrate" or
# "demonstration" (case-insensitive), per the gate's definition of a tracking row.
DEMONSTRATE = re.compile(r"(?i)\b(?:demonstrate|demonstration)\b")
# An ATX heading line: capturing groups are the level (#s) and the title text.
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
# A heading whose title names a Verify step (whole word, case-insensitive).
VERIFY_TITLE = re.compile(r"(?i)\bverify\b")

BASELINE_PATH = Path("tools/reasoned_row_baseline.txt")


def guides(root: Path):
    """Yield each root-level guide path, sorted, meta files excluded."""
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        if path.name not in META_EXCLUDE:
            yield path


def verify_sections_text(text: str) -> str:
    """Concatenate the body of every Verify section in the guide.

    Lines are parsed as ATX headings. A Verify section begins at a heading whose title
    contains the word 'verify' and runs from the line AFTER that heading up to (but not
    including) the next heading whose level is <= the Verify heading's level, or the end
    of the file. This captures a `## Verify` section with its deeper subsections and each
    per-tool `### Verify` subsection in a catalogue guide. Returns the joined text of all
    such sections; a guide with no Verify heading yields the empty string.
    """
    lines = text.splitlines()
    collected = []
    i = 0
    n = len(lines)
    while i < n:
        m = HEADING.match(lines[i])
        if m and VERIFY_TITLE.search(m.group(2)):
            level = len(m.group(1))
            j = i + 1
            while j < n:
                mj = HEADING.match(lines[j])
                if mj and len(mj.group(1)) <= level:
                    break
                collected.append(lines[j])
                j += 1
            i = j
        else:
            i += 1
    return "\n".join(collected)


def has_reasoned_step(path: Path) -> bool:
    """True iff the word 'reasoned' appears inside a Verify section of the guide."""
    verify_text = verify_sections_text(path.read_text(encoding="utf-8"))
    return REASONED.search(verify_text) is not None


def demonstration_lines(root: Path):
    """Return the list of TODO/DONE lines that commit to a demonstration.

    A demonstration line is any line of TODO.md or DONE.md that contains the word
    'demonstrate'/'demonstration'. A missing backlog file is treated as empty rather than
    an error, so the gate is robust to either being absent.
    """
    lines = []
    for name in ("TODO.md", "DONE.md"):
        path = root / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue  # a missing or unreadable backlog file contributes no rows
        for line in text.splitlines():
            if DEMONSTRATE.search(line):
                lines.append(line)
    return lines


def tracked_basenames(root: Path, names):
    """Return the subset of guide basenames named on a demonstration row in TODO/DONE.

    A basename `b` is tracked iff some demonstration line references `b` as a COMPLETE
    filename token: the match must not be followed by another filename character
    (a letter/digit, or a dot introducing another alphanumeric), so `redis.md` matches
    `Demonstrate redis.md`, `` `redis.md` ``, `redis.md.` and `redis.md,` but NOT
    `redis.md.bak` or `redis.mdx`.
    """
    lines = demonstration_lines(root)
    tracked = set()
    for b in names:
        token = re.compile(re.escape(b) + r"(?![A-Za-z0-9]|\.[A-Za-z0-9])")
        if any(token.search(line) for line in lines):
            tracked.add(b)
    return tracked


def load_baseline(root: Path):
    """Return the set of grandfathered guide basenames from the baseline file.

    Blank lines and '#' comments are ignored. An absent file is an empty baseline.
    """
    path = root / BASELINE_PATH
    grandfathered = set()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return grandfathered
    for line in text.splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            grandfathered.add(entry)
    return grandfathered


def scan(root: Path):
    """Return the sorted list of guide basenames with a reasoned step but no demo row."""
    reasoned = [path for path in guides(root) if has_reasoned_step(path)]
    tracked = tracked_basenames(root, {path.name for path in reasoned})
    return [path.name for path in reasoned if path.name not in tracked]


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        prog="check_reasoned_rows.py",
        description="Flag guides with a reasoned Verify step that no demonstration "
                    "backlog row in TODO.md or DONE.md tracks.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true",
                      help="exit 1 if any non-grandfathered gap exists (blocking shape)")
    mode.add_argument("--write-baseline", action="store_true", dest="write_baseline",
                      help="overwrite tools/reasoned_row_baseline.txt with the current "
                           "full gap list (human-run, seeds the ratchet)")
    opts = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    try:
        gaps = scan(root)
    except OSError as exc:
        print(f"error: cannot scan the tree ({exc}); fail-closed", file=sys.stderr)
        return 2

    if opts.write_baseline:
        path = root / BASELINE_PATH
        header = (
            "# Reasoned-row gate baseline: guides with a reasoned Verify step and no\n"
            "# demonstration backlog row, grandfathered as known pre-existing gaps.\n"
            "# One guide basename per line; '#' comments allowed. Remove a line as its\n"
            "# demonstration row lands, to ratchet toward an empty baseline.\n")
        body = "".join(f"{name}\n" for name in gaps)
        path.write_text(header + body, encoding="utf-8")
        print(f"wrote {path} with {len(gaps)} grandfathered gap(s):")
        for name in gaps:
            print(f"  {name}")
        return 0

    grandfathered = load_baseline(root)
    new_gaps = [name for name in gaps if name not in grandfathered]
    old_gaps = [name for name in gaps if name in grandfathered]

    for name in new_gaps:
        print(f"REASONED-ROW: {name} has a reasoned Verify step but no demonstration "
              f"backlog row in TODO.md or DONE.md")
    for name in old_gaps:
        print(f"REASONED-ROW (baseline, grandfathered): {name}")

    print(f"{len(gaps)} reasoned guide(s) without a demonstration row "
          f"({len(new_gaps)} new, {len(old_gaps)} grandfathered)")

    if opts.strict:
        if new_gaps:
            print(f"FAIL: {len(new_gaps)} reasoned guide(s) have no demonstration "
                  f"backlog row and are not grandfathered. Add a 'Demonstrate ... "
                  f"<guide>' row to TODO.md, or grandfather it via --write-baseline.")
            return 1
        print("PASS: every reasoned guide is tracked or grandfathered")
        return 0

    # Advisory (default): always green.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
