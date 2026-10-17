#!/usr/bin/env python3
"""Reject bare double-underscore URLs in tracked root Markdown bodies.

With the pinned CommonMark parser, inspect every inline token, including those in
headings, tables, lists and quotes at any depth. Join rendered text across inline
formatting and restore underscore markers that open inside a URL, since
``__`` can split a URL into emphasis tokens. A URL containing
``__`` (also when written ``\\_\\_``) is bare in rendered text, including link
text. Link and autolink destinations and code spans are exempt. Block code, HTML
blocks and reference definitions produce no inline tokens. Front matter is excluded.
Without the pin, the existing lexical scan runs with an advisory SKIP; CI requires
the parser. Neither path fetches links.
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences, body_lines
from _walk import walk_files
from check_verify_marking import ParserUnavailable, code_spans, gate_parser, html_end

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


def lexical_findings(path):
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


def parsed_findings(path, parser):
    """Scan rendered inline text, never link targets or code-span contents."""
    lines = body_lines(path.read_text(encoding="utf-8"))
    for token in parser.parse("\n".join(lines)):
        if token.type != "inline":
            continue
        pieces = []
        line = token.map[0] + 1
        autolink = 0
        strong = []

        def scan():
            if not pieces:
                return
            rendered = "".join(part for part, _ in pieces)
            positions = []
            for part, part_line in pieces:
                positions.extend([part_line] * len(part))
            for match in URL.finditer(rendered):
                candidate = url_token(match)
                if "__" in candidate:
                    yield (f"{path.name}:{positions[match.start()]}: "
                           f"bare URL contains __: {candidate}")
            pieces.clear()
            strong[:] = [False] * len(strong)

        for child in token.children or ():
            if child.type == "link_open" and child.markup == "autolink":
                yield from scan()
                autolink += 1
            elif child.type == "link_close" and child.markup == "autolink":
                autolink -= 1
            elif child.type == "text":
                if not autolink:
                    pieces.append((child.content, line))
            elif child.type == "strong_open" and child.markup == "__":
                # Surrounding emphasis is not part of the URL; an opener inside
                # its current text prefix is. Restore only the latter pair.
                so_far = "".join(part for part, _ in pieces)
                inside_url = any(match.end() == len(so_far) for match in URL.finditer(so_far))
                strong.append(inside_url)
                if inside_url and not autolink:
                    pieces.append(("__", line))
            elif child.type == "strong_close" and child.markup == "__":
                if strong.pop() and not autolink:
                    pieces.append(("__", line))
            elif child.type in ("softbreak", "hardbreak"):
                if not autolink:
                    pieces.append(("\n", line))
                line += 1
            elif child.type in ("code_inline", "html_inline", "image"):
                yield from scan()
        yield from scan()


def main(argv=None):
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--require-parser", action="store_true",
                           help="fail if the shared pinned parser is unavailable")
    args = arguments.parse_args(argv)
    try:
        try:
            parser = gate_parser(required=True)
        except ParserUnavailable as exc:
            if args.require_parser or os.environ.get("CI"):
                raise
            parser = None
            print(f"  SKIP  bare URL parser path: {exc} (lexical fallback runs)")
        errors = []
        for path in walk_files(ROOT, suffixes={".md"}):
            if path.parent == ROOT:
                errors.extend(parsed_findings(path, parser) if parser else lexical_findings(path))
        for error in errors:
            print(f"  FAIL  {error}")
        if errors:
            return 1
        mode = "pinned parser" if parser else "lexical fallback"
        print(f"  ok    tracked root Markdown has no bare double-underscore URLs ({mode})")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"  FAIL  check_bare_urls.py could not scan tracked Markdown: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
