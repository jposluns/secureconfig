#!/usr/bin/env python3
"""End-to-end fixtures for the Verify fence ratchet; no corpus files are changed."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_reasoned_rows import META_EXCLUDE, verify_sections_text
from check_verify_marking import scan_guide

TOOLS = Path(__file__).resolve().parent
PLAIN = "# Guide\n\n## Verify\n\n```sh\necho ok\n```\n"
MARK = "REASONED: no authorized second network; TODO 1.1 tracks both-state checks."
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
        for name in ("check_verify_marking.py", "check_reasoned_rows.py",
                     "_markdown.py", "_verify_sections.py"):
            shutil.copyfile(TOOLS / name, root / "tools" / name)
        guide = root / "guide.md"
        baseline = root / "tools/verify_marking_baseline.txt"

        def run(body, expected, name, message=""):
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
        check("seed", rc == 0 and "1 grandfathered" in out)
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
            + "\n  echo ok\n  ```\n", 0, "list continuation")
        run("# Guide\n\n## Verify\n\n- outer\n  - inner\n\n"
            "    ```sh\n    # " + MARK + "\n    echo ok\n    ```\n",
            0, "nested list")
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
            0, "Unicode separator is not a heading")
        run(PLAIN.rsplit("```", 1)[0], 1, "unclosed fence")
        run("# Guide\n\n## Verify\n\n- ```sh\n  # " + MARK
            + "\n  echo ok\n```\n", 1, "dedented list close fails")
        run(PLAIN + "\n> unsupported quote\n", 1, "quoted prose does not mark fence", "new/changed/excess")
        run("# Guide\n\n## Verify\n\n- prose check\n\n| Check | Result |\n"
            "| --- | --- |\n| A | B |\n", 0, "lists tables prose not gated")

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
                f"quoted prose {indent}")
            run("## Verify\n\n" + " " * indent + fence.replace("\n", "\n" + " " * indent),
                1, f"fence indent {indent}", "new/changed/excess")
            run("## Verify\n\n" + " " * indent + marked.replace("\n", "\n" + " " * indent),
                0, f"marked fence indent {indent}")

        for prefix in ("    ", "\t", " \t"):
            for content in (MARK, "DEMONSTRATED: both states observed.", "<!--", "- ```sh\n  echo ok\n  ```",
                            "> ```sh\n> echo ok\n> ```", fence.rstrip()):
                code = "\n".join(prefix + line for line in content.splitlines()) + "\n"
                run("## Verify\n\n" + code, 0, f"indented code alone {prefix!r} {content}")
                run("## Verify\n\n" + code + "\n" + fence, 1,
                    f"code cannot mark or hide {prefix!r} {content}", "new/changed/excess")
                run("## Verify\n\n" + code + "\n" + marked, 0,
                    f"code before marked fence {prefix!r} {content}")
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
            "quoted indented fence sample is code")

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
                    "bad suffix without fence is outside gate " + heading + suffix)
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
            "blank ends lazy quote")
        run("## Verify\n\n> See Sources.\n" + marked, 0,
            "fence interrupts quote laziness")
        run("> See Sources.\n## Verify\n\n" + fence, 1,
            "heading interrupts quote laziness", "new/changed/excess")
        run("## Verify\n\n> ```sh\noutside\n", 1,
            "quote fence has no lazy continuation", "unsupported fenced blockquote")
        run("## Setup\n\n> ```sh\n## Verify\n\n" + marked, 0,
            "missing quote ends outside fence before Verify heading")
        run("## Verify\n\n> > Sources.\n" + MARK + "\n\n" + fence, 1,
            "nested quote laziness stays quoted", "new/changed/excess")
        run("## Verify\n\n> > Sources.\n\n" + MARK + "\n\n" + fence, 0,
            "blank ends nested lazy quote")
        run("## Verify\n\n  > ```sh\n  > echo ok\n  > ```\n", 1,
            "exact indented quote reproduction", "unsupported fenced blockquote")

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
