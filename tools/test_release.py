#!/usr/bin/env python3
"""Cases for check_release.py.

Each case builds a throwaway git repository whose first-parent history is a run of pull
request merges with fixed UTC committer dates, each carrying VERSION, plugin/plugin.json,
site/llms-full.txt, CHANGELOG.md and a stub tools/run_all_checks.sh, so the check is exercised
against real history, real `git archive` output and a real `git worktree`, not a stubbed one.
The stub suite stands in for the gate suite and prints its pass line, a FAIL, a SKIP or
nothing, as each case needs.

A release is built with --build and then checked, as the procedure does. Each refusal has a
passing twin that differs only in its defect: the two clean releases below, a first one and a
later one, are the twins, and each finding case changes one thing about them. Every case runs
the shipped entry point under `python3 -I -B`.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent / "check_release.py"
OK = "  ok    "
RECORDED = "is recorded, not verified"
RUN = "4242"

# The passing stub prints the one accepted SKIP, and a line on stderr before its pass line, so a
# check that read stderr after stdout would see the wrong last line.
PASSING_SUITE = ('#!/usr/bin/env bash\necho "  ok    fixture"\n'
                 'echo "  SKIP  .claude/settings.json absent; AIQT hooks are not activated"\n'
                 'echo "a note on stderr" >&2\necho\necho "All gates passed."\n')
FAILING_SUITE = ('#!/usr/bin/env bash\necho "  FAIL  fixture"\necho\n'
                 'echo "One or more gates failed."\nexit 1\n')
SKIPPING_SUITE = ('#!/usr/bin/env bash\necho "  SKIP  shellcheck is not installed"\necho\n'
                  'echo "All gates passed."\n')
SILENT_SUITE = "#!/usr/bin/env bash\nexit 0\n"
STDERR_FAIL_SUITE = ('#!/usr/bin/env bash\necho "  FAIL  on stderr" >&2\necho\n'
                     'echo "All gates passed."\n')
# The suite's advisory Python SKIP, in its exact wording, which a release accepts beside the
# settings one; the near miss drops its tail, and the unavailable line is a different SKIP.
PYTHON_SKIP = ("  SKIP  python3 3.14.4 differs from CI's pinned PYTHON_VERSION 3.14.7; "
               "html.parser behaviour may differ, so a local green predicts CI less well")
PYTHON_LINES = ('#!/usr/bin/env bash\necho "  ok    fixture"\n'
                'echo "  SKIP  .claude/settings.json absent; AIQT hooks are not activated"\n'
                f'echo "{PYTHON_SKIP}"\n')
PYTHON_SUITE = PYTHON_LINES + 'echo\necho "All gates passed."\n'
PYTHON_AND_SHELLCHECK_SUITE = (PYTHON_LINES + 'echo "  SKIP  shellcheck is not installed"\n'
                               'echo\necho "All gates passed."\n')
NEAR_MISS_SUITE = ('#!/usr/bin/env bash\n'
                   'echo "  SKIP  python3 3.14.4 differs from CI\'s pinned PYTHON_VERSION 3.14.7"\n'
                   'echo\necho "All gates passed."\n')
UNAVAILABLE_SUITE = ('#!/usr/bin/env bash\n'
                     'echo "  SKIP  Python version comparison unavailable: python3 did not '
                     'complete"\necho\necho "All gates passed."\n')
PYTHON_NOTE = ("Local python3 3.14.4 differed from CI's pinned PYTHON_VERSION 3.14.7, so CI's "
               "pinned Python is covered by the online gates check on the target, which the "
               "procedure records.")

# (pull request, UTC committer time, the date heading its entry sits under). #12 and #13 share
# 2026-10-03, so #13 is the last merge of that day and #12 is not.
HISTORY = [
    (10, "2026-10-01T12:00:00Z", "2026-10-01"),
    (11, "2026-10-02T09:00:00Z", "2026-10-02"),
    (12, "2026-10-03T10:00:00Z", "2026-10-03"),
    (13, "2026-10-03T23:30:00Z", "2026-10-03"),
    (14, "2026-10-04T08:00:00Z", "2026-10-04"),
]


def environment(root, when=None):
    """The caller's environment without Git selectors, with discovery stopped above root."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CEILING_DIRECTORIES=str(root.parent))
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return env


