#!/usr/bin/env python3
"""Cases for check_csp_hashes.py, one per defect a reviewer demonstrated against it.

Six rounds are recorded, and the arc matters more than any single case. Round 1 broke a
regular-expression reader and the gate moved to `html.parser`. Rounds 2, 3 and 4 then spent
themselves teaching that parser about HTML: `src` on a style, foreign content, integration points,
MathML, inert script types. Round 3 found that a round-2 fix was BACKWARDS and that the case written
for it was holding the wrong answer in place. Round 4 found two more silent fail-opens in the same
family, a `<style>` inside `<svg><title>` that `html.parser` swallows entirely and a `<script>` whose
escape states it misreads. Round 5 found three wrong pages that satisfied every one of the new guards,
the worst of which had this gate printing the hash of the EMPTY STRING in its own failure message and
going green once an author pinned what it asked for.

Round 6 generalized the gate from one hard-coded page to a KNOWN LIST of pages, because
`site/404.html` shipped a `<style>` pinned in the shared `/*` CSP that the gate never read, so editing
it would leave the gate green while a browser refused the style. The cases below now run against BOTH
real pages; the ones that reconstruct the CSP carry every page's pin, and the header-topology cases
that once spoke of "reaching the root" now assert the one-policy-under-/* contract that a page served
at any request path forces. New cases exercise the second page directly: an edited-but-unrepinned 404
style FAILS, a block added to the script-free page FAILS, an unlisted page FAILS, and the happy path
now proves three blocks across two pages.

So the gate stopped modelling HTML and started refusing what it cannot model, and most of the cases
below are now assertions that it refuses. Several of them USED to be passes, and each says so, because
a case that quietly changes direction is how round 2's regression survived.

Two kinds of case appear here. Most modify the page and assert the gate FAILS. The rest modify the
page, repin the CSP to the hash a browser would actually compute, and assert it PASSES; those hold a
closed defect closed, because reintroducing the old behaviour moves the computed hash and the case
goes red. `body_hash` computes that pin independently of the gate.

Row 3.18 (the maintainer's 2026-09-25 ruling) extended the gate past HTML pages to the rest of
`site/`: an `.xhtml`, `.xht` or `.svgz` is refused, a symbolic link or non-regular entry is refused,
and every `.svg` is inspected and fails on a `<script>` element or an `on*` attribute, failing closed
on anything it cannot read, decode or parse. The same day's P5 ruling ("all three") added, each as
its own refusal with its own cases: a `javascript:` URL in any SVG attribute, an href or an
animation's `to`, `from`, `by` or `values` alike; an SVG `<style>` element or `style=` attribute; and
an `on*` attribute on an HTML page, structural and literal, mirroring the `style=` accounting. These
cases are counted separately from the six review rounds, because they record a scope extension
rather than a defect a reviewer demonstrated. The harness now writes the real `site/favicon.svg`
into every run, so every case, old and new, also proves the real favicon passes; `extra_files` may
name subdirectories and carry bytes; `setup` makes the entries that are not plain files (links, a
FIFO, a missing or regular site root). Injected I/O errors exercise the traversal's failure handling
independently of the account's permissions, since a `chmod` fixture is a no-op for root. Passing
boundary cases document what the rulings do not ask this gate to police (references, `data:` URLs,
presentation attributes, text that merely looks like a URL or a handler).

Round 2 of the #352 review added three sets, counted with the row 3.18 cases: valueless,
slash-terminated and hyphenated page handlers at each SVG integration point on both pages, which the
old `on<word>=` accounting let through inside `<title>`, with prose and `data-onload` guards; a
case per character an XML attribute can carry to URL_NOISE (tab, LF, CR, DEL, space), so dropping
any one of them turns the suite red, which dropping CR once did not; and dotfile (`.svg`),
trailing-dot and compressed (`.gz`, `.br`, `.zst`) names, which pathlib's suffix let escape.

Round 3 of #352 found fake markup inside inert text (`<!-- <b title=" -->`, CDATA, a bogus
`<!thing>` or `<?thing>`, and text crossing a `textarea`, `title`, `noscript` or `xmp` boundary)
making the literal scan swallow a real handler inside SVG `<title>`, which html.parser missed too.
Its cases, on both pages, are counted with the row 3.18 cases: every reproduction with a valued and
a valueless handler, each refusal rule alone (the context-free valued-handler scan, inert text
holding a `<`, and `<math>` or an SVG `title`, `desc`, `foreignObject`, `style` or `script`), and
false-positive guards (plain text in a comment, `<title>`, `<noscript>` and `<textarea>`, on-words in
prose, `data-onload`). Three earlier cases changed: the round-2 integration-point cases now expect
the SVG refusal; the prose guard, which sat inside `<svg><title>` and carried `on = off`, moved to the
page's own `<title>` and a `<p>` without the `=`; and `data-onload` inside `<svg><title>`, once a
pass, is now refused as an SVG `<title>`, with a new pass case for `data-onload` in the body.

Round 4 of #352 found that a malformed end tag (`</ x </svg>`, `</1`, `</` and a tab, `</!`) is a
bogus comment to a browser and not to html.parser, so it hid an `</svg>` from a browser and let a
pinned stylesheet or script, wrapped in `<svg>`, carry a live `<a onclick>`. Its cases, counted with
the row 3.18 cases, repin every reproduction so that only the new rule can refuse it: the sixteen
stylesheet combinations (two pages, two handler forms, four prefixes), the script-wrapping variant
in both forms, `</` in the pinned script itself, and each malformed spelling in page text.

Round 5 of #352 found `<frameset>` and `<select>` wrapping the pinned stylesheet so that a browser
built a `<frame onload>` or `<a onclick>` from what html.parser hashed as the block, and the model
changed: every tag name on a page must be in an allowlist of the elements the real pages use. Its
cases, counted with the row 3.18 cases, are both reproductions in both handler forms on both pages
(repinned so only the allowlist can refuse them), a refusal per disallowed element, mixed case, a
lone end tag, a name inside a comment and one inside the pinned script, and a pass for allowed
elements in any case, and, so that rule 2 stays tested behind the allowlist, each inert context
holding only an allowlisted `<p>`. Two earlier cases changed: the `<noscript>`/`<textarea>` plain-text guard, once
a pass, is now refused by the allowlist, and the handler-bearing tag in the pinned script string is
an `<a>` rather than a `<b>`, so that it still passes.
"""
import base64
import contextlib
import gzip
import hashlib
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
HEADERS = (ROOT / "site" / "_headers").read_text(encoding="utf-8")
FAVICON = (ROOT / "site" / "favicon.svg").read_bytes()


