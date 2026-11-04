#!/usr/bin/env python3
"""Check that the published site is self-contained and that only /draft/ and the 404 are noindex.

WHY: since promotion (baseline SPECIFICATION section 4.1 item 5) the generated pages are served
from the site root. A root-relative link that names no file ships a broken page; an absolute URL
on this site's own host bypasses that check and can pin a scheme or an alias this gate cannot
read; a stray robots meta on an indexable page, or a lost one on the 404 or the /draft/ review
page, silently changes what search engines index; and the /draft/ review page stays out of the
published indexes (SPECIFICATION section 4.1 item 2). Nothing else in the suite checks any of
that. The sitemap gates import BASE and DRAFT below, and BASE = "/" switches their staged-draft
rules off; tools/check_sitemap.py keeps /draft/ out of sitemap.xml through its noindex rule.

A PAGE is any file under site/ named .html or .htm in any case, read by the CSP gate's own suffix
rule (check_csp_hashes.name_suffix), so a page the CSP gate checks is a page this gate checks too.

PART 1, INDEXABILITY:
  - site/draft/index.html (the "Draft review" page) and site/404.html each carry exactly 1 robots
    meta element, read by html.parser (so a commented-out one does not count, attribute case and
    quoting do not matter, and of duplicate attributes the first counts, as in a browser), whose
    content is `noindex, nofollow` (case and spacing aside);
  - every other page carries NO robots meta element at all: the generated pages are indexable and
    carry none, so one appearing is an edit this gate refuses rather than guesses about;
  - site/_redirects does not exist: a missing path returns the 404 page with status 404, never a
    redirect (the owner's rule). tools/check_csp_hashes.py holds site/_headers, X-Robots-Tag
    included.

PART 2, SELF-CONTAINED:
  - every URL a page carries, in any attribute whose name ends in `href` or `src` (so `xlink:href`
    too) and in `srcset`, `imagesrcset`, `formaction`, `action`, `ping`, `poster` and `background`,
    is an in-page `#` anchor, a root-relative path that names a file under site/ (a folder path
    names its index.html), or an absolute http(s) URL with a non-empty authority written as
    `scheme://host`, on a host other than this site's;
  - refused, because a browser normalizes them onto a host or file the check above does not see:
    any whitespace, control character or backslash in a URL; `https:///host` and other spellings
    without a host right after `//`; this site's host in any case, with a trailing dot or
    percent-encoded (a same-site link is written root-relative, so the file check reads it); a
    host that is not plain ASCII after percent-decoding (fullwidth letters, U+3002 and the other
    forms IDNA maps onto ASCII); a `pages.dev` host (the Pages project's own aliases); a
    scheme-relative URL; and a relative path, since the pages use root-relative paths;
  - a `<link rel="canonical">` href, which is required to be absolute, has its own rule instead:
    each of the 7 indexable pages (INDEXABLE below) and the /draft/ review page carries exactly 1,
    equal byte for byte to `https://secureconfig.ai` plus that page's own root path (`/`,
    `/guides/`, ..., `/draft/`); the 404 page carries none; any other page carries at most its own;
  - any `http-equiv` attribute is refused (a refresh would navigate away without a link);
  - every link that opens a new tab carries the visually hidden "(opens in a new tab)";
  - only the landing page, the Disclosure page and the Licence page link the Disclosure and Licence
    pages (the owner's template note of 2026-11-03: they left the top bar), and no page links the
    /draft/ review page. Both rules compare the FILE a root-relative URL resolves to, read as
    resolves() reads it (query and fragment cut, percent-decoded, dot segments resolved, a folder
    naming its index.html), with site/disclosure/index.html, site/license/index.html and
    site/draft/index.html, so `/draft/?x`, `/draft//`, `/guides/../draft/`, `/%64raft/` and
    `/draft/index.html#a` are each a link to the review page;
  - no stylesheet under site/ carries `@import` in any spelling (CSS escapes decoded), every
    `url(` in one is relative and resolves to a file inside site/assets/, and a site/assets/site.css,
    where one exists (scripts/build-site.py --check allows that 1 file beside the pages and the
    copied files), matches the whole permitted grammar: rules (at the top level or inside
    `@media (prefers-color-scheme: dark|light)`) whose only declarations set `--sw` or
    `--logo-inset` to a number (baseline README, "Per-site constants").

PART 3, THE PUBLISHED INDEXES (site/llms.txt, site/llms-full.txt, site/robots.txt and
site/.well-known/security.txt): none of them refers to the /draft/ review page. Each file is read
without newline translation, and each finding names the file and the line, counting `\\n` only (a
U+2028 or a lone `\\r` ends no line):
  - every line is NORMALIZED: the round { percent-decode; `html.unescape` } repeats until the line
    stops changing, at most 8 rounds (a line still changing in a 9th round is refused); then
    Unicode NFKC, case folding and every `\\` read as `/`;
  - site/llms.txt, site/robots.txt and site/.well-known/security.txt are hand-written indexes that
    never need the word, so any literal `draft` in their normalized text with every ASCII tab and
    CR deleted is refused, read across line ends too (deleting only joins characters, so that text
    holds every `draft` the normalized text holds);
  - site/llms-full.txt, the generated guide corpus, says "draft" in prose and in `draft-ietf-...`
    names, so there the rule reads URLs and never a prose word: each URL read in one of the 3 ways
    below is RESOLVED against https://secureconfig.ai/llms-full.txt and refused when it lands on
    this site with the draft path. A finding names the way it was read, once per line and way:
      a. Markdown, parsed by the pinned markdown-it-py with its CommonMark rules (the pin carries
         no linkify-it-py, so markdown-it reads no bare URL; c reads them): each inline link
         destination, image source and autolink, and every reference definition, used or not,
         duplicates too, as written (entities and backslash escapes decoded, nothing
         percent-encoded); a definition is reported on the line its label closes, and an
         unbracketed definition destination that ends its line is read again joined to the first
         word of the next line (a line end inside it). The parse reads `\\r\\n` as `\\n` and
         deletes a lone `\\r`, so its lines are the lines counted above;
      b. raw HTML, the html_block and html_inline tokens of a, read by html.parser (character
         references decoded), each duplicate attribute too: every attribute named or ending in
         `href` or `src` (`xlink:href` among them), and action, formaction, data, cite, poster,
         background and longdesc; each whitespace-separated ping URL; each srcset and imagesrcset
         candidate URL, split by the HTML candidate rules; and, on an element with an
         `http-equiv` (exactly that name) that is `refresh` once trimmed and case folded, the URL
         of each content value by the HTML standard's shared declarative refresh steps (digits
         and dots, then `;`, `,` or whitespace, then an optional `url` `=` and an optional quote
         that ends the URL at its partner);
      c. bare URLs and paths: each line normalized as above and split into words at whitespace
         other than tab and CR and at any of ( ) [ ] < > { } " ' ` | *, with any trailing
         . , ; : ! ? cut. A tab, CR or decoded LF inside a word reads the word twice, once with
         them deleted and once split at them. A word is read when it starts with a special
         scheme (http, https, ws, wss or ftp) and a `:`; when it starts with a host name (dotted
         labels ending in 2 or more letters, or `www.`), as `http://` and the word; or when it
         holds a `/`. A word with another scheme is read from after its first `:` when that holds
         a `/`. A word with none of these, such as "drafting", "draft." or `draft-ietf-...`, is
         prose and never read;
    RESOLVED: the URL is browser-normalized (leading and trailing C0 controls and spaces stripped,
    every tab, LF and CR deleted, `\\` read as `/`, as for any special scheme and any URL relative
    to an https base); `https:` without `//` after it is relative to the base, as is a URL with no
    scheme; another special scheme, or a leading `//`, skips every slash up to its host; any other
    scheme (`mailto:`, `file:`, `javascript:` ...) leaves the site. The host, without userinfo and
    port, is percent-decoded, U+3002, U+FF0E and U+FF61 read as dots, NFKC and case folded, its
    trailing dot cut, and is this site when it is secureconfig.ai, a subdomain of it, pages.dev or
    a subdomain of that (the Pages aliases; llms-full.txt lists none). The path, query and
    fragment cut, is percent-decoded until it stops changing, at most 8 rounds (a path still
    changing is refused), then has every tab, LF and CR deleted, `\\` read as `/`, NFKC and case
    folding, and its `.` and `..` segments resolved; it is the DRAFT PATH when its first non-empty
    segment is `draft`, or `draft` followed by a character other than a-z, 0-9, `_` or `-` (so
    `draft.html`, which Pages serves as the review page, too).
    So `/draft/`, `./draft/`, `\\draft\\`, `%2Fdraft%2F`, `dr&#97;ft/`, `/draft.html`,
    `secureconfig.ai/draft/`, `[x](draft)`, `[x](<draft>)`, `[x](\\ndraft)`, `![x](draft)`,
    `<https:draft>`, `[x]: draft`, `> [x]: draft`, `[x]: dr\\naft`, `href="draft"`,
    `href="\\x01draft"`, `href="htt\\nps:draft"`, `srcset="a.png 1x, draft 2x"`,
    `content="0 draft"`, `content="0;url=&quot;draft&quot;"` on a refresh, `[x](dr&#9;aft)` and
    `[x](dr%0Daft)` are refused, while "drafting", "drafted", "a draft.", "the draft's",
    "draft / final", "and Raft", "draft-ietf-oauth-v2-1", a link title or a description meta
    saying "draft", a content on an element with `data-http-equiv`, `https://draft.example/`,
    `https://draft/` and `https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/` are accepted.
    Code spans and code blocks are read by c only. Markdown inline parsing, raw HTML and bare
    words skip a block or line whose normalization with every tab, LF and CR deleted holds no
    `draft`, as no URL read from it can then have the draft path.

Exit 0 ok, 1 on a finding, 2 on a read error.
Usage: python3 -I -B tools/check_draft.py [--root <repository root>]
"""
import argparse
import html
import re
import sys
import unicodedata
from bisect import bisect_right
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_csp_hashes import name_suffix  # noqa: E402  (the CSP gate's page-name rule)

