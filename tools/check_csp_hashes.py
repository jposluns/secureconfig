#!/usr/bin/env python3
"""Check that every inline block in each listed site page is pinned by hash in the site/_headers CSP.

WHY: the site drops `'unsafe-inline'` and pins every inline stylesheet and script by hash. A hash
is exact, so editing a block without repinning it produces a page whose style or script the browser
silently refuses. Nothing said so, and the page is the first thing a security-minded reader
inspects.

THIS GATE COVERS A KNOWN LIST OF PAGES, NOT ONE. `site/_headers` serves a single Content-Security-
Policy over the whole site, so its `style-src`/`script-src` are a UNION of every page's block hashes.
The gate reads each page in `PAGES` with its declared inline-block shape and proves that page's every
block is pinned. An `.html` or `.htm` (any case) under `site/` that is NOT in `PAGES` is refused, because it is
served under the same CSP and its blocks would otherwise go unverified: that omission (site/404.html shipped
pinned but unchecked) is the failure this list closes.

IT REFUSES WHAT IT CANNOT MODEL, WHICH IS THE WHOLE DESIGN. Four rounds were spent teaching this gate
about HTML: `src` on a style, foreign content in `<svg>`, HTML integration points, MathML, inert
script types. Each round closed the case in front of it and the next round found another divergence
between `html.parser` and a browser, including two silent fail-opens: a `<style>` inside `<svg><title>`
that `html.parser` swallows as RCDATA and never reports at all, and a `<script>` containing
`<!--<script>` where the parser stops at the first `</script>` and a browser does not. Modelling HTML
well enough to hash it is a real project, and these are hand-written files with one or two inline
blocks each.

So the model is deliberately tiny, declared PER PAGE, and everything outside it is a finding:

  - each page declares how many `<style>` and `<script>` it carries, each count 0 or 1; the gate
    refuses a page whose observed count differs (which catches a second block it cannot tell apart, a
    required block gone missing, and a block relocated onto a page declared to have none), and refuses
    a declared count outside {0, 1} as a deliberate-model-change-not-a-config-edit;
  - each present block carries NO attributes, and is NOT written self-closing: `html.parser` reads
    `<style/>` as an empty element and never enters CDATA, while a browser ignores the self-closing
    flag and reads to the real `</style>`. That one was the worst thing this gate has done. It hashed
    the empty string, printed that hash in its own failure message, and went green once an author
    pinned what it asked for, with the whole stylesheet refused by the browser;
  - every literal `<style` or `<script` in a page accounted for, either as one of its declared
    elements or as text INSIDE one of them (a `<style>` written in a JavaScript string is fine and is
    the round-1 case; one hiding anywhere else is not);
  - every literal `style=` accounted for the same way, because the blind spot that hides an element
    hides an attribute too: `<title>` content is RCDATA, so a `style=` smuggled through `<svg><title>`
    was invisible here and applied in a browser;
  - exactly one `<meta charset="utf-8">` and no other charset declaration per page, because this
    always decodes UTF-8 and a page declaring something else would be decoded, and hashed, differently
    by a browser that has no transport charset to override it;
  - no `<!--` inside any script, because that is what opens HTML's script-data escape states, which is
    where the parser and the browser part company;
  - no NUL byte, which a browser's tokenizer turns into U+FFFD before hashing and this would not.

Any of those fails with a message naming the page and saying it outgrew the gate.

THE ONE POLICY, UNDER `/*`. `site/404.html` is served as the body for any unmatched request path, and
Cloudflare matches `_headers` rules against the REQUESTED URL, so a CSP set (or detached) under any
path-scoped rule can govern the 404 page on those paths while a root-only scan never sees it. A rule
set the gate cannot prove governs every listed page on every serving path is outside the model, so the
gate requires exactly ONE Content-Security-Policy across the whole `_headers` file, under the BARE
`/*` rule (an absolute-URL rule such as `https://host/*` is scoped by Cloudflare to that one host, so
it would leave every other host uncovered), and refuses any other rule that sets or detaches Content-Security-Policy anywhere (a rule
carrying only unrelated headers is fine).

WHAT IT STILL DOES NOT COVER, stated rather than left to be found: a document embedded with `srcdoc`
inherits a page's CSP, and nothing here looks inside one; and a directory SYMLINKED under `site/` is not descended
into, so pages reached only through one are not scanned. A STALE pin (a hash left in a gate-selected directive
after its block was edited or deleted) IS now rejected as an orphan (row 3.15); it is not a fail-open,
but dead allowlist entries otherwise accumulate in site/_headers.

WHAT IT HASHES: each file's bytes, decoded, with CRLF and lone CR normalized to LF, because HTML's
input-stream preprocessing normalizes CR and CRLF to LF before tokenizing, so a DOM never contains a
CR and a CSP hash covers the normalized text. Reading raw bytes made this gate demand a hash no
browser computes.

WHICH DIRECTIVE GOVERNS. CSP3's fallback chain, in order: `script-src-elem`, then `script-src`, then
`default-src`, and the style equivalent. Names are matched case-insensitively and the first occurrence
of a directive wins, both per CSP3.

THE HEADERS FILE IS CLOUDFLARE'S. A rule may be a path or an absolute URL. `#` starts a comment. A
single header VALUE is more than one policy when it contains a comma, and a browser enforces each, so
a comma is refused. A header name prefixed with `!` DETACHES it: `! Content-Security-Policy` removes
the policy, which has no colon and so once passed silently.

WHAT IT DOES NOT PROVE: that the CSP is otherwise sound, or that the hashed content is safe.
`script-src` is hash-only with no `'self'`, so the first external script or stylesheet anyone adds is
blocked by the browser and no gate here says so.
"""
import base64
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# (page path, declared inline-block shape). Every count is 0 or 1; a page with two blocks of a kind
# needs a gate that can tell them apart, which is a deliberate model change, not a dict edit. Every
# `.html` under site/ MUST appear here, because all of them are served under the one /* CSP.
PAGES = ((Path("site") / "index.html", {"style": 1, "script": 1}),
         (Path("site") / "404.html", {"style": 1, "script": 0}))
