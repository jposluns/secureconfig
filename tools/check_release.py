#!/usr/bin/env python3
"""Check a release candidate offline before it is published.

A release is a GitHub release on a tag `v1.0.<N>` that names one merge commit on `main`, with
four assets: `llms-full.txt`, the plugin tarball, the full release notes and `SHA256SUMS`.
CONTRIBUTING.md's "Releasing" section gives the procedure and DECISIONS.md the rulings of
2026-11-01. This tool is run by that procedure, not on every pull request; its self-test,
tools/test_release.py, runs in tools/run_all_checks.sh so the shipped rule is tested there.

WHAT THIS CATCHES: a release whose tag, notes or assets do not match the commit it names. A
tag one number off, a week whose only merges are out of order and so share a `VERSION`, an
entry filed under the wrong date that would put a change in the wrong release's notes, a
target whose own entry is missing, or an asset rebuilt from a working tree rather than the
commit would each be published unnoticed, and a published tag is never moved.

WHAT IT CHECKS, reading only local git objects, for a target commit, a tag, the previous
release's tag (or --first) and a release directory holding `body.md` and `assets/`:

1. The target is a full commit id on the first-parent chain of `main` (--main), and its
   subject begins `Merge pull request #N from `. It is the last first-parent merge of its UTC
   date on that chain, and that UTC date is before today's, so every CHANGELOG date section
   falls wholly in one release.
2. The tag is `v` plus `VERSION` at the target, `VERSION` is `1.0.<digits>` once trailing
   newlines are dropped (as scripts/build-plugin.sh reads it), and `plugin/plugin.json` at the
   target carries the same version.
3. The tag does not exist locally. With --first, no `v1.0.<N>` tag exists locally. With
   --previous, that tag exists locally, is the highest-numbered `v1.0.<N>` tag, and its number
   is strictly lower than the new tag's.
4. The previous tag's commit is an ancestor of the target on its first-parent chain.
5. `CHANGELOG.md` at the target passes the rules of tools/check_changelog_format.py, and every
   pull request merged on the first-parent range from the previous tag (the whole chain for a
   first release) to the target is referenced, with no newest-PR exemption, so a target whose
   own entry is missing is refused.
6. With --previous, each pull request merged in the range is referenced under the dated
   heading equal to its merge commit's UTC committer date, and that date is after the
   previous release's UTC date and on or before the target's, so the notes, which take only
   those dates, leave none of them out. A first release extracts no sections, so this is not
   applied to it.
7. The notes asset and `body.md` equal, byte for byte, the ones regenerated from the target;
   the body holds the range's merged pull requests, so its list cannot drift from the range.
8. `llms-full.txt` equals `site/llms-full.txt` at the target, the tarball equals a rebuild from
   `git archive` of the target's `plugin/` (built twice, and the two must agree), `SHA256SUMS`
   equals its rebuild and verifies every asset, and `assets/` holds nothing else.
9. Only when 1 to 8 pass: tools/run_all_checks.sh, run in a `git worktree` of the target,
   exits 0, ends with "All gates passed.", prints the shell-block gate's pass line, and prints
   no line beginning `  FAIL  ` and no line beginning `  SKIP  ` but two. A line is read as a
   FAIL or a SKIP only by that prefix. A SKIP means a lint or comparison did not run as CI
   runs it, such as a missing shellcheck, so it is refused here. The first accepted is
   tools/gen_aiqt_settings.py's line for an absent .claude/settings.json, which is untracked,
   so every checkout prints it. The second is the suite's advisory line saying the local
   python3 differs from CI's pinned PYTHON_VERSION: CI's pinned Python is then covered by the
   online `gates` check on the target, which the procedure records, and the pass line says
   so. Every other SKIP, including a Python comparison that could not run, is refused. The pass line names the shellcheck version the
   shell-block gate reported, which this check does not compare with CI's pinned
   SHELLCHECK_VERSION, so CI's pinned shellcheck, like its Python, is covered by the online
   `gates` check on the target. This whole-corpus run is the release's explicit need and is
   not repeated per review round.

WHAT IT CANNOT CHECK: whether `gates` passed on GitHub for the target's push to `main`. That is
an online step of the procedure; --gates-check-run takes the id it found only to print it in
the body and the pass line, which says the result is recorded, not verified. It also cannot see
a merge, tag or release that exists only on GitHub, so the procedure fetches `main` and the
`v*` tags first, and it does not check that a mention of a pull request in a section is that
pull request's own entry.

THE RELEASE DIRECTORY: --build writes it into a new directory: `body.md`, the release body, and
`assets/` with `llms-full.txt`, `secureconfig-plugin-v1.0.<N>.tar.gz`,
`RELEASE-NOTES-v1.0.<N>.md` and `SHA256SUMS`. It refuses when any of checks 1 to 6 fails, and
it does not run the suite. The notes are a heading and one paragraph, then each dated section
in the range, newest first, from its heading to its last non-empty line, separated by one
empty line. The tarball is `git archive --format=tar --prefix=secureconfig-plugin-v1.0.<N>/`
of `plugin` with tar.umask 0002, compressed by Python's gzip at level 9 with mtime 0, so its
bytes repeat for one git, Python and zlib. `git archive` applies export-ignore and export-subst
attributes; .gitattributes sets neither today.

Exit 0 is a pass, 1 a finding, and 2 a candidate that could not be checked.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_changelog_format import HEADING, check as format_findings  # noqa: E402
from check_changelog_prs import MERGE_COMMIT, merged_number, referenced  # noqa: E402

REPOSITORY = "https://github.com/jposluns/secureconfig"
CHANGELOG = "CHANGELOG.md"
SUITE = "tools/run_all_checks.sh"
SUITE_PASS = "All gates passed."
# The SKIPs a release accepts. .claude/settings.json is untracked, so every checkout, including
# CI's, prints the first, and CLAUDE.md records those hooks as inert here (backlog row 3.6).
ALLOWED_SKIPS = ("  SKIP  .claude/settings.json absent; AIQT hooks are not activated",)
# The second is the suite's advisory Python comparison, in its exact wording: CI's pinned Python
# is covered by the online `gates` check on the target, which the procedure records.
PYTHON_SKIP = re.compile(r"  SKIP  python3 ([0-9]+\.[0-9]+\.[0-9]+) differs from CI's pinned "
                         r"PYTHON_VERSION ([0-9]+\.[0-9]+\.[0-9]+); html\.parser behaviour may "
                         r"differ, so a local green predicts CI less well")
# tools/check_shell_blocks.py's pass line, which names the shellcheck version that ran. A
# passing suite always prints it, since a missing shellcheck prints a SKIP instead.
SHELL_PASS = re.compile(r"  ok    [0-9]+ bash blocks in [0-9]+ guides parse and pass "
                        r"shellcheck (\S+) at \S.*")
VERSION_SHAPE = re.compile(r"1\.0\.([0-9]+)")
TAG_SHAPE = re.compile(r"v1\.0\.([0-9]+)")
FULL_ID = re.compile(r"[0-9a-f]{40}")
RUN_ID = re.compile(r"[0-9]+")


class CannotCheck(Exception):
    """A git step failed, so the candidate was not checked."""


def git(root, *args, binary=False):
    """Run git in root and return its standard output."""
    try:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=600)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotCheck(f"git {args[0]} could not run: {exc}") from exc
    if done.returncode:
        detail = done.stderr.decode("utf-8", "replace").strip() or f"exit {done.returncode}"
        raise CannotCheck(f"git {' '.join(args[:2])} failed: {detail}")
    return done.stdout if binary else done.stdout.decode("utf-8")


def succeeds(root, *args):
    """Whether a git command exits 0."""
    try:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=600)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotCheck(f"git {args[0]} could not run: {exc}") from exc
    return done.returncode == 0


def utc_date(seconds):
    return datetime.datetime.fromtimestamp(int(seconds), datetime.timezone.utc).date().isoformat()


def first_parent(root, rev, stop=None):
    """(id, UTC committer date, subject) for each first-parent commit, newest first."""
    span = f"{stop}..{rev}" if stop else rev
    out = git(root, "log", "--first-parent", "--format=%H%x00%ct%x00%s", span, "--")
    chain = []
    for line in out.splitlines():
        commit, seconds, subject = line.split("\0", 2)
        chain.append((commit, utc_date(seconds), subject))
    return chain


def at_target(root, target, path):
    return git(root, "show", f"{target}:{path}", binary=True)


def release_tags(root):
    """Every local tag shaped `v1.0.<N>`, by number."""
    out = git(root, "for-each-ref", "--format=%(refname:strip=2)", "refs/tags/")
    found = {}
    for name in out.splitlines():
        match = TAG_SHAPE.fullmatch(name)
        if match:
            found[name] = int(match.group(1))
    return found


def names(tag):
    """The four asset names, in SHA256SUMS order."""
    return ("llms-full.txt", f"secureconfig-plugin-{tag}.tar.gz", f"RELEASE-NOTES-{tag}.md",
            "SHA256SUMS")


def changelog_lines(data):
    """CHANGELOG.md split on LF alone, as check_changelog_format.py reads it."""
    text = data.decode("utf-8")
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    return lines


def dated_sections(lines):
    """Each dated heading's date mapped to its lines, from the heading to the next one."""
    starts = [(i, HEADING.fullmatch(line).group(1)) for i, line in enumerate(lines)
              if HEADING.fullmatch(line)]
    sections = {}
    for k, (i, date) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        body = lines[i:end]
        while body and not body[-1].strip():
            body.pop()
        sections.setdefault(date, body)
    return sections


