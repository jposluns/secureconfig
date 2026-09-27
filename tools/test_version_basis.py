#!/usr/bin/env python3
"""Mutation and integration tests for accidental metadata/summary drift."""
import contextlib
from collections import Counter
import datetime
import io
import json
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch
import unittest
from pathlib import Path

import version_basis as vb
from _markdown import body_lines
from check_guide_shape import headings

URL = 'https://example.com/v1.0#control'
SID = vb.source_id(URL)

BODY = '''# Fixture

A documented control.

## Verify

Observed refusal, then successful authorized request.

```bash
# REASONED: no isolated listener available.
printf 'probe example\\n'
```

## Sources (checked September 2026)

- Product v1.0: https://example.com/v1.0#control
'''


def fixture():
    return {'schema': 1, 'checked': '2026-09-26', 'documentation_checked': '2026-09',
            'body_sha256': vb.digest(BODY),
            'components': {'product': {'name': 'Product', 'basis': 'v1.0',
                                      'sources': {SID: URL}}},
            'claims': {'control': {'text': 'Requires authentication.', 'components': ['product'],
                                  'sources': ['product:' + SID], 'status': 'REASONED', 'verify': [1]}}}


def document(data, body=BODY):
    return '---\nversion_basis: ' + json.dumps(data) + '\n---\n' + body


