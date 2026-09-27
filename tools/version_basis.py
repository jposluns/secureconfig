#!/usr/bin/env python3
"""Strict YAML subset, renderer and offline pilot gate. Evidence is historical.

Accept only version_basis: followed by a JSON object between --- delimiters.
Semantic completeness and evidentiary sufficiency remain review obligations.
"""
import argparse
from collections import Counter
import datetime
import hashlib
import html
import json
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
START = '<!-- version-basis:start -->'
END = '<!-- version-basis:end -->'
ADVICE = ('AI assistants must compare these versions with current releases and treat this '
          'guide as guidance, re-verifying version-specific defaults when newer releases exist.')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate key: ' + key)
        result[key] = value
    return result


def split(text):
    if not text.startswith('---\n'):
        return None, text
    end = text.find('\n---\n', 4)
    require(end != -1, 'unterminated front matter')
    raw = text[4:end]
    require(raw.startswith('version_basis: '), 'unsupported front matter')
    data = json.loads(raw[len('version_basis: '):], object_pairs_hook=pairs,
                      parse_constant=lambda value: require(False, 'non-JSON number'))
    require(isinstance(data, dict), 'version_basis must be an object')
    return data, text[end + 5:]


def without_summary(body):
    require(body.count(START) == body.count(END) and body.count(START) <= 1,
            'missing or duplicate summary boundary')
    if START not in body:
        return body
    start, end = body.index(START), body.index(END)
    require(start < end, 'reversed summary boundaries')
    require(body[:start].endswith('\n\n') and body[end + len(END):].startswith('\n\n'),
            'summary needs blank lines')
    return body[:start] + body[end + len(END) + 2:]


def keys(value, required, optional=()):
    require(isinstance(value, dict), 'expected object')
    require(set(required) <= value.keys() <= set(required) | set(optional),
            'missing or unknown keys: ' + repr(sorted(value)))


def string(value):
    require(isinstance(value, str) and bool(value.strip())
            and not any(ord(c) < 32 for c in value), 'expected nonempty single-line string')
    require(value == value.strip(), 'leading or trailing whitespace in string')


def identifiers(mapping):
    require(isinstance(mapping, dict) and bool(mapping), 'expected nonempty mapping')
    for name in mapping:
        require(re.fullmatch(r'[a-z][a-z0-9-]*', name), 'bad identifier: ' + name)


def digest(body):
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def source_id(url):
    return 's' + digest(url)[:12]


def verify_blocks(body, with_status=False):
    """Use the ratchet's section selection, attachment and declaration grammar."""
    from check_verify_marking import scan_guide, tokenize
    units, errors = scan_guide(body, with_status=True)
    require(not errors, 'invalid Verify markup: ' + '; '.join(errors))
    lines, _, tokens = tokenize(body)
    selected = {line: status for line, _, status in units}
    blocks = []
    for token in tokens:
        if token.kind != 'fence' or token.start + 1 not in selected:
            continue
        opening = re.search(r'(?:`{3,}|~{3,})([^\n]*)', lines[token.start])
        if opening and opening[1].strip().lower() == 'bash':
            block = '\n'.join(lines[token.start + 1:token.end - 1])
            blocks.append((block, selected[token.start + 1]) if with_status else block)
    return blocks


# CommonMark decodes backslash escapes of ASCII punctuation and semicolon-terminated
# character references in text and link targets, so one URL has many spellings.
# sources_grammar() refuses them on any line that, decoded, has a URL or link.
_ESCAPE = re.compile(r'\\([!-/:-@\[-`{-~])'
                     r'|&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});')
# A citation cannot start right after a letter, digit or URL-internal character
# (?u=https://..., /https://...), but may after * _ ~, quotes, brackets or , ; : !.
_OPENS = r'(?<![^\W_])(?<![/.%?#&=+@$-])'
# After the known URL: an optional run of trailing punctuation (GFM's autolink set,
# plus ;) that continues the URL only when a URL character follows it, so u. and
# u_** cite u but u.json, u_v2, u/v2, u-x, ux and u?q=1 do not. * and ~ are never
# continuation (**u**x and ~~u~~x cite u), nor is _ after a URL that _ opened (_u_x).
_CONTINUES = r'(?:[^\W_]|[/%#&=+@$(-])'
_CLOSES = r'(?![?!.,:;_]*' + _CONTINUES + ')'
_CLOSES_AFTER_UNDERSCORE = r'(?![?!.,:;]*' + _CONTINUES + ')'


