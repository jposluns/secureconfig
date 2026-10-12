#!/usr/bin/env python3
"""Cases for check_changelog_prs.py.

Each case builds a throwaway git repository, so the gate is exercised against real
history rather than a stubbed one. A case earns its place by failing when the defect it
describes is restored: every case below is run in BOTH states where that is meaningful,
the broken one expecting a non-zero exit and the fixed one expecting zero.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from _walk import isolated_git_environment

GATE = Path(__file__).resolve().parent / "check_changelog_prs.py"


def git(repo, *args):
    subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True, timeout=30
    )


def build(repo, subjects, changelog):
    """A repository whose commit subjects are `subjects`, with the given CHANGELOG.md."""
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    (repo / "tools").mkdir(exist_ok=True)
    (repo / "tools" / GATE.name).write_text(GATE.read_text(encoding="utf-8"), encoding="utf-8")
    (repo / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    for subject in subjects:
        (repo / "f.txt").write_text(subject, encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", subject)
    return repo


def run_gate(repo):
    r = subprocess.run(
        [sys.executable, str(repo / "tools" / GATE.name)],
        cwd=repo, capture_output=True, text=True, timeout=60,
    )
    return r.returncode, (r.stdout + r.stderr)


CASES = []


def case(name, subjects, changelog, expect_fail, expect_text=None):
    CASES.append((name, subjects, changelog, expect_fail, expect_text))


# The defect this gate exists for: a merged pull request with no entry. Two merges, so
# the newest-exemption cannot account for the missing one.
case(
    "a merged pull request with no reference fails",
    ["Add a thing (#10)", "Add another (#11)"],
    "# Changelog\n\n- nothing referenced here\n",
    True,
    "#10 merged but never referenced",
)
case(
    "the same history passes once the entry exists",
    ["Add a thing (#10)", "Add another (#11)"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)

# The exemption, and its limit.
case(
    "the newest merged pull request may be unreferenced",
    ["Add a thing (#10)", "Add another (#11)"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)
case(
    "the exemption covers exactly one, not two",
    ["A (#10)", "B (#11)", "C (#12)"],
    "# Changelog\n\n- Added a thing (#10).\n",
    True,
    "#11 merged but never referenced",
)

# The exemption is the highest number, not the latest merge, and pull requests do merge
# out of number order (#299 merged after #302). Here #11 merges after #12: exempting the
# latest merge instead would demand an entry for #12.
case(
    "the exemption follows the highest number, not the latest merge",
    ["A (#10)", "Merge pull request #12 from o/c", "Merge pull request #11 from o/b"],
    "# Changelog\n\n- A (#10). B (#11).\n",
    False,
)

# The mismeasurement that prompted the gate: a reference sharing a parenthesis with
# another must still count.
case(
    "a grouped reference counts, as in (#38, #41)",
    ["A (#38)", "B (#41)", "C (#42)"],
    "# Changelog\n\n- Both landed (#38, #41).\n",
    False,
)

# A number in the middle of a subject is not a merge suffix. The revert shape is the
# one with teeth: an unanchored pattern reads the quoted (#10) as a second merge, so it
# demands an entry for a pull request that merged long ago and may sit far from newest.
case(
    "a number mid-subject is not read as a merge",
    ["Mentions #99 in passing (#10)", "B (#11)"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)
case(
    "a revert subject quoting an older merge does not re-open it",
    ["A (#10)", 'Revert "A (#10)" (#25)', "C (#26)"],
    "# Changelog\n\n- Added a thing (#10). Reverted (#25).\n",
    False,
)
case(
    "the revert case discriminates: drop #10's entry and it must fail",
    ["A (#10)", 'Revert "A (#10)" (#25)', "C (#26)"],
    "# Changelog\n\n- Reverted (#25).\n",
    True,
    "#10 merged but never referenced",
)
# The mutant this exists to kill: dropping the end anchor from MERGE_SUFFIX. `search`
# returns the FIRST match, so an unanchored pattern reads the quoted (#10) and silently
# never records the revert's own #25 as merged at all. The gate then cannot notice #25
# is unreferenced, and reports a pass over a real gap.
case(
    "a revert's own number is the merge, not the number it quotes",
    ["A (#10)", 'Revert "A (#10)" (#25)', "C (#26)"],
    "# Changelog\n\n- Added a thing (#10). And later (#26).\n",
    True,
    "#25 merged but never referenced",
)

# Since #299 this repository merges with merge commits, whose subject GitHub writes
# as `Merge pull request #N from <owner>/<branch>`. A gate reading only the squash suffix
# read none of those subjects, so it checked such a pull request only when another
# commit happened to end in its `(#N)`, and it still reported a pass. Two merges, as
# above, so the newest-exemption cannot account for the missing one.
case(
    "a merge-commit pull request with no reference fails",
    ["Merge pull request #10 from o/a", "Merge pull request #11 from o/b"],
    "# Changelog\n\n- nothing referenced here\n",
    True,
    "#10 merged but never referenced",
)
case(
    "the same merge-commit history passes once the entry exists",
    ["Merge pull request #10 from o/a", "Merge pull request #11 from o/b"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)

# Both shapes in one history, as on main: the squash suffix still counts after merge
# commits arrive, and a merge commit counts after squash merges.
case(
    "a squash pull request is still checked alongside merge commits",
    ["A (#10)", "B (#11)", "Merge pull request #12 from o/c"],
    "# Changelog\n\n- B (#11). C (#12).\n",
    True,
    "#10 merged but never referenced",
)
case(
    "a merge-commit pull request is checked alongside squash merges",
    ["A (#10)", "Merge pull request #11 from o/b", "Merge pull request #12 from o/c"],
    "# Changelog\n\n- A (#10). C (#12).\n",
    True,
    "#11 merged but never referenced",
)

# The merge-commit pattern is anchored at the start of the subject. The revert line is
# the one that tests the anchor: GitHub's revert of a merge commit quotes the prefix, so
# an unanchored search reads #4, which is not the newest, and demands an entry for it.
# The branch commit leading with its pull request number does not contain the prefix,
# so it does not exercise the anchor.
case(
    "a #N mid-subject is not read as a merge-commit pull request",
    [
        "Merge pull request #10 from o/a",
        "#11 r1 fix: mentions #3 in passing",
        'Revert "Merge pull request #4 from o/d"',
        "Merge pull request #11 from o/b",
    ],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)
# The merge-commit prefix wins over a suffix-shaped branch name, so the number read is
# the one GitHub wrote. Reading the suffix first records #3 and never records #11.
case(
    "a merge commit's own number wins over a suffix in its branch name",
    ["Merge pull request #10 from o/a", "Merge pull request #11 from o/b-(#3)", "Merge pull request #12 from o/c"],
    "# Changelog\n\n- A (#10). C (#12).\n",
    True,
    "#11 merged but never referenced",
)

# GitHub writes ` from ` after the number, and the pattern requires it. A subject that
# only starts like GitHub's, or another merge subject carrying a number, is not a merged
# pull request: dropping ` from ` reads #5, and reading any `Merge` subject with a
# number reads #5 and #6.
case(
    "only GitHub's merge-commit subject counts, not a subject that starts like it",
    ["Merge pull request #10 from o/a", "Merge pull request #5 was superseded",
     "Merge branch 'issue-#6' into o/b", "Merge pull request #11 from o/b"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)

# Merging main into a branch writes a merge commit too, with no pull request in it, and
# main carries many of them. It must not count: it adds no number, and a history holding
# only such merges still fails closed rather than passing.
case(
    "merging main into a branch is not a merged pull request",
    [
        "Merge pull request #10 from o/a",
        "Merge remote-tracking branch 'origin/main' into o/b",
        "Merge pull request #11 from o/b",
    ],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)
case(
    "a history of only branch merges fails rather than reporting a pass",
    ["plain commit", "Merge remote-tracking branch 'origin/main' into o/b"],
    "# Changelog\n\n- nothing\n",
    True,
    "no merged pull request was found",
)

# Fail closed rather than pass vacuously.
case(
    "a history with no merges fails rather than reporting a pass",
    ["plain commit", "another plain commit"],
    "# Changelog\n\n- nothing\n",
    True,
    "no merged pull request was found",
)


@isolated_git_environment()
def main():
    failures = 0
    run = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, subjects, changelog, expect_fail, expect_text) in enumerate(CASES):
            repo = build(Path(tmp) / f"case{i}", subjects, changelog)
            code, out = run_gate(repo)
            run += 1
            failed = code != 0
            if failed != expect_fail:
                print(f"  FAIL  {name}: expected {'failure' if expect_fail else 'pass'}, got exit {code}")
                print(f"        output: {out.strip()[:200]}")
                failures += 1
                continue
            if expect_text and expect_text not in out:
                print(f"  FAIL  {name}: expected text {expect_text!r} not in output")
                print(f"        output: {out.strip()[:200]}")
                failures += 1

        # A shallow clone must fail rather than skip.
        src = build(Path(tmp) / "deep", ["A (#10)", "B (#11)"], "# Changelog\n\n- A (#10).\n")
        shallow = Path(tmp) / "shallow"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", f"file://{src}", str(shallow)],
            check=True, capture_output=True, text=True, timeout=60,
        )
        code, out = run_gate(shallow)
        run += 1
        if code == 0 or "shallow clone" not in out:
            print(f"  FAIL  a shallow clone must fail closed, got exit {code}: {out.strip()[:200]}")
            failures += 1

    if failures:
        print(f"  FAIL  {failures} of {run} recorded cases for the changelog-coverage gate")
        return 1
    print(f"  ok    {run} recorded cases for the changelog-coverage gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
