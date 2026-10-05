#!/usr/bin/env python3
"""D1 adapter contracts; the adversarial fixture migration is deferred to D2."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources_render as gate

URL = "https://example.com/p"
ROOT = "# Guide\n\n## Sources (checked October 2026)\n\n"
# Recorded whole-authority regressions; None denotes the incompatible A-label.
UNICODE_BARE_CASES = (
    ("codex reproduction", "https://example\uff0exn--fa-hia.de/p", None),
    ("fullwidth dot", "https://example\uff0ecom/p", URL),
    ("NFD host", "https://bu\u0308cher.example/p", "https://xn--bcher-kva.example/p"),
    ("fullwidth host and path", "https://\uff45\uff58\uff41\uff4d\uff50\uff4c\uff45.com/p", URL),
    ("compatibility dot", "https://example\u2024com/p", URL),
    ("compatibility letter", "https://ex\u24d0mple.com/p", URL),
)


class Contracts(unittest.TestCase):
    def test_url_identity(self):
        normal = gate.normalize_url
        for spelling in ("https://b\u00fccher.example/p", "https://xn--bcher-kva.example/p"):
            self.assertEqual(normal(spelling), "https://xn--bcher-kva.example/p")
        self.assertEqual(normal("HTTPS://User:Pass@\uff45\uff58\uff41\uff4d\uff50\uff4c\uff45.com:00443/P?#"),
                         "https://user:pass@example.com:00443/P?#")
        self.assertEqual(normal("https://fa\u00df.de/"), "https://fass.de/")
        for suffix in ("/P", "/p?", "/p#", "/p?q=1", "/p.", "/p%2F"):
            self.assertEqual(normal("https://EXAMPLE.com" + suffix),
                             "https://example.com" + suffix)
        self.assertEqual(normal("https://[2001:DB8::1]:443/p"), "https://[2001:db8::1]:443/p")
        for bad, diagnostic in (
                ("https://", "destination is not an absolute HTTP"),
                ("/p", "destination is not an absolute HTTP"),
                ("//example.com/p", "destination is not an absolute HTTP"),
                ("mailto:a@example.com", "destination is not an absolute HTTP"),
                ("https://a..b/p", "label empty"),
                ("https://xn--a/p", "Invalid character"),
                ("https://a\uff0fb/p", "host mapping introduces a delimiter"),
                ("https://a%2eb/p", "URL contains an escape, entity or encoded unreserved"),
                ("https://a:bad/p", "invalid port"),
                ("https://a:65536/p", "invalid port"),
                ("https://example.com/%61", "URL contains an escape, entity or encoded unreserved"),
                ("https://xn--fa-hia.de/", "IDNA does not round-trip")):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, diagnostic):
                normal(bad)

    def test_bare_url_grammar(self):
        for text in (URL, URL + ".", "(" + URL + ")", "**" + URL + "**x",
                     "_" + URL + "_x", "prefix: " + URL + "; suffix"):
            with self.subTest(text=text):
                self.assertEqual(gate.bare_urls(text), ([URL], []))
                self.assertEqual(gate.legacy.cites(text, URL), 1)
        for punctuation in ("?", "!", ".", ",", ":", ";", "_", "?!.,:;_"):
            with self.subTest(punctuation=punctuation):
                text = URL + punctuation
                self.assertEqual(gate.bare_urls(text), ([URL], []))
                self.assertEqual(gate.legacy.cites(text, URL), 1)
        for suffix in ("/v2", "_v2", ".json", "?q=1", "#part"):
            self.assertEqual(gate.bare_urls(URL + suffix), ([URL + suffix], []))
        for text, diagnostic in (
                ("www.example.com", "unclassified URL-like text 'www.example.com'"),
                ("ftp://example.com/p", "unclassified URL-like text 'ftp://example.com/p'"),
                ("x" + URL, "unclassified URL-like text 'x" + URL + "'"),
                (URL + "(ambiguous)", "ambiguous parentheses in bare URL '" + URL + "(ambiguous)'")):
            with self.subTest(text=text):
                self.assertEqual(gate.bare_urls(text), ([], [diagnostic]))
        urls, findings = gate.bare_urls("https://a..b/p")
        self.assertEqual(urls, [])
        self.assertEqual(len(findings), 1)
        self.assertRegex(findings[0], r"^invalid bare URL 'https://a\.\.b/p': .*label empty$")
        self.assertEqual(gate.bare_urls(URL + " " + URL), ([URL, URL], []))

    def test_unicode_bare_authorities(self):
        for name, url, normalized in UNICODE_BARE_CASES:
            with self.subTest(name=name):
                if normalized is None:
                    with self.assertRaisesRegex(ValueError, "IDNA does not round-trip"):
                        gate.normalize_url(url)
                else:
                    self.assertEqual(gate.normalize_url(url), normalized)
                # Even valid mappings are findings here: legacy boundaries
                # cannot distinguish a Unicode authority from adjacent text.
                self.assertEqual(gate.bare_urls(url),
                                 ([], [f"non-ASCII authority in bare URL {url!r}"]))

    def test_unicode_bare_comparison(self):
        parser = self.parser()
        data = {"components": {"component": {"sources": {"source": URL}}}}
        for name, url, _ in UNICODE_BARE_CASES:
            with self.subTest(name=name):
                body = ROOT + "- " + URL + "\n- " + url + "\n"
                diagnostic = f"body line 6: non-ASCII authority in bare URL {url!r}"
                result = gate.scan(body, parser)
                self.assertEqual(result.findings, [diagnostic])
                self.assertEqual([item.hrefs for item in result.items.values()], [[URL], []])
                self.assertEqual(gate.compare(data, body, parser),
                                 ([], False, (2, 2), [diagnostic]))

    def test_dependency_policy(self):
        for ci, required, rc in (("", False, 0), ("true", False, 1), ("", True, 1)):
            output = StringIO()
            with patch.dict(os.environ, {"CI": ci}), \
                    patch.object(gate, "gate_parser", side_effect=gate.ParserUnavailable("parser absent")), \
                    redirect_stdout(output), redirect_stderr(output):
                args = ["--compare"] + (["--require-parser"] if required else [])
                self.assertEqual(gate.main(args), rc)
            self.assertEqual(output.getvalue().count("  SKIP  "), int(rc == 0))
            self.assertEqual(output.getvalue().count("  FAIL  "), int(rc != 0))
            expected = ("  FAIL  rendered Sources comparison: parser absent\n" if rc else
                        "  SKIP  rendered Sources comparison: parser absent "
                        "(advisory; legacy check unchanged)\n")
            self.assertEqual(output.getvalue(), expected)
        output = StringIO()
        with patch.object(gate, "gate_parser", side_effect=ValueError("broken lock")), \
                redirect_stderr(output):
            self.assertEqual(gate.main(["--compare"]), 1)
        self.assertEqual(output.getvalue(), "  FAIL  rendered Sources comparison: broken lock\n")

    def parser(self):
        parser = gate.gate_parser()
        if parser is None:
            self.skipTest("pinned parser unavailable")
        return parser

    def test_links_and_ownership(self):
        parser = self.parser()
        body = ROOT + ("- [one](" + URL + ") <" + URL + "> [ref]\n"
                       "  continuation\n\n  - [child](" + URL + ")\n\n"
                       "- " + URL + " `" + URL + "` ![image](" + URL + ")\n\n"
                       "## After\n\n[ref]: " + URL + "\n")
        with patch.object(parser, "parse", wraps=parser.parse) as parse:
            result = gate.scan(body, parser)
            self.assertEqual(parse.call_count, 1)
        self.assertEqual(result.findings, [])
        self.assertEqual([item.hrefs for item in result.items.values()],
                         [[URL, URL, URL], [URL], [URL]])

    def test_comparison_counts(self):
        parser = self.parser()
        data = {"components": {"component": {"basis": "unknown", "sources": {"source": URL}}}}
        changes, owners, counts, findings = gate.compare(
            data, ROOT + "- [" + URL + "](" + URL + ")\n", parser)
        self.assertEqual(findings, [])
        self.assertFalse(owners)
        self.assertEqual(counts, (1, 1))
        self.assertEqual(changes, [((4,), ("component", "source"), 2, 1)])
        for cite in (URL, "<" + URL + ">", "[link](" + URL + ")", "**" + URL + "**"):
            changes, owners, counts, findings = gate.compare(data, ROOT + "- " + cite + "\n", parser)
            self.assertEqual((changes, owners, counts, findings), ([], False, (1, 1), []))

    def test_emphasis_in_bare_path(self):
        parser = self.parser()
        target = URL + "/__init__.py"
        body = ROOT + "- " + target + "\n"
        result = gate.scan(body, parser)
        self.assertEqual(result.findings, [])
        self.assertEqual([item.hrefs for item in result.items.values()], [[URL + "/init.py"]])
        data = {"components": {"component": {"sources": {"source": target}}}}
        changes, owners, counts, findings = gate.compare(data, body, parser)
        self.assertEqual((changes, owners, counts, findings),
                         ([((4,), ("component", "source"), 1, 0)], False, (1, 1), []))

    def test_unknowns_are_findings(self):
        parser = self.parser()
        self.assertEqual(gate.scan(ROOT + '- <a href="' + URL + '">link</a>\n', parser).findings,
                         ["body line 5: unclassified raw HTML"] * 2)
        self.assertEqual(gate.scan("# Guide\n\nText <placeholder>.\n\n" + ROOT + "- " + URL, parser).findings, [])
        self.assertEqual(gate.scan(ROOT + "- www.example.com\n", parser).findings,
                         ["body line 5: unclassified URL-like text 'www.example.com'"])
        original = parser.parse
        for defect, diagnostic in (
                ("map", "extraction failed: missing or invalid source map for inline"),
                ("kind", "extraction failed: unclassified block token future_token")):
            def broken(body, env):
                tokens = original(body, env)
                if defect == "map":
                    next(t for t in reversed(tokens) if t.type == "inline").map = None
                else:
                    next(t for t in reversed(tokens) if t.type == "inline").type = "future_token"
                return tokens
            with patch.object(parser, "parse", side_effect=broken):
                self.assertEqual(gate.scan(ROOT + "- [one](" + URL + ")\n", parser).findings,
                                 [diagnostic])


    def test_suite_contract(self):
        suite = Path(gate.__file__).with_name("run_all_checks.sh").read_text()
        block = suite[suite.index('echo "== rendered Sources shadow'):
                      suite.index('echo "== llms-full.txt')]
        adapter = """fail=0
