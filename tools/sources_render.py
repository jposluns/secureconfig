#!/usr/bin/env python3
"""Advisory rendered Sources comparison. The line-grammar gate stays authoritative.

One shared, pinned CommonMark parse (with tables) per guide body resolves
references document-wide. Bare URLs in text use the existing Sources URL
boundaries; link labels and image alt text do not add duplicate destinations.
Positions below are zero-based body lines, after metadata/summary removal.

Host identity uses host-only NFKC and Python's built-in idna codec (IDNA 2003,
Unicode 3.2 nameprep), NOT full UTS #46 or IDNA 2008. In particular, sharp s
folds to ss. Every mapped host must survive an ASCII/decode/re-encode
round trip; incompatible A-labels are findings. NFKC follows the running Python Unicode database. Percent-encoded
hosts and invalid A-labels are findings. This is not browser URL canonicalization.
"""
import argparse
from collections import Counter
from dataclasses import dataclass, field
import ipaddress
import os
from pathlib import Path
import re
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import version_basis as legacy
from check_guide_shape import SOURCES_RE, headings, section_body
from check_verify_marking import ParserUnavailable, gate_parser, inline_text, tokenize


def normalize_url(url):
    """Preserve legacy scheme/authority folding and exact suffix/delimiters."""
    if not isinstance(url, str) or not url or any(
            c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url):
        raise ValueError("empty URL or whitespace/control in URL")
    if legacy._ESCAPE.search(url) or legacy._UNRESERVED.search(url):
        raise ValueError("URL contains an escape, entity or encoded unreserved character")
    if re.search(r"%(?![0-9A-Fa-f]{2})", url):
        raise ValueError("malformed percent escape")
    match = re.fullmatch(r"(https?)://([^/?#]+)(.*)", url, re.I)
    if not match:
        raise ValueError("destination is not an absolute HTTP(S) URL")
    scheme, authority, suffix = match.groups()
    user, sep, hostport = authority.rpartition("@")
    if not sep:
        hostport = authority
    elif "@" in user:
        raise ValueError("ambiguous userinfo")
    prefix = user.lower() + "@" if sep else ""
    if hostport.startswith("["):
        host, close, port = hostport[1:].partition("]")
        if not close or "%" in host:
            raise ValueError("invalid or scoped IP literal")
        ipaddress.IPv6Address(host)
        host = "[" + host.lower() + "]"  # Do not collapse alternate IPv6 spellings.
    else:
        host, colon, port = hostport.partition(":")
        port = colon + port
        # Decode A-labels before NFKC, including ones emitted by the parser.
        labels = re.split(r"[.\u3002\uff0e\uff61]", host)
        host = ".".join(label.lower().encode("ascii").decode("idna")
                        if label.lower().startswith("xn--") else label for label in labels)
        host = unicodedata.normalize("NFKC", host)
        if any(c in host for c in "/?#@:\\[]%") or any(c.isspace() for c in host):
            raise ValueError("host mapping introduces a delimiter or unsupported character")
        host = host.encode("idna").decode("ascii").lower()
        if host.encode("ascii").decode("idna").encode("idna").decode("ascii").lower() != host:
            raise ValueError("host does not round-trip through IDNA 2003")
        labels = host[:-1].split(".") if host.endswith(".") else host.split(".")
        if len(host.rstrip(".")) > 253 or any(
                not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                for label in labels):
            raise ValueError("invalid DNS host")
    if port and (not re.fullmatch(r":[0-9]+", port) or not 0 <= int(port[1:]) <= 65535):
        raise ValueError("invalid port")
    return scheme.lower() + "://" + prefix + host + port + suffix


# Reuse the authoritative matcher's grammar, including punctuation and the
# special underscore opener. No linkifier or second URL grammar is introduced.
BARE_OPEN = re.compile(legacy._OPENS)
BARE_CLOSE = re.compile(legacy._CLOSES)
BARE_UNDERSCORE_CLOSE = re.compile(legacy._CLOSES_AFTER_UNDERSCORE)
# Only these rendered trailing characters may be discarded. A terminal
# underscore is prose by the legacy convention; an internal one is not.
TRAILING_PROSE = frozenset("?!.,:;_)'\"]>}")


