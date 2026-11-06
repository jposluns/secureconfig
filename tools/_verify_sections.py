"""Guide selection and verification roots shared by the offline gates.

Only whole canonical titles (optionally numbered) open a root. Descendants
belong to that root, including headings that happen to contain "verify".
Legacy parenthesized status suffixes remain section titles, not declarations.
"""
import html
import re
import sys
from pathlib import Path

from _markdown import Fences

TITLE = re.compile(
    r"(?i)^(?:[0-9]+[.)][ \t]+)?"
    r"(?:Verify|Verification checklist|Quick checks)$"
)
STATUS = r"(?:\*\*|__)?(?:DEMONSTRATED|REASONED)(?:\*\*|__)?"
SUFFIX = re.compile(r"(?i)^(.*?)[ \t]*([(:])[ \t]*(" + STATUS + r"\b.*)$")
LEGACY = re.compile(r"(?i)^" + STATUS + r"$")


def heading_parts(title):
    """Return (base title, declaration, error) using one suffix grammar.

    Recognize the status introducer even if its suffix is malformed, so a bad
    declaration cannot make a Verify root disappear. Parenthesized declarations
    must end the title. Legacy bare statuses select roots but do not mark fences.
    Validation is reported only when a fence uses the heading.
    """
    title = title_text(title)
    match = SUFFIX.fullmatch(title)
    if not match:
        return title, None, None
    base, delimiter, suffix = match.groups()
    if delimiter == "(":
        depth = 1
        for i, char in enumerate(suffix):
            depth += (char == "(") - (char == ")")
            if depth == 0 and i != len(suffix) - 1:
                break
        if depth != 0 or i != len(suffix) - 1:
            return base.rstrip(), None, "heading declaration must be a complete suffix"
        suffix = suffix[:-1].rstrip()
    if LEGACY.fullmatch(suffix):
        return base.rstrip(), None, None
    return base.rstrip(), suffix, None


def title_text(title):
    """Remove optional ATX closing hashes; normalize horizontal whitespace."""
    title = re.sub(r"[ \t]+#+[ \t]*$", "", title)
    return re.sub(r"[ \t]+", " ", title.strip(" \t"))


def verify_ranges(heads):
    """Yield disjoint [start, end) ranges from fence-aware (level, title) heads."""
    i = 0
    while i < len(heads):
        head = heads[i]
        if not head or not TITLE.fullmatch(heading_parts(head[1])[0]):
            i += 1
            continue
        end = i + 1
        while end < len(heads):
            if heads[end] and heads[end][0] <= head[0]:
                break
            end += 1
        yield i, end
        i = end


# Keep the guide exclude set aligned with not_a_guide() in run_all_checks.sh.
META_EXCLUDE = frozenset({
    "CONTRIBUTING.md", "SECURITY.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md",
    "README.sources.md", "TODO.md", "DONE.md", "DECISIONS.md",
    "PENDING-DECISIONS.md", "controls-reference.md",
})


HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")


def guides(root: Path):
    """Yield each root-level guide path, sorted, meta files excluded.

    A guide is a regular file at the root whose name ends in ".md" and does not start with ".",
    as the shell glob *.md matches it, so neither a dot-named file nor a directory is a guide.
    """
    for path in sorted(p for p in root.iterdir()
                       if p.suffix == ".md" and not p.name.startswith(".") and p.is_file()):
        if path.name not in META_EXCLUDE:
            yield path


def counted_guides(root: Path):
    """The names of the guides that README.md and SKILL.md count: guides() less README.md.

    The guide-counts gate in tools/run_all_checks.sh reads this list by running this module,
    and scripts/build-plugin.sh and tools/check_generated_committed.py call this function, so
    the three counts have one definition.
    """
    return [path.name for path in guides(root) if path.name != "README.md"]


SKILL_COUNT = re.compile(r"This skill carries ([0-9]+) short guides")
# Inside a raw HTML block, which the parser passes through unparsed: a comment runs from "<!--" to
# the next "-->" or "--!>", or to the end of the block when neither follows, and "<!-->" and
# "<!--->" are empty comments, as an HTML parser reads them. A tag, declaration or processing
# instruction runs to the next ">". None of them shows text.
HTML_COMMENT = re.compile(r"<!---?>|<!--.*?(?:--!?>|\Z)", re.S)
HTML_TAG = re.compile(r"<[A-Za-z/?!][^>]*>")


