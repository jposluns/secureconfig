#!/usr/bin/env python3
"""Offline Verify fence marker ratchet; stdlib only.

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

This is not a full CommonMark parser: link-reference definitions, full list
semantics and general inline parsing are not implemented. Status emphasis uses
the declaration grammar, not a general emphasis parser. Quoted declarations
are never attached to outside fences.

Fingerprints contain normalized heading ancestry, exact LF-normalized fence
text (including delimiters/info), and adjacent paragraphs in the same list
item. Line numbers and list-item serials are diagnostic, never identity.
Ambiguous paragraphs supply no declaration to either fence. Malformed or
conflicting declarations cannot be grandfathered. --write-baseline is an explicit one-time seed operation.
Normal runs never rewrite it. Strict mode rejects new, changed, duplicate and
stale exemptions. OS/UTF-8 errors exit 2; convention errors exit 1 in strict
mode (also in seed mode). Default mode reports convention findings, exits 0.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences
from _verify_sections import TITLE, heading_parts, title_text, verify_ranges
from _verify_sections import HEADING, guides

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


def scan(root):
    counts, locations, errors, marked = Counter(), {}, [], 0
    enrolled = set((root / "tools/version_basis_guides.txt").read_text(
        encoding="utf-8").splitlines())
    for path in guides(root):
        try:
            units, findings = scan_guide(path.read_text(encoding="utf-8"),
                                         enrolled=path.name in enrolled)
        except ValueError as exc:
            # UnicodeError is handled by main as an input error, not a convention.
            if isinstance(exc, UnicodeError):
                raise
            errors.append(f"{path.name}: {exc}")
            continue
        errors.extend(f"{path.name}: {finding}" for finding in findings)
        for line, digest, has_mark in units:
            if has_mark:
                marked += 1
            else:
                key = (path.name, "fence", digest)
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
                or fields[1] != "fence" or not re.fullmatch(r"[0-9a-f]{64}", fields[2])
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
    mode.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        current, locations, errors, marked = scan(root)
        if args.write_baseline:
            if errors:
                for error in errors:
                    print(f"  FAIL  VERIFY-MARK {error}")
                return 1
            body = "# Explicit one-time seed; remove exemptions as fences are marked.\n"
            body += "# guide<TAB>fence<TAB>sha256<TAB>count; no automatic refresh.\n"
            body += "".join("\t".join(key) + f"\t{count}\n"
                            for key, count in sorted(current.items()))
            (root / BASELINE).write_text(body, encoding="utf-8")
            print(f"  ok    wrote {sum(current.values())} grandfathered fences")
            return 0
        baseline = load_baseline(root / BASELINE)
        retained = 0
        for key in sorted(current.keys() | baseline.keys()):
            actual, allowed = current[key], baseline[key]
            where = f"{key[0]}:{','.join(map(str, locations.get(key, [])))}"
            if actual > allowed:
                errors.append(f"{where} new/changed/excess fence {key[2]} ({actual} > {allowed})")
            if actual < allowed:
                errors.append(f"{key[0]} stale baseline {key[2]} ({actual} < {allowed}); remove it")
            kept = min(actual, allowed)
            if kept:
                retained += kept
                print(f"  BASELINE  {where} {key[2]} retained {kept}")
        for error in errors:
            print(f"  FAIL  VERIFY-MARK {error}")
        print(f"  {'FAIL' if errors else 'ok  '}  Verify marking: {marked} marked, "
              f"{retained} grandfathered fences retained, {len(errors)} findings")
        return 1 if errors and args.strict else 0
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  VERIFY-MARK input error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"  FAIL  VERIFY-MARK {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
