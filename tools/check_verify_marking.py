#!/usr/bin/env python3
"""Offline Verify declaration ratchet; shared pinned parser for non-fence units.

Declarations begin a prose paragraph, a leading shell/Python '#' or SQL '--'
comment, or a heading suffix '(STATUS: provenance)' / ': STATUS: provenance'.
STATUS is DEMONSTRATED or REASONED, case-insensitively. Nonempty provenance
is required; its truth and scope remain review obligations. A heading covers
direct content only. A paragraph between fences needs an explicit
'preceding block;' or 'following block;' immediately after the colon.
Narrative mentions, command strings and HTML comments are not declarations.

All fence languages count. CommonMark 0.31.2 sections 2.2, 4.4, 4.5 and 5.1:
recognize four-column tab stops, indented code before prose, up to three spaces
before fences or '>', matching fence character/length, and paragraph-only lazy
quote continuation. A missing '>' ends quoted fenced code, never continues it.
Quoted fences (including quoted Verify roots) are detected but rejected as an
unsupported declaration container. Unclosed fences are convention errors only
inside Verify. Non-fence code and quoted prose are attachment boundaries;
comment rejection below still applies. Space-indented lists and ATX headings are supported.
Verify fences or headings in unsupported containers fail with
'[unsupported-container]', including compact nested lists, lists inside quotes,
empty list items, and headings inside lists or quotes. Lazy paragraph continuation
retains list ownership for this rejection. Setext headings are rejected throughout
guides, including nested candidates. HTML blocks (types 1-7) are quarantined to
their CommonMark end condition; every heading/fence candidate inside is rejected
and cannot change section selection. These constructs are detected, not modeled.
Every HTML comment opener outside a fence or matched code span is rejected,
including mid-paragraph openers and indented code samples. Code-span matching
handles equal-length backtick runs across paragraph lines and escaped openers.
https://spec.commonmark.org/0.31.2/

A leading version-basis front matter is masked only after strict parsing.
An enrolled guide may carry exactly one standalone generated summary pair
before its first level-2 heading. The pair is opaque to section selection;
headings, fences and other HTML comments inside still fail closed.

The legacy fence scanner is not a full CommonMark parser. The separate unit
scanner below uses the shared pinned CommonMark parser with table support. Status emphasis uses
the declaration grammar, not a general emphasis parser. Quoted declarations
are never attached to outside fences.

Fingerprints contain normalized heading ancestry, exact LF-normalized fence
text (including delimiters/info), and adjacent paragraphs in the same list
item. Line numbers and list-item serials are diagnostic, never identity.
Ambiguous paragraphs supply no declaration to either fence. Malformed or
conflicting declarations cannot be grandfathered. --write-baseline is an explicit one-time seed operation.
Normal runs never rewrite it. Strict mode rejects new, changed, duplicate and
stale exemptions. OS/UTF-8 errors exit 2; convention errors exit 1 in strict
mode (also in seed mode). Structural findings always fail, including report mode.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences
from _verify_sections import TITLE, heading_parts, title_text, verify_ranges
from _verify_sections import HEADING, META_EXCLUDE, guides

BASELINE = Path("tools/verify_marking_baseline.txt")
DECL = re.compile(
    r"(?i)^(?:\*\*|__)?(DEMONSTRATED|REASONED)(?:\*\*|__)?"
    r":(?:\*\*|__)?[ \t]*(.*)$"
)
LIST = re.compile(r"^( {0,3})(?:[-+*]|[0-9]{1,9}[.)])([ ]+)(.*)$")
EMPTY_LIST = re.compile(r"^ {0,3}(?:[-+*]|[0-9]{1,9}[.)]) *$")
QUOTE = re.compile(r"^ {0,3}> ?")
SETEXT = re.compile(r"^ {0,3}(?:=+|-+)[ \t]*$")
THEMATIC = re.compile(r" {0,3}(?:(?:\* *){3,}|(?:_ *){3,}|(?:- *){3,})$")

# CommonMark 0.31.2 section 4.6. These are quarantine boundaries only;
# no Markdown semantics or declarations are read from the enclosed HTML.
HTML_TAGS = (
    "address|article|aside|base|basefont|blockquote|body|caption|center|col|"
    "colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|"
    "form|frame|frameset|h1|h2|h3|h4|h5|h6|head|header|hr|html|iframe|legend|li|"
    "link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|search|"
    "section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul"
)
HTML_TYPE6 = re.compile(r"^ {0,3}</?(?:" + HTML_TAGS + r")(?:[ \t>]|/>|$)", re.I)
HTML_RAW = re.compile(r"^ {0,3}<(?:pre|script|style|textarea)(?:[ \t>]|$)", re.I)
HTML_RAW_END = re.compile(r"</(?:pre|script|style|textarea)>", re.I)
HTML_ATTRIBUTE = r'[a-zA-Z_:][a-zA-Z0-9_.:-]*(?:[ \t]*=[ \t]*(?:[^ \t"\'=<>`]+|\'[^\']*\'|"[^"]*"))?'
HTML_TYPE7 = re.compile(
    r"^ {0,3}(?:<(?!(?:pre|script|style|textarea)(?:[ \t/>]))"
    r"[a-zA-Z][a-zA-Z0-9-]*(?:[ \t]+" + HTML_ATTRIBUTE
    + r")*[ \t]*/?>|</[a-zA-Z][a-zA-Z0-9-]*[ \t]*>)[ \t]*$", re.I
)


def html_end(line, continuing=False):
    """Return a quarantine terminator for HTML types 1-7, or None."""
    if HTML_RAW.match(line):
        return HTML_RAW_END
    for start, end in ((r"<!--", r"-->"), (r"<\?", r"\?>"),
                       (r"<![A-Za-z]", r">"), (r"<!\[CDATA\[", r"\]\]>")):
        if re.match(r"^ {0,3}" + start, line):
            return re.compile(end)
    if HTML_TYPE6.match(line) or (not continuing and HTML_TYPE7.fullmatch(line)):
        return re.compile(r"^ *$")
    return None


def html_block(lines, start, first, offset, owner, terminator):
    """Keep HTML opaque through its terminator, EOF or container dedent."""
    end, body = start + 1, [first]
    while not terminator.search(body[-1]) and end < len(lines):
        line = lines[end].expandtabs(4)
        if line.strip() and not line.startswith(" " * offset):
            break
        body.append(line[offset:])
        end += 1
    return Token("html", start, end, "\n".join(body), owner)


def code_spans(text):
    """Yield (start, end, body) for equal-length backtick spans.

    Spans can cross paragraph lines; backslashes escape opening backticks
    but are literal inside a span. Offsets refer to the unnormalized text.
    """
    runs = list(re.finditer(r"`+", text))
    i = 0
    while i < len(runs):
        opening = runs[i]
        before = text[:opening.start()]
        escaped = (len(before) - len(before.rstrip("\\"))) % 2
        width = len(opening[0]) - escaped
        closing = next((j for j in range(i + 1, len(runs))
                        if len(runs[j][0]) == width), None)
        if not width or closing is None:
            i += 1
            continue
        yield (opening.start() + escaped, runs[closing].end(),
               text[opening.end():runs[closing].start()])
        i = closing + 1


def comment_lines(text):
    """Locate comment openers outside matched, equal-length code spans."""
    visible, position = [], 0
    for begin, end, _body in code_spans(text):
        visible.append(text[position:begin])
        visible.append("\n" * text[begin:end].count("\n"))
        position = end
    visible.append(text[position:])
    return [number for number, line in enumerate("".join(visible).split("\n"))
            if "<!--" in line]


@dataclass
class Token:
    kind: str
    start: int
    end: int
    text: str
    owner: tuple


def paragraph_open(text):
    """Is the final quoted line paragraph content, eligible for laziness?"""
    lines, _, tokens = tokenize(text)
    if not tokens or tokens[-1].end != len(lines):
        return False
    last = tokens[-1]
    return last.kind == "paragraph" or (
        last.kind == "quote" and paragraph_open(last.text)
    )


def interrupts_paragraph(line):
    """Only block starts can prevent a missing '>' from being lazy prose."""
    return (not line.strip(" \t") or HEADING.match(line)
            or Fences().feed(line) or QUOTE.match(line) or THEMATIC.fullmatch(line)
            or re.match(r"^ {0,3}(?:[-+*] +|1[.)] +)", line)
            or html_end(line, continuing=True) is not None)


def unsupported_block(lines, start, first, offset, owner):
    """Quarantine an unsupported item through its indented continuation.

    Keep it opaque: its headings cannot end Verify and its prose cannot mark
    another fence. Prefix stripping below is only a rejection scan, not parsing.
    """
    end, body = start + 1, [first]
    while end < len(lines):
        line = lines[end].expandtabs(4)
        if line.strip() and not line.startswith(" " * offset):
            if not body[-1].strip() or interrupts_paragraph(line):
                break
            body.append(line)
        else:
            body.append(line[offset:])
        end += 1
    return Token("unsupported", start, end, "\n".join(body), owner)


def unsupported_features(text):
    """Locate fence/heading candidates without interpreting container syntax."""
    features = []
    previous = ""
    for number, line in enumerate(text.split("\n")):
        line = line.lstrip(" ")
        while True:
            quote, item = QUOTE.match(line), LIST.match(line)
            if quote:
                line = line[quote.end():].lstrip(" ")
            elif item:
                line = item[3].lstrip(" ")
            else:
                break
        if previous and SETEXT.fullmatch(line):
            features.append((number, "Setext heading", True))
        previous = line if (line.strip() and not interrupts_paragraph(line)) else ""
        head = HEADING.match(line)
        if head or Fences().feed(line):
            root = bool(head and TITLE.fullmatch(heading_parts(head[2] or "")[0]))
            features.append((number, "heading" if head else "fence", root))
    return features


def tokenize(text, in_quote=False):
    """Return lines, headings and block tokens; keep source for fingerprints."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    heads, tokens, stack = [None] * len(lines), [], []
    fences = Fences()
    start, fence_owner = 0, ()
    i = 0
    while i < len(lines):
        raw = lines[i]
        # Expand tabs only for block recognition, at CommonMark's four-column
        # tab stops. Exact source remains in lines and fence fingerprints.
        expanded = raw.expandtabs(4)
        if expanded.strip(" ") and (not fences.inside or stack):
            indent = len(expanded) - len(expanded.lstrip(" "))
            if fences.inside and indent < stack[-1][0]:
                tokens.append(Token("unclosed", start, i,
                                    "unclosed list fence", fence_owner))
                fences.close()
            if not fences.inside:
                # A dedented paragraph line can still belong to the list.
                # Retain that ownership so a later indented heading cannot
                # masquerade as a top-level boundary. A blank or interrupting
                # block ends laziness; no additional list syntax is modeled.
                lazy = (tokens and tokens[-1].kind == "paragraph"
                        and tokens[-1].end == i
                        and tokens[-1].owner == tuple(item[1] for item in stack)
                        # A dedented sibling item ends this item even when its
                        # ordered marker is above 1 or it is marker-only (as in
                        # CommonMark); it is not lazy prose.
                        and not re.match(r"^ *(?:[-+*]|[0-9]{1,9}[.)])(?: +|$)", expanded)
                        and not interrupts_paragraph(expanded))
                while stack and indent < stack[-1][0] and not lazy:
                    stack.pop()
        offset = stack[-1][0] if stack else 0
        line = expanded[offset:] if expanded.startswith(" " * offset) else expanded
        owner = tuple(item[1] for item in stack)
        if not fences.inside:
            # Indented code cannot interrupt a paragraph. Classify it before
            # HTML, lists or declarations, and retain it as an attachment wall.
            continuing = (tokens and tokens[-1].kind == "paragraph"
                          and tokens[-1].end == i and tokens[-1].owner == owner)
            if continuing and SETEXT.fullmatch(line):
                tokens[-1].kind = "setext"
                tokens[-1].end = i + 1
                tokens[-1].text += "\n" + line
                i += 1
                continue
            if line.startswith("    ") and line.strip() and not continuing:
                tokens.append(Token("code", i, i + 1, raw, owner))
                i += 1
                continue
            if (EMPTY_LIST.fullmatch(line)
                    and (in_quote or not continuing)):
                # Empty items are not modeled either. Include the conventional
                # content indentation only to quarantine their continuation.
                width = len(line.rstrip(" ")) + 1
                token = unsupported_block(lines, i, "", offset + width, owner)
                tokens.append(token)
                i = token.end
                continue
            match = LIST.match(line)
            # Ordered lists starting above 1 cannot interrupt a paragraph.
            # In a quote, quarantine any list-looking container first, even
            # when its interruption rules would otherwise make it prose.
            if match and continuing and not in_quote and not interrupts_paragraph(line):
                match = None
            if match:
                # More than four padding spaces: one belongs to the marker;
                # the remainder starts indented code (CommonMark list rule 2).
                padding = len(match[2])
                width = len(line) - len(match[3]) - (padding - 1 if padding > 4 else 0)
                stack.append((offset + width, i))
                continuing = False
                line = line[width:]
                owner = tuple(item[1] for item in stack)
                if line.startswith("    "):
                    tokens.append(Token("code", i, i + 1, raw, owner))
                    i += 1
                    continue
                if (in_quote or LIST.match(line) or EMPTY_LIST.fullmatch(line)
                        or HEADING.match(line)):
                    token = unsupported_block(lines, i, line, offset + width, owner)
                    tokens.append(token)
                    i = token.end
                    continue
            match = QUOTE.match(line)
            if match:
                # Quotes are attachment boundaries. Recursively inspect their
                # contents for fences, but never use quoted prose as a marker.
                begin, quoted = i, [line[match.end():]]
                i += 1
                while i < len(lines):
                    following = lines[i].expandtabs(4)
                    if not following.startswith(" " * offset):
                        break
                    following = following[offset:]
                    prefix = QUOTE.match(following)
                    if prefix:
                        quoted.append(following[prefix.end():])
                    elif (not interrupts_paragraph(following)
                          and paragraph_open("\n".join(quoted))):
                        quoted.append(following)
                    else:
                        break
                    i += 1
                tokens.append(Token("quote", begin, i, "\n".join(quoted), owner))
                continue
            terminator = html_end(line, continuing)
            if terminator is not None:
                html_offset = stack[-1][0] if stack else 0
                token = html_block(lines, i, line, html_offset, owner, terminator)
                tokens.append(token)
                i = token.end
                continue
            if owner and HEADING.match(line):
                token = unsupported_block(lines, i, line, stack[-1][0], owner)
                tokens.append(token)
                i = token.end
                continue
        was_inside = fences.inside
        if fences.feed(line):
            if was_inside:
                tokens.append(Token("fence", start, i + 1,
                                    "\n".join(lines[start:i + 1]), fence_owner))
            else:
                start, fence_owner = i, owner
            i += 1
            continue
        if fences.inside:
            i += 1
            continue
        match = HEADING.match(line)
        if match:
            heads[i] = (len(match[1]), title_text(match[2] or ""))
            kind = "heading"
        elif not line.strip(" "):
            kind = "break"
        elif line.startswith("|") or THEMATIC.fullmatch(line):
            kind = "break"
        else:
            kind = "paragraph"
        if (kind == "paragraph" and tokens and tokens[-1].kind == kind
                and tokens[-1].end == i and tokens[-1].owner == owner):
            tokens[-1].end = i + 1
            tokens[-1].text += "\n" + line
        else:
            tokens.append(Token(kind, i, i + 1, line, owner))
        i += 1
    if fences.inside:
        tokens.append(Token("unclosed", start, len(lines), "unclosed fence", fence_owner))
    return lines, heads, tokens