SITE = Path("site")
# The published base path and the review-page tree, imported by tools/check_sitemap.py and
# tools/check_sitemap_lastmod.py. At "/" their staged-draft rules switch off.
BASE = "/"
DRAFT = Path("site") / "draft"
SITE_HOST = "secureconfig.ai"
NEWTAB = "(opens in a new tab)"
URL_FN = re.compile(r"url\(\s*(['\"]?)([^'\")]*)\1\s*\)", re.I)
# The pages that may link /disclosure/ and /license/ (the owner's template note of 2026-11-03).
ABOUT_PAGES = {"index.html", "disclosure/index.html", "license/index.html"}
# The files those 2 rules protect, compared after resolution (see resolved()).
ABOUT_TARGETS = ("disclosure/index.html", "license/index.html")
REVIEW_PAGE = "draft/index.html"
# The 7 indexable pages, each carrying exactly 1 canonical: the origin plus its own root path.
INDEXABLE = ("index.html", "guides/index.html", "for-ai/index.html", "for-humans/index.html",
             "checklist/index.html", "disclosure/index.html", "license/index.html")
NOTFOUND = "404.html"
# The published indexes (PART 3): the hand-written ones refuse the word, read after normalized();
# the guide corpus refuses each URL that resolves to the draft path.
STRICT_INDEXES = ("llms.txt", "robots.txt", ".well-known/security.txt")
CORPUS_INDEX = "llms-full.txt"
DRAFT_WORD = re.compile(r"draft")
DECODE_ROUNDS = 8
# The URL every llms-full.txt URL is resolved against, and the draft path's first segment.
CORPUS_URL = "https://secureconfig.ai/llms-full.txt"
DRAFT_SEGMENT = re.compile(r"draft(?![a-z0-9_-])")
SCHEME = re.compile(r"([a-zA-Z][a-zA-Z0-9+.-]*):")
SPECIAL = {"http", "https", "ws", "wss", "ftp", "file"}
C0_SPACE = "".join(map(chr, range(0x21)))
# The HTML attributes PART 3 reads (besides any name ending in href or src, ping, the candidate
# lists and a refresh content), and ASCII whitespace as the HTML standard defines it.
INDEX_URL_NAMES = {"action", "formaction", "data", "cite", "poster", "background", "longdesc"}
HTML_SPACE = " \t\n\r\f"
# Bare words (form c): the separators, the trailing punctuation cut, a host name at the start.
WORD_BREAK = re.compile(r"[^\S\t\r\n]+|[()\[\]<>{}\"'`|*]")
INSIDE_BREAK = re.compile(r"[\t\r\n]")
HOST_START = re.compile(r"(?:www\.|(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d*)?(?:[/?#]|$))")
# How each URL was read, named in a finding.
MD_LINK = "a Markdown link destination"
MD_IMAGE = "a Markdown image source"
MD_AUTOLINK = "a Markdown autolink"
MD_DEFINITION = "a Markdown reference definition"
MD_JOINED = "a Markdown reference definition joined across a line end"
HTML_REFRESH = "an HTML meta refresh URL"
BARE = "a bare URL or path"
# The pages that carry a robots meta, each exactly 'noindex, nofollow', and what every other page
# must not carry at all.
NOINDEX_PAGES = {"draft/index.html", "404.html"}
URL_LISTS = {"srcset", "imagesrcset"}
URL_NAMES = {"formaction", "action", "ping", "poster", "background"}
BAD_URL_CHARS = re.compile(r"[\x00-\x20\x7f\\]")
AUTHORITY = re.compile(r"(?i)^https?://[^/?#\\\s]")
# site.css: the whole permitted grammar (comments removed first).
DECL = r"\s*--(?:sw|logo-inset)\s*:\s*\d+(?:\.\d+)?\s*"
RULE = rf"\s*[^{{}};@\\]+\{{{DECL}(?:;{DECL})*;?\s*\}}"
MEDIA = rf"\s*@media\s*\(\s*prefers-color-scheme\s*:\s*(?:dark|light)\s*\)\s*\{{(?:{RULE})+\s*\}}"
SITE_CSS = re.compile(rf"(?:{RULE}|{MEDIA})+\s*")
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
CSS_ESCAPE = re.compile(r"\\([0-9a-fA-F]{1,6})[ \t\n\r\f]?|\\(.)", re.S)
AT_KEYWORD = re.compile(r"@((?:[A-Za-z0-9_-]|\\[0-9a-fA-F]{1,6}[ \t\n\r\f]?|\\[^\n\r\f0-9a-fA-F])+)")


