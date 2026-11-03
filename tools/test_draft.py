#!/usr/bin/env python3
"""Cases for check_draft.py: each way the staged draft could leak into search or out of /draft/.

Each failing case copies the real draft and the live files the gate reads, makes 1 change and
asserts that the gate exits 1 with a message naming the defect; each passing case makes a change
the gate must accept (the pristine copy among them). A mutation that no longer applies RAISES, so a
page edit cannot turn a case into a pristine run. The cases added in QA round 1 of #1182 cover the
bypasses that review found: a browser-normalized host, a trailing-dot or upper-case host, URL
attributes beyond href and src, http-equiv, CSS @import, the site.css grammar, robots meta elements
read as elements, .htm pages, site/_redirects, relative and entity-encoded live links to the draft,
and site/llms-full.txt. Round 2 added non-ASCII hosts (including 1 written in content.json and
generated), first-wins duplicate attributes, `background`, live links through a backslash, an
encoded dot segment and a meta refresh, llms-full.txt URLs followed by punctuation, and a site.css
that the build's --check and this gate both accept. Round 3 replaced URL emulation on live pages and
in the index files with the folded draft-segment rule, and added extra-slash, doubly encoded,
dot-segment and other-host spellings, refreshes without `url=` (refused as http-equiv), robots.txt
and sitemap.xml cases, and guards that IETF drafts, `/drafts-archive`, this repository's
`site/draft/` folder and other hosts' paths in llms-full.txt pass. Round 4 added the fold's
fail-closed limits (a tab, newline or carriage return inside `draft`, a leading or trailing space,
a leading newline, and a value still changing after 32 rounds of percent-decoding, beside 1 that
resolves in 17) and robots.txt's `*` and `$` wildcards, with `/draft-` and `/drafts` still passing.
The LOW rows from rounds 4 and 5 added llms-full.txt tokens that a quote splits off this site's
host, that hold the host anywhere (percent-encoded too), or that carry a scheme-like prefix other
than http or https (`see:/draft/`, 2 prefixes, inside brackets, and `ftp://`), a token that is no
site token still changing after 32 rounds, and guards that a mail address on this site,
`/drafts-archive` and `/draft-` paths behind a prefix, a quoted IETF draft, a quoted repository
path and a control character in another host's URL pass.

Beside the cases: 3 cases read fold's still-changing flag directly, and the base-path checks build
the pages with scripts/build-site.py into a scratch folder, once with check_draft.BASE (the staged
form) and once with `--base /` (the promoted form). Every root-relative URL a page carries is
written to llms-full.txt as a bare path, as a URL on this site and behind `see:`: the gate refuses
exactly the forms of the staged URLs under the base (not the 2 live files) and accepts every form
of the promoted build's URLs. segment_rule(`/`) matches none of them, so the draft-segment rules
switch off at the root.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import check_draft  # noqa: E402  (BASE, SITE_HOST, fold, segment_rule and the page parser)

LIVE = ("_headers", "llms.txt", "robots.txt", "sitemap.xml", "index.html", "404.html")


def run(mutate=None):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / "site" / "draft", d / "site" / "draft")
        for name in LIVE:
            if (ROOT / "site" / name).is_file():
                shutil.copyfile(ROOT / "site" / name, d / "site" / name)
        if mutate is not None:
            mutate(d)
        r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "check_draft.py"), "--root",
                            str(d)], capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edit(rel, old, new):
    def mutate(d):
        path = d / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"mutation {old!r} no longer matches {rel}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return mutate


def append(rel, extra):
    def mutate(d):
        path = d / rel
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    return mutate


def write(rel, text):
    def mutate(d):
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8")
    return mutate


HOME = "site/draft/index.html"
GUIDES = "site/draft/guides/index.html"
META = '<meta name="robots" content="noindex, nofollow">'
START = 'href="/draft/guides/"'
STRAY = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>x</title>\n'
         '</head>\n<body><a href="/">Live</a></body>\n</html>\n')


def link(value):
    """The landing page's start link pointed at value."""
    return edit(HOME, START, f'href="{value}"')


