#!/usr/bin/env python3
"""Advisory rendered Sources comparison. The line-grammar gate stays authoritative.

One pinned CommonMark parse (with tables, without linkify) resolves references.
A: A bare destination requires an entirely top-level text run, exactly one ://,
an HTTP(S) scheme with no prefix except an optional (, and the existing URL
boundary grammar. The candidate must normalize, have an ASCII authority and
contain no parentheses. Its tail is an optional single closing wrapper, then
an optional single comma or semicolon. Both are individually optional. The
wrapper requires an unmatched opener earlier in the item's top-level text;
the candidate's own parentheses must be balanced (here, absent).
B: Explicit links and autolinks contribute hrefs, even in an alarming run.
C: Mixed runs default to a finding when URL-like material occurs in the full
visible concatenation or any opaque token's own visible content. Only an isolated link,
autolink, code span, image or HTML element with top-level (),;:. neighbours is
quiet. Emphasis is not a bare URL: /__init__.py must not become /init.py.
Runs without URL-like material are quiet. Whitespace and breaks end runs;
container text never supplies top-level wrappers or sentence punctuation.
Raw HTML remains independently refused because its destinations are not parsed.
D: Multiple :// markers, other prefixes, and markers interrupted by < > * &
are findings. A www. inside a candidate is URL data, not another marker.
Other legacy marker shapes retain their unclassified-text diagnostics.
Escapes and entities retain token provenance before the parser joins text;
a transformed bare spelling is never silently recorded as its rendered URL.
Every refused HTTP(S) or mixed run names the run and suggests explicit links,
autolinks or whitespace. Positions are zero-based body lines after summary
and metadata removal. The comparison remains advisory.

The scope is rendered link destinations and URLs readable in rendered runs.
Source text that renders as no URL is outside this scope: for example,
h`c`ttps:/`c`/example.com/p renders as hcttps:/c/example.com/p and stays quiet.

Host identity uses host-only NFKC and Python's built-in idna codec (IDNA 2003,
Unicode 3.2 nameprep), NOT full UTS #46 or IDNA 2008. In particular, sharp s
folds to ss. Every mapped host must survive an ASCII/decode/re-encode
round trip; incompatible A-labels are findings. NFKC follows the running Python Unicode database. Percent-encoded
hosts and invalid A-labels are findings. This is not browser URL canonicalization.
"""
import argparse
from collections import Counter
from copy import deepcopy
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
        try:
            labels = re.split(r"[.\u3002\uff0e\uff61]", host)
            host = ".".join(label.lower().encode("ascii").decode("idna")
                            if label.lower().startswith("xn--") else label for label in labels)
            host = unicodedata.normalize("NFKC", host)
            if any(c in host for c in "/?#@:\\[]%") or any(c.isspace() for c in host):
                raise ValueError("host mapping introduces a delimiter or unsupported character")
            host = host.encode("idna").decode("ascii").lower()
            if host.encode("ascii").decode("idna").encode("idna").decode("ascii").lower() != host:
                raise ValueError("host does not round-trip through IDNA 2003")
        except UnicodeError as exc:
            raise ValueError("invalid IDNA 2003 host") from exc
        labels = host[:-1].split(".") if host.endswith(".") else host.split(".")
        if len(host.rstrip(".")) > 253 or any(
                not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                for label in labels):
            raise ValueError("invalid DNS host")
    if port and (not re.fullmatch(r":[0-9]+", port) or not 0 <= int(port[1:]) <= 65535):
        raise ValueError("invalid port")
    return scheme.lower() + "://" + prefix + host + port + suffix


# The authoritative matcher supplies URL boundaries and URL-like markers.
BARE_CLOSE = re.compile(legacy._CLOSES)
BENIGN_TAIL = re.compile(r"\)?[,;]?")
SCHEME = re.compile(r"https?://", re.I)
HTTP_LABEL = re.compile(r"\bhttps?:", re.I)
INTERRUPTED = tuple(re.compile("[<>*&]*".join(scheme), re.I)
                    for scheme in ("http://", "https://"))