def page_files(base):
    """Every .html or .htm file under base, in any case, as the CSP gate names a page."""
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*") if p.is_file() and name_suffix(p.name) in (".html", ".htm"))


def site_host(host):
    """True for this site's host or a Pages alias, after the normalizations a browser applies."""
    host = unquote(host or "").lower().rstrip(".")
    return (host == SITE_HOST or host.endswith("." + SITE_HOST) or host == "pages.dev"
            or host.endswith(".pages.dev"))


class Page(HTMLParser):
    """URLs, robots meta elements, http-equiv attributes and new-tab links of 1 page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []          # (line, attribute, value)
        self.canonicals = []    # (line, value) of each <link rel="canonical"> href
        self.robots = []        # (line, content)
        self.http_equiv = []    # line
        self.newtab = []        # (line, text)
        self._open = []

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        names = {k for k, _ in attrs}
        # A <link rel="canonical"> href is required to be absolute, so it has its own rule
        # (check() below) instead of the same-site refusal; the first rel counts, as in a browser.
        rels = [v for k, v in attrs if k == "rel"]
        canonical = tag == "link" and bool(rels) and (rels[0] or "").strip().lower() == "canonical"
        for k, v in attrs:
            if v is None:
                continue
            if canonical and k == "href":
                self.canonicals.append((line, v))
                continue
            if k in URL_LISTS:
                for part in v.split(","):
                    if part.strip():
                        self.urls.append((line, k, part.strip().split()[0]))
            elif k == "ping":
                for part in v.split():
                    self.urls.append((line, k, part))
            elif k.endswith("href") or k.endswith("src") or k in URL_NAMES:
                self.urls.append((line, k, v))
        # A browser keeps the first of duplicate attributes, so this reads them the same way.
        a = {}
        for k, v in attrs:
            a.setdefault(k, v or "")
        if "http-equiv" in names:
            self.http_equiv.append(line)
        if tag == "meta" and a.get("name", "").strip().lower() == "robots":
            self.robots.append((line, a.get("content", "")))
        if tag == "a":
            # An aria-label replaces the link text as its accessible name, so it may carry the hint.
            self._open.append([line, a.get("aria-label", ""), a.get("target") == "_blank"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        for a in self._open:
            a[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._open:
            line, text, blank = self._open.pop()
            if blank:
                self.newtab.append((line, text))


def parse(text):
    p = Page()
    p.feed(text)
    p.close()
    return p


def resolved(root, path):
    """The resolved file a root-relative path names under site/ (query and fragment cut,
    percent-decoded, dot segments resolved, a folder naming its index.html), or None when it
    leaves site/."""
    rel = unquote(path.lstrip("/").split("#", 1)[0].split("?", 1)[0])
    target = (root / SITE / rel)
    if rel == "" or rel.endswith("/"):
        target = target / "index.html"
    target = target.resolve()
    try:
        target.relative_to((root / SITE).resolve())
    except ValueError:
        return None
    return target


def resolves(root, path):
    """True when a root-relative path names a file under site/."""
    target = resolved(root, path)
    return target is not None and target.is_file()


def normalized(text):
    """Published-index text (PART 3) put through { percent-decode; html.unescape } until stable,
    then NFKC, case folded and with `\\` read as `/` (the kept text), or None when it still
    changes in round DECODE_ROUNDS + 1."""
    for _ in range(DECODE_ROUNDS + 1):
        decoded = html.unescape(unquote(text))
        if decoded == text:
            return unicodedata.normalize("NFKC", text).casefold().replace("\\", "/")
        text = decoded
    return None


def deleted(text):
    """The text with every tab and CR deleted (a browser deletes them from a URL)."""
    return text.replace("\t", "").replace("\r", "")


def browser_url(value):
    """value as a URL parser first reads it: leading and trailing C0 controls and spaces stripped,
    every tab, LF and CR deleted."""
    return value.strip(C0_SPACE).replace("\t", "").replace("\n", "").replace("\r", "")


def on_site(host):
    """True for this site's host, a subdomain of it or a Pages alias, read as a URL parser reads
    a host (percent-decoded, the IDNA full stops read as dots, NFKC, case folded, trailing dot
    cut)."""
    host = unquote(host)
    for dot in "\N{IDEOGRAPHIC FULL STOP}\N{FULLWIDTH FULL STOP}\N{HALFWIDTH IDEOGRAPHIC FULL STOP}":
        host = host.replace(dot, ".")
    host = unicodedata.normalize("NFKC", host).casefold().rstrip(".")
    return (host == SITE_HOST or host.endswith("." + SITE_HOST) or host == "pages.dev"
            or host.endswith(".pages.dev"))


def draft_path(path):
    """True when a resolved path is the draft path, None when it still changes after
    DECODE_ROUNDS rounds of percent-decoding, else False (the RESOLVED rule of PART 3)."""
    path = re.split(r"[?#]", path, maxsplit=1)[0]
    for _ in range(DECODE_ROUNDS + 1):
        decoded = unquote(path)
        if decoded == path:
            break
        path = decoded
    else:
        return None
    path = unicodedata.normalize("NFKC", deleted(path).replace("\n", "").replace("\\", "/"))
    segments = []
    for segment in path.casefold().split("/"):
        if segment in (".", ""):
            continue
        if segment == "..":
            segments = segments[:-1]
            continue
        segments.append(segment)
    return bool(segments) and bool(DRAFT_SEGMENT.match(segments[0]))


def refuses(value):
    """True when value, resolved against CORPUS_URL, is on this site with the draft path; None
    when its path still changes after DECODE_ROUNDS rounds; else False."""
    url = browser_url(value).replace("\\", "/")
    m = SCHEME.match(url)
    if m:
        scheme = m.group(1).lower()
        if scheme not in SPECIAL or scheme == "file":
            return False
        rest = url[m.end():]
        # The URL standard: the base's own scheme without `//` after it is relative to the base;
        # any other special scheme skips every slash up to its host.
        if scheme == "https" and not rest.startswith("//"):
            url = rest
        else:
            url = "//" + rest.lstrip("/")
    if url.startswith("//"):
        rest = url.lstrip("/")
        cut = re.search(r"[/?#]", rest)
        authority, path = (rest[:cut.start()], rest[cut.start():]) if cut else (rest, "/")
        host = authority.rsplit("@", 1)[-1]
        if not host.startswith("["):
            host = host.split(":", 1)[0]
        if not on_site(host):
            return False
        return draft_path(path)
    # Relative to https://secureconfig.ai/llms-full.txt: a path, a query or fragment of the
    # corpus itself, or a path relative to the root folder.
    if url.startswith("/"):
        return draft_path(url)
    if url[:1] in ("", "?", "#"):
        return False
    return draft_path("/" + url)


def refresh_url(content):
    """The URL of a meta refresh content by the HTML standard's shared declarative refresh steps,
    or None when it names none."""
    pos, n = 0, len(content)

    def skip_space(pos):
        while pos < n and content[pos] in HTML_SPACE:
            pos += 1
        return pos

    pos = skip_space(pos)
    start = pos
    while pos < n and content[pos].isdigit() and content[pos].isascii():
        pos += 1
    if pos == start and (pos >= n or content[pos] != "."):
        return None
    while pos < n and ((content[pos].isdigit() and content[pos].isascii()) or content[pos] == "."):
        pos += 1
    if pos >= n:
        return None
    if content[pos] not in ";," + HTML_SPACE:
        return None
    pos = skip_space(pos)
    if pos < n and content[pos] in ";,":
        pos = skip_space(pos + 1)
    if pos >= n:
        return None
    url = content[pos:]
    # An optional `url` `=` (any case, whitespace around the `=`), then an optional quote.
    probe = pos
    if content[probe:probe + 1] in ("U", "u"):
        probe += 1
        if content[probe:probe + 1] not in ("R", "r"):
            return url
        probe += 1
        if content[probe:probe + 1] not in ("L", "l"):
            return url
        probe = skip_space(probe + 1)
        if content[probe:probe + 1] != "=":
            return url
        probe = skip_space(probe + 1)
    quote = content[probe:probe + 1] if content[probe:probe + 1] in ("'", '"') else ""
    url = content[probe + len(quote):]
    if quote and quote in url:
        url = url[:url.index(quote)]
    return url


def srcset_urls(value):
    """The candidate URLs of a srcset or imagesrcset value, split by the HTML candidate rules."""
    urls, pos, n = [], 0, len(value)
    while True:
        while pos < n and (value[pos] in HTML_SPACE or value[pos] == ","):
            pos += 1
        if pos >= n:
            return urls
        start = pos
        while pos < n and value[pos] not in HTML_SPACE:
            pos += 1
        url = value[start:pos]
        if url.endswith(","):
            urls.append(url.rstrip(","))
            continue
        urls.append(url)
        # The descriptors run to the next comma outside parentheses.
        paren = False
        while pos < n:
            c = value[pos]
            pos += 1
            if c == "(":
                paren = True
            elif c == ")":
                paren = False
            elif c == "," and not paren:
                break


class IndexHTML(HTMLParser):
    """The URL-valued attributes of 1 raw HTML fragment of llms-full.txt (form b of PART 3)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []  # (line within the fragment, way read, value)

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        refresh = any(k == "http-equiv" and (v or "").strip().casefold() == "refresh"
                      for k, v in attrs)
        for k, v in attrs:
            if v is None:
                continue
            if k in URL_LISTS:
                values = srcset_urls(v)
            elif k == "ping":
                values = v.split()
            elif k.endswith("href") or k.endswith("src") or k in INDEX_URL_NAMES:
                values = [v]
            elif k == "content" and refresh:
                url = refresh_url(v)
                self.urls.extend([(line, HTML_REFRESH, url)] if url is not None else [])
                continue
            else:
                continue
            self.urls.extend((line, f"the HTML {k} attribute", u) for u in values)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def html_urls(fragment, line):
    """(line, way read, value) of each URL in 1 raw HTML fragment starting on line."""
    p = IndexHTML()
    p.feed(fragment)
    p.close()
    return [(line + at - 1, how, value) for at, how, value in p.urls]


