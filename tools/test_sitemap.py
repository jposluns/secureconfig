#!/usr/bin/env python3
"""Cases for check_sitemap.py: the real files pass, and each defect it names fails.

Each case copies the real gate and the modules it imports (check_draft.py, check_csp_hashes.py)
into a throwaway tree with the real pages under site/, site/robots.txt and site/sitemap.xml,
applies one change, and runs the gate as a subprocess, so what is under test is the shipped entry
point. A must-fail case names a substring its finding must carry; every case checks the exit
status, the ok line on a pass and a FAIL line on a refusal.

Each run sets the BASE line of the copied check_draft.py, so the cases hold whichever base the
shipped file names. CASES run at base /, the promoted site, where the real sitemap lists the 7
indexable pages and the 404 stays out by its noindex. The live site carries no /draft/ page
(baseline SPECIFICATION section 4.1 items 0 and 2), so at base / a /draft/ loc, in any case, is
refused by its first segment, with or without a page planted under site/draft/. STAGED_CASES run
at base /draft/, where the gate's staged rules switch back on: a tree under site/draft/ is left
out of the sitemap and a /draft/ loc is refused outright. One case at each base writes the pages
of scripts/build-site.py, with `--base / --out <tree>/site` at / and under site/draft/ at
/draft/.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SITE = ROOT / "site"
BUILD = ROOT / "scripts" / "build-site.py"
GATES = ("check_sitemap.py", "check_draft.py", "check_csp_hashes.py")
# The line of check_draft.py that sets the base path, which each run sets to its own base.
BASE_LINE = re.compile(r'^BASE = "[^"\n]*"$', re.M)
PAGES = ("index.html", "404.html", "guides/index.html", "for-ai/index.html",
         "for-humans/index.html", "checklist/index.html", "disclosure/index.html",
         "license/index.html")
REAL = {name: (SITE / name).read_bytes() for name in PAGES + ("robots.txt", "sitemap.xml")}
SITEMAP = REAL["sitemap.xml"].decode("utf-8")
ROBOTS = REAL["robots.txt"].decode("utf-8")
# The real sitemap's first lastmod, read rather than written here, so a lastmod update cannot turn
# the date mutations below into no-ops.
LASTMOD = re.search(r"<lastmod>([^<]*)</lastmod>", SITEMAP).group(1)
LOC = "<loc>https://secureconfig.ai/</loc>"
URL_END = "  </url>\n"
INDEXABLE = b'<!doctype html>\n<meta charset="utf-8">\n<title>t</title>\n'
HIDDEN = b'<!doctype html>\n<meta charset="utf-8">\n<meta name="robots" content="noindex">\n'
NOINDEX_META = b'<meta name="robots" content="noindex, nofollow">\n'


def entry(path, lastmod=LASTMOD):
    return (f"  <url>\n    <loc>https://secureconfig.ai{path}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n  </url>\n")


def with_entry(path, lastmod=LASTMOD):
    return SITEMAP.replace("</urlset>", entry(path, lastmod) + "</urlset>", 1)


def run(files=None, setup=None, base="/"):
    """Run the real gate against the real files with `files` (name: str, bytes or None) applied."""
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        for gate in GATES:
            shutil.copy(TOOLS / gate, d / "tools" / gate)
        draft = d / "tools" / "check_draft.py"
        text, count = BASE_LINE.subn(f'BASE = "{base}"', draft.read_text(encoding="utf-8"))
        if count != 1:
            return None, f"check_draft.py holds {count} BASE lines; this test sets exactly 1"
        draft.write_text(text, encoding="utf-8")
        (d / "site").mkdir()
        merged = dict(REAL)
        merged.update(files or {})
        for name, content in merged.items():
            if content is None:
                continue
            target = d / "site" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        if setup is not None:
            setup(d)
        r = subprocess.run([sys.executable, "-I", "-B", "tools/check_sitemap.py"], cwd=d,
                           capture_output=True, text=True, timeout=20)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def symlinked(d):
    (d / "site" / "sitemap.xml").rename(d / "site" / "real.xml")
    (d / "site" / "sitemap.xml").symlink_to("real.xml")


def built(base, out):
    """A setup that writes the pages of scripts/build-site.py for `base` under `out` in the tree."""
    def setup(d):
        r = subprocess.run([sys.executable, "-I", "-B", str(BUILD), "--base", base,
                            "--out", str(d / out)], capture_output=True, text=True, timeout=120)
        if r.returncode:
            raise RuntimeError(f"build-site.py --base {base} failed: {r.stdout + r.stderr}")
    return setup


# (description, files, setup, expected substring for a refusal or None for a pass), at base /.
CASES = [
    ("the real files", None, None, None),
    ("the promoted build of scripts/build-site.py at the root, its indexable pages listed", None,
     built("/", "site"), None),
    ("a new live folder page, listed",
     {"extra/index.html": INDEXABLE, "sitemap.xml": with_entry("/extra/")}, None, None),
    ("a listed folder page whose robots meta carries noindex, nofollow",
     {"extra/index.html": INDEXABLE.replace(
         b"<title>", b'<meta name="robots" content="noindex, nofollow">\n<title>'),
      "sitemap.xml": with_entry("/extra/")}, None, "carries a robots noindex"),
    ("a noindex folder page left out of the sitemap",
     {"extra/index.html": HIDDEN}, None, None),
    ("a listed folder page whose robots meta is NONE, noarchive",
     {"extra/index.html": HIDDEN.replace(b'content="noindex"', b'content="NONE, noarchive"'),
      "sitemap.xml": with_entry("/extra/")}, None, "carries a robots noindex"),
    ("a folder page whose robots meta is none, left out of the sitemap",
     {"extra/index.html": HIDDEN.replace(b'content="noindex"', b'content="none"')}, None, None),
    # The unlisted advisory page is noindex and is not a folder index.html, so the gate neither
    # requires it in the sitemap nor flags it, and the sitemap cannot list it: its URL is not a
    # folder path ending with /.
    ("the noindex advisory page, not a folder index, left out of the sitemap",
     {"advisories/n8n.html": HIDDEN}, None, None),
    ("a sitemap listing the advisory page by its exact path",
     {"advisories/n8n.html": HIDDEN, "sitemap.xml": with_entry("/advisories/n8n.html")}, None,
     "folder path"),
    ("a /draft/ loc, with no draft tree", {"sitemap.xml": with_entry("/draft/")}, None,
     "is a /draft/ page; the live site carries no /draft/ page"),
    ("a /Draft/ loc in another case", {"sitemap.xml": with_entry("/Draft/")}, None,
     "is a /draft/ page; the live site carries no /draft/ page"),
    ("a /draft/ loc with a noindex page planted under site/draft/",
     {"draft/index.html": HIDDEN, "sitemap.xml": with_entry("/draft/")}, None,
     "is a /draft/ page; the live site carries no /draft/ page"),
    ("a /draft/ subpage loc with an indexable page planted under site/draft/",
     {"draft/guides/index.html": INDEXABLE, "sitemap.xml": with_entry("/draft/guides/")}, None,
     "is a /draft/ page; the live site carries no /draft/ page"),
    ("no sitemap", {"sitemap.xml": None}, None, "site/sitemap.xml is missing"),
    ("the sitemap as a symbolic link", None, symlinked, "symbolic link"),
    ("a sitemap that is not UTF-8", {"sitemap.xml": REAL["sitemap.xml"] + b"\xff"}, None,
     "as UTF-8"),
    ("a sitemap that is not well-formed", {"sitemap.xml": SITEMAP.replace("</urlset>", "", 1)},
     None, "cannot parse the sitemap"),
    ("a document type declaration",
     {"sitemap.xml": SITEMAP.replace("<urlset", "<!DOCTYPE urlset>\n<urlset", 1)}, None,
     "document type declaration"),
    ("a processing instruction",
     {"sitemap.xml": SITEMAP.replace("<urlset", '<?xml-stylesheet href="s.xsl"?>\n<urlset', 1)},
     None, "processing instruction"),
    ("an encoding other than UTF-8",
     {"sitemap.xml": SITEMAP.replace('encoding="UTF-8"', 'encoding="ISO-8859-1"', 1)}, None,
     "not UTF-8"),
    ("the wrong namespace",
     {"sitemap.xml": SITEMAP.replace("sitemap/0.9", "sitemap/0.8", 1)}, None, "is not allowed here"),
    ("an element outside the model",
     {"sitemap.xml": SITEMAP.replace(URL_END, "    <changefreq>weekly</changefreq>\n" + URL_END, 1)},
     None, "is not allowed here"),
    ("an attribute", {"sitemap.xml": SITEMAP.replace("<url>", '<url id="a">', 1)}, None,
     "carries attributes"),
    ("text outside loc and lastmod",
     {"sitemap.xml": SITEMAP.replace(URL_END, "    stray\n" + URL_END, 1)}, None,
     "text outside loc and lastmod"),
    ("a url with no lastmod",
     {"sitemap.xml": SITEMAP.replace(f"    <lastmod>{LASTMOD}</lastmod>\n", "", 1)}, None,
     "exactly one <loc> and one <lastmod>"),
    ("a url with two locs",
     {"sitemap.xml": SITEMAP.replace(LOC, LOC + "\n    " + LOC, 1)}, None,
     "exactly one <loc> and one <lastmod>"),
    ("a lastmod that is no calendar date",
     {"sitemap.xml": SITEMAP.replace(LASTMOD, "2026-13-01", 1)}, None, "not a calendar date"),
    ("a lastmod with a time", {"sitemap.xml": SITEMAP.replace(LASTMOD, LASTMOD + "T00:00Z", 1)},
     None, "not a calendar date"),
    ("a loc on another host",
     {"sitemap.xml": SITEMAP.replace("secureconfig.ai/", "secureconfig.example/", 1)}, None,
     "is not https://secureconfig.ai"),
    ("a loc over plain HTTP", {"sitemap.xml": SITEMAP.replace("https://", "http://", 1)}, None,
     "is not https://secureconfig.ai"),
    ("a loc with a query string", {"sitemap.xml": SITEMAP.replace(LOC, LOC.replace("/<", "/?a=1<"), 1)},
     None, "folder path"),
    ("a loc naming a file, not a folder", {"sitemap.xml": with_entry("/404.html")}, None,
     "folder path"),
    ("a loc with a dot-dot segment", {"sitemap.xml": with_entry("/../")}, None, "folder path"),
    ("a loc naming a page that does not exist", {"sitemap.xml": with_entry("/nowhere/")}, None,
     "site/nowhere/index.html is missing"),
    ("the same loc twice", {"sitemap.xml": with_entry("/")}, None, "listed more than once"),
    ("an indexable live folder page left out", {"extra/index.html": INDEXABLE}, None,
     "does not list https://secureconfig.ai/extra/"),
    ("every page left out",
     {"sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>\n'},
     None, "does not list https://secureconfig.ai/"),
    ("an indexable page that is not a folder index", {"about.html": INDEXABLE}, None,
     "not a folder index.html"),
    ("the 404 page losing its noindex",
     {"404.html": REAL["404.html"].replace(NOINDEX_META, b"", 1)},
     None, "site/404.html is an indexable live page"),
    ("robots.txt with no Sitemap line",
     {"robots.txt": ROBOTS.replace("Sitemap: https://secureconfig.ai/sitemap.xml\n", "", 1)}, None,
     "exactly one Sitemap line"),
    ("robots.txt with two Sitemap lines",
     {"robots.txt": ROBOTS + "sitemap: https://secureconfig.ai/other.xml\n"}, None,
     "exactly one Sitemap line"),
    ("robots.txt naming another sitemap",
     {"robots.txt": ROBOTS.replace("/sitemap.xml", "/other/sitemap.xml", 1)}, None,
     "exactly one Sitemap line"),
    ("no robots.txt", {"robots.txt": None}, None, "site/robots.txt is missing"),
]

# The same shape as CASES, run at base /draft/ (a staged rebuild), where the gate's draft rules
# switch back on: the staged tree stays out of the sitemap and a /draft/ loc is refused outright.
STAGED_CASES = [
    ("the real files", None, None, None),
    ("a staged tree with its own index pages, left out of the sitemap",
     {"draft/staging/index.html": INDEXABLE, "draft/guides/index.html": INDEXABLE}, None, None),
    ("the staged build of scripts/build-site.py under site/draft/, left out of the sitemap", None,
     built("/draft/", "site/draft"), None),
    ("a /draft/ page", {"sitemap.xml": with_entry("/draft/")}, None, "is a /draft/ page"),
    ("a /draft/ subpage", {"draft/guides/index.html": INDEXABLE,
                           "sitemap.xml": with_entry("/draft/guides/")}, None, "is a /draft/ page"),
]


def main() -> int:
    failures = []
    for (desc, files, setup, expected), base in (
            [(case, "/") for case in CASES] + [(case, "/draft/") for case in STAGED_CASES]):
        desc = desc if base == "/" else f"base /draft/: {desc}"
        for name, content in (files or {}).items():
            if name in REAL and content is not None and (
                    content if isinstance(content, bytes) else content.encode("utf-8")) == REAL[name]:
                failures.append(f"{desc}: the mutation of {name} did not change the real file")
        rc, out = run(files, setup, base)
        if rc != (0 if expected is None else 1):
            failures.append(f"{desc}: expected the gate to {'pass' if expected is None else 'fail'}"
                            f", exit {rc}: {out!r}")
        elif expected is not None and expected not in out:
            failures.append(f"{desc}: expected a finding containing {expected!r}: {out!r}")
        elif expected is None and ("  FAIL  " in out or not out.startswith("ok    ")):
            failures.append(f"{desc}: a pass must print one ok line and no FAIL line: {out!r}")
        elif expected is not None and not out.startswith("FAIL  "):
            failures.append(f"{desc}: a refusal must print a FAIL line: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES) + len(STAGED_CASES)} recorded cases for the sitemap gate, "
          f"{len(STAGED_CASES)} of them at base /draft/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
