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
that skipped it would also skip a regex that happened to start with a quote. A `]` first in the
list, as in `[]-z]` or `[^]-z]`, is a literal and can start a range.

Lines are joined as the shell joins them before any bracket is read. Outside single quotes and
`$'...'`, bash removes a backslash-newline before it reads the text, so `grep -E "[A-\` followed
by a line `Za-z]+"` is the pattern `[A-Za-z]+`, and the gate reads it so, unquoted or in double
quotes. A here-document body is joined the same way: every backslash-newline under a bare
delimiter, which bash removes as it writes the body, and under a quoted one as the shell that
runs the script would join it, quotes and all. A finding names the line of its opening bracket and
the lines it was joined from. A `[` that nothing closes before the end of its command, after
that joining, is itself a finding, because what follows it may hold a range the gate cannot
place, and so is one left open at a line ending in a backslash the shell kept, as single quotes
keep a backslash-newline inside a set. One left open at any other line break of a multi-line
string or here-document is data, such as a JSON or Python list written over several lines: a
bracket expression does not span a real newline in grep, sed, awk or a shell word.

THE FIX is a spelled-out set, which means the same thing in every locale, tool and shell:
`[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]`. `model-servers.md` already
carried `[!0123456789abcdef]` from #350 and #355. A POSIX class in an accept list is sound only
under an explicit `LC_ALL=C` that covers the whole check, since `[[:alnum:]]` accepts non-ASCII
letters under C.utf8. A class in a reject list, such as refusing the locale's control or
whitespace characters, is sound in any locale, because a wider class only refuses more. This gate
does not read POSIX classes or `LC_ALL`: a class needs no marker, and a range under `LC_ALL=C`
still does.

THE MARKER. A range that is not a validator (a search pattern, a label in a format string, a
JSON request body) carries a shell comment

    # bracket-ranges: allow <reason>

in the same shape as `# guard-conventions: allow` and `# unfiltered-ss: allow`, either at the
end of the command, which covers that command, or on a comment line immediately before it,
which covers the next command and nothing further. A command is a single one: `;`, `;;`, `&&`,
`||`, `|`, `|&` and a lone `&` outside quotes end it, so in `a; b  # bracket-ranges: allow x`
the marker covers `b` alone, and a marker on the line above `a; b` covers `a` alone. Backslash
continuations, a quoted string left open across lines and the here-document bodies a command
opened belong to it, so a marker on a here-document's opening line covers that body. The reason
is required. The marker must be a real comment, so the same text inside a quoted string, a
`${...}` expansion or a here-document body does not count. A marker that covers no range is
reported as stale, so one cannot outlive the range it was written for and go on covering
whatever is written there next. A validator never takes the marker: it takes the spelled-out set.

WHAT THIS IS NOT. A shell parser, and not proof that a guard is correct. Known gaps, each
recorded as a case in tools/test_bracket_ranges.py so that closing one is loud:

  - Only bracket expressions are read. `tr -dc 'A-Za-z0-9'` has no brackets and is not flagged.
  - POSIX classes and `\w` are not flagged, although they are locale dependent too.
  - A `[` or `[[` standing as its own word before whitespace is read as the test command.
  - Quotes and `${...}` nesting carry across lines, but `$(...)` nesting is not modelled. A `<<`
    in shell arithmetic is read as a here-document opener; the rest of the block is then data,
    where a range is still reported and a marker no longer counts, which fails closed. An
    operator inside `[[ ]]`, `$(...)` or a `case` pattern's `|` also ends a command here, so a
    marker covers less than it may appear to, which fails closed too.
  - A `[` left open at a line break inside a multi-line string is read as data, so a set that
    glibc's regcomp reads across a quoted newline, `re='^[A-Z` then a line `a-z]+$'` used in
    `[[ =~ ]]`, is not flagged.
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
COMMENT_BEFORE = " \t\n;&|()"
# A `[` or `[[` after one of these and before whitespace is the test command.
TEST_BEFORE = " \t\n;&|(!"
# The operators that end one command of a list or pipeline, longest first. A lone `&` is one
# unless it belongs to a redirection such as `2>&1` or `&>file`.
SEPARATORS = ("&&", "||", ";;", "|&", ";", "|", "&")
# A here-document delimiter: single-quoted, double-quoted, backslash-quoted or bare.
HEREDOC_WORD_RE = re.compile(r"""'([^']*)'|"([^"]*)"|(\\?)([A-Za-z0-9_.+-]+)""")
# The contexts _scan tracks: quotes, and a ${...} expansion outside or inside double quotes.
SQ, DQ, ANSI, BRACE, DQ_BRACE = "'", '"', "$'", "${", '"${'
HINT = ("outside the C locale a bracket range can match non-ASCII letters and digits (GNU grep, "
        "GNU sed and bash [[ =~ ]] were observed doing it under en_US.utf8, and bash case does "
        "it with globasciiranges off), so a validator written with one accepts values it claims "
        "to refuse. Spell the set out, as in "
        "[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. Where the range is "
        "not a validator, put '# bracket-ranges: allow <reason>' at the end of the command or on "
        "a comment line directly above it. See tools/check_bracket_ranges.py.")