def declaration(text):
    """Return (status, direction), None, or raise for an empty declaration."""
    match = DECL.fullmatch(" ".join(text.strip().split("\n")))
    if not match:
        return None
    detail = match[2].strip()
    direction = ""
    for name in ("preceding", "following"):
        prefix = name + " block;"
        if detail.lower().startswith(prefix):
            direction, detail = name, detail[len(prefix):].strip()
    if not detail.strip("*_ \t"):
        raise ValueError("declaration needs scope and provenance")
    return match[1].upper(), direction


def guide_context(text, in_verify=False, in_quote=False, *, enrolled=False):
    """Share scan_guide's metadata masking, tokens and Verify selection."""
    # Only a document's leading, strictly parsed metadata is opaque. Recursive
    # quote scans must never gain a front-matter or generated-summary exemption.
    if not in_quote:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        from version_basis import split
        data, body = split(text)
        if data is not None:
            text = "\n" * text[:len(text) - len(body)].count("\n") + body
    lines, heads, tokens = tokenize(text, in_quote)
    if enrolled and not in_quote:
        from version_basis import START, END
        # Count exact physical lines, never substrings or stripped spellings.
        if lines.count(START) == lines.count(END) == 1:
            start, end = lines.index(START), lines.index(END)
            boundaries = {t.start for t in tokens if t.kind == "html"
                          and not t.owner and t.end == t.start + 1}
            if start < end and {start, end} <= boundaries:
                first_h2 = next((i for i, head in enumerate(heads)
                                 if head and head[0] == 2), len(lines))
                kind = "summary" if end < first_h2 else "html"
                summary = Token(kind, start, end + 1,
                                "\n".join(lines[start:end + 1]), ())
                # Quarantine even a misplaced pair. Report its comments below,
                # but never let enclosed headings change section selection.
                masked = lines[:start] + [""] * (end - start + 1) + lines[end + 1:]
                _, heads, tokens = tokenize("\n".join(masked), in_quote)
                tokens = [t for t in tokens if not start <= t.start <= end]
                tokens.append(summary)
                tokens.sort(key=lambda t: t.start)
    selected = (set(range(len(lines))) if in_verify else
                {i for a, b in verify_ranges(heads) for i in range(a, b)})
    return lines, heads, tokens, selected


