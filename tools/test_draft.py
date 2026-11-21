#!/usr/bin/env python3
"""Cases for check_draft.py at the root: each way the published site could stop being
self-contained, or its indexability could silently change.

Each failing case copies the real site/ tree, makes 1 change and asserts that the gate exits 1
with a message naming the defect; each passing case makes a change the gate must accept (the
pristine copy among them). A mutation that no longer applies RAISES, so a page edit cannot turn a
case into a pristine run.

The staged-era /draft/* header rule retired with the staging it policed. What carried over is
retargeted to the generated pages at the root: the robots-meta reading (on the 404, with every
other page carrying none; the cases once read on the /draft/ review page, which baseline 1.11.0
moved to the `draft` branch, now read the 404's), every URL-shape refusal (a browser-normalized
host, a trailing-dot, upper-case, percent-encoded or non-ASCII host, a Pages alias, https:/// and
scheme-relative spellings, a backslash, whitespace, javascript:), the URL attributes beyond href
and src, http-equiv, the new-tab hint, site/_redirects, CSS @import and url() containment and the
site.css grammar. New at the root: a root-relative link must name a file under site/, and a link
or a stylesheet url() that percent-decodes to a NUL is refused with a finding, never a traceback,
as unpathable() also refuses a character the file system encoding cannot encode, checked in
process; each canonical is its page's own URL (exactly 1 on the 7 indexable pages, none on the 404
or the unlisted advisory, not even its own); the noindex admission is the exact path
advisories/n8n-2026-11-07-jposluns.html, so a noindex site/advisories/other.html, and a noindex
page at the advisory's old path advisories/n8n.html, are still refused, while the advisory's
build-written plain-text copy beside it, which is not a page, is in the pristine copy the gate
accepts; the live site carries no draft tree, so a site/draft/ folder (with a page or with any
other file), a site/Draft/ folder and a site/draft file are each refused while a site/drafts/
folder is not the draft tree; the "no page links /draft/" and Disclosure and Licence rules compare
the resolved target file, so a query, an extra slash, a dot segment (plain or percent-encoded), a
percent-encoded letter or a fragment does not get past them (the /draft/ link cases plant a draft
tree, so the link rule itself is read; without one a /draft/ link names no file); and the
published indexes are read by a fail-closed rule after percent-decoding and character-reference
decoding (at most 8 rounds), NFKC, case folding and `\\` read as `/`: site/llms.txt,
site/robots.txt and site/.well-known/security.txt are refused for any literal `draft` once tabs
and CRs are deleted (relative, Disallow, bold, host-only, www, href=, backslash, 1-slash, .html,
character-reference, tab and CR spellings and a raw CR inside the path among the cases) and accept
"Raft consensus and Raft logs", and site/llms-full.txt for each form of the draft path, matched
with tabs and CRs kept and with them deleted (character references, a tab or CR character
reference or a raw CR inside the path, a tab as the only separator between a word and the
reference for forms a, b and e, bare Markdown link destinations, reference definitions, HTML
attribute values, a link broken across a line end, a link broken inside a blockquote, a reference
definition whose destination is on the next line, whose label spans 2 lines, or that sits in a
blockquote or a list item, and 1 case each for forms b, d and e that only that form catches),
while its prose ("drafting", "drafted", "a draft.", "the draft's", "draft / final", "and Raft",
"Choose draft" wrapped before "/ final wording." in the text and in a link title,
"draft-ietf-oauth-v2-1", a datatracker draft URL and a description meta saying "draft") is
accepted. site/secureconfig-instructions.md, the generated chat fallback file, is read with the
same corpus forms, and one case plants a /draft/ path in it. A 9-times percent-encoded path
exceeds the round limit and is refused. Each refusal names the file and line, counted by `\\n`
only (a U+2028 or a `\\r` ends no line, and llms-full.txt written with `\\r\\n` line endings
reports a reference on line 2 as line 2). The edit, append, prepend and crlf mutations read and
write bytes, so they translate no newline. A second robots meta whose first name attribute is
robots is read by that first name, as a browser reads it.

site/_redirects is no longer refused outright: the gate admits only the generator's header, the
entries of tools/redirects_allowlist.txt and, written only once a release record exists, the two
latest 302 links as the last 2 lines, naming one version's archives staged in site/downloads/.
The cases cover an accepted full file, the accepted record-less shape (the header and an
allowlisted rule, no latest line), an allowlisted entry, an aged-out zip redirected to its own
release asset, a headerless file, a 301, a wrong-kind target, a missing staged archive, a lone
latest link and the reversed order. They also cover 2 versions, a third rule, a /draft rule
(allowlisted or not), sources whose first segment starts with draft, case folded and
percent-decoded (/draft, /draft.html, /drafts, /DraftS.html and /%64rafts, each refused, while
/old-draft, whose first segment does not start with draft, is accepted), an entry without a
reason, an aged-out redirect from a foreign source, an
entry whose source names a staged archive or an existing page (it would shadow served bytes, and
the folder, index and other-case forms of a page's path are read too), and a -latest file under
site/, in downloads/ and elsewhere. Further refusals cover an entry whose target lies under
/downloads/ (written plainly or through a plain or percent-encoded dot segment), a /draft source
written through a plain or percent-encoded dot segment, a scheme-relative target, an absolute
target that is no release asset, and a .zip target outside /downloads/. A gated field is one
exact literal path. The cases refuse the splat sources /downloads/*, /*, /checklist/*,
/assets/* and /check*, the placeholder sources /:page, /:dir/index.html and /downloads/:file,
and the query and fragment sources /draft?x, /draft#x, /checklist?x, /checklist/?x,
/checklist/#x, /assets/site.css?x, /assets/site.css#x, /downloads/<staged zip>?x and
/downloads/secureconfig-plugin-latest.zip?x. They also refuse the trailing-slash sources
/assets/site.css/, /downloads/<staged zip>/ and /downloads/secureconfig-latest.zip/. A gated
field is printable ASCII, raw and percent-decoded: the cases refuse a raw U+FEFF at the end of
each gated source shape (/draft, a page, the stylesheet, both latest names, a staged and an
aged-out zip) and inside a target. They also refuse sources that percent-decode to U+FEFF, a
no-break space, an ideographic space or a U+2028 line separator, and a source carrying a
fullwidth letter, a fullwidth solidus, a zero-width space or a raw C1 control character. No
two entries share a source: the cases refuse two identical entries, a repeated source with
another target, a case-varied and a percent-encoded repeat, and a page rule repeating an
aged-out zip's asset-redirect source, which would mask that redirect. The archive target rule
reads bytes as well as names: a target outside /downloads/ whose file opens with a zip or gzip
signature under a .bin, .tar.gz or .zip.txt name is refused. A target is a page or a published
file in check_draft.PUBLISHED_TARGETS, which one case holds to scripts/build-site.py's
PUBLISHED without _headers: the host's own _headers and _redirects are refused as targets, and
llms.txt is accepted.

The generated() cases keep the source-to-generated-page path: a Unicode host written in
content.json survives the build and its own --check and is refused by this gate, and a site.css
setting only the 2 per-site constants is accepted by the build and the gate. The staged() case
builds the `draft` branch's staging form (`--base /draft/ --out site/draft`) beside the root
build: the staged --check passes, so the staging form keeps working, and on this tree, as on
`main`, the root --check and this gate each refuse the draft tree (baseline SPECIFICATION
section 4.1 items 0 and 3).

The ASCII_CASES run the gate with its stdout encoded as strict ASCII, as on a host whose locale
is ASCII: a site/_redirects line naming /draft/ and a latest link whose target is not a staged
zip, each carrying a printable non-ASCII character, must each exit 1 with the line printed
escaped, never end in a traceback.
"""
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent


