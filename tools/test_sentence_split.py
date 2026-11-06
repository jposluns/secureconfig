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

    def test_never_after_an_abbreviation(self):
        for abbreviation in ("e.g.", "i.e.", "vs.", "cf.", "E.g."):
            with self.subTest(abbreviation=abbreviation):
                text = f"Some values, {abbreviation} Redis, are listed."
                self.assertEqual(split_sentences(text), [text])

    def test_closer_after_an_abbreviation_ends_the_sentence(self):
        self.assertEqual(split_sentences("Use a proxy (see e.g.) The next one."),
                         ["Use a proxy (see e.g.)", "The next one."])

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


class Cases1015(unittest.TestCase):
    """The inputs the first splitter joined or held back after #1015 merged, and the
    nested quotations and citation runs that the fixes for them must keep."""

    def test_etc_at_a_real_sentence_end(self):
        self.assertEqual(split_sentences("Use Redis, Kafka, etc. The next one."),
                         ["Use Redis, Kafka, etc.", "The next one."])

    def test_inch_mark_holds_back_no_boundary(self):
        self.assertEqual(split_sentences('The screen is 27" wide. Next. Another.'),
                         ['The screen is 27" wide.', "Next.", "Another."])

    def test_straight_quote_after_a_digit_closes_an_open_quotation(self):
        self.assertEqual(split_sentences('He set "width 27" here. Then "bold" text.'),
                         ['He set "width 27" here.', 'Then "bold" text.'])

    def test_unpaired_quote_holds_back_no_boundary(self):
        self.assertEqual(split_sentences('He wrote "Use TLS. Rotate keys. Next.'),
                         ['He wrote "Use TLS.', "Rotate keys.", "Next."])

    def test_straight_and_curly_quotes_pair(self):
        self.assertEqual(split_sentences('"Use TLS. Rotate keys” now. Next.'),
                         ['"Use TLS. Rotate keys” now.', "Next."])
        self.assertEqual(split_sentences('“Use TLS. Rotate keys" now. Next.'),
                         ['“Use TLS. Rotate keys" now.', "Next."])

    def test_nested_quotation_does_not_end_the_outer_one(self):
        for text, first in (('He said “Outer "Inner. Stop." Continue.” Then leave.',
                             'He said “Outer "Inner. Stop." Continue.”'),
                            ('He said "Outer “Inner. Stop.” Continue." Then leave.',
                             'He said "Outer “Inner. Stop.” Continue."'),
                            ('He said “Outer "Inner. Continue.” Then leave.',
                             'He said “Outer "Inner. Continue.”')):
            with self.subTest(text=text):
                self.assertEqual(split_sentences(text), [first, "Then leave."])
        self.assertEqual(split_sentences('“He said "Stop. Now." then left.” Next.'),
                         ['“He said "Stop. Now." then left.”', "Next."])

    def test_quotation_closes_with_its_table_cell(self):
        table = '| Size | Note |\n|---|---|\n| 27" wide. Next. | "Open. Shut. |\n'
        self.assertEqual(guide(table), [(1, "Size"), (1, "Note"), (3, '27" wide.'),
                                        (3, "Next."), (3, '"Open.'), (3, "Shut.")])

    def test_full_stop_in_link_text(self):
        self.assertEqual(split_sentences("Read [the guide.](https://example.com/g) Then go."),
                         ["Read the guide.", "Then go."])

    def test_capitalised_citation_run_stays_with_the_sentence_before(self):
        self.assertEqual(split_sentences("Bind it. [Redis security](https://example.com/r) "
                                         "[Sentinel](https://example.com/s) Then enable auth."),
                         ["Bind it. Redis security Sentinel", "Then enable auth."])


