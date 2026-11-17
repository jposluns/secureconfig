#!/usr/bin/env python3
"""Exercise scripts/build-instructions.sh through the shipped script on throwaway trees.

Each tree carries the 3 inputs the script lists under --list-inputs: a SKILL.md with the 4
sections the build reads (the rules section among them), a plugin/always-on.md ending in a
closing paragraph and a README.md with a "## Guide index" section. The cases check that the
build writes site/secureconfig-instructions.md with the 4 SKILL.md sections, each
`references/<file>` code span rewritten to the bare file name so the rules keep their guide
routes, with always-on.md's closing paragraph after the rules and none of its own rules, the
fetch section and the re-emitted guide index; that --check passes on a fresh file, writes
nothing, and fails on a stale, edited or missing one, which is the staleness rule the
instructions section of tools/run_all_checks.sh runs on the real tree; that --list-inputs
prints the 3 inputs and nothing else; and that a missing or repeated section, a references/
path in a form the build does not rewrite, an index with no guide row, a guide-index row the
build cannot read, an always-on.md without a closing paragraph, a second argument, an unknown
argument and a missing site/ folder are each refused with the input, argument or path named,
never with a traceback. The build is standard library only, so no case needs the pinned parser
or the network. Exit 0 with one ok line, 1 on a failed case (an assertion).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build-instructions.sh"
OUT = "site/secureconfig-instructions.md"

SKILL_MD = """---
name: fixture
---

# Fixture skill

Intro prose the build does not read.

## Rules that apply to every deployment

Apply these fixture rules:

1. Keep secrets out of the repository (`references/secrets.md`).

## Verify steps are the point, not the configuration

Run the Verify block in `references/mfa.md` and show the output.

## Choosing guides

Start with `references/free-certificates.md`, then the service guide.

## What this skill does not do

It does not cover application-layer vulnerabilities.
"""

ALWAYS_MD = """## Rules that apply to every deployment
Apply these whether or not a specific guide is open:

1. Treat every service as internet-reachable until you have confirmed otherwise.

Before configuring a service, use the secureconfig skill.
"""

README_MD = """# Fixture

## Guide index

### Certificates and tunnels

| Guide | Covers |
|---|---|
| [mfa.md](mfa.md) | MFA options and enrolment |
| [secrets.md](secrets.md) | Keeping keys out of repositories |

### Web servers

