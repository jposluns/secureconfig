#!/usr/bin/env python3
"""Recorded cases for the guide-counts section of tools/run_all_checks.sh.

Each case writes a fixture tree holding two guides, a README.md and copies of the tools the
section imports (tools/check_verify_marking.py, tools/_markdown.py and tools/_verify_sections.py)
beside a parser lock, then runs the section's own text, from its guide_files=() line to the next
section, with bash in that tree and python3 bound to this interpreter, and checks the ok or FAIL
line it prints.

The README cases pin how HTML comments are read. A real comment, an HTML block or an inline HTML
comment as the pinned parser reads it, or one in text the parser drops unread (a table cell past
the header's columns), is still stripped before the count sentence is matched, so a stale copy
inside one neither counts nor fails. A "<!--" the parser reads as literal text (in a code span, a
fenced or indented code block, a link destination, an inline HTML tag's attribute or after a
backslash) is text and is kept, so a count sentence between it and a later "-->" is still read,
and a visible stale copy inside a code span is found. The README cases need the pinned parser;
where it is absent or another version they are skipped and counted in a "skip" line naming the
reason. One case runs on every host: a copy of the tools whose lock pins a markdown-it-py version
other than the installed one must fail the gate in one line naming the parser.
"""
import shlex
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from check_verify_marking import ParserUnavailable, gate_parser  # noqa: E402

COPIED = ("check_verify_marking.py", "_markdown.py", "_verify_sections.py")
LOCK = "requirements-gates.txt"
SENTENCE = "that is 2 guides across the 1 categories indexed below"
STALE = "that is 9 guides across the 1 categories indexed below"
OK = "  ok    README.md's stated counts match the corpus: 2 guides across 1 categories\n"
FAIL = "  FAIL  README.md's stated guide or category count does not match the corpus\n"


def parser_problem():
    """Why the pinned parser cannot run here, or None when it can."""
    try:
        gate_parser(required=True)
    except ParserUnavailable as exc:
        return str(exc)
    except Exception as exc:  # noqa: BLE001  any failure to load the parser skips its cases
        return "the pinned parser cannot be loaded: " + " ".join(
            f"{type(exc).__name__}: {exc}".split())
    return None


def readme(intro, tail=""):
    return ("# secureconfig\n\n## What this is\n\n" + intro + "\n\n## Guide index\n\n"
            "### One category\n\n| Guide | Covers |\n| --- | --- |\n"
            "| [a.md](a.md) | a |\n| [b.md](b.md) | b |\n" + tail)


def section():
    """The guide-counts section's text from guide_files=() on, without its self-test."""
    suite = (TOOLS / "run_all_checks.sh").read_text(encoding="utf-8")
    assert suite.count("# section: guide-counts\n") == 1, "no single guide-counts section"
    text = suite.split("# section: guide-counts\n", 1)[1].split("\n# section: ", 1)[0]
    assert text.count("guide_files=()\n") == 1, "no single guide_files=() line"
    return text[text.index("guide_files=()\n"):]


def run_gate(readme_text, lock_text=None):
    """Run the section on a fixture tree; return (exit status, output)."""
    with tempfile.TemporaryDirectory(prefix="guide-counts-test-") as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        for name in COPIED:
            shutil.copyfile(TOOLS / name, root / "tools" / name)
        if lock_text is None:
            shutil.copyfile(TOOLS / LOCK, root / "tools" / LOCK)
        else:
            (root / "tools" / LOCK).write_text(lock_text, encoding="utf-8")
        for name in ("a.md", "b.md"):
            (root / name).write_text("# Guide\n", encoding="utf-8")
        (root / "README.md").write_bytes(readme_text.encode("utf-8"))
        script = ("set -uo pipefail\nfail=0\n"
                  "ok()  { printf '  ok    %s\\n' \"$1\"; }\n"
                  "bad() { printf '  FAIL  %s\\n' \"$1\"; fail=1; }\n"
                  f"python3() {{ {shlex.quote(sys.executable)} \"$@\"; }}\n"
                  + section() + '\nexit "$fail"\n')
        result = subprocess.run(["bash", "-c", script], cwd=root, capture_output=True,
                                text=True, encoding="utf-8", timeout=120)
        return result.returncode, result.stdout + result.stderr


