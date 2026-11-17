#!/usr/bin/env bash
# Regenerates site/secureconfig-instructions.md, the chat fallback file: the rules and the guide
# index in one small file an assistant reads where the secureconfig skill is not installed. The
# file carries no guide content; it tells the assistant to fetch the one guide a deployment
# needs, raw from the repository or through https://secureconfig.ai/llms-full.txt, or to ask the
# user to attach it, so the guide that is applied is always the published one, never a stale
# copy frozen in this file.
#
# Run from the repository root after changing any of the 4 SKILL.md sections named in SECTIONS
# below, plugin/always-on.md's closing paragraph or README.md's "## Guide index" section.
# `--check` builds in memory and compares with the committed file, writing nothing, so the
# staleness gate in tools/run_all_checks.sh can run it without rewriting the working tree.
set -euo pipefail

cd "$(dirname "$0")/.."
out="site/secureconfig-instructions.md"

if [ "$#" -gt 1 ]; then
  echo "scripts/build-instructions.sh: $# arguments given; this build takes --list-inputs, --check or no argument" >&2
  exit 1
fi

# Say what we build from, so the generated-file record in .aiqt/gensrc.json does not have to
# work it out. As in scripts/build-llms-full.sh, anything that changes this list has to happen
# ABOVE this block, or the list reported here would not be the list built from below.
inputs=(plugin/skills/secureconfig/SKILL.md plugin/always-on.md README.md)
if [ "${1:-}" = "--list-inputs" ]; then
  printf '%s\n' "${inputs[@]}"
  exit 0
fi

# The whole build, standard library only, so it runs wherever the gates run and needs no
# network and no installed package. It reads the 3 inputs listed above and nothing else:
#   - the 4 SKILL.md sections named in SECTIONS, the rules among them, with each code-span
#     `references/<file>` path rewritten to the bare `<file>`, because a chat reader has no
#     references/ folder; a references/ path left in any other form fails the build rather
#     than shipping unresolved;
#   - plugin/always-on.md's closing paragraph only, the pointer line after its rules that
#     SKILL.md's rules section does not carry, placed after the rules here too;
#   - README.md's "## Guide index" section, re-emitted as one `- <file>: <covers>` line per
#     guide under its category heading, so the reader can name the guide to fetch or request.
# The fetch section and the framing lines are written here. A missing or repeated section, an
# index with no category or no guide row, an index row the build cannot read, or a site/
# folder it cannot write into, fails the build with the input or path named.
IFS= read -r -d '' build <<'PY' || true
import re
import sys

SKILL = "plugin/skills/secureconfig/SKILL.md"
ALWAYS = "plugin/always-on.md"
README = "README.md"
NAME = "scripts/build-instructions.sh"
# The SKILL.md sections this build carries, in SKILL.md's own order. The rules are read from
# SKILL.md itself, so the guide routes its rules 2, 5, 7 and 8 name survive into this file,
# rewritten like every other references/ span, and the rules here cannot drift from the
# skill's. plugin/always-on.md, the hand-kept snippet of that section, contributes only its
# closing paragraph, the pointer line SKILL.md's rules section does not carry.
RULES = "## Rules that apply to every deployment"
SECTIONS = (RULES,
            "## Verify steps are the point, not the configuration",
            "## Choosing guides",
            "## What this skill does not do")
# A README guide-index row, as scripts/build-site.py reads one.
GUIDE_ROW = re.compile(r"^\| \[([a-z0-9.-]+)\.md\]\(\1\.md\) \| (.+) \|$")
# An unescaped pipe in a row's Covers text starts a third column, which this build cannot read.
CELL_PIPE = re.compile(r"(?<!\\)\|")
# The index's table frame: its header row and its separator row carry no guide.
TABLE_HEAD = "| Guide | Covers |"
TABLE_RULE = re.compile(r"\|[-: ]+\|[-: ]+\|")

HEAD = """\
# secureconfig instructions for AI assistants

> Generated from https://github.com/jposluns/secureconfig by scripts/build-instructions.sh \
(Apache-2.0; see LICENSE and NOTICE there. Versions before 1.0.1341 are CC0 1.0). Do not edit \
this file by hand.
> Per-guide index with fetch links: https://secureconfig.ai/llms.txt . Every guide in one \
file: https://secureconfig.ai/llms-full.txt .

This file is the chat fallback for the secureconfig skill: attach it to a conversation where \
that skill is not installed. It holds the rules that apply to every deployment and the index \
of every guide, and no guide content, so the guide a deployment needs is read fresh and never \
goes stale inside this file. Apply the rules below to every service you configure, generate \
or review, choose every guide that fits from the index at the end, and read each one as \
"Fetching a guide" says, or ask the user to attach it."""

