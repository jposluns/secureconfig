#!/usr/bin/env python3
"""Exercise the shipped bare-URL entry point in throwaway tracked repositories."""
import shutil
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from _walk import isolated_git_environment
from check_verify_marking import ParserUnavailable, gate_parser

TOOLS = Path(__file__).resolve().parent
MODULES = ("check_bare_urls", "_markdown", "_walk", "version_basis",
           "check_verify_marking", "_verify_sections")
BARE = "See https://example.com/__init__.py\n"


@isolated_git_environment()
def fixture(body, gate_source=None, prefix="# Fixture\n\n"):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        for module in MODULES:
            shutil.copyfile(TOOLS / (module + ".py"), root / "tools" / (module + ".py"))
        shutil.copyfile(TOOLS / "requirements-gates.txt", root / "tools/requirements-gates.txt")
        if gate_source is not None:
            (root / "tools/check_bare_urls.py").write_text(gate_source, encoding="utf-8")
        (root / "fixture.md").write_text(prefix + body, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "fixture.md"], cwd=root, check=True,
                       capture_output=True)
        result = subprocess.run([sys.executable, "-I", "-B",
                                 str(root / "tools/check_bare_urls.py"), "--require-parser"], cwd=root,
                                capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout + result.stderr


def assert_failure(body, prefix="# Fixture\n\n", line=3, gate_source=None):
    result = fixture(body, gate_source, prefix)
    assert result[0] == 1 and f"  FAIL  fixture.md:{line}: bare URL contains __" in result[1], result


def main():
    try:
        gate_parser(required=True)
    except ParserUnavailable as exc:
        if os.environ.get("CI"):
            raise
        print(f"  SKIP  bare URL parser fixtures: {exc}")
        return
    failures = (
        (BARE, 3),
        ("[https://example.com/__init__.py](https://example.com/ok)\n", 3),
        (r"See https://example.com/\_\_init.py" + "\n", 3),
        ("[source]:\n\nhttps://example.com/__init__.py\n", 5),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\nRun `ls`.\n", 5),
        ("1. Item\n    https://example.com/__init__.py\n", 4),
        ("- Parent\n    - https://example.com/__init__.py\n", 4),
        ("Text\n    https://example.com/__init__.py\n", 4),
        ("Text\n<span>\nhttps://example.com/__init__.py\n", 5),
        ("<div>\ninside\n\t\nhttps://example.com/__init__.py\n", 6),
        ("Text\n[x]: https://example.com/__init__.py\n", 4),
        ("[x]: https://example.com/ok see https://example.com/__init__.py\n", 3),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n~~~\n`\n~~~\n", 5),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n````\n`\n`````\n", 5),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n<div>\n`\n</div>\n", 5),
    )
    for body, line in failures:
        assert_failure(body, line=line)
    passing = (
        ("<https://example.com/__init__.py>\n", "# Fixture\n\n"),
        ("[source](https://example.com/__init__.py)\n", "# Fixture\n\n"),
        ("`https://example.com/__init__.py`\n", "# Fixture\n\n"),
        ("```text\nhttps://example.com/__init__.py\n```\n", "# Fixture\n\n"),
        ("    https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("    - https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("   \thttps://example.com/__init__.py\n", "# Fixture\n\n"),
        ("<div>\nhttps://example.com/__init__.py\n</div>\n", "# Fixture\n\n"),
        ("[source]: https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("[source]:\n https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("[t](\nhttps://example.com/__init__.py\n)\n", "# Fixture\n\n"),
        ("[https://example.com/ok](https://example.com/__init__.py)\n", "# Fixture\n\n"),
        ("# Fixture\n", '---\nversion_basis: {"url":"https://example.com/__init__.py"}\n---\n'),
    )
    for body, prefix in passing:
        result = fixture(body, prefix=prefix)
        assert result[0] == 0 and "  ok    tracked root Markdown" in result[1], result

    # Each regression is an input named in the two QA rounds. The expected result
    # follows the pinned CommonMark parse, including container and link ownership.
    regressions = (
        ("quote prose", "> See https://example.com/__init__.py\n", True),
        ("table cell", "| Source |\n| --- |\n| https://example.com/__init__.py |\n", True),
        ("Setext heading", "https://example.com/__init__.py\n===\n", True),
        ("CRLF", "See https://example.com/__init__.py\r\n", True),
        ("tab list", "- item\n\thttps://example.com/__init__.py\n", True),
        ("four-space list continuation", "- item\n    https://example.com/__init__.py\n", True),
        ("lazy quote", "> Start\nhttps://example.com/__init__.py\n", True),
        ("link text", "[https://example.com/__init__.py](https://example.com/ok)\n", True),
        ("ATX boundary", "Press the ` key.\n## See https://example.com/__init__.py `x`\n", True),
        ("quote boundary", "> Press the ` key.\n>\n> See https://example.com/__init__.py and `ls`.\n", True),
        ("table boundary", "| Press ` | x |\n| --- | --- |\n| https://example.com/__init__.py `y` | z |\n", True),
        ("lazy list owner", "- a\nlazy\n\n    https://example.com/__init__.py\n", True),
        ("nested lazy owner", "- a\nlazy\n\n    - https://example.com/__init__.py\n", True),
        ("nested list owner", "- a\n  - b\n\n  c\n\n    https://example.com/__init__.py\n", True),
        ("list fence dedent", "- ~~~\n  code\nhttps://example.com/__init__.py\n", True),
        ("HTML list dedent", "- a\n\n  <div>\nhttps://example.com/__init__.py\n", True),
        ("definition tail", "[x]: https://example.com/__init__.py see notes\n", True),
        ("paragraph before angle definition", "Text\n[x]: <https://example.com/__init__.py>\n", False),
        ("definition next-line tail", "[x]:\nhttps://example.com/__init__.py and more\n", True),
        ("inline destination tail", "[t](\nhttps://example.com/__init__.py and more\n)\n", True),
        ("thematic break then indent", "* * *\n    https://example.com/__init__.py\n", False),
        ("Setext marker then indent", "===\n    https://example.com/__init__.py\n", True),
        ("inline destination", "[t](\nhttps://example.com/__init__.py)\n", False),
        ("inline destination newline", "[t](\nhttps://example.com/__init__.py\n)\n", False),
        ("list fence", "- ```\n  https://example.com/__init__.py\n  ```\n", False),
        ("nested list fence", "- a\n  - b\n    ~~~\n    https://example.com/__init__.py\n    ~~~\n", False),
        ("quote fence", "> ~~~\n> https://example.com/__init__.py\n> ~~~\n", False),
        ("list definition", "- [source]: https://example.com/__init__.py\n", False),
        ("quote definition", "> [source]: https://example.com/__init__.py\n", False),
        ("link title", "[t](https://example.com/ok \"https://example.com/__init__.py\")\n", False),
        ("inline comment", "Text <!-- https://example.com/__init__.py --> more\n", False),
        ("block HTML", "<div>\nhttps://example.com/__init__.py\n</div>\n", False),
        ("angle URL punctuation", "<https://example.com/__init__.py.>\n", False),
        ("indented list code", "1.     https://example.com/__init__.py\n", False),
        ("nested code span", "`` https://example.com/__init__.py ` ``\n", False),
        ("escaped backtick", "\\` https://example.com/__init__.py\n", True),
        ("URL ending underscores", "See https://example.com/path__\n", True),
        ("emphasis wrapper", "__https://example.com/plain__\n", False),
        ("GFM www residual", "www.example.com/__init__.py\n", False),
        ("single underscores residual", "See https://example.com/_init_.py\n", False),
    )
    for name, body, bare in regressions:
        result = fixture(body)
        expected = "  FAIL  fixture.md:" if bare else "  ok    tracked root Markdown"
        assert result[0] == int(bare) and expected in result[1], (name, result)
    split_span = fixture("https://example.com/__bold `code` https://example.com/plain__\n")
    assert split_span[0] == 1 and split_span[1].count("  FAIL  ") == 1, split_span
    invalid_front_matter = fixture("See https://example.com/__init__.py\n",
                                   prefix="---\nno: matter\n---\n")
    assert invalid_front_matter[0] == 1 and "unsupported front matter" in invalid_front_matter[1], invalid_front_matter

    # Kill the condition in a copied gate: the bare assertion must then fail.
    source = (TOOLS / "check_bare_urls.py").read_text(encoding="utf-8")
    condition = 'if "__" in candidate:'
    assert source.count(condition) == 1
    disabled = source.replace(condition, "if False:")
    mutated = fixture(BARE, gate_source=disabled)
    assert mutated == (0, "  ok    tracked root Markdown has no bare double-underscore URLs (pinned parser)\n"), mutated
    exemption = 'child.type == "link_open" and child.markup == "autolink"'
    assert source.count(exemption) == 1
    disabled = source.replace(exemption, 'child.type == "link_open" and False')
    assert_failure("<https://example.com/__init__.py>\n", gate_source=disabled)
    print(f"  ok    bare URL gate: {len(failures) + sum(bare for _, _, bare in regressions)} failures, "
          f"{len(passing) + sum(not bare for _, _, bare in regressions)} exemptions, "
          "and bare-fixture mutation proof")


if __name__ == "__main__":
    main()