# (label, README text, passes, a fragment the output holds)
KEPT = (
    ("plain sentence", readme(f"The corpus, {SENTENCE}."), True, OK),
    ("a comment block hides a stale copy",
     readme(f"<!-- {STALE} -->\n\nThe corpus, {SENTENCE}."), True, OK),
    ("a multi-line comment block hides a stale copy elsewhere",
     readme(f"The corpus, {SENTENCE}.", f"\n<!--\n{STALE}\n-->\n"), True, OK),
    ("an inline comment inside the sentence is removed",
     readme("The corpus, that is 2 guides <!-- a note --> across the 1 categories indexed "
            "below."), True, OK),
    ("an inline comment hides a stale copy elsewhere",
     readme(f"The corpus, {SENTENCE}.", f"\n## Notes\n\nOld text <!-- {STALE} --> ends.\n"),
     True, OK),
    ("a comment inside an HTML block is removed",
     readme(f"The corpus, {SENTENCE}.",
            f"\n<details>\n<summary>Old</summary>\n<!-- {STALE} -->\n</details>\n"), True, OK),
    ("a comment in a table cell past the header's columns, which the parser drops, is removed",
     readme(f"The corpus, {SENTENCE}.",
            f"\n## Notes\n\n| A |\n| --- |\n| shown | <!-- {STALE} --> |\n"), True, OK),
    ("a real comment after a code-span opener is still removed",
     readme(f"Write `<!--` to open one. <!-- {STALE} --> The corpus, {SENTENCE}."), True, OK),
    ("CRLF line endings",
     readme(f"<!-- {STALE} -->\n\nThe corpus, {SENTENCE}.").replace("\n", "\r\n"), True, OK),
    ("a stale count still fails",
     readme(STALE + "."), False, "README.md states 9 guides but the root has 2 guides"),
)
# Each of these failed at ffffa1c3567c5da673989a9a87ce5cbe5b7d961c, whose code-blind strip
# removed text from a "<!--" that is not a comment through the next "-->".
FIXED = (
    ("code-span opener and closer around the sentence",
     readme(f"Write `<!--` to open a comment; {SENTENCE}. Write `-->` to close it."), True, OK),
    ("fenced code opener and closer around the sentence",
     readme(f"```html\n<!--\n```\n\nThe corpus, {SENTENCE}.\n\n```html\n-->\n```"), True, OK),
    ("indented code opener and closer around the sentence",
     readme(f"    <!--\n\nThe corpus, {SENTENCE}.\n\n    -->"), True, OK),
    ("escaped opener before the sentence",
     readme(f"Write \\<!-- to open one; {SENTENCE}. Close it with -->."), True, OK),
    ("link destinations holding an opener and a closer",
     readme(f"See [the opener](https://example.com/<!--); {SENTENCE}; see "
            "[the closer](https://example.com/-->)."), True, OK),
    ("inline HTML tag attributes holding an opener and a closer",
     readme(f'The corpus, <span title="<!--">x</span> {SENTENCE} <span title="-->">y</span>.'),
     True, OK),
    ("a visible stale copy in a code span is found",
     readme(f"The corpus, {SENTENCE}.", f"\n## Notes\n\n`<!-- {STALE} -->`\n"), False,
     "states its counts as 'that is N guides across the M categories indexed below' 1 more "
     "time(s) outside '## What this is'"),
)


def other_lock():
    """A lock pinning a markdown-it-py version that is not the installed one."""
    try:
        installed = version("markdown-it-py")
    except PackageNotFoundError:
        installed = None
    digest = " --hash=sha256:" + "0" * 64
    wanted = "0.0.2" if installed == "0.0.1" else "0.0.1"
    return f"markdown-it-py=={wanted}{digest}\nmdurl==0.1.2{digest}\n"


def main():
    failures, count, skipped = [], 0, 0
    problem = parser_problem()
    for label, text, passes, fragment in KEPT + FIXED:
        if problem is not None:
            skipped += 1
            continue
        count += 1
        status, output = run_gate(text)
        if (status == 0) != passes or fragment not in output or "Traceback" in output:
            failures.append(f"{label}: exit {status}: {' | '.join(output.splitlines())}")
        elif not passes and FAIL not in output:
            failures.append(f"{label}: no FAIL line: {' | '.join(output.splitlines())}")
    count += 1
    status, output = run_gate(readme(f"The corpus, {SENTENCE}."), other_lock())
    if (status != 1 or "README.md's sections need the pinned Markdown parser: " not in output
            or "Traceback" in output):
        failures.append(f"another pinned version: exit {status}: "
                        f"{' | '.join(output.splitlines())}")
    if failures:
        for failure in failures:
            print(f"  FAIL  guide-counts gate self-test: {failure}")
        return 1
    print(f"  ok    {count} recorded cases for the guide-counts gate")
    if skipped:
        print(f"  skip  {skipped} recorded cases need the pinned parser, which cannot run "
              f"here: {problem}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
