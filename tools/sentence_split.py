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
  split_sentences(). A code span and a comment are read from left to right, and
  whichever opens first wins, so a `<!--` inside a code span opens no comment and
  a backtick inside a comment opens no code span. A backtick run opens a code span
  only when a run of the same length closes it later in its paragraph, on its own
  line or a later one, as CommonMark pairs them; a heading is a paragraph of one
  line here, each table cell is read on its own, and a backslash-escaped backtick
  or `<` opens nothing. A `<!--` at the start of a line, after any block quote
  markers and list marker, where the splitter takes a block to start (no
  paragraph is open, or the line may interrupt the one that is), opens a comment
  that runs to the next `-->` or the end of the file, as an HTML block outside a
  container does, and the rest of the line that closes it is a unit of its own,
  as the end of that block.
  Anywhere else, a `<!--` opens a comment only when a `-->` follows it in its
  paragraph or table cell, and is text otherwise. As in CommonMark 0.31.2, `<!-->`
  and `<!--->` are whole comments. A line of a paragraph that an inline comment
  leaves empty does not end the paragraph. A link's destination and title, and a
  link reference definition, are read as paragraph text, as item 4 of the limits
  below says.
- Rendering. A link or image renders as its text, and an autolink as its URL,
  before splitting, so a mark in link text counts like any other.
  Backticks, emphasis markers and every other character are kept and counted;
  a backslash escape counts as the character it escapes.
- Boundaries. A sentence ends at `.`, `?` or `!` followed by whitespace and then
  a capital letter, digit, backtick, quote or bracket. Closing quotes, closing
  brackets and emphasis markers may sit between the mark and the whitespace,
  and emphasis markers between the whitespace and the next sentence's first
  character. A run of links between two sentences, such as rendered source
  citations, stays with the sentence before it, even when its text starts with
  a capital. A link run followed by text that cannot open a sentence starts
  the sentence instead, whatever its own text, as in `It ends. [RFC 6455](u)
  says so.` and `It ends. [mfa.md](u) covers it.` A link run that ends its unit
  starts a sentence only when its own text can open one. A full stop after
  etc. ends a sentence like any other.
- Not boundaries. A mark inside a code span, or inside a quotation or a
  single-quoted phrase that has not closed by the whitespace, and a full stop
  directly after e.g., i.e., vs. or cf., which seldom end a sentence, or after
  the number that opens a numbered heading such as `## 1. Bind privately`. When
  a closing quote or bracket follows the abbreviation, as in `(see e.g.) The`,
  the end of the bracket is taken as the end of the sentence.
- Quotations. A quote pairs with one of its own style first, so a
  straight-quoted span nested in a curly quotation, or the reverse, does not
  end the outer one. Straight and curly double quotes pair with each other
  otherwise, and a quotation never stays open past its unit. A quote with no
  partner later in the unit opens nothing. A straight quote right after a
  digit opens nothing and closes only an open straight quotation, so an inch
  mark as in `“A 27" screen. Still inside.”` leaves a curly quotation open.
- Single quotes. A straight single quote or ‘ opens a phrase after a space,
  an opening bracket or the start of the unit and before a non-space, and a
  straight single quote or ’ closes it after a non-space and before anything
  but a letter or digit, as in `He said 'Stop. Now.' Then leave.` An
  apostrophe inside a word, as in don't, does neither, and single-quoted
  phrases do not nest.

Length is len() of the sentence in Unicode code points, the unit the claim-length
gate uses.