def run_against(page=None, headers=None, extra_files=None, gate=None, setup=None):
    """Run the real gate against a copy of the site. Returns (exit, stdout and stderr).

    `page` is None (both real pages), a str (an index.html override, so every pre-round-6 case is
    byte-identical), or a dict {"index.html"/"404.html": text} overriding those pages; an unknown key
    RAISES, so a typo cannot silently test a pristine corpus. The real `site/favicon.svg` is written
    into every run. `extra_files` writes extra files under site/, in subdirectories as named, as
    text (written as UTF-8) or bytes (written as given). `gate` is an (old, new) pair applied to the
    gate SOURCE (for the config-guard case); it RAISES if `old` no longer matches, so a refactor
    cannot turn a mutation case into a run of the pristine gate. `setup` is called with the copy's
    root, for entries that are not plain files (a link, a FIFO, a replaced site/). A gate that hangs
    (on a FIFO it should never open) is reported as exit 124 rather than hanging the suite.
    """
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        (d / "site").mkdir()
        src = (TOOLS / "check_csp_hashes.py").read_text(encoding="utf-8")
        if gate is not None:
            if gate[0] not in src:
                raise AssertionError(f"gate mutation {gate[0]!r} no longer matches the source")
            src = src.replace(gate[0], gate[1])
        (d / "tools" / "check_csp_hashes.py").write_text(src, encoding="utf-8")
        pages = {"index.html": PAGE, "404.html": PAGE_404}
        if isinstance(page, str):
            pages["index.html"] = page
        elif isinstance(page, dict):
            for k, v in page.items():
                if k not in pages:
                    raise KeyError(f"run_against got an unknown page override {k!r}")
                pages[k] = v
        # Bytes, not text: the newline cases are only cases if the bytes survive the write.
        for name, text in pages.items():
            (d / "site" / name).write_bytes(text.encode("utf-8"))
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


def body_hash(page, tag):
    """sha256 of an element's text, computed here rather than asked of the gate."""
    m = re.search(rf"<{tag}>(.*?)</{tag}>", page, re.S)
    return base64.b64encode(hashlib.sha256(m.group(1).encode("utf-8")).digest()).decode()


def repinned(page, tag, base_page=None, headers=None):
    """HEADERS with that element's pin replaced by what the page now hashes to.

    `base_page` is the page whose OLD hash is being replaced (PAGE for index, PAGE_404 for the 404
    page), so a 404 repin replaces exactly the 404 token and leaves the index tokens intact.
    """
    base = HEADERS if headers is None else headers
    old = PAGE if base_page is None else base_page
    return base.replace(f"'sha256-{body_hash(old, tag)}'", f"'sha256-{body_hash(page, tag)}'")


def alt_pin(page, tag, fn):
    """The same element text under another CSP-permitted hash algorithm."""
    m = re.search(rf"<{tag}>(.*?)</{tag}>", page, re.S)
    return base64.b64encode(fn(m.group(1).encode("utf-8")).digest()).decode()


STYLE_PIN = f"'sha256-{body_hash(PAGE, 'style')}'"
SCRIPT_PIN = f"'sha256-{body_hash(PAGE, 'script')}'"
STYLE_404_PIN = f"'sha256-{body_hash(PAGE_404, 'style')}'"

COMMENTY = "/* <!-- keep this --> */\n    :root"
STRINGY = "(function () {\n  var tpl = \"<style>h1{color:red}</style>\";"
COMMENT_PAGE = PAGE.replace(":root", COMMENTY, 1)
STRING_PAGE = PAGE.replace("(function () {", STRINGY, 1)
SCRIPT_PAGE = PAGE.replace("(function () {", "(function () {\n  /* an edit */", 1)
CRLF_PAGE = PAGE.replace("\n", "\r\n")
CR_PAGE = PAGE.replace("\n", "\r")
CRLF_PINS = HEADERS.replace(STYLE_PIN, f"'sha256-{body_hash(CRLF_PAGE, 'style')}'").replace(
    SCRIPT_PIN, f"'sha256-{body_hash(CRLF_PAGE, 'script')}'")

# Round-6 second-page mutations (site/404.html has one <style>, no <script>).
E404 = PAGE_404.replace("<style>", "<style>\n    /* an edit */", 1)
E404_COMMENT = PAGE_404.replace("<style>", "<style>\n    /* <!-- keep --> */", 1)
TWO_STYLE_404 = PAGE_404.replace("</style>", "</style>\n<style>h1{color:red}</style>", 1)
SCRIPT_ON_404 = PAGE_404.replace("</style>", "</style>\n<script>var x=1;</script>", 1)
NOSCRIPT_INDEX = re.sub(r"<script>.*?</script>", "", PAGE, count=1, flags=re.S)
IDX_STYLE_BODY = re.search(r"<style>(.*?)</style>", PAGE, re.S).group(1)
P404_SHARED = re.sub(r"<style>.*?</style>", lambda m: "<style>" + IDX_STYLE_BODY + "</style>",
                     PAGE_404, count=1, flags=re.S)
SVG_TITLE_STYLE_404 = PAGE_404.replace(
    "</style>", "</style>\n<svg><title><STYLE>p{color:red}</STYLE></title></svg>", 1)
SVG_TITLE_SCRIPT_404 = PAGE_404.replace(
    "</style>", "</style>\n<svg><title><script>x</script></title></svg>", 1)
ORPHAN = "'sha256-" + "A" * 43 + "='"