# Runs the script named first after it as __main__ with sys.stdout re-encoded as strict ASCII, so
# a print the stream cannot encode ends the run in a UnicodeEncodeError traceback.
ASCII_STDOUT = ("import runpy, sys; sys.stdout.reconfigure(encoding='ascii', errors='strict'); "
                "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')")


def run(mutate=None, ascii_stdout=False):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / "site", d / "site")
        if mutate is not None:
            mutate(d)
        start = ["-c", ASCII_STDOUT] if ascii_stdout else []
        r = subprocess.run([sys.executable, "-I", "-B", *start, str(TOOLS / "check_draft.py"),
                            "--root", str(d)], capture_output=True, text=True, timeout=60)
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


def write_bytes(rel, data):
    """rel written with data as raw bytes, for planting an archive signature untranslated."""
    def mutate(d):
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_bytes(data)
    return mutate


HOME = "site/index.html"
GUIDES = "site/guides/index.html"
P404 = "site/404.html"
ADVISORY = "site/advisories/n8n-2026-11-07-jposluns.html"
# The advisory's plain-text copy, which scripts/build-site.py writes beside it.
ADVISORY_TEXT = "site/advisories/n8n-2026-11-07-jposluns.txt"
META = '<meta name="robots" content="noindex, nofollow">'
START = 'href="/guides/"'
GUIDES_CANONICAL = 'href="https://secureconfig.ai/guides/"'
OK_LINE = "10 pages are self-contained"
STRAY = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>x</title>\n'
         '</head>\n<body><a href="/nowhere/">gone</a></body>\n</html>\n')
# A page that passes every per-page rule of the gate, for planting where only its path matters.
PLAIN = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>x</title>\n'
         '</head>\n<body><p>x</p></body>\n</html>\n')
# The finding for a draft tree under site/ (PART 1 of the gate).
NO_TREE = "the live site carries no /draft/ tree"
LINKS_DRAFT = "no live page links /draft/"
# site/_redirects: the generator's header and the two latest links (PART 1 of the gate), written
# out here rather than read from the gate.
R_HEADER = ("# Generated by tools/gen_hosted.py from releases/ and "
            "tools/redirects_allowlist.txt; do not edit by hand.\n")
SKILL_ZIP = "secureconfig-1.0.7.zip"
PLUGIN_ZIP = "secureconfig-plugin-1.0.7.zip"
LATEST = (f"/downloads/secureconfig-latest.zip /downloads/{SKILL_ZIP} 302\n"
          f"/downloads/secureconfig-plugin-latest.zip /downloads/{PLUGIN_ZIP} 302\n")
ASSET = ("/downloads/secureconfig-1.0.5.zip https://github.com/jposluns/secureconfig/releases/"
         "download/v1.0.5/secureconfig-1.0.5.zip 302")


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


def draft_link(value):
    """A planted draft tree (site/draft/index.html) and the home page's first /guides/ link
    pointed at value, so the gate's /draft/ link rule, not only its missing-file rule, reads it."""
    def mutate(d):
        write("site/draft/index.html", PLAIN)(d)
        link(value)(d)
    return mutate


def guides_link(value):
    """A link to value planted in the Guides page's top bar, before its For AI assistants link."""
    return edit(GUIDES, '<a href="/for-ai/">', f'<a href="{value}">x</a><a href="/for-ai/">')


