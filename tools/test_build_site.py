#!/usr/bin/env python3
"""Cases for scripts/build-site.py: its refusals, its base path, and its --check mode.

The refusals are SPECIFICATION section 12's: a page carrying a dash character (U+2010 to
U+2015, U+2212), an inline style or style= attribute, an inline script, an on* attribute or "what
this is" framing is never written. Each is planted in a real generated page and must be refused,
while the page as generated passes.
The base path must reach every internal link and asset at / (the default since promotion) and at
/draft/ (the staging form). At the root, every page is indexable except the 404 page and the
/draft/ review page, which carry the noindex meta; a staged build is noindex everywhere. The
review page carries its canonical, description and link previews at every base (as auditthis.ai's
/draft/ page does), and no other page names /draft/. At the root each indexable page and the
review page carry their description, the link-preview tags (og:site_name after og:type) and their
canonical in the template's head order; the 404 page and a staged build's other pages carry no
previews.
--check must report a one-byte change, an extra page (.html or .htm in any case) and a missing
page at any base; a stray file outside assets/baseline/ is refused in a staged build and allowed
at the root, where the published files (llms.txt, robots.txt, _headers) sit beside the pages.
"""
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
    pages = build_site.Builder("/").build()
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

    # The base path reaches every internal link and asset, at the root and in the staging form.
    staged_pages = build_site.Builder("/draft/").build()
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        for name, text in built.items():
            for needle in (f'href="{base}assets/baseline/baseline.css"', f'href="{base}guides/"',
                           f'src="{base}assets/baseline/logos/secureconfig.svg"'):
                if needle not in text:
                    failures.append(f"base {base}: {name} lacks {needle}")

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

    # At the root each indexable page and the review page carry their description, then the link
    # previews (og:site_name after og:type, as auditthis.ai orders it), then the icons and
    # stylesheets, then their canonical URL; the 404 page carries no link previews, canonical or
    # description, and a staged build's other pages no link previews or canonical.
    for name, text in pages.items():
        head = text.split("</head>", 1)[0]
        if name == "404.html":
            if 'property="og:' in head or 'name="twitter:' in head:
                failures.append(f"base /: {name} carries link-preview tags")
            if 'rel="canonical"' in head or 'name="description"' in head:
                failures.append("base /: 404.html carries a canonical or a description")
            continue
        url = build_site.ORIGIN + "/" + name[:-len("index.html")]
        needles = ("</title>", '<meta name="description" content="',
                   '<meta property="og:type" content="website">',
                   '<meta property="og:site_name" content="SecureConfig.ai">',
                   f'<meta property="og:url" content="{url}">', '<meta property="og:title" content="',
                   '<meta property="og:description" content="',
                   f'<meta property="og:image" content="{build_site.CARD}">',
                   '<meta property="og:image:type" content="image/png">',
                   '<meta property="og:image:width" content="1200">',
                   '<meta property="og:image:height" content="630">',
                   '<meta property="og:image:alt" content="',
                   '<meta name="twitter:card" content="summary_large_image">',
                   '<meta name="twitter:title" content="', '<meta name="twitter:description" content="',
                   f'<meta name="twitter:image" content="{build_site.CARD}">',
                   '<meta name="twitter:image:alt" content="', '<link rel="icon" ',
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
        # At the root base the published files sit beside the pages, so a non-page stray passes
        # --check here; the CSP and self-containment gates read the real tree.
        (out / "llms.txt").write_text("# index\n", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check at the root refused a non-page file beside the pages: {text!r}")
        (out / "llms.txt").unlink()
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
    print(f"  ok    {len(plants)} planted refusals, the base path at / and /draft/ with the root's "
          f"indexability, link previews and canonicals and the review page's canonical and link "
          f"previews, and --check on a changed, an extra .html "
          f"and .HTM page, a missing page, a root-base non-page file, and the staged strays")
    return 0


if __name__ == "__main__":
    sys.exit(main())
