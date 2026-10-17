#!/usr/bin/env python3
"""Reject bare body URLs containing a double underscore in tracked root Markdown.

This is a raw-text guard against CommonMark emphasis changing a cited URL. It is
deliberately narrower than a link checker: it does not fetch or render links.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences, body_lines
from _walk import walk_files
from check_verify_marking import code_spans, html_end

ROOT = Path(__file__).resolve().parents[1]
URL = re.compile(r"https?://[^\s<>\"'`\[\]]+", re.I)
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:[ \t]*", re.I)
INLINE = re.compile(r"\]\([ \t]*(?:<)?$")
LIST = re.compile(r"^( {0,3}| {4,})(?:[-+*]|[0-9]{1,9}[.)])([ \t]+)")
DESTINATION = re.compile(r"[ \t]*(?:<[^>]+>|\S+)")
ATX = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+|$)")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")


def visible_lines(lines, prose, starts):
    """Blank spans only within consecutive prose lines of one paragraph."""
    visible = lines[:]
    start = 0
    while start < len(lines):
        if not prose[start]:
            start += 1
            continue
        end = start + 1
        while end < len(lines) and prose[end] and end not in starts:
            end += 1
        text = "\n".join(lines[start:end])
        for first, last, _ in reversed(list(code_spans(text))):
            text = text[:first] + re.sub(r"[^\n]", " ", text[first:last]) + text[last:]
        visible[start:end] = text.split("\n")
        start = end
    return visible


def url_token(match):
    """Exclude prose punctuation and unmatched closing parentheses from a URL."""
    token = match.group()
    token = token.rstrip(".,;:!?*~")
    while token.endswith(")") and token.count(")") > token.count("("):
        token = token[:-1]
    return token


def findings(path):
    lines = body_lines(path.read_text(encoding="utf-8"))
    fences = Fences()
    html_terminator = None
    paragraph = False
    list_content = 0
    prose = []
    starts = set()
    for raw in lines:
        blank = not raw.strip()
        if html_terminator is not None:
            if html_terminator.search(raw) or (html_terminator.pattern == r"^ *$" and blank):
                html_terminator = None
                paragraph = False
            prose.append(False)
            continue
        if fences.feed(raw) or fences.inside:
            paragraph = False
            prose.append(False)
            continue
        if blank:
            paragraph = False
            prose.append(False)
            continue
        expanded = raw.expandtabs(4)
        indent = len(expanded) - len(expanded.lstrip(" "))
        if list_content and indent < list_content:
            list_content = 0
        candidate = LIST.match(expanded)
        marker = candidate if candidate and (indent <= 3 or
                        (list_content and list_content <= indent < list_content + 4)) else None
        # A list marker is prose even when its indentation reaches four columns.
        if marker:
            list_content = len(marker.group(0))
        code_indent = list_content + 4 if list_content else 4
        if not marker and indent >= code_indent and not paragraph:
            prose.append(False)
            continue
        html_terminator = html_end(raw, continuing=paragraph)
        if html_terminator is not None:
            if html_terminator.search(raw) or (html_terminator.pattern == r"^ *$" and blank):
                html_terminator = None
            paragraph = False
            prose.append(False)
            continue
        if not paragraph or marker:
            starts.add(len(prose))
        prose.append(True)
        paragraph = not ((REFERENCE.match(raw) and not paragraph) or
                         ATX.match(raw) or SETEXT.match(raw))

    visible = visible_lines(lines, prose, starts)
    paragraph = False
    reference_next = False
    for index, (raw, line) in enumerate(zip(lines, visible)):
        if not prose[index]:
            paragraph = False
            reference_next = False
            continue
        continuation, reference_next = reference_next, False
        definition = REFERENCE.match(line) if not paragraph else None
        destination = DESTINATION.match(line, definition.end()) if definition else None
        if definition and destination is None:
            reference_next = True
        next_destination = DESTINATION.match(line) if continuation else None
        for match in URL.finditer(line):
            token = url_token(match)
            if "__" not in token.replace(r"\_", "_"):
                continue
            start, end = match.start(), match.start() + len(token)
            # Only a whole <URL> is an autolink. Link text remains bare.
            if start and line[start - 1] == "<" and line[end:end + 1] == ">":
                continue
            before = line[:start]
            if INLINE.search(before):
                continue
            if destination and destination.start() <= start and end <= destination.end():
                continue
            if next_destination and next_destination.start() <= start and end <= next_destination.end():
                continue
            if (index and INLINE.search(visible[index - 1]) and
                    index + 1 < len(lines) and re.match(r"^[ \t]*\)[ \t]*$", lines[index + 1]) and
                    not before.strip()):
                continue
            yield f"{path.name}:{index + 1}: bare URL contains __: {token}"
        paragraph = not (definition or continuation or ATX.match(raw) or SETEXT.match(raw))


def main():
    try:
        errors = []
        for path in walk_files(ROOT, suffixes={".md"}):
            if path.parent == ROOT:
                errors.extend(findings(path))
        for error in errors:
            print(f"  FAIL  {error}")
        if errors:
            return 1
        print("  ok    tracked root Markdown has no bare double-underscore URLs")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"  FAIL  check_bare_urls.py could not scan tracked Markdown: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
