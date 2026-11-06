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

# The shell-block gate's pass line, which names the shellcheck version that ran.
SHELL_OK = 'echo "  ok    3 bash blocks in 2 guides parse and pass shellcheck {} at /bin/sc"\n'
# The passing stub prints the shell-block pass line and the one accepted SKIP, and a line on
# stderr before its pass line, so a check that read stderr after stdout would see the wrong last
# line. The other-shellcheck stub differs from it only in the version, which is not compared.
PASSING_LINES = ('echo "  SKIP  .claude/settings.json absent; AIQT hooks are not activated"\n'
                 'echo "a note on stderr" >&2\necho\necho "All gates passed."\n')
PASSING_SUITE = '#!/usr/bin/env bash\n' + SHELL_OK.format("0.11.0") + PASSING_LINES
OTHER_SHELLCHECK_SUITE = '#!/usr/bin/env bash\n' + SHELL_OK.format("0.10.0") + PASSING_LINES
UNLINTED_SUITE = '#!/usr/bin/env bash\necho "  ok    fixture"\n' + PASSING_LINES
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
PYTHON_LINES = ('#!/usr/bin/env bash\n' + SHELL_OK.format("0.11.0") +
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

# The body's statement of the run every release dispatches, and of the targets that can have one.
SINCE_1194 = ("A release targets a commit at or after the merge of pull request #1194, the first "
              "merge on `main` whose `.github/workflows/checks.yml` has the `workflow_dispatch` "
              "trigger.")
DISPATCH_BODY = ("the publisher confirmed online that `gates` check run 4242 is from a run of the "
                 "whole suite whose event is `workflow_dispatch` and whose branch is "
                 "`release-check/v1.0.11`")
CONFIRMED = ("succeeded on exactly the target commit. These are the publisher's confirmations; "
             "the offline release check records the id and does not verify them.")

# The target's .github/workflows/checks.yml: a stub with the trigger as checks.yml writes it,
# and the variants below, each of which replaces only its `on:` block.
WORKFLOW_HEAD = "name: Checks\n\n# A release runs this on its target.\n"
WORKFLOW_ON = ('on:\n  pull_request:\n    types: [opened, synchronize]\n  schedule:\n'
               '    - cron: "0 6 * * 1"\n  workflow_dispatch: {}\n')
WORKFLOW_TAIL = ("\npermissions:\n  contents: read\n\njobs:\n  gates:\n"
                 "    runs-on: ubuntu-latest\n    steps:\n      - run: |\n"
                 "          bash tools/run_all_checks.sh\n")
WORKFLOW = WORKFLOW_HEAD + WORKFLOW_ON + WORKFLOW_TAIL
SYMLINK = object()
DIRECTORY = object()
NEEDS_TRIGGER = ("a release needs the plain `workflow_dispatch:` key directly under the file's "
                 "top-level `on:` block mapping, as at the merge of #1194 and later")


def workflow(on):
    """The stub workflow with its `on:` block replaced."""
    return WORKFLOW_HEAD + on + WORKFLOW_TAIL


def valued(value):
    """The stub workflow with the trigger and, on line 6, `pull_request:` holding value."""
    return workflow("on:\n  workflow_dispatch: {}\n  pull_request: " + value + "\n")


# The start of a refusal of line 6 as a form the line model does not list, and the reason
# given for every flow collection other than the two forms read.
FORMS_6 = "line 6 is outside the forms this check reads ("
FLOW_REFUSED = ("a flow collection other than {} or a one-line [a, b] list of names made of "
                "letters, digits and _ . / -, which this check does not read")


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
          broken=None, checks=WORKFLOW):
    """A repository whose main is `history`; returns each pull request's merge commit.

    `checks` is the text of .github/workflows/checks.yml, its bytes, None for no such file,
    SYMLINK for a symlink to a file holding the stub, or DIRECTORY for a directory holding it.
    """
    root.mkdir(parents=True)
    git(root, "init", "-q")
    write(root, "tools/run_all_checks.sh", suite)
    if checks is SYMLINK:
        write(root, ".github/workflows/real.yml", WORKFLOW)
        (root / ".github/workflows/checks.yml").symlink_to("real.yml")
    elif checks is DIRECTORY:
        write(root, ".github/workflows/checks.yml/checks.yml", WORKFLOW)
    elif isinstance(checks, bytes):
        (root / ".github/workflows").mkdir(parents=True)
        (root / ".github/workflows/checks.yml").write_bytes(checks)
    elif checks is not None:
        write(root, ".github/workflows/checks.yml", checks)
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
           "dating not checked for a first release",
           "Its shell-block gate reported shellcheck 0.11.0, which this check does not compare",
           absent=("differed from CI's pinned",))
    body = (first / "body.md").read_text(encoding="utf-8")
    notes = (first / "assets" / "RELEASE-NOTES-v1.0.11.md").read_text(encoding="utf-8")
    expect("the first release's body lists every pull request up to the target",
           (0, body), 0, "Pull requests merged in that range (3): #9, #10, #11.",
           "This is the first tagged release.", "/blob/v1.0.11/CHANGELOG.md",
           "follow the moving branch", SINCE_1194, DISPATCH_BODY,
           "a temporary branch pushed at the target and deleted afterwards", CONFIRMED,
           absent=("#12", "push to `main`"))
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
        ("a SHA256SUMS changed after the build, with the assets unchanged, is refused",
         "assets/SHA256SUMS", b"0" * 64 + b"  llms-full.txt\n",
         ["SHA256SUMS differs from its rebuild", "SHA256SUMS does not verify llms-full.txt"]),
    ]
    for name, relative, data, needles in mutations:
        copy = tmp / f"mutated{COUNT[0]}"
        gate(repo, c[13], "v1.0.13", "v1.0.11", copy, "--build")
        (copy / relative).write_bytes(data)
        expect(name, gate(repo, c[13], "v1.0.13", "v1.0.11", copy), 1, *needles,
               "was not run because an earlier check failed")
    copy = tmp / "unlinked"
    gate(repo, c[13], "v1.0.13", "v1.0.11", copy, "--build")
    (copy / "assets" / "RELEASE-NOTES-v1.0.13.md").unlink()
    expect("a missing asset is refused", gate(repo, c[13], "v1.0.13", "v1.0.11", copy), 1,
           "RELEASE-NOTES-v1.0.13.md is missing or not a regular file",
           "was not run because an earlier check failed")
    # A symlink to a file holding the right bytes: the asset must be the regular file itself.
    copy = tmp / "symlinked"
    gate(repo, c[13], "v1.0.13", "v1.0.11", copy, "--build")
    outside = tmp / "outside-llms-full.txt"
    outside.write_bytes((copy / "assets" / "llms-full.txt").read_bytes())
    (copy / "assets" / "llms-full.txt").unlink()
    (copy / "assets" / "llms-full.txt").symlink_to(outside)
    expect("a symlinked asset with the right bytes is refused",
           gate(repo, c[13], "v1.0.13", "v1.0.11", copy), 1,
           "llms-full.txt is missing or not a regular file",
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

    # Check 1 again: the target's checks.yml has the workflow_dispatch trigger. The clean
    # releases above pass with `workflow_dispatch: {}`; these other accepted forms pass checks 1
    # to 6 with --build, and each refused form is checked for the message it expects.
    accepted = [
        ("a bare `workflow_dispatch:` with a comment",
         workflow("on:  # triggers\n  pull_request:\n  workflow_dispatch:  # on demand\n")),
        ("`workflow_dispatch:` with a nested block mapping",
         workflow("on:\n  workflow_dispatch:\n    inputs:\n      reason:\n"
                  "        description: why\n  pull_request:\n")),
        ("CRLF line endings and a leading ---", "---\r\n" + WORKFLOW.replace("\n", "\r\n")),
        # Rules of the pins gate that are not the release check's: the word `uses` in a block
        # scalar, and a quoted `"uses"` key.
        ("the word `uses` in a block scalar and a quoted `\"uses\"` key",
         WORKFLOW + "      - \"uses\": ./local\n      - run: |\n          echo uses\n"),
        ("block sequences at their key's own column and nested deeper",
         workflow("on:\n  schedule:\n  - cron: \"0 6 * * 1\"\n  pull_request:\n    types:\n"
                  "    - opened\n    - - nested\n      - key: value\n        other: value\n"
                  "  workflow_dispatch:\n    inputs:\n      kind:\n        options:\n"
                  "        - quick\n")),
        # The longest key read: 1,024 characters from its first to its `:`.
        ("a key of 1,024 characters",
         workflow("on:\n  workflow_dispatch: {}\n  " + "k" * 1024 + ": x\n")),
        # Every flow sequence entry character the line model reads, and a comment after it.
        ("a flow sequence of names using every character it reads",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n"
                  "    types: [Opened_1, a.b/c-d, 9]  # c\n")),
    ]
    for name, text in accepted:
        other = tmp / f"dispatch{COUNT[0]}"
        merges = build(other, checks=text)
        expect(f"a target whose checks.yml has {name} passes checks 1 to 6",
               gate(other, merges[11], "v1.0.11", None, tmp / f"dispatch-out{COUNT[0]}",
                    "--build"), 0, "checks 1 to 6 passed", absent=("FAIL",))
    refused = [
        ("no checks.yml", None, "checks.yml at the target: it does not exist"),
        ("a symlinked checks.yml", SYMLINK, "it is not a regular file (mode 120000, blob)"),
        ("no workflow_dispatch key",
         workflow("on:\n  pull_request:\n  schedule:\n    - cron: \"0 6 * * 1\"\n"),
         "the top-level `on:` has no `workflow_dispatch` key"),
        ("the key only nested under another trigger",
         workflow("on:\n  pull_request:\n    workflow_dispatch: {}\n"),
         "`workflow_dispatch` is a key only at line 6, which is not directly under"),
        ("the key only at the top level, beside `on:`",
         workflow("on:\n  pull_request:\nworkflow_dispatch: {}\n"),
         "`workflow_dispatch` is a key only at line 6, which is not directly under"),
        ("the key only in a comment",
         workflow("on:\n  pull_request:\n  # workflow_dispatch: {}\n"),
         "`workflow_dispatch` appears only in a comment or a scalar, first at line 6"),
        ("the key only in a string",
         workflow("on:\n  pull_request:\n    types: \"workflow_dispatch\"\n"),
         "`workflow_dispatch` appears only in a comment or a scalar, first at line 6"),
        ("`on:` as a plain string", workflow("on: workflow_dispatch\n"),
         "line 4: the top-level `on:` is a plain string, 'workflow_dispatch', not a block mapping"),
        ("`on:` as a quoted string", workflow("on: \"workflow_dispatch\"\n"),
         "the top-level `on:` is a quoted string"),
        ("`on:` as a flow sequence", workflow("on: [pull_request, workflow_dispatch]\n"),
         "the top-level `on:` is a flow sequence"),
        ("`on:` as a flow mapping", workflow("on: {}\n"),
         "line 4: the top-level `on:` is a flow mapping, '{}', not a block mapping"),
        ("`on:` as an indented block sequence",
         workflow("on:\n  - pull_request\n  - workflow_dispatch\n"),
         "line 5: the top-level `on:` holds a block sequence"),
        ("`on:` as a block sequence at column 0",
         workflow("on:\n- pull_request\n- workflow_dispatch\n"),
         "line 5: the top-level `on:` holds a block sequence"),
        ("`on:` as a block scalar", workflow("on: |\n  workflow_dispatch\n"),
         "the top-level `on:` is a block scalar"),
        ("`on:` with nothing beneath it", workflow("on:\n"),
         "line 4: the top-level `on:` has nothing beneath it"),
        # Refused at the next line, before the second `on:` could be named instead.
        ("`on:` with nothing beneath it before a second `on:`",
         workflow("on:\nname: x\non:\n  workflow_dispatch: {}\n"),
         "line 4: the top-level `on:` has nothing beneath it"),
        ("no top-level `on:`", workflow(""), "there is no top-level `on:` key"),
        ("a second top-level `on:`",
         workflow("on:\n  workflow_dispatch: {}\non:\n  pull_request:\n"),
         "line 6: a second top-level `on:` key; the first is at line 4"),
        ("a double-quoted `on` key", workflow("\"on\":\n  workflow_dispatch: {}\n"),
         "the top-level key is written '\"on\"'; only the plain key `on` is read"),
        ("an `on` key in another case", workflow("On:\n  workflow_dispatch: {}\n"),
         "the top-level key is written 'On'; only the plain key `on` is read"),
        ("a double-quoted `workflow_dispatch` key",
         workflow("on:\n  \"workflow_dispatch\": {}\n"),
         "the key under `on:` is written '\"workflow_dispatch\"'; only the plain key"),
        ("a single-quoted `workflow_dispatch` key",
         workflow("on:\n  'workflow_dispatch':\n"),
         "the key under `on:` is written \"'workflow_dispatch'\"; only the plain key"),
        ("a `workflow_dispatch` key in another case",
         workflow("on:\n  Workflow_Dispatch: {}\n"),
         "the key under `on:` is written 'Workflow_Dispatch'"),
        ("a second `workflow_dispatch` key",
         workflow("on:\n  workflow_dispatch:\n  workflow_dispatch: {}\n"),
         "line 6: a second `workflow_dispatch:` under `on:`; the first is at line 5"),
        ("`workflow_dispatch:` with a plain value", workflow("on:\n  workflow_dispatch: true\n"),
         "`workflow_dispatch:` under `on:` is a plain string, 'true'; only no value"),
        ("`workflow_dispatch:` with a flow sequence",
         workflow("on:\n  workflow_dispatch: [inputs]\n"),
         "`workflow_dispatch:` under `on:` is a flow sequence, '[inputs]'; only no value"),
        ("`workflow_dispatch:` holding a block sequence",
         workflow("on:\n  workflow_dispatch:\n    - inputs\n"),
         "line 6: `workflow_dispatch:` holds a block sequence"),
        ("an anchor on `on:`", workflow("on: &triggers\n  workflow_dispatch: {}\n"),
         "line 4 is outside the forms this check reads (an anchor"),
        ("a top level indented past column 0", "  on:\n    workflow_dispatch: {}\n",
         "line 1: the document's top level is not a block mapping at column 0"),
        ("a second document", WORKFLOW + "---\non:\n  pull_request:\n",
         "a YAML directive or document marker"),
        # The target's path holds something other than a regular file of UTF-8 text.
        ("a directory at the path of checks.yml", DIRECTORY,
         "it is not a regular file (mode 040000, tree)"),
        ("bytes that are not UTF-8", WORKFLOW.encode() + b"# \xff\n", "it is not valid UTF-8"),
        ("a lone CR", workflow("on:\n  workflow_dispatch: {}\r  pull_request:\n"),
         "line 5 has the character U+000D, which is outside the forms this check reads"),
        # Indentation that opens no block: a dedent to a column no open collection uses (the
        # three examples from QA round 1), and lines deeper than a line that opened no block.
        ("a key dedenting below `inputs:` to a column no mapping opened",
         workflow("on:\n  workflow_dispatch:\n      inputs:\n    bogus:\n"),
         "line 7 is outside the forms this check reads (its indentation, column 5, is not "
         "that of any block mapping or sequence still open there)"),
        # The second example's `inputs: {}` is now refused first; its variant below keeps the
        # dedent with a block mapping under `inputs:`.
        ("a key dedenting below a flow `inputs:` to a column no mapping opened",
         workflow("on:\n  workflow_dispatch:\n      inputs: {}\n    foo: {}\n"),
         "line 6: `inputs:` under `workflow_dispatch:` is a flow mapping, '{}'; only a block "
         "mapping beneath it is read"),
        ("a key dedenting below a block `inputs:` to a column no mapping opened",
         workflow("on:\n  workflow_dispatch:\n      inputs:\n        a: {}\n    foo: {}\n"),
         "line 8 is outside the forms this check reads (its indentation, column 5, is not"),
        ("a key in a job dedenting to a column no mapping opened",
         WORKFLOW_HEAD + "on:\n  workflow_dispatch: {}\n\njobs:\n  gates:\n    a: 1\n   b: 2\n",
         "line 10 is outside the forms this check reads (its indentation, column 4, is not"),
        ("a key under `on:` less indented than the first",
         workflow("on:\n    workflow_dispatch: {}\n  pull_request:\n"),
         "line 6 is less indented than the first key under `on:`, at column 5"),
        ("a key under `on:` deeper than a key with a value",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request: x\n    types: [opened]\n"),
         "line 7: a scalar from an earlier line continues onto this more indented line"),
        ("a key after `on:` deeper than a key with a value",
         workflow("on:\n  workflow_dispatch: {}\nconcurrency: x\n  group: y\n"),
         "line 7: a scalar from an earlier line continues onto this more indented line"),
        ("a line that is neither a key nor a sequence entry",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n    opened\n"),
         "line 7 is outside the forms this check reads (a line that is neither a key nor"),
        ("a sequence entry among the keys under `on:`",
         workflow("on:\n  workflow_dispatch: {}\n  - pull_request\n"),
         "line 6: a sequence entry among the keys of the top-level `on:`"),
        ("a sequence entry among a deeper mapping's keys",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n    types: [opened]\n    - x\n"),
         "line 8 is outside the forms this check reads (a sequence entry among the keys of "
         "a block mapping)"),
        ("a key among a block sequence's entries",
         workflow("on:\n  workflow_dispatch: {}\n  schedule:\n    - cron: x\n    other: y\n"),
         "line 8 is outside the forms this check reads (a key among the entries of a block "
         "sequence)"),
        ("a sequence entry at the top level", WORKFLOW_HEAD + "- x\n" + WORKFLOW_ON,
         "line 4: the document's top level is not a block mapping"),
        ("`on:` with nothing beneath it at the end of the file", WORKFLOW_HEAD + "on:\n",
         "line 4: the top-level `on:` has nothing beneath it"),
        # Block scalars.
        ("a block scalar line less indented than its content but more than its key",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n    types: |\n        opened\n"
                  "      closed\n"),
         "line 9 is outside the forms this check reads (a line less indented than its "
         "block scalar's content but more than the key or dash that opened it)"),
        ("a blank line before a block scalar's content holding more spaces than it",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n    types: |\n          \n"
                  "        opened\n"),
         "line 8 is outside the forms this check reads (a blank line at the start of a "
         "block scalar holding more spaces"),
        ("a block scalar header with an indentation indicator",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request: |2\n    x\n"),
         "line 6 is outside the forms this check reads (a block scalar header with an "
         "indentation indicator"),
        # What `workflow_dispatch:` may hold.
        ("a key other than `inputs:` under `workflow_dispatch:`",
         workflow("on:\n  workflow_dispatch:\n    bogus: 1\n"),
         "line 6: the key under `workflow_dispatch:` is written 'bogus'; only the plain key "
         "`inputs` is read there"),
        ("a quoted `inputs` key under `workflow_dispatch:`",
         workflow("on:\n  workflow_dispatch:\n    \"inputs\": {}\n"),
         "line 6: the key under `workflow_dispatch:` is written '\"inputs\"'"),
        ("a second `inputs:` under `workflow_dispatch:`",
         workflow("on:\n  workflow_dispatch:\n    inputs:\n      a: {}\n    inputs:\n"),
         "line 8: a second `inputs:` under `workflow_dispatch:`; the first is at line 6"),
        ("`inputs:` with a plain value", workflow("on:\n  workflow_dispatch:\n    inputs: foo\n"),
         "line 6: `inputs:` under `workflow_dispatch:` is a plain string, 'foo'; only a block "
         "mapping beneath it is read"),
        ("`inputs:` with a block scalar",
         workflow("on:\n  workflow_dispatch:\n    inputs: |\n      a\n"),
         "line 6: `inputs:` under `workflow_dispatch:` is a block scalar"),
        ("`inputs:` with nothing beneath it before another key",
         workflow("on:\n  workflow_dispatch:\n    inputs:\n  pull_request:\n"),
         "line 6: `inputs:` under `workflow_dispatch:` has nothing beneath it"),
        ("`inputs:` with nothing beneath it at the end of the file",
         WORKFLOW_HEAD + "on:\n  workflow_dispatch:\n    inputs:\n  # end\n",
         "line 6: `inputs:` under `workflow_dispatch:` has nothing beneath it"),
        ("`inputs:` holding a block sequence",
         workflow("on:\n  workflow_dispatch:\n    inputs:\n      - a\n"),
         "line 7: `inputs:` under `workflow_dispatch:` holds a block sequence"),
        ("`inputs:` holding a block sequence at its own column",
         workflow("on:\n  workflow_dispatch:\n    inputs:\n    - a\n"),
         "line 7: `inputs:` under `workflow_dispatch:` holds a block sequence"),
        ("`workflow_dispatch:` holding a block sequence at its own column",
         workflow("on:\n  workflow_dispatch:\n  - inputs\n"),
         "line 6: `workflow_dispatch:` holds a block sequence"),
        # Lines in forms the line model does not list.
        ("a tab", workflow("on:\n  workflow_dispatch: {}\n  pull_request:\t{}\n"),
         "line 6 is outside the forms this check reads (a tab"),
        ("a quoted key that is not a plain name",
         workflow("on:\n  workflow_dispatch: {}\n  \"pull request\": {}\n"),
         "line 6 is outside the forms this check reads (a quoted key that is not a plain"),
        ("an alias", workflow("on:\n  workflow_dispatch: *trigger\n"),
         "line 5 is outside the forms this check reads (an alias (*)"),
        ("a tag", workflow("on:\n  workflow_dispatch: !!map {}\n"),
         "line 5 is outside the forms this check reads (a tag (!)"),
        ("a sequence entry on its key's line", valued("- opened"),
         FORMS_6 + "a value starting with '-'"),
        ("a quoted scalar running past its line", valued("\"opened"),
         FORMS_6 + "a quoted scalar that runs past"),
        ("text after a flow collection", workflow("on:\n  workflow_dispatch: {} x\n"),
         "line 5 is outside the forms this check reads (text follows a flow collection"),
        ("text after a quoted scalar", valued("\"opened\" x"),
         FORMS_6 + "text follows a quoted scalar"),
        ("a plain scalar holding ': '", valued("a: b"),
         FORMS_6 + "a plain scalar holding ': '"),
        # QA round 2: each condition below was untested or missing.
        ("a plain scalar ending in ':'", valued("value:"),
         FORMS_6 + "a plain scalar holding ': ' or ending in ':'"),
        ("a '#' in a plain scalar with no space before it", valued("a#b"),
         FORMS_6 + "a '#' in a plain scalar with no space before it"),
        ("a '#' right after a closed quoted scalar", valued("'x'#c"),
         FORMS_6 + "text follows a quoted scalar"),
        ("a '#' right after `{}`", workflow("on:\n  workflow_dispatch: {}#c\n"),
         "line 5 is outside the forms this check reads (text follows a flow collection"),
        ("a '#' right after a flow sequence", valued("[a]#c"),
         FORMS_6 + "text follows a flow collection"),
        ("a backslash in a double-quoted value", valued("\"\\q\""),
         FORMS_6 + "a backslash in a double-quoted scalar"),
        ("a backslash in a double-quoted sequence entry",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request:\n    - \"C:\\dir\"\n"),
         "line 7 is outside the forms this check reads (a backslash in a double-quoted scalar"),
        ("a backslash in a double-quoted key",
         workflow("on:\n  workflow_dispatch: {}\n  \"a\\b\": x\n"),
         FORMS_6 + "a backslash in a double-quoted scalar"),
        ("a plain key of 1,025 characters",
         workflow("on:\n  workflow_dispatch: {}\n  " + "k" * 1025 + ": x\n"),
         FORMS_6 + "a key spanning 1025 characters before its ':', more than the 1,024"),
        ("a quoted key spanning 1,025 characters with the spaces before its ':'",
         workflow("on:\n  workflow_dispatch: {}\n  \"" + "k" * 1020 + "\"   : x\n"),
         FORMS_6 + "a key spanning 1025 characters before its ':'"),
        # Each range or character of the refused set.
        *[(f"the character U+{c:04X}",
           workflow("on:\n  workflow_dispatch: {}\n  # a" + chr(c) + "b\n"),
           f"line 6 has the character U+{c:04X}, which is outside the forms this check reads")
          for c in (0x00, 0x7F, 0x85, 0x2028, 0x2029, 0xFEFF, 0xFFFE, 0xFFFF)],
        # Directives and document markers: only one line that is exactly `---`, before the
        # first structural line, is read.
        ("a directive", "%YAML 1.2\n---\n" + WORKFLOW,
         "line 1: a YAML directive or document marker"),
        ("a `...` marker", WORKFLOW + "...\n", "line 20: a YAML directive or document marker"),
        ("a `...` marker with a comment", WORKFLOW + "... # end\n",
         "line 20: a YAML directive or document marker"),
        ("a leading `---` with a comment", "--- # c\n" + WORKFLOW,
         "line 1: a YAML directive or document marker"),
        ("an indented leading `---`", "  ---\n" + WORKFLOW,
         "line 1: a YAML directive or document marker"),
        ("a second leading `---`", "---\n---\n" + WORKFLOW,
         "line 2: a YAML directive or document marker"),
        # Each indicator a plain scalar may not start with.
        *[(f"a value starting with {start!r}", valued(start),
           FORMS_6 + f"a value starting with {start[0]!r}")
          for start in ("?x", "%x", "@x", "`x", ",x", "]x", "}x", "-", ": x", ":")],
        # Flow collections: only `{}` and a one-line `[a, b]` list of names are read.
        *[(f"the flow collection {flow!r}", valued(flow), FORMS_6 + FLOW_REFUSED)
          for flow in ("[a,,b]", "[a, , b]", "[, a]", "[a, ]", "[- a]", "[]", "[a,b]",
                       "[a,  b]", "[ a]", "[a ]", "[\"a\"]", "['a']", "[a #b]", "[a, [b]]",
                       "[a: b]", "[.a]", "[-a]", "[a b]", "[a, b", "[*opened]", "[\"opened]",
                       "{a: b: c}", "{\"a\" \"b\"}", "{: }", "{ }", "{a: [b,,c]}", "{a: b}",
                       "{]", "{")],
        ("a flow sequence over two lines",
         workflow("on:\n  workflow_dispatch: {}\n  pull_request: [a,\n    b]\n"),
         FORMS_6 + FLOW_REFUSED),
        ("`on:` as a non-empty flow mapping", workflow("on: {workflow_dispatch: {}}\n"),
         "line 4 is outside the forms this check reads (" + FLOW_REFUSED),
    ]
    for name, text, needle in refused:
        other = tmp / f"dispatch{COUNT[0]}"
        merges = build(other, checks=text)
        expect(f"a target with {name} in checks.yml is refused",
               release(other, merges[11], "v1.0.11", None, tmp / f"dispatch-out{COUNT[0]}"), 1,
               needle, NEEDS_TRIGGER)

    # Checks 2 and 3: the tag.
    expect("a tag that is not v plus VERSION at the target is refused",
           release(repo, c[13], "v1.0.14", "v1.0.11", tmp / "wrongtag"), 1,
           "is not `v` plus VERSION at the target, v1.0.13")
    expect("a tag that already exists locally is refused",
           release(repo, c[11], "v1.0.11", None, tmp / "exists"), 1,
           "already exists locally", "--first was given")
    expect("a previous tag that does not exist locally cannot be checked",
           release(repo, c[13], "v1.0.13", "v1.0.12", tmp / "absent"), 2,
           "the previous tag 'v1.0.12' is not a local v1.0.<digits> tag")
    git(repo, "tag", "v1.0.10", c[10])
    expect("a previous tag that is not the highest local release tag is refused",
           release(repo, c[13], "v1.0.13", "v1.0.10", tmp / "nothighest"), 1,
           "is not the highest-numbered local release tag; v1.0.11 is")
    # With no ancestor to start from, the range is empty, so that finding comes too; a valid
    # range always holds the target's own merge, so it cannot arise alone.
    git(repo, "tag", "v1.0.20", side)
    expect("a previous tag that is not an ancestor of the target is refused",
           release(repo, c[13], "v1.0.13", "v1.0.20", tmp / "notancestor"), 1,
           "is not an ancestor of the target", "not numbered strictly above",
           "no merged pull request was found in the release's range")

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
    # A previous release that was not the last merge of its UTC day: #12 merged after it on
    # 2026-10-02 and sits under that date, which the later notes, taking only the dates after
    # the previous release's, would leave out.
    repo = tmp / "sameday"
    c = build(repo, history=[HISTORY[0], HISTORY[1], (12, "2026-10-02T10:00:00Z", "2026-10-02"),
                             HISTORY[3], HISTORY[4]])
    git(repo, "tag", "v1.0.11", c[11])
    expect("a range pull request merged on the previous release's UTC date is refused",
           release(repo, c[13], "v1.0.13", "v1.0.11", tmp / "sd"), 1,
           "#12 (", "merged on 2026-10-02 UTC, which is not after the previous release's "
           "2026-10-02 and on or before the target's 2026-10-03", absent=("#13 (",))
    expect("a target whose UTC date is not after the previous release's is refused",
           release(repo, c[12], "v1.0.12", "v1.0.11", tmp / "sd12"), 1,
           "the target's UTC date 2026-10-02 is not after the previous release's 2026-10-02")

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
        ("a suite with no shell-block pass line refuses the release", UNLINTED_SUITE,
         "printed no shell-block pass line naming a shellcheck version"),
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
    repo = tmp / "othershellcheck"
    c = build(repo, suite=OTHER_SHELLCHECK_SUITE)
    expect("a shellcheck other than CI's pin passes, and the pass line names it uncompared",
           release(repo, c[11], "v1.0.11", None, tmp / "othershellcheck-out"), 0, OK,
           "reported shellcheck 0.10.0, which this check does not compare with CI's pinned "
           "SHELLCHECK_VERSION", RECORDED)

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