Limits, disclosed rather than handled: this is a line scanner that approximates
CommonMark 0.31.2 and GFM tables, not a CommonMark parser. Quotes pair by
position, not meaning, so a stray quote can still pair with a later one and
hold back the boundaries between them, and a backslash-escaped quote neither
opens nor closes one. A table row is a line
that starts with a pipe, a header row whose next line is a delimiter row with
as many cells, or a line with an unescaped pipe right after another table row.
Setext headings, indented code, HTML blocks and reference-style links are read
as ordinary lines, a link reference definition is read as a line of text, and a
lazy continuation line joins whatever unit is open. An
abbreviation outside the four listed, such as "Mr.", or etc. in mid-sentence,
ends a sentence when a capital follows it, and a real sentence end after one of
the four is joined to the next sentence. A link that opens a sentence and is
followed by a capital, as in `It ends. [Redis](u) Sentinel docs say so.`, cannot
be told apart from a citation run, so it stays with the sentence before; every
such run in the guides is a run of source citations, and reading them as
sentence starts would add a sentence over 400 characters. A possessive
apostrophe after a final s, as in users', closes a single-quoted phrase left
open before it, and a leading apostrophe after a space, as in '90s, opens one.
A paragraph ends, for pairing backtick runs and finding a comment's `-->`, at a
blank line, a lone `>` in a block quote, a deeper block quote, and a line that
opens an ATX heading, a thematic break, a setext underline, an HTML block of
CommonMark types 1 to 6 (with the type 6 tag names of CommonMark 0.31.2), a
fence, a table, or a list item that may interrupt a paragraph: a bullet or an
item numbered 1, with text after its marker, or, in a list item, a marker
indented less than that item's text, where the item is the one that opens the
unit.

Because the scanner only approximates CommonMark, a real comment can still be
shown, or text hidden, in layouts it does not model. These are the known ones,
and the list is not exhaustive:
1. HTML blocks other than comments are read as paragraph lines, so two backticks
   in one still pair, and a real comment between them is shown.
2. Indented code blocks are read as paragraph lines, so a `<!--` and a later
   `-->` in one hide the code between them, which CommonMark shows.
3. Inline HTML tags and autolinks are not recognized, so a backtick inside one
   can pair with a later backtick and show a real comment between them, and a
   `<!--` in a tag's attribute value can hide text up to a later `-->`.
4. A link's destination and title, and a link reference definition, are read
   as paragraph text. So a backtick in one can pair with a later backtick and
   show a real comment between them, and a `<!--` in one can open a comment
   that hides the text after it up to a later `-->`.
5. Container structure is approximated: any line that opens with a pipe ends a
   paragraph, a list marker indented 4 or more spaces ends one as it does
   unindented, a block quote marker is read as one however far it is indented,
   so one indented 4 or more spaces on a paragraph line is read as a deeper
   block quote, which ends the paragraph for pairing backtick runs, and a list
   item's column comes from the first line of the unit. As item 13 says, a
   later line's indentation is compared with that column after any block quote
   markers, with a tab counted as one column, not as the tab stop CommonMark
   advances to.
6. A block start in a list item whose text starts at column 4 or more, indented
   to that text, as with a `<div>` or a thematic break under `10. `, is read as
   indented 4 spaces and so ends no paragraph.
7. A setext underline that CommonMark reads as a lazy continuation line, after a
   paragraph in a block quote or list item, ends the paragraph here.
8. A GFM table body row without a pipe is read as a paragraph line, not as a row.
9. A comment HTML block in a block quote or list item runs to the next `-->` or
   the end of the file, and does not end with its container as CommonMark's
   does, so it can hide the text after the container.
10. A `<!--` on a line of a list item counts its indentation from column 0, not
    from the item's text, so one indented 4 or more spaces, as on a later line
    of an item under `- ` or `10. `, opens no comment block. With no `-->` later
    in its paragraph it is text, and the comment it opens in CommonMark is shown.
11. After a paragraph in a block quote, a line with no block quote marker that
    starts an ordered item numbered other than 1, such as `2.`, starts a new
    list in CommonMark. Here, for pairing backtick runs and finding a comment's
    `-->`, it is read as a lazy continuation line of that paragraph, so a code
    span can pair across it and show a real comment, and a `<!--` in the
    paragraph can hide text up to a `-->` in the item.
12. A block quote or list marker is read as one on a line of an indented code
    block too, so a `<!--` after it, as in `    > <!--` or `    - <!--`, opens a
    comment block that runs to the next `-->` or the end of the file and hides
    the code and the text after it, which CommonMark shows.