def may_name_draft(text):
    """False only when no URL read from text can have the draft path: its normalization (a line
    still changing counts as may) with every tab, LF and CR deleted holds no `draft`. Every step
    that builds a URL's path (character references, percent-decoding, NFKC, case folding, tab,
    LF and CR deletion) is one that normalization applies too; the rest only cut characters."""
    norm = normalized(text)
    return norm is None or "draft" in deleted(norm).replace("\n", "")


def first_word(text):
    """The first word of text after any whitespace and blockquote markers."""
    return re.match(r"[\s>]*(\S*)", text).group(1)


def markdown_urls(text):
    """(line, way read, value) of each Markdown and raw HTML URL of llms-full.txt (forms a and b
    of PART 3), parsed by the pinned markdown-it-py."""
    from markdown_it import MarkdownIt
    from markdown_it.rules_block.reference import reference

    md = MarkdownIt("commonmark")
    # Each destination as written (entities and escapes decoded), not percent-encoded, and the
    # last one the reference rule read.
    destinations = []

    def as_written(url):
        destinations.append(url)
        return url

    md.normalizeLink = as_written
    # `\r\n` read as `\n` and a lone `\r` deleted, so the parse's lines are the lines PART 3 counts.
    source = text.replace("\r\n", "\n").replace("\r", "")
    lines = source.split("\n")
    urls = []

    def definition(state, start, end, silent):
        destinations.clear()
        found = reference(state, start, end, silent)
        if not found or silent or not destinations:
            return found
        # The definition's own lines, its first from its `[`, the rest without blockquote markers
        # or indentation; it is reported on the line its label closes.
        body = [lines[start][lines[start].index("["):]]
        body += [re.sub(r"^[\s>]*", "", lines[i]) for i in range(start + 1, state.line)]
        written = "\n".join(body)
        pos, close = 1, len(written)
        while pos < len(written):
            if written[pos] == "\\":
                pos += 2
                continue
            if written[pos] == "]":
                close = pos
                break
            pos += 1
        line = start + 1 + written.count("\n", 0, close)
        urls.append((line, MD_DEFINITION, destinations[-1]))
        # An unbracketed destination ending its line is read joined to the next line's first word.
        rest = re.match(r"\]:\s*", written[close:])
        if rest:
            after = written[close + rest.end():]
            dest = re.match(r"[^\s<][^\s]*", after)
            dest_line = start + written.count("\n", 0, close + rest.end())
            if dest and dest.end() == len(after.split("\n", 1)[0]) and dest_line + 1 < len(lines):
                word = first_word(lines[dest_line + 1])
                if word:
                    urls.append((line, MD_JOINED, dest.group(0) + word))
        return True

    md.block.ruler.at("reference", definition)
    # The block structure of the whole file; the inline rules run only on a block that may hold
    # the draft path (may_name_draft), since the corpus is some 9 MB.
    md.disable("inline")
    env = {}
    tokens = md.parse(source, env)
    for token in tokens:
        if token.type == "html_block" and token.map and may_name_draft(token.content):
            urls.extend(html_urls(token.content, token.map[0] + 1))
        if token.type != "inline" or not token.map or not may_name_draft(token.content):
            continue
        children = []
        md.inline.parse(token.content, md, env, children)
        line = token.map[0] + 1
        for child in children:
            if child.type == "link_open":
                how = MD_AUTOLINK if child.markup == "autolink" else MD_LINK
                urls.append((line, how, child.attrGet("href") or ""))
            elif child.type == "image":
                urls.append((line, MD_IMAGE, child.attrGet("src") or ""))
            elif child.type == "html_inline":
                urls.extend(html_urls(child.content, line))
                line += child.content.count("\n")
            elif child.type in ("softbreak", "hardbreak"):
                line += 1
    return urls


