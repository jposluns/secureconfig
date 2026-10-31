#!/usr/bin/env python3
"""Exercise check_generated_committed.py through the shipped gate on throwaway repositories.

Each repository carries a guide, VERSION, plugin/plugin.json, a tracked site/index.html and
stub build scripts that do what the gate depends on the real ones doing: build-llms-full.sh
writes site/llms-full.txt from the guide, and build-plugin.sh refuses a malformed VERSION,
replaces the references directory, writes VERSION into plugin.json with the real script's sed,
and writes a MANIFEST.sha256. The repository is built and committed clean before each case
changes it.

The two finding cases reproduce how each defect reaches a commit: the working tree is rebuilt
in full, so the working-tree staleness gates pass, which each case confirms by rebuilding the
working tree and finding nothing changed, while the commit is incomplete. Each has a passing
twin that differs only in the defect and takes the same rebuild path. A case whose working
tree is clean passes --rebuild where it needs the rebuild path. The last cases fail closed,
and two record what the gate does not do: read the index, or rebuild a clean tree unasked.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent / "check_generated_committed.py"
OK = "  ok    commit "
REBUILT = "site/llms-full.txt and 3 files under plugin/ match a fresh build of the commit"
DEFERRED = "the working tree is this commit with no change"

LLMS_BUILD = r"""#!/usr/bin/env bash
set -euo pipefail
cat guide.md > site/llms-full.txt
"""

PLUGIN_BUILD = r"""#!/usr/bin/env bash
set -euo pipefail
dest=plugin/references
version=$(cat VERSION)
printf '%s' "$version" | grep -qxE '1\.0\.[0-9]+' \
  || { echo "VERSION is '$version', not 1.0.<number>; refusing to build" >&2; exit 1; }
rm -rf "$dest"
mkdir -p "$dest"
cp guide.md "$dest/guide.md"
sed -i "s/^\(  \"version\": \)\"[^\"]*\"/\1\"$version\"/" plugin/plugin.json
( cd "$dest" && sha256sum guide.md ) > "$dest/MANIFEST.sha256"
"""

PLUGIN_JSON = '{\n  "name": "fixture",\n  "version": "1.0.5",\n  "license": "CC0-1.0"\n}\n'


def environment(root):
    """The caller's environment without Git selectors, with discovery stopped above root."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CEILING_DIRECTORIES=str(root.parent))
    return env


def run(root, *command):
    done = subprocess.run(command, cwd=root, capture_output=True, text=True,
                          env=environment(root), timeout=120)
    assert done.returncode == 0, (command, done.returncode, done.stdout + done.stderr)


def git(root, *args):
    run(root, "git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args)


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(root):
    run(root, "bash", "scripts/build-llms-full.sh")
    run(root, "bash", "scripts/build-plugin.sh")


def commit(root, *paths):
    if paths:
        git(root, "add", "--", *paths)
    else:
        git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "change")


def generated(root):
    """Bytes of every generated file in the working tree."""
    files = {}
    for path in [root / "site" / "llms-full.txt", *sorted((root / "plugin").rglob("*"))]:
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def case(change, expected=0, needle=OK, *, also=(), absent=(), worktree_current=False,
         args=(), init=True):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        write(root, "scripts/build-llms-full.sh", LLMS_BUILD)
        write(root, "scripts/build-plugin.sh", PLUGIN_BUILD)
        write(root, "guide.md", "first text\n")
        write(root, "VERSION", "1.0.5\n")
        write(root, "plugin/plugin.json", PLUGIN_JSON)
        # Tracked, so site/ is in every export, as it is in the repository.
        write(root, "site/index.html", "<!doctype html>\n")
        build(root)
        if init:
            git(root, "init", "-q")
            commit(root)
        change(root)
        if worktree_current:
            # The working-tree staleness gates rebuild and compare; a rebuild that changes
            # nothing is their pass, so this case shows the commit-level gap they leave.
            before = generated(root)
            build(root)
            assert generated(root) == before, "the working tree was not current"
        done = subprocess.run([sys.executable, "-I", "-B", str(GATE), str(root), *args],
                              capture_output=True, text=True, env=environment(root),
                              timeout=900)
        output = done.stdout + done.stderr
        assert done.returncode == expected, (done.returncode, expected, output)
        for text in (needle, *also):
            assert text in output, (text, output)
        for text in absent:
            assert text not in output, (text, output)
        if expected == 0:
            assert "  FAIL  " not in output, output
    return 1


def nothing(root):
    pass


def partial_stage(stage_manifest):
    """Rebuild in full after a guide edit, and commit the rebuild with or without its MANIFEST."""
    def change(root):
        write(root, "guide.md", "second text\n")
        build(root)
        paths = ["guide.md", "site/llms-full.txt", "plugin/references/guide.md"]
        if stage_manifest:
            paths.append("plugin/references/MANIFEST.sha256")
        commit(root, *paths)
    return change


def bump(stage_manifest, stage_after=False):
    """Bump VERSION and rebuild in full, and commit with or without plugin.json."""
    def change(root):
        write(root, "VERSION", "1.0.6\n")
        build(root)
        commit(root, "VERSION", *(["plugin/plugin.json"] if stage_manifest else []))
        if stage_after:
            git(root, "add", "--", "plugin/plugin.json")
    return change


def unbuilt_guide(root):
    write(root, "guide.md", "second text\n")
    commit(root, "guide.md")


