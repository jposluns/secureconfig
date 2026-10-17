#!/usr/bin/env python3
"""Exercise the shipped bare-URL entry point in throwaway tracked repositories."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _walk import isolated_git_environment

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
        if gate_source is not None:
            (root / "tools/check_bare_urls.py").write_text(gate_source, encoding="utf-8")
        (root / "fixture.md").write_text(prefix + body, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "fixture.md"], cwd=root, check=True,
                       capture_output=True)
        result = subprocess.run([sys.executable, "-I", "-B",
                                 str(root / "tools/check_bare_urls.py")], cwd=root,
                                capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout + result.stderr


def assert_failure(body, prefix="# Fixture\n\n", line=3, gate_source=None):
    result = fixture(body, gate_source, prefix)
    assert result[0] == 1 and f"  FAIL  fixture.md:{line}: bare URL contains __" in result[1], result


def main():
    assert_failure(BARE)
    assert_failure("[https://example.com/__init__.py](https://example.com/ok)\n")
    assert_failure(r"See https://example.com/\_\_init.py" + "\n")
    assert_failure("[source]:\n\nhttps://example.com/__init__.py\n", line=5)
    passing = (
        ("<https://example.com/__init__.py>\n", "# Fixture\n\n"),
        ("[source](https://example.com/__init__.py)\n", "# Fixture\n\n"),
        ("`https://example.com/__init__.py`\n", "# Fixture\n\n"),
        ("```text\nhttps://example.com/__init__.py\n```\n", "# Fixture\n\n"),
        ("    https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("   \thttps://example.com/__init__.py\n", "# Fixture\n\n"),
        ("<div>\nhttps://example.com/__init__.py\n</div>\n", "# Fixture\n\n"),
        ("[source]: https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("[source]:\n https://example.com/__init__.py\n", "# Fixture\n\n"),
        ("# Fixture\n", '---\nversion_basis: {"url":"https://example.com/__init__.py"}\n---\n'),
    )
    for body, prefix in passing:
        result = fixture(body, prefix=prefix)
        assert result[0] == 0 and "  ok    tracked root Markdown" in result[1], result

    # Kill the condition in a copied gate: the bare assertion must then fail.
    source = (TOOLS / "check_bare_urls.py").read_text(encoding="utf-8")
    condition = 'if "__" not in token.replace(r"\\_", "_"):'
    assert source.count(condition) == 1
    disabled = source.replace(condition, "if True:")
    try:
        assert_failure(BARE, gate_source=disabled)
    except AssertionError:
        pass
    else:
        raise AssertionError("bare fixture still passed after disabling the check")
    print("  ok    bare URL gate: 4 failures, 10 exemptions, and bare-fixture mutation proof")


if __name__ == "__main__":
    main()