def scan_guide(text, in_verify=False, in_quote=False, *, enrolled=False,
               with_status=False):
    """Return (line, fingerprint, marked) units and findings.

    with_status returns the parsed status (or None) instead of the boolean.
    Callers must reject findings before using these statuses as declarations.
    """
    try:
        lines, heads, tokens, selected = guide_context(
            text, in_verify, in_quote, enrolled=enrolled)
    except ValueError as exc:
        return [], [f"line 1: [unsupported-container] invalid front matter: {exc}"]
    ancestry, paths = [], {}
    for i, head in enumerate(heads):
        if head:
            while ancestry and ancestry[-1][0] >= head[0]:
                ancestry.pop()
            ancestry.append(head)
        paths[i] = list(ancestry)
    # Blank lines do not break paragraph attachment; other block types do.
    blocks = [t for t in tokens if t.kind != "break" or t.text.strip()]
    units, errors = [], []
    for k, token in enumerate(blocks):
        if (token.kind == "break" and token.text == "---"
                and token.start + 1 < len(lines)
                and lines[token.start + 1].startswith("version_basis:")):
            errors.append(f"line {token.start + 1}: "
                          "[unsupported-container] non-leading front matter")
        if token.kind not in {"fence", "unclosed", "quote"}:
            comments = ([n for n, line in enumerate(token.text.split("\n"))
                         if "<!--" in line] if token.kind in {"html", "summary"}
                        else comment_lines(token.text))
            for number in comments:
                if token.kind == "summary" and number in {0, token.end - token.start - 1}:
                    continue
                errors.append(f"line {token.start + number + 1}: "
                              "[unsupported-container] HTML comment outside fence or code span")
        if token.kind in {"html", "summary"}:
            for number, kind, _ in unsupported_features(token.text):
                errors.append(f"line {token.start + number + 1}: "
                              f"[unsupported-container] {kind} in HTML block")
            continue
        if token.kind == "setext":
            errors.append(f"line {token.end}: [unsupported-container] Setext heading")
            continue
        if token.kind == "quote":
            quoted_units, quoted_errors = scan_guide(token.text, token.start in selected, True)
            if quoted_units or quoted_errors:
                errors.append(f"line {token.start + 1}: [unsupported-container] "
                              "unsupported fenced blockquote or heading in Verify")
            continue
        if token.kind == "unsupported":
            features = unsupported_features(token.text)
            if token.start in selected or any(root for _, _, root in features):
                for number, kind, _ in features:
                    errors.append(f"line {token.start + number + 1}: "
                                  f"[unsupported-container] {kind} in unsupported container")
            continue
        if token.start not in selected:
            continue
        if in_quote and token.kind == "heading":
            errors.append(f"line {token.start + 1}: [unsupported-container] heading in quote")
        if token.kind == "unclosed":
            errors.append(f"line {token.start + 1}: {token.text}")
        if token.kind != "fence":
            continue
        context, statuses = [], []
        try:
            for delta, direction in ((-1, "following"), (1, "preceding")):
                neighbor = blocks[k + delta] if 0 <= k + delta < len(blocks) else None
                para = (neighbor and neighbor.kind == "paragraph"
                        and neighbor.owner == token.owner and neighbor.start in selected)
                context.append(neighbor.text if para else "")
                if not para:
                    continue
                mark = declaration(neighbor.text)
                if mark:
                    other = k + 2 * delta
                    shared = (0 <= other < len(blocks)
                              and blocks[other].kind == "fence"
                              and blocks[other].owner == token.owner)
                    if shared and not mark[1]:
                        continue  # no unambiguous attachment; each fence needs its own marker
                    if not mark[1] or mark[1] == direction:
                        statuses.append(mark[0])
            heading = paths[token.start][-1][1] if paths[token.start] else ""
            _, suffix, error = heading_parts(heading)
            if error:
                raise ValueError(error)
            if suffix is not None:
                mark = declaration(suffix)
                if mark:
                    statuses.append(mark[0])
            opening = re.search(r"(?:`{3,}|~{3,})([^\n]*)", lines[token.start])
            language = opening[1].strip().lower() if opening else ""
            prefix = "--" if language == "sql" else "#" if language in {
                "sh", "shell", "bash", "python", "py"
            } else None
            body = lines[token.start + 1:token.end - 1]
            first = next((line.strip() for line in body if line.strip()), "")
            if prefix and first.startswith(prefix):
                mark = declaration(first[len(prefix):].strip())
                if mark:
                    statuses.append(mark[0])
            if len(set(statuses)) > 1:
                raise ValueError("conflicting declarations; split or label the whole block REASONED")
        except ValueError as exc:
            errors.append(f"line {token.start + 1}: {exc}")
        payload = [paths[token.start], token.text, context]
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False,
                                          separators=(",", ":")).encode("utf-8")).hexdigest()
        status = statuses[0] if statuses else None
        units.append((token.start + 1, digest, status if with_status else bool(statuses)))
    return units, errors


