#!/usr/bin/env python3
"""Cases for check_draft.py at the root: each way the published site could stop being
self-contained, or its indexability could silently change.

Each failing case copies the real site/ tree, makes 1 change and asserts that the gate exits 1
with a message naming the defect; each passing case makes a change the gate must accept (the
pristine copy among them). A mutation that no longer applies RAISES, so a page edit cannot turn a
case into a pristine run.

The staged-era /draft/* header rule retired with the staging it policed. What carried over is
retargeted to the generated pages at the root: the robots-meta reading (now on the /draft/ review
page and the 404, with every other page carrying none), every URL-shape refusal (a
browser-normalized host, a trailing-dot, upper-case, percent-encoded or non-ASCII host, a Pages
alias, https:/// and scheme-relative spellings, a backslash, whitespace, javascript:), the URL
attributes beyond href and src, http-equiv, the new-tab hint, site/_redirects, CSS @import and
url() containment and the site.css grammar. New at the root: a root-relative link must name a file
under site/; each canonical is its page's own URL (exactly 1 on the 7 indexable pages and the
review page, none on the 404); the "no page links /draft/" and Disclosure and Licence rules compare
the resolved target file, so a query, an extra slash, a dot segment (plain or percent-encoded), a
percent-encoded letter or a fragment does not get past them; and the published indexes are read
by a fail-closed rule after percent-decoding and character-reference decoding (at most 8 rounds),
NFKC, case folding, `\\` read as `/` and tab and CR deleted: site/llms.txt, site/robots.txt and
site/.well-known/security.txt are refused for any literal `draft` (relative, Disallow, bold,
host-only, www, href=, backslash, 1-slash, .html, character-reference, tab and CR spellings among
the cases) and accept "Raft consensus and Raft logs", and site/llms-full.txt for each form of the
draft path (character references, a tab or CR character reference inside the path, bare Markdown
link destinations, reference definitions, HTML attribute values, a link broken across a line end,
a link broken inside a blockquote, a reference definition whose destination is on the next line,
whose label spans 2 lines, or that sits in a blockquote or a list item, and 1 case each for forms
b, d and e that only that form catches), while its prose ("drafting", "drafted", "a draft.",
"the draft's", "draft / final", "and Raft", "Choose draft" wrapped before "/ final wording." in
the text and in a link title, "draft-ietf-oauth-v2-1", a datatracker draft URL and a description
meta saying "draft") is accepted. A 9-times percent-encoded path exceeds the round limit and is
refused. Each refusal names the file and line, counted by `\\n` only (a U+2028 or a `\\r` ends no
line, and llms-full.txt written with `\\r\\n` line endings reports a reference on line 2 as
line 2). The edit, append, prepend and crlf mutations read and write bytes, so they translate no
newline. A second robots meta whose first name attribute is robots is read by that first name, as
a browser reads it.

The generated() cases keep the source-to-generated-page path: a Unicode host written in
content.json survives the build and its own --check and is refused by this gate, and a site.css
setting only the 2 per-site constants is accepted by the build and the gate.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent


def run(mutate=None):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / "site", d / "site")
        if mutate is not None:
            mutate(d)
        r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "check_draft.py"), "--root",
                            str(d)], capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edit(rel, old, new):
    """The first old in rel replaced with new, read and written as bytes (no newline translation)."""
    def mutate(d):
        path = d / rel
        data, old_b = path.read_bytes(), old.encode("utf-8")
        if old_b not in data:
            raise AssertionError(f"mutation {old!r} no longer matches {rel}")
        path.write_bytes(data.replace(old_b, new.encode("utf-8"), 1))
    return mutate


def write(rel, text):
    def mutate(d):
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return mutate


HOME = "site/index.html"
GUIDES = "site/guides/index.html"
REVIEW = "site/draft/index.html"
P404 = "site/404.html"
META = '<meta name="robots" content="noindex, nofollow">'
START = 'href="/guides/"'
OK_LINE = "9 pages are self-contained"
STRAY = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>x</title>\n'
         '</head>\n<body><a href="/nowhere/">gone</a></body>\n</html>\n')


def append(rel, text):
    """text added at the end of an existing file, read and written as bytes."""
    def mutate(d):
        path = d / rel
        if not path.is_file():
            raise AssertionError(f"mutation target {rel} does not exist")
        path.write_bytes(path.read_bytes() + text.encode("utf-8"))
    return mutate


def link(value):
    """The home page's first /guides/ link pointed at value."""
    return edit(HOME, START, f'href="{value}"')


