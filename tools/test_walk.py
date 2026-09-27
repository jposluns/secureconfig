#!/usr/bin/env python3
"""Exercise tracked selection and real gate entry points with temporary Git indexes."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _walk import walk_files

TOOLS = Path(__file__).resolve().parent
GATES = {
    "check_prose_conventions": ("stray.md", "randomised\n"),
    "check_no_dashes": ("stray.md", chr(0x2014) + "\n"),
    "check_shell_blocks": ("stray.md", "```bash\nif\n```\n"),
    "check_bracket_ranges": ("stray.md", "```bash\nprintf '%s\\n' '[a-z]'\n```\n"),
    "check_verify_safety": ("stray.md", "```bash\ncurl -k https://example.com\n```\n"),
    "check_workflow_pins": (".github/workflows/stray.yml",
                            "steps:\n  - uses: actions/checkout@v4\n"),
    "check_site": ("site/stray.html", "<title>T</title><p><div></p></div>"),
    "check_newtab": ("site/stray.html", '<a href="https://example.com">x</a>'),
}


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, timeout=30)


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def gate_case(gate, name, violation):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        git(root, "init", "-q")
        (root / "tools").mkdir()
        for module in (*GATES, "_walk", "_markdown", "_standards", "_gen_common"):
            shutil.copyfile(TOOLS / (module + ".py"), root / "tools" / (module + ".py"))
        write(root, "guide.md", "# Guide\n\n```bash\necho ok\n```\n")
        write(root, "site/index.html", "<!doctype html><title>T</title><p>ok</p>")
        write(root, ".github/workflows/check.yml",
              "steps:\n  - uses: actions/checkout@" + "a" * 40 + "  # v1.2.3\n")
        write(root, ".gitignore", "ignored/\n")
        git(root, "add", ".")
        stray = write(root, name, violation)
        write(root, "ignored/stray.md", violation)
        blocked = stray.parent / "blocked"
        blocked.mkdir()
        write(blocked, "hidden.md", violation)
        blocked.chmod(0)
        env = dict(os.environ, AIQT_NEWTAB_ROOTS="site")

        def run():
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(root / "tools" / (gate + ".py"))],
                cwd=root, env=env, capture_output=True, text=True, timeout=60,
            )
            return result.returncode, result.stdout + result.stderr

        try:
            try:
                list(blocked.iterdir())
            except PermissionError:
                pass
            else:
                raise AssertionError("mode-000 fixture is still readable")
            rc, output = run()
            assert rc == 0 and "stray" not in output, (gate, rc, output)
            # The same violation must be detected as soon as it is tracked.
            git(root, "add", "--", name)
            rc, output = run()
            assert rc == 1 and name in output, (gate, rc, output)
            stray.unlink()
            rc, output = run()
            assert rc != 0 and "stray" in output, (gate, rc, output)
        finally:
            blocked.chmod(0o755)


def selection_cases():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        git(root, "init", "-q")
        names = {"keep.md", "space and\nnewline.md", "nested/keep.md", "site/keep.md",
                 "plugin/keep.md", "ignored.md", "skip/hidden.md", "deep/skip/hidden.md",
                 "nested/skip", "upper.MD", "other.txt"}
        # A basename exclusion applies to files as well as directories.
        for name in names:
            write(root, name, "clean\n")
        write(root, ".gitignore", "ignored.md\nuntracked/\n")
        git(root, "add", ".")
        git(root, "add", "-f", "ignored.md")
        write(root, "untracked/stray.md", "untracked\n")
        (root / "dir-link.md").symlink_to("nested", target_is_directory=True)
        (root / "file-link.md").symlink_to("keep.md")
        git(root, "add", "dir-link.md", "file-link.md")
        selected = {str(p.relative_to(root)) for p in walk_files(root, {"skip"}, {".md"})}
        assert selected == {"keep.md", "space and\nnewline.md", "nested/keep.md",
                            "site/keep.md", "plugin/keep.md", "ignored.md", "file-link.md"}, selected
        assert list(walk_files(root / "site", {"site"}, {".md"})) == [root / "site/keep.md"]
        assert root / "nested/skip" not in list(walk_files(root, {"skip"}))
        assert root / "upper.MD" in list(walk_files(root))
        # A tracked directory replaced by a symlink must not broaden the old walk's coverage.
        (root / "nested").rename(root / "moved")
        (root / "nested").symlink_to("moved", target_is_directory=True)
        assert root / "nested/keep.md" not in list(walk_files(root, {"skip"}, {".md"}))
        (root / "nested").unlink()
        (root / "moved").rename(root / "nested")
        for path, mode in ((root / "nested", 0o755), (root / "keep.md", 0o644)):
            path.chmod(0)
            try:
                try:
                    for selected in walk_files(root, {"skip"}, {".md"}):
                        selected.read_bytes()
                except PermissionError:
                    pass
                else:
                    raise AssertionError("inaccessible tracked input passed")
            finally:
                path.chmod(mode)
        # Real failures, with no fallback or mocked Git output.
        saved_path = os.environ.get("PATH")
        try:
            os.environ["PATH"] = str(root / "absent-bin")
            expect_git_error(root)
        finally:
            if saved_path is None:
                os.environ.pop("PATH", None)
            else:
                os.environ["PATH"] = saved_path
        shutil.rmtree(root / ".git")
        expect_git_error(root)


def expect_git_error(root):
    try:
        list(walk_files(root))
    except OSError as exc:
        assert "git ls-files requires Git and a readable checkout" in str(exc), str(exc)
    else:
        raise AssertionError("Git failure passed")


def main():
    try:
        selection_cases()
        for gate, (name, violation) in GATES.items():
            gate_case(gate, name, violation)
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  tracked walker self-test: {exc}")
        return 1
    print("  ok    tracked selection, fail-closed inputs and all 8 gate entry points")
    return 0


if __name__ == "__main__":
    sys.exit(main())
