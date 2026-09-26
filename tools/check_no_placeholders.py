#!/usr/bin/env python3
"""Refuse authoring placeholders in tracked Markdown and the root VERSION.

Scan raw text, including comments, quotations and code blocks. Generated site/ and
plugin/ trees are excluded. There are no exemptions. Match standalone PR, id and
version markers, plus the case-sensitive stale completion phrase. Ids have a
single digit and optionally a hyphen followed by one uppercase ASCII word.
Token boundaries use ASCII letters and digits. An adjacent underscore is a
boundary unless its other neighbour is an ASCII letter or digit, so Markdown
underscore emphasis is checked while underscore-joined identifiers stay clean.

Git supplies the tracked set; read only the selected paths directly.
Missing tracked inputs, unreadable files and invalid UTF-8 are errors, not passes.
No network or third-party Python modules are used.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# Do not match a prefix of a longer token or an unsupported id suffix.
# A sentence-ending dot is punctuation; a dot followed by an ASCII alphanumeric
# extends an id. Underscores join identifiers only next to ASCII alphanumerics.
PLACEHOLDER = re.compile(
    r"(?<![A-Za-z0-9])(?<![A-Za-z0-9]_)#NNN(?![A-Za-z0-9]|_[A-Za-z0-9])"
    r"|(?<![A-Za-z0-9.])(?<![A-Za-z0-9]_)[0-9]\.NEW(?:-[A-Z]+)?"
    r"(?![A-Za-z0-9]|-[A-Za-z0-9]|_[A-Za-z0-9]|\.[A-Za-z0-9])"
    r"|(?<![A-Za-z0-9])(?<![A-Za-z0-9]_)[0-9]+\.[0-9]+\.NNN"
    r"(?![A-Za-z0-9]|_[A-Za-z0-9])"
    r"|Done in this draft"
)
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
        for relative in sorted(wanted):
            path = root / relative
            if path.is_symlink():
                raise ValueError(f"{relative}: tracked input is a symbolic link")
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in PLACEHOLDER.finditer(line):
                    findings.append(
                        f"{relative}:{number}:{match.start() + 1}: "
                        f"leftover authoring placeholder {match.group()!r}"
                    )
    except (OSError, UnicodeError, ValueError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  cannot scan authoring placeholders: {exc}")
        return 2
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    no authoring placeholders in {len(wanted)} tracked Markdown/VERSION files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