# (description, page, headers, must_fail, expected substring or None)
CASES = (
    ("the site as it stands, now three blocks across two pages", None, None, False, None),
    ("an edited stylesheet nobody repinned",
     PAGE.replace(":root", "/* an edit */\n    :root", 1), None, True, "lacks the hash"),
    ("an edited inline script nobody repinned", SCRIPT_PAGE, None, True, "lacks the hash"),
    ("a style= attribute, which no hash can ever cover",
     PAGE.replace("<body", '<body style="color:red"', 1), None, True, "style= attribute"),
    ("'unsafe-inline' coming back",
     None, re.sub(r"style-src '[^']*'", "style-src 'unsafe-inline'", HEADERS, count=1), True,
     "'unsafe-inline'"),

    # THE PAGE OUTGROWING THE GATE. Each of these used to be modelled, mostly wrongly.
    ("a second inline block, which this gate no longer tries to tell apart",
     PAGE.replace("</style>", "</style>\n<style>h1{color:red}</style>", 1), None, True,
     "models exactly one"),
    ("a <style src=>, once skipped as external and once hashed",
     PAGE.replace("</style>", "</style>\n<style src=\"theme.css\">h1{color:red}</style>", 1),
     None, True, "models exactly one"),
    ("an attribute on the hashed block, where a browser's rules decide whether it runs",
     PAGE.replace("<style>", '<style title="a > b">', 1), None, True, "carries attributes"),
    ("a <script> with a type, which used to be judged live or inert here",
     PAGE.replace("<script>", '<script type="module">', 1), None, True, "carries attributes"),
    ("a <style> inside <svg><title>, which html.parser never reports",
     PAGE.replace("</svg>", "<title><style>p{color:red}</style></title>\n    </svg>", 1), None,
     True, "openers"),
    ("a <style> inside the inline <svg>",
     PAGE.replace("</svg>", "<style>circle{fill:red}</style>\n    </svg>", 1), None, True,
     "models exactly one"),
    ("a <style> inside <math>",
     PAGE.replace("</style>", "</style>\n<math><style>m{color:red}</style></math>", 1), None,
     True, "models exactly one"),
    ("a <script> containing <!--, which opens HTML's script-data escape states",
     PAGE.replace("(function () {", "// <!--<script>x</script>-->\n(function () {", 1), None,
     True, "escape states"),
    ("a NUL byte, which a browser replaces with U+FFFD before hashing",
     PAGE.replace(":root", "\x00:root", 1), None, True, "NUL byte"),

    # DIRECTIVE RESOLUTION, per CSP3's fallback chain.
    ("script-src-elem 'none' added beside a correct script-src",
     None, HEADERS.replace("; img-src", "; script-src-elem 'none'; img-src", 1), True,
     "script-src-elem lacks the hash"),
    # style-src-elem, once present, governs BOTH pages' styles, so it must carry both pins.
    ("style-src-elem preferred over a hostile style-src, carrying both style pins",
     None, HEADERS.replace(f"style-src {STYLE_PIN} {STYLE_404_PIN}", "style-src 'none'", 1)
     .replace("; img-src", f"; style-src-elem {STYLE_PIN} {STYLE_404_PIN}; img-src", 1),
     False, None),
    ("style-src-elem 'none' added beside a correct style-src",
     None, HEADERS.replace("; img-src", "; style-src-elem 'none'; img-src", 1), True,
     "style-src-elem lacks the hash"),
    ("default-src carrying every hash, with no script-src or style-src",
     None, HEADERS.replace(
         f"default-src 'none'; script-src {SCRIPT_PIN}; style-src {STYLE_PIN}",
         f"default-src {SCRIPT_PIN} {STYLE_PIN}", 1), False, None),
    ("a directive repeated, the first one hostile, which is the one a browser takes",
     None, HEADERS.replace("style-src ", "style-src 'none'; style-src ", 1), True,
     "style-src lacks the hash"),
    ("a directive name in mixed case, which CSP3 matches case-insensitively",
     None, HEADERS.replace("style-src ", "Style-Src ", 1), False, None),
    ("the style hash pinned under script-src instead of style-src",
     None, HEADERS.replace(f"style-src {STYLE_PIN}", "style-src 'none'", 1)
     .replace("script-src 'sha256-", f"script-src {STYLE_PIN} 'sha256-", 1),
     True, "style-src lacks the hash"),

    # THE HEADERS FILE, whose syntax is Cloudflare's. Round 6 requires exactly one CSP, under /*.
    ("a later rule detaching the Content-Security-Policy entirely",
     None, HEADERS + "\n/*\n  ! Content-Security-Policy\n", True, "detaches"),
    ("a second CSP in a host-scoped rule, which this gate forbids",
     None, HEADERS + "\nhttps://secureconfig.example/*\n  Content-Security-Policy: style-src 'none'\n",
     True, "exactly one Content-Security-Policy"),
    ("a comment between a rule and its headers, which is valid in _headers",
     None, HEADERS.replace("/*\n", "/*\n# the policy below is pinned by tools/check_csp_hashes.py\n", 1),
     False, None),
    ("a hostile CSP in a separate / block beside the /* block",
     None, "/\n  Content-Security-Policy: default-src 'none'\n\n" + HEADERS, True,
     "exactly one Content-Security-Policy"),
    ("two /* blocks, the hostile policy in the first",
     None, "/*\n  Content-Security-Policy: default-src 'none'\n\n" + HEADERS, True,
     "exactly one Content-Security-Policy"),
    ("the only CSP under a non-root rule, which cannot govern every page",
     None, HEADERS.replace("/*", "/assets/*", 1), True, "not the /* rule"),
    ("a root rule with no Content-Security-Policy line",
     None, re.sub(r"^  Content-Security-Policy:.*$", "  X-Other: 1", HEADERS, count=1,
                  flags=re.M), True, "Content-Security-Policy header"),

    # NEWLINES. Round 2 recorded this backwards and the case killed the mutant that fixed it.
    ("a CRLF page against the real pins, which a browser renders correctly",
     CRLF_PAGE, None, False, None),
    ("a CRLF page pinned to the hash of its CRLF bytes, which no browser computes",
     CRLF_PAGE, CRLF_PINS, True, "lacks the hash"),
    ("a lone-CR page against the real pins, normalized the same way",
     CR_PAGE, None, False, None),

    # ROUND 5. Three wrong pages that passed every guard, each verified against html5lib and Gumbo.
    ("a self-closing <style/>, which html.parser reads as empty and a browser does not",
     PAGE.replace("<style>", "<style/>", 1), None, True, "self-closing"),
    ("a charset declaration this gate does not obey",
     PAGE.replace('<meta charset="utf-8">', '<meta charset="windows-1252">', 1), None, True,
     "charset"),
    ("a style= attribute smuggled through <svg><title>",
     PAGE.replace("</svg>", '<title>t<div style="display:none">x</div></title>\n    </svg>', 1),
     None, True, "style="),
    ("a comma splitting the CSP into two policies, the first hostile",
     None, HEADERS.replace("style-src ", "style-src 'none', style-src ", 1), True, "comma"),
    ("an uppercase <STYLE> smuggled through <svg><title>",
     PAGE.replace("</svg>", "<title>t<STYLE>p{color:red}</STYLE></title>\n    </svg>", 1),
     None, True, "openers"),
    ("a CSP with no style-src, style-src-elem or default-src at all",
     None, re.sub(r"Content-Security-Policy: .*$", "Content-Security-Policy: img-src 'self'",
                  HEADERS, count=1, flags=re.M), True, "no script-src directive"),
    ("the correct hash embedded in a longer, invalid token",
     None, HEADERS.replace(STYLE_PIN, STYLE_PIN[:-1] + "x'", 1), True, "lacks the hash"),
    ("'unsafe-inline' on script-src beside the correct pin",
     None, HEADERS.replace("script-src ", "script-src 'unsafe-inline' ", 1), True,
     "'unsafe-inline'"),
    ("a pin whose algorithm name is upper case, which CSP3 accepts",
     None, HEADERS.replace(STYLE_PIN, STYLE_PIN.replace("sha256", "SHA256"), 1), False, None),
    ("a sha384 pin, which is stronger and equally valid",
     None, HEADERS.replace(STYLE_PIN, f"'sha384-{alt_pin(PAGE, 'style', hashlib.sha384)}'", 1),
     False, None),

    # REPINNED, ASSERTING A PASS. These hold a closed round-1 defect closed.
    ("stylesheet text containing <!-- and -->, which is text and not a comment node",
     COMMENT_PAGE, repinned(COMMENT_PAGE, "style"), False, None),
    ("a <style> written inside a JavaScript string, which is a string and not an element",
     STRING_PAGE, repinned(STRING_PAGE, "script"), False, None),

    # ROUND 6. The second page, site/404.html, exercised directly.
    ("an edited 404 stylesheet nobody repinned",
     {"404.html": E404}, None, True, "site/404.html"),
    ("the edited 404 stylesheet, repinned to what a browser computes",
     {"404.html": E404}, repinned(E404, "style", base_page=PAGE_404), False, None),
    ("the 404 style pin deleted from style-src, the page untouched",
     None, HEADERS.replace(" " + STYLE_404_PIN, "", 1), True, "lacks the hash"),
    ("the index style pin deleted, the 404 pin kept, which must fail on index",
     None, HEADERS.replace(STYLE_PIN + " ", "", 1), True, "site/index.html"),
    ("a second <style> on the 404 page",
     {"404.html": TWO_STYLE_404}, None, True, "models exactly one"),
    ("a <script> added to the script-free 404 page",
     {"404.html": SCRIPT_ON_404}, None, True, "models exactly 0"),
    ("index's <script> deleted, its pin left behind",
     NOSCRIPT_INDEX, None, True, "has 0 <script>"),
    ("index's script moved onto the 404 page, both pins untouched",
     {"index.html": NOSCRIPT_INDEX, "404.html": SCRIPT_ON_404}, None, True, "models exactly 0"),
    ("a self-closing <style/> on the 404 page",
     {"404.html": PAGE_404.replace("<style>", "<style/>", 1)}, None, True, "self-closing"),
    ("a charset the 404 page does not obey",
     {"404.html": PAGE_404.replace('<meta charset="utf-8">', '<meta charset="windows-1252">', 1)},
     None, True, "charset"),
    ("the 404 charset declaration removed",
     {"404.html": PAGE_404.replace('<meta charset="utf-8">', "", 1)}, None, True, "charset"),
    ("a NUL byte on the 404 page",
     {"404.html": PAGE_404.replace("<style>", "<style>\x00", 1)}, None, True, "NUL byte"),
    ("a style= attribute on the 404 page's body",
     {"404.html": PAGE_404.replace("<body", '<body style="color:red"', 1)}, None, True,
     "style= attribute"),
    ("a <STYLE> smuggled through <svg><title> on the 404 page",
     {"404.html": SVG_TITLE_STYLE_404}, None, True, "openers"),
    ("a <script> smuggled through <svg><title> on the script-free 404 page",
     {"404.html": SVG_TITLE_SCRIPT_404}, None, True, "openers"),
    ("the 404 style made byte-identical to index's, pinned by the one shared token",
     {"404.html": P404_SHARED}, HEADERS.replace(" " + STYLE_404_PIN, "", 1), False, None),
    ("a bogus unused hash appended to style-src, an orphan pin the gate now rejects",
     None, HEADERS.replace(STYLE_404_PIN, STYLE_404_PIN + " " + ORPHAN, 1), True, "orphan"),
    ("a used pin also spelled in the base64url alphabet is the same pin, not an orphan",
     None, HEADERS.replace(STYLE_404_PIN, STYLE_404_PIN + " " + STYLE_404_PIN.replace("+", "-").replace("/", "_"), 1), False, None),
    ("the CSP moved under a / rule only",
     None, HEADERS.replace("/*", "/", 1), True, "not the /* rule"),
    ("a second CSP under a /guides/* rule, which governs the 404 page on those paths",
     None, HEADERS + "\n/guides/*\n  Content-Security-Policy: style-src 'none'\n", True,
     "exactly one Content-Security-Policy"),
    ("a CSP detached under a /guides/* rule",
     None, HEADERS + "\n/guides/*\n  ! Content-Security-Policy\n", True, "detaches"),
    ("an unlisted extra page served under the same /* CSP",
     None, None, True, "not in this gate's page list"),
    ("a declared block count outside {0, 1}",
     None, None, True, "0 or 1"),
    ("a CRLF 404 page against the real pin, normalized the same way",
     {"404.html": PAGE_404.replace("\n", "\r\n")}, None, False, None),
    ("the 404 style repinned under sha384",
     None, HEADERS.replace(STYLE_404_PIN, f"'sha384-{alt_pin(PAGE_404, 'style', hashlib.sha384)}'", 1),
     False, None),
    ("<!-- inside the 404 stylesheet text, which is text and not a script",
     {"404.html": E404_COMMENT}, repinned(E404_COMMENT, "style", base_page=PAGE_404), False, None),

    # ROUND 6 fixes, each locked by an independent verifier's finding.
    ("the sole CSP under a host-scoped absolute-URL rule, which covers only that host",
     None, HEADERS.replace("/*", "https://secureconfig.example/*", 1), True, "not the /* rule"),
    ("a CSP detached with a trailing colon and value under a path-scoped rule",
     None, HEADERS + "\n/guides/*\n  ! Content-Security-Policy: default-src 'none'\n", True,
     "detaches"),
    ("a Content-Security-Policy header line with no colon, which must fail without crashing",
     None, re.sub(r"^  Content-Security-Policy:.*$", "  Content-Security-Policy", HEADERS, count=1,
                  flags=re.M), True, "Content-Security-Policy header"),
    ("an unlisted page with an upper-case .HTML extension",
     None, None, True, "not in this gate's page list"),
    ("an unlisted page with a .htm extension",
     None, None, True, "not in this gate's page list"),
)

