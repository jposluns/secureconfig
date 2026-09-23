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
iff it contains the whole word "reasoned" (case-insensitive, `(?i)\breasoned\b`). This
is deliberately a whole-word substring test, not a parse of the Verify section: it does
not confirm the word sits under a `## Verify` heading, and it does not catch a guide
that reasons in its Verify step without ever writing the word "reasoned". The gate's
guarantee is only over the corpus's own convention, where the word IS the marker; it is
a tracking aid, not an adversarial classifier, and a guide that reasons under another
phrasing is out of scope by design rather than chased.

THE DEMONSTRATION-ROW DETECTOR. A guide is "tracked" iff at least one line in TODO.md
OR DONE.md contains the guide's exact basename (for example `redis.md`) AND the
case-insensitive word "demonstrate" or "demonstration" on that same line. A
creation-or-deepen row that names the guide but does not say "demonstrate" does not
count: the point is a row that commits to demonstrating the reasoned step, not merely
one that mentions the file.

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

# The rule-5 Verify marker, as a whole word so "reasoning"/"reasonable" do not match.
REASONED = re.compile(r"(?i)\breasoned\b")
# A backlog row that commits to demonstrating: the whole word "demonstrate" or
# "demonstration" (case-insensitive), per the gate's definition of a tracking row.
DEMONSTRATE = re.compile(r"(?i)\b(?:demonstrate|demonstration)\b")

BASELINE_PATH = Path("tools/reasoned_row_baseline.txt")


def guides(root: Path):
    """Yield each root-level guide path, sorted, meta files excluded."""
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        if path.name not in META_EXCLUDE:
            yield path


def has_reasoned_step(path: Path) -> bool:
    """True iff the guide contains the whole word 'reasoned' (case-insensitive)."""
    return REASONED.search(path.read_text(encoding="utf-8")) is not None


def tracked_basenames(root: Path):
    """Return the set of guide basenames named on a demonstration row in TODO/DONE.

    A basename is tracked iff some line of TODO.md or DONE.md contains BOTH that exact
    basename and the word 'demonstrate'/'demonstration'. A missing backlog file is
    treated as empty rather than an error, so the gate is robust to either being absent.
    """
    tracked = set()
    for name in ("TODO.md", "DONE.md"):
        path = root / name
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue  # a missing or unreadable backlog file contributes no rows
        for line in text.splitlines():
            if DEMONSTRATE.search(line):
                for token in re.findall(r"[\w.\-]+\.md", line):
                    tracked.add(token)
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
    tracked = tracked_basenames(root)
    gaps = []
    for path in guides(root):
        if has_reasoned_step(path) and path.name not in tracked:
            gaps.append(path.name)
    return gaps


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