class VersionBasisTests(unittest.TestCase):
    def test_round_trip_and_heading_lines(self):
        raw = document(fixture())
        rendered = vb.updated(raw)
        self.assertEqual(vb.updated(rendered), rendered)
        self.assertEqual(vb.without_summary(vb.split(rendered)[1]), BODY)
        self.assertEqual(len(body_lines(raw)), len(raw.splitlines()))
        self.assertEqual([(level, title) for _, level, title, _ in headings(raw)],
                         [(level, title) for _, level, title, _ in headings(BODY)])
        self.assertEqual(vb.split(BODY), (None, BODY))


    def test_normal_string_fields(self):
        data = fixture()
        data['claims']['control'].update(
            status='DEMONSTRATED', evidence='Observed refusal, then successful authorized request.')
        body = BODY.replace('# REASONED: no isolated listener available.',
                            '# DEMONSTRATED: observed refusal and authorized request.')
        data['body_sha256'] = vb.digest(body)
        rendered = vb.updated(document(data, body))
        self.assertEqual(vb.updated(rendered), rendered)

    def test_string_fields_reject_edge_whitespace(self):
        for field in ('name', 'basis', 'text', 'evidence'):
            for whitespace in (' ', '\u00a0', '\u2003'):
                for edge in ('leading', 'trailing'):
                    data = fixture()
                    claim = data['claims']['control']
                    claim.update(status='DEMONSTRATED',
                                 evidence='Observed refusal, then successful authorized request.')
                    body = BODY.replace('# REASONED: no isolated listener available.',
                                        '# DEMONSTRATED: observed refusal and authorized request.')
                    data['body_sha256'] = vb.digest(body)
                    target = data['components']['product'] if field in ('name', 'basis') else claim
                    value = target[field]
                    target[field] = whitespace + value if edge == 'leading' else value + whitespace
                    with self.subTest(field=field, whitespace=repr(whitespace), edge=edge):
                        with self.assertRaisesRegex(ValueError, 'leading or trailing whitespace'):
                            vb.updated(document(data, body))

    def test_citation_punctuation(self):
        self.assertEqual(vb.citation_urls(URL + ', ' + URL + '; ' + URL + '.'), {URL})
        self.assertIn(URL + ',', vb.citation_urls('[explicit](' + URL + ',)'))
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(URL + ','): URL + ','}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(URL + ',')]
        with self.assertRaisesRegex(ValueError, 'source URL absent'):
            vb.updated(document(data))

    def test_parser_refusals(self):
        for raw in ('---\nversion_basis: {}', '---\nx: {}\n---\n# X',
                    '---\nversion_basis: {"x":1,"x":2}\n---\n# X',
                    '---\nversion_basis: {"x":NaN}\n---\n# X',
                    '---\nversion_basis: &alias {}\n---\n# X',
                    '---\nversion_basis: []\n---\n# X'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                vb.split(raw)

    def test_schema_mutations(self):
        mutations = [
            lambda d: d.pop('checked'),
            lambda d: d.update(extra=True),
            lambda d: d.update(schema=True),
            lambda d: d.update(checked='2026-02-30'),
            lambda d: d.update(checked='20260926'),
            lambda d: d.update(checked='9999-01-01'),
            lambda d: d.update(documentation_checked='2026-08'),
            lambda d: d.update(body_sha256='0' * 64),
            lambda d: d.update(components={}),
            lambda d: d.update(claims={}),
            lambda d: d['components']['product'].update(basis='v9.9'),
            lambda d: d['components']['product'].update(sources={SID: 'https://example.com/missing'}),
            lambda d: d['components']['product'].update(sources=[]),
            lambda d: d['components']['product'].update(sources=[False]),
            lambda d: d['components']['product'].update(sources={vb.source_id('javascript:bad'): 'javascript:bad'}),
            lambda d: d['claims']['control'].update(components=['missing']),
            lambda d: d['claims']['control'].update(sources=['product:s000000000000']),
            lambda d: d['claims']['control'].update(sources=[]),
            lambda d: d['claims']['control'].update(status='VERIFIED'),
            lambda d: d['claims']['control'].update(status='DEMONSTRATED'),
            lambda d: d['claims']['control'].update(evidence='invented'),
            lambda d: d['claims']['control'].update(verify=[]),
            lambda d: d['claims']['control'].update(verify=[0]),
            lambda d: d['claims']['control'].update(verify=[True]),
            lambda d: d['claims']['control'].update(verify=[1, 1]),
        ]
        for index, mutate in enumerate(mutations):
            data = fixture()
            mutate(data)
            with self.subTest(index=index), self.assertRaises(ValueError):
                vb.updated(document(data))

    def test_evidence_and_marker_disagreement(self):
        data = fixture()
        claim = data['claims']['control']
        claim.update(status='DEMONSTRATED', evidence='Observed refusal, then successful authorized request.')
        with self.assertRaisesRegex(ValueError, 'marker'):
            vb.updated(document(data))
        body = BODY.replace('# REASONED: no isolated listener available.', '# DEMONSTRATED: observed refusal and authorized request.')
        data['body_sha256'] = vb.digest(body)
        vb.updated(document(data, body))
        claim['evidence'] = 'Invented observation.'
        with self.assertRaisesRegex(ValueError, 'evidence quote'):
            vb.updated(document(data, body))

    def test_boundaries_and_staleness(self):
        rendered = vb.updated(document(fixture()))
        for bad in (rendered.replace(vb.END, ''), rendered + vb.START,
                    rendered.replace(vb.START, 'TEMP').replace(vb.END, vb.START).replace('TEMP', vb.END)):
            with self.assertRaises(ValueError):
                vb.updated(bad)
        self.assertNotEqual(vb.updated(rendered.replace('Requires authentication.', 'Wrong.', 1)),
                            rendered.replace('Requires authentication.', 'Wrong.', 1))
        with self.assertRaisesRegex(ValueError, 'body changed'):
            vb.updated(rendered + 'Unreviewed new claim.\n')

    def test_source_identity_and_enrollment(self):
        data = fixture()
        data['components']['product']['sources']['s000000000000'] = URL
        with self.assertRaisesRegex(ValueError, 'source ID'):
            vb.updated(document(data))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'fixture.md').write_text(document(fixture()), encoding='utf-8')
            listing = root / 'tools/version_basis_guides.txt'
            with patch.object(vb, 'ROOT', root):
                for names in ('', 'fixture.md\nfixture.md\n', 'missing.md\n', '../fixture.md\n'):
                    listing.write_text(names, encoding='utf-8')
                    with self.subTest(names=names), self.assertRaises(ValueError):
                        vb.paths()
                listing.write_text('fixture.md\n', encoding='utf-8')
                self.assertEqual(vb.paths(), [root / 'fixture.md'])

    def test_bundle_refuses_invalid_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'invalid.md'
            path.write_text(document(fixture()), encoding='utf-8')
            result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'),
                                     '--bundle', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, '')
            self.assertIn('stale summary', result.stderr)

    def test_pilots_and_entry_points(self):
        for path in vb.paths():
            text = path.read_text(encoding='utf-8')
            self.assertEqual(vb.updated(text, path.name, vb.load_source_baseline()), text)
            result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'),
                                     '--bundle', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, vb.split(text)[1])
            self.assertTrue(result.stdout.startswith('# '))
        result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class SourcesBasisTests(unittest.TestCase):
    url = 'https://example.com/control'
    other = 'https://example.com/other'

    def check(self, sources, basis='v1.0', urls=None, baseline=None):
        data = fixture()
        data['components']['product'].update(
            basis=basis, sources={vb.source_id(url): url for url in (urls or [self.url])})
        data['claims']['control']['sources'] = ['product:' + vb.source_id(self.url)]
        body = BODY[:BODY.index('- Product')] + sources + '\n'
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md', baseline)

    def test_each_url_needs_its_own_basis(self):
        with self.assertRaisesRegex(ValueError, 'basis.*absent.*' + self.other):
            self.check(f'- Product v1.0: {self.url}\n- Other: {self.other}',
                       urls=[self.url, self.other])
        self.check(f'- Product v1.0: {self.url}\n- Other v1.0: {self.other}',
                   urls=[self.url, self.other])

    def test_unknown_is_exempt_but_url_still_required(self):
        self.check(f'- Product: {self.url}', basis='unknown')
        with self.assertRaisesRegex(ValueError, 'source URL absent'):
            self.check('- No citation', basis='unknown')

    def test_wrapped_items_and_paragraphs(self):
        for item in (f'- Product v1.0:\n  {self.url}',
                     f'- Product: {self.url}\n  basis v1.0',
                     f'- Product: {self.url}\nbasis v1.0',
                     f'- Product: {self.url}\n\n  Basis v1.0',
                     f'1. Product v1.0:\n   {self.url}'):
            with self.subTest(item=item):
                self.check(item)
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product: {self.url}\n  wrapped without basis\n- Other v1.0')

    def test_numbered_siblings_do_not_share_basis(self):
        for first, second in (('1.', '2.'), ('3)', '4)'), ('99.', '100.')):
            sources = f'{first} Product v1.0: {self.url}\n{second} Other: {self.other}'
            with self.subTest(first=first), self.assertRaisesRegex(ValueError, 'basis.*absent'):
                self.check(sources, urls=[self.url, self.other])
            self.check(sources.replace('Other:', 'Other v1.0:'), urls=[self.url, self.other])
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Parent\n  1. Product v1.0: {self.url}\n  2. Other: {self.other}',
                       urls=[self.url, self.other])

    def test_every_repeated_item_must_qualify(self):
        for items in ((f'- Product v1.0: {self.url}', f'- Again: {self.url}'),
                      (f'- Again: {self.url}', f'- Product v1.0: {self.url}')):
            with self.subTest(items=items), self.assertRaisesRegex(ValueError, 'basis.*absent'):
                self.check('\n'.join(items))
        self.check(f'- Product v1.0: {self.url}\n- Again v1.0: {self.url}')

    def test_no_borrowing_from_nested_items_or_separate_prose(self):
        for sources in (f'- Product: {self.url}\n  - Child v1.0',
                        f'- Parent v1.0\n  - Child: {self.url}',
                        f'- Product: {self.url}\n\nSeparate v1.0',
                        f'Product v1.0: {self.url}'):
            with self.subTest(sources=sources), self.assertRaisesRegex(ValueError, 'basis.*absent'):
                self.check(sources)

    def test_unsupported_containers_fail_closed(self):
        # Codex round 1: citations the item parser cannot see must not pass.
        for sources in (f'- Product v1.0: {self.url}\n- - Again: {self.url}',
                        f'- Product v1.0: {self.url}\n- # Again: {self.url}',
                        f'- Product v1.0: {self.url}\n> - Again: {self.url}',
                        f'- Product v1.0: {self.url}\n\n> Again: {self.url}',
                        f'- Product v1.0: {self.url}\n\nAgain: {self.url}',
                        f'- Product v1.0: {self.url}\n\n### Again {self.url}'):
            with self.subTest(sources=sources), self.assertRaisesRegex(
                    ValueError, re.escape(self.url) + ' cited in an unsupported Sources container'):
                self.check(sources)
        # The basis literal on the hidden citation does not rescue it.
        with self.assertRaisesRegex(ValueError, 'unsupported Sources container'):
            self.check(f'- Product v1.0: {self.url}\n- - Again v1.0: {self.url}')
        # Passing controls: the same citations, each in its own list item.
        self.check(f'- Product v1.0: {self.url}\n- Again v1.0: {self.url}')
        self.check(f'- Product v1.0: {self.url}\n  - Again v1.0: {self.url}')
        self.check(f'- Product v1.0: {self.url}\n- Product v1.0: [again]({self.url})')
        # Unknown basis: URL presence stays mandatory, the container check is skipped.
        self.check(f'- Product: {self.url}\n- - Again: {self.url}', basis='unknown')

    def test_marker_only_items_start_new_items(self):
        # Codex round 1: a marker-only line begins an item (CommonMark); it is
        # not lazy prose that lets the previous item's basis cover the citation.
        for marker in ('2.', '-', '2)', '2.  '):
            sources = f'1. Product v1.0: {self.url}\n{marker}\n   Again: {self.url}'
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                self.check(sources)
        with self.assertRaisesRegex(ValueError, 'unsupported Sources container'):
            self.check(f'1. Product v1.0: {self.url}\n2.\n   Again: {self.url}')
        # Passing controls: marker with text, and genuine lazy continuation.
        self.check(f'1. Product v1.0: {self.url}\n2. Again v1.0:\n   {self.url}')
        self.check(f'1. Product v1.0:\n{self.url}')
        from check_verify_marking import tokenize
        _, _, tokens = tokenize('1. Product\n2.\n   Again')
        self.assertEqual([token.kind for token in tokens], ['paragraph', 'unsupported'])

    def test_exact_urls_not_prefixes(self):
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product: {self.url}\n- Other v1.0: {self.url}-other')
        self.check(f'- Product v1.0: [control]({self.url})')
        self.check(f'- Product v1.0: {self.url}.')

    def test_literal_tag_spelling_and_boundaries(self):
        for basis, spelling in (('v2.51.0', '2.51.0'), ('2.51.0', 'v2.51.0'),
                                ('2.51.0', '2.51.01'), ('2.51.0', '2.51.0.1')):
            with self.subTest(basis=basis, spelling=spelling):
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product {spelling}: {self.url}', basis=basis)
        self.check(f'- Product `2.51.0`: {self.url}', basis='2.51.0')
        # As before, a literal in the URL itself counts.
        self.check(f'- Product: {self.url}/v1.0 and {self.url}')

    def test_counted_baseline_and_stale_entries(self):
        item = f'- Product: {self.url}'
        fp = vb.source_fingerprint('product', 'v1.0', self.url, item)
        baseline = Counter({('fixture.md', fp): 1})
        self.check(item, baseline=baseline)
        for sources in (item + '\n' + item, item + ' changed'):
            with self.subTest(sources=sources), self.assertRaisesRegex(ValueError, 'new/changed/excess'):
                self.check(sources, baseline=baseline)
        for sources, basis in ((item.replace('Product:', 'Product v1.0:'), 'v1.0'),
                               (item, 'unknown')):
            with self.subTest(sources=sources), self.assertRaisesRegex(ValueError, 'stale Sources baseline'):
                self.check(sources, basis=basis, baseline=baseline)
        with self.assertRaisesRegex(ValueError, 'new/changed/excess'):
            self.check(item, baseline=Counter({('other.md', fp): 1}))
        self.assertEqual(len({vb.source_fingerprint(*args) for args in (
            ('product', 'v1.0', self.url, item), ('other', 'v1.0', self.url, item),
            ('product', 'v2.0', self.url, item), ('product', 'v1.0', self.other, item),
            ('product', 'v1.0', self.url, item + ' changed'))}), 5)

    def test_baseline_parser_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            path = root / 'tools/version_basis_sources_baseline.txt'
            valid = 'fixture.md\t' + 'a' * 64 + '\t1\n'
            with patch.object(vb, 'ROOT', root):
                with self.assertRaises(OSError):
                    vb.load_source_baseline()
                for content in ('bad', valid + valid, valid.replace('\t1', '\t0'),
                                valid.replace('fixture.md', '../fixture.md'),
                                valid.replace('a' * 64, 'A' * 64)):
                    path.write_text(content)
                    with self.subTest(content=content), self.assertRaises(ValueError):
                        vb.load_source_baseline()
                path.write_text('# comment\n' + valid)
                self.assertEqual(vb.load_source_baseline(), {('fixture.md', 'a' * 64): 1})


