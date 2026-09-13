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

# The mismeasurement that prompted the gate: a reference sharing a parenthesis with
# another must still count.
case(
    "a grouped reference counts, as in (#38, #41)",
    ["A (#38)", "B (#41)", "C (#42)"],
    "# Changelog\n\n- Both landed (#38, #41).\n",
    False,
)

# A number in the middle of a subject is not a merge suffix.
case(
    "a number mid-subject is not read as a merge",
    ["Mentions #99 in passing (#10)", "B (#11)"],
    "# Changelog\n\n- Added a thing (#10).\n",
    False,
)

# Fail closed rather than pass vacuously.
case(
    "a history with no merges fails rather than reporting a pass",
    ["plain commit", "another plain commit"],
    "# Changelog\n\n- nothing\n",
    True,
    "no merged pull request was found",
)


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