# The fence-only scan_guide API above is also used for version-basis ordinals.
# New unit parsing must never insert units into that API or change its hashes.
KINDS = ("fence", "list-item", "table-row", "prose")


class ParserUnavailable(ValueError):
    """An absent or mismatched dependency; local checks may remain fence-only."""


def gate_parser(*, required=False):
    """Return the pinned parser, or None for a local absent/mismatched dependency.

    The lock is the sole version authority. Required callers get the precise
    absence/mismatch reason. Broken installations and invalid locks always fail.
    """
    from importlib.metadata import version
    from importlib.util import find_spec
    lock = Path(__file__).with_name("requirements-gates.txt").read_text(encoding="utf-8")
    pins = {}
    for line in lock.splitlines():
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z0-9-]*)==([0-9.]+) --hash=sha256:[0-9a-f]{64}", line)
        if not match or match[1] in pins:
            raise ValueError("invalid shared parser lock entry")
        pins[match[1]] = match[2]
    if set(pins) != {"markdown-it-py", "mdurl"}:
        raise ValueError("invalid shared parser lock")
    problem = None
    if find_spec("markdown_it") is None:
        problem = "parser absent"
    else:
        mismatches = []
        for package, wanted in pins.items():
            installed = version(package)
            if installed != wanted:
                mismatches.append(f"{package} installed {installed}, pinned {wanted}")
        if mismatches:
            problem = "; ".join(mismatches)
    if problem:
        if required:
            raise ParserUnavailable(problem + "; install tools/requirements-gates.txt")
        return None
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark").enable("table")


