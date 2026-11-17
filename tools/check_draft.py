#!/usr/bin/env python3
"""Check that the site is self-contained, only the 404 page, the unlisted advisory and the quality
matrix page are noindex, and no /draft/ exists.

WHY: since promotion (baseline SPECIFICATION section 4.1 item 5) the generated pages are served
from the site root. A root-relative link that names no file ships a broken page; an absolute URL
on this site's own host bypasses that check and can pin a scheme or an alias this gate cannot
read; a stray robots meta on an indexable page, or a lost one on the 404 page, silently changes
what search engines index. From baseline 1.11.0 (SPECIFICATION section 4.1 items 0 and 3) a
draft for review is built on the `draft` branch and reviewed at
https://draft.secureconfig.pages.dev/draft/; the production branch (`main`) carries no /draft/
page, and no live page or published index refers to one (item 2). Nothing else in the suite
checks any of that. On the `draft` branch this gate meets the staged tree under site/draft/ and
refuses it, so that branch, as item 3 requires, either covers the draft under the template's
rules or excludes /draft/ explicitly, and removes the exclusion at promotion. The sitemap gates
import BASE and DRAFT below, and BASE = "/" switches their staged-draft rules off;
tools/check_sitemap.py refuses a /draft/ `loc` by its first segment at any base.

A PAGE is any file under site/ named .html or .htm in any case, read by the CSP gate's own suffix
rule (check_csp_hashes.name_suffix), so a page the CSP gate checks is a page this gate checks too.

PART 1, INDEXABILITY AND NO DRAFT TREE:
  - site/404.html and site/advisories/n8n-2026-11-07-jposluns.html (NOINDEX_PAGES) each carry
    exactly 1 robots meta element, read by html.parser (so a commented-out one does not count,
    attribute case and quoting do not matter, and of duplicate attributes the first counts, as in a
    browser), whose content is `noindex, nofollow` (case and spacing aside).
    advisories/n8n-2026-11-07-jposluns.html (ADVISORY) is the one unlisted advisory the maintainer
    keeps out of search, reachable only by its URL and linked from no page; it is admitted by that
    exact path, and any OTHER noindex page, the old advisories/n8n.html included, is still refused.
    Its plain-text copy, advisories/n8n-2026-11-07-jposluns.txt, is not a page, so this gate does
    not read it; quality/index.html (QUALITY) is the GQS 1.0 compliance matrix, kept out of search
    by the GQS-ADOPT decision and admitted by that exact path like the advisory;
  - every other page carries NO robots meta element at all: the generated pages are indexable and
    carry none, so one appearing is an edit this gate refuses rather than guesses about;
  - site/ holds no entry named `draft` in any case (a folder, with any file in it, or a file): the
    live site carries no /draft/ tree (SPECIFICATION section 4.1 items 0 and 3). Any case is
    refused, as a case-insensitive file system or server could serve `Draft/` at /draft/;
  - site/_redirects, when present, holds only the fixed generator header (its first line), the
    entries of tools/redirects_allowlist.txt and, written only once a release record exists, the
    two latest links as the last 2 lines. Those are /downloads/secureconfig-latest.zip then
    /downloads/secureconfig-plugin-latest.zip, each `SOURCE TARGET 302` with single spaces and
    both targets one version's zips staged in site/downloads/. Every other line is refused, so a
    missing path still returns the 404 page with status 404. An allowlist entry is
    `SOURCE TARGET 302<TAB>REASON` with a non-empty reason. Every root-relative source and
    target is read in a normal form first: it is percent-decoded until it stops changing (at
    most DECODE_ROUNDS rounds). A field is refused when the decoding does not settle, when it
    decodes to whitespace, a control character or a backslash, when it carries a `.`, `..` or
    empty segment, when it carries a `*`, `:`, `?` or `#` (FIELD_MARKS), or when it starts
    `//` (scheme-relative). A host can read `*` as a splat and `:` as a placeholder, each
    matching more than one path, and `?` and `#` as a query or fragment the rules below would
    not read, and a browser folds the other refused forms onto a URL the rules below would not
    read, so a gated field is one exact literal path. A source with a trailing slash is
    refused too: whether a host folds `/x/` and `/x` onto one request is not verified here, so
    a gated source has no second spelling. A target is such a normal root-relative path naming a
    file under site/ that lies outside /downloads/, has no `.zip` name in any case, and whose
    bytes carry none of the archive signatures this gate reads (ARCHIVE_MAGICS at the start, or
    a tar magic at TAR_MAGIC_OFFSET), or an aged-out versioned zip's own GitHub release asset
    URL reached from /downloads/<zip>; any other absolute URL is refused. An entry's source
    never names a file under site/ by its exact path, an `.html`, `.htm`, `/index.html` or
    `/index.htm` completion, or another case, staged archives included: whether the server
    would answer with the redirect or the file is not verified here, so a source that reads as
    a staged file in any of those spellings is refused. A target under /downloads/ is refused
    because a staged archive is reached by its own URL or the generated latest links, never
    through a gated redirect. A `.zip`-named or archive-signed target elsewhere under site/ is
    refused because the release record vouches for no archive outside /downloads/.
    tools/check_hosted.py also holds each release-asset entry to the release record (a
    recorded zip that is no longer staged) and refuses any file under site/downloads/ that no
    record names. The literal 302 is required
    everywhere: a latest link answers 302, never 301, and so does every gated redirect. No
    source or target in the file or the allowlist names /draft/ in any case, percent-encoding
    or dot-segment spelling, and no file under site/ has a `-latest.zip` name, since a latest
    link is a 302 redirect with no bytes of its own. tools/check_hosted.py holds the file to
    the generator's output; tools/check_csp_hashes.py holds site/_headers, X-Robots-Tag
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
    each of the 7 indexable pages (INDEXABLE below) carries exactly 1, equal byte for byte to
    `https://secureconfig.ai` plus that page's own root path (`/`, `/guides/`, ...,
    `/license/`); the 404 page and the unlisted site/advisories/n8n-2026-11-07-jposluns.html
    (NO_CANONICAL_PAGES, by exact path) carry none, not even their own; any other page carries at
    most its own;
  - any `http-equiv` attribute is refused (a refresh would navigate away without a link);
  - every link that opens a new tab carries the visually hidden "(opens in a new tab)";
  - only the landing page, the Disclosure page and the Licence page link the Disclosure and Licence
    pages (the owner's template note of 2026-11-03: they left the top bar), and no page links
    /draft/ (SPECIFICATION section 4.1 item 2). Both rules compare the FILE a root-relative URL
    resolves to, read as resolves() reads it (query and fragment cut, percent-decoded, dot
    segments resolved, a folder naming its index.html), with site/disclosure/index.html,
    site/license/index.html and anything under site/draft/ (first segment in any case), so
    `/draft/?x`, `/draft//`, `/guides/../draft/`, `/%64raft/` and `/draft/index.html#a` are each a
    link to /draft/. With no draft tree such a link names no file, which the rule above refuses;
    with a tree present, this rule names the link beside PART 1's draft-tree finding;
  - no stylesheet under site/ carries `@import` in any spelling (CSS escapes decoded), every
    `url(` in one is relative and resolves to a file inside site/assets/, and a site/assets/site.css,
    where one exists (scripts/build-site.py --check allows that 1 file beside the pages and the
    copied files), matches the whole permitted grammar: rules (at the top level or inside
    `@media (prefers-color-scheme: dark|light)`) whose only declarations set `--sw` or
    `--logo-inset` to a number (baseline README, "Per-site constants").

PART 3, THE PUBLISHED INDEXES (site/llms.txt, site/llms-full.txt, site/robots.txt and
site/.well-known/security.txt): none of them refers to /draft/. The rule is
fail-closed and parses no URL, since 2 rounds of URL parsing each missed spellings:
  - the whole file text is normalized: the round { percent-decode; `html.unescape` } repeats until
    the text stops changing, at most 8 rounds (text still changing in a 9th round is refused);
    then Unicode NFKC, case folding and every `\\` read as `/`. That gives the KEPT text, and the
    kept text with every ASCII tab and CR deleted gives the DELETED text (a browser deletes both
    from a URL; the `\\n`s stay). Each text is normalized piece by piece between its `\\n`s and
    the pieces joined with `\\n` again, which is the same text, as no step reads across a `\\n`;
    so a match maps to the original line it starts on;
  - site/llms.txt, site/robots.txt and site/.well-known/security.txt are hand-written indexes that
    never need the word, so any literal `draft` anywhere in their deleted text is refused (deleting
    only joins characters, so the deleted text holds every `draft` the kept text holds);
  - site/llms-full.txt, the generated guide corpus, uses "draft" in prose and in `draft-ietf-...`
    names, so there each match of any of these, on the kept text and on the deleted text, is
    refused, and a line matched in either is reported once (each read across a line end too, as a
    Markdown link may break there). The kept text keeps a tab or CR that alone separates a word
    from the path, which deleting would join to it; the deleted text joins a path a tab or CR
    splits:
      a. `/draft(?![a-z0-9_-])`;
      b. `(?<![a-z0-9_-])draft/`;
      c. a Markdown link destination whose first segment is `draft`, with any whitespace, line
         ends and blockquote `>` markers before it or its `<`:
         `\\]\\([\\s>]*<?[\\s>]*(?:\\./)*draft(?![a-z0-9_-])`;
      d. a reference definition, with no line-start anchor, so its label may span lines and it
         may sit in a blockquote or a list item, and with any whitespace, line ends and
         blockquote `>` markers before its destination or its `<`, so the destination may be on
         the next line: `\\]:[\\s>]*<?[\\s>]*(?:\\./)*draft(?![a-z0-9_-])`;
      e. an HTML attribute value:
         `\\b(?:href|src|action|formaction|content|url)\\s*=\\s*["']?\\s*(?:\\./)*draft(?![a-z0-9_-])`.
    So `/draft/`, `./draft/`, `[x](draft)`, `[x](<draft>)`, `[x](draft#top)`, `[x]: draft`,
    `> [x]: draft`, `- [x]: draft`, `href="draft"`, `secureconfig.ai/draft/`, `%2Fdraft%2F`,
    `/&#100;raft/`, `/dr&#9;aft/`, `/dr&#13;aft/`, a raw CR inside `/draft/`, a tab alone between
    `/draft` and "for", between "see" and `draft/`, and between `<a` and `href="draft"`,
    `\\draft\\` and `/draft.html` are refused, while "drafting", "drafted", "a draft.",
    "the draft's", "draft / final", "and Raft", "draft-ietf-oauth-v2-1" and
    `https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/` are accepted.
  Each finding names the file and the line, counting `\\n` only (a U+2028 or a `\\r` ends no line),
  and the file is read without newline translation.

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
# The published base path and the draft tree the `draft` branch stages, imported by
# tools/check_sitemap.py and tools/check_sitemap_lastmod.py. At "/" their staged-draft rules
# switch off. This gate refuses any site/ entry named DRAFT_NAME, in any case (PART 1).
BASE = "/"
DRAFT = Path("site") / "draft"
DRAFT_NAME = "draft"
SITE_HOST = "secureconfig.ai"
# site/_redirects (PART 1): the generator's header, the gated allowlist and the two latest links.
# tools/gen_hosted.py writes the file whole; tools/test_hosted.py holds REDIRECTS_HEADER to the
# generator's own copy of the line, so the two spellings cannot drift apart.
REDIRECTS = Path("site") / "_redirects"
REDIRECTS_ALLOWLIST = Path("tools") / "redirects_allowlist.txt"
REDIRECTS_HEADER = ("# Generated by tools/gen_hosted.py from releases/ and "
                    "tools/redirects_allowlist.txt; do not edit by hand.")
LATEST_SUFFIX = "-latest.zip"
# Each latest link's source and the target shape of its kind, with the version captured.
LATEST_RULES = (
    ("/downloads/secureconfig-latest.zip",
     re.compile(r"/downloads/secureconfig-(1\.0\.[1-9][0-9]*)\.zip")),
    ("/downloads/secureconfig-plugin-latest.zip",
     re.compile(r"/downloads/secureconfig-plugin-(1\.0\.[1-9][0-9]*)\.zip")),
)
LATEST_SOURCES = tuple(source for source, _ in LATEST_RULES)
DOWNLOADS_NAME = "downloads"
ALLOW_ENTRY = re.compile(r"(/\S+) (\S+) 302")
# An aged-out zip's redirect target: that release's own GitHub asset, same version and name.
ASSET_TARGET = re.compile(r"https://github\.com/jposluns/secureconfig/releases/download/"
                          r"v(1\.0\.[1-9][0-9]*)/(secureconfig(?:-plugin)?-\1\.zip)")
NEWTAB = "(opens in a new tab)"
URL_FN = re.compile(r"url\(\s*(['\"]?)([^'\")]*)\1\s*\)", re.I)
# The pages that may link /disclosure/ and /license/ (the owner's template note of 2026-11-03).
ABOUT_PAGES = {"index.html", "disclosure/index.html", "license/index.html"}
# The files those 2 rules protect, compared after resolution (see resolved()).
ABOUT_TARGETS = ("disclosure/index.html", "license/index.html")
# The 7 indexable pages, each carrying exactly 1 canonical: the origin plus its own root path.
INDEXABLE = ("index.html", "guides/index.html", "for-ai/index.html", "for-humans/index.html",
             "checklist/index.html", "disclosure/index.html", "license/index.html")
NOTFOUND = "404.html"
# The one unlisted advisory page (the maintainer's instruction of 2026-11-07 gave it this dated
# name), as scripts/build-site.py ADVISORY_PAGE writes it.
ADVISORY = "advisories/n8n-2026-11-07-jposluns.html"
# The GQS 1.0 compliance matrix page, noindex by the GQS-ADOPT decision, as scripts/build-site.py
# writes it; kept out of search, in no menu or sitemap, and reachable by its URL.
QUALITY = "quality/index.html"
# The pages that carry NO canonical, not even their own URL, by exact path, with the name a finding
# gives each: the 404 page, the unlisted advisory and the quality matrix page, each kept out of
# search and not naming its URL as one to index. Any other page carries at most its own canonical.
NO_CANONICAL_PAGES = {NOTFOUND: "the 404 page",
                      ADVISORY: "the unlisted advisory page",
                      QUALITY: "the quality matrix page"}
# The published indexes (PART 3): the hand-written ones refuse the word, the guide corpus refuses
# each form of the draft path, both read after normalized().
STRICT_INDEXES = ("llms.txt", "robots.txt", ".well-known/security.txt")
CORPUS_INDEX = "llms-full.txt"
DRAFT_WORD = re.compile(r"draft")
# The corpus forms a to e of the docstring, each matched on its own.
DRAFT_REFS = (
    re.compile(r"/draft(?![a-z0-9_-])"),
    re.compile(r"(?<![a-z0-9_-])draft/"),
    re.compile(r"\]\([\s>]*<?[\s>]*(?:\./)*draft(?![a-z0-9_-])"),
    re.compile(r"\]:[\s>]*<?[\s>]*(?:\./)*draft(?![a-z0-9_-])"),
    re.compile(r"""\b(?:href|src|action|formaction|content|url)\s*=\s*["']?\s*(?:\./)*draft(?![a-z0-9_-])"""),
)
DECODE_ROUNDS = 8
# A redirect field is one exact literal path, so each of these marks is refused in a decoded
# root-relative field: a host can read `*` as a splat and `:` as a placeholder, each matching
# more than one path, and `?` and `#` as a query or fragment the redirect rules would not read.
FIELD_MARKS = "*:?#"
# The archive signatures the target rule reads by content: the zip local-file, empty and
# spanned headers, gzip, bzip2, xz, zstd, 7z and rar at offset 0, and the two ustar magics of a
# tar header at offset TAR_MAGIC_OFFSET.
ARCHIVE_MAGICS = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08", b"\x1f\x8b", b"BZh",
                  b"\xfd7zXZ\x00", b"\x28\xb5\x2f\xfd", b"7z\xbc\xaf\x27\x1c", b"Rar!\x1a\x07")
