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
non-ASCII value only in some locales does not refuse it. The corpus's `case` guards had relied on
`globasciiranges` without saying so, and its `[[ =~ ]]` guards had relied on nothing.

WHAT THIS CATCHES. Every bracket expression holding a range (`X-Y`, with the hyphen neither first
nor last) inside a fenced bash block of a guide, README.md, controls-reference.md or
CONTRIBUTING.md, taken from `check_shell_blocks.blocks_of` so that "a fenced bash block" means
the same set of blocks the shell-block gate lints. Shell text, comments and here-document bodies
are all read: a regex stored in a variable, a `case` alternative on a line of its own and a script
written to a file through a here-document are validators too, and a commented-out probe is still
a command a reader uncomments. The gate does not ask which tool reads the pattern. A JSON array
holding a hyphenated string, `["app-data"]`, reads as a range as well and takes a marker; a rule
that skipped it would also skip a regex that happened to start with a quote.

THE FIX is a spelled-out set, which means the same thing in every locale, tool and shell:
`[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]`. `model-servers.md` already
carried `[!0123456789abcdef]` from #350 and #355. A POSIX class is sound only under an explicit
`LC_ALL=C` that covers the whole check. This gate does not read `LC_ALL`: a class under it needs
no marker, and a range under it still does.

THE MARKER. A range that is not a validator (a search pattern, a label in a format string, a
JSON request body) carries a shell comment

    # bracket-ranges: allow <reason>

in the same shape as `# guard-conventions: allow` and `# unfiltered-ss: allow`, either at the
end of the command, which covers that command, or on a comment line immediately before it,
which covers the next command and nothing further. A command is a logical one: backslash
continuations, a quoted string left open across lines and here-document bodies belong to the
command that opened them, so a marker on a here-document's opening line covers its body. The
reason is required. The marker must be a real comment, so the same text inside a quoted string
or a here-document body does not count. A marker that covers no range is reported as stale, so
one cannot outlive the range it was written for and go on covering whatever is written there
next. A validator never takes the marker: it takes the spelled-out set.

WHAT THIS IS NOT. A shell parser, and not proof that a guard is correct. Known gaps, each
recorded as a case in tools/test_bracket_ranges.py so that closing one is loud:

  - Only bracket expressions are read. `tr -dc 'A-Za-z0-9'` has no brackets and is not flagged.
  - POSIX classes and `\w` are not flagged, although they are locale dependent too.
  - A `[` or `[[` standing as its own word before whitespace is read as the test command.
  - Quote state carries across lines, but `$(...)` nesting is not modelled. A `<<` in shell
    arithmetic is read as a here-document opener; the rest of the block is then data, where a
    range is still reported and a marker no longer counts, which fails closed.
  - Fence extraction has exactly the limits `check_shell_blocks.blocks_of` discloses.
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
# The comment must open with the marker and give a reason, as the sibling gates' waivers must.
MARKER_RE = re.compile(r"#[ \t]*bracket-ranges:[ \t]*allow[ \t]+\S")
# A `#` begins a comment at the start of a word, which these characters end.
COMMENT_BEFORE = " \t;&|()"
# A `[` or `[[` after one of these and before whitespace is the test command.
TEST_BEFORE = " \t;&|(!"
# A here-document delimiter: single-quoted, double-quoted, backslash-quoted or bare.
HEREDOC_WORD_RE = re.compile(r"""'([^']*)'|"([^"]*)"|\\?([A-Za-z0-9_.+-]+)""")
HINT = ("outside the C locale a bracket range can match non-ASCII letters and digits (GNU grep, "
        "GNU sed and bash [[ =~ ]] were observed doing it under en_US.utf8, and bash case does "
        "it with globasciiranges off), so a validator written with one accepts values it claims "
        "to refuse. Spell the set out, as in "
        "[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. Where the range is "
        "not a validator, put '# bracket-ranges: allow <reason>' at the end of the command or on "
        "a comment line directly above it. See tools/check_bracket_ranges.py.")