class Cases1016(unittest.TestCase):
    """The limits the splitter still disclosed after #1016, and the apostrophes and
    citation runs that the fixes for them must keep."""

    def test_inch_mark_leaves_a_curly_quotation_open(self):
        self.assertEqual(split_sentences('“A 27" screen. Still inside.” Next.'),
                         ['“A 27" screen. Still inside.”', "Next."])

    def test_never_inside_a_single_quoted_phrase(self):
        for text, first in (("He said 'Stop. Now.' Then leave.", "He said 'Stop. Now.'"),
                            ("He said ‘Stop. Now.’ Then leave.", "He said ‘Stop. Now.’"),
                            ("See ('Stop. Now.') Then leave.", "See ('Stop. Now.')")):
            with self.subTest(text=text):
                self.assertEqual(split_sentences(text), [first, "Then leave."])

    def test_apostrophes_in_words_open_no_quotation(self):
        self.assertEqual(split_sentences("Don't stop. The users' keys rotate. It’s done."),
                         ["Don't stop.", "The users' keys rotate.", "It’s done."])

    def test_link_that_opens_a_sentence_before_lowercase_text(self):
        self.assertEqual(split_sentences("It ends. [mfa.md](mfa.md) covers it."),
                         ["It ends.", "mfa.md covers it."])

    def test_link_before_a_capital_stays_with_the_sentence_before(self):
        self.assertEqual(split_sentences("It ends. [Redis](https://example.com/r) Sentinel "
                                         "docs say so. [source](https://example.com/s)"),
                         ["It ends. Redis", "Sentinel docs say so. source"])


class CodeSpanComments(unittest.TestCase):
    """A `<!--` in a code span opens no comment. Before this was handled, one such opener
    with no closer hid every later sentence of a pull request body, and one with a later
    code span holding `-->` joined two sentences into one."""

    def test_code_span_opener_hides_no_later_sentence(self):
        self.assertEqual(guide("A `<!--` in it opens no comment. The next one is seen.\n\n"
                               "A later paragraph.\n"),
                         [(1, "A `<!--` in it opens no comment."), (1, "The next one is seen."),
                          (3, "A later paragraph.")])

    def test_code_span_opener_and_closer_leave_two_sentences(self):
        self.assertEqual(guide("Type `<!--` to open one. Type `-->` to close it.\n"),
                         [(1, "Type `<!--` to open one."), (1, "Type `-->` to close it.")])

    def test_real_comment_after_a_code_span_is_still_hidden(self):
        self.assertEqual(guide("Run `x`. <!-- Not. Seen. --> Then this.\n<!--\nHidden. Too.\n-->\n"
                               "After.\n"),
                         [(1, "Run `x`."), (1, "Then this."), (5, "After.")])

    def test_real_comment_holding_a_backtick_is_still_hidden(self):
        self.assertEqual(guide("Kept. <!-- a ` b. Not. --> Shown.\n<!-- `\nStill. Hidden. -->\n"
                               "After `x`.\n"),
                         [(1, "Kept."), (1, "Shown."), (4, "After `x`.")])

    def test_code_span_may_cross_lines_of_its_paragraph(self):
        self.assertEqual(guide("Type `<!--\nstill code` here. Then more.\n"),
                         [(1, "Type `<!-- still code` here."), (2, "Then more.")])

    def test_backtick_with_no_closer_opens_nothing(self):
        self.assertEqual(guide("A stray ` then <!-- Hidden. Text. --> shown.\n"),
                         [(1, "A stray ` then  shown.")])

    def test_escaped_backtick_opens_nothing(self):
        self.assertEqual(guide("An \\` then <!-- Hidden. ` --> shown. Next.\n"),
                         [(1, "An ` then  shown."), (1, "Next.")])

    def test_code_span_does_not_close_past_a_heading(self):
        self.assertEqual(guide("Use a ` here.\n# Type `<!--`\n`\nSeen. Also seen.\n"),
                         [(1, "Use a ` here."), (2, "Type `<!--`"), (3, "` Seen."),
                          (4, "Also seen.")])