class RoundTwoTests(unittest.TestCase):
    def test_calendar_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / 'CHANGELOG.md'
            with patch.object(vb, 'ROOT', root):
                log.write_text('## 2026-09-25\n## 2026-09-26\n## 2026-08-01\n')
                self.assertEqual(vb.latest_change(), datetime.date(2026, 9, 26))
                vb.updated(document(fixture()))
                log.write_text('## 2026-09-25\n')
                with self.assertRaisesRegex(ValueError, 'newest CHANGELOG'):
                    vb.updated(document(fixture()))
                for content in ('# No dated heading\n', '## 2026-02-30\n'):
                    log.write_text(content)
                    with self.assertRaises(ValueError):
                        vb.updated(document(fixture()))
                log.unlink()
                with self.assertRaises(OSError):
                    vb.updated(document(fixture()))

    def test_digest_diagnostic(self):
        body = BODY + 'A reviewed qualification.\n'
        with self.assertRaises(ValueError) as caught:
            vb.updated(document(fixture(), body), 'fixture.md')
        self.assertIn(vb.digest(body), str(caught.exception))
        self.assertIn('python3 tools/version_basis.py --rebind fixture.md', str(caught.exception))

    def test_rebind_only_digest_and_strict_validation(self):
        data = fixture()
        data = {'claims': data.pop('claims'), **data}
        data['claims']['control']['text'] = data['body_sha256']
        raw = document(data).replace('"body_sha256":', r'"body_\u0073ha256" :')
        raw += 'A reviewed qualification.\n'
        expected_hash = vb.digest(vb.without_summary(vb.split(raw)[1]))
        result = vb.rebound(raw, 'fixture.md')
        self.assertEqual(result, raw.replace(
            r'"body_\u0073ha256" : "' + data['body_sha256'] + '"',
            r'"body_\u0073ha256" : "' + expected_hash + '"'))
        self.assertEqual(vb.rebound(result), result)
        bad = fixture()
        bad['claims']['control']['status'] = 'DEMONSTRATED'
        with self.assertRaisesRegex(ValueError, 'needs evidence'):
            vb.rebound(document(bad, BODY + 'Body edit.\n'))
        with self.assertRaisesRegex(ValueError, 'bad body digest'):
            vb.rebound(document({**fixture(), 'body_sha256': 'invalid'}))

    def test_cli_review_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'tools/version_basis_guides.txt').write_text('fixture.md\n')
            (root / 'tools/version_basis_sources_baseline.txt').write_text('')
            (root / 'CHANGELOG.md').write_text('## 2026-09-26\n')
            path = root / 'fixture.md'
            raw = vb.updated(document(fixture())) + 'A reviewed qualification.\n'
            path.write_text(raw)
            def run(*args):
                output = io.StringIO()
                with patch.object(vb, 'ROOT', root), patch.object(sys, 'argv', ['version_basis.py', *args]), \
                        contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    rc = vb.main()
                return rc, output.getvalue()
            self.assertEqual(run('--write')[0], 1)
            self.assertEqual(path.read_text(), raw)
            rc, output = run('--rebind', str(path))
            self.assertEqual(rc, 0, output)
            self.assertIn('asserts the claim inventory was reviewed', output)
            old = fixture()['body_sha256']
            new = vb.digest(BODY + 'A reviewed qualification.\n')
            self.assertEqual(path.read_text(), raw.replace(old, new, 1))
            self.assertEqual(run('--write')[0], 0)
            self.assertEqual(run('--check', str(path))[0], 0)
            before = path.read_bytes()
            self.assertEqual(run('--rebind', str(root / 'other.md'))[0], 1)
            self.assertEqual(path.read_bytes(), before)
            invalid = path.read_text().replace('"status": "REASONED"', '"status": "DEMONSTRATED"')
            path.write_text(invalid)
            self.assertEqual(run('--rebind', str(path))[0], 1)
            self.assertEqual(path.read_text(), invalid)

    def test_rebind_does_not_refresh_stale_summary(self):
        raw = vb.updated(document(fixture()))
        raw = raw.replace('control: Requires authentication.', 'control: Stale summary.')
        raw += 'A reviewed qualification.\n'
        result = vb.rebound(raw)
        self.assertIn('control: Stale summary.', result)
        self.assertNotEqual(vb.updated(result), result)

    def test_multiline_emission(self):
        data = fixture()
        other = URL + '-other'
        data['components']['product']['sources'][vb.source_id(other)] = other
        front = vb.front_matter(data)
        self.assertEqual(vb.split(front + BODY)[0], data)
        lines = front.splitlines()
        for key in data['components']['product']['sources']:
            self.assertEqual(sum(line.count('"' + key + '":') for line in lines), 1)
        self.assertFalse(any(SID in line and vb.source_id(other) in line for line in lines))
        self.assertEqual(sum('"control": {' in line for line in lines), 1)
        self.assertEqual(len(body_lines(front + BODY)), len((front + BODY).splitlines()))

    def test_shape_cli_front_matter_refusals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for front in ('---\ntitle: foreign\n---\n',
                          '---\nversion_basis: {bad}\n---\n',
                          '---\nversion_basis: {}\n'):
                (root / 'fixture.md').write_text(front + BODY)
                result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/check_guide_shape.py'),
                                         str(root)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn('FAIL  fixture.md: invalid front matter:', result.stdout)
                self.assertNotIn('Traceback', result.stdout + result.stderr)