TAR_MAGIC_OFFSET = 257
TAR_MAGICS = (b"ustar\x00", b"ustar ")
# The pages that carry a robots meta, each exactly 'noindex, nofollow', and what every other page
# must not carry at all. The 404 page is the not-found page; ADVISORY is the one unlisted
# advisory the maintainer keeps out of search (reachable only by its URL, linked from no page, and
# absent from every index); QUALITY is the compliance matrix page, noindex by the GQS-ADOPT
# decision. Any OTHER noindex page is still refused, by exact path.
NOINDEX_PAGES = {NOTFOUND, ADVISORY, QUALITY}
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


def in_draft(rel):
    """True when a path relative to site/ lies in the draft tree: its first segment, in any case,
    is DRAFT_NAME."""
    return bool(rel.parts) and rel.parts[0].casefold() == DRAFT_NAME


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
    """The kept text with every tab and CR deleted (a browser deletes them from a URL)."""
    return text.replace("\t", "").replace("\r", "")


def index_findings(name, text):
    """The PART 3 findings for 1 published index under site/, each naming the file and line."""
    findings = []
    kept = []
    # Lines end at `\n` only. No normalization step reads across a `\n`, so normalizing each piece
    # and joining them with `\n` gives the whole text's normalization.
    for n, line in enumerate(text.split("\n"), 1):
        line = normalized(line)
        if line is None:
            findings.append(f"{SITE}/{name}:{n}: the published-index rule refuses a line still "
                            f"changing after {DECODE_ROUNDS} rounds of percent-decoding and "
                            f"character-reference decoding; no published index refers to /draft/")
            line = ""
        kept.append(line)
    # The literal word is read on the deleted text only, which holds every `draft` the kept text
    # holds; the corpus forms on both, as deleting a tab or CR may join a word to the path.
    if name in STRICT_INDEXES:
        texts = ([deleted(line) for line in kept],)
        patterns, why = (DRAFT_WORD,), "this hand-written index never carries the word draft"
    else:
        texts = (kept, [deleted(line) for line in kept])
        patterns, why = DRAFT_REFS, "a reference to the draft path"
    # Matched on the joined text, so a Markdown link broken across a line end is still read; a
    # match is reported on the original line it starts on, once whichever text it is found in.
    excerpts = {}
    for norm in texts:
        starts, at = [], 0
        for line in norm:
            starts.append(at)
            at += len(line) + 1
        joined = "\n".join(norm)
        for start, end in sorted((m.start(), m.end()) for p in patterns for m in p.finditer(joined)):
            excerpts.setdefault(bisect_right(starts, start), joined[max(0, start - 20):end + 20])
    for n, excerpt in sorted(excerpts.items()):
        findings.append(f"{SITE}/{name}:{n}: the published-index rule refuses {excerpt!r} ({why}); "
                        f"no published index refers to /draft/")
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