def bare_readings(word):
    """The URLs a bare word of a normalized line is read as (form c of PART 3), none for prose."""
    word = word.rstrip(".,;:!?")
    m = SCHEME.match(word)
    if m:
        if m.group(1).lower() in SPECIAL:
            return [word]
        rest = word[m.end():]
        return [rest] if "/" in rest else []
    if HOST_START.match(word):
        return ["http://" + word]
    return [word] if "/" in word else []


def bare_urls(normalized_lines):
    """(line, way read, value) of each bare URL or path (form c of PART 3)."""
    urls = []
    for n, line in enumerate(normalized_lines, 1):
        # A line is already normalized, so a word's path can only hold what the line holds.
        if "draft" not in deleted(line).replace("\n", ""):
            continue
        for word in WORD_BREAK.split(line):
            pieces = {deleted(word).replace("\n", ""), *INSIDE_BREAK.split(word)}
            urls.extend((n, BARE, url) for piece in sorted(pieces) for url in bare_readings(piece))
    return urls


def index_findings(name, text):
    """The PART 3 findings for 1 published index under site/, each naming the file and line."""
    findings = []
    kept = []
    rounds = (f"a line still changing after {DECODE_ROUNDS} rounds of percent-decoding and "
              f"character-reference decoding")
    # Lines end at `\n` only. No normalization step reads across a `\n`, so normalizing each piece
    # and joining them with `\n` gives the whole text's normalization.
    for n, line in enumerate(text.split("\n"), 1):
        line = normalized(line)
        if line is None:
            findings.append(f"{SITE}/{name}:{n}: the published-index rule refuses {rounds}; the "
                            f"/draft/ review page stays out of every published index")
            line = ""
        kept.append(line)
    if name in STRICT_INDEXES:
        # The literal word, read on the joined text with tabs and CRs deleted, reported on the
        # original line it starts on.
        norm = [deleted(line) for line in kept]
        starts, at = [], 0
        for line in norm:
            starts.append(at)
            at += len(line) + 1
        joined = "\n".join(norm)
        excerpts = {}
        for m in DRAFT_WORD.finditer(joined):
            excerpts.setdefault(bisect_right(starts, m.start()),
                                joined[max(0, m.start() - 20):m.end() + 20])
        for n, excerpt in sorted(excerpts.items()):
            findings.append(f"{SITE}/{name}:{n}: the published-index rule refuses {excerpt!r} "
                            f"(this hand-written index never carries the word draft); the /draft/ "
                            f"review page stays out of every published index")
        return findings
    # The guide corpus: each URL read as Markdown, as raw HTML or as a bare word, resolved.
    seen = set()
    for n, how, value in sorted(set(markdown_urls(text) + bare_urls(kept))):
        verdict = refuses(value)
        if verdict is False or (n, how) in seen:
            continue
        seen.add((n, how))
        what = f"{value!r} ({how})" if verdict else f"{value!r} ({how}), whose path is {rounds}"
        findings.append(f"{SITE}/{name}:{n}: the published-index rule refuses {what}; the "
                        f"/draft/ review page stays out of every published index")
    return findings