class ParagraphEnds(unittest.TestCase):
    """Where CommonMark ends a paragraph, a code span cannot pair past it, so a real comment
    after it stays hidden (QA round 1 on #1235). A thematic break or a setext underline is
    still read as a line of the unit, as the module docstring says."""

    def test_lone_quote_marker_ends_the_paragraph(self):
        self.assertEqual(guide("> Text `code\n>\n> Text <!-- Hidden. -->` after.\n"),
                         [(1, "Text `code"), (3, "Text ` after.")])

    def test_thematic_break_ends_the_paragraph(self):
        self.assertEqual(guide("Text with ` stray.\n***\nAnother <!-- a ` b --> end.\n"),
                         [(1, "Text with ` stray. *** Another  end.")])

    def test_setext_underlines_end_the_paragraph(self):
        for underline in ("---", "==="):
            self.assertEqual(guide(f"Head ` x\n{underline}\nAnd <!-- c ` d --> e.\n"),
                             [(1, f"Head ` x {underline} And  e.")])

    def test_html_block_start_ends_the_paragraph(self):
        self.assertEqual(guide("Use ` here.\n<div>\nThen <!-- e ` f --> g.\n</div>\n"),
                         [(1, "Use ` here. <div> Then  g. </div>")])

    def test_table_cells_are_read_one_at_a_time(self):
        self.assertEqual(guide("| `a | b <!-- x --> ` |\n| --- | --- |\n"
                               "| c <!-- y | z --> |\n"),
                         [(1, "`a"), (1, "b  `"), (3, "c <!-- y"), (3, "z -->")])

    def test_item_numbered_2_does_not_interrupt_a_paragraph(self):
        self.assertEqual(guide("See `a\n2. <!-- b` c. Shown?\n\nMore text.\n"),
                         [(1, "See `a"), (2, "<!-- b` c."), (2, "Shown?"), (4, "More text.")])

    def test_sibling_item_ends_the_paragraph(self):
        self.assertEqual(guide("1. Use ` here.\n2. Then <!-- b ` --> c.\n"),
                         [(1, "Use ` here."), (2, "Then  c.")])

    def test_nested_item_numbered_2_does_not_end_the_paragraph(self):
        self.assertEqual(guide("- See `a\n  2. b` c. Shown.\n"),
                         [(1, "See `a"), (2, "b` c."), (2, "Shown.")])


class CommentOpeners(unittest.TestCase):
    """A `<!--` that CommonMark reads as text hides nothing (QA round 1 on #1235)."""

    def test_escaped_opener_is_text(self):
        self.assertEqual(guide("An \\<!-- escaped. Shown.\n\nMore text.\n"),
                         [(1, "An <!-- escaped."), (1, "Shown."), (3, "More text.")])

    def test_opener_with_no_closer_in_its_paragraph_is_text(self):
        self.assertEqual(guide("A <!-- with no closer. Shown.\n\nMore -->text.\n"),
                         [(1, "A <!-- with no closer."), (1, "Shown."), (3, "More -->text.")])

    def test_short_comments_close_at_once(self):
        for opener in ("<!-->", "<!--->"):
            self.assertEqual(guide(f"A {opener} empty. Shown.\n\nMore -->text.\n"),
                             [(1, "A  empty."), (1, "Shown."), (3, "More -->text.")])

    def test_comment_across_lines_of_its_paragraph_is_hidden(self):
        self.assertEqual(guide("A <!-- spans\nlines --> here. Shown.\n"),
                         [(1, "A here."), (2, "Shown.")])

    def test_comment_block_with_no_closer_hides_to_the_end(self):
        self.assertEqual(guide("Text\n<!-- block\n\nstill hidden -->\nAfter.\n"),
                         [(1, "Text"), (5, "After.")])
        self.assertEqual(guide("Text\n<!-- block\n\nHidden too.\n"), [(1, "Text")])


