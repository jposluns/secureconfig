#!/usr/bin/env python3
"""Exercise check_generated_committed.py through the shipped gate on throwaway repositories.

Each repository carries a guide, VERSION, plugin/plugin.json, a tracked site/index.html and
stub build scripts that do what the gate depends on the real ones doing: build-llms-full.sh
writes site/llms-full.txt from the guide, and build-plugin.sh refuses a malformed VERSION,
replaces the references directory, writes VERSION into plugin.json with the real script's sed,
writes VERSION and the guide count from the gate's own tools/_verify_sections.py into SKILL.md
with the real script's seds, and writes a MANIFEST.sha256. The repository is built and committed
clean before each case changes it. The last group runs the real scripts/build-plugin.sh, with
stand-ins only for its guide list and its version-basis check, on SKILL.md files it must
rewrite or refuse.

The two finding cases reproduce how each defect reaches a commit: the working tree is rebuilt
in full, so the working-tree staleness gates pass, which each case confirms by rebuilding the
working tree and finding nothing changed, while the commit is incomplete. Each has a passing
twin that differs only in the defect and takes the same rebuild path. A case whose working
tree is clean passes --rebuild where it needs the rebuild path. The last cases fail closed,
and two record what the gate does not do: read the index, or rebuild a clean tree unasked.

The gate and the real build find SKILL.md's count sentence with the pinned CommonMark parser
(skill_counts() in tools/_verify_sections.py). Where that parser is absent or another version,
every case that needs it is skipped and counted in a "skip" line naming the reason. 2 cases run
on every host and confirm that the gate and the real build refuse when the parser is not the
pinned one: each runs on a copy of the tools whose lock pins a markdown-it-py version other than
the installed one.
"""
import os
import re
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

GATE = Path(__file__).resolve().parent / "check_generated_committed.py"
sys.path.insert(0, str(GATE.parent))
from _verify_sections import skill_counts  # noqa: E402  the count rule the build and gate share
from check_verify_marking import ParserUnavailable, gate_parser  # noqa: E402


def parser_problem():
    """Why the pinned parser cannot run here, or None when it can."""
    try:
        gate_parser(required=True)
    except ParserUnavailable as exc:
        return str(exc)
    return None


PARSER_PROBLEM = parser_problem()
# What gate_parser() reads beside itself, and what the gate and the build import.
TOOLS = ("_verify_sections.py", "_markdown.py", "check_verify_marking.py",
         "requirements-gates.txt")


def other_lock():
    """tools/requirements-gates.txt with markdown-it-py pinned to a version that is not the
    installed one, so a copy of the tools holding it refuses on every host."""
    try:
        installed = version("markdown-it-py")
    except PackageNotFoundError:
        installed = None
    other = "0.0.2" if installed == "0.0.1" else "0.0.1"
    lock, found = re.subn(r"(?m)^markdown-it-py==[0-9.]+ ", f"markdown-it-py=={other} ",
                          (GATE.parent / "requirements-gates.txt").read_text(encoding="utf-8"))
    assert found == 1, "tools/requirements-gates.txt holds no single markdown-it-py pin"
    return lock


SKIPPED = []
OK = "  ok    commit "
REBUILT = "site/llms-full.txt and 4 files under plugin/ match a fresh build of the commit"
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
skill=plugin/skills/secure-deployment-config/SKILL.md
count=$(python3 "SECTIONS_PY" | wc -l)
sed -i -e "1,/^---\$/ { /^metadata:\$/,/^[^ ]/ s/^\(  version: \)\"[^\"]*\"\$/\1\"$version\"/ }" \
  -e "s/\(This skill carries \)[0-9][0-9]*\( short guides\)/\1$count\2/" "$skill"
