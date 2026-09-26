#!/usr/bin/env python3
"""Exercise the shipped placeholder gate against real temporary git indexes."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def git(root, *args):
    subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, timeout=30,
    )


def case(files, expected=1, needle="leftover authoring placeholder", *,
         untracked=(), missing=(), symlink=False, no_git=False):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        git(root, "init", "-q")
        (root / "tools").mkdir()
        for name in ("check_no_placeholders.py", "_walk.py"):
            shutil.copyfile(TOOLS / name, root / "tools" / name)
        for name, content in {"VERSION": "1.0.371\n", **files}.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        if symlink:
            (root / "link.md").symlink_to("VERSION")
        git(root, "add", ".")
        for name in untracked:
            git(root, "rm", "--cached", "--", name)
        for name in missing:
            (root / name).unlink()
        if no_git:
            shutil.rmtree(root / ".git")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(root / "tools/check_no_placeholders.py")],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        output = result.stdout + result.stderr
        prefix = "  ok    " if expected == 0 else "  FAIL  "
        assert result.returncode == expected, (result.returncode, expected, output)
        assert prefix in output and needle in output, output
        if expected == 0:
            assert "  FAIL  " not in output, output
        return 1


def main():
    count = 0
    try:
        # The incident, plus changelog punctuation, version and every id series.
        count += case({"TODO.md": "| Item | Opened by #NNN |\n"},
                      needle="TODO.md:1:20:")
        count += case({"CHANGELOG.md": "- Added a gate (#NNN).\n"})
        count += case({"VERSION": "1.0.NNN\n"})
        for digit in "0123456789":
            for suffix in ("", "-VERIFY", "_FOLLOWUP"):
                count += case({"DONE.md": f"| {digit}.NEW{suffix} | Done |\n"})
        # No directory, Markdown context or familiar document gets an exemption.
        for name in ("CONTRIBUTING.md", "requests/draft.md", ".github/notes.md",
                     ".aiqt/notes.md", "tools/notes.md", "nested/site/notes.md",
                     "docs/notes.MD", "docs/notes.markdown", "docs/notes.mdc"):
            count += case({name: "#NNN\n"})
        for text in ("<!-- #NNN -->\n", "```text\n#NNN\n```\n",
                     "`1.NEW-VERIFY`\n", "> 1.0.NNN\n", "(#NNN),#NNN\n"):
            count += case({"notes.md": text})
        count += case({"notes.md": "#371 (#371) 1.158 3.26 1.0.371\n"},
                      0, "no authoring placeholders")
        count += case({"site/a.md": "#NNN\n", "plugin/a.md": "1.NEW\n",
                       "notes.txt": "1.0.NNN\n", "untracked.md": "#NNN\n"},
                      0, "no authoring placeholders", untracked=("untracked.md",))
        count += case({"lost.md": "clean\n"}, 2, "missing tracked inputs: lost.md",
                      missing=("lost.md",))
        count += case({"bad.md": b"\xff"}, 2, "cannot scan authoring placeholders")
        count += case({}, 2, "symbolic link", symlink=True)
        count += case({}, 2, "VERSION is not tracked", untracked=("VERSION",))
        count += case({}, 2, "cannot scan authoring placeholders", no_git=True)
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  placeholder gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the placeholder gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