def redirects(text, allow=None, zips=(SKILL_ZIP, PLUGIN_ZIP)):
    """site/_redirects written as the generator's header plus text, the named archives staged in
    site/downloads/, and, when allow is given, a tools/redirects_allowlist.txt beside the root."""
    def mutate(d):
        for name in zips:
            write(f"site/downloads/{name}", "zip bytes\n")(d)
        if allow is not None:
            write("tools/redirects_allowlist.txt", allow)(d)
        write("site/_redirects", R_HEADER + text)(d)
    return mutate


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
        # A raw CR inside the path, which ends no line.
        "- [Review](/dr\raft/): the next version\n",
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
        # A raw CR inside the path, which ends no line.
        "The next version is staged at /dr\raft/ for review.\n",
        # A tab as the only separator between a word and the reference, which forms a, b and e
        # read on the text with tabs kept (deleting the tab would join them).
        "The next version is staged at https://secureconfig.ai/draft\tfor review.\n",
        "The next version: see\tdraft/notes for review.\n",
        'The next version is staged <a\thref="draft">here</a>.\n',
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
# The generated chat fallback file is a published index too: PART 3 reads it with the same
# corpus forms as llms-full.txt, so a planted /draft/ path is refused there.
INDEX_CASES += [("secureconfig-instructions.md naming /draft/",
                 append("site/secureconfig-instructions.md",
                        "The next version is staged at /draft/ for review.\n"),
                 refused_at("site/secureconfig-instructions.md"), 1)]
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
    ("the 404 page without its robots meta", edit(P404, META + "\n", ""),
     "must carry exactly 1 robots meta", 1),
    ("the 404 page with a second robots meta", edit(P404, META, META + META),
     "must carry exactly 1 robots meta", 1),
    ("the 404 page's robots meta only inside a comment", edit(P404, META, f"<!-- {META} -->"),
     "must carry exactly 1 robots meta", 1),
    ("a second robots meta on the 404 page, single-quoted, allowing indexing",
     edit(P404, META, META + "<meta name='ROBOTS' content='index, follow'>"),
     "must carry exactly 1 robots meta", 1),
    ("a duplicate name attribute on a second robots meta on the 404 page, the first being robots",
     edit(P404, META, META + '<meta name="robots" name="x" content="index, follow">'),
     "must carry exactly 1 robots meta", 1),
    ("the 404 page's robots meta in upper case with other spacing",
     edit(P404, META, '<META NAME="Robots" CONTENT="NOINDEX,NOFOLLOW">'), OK_LINE, 0),
    ("a robots meta on an indexable page", edit(GUIDES, "<title>Guides", META + "\n<title>Guides"),
     "carries a robots meta element", 1),
    # The one unlisted advisory is admitted as a noindex page by its exact path: the pristine site
    # (it is noindex and carries no canonical) is accepted below, losing or doubling its noindex is
    # refused, and any OTHER unexpected noindex page is still refused.
    ("the advisory page without its robots meta", edit(ADVISORY, META + "\n", ""),
     "must carry exactly 1 robots meta", 1),
    ("the advisory page with a second robots meta", edit(ADVISORY, META, META + META),
     "must carry exactly 1 robots meta", 1),
    ("a stray noindex page other than the 404 and the advisory",
     write("site/extra.html", PLAIN.replace('<meta charset="utf-8">',
                                            '<meta charset="utf-8">\n' + META)),
     "carries a robots meta element", 1),
    # #1252 QA: the admission is the exact path, not the advisories/ folder, so a noindex page
    # beside the advisory is refused; NOINDEX_PAGES widened to a prefix fails this case.
    ("a noindex page beside the advisory, under site/advisories/",
     write("site/advisories/other.html", PLAIN.replace('<meta charset="utf-8">',
                                                       '<meta charset="utf-8">\n' + META)),
     "'site/advisories/other.html' carries a robots meta element", 1),
    # The advisory moved to a dated name (the maintainer's instruction of 2026-11-07): a noindex
    # page at its old path is no longer admitted.
    ("a noindex page at the advisory's old path, site/advisories/n8n.html",
     write("site/advisories/n8n.html", PLAIN.replace('<meta charset="utf-8">',
                                                     '<meta charset="utf-8">\n' + META)),
     "'site/advisories/n8n.html' carries a robots meta element", 1),
    # The live site carries no draft tree (SPECIFICATION 4.1 items 0 and 3), in any case and
    # whatever it holds; a folder whose name only begins with draft is not the tree.
    ("a site/draft/ folder holding a page", write("site/draft/index.html", PLAIN),
     f"'site/draft' exists (folder); {NO_TREE}", 1),
    ("a site/draft/ folder holding no page, only a stylesheet",
     write("site/draft/assets/baseline/baseline.css", "p{}\n"),
     f"'site/draft' exists (folder); {NO_TREE}", 1),
    ("a site/Draft/ folder in another case", write("site/Draft/notes.txt", "x\n"),
     f"'site/Draft' exists (folder); {NO_TREE}", 1),
    ("a site/draft file", write("site/draft", "x\n"), f"'site/draft' exists (file); {NO_TREE}", 1),
    ("a site/drafts/ folder, which is not the draft tree", write("site/drafts/index.html", PLAIN),
     "11 pages are self-contained", 0),
    ("a link to a page that does not exist", link("/nowhere/"), "names no file", 1),
    ("a ../ path out of site/", link("/../SECURITY.md"), "names no file", 1),
    # A link that percent-decodes to a NUL names no file: a finding, never the ValueError that
    # Path.resolve() raises on a NUL, which ended the gate in a traceback with no FAIL line.
    ("a link that percent-decodes to a NUL", link("/x%00"), "decodes to a NUL character", 1),
    ("a link to a page's path with a NUL after it", link("/guides/index.html%00"),
     "decodes to a NUL character", 1),
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
     "'xlink:href'='javascript:x()' uses the javascript: scheme", 1),
    ("a formaction to a missing file",
     edit(HOME, '<a class="start"', '<button formaction="/x">x</button><a class="start"'),
     "'formaction'='/x' names no file", 1),
    ("a ping to a missing file", edit(HOME, START, START + ' ping="/guides/ /x"'),
     "'ping'='/x' names no file", 1),
    ("a srcset candidate naming a missing file",
     edit(HOME, 'alt="A terminal',
          'srcset="/assets/baseline/logos/secureconfig.svg 1x, /x.svg 2x" alt="A terminal'),
     "'srcset'='/x.svg' names no file", 1),
    ("an imagesrcset naming a missing file",
     edit(HOME, "</head>", '<link rel="preload" as="image" imagesrcset="/x.png 1x">\n</head>'),
     "'imagesrcset'='/x.png' names no file", 1),
    ("a poster naming a missing file",
     edit(HOME, '<a class="start"', '<video poster="/p.png"></video><a class="start"'),
     "'poster'='/p.png' names no file", 1),
    ("a background attribute naming a missing file",
     edit(HOME, '<a class="start"', '<table background="/bg.png"></table><a class="start"'),
     "'background'='/bg.png' names no file", 1),
    ("a meta refresh", edit(HOME, "</head>", '<meta http-equiv="refresh" content="0;url=/">\n</head>'),
     "http-equiv", 1),
    ("a meta refresh on the 404 page",
     edit(P404, "</head>", '<meta http-equiv="refresh" content="0; /x/">\n</head>'), "http-equiv", 1),
    ("a new-tab link without the hidden hint",
     edit(GUIDES, 'free-certificates<span class="vh"> (opens in a new tab)</span>', "free-certificates"),
     "does not say so", 1),
    ("a stray .htm page linking a missing file", write("site/extra.htm", STRAY),
     "'site/extra.htm':7: 'href'='/nowhere/' names no file", 1),
    ("a stray .HTML page in a folder, read as a page", write("site/x/Page.HTML", STRAY),
     "'site/x/Page.HTML':7: 'href'='/nowhere/' names no file", 1),
    ("a site/_redirects file without the generator's header",
     write("site/_redirects", "/old / 301\n"), "the first line is the generator's header", 1),
    ("site/_redirects with the header, the 2 latest links and both archives staged",
     redirects(LATEST), OK_LINE, 0),
    ("a latest link with a 301 status", redirects(LATEST.replace(" 302\n", " 301\n", 1)),
     "answers 302, never 301", 1),
    ("a latest link naming the wrong kind of zip",
     redirects(LATEST.replace(f"/downloads/{SKILL_ZIP} 302", f"/downloads/{PLUGIN_ZIP} 302")),
     "that link's own kind of zip", 1),
    ("a latest link naming no staged archive", redirects(LATEST, zips=(PLUGIN_ZIP,)),
     "names no staged archive", 1),
    ("the 2 latest links naming 2 versions",
     redirects(LATEST.replace(PLUGIN_ZIP, "secureconfig-plugin-1.0.9.zip"),
               zips=(SKILL_ZIP, "secureconfig-plugin-1.0.9.zip")),
     "name 2 versions", 1),
    ("a lone latest link", redirects(LATEST.splitlines()[0] + "\n", zips=(SKILL_ZIP,)),
     "a lone, repeated, reordered or displaced latest link", 1),
    ("the 2 latest links in the wrong order",
     redirects("\n".join(reversed(LATEST.splitlines())) + "\n"),
     "a lone, repeated, reordered or displaced latest link", 1),
    ("a third rule beside the 2 latest links", redirects("/old / 302\n" + LATEST),
     "is not an allowlisted redirect", 1),
    ("a /draft rule", redirects("/draft/x /index.html 302\n" + LATEST), "names /draft/", 1),
    ("an allowlisted redirect to a file under site/",
     redirects("/old / 302\n" + LATEST, allow="/old / 302\tthe old URL of the landing page\n"),
     OK_LINE, 0),
    ("an allowlisted redirect whose target names no file",
     redirects("/old /gone/ 302\n" + LATEST, allow="/old /gone/ 302\tmoved\n"),
     "naming no file under site/", 1),
    ("an allowlisted /draft rule, still refused",
     redirects("/x /draft/ 302\n" + LATEST, allow="/x /draft/ 302\tan old draft link\n"),
     "names /draft/", 1),
    # A source's first segment must not even start with draft, case folded and percent-decoded.
    ("an allowlisted /draft source",
     redirects("/draft /index.html 302\n" + LATEST,
               allow="/draft /index.html 302\tan old draft link\n"),
     "starts with draft", 1),
    ("an allowlisted /draft.html source",
     redirects("/draft.html /index.html 302\n" + LATEST,
               allow="/draft.html /index.html 302\tan old draft page\n"),
     "starts with draft", 1),
    ("an allowlisted /drafts source",
     redirects("/drafts /index.html 302\n" + LATEST,
               allow="/drafts /index.html 302\tan old drafts folder\n"),
     "starts with draft", 1),
    ("an allowlisted /DraftS.html source in another case",
     redirects("/DraftS.html /index.html 302\n" + LATEST,
               allow="/DraftS.html /index.html 302\tan old draft page\n"),
     "starts with draft", 1),
    ("an allowlisted /%64rafts source, percent-encoded",
     redirects("/%64rafts /index.html 302\n" + LATEST,
               allow="/%64rafts /index.html 302\tan old drafts folder\n"),
     "starts with draft", 1),
    ("an allowlisted /old-draft source, whose first segment does not start with draft",
     redirects("/old-draft /index.html 302\n" + LATEST,
               allow="/old-draft /index.html 302\tan old page\n"),
     OK_LINE, 0),
    ("an allowlist entry without a reason", redirects(LATEST, allow="/old / 302\n"),
     "reason with visible text", 1),
    # Row 3.111: a reason of U+200B alone is no reason, as reason_present() judges it.
    ("an allowlist entry whose reason is U+200B alone",
     redirects(LATEST, allow="/old / 302\t\u200b\n"), "reason with visible text", 1),
    ("an aged-out zip redirected to its own release asset",
     redirects(ASSET + "\n" + LATEST, allow=ASSET + "\taged out of site/downloads/\n"),
     OK_LINE, 0),
    ("an aged-out redirect from a source that is not the zip's own path",
     redirects(LATEST, allow=ASSET.replace("/downloads/secureconfig-1.0.5.zip ", "/old ", 1)
               + "\tx\n"),
     "a source other than its own /downloads/<zip> path", 1),
    ("an allowlisted redirect whose source is a staged archive",
     redirects(f"/downloads/{SKILL_ZIP} / 302\n" + LATEST,
               allow=f"/downloads/{SKILL_ZIP} / 302\tmoved to the landing page\n"),
     "has a source naming a file under site/", 1),
    ("an allowlisted redirect whose source is an existing page",
     redirects("/404.html /index.html 302\n" + LATEST,
               allow="/404.html /index.html 302\tmoved\n"),
     "has a source naming a file under site/", 1),
    ("an allowlisted redirect whose target lies under /downloads/",
     redirects("/old /downloads/extra.zip 302\n" + LATEST,
               allow="/old /downloads/extra.zip 302\tserve the staged copy\n",
               zips=(SKILL_ZIP, PLUGIN_ZIP, "extra.zip")),
     "has a target under /downloads/", 1),
    ("an allowlisted redirect whose target reaches /downloads/ through a dot segment",
     redirects("/get /assets/../downloads/extra.zip 302\n" + LATEST,
               allow="/get /assets/../downloads/extra.zip 302\tserve the staged copy\n",
               zips=(SKILL_ZIP, PLUGIN_ZIP, "extra.zip")),
     "carries a `.` or `..` segment", 1),
    ("an allowlisted redirect whose target reaches /downloads/ through a percent-encoded dot "
     "segment",
     redirects("/get /assets/%2e%2e/downloads/extra.zip 302\n" + LATEST,
               allow="/get /assets/%2e%2e/downloads/extra.zip 302\tserve the staged copy\n",
               zips=(SKILL_ZIP, PLUGIN_ZIP, "extra.zip")),
     "carries a `.` or `..` segment", 1),
    ("an allowlisted /draft rule whose source carries a dot segment",
     redirects("/assets/../draft/ /index.html 302\n" + LATEST,
               allow="/assets/../draft/ /index.html 302\tan old draft link\n"),
     "carries a `.` or `..` segment", 1),
    ("an allowlisted /draft splat rule whose source carries a percent-encoded dot segment",
     redirects("/assets/%2e%2e/draft/* /index.html 302\n" + LATEST,
               allow="/assets/%2e%2e/draft/* /index.html 302\tan old draft link\n"),
     "carries a `.` or `..` segment", 1),
    ("an allowlisted redirect whose target is an archive outside /downloads/",
     lambda d: (write("site/assets/extra.zip", "zip bytes\n")(d),
                redirects("/get /assets/extra.zip 302\n" + LATEST,
                          allow="/get /assets/extra.zip 302\tserve the extra archive\n")(d)),
     "has a target naming an archive under site/", 1),
    ("an allowlisted redirect whose source is a page's folder path without its slash",
     redirects("/checklist /index.html 302\n" + LATEST,
               allow="/checklist /index.html 302\tmoved\n"),
     "has a source naming a file under site/", 1),
    ("an allowlisted redirect whose source is a page's index path without its .html",
     redirects("/checklist/index /index.html 302\n" + LATEST,
               allow="/checklist/index /index.html 302\tmoved\n"),
     "has a source naming a file under site/", 1),
    ("an allowlisted redirect whose source is a page's folder in another case",
     redirects("/CHECKLIST/ /index.html 302\n" + LATEST,
               allow="/CHECKLIST/ /index.html 302\tmoved\n"),
     "has a source naming a file under site/", 1),
    ("an allowlisted redirect with a scheme-relative target",
     lambda d: (write("site/assets/site.css", ".statement { --sw: 14; }\n")(d),
                redirects("/old //assets/site.css 302\n" + LATEST,
                          allow="/old //assets/site.css 302\tmoved\n")(d)),
     "is scheme-relative", 1),
    ("an allowlisted redirect whose target is an absolute URL that is no release asset",
     redirects("/old https://example.net/secureconfig-1.0.5.zip 302\n" + LATEST,
               allow="/old https://example.net/secureconfig-1.0.5.zip 302\ta mirror\n"),
     "neither a root-relative path", 1),
    # A gated field is one exact literal path: splat, placeholder, query, fragment and
    # trailing-slash source spellings are each refused, since a host can match each of them
    # more widely than the one path the rules read.
    ("an allowlisted splat source under /downloads/",
     redirects("/downloads/* /index.html 302\n" + LATEST,
               allow="/downloads/* /index.html 302\tcatch old download URLs\n"),
     "one exact literal path", 1),
    ("an allowlisted catch-all splat source",
     redirects("/* /index.html 302\n" + LATEST,
               allow="/* /index.html 302\tcatch every path\n"),
     "one exact literal path", 1),
    ("an allowlisted splat source under a page's folder",
     redirects("/checklist/* /index.html 302\n" + LATEST,
               allow="/checklist/* /index.html 302\tcatch old checklist URLs\n"),
     "one exact literal path", 1),
    ("an allowlisted splat source under /assets/",
     redirects("/assets/* /index.html 302\n" + LATEST,
               allow="/assets/* /index.html 302\tcatch old asset URLs\n"),
     "one exact literal path", 1),
    ("an allowlisted splat source ending a partial name",
     redirects("/check* /index.html 302\n" + LATEST,
               allow="/check* /index.html 302\tcatch checklist spellings\n"),
     "one exact literal path", 1),
    ("an allowlisted placeholder source",
     redirects("/:page /index.html 302\n" + LATEST,
               allow="/:page /index.html 302\tcatch every page\n"),
     "one exact literal path", 1),
    ("an allowlisted placeholder source before an index path",
     redirects("/:dir/index.html /index.html 302\n" + LATEST,
               allow="/:dir/index.html /index.html 302\tcatch every index\n"),
     "one exact literal path", 1),
    ("an allowlisted placeholder source under /downloads/",
     redirects("/downloads/:file /index.html 302\n" + LATEST,
               allow="/downloads/:file /index.html 302\tcatch every download\n"),
     "one exact literal path", 1),
    ("an allowlisted /draft source with a query",
     redirects("/draft?x /index.html 302\n" + LATEST,
               allow="/draft?x /index.html 302\tan old draft link\n"),
     "one exact literal path", 1),
    ("an allowlisted /draft source with a fragment",
     redirects("/draft#x /index.html 302\n" + LATEST,
               allow="/draft#x /index.html 302\tan old draft link\n"),
     "one exact literal path", 1),
    ("an allowlisted page source with a query",
     redirects("/checklist?x /index.html 302\n" + LATEST,
               allow="/checklist?x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted folder source with a query",
     redirects("/checklist/?x /index.html 302\n" + LATEST,
               allow="/checklist/?x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted folder source with a fragment",
     redirects("/checklist/#x /index.html 302\n" + LATEST,
               allow="/checklist/#x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted stylesheet source with a query",
     redirects("/assets/site.css?x /index.html 302\n" + LATEST,
               allow="/assets/site.css?x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted stylesheet source with a fragment",
     redirects("/assets/site.css#x /index.html 302\n" + LATEST,
               allow="/assets/site.css#x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted stylesheet source with a trailing slash",
     redirects("/assets/site.css/ /index.html 302\n" + LATEST,
               allow="/assets/site.css/ /index.html 302\tmoved\n"),
     "has a source with a trailing slash", 1),
    ("an allowlisted staged-archive source with a query",
     redirects(f"/downloads/{SKILL_ZIP}?x /index.html 302\n" + LATEST,
               allow=f"/downloads/{SKILL_ZIP}?x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    ("an allowlisted staged-archive source with a trailing slash",
     redirects(f"/downloads/{SKILL_ZIP}/ /index.html 302\n" + LATEST,
               allow=f"/downloads/{SKILL_ZIP}/ /index.html 302\tmoved\n"),
     "has a source with a trailing slash", 1),
    ("an allowlisted latest-name source with a trailing slash",
     redirects("/downloads/secureconfig-latest.zip/ /index.html 302\n" + LATEST,
               allow="/downloads/secureconfig-latest.zip/ /index.html 302\tmoved\n"),
     "has a source with a trailing slash", 1),
    ("an allowlisted latest-name source with a query",
     redirects("/downloads/secureconfig-plugin-latest.zip?x /index.html 302\n" + LATEST,
               allow="/downloads/secureconfig-plugin-latest.zip?x /index.html 302\tmoved\n"),
     "one exact literal path", 1),
    # A gated field is printable ASCII, raw and percent-decoded: a raw U+FEFF, another
    # invisible or non-ASCII character or a raw C1 control character in a field is refused, and
    # so is a field that percent-decodes to one, so no rule can shadow a staged path or take
    # over /draft or a latest link for a parser that trims or splits on more than a space.
    ("an allowlisted /draft source carrying a raw U+FEFF",
     redirects("/draft﻿ /index.html 302\n" + LATEST,
               allow="/draft﻿ /index.html 302\tan old draft link\n"),
     "printable ASCII", 1),
    ("an allowlisted page source carrying a raw U+FEFF",
     redirects("/checklist﻿ /index.html 302\n" + LATEST,
               allow="/checklist﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted stylesheet source carrying a raw U+FEFF",
     redirects("/assets/site.css﻿ /index.html 302\n" + LATEST,
               allow="/assets/site.css﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted latest-name source carrying a raw U+FEFF",
     redirects("/downloads/secureconfig-latest.zip﻿ /index.html 302\n" + LATEST,
               allow="/downloads/secureconfig-latest.zip﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted plugin-latest-name source carrying a raw U+FEFF",
     redirects("/downloads/secureconfig-plugin-latest.zip﻿ /index.html 302\n" + LATEST,
               allow="/downloads/secureconfig-plugin-latest.zip﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted staged-archive source carrying a raw U+FEFF",
     redirects(f"/downloads/{SKILL_ZIP}﻿ /index.html 302\n" + LATEST,
               allow=f"/downloads/{SKILL_ZIP}﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted aged-out-zip source carrying a raw U+FEFF",
     redirects("/downloads/secureconfig-1.0.5.zip﻿ /index.html 302\n" + LATEST,
               allow="/downloads/secureconfig-1.0.5.zip﻿ /index.html 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted target carrying a raw U+FEFF",
     redirects("/old /index.html﻿ 302\n" + LATEST,
               allow="/old /index.html﻿ 302\tmoved\n"),
     "printable ASCII", 1),
    ("an allowlisted source that percent-decodes to a U+FEFF",
     redirects("/draft%EF%BB%BF /index.html 302\n" + LATEST,
               allow="/draft%EF%BB%BF /index.html 302\tan old draft link\n"),
     "outside printable ASCII", 1),
    ("an allowlisted source that percent-decodes to a no-break space",
     redirects("/draft%C2%A0 /index.html 302\n" + LATEST,
               allow="/draft%C2%A0 /index.html 302\tan old draft link\n"),
     "outside printable ASCII", 1),
    ("an allowlisted source that percent-decodes to an ideographic space",
     redirects("/draft%E3%80%80 /index.html 302\n" + LATEST,
               allow="/draft%E3%80%80 /index.html 302\tan old draft link\n"),
     "outside printable ASCII", 1),
    ("an allowlisted source that percent-decodes to a U+2028 line separator",
     redirects("/draft%E2%80%A8 /index.html 302\n" + LATEST,
               allow="/draft%E2%80%A8 /index.html 302\tan old draft link\n"),
     "outside printable ASCII", 1),
    ("an allowlisted source carrying a fullwidth letter",
     redirects("/ｄraft /index.html 302\n" + LATEST,
               allow="/ｄraft /index.html 302\tan old draft link\n"),
     "printable ASCII", 1),
    ("an allowlisted source carrying a fullwidth solidus",
     redirects("/draft／x /index.html 302\n" + LATEST,
               allow="/draft／x /index.html 302\tan old draft link\n"),
     "printable ASCII", 1),
    ("an allowlisted source carrying a zero-width space",
     redirects("/dra​ft /index.html 302\n" + LATEST,
               allow="/dra​ft /index.html 302\tan old draft link\n"),
     "printable ASCII", 1),
    ("an allowlisted source carrying a raw C1 control character",
     redirects("/draft\u0085x /index.html 302\n" + LATEST,
               allow="/draft\u0085x /index.html 302\tan old draft link\n"),
     "printable ASCII", 1),
    # No two entries share a source: a host applies the first rule whose source matches, so a
    # repeated source, identical, retargeted, case-varied or percent-encoded, is refused, and a
    # page rule cannot mask an aged-out zip's asset redirect.
    ("two identical allowlisted entries",
     redirects("/old / 302\n/old / 302\n" + LATEST,
               allow="/old / 302\tmoved\n/old / 302\tmoved again\n"),
     "already names", 1),
    ("two allowlisted entries sharing a source, with different targets",
     redirects("/old / 302\n/old /checklist/ 302\n" + LATEST,
               allow="/old / 302\tmoved\n/old /checklist/ 302\tmoved again\n"),
     "already names", 1),
    ("two allowlisted entries sharing a source in different cases",
     redirects("/old / 302\n/OLD /checklist/ 302\n" + LATEST,
               allow="/old / 302\tmoved\n/OLD /checklist/ 302\tmoved again\n"),
     "already names", 1),
    ("two allowlisted entries sharing a source, one percent-encoded",
     redirects("/old / 302\n/%6Fld /checklist/ 302\n" + LATEST,
               allow="/old / 302\tmoved\n/%6Fld /checklist/ 302\tmoved again\n"),
     "already names", 1),
    ("a page rule repeating an aged-out zip's asset-redirect source, which would mask it",
     redirects("/downloads/secureconfig-1.0.5.zip / 302\n" + ASSET + "\n" + LATEST,
               allow="/downloads/secureconfig-1.0.5.zip / 302\tserve the home page\n"
                     + ASSET + "\taged out of site/downloads/\n"),
     "already names", 1),
    # The archive target rule reads bytes as well as names: a known signature under another
    # name is still an archive target.
    ("an allowlisted redirect whose target is a zip's bytes under a .bin name",
     lambda d: (write_bytes("site/assets/extra.bin", b"PK\x03\x04" + b"\0" * 28)(d),
                redirects("/get /assets/extra.bin 302\n" + LATEST,
                          allow="/get /assets/extra.bin 302\tserve the extra file\n")(d)),
     "bytes carrying a known archive signature", 1),
    ("an allowlisted redirect whose target is a gzip under a .tar.gz name",
     lambda d: (write_bytes("site/assets/extra.tar.gz", b"\x1f\x8b\x08\0" + b"\0" * 28)(d),
                redirects("/get /assets/extra.tar.gz 302\n" + LATEST,
                          allow="/get /assets/extra.tar.gz 302\tserve the extra file\n")(d)),
     "bytes carrying a known archive signature", 1),
    ("an allowlisted redirect whose target is a zip's bytes under a .zip.txt name",
     lambda d: (write_bytes("site/assets/extra.zip.txt", b"PK\x03\x04" + b"\0" * 28)(d),
                redirects("/get /assets/extra.zip.txt 302\n" + LATEST,
                          allow="/get /assets/extra.zip.txt 302\tserve the extra file\n")(d)),
     "bytes carrying a known archive signature", 1),
    # A target is a page or a published file (PUBLISHED_TARGETS), never the host's own
    # configuration files.
    ("an allowlisted redirect whose target is the host's _headers file",
     redirects("/old /_headers 302\n" + LATEST, allow="/old /_headers 302\tthe header rules\n"),
     "neither a page nor a published file", 1),
    ("an allowlisted redirect whose target is the host's _redirects file",
     redirects("/old /_redirects 302\n" + LATEST,
               allow="/old /_redirects 302\tthe redirect rules\n"),
     "neither a page nor a published file", 1),
    ("an allowlisted redirect whose target is a published file beside the pages",
     redirects("/old /llms.txt 302\n" + LATEST, allow="/old /llms.txt 302\tthe old index URL\n"),
     OK_LINE, 0),
    ("the record-less shape: the header and an allowlisted rule, no latest line",
     redirects("/old / 302\n", allow="/old / 302\tthe old URL of the landing page\n", zips=()),
     OK_LINE, 0),
    ("a -latest file under site/downloads/",
     write("site/downloads/secureconfig-latest.zip", "x\n"), "has a latest name", 1),
    ("a -latest file elsewhere under site/",
     write("site/assets/secureconfig-plugin-latest.zip", "x\n"), "has a latest name", 1),
    ("an inner page linking the Licence page",
     edit(GUIDES, '<a href="/for-ai/">', '<a href="/license/">Licence</a><a href="/for-ai/">'),
     "only the landing page", 1),
    ("an inner page linking the Disclosure page through a dot segment, a query and a fragment",
     guides_link("/guides/../disclosure/index.html?x#y"), "only the landing page", 1),
    ("an inner page linking the Licence page with a percent-encoded letter",
     guides_link("/%6cicense/"), "only the landing page", 1),
    ("a page linking /draft/, with no draft tree",
     edit(HOME, '<a class="start"', '<a href="/draft/">drafts</a><a class="start"'),
     "'href'='/draft/' names no file", 1),
    ("a page linking /draft/, with a draft tree planted", draft_link("/draft/"), LINKS_DRAFT, 1),
    ("a link to /draft/ with a query", draft_link("/draft/?x"), LINKS_DRAFT, 1),
    ("a link to /draft/ with an extra slash", draft_link("/draft//"), LINKS_DRAFT, 1),
    ("a link to /draft/ through a dot segment", draft_link("/guides/../draft/"), LINKS_DRAFT, 1),
    ("a link to /draft/ through a percent-encoded dot segment", draft_link("/guides/%2e%2e/draft/"),
     LINKS_DRAFT, 1),
    ("a link to /draft/ with a percent-encoded letter", draft_link("/%64raft/"), LINKS_DRAFT, 1),
    ("a link to /draft/index.html with a fragment", draft_link("/draft/index.html#a"),
     LINKS_DRAFT, 1),
    ("an indexable page's canonical on another host",
     edit(GUIDES, GUIDES_CANONICAL, 'href="https://example.net/guides/"'),
     "is not this page's own URL", 1),
    ("an indexable page's canonical naming a missing path",
     edit(GUIDES, GUIDES_CANONICAL, 'href="https://secureconfig.ai/nowhere/"'),
     "is not this page's own URL", 1),
    ("a canonical over plain HTTP",
     edit(GUIDES, GUIDES_CANONICAL, 'href="http://secureconfig.ai/guides/"'),
     "is not this page's own URL", 1),
    ("an indexable page's canonical resolving to another page, the home page",
     edit(GUIDES, GUIDES_CANONICAL, 'href="https://secureconfig.ai/"'),
     "the canonical 'https://secureconfig.ai/' is not this page's own URL", 1),
    ("an indexable page's canonical naming /draft/",
     edit(GUIDES, GUIDES_CANONICAL, 'href="https://secureconfig.ai/draft/"'),
     "the canonical 'https://secureconfig.ai/draft/' is not this page's own URL", 1),
    ("an indexable page without its canonical",
     edit(GUIDES, '<link rel="canonical" href="https://secureconfig.ai/guides/">\n', ""),
     "'site/guides/index.html' must carry exactly 1 canonical", 1),
    ("an indexable page with a second canonical, also its own URL",
     edit(HOME, '<link rel="canonical" href="https://secureconfig.ai/">',
          '<link rel="canonical" href="https://secureconfig.ai/">\n'
          '<link rel="canonical" href="https://secureconfig.ai/">'),
     "'site/index.html' must carry exactly 1 canonical", 1),
    ("a canonical on the 404 page",
     edit(P404, "</head>", '<link rel="canonical" href="https://secureconfig.ai/404.html">\n</head>'),
     "the 404 page carries none", 1),
    # #1252 QA: the unlisted advisory carries no canonical, not even its own URL, which the rule
    # for any other page would accept.
    ("a canonical on the unlisted advisory page, its own URL",
     edit(ADVISORY, "</head>",
          '<link rel="canonical" '
          'href="https://secureconfig.ai/advisories/n8n-2026-11-07-jposluns.html">\n</head>'),
     "the unlisted advisory page carries none", 1),
    *INDEX_CASES,
    ("llms-full.txt prose that merely says draft",
     append("site/llms-full.txt", "Write a draft of the policy first; the Draft review comes "
            "later, and draft-ietf-oauth and drafts are words, not paths.\n"), OK_LINE, 0),
    ("a stylesheet url() outside site/assets/",
     write("site/assets/site.css", ".statement { --sw: 14; }\n.x { background: url(/logo.svg); }\n"),
     "is not a relative path", 1),
    # So is a url() that percent-decodes to a NUL, in a stylesheet anywhere under site/.
    ("a stylesheet url() that percent-decodes to a NUL",
     write("site/assets/site.css", ".statement { --sw: 14; }\n.x { background: url(%00); }\n"),
     "url('%00') decodes to a NUL character", 1),
    ("a quoted url() to a real file with a NUL after it, in another stylesheet",
     write("site/assets/extra.css", '.x { background: url("site.css%00"); }\n'),
     "url('site.css%00') decodes to a NUL character", 1),
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

# (description, mutation, the escaped finding the gate must print on a strict ASCII stdout, with
# exit 1 and no traceback)
ASCII_CASES = [
    ("a site/_redirects line naming /draft/ with a euro sign in its path",
     redirects("/draft/€ /index.html 302\n" + LATEST),
     "'/draft/\\u20ac /index.html 302' names /draft/"),
    ("a latest link whose target carries a euro sign",
     redirects("/downloads/secureconfig-latest.zip /€ 302\n"
               f"/downloads/secureconfig-plugin-latest.zip /downloads/{PLUGIN_ZIP} 302\n"),
     "'/downloads/secureconfig-latest.zip /\\u20ac 302' is not `"),
]


def generated(edit_content, extra=None):
    """Build the pages from a scratch copy of their sources with 1 content edit, then run
    build-site.py --check and check_draft.py on it: the source-to-generated-page path."""
    d = Path(tempfile.mkdtemp())
    try:
        for rel in ("scripts/build-site.py", "tools/check_csp_hashes.py", "tools/check_draft.py",
                    "tools/gen_hosted.py", "tools/_archives.py", "tools/_reason.py",
                    "site-src/content.json", "README.md", "tools/version_basis_guides.txt",
                    "tools/guide_quality.tsv"):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, d / rel)
        shutil.copytree(ROOT / "site" / "assets", d / "site" / "assets")
        for name in ("_headers", "llms.txt", "llms-full.txt", "secureconfig-instructions.md",
                     "robots.txt", "sitemap.xml", "favicon.svg"):
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


def staged():
    """Build the root pages and, beside them, the `draft` branch's staging form
    (`--base /draft/ --out site/draft`) from a scratch copy of their sources, then run the staged
    --check, the root --check and check_draft.py: [(exit, output)] for those 3."""
    d = Path(tempfile.mkdtemp())
    try:
        for rel in ("scripts/build-site.py", "tools/check_csp_hashes.py", "tools/check_draft.py",
                    "tools/gen_hosted.py", "tools/_archives.py", "tools/_reason.py",
                    "site-src/content.json", "README.md", "tools/version_basis_guides.txt",
                    "tools/guide_quality.tsv"):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, d / rel)
        shutil.copytree(ROOT / "site" / "assets", d / "site" / "assets")
        build = str(d / "scripts" / "build-site.py")
        out = []
        for args in ([], ["--base", "/draft/", "--out", "site/draft"]):
            r = subprocess.run([sys.executable, "-I", "-B", build, *args], capture_output=True,
                               text=True, timeout=120)
            if r.returncode:
                return [(r.returncode, f"the build {args} failed: {(r.stdout + r.stderr).strip()}")] * 3
        for cmd in ([build, "--check", "--base", "/draft/", "--out", "site/draft"],
                    [build, "--check"],
                    [str(d / "tools" / "check_draft.py"), "--root", str(d)]):
            r = subprocess.run([sys.executable, "-I", "-B", *cmd], capture_output=True, text=True,
                               timeout=120)
            out.append((r.returncode, (r.stdout + r.stderr).strip()))
        return out
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    failures = []
    # The pristine copy carries the advisory's plain-text copy, so the pristine case below shows the
    # gate accepts a build-written .txt under site/advisories/.
    if not (ROOT / ADVISORY_TEXT).is_file():
        failures.append(f"{ADVISORY_TEXT} is missing, so the pristine case does not show the gate "
                        f"accepts it; rerun python3 -I -B scripts/build-site.py")
    for desc, mutate, expected, want in CASES:
        rc, out = run(mutate)
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    for desc, mutate, expected in ASCII_CASES:
        rc, out = run(mutate, ascii_stdout=True)
        if rc != 1 or expected not in out or "Traceback (most recent call last):" in out:
            failures.append(f"{desc}, on an ASCII stdout: expected exit 1, {expected!r} and no "
                            f"traceback, got exit {rc}: {out!r}")
    # Each SINGLE_FORM line is caught by its own corpus form and by no other.
    sys.path.insert(0, str(TOOLS))
    from check_draft import DRAFT_REFS, normalized, unpathable
    # unpathable() also names a character the file system encoding cannot encode, which no page
    # or stylesheet read as UTF-8 can carry, so it is checked here in process.
    for text, want in (("guides/index.html", None), ("x\x00", "a NUL character"),
                       ("x\ud800", "a character the file system encoding cannot encode")):
        if unpathable(text) != want:
            failures.append(f"unpathable({text!a}) is {unpathable(text)!r}, not {want!r}")
    for line, form, _ in SINGLE_FORM:
        forms = "".join(f for f, p in zip("abcde", DRAFT_REFS) if p.search(normalized(line)))
        if forms != form:
            failures.append(f"{line.strip()!r}: expected only form {form} to match, got {forms!r}")
    # The gate's published targets are scripts/build-site.py's PUBLISHED without _headers, so the
    # two lists cannot drift apart.
    from check_draft import PUBLISHED_TARGETS
    spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build-site.py")
    build_site = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_site)
    if set(PUBLISHED_TARGETS) != set(build_site.PUBLISHED) - {"_headers"}:
        failures.append(f"check_draft.PUBLISHED_TARGETS {PUBLISHED_TARGETS!r} is not "
                        f"scripts/build-site.py's PUBLISHED without _headers")
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
    # The `draft` branch's staging form keeps working (its own --check passes), and a draft tree
    # beside the root pages, as on `main`, fails the root --check and this gate (SPECIFICATION
    # 4.1 items 0 and 3).
    (s, sout), (c, cout), (g, gout) = staged()
    if s or "match a fresh build (base /draft/)" not in sout:
        failures.append(f"the staging form --base /draft/ --out site/draft did not pass its own "
                        f"--check: {sout!r}")
    if c != 1 or "'site/draft/index.html' is not a page this build writes" not in cout:
        failures.append(f"the root --check accepted a staged draft tree under site/draft/: {cout!r}")
    if g != 1 or f"'site/draft' exists (folder); {NO_TREE}" not in gout:
        failures.append(f"the gate accepted a staged draft tree under site/draft/: {gout!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    refusals = sum(1 for case in CASES if case[3])
    print(f"  ok    {len(CASES)} self-containment, indexability and published-index cases at the "
          f"root ({refusals} refusals and {len(CASES) - refusals} accepted changes, the pristine "
          f"site among them), {len(ASCII_CASES)} refusals printed escaped on an ASCII stdout, "
          f"2 generated-page cases (a Unicode host refused, a site.css accepted by the build "
          f"and the gate), and the staging form built beside the root pages (its own --check "
          f"passes; the root --check and the gate refuse the draft tree)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