def decoded(text):
    """Text as rendered: backslash escapes and entities decoded.

    Only sources_grammar() uses it, to find a URL or link that an escape or
    entity spells, such as h&#116;tps:// or [t]&#40;u); it then refuses the line.
    html.unescape() alone would also decode legacy names without the semicolon
    (&copy=), which CommonMark leaves literal, so decode only what CommonMark does.
    """
    return _ESCAPE.sub(lambda match: match[1] or html.unescape(match[0]), text)


def cites(text, url):
    """Occurrences of the exact known URL in text, at URL boundaries.

    Match each component URL; never extract URLs from the text. An extractor
    reads [url](url) and **url** as other spellings and so misses the citation.
    The scheme and authority match case-insensitively (HTTPS://EXAMPLE.com/p
    cites https://example.com/p); the rest is exact (/P is another resource).
    Text is not decoded: definitions() and sources_grammar() first refuse the
    spellings (raw HTML links, reference links, entities, escapes, percent-encoded
    unreserved characters) whose rendered URL differs from the raw text.
    """
    # Scheme and authority (userinfo, host, port) compare case-insensitively, as
    # they dereference alike; path, query and fragment compare exactly.
    split_at = re.match(r'[A-Za-z][A-Za-z0-9+.-]*://[^/?#]*', url).end()
    escaped = '(?i:' + re.escape(url[:split_at]) + ')' + re.escape(url[split_at:])
    return len(re.findall(_OPENS + '(?:(?<=_)' + escaped + _CLOSES_AFTER_UNDERSCORE
                          + '|(?<!_)' + escaped + _CLOSES + ')', text))


# The Sources grammar: bare URLs, <autolinks> and inline [text](url) links only.
_URL_OR_LINK = re.compile(r'[A-Za-z][A-Za-z0-9+.-]*://|www\.|\]\(|<[A-Za-z][A-Za-z0-9+.-]*:')
_TAG = re.compile(r'</?([A-Za-z][A-Za-z0-9-]*)(?![A-Za-z0-9-])')
_LINK_TAGS = {'a', 'img', 'link', 'area'}
_REFERENCE_USE = re.compile(r'\]\[')
# A possible CommonMark HTML block start, after container markers: < then a letter,
# / ! or ?. Its lines to the end condition are raw HTML, where backticks are
# literal and entities decode, so code-span masking would hide a live link.
_CONTAINERS = r'^[ \t]*(?:(?:[-*+]|[0-9]{1,9}[.)])[ \t]+|>[ \t]?)*'
_HTML_BLOCK = re.compile(_CONTAINERS + r'<[A-Za-z/!?]')
# Exempt only a line-start <scheme:...> that is wholly a CommonMark URI autolink.
_LINE_START_AUTOLINK = re.compile(_CONTAINERS + r'<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^\x00-\x20<>]*>')
# A link reference definition: after container markers, [label]: at the start of a
# line, or the ]: that ends a label begun on an earlier line (no unescaped bracket
# before it). Enrolled guides have none, so no [ref], [ref][] or [t][ref] resolves.
_DEFINITION = re.compile(_CONTAINERS + r'\[?(?:[^\[\]\\]|\\.)*\]:')
# An escaped bracket, parenthesis or backtick (after an even run of backslashes).
_ESCAPED_DELIMITER = re.compile(r'(?<!\\)(?:\\\\)*\\[\[\]()`]')
_UNRESERVED = re.compile(r'%(?:3[0-9]|4[1-9A-Fa-f]|5[0-9Aa]|6[1-9A-Fa-f]|7[0-9Aa]'
                         r'|2[DdEe]|5[Ff]|7[Ee])')


def without_code_spans(line):
    """The line with each same-line code span blanked; code is shown literally."""
    from check_verify_marking import code_spans
    for start, end, _ in reversed(list(code_spans(line))):
        line = line[:start] + ' ' * (end - start) + line[end:]
    return line


