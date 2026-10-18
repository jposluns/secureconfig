#!/usr/bin/env python3
"""Reject bare double-underscore URLs in tracked root Markdown bodies.

With the pinned CommonMark parser, inspect every inline token, including those in
headings, tables, lists and quotes at any depth. Count URL occurrences in raw
inline content, then account for parsed link destinations, image sources and code
spans. Every remaining occurrence is bare, including link text and image alt text.
Escaped underscores and character references count. Block code, HTML blocks and
reference definitions produce no inline tokens. Front matter is excluded.
Without the pin, the existing lexical scan runs with an advisory SKIP; CI requires
the parser. Neither path fetches links.
"""
import argparse
from collections import Counter
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences, body_lines
from _walk import walk_files
from check_verify_marking import ParserUnavailable, code_spans, gate_parser, html_end
from version_basis import split as split_front_matter

ROOT = Path(__file__).resolve().parents[1]
URL = re.compile(r"https?://[^\s<>\"'`\[\]]+", re.I)
INLINE_DESTINATION = re.compile(r"\]\([ \t\n]*(<?)")
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


def url_token(match, protected_closers=0):
    """Exclude prose punctuation and unmatched closing parentheses from a URL."""
    token = match.group() if hasattr(match, "group") else match
    while True:
        trimmed = token.rstrip(".,;:!?*~")
        if trimmed != token:
            token = trimmed
        elif token.endswith(")") and token.count(")") > token.count("(") + protected_closers:
            token = token[:-1]
        else:
            break
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
    """Count raw URL occurrences that the parse does not assign to exempt tokens."""
    from markdown_it.common.utils import unescapeAll

    def decoded_url(raw):
        # Preserve escaped closing parentheses while trimming link syntax.
        escaped_closers = len(re.findall(r"(?<!\\)(?:\\\\)*\\\)", raw))
        return url_token(unescapeAll(raw), escaped_closers)

    def parsed_position(content, start, end, autolink, decoded, original):
        """Check that this source span belongs to a parsed destination."""
        sentinel = f"https://bare-url-probe.invalid/path{start}x{end}"
        if sentinel in content:
            return False
        probe = content[:start] + sentinel + content[end:]
        def child_stream(children):
            stream = []
            inside_autolink = False
            for child in children:
                if child.type in ("link_open", "image"):
                    stream.append((child.type, child.info == "auto",
                                   child.attrGet("href" if child.type == "link_open" else "src")))
                    if child.type == "link_open" and child.info == "auto":
                        inside_autolink = True
                else:
                    stream.append((child.type, "" if child.type == "text" and inside_autolink
                                   else child.content))
                    if child.type == "link_close" and inside_autolink:
                        inside_autolink = False
            return stream

        before = child_stream(original)
        after_children = parser.parseInline(
            probe, {"references": env.get("references", {})})[0].children or ()
        after = child_stream(after_children)
        if len(before) != len(after):
            return False
        changed = [index for index, (old, new) in enumerate(zip(before, after))
                   if old != new]
        if len(changed) != 1:
            return False
        old, new = before[changed[0]], after[changed[0]]
        return (old[0] in ("link_open", "image") and old[:2] == new[:2]
                and old[1] == autolink
                and new[2] == sentinel and old[2] is not None
                and parser.normalizeLink(old[2]) == parser.normalizeLink(decoded))

    def raw_destinations(content, children):
        """Count whole raw URLs at parsed inline link and image destinations."""
        destinations = Counter()
        spans = [(first, last) for first, last, _ in code_spans(content)]
        starts = {(match.end(), bool(match.group(1)), False)
                  for match in INLINE_DESTINATION.finditer(content)}
        for start, angle, autolink in starts:
            if any(first <= start < last for first, last in spans):
                continue
            match = URL.match(content, start)
            if not match:
                continue
            if angle:
                if content[match.end():match.end() + 1] != ">":
                    continue
                ends = (match.end(),)
                protected = max(0, match.group().count(")") - match.group().count("("))
            else:
                protected = len(re.findall(r"(?<!\\)(?:\\\\)*\\\)", match.group()))
                shortest = start + len(url_token(match, protected))
                ends = range(match.end(), shortest - 1, -1)
            for end in ends:
                raw = content[start:end]
                decoded = raw if angle else unescapeAll(raw)
                if (URL.fullmatch(decoded)
                        and parsed_position(content, start, end,
                                            autolink, decoded, children)):
                    destinations[parser.normalizeLink(url_token(decoded, protected))] += 1
                    break
        return destinations

    text = path.read_text(encoding="utf-8")
    _, body = split_front_matter(text)
    prefix = text[:len(text) - len(body)]
    # Only LF separates lines here; splitlines() would turn Unicode separators
    # into artificial block boundaries before CommonMark sees the input.
    lines = [''] * prefix.count('\n') + body.split('\n')
    env = {}
    tokens = parser.parse("\n".join(lines), env)
    reference_hrefs = {parser.normalizeLink(ref["href"])
                       for ref in env.get("references", {}).values()}
    for token in tokens:
        if token.type != "inline":
            continue
        line = token.map[0] + 1
        candidates = []
        children = token.children or ()
        for match in URL.finditer(token.content):
            angle = (match.start() > 0 and token.content[match.start() - 1] == "<"
                     and token.content[match.end():match.end() + 1] == ">")
            closers = max(0, match.group().count(")") - match.group().count("(")) if angle else 0
            candidate = url_token(match, closers)
            decoded = (url_token(unescapeAll(match.group()), closers) if angle
                       else decoded_url(match.group()))
            if "__" in decoded:
                if (angle and parser.normalizeLink(decoded) not in reference_hrefs
                        and parsed_position(token.content, match.start(), match.end(),
                                            True, match.group(), children)):
                    continue
                candidates.append((candidate, parser.normalizeLink(decoded)))
        accounted = Counter()
        whole_destinations = raw_destinations(token.content, children)
        for child in children:
            if child.type == "link_open":
                href = child.attrGet("href")
                match = URL.match(href or "")
                if match and child.info != "auto" and parser.normalizeLink(href) not in reference_hrefs:
                    closers = max(0, match.group().count(")") - match.group().count("("))
                    normalized = parser.normalizeLink(url_token(match, closers))
                    if whole_destinations[normalized]:
                        accounted[normalized] += 1
                        whole_destinations[normalized] -= 1
            elif child.type == "image":
                src = child.attrGet("src")
                match = URL.match(src or "")
                if match and parser.normalizeLink(src) not in reference_hrefs:
                    closers = max(0, match.group().count(")") - match.group().count("("))
                    normalized = parser.normalizeLink(url_token(match, closers))
                    if whole_destinations[normalized]:
                        accounted[normalized] += 1
                        whole_destinations[normalized] -= 1
            elif child.type == "code_inline":
                for match in URL.finditer(child.content):
                    accounted[parser.normalizeLink(decoded_url(match.group()))] += 1
        for candidate, normalized in candidates:
            if accounted[normalized]:
                accounted[normalized] -= 1
            else:
                yield f"{path.name}:{line}: bare URL contains __: {candidate}"


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
                print(f"  FAIL  bare URL parser unavailable: {exc}")
                return 1
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
