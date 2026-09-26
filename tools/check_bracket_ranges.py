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
`check_shell_blocks.blocks_of`) is read on its own. Nothing is joined: not a backslash
continuation, not a quoted string left open, not a here-document body. Two earlier versions of
this gate modelled that joining as bash does, and adversarial review found a new way around the
model each time; this version deliberately refuses to model it and fails closed instead.

On each physical line, two things are findings:

  - A bracket expression holding a range (`X-Y`, hyphen neither first nor last). POSIX rules
    apply within the line: a leading `^` negates, a `]` first in the list is a literal and can
    start a range (`[]-z]`, `[^]-z]`), `[:class:]`, `[=x=]` and `[.x.]` are single items, and a
    glob's `!` is an ordinary character, so `[!0-9]` still holds 0-9 and a `]` right after `[!`
    is a literal whenever a later `]` on the line closes the expression. A `[]` or `[^]` that
    no later `]` on the line closes is the empty pair of a JSON, jq or JMESPath expression,
    which no tool reads as a bracket expression. A backslash does not hide a bracket: the shell
    removes an unquoted `\` before the tool sees `[`, so `grep -E \[0-9] f` holds a live range,
    and a quoted `\[` is flagged too rather than guessed about.
  - A `[` that nothing on its own physical line closes. A set split across lines by any means, a
    backslash continuation, a quoted newline (`re='^[A-Z` then a line `a-z]+$'`, which glibc's
    regcomp reads across the newline), or a multi-line data list, lands here by construction,
    without the gate having to know which of those it was.

Shell text, comments and here-document bodies are all read the same way: a regex stored in a
variable, a `case` alternative on its own line, a script written to a file through a
here-document and a commented-out probe are validators too. The gate does not ask which tool
reads the pattern. A JSON array holding a hyphenated string, `["app-data"]`, reads as a range as
well and takes a marker; a rule that skipped it would also skip a regex that happened to start
with a quote.

THE FIX is a spelled-out set, which means the same thing in every locale, tool and shell:
`[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]`. `model-servers.md` already
carried `[!0123456789abcdef]` from #350 and #355. A POSIX class in an accept list is sound only
under an explicit `LC_ALL=C` that covers the whole check, since `[[:alnum:]]` accepts non-ASCII
letters under C.utf8. A class in a reject list, such as refusing the locale's control or
whitespace characters, is sound in any locale, because a wider class only refuses more. This gate
does not read POSIX classes or `LC_ALL`: a class needs no marker, and a range under `LC_ALL=C`
still does.

THE MARKER. A range that is not a validator (a search pattern, a label in a format string, a
JSON request body) carries a trailing shell comment on the same physical line

    ... the code with the range ...  # bracket-ranges: allow <reason>

and the waiver covers that one physical line and nothing else. There is no preceding-line form:
what a marker covers is exactly what a reviewer sees beside it. A validator never takes the
marker: it takes the spelled-out set. The marker counts only when all of these hold, and one
that fails is itself a finding ("waiver refused"), never silently ignored:

  - Its `#` is unambiguously a comment: at the start of the line, or at the start of a word,
    outside any quote, expansion, command substitution or backtick as a fresh scan of that one
    line reads them, and not on a line of a here-document body, where a `#` is data. When the
    scan cannot decide, it is not a comment.
  - Every line before it in the block was plainly resolved: none left a quote, an expansion, a
    substitution or a backtick open at its end, none ended with a backslash right after `$`,
    `<` or `>` (which splits a token across the break and can change what the next line means),
    and none opened a here-document whose delimiter the gate could not read. After any of
    those, the gate cannot trust its own reading of a later `#`, so no later marker in the
    block counts.
  - The reason is present and holds no `[`, so a reason cannot smuggle in the very text being
    waived, and cannot satisfy the staleness rule by quoting a range.
  - The code before the `#` holds no unquoted `;`, `;;`, `&&`, `||`, `|`, `|&` or `&` (a `&`
    belonging to a redirection such as `2>&1` or `&>f` excepted): a waived line is one command,
    so the marker cannot silently cover a second one sharing the line.

A marker that is valid but covers no finding on its own line is reported as stale, so one cannot
outlive the range it was written for.

WHAT THIS IS NOT. A shell parser, and not proof that a guard is correct. The model is
deliberately conservative: everything in the first list below is over-flagging that fails
closed, listed honestly; what the gate still does not see at all is in the second. Each is a
recorded case in tools/test_bracket_ranges.py so that a change is loud.

  Over-flagged, by design (restructure the line, or waive it where a waiver is legal):
  - A multi-line data list, a JSON array or Python list whose `[` closes on a later line, is an
    unclosed-bracket finding on the line of the `[`. Data written over several lines inside a
    here-document cannot be waived at all, since a marker in a body is data; keep such a list
    on one line where a waiver can sit, or use a bracket-free shape (a Python tuple, a split
    string).
  - A quoted literal `\[a-z\]`, an array subscript `a[i-1]` in an expansion or in arithmetic,
    and a slice `[1:-1]` are flagged: the gate does not know a backslash is quoted or a context
    is arithmetic, and guessing was what the joined-line model got wrong.
  - A here-document body can never carry a valid waiver, and a body under a delimiter the gate
    cannot read refuses every later waiver in the block. The bodies are still scanned.
  - After a line that ends inside an open quote or expansion, or ends with a backslash right
    after `$`, `<` or `>`, no later waiver in the block counts, even a legitimate one.
  - A waiver on a line holding a `;`, `&&`, `|` or another separator is refused even when the
    separator joins two commands that are both fine.
  - A `<<` in a bare arithmetic command, `(( x = 1 << 2 ))`, is read as a here-document opener,
    so the rest of the block becomes a body where no waiver counts; `$((1 << 2))` inside a
    substitution is read correctly. The lines are still scanned.
  - A bare-delimiter here-document is held open across a body line ending in a backslash, as
    bash joins those before matching the terminator, so the gate never leaves a body earlier
    than bash does; it may leave later, which only refuses more waivers.

  Still not seen at all:
  - Ranges with no brackets: `tr -dc 'A-Za-z0-9'`.
  - POSIX classes and `\w`, although they are locale dependent too.
  - A `[` or `[[` standing as its own word before whitespace is read as the test command.
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
# A marker attempt: anything that looks like the marker, valid or not, is never quietly ignored.
MARKERISH_RE = re.compile(r"#[ \t]*bracket-ranges:")
# The comment must open with the marker and give a reason, as the sibling gates' waivers must.
MARKER_RE = re.compile(r"#[ \t]*bracket-ranges:[ \t]*allow[ \t]+\S")
# A `#` begins a comment at the start of a word, which these characters end.
COMMENT_BEFORE = " \t;&|()"
# A `[` or `[[` after one of these and before whitespace is the test command.
TEST_BEFORE = " \t;&|(!"
# The operators that end one command of a list or pipeline, longest first. A lone `&` is one
# unless it belongs to a redirection such as `2>&1` or `&>file`.
SEPARATORS = ("&&", "||", ";;", "|&", ";", "|", "&")
# A here-document delimiter: single-quoted, double-quoted, backslash-quoted or bare.
HEREDOC_WORD_RE = re.compile(r"""'([^']*)'|"([^"]*)"|(\\?)([A-Za-z0-9_.+-]+)""")
# The contexts _lex tracks: quotes, expansions and substitutions. A `#` inside any of them is
# not a comment, and a line ending inside one refuses every later waiver in its block.
SQ, DQ, ANSI, BRACE, DQ_BRACE, CMDSUB, PAREN, BT = "'", '"', "$'", "${", '"${', "$(", "(", "`"
# A backslash at the end of a line right after one of these splits a token across the break,
# which can change what the next line means.
GLUE_BEFORE = "$<>"
HINT = ("outside the C locale a bracket range can match non-ASCII letters and digits (GNU grep, "
        "GNU sed and bash [[ =~ ]] were observed doing it under en_US.utf8, and bash case does "
        "it with globasciiranges off), so a validator written with one accepts values it claims "
        "to refuse. Spell the set out, as in "
        "[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. Where the range is "
        "not a validator, put '# bracket-ranges: allow <reason>' at the end of that same "
        "physical line; the waiver covers that line alone. See tools/check_bracket_ranges.py.")


def _heredoc_word(line, i):
    """The delimiter of a `<<` or `<<-` at index i: ((word_or_None, strip_tabs, quoted), next)."""
    j = i + 2
    strip = line[j:j + 1] == "-"
    if strip:
        j += 1
    while j < len(line) and line[j] in " \t":
        j += 1
    m = HEREDOC_WORD_RE.match(line, j)
    if not m:
        # A delimiter the gate cannot read: where the body ends is unknowable.
        return (None, strip, False), j
    single, double, backslash, bare = m.groups()
    word = next(g for g in (single, double, bare) if g is not None)
    return (word, strip, bare is None or backslash == "\\"), m.end()


class Line:
    """What one fresh scan of one physical line establishes.

    `comment` is the index of the first `#` that starts a comment, or None; `sep` whether the
    code before any comment holds a command separator; `heredocs` the (word, strip, quoted) of
    each here-document the line opens, word None when unreadable; `dirty` a reason the line's
    end cannot be trusted as a boundary, or None.
    """

    __slots__ = ("comment", "sep", "heredocs", "dirty")

    def __init__(self):
        self.comment, self.sep, self.heredocs, self.dirty = None, False, [], None


def _lex(line):
    """Scan one physical line from a clean start. Returns a Line.

    This is the only lexing the gate does, and it never crosses a line break: its answers are
    trusted only while every prior line of the block resolved plainly, which scan_blocks
    enforces by refusing every waiver after one that did not.
    """
    info, stack, i, n = Line(), [], 0, len(line)
    while i < n:
        c, nxt = line[i], line[i + 1:i + 2]
        top = stack[-1] if stack else None
        if top in (SQ, ANSI):
            if top == ANSI and c == "\\" and nxt:
                i += 2
                continue
            if c == "'":
                stack.pop()
            i += 1
            continue
        if top == BT:
            if c == "\\" and nxt:
                i += 2
                continue
            if c == "`":
                stack.pop()
            i += 1
            continue
        if c == "\\":
            if not nxt:
                if i and line[i - 1] in GLUE_BEFORE:
                    info.dirty = (f"ends with a backslash right after '{line[i - 1]}', "
                                  f"splitting a token across the break")
                return info
            i += 2
            continue
        if top in (DQ, BRACE, DQ_BRACE):
            if c == "$" and nxt == "{":
                stack.append(BRACE if top == BRACE else DQ_BRACE)
                i += 2
                continue
            if c == "$" and nxt == "(":
                stack.append(CMDSUB)
                i += 2
                continue
            if c == "`":
                stack.append(BT)
                i += 1
                continue
            if top == DQ:
                if c == '"':
                    stack.pop()
            elif c == "}":
                stack.pop()
            elif c == '"':
                stack.append(DQ)
            elif top == BRACE and c == "$" and nxt == "'":
                stack.append(ANSI)
                i += 2
                continue
            elif top == BRACE and c == "'":
                # Within double quotes a single quote inside an expansion is literal; outside,
                # it quotes.
                stack.append(SQ)
            i += 1
            continue
        # From here the top is None (plain code), CMDSUB or PAREN, which read alike except that
        # a `)` closes the latter two and a comment or here-document starts only at the top.
        if c == "$" and nxt in ("'", "{", "("):
            stack.append(c + nxt)
            i += 2
            continue
        if c in "'\"`":
            stack.append(BT if c == "`" else c)
            i += 1
            continue
        if top in (CMDSUB, PAREN):
            if c == "(":
                stack.append(PAREN)
                i += 1
                continue
            if c == ")":
                stack.pop()
                i += 1
                continue
            op = next((s for s in SEPARATORS if line.startswith(s, i)), None)
            if op is not None:
                if not (op == "&" and (i and line[i - 1] in "<>" or nxt == ">")):
                    info.sep = True
                i += len(op)
                continue
            i += 1
            continue
        if c == "#" and (i == 0 or line[i - 1] in COMMENT_BEFORE):
            info.comment = i
            return info
        if line.startswith("<<<", i):
            i += 3
            continue
        if line.startswith("<<", i):
            word, j = _heredoc_word(line, i)
            info.heredocs.append(word)
            i = j
            continue
        op = next((s for s in SEPARATORS if line.startswith(s, i)), None)
        if op is not None:
            if not (op == "&" and (i and line[i - 1] in "<>" or nxt == ">")):
                info.sep = True
            i += len(op)
            continue
        i += 1
    if stack:
        info.dirty = f"ends inside an open {stack[0]}"
    return info


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
            close = text.find(text[j + 1] + "]", j + 2, n)
            if close == -1:
                return None, ranges
            # A class cannot be a range endpoint; an equivalence class or collating symbol can.
            prev = None if text[j + 1] == ":" else text[j:close + 2]
            j = close + 2
            continue
        if c == "-" and prev is not None and j + 1 < n and text[j + 1] != "]":
            k = j + 1
            if text[k] == "[" and text[k + 1:k + 2] in ("=", "."):
                close = text.find(text[k + 1] + "]", k + 2, n)
                if close == -1:
                    return None, ranges
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
    return None, ranges


def _parse_bracket(text, i):
    """Parse the bracket expression opening at text[i]. Returns (close_index, ranges).

    POSIX rules: a leading `^` negates, a `]` first in the list is a literal and may start a
    range, `[:class:]`, `[=x=]` and `[.x.]` are single items, and a hyphen that is neither first
    nor last joins the items on either side of it into a range. A glob's `!` is read as an
    ordinary character, so `[!0-9]` still holds the range 0-9 and `[!-~]`, which a regex reads
    as the range ! to ~, is flagged; a `]` right after `[!` is read as a glob reads it, a
    literal, whenever a later `]` on the line closes the expression. A `[]` or `[^]` that no
    later `]` on the line closes is the empty pair of a JSON, jq or JMESPath expression, which
    no tool reads as a bracket expression. A backslash is an ordinary character inside
    brackets. Returns (None, ranges) when nothing closes the expression on this line.
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


def bracket_hits(text):
    """Yield one description per bracket expression in one line's text holding a range, and per
    `[` left open at the end of the line. A closed expression is stepped over whole, so a nested
    `[` inside it is not reported twice. A backslash before a `[` does not hide it: unquoted,
    the shell removes it and the tool sees a live bracket."""
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
        if close is None:
            yield (f"{text[i:i + 60].rstrip()} opens a bracket expression that nothing closes "
                   f"on its physical line, so a range in it cannot be ruled out,")
            i += 1
            continue
        if ranges:
            noun = "range" if len(ranges) == 1 else "ranges"
            yield f"{text[i:close + 1]} holds the {noun} {', '.join(ranges)}"
        i = close + 1


def scan_blocks(name, blocks):
    """Scan one guide's bash blocks, one physical line at a time.

    Returns (findings, n_blocks, n_marked). `pending` queues the here-documents whose bodies
    the lines ahead are; `tainted` carries the reason no later waiver in the block counts, once
    one exists; `glued` tracks a bare-delimiter body line bash would join onward, so the gate
    never leaves a body earlier than bash does.
    """
    findings, n_blocks, n_marked = [], 0, 0
    for start, body in blocks:
        n_blocks += 1
        tainted, pending, glued = None, [], False
        for idx, raw in enumerate(body.split("\n")):
            lineno = start + idx
            in_body, info = False, None
            if pending:
                word, strip, quoted = pending[0]
                if word is not None and not (not quoted and glued) \
                        and (raw.lstrip("\t") if strip else raw) == word:
                    pending.pop(0)
                    glued = False
                    # The terminator line itself is still scanned below, like every line.
                else:
                    if word is not None and not quoted:
                        glued = (len(raw) - len(raw.rstrip("\\"))) % 2 == 1
                    in_body = True
            if not in_body:
                info = _lex(raw)
                pending.extend(info.heredocs)
            # The waiver: a marker attempt is validated or refused, never quietly ignored.
            marker = None
            for m in MARKERISH_RE.finditer(raw):
                marker = m
            valid = False
            if marker is not None:
                p = marker.start()
                if in_body:
                    why = "it sits in a here-document body, where a # is data, not a comment"
                elif tainted:
                    why = tainted
                elif info.comment is None or p < info.comment \
                        or (p > info.comment and raw[p - 1] not in " \t"):
                    why = ("its # is not clearly a comment (it sits inside a quote, an "
                           "expansion, a substitution or a backtick, or not at the start "
                           "of a word)")
                elif not MARKER_RE.match(raw, p):
                    why = "no reason follows 'allow'"
                elif "[" in raw[p:]:
                    why = "its reason holds a '[', which a reason must not"
                elif info.sep:
                    why = ("the code beside it holds a command separator, so the waiver would "
                           "cover more than one command")
                else:
                    valid = True
                if not valid:
                    findings.append(f"{name}:{lineno}: waiver refused: {why}")
            hits = list(bracket_hits(raw[:marker.start()] if valid else raw))
            if valid:
                if hits:
                    n_marked += len(hits)
                else:
                    findings.append(f"{name}:{lineno}: stale bracket-ranges marker: no bracket "
                                    f"range on its line")
            else:
                findings.extend(f"{name}:{lineno}: {what} and no bracket-ranges marker covers "
                                f"it" for what in hits)
            if not in_body and tainted is None and info.dirty is not None:
                tainted = (f"line {lineno} {info.dirty}, so no later # in this block is "
                           f"clearly a comment")
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
