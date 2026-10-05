#!/usr/bin/env python3
"""End-to-end fixtures for the Verify fence ratchet; no corpus files are changed."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _verify_sections import META_EXCLUDE, verify_sections_text
from check_verify_marking import gate_parser, scan_guide

HAS_PARSER = gate_parser() is not None

TOOLS = Path(__file__).resolve().parent
PLAIN = "# Guide\n\n## Verify\n\n```sh\necho ok\n```\n"
MARK = "REASONED: expected exposed and fixed outcomes follow the cited vendor source."
count = 0


def check(name, condition):
    global count
    count += 1
    if not condition:
        raise AssertionError(name)


def invoke(root, *flags):
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(root / "tools/check_verify_marking.py"), *flags],
        capture_output=True, text=True, encoding="utf-8",
    )
    return result.returncode, result.stdout + result.stderr


def main():
    with tempfile.TemporaryDirectory(prefix="verify-marking-test-") as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        for name in ("check_verify_marking.py", "_markdown.py",
                     "_verify_sections.py", "version_basis.py", "requirements-gates.txt"):
            shutil.copyfile(TOOLS / name, root / "tools" / name)
        (root / "tools/version_basis_guides.txt").write_text("guide.md\n", encoding="utf-8")
        guide = root / "guide.md"
        baseline = root / "tools/verify_marking_baseline.txt"

        def run(body, expected, name, message="", *, unit_expected=None):
            if HAS_PARSER and unit_expected is not None:
                expected = unit_expected
            guide.write_text(body, encoding="utf-8")
            baseline.write_text("", encoding="utf-8")
            rc, out = invoke(root, "--strict")
            check(name, rc == expected and ("0 grandfathered" in out or expected == 2)
                  and message in out)

        for status in ("REASONED", "DEMONSTRATED", "reasoned", "demonstrated"):
            declaration = status + ": scope and provenance recorded here."
            for location, body in (
                ("before", PLAIN.replace("```sh", declaration + "\n\n```sh")),
                ("after", PLAIN + "\n" + declaration + "\n"),
                ("inside", PLAIN.replace("echo ok", "# " + declaration + "\necho ok")),
                ("heading", PLAIN.replace("## Verify", "## Verify (" + declaration + ")")),
            ):
                run(body, 0, status + " " + location)

        run(PLAIN.replace("echo ok", "# **REASONED:** evidence\necho ok"), 0, "bold")
        run(PLAIN.replace("```sh\necho ok", "```sql\n-- " + MARK + "\nSELECT 1;"),
            0, "SQL leading comment")
        for text in ('echo "REASONED: fake"', '{"status": "REASONED: fake"}',
                     "# not demonstrated", "# observed", "# unreasoned",
                     "# reasonedness", "# <!-- REASONED: hidden -->"):
            run(PLAIN.replace("echo ok", text), 1, "incidental " + text)
        run(PLAIN.replace("## Verify", "## Verify\n\n<!-- " + MARK + " -->"),
            1, "HTML comment")
        run(PLAIN.replace("```sh", "```console").replace("echo ok", "# " + MARK),
            1, "console output is not a comment declaration")
        run(PLAIN.replace("echo ok", "# REASONED:"), 1, "missing detail")
        run(PLAIN.replace("echo ok", "# " + MARK).replace(
            "## Verify", "## Verify (DEMONSTRATED: recorded run)"), 1, "conflict")
        run(PLAIN.replace("## Verify", "## Verify (" + MARK + ")\n\n### Child"),
            1, "heading does not propagate")
        run(PLAIN.replace("## Verify", MARK + "\n\n## Verify"),
            1, "remote introduction")
        run(PLAIN + "\n## Sources\n\n" + MARK, 1, "Sources does not attach")
        run(PLAIN + "\n" + MARK + "\n\n```sh\necho second\n```\n",
            1, "ambiguous paragraph")
        run(PLAIN + "\nREASONED: preceding block; recorded evidence.\n\n"
            "```sh\n# " + MARK + "\necho second\n```\n",
            0, "explicit preceding direction")
        run(PLAIN.replace("echo ok", "# " + MARK + "\necho ok")
            + "\nREASONED: following block; recorded evidence.\n\n"
            "```sh\necho second\n```\n", 0, "explicit following direction")

        run(PLAIN, 1, "new unmarked fence")
        rc, out = invoke(root, "--write-baseline")
        if HAS_PARSER:
            check("seed", rc == 0 and "1 grandfathered" in out)
        else:
            check("seed needs parser", rc == 1 and "seeding requires the pinned parser" in out)
            # Supply the old fence fixture explicitly so its ratchet still runs
            # when the new unit checks are unavailable. No seed is simulated.
            digest = scan_guide(PLAIN)[0][0][1]
            baseline.write_text(f"guide.md\tfence\t{digest}\t1\n", encoding="utf-8")
        saved = baseline.read_text(encoding="utf-8")
        rc, out = invoke(root, "--strict")
        check("retained exemption visible", rc == 0 and "BASELINE" in out)
        guide.write_text("\n\n" + PLAIN, encoding="utf-8")
        check("line movement stable", invoke(root, "--strict")[0] == 0)
        guide.write_text(PLAIN.replace("## Verify", "##   Verify   ##"), encoding="utf-8")
        check("heading normalization stable", invoke(root, "--strict")[0] == 0)
        for name, changed in (
            ("content", PLAIN.replace("echo ok", "echo changed")),
            ("ancestry", PLAIN.replace("# Guide", "# Changed")),
            ("context", PLAIN.replace("```sh", "New context.\n\n```sh")),
            ("language", PLAIN.replace("```sh", "```python")),
        ):
            guide.write_text(changed, encoding="utf-8")
            rc, out = invoke(root, "--strict")
            check("fingerprint " + name, rc == 1 and "stale baseline" in out
                  and "new/changed/excess" in out)
        guide.write_text(PLAIN + "\n```sh\necho ok\n```\n", encoding="utf-8")
        rc, out = invoke(root, "--strict")
        check("duplicate occurrence", rc == 1 and "(2 > 1)" in out)
        for name, changed in (
            ("marked", PLAIN.replace("echo ok", "# " + MARK + "\necho ok")),
            ("deleted", "# Guide\n\n## Verify\n"),
        ):
            guide.write_text(changed, encoding="utf-8")
            rc, out = invoke(root, "--strict")
            check("stale " + name, rc == 1 and "stale baseline" in out)
        guide.write_text(PLAIN, encoding="utf-8")
        baseline.write_text(saved + saved, encoding="utf-8")
        check("duplicate baseline key", invoke(root, "--strict")[0] == 1)
        baseline.write_text("bad entry\n", encoding="utf-8")
        check("malformed baseline", invoke(root, "--strict")[0] == 1)
        baseline.unlink()
        check("missing baseline fails closed", invoke(root, "--strict")[0] == 2)
        baseline.write_bytes(b"\xff")
        check("baseline encoding fails closed", invoke(root, "--strict")[0] == 2)
        baseline.write_text("", encoding="utf-8")
        guide.write_bytes(b"\xff")
        check("guide encoding fails closed", invoke(root, "--strict")[0] == 2)
        guide.write_text(PLAIN, encoding="utf-8")
        # A directory masquerading as the baseline reliably raises an OS error,
        # including when the tests run as a user who can bypass mode bits.
        baseline.unlink()
        baseline.mkdir()
        check("baseline OS error fails closed", invoke(root, "--strict")[0] == 2)
        guide.unlink()
        baseline.rmdir()

        for title in ("Verification checklist", "Quick checks", "3. Verify",
                      "Verify (REASONED: scoped evidence)"):
            body = PLAIN.replace("## Verify", "## " + title)
            check("alias " + title, len(scan_guide(body)[0]) == 1
                  and "echo ok" in verify_sections_text(body))
        for title in ("Deploying: verify from outside", "1. Verify from outside",
                      "Webhooks: verify the sender", "Re-verify after changes"):
            body = PLAIN.replace("## Verify", "## " + title)
            check("non-root " + title, not scan_guide(body)[0]
                  and not verify_sections_text(body))
        body = PLAIN.replace("## Verify", "## Verify\n\n### Nested\n\n#### Verify")
        check("nested root counted once", len(scan_guide(body)[0]) == 1)
        body = PLAIN + "\n## Setup\n\n```sh\necho outside\n```\n"
        check("sibling boundary", len(scan_guide(body)[0]) == 1)
        run("# Guide\n\n## Verify\n\n- item\n\n  ```sh\n  # " + MARK
            + "\n  echo ok\n  ```\n", 0, "list continuation", unit_expected=1)
        run("# Guide\n\n## Verify\n\n- outer\n  - inner\n\n"
            "    ```sh\n    # " + MARK + "\n    echo ok\n    ```\n",
            0, "nested list", unit_expected=1)
        run("# Guide\n\n## Verify\n\n- ```sh\n  echo ok\n  ```\n",
            1, "same-line list fence")
        run("# Guide\n\n## Verify\n\n- ```sh\n  echo ok\n  ```\n- "
            + MARK + "\n", 1, "sibling list paragraph does not attach")
        run(PLAIN.replace("```", "~~~~").replace("echo ok", "# " + MARK),
            0, "tilde fence")
        run(PLAIN.replace("```sh", "````sh").replace("echo ok",
            "# " + MARK + "\n```\n## fake"), 1, "short close stays in Verify",
            "unclosed fence")
        run("# Guide\n\n## Setup\n\n````md\n## Verify\n```\n````\n",
            0, "fake heading and shorter fence")
        run(PLAIN.replace("echo ok", "# " + MARK).replace("\n", "\r\n"),
            0, "CRLF")
        run(PLAIN.replace("echo ok", "# " + MARK) + "\ntext\u2028## Setup\n",
            0, "Unicode separator is not a heading", unit_expected=1)
        run(PLAIN.rsplit("```", 1)[0], 1, "unclosed fence")
        run("# Guide\n\n## Verify\n\n- ```sh\n  # " + MARK
            + "\n  echo ok\n```\n", 1, "dedented list close fails")
        run(PLAIN + "\n> unsupported quote\n", 1, "quoted prose does not mark fence", "new/changed/excess")
        run("# Guide\n\n## Verify\n\n- prose check\n\n| Check | Result |\n"
            "| --- | --- |\n| A | B |\n", 0, "lists tables prose need declarations when parser is present", unit_expected=1)

        # Version-basis integration: parser and summary exceptions stay narrow.
        from version_basis import START, END
        marked_pilot = PLAIN.replace("echo ok", "# " + MARK + "\necho ok")
        front = '---\nversion_basis: {"schema": 1}\n---\n'
        summary = START + "\n**Version basis**\n\n| Claim | Status |\n" + END + "\n\n"
        pilot = marked_pilot.replace("## Verify", summary + "## Verify")
        run(front + pilot, 0, "leading strict front matter and generated pair")
        run(front + marked_pilot, 0, "front matter closing delimiter is not Setext")
        units, errors = scan_guide(front + marked_pilot)
        check("masked metadata preserves fence lines",
              not errors and units[0][0] == 8)
        run(pilot, 0, "enrolled exact pair without front matter")
        units, errors = scan_guide((front + pilot).replace("\n", "\r\n"), enrolled=True)
        check("direct CRLF scan", len(units) == 1 and not errors)
        run((front + pilot).replace("\n", "\r\n"), 0, "pilot CRLF")
        run(front + marked_pilot.replace("echo ok", "echo ok\u2028## Setup"), 0,
            "front matter preserves Unicode line separator")
        for name, raw in (
            ("foreign key", "---\ntitle: Example\n---\n"),
            ("invalid JSON", "---\nversion_basis: {bad}\n---\n"),
            ("duplicate key", '---\nversion_basis: {"x":1,"x":2}\n---\n'),
            ("non-object", "---\nversion_basis: []\n---\n"),
            ("alias", "---\nversion_basis: &alias {}\n---\n"),
            ("tag", "---\nversion_basis: !!map {}\n---\n"),
            ("comment", "---\nversion_basis: {} # comment\n---\n"),
            ("trailing comma", '---\nversion_basis: {"x":1,}\n---\n'),
            ("non-JSON number", '---\nversion_basis: {"x":NaN}\n---\n'),
            ("unclosed", "---\nversion_basis: {}\n"),
            ("first close wins", "---\nversion_basis: {\n---\n}\n---\n"),
            ("non-leading", "\n" + front),
            ("non-leading with blank before close", "\n---\nversion_basis: {}\n\n---\n"),
            ("after title", "# Guide\n\n" + front),
            ("indented opener", " " + front),
        ):
            run(raw + marked_pilot, 1, "front matter refusal " + name,
                "[unsupported-container]")
        for name, changed in (
            ("start spelling", pilot.replace(START, "<!-- version_basis:start -->")),
            ("end spelling", pilot.replace(END, "<!-- version_basis:end -->")),
            ("case", pilot.replace(START, "<!-- Version-basis:start -->")),
            ("inner spacing", pilot.replace(END, "<!--version-basis:end-->")),
            ("indent", pilot.replace(START, " " + START)),
            ("trailing space", pilot.replace(END, END + " ")),
            ("text before", pilot.replace(START, "text " + START)),
            ("text after", pilot.replace(END, END + " text")),
            ("same line", pilot.replace(summary, START + END + "\n\n")),
            ("second pair", pilot.replace(summary, summary + summary)),
            ("duplicate start", pilot.replace(START, START + "\n" + START)),
            ("duplicate end", pilot.replace(END, END + "\n" + END)),
            ("missing start", pilot.replace(START, "")),
            ("missing end", pilot.replace(END, "")),
            ("reversed", pilot.replace(START, "TEMP").replace(END, START).replace("TEMP", END)),
            ("after H2", pilot.replace(summary, "").replace("## Verify", "## Verify\n" + summary)),
            ("straddles H2", pilot.replace(END, "## Setup\n\n" + END)),
            ("ordinary comment", pilot.replace(END, "<!-- other -->\n" + END)),
        ):
            run(changed, 1, "summary refusal " + name, "HTML comment outside")
        for heading in ("  ## Setup", "##\tSetup"):
            run(heading + "\n\n" + pilot, 1, "pair after alternate H2 " + heading,
                "HTML comment outside")
        run(pilot.replace(END, END + "\n\n```text\n" + START + "\n" + END + "\n```"),
            1, "literal duplicate does not authorize the real pair", "HTML comment outside")
        listing = root / "tools/version_basis_guides.txt"
        listing.write_text("other.md\n", encoding="utf-8")
        run(front + pilot, 1, "pair in non-enrolled guide", "HTML comment outside")
        listing.unlink()
        run(marked_pilot, 2, "missing enrollment list fails closed", "input error")
        listing.write_text("guide.md\n", encoding="utf-8")
        for content in ("## Verify", "### Verify", "# Other", "Details\n---",
                        "```bash\necho hidden\n```"):
            changed = pilot.replace("**Version basis**", content)
            run(changed, 1, "summary content cannot select sections " + content,
                "[unsupported-container]")
            units, errors = scan_guide(changed, enrolled=True)
            check("summary quarantined " + content, len(units) == 1 and bool(errors))
        # A pair after Verify must not let an enclosed peer heading hide a fence.
        changed = marked_pilot.replace("```sh", START + "\n## Setup\n" + END + "\n\n```sh")
        units, errors = scan_guide(changed, enrolled=True)
        check("misplaced summary cannot close Verify", len(units) == 1 and bool(errors))
        run(marked_pilot + "\n## Samples\n\n```text\n" + START + "\n" + END
            + "\n```\n", 0, "markers inside a literal fence")
        run(marked_pilot + "\n`" + START + " " + END + "`\n", 0,
            "markers inside a matched code span", unit_expected=1)
        run("> ---\n> version_basis: {}\n> ---\n", 1,
            "quoted metadata is not a document header", "[unsupported-container]")
        for body in (
            marked_pilot.replace("# " + MARK, "# ordinary\n# " + MARK),
            marked_pilot.replace("# " + MARK, "echo first\n# " + MARK),
        ):
            run(body, 1, "per-command comment is not a fence declaration", "new/changed/excess")

        # Round-2: unsupported containers must fail closed even when their
        # contents look marked, or a nested heading would hide the Verify root.
        unsupported = "[unsupported-container]"
        for prefix in ("- - ", "- 2. ", "1. - ", "+ * ", "- - - "):
            indent = " " * len(prefix)
            for comment in ("ordinary comment", MARK):
                body = (prefix + "```sh\n" + indent + "# " + comment + "\n"
                        + indent + "echo ok\n" + indent + "```\n")
                run("## Verify\n\n" + body, 1,
                    f"compact fence {prefix!r} {comment}", unsupported)
            for title in ("## Verify", "### Quick checks", "## Verify (" + MARK + ")"):
                run(prefix + title + "\n", 1,
                    f"compact Verify root {prefix!r} {title}", unsupported)
            run("## Verify\n\n" + prefix + "## Details\n", 1,
                f"compact heading cannot end Verify {prefix!r}", unsupported)
        run("## Verify\n\n- - explanation\n\n    ```sh\n"
            "    # ordinary comment\n    echo ok\n    ```\n", 1,
            "compact state survives to later fence", unsupported)
        run("- - explanation\n\n    ## Verify\n\n    ```sh\n"
            "    # ordinary comment\n    echo ok\n    ```\n", 1,
            "compact state contains later Verify root", unsupported)
        for prefix in ("-", "+", "2.", "- -"):
            indent = " " * (len(prefix) + 1)
            run("## Verify\n\n" + prefix + "\n\n" + indent + "```sh\n"
                + indent + "# " + MARK + "\n" + indent + "```\n", 1,
                "empty item contains marked fence " + prefix, unsupported)
            run(prefix + "\n\n" + indent + "## Verify\n", 1,
                "empty item contains Verify root " + prefix, unsupported)
        run("## Setup\n\n- <!-- comment --> ## Details\n\n## Verify\n\n"
            + MARK + "\n\n```sh\necho ok\n```\n", 1,
            "comment before list heading is unsupported", unsupported)
        for item in ("- ## Details", "- item\n\n  ## Details",
                     "- outer\n  - ## Details"):
            run("## Verify\n\n" + item + "\n", 1,
                "heading in list " + item, unsupported)
            run(item.replace("## Details", "## Verify") + "\n", 1,
                "Verify root in list " + item, unsupported)
        for quote in ("> ", "> > ", "  > "):
            for item in ("2. ## Details", "1. ## Details", "- ## Details"):
                run("## Verify\n\n" + quote + "explanation\n" + quote + item
                    + "\n" + MARK + "\n\n```sh\necho ok\n```\n", 1,
                    f"quoted list provenance {quote!r} {item}", unsupported)
            run(quote + "- - ## Verify\n", 1,
                "quoted compact Verify root " + quote, unsupported)
            run("## Verify\n\n" + quote + "## Details\n", 1,
                "quoted heading without fence " + quote, unsupported)
        run("## Verify\n\n> - item\n>\n>   ```sh\n"
            ">   # ordinary comment\n>   echo ok\n>   ```\n", 1,
            "quoted list state contains later fence", unsupported)
        rc, out = invoke(root, "--write-baseline")
        check("unsupported containers cannot be seeded", rc == 1
              and (unsupported if HAS_PARSER else "seeding requires the pinned parser") in out
              and baseline.read_text(encoding="utf-8") == "")
        run("## Verify\n\n" + MARK + "\n2. additional provenance\n\n"
            "```sh\necho ok\n```\n", 0, "ordered prose retains adjacent declaration")
        for marker in ("+", "2."):
            run("## Verify\n\n" + MARK + "\n" + marker + "\n\n"
                "```sh\necho ok\n```\n", 0,
                "empty marker cannot interrupt declaration " + marker)
        run("## Setup\n\n- - ```sh\n    # ordinary comment\n    ```\n", 0,
            "unsupported fence outside Verify")
        run("## Verify\n\n- - prose only\n\n> - quoted prose only\n", 0,
            "unsupported prose without headings or fences", unit_expected=1)
        run("## Verify\n\n- - prose only\n\n" + MARK + "\n\n"
            "```sh\necho ok\n```\n", 0, "dedent ends unsupported item", unit_expected=1)
        run("## Verify\n\n- - " + MARK + "\n\n```sh\necho ok\n```\n", 1,
            "unsupported prose cannot declare outside fence", "new/changed/excess")

        # Round-3: detect unsupported syntax even without an unmarked fence.
        fence = "```sh\necho ok\n```\n"
        marked = fence.replace("echo ok", "# " + MARK + "\necho ok")
        for underline in ("-", "--", "------", "=", "======", "   ===\t"):
            for title in ("Verify", "Quick checks", "Details"):
                for prefix, indent in (("", ""), ("- ", "  "),
                                       ("> ", "> "), ("- - ", "    ")):
                    body = prefix + title + "\n" + indent + underline + "\n"
                    run(body, 1, f"Setext alone {prefix!r} {title} {underline!r}",
                        unsupported)
            run("Verify\n" + underline + "\n\n" + fence, 1,
                "Setext root with fence " + repr(underline), unsupported)
            run("## Verify\n\nDetails\n" + underline + "\n\n" + marked, 1,
                "Setext cannot close Verify " + repr(underline), unsupported)
        run(PLAIN + "\nQuick checks\n------------\n\n" + fence, 1,
            "Setext root shadows ATX guide shape", "Setext heading")
        for underline in ("---", "==="):
            run("## Setup\n\nProse\n\n" + underline + "\n", 0,
                "separated underline is not Setext " + underline)
            run("## Setup\n\n```text\nVerify\n" + underline + "\n```\n", 0,
                "fenced Setext sample " + underline)

        html_cases = (
            ("<div>", "</div>\n\n"), ("<details>", "</details>\n\n"),
            ("<pre>", "</pre>\n"), ("<SCRIPT>", "</script>\n"),
            ("<style>", "</style>\n"), ("<textarea>", "</textarea>\n"),
            ("<!--", "-->\n"), ("<?instruction", "?>\n"),
            ("<!DOCTYPE", ">\n"), ("<![CDATA[", "]]>\n"),
            ("<custom data-x='a > b'>", "</custom>\n\n"),
            ("</custom>", "\n"), ("<hr/>", "\n"),
            ("<div", "\n"),
        )
        for opening, ending in html_cases:
            for label, content in (("heading", "## Verify\n"),
                                   ("marked fence", marked), ("plain fence", fence)):
                run(opening + "\n" + content + ending, 1,
                    f"HTML {opening} {label} outside Verify", unsupported)
            body = "## Verify\n\n" + opening + "\n## Details\n" + ending + "\n" + fence
            run(body, 1, "HTML cannot close Verify " + opening, "heading in HTML block")
            check("HTML boundary retains real fence " + opening,
                  len(scan_guide(body)[0]) == 1)
            run(opening + "\n## Verify\n", 1,
                "HTML at EOF " + opening, "heading in HTML block")
        for opening in ("<pre>", "<script>", "<style>", "<textarea>"):
            run(opening + "\n\n## Verify\n</pre>\n", 1,
                "raw HTML spans blanks " + opening, "heading in HTML block")
        for opening, ending in html_cases:
            if opening == "<!--":
                continue
            run("## Verify\n\n" + opening + "\nplain text\n" + ending + "\n" + marked,
                0, "HTML terminator restores Markdown " + opening, unit_expected=1)
        run("## Verify\n\n<pre>sample</style>\n" + marked, 0,
            "raw HTML can close on opener with different raw tag", unit_expected=1)
        run("## Verify\n\n<div>\n<pre>\n\n" + marked, 0,
            "nested HTML does not replace blank terminator", unit_expected=1)
        run("## Verify\n\n" + MARK + "\n<custom>\n\n" + fence, 0,
            "type 7 cannot interrupt a paragraph", unit_expected=1)
        run("## Verify\n\n- item\n<div>\n## Details\n</div>\n\n" + fence,
            1, "HTML interrupts list paragraph before quarantine", "heading in HTML block")
        run("Introductory prose\n- <custom>\n  ```sh\n  # " + MARK + "\n  ```\n",
            1, "type 7 starts in a new list item after prose", "fence in HTML block")
        run("<pre/>\n## Verify\n\n" + marked, 0,
            "self-closing raw tag is not type 1 or type 7", unit_expected=1)
        run("- <pre>\n  sample\n\n## Verify\n\n" + marked, 0,
            "container dedent ends HTML quarantine")

        for item in ("- item", "1. item", "- - item"):
            indent = " " * (4 if item == "- - item" else len(item) - len("item"))
            body = item + "\nlazy continuation\n\n" + indent
            run(body + "## Verify\n", 1,
                "Verify alone after lazy list line " + item, unsupported)
            run("## Verify\n\n" + body + "## Details\n\n"
                + "".join(indent + line + "\n" for line in fence.splitlines()),
                1, "lazy list boundary reproduction " + item, unsupported)
        run("- item\nlazy continuation\n\n## Verify\n\n" + marked, 0,
            "blank and dedent release lazy list ownership")
        run("- item\nlazy continuation\n## Verify\n\n" + marked, 0,
            "top-level ATX heading interrupts lazy paragraph")

        run("## Verify\n\nCheck the service <!-- note\n\n" + fence + "\n-->\n",
            1, "mid-paragraph comment reproduction", "HTML comment outside fence or code span")
        for text in ("prose <!--", "<!-- note -->", "`unmatched <!--",
                     "``different ` <!--", "\\`escaped <!-- `"):
            run("## Setup\n\n" + text + "\n", 1,
                "comment rejected outside Verify " + text, unsupported)
        for text in ("`<!--`", "`` ` <!-- ``", "`multiline\nliteral <!-- span`",
                     "``backslash \\` <!--``"):
            run("## Verify\n\n" + text + "\n\n" + marked, 0,
                "matched code span contains literal opener " + text, unit_expected=1)
        run("## Setup\n\n`unfinished span\n<!-- block comment`\n", 1,
            "HTML block interrupts paragraph before span matching", unsupported)
        run("## Verify\n\n" + r"\``<!--`" + "\n\n" + marked, 0,
            "escape consumes only first backtick in opening run", unit_expected=1)
        run("## Verify\n\n`<!--` then <!-- real -->\n\n" + marked, 1,
            "code span does not hide subsequent comment", unsupported)
        run("## Verify\n\n```sh\n# " + MARK + "\nprintf '<!--'\n```\n", 0,
            "fenced comment literal")
        run("## Verify\n\n<!-- harmless -->\n\n" + marked, 1,
            "even closed block comment is unsupported", unsupported)
        rc, out = invoke(root, "--write-baseline")
        check("comment cannot be grandfathered", rc == 1
              and (unsupported if HAS_PARSER else "seeding requires the pinned parser") in out
              and baseline.read_text(encoding="utf-8") == "")

        # Round-1 reproductions: strict CLI checks include the diagnostic, so a
        # different failure cannot accidentally satisfy a regression.
        fence = "```sh\necho ok\n```\n"
        marked = fence.replace("echo ok", "# " + MARK + "\necho ok")
        for indent in range(4):
            prefix = " " * indent + "> "
            for label, content in (("unmarked", fence), ("marked", marked)):
                quoted = "".join(prefix + line + "\n" for line in content.splitlines())
                run("## Verify\n\n" + quoted, 1, f"quoted {indent} {label}",
                    "unsupported fenced blockquote")
                run("## Setup\n\n" + quoted, 0, f"outside quote {indent} {label}")
                run(prefix + "## Verify\n" + prefix + "\n" + quoted, 1,
                    f"quoted Verify root {indent} {label}", "unsupported fenced blockquote")
            run("## Verify\n\n" + prefix + "See Sources.\n", 0,
                f"quoted prose {indent}", unit_expected=1)
            run("## Verify\n\n" + " " * indent + fence.replace("\n", "\n" + " " * indent),
                1, f"fence indent {indent}", "new/changed/excess")
            run("## Verify\n\n" + " " * indent + marked.replace("\n", "\n" + " " * indent),
                0, f"marked fence indent {indent}")

        for prefix in ("    ", "\t", " \t"):
            for content in (MARK, "DEMONSTRATED: both states observed.", "<!--", "- ```sh\n  echo ok\n  ```",
                            "> ```sh\n> echo ok\n> ```", fence.rstrip()):
                code = "\n".join(prefix + line for line in content.splitlines()) + "\n"
                expected = int(content == "<!--")
                run("## Verify\n\n" + code, expected,
                    f"indented code alone {prefix!r} {content}", unit_expected=1)
                run("## Verify\n\n" + code + "\n" + fence, 1,
                    f"code cannot mark or hide {prefix!r} {content}", "new/changed/excess")
                run("## Verify\n\n" + code + "\n" + marked, expected,
                    f"code before marked fence {prefix!r} {content}", unit_expected=1)
            run("## Verify\n\n" + MARK + "\n\n" + prefix + "sample\n\n" + fence,
                1, f"indented code blocks attachment {prefix!r}", "new/changed/excess")
            run("## Verify\n\n" + fence + "\n" + prefix + MARK, 1,
                f"indented following declaration {prefix!r}", "new/changed/excess")
        run("## Verify\n\n" + MARK + "\n    continued provenance\n\n" + fence,
            0, "indent cannot interrupt paragraph")
        run("## Verify\n\n- item\n\n      " + MARK + "\n\n  "
            + fence.replace("\n", "\n  "), 1, "list indented code is not prose",
            "new/changed/excess")
        run("## Verify\n\n-     <!--\n\n  " + fence.replace("\n", "\n  "),
            1, "list padding starts code before HTML", "new/changed/excess")
        run("## Verify\n\n>     <!--\n>\n> ```\n> text\n> ```\n", 1,
            "quoted indented HTML cannot hide fence", "unsupported fenced blockquote")
        run("## Verify\n\n>     ```\n>     sample\n>     ```\n", 0,
            "quoted indented fence sample is code", unit_expected=1)

        for suffix in ("(**DEMONSTRATED:** observed pair)",
                       "(__DEMONSTRATED:__ observed pair)",
                       "(**DEMONSTRATED**: observed pair)",
                       "( DEMONSTRATED: observed pair )",
                       "(DEMONSTRATED: recorded run (local))",
                       ": **DEMONSTRATED:** observed pair"):
            body = "## Verify " + suffix + "\n\n" + fence
            run(body, 0, "complete heading suffix " + suffix, "1 marked")
            run(body.replace("echo ok", "# " + MARK + "\necho ok"), 1,
                "heading conflict " + suffix, "conflicting declarations")
            check("shared heading grammar " + suffix,
                  "echo ok" in verify_sections_text(body) and len(scan_guide(body)[0]) == 1)
        for suffix in ("(**DEMONSTRATED:**)", "( DEMONSTRATED: )",
                       "(DEMONSTRATED: recorded run) is false",
                       "(DEMONSTRATED: recorded run) is false)",
                       "(DEMONSTRATED: recorded run) (unrelated)",
                       "(**DEMONSTRATED:** recorded run"):
            for heading in ("## Verify ", "## Verify\n\n### Check "):
                body = heading + suffix + "\n\n" + marked
                message = ("needs scope and provenance" if "recorded run" not in suffix
                           else "complete suffix")
                run(body, 1, "bad suffix still selected " + heading + suffix, message)
                run((heading + suffix + "\n\nprose only\n"), 0,
                    "bad suffix applies to prose when parser is present " + heading + suffix, unit_expected=1)
                check("malformed suffix retains section " + heading + suffix,
                      "echo ok" in verify_sections_text(body) and len(scan_guide(body)[0]) == 1)
        run("## Verify (REASONED)\n\n" + fence, 1,
            "legacy status selects but does not mark", "new/changed/excess")
        run("## Verify\n\n### Check (DEMONSTRATED: recorded run)\n\n" + fence,
            0, "descendant complete suffix", "1 marked")

        for heading in ("## Setup", "## Verify"):
            expected = int(heading == "## Verify")
            run(heading + "\n\n```sh\necho ok\n", expected,
                "unclosed scope " + heading, "unclosed fence" if expected else "0 findings")
            run(heading + "\n\n- ```sh\n  echo ok\noutside\n", expected,
                "unclosed list scope " + heading,
                "unclosed list fence" if expected else "0 findings")
        run("## Verify\n\n" + marked + "\n## Setup\n\n```sh\nunfinished\n", 0,
            "unclosed after Verify boundary")
        run("## Verify\n\n> See Sources.\n" + MARK + "\n\n" + fence, 1,
            "lazy quoted paragraph cannot mark outside fence", "new/changed/excess")
        run("## Verify\n\n> See Sources.\n\n" + MARK + "\n\n" + fence, 0,
            "blank ends lazy quote", unit_expected=1)
        run("## Verify\n\n> See Sources.\n" + marked, 0,
            "fence interrupts quote laziness", unit_expected=1)
        run("> See Sources.\n## Verify\n\n" + fence, 1,
            "heading interrupts quote laziness", "new/changed/excess")
        run("## Verify\n\n> ```sh\noutside\n", 1,
            "quote fence has no lazy continuation", "unsupported fenced blockquote")
        run("## Setup\n\n> ```sh\n## Verify\n\n" + marked, 0,
            "missing quote ends outside fence before Verify heading")
        run("## Verify\n\n> > Sources.\n" + MARK + "\n\n" + fence, 1,
            "nested quote laziness stays quoted", "new/changed/excess")
        run("## Verify\n\n> > Sources.\n\n" + MARK + "\n\n" + fence, 0,
            "blank ends nested lazy quote", unit_expected=1)
        run("## Verify\n\n  > ```sh\n  > echo ok\n  > ```\n", 1,
            "exact indented quote reproduction", "unsupported fenced blockquote")

    from test_verify_units import run_cases
    run_cases(check)

    suite = (TOOLS / "run_all_checks.sh").read_text(encoding="utf-8")
    excluded = re.search(r"    (CONTRIBUTING\.md\|.*?)\) return 0", suite)[1]
    check("guide set matches suite", set(excluded.split("|")) == META_EXCLUDE)
    print(f"  ok    {count} Verify-marking fixture cases")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, OSError) as exc:
        print(f"  FAIL  Verify-marking fixtures: {exc}")
        sys.exit(1)
