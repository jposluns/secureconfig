#!/usr/bin/env python3
r"""Cases for check_bracket_ranges.py, including what it deliberately over-flags.

Most cases hand one guide to the gate's own scan_path and assert the exact number of findings
and a substring of one, so a stale marker, a refused waiver and an unmarked range are counted
apart rather than merged into "it failed". The ENTRY POINT group builds throwaway repositories
and runs the shipped file, for what only the entry point does: choosing which files to read, the
pass line, the exit status, and failing closed on an unreadable guide, an unlistable directory,
or a corpus with no bash block in it.

The REGRESSIONS group pins every bypass the two adversarial review rounds found against the
joined-line models this gate replaced. Each of those bypasses produced zero findings then; each
is at least one finding now, by construction of the physical-line model: a range and its waiver
must share a physical line, a `[` that its own line does not close is a finding wherever the
closing half went, and a waiver is refused, loudly, whenever the one-line scan cannot prove its
`#` is a comment.

The OVER-FLAGGED group asserts the cost of failing closed on inputs a shell parser would accept,
so the docstring's list stays honest, and the NOT SEEN group asserts what the gate still does
not read at all, so closing one of those is loud too.
"""
import os
import re
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
JSON_ARRAY = "[" + Q + "app-data" + Q + "]"
UNCLOSED = "opens a bracket expression that nothing closes"
REFUSED = "waiver refused"
STALE = "stale bracket-ranges marker"


def doc(block, fence="```bash"):
    """A guide whose one block starts on line 6, which the line numbers below assume."""
    close = re.match(r"[`~]+", fence).group(0)
    return "# T\n\n## Verify\n\n" + fence + "\n" + block + "\n" + close + "\n"


def findings(text):
    """Run the gate's scanner over one guide held in a throwaway file."""
    d = Path(tempfile.mkdtemp())
    try:
        p = d / "guide.md"
        p.write_text(text, encoding="utf-8")
        return gate.scan_path(p)[0]
    finally:
        shutil.rmtree(d, ignore_errors=True)


