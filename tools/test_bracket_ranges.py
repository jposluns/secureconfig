#!/usr/bin/env python3
r"""Cases for check_bracket_ranges.py, including what it deliberately over-flags.

Most cases hand one guide to the gate's own scan_path, with or without a throwaway allowlist,
and assert the exact number of findings and a substring of one, so a stale allowlist entry, an
in-guide marker and an unmarked range are counted apart rather than merged into "it failed". The
ENTRY POINT group builds throwaway repositories and runs the shipped file, for what only the
entry point does: choosing which files to read, loading tools/bracket_ranges_allow.txt, the pass
line, the exit status, and failing closed on an unreadable guide, an unlistable directory, an
unreadable allowlist, or a corpus with no bash block in it.

Four direct quote-removal checks and seventeen joining checks pin the context-free transformations.

The REGRESSIONS groups preserve the reported bypasses and nearby variants, with their original
in-block waiver attempts where present. Rounds 1 and 2 beat the joined-line lexing; round 3 beat the
residual one-line lexing that decided whether a waiver comment was real (an escaped space before
a data `#`, a trailing backslash dropping an open quote, a partly recognized here-document
delimiter, a fake POSIX atom swallowing a validator, quoting inside a parameter-removal pattern,
and only the last marker attempt on a line being validated). Not every variant was fail-open:
the round-2 trailing-marker `codex r2-1` case already produced two findings in round 2, while its
preceding-marker counterpart produced zero. Round 4 found escaped and quoted closing brackets
hiding a live range. Round 5 found buried quoted closes and quote removal shifting a leading
negation; the development fuzzer then found six unset-variable shifts of a literal close.
Round 6 found continuations and quoted newlines; the widened fuzzer supplied 1143 more fixtures.
Round 8 covers even quote counts and leading literal closes across heredoc newlines.
Except for the disclosed NOT SEEN cases, each reported bypass is a finding. Ranges and unclosed
`[` are findings on their own physical line whatever surrounds them. Waivers live only in
tools/bracket_ranges_allow.txt, bound to the complete physical span; the old in-block marker is
itself a finding wherever it sits in a guide.

The OVER-FLAGGED group asserts the cost of failing closed on inputs a shell parser would accept,
so the docstring's list stays honest, and the NOT SEEN group asserts what the gate still does
not read at all, so closing one of those is loud too.
"""
import hashlib
import itertools
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import check_bracket_ranges as gate  # noqa: E402

MARK = "# bracket-ranges: allow "
GREP = "grep -E '^[a-z]+$' f"
Q = chr(34)
BS = chr(92)
JSON_ARRAY = "[" + Q + "app-data" + Q + "]"
UNCLOSED = "opens a bracket expression that nothing closes"
MARKER = "in-guide bracket-ranges marker"
STALE = "stale allowlist entry"
ALLOW = "tools/bracket_ranges_allow.txt"


def doc(block, fence="```bash"):
    """A guide whose one block starts on line 6, which the line numbers below assume."""
    close = re.match(r"[`~]+", fence).group(0)
    return "# T\n\n## Verify\n\n" + fence + "\n" + block + "\n" + close + "\n"


def entry(text, guide="guide.md", reason="not a validator"):
    """One allowlist entry binding the complete physical source `text` in `guide`."""
    return guide + "\tsha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest() + "\t" + reason


def findings(text, allow=None):
    """Run the gate's scanner over one guide held in a throwaway file, with `allow` the content
    of a throwaway allowlist or None for an empty one, in scan_repo's finding order: what
    loading the allowlist flagged, then the guide's findings, then the stale entries."""
    d = Path(tempfile.mkdtemp())
    try:
        p = d / "guide.md"
        p.write_text(text, encoding="utf-8")
        if allow is None:
            allowlist = gate.Allowlist()
        else:
            a = d / "allow.txt"
            a.write_text(allow, encoding="utf-8")
            allowlist = gate.Allowlist.load(a)
        found = gate.scan_path(p, allowlist)[0]
        return list(allowlist.findings) + found + allowlist.stale()
    finally:
        shutil.rmtree(d, ignore_errors=True)


