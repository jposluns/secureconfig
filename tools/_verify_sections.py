"""Guide selection and verification roots shared by the offline gates.

Only whole canonical titles (optionally numbered) open a root. Descendants
belong to that root, including headings that happen to contain "verify".
Legacy parenthesized status suffixes remain section titles, not declarations.
"""
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
HTML_SPACE = " \t\n\f\r"


class SkillHtml(ValueError):
    """SKILL.md's body holds HTML other than whole HTML comments that stand as HTML blocks of
    their own outside any list item or block quote, or such a comment whose source lines are not
    its text as the parser read it, so skill_counts() cannot find the count sentence."""


def whole_comment(raw):
    """Whether raw, less surrounding whitespace, is exactly one whole HTML comment.

    The parser passes raw HTML through unread, so this does not decide what an HTML parser would
    show; it accepts only the one shape whose text plainly shows nothing: "<!--" first, "-->"
    last, and no earlier "-->" or "--!>", either of which ends a comment in HTML. The abrupt
    "<!-->" and "<!--->" end where they open, so they are refused too.
    """
    text = raw.strip(HTML_SPACE)
    if not text.startswith("<!--") or text.startswith(("<!-->", "<!--->")):
        return False
    ends = [at for at in (text.find("-->", 4), text.find("--!>", 4)) if at >= 0]
    return bool(ends) and min(ends) == len(text) - 3


def front_matter(text):
    """Split SKILL.md into (front matter, body): lines 1 to the next "---" line when line 1 is
    "---", the scope scripts/build-plugin.sh rewrites; ("", text) when there is none."""
    lines = text.split("\n")
    if lines[0] == "---" and "---" in lines[1:]:
        end = lines.index("---", 1) + 1
        return "\n".join(lines[:end]), "\n".join(lines[end:])
    return "", text


def skill_counts(text):
    """The N of each "This skill carries N short guides" in SKILL.md, front matter included,
    outside the whole HTML comments that stand as HTML blocks of their own in its body: in its
    text and code, in link and image destinations and titles, in reference labels and
    definitions, in fence info strings, and in the front matter.

    The sentence is searched for in the raw source, as the regex this replaced searched the file
    with comments removed, so every copy that stands in the file outside such a comment counts.
    The front matter is not parsed and nothing in it is removed, so a copy there counts even
    inside "<!--" and "-->", which fails closed. Only which lines are a comment is taken from the
    pinned CommonMark parser, gate_parser(required=True) in tools/check_verify_marking.py, which
    parses the body: a "<!--" in code, in a link destination, title or label, or after a
    backslash is not an HTML token, so it hides nothing. Raw HTML, which the parser passes
    through unread, is not read. The body may hold HTML only as HTML blocks at nesting level 0,
    so in no list item or block quote, each of them one whole HTML comment as whole_comment()
    accepts it. Any inline HTML token, children included, any HTML block in a list item or block
    quote, and any HTML block that is not one whole comment raise SkillHtml, naming the first
    line of the block, or the table row, that holds it, not the line of the HTML itself. Each
    accepted comment is removed by blanking exactly the source lines the parser maps it to, after
    confirming that those lines, joined, are the token's text, or SkillHtml is raised. Each run
    of whitespace in what remains is read as 1 space, so a sentence wrapped within a block
    counts, and so does one split across blocks. ParserUnavailable is raised when that parser is
    absent or not the pinned version. scripts/build-plugin.sh and
    tools/check_generated_committed.py each require exactly one, so a copy in a removed comment
    neither counts nor stands in for a stale or missing sentence.
    """
    from check_verify_marking import gate_parser  # here, as that module imports this one
    parser = gate_parser(required=True)
    head, body = front_matter(text)
    first_line = head.count("\n") + 2 if head else 1
    # The parser reads "\r\n" and "\r" as "\n" and NUL as U+FFFD before it parses, so the same is
    # done here, and its line numbers and token text then match these lines.
    body = re.sub(r"\r\n?", "\n", body).replace("\0", "\ufffd")
    lines = body.split("\n")

    def walk(tokens, block):
        for token in tokens:
            if token.type == "html_inline" or (token.type == "html_block" and (
                    token.level != 0 or not whole_comment(token.content))):
                # An inline token's map is its block's lines, and a table cell's is its row's.
                where = token.map if token.type == "html_block" else block
                raise SkillHtml(f"raw HTML in the block, or the table row, starting at line "
                                f"{first_line + where[0]} is not a whole HTML comment in an HTML "
                                "block of its own outside any list item or block quote, the only "
                                "HTML SKILL.md may hold")
            if token.type == "html_block":
                start, end = token.map
                # The block's text is its lines, the last with its line ending when one follows.
                source = "\n".join(lines[start:end]) + ("\n" if end < len(lines) else "")
                if source != token.content:
                    raise SkillHtml(f"the HTML comment block starting at line "
                                    f"{first_line + start} is not its source lines as written, "
                                    "so it cannot be removed")
                lines[start:end] = [""] * (end - start)
            if token.children:
                # An image's alt text has no map, so its image's block is named.
                walk(token.children, token.map or block)

    walk(parser.parse(body), [0, len(lines)])
    rest = "\n".join(lines)
    return SKILL_COUNT.findall(re.sub(r"\s+", " ", (head + "\n" if head else "") + rest))


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
