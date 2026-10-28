#!/usr/bin/env python3
"""Split a Markdown guide into sentences, so the 400-character rules share one measure.

Row 3.47: guide prose (DONE 1.385) and generated claim-summary sentences (row 1.383)
are each limited to 400 characters, and each was measured by its own ad hoc scan.
This module is the one measure. It is not a gate: nothing here fails a build. The
CLI lists sentences longer than a limit, exits 0 once every file was read and 2
when a file cannot be read or decoded.

    python3 tools/sentence_split.py FILE... [--over N]

prints `file:line (length)` for each sentence longer than N (default 400), where
line is the line on which the sentence starts.

What a sentence is, here:

- Units. Each paragraph is one unit, its hard-wrapped lines joined by one space.
  A list item starts a new unit, and its marker is not counted; a blockquote
  marker is not counted either. Each heading and each table cell is a unit of
  its own, and table delimiter rows are skipped. Fenced code blocks, HTML
  comments, legacy front matter and the generated version-basis section (its
  summary and claims JSON) are skipped, as the closing measurement recorded in
  DONE 1.385 skipped them. A claim-summary line can be measured on its own with
  split_sentences().
- Rendering. A link or image renders as its text, and an autolink as its URL.
  Backticks, emphasis markers and every other character are kept and counted;
  a backslash escape counts as the character it escapes.
- Boundaries. A sentence ends at `.`, `?` or `!` followed by whitespace and then
  a capital letter, digit, backtick, quote or bracket. Closing quotes, closing
  brackets and emphasis markers may sit between the mark and the whitespace,
  and emphasis markers between the whitespace and the next sentence's first
  character. A run of links between two sentences, such as rendered source
  citations, stays with the sentence before it.
- Not boundaries. A mark inside a code span, inside link text, or inside a
  double-quoted quotation that has not closed by the whitespace, and a full
  stop directly after e.g., i.e., etc., vs. or cf., or after the number that
  opens a numbered heading such as `## 1. Bind privately`. When a closing
  quote or bracket follows the abbreviation, as in `"... 2FA, etc." The`, the
  end of the quotation is taken as the end of the sentence.

Length is len() of the sentence in Unicode code points, the unit the claim-length
gate uses.

Limits, disclosed rather than handled: this is a line scanner, not a CommonMark
parser. Straight double quotes pair by alternation within a unit. A table row
must start with a pipe. Setext headings, indented code, HTML blocks and
reference-style links are read as ordinary lines, and a lazy continuation line
joins whatever unit is open. An abbreviation outside the five listed, such as
"Mr.", ends a sentence when a capital follows it.
"""
import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences  # noqa: E402

LIMIT = 400
START = "<!-- version-basis:start -->"
END = "<!-- version-basis:end -->"

HEADING_RE = re.compile(r" {0,3}#{1,6}(?=[ \t]|$)(.*)$")
CLOSING_HASHES_RE = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
QUOTE_RE = re.compile(r"[ \t]*(?:>[ \t]?)+")
LIST_RE = re.compile(r"[ \t]*(?:[-*+]|[0-9]{1,9}[.)])(?:[ \t]+|$)")
CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")
DELIMITER_CELL_RE = re.compile(r"[ \t]*:?-+:?[ \t]*")
BACKTICKS_RE = re.compile(r"`+")
LINK_RE = re.compile(
    r"!?\[((?:[^\[\]`\\]|\\.|`[^`]*`)*)\]"
    r"\([ \t]*(?:<[^<>]*>|[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)"
    r"(?:[ \t]+(?:\"[^\"]*\"|'[^']*'))?[ \t]*\)")
AUTOLINK_RE = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*)>")
ESCAPABLE = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
ABBREVIATION_RE = re.compile(r"(?<![A-Za-z])(?:e\.g|i\.e|etc|vs|cf)\Z", re.I)
CLOSERS = "\"”’')]*_"
OPENERS = "`\"“‘'(["

Rendered = namedtuple("Rendered", "text src code links")


def render(raw):
    """Render one unit's inline Markdown: links as their text, everything else kept.

    Returns the text, each text character's index in raw, and the (start, end)
    ranges of the text's code spans and links.
    """
    text, src, code, links = [], [], [], []

    def emit(start, end):
        text.extend(raw[start:end])
        src.extend(range(start, end))

    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "`":
            run = BACKTICKS_RE.match(raw, i)
            close = re.compile(rf"(?<!`){run.group()}(?!`)").search(raw, run.end())
            end = close.end() if close else run.end()
            start = len(text)
            emit(i, end)
            if close:
                code.append((start, len(text)))
            i = end
        elif ch == "\\" and i + 1 < len(raw) and raw[i + 1] in ESCAPABLE:
            emit(i + 1, i + 2)
            i += 2
        elif ch in "[!" and (m := LINK_RE.match(raw, i)):
            inner, offset = render(m.group(1)), len(text)
            text.extend(inner.text)
            src.extend(m.start(1) + k for k in inner.src)
            code.extend((a + offset, b + offset) for a, b in inner.code)
            links.append((offset, len(text)))
            i = m.end()
        elif ch == "<" and (m := AUTOLINK_RE.match(raw, i)):
            start = len(text)
            emit(m.start(1), m.end(1))
            links.append((start, len(text)))
            i = m.end()
        else:
            emit(i, i + 1)
            i += 1
    return Rendered("".join(text), src, code, links)


def _skip_space(text, k):
    while k < len(text) and text[k].isspace():
        k += 1
    return k


