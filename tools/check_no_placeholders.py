#!/usr/bin/env python3
"""Refuse authoring placeholders in tracked Markdown and the root VERSION.

Scan raw text, including comments, quotations and code blocks. Generated site/ and
plugin/ trees are excluded. There were no existing matches in the tracked corpus
when this gate was added, so there are no exemptions. Matching the literal PR
marker also catches its parenthesized form. An id's suffix does not excuse it.

Git supplies the tracked set; the shared fail-closed walker supplies files on disk.
Missing tracked inputs, unreadable files and invalid UTF-8 are errors, not passes.
No network or third-party Python modules are used.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _walk import walk_files  # noqa: E402

PLACEHOLDER = re.compile(r"#NNN|[0-9]\.NEW[\w.-]*|1\.0\.NNN")
MARKDOWN = {".md", ".markdown", ".mdc"}
GENERATED = {"site", "plugin"}


def main():
    root = Path(__file__).resolve().parent.parent
    findings = []
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached"], cwd=root, check=True,
            capture_output=True, timeout=30,
        )
        tracked = {Path(os.fsdecode(name)) for name in result.stdout.split(b"\0") if name}
        wanted = {
            path for path in tracked
            if path.parts[0] not in GENERATED
            and (path.suffix.lower() in MARKDOWN or path == Path("VERSION"))
        }
        if Path("VERSION") not in wanted:
            raise ValueError("VERSION is not tracked")
        seen = set()
        for path in sorted(walk_files(root, skip_dirs={".git"})):
            relative = path.relative_to(root)
            if relative not in wanted:
                continue
            if path.is_symlink():
                raise ValueError(f"{relative}: tracked input is a symbolic link")
            seen.add(relative)
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in PLACEHOLDER.finditer(line):
                    findings.append(
                        f"{relative}:{number}:{match.start() + 1}: "
                        f"leftover authoring placeholder {match.group()!r}"
                    )
        missing = wanted - seen
        if missing:
            raise ValueError("missing tracked inputs: " + ", ".join(map(str, sorted(missing))))
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  cannot scan authoring placeholders: {exc}")
        return 2
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    no authoring placeholders in {len(seen)} tracked Markdown/VERSION files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