HEADERS = Path("site") / "_headers"
SITE = Path("site")
# (tag, the directives that can govern an inline element of that tag, in CSP3 fallback order).
KINDS = (("script", ("script-src-elem", "script-src", "default-src")),
         ("style", ("style-src-elem", "style-src", "default-src")))
OPENER = re.compile(r"<(style|script)\b", re.I)
STYLE_ATTR = re.compile(r"\bstyle\s*=", re.I)
CHARSET = re.compile(r"charset\s*=", re.I)
META_UTF8 = '<meta charset="utf-8">'
CSP = "content-security-policy"
# CSP3 allows sha256, sha384 and sha512, and matches the algorithm name case-insensitively.
ALGORITHMS = (("sha256", hashlib.sha256), ("sha384", hashlib.sha384), ("sha512", hashlib.sha512))


class Inline(HTMLParser):
    """Collect the text of every <script> and <style>, and any style= attribute."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.blocks = {"script": [], "style": []}
        self.attrs = {"script": [], "style": []}
        self.style_attrs = []
        self.self_closing = []
        self._open = None

    def handle_starttag(self, tag, attrs):
        if any(k.lower() == "style" for k, _ in attrs):
            self.style_attrs.append((tag, self.getpos()[0]))
        if tag in ("script", "style"):
            self._open = tag
            self.blocks[tag].append([])
            self.attrs[tag].append(([k.lower() for k, _ in attrs], self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        # `<style/>` never enters CDATA mode in html.parser, so the element records an EMPTY body and
        # the stylesheet is parsed as markup after it. A browser ignores the self-closing flag on a
        # non-void HTML element and reads to the real `</style>`.
        if tag in ("script", "style"):
            self.self_closing.append((tag, self.getpos()[0]))
        super().handle_startendtag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == self._open:
            self._open = None

    def handle_data(self, data):
        if self._open:
            self.blocks[self._open][-1].append(data)

    def bodies(self, tag):
        return ["".join(parts) for parts in self.blocks[tag]]


def sha256_b64(text):
    return base64.b64encode(hashlib.sha256(text.encode("utf-8")).digest()).decode()


def pin_tokens(text):
    """Every `'<algorithm>-<base64>'` token a browser would accept for this text."""
    return {f"'{name}-{base64.b64encode(fn(text.encode('utf-8')).digest()).decode()}'"
            for name, fn in ALGORITHMS}


def normalize_pin(token):
    """A source expression with its algorithm name lower-cased and its digest folded from the
    base64url alphabet to standard base64.

    CSP3 matches the algorithm ASCII-case-insensitively, so `'SHA256-...'` is the same pin; the base64
    after it is case-SENSITIVE, which is why this cannot simply lower the token. CSP3 also accepts the
    base64url alphabet, treating `-`/`_` as `+`/`/`, so those are folded to the standard alphabet here.
    Standard base64 never contains `-`/`_`, so this is a no-op on a canonically-spelled pin; it lets a
    base64url spelling compare equal to its standard spelling in both block matching and orphan detection.
    """
    head, sep, tail = token.partition("-")
    return head.lower() + sep + tail.replace("-", "+").replace("_", "/") if sep else token


def is_hash_pin(token):
    """True for a CSP hash source expression (`'sha256-...'`, sha384, sha512; algorithm matched
    case-insensitively). Non-hash tokens ('self', 'none', 'unsafe-inline', a directive name, a URL)
    are not policed as orphans."""
    return token.lower().startswith(("'sha256-", "'sha384-", "'sha512-"))


def normalized(data: bytes) -> str:
    """The page as a browser's tokenizer sees it. See WHAT IT HASHES in the docstring."""
    return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def parse_page(html):
    """Parsed inline blocks and style attributes. Lenient by design; simple_enough refuses."""
    p = Inline()
    p.feed(html)
    p.close()
    return p