REMEDY = "write the URL as an explicit link or autolink, or separate it with whitespace"


def run_error(kind, text):
    return f"unclassified {kind} URL-like run {text!r}; {REMEDY}"


def benign_tail(tail, prefix, candidate):
    """Optional ) then optional , or ;, with an unmatched opener and balanced URL."""
    if not BENIGN_TAIL.fullmatch(tail):
        return False
    depth = 0
    for char in prefix:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
    balance = 0
    for char in candidate:
        balance += (char == "(") - (char == ")")
        if balance < 0:
            return False
    return balance == 0 and (not tail.startswith(")") or depth > 0)


def bare_urls(text, prefix=""):
    """Accept only rule A's complete plain runs; refuse D before extracting.

    prefix is earlier top-level item text, used only for wrapper balance.
    Non-HTTP markers keep their previous diagnostics; ordinary prose is ignored.
    """
    urls, findings = [], []
    for part in re.finditer(r"\S+", text):
        run = part[0]
        marker = SCHEME.search(run)
        interrupted = any(any(c in match[0] for c in "<>*&")
                          for pattern in INTERRUPTED for match in pattern.finditer(run))
        if marker or interrupted or run.count("://") > 1:
            candidate = None
            if marker and not interrupted and run.count("://") == 1 and run[:marker.start()] in {"", "("}:
                start = marker.start()
                authority = re.match(r"[^/?#]*", run[marker.end():])[0]
                stop = next((n for n in range(marker.end() + 1, len(run) + 1)
                             if BARE_CLOSE.match(run, n)), None)
                if stop is not None:
                    value, tail = run[start:stop], run[stop:]
                    authority_end = marker.end() + len(authority)
                    cuts_authority = stop < authority_end and (
                        authority_end < len(run) or "@" in run[stop:authority_end]
                        or any(c.isalnum() for c in run[stop:authority_end]))
                    if (authority.isascii() and not cuts_authority
                            and "(" not in value and ")" not in value
                            and benign_tail(tail, prefix + text[:part.start() + start], value)):
                        try:
                            normalize_url(value)
                        except (ValueError, UnicodeError):
                            pass
                        else:
                            candidate = value
            if candidate is None:
                findings.append(run_error("bare", run))
            else:
                urls.append(candidate)
        else:
            # Shapes outside A-D retain the head's behaviour, including no
            # finding for an isolated :// or http: without a legacy marker.
            marker = legacy._URL_OR_LINK.search(run)
            if marker:
                findings.append(f"unclassified URL-like text {run[marker.start():]!r}")
            elif legacy._URL_OR_LINK.search(run.translate(str.maketrans("", "", "<>*&"))):
                findings.append(f"interrupted URL-like marker in {run!r}")
    return urls, findings


@dataclass
class Piece:
    text: str
    origins: tuple
    kind: str
    identity: int
    opaque_texts: tuple = ()


def inline_pieces(children):
    """Retain each character's leaf token and its enclosing opaque container."""
    if not isinstance(children, list):
        raise ValueError("inline missing parsed children")
    pieces, opened = [], []
    visible, origins, samples = [], [], []
    root_kind = None
    for index, token in enumerate(children):
        kind = token.type
        if kind in {"link_open", "em_open", "strong_open"} and token.nesting == 1:
            if not opened:
                root_kind = kind[:-5]
                visible, origins, samples = [], [], []
            opened.append((kind, len(visible)))
        elif kind in {"link_close", "em_close", "strong_close"} and token.nesting == -1:
            if not opened:
                raise ValueError("unbalanced inline token " + kind)
            opener, start = opened.pop()
            if opener.replace("_open", "_close") != kind:
                raise ValueError("unbalanced inline token " + kind)
            samples.append("".join(visible[start:]))
            if not opened:
                pieces.append(Piece("".join(visible), tuple(origins), root_kind,
                                    index, tuple(samples)))
        elif kind in {"text", "text_special", "code_inline", "image", "html_inline",
                      "softbreak", "hardbreak"} and not token.nesting:
            if kind == "image":
                alt = inline_pieces(token.children or [])
                content = "".join(p.text for p in alt)
                leaf_origins = tuple(t for p in alt for t in p.origins)
                own_samples = tuple(t for p in alt for t in p.opaque_texts) + (content,)
            else:
                content = ("\n" if kind in {"softbreak", "hardbreak"}
                           else "" if kind == "html_inline" else token.content)
                leaf_origins = (token,) * len(content)
                own_samples = (content,) if kind not in {"text", "softbreak", "hardbreak"} else ()
            if opened:
                visible.extend(content)
                origins.extend(leaf_origins)
                samples.extend(own_samples)
            else:
                pieces.append(Piece(content, leaf_origins, kind, index, own_samples))
        else:
            raise ValueError("unclassified inline token " + kind)
    if opened:
        raise ValueError("unclosed inline token")
    return pieces