def clean_field(value):
    """(the normal form of a root-relative redirect field, None), or (None, why it is refused).
    The field is percent-decoded until it stops changing (at most DECODE_ROUNDS rounds). It is
    refused when the decoding does not settle, when it decodes to whitespace, a control
    character or a backslash, when it carries a `.`, `..` or empty segment, when it carries one
    of FIELD_MARKS (`*`, `:`, `?` or `#`), or when it is scheme-relative: a browser or a host
    reads each of those as more, or as other, than one exact literal path. Every rule then
    reads the normal form, the one path the entry is about."""
    if value.startswith("//"):
        return None, "is scheme-relative, which a browser reads as a URL on another host"
    for _ in range(DECODE_ROUNDS + 1):
        decoded = unquote(value)
        if decoded == value:
            break
        value = decoded
    else:
        return None, f"still changes after {DECODE_ROUNDS} rounds of percent-decoding"
    if BAD_URL_CHARS.search(value):
        return None, ("percent-decodes to whitespace, a control character or a backslash, "
                      "which a browser strips or reads as a slash")
    segments = value.split("/")[1:]
    if "." in segments or ".." in segments:
        return None, ("carries a `.` or `..` segment, which a browser folds onto another path "
                      "before requesting it")
    if "" in segments[:-1]:
        return None, "carries an empty segment, which can be read as another path"
    for mark in FIELD_MARKS:
        if mark in value:
            return None, (f"carries `{mark}`; a gated field is one exact literal path, and a "
                          f"host can read `*` as a splat, `:` as a placeholder, and `?` or `#` "
                          f"as a query or fragment, each matching or meaning more than that "
                          f"one path")
    return value, None


