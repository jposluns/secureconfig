#!/usr/bin/env python3
"""Check site/sitemap.xml and the Sitemap line in site/robots.txt, offline.

WHY: the owner's W4 item (his decision of 2026-11-03) has the live site publish a sitemap of every
indexable live page, with a lastmod each, referenced from robots.txt. A sitemap that lists a page
that does not exist, a page that asks not to be indexed, or a /draft/ page sends crawlers the
wrong way, and one that misses a live page leaves it out. Nothing else in the suite reads either
file.

WHAT IT CHECKS:

  - site/sitemap.xml is a regular file, not a symbolic link, decoded as strict UTF-8 and parsed
    with expat, the standard library's XML parser, with namespace processing on. It is
    well-formed, carries no document type declaration and no processing instruction, and any XML
    declaration names version 1.0 and, if it names an encoding, UTF-8;
  - its root is `urlset` in the sitemaps.org 0.9 namespace, whose only children are `url`
    elements, each holding exactly one `loc` and exactly one `lastmod`, all in that namespace, with
    no other element, no attribute and no text outside `loc` and `lastmod` but whitespace;
  - every `loc` is `https://secureconfig.ai` and a path, with no query, fragment, `..`, `.` or
    empty segment and no percent sign, that is `/` or ends with `/`, so it names the folder page
    `site/<path>index.html` (page_of). That page exists as a regular file, is not under the
    draft's base path while the site is staged, and carries no robots meta tag whose content
    includes `noindex` or `none` (which means `noindex, nofollow`), each read as one
    comma-separated token in any case. No `loc` is listed twice;
  - every `lastmod` is a calendar date written YYYY-MM-DD;
  - every indexable live page is listed: each `index.html` under site/, outside the draft tree
    while the site is staged, with no robots `noindex` or `none`. Any other `.html` there must
    carry `noindex` or `none` (site/404.html carries `noindex`), because this gate maps only
    folder pages to URLs;
  - site/robots.txt carries exactly one Sitemap line (the field name in any case), and it is
    `Sitemap: https://secureconfig.ai/sitemap.xml`.

THE BASE PATH: the draft tree (DRAFT, site/draft) and its base path (BASE, /draft/) are imported
from tools/check_draft.py, the one place they are kept. The site is staged while BASE is not `/`.
When promotion sets BASE to `/`, the two draft rules above switch off: no `loc` is refused as a
draft page, and every page under site/ is a live page.

WHAT IT DOES NOT CHECK: that a `lastmod` is the date the page last changed. That needs git
history, and this gate reads none, so it runs the same with or without a repository;
tools/check_sitemap_lastmod.py compares each `lastmod` with `git log -1 --format=%cs -- <page>`
for the page that page_of maps its `loc` to. This gate does not check how a host or crawler
treats either file, or the protocol's size limits, which one URL is far inside. The robots
`noindex` reading is a lexical scan of `<meta>` tags with html.parser, not a browser's reading of
the page.

Exit 0 with one ok line, or 1 with one FAIL line per finding.
"""
import os
import re
import stat
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from xml.parsers import expat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_draft import BASE, DRAFT  # noqa: E402  (the draft tree and its base path)

SITE = Path("site")
SITEMAP = SITE / "sitemap.xml"
ROBOTS = SITE / "robots.txt"
# The draft rules hold only while the site is staged below the root.
STAGED = BASE != "/"
ORIGIN = "https://secureconfig.ai"
SITEMAP_URL = f"{ORIGIN}/sitemap.xml"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SEP = "|"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# A path of folder segments: ASCII letters, digits, hyphens and underscores, each followed by `/`.
FOLDER_PATH = re.compile(r"/(?:[A-Za-z0-9_-]+/)*")