def bare_urls(text):
    """Accept the rendered chunk from a URL marker to whitespace only after
    classifying all of it. The first legacy closing boundary chooses its
    endpoint; shortening is allowed only for a tail wholly in TRAILING_PROSE.

    Literal stars, tildes and underscores followed by text are never evidence
    of emphasis. Write literal stars or tildes in paths as explicit links.
    The parser has already consumed real emphasis before this function runs.

    Terminal punctuation, including terminal underscores, is a prose judgement;
    explicit links avoid that ambiguity. Authority boundaries, non-ASCII bare
    authorities and parentheses within destinations fail closed. A marker inside
    an accepted destination is URL data, not a second independent citation.
    """
    urls, findings = [], []
    consumed = 0
    for marker in legacy._URL_OR_LINK.finditer(text):
        if marker.start() < consumed:
            continue
        start = marker.start()
        end = start
        while end < len(text) and not text[end].isspace():
            end += 1
        chunk = text[start:end]
        consumed = end
        diagnostic = f"unclassified URL-like text {chunk!r}"
        if marker[0].lower() in {"http://", "https://"} and BARE_OPEN.match(text, start):
            authority = re.match(r"[^/?#]*", chunk[len(marker[0]):])[0]
            authority_end = marker.end() + len(authority)
            underscore = start > 0 and text[start - 1] == "_"
            closing = BARE_UNDERSCORE_CLOSE if underscore else BARE_CLOSE
            stop = next((n for n in range(marker.end() + 1, end + 1)
                         if closing.match(text, n)), None)
            if not authority.isascii():
                diagnostic = f"non-ASCII authority in bare URL {chunk!r}"
            elif stop is not None:
                candidate, tail = text[start:stop], text[stop:end]
                terminal = all(char in TRAILING_PROSE for char in tail)
                if (stop < authority_end and
                        (authority_end < end or "@" in text[stop:authority_end]
                         or not terminal)):
                    diagnostic = f"closing boundary inside bare URL authority {chunk!r}"
                elif "(" in candidate or ")" in candidate:
                    diagnostic = f"ambiguous parentheses in bare URL {chunk!r}"
                elif not terminal:
                    diagnostic = (f"unclassified bare URL tail {tail!r} in {chunk!r}; "
                                  "write it as an explicit link")
                else:
                    try:
                        normalize_url(candidate)
                    except (ValueError, UnicodeError) as exc:
                        diagnostic = f"invalid bare URL {candidate!r}: {exc}"
                    else:
                        urls.append(candidate)
                        continue
        findings.append(diagnostic)
    return urls, findings


@dataclass
class Item:
    owner: tuple
    span: tuple
    hrefs: list = field(default_factory=list)


@dataclass
class Rendered:
    items: dict = field(default_factory=dict)
    outside: list = field(default_factory=list)
    findings: list = field(default_factory=list)


def source_map(span, size, kind):
    if (not isinstance(span, list) or len(span) != 2
            or any(type(n) is not int for n in span)
            or not 0 <= span[0] < span[1] <= size):
        raise ValueError("missing or invalid source map for " + kind)
    return tuple(span)