def guides_link(value):
    """A link to value planted in the Guides page's top bar, before its For AI assistants link."""
    return edit(GUIDES, '<a href="/for-ai/">', f'<a href="{value}">x</a><a href="/for-ai/">')


def prepend(rel, text):
    """text added at the start of an existing file, read and written as bytes."""
    def mutate(d):
        path = d / rel
        if not path.is_file():
            raise AssertionError(f"mutation target {rel} does not exist")
        path.write_bytes(text.encode("utf-8") + path.read_bytes())
    return mutate


def crlf(rel, second):
    """rel with every line ending written `\\r\\n` and second inserted as its line 2."""
    def mutate(d):
        path = d / rel
        data = path.read_bytes()
        lines = data.split(b"\n")
        if len(lines) < 2 or b"\r" in data:
            raise AssertionError(f"{rel} has fewer than 2 lines or already carries a CR")
        lines.insert(1, second.encode("utf-8"))
        path.write_bytes(b"\r\n".join(lines))
    return mutate


def refused_at(rel, after=0):
    """The start of the gate's PART 3 finding for a match on the first line appended to rel, or
    `after` lines below it: its file and line, with lines counted by `\\n` only, as the gate counts
    them."""
    text = (ROOT / rel).read_bytes().decode("utf-8")
    if not text.endswith("\n"):
        raise AssertionError(f"{rel} does not end with a newline, so an appended line joins its last")
    n = text.count("\n") + 1 + after
    return f"{rel}:{n}: the published-index rule refuses"