# (description, guide text, exact number of findings, substring one finding must contain or None)
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
    ("a JSON array holding a hyphenated string takes a marker, by design",
     doc("printf '%s' '" + JSON_ARRAY + "'"), 1, "p-d"),
    ("a range under LC_ALL=C still takes a marker", doc("LC_ALL=C " + GREP), 1, None),
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
     doc('[[ "$t" =~ ^[0-9a-\\\nf]+$ ]] || exit 2'), 1, UNCLOSED),
    ("the surrealdb JWT check split after A-Za-, the round-1 reproduction",
     doc('  [[ "$probe_jwt" =~ ^[A-Za-\\\nz0-9_.-]+$ ]] || { echo ' + "'missing or malformed "
         "JWT; not probing'; exit 2; }"), 1, "guide.md:6:"),
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

    # A WAIVER COVERS ITS OWN PHYSICAL LINE, AND ONLY A LINE THAT IS ONE COMMAND.
    ("a marker at the end of the line covers its range", doc(GREP + "  " + MARK + "a search "
     "pattern"), 0, None),
    ("a marker on the line above no longer exists, and is stale there",
     doc(MARK + "a search pattern\n" + GREP), 2, "guide.md:6: " + STALE),
    ("a marker beside a semicolon is refused, covering neither command",
     doc("grep -E '^[a-z]+$' a; grep -E '^[0-9]+$' b  " + MARK + "x"), 3, REFUSED),
    ("a marker above a line with two commands is stale, covering neither",
     doc(MARK + "x\ngrep -E '^[a-z]+$' a && grep -E '^[0-9]+$' b"), 3, STALE),
    ("a marker beside a pipe is refused",
     doc(GREP + " | head -n 1  " + MARK + "x"), 2, REFUSED),
    ("a marker beside a lone ampersand is refused",
     doc("grep -E '^[a-z]+$' a & grep -E '^[0-9]+$' b  " + MARK + "x"), 3, REFUSED),
    ("a marker after a trailing semicolon is refused",
     doc(GREP + ";  " + MARK + "x"), 2, REFUSED),
    ("a marker at the end of one line does not reach the next",
     doc(GREP.replace(" f", " a") + "  " + MARK + "x\ngrep -E '^[0-9]+$' b"), 1, "guide.md:7:"),
    ("a redirection's ampersand refuses nothing",
     doc(GREP + " 2>&1 >/dev/null &>/dev/null  " + MARK + "x"), 0, None),
    ("a semicolon inside quotes refuses nothing",
     doc("grep -E '^[a-z]+;$' f  " + MARK + "x"), 0, None),

    # MARKERS THAT ARE NOT COMMENTS ARE REFUSED, LOUDLY.
    ("a marker inside a parameter-expansion default is refused",
     doc(GREP + " ${u:-x " + MARK.rstrip() + " fake}"), 2, REFUSED),
    ("a marker inside a nested parameter expansion is refused",
     doc(GREP + " ${u:-${v:-x} " + MARK.rstrip() + " fake}"), 2, REFUSED),
    ("a marker inside a quoted string is refused",
     doc("grep -E '^[a-z]+$ " + MARK.rstrip() + " fake' f"), 2, REFUSED),
    ("a marker inside a command substitution is refused",
     doc('x="$(y ' + MARK.rstrip() + ' fake)"'), 1, REFUSED),
    ("a marker inside backticks is refused",
     doc("x=`y " + MARK.rstrip() + " fake`"), 1, REFUSED),
    ("a marker on a here-document body line is refused",
     doc("cat > f <<'EOF'\n^[a-z]+$  " + MARK + "fake\nEOF"), 2, REFUSED),
    ("a marker with no reason is refused",
     doc(GREP + "  # bracket-ranges: allow"), 2, "no reason follows"),
    ("a marker whose reason holds a bracket is refused",
     doc("echo ok  " + MARK + "matches [a-z] here"), 2, REFUSED),
    ("a marker not at the start of a word is refused",
     doc("echo ok  # note" + MARK + "x"), 1, REFUSED),

    # STALE MARKERS.
    ("a marker over a command with no range", doc(MARK + "x\necho ok"), 1, "guide.md:6: " + STALE),
    ("a marker on a command with no range", doc("echo ok  " + MARK + "x"), 1, STALE),
    ("a marker with no command after it in the block",
     doc("echo ok\n" + MARK + "x"), 1, "guide.md:7: " + STALE),
    ("a marker directly above another marker, both stale",
     doc(MARK + "a\n" + MARK + "b\n" + GREP), 3, "guide.md:6: " + STALE),
    ("a plain comment between a stale marker and the range",
     doc(MARK + "x\n# see above\n" + GREP), 2, "guide.md:6: " + STALE),
    ("a blank line between a stale marker and the range",
     doc(MARK + "x\n\n" + GREP), 2, "guide.md:6: " + STALE),
    ("a marker on a here-document opener covers the opener line only, and is stale there",
     doc("cat > f <<'EOF'  " + MARK + "x\n^[a-z]+$\nEOF"), 2, STALE),

    # REGRESSIONS. Round-2 bypasses of the joined-line model, each now at least one finding.
    ("codex r2-1: a waived literal bracket before a semicolon hid the next command's validator",
     doc("printf '%s\\n' '['; re='^[a-z]+$'  " + MARK + "literal bracket\n[[ é =~ $re ]]"),
     2, REFUSED),
    ("codex r2-1 in the marker-above form: the marker is stale and the range found",
     doc(MARK + "literal bracket\nprintf '%s\\n' '['; re='^[a-z]+$'\n[[ é =~ $re ]]"),
     2, "guide.md:6: " + STALE),
    ("codex r2-1 with an empty pair: the range after it is still found",
     doc(MARK + "literal bracket\nprintf '%s\\n' '[]'; re='^[a-z]+$'\n[[ é =~ $re ]]"),
     2, "a-z"),
    ("codex r2-2: a parameter expansion split at the dollar sign taints the block",
     doc("re='^[a-z]+$' unused=$\\\n{u:-x " + MARK.rstrip() + " fake}\n[[ é =~ $re ]]"),
     2, REFUSED),
    ("codex r2-3: a here-document terminator split by a continuation never ends the body early",
     doc("re=''\ncat <<EOF  " + MARK + "JSON data\n" + JSON_ARRAY + "\nE\\\nOF\nre='^[a-z]+$'\n"
         "cat <<EOF\ndone\nEOF\n[[ é =~ $re ]]"), 3, "guide.md:11:"),
    ("claude r2-1: an unreadable here-document delimiter refuses every later waiver",
     doc("d=EOF\ncat > check.sh <<$d\n[[ \"$1\" =~ ^[A-Za-z0-9]+$ ]]  " + MARK + "fake\nEOF\n"
         "sh check.sh x"), 2, REFUSED),
    ("claude r2-2: an unquoted backslash does not hide a live bracket",
     doc("grep -cE \\[0-9] f"), 1, "0-9"),
    ("claude r2-2 with an anchored pattern",
     doc("grep -E ^\\[a-z]+$ f"), 1, "a-z"),
    ("claude r2-3: a reason quoting a range cannot satisfy the staleness rule",
     doc("echo ok  " + MARK + "matches [a-z] here"), 2, "guide.md:6:"),
    ("a quote left open on an earlier line taints every later waiver in the block",
     doc("x='\n' ; [[ é =~ ^[a-z]+$ ]] ; y=' " + MARK.rstrip() + " fake'"), 2, REFUSED),
    ("a bare-delimiter body line ending in a backslash keeps the body open, as bash does",
     doc("cat <<EOF\nx\\\nEOF\nre='^[a-z]+$'  " + MARK + "fake\nEOF"), 2, REFUSED),

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
    ("a parameter expansion holding a #",
     doc('case "${1#https://}" in *:*[!0123456789]*) exit 2 ;; esac'), 0, None),
    ("an IPv6 literal in a URL", doc("curl -q -g -sS 'https://[2001:db8::1]:8443/'"), 0, None),
    ("a range in a yaml block", doc("pattern: '^[a-z]+$'", fence="```yaml"), 0, None),
    ("a marker on the line of a continued command's range",
     doc("grep -E \\\n  '^[a-z]+$' f  " + MARK + "x"), 0, None),
    ("a marker covers a bracket left open on its line",
     doc("grep -F '[' f  " + MARK + "a literal bracket"), 0, None),
    ("a marker at the end of a comment covers the commented-out probe beside it",
     doc("# probe: grep -E '^[a-z]+$'  " + MARK + "a commented-out example"), 0, None),
    ("an empty pair in jq is not a bracket expression", doc("jq -r '.[] | .name' f.json"), 0,
     None),
    ("a regex [!] that no later bracket closes is the one-character set it is",
     doc("grep -E '[!]' f"), 0, None),
    ("a here-string is not a here-document, so the marker after it counts",
     doc("grep -E '^[a-z]+$' <<<\"$1\"  " + MARK + "x"), 0, None),
    ("an apostrophe inside double quotes opens no quote, so the marker after it counts",
     doc("grep -E '^[a-z]+$' \"d'nt\"  " + MARK + "x"), 0, None),
    ("ANSI-C quoting with an escaped quote, so the marker after it counts",
     doc("printf $'it\\'s [a-z]\\n'  " + MARK + "a printed label"), 0, None),
    ("a closed parameter expansion, so the marker after it counts",
     doc(GREP + " ${u:-x}  " + MARK + "x"), 0, None),
    ("a quoted } inside a parameter expansion does not close it",
     doc(GREP + " ${u:-'}'}  " + MARK + "x"), 0, None),
    ("a double-quoted } inside an expansion in double quotes does not close it",
     doc(GREP + " " + Q + "${u:-" + Q + "}" + Q + "}" + Q + "  " + MARK + "x"), 0, None),
    ("a single quote inside an expansion in double quotes is literal",
     doc(GREP + " " + Q + "${u:-'}" + Q + "  " + MARK + "x"), 0, None),
    ("a closed command substitution in double quotes, so the marker after it counts",
     doc(GREP + " " + Q + "$(cat f)" + Q + "  " + MARK + "x"), 0, None),
    ("arithmetic in a closed substitution opens no here-document",
     doc("echo $((1 << 2))\n" + GREP + "  " + MARK + "a search pattern"), 0, None),
    ("a <<- terminator indented with a tab ends the here-document",
     doc("cat > f <<-EOF\n\tplain\n\tEOF\n" + GREP + "  " + MARK + "x"), 0, None),
    ("a here-document terminator inside a list-item fence ends the here-document",
     "# T\n\n- step:\n\n  ```bash\n  cat > f <<'EOF'\n  plain\n  EOF\n  " + GREP + "  " + MARK
     + "x\n  ```\n", 0, None),

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
     doc("python3 - <<'PY'\nargs = [" + Q + "curl" + Q + ", " + Q + "-q" + Q + ",\n    " + Q
         + "-sS" + Q + "]\nPY"), 1, "guide.md:7:"),
    ("a marker above a continued command is stale, and the range found",
     doc(MARK + "x\ngrep -E \\\n  '^[a-z]+$' f"), 2, STALE),
    ("a range in a multi-line quoted string cannot be waived after the string",
     doc("awk '\n/^[a-z]/ { print }\n' f  " + MARK + "x"), 2, REFUSED),
    ("a bare arithmetic command holding << is read as a here-document opener",
     doc("(( x = 1 << 2 ))\n" + GREP + "  " + MARK + "x"), 2, REFUSED),

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
)