def scan(body, parser):
    """Extract nearest-item hrefs; uncertainty is always a finding.

    Keep today's unindented ATX boundaries, including its refusal to use
    Setext as an end boundary. Reconcile every selected opener and boundary
    with parsed top-level headings so an opaque/nested root cannot hide work.
    Cells inherit row maps; inline children inherit their mapped inline block.
    Closing tokens inherit their opener. These tokens normally have no map.
    Raw HTML blocks are refused guide-wide because they can hide headings.
    Opaque inline boundaries alarm only when URL text continues across a join
    in the rendered text: a marker straddles the join, or a complete marker
    shares a whitespace-free chunk with content on the other side. Strip only
    TRAILING_PROSE from the chunk's end before testing that continuation.
    Thus code mentioning a scheme followed only by trailing prose punctuation
    and whitespace/end is documentation, not a continuation. Code contributes
    visible text to this alarm-only projection, never destinations. Images
    are checked both with visible alt text and with no textual width (loaded
    image); neither projection contributes destinations.
    Inline HTML is refused inside Sources; mapped inline HTML elsewhere cannot
    hide a selected opener or boundary without the reconciliation failing.
    """
    result = Rendered()
    try:
        lines = body.splitlines()
        _, ranges = legacy._sources_ranges(body, headings(body))
        if not ranges:
            raise ValueError("no Sources section")
        selected = {n for start, end in ranges for n in range(start, end)}
        env = {}
        tokens = parser.parse(body, env)  # The only Markdown parse.
        stack, parsed_heads = [], {}
        containers = {"heading", "paragraph", "bullet_list", "ordered_list",
                      "list_item", "blockquote", "table", "thead", "tbody", "tr", "th", "td"}
        leaves = {"inline", "fence", "code_block", "html_block", "hr"}

        def record(href, span, owner):
            try:
                normalize_url(href)
            except (ValueError, UnicodeError) as exc:
                result.findings.append(f"body line {span[0] + 1}: URL {href!r}: {exc}")
                return
            if owner:
                result.items[owner].hrefs.append(href)
            else:
                result.outside.append(href)

        def inlines(children, span, owner, emit=True):
            if not isinstance(children, list):
                raise ValueError("inline missing parsed children")
            opened, plain = [], []
            # Alarm-only projections; never feed them to destination extraction.
            projections = []
            image_views = (False, True) if any(t.type == "image" for t in children) else (False,)
            for show_alt in image_views:
                projected, offsets = [], []
                position = 0
                for child in children:
                    visible = (child.content if child.type in {"text", "code_inline"}
                               else inline_text(child.children, title=True)
                               if child.type == "image" and show_alt
                               else "\n" if child.type in {"softbreak", "hardbreak"} else "")
                    offsets.append((position, position + len(visible)))
                    projected.append(visible)
                    position += len(visible)
                projected = "".join(projected)
                # Only a positively classified terminal prose tail ends a URL
                # chunk before whitespace. All other joined content alarms.
                url_chunks = [
                    (chunk.start(), chunk.start() + len(chunk[0].rstrip("".join(TRAILING_PROSE))))
                    for chunk in re.finditer(r"\S+", projected)
                    if legacy._URL_OR_LINK.search(chunk[0])
                ]
                projections.append((offsets, url_chunks))
            html_reported = False

            def flush():
                # Emphasis has no visible separator. Join its text tokens so a
                # path such as /__init__.py is seen as rendered: /init.py.
                urls, errors = bare_urls("".join(plain))
                plain.clear()
                for href in urls:
                    record(href, span, owner)
                result.findings.extend(f"body line {span[0] + 1}: {error}" for error in errors)

            for index, token in enumerate(children):
                kind = token.type
                edges = ()
                if kind == "link_open":
                    edges = (-1,)
                elif kind == "link_close":
                    edges = (1,)
                elif kind in {"code_inline", "image"} and "link_open" not in opened:
                    edges = (-1, 1)
                if emit:
                    # Link labels belong to their destination, not bare text.
                    # Transparent emphasis tokens do not separate visible text.
                    touches = False
                    for offsets, url_chunks in projections:
                        for step in edges:
                            boundary = offsets[index][0 if step == -1 else 1]
                            if any(start < boundary < end for start, end in url_chunks):
                                touches = True
                    if touches:
                        result.findings.append(
                            f"body line {span[0] + 1}: URL-like text touches {kind}")
                if kind not in {"text", "em_open", "em_close", "strong_open", "strong_close"}:
                    flush()
                if kind in {"link_open", "em_open", "strong_open"} and token.nesting == 1:
                    opened.append(kind)
                    if kind == "link_open" and emit:
                        record(token.attrGet("href"), span, owner)
                elif kind in {"link_close", "em_close", "strong_close"} and token.nesting == -1:
                    if not opened or opened.pop().replace("_open", "_close") != kind:
                        raise ValueError("unbalanced inline token " + kind)
                elif kind == "text" and token.nesting == 0:
                    if emit and "link_open" not in opened:
                        plain.append(token.content)
                elif kind == "html_inline":
                    if emit and not html_reported:
                        result.findings.append(f"body line {span[0] + 1}: unclassified raw HTML")
                        html_reported = True
                elif kind == "image" and token.nesting == 0:
                    # Image alt children do not render anchors; still validate types.
                    inlines(token.children, span, owner, emit=False)
                elif kind not in {"text", "code_inline", "softbreak", "hardbreak"} or token.nesting:
                    raise ValueError("unclassified inline token " + kind)
            flush()
            if opened:
                raise ValueError("unclosed inline token")

        for token in tokens:
            kind = token.type
            if token.nesting == -1:
                if not stack or stack[-1][0].type.replace("_open", "_close") != kind:
                    raise ValueError("unbalanced block token " + kind)
                stack.pop()
                continue
            if not (kind in leaves and token.nesting == 0 or token.nesting == 1
                    and kind.endswith("_open") and kind[:-5] in containers):
                raise ValueError("unclassified block token " + kind)
            if kind in {"th_open", "td_open"}:
                if not stack or stack[-1][0].type != "tr_open":
                    raise ValueError("table cell without mapped row")
                span = stack[-1][1]
            else:
                span = source_map(token.map, len(lines), kind)
            if stack and not stack[-1][1][0] <= span[0] < span[1] <= stack[-1][1][1]:
                raise ValueError("source map outside parent")
            active = bool(selected.intersection(range(*span)))
            owner = tuple(s[1][0] for s in stack if s[0].type == "list_item_open")
            if kind == "list_item_open" and active:
                if not set(range(*span)) <= selected:
                    raise ValueError("list item crosses Sources boundary")
                key = owner + (span[0],)
                if key in result.items:
                    raise ValueError("duplicate item source identity")
                result.items[key] = Item(key, span)
            if kind == "heading_open":
                if not re.fullmatch(r"h[1-6]", token.tag):
                    raise ValueError("invalid heading rank")
                if not stack:
                    if span[0] in parsed_heads:
                        raise ValueError("duplicate heading source identity")
                    parsed_heads[span[0]] = (int(token.tag[1:]), span[1], token.markup)
            if kind == "inline":
                if active and not set(range(*span)) <= selected:
                    raise ValueError("inline crosses Sources boundary")
                if token.content and not token.children:
                    raise ValueError("inline missing parsed children")
                inlines(token.children, span, owner, emit=active)
                if (stack and stack[-1][0].type == "heading_open"
                        and SOURCES_RE.match(inline_text(token.children, title=True))):
                    if (len(stack) != 1 or not legacy._SOURCES_HEADING.fullmatch(token.content)
                            or not lines[span[0]].startswith("#")):
                        result.findings.append(f"body line {span[0] + 1}: unsupported Sources heading")
                    if span[1] not in {start for start, _ in ranges}:
                        result.findings.append(f"body line {span[0] + 1}: unselected rendered Sources")
            elif kind == "html_block":
                result.findings.append(f"body line {span[0] + 1}: unclassified raw HTML")
            if token.nesting == 1:
                stack.append((token, span))
        if stack:
            raise ValueError("unclosed block token")
        for start, end in ranges:
            head = parsed_heads.get(start - 1)
            if head is None or head[1] != start or not head[2].startswith("#"):
                raise ValueError("Sources opener missing from rendered top-level headings")
            rendered_end = next((n for n, h in parsed_heads.items()
                                 if n >= start and h[0] <= head[0] and h[2].startswith("#")
                                 and lines[n].startswith("#")), len(lines))
            if rendered_end != end:
                raise ValueError("Sources end differs from rendered top-level ATX boundary")
        references = list(env.get("references", {}).values()) + env.get("duplicate_refs", [])
        for reference in references:
            source_map(reference.get("map"), len(lines), "reference definition")
    except Exception as exc:
        # Parser errors, unknown tokens and invalid maps never become absence.
        result.findings.append("extraction failed: " + str(exc))
    return result