# Each spelling of the /draft/ path planted in each published index (PART 3 of the gate).
DRAFT_SPELLINGS = ("/draft/", "/Draft/", "/%64raft/", "https://secureconfig.ai/draft")
INDEX_LINES = {
    "site/llms.txt": "- [Review]({}): the next version\n",
    "site/llms-full.txt": "The next version is staged at {} for review.\n",
    "site/robots.txt": "Disallow: {}\n",
}
# The spellings the token rule missed, and the corpus forms of the fail-closed rule.
REFUSED_LINES = {
    "site/llms.txt": (
        "- [Review](draft/): the next version\n",
        "- [Review](./draft/): the next version\n",
        "Disallow:/draft/\n",
        "- **https://secureconfig.ai/draft/**: the next version\n",
        "- The next version: secureconfig.ai/draft/\n",
        "- The next version: www.secureconfig.ai/draft/\n",
        "- <a href=/draft/>Review</a>\n",
        "- The next version: https:\\\\secureconfig.ai\\draft\\\n",
        "- The next version: https:/secureconfig.ai/draft/\n",
        "- [Review](/draft.html): the next version\n",
        "- Draft review: the next version\n",
        "- [Review](/&#100;raft/): the next version\n",
        "- The next version: dr&#97;ft/\n",
        # A tab or CR inside the path, which a browser deletes from a URL and the gate deletes.
        "- [Review](/dr&#9;aft/): the next version\n",
        "- [Review](/dr&#13;aft/): the next version\n",
    ),
    "site/robots.txt": ("Disallow: draft/\n", "Disallow:/draft/\n", "Disallow: \\draft\\\n"),
    "site/.well-known/security.txt": ("Policy: https://secureconfig.ai/draft/\n",),
    "site/llms-full.txt": (
        "The next version is staged at ./draft/ for review.\n",
        "The next version is staged [x](draft) for review.\n",
        "The next version is staged at secureconfig.ai/draft/ for review.\n",
        "The next version is staged at %2Fdraft%2F for review.\n",
        "The next version is staged at /draft.html for review.\n",
        "The next version is staged [Review](/&#100;raft/) for review.\n",
        "The next version is staged at dr&#97;ft/ for review.\n",
        "The next version is staged [Review](draft \"Draft review\") for review.\n",
        "The next version is staged [Review](<draft>) for review.\n",
        "The next version is staged [Review](draft#top) for review.\n",
        "The next version is staged [Review](draft?review=1) for review.\n",
        "The next version is staged [Review](draft.html) for review.\n",
        "The next version is staged [x](\ndraft) for review.\n",
        "The next version is staged at \\draft\\ for review.\n",
        # 8 times percent-encoded: decoded within the round limit, then refused by its form.
        "The next version is staged at %" + "25" * 7 + "2Fdraft%" + "25" * 7 + "2F for review.\n",
        # A tab or CR inside the path, which a browser deletes from a URL and the gate deletes.
        "The next version is staged at /dr&#9;aft/ for review.\n",
        "The next version is staged at /dr&#13;aft/ for review.\n",
    ),
}
# The llms-full.txt cases that only 1 corpus form catches (DRAFT_REFS a to e in the gate), each
# with that form's letter and how many lines below the first appended line its match starts;
# main() asserts that no other form matches. The reference definition follows a blank line, so it
# is a definition and not a paragraph continuation.
SINGLE_FORM = (
    ("The next version: see draft/notes for review.\n", "b", 0),
    ("\n[review]: draft\n", "d", 1),
    ('The next version is staged <a href="draft">here</a>.\n', "e", 0),
)
# Ordinary Markdown that forms c and d read across a line end or a blockquote or list marker, each
# with how many lines below the first appended line its match starts: a reference definition (after
# a blank line) whose destination is on the next line, whose label spans 2 lines, or that sits in a
# blockquote or a list item, and an inline link broken inside a blockquote.
MARKDOWN_FORMS = (
    ("\n[review]:\n  draft\n", 1),
    ("\n[review\nnotes]: draft\n", 2),
    ("\n> [review]: draft\n", 1),
    ("\n- [review]: draft\n", 1),
    ("> The next version is staged [x](\n> draft) for review.\n", 0),
)
INDEX_CASES = [(f"{rel[5:]} naming {spelling}", append(rel, line.format(spelling)),
                refused_at(rel), 1)
               for rel, line in INDEX_LINES.items() for spelling in DRAFT_SPELLINGS]
INDEX_CASES += [(f"{rel[5:]} carrying {line.strip()!r}", append(rel, line), refused_at(rel), 1)
                for rel, lines in REFUSED_LINES.items() for line in lines]
INDEX_CASES += [(f"llms-full.txt carrying {line.strip()!r}", append("site/llms-full.txt", line),
                 refused_at("site/llms-full.txt", after), 1)
                for line, *_, after in (*SINGLE_FORM, *MARKDOWN_FORMS)]
# 9 times percent-encoded: still changing after the 8-round limit, so refused as such.
NINE = "%" + "25" * 8 + "2F"
INDEX_CASES += [("llms-full.txt carrying /draft/ percent-encoded 9 times",
                 append("site/llms-full.txt", f"The next version is staged at {NINE}draft{NINE}.\n"),
                 refused_at("site/llms-full.txt") + " a line still changing after 8 rounds", 1)]
# A U+2028 before the reference on line 1 ends no line, so the finding names line 1.
INDEX_CASES += [("llms-full.txt line 1 carrying a U+2028 before /draft/",
                 prepend("site/llms-full.txt",
                         "Staged:\N{LINE SEPARATOR}the next version is at /draft/.\n"),
                 "site/llms-full.txt:1: the published-index rule refuses", 1)]
