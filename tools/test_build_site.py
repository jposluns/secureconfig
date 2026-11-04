#!/usr/bin/env python3
"""Cases for scripts/build-site.py: its refusals, its base path, and its --check mode.

The refusals are SPECIFICATION section 12's: a page carrying a dash character (U+2010 to
U+2015, U+2212), an inline style or style= attribute, an inline script, an on* attribute or "what
this is" framing is never written. Each is planted in a real generated page and must be refused,
while the page as generated passes. An on* attribute is a name in a tag: an onload after a quoted
value holding ">" is refused, and the word "on" inside a closed quoted value (a description reading
"Read on GitHub") is not refused.
The base path must reach every internal link and asset at / (the default since promotion) and at
/draft/ (the staging form). At the root, every page is indexable except the 404 page and the
/draft/ review page, which carry the noindex meta; a staged build is noindex everywhere. The
review page carries its canonical, description and link previews at every base (as auditthis.ai's
/draft/ page does), and no other page names /draft/. At the root each indexable page and the
review page carry their title, description, the link-preview tags (og:site_name after og:type)
and their canonical in the template's head order, each tag with its full value (the page title with
" | SecureConfig.ai", the description from site-src/content.json, the card's alt text); the 404
page and a staged build's other pages carry no previews.
Every page, the 404 and the review page included, at both bases, carries the light and dark switch
of baseline 1.6.0 (SPECIFICATION 7.33) exactly as the reference pages write it, once, as the last
child of the top bar after its nav, and loads scheme.js once, right after the touch icon and
before the first stylesheet, with data-cfasync="false" before src and no defer or async.
--check must report a one-byte change, an extra page (.html or .htm in any case) and a missing
page at any base; a stray file outside assets/baseline/ other than assets/site.css is refused at
both bases, except at the root a published file (PUBLISHED, such as llms.txt) beside the pages.
"""
import html
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SCRIPT = ROOT / "scripts" / "build-site.py"
spec = importlib.util.spec_from_file_location("build_site", SCRIPT)
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)
ROBOTS_META = '<meta name="robots" content="noindex, nofollow">'
# The switch as baseline 1.6.0's reference pages write it (reference/404.html, line 18), copied
# here by hand so that a drift in the generator's copy is caught.
REFERENCE_SWITCH = (
    '<button class="scheme" type="button" data-scheme-toggle aria-pressed="false" hidden><svg '
    'class="moon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'focusable="false"><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7z"/></svg>'
    '<svg class="sun" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'focusable="false"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 '
    '12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/>'
    '</svg><span class="vh">Dark mode</span></button>')
# Each page with link previews at the root: its title and the site-src/content.json key of its
# description.
PREVIEWS = {"index.html": ("Home", "home"), "guides/index.html": ("Guides", "guides"),
            "for-ai/index.html": ("For AI assistants", "for_ai"),
            "for-humans/index.html": ("For humans", "for_humans"),
            "checklist/index.html": ("Checklist", "checklist"),
            "disclosure/index.html": ("Disclosure", "disclosure"),
            "license/index.html": ("Licence", "license"), "draft/index.html": ("Draft review", "draft")}


def refused(text):
    try:
        build_site.refuse("page", text)
    except build_site.Refused as exc:
        return str(exc)
    return None