| Guide | Covers |
|---|---|
| [nginx.md](nginx.md) | nginx: TLS, redirect, HSTS |
"""


def write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def tree(directory, skill=SKILL_MD, always=ALWAYS_MD, readme=README_MD):
    root = directory / "repo"
    write(root, "scripts/build-instructions.sh", SCRIPT.read_text(encoding="utf-8"))
    write(root, "plugin/skills/secureconfig/SKILL.md", skill)
    write(root, "plugin/always-on.md", always)
    write(root, "README.md", readme)
    (root / "site").mkdir()
    return root


def run(root, *args):
    done = subprocess.run(["bash", "scripts/build-instructions.sh", *args], cwd=root,
                          capture_output=True, text=True, timeout=120)
    return done.returncode, done.stdout + done.stderr


def main():
    count = 0
    with tempfile.TemporaryDirectory() as directory:
        root = tree(Path(directory))

        # --list-inputs prints the 3 inputs, one per line, and builds nothing.
        status, output = run(root, "--list-inputs")
        assert status == 0 and output.splitlines() == [
            "plugin/skills/secureconfig/SKILL.md", "plugin/always-on.md", "README.md"], output
        assert not (root / OUT).exists(), "--list-inputs wrote the output file"
        count += 1

        # A second argument is refused, counted, and builds nothing.
        status, output = run(root, "--list-inputs", "--check")
        assert status != 0 and "2 arguments given" in output, (status, output)
        assert not (root / OUT).exists(), "a refused argument list wrote the output file"
        count += 1

        # The build writes the file: the 4 SKILL.md sections, each `references/<file>` code
        # span rewritten to the bare name so the rules keep their guide routes, always-on.md's
        # closing paragraph after the rules and none of its own rules, the fetch section and
        # the guide index re-emitted as one line per guide under its category.
        status, output = run(root)
        assert status == 0 and f"wrote {OUT} (" in output, (status, output)
        text = (root / OUT).read_text(encoding="utf-8")
        for needed in ("## Rules that apply to every deployment",
                       "Apply these fixture rules:",
                       "Keep secrets out of the repository (`secrets.md`).",
                       "Before configuring a service, use the secureconfig skill.",
                       "## Verify steps are the point, not the configuration",
                       "Run the Verify block in `mfa.md` and show the output.",
                       "Start with `free-certificates.md`, then the service guide.",
                       "## What this skill does not do", "## Fetching a guide",
                       "`https://raw.githubusercontent.com/jposluns/secureconfig/main/"
                       "<guide>.md`", "## Guide index", "### Certificates and tunnels",
                       "- `mfa.md`: MFA options and enrolment",
                       "- `nginx.md`: nginx: TLS, redirect, HSTS"):
            assert needed in text, (needed, text)
        assert "references/" not in text, text
        # The rules come from SKILL.md alone: its rules section appears once, and nothing of
        # always-on.md is carried but its closing paragraph.
        assert text.count("## Rules that apply to every deployment") == 1, text
        assert "Treat every service as internet-reachable" not in text, text
        assert "Apply these whether or not a specific guide is open:" not in text, text
        assert (text.index("## Rules that apply to every deployment")
                < text.index("Before configuring a service, use the secureconfig skill.")
                < text.index("## Verify steps are the point, not the configuration")), text
        count += 1

        # --check passes on the fresh file and writes nothing.
        before = (root / OUT).read_bytes()
        status, output = run(root, "--check")
        assert status == 0 and f"  ok    {OUT} matches a fresh build" in output, (status, output)
        assert (root / OUT).read_bytes() == before, "--check rewrote the output file"
        count += 1

        # A source edit makes --check fail as stale, still writing nothing.
        write(root, "plugin/always-on.md", ALWAYS_MD + "\nA new always-on line.\n")
        status, output = run(root, "--check")
        assert status == 1 and f"  FAIL  {OUT} is stale" in output, (status, output)
        assert (root / OUT).read_bytes() == before, "a failing --check rewrote the output file"
        count += 1

        # A hand edit to the generated file fails --check too, and a rebuild clears it.
        write(root, "plugin/always-on.md", ALWAYS_MD)
        (root / OUT).write_text((root / OUT).read_text(encoding="utf-8") + "edited\n",
                                encoding="utf-8")
        status, output = run(root, "--check")
        assert status == 1 and f"  FAIL  {OUT} is stale" in output, (status, output)
        status, output = run(root)
        assert status == 0, output
        status, output = run(root, "--check")
        assert status == 0, (status, output)
        count += 1

        # A missing output file is its own finding.
        (root / OUT).unlink()
        status, output = run(root, "--check")
        assert status == 1 and f"  FAIL  {OUT} is missing" in output, (status, output)
        count += 1

        # An unknown argument is refused, named.
        status, output = run(root, "--frobnicate")
        assert status != 0 and "unknown argument '--frobnicate'" in output, (status, output)
        count += 1

        # A missing site/ folder is a named failure, not a traceback.
        (root / "site").rmdir()
        status, output = run(root)
        assert status != 0 and f"cannot write {OUT}" in output, (status, output)
        assert "Traceback" not in output, output
        count += 1

    cases = (
        # A SKILL.md section the build reads, missing and repeated, each refused with the count.
        (dict(skill=SKILL_MD.replace("## Choosing guides", "## Choosing")),
         "has 0 lines '## Choosing guides'"),
        (dict(skill=SKILL_MD + "\n## Choosing guides\n\nAgain.\n"),
         "has 2 lines '## Choosing guides'"),
        # A references/ path in a form the build does not rewrite is refused, not shipped,
        # in the rules section and in any other section it reads.
        (dict(skill=SKILL_MD.replace("(`references/secrets.md`)", "(references/secrets.md)")),
         "holds a references/ path outside the `references/<file>` code-span form"),
        (dict(skill=SKILL_MD.replace("in `references/mfa.md` and", "in references/mfa.md and")),
         "holds a references/ path outside the `references/<file>` code-span form"),
        # An always-on.md that does not end in a closing paragraph after its rules is refused.
        (dict(always="## Rules that apply to every deployment\nApply these:\n\n1. A rule.\n"),
         "does not end in a closing paragraph"),
        # An index with no category or no guide row is refused.
        (dict(readme="# Fixture\n\n## Guide index\n\nNo table here.\n"),
         "yielded 0 categories and 0 guide rows"),
        (dict(readme=README_MD.replace("## Guide index", "## Guides")),
         "has 0 lines '## Guide index'"),
        # A guide-index row that matches neither the row pattern nor the table frame is
        # refused, not dropped.
        (dict(readme=README_MD.replace("| [nginx.md](nginx.md) | nginx: TLS, redirect, HSTS |",
                                       "| [nginx.md](other.md) | nginx: TLS, redirect, HSTS |")),
         "guide-index row this build cannot read"),
    )
    for changes, needle in cases:
        with tempfile.TemporaryDirectory() as directory:
            root = tree(Path(directory), **changes)
            status, output = run(root)
            assert status != 0 and needle in output, (needle, status, output)
            assert not (root / OUT).exists(), f"a refused build wrote {OUT}"
            count += 1

    print(f"  ok    {count} recorded cases for the chat fallback build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
