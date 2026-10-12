#!/usr/bin/env python3
"""D1 adapter contracts; the adversarial fixture migration is deferred to D2."""
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
import re
import string
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


def tail_error(tail, chunk):
    return (f"unclassified bare URL tail {tail!r} in {chunk!r}; "
            "write it as an explicit link or put whitespace after it")


MATRIX_TEMPLATES = {
    "userinfo": "https://alice{}ops@example.com/p",
    "host": "https://exam{}ple.com/p",
    "port": "https://example.com:8{}0/p",
    "authority/path": "https://example.com{}/p",
    "authority/end": "https://example.com{}",
    "path/middle": URL + "{}/more",
    "path/letter": URL + "{}x",
    "path/digit": URL + "{}1",
    "path/end": URL + "{}",
    "doubled": URL + "{}{}",
    "wrapped": "{}" + URL + "{}",
    "query": URL + "?q=a{}b",
    "fragment": URL + "#part{}x",
}
# Named outcomes and exact reasons, specified independently of gate constants.
# Hard boundaries cannot be internal URL bytes under the legacy line grammar.
HARD = set("\"'*)<>[\\]^`{|}~")
SOFT = set("?!.,:;_")


def matrix_expectation(char, position, text):
    chunk = text[1:] if position == "wrapped" and char != "<" else text
    def finding(reason):
        return "finding", ([], [reason])
    def invalid(reason):
        return finding(f"invalid bare URL {chunk!r}: {reason}")
    def tail(value):
        return finding(tail_error(value, chunk))
    whole = ("whole", ([text], []))
    nonword = not char.isascii() and not char.isalnum()
    hard = char in HARD or nonword
    if position == "wrapped":
        if char in "/.%?#&=+@$-" or char.isalnum() or char == "<":
            return finding(f"unclassified URL-like text {chunk!r}")
        if char == "(":
            return finding(f"ambiguous parentheses in bare URL {chunk!r}")
        if char in ",;":
            # Both commas/semicolons are prose; the prefix is not a destination.
            return "wrapped", ([URL], [])
        return tail(char)
    authority = position in {"userinfo", "host", "port", "authority/path", "authority/end"}
    if authority and not char.isascii():
        return finding(f"non-ASCII authority in bare URL {chunk!r}")
    if position in {"userinfo", "host", "port", "authority/path"}:
        if hard:
            return finding(f"closing boundary inside bare URL authority {chunk!r}")
        if char == "(":
            return finding(f"ambiguous parentheses in bare URL {chunk!r}")
        if char == "%":
            return invalid("malformed percent escape")
        if position == "userinfo":
            return invalid("ambiguous userinfo") if char == "@" else whole
        if char in "/?#":
            return whole
        if position == "host":
            if char in "-.@":
                return whole
            return invalid("invalid port" if char == ":" else "invalid DNS host")
        if position == "port":
            return whole if char == "@" else invalid("invalid port")
        if char == ".":
            return whole
        return invalid("invalid port" if char == ":" else "invalid DNS host")
    if char == "(":
        return finding(f"ambiguous parentheses in bare URL {chunk!r}")
    if position in {"path/end", "authority/end", "doubled"}:
        count = 2 if position == "doubled" else 1
        if hard or char in SOFT:
            if char in ",;" and count == 1:
                return "shortened", ([text[:-1]], [])
            return tail(char * count)
        if char == "%":
            return invalid("malformed percent escape")
        if position == "authority/end" and char in "&=+$-@":
            return invalid("invalid DNS host")
        return whole
    if hard:
        suffix = {"path/middle": "/more", "path/letter": "x", "path/digit": "1",
                  "query": "b", "fragment": "x"}[position]
        return tail(char + suffix)
    if char == "%":
        return invalid("malformed percent escape")
    return whole


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
                ("https://", "destination is not an absolute HTTP(S) URL"),
                ("/p", "destination is not an absolute HTTP(S) URL"),
                ("//example.com/p", "destination is not an absolute HTTP(S) URL"),
                ("mailto:a@example.com", "destination is not an absolute HTTP(S) URL"),
                ("https://a..b/p", "invalid IDNA 2003 host"),
                ("https://xn--a/p", "invalid IDNA 2003 host"),
                ("https://a\uff0fb/p", "host mapping introduces a delimiter or unsupported character"),
                ("https://a%2eb/p", "URL contains an escape, entity or encoded unreserved character"),
                ("https://a:bad/p", "invalid port"),
                ("https://a:65536/p", "invalid port"),
                ("https://example.com/%61", "URL contains an escape, entity or encoded unreserved character"),
                ("https://xn--fa-hia.de/", "invalid IDNA 2003 host")):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "^" + re.escape(diagnostic) + "$"):
                normal(bad)

    def test_bare_url_grammar(self):
        for text in (URL, URL + ",", "(" + URL + ")",
                     "prefix: " + URL + "; suffix"):
            with self.subTest(text=text):
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
        self.assertEqual(gate.bare_urls("https://a..b/p"), ([], [
            "invalid bare URL 'https://a..b/p': invalid IDNA 2003 host"]))
        self.assertEqual(gate.bare_urls(URL + " " + URL), ([URL, URL], []))

    def test_ascii_authority_boundaries(self):
        # ! , ; : are continuations in the legacy grammar. Exercise them both
        # intact below and before a later hard stop inside the same userinfo.
        for punctuation in ("~", "*", ")", "(", "!", "'", ",", ";", ":"):
            url = "https://alice" + punctuation + "ops@example.com/p"
            if punctuation == "(":
                diagnostic = f"ambiguous parentheses in bare URL {url!r}"
            elif punctuation in "!,;:":
                self.assertEqual(gate.bare_urls(url), ([url], []))
                url = "https://alice" + punctuation + "ops~more@example.com/p"
                diagnostic = f"closing boundary inside bare URL authority {url!r}"
            else:
                diagnostic = f"closing boundary inside bare URL authority {url!r}"
            with self.subTest(punctuation=punctuation):
                self.assertEqual(gate.bare_urls(url), ([], [diagnostic]))
        for url in ("https://exam~ple.com/p", "https://example.com:80~90/p",
                    "https://alice~ops@first@example.com/p",
                    "https://alice)ops@example.com", "https://exam*ple.com"):
            with self.subTest(url=url):
                self.assertEqual(gate.bare_urls(url), ([], [
                    f"closing boundary inside bare URL authority {url!r}"]))
        url = "https://alice@first@example.com/p"
        self.assertEqual(gate.bare_urls(url), ([], [
            f"invalid bare URL {url!r}: ambiguous userinfo"]))

    def test_whole_tail_classification(self):
        for opener in ("", "("):
            for tail in ("", ",", ";", ")", "),", ");", ".", ":", "?", "!", "_",
                         "'", '"', "]", ">", "}", "~", "*", ",;", "))", "?!.,:;_"):
                with self.subTest(opener=opener, tail=tail):
                    chunk = URL + tail
                    expected = ([URL], []) if tail in ("", ",", ";") or (
                        opener and tail in (")", "),", ");")) else ([], [tail_error(tail, chunk)])
                    self.assertEqual(gate.bare_urls(opener + chunk), expected)
        self.assertEqual(gate.bare_urls("_" + URL), ([], [
            f"literal underscore opener in bare URL {URL!r}; write it as an explicit link"]))
        for tail in ("~unchecked/path", ")text", "'ops@example.com/p",
                     "**https://elsewhere.example/p", ")www.example.com"):
            with self.subTest(tail=tail):
                chunk = URL + tail
                self.assertEqual(gate.bare_urls(chunk), ([], [
                    f"unclassified bare URL tail {tail!r} in {chunk!r}; write it as an explicit link or put whitespace after it"]))


    def test_literal_tail_regressions(self):
        # bare_urls receives rendered text, never raw emphasis delimiters.
        for prefix, tail in (
                ("", "*tail"), ("", "**tail"), ("", "~tail"), ("", "~~tail"),
                ("", "~é"), ("", "~中"), ("", "~ß"),
                ("_", "_tail"), ("_", "_x"), ("**", "**x"),
                ("", "*ops"), ("", "~ops"), ("", "~1"), ("", "*3")):
            chunk = URL + tail
            with self.subTest(prefix=prefix, tail=tail):
                self.assertEqual(gate.bare_urls(prefix + chunk), ([], [
                    f"unclassified bare URL tail {tail!r} in {chunk!r}; write it as an explicit link or put whitespace after it"]))

    def test_rendered_literal_tail_regressions(self):
        parser = self.parser()
        data = {"components": {"component": {"sources": {"source": URL}}}}
        cases = [(URL + tail, tail) for tail in
                 ("*tail", "**tail", "~tail", "~~tail", "~é", "~中", "~ß",
                  "~1", "*3 and more")]
        cases += [("_" + URL + tail, tail) for tail in ("_tail", "_x")]
        cases += [(URL + "&ast;ops", "*ops"), (URL + "&#126;ops", "~ops")]
        cases += [("https://example.com/~user", "~user")]
        for raw, tail in cases:
            tail = tail.split()[0]
            rendered = gate.inline_text(parser.parseInline(raw)[0].children)
            chunk = rendered[rendered.index("https://"):].split()[0]
            diagnostic = f"body line 5: unclassified bare URL tail {tail!r} in {chunk!r}; write it as an explicit link or put whitespace after it"
            with self.subTest(raw=raw):
                body = ROOT + "- " + raw + "\n"
                result = gate.scan(body, parser)
                self.assertEqual(result.findings, [diagnostic])
                self.assertEqual([item.hrefs for item in result.items.values()], [[]])
                self.assertEqual(gate.compare(data, body, parser)[3], [diagnostic])

    def test_punctuation_matrix(self):
        # Expected classes and reasons come from the independent case table.
        for char in string.punctuation + "é中ß☃\u0301":
            for position, template in MATRIX_TEMPLATES.items():
                with self.subTest(char=char, position=position):
                    text = template.format(char, char)
                    outcome, expected = matrix_expectation(char, position, text)
                    actual = gate.bare_urls(text)
                    self.assertEqual(actual, expected, outcome)
                    urls, findings = actual
                    if outcome == "whole":
                        self.assertEqual((urls, findings), ([text], []))
                    elif outcome == "shortened":
                        prefix = "(" if text.startswith("(") else ""
                        self.assertEqual(findings, [])
                        self.assertEqual(len(urls), 1)
                        tail = text[len(prefix) + len(urls[0]):]
                        self.assertIn(tail, (",", ";", ")", "),", ");"))
                        if tail.startswith(")"):
                            self.assertEqual(prefix, "(")
                    elif outcome == "wrapped":
                        self.assertEqual((urls, findings), ([URL], []))
                    else:
                        self.assertEqual(urls, [])
                        self.assertEqual(len(findings), 1)

    def test_round_four_regressions(self):
        parser = self.parser()
        data = {"components": {"component": {"sources": {"source": URL}}}}
        for tail in ("_", "?"):
            diagnostic = "body line 5: " + tail_error(tail, URL + tail)
            body = ROOT + "- " + URL + tail + "\n"
            self.assertEqual(gate.scan(body, parser).findings, [diagnostic])
            self.assertEqual(gate.compare(data, body, parser),
                             ([((4,), ("component", "source"), 1, 0)],
                              False, (1, 1), [diagnostic]))
        target = "https://example.com"
        self.assertEqual(gate.bare_urls(target + ":"),
                         ([], [tail_error(":", target + ":")]))
        for raw in (URL + "`_`", "`https://`_", "https:`c`//example.com/p"):
            self.assertEqual(gate.scan(ROOT + "- " + raw + "\n", parser).findings,
                             ["body line 5: URL-like text touches code_inline"])
        for raw, destinations in (("(`https://`)", []),
                                  ("(`wss://`): " + URL, [URL])):
            result = gate.scan(ROOT + "- " + raw + "\n", parser)
            self.assertEqual(result.findings, [])
            self.assertEqual([i.hrefs for i in result.items.values()], [destinations])
        self.assertEqual(gate.bare_urls("_" + URL + "_"),
                         ([], [tail_error("_", URL + "_")]))
        # Whole code URLs are mentions; enrolled URLs still differ in counts.
        self.assertEqual(gate.compare(data, ROOT + "- `" + URL + "`\n", parser),
                         ([((4,), ("component", "source"), 1, 0)], False, (1, 1), []))

    def test_interrupted_plain_markers(self):
        parser = self.parser()
        for raw in ("https<://example.com/p>", "https:<//example.com/p>",
                    "https:/</example.com/p>", "https*://example.com/p*",
                    "https**://example.com/p**"):
            with self.subTest(raw=raw):
                children = parser.parseInline(raw)[0].children
                self.assertEqual([(t.type, t.content) for t in children], [("text", raw)])
                diagnostic = f"interrupted URL-like marker in {raw!r}"
                self.assertEqual(gate.bare_urls(raw), ([], [diagnostic]))
                self.assertEqual(gate.scan(ROOT + "- " + raw + "\n", parser).findings,
                                 ["body line 5: " + diagnostic])
        for offset in (5, 6, 7):
            raw = URL[:offset] + "&amp;" + URL[offset:]
            rendered = URL[:offset] + "&" + URL[offset:]
            with self.subTest(entity_offset=offset):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                self.assertEqual(result.findings,
                                 [f"body line 5: interrupted URL-like marker in {rendered!r}"])
                self.assertEqual([i.hrefs for i in result.items.values()], [[]])

    def test_mention_adjacency_matrix(self):
        parser = self.parser()
        for marker in ("https://", "wss://"):
            for char in string.punctuation + "a1é中":
                for side in ("left", "right"):
                    raw = char + "`" + marker + "`" if side == "left" else "`" + marker + "`" + char
                    # Preserve rendered punctuation that would otherwise merge
                    # with code delimiters or introduce a blockquote.
                    if char in "`\\>":
                        encoded = f"&#{ord(char)};"
                        raw = encoded + "`" + marker + "`" if side == "left" else "`" + marker + "`" + encoded
                    with self.subTest(marker=marker, char=char, side=side):
                        result = gate.scan(ROOT + "- " + raw + "\n", parser)
                        expected = [] if char in "(),;:." else [
                            "body line 5: URL-like text touches code_inline"]
                        self.assertEqual(result.findings, expected)
                        self.assertEqual([i.hrefs for i in result.items.values()], [[]])

    def test_generated_opaque_offsets(self):
        parser = self.parser()
        wrappers = {
            "code_inline": lambda text: "`" + text + "`",
            "image": lambda text: "![" + text + "](image.png)",
            "link": lambda text: "[" + text + "](" + URL + ")",
            "html": lambda text: '<span data-url="' + text + '"></span>',
        }
        for kind, wrap in wrappers.items():
            for offset in range(1, len(URL)):
                for side in ("prefix", "suffix"):
                    prefix, suffix = URL[:offset], URL[offset:]
                    raw = wrap(prefix) + suffix if side == "prefix" else prefix + wrap(suffix)
                    expected = set()
                    if kind == "html":
                        expected.add("body line 5: unclassified raw HTML")
                    else:
                        edge = "link_close" if side == "prefix" else "link_open"
                        expected.add("body line 5: URL-like text touches " + (edge if kind == "link" else kind))
                    if side == "prefix" and offset < 5:
                        expected.add(f"body line 5: unclassified URL-like text {suffix!r}")
                    if side == "suffix" and offset == 8:
                        expected.add(f"body line 5: unclassified URL-like text {prefix!r}")
                    if side == "suffix" and offset == 16:
                        expected.add("body line 5: " + tail_error(".", prefix))
                    with self.subTest(kind=kind, offset=offset, side=side):
                        result = gate.scan(ROOT + "- " + raw + "\n", parser)
                        self.assertEqual(set(result.findings), expected)
                        self.assertEqual(len(result.findings), len(expected))
            # Endpoints: the entire URL is opaque, with no adjacent plain text.
            result = gate.scan(ROOT + "- " + wrap(URL) + "\n", parser)
            self.assertEqual(result.findings,
                             ["body line 5: unclassified raw HTML"] if kind == "html" else [])
            self.assertEqual([i.hrefs for i in result.items.values()],
                             [[URL] if kind == "link" else []])

    def test_disclosed_opaque_limit(self):
        # Neither adjacent edge has scheme: or //; no complete marker survives
        # the visible projection. This remains a documented symmetric blind spot.
        body = ROOT + "- https:/`c`/example.com/p\n"
        result = gate.scan(body, self.parser())
        self.assertEqual(result.findings, [])
        self.assertEqual([i.hrefs for i in result.items.values()], [[]])

    def test_split_scheme_boundaries(self):
        parser = self.parser()
        for raw, kind in (
                ("https`://`example.com/p", "code_inline"),
                ("https:`/`/example.com/p", "code_inline"),
                ("https`:`//example.com/p", "code_inline"),
                ("https![x](y)://example.com/p", "image"),
                ("`https://`example.com/p", "code_inline"),
                ("`https://example.com`/p", "code_inline"),
                ("https[part](https://target.example/p)://example.com/p", "link_close"),
                ("https<b></b>://example.com/p", "html")):
            with self.subTest(raw=raw):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                expected = ("unclassified raw HTML" if kind == "html"
                            else "URL-like text touches " + kind)
                expected_findings = ["body line 5: " + expected]
                if kind == "link_close":
                    expected_findings.insert(0, "body line 5: URL-like text touches link_open")
                self.assertEqual(result.findings, expected_findings)
                if kind != "link_close":
                    self.assertEqual([item.hrefs for item in result.items.values()], [[]])

    def test_generated_scheme_splits(self):
        parser = self.parser()
        marker = "https://"
        for start in range(len(marker)):
            for end in range(start + 1, len(marker) + 1):
                raw = URL[:start] + "`" + URL[start:end] + "`" + URL[end:]
                with self.subTest(start=start, end=end):
                    result = gate.scan(ROOT + "- " + raw + "\n", parser)
                    expected = {"body line 5: URL-like text touches code_inline"}
                    # A suffix beginning inside "https" still spells a generic
                    # scheme (ttps, tps, ps or s), independently of the join.
                    # The prefix cannot contain :// because start < len(marker).
                    if end < len("https"):
                        expected.add("body line 5: unclassified URL-like text " + repr(URL[end:]))
                    self.assertEqual(set(result.findings), expected)
                    self.assertEqual(len(result.findings), len(expected))
                    self.assertEqual([item.hrefs for item in result.items.values()], [[]])
        for split in range(1, len(marker)):
            raw = URL[:split] + "![x](y)" + URL[split:]
            with self.subTest(image_split=split):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                expected = {"body line 5: URL-like text touches image"}
                if split < len("https"):
                    expected.add("body line 5: unclassified URL-like text " + repr(URL[split:]))
                self.assertEqual(set(result.findings), expected)
                self.assertEqual(len(result.findings), len(expected))
                self.assertEqual([item.hrefs for item in result.items.values()], [[]])

    def test_literal_path_requires_explicit_link(self):
        parser = self.parser()
        for tail in ("~user", "*user", "~", "*"):
            target = "https://example.com/" + tail
            with self.subTest(target=target):
                result = gate.scan(ROOT + "- " + target + "\n", parser)
                self.assertEqual(result.findings, [
                    f"body line 5: unclassified bare URL tail {tail!r} in {target!r}; "
                    "write it as an explicit link or put whitespace after it"])
                self.assertEqual([item.hrefs for item in result.items.values()], [[]])
            for raw in ("[source](" + target + ")", "<" + target + ">"):
                with self.subTest(raw=raw):
                    result = gate.scan(ROOT + "- " + raw + "\n", parser)
                    self.assertEqual(result.findings, [])
                    self.assertEqual([item.hrefs for item in result.items.values()], [[target]])

    def test_opaque_scheme_mentions(self):
        parser = self.parser()
        # This is a documentation mention followed by a separate real URL.
        raw = "Deployment (TLS terminates at a proxy; `wss://`): " + URL
        result = gate.scan(ROOT + "- " + raw + "\n", parser)
        self.assertEqual(result.findings, [])
        self.assertEqual([item.hrefs for item in result.items.values()], [[URL]])
        # Keep this independent of the production trailing-punctuation set.
        for tail in ("", "):", "(),;:."):
            for end in ("", " " + URL):
                with self.subTest(tail=tail, end=end):
                    result = gate.scan(ROOT + "- `https://`" + tail + end + "\n", parser)
                    self.assertEqual(result.findings, [])
                    self.assertEqual([item.hrefs for item in result.items.values()],
                                     [[URL] if end else []])
        # Whitespace in visible code is also a separator at either join.
        for raw in (URL + "` doc`", "`doc `" + URL):
            with self.subTest(raw=raw):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                self.assertEqual(result.findings, [])
                self.assertEqual([item.hrefs for item in result.items.values()], [[URL]])

    def test_opaque_url_continuations(self):
        parser = self.parser()
        for suffix in ("_", "~", "example.com/p", "1", "[::1]/p", "%2F", "/p", "@host/p",
                       "é", "):x"):
            with self.subTest(suffix=suffix):
                result = gate.scan(ROOT + "- `https://`" + suffix + "\n", parser)
                self.assertEqual(result.findings, ["body line 5: URL-like text touches code_inline"])
                self.assertEqual([item.hrefs for item in result.items.values()], [[]])
        for suffix in ("_", "~", "p", "1", "[", "%2F", "/", "@", "é", "):x"):
            with self.subTest(code_suffix=suffix):
                result = gate.scan(ROOT + "- " + URL + "`" + suffix + "`\n", parser)
                self.assertEqual(result.findings, ["body line 5: URL-like text touches code_inline"])
        for raw in ("https://example.com/`p`", "https://example.com/`p`):",
                    "`wss://`):x"):
            with self.subTest(raw=raw):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                self.assertEqual(result.findings, ["body line 5: URL-like text touches code_inline"])

    def test_percent_suffixes(self):
        for suffix in ("%", "%2", "%zz"):
            chunk = URL + suffix
            with self.subTest(suffix=suffix):
                self.assertEqual(gate.bare_urls(chunk), ([], [
                    f"invalid bare URL {chunk!r}: malformed percent escape"]))
                with self.assertRaisesRegex(ValueError, "^malformed percent escape$"):
                    gate.normalize_url(chunk)
        self.assertEqual(gate.bare_urls(URL + "%2F"), ([URL + "%2F"], []))

    def test_embedded_marker(self):
        # A complete nested URL is literal path/query data, not a second cite.
        chunk = URL + "?next=https://other.example/p"
        self.assertEqual(gate.bare_urls(chunk), ([chunk], []))
        for tail in ("*https://other.example/p", "~ftp://other.example/p"):
            self.assertEqual(gate.bare_urls(URL + tail), ([], [
                f"unclassified bare URL tail {tail!r} in {URL + tail!r}; write it as an explicit link or put whitespace after it"]))

    def test_emphasis_token_evidence(self):
        parser = self.parser()
        children = parser.parseInline("_" + URL + "_x")[0].children
        self.assertEqual([(t.type, t.content) for t in children],
                         [("text", "_" + URL + "_x")])
        children = parser.parseInline("_" + URL + "_")[0].children
        self.assertEqual([(t.type, t.content) for t in children],
                         [("em_open", ""), ("text", URL), ("em_close", "")])

    def test_rendered_positive_cases(self):
        parser = self.parser()
        for raw in (URL + ",", "(" + URL + ")", "source:" + URL,
                    "_" + URL + "_", "**" + URL + "**"):
            with self.subTest(raw=raw):
                result = gate.scan(ROOT + "- " + raw + "\n", parser)
                self.assertEqual(result.findings, [])
                self.assertEqual([item.hrefs for item in result.items.values()], [[URL]])
        result = gate.scan(ROOT + "- " + URL + " ; " + URL + "\n", parser)
        self.assertEqual(result.findings, [])
        self.assertEqual([item.hrefs for item in result.items.values()], [[URL, URL]])
        # Literal underscore paths fit the legacy grammar without shortening.
        target = URL + "/a_b"
        self.assertEqual(gate.bare_urls(target), ([target], []))
        # Explicit link destinations retain literal stars, tildes and underscores.
        target = "https://example.com/~user/a_b/__init__.py*"
        result = gate.scan(ROOT + "- [source](" + target + ")\n", parser)
        self.assertEqual(result.findings, [])
        self.assertEqual([item.hrefs for item in result.items.values()], [[target]])

    def test_html_reports_once(self):
        result = gate.scan(ROOT + "- <b>" + URL + "</b>\n", self.parser())
        self.assertEqual(result.findings, ["body line 5: unclassified raw HTML"])

    def test_truncated_authority_comparison(self):
        parser = self.parser()
        data = {"components": {"component": {"sources": {"source": "https://alice"}}}}
        for punctuation in ("~", "*", ")", "'"):
            url = "https://alice" + punctuation + "ops@example.com/p"
            with self.subTest(punctuation=punctuation):
                diagnostic = f"body line 5: closing boundary inside bare URL authority {url!r}"
                self.assertEqual(gate.compare(data, ROOT + "- " + url + "\n", parser),
                                 ([((4,), ("component", "source"), 1, 0)],
                                  False, (1, 1), [diagnostic]))

    def test_opaque_inline_boundaries(self):
        parser = self.parser()
        for token, opaque in (("code_inline", "`ops`"),
                              ("image", "![ops](image.png)")):
            for text in ("https://alice" + opaque + "@example.com/p", opaque + URL,
                         "https://ali**ce**" + opaque + "@example.com/p"):
                with self.subTest(token=token, text=text):
                    result = gate.scan(ROOT + "- " + text + "\n", parser)
                    self.assertEqual(result.findings,
                                     [f"body line 5: URL-like text touches {token}"])
            self.assertEqual(gate.scan(ROOT + "- " + URL + " " + opaque + "\n",
                                       parser).findings, [])

    def test_link_edges_and_labels(self):
        parser = self.parser()
        for text, kinds in (("https://ali[ce](" + URL + ")@example.com/p",
                             ("link_open", "link_close")),
                            ("[prefix](" + URL + ")" + URL, ("link_close",))):
            with self.subTest(text=text):
                self.assertEqual(gate.scan(ROOT + "- " + text + "\n", parser).findings,
                                 [f"body line 5: URL-like text touches {kind}" for kind in kinds])
        for label in (URL, URL + "`code`", "![alt](image.png)" + URL):
            with self.subTest(label=label):
                result = gate.scan(ROOT + "- [" + label + "](" + URL + ")\n", parser)
                self.assertEqual(result.findings, [])
                self.assertEqual([item.hrefs for item in result.items.values()], [[URL]])

    def test_invalid_link_is_not_recorded(self):
        parser = self.parser()
        body = ROOT + "- [bad](https://example.com:bad/p)\n"
        result = gate.scan(body, parser)
        self.assertEqual(result.findings,
                         ["body line 5: URL 'https://example.com:bad/p': invalid port"])
        self.assertEqual([item.hrefs for item in result.items.values()], [[]])

    def test_partial_and_duplicate_maps(self):
        parser = self.parser()
        original = parser.parse
        body = ROOT + URL + "\n"
        for defect, diagnostic in (
                ("inline", "extraction failed: inline crosses Sources boundary"),
                ("heading", "extraction failed: duplicate heading source identity")):
            def broken(text, env):
                tokens = original(text, env)
                if defect == "inline":
                    # Include a line before Sources content, within its parent.
                    tokens[-3].map = [2, 5]
                    tokens[-2].map = [2, 5]
                else:
                    tokens[3:3] = original("# Guide\n", {})
                return tokens
            with self.subTest(defect=defect), patch.object(parser, "parse", side_effect=broken):
                self.assertEqual(gate.scan(body, parser).findings, [diagnostic])

    def test_unicode_bare_authorities(self):
        for name, url, normalized in UNICODE_BARE_CASES:
            with self.subTest(name=name):
                if normalized is None:
                    with self.assertRaisesRegex(ValueError, "^invalid IDNA 2003 host$"):
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
                         ["body line 5: unclassified raw HTML"])
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
bad() { printf 'DIAGNOSTIC: %s\\n' "$1"; fail=1; }
python3() {
  case "$3" in
    tools/test_sources_render.py) printf '%s\\n' "$SELF"; return "$SELF_RC" ;;
    tools/sources_render.py) printf '%s\\n' "$REPORT"; return "$RC" ;;
    *) return 99 ;;
  esac
}
"""
        advisory = "  ADVISORY  rendered Sources: 1/1 guides disagree; 1 findings"
        skip = "  SKIP  rendered Sources comparison: parser absent"
        self_bad = "rendered Sources self-test exited 0 without a clean result"
        report_bad = "rendered Sources comparison exited 0 without a report"
        for self_out, self_rc, report, rc, ci, diagnostic in (
                ("OK", "0", advisory, "0", "", None),
                ("OK", "0", skip, "0", "", None),
                ("OK", "0", skip, "0", "true", "rendered Sources parser required in CI"),
                ("OK", "0", "", "0", "", report_bad),
                ("", "0", advisory, "0", "", self_bad),
                ("OK", "1", advisory, "0", "", "rendered Sources self-test"),
                ("OK", "0", advisory, "1", "", "rendered Sources comparison could not run"),
                ("OK\n  FAIL  injected", "0", advisory, "0", "", self_bad),
                ("OK", "0", advisory + "\n  FAIL  injected", "0", "", report_bad)):
            with self.subTest(self_out=self_out, self_rc=self_rc, report=report, rc=rc, ci=ci):
                result = subprocess.run(["bash", "-c", adapter + block + '\nexit "$fail"'],
                                        env=dict(os.environ, SELF=self_out, SELF_RC=self_rc,
                                                 REPORT=report, RC=rc, CI=ci),
                                        capture_output=True, text=True)
                output = result.stdout + result.stderr
                self.assertEqual(result.returncode, int(diagnostic is not None), output)
                self.assertEqual([line for line in output.splitlines()
                                  if line.startswith("DIAGNOSTIC: ")],
                                 ["DIAGNOSTIC: " + diagnostic] if diagnostic else [], output)

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