def _heredoc_word(line, i):
    """The delimiter of a `<<` or `<<-` at index i: ((word, strip_tabs, quoted), next_index)."""
    j = i + 2
    strip = line[j:j + 1] == "-"
    if strip:
        j += 1
    while j < len(line) and line[j] in " \t":
        j += 1
    m = HEREDOC_WORD_RE.match(line, j)
    if not m:
        return None, j
    single, double, backslash, bare = m.groups()
    word = next(g for g in (single, double, bare) if g is not None)
    return (word, strip, bare is None or backslash == "\\"), m.end()


def _scan(line, stack, last):
    """Read one physical shell line. Returns (code, seps, heredocs, comment, joins).

    `stack` holds the quotes and `${` expansions the lines before left open, innermost last, and
    is updated in place; `last` is the character before this line in the joined command, "" at
    its start. `code` is the line's shell text as a list of characters, less its comment and
    less a backslash that joins the next line to it, which the shell removes outside single
    quotes and `$'...'`. `seps` are the offsets in `code` where the next command of a list or
    pipeline begins, and `heredocs` the ((word, strip, quoted), offset) of each here-document
    the line opens. A comment ends the line, so a backslash inside it joins nothing.
    """
    code, seps, heredocs, i, n = [], [], [], 0, len(line)
    while i < n:
        c, nxt = line[i], line[i + 1:i + 2]
        top = stack[-1] if stack else None
        if top in (SQ, ANSI):
            # A backslash-newline inside either stays in the string; $'...' escapes a quote.
            if top == ANSI and c == "\\" and nxt:
                code.extend(line[i:i + 2])
                i += 2
                continue
            if c == "'":
                stack.pop()
            code.append(c)
            i += 1
            continue
        if c == "\\":
            if not nxt:
                return code, seps, heredocs, "", True
            code.extend(line[i:i + 2])
            i += 2
            continue
        if top is not None:
            # Inside double quotes or ${...}: no comment, operator or here-document starts.
            if c == "$" and nxt == "{":
                stack.append(BRACE if top == BRACE else DQ_BRACE)
                code.extend(c + nxt)
                i += 2
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
                code.extend(c + nxt)
                i += 2
                continue
            elif top == BRACE and c == "'":
                # Within double quotes a single quote inside ${...} is literal; outside, it quotes.
                stack.append(SQ)
            code.append(c)
            i += 1
            continue
        if c == "$" and nxt in ("'", "{"):
            stack.append(c + nxt)
            code.extend(c + nxt)
            i += 2
            continue
        if c in "'\"":
            stack.append(c)
            code.append(c)
            i += 1
            continue
        if c == "#" and (code[-1] if code else last) in COMMENT_BEFORE:
            return code, seps, heredocs, line[i:], False
        if line.startswith("<<<", i):
            code.extend("<<<")
            i += 3
            continue
        if line.startswith("<<", i):
            word, j = _heredoc_word(line, i)
            if word is not None:
                heredocs.append((word, len(code)))
            code.extend(line[i:j])
            i = j
            continue
        op = next((s for s in SEPARATORS if line.startswith(s, i)), None)
        if op == "&" and (code and code[-1] in "<>" or nxt == ">"):
            op = None
        if op is not None:
            code.extend(op)
            i += len(op)
            seps.append(len(code))
            continue
        code.append(c)
        i += 1
    return code, seps, heredocs, "", False