class HtmlBlockStarts(unittest.TestCase):
    """The start of a CommonMark 0.31.2 HTML block of types 1 to 6 ends a paragraph, so a code
    span cannot pair past it and a real comment after it stays hidden; a line that only looks
    like one is paragraph text, so the span pairs (QA round 2 on #1235)."""

    def check(self, starts, ends):
        for start in starts:
            with self.subTest(start=start):
                tail = "Then  g." if ends else "Then <!-- e ` f --> g."
                self.assertEqual(guide(f"Use ` here.\n{start}\nThen <!-- e ` f --> g.\n"),
                                 [(1, f"Use ` here. {start} {tail}")])

    def test_type_1(self):
        self.check(["<script>", "<PRE class=x>", "<textarea"], True)
        self.check(["<scripts>", "<preview>"], False)

    def test_type_2(self):
        self.assertEqual(guide("Use ` here.\n<!-- c -->\nThen <!-- e ` f --> g.\n"),
                         [(1, "Use ` here."), (3, "Then  g.")])
        self.check(["<!- c", "<! -- c"], False)

    def test_type_3(self):
        self.check(["<?php", "<?xml version=1?>"], True)
        self.check(["< ?php"], False)

    def test_type_4(self):
        self.check(["<!DOCTYPE html>", "<!doctype html>"], True)
        self.check(["<!1>", "<! DOCTYPE>"], False)

    def test_type_5_is_case_sensitive(self):
        self.check(["<![CDATA[ x"], True)
        self.check(["<![cdata[", "<![Cdata["], False)
        self.assertEqual(guide("Text `x\n<![cdata[\nY <!-- z` kept. --> End.\n"),
                         [(1, "Text `x <![cdata[ Y <!-- z` kept. --> End.")])

    def test_type_6_follows_commonmark_0_31_2(self):
        self.check(["<search>", "<DIV>", "</div>", "<hr/>", "<p", "<Section class=x>"], True)
        self.check(["<source>", "<span>", "<divx>", "<p-x>"], False)


class Round2Layouts(unittest.TestCase):
    """Layouts in which QA round 2 on #1235 found a real comment shown or text hidden."""

    def test_reference_definition_pairs_no_backtick_with_later_text(self):
        self.assertEqual(guide("[x]: /url`foo\nText <!-- hidden ` --> visible.\n"),
                         [(1, "[x]: /url`foo"), (2, "Text  visible.")])
        self.assertEqual(guide('[r]: http://e.com "`"\nText <!-- h --> `x`.\n'),
                         [(1, '[r]: http://e.com "`"'), (2, "Text  `x`.")])

    def test_reference_definition_cannot_interrupt_a_paragraph(self):
        self.assertEqual(guide("Para `x\n[r]: /u\nb <!-- c --> `\n"),
                         [(1, "Para `x [r]: /u b <!-- c --> `")])

    def test_link_destination_and_title_open_nothing(self):
        for link in ('[a](http://e.com "`")', "[a](http://e.com/`)"):
            with self.subTest(link=link):
                self.assertEqual(guide(f"See {link} <!-- h --> and `x` y.\n"),
                                 [(1, "See a  and `x` y.")])
        self.assertEqual(guide('See [a](http://e.com "<!--") Shown --> b.\n'),
                         [(1, "See a Shown --> b.")])

    def test_comment_block_ends_with_its_closing_line(self):
        self.assertEqual(guide("<!-- c --> `x\nb <!-- h --> `\n"), [(1, "`x"), (2, "b  `")])
        self.assertEqual(guide("<!--\nc\n--> `x\nb <!-- h --> `\n"), [(3, "`x"), (4, "b  `")])

    def test_item_numbered_2_opens_no_comment_block(self):
        for marker in ("2.", "2)"):
            with self.subTest(marker=marker):
                self.assertEqual(guide(f"See a\n{marker} <!-- Shown c.\n\nMore shown.\n"),
                                 [(1, "See a"), (2, "<!-- Shown c."), (4, "More shown.")])


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