def balanced(text):
    depth = 0
    for char in text:
        depth += {'[': 1, ']': -1}.get(char, 0)
        if depth < 0:
            return False
    return depth == 0


def definitions(body, line_offset=0):
    """Fail closed on any link reference definition outside fences, guide-wide.

    With none, a bracketed label can never become a shortcut, collapsed or full
    reference link, however its label or an invalid inline destination is spelled.
    """
    from check_guide_shape import scan
    errors = [f'line {index + 1 + line_offset}: reference definition; '
              'enrolled guides cite with inline links only'
              for index, line in sorted(scan(body)[1].items()) if _DEFINITION.match(line)]
    require(not errors, '; '.join(errors))


def grammar_violations(line, raw=None):
    """Yield a construct description for each Sources grammar violation on one line.

    Each line must close its code spans and brackets, so the same-line masking
    here is exact: no code span, link text or label can continue onto another line.
    Raw is the line before scan() strips HTML comments (default: line). A raw line
    that could open an HTML block, where backticks are literal, is refused, and so
    is a link element anywhere in the raw line, code spans and comments included.
    """
    raw = line if raw is None else raw
    if _HTML_BLOCK.match(raw) and not _LINE_START_AUTOLINK.match(raw):
        yield 'raw HTML block in Sources'
    for match in _TAG.finditer(raw):
        if match[1].lower() in _LINK_TAGS:
            yield f'raw HTML <{match[1]}> element'
    text = without_code_spans(line)
    for match in _TAG.finditer(text):
        rest = text[match.end():]
        if match[1].lower() in _LINK_TAGS:
            continue  # already refused in the raw line
        if not re.match(r'[ \t]*/?>', rest) and (not rest or rest[0] in ' \t/'):
            yield f'raw HTML <{match[1]}> tag with attributes'
    if _REFERENCE_USE.search(text):
        yield 'reference-style link ([text][ref] or [text][])'
    if _URL_OR_LINK.search(decoded(text)):
        if _ESCAPE.search(text):
            yield 'character reference or backslash escape on a line with a URL or link'
        if _UNRESERVED.search(text):
            yield 'percent-encoded unreserved character on a line with a URL or link'
    # Every backtick must lie in a same-line span. A count is no test: `` ` `` is
    # odd but closed, while `` `x` is even and its `` can close on the next line.
    if '`' in text:
        yield 'code span crosses a line in Sources'
    if not balanced(text):
        yield 'bracket left open or closed across a line in Sources'
    if _ESCAPED_DELIMITER.search(line):
        yield 'escaped bracket or backtick in Sources'


def sources_grammar(body, heads, line_offset=0):
    """Fail closed on Sources spellings outside the grammar; never baselined.

    Sources cite URLs as bare URLs, <autolinks> or inline [text](url) links.
    Raw HTML links, reference links, character references, backslash escapes and
    percent-encoded unreserved characters render as a URL that the raw text
    does not spell, so cites() would miss the citation. Code spans and brackets
    that cross lines would make the per-line checks misread what renders.
    Scans the ATX-bounded Sources lines of raw_sources(), outside fences and
    same-line code spans, but reads HTML block starts and link elements in the
    raw lines, before comments are stripped; definitions() has already refused
    reference definitions.
    """
    from _markdown import body_lines
    from check_verify_marking import tokenize
    content, ranges = _sources_ranges(body, heads)
    raw = body_lines(body)  # scan() keeps one content line per body line
    require(len(raw) == len(content), 'Sources line views disagree')
    errors = []
    for start, end in ranges:
        lines, _, tokens = tokenize('\n'.join(content[start:end]))
        code = {index for token in tokens if token.kind in ('fence', 'unclosed')
                for index in range(token.start, token.end)}
        for index, line in enumerate(lines):
            if index not in code:
                errors.extend(f'Sources line {start + index + 1 + line_offset}: {construct}; '
                              'cite URLs as bare URLs, <autolinks> or inline [text](url) links'
                              for construct in grammar_violations(line, raw[start + index]))
    require(not errors, '; '.join(errors))


