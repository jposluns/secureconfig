#!/usr/bin/env python3
"""Exercise the shipped bare-URL entry point in throwaway tracked repositories."""
import shutil
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
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
    assert result[0] == 1 and result[1].count("  FAIL  fixture.md:") == 1, result
    assert f"  FAIL  fixture.md:{line}: bare URL contains __" in result[1], result


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
        ("1. Item\n    https://example.com/__init__.py\n", 3),
        ("- Parent\n    - https://example.com/__init__.py\n", 4),
        ("Text\n    https://example.com/__init__.py\n", 3),
        ("Text\n<span>\nhttps://example.com/__init__.py\n", 3),
        ("<div>\ninside\n\t\nhttps://example.com/__init__.py\n", 6),
        ("Text\n[x]: https://example.com/__init__.py\n", 3),
        ("[x]: https://example.com/ok see https://example.com/__init__.py\n", 3),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n~~~\n`\n~~~\n", 5),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n````\n`\n`````\n", 5),
        ("Press the ` key.\n\nSee https://example.com/__init__.py\n\n<div>\n`\n</div>\n", 5),
        ("See [docs][d] and https://example.com/__x now.\n\n[d]: https://example.com/__x\n", 3),
        ("See [d] and https://example.com/__x now.\n\n[d]: https://example.com/__x\n", 3),
        ("See [d][] and https://example.com/__x now.\n\n[d]: https://example.com/__x\n", 3),
        ("See ![alt][d] and https://example.com/__x now.\n\n[d]: https://example.com/__x\n", 3),
        ("[https://example.com/__x][d]\n\n[d]: https://example.com/__x\n", 3),
        ("[ref]: https://example.com/__init__.py\n\nSee https://example.com/__init__.py and [label][ref]\n", 5),
        ("[ref]: https://example.com/__init__.py\n\nSee https://example.com/__init__.py and ![alt][ref]\n", 5),
    )
    for body, line in failures:
        assert_failure(body, line=line)
    percent_encoding_failures = (
        ("quote", '[t](https://example.com/x\\"__y) and https://example.com/x%22__y\n'),
        ("opening bracket", "[t](https://example.com/x[__y) and https://example.com/x%5B__y\n"),
        ("closing bracket", "[t](https://example.com/x]__y) and https://example.com/x%5D__y\n"),
        ("opening angle", "[t](<https://example.com/x\\<__y>) and https://example.com/x%3C__y\n"),
        ("closing angle", "[t](<https://example.com/x\\>__y>) and https://example.com/x%3E__y\n"),
        ("backtick", "[t](https://example.com/x`__y) and https://example.com/x%60__y\n"),
        ("space", "[t](<https://example.com/x __y>) and https://example.com/x%20__y\n"),
        ("autolink quote", '<https://example.com/x"__y> and https://example.com/x%22__y\n'),
        ("image quote", '![t](https://example.com/x\\"__y) and https://example.com/x%22__y\n'),
        ("code span cannot supply destination", '[t](https://example.com/x\\"__y) and `[t](https://example.com/x%22__y)` and https://example.com/x%22__y\n'),
    )
    for name, body in percent_encoding_failures:
        try:
            assert_failure(body)
        except AssertionError as exc:
            raise AssertionError(name) from exc
    round_six_failures = (
        ("invalid link position", '[t](https://example.com/x\\"__y) and [u](https://example.com/x%22__y oops)\n'),
        ("escaped autolink position", '[t](https://example.com/x\\"__y) and \\<https://example.com/x%22__y>\n'),
        ("escaped link position", '[t](https://example.com/x\\"__y) and \\[u](https://example.com/x%22__y)\n'),
        ("entity colon destination", '[t](https&#58;//example.com/__x) and https://example.com/__x\n'),
        ("escaped colon destination", '[t](https\\://example.com/__x) and https://example.com/__x\n'),
        ("entity colon image", '![t](https&#58;//example.com/__x) and https://example.com/__x\n'),
        ("entity slash destination", '[t](https:&#47;/example.com/__x) and https://example.com/__x\n'),
    )
    for name, body in round_six_failures:
        try:
            assert_failure(body)
        except AssertionError as exc:
            raise AssertionError(name) from exc
    round_seven_failures = (
        ("autolink before bare", "<https://example.com/__x> and https://example.com/__x\n"),
        ("bare before autolink", "https://example.com/__x and <https://example.com/__x>\n"),
        ("link text beside autolink", "[https://example.com/__x](https://example.com/ok) <https://example.com/__x>\n"),
        ("two autolinks before bare", "<https://example.com/__x> <https://example.com/__x> https://example.com/__x\n"),
        ("image alt beside autolink", "![https://example.com/__x](i.png) <https://example.com/__x>\n"),
        ("link title beside autolink", '[t](https://example.com/ok "https://example.com/__x") <https://example.com/__x>\n'),
        ("nested destination position", '[a [b](https://example.com/__x((y) "t") c](https://example.com/ok) [t](<https&#58;//example.com/__x((y)>)\n'),
        ("control destination position", '[a [b](https://example.com/__x\x01y "t") c](https://example.com/ok) [t](<https&#58;//example.com/__x\x01y>)\n'),
    )
    for name, body in round_seven_failures:
        try:
            assert_failure(body)
        except AssertionError as exc:
            raise AssertionError(name) from exc
    passing = (
        ("<https://example.com/__init__.py>\n", "# Fixture\n\n"),
        ("[source](https://example.com/__init__.py)\n", "# Fixture\n\n"),
        (r"[source](https://example.com/\_\_init.py)" + "\n", "# Fixture\n\n"),
        ("[source](https://example.com/&#95;&#95;init.py)\n", "# Fixture\n\n"),
        ("![source](https://example.com/__init__.py)\n", "# Fixture\n\n"),
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
        ("[t](https://example.com/__x.)\n", "# Fixture\n\n"),
        ("[t](https://example.com/__x*)\n", "# Fixture\n\n"),
        (r"[t](https://example.com/__x\*y)" + "\n", "# Fixture\n\n"),
        (r"[t](https://example.com/__x\))" + "\n", "# Fixture\n\n"),
        ("[t](https://example.com/__x&ampy)\n", "# Fixture\n\n"),
        ("[t](https://example.com/x%22__y)\n", "# Fixture\n\n"),
        ("[t](<https://example.com/__x)>)\n", "# Fixture\n\n"),
        ("https://example.com/&#95&#95x\n", "# Fixture\n\n"),
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
        ("link title", "[t](https://example.com/ok \"https://example.com/__init__.py\")\n", True),
        ("inline comment", "Text <!-- https://example.com/__init__.py --> more\n", True),
        ("block HTML", "<div>\nhttps://example.com/__init__.py\n</div>\n", False),
        ("angle URL punctuation", "<https://example.com/__init__.py.>\n", False),
        ("indented list code", "1.     https://example.com/__init__.py\n", False),
        ("nested code span", "`` https://example.com/__init__.py ` ``\n", False),
        ("escaped backtick", "\\` https://example.com/__init__.py\n", True),
        ("URL ending underscores", "See https://example.com/path__\n", True),
        ("emphasis wrapper", "__https://example.com/plain__\n", True),
        ("GFM www residual", "www.example.com/__init__.py\n", False),
        ("single underscores residual", "See https://example.com/_init_.py and __word__\n", False),
        ("B1 closer in URL", "See https://example.com/__init_ now\n", True),
        ("B1 later closer", "See https://example.com/__all and then_ more\n", True),
        ("N1 external opener", "__note https://example.com/foo__/bar\n", True),
        ("N2 scheme opener", "https://__x__.example.com/\n", True),
        ("image alt", "![https://example.com/__init__.py](i.png)\n", True),
        ("entity underscores", "See https://example.com/&#95;&#95;init.py\n", True),
        ("inline HTML around URL", "<span>https://example.com/__init__.py</span>\n", True),
        ("hard break", "See  \nhttps://example.com/__init__.py\n", True),
        ("nested emphasis", "**See *https://example.com/__init__.py* now**\n", True),
        ("mixed emphasis", "_See **https://example.com/__init__.py** now_\n", True),
        ("quoted indented code", ">     https://example.com/__init__.py\n", False),
        ("N5 Unicode separator", "Text\u2028\u2028    https://example.com/__init__.py\n", True),
        ("disclosed escaped opener", "[t](https://example.com/__x\\()\n", True),
        ("disclosed definition and inline link", "[d]: https://example.com/__x\n\n[t](https://example.com/__x)\n", True),
        ("disclosed definition and autolink", "[d]: https://example.com/__x\n\n<https://example.com/__x>\n", True),
        ("disclosed definition and image", "[d]: https://example.com/__x\n\n![t](https://example.com/__x)\n", True),
        ("disclosed bare CR line", "a\r\rSee https://example.com/__x\n", True),
        ("disclosed code span in image alt", "![`https://example.com/__x`](i.png)\n", True),
        ("authored encoded destination beside bare URL", "[t](https://example.com/x%22__y) and https://example.com/x%22__y\n", True),
        ("entity underscore autolink", "<https://example.com/&#95;&#95;x>\n", False),
        ("escaped underscore autolink", "<https://example.com/\\_\\_x>\n", False),
        ("disclosed entity scheme limit", "See https&#58;//example.com/__x\n", False),
        ("disclosed escaped scheme limit", "See https\\://example.com/__x\n", False),
        ("disclosed autolink URL boundary", "<https://example.com/__x'y>\n", True),
    )
    lines = {"table cell": 5, "ATX boundary": 4, "quote boundary": 5,
             "table boundary": 5, "lazy list owner": 6, "nested lazy owner": 6,
             "nested list owner": 8, "list fence dedent": 5, "HTML list dedent": 6,
             "disclosed definition and inline link": 5,
             "disclosed definition and autolink": 5,
             "disclosed definition and image": 5,
             "disclosed bare CR line": 5}
    for name, body, bare in regressions:
        result = fixture(body)
        expected = f"  FAIL  fixture.md:{lines.get(name, 3)}: bare URL contains __"
        count = result[1].count("  FAIL  fixture.md:")
        assert result[0] == int(bare) and count == int(bare), (name, result)
        assert (expected in result[1]) if bare else ("  ok    tracked root Markdown" in result[1]), (name, result)
    split_span = fixture("https://example.com/__bold `code` https://example.com/plain__\n")
    assert split_span[0] == 1 and split_span[1].count("  FAIL  fixture.md:3:") == 2, split_span
    invalid_front_matter = fixture("See https://example.com/__init__.py\n",
                                   prefix="---\nno: matter\n---\n")
    assert invalid_front_matter[0] == 1 and "unsupported front matter" in invalid_front_matter[1], invalid_front_matter

    # Kill the condition in a copied gate: the bare assertion must then fail.
    source = (TOOLS / "check_bare_urls.py").read_text(encoding="utf-8")
    condition = 'if "__" in decoded:'
    assert source.count(condition) == 1
    disabled = source.replace(condition, "if False:")
    mutated = fixture(BARE, gate_source=disabled)
    assert mutated == (0, "  ok    tracked root Markdown has no bare double-underscore URLs (pinned parser)\n"), mutated
    for exemption, body in (
        ('if child.type == "link_open":', "[x](https://example.com/__init__.py)\n"),
        ('elif child.type == "code_inline":', "`https://example.com/__init__.py`\n"),
    ):
        assert source.count(exemption) == 1
        disabled = source.replace(exemption, exemption.replace(":", " and False:"))
        assert_failure(body, gate_source=disabled)
    doubled = fixture("[https://example.com/__init__.py](https://example.com/__init__.py)\n")
    assert doubled[0] == 1 and doubled[1].count("  FAIL  fixture.md:3:") == 1, doubled
    repeated = fixture("https://example.com/__init__.py and https://example.com/__init__.py\n")
    assert repeated[0] == 1 and repeated[1].count("  FAIL  fixture.md:3:") == 2, repeated
    print(f"  ok    bare URL gate: {len(failures) + len(percent_encoding_failures) + len(round_six_failures) + len(round_seven_failures) + sum(bare for _, _, bare in regressions)} failures, "
          f"{len(passing) + sum(not bare for _, _, bare in regressions)} exemptions, "
          "and bare, href and code-span mutation proofs")


if __name__ == "__main__":
    main()