def source_forms(value):
    """The staged files a redirect source could be served as, relative to site/ and case folded:
    the path itself and its .html, .htm, /index.html and /index.htm completions, and, for the
    empty or trailing-slash folder form, that folder's index.html and index.htm."""
    rel = value.lstrip("/").casefold()
    if rel == "" or rel.endswith("/"):
        return (rel + "index.html", rel + "index.htm")
    return (rel, rel + ".html", rel + ".htm", rel + "/index.html", rel + "/index.htm")


def looks_like_archive(path):
    """True when the file's bytes open with one of ARCHIVE_MAGICS or carry a ustar magic at
    TAR_MAGIC_OFFSET: the archive forms this gate identifies by content, not by name."""
    with path.open("rb") as handle:
        head = handle.read(TAR_MAGIC_OFFSET + 6)
    return (head.startswith(ARCHIVE_MAGICS)
            or head[TAR_MAGIC_OFFSET:TAR_MAGIC_OFFSET + 6] in TAR_MAGICS)


def draft_path(value):
    """True when a redirect field names /draft/: a root-relative path whose first segment, in any
    case and percent-decoded, is DRAFT_NAME."""
    if not value.startswith("/"):
        return False
    return in_draft(Path(unquote(value.lstrip("/"))))


def downloads_path(value):
    """True when a redirect field lies under /downloads/: a root-relative path whose first
    segment, in any case and percent-decoded, is DOWNLOADS_NAME."""
    if not value.startswith("/"):
        return False
    parts = Path(unquote(value.lstrip("/"))).parts
    return bool(parts) and parts[0].casefold() == DOWNLOADS_NAME


