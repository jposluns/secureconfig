#!/usr/bin/env python3
"""Check that the staged site under site/draft/ stays out of search and inside /draft/.

WHY: the template rebuild is staged at /draft/ on the live domain for the owner's review
(baseline SPECIFICATION.md section 4.1). Until it is promoted it must not be indexed, the live
pages must not point at it, and it must not depend on the live pages it will replace, or promotion
would break links that worked on the draft. Nothing else in the suite checks any of that.

PART 1, KEPT OUT OF SEARCH:
  - every site/draft/**/*.html carries exactly 1 `<meta name="robots" content="noindex, nofollow">`;
  - site/_headers has exactly 1 `/draft/*` rule and it sends `X-Robots-Tag: noindex` exactly once;
  - site/llms.txt, site/robots.txt and site/sitemap.xml (where present) and every live page
    (site/**/*.html outside site/draft/) name no `/draft` path.

PART 2, SELF-CONTAINED:
  - every href, src and srcset value in a draft page is an in-page `#` anchor, a root-relative path
    under the base path that names a file under site/draft/ (a folder path names its index.html),
    one of the recorded live exceptions (LIVE_EXCEPTIONS, the owner's decision of 2026-11-03), or
    an absolute http(s) URL on a host other than this site's; a relative path, any other
    root-relative path, a URL on this site's host and any other scheme are findings;
  - every link that opens a new tab carries the visually hidden "(opens in a new tab)";
  - only the landing page, the Disclosure page and the Licence page link the Disclosure and Licence
    pages (the owner's template note of 2026-11-03: they left the top bar);
  - every `url(` in a stylesheet under site/draft/ is relative and resolves to a file inside
    site/draft/assets/, and a site/draft/assets/site.css, where one exists, sets only the 2 per-site constants
    `--sw` and `--logo-inset` (baseline README, "Per-site constants").

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
from urllib.parse import urlsplit

DRAFT = Path("site") / "draft"
BASE = "/draft/"
SITE_HOSTS = {"secureconfig.ai", "www.secureconfig.ai"}
# Live files the draft links directly, by the owner's decision of 2026-11-03. Removed at promotion.
LIVE_EXCEPTIONS = {"/llms.txt", "/llms-full.txt"}
ROBOTS_META = '<meta name="robots" content="noindex, nofollow">'
NEWTAB = "(opens in a new tab)"
URL_FN = re.compile(r"url\(\s*(['\"]?)([^'\")]*)\1\s*\)", re.I)
CONSTANTS = {"--sw", "--logo-inset"}
ABOUT_PAGES = {"index.html", "disclosure/index.html", "license/index.html"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []          # (line, attribute, value)
        self.newtab = []        # [line, text] for each open target=_blank anchor
        self._open = []

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        for k, v in attrs:
            if v is None:
                continue
            if k in ("href", "src"):
                self.urls.append((line, k, v))
            elif k == "srcset":
                for part in v.split(","):
                    if part.strip():
                        self.urls.append((line, k, part.strip().split()[0]))
        if tag == "a":
            a = dict(attrs)
            # An aria-label replaces the link text as its accessible name, so it may carry the hint.
            self._open.append([line, a.get("aria-label") or "", a.get("target") == "_blank"])

    def handle_data(self, data):
        for a in self._open:
            a[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._open:
            line, text, blank = self._open.pop()
            if blank:
                self.newtab.append((line, text))


def resolves(root, path):
    """True when a root-relative draft path names a file under site/draft/."""
    rel = path[len(BASE):].split("#", 1)[0].split("?", 1)[0]
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
    if value.startswith("#"):
        return None
    parts = urlsplit(value)
    if parts.scheme:
        if parts.scheme.lower() not in ("http", "https"):
            return f"uses the {parts.scheme}: scheme"
        if (parts.hostname or "").lower() in SITE_HOSTS:
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


def draft_pages(root):
    return sorted(p for p in (root / DRAFT).rglob("*.html") if p.is_file())


def check(root):
    findings = []
    pages = draft_pages(root)
    if not pages:
        findings.append(f"{DRAFT} holds no pages")
    for page in pages:
        rel = page.relative_to(root)
        text = page.read_text(encoding="utf-8")
        if text.count(ROBOTS_META) != 1 or len(re.findall(r'name="robots"', text)) != 1:
            findings.append(f"{rel} does not carry exactly 1 {ROBOTS_META}")
        parser = Links()
        parser.feed(text)
        parser.close()
        for line, name, value in parser.urls:
            why = check_url(root, value)
            if why:
                findings.append(f"{rel}:{line}: {name}={value!r} {why}")
        # The owner's template note of 2026-11-03: Disclosure and Licence are linked from the landing
        # page's "About this project" region and from each other, and from no other page.
        page_rel = page.relative_to(root / DRAFT).as_posix()
        if page_rel not in ABOUT_PAGES:
            for line, name, value in parser.urls:
                if value.split("#", 1)[0] in (BASE + "disclosure/", BASE + "license/"):
                    findings.append(f"{rel}:{line}: links {value}; only the landing page, the "
                                    f"Disclosure page and the Licence page link those 2 pages")
        for line, label in parser.newtab:
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
    for index in ("llms.txt", "robots.txt", "sitemap.xml"):
        path = root / "site" / index
        if path.is_file() and "/draft" in path.read_text(encoding="utf-8"):
            findings.append(f"site/{index} names a /draft path; the draft stays out of every index")
    for page in sorted((root / "site").rglob("*.html")):
        if DRAFT in page.relative_to(root).parents:
            continue
        if "/draft" in page.read_text(encoding="utf-8"):
            findings.append(f"{page.relative_to(root)} is a live page and names a /draft path")
    assets = (root / DRAFT / "assets").resolve()
    for css in sorted((root / DRAFT).rglob("*.css")):
        rel = css.relative_to(root)
        text = css.read_text(encoding="utf-8")
        for m in URL_FN.finditer(text):
            ref = m.group(2).strip()
            parts = urlsplit(ref)
            target = (css.parent / parts.path).resolve()
            if parts.scheme or ref.startswith("/") or not target.is_file():
                findings.append(f"{rel}: url({ref}) is not a relative path to a file in the draft")
                continue
            try:
                target.relative_to(assets)
            except ValueError:
                findings.append(f"{rel}: url({ref}) resolves outside {DRAFT}/assets/")
    site_css = root / DRAFT / "assets" / "site.css"
    if site_css.is_file():
        body = re.sub(r"/\*.*?\*/", "", site_css.read_text(encoding="utf-8"), flags=re.S)
        props = re.findall(r"([A-Za-z-]+)\s*:", re.sub(r"[^{};]*\{", "{", body))
        others = sorted(set(props) - CONSTANTS)
        if not props or others:
            findings.append(f"{DRAFT}/assets/site.css may set only {sorted(CONSTANTS)}; it sets "
                            f"{others or 'nothing'}")
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
          f"X-Robots-Tag: noindex; no live page or index names /draft")
    return 0


if __name__ == "__main__":
    sys.exit(main())
