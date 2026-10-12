#!/usr/bin/env python3
"""Closed-form rendered Sources contracts and adversarial regressions."""
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


def error(kind, visible):
    # Literal contract text, deliberately independent of production constants.
    return (f"unclassified {kind} URL-like run {visible!r}; "
            "write the URL as an explicit link or autolink, or separate it with whitespace")


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
    chunk = text
    def finding(reason):
        return "finding", ([], [error("bare", text)])
    def invalid(reason):
        return finding(f"invalid bare URL {chunk!r}: {reason}")
    def tail(value):
        return finding("tail")
    whole = ("whole", ([text], []))
    nonword = not char.isascii() and not char.isalnum()
    hard = char in HARD or nonword
    if position == "wrapped":
        return finding("prefix or parentheses")
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


    def test_emphasis_token_evidence(self):
        parser = self.parser()
        children = parser.parseInline("_" + URL + "_x")[0].children
        self.assertEqual([(t.type, t.content) for t in children],
                         [("text", "_" + URL + "_x")])
        children = parser.parseInline("_" + URL + "_")[0].children
        self.assertEqual([(t.type, t.content) for t in children],
                         [("em_open", ""), ("text", URL), ("em_close", "")])


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


    def check_run(self, raw, visible, kind="mixed", hrefs=(), html=False):
        result = gate.scan(ROOT + "- " + raw + "\n", self.parser())
        expected = ["body line 5: unclassified raw HTML"] if html else []
        if kind:
            expected.append("body line 5: " + error(kind, visible))
        self.assertEqual(result.findings, expected, raw)
        self.assertEqual([i.hrefs for i in result.items.values()], [list(hrefs)], raw)

    def test_bare_url_grammar(self):
        for text in (URL, URL + ",", "(" + URL + ")", "prefix: " + URL + "; suffix"):
            self.assertEqual(gate.bare_urls(text), ([URL], []))
            self.assertEqual(gate.legacy.cites(text, URL), 1)
        for suffix in ("/v2", "_v2", ".json", "?q=1", "#part", "/a_b", "%2F"):
            self.assertEqual(gate.bare_urls(URL + suffix), ([URL + suffix], []))
        for raw in ("www.example.com", "ftp://example.com/p", "tcp://:9092", "wss://"):
            self.assertEqual(gate.bare_urls(raw), ([], [f"unclassified URL-like text {raw!r}"]))
        for raw in ("http:", "://", "init:", "behaviour:", "//", "`a`/`b`/c"):
            self.assertEqual(gate.bare_urls(raw), ([], []))
        for raw in ("x" + URL, URL + "(ambiguous)", "https://a..b/p", "_" + URL):
            self.assertEqual(gate.bare_urls(raw), ([], [error("bare", raw)]))
        self.assertEqual(gate.bare_urls(URL + " ; " + URL), ([URL, URL], []))

    def test_ascii_authority_boundaries(self):
        for punctuation in ("~", "*", ")", "(", "!", "'", ",", ";", ":"):
            url = "https://alice" + punctuation + "ops@example.com/p"
            if punctuation in "!,;:":
                self.assertEqual(gate.bare_urls(url), ([url], []))
                url = "https://alice" + punctuation + "ops~more@example.com/p"
            self.assertEqual(gate.bare_urls(url), ([], [error("bare", url)]))
        for url in ("https://exam~ple.com/p", "https://example.com:80~90/p",
                    "https://alice~ops@first@example.com/p", "https://alice)ops@example.com",
                    "https://exam*ple.com", "https://alice@first@example.com/p"):
            self.assertEqual(gate.bare_urls(url), ([], [error("bare", url)]))

    def test_whole_tail_classification(self):
        for opener in ("", "("):
            for tail in ("", ",", ";", ")", "),", ");", ".", ":", "?", "!", "_",
                         "'", '"', "]", ">", "}", "~", "*", ",;", "))", "?!.,:;_"):
                raw = opener + URL + tail
                expected = ([URL], []) if tail in ("", ",", ";") or (
                    opener and tail in (")", "),", ");")) else ([], [error("bare", raw)])
                with self.subTest(raw=raw):
                    self.assertEqual(gate.bare_urls(raw), expected)
        for tail in ("~unchecked/path", ")text", "'ops@example.com/p",
                     "**https://elsewhere.example/p", ")www.example.com"):
            self.assertEqual(gate.bare_urls(URL + tail), ([], [error("bare", URL + tail)]))
        for prefix in ("(see ", "(nested (see) "):
            self.assertEqual(gate.bare_urls(prefix + URL + "),"), ([URL], []))
        self.assertEqual(gate.bare_urls("(closed) " + URL + ")"),
                         ([], [error("bare", URL + ")")]))
        self.assertFalse(gate.benign_tail(")", "(", URL + "("))

    def test_literal_tail_regressions(self):
        for prefix, tail in (("", "*tail"), ("", "**tail"), ("", "~tail"), ("", "~~tail"),
                             ("", "~é"), ("", "~中"), ("", "~ß"), ("_", "_tail"),
                             ("_", "_x"), ("**", "**x"), ("", "*ops"), ("", "~ops"),
                             ("", "~1"), ("", "*3")):
            raw = prefix + URL + tail
            self.assertEqual(gate.bare_urls(raw), ([], [error("bare", raw)]))
        for raw, visible, kind in (
                *[(URL + t, URL + t, "bare") for t in
                  ("*tail", "**tail", "~tail", "~~tail", "~é", "~中", "~ß", "~1")],
                (URL + "*3 and more", URL + "*3", "bare"),
                ("_" + URL + "_tail", "_" + URL + "_tail", "bare"),
                ("_" + URL + "_x", "_" + URL + "_x", "bare"),
                (URL + "&ast;ops", URL + "*ops", "mixed"),
                (URL + "&#126;ops", URL + "~ops", "mixed"),
                ("https://example.com/~user", "https://example.com/~user", "bare")):
            self.check_run(raw, visible, kind)
            data = {"components": {"component": {"sources": {"source": URL}}}}
            self.assertEqual(gate.compare(data, ROOT + "- " + raw + "\n", self.parser())[3],
                             ["body line 5: " + error(kind, visible)])

    def test_punctuation_matrix(self):
        for char in string.punctuation + "é中ß☃\u0301":
            for position, template in MATRIX_TEMPLATES.items():
                with self.subTest(char=char, position=position):
                    text = template.format(char, char)
                    outcome, expected = matrix_expectation(char, position, text)
                    self.assertEqual(gate.bare_urls(text), expected, outcome)

    def test_round_four_regressions(self):
        data = {"components": {"component": {"sources": {"source": URL}}}}
        for tail in ("_", "?"):
            diagnostic = "body line 5: " + error("bare", URL + tail)
            self.assertEqual(gate.compare(data, ROOT + "- " + URL + tail + "\n", self.parser()),
                             ([((4,), ("component", "source"), 1, 0)], False, (1, 1), [diagnostic]))
        for raw in ("https://example.com:", "_" + URL + "_"):
            self.assertEqual(gate.bare_urls(raw), ([], [error("bare", raw)]))
        for raw, visible in ((URL + "`_`", URL + "_"), ("`https://`_", "https://_"),
                             ("https:`c`//example.com/p", "https:c//example.com/p")):
            self.check_run(raw, visible)
        self.assertEqual(gate.compare(data, ROOT + "- `" + URL + "`\n", self.parser()),
                         ([((4,), ("component", "source"), 1, 0)], False, (1, 1), []))

    def test_interrupted_plain_markers(self):
        for raw in ("https<://example.com/p>", "https:<//example.com/p>",
                    "https:/</example.com/p>", "https*://example.com/p*", "https**://example.com/p**"):
            self.assertEqual(gate.bare_urls(raw), ([], [error("bare", raw)]))
            self.check_run(raw, raw, "bare")
        for offset in (5, 6, 7):
            raw = URL[:offset] + "&amp;" + URL[offset:]
            self.check_run(raw, URL[:offset] + "&" + URL[offset:])

    def test_mention_adjacency_matrix(self):
        for marker in ("https://", "wss://"):
            for char in string.punctuation + "a1é中":
                for side in ("left", "right"):
                    encoded = f"&#{ord(char)};" if char in "`\\>" else char
                    raw = encoded + "`" + marker + "`" if side == "left" else "`" + marker + "`" + encoded
                    visible = char + marker if side == "left" else marker + char
                    with self.subTest(marker=marker, char=char, side=side):
                        self.check_run(raw, visible, None if char in "(),;:." else "mixed")

    def test_generated_opaque_offsets(self):
        # Each representation has a specified visible spelling, independent of
        # the adapter. HTML attributes and image destinations are not visible.
        wrappers = {
            "code": lambda t: ("`" + t + "`", t, (), False),
            "image": lambda t: ("![" + t + "](image.png)", t, (), False),
            "empty image": lambda t: ("![](" + t + ")", "", (), False),
            "link": lambda t: ("[" + t + "](" + URL + ")", t, (URL,), False),
            "autolink": lambda t: ("<" + URL + ">", URL, (URL,), False),
            "html": lambda t: ('<span data-url="' + t + '"></span>', "", (), True),
            "em": lambda t: ("*" + t + "*", t, (), False),
            "strong": lambda t: ("**" + t + "**", t, (), False),
            "entity": lambda t: ("".join(f"&#{ord(c)};" for c in t), t, (), False),
        }
        for kind, wrap in wrappers.items():
            for offset in range(1, len(URL)):
                for side in ("prefix", "suffix"):
                    prefix, suffix = URL[:offset], URL[offset:]
                    raw, shown, hrefs, html = wrap(prefix if side == "prefix" else suffix)
                    raw = raw + suffix if side == "prefix" else prefix + raw
                    visible = shown + suffix if side == "prefix" else prefix + shown
                    # Hidden fragments can leave no visible URL, by the ruling.
                    like = bool(re.search(r"[\w+.-]+://|www\.|\bhttps?:|://", visible, re.I))
                    # CommonMark punctuation flanking leaves these delimiters literal.
                    literal = kind in {"em", "strong"} and (
                        side == "suffix" and prefix[-1].isalnum() and suffix[0] in string.punctuation
                        or side == "prefix" and prefix[-1] in string.punctuation and suffix[0].isalnum())
                    with self.subTest(kind=kind, offset=offset, side=side):
                        self.check_run(raw, raw if literal else visible,
                                       "bare" if literal else "mixed" if like else None, hrefs, html)
            raw, shown, hrefs, html = wrap(URL)
            self.check_run(raw, shown, "mixed" if kind in {"em", "strong", "entity"} else None,
                           hrefs, html)

    def test_maintainer_ruling_non_url_split_is_quiet(self):
        # Maintainer scope ruling 2026-10-12: no readable URL remains.
        for raw in ("h`c`ttps:/`c`/example.com/p", "`a`/`b`/c"):
            self.check_run(raw, "", None)
        # A readable http: remains in the former disclosed blind spot.
        self.check_run("https:/`c`/example.com/p", "https:/c/example.com/p")

    def test_split_scheme_boundaries(self):
        for raw, visible, hrefs, html in (
                ("https`://`example.com/p", URL, (), False),
                ("https:`/`/example.com/p", URL, (), False),
                ("https`:`//example.com/p", URL, (), False),
                ("https![x](y)://example.com/p", "httpsx://example.com/p", (), False),
                ("`https://`example.com/p", URL, (), False),
                ("`https://example.com`/p", URL, (), False),
                ("https[part](https://target.example/p)://example.com/p",
                 "httpspart://example.com/p", ("https://target.example/p",), False),
                ("https<b></b>://example.com/p", URL, (), True)):
            self.check_run(raw, visible, hrefs=hrefs, html=html)

    def test_generated_scheme_splits(self):
        for start in range(8):
            for end in range(start + 1, 9):
                self.check_run(URL[:start] + "`" + URL[start:end] + "`" + URL[end:], URL)
        for split in range(1, 8):
            self.check_run(URL[:split] + "![x](y)" + URL[split:], URL[:split] + "x" + URL[split:])

    def test_literal_path_requires_explicit_link(self):
        for tail in ("~user", "*user", "~", "*"):
            target = "https://example.com/" + tail
            self.check_run(target, target, "bare")
            for raw in ("[source](" + target + ")", "<" + target + ">"):
                self.check_run(raw, target, None, (target,))

    def test_opaque_scheme_mentions(self):
        self.check_run("Deployment (TLS terminates at a proxy; `wss://`): " + URL, "", None, (URL,))
        for tail in ("", "):", "(),;:."):
            for end in ("", " " + URL):
                self.check_run("`https://`" + tail + end, "", None, (URL,) if end else ())
        for suffix in ("_", "~", "p", "1", "[", "%2F", "/", "@", "é", "):x"):
            self.check_run("`https://`" + suffix, "https://" + suffix)
            self.check_run(URL + "`" + suffix + "`", URL + suffix)
        for raw, visible in (("https://example.com/`p`", URL),
                             ("https://example.com/`p`):", URL + "):"), ("`wss://`):x", "wss://):x")):
            self.check_run(raw, visible)

    def test_percent_suffixes(self):
        for suffix in ("%", "%2", "%zz"):
            self.assertEqual(gate.bare_urls(URL + suffix), ([], [error("bare", URL + suffix)]))
            with self.assertRaisesRegex(ValueError, "^malformed percent escape$"):
                gate.normalize_url(URL + suffix)

    def test_embedded_marker(self):
        for tail in ("?next=https://other.example/p", "*https://other.example/p", "~ftp://other.example/p"):
            self.assertEqual(gate.bare_urls(URL + tail), ([], [error("bare", URL + tail)]))

    def test_rendered_positive_cases(self):
        for raw in (URL + ",", "(" + URL + ")", "source: " + URL,
                    "(see " + URL + "),", "([label](" + URL + ")),", "<" + URL + ">"):
            self.check_run(raw, "", None, (URL,))
        self.check_run(URL + " ; " + URL, "", None, (URL, URL))
        self.check_run("source:" + URL, "source:" + URL, "bare")
        for raw in ("_" + URL + "_", "**" + URL + "**"):
            self.check_run(raw, URL)
        target = "https://example.com/~user/a_b/__init__.py*"
        self.check_run("[source](" + target + ")", "", None, (target,))
        target = "https://www.postgresql.org/docs/"
        self.check_run(target, "", None, (target,))
        target = "https://developer.hashicorp.com/vault/docs/commands/operator/init"
        self.check_run("Vault operator init: " + target, "", None, (target,))

    def test_html_reports_once(self):
        self.check_run("<b>" + URL + "</b>", URL, html=True)
        self.check_run('<a href="' + URL + '">link</a>', "link", None, html=True)

    def test_truncated_authority_comparison(self):
        data = {"components": {"component": {"sources": {"source": "https://alice"}}}}
        for punctuation in ("~", "*", ")", "'"):
            url = "https://alice" + punctuation + "ops@example.com/p"
            self.assertEqual(gate.compare(data, ROOT + "- " + url + "\n", self.parser()),
                             ([((4,), ("component", "source"), 1, 0)], False, (1, 1),
                              ["body line 5: " + error("bare", url)]))

    def test_opaque_inline_boundaries(self):
        for opaque in ("`ops`", "![ops](image.png)"):
            for raw, visible in (("https://alice" + opaque + "@example.com/p", "https://aliceops@example.com/p"),
                                 (opaque + URL, "ops" + URL),
                                 ("https://ali**ce**" + opaque + "@example.com/p", "https://aliceops@example.com/p")):
                self.check_run(raw, visible)
            self.check_run(URL + " " + opaque, "", None, (URL,))

    def test_link_edges_and_labels(self):
        self.check_run("https://ali[ce](" + URL + ")@example.com/p", "https://alice@example.com/p", hrefs=(URL,))
        self.check_run("[prefix](" + URL + ")" + URL, "prefix" + URL, hrefs=(URL,))
        for label in (URL, URL + "`code`", "![alt](image.png)" + URL):
            self.check_run("[" + label + "](" + URL + ")", "", None, (URL,))

    def test_unicode_bare_authorities(self):
        data = {"components": {"component": {"sources": {"source": URL}}}}
        for name, url, normalized in UNICODE_BARE_CASES:
            with self.subTest(name=name):
                if normalized is None:
                    with self.assertRaisesRegex(ValueError, "^invalid IDNA 2003 host$"):
                        gate.normalize_url(url)
                else:
                    self.assertEqual(gate.normalize_url(url), normalized)
                self.assertEqual(gate.bare_urls(url), ([], [error("bare", url)]))
                self.assertEqual(gate.compare(data, ROOT + "- " + URL + "\n- " + url + "\n", self.parser()),
                                 ([], False, (2, 2), ["body line 6: " + error("bare", url)]))

    def test_comparison_counts(self):
        data = {"components": {"component": {"sources": {"source": URL}}}}
        self.assertEqual(gate.compare(data, ROOT + "- [" + URL + "](" + URL + ")\n", self.parser()),
                         ([((4,), ("component", "source"), 2, 1)], False, (1, 1), []))
        for cite in (URL, "<" + URL + ">", "[link](" + URL + ")"):
            self.assertEqual(gate.compare(data, ROOT + "- " + cite + "\n", self.parser()),
                             ([], False, (1, 1), []))

    def test_emphasis_in_bare_path(self):
        target = URL + "/__init__.py"
        self.check_run(target, URL + "/init.py")
        data = {"components": {"component": {"sources": {"source": target}}}}
        self.assertEqual(gate.compare(data, ROOT + "- " + target + "\n", self.parser()),
                         ([((4,), ("component", "source"), 1, 0)], False, (1, 1),
                          ["body line 5: " + error("mixed", URL + "/init.py")]))

    def test_unknowns_are_findings(self):
        parser = self.parser()
        self.assertEqual(gate.scan("# Guide\n\nText <placeholder>.\n\n" + ROOT + "- " + URL, parser).findings, [])
        original = parser.parse
        for defect, diagnostic in (("map", "extraction failed: missing or invalid source map for inline"),
                                   ("kind", "extraction failed: unclassified block token future_token")):
            def broken(body, env):
                tokens = original(body, env)
                token = next(t for t in reversed(tokens) if t.type == "inline")
                if defect == "map":
                    token.map = None
                else:
                    token.type = "future_token"
                return tokens
            with patch.object(parser, "parse", side_effect=broken):
                self.assertEqual(gate.scan(ROOT + "- [one](" + URL + ")\n", parser).findings, [diagnostic])

    def test_round_five_compositions(self):
        other = "https://other.example/"
        wrappers = {
            "code": lambda t: ("`" + t + "`", t, (), False),
            "link": lambda t: ("[" + t + "](" + other + ")", t, (other,), False),
            "image": lambda t: ("![" + t + "](image.png)", t, (), False),
            "empty image": lambda t: ("![](image.png)", "", (), False),
            "autolink": lambda t: ("<" + other + ">", other, (other,), False),
            "html": lambda t: ("<b>" + t + "</b>", t, (), True),
            "em": lambda t: ("*" + t + "*", t, (), False),
            "strong": lambda t: ("**" + t + "**", t, (), False),
            "entity": lambda t: ("".join(f"&#{ord(c)};" for c in t), t, (), False),
        }
        for kind, wrap in wrappers.items():
            for ch in (",", ";", ")", "),", ");"):
                raw, visible, hrefs, html = wrap(ch)
                prefix = "(see " if ")" in ch else ""
                with self.subTest(kind=kind, tail=ch):
                    literal = kind in {"em", "strong"}
                    self.check_run(prefix + URL + raw, URL + (raw if literal else visible),
                                   "bare" if literal else "mixed", hrefs=hrefs, html=html)
            for ch in "()":
                raw, visible, hrefs, html = wrap(ch)
                with self.subTest(kind=kind, wrapper=ch):
                    literal = kind in {"em", "strong"}
                    self.check_run(raw + URL, (raw if literal else visible) + URL,
                                   "bare" if literal else "mixed", hrefs=hrefs, html=html)
            for offset in range(1, 9):
                raw, visible, hrefs, html = wrap("c")
                split = URL[:offset] + raw + URL[offset:]
                shown = URL[:offset] + visible + URL[offset:]
                for following, rendered, extra in ((other, other, ()),
                                                    ("[x](" + other + ")", "x", (other,))):
                    with self.subTest(kind=kind, offset=offset, following=following):
                        self.check_run(split + following, shown + rendered,
                                       hrefs=hrefs + extra, html=html)
        # All 24 interrupted-then-intact cases, and all 24 reverse orders.
        for char in "<>*&":
            for offset in (5, 6, 7):
                broken = URL[:offset] + char + URL[offset:]
                for separator in ",;":
                    for raw in (broken + separator + other, other + separator + broken):
                        with self.subTest(raw=raw):
                            self.assertEqual(gate.bare_urls(raw), ([], [error("bare", raw)]))
                            self.check_run(raw, raw, "bare")
        for raw, shown, hrefs in ((URL + "[,](" + other + ")", URL + ",", (other,)),
                                  ("[(](" + other + ")" + URL, "(" + URL, (other,)),
                                  ("https:/[c](" + other + ")/example.com/p", "https:/c/example.com/p", (other,)),
                                  ("https:/*c*/example.com/p", "https:/c/example.com/p", ())):
            self.check_run(raw, shown, hrefs=hrefs)
        # An opaque opening parenthesis never supplies top-level punctuation.
        self.check_run("![x(](image.png)`wss://`", "x(wss://")
        self.check_run("![x(](image.png)" + URL + ")", "x(" + URL + ")")

    def test_slash_separated_corpus_mentions(self):
        # The five corpus lines from the corrected brief; no slash projection.
        for raw in ("`mysecret`/`mysalt`/all-zero",
                    "`--config`/`CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME`,",
                    "`stats enable`/`auth`/`admin`",
                    "`a`/`b`/c"):
            self.check_run(raw, "", None)
        root = Path(gate.__file__).resolve().parent.parent
        for name, number in (("llm-observability.md", 549), ("code-server.md", 176),
                             ("haproxy.md", 338), ("haproxy.md", 341), ("surrealdb.md", 297)):
            path = next(root.rglob(name))
            line = path.read_text().splitlines()[number - 1]
            with self.subTest(name=name, line=number):
                self.assertEqual(gate.scan(ROOT + line + "\n", self.parser()).findings, [])

    def test_whitespace_around_opaque_tokens(self):
        for raw, extra, html in (("`c`", (), False), ("![alt](image.png)", (), False),
                                 ("![](image.png)", (), False), ("[label](" + URL + ")", (URL,), False),
                                 ("<" + URL + ">", (URL,), False), ("<b></b>", (), True),
                                 ("*c*", (), False), ("**c**", (), False), ("&amp;", (), False)):
            self.check_run(URL + " " + raw + " " + URL, "", None, (URL,) + extra + (URL,), html)

    def test_nested_opaque_content_and_origins(self):
        # The full run has no marker, but the inner code token contains http:.
        self.check_run("x[a`http:`b](" + URL + ")", "xahttp:b", hrefs=(URL,))
        parser = self.parser()
        children = parser.parseInline("a[bc](" + URL + ")d")[0].children
        pieces = gate.inline_pieces(children)
        self.assertEqual([p.kind for p in pieces], ["text", "link", "text"])
        self.assertEqual([t.content for p in pieces for t in p.origins], ["a", "bc", "bc", "d"])

    def test_code_whitespace_and_prior_continuations(self):
        for raw in (URL + "` doc`", "`doc `" + URL):
            self.check_run(raw, "", None, (URL,))
        for suffix in ("_", "~", "example.com/p", "1", "[::1]/p", "%2F", "/p", "@host/p", "é", "):x"):
            self.check_run("`https://`" + suffix, "https://" + suffix)


if __name__ == "__main__":
    unittest.main()