# `\r\n` line endings throughout: a `\r` ends no line, so a reference on line 2 is reported there,
# and the corpus written that way is still accepted.
INDEX_CASES += [("llms-full.txt with \\r\\n line endings and /draft/ on line 2",
                 crlf("site/llms-full.txt", "The next version is staged at /draft/ for review."),
                 "site/llms-full.txt:2: the published-index rule refuses", 1),
                ("llms-full.txt with \\r\\n line endings",
                 crlf("site/llms-full.txt", "Keep drafting the policy until it is reviewed."),
                 OK_LINE, 0)]
# Guide-corpus prose and draft-ietf names that the llms-full.txt rule accepts.
CORPUS_PROSE = ("Keep drafting the policy until it is reviewed.\n",
                "Read the draft's scope before the policy.\n",
                "OAuth 2.1 is still draft-ietf-oauth-v2-1.\n",
                "OAuth 2.1: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/\n",
                "[draft-ietf-oauth-v2-1]: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/\n",
                "[Drafting notes](/guides/)\n",
                # Prose that names no path: wrapped at a slash (here and in the link title last),
                # spaced around a slash, inflected, at a sentence end, the word Raft, and a
                # description meta.
                "Choose draft\n/ final wording.\n",
                "Mark each section draft / final before the review.\n",
                "The policy was drafted last week.\n",
                "Start from a draft.\n",
                "Keep the gRPC and Raft ports closed.\n",
                '<meta name="description" content="This is a draft.">\n',
                '[x](/guide "Choose draft\n/ final wording.")\n')
INDEX_CASES += [(f"llms-full.txt prose {line.strip()!r}", append("site/llms-full.txt", line),
                 OK_LINE, 0) for line in CORPUS_PROSE]
# The hand-written indexes refuse only the literal word.
INDEX_CASES += [("llms.txt prose 'Raft consensus and Raft logs'",
                 append("site/llms.txt", "- Raft consensus and Raft logs\n"), OK_LINE, 0)]


