#!/usr/bin/env python3
"""Cases for check_csp_hashes.py, one per defect a reviewer demonstrated against it.

Five rounds are recorded, and the arc matters more than any single case. Round 1 broke a
regular-expression reader and the gate moved to `html.parser`. Rounds 2, 3 and 4 then spent
themselves teaching that parser about HTML: `src` on a style, foreign content, integration points,
MathML, inert script types. Round 3 found that a round-2 fix was BACKWARDS and that the case written
for it was holding the wrong answer in place. Round 4 found two more silent fail-opens in the same
family, a `<style>` inside `<svg><title>` that `html.parser` swallows entirely and a `<script>` whose
escape states it misreads. Round 5 found three wrong pages that satisfied every one of the new guards,
the worst of which had this gate printing the hash of the EMPTY STRING in its own failure message and
going green once an author pinned what it asked for.

Round 6 (this one) generalized the gate from one hard-coded page to a KNOWN LIST of pages, because
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
"""
import base64
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
PAGE = (ROOT / "site" / "index.html").read_bytes().decode("utf-8")
PAGE_404 = (ROOT / "site" / "404.html").read_bytes().decode("utf-8")
HEADERS = (ROOT / "site" / "_headers").read_text(encoding="utf-8")


def run_against(page=None, headers=None, extra_files=None, gate=None):
    """Run the real gate against a copy of the site. Returns (exit, full output).

    `page` is None (both real pages), a str (an index.html override, so every pre-round-6 case is
    byte-identical), or a dict {"index.html"/"404.html": text} overriding those pages; an unknown key
    RAISES, so a typo cannot silently test a pristine corpus. `extra_files` writes extra files under
    site/ (for the unlisted-page case). `gate` is an (old, new) pair applied to the gate SOURCE (for
    the config-guard case).
    """
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        (d / "site").mkdir()
        src = (TOOLS / "check_csp_hashes.py").read_text(encoding="utf-8")
        if gate is not None:
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
        for name, text in (extra_files or {}).items():
            (d / "site" / name).write_bytes(text.encode("utf-8"))
        (d / "site" / "_headers").write_text(
            headers if headers is not None else HEADERS, encoding="utf-8")
        r = subprocess.run([sys.executable, "tools/check_csp_hashes.py"], cwd=d,
                           capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
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


def main() -> int:
    failures = []
    for desc, page, headers, must_fail, expected in CASES:
        rc, out = run_against(page, headers, **EXTRA_ARGS.get(desc, {}))
        if bool(rc) != must_fail:
            want = "fail" if must_fail else "pass"
            failures.append(f"{desc}: expected the gate to {want}, it did not ({out!r})")
        elif expected is not None and expected not in out:
            failures.append(
                f"{desc}: the gate's exit status was right but its message was not. "
                f"Expected it to contain {expected!r}. It said: {out!r}")

    # The repinned cases only mean something if their repin actually moved the hash.
    for page, tag, base, desc in ((COMMENT_PAGE, "style", PAGE, "the <!-- in stylesheet text"),
                                  (STRING_PAGE, "script", PAGE, "the <style> in a JavaScript string"),
                                  (CRLF_PAGE, "style", PAGE, "the CRLF"),
                                  (E404, "style", PAGE_404, "the 404 stylesheet edit")):
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

    # Relocating index's script onto the 404 page must fail BOTH pages in the model phase.
    rc, out = run_against({"index.html": NOSCRIPT_INDEX, "404.html": SCRIPT_ON_404})
    if "site/index.html" not in out or "site/404.html" not in out:
        failures.append(f"moving the script did not fault both pages: {out!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} recorded cases for the CSP hash gate, across six review rounds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
