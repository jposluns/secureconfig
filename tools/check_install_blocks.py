#!/usr/bin/env python3
"""Check that the site build reads README.md's install section as CommonMark does.

scripts/build-site.py takes the Claude Code install commands on the For AI assistants page from
README.md's "Install in Claude Code" section with install_blocks(), a small standard-library fence
reader, because the Cloudflare Pages build (scripts/pages-build.sh) that runs it needs only bash
and Python and installs nothing. That reader knows only lines, so an HTML comment or HTML block, an indented code block, a
setext heading, a list or a block quote can make it read a block that CommonMark hides, or miss
one that CommonMark shows. This CI gate reads the same README.md with the pinned CommonMark parser
(gate_parser(required=True) in tools/check_verify_marking.py, pinned by
tools/requirements-gates.txt) and fails unless:

  - install_blocks() accepts the section (its refusal is the finding);
  - the parser finds exactly 1 level-2 heading "Install in Claude Code";
  - from that heading to the next level-1 or level-2 heading, the parser finds exactly as many
    code blocks, fenced or indented and at any depth, as install_blocks() extracted, and each in
    turn is a top-level fence that opens on the line install_blocks() gives, with the same info
    string and the same content.

It compares code blocks only. Commands that raw HTML shows, such as a <pre> element in the
section, are a code block to neither reader, so README.md can show commands that neither the page
nor this gate counts; nothing refuses raw HTML in the section.

Exit 0 when the two readings agree, 1 on a finding, 2 when README.md cannot be read or the parser
is absent, not the pinned version or cannot be loaded (1 FAIL line naming the cause, never a
traceback). Its cases are in tools/test_install_blocks.py. The standard library and the pinned
markdown-it-py. No network.
"""
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from check_verify_marking import ParserUnavailable, gate_parser  # noqa: E402  (the pinned parser)

spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build-site.py")
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)
WHERE = "README.md section 'Install in Claude Code'"
INFO = {key: info for key, info, _ in build_site.INSTALL_FENCES}  # each block's info string


def starts(lines):
    """'blocks (first lines 57, 64)' for a list of first lines, in the singular for 1."""
    if not lines:
        return "blocks"
    word = "block (first line" if len(lines) == 1 else "blocks (first lines"
    return f"{word} {', '.join(str(n) for n in lines)})"


def compare(text, parser):
    """(findings, blocks): how the parser's reading of the install section in text differs from
    install_blocks()'s, and the blocks install_blocks() extracted ([] when it refused)."""
    try:
        blocks = build_site.install_blocks(text)
    except build_site.SourceError as exc:
        return [f"scripts/build-site.py refuses README.md: {exc}"], []
    tokens = parser.parse(text)
    title = build_site.INSTALL[3:]
    heads = [i for i, t in enumerate(tokens) if t.type == "heading_open" and t.tag == "h2"
             and tokens[i + 1].content.strip() == title]
    if len(heads) != 1:
        return [f"the pinned parser finds {len(heads)} level-2 headings {title!r} in README.md, "
                f"where scripts/build-site.py reads 1"], blocks
    end = next((i for i in range(heads[0] + 1, len(tokens)) if tokens[i].type == "heading_open"
                and tokens[i].tag in ("h1", "h2")), len(tokens))
    parsed = [t for t in tokens[heads[0]:end] if t.type in ("fence", "code_block")]
    if len(parsed) != len(blocks):
        return [f"{WHERE}: the pinned parser finds {len(parsed)} code "
                f"{starts([t.map[0] + 1 for t in parsed])}, where scripts/build-site.py reads "
                f"{len(blocks)} {starts([line for _, line, _ in blocks])}"], blocks
    findings = []
    for n, (token, (key, line, body)) in enumerate(zip(parsed, blocks), 1):
        info = INFO[key]
        content = token.content[:-1] if token.content.endswith("\n") else token.content
        got = (token.type, token.level, token.map[0] + 1, token.info.strip(), content)
        if got != ("fence", 0, line, info, body):
            findings.append(f"{WHERE}: code block {n} is, to the pinned parser, a {token.type} at "
                            f"depth {token.level} from line {token.map[0] + 1} with info string "
                            f"{token.info.strip()!r} and content {content!r}; "
                            f"scripts/build-site.py reads a top-level fence from line {line} with "
                            f"info string {info!r} and content {body!r}")
    return findings, blocks


def main():
    try:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot read README.md: {exc}")
        return 2
    try:
        parser = gate_parser(required=True)
    except ParserUnavailable as exc:
        print(f"  FAIL  {WHERE} is checked with the pinned parser: {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001  any failure to load the parser leaves it unchecked
        # A lock that cannot be read or parsed, or a markdown_it package without the version
        # metadata of markdown-it-py or mdurl, raises something other than ParserUnavailable.
        cause = " ".join(f"{type(exc).__name__}: {exc}".split())
        print(f"  FAIL  {WHERE} is checked with the pinned parser, which cannot be loaded from "
              f"tools/requirements-gates.txt and the installed markdown-it-py and mdurl: {cause}")
        return 2
    findings, blocks = compare(text, parser)
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {WHERE}: the pinned parser finds the {len(blocks)} fenced blocks "
          f"scripts/build-site.py reads, from lines "
          f"{' and '.join(str(line) for _, line, _ in blocks)}, with the same info strings and "
          f"content")
    return 0


if __name__ == "__main__":
    sys.exit(main())