# (description, mutation, expected text, expected exit)
CASES = [
    ("the review page without the robots meta", edit(REVIEW, META + "\n", ""),
     "must carry exactly 1 robots meta", 1),
    ("the review page with a second robots meta", edit(REVIEW, META, META + META),
     "must carry exactly 1 robots meta", 1),
    ("the review page's robots meta only inside a comment", edit(REVIEW, META, f"<!-- {META} -->"),
     "must carry exactly 1 robots meta", 1),
    ("a second robots meta on the review page, single-quoted, allowing indexing",
     edit(REVIEW, META, META + "<meta name='ROBOTS' content='index, follow'>"),
     "must carry exactly 1 robots meta", 1),
    ("a duplicate name attribute on a second robots meta on the review page, the first being robots",
     edit(REVIEW, META, META + '<meta name="robots" name="x" content="index, follow">'),
     "must carry exactly 1 robots meta", 1),
    ("the review page's robots meta in upper case with other spacing",
     edit(REVIEW, META, '<META NAME="Robots" CONTENT="NOINDEX,NOFOLLOW">'), OK_LINE, 0),
    ("the 404 page without its robots meta", edit(P404, META + "\n", ""),
     "must carry exactly 1 robots meta", 1),
    ("a robots meta on an indexable page", edit(GUIDES, "<title>Guides", META + "\n<title>Guides"),
     "carries a robots meta element", 1),
    ("a link to a page that does not exist", link("/nowhere/"), "names no file", 1),
    ("a ../ path out of site/", link("/../SECURITY.md"), "names no file", 1),
    ("a relative link", link("guides/"), "relative path", 1),
    ("an absolute link to this site's own host", link("https://secureconfig.ai/guides/"),
     "own host", 1),
    ("this site's host with a trailing dot", link("https://secureconfig.ai./"), "own host", 1),
    ("this site's host in upper case", link("HTTPS://SECURECONFIG.AI/"), "own host", 1),
    ("this site's host percent-encoded", link("https://secureconfig%2Eai/"), "own host", 1),
    ("a Pages alias host", link("https://secureconfig.pages.dev/"), "own host", 1),
    ("https:/// with the site's host after it, which a browser opens as the site",
     link("https:///secureconfig.ai/"), "no host right after //", 1),
    ("https: with 1 slash", link("https:/secureconfig.ai/"), "no host right after //", 1),
    ("a backslash in a URL", link("https:\\\\secureconfig.ai/"), "backslash", 1),
    ("a tab inside a URL", link("/gui&#9;des/"), "whitespace", 1),
    ("a javascript: URL", link("javascript:void(0)"), "javascript: scheme", 1),
    ("a scheme-relative URL", link("//example.net/"), "scheme-relative", 1),
    ("an ideographic full stop in the site's host", link("https://secureconfig。ai/"),
     "not plain ASCII", 1),
    ("fullwidth letters in the site's host",
     link("https://ｓｅｃｕｒｅconfig.ai/"), "not plain ASCII", 1),
    ("a percent-encoded non-ASCII host", link("https://secureconfig%E3%80%82ai/"),
     "not plain ASCII", 1),
    ("an xlink:href with a javascript: URL",
     edit(HOME, '<a class="start"', '<svg><a xlink:href="javascript:x()"></a></svg><a class="start"'),
     "xlink:href='javascript:x()' uses the javascript: scheme", 1),
    ("a formaction to a missing file",
     edit(HOME, '<a class="start"', '<button formaction="/x">x</button><a class="start"'),
     "formaction='/x' names no file", 1),
    ("a ping to a missing file", edit(HOME, START, START + ' ping="/guides/ /x"'),
     "ping='/x' names no file", 1),
    ("a srcset candidate naming a missing file",
     edit(HOME, 'alt="A terminal',
          'srcset="/assets/baseline/logos/secureconfig.svg 1x, /x.svg 2x" alt="A terminal'),
     "srcset='/x.svg' names no file", 1),
    ("an imagesrcset naming a missing file",
     edit(HOME, "</head>", '<link rel="preload" as="image" imagesrcset="/x.png 1x">\n</head>'),
     "imagesrcset='/x.png' names no file", 1),
    ("a poster naming a missing file",
     edit(HOME, '<a class="start"', '<video poster="/p.png"></video><a class="start"'),
     "poster='/p.png' names no file", 1),
    ("a background attribute naming a missing file",
     edit(HOME, '<a class="start"', '<table background="/bg.png"></table><a class="start"'),
     "background='/bg.png' names no file", 1),
    ("a meta refresh", edit(HOME, "</head>", '<meta http-equiv="refresh" content="0;url=/">\n</head>'),
     "http-equiv", 1),
    ("a meta refresh on the 404 page",
     edit(P404, "</head>", '<meta http-equiv="refresh" content="0; /x/">\n</head>'), "http-equiv", 1),
    ("a new-tab link without the hidden hint",
     edit(GUIDES, 'free-certificates<span class="vh"> (opens in a new tab)</span>', "free-certificates"),
     "does not say so", 1),
    ("a stray .htm page linking a missing file", write("site/extra.htm", STRAY),
     "site/extra.htm:7: href='/nowhere/' names no file", 1),
    ("a stray .HTML page in a folder, read as a page", write("site/x/Page.HTML", STRAY),
     "site/x/Page.HTML:7: href='/nowhere/' names no file", 1),
    ("a site/_redirects file", write("site/_redirects", "/old / 301\n"),
     "site/_redirects exists", 1),
    ("an inner page linking the Licence page",
     edit(GUIDES, '<a href="/for-ai/">', '<a href="/license/">Licence</a><a href="/for-ai/">'),
     "only the landing page", 1),
    ("an inner page linking the Disclosure page through a dot segment, a query and a fragment",
     guides_link("/guides/../disclosure/index.html?x#y"), "only the landing page", 1),
    ("an inner page linking the Licence page with a percent-encoded letter",
     guides_link("/%6cicense/"), "only the landing page", 1),
    ("a page linking the /draft/ review page",
     edit(HOME, '<a class="start"', '<a href="/draft/">drafts</a><a class="start"'),
     "no page links the /draft/ review page", 1),
    ("a link to /draft/ with a query", link("/draft/?x"), "no page links the /draft/ review page", 1),
    ("a link to /draft/ with an extra slash", link("/draft//"),
     "no page links the /draft/ review page", 1),
    ("a link to /draft/ through a dot segment", link("/guides/../draft/"),
     "no page links the /draft/ review page", 1),
    ("a link to /draft/ through a percent-encoded dot segment", link("/guides/%2e%2e/draft/"),
     "no page links the /draft/ review page", 1),
    ("a link to /draft/ with a percent-encoded letter", link("/%64raft/"),
     "no page links the /draft/ review page", 1),
    ("a link to /draft/index.html with a fragment", link("/draft/index.html#a"),
     "no page links the /draft/ review page", 1),
    ("the review page's canonical on another host",
     edit(REVIEW, 'href="https://secureconfig.ai/draft/"', 'href="https://example.net/draft/"'),
     "is not this page's own URL", 1),
    ("the review page's canonical naming a missing path",
     edit(REVIEW, 'href="https://secureconfig.ai/draft/"', 'href="https://secureconfig.ai/nowhere/"'),
     "is not this page's own URL", 1),
    ("a canonical over plain HTTP",
     edit(REVIEW, 'href="https://secureconfig.ai/draft/"', 'href="http://secureconfig.ai/draft/"'),
     "is not this page's own URL", 1),
    ("the review page's canonical resolving to another page, the home page",
     edit(REVIEW, 'href="https://secureconfig.ai/draft/"', 'href="https://secureconfig.ai/"'),
     "the canonical 'https://secureconfig.ai/' is not this page's own URL", 1),
    ("an indexable page without its canonical",
     edit(GUIDES, '<link rel="canonical" href="https://secureconfig.ai/guides/">\n', ""),
     "site/guides/index.html must carry exactly 1 canonical", 1),
    ("an indexable page with a second canonical, also its own URL",
     edit(HOME, '<link rel="canonical" href="https://secureconfig.ai/">',
          '<link rel="canonical" href="https://secureconfig.ai/">\n'
          '<link rel="canonical" href="https://secureconfig.ai/">'),
     "site/index.html must carry exactly 1 canonical", 1),
    ("a canonical on the 404 page",
     edit(P404, "</head>", '<link rel="canonical" href="https://secureconfig.ai/404.html">\n</head>'),
     "the 404 page carries none", 1),
    *INDEX_CASES,
    ("llms-full.txt prose that merely says draft",
     append("site/llms-full.txt", "Write a draft of the policy first; the Draft review comes "
            "later, and draft-ietf-oauth and drafts are words, not paths.\n"), OK_LINE, 0),
    ("a stylesheet url() outside site/assets/",
     write("site/assets/site.css", ".statement { --sw: 14; }\n.x { background: url(/logo.svg); }\n"),
     "is not a relative path", 1),
    ("a stylesheet @import", write("site/assets/site.css", '@import "/live.css";\n.statement { --sw: 14; }\n'),
     "carries @import", 1),
    ("a stylesheet @import written with a CSS escape",
     write("site/assets/site.css", '@\\69mport "/live.css";\n.statement { --sw: 14; }\n'),
     "carries @import", 1),
    ("site.css setting another property",
     write("site/assets/site.css", ".statement { --sw: 14; color: red; }\n"), "may hold only", 1),
    ("site.css with a declaration outside a rule", write("site/assets/site.css", "--sw: 14;\n"),
     "may hold only", 1),
    ("site.css with another at-rule", write("site/assets/site.css", "@font-face { --sw: 1; }\n"),
     "may hold only", 1),
    ("site.css setting only the 2 constants, at the top level and for dark mode",
     write("site/assets/site.css", "/* measured */\n.site-secureconfig .statement { --sw: 13.9; }\n"
           "@media (prefers-color-scheme: dark) { :root:not([data-scheme=\"light\"]) .statement { --sw: 14.8; } }\n"
           ".site-secureconfig .rail { --logo-inset: 0.12; }\n"),
     OK_LINE, 0),
    ("the pristine site", None, OK_LINE, 0),
]