# Cases carried by run_against arguments rather than page/headers overrides.
EXTRA_ARGS = {
    "an unlisted extra page served under the same /* CSP":
        {"extra_files": {"extra.html": "<!doctype html>\n<meta charset=\"utf-8\">\n"
                         "<style>a{color:red}</style>\n"}},
    "a declared block count outside {0, 1}":
        {"gate": ('"style": 1', '"style": 2')},
    "an unlisted page with an upper-case .HTML extension":
        {"extra_files": {"help.HTML": '<!doctype html>\n<meta charset="utf-8">\n'
                         '<style>a{color:red}</style>\n'}},
    "an unlisted page with a .htm extension":
        {"extra_files": {"help.htm": '<!doctype html>\n<meta charset="utf-8">\n'
                         '<style>a{color:red}</style>\n'}},
}

# Row 3.18 and P5 cases, appended to CASES below and carried by run_against arguments. Each is a
# document, a filesystem entry, a page or a parser input the gate must refuse or must pass.
LEGACY_CASE_COUNT = len(CASES)
SCOPE_CASES = []
# The gate's result lines, matched at a line start because run_against strips the first line's indent.
FAIL_LINE = re.compile(r"^\s*FAIL  ", re.M)
OK_LINE = re.compile(r"^\s*ok    ", re.M)


