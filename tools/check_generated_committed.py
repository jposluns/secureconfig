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
- plugin/skills/secure-deployment-config/SKILL.md as committed opens with front matter (line 1
  is "---", closed by the next "---" line) whose "metadata:" mapping holds exactly 1 line
  `  version: "..."`, naming that VERSION, the scope scripts/build-plugin.sh rewrites, so a
  version-shaped line elsewhere does not count. In its source, front matter included, less the
  whole HTML comments that stand as HTML blocks of their own outside any list item or block
  quote in its body, as skill_counts() in tools/_verify_sections.py reads it (the pinned
  CommonMark parser tells which lines are such a comment, so a `<!--` in code or after a
  backslash hides nothing, and a copy in code, a title, a destination, a label, an info string
  or the front matter counts, wrapped or not), it states "This skill carries N short guides"
  exactly once, on one line with 1 space between its words, as scripts/build-plugin.sh rewrites
  it, with N the guide-counts gate's set in the commit, as counted_guides() in
  tools/_verify_sections.py lists it, so a wrapped stale copy is a second statement, a lone
  sentence wrapped across lines, split across blocks or around a comment block is a finding,
  and a copy in a removed comment neither counts nor stands in for a stale or missing sentence.
  Any `<!--` in the front matter, which is not parsed, and any other HTML in SKILL.md's body,
  inline HTML included, is not read and is a finding naming the front matter's line, or the
  first line of the block, or the table row, that holds it. That module is this gate's own
  copy, not the commit's. Without the pinned parser the commit could not be checked, and nor
  could it when that parser cannot be loaded at all, from a lock beside this gate that cannot
  be read or parsed or from an install without its version metadata; each is one line;
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
cannot run, or --rebuild makes it rebuild the export. The skip trusts `git status`, which does
not report a tracked file marked skip-worktree or assume-unchanged; a build input or generated
file edited locally under either mark leaves the status clean, so this gate skips its rebuild
while the working-tree staleness gates rebuild something other than HEAD. CI checks out the
commit with neither mark set, so it is unaffected.

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
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verify_sections import SkillHtml, counted_guides, skill_counts  # noqa: E402  as the build
from check_verify_marking import ParserUnavailable, gate_parser  # noqa: E402  as skill_counts()

LLMS_FULL = "site/llms-full.txt"
PLUGIN = "plugin"
MANIFEST = "plugin/plugin.json"
SKILL = "plugin/skills/secure-deployment-config/SKILL.md"
# What scripts/build-plugin.sh rewrites in SKILL.md: the version line of the metadata mapping in
# the front matter (metadata_versions() below), and the guide count in this sentence.
SKILL_VERSION = re.compile(r'  version: "([^"]*)"')
# Text inside an HTML comment is not shown to a reader, so skill_counts() in
# tools/_verify_sections.py, which scripts/build-plugin.sh also calls, blanks in SKILL.md's body
# the lines of each whole HTML comment the pinned CommonMark parser reads as an HTML block of its
# own outside any list item or block quote, and counts the sentence in the rest, front matter
# included, wrapped or not, and again only where it stands on one line as written; it
# raises SkillHtml, a finding here, for any "<!--" in the front matter and any other HTML in the
# body, inline HTML included, which it does not read.
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


def guide_count(tree):
    """The guides the guide-counts gate counts: counted_guides() in tools/_verify_sections.py."""
    return len(counted_guides(tree))


def metadata_versions(lines):
    """The "  version:" lines of the metadata mapping in SKILL.md's front matter, or None.

    The scope is the one scripts/build-plugin.sh rewrites and confirms: the front matter runs from
    line 1, which must be "---", to the next "---" line, and the mapping from a "metadata:" line to
    the next line that does not start with a space. None means no front matter, or one not closed.
    """
    if not lines or lines[0] != "---":
        return None
    found, inside = [], False
    for line in lines[1:]:
        if line == "---":
            return found
        if inside:
            if line and not line.startswith(" "):
                inside = False
            elif line.startswith("  version:"):
                found.append(line)
        elif line == "metadata:":
            inside = True
    return None