def stale_extra(root):
    write(root, "plugin/references/old.md", "a guide no build carries\n")
    commit(root)


def missing_bundle(root):
    git(root, "rm", "-q", "--", "site/llms-full.txt")
    git(root, "commit", "-q", "-m", "change")


def worktree_only(root):
    write(root, "guide.md", "uncommitted text\n")
    write(root, "plugin/references/untracked.md", "untracked\n")


def bad_version(root):
    write(root, "VERSION", "1.0.x\n")
    write(root, "plugin/plugin.json", PLUGIN_JSON.replace("1.0.5", "1.0.x"))
    commit(root)


def manifest(text):
    def change(root):
        write(root, "plugin/plugin.json", text)
        commit(root)
    return change


def init_only(root):
    git(root, "init", "-q")


def main():
    count = 0
    rebuild = ("--rebuild",)
    try:
        # Clean, both ways: with the tree clean the gate defers to the staleness gates, and
        # with --rebuild the commit is its own fresh build.
        count += case(nothing, also=("plugin/plugin.json names VERSION 1.0.5; " + DEFERRED,),
                      absent=(REBUILT,))
        count += case(nothing, args=rebuild,
                      also=("plugin/plugin.json names VERSION 1.0.5, and " + REBUILT,))

        # F-PLUGIN-MANIFEST-PARTIAL-STAGE: the working tree is current, the commit lacks the
        # rebuilt MANIFEST.sha256; the twin stages it and passes on the same rebuild path.
        count += case(partial_stage(False), expected=1, worktree_current=True,
                      needle="plugin/references/MANIFEST.sha256 as committed differs from a "
                             "fresh build of the commit; run bash scripts/build-llms-full.sh",
                      absent=("plugin/references/guide.md as committed",
                              "site/llms-full.txt as committed", "names version"))
        count += case(partial_stage(True), worktree_current=True, args=rebuild,
                      also=(REBUILT,))

        # F-VERSION-BUMP-NO-REGEN: VERSION is bumped and rebuilt in the working tree, and the
        # commit lacks plugin.json; the twin commits it and passes on the same rebuild path.
        count += case(bump(False), expected=1, worktree_current=True,
                      needle="plugin/plugin.json as committed names version '1.0.5' but "
                             "VERSION as committed is '1.0.6'",
                      also=("plugin/plugin.json as committed differs from a fresh build",))
        count += case(bump(True), worktree_current=True, args=rebuild,
                      also=("plugin/plugin.json names VERSION 1.0.6, and " + REBUILT,))

        # A guide committed with nothing rebuilt: every derived file is reported.
        count += case(unbuilt_guide, expected=1, args=rebuild,
                      needle="site/llms-full.txt as committed differs from a fresh build",
                      also=("plugin/references/guide.md as committed differs",
                            "plugin/references/MANIFEST.sha256 as committed differs"))
        # A committed file the build no longer produces, and a generated file not committed.
        count += case(stale_extra, expected=1, args=rebuild,
                      needle="plugin/references/old.md is committed, and a fresh build of the "
                             "commit removes it")
        count += case(missing_bundle, expected=1, args=rebuild,
                      needle="site/llms-full.txt is not committed, and a fresh build of the "
                             "commit creates it")

        # Uncommitted and untracked changes make the gate rebuild, and do not reach the export.
        count += case(worktree_only, also=(REBUILT,))
        # --rev selects the commit: the partial stage is HEAD, and its parent is clean.
        count += case(partial_stage(False), args=("--rev", "HEAD~1"), also=(REBUILT,))

        # A build that fails on the commit is a finding, with the build's own message.
        count += case(bad_version, expected=1, args=rebuild,
                      needle="scripts/build-plugin.sh exited 1 on the commit: VERSION is "
                             "'1.0.x', not 1.0.<number>; refusing to build",
                      absent=("names version",))
        # A manifest the version check cannot read fails on a clean tree too.
        count += case(manifest("{\n"), expected=1,
                      needle="plugin/plugin.json as committed is not JSON")
        count += case(manifest(PLUGIN_JSON.replace('  "version": "1.0.5",\n', "")),
                      expected=1,
                      needle='plugin/plugin.json as committed has no top-level string "version"')

        # Fail closed: a revision that is not a commit, an option-shaped revision, a directory
        # that is not a repository, and a repository with no commit.
        count += case(nothing, expected=2, args=("--rev", "no-such-revision"),
                      needle="  FAIL  cannot check the committed generated files: "
                             "'no-such-revision' does not name a commit")
        count += case(nothing, expected=2, args=("--rev=--output=x",),
                      needle="'--output=x' is not a revision")
        count += case(nothing, expected=2, init=False,
                      needle="  FAIL  cannot check the committed generated files: ")
        count += case(init_only, expected=2, init=False,
                      needle="'HEAD' does not name a commit")

        # Known limit: the index is not read, so a fix staged and not committed still fails.
        count += case(bump(False, stage_after=True), expected=1,
                      needle="plugin/plugin.json as committed names version '1.0.5'")
        # Known limit: with the tree clean the gate does not rebuild, so on its own it passes
        # a commit whose generated files are stale; the working-tree staleness gates, which
        # run before it in tools/run_all_checks.sh, fail that same tree.
        count += case(unbuilt_guide, also=(DEFERRED,))
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  committed-generated-files gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the committed-generated-files gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
