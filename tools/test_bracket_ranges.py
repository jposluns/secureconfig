#!/usr/bin/env python3
r"""Cases for check_bracket_ranges.py, including what it deliberately does not catch.

Most cases hand one guide to the gate's own scan_path and assert the exact number of findings
and a substring of one, so a stale marker and an unmarked range are counted apart rather than
merged into "it failed". The ENTRY POINT group builds throwaway repositories and runs the shipped
file, for what only the entry point does: choosing which files to read, the pass line, the exit
status, and failing closed on an unreadable guide, an unlistable directory, or a corpus with no
bash block in it.

Several cases exist because a simpler scanner gets them wrong in a way that matters. The `#` in
`${#1}` read as a comment hides the range after it. An apostrophe inside double quotes read as a
quote hides the marker after it. A here-string read as a here-document turns the rest of the
block into data, where no marker counts. A here-document terminator after `<<-`, or inside a
list-item fence, left unrecognized does the same. A set split by a backslash-newline, which bash
joins outside single quotes, is seen only once the lines are joined. A marker read as covering
every command on its line covers `a` in `a; b  # bracket-ranges: allow x`, and a `#` inside a
`${...}` expansion read as a comment fakes a marker.

The KNOWN LIMITS group asserts the gate's current answer on inputs it is known to get wrong, as
tools/test_shell_blocks.py does, so a change that closes one fails here and the gate's docstring
is updated with it.
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
    ("a range on a continuation line",
     doc("grep -E \\\n  '^[a-z]+$' names.txt"), 1, "guide.md:7:"),
    ("the # in ${#1} starts no comment, so the range after it is still read",
     doc('[ "${#1}" -eq 32 ] && case "$1" in *[!0-9a-f]*) exit 2 ;; esac'), 1, "[!0-9a-f]"),
    ("two ranges in one command are two findings",
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

    # CONTINUATION LINES, joined as bash joins them before the set is read.
    ("a set split by a backslash-newline inside double quotes, in grep",
     doc('grep -E "^[A-\\\nZa-z]+$" names.txt'), 1,
     "guide.md:6: [A-Za-z] holds the ranges A-Z, a-z (joined from lines 6-7)"),
    ("a set split by a backslash-newline in an unquoted word",
     doc("grep -E ^[A-\\\nZa-z]+$ names.txt"), 1, "[A-Za-z] holds the ranges A-Z, a-z (joined"),
    ("a set split by a backslash-newline in sed", doc('sed -E "s/[^a-\\\nz]//g" names.txt'), 1,
     "[^a-z] holds the range a-z (joined"),
    ("a set split by a backslash-newline in awk", doc('awk "/^[0-\\\n9]+$/" ports.txt'), 1,
     "[0-9] holds the range 0-9 (joined"),
    ("a set split by a backslash-newline in a case pattern",
     doc('case "$1" in *[!A-Za-\\\nz0-9.-]*) exit 2 ;; esac'), 1, "[!A-Za-z0-9.-] holds"),
    ("a set split by a backslash-newline in [[ =~ ]]",
     doc('[[ "$t" =~ ^[0-9a-\\\nf]+$ ]] || exit 2'), 1, "[0-9a-f] holds the ranges 0-9, a-f"),
    ("the surrealdb JWT check split after A-Za-, the round-1 reproduction",
     doc('  [[ "$probe_jwt" =~ ^[A-Za-\\\nz0-9_.-]+$ ]] || { echo ' + "'missing or malformed "
         "JWT; not probing'; exit 2; }"), 1,
     "guide.md:6: [A-Za-z0-9_.-] holds the ranges A-Z, a-z, 0-9 (joined from lines 6-7)"),
    ("a set split across three lines", doc('grep -E "[A-\\\nZa-\\\nz]" f'), 1,
     "(joined from lines 6-8)"),
    ("a set split by a backslash-newline in a script written through a quoted here-document",
     doc("cat > check.sh <<'EOF'\ngrep -qE \"^[a-\\\nz]+$\" name.txt\nEOF"), 1,
     "guide.md:7: [a-z] holds the range a-z (joined from lines 7-8)"),
    ("a set split by a backslash-newline in a bare here-document, which bash joins",
     doc("cat > f <<EOF\n^[0-\\\n9]+$\nEOF"), 1, "guide.md:7: [0-9] holds the range 0-9 (joined"),
    ("a backslash-newline in single quotes stays, and the open set fails closed",
     doc("grep -E '^[A-\\\nZa-z]+$' names.txt"), 1, "guide.md:6: [A-\\"),
    ("a backslash-newline in $'...' stays, and the open set fails closed",
     doc("grep -E $'^[A-\\\nZa-z]+$' names.txt"), 1, "nothing closes before the end"),
    ("a backslash-newline in single quotes in a here-document script fails closed",
     doc("cat > check.sh <<'EOF'\ngrep -qE '^[a-\\\nz]+$' name.txt\nEOF"), 1, "guide.md:7:"),
    ("a set nothing closes before the end of its command", doc("grep -E '^[a-z' f"), 1,
     "[a-z' f opens a bracket expression that nothing closes"),

    # A MARKER COVERS ONE COMMAND OF A LIST OR PIPELINE.
    ("a marker after a ; covers the second command, not the first",
     doc("grep -E '^[a-z]+$' a; grep -E '^[0-9]+$' b  " + MARK + "x"), 1, "guide.md:6: [a-z]"),
    ("a marker above && covers the first command, not the second",
     doc(MARK + "x\ngrep -E '^[a-z]+$' a && grep -E '^[0-9]+$' b"), 1, "guide.md:7: [0-9]"),
    ("a marker after || covers the second command, not the first",
     doc("grep -E '^[a-z]+$' a || grep -E '^[0-9]+$' b  " + MARK + "x"), 1, "[a-z]"),
    ("a marker after a lone & covers the second command, not the first",
     doc("grep -E '^[a-z]+$' a & grep -E '^[0-9]+$' b  " + MARK + "x"), 1, "[a-z]"),
    ("a marker at the end of a pipeline covers its last command, and is stale there",
     doc(GREP + " | head -n 1  " + MARK + "x"), 2, "guide.md:6: stale"),

    # MARKERS INSIDE ${...}, WHICH ARE NOT COMMENTS.
    ("a marker inside a ${...} default is expansion text, not a comment",
     doc(GREP + " ${u:-x # bracket-ranges: allow fake}"), 1, "no bracket-ranges marker"),
    ("a marker inside a nested ${...} is expansion text, not a comment",
     doc(GREP + " ${u:-${v:-x} # bracket-ranges: allow fake}"), 1, None),

    # MARKERS THAT DO NOT COUNT, AND STALE MARKERS.
    ("a marker with no reason",
     doc(GREP + "  # bracket-ranges: allow"), 1, "no bracket-ranges marker covers it"),
    ("the marker text inside a quoted string",
     doc("grep -E '^[a-z]+$ # bracket-ranges: allow fake' f"), 1, None),
    ("a marker inside a here-document body, which is data written to a file",
     doc("cat > f <<'EOF'\n" + MARK + "x\n^[a-z]+$\nEOF"), 1, "guide.md:8:"),
    ("a marker at the end of one command does not reach the next",
     doc("grep -E '^[a-z]+$' a  " + MARK + "x\ngrep -E '^[0-9]+$' b"), 1, "guide.md:7:"),
    ("a plain comment between the marker and the command",
     doc(MARK + "x\n# see above\n" + GREP), 2, "guide.md:6: stale"),
    ("a blank line between the marker and the command",
     doc(MARK + "x\n\n" + GREP), 2, "guide.md:6: stale"),
    ("a marker over a command with no range", doc(MARK + "x\necho ok"), 1, "guide.md:6: stale"),
    ("a marker on a command with no range", doc("echo ok  " + MARK + "x"), 1, "guide.md:6: stale"),
    ("a marker with no command after it in the block",
     doc("echo ok\n" + MARK + "x"), 1, "no command follows"),
    ("a marker directly above another marker",
     doc(MARK + "a\n" + MARK + "b\n" + GREP), 1, "guide.md:6: stale"),

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
    ("an escaped bracket", doc("grep -E '\\[a-z\\]' f"), 0, None),
    ("an IPv6 literal in a URL", doc("curl -q -g -sS 'https://[2001:db8::1]:8443/'"), 0, None),
    ("a range in a yaml block", doc("pattern: '^[a-z]+$'", fence="```yaml"), 0, None),
    ("a marker at the end of the command", doc(GREP + "  " + MARK + "a search pattern"), 0, None),
    ("a marker on the line above", doc(MARK + "a search pattern\n" + GREP), 0, None),
    ("a marker at the end of a continued command covers its continuation line",
     doc("grep -E \\\n  '^[a-z]+$' f  " + MARK + "x"), 0, None),
    ("a marker above a continued command", doc(MARK + "x\ngrep -E \\\n  '^[a-z]+$' f"), 0, None),
    ("a marker on a here-document opener covers the body",
     doc("cat > f <<'EOF'  " + MARK + "x\n^[a-z]+$\nEOF"), 0, None),
    ("a marker on a line opening two here-documents covers both bodies",
     doc("cat /dev/fd/3 /dev/fd/4 3<<'A' 4<<'B'  " + MARK + "x\n[a-z]\nA\n[0-9]\nB"), 0, None),
    ("a here-string is not a here-document, so the marker after it counts",
     doc("grep -E '^[a-z]+$' <<<\"$1\"  " + MARK + "x"), 0, None),
    ("a marker after a quoted string that spans lines",
     doc("awk '\n/^[a-z]/ { print }\n' f  " + MARK + "x"), 0, None),
    ("an apostrophe inside double quotes opens no quote, so the marker after it counts",
     doc("echo \"don't\"; " + GREP + "  " + MARK + "x"), 0, None),
    ("ANSI-C quoting with an escaped quote, so the marker after it counts",
     doc("printf $'it\\'s\\n'; " + GREP + "  " + MARK + "x"), 0, None),
    ("a <<- terminator indented with a tab ends the here-document",
     doc("cat > f <<-EOF\n\tplain\n\tEOF\n" + GREP + "  " + MARK + "x"), 0, None),
    ("a here-document terminator inside a list-item fence ends the here-document",
     "# T\n\n- step:\n\n  ```bash\n  cat > f <<'EOF'\n  plain\n  EOF\n  " + GREP + "  " + MARK
     + "x\n  ```\n", 0, None),

    ("a spelled-out set split by a backslash-newline",
     doc('grep -E "^[0123456789abc\\\ndef]+$" f'), 0, None),
    ("a marker covers a bracket left open", doc("grep -F '[' f  " + MARK + "a literal bracket"),
     0, None),
    ("an empty pair in jq is not a bracket expression", doc("jq -r '.[] | .name' f.json"), 0, None),
    ("a regex [!] that no later bracket closes is the one-character set it is",
     doc("grep -E '[!]' f"), 0, None),
    ("a list opened on one line of a here-document and closed on a later one is data",
     doc("python3 - <<'PY'\nargs = [" + Q + "curl" + Q + ", " + Q + "-q" + Q + ",\n    " + Q
         + "-sS" + Q + "]\nPY"), 0, None),
    ("a redirection's & ends no command, so the marker covers the range before it",
     doc(GREP + " 2>&1 >/dev/null &>/dev/null  " + MARK + "x"), 0, None),
    ("a marker after a trailing ; covers the command before it", doc(GREP + ";  " + MARK + "x"),
     0, None),
    ("a ; inside quotes ends no command", doc("grep -E '^[a-z]+;$' f  " + MARK + "x"), 0, None),
    ("a marker after a closed ${...} counts", doc(GREP + " ${u:-x}  " + MARK + "x"), 0, None),
    ("a quoted } inside ${...} does not close it, so the marker after it counts",
     doc(GREP + " ${u:-'}'}  " + MARK + "x"), 0, None),
    ("a double-quoted } inside ${...} in double quotes does not close it",
     doc(GREP + " " + Q + "${u:-" + Q + "}" + Q + "}" + Q + "  " + MARK + "x"), 0, None),
    ("a single quote inside ${...} in double quotes is literal, so the marker after it counts",
     doc(GREP + " " + Q + "${u:-'}" + Q + "  " + MARK + "x"), 0, None),

    # FENCES AND LINES.
    ("a U+2028 inside a block does not shift the line number",
     doc("printf '%s' 'x" + chr(0x2028) + "y'\n" + GREP), 1, "guide.md:7:"),
    ("a block the file never closed", "# T\n\n```bash\n" + GREP + "\n", 1, "guide.md:4:"),
)
CASES += tuple(("a " + f + " fence", doc(GREP, fence=f), 1, None)
               for f in ("````bash", "~~~bash", "```Bash", "```bash {.numberLines}", "```bash "))
CASES += (
    # KNOWN LIMITS. Each asserts the CURRENT answer, so a change that closes one is loud.
    ("known limit: tr takes a range with no brackets",
     doc("tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32"), 0, None),
    ("known limit: a POSIX class is locale dependent and not flagged",
     doc('[[ "$1" =~ ^[[:alnum:]]+$ ]] || exit 2'), 0, None),
    ("known limit: \\w is locale dependent and not flagged",
     doc("grep -qE '^\\w+$' f"), 0, None),
    ("known limit: a << in arithmetic opens a here-document, so a later marker is ignored",
     doc("echo $((1 << 2))\n" + GREP + "  " + MARK + "x"), 1, None),
    ("known limit: a sh, shell or zsh fence is not a bash fence and is not read",
     doc(GREP, fence="```sh"), 0, None),
    ("known limit: a set spanning a real newline inside quotes is not read across it",
     doc("re='^[A-Z\na-z]+$'"), 0, None),
    ("known limit: an operator inside [[ ]] ends a command, so a marker covers less",
     doc('[[ "$1" =~ ^[a-z]+$ || -z "$1" ]]  ' + MARK + "x"), 2, "guide.md:6: stale"),
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
    rc, out = run_repo((("a.md", clean), ("b.md", doc(MARK + "a search pattern\n" + GREP))))
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
    limits = sum(1 for c in CASES if c[0].startswith("known limit:"))
    print(f"  ok    {len(CASES)} recorded cases and {runs} entry-point runs for the bracket-ranges "
          f"gate: {len(CASES) - limits} behaviours checked, {limits} disclosed limits still open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
