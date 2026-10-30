#!/usr/bin/env python3
"""Check that the generated files in a commit match a fresh build of that commit.

WHAT THIS CATCHES: two findings closed on 2026-09-28. F-PLUGIN-MANIFEST-PARTIAL-STAGE is a
plugin bundle rebuilt in the working tree and only partly staged, so the commit carried
generated files that no build of that commit produces. F-VERSION-BUMP-NO-REGEN is a VERSION
bump committed without the plugin/plugin.json it regenerates. The two staleness gates in
tools/run_all_checks.sh rebuild site/llms-full.txt and plugin/ in the WORKING TREE and
compare, so they pass whenever the working tree is right, including when the rebuilt files
were never committed. CI checks out the commit, so there those gates already decide the
commit; this gate gives a local run after committing the same answer before a push.

WHAT IT CHECKS, for one commit (HEAD unless --rev names another):

- the commit's tree is exported with `git archive` into a new temporary directory, which is
  not a Git repository, so nothing in the working tree, the index or the untracked files is
  read from the export;
- plugin/plugin.json as committed is a JSON object whose top-level "version" is a string equal
  to VERSION as committed, read the way scripts/build-plugin.sh reads it (`$(cat VERSION)`,
  which drops trailing newlines). This runs before any build, so a bump without a rebuild is
  reported in those words and not only as a changed file;
- unless the rebuild is skipped as below, scripts/build-llms-full.sh and then
  scripts/build-plugin.sh run in the export, the scripts and order the staleness gates use,
  and each must exit 0;
- site/llms-full.txt and every file under plugin/ are then compared, byte for byte, with what
  the commit carried. A file the build changes, creates or removes is a finding, and a
  symbolic link is compared by its target.

WHEN IT DOES NOT REBUILD: when the commit is HEAD and `git status` reports nothing, no staged,
modified or untracked file, the working tree is the commit, and the two staleness gates, which
run earlier in tools/run_all_checks.sh, have already rebuilt exactly this commit. The gate then
checks the version and stops, which saves the minutes the two builds take; that is the CI case.
Run on its own with a clean tree, it relies on those staleness gates and says so in its ok
line. Any staged, modified or untracked file, a --rev other than HEAD, a `git status` that
cannot run, or --rebuild makes it rebuild the export.

WHAT IT DOES NOT CHECK: the index. A run before committing checks the previous commit, which
is why CONTRIBUTING.md says to run the suite again after committing; uncommitted edits stay
with the working-tree staleness gates. It does not check file modes, whether VERSION names the
right pull request, which no offline gate can know, or any generated file other than
site/llms-full.txt and plugin/. `git archive` applies the export-ignore and export-subst
attributes; .gitattributes sets neither today, and one set on a build input would make the
export differ from the commit.

Deterministic and offline: `git archive` and `git status` read the local repository, and the
builds read only the export. Exit 0 is a pass, 1 a finding, and 2 a commit that could not be
checked.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

LLMS_FULL = "site/llms-full.txt"
PLUGIN = "plugin"
MANIFEST = "plugin/plugin.json"
BUILDS = ("scripts/build-llms-full.sh", "scripts/build-plugin.sh")
REMEDY = ("run bash scripts/build-llms-full.sh and bash scripts/build-plugin.sh, then commit "
          "every file they change")


class CannotCheck(Exception):
    """A Git step failed, so nothing was compared."""


def git(root, *args):
    """Run git in root and return its standard output as bytes."""
    try:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotCheck(f"git {args[0]} could not run: {exc}") from exc
    if done.returncode:
        detail = done.stderr.decode("utf-8", "replace").strip() or f"exit {done.returncode}"
        raise CannotCheck(f"git {args[0]} failed: {detail}")
    return done.stdout


def resolve(root, rev):
    """The full id of the commit rev names in root."""
    if not rev or rev.startswith("-"):
        raise CannotCheck(f"{rev!r} is not a revision")
    try:
        commit = git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    except CannotCheck as exc:
        raise CannotCheck(f"{rev!r} does not name a commit in {root} ({exc})") from exc
    return commit.decode("ascii", "replace").strip()


def export(root, commit, dest):
    """Unpack the tree of commit under dest."""
    data = git(root, "archive", "--format=tar", commit)
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            tar.extractall(dest, filter="data")
    except (tarfile.TarError, OSError) as exc:
        raise CannotCheck(f"cannot unpack the export of {commit[:12]}: {exc}") from exc


def worktree_is_commit(root, commit):
    """Whether HEAD is commit and git status reports no staged, modified or untracked file."""
    if resolve(root, "HEAD") != commit:
        return False
    status = git(root, "--no-optional-locks", "status", "--porcelain=v1", "-z",
                 "--untracked-files=all")
    return status == b""


def entry(path):
    """What a generated path holds, or None when it is absent or a directory."""
    if path.is_symlink():
        return ("symbolic link", os.readlink(path))
    if path.is_file():
        return ("file", path.read_bytes())
    return None


def snapshot(root):
    """Each generated file under root, by its slash-separated relative path."""
    found = {}
    item = entry(root / LLMS_FULL)
    if item is not None:
        found[LLMS_FULL] = item
    base = root / PLUGIN
    if base.is_dir() and not base.is_symlink():
        for path in sorted(base.rglob("*")):
            item = entry(path)
            if item is not None:
                found[path.relative_to(root).as_posix()] = item
    return found


def differences(committed, rebuilt):
    """One finding per generated path that a fresh build changes, creates or removes."""
    findings = []
    for path in sorted(committed.keys() | rebuilt.keys()):
        if path not in rebuilt:
            findings.append(f"{path} is committed, and a fresh build of the commit removes it")
        elif path not in committed:
            findings.append(f"{path} is not committed, and a fresh build of the commit "
                            "creates it")
        elif committed[path] != rebuilt[path]:
            findings.append(f"{path} as committed differs from a fresh build of the commit")
    return findings


def version_findings(version_text, manifest_text):
    """Findings for the committed plugin.json version against the committed VERSION."""
    version = version_text.rstrip("\n")
    try:
        data = json.loads(manifest_text)
    except ValueError as exc:
        return [f"{MANIFEST} as committed is not JSON: {exc}"]
    if not isinstance(data, dict) or not isinstance(data.get("version"), str):
        return [f'{MANIFEST} as committed has no top-level string "version"']
    if data["version"] != version:
        return [f"{MANIFEST} as committed names version {data['version']!r} but VERSION as "
                f"committed is {version!r}; {REMEDY}"]
    return []


def build_findings(tree):
    """Run both builds in the export; a finding for the first one that does not exit 0."""
    for script in BUILDS:
        try:
            done = subprocess.run(["bash", script], cwd=tree, capture_output=True, text=True,
                                  errors="replace", timeout=1800)
        except (OSError, subprocess.SubprocessError) as exc:
            return [f"{script} could not run on the commit: {exc}"]
        if done.returncode:
            tail = " | ".join((done.stderr.strip() or done.stdout.strip()).splitlines()[-3:])
            return [f"{script} exited {done.returncode} on the commit: {tail}"]
    return []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("root", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--rev", default="HEAD", help="the commit to check (default HEAD)")
    parser.add_argument("--rebuild", action="store_true",
                        help="rebuild the export even when the working tree is the commit")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    with tempfile.TemporaryDirectory(prefix="generated-committed.") as directory:
        tree = Path(directory)
        try:
            commit = resolve(root, args.rev)
            export(root, commit, tree)
        except CannotCheck as exc:
            print(f"  FAIL  cannot check the committed generated files: {exc}")
            return 2
        label = f"commit {commit[:12]}"
        findings = []
        version = None
        try:
            version_text = (tree / "VERSION").read_text(encoding="utf-8")
            manifest_text = (tree / MANIFEST).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"cannot read VERSION or {MANIFEST} as committed: {exc}")
        else:
            findings += version_findings(version_text, manifest_text)
            version = version_text.rstrip("\n")
        rebuild = args.rebuild
        if not rebuild:
            try:
                rebuild = not worktree_is_commit(root, commit)
            except CannotCheck:
                rebuild = True
        committed = {}
        if rebuild:
            try:
                committed = snapshot(tree)
                failed = build_findings(tree)
                findings += failed
                if not failed:
                    changed = differences(committed, snapshot(tree))
                    if changed:
                        changed[-1] += f"; {REMEDY}"
                    findings += changed
            except OSError as exc:
                findings.append(f"cannot read the generated files of the export: {exc}")
        if findings:
            for finding in findings:
                print(f"  FAIL  {label}: {finding}")
            return 1
        if rebuild:
            files = sum(1 for path in committed if path.startswith(PLUGIN + "/"))
            print(f"  ok    {label}: {MANIFEST} names VERSION {version}, and {LLMS_FULL} and "
                  f"{files} files under {PLUGIN}/ match a fresh build of the commit")
        else:
            print(f"  ok    {label}: {MANIFEST} names VERSION {version}; the working tree is "
                  "this commit with no change, so the working-tree staleness gates in "
                  "tools/run_all_checks.sh decide its generated files (--rebuild rebuilds "
                  "it here)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