FETCH = """\
## Fetching a guide

Each guide in the index below is one Markdown file at the repository root. Fetch it raw from \
`https://raw.githubusercontent.com/jposluns/secureconfig/main/<guide>.md`, with the guide's \
file name in place of `<guide>`. If raw.githubusercontent.com is unreachable, use \
https://secureconfig.ai/llms-full.txt, which holds every guide; a guide's text is the section \
that starts with a line such as `==> nginx.md` between two lines of `=` characters. If you \
cannot fetch at all, ask the user to attach the guide's file, naming it from the index below."""


def fail(message):
    sys.exit(f"{NAME}: {message}")


def read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        fail(f"cannot read {path}: {exc}")


def section(lines, heading, name):
    """A level-2 section, heading included, to the next level-2 heading, trailing blanks cut."""
    starts = [i for i, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        fail(f"{name} has {len(starts)} lines {heading!r}; this build reads exactly 1 such "
             f"section")
    end = next((i for i in range(starts[0] + 1, len(lines)) if lines[i].startswith("## ")),
               len(lines))
    while end > starts[0] and not lines[end - 1].strip():
        end -= 1
    return lines[starts[0]:end]


def closing_paragraph(text):
    """plugin/always-on.md's closing paragraph: the pointer line after its rules, the one part
    of that file SKILL.md's rules section does not carry."""
    paragraphs = [p for p in re.split(r"\n[ \t]*\n", text.strip("\n")) if p.strip()]
    last = paragraphs[-1] if paragraphs else ""
    if len(paragraphs) < 2 or last.lstrip().startswith("#") or re.match(r"[0-9]+\.",
                                                                        last.lstrip()):
        fail(f"{ALWAYS} does not end in a closing paragraph after its rules; this build "
             f"carries only that paragraph")
    return last


def guide_index(lines):
    """README.md's guide index as `- <file>: <covers>` lines under its category headings."""
    out, categories, rows = ["## Guide index"], 0, 0
    for line in section(lines, "## Guide index", README)[1:]:
        if line.startswith("### "):
            out += ["", f"### {line[4:].strip()}", ""]
            categories += 1
        elif (match := GUIDE_ROW.match(line)) and not CELL_PIPE.search(match.group(2)):
            if not categories:
                fail(f"{README} has a guide-index row before any category heading")
            out.append(f"- `{match.group(1)}.md`: {match.group(2)}")
            rows += 1
        elif "|" in line and line != TABLE_HEAD and not TABLE_RULE.fullmatch(line):
            # Any other line with a pipe may be a table row: an indented one, one with an extra
            # column or one without its leading pipe would be dropped or misread, so each is
            # refused.
            fail(f"{README} has a guide-index row this build cannot read: {line!r}")
    if not categories or not rows:
        fail(f"{README} yielded {categories} categories and {rows} guide rows; this build "
             f"needs at least 1 of each")
    return "\n".join(out)


parts = [HEAD]
skill_lines = read(SKILL).split("\n")
for heading in SECTIONS:
    body = "\n".join(section(skill_lines, heading, SKILL))
    # A chat reader has no references/ folder, so each code-span path such as
    # `references/mfa.md` becomes the bare `mfa.md` the fetch section resolves. Any other
    # spelling of a references/ path would ship unresolved, so it is refused instead.
    body = body.replace("`references/", "`")
    if "references/" in body:
        fail(f"{SKILL} section {heading!r} holds a references/ path outside the `references/"
             f"<file>` code-span form, the only form this build rewrites")
    parts.append(body)
    if heading == RULES:
        parts.append(closing_paragraph(read(ALWAYS)))
parts += [FETCH, guide_index(read(README).split("\n"))]
text = "\n\n".join(parts) + "\n"

out, mode = sys.argv[1], sys.argv[2]
if mode == "--check":
    try:
        with open(out, "rb") as handle:
            committed = handle.read()
    except FileNotFoundError:
        print(f"  FAIL  {out} is missing; run bash {NAME} and commit the result")
        sys.exit(1)
    except OSError as exc:
        print(f"  FAIL  cannot read {out}: {exc}")
        sys.exit(2)
    if committed != text.encode("utf-8"):
        print(f"  FAIL  {out} is stale; run bash {NAME} and commit the result")
        sys.exit(1)
    print(f"  ok    {out} matches a fresh build of its sources ({len(text)} characters)")
elif mode == "":
    try:
        with open(out, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    except OSError as exc:
        fail(f"cannot write {out}: {exc}")
    print(f"wrote {out} ({len(text)} characters)")
else:
    fail(f"unknown argument {mode!r}; this build takes --list-inputs, --check or no argument")
PY

python3 -I -c "$build" "$out" "${1:-}"
