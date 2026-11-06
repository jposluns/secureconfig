#!/usr/bin/env python3
"""Cases for tools/check_install_blocks.py, the CI gate that holds scripts/build-site.py's simple
reading of README.md's install section to the pinned CommonMark parser's.

Each case edits this checkout's README.md and runs the gate's compare() on it with the pinned
parser:

  - AGREE: README.md as it is, the shell block edited, the shell block fenced with tildes, and
    README.md with CRLF line endings pass, and compare() returns the blocks install_blocks() read;
  - MISREAD: layouts install_blocks() accepts but reads differently from CommonMark fail, and
    install_blocks() is first shown to accept each, so the gate is what catches it, and each fails
    for its own reason: the in-session block commented out, the in-session block inside an HTML
    block, an indented code block in the section, a fence in a block quote, a setext level-2
    heading before the shell block, a second install heading in setext form, the in-session
    block commented out beside an added indented code block (2 blocks to each reader, not the same
    2), and the in-session block inside an HTML block beside an added fence in a block quote (2
    blocks to each reader with the same info strings in the same order, which a gate comparing
    only the number of blocks and their info strings would pass), both blocks commented out above
    an HTML block holding a level-2 heading line, with copies of both after it (each pair differs
    only in its line), and a NUL character in the shell block, which CommonMark reads as U+FFFD
    (the pair differs only in its content);
  - FIELD: README.md as it is, read by a parser that changes one field of the first block's token
    from the pinned parser's reading, fails for each of the 5 fields compare() checks (type, depth,
    line, info string and content), so dropping any one field from compare() fails a case;
  - REFUSED: a layout install_blocks() refuses (a third block, and the in-session block commented
    out beside a visible replacement) fails, naming the build's refusal.

Then the gate itself runs: on this checkout it exits 0 with its ok line, and on a copy whose lock
pins another markdown-it-py, or cannot be parsed, it exits 2 with 1 FAIL line and no traceback.
These cases need the pinned parser; without it the test fails at start-up, naming the cause.
Exit 0 ok, 1 on a finding.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import check_install_blocks as gate  # noqa: E402

build_site = gate.build_site
# The files a copy of the gate needs: the gate, the parser loader and its imports, the site build
# and its import, and README.md.
COPIED = ("tools/check_install_blocks.py", "tools/check_verify_marking.py", "tools/_markdown.py",
          "tools/_verify_sections.py", "tools/check_csp_hashes.py", "scripts/build-site.py",
          "README.md")
HASH = "--hash=sha256:" + "0" * 64


class FieldChanged:
    """The pinned parser, with one attribute of the first fence token of each reading changed."""

    def __init__(self, parser, attr, value):
        self.parser, self.attr, self.value = parser, attr, value

    def parse(self, text):
        tokens = self.parser.parse(text)
        setattr(next(t for t in tokens if t.type == "fence"), self.attr, self.value)
        return tokens


def run_copy(lock):
    """(exit, output) of the gate run on a copy of this checkout's files with lock as its
    tools/requirements-gates.txt."""
    d = Path(tempfile.mkdtemp())
    try:
        for rel in COPIED:
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, d / rel)
        (d / "tools" / "requirements-gates.txt").write_text(lock, encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", "-B", str(d / "tools" / "check_install_blocks.py")],
                           capture_output=True, text=True, timeout=120)
        return r.returncode, (r.stdout + r.stderr).rstrip("\n")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    try:
        parser = gate.gate_parser(required=True)
    except Exception as exc:  # noqa: BLE001  any failure to load the parser stops every case
        cause = " ".join(f"{type(exc).__name__}: {exc}".split())
        print(f"  FAIL  the pinned parser cannot be loaded, so no case ran: {cause}")
        return 1
    failures = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    blocks = build_site.install_blocks(readme)
    session, shell = (body for _, _, body in blocks)
    session_block = f"```text\n{session}\n```\n"
    shell_block = f"```bash\n{shell}\n```\n"
    if readme.count(session_block) != 1 or readme.count(shell_block) != 1:
        print("  FAIL  README.md does not hold the install blocks the build read, each once as a "
              "```text and a ```bash block, so no case ran")
        return 1
    edited = shell + " --scope project"
    agree = {
        "README.md as it is": readme,
        "the shell block edited": readme.replace(shell_block, f"```bash\n{edited}\n```\n", 1),
        "the shell block fenced with tildes": readme.replace(shell_block, f"~~~bash\n{shell}\n~~~\n", 1),
        "CRLF line endings": readme.replace("\n", "\r\n"),
    }
    indented = "\n    /plugin install other@other\n"
    # (README text, the part of the gate's finding that names the difference)
    misread = {
        "the in-session block commented out":
            (readme.replace(session_block, f"<!--\n{session_block}-->\n", 1),
             "finds 1 code block (first line"),
        "the in-session block inside an HTML block":
            (readme.replace(session_block, f"<div>\n{session_block}</div>\n", 1),
             "finds 1 code block (first line"),
        "an indented code block in the section":
            (readme.replace(shell_block, shell_block + indented, 1), "finds 3 code blocks"),
        "a fence in a block quote":
            (readme.replace(shell_block, shell_block + "\n> ```text\n> /plugin install "
                            "other@other\n> ```\n", 1), "finds 3 code blocks"),
        "a setext level-2 heading before the shell block":
            (readme.replace(shell_block, "Elsewhere\n---------\n\n" + shell_block, 1),
             "finds 1 code block (first line"),
        "a second install heading in setext form":
            (readme + f"\n{build_site.INSTALL[3:]}\n{'-' * len(build_site.INSTALL[3:])}\n",
             "finds 2 level-2 headings"),
        # As many blocks to both readers, but not the same ones.
        "the in-session block commented out and an indented code block added":
            (readme.replace(session_block, f"<!--\n{session_block}-->\n", 1)
             .replace(shell_block, shell_block + indented, 1), "code block 1 is, to the pinned "
             "parser, a fence"),
        # As many blocks to both readers, with the same info strings in the same order, so only
        # the line, depth and content tell them apart: the parser's first block is the quoted one.
        "the in-session block inside an HTML block and a quoted fence added after it":
            (readme.replace(session_block, f"<div>\n{session_block}</div>\n\n> ```text\n> /plugin "
                            f"install other@other\n> ```\n", 1),
             "code block 1 is, to the pinned parser, a fence at depth 1"),
        # The build's reader ends the section at the heading line inside the HTML block and reads
        # the 2 commented-out blocks; the parser reads the copies after it. Only the lines differ.
        "both blocks commented out above an HTML block with a heading line, and copies after it":
            (readme.replace(session_block, f"<!--\n{session_block}-->\n", 1)
             .replace(shell_block, f"<!--\n{shell_block}-->\n\n<div>\n## Elsewhere\n</div>\n\n"
                      f"{session_block}\n{shell_block}", 1),
             "code block 1 is, to the pinned parser, a fence at depth 0"),
        # CommonMark replaces U+0000 with U+FFFD; the build's reader keeps it. Only the content
        # differs.
        "a NUL character in the shell block":
            (readme.replace(shell_block, f"```bash\n{shell}\x00\n```\n", 1),
             "code block 2 is, to the pinned parser, a fence at depth 0"),
    }
    # (field, the change to the first block's token): compare() must report each on its own.
    first = next(t for t in parser.parse(readme) if t.type == "fence")
    field = {
        "type": ("type", "code_block"),
        "depth": ("level", first.level + 1),
        "line": ("map", [first.map[0] + 1, first.map[1] + 1]),
        "info string": ("info", first.info + "x"),
        "content": ("content", first.content + "x\n"),
    }
    refused = {
        "a third block":
            readme.replace(shell_block, shell_block + "\n```bash\nclaude plugin install "
                           "other@other\n```\n", 1),
        "the in-session block commented out beside a visible replacement":
            readme.replace(session_block, f"<!--\n{session_block}-->\n\n```text\n/plugin install "
                           f"wrong@wrong\n```\n", 1),
    }
    cases = 0
    for desc, text in agree.items():
        cases += 1
        found, got = gate.compare(text, parser)
        if found or len(got) != 2:
            failures.append(f"{desc}: the gate should pass with 2 blocks: {found!r}, {got!r}")
    for desc, (text, reason) in misread.items():
        cases += 1
        if text == readme:
            failures.append(f"{desc}: the case's edit did not change README.md")
            continue
        try:
            build_site.install_blocks(text)
        except build_site.SourceError as exc:
            failures.append(f"{desc}: install_blocks() refused it, so the case does not show the "
                            f"gate catching a misreading: {exc}")
            continue
        found, _ = gate.compare(text, parser)
        if not found or not any(reason in f for f in found):
            failures.append(f"{desc}: the gate should report the parser's different reading "
                            f"({reason!r}): {found!r}")
    for desc, change in field.items():
        cases += 1
        found, _ = gate.compare(readme, FieldChanged(parser, *change))
        if len(found) != 1 or "code block 1 is, to the pinned parser" not in found[0]:
            failures.append(f"a block whose {desc} alone differs: the gate should report code "
                            f"block 1 once: {found!r}")
    for desc, text in refused.items():
        cases += 1
        found, got = gate.compare(text, parser)
        if got or len(found) != 1 or "scripts/build-site.py refuses README.md" not in found[0]:
            failures.append(f"{desc}: the gate should report the build's refusal: {found!r}")

    rc, out = run_copy((ROOT / "tools" / "requirements-gates.txt").read_text(encoding="utf-8"))
    cases += 1
    if rc != 0 or not out.startswith("  ok    ") or "FAIL" in out:
        failures.append(f"the gate on this checkout's files should pass: exit {rc}, {out!r}")
    for desc, lock in (("pins another markdown-it-py",
                        f"markdown-it-py==0.0.1 {HASH}\nmdurl==0.0.1 {HASH}\n"),
                       ("cannot be parsed", "markdown-it-py\n")):
        rc, out = run_copy(lock)
        cases += 1
        lines = out.splitlines()
        if (rc != 2 or len(lines) != 1 or not lines[0].startswith("  FAIL  ")
                or "pinned parser" not in lines[0] or "Traceback" in out):
            failures.append(f"the gate with a lock that {desc} should exit 2 in 1 FAIL line: "
                            f"exit {rc}, {out!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {cases} cases for the install-section gate: {len(agree)} layouts both readers "
          f"agree on, {len(misread)} the site build's reader misreads and the gate catches, "
          f"{len(field)} fields of a block each caught on its own, {len(refused)} the build "
          f"refuses, and the gate run on this checkout, on a lock pinning another version and on "
          f"a lock it cannot parse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