def inline_text(tokens, *, title=False, plain=False):
    """Project parsed inlines, never raw Markdown.

    Declaration text preserves supported emphasis and replaces opaque spans.
    The plain view keeps only text content for the provenance-content check.
    The title view renders their visible text for conservative root selection;
    that view must never be used to authorize a declaration.
    """
    parts, links = [], 0
    for token in tokens:
        kind = token.type
        if kind == "link_open":
            links += 1
            if not title:
                parts.append("" if plain else "\0")
        elif kind == "link_close":
            links -= 1
            if links < 0:
                raise ValueError("unbalanced inline link")
        elif kind in {"code_inline", "image"}:
            child_text = inline_text(token.children, title=title) if token.children else ""
            parts.append((child_text if kind == "image" else token.content) if title
                         else "" if plain else "\0")
        elif kind == "html_inline" and title:
            continue  # Tags have no visible text; declarations still reject HTML.
        elif kind in {"text", "softbreak", "hardbreak", "em_open", "em_close",
                      "strong_open", "strong_close"}:
            if not links or title:
                parts.append(token.content if kind == "text" else
                             "\n" if kind in {"softbreak", "hardbreak"} else
                             "" if title or plain else token.markup)
        else:
            raise ValueError("unsupported inline token " + kind)
    if links:
        raise ValueError("unbalanced inline link")
    return "".join(parts)


def inline_declaration(tokens, *, heading=False, directional=False):
    """Apply the declaration grammar only to text outside opaque inline tokens."""
    text = inline_text(tokens)
    if heading:
        _, text, error = heading_parts(text)
        if error:
            raise ValueError(error)
        if text is None:
            return None
    mark = unit_declaration(text, directional=directional)
    if mark:
        plain = inline_text(tokens, plain=True)
        if heading:
            _, plain, _ = heading_parts(plain)
        if not has_provenance_content(plain or ""):
            raise ValueError("declaration needs scope and provenance")
    return mark


def has_provenance_content(text):
    """Require a Unicode letter or digit in the plain scope/provenance text."""
    match = DECL.fullmatch(" ".join(text.strip().split("\n")))
    if not match:
        return False
    detail = match[2].strip()
    for name in ("preceding", "following"):
        prefix = name + " block;"
        if detail.lower().startswith(prefix):
            detail = detail[len(prefix):].strip()
    return any(ch.isalnum() for ch in detail)


@dataclass
class UnitNode:
    token: object
    children: list


def unit_declaration(text, *, directional=False):
    """Validate the existing declaration spellings without accepting broken emphasis."""
    mark = declaration(text)
    if not mark and re.match(r"(?i)^[*_]*(?:DEMONSTRATED|REASONED)[*_ \t]*:", text.strip()):
        raise ValueError("malformed declaration emphasis")
    if mark:
        prefix = re.match(
            r"(?i)^(?:DEMONSTRATED:|REASONED:|"
            r"(?P<em>\*\*|__)(?:DEMONSTRATED|REASONED)"
            r"(?::(?P=em)|(?P=em):|:(?=.+(?P=em))))", text.strip(), re.S)
        if not prefix:
            raise ValueError("malformed declaration emphasis: " + repr(text))
        if mark[1] and not directional:
            raise ValueError("directional declaration only applies to prose and fences")
    return mark


