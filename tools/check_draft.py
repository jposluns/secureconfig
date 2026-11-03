#!/usr/bin/env python3
"""Check that the staged site under site/draft/ stays out of search and inside /draft/.

WHY: the template rebuild is staged at /draft/ on the live domain for the owner's review
(baseline SPECIFICATION.md section 4.1). Until it is promoted it must not be indexed, the live
pages must not point at it, and it must not depend on the live pages it will replace, or promotion
would break links that worked on the draft. Nothing else in the suite checks any of that.

A DRAFT PAGE is any file under site/draft/ named .html or .htm in any case, read by the CSP gate's
own suffix rule (check_csp_hashes.name_suffix), so a page the CSP gate checks is a page this gate
checks too.

PART 1, KEPT OUT OF SEARCH:
  - every draft page carries exactly 1 robots meta element, read by html.parser (so a commented-out
    one does not count, and attribute case and quoting do not matter), whose content is
    `noindex, nofollow` (case and spacing aside);
  - site/_headers has exactly 1 `/draft/*` rule and it sends `X-Robots-Tag: noindex` exactly once
    (the CSP gate pins that rule's other lines);
  - site/_redirects does not exist while site/draft/ holds pages: a missing draft path gets the
    draft's 404 page, never a redirect, and a redirect could serve the draft at a live URL that
    the `/draft/*` noindex rule does not match (the owner's rule);
  - site/llms.txt, site/robots.txt and site/sitemap.xml name no `/draft` path, site/llms-full.txt
    names no `secureconfig.ai/draft` URL (host-anchored, because the bundle quotes vendor URLs
    such as IETF drafts), and no live page links or loads a same-site path under /draft: each
    live page's URL attributes are read with html.parser, which decodes entities, and resolved
    against the page's own URL with urljoin, so a relative `draft/` is caught too.

PART 2, SELF-CONTAINED:
  - every URL a draft page carries, in any attribute whose name ends in `href` or `src` (so
    `xlink:href` too) and in `srcset`, `imagesrcset`, `formaction`, `action`, `ping` and `poster`,
    is an in-page `#` anchor, a root-relative path under the base path that names a file under
    site/draft/ (a folder path names its index.html), one of the recorded live exceptions
    (LIVE_EXCEPTIONS, the owner's decision of 2026-11-03), or an absolute http(s) URL with a
    non-empty authority written as `scheme://host`, on a host other than this site's;
  - refused, because a browser normalizes them onto a host the check above does not see: any
    whitespace, control character or backslash in a URL; `https:///host` and other spellings
    without a host right after `//`; and this site's host in any case, with a trailing dot or
    percent-encoded; a `pages.dev` host (the Pages project's own aliases) is refused too;
  - any `http-equiv` attribute is refused (a refresh would navigate away without a link);
  - every link that opens a new tab carries the visually hidden "(opens in a new tab)";
  - only the landing page, the Disclosure page and the Licence page link the Disclosure and Licence
    pages (the owner's template note of 2026-11-03: they left the top bar);
  - no stylesheet under site/draft/ carries `@import` in any spelling (CSS escapes decoded), every
    `url(` in one is relative and resolves to a file inside site/draft/assets/, and a
    site/draft/assets/site.css, where one exists, matches the whole permitted grammar: rules (at
    the top level or inside `@media (prefers-color-scheme: dark|light)`) whose only declarations
    set `--sw` or `--logo-inset` to a number (baseline README, "Per-site constants").

AT PROMOTION: the base path becomes `/`, LIVE_EXCEPTIONS is emptied (the files then sit beside the
pages), part 1's draft rules are removed with the /draft/ noindex, and this gate is retired or
rewritten for the root. Exit 0 ok, 1 on a finding, 2 on a read error.
Usage: python3 -I -B tools/check_draft.py [--root <repository root>]
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_csp_hashes import name_suffix  # noqa: E402  (the CSP gate's page-name rule)

DRAFT = Path("site") / "draft"
BASE = "/draft/"
SITE_HOST = "secureconfig.ai"
ORIGIN = f"https://{SITE_HOST}/"
# Live files the draft links directly, by the owner's decision of 2026-11-03. Removed at promotion.
LIVE_EXCEPTIONS = {"/llms.txt", "/llms-full.txt"}
NEWTAB = "(opens in a new tab)"
URL_FN = re.compile(r"url\(\s*(['\"]?)([^'\")]*)\1\s*\)", re.I)
ABOUT_PAGES = {"index.html", "disclosure/index.html", "license/index.html"}
URL_LISTS = {"srcset", "imagesrcset"}
URL_NAMES = {"formaction", "action", "ping", "poster"}
BAD_URL_CHARS = re.compile(r"[\x00-\x20\x7f\\]")
AUTHORITY = re.compile(r"(?i)^https?://[^/?#\\\s]")
LLMS_FULL_DRAFT = re.compile(r"(?i)(?:www\.)?secureconfig\.ai\.?(?::\d+)?/draft(?:[/?#\s)\]>\"']|$)")
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
        self.robots = []        # (line, content)
        self.http_equiv = []    # line
        self.newtab = []        # (line, text)
        self._open = []

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        names = {k for k, _ in attrs}
        for k, v in attrs:
            if v is None:
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
        if "http-equiv" in names:
            self.http_equiv.append(line)
        a = {k: (v or "") for k, v in attrs}
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


def resolves(root, path):
    """True when a root-relative draft path names a file under site/draft/."""
    rel = unquote(path[len(BASE):].split("#", 1)[0].split("?", 1)[0])
    target = (root / DRAFT / rel)
    if rel == "" or rel.endswith("/"):
        target = target / "index.html"
    try:
        target.resolve().relative_to((root / DRAFT).resolve())
    except ValueError:
        return False
    return target.is_file()


def check_url(root, value):
    """None when the value is allowed in a draft page, else the reason it is not."""
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
        if site_host(parts.hostname):
            return "is an absolute URL on this site's own host, which reaches the live pages"
        return None
    if value.startswith("//"):
        return "is a scheme-relative URL"
    if value in LIVE_EXCEPTIONS:
        return None
    if not value.startswith("/"):
        return "is a relative path; draft pages use root-relative paths under the base path"
    if not value.startswith(BASE):
        return f"is outside the base path {BASE}, so it reaches the live pages"
    if not resolves(root, value):
        return "names no file under site/draft/"
    return None


def css_unescape(text):
    return CSS_ESCAPE.sub(lambda m: chr(int(m.group(1), 16)) if m.group(1) else m.group(2), text)


def check(root):
    findings = []
    pages = page_files(root / DRAFT)
    if not pages:
        findings.append(f"{DRAFT} holds no pages")
    for page in pages:
        rel = page.relative_to(root)
        parsed = parse(page.read_text(encoding="utf-8"))
        robots = [" ".join(c.lower().replace(",", " , ").split()) for _, c in parsed.robots]
        if robots != ["noindex , nofollow"]:
            findings.append(f"{rel} must carry exactly 1 robots meta element with content "
                            f"'noindex, nofollow'; it carries {[c for _, c in parsed.robots]!r}")
        for line in parsed.http_equiv:
            findings.append(f"{rel}:{line}: carries http-equiv, which can refresh or redirect the "
                            f"page without a link; draft pages carry none")
        for line, name, value in parsed.urls:
            why = check_url(root, value)
            if why:
                findings.append(f"{rel}:{line}: {name}={value!r} {why}")
        # The owner's template note of 2026-11-03: Disclosure and Licence are linked from the landing
        # page's "About this project" region and from each other, and from no other page.
        page_rel = page.relative_to(root / DRAFT).as_posix()
        if page_rel not in ABOUT_PAGES:
            for line, name, value in parsed.urls:
                if value.split("#", 1)[0] in (BASE + "disclosure/", BASE + "license/"):
                    findings.append(f"{rel}:{line}: links {value}; only the landing page, the "
                                    f"Disclosure page and the Licence page link those 2 pages")
        for line, label in parsed.newtab:
            if NEWTAB not in label:
                findings.append(f"{rel}:{line}: a link that opens a new tab does not say so "
                                f"with a hidden {NEWTAB!r}")
    headers = (root / "site" / "_headers").read_text(encoding="utf-8").splitlines()
    rules = [i for i, line in enumerate(headers) if line.strip() == "/draft/*" and not line[0].isspace()]
    if len(rules) != 1:
        findings.append(f"site/_headers has {len(rules)} /draft/* rules; it needs exactly 1")
    else:
        block = []
        for line in headers[rules[0] + 1:]:
            if line.strip() and not line[0].isspace() and not line.lstrip().startswith("#"):
                break
            block.append(line.strip())
        robots = [b for b in block if b.lower().startswith("x-robots-tag:")]
        if robots != ["X-Robots-Tag: noindex"]:
            findings.append(f"the site/_headers /draft/* rule must send X-Robots-Tag: noindex "
                            f"exactly once; it has {robots!r}")
    if pages and (root / "site" / "_redirects").exists():
        findings.append("site/_redirects exists while site/draft/ holds pages; a missing path gets "
                        "the 404 page, never a redirect, and a redirect could serve the draft at a "
                        "live URL the /draft/* noindex rule does not match")
    for index in ("llms.txt", "robots.txt", "sitemap.xml"):
        path = root / "site" / index
        if path.is_file() and "/draft" in path.read_text(encoding="utf-8"):
            findings.append(f"site/{index} names a /draft path; the draft stays out of every index")
    full = root / "site" / "llms-full.txt"
    if full.is_file() and LLMS_FULL_DRAFT.search(full.read_text(encoding="utf-8")):
        findings.append("site/llms-full.txt names a secureconfig.ai/draft URL; the draft stays out "
                        "of every index")
    for page in page_files(root / "site"):
        rel = page.relative_to(root)
        if DRAFT in rel.parents:
            continue
        url = urljoin(ORIGIN, rel.relative_to("site").as_posix())
        parsed = parse(page.read_text(encoding="utf-8"))
        for line, name, value in parsed.urls:
            target = urlsplit(urljoin(url, value.strip()))
            if target.scheme and target.scheme.lower() not in ("http", "https"):
                continue
            path = unquote(target.path).lower()
            if (not target.hostname or site_host(target.hostname)) and (
                    path == "/draft" or path.startswith("/draft/")):
                findings.append(f"{rel}:{line}: is a live page and its {name}={value!r} reaches "
                                f"{path}, under /draft")
    assets = (root / DRAFT / "assets").resolve()
    css_files = sorted(p for p in (root / DRAFT).rglob("*") if p.is_file() and name_suffix(p.name) == ".css")
    for css in css_files:
        rel = css.relative_to(root)
        text = CSS_COMMENT.sub(" ", css.read_text(encoding="utf-8"))
        for m in AT_KEYWORD.finditer(text):
            if css_unescape(m.group(1)).lower() == "import":
                findings.append(f"{rel}: carries @import, which loads another stylesheet the "
                                f"draft's checks do not read")
        for m in URL_FN.finditer(text):
            ref = m.group(2).strip()
            parts = urlsplit(ref)
            target = (css.parent / unquote(parts.path)).resolve()
            if parts.scheme or ref.startswith("/") or "\\" in ref or not target.is_file():
                findings.append(f"{rel}: url({ref}) is not a relative path to a file in the draft")
                continue
            try:
                target.relative_to(assets)
            except ValueError:
                findings.append(f"{rel}: url({ref}) resolves outside {DRAFT}/assets/")
    site_css = root / DRAFT / "assets" / "site.css"
    if site_css.is_file():
        body = CSS_COMMENT.sub(" ", site_css.read_text(encoding="utf-8"))
        if not SITE_CSS.fullmatch(body):
            findings.append(f"{DRAFT}/assets/site.css may hold only rules (at the top level or in "
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
        print(f"  FAIL  cannot read the draft: {exc}")
        return 2
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {n} draft pages carry noindex and link only inside {BASE}, to the "
          f"{len(LIVE_EXCEPTIONS)} recorded live files, or off-site; the /draft/* rule sends "
          f"X-Robots-Tag: noindex; no _redirects, live page or index reaches /draft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