def skill_findings(version_text, skill_text, count):
    """Findings for the committed SKILL.md version and guide count against the commit."""
    version = version_text.rstrip("\n")
    stated = metadata_versions(skill_text.split("\n"))
    findings = []
    if stated is None:
        findings.append(f'{SKILL} as committed has no front matter between a "---" first line and '
                        f'a closing "---" line; {REMEDY}')
    elif len(stated) != 1:
        findings.append(f"{SKILL} as committed has {len(stated)} metadata version lines in its "
                        "front matter, not 1")
    elif not (match := SKILL_VERSION.fullmatch(stated[0])):
        findings.append(f"{SKILL} as committed has the metadata version line {stated[0]!r}, not "
                        "in the form '  version: \"...\"' that scripts/build-plugin.sh rewrites")
    elif match[1] != version:
        findings.append(f"{SKILL} as committed names version {match[1]!r} but VERSION as "
                        f"committed is {version!r}; {REMEDY}")
    try:
        counts, written = skill_counts(skill_text)
    except SkillHtml as exc:
        findings.append(f"{SKILL} as committed cannot have its guide count checked: {exc}")
        return findings
    if len(counts) != 1:
        findings.append(f'{SKILL} as committed states "This skill carries N short guides" '
                        f"{len(counts)} times, not once (text inside an HTML comment block in the "
                        "body does not count; the front matter is searched as written)")
    elif written != counts:
        findings.append(f'{SKILL} as committed states "This skill carries N short guides" once, '
                        "but not on one line with 1 space between its words, the only form "
                        "scripts/build-plugin.sh rewrites; it is wrapped, split across blocks or "
                        "around an HTML comment block, or spaced otherwise")
    elif int(counts[0]) != count:
        findings.append(f"{SKILL} as committed states {counts[0]} guides but the commit has "
                        f"{count} (counted_guides() in tools/_verify_sections.py); {REMEDY}")
    return findings


def parser_failure():
    """Why the pinned parser that skill_counts() needs cannot run here, in one line, or None.

    gate_parser() in tools/check_verify_marking.py raises ParserUnavailable when the parser is
    absent or not the pinned version, and other exceptions when the lock beside it cannot be read
    or parsed or when a markdown_it package is present without the installed version metadata of
    markdown-it-py or mdurl. Each leaves the guide count unchecked, so each is reported as a commit
    that could not be checked, naming the cause, and none as a traceback.
    """
    try:
        gate_parser(required=True)
    except ParserUnavailable as exc:
        return f"{SKILL}'s guide count is checked with the pinned parser: {exc}"
    except Exception as exc:  # noqa: BLE001  any failure to load the parser leaves it unchecked
        cause = " ".join(f"{type(exc).__name__}: {exc}".split())
        return (f"{SKILL}'s guide count is checked with the pinned parser, which cannot be loaded "
                "from tools/requirements-gates.txt and the installed markdown-it-py and mdurl: "
                f"{cause}")
    return None


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
            skill_text = (tree / SKILL).read_text(encoding="utf-8")
            count = guide_count(tree)
        except (OSError, UnicodeError) as exc:
            findings.append(f"cannot read VERSION, {MANIFEST}, {SKILL} or the guides as "
                            f"committed: {exc}")
        else:
            findings += version_findings(version_text, manifest_text)
            problem = parser_failure()
            if problem:
                print(f"  FAIL  cannot check {label}: {problem}")
                return 2
            findings += skill_findings(version_text, skill_text, count)
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
            print(f"  ok    {label}: {MANIFEST} names VERSION {version}, SKILL.md names it and "
                  f"states {count} guides, and {LLMS_FULL} and "
                  f"{files} files under {PLUGIN}/ match a fresh build of the commit")
        else:
            print(f"  ok    {label}: {MANIFEST} names VERSION {version}, SKILL.md names it and "
                  f"states {count} guides; the working tree is "
                  "this commit with no change, so the working-tree staleness gates in "
                  "tools/run_all_checks.sh decide its generated files (--rebuild rebuilds "
                  "it here)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