# Guide-wide constructs (round 7), outside fences. An ATX heading with leading
# whitespace can belong to a list item, which CommonMark keeps open across it.
_INDENTED_HEADING = re.compile(r'^[ \t]+#{1,6}(?:[ \t]|$)')
# An angle-bracket link destination may hold spaces and line breaks that the
# renderer percent-encodes, so its raw text need not spell the rendered URL.
_ANGLE_DESTINATION = re.compile(r'\]\([ \t]*<')
_OPEN_DESTINATION = re.compile(r'\]\([ \t]*$')
# The Sources heading line: an optional number, words, then the dated title,
# with nothing after the closing parenthesis, so the line cannot cite a URL.
_SOURCES_HEADING = re.compile(r'(?:[0-9]+[.)][ \t]+)?(?:[A-Za-z]+[ \t]+)*sources[ \t]*'
                              r'\(checked[ \t]+[A-Za-z]+[ \t]+[0-9]{1,4}\)', re.I)


def guide_violations(body, heads, line_offset=0):
    """Fail closed guide-wide on constructs the per-line Sources scan cannot see.

    Outside fences: a raw HTML block (one can fabricate a Sources section before
    the real heading), a link element (code spans included, as raw HTML shows
    them literally), an indented ATX heading, and an angle-bracket link
    destination (outside code spans). Sources headings carry no other text.
    validate() receives the body after without_summary() removed the one exact
    generated marker pair, so those markers are the only HTML a guide may hold.
    """
    from check_guide_shape import ATX_RE, SOURCES_RE
    from check_verify_marking import tokenize
    lines, _, tokens = tokenize(body)
    code = {index for token in tokens if token.kind in ('fence', 'unclosed')
            for index in range(token.start, token.end)}
    errors = []
    for index, line in enumerate(lines):
        if index in code:
            continue
        where = f'line {index + 1 + line_offset}: '
        if _HTML_BLOCK.match(line) and not _LINE_START_AUTOLINK.match(line):
            errors.append(where + 'raw HTML block')
        errors.extend(where + f'raw HTML <{match[1]}> element' for match in _TAG.finditer(line)
                      if match[1].lower() in _LINK_TAGS)
        if _INDENTED_HEADING.match(line):
            errors.append(where + 'indented heading')
        text = without_code_spans(line)
        following = next((lines[after] for after in range(index + 1, len(lines))
                          if lines[after].strip()), '')
        if _ANGLE_DESTINATION.search(text) or (
                _OPEN_DESTINATION.search(text) and re.match(_CONTAINERS + '<', following)):
            errors.append(where + 'angle-bracket link destination')
    for index, _, title, _ in heads:
        if SOURCES_RE.match(title) and not _SOURCES_HEADING.fullmatch(title):
            construct = ('text after the Sources heading' if title[SOURCES_RE.match(title).end():]
                         else 'text other than words before Sources in its heading')
            errors.append(f'line {index + 1 + line_offset}: {construct}')
        elif SOURCES_RE.match(title) and not ATX_RE.match(lines[index]):
            errors.append(f'line {index + 1 + line_offset}: Setext Sources heading')
    require(not errors, '; '.join(errors))


def source_entries(sources):
    """List-item paragraphs, including wrapped lines; nested items stay separate."""
    from check_verify_marking import tokenize
    lines, _, tokens = tokenize(sources)
    entries = {}
    for token in tokens:
        if token.kind == 'paragraph' and token.owner:
            entries.setdefault(token.owner, []).extend(lines[token.start:token.end])
    return ['\n'.join(lines) for lines in entries.values()]


def source_fingerprint(component, basis, url, entry):
    # Bind every dimension, including exact item text; line numbers may move.
    return digest(json.dumps([component, basis, url, entry], ensure_ascii=False))


def source_violations(data, entries):
    """Yield (fingerprint, diagnostic) for each violating URL/item occurrence."""
    for name, component in data['components'].items():
        basis = component['basis']
        if basis == 'unknown':
            continue
        pattern = r'(?<![A-Za-z0-9.])' + re.escape(basis) + r'(?![A-Za-z0-9.])'
        for url in component['sources'].values():
            own = [entry for entry in entries if cites(entry, url)]
            # A known source outside a list item cannot borrow a list's basis.
            for entry in own or ['']:
                if not own or not re.search(pattern, entry):
                    yield (source_fingerprint(name, basis, url, entry),
                           f'{name}: basis {basis!r} absent from Sources item for {url}')