def scan_units(text, *, enrolled=False, parser=None):
    """Return (line, kind, fingerprint, status) units and fail-closed findings.

    All Verify paragraphs, list items and body rows count. This adapter combines
    unchanged legacy fence results with a separate, single-parse unit layer.
    Parser fence validation can add findings, never alter legacy results.
    Structural findings are never eligible for a baseline exemption.
    """
    fences, errors = scan_guide(text, enrolled=enrolled, with_status=True)
    units = [(line, "fence", digest, status) for line, digest, status in fences]
    if parser is None:
        parser = gate_parser()
    if parser is None:
        raise ValueError("scan_units requires the pinned parser")
    try:
        # Preserve the legacy selector; any difference from rendered titles
        # or opaque suffixes in the unit layer must be a structural finding.
        _, legacy_heads, legacy_tokens, legacy_selected = guide_context(
            text, enrolled=enrolled)
        legacy_ranges = set(verify_ranges(legacy_heads))
        # Front matter is strict JSON metadata, not Markdown. Preserve maps
        # while masking it; no declaration or heading is selected from source.
        from version_basis import split, START, END
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        try:
            data, body = split(text)
        except ValueError as exc:
            raise ValueError("[unsupported-container] invalid front matter: " + str(exc)) from exc
        if data is not None:
            text = "\n" * text[:len(text) - len(body)].count("\n") + body
        lines = text.split("\n")
        env = {}
        tokens = parser.parse(text, env)
        roots, stack = [], []
        containers = {"heading", "paragraph", "bullet_list", "ordered_list",
                      "list_item", "table", "thead", "tbody", "tr", "th", "td",
                      "blockquote"}
        leaves = {"inline", "fence", "hr", "code_block", "html_block"}
        for token in tokens:
            if token.nesting == -1:
                if (not stack or token.type != stack[-1].token.type.replace("_open", "_close")):
                    raise ValueError("unrecognized or unbalanced closing token " + token.type)
                stack.pop()
                continue
            if not (token.type in leaves and token.nesting == 0 or
                    token.type.endswith("_open") and token.type[:-5] in containers
                    and token.nesting == 1):
                raise ValueError("unrecognized block token " + token.type)
            # Cells and closing tokens have no map in this parser. Cells inherit
            # their explicitly validated row span; all other blocks need a map.
            if token.type in {"th_open", "td_open"}:
                if not stack or stack[-1].token.type != "tr_open":
                    raise ValueError("table cell outside mapped row")
            elif (not isinstance(token.map, list) or len(token.map) != 2
                  or any(type(n) is not int for n in token.map)
                  or not 0 <= token.map[0] < token.map[1] <= len(lines)):
                raise ValueError("missing or invalid source map for " + token.type)
            if token.type == "inline":
                if not isinstance(token.children, list) or token.content and not token.children:
                    raise ValueError("inline missing parsed children")
                inline_text(token.children, title=True)
            node = UnitNode(token, [])
            (stack[-1].children if stack else roots).append(node)
            if token.nesting == 1:
                stack.append(node)
        if stack:
            raise ValueError("unclosed parser token")

        # Recognize generated summaries from mapped, top-level HTML tokens.
        # Excluding these nodes needs no second parse or legacy tokenization.
        if enrolled:
            starts = [n for n in roots if n.token.type == "html_block"
                      and n.token.content == START + "\n"]
            ends = [n for n in roots if n.token.type == "html_block"
                    and n.token.content == END + "\n"]
            if len(starts) == len(ends) == 1:
                start, end = starts[0].token.map[0], ends[0].token.map[1]
                first_h2 = next((n.token.map[0] for n in roots
                                 if n.token.type == "heading_open" and n.token.tag == "h2"),
                                len(lines))
                if start < end <= first_h2:
                    roots = [n for n in roots if not start <= n.token.map[0] < end]

        def paragraph_inline(node):
            if len(node.children) != 1 or node.children[0].token.type != "inline":
                raise ValueError("paragraph missing inline content")
            return node.children[0].token

        # Selection uses only validated inline tokens. A canonical title followed
        # by ':' or '(' remains a root regardless of the suffix's declaration.
        # Opaque suffixes therefore cannot hide the section they fail to mark.
        heads, heading_inlines = {}, {}

        def collect_headings(nodes, nested=False):
            for node in nodes:
                t = node.token
                if t.type == "heading_open":
                    inline = paragraph_inline(node)
                    title = title_text(inline_text(inline.children or [], title=True))
                    base = re.split(r"[(:]", title, maxsplit=1)[0].strip()
                    if not re.fullmatch(r"h[1-6]", t.tag):
                        raise ValueError("invalid heading level")
                    is_root = bool(TITLE.fullmatch(base))
                    if nested and is_root:
                        raise ValueError(f"line {t.map[0] + 1}: [unsupported-container] "
                                         "Verify heading in unsupported container")
                    if not nested:
                        heads[t.map[0]] = (int(t.tag[1:]), is_root)
                        heading_inlines[t.map[0]] = inline
                collect_headings(node.children, True)

        collect_headings(roots)
        selected, paths, ancestry, heading_starts = set(), {}, [], {}
        current_heading, root_level, root_start = None, None, None
        parsed_ranges = set()
        for i in range(len(lines)):
            head = heads.get(i)
            if head:
                level, is_root = head
                if root_level is not None and level <= root_level:
                    parsed_ranges.add((root_start, i))
                    root_level = None
                if root_level is None and is_root:
                    root_level, root_start = level, i
                current_heading = i
                while ancestry and ancestry[-1][0] >= level:
                    ancestry.pop()
                # Raw inline content is identity only, never a declaration or
                # selection input. Keep existing unit fingerprints stable.
                ancestry.append((level, title_text(heading_inlines[i].content)))
            if root_level is not None:
                selected.add(i)
            paths[i] = list(ancestry)
            heading_starts[i] = current_heading
        if root_level is not None:
            parsed_ranges.add((root_start, len(lines)))

        def agreement(kind, legacy, parsed):
            if legacy != parsed:
                # One-based, half-open spans retain identity and boundaries.
                display = lambda spans: [(a + 1, b + 1) for a, b in sorted(spans)]
                errors.append(f"[layer-disagreement] {kind}: "
                              f"legacy-only {display(legacy - parsed)}; "
                              f"parser-only {display(parsed - legacy)}")

        agreement("Verify roots", legacy_ranges, parsed_ranges)
        # A final empty split line is not part of a parser fence's physical map.
        eof = len(lines) - int(lines[-1] == "")
        legacy_spans = {(t.start, min(t.end, eof)) for t in legacy_tokens
                        if t.kind in {"fence", "unclosed"} and t.start in legacy_selected}
        parsed_fences = [t for t in tokens if t.type == "fence" and t.map[0] in selected]
        agreement("Verify fences", legacy_spans, {tuple(t.map) for t in parsed_fences})
        # Validate every fence before declaration walking can fail. The parser
        # accepts EOF/container ends as implicit closes; the gate does not.
        for t in parsed_fences:
            start, end = t.map
            closing = lines[end - 1].expandtabs(4).lstrip(" ")
            while QUOTE.match(closing):
                closing = QUOTE.sub("", closing, count=1).lstrip(" ")
            closure = Fences()
            closure.feed(t.markup)
            has_closer = end - start == t.content.count("\n") + 2
            if not has_closer or not closure.feed(closing) or closure.inside:
                errors.append(f"line {start + 1}: unclosed fence (parser)")
        covered = set()
        legacy_fences = {line: status for line, _, status in fences}
        heading_marks = {}
        def source(span):
            return "\n".join(lines[span[0]:span[1]])

        def first_paragraph(node):
            return next((c for c in node.children if c.token.type == "paragraph_open"), None)

        def heading_status(start):
            position = heading_starts[start]
            if position is None:
                return None
            if position not in heading_marks:
                children = heading_inlines[position].children or []
                # Inline HTML cannot authorize a declaration. Retain units
                # below that root as unmarked and report the unsupported syntax.
                if any(t.type == "html_inline" for t in children):
                    errors.append(f"line {position + 1}: unit extraction failed: "
                                  "unsupported inline token html_inline")
                    heading_marks[position] = None
                else:
                    heading_marks[position] = inline_declaration(children, heading=True)
            return heading_marks[position]

        def status_for(start, texts, directional=False):
            marks = [heading_status(start)]
            marks += [inline_declaration(t.children or [], directional=directional) for t in texts]
            statuses = {m[0] for m in marks if m}
            if len(statuses) > 1:
                raise ValueError("conflicting declarations")
            return next(iter(statuses), None)

        def emit(node, kind, owners, schema, texts):
            start, end = node.token.map
            if kind == "list-item":
                while end > start and not lines[end - 1].strip():
                    end -= 1
            payload = ["verify-unit-v1", kind, paths[start], owners, schema,
                       source((start, end))]
            digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False,
                                               separators=(",", ":")).encode("utf-8")).hexdigest()
            status = status_for(start, texts, directional=kind == "prose")
            units.append((start + 1, kind, digest, status))

        item_starts = {t.map[0] for t in tokens if t.type == "list_item_open"}

        def cells(line, start):
            # Match the pinned table rule's escaped-pipe convention, including
            # pipes in code spans. No silent padding or truncation is permitted.
            # Raw source here can only reject structure, never declare a unit.
            from markdown_it.rules_block.table import escapedSplit
            line = line.expandtabs(4).lstrip()
            if start in item_starts:
                marker = LIST.match(line)
                if marker is None:
                    raise ValueError("unrecognized table container prefix")
                line = marker[3]
            parts = escapedSplit(line.strip())
            if parts and not parts[0].strip():
                parts.pop(0)
            if parts and not parts[-1].strip():
                parts.pop()
            return parts

        def walk(nodes, owners=None, schema=None, in_item=False, in_cell=False, table_width=None):
            owners = [] if owners is None else owners
            schema = [] if schema is None else schema
            for index, node in enumerate(nodes):
                t = node.token
                span = t.map
                if span is None:  # only table cells, validated above
                    walk(node.children, owners, schema, in_item, True, table_width)
                    continue
                start, end = span
                active = bool(selected.intersection(range(start, end)))
                if not active:
                    continue
                if not set(range(start, end)) <= selected:
                    raise ValueError(f"line {start + 1}: block crosses Verify boundary")
                kind = t.type
                if kind in {"blockquote_open", "code_block", "html_block"}:
                    raise ValueError(f"line {start + 1}: [unsupported-container] {kind}")
                if kind == "inline":
                    inline_text(t.children or [])
                elif kind == "heading_open":
                    if in_item or in_cell:
                        raise ValueError("[unsupported-container] heading in unit container")
                    if t.markup not in {"#", "##", "###", "####", "#####", "######"}:
                        raise ValueError("[unsupported-container] Setext heading")
                    heading_status(start)
                    covered.update(range(start, end))
                elif kind == "hr":
                    covered.update(range(start, end))
                elif kind == "list_item_open":
                    first = first_paragraph(node)
                    if not node.children:
                        raise ValueError(f"line {start + 1}: [unsupported-container] empty item")
                    if any(c.token.map[0] == start for c in node.children
                           if c.token.type in {"bullet_list_open", "ordered_list_open"}):
                        raise ValueError("[unsupported-container] compact list")
                    texts = [paragraph_inline(first)] if first else []
                    emit(node, "list-item", owners, [], texts)
                    owner = source(first.token.map) if first else ""
                    walk(node.children, owners + [owner], schema, True, in_cell, table_width)
                elif kind == "paragraph_open":
                    if not in_item and not in_cell:
                        emit(node, "prose", owners, [], [paragraph_inline(node)])
                    covered.update(range(start, end))
                    walk(node.children, owners, schema, in_item, in_cell, table_width)
                elif kind == "table_open":
                    if end - start < 2:
                        raise ValueError("table missing schema")
                    table_schema = lines[start:start + 2]
                    widths = [len(cells(line, start + offset))
                              for offset, line in enumerate(table_schema)]
                    if not widths[0] or widths[0] != widths[1]:
                        raise ValueError("ragged table schema")
                    covered.update(range(start, start + 2))
                    walk(node.children, owners, table_schema, in_item, in_cell, widths[0])
                elif kind == "tr_open":
                    cell_nodes = [c for c in node.children if c.token.type in {"td_open", "th_open"}]
                    if end != start + 1 or len(cells(lines[start], start)) != len(cell_nodes):
                        raise ValueError(f"line {start + 1}: ragged table row")
                    if len(cell_nodes) != table_width:
                        raise ValueError(f"line {start + 1}: table row differs from schema")
                    if cell_nodes and cell_nodes[0].token.type == "td_open":
                        texts = [paragraph_inline(c) for c in cell_nodes]
                        emit(node, "table-row", owners, schema, texts)
                    covered.update(range(start, end))
                    walk(node.children, owners, schema, in_item, in_cell, table_width)
                elif kind == "fence":
                    covered.update(range(start, end))
                    marks = [heading_status(start)]
                    for delta, direction in ((-1, "following"), (1, "preceding")):
                        k = index + delta
                        if not 0 <= k < len(nodes) or nodes[k].token.type != "paragraph_open":
                            continue
                        mark = inline_declaration(paragraph_inline(nodes[k]).children or [],
                                                  directional=True)
                        other = index + 2 * delta
                        shared = 0 <= other < len(nodes) and nodes[other].token.type == "fence"
                        if mark and (mark[1] == direction or not mark[1] and not shared):
                            marks.append(mark)
                    language = t.info.strip().lower()
                    prefix = "--" if language == "sql" else "#" if language in {
                        "sh", "shell", "bash", "python", "py"} else None
                    first = next((line.strip() for line in t.content.split("\n") if line.strip()), "")
                    if prefix and first.startswith(prefix):
                        comment = first[len(prefix):].strip()
                        inlines = parser.parseInline(comment, env)[0].children or []
                        marks.append(inline_declaration(inlines, directional=True))
                    statuses = {m[0] for m in marks if m}
                    if len(statuses) > 1:
                        raise ValueError("conflicting declarations")
                    status = next(iter(statuses), None)
                    line = start + 1
                    if line not in legacy_fences and status is None:
                        errors.append(f"line {line}: parser fence declaration missing "
                                      "in parser-selected Verify section")
                    elif line in legacy_fences and legacy_fences[line] and status != legacy_fences[line]:
                        errors.append(f"line {line}: parser fence declaration disagrees "
                                      "with legacy declaration")
                elif kind in {"bullet_list_open", "ordered_list_open", "thead_open", "tbody_open"}:
                    walk(node.children, owners, schema, in_item, in_cell, table_width)
                else:
                    raise ValueError("unhandled block token " + kind)
        walk(roots)
        missing = [i + 1 for i in sorted(selected - covered) if lines[i].strip()]
        if missing:
            raise ValueError(f"uncovered Verify source lines: {missing}")
        # References can disappear into env without producing a block token.
        references = list(env.get("references", {}).values()) + env.get("duplicate_refs", [])
        for reference in references:
            span = reference.get("map")
            if span is None or selected.intersection(range(*span)):
                raise ValueError("unsupported reference definition in Verify")
    except Exception as exc:
        # Parser exceptions and unmodeled syntax are findings, never a skipped
        # scan or a baseline-eligible unit. KeyboardInterrupt still propagates.
        errors.append(f"unit extraction failed: {exc}")
    return units, errors