def generated(edit_content, extra=None):
    """Build the pages from a scratch copy of their sources with 1 content edit, then run
    build-site.py --check and check_draft.py on it: the source-to-generated-page path."""
    d = Path(tempfile.mkdtemp())
    try:
        for rel in ("scripts/build-site.py", "tools/check_csp_hashes.py", "tools/check_draft.py",
                    "site-src/content.json", "README.md", "tools/version_basis_guides.txt"):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, d / rel)
        shutil.copytree(ROOT / "site" / "assets", d / "site" / "assets")
        for name in ("_headers", "llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml",
                     "favicon.svg"):
            if (ROOT / "site" / name).is_file():
                shutil.copyfile(ROOT / "site" / name, d / "site" / name)
        if edit_content:
            edit("site-src/content.json", *edit_content)(d)
        if extra:
            extra(d)
        out = []
        for cmd in (["scripts/build-site.py"], ["scripts/build-site.py", "--check"],
                    ["tools/check_draft.py", "--root", str(d)]):
            r = subprocess.run([sys.executable, "-I", "-B", str(d / cmd[0]), *cmd[1:]],
                               capture_output=True, text=True, timeout=120)
            out.append((r.returncode, (r.stdout + r.stderr).strip()))
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    failures = []
    for desc, mutate, expected, want in CASES:
        rc, out = run(mutate)
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    # Each SINGLE_FORM line is caught by its own corpus form and by no other.
    sys.path.insert(0, str(TOOLS))
    from check_draft import DRAFT_REFS, normalized
    for line, form, _ in SINGLE_FORM:
        forms = "".join(f for f, p in zip("abcde", DRAFT_REFS) if p.search(normalized(line)))
        if forms != form:
            failures.append(f"{line.strip()!r}: expected only form {form} to match, got {forms!r}")
    # Source to generated page: a Unicode host written in content.json is generated, passes the
    # build's own --check, and is refused by this gate.
    (b, bout), (c, cout), (g, gout) = generated(
        ('"start": {"text": "Browse the guides", "href": "/guides/"',
         '"start": {"text": "Browse the guides", "href": "https://secureconfig。ai/"'))
    if b or c or g != 1 or "not plain ASCII" not in gout:
        failures.append(f"a Unicode host from content.json was not refused on the generated page: "
                        f"build {b} {bout!r}, check {c} {cout!r}, gate {g} {gout!r}")
    # The optional site.css (baseline README) is accepted by the build's --check and by this gate.
    css = ".site-secureconfig .statement { --sw: 13.9; }\n"
    (b, bout), (c, cout), (g, gout) = generated(
        None, lambda d: (d / "site/assets/site.css").write_text(css, encoding="utf-8"))
    if b or c or g:
        failures.append(f"a site.css setting only --sw was refused: build {b} {bout!r}, check {c} "
                        f"{cout!r}, gate {g} {gout!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    refusals = sum(1 for case in CASES if case[3])
    print(f"  ok    {len(CASES)} self-containment, indexability and published-index cases at the "
          f"root ({refusals} refusals and {len(CASES) - refusals} accepted changes, the pristine "
          f"site among them), "
          f"and 2 generated-page cases (a Unicode host refused, a site.css accepted by the build "
          f"and the gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