def guard_config(pages):
    """Refuse a page list this gate cannot honour. These are configuration errors, not page defects."""
    out = []
    if not pages:
        out.append("this gate has an empty page list; it must name at least one page to check")
    seen = set()
    for path, shape in pages:
        if path in seen:
            out.append(f"{path} is listed more than once in this gate's page list")
        seen.add(path)
        if set(shape) != {"style", "script"}:
            out.append(f"the shape for {path} must declare exactly a style and a script count")
            continue
        for tag, n in shape.items():
            if n not in (0, 1):
                out.append(f"the shape for {path} declares {tag}={n}; this gate models 0 or 1 of a "
                           f"kind per page, and extending it to more is a deliberate model change, "
                           f"not a count edit")
    return out


def simple_enough(path, page, html, shape):
    """Reasons this page is outside the shape the gate can hash. See the docstring."""
    out = []
    for tag, line in page.self_closing:
        out.append(f"the <{tag}> at {path}:{line} is written self-closing. html.parser reads that as "
                   f"an empty element and a browser reads to the real </{tag}>, so the hash here "
                   f"would be the hash of nothing; write it with a separate closing tag")
    if CHARSET.search(html.replace(META_UTF8, "", 1)) or META_UTF8 not in html:
        out.append(f"{path} does not declare exactly one {META_UTF8}, and this gate always decodes "
                   f"UTF-8; a different declared charset would make a browser decode other bytes and "
                   f"hash a different stylesheet")
    if "\x00" in html:
        out.append(f"{path} contains a NUL byte, which a browser's tokenizer replaces with U+FFFD "
                   f"before hashing and this gate would not")
    for tag in ("style", "script"):
        bodies = page.bodies(tag)
        if len(bodies) != shape[tag]:
            if shape[tag] == 1:
                out.append(f"the page {path} has {len(bodies)} <{tag}> elements and this gate models "
                           f"exactly one; pinning more than one by hash needs a gate that knows which "
                           f"is which")
            else:
                out.append(f"the page {path} has {len(bodies)} <{tag}> elements and this gate models "
                           f"exactly {shape[tag]} <{tag}> for this page, which is declared to carry "
                           f"none")
            continue
        for names, line in page.attrs[tag]:
            if names:
                out.append(f"the <{tag}> at {path}:{line} carries attributes ({', '.join(names)}), "
                           f"and whether a browser runs an element with them depends on rules this "
                           f"gate does not model; keep it bare or extend the gate deliberately")
    # A literal `style=` the parser never reported is the same blind spot as an unreported element:
    # html.parser swallows <title> content as RCDATA, so an attribute smuggled through <svg><title>
    # was invisible while a browser applies it and CSP-checks it.
    in_body = sum(len(STYLE_ATTR.findall(b))
                  for tag in ("style", "script") for b in page.bodies(tag))
    if len(STYLE_ATTR.findall(html)) != len(page.style_attrs) + in_body:
        out.append(f"the page {path} contains literal `style=` text this gate cannot account for; a "
                   f"style attribute the parser did not report, such as one inside <svg> or <title>, "
                   f"is still applied and still CSP-checked by a browser")
    for script in page.bodies("script"):
        if "<!--" in script:
            out.append(f"the inline <script> in {path} contains `<!--`, which opens HTML's script-data "
                       f"escape states; a browser reads to a later </script> than this parser does, "
                       f"so the hash here would not be the hash there")
            break
    # Every literal opener has to be one of the declared elements or text inside one of them. This is
    # what catches an element the parser never reported: a <style> or <script> inside <svg><title> is
    # swallowed as RCDATA and produces no start tag at all, and it is live in a browser. It is the
    # check that makes a page declared to carry no script safe.
    inside = sum(len(OPENER.findall(b)) for tag in ("style", "script") for b in page.bodies(tag))
    total = len(OPENER.findall(html))
    expected = len(page.bodies("style")) + len(page.bodies("script")) + inside
    if total != expected:
        out.append(f"the page {path} contains {total} literal <style or <script openers and this gate "
                   f"accounts for {expected}; one of them is somewhere the parser did not report an "
                   f"element, such as inside <svg>, <title> or a comment, and a browser may well run it")
    return out