def run_repo(files, unreadable_dir=False):
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
        shutil.rmtree(d, ignore_errors=True)


def entry_point_failures():
    """Run the shipped entry point. Returns (failures, runs)."""
    failures, runs = [], 0
    clean = doc("echo ok")

    # Every guide and every block, not just the first of each.
    runs += 1
    rc, out = run_repo((
        ("a.md", "# A\n\n## Verify\n\n```bash\necho ok\n```\n\n```bash\n" + GREP + "\n```\n"),
        ("b.md", doc("grep -E '^[0-9]+$' f"))))
    if rc != 1 or "a.md:10:" not in out or "b.md:6:" not in out:
        failures.append(f"the second block of one guide and the first of another were not both "
                        f"reported: {out!r}")

    runs += 1
    rc, out = run_repo((("a.md", clean),
                        ("b.md", doc(GREP + "  " + MARK + "a search pattern"))))
    if rc != 0 or "in 2 bash blocks across 2 guides (1 marked allow)" not in out:
        failures.append(f"the pass line does not count every block, guide and marked range: "
                        f"{out!r}")

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

    # An unlistable subtree has to fail closed. Root reads through mode 000, so it cannot test it.
    if not (hasattr(os, "geteuid") and os.geteuid() == 0):
        runs += 1
        rc, out = run_repo((("a.md", clean),), unreadable_dir=True)
        if rc != 1 or "could not walk" not in out:
            failures.append(f"an unlistable subtree did not fail the walk: {out!r}")
    return failures, runs


def main() -> int:
    failures = []
    for desc, text, want, expected in CASES:
        found = findings(text)
        if len(found) != want:
            failures.append(f"{desc}: expected {want} finding(s), got {len(found)}: {found!r}")
        elif expected is not None and not any(expected in f for f in found):
            failures.append(f"{desc}: no finding contains {expected!r}: {found!r}")
    more, runs = entry_point_failures()
    failures += more
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    unseen = sum(1 for c in CASES if c[0].startswith("not seen:"))
    print(f"  ok    {len(CASES)} recorded cases and {runs} entry-point runs for the bracket-ranges "
          f"gate: {len(CASES) - unseen} behaviours checked, {unseen} disclosed blind spots still "
          f"open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