def scope_case(desc, content=None, expected=None, name="assets/probe.svg", setup=None, page=None,
               headers=None):
    """Record one row 3.18 or P5 case: a must-fail if `expected` names the finding, a must-pass if None.

    `content` is written under site/ at `name`; `page` and `headers` are run_against's overrides,
    for the P5 page cases; `setup` makes an entry that is not a plain file.
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

# Unlisted HTML, nested, still refused by the new walk with the old message.
for suffix in (".html", ".HTML", ".HtM"):
    scope_case("nested unlisted HTML " + suffix, "<!doctype html>", "not in this gate's page list",
               name="deep/probe" + suffix)

# Round 2 of #352 (claude finding 2): pathlib gives a dotfile no suffix, so a file named exactly
# `.svg` escaped every rule. The suffix is now the text from the last dot of the whole name.
scope_case("dotfile .svg carrying a script", svg("<script/>"), "script element", name="deep/.svg")
scope_case("dotfile .SVG carrying a handler", svg(attrs='onload="x"'), "on* handler", name=".SVG")
scope_case("clean dotfile .svg is inspected and passes", svg("<path/>"), name="deep/.svg")
for dotfile, expected, content in ((".xhtml", "is XHTML", XHTML_DOC), (".xht", "is XHTML", XHTML_DOC),
                                   (".svgz", "compressed SVG", gzip.compress(FAVICON, mtime=0)),
                                   (".html", "not in this gate's page list", "<!doctype html>"),
                                   (".htm", "not in this gate's page list", "<!doctype html>")):
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

# P5 (3): an on* handler attribute on an HTML page, structural and literal, on both pages.
ONJS_PAGE = PAGE.replace("(function () {", "(function () {\n  document.body.onload = null;", 1)
ONCSS_PAGE = PAGE.replace(":root", "/* onclick= here is stylesheet text */\n    :root", 1)
scope_case("P5 page handler on index's body", expected="on* handler",
           page=PAGE.replace("<body", '<body onload="init()"', 1))
scope_case("P5 upper-case page handler on the 404 page names the page", expected="site/404.html",
           page={"404.html": PAGE_404.replace("<body", "<body ONCLICK=go", 1)})
scope_case("P5 valueless page handler", expected="on* handler",
           page=PAGE.replace("<body", "<body onclick", 1))
scope_case("P5 page handler with a spaced =", expected="on* handler",
           page=PAGE.replace("<body", "<body onload = 'x'", 1))
scope_case("P5 page handler on the inline <svg>", expected="on* handler",
           page=PAGE.replace("<svg ", '<svg onload="x" ', 1))
scope_case("P5 page handler on the 404 page's inline <svg>", expected="on* handler",
           page={"404.html": PAGE_404.replace("<svg ", '<svg onclick="x" ', 1)})
scope_case("P5 page handler smuggled through <svg><title>", expected="on* handler",
           page=PAGE.replace("</svg>", '<title>t<div onclick="x">x</div></title>\n    </svg>', 1))
scope_case("P5 handler text inside the index script is text, repinned",
           page=ONJS_PAGE, headers=repinned(ONJS_PAGE, "script"))
scope_case("P5 handler text inside the index stylesheet is text, repinned",
           page=ONCSS_PAGE, headers=repinned(ONCSS_PAGE, "style"))
scope_case("P5 data-onload= on a page is not a handler",
           page=PAGE.replace("<body", '<body data-onload="x"', 1))

# Round 2 of #352 (codex finding 1): the literal accounting once required `on<word>=`, so a
# valueless, slash-terminated or hyphenated handler name hidden at an SVG integration point passed.
# Each form, at each integration point, on both pages.
HIDDEN_HANDLERS = (("valueless onclick", "<div onclick>x</div>"),
                   ("valueless onload after another attribute", "<div hidden onload>x</div>"),
                   ("slash-terminated onclick", "<div onclick/>x"),
                   ("hyphenated on-click", '<div on-click="x">x</div>'))
INTEGRATION_POINTS = (("title", "<title>t{}</title>"), ("desc", "<desc>d{}</desc>"),
                      ("foreignObject", "<foreignObject>{}</foreignObject>"))
# Round 3 of #352 refuses every one of those integration points inside <svg> outright, so each case
# now expects that refusal rather than the literal-accounting message; each is still refused.
SVG_REFUSAL = "inside an inline <svg>"
for page_name, base in (("index.html", PAGE), ("404.html", PAGE_404)):
    for point, wrapper in INTEGRATION_POINTS:
        for form, fragment in HIDDEN_HANDLERS:
            scope_case(f"P5 {form} inside <svg><{point}> on {page_name}", expected=SVG_REFUSAL,
                       page={page_name: base.replace(
                           "</svg>", wrapper.format(fragment) + "\n    </svg>", 1)})
    # Round 3 of #352 changed these two: the prose once sat inside <svg><title>, now refused, and
    # carried `on = off` and `one = two`, which the context-free scan now refuses as text it cannot
    # tell from a handler (a case below). The prose moves to the page's own <title> and a <p>.
    scope_case(f"P5 prose on-words on {page_name} are not handlers",
               page={page_name: re.sub(r"<title>[^<]*</title>",
                                       "<title>only one on duty, on-call; one, on</title>", base,
                                       count=1)
                   .replace("</body>", "<p>only one on duty, on-call; online, on</p>\n</body>", 1)})
    scope_case(f"P5 data-onload inside <svg><title> on {page_name} is refused as SVG <title>",
               expected=SVG_REFUSAL,
               page={page_name: base.replace(
                   "</svg>", '<title>t<div data-onload="x" data-on>x</div></title>\n    </svg>', 1)})
    scope_case(f"P5 data-onload on {page_name} is not a handler",
               page={page_name: base.replace(
                   "</body>", '<div data-onload="x" data-on>x</div>\n</body>', 1)})
# Round 5 of #352: `<b>` is not in the page allowlist, so the string now carries an `<a>`.
ONTAG_JS_PAGE = PAGE.replace("(function () {", '(function () {\n  var tpl = "<a onclick>x</a>";', 1)
scope_case("P5 a handler-bearing tag in a JavaScript string is script text, repinned",
           page=ONTAG_JS_PAGE, headers=repinned(ONTAG_JS_PAGE, "script"))
scope_case("P5 a handler-bearing tag in a page comment fails closed", expected="on* handler",
           page=PAGE.replace("</body>", "<!-- <b onclick> -->\n</body>", 1))

# Round 3 of #352 (codex finding): fake markup inside inert text made literal_on_attrs() read a tag
# that a browser never sees and swallow a real handler after it as a quoted value, while html.parser
# missed the handler inside SVG <title>, so both counts were 0. Three rules that ask html.parser
# nothing now refuse it: (1) a context-free scan for a valued `on...=` outside the pinned blocks,
# (2) inert text holding a `<`, and (3) the foreign-content elements html.parser reads as HTML.
ON_TEXT = "outside the hash-pinned blocks"
CROSSINGS = (("comment", '<!-- <b title=" -->', "has a comment whose text"),
             ("CDATA section", '<![CDATA[ <b title=" ]]>', "has a CDATA section whose text"),
             ("bogus declaration", '<!thing <b title=">', "has a <! declaration whose text"),
             ("bogus processing instruction", '<?thing <b title=">', "has a <? declaration whose text"),
             ("textarea crossing", '<textarea><b title="</textarea>', "has a <textarea> whose content"),
             ("title crossing", '<title><b title="</title>', "has a <title> whose content"),
             ("noscript crossing", '<noscript><b title="</noscript>', "has a <noscript> whose content"),
             ("xmp crossing", '<xmp><b title="</xmp>', "has a <xmp> whose content"))
HANDLER_FORMS = (("valued", "onclick=alert(1)"), ("valueless", "onclick"))
for page_name, base in (("index.html", PAGE), ("404.html", PAGE_404)):
    # The reproduction exactly as filed, before the first </svg>, then each crossing before </body>.
    for form, handler in HANDLER_FORMS:
        scope_case(f"#352 r3 codex reproduction, {form}, on {page_name}",
                   expected="has a comment whose text",
                   page={page_name: base.replace(
                       "</svg>", f'<!-- <b title=" -->\n<title><div {handler}>x</div></title>\n'
                                 f'<!-- " -->\n</svg>', 1)})
        for what, opener, expected in CROSSINGS:
            scope_case(f"#352 r3 {what} swallowing a {form} handler on {page_name}",
                       expected=expected,
                       page={page_name: base.replace(
                           "</body>", f"{opener}\n<svg><title><div {handler}>x</div></title></svg>\n"
                                      f'<!-- " -->\n</body>', 1)})
    # Rule 1 alone: text a browser does not wire up, but which this gate cannot tell from a handler.
    for what, fragment in (("in prose", "<p>x onclick=alert(1)</p>"),
                           ("as prose `one = two`", "<p>one = two</p>"),
                           ("in a comment without a <", "<!-- onclick=x -->"),
                           ("in an attribute value", '<p title="a ONLOAD = b">x</p>'),
                           ("hyphenated, in prose", '<p>on-click="x"</p>')):
        scope_case(f"#352 r3 rule 1: handler-like text {what} on {page_name}", expected=ON_TEXT,
                   page={page_name: base.replace("</body>", fragment + "\n</body>", 1)})
    # Rule 2 alone: inert text holding a `<`, no handler anywhere.
    for what, fragment, expected in (
            ("comment", "<!-- a <b> c -->", "has a comment whose text"),
            ("CDATA section", "<![CDATA[ a <b> c ]]>", "has a CDATA section whose text"),
            ("declaration", "<!thing a <b>", "has a <! declaration whose text"),
            ("processing instruction", "<?thing a <b>", "has a <? declaration whose text"),
            ("second doctype", "<!doctype <b>", "has a <! declaration whose text")) + tuple(
            (f"<{el}>", f"<{el.upper() if el == 'iframe' else el}>a <b>c</{el}>",
             f"has a <{el}> whose content") for el in (
                "textarea", "title", "xmp", "noscript", "plaintext", "noembed", "noframes",
                "iframe")):
        scope_case(f"#352 r3 rule 2: {what} holding a < on {page_name}", expected=expected,
                   page={page_name: base.replace("</body>", fragment + "\n</body>", 1)})
    # Rule 3 alone: plain-text divergent elements inside the real inline <svg>, and <math>.
    for element in ("title", "TITLE", "desc", "foreignObject", "FOREIGNOBJECT", "style", "Script"):
        scope_case(f"#352 r3 rule 3: <{element}> inside the inline <svg> on {page_name}",
                   expected=SVG_REFUSAL,
                   page={page_name: base.replace(
                       "</svg>", f"<{element}>plain</{element}>\n    </svg>", 1)})
    scope_case(f"#352 r3 rule 3: <desc> in a nested <svg> after an inner </svg> on {page_name}",
               expected=SVG_REFUSAL,
               page={page_name: base.replace(
                   "</svg>", "<svg><path/></svg><desc>plain</desc>\n    </svg>", 1)})
    for element in ("math", "MATH"):
        scope_case(f"#352 r3 rule 3: <{element}> on {page_name}", expected="has a <math> element",
                   page={page_name: base.replace(
                       "</body>", f"<{element}><mi>x</mi></{element}>\n</body>", 1)})
    # False-positive guards: plain inert text passes, and a <title> element outside <svg> passes.
    scope_case(f"#352 r3 a comment holding plain on-word text on {page_name} passes",
               page={page_name: base.replace(
                   "</body>", "<!-- only one on duty; see _headers -->\n</body>", 1)})
    scope_case(f"#352 r3 a <title> holding plain text on {page_name} passes",
               page={page_name: re.sub(r"<title>[^<]*</title>", "<title>Only one, on call</title>",
                                       base, count=1)})
    # Round 5 of #352: once a pass, now refused, since neither element is in the page allowlist.
    scope_case(f"#352 r3 a <noscript> and a <textarea> holding plain text on {page_name}, refused "
               f"by the allowlist", expected="element <noscript> is not in the page allowlist",
               page={page_name: base.replace(
                   "</body>", "<noscript>on duty</noscript><textarea>one, on</textarea>\n</body>", 1)})

# Round 4 of #352 (codex finding): a malformed end tag (`</` and no letter) is a bogus comment to a
# browser and not to html.parser, so `</ x </svg>` hid an </svg> from a browser and closed the SVG
# region here, and a stylesheet or script wrapped in that <svg> became SVG content holding a live
# <a onclick> while this gate hashed it as the pinned block. Every reproduction, repinned so only
# the new rule can refuse it, on both pages; then the rule alone, in page text.
MALFORMED = "has a malformed end tag"
BOGUS_PREFIXES = (("space and letter", "</ x </svg>"), ("digit", "</1 </svg>"),
                  ("tab", "</\t</svg>"), ("bang", "</! </svg>"))
for page_name, base in (("index.html", PAGE), ("404.html", PAGE_404)):
    for prefix_name, prefix in BOGUS_PREFIXES:
        for form, handler in HANDLER_FORMS:
            wrapped = base.replace("<style>", f"<svg>{prefix}<style>\n/* <a {handler}>x</a> */\n", 1
                                   ).replace("</style>", "</style></svg>", 1)
            scope_case(f"#352 r4 stylesheet wrapped after {prefix_name} bogus comment, {form}, on "
                       f"{page_name}", expected=MALFORMED, page={page_name: wrapped},
                       headers=repinned(wrapped, "style", base_page=base))
    for what, fragment in (("</>", "</>"), ("</ and a space", "</ p>"), ("</ and a digit", "</1>"),
                           ("</!", "</!x>"), ("</ and a tab", "</\tp>")):
        scope_case(f"#352 r4 rule 4: {what} in page text on {page_name}", expected=MALFORMED,
                   page={page_name: base.replace("</body>", f"<p>a{fragment}b</p>\n</body>", 1)})
for form, handler in HANDLER_FORMS:
    wrapped = PAGE.replace("<script>", f"<svg></ x </svg><script>\n// <a {handler}>x</a>\n", 1
                           ).replace("</script>", "</script></svg>", 1)
    scope_case(f"#352 r4 script wrapped after a bogus comment, {form}, on index.html",
               expected=MALFORMED, page=wrapped, headers=repinned(wrapped, "script"))
scope_case("#352 r4 rule 4: `</` inside the pinned index script, repinned", expected=MALFORMED,
           page=PAGE.replace("(function () {", "(function () {\n  var s = '</ x';", 1),
           headers=repinned(PAGE.replace("(function () {", "(function () {\n  var s = '</ x';", 1),
                            "script"))

# Round 5 of #352 (codex finding): a <frameset> around the pinned stylesheet made a browser drop the
# <style> and build a <frame onload> from what html.parser hashed as its body, and
# <select><style><input><a onclick> did the same through select parsing; every rule above passed.
# The gate now allows only the elements the real pages use. Each reproduction is repinned to the
# text html.parser hashes, so only the allowlist can refuse it.
ALLOWLIST = "is not in the page allowlist"
for page_name, base in (("index.html", PAGE), ("404.html", PAGE_404)):
    for form, attr in (("valued", 'onload="window.__qa352=1"'), ("valueless", "onload")):
        wrapped = base.replace("<style>", f"<frameset><style>\n<frame {attr}>\n", 1
                               ).replace("</style>", "</style></frameset>", 1)
        scope_case(f"#352 r5 frameset around the stylesheet, {form} <frame onload>, on {page_name}",
                   expected="element <frameset> " + ALLOWLIST, page={page_name: wrapped},
                   headers=repinned(wrapped, "style", base_page=base))
    for form, handler in HANDLER_FORMS:
        wrapped = base.replace("<style>", f"<select><style>\n<input><a {handler}>\n", 1
                               ).replace("</style>", "</style></select>", 1)
        scope_case(f"#352 r5 select around the stylesheet, {form} <a onclick>, on {page_name}",
                   expected="element <select> " + ALLOWLIST, page={page_name: wrapped},
                   headers=repinned(wrapped, "style", base_page=base))
    for element in ("frameset", "frame", "select", "template", "math", "iframe", "object", "embed",
                    "noscript", "textarea", "xmp", "plaintext", "noembed", "noframes",
                    "foreignObject", "desc", "input", "b", "table", "form", "image", "isindex"):
        scope_case(f"#352 r5 allowlist: <{element}> on {page_name}",
                   expected=f"element <{element.lower()}> " + ALLOWLIST,
                   page={page_name: base.replace("</body>", f"<{element}></{element}>\n</body>", 1)})
    scope_case(f"#352 r5 allowlist: mixed-case <FrameSet> on {page_name}",
               expected="element <frameset> " + ALLOWLIST,
               page={page_name: base.replace("</body>", "<FrameSet>\n</body>", 1)})
    scope_case(f"#352 r5 allowlist: an end tag alone, </select>, on {page_name}",
               expected="element <select> " + ALLOWLIST,
               page={page_name: base.replace("</body>", "</select>\n</body>", 1)})
    scope_case(f"#352 r5 allowlist: <frameset> inside a comment on {page_name}, read context-free",
               expected="element <frameset> " + ALLOWLIST,
               page={page_name: base.replace("</body>", "<!-- <frameset> -->\n</body>", 1)})
    scope_case(f"#352 r5 allowed elements in any case on {page_name} pass",
               page={page_name: base.replace(
                   "</body>", "<P>x <SPAN>y</SPAN> <Code>z</Code></P>\n</body>", 1)})
    # Rule 2 behind the allowlist: each inert context holding only an allowlisted name, so the
    # allowlist passes it and rule 2 alone refuses it.
    for what, fragment, expected in (
            ("comment", "<!-- a <p> c -->", "has a comment whose text"),
            ("CDATA section", "<![CDATA[ a <p> c ]]>", "has a CDATA section whose text"),
            ("declaration", "<!thing a <p>", "has a <! declaration whose text"),
            ("processing instruction", "<?thing a <p>", "has a <? declaration whose text"),
            ("<title>", "<title>a <p>c</title>", "has a <title> whose content")):
        scope_case(f"#352 r5 rule 2 alone: {what} holding an allowlisted <p> on {page_name}",
                   expected=expected,
                   page={page_name: base.replace("</body>", fragment + "\n</body>", 1)})
FRAMESET_JS_PAGE = PAGE.replace("(function () {", '(function () {\n  var tpl = "<frameset>";', 1)
scope_case("#352 r5 allowlist: <frameset> inside the pinned index script, repinned",
           expected="element <frameset> " + ALLOWLIST, page=FRAMESET_JS_PAGE,
           headers=repinned(FRAMESET_JS_PAGE, "script"))


def file_link(d):
    (d / "site" / "linked.svg").symlink_to("favicon.svg")


def listed_page_link(d):
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


for desc, setup in (("file symlink", file_link), ("listed HTML page symlink", listed_page_link),
                    ("external directory symlink", directory_link), ("site root symlink", root_link),
                    ("dangling symlink", lambda d: (d / "site" / "missing.svg").symlink_to("absent")),
                    ("symlink loop", lambda d: (d / "site" / "loop").symlink_to("loop"))):
    scope_case(desc, expected="is a symbolic link", setup=setup)
scope_case("FIFO named .svg, never opened", expected="not a regular file",
           setup=lambda d: os.mkfifo(d / "site" / "pipe.svg"))
scope_case("missing site root", expected="cannot inspect site entry", setup=missing_root)
scope_case("regular file as site root", expected="is not a directory", setup=regular_root)

CASES += tuple(SCOPE_CASES)


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
            failures.append(f"{desc}: a pass must print one ok line and no FAIL line: {out!r}")
        if must_fail and not FAIL_LINE.search(out):
            failures.append(f"{desc}: a refusal must print a FAIL line: {out!r}")

    # The repinned cases only mean something if their repin actually moved the hash.
    for page, tag, base, desc in ((COMMENT_PAGE, "style", PAGE, "the <!-- in stylesheet text"),
                                  (STRING_PAGE, "script", PAGE, "the <style> in a JavaScript string"),
                                  (CRLF_PAGE, "style", PAGE, "the CRLF"),
                                  (E404, "style", PAGE_404, "the 404 stylesheet edit"),
                                  (ONJS_PAGE, "script", PAGE, "the handler text in the index script"),
                                  (ONCSS_PAGE, "style", PAGE, "the handler text in the index stylesheet"),
                                  (ONTAG_JS_PAGE, "script", PAGE, "the handler tag in the index script")):
        if body_hash(page, tag) == body_hash(base, tag):
            failures.append(
                f"{desc} case no longer discriminates: the edit did not change the raw "
                f"<{tag}> text, so the gate would answer the same with the defect restored")

    # A finding has to name the line a reader can go to, on each page it can fire on.
    rc, out = run_against(PAGE.replace("<body", '<body style="color:red"', 1))
    want = PAGE[:PAGE.index("<body")].count("\n") + 1
    if f"site/index.html:{want}" not in out:
        failures.append(f"the style= finding does not name the right line on index: <body> is on "
                        f"line {want}. It said: {out!r}")
    if "<body" in PAGE_404:
        rc, out = run_against({"404.html": PAGE_404.replace("<body", '<body style="color:red"', 1)})
        want = PAGE_404[:PAGE_404.index("<body")].count("\n") + 1
        if f"site/404.html:{want}" not in out:
            failures.append(f"the style= finding does not name the right line on 404: <body> is on "
                            f"line {want}. It said: {out!r}")

    # P5: the on* finding names its line too, on each page it can fire on.
    rc, out = run_against(PAGE.replace("<body", '<body onload="x"', 1))
    want = PAGE[:PAGE.index("<body")].count("\n") + 1
    if f"site/index.html:{want}" not in out:
        failures.append(f"the on* finding does not name the right line on index: <body> is on "
                        f"line {want}. It said: {out!r}")
    if "<body" in PAGE_404:
        rc, out = run_against({"404.html": PAGE_404.replace("<body", '<body onload="x"', 1)})
        want = PAGE_404[:PAGE_404.index("<body")].count("\n") + 1
        if f"site/404.html:{want}" not in out:
            failures.append(f"the on* finding does not name the right line on 404: <body> is on "
                            f"line {want}. It said: {out!r}")

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

    # Relocating index's script onto the 404 page must fail BOTH pages in the model phase.
    rc, out = run_against({"index.html": NOSCRIPT_INDEX, "404.html": SCRIPT_ON_404})
    if "site/index.html" not in out or "site/404.html" not in out:
        failures.append(f"moving the script did not fault both pages: {out!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {LEGACY_CASE_COUNT} recorded cases for the CSP hash gate across six review rounds, "
          f"{len(SCOPE_CASES)} row 3.18 and P5 document, page and filesystem cases, and "
          f"{io_case_count} injected I/O failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
