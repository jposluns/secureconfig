#!/usr/bin/env python3
"""Recorded cases for tools/sentence_split.py, one or more per splitting rule.

The cases met in the TODO 1.385 work, where the measurement recorded in DONE 1.385
joined sentences that a reader sees as separate, are named for that row.
"""
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from sentence_split import sentences, split_sentences  # noqa: E402


def guide(markdown):
    """Every (line, sentence) of a guide, as a list."""
    return list(sentences(markdown))


class Rendering(unittest.TestCase):
    def test_link_renders_as_its_text(self):
        self.assertEqual(split_sentences("See [the guide](https://example.com/a) now."),
                         ["See the guide now."])

    def test_image_and_autolink_render(self):
        self.assertEqual(split_sentences("An ![icon](i.png) at <https://example.com/x>."),
                         ["An icon at https://example.com/x."])

    def test_backticks_and_emphasis_are_kept(self):
        self.assertEqual(split_sentences("Set `bind` to **loopback** and _only_ that."),
                         ["Set `bind` to **loopback** and _only_ that."])

    def test_code_span_in_link_text_keeps_backticks(self):
        self.assertEqual(split_sentences("Read [`env.go`](https://example.com/env.go) first."),
                         ["Read `env.go` first."])


class Units(unittest.TestCase):
    def test_hard_wrapped_paragraph_is_joined(self):
        self.assertEqual(guide("One sentence that\nwraps. Another\nstarts on line 2.\n"),
                         [(1, "One sentence that wraps."), (2, "Another starts on line 2.")])

    def test_blank_line_ends_a_paragraph(self):
        self.assertEqual(guide("no end here\n\nnew paragraph\n"),
                         [(1, "no end here"), (3, "new paragraph")])

    def test_list_items_are_separate_and_markers_not_counted(self):
        self.assertEqual(guide("- first item\n  continues\n- second item\n1. third\n"),
                         [(1, "first item continues"), (3, "second item"), (4, "third")])

    def test_each_table_cell_is_measured_on_its_own(self):
        table = ("| Port | Notes |\n| --- | :---: |\n"
                 "| 3000 | First note. Second note | a \\| b |\n")
        self.assertEqual(guide(table), [(1, "Port"), (1, "Notes"), (3, "3000"),
                                        (3, "First note."), (3, "Second note"),
                                        (3, "a | b")])

    def test_table_without_leading_pipes_is_measured_cell_by_cell(self):
        table = ("Port | Notes\n--- | :---:\n3000 | First note. Second note\n"
                 "8080 | Third\n\nA | paragraph.\n")
        self.assertEqual(guide(table), [(1, "Port"), (1, "Notes"), (3, "3000"),
                                        (3, "First note."), (3, "Second note"),
                                        (4, "8080"), (4, "Third"), (6, "A | paragraph.")])

    def test_heading_is_measured(self):
        self.assertEqual(guide("## 1. Bind privately. Then add TLS ##\nBody.\n"),
                         [(1, "1. Bind privately."), (1, "Then add TLS"), (2, "Body.")])

    def test_numbered_heading_number_is_not_a_sentence(self):
        self.assertEqual(guide("## 12. Verify\n"), [(1, "12. Verify")])

    def test_code_fences_are_skipped(self):
        text = ("Before.\n````markdown\n```\nNot. Prose.\n```\n````\n"
                "~~~\nAlso. Code.\n~~~\nAfter.\n")
        self.assertEqual(guide(text), [(1, "Before."), (10, "After.")])

    def test_claims_json_block_and_generated_section_are_skipped(self):
        text = ("Body.\n\n<!-- version-basis:start -->\n## About the AI assistant section below\n\n"
                "- c (REASONED; a): Summary.\n\n````json\n{\"claims\": {}}\n````\n"
                "<!-- version-basis:end -->\n")
        self.assertEqual(guide(text), [(1, "Body.")])

    def test_legacy_front_matter_is_skipped(self):
        text = '---\nversion_basis: {"claims": {"c": {"text": "No. Not."}}}\n---\n# T\n'
        self.assertEqual(guide(text), [(4, "T")])

    def test_html_comments_are_skipped(self):
        self.assertEqual(guide("Kept <!-- Not. This --> too.\n<!-- open\nStill. Hidden.\n-->\n"),
                         [(1, "Kept  too.")])

    def test_crlf_lines_read_as_lf(self):
        self.assertEqual(guide("One.\r\nTwo.\r\n"), [(1, "One."), (2, "Two.")])