def scan(root, parser=None):
    counts, locations, errors, marked = Counter(), {}, [], Counter()
    enrolled = set((root / "tools/version_basis_guides.txt").read_text(
        encoding="utf-8").splitlines())
    paths = sorted(p for p in root.iterdir() if p.suffix == ".md" and p.name not in META_EXCLUDE)
    if not paths:
        raise ValueError("guide corpus is empty")
    for path in paths:
        if not path.is_file():
            raise OSError(f"guide is not a readable regular file: {path}")
        try:
            text = path.read_text(encoding="utf-8")
            if parser is None:
                fences, findings = scan_guide(text, enrolled=path.name in enrolled)
                units = [(line, "fence", digest, status) for line, digest, status in fences]
            else:
                units, findings = scan_units(text, enrolled=path.name in enrolled, parser=parser)
        except ValueError as exc:
            # UnicodeError is handled by main as an input error, not a convention.
            if isinstance(exc, UnicodeError):
                raise
            errors.append(f"{path.name}: {exc}")
            continue
        errors.extend(f"{path.name}: {finding}" for finding in findings)
        for line, kind, digest, has_mark in units:
            if has_mark:
                marked[kind] += 1
            else:
                key = (path.name, kind, digest)
                counts[key] += 1
                locations.setdefault(key, []).append(line)
    return counts, locations, errors, marked


