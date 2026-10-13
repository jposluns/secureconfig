#!/usr/bin/env python3
"""Refuse authoring placeholders in tracked Markdown and the root VERSION.

Scan raw text, including comments, quotations and code blocks. Generated site/ and
plugin/ trees are excluded. There are no path exemptions. Match standalone PR, id
and version markers, plus the case-sensitive stale completion phrase. Ids have a
single digit and optionally a hyphen followed by one uppercase ASCII word.
Token boundaries use ASCII letters and digits. An adjacent underscore is a
boundary unless its other neighbour is an ASCII letter or digit, so Markdown
underscore emphasis is checked while underscore-joined identifiers stay clean.

The shorter PR marker #N is refused everywhere, including code spans and fences,
except in three exact notations: `#N`, `(#N)`, and the literal prefix
`Merge pull request #N from . Only the characters immediately around the match
on the same line determine the exemption; Markdown structure is not interpreted.
All markers matched by PLACEHOLDER remain refused everywhere.

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
# The shorter PR marker has the same boundaries, with exact notation exemptions.
SHORT_PR = re.compile(r"(?<![A-Za-z0-9])(?<![A-Za-z0-9]_)#N(?![A-Za-z0-9]|_[A-Za-z0-9])")
MARKDOWN = {".md", ".markdown", ".mdc"}
GENERATED = {"site", "plugin"}


def exact_notation(line, match):
    """Whether this match has one of the three allowed literal contexts."""
    before, after = line[:match.start()], line[match.end():]
    return any(
        before.endswith(prefix) and after.startswith(suffix)
        for prefix, suffix in (
            ("`", "`"),
            ("`(", ")`"),
            ("`Merge pull request ", " from "),
        )
    )


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
            lines = path.read_text(encoding="utf-8").splitlines()
            for number, line in enumerate(lines, 1):
                matches = list(PLACEHOLDER.finditer(line)) + [
                    match for match in SHORT_PR.finditer(line)
                    if not exact_notation(line, match)
                ]
                for match in sorted(matches, key=lambda match: match.start()):
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
