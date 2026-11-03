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

PART 3, THE PUBLISHED INDEXES (site/llms.txt, site/llms-full.txt, site/robots.txt):
  - none of them names the /draft/ path. Each file is cut into tokens at whitespace and at the
    characters ( ) [ ] < > " ' and the backtick, so a Markdown link or an autolink yields its URL.
    Only 2 kinds of token are read, and every other token is prose and accepted (the word "draft",
    "Draft review" or "draft-ietf-..." in the guide corpus is never refused):
      * a URL token: it starts with `http://` or `https://` in any case and its host, after
        percent-decoding, NFKC folding, U+3002 and U+FF61 read as `.`, case folding and a
        trailing `.` removed, is this site's host or a Pages alias (site_host() below); a URL on
        another host is accepted whatever its path;
      * a path token: it starts with `/` (so `//host/draft/` is read as a path too).
    Of a URL token its path is read, of a path token the whole token; the query and fragment are
    cut and trailing `. , ; : ! ?` removed. The text is then percent-decoded repeatedly (up to 8
    rounds), and at every round, with backslashes read as `/` and case folded, it is split at `/`;
    a segment equal to `draft` refuses the token. So `/draft/`, `/Draft/`, `/%64raft/`,
    `/guides/../draft/`, `Disallow: /draft` and `https://secureconfig.ai/draft` are refused, while
    `/drafts/`, `/draft.html` and `https://example.net/draft/` are not.

Exit 0 ok, 1 on a finding, 2 on a read error.
Usage: python3 -I -B tools/check_draft.py [--root <repository root>]
"""
import argparse
import re
import sys
import unicodedata
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
# The published indexes that must not name the /draft/ path (PART 3).
INDEXES = ("llms.txt", "llms-full.txt", "robots.txt")
INDEX_TOKEN_SPLIT = re.compile(r"[\s()\[\]<>\"'`]+")
INDEX_URL = re.compile(r"(?i)^https?://")
DECODE_ROUNDS = 8
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


def names_draft(token):
    """True when an index token (PART 3) is a URL on this site, or a path, naming the /draft/
    segment after percent-decoding and case folding."""
    if INDEX_URL.match(token):
        parts = urlsplit(token)
        host = unicodedata.normalize("NFKC", unquote(parts.netloc.rsplit("@", 1)[-1]))
        host = host.replace("。", ".").replace("｡", ".").split(":", 1)[0]
        if not parts.netloc:
            # `https:///secureconfig.ai/draft/`: no host after //, which a browser opens on the
            # host that follows, so the whole remainder is read as a path.
            text = token.split(":", 1)[1]
        elif not site_host(host.casefold()):
            return False
        else:
            text = parts.path
    elif token.startswith("/"):
        text = token
    else:
        return False
    text = text.split("#", 1)[0].split("?", 1)[0].rstrip(".,;:!?")
    for _ in range(DECODE_ROUNDS):
        if "draft" in text.replace("\\", "/").casefold().split("/"):
            return True
        decoded = unquote(text)
        if decoded == text:
            return False
        text = decoded
    return "draft" in text.replace("\\", "/").casefold().split("/")


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
    # PART 3: the published indexes do not name the /draft/ path.
    for name in INDEXES:
        path = root / SITE / name
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for token in INDEX_TOKEN_SPLIT.split(line):
                if token and names_draft(token):
                    findings.append(f"{SITE}/{name}:{n}: names the /draft/ path ({token!r}); the "
                                    f"review page stays out of every published index")
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
          f"the /draft/ review page and the 404 page carry a robots noindex, each canonical is "
          f"its page's own URL, no page or published index names /draft/, and there is no "
          f"_redirects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