13. In a list item, a later line's indentation is compared with the item's
    text column after any block quote markers, and a tab in it counts as one
    column. So an ordered item numbered other than 1 on a line indented with a
    tab, as in `- a` then a tab and `2. <!--`, or after the marker of a block
    quote in the item, as in `- > Para` then `  > 2. <!--`, is read as a
    sibling item that ends the paragraph, and a `<!--` after its marker opens a
    comment block that runs to the next `-->` or the end of the file, where
    CommonMark reads paragraph text and shows it.
Where a paragraph ends here and not in CommonMark (items 5, 7 and 13), a code
span may not pair, and a `<!--` in it then hides text up to a later `-->`; where
it goes on here and not in CommonMark (items 5, 6, 8 and 11), a code span may
pair and show a real comment.
"""
import argparse
import re
import sys
from collections import namedtuple
from itertools import accumulate
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import FENCE_RE, Fences  # noqa: E402

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
# Where a "<!--" opens an HTML block (CommonMark type 2): at the start of a line, after any
# block quote markers and list marker and up to 3 spaces.
COMMENT_BLOCK_RE = re.compile(r"(?:[ \t]*>[ \t]?)*(?:[ \t]*(?:[-*+]|[0-9]{1,9}[.)])[ \t]+)?"
                              r" {0,3}<!--")
THEMATIC_BREAK_RE = re.compile(r" {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
SETEXT_UNDERLINE_RE = re.compile(r" {0,3}(?:=+|-+)[ \t]*$")
# The starts of CommonMark 0.31.2 HTML blocks of types 1 to 6, the ones that may end a paragraph.
# As in that spec, only the tag names of types 1 and 6 match in any case (so "<![cdata[" starts no
# block), and the type 6 names are its list, which has "search" and not "source".
HTML_BLOCK_RE = re.compile(
    r" {0,3}(?:<(?ai:script|pre|style|textarea)(?=[ \t>]|$)|<!--|<\?|<![A-Za-z]|<!\[CDATA\["
    r"|</?(?ai:address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup"
    r"|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset"
    r"|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol"
    r"|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr"
    r"|track|ul)(?=[ \t>]|/>|$))")
LINK_RE = re.compile(
    r"!?\[((?:[^\[\]`\\]|\\.|`[^`]*`)*)\]"
    r"\([ \t]*(?:<[^<>]*>|[^\s()]*(?:\([^\s()]*\)[^\s()]*)*)"
    r"(?:[ \t]+(?:\"[^\"]*\"|'[^']*'))?[ \t]*\)")
AUTOLINK_RE = re.compile(r"<([A-Za-z][A-Za-z0-9+.-]{1,31}:[^\s<>]*)>")
ESCAPABLE = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
ABBREVIATION_RE = re.compile(r"(?<![A-Za-z])(?:e\.g|i\.e|vs|cf)\Z", re.I)
CLOSERS = "\"”’')]*_"
OPENERS = "`\"“‘'(["

Rendered = namedtuple("Rendered", "text src code links escaped")


def render(raw):
    """Render one unit's inline Markdown: links as their text, everything else kept.

    Returns the text, each text character's index in raw, the (start, end)
    ranges of the text's code spans and links, and the set of text indices
    that came from a backslash escape.
    """
    text, src, code, links, escaped = [], [], [], [], set()

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
            escaped.add(len(text))
            emit(i + 1, i + 2)
            i += 2
        elif ch in "[!" and (m := LINK_RE.match(raw, i)):
            inner, offset = render(m.group(1)), len(text)
            text.extend(inner.text)
            src.extend(m.start(1) + k for k in inner.src)
            code.extend((a + offset, b + offset) for a, b in inner.code)
            escaped.update(k + offset for k in inner.escaped)
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
    return Rendered("".join(text), src, code, links, escaped)


def _skip_space(text, k):
    while k < len(text) and text[k].isspace():
        k += 1
    return k


def _opens(text, k):
    """True if a sentence can start at k, after any opening emphasis markers."""
    while k < len(text) and text[k] in "*_":
        k += 1
    return k < len(text) and (text[k].isupper() or text[k].isdigit() or text[k] in OPENERS)


def _single_quotes(text, opaque, escaped):
    """(open, close) index pairs of single-quoted phrases in text.

    A straight quote or ‘ opens a phrase after a space, an opening bracket or
    the start of text and before a non-space; a straight quote or ’ closes the
    open phrase after a non-space and before anything but a letter or digit.
    So an apostrophe inside a word, as in don't, does neither. A phrase still
    open at the end of text opens nothing.
    """
    pairs, start = [], None
    for k, ch in enumerate(text):
        if opaque[k] or k in escaped or ch not in "'‘’":
            continue
        before = text[k - 1] if k else " "
        after = text[k + 1] if k + 1 < len(text) else " "
        opens = before.isspace() or before in "(["
        if start is not None and ch != "‘" and not before.isspace() and not after.isalnum():
            pairs.append((start, k))
            start = None
        elif start is None and ch != "’" and opens and not after.isspace():
            start = k
    return pairs


def _quote_depth(text, opaque, escaped):
    """How many quotations are open before each index of text, up to len(text).

    A quote closes a quotation of its own style first: a straight quote closes
    an open straight one, and a closing curly quote the innermost open curly
    one along with any straight quote left open inside it. Otherwise a straight
    quote opens a nested quotation unless it follows a digit, and a closing
    curly quote closes a straight one. Openers left unpaired at the end of the
    unit pair a curly one with a straight one after it, and the rest are
    dropped, so they hold back no boundary. Single quotes add the pairs that
    _single_quotes finds.
    """
    stack, pairs = [], _single_quotes(text, opaque, escaped)
    for k, ch in enumerate(text):
        if opaque[k] or k in escaped or ch not in "\"“”":
            continue
        after_digit = k and text[k - 1].isdigit()
        if ch == "“":
            stack.append(k)
        elif ch == "”" and stack:
            n = max((n for n, o in enumerate(stack) if text[o] == "“"), default=-1)
            pairs.append((stack[n], k))
            del stack[n:]
        elif ch == '"' and stack and text[stack[-1]] == '"':
            pairs.append((stack.pop(), k))
        elif ch == '"' and not after_digit:
            stack.append(k)
    pairs += [(a, b) for a, b in zip(stack, stack[1:]) if text[a] == "“" and text[b] == '"']
    step = [0] * (len(text) + 1)
    for a, b in pairs:
        step[a + 1] += 1
        step[b + 1] -= 1
    return list(accumulate(step))


def _next_start(text, i, opaque, depth, link_end):
    """Where the sentence after the mark at i starts, or None if i ends no sentence."""
    j = i + 1
    while j < len(text) and text[j] in CLOSERS and not opaque[j]:
        j += 1
    if depth[j]:
        return None
    if j == i + 1 and text[i] == "." and (ABBREVIATION_RE.search(text, 0, i)
                                          or (i <= 9 and text[:i].isdigit())):
        return None
    if j == len(text) or not text[j].isspace():
        return None
    k = m = _skip_space(text, j)
    while m in link_end:
        m = _skip_space(text, link_end[m])
    if m == k or m == len(text):
        return k if _opens(text, k) else None
    return m if _opens(text, m) else k


def split_rendered(rendered):
    """Yield (start, sentence) for each sentence of a rendered unit."""
    text = rendered.text
    opaque = [False] * len(text)
    for a, b in rendered.code:
        opaque[a:b] = [True] * (b - a)
    depth = _quote_depth(text, opaque, rendered.escaped)
    link_end = dict(rendered.links)
    starts = set()
    for i, ch in enumerate(text):
        if ch in ".?!" and not opaque[i]:
            start = _next_start(text, i, opaque, depth, link_end)
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


def _closing_run(n):
    """A run of exactly n backticks, the only run that closes a code span opened by n."""
    return re.compile(rf"(?<!`)`{{{n}}}(?!`)")


def _unquoted(line):
    """line without the block quote markers that open it."""
    return QUOTE_RE.sub("", line, count=1) if QUOTE_RE.match(line) else line


def _block_start(line, item=None):
    """True if line ends the paragraph before it, read after any block quote markers.

    That is a blank line in a block quote (a lone ">"), an ATX heading, a thematic break,
    a setext heading underline, the start of an HTML block of CommonMark types 1 to 6, a
    fence (as Fences opens one), a table row that starts with a pipe, or a list item that
    may interrupt a paragraph: a bullet or an ordered item numbered 1, each with text after
    its marker. When the paragraph is in a list item whose text starts at column item, any
    list marker indented less than that starts a sibling item and ends it too. This is the
    closest this line scanner comes to CommonMark's rule.
    """
    line = _unquoted(line)
    fence = FENCE_RE.match(line)
    marker = LIST_RE.match(line)
    return bool(not line.strip() or HEADING_RE.match(line) or THEMATIC_BREAK_RE.match(line)
                or SETEXT_UNDERLINE_RE.match(line) or HTML_BLOCK_RE.match(line)
                or (marker and line[marker.end():].strip()
                    and int(marker.group().strip()[:-1] or 1) == 1)
                or (marker and item is not None and len(line) - len(line.lstrip()) < item)
                or line.lstrip().startswith("|")
                or (fence and not (fence[1][0] == "`" and "`" in fence[2])))


def _quote_depth_of(line):
    """How many block quote markers open line."""
    m = QUOTE_RE.match(line)
    return m.group().count(">") if m else 0


def _paragraph_after(lines, number, item=None):
    """The lines after line number (one-based) that continue its paragraph, joined with LF.

    The paragraph ends at a blank line, at a line that ends it as _block_start says (item
    is the column at which the text of the list item holding it starts, or None), at a
    deeper block quote and at a table header row; a line with fewer quote markers is a lazy
    continuation and does not end it.
    """
    depth, found = _quote_depth_of(lines[number - 1]), []
    for k in range(number, len(lines)):
        line = lines[k].rstrip("\r")
        if (not line.strip() or _block_start(line, item) or _quote_depth_of(line) > depth
                or (k + 1 < len(lines) and starts_table(line, lines[k + 1].rstrip("\r")))):
            break
        found.append(line)
    return "\n".join(found)


def _strip_comments(line, in_comment, span=0, later="", block=True):
    """Remove HTML comment text from a line, keeping code spans.

    Returns the rest of the line, whether a comment is still open at its end and, when a
    code span is, the length of the backtick run that opened it, else 0. A code span
    and a comment are read from left to right, so whichever opens first wins, as in
    CommonMark: a "<!--" inside a code span opens no comment, and a backtick inside a
    comment opens no code span. A backtick run opens a code span only when a run of the
    same length closes it later in the line or in later, the text of the lines after it
    that continue its paragraph (_paragraph_after); span carries a code span still open
    at the end of a line into the next. A backslash escape, of a backtick or a "<" among
    others, opens nothing. A "<!--" where it opens an HTML block (COMMENT_BLOCK_RE, unless
    block is false) opens a comment that runs to the next "-->" or the end of the file.
    Anywhere else it opens one only when a "-->" follows it in the line or in later, and is
    text otherwise. As in CommonMark 0.31.2, "<!-->" and "<!--->" are whole comments. A
    link's destination and title are read as text like the rest of the line.
    """
    out = ""
    opener = COMMENT_BLOCK_RE.match(line) if block and not in_comment and not span else None
    opener = opener.end() - 4 if opener else -1
    while line:
        if in_comment:
            end = line.find("-->")
            if end < 0:
                return out, True, 0
            line, in_comment = line[end + 3:], False
        elif span:
            close = _closing_run(span).search(line)
            if not close:
                return out + line, False, span
            out, line, span = out + line[:close.end()], line[close.end():], 0
        else:
            i = 0
            while i < len(line):
                if line.startswith("<!--", i):
                    if i == opener or (line + "\n" + later).find("-->", i + 2) >= 0:
                        break
                    i += 4
                elif line[i] == "\\" and line[i + 1:i + 2] and line[i + 1] in ESCAPABLE:
                    i += 2
                elif line[i] == "`":
                    run = BACKTICKS_RE.match(line, i)
                    close = _closing_run(len(run.group())).search(line + "\n" + later, run.end())
                    if close and close.end() > len(line):
                        return out + line, False, len(run.group())
                    i = close.end() if close else run.end()
                else:
                    i += 1
            if i >= len(line):
                return out + line, False, 0
            # From the "<!--"'s own dashes, so that "<!-->" and "<!--->" close at once.
            out, line, in_comment, opener = out + line[:i], line[i + 2:], True, -1
    return out, in_comment, span


def table_cells(line):
    """The cells of a pipe table row, split at unescaped pipes."""
    cells = CELL_SPLIT_RE.split(line.strip())
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return cells


def starts_table(line, below):
    """True if line is a table header row: below is a delimiter row with as many cells."""
    if not (CELL_SPLIT_RE.search(line) and CELL_SPLIT_RE.search(below)):
        return False
    delimiters = table_cells(below)
    return (len(delimiters) == len(table_cells(line))
            and all(DELIMITER_CELL_RE.fullmatch(cell) for cell in delimiters))


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
    generated = in_comment = block_comment = False
    span, last_row, item = 0, -1, None
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
        quoted = _unquoted(line)
        marker = LIST_RE.match(quoted)
        row = (line.lstrip().startswith("|")
               or (last_row == number - 1 and CELL_SPLIT_RE.search(line))
               or (number < len(lines) and starts_table(line, lines[number])))
        alone = emptied = False
        if row and not in_comment and not span:
            # GFM splits a table row into cells before it reads code spans or comments, so
            # each cell is read on its own, and a "<!--" opens a comment only within its cell.
            line = "|".join(_strip_comments(cell, False, block=False)[0]
                            for cell in CELL_SPLIT_RE.split(line))
        else:
            # A comment HTML block starts only where no paragraph is open or where the line
            # may interrupt the one that is.
            starts = not (in_comment or span) and (not raw.strip() or _block_start(line, item))
            alone = block_comment = block_comment or bool(starts and COMMENT_BLOCK_RE.match(line))
            later = ""
            if ("`" in line or "<!--" in line) and not (HEADING_RE.match(quoted) or row or alone):
                # A code span or a comment may close on a later line of the paragraph, but
                # not past a heading, a table row or a comment HTML block, whose text ends
                # with the line.
                column = marker.end() if marker else item if raw.strip() else None
                later = _paragraph_after(lines, number, column)
            source = line
            line, in_comment, span = _strip_comments(line, in_comment, span, later, starts)
            # A line of an open paragraph that an inline comment leaves empty does not end the
            # paragraph, so the next line is read as it would be without the comment.
            emptied = bool(raw.strip() and not alone and _unquoted(source).strip()
                           and not _unquoted(line).strip())
            # The rest of the line that closes a comment HTML block ends that block, so it is a
            # unit of its own.
            block_comment = block_comment and in_comment
            alone = alone and not in_comment
            if alone:
                flush()
        if emptied:
            continue
        if not line.strip():
            flush()
            continue
        if m := HEADING_RE.match(line):
            flush()
            add(CLOSING_HASHES_RE.sub("", m.group(1)).strip(), number)
            flush()
            continue
        if (line.lstrip().startswith("|")
                or (last_row == number - 1 and CELL_SPLIT_RE.search(line))
                or (number < len(lines) and starts_table(line, lines[number]))):
            flush()
            last_row = number
            cells = table_cells(line)
            if not all(DELIMITER_CELL_RE.fullmatch(cell) for cell in cells):
                for cell in cells:
                    add(cell.strip(), number)
                    flush()
            continue
        line = _unquoted(line)
        if not line.strip():
            # A blank line in a block quote, such as a lone ">", ends the paragraph.
            flush()
            continue
        if m := LIST_RE.match(line):
            flush()
            item = m.end()
            line = line[m.end():]
        elif not raw.strip():
            item = None
        add(line.strip(), number)
        if alone:
            flush()
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