class Robots(HTMLParser):
    """Collect the content of every `<meta name="robots">` on a page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.contents = []

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            values = {k.lower(): (v or "") for k, v in attrs}
            if values.get("name", "").strip().lower() == "robots":
                self.contents.append(values.get("content", ""))

    handle_startendtag = handle_starttag


def noindex(path):
    """True when the page carries a robots meta tag whose content includes noindex or none."""
    parser = Robots()
    parser.feed(path.read_bytes().decode("utf-8"))
    parser.close()
    return any({"noindex", "none"} & {t.strip().lower() for t in c.split(",")}
               for c in parser.contents)


def regular(root, rel):
    """None when root/rel is a regular file that is not a link, otherwise the reason it is not."""
    try:
        mode = (root / rel).lstat().st_mode
    except FileNotFoundError:
        return f"{rel} is missing"
    except OSError as exc:
        return f"cannot inspect {rel}: {exc}"
    if stat.S_ISLNK(mode):
        return f"{rel} is a symbolic link; ship the file itself, so what is checked is what is served"
    if not stat.S_ISREG(mode):
        return f"{rel} is not a regular file"
    return None


def parse_sitemap(text):
    """(entries, findings): each entry a dict of `loc` and `lastmod` lists, in document order."""
    parser = expat.ParserCreate(namespace_separator=SEP)
    entries, findings, stack = [], [], []

    def where():
        return f"{SITEMAP}:{parser.CurrentLineNumber}"

    fields = {f"{NS}{SEP}loc": "loc", f"{NS}{SEP}lastmod": "lastmod"}

    def start(name, attrs):
        depth = len(stack)
        stack.append([name, ""])
        if attrs:
            findings.append(f"{where()}: <{name}> carries attributes, which this gate does not model")
        expected = {0: ("urlset",), 1: ("url",), 2: ("loc", "lastmod")}.get(depth, ())
        if name not in tuple(f"{NS}{SEP}{e}" for e in expected):
            findings.append(f"{where()}: <{name}> is not allowed here; the model is urlset, url, "
                            f"loc and lastmod in the {NS} namespace")
        if depth == 1:
            entries.append({"loc": [], "lastmod": [], "line": parser.CurrentLineNumber})
        elif depth == 2 and entries and name in fields:
            entries[-1][fields[name]].append("")

    def end(name):
        _, text = stack.pop()
        if len(stack) == 2 and entries and name in fields:
            entries[-1][fields[name]][-1] = text

    def chars(data):
        if stack:
            stack[-1][1] += data
            if len(stack) != 3 and data.strip():
                findings.append(f"{where()}: text outside loc and lastmod: {data.strip()!r}")

    def xml_decl(version, encoding, standalone):
        if version != "1.0":
            raise ValueError(f"the XML declaration names version {version!r}, not 1.0")
        if encoding is not None and encoding.lower() != "utf-8":
            raise ValueError(f"the XML declaration names encoding {encoding!r}, not UTF-8")

    def refuse(what):
        def handler(*args):
            raise ValueError(f"{what} is outside this gate's model")
        return handler

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = chars
    parser.XmlDeclHandler = xml_decl
    parser.StartDoctypeDeclHandler = refuse("a document type declaration")
    parser.ProcessingInstructionHandler = refuse("a processing instruction")
    parser.ExternalEntityRefHandler = refuse("an external entity")
    try:
        parser.Parse(text, True)
    except (expat.ExpatError, ValueError) as exc:
        return [], [f"{where()}: cannot parse the sitemap: {exc}"]
    return entries, findings


def page_of(loc):
    """(page, None) for a loc in the one URL form this gate maps, else (None, the reason).

    `https://secureconfig.ai/` maps to site/index.html and `https://secureconfig.ai/<path>/` to
    site/<path>/index.html, relative to the root, at any depth. While the site is staged, a loc
    under BASE maps to no page. Whether the page exists is not checked here.
    """
    path = loc[len(ORIGIN):] if loc.startswith(ORIGIN + "/") else None
    if path is None or not FOLDER_PATH.fullmatch(path):
        return None, (f"loc {loc!r} is not {ORIGIN} and a folder path ending with /, "
                      f"the only URL form this gate maps to a page")
    if STAGED and path.startswith(BASE):
        return None, f"loc {loc!r} is a {BASE} page, which stays out of search"
    return (SITE / path.strip("/") / "index.html" if path != "/" else SITE / "index.html"), None


def live_pages(root):
    """(folder page paths, other HTML paths) relative to root, skipping DRAFT while staged; no
    links followed."""
    folders, others = [], []
    for current, dirs, files in os.walk(root / SITE):
        here = Path(current).relative_to(root)
        dirs[:] = sorted(d for d in dirs if not (STAGED and here / d == DRAFT))
        for f in sorted(files):
            if f.lower().endswith((".html", ".htm")):
                (folders if f == "index.html" else others).append(here / f)
    return folders, others


def check(root):
    """Every finding for the sitemap and robots.txt under `root`, as display strings."""
    findings = []
    reason = regular(root, SITEMAP)
    if reason:
        findings.append(reason)
        entries = []
    else:
        try:
            text = (root / SITEMAP).read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            text = None
            findings.append(f"cannot read {SITEMAP} as UTF-8: {exc}")
        entries, parsed = parse_sitemap(text) if text is not None else ([], [])
        findings += parsed

    listed = set()
    for entry in entries:
        line = f"{SITEMAP}:{entry['line']}"
        if len(entry["loc"]) != 1 or len(entry["lastmod"]) != 1:
            findings.append(f"{line}: a <url> must hold exactly one <loc> and one <lastmod>; it "
                            f"holds {len(entry['loc'])} and {len(entry['lastmod'])}")
            continue
        loc, lastmod = entry["loc"][0].strip(), entry["lastmod"][0].strip()
        try:
            valid_date = bool(DATE.fullmatch(lastmod)) and date.fromisoformat(lastmod)
        except ValueError:
            valid_date = False
        if not valid_date:
            findings.append(f"{line}: lastmod {lastmod!r} is not a calendar date written YYYY-MM-DD")
        page, reason = page_of(loc)
        if reason:
            findings.append(f"{line}: {reason}")
            continue
        if loc in listed:
            findings.append(f"{line}: loc {loc!r} is listed more than once")
            continue
        listed.add(loc)
        reason = regular(root, page)
        if reason:
            findings.append(f"{line}: loc {loc!r} names {page}, but {reason}")
        else:
            try:
                if noindex(root / page):
                    findings.append(f"{line}: loc {loc!r} names {page}, which carries a robots "
                                    f"noindex or none, so it must not be in the sitemap")
            except (OSError, UnicodeError) as exc:
                findings.append(f"cannot read {page} as UTF-8: {exc}")

    folders, others = live_pages(root)
    for page in folders + others:
        try:
            hidden = noindex(root / page)
        except (OSError, UnicodeError) as exc:
            findings.append(f"cannot read {page} as UTF-8: {exc}")
            continue
        if hidden:
            continue
        if page in others:
            findings.append(f"{page} is an indexable live page that is not a folder index.html, "
                            f"which this gate cannot map to a sitemap URL; give it a robots "
                            f"noindex or move it to a folder")
            continue
        rel = page.parent.relative_to(SITE).as_posix()
        loc = f"{ORIGIN}/" if rel == "." else f"{ORIGIN}/{rel}/"
        if loc not in listed:
            findings.append(f"{page} is an indexable live page, and {SITEMAP} does not list {loc}")

    reason = regular(root, ROBOTS)
    if reason:
        findings.append(reason)
    else:
        try:
            robots = (root / ROBOTS).read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(f"cannot read {ROBOTS} as UTF-8: {exc}")
        else:
            lines = [ln for ln in robots.splitlines()
                     if ln.split(":", 1)[0].strip().lower() == "sitemap" and ":" in ln]
            if lines != [f"Sitemap: {SITEMAP_URL}"]:
                findings.append(f"{ROBOTS} must carry exactly one Sitemap line, "
                                f"'Sitemap: {SITEMAP_URL}'; it carries {lines!r}")
    return findings, len(listed)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings, count = check(root)
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    draft = f" and none under {BASE}" if STAGED else ""
    print(f"  ok    {SITEMAP} lists all {count} indexable live page(s), each existing with a "
          f"lastmod{draft}, and {ROBOTS} names it in one Sitemap line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
