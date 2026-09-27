#!/usr/bin/env python3
"""Strict YAML subset, renderer and offline pilot gate. Evidence is historical.

Accept only version_basis: followed by a JSON object between --- delimiters.
Semantic completeness and evidentiary sufficiency remain review obligations.
"""
import argparse
import datetime
import hashlib
import html
import json
import re
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


def identifiers(mapping):
    require(isinstance(mapping, dict) and bool(mapping), 'expected nonempty mapping')
    for name in mapping:
        require(re.fullmatch(r'[a-z][a-z0-9-]*', name), 'bad identifier: ' + name)


def digest(body):
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def source_id(url):
    return 's' + digest(url)[:12]


def verify_blocks(body):
    from check_guide_shape import headings, section_body, VERIFY_RE
    from _markdown import Fences
    blocks = []
    heads = headings(body)
    for _, level, title, start in heads:
        if not VERIFY_RE.match(title):
            continue
        fences, current, language = Fences(), [], ''
        for line in section_body(body, heads, start, level).splitlines():
            was_inside = fences.inside
            if fences.feed(line):
                if not was_inside:
                    language = re.sub(r'^ {0,3}[`~]+', '', line).strip().split(' ')[0]
                    current = []
                elif language == 'bash':
                    blocks.append('\n'.join(current))
            elif fences.inside:
                current.append(line)
    return blocks


def citation_urls(text):
    # Preserve explicit Markdown targets; trim sentence punctuation from bare URLs.
    explicit = set(re.findall(r'\]\((https?://[^\s<>\)]+)\)', text))
    bare = {url.rstrip('.,;') for url in re.findall(r'https?://[^\s<>\)]+', text)}
    return explicit | bare


def validate(data, body):
    from check_guide_shape import headings, section_body, SOURCES_RE
    keys(data, ('schema', 'checked', 'documentation_checked', 'body_sha256', 'components', 'claims'))
    require(type(data['schema']) is int and data['schema'] == 1, 'unsupported schema')
    string(data['checked'])
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', data['checked']), 'checked must be YYYY-MM-DD')
    checked = datetime.date.fromisoformat(data['checked'])
    require(checked <= datetime.date.today(), 'checked date is in the future')
    string(data['documentation_checked'])
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}', data['documentation_checked']),
            'documentation_checked must be YYYY-MM (preserve recorded precision)')
    documentation = datetime.date.fromisoformat(data['documentation_checked'] + '-01')
    require(documentation <= checked, 'documentation check follows metadata review')
    string(data['body_sha256'])
    require(re.fullmatch(r'[0-9a-f]{64}', data['body_sha256']), 'bad body digest')
    require(data['body_sha256'] == digest(body), 'body changed: review claims before rebinding digest')
    require(body.startswith('# ') and sum(level == 1 for _, level, _, _ in headings(body)) == 1,
            'guide body must start with exactly one H1')
    heads = headings(body)
    sources = '\n'.join(section_body(body, heads, start, level)
                        for _, level, title, start in heads if SOURCES_RE.match(title))
    require(any(SOURCES_RE.match(title) and
                SOURCES_RE.match(title).group(1).lower() == documentation.strftime('%B').lower() and
                int(SOURCES_RE.match(title).group(2)) == documentation.year
                for _, _, title, _ in heads), 'documentation month differs from Sources')
    source_urls = citation_urls(sources)
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
            require(url in source_urls, 'source URL absent from Sources: ' + url)
        cited_lines = '\n'.join(line for line in sources.splitlines()
                                if any(url in line for url in component['sources'].values()))
        require(component['basis'] == 'unknown' or re.search(r'(?<![A-Za-z0-9.])' + re.escape(component['basis']) +
                          r'(?![A-Za-z0-9.])', cited_lines),
                'basis absent from its Sources entries: ' + component['basis'])
    identifiers(data['claims'])
    blocks = verify_blocks(body)
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
            markers = re.findall(r'^# (DEMONSTRATED|REASONED)\b', blocks[number - 1], re.M)
            if markers:
                require(claim['status'] in markers, 'claim disagrees with explicit Verify fence marker')
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


def updated(text):
    data, full_body = split(text)
    require(data is not None, 'missing version_basis front matter')
    body = without_summary(full_body)
    validate(data, body)
    title, rest = body.split('\n\n', 1)
    prefix = text[:len(text) - len(full_body)]
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
    args = parser.parse_args()
    try:
        if args.bundle:
            text = args.bundle.read_text(encoding='utf-8')
            data, body = split(text)
            if data is not None:
                require(updated(text) == text, 'stale summary')
            sys.stdout.write(body)
            return 0
        pending = []
        for path in paths():
            text = path.read_text(encoding='utf-8')
            try:
                expected = updated(text)
                require(args.write or text == expected, 'stale summary: run tools/version_basis.py --write')
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f'{path.name}: {exc}') from exc
            pending.append((path, expected))
        if args.write:
            for path, expected in pending:
                path.write_text(expected, encoding='utf-8')
        print(f'  ok    version basis: {len(pending)} opted-in guides')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'  FAIL  version basis: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
