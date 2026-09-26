#!/usr/bin/env python3
r"""Flag bracket ranges in fenced bash blocks: outside the C locale a range can match non-ASCII.

WHY THIS EXISTS. A guard such as `case "$1" in *[!A-Za-z0-9.-]*) exit 2 ;; esac` or
`[[ "$t" =~ ^[A-Za-z0-9_.-]+$ ]]` reads as an ASCII accept list, and whether it is one depends on
the tool, the locale and a shell option. The #356 review found `é` matching both `[A-Za-z]` and
`[0-9a-f]` in GNU grep under en_US.UTF-8. Reproduced on 2026-09-26 with GNU grep 3.12, GNU sed 4.9,
gawk 5.3, dash, bash 5.3.9 and glibc's en_US.utf8, C.utf8 and C locales:

  - Under en_US.utf8, `grep -E` and `sed -E` matched é, É, ß, a fullwidth e, the Kelvin sign
    U+212A and the long s U+017F with `[A-Za-z]`, and é, a superscript two and the Arabic-Indic
    digit three with `[0-9a-f]`. `[0-9]` on its own matched none of the samples in either tool.
  - Under en_US.utf8, bash `[[ =~ ]]`, which hands the pattern to the C library, accepted every
    one of those samples with `^[A-Za-z0-9_.-]+$`, and accepted the superscript two and the
    Arabic-Indic three with `^[0-9]+$`. No shell option changes this.
  - bash `case` was ASCII only while `globasciiranges` was on, which bash 5.x sets by default
    and a build or a `shopt -u` can turn off; with it off, `*[!A-Za-z0-9.-]*` let every sample
    through. dash's `case` and gawk were ASCII only in every locale tried.
  - Under C.utf8 and C, every range was ASCII only. A POSIX class is not a fix by itself:
    `[[:alnum:]]` matched é, ß and the Arabic-Indic three under C.utf8 as well.

A reader pastes these blocks into whatever locale their terminal has, so a guard that refuses a
non-ASCII value only in some locales does not refuse it.

THE MODEL. Every physical line of every fenced bash block of a guide, README.md,
controls-reference.md or CONTRIBUTING.md (the same blocks the shell-block gate lints, from
`check_shell_blocks.blocks_of`) is read on its own, here-document bodies included. The gate does
no bash lexing at all: no quotes, no comments, no here-documents, no expansions and no command
separators. Three earlier versions of this gate lexed bash, first to join lines and then only to
decide whether an in-block waiver comment was real, and adversarial review found a new way around
the lexing each time; round 3 alone found an escaped space making a data `#` read as a comment, a
trailing backslash dropping an open quote, a partly recognized here-document delimiter ending a
body early, a fake POSIX atom swallowing a validator between two printf arguments, and quoting
inside a parameter-removal pattern misread as closing the expansion. This version removes the
attack surface instead of patching it again: a waiver decision reads nothing in the block,
because waivers do not live in blocks at all.

On each physical line, two things are findings:

  - A bracket expression holding a range (`X-Y`, hyphen neither first nor last). POSIX rules
    apply within the line: a leading `^` negates, a `]` first in the list is a literal and can
    start a range (`[]-z]`, `[^]-z]`), `[:class:]`, `[=x=]` and `[.x.]` are single items, and a
    glob's `!` is an ordinary character, so `[!0-9]` still holds 0-9 and a `]` right after `[!`
    is a literal whenever a later `]` on the line closes the expression. An atom counts as one
    item only when its interior is the plain name or character those forms carry (letters and
    digits, or any one character that is not `[`): round 3 built `[[:` and `:]]` out of two
    printf arguments and an unconstrained scan swallowed the live validator between them, so
    anything else is read as ordinary characters, and a range inside it is still seen. A `[]`
    or `[^]` that no later `]` on the line closes is the empty pair of a JSON, jq or JMESPath
    expression, which no tool reads as a bracket expression. A backslash does not hide a
    bracket: the shell removes an unquoted `\` before the tool sees `[`, so `grep -E \[0-9] f`
    holds a live range, and a quoted `\[` is flagged too rather than guessed about.
  - A `[` that nothing on its own physical line closes. A set split across lines by any means, a
    backslash continuation, a quoted newline (`re='^[A-Z` then a line `a-z]+$'`, which glibc's
    regcomp reads across the newline), or a multi-line data list, lands here by construction,
    without the gate having to know which of those it was.

A close immediately preceded by a backslash or quote is ambiguous. A quote immediately after
`]` also makes it ambiguous when that same quote occurs inside the list. Besides the ordinary
reading, the gate reads that `]` as a member and continues to the next close, repeating at each
ambiguous close. Either reading holding a range, or an alternative running off the physical
line, is a finding. This is a local character test, not quote or escape lexing. Requiring an
interior quote for the quote-after case keeps `'[0123456789]'` and "[[:digit:]]" clean: outside
quoting does not hide the closing bracket from a regex engine, and quoting a glob's opening
bracket makes that opener literal too. The ordinary close still bounds the outer scan, so an
alternative cannot swallow a separate expression. There is at most one finding per opener.

Shell text, comments and here-document bodies are all read the same way: a regex stored in a
variable, a `case` alternative on its own line, a script written to a file through a
here-document and a commented-out probe are validators too. The gate does not ask which tool
reads the pattern. A JSON array holding a hyphenated string, `["app-data"]`, reads as a range as
well and takes an allowlist entry; a rule that skipped it would also skip a regex that happened
to start with a quote.

THE FIX is a spelled-out set, which means the same thing in every locale, tool and shell:
`[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]`. `model-servers.md` already
carried `[!0123456789abcdef]` from #350 and #355. A POSIX class in an accept list is sound only
under an explicit `LC_ALL=C` that covers the whole check, since `[[:alnum:]]` accepts non-ASCII
letters under C.utf8. A class in a reject list, such as refusing the locale's control or
whitespace characters, is sound in any locale, because a wider class only refuses more. This gate
does not read POSIX classes or `LC_ALL`: a class needs no waiver, and a range under `LC_ALL=C`
still does.

THE ALLOWLIST. A range that is not a validator (a search pattern, a JSON request body, a label
in a format string) is waived in tools/bracket_ranges_allow.txt, never in the guide. Earlier
versions took a trailing `bracket-ranges: allow` comment in the block, and deciding whether that
comment was real is exactly the lexing this version removes, so a guide line still carrying that
marker (a `#`, then optional blanks, then `bracket-ranges:`) is itself a finding, anywhere in the
file. Each allowlist entry is one line

    <guide-file> TAB <exact physical line text> TAB <reason>

and a line starting with `#` is a comment. A finding is waived only when its guide's file name
and its line's exact text both match an entry, the whole line as the block extraction yields it
(the opening fence's own indentation removed, nothing else changed), never a substring, so an
entry cannot quietly keep covering a line that grew a second command or a second range; an entry
waives every finding on its one line at once, which is what a reviewer reading that line sees.
Each flagged occurrence of a line consumes one entry, so a duplicate entry is legal exactly while
the same text genuinely occurs that many times, and every entry left unconsumed at the end of a
repository scan is a finding ("stale allowlist entry"): an edit cannot leave a dead waiver
behind. An entry with fewer than three fields, an empty guide, an empty text or an empty reason
is a finding. The guide name is read up to the first TAB and the reason back from the last, so
the text may itself hold a TAB; a reason may not.

WHAT THIS IS NOT. A shell parser, and not proof that a guard is correct. The model is
deliberately conservative: everything in the first list below is over-flagging that fails
closed, listed honestly; what the gate still does not see at all is in the second. Each is a
recorded case in tools/test_bracket_ranges.py so that a change is loud.

  Over-flagged, by design (restructure the line, spell the set out, or allowlist the line):
  - A multi-line data list, a JSON array or Python list whose `[` closes on a later line, is an
    unclosed-bracket finding on the line of the `[`. Keep such a list on one line, use a
    bracket-free shape (a Python tuple, a split string), or allowlist the opening line.
  - A quoted literal `\[a-z\]`, an array subscript `a[i-1]` in an expansion or in arithmetic,
    and a slice `[1:-1]` are flagged: the gate does not know a backslash is quoted or a context
    is arithmetic, and guessing was what the lexing models got wrong.
  - A malformed atom, `[[:alpha]` with no closing `:]` on its line, is read as ordinary
    characters rather than an atom, so `alpha` contributes no range but a live range beside it
    is still seen.
  - Ambiguous closes in data, such as `["read"]`, `d["key"]` or the regex `[^"]`, can produce
    an unclosed alternative even when the ordinary reading is harmless. On the 411-block,
    99-guide corpus, allowing every quote-after close added 17 falsely flagged lines; requiring
    an interior matching quote reduced that to 8. Both rules added one expression on each of
    2 already waived lines. The narrowed rule has 14 consumed entries waiving 16 expressions;
    the 8 new entries name non-validator uses, never locale-dependent accept lists.
  - An allowlist entry waives its whole line: one of two ranges on a line cannot be waived
    alone. Changing its text or guide breaks its entry, but moving unchanged text within the
    same guide does not. Neither does changing surrounding lines: a continued printf argument
    can become a grep validator while its exact line remains waived. Review the context on
    every edit; the key binds text and guide, not location or interpretation.

  Still not seen:
  - Ranges with no brackets: `tr -dc 'A-Za-z0-9'`.
  - POSIX classes and `\w`, although they are locale dependent too.
  - A `[` or `[[` standing as its own word before whitespace is read as the test command, even
    when it sits inside a regex or other data: `re='^ [ a-z]+$'` carries a live range into
    glibc's regcomp and is not flagged.
  - A range assembled at runtime, where no literal `X-Y` sits between a literal `[` and `]` in
    the source: endpoints spliced from variables (`lo='a-'; hi=z; re="^[$lo$hi]+$"`), brackets
    built by escapes (`$'\x5bA-Za-z\x5d'`, `$'^[a\x2dz]+$'`), and their combinations. These are
    the bracketed siblings of the `tr` case: a lexical gate that does not expand words cannot
    see them, and rule 5's tracing obligation is what covers them.
  - Fence extraction has exactly the limits `check_shell_blocks.blocks_of` discloses, and a
    fence whose info string is not bash (`sh`, `zsh`) is not read.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _walk import walk_files  # noqa: E402  fail-closed tree walk
from check_shell_blocks import SKIP_DIRS, blocks_of  # noqa: E402  one definition of a bash block

# Root-level documents about the repository, which a reader does not copy from: the files
# not_a_guide() in tools/run_all_checks.sh names, less CONTRIBUTING.md, whose example blocks are
# the shapes new guides are built from, and controls-reference.md, which site/llms.txt lists.
NOT_A_GUIDE = frozenset(("CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "README.sources.md", "TODO.md",
                         "DONE.md", "DECISIONS.md", "PENDING-DECISIONS.md", "SECURITY.md"))
# The waivers live here, one `<guide> TAB <exact line text> TAB <reason>` entry per line.
ALLOWLIST = "bracket_ranges_allow.txt"
# The retired in-block waiver marker. A guide line holding one is a finding, wherever it sits:
# deciding whether such a comment is real is the lexing this gate no longer does.
MARKERISH_RE = re.compile(r"#[ \t]*bracket-ranges:")
# A `[` or `[[` after one of these and before whitespace is the test command.
TEST_BEFORE = " \t;&|(!"
# The interior an atom may carry and still count as one item: a class name, an equivalence
# class or a collating symbol. Anything longer or stranger is scanned as ordinary characters.
ATOM_RE = re.compile(r"[A-Za-z0-9]+\Z")
HINT = ("outside the C locale a bracket range can match non-ASCII letters and digits (GNU grep, "
        "GNU sed and bash [[ =~ ]] were observed doing it under en_US.utf8, and bash case does "
        "it with globasciiranges off), so a validator written with one accepts values it claims "
        "to refuse. Spell the set out, as in "
        "[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. Where the range is "
        "not a validator, add a '<guide> TAB <exact line text> TAB <reason>' entry to "
        "tools/bracket_ranges_allow.txt; the entry waives that one physical line and nothing "
        "else. See tools/check_bracket_ranges.py.")


def _atom(text, j, n):
    """The close index of the `[:class:]`, `[=x=]` or `[.x.]` atom at text[j], or None.

    An atom counts only when its interior is the single item those forms carry: letters and
    digits, or any one character that is not `[`. Round 3 assembled `[[:` and `:]]` from two
    printf arguments, and an unconstrained forward search swallowed the live validator between
    them as one atom; an interior holding a quote, a space or a `[` is not an atom here, and
    the caller scans it as ordinary characters instead, which fails closed.
    """
    close = text.find(text[j + 1] + "]", j + 2, n)
    if close == -1:
        return None
    interior = text[j + 2:close]
    if ATOM_RE.fullmatch(interior) or (len(interior) == 1 and interior != "["):
        return close
    return None


def _parse_list(text, j, prev):
    """Read a bracket list from text[j], with `prev` the item already read or None.

    Returns (close_index, ranges), or (None, ranges) when the end of the line comes first.
    """
    n, ranges = len(text), []
    while j < n:
        c = text[j]
        if c == "]":
            return j, ranges
        if c == "[" and text[j + 1:j + 2] in (":", "=", "."):
            close = _atom(text, j, n)
            if close is not None:
                # A class cannot be a range endpoint; an equivalence or collating symbol can.
                prev = None if text[j + 1] == ":" else text[j:close + 2]
                j = close + 2
                continue
            # Not an atom: the `[` is an ordinary item, scanned like any other character, so a
            # range hidden past a fake atom opener is still seen.
        if c == "-" and prev is not None and j + 1 < n and text[j + 1] != "]":
            k = j + 1
            if text[k] == "[" and text[k + 1:k + 2] in ("=", "."):
                close = _atom(text, k, n)
                if close is not None:
                    end, j = text[k:close + 2], close + 2
                else:
                    end, j = text[k], k + 1
            elif text[k] == "[" and text[k + 1:k + 2] == ":":
                close = _atom(text, k, n)
                if close is not None:
                    prev, j = None, j + 1
                    continue
                end, j = text[k], k + 1
            else:
                end, j = text[k], k + 1
            ranges.append(prev + "-" + end)
            prev = None
            continue
        prev = c
        j += 1
    return None, ranges


def _parse_bracket(text, i):
    """Parse the bracket expression opening at text[i]. Returns (close_index, ranges).

    POSIX rules: a leading `^` negates, a `]` first in the list is a literal and may start a
    range, `[:class:]`, `[=x=]` and `[.x.]` are single items when _atom recognizes them, and a
    hyphen that is neither first nor last joins the items on either side of it into a range. A
    glob's `!` is read as an ordinary character, so `[!0-9]` still holds the range 0-9 and
    `[!-~]`, which a regex reads as the range ! to ~, is flagged; a `]` right after `[!` is
    read as a glob reads it, a literal, whenever a later `]` on the line closes the expression.
    A `[]` or `[^]` that no later `]` on the line closes is the empty pair of a JSON, jq or
    JMESPath expression, which no tool reads as a bracket expression. A backslash is an
    ordinary character inside brackets. Returns (None, ranges) when nothing closes the
    expression on this line.
    """
    j = i + 1
    if text[j:j + 1] == "^":
        j += 1
    if text[j:j + 1] == "]" or text[j:j + 2] == "!]":
        close, ranges = _parse_list(text, j + 1 if text[j] == "]" else j + 2, "]")
        if close is not None:
            return close, ranges
    # Nothing later on the line closes it, so `[]` and `[^]` are an empty pair, `[!]` a set.
    return _parse_list(text, j, None)


def _ambiguous_close(text, start, close):
    """A local ambiguity test, with no quote state or escape decoding.

    A backslash or quote immediately before `]` permits a literal-member reading. A quote
    immediately after it does too, if that same quote occurs inside the list. Without an
    interior quote, the latter is just outside quoting: it does not hide a regex's close,
    and quoting a glob's opening `[` makes that opener literal too.
    """
    before, after = text[close - 1], text[close + 1:close + 2]
    return before in "\\'\"" or (after in ("'", '"') and after in text[start + 1:close])


def bracket_hits(text):
    """Yield one description per bracket expression in one line's text holding a range, and per
    `[` left open at the end of the line. A closed expression is stepped over whole, so a nested
    `[` inside it is not reported twice. Ambiguous closes also admit a literal-member reading;
    a range or an unclosed alternative is a finding for the original opener. A backslash before
    a `[` does not hide it: unquoted, the shell removes it and the tool sees a live bracket."""
    i, n = 0, len(text)
    while i < n:
        if text[i] != "[":
            i += 1
            continue
        word_end = i + 2 if text.startswith("[[", i) else i + 1
        if (i == 0 or text[i - 1] in TEST_BEFORE) and (word_end == n or text[word_end] in " \t"):
            i = word_end
            continue
        close, ranges = _parse_bracket(text, i)
        first_close = close
        # Keep the ordinary boundary for the outer scan, so a possible continuation cannot
        # swallow another expression. One finding per opener suffices if either reading has
        # a range. Otherwise try each ambiguous close as a literal member, without lexing.
        while close is not None and not ranges and _ambiguous_close(text, i, close):
            close, ranges = _parse_list(text, close + 1, "]")
        if close is None:
            yield (f"{text[i:i + 60].rstrip()} opens a bracket expression that nothing closes "
                   f"on its physical line in at least one reading, so a range in it cannot "
                   f"be ruled out,")
            i = first_close + 1 if first_close is not None else i + 1
            continue
        if ranges:
            noun = "range" if len(ranges) == 1 else "ranges"
            yield f"{text[i:close + 1]} holds the {noun} {', '.join(ranges)}"
        i = first_close + 1


class Allowlist:
    """The entries of tools/bracket_ranges_allow.txt, each consumable by one flagged line.

    `findings` holds what loading itself flagged (a malformed entry, an empty field); `take`
    consumes one entry for one flagged occurrence of a line; `stale` names every entry nothing
    consumed, so an entry cannot outlive the line it was written for.
    """

    def __init__(self):
        self.findings, self.n_entries, self._avail = [], 0, {}

    @classmethod
    def load(cls, path):
        """Read the allowlist at `path`. A missing file is an empty allowlist, which only
        refuses more; a file that exists but cannot be read raises (OSError or
        UnicodeDecodeError), which main turns into a failed gate rather than an empty list."""
        allow = cls()
        if not path.exists():
            return allow
        where = f"tools/{path.name}"
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if not raw.strip() or raw.startswith("#"):
                continue
            parts = raw.split("\t")
            guide = parts[0]
            text = "\t".join(parts[1:-1])
            reason = parts[-1] if len(parts) > 1 else ""
            if len(parts) < 3 or not guide.strip() or not text:
                allow.findings.append(f"{where}:{lineno}: malformed allowlist entry: three "
                                      f"TAB-separated fields, guide, exact line text, reason")
                continue
            if not reason.strip():
                allow.findings.append(f"{where}:{lineno}: allowlist entry with an empty "
                                      f"reason: say why the line is not a validator")
                continue
            allow._avail.setdefault((guide, text), []).append((lineno, where))
            allow.n_entries += 1
        return allow

    def take(self, guide, text):
        """Consume one entry for one flagged occurrence of `text` in `guide`, if one is left."""
        left = self._avail.get((guide, text))
        if not left:
            return False
        left.pop(0)
        return True

    def stale(self):
        """One finding per entry that no flagged line consumed."""
        out = []
        for (guide, _), left in self._avail.items():
            out.extend((lineno, f"{where}:{lineno}: stale allowlist entry: no flagged line of "
                                f"{guide} matches its exact text") for lineno, where in left)
        return [msg for _, msg in sorted(out)]


def scan_blocks(name, blocks, allow):
    """Scan one guide's bash blocks, one physical line at a time, against `allow`.

    Returns (findings, n_blocks, n_waived). Every physical line is read the same way, a
    here-document body like any other; a line whose findings the allowlist covers consumes one
    entry for that occurrence; n_waived counts expressions, not entries.
    """
    findings, n_blocks, n_waived = [], 0, 0
    for start, body in blocks:
        n_blocks += 1
        for idx, raw in enumerate(body.split("\n")):
            hits = list(bracket_hits(raw))
            if not hits:
                continue
            if allow.take(name, raw):
                n_waived += len(hits)
                continue
            findings.extend(f"{name}:{start + idx}: {what} and no allowlist entry covers its "
                            f"line" for what in hits)
    return findings, n_blocks, n_waived


def scan_path(path, allow=None):
    """Scan one guide file: its whole text for the retired in-block marker, and every physical
    line of its bash blocks for ranges and unclosed brackets. Raises what blocks_of raises on a
    file it cannot read. With no allowlist given, nothing is waived."""
    allow = Allowlist() if allow is None else allow
    findings = [f"{path.name}:{lineno}: in-guide bracket-ranges marker: waivers live in "
                f"tools/{ALLOWLIST}, keyed by the guide and the exact line"
                for lineno, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1)
                if MARKERISH_RE.search(raw)]
    found, n_blocks, n_waived = scan_blocks(path.name, list(blocks_of(path)), allow)
    return findings + found, n_blocks, n_waived


def scan_repo(root):
    """Scan every guide under root against the allowlist.

    Returns (findings, n_files, n_blocks, n_waived), the stale-entry findings included.
    """
    allow = Allowlist.load(root / "tools" / ALLOWLIST)
    paths = sorted(walk_files(root, SKIP_DIRS, suffixes={".md"}))
    findings, n_files, n_blocks, n_waived = list(allow.findings), 0, 0, 0
    for path in paths:
        if path.parent != root or path.name in NOT_A_GUIDE:
            continue
        try:
            found, blocks_here, waived = scan_path(path, allow)
        except Exception as exc:
            findings.append(f"{path.name}: unreadable ({exc})")
            continue
        findings.extend(found)
        n_blocks += blocks_here
        n_waived += waived
        n_files += 1 if blocks_here else 0
    findings.extend(allow.stale())
    return findings, n_files, n_blocks, n_waived


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        findings, n_files, n_blocks, n_waived = scan_repo(root)
    except Exception as exc:
        print(f"  FAIL  could not scan the repository: {exc}")
        return 1
    if not findings and not n_blocks:
        # A pass over nothing is not a pass.
        findings.append("no bash block was found in any guide, so nothing was checked")
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        print(f"  FAIL  {HINT}")
        return 1
    print(f"  ok    no unwaived bracket range in {n_blocks} bash blocks across {n_files} "
          f"guides ({n_waived} expressions waived by tools/{ALLOWLIST})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
