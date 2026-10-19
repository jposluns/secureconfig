#!/usr/bin/env python3
"""Mutation and integration tests for accidental metadata/summary drift."""
import contextlib
from collections import Counter
import datetime
import io
import json
import os
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
from check_verify_marking import gate_parser, ParserUnavailable

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
    @staticmethod
    def local_env():
        env = os.environ.copy()
        env.pop('CI', None)
        return env

    def test_round_trip_and_heading_lines(self):
        raw = document(fixture())
        rendered = vb.updated(raw)
        self.assertEqual(vb.updated(rendered), rendered)
        self.assertEqual(vb.without_summary(vb.split(rendered)[1]), BODY)
        self.assertEqual(len(body_lines(raw)), len(raw.splitlines()))
        self.assertEqual([(level, title) for _, level, title, _ in headings(raw)],
                         [(level, title) for _, level, title, _ in headings(BODY)])
        self.assertEqual(vb.split(BODY), (None, BODY))


    def test_summary_lists_and_order(self):
        data = fixture()
        sha = '4ba3cc0e2ebec61b726b227fdf51e55f4a502182'
        data['components']['product']['basis'] = sha
        data['components']['aux'] = {'name': 'Aux <&|`>', 'basis': 'unknown',
                                     'sources': {SID: URL}}
        data['claims']['control']['components'] = ['aux', 'product']
        data['claims']['control']['sources'].append('aux:' + SID)
        data['claims']['another'] = dict(data['claims']['control'],
            text='Observed control.', status='DEMONSTRATED', verify=[],
            evidence='Observed refusal, then successful authorized request.')
        body = BODY.replace('- Product v1.0:', f'- Product {sha}:')
        data['body_sha256'] = vb.digest(body)
        rendered = vb.updated(document(data, body))
        summary = vb.render(data)
        self.assertEqual(summary, '\n'.join([
            vb.START, '**Version basis**', '', vb.ADVICE, '',
            'Metadata reviewed 2026-09-26; documentation checked 2026-09 '
            '(exact day unknown). DEMONSTRATED refers to historical evidence in this guide; '
            'REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.',
            '', 'Components (recorded basis):', '',
            f'- product: Product, {sha}', '- aux: Aux &lt;&amp;&#124;&#96;&gt;, unknown',
            '', 'Claims (full source mapping in the front matter):', '',
            '- control (REASONED; aux, product): Requires authentication.',
            '- another (DEMONSTRATED; aux, product): Observed control.', vb.END]))
        metadata, full_body = vb.split(rendered)
        self.assertEqual(metadata, data)
        self.assertEqual(full_body, body.replace('# Fixture\n\n', '# Fixture\n\n' + summary + '\n\n', 1))
        self.assertEqual(vb.without_summary(full_body), body)
        self.assertEqual(vb.updated(rendered), rendered)
        data['components']['product']['basis'] = '<&|`>'
        self.assertIn('- product: Product, &lt;&amp;&#124;&#96;&gt;', vb.render(data))

    def test_claim_text_preserves_cell_output_and_list_structure(self):
        try:
            parser = gate_parser(required=True)
        except ParserUnavailable as exc:
            if os.environ.get('CI'):
                raise
            self.skipTest(str(exc))
        for text in ('- item', '+ item', '* item', '# heading', '> quote', '1. item',
                     '1) item', '---', '~~~', '**bold** _emphasis_',
                     '[link](https://example.com)', '![image](https://example.com)',
                     r'\*literal\* &amp; <b> | `code`', 'word\u2028- item'):
            with self.subTest(text=text):
                data = fixture()
                data['claims']['control']['text'] = text
                rendered = vb.updated(document(data))
                line = next(line for line in rendered.split('\n')
                            if line.startswith('- control ('))
                tokens = parser.parse(line)
                self.assertEqual([token.type for token in tokens],
                                 ['bullet_list_open', 'list_item_open', 'paragraph_open',
                                  'inline', 'paragraph_close', 'list_item_close', 'bullet_list_close'])
                self.assertEqual(line, '- control (REASONED; product): ' + vb.cell(text))
                self.assertEqual(vb.split(rendered)[0], data)

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
        self.assertEqual(vb.cites(URL + ', ' + URL + '; ' + URL + '.', URL), 3)
        self.assertEqual(vb.cites('[explicit](' + URL + ',)', URL + ','), 1)
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
                                     '--bundle', str(path)], capture_output=True, text=True,
                                    env=self.local_env())
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, '')
            self.assertIn('stale summary', result.stderr)

    def test_pilots_and_entry_points(self):
        for path in vb.paths():
            text = path.read_text(encoding='utf-8')
            self.assertEqual(vb.updated(text, path.name, vb.load_source_baseline()), text)
            result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'),
                                     '--bundle', str(path)], capture_output=True, text=True,
                                    env=self.local_env())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, vb.split(text)[1])
            self.assertTrue(result.stdout.startswith('# '))
        result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'), '--check'],
                                capture_output=True, text=True, env=self.local_env())
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_parser_requirement_in_subprocess(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'plain.md'
            path.write_text('# Plain\n', encoding='utf-8')
            script = str(vb.ROOT / 'tools/version_basis.py')
            for ci, required in ((False, False), (True, False), (False, True), (True, True)):
                env = self.local_env()
                if ci:
                    env['CI'] = 'true'
                command = [sys.executable, '-S', script, '--bundle', str(path)]
                if required:
                    command.append('--require-parser')
                with self.subTest(ci=ci, required=required):
                    result = subprocess.run(command, capture_output=True, text=True, env=env)
                    self.assertEqual(result.returncode, int(ci or required), result.stderr)
                    if ci or required:
                        self.assertIn('pinned parser unavailable', result.stderr)
                    else:
                        self.assertIn('SKIP  version basis rendered Sources checks', result.stderr)
                        self.assertEqual(result.stdout, '# Plain\n')

            standalone = subprocess.run([sys.executable, '-S', script, '--bundle', str(path)],
                                        capture_output=True, text=True, env=self.local_env())
            quiet = subprocess.run([sys.executable, '-S', script, '--no-advisory',
                                    '--bundle', str(path)], capture_output=True, text=True,
                                   env=self.local_env())
            self.assertEqual(standalone.stderr.count('SKIP  version basis'), 1)
            self.assertEqual(quiet.returncode, 0, quiet.stderr)
            self.assertNotIn('SKIP  version basis', quiet.stderr)
            disallowed = subprocess.run([sys.executable, '-S', script, '--no-advisory',
                                         '--check'], capture_output=True, text=True,
                                        env=self.local_env())
            self.assertEqual(disallowed.returncode, 2)
            self.assertIn('--no-advisory requires --bundle', disallowed.stderr)
            build = (vb.ROOT / 'scripts/build-llms-full.sh').read_text(encoding='utf-8')
            self.assertIn('python3 tools/version_basis.py --check', build)
            self.assertIn('python3 tools/version_basis.py --no-advisory --bundle "$f"', build)


class SourcesBasisTests(unittest.TestCase):
    url = 'https://example.com/control'
    other = 'https://example.com/other'

    def check(self, sources, basis='v1.0', urls=None, baseline=None, parser=None):
        data = fixture()
        urls = urls or [self.url]
        data['components']['product'].update(
            basis=basis, sources={vb.source_id(url): url for url in urls})
        data['claims']['control']['sources'] = ['product:' + vb.source_id(urls[0])]
        body = BODY[:BODY.index('- Product')] + sources + '\n'
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md', baseline, parser=parser)

    def check_urls(self, sources, urls):
        """Like check(), with the claim citing urls[0] instead of self.url."""
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(url): url for url in urls}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(urls[0])]
        body = BODY[:BODY.index('- Product')] + sources + '\n'
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md')

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

    def test_pinned_source_requires_known_basis_with_and_without_parser(self):
        sha = '4ba3cc0e2ebec61b726b227fdf51e55f4a502182'
        cases = (
            (f'https://github.com/acme/repo/blob/{sha}/README.md', sha),
            ('https://github.com/acme/repo/tree/v2.4/src', 'v2.4'),
            ('https://github.com/acme/repo/tree/release/1.2', 'release/1.2'),
            ('https://github.com/acme/repo/blob/version/2026.8.3/README.md',
             'version/2026.8.3'),
            ('https://github.com/acme/repo/raw/v2.4/file', 'v2.4'),
            ('https://github.com/acme/repo/blame/v2.4/file', 'v2.4'),
            (f'https://github.com/acme/repo/commit/{sha}', sha),
            ('https://github.com/acme/repo/releases/tag/v2.4', 'v2.4'),
            ('https://github.com/acme/repo/releases/tag/stable', 'stable'),
            (f'https://gitlab.com/acme/repo/-/blob/{sha}/README.md', sha),
            ('https://gitlab.com/acme/repo/-/tree/v2.4/src', 'v2.4'),
            ('https://gitlab.com/acme/repo/-/raw/v2.4/file', 'v2.4'),
            (f'https://gitlab.com/acme/repo/-/commit/{sha}', sha),
            ('https://gitlab.com/acme/repo/-/tags/stable', 'stable'),
            ('https://gitlab.com/acme/repo/-/releases/stable', 'stable'),
            ('https://gitlab.com/acme/tree/repo/-/blob/v2.4/file', 'v2.4'),
            (f'https://raw.githubusercontent.com/acme/repo/{sha}/README.md', sha),
            ('https://raw.githubusercontent.com/acme/repo/refs/tags/stable/README.md', 'stable'),
            ('https://raw.githubusercontent.com/acme/repo/refs/tags/release/1.2/README.md',
             'release/1.2'),
            ('https://raw.githubusercontent.com/acme/repo/refs/heads/release-1.2/README.md',
             'release-1.2'),
            ('https://git.example.org/cgit/repo/tree/file?h=v2.4', 'v2.4'),
            (f'https://git.example.org/cgit/repo/tree/file?id={sha}', sha),
            ('https://git.kernel.org/pub/scm/acme/repo.git/tree/file?h=v2.4', 'v2.4'),
            ('https://git.zx2c4.com/acme/repo/tree/file?h=stable', 'stable'),
            ('https://git.zx2c4.com/acme/repo/plain/file?id=stable', 'stable'),
            (f'https://git.zx2c4.com/acme/repo/commit/?h=master&id={sha}', sha),
            (f'https://git.zx2c4.com/acme/repo/diff/?id={sha}', sha),
            (f'https://git.zx2c4.com/acme/repo/patch/?h=master&id={sha}', sha),
            (f'https://git.zx2c4.com/acme/repo/commit/?id=main&id={sha}', sha),
            (f'https://git.zx2c4.com/acme/repo/commit/?id={sha}&h=master', sha),
            (f'https://git.zx2c4.com/acme/repo/tree/file?h=main&id={sha}', sha),
            (f'https://git.zx2c4.com/acme/repo/tree/file?id={sha}&h=main', sha),
            (f'https://git.zx2c4.com/acme/repo/tree/file?h=v2.4&id={sha}', sha),
            ('https://github.com/acme/repo/blob/v2.4/file?h=main', 'v2.4'),
            ('https://github.com/acme/repo/blob/v2.4/file?id=main&h=master', 'v2.4'),
            (f'https://github.com/acme/repo/wiki/History/{sha}', sha),
            (f'https://www.github.com/acme/repo/wiki/History/{sha}', sha),
        )
        parser = gate_parser(required=bool(os.environ.get('CI')))
        for url, pin in cases:
            for selected in ((None, parser) if parser is not None else (None,)):
                with self.subTest(url=url, parser=selected is not None):
                    with self.assertRaisesRegex(
                            ValueError, f'pinned source URL requires a known basis '
                            f'\\(component product, ref {re.escape(pin)}\\)'):
                        self.check(f'- Product: [doc]({url})', basis='unknown',
                                   urls=[url], parser=selected)
                    self.check(f'- Product {pin}: [doc]({url})', basis=pin,
                               urls=[url], parser=selected)

    def test_moving_refs_and_release_line_docs_are_not_pins(self):
        parser = gate_parser(required=bool(os.environ.get('CI')))
        for url in ('https://github.com/acme/repo/blob/main/README.md',
                    'https://github.com/acme/repo/tree/master/src',
                    'https://github.com/acme/repo/raw/HEAD/file',
                    'https://github.com/acme/repo/blame/trunk/file',
                    'https://raw.githubusercontent.com/acme/repo/develop/README.md',
                    'https://raw.githubusercontent.com/acme/repo/refs/heads/master/README.md',
                    'https://github.com/acme/repo/blob/feature/README.md',
                    'https://gitlab.com/acme/repo/-/blob/main/README.md',
                    'https://git.zx2c4.com/acme/repo/tree/file?h=master',
                    'https://github.com/acme/repo/releases/tag/main',
                    'https://docs.example.org/docs/2.4/guide'):
            for selected in ((None, parser) if parser is not None else (None,)):
                with self.subTest(url=url, parser=selected is not None):
                    self.check(f'- Product: [doc]({url})', basis='unknown',
                               urls=[url], parser=selected)

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
        try:
            pinned = gate_parser(required=True)
        except ParserUnavailable:
            pinned = None
        for parser in (None, pinned) if pinned is not None else (None,):
            for sources in (f'- Product v1.0: {self.url}\n- - Again: {self.url}',
                        f'- Product v1.0: {self.url}\n- # Again: {self.url}',
                        f'- Product v1.0: {self.url}\n> - Again: {self.url}',
                        f'- Product v1.0: {self.url}\n\n> Again: {self.url}',
                        f'- Product v1.0: {self.url}\n\nAgain: {self.url}',
                        f'- Product v1.0: {self.url}\n\n### Again {self.url}'):
                with self.subTest(sources=sources, parser=parser), self.assertRaisesRegex(
                        ValueError, re.escape(self.url) + ' cited in an unsupported Sources container'):
                    self.check(sources, parser=parser)
            # The basis literal on the hidden citation does not rescue it.
            with self.assertRaisesRegex(ValueError, 'unsupported Sources container'):
                self.check(f'- Product v1.0: {self.url}\n- - Again v1.0: {self.url}', parser=parser)
            # Passing controls: the same citations, each in its own list item.
            self.check(f'- Product v1.0: {self.url}\n- Again v1.0: {self.url}', parser=parser)
            self.check(f'- Product v1.0: {self.url}\n  - Again v1.0: {self.url}', parser=parser)
            self.check(f'- Product v1.0: {self.url}\n- Product v1.0: [again]({self.url})',
                       parser=parser)
            # Unknown basis: URL presence stays mandatory, the container check is skipped.
            self.check(f'- Product: {self.url}\n- - Again: {self.url}', basis='unknown', parser=parser)

    def test_formatted_bare_urls_are_counted(self):
        # Codex round 2: a trailing ** once hid the URL from every check.
        forms = (f'**{self.url}**', f'`{self.url}`', f'_{self.url}_', f'<{self.url}>',
                 f'*_{self.url}_*.', f'~~{self.url}~~;', f'`{self.url}`**,')
        for form in forms:
            with self.subTest(form=form):
                self.assertEqual(vb.cites(form, self.url), 1)
                self.check(f'- Product v1.0: {form}')
                with self.assertRaisesRegex(
                        ValueError, re.escape(self.url) + ' cited in an unsupported Sources container'):
                    self.check(f'- Product v1.0: {self.url}\n- - Again: {form}')
        # An explicit target keeps its exact spelling; like GFM's autolinks, a
        # trailing _ before a non-URL character also reads as citing the shorter URL.
        self.assertEqual(vb.cites(f'[x]({self.url}_)', self.url + '_'), 1)
        self.assertEqual(vb.cites(f'[x]({self.url}_)', self.url), 1)

    def test_known_urls_match_exactly_in_any_spelling(self):
        # Round 3: URL extraction read these spellings as other URLs, so the
        # known URL was counted zero times and the basis-less item escaped.
        u = self.url
        forms = (f'[{u}]({u})', f'[**{u}**]({u})', f'[text]({u})', f'<{u}>', u)
        for form in forms:
            with self.subTest(form=form):
                self.assertGreaterEqual(vb.cites(form, u), 1)
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product v1.0: {u}\n- Again: {form}')
                with self.assertRaisesRegex(
                        ValueError, re.escape(u) + ' cited in an unsupported Sources container'):
                    self.check(f'- Product v1.0: {u}\n- - Again: {form}')
                self.check(f'- Product v1.0: {form}')
        self.assertEqual(vb.cites(f'[{u}]({u})', u), 2)
        self.assertEqual(vb.cites(f'[**{u}**]({u})', u), 2)
        # CommonMark leaves a legacy name without its semicolon literal.
        self.assertEqual(vb.cites(u.replace('/control', '&sol/control'), u), 0)

    def test_sources_grammar_rejections(self):
        # Round 4: raw HTML, reference links, references, escapes and encoded
        # unreserved characters cite a URL the raw text does not spell. Each
        # fails the grammar, even with the basis present; round 3 counted the
        # &#47; and <a href> spellings instead.
        u = self.url
        html_forms = {f'<a href={u}>t</a>': '<a> element', f'<a href="{u}">t</a>': '<a> element',
                      f'<A HREF={u}>t</A>': '<A> element', f'<img src={u}>': '<img> element',
                      f'<link href={u}>': '<link> element', f'<area href={u}>': '<area> element',
                      f'{u} <a': '<a> element', f'{u} <span title="x">t</span>':
                      '<span> tag with attributes', f'{u} <span\n  title=x>t</span>':
                      '<span> tag with attributes'}
        reference_forms = {f'[t][r] {u}': 'reference-style link', f'[t][] {u}': 'reference-style link'}
        entity = 'character reference or backslash escape'
        encoded = 'percent-encoded unreserved character'
        spelling_forms = {u.replace('/control', '&#47;control'): entity,
                          u.replace('https', '&#x68;ttps'): entity,
                          u.replace('://', '&colon;//'): entity,
                          f'[t]({u.replace("/control", "&#47;control")})': entity,
                          u.replace('/control', '\\/control'): entity,
                          f'{u} AT&amp;T': entity, f'{u}&amp;x=1': entity,
                          f'{u}&#46;json': entity, f'[t]&#40;{u})': entity,
                          f'\\[t]({u})': entity,
                          u.replace('control', 'c%6Fntrol'): encoded,
                          u.replace('control', 'c%6fntrol'): encoded,
                          f'{u} [t](m%61npage)': encoded, f'{u} https://x.example/%7Eu': encoded,
                          f'{u} https://x.example/a%2Db': encoded,
                          f'{u} https://x.example/a%2eb': encoded,
                          f'{u} https://x.example/a%5Fb': encoded,
                          f'{u} https://x.example/%30': encoded,
                          f'{u} https://x.example/%5A': encoded}
        for form, construct in {**html_forms, **reference_forms, **spelling_forms}.items():
            with self.subTest(form=form), self.assertRaisesRegex(
                    ValueError, r'Sources line \d+: .*' + re.escape(construct)
                    + '.*cite URLs as bare URLs, <autolinks> or inline'):
                self.check(f'- Product v1.0: {u}\n- Again v1.0: {form}')
        # The message names the file line, and no baseline entry excuses it.
        form = f'- Product v1.0: <a href={u}>t</a>'
        fp = vb.source_fingerprint('product', 'v1.0', u, form)
        with self.assertRaisesRegex(ValueError, r'^Sources line 19: raw HTML <a> element'):
            self.check(form, baseline=Counter({('fixture.md', fp): 1}))

    def check_with_prose(self, prose, sources):
        """Like check(), with prose added after the fixture's first paragraph."""
        u = self.url
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(u): u}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(u)]
        body = (BODY[:BODY.index('- Product')].replace(
                    'A documented control.', 'A documented control.\n\n' + prose)
                + sources + '\n')
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md')

    def test_reference_definitions_fail_guide_wide(self):
        # Round 5: with a definition anywhere, each of these Sources labels renders
        # as a link to u (checked against markdown-it-py's CommonMark renderer),
        # but the per-line shortcut check missed it and the basis-less item passed.
        u = self.url
        definition = 'reference definition; enrolled guides cite with inline links only'
        for prose, again in ((f'[ref doc]: {u}', '[ref\n  doc]'),          # split use
                             (f'[ref\ndoc]: {u}', '[ref doc]'),            # split definition
                             (f'[ref\\]doc]: {u}', '[ref\\]doc]'),        # escaped bracket
                             (f'[manual]: {u}', '[manual](updated September 2026)'),
                             (f'[Ref  Doc]: {u}', '[ref doc]'),
                             (f'- [r]: {u}', '[r]'), (f'> [r]:\n> {u}', '[r]'),
                             (f'   [r]: <{u}>', '[r]')):
            with self.subTest(prose=prose), self.assertRaisesRegex(
                    ValueError, r'^line \d+: ' + re.escape(definition)):
                self.check_with_prose(prose, f'- Product v1.0: {u}\n- Again: {again}')
        # A definition outside Sources fails with no use at all, and so does one in Sources.
        with self.assertRaisesRegex(ValueError, r'^line 8: ' + re.escape(definition)):
            self.check_with_prose(f'[r]: {u}', f'- Product v1.0: {u}')
        for sources in (f'- Product v1.0: {u}\n\n[r]: {u}', f'- Product v1.0: {u}\n  [r]:\n  {u}',
                        f'- Product v1.0: {u}\n  [r\n  s]: {u}'):
            with self.subTest(sources=sources), self.assertRaisesRegex(
                    ValueError, r'^line \d+: ' + re.escape(definition)):
                self.check(sources)
        # Passing controls: a bracketed word or an IPv6 literal is literal text.
        self.check(f'- Product v1.0: {u}; `loopback_users` [guest] and [::]')
        self.check_with_prose('Listen on [::]:443 and [guest].', f'- Product v1.0: {u}')

    def test_sources_lines_close_brackets_and_code_spans(self):
        # Round 5: constructs that span lines escaped the per-line grammar.
        u = self.url
        grammar = r'^Sources line \d+: .*'
        span = 'code span crosses a line in Sources'
        bracket = 'bracket left open or closed across a line in Sources'
        escaped = 'escaped bracket or backtick in Sources'
        # Each hides a live <a href> from same-line masking (markdown-it-py renders
        # it); the second has an even count of backticks on each line.
        for again, construct in ((f'` ``\n  ` <a href={u}>t</a> `', span),
                                 (f'`` `x`\n  ` `` <a href={u}>t</a> `', span),
                                 ('`one line', span), ('[ref\n  doc]', bracket),
                                 ('ref]', bracket), ('][', bracket), ('[a [b]', bracket),
                                 ('[t\n  more](https://x.example/)', bracket),
                                 ('[ref\\]doc]', escaped), ('\\[literal\\]', escaped),
                                 ('a \\( b', escaped), ('a \\) b', escaped),
                                 ('a \\` b', escaped), ('`\\[`', escaped)):
            with self.subTest(again=again), self.assertRaisesRegex(
                    ValueError, grammar + re.escape(construct)):
                self.check(f'- Product v1.0: {u}\n- Again: {again}')
        # Passing controls: an even run of backslashes escapes only itself; a
        # wrapped item without brackets across lines; ordinary [text](url); code
        # spans and bracket pairs that close on their own line.
        for sources in (f'- Product v1.0: {u}\n  Again C:\\\\[x] without a URL',
                        f'- Product v1.0 wrapped\n  across lines:\n  {u}',
                        f'- Product v1.0: [text]({u})',
                        f'- Product v1.0 (`[a`, `` ` ``, [b [c]]):\n  [text]({u})'):
            with self.subTest(sources=sources):
                self.check(sources)

    def test_sources_grammar_allowed_forms(self):
        u = self.url
        for sources in (f'- Product v1.0: {u}', f'- Product v1.0: <{u}>',
                        f'- Product v1.0: [text]({u})', f'- Product v1.0: [**{u}**]({u})',
                        f'- Product v1.0 reads <VAR>_FILE and `<GRPC_PORT>`: {u}',
                        f'- Product v1.0 (<PLACEHOLDER>, <br/>): {u}',
                        f'- Product v1.0 (`a&amp;b`, `m%61npage`, `<b id=x>`, `[t][r]`): {u}',
                        f'- Product v1.0: {u}\n  AT&amp;T and 50%41 on a line with no URL',
                        f'- Product v1.0: {u}\n\n  ```\n  <a href="x">&amp;</a> %61 [r]: x\n  ```',
                        f'- Product v1.0: {u} and https://x.example/pkg%40v1%20x%2F'):
            with self.subTest(sources=sources):
                self.check(sources)

    def test_raw_html_blocks_and_link_elements_fail_closed(self):
        # Round 6: a line that opens a CommonMark HTML block makes the following
        # lines raw HTML, where backticks are literal and entities decode, so a
        # masked code span hid a live link. markdown-it-py renders each <a> or
        # <iframe> below as raw HTML; all passed before this round.
        u = self.url
        grammar = r'^Sources line \d+: '
        block = 'raw HTML block in Sources'
        element = 'raw HTML <a> element'
        entity = 'https://example.com/co&#110;trol'
        for again, construct in (
                (f'<div>\n`<a href={u}>Again</a>`\n</div>', block),
                (f'<div>\n`<a href="{entity}">Again</a>`\n</div>', block),
                (f'\n<span>\n`<a href={u}>Again</a>`\n</span>', block),     # type 7
                (f'<div>\n`<iframe src={u}></iframe>`\n</div>', block),
                (f'</div> `<a href={u}>Again</a>`', block),
                (f'<?x ?> `<a href={u}>Again</a>`', block),
                (f'\n<!-- x --> `<iframe src="{entity}"></iframe>`', block),
                (f'\n<!--\n--> `<iframe src={u}></iframe>`', block),
                (f'   <div>\n`<a href={u}>Again</a>`', block),
                (f'- <div>\n  `<a href={u}>Again</a>`', block),
                (f'\n> <div>\n> `<a href={u}>Again</a>`', block),
                (f'<https://example.com/a b>', block),                      # not an autolink
                (f'- Again `<a href={u}>x</a>`', element),                  # no block needed
                (f'- Again `<A HREF="{entity}">x</A>`', 'raw HTML <A> element'),
                (f'- Again `<img src={u}>`', 'raw HTML <img> element'),
                (f'- Again `<link href={u}>`', 'raw HTML <link> element'),
                (f'- Again `<area href={u}>`', 'raw HTML <area> element')):
            with self.subTest(again=again), self.assertRaisesRegex(
                    ValueError, grammar + re.escape(construct)):
                self.check(f'- Product v1.0: {u}\n{again}')
        # Passing controls: a line-start autolink, a placeholder in a code span,
        # an IPv6 literal before a port, and a non-link tag shown as code.
        for sources in (f'- Product v1.0:\n  <{u}>', f'- <{u}> (Product v1.0)',
                        f'- Product v1.0 reads `<VAR>`: {u}',
                        f'- Product v1.0 listens on [::]:443: {u}',
                        f'- Product v1.0 (`<b title="x">`): {u}'):
            with self.subTest(sources=sources):
                self.check(sources)

    def check_heading(self, heading, sources, prose=''):
        """Like check_with_prose(), with the Sources heading line replaced."""
        u = self.url
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(u): u}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(u)]
        head = BODY[:BODY.index('- Product')]
        if prose:
            head = head.replace('A documented control.', 'A documented control.\n\n' + prose)
        body = head.replace('## Sources (checked September 2026)', heading) + sources + '\n'
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md')

    def test_round_seven_reproducers(self):
        # Round 7: each passed before this round while its markup renders a live
        # citation of u (or of w) that no basis-bearing Sources item counted.
        u, base, sources = self.url, f'- Product v1.0: {self.url}', '## Sources (checked September 2026)'
        after = 'text after the Sources heading'
        # (B1) Text or a link on the Sources heading line itself.
        for heading, construct in ((f'{sources} [Again]({u})', after), (f'{sources} {u}', after),
                                   (f'{sources} <{u}>', after), (f'{sources} ## {u} ##', after),
                                   (f'## See {u} sources (checked September 2026)',
                                    'text other than words before Sources')):
            with self.subTest(heading=heading), self.assertRaisesRegex(
                    ValueError, r'^line 17: ' + re.escape(construct)):
                self.check_heading(heading, base)
        # (B2) An HTML block or link element before the Sources heading.
        for prose, construct in ((f'<div>\n<h2>Sources</h2>\n<a href="{u}">Again</a>\n</div>',
                                  'raw HTML block'),
                                 (f'<details><summary>Sources</summary>\n\n`<a href={u}>x</a>`'
                                  '\n\n</details>', 'raw HTML block'),
                                 (f'See <a href="{u}">Again</a>.', 'raw HTML <a> element'),
                                 (f'See `<img src={u}>`.', 'raw HTML <img> element')):
            with self.subTest(prose=prose), self.assertRaisesRegex(
                    ValueError, r'^line 8: ' + re.escape(construct)):
                self.check_with_prose(prose, base)
        # (B3) A heading inside a list item: CommonMark keeps it in the item, so it
        # no longer ends the Sources range, and it is refused anywhere.
        with self.assertRaisesRegex(ValueError, r'unsupported Sources container.*\(2 in Sources'):
            self.check(f'{base}\n- Again\n  ## More: <{u}>')
        for prose in ('- item\n  ## Note', '- item\n\n   ## Note', '\t## Note'):
            with self.subTest(prose=prose), self.assertRaisesRegex(
                    ValueError, r'^line \d+: indented heading'):
                self.check_with_prose(prose, base)
        body = f'# T\n\n{sources}\n\n{base}\n- Again\n  ## More\n- {u}\n\n## Next\n\n{u}\n'
        self.assertEqual(vb.cites(vb.raw_sources(body, headings(body)), u), 2)
        # (B4) An angle-bracket destination, whose spaces render percent-encoded.
        w = 'https://example.com/con%20trol'
        angle = 'angle-bracket link destination'
        spaced = 'https://example.com/con trol'
        for again in (f'[t](<{spaced}>\n  )', f'[t](<{spaced}>)', f'[t]( <{spaced}> "title")'):
            with self.subTest(again=again), self.assertRaisesRegex(
                    ValueError, r'^line \d+: ' + re.escape(angle)):
                self.check_urls(f'- Product v1.0: {w}\n- Again: {again}', [w])
        for prose in (f'See [t](<{u}>).', f'See [t](\n<{u}>).'):
            with self.subTest(prose=prose), self.assertRaisesRegex(
                    ValueError, r'^line 8: ' + re.escape(angle)):
                self.check_with_prose(prose, base)
        # Passing controls: a numbered, worded Sources heading with a closing
        # sequence; ](< shown in a code span; a heading-like #tag; ordinary links.
        for heading in ('## 9. Standards and sources (checked September 2026)',
                        '## Sources (checked September 2026) ##',
                        '### Sources (checked September 2026)  '):
            with self.subTest(heading=heading):
                self.check_heading(heading, base)
        self.check_with_prose('Write `[t](<u>)` and `<b>`; #tag\n  #tag', base)
        self.check(f'{base}\n- Also v1.0 [text]({u})')

    def test_scheme_and_host_match_case_insensitively(self):
        # Round 6: HTTPS://, Https:// and an uppercase host dereference to the same
        # resource, so they cite u; an uppercase path is another resource.
        u = self.url
        for form in ('HTTPS://example.com/control', 'Https://example.com/control',
                     'https://EXAMPLE.com/control', 'HTTPS://Example.COM/control',
                     '[t](HTTPS://example.com/control)', '<Https://EXAMPLE.com/control>'):
            with self.subTest(form=form):
                self.assertEqual(vb.cites(form, u), 1)
                self.check(f'- Product v1.0: {form}')
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product v1.0: {u}\n- Again: {form}')
        for form in ('https://example.com/CONTROL', 'https://example.com/Control'):
            with self.subTest(form=form):
                self.assertEqual(vb.cites(form, u), 0)
                with self.assertRaisesRegex(ValueError, 'source URL absent from Sources'):
                    self.check(f'- Product v1.0: {form}')
        self.assertEqual(vb.cites('https://Example.com:8443/a', 'https://example.com:8443/a'), 1)
        self.assertEqual(vb.cites('https://example.com:8443/A', 'https://example.com:8443/a'), 0)

    def test_closing_emphasis_counts_as_citation(self):
        # Round 4: _CLOSES read the closing delimiter plus a letter as URL continuation.
        u = self.url
        for text in (f'**{u}**x', f'~~{u}~~x', f'_{u}_x', f'*{u}*x', u + '~x', f'__{u}__x'):
            with self.subTest(text=text):
                self.assertEqual(vb.cites(text, u), 1)
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product v1.0: {u}\n- Again: {text}')
        for longer in (u + '_v2', f'**{u}_v2**', u + '_.x'):
            with self.subTest(longer=longer):
                self.assertEqual(vb.cites(longer, u), 0)
        # A real URL ending in * still matches itself, and also cites the shorter URL.
        star = u + '*'
        for text in (star, f'{star}.', f'[t]({star})', f'**{star}**'):
            with self.subTest(text=text):
                self.assertEqual(vb.cites(text, star), 1)
                self.check_urls(f'- Product v1.0: {text}', [star])
        self.assertEqual(vb.cites(star, u), 1)

    def test_known_url_is_not_a_prefix_match(self):
        u = self.url
        for longer in (u + '/v2', u + '.json', u + 'x', u + '_v2', u + '-x', u + '?q=1',
                       u + '#frag', u + '%20', u + '.,x', u + '&x=1', u + '%2Fx',
                       'https://proxy.example/?u=' + u,
                       'https://archive.example/' + u, 'x' + u):
            with self.subTest(longer=longer):
                self.assertEqual(vb.cites(longer, u), 0)
                with self.assertRaisesRegex(ValueError, 'source URL absent'):
                    self.check(f'- Product v1.0: {longer}')
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product: {u}\n- Other v1.0: {u}/v2 and {u}.json')

    def test_known_url_before_punctuation_and_delimiters(self):
        u = self.url
        for text in (u + '.', u + ',', u + ';', u + ':', u + '?', u + '!', u + ')', f'({u})',
                     f'({u}).', f'"{u}"', f"'{u}'", f'**{u}**', f'`{u}`', f'<{u}>', f'[{u}]',
                     u + '...', u + '. Next', u + ',\nwrapped', f'_{u}_', f'~~{u}~~', u + '\n'):
            with self.subTest(text=text):
                self.assertEqual(vb.cites(text, u), 1)
                self.check(f'- Product v1.0: {text}')
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product v1.0: {u}\n- Again: {text}')

    def test_known_url_ending_in_delimiter_passes(self):
        # Round 2 stripped trailing _ ~ * from bare URLs, so these never matched.
        for url in (self.url + '_', self.url + '~', self.url + '*', self.url + '_(x)'):
            for text in (url, url + '.', f'**{url}**', f'[t]({url})'):
                with self.subTest(url=url, text=text):
                    self.assertEqual(vb.cites(text, url), 1)
                    self.check_urls(f'- Product v1.0: {text}', [url])
                    with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                        self.check_urls(f'- Product v1.0: {text}\n- Again: {text}', [url])

    def test_url_with_character_reference_is_refused(self):
        url = self.url + '?a=1&amp;b=2'
        with self.assertRaisesRegex(ValueError, 'character reference or backslash escape'):
            self.check_urls(f'- Product v1.0: {url}', [url])
        # A code span escapes the grammar, so the component URL is checked itself.
        with self.assertRaisesRegex(ValueError, 'source URL contains an escape or entity'):
            self.check_urls(f'- Product v1.0: `{url}`', [url])
        url = self.url.replace('control', 'c%6Fntrol')
        with self.assertRaisesRegex(ValueError, 'percent-encodes an unreserved character'):
            self.check_urls(f'- Product v1.0: `{url}`', [url])

    def test_setext_lookalike_does_not_truncate_sources(self):
        # Codex round 2: "- item" over a marker-only "-" reads as a Setext heading
        # in check_guide_shape.headings(), which ended section_body() early.
        with self.assertRaisesRegex(
                ValueError, re.escape(self.url) + ' cited in an unsupported Sources container'):
            self.check(f'- Product v1.0: {self.url}\n- Additional v1.0: {self.url}\n-\n'
                       f'  Again: {self.url}')
        # Passing control: a later ATX section still ends Sources for the count.
        self.check(f'- Product v1.0: {self.url}\n\n## Later\n\nProse: {self.url}')

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
        raw = raw.replace('control (REASONED; product): Requires authentication.',
                          'control (REASONED; product): Stale summary.')
        raw += 'A reviewed qualification.\n'
        result = vb.rebound(raw)
        self.assertIn('control (REASONED; product): Stale summary.', result)
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


class RenderedSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.parser = gate_parser(required=True)
        except ParserUnavailable as exc:
            if os.environ.get('CI'):
                raise RuntimeError(f'pinned parser unavailable in CI: {exc}') from exc
            raise unittest.SkipTest(f'pinned parser unavailable: {exc}') from exc

    def check(self, sources, url='https://example.com/control', prose='', use_parser=True,
              basis='v1.0', baseline=None):
        data = fixture()
        data['components']['product']['basis'] = basis
        data['components']['product']['sources'] = {vb.source_id(url): url}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
        body = BODY.replace('## Verify', prose + '\n\n## Verify' if prose else '## Verify')
        body = body[:body.index('- Product')] + sources + '\n'
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md', baseline,
                          parser=self.parser if use_parser else None)

    def test_allowed_links_and_emphasis_are_counted(self):
        url = 'https://example.com/control'
        for target in (f'<{url}>', f'[doc]({url})', f'*{url}*'):
            with self.subTest(target=target):
                self.check(f'- Product v1.0: {target}', url)
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(f'- Product v1.0: {url}\n- Again: {target}', url)

    def test_existing_bans_apply_with_and_without_parser(self):
        url = 'https://example.com/control'
        cases = (
            (f'- Product v1.0: [doc](https://example.com/con&#116;rol)', '',
             'character reference or backslash escape on a line with a URL or link'),
            (f'- Product v1.0: [doc](https://example.com/con\\-trol)', '',
             'character reference or backslash escape on a line with a URL or link'),
            (f'- Product v1.0: [doc](https://example.com/%63ontrol)', '',
             'percent-encoded unreserved character on a line with a URL or link'),
            (f'- Product v1.0: {url}', f'[ref]: {url}', 'reference definition'),
            (f'- Product v1.0: {url}\n- Again: [doc][ref]', '', 'reference-style link'),
            (f'- Product v1.0: {url} <span title="x">tag</span>', '',
             'raw HTML <span> tag with attributes'),
            (f'- Product v1.0: {url} <a href="{url}">Again</a>', '',
             'raw HTML <a> element'),
        )
        for sources, prose, diagnostic in cases:
            with self.subTest(sources=sources, prose=prose):
                errors = []
                for use_parser in (False, True):
                    with self.assertRaisesRegex(ValueError, re.escape(diagnostic)) as caught:
                        self.check(sources, url, prose, use_parser)
                    errors.append(str(caught.exception))
                self.assertEqual(*errors)

    def test_raw_basis_is_required_with_and_without_parser(self):
        url = 'https://example.com/control'
        for basis in ('v1.**0**', 'v1&#46;0', 'v1\\.0'):
            sources = f'- Product {basis}\n  [doc]({url})'
            with self.subTest(basis=basis):
                messages = []
                for use_parser in (False, True):
                    with self.assertRaises(ValueError) as caught:
                        self.check(sources, use_parser=use_parser)
                    messages.append(str(caught.exception))
                self.assertEqual(*messages)
                self.assertIn("product: basis 'v1.0' absent from Sources item", messages[0])

    def test_normalized_link_text_cannot_supply_raw_basis(self):
        cases = (
            ('https://example.bücher/doc', 'kva',
             '- [doc](https://example.bücher/doc)'),
            ('https://bücher.example/doc', 'bcher',
             '- Docs: <https://bücher.example/doc>'),
            ('https://ü@example.com/doc', 'BC',
             '- [doc](https://ü@example.com/doc)'),
            ('https://example.com/Product%20v1.0/doc', 'Product v1.0',
             '- Docs: <https://example.com/Product%20v1.0/doc>'),
        )
        for url, basis, sources in cases:
            with self.subTest(sources=sources):
                messages = []
                for use_parser in (False, True):
                    with self.assertRaises(ValueError) as caught:
                        self.check(sources, url=url, basis=basis, use_parser=use_parser)
                    messages.append(str(caught.exception))
                self.assertEqual(*messages)
                self.assertIn(f"basis {basis!r} absent from Sources item", messages[0])

    def test_basis_in_link_label_keeps_its_boundary(self):
        url = 'https://example.com/control'
        self.check(f'- [Product v1.0]({url}).')
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product v1.0. [doc]({url})')

    def test_opening_link_label_boundary(self):
        url = 'https://example.com/control'
        self.check(f'- Product v1.0[doc]({url})')
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product av1.0[doc]({url})')

    def test_cited_href_only_supplies_its_own_basis(self):
        cited = 'https://example.com/control'
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- [doc]({cited}) [other](https://other.example/v1.0)')
        self.check(f'- [doc](https://example.com/v1.0)', url='https://example.com/v1.0')

    def test_basis_only_in_declared_link_target(self):
        for basis, url in (('café', 'https://example.com/café'),
                           ('a|b', 'https://example.com/a|b')):
            with self.subTest(basis=basis):
                for use_parser in (False, True):
                    self.check(f'- [doc]({url})', url=url, basis=basis,
                               use_parser=use_parser)

    def test_basis_does_not_borrow_declared_url_capitals(self):
        cases = (
            ('https://v2-docs.example.com/doc', 'v2',
             '- Docs: https://V2-docs.example.com/doc'),
            ('https://v2-docs.example.com/doc', 'v2',
             '- [doc](https://V2-docs.example.com/doc)'),
            ('https://v2-docs.example.com/doc', 'v2',
             '- Docs: <https://V2-docs.example.com/doc>'),
            ('https://v1@example.com/doc', 'v1',
             '- Docs: https://V1@example.com/doc'),
            ('https://example.com/doc', 'https',
             '- Docs: HTTPS://example.com/doc'),
        )
        for url, basis, sources in cases:
            with self.subTest(sources=sources):
                messages = []
                for use_parser in (False, True):
                    with self.assertRaises(ValueError) as caught:
                        self.check(sources, url=url, basis=basis,
                                   use_parser=use_parser)
                    messages.append(str(caught.exception))
                self.assertEqual(*messages)
                self.assertIn('basis', messages[0])
                self.assertIn('absent from Sources item', messages[0])

    def test_base_computed_case_baseline_stays_valid(self):
        url = 'https://v2-docs.example.com/doc'
        basis = 'v2'
        sources = '- Docs: https://V2-docs.example.com/doc'
        fingerprint = vb.source_fingerprint('product', basis, url, sources)
        baseline = {('fixture.md', fingerprint): 1}
        for use_parser in (False, True):
            with self.subTest(use_parser=use_parser):
                self.check(sources, url=url, basis=basis, baseline=baseline,
                           use_parser=use_parser)

    def test_raw_baseline_is_consumed_once_in_parser_path(self):
        url = 'https://example.com/control'
        sources = f'- Product: {url}'
        fingerprint = vb.source_fingerprint('product', 'v1.0', url, sources)
        baseline = {('fixture.md', fingerprint): 1}
        for use_parser in (False, True):
            with self.subTest(use_parser=use_parser):
                self.check(sources, baseline=baseline, use_parser=use_parser)

    def test_repeated_citations_count_once_per_violating_item(self):
        url = 'https://example.com/control'
        cases = (
            ('two links', f'- Product: [first]({url}) and [second]({url})', 1),
            ('link and bare', f'- Product: [doc]({url}) and {url}', 1),
            ('autolink and bare', f'- Product: <{url}> and {url}', 1),
            ('bare and emphasized', f'- Product: {url} and *{url}*', 1),
            ('wrapped citation', f'- Product: [doc]({url})\n  and {url}', 1),
            ('two distinct items', f'- Product: [doc]({url}) and {url}\n'
                                   f'- Product: [doc]({url}) and {url}', 2),
        )
        for label, sources, expected in cases:
            with self.subTest(label=label):
                body = BODY[:BODY.index('- Product')] + sources + '\n'
                entries = vb.source_entries(vb.raw_sources(body, headings(body)))
                data = fixture()
                data['components']['product']['sources'] = {vb.source_id(url): url}
                data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
                counts = Counter(fp for fp, _ in vb.source_violations(data, entries))
                self.assertEqual(sum(counts.values()), expected)
                self.assertEqual(len(counts), 1)
                baseline = {('fixture.md', fp): count for fp, count in counts.items()}
                for use_parser in (False, True):
                    with self.subTest(use_parser=use_parser):
                        self.check(sources, baseline=baseline, use_parser=use_parser)

        other = 'https://example.com/other'
        sources = f'- Product: [doc]({url}) and [other]({other}) and {other}'
        body = BODY[:BODY.index('- Product')] + sources + '\n'
        entries = vb.source_entries(vb.raw_sources(body, headings(body)))
        data = fixture()
        data['components']['product']['sources'] = {
            vb.source_id(candidate): candidate for candidate in (url, other)}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
        counts = Counter(fp for fp, _ in vb.source_violations(data, entries))
        self.assertEqual(len(counts), 2)
        self.assertEqual(sorted(counts.values()), [1, 1])
        baseline = {('fixture.md', fp): count for fp, count in counts.items()}
        for use_parser in (False, True):
            with self.subTest(case='two URLs in one item', use_parser=use_parser):
                data['body_sha256'] = vb.digest(body)
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    vb.updated(document(data, body), 'fixture.md', parser=(
                        self.parser if use_parser else None))
                vb.updated(document(data, body), 'fixture.md', baseline,
                           self.parser if use_parser else None)

        sources = (f'- Product: [doc]({url})\n'
                   f'- Product v1.0: [other]({url})')
        body = BODY[:BODY.index('- Product')] + sources + '\n'
        entries = vb.source_entries(vb.raw_sources(body, headings(body)))
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(url): url}
        counts = Counter(fp for fp, _ in vb.source_violations(data, entries))
        self.assertEqual(sum(counts.values()), 1)
        baseline = {('fixture.md', fp): count for fp, count in counts.items()}
        for use_parser in (False, True):
            with self.subTest(case='violating and satisfying items', use_parser=use_parser):
                with self.assertRaisesRegex(ValueError, 'basis.*absent'):
                    self.check(sources, use_parser=use_parser)
                self.check(sources, baseline=baseline, use_parser=use_parser)

        same_item = f'- Product: [doc]({url}) and v1.0 {url}'
        same_body = BODY[:BODY.index('- Product')] + same_item + '\n'
        same_entries = vb.source_entries(vb.raw_sources(same_body, headings(same_body)))
        self.assertEqual(list(vb.source_violations(data, same_entries)), [])
        for use_parser in (False, True):
            with self.subTest(case='two occurrences in a satisfying item',
                              use_parser=use_parser):
                self.check(same_item, use_parser=use_parser)

        # The raw path counts the image URL; the parser cannot use an image as a citation.
        image_sources = sources.replace(f'[other]({url})', f'![other]({url})')
        image_body = BODY[:BODY.index('- Product')] + image_sources + '\n'
        image_entries = vb.source_entries(vb.raw_sources(image_body, headings(image_body)))
        image_counts = Counter(fp for fp, _ in vb.source_violations(data, image_entries))
        image_baseline = {('fixture.md', fp): count for fp, count in image_counts.items()}
        self.check(image_sources, baseline=image_baseline, use_parser=False)
        with self.assertRaisesRegex(ValueError, 'absent from rendered Sources item'):
            self.check(image_sources, baseline=image_baseline, use_parser=True)

    def test_raw_baseline_stays_valid_when_rendered_basis_matches(self):
        url = 'https://example.com/control'
        sources = f'- Product v1.**0**\n  [doc]({url})'
        fingerprint = vb.source_fingerprint('product', 'v1.0', url, sources)
        baseline = {('fixture.md', fingerprint): 1}
        for use_parser in (False, True):
            with self.subTest(use_parser=use_parser):
                self.check(sources, baseline=baseline, use_parser=use_parser)

    def test_verify_markup_diagnostic_precedes_rendered_failure(self):
        url = 'https://example.com/control'
        sources = f'- Product v1.0: {url}'
        messages = []
        for use_parser in (False, True):
            with self.assertRaises(ValueError) as caught:
                self.check(sources, prose='<pre>', use_parser=use_parser)
            messages.append(str(caught.exception))
        self.assertEqual(*messages)
        self.assertIn('invalid Verify markup', messages[0])

    def test_href_path_case_remains_exact(self):
        url = 'https://example.com/Control'
        self.assertEqual(vb.rendered_cites('https://EXAMPLE.com/control', url, True,
                                           self.parser), 0)
        with self.assertRaisesRegex(ValueError, 'source URL absent'):
            self.check(f'- Product v1.0: `{url}` [doc](https://EXAMPLE.com/control)', url=url)
        self.check('- Product v1.0: [doc](https://EXAMPLE.com/Control)', url=url)

    def test_normalized_link_target(self):
        for url in ('https://example.com/café', 'https://bücher.example/control',
                    'https://example.com/a|b', 'https://example.com/a[b]'):
            with self.subTest(url=url):
                self.check(f'- Product v1.0: [doc]({url})', url=url)

    def test_outside_list_item_has_base_container_message(self):
        url = 'https://example.com/control'
        sources = f'- Product v1.0: {url}\n\nLoose v1.0: {url}'
        messages = []
        for use_parser in (False, True):
            with self.assertRaisesRegex(ValueError, 'unsupported Sources container') as caught:
                self.check(sources, use_parser=use_parser)
            messages.append(str(caught.exception))
        self.assertEqual(*messages)

    def test_normalized_link_in_loose_prose_reaches_rendered_backstop(self):
        url = 'https://bücher.example/control'
        sources = (f'- Product v1.0: {url}\n\n'
                   'Loose v1.0: [doc](https://xn--bcher-kva.example/control)')
        self.check(sources, url=url, use_parser=False)
        with self.assertRaisesRegex(ValueError, 'unsupported Sources container'):
            self.check(sources, url=url, use_parser=True)

    def test_base_container_and_presence_diagnostics_in_both_paths(self):
        url = 'https://example.com/control'
        first = f'- Product v1.0: {url}'
        cases = (
            first + f'\n- - Again v1.0: {url}',
            f'- - Product v1.0: {url}',
            first + f'\n- # Again v1.0 {url}',
            first + f'\n> - Again v1.0: {url}',
            f'> - Product v1.0: {url}',
            first + f'\n- > Again v1.0: {url}',
            first + f'\n\nIntro\n\n    Again: {url}',
            first + f'\n\n```text\nAgain: {url}\n```',
            '- Product v1.0\n-\n  Again v1.0: ' + url,
            first + f'\n- Other\n-\n  Again v1.0: {url}',
            first + f'\n- Again: ![doc]({url})',
            f'- Product v1`.0`: {url}',
            f'- Product v1<br>.0: {url}',
            f'- Product: {url}\n  > v1.0',
            (f'- Product: {url}\n\n  | Field | Value |\n'
             '  | --- | --- |\n  | Basis | v1.0 |'),
        )
        for sources in cases:
            with self.subTest(sources=sources):
                messages = []
                for use_parser in (False, True):
                    with self.assertRaises(ValueError) as caught:
                        self.check(sources, use_parser=use_parser)
                    messages.append(str(caught.exception))
                self.assertEqual(*messages)

    def test_existing_unsupported_containers_in_both_paths(self):
        url = 'https://example.com/control'
        for sources in (f'- Product v1.0: {url}\n- - Again: {url}',
                        f'- Product v1.0: {url}\n> - Again: {url}',
                        f'- Product v1.0: {url}\n\nAgain: {url}'):
            with self.subTest(sources=sources):
                messages = []
                for use_parser in (False, True):
                    with self.assertRaises(ValueError) as caught:
                        self.check(sources, use_parser=use_parser)
                    messages.append(str(caught.exception))
                self.assertEqual(*messages)

    def test_code_spans_are_not_citations(self):
        url = 'https://example.com/control'
        with self.assertRaisesRegex(ValueError, 'source URL absent'):
            self.check(f'- Product v1.0: `{url}`')
        self.check(f'- Product v1.0: `{url}`', use_parser=False)
        for use_parser in (False, True):
            with self.subTest(use_parser=use_parser), self.assertRaisesRegex(
                    ValueError, 'basis.*absent'):
                self.check(f'- Product v1.0: {url}\n- Example only: `{url}`',
                           use_parser=use_parser)

    def test_link_label_is_not_a_citation(self):
        url = 'https://example.com/control'
        with self.assertRaisesRegex(ValueError, 'source URL absent from Sources'):
            self.check(f'- Product v1.0: [{url}](https://other.example/doc)')
        self.check(f'- Product v1.0: [{url}](https://other.example/doc)', use_parser=False)

    def test_html_comment_remains_banned(self):
        url = 'https://example.com/control'
        errors = []
        for use_parser in (False, True):
            with self.assertRaisesRegex(ValueError, 'HTML comment outside fence or code span') as caught:
                self.check(f'- Product v1.0: {url}\n- Again <!-- {url} -->',
                           use_parser=use_parser)
            errors.append(str(caught.exception))
        self.assertEqual(*errors)

    def test_inline_link_destination_wraps_across_lines(self):
        url = 'https://example.com/control'
        target = f'[doc](\n  {url})'
        self.check(f'- Product v1.0: {target}')
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product v1.0: {url}\n- Again: {target}')

    def test_softbreak_splits_basis(self):
        url = 'https://example.com/control'
        with self.assertRaisesRegex(ValueError, 'basis.*absent'):
            self.check(f'- Product v1\n  .0: {url}')

    def test_non_lf_line_boundaries_fail_closed(self):
        url = 'https://example.com/control'
        sources = f'- Product v1.0: {url}'
        for boundary in '\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029':
            with self.subTest(boundary=repr(boundary)):
                body = BODY.replace('- Product v1.0:',
                                    boundary + '\n- Product v1.0:')
                body = body[:body.index('- Product')] + sources + '\n'
                data = fixture()
                data['components']['product']['sources'] = {vb.source_id(url): url}
                data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
                data['body_sha256'] = vb.digest(body)
                with self.assertRaisesRegex(ValueError, 'unsupported line boundary'):
                    vb.updated(document(data, body), 'fixture.md', parser=self.parser)

    def test_line_boundary_does_not_preempt_raw_failure(self):
        url = 'https://example.com/control'
        body = BODY.replace('A documented control.', 'A documented\u2028\u2028control.')
        body = body.replace('## Sources (checked September 2026)\n\n'
                            '- Product v1.0: https://example.com/v1.0#control',
                            f'## Sources (checked September 2026)\n- Again: {url}\n'
                            f'### Detail\n- Product v1.0: {url}')
        data = fixture()
        data['components']['product']['sources'] = {vb.source_id(url): url}
        data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
        data['body_sha256'] = vb.digest(body)
        raw = document(data, body)
        occurrences, _ = vb.rendered_sources(body, headings(body), self.parser)
        self.assertEqual(len(occurrences), 1)  # The basisless first item is invisible.
        messages = []
        for parser in (None, self.parser):
            with self.assertRaises(ValueError) as caught:
                vb.updated(raw, 'fixture.md', parser=parser)
            messages.append(str(caught.exception))
        self.assertEqual(*messages)
        self.assertIn('basis', messages[0])
        self.assertIn('absent from Sources item', messages[0])

    def test_image_basis_violation_cannot_be_baselined_with_parser(self):
        url = 'https://example.com/control'
        first = f'- Product v1.0: {url}\n'
        for item in (f'- Again: ![doc]({url})',):
            sources = first + item
            fingerprint = vb.source_fingerprint('product', 'v1.0', url, item)
            baseline = Counter({('fixture.md', fingerprint): 1})
            with self.subTest(item=item):
                self.check(sources, baseline=baseline, use_parser=False)
                with self.assertRaisesRegex(ValueError, 'absent from rendered Sources item'):
                    self.check(sources, baseline=baseline)

    def test_complex_item_fingerprints_match_fallback(self):
        url = 'https://example.com/control'
        for sources in (
                f'- Product: {url}\n  > v1.0',
                (f'- Product: {url}\n\n  | Field | Value |\n'
                 '  | --- | --- |\n  | Basis | v1.0 |')):
            with self.subTest(sources=sources):
                body = BODY[:BODY.index('- Product')] + sources + '\n'
                heads = headings(body)
                raw = vb.raw_sources(body, heads)
                old = vb.source_entries(raw)
                _, items = vb.rendered_sources(body, heads, self.parser)
                self.assertEqual([entry for entry, _ in items], old)
                fp = vb.source_fingerprint('product', 'v1.0', url, old[0])
                baseline = Counter({('fixture.md', fp): 1})
                data = fixture()
                data['components']['product']['sources'] = {vb.source_id(url): url}
                data['claims']['control']['sources'] = ['product:' + vb.source_id(url)]
                data['body_sha256'] = vb.digest(body)
                vb.updated(document(data, body), 'fixture.md', baseline, self.parser)

    def test_current_corpus_agrees_on_occurrence_counts(self):
        differences = []
        for path in vb.paths():
            data, full = vb.split(path.read_text(encoding='utf-8'))
            body = vb.without_summary(full)
            heads = headings(body)
            raw = vb.raw_sources(body, heads)
            occurrences, _ = vb.rendered_sources(body, heads, self.parser)
            for component in data['components'].values():
                for url in component['sources'].values():
                    old = vb.cites(raw, url)
                    new = sum(vb.rendered_cites(value, url, link, self.parser)
                              for value, _, link in occurrences)
                    if old != new:
                        differences.append((path.name, url, old, new))
        self.assertEqual(differences, [])

    def test_current_corpus_item_fingerprints_match_fallback(self):
        differences = []
        for path in vb.paths():
            data, full = vb.split(path.read_text(encoding='utf-8'))
            body = vb.without_summary(full)
            heads = headings(body)
            raw = vb.raw_sources(body, heads)
            _, items = vb.rendered_sources(body, heads, self.parser)
            for name, component in data['components'].items():
                for url in component['sources'].values():
                    old = Counter(vb.source_fingerprint(name, component['basis'], url, entry)
                                  for entry in vb.source_entries(raw) if vb.cites(entry, url))
                    new = Counter(vb.source_fingerprint(name, component['basis'], url, entry)
                                  for entry, _ in items if vb.cites(entry, url))
                    if old != new:
                        differences.append((path.name, name, url))
        self.assertEqual(differences, [])


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