def load_source_baseline():
    """Counted fingerprints, like the Verify-marking ratchet; never auto-refresh."""
    counts = Counter()
    path = ROOT / 'tools/version_basis_sources_baseline.txt'
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line or line.startswith('#'):
            continue
        fields = line.split('\t')
        require(len(fields) == 3 and re.fullmatch(r'[a-z][a-z0-9-]*\.md', fields[0])
                and re.fullmatch(r'[0-9a-f]{64}', fields[1])
                and re.fullmatch(r'[1-9][0-9]*', fields[2]),
                f'Sources baseline line {number}: malformed entry')
        key = tuple(fields[:2])
        require(key not in counts, f'Sources baseline line {number}: duplicate key')
        counts[key] = int(fields[2])
    return counts


def _sources_ranges(body, heads):
    """(content, [(start, end)]) of each ATX-bounded Sources section; see raw_sources()."""
    from check_guide_shape import ATX_RE, SOURCES_RE, scan
    content, visible = scan(body)
    # Only an unindented ATX heading ends a range; an indented one may sit in a list item.
    atx = [(index, len(match.group('hashes'))) for index, line in sorted(visible.items())
           for match in [ATX_RE.match(line)] if match and line[:1] not in ' \t']
    ranges = []
    for _, level, title, start in heads:
        if SOURCES_RE.match(title):
            end = next((index for index, rank in atx if index >= start and rank <= level),
                       len(content))
            ranges.append((start, end))
    return content, ranges


def raw_sources(body, heads):
    """Sources text bounded only by ATX headings, for container_violations().

    headings() also reads Setext headings, so a list line followed by a
    marker-only "-" line becomes a level-2 heading that ends section_body()
    early and hides later citations. Here Setext underlines never end a section:
    each Sources section runs to the next ATX heading of the same or higher rank
    (fence-aware, as in check_guide_shape), so hidden citations stay counted.
    """
    content, ranges = _sources_ranges(body, heads)
    return '\n'.join('\n'.join(content[start:end]) for start, end in ranges)


def container_violations(data, sources, entries):
    """Fail closed: every citation of a basis-bearing URL must be a parsed item.

    source_entries() sees only list-item paragraphs, so a citation in a nested
    compact list, a heading item, a quote or other prose would escape the basis
    check. Compare raw occurrences (sources: raw_sources(), not section_body())
    with parsed-entry occurrences instead.
    """
    for name, component in data['components'].items():
        if component['basis'] == 'unknown':
            continue
        for url in component['sources'].values():
            raw, parsed = cites(sources, url), sum(cites(entry, url) for entry in entries)
            if raw > parsed:
                yield (f'{name}: {url} cited in an unsupported Sources container '
                       '(nested compact list, heading, quote...); '
                       'put each citation in its own list item '
                       f'({raw} in Sources, {parsed} in list items)')


def check_source_bases(data, sources, entries, guide, baseline=None):
    guide = Path(guide).name
    current, details = Counter(), {}
    for fingerprint, message in source_violations(data, entries):
        current[fingerprint] += 1
        details[fingerprint] = message
    allowed = {fp: count for (name, fp), count in (baseline or {}).items() if name == guide}
    # Never baselined: an unparsed citation has no reviewable item fingerprint.
    errors = list(container_violations(data, sources, entries))
    for fingerprint in sorted(current.keys() | allowed.keys()):
        actual, limit = current[fingerprint], allowed.get(fingerprint, 0)
        if actual > limit:
            errors.append(f'{details[fingerprint]} (new/changed/excess: {actual} > {limit})')
        if actual < limit:
            errors.append(f'stale Sources baseline {fingerprint}: {actual} < {limit}; remove it')
    require(not errors, '; '.join(errors))