class Boundaries(unittest.TestCase):
    def test_each_mark_before_each_opener(self):
        for mark in ".?!":
            for opener in ("Next", "4 more", "`code`", '"Quoted"', "“Curly”",
                           "(Aside)", "[Link text]"):
                with self.subTest(mark=mark, opener=opener):
                    self.assertEqual(split_sentences(f"Ends here{mark} {opener} goes on."),
                                     [f"Ends here{mark}", f"{opener} goes on."])

    def test_lowercase_or_no_whitespace_is_not_a_boundary(self):
        for text in ("It stops. then goes on.", "Version 1.5 is out.",
                     "Use example.com. Done.", "Is it?yes."):
            with self.subTest(text=text):
                self.assertEqual(len(split_sentences(text)), 1 + text.endswith("Done."))

    def test_across_closing_quote_and_bracket(self):
        self.assertEqual(split_sentences('He said "it works." Then it broke.'),
                         ['He said "it works."', "Then it broke."])
        self.assertEqual(split_sentences("A list [of two.] Next one."),
                         ["A list [of two.]", "Next one."])

    def test_across_opening_and_closing_emphasis(self):
        self.assertEqual(split_sentences("It is **required.** Next one."),
                         ["It is **required.**", "Next one."])
        self.assertEqual(split_sentences("It is required. *Next* one."),
                         ["It is required.", "*Next* one."])
        self.assertEqual(split_sentences("It is _done._ __Next__ one."),
                         ["It is _done._", "__Next__ one."])

    def test_never_inside_a_double_quoted_quotation(self):
        self.assertEqual(split_sentences('The page says "Use TLS. Rotate keys." today.'),
                         ['The page says "Use TLS. Rotate keys." today.'])
        self.assertEqual(split_sentences("It reads “One. Two” here."),
                         ["It reads “One. Two” here."])

    def test_escaped_quote_does_not_end_a_quotation(self):
        self.assertEqual(split_sentences('He said "Use \\"alpha. Beta\\" now." Then leave.'),
                         ['He said "Use "alpha. Beta" now."', "Then leave."])
        self.assertEqual(split_sentences('He said "Use \\"alpha.\\" Beta now." Then leave.'),
                         ['He said "Use "alpha." Beta now."', "Then leave."])

    def test_full_stop_inside_quotation_before_comma_is_not_a_boundary(self):
        text = 'stating "2FA actions must be performed in the personal context.", and its page.'
        self.assertEqual(split_sentences(text), [text])

    def test_never_inside_a_code_span(self):
        self.assertEqual(split_sentences("Run `a. B` and ``c? `D` `` here."),
                         ["Run `a. B` and ``c? `D` `` here."])

    def test_never_inside_link_text(self):
        self.assertEqual(split_sentences("See [Part 1. Setup](https://example.com/p) now."),
                         ["See Part 1. Setup now."])

    def test_never_after_an_abbreviation(self):
        for abbreviation in ("e.g.", "i.e.", "etc.", "vs.", "cf.", "E.g.", "Etc."):
            with self.subTest(abbreviation=abbreviation):
                text = f"Some values, {abbreviation} Redis, are listed."
                self.assertEqual(split_sentences(text), [text])

    def test_abbreviation_needs_a_word_boundary(self):
        self.assertEqual(split_sentences("It is a fetc. Then more."),
                         ["It is a fetc.", "Then more."])


class Cases1385(unittest.TestCase):
    """The cases the TODO 1.385 work met."""

    def test_full_stop_in_quoted_vendor_phrase_ending_in_etc(self):
        text = ('Its page lists a scope that "Allows the ability to change account settings '
                'such as email, password, 2FA, etc." The permissions reference reads otherwise.')
        self.assertEqual(split_sentences(text), [
            'Its page lists a scope that "Allows the ability to change account settings '
            'such as email, password, 2FA, etc."',
            "The permissions reference reads otherwise."])

    def test_eg_before_a_backtick(self):
        text = "Set a key flag, e.g. `--api-key`, before starting."
        self.assertEqual(split_sentences(text), [text])

    def test_sentence_opening_with_bold(self):
        self.assertEqual(split_sentences("Bind privately. **Never** publish the port."),
                         ["Bind privately.", "**Never** publish the port."])

    def test_run_of_rendered_source_links_between_two_sentences(self):
        text = ("It sets the demo password. [source](https://example.com/a#L1) "
                "[source](https://example.com/b#L2) The file comments require keys.")
        self.assertEqual(split_sentences(text), ["It sets the demo password. source source",
                                                 "The file comments require keys."])

    def test_link_whose_text_opens_a_sentence(self):
        self.assertEqual(split_sentences("It ends. [RFC 6455](https://example.com/r) says so."),
                         ["It ends.", "RFC 6455 says so."])

    def test_closing_parenthesis(self):
        self.assertEqual(split_sentences("Use a proxy (see section 2.) Then verify it."),
                         ["Use a proxy (see section 2.)", "Then verify it."])

    def test_table_cell(self):
        row = "| 3000 | The most crowded port. Most likely owners vary | [a.md](a.md) |\n"
        self.assertEqual(guide(row), [(1, "3000"), (1, "The most crowded port."),
                                      (1, "Most likely owners vary"), (1, "a.md")])

    def test_heading(self):
        self.assertEqual(guide("### Verify (REASONED: no runtime. Read from source)\n"),
                         [(1, "Verify (REASONED: no runtime."), (1, "Read from source)")])


class Command(unittest.TestCase):
    def run_cli(self, text, *args):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "g.md"
            path.write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(TOOLS / "sentence_split.py"), str(path), *args],
                capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout.replace(str(path), "g.md"), result.stderr

    def test_default_limit_is_400(self):
        text = "Intro.\n\n" + "x" * 399 + ".\n\n" + "y" * 400 + ".\n"
        self.assertEqual(self.run_cli(text), (0, "g.md:5 (401)\n", ""))

    def test_over_sets_the_limit(self):
        self.assertEqual(self.run_cli("Short one. Longer one here.\n", "--over", "10"),
                         (0, "g.md:1 (16)\n", ""))

    def test_unreadable_file_fails_closed(self):
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(TOOLS / "sentence_split.py"), "/nonexistent/g.md"],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)

    def test_undecodable_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "g.md"
            path.write_bytes(b"\xff")
            result = subprocess.run(
                [sys.executable, "-I", "-B", str(TOOLS / "sentence_split.py"), str(path)],
                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read", result.stderr)


def main():
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    if not result.wasSuccessful():
        print(stream.getvalue())
        print(f"  FAIL  sentence-splitter self-test: {len(result.failures)} failures, "
              f"{len(result.errors)} errors in {result.testsRun} tests")
        return 1
    print(f"  ok    {result.testsRun} recorded tests for the sentence splitter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