def run(*args):
    r = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], capture_output=True,
                       text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    failures = []
    builder = build_site.Builder("/")
    pages = builder.build()
    home = pages["index.html"]
    rail_page = pages["disclosure/index.html"]
    plants = [
        ("a static aria-current on a rail link",
         rail_page.replace('<li><a href="#d-1">', '<li><a href="#d-1" aria-current="true">', 1),
         "static aria-current"),
        ("a section rail without rail.js",
         rail_page.replace('<script src="/assets/baseline/rail.js" defer></script>\n', "", 1),
         "without rail.js"),
        ("an en dash", home.replace("Start here", "Start–here", 1), "dash character"),
        ("an em dash", home.replace("Start here", "Start—here", 1), "dash character"),
        ("a hyphen character U+2010", home.replace("Start here", "Start‐here", 1), "dash character"),
        ("a figure dash", home.replace("Start here", "Start‒here", 1), "dash character"),
        ("a horizontal bar", home.replace("Start here", "Start―here", 1), "dash character"),
        ("a minus sign", home.replace("Start here", "Start−here", 1), "dash character"),
        ("a style block", home.replace("</head>", "<style>p{}</style></head>", 1), "inline style"),
        ("a style= attribute", home.replace('<p class="intro">', '<p class="intro" style="x">', 1),
         "inline style"),
        ("an inline script", home.replace("</head>", "<script>x()</script></head>", 1), "inline script"),
        ("a script with a src and a body",
         home.replace("</head>", '<script src="/x.js">x()</script></head>', 1), "inline script"),
        ("an onclick attribute", home.replace('<p class="intro">', '<p class="intro" onclick="x()">', 1),
         "on* attribute"),
        ("a valueless onload attribute", home.replace("<body>", "<body onload>", 1), "on* attribute"),
        # The on* check reads attribute names, so a ">" inside a quoted value does not end the tag,
        # and a word in a closed quoted value hides no name after it.
        ('an onload after a quoted value holding ">"',
         home.replace('<p class="intro">', '<p class="intro" title="a>b" onload>', 1), "on* attribute"),
        ('an onload after a quoted value reading "read on"',
         home.replace('<p class="intro">', '<p class="intro" title="read on" onload>', 1),
         "on* attribute"),
        ("an on after a quote that never closes", home + '<p title="read on>', "on* attribute"),
        ('"what this is" framing', home.replace("Start here", "What this is", 1), "what this is"),
    ]
    for desc, text, expected in plants:
        if text == home:
            failures.append(f"{desc}: the plant did not change the page")
            continue
        why = refused(text)
        if why is None or expected not in why:
            failures.append(f"{desc}: expected a refusal naming {expected!r}, got {why!r}")
    for name, text in pages.items():
        if refused(text) is not None:
            failures.append(f"{name} as generated is refused: {refused(text)}")
    # #1189 drafting: a description may use the word "on" inside its quoted value.
    worded = home.replace('<meta name="description" content="',
                          '<meta name="description" content="Read on GitHub. ', 1)
    if worded == home or refused(worded) is not None:
        failures.append(f'a description reading "Read on GitHub" was refused: {refused(worded)!r}')

    # The base path reaches every internal link and asset, at the root and in the staging form.
    staged_pages = build_site.Builder("/draft/").build()
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        for name, text in built.items():
            for needle in (f'href="{base}assets/baseline/baseline.css"', f'href="{base}guides/"',
                           f'src="{base}assets/baseline/logos/secureconfig.svg"'):
                if needle not in text:
                    failures.append(f"base {base}: {name} lacks {needle}")

    # Baseline 1.6.0 (SPECIFICATION 7.33): the switch on every page, the 404 and the review page
    # included, as the last child of the top bar, and scheme.js between the touch icon and the
    # first stylesheet, without defer or async.
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        script = f'<script data-cfasync="false" src="{base}assets/baseline/scheme.js"></script>'
        head = (f'secureconfig-touch.png">\n{script}\n'
                f'<link rel="stylesheet" href="{base}assets/baseline/fonts.css">\n')
        for name, text in built.items():
            if text.count(REFERENCE_SWITCH) != 1 or f"</nav>{REFERENCE_SWITCH}</header>" not in text:
                failures.append(f"base {base}: {name} does not carry the reference switch exactly "
                                f"once as the last child of header.mast, after nav.nav")
            if text.count("scheme.js") != 1 or text.count(head) != 1:
                failures.append(f"base {base}: {name} does not load scheme.js once, after the touch "
                                f"icon and before the first stylesheet, as {script}")

    # At the root, only the 404 page and the /draft/ review page are noindex; a staged build is
    # noindex everywhere. The review page carries its canonical, description and link previews at
    # every base, and no other page names /draft/.
    for name, text in pages.items():
        hidden = name in ("404.html", "draft/index.html")
        if (ROBOTS_META in text) is not hidden:
            failures.append(f"base /: {name} {'lost' if hidden else 'still carries'} the noindex meta")
        if name != "draft/index.html" and "/draft/" in text:
            failures.append(f"base /: {name} names /draft/")
    for name, text in staged_pages.items():
        if ROBOTS_META not in text:
            failures.append(f"base /draft/: {name} lacks the noindex meta")
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        review = built["draft/index.html"]
        for needle in ('<link rel="canonical" href="https://secureconfig.ai/draft/">',
                       '<meta name="description" content="The path where new versions of '
                       'secureconfig.ai are staged for review before they are published.">',
                       '<meta property="og:url" content="https://secureconfig.ai/draft/">',
                       '<meta property="og:title" content="Draft review | SecureConfig.ai">',
                       '<meta name="twitter:title" content="Draft review | SecureConfig.ai">',
                       "<h1>Draft review</h1>", '<p class="lbl first">Drafts</p>'):
            if needle not in review:
                failures.append(f"base {base}: the review page lacks {needle}")

    # At the root each indexable page and the review page carry their title and description, then
    # the link previews (og:site_name after og:type, as auditthis.ai orders it), then the icons and
    # stylesheets, then their canonical URL, each tag with its full value; the 404 page carries no
    # link previews, canonical or description, and a staged build's other pages no link previews or
    # canonical.
    for name, text in pages.items():
        head = text.split("</head>", 1)[0]
        if name == "404.html":
            if 'property="og:' in head or 'name="twitter:' in head:
                failures.append(f"base /: {name} carries link-preview tags")
            if 'rel="canonical"' in head or 'name="description"' in head:
                failures.append("base /: 404.html carries a canonical or a description")
            continue
        url = build_site.ORIGIN + "/" + name[:-len("index.html")]
        # #1189 QA: the full value of each tag, not its prefix.
        title, key = PREVIEWS[name]
        full = html.escape(f"{title} | SecureConfig.ai", quote=True)
        desc = html.escape(builder.n(builder.c[key]["description"]["text"]), quote=True)
        alt = html.escape(build_site.CARD_ALT, quote=True)
        needles = (f"<title>{title} | SecureConfig.ai</title>",
                   f'<meta name="description" content="{desc}">',
                   '<meta property="og:type" content="website">',
                   '<meta property="og:site_name" content="SecureConfig.ai">',
                   f'<meta property="og:url" content="{url}">',
                   f'<meta property="og:title" content="{full}">',
                   f'<meta property="og:description" content="{desc}">',
                   f'<meta property="og:image" content="{build_site.CARD}">',
                   '<meta property="og:image:type" content="image/png">',
                   '<meta property="og:image:width" content="1200">',
                   '<meta property="og:image:height" content="630">',
                   f'<meta property="og:image:alt" content="{alt}">',
                   '<meta name="twitter:card" content="summary_large_image">',
                   f'<meta name="twitter:title" content="{full}">',
                   f'<meta name="twitter:description" content="{desc}">',
                   f'<meta name="twitter:image" content="{build_site.CARD}">',
                   f'<meta name="twitter:image:alt" content="{alt}">', '<link rel="icon" ',
                   '<script data-cfasync="false" src="/assets/baseline/scheme.js"></script>',
                   '<link rel="stylesheet" href="/assets/baseline/baseline.css">',
                   f'<link rel="canonical" href="{url}">')
        at = [head.find(n) for n in needles]
        if -1 in at or at != sorted(at):
            missing = [n for n, i in zip(needles, at) if i == -1]
            failures.append(f"base /: {name} lacks the head's description, link previews and "
                            f"canonical in order (missing {missing!r})")
    for name, text in staged_pages.items():
        if name != "draft/index.html" and ('rel="canonical"' in text or 'property="og:' in text):
            failures.append(f"base /draft/: {name} carries a canonical or link-preview tags")

    # --check against a build it did not write, at the root base (the default).
    d = Path(tempfile.mkdtemp())
    try:
        out = d / "root"
        rc, text = run("--out", str(out))
        if rc != 0:
            failures.append(f"a build into a scratch folder failed: {text!r}")
        rc, text = run("--check", "--out", str(out))
        if rc != 0 or "match a fresh build" not in text:
            failures.append(f"--check on a fresh build did not pass: {text!r}")
        target = out / "guides" / "index.html"
        data = bytearray(target.read_bytes())
        data[100] ^= 1
        target.write_bytes(bytes(data))
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "guides/index.html differs" not in text:
            failures.append(f"--check missed a one-byte change: {text!r}")
        run("--out", str(out))
        (out / "extra").mkdir()
        (out / "extra" / "index.html").write_text("<p>x</p>", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "extra/index.html is not a page this build writes" not in text:
            failures.append(f"--check missed an extra page: {text!r}")
        shutil.rmtree(out / "extra")
        # QA round 1 of #1182: a page is .html or .htm in any case.
        (out / "Extra.HTM").write_text("<p>x</p>", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "Extra.HTM is not a page this build writes" not in text:
            failures.append(f"--check missed an extra .HTM page: {text!r}")
        (out / "Extra.HTM").unlink()
        # At the root base the published files (PUBLISHED) sit beside the pages and pass --check.
        (out / "llms.txt").write_text("# index\n", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check at the root refused a published file beside the pages: {text!r}")
        (out / "llms.txt").unlink()
        # #1189 QA: any other file at the root is refused, so a stray script cannot ship.
        for stray in ("assets/other.js", "notes.txt"):
            (out / stray).parent.mkdir(exist_ok=True)
            (out / stray).write_text("x\n", encoding="utf-8")
            rc, text = run("--check", "--out", str(out))
            if rc != 1 or f"{stray} is neither a page this build writes" not in text:
                failures.append(f"--check at the root accepted a stray {stray}: {text!r}")
            (out / stray).unlink()
        (out / "404.html").unlink()
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "404.html is missing" not in text:
            failures.append(f"--check missed a missing page: {text!r}")

        # The staging form refuses a stray file outside assets/baseline/ and allows the optional
        # assets/site.css (baseline README); tools/check_draft.py holds its grammar.
        staged = d / "draft"
        rc, text = run("--base", "/draft/", "--out", str(staged))
        if rc != 0:
            failures.append(f"a staged build into a scratch folder failed: {text!r}")
        (staged / "assets").mkdir()
        (staged / "assets" / "live.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 1 or "assets/live.css is neither a page this build writes" not in text:
            failures.append(f"staged --check missed a stray file outside assets/baseline/: {text!r}")
        (staged / "assets" / "live.css").unlink()
        (staged / "assets" / "baseline").mkdir()
        (staged / "assets" / "baseline" / "baseline.css").write_text("p{}", encoding="utf-8")
        (staged / "assets" / "site.css").write_text(".statement { --sw: 13.9; }\n", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 0:
            failures.append(f"staged --check refused assets/baseline/ or site.css, which are "
                            f"allowed: {text!r}")
        (staged / "assets" / "other.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 1 or "assets/other.css is neither" not in text:
            failures.append(f"staged --check accepted assets/other.css beside site.css: {text!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    rc, text = run("--base", "draft")
    if rc != 2 or "must start and end with /" not in text:
        failures.append(f"a base path without slashes was accepted: {text!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(plants)} planted refusals and a description using the word on, the base "
          f"path at / and /draft/ with the root's indexability, link previews at their full values "
          f"and canonicals and the review page's canonical and link previews, the light and dark "
          f"switch and scheme.js on every page at both bases, and --check on a changed, an extra "
          f".html and .HTM page, a missing page, a root-base published file and strays, and the "
          f"staged strays")
    return 0


if __name__ == "__main__":
    sys.exit(main())