def load_baseline(path):
    counts = Counter()
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if (len(fields) != 4 or not re.fullmatch(r"[^/\\\s]+\.md", fields[0])
                or fields[1] not in KINDS or not re.fullmatch(r"[0-9a-f]{64}", fields[2])
                or not re.fullmatch(r"[1-9][0-9]*", fields[3])):
            raise ValueError(f"baseline line {number}: malformed entry")
        key = tuple(fields[:3])
        if key in counts:
            raise ValueError(f"baseline line {number}: duplicate key")
        counts[key] = int(fields[3])
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true")
    mode.add_argument("--seed-baseline", "--write-baseline", dest="seed_baseline", action="store_true")
    mode.add_argument("--assert-parser", action="store_true")
    parser.add_argument("--require-parser", action="store_true",
                        help="fail instead of skipping unavailable unit checks (CI)")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        try:
            parser = gate_parser(required=True)
        except ParserUnavailable as exc:
            if args.seed_baseline:
                raise ValueError(f"seeding requires the pinned parser: {exc}") from exc
            if args.assert_parser or args.require_parser or os.environ.get("CI"):
                raise
            parser = None
            print(f"  SKIP  Verify list-item/table-row/prose checks: {exc} "
                  "(fence checks still run)")
        if args.assert_parser:
            if parser is None:
                raise ValueError("pinned parser missing; install tools/requirements-gates.txt")
            print("  ok    shared gate parser versions match tools/requirements-gates.txt")
            return 0
        if args.seed_baseline:
            if parser is None:
                raise ValueError("seeding requires the pinned parser")
            if (root / BASELINE).exists() and load_baseline(root / BASELINE):
                raise ValueError("seed refused: baseline already has entries")
        current, locations, errors, marked = scan(root, parser)
        structural_errors = bool(errors)
        if args.seed_baseline:
            if errors:
                for error in errors:
                    print(f"  FAIL  VERIFY-MARK {error}")
                return 1
            body = "# Explicit one-time seed; remove exemptions as units are marked.\n"
            body += "# guide<TAB>kind<TAB>sha256<TAB>count; no automatic refresh.\n"
            body += "".join("\t".join(key) + f"\t{count}\n"
                            for key, count in sorted(current.items()))
            (root / BASELINE).write_text(body, encoding="utf-8")
            print(f"  ok    wrote {sum(current.values())} grandfathered units")
            for kind in KINDS:
                print(f"  ok    seeded {kind}: "
                      f"{sum(n for key, n in current.items() if key[1] == kind)}")
            return 0
        baseline = load_baseline(root / BASELINE)
        # Local absent/mismatched parsers leave the fence ratchet active.
        # Validate the entire baseline first, including skipped kinds.
        if parser is None:
            baseline = Counter({k: n for k, n in baseline.items() if k[1] == "fence"})
        retained = Counter()
        for key in sorted(current.keys() | baseline.keys()):
            actual, allowed = current[key], baseline[key]
            where = f"{key[0]}:{','.join(map(str, locations.get(key, [])))}"
            if actual > allowed:
                errors.append(f"{where} new/changed/excess {key[1]} {key[2]} ({actual} > {allowed})")
            if actual < allowed:
                errors.append(f"{key[0]} stale baseline {key[1]} {key[2]} ({actual} < {allowed}); remove it")
            kept = min(actual, allowed)
            if kept:
                retained[key[1]] += kept
                print(f"  BASELINE  {where} {key[1]} {key[2]} retained {kept}")
        for error in errors:
            print(f"  FAIL  VERIFY-MARK {error}")
        for kind in KINDS if parser is not None else ("fence",):
            print(f"  COUNTS  {kind}: {marked[kind]} marked, {retained[kind]} retained")
        print(f"  {'FAIL' if errors else 'ok  '}  Verify marking: {sum(marked.values())} marked, "
              f"{sum(retained.values())} grandfathered units retained, {len(errors)} findings")
        return 1 if structural_errors or errors and args.strict else 0
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  VERIFY-MARK input error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, ImportError) as exc:
        print(f"  FAIL  VERIFY-MARK {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