def git(root, *args, when=None):
    done = subprocess.run(
        ["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
        cwd=root, capture_output=True, text=True, env=environment(root, when), timeout=60)
    assert done.returncode == 0, (args, done.returncode, done.stdout + done.stderr)
    return done.stdout.strip()


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def changelog(entries, broken=False):
    """CHANGELOG.md for (pull request, heading date) entries, newest date first."""
    dates = sorted({date for _, date in entries}, reverse=True)
    parts = ["# Changelog\n\nFixture preamble.\n"]
    for date in dates:
        bullets = "".join(f"- Change {pr} (#{pr}).\n" for pr, d in entries if d == date)
        gap = "" if broken and date == dates[0] else "\n"
        parts.append(f"## {date}\n{gap}{bullets}")
    return "\n".join(parts)


def build(root, history=HISTORY, suite=PASSING_SUITE, omit=(), version=None, plugin=None,
          broken=None):
    """A repository whose main is `history`; returns each pull request's merge commit."""
    root.mkdir(parents=True)
    git(root, "init", "-q")
    write(root, "tools/run_all_checks.sh", suite)
    write(root, "VERSION", "1.0.9\n")
    write(root, "plugin/plugin.json", '{\n  "name": "fixture",\n  "version": "1.0.9"\n}\n')
    write(root, "plugin/SKILL.md", "fixture skill\n")
    write(root, "site/llms-full.txt", "bundle 9\n")
    write(root, "CHANGELOG.md", changelog([]) + "\n## 2026-09-30\n\n- Start (#9).\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "Start (#9)", when="2026-09-30T12:00:00Z")
    entries = [(9, "2026-09-30")]
    commits = {}
    for pr, when, heading in history:
        if pr not in omit:
            entries.append((pr, heading))
        number = (version or {}).get(pr, pr)
        write(root, "VERSION", f"1.0.{number}\n")
        shown = (plugin or {}).get(pr, number)
        write(root, "plugin/plugin.json",
              f'{{\n  "name": "fixture",\n  "version": "1.0.{shown}"\n}}\n')
        write(root, "site/llms-full.txt", f"bundle {pr}\n")
        write(root, "CHANGELOG.md", changelog(entries, broken == pr))
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", f"Merge pull request #{pr} from o/b{pr}", when=when)
        commits[pr] = git(root, "rev-parse", "HEAD")
    return commits


def gate(root, target, tag, previous, out, *extra):
    selector = ["--first"] if previous is None else ["--previous", previous]
    done = subprocess.run(
        [sys.executable, "-I", "-B", str(GATE), "--repo", str(root), "--target", target,
         "--tag", tag, *selector, "--gates-check-run", RUN, "--dir", str(out), *extra],
        cwd=root, capture_output=True, text=True, env=environment(root), timeout=600)
    return done.returncode, done.stdout + done.stderr


FAILURES = []
COUNT = [0]


def expect(name, result, code, *needles, absent=()):
    COUNT[0] += 1
    got, out = result
    problems = []
    if got != code:
        problems.append(f"expected exit {code}, got {got}")
    problems += [f"expected text {n!r} not in output" for n in needles if n not in out]
    problems += [f"unexpected text {n!r} in output" for n in absent if n in out]
    if problems:
        FAILURES.append(name)
        print(f"  FAIL  {name}: {'; '.join(problems)}")
        print(f"        output: {out.strip()[:400]}")


def release(root, target, tag, previous, out, *extra):
    """Build, then check, as the procedure does; the check's result."""
    built = gate(root, target, tag, previous, out, "--build", *extra)
    if built[0] != 0:
        return built
    return gate(root, target, tag, previous, out, *extra)


def cases(tmp):
    # The two clean releases, which every finding case below differs from by one thing.
    repo = tmp / "clean"
    c = build(repo)
    first = tmp / "first"
    expect("a first release of the last merge of a UTC day passes",
           release(repo, c[11], "v1.0.11", None, first), 0, OK, RECORDED, "check run 4242",
           "dating not checked for a first release", absent=("differed from CI's pinned",))
    body = (first / "body.md").read_text(encoding="utf-8")
    notes = (first / "assets" / "RELEASE-NOTES-v1.0.11.md").read_text(encoding="utf-8")
    expect("the first release's body lists every pull request up to the target",
           (0, body), 0, "Pull requests merged in that range (3): #9, #10, #11.",
           "This is the first tagged release.", "/blob/v1.0.11/CHANGELOG.md",
           "follow the moving branch", absent=("#12",))
    expect("the first release's notes extract no sections and point to CHANGELOG.md at the tag",
           (0, notes), 0, "first tagged release", "/blob/v1.0.11/CHANGELOG.md",
           absent=("## 2026-",))
    worktrees = git(repo, "worktree", "list")
    expect("the check leaves no worktree behind", (0, worktrees), 0,
           absent=("release-check.",))
    expect("the release directory must be new for --build",
           gate(repo, c[11], "v1.0.11", None, first, "--build"), 2, "cannot check")

    git(repo, "tag", "v1.0.11", c[11])
    later = tmp / "later"
    expect("a later release from the previous tag passes",
           release(repo, c[13], "v1.0.13", "v1.0.11", later), 0, OK, RECORDED,
           "each one referenced under its UTC merge date")
    notes = (later / "assets" / "RELEASE-NOTES-v1.0.13.md").read_text(encoding="utf-8")
    expect("the later notes hold exactly the sections after the previous release's date",
           (0, notes), 0, "## 2026-10-03\n\n- Change 12 (#12).\n- Change 13 (#13).\n",
           "after 2026-10-02, the date of v1.0.11", absent=("## 2026-10-02", "## 2026-10-04"))
    body = (later / "body.md").read_text(encoding="utf-8")
    expect("the later body lists exactly the range's pull requests",
           (0, body), 0, "Pull requests merged in that range (2): #12, #13.")
    again = tmp / "again"
    gate(repo, c[13], "v1.0.13", "v1.0.11", again, "--build")
    same = all((later / p).read_bytes() == (again / p).read_bytes()
               for p in ["body.md", *(f"assets/{n}" for n in sorted(os.listdir(later / "assets")))])
    expect("two builds of one release are byte-identical", (0 if same else 1, ""), 0)

    # Checks 7 and 8: the release directory, each mutated once from the clean later release.
    mutations = [
        ("an asset changed after the build is refused", "assets/llms-full.txt", b"other\n",
         ["differs from its rebuild", "does not verify llms-full.txt"]),
        ("a body whose pull request list was edited is refused", "body.md",
         body.replace("#12, #13", "#13").encode(), ["body regenerated from the target"]),
        ("an extra file among the assets is refused", "assets/extra.txt", b"x\n",
         ["is not a release asset"]),
        ("edited notes are refused", "assets/RELEASE-NOTES-v1.0.13.md", b"# notes\n",
         ["RELEASE-NOTES-v1.0.13.md differs"]),
    ]
    for name, relative, data, needles in mutations:
        copy = tmp / f"mutated{COUNT[0]}"
        gate(repo, c[13], "v1.0.13", "v1.0.11", copy, "--build")
        (copy / relative).write_bytes(data)
        expect(name, gate(repo, c[13], "v1.0.13", "v1.0.11", copy), 1, *needles,
               "was not run because an earlier check failed")

    # Check 1: the target.
    expect("a target that is not the last merge of its UTC day is refused",
           release(repo, c[12], "v1.0.12", "v1.0.11", tmp / "midday"), 1,
           "is not the last merge of 2026-10-03 UTC")
    git(repo, "checkout", "-q", "-b", "side", c[11])
    write(repo, "VERSION", "1.0.15\n")
    git(repo, "commit", "-q", "-am", "Merge pull request #15 from o/b15",
        when="2026-10-02T10:00:00Z")
    side = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "main")
    expect("a target off main's first-parent chain is refused",
           release(repo, side, "v1.0.15", "v1.0.11", tmp / "side"), 1,
           "is not on the first-parent chain of main")
    expect("a target that is not a pull request merge is refused",
           release(repo, git(repo, "rev-parse", "HEAD~5"), "v1.0.9", None, tmp / "plain"), 1,
           "does not begin `Merge pull request #N from `")
    expect("an abbreviated target id cannot be checked",
           release(repo, c[13][:12], "v1.0.13", "v1.0.11", tmp / "short"), 2,
           "not a full 40-character")
    expect("a non-numeric gates check run id cannot be checked",
           subprocess_result(repo, c[13], "abc"), 2, "not a numeric check run id")

    # Checks 2 and 3: the tag.
    expect("a tag that is not v plus VERSION at the target is refused",
           release(repo, c[13], "v1.0.14", "v1.0.11", tmp / "wrongtag"), 1,
           "is not `v` plus VERSION at the target, v1.0.13")
    expect("a tag that already exists locally is refused",
           release(repo, c[11], "v1.0.11", None, tmp / "exists"), 1,
           "already exists locally", "--first was given")
    git(repo, "tag", "v1.0.10", c[10])
    expect("a previous tag that is not the highest local release tag is refused",
           release(repo, c[13], "v1.0.13", "v1.0.10", tmp / "nothighest"), 1,
           "is not the highest-numbered local release tag; v1.0.11 is")
    git(repo, "tag", "v1.0.20", side)
    expect("a previous tag that is not an ancestor of the target is refused",
           release(repo, c[13], "v1.0.13", "v1.0.20", tmp / "notancestor"), 1,
           "is not an ancestor of the target", "not numbered strictly above")

    # Checks 5 and 6: CHANGELOG.md at the target, in fixtures that differ by one entry.
    repo = tmp / "missing"
    c = build(repo, omit=(13,))
    git(repo, "tag", "v1.0.11", c[11])
    expect("a target whose own entry is missing is refused, with no newest exemption",
           release(repo, c[13], "v1.0.13", "v1.0.11", tmp / "m"), 1,
           "#13 (", "never referenced")
    repo = tmp / "misdated"
    c = build(repo, history=[*HISTORY[:3], (13, "2026-10-03T23:30:00Z", "2026-10-04"),
                             HISTORY[4]])
    git(repo, "tag", "v1.0.11", c[11])
    expect("an entry under a date other than its UTC merge date is refused",
           release(repo, c[13], "v1.0.13", "v1.0.11", tmp / "d"), 1,
           "#13 (", "merged on 2026-10-03 UTC but is not referenced under `## 2026-10-03`")
    repo = tmp / "format"
    c = build(repo, broken=13)
    git(repo, "tag", "v1.0.11", c[11])
    expect("a CHANGELOG.md at the target that fails the format rules is refused",
           release(repo, c[13], "v1.0.13", "v1.0.11", tmp / "f"), 1,
           "at the target: `## 2026-10-03` is not followed by a blank line")

    # Checks 2 and 3 again: out-of-order merges that share one VERSION, and a lagging manifest.
    repo = tmp / "outoforder"
    c = build(repo, history=[HISTORY[0], (13, "2026-10-02T09:00:00Z", "2026-10-02"),
                             (12, "2026-10-03T23:30:00Z", "2026-10-03"), HISTORY[4]],
              version={12: 13})
    git(repo, "tag", "v1.0.13", c[13])
    expect("a release whose VERSION did not move past the previous one is refused",
           release(repo, c[12], "v1.0.13", "v1.0.13", tmp / "o"), 1,
           "already exists locally", "not numbered strictly above the previous release")
    repo = tmp / "manifest"
    c = build(repo, plugin={11: 10})
    expect("a plugin.json version that differs from VERSION is refused",
           release(repo, c[11], "v1.0.11", None, tmp / "p"), 1,
           "plugin/plugin.json at the target carries version '1.0.10'")
    repo = tmp / "badversion"
    c = build(repo, version={11: "11-rc"}, plugin={11: "11-rc"})
    expect("a malformed VERSION is refused",
           release(repo, c[11], "v1.0.11-rc", None, tmp / "b"), 2,
           "is not shaped v1.0.<digits>", "VERSION at the target is '1.0.11-rc'")

    # Check 1 again: a UTC day that has not ended.
    repo = tmp / "future"
    c = build(repo, history=[*HISTORY, (15, "2099-01-01T12:00:00Z", "2099-01-01")])
    expect("a target whose UTC date has not ended is refused",
           release(repo, c[15], "v1.0.15", None, tmp / "future-out"), 1, "has not ended")

    # Check 9: the suite in a worktree of the target.
    for name, suite, needle in [
        ("a suite that fails in the target's worktree refuses the release", FAILING_SUITE,
         "exited 1 with 1 FAIL or SKIP lines"),
        ("a suite that skips a gate refuses the release", SKIPPING_SUITE,
         "SKIP  shellcheck is not installed"),
        ("a suite that exits 0 without its pass line refuses the release", SILENT_SUITE,
         "last line ''"),
        ("a FAIL the suite prints on stderr refuses the release", STDERR_FAIL_SUITE,
         "FAIL  on stderr"),
        ("an accepted Python SKIP does not excuse another SKIP", PYTHON_AND_SHELLCHECK_SUITE,
         "exited 0 with 1 FAIL or SKIP lines, last line 'All gates passed.': SKIP  shellcheck"),
        ("a Python SKIP in other wording refuses the release", NEAR_MISS_SUITE,
         "SKIP  python3 3.14.4 differs from CI's pinned PYTHON_VERSION 3.14.7"),
        ("a Python comparison that could not run refuses the release", UNAVAILABLE_SUITE,
         "SKIP  Python version comparison unavailable"),
    ]:
        repo = tmp / f"suite{COUNT[0]}"
        c = build(repo, suite=suite)
        expect(name, release(repo, c[11], "v1.0.11", None, tmp / f"suite-out{COUNT[0]}"), 1,
               needle)
    repo = tmp / "python"
    c = build(repo, suite=PYTHON_SUITE)
    expect("the suite's advisory Python SKIP passes, and the pass line says CI's Python is "
           "covered online", release(repo, c[11], "v1.0.11", None, tmp / "python-out"), 0, OK,
           PYTHON_NOTE, RECORDED, absent=("FAIL",))

    # A shallow clone cannot show the history, so it fails closed rather than passing.
    shallow = tmp / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", "--no-local", str(tmp / "clean"),
                    str(shallow)], check=True, capture_output=True, text=True,
                   env=environment(tmp / "clean"), timeout=60)
    head = git(shallow, "rev-parse", "HEAD")
    expect("a shallow clone fails closed",
           release(shallow, head, "v1.0.14", None, tmp / "s"), 2, "shallow clone")


def subprocess_result(repo, target, run_id):
    done = subprocess.run(
        [sys.executable, "-I", "-B", str(GATE), "--repo", str(repo), "--target", target,
         "--tag", "v1.0.13", "--previous", "v1.0.11", "--gates-check-run", run_id,
         "--dir", str(repo.parent / "runid"), "--build"],
        cwd=repo, capture_output=True, text=True, env=environment(repo), timeout=600)
    return done.returncode, done.stdout + done.stderr


def main():
    with tempfile.TemporaryDirectory() as directory:
        cases(Path(directory))
    if FAILURES:
        print(f"  FAIL  {len(FAILURES)} of {COUNT[0]} recorded cases for the release check")
        return 1
    print(f"  ok    {COUNT[0]} recorded cases for the release check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
