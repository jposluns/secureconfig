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

WHAT IT CHECKS: every merged pull request must appear somewhere in CHANGELOG.md as
`#N`. A commit subject records a merged pull request in one of two shapes, and the gate
reads both:

- a squash merge, whose subject ends in a `(#N)` suffix; the early history used these,
  and pull requests land this way again after the move to squash merges that the
  maintainer's ruling of 2026-11-21 in DECISIONS.md sets out;
- a merge commit, whose subject begins `Merge pull request #N from `; this repository
  merged that way from #299 until that move.

The history holds both shapes, and the gate reads every subject in it whatever its order.

Reading only the first shape left merge-commit pull requests unchecked while the gate
still reported a pass. It still caught #303 and #306, but only because a commit on each
one's branch, which reached main with the merge, ended in that pull request's `(#N)`.
A merge of one branch into another, such as
`Merge remote-tracking branch 'origin/main' into ...`, is neither shape and does not
count, nor does a `#N` anywhere else in a subject. So a squash commit whose subject does
not end in its `(#N)` records no pull request, and this gate does not count it.

SQUASH SUBJECTS AFTER THE LAST MERGE COMMIT: by the maintainer's ruling of 2026-11-23 in
DECISIONS.md, "Infer from history", every first-parent commit of `main` after the newest
one whose subject begins `Merge pull request #N from ` is treated as squash-landed, and its
subject must end in `(#N)`, or this gate fails naming it. Merge commits cannot land after
the move to squash merges, so that newest merge commit marks the switch and no file has to
record it. Commits at or before it are read exactly as above; none of them is required to
end in `(#N)`. If `main` holds no such merge commit, every first-parent commit is treated as
squash-landed.

HOW `main` IS TOLD APART FROM A BRANCH: `main` is `refs/remotes/origin/main` when it
exists, else `refs/heads/main`, and if neither exists the gate fails rather than skipping
the rule. A commit is on `main` when `git rev-list --first-parent` from that ref lists it,
and the rule checks those commits only where HEAD's history also holds them. A commit that
the ref's first-parent walk does not list, such as a pull request branch's own commit, a
merge of `main` into that branch, or CI's temporary merge commit at HEAD (two parents, made
by `actions/checkout` on a `pull_request` run), is not on `main` and is skipped. So a local
run on a branch does not fail on the branch's own commits, while a direct commit to `main`
after the switch whose subject does not end in `(#N)` fails. A local run in a clone that has
`refs/remotes/origin/main` therefore checks `origin/main`, not the local `main` branch: a
direct commit on local `main` that has not been pushed is not on that ref, so a local run
skips it, and the rule checks it only once it reaches `origin/main`.

THE ONE EXEMPTION: the highest-numbered merged pull request, even when a lower-numbered
one merged after it. A pull request cannot reference its own number until it is opened,
so the highest-numbered one may be missing its entry. That is a tolerance, not a
convention: CONTRIBUTING.md's "Shipping a change" section says to record the change in
`CHANGELOG.md` "in the same pull request, not in a later bookkeeping one". The
exemption covers exactly one: let a second pull request merge without its entry and this
gate goes red.

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

# A merge commit puts it at the start, in the subject GitHub writes. Anchored at start
# of line for the same reason, and requiring ` from ` so a subject that merely begins
# with the phrase is not read as one.
MERGE_COMMIT = re.compile(r"^Merge pull request #(\d+) from ")

# Any `#N` token in the changelog counts as a reference. Deliberately looser than the
# merge pattern: `(#38, #41)`, `#45`, and `see #12` are all references, and a gate that
# recognised only one shape is what produced the mismeasurement described above.
REFERENCE = re.compile(r"#(\d+)")

# The refs that name `main`, in the order they are tried. CI's checkout with fetch-depth 0
# has the remote-tracking ref; a fresh local repository may have only the branch.
MAIN_REFS = ("refs/remotes/origin/main", "refs/heads/main")


def run(args, root):
    return subprocess.run(
        args, cwd=root, check=True, capture_output=True, text=True, timeout=30
    ).stdout


def main_ref(root):
    """The first ref in MAIN_REFS that names a commit, or None."""
    for ref in MAIN_REFS:
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        if probe.returncode == 0:
            return ref
    return None


def squash_subjects(root, ref):
    """Check the first-parent commits of `main` after its newest merge commit.

    Returns (findings, note). Each finding names a commit treated as squash-landed whose
    subject does not end in `(#N)`. The note says what was checked and, when HEAD is not
    on `main`, that HEAD was skipped.
    """
    in_head = set(run(["git", "rev-list", "HEAD"], root).split())
    on_main = []
    for row in run(["git", "log", "--first-parent", "--format=%H %s", ref], root).splitlines():
        sha, _, subject = row.partition(" ")
        if sha in in_head:
            on_main.append((sha, subject.strip()))
    if not on_main:
        return [f"no first-parent commit of {ref} is in HEAD's history"], ""

    after = on_main
    boundary = None
    for index, (sha, subject) in enumerate(on_main):
        if MERGE_COMMIT.match(subject):
            after, boundary = on_main[:index], subject
            break

    where = f"after {boundary!r}" if boundary else "with no merge commit before them"
    findings = [
        f"{ref}: {sha[:12]} is a first-parent commit {where}, so it is treated as "
        f"squash-landed, but its subject does not end in (#N): {subject}"
        for sha, subject in after
        if not MERGE_SUFFIX.search(subject)
    ]

    count = len(after)
    note = (
        f"{count} first-parent commit{'' if count == 1 else 's'} of {ref} {where} "
        f"end{'s' if count == 1 else ''} in (#N)"
    )
    head = run(["git", "rev-parse", "HEAD"], root).strip()
    if head != on_main[0][0]:
        parents = len(run(["git", "rev-list", "--parents", "-n", "1", "HEAD"], root).split()) - 1
        if parents > 1:
            note += f"; HEAD {head[:12]} is a temporary merge commit not on {ref}, skipped"
        else:
            note += f"; HEAD {head[:12]} is not on {ref}, so commits not on it are skipped"
    return findings, note


def merged_number(subject):
    """The pull request a commit subject records as merged, or None.

    A merge-commit prefix is read first: its number is the one GitHub wrote, whatever
    the branch name after it happens to end with.
    """
    m = MERGE_COMMIT.match(subject) or MERGE_SUFFIX.search(subject)
    return int(m.group(1)) if m else None


def merged_pull_requests(root):
    """Every pull request number a commit subject records as merged, with its subject."""
    out = run(["git", "log", "--format=%s"], root)
    found = {}
    for line in out.splitlines():
        number = merged_number(line.strip())
        if number is not None:
            found.setdefault(number, line.strip())
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

    ref = main_ref(root)
    if ref is None:
        findings.append(
            f"neither {' nor '.join(MAIN_REFS)} names a commit, so the first-parent commits "
            "of main after its newest merge commit cannot be checked"
        )
        squash_note = ""
    else:
        squash_findings, squash_note = squash_subjects(root, ref)
        findings.extend(squash_findings)

    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1

    exempt = "" if newest in refs else f", #{newest} exempt as the newest"
    print(f"  ok    all {len(merged)} merged pull requests are referenced in {CHANGELOG}{exempt}")
    print(f"  ok    {squash_note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
