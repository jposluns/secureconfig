#!/usr/bin/env python3
"""Cases for check_csp_hashes.py under the template page model, since promotion.

WHAT CARRIED OVER, AND WHAT RETIRED. Six review rounds and the row 3.18 and P5 rulings built this
suite against the hash-pinning gate that guarded the old hand-written pages. At promotion the
pages became generated template pages with no inline block anywhere, and the gate dropped the
hash model, #1181's temporary A15 'unsafe-inline' acceptance and the /draft/* rule model. Each
case group was kept, retargeted or dropped as follows, with the reason:

  - KEPT, unchanged: every row 3.18 and P5 document and filesystem case (SVG scripts, handlers,
    javascript: URLs with each URL_NOISE character, style elements and attributes, fail-closed
    parsing, refused suffixes, dotfiles, trailing dots, compressed names, symlinks, FIFOs, the
    site-root shapes, and the injected I/O failures). None of them depended on the hash model.
  - KEPT, retargeted to the generated pages: the page-model refusals whose rule still applies
    under a shape of 0 inline blocks: an inline <style> or <script>, a self-closing <style/>, a
    charset other than exactly one `<meta charset="utf-8">`, a NUL byte, a style= attribute, a
    valued and a valueless on* handler (structural and literal, the <svg><title> smuggling
    included by the allowlist below), rules 1 to 4 of the refused contexts (handler-like text,
    inert text holding `<`, <math>, malformed end tags) and the element allowlist. The staged
    draft's page cases BECAME these cases: the template model that covered site/draft/ now covers
    every page, so "a baseline script written any other way", "an element outside the allowlist"
    and their kin run against the root pages.
  - DROPPED, hash-model cases: the pin-matching, directive-resolution (script-src-elem /
    default-src fallback), orphan-pin, base64url, sha384, repinned-pass and CRLF-pin cases all
    exercised machinery the gate no longer contains; the policy carries no hash and no page
    carries a block to pin. The repinned-pass variants of rounds 3 to 5 (which isolated each new
    rule from a pin mismatch) collapse into plain refusals, because with no pins there is nothing
    to mask a refusal; their rules are still exercised below.
  - DROPPED, A15 live-policy cases: the temporary 'unsafe-inline' acceptance left the gate; the
    shared policy is now required byte for byte, so every widening those cases probed
    ('strict-dynamic', extra hosts, a hash or nonce beside 'unsafe-inline') is refused by the
    exact-policy rule, which has its own cases below.
  - DROPPED, /draft/* rule-model cases: the rule and its model are gone; reintroducing any
    /draft/* block now fails the no-detach, one-policy or X-Robots-Tag rule, which the header
    cases below pin.
  - DROPPED, wording and base-path-advice cases: they pinned message clauses of the hash model
    (pins that look like nonces, the per-shape handler advice) and the staged/promoted shape
    split, none of which exists in the gate; the surviving messages are pinned by the expected
    substrings of the cases below.
  - The round-1 to round-6 narrative cases that asserted PASSES after a repin (stylesheet text
    with <!-- and -->, a <style> in a JavaScript string) dropped with the blocks they lived in; a
    page has no inline block for such text to sit in, and any <style> opener is refused outright.

BASELINE 1.6.0 CASES. The light and dark switch (SPECIFICATION 7.33) brings 1 script without defer
and 2 inline SVG glyphs. The head script passes only as the generator writes it, as its own line,
once, read as a start tag in <head> after nothing but meta, title and link elements and before any
link whose decoded, case-folded rel holds the token stylesheet; a page without it is refused. Each
other spelling (attribute order, defer, async, a type, a body, another file, host or base path),
each other place (after a `rel="style&#115;heet"` or `rel="preload stylesheet"` link, after a
<div>, text or a comment in <head>, inside <svg> or <title>, after </head>, in <body>), a second
copy, and any other scheme.js (deferred, in an attribute, as text, percent-encoded or split by a
tab or newline in an href, or in text that starts on the head line itself) has its own refusal;
the `</head>` reason is isolated on a page with no stylesheet link before it. The glyphs pass as
generated; inside one, any element but path and circle (an a, g, script, foreignObject, use,
image, style, title or svg, a deferred baseline script included, and any end tag but theirs) is
refused, as are a style= or on* attribute on one and any attribute outside the glyphs'
presentation and geometry attributes, class, aria-hidden and focusable. Rules 2 and 3 of
the refused contexts also have direct cases, each pinning its own message beside the allowlist's:
a textarea, noscript or xmp holding `<`, a <math>, and each SVG integration point (title, desc,
foreignObject, style, script) inside a glyph.

HEADER CASES. site/_headers must carry exactly the shared template policy under the bare /*:
widened, reordered, comma-split, duplicated, detached, path-scoped or host-scoped policies fail,
as does any X-Robots-Tag; a comment between the rule and its headers passes, as Cloudflare allows.
X-Frame-Options, Permissions-Policy and Cross-Origin-Opener-Policy each fail when missing,
changed, set twice, set only under a narrower rule or detached, and X-Content-Type-Options,
Referrer-Policy and Strict-Transport-Security fail when set or detached anywhere.

Exit 0 ok, 1 on a finding.
"""
import contextlib
import gzip
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
PAGE = (ROOT / "site" / "index.html").read_bytes().decode("utf-8")
PAGE_404 = (ROOT / "site" / "404.html").read_bytes().decode("utf-8")
SCRIPTED = (ROOT / "site" / "for-ai" / "index.html").read_bytes().decode("utf-8")
REVIEW = (ROOT / "site" / "draft" / "index.html").read_bytes().decode("utf-8")
HEADERS = (ROOT / "site" / "_headers").read_text(encoding="utf-8")
FAVICON = (ROOT / "site" / "favicon.svg").read_bytes()
COPY_JS = '<script src="/assets/baseline/copy.js" defer></script>'
# Baseline 1.6.0: the 1 head script without defer, and the first stylesheet it must precede.
SCHEME_JS = '<script data-cfasync="false" src="/assets/baseline/scheme.js"></script>'
FONTS_CSS = '<link rel="stylesheet" href="/assets/baseline/fonts.css">'
# The switch's first glyph opening tag, as the generator writes it.
MOON = '<svg class="moon" viewBox="0 0 24 24"'
# The moon glyph's path, as the generator writes it.
MOON_PATH = '<path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7z"/>'
HEAD_PLACE = "is not in <head> before the first stylesheet"
HEAD_AFTER = HEAD_PLACE + ": it is after </head>"
# The home page without its stylesheet links, so a head line after </head> meets </head> before
# any stylesheet and the </head> reason is the one reported.
NO_STYLESHEETS, STYLESHEETS_REMOVED = re.subn(r'<link rel="stylesheet" [^>]*>\n', "", PAGE)
if not STYLESHEETS_REMOVED:
    raise AssertionError("the home page no longer carries a stylesheet link to remove")
SCHEME_ELSEWHERE = "scheme.js appears outside the 1 head line this gate accepts"
SCHEME_DEFERRED = '<script src="/assets/baseline/scheme.js" defer></script>'
SVG_CONTENT = "inside an inline <svg>, where this gate admits only <path> and <circle>"
# The smallest page that fits the model: every page carries the head script exactly once.
STRAY_PAGE = ('<!doctype html>\n<head>\n<meta charset="utf-8">\n' + SCHEME_JS
              + '\n</head>\n<p>x</p>\n')
# The default fixture pages: the generated home and 404, a page that loads a baseline script, and
# the /draft/ review page.
FIXTURE = {"index.html": PAGE, "404.html": PAGE_404, "for-ai/index.html": SCRIPTED,
           "draft/index.html": REVIEW}