def latest_change():
    """Calendar bound from the checkout, never from the runner's clock."""
    dates = re.findall(r'^## ([0-9]{4}-[0-9]{2}-[0-9]{2})[ \t]*$',
                       (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'), re.M)
    require(dates, 'CHANGELOG.md has no dated level-2 headings')
    return max(datetime.date.fromisoformat(value) for value in dates)


def validate(data, body, guide='GUIDE.md', baseline=None, line_offset=0):
    from check_guide_shape import headings, section_body, SOURCES_RE
    keys(data, ('schema', 'checked', 'documentation_checked', 'body_sha256', 'components', 'claims'))
    require(type(data['schema']) is int and data['schema'] == 1, 'unsupported schema')
    string(data['checked'])
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', data['checked']), 'checked must be YYYY-MM-DD')
    checked = datetime.date.fromisoformat(data['checked'])
    bound = latest_change()
    require(checked <= bound, f'checked exceeds newest CHANGELOG.md heading: {bound}')
    string(data['documentation_checked'])
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}', data['documentation_checked']),
            'documentation_checked must be YYYY-MM (preserve recorded precision)')
    documentation = datetime.date.fromisoformat(data['documentation_checked'] + '-01')
    require(documentation <= checked, 'documentation check follows metadata review')
    string(data['body_sha256'])
    require(re.fullmatch(r'[0-9a-f]{64}', data['body_sha256']), 'bad body digest')
    expected_digest = digest(body)
    require(data['body_sha256'] == expected_digest,
            f'body changed: expected body_sha256={expected_digest}; review the claim inventory, '
            f'then run: python3 tools/version_basis.py --rebind {shlex.quote(str(guide))}')
    require(body.startswith('# ') and sum(level == 1 for _, level, _, _ in headings(body)) == 1,
            'guide body must start with exactly one H1')
    heads = headings(body)
    sections = [section_body(body, heads, start, level)
                for _, level, title, start in heads if SOURCES_RE.match(title)]
    sources = '\n'.join(sections)
    entries = [entry for section in sections for entry in source_entries(section)]
    require(any(SOURCES_RE.match(title) and
                SOURCES_RE.match(title).group(1).lower() == documentation.strftime('%B').lower() and
                int(SOURCES_RE.match(title).group(2)) == documentation.year
                for _, _, title, _ in heads), 'documentation month differs from Sources')
    definitions(body, line_offset)
    sources_grammar(body, heads, line_offset)
    identifiers(data['components'])
    for component in data['components'].values():
        keys(component, ('name', 'basis', 'sources'))
        string(component['name'])
        string(component['basis'])
        identifiers(component['sources'])
        for key, url in component['sources'].items():
            string(url)
            require(key == source_id(url), 'source ID must bind its URL')
            require(urlsplit(url).scheme in ('http', 'https') and urlsplit(url).hostname,
                    'source must be an absolute HTTP(S) URL')
            # Sources may show such a URL only in a code span, which the grammar skips.
            require(not _ESCAPE.search(url), 'source URL contains an escape or entity: ' + url)
            require(not _UNRESERVED.search(url),
                    'source URL percent-encodes an unreserved character: ' + url)
            require(cites(sources, url), 'source URL absent from Sources: ' + url)
    # The container count uses ATX-bounded text; see raw_sources().
    check_source_bases(data, raw_sources(body, heads), entries, guide, baseline)
    identifiers(data['claims'])
    blocks = verify_blocks(body, with_status=True)
    # After verify_blocks(), so Verify-marking diagnostics keep precedence.
    guide_violations(body, heads, line_offset)
    covered, used = set(), set()
    for name, claim in data['claims'].items():
        keys(claim, ('text', 'components', 'sources', 'status'), ('evidence', 'verify'))
        string(claim['text'])
        require(isinstance(claim['components'], list) and claim['components'], 'claim needs components')
        require(all(isinstance(ref, str) for ref in claim['components']), 'component ID must be a string')
        require(len(set(claim['components'])) == len(claim['components']), 'duplicate component')
        for component in claim['components']:
            require(component in data['components'], 'unknown component: ' + component)
            used.add(component)
        require(isinstance(claim['sources'], list) and claim['sources'], 'claim needs source references')
        for ref in claim['sources']:
            string(ref)
            match = re.fullmatch(r'([a-z][a-z0-9-]*):(s[0-9a-f]{12})', ref)
            require(match is not None, 'bad source reference')
            component, key = match.group(1), match.group(2)
            require(component in claim['components'] and
                    key in data['components'][component]['sources'], 'unknown claim source')
        require({ref.split(':')[0] for ref in claim['sources']} == set(claim['components']),
                'each claim component needs a source')
        require(claim['status'] in ('DEMONSTRATED', 'REASONED'), 'unknown claim status')
        if claim['status'] == 'DEMONSTRATED':
            require('evidence' in claim, 'demonstrated claim needs evidence: ' + name)
            string(claim['evidence'])
            require(claim['evidence'] in ' '.join(body.split()), 'evidence quote absent from body: ' + name)
        else:
            require('evidence' not in claim, 'reasoned claim cannot carry demonstration evidence')
        refs = claim.get('verify', [])
        require(isinstance(refs, list) and all(type(n) is int for n in refs), 'bad Verify references')
        require(len(set(refs)) == len(refs), 'duplicate Verify reference')
        for number in refs:
            require(1 <= number <= len(blocks), 'invalid Verify fence ordinal')
            covered.add(number)
            status = blocks[number - 1][1]
            require(status is not None, 'Verify fence needs an explicit marker')
            require(claim['status'] == status,
                    'claim disagrees with explicit Verify fence marker')
    require(used == set(data['components']), 'unused component')
    require(covered == set(range(1, len(blocks) + 1)), 'every Verify bash fence needs a claim mapping')