def front_matter(text):
    """Split SKILL.md into (front matter, body): lines 1 to the next "---" line when line 1 is
    "---", the scope scripts/build-plugin.sh rewrites; ("", text) when there is none."""
    lines = text.split("\n")
    if lines[0] == "---" and "---" in lines[1:]:
        end = lines.index("---", 1) + 1
        return "\n".join(lines[:end]), "\n".join(lines[end:])
    return "", text


def visible_text(tokens):
    """The text a reader sees in parsed Markdown tokens, less HTML comments, with a NUL between
    blocks.

    The parser decides what is code, a comment or text, so a "<!--" in a code span, in a fenced or
    indented code block (in a block quote or list item too) or after a backslash is literal text.
    Code is kept, since a reader sees it. An inline HTML token (a tag, comment, declaration or
    processing instruction) shows nothing and is dropped. A raw HTML block keeps its text less
    HTML_COMMENT and HTML_TAG matches, with character references decoded. Emphasis, links and
    inline code join the text around them, a line break is a newline, and an image keeps its alt
    text.
    """
    parts = []
    for token in tokens:
        if token.type in ("text", "text_special", "code_inline", "code_block", "fence"):
            parts.append(token.content)
        elif token.type in ("softbreak", "hardbreak"):
            parts.append("\n")
        elif token.type == "html_block":
            parts.append(html.unescape(HTML_TAG.sub("", HTML_COMMENT.sub("", token.content))))
        elif token.children:
            parts.append(visible_text(token.children))
        if token.block:
            parts.append("\0")
    return "".join(parts)


def skill_counts(text):
    """The N of each "This skill carries N short guides" a reader of SKILL.md sees.

    The body is parsed with the pinned CommonMark parser, gate_parser(required=True) in
    tools/check_verify_marking.py, and searched in visible_text(); the front matter, which is not
    Markdown, is searched as it stands. Each run of whitespace is read as 1 space, as a rendered
    page shows it, so a sentence wrapped within one block counts; one split across blocks does
    not. ParserUnavailable is raised when that parser is absent or not the pinned version.
    scripts/build-plugin.sh and tools/check_generated_committed.py each require exactly one, so a
    commented copy neither counts nor stands in for a stale or missing visible sentence.
    """
    from check_verify_marking import gate_parser  # here, as that module imports this one
    parser = gate_parser(required=True)
    head, body = front_matter(text)
    visible = head + "\0" + visible_text(parser.parse(body))
    return SKILL_COUNT.findall(re.sub(r"\s+", " ", visible))


def atx_headings(lines):
    """Return a list parallel to `lines`: (level, title) for each line that is an ATX
    heading OUTSIDE a fenced code block, else None.

    Code fences are tracked with _markdown.Fences (this repository's one CommonMark fence
    definition) so a `# comment` or a `## Verify` EXAMPLE inside a ``` or ~~~ block is not
    mistaken for a heading, and neither an opening nor a closing fence marker line is a
    heading. Fences reuses the shared rules -- an opening fence is indented no more than
    three spaces and a backtick fence carries no backtick in its info string -- so indented
    code and inline code spans are not misread as fences. An absent ATX title (an empty
    heading such as a bare `##`) normalizes to the empty string.
    """
    fences = Fences()
    out = []
    for line in lines:
        if fences.feed(line):
            out.append(None)  # a fence marker line is neither heading nor content
            continue
        if fences.inside:
            out.append(None)
            continue
        m = HEADING.match(line)
        out.append((len(m.group(1)), m.group(2) or "") if m else None)
    return out


def verify_sections_text(text: str) -> str:
    """Concatenate disjoint canonical Verify roots, including their descendants.

    The shared selector includes Verification checklist and Quick checks, optional
    numbering and status suffixes. Setup headings merely mentioning verify do not
    start roots. Including the title retains detection of heading markers.
    """
    lines = text.split("\n")
    heads = atx_headings(lines)
    return "\n".join(
        "\n".join([heads[start][1], *lines[start + 1:end]])
        for start, end in verify_ranges(heads)
    )


if __name__ == "__main__":
    # `python3 tools/_verify_sections.py [ROOT]` prints counted_guides(ROOT), one name per line,
    # for the shell gates; ROOT defaults to the current directory.
    for name in counted_guides(Path(sys.argv[1] if len(sys.argv) > 1 else ".")):
        print(name)