def tarball(root, target, tag):
    data = git(root, "-c", "tar.umask=0002", "archive", "--format=tar",
               f"--prefix=secureconfig-plugin-{tag}/", target, "plugin", binary=True)
    return gzip.compress(data, compresslevel=9, mtime=0)


def sums(files):
    return "".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n"
                   for name, data in files).encode("ascii")


def examine(root, main_ref, target, tag, previous, gates_run):
    """Findings for checks 1 to 6, and the regenerated release when they pass."""
    findings = []
    if git(root, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise CannotCheck("the repository is a shallow clone, so the merge history cannot be "
                          "read")
    if not FULL_ID.fullmatch(target):
        raise CannotCheck(f"the target {target!r} is not a full 40-character lowercase commit id")
    if not succeeds(root, "cat-file", "-e", f"{target}^{{commit}}"):
        raise CannotCheck(f"the target {target} is not a commit in {root}")
    if not RUN_ID.fullmatch(gates_run):
        raise CannotCheck(f"--gates-check-run {gates_run!r} is not a numeric check run id")

    # 1. On main's first-parent chain, a pull request merge, and the last merge of its UTC day.
    chain = first_parent(root, main_ref)
    position = next((i for i, (commit, _, _) in enumerate(chain) if commit == target), None)
    subject = git(root, "log", "-1", "--format=%s", target, "--").strip()
    merge = MERGE_COMMIT.match(subject)
    if position is None:
        findings.append(f"the target {target[:12]} is not on the first-parent chain of "
                        f"{main_ref}")
    if not merge:
        findings.append(f"the target's subject {subject!r} does not begin "
                        "`Merge pull request #N from `")
    target_date = utc_date(git(root, "log", "-1", "--format=%ct", target, "--").strip())
    if position is not None:
        for commit, date, later in chain[:position]:
            if date == target_date and merged_number(later) is not None:
                findings.append(f"the target is not the last merge of {target_date} UTC on "
                                f"{main_ref}: {commit[:12]} {later!r} merged later that day")
                break
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    if target_date >= today:
        findings.append(f"the target's UTC date {target_date} has not ended (today is {today} "
                        "UTC), so a later merge could still land under that date")

    # 2. The tag, VERSION and plugin.json agree.
    version = at_target(root, target, "VERSION").decode("utf-8", "replace").rstrip("\n")
    if not VERSION_SHAPE.fullmatch(version):
        findings.append(f"VERSION at the target is {version!r}, not 1.0.<digits>")
    if tag != f"v{version}":
        findings.append(f"the tag {tag!r} is not `v` plus VERSION at the target, v{version}")
    try:
        manifest = json.loads(at_target(root, target, "plugin/plugin.json"))
        plugin_version = manifest.get("version") if isinstance(manifest, dict) else None
    except ValueError as exc:
        plugin_version = f"(not JSON: {exc})"
    if plugin_version != version:
        findings.append(f"plugin/plugin.json at the target carries version {plugin_version!r}, "
                        f"not VERSION's {version!r}")
    shaped = TAG_SHAPE.fullmatch(tag)
    if not shaped:
        raise CannotCheck(f"the tag {tag!r} is not shaped v1.0.<digits>"
                          + (f"; {findings[0]}" if findings else ""))
    number = int(shaped.group(1))

    # 3 and 4. The tag is new, numbered above the previous release, whose commit is an ancestor.
    tags = release_tags(root)
    if succeeds(root, "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"):
        findings.append(f"the tag {tag} already exists locally; a published tag is never moved")
    previous_commit = previous_date = None
    if previous is None:
        if tags:
            findings.append(f"--first was given but {', '.join(sorted(tags))} already exists "
                            "locally; pass --previous with the last release's tag")
    else:
        if previous not in tags:
            raise CannotCheck(f"the previous tag {previous!r} is not a local v1.0.<digits> tag")
        highest = max(tags, key=tags.get)
        if tags[highest] != tags[previous]:
            findings.append(f"the previous tag {previous} is not the highest-numbered local "
                            f"release tag; {highest} is")
        if tags[previous] >= number:
            findings.append(f"the tag {tag} is not numbered strictly above the previous "
                            f"release {previous}; no release until a higher-numbered merge lands")
        previous_commit = git(root, "rev-parse", "--verify",
                              f"refs/tags/{previous}^{{commit}}").strip()
        on_chain = any(c == previous_commit for c, _, _ in first_parent(root, target)[1:])
        if not on_chain or not succeeds(root, "merge-base", "--is-ancestor", previous_commit,
                                        target):
            findings.append(f"the previous tag {previous} ({previous_commit[:12]}) is not an "
                            "ancestor of the target on its first-parent chain")
            previous_commit = None
        else:
            seconds = git(root, "log", "-1", "--format=%ct", previous_commit, "--").strip()
            previous_date = utc_date(seconds)
            if previous_date >= target_date:
                findings.append(f"the target's UTC date {target_date} is not after the previous "
                                f"release's {previous_date}")

    # 5 and 6. CHANGELOG.md at the target: format, coverage of the range, and dating.
    try:
        lines = changelog_lines(at_target(root, target, CHANGELOG))
    except (CannotCheck, UnicodeError) as exc:
        findings.append(f"{CHANGELOG} at the target cannot be read: {exc}")
        lines = []
    for line_number, message in format_findings(lines)[0]:
        findings.append(f"{CHANGELOG}:{line_number} at the target: {message}")
    sections = dated_sections(lines)
    if lines and not sections:
        findings.append(f"{CHANGELOG} at the target has no dated `## YYYY-MM-DD` heading")
    stop = previous_commit if previous is not None else None
    merged = []
    if previous is None or previous_commit is not None:
        for commit, date, line in first_parent(root, target, stop):
            pr = merged_number(line)
            if pr is not None:
                merged.append((pr, commit, date))
    if not merged:
        findings.append("no merged pull request was found in the release's range")
    refs = referenced("\n".join(lines))
    for pr, commit, date in sorted(merged):
        if pr not in refs:
            findings.append(f"#{pr} ({commit[:12]}, merged {date} UTC) is in the range but never "
                            f"referenced in {CHANGELOG} at the target")
        elif previous is not None and pr not in referenced("\n".join(sections.get(date, []))):
            findings.append(f"#{pr} ({commit[:12]}) merged on {date} UTC but is not referenced "
                            f"under `## {date}`; move its entry in a records pull request first")
        if previous_date is not None and not previous_date < date <= target_date:
            findings.append(f"#{pr} ({commit[:12]}) merged on {date} UTC, which is not after the "
                            f"previous release's {previous_date} and on or before the target's "
                            f"{target_date}, so the notes would leave it out")

    if findings:
        return findings, None

    # The release, regenerated from the target.
    numbers = sorted({pr for pr, _, _ in merged})
    pr_list = ", ".join(f"#{n}" for n in numbers)
    changelog_url = f"{REPOSITORY}/blob/{tag}/{CHANGELOG}"
    llms, tar_name, notes_name, sums_name = names(tag)
    own = f"pull request #{merge.group(1)}"
    if previous is None:
        covered = f"up to and including {target_date}"
        notes = (f"# secureconfig {tag} release notes\n\n"
                 f"This is the first tagged release of secureconfig. Its target commit is "
                 f"`{target}`, the merge of {own} on {target_date} UTC. These notes extract no "
                 f"`{CHANGELOG}` sections: the whole history up to this release is in "
                 f"`{CHANGELOG}` at the tag, {changelog_url}.\n")
        scope = (f"- This is the first tagged release. It covers the history up to and including "
                 f"{target_date} UTC, all of it in `{CHANGELOG}` at the tag.\n")
    else:
        dates = [d for d in sections if previous_date < d <= target_date]
        covered = f"after {previous_date} up to and including {target_date}"
        parts = [f"# secureconfig {tag} release notes\n\n"
                 f"Target commit `{target}`, the merge of {own}. These are the sections of "
                 f"`{CHANGELOG}` at the target for the UTC dates after {previous_date}, the date "
                 f"of {previous}, up to and including {target_date}, copied unchanged.\n"]
        parts += ["\n".join(sections[d]) + "\n" for d in dates]
        notes = "\n".join(parts)
        scope = (f"- It covers the UTC dates after {previous_date}, the date of `{previous}`, up "
                 f"to and including {target_date}.\n")
    body = (f"secureconfig {tag} is a checksummed snapshot of `main` at `{target}`, the merge "
            f"of {own}.\n\n"
            f"- Tag `{tag}`. `VERSION` and the plugin version at the target are both "
            f"`{version}`.\n"
            f"- The `gates` check of the target's push to `main`, check run {gates_run}, was "
            f"confirmed online by the publisher. The offline release check records that id and "
            f"does not verify it.\n"
            + scope +
            f"- Pull requests merged in that range ({len(numbers)}): {pr_list}.\n"
            f"- The full notes are the `{notes_name}` asset, and the history is in "
            f"`{CHANGELOG}` at the tag: {changelog_url}.\n"
            f"- The `{llms}` asset is the committed `site/llms-full.txt` at the target, "
            f"unchanged. Its repository links point at `main`, not at this tag, so they follow "
            f"the moving branch.\n"
            f"- `{sums_name}` covers the other three assets; check a download with "
            f"`sha256sum -c {sums_name}`.\n")
    first_build = tarball(root, target, tag)
    if tarball(root, target, tag) != first_build:
        return [f"two builds of {tar_name} from the target differ, so it is not reproducible "
                "here"], None
    files = [(llms, at_target(root, target, "site/llms-full.txt")),
             (tar_name, first_build),
             (notes_name, notes.encode("utf-8"))]
    files.append((sums_name, sums(files)))
    release = {"body": body.encode("utf-8"), "files": files, "prs": numbers,
               "covered": covered, "previous": previous}
    return [], release


def compare(directory, release):
    """Findings for checks 7 and 8: the release directory against the regenerated release."""
    findings = []
    body_path = directory / "body.md"
    if not body_path.is_file():
        findings.append(f"{body_path} is missing")
    elif body_path.read_bytes() != release["body"]:
        findings.append(f"{body_path} differs from the body regenerated from the target, so its "
                        "pull request list or a stated fact does not match the range")
    assets = directory / "assets"
    expected = dict(release["files"])
    present = sorted(p.name for p in assets.iterdir()) if assets.is_dir() else []
    if not assets.is_dir():
        findings.append(f"{assets} is missing")
    for name in present:
        if name not in expected:
            findings.append(f"{assets / name} is not a release asset")
    for name, data in release["files"]:
        path = assets / name
        if not path.is_file() or path.is_symlink():
            findings.append(f"{path} is missing or not a regular file")
        elif path.read_bytes() != data:
            findings.append(f"{path} differs from its rebuild from the target")
    sums_name = release["files"][-1][0]
    sums_path = assets / sums_name
    if sums_path.is_file():
        for line in sums_path.read_bytes().decode("ascii", "replace").splitlines():
            digest, _, name = line.partition("  ")
            path = assets / name
            if name not in expected or name == sums_name or not path.is_file():
                findings.append(f"{sums_name} names {name!r}, which is not a release asset here")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                findings.append(f"{sums_name} does not verify {name}")
    return findings


def suite(root, target):
    """Findings for check 9, the accepted Python SKIP's match, and the reported shellcheck."""
    with tempfile.TemporaryDirectory(prefix="release-check.") as directory:
        tree = Path(directory) / "tree"
        git(root, "worktree", "add", "--detach", "--quiet", str(tree), target)
        try:
            # One stream, in the order written, so the last line is the suite's last line.
            done = subprocess.run(["bash", SUITE], cwd=tree, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, errors="replace",
                                  timeout=7200)
        except (OSError, subprocess.SubprocessError) as exc:
            return [f"{SUITE} could not run in a worktree of the target: {exc}"], None, None
        finally:
            git(root, "worktree", "remove", "--force", str(tree))
            git(root, "worktree", "prune")
    lines = done.stdout.splitlines()
    python = next((m for m in (PYTHON_SKIP.fullmatch(line.rstrip()) for line in lines) if m),
                  None)
    bad = [line.strip() for line in lines
           if line.startswith("  FAIL  ")
           or (line.startswith("  SKIP  ") and line.rstrip() not in ALLOWED_SKIPS
               and not PYTHON_SKIP.fullmatch(line.rstrip()))]
    last = next((line for line in reversed(lines) if line.strip()), "")
    shell = next((m for m in (SHELL_PASS.fullmatch(line.rstrip()) for line in lines) if m),
                 None)
    if done.returncode or last != SUITE_PASS or bad:
        detail = "; ".join(bad[:5]) or (last[:200] or "no output")
        finding = (f"{SUITE} in a worktree of the target exited {done.returncode} with "
                   f"{len(bad)} FAIL or SKIP lines, last line {last[:80]!r}: {detail}")
    elif not shell:
        finding = (f"{SUITE} in a worktree of the target printed no shell-block pass line "
                   "naming a shellcheck version, so its bash blocks are not shown to have been "
                   "linted")
    else:
        return [], python, shell.group(1)
    return [finding], None, None
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--main", default="main", help="the branch the target merged into")
    parser.add_argument("--target", required=True, help="the full id of the merge commit")
    parser.add_argument("--tag", required=True, help="the new tag, v plus VERSION at the target")
    first = parser.add_mutually_exclusive_group(required=True)
    first.add_argument("--previous", help="the previous release's tag")
    first.add_argument("--first", action="store_true", help="this is the first release")
    parser.add_argument("--gates-check-run", required=True,
                        help="the id of the target's gates check run, found online; printed only")
    parser.add_argument("--dir", required=True, type=Path,
                        help="the release directory, holding body.md and assets/")
    parser.add_argument("--build", action="store_true",
                        help="write the release directory, which must not exist, then stop")
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    try:
        findings, release = examine(root, args.main, args.target, args.tag, args.previous,
                                    args.gates_check_run)
        if not findings and args.build:
            directory = args.dir
            directory.mkdir()
            (directory / "assets").mkdir()
            (directory / "body.md").write_bytes(release["body"])
            for name, data in release["files"]:
                (directory / "assets" / name).write_bytes(data)
            print(f"  ok    built {args.tag} at {args.target[:12]} into {directory}: "
                  f"{len(release['prs'])} pull requests; checks 1 to 6 passed, and the release "
                  "is not yet checked: run again without --build")
            return 0
        if not findings:
            findings = compare(args.dir, release)
        suite_ran = False
        python = shellcheck = None
        if not findings and not args.build:
            findings, python, shellcheck = suite(root, args.target)
            suite_ran = True
    except (CannotCheck, OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot check the release candidate: {exc}")
        return 2
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        if not suite_ran and not args.build:
            print(f"  FAIL  {args.tag} refused; {SUITE} was not run because an earlier check "
                  "failed")
        return 1
    dated = ("each one referenced under its UTC merge date"
             if release["previous"] else "dating not checked for a first release")
    runtime = ""
    if python:
        runtime = (f" Local python3 {python.group(1)} differed from CI's pinned PYTHON_VERSION "
                   f"{python.group(2)}, so CI's pinned Python is covered by the online gates "
                   "check on the target, which the procedure records.")
    runtime += (f" Its shell-block gate reported shellcheck {shellcheck}, which this check does "
                "not compare with CI's pinned SHELLCHECK_VERSION; CI's pinned shellcheck is "
                "covered by the online gates check on the target.")
    print(f"  ok    {args.tag} at {args.target[:12]}: {len(release['prs'])} pull requests "
          f"merged {release['covered']} UTC, all in {CHANGELOG}, {dated}; notes, body and "
          f"assets match a rebuild of the target and {SUITE} passed in its worktree.{runtime} "
          f"The online gates result, check run {args.gates_check_run}, is recorded, not "
          "verified: confirm it on GitHub before publishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
