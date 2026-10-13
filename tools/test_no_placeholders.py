#!/usr/bin/env python3
"""Exercise the recorded cases through the shipped gate against real temporary git indexes."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from _walk import isolated_git_environment  # noqa: E402


def git(root, *args):
    subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, timeout=30,
    )


@isolated_git_environment()
def case(files, expected=1, needle="leftover authoring placeholder", *,
         untracked=(), missing=(), unreadable=(), blocked_dirs=(),
         symlink=False, no_git=False, absent=()):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        git(root, "init", "-q")
        (root / "tools").mkdir()
        shutil.copyfile(TOOLS / "check_no_placeholders.py",
                        root / "tools/check_no_placeholders.py")
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
        modes = []
        try:
            for name in blocked_dirs:
                (root / name).mkdir(parents=True, exist_ok=True)
            for name in (*unreadable, *blocked_dirs):
                path = root / name
                modes.append((path, path.stat().st_mode))
                path.chmod(0)
                # Verify real denied access, including on privileged test runners.
                try:
                    if name in blocked_dirs:
                        list(path.iterdir())
                    else:
                        path.read_bytes()
                except PermissionError:
                    pass
                else:
                    raise AssertionError(f"fixture is still readable: {name}")
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(root / "tools/check_no_placeholders.py")],
                cwd=root, capture_output=True, text=True, timeout=30,
            )
        finally:
            for path, mode in reversed(modes):
                path.chmod(mode)
        output = result.stdout + result.stderr
        prefix = "  ok    " if expected == 0 else "  FAIL  "
        assert result.returncode == expected, (result.returncode, expected, output)
        assert prefix in output and needle in output, output
        for text in absent:
            assert text not in output, output
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
        for version in ("1.0.NNN", "1.1.NNN", "2.0.NNN", "12.345.NNN"):
            count += case({"VERSION": version + "\n"})
        for digit in "0123456789":
            for suffix in ("", "-VERIFY"):
                count += case({"DONE.md": f"| {digit}.NEW{suffix} | Done |\n"},
                              needle=f"'{digit}.NEW{suffix}'")
        # No directory, Markdown context or familiar document gets an exemption.
        for name in ("CONTRIBUTING.md", "requests/draft.md", ".github/notes.md",
                     ".aiqt/notes.md", "tools/notes.md", "nested/site/notes.md",
                     "docs/notes.MD", "docs/notes.markdown", "docs/notes.mdc"):
            count += case({name: "#NNN\n"})
        for text in ("<!-- #NNN -->\n", "```text\n#NNN\n```\n",
                     "`1.NEW-VERIFY`\n", "> 1.0.NNN\n", "(#NNN),#NNN\n",
                     "(#NNN)", "#NNN.", "`1.NEW`", "|1.NEW|", "**1.0.NNN**",
                     "1.NEW.", "(1.NEW-VERIFY).", "**2.0.NNN**"):
            count += case({"notes.md": text})
        # Underscore delimiters, Markdown emphasis and comment terminators expose placeholders.
        for text in ("_#NNN_", "__#NNN__", "_1.NEW_", "__1.NEW__",
                     "_1.NEW-VERIFY_", "_1.0.NNN_", "*1.NEW*",
                     "_#NNN", "#NNN_", "_1.NEW", "1.NEW_", "_12.345.NNN",
                     "<!--1.NEW-->", "<!--1.NEW-VERIFY-->", "<!--#NNN-->", "<!--1.0.NNN-->",
                     "1.NEW-", "1.NEW--"):
            count += case({"notes.md": text})
        # Embedded and longer tokens, including unsupported id suffixes, are clean.
        for text in ("ldap1.NEW_PASSWORD", "v1.NEWS.md", "#NNNN", "release1.0.NNN",
                     "a#NNN", "#NNN1", "#NNNs",
                     "a1.NEW", "11.NEW", "12.NEW", "12.NEW-VERIFY", ".1.NEW", "1.0.NEW",
                     "1.NEWS", "1.new", "1.NEW1", "1.NEW-Followup", "1.NEW-verify",
                     "1.NEW-VERIFY2", "1.NEW-VERIFY_MORE", "1.NEW-VERIFY-MORE",
                     "1.NEW.md", "1.NEW-VERIFY.md", "1.NEW_FOLLOWUP",
                     "v1.1.NNN", "release2.0.NNN", "1.1.NNNN",
                     "2.0.NNN1", "12.345.NNN_suffix", "1.0.NNNs",
                     "release1.0.NNNN", "x_#NNN", "1.NEW_PASSWORD", "MY_1.NEW"):
            count += case({"notes.md": text}, 0, "no authoring placeholders")
        for text in ("Done in this draft", "Done in this draft, #363.",
                     "<!-- Done in this draft -->", "`Done in this draft`",
                     "> Done in this draft", "```text\nDone in this draft\n```"):
            count += case({"DONE.md": text}, needle="'Done in this draft'")
        for text in ("done in this draft", "Done in this Draft", "Done in this DRAFT",
                     "Done in a draft", "Done, #363."):
            count += case({"DONE.md": text}, 0, "no authoring placeholders")
        # A bare #N in prose is the #495 incident. Inside an inline code span it names the
        # reference format; #NNN stays refused even there. An unclosed run opens no span.
        count += case({"DONE.md": "Done, #N."}, needle="DONE.md:1:7:")
        for text in ("#N", "(#N)", "#N.", "(#N),#N", "_#N_", "__#N__", "*#N*",
                     "<!-- #N -->", "<!--#N-->", "> #N", "_#N", "#N_",
                     "`#N", "``#N`", "`#N``", "\\`#N\\`", "`a` #N `b`",
                     "`x\n#N`", "```text\n#N\n```"):
            count += case({"notes.md": text}, needle="'#N'")
        count += case({"notes.md": "`#N` #N\n"}, needle="notes.md:1:6:",
                      absent=("notes.md:1:2:",))
        count += case({"notes.md": "`#N`\n#N\n"}, needle="notes.md:2:1:",
                      absent=("notes.md:1:",))
        for text in ("`#NNN`", "``#NNN``", "`(#NNN)`", "`` `#NNN` ``"):
            count += case({"notes.md": text}, needle="'#NNN'")
        for text in ("`#N`", "``#N``", "`(#N)`", "`` `#N` ``", "``#N` and `#N``",
                     "`Merge pull request #N from ...`",
                     "every `(#N)` suffix and `#N` reference",
                     "#NN", "a#N", "#N1", "#Ns", "#Nx", "x_#N", "#N_suffix", "N#N", "#n"):
            count += case({"notes.md": text}, 0, "no authoring placeholders")
        # Fenced code has no spans. Only a run of the fence's own character, at least as long
        # and alone on its line, closes it; container markers may precede the opener.
        for text in ("```text\n`#N`\n```", "~~~text\n`#N`\n~~~", "````\n```\n`#N`\n````",
                     "~~~\n```\n`#N`\n~~~", "```\n~~~\n`#N`\n```", "```\n``` x\n`#N`\n```",
                     "```\n    ```\n`#N`\n```", "```\n\n`#N`", "~~~ `#N`\n~~~",
                     "- ```text\n  `#N`\n  ```", "> ```\n> `#N`\n> ```",
                     "1. item\n\n   ~~~\n   `#N`\n   ~~~"):
            count += case({"notes.md": text}, needle="'#N'")
        for text in ("```\nx\n```\n`#N`", "~~~~\n~~~\n~~~~\n`#N`", "   ```\nx\n```\n`#N`",
                     "- ```\n  x\n  ```\n\n`#N`", "```a`\n\n`#N`", "``a\n`#N` b``"):
            count += case({"notes.md": text}, 0, "no authoring placeholders")
        # A span closed on the next line does not open another there, and a line's own pairs
        # must agree with its paragraph's. Raw HTML is not modelled, so a comment stays clean.
        count += case({"notes.md": "see `a\nb` #N `c`"}, needle="notes.md:2:4:")
        count += case({"notes.md": "`a\n# h `x` #N `y`"}, needle="notes.md:2:9:")
        count += case({"notes.md": "<!-- `#N` -->"}, 0, "no authoring placeholders")
        count += case({"notes.md": "#371 (#371) 1.158 3.26 1.0.371\n"},
                      0, "no authoring placeholders")
        count += case({"site/a.md": "#NNN\n", "plugin/a.md": "1.NEW\n",
                       "notes.txt": "1.0.NNN\n", "untracked.md": "#NNN\n"},
                      0, "no authoring placeholders", untracked=("untracked.md",))
        count += case({"lost.md": "clean\n"}, 2, "lost.md",
                      missing=("lost.md",))
        for name in ("untracked/locked", "site/locked", "plugin/locked"):
            count += case({}, 0, "no authoring placeholders", blocked_dirs=(name,))
        for name in ("notes.md", "VERSION"):
            count += case({name: "clean\n"}, 2, "Permission denied", unreadable=(name,))
        count += case({"docs/notes.md": "clean\n"}, 2, "Permission denied",
                      blocked_dirs=("docs",))
        count += case({}, 2, "VERSION", missing=("VERSION",))
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