# (description, guide text, exact findings or None for at least one, required substring or None)
CASES = (
    # CAUGHT. Validators in the shapes this corpus uses, and the places a range hides.
    ("a case accept list for a host name",
     doc('case "$1" in *[!A-Za-z0-9.-]*) exit 2 ;; esac'), 1,
     "guide.md:6: [!A-Za-z0-9.-] holds the ranges A-Z, a-z, 0-9"),
    ("a secret checked with [[ =~ ]], reported as the bracket and not the test word",
     doc('[[ "$t" =~ ^[A-Za-z0-9_.-]+$ ]] || exit 2'), 1, "guide.md:6: [A-Za-z0-9_.-] holds"),
    ("a regex stored in a variable, with no tool on the line",
     doc("ipv4='^[0-9]{1,3}$'"), 1, "[0-9] holds the range 0-9 "),
    ("a case alternative on a line of its own",
     doc("case \"$2\" in\n  ''|*[!0-9]*) exit 2 ;;\nesac"), 1, "guide.md:7:"),
    ("a generated hex value checked with grep -E",
     doc("grep -qE '^[0-9a-f]{32}$' marker.txt"), 1, "0-9, a-f"),
    ("a negated range in sed", doc("sed -E 's/[^a-z]//g' names.txt"), 1, "[^a-z]"),
    ("a range whose ends are not letters or digits", doc("grep -E '[ -~]' notes.txt"), 1, "[ -~]"),
    ("a glob's ! read as a range endpoint, which a regex makes it",
     doc("grep -E '[!-~]' notes.txt"), 1, "!-~"),
    ("a literal ] first in the list, then a range", doc("grep -E '[]a-z]' f"), 1, "a-z"),
    ("a class beside a range", doc("grep -E '[[:digit:]a-f]' f"), 1, "a-f"),
    ("a range in a here-document body",
     doc("cat > check.sh <<'EOF'\ngrep -qE '^[a-z]+$' name.txt\nEOF"), 1, "guide.md:7:"),
    ("a range on a continuation line is found on its own line",
     doc("grep -E \\\n  '^[a-z]+$' names.txt"), 1, "guide.md:7:"),
    ("the # in a length expansion starts no comment and hides nothing",
     doc('[ "${#1}" -eq 32 ] && case "$1" in *[!0-9a-f]*) exit 2 ;; esac'), 1, "[!0-9a-f]"),
    ("two ranges on one line are two findings",
     doc('case "$1" in *[!a-z]*|*[!0-9]*) exit 2 ;; esac'), 2, None),
    ("a JSON array holding a hyphenated string takes an allowlist entry, by design",
     doc("printf '%s' '" + JSON_ARRAY + "'"), 1, "p-d"),
    ("a range under LC_ALL=C still takes an allowlist entry", doc("LC_ALL=C " + GREP), 1, None),
    ("a range in a comment, which a reader may uncomment",
     doc("# accepts only [A-Za-z]\necho ok"), 1, "guide.md:6:"),
    ("a commented-out probe with a validator",
     doc('#   [[ "$1" =~ ^[0-9]+$ ]] || exit 2'), 1, "[0-9]"),
    ("two here-documents on one line, both bodies read",
     doc("cat /dev/fd/3 /dev/fd/4 3<<'A' 4<<'B'\n[a-z]\nA\n[0-9]\nB"), 2, "guide.md:9:"),
    ("a literal ] first in the list starts a range", doc("grep -E '[]-z]' f"), 1, "]-z"),
    ("a literal ] first in a negated list starts a range", doc("grep -E '[^]-z]' f"), 1, "]-z"),
    ("a literal ] first in a glob's negated list starts a range",
     doc('case "$1" in *[!]-z]*) exit 2 ;; esac'), 1, "[!]-z] holds the range ]-z"),

    # REGRESSIONS, ROUND 4. Local close ambiguity, without quote or escape lexing.
    ('round 4: escaped close hides a live range',
     doc('case "$1" in *[!\\]a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: single-quoted close hides a live range',
     doc('case "$1" in *[!\']\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: double-quoted close hides a live range',
     doc('case "$1" in *[!"]"a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: escaped close starts a range',
     doc('case "$1" in *[!\\]-z]*) exit 2 ;; esac'), 1, ']-z'),
    ('round 4: a quote after the close can end a longer single-quoted member',
     doc('case "$1" in *[!\'x]\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: a quote after the close can end a longer double-quoted member',
     doc('case "$1" in *[!"x]"a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: successive ambiguous closes are each followed',
     doc('case "$1" in *[!\\]\\]a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 4: a range in the ordinary reading is still a finding',
     doc('case "$1" in *[!a-z\\]abc]*) exit 2 ;; esac'), 1, 'a-z'),
    ('over-flagged: escaped close with a closed range-free alternative',
     doc('case "$1" in *[!\\]abc]*) exit 2 ;; esac'), 1, None),
    ('over-flagged: single-quoted close with a closed range-free alternative',
     doc('case "$1" in *[!\']\'abc]*) exit 2 ;; esac'), 1, None),
    ('over-flagged: double-quoted close with a closed range-free alternative',
     doc('case "$1" in *[!"]"abc]*) exit 2 ;; esac'), 1, None),
    ('escaped close with an unclosed alternative',
     doc('pattern=[!\\]'), 1, UNCLOSED),
    ('single-quoted close with an unclosed alternative',
     doc("pattern=[!']'"), 1, UNCLOSED),
    ('double-quoted close with an unclosed alternative',
     doc('pattern=[!"]"'), 1, UNCLOSED),
    ('a possible continuation does not swallow the next expression',
     doc('case "$1" in *[!\\]abc]*|*[!0-9]*) exit 2 ;; esac'), 2, '0-9'),
    ("an alternative spanning a separate expression preserves both openers",
     doc("printf '%s\\n' '[\"key\"]' '[a-z]'"), 2, "a-z"),
    ('a single-quoted spelled set needs no alternative',
     doc("grep -E '[0123456789]' f"), 0, None),
    ('a double-quoted POSIX class needs no alternative',
     doc('grep -E "[[:digit:]]" f'), 0, None),
    ('over-flagged: a quoted dictionary key has an unclosed alternative',
     doc('python3 -c \'print(d["key"])\''), 1, UNCLOSED),
    ('over-flagged: a literal quote in a regex has an unclosed alternative',
     doc('grep -o \'[^"]\' f'), 1, UNCLOSED),

    # A SET SPLIT ACROSS LINES IS AN UNCLOSED BRACKET ON ITS OWN LINE, HOWEVER IT WAS SPLIT.
    ("a set split by a backslash-newline inside double quotes, in grep",
     doc('grep -E "^[A-\\\nZa-z]+$" names.txt'), 1, "guide.md:6:"),
    ("a set split by a backslash-newline in an unquoted word",
     doc("grep -E ^[A-\\\nZa-z]+$ names.txt"), 1, UNCLOSED),
    ("a set split by a backslash-newline in sed",
     doc('sed -E "s/[^a-\\\nz]//g" names.txt'), 1, "guide.md:6:"),
    ("a set split by a backslash-newline in awk", doc('awk "/^[0-\\\n9]+$/" ports.txt'), 1,
     UNCLOSED),
    ("a set split by a backslash-newline in a case pattern",
     doc('case "$1" in *[!A-Za-\\\nz0-9.-]*) exit 2 ;; esac'), 1, UNCLOSED),
    ("a set split by a backslash-newline in [[ =~ ]]",
     doc('[[ "$t" =~ ^[0-9a-\\\nf]+$ ]] || exit 2'), 3, UNCLOSED),
    ("the surrealdb JWT check split after A-Za-, the round-1 reproduction",
     doc('  [[ "$probe_jwt" =~ ^[A-Za-\\\nz0-9_.-]+$ ]] || { echo ' + "'missing or malformed "
         "JWT; not probing'; exit 2; }"), 3, "guide.md:6:"),
    ("a set split across three lines", doc('grep -E "[A-\\\nZa-\\\nz]" f'), 1, "guide.md:6:"),
    ("a set split by a backslash-newline in a script written through a quoted here-document",
     doc("cat > check.sh <<'EOF'\ngrep -qE \"^[a-\\\nz]+$\" name.txt\nEOF"), 1, "guide.md:7:"),
    ("a set split by a backslash-newline in a bare here-document",
     doc("cat > f <<EOF\n^[0-\\\n9]+$\nEOF"), 1, "guide.md:7:"),
    ("a backslash-newline in single quotes stays, and the open set is found",
     doc("grep -E '^[A-\\\nZa-z]+$' names.txt"), 1, "guide.md:6:"),
    ("a backslash-newline in ANSI-C quotes stays, and the open set is found",
     doc("grep -E $'^[A-\\\nZa-z]+$' names.txt"), 1, UNCLOSED),
    ("a backslash-newline in single quotes in a here-document script",
     doc("cat > check.sh <<'EOF'\ngrep -qE '^[a-\\\nz]+$' name.txt\nEOF"), 1, "guide.md:7:"),
    ("a set nothing closes on its line", doc("grep -E '^[a-z' f"), 1, UNCLOSED),
    ("a set spanning a real newline inside quotes, once a disclosed miss, is caught",
     doc("re='^[A-Z\na-z]+$'\n[[ é =~ $re ]]"), 1, "guide.md:6:"),
    ("a case pattern spanning a real newline is caught",
     doc('case "$1" in *[!A-Z\na-z0-9]*) exit 2 ;; esac'), 1, "guide.md:6:"),
    ("a range in a multi-line awk program string is found on its own line",
     doc("awk '\n/^[a-z]/ { print }\n' f"), 1, "guide.md:7:"),
)
CASES += (
    # THE RETIRED IN-BLOCK MARKER. Any guide line holding it is a finding, wherever it sits:
    # in code, in a comment, in prose, in a quote or in a here-document body. The gate does not
    # decide whether it is a real comment; that decision was the round-3 attack surface.
    ("a marker at the end of a range's line waives nothing and is itself a finding",
     doc(GREP + "  " + MARK + "a search pattern"), 2, MARKER),
    ("a marker on the line above a range",
     doc(MARK + "a search pattern\n" + GREP), 2, "guide.md:6: " + MARKER),
    ("a marker on a clean line", doc("echo ok  " + MARK + "x"), 1, MARKER),
    ("a marker in prose outside any block",
     "# T\n\nSay " + MARK + "here.\n\n```bash\necho ok\n```\n", 1, "guide.md:3: " + MARKER),
    ("a marker in a here-document body",
     doc("cat > f <<'EOF'\n^[a-z]+$  " + MARK + "fake\nEOF"), 2, MARKER),
    ("a marker inside a quoted string",
     doc("grep -F '" + MARK.rstrip() + " fake' f"), 1, MARKER),
    ("a marker with no reason is still the marker",
     doc("echo ok  # bracket-ranges: allow"), 1, MARKER),
    ("a marker misspelled past the colon is still the marker",
     doc("echo ok  # bracket-ranges: allowed maybe"), 1, MARKER),
    ("one finding per line however many marker attempts the line holds",
     doc("printf '%s" + BS + "n' '[a-z]' '# bracket-ranges: broken' " + MARK + "label"),
     2, MARKER),

    # REGRESSIONS, ROUNDS 1 AND 2. The joined-line bypasses, each with its original in-block
    # waiver attempt where it had one; every waiver attempt is now an in-guide-marker finding
    # and every range or unclosed bracket is found on its own line.
    ("codex r2-1: a waived literal bracket before a semicolon hid the next command's validator",
     doc("printf '%s\\n' '['; re='^[a-z]+$'  " + MARK + "literal bracket\n[[ é =~ $re ]]"),
     2, MARKER),
    ("codex r2-1 in the marker-above form",
     doc(MARK + "literal bracket\nprintf '%s\\n' '['; re='^[a-z]+$'\n[[ é =~ $re ]]"),
     2, "guide.md:6: " + MARKER),
    ("codex r2-1 with an empty pair: the range after it is still found",
     doc(MARK + "literal bracket\nprintf '%s\\n' '[]'; re='^[a-z]+$'\n[[ é =~ $re ]]"),
     2, "a-z"),
    ("codex r2-2: a parameter expansion split at the dollar sign",
     doc("re='^[a-z]+$' unused=$\\\n{u:-x " + MARK.rstrip() + " fake}\n[[ é =~ $re ]]"),
     2, MARKER),
    ("codex r2-3: a here-document terminator split by a continuation",
     doc("re=''\ncat <<EOF  " + MARK + "JSON data\n" + JSON_ARRAY + "\nE\\\nOF\nre='^[a-z]+$'\n"
         "cat <<EOF\ndone\nEOF\n[[ é =~ $re ]]"), 3, "guide.md:11:"),
    ("claude r2-1: an unreadable here-document delimiter with a waiver in the body",
     doc("d=EOF\ncat > check.sh <<$d\n[[ \"$1\" =~ ^[A-Za-z0-9]+$ ]]  " + MARK + "fake\nEOF\n"
         "sh check.sh x"), 2, MARKER),
    ("claude r2-2: an unquoted backslash does not hide a live bracket",
     doc("grep -cE \\[0-9] f"), 1, "0-9"),
    ("claude r2-2 with an anchored pattern",
     doc("grep -E ^\\[a-z]+$ f"), 1, "a-z"),
    ("claude r2-3: a reason quoting a range, and the quoted range is found too",
     doc("echo ok  " + MARK + "matches [a-z] here"), 2, "a-z"),
    ("a quote left open on an earlier line, with the waiver attempt inside it",
     doc("x='\n' ; [[ é =~ ^[a-z]+$ ]] ; y=' " + MARK.rstrip() + " fake'"), 2, MARKER),
    ("a bare-delimiter body line ending in a backslash, with the waiver attempt after it",
     doc("cat <<EOF\nx\\\nEOF\nre='^[a-z]+$'  " + MARK + "fake\nEOF"), 2, MARKER),
    ("a marker inside a parameter-expansion default",
     doc(GREP + " ${u:-x " + MARK.rstrip() + " fake}"), 2, MARKER),
    ("a marker inside a nested parameter expansion",
     doc(GREP + " ${u:-${v:-x} " + MARK.rstrip() + " fake}"), 2, MARKER),
    ("a marker inside a command substitution",
     doc('x="$(y ' + MARK.rstrip() + ' fake)"'), 1, MARKER),
    ("a marker inside backticks", doc("x=`y " + MARK.rstrip() + " fake`"), 1, MARKER),
    ("a marker covering a second command on the line",
     doc("grep -E '^[a-z]+$' a; grep -E '^[0-9]+$' b  " + MARK + "x"), 3, MARKER),
    ("claude r2-1 variant: a marker on a here-document opener line",
     doc("cat > f <<'EOF'  " + MARK + "x\n^[a-z]+$\nEOF"), 2, MARKER),

    # REGRESSIONS, ROUND 3. The bypasses of the round-3 one-line waiver lexing, verified
    # fail-open on that model (zero findings, the fake waiver counted as marked) and each at
    # least one finding now. The lexing they beat no longer exists.
    ("codex r3-1: an escaped space made a data # read as a comment",
     doc("bash -c '[[ é =~ ^[a-z]+$ ]]' x" + BS + " " + MARK + "fake"), 2, MARKER),
    ("codex r3-2: a trailing backslash dropped an open double quote",
     doc('bash -c "' + BS + "\n[[ é =~ ^[a-z]+$ ]] " + MARK + "fake\n" + Q), 2, MARKER),
    ("codex r3-3: a partly recognized here-document delimiter ended the body early",
     doc("bash <<true" + BS + "EOF\ntrue\n[[ é =~ ^[a-z]+$ ]] " + MARK + "fake\ntrueEOF"),
     2, MARKER),
    ("codex r3-4: a fake POSIX atom built from two printf arguments swallowed the validator",
     doc("printf '[[:'; re='^[a-z]+$'; printf ':]]" + BS + "n'\n[[ é =~ $re ]]"), 1, "a-z"),
    ("codex r3-5: quoting inside a parameter-removal pattern misread as closing the expansion",
     doc("v=x\nre='^[a-z]+$' ignored=\"${v#'}\" " + MARK + "fake'}\"\n"
         "printf '%s" + BS + "n' \"$ignored\"\n[[ é =~ $re ]]"), 2, MARKER),
    ("codex r3-6: only the last marker attempt on a line was validated",
     doc("printf '%s" + BS + "n' '[a-z]' '# bracket-ranges: broken' " + MARK + "label"),
     2, "a-z"),
    ("claude r3-1: a bare delimiter read as a prefix (EOF for EOF!) left the body early",
     doc("cat > check.sh <<EOF!\nx\nEOF\n[[ \"$1\" =~ ^[a-z]+$ ]]  " + MARK + "fake\nEOF!\n"
         "bash check.sh \"$1\""), 2, MARKER),
    ("claude r3-2: a here-document opened inside a command substitution went untracked",
     doc("v=$(cat <<'EOF')\n[[ é =~ ^[a-z]+$ ]]  " + MARK + "fake\nEOF"), 2, MARKER),
)
CASES += (
    # NOT FLAGGED.
    ("the spelled-out set",
     doc('case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*) '
         'exit 2 ;; esac'), 0, None),
    ("the test command, whose operands may hold a hyphen",
     doc('[ -r "$HOME/a-b.pem" ] || exit 2\n[[ -n "$x-y" ]] || exit 2\n([ -r a-b ]) || exit 2\n'
         '! [ -e a-b ] || exit 2'), 0, None),
    ("a quoted count", doc('[ "$#" -eq 1 ] || exit 2'), 0, None),
    ("a hyphen first or last in the set is literal",
     doc('case "$1" in *[-_.a]*|*[_.a-]*|*[^-a]*|*[-]*) exit 2 ;; esac'), 0, None),
    ("a POSIX class on its own, which is not a range",
     doc('case "$1" in *[[:space:][:cntrl:]]*|*[[:cntrl:]]*) exit 2 ;; esac'), 0, None),
    ("a C-scoped POSIX class, the mcp-clients.md shape",
     doc("env LC_ALL=C grep -o '[[:print:]]' f"), 0, None),
    ("a parameter expansion holding a #",
     doc('case "${1#https://}" in *:*[!0123456789]*) exit 2 ;; esac'), 0, None),
    ("an IPv6 literal in a URL", doc("curl -q -g -sS 'https://[2001:db8::1]:8443/'"), 0, None),
    ("a range in a yaml block", doc("pattern: '^[a-z]+$'", fence="```yaml"), 0, None),
    ("over-flagged: an empty pair in jq is not a bracket expression", doc("jq -r '.[] | .name' f.json"), 1,
     None),
    ("over-flagged: a regex [!] that no later bracket closes is the one-character set it is",
     doc("grep -E '[!]' f"), 1, None),
    ("a class whose atom never closes on its line is read as ordinary characters",
     doc("grep -E '[[:alpha]' f"), 0, None),
    ("a fake equivalence atom with a space inside is read as ordinary characters",
     doc("grep -E '[[=a b=]]' f"), 0, None),

    # OVER-FLAGGED, BY DESIGN. The recorded cost of failing closed; the docstring lists these.
    ("a quoted escaped bracket is read as a bracket",
     doc("grep -E '\\[a-z\\]' f"), 1, "a-z"),
    ("an array subscript holding arithmetic is read as a range",
     doc('echo "${a[i-1]}"'), 1, "i-1"),
    ("a Python slice is read as a range",
     doc("python3 -c 'print(x[1:-1])'"), 1, None),
    ("a spelled-out set split by a continuation is an unclosed bracket",
     doc('grep -E "^[0123456789abc\\\ndef]+$" f'), 1, UNCLOSED),
    ("a multi-line Python list in a here-document is an unclosed bracket",
     doc("python3 - <<'EOS'\nargs = [" + Q + "curl" + Q + ", " + Q + "-q" + Q + ",\n    " + Q
         + "-sS" + Q + "]\nEOS"), 1, "guide.md:7:"),
    ("a hyphen before a fake equivalence atom is read as a range, failing closed",
     doc("grep -E '[a-[=xy z=]]' f"), 1, "a-["),

    # FENCES AND LINES.
    ("a U+2028 inside a block does not shift the line number",
     doc("printf '%s' 'x" + chr(0x2028) + "y'\n" + GREP), 1, "guide.md:7:"),
    ("a block the file never closed", "# T\n\n```bash\n" + GREP + "\n", 1, "guide.md:4:"),
)
CASES += tuple(("a " + f + " fence", doc(GREP, fence=f), 1, None)
               for f in ("````bash", "~~~bash", "```Bash", "```bash {.numberLines}", "```bash "))
CASES += (
    # STILL NOT SEEN. Each asserts the CURRENT answer, so a change that closes one is loud.
    ("not seen: tr takes a range with no brackets",
     doc("tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32"), 0, None),
    ("not seen: a POSIX class is locale dependent and not flagged",
     doc('[[ "$1" =~ ^[[:alnum:]]+$ ]] || exit 2'), 0, None),
    ("not seen: a backslash-w class is locale dependent and not flagged",
     doc("grep -qE '^\\w+$' f"), 0, None),
    ("not seen: a sh, shell or zsh fence is not a bash fence and is not read",
     doc(GREP, fence="```sh"), 0, None),
    ("a test-shaped opener without a standalone close is scanned",
     doc("re='^ [ a-z]+$'\n[[ ' é' =~ $re ]]"), 1, None),
    ("not seen: brackets built by escapes hold no literal bracket",
     doc("re=$'" + BS + "x5bA-Za-z" + BS + "x5d'\n[[ é =~ $re ]]"), 0, None),
    ("an escaped hyphen retains a conservative unclosed alternative",
     doc("re=$'^[a" + BS + "x2dz]+$'\n[[ é =~ $re ]]"), 1, None),
    ("not seen: a range assembled from variables holds no literal X-Y in its brackets",
     doc("lo='a-'\nhi=z\nre=" + Q + "^[$lo$hi]+$" + Q + "\n[[ é =~ $re ]]"), 0, None),
)

# REGRESSIONS, ROUND 5, AND THE LAST-CLOSE RULE.
CASES += (
    ('round 5: a double-quoted close buried between letters',
     doc('case "$1" in *[!"x]y"a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: a single-quoted close buried between letters',
     doc('case "$1" in *[\'x]y\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: an ANSI-C quoted close buried between letters',
     doc('case "$1" in *[$\'x]y\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: a locale-quoted close buried between letters',
     doc('case "$1" in *[$"x]y"a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: nested quote characters around a buried close',
     doc('case "$1" in *["\'x]y\'"a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: an escaped close followed by a buried quoted close',
     doc('case "$1" in *[\\]\'x]y\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: mixed quotes around a buried close',
     doc('case "$1" in *[!\'x]"y"\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: a space after a buried quoted close',
     doc('case "$1" in *[!\'x] y\'a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: a quoted close at physical end of line',
     doc('case "$1" in *[!"x]\ny"a-z]*) exit 2 ;; esac'), 1, 'guide.md:6:'),
    ('round 5: empty quotes expose a leading glob negation',
     doc('case "$1" in *[""!]a-z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('round 5: empty quotes expose a leading regex negation',
     doc('re=[""^]a-z]\nprintf "%s\\n" "$1" | grep -qE "$re"'), 1, 'a-z'),
    ('round 5: empty quotes expose a leading Bash regex negation',
     doc('re=[""^]a-z]\n[[ $1 =~ $re ]]'), 1, 'a-z'),
    ('quotes join the two range endpoints',
     doc('case "$1" in *[a""-""z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('backslashes join the two range endpoints',
     doc('case "$1" in *[\\a-\\z]*) exit 2 ;; esac'), 1, 'a-z'),
    ('ANSI-C prefix deletion exposes a leading regex negation',
     doc("re=[$''^]a-z]"), 1, 'a-z'),
    ('locale prefix deletion exposes a leading regex negation',
     doc('re=[$""^]a-z]'), 1, 'a-z'),
    ('a quote after the ordinary close still affects the whole region',
     doc('re=[x]""a-z]'), 1, 'a-z'),
    ('a backslash after the ordinary close still affects the whole region',
     doc('re=[x]\\a-z]'), 1, 'a-z'),
    ('an interior close can itself be a range endpoint',
     doc('case "$1" in *["x]y"]-z]*) exit 2 ;; esac'), 1, ']-z'),
    ('no quote means no reading beyond the ordinary close',
     doc('re=[x]a-z]'), 0, None),
    ('a quote after an unambiguous closed prefix needs no span',
     doc('re=[x]a-z]"'), 0, None),
    ('over-flagged: quoted range-free members retain an open alternative',
     doc('case "$1" in *["x]y"abc]*) exit 2 ;; esac'), 1, None),
    ('over-flagged: quotes between two subscripts reach a line-final close',
     doc('digest = ("0" if digest[0] != "0" else "1") + digest[1:]'), 2, 'opens a bracket expression'),
    ('over-flagged: a range outside an earlier quote-affected set',
     doc('printf "%s\\n" \'["key"] a-z [abc]\''), 1, 'a-z'),
)

CASES += (
    ("quote removal restores collating atoms for the ordinary parser",
     doc("re=[[.'a'.]-[.'z'.]]"), 2, "[.a.]-[.z.]"),
)

JOIN_CASES = (
    (['re=[x]\\', 'a-z]'], 0, 're=[x]a-z]'),
    (['re=[!"x]y', 'middle', '"a-z]'], 0, 're=[!"x]y\nmiddle\n"a-z]'),
    (["re=[!'x]y", '', "'a-z]"], 0, "re=[!'x]y\n\n'a-z]"),
    (['re=[x]\\', 'y', 'outside=a-z]'], 0, 're=[x]y\noutside=a-z]'),
    (['re=[x]', 'outside=a-z]'], 0, 're=[x]\noutside=a-z]'),
    (['re=[x]\\'], 0, 're=[x]\\'),
)

JOIN_CASES += (
    (['re=\'[]\'"\'"\'-z', "]'"], 0, 're=\'[]\'"\'"\'-z\n]\''),
    (['re="[]"\'"\'"-z', ']"'], 0, 're="[]"\'"\'"-z\n]"'),
)

JOIN_CASES += (
    (['re=[x"\'"y\'', ']'], 0, 're=[x"\'"y\'\n]'),
    (['re=[x\'"\'y"', ']'], 0, 're=[x\'"\'y"\n]'),
)

# REGRESSIONS, ROUND 8: parity is not closure; literal closes survive newlines.
CASES += (
    ('round 8: even ANSI-C quote count',
     doc('case "$1" in *[!$\'x]y\\\'z\n\'a-z]*) exit 1 ;; esac'), 1, 'a-z'),
    ('round 8: even mixed quote count',
     doc('case "$1" in *[!\'a"b\'"x]y\n"a-z]*) exit 1 ;; esac'), 1, 'a-z'),
    ('round 8: negative literal close with balanced quotes',
     doc('re=$(cat <<\'EOF\'\n[^]a""\'\'\n-z]\nEOF\n)\n[[ $1 =~ $re ]]'), 1, 'guide.md:7:'),
    ('round 8: negative literal close without quotes',
     doc("re=$(cat <<'EOF'\n[^]a\n-z]\nEOF\n)\n[[ $1 =~ $re ]]"), 1, 'guide.md:7:'),
    ('round 8: positive literal close with balanced quotes',
     doc('re=$(cat <<\'EOF\'\n[]a""\'\'\n-z]\nEOF\n)\n[[ $1 =~ $re ]]'), 1, 'guide.md:7:'),
    ('round 8: positive literal close without quotes',
     doc("re=$(cat <<'EOF'\n[]a\n-z]\nEOF\n)\n[[ $1 =~ $re ]]"), 1, 'guide.md:7:'),
    ('round 8: glob literal close with balanced quotes',
     doc('re=$(cat <<\'EOF\'\n[!]a""\'\'\n-z]\nEOF\n)\n[[ $1 =~ $re ]]'), 1, 'guide.md:7:'),
    ('round 8: glob literal close without quotes',
     doc("re=$(cat <<'EOF'\n[!]a\n-z]\nEOF\n)\n[[ $1 =~ $re ]]"), 1, 'guide.md:7:'),
    ('round 8: quote-free bracket before independent ambiguous opener',
     doc('a=[x]; re=[^]a\n-z]'), 1, 'guide.md:6:'),
    ('round 8: block bound excludes a later fenced range tail',
     doc("re=[!$'x]y\\'z") + doc("echo a-z]"), 1, UNCLOSED),
)

JOIN_CASES += (
    (['case "$1" in *[!$\'x]y\\\'z', "'a-z]*) exit 1 ;; esac"], 0, 'case "$1" in *[!$\'x]y\\\'z\n\'a-z]*) exit 1 ;; esac'),
    (['case "$1" in *[!\'a"b\'"x]y', '"a-z]*) exit 1 ;; esac'], 0, 'case "$1" in *[!\'a"b\'"x]y\n"a-z]*) exit 1 ;; esac'),
    (['[^]a', 'middle', '-z]'], 0, '[^]a\nmiddle\n-z]'),
    (['[]a', '-z]'], 0, '[]a\n-z]'),
    (['[!]a', '-z]'], 0, '[!]a\n-z]'),
    (['re=[x]', 'a-z]'], 0, 're=[x]\na-z]'),
    (["re=[!$'x]y\\'z"], 0, "re=[!$'x]y\\'z"),
)

# The exact 1472 emitted round-8 exploratory misses, factored into Cartesian sets.
# A string in a column enumerates alternatives for that one character, not a substring.
R8_MISS_COLUMNS = (
    ('[', '\n', ' !"$\'.:=[\\^a', '-', 'xz', ' !-.:=^axz', ']'),
    ('[', '\n', ' !"$\'.:=[\\^a', '-', 'xz', ']'),
    ('[', '\n', ' !"$\'.:=[\\^axz', ' ^', '-', 'xz', ']'),
    ('[', '\n', ' !"$\'.:=\\^a', '-', 'xz', '"$\'\\', ']'),
    ('[', '\n', ' !"$\'.:=\\^axz', '!"$\'.:=[\\a', '-', 'xz', ']'),
    ('[', '\n', '-', 'xz', ' !"$\'-.:=\\^axz', ']'),
    ('[', '\n', '-', 'xz', ' !"$\'.:=[\\^axz', ' -axz', ']'),
    ('[', '\n', '-', 'xz', ' !"$\'.:=\\^axz', '!"$\'.:=\\^', ']'),
    ('[', '\n', '-', 'xz', '[', '[', ']'),
    ('[', '\n', '-', 'xz', ']'),
    ('[', '\n', '[', '-', 'xz', '[', ']'),
    ('[', '\n ', '!"$\'.:=[\\^axz', '\n', '-', 'xz', ']'),
    ('[', '\n ', '!"$\'.:=\\^a', '-', 'xz', '\n', ']'),
    ('[', '\n ', '-', 'xz', '\n', ' !"$\'-.:=\\^axz', ']'),
    ('[', '\n ', '-', 'xz', '\n', ']'),
    ('[', '\n ', '-', 'xz', '\n !"$\'.:=\\^axz', '\n', ']'),
    ('[', '\n [', '\n', ' !"$\'.:=[\\^a', '-', 'xz', ']'),
    ('[', '\n [', '\n', '-', 'xz', ' !"$\'-.:=\\^axz', ']'),
    ('[', '\n [', '\n', '-', 'xz', ']'),
    ('[', '\n [', '\n ', '\n', '-', 'xz', ']'),
    ('[', '\n [', '\n ', '-', 'xz', '\n', ']'),
    ('[', ' ', '-', 'xz', ']', '\n', ']'),
)
R8_MISSES = sorted({"".join(chars) for columns in R8_MISS_COLUMNS
                    for chars in itertools.product(*columns)})
assert len(R8_MISSES) == 1472
CASES += tuple(("round 8 fuzz heredoc: " + repr(pattern),
                doc("re=$(cat <<'EOF'\n" + pattern + "\nEOF\n)"), None, None)
               for pattern in R8_MISSES)
CASES += tuple(("round 8 fuzz single-word test: " + repr(pattern),
                doc("re=$(cat <<'EOF'\n" + pattern + "\nEOF\n)"), 1, None)
               for pattern in ("[ -z ]\n]", "[ -x ]\n]", "[ a-z ]\n]"))
CASES += (
    ("not seen: disclosed codex round-8 P1-2, test-shaped regex data",
     doc("set -- ' é '\nre='^ [ a-z x ] +$'\n[[ $1 =~ $re ]]"), 0, None),
    ("not seen: disclosed codex round-8 P1-1, empty variable across a quoted newline",
     doc("(\n  a=\n  set -- é\n  shopt -u globasciiranges\n"
         "  case \"$1\" in *[!$a]$'x\n'a-z]*) exit 1 ;; esac\n)"), 0, None),
)

# All 17 one-character lists before grep's separate two-dot alternative.
CASES += tuple(("round 8 terminal list: " + repr(c),
                doc("re=$(cat <<'EOF'\n[" + c + "]\n..\n]\nEOF\n)"), None, None)
               for c in "'\"\\]^!az-x$ \n[:=.")

QUOTE_CASES = (
    ('[""^]a-z]', '[^]a-z]'),
    ("[$''^]a-z]", '[^]a-z]'),
    ('[$""!]a-z]', '[!]a-z]'),
    ("[a" + BS + "-z$" + Q + Q + "$x]", '[a-z$x]'),
)

# Fixed counterexamples found by the development fuzzer with unset a, z and x.
CASES += (
    ('fuzz: glob [$a]-z]',
     doc('case "$1" in *[$a]-z]*) exit 2 ;; esac'), 1, None),
    ('fuzz: glob [$a]-x]',
     doc('case "$1" in *[$a]-x]*) exit 2 ;; esac'), 1, None),
    ('fuzz: glob [$z]-z]',
     doc('case "$1" in *[$z]-z]*) exit 2 ;; esac'), 1, None),
    ('fuzz: glob [$z]-x]',
     doc('case "$1" in *[$z]-x]*) exit 2 ;; esac'), 1, None),
    ('fuzz: glob [$x]-z]',
     doc('case "$1" in *[$x]-z]*) exit 2 ;; esac'), 1, None),
    ('fuzz: glob [$x]-x]',
     doc('case "$1" in *[$x]-x]*) exit 2 ;; esac'), 1, None),
)

CASES += (
    ("claude round 5: *[!'x]y'a-z]*",
     doc('case "$1" in *[!\'x]y\'a-z]*) exit 2 ;; esac'), 1, "a-z"),
    ("claude round 5: *[!$'x]y'a-z]*",
     doc('case "$1" in *[!$\'x]y\'a-z]*) exit 2 ;; esac'), 1, "a-z"),
)


# REGRESSIONS, ROUND 6: physical continuations and quoted newlines.
CASES += (
    ('round 6: continued buried close',
     doc('case "$1" in *[!"x]y"\\\na-z]*) exit 1 ;; esac'), 1, 'guide.md:6:'),
    ('round 6: empty quotes grep',
     doc('re=[""^]\\\na-z]\nprintf "%s\\n" "$1" | grep -qE "$re"'), 1, 'guide.md:6:'),
    ('round 6: empty quotes regex',
     doc('re=[""^]\\\na-z]\n[[ $1 =~ $re ]]'), 1, 'guide.md:6:'),
    ('round 6: quoted class',
     doc('re=\'^\'[[:\'digit\':]\\\na-z]\'$\'\nprintf \'%s\\n\' é | grep -qE "$re"'), 1, 'guide.md:6:'),
    ('round 6: quoted equivalence',
     doc('re=\'^\'[[=\'x\'=]\\\na-z]\'$\'\nprintf \'%s\\n\' é | grep -qE "$re"'), 1, 'guide.md:6:'),
    ('round 6: quoted collating',
     doc('re=\'^\'[[.\'x\'.]\\\na-z]\'$\'\nprintf \'%s\\n\' é | grep -qE "$re"'), 1, 'guide.md:6:'),
    ('round 6: quoted newline',
     doc('case "$1" in *[!"x]y\n"a-z]*) exit 1 ;; esac'), 1, 'guide.md:6:'),
    ('round 6: nested opener',
     doc('case "$1" in *[![["x]y"\\\na-z]*) exit 1 ;; esac'), 1, 'guide.md:6:'),
    ('round 6: heredoc',
     doc('bash <<\'EOF\'\nset -- é\nshopt -u globasciiranges\ncase "$1" in *[!"x]y"\\\na-z]*) exit 1 ;; esac\nEOF'), 1, 'guide.md:9:'),
    ('continued endpoints',
     doc('re=[""^]a\\\n-\\\nz]'), 1, 'a-z'),
    ('quoted member across three lines',
     doc('re=[!"x]y\nmiddle\n"a-z]'), 1, 'a-z'),
    ('single-quoted member across three lines',
     doc("re=[!'x]y\nmiddle\n'a-z]"), 1, 'a-z'),
    ('unclosed stripped spanning list',
     doc('re=["xy\\\ntext'), 1, 'opens a bracket expression that nothing closes'),
    ('a later opener retains its own line',
     doc('re=[x]\\\nother=[a-z]'), 2, 'guide.md:7:'),
    ('joining retains uncertainty past a balanced line',
     doc('re=[x]\\\ny\nother=a-z]'), 1, 'guide.md:6:'),
    ('a comment quote cannot reopen an unambiguous closed prefix',
     doc("re=[x] # a single quote '\necho a-z]"), 0, None),
    ('range with newline endpoint',
     doc('re=[!"x]y\n"-z]'), 1, '\\n-z'),
    ('joining cannot cross a fence',
     doc("re=[x'y]") + doc("echo a-z]"), 1, UNCLOSED),
)

# Every counterexample emitted by the first widened exploratory run.
# Regex engines receive literal text, represented by a quoted shell assignment.
FUZZ_CASES = {'grep': ['[^]].\n]',
          '[^^].\n]',
          '[^!].\n]',
          '[^a].\n]',
          '[^z].\n]',
          '[^-].\n]',
          '[^x].\n]',
          '[^$].\n]',
          '[^ ].\n]',
          '[^[].\n]',
          '[^:].\n]',
          '[^=].\n]',
          '[^.].\n]'],
 'regex': ['[]-z\n]',
           '[]-x\n]',
           '[]\n-z]',
           '[]\n-x]',
           '[]\\-z\n]',
           '[]\\-x\n]',
           '[]^-z\n]',
           '[]^-x\n]',
           '[]^\n-z]',
           '[]^\n-x]',
           '[]!-z\n]',
           '[]!-x\n]',
           '[]!\n-z]',
           '[]!\n-x]',
           '[]a-z\n]',
           '[]a-x\n]',
           '[]a\n-z]',
           '[]a\n-x]',
           '[]z\n-z]',
           '[]z\n-x]',
           '[]-z^\n]',
           '[]-z!\n]',
           '[]-za\n]',
           '[]-zz\n]',
           '[]-zx\n]',
           '[]-z$\n]',
           '[]-z \n]',
           "[]-z\n']",
           '[]-z\n"]',
           '[]-z\n\\]',
           '[]-z\n^]',
           '[]-z\n!]',
           '[]-z\na]',
           '[]-z\nz]',
           '[]-z\n-]',
           '[]-z\nx]',
           '[]-z\n$]',
           '[]-z\n ]',
           '[]-z\n\n]',
           '[]-z\n[]',
           '[]-z\n:]',
           '[]-z\n=]',
           '[]-z\n.]',
           '[]-z:\n]',
           '[]-z=\n]',
           '[]-z.\n]',
           '[]-x^\n]',
           '[]-x!\n]',
           '[]-xa\n]',
           '[]-xz\n]',
           '[]-xx\n]',
           '[]-x$\n]',
           '[]-x \n]',
           "[]-x\n']",
           '[]-x\n"]',
           '[]-x\n\\]',
           '[]-x\n^]',
           '[]-x\n!]',
           '[]-x\na]',
           '[]-x\nz]',
           '[]-x\n-]',
           '[]-x\nx]',
           '[]-x\n$]',
           '[]-x\n ]',
           '[]-x\n\n]',
           '[]-x\n[]',
           '[]-x\n:]',
           '[]-x\n=]',
           '[]-x\n.]',
           '[]-x:\n]',
           '[]-x=\n]',
           '[]-x.\n]',
           '[]x\n-z]',
           '[]x\n-x]',
           '[]$-z\n]',
           '[]$-x\n]',
           '[]$\n-z]',
           '[]$\n-x]',
           '[] -z\n]',
           '[] -x\n]',
           '[] \n-z]',
           '[] \n-x]',
           "[]\n'-z]",
           "[]\n'-x]",
           '[]\n"-z]',
           '[]\n"-x]',
           '[]\n\\-z]',
           '[]\n\\-x]',
           '[]\n^-z]',
           '[]\n^-x]',
           '[]\n!-z]',
           '[]\n!-x]',
           '[]\na-z]',
           '[]\na-x]',
           "[]\n-z']",
           '[]\n-z"]',
           '[]\n-z\\]',
           '[]\n-z^]',
           '[]\n-z!]',
           '[]\n-za]',
           '[]\n-zz]',
           '[]\n-z-]',
           '[]\n-zx]',
           '[]\n-z$]',
           '[]\n-z ]',
           '[]\n-z\n]',
           '[]\n-z[]',
           '[]\n-z:]',
           '[]\n-z=]',
           '[]\n-z.]',
           "[]\n-x']",
           '[]\n-x"]',
           '[]\n-x\\]',
           '[]\n-x^]',
           '[]\n-x!]',
           '[]\n-xa]',
           '[]\n-xz]',
           '[]\n-x-]',
           '[]\n-xx]',
           '[]\n-x$]',
           '[]\n-x ]',
           '[]\n-x\n]',
           '[]\n-x[]',
           '[]\n-x:]',
           '[]\n-x=]',
           '[]\n-x.]',
           '[]\n$-z]',
           '[]\n$-x]',
           '[]\n -z]',
           '[]\n -x]',
           '[]\n\n-z]',
           '[]\n\n-x]',
           '[]\n[-z]',
           '[]\n[-x]',
           '[]\n:-z]',
           '[]\n:-x]',
           '[]\n=-z]',
           '[]\n=-x]',
           '[]\n.-z]',
           '[]\n.-x]',
           '[]:-z\n]',
           '[]:-x\n]',
           '[]:\n-z]',
           '[]:\n-x]',
           '[]=-z\n]',
           '[]=-x\n]',
           '[]=\n-z]',
           '[]=\n-x]',
           '[].-z\n]',
           '[].-x\n]',
           '[].\n-z]',
           '[].\n-x]',
           '[^]-z\n]',
           '[^]-x\n]',
           '[^]\n-z]',
           '[^]\n-x]',
           "[]'-z\n]",
           "[]'-x\n]",
           "[]'\n-z]",
           "[]'\n-x]",
           "[]-z'\n]",
           "[]-x'\n]"]}
CASES += tuple((f'fuzz multiline {engine}: {pattern!r}',
                doc('re=' + shlex.quote(pattern)), None, 'guide.md:6:')
               for engine, patterns in FUZZ_CASES.items() for pattern in patterns)

CASES += (("over-flagged: a continuation enables the broad range reading",
           doc('re=[x]\\\na-z]'), 1, "holds the range a-z"),)

# Exact adjacent-list counterexamples emitted by the widened oracle.
ADJACENT_MISSES = (('grep', '[^"]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^"]', '^', ']^!az-x$ [:=.'),
 ('grep', '[^\\]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^\\]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^]]', '^', ']^!az-x$[:=.'),
 ('glob', '[^]]', '!', ']^!az-x$[:=.'),
 ('grep', '[^]]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^]]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^^]', '^', ']^!az-x$[:=.'),
 ('glob', '[^^]', '!', ']^!az-x$[:=.'),
 ('grep', '[^^]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^^]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^!]', '^', ']^!az-x$[:=.'),
 ('glob', '[^!]', '!', ']^!az-x$[:=.'),
 ('grep', '[^!]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^!]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^a]', '^', ']^!az-x$[:=.'),
 ('glob', '[^a]', '!', ']^!az-x$[:=.'),
 ('grep', '[^a]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^a]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^z]', '^', ']^!az-x$[:=.'),
 ('glob', '[^z]', '!', ']^!az-x$[:=.'),
 ('grep', '[^z]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^z]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^-]', '^', ']^!az-x$[:=.'),
 ('glob', '[^-]', '!', ']^!az-x$[:=.'),
 ('grep', '[^-]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^-]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^x]', '^', ']^!az-x$[:=.'),
 ('glob', '[^x]', '!', ']^!az-x$[:=.'),
 ('grep', '[^x]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^x]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^$]', '^', ']^!az-x$[:=.'),
 ('glob', '[^$]', '!', ']^!az-x$[:=.'),
 ('grep', '[^$]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^$]', '^', ']^!az-x$ [:=.'),
 ('grep', '[^ ]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^ ]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^[]', '^', ']^!az-x$[:=.'),
 ('glob', '[^[]', '!', ']^!az-x$[:=.'),
 ('grep', '[^[]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^[]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^:]', '^', ']^!az-x$[:=.'),
 ('glob', '[^:]', '!', ']^!az-x$[:=.'),
 ('grep', '[^:]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^:]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^=]', '^', ']^!az-x$[:=.'),
 ('glob', '[^=]', '!', ']^!az-x$[:=.'),
 ('grep', '[^=]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^=]', '^', ']^!az-x$ [:=.'),
 ('glob', '[^.]', '^', ']^!az-x$[:=.'),
 ('glob', '[^.]', '!', ']^!az-x$[:=.'),
 ('grep', '[^.]', '^', ']^!az-x$ [:=.'),
 ('regex', '[^.]', '^', ']^!az-x$ [:=.'),
 ('glob', '[!]]', '^', ']^!az-x$[:=.'),
 ('glob', '[!]]', '!', ']^!az-x$[:=.'),
 ('glob', '[!^]', '^', ']^!az-x$[:=.'),
 ('glob', '[!^]', '!', ']^!az-x$[:=.'),
 ('glob', '[!!]', '^', ']^!az-x$[:=.'),
 ('glob', '[!!]', '!', ']^!az-x$[:=.'),
 ('glob', '[!a]', '^', ']^!az-x$[:=.'),
 ('glob', '[!a]', '!', ']^!az-x$[:=.'),
 ('glob', '[!z]', '^', ']^!az-x$[:=.'),
 ('glob', '[!z]', '!', ']^!az-x$[:=.'),
 ('glob', '[!-]', '^', ']^!az-x$[:=.'),
 ('glob', '[!-]', '!', ']^!az-x$[:=.'),
 ('glob', '[!x]', '^', ']^!az-x$[:=.'),
 ('glob', '[!x]', '!', ']^!az-x$[:=.'),
 ('glob', '[!$]', '^', ']^!az-x$[:=.'),
 ('glob', '[!$]', '!', ']^!az-x$[:=.'),
 ('glob', '[![]', '^', ']^!az-x$[:=.'),
 ('glob', '[![]', '!', ']^!az-x$[:=.'),
 ('glob', '[!:]', '^', ']^!az-x$[:=.'),
 ('glob', '[!:]', '!', ']^!az-x$[:=.'),
 ('glob', '[!=]', '^', ']^!az-x$[:=.'),
 ('glob', '[!=]', '!', ']^!az-x$[:=.'),
 ('glob', '[!.]', '^', ']^!az-x$[:=.'),
 ('glob', '[!.]', '!', ']^!az-x$[:=.'))
CASES += tuple((f'fuzz adjacent {engine}: {first + second!r}',
                doc('case "$1" in *' + first + second + '*) :;; esac'
                    if engine == 'glob' else 're=' + shlex.quote(first + second)),
                None, 'adjacent negated bracket lists')
               for engine, first, negation, members in ADJACENT_MISSES
               for member in members for second in ('[' + negation + member + ']',))

CASES += (
    ('empty atom broad reading: [..]-z',
     doc('case "$1" in *[[..]-z]*) :;; esac'), 1, '-z'),
    ('empty atom broad reading: [..]-x',
     doc('case "$1" in *[[..]-x]*) :;; esac'), 1, '-x'),
    ('empty atom broad reading: [==]-z',
     doc('case "$1" in *[[==]-z]*) :;; esac'), 1, '-z'),
    ('empty atom broad reading: [::]-z',
     doc('case "$1" in *[[::]-z]*) :;; esac'), 1, '-z'),
)

CASES += (
    ('claude round 6: a literal opener in a collating atom',
     doc("re='[[.[.]-z]'"), 1, '-z'),
    ('literal opener in an equivalence atom: conservative reading',
     doc("re='[[=[=]-z]'"), 1, '-z'),
)

# (description, guide text, allowlist text, exact findings, substring or None)
ALLOW_CASES = (
    ("an entry waives its exact line", doc(GREP), entry(GREP), 0, None),
    ("moving unchanged text within the same guide keeps its waiver",
     doc("echo moved\n" + GREP), entry(GREP), 0, None),
    ("changing the preceding command keeps the same line's waiver: review the context",
     doc("printf '%s\\n' é | grep -qxE \\\n  '[a-z]'"),
     entry("  '[a-z]'", reason="originally a continued printf label; now unsafe"), 0, None),
    ("one entry waives every finding on its one line",
     doc('case "$1" in *[!a-z]*|*[!0-9]*) exit 2 ;; esac'),
     entry('case "$1" in *[!a-z]*|*[!0-9]*) exit 2 ;; esac'), 0, None),
    ("an unclosed bracket's line can be waived",
     doc("python3 - <<'EOS'\nargs = [" + Q + "curl" + Q + ",\n    " + Q + "-sS" + Q + "]\nEOS"),
     entry("args = [" + Q + "curl" + Q + ",\n    " + Q + "-sS" + Q + "]\nEOS"), 0, None),
    ("the whole line must match, not a substring: a line that grew a second command",
     doc(GREP + "; rm -f g"), entry(GREP), 2, STALE),
    ("the whole line must match: leading whitespace counts",
     doc("  " + GREP), entry(GREP), 2, STALE),
    ("an entry names its guide", doc(GREP), entry(GREP, guide="other.md"), 2, STALE),
    ("an entry no flagged line consumes is stale",
     doc("echo ok"), entry(GREP), 1, "allow.txt:1: " + STALE),
    ("an entry matching an unflagged line is stale too",
     doc("echo a-z"), entry("echo a-z"), 1, STALE),
    ("an entry with an empty reason",
     doc(GREP), entry(GREP, reason=""), 2, "empty reason"),
    ("an entry with two fields is malformed",
     doc(GREP), "guide.md\t" + GREP, 2, "malformed allowlist entry"),
    ("an entry with one field is malformed",
     doc(GREP), "guide.md", 2, "malformed allowlist entry"),
    ("an entry with an empty line text is malformed",
     doc(GREP), "guide.md\t\tr", 2, "malformed allowlist entry"),
    ("comment and blank lines in the allowlist are skipped",
     doc(GREP), "# c\n\n" + entry(GREP), 0, None),
    ("two occurrences of one line consume two entries",
     doc(GREP + "\n" + GREP), entry(GREP) + "\n" + entry(GREP), 0, None),
    ("one entry does not cover a second occurrence of its line",
     doc(GREP + "\n" + GREP), entry(GREP), 1, "guide.md:7:"),
    ("a duplicate entry beyond the real occurrences is stale",
     doc(GREP), entry(GREP) + "\n" + entry(GREP), 1, "allow.txt:2: " + STALE),
    ("an entry does not silence the in-guide marker finding on its line",
     doc(GREP + "  " + MARK + "x"), entry(GREP + "  " + MARK + "x"), 1, MARKER),
    ("an entry matches the line as the block extraction yields it, fence indentation removed",
     "# T\n\n- step:\n\n  ```bash\n  " + GREP + "\n  ```\n", entry(GREP), 0, None),
    ("a TAB inside the source text is bound by its digest",
     doc("grep -E '^[a-z]+$'\tf"), entry("grep -E '^[a-z]+$'\tf"), 0, None),
    ("an entry for a non-bash fence is stale, since that fence is not read",
     doc("pattern: '^[a-z]+$'", fence="```yaml"), entry("pattern: '^[a-z]+$'"), 1, STALE),
)


SPAN = 're=[""^]' + BS + "\na-z]"
ALLOW_CASES += (
    ("a spanning finding needs every original physical line",
     doc(SPAN), entry(SPAN), 0, None),
    ("an opener-only waiver is stale",
     doc(SPAN), entry(SPAN.split("\n")[0]), 2, STALE),
    ("a continuation-line waiver does not cover its opener",
     doc(SPAN), entry("a-z]"), 2, STALE),
    ("removing a physical continuation changes the key",
     doc(SPAN), entry('re=[""^]a-z]'), 2, STALE),
    ("a changed continuation tail leaves its full-span waiver stale",
     doc("[\na-z]"), entry("[\njson]"), 2, STALE),
    ("the Elasticsearch bare opener cannot waive a heredoc range",
     doc("re=$(cat <<'EOF'\n[\na-z]\nEOF\n)\n[[ $1 =~ $re ]]"),
     entry("["), 2, STALE),
    ("literal backslash-n is distinct from a physical newline",
     doc("[\na-z]"), entry(r"[\na-z]"), 2, STALE),
    ("a span digest preserves a literal backslash-n",
     doc(r"re='[a-z]\n'"), entry(r"re='[a-z]\n'"), 0, None),
    ("a bare number is not a span digest", doc(GREP), "guide.md\t42\treason", 2,
     "malformed allowlist span"),
    ("invalid digest text is refused", doc(GREP), 'guide.md\tsha256:xyz\treason', 2,
     "malformed allowlist span"),
    ("a raw TAB inside a span field is malformed", doc(GREP),
     'guide.md\tbad\ttext\treason', 2, "malformed allowlist entry"),
    ("an appended physical line invalidates a spanning waiver",
     doc("[\na-z]\necho changed"), entry("[\na-z]"), 2, STALE),
    ("an independent later opener still needs its own waiver",
     doc("[\na-z]\nre='[0-9]'"), entry("[\na-z]\nre='[0-9]'"), 1, "0-9"),
)


def run_repo(files, unreadable_dir=False, unreadable_allow=False):
    """Build a throwaway repository and run the shipped gate in it. Returns (exit, stdout)."""
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        for name in ("check_bracket_ranges.py", "check_shell_blocks.py", "_walk.py",
                     "_markdown.py"):
            shutil.copy(TOOLS / name, d / "tools" / name)
        for rel, body in files:
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(body, bytes):
                p.write_bytes(body)
            else:
                p.write_text(body, encoding="utf-8")
        if unreadable_allow:
            (d / "tools" / "bracket_ranges_allow.txt").chmod(0o000)
        if unreadable_dir:
            blocked = d / "blocked"
            blocked.mkdir()
            (blocked / "x.md").write_text("# x\n", encoding="utf-8")
            blocked.chmod(0o000)
        r = subprocess.run([sys.executable, "tools/check_bracket_ranges.py"], cwd=d,
                           capture_output=True, text=True)
        return r.returncode, r.stdout
    finally:
        if unreadable_dir:
            (d / "blocked").chmod(0o755)
        if unreadable_allow:
            (d / "tools" / "bracket_ranges_allow.txt").chmod(0o644)
        shutil.rmtree(d, ignore_errors=True)


def entry_point_failures():
    """Run the shipped entry point. Returns (failures, runs)."""
    failures, runs = [], 0
    clean = doc("echo ok")
    root_ok = os.geteuid() == 0 if hasattr(os, "geteuid") else True

    # Every guide and every block, not just the first of each.
    runs += 1
    rc, out = run_repo((
        ("a.md", "# A\n\n## Verify\n\n```bash\necho ok\n```\n\n```bash\n" + GREP + "\n```\n"),
        ("b.md", doc("grep -E '^[0-9]+$' f"))))
    if rc != 1 or "a.md:10:" not in out or "b.md:6:" not in out:
        failures.append(f"the second block of one guide and the first of another were not both "
                        f"reported: {out!r}")

    # The pass line counts expressions: one consumed entry here covers two expressions.
    runs += 1
    two = "printf '%s\\n' '[a-z]' '[0-9]'"
    rc, out = run_repo((("a.md", clean), ("b.md", doc(two)),
                        ("tools/bracket_ranges_allow.txt",
                         entry(two, guide="b.md") + "\n")))
    if rc != 0 or "in 2 bash blocks across 2 guides (2 expressions waived by " + ALLOW + ")" not in out:
        failures.append(f"the pass line does not count every block, guide and waived range: "
                        f"{out!r}")

    # A missing allowlist is an empty allowlist: nothing is waived.
    runs += 1
    rc, out = run_repo((("a.md", clean), ("b.md", doc(GREP))))
    if rc != 1 or "b.md:6:" not in out:
        failures.append(f"a repository without an allowlist file waived something: {out!r}")

    # A stale entry fails through the entry point, naming the allowlist line.
    runs += 1
    rc, out = run_repo((("a.md", clean),
                        ("tools/bracket_ranges_allow.txt", entry(GREP, guide="a.md") + "\n")))
    if rc != 1 or ALLOW + ":1: " + STALE not in out:
        failures.append(f"a stale allowlist entry did not fail the gate: {out!r}")

    # Repository documents and subdirectories are not guides.
    runs += 1
    rc, out = run_repo((("a.md", clean), ("CHANGELOG.md", doc(GREP)),
                        ("requests/x.md", doc(GREP))))
    if rc != 0:
        failures.append(f"CHANGELOG.md or a subdirectory was read as a guide: {out!r}")

    # CONTRIBUTING.md and README.md are read: new guides copy their blocks.
    runs += 1
    rc, out = run_repo((("a.md", clean), ("CONTRIBUTING.md", doc(GREP)),
                        ("README.md", doc("grep -E '^[0-9]+$' f"))))
    if rc != 1 or "CONTRIBUTING.md:6:" not in out or "README.md:6:" not in out:
        failures.append(f"CONTRIBUTING.md or README.md was not scanned: {out!r}")

    # A pass over nothing is not a pass.
    runs += 1
    rc, out = run_repo((("a.md", doc("pattern: x", fence="```yaml")),))
    if rc != 1 or "nothing was checked" not in out:
        failures.append(f"a corpus with no bash block passed: {out!r}")

    runs += 1
    rc, out = run_repo((("a.md", clean), ("b.md", b"# B\n\n```bash\necho \xff\n```\n")))
    if rc != 1 or "b.md: unreadable" not in out:
        failures.append(f"a guide that is not UTF-8 did not fail the gate: {out!r}")

    # run_all_checks.sh reads the FAIL prefix; every finding line must carry it, and the fix.
    runs += 1
    rc, out = run_repo((("a.md", doc(GREP)),))
    lines = [line for line in out.splitlines() if line.strip()]
    if rc != 1 or not all(line.startswith("  FAIL  ") for line in lines) \
            or "Spell the set out" not in out:
        failures.append(f"a finding did not print in the suite's FAIL format with the fix: "
                        f"{out!r}")

    # An unreadable allowlist has to fail closed, not read as empty. Root reads through
    # mode 000, so it cannot test this.
    if not root_ok:
        runs += 1
        rc, out = run_repo((("a.md", clean),
                            ("tools/bracket_ranges_allow.txt", entry(GREP) + "\n")),
                           unreadable_allow=True)
        if rc != 1 or "could not scan" not in out:
            failures.append(f"an unreadable allowlist did not fail the gate: {out!r}")

    # An unlistable subtree has to fail closed.
    if not root_ok:
        runs += 1
        rc, out = run_repo((("a.md", clean),), unreadable_dir=True)
        if rc != 1 or "could not scan" not in out:
            failures.append(f"an unlistable subtree did not fail the walk: {out!r}")
    return failures, runs


def corpus_waiver_failures():
    """Every checked-in waiver matches a real span; editing any physical line invalidates it."""
    root = TOOLS.parent
    allow_path = TOOLS / gate.ALLOWLIST
    allow = gate.Allowlist.load(allow_path)
    failures, consumed = list(allow.findings), []
    take = allow.take

    def record(name, span):
        matched = take(name, span)
        if matched:
            consumed.append((name, span))
        return matched

    allow.take = record
    blocks = {}
    for path in sorted(root.glob("*.md")):
        if path.name in gate.NOT_A_GUIDE:
            continue
        blocks[path.name] = list(gate.blocks_of(path))
        failures.extend(gate.scan_blocks(path.name, blocks[path.name], allow)[0])
    failures.extend(allow.stale())
    if failures:
        return failures, len(consumed), 0
    edits = 0
    occurrences = {}
    for name, span in consumed:
        physical = span.split("\n")
        locations = []
        for block_index, (_, body) in enumerate(blocks[name]):
            lines = body.split("\n")
            locations.extend((block_index, i) for i in range(len(lines))
                             if lines[i:i + len(physical)] == physical)
        occurrence = occurrences.get((name, span), 0)
        occurrences[name, span] = occurrence + 1
        if occurrence >= len(locations):
            failures.append(f"{name}: waiver has no exact physical occurrence")
            continue
        block_index, opener = locations[occurrence]
        start, body = blocks[name][block_index]
        if "--show-waivers" in sys.argv:
            first = start + opener
            print(f"  waiver {name}:{first}-{first + len(physical) - 1} "
                  f"sha256:{hashlib.sha256(span.encode('utf-8')).hexdigest()}")
            print(json.dumps(span, ensure_ascii=False))

        def matching_keys(candidate):
            audit = gate.Allowlist()
            keys = []

            def record_key(guide, text):
                if (guide, text) == (name, span):
                    keys.append(text)
                return False

            audit.take = record_key
            gate.scan_blocks(name, [(start, candidate)], audit)
            return len(keys)

        original_matches = matching_keys(body)
        for offset in range(len(physical)):
            lines = body.split("\n")
            lines[opener + offset] += " # changed waiver span"
            edits += 1
            # Removing a finding also invalidates its old waiver. The exact key must
            # disappear even if there is no replacement finding on the edited line.
            changed = "\n".join(lines)
            if matching_keys(changed) != original_matches - 1:
                failures.append(f"{name}: edit to span line {offset + 1} kept its waiver")
            isolated = Path(tempfile.mkdtemp())
            try:
                one = isolated / "allow.txt"
                one.write_text(entry(span, guide=name), encoding="utf-8")
                check = gate.Allowlist.load(one)
                gate.scan_blocks(name, [(start, changed)], check)
                if len(check.stale()) != 1:
                    failures.append(f"{name}: edit to span line {offset + 1} was not stale")
            finally:
                shutil.rmtree(isolated)
    return failures, len(consumed), edits


def main() -> int:
    failures = []
    for desc, text, want, expected in CASES:
        found = findings(text)
        if (not found if want is None else len(found) != want):
            failures.append(f"{desc}: expected {want} finding(s), got {len(found)}: {found!r}")
        elif expected is not None and not any(expected in f for f in found):
            failures.append(f"{desc}: no finding contains {expected!r}: {found!r}")
    for desc, text, allow, want, expected in ALLOW_CASES:
        found = findings(text, allow)
        if len(found) != want:
            failures.append(f"{desc}: expected {want} finding(s), got {len(found)}: {found!r}")
        elif expected is not None and not any(expected in f for f in found):
            failures.append(f"{desc}: no finding contains {expected!r}: {found!r}")
    for raw, expected in QUOTE_CASES:
        actual = gate._strip_quotes(raw)
        if actual != expected:
            failures.append(f"quote removal: {raw!r}: expected {expected!r}, got {actual!r}")
    for lines, idx, expected in JOIN_CASES:
        actual = gate.joined_reading(lines, idx)
        if actual != expected:
            failures.append(f"joined reading: {lines!r}: expected {expected!r}, got {actual!r}")
    more, bindings, edits = corpus_waiver_failures()
    failures += more
    more, runs = entry_point_failures()
    failures += more
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    n = len(CASES) + len(ALLOW_CASES) + len(QUOTE_CASES) + len(JOIN_CASES)
    unseen = sum(1 for c in CASES if c[0].startswith("not seen:"))
    print(f"  ok    {n} recorded cases and {runs} entry-point runs for the bracket-ranges "
          f"gate: {n - unseen} behaviours checked, {unseen} disclosed blind spots still "
          f"open")
    print(f"  ok    {bindings} corpus waiver bindings; {edits} physical-line edits "
          f"each invalidate their span and leave a stale entry")
    return 0


if __name__ == "__main__":
    sys.exit(main())