bad() { fail=1; }
python3() {
  case "$3" in
    tools/test_sources_render.py) printf '%s\\n' "$SELF"; return 0 ;;
    tools/sources_render.py) printf '%s\\n' "$REPORT"; return "$RC" ;;
    *) return 99 ;;
  esac
}
"""
        advisory = "  ADVISORY  rendered Sources: 1/1 guides disagree; 1 findings"
        skip = "  SKIP  rendered Sources comparison: parser absent"
        for self_out, report, rc, ci, expected in (
                ("OK", advisory, "0", "", 0), ("OK", skip, "0", "", 0),
                ("OK", skip, "0", "true", 1), ("OK", "", "0", "", 1),
                ("", advisory, "0", "", 1), ("OK", advisory, "1", "", 1),
                ("OK\n  FAIL  injected", advisory, "0", "", 1),
                ("OK", advisory + "\n  FAIL  injected", "0", "", 1)):
            result = subprocess.run(["bash", "-c", adapter + block + '\nexit "$fail"'],
                                    env=dict(os.environ, SELF=self_out, REPORT=report, RC=rc, CI=ci),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_section_boundaries(self):
        parser = self.parser()
        for ending in ("", "\n", "\n## After\n\n- [elsewhere](" + URL + ")\n"):
            result = gate.scan(ROOT + "- [one](" + URL + ")" + ending, parser)
            self.assertEqual(result.findings, [])
            self.assertEqual([item.hrefs for item in result.items.values()], [[URL]])
        result = gate.scan(ROOT + "- [one](" + URL + ")\n\n"
                           "## **Sources** (checked October 2026)\n\n- [two](" + URL + ")\n", parser)
        self.assertEqual(result.findings,
                         ["body line 7: unsupported Sources heading",
                          "body line 7: unselected rendered Sources"])


if __name__ == "__main__":
    unittest.main()
