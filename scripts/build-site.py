#!/usr/bin/env python3
"""Build the secureconfig.ai pages on the shared site template (baseline 1.3.1).

Usage:
  python3 -I -B scripts/build-site.py                 write the pages under site/draft/
  python3 -I -B scripts/build-site.py --check         build in memory and compare; write nothing
  python3 -I -B scripts/build-site.py --list-inputs   print the files the build reads
  python3 -I -B scripts/build-site.py --base / --out site   the build after promotion

Every page is generated from this repository's sources with the markup of the baseline's reference
pages (SPECIFICATION.md section 7): README.md for the guide index, the 10 rules and the checklist
count; site-src/content.json for the page copy, each entry with its source; and
tools/version_basis_guides.txt for 1 count on the Disclosure page. Counts are computed, so a new
guide or rule makes `--check` report the pages stale. Internal links and assets take the base path
(`/draft/` while staging, `/` after promotion); the only internal links that do not are the 2 live
files the draft links directly, /llms.txt and /llms-full.txt.

The build refuses to write, and `--check` fails, when a page would contain an en or em dash, an
inline style or `style=` attribute, a `<script>` without `src` or with a body, an `on*` attribute,
or "what this is" framing (SPECIFICATION.md section 12). It does not write the copied baseline
files under assets/baseline/ (scripts/copy-baseline.py does). `--check` also fails on any file under
the output folder that is neither a page it writes nor under assets/baseline/, a page being a .html
or .htm file in any case, as the CSP gate names one.

Exit status: 0 on success (or no difference), 1 on a refusal or a difference, 2 on a read error.
Standard library only. No network.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_csp_hashes import STYLE_ATTR, VALUED_HANDLER, name_suffix  # noqa: E402  (shared rules)

CONTENT = Path("site-src") / "content.json"
README = Path("README.md")
VERSIONED = Path("tools") / "version_basis_guides.txt"
LIVE_INDEX = Path("site") / "index.html"
COPIED = "assets/baseline/"  # the copied template files, which this build does not write
REPO = "https://github.com/jposluns/secureconfig"
BLOB = REPO + "/blob/main/"
# The live files the draft links directly (owner's decision 5, 2026-11-03); removed at promotion,
# when they sit beside the pages at the same root.
LIVE_FILES = ("/llms.txt", "/llms-full.txt")
LOGO_ALT = "A terminal window with a padlock and a small shield"
NEWTAB = '<span class="vh"> (opens in a new tab)</span>'
# The site's own pages, then GitHub last (the owner's template note of 2026-11-03): Disclosure and
# Licence are linked from the landing page's "About this project" region, not the top bar.
NAV = (("Guides", "guides/"), ("For AI assistants", "for-ai/"), ("For humans", "for-humans/"),
       ("Checklist", "checklist/"))
FAMILY = (("secureconfig", "SecureConfig", None), ("opfiles", "OPFiles", "https://opfiles.ai/"),
          ("auditthis", "AuditThis", "https://auditthis.ai/"),
          ("cleanlanguage", "CleanLanguage", "https://cleanlanguage.ai/"),
          ("aiqt", "AIQT", "https://aiqt.ai/"), ("grclibrary", "GRCLibrary", "https://grclibrary.ai/"))
INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|\*([^*]+)\*|(https?://[^\s)]+[^\s).,;:])")
DASHES = ("–", "—")
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)
FRAMING = re.compile(r"what\s+this\s+is", re.I)


class Refused(Exception):
    """A page the build will not write."""


class SourceError(Exception):
    """A source file is missing or not in the shape the build reads."""


def esc(text):
    return html.escape(text, quote=False)


def attr(text):
    return html.escape(text, quote=True)


class Builder:
    def __init__(self, base, root=ROOT):
        if not (base.startswith("/") and base.endswith("/")):
            raise SourceError(f"--base must start and end with /, not {base!r}")
        self.base = base
        self.root = root
        self.read_sources()

    # ---- sources ----
    def read(self, rel):
        try:
            return (self.root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise SourceError(f"cannot read {rel}: {exc}") from exc

    def section(self, lines, heading):
        """The lines of a level-2 README section, up to the next level-2 heading."""
        try:
            start = lines.index(heading) + 1
        except ValueError:
            raise SourceError(f"{README} has no {heading!r} section") from None
        end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
        return lines[start:end]

    def read_sources(self):
        try:
            self.c = json.loads(self.read(CONTENT))
        except json.JSONDecodeError as exc:
            raise SourceError(f"{CONTENT} is not valid JSON: {exc}") from exc
        lines = self.read(README).splitlines()
        self.categories = []
        for line in self.section(lines, "## Guide index"):
            if line.startswith("### "):
                self.categories.append((line[4:].strip(), []))
            elif m := re.match(r"^\| \[([a-z0-9.-]+)\.md\]\(\1\.md\) \| (.+) \|$", line):
                if not self.categories:
                    raise SourceError(f"{README} has a guide row before any category")
                self.categories[-1][1].append((m.group(1), m.group(2)))
        self.rules = [m.group(1) for line in
                      self.section(lines, "## Instructions for AI development assistants")
                      if (m := re.match(r"^\d+\. (.+)$", line))]
        self.checks = [m.group(1) for line in self.section(lines, "## Verification checklist")
                       if (m := re.match(r"^\d+\. (.+)$", line))]
        if not self.categories or not self.rules or not self.checks:
            raise SourceError(f"{README} yielded no guides, rules or checks")
        # README's own cross-references ("the checklist below") that do not hold on the site page.
        for e in self.c["for_ai"].get("rule_edits", []):
            i = e["rule"] - 1
            if not 0 <= i < len(self.rules) or self.rules[i].count(e["old"]) != 1:
                raise SourceError(f"rule edit for rule {e['rule']}: {e['old']!r} is not in "
                                  f"{README} rule {e['rule']} exactly once")
            self.rules[i] = self.rules[i].replace(e["old"], e["new"])
        self.versioned = sum(1 for line in self.read(VERSIONED).splitlines()
                             if line.strip() and not line.startswith("#"))
        tasks = self.c["for_humans"]["tasks"]
        self.counts = {
            "guides": sum(len(g) for _, g in self.categories),
            "categories": len(self.categories),
            "rules": len(self.rules),
            "checks": len(self.checks),
            "tasks": len(tasks),
            "versioned": self.versioned,
            "checklist_tasks": sum("verification checklist" in t["prompt"].lower() for t in tasks),
            "approval_tasks": sum("wait for my approval" in t["prompt"].lower() for t in tasks),
        }
        rows = self.c["checklist"]["rows"]
        if len(rows) != len(self.checks):
            raise SourceError(f"{CONTENT} has {len(rows)} checklist rows and {README} has "
                              f"{len(self.checks)} checklist items")
        for i, (row, item) in enumerate(zip(rows, self.checks), 1):
            if row["quote"] not in item:
                raise SourceError(f"checklist row {i}: its quote {row['quote']!r} is not in "
                                  f"{README} checklist item {i}")
        # While the live page exists, the task prompts must be the live page's, word for word.
        if (self.root / LIVE_INDEX).is_file():
            live = self.read(LIVE_INDEX)
            for t in tasks:
                if f'<pre id="{t["id"]}">{t["prompt"]}</pre>' not in live:
                    raise SourceError(f"task {t['id']} differs from its prompt in {LIVE_INDEX}")
                if f"<h3>{t['title']}</h3>" not in live:
                    raise SourceError(f"task {t['id']} title differs from {LIVE_INDEX}")

    def inputs(self):
        out = [CONTENT, README, VERSIONED]
        if (self.root / LIVE_INDEX).is_file():
            out.append(LIVE_INDEX)
        return [p.as_posix() for p in out]

    # ---- inline text ----
    def n(self, text):
        for key, value in self.counts.items():
            text = text.replace("{" + key + "}", str(value))
        return text

    def url(self, target):
        """(href, external) for a link target in the inline syntax."""
        if target.startswith(("https://", "http://")):
            return target, True
        if target.startswith("#"):
            return target, False
        if target.startswith("/"):
            path = target.split("#", 1)[0]
            if path in LIVE_FILES:
                return target, False
            return self.base + target[1:], False
        return BLOB + target, True

    def link(self, label_html, target):
        href, external = self.url(target)
        if external:
            return (f'<a href="{attr(href)}" target="_blank" rel="noopener noreferrer">'
                    f'{label_html}{NEWTAB}</a>')
        return f'<a href="{attr(href)}">{label_html}</a>'

    def inline(self, text, autolink=False):
        text = self.n(text)
        out, pos = [], 0
        for m in INLINE.finditer(text):
            code, label, target, em, bare = m.groups()
            if bare is not None and not autolink:
                continue
            out.append(esc(text[pos:m.start()]))
            if code is not None:
                out.append(f"<code>{esc(code)}</code>")
            elif label is not None:
                inner = (f"<code>{esc(label[1:-1])}</code>"
                         if label.startswith("`") and label.endswith("`") else esc(label))
                out.append(self.link(inner, target))
            elif em is not None:
                out.append(f"<em>{esc(em)}</em>")
            else:
                out.append(self.link(esc(bare), bare))
            pos = m.end()
        out.append(esc(text[pos:]))
        return "".join(out)

    # ---- page parts ----
    def head(self, title, scripts=(), noindex=True):
        b = self.base
        parts = ["<!doctype html>", '<html lang="en" class="site-secureconfig">', "<head>",
                 '<meta charset="utf-8">',
                 '<meta name="viewport" content="width=device-width, initial-scale=1">']
        if noindex:
            parts.append('<meta name="robots" content="noindex, nofollow">')
        parts += [f"<title>{esc(title)} | SecureConfig.ai</title>",
                  f'<link rel="icon" href="{b}assets/baseline/logos/secureconfig-favicon.svg" '
                  f'type="image/svg+xml">',
                  f'<link rel="apple-touch-icon" href="{b}assets/baseline/logos/secureconfig-touch.png">',
                  f'<link rel="stylesheet" href="{b}assets/baseline/fonts.css">',
                  f'<link rel="stylesheet" href="{b}assets/baseline/palettes.css">',
                  f'<link rel="stylesheet" href="{b}assets/baseline/baseline.css">']
        parts += [f'<script src="{b}assets/baseline/{s}" defer></script>' for s in scripts]
        parts += ["</head>", "<body>", '<a class="skip" href="#main-content">Skip to content</a>']
        return "\n".join(parts)

    def mast(self, current):
        b = self.base
        items = []
        for label, path in NAV:
            cur = ' aria-current="page"' if path == current else ""
            items.append(f'<a href="{b}{path}"{cur}>{esc(label)}</a>')
        items.append(f'<a href="{REPO}" target="_blank" rel="noopener noreferrer">GitHub{NEWTAB}</a>')
        return (f'<header class="mast"><a class="brand" href="{b}"><span class="name">SecureConfig'
                f'<span class="tld">.ai</span></span><span class="rule" aria-hidden="true"></span>'
                f'</a><nav class="nav" aria-label="Site">{"".join(items)}</nav></header>')

    def footer(self):
        b = self.base
        cards = []
        for i, (slug, name, href) in enumerate(FAMILY, 1):
            img = f'<img src="{b}assets/baseline/logos/{slug}.svg" alt="">'
            cname = f'<span class="cname">{name}<span class="tld">.ai</span></span>'
            if href is None:
                cards.append(f'<li class="slice slice-{i}"><a class="card" href="{b}" '
                             f'aria-current="page">{img}{cname}<span class="vh"> (this site)</span>'
                             f'</a></li>')
            else:
                cards.append(f'<li class="slice slice-{i}"><a class="card" href="{href}" '
                             f'target="_blank" rel="noopener noreferrer">{img}{cname}{NEWTAB}</a></li>')
        m = f"{b}assets/baseline/marks/"
        ext = 'target="_blank" rel="noopener noreferrer"'
        tail = (f'<li class="tile tile-1"><a class="card" href="https://github.com/jposluns" {ext}>'
                f'<img class="only-light" src="{m}github-invertocat-black.svg" alt="">'
                f'<img class="only-dark" src="{m}github-invertocat-white.svg" alt="">'
                f'<span class="cname vh">GitHub</span>{NEWTAB}</a></li>'
                f'<li class="tile tile-2"><a class="card" href="https://www.linkedin.com/in/jposluns/" '
                f'{ext}><img src="{m}linkedin-in-bug.png" alt=""><span class="cname vh">LinkedIn</span>'
                f'{NEWTAB}</a></li>'
                f'<li class="tile tile-3"><a class="card" href="https://orcid.org/0009-0000-7775-2233" '
                f'{ext}><img src="{m}orcid-id.svg" alt=""><span class="cname vh">ORCID</span>'
                f'{NEWTAB}</a></li>')
        sig = (f'<div class="tile sigtile"><a class="sig" href="https://posluns.ca/" {ext} '
               f'aria-label="A Jeff at Posluns dot ca project: posluns.ca (opens in a new tab)">'
               f'<span class="pre">A </span>Jeff<span class="gold">@</span>Posluns'
               f'<span class="gold">.ca</span><span class="post"> Project</span></a></div>')
        return (f'<footer class="family wrap"><div class="bar"><ul class="cards rainbow" '
                f'aria-label="The 6 project sites">{"".join(cards)}</ul><ul class="tail" '
                f'aria-label="Jeff Posluns elsewhere">{tail}</ul>{sig}</div></footer>\n'
                f'<p class="vh" id="copy-status" role="status" aria-live="polite"></p>\n'
                f"</body>\n</html>\n")

    def page(self, title, current, main, scripts=(), noindex=True):
        return (self.head(title, scripts, noindex) + "\n" + self.mast(current) + "\n"
                + '<main id="main-content">\n' + main + "\n</main>\n" + self.footer())

    def logo(self):
        return f'<img class="rail-logo" src="{self.base}assets/baseline/logos/secureconfig.svg" alt="{LOGO_ALT}">'

    def rail(self, sections=None):
        if not sections:
            return f'<div class="rail">{self.logo()}</div>'
        items = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in sections)
        return (f'<nav class="rail" aria-label="On this page">{self.logo()}'
                f'<p class="lbl">On this page</p><ol>{items}</ol></nav>')

    def next_block(self, nxt):
        line = f'<p>{self.inline(nxt["line"])}</p>' if nxt.get("line") else ""
        href, _ = self.url(nxt["href"])
        return (f'<div class="next"><p class="lbl">Next</p>{line}<a class="start" href="{attr(href)}">'
                f'{esc(nxt["text"])} <span class="arrow" aria-hidden="true">&rarr;</span></a></div>')

    def doc(self, label, h1, rail, body):
        return (f'<div class="wrap"><div class="doc"><p class="lbl first">{esc(label)}</p>\n'
                f"<h1>{esc(h1)}</h1>\n{rail}\n" + "\n".join(body) + "\n</div></div>")

    @staticmethod
    def figures(items):
        figs = "".join(f'<div class="fig"><span class="num">{n}</span><span class="cap">{esc(c)}</span></div>'
                       for n, c in items)
        return f'<div class="wide"><div class="figures">{figs}</div></div>'

    def copyblock(self, pid, text):
        return (f'<pre id="{pid}" class="hascopy"><button class="copy" type="button" '
                f'data-copy="{pid}" hidden>Copy</button>{esc(text)}</pre>')

    # ---- pages ----
    def home(self):
        h = self.c["home"]
        tiles = "".join(
            f'<li><a href="{attr(self.url(t["href"])[0])}"><span class="t">{esc(t["title"])}</span>'
            f'<span class="n">{esc(self.n(t["meta"]))}</span><span class="d">{self.inline(t["desc"])}'
            f"</span></a></li>" for t in h["tiles"])
        start, _ = self.url(h["start"]["href"])
        # SPECIFICATION 7.24: the links separated by hidden-from-reading middle dots.
        about = '<span class="dot" aria-hidden="true">&middot;</span>'.join(
            self.inline(link) for link in h["about"]["links"])
        main = (f'<div class="wrap"><section class="hero" aria-label="Introduction"><div class="hero-text">'
                f'<p class="lbl gold">{self.inline(h["kicker"]["text"])}</p>'
                f'<h1 class="statement">{self.inline(h["statement"]["text"])}</h1>'
                f'<p class="intro">{self.inline(h["intro"]["text"])}</p>'
                f'<a class="start" href="{attr(start)}">{esc(h["start"]["text"])} '
                f'<span class="arrow" aria-hidden="true">&rarr;</span></a></div>'
                f'<div class="hero-art"><img src="{self.base}assets/baseline/logos/secureconfig.svg" '
                f'alt="{LOGO_ALT}"></div></section>'
                f'<div class="region"><p class="lbl">Start here</p><div><ol class="entries">{tiles}'
                f'</ol></div></div><div class="region"><p class="lbl">What it gives you</p><div>'
                f'<p class="value">{self.inline(h["value"]["text"])}</p></div></div>'
                f'<div class="region"><p class="lbl">About this project</p><div>'
                f'<p class="about">{about}</p></div></div></div>')
        return self.page("Home", "", main, noindex=self.base != "/")

    def guides(self):
        g = self.c["guides"]
        k = self.counts
        jump = "\n".join(f'<li><a href="#cat-{i}">{esc(name)}</a><span class="n">{len(rows)}</span></li>'
                         for i, (name, rows) in enumerate(self.categories, 1))
        body = [f'<p class="meta">{self.inline(g["meta"]["text"])}</p>',
                '<p class="lbl blk">Scope</p>', f'<p>{self.inline(g["scope"]["text"])}</p>',
                '<p class="lbl blk">At a glance</p>',
                self.figures(((k["guides"], "guides"), (k["categories"], "categories"),
                              (k["checks"], "verification checks"))),
                '<p class="lbl blk">Categories</p>',
                f'<div class="wide"><ul class="plan three">\n{jump}\n</ul></div>']
        for i, (name, rows) in enumerate(self.categories, 1):
            items = "\n".join(
                f'<li><a href="{BLOB}{slug}.md" target="_blank" rel="noopener noreferrer">{slug}'
                f"{NEWTAB}</a><small>{self.inline(covers)}</small></li>" for slug, covers in rows)
            body += [f'<p class="lbl sec">{len(rows)} guide{"" if len(rows) == 1 else "s"}</p>',
                     f'<h2 id="cat-{i}">{esc(name)}</h2>',
                     f'<div class="wide"><ul class="plan described">\n{items}\n</ul></div>']
        refs = "\n".join(f'<li>{self.inline(r["text"])}<span class="n">{esc(r["n"])}</span></li>'
                         for r in g["reference"])
        body += ['<p class="lbl sec">Reference</p>', '<h2 id="reference">Reference files</h2>',
                 f'<div class="wide"><ul class="plan">\n{refs}\n</ul></div>', self.next_block(g["next"])]
        title = f'{k["guides"]} guides in {k["categories"]} categories'
        return self.page("Guides", "guides/", self.doc("Guide index", title, self.rail(), body))

    def for_ai(self):
        a = self.c["for_ai"]
        rules = "".join(f"<li><span>{self.inline(r, autolink=True)}</span></li>" for r in self.rules)
        body = [f'<p class="meta">{self.inline(a["meta"]["text"])}</p>',
                '<p class="lbl accent blk">Note</p>',
                f'<div class="callout"><p>{self.inline(a["note"]["text"])}</p></div>',
                f'<p class="lbl sec">The {self.counts["rules"]} rules</p>',
                f'<h2 id="rules">The {self.counts["rules"]} rules</h2>',
                f'<div class="wide"><ol class="steps">{rules}</ol></div>',
                '<p class="lbl sec">Fetch</p>', '<h2 id="fetch">Fetch the guides</h2>',
                f'<p>{self.inline(a["fetch"]["text"])}</p>', '<p class="lbl blk">Pattern</p>',
                self.copyblock("raw-pattern", a["pattern"]),
                f'<p>{self.inline(a["files"]["text"])}</p>', self.next_block(a["next"])]
        return self.page("For AI assistants", "for-ai/",
                         self.doc("For AI assistants", a["h1"]["text"], self.rail(), body),
                         scripts=("copy.js",))

    def for_humans(self):
        f = self.c["for_humans"]
        k = self.counts
        tasks = f["tasks"]
        body = [f'<p class="meta">{self.inline(f["meta"]["text"])}</p>',
                '<p class="lbl blk">At a glance</p>',
                self.figures(((k["tasks"], "tasks"), (k["checklist_tasks"], "run the checklist"),
                              (k["approval_tasks"], "wait for your approval")))]
        for i, t in enumerate(tasks, 1):
            body += [f'<p class="lbl sec">Task {i}</p>', f'<h2 id="task-{i}">{esc(t["title"])}</h2>',
                     '<p class="lbl blk">Prompt</p>', self.copyblock(t["id"], t["prompt"])]
        body.append(self.next_block(f["next"]))
        rail = self.rail([(f"task-{i}", t["title"]) for i, t in enumerate(tasks, 1)])
        return self.page("For humans", "for-humans/",
                         self.doc("For humans", "Ready-made tasks for your assistant", rail, body),
                         scripts=("copy.js", "rail.js"))

    def checklist(self):
        c = self.c["checklist"]
        rows = []
        for i, r in enumerate(c["rows"], 1):
            how = f"<code>{esc(r['code'])}</code>" if "code" in r else self.inline(r["method"])
            rows.append(f'<tr><td class="num">{i}</td><td>{self.inline(r["check"])}</td><td>{how}</td></tr>')
        table = (f'<div class="wide"><div class="tablewrap" tabindex="0"><table><caption class="vh">'
                 f"Verification checklist</caption><thead><tr><th>No.</th><th>Check</th>"
                 f"<th>Command or method</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
                 f"</div></div>")
        n = self.counts["checks"]
        body = [f'<p class="meta">{self.inline(c["meta"]["text"])}</p>',
                '<p class="lbl blk">Scope</p>', f'<p>{self.inline(c["scope"]["text"])}</p>',
                '<p class="lbl accent blk">Rule</p>',
                f'<div class="callout rule"><p>{self.inline(c["rule"]["text"])}</p></div>',
                f'<p class="lbl blk">Checklist, {n} items</p>', table,
                f'<p>{self.inline(c["sources"]["text"])}</p>', self.next_block(c["next"])]
        return self.page("Checklist", "checklist/",
                         self.doc("Verification checklist", f"{n} checks before reporting completion",
                                  self.rail(), body))

    def disclosure(self):
        d = self.c["disclosure"]
        body = [f'<p class="meta">{self.inline(d["meta"]["text"])}</p>']
        for i, e in enumerate(d["entries"], 1):
            ev = " ".join(self.link(esc(label), target) for label, target in e["evidence"])
            body += [f'<p class="lbl sec">Entry {i}</p>', f'<h2 id="{e["id"]}">{esc(e["title"])}</h2>',
                     f'<p><strong>Claim:</strong> {self.inline(e["claim"])}</p>',
                     f'<p><strong>Limitation:</strong> {self.inline(e["limitation"])}</p>',
                     f"<p><strong>Evidence:</strong> {ev}</p>"]
        body += ['<p class="lbl blk">Security</p>', f'<p>{self.inline(d["security"]["text"])}</p>',
                 self.next_block(d["next"])]
        rail = self.rail([(e["id"], e["title"]) for e in d["entries"]])
        return self.page("Disclosure", "disclosure/", self.doc("Disclosure", "Disclosure", rail, body),
                         scripts=("rail.js",))

    def license(self):
        lic = self.c["license"]
        parts = "".join(f"<li>{self.inline(p['text'])}</li>" for p in lic["parts"])
        summary = [f"<p>{self.inline(p['text'])}</p>" for p in lic["cc0"]]
        summary.append("<h3>The Apache-licensed AIQT material</h3>")
        for p in lic["apache"]:
            if "list" in p:
                summary.append("<ul>" + "".join(f"<li>{self.inline(x)}</li>" for x in p["list"]) + "</ul>")
            else:
                summary.append(f"<p>{self.inline(p['text'])}</p>")
        summary.append("<h3>The fonts under the SIL Open Font License</h3>")
        summary += [f"<p>{self.inline(p['text'])}</p>" for p in lic["ofl"]]
        body = [f'<p class="meta">{self.inline(lic["meta"]["text"])}</p>',
                '<p class="lbl blk">The licence</p>', f'<p>{self.inline(lic["scope"]["text"])}</p>',
                '<p class="lbl sec">Parts</p>', "<h2>Parts under a different licence</h2>",
                f"<ul>{parts}</ul>", '<p class="lbl sec">In plain language</p>', "<h2>What you may do</h2>",
                "".join(summary), f'<p>{esc(lic["governs"]["text"])}</p>',
                '<p class="lbl accent blk">Note</p>',
                f'<div class="callout"><p>{esc(lic["note"]["text"])}</p></div>', self.next_block(lic["next"])]
        return self.page("Licence", "license/", self.doc("Licence", "CC0 1.0 Universal", self.rail(), body))

    def notfound(self):
        nf = self.c["notfound"]
        body = [f'<p class="lead">{self.inline(nf["lead"]["text"])}</p>', self.next_block(nf["next"])]
        return self.page("Page not found", "", self.doc("404", "That page is not here.", self.rail(), body))

    def build(self):
        pages = {"index.html": self.home(), "guides/index.html": self.guides(),
                 "for-ai/index.html": self.for_ai(), "for-humans/index.html": self.for_humans(),
                 "checklist/index.html": self.checklist(), "disclosure/index.html": self.disclosure(),
                 "license/index.html": self.license(), "404.html": self.notfound()}
        for name, text in pages.items():
            refuse(name, text)
        return pages


def refuse(name, text):
    """Raise Refused when a page carries what SPECIFICATION section 12 forbids."""
    why = []
    if any(d in text for d in DASHES):
        why.append("an en or em dash")
    if re.search(r"<style\b", text, re.I) or STYLE_ATTR.search(text):
        why.append("an inline style or style= attribute")
    for m in SCRIPT_TAG.finditer(text):
        if "src=" not in m.group(1) or m.group(2).strip():
            why.append("an inline script")
    if len(re.findall(r"<script\b", text, re.I)) != len(SCRIPT_TAG.findall(text)):
        why.append("an unclosed or unparsed <script>")
    if VALUED_HANDLER.search(text) or re.search(r"<[a-z][^>]*\son[a-z-]*[\s>/=]", text, re.I):
        why.append("an on* attribute")
    if FRAMING.search(re.sub(r"<[^>]+>", " ", text)):
        why.append('"what this is" framing')
    # SPECIFICATION 1.3 section 7.6: a rail that lists sections loads rail.js, and no rail link
    # carries aria-current in the markup (the script marks the reader's section).
    rail = re.search(r'<nav class="rail".*?</nav>', text, re.S)
    if rail and "aria-current" in rail.group(0):
        why.append("a static aria-current on a rail link")
    if rail and 'assets/baseline/rail.js" defer></script>' not in text:
        why.append("a section rail without rail.js")
    if why:
        raise Refused(f"{name} would contain " + ", ".join(why))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="/draft/")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--list-inputs", action="store_true")
    args = ap.parse_args(argv)
    try:
        b = Builder(args.base)
        if args.list_inputs:
            print("\n".join(b.inputs()))
            return 0
        pages = b.build()
    except SourceError as exc:
        print(f"  FAIL  {exc}")
        return 2
    except Refused as exc:
        print(f"  FAIL  refused: {exc}")
        return 1
    out = args.out or Path("site") / args.base.lstrip("/")
    out = out if out.is_absolute() else ROOT / out
    if args.check:
        problems = []
        for name, text in pages.items():
            path = out / name
            try:
                if path.read_bytes() != text.encode("utf-8"):
                    problems.append(f"{name} differs from a fresh build")
            except FileNotFoundError:
                problems.append(f"{name} is missing")
            except OSError as exc:
                print(f"  FAIL  cannot read {path}: {exc}")
                return 2
        # Every file under the output folder is a page this build writes, or a copied template file
        # under assets/baseline/ (scripts/copy-baseline.py, pinned by tools/check_baseline_pin.py).
        # A page is .html or .htm in any case, read as the CSP gate reads one (name_suffix). At the
        # root after promotion the folder also holds the live files, so only pages are compared.
        if out.is_dir():
            for path in sorted(p for p in out.rglob("*") if not p.is_dir()):
                rel = path.relative_to(out).as_posix()
                if rel in pages or rel.startswith(COPIED):
                    continue
                if name_suffix(path.name) in (".html", ".htm"):
                    problems.append(f"{rel} is not a page this build writes")
                elif args.base != "/":
                    problems.append(f"{rel} is neither a page this build writes nor a copied "
                                    f"template file under {COPIED}")
        if problems:
            for p in problems:
                print(f"  FAIL  {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}/{p}; "
                      f"rerun python3 -I -B scripts/build-site.py")
            return 1
        print(f"  ok    the {len(pages)} pages under {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} "
              f"match a fresh build (base {args.base})")
        return 0
    for name, text in pages.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    print(f"  ok    wrote {len(pages)} pages under {out} (base {args.base})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