def _heredoc_word(line, i):
    """The delimiter of a `<<` or `<<-` at index i: ((word, strip_tabs), next_index)."""
    j = i + 2
    strip = line[j:j + 1] == "-"
    if strip:
        j += 1
    while j < len(line) and line[j] in " \t":
        j += 1
    m = HEREDOC_WORD_RE.match(line, j)
    if not m:
        return None, j
    word = next(g for g in m.groups() if g is not None)
    return (word, strip), m.end()


def _scan(line, quote):
    """Split one physical shell line. Returns (code, comment, quote, heredocs, continues).

    `quote` is the quote the previous line left open, if any, and the one returned is the quote
    this line leaves open. A comment ends the line, so a backslash inside it continues nothing.
    """
    heredocs, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if quote == "'":
            if c == "'":
                quote = None
            i += 1
            continue
        if quote is not None:
            if c == "\\":
                i += 2
                continue
            if (quote == '"' and c == '"') or (quote == "$'" and c == "'"):
                quote = None
            i += 1
            continue
        if c == "\\":
            i += 2
            continue
        if c == "$" and line[i + 1:i + 2] == "'":
            quote, i = "$'", i + 2
            continue
        if c in "'\"":
            quote, i = c, i + 1
            continue
        if c == "#" and (i == 0 or line[i - 1] in COMMENT_BEFORE):
            return line[:i], line[i:], None, heredocs, False
        if line.startswith("<<<", i):
            i += 3
            continue
        if line.startswith("<<", i):
            word, i = _heredoc_word(line, i)
            if word is not None:
                heredocs.append(word)
            continue
        i += 1
    trailing = len(line) - len(line.rstrip("\\"))
    return line, "", quote, heredocs, quote is None and trailing % 2 == 1


def commands(lines):
    """Group a block's physical lines into logical commands.

    Each command is a list of (index, code, comment, data) tuples, one per physical line, where
    `data` marks a here-document body line, all of whose text is data.
    """
    out, cur, quote, pending = [], [], None, []
    for idx, line in enumerate(lines):
        if pending:
            word, strip = pending[0]
            cur.append((idx, line, "", True))
            if (line.lstrip("\t") if strip else line) == word:
                pending.pop(0)
                if not pending and quote is None:
                    out.append(cur)
                    cur = []
            continue
        code, comment, quote, opened, continues = _scan(line, quote)
        cur.append((idx, code, comment, False))
        pending.extend(opened)
        if not pending and quote is None and not continues:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _escaped(text, i):
    k = i
    while k > 0 and text[k - 1] == "\\":
        k -= 1
    return (i - k) % 2 == 1


def _parse_bracket(text, i):
    """Parse the bracket expression opening at text[i]. Returns (close_index, ranges).

    POSIX rules: a leading `^` negates, a `]` first in the list is literal, `[:class:]`, `[=x=]`
    and `[.x.]` are single items, and a hyphen that is neither first nor last joins the items on
    either side of it into a range. A glob's `!` is read as an ordinary character, so `[!0-9]`
    still holds the range 0-9 and `[!-~]`, which a regex reads as the range ! to ~, is flagged.
    A backslash is an ordinary character inside brackets. Returns (None, []) when no closing
    bracket follows on the line.
    """
    n, j = len(text), i + 1
    if text[j:j + 1] == "^":
        j += 1
    if text[j:j + 1] == "]":
        j += 1
    prev, ranges = None, []
    while j < n:
        c = text[j]
        if c == "]":
            return j, ranges
        if c == "[" and text[j + 1:j + 2] in (":", "=", "."):
            close = text.find(text[j + 1] + "]", j + 2)
            if close == -1:
                return None, []
            # A class cannot be a range endpoint; an equivalence class or collating symbol can.
            prev = None if text[j + 1] == ":" else text[j:close + 2]
            j = close + 2
            continue
        if c == "-" and prev is not None and j + 1 < n and text[j + 1] != "]":
            k = j + 1
            if text[k] == "[" and text[k + 1:k + 2] in ("=", "."):
                close = text.find(text[k + 1] + "]", k + 2)
                if close == -1:
                    return None, []
                end, j = text[k:close + 2], close + 2
            elif text[k] == "[" and text[k + 1:k + 2] == ":":
                prev, j = None, j + 1
                continue
            else:
                end, j = text[k], k + 1
            ranges.append(prev + "-" + end)
            prev = None
            continue
        prev = c
        j += 1
    return None, []


