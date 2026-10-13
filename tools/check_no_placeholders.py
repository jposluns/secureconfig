#!/usr/bin/env python3
"""Refuse authoring placeholders in tracked Markdown and the root VERSION.

Scan raw text, including comments, quotations and code blocks. Generated site/ and
plugin/ trees are excluded. There are no path exemptions. Match standalone PR, id
and version markers, plus the case-sensitive stale completion phrase. Ids have a
single digit and optionally a hyphen followed by one uppercase ASCII word.
Token boundaries use ASCII letters and digits. An adjacent underscore is a
boundary unless its other neighbour is an ASCII letter or digit, so Markdown
underscore emphasis is checked while underscore-joined identifiers stay clean.

The PR marker #NNN is refused everywhere. The shorter #N is refused except inside
an inline code span, where it names the pull-request reference format. Spans follow
CommonMark: a backtick run opens a span that the next run of the same length closes,
and a backslash-escaped backtick opens nothing. A run with no such closer is literal
text, so #N after an unclosed backtick is still refused. Spans are read twice, within
each line and within each paragraph, taken as consecutive non-blank lines. A line
read alone takes a backtick that closes a span from the line before as an opener,
and a paragraph so taken can run across a heading, list item or table row that
Markdown separates, so #N is exempt only where both readings put it in a span.

Fenced code has no spans, so #N there is refused even between backticks. A fence
opens with three or more backticks (none after them on the line) or tildes, after
any indentation and block-quote or list markers. It closes on a line holding only
indentation, block-quote markers and at least as many of the same character,
indented at most three columns past the opener. Container blocks are not tracked,
so a fence does not close where its list item or block quote ends. Raw HTML is not
modelled: a span inside a comment or tag, as in <!-- `#N` -->, still exempts #N.

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
# The shorter PR marker has the same boundaries, but an inline code span exempts it.
SHORT_PR = re.compile(r"(?<![A-Za-z0-9])(?<![A-Za-z0-9]_)#N(?![A-Za-z0-9]|_[A-Za-z0-9])")
# A backslash escapes one ASCII punctuation character; otherwise take a whole backtick run.
BACKTICK_RUN = re.compile(r"\\[!-/:-@\[-`{-~]|`+")
# A fence may follow indentation and block-quote or list markers. A backtick fence has no
# backtick after its run, so a line such as ```a``` stays inline code.
FENCE = re.compile(r"[ \t>]*(?:(?:[-+*]|[0-9]{1,9}[.)])(?=[ \t])[ \t>]*)*(`{3,}(?!.*`)|~{3,})")
MARKDOWN = {".md", ".markdown", ".mdc"}
GENERATED = {"site", "plugin"}


def code_spans(text):
    """Return the content range of each inline code span in text."""
    spans = []
    position = 0
    while True:
        opener = BACKTICK_RUN.search(text, position)
        if opener is None:
            return spans
        position = opener.end()
        if opener.group().startswith("\\"):
            continue
        # Backslashes are literal inside a span, so only a run of equal length closes it.
        closer = re.compile(rf"(?<!`)`{{{len(opener.group())}}}(?!`)").search(text, position)
        if closer is not None:
            spans.append((position, closer.start()))
            position = closer.end()


def exempt_spans(lines):
    """Return, for each line, the ranges where a code span exempts the shorter PR marker."""
    paragraphs = [[]]
    fence = None
    for index, line in enumerate(lines):
        if fence is not None:
            # Fenced code has no spans; only the same character, at least as long, closes it.
            run = fence.group(1)
            closer = re.fullmatch(rf"[ \t>]*({run[0]}{{{len(run)},}})[ \t]*", line)
            if closer is not None and closer.start(1) <= fence.start(1) + 3:
                fence = None
            continue
        fence = FENCE.match(line)
        if fence is None and line.strip(" \t"):
            paragraphs[-1].append(index)
        else:
            paragraphs.append([])
    exempt = [[] for _ in lines]
    for paragraph in paragraphs:
        # Keep only what both the paragraph and the line read alone put in a span.
        joined = code_spans("\n".join(lines[index] for index in paragraph))
        offset = 0
        for index in paragraph:
            for start, end in code_spans(lines[index]):
                for joined_start, joined_end in joined:
                    low = max(start, joined_start - offset)
                    high = min(end, joined_end - offset)
                    if low < high:
                        exempt[index].append((low, high))
            offset += len(lines[index]) + 1
    return exempt


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
            for number, (line, spans) in enumerate(zip(lines, exempt_spans(lines)), 1):
                matches = list(PLACEHOLDER.finditer(line)) + [
                    match for match in SHORT_PR.finditer(line)
                    if not any(start <= match.start() < end for start, end in spans)
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
