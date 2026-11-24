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

# `python3 -I` leaves the script's folder off sys.path, so put tools/ there for _walk.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _walk import isolated_git_environment  # noqa: E402

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
        commit(repo, subject)
    return repo


def commit(repo, subject, name="f.txt"):
    (repo / name).write_text(subject, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", subject)


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

# From #299 this repository merged with merge commits, whose subject GitHub writes as
# `Merge pull request #N from <owner>/<branch>`, until the move to squash merges that the
# maintainer's ruling of 2026-11-21 in DECISIONS.md sets out; main keeps both shapes after
# that move, so the merge-commit cases below still apply. A gate reading only the
# squash suffix read none of those subjects, so it checked such a pull request only when
# another commit happened to end in its `(#N)`, and it still reported a pass. Two merges,
# as above, so the newest-exemption cannot account for the missing one.
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


# Row 3.128, by the maintainer's ruling of 2026-11-23, "Infer from history": every
# first-parent commit of main after the newest `Merge pull request #N from ` commit is
# squash-landed and must end in `(#N)`. Each case below builds main from its subjects and
# then runs its shape, which may move HEAD off main or return a clone, and the gate runs in
# the clone when there is one. Every one of them fails on the gate before that change: a
# case expecting failure because that gate passes over the commit or the missing ref, and a
# case expecting a pass because that gate never checks first-parent subjects, so the text it
# expects is absent. Each case expecting a pass has a partner of the same shape expecting
# failure, so the pair asserts that the check still runs in that shape, not only the note.
SHAPED = []


def shaped(name, subjects, shape, changelog, expect_fail, expect_text):
    """`expect_text` is one string, or a tuple of strings that must all be in the output."""
    SHAPED.append((name, subjects, shape, changelog, expect_fail, expect_text))


# Branch commits write their own file, so merging main into the branch cannot conflict.
BRANCH_FILE = "branch.txt"


def on_main(repo):
    """HEAD is main's tip, as on a scheduled run."""


def temporary_merge(repo):
    """CI's pull_request checkout: a two-parent merge of the branch into main, detached."""
    git(repo, "checkout", "-q", "-b", "o/d")
    commit(repo, "work in progress, no number yet", BRANCH_FILE)
    git(repo, "checkout", "-q", "--detach", "main")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge 0123abc into 4567def", "o/d")


def branch_commit(repo):
    """A local run on a pull request's branch, one commit ahead of main."""
    git(repo, "checkout", "-q", "-b", "o/d")
    commit(repo, "work in progress, no number yet", BRANCH_FILE)


def main_merged_into_branch(subject):
    """A branch that merged main in after main gained `subject`."""
    def shape(repo):
        git(repo, "checkout", "-q", "-b", "o/d")
        commit(repo, "work in progress, no number yet", BRANCH_FILE)
        git(repo, "checkout", "-q", "main")
        commit(repo, subject)
        git(repo, "checkout", "-q", "o/d")
        git(repo, "merge", "-q", "--no-ff", "-m", "Merge branch 'main' into o/d", "main")
        commit(repo, "more work, still no number", BRANCH_FILE)
    return shape


def pull_request_clone(repo):
    """CI's pull_request checkout with fetch-depth 0, cloned from `repo` as its origin.

    The origin gains a branch and GitHub's refs/pull/1/merge, a two-parent merge of that
    branch into main. The clone fetches the origin's branches as refs/remotes/origin/* and
    that merge ref, then checks the merge out detached, as actions/checkout does, so it has
    no refs/heads/main and the gate has to take refs/remotes/origin/main.
    """
    temporary_merge(repo)
    git(repo, "update-ref", "refs/pull/1/merge", "HEAD")
    git(repo, "checkout", "-q", "main")
    clone = repo.parent / f"{repo.name}-clone"
    clone.mkdir()
    git(clone, "init", "-q")
    git(clone, "remote", "add", "origin", f"file://{repo}")
    git(clone, "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*",
        "+refs/pull/1/merge:refs/remotes/pull/1/merge")
    git(clone, "checkout", "-q", "--detach", "refs/remotes/pull/1/merge")
    return clone


def no_main_ref(repo):
    """A repository whose branch is `trunk`, with no origin, so neither ref names main."""
    git(repo, "branch", "-q", "-m", "main", "trunk")


MERGED = "# Changelog\n\n- A (#10). B (#11). C (#12).\n"

shaped(
    "a squash commit without (#N) after the newest merge commit fails, naming it",
    ["A (#10)", "Merge pull request #11 from o/b", "C landed without its number"],
    on_main, MERGED, True,
    "its subject does not end in (#N): C landed without its number",
)
shaped(
    "a squash commit with (#N) after the newest merge commit passes",
    ["A (#10)", "Merge pull request #11 from o/b", "C (#12)"],
    on_main, MERGED, False,
    "1 first-parent commit of refs/heads/main after 'Merge pull request #11 from o/b' ends in (#N)",
)
# A naive walk from HEAD would read CI's merge subject, which has no `(#N)`, and fail.
shaped(
    "a temporary merge commit at HEAD is skipped",
    ["A (#10)", "Merge pull request #11 from o/b", "C (#12)"],
    temporary_merge, MERGED, False,
    "is a temporary merge commit not on refs/heads/main, skipped",
)
# Skipping HEAD must not skip main: a gate that checked nothing when HEAD is not on main
# would pass the case above.
shaped(
    "a bad squash subject on main fails under a temporary merge commit at HEAD",
    ["A (#10)", "Merge pull request #11 from o/b", "C landed without its number"],
    temporary_merge, MERGED, True,
    "its subject does not end in (#N): C landed without its number",
)
# A naive walk from HEAD would read the branch's own commit, which has no `(#N)`, and fail.
shaped(
    "a branch commit on top of main is skipped",
    ["A (#10)", "Merge pull request #11 from o/b", "C (#12)"],
    branch_commit, MERGED, False,
    "is not on refs/heads/main, so commits not on it are skipped",
)
shaped(
    "a bad squash subject on main fails under a branch commit at HEAD",
    ["A (#10)", "Merge pull request #11 from o/b", "C landed without its number"],
    branch_commit, MERGED, True,
    "its subject does not end in (#N): C landed without its number",
)
# The walk is main's, not HEAD's: a branch that merged main in still has main's later
# commits checked, though HEAD's own first-parent walk never reaches them.
shaped(
    "main's commits are still checked on a branch that merged main in",
    ["A (#10)", "Merge pull request #11 from o/b"],
    main_merged_into_branch("C (#12)"), MERGED, False,
    "1 first-parent commit of refs/heads/main after 'Merge pull request #11 from o/b' ends in (#N)",
)
shaped(
    "a bad squash subject on main fails on a branch that merged main in",
    ["A (#10)", "Merge pull request #11 from o/b"],
    main_merged_into_branch("C landed without its number"), MERGED, True,
    "its subject does not end in (#N): C landed without its number",
)
# Behaviour before the boundary is unchanged: a commit at or before the newest merge
# commit need not end in (#N).
shaped(
    "a commit before the newest merge commit need not end in (#N)",
    ["an early commit with no number", "Merge pull request #11 from o/b", "C (#12)"],
    on_main, MERGED, False,
    "1 first-parent commit of refs/heads/main after 'Merge pull request #11 from o/b' ends in (#N)",
)

# The CI path. Every case above has refs/heads/main and no remote, so a gate that dropped
# refs/remotes/origin/main from the refs it tries passed them all. In CI's pull_request
# checkout only refs/remotes/origin/main names main, and the gate must check it.
shaped(
    "CI's pull_request checkout checks refs/remotes/origin/main and skips its merge",
    ["A (#10)", "Merge pull request #11 from o/b", "C (#12)"],
    pull_request_clone, MERGED, False,
    ("1 first-parent commit of refs/remotes/origin/main after 'Merge pull request #11 from o/b' "
     "ends in (#N)",
     "is a temporary merge commit not on refs/remotes/origin/main, skipped"),
)
shaped(
    "a bad squash subject on refs/remotes/origin/main fails in CI's pull_request checkout",
    ["A (#10)", "Merge pull request #11 from o/b", "C landed without its number"],
    pull_request_clone, MERGED, True,
    ("FAIL  refs/remotes/origin/main: ",
     "its subject does not end in (#N): C landed without its number"),
)
# Fail closed: with neither ref the rule cannot be checked, so the gate exits 1 and says why
# rather than passing. Every subject is good, so that is the only reason it can fail.
shaped(
    "neither refs/remotes/origin/main nor refs/heads/main fails rather than passing",
    ["A (#10)", "Merge pull request #11 from o/b", "C (#12)"],
    no_main_ref, MERGED, True,
    "neither refs/remotes/origin/main nor refs/heads/main names a commit, so the first-parent "
    "commits of main after its newest merge commit cannot be checked",
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

        for i, (name, subjects, shape, changelog, expect_fail, expect_text) in enumerate(SHAPED):
            repo = build(Path(tmp) / f"shaped{i}", subjects, changelog)
            code, out = run_gate(shape(repo) or repo)
            run += 1
            failed = code != 0
            if failed != expect_fail:
                print(f"  FAIL  {name}: expected {'failure' if expect_fail else 'pass'}, got exit {code}")
                print(f"        output: {out.strip()[:300]}")
                failures += 1
                continue
            texts = (expect_text,) if isinstance(expect_text, str) else expect_text
            missing = [text for text in texts if text not in out]
            if missing:
                print(f"  FAIL  {name}: expected text {missing[0]!r} not in output")
                print(f"        output: {out.strip()[:300]}")
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
