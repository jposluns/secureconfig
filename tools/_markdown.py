#!/usr/bin/env python3
"""One definition of a fenced code block, shared by the gates that need one.

Two gates used to carry their own fence tracker. They disagreed: one compared the marker
CHARACTER and the other did not, and neither compared the marker LENGTH. Review
demonstrated both halves of that gap. A closing run shorter than the opening run does not
close the block, so a three-backtick line inside a four-backtick fence read as a close and
handed the rest of the block to whichever scanner was watching; the same line read as an
open in the other gate. Both failure directions were shown with real inputs: an insecure
command hidden after the false close, and ordinary Python rejected as prose after it.

CommonMark's rule, which this implements: a fence opens with three or more backticks or
three or more tildes, indented no more than three spaces. It closes on a line whose run
uses the SAME character and is AT LEAST AS LONG, followed by only spaces or tabs. An
opening line may carry an info string; a closing line may not.

https://spec.commonmark.org/0.31.2/#fenced-code-blocks

This is not a Markdown parser. It does not know about list indentation, HTML blocks, or
link reference definitions, and it is not trying to. It answers one question for both
gates in the same way, so that a construction cannot be a fence in one and prose in the
other. A fence indented four or more spaces, which is what a fence nested two list levels
deep looks like, is not recognized. A renderer shows it as code and a reader copies from it,
and no guide in this corpus has one today, so this is disclosed rather than handled.

This module also provides reason_present(), a rule for whether a waiver, allowlist, exception
or baseline reason is present, and BLANK_CATEGORIES, the set it reads. Both are defined in
tools/_reason.py, which imports only the standard library, and imported here, so a reader that
imports them from this module keeps working unchanged. These readers import reason_present()
from this module: load_baseline() in tools/check_verify_marking.py, Allowlist.load() in
tools/check_bracket_ranges.py, waiver_reasoned() in tools/gen_guide_quality.py,
parse_exceptions() in tools/export_lists.py, _analyze_fence() and _scan_inline() in
tools/check_guard_conventions.py and _waived_lines() in tools/check_unfiltered_ss.py. The
regular expressions of the last two gates find a waiver, and reason_present() then judges the
reason each one captures: WAIVER_RE in both, C4_WAIVER_RE, which applies only to a reason that
WAIVER_RE has matched, and INLINE_WAIVER_RE. tools/export_lists.py calls it after its
split_lines() has refused any line that holds a control or format character. The two parsers of
tools/redirects_allowlist.txt, allowlist_entries() in tools/check_draft.py and read_allowlist()
in tools/gen_hosted.py, import it from tools/_reason.py instead. The Pages build,
scripts/pages-build.sh, runs tools/check_draft.py directly and reaches tools/gen_hosted.py
only through the imports of tools/check_hosted.py and scripts/build-site.py, which it runs.
tools/test_pages_build.py requires every module that build reaches, by an import at any depth,
to import only the standard library and this repository's modules. It follows the import in
body_lines() here to tools/version_basis.py, which imports markdown-it-py, so it fails when
either parser imports this module. Two other modules use the parser in tools/gen_hosted.py
rather than one of their own: tools/check_hosted.py calls its read_allowlist() directly and
through its redirects_text(), and scripts/build-site.py calls it through redirects_text(). A
search of the tree of #1369 found seven places that judged a reason without reason_present(),
and TODO row 3.111 recorded them; the search may have missed some. All seven now call it. A
self-test fixture that copies this module needs tools/_reason.py too.
"""
import re

from _reason import BLANK_CATEGORIES, reason_present  # noqa: F401  (defined there, row 3.111)

FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


class Fences:
    """Line-by-line fence state. Feed every line in order; ask `inside` after each.

    Usage is deliberately blunt:

        f = Fences()
        for line in text.splitlines():
            if f.feed(line):
                continue        # the line IS a fence marker, not content
            if f.inside:
                ...             # code
            else:
                ...             # prose

    `feed` returns True for an opening or closing marker line, which belongs to neither
    the code nor the prose around it.
    """

    def __init__(self):
        self.char = None
        self.length = 0

    @property
    def inside(self):
        return self.char is not None

    def close(self):
        """Force the block closed, for a container that ended before its fence did."""
        self.char, self.length = None, 0

    def feed(self, line):
        m = FENCE_RE.match(line)
        if not m:
            return False
        run, rest = m.group(1), m.group(2)
        char, length = run[0], len(run)
        if self.char is None:
            # An opening backtick fence may not carry a backtick in its info string,
            # because the info string would be ambiguous with a closing run.
            if char == "`" and "`" in rest:
                return False
            self.char, self.length = char, length
            return True
        # Only spaces or tabs may follow a closing run. str.strip() would also remove a
        # non-breaking space or other Unicode whitespace, which CommonMark treats as content.
        if char == self.char and length >= self.length and not rest.strip(" \t"):
            self.char, self.length = None, 0
            return True
        # A shorter run, a different character, or a trailing info string is CONTENT of
        # the open block, not a close.
        return False


def body_lines(text):
    """Mask legacy front matter only; EOF metadata is already fenced Markdown."""
    from version_basis import split_front_matter
    data, body = split_front_matter(text)
    if data is None:
        return text.splitlines()
    prefix = text[:len(text) - len(body)]
    return [''] * prefix.count('\n') + body.splitlines()