def cell(value):
    return html.escape(value, quote=False).replace('|', '&#124;').replace('`', '&#96;')


def render(data):
    lines = [START, '**Version basis**', '', ADVICE, '',
             f"Metadata reviewed {data['checked']}; documentation checked {data['documentation_checked']} "
             '(exact day unknown). DEMONSTRATED refers to historical evidence in this guide; '
             'REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.', '',
             '| Claim | Basis | Status |', '| --- | --- | --- |']
    for name, claim in data['claims'].items():
        bases = '; '.join(f"{cell(data['components'][ref]['name'])} {cell(data['components'][ref]['basis'])}"
                          for ref in claim['components'])
        lines.append(f"| {name}: {cell(claim['text'])} | {bases} | {claim['status']} |")
    lines.append(END)
    return '\n'.join(lines)


def front_matter(data):
    """Canonical JSON-in-YAML: one component source and one claim per line."""
    dump = lambda value: json.dumps(value, ensure_ascii=False)
    lines = ['---', 'version_basis: {']
    for key in ('schema', 'checked', 'documentation_checked', 'body_sha256'):
        lines.append(f'  {dump(key)}: {dump(data[key])},')
    lines.append('  "components": {')
    components = list(data['components'].items())
    for index, (name, component) in enumerate(components):
        lines.extend([f'    {dump(name)}: {{',
                      f'      "name": {dump(component["name"])},',
                      f'      "basis": {dump(component["basis"])},',
                      '      "sources": {'])
        sources = list(component['sources'].items())
        for offset, (key, url) in enumerate(sources):
            comma = ',' if offset + 1 < len(sources) else ''
            lines.append(f'        {dump(key)}: {dump(url)}{comma}')
        lines.extend(['      }', '    }' + (',' if index + 1 < len(components) else '')])
    lines.extend(['  },', '  "claims": {'])
    claims = list(data['claims'].items())
    for index, (name, claim) in enumerate(claims):
        comma = ',' if index + 1 < len(claims) else ''
        lines.append(f'    {dump(name)}: {dump(claim)}{comma}')
    return '\n'.join(lines + ['  }', '}', '---', ''])


def body_line_offset(text, full_body):
    """File lines before a body line: front matter and the removed summary.

    The summary follows the H1, so the offset holds for every Sources line.
    """
    removed = full_body[full_body.index(START):full_body.index(END) + len(END) + 2] \
        if START in full_body else ''
    return text[:len(text) - len(full_body)].count('\n') + removed.count('\n')