def allowlist_entries(root):
    """(the valid rules of tools/redirects_allowlist.txt, the findings for the others). A missing
    file is an empty list, so site/_redirects then admits only the header and the latest links."""
    path = root / REDIRECTS_ALLOWLIST
    rules, findings = [], []
    if not path.is_file():
        return rules, findings
    # Every file under site/, case folded, for the source shadow rule below; the original
    # spelling is kept for the finding.
    staged = {}
    if (root / SITE).is_dir():
        for entry in sorted(p for p in (root / SITE).rglob("*") if p.is_file()):
            rel = entry.relative_to(root / SITE).as_posix()
            staged.setdefault(rel.casefold(), rel)
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        where = f"{REDIRECTS_ALLOWLIST}:{n}"
        rule, sep, reason = line.partition("\t")
        if not sep or not reason or reason != reason.strip():
            findings.append(f"{where}: an entry is `SOURCE TARGET 302<TAB>REASON` with a "
                            f"non-empty reason")
            continue
        matched = ALLOW_ENTRY.fullmatch(rule)
        if not matched:
            findings.append(f"{where}: the rule before the tab is `SOURCE TARGET 302` with "
                            f"single spaces, a root-relative source and the literal 302 (every "
                            f"redirect here answers 302, never 301)")
            continue
        source, target = matched.group(1), matched.group(2)
        problems = []
        # Each root-relative field is read in its normal form, so no rule below reads a path a
        # browser would fold onto another one.
        normal = {}
        for name, field in (("source", source), ("target", target)):
            if not field.startswith("/"):
                continue
            value, why = clean_field(field)
            if why is None:
                normal[name] = value
            else:
                problems.append(f"has a {name} that {why}; every root-relative source and "
                                f"target is read in the normal form a browser would request, "
                                f"so a field that does not normalize cleanly is refused")
        src, tgt = normal.get("source"), normal.get("target")
        if src is not None and src.endswith("/"):
            problems.append("has a source with a trailing slash; a gated source is one exact "
                            "literal path, and whether a host folds `/x/` and `/x` onto one "
                            "request is not verified here, so a second spelling of a path is "
                            "refused")
        if (src is not None and draft_path(src)) or (tgt is not None and draft_path(tgt)):
            problems.append("names /draft/; the live site carries no /draft/ tree and no "
                            "redirect, gated or generated, names it")
        if ((src is not None and src.lower().endswith(LATEST_SUFFIX))
                or (tgt is not None and tgt.lower().endswith(LATEST_SUFFIX))):
            problems.append("names a -latest file; the two latest links are generated, never "
                            "listed here")
        shadow = None
        if src is not None:
            shadow = next((staged[form] for form in source_forms(src) if form in staged), None)
        if shadow is not None:
            problems.append(f"has a source naming a file under site/ ({SITE}/{shadow}) by its "
                            f"exact path, an index, .html or .htm form, or another case; "
                            f"whether the server would answer with the redirect or the file is "
                            f"not verified, so no entry names a staged file's path in a "
                            f"spelling this gate reads")
        asset = ASSET_TARGET.fullmatch(target)
        if target.startswith("/"):
            if tgt is None:
                pass
            elif downloads_path(tgt):
                problems.append("has a target under /downloads/; a staged archive is reached by "
                                "its own URL or the generated latest links, never through a "
                                "gated redirect")
            else:
                file = resolved(root, tgt)
                if file is None or not file.is_file():
                    problems.append("has a target naming no file under site/")
                elif file.name.casefold().endswith(".zip") or looks_like_archive(file):
                    problems.append("has a target naming an archive under site/ (a `.zip` "
                                    "name, or bytes carrying a known archive signature); the "
                                    "release record vouches for no archive outside "
                                    "/downloads/")
        elif asset:
            if source != f"/downloads/{asset.group(2)}":
                problems.append("redirects a release asset from a source other than its own "
                                "/downloads/<zip> path")
        else:
            problems.append("has a target that is neither a root-relative path naming a file "
                            "under site/ nor an aged-out versioned zip's GitHub release asset "
                            "URL")
        for problem in problems:
            findings.append(f"{where}: {rule!r} {problem}")
        if not problems:
            rules.append(rule)
    return rules, findings