class Segment:
    """One command of a list or pipeline within a logical command.

    `start` is where its text begins in the command's joined text, `bodies` holds each
    here-document it opened as [characters, source lines, quote stack], `comments` the
    (line, text) of each comment annotating it, and `marker` the line of a marker among them.
    """

    def __init__(self, start):
        self.start, self.bodies, self.comments, self.marker = start, [], [], None


class Command:
    """A logical command: its physical lines joined as the shell joins them, in segments.

    `text` holds the joined shell text and `origin` the index of the physical line each
    character came from. A line the shell does not join to the next ends in a newline.
    """

    def __init__(self):
        self.text, self.origin, self.segs = [], [], [Segment(0)]

    def add(self, chars, idx):
        self.text.extend(chars)
        self.origin.extend([idx] * len(chars))

    def seg_at(self, pos):
        """The segment holding position pos of the joined text."""
        return [s for s in self.segs if s.start <= pos][-1]

    def has_code(self, k):
        """Whether segment k holds shell text or a here-document, not only blanks."""
        end = self.segs[k + 1].start if k + 1 < len(self.segs) else len(self.text)
        return bool("".join(self.text[self.segs[k].start:end]).strip() or self.segs[k].bodies)


def commands(lines):
    """Group a block's physical lines into logical commands, joining lines as the shell would.

    A here-document body is data, all of which is read, and belongs to the segment that opened
    it. Its lines are joined as bash joins them when it writes the body (a bare delimiter) or
    as the shell that later runs the script joins them (a quoted one).
    """
    out, cmd, stack, pending, body = [], None, [], [], None
    for idx, line in enumerate(lines):
        if cmd is None:
            cmd = Command()
        if pending:
            (word, strip, quoted), seg = pending[0]
            if (line.lstrip("\t") if strip else line) == word:
                pending.pop(0)
                body = None
                if not pending and not stack:
                    out.append(cmd)
                    cmd = None
                continue
            if body is None:
                body = [[], [], []]
                seg.bodies.append(body)
            if quoted:
                joins = _scan(line, body[2], "")[4]
            else:
                joins = (len(line) - len(line.rstrip("\\"))) % 2 == 1
            text = line[:-1] if joins else line + "\n"
            body[0].extend(text)
            body[1].extend([idx] * len(text))
            continue
        code, seps, opened, comment, joins = _scan(line, stack, cmd.text[-1] if cmd.text else "")
        base = len(cmd.text)
        cmd.add(code, idx)
        cmd.segs.extend(Segment(base + off) for off in seps)
        pending.extend((word, cmd.seg_at(base + off)) for word, off in opened)
        if comment:
            # A comment annotates the last command with text before it, not an empty one after
            # a trailing `;`.
            coded = [k for k in range(len(cmd.segs)) if cmd.has_code(k)]
            seg = cmd.segs[coded[-1]] if coded else cmd.segs[-1]
            seg.comments.append((idx, comment))
            if MARKER_RE.match(comment):
                seg.marker = idx
        if joins:
            continue
        cmd.add("\n", idx)
        if not pending and not stack:
            out.append(cmd)
            cmd = None
    if cmd is not None and cmd.text:
        out.append(cmd)
    return out


def _escaped(text, i):
    k = i
    while k > 0 and text[k - 1] == "\\":
        k -= 1
    return (i - k) % 2 == 1


def _line_end(text, i):
    end = text.find("\n", i)
    return len(text) if end == -1 else end


