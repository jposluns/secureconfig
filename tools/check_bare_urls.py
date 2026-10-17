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
URL = re.compile(r"https?://[^\s<>\"'`]+", re.I)
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:[ \t]*(?:<)?", re.I)
INLINE = re.compile(r"\]\([ \t]*(?:<)?$")


def visible_lines(lines):
    """Blank matched code spans while keeping every original line boundary."""
    text = "\n".join(lines)
    for start, end, _ in reversed(list(code_spans(text))):
        text = text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]
    return text.split("\n")


def url_token(match):
    """Exclude prose punctuation and unmatched closing parentheses from a URL."""
    token = match.group()
    token = token.rstrip(".,;:!?*~")
    while token.endswith(")") and token.count(")") > token.count("("):
        token = token[:-1]
    return token


def findings(path):
    lines = body_lines(path.read_text(encoding="utf-8"))
    visible = visible_lines(lines)
    fences = Fences()
    html_terminator = None
    reference_next = False
    for number, (raw, line) in enumerate(zip(lines, visible), 1):
        continuation, reference_next = reference_next, False
        if html_terminator is not None:
            if html_terminator.search(raw):
                html_terminator = None
            continue
        if fences.feed(raw) or fences.inside:
            continue
        if raw.expandtabs(4).startswith("    "):
            continue
        html_terminator = html_end(raw)
        if html_terminator is not None:
            if html_terminator.search(raw):
                html_terminator = None
            continue
        definition = REFERENCE.match(line)
        if definition:
            reference_next = line[definition.end():].strip() == ""
        for match in URL.finditer(line):
            token = url_token(match)
            if "__" not in token.replace(r"\_", "_"):
                continue
            start, end = match.start(), match.start() + len(token)
            # Only a whole <URL> is an autolink. Link text remains bare.
            if start and line[start - 1] == "<" and line[end:end + 1] == ">":
                continue
            before = line[:start]
            if INLINE.search(before) or (definition and start >= definition.end()):
                continue
            if continuation and not before.strip():
                continue
            yield f"{path.name}:{number}: bare URL contains __: {token}"


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