( cd "$dest" && sha256sum guide.md ) > "$dest/MANIFEST.sha256"
""".replace("SECTIONS_PY", str(GATE.parent / "_verify_sections.py"))

# The real scripts/build-plugin.sh runs on a fixture whose guide list and version-basis check are
# stand-ins, the second because the real check reads the whole repository; everything after them
# is the real script, with the real tools/_verify_sections.py counting the guides and finding the
# count sentence with the pinned parser.
REAL_BUILD = GATE.parent.parent / "scripts" / "build-plugin.sh"
LIST_GUIDES = r"""#!/usr/bin/env bash
printf '%s\n' guide.md
"""
VERSION_BASIS = "import sys\nsys.exit(0)\n"

PLUGIN_JSON = '{\n  "name": "fixture",\n  "version": "1.0.5",\n  "license": "CC0-1.0"\n}\n'
SKILL = "plugin/skills/secure-deployment-config/SKILL.md"
SKILL_MD = ('---\nname: fixture\nmetadata:\n  version: "1.0.5"\n---\n\n'
            "This skill carries 1 short guides.\n")
# A "<!--" in code is literal text, as CommonMark has it, so a stale count sentence after one in a
# code span or a fenced code block is visible; a real comment beside such code still hides its text.
CODE_SPAN = "Type `<!--` to open a comment.\nThis skill carries 3 short guides.\n"
FENCED = "```html\n<!--\n```\nThis skill carries 3 short guides.\n"
BESIDE_CODE = "Type `<!--` to open one. <!-- This skill carries 7 short guides. -->\n"
# What the hand-written scan that the parser replaced misread, from the 2 QA reports on #1233: a
# "<!--" in a fence in a block quote, in a code span on a heading, list item or block quote line
# after a stray backtick, after a backslash, or in an indented code block, then a stale sentence.
STALE_AFTER = (
    "\n> ~~~html\n> <!--\n> ~~~\n\nThis skill carries 3 short guides.\n",
    "\nUse a ` here.\n# Type `<!--`\n`\nThis skill carries 3 short guides.\n",
    "\n- a ` b\n- Type `<!--`\n`\nThis skill carries 3 short guides.\n",
    "\na ` b\n> Type `<!--`\n`\nThis skill carries 3 short guides.\n",
    "\n\\<!--\nThis skill carries 3 short guides.\n",
    "\n    <!--\n\nThis skill carries 3 short guides.\n",
)
# A sentence wrapped within its paragraph is shown on 1 line, so a stale one counts.
WRAPPED = "This skill carries\n3 short guides.\n"
# Beside the same constructs, a real comment still hides its sentence: one after a heading that
# holds a stray backtick, one after an escaped opener, and one after a fence in a block quote.
REAL_COMMENTS = (
    "\n# `heading\n<!-- ` This skill carries 3 short guides. -->\n",
    "\n\\<!-- <!-- This skill carries 3 short guides. -->\n",
    "\n> ~~~\n> <!--\n> ~~~\n\n<!-- This skill carries 3 short guides. -->\n",
)
# Raw HTML other than a whole comment is not read, so each is refused, naming line 9, where each
# starts after SKILL_MD. From the round 2 QA reports on #1233: a "<!--" in a quoted attribute or
# in a textarea, which a browser shows; an apparent tag in a textarea, which a browser shows; a
# quoted ">" in an attribute, which a browser does not show; a comment opened in a div block and
# continued past a blank line; and script content, which a browser does not show. Also a style
# block, a comment ended early by "--!>", the abrupt "<!-->", text after a comment's "-->", and
# an inline tag.
RAW_HTML = (
    '\n<div title="<!--">\nThis skill carries 3 short guides.\n</div>\n',
    "\n<textarea>\n<!--\nThis skill carries 3 short guides.\n</textarea>\n",
    "\n<textarea>\n<This skill carries 3 short guides>\n</textarea>\n",
    '\n<div title="a>This skill carries 3 short guides">\n</div>\n',
    "\n<div>\n<!--\n\nThis skill carries 3 short guides.\n-->\n</div>\n",
    "\n<script>\nlet s = 'This skill carries 3 short guides';\n</script>\n",
    "\n<style>\n/* This skill carries 3 short guides */\n</style>\n",
    "\n<!-- a --!> This skill carries 3 short guides. -->\n",
    "\n<!-->\nThis skill carries 3 short guides.\n",
    "\n<!-- a --> This skill carries 3 short guides.\n",
    "\nSee <b>this</b>.\n",
)
NOT_READ = "line 9 holds raw HTML; SKILL.md may hold HTML only as whole HTML comments"
# A copy of the sentence in a link title, a link reference definition title, an image title or a
# fence info string counts, as it did when a regex searched the whole file, so a stale one there
# is a second statement.
TITLES = (
    '\nSee [this](https://example.invalid "This skill carries 3 short guides").\n',
    '\nSee [this].\n\n[this]: https://example.invalid "This skill carries 3 short guides"\n',
    '\n![a figure](figure.png "This skill carries 3 short guides")\n',
    "\n```This skill carries 3 short guides\ncode\n```\n",
)
# A whole comment, inline or as a block, still hides its text.
WHOLE_COMMENTS = (
    "\nSee <!-- This skill carries 3 short guides. --> this.\n",
    "\n<!--\nThis skill carries 3 short guides.\n-->\n",
)


def skipped(parser):
    """Whether a case that needs the pinned parser (parser True) cannot run here; a skipped case
    is counted for the skip line."""
    if parser and PARSER_PROBLEM is not None:
        SKIPPED.append(1)
        return True
    return False


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
         args=(), init=True, parser=True, lock=None):
    """Run the gate on a fixture repository after change; with lock, run a copy of the gate and
    the modules it imports beside lock as its tools/requirements-gates.txt."""
    if skipped(parser):
        return 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        gate = GATE
        if lock is not None:
            gate = Path(directory) / "tools" / GATE.name
            for name in (GATE.name, *TOOLS):
                write(gate.parent, name, (GATE.parent / name).read_text(encoding="utf-8"))
            write(gate.parent, "requirements-gates.txt", lock)
        write(root, "scripts/build-llms-full.sh", LLMS_BUILD)
        write(root, "scripts/build-plugin.sh", PLUGIN_BUILD)
        write(root, "guide.md", "first text\n")
        write(root, "VERSION", "1.0.5\n")
        write(root, "plugin/plugin.json", PLUGIN_JSON)
        write(root, SKILL, SKILL_MD)
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
        done = subprocess.run([sys.executable, "-I", "-B", str(gate), str(root), *args],
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
        commit(root, "VERSION", *(["plugin/plugin.json", SKILL] if stage_manifest else []))
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
    write(root, SKILL, SKILL_MD.replace("1.0.5", "1.0.x"))
    commit(root)


def skill(old, new):
    """Commit SKILL.md with old replaced by new and nothing rebuilt."""
    def change(root):
        write(root, SKILL, SKILL_MD.replace(old, new))
        commit(root)
    return change


def added_guide(rebuilt):
    """Commit a second guide, with or without the rebuild that restates SKILL.md's count."""
    def change(root):
        write(root, "other.md", "another guide\n")
        if rebuilt:
            build(root)
        commit(root)
    return change


