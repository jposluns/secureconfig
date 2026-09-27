#!/usr/bin/env python3
"""Mutation and integration tests for accidental metadata/summary drift."""
import json
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
        body = BODY.replace('# REASONED: no isolated listener available.', '# DEMONSTRATED')
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
            self.assertEqual(vb.updated(text), text)
            result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'),
                                     '--bundle', str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, vb.split(text)[1])
            self.assertTrue(result.stdout.startswith('# '))
        result = subprocess.run([sys.executable, str(vb.ROOT / 'tools/version_basis.py'), '--check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