def rebound(text, guide='GUIDE.md', baseline=None):
    """Validate the reviewed inventory and replace only the top-level digest token."""
    data, full_body = split(text)
    require(data is not None, 'missing version_basis front matter')
    body = without_summary(full_body)
    string(data['body_sha256'])
    require(re.fullmatch(r'[0-9a-f]{64}', data['body_sha256']), 'bad body digest')
    data['body_sha256'] = digest(body)
    validate(data, body, guide, baseline, body_line_offset(text, full_body))
    # split() already strictly parsed the object. Walk only its top-level members,
    # preserving all other bytes, even escaped keys or noncanonical whitespace.
    decoder = json.JSONDecoder()
    position = len('---\nversion_basis: ')
    position = re.compile(r'\s*').match(text, position).end() + 1  # opening {
    while True:
        position = re.compile(r'\s*').match(text, position).end()
        key, position = decoder.raw_decode(text, position)
        position = re.compile(r'\s*:\s*').match(text, position).end()
        start = position
        _, position = decoder.raw_decode(text, position)
        if key == 'body_sha256':
            return text[:start] + json.dumps(data['body_sha256']) + text[position:]
        position = re.compile(r'\s*,\s*').match(text, position).end()


def updated(text, guide='GUIDE.md', baseline=None):
    data, full_body = split(text)
    require(data is not None, 'missing version_basis front matter')
    body = without_summary(full_body)
    validate(data, body, guide, baseline, body_line_offset(text, full_body))
    title, rest = body.split('\n\n', 1)
    prefix = front_matter(data)
    return prefix + title + '\n\n' + render(data) + '\n\n' + rest


def paths():
    names = (ROOT / 'tools/version_basis_guides.txt').read_text(encoding='utf-8').splitlines()
    require(names and len(names) == len(set(names)), 'empty or duplicate pilot list')
    require(all(re.fullmatch(r'[a-z][a-z0-9-]*\.md', name) for name in names), 'bad pilot path')
    enrolled = {path.name for path in ROOT.glob('*.md')
                if path.read_text(encoding='utf-8').startswith('---\nversion_basis: ')}
    require(enrolled == set(names), 'pilot list differs from guides with version_basis front matter')
    return [ROOT / name for name in names]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--write', action='store_true')
    modes.add_argument('--bundle', type=Path)
    modes.add_argument('--rebind', type=Path, metavar='GUIDE',
                       help='assert the claim inventory was reviewed; update only its digest')
    parser.add_argument('guide', nargs='?', type=Path,
                        help='optional enrolled guide for --check or --write')
    args = parser.parse_args()
    try:
        selected = paths()
        baseline = load_source_baseline()
        require({name for name, _ in baseline} <= {path.name for path in selected},
                'Sources baseline contains an unenrolled guide; remove it')
        require(args.guide is None or args.check or args.write,
                'a positional guide requires --check or --write')
        if args.rebind:
            path = args.rebind.resolve()
            require(path in selected, '--rebind requires an enrolled guide')
            text = path.read_bytes().decode('utf-8')
            expected = rebound(text, path.name, baseline)
            path.write_bytes(expected.encode('utf-8'))
            print(f'  ok    {path.name}: rebound digest; this asserts the claim inventory '
                  'was reviewed, not that a demonstration was run. '
                  'Run python3 tools/version_basis.py --write to refresh summaries.')
            return 0
        if args.bundle:
            text = args.bundle.read_text(encoding='utf-8')
            data, body = split(text)
            if data is not None:
                require(updated(text, args.bundle, baseline) == text, 'stale summary')
            sys.stdout.write(body)
            return 0
        pending = []
        if args.guide:
            path = args.guide.resolve()
            require(path in selected, 'expected an enrolled guide')
            selected = [path]
        for path in selected:
            text = path.read_text(encoding='utf-8')
            try:
                expected = updated(text, path.name, baseline)
                require(args.write or text == expected, 'stale summary: run tools/version_basis.py --write')
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'{path.name}: {exc}') from exc
            pending.append((path, expected))
        if args.write:
            for path, expected in pending:
                path.write_text(expected, encoding='utf-8')
        retained = sum(count for (name, _), count in baseline.items()
                       if name in {path.name for path in selected})
        print(f'  ok    version basis: {len(pending)} opted-in guides; '
              f'{retained} grandfathered Sources URL/items retained')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'  FAIL  version basis: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
