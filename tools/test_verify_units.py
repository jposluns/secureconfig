#!/usr/bin/env python3
"""Recorded unit and dependency cases; all CLI writes stay in temporary roots."""
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import os
from pathlib import Path
import tempfile
import subprocess
from unittest.mock import patch

import check_verify_marking as gate

MARK = "REASONED: vendor evidence"
PREFIX = "# Guide\n\n## Verify\n\n"


def run_cases(check):
    parser = gate.gate_parser()
    suite = Path(gate.__file__).with_name("run_all_checks.sh").read_text()
    block = suite[suite.index('echo "== Verify fences,'):suite.index('echo "== every port')]
    adapter = r'''fail=0
bad() { printf '  FAIL  %s\n' "$1"; fail=1; }
python3() {
  case "$3" in
    tools/test_verify_marking.py) printf '%s\n' "$CASE_SELF"; return "$CASE_SELF_RC" ;;
    tools/check_verify_marking.py) printf '%s\n' "$CASE_GATE"; return "$CASE_GATE_RC" ;;
    *) return 99 ;;
  esac
}
'''
    good_self = "  ok    1 Verify-marking fixture cases"
    good_gate = "  COUNTS  fence: 1 marked, 0 retained\n  ok    Verify marking: 1 marked"
    for label, self_out, self_rc, gate_out, gate_rc, expected, diagnostic in (
        ("clean", good_self, 0, good_gate, 0, 0, good_gate),
        ("self silent", "", 0, good_gate, 0, 1, "self-test exited 0 without a clean result"),
        ("self printed failure", good_self + "\n  FAIL  injected", 0, good_gate, 0, 1,
         "self-test exited 0 without a clean result"),
        ("self exit", good_self, 1, good_gate, 0, 1, "self-test failed"),
        ("gate silent", good_self, 0, "", 0, 1, "gate exited 0 without a clean result"),
        ("gate printed failure", good_self, 0, good_gate + "\n  FAIL  injected", 0, 1,
         "gate exited 0 without a clean result"),
        ("gate exit", good_self, 0, good_gate, 1, 1, "Verify-marking gate failed"),
    ):
        env = dict(os.environ, CI="", CASE_SELF=self_out, CASE_SELF_RC=str(self_rc),
                   CASE_GATE=gate_out, CASE_GATE_RC=str(gate_rc))
        result = subprocess.run(["bash", "-c", adapter + block + '\nexit "$fail"'],
                                env=env, capture_output=True, text=True)
        check("suite contract " + label, result.returncode == expected
              and diagnostic in result.stdout)
    with tempfile.TemporaryDirectory(prefix="verify-units-") as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        lock = Path(gate.__file__).with_name("requirements-gates.txt").read_bytes()
        (root / "tools/requirements-gates.txt").write_bytes(lock)
        (root / "tools/version_basis_guides.txt").write_text("guide.md\n")
        guide = root / "guide.md"
        baseline = root / gate.BASELINE
        baseline.write_text("")

        def cli(*args, ci=""):
            output = StringIO()
            with patch.object(gate, "__file__", str(root / "tools/check_verify_marking.py")), \
                    patch.dict(os.environ, {"CI": ci}), \
                    redirect_stdout(output), redirect_stderr(output):
                rc = gate.main(list(args))
            return rc, output.getvalue()

        # Explicit dependency fault injection, independent of the installed parser.
        # Real 4.2.0/3.0.0/absent installations are also exercised by the suite.
        guide.write_text(PREFIX + "unmarked prose\n\n```sh\n# " + MARK + "\necho ok\n```\n")
        for label, present, versions, reason in (
            ("missing", None, {}, "parser absent"),
            ("mismatch", object(), {"markdown-it-py": "3.0.0", "mdurl": "0.1.2"},
             "markdown-it-py installed 3.0.0, pinned 4.2.0"),
            ("closure mismatch", object(), {"markdown-it-py": "4.2.0", "mdurl": "0.0.0"},
             "mdurl installed 0.0.0, pinned 0.1.2"),
        ):
            with patch("importlib.util.find_spec", return_value=present), \
                    patch("importlib.metadata.version", side_effect=versions.__getitem__):
                check(label + " API unavailable", gate.gate_parser() is None)
                rc, out = cli("--strict")
                expected_skip = ("  SKIP  Verify list-item/table-row/prose checks: " + reason
                                 + "; install tools/requirements-gates.txt (fence checks still run)")
                check(label + " one advisory and fence count", rc == 0
                      and out.splitlines().count(expected_skip) == 1
                      and out.count("  SKIP  ") == 1
                      and "  COUNTS  fence: 1 marked, 0 retained\n" in out
                      and out.count("  COUNTS  ") == 1 and "0 findings" in out)
                for args, ci in ((('--strict',), 'true'),
                                 (('--strict', '--require-parser'), ''),
                                 (('--assert-parser',), '')):
                    rc, out = cli(*args, ci=ci)
                    check(label + " required failure " + str(args) + ci, rc == 1
                          and "  FAIL  VERIFY-MARK " + reason in out
                          and "SKIP" not in out and "COUNTS" not in out)
                before = baseline.read_bytes()
                rc, out = cli("--write-baseline")
                check(label + " seed refusal", rc == 1
                      and "seeding requires the pinned parser: " + reason in out
                      and "COUNTS" not in out and baseline.read_bytes() == before)
                guide.write_text(PREFIX + "```sh\necho unmarked\n```\n")
                rc, out = cli("--strict")
                check(label + " fence ratchet remains active", rc == 1
                      and "new/changed/excess fence" in out
                      and "  COUNTS  fence: 0 marked, 0 retained\n" in out
                      and out.count("  COUNTS  ") == 1)
                for context in ("REASONED: evidence\n\n",
                                "### Example (REASONED: evidence)\n\n"):
                    units, errors = gate.scan_guide(PREFIX + context
                                                    + "```sh\necho ok\n```\n")
                    check(label + " inline context needs parser " + context,
                          units and not units[0][2] and any(
                              "inline declarations require the pinned parser" in e
                              for e in errors))
                guide.write_text(PREFIX + "unmarked prose\n\n```sh\n# " + MARK + "\necho ok\n```\n")

        if parser is None:
            return

        def scan(name, body, counts, marked=0, diagnostic="", *, full=False, use_parser=None):
            units, errors = gate.scan_units(body if full else PREFIX + body,
                                           parser=use_parser or parser)
            actual = Counter(u[1] for u in units)
            check(name + " units", tuple(actual[k] for k in gate.KINDS) == counts)
            check(name + " marks", sum(bool(u[3]) for u in units) == marked)
            check(name + " diagnostic", any(diagnostic in e for e in errors)
                  if diagnostic else not errors)
            return units

        scan("mixed tight loose lazy tabs and dedent",
             "1. first\nlazy line\n\n   second paragraph\n\n   - child\n\n"
             "2. next\n\n-\ttab item\n\noutside\n", (0, 4, 0, 1))
        scan("same line fence", "- ```sh\n  # " + MARK + "\n  echo ok\n  ```\n",
             (1, 1, 0, 0), 1)
        for inline in ("`REASONED: fake`", "``a ` REASONED: fake``", "`a\nb`",
                       r"\`REASONED: fake`", "[REASONED: fake](https://example.com)"):
            scan("inline " + inline, inline + "\n", (0, 0, 0, 1))
        for row in ("| A | B |\n| :--- | ---: |\n| x | y |\n",
                    "A | B\n--- | ---\nx | y\n",
                    "| A | B |\n| --- | --- |\n| `x\\|y` | |\n"):
            scan("table " + row, row, (0, 0, 1, 0))
        table = "| A | B |\n| --- | --- |\n| x | y |\n"
        scan("two tables and following paragraph", table + "\ncontinued\n\n" + table,
             (0, 0, 2, 1))
        scan("nested table", "- parent\n\n" + "".join("  " + s + "\n" for s in table.splitlines()),
             (0, 1, 1, 0))
        scan("missing delimiter is prose", "| A | B |\n| x | y |\n", (0, 0, 0, 1))
        for row in ("| x |\n", "| x | y | z |\n"):
            scan("ragged " + row, "| A | B |\n| --- | --- |\n" + row,
                 (0, 0, 0, 0), diagnostic="ragged table row")
        scan("wrap hard break blank", "wrapped\nline  \nhard\n\nseparate\n", (0, 0, 0, 2))
        scan("attachment boundaries", MARK + "\n\n```sh\necho ok\n```\n\n"
             "plain\n\n- item\n\n" + table, (1, 1, 1, 2), 2)
        for spelling in ("REASONED:", "reasoned:", "DEMONSTRATED:", "demonstrated:",
                         "**REASONED:**", "__REASONED:__", "**REASONED**:",
                         "__REASONED__:", "**REASONED: evidence**", "__REASONED: evidence__"):
            mark = spelling + " evidence"
            scan("spelling " + spelling, mark + "\n\n- " + mark + "\n\n"
                 "| A | B |\n| --- | --- |\n| x | " + mark + " |\n", (0, 1, 1, 1), 3)
        scan("empty provenance", "REASONED:\n", (0, 0, 0, 0),
             diagnostic="needs scope and provenance")
        scan("malformed emphasis", "*REASONED:* evidence\n", (0, 0, 0, 0),
             diagnostic="malformed declaration emphasis")
        scan("conflicting cells", "| A | B |\n| --- | --- |\n"
             "| REASONED: source | DEMONSTRATED: run |\n", (0, 0, 0, 0),
             diagnostic="conflicting declarations")
        scan("parent does not mark child or row", "- " + MARK + "\n  - child\n\n"
             + "".join("  " + s + "\n" for s in table.splitlines()), (0, 2, 1, 0), 1)
        scan("heading stops at child", "## Verify (" + MARK + ")\n\n- marked\n\n"
             "### Child\n\nplain\n\n### Next\n\nplain too\n", (0, 1, 0, 2), 1, full=True)
        for title in ("Verify", "Verification checklist", "Quick checks", "3. Verify"):
            scan("alias and roots " + title, "## " + title + "\n\none\n\n"
                 "## Setup\n\nignored\n\n## Verify\n\ntwo\n", (0, 0, 0, 2), full=True)
        scan("malformed suffix", "## Verify (REASONED:)\n\nplain\n", (0, 0, 0, 0),
             diagnostic="needs scope and provenance", full=True)
        scan("fake heading in code", "```text\n## Setup\n```\n\nplain\n", (1, 0, 0, 1))
        scan("metadata boundary attack", "---\ntitle: fake\n---\n\n" + PREFIX + "plain\n",
             (0, 0, 0, 0), diagnostic="[unsupported-container]", full=True)
        scan("summary boundary attack", "<!-- version-basis:start -->\n## Setup\n"
             "<!-- version-basis:end -->\n", (0, 0, 0, 0), diagnostic="HTML comment outside")
        for name, body, diagnostic in (
            ("quote", "> text\n", "blockquote_open"),
            ("compact", "- - text\n", "compact list"),
            ("empty", "-\n", "empty item"),
            ("indented", "    text\n", "code_block"),
            ("setext", "text\n====\n", "Setext heading"),
            ("HTML", "<div>text</div>\n", "html_block"),
            ("comment", "<!-- text -->\n", "HTML comment outside"),
            ("reference", "[x]: https://example.com\n", "uncovered Verify source lines"),
        ):
            scan(name, body, (0, 0, 0, 0), diagnostic=diagnostic)

        class AlteredParser:
            def __init__(self, change):
                self.change = change

            def parse(self, text, env):
                tokens = parser.parse(text, env)
                self.change(tokens)
                return tokens

        for attr, value, diagnostic in (("type", "future_open", "unrecognized block token future_open"),
                                        ("map", None, "missing or invalid source map for paragraph_open")):
            def change(tokens, attr=attr, value=value):
                token = next(t for t in tokens if t.type == "paragraph_open")
                setattr(token, attr, value)
            scan("parser contract " + attr, "plain\n", (0, 0, 0, 0), diagnostic=diagnostic,
                 use_parser=AlteredParser(change))

        def unknown_inline(tokens):
            inline = next(t for t in tokens if t.type == "inline" and t.content == "plain")
            inline.children[0].type = "future_inline"

        scan("unknown inline fails closed", "plain\n", (0, 0, 0, 0),
             diagnostic="unsupported inline token future_inline",
             use_parser=AlteredParser(unknown_inline))

        # Declarations must survive inline context checks at every attachment site.
        def rejected(name, body, kinds, diagnostic=None):
            guide.write_text(body)
            baseline.write_text("")
            rc, out = cli("--strict")
            check(name + " exit", rc == 1)
            for kind in kinds:
                check(name + " " + kind + " diagnostic",
                      (diagnostic or "new/changed/excess " + kind) in out)
            if diagnostic is None:
                units, errors = gate.scan_units(body, parser=parser)
                check(name + " unmarked", not errors and units
                      and all(u[3] is None for u in units))

        fence = "```sh\necho ok\n```\n"
        for heading in ("`Example: REASONED: vendor evidence`",
                        "[Example: REASONED: vendor evidence](https://example.com)",
                        "[Example](REASONED:vendor)"):
            rejected("reported heading " + heading,
                     PREFIX + "### " + heading + "\n\nUnmarked check.\n\n"
                     + fence + "\n- Unmarked item.\n\n" + table, gate.KINDS)

        for status in ("REASONED", "DEMONSTRATED"):
            marker = status + ": vendor evidence"
            for context, opaque in (
                ("code", "`" + marker + "`"),
                ("link text", "[" + marker + "](https://example.com)"),
                ("destination", "[Example](" + status + ":vendor)"),
                ("image", "![" + marker + "](https://example.com/image.png)"),
                ("autolink", "<" + status + ":vendor>"),
                ("HTML text", "<span>" + marker + "</span>"),
                ("HTML attribute", '<span title="' + marker + '">value</span>'),
            ):
                for site, body, kind in (
                    ("heading", "### Example: " + opaque + "\n\nCheck.\n", "prose"),
                    ("paragraph", opaque + "\n", "prose"),
                    ("item", "- " + opaque + "\n", "list-item"),
                    ("cell", "| A | B |\n| --- | --- |\n| check | " + opaque + " |\n",
                     "table-row"),
                    ("before fence", opaque + "\n\n" + fence, "fence"),
                    ("after fence", fence + "\n" + opaque + "\n", "fence"),
                ):
                    rejected(status + " " + site + " " + context, PREFIX + body, (kind,),
                             "unsupported inline token html_inline"
                             if context.startswith("HTML") else None)
            # Opaque provenance is allowed when the marker itself is plain text.
            for evidence in ("`vendor evidence`", "[vendor evidence](https://example.com)"):
                mark = status + ": " + evidence
                scan("plain marker " + mark, mark + "\n\n- " + mark + "\n\n"
                     "| A | B |\n| --- | --- |\n| x | " + mark + " |\n\n"
                     + fence, (1, 1, 1, 1), 3)

        rejected("reference link heading",
                 "[r]: https://example.com\n\n" + PREFIX
                 + "### [Example: REASONED: vendor evidence][r]\n\n" + fence,
                 ("fence",))
        rejected("reference link paragraph",
                 "[r]: https://example.com\n\n" + PREFIX
                 + "[REASONED: vendor evidence][r]\n\n" + fence,
                 ("prose", "fence"))

        for prefix, indent in (("- ", "  "), ("1. ", "   "), ("  + ", "    ")):
            body = "## Verify (" + MARK + ")\n\n" + prefix + "| A | B |\n"
            body += indent + "| --- | --- |\n" + indent + "| Check endpoint | Expect refusal |\n"
            guide.write_text(body)
            baseline.write_text("")
            rc, out = cli("--strict")
            check("first-line table " + prefix, rc == 0
                  and "list-item: 1 marked, 0 retained" in out
                  and "table-row: 1 marked, 0 retained" in out and "0 findings" in out)
            for row in ("| Check endpoint |", "| Check | Expect refusal | excess |"):
                malformed = body.rsplit(indent, 1)[0] + indent + row + "\n"
                rejected("first-line ragged " + prefix + row, malformed, ("table-row",),
                         "ragged table row")

        # Fingerprint equality and baseline errors through the actual CLI.
        original = PREFIX + "plain\n"
        guide.write_text(original)
        baseline.write_text("")
        rc, out = cli("--write-baseline")
        check("unit seed counts", rc == 0 and "wrote 1 grandfathered units" in out
              and "seeded prose: 1" in out and "seeded list-item: 0" in out)
        saved = baseline.read_bytes()
        rc, out = cli("--write-baseline")
        check("nonempty seed refusal", rc == 1 and "seed refused: baseline already has entries" in out
              and baseline.read_bytes() == saved and "COUNTS" not in out)
        for name, body, diagnostic, counts in (
            ("retained", original, "0 findings", "prose: 0 marked, 1 retained"),
            ("moved", "\n" + original, "0 findings", "prose: 0 marked, 1 retained"),
            ("changed", PREFIX + "changed\n", "new/changed/excess prose", "prose: 0 marked, 0 retained"),
            ("duplicate", original + "\nplain\n", "(2 > 1)", "prose: 0 marked, 1 retained"),
            ("kind", PREFIX + "- plain\n", "new/changed/excess list-item", "list-item: 0 marked, 0 retained"),
            ("marked", PREFIX + MARK + "\n", "stale baseline prose", "prose: 1 marked, 0 retained"),
            ("deleted", PREFIX, "stale baseline prose", "prose: 0 marked, 0 retained"),
        ):
            guide.write_text(body)
            rc, out = cli("--strict")
            check("ratchet " + name, rc == (0 if name in {"retained", "moved"} else 1)
                  and diagnostic in out and "  COUNTS  " + counts + "\n" in out
                  and out.count("  COUNTS  ") == 4 and baseline.read_bytes() == saved)
        guide.write_text(original)
        for bad in (saved + saved, b"guide.md\tunknown\t" + b"a" * 64 + b"\t1\n",
                    b"guide.md\tprose\tbad\t1\n", saved.replace(b"\t1\n", b"\t0\n")):
            baseline.write_bytes(bad)
            rc, out = cli("--strict")
            check("invalid baseline " + repr(bad), rc == 1 and "baseline line" in out
                  and ("duplicate key" if bad == saved + saved else "malformed entry") in out
                  and "COUNTS" not in out)
        baseline.write_bytes(saved.replace(b"\t1\n", b"\t2\n"))
        rc, out = cli("--strict")
        check("count reduction", rc == 1 and "(1 < 2)" in out
              and "  COUNTS  prose: 0 marked, 1 retained\n" in out)
        for mode in ("missing", "directory", "encoding"):
            baseline.unlink()
            if mode == "directory":
                baseline.mkdir()
            elif mode == "encoding":
                baseline.write_bytes(b"\xff")
            rc, out = cli("--strict")
            check("baseline input " + mode, rc == 2 and "VERIFY-MARK input error:" in out
                  and "COUNTS" not in out)
            if baseline.is_dir():
                baseline.rmdir()
            baseline.write_bytes(saved)
        for mode in ("missing", "directory", "encoding"):
            guide.unlink()
            if mode == "directory":
                guide.mkdir()
            elif mode == "encoding":
                guide.write_bytes(b"\xff")
            rc, out = cli("--strict")
            diagnostic = "guide corpus is empty" if mode == "missing" else "VERIFY-MARK input error:"
            check("guide input " + mode, rc == (1 if mode == "missing" else 2)
                  and diagnostic in out and "COUNTS" not in out)
            if guide.is_dir():
                guide.rmdir()
            guide.write_text(original)
        guide.write_text(PREFIX + "> forbidden\n")
        baseline.write_text("# sentinel\n")
        rc, out = cli("--write-baseline")
        check("structural seed refusal preserves bytes", rc == 1 and "blockquote_open" in out
              and "COUNTS" not in out and baseline.read_bytes() == b"# sentinel\n")

        # Existing consumers keep fence ordering and inline credential coverage.
        from version_basis import verify_blocks
        from check_guard_conventions import verify_inline_spans, scan_text, Stats, parse_args
        body = PREFIX + MARK + "\n\n```bash\necho first\n```\n\n- item\n\n"
        body += "```bash\n# " + MARK + "\necho second\n```\n\n`curl -u user:secret https://example.com`\n"
        units = scan("consumer integration", body, (2, 1, 0, 2), 3, full=True)
        check("version basis fence ordinals", verify_blocks(body) ==
              ["echo first", "# " + MARK + "\necho second"])
        check("fence API identity", [(u[0], u[2], u[3]) for u in units if u[1] == "fence"]
              == gate.scan_guide(body, with_status=True)[0])
        check("inline credential span retained", [s for _, s in verify_inline_spans(body)]
              == ["curl -u user:secret https://example.com"])
        findings, stats = [], Stats()
        scan_text("guide.md", body, findings, stats, parse_args([]))
        check("inline credential diagnostic", [(line, code) for _, line, code, _ in findings
              if code == "C3-USER-ARGV"] == [(18, "C3-USER-ARGV")]
              and stats.inline_commands == 1)