def own_url(page_rel):
    """A page's own canonical URL: the origin plus its root path (a folder's index.html is the
    folder)."""
    if page_rel == "index.html" or page_rel.endswith("/index.html"):
        page_rel = page_rel[:-len("index.html")]
    return f"https://{SITE_HOST}/{page_rel}"


def check_url(root, value):
    """None when the value is allowed on a page, else the reason it is not."""
    if BAD_URL_CHARS.search(value):
        return ("carries whitespace, a control character or a backslash, which a browser strips "
                "or reads as a slash")
    if value.startswith("#"):
        return None
    parts = urlsplit(value)
    if parts.scheme:
        if parts.scheme.lower() not in ("http", "https"):
            return f"uses the {parts.scheme}: scheme"
        if not AUTHORITY.match(value):
            return ("has no host right after //, a form a browser normalizes onto another host "
                    "(`https:///secureconfig.ai/` opens secureconfig.ai)")
        host = unquote(parts.hostname or "")
        if not host.isascii():
            return ("has a host that is not plain ASCII, which a browser maps onto another host "
                    "(`secureconfig。ai` and fullwidth letters open secureconfig.ai)")
        if site_host(host):
            return ("is an absolute URL on this site's own host; a same-site link is written "
                    "root-relative, so what is checked is the file that is served")
        return None
    if value.startswith("//"):
        return "is a scheme-relative URL"
    if not value.startswith("/"):
        return "is a relative path; the pages use root-relative paths"
    if not resolves(root, value):
        return "names no file under site/"
    return None