def _opens(text, k):
    """True if a sentence can start at k, after any opening emphasis markers."""
    while k < len(text) and text[k] in "*_":
        k += 1
    return k < len(text) and (text[k].isupper() or text[k].isdigit() or text[k] in OPENERS)


def _next_start(text, i, opaque, link_end, straight, curly):
    """Where the sentence after the mark at i starts, or None if i ends no sentence."""
    j = i + 1
    while j < len(text) and text[j] in CLOSERS and not opaque[j]:
        if text[j] == '"':
            if not straight:
                break
            straight = False
        elif text[j] == "”":
            curly = max(0, curly - 1)
        j += 1
    if straight or curly:
        return None
    if j == i + 1 and text[i] == "." and (ABBREVIATION_RE.search(text, 0, i)
                                          or (i <= 9 and text[:i].isdigit())):
        return None
    if j == len(text) or not text[j].isspace():
        return None
    k = m = _skip_space(text, j)
    while m in link_end:
        m = _skip_space(text, link_end[m])
    if m != k and _opens(text, m):
        return m
    return k if _opens(text, k) else None


def split_rendered(rendered):
    """Yield (start, sentence) for each sentence of a rendered unit."""
    text = rendered.text
    opaque = [False] * len(text)
    for a, b in rendered.code + rendered.links:
        opaque[a:b] = [True] * (b - a)
    link_end = dict(rendered.links)
    starts = set()
    straight, curly = False, 0
    for i, ch in enumerate(text):
        if opaque[i]:
            continue
        if ch == '"':
            straight = not straight
        elif ch == "“":
            curly += 1
        elif ch == "”":
            curly = max(0, curly - 1)
        elif ch in ".?!":
            start = _next_start(text, i, opaque, link_end, straight, curly)
            if start is not None:
                starts.add(start)
    edges = [0, *sorted(starts), len(text)]
    for a, b in zip(edges, edges[1:]):
        a = _skip_space(text, a)
        sentence = text[a:b].rstrip()
        if sentence:
            yield a, sentence


def split_sentences(raw):
    """The sentences of one unit of inline Markdown, such as a joined paragraph."""
    return [sentence for _, sentence in split_rendered(render(raw))]


def _strip_comments(line, in_comment):
    """Remove HTML comment text from a line; return the rest and whether one is open."""
    out = ""
    while line:
        if in_comment:
            end = line.find("-->")
            if end < 0:
                return out, True
            line, in_comment = line[end + 3:], False
        else:
            start = line.find("<!--")
            if start < 0:
                return out + line, False
            out, line, in_comment = out + line[:start], line[start + 4:], True
    return out, in_comment


def table_cells(line):
    """The cells of a pipe table row, split at unescaped pipes."""
    cells = CELL_SPLIT_RE.split(line.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return cells


def units(markdown):
    """Return (raw, where) for each unit: its raw inline Markdown and, for each
    joined line, that line's (offset in raw, one-based line number)."""
    out, raw, where = [], "", []

    def flush():
        nonlocal raw, where
        if raw.strip():
            out.append((raw, where))
        raw, where = "", []

    def add(text, number):
        nonlocal raw
        if raw:
            raw += " "
        where.append((len(raw), number))
        raw += text

    lines = markdown.split("\n")
    fences = Fences()
    front = bool(lines) and lines[0].rstrip("\r") == "---"
    generated = in_comment = False
    for number, line in enumerate(lines, 1):
        line = line.rstrip("\r")
        if front:
            front = number == 1 or line != "---"
            continue
        if generated:
            generated = line.strip() != END
            continue
        if not in_comment and not fences.inside and line.strip() == START:
            flush()
            generated = True
            continue
        if not in_comment and fences.feed(line):
            flush()
            continue
        if fences.inside:
            continue
        line, in_comment = _strip_comments(line, in_comment)
        if not line.strip():
            flush()
            continue
        if m := HEADING_RE.match(line):
            flush()
            add(CLOSING_HASHES_RE.sub("", m.group(1)).strip(), number)
            flush()
            continue
        if line.lstrip().startswith("|"):
            flush()
            cells = table_cells(line)
            if not all(DELIMITER_CELL_RE.fullmatch(cell) for cell in cells):
                for cell in cells:
                    add(cell.strip(), number)
                    flush()
            continue
        line = QUOTE_RE.sub("", line, count=1) if QUOTE_RE.match(line) else line
        if m := LIST_RE.match(line):
            flush()
            line = line[m.end():]
        add(line.strip(), number)
    flush()
    return out


def sentences(markdown):
    """Yield (line, sentence) for every sentence of a guide, in order."""
    for raw, where in units(markdown):
        rendered = render(raw)
        for start, sentence in split_rendered(rendered):
            offset = rendered.src[start]
            yield [n for o, n in where if o <= offset][-1], sentence


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="List sentences longer than a limit in Markdown guides.")
    parser.add_argument("files", nargs="+", metavar="FILE")
    parser.add_argument("--over", type=int, default=LIMIT, metavar="N",
                        help=f"print sentences longer than N characters (default {LIMIT})")
    args = parser.parse_args(argv)
    status = 0
    for name in args.files:
        try:
            text = Path(name).read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"{name}: cannot read: {exc}", file=sys.stderr)
            status = 2
            continue
        for line, sentence in sentences(text):
            if len(sentence) > args.over:
                print(f"{name}:{line} ({len(sentence)})")
    return status


if __name__ == "__main__":
    sys.exit(main())
