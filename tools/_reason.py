#!/usr/bin/env python3
"""One rule for whether a waiver, allowlist, exception or baseline reason is present.

reason_present() lived in tools/_markdown.py until TODO row 3.111 moved it here. This module
imports only the standard library, so the two parsers of tools/redirects_allowlist.txt,
tools/check_draft.py and tools/gen_hosted.py, can import it. scripts/pages-build.sh runs both,
and tools/test_pages_build.py requires every module that build reaches to import only the
standard library and this repository's modules. tools/_markdown.py reaches markdown-it-py through
body_lines(), which imports tools/version_basis.py, so the two parsers cannot import that module.
tools/_markdown.py imports reason_present() and BLANK_CATEGORIES from here, so every reader that
imports them from tools/_markdown.py gets these same objects. Keep this module to the standard
library: tools/test_pages_build.py names it and fails when the Pages build stops reaching it.
"""
import unicodedata

# The general categories a reason may not be made of alone (row 3.106). Cf holds the format
# characters, such as U+200B ZERO WIDTH SPACE, U+FEFF ZERO WIDTH NO-BREAK SPACE and U+2060 WORD
# JOINER, which str.isspace() does not count as whitespace and which Unicode lists as default
# ignorable code points, so a renderer normally shows nothing for them. A few Cf characters,
# such as U+0600 ARABIC NUMBER SIGN, are drawn, but they format the text around them, so a
# reason made of them alone still says nothing. Zs, Zl and Zp hold the space, line and
# paragraph separators, which str.isspace() already counts, since Python counts every Zs
# character and every character of bidirectional class WS, B or S; naming them keeps the rule
# whole on its own. Whitespace controls such as TAB and LF are Cc and stay blank through
# str.isspace().
BLANK_CATEGORIES = frozenset({"Cf", "Zs", "Zl", "Zp"})


def reason_present(text):
    """Whether `text` holds a character that is neither whitespace nor in BLANK_CATEGORIES.

    A reason made only of such characters shows as nothing, so it is no reason. Before row
    3.106 the first three readers to call this function judged a reason with str.strip(),
    which removes whitespace but not a format character such as U+200B, so a reason of U+200B
    alone passed; before row 3.111 the two parsers of tools/redirects_allowlist.txt did too.
    The categories come from the unicodedata module of the running Python. Other characters
    that may show as nothing, such as a lone combining mark (Mn), a control character that is
    not whitespace (Cc), U+3164 HANGUL FILLER (Lo) or U+2800 BRAILLE PATTERN BLANK (So), count
    as text.
    """
    return any(not ch.isspace() and unicodedata.category(ch) not in BLANK_CATEGORIES
               for ch in text)
