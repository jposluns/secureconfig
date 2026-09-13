#!/usr/bin/env python3
"""Check that every merged pull request is referenced in CHANGELOG.md.

WHAT THIS CATCHES: a merged pull request whose work is never recorded, so the history
cannot be mapped back to the changes that produced it. Eight such pull requests had
accumulated before anyone noticed, and the gap was found by an audit rather than by a
gate. They were all records maintenance, which is why nobody missed them: the changelog
recorded every content change and omitted only its own upkeep.

It also catches a careless measurement of that gap. The first attempt matched a lone
`(#N)` and silently missed `(#38, #41)`, reporting a larger gap than existed. A gate does
not get to be approximately right.

WHAT IT CHECKS: every pull request number appearing as a `(#N)` suffix on a commit
subject must appear somewhere in CHANGELOG.md as `#N`.

THE ONE EXEMPTION: the highest-numbered merged pull request. A pull request cannot
reference its own number until it is opened, and the convention here is that a content
change may be followed by a separate bookkeeping change that records it. Exempting the
newest one leaves room for exactly that, and no more: let a second pull request merge
without its entry and this gate goes red.

WHY IT FAILS ON A SHALLOW CLONE rather than skipping: `actions/checkout` fetches one
commit by default, and with one commit this gate would find nothing missing and report a
pass. A check whose failure is indistinguishable from its success is the defect this
repository keeps finding, so an unusable history is an error, not a skip. The workflow
sets `fetch-depth: 0` to make the history available.

This gate is deterministic and offline: it reads the local git history and one file.
"""

import re
import subprocess
import sys
from pathlib import Path

CHANGELOG = "CHANGELOG.md"

# A squash merge puts the pull request number in the subject, as a parenthesised
# suffix. Anchored at end of line so a number mentioned mid-subject is not a merge.
MERGE_SUFFIX = re.compile(r"\(#(\d+)\)$")

# Any `#N` token in the changelog counts as a reference. Deliberately looser than the
# merge pattern: `(#38, #41)`, `#45`, and `see #12` are all references, and a gate that
# recognised only one shape is what produced the mismeasurement described above.
REFERENCE = re.compile(r"#(\d+)")


def run(args, root):
    return subprocess.run(
        args, cwd=root, check=True, capture_output=True, text=True, timeout=30
    ).stdout


def merged_pull_requests(root):
    """Every pull request number that appears as a squash-merge suffix, with its subject."""
    out = run(["git", "log", "--format=%s"], root)
    found = {}
    for line in out.splitlines():
        m = MERGE_SUFFIX.search(line.strip())
        if m:
            found.setdefault(int(m.group(1)), line.strip())
    return found


def referenced(text):
    return {int(n) for n in REFERENCE.findall(text)}


def main():
    root = Path(__file__).resolve().parent.parent
    findings = []

    shallow = run(["git", "rev-parse", "--is-shallow-repository"], root).strip()
    if shallow == "true":
        print(
            "  FAIL  the repository is a shallow clone, so the merge history cannot be "
            "read; check out with fetch-depth: 0"
        )
        return 1

    changelog = root / CHANGELOG
    if not changelog.is_file():
        print(f"  FAIL  {CHANGELOG} is missing")
        return 1

    merged = merged_pull_requests(root)
    if not merged:
        print(
            "  FAIL  no merged pull request was found in the history; either the history "
            "is unavailable or the merge convention changed"
        )
        return 1

    refs = referenced(changelog.read_text(encoding="utf-8"))
    newest = max(merged)

    for number in sorted(set(merged) - refs):
        if number == newest:
            continue
        findings.append(f"{CHANGELOG}: #{number} merged but never referenced: {merged[number]}")

    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1

    exempt = "" if newest in refs else f", #{newest} exempt as the newest"
    print(f"  ok    all {len(merged)} merged pull requests are referenced in {CHANGELOG}{exempt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