# (description, mutation, expected text, expected exit)
CASES = [
    ("a draft page without the robots meta", edit(HOME, META + "\n", ""), "exactly 1 robots meta", 1),
    ("a draft page with a second robots meta", edit(HOME, META, META + META), "exactly 1 robots meta", 1),
    ("the robots meta only inside a comment", edit(HOME, META, f"<!-- {META} -->"),
     "exactly 1 robots meta", 1),
    ("a second robots meta, single-quoted, allowing indexing",
     edit(HOME, META, META + "<meta name='ROBOTS' content='index, follow'>"), "exactly 1 robots meta", 1),
    ("the robots meta in upper case with other spacing",
     edit(HOME, META, '<META NAME="Robots" CONTENT="NOINDEX,NOFOLLOW">'), "8 draft pages", 0),
    ("a link to a live page", link("/guides/"), "outside the base path", 1),
    ("a stylesheet loaded from the live root",
     edit(HOME, 'href="/draft/assets/baseline/baseline.css"', 'href="/assets/baseline.css"'),
     "outside the base path", 1),
    ("a relative link", link("guides/"), "relative path", 1),
    ("a ../ path out of the draft", link("/draft/../guides/"), "names no file", 1),
    ("a link to a draft page that does not exist", link("/draft/nowhere/"), "names no file", 1),
    ("an absolute link to this site's own host", link("https://secureconfig.ai/"), "own host", 1),
    ("this site's host with a trailing dot", link("https://secureconfig.ai./"), "own host", 1),
    ("this site's host in upper case", link("HTTPS://SECURECONFIG.AI/"), "own host", 1),
    ("this site's host percent-encoded", link("https://secureconfig%2Eai/"), "own host", 1),
    ("a Pages alias host", link("https://secureconfig.pages.dev/"), "own host", 1),
    ("https:/// with the site's host after it, which a browser opens as the site",
     link("https:///secureconfig.ai/"), "no host right after //", 1),
    ("https: with 1 slash", link("https:/secureconfig.ai/"), "no host right after //", 1),
    ("a backslash in a URL", link("https:\\\\secureconfig.ai/"), "backslash", 1),
    ("a tab inside a URL", link("/draft/gui&#9;des/"), "whitespace", 1),
    ("a javascript: URL", link("javascript:void(0)"), "javascript: scheme", 1),
    ("a scheme-relative URL", link("//example.net/"), "scheme-relative", 1),
    ("an xlink:href with a javascript: URL",
     edit(HOME, "<a class=\"start\"", '<svg><a xlink:href="javascript:x()"></a></svg><a class="start"'),
     "xlink:href='javascript:x()' uses the javascript: scheme", 1),
    ("a formaction to the live root",
     edit(HOME, "<a class=\"start\"", '<button formaction="/">x</button><a class="start"'),
     "formaction='/' is outside the base path", 1),
    ("a ping to the live root", edit(HOME, START, START + ' ping="/draft/ /"'),
     "ping='/' is outside the base path", 1),
    ("a srcset candidate on the live root",
     edit(HOME, 'alt="A terminal', 'srcset="/draft/assets/baseline/logos/secureconfig.svg 1x, /x.svg 2x" alt="A terminal'),
     "srcset='/x.svg' is outside the base path", 1),
    ("an imagesrcset on the live root",
     edit(HOME, "</head>", '<link rel="preload" as="image" imagesrcset="/x.png 1x">\n</head>'),
     "imagesrcset='/x.png' is outside the base path", 1),
    ("a poster on the live root", edit(HOME, "<a class=\"start\"", '<video poster="/p.png"></video><a class="start"'),
     "poster='/p.png' is outside the base path", 1),
    ("a meta refresh", edit(HOME, "</head>", '<meta http-equiv="refresh" content="0;url=/">\n</head>'),
     "http-equiv", 1),
    ("a new-tab link without the hidden hint",
     edit(GUIDES, 'free-certificates<span class="vh"> (opens in a new tab)</span>', "free-certificates"),
     "does not say so", 1),
    ("a stray .htm page with no robots meta", write("site/draft/extra.htm", STRAY),
     "site/draft/extra.htm must carry exactly 1 robots meta", 1),
    ("a stray .HTML page linking the live root", write("site/draft/x/Page.HTML", STRAY),
     "site/draft/x/Page.HTML:7: href='/' is outside the base path", 1),
    ("the /draft/* rule without X-Robots-Tag",
     edit("site/_headers", "  X-Robots-Tag: noindex\n", ""), "X-Robots-Tag: noindex", 1),
    ("a second /draft/* rule", append("site/_headers", "\n/draft/*\n  X-Robots-Tag: noindex\n"),
     "2 /draft/* rules", 1),
    ("a site/_redirects file while the draft is staged", write("site/_redirects", "/old /draft/ 301\n"),
     "site/_redirects exists", 1),
    ("llms.txt naming the draft", append("site/llms.txt", "\n- [draft](https://secureconfig.ai/draft/)\n"),
     "site/llms.txt names a draft path segment", 1),
    ("llms-full.txt naming a draft URL",
     write("site/llms-full.txt", "See https://secureconfig.ai/draft/guides/ for the new index.\n"),
     "site/llms-full.txt names a draft path segment on this site", 1),
    ("llms-full.txt quoting an IETF draft URL, which is not the site",
     write("site/llms-full.txt", "https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/\n"),
     "8 draft pages", 0),
    ("a live page linking the draft", edit("site/index.html", "</footer>", '<a href="/draft/">draft</a></footer>'),
     "is a live page and its href='/draft/' names a draft path segment", 1),
    ("a live page linking the draft with a relative path",
     edit("site/index.html", "</footer>", '<a href="draft/">draft</a></footer>'),
     "is a live page and its href='draft/' names a draft path segment", 1),
    ("a live page linking the draft through a character reference",
     edit("site/index.html", "</footer>", '<a href="/&#100;raft/">draft</a></footer>'),
     "is a live page and its href='/draft/' names a draft path segment", 1),
    ("a live page linking the draft by its absolute URL",
     edit("site/404.html", "</body>", '<a href="https://secureconfig.ai/draft/">d</a></body>'),
     "site/404.html", 1),
    ("a stylesheet url() outside the draft",
     write("site/draft/assets/site.css", ".statement { --sw: 14; }\n.x { background: url(/logo.svg); }\n"),
     "is not a relative path", 1),
    ("a stylesheet @import", write("site/draft/assets/site.css", '@import "/live.css";\n.statement { --sw: 14; }\n'),
     "carries @import", 1),
    ("a stylesheet @import written with a CSS escape",
     write("site/draft/assets/site.css", '@\\69mport "/live.css";\n.statement { --sw: 14; }\n'),
     "carries @import", 1),
    ("site.css setting another property",
     write("site/draft/assets/site.css", ".statement { --sw: 14; color: red; }\n"), "may hold only", 1),
    ("site.css with a declaration outside a rule", write("site/draft/assets/site.css", "--sw: 14;\n"),
     "may hold only", 1),
    ("site.css with another at-rule", write("site/draft/assets/site.css", "@font-face { --sw: 1; }\n"),
     "may hold only", 1),
    ("site.css setting only the 2 constants, at the top level and for dark mode",
     write("site/draft/assets/site.css", "/* measured */\n.site-secureconfig .statement { --sw: 13.9; }\n"
           "@media (prefers-color-scheme: dark) { :root:not([data-scheme=\"light\"]) .statement { --sw: 14.8; } }\n"
           ".site-secureconfig .rail { --logo-inset: 0.12; }\n"),
     "8 draft pages", 0),
    ("an inner page linking the Licence page",
     edit(GUIDES, '<a href="/draft/for-ai/">', '<a href="/draft/license/">Licence</a><a href="/draft/for-ai/">'),
     "only the landing page", 1),
    # QA round 2 of #1182.
    ("an ideographic full stop in the site's host", link("https://secureconfig\u3002ai/"),
     "not plain ASCII", 1),
    ("fullwidth letters in the site's host", link("https://\uff53\uff45\uff43\uff55\uff52\uff45config.ai/"),
     "not plain ASCII", 1),
    ("a percent-encoded non-ASCII host", link("https://secureconfig%E3%80%82ai/"), "not plain ASCII", 1),
    ("a duplicate name attribute on a second robots meta, the first being robots",
     edit(HOME, META, META + '<meta name="robots" name="x" content="index, follow">'),
     "exactly 1 robots meta", 1),
    ("a background attribute on the live root",
     edit(HOME, "<a class=\"start\"", '<table background="/bg.png"></table><a class="start"'),
     "background='/bg.png' is outside the base path", 1),
    ("a live page linking the draft with a backslash",
     edit("site/index.html", "</footer>", '<a href="\\draft/">draft</a></footer>'),
     "names a draft path segment once folded", 1),
    ("a live page linking the draft through an encoded dot segment",
     edit("site/index.html", "</footer>", '<a href="/x/%2e%2e/draft/">draft</a></footer>'),
     "names a draft path segment once folded ('/x/../draft/')", 1),
    ("a live page refreshing to the draft",
     edit("site/404.html", "</head>", '<meta http-equiv="refresh" content="0;url=/draft/">\n</head>'),
     "site/404.html:56: is a live page and carries http-equiv", 1),
    ("llms-full.txt naming the draft before a full stop",
     write("site/llms-full.txt", "The new site is at https://secureconfig.ai/draft.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming the draft before a comma",
     write("site/llms-full.txt", "See secureconfig.ai/draft, then the guides.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming the draft before a semicolon",
     write("site/llms-full.txt", "See secureconfig.ai/draft; then the guides.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming the draft before a backtick",
     write("site/llms-full.txt", "Open `https://secureconfig.ai/draft` to review.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming a /drafts path, which is not the draft",
     write("site/llms-full.txt", "See https://secureconfig.ai/drafts-archive for history.\n"),
     "8 draft pages", 0),
    # QA round 3 of #1182: the folded draft-segment rule, which does not emulate URL parsing.
    ("a live page linking https:////secureconfig.ai/draft/",
     edit("site/index.html", "</footer>", '<a href="https:////secureconfig.ai/draft/">d</a></footer>'),
     "names a draft path segment", 1),
    ("a live page linking https:///secureconfig.ai/draft/",
     edit("site/index.html", "</footer>", '<a href="https:///secureconfig.ai/draft/">d</a></footer>'),
     "names a draft path segment", 1),
    ("a live page linking a doubly percent-encoded slash before draft",
     edit("site/index.html", "</footer>", '<a href="/x%252fdraft">d</a></footer>'),
     "names a draft path segment once folded ('/x/draft')", 1),
    ("a live page linking another host's draft path, refused whatever the host",
     edit("site/index.html", "</footer>", '<a href="https://example.net/draft/">d</a></footer>'),
     "names a draft path segment", 1),
    ("a live page refreshing without url=",
     edit("site/404.html", "</head>", '<meta http-equiv="refresh" content="0; /draft/">\n</head>'),
     "is a live page and carries http-equiv", 1),
    ("a live page refreshing with a comma",
     edit("site/404.html", "</head>", '<meta http-equiv="refresh" content="0, /draft/">\n</head>'),
     "is a live page and carries http-equiv", 1),
    ("a live page linking an IETF draft, which is no draft path segment",
     edit("site/index.html", "</footer>", '<a href="https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/">d</a></footer>'),
     "8 draft pages", 0),
    ("a live page linking /drafts-archive, which is no draft path segment",
     edit("site/index.html", "</footer>", '<a href="/drafts-archive/">d</a></footer>'),
     "8 draft pages", 0),
    ("llms-full.txt naming the draft through a dot segment",
     write("site/llms-full.txt", "See https://secureconfig.ai/x/../draft/ for the draft.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming the draft through an encoded dot segment",
     write("site/llms-full.txt", "See https://secureconfig.ai/%2e/draft/ for the draft.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming the draft after extra slashes",
     write("site/llms-full.txt", "See https:////secureconfig.ai/draft/ for the draft.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming a bare same-site draft path",
     write("site/llms-full.txt", "The draft is served from /draft/ on the site.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming this repository's site/draft/ folder, which is a repository path",
     write("site/llms-full.txt", "The copied files are under `site/draft/assets/baseline/`.\n"),
     "8 draft pages", 0),
    ("llms-full.txt naming another host's draft path, which the guides may cite",
     write("site/llms-full.txt", "See https://example.net/draft/spec for the vendor's draft.\n"),
     "8 draft pages", 0),
    ("robots.txt naming the draft through a dot segment",
     append("site/robots.txt", "\nDisallow: /x/%2e%2e/draft/\n"), "site/robots.txt names a draft path segment", 1),
    ("sitemap.xml naming the draft through an entity",
     edit("site/sitemap.xml", "</urlset>", "<url><loc>https://secureconfig.ai/&#100;raft/</loc></url></urlset>"),
     "site/sitemap.xml names a draft path segment", 1),
    # QA round 4 of #1182: fail-closed limits of the fold, and robots.txt wildcards.
    ("a live link with a tab character reference inside draft",
     edit("site/index.html", "</footer>", '<a href="/dr&#9;aft/">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a live link with a newline character reference inside draft",
     edit("site/index.html", "</footer>", '<a href="/dr&#10;aft/">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a live link with a carriage-return character reference inside draft",
     edit("site/index.html", "</footer>", '<a href="/dr&#13;aft/">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a live link with a leading space",
     edit("site/index.html", "</footer>", '<a href=" draft/">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a live link with a trailing space",
     edit("site/index.html", "</footer>", '<a href="/guides/ ">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a live link with a leading newline character reference",
     edit("site/index.html", "</footer>", '<a href="&#10;draft/">d</a></footer>'),
     "contains an ASCII control character or a space", 1),
    ("a sitemap URL with a tab character reference inside draft",
     edit("site/sitemap.xml", "</urlset>", "<url><loc>https://secureconfig.ai/dr&#9;aft/</loc></url></urlset>"),
     "contains an ASCII control character or a space", 1),
    ("a live link that needs 17 rounds of percent-decoding to read /draft/",
     edit("site/index.html", "</footer>", '<a href="/' + "%25" + "25" * 15 + '64raft/">d</a></footer>'),
     "names a draft path segment once folded ('/draft/')", 1),
    ("a live link still changing after 32 rounds of percent-decoding",
     edit("site/index.html", "</footer>", '<a href="/' + "%25" + "25" * 40 + '64raft/">d</a></footer>'),
     "is still changing after 32 rounds of percent-decoding", 1),
    ("robots.txt disallowing /draft* with a wildcard",
     append("site/robots.txt", "\nDisallow: /draft*\n"), "site/robots.txt names a draft path segment", 1),
    ("robots.txt allowing /draft$ with an end anchor",
     append("site/robots.txt", "\nAllow: /draft$\n"), "site/robots.txt names a draft path segment", 1),
    ("robots.txt naming /draft- and /drafts paths, which are no draft path segment",
     append("site/robots.txt", "\nDisallow: /draft-ietf-x\nDisallow: /drafts\n"), "8 draft pages", 0),
    # QA rounds 4 and 5 of #1182: llms-full.txt tokens split by a quote or read through a prefix.
    ("llms-full.txt naming the draft after a quote inside a URL on this site",
     write("site/llms-full.txt", "See https://secureconfig.ai/a'b/../../draft/ for the draft.\n"),
     "names a draft path segment on this site in \"https://secureconfig.ai/a'b/../../draft/\"", 1),
    ("llms-full.txt naming the draft behind a prose prefix read as a scheme",
     write("site/llms-full.txt", "The staged site, see:/draft/, is not indexed.\n"),
     "names a draft path segment on this site in 'see:/draft/'", 1),
    ("llms-full.txt naming the draft behind 2 scheme-like prefixes",
     write("site/llms-full.txt", "See note:see:/draft/ for it.\n"),
     "names a draft path segment on this site in 'note:see:/draft/'", 1),
    ("llms-full.txt naming the draft behind a prose prefix inside brackets",
     write("site/llms-full.txt", "The staged site (see:/draft/) is not indexed.\n"),
     "names a draft path segment on this site in 'see:/draft/'", 1),
    ("llms-full.txt naming this site's host inside another host's URL, beside a draft segment",
     write("site/llms-full.txt", "See https://example.net/?u=secureconfig.ai/draft/ for it.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming this site's percent-encoded host inside another host's URL",
     write("site/llms-full.txt", "See https://example.net/secureconfig%2Eai/draft/ for it.\n"),
     "names a draft path segment on this site", 1),
    ("llms-full.txt naming a draft path through another scheme, read as a bare path",
     write("site/llms-full.txt", "See ftp://example.net/draft/ for it.\n"),
     "names a draft path segment on this site in 'ftp://example.net/draft/'", 1),
    ("llms-full.txt naming another host's URL still changing after 32 rounds of percent-decoding",
     write("site/llms-full.txt", "See https://example.net/%25" + "25" * 40 + "41 for it.\n"),
     "is still changing after 32 rounds of percent-decoding", 1),
    ("llms-full.txt naming this site's host in a mail address and /drafts-archive behind a prefix",
     write("site/llms-full.txt", "Write to mailto:security@secureconfig.ai or see:/drafts-archive.\n"),
     "8 draft pages", 0),
    ("llms-full.txt quoting an IETF draft behind a prefix, and a /draft- path behind one",
     write("site/llms-full.txt",
           "Read 'see:https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/' and see:/draft-notes.\n"),
     "8 draft pages", 0),
    ("llms-full.txt quoting this repository's site/draft/ folder",
     write("site/llms-full.txt", "Run cp -r 'site/draft/assets/' \"site/draft/x/\" now.\n"),
     "8 draft pages", 0),
    ("llms-full.txt naming another host's URL with a tab reference, which is no site token",
     write("site/llms-full.txt", "See https://example.net/a&#9;b for it.\n"), "8 draft pages", 0),
    ("the pristine draft", None, "8 draft pages", 0),
]


def generated(edit_content, extra=None):
    """Build the draft from a scratch copy of its sources with 1 content edit, then run
    build-site.py --check and check_draft.py on it: the source-to-generated-page path."""
    d = Path(tempfile.mkdtemp())
    try:
        for rel in ("scripts/build-site.py", "tools/check_csp_hashes.py", "tools/check_draft.py",
                    "site-src/content.json", "README.md", "tools/version_basis_guides.txt"):
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, d / rel)
        shutil.copytree(ROOT / "site" / "draft" / "assets", d / "site" / "draft" / "assets")
        for name in LIVE:
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


def built_urls(base):
    """The root-relative URLs on the pages scripts/build-site.py writes with --base base, into a
    scratch folder."""
    d = Path(tempfile.mkdtemp())
    try:
        r = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "scripts" / "build-site.py"),
                            "--base", base, "--out", str(d / "out")],
                           capture_output=True, text=True, timeout=120)
        if r.returncode:
            raise AssertionError(f"build-site.py --base {base} exited {r.returncode}: "
                                 f"{(r.stdout + r.stderr).strip()!r}")
        urls = set()
        for page in check_draft.page_files(d / "out"):
            for _, _, value in check_draft.parse(page.read_text(encoding="utf-8")).urls:
                if value.startswith("/") and not value.startswith("//"):
                    urls.add(value)
        return sorted(urls)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def forms(url):
    """A root-relative URL as llms-full.txt could name it: bare, on this site, behind `see:`."""
    return [url, f"https://{check_draft.SITE_HOST}{url}", f"see:{url}"]


def base_path_failures():
    """The staged build's same-site URLs are each refused in llms-full.txt, the promoted build's
    are all accepted, and segment_rule(`/`) matches none of them."""
    failures = []
    staged, promoted = built_urls(check_draft.BASE), built_urls("/")
    under = [u for u in staged if u.startswith(check_draft.BASE)]
    if not under or not promoted:
        failures.append(f"base paths: the builds carried {len(under)} URLs under "
                        f"{check_draft.BASE} and {len(promoted)} at /; each needs at least 1")
    tokens = [f for u in staged for f in forms(u)]
    rc, out = run(write("site/llms-full.txt", "\n".join(tokens) + "\n"))
    named = [t for t in tokens if f"on this site in {t!r};" in out]
    want = [f for u in under for f in forms(u)]
    if rc != 1 or named != want:
        failures.append(f"base {check_draft.BASE}: llms-full.txt should refuse exactly the "
                        f"{len(want)} forms of the URLs under the base; exit {rc}, refused "
                        f"{named!r}: {out!r}")
    rc, out = run(write("site/llms-full.txt", "\n".join(f for u in promoted for f in forms(u)) + "\n"))
    if rc != 0 or "8 draft pages" not in out:
        failures.append(f"base /: llms-full.txt naming the promoted build's URLs should pass; "
                        f"exit {rc}: {out!r}")
    root_rule = check_draft.segment_rule("/")
    matched = [f for u in staged + promoted for f in forms(u)
               if root_rule.search(check_draft.fold(f, entities=True)[0])]
    if matched:
        failures.append(f"base /: segment_rule('/') should match nothing; it matched {matched!r}")
    if check_draft.segment_rule(check_draft.BASE).pattern != check_draft.DRAFT_SEGMENT.pattern:
        failures.append("DRAFT_SEGMENT is not segment_rule(BASE)")
    return failures


def fold_flag_failures():
    """fold flags a value still changing after MAX_DECODES rounds, and only that value: 1 that
    settles in 17 rounds has no reason, and 1 with a tab has a reason but no flag."""
    # (value, still changing, has a reason)
    cases = (("/%25" + "25" * 40 + "64raft/", True, True), ("/%25" + "25" * 15 + "64raft/", False, False),
             ("/dr&#9;aft/", False, True))
    failures = []
    for value, changing_want, why_want in cases:
        _, why, changing = check_draft.fold(value, entities=True)
        if changing is not changing_want or (why is not None) is not why_want:
            failures.append(f"fold({value!r}): still changing {changing}, reason {why!r}; "
                            f"expected still changing {changing_want}, a reason {why_want}")
    return failures


def main():
    failures = fold_flag_failures() + base_path_failures()
    for desc, mutate, expected, want in CASES:
        rc, out = run(mutate)
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
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
        None, lambda d: (d / "site/draft/assets/site.css").write_text(css, encoding="utf-8"))
    if b or c or g:
        failures.append(f"a site.css setting only --sw was refused: build {b} {bout!r}, check {c} "
                        f"{cout!r}, gate {g} {gout!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    refusals = sum(1 for case in CASES if case[3])
    print(f"  ok    {len(CASES)} draft noindex and self-containment cases ({refusals} refusals and "
          f"{len(CASES) - refusals} accepted changes, the pristine draft among them), 2 "
          f"generated-page cases (a Unicode host refused, a site.css accepted by the build and the "
          f"gate), 3 fold-flag cases, and the base-path checks at {check_draft.BASE} and /")
    return 0


if __name__ == "__main__":
    sys.exit(main())