def css_unescape(text):
    return CSS_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)) if m.group(1) else m.group(2), text)


def check(root):
    findings = []
    pages = page_files(root / SITE)
    if not pages:
        findings.append(f"{SITE} holds no pages")
    for page in pages:
        rel = page.relative_to(root)
        page_rel = page.relative_to(root / SITE).as_posix()
        parsed = parse(page.read_text(encoding="utf-8"))
        robots = [" ".join(c.lower().replace(",", " , ").split()) for _, c in parsed.robots]
        if page_rel in NOINDEX_PAGES:
            if robots != ["noindex , nofollow"]:
                findings.append(f"{rel} must carry exactly 1 robots meta element with content "
                                f"'noindex, nofollow'; it carries {[c for _, c in parsed.robots]!r}")
        elif parsed.robots:
            findings.append(f"{rel} carries a robots meta element "
                            f"({[c for _, c in parsed.robots]!r}); only the /draft/ review page "
                            f"and the 404 page are noindex, and every other page carries none")
        for line in parsed.http_equiv:
            findings.append(f"{rel}:{line}: carries http-equiv, which can refresh or redirect the "
                            f"page without a link; the pages carry none")
        for line, name, value in parsed.urls:
            why = check_url(root, value)
            if why:
                findings.append(f"{rel}:{line}: {name}={value!r} {why}")
        # A canonical is this page's own absolute URL, byte for byte: exactly 1 on each indexable
        # page and on the review page (https://secureconfig.ai/draft/), none on the 404, and at
        # most its own on any other page.
        expected = own_url(page_rel)
        if page_rel == NOTFOUND:
            for line, value in parsed.canonicals:
                findings.append(f"{rel}:{line}: carries the canonical {value!r}; the 404 page "
                                f"carries none")
        else:
            required = page_rel in INDEXABLE or page_rel == REVIEW_PAGE
            if (required and len(parsed.canonicals) != 1) or len(parsed.canonicals) > 1:
                findings.append(f"{rel} must carry exactly 1 canonical, {expected!r}; it carries "
                                f"{[v for _, v in parsed.canonicals]!r}")
            for line, value in parsed.canonicals:
                if value != expected:
                    findings.append(f"{rel}:{line}: the canonical {value!r} is not this page's "
                                    f"own URL {expected!r}")
        # The owner's template note of 2026-11-03: Disclosure and Licence are linked from the landing
        # page's "About this project" region and from each other, and from no other page; and no
        # page links the /draft/ review page. Both compare the file a root-relative URL resolves to.
        site = (root / SITE).resolve()
        review = site / REVIEW_PAGE
        about = {site / p for p in ABOUT_TARGETS}
        for line, name, value in parsed.urls:
            if not value.startswith("/") or value.startswith("//") or BAD_URL_CHARS.search(value):
                continue
            target = resolved(root, value)
            if page_rel not in ABOUT_PAGES and target in about:
                findings.append(f"{rel}:{line}: links {value}; only the landing page, the "
                                f"Disclosure page and the Licence page link those 2 pages")
            if target == review and page_rel != REVIEW_PAGE:
                findings.append(f"{rel}:{line}: links {value}; no page links the /draft/ review "
                                f"page, which is reached only by its URL")
        for line, label in parsed.newtab:
            if NEWTAB not in label:
                findings.append(f"{rel}:{line}: a link that opens a new tab does not say so "
                                f"with a hidden {NEWTAB!r}")
    if (root / "site" / "_redirects").exists():
        findings.append("site/_redirects exists; a missing path gets the 404 page with status 404, "
                        "never a redirect (the owner's rule)")
    # PART 3: the published indexes do not refer to the /draft/ review page (fail-closed).
    for name in (*STRICT_INDEXES, CORPUS_INDEX):
        path = root / SITE / name
        if path.is_file():
            findings.extend(index_findings(name, path.read_bytes().decode("utf-8")))
    assets = (root / SITE / "assets").resolve()
    css_files = sorted(p for p in (root / SITE).rglob("*") if p.is_file() and name_suffix(p.name) == ".css")
    for css in css_files:
        rel = css.relative_to(root)
        text = CSS_COMMENT.sub(" ", css.read_text(encoding="utf-8"))
        for m in AT_KEYWORD.finditer(text):
            if css_unescape(m.group(1)).lower() == "import":
                findings.append(f"{rel}: carries @import, which loads another stylesheet the "
                                f"site's checks do not read")
        for m in URL_FN.finditer(text):
            ref = m.group(2).strip()
            parts = urlsplit(ref)
            target = (css.parent / unquote(parts.path)).resolve()
            if parts.scheme or ref.startswith("/") or "\\" in ref or not target.is_file():
                findings.append(f"{rel}: url({ref}) is not a relative path to a file in the site")
                continue
            try:
                target.relative_to(assets)
            except ValueError:
                findings.append(f"{rel}: url({ref}) resolves outside {SITE}/assets/")
    site_css = root / SITE / "assets" / "site.css"
    if site_css.is_file():
        body = CSS_COMMENT.sub(" ", site_css.read_text(encoding="utf-8"))
        if not SITE_CSS.fullmatch(body):
            findings.append(f"{SITE}/assets/site.css may hold only rules (at the top level or in "
                            f"@media (prefers-color-scheme: dark|light)) that set --sw or "
                            f"--logo-inset to a number")
    return findings, len(pages)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    try:
        findings, n = check(args.root)
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot read the site: {exc}")
        return 2
    except ImportError as exc:
        print(f"  FAIL  cannot import the pinned markdown-it-py (tools/requirements-gates.txt): {exc}")
        return 2
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {n} pages are self-contained (every root-relative link names a file under "
          f"site/, external links leave by http(s) on another host with the new-tab hint), only "
          f"the /draft/ review page and the 404 page carry a robots noindex, each canonical is "
          f"its page's own URL, no page or published index names /draft/, and there is no "
          f"_redirects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