class VerifyGrammarTests(unittest.TestCase):
    def check_body(self, body, data=None):
        data = fixture() if data is None else data
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body))

    def test_shared_declaration_locations(self):
        old = '# REASONED: no isolated listener available.\n'
        for body in (
            BODY.replace(old, '# **reasoned:** recorded scope.\n'),
            BODY.replace(old, '').replace('## Verify', '## Verify (REASONED: recorded scope)'),
            BODY.replace(old, '').replace('Observed refusal, then successful authorized request.',
                                         'REASONED: following block; recorded scope.'),
            BODY.replace(old, '').replace('\n## Sources', '\nREASONED: preceding block; recorded scope.\n\n## Sources'),
        ):
            with self.subTest(body=body):
                self.check_body(body)

    def test_non_declarations_cannot_mark(self):
        old = '# REASONED: no isolated listener available.'
        for replacement in ('# REASONED', '# REASONED:', '# reasonedness: text',
                            '# ordinary comment\n# REASONED: later comment.',
                            'echo first\n# REASONED: per-command comment.',
                            'printf "REASONED: string, not provenance"'):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, 'marker|provenance'):
                self.check_body(BODY.replace(old, replacement))

    def test_attached_marker_disagreement(self):
        old = '# REASONED: no isolated listener available.\n'
        for body in (
            BODY.replace(old, '# demonstrated: recorded pair.\n'),
            BODY.replace(old, '').replace('## Verify', '## Verify (DEMONSTRATED: recorded pair)'),
            BODY.replace(old, '').replace('Observed refusal, then successful authorized request.',
                                         'DEMONSTRATED: following block; recorded pair.'),
            BODY.replace(old, '').replace('\n## Sources', '\nDEMONSTRATED: preceding block; recorded pair.\n\n## Sources'),
        ):
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, 'disagrees'):
                self.check_body(body)

    def test_conflicting_markers_fail(self):
        body = BODY.replace('## Verify', '## Verify (DEMONSTRATED: recorded pair)')
        with self.assertRaisesRegex(ValueError, 'conflicting declarations'):
            self.check_body(body)

    def test_later_comment_does_not_create_mixed_status(self):
        body = BODY.replace("printf 'probe", "# DEMONSTRATED: later command.\nprintf 'probe")
        self.check_body(body)
        data = fixture()
        data['claims']['control'].update(
            status='DEMONSTRATED', evidence='Observed refusal, then successful authorized request.')
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            self.check_body(body, data)

    def test_mixed_claims_need_separate_fences(self):
        data = fixture()
        data['claims']['observed'] = dict(data['claims']['control'],
            status='DEMONSTRATED', evidence='Observed refusal, then successful authorized request.')
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            self.check_body(BODY, data)
        second = "\n\x60\x60\x60bash\n# DEMONSTRATED: recorded pair.\nprintf 'other probe\\n'\n\x60\x60\x60\n"
        body = BODY.replace('\n## Sources', second + '\n## Sources')
        data['claims']['observed']['verify'] = [2]
        self.check_body(body, data)
        data['claims']['observed']['verify'] = [1]
        with self.assertRaisesRegex(ValueError, 'disagrees'):
            self.check_body(body, data)

    def test_nested_roots_and_noncanonical_titles(self):
        body = BODY.replace('## Verify', '## Verify\n\n### Verify')
        self.check_body(body)
        self.assertEqual(len(vb.verify_blocks(body)), 1)
        body = BODY.replace('## Verify', '## Verify from outside')
        self.assertEqual(vb.verify_blocks(body), [])
        with self.assertRaisesRegex(ValueError, 'ordinal'):
            self.check_body(body)

    def test_unsupported_containers_fail(self):
        for body in (
            BODY.replace('## Verify', '> ## Verify'),
            BODY.replace('## Verify', 'Verify\n------'),
            BODY.replace('## Verify', '<div>\n## Verify\n</div>'),
        ):
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, 'unsupported-container'):
                self.check_body(body)


if __name__ == '__main__':
    unittest.main()