def all_rule_blocks(headers_text):
    """Every rule block in the file, in order, duplicates kept: (rule, [header lines]).

    A rule is a line starting in column zero; its headers are the indented lines under it. `#` is a
    comment. Unlike the earlier root-only reader, this returns EVERY rule, because a CSP set or
    detached under any path-scoped rule can govern the 404 page on that path.
    """
    out, rule, lines = [], None, []
    for raw in headers_text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            if rule is not None:
                out.append((rule, lines))
            rule, lines = raw.strip(), []
        elif rule is not None:
            lines.append(raw.strip())
    if rule is not None:
        out.append((rule, lines))
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    config = guard_config(PAGES)
    if config:
        for why in config:
            print(f"  FAIL  {why}")
        return 1

    listed = {root / path for path, _ in PAGES}
    strays = sorted(p for p in (root / SITE).rglob("*")
                    if p.is_file() and p.suffix.lower() in (".html", ".htm") and p not in listed)
    if strays:
        for p in strays:
            print(f"  FAIL  {p.relative_to(root)} is served under the site's /* CSP but is not in "
                  f"this gate's page list; add it with its inline-block shape, or this gate cannot "
                  f"prove its blocks are pinned")
        return 1

    reasons, parsed = [], {}
    for path, shape in PAGES:
        try:
            html = normalized((root / path).read_bytes())
        except Exception as exc:
            reasons.append(f"could not read {path}: {exc}")
            continue
        page = parse_page(html)
        reasons += simple_enough(path, page, html, shape)
        parsed[path] = page
    if reasons:
        for why in reasons:
            print(f"  FAIL  {why}")
        return 1

    try:
        headers_text = (root / HEADERS).read_text(encoding="utf-8")
    except Exception as exc:
        print(f"  FAIL  could not read {HEADERS}: {exc}")
        return 1

    blocks = all_rule_blocks(headers_text)
    detached = [rule for rule, lines in blocks for line in lines
                if line.startswith("!") and line[1:].split(":", 1)[0].strip().lower() == CSP]
    if detached:
        print(f"  FAIL  {HEADERS} detaches the Content-Security-Policy ({detached[0]}), so a page "
              f"under that rule is served without one at all")
        return 1

    csps = []
    for rule, lines in blocks:
        for line in lines:
            name, sep, value = line.partition(":")
            if sep and name.strip().lower() == CSP:
                csps.append((rule, value.strip()))
    if not csps:
        print(f"  FAIL  no Content-Security-Policy header anywhere in {HEADERS}; the listed pages "
              f"are served without one")
        return 1
    if len(csps) > 1:
        where = ", ".join(rule for rule, _ in csps)
        print(f"  FAIL  {HEADERS} has {len(csps)} Content-Security-Policy headers ({where}), and "
              f"this gate models exactly one Content-Security-Policy, under /*, governing every "
              f"listed page")
        return 1
    rule, csp = csps[0]
    if rule != "/*":
        print(f"  FAIL  the Content-Security-Policy in {HEADERS} is under the rule {rule}, which is "
              f"not the /* rule this gate requires; an absolute-URL or path-scoped rule governs only "
              f"some hosts or paths and leaves the 404 page uncovered on the rest")
        return 1
    if "," in csp:
        # A CSP header value is a comma-separated LIST of policies and a browser enforces every one.
        print(f"  FAIL  the Content-Security-Policy value contains a comma, which makes it more than "
              f"one policy; a browser enforces all of them and this gate reads only the directives it "
              f"can see")
        return 1

    directives = {}
    for d in csp.split(";"):
        parts = d.split()
        if parts:
            # First occurrence wins, per CSP3.
            directives.setdefault(parts[0].lower(), parts)

    findings, verified = [], 0
    used = {}
    used_pins = {}
    for tag, names in KINDS:
        # Resolve each kind's directive once, whether or not any listed page carries that kind: a CSP
        # that fails to constrain a kind at all should never be blessed by this gate.
        chosen = next((n for n in names if n in directives), None)
        used[tag] = chosen
        if chosen is None:
            findings.append(f"the Content-Security-Policy has no {names[1]} directive, and neither "
                            f"{names[0]} nor {names[2]} to fall back to")
            continue
        if "'unsafe-inline'" in directives[chosen]:
            findings.append(
                f"{chosen} carries 'unsafe-inline', which permits any inline <{tag}> including one "
                f"injected into the page. A browser ignores it while a hash is present, so this is "
                f"not broken today; it is one edit from permitting everything, and this site's whole "
                f"claim is that it does not need it")

    for path, shape in PAGES:
        page = parsed[path]
        for tag, _ in KINDS:
            chosen = used[tag]
            for body in page.bodies(tag):
                if chosen is None:
                    continue
                present = {normalize_pin(token) for token in directives[chosen]}
                matched = pin_tokens(body) & present
                if matched:
                    verified += 1
                    used_pins.setdefault(chosen, set()).update(matched)
                else:
                    findings.append(f"{chosen} lacks the hash of the inline <{tag}> in {path} "
                                    f"(sha256-{sha256_b64(body)})")
        for tag, line in sorted(set(page.style_attrs)):
            findings.append(
                f"<{tag}> at {path}:{line} carries a style= attribute. A CSP hash covers an "
                f"element's text, never an attribute, so it needs the rule moved into the stylesheet, "
                f"or a style-src-attr directive carrying 'unsafe-hashes' and the attribute's own "
                f"hash, which this gate does not check")

    # Orphan pins (row 3.15): a hash left in a gate-selected directive that no listed block uses.
    # Not a fail-open (an orphan cannot make a real block go unhashed), but a stale pin is dead
    # weight in site/_headers after its block is edited or removed, so reject it. Only the chosen
    # directive per kind is policed, matching the model above; a shared pin used by several pages is
    # in the used set and is not an orphan.
    for chosen in sorted({c for c in used.values() if c is not None}):
        present_hashes = {normalize_pin(t) for t in directives[chosen] if is_hash_pin(t)}
        for orphan in sorted(present_hashes - used_pins.get(chosen, set())):
            findings.append(f"{chosen} pins {orphan}, an orphan hash no inline <style>/<script> on "
                            f"any listed page uses; remove the stale pin")

    declared_total = sum(n for _, shape in PAGES for n in shape.values())
    if not findings and verified != declared_total:
        findings.append(f"internal accounting error: verified {verified} inline blocks but the page "
                        f"shapes declare {declared_total}")

    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {verified} inline blocks across {len(PAGES)} pages are pinned by hash in the "
          f"{HEADERS} CSP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