def redirect_findings(root):
    """The findings for site/_redirects (PART 1): the generator's header first, then only
    allowlisted rules, then, when present, exactly the two latest links as the last 2 lines, in
    the generator's order, each 302 and each naming a staged archive of one version."""
    rules, findings = allowlist_entries(root)
    path = root / REDIRECTS
    if not path.exists():
        return findings
    if not path.is_file():
        findings.append(f"{REDIRECTS} is not a regular file; tools/gen_hosted.py writes a plain "
                        f"text file")
        return findings
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        findings.append(f"{REDIRECTS} does not end with a newline")
        text += "\n"
    lines = text.split("\n")[:-1]
    if not lines or lines[0] != REDIRECTS_HEADER:
        findings.append(f"{REDIRECTS}:1: the first line is the generator's header; the file is "
                        f"written whole by tools/gen_hosted.py and never edited by hand")
    numbered = list(enumerate(lines[1:], 2))
    rest = numbered
    if any(line.split(" ", 1)[0] in LATEST_SOURCES for _, line in numbered):
        last = numbered[-2:]
        rest = numbered[:-2]
        if [line.split(" ", 1)[0] for _, line in last] != list(LATEST_SOURCES):
            findings.append(f"{REDIRECTS}: the latest links are exactly 2 lines, the last of "
                            f"the file, {LATEST_SOURCES[0]} then {LATEST_SOURCES[1]}; a lone, "
                            f"repeated, reordered or displaced latest link is refused")
            rest = [(n, line) for n, line in numbered
                    if line.split(" ", 1)[0] not in LATEST_SOURCES]
            last = []
        versions = []
        for (n, line), (source, target_re) in zip(last, LATEST_RULES):
            parts = line.split(" ")
            matched = target_re.fullmatch(parts[1]) if len(parts) == 3 else None
            if len(parts) != 3 or parts[2] != "302" or not matched:
                findings.append(f"{REDIRECTS}:{n}: {line!r} is not `{source} "
                                f"/downloads/<its versioned zip> 302`; the target is that "
                                f"link's own kind of zip and the status answers 302, never 301")
                continue
            versions.append(matched.group(1))
            if not (root / SITE / "downloads" / Path(parts[1]).name).is_file():
                findings.append(f"{REDIRECTS}:{n}: {line!r} names no staged archive; the "
                                f"records pull request copies the released zip into "
                                f"site/downloads/ byte for byte before a link points at it")
        if len(versions) == 2 and versions[0] != versions[1]:
            findings.append(f"{REDIRECTS}: the 2 latest links name 2 versions ({versions[0]} "
                            f"and {versions[1]}); both point at the current versioned archive")
    for n, line in rest:
        if line in rules:
            continue
        if any(draft_path(field) for field in line.split(" ")):
            findings.append(f"{REDIRECTS}:{n}: {line!r} names /draft/; the live site carries no "
                            f"/draft/ tree and no redirect names it")
            continue
        findings.append(f"{REDIRECTS}:{n}: {line!r} is not an allowlisted redirect; the file "
                        f"holds only the generator's header, the entries of "
                        f"{REDIRECTS_ALLOWLIST} and the 2 latest links")
    return findings


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
                            f"({[c for _, c in parsed.robots]!r}); only the 404 page and the "
                            f"unlisted {ADVISORY} are noindex, and every other page "
                            f"carries none")
        for line in parsed.http_equiv:
            findings.append(f"{rel}:{line}: carries http-equiv, which can refresh or redirect the "
                            f"page without a link; the pages carry none")
        for line, name, value in parsed.urls:
            why = check_url(root, value)
            if why:
                findings.append(f"{rel}:{line}: {name}={value!r} {why}")
        # A canonical is this page's own absolute URL, byte for byte: exactly 1 on each indexable
        # page, none on the 404 or the unlisted advisory (NO_CANONICAL_PAGES), and at most its own
        # on any other page.
        expected = own_url(page_rel)
        if page_rel in NO_CANONICAL_PAGES:
            for line, value in parsed.canonicals:
                findings.append(f"{rel}:{line}: carries the canonical {value!r}; "
                                f"{NO_CANONICAL_PAGES[page_rel]} carries none")
        else:
            required = page_rel in INDEXABLE
            if (required and len(parsed.canonicals) != 1) or len(parsed.canonicals) > 1:
                findings.append(f"{rel} must carry exactly 1 canonical, {expected!r}; it carries "
                                f"{[v for _, v in parsed.canonicals]!r}")
            for line, value in parsed.canonicals:
                if value != expected:
                    findings.append(f"{rel}:{line}: the canonical {value!r} is not this page's "
                                    f"own URL {expected!r}")
        # The owner's template note of 2026-11-03: Disclosure and Licence are linked from the landing
        # page's "About this project" region and from each other, and from no other page; and no
        # page links /draft/ (SPECIFICATION 4.1 item 2). Both compare the file a root-relative URL
        # resolves to.
        site = (root / SITE).resolve()
        about = {site / p for p in ABOUT_TARGETS}
        for line, name, value in parsed.urls:
            if not value.startswith("/") or value.startswith("//") or BAD_URL_CHARS.search(value):
                continue
            target = resolved(root, value)
            if page_rel not in ABOUT_PAGES and target in about:
                findings.append(f"{rel}:{line}: links {value}; only the landing page, the "
                                f"Disclosure page and the Licence page link those 2 pages")
            if target is not None and in_draft(target.relative_to(site)):
                findings.append(f"{rel}:{line}: links {value}; no live page links /draft/, which "
                                f"the live site does not carry")
        for line, label in parsed.newtab:
            if NEWTAB not in label:
                findings.append(f"{rel}:{line}: a link that opens a new tab does not say so "
                                f"with a hidden {NEWTAB!r}")
    # PART 1: the live site carries no /draft/ tree (SPECIFICATION 4.1 items 0 and 3).
    if (root / SITE).is_dir():
        for entry in sorted((root / SITE).iterdir()):
            if in_draft(Path(entry.name)):
                kind = "folder" if entry.is_dir() else "file"
                findings.append(f"{SITE}/{entry.name} exists ({kind}); the live site carries no "
                                f"/draft/ tree: a draft is built and reviewed on the `draft` branch "
                                f"at https://draft.secureconfig.pages.dev/draft/ (baseline "
                                f"SPECIFICATION section 4.1 items 0 and 3)")
    findings.extend(redirect_findings(root))
    if (root / SITE).is_dir():
        for entry in sorted(p for p in (root / SITE).rglob("*")
                            if p.is_file() and p.name.lower().endswith(LATEST_SUFFIX)):
            findings.append(f"{entry.relative_to(root)} has a latest name; a latest link is a "
                            f"302 redirect with no bytes of its own, so no file under site/ "
                            f"carries one")
    # PART 3: the published indexes do not refer to /draft/ (fail-closed).
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
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {n} pages are self-contained (every root-relative link names a file under "
          f"site/, external links leave by http(s) on another host with the new-tab hint), only "
          f"the 404 page and the unlisted {ADVISORY} carry a robots noindex and no "
          f"canonical, each other canonical is its page's own URL, site/ holds no draft tree or "
          f"-latest file, no page or published index names /draft/, and site/_redirects, when "
          f"present, holds only the generator's header, allowlisted redirects and the 2 latest "
          f"links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