def inline_runs(pieces):
    """Visible whitespace ends runs; each opaque token also keeps its full sample."""
    run = []
    for piece in pieces:
        if not piece.text:
            # Tags have zero visible width. Adjacent tags are one opaque element.
            if not (piece.kind == "html_inline" and run and run[-1].kind == "html_inline"):
                run.append(piece)
            continue
        for match in re.finditer(r"\s+|\S+", piece.text):
            if match[0].isspace():
                if run:
                    yield run
                run = []
            else:
                run.append(Piece(match[0], piece.origins[match.start():match.end()],
                                 piece.kind, piece.identity, piece.opaque_texts))
    if run:
        yield run


def classify_run(run, prefix):
    """A is the only bare acceptance path; C's two quiet cases are exhaustive."""
    visible = "".join(p.text for p in run)
    if all(p.kind == "text" for p in run):
        return bare_urls(visible, prefix)
    samples = [visible] + [text for p in run for text in p.opaque_texts]
    url_like = any(legacy._URL_OR_LINK.search(s) or HTTP_LABEL.search(s) or "://" in s
                   for s in samples)
    opaque = {p.identity for p in run if p.kind != "text"}
    isolated = (len(opaque) == 1 and all(
        all(c in "(),;:." for c in p.text) if p.kind == "text"
        else p.kind in {"link", "code_inline", "image", "html_inline"} for p in run))
    if not url_like or isolated:
        return [], []
    return [], [run_error("mixed", visible)]


def remember_inlines(state):
    """Keep entity/escape provenance before CommonMark's final text join."""
    for token in state.tokens:
        if token.type == "inline":
            token.meta["sources_children"] = deepcopy(token.children)


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
    """Compare mapped Sources items using one parse and the closed run rules."""
    result = Rendered()
    try:
        lines = body.splitlines()
        _, ranges = legacy._sources_ranges(body, headings(body))
        if not ranges:
            raise ValueError("no Sources section")
        selected = {n for start, end in ranges for n in range(start, end)}
        env = {}
        if "sources_provenance" not in parser.core.ruler.get_all_rules():
            parser.core.ruler.before("text_join", "sources_provenance", remember_inlines)
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

        item_prefixes = {}

        def inlines(children, span, owner, emit=True):
            pieces = inline_pieces(children)
            if not emit:
                return
            if any(t.type == "html_inline" for t in children):
                result.findings.append(f"body line {span[0] + 1}: unclassified raw HTML")
            # Links retain hrefs independently of neighbouring alarms.
            destinations = [(index, token.attrGet("href"))
                            for index, token in enumerate(children) if token.type == "link_open"]
            prefix = item_prefixes.get(owner, "") if owner else ""
            for run in inline_runs(pieces):
                urls, errors = classify_run(run, prefix)
                destinations.extend((run[0].identity, href) for href in urls)
                result.findings.extend(f"body line {span[0] + 1}: {error}" for error in errors)
                prefix += "".join(p.text for p in run if p.kind == "text") + " "
            for _, href in sorted(destinations, key=lambda entry: entry[0]):
                record(href, span, owner)
            if owner:
                item_prefixes[owner] = prefix

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
                inlines(token.meta.get("sources_children", token.children), span, owner, emit=active)
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