def bracket_ranges(text):
    """Yield (column, expression, ranges) for each bracket expression in text holding a range.

    A closed expression is stepped over whole, so a nested `[` inside it is not reported twice.
    """
    i, n = 0, len(text)
    while i < n:
        if text[i] != "[" or _escaped(text, i):
            i += 1
            continue
        word_end = i + 2 if text.startswith("[[", i) else i + 1
        if (i == 0 or text[i - 1] in TEST_BEFORE) and (word_end == n or text[word_end] in " \t"):
            i = word_end
            continue
        close, ranges = _parse_bracket(text, i)
        if close is None:
            i += 1
            continue
        if ranges:
            yield i, text[i:close + 1], ranges
        i = close + 1


def scan_blocks(name, blocks):
    """Scan one guide's bash blocks. Returns (findings, n_blocks, n_marked)."""
    findings, n_blocks, n_marked = [], 0, 0
    for start, body in blocks:
        n_blocks += 1
        waiting = None  # the line of a marker on a comment line, waiting for the next command
        for cmd in commands(body.split("\n")):
            own, hits = None, []
            for idx, code, comment, data in cmd:
                if not data and MARKER_RE.match(comment):
                    own = start + idx
                # A comment is read too: a commented-out probe is a command a reader uncomments.
                for text in (code, comment):
                    for _col, expr, ranges in bracket_ranges(text):
                        hits.append((start + idx, expr, ranges))
            comment_only = len(cmd) == 1 and not cmd[0][3] and not cmd[0][1].strip() and cmd[0][2]
            if comment_only and own is not None:
                if waiting is not None:
                    findings.append(f"{name}:{waiting}: stale bracket-ranges marker: the line "
                                    f"after it is another marker, not a command")
                waiting = own
                continue
            covered = own if own is not None else waiting
            if covered is None:
                for line, expr, ranges in hits:
                    noun = "range" if len(ranges) == 1 else "ranges"
                    listed = ", ".join(ranges)
                    findings.append(f"{name}:{line}: {expr} holds the {noun} {listed} and no "
                                    f"bracket-ranges marker covers it")
            else:
                n_marked += len(hits)
                if not hits:
                    findings.append(f"{name}:{covered}: stale bracket-ranges marker: the "
                                    f"command it covers holds no bracket range")
            waiting = None
        if waiting is not None:
            findings.append(f"{name}:{waiting}: stale bracket-ranges marker: no command follows "
                            f"it in the block")
    return findings, n_blocks, n_marked


def scan_path(path):
    """Scan one guide file. Raises what blocks_of raises on a file it cannot read."""
    return scan_blocks(path.name, list(blocks_of(path)))


def scan_repo(root):
    """Scan every guide under root. Returns (findings, n_files, n_blocks, n_marked)."""
    paths = sorted(walk_files(root, SKIP_DIRS, suffixes={".md"}))
    findings, n_files, n_blocks, n_marked = [], 0, 0, 0
    for path in paths:
        if path.parent != root or path.name in NOT_A_GUIDE:
            continue
        try:
            found, blocks_here, marked = scan_path(path)
        except Exception as exc:
            findings.append(f"{path.name}: unreadable ({exc})")
            continue
        findings.extend(found)
        n_blocks += blocks_here
        n_marked += marked
        n_files += 1 if blocks_here else 0
    return findings, n_files, n_blocks, n_marked


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        findings, n_files, n_blocks, n_marked = scan_repo(root)
    except Exception as exc:
        print(f"  FAIL  could not walk the repository: {exc}")
        return 1
    if not findings and not n_blocks:
        # A pass over nothing is not a pass.
        findings.append("no bash block was found in any guide, so nothing was checked")
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        print(f"  FAIL  {HINT}")
        return 1
    print(f"  ok    no unmarked bracket range in {n_blocks} bash blocks across {n_files} "
          f"guides ({n_marked} marked allow)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