class TwoSectionTests(unittest.TestCase):
    def legacy(self, body=BODY):
        data = fixture()
        data['body_sha256'] = vb.digest(body)
        return vb.updated(document(data, body), 'fixture.md')

    def test_round_trip_digest_endings_and_both_bundles(self):
        for ending in ('', '\n', '\n\n', '\n \n'):
            body = BODY.rstrip('\n') + ending
            legacy = self.legacy(body)
            current = vb.migrated(legacy, 'fixture.md')
            data, full = vb.split(current)
            self.assertEqual(vb.without_summary(full), body)
            self.assertEqual(data, vb.split(legacy)[0])
            self.assertEqual(data['body_sha256'], vb.digest(body))
            self.assertEqual(vb.updated(current, 'fixture.md'), current)
            vb.validate(data, full, 'fixture.md')
            self.assertEqual(body_lines(current), current.splitlines())
            self.assertTrue(current.startswith('# Fixture\n\nWritten against Product v1.0.'))
            self.assertTrue(current.endswith(vb.END + '\n'))
            self.assertIn('/main/fixture.md\nin full', current)
            self.assertIn('compare the versions listed below', current)
            self.assertEqual(current.count('Metadata reviewed'), 1)
            self.assertIn('Claims (full source mapping in the JSON block below):', current)
            self.assertEqual(vb.without_summary(current + '\n \t\n'), body)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'fixture.md'
                for text in (legacy, current):
                    path.write_bytes(text.encode('utf-8'))
                    result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'),
                                             '--bundle', str(path)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, vb.split(text)[1])

    def test_header_counts_folding_merging_and_limits(self):
        data = fixture()
        self.assertIn('1 claim, all reasoned from cited sources.', vb.header(data))
        data['claims']['other'] = dict(data['claims']['control'], status='DEMONSTRATED')
        self.assertIn('2 claims: 1 demonstrated by a check that ran and 1 reasoned', vb.header(data))
        data['claims']['control']['status'] = 'DEMONSTRATED'
        self.assertIn('2 claims, all demonstrated by a check that ran.', vb.header(data))
        def components(pairs):
            data['components'] = {f'c{i}': dict(name=name, basis=basis, sources={SID: URL})
                                  for i, (name, basis) in enumerate(pairs)}
            return vb.versions_sentence(data)
        self.assertEqual(components([('Product', 'v1'), ('Product', 'v2'), ('Product', 'v3'),
                                     ('Snapshot', 'a' * 7), ('Docs', 'unknown')]),
                         'Written against Product v1, v2, and v3; 1 further source is pinned '
                         'to a commit and 1 carries no recorded version.')
        self.assertIn('Product v1 and v2.', components([('Product', 'v1'), ('Product', 'v2')]))
        self.assertIn('No release versions are recorded', components([('Docs', 'unknown'),
                                                                     ('Pin', 'a' * 40)]))
        self.assertEqual(components([('Notice', '2025')]), 'Written against Notice 2025.')
        self.assertIn('&lt;&amp;&#124;&#96;&gt;', components([('<&|`>', 'v1')]))
        sentence = components([(f'Product{i}', 'v1') for i in range(10)])
        self.assertIn('plus 2 more recorded bases', sentence)
        self.assertNotIn('Product8', sentence)
        sentence = components([(f'Product{i}' + 'x' * 90, 'v1') for i in range(8)])
        self.assertLessEqual(len(sentence), 400)
        self.assertIn('plus 5 more recorded bases', sentence)
        with self.assertRaisesRegex(ValueError, '400-character'):
            components([('x' * 400, 'v1')])

    def test_malformed_mixed_and_stale_sections(self):
        current = vb.migrated(self.legacy(), 'fixture.md')
        mutations = (
            current + 'After END\n', current.replace(vb.END, vb.END + ' '),
            current + vb.START, current.replace(vb.START, ''),
            current.replace('## ' + vb.NOTE_TITLE, '## Verify'),
            current.replace('```text', '```bash'), current.replace('````json', '```json'),
            current.replace('\n````\n', '\n```\n'),
            current.replace('**Version basis**', '### Other'),
            current.replace('Read the secureconfig guide at', '## Verify'),
            current.replace('**Version basis**', '<b>Other</b>'),
            current.replace('**Version basis**', '```sh\necho hidden\n```'),
            current.replace('"schema": 1,', '"schema": 1, "schema": 1,'),
            current.replace('"schema": 1,', '"schema": NaN,'),
            vb.front_matter(fixture()) + current,
        )
        for text in mutations:
            with self.subTest(text=text[-120:]), self.assertRaises(ValueError):
                vb.updated(text, 'fixture.md')
        for text in (current.replace('Written against Product', 'Written against Other', 1),
                     current.replace(vb.header(fixture()) + '\n\n', '', 1)):
            with self.assertRaisesRegex(ValueError, 'generated header'):
                vb.updated(text, 'fixture.md')
        stale = current.replace('Requires authentication.', 'Wrong.', 1)
        self.assertNotEqual(vb.updated(stale, 'fixture.md'), stale)
        with patch.object(vb, 'front_matter', return_value='---\nversion_basis: {\n````\n}\n---\n'):
            with self.assertRaisesRegex(ValueError, 'generated JSON contains a fence'):
                vb.render(fixture(), 'fixture.md')

    def test_migration_refuses_digest_change(self):
        with self.assertRaisesRegex(ValueError, 'immediately follow the H1'):
            vb.migrated(self.legacy(BODY.replace('# Fixture\n\n', '# Fixture\nIntro\n\n')),
                        'fixture.md')
        renderer = vb.two_section
        def changed(data, body, guide):
            return renderer(data, body + 'Extra prose.\n', guide)
        with patch.object(vb, 'two_section', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'migration changed digested body'):
                vb.migrated(self.legacy(), 'fixture.md')
        with self.assertRaisesRegex(ValueError, 'body changed'):
            vb.migrated(self.legacy() + 'Unreviewed.\n', 'fixture.md')

    def test_rebind_and_diagnostic_lines_in_both_layouts(self):
        legacy = self.legacy()
        for text in (legacy, vb.migrated(legacy, 'fixture.md')):
            changed = text.replace('A documented control.', 'A reviewed control.')
            rebound = vb.rebound(changed, 'fixture.md')
            data, full = vb.split(changed)
            expected = vb.digest(vb.without_summary(full))
            self.assertEqual(rebound, changed.replace(data['body_sha256'], expected, 1))
            self.assertEqual(vb.updated(rebound, 'fixture.md'), rebound)
            bad = text.replace('- Product v1.0:', '- Product v1.0 <a href=x>bad</a>:')
            line = next(i for i, value in enumerate(bad.split('\n'), 1) if value.startswith('- Product'))
            with self.assertRaisesRegex(ValueError, f'Sources line {line}: raw HTML <a>'):
                vb.rebound(bad, 'fixture.md')

    def test_enrollment_and_cli_preflight(self):
        legacy = self.legacy()
        current = vb.migrated(legacy, 'fixture.md')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'tools/version_basis_guides.txt').write_text('fixture.md\nother.md\n')
            (root / 'tools/version_basis_sources_baseline.txt').write_text('')
            (root / 'CHANGELOG.md').write_text('## 2026-09-26\n')
            first, second = root / 'fixture.md', root / 'other.md'
            first.write_text(current)
            second.write_text(legacy)
            with patch.object(vb, 'ROOT', root):
                self.assertEqual(vb.paths(), [first, second])
                first.write_text(BODY)
                with self.assertRaisesRegex(ValueError, 'missing version_basis'):
                    vb.paths()
                first.write_text(vb.front_matter(fixture()) + current)
                with self.assertRaisesRegex(ValueError, 'both'):
                    vb.paths()
                first.write_text(legacy)
                def run(*args):
                    output = io.StringIO()
                    with patch.object(sys, 'argv', ['version_basis.py', *args]), \
                            contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                        result = vb.main()
                    return result, output.getvalue()
                second.write_text(legacy + 'Changed body.\n')
                self.assertEqual(run('--migrate', str(first), str(second))[0], 1)
                self.assertEqual(first.read_text(), legacy)
                second.write_text(legacy)
                self.assertEqual(run('--migrate', str(first), str(first))[0], 1)
                self.assertEqual(run('--migrate', str(root / 'missing.md'))[0], 1)
                code, output = run('--migrate', str(first), str(second))
                self.assertEqual(code, 0, output)
                self.assertEqual(output.count('body bytes equal'), 2)
                self.assertEqual(first.read_text(), current)
                self.assertEqual(run('--check')[0], 0)
                self.assertEqual(run('--migrate', str(first))[0], 1)
                (root / 'extra.md').write_text(current)
                with self.assertRaisesRegex(ValueError, 'pilot list differs'):
                    vb.paths()

    def test_shape_urls_and_verify_fingerprints(self):
        from check_bare_urls import lexical_findings, parsed_findings
        from check_guide_shape import find_sources, find_verify
        from check_verify_marking import scan_units
        parser = gate_parser(required=bool(os.environ.get('CI')))
        if parser is None:
            self.skipTest('pinned parser unavailable')
        legacy = self.legacy()
        current = vb.migrated(legacy, 'fixture.md', parser=parser)
        old, old_errors = scan_units(legacy, enrolled=True, parser=parser)
        new, new_errors = scan_units(current, enrolled=True, parser=parser)
        self.assertEqual(old_errors, new_errors)
        self.assertEqual([unit[1:] for unit in old], [unit[1:] for unit in new])
        self.assertEqual(find_verify('fixture.md', current), [])
        self.assertEqual(find_sources('fixture.md', current, datetime.date(2026, 10, 18)), [])
        missing = current.replace('- Product v1.0: ' + URL, '- No citation', 1)
        self.assertTrue(find_sources('fixture.md', missing, datetime.date(2026, 10, 18)))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'fixture.md'
            for text in (legacy, current):
                # JSON URLs are opaque; an ordinary body occurrence is still checked.
                text = text.replace('"schema": 1,', '"sample": "https://example.com/a__b", "schema": 1,')
                path.write_text(text)
                self.assertEqual(list(lexical_findings(path)), [])
                self.assertEqual(list(parsed_findings(path, parser)), [])
                text = text.replace('A documented control.', 'https://example.com/a__b')
                path.write_text(text)
                line = text.split('\n').index('https://example.com/a__b') + 1
                for findings in (lexical_findings(path), parsed_findings(path, parser)):
                    self.assertEqual(list(findings), [f'fixture.md:{line}: bare URL contains __: https://example.com/a__b'])


if __name__ == '__main__':
    unittest.main()
