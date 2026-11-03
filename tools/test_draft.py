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
that the build's --check and this gate both accept.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
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
     "site/llms.txt names a /draft path", 1),
    ("llms-full.txt naming a draft URL",
     write("site/llms-full.txt", "See https://secureconfig.ai/draft/guides/ for the new index.\n"),
     "site/llms-full.txt names a secureconfig.ai/draft URL", 1),
    ("llms-full.txt quoting an IETF draft URL, which is not the site",
     write("site/llms-full.txt", "https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/\n"),
     "8 draft pages", 0),
    ("a live page linking the draft", edit("site/index.html", "</footer>", '<a href="/draft/">draft</a></footer>'),
     "is a live page and its href='/draft/' reaches /draft/", 1),
    ("a live page linking the draft with a relative path",
     edit("site/index.html", "</footer>", '<a href="draft/">draft</a></footer>'),
     "is a live page and its href='draft/' reaches /draft/", 1),
    ("a live page linking the draft through a character reference",
     edit("site/index.html", "</footer>", '<a href="/&#100;raft/">draft</a></footer>'),
     "is a live page and its href='/draft/' reaches /draft/", 1),
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
     "reaches /draft/", 1),
    ("a live page linking the draft through an encoded dot segment",
     edit("site/index.html", "</footer>", '<a href="/x/%2e%2e/draft/">draft</a></footer>'),
     "reaches /draft/", 1),
    ("a live page refreshing to the draft",
     edit("site/404.html", "</head>", '<meta http-equiv="refresh" content="0;url=/draft/">\n</head>'),
     "http-equiv refresh='/draft/' reaches /draft/", 1),
    ("llms-full.txt naming the draft before a full stop",
     write("site/llms-full.txt", "The new site is at https://secureconfig.ai/draft.\n"),
     "names a secureconfig.ai/draft URL", 1),
    ("llms-full.txt naming the draft before a comma",
     write("site/llms-full.txt", "See secureconfig.ai/draft, then the guides.\n"),
     "names a secureconfig.ai/draft URL", 1),
    ("llms-full.txt naming the draft before a semicolon",
     write("site/llms-full.txt", "See secureconfig.ai/draft; then the guides.\n"),
     "names a secureconfig.ai/draft URL", 1),
    ("llms-full.txt naming the draft before a backtick",
     write("site/llms-full.txt", "Open `https://secureconfig.ai/draft` to review.\n"),
     "names a secureconfig.ai/draft URL", 1),
    ("llms-full.txt naming a /drafts path, which is not the draft",
     write("site/llms-full.txt", "See https://secureconfig.ai/drafts-archive for history.\n"),
     "8 draft pages", 0),
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
          f"{len(CASES) - refusals} accepted changes, the pristine draft among them), and 2 "
          f"generated-page cases (a Unicode host refused, a site.css accepted by the build and the gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