def skill_text(text):
    """Commit SKILL.md as text and nothing rebuilt."""
    def change(root):
        write(root, SKILL, text)
        commit(root)
    return change


def not_guides(rebuilt):
    """Commit a dot-named .md file and a directory named *.md, which are not guides."""
    def change(root):
        write(root, ".notes.md", "not a guide\n")
        write(root, "drafts.md/note.txt", "not a guide\n")
        if rebuilt:
            build(root)
        commit(root)
    return change


def real_build(skill_md, expected, needle, parser=True, lock=None):
    """Run the real build-plugin.sh on a fixture holding skill_md, with one guide and two .md
    names that are not guides, and with lock, when given, as its tools/requirements-gates.txt;
    on success, SKILL.md must name VERSION 1.0.5 and, in the text a reader sees, 1 guide."""
    if skipped(parser):
        return 0
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        write(root, "scripts/build-plugin.sh", REAL_BUILD.read_text(encoding="utf-8"))
        write(root, "scripts/build-llms-full.sh", LIST_GUIDES)
        write(root, "tools/version_basis.py", VERSION_BASIS)
        for name in TOOLS:
            write(root, "tools/" + name, (GATE.parent / name).read_text(encoding="utf-8"))
        if lock is not None:
            write(root, "tools/requirements-gates.txt", lock)
        write(root, "guide.md", "first text\n")
        write(root, ".notes.md", "not a guide\n")
        write(root, "drafts.md/note.txt", "not a guide\n")
        write(root, "VERSION", "1.0.5\n")
        write(root, "plugin/plugin.json", PLUGIN_JSON)
        write(root, SKILL, skill_md)
        done = subprocess.run(["bash", "scripts/build-plugin.sh"], cwd=root, capture_output=True,
                              text=True, env=environment(root), timeout=120)
        output = done.stdout + done.stderr
        assert done.returncode == expected, ("real build", done.returncode, expected, output)
        assert needle in output, (needle, output)
        if expected == 0:
            text = (root / SKILL).read_text(encoding="utf-8")
            assert '  version: "1.0.5"\n' in text and skill_counts(text) == ["1"], text
    return 1


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
        count += case(nothing, also=("plugin/plugin.json names VERSION 1.0.5, SKILL.md names it "
                                     "and states 1 guides; " + DEFERRED,),
                      absent=(REBUILT,))
        count += case(nothing, args=rebuild,
                      also=("plugin/plugin.json names VERSION 1.0.5, SKILL.md names it and "
                            "states 1 guides, and " + REBUILT,))

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
                      also=("plugin/plugin.json names VERSION 1.0.6, SKILL.md names it and "
                            "states 1 guides, and " + REBUILT,))

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

        # SKILL.md's version and guide count, which build-plugin.sh rewrites, are checked on a
        # clean tree too: a stale version, a stale count and its fixed twin, and the version
        # line or count sentence missing or stated twice.
        count += case(skill('"1.0.5"', '"1.0.4"'), expected=1,
                      needle=SKILL + " as committed names version '1.0.4' but VERSION as "
                             "committed is '1.0.5'",
                      absent=("plugin/plugin.json as committed",))
        count += case(added_guide(False), expected=1,
                      needle=SKILL + " as committed states 1 guides but the commit has 2")
        count += case(added_guide(False), expected=1, args=rebuild,
                      needle=SKILL + " as committed states 1 guides but the commit has 2",
                      also=(SKILL + " as committed differs from a fresh build",))
        count += case(added_guide(True), args=rebuild,
                      also=("SKILL.md names it and states 2 guides, and " + REBUILT,))
        count += case(skill("This skill carries 1 short guides", "This skill has 1 guide"),
                      expected=1,
                      needle=SKILL + ' as committed states "This skill carries N short guides" '
                             "0 times, not once")
        count += case(skill("This skill carries 1 short guides.",
                            "This skill carries 1 short guides. This skill carries 1 short "
                            "guides."),
                      expected=1, needle='short guides" 2 times, not once')
        # Text inside an HTML comment is not the count sentence: a commented sentence with no
        # visible one fails, a commented current count beside a stale visible one fails, and a
        # commented copy beside the one current visible sentence is not a second statement.
        count += case(skill("This skill carries 1 short guides.",
                            "<!-- This skill carries 1 short guides. -->"),
                      expected=1,
                      needle=SKILL + ' as committed states "This skill carries N short guides" '
                             "0 times, not once (text inside HTML comments does not count)")
        count += case(skill_text(SKILL_MD.replace("carries 1 short", "carries 3 short")
                                 + "<!--\nThis skill carries 1 short guides.\n-->\n"),
                      expected=1,
                      needle=SKILL + " as committed states 3 guides but the commit has 1",
                      absent=("times, not once",))
        count += case(skill_text(SKILL_MD + "<!-- This skill carries 7 short guides. -->\n"),
                      also=("SKILL.md names it and states 1 guides; ",))
        # A line opening "<!--" with no "-->" after it starts an HTML block that runs to the end
        # of the file and is not a whole comment, so it is refused, naming its line.
        count += case(skill("This skill carries 1 short guides.",
                            "<!--\nThis skill carries 1 short guides."),
                      expected=1,
                      needle=SKILL + " as committed cannot have its guide count checked: line 7 "
                             "holds raw HTML; SKILL.md may hold HTML only as whole HTML comments",
                      absent=("times, not once",))
        # A "<!--" in a code span or a fenced code block opens no comment, so the stale sentence
        # after it is a second statement; a real comment beside a code span still hides its text,
        # and an inline one holding a backtick still closes at its "-->", so a stale sentence
        # after it shows. As an HTML block, with text after its "-->", it is raw HTML that is not
        # a whole comment, and is refused.
        count += case(skill_text(SKILL_MD + CODE_SPAN), expected=1,
                      needle='short guides" 2 times, not once')
        count += case(skill_text(SKILL_MD + FENCED), expected=1,
                      needle='short guides" 2 times, not once')
        count += case(skill_text(SKILL_MD + BESIDE_CODE),
                      also=("SKILL.md names it and states 1 guides; ",))
        count += case(skill_text(SKILL_MD + "See <!-- `x --> `\nThis skill carries 3 short "
                                 "guides.\n"),
                      expected=1, needle='short guides" 2 times, not once')
        count += case(skill_text(SKILL_MD + "<!-- `x --> `\nThis skill carries 3 short guides.\n"),
                      expected=1,
                      needle=SKILL + " as committed cannot have its guide count checked: line 8 "
                             "holds raw HTML; SKILL.md may hold HTML only as whole HTML comments")
        # The QA cases on #1233: each stale sentence, and a wrapped one, is a second statement,
        # and each real comment beside the same constructs still hides its sentence.
        for tail in (*STALE_AFTER, WRAPPED):
            count += case(skill_text(SKILL_MD + tail), expected=1,
                          needle='short guides" 2 times, not once')
        for tail in REAL_COMMENTS:
            count += case(skill_text(SKILL_MD + tail),
                          also=("SKILL.md names it and states 1 guides; ",))
        # The round 2 QA cases on #1233: raw HTML other than a whole comment is a finding, a
        # failed check and not a commit that could not be checked; a stale copy in a title or an
        # info string is a second statement; and a whole comment, inline or as a block, still
        # hides its sentence.
        for tail in RAW_HTML:
            count += case(skill_text(SKILL_MD + tail), expected=1,
                          needle=SKILL + " as committed cannot have its guide count checked: "
                                 + NOT_READ)
        for tail in TITLES:
            count += case(skill_text(SKILL_MD + tail), expected=1,
                          needle='short guides" 2 times, not once')
        for tail in WHOLE_COMMENTS:
            count += case(skill_text(SKILL_MD + tail),
                          also=("SKILL.md names it and states 1 guides; ",))
        count += case(skill('  version: "1.0.5"\n', ""), expected=1,
                      needle=SKILL + " as committed has 0 metadata version lines in its front "
                             "matter, not 1")
        # An unquoted metadata version, two metadata version lines, and front matter that opens
        # with "---" and never closes.
        count += case(skill('"1.0.5"', "1.0.5"), expected=1,
                      needle=SKILL + " as committed has the metadata version line '  version: "
                             "1.0.5', not in the form")
        count += case(skill('  version: "1.0.5"\n', '  version: "1.0.5"\n  version: "1.0.5"\n'),
                      expected=1,
                      needle=SKILL + " as committed has 2 metadata version lines in its front "
                             "matter, not 1")
        count += case(skill_text(SKILL_MD.replace("\n---\n", "\n", 1)), expected=1,
                      needle=SKILL + ' as committed has no front matter between a "---" first '
                             'line and a closing "---" line')
        # A version-shaped line after the front matter is not the metadata line, to the build's
        # sed range or to the gate.
        count += case(skill("short guides.\n", 'short guides.\n  version: "1.0.4"\n'),
                      args=rebuild, also=(REBUILT,))
        # Nor does one satisfy them: a stale metadata version with a current decoy in the body,
        # a version line outside the metadata mapping, and no front matter at all.
        stale = SKILL_MD.replace('"1.0.5"', '"1.0.4"')
        count += case(skill_text(stale + '  version: "1.0.5"\n'), expected=1,
                      needle=SKILL + " as committed names version '1.0.4' but VERSION as "
                             "committed is '1.0.5'")
        count += case(skill("metadata:\n", "other:\n"), expected=1,
                      needle=SKILL + " as committed has 0 metadata version lines in its front "
                             "matter, not 1")
        count += case(skill_text(SKILL_MD.replace("---\n", "")), expected=1,
                      needle=SKILL + ' as committed has no front matter between a "---" first '
                             'line and a closing "---" line')
        # One count definition: a dot-named .md file and a directory named *.md are not guides
        # to the build or the gate (each was one to the shell glob or to the earlier guides()).
        count += case(not_guides(False), also=("SKILL.md names it and states 1 guides; ",))
        count += case(not_guides(True), args=rebuild,
                      also=("SKILL.md names it and states 1 guides, and " + REBUILT,))

        # The real build-plugin.sh rewrites only the metadata version in the front matter and
        # the count sentence, and refuses when either is not there to rewrite, decoy or not.
        count += real_build(stale, 0, "wrote plugin/skills/secure-deployment-config/references")
        count += real_build((GATE.parent.parent / SKILL).read_text(encoding="utf-8"), 0,
                            "wrote plugin/skills/secure-deployment-config/references")
        refused = "SKILL.md version did not update to 1.0.5"
        count += real_build(SKILL_MD.replace('"1.0.5"', "1.0.4") + '  version: "1.0.5"\n', 1,
                            refused)
        count += real_build(SKILL_MD.replace('  version: "1.0.5"\n', "")
                            + '  version: "1.0.5"\n', 1, refused)
        count += real_build(SKILL_MD.replace("metadata:\n", "other:\n"), 1, refused)
        count += real_build(SKILL_MD.replace("---\n", ""), 1, refused)
        # An unquoted metadata version, two metadata version lines, and front matter that opens
        # with "---" and never closes.
        count += real_build(SKILL_MD.replace('"1.0.5"', "1.0.5"), 1, refused)
        count += real_build(SKILL_MD.replace('  version: "1.0.5"\n',
                                             '  version: "1.0.5"\n  version: "1.0.5"\n'),
                            1, refused)
        count += real_build(SKILL_MD.replace("\n---\n", "\n", 1), 1, refused)
        count += real_build(SKILL_MD.replace("This skill carries", "This skill has"), 1,
                            "SKILL.md guide count did not update to 1")
        # Only text outside HTML comments counts: a commented sentence with no visible one, and
        # a second visible sentence, are refused; a stale visible count beside a commented
        # current one is rewritten, which real_build confirms outside comments.
        uncounted = "SKILL.md guide count did not update to 1; outside HTML comments"
        count += real_build(SKILL_MD.replace("This skill carries 1 short guides.",
                                             "<!-- This skill carries 1 short guides. -->"),
                            1, uncounted)
        count += real_build(SKILL_MD + "This skill carries 1 short guides.\n", 1, uncounted)
        # A line opening "<!--" with no "-->" after it starts raw HTML that is not a whole
        # comment, so the build refuses it, naming its line.
        not_read = "SKILL.md's guide count cannot be checked: "
        count += real_build(SKILL_MD.replace("This skill carries 1 short guides.",
                                             "<!--\nThis skill carries 1 short guides."),
                            1, not_read + "line 7 holds raw HTML; SKILL.md may hold HTML only "
                            "as whole HTML comments; refusing to build")
        count += real_build(SKILL_MD.replace("carries 1 short", "carries 3 short")
                            + "<!-- This skill carries 1 short guides. -->\n", 0,
                            "wrote plugin/skills/secure-deployment-config/references")
        # A "<!--" in a code span or a fenced code block hides nothing, so the rewritten sentence
        # after it is a second visible one and is refused; a real comment beside code still hides.
        count += real_build(SKILL_MD + CODE_SPAN, 1, uncounted)
        count += real_build(SKILL_MD + FENCED, 1, uncounted)
        count += real_build(SKILL_MD + BESIDE_CODE, 0,
                            "wrote plugin/skills/secure-deployment-config/references")
        # The QA cases on #1233: the build rewrites each stale sentence and refuses the second
        # visible one, and builds beside each real comment.
        for tail in (*STALE_AFTER, WRAPPED):
            count += real_build(SKILL_MD + tail, 1, uncounted)
        for tail in REAL_COMMENTS:
            count += real_build(SKILL_MD + tail, 0,
                                "wrote plugin/skills/secure-deployment-config/references")
        # The round 2 QA cases on #1233: the build refuses raw HTML other than a whole comment,
        # rewrites a stale copy in a title or an info string and refuses it as a second visible
        # sentence, and builds beside a whole comment, inline or as a block.
        for tail in RAW_HTML:
            count += real_build(SKILL_MD + tail, 1, not_read + NOT_READ)
        for tail in TITLES:
            count += real_build(SKILL_MD + tail, 1, uncounted)
        for tail in WHOLE_COMMENTS:
            count += real_build(SKILL_MD + tail, 0,
                                "wrote plugin/skills/secure-deployment-config/references")

        # Fail closed: a revision that is not a commit, an option-shaped revision, a directory
        # that is not a repository, and a repository with no commit.
        count += case(nothing, expected=2, args=("--rev", "no-such-revision"),
                      needle="  FAIL  cannot check the committed generated files: "
                             "'no-such-revision' does not name a commit", parser=None)
        count += case(nothing, expected=2, args=("--rev=--output=x",),
                      needle="'--output=x' is not a revision", parser=None)
        count += case(nothing, expected=2, init=False,
                      needle="  FAIL  cannot check the committed generated files: ", parser=None)
        count += case(init_only, expected=2, init=False,
                      needle="'HEAD' does not name a commit", parser=None)
        # Without the pinned parser, the gate cannot check the count and the build refuses: each
        # runs with a lock pinning a markdown-it-py version other than the installed one, so
        # both run on every host.
        count += case(nothing, expected=2, parser=None, lock=other_lock(),
                      needle=SKILL + "'s guide count is checked with the pinned parser: ")
        count += real_build(SKILL_MD, 1, "SKILL.md's guide count is checked with the pinned "
                            "parser: ", parser=None, lock=other_lock())

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
    if SKIPPED:
        print(f"  skip  {len(SKIPPED)} recorded cases need the pinned parser, which cannot run "
              f"here: {PARSER_PROBLEM}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