OK_PAGES = "4 page(s) under site"
SHARED = "shared template policy"
# The line of the moon glyph's path on the page that loads copy.js, for a finding that names it.
FOR_AI_MOON_LINE = SCRIPTED[:SCRIPTED.index(MOON_PATH)].count("\n") + 1
# Section 9's other header lines under /*, as site/_headers writes them.
XFO_LINE = "  X-Frame-Options: DENY\n"
COOP_LINE = "  Cross-Origin-Opener-Policy: same-origin\n"
CLOUDFLARE_SENDS = "which Cloudflare sends itself"


def run_against(page=None, headers=None, extra_files=None, setup=None):
    """Run the real gate against a copy of the site. Returns (exit, stdout and stderr).

    `page` is None (the fixture pages), a str (an index.html override), or a dict keyed by a
    FIXTURE path overriding that page; an unknown key RAISES, so a typo cannot silently test a
    pristine fixture. The real `site/favicon.svg` is written into every run. `extra_files` writes
    extra files under site/, in subdirectories as named, as text (written as UTF-8) or bytes
    (written as given). `setup` is called with the copy's root, for entries that are not plain
    files (a link, a FIFO, a replaced site/). A gate that hangs (on a FIFO it should never open)
    is reported as exit 124 rather than hanging the suite.
    """
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        (d / "site").mkdir()
        shutil.copy(TOOLS / "check_csp_hashes.py", d / "tools" / "check_csp_hashes.py")
        pages = dict(FIXTURE)
        if isinstance(page, str):
            pages["index.html"] = page
        elif isinstance(page, dict):
            for k, v in page.items():
                if k not in pages:
                    raise KeyError(f"run_against got an unknown page override {k!r}")
                pages[k] = v
        # Bytes, not text: the newline cases are only cases if the bytes survive the write.
        for name, text in pages.items():
            target = d / "site" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(text.encode("utf-8"))
        (d / "site" / "favicon.svg").write_bytes(FAVICON)
        for name, content in (extra_files or {}).items():
            target = d / "site" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        (d / "site" / "_headers").write_text(
            headers if headers is not None else HEADERS, encoding="utf-8")
        if setup is not None:
            setup(d)
        try:
            r = subprocess.run([sys.executable, "-B", "tools/check_csp_hashes.py"], cwd=d,
                               capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired:
            return 124, "the gate timed out"
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edited(base, old, new):
    """base with old replaced once; RAISES when old no longer matches, so a page edit cannot turn
    a mutation case into a pristine run."""
    if old not in base:
        raise AssertionError(f"mutation {old!r} no longer matches the page")
    return base.replace(old, new, 1)


# The wording every page on* finding shares, whatever the policy.
ON_RULE = ("refuses every on* handler on a page (P5), whatever the site's script-src or "
           "script-src-attr would let a browser do with it")
ON_TEXT = "outside the inline <style> and <script> blocks"
ALLOWLIST = "is not in the page allowlist"
MALFORMED = "has a malformed end tag"
SVG_REFUSAL = "inside an inline <svg>"

# (description, page override, headers override, must_fail, expected substring or None)
CASES = [
    ("the generated pages under the shared policy", None, None, False, OK_PAGES),

    # THE PAGE MODEL: no inline block, scripts only in the generator's baseline form.
    ("an inline <script> on the home page",
     edited(PAGE, "</head>", "<script>alert(1)</script>\n</head>"), None, True,
     "has 1 <script> elements and this gate models exactly 0"),
    ("an inline <style> on the home page",
     edited(PAGE, "</head>", "<style>p{}</style>\n</head>"), None, True,
     "has 1 <style> elements and this gate models exactly 0"),
    ("a baseline script without defer",
     {"for-ai/index.html": edited(SCRIPTED, COPY_JS,
                                  '<script src="/assets/baseline/copy.js"></script>')}, None, True,
     "<script> elements"),
    ("a script from another host",
     {"for-ai/index.html": edited(SCRIPTED, COPY_JS,
                                  '<script src="https://cdn.example.net/x.js" defer></script>')},
     None, True, "<script> elements"),
    ("a baseline script with a body",
     {"for-ai/index.html": edited(SCRIPTED, COPY_JS,
                                  COPY_JS.replace("></script>", ">alert(1)</script>"))}, None, True,
     "<script> elements"),
    ("a baseline script still written with the staged /draft/ path",
     {"for-ai/index.html": edited(SCRIPTED, COPY_JS,
                                  '<script src="/draft/assets/baseline/copy.js" defer></script>')},
     None, True, "<script> elements"),

    # THE 1 HEAD SCRIPT (baseline 1.6.0, SPECIFICATION 7.33): accepted exactly as the generator
    # writes it, in <head> before the first stylesheet, once; every other non-defer script refused.
    ("src before data-cfasync on the head script",
     edited(PAGE, SCHEME_JS, '<script src="/assets/baseline/scheme.js" data-cfasync="false"></script>'),
     None, True, "<script> elements"),
    ("the head script without data-cfasync",
     edited(PAGE, SCHEME_JS, '<script src="/assets/baseline/scheme.js"></script>'), None, True,
     "<script> elements"),
    ("the head script with data-cfasync=\"true\"",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace('"false"', '"true"')), None, True,
     "<script> elements"),
    ("the head script with defer",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("></script>", " defer></script>")), None, True,
     "<script> elements"),
    ("the head script with async",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("></script>", " async></script>")), None, True,
     "<script> elements"),
    ("the head script with a type",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("<script ", '<script type="module" ')), None, True,
     "<script> elements"),
    ("the head script with a body",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("></script>", ">alert(1)</script>")), None, True,
     "<script> elements"),
    ("another baseline file in the head script's form",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("scheme.js", "copy.js")), None, True,
     "<script> elements"),
    ("the head script from another host",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("/assets/", "https://cdn.example.net/assets/")),
     None, True, "<script> elements"),
    ("the head script still written with the staged /draft/ path",
     edited(PAGE, SCHEME_JS, SCHEME_JS.replace("/assets/", "/draft/assets/")), None, True,
     "<script> elements"),
    ("the head script after the first stylesheet",
     edited(edited(PAGE, SCHEME_JS + "\n", ""), FONTS_CSS, FONTS_CSS + "\n" + SCHEME_JS), None,
     True, HEAD_PLACE),
    ("the head script after the first stylesheet on the 404 page names the page",
     {"404.html": edited(edited(PAGE_404, SCHEME_JS + "\n", ""), FONTS_CSS,
                         FONTS_CSS + "\n" + SCHEME_JS)}, None, True, "site/404.html:"),
    ("the head script in <body>",
     edited(edited(PAGE, SCHEME_JS + "\n", ""), "</body>", SCHEME_JS + "\n</body>"), None, True,
     HEAD_PLACE),
    ("the head script loaded twice",
     edited(PAGE, SCHEME_JS, SCHEME_JS + "\n" + SCHEME_JS), None, True, "more than once"),
    ("the head script in <head> and again in <body>",
     edited(PAGE, "</body>", SCHEME_JS + "\n</body>"), None, True, "more than once"),
    ("the head script in <head> and again without data-cfasync",
     edited(PAGE, SCHEME_JS, SCHEME_JS + '\n<script src="/assets/baseline/scheme.js"></script>'),
     None, True, "<script> elements"),
    ("a page without the head script",
     edited(PAGE, SCHEME_JS + "\n", ""), None, True, "does not carry the scheme.js head line"),
    # QA round 1 of #1190: scheme.js exactly once, exactly there, read on the page as written.
    ("the deferred spelling of scheme.js in place of the head line",
     edited(PAGE, SCHEME_JS, SCHEME_DEFERRED), None, True, SCHEME_ELSEWHERE),
    ("the deferred spelling of scheme.js in place of the head line is not taken out",
     edited(PAGE, SCHEME_JS, SCHEME_DEFERRED), None, True, "has 1 <script> elements"),
    ("a second, deferred scheme.js in <body>",
     edited(PAGE, "</body>", SCHEME_DEFERRED + "\n</body>"), None, True, SCHEME_ELSEWHERE),
    ("scheme.js in a link's href",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/scheme.js">x</a></p>\n</body>'), None,
     True, SCHEME_ELSEWHERE),
    ("scheme.js in an attribute, spelled with a character reference",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/scheme&#46;js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js as text, in another case",
     edited(PAGE, "</body>", "<p>see Scheme.JS</p>\n</body>"), None, True, SCHEME_ELSEWHERE),
    # QA round 2 of #1190: a URL spelling of scheme.js, read as a URL parser and a host read it.
    ("scheme.js in an href, percent-encoded",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/%73cheme.js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js in an href, percent-encoded twice",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/%2573cheme.js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js in an href, percent-encoded in upper case with an encoded dot",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/%53CHEME%2eJS">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js in an href, split by a tab reference",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/sch&#9;eme.js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js in an href, split by a newline reference",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/sch&#10;eme.js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    ("scheme.js in an href, split by a literal tab",
     edited(PAGE, "</body>", '<p><a href="/assets/baseline/sch\teme.js">x</a></p>\n</body>'),
     None, True, SCHEME_ELSEWHERE),
    # QA round 2 of #1190: the text after the head line starts on its line and is still searched.
    ("scheme.js in a character reference, in the text that starts on the head line",
     edited(PAGE, SCHEME_JS + "\n", SCHEME_JS + "\nsee sch&#101;me.js\n"), None, True,
     SCHEME_ELSEWHERE),
    ('rel="style&#115;heet" before the head script',
     edited(PAGE, SCHEME_JS, '<link rel="style&#115;heet" href="/assets/baseline/fonts.css">\n'
            + SCHEME_JS), None, True, HEAD_PLACE),
    ('rel="preload stylesheet" before the head script',
     edited(PAGE, SCHEME_JS, '<link rel="preload stylesheet" href="/assets/baseline/fonts.css">\n'
            + SCHEME_JS), None, True, HEAD_PLACE),
    ('rel="Alternate\tStyleSheet" before the head script',
     edited(PAGE, SCHEME_JS,
            '<link rel="Alternate\tStyleSheet" href="/assets/baseline/fonts.css">\n' + SCHEME_JS),
     None, True, HEAD_PLACE),
    ("a <div></div> before the head script in <head>",
     edited(PAGE, SCHEME_JS, "<div></div>\n" + SCHEME_JS), None, True, HEAD_PLACE),
    ("text before the head script in <head>, which ends the head in a browser",
     edited(PAGE, SCHEME_JS, "x\n" + SCHEME_JS), None, True, HEAD_PLACE),
    ("a comment before the head script in <head>",
     edited(PAGE, SCHEME_JS, "<!-- x -->\n" + SCHEME_JS), None, True, HEAD_PLACE),
    ("the head line inside <svg> in <head>",
     edited(PAGE, SCHEME_JS, "<svg>\n" + SCHEME_JS + "\n</svg>"), None, True, HEAD_PLACE),
    ("the head line inside <svg> in <head> is refused as SVG content",
     edited(PAGE, SCHEME_JS, "<svg>\n" + SCHEME_JS + "\n</svg>"), None, True,
     "<script> is " + SVG_CONTENT),
    ("the head line inside the moon glyph",
     edited(edited(NO_STYLESHEETS, SCHEME_JS + "\n", ""), MOON_PATH,
            "\n" + SCHEME_JS + "\n" + MOON_PATH), None, True, HEAD_AFTER),
    ("the head line after </head>",
     edited(edited(NO_STYLESHEETS, SCHEME_JS + "\n", ""), "</head>\n",
            "</head>\n" + SCHEME_JS + "\n"), None, True, HEAD_AFTER),
    ("the head line inside <title>",
     edited(edited(PAGE, SCHEME_JS + "\n", ""), "</title>\n", "\n" + SCHEME_JS + "\n</title>\n"),
     None, True, HEAD_PLACE),
    ("a self-closing <style/>",
     edited(PAGE, "</head>", "<style/>\n</head>"), None, True, "self-closing"),
    ("a charset declaration this gate does not obey",
     edited(PAGE, '<meta charset="utf-8">', '<meta charset="windows-1252">'), None, True, "charset"),
    ("the charset declaration removed",
     edited(PAGE, '<meta charset="utf-8">\n', ""), None, True, "charset"),
    ("a NUL byte on a page",
     edited(PAGE, "</body>", "\x00</body>"), None, True, "NUL byte"),

    # style= AND on* HANDLERS, structural and literal, on each kind of page.
    ("a style= attribute on the home page",
     edited(PAGE, "<body>", '<body style="color:red">'), None, True,
     "This gate refuses every style= attribute on a page"),
    ("a style= attribute on the 404 page names the page",
     {"404.html": edited(PAGE_404, "<body>", '<body style="color:red">')}, None, True,
     "site/404.html"),
    ("a valued on* handler", edited(PAGE, "<body>", '<body onload="x()">'), None, True, ON_TEXT),
    ("a valueless on* handler", edited(PAGE, "<body>", "<body onclick>"), None, True, ON_RULE),
    ("an on* handler on the review page names the page",
     {"draft/index.html": edited(REVIEW, "<body>", "<body ONCLICK=go>")}, None, True,
     "site/draft/index.html"),
    ("a handler with a spaced =", edited(PAGE, "<body>", "<body onload = 'x'>"), None, True, ON_TEXT),
    ("handler-like text in prose",
     edited(PAGE, "</body>", "<p>x onclick=alert(1)</p>\n</body>"), None, True, ON_TEXT),
    ("prose on-words are not handlers",
     edited(PAGE, "</body>", "<p>only one on duty, on-call; online, on</p>\n</body>"), None, False,
     OK_PAGES),
    ("data-onload= is not a handler",
     edited(PAGE, "</body>", '<p data-onload="x" data-on>x</p>\n</body>'), None, False, OK_PAGES),

    # THE ELEMENT ALLOWLIST (round 5 of #352): every tag name, read context-free. From baseline
    # 1.6.0 the switch's glyphs bring `svg`, `path` and `circle` into the list and no other SVG
    # element, so the <svg>-smuggling reproductions of rounds 2 to 5 are refused by rule 3 and by
    # the allowlist's refusal of what they carry.
    ("a <title><style> smuggled into an inline <svg>",
     edited(PAGE, "</body>", '<svg><title><style>p{}</style></title></svg>\n</body>'), None, True,
     SVG_REFUSAL),
    ("a <title><style> smuggled into an inline <svg> names the <style>",
     edited(PAGE, "</body>", '<svg><title><style>p{}</style></title></svg>\n</body>'), None, True,
     "element <style> " + ALLOWLIST),
    ("a <title> added to the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<title>Moon</title><path d="M20.5'), None, True, SVG_REFUSAL),
    ("a <desc> added to the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<desc>x</desc><path d="M20.5'), None, True, SVG_REFUSAL),
    ("a <script> inside the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<script>alert(1)</script><path d="M20.5'), None, True,
     SVG_REFUSAL),
    ("a <style> inside the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<style>p{}</style><path d="M20.5'), None, True, SVG_REFUSAL),
    ("a <foreignObject> inside the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<foreignObject></foreignObject><path d="M20.5'), None, True,
     "element <foreignobject> " + ALLOWLIST),
    ("a <use> inside the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<use href="#x"/><path d="M20.5'), None, True,
     "element <use> " + ALLOWLIST),
    ("an <animate> inside the switch's glyph",
     edited(PAGE, '<path d="M20.5', '<animate attributeName="d"/><path d="M20.5'), None, True,
     "element <animate> " + ALLOWLIST),
    ("an empty <g> beside the switch's path",
     edited(PAGE, '<path d="M20.5', '<g></g><path d="M20.5'), None, True,
     "element <g> " + ALLOWLIST),
    # QA round 1 of #1190: SVG CONTENT, read on the page as written: only path and circle.
    ("a <g> that wraps the switch's path",
     edited(PAGE, MOON_PATH, "<g>" + MOON_PATH + "</g>"), None, True, "<g> is " + SVG_CONTENT),
    ("a deferred copy.js inside the moon glyph",
     edited(PAGE, MOON_PATH, COPY_JS + MOON_PATH), None, True, "<script> is " + SVG_CONTENT),
    ("a deferred copy.js inside the moon glyph, on the page that loads copy.js",
     {"for-ai/index.html": edited(SCRIPTED, MOON_PATH, COPY_JS + MOON_PATH)}, None, True,
     f"site/for-ai/index.html:{FOR_AI_MOON_LINE}: <script> is " + SVG_CONTENT),
    ("a link inside the switch's glyph",
     edited(PAGE, MOON_PATH, '<a href="https://example.org">x</a>' + MOON_PATH), None, True,
     "<a> is " + SVG_CONTENT),
    ("a <foreignObject> inside the switch's glyph, as SVG content",
     edited(PAGE, MOON_PATH, "<foreignObject></foreignObject>" + MOON_PATH), None, True,
     "<foreignobject> is " + SVG_CONTENT),
    ("a <use> inside the switch's glyph, as SVG content",
     edited(PAGE, MOON_PATH, '<use href="#x"/>' + MOON_PATH), None, True,
     "<use> is " + SVG_CONTENT),
    ("an <image> inside the switch's glyph",
     edited(PAGE, MOON_PATH, '<image href="/favicon.svg"/>' + MOON_PATH), None, True,
     "<image> is " + SVG_CONTENT),
    ("a <style> inside the switch's glyph, as SVG content",
     edited(PAGE, MOON_PATH, "<style>p{}</style>" + MOON_PATH), None, True,
     "<style> is " + SVG_CONTENT),
    ("a <title> inside the switch's glyph, as SVG content",
     edited(PAGE, MOON_PATH, "<title>Moon</title>" + MOON_PATH), None, True,
     "<title> is " + SVG_CONTENT),
    ("an <svg> inside the switch's glyph",
     edited(PAGE, MOON_PATH, '<svg class="x">' + MOON_PATH + "</svg>"), None, True,
     "<svg> is " + SVG_CONTENT),
    ("an HTML end tag inside the switch's glyph",
     edited(PAGE, MOON_PATH, "</p>" + MOON_PATH), None, True, "</p> is " + SVG_CONTENT),
    ("an explicit </path> inside the switch's glyph passes",
     edited(PAGE, MOON_PATH, MOON_PATH[:-2] + "></path>"), None, False, OK_PAGES),
    ("a style= attribute on the switch's glyph",
     edited(PAGE, MOON, MOON + ' style="fill:red"'), None, True,
     "This gate refuses every style= attribute on a page"),
    ("an onload handler on the switch's glyph",
     edited(PAGE, MOON, MOON + ' onload="x()"'), None, True, ON_TEXT),
    ("a valueless onclick on the switch's path",
     edited(PAGE, '<path d="M20.5', '<path onclick d="M20.5'), None, True, ON_RULE),
    ("an href on the switch's glyph, outside its presentation attributes",
     edited(PAGE, MOON, MOON + ' href="#x"'), None, True, "carries the attribute href"),
    ("a transform on the switch's circle, outside its presentation attributes",
     edited(PAGE, '<circle cx="12"', '<circle transform="scale(2)" cx="12"'), None, True,
     "carries the attribute transform"),
    ("an xmlns:xlink on the switch's glyph, outside its presentation attributes",
     edited(PAGE, MOON, MOON + ' xmlns:xlink="http://www.w3.org/1999/xlink"'), None, True,
     "carries the attribute xmlns:xlink"),
    ("the switch's glyphs as generated, in any case of the tag names, pass",
     PAGE.replace("<svg ", "<SVG ").replace("</svg>", "</SVG>"), None, False, OK_PAGES),
    ("a <details>, which the generator never emits",
     edited(PAGE, "</body>", "<details><summary>x</summary></details>\n</body>"), None, True,
     "element <details> " + ALLOWLIST),
    ("a <frameset> in mixed case",
     edited(PAGE, "</body>", "<FrameSet>\n</body>"), None, True, "element <frameset> " + ALLOWLIST),
    ("an end tag alone",
     edited(PAGE, "</body>", "</select>\n</body>"), None, True, "element <select> " + ALLOWLIST),
    ("an unlisted element inside a comment, read context-free",
     edited(PAGE, "</body>", "<!-- <frameset> -->\n</body>"), None, True,
     "element <frameset> " + ALLOWLIST),
    ("allowed elements in any case pass",
     edited(PAGE, "</body>", "<P>x <SPAN>y</SPAN> <Code>z</Code></P>\n</body>"), None, False,
     OK_PAGES),

    # REFUSED CONTEXTS (rounds 3 and 4 of #352), each rule alone, with only allowlisted names.
    ("a comment holding a <", edited(PAGE, "</body>", "<!-- a <p> c -->\n</body>"), None, True,
     "has a comment whose text"),
    ("a comment holding plain text passes",
     edited(PAGE, "</body>", "<!-- only one on duty; see _headers -->\n</body>"), None, False,
     OK_PAGES),
    ("a CDATA section holding a <", edited(PAGE, "</body>", "<![CDATA[ a <p> c ]]>\n</body>"), None,
     True, "has a CDATA section whose text"),
    ("a bogus declaration holding a <", edited(PAGE, "</body>", "<!thing a <p>\n</body>"), None,
     True, "has a <! declaration whose text"),
    ("a bogus processing instruction holding a <",
     edited(PAGE, "</body>", "<?thing a <p>\n</body>"), None, True, "has a <? declaration whose text"),
    ("a <title> whose content holds a <",
     edited(PAGE, "</body>", "<title>a <p>c</title>\n</body>"), None, True,
     "has a <title> whose content"),
    ("a <title> holding plain text passes",
     re.sub(r"<title>[^<]*</title>", "<title>Only one, on call</title>", PAGE, count=1), None,
     False, OK_PAGES),
    ("a <math> element", edited(PAGE, "</body>", "<math><mi>x</mi></math>\n</body>"), None, True,
     "element <math> " + ALLOWLIST),
    # QA round 1 of #1189: rules 2 and 3 by their own messages, not only by the allowlist's.
    ("a <math> element, by rule 3",
     edited(PAGE, "</body>", "<math><mi>x</mi></math>\n</body>"), None, True,
     "has a <math> element. html.parser reads MathML as HTML"),
    *[(f"a <{name}> whose content holds a <, by rule 2",
       edited(PAGE, "</body>", f"<{name}>a <p> c</{name}>\n</body>"), None, True,
       f"has a <{name}> whose content contains `<` before its </{name}>")
      for name in ("textarea", "noscript", "xmp")],
    *[(f"a <{name}> inside the switch's glyph, by rule 3",
       edited(PAGE, MOON_PATH, f"<{name}></{name}>" + MOON_PATH), None, True,
       f"has a <{name}> inside an inline <svg>. html.parser reads it as an HTML element")
      for name in ("title", "desc", "foreignObject", "style", "script")],
    ("a malformed end tag, </ and a space",
     edited(PAGE, "</body>", "<p>a</ p>b</p>\n</body>"), None, True, MALFORMED),
    ("a malformed end tag, </>", edited(PAGE, "</body>", "<p>a</>b</p>\n</body>"), None, True,
     MALFORMED),
    ("a malformed end tag, </ and a digit",
     edited(PAGE, "</body>", "<p>a</1>b</p>\n</body>"), None, True, MALFORMED),
    ("a malformed end tag, </!", edited(PAGE, "</body>", "<p>a</!x>b</p>\n</body>"), None, True,
     MALFORMED),
    ("a CRLF page, normalized as a browser's tokenizer normalizes it",
     PAGE.replace("\n", "\r\n"), None, False, OK_PAGES),
    ("a lone-CR page, normalized the same way", PAGE.replace("\n", "\r"), None, False, OK_PAGES),

    # THE HEADERS FILE: exactly the shared policy, under /* alone, no detach, no X-Robots-Tag.
    ("style-src widened with 'unsafe-inline'",
     None, HEADERS.replace("style-src 'self';", "style-src 'self' 'unsafe-inline';", 1), True,
     SHARED),
    ("script-src widened with another host",
     None, HEADERS.replace("script-src 'self'", "script-src 'self' https://cdn.example.net", 1),
     True, SHARED),
    ("a hash added to script-src",
     None, HEADERS.replace("script-src 'self'", "script-src 'sha256-" + "A" * 43 + "=' 'self'", 1),
     True, SHARED),
    ("a directive dropped from the policy",
     None, HEADERS.replace(" font-src 'self';", "", 1), True, SHARED),
    ("a comma splitting the value into two policies",
     None, HEADERS.replace("style-src 'self';", "style-src 'none', style-src 'self';", 1), True,
     "comma"),
    ("a second CSP in a host-scoped rule",
     None, HEADERS + "\nhttps://secureconfig.example/*\n  Content-Security-Policy: style-src 'none'\n",
     True, "exactly one Content-Security-Policy"),
    ("a second CSP under a /guides/* rule, which governs the 404 page on those paths",
     None, HEADERS + "\n/guides/*\n  Content-Security-Policy: style-src 'none'\n", True,
     "exactly one Content-Security-Policy"),
    ("a CSP detached under a /guides/* rule",
     None, HEADERS + "\n/guides/*\n  ! Content-Security-Policy\n", True, "detaches"),
    ("the old /draft/* block reintroduced",
     None, HEADERS + "\n/draft/*\n  ! Content-Security-Policy\n  X-Robots-Tag: noindex\n", True,
     "detaches"),
    ("an X-Robots-Tag under the /* rule",
     None, HEADERS.replace("  Cross-Origin-Opener-Policy: same-origin\n",
                           "  Cross-Origin-Opener-Policy: same-origin\n  X-Robots-Tag: noindex\n",
                           1), True, "X-Robots-Tag"),
    ("an X-Robots-Tag under another rule",
     None, HEADERS + "\n/draft/*\n  X-Robots-Tag: noindex\n", True, "X-Robots-Tag"),
    ("an X-Robots-Tag detached",
     None, HEADERS + "\n/guides/*\n  ! X-Robots-Tag\n", True, "X-Robots-Tag"),
    ("the only CSP under a non-root rule",
     None, HEADERS.replace("\n/*\n", "\n/assets/*\n", 1), True, "not the /* rule"),
    ("the CSP under a bare / rule only",
     None, HEADERS.replace("\n/*\n", "\n/\n", 1), True, "not the /* rule"),
    ("the sole CSP under a host-scoped absolute-URL rule",
     None, HEADERS.replace("\n/*\n", "\nhttps://secureconfig.ai/*\n", 1), True, "not the /* rule"),
    ("a root rule with no Content-Security-Policy line",
     None, re.sub(r"^  Content-Security-Policy:.*$", "  X-Other: 1", HEADERS, count=1, flags=re.M),
     True, "no Content-Security-Policy header"),
    ("a Content-Security-Policy line with no colon, which must fail without crashing",
     None, re.sub(r"^  Content-Security-Policy:.*$", "  Content-Security-Policy", HEADERS, count=1,
                  flags=re.M), True, "no Content-Security-Policy header"),
    ("a comment between the rule and its headers, which is valid in _headers",
     None, HEADERS.replace("/*\n", "/*\n# the policy below is held by tools/check_csp_hashes.py\n", 1),
     False, OK_PAGES),

    # QA round 1 of #1189: section 9's other headers, pinned under /*, and none Cloudflare sends.
    ("X-Frame-Options removed", None, edited(HEADERS, XFO_LINE, ""), True,
     "sets X-Frame-Options 0 times"),
    ("X-Frame-Options: SAMEORIGIN",
     None, edited(HEADERS, "X-Frame-Options: DENY", "X-Frame-Options: SAMEORIGIN"), True,
     "sets X-Frame-Options under /* to SAMEORIGIN"),
    ("X-Frame-Options set again under /guides/*",
     None, HEADERS + "\n/guides/*\n  X-Frame-Options: DENY\n", True, "sets X-Frame-Options 2 times"),
    ("X-Frame-Options only under /guides/*",
     None, edited(HEADERS, XFO_LINE, "") + "\n/guides/*\n" + XFO_LINE, True,
     "sets X-Frame-Options under the rule /guides/*"),
    ("X-Frame-Options detached under /guides/*",
     None, HEADERS + "\n/guides/*\n  ! X-Frame-Options\n", True,
     "detaches X-Frame-Options under /guides/*"),
    ("Permissions-Policy removed",
     None, edited(HEADERS, "  Permissions-Policy: ", "  X-Other: "), True,
     "sets Permissions-Policy 0 times"),
    ("Permissions-Policy widened to let the page use the camera",
     None, edited(HEADERS, "camera=()", "camera=(self)"), True,
     "sets Permissions-Policy under /* to"),
    ("Cross-Origin-Opener-Policy removed", None, edited(HEADERS, COOP_LINE, ""), True,
     "sets Cross-Origin-Opener-Policy 0 times"),
    ("Cross-Origin-Opener-Policy weakened to same-origin-allow-popups",
     None, edited(HEADERS, COOP_LINE, COOP_LINE.replace("same-origin", "same-origin-allow-popups")),
     True, "sets Cross-Origin-Opener-Policy under /* to same-origin-allow-popups"),
    *[(f"{name} set under /*",
       None, edited(HEADERS, XFO_LINE, XFO_LINE + f"  {name}: {value}\n"), True,
       f"sets or detaches {name.lower()}, {CLOUDFLARE_SENDS}")
      for name, value in (("X-Content-Type-Options", "nosniff"),
                          ("Referrer-Policy", "strict-origin-when-cross-origin"),
                          ("Strict-Transport-Security", "max-age=31536000"))],
    ("Referrer-Policy detached under /guides/*",
     None, HEADERS + "\n/guides/*\n  ! Referrer-Policy\n", True,
     f"sets or detaches referrer-policy, {CLOUDFLARE_SENDS}"),
]

# Cases carried by run_against arguments rather than page/headers overrides.
EXTRA_ARGS = {}

# Row 3.18 and P5 cases, appended to CASES below and carried by run_against arguments. Each is a
# document, a filesystem entry, a page or a parser input the gate must refuse or must pass. They
# are kept from the hash-model suite unchanged: none of them depended on the hash model.
SCOPE_CASES = []
# The gate's result lines, matched at a line start because run_against strips the first line's indent.
FAIL_LINE = re.compile(r"^\s*FAIL  ", re.M)
OK_LINE = re.compile(r"^\s*ok    ", re.M)


def scope_case(desc, content=None, expected=None, name="assets/probe.svg", setup=None, page=None,
               headers=None):
    """Record one row 3.18 or P5 case: a must-fail if `expected` names the finding, a must-pass if None.

    `content` is written under site/ at `name`; `page` and `headers` are run_against's overrides;
    `setup` makes an entry that is not a plain file.
    """
    desc = "row 3.18: " + desc
    if desc in EXTRA_ARGS:
        raise KeyError(f"duplicate row 3.18 case {desc!r}")
    args = {}
    if content is not None:
        args["extra_files"] = {name: content}
    if setup is not None:
        args["setup"] = setup
    SCOPE_CASES.append((desc, page, headers, expected is not None, expected))
    EXTRA_ARGS[desc] = args


def svg(body="", attrs=""):
    """A minimal SVG with the SVG, a second SVG-bound, a foreign, the XHTML and the XLink prefixes."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:s="http://www.w3.org/2000/svg" '
            'xmlns:x="urn:test" xmlns:h="http://www.w3.org/1999/xhtml" '
            'xmlns:xl="http://www.w3.org/1999/xlink"' + (" " + attrs if attrs else "") + ">"
            + body + "</svg>")


XHTML_DOC = ('<?xml version="1.0" encoding="UTF-8"?>\n<html xmlns="http://www.w3.org/1999/xhtml">'
             '<head><title>t</title></head><body><p>hi</p></body></html>\n')

# Refused suffixes, in every case, in a subdirectory, and even as a directory name.
for suffix in (".xhtml", ".xht"):
    for spelling in (suffix, suffix.upper(), suffix.title()):
        scope_case("refuse " + spelling, XHTML_DOC, "is XHTML", name="nested/probe" + spelling)
for spelling in (".svgz", ".SVGZ", ".Svgz"):
    scope_case("refuse " + spelling, gzip.compress(FAVICON, mtime=0), "compressed SVG",
               name="nested/probe" + spelling)
scope_case("refuse a directory named .XHTML", expected="is XHTML",
           setup=lambda d: (d / "site" / "docs.XHTML").mkdir())

# Clean SVG documents, in every case of the suffix and nested.
for spelling in (".svg", ".SVG", ".SvG"):
    scope_case("clean " + spelling, svg("<path/>"), name="deep/nested/probe" + spelling)
scope_case("the real favicon as a second copy", FAVICON, name="img/logo.svg")
scope_case("unqualified SVG root", "<svg><path/></svg>")
scope_case("prefixed SVG root", '<s:svg xmlns:s="http://www.w3.org/2000/svg"><s:path/></s:svg>')
scope_case("XML declaration", '<?xml version="1.0"?>' + svg())
scope_case("UTF-8 declaration", '<?xml version="1.0" encoding="UTF-8"?>' + svg())
scope_case("lowercase encoding declaration", '<?xml version="1.0" encoding="utf-8"?>' + svg())
scope_case("UTF-8 BOM", b"\xef\xbb\xbf" + svg().encode("utf-8"))
scope_case("CRLF line endings", svg("\r\n<path/>\r\n"))
scope_case("Unicode text", svg("<text>caf" + chr(233) + "</text>"))
scope_case("comments are text",
           svg("<!-- <script/> <style/> onload='x' style='y' href='javascript:z' -->"))
scope_case("CDATA is text", svg("<![CDATA[<script/> <style/> onload='x' javascript:z]]>"))
scope_case("escaped markup is text",
           svg("<text>&lt;script/&gt; &lt;style/&gt; onload= style= javascript:</text>"))
scope_case("ordinary attributes", svg('<path data-onload="x" stroke="red" opacity="1"/>'))
scope_case("presentation attributes are not style",
           svg('<path fill="red" stroke="#fff" stroke-width="1.8" class="icon" id="styled"/>'))
scope_case("names and prose containing on that are not handlers",
           svg('<g id="button" class="icon-on"><title>on = duty, on-call</title></g>'))
scope_case("a non-SVG root is not itself refused",
           '<html xmlns="http://www.w3.org/1999/xhtml"><p>x</p></html>')
scope_case("unrelated regular file", b"\xff\xfe", name="assets/data.bin")
scope_case("empty directory", setup=lambda d: (d / "site" / "empty").mkdir())

# Script elements: any case, any namespace, any body, anywhere.
for tag in ("script", "SCRIPT", "ScRiPt", "s:script", "x:ScRiPt", "h:script"):
    scope_case("script " + tag, svg(f"<{tag}/>"), "script element")
scope_case("nonempty script", svg("<script>alert(1)</script>"), "script element")
scope_case("external script", svg('<script href="other.js"/>'), "script element")
scope_case("script in unqualified subtree", svg('<g xmlns=""><script/></g>'), "script element")
scope_case("script in foreignObject", svg("<foreignObject><h:script/></foreignObject>"),
           "script element")
scope_case("script under a non-SVG root",
           '<html xmlns="http://www.w3.org/1999/xhtml"><script/></html>', "script element")
scope_case("script in .SVG", svg("<script/>"), "script element", name="deep/probe.SVG")
scope_case("script finding names the file", svg("<script/>"), "site/assets/probe.svg:1:")

# Handler attributes: any case, any namespace, any spacing, even empty.
for attr in ("onload", "ONCLICK", "oNbegin", "x:OnLoad", "on", "once"):
    scope_case("handler " + attr, svg(attrs=attr + '="x"'), "on* handler")
for space in (" ", "\t", "\n", "\r\n"):
    scope_case("handler whitespace " + repr(space), svg(f"<g onload{space}={space}'x'/>"),
               "on* handler")
scope_case("empty handler", svg('<g onload=""/>'), "on* handler")
scope_case("handler in foreignObject", svg('<foreignObject><h:p onclick="x"/></foreignObject>'),
           "on* handler")
scope_case("handler finding names the element line", svg("\n<g\n onload='x'/>"),
           "site/assets/probe.svg:2:")

# Fail closed: what cannot be decoded, parsed or modelled is a finding.
for desc, document in (("empty", ""), ("unclosed", "<svg>"), ("mismatched close", "<svg><g></svg>"),
                       ("trailing junk", "<svg/>junk"), ("multiple roots", "<svg/><svg/>"),
                       ("unbound prefix", "<svg><x:script/></svg>"),
                       ("duplicate attributes", '<svg onload="a" onload="b"/>'),
                       ("unquoted attribute", "<svg onload=x/>"),
                       ("unknown entity", "<svg>&unknown;</svg>"), ("NUL", "<svg>\x00</svg>")):
    scope_case("malformed " + desc, document, "cannot inspect SVG")
scope_case("invalid UTF-8", b"<svg>\xff</svg>", "cannot read SVG as UTF-8")
scope_case("UTF-16 bytes", "<svg/>".encode("utf-16"), "cannot read SVG as UTF-8")
scope_case("non-UTF-8 declaration", '<?xml version="1.0" encoding="ISO-8859-1"?><svg/>',
           "encoding declaration names 'ISO-8859-1'")
scope_case("XML 1.1 declaration", '<?xml version="1.1"?><svg/>', "models XML 1.0")
for desc, document in (
        ("bare DTD", "<!DOCTYPE svg><svg/>"),
        ("internal entity", '<!DOCTYPE svg [<!ENTITY e "&#60;script/&#62;">]><svg>&e;</svg>'),
        ("attribute default", '<!DOCTYPE svg [<!ATTLIST svg onload CDATA "x">]><svg/>'),
        ("external DTD", '<!DOCTYPE svg SYSTEM "https://example.com/a.dtd"><svg/>'),
        ("local external DTD", '<!DOCTYPE svg SYSTEM "file:///missing.dtd"><svg/>')):
    scope_case(desc, document, "document type declarations")
scope_case("stylesheet processing instruction",
           '<?xml-stylesheet href="other.xsl" type="text/xsl"?>' + svg(), "processing instructions")
scope_case("other processing instruction", svg("<?custom x?>"), "processing instructions")

# P5 (1): a javascript: URL, in an href, an xlink:href, and set by animation, however spelled.
for desc, document in (
        ("href", svg('<a href="javascript:alert(1)"/>')),
        ("upper-case scheme", svg('<a href="JAVASCRIPT:alert(1)"/>')),
        ("mixed-case scheme", svg('<a href="JavaScript:alert(1)"/>')),
        ("upper-case HREF attribute", svg('<a HREF="javascript:alert(1)"/>')),
        ("xlink href", svg('<a xl:href="javascript:alert(1)"/>')),
        ("leading spaces", svg('<a href="   javascript:alert(1)"/>')),
        ("leading newline reference", svg('<a href="&#10;javascript:alert(1)"/>')),
        ("tab reference inside the scheme", svg('<a href="java&#9;script:alert(1)"/>')),
        ("newline reference inside the scheme", svg('<a href="java&#10;script:alert(1)"/>')),
        ("literal newline inside the scheme, a space to XML, refused as the superset",
         svg('<a href="java\nscript:alert(1)"/>')),
        ("entity-encoded scheme letter", svg('<a href="java&#x73;cript:alert(1)"/>')),
        ("entity-encoded colon", svg('<a href="javascript&#58;alert(1)"/>')),
        ("image href", svg('<image href="javascript:alert(1)"/>')),
        ("use href", svg('<use href="javascript:alert(1)"/>')),
        ("set to", svg('<a href="#x"><set attributeName="href" to="javascript:alert(1)"/></a>')),
        ("animate to", svg('<animate attributeName="href" to="javascript:alert(1)"/>')),
        ("animate to on xlink:href",
         svg('<animate attributeName="xlink:href" to="javascript:alert(1)"/>')),
        ("animate from", svg('<animate attributeName="href" from="javascript:alert(1)" to="#x"/>')),
        ("animate by", svg('<animate attributeName="href" by="javascript:alert(1)"/>')),
        ("animate values, first entry",
         svg('<animate attributeName="href" values="javascript:alert(1);#x"/>')),
        ("animate values, later entry",
         svg('<animate attributeName="href" values="#x; javascript:alert(1)"/>')),
        ("javascript URL in foreignObject",
         svg('<foreignObject><h:a href="javascript:alert(1)"/></foreignObject>')),
        ("javascript URL in an unrelated attribute, refused as the superset",
         svg('<g data-x="javascript:alert(1)"/>'))):
    scope_case("P5 javascript: " + desc, document, "javascript: URL")
scope_case("P5 javascript: finding names the element line", svg('\n<a\n href="javascript:x"/>'),
           "site/assets/probe.svg:2:")
# Round 2 of #352 (codex finding 2): with CR dropped from URL_NOISE every case above still passed.
# Each character an XML 1.0 attribute value can carry to URL_NOISE (tab, LF, CR by reference, and
# space, DEL) now has a case inside the scheme, in an href, an xlink:href, an animation's values and
# a set's to; XML forbids the other C0 controls, so expat refuses them before URL_NOISE is asked.
for ref in ("&#13;", "&#xd;", "&#10;", "&#9;", "&#x7f;"):
    url = f"java{ref}script:alert(1)"
    for where, document in (
            ("href", svg(f'<a href="{url}"/>')), ("xlink:href", svg(f'<a xl:href="{url}"/>')),
            ("animate values", svg(f'<animate attributeName="href" values="#x;{url}"/>')),
            ("set to", svg(f'<a href="#x"><set attributeName="href" to="{url}"/></a>'))):
        scope_case(f"P5 javascript: {ref} inside the scheme, in {where}", document,
                   "javascript: URL")

# P5 (2): inline style, as an element or an attribute, in any case and namespace.
for tag in ("style", "STYLE", "StYlE", "s:style", "x:style", "h:style"):
    scope_case("P5 style element " + tag, svg(f"<{tag}>path{{fill:red}}</{tag}>"), "style element")
scope_case("P5 empty style element", svg("<style/>"), "style element")
scope_case("P5 style element in foreignObject",
           svg("<foreignObject><h:style>p{}</h:style></foreignObject>"), "style element")
for attr in ("style", "STYLE", "Style", "x:style", "h:style"):
    scope_case("P5 style attribute " + attr, svg(f'<path {attr}="fill:red"/>'), "style attribute")
scope_case("P5 empty style attribute", svg('<path style=""/>'), "style attribute")
scope_case("P5 style attribute on the root", svg(attrs='style="fill:red"'), "style attribute")
scope_case("P5 style attribute in foreignObject",
           svg('<foreignObject><h:p style="x"/></foreignObject>'), "style attribute")
scope_case("P5 style finding names the element line", svg("\n<g\n style='x'/>"),
           "site/assets/probe.svg:2:")

# Passing boundary cases: what the rulings do not ask this gate to police, stated in the docstring.
scope_case("a URL in text content is text", svg("<text>javascript:alert(1)</text>"))
scope_case("javascript in a URL's path is not its scheme",
           svg('<a href="https://example.com/javascript:x"/>'))
scope_case("a relative href named javascript", svg('<a href="javascript.svg"/>'))
scope_case("a scheme that merely ends in javascript", svg('<a href="not-javascript:x"/>'))
scope_case("an animation to a fragment",
           svg('<animate attributeName="href" values="#a;#b" to="#c" from="#d"/>'))
scope_case("attribute names containing style", svg('<g data-style="x" class="lifestyle"/>'))
scope_case("plain foreignObject", svg("<foreignObject><h:p>text</h:p></foreignObject>"))
for href in ("#local", "other.svg#id", "https://example.com/a.svg#id", "//example.com/a.svg#id",
             "data:image/svg+xml,example"):
    scope_case("use reference " + href, svg(f'<use href="{href}"/>'))
scope_case("external xlink use outside scope", svg('<use xl:href="https://example.com/a.svg#id"/>'))

# A stray page anywhere under site/ is checked as a page under the template model: the gate has no
# page list any more, so nothing is "unlisted"; what the old unlisted-page refusal protected (a
# page served under the /* policy going unchecked) is protected by checking every page.
for suffix in (".html", ".HTML", ".HtM"):
    scope_case("a nested stray page with an inline style, checked as a page " + suffix,
               '<!doctype html>\n<meta charset="utf-8">\n<style>a{color:red}</style>\n',
               "models exactly 0", name="deep/probe" + suffix)
scope_case("a nested stray page without the charset, checked as a page",
           "<!doctype html>\n<p>x</p>\n", "charset", name="deep/probe.htm")
scope_case("a clean stray page is a page like any other", STRAY_PAGE, name="deep/extra.html")

# Round 2 of #352 (claude finding 2): pathlib gives a dotfile no suffix, so a file named exactly
# `.svg` escaped every rule. The suffix is now the text from the last dot of the whole name.
scope_case("dotfile .svg carrying a script", svg("<script/>"), "script element", name="deep/.svg")
scope_case("dotfile .SVG carrying a handler", svg(attrs='onload="x"'), "on* handler", name=".SVG")
scope_case("clean dotfile .svg is inspected and passes", svg("<path/>"), name="deep/.svg")
for dotfile, expected, content in ((".xhtml", "is XHTML", XHTML_DOC), (".xht", "is XHTML", XHTML_DOC),
                                   (".svgz", "compressed SVG", gzip.compress(FAVICON, mtime=0)),
                                   (".html", "charset", "<!doctype html>"),
                                   (".htm", "charset", "<!doctype html>")):
    scope_case("dotfile " + dotfile, content, expected, name="deep/" + dotfile)
scope_case("an unrelated dotfile is not inspected", "", name=".nojekyll")
# A name ending with a dot, file or directory, is refused: pathlib gives `probe.svg.` the suffix ".".
TRAILING_DOT = "ends with a dot"
for name in ("probe.svg.", "probe.xhtml.", "probe.html.", "probe."):
    scope_case("trailing-dot file " + name, svg("<script/>"), TRAILING_DOT, name="deep/" + name)
scope_case("trailing-dot directory", expected=TRAILING_DOT,
           setup=lambda d: (d / "site" / "docs.").mkdir())
# Compressed forms are refused as .svgz is, since a host serving precompressed files can answer a
# request for the inner name with one.
COMPRESSED = "is compressed, which this gate cannot read"
for name in ("probe.svg.gz", "probe.html.br", "probe.svg.zst", "probe.SVG.GZ", "probe.Br",
             ".gz", ".zst"):
    scope_case("compressed " + name, gzip.compress(FAVICON, mtime=0), COMPRESSED,
               name="deep/" + name)
scope_case("a directory named assets.gz", expected=COMPRESSED,
           setup=lambda d: (d / "site" / "assets.gz").mkdir())


def file_link(d):
    (d / "site" / "linked.svg").symlink_to("favicon.svg")


def page_link(d):
    (d / "site" / "index.html").rename(d / "saved-index")
    (d / "site" / "index.html").symlink_to("../saved-index")


def directory_link(d):
    (d / "outside").mkdir()
    (d / "outside" / "hidden.xhtml").write_text(XHTML_DOC, encoding="utf-8")
    (d / "site" / "linked").symlink_to(d / "outside", target_is_directory=True)


def root_link(d):
    (d / "site").rename(d / "actual-site")
    (d / "site").symlink_to("actual-site", target_is_directory=True)


def missing_root(d):
    shutil.rmtree(d / "site")


def regular_root(d):
    shutil.rmtree(d / "site")
    (d / "site").write_bytes(b"")


for desc, setup in (("file symlink", file_link), ("HTML page symlink", page_link),
                    ("external directory symlink", directory_link), ("site root symlink", root_link),
                    ("dangling symlink", lambda d: (d / "site" / "missing.svg").symlink_to("absent")),
                    ("symlink loop", lambda d: (d / "site" / "loop").symlink_to("loop"))):
    scope_case(desc, expected="is a symbolic link", setup=setup)
scope_case("FIFO named .svg, never opened", expected="not a regular file",
           setup=lambda d: os.mkfifo(d / "site" / "pipe.svg"))
scope_case("missing site root", expected="cannot inspect site entry", setup=missing_root)
scope_case("regular file as site root", expected="is not a directory", setup=regular_root)

CASES += SCOPE_CASES


def io_failure_cases():
    """Run the gate in-process with one Path method made to raise, and require a FAIL for each.

    These inject the OSError directly, so they hold whether or not the account can be denied by the
    filesystem (a chmod fixture is a no-op for root). They exercise the real tree read-only.
    """
    source = (TOOLS / "check_csp_hashes.py").read_text(encoding="utf-8")
    ns = {"__name__": "csp_gate_under_test", "__file__": str(TOOLS / "check_csp_hashes.py")}
    exec(compile(source, ns["__file__"], "exec"), ns)
    failures = []
    cases = (("read_bytes", ROOT / "site" / "favicon.svg", "cannot read SVG as UTF-8"),
             ("iterdir", ROOT / "site", "cannot enumerate site directory"),
             ("lstat", ROOT / "site" / "favicon.svg", "cannot inspect site entry"))
    for method, target, expected in cases:
        original = getattr(Path, method)

        def fail_target(self, *args, _orig=original, _target=target, **kwargs):
            if self == _target:
                raise PermissionError("injected permission denial")
            return _orig(self, *args, **kwargs)

        output = io.StringIO()
        with patch.object(Path, method, fail_target), contextlib.redirect_stdout(output):
            rc = ns["main"]()
        text = output.getvalue()
        display = str(target.relative_to(ROOT))
        if rc != 1 or expected not in text or display not in text or "  FAIL  " not in text:
            failures.append(f"row 3.18: an injected {method} failure did not fail closed: "
                            f"rc={rc}, {text!r}")
    return failures, len(cases)


def main() -> int:
    failures, io_case_count = io_failure_cases()
    for desc, page, headers, must_fail, expected in CASES:
        rc, out = run_against(page, headers, **EXTRA_ARGS.get(desc, {}))
        if rc != (1 if must_fail else 0):
            want = "fail" if must_fail else "pass"
            failures.append(f"{desc}: expected the gate to {want}, it did not ({out!r})")
        elif expected is not None and expected not in out:
            failures.append(
                f"{desc}: the gate's exit status was right but its message was not. "
                f"Expected it to contain {expected!r}. It said: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
        if not must_fail and (FAIL_LINE.search(out) or not OK_LINE.search(out)):
            failures.append(f"{desc}: a pass must print an ok line and no FAIL line: {out!r}")
        if must_fail and not FAIL_LINE.search(out):
            failures.append(f"{desc}: a refusal must print a FAIL line: {out!r}")

    # A finding has to name the line a reader can go to, on each page it can fire on.
    rc, out = run_against(edited(PAGE, "<body>", '<body style="color:red">'))
    want = PAGE[:PAGE.index("<body>")].count("\n") + 1
    if f"site/index.html:{want}" not in out:
        failures.append(f"the style= finding does not name the right line on the home page: <body> "
                        f"is on line {want}. It said: {out!r}")
    rc, out = run_against({"404.html": edited(PAGE_404, "<body>", '<body onload="x">')})
    want = PAGE_404[:PAGE_404.index("<body>")].count("\n") + 1
    if f"site/404.html:{want}" not in out:
        failures.append(f"the on* finding does not name the right line on the 404 page: <body> is "
                        f"on line {want}. It said: {out!r}")

    # Row 3.18: every pass case above would also pass a gate that never looked at an SVG, so prove
    # the inspection ran: the happy path counts the real favicon, and a second SVG raises the count.
    rc, out = run_against()
    if rc != 0 or "1 SVG document(s)" not in out:
        failures.append(f"row 3.18: the happy path did not report inspecting the one real SVG: {out!r}")
    rc, out = run_against(extra_files={"img/logo.svg": FAVICON})
    if rc != 0 or "2 SVG document(s)" not in out:
        failures.append(f"row 3.18: a second SVG under site/img/ was not counted: {out!r}")
    rc, out = run_against(extra_files={"img/.svg": FAVICON})
    if rc != 0 or "2 SVG document(s)" not in out:
        failures.append(f"row 3.18: a dotfile named .svg was not counted as an SVG: {out!r}")
    # And prove the page count follows the pages: a fifth page raises it.
    rc, out = run_against(extra_files={"extra/index.html": STRAY_PAGE})
    if rc != 0 or "5 page(s) under site" not in out:
        failures.append(f"a fifth page was not counted as a page: {out!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    model_cases = len(CASES) - len(SCOPE_CASES)
    print(f"  ok    {model_cases} template page-model and shared-policy cases, "
          f"{len(SCOPE_CASES)} row 3.18 and P5 document, page and filesystem cases, "
          f"and {io_case_count} injected I/O failures; the docstring records the hash-model, A15 "
          f"and /draft/* case groups that retired at promotion and why")
    return 0


if __name__ == "__main__":
    sys.exit(main())