def _parse_list(text, j, prev):
    """Read a bracket list from text[j], with `prev` the item already read or None.

    Returns (close_index, ranges), or (None, ranges) when a newline or the end of the text
    comes first.
    """
    n, ranges = _line_end(text, j), []
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
    brackets. Returns (None, ranges) when nothing closes the expression before a newline or the
    end of the text.
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


def _open_at_end(text, i):
    """Whether a `[` at i left open reaches the end of its command: the end of the text, or a
    line that ends in a backslash the shell kept, as single quotes keep one. A `[` left open at
    any other newline of a multi-line string or here-document is data, such as a JSON or Python
    list written over several lines: a bracket expression does not span a real newline in grep,
    sed, awk or a shell word."""
    end = _line_end(text, i)
    return end >= len(text) - 1 or _escaped(text, end)


def bracket_ranges(text):
    """Yield (column, close, expression, ranges) for each bracket expression in text holding a
    range, and for each one left open at the end of its command, whose `close` is None.

    A closed expression is stepped over whole, so a nested `[` inside it is not reported twice.
    """
    i, n = 0, len(text)
    while i < n:
        if text[i] != "[" or _escaped(text, i):
            i += 1
            continue
        word_end = i + 2 if text.startswith("[[", i) else i + 1
        if (i == 0 or text[i - 1] in TEST_BEFORE) and (word_end == n or text[word_end] in " \t\n"):
            i = word_end
            continue
        close, ranges = _parse_bracket(text, i)
        if close is None:
            if _open_at_end(text, i):
                yield i, None, text[i:_line_end(text, i)].rstrip(), ranges
            i += 1
            continue
        if ranges:
            yield i, close, text[i:close + 1], ranges
        i = close + 1


def _hits(text, origin, start):
    """Yield (column, line, description) for each range and each open bracket in joined text."""
    for col, close, expr, ranges in bracket_ranges(text):
        line = start + origin[col]
        if close is None:
            yield col, line, (f"{expr[:60]} opens a bracket expression that nothing closes "
                              f"before the end of its command, so a range in it cannot be "
                              f"ruled out,")
            continue
        noun = "range" if len(ranges) == 1 else "ranges"
        listed = ", ".join(ranges)
        joined = ""
        if origin[close] != origin[col]:
            joined = f" (joined from lines {line}-{start + origin[close]})"
        yield col, line, f"{expr} holds the {noun} {listed}{joined}"


def scan_blocks(name, blocks):
    """Scan one guide's bash blocks. Returns (findings, n_blocks, n_marked)."""
    findings, n_blocks, n_marked = [], 0, 0
    for start, body in blocks:
        n_blocks += 1
        waiting = None  # the line of a marker on a comment line, waiting for the next command
        for cmd in commands(body.split("\n")):
            hits = [[] for _ in cmd.segs]
            for col, line, what in _hits("".join(cmd.text), cmd.origin, start):
                # A range belongs to the command its opening bracket is in.
                hits[cmd.segs.index(cmd.seg_at(col))].append((line, what))
            for k, seg in enumerate(cmd.segs):
                for chars, origin, _stack in seg.bodies:
                    hits[k].extend(h[1:] for h in _hits("".join(chars), origin, start))
                # A comment is read too: a commented-out probe is a command a reader uncomments.
                for idx, comment in seg.comments:
                    hits[k].extend(h[1:] for h in _hits(comment, [idx] * len(comment), start))
            coded = [k for k in range(len(cmd.segs)) if cmd.has_code(k)]
            markers = [seg.marker for seg in cmd.segs if seg.marker is not None]
            if not coded and markers:
                if waiting is not None:
                    findings.append(f"{name}:{waiting}: stale bracket-ranges marker: the line "
                                    f"after it is another marker, not a command")
                waiting = start + markers[0]
                continue
            first = coded[0] if coded else 0
            for k, seg in enumerate(cmd.segs):
                if seg.marker is not None:
                    covered = start + seg.marker
                else:
                    covered = waiting if k == first else None
                if covered is None:
                    findings.extend(f"{name}:{line}: {what} and no bracket-ranges marker "
                                    f"covers it" for line, what in hits[k])
                else:
                    n_marked += len(hits[k])
                    if not hits[k]:
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