def legacy_items(body):
    """Project the exact existing source_entries grouping with body positions."""
    heads = headings(body)
    items = {}
    for _, level, title, start in heads:
        if not SOURCES_RE.match(title):
            continue
        section = section_body(body, heads, start, level)
        lines, _, tokens = tokenize(section)
        entries = {}
        for token in tokens:
            if token.kind == "paragraph" and token.owner:
                entries.setdefault(token.owner, []).extend(lines[token.start:token.end])
        for owner, text in entries.items():
            key = tuple(start + n for n in owner)
            if key in items:
                raise ValueError("duplicate legacy item identity")
            items[key] = "\n".join(text)
        if ["\n".join(text) for text in entries.values()] != legacy.source_entries(section):
            raise ValueError("legacy item projection differs")
    return items


def compare(data, body, parser):
    """Return item/URL count deltas, item counts, and unbaselinable findings."""
    rendered = scan(body, parser)
    try:
        old_items = legacy_items(body)
    except Exception as exc:
        old_items = {}
        rendered.findings.append("legacy item projection failed: " + str(exc))
    old, new = Counter(), Counter()
    raw = legacy.raw_sources(body, headings(body))
    targets = {}
    for component, entry in data["components"].items():
        for source, url in entry["sources"].items():
            ref = (component, source)
            try:
                targets.setdefault(normalize_url(url), []).append(ref)
            except (ValueError, UnicodeError) as exc:
                rendered.findings.append(f"{component}:{source}: URL {url!r}: {exc}")
            for owner, text in old_items.items():
                old[owner, ref] = legacy.cites(text, url)
            outside = legacy.cites(raw, url) - sum(old[owner, ref] for owner in old_items)
            if outside < 0:
                rendered.findings.append(f"{component}:{source}: inconsistent legacy counts")
            old[(), ref] = outside
    for owner, hrefs in [(k, v.hrefs) for k, v in rendered.items.items()] + [((), rendered.outside)]:
        for href in hrefs:
            try:
                target = normalize_url(href)
            except (ValueError, UnicodeError):
                continue  # scan already recorded a finding; never a clean absence.
            for ref in targets.get(target, []):
                new[owner, ref] += 1
    changes = [(owner, ref, old[owner, ref], new[owner, ref])
               for owner, ref in sorted(old.keys() | new.keys()) if old[owner, ref] != new[owner, ref]]
    owners_differ = set(old_items) != set(rendered.items)
    return changes, owners_differ, (len(old_items), len(rendered.items)), rendered.findings


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--compare", action="store_true", required=True)
    cli.add_argument("--require-parser", action="store_true")
    cli.add_argument("--details", action="store_true", help="show every item/component count delta")
    cli.add_argument("--summary", action="store_true", help="print only the advisory totals")
    args = cli.parse_args(argv)
    try:
        try:
            parser = gate_parser(required=True)
        except ParserUnavailable as exc:
            if args.require_parser or os.environ.get("CI"):
                raise
            print(f"  SKIP  rendered Sources comparison: {exc} (advisory; legacy check unchanged)")
            return 0
        paths = legacy.paths()  # Validates nonempty enrollment and exact coverage.
        baseline = legacy.load_source_baseline()
        disagreements = differences = findings = 0
        for path in paths:
            text = path.read_text(encoding="utf-8")
            data, full_body = legacy.split(text)
            body = legacy.without_summary(full_body)
            prior = []
            try:
                legacy.require(legacy.updated(text, path.name, baseline) == text, "stale summary")
            except (ValueError, TypeError, KeyError) as exc:
                prior.append("authoritative check: " + str(exc))
            changes, owners_differ, counts, errors = compare(data, body, parser)
            errors = prior + errors
            if changes or owners_differ or errors:
                disagreements += 1
                if not args.summary:
                    print(f"  DIFF  {path.name}: {len(changes)} item/component-URL count differences; "
                          f"items {counts[0]} legacy/{counts[1]} rendered; {len(errors)} findings")
                    if args.details:
                        for owner, ref, before, after in changes:
                            where = "/".join(str(n + 1) for n in owner) or "outside items"
                            print(f"    body item {where} {':'.join(ref)}: {before} -> {after}")
                    for error in errors:
                        print(f"  FINDING  {path.name}: {error}")
            differences += len(changes)
            findings += len(errors)
        print(f"  ADVISORY  rendered Sources: {disagreements}/{len(paths)} guides disagree; "
              f"{differences} item/component-URL count differences; "
              f"{findings} findings; legacy check authoritative")
        return 0
    except Exception as exc:
        print(f"  FAIL  rendered Sources comparison: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
