#!/usr/bin/env python3
"""Build the secureconfig.ai pages on the shared site template (baseline 1.12.4).

Usage:
  python3 -I -B scripts/build-site.py                 write the pages under site/
  python3 -I -B scripts/build-site.py --check         build in memory and compare; write nothing
  python3 -I -B scripts/build-site.py --list-inputs   print the files the build reads
  python3 -I -B scripts/build-site.py --base /draft/ --out site/draft   the staging form

Every page is generated from this repository's sources with the markup of the baseline's reference
pages (SPECIFICATION.md section 7): README.md for the guide index, the 10 rules and the checklist
count, and the Claude Code install commands on the For AI assistants page; site-src/content.json
for the page copy, each entry with its source; and
tools/version_basis_guides.txt for 1 count on the Disclosure page. Counts are computed, so a new
guide or rule makes `--check` report the pages stale. Internal links and assets take the base path
(`/` since promotion; `/draft/` builds the staging form). The live site carries no /draft/ page
(baseline 1.11.0 onward, SPECIFICATION.md section 4.1 items 0 and 3): a draft for review is
built on the `draft` branch with `--base /draft/ --out site/draft`, which Cloudflare Pages deploys
at https://draft.secureconfig.pages.dev, so the owner reviews
https://draft.secureconfig.pages.dev/draft/, and `main` never carries site/draft/. The root build
writes no page under draft/, and its `--check` refuses any file there. A staged build is noindex
everywhere and carries no canonical or link previews. At the root base every page is indexable
except the 404 page and the unlisted advisory advisories/n8n-2026-11-07-jposluns.html, which are
noindex and carry no canonical, description or link previews. The build also writes that
advisory's plain-text copy, advisories/n8n-2026-11-07-jposluns.txt (Builder.texts), with no
HTML and no Markdown, for attaching to a report; it carries the same facts and labels as the
page. Each indexable page carries its description, its
canonical URL and the Open Graph (og:site_name after og:type) and Twitter link-preview tags with
the card at images/secureconfig-card.png (as on auditthis.ai). Every page, the 404 included, carries the light
and dark switch as the last child of the top bar, after its `nav`, and loads scheme.js in
`<head>` before the stylesheets, without `defer` or `async` (SPECIFICATION.md section 7.33).

The install commands have 1 source, README.md's "Install in Claude Code" section, so
site-src/content.json carries none of them. The build reads that section with install_blocks()
below, a small standard-library fence reader, not a Markdown parser. The section must hold exactly
2 fenced blocks, each opened at the start of a line and closed by a fence of the same character
and length: first the in-session block, info string `text`, every line starting `/plugin `; then
the shell block, info string `bash`, every line starting `claude plugin `. Anything else is
refused (exit 2), and so is a README with no such section or more than 1. The reader does not
know HTML comments, indented code blocks, lists or block quotes, so tools/check_install_blocks.py,
a CI gate, reads the same section with the pinned CommonMark parser and fails unless the parser
finds exactly the 2 blocks this reader extracted, at the same lines, with the same content.

The build refuses to write, and `--check` fails, when a page would contain a dash character
(U+2010 to U+2015, U+2212), an inline style or `style=` attribute, a `<script>` without `src` or
with a body, an `on*` attribute, or "what this is" framing (SPECIFICATION.md section 12). An
`on*` attribute is any `on...=` text (the CSP gate's VALUED_HANDLER) or an attribute name in a tag
that begins with "on" after whitespace; a word inside a closed quoted attribute value is not a
name, so a description may say "read on GitHub". It does not write the copied baseline files
under assets/baseline/ (scripts/copy-baseline.py does).
The plain-text copy is refused when it would contain one of those dash characters, "what this is"
framing, a backtick, a Markdown link, a character reference such as `&lt;`, or a tag of the
markup the pages use.
`--check` compares every page and plain-text copy it writes with the file on disk, byte for byte,
and also fails on any other file under the output folder outside assets/baseline/ and the optional
assets/site.css:
an extra page (a .html or .htm file in any case, as the CSP gate names one) at any base, and any
other file except, at base `/` only, the published files the root holds beside the pages
(PUBLISHED: llms.txt, llms-full.txt, robots.txt, sitemap.xml, _headers, .well-known/security.txt,
favicon.svg, favicon.ico, apple-touch-icon.png and images/secureconfig-card.png). A new published
file is added to PUBLISHED before it ships.

Exit status: 0 on success (or no difference), 1 on a refusal or a difference, 2 on a read error
or a source the build cannot read as it needs.
Standard library only, because scripts/pages-build.sh runs `--check` on Cloudflare Pages, needs
only bash and Python, and installs nothing. No network.
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
QUALITY_TSV = Path("tools") / "guide_quality.tsv"
# The README section that is the only source of the install commands on the For AI assistants
# page, and its 2 fenced blocks in order: (key, info string, the start of every line).
INSTALL = "## Install in Claude Code"
INSTALL_FENCES = (("session", "text", "/plugin "), ("shell", "bash", "claude plugin "))
COPIED = "assets/baseline/"  # the copied template files, which this build does not write
SITE_CSS = "assets/site.css"  # the optional per-site constants file (baseline README), hand-written
# The files the root holds beside the pages and the copied template files; a root --check refuses
# every other file, so a stray file cannot ship unnoticed.
PUBLISHED = (".well-known/security.txt", "_headers", "apple-touch-icon.png", "favicon.ico",
             "favicon.svg", "images/secureconfig-card.png", "llms-full.txt", "llms.txt", "robots.txt",
             "sitemap.xml")
# The unlisted n8n advisory (the maintainer's instruction of 2026-11-07: a dated name) and its
# plain-text copy. tools/check_draft.py admits the page as noindex with no canonical by this exact
# path, and the overflow page list in tools/run_all_checks.sh names it.
ADVISORY_PAGE = "advisories/n8n-2026-11-07-jposluns.html"
ADVISORY_TEXT = "advisories/n8n-2026-11-07-jposluns.txt"
REPO = "https://github.com/jposluns/secureconfig"
BLOB = REPO + "/blob/main/"
ORIGIN = "https://secureconfig.ai"
LOGO_ALT = "A terminal window with a padlock and a small shield"
# The link-preview card the live home page carried before promotion (1200 by 630 PNG).
CARD = ORIGIN + "/images/secureconfig-card.png"
CARD_ALT = "SecureConfig.ai: The secure option at every decision. TLS, identity, MFA, secrets, network."
NEWTAB = '<span class="vh"> (opens in a new tab)</span>'
# The light and dark switch of SPECIFICATION 7.33, as the baseline's reference pages write it: the
# 2 glyphs in inline SVG with presentation attributes only, hidden until scheme.js reveals it.
GLYPH = ('viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
         'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
         'focusable="false"')
SWITCH = ('<button class="scheme" type="button" data-scheme-toggle aria-pressed="false" hidden>'
          f'<svg class="moon" {GLYPH}><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 '
          '10.7 10.7z"/></svg>'
          f'<svg class="sun" {GLYPH}><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 '
          '19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 '
          '6.9l1.6-1.6"/></svg><span class="vh">Dark mode</span></button>')
# The site's own pages, then GitHub last (the owner's template note of 2026-11-03): Disclosure and
# Licence are linked from the landing page's "About this project" region, not the top bar.
NAV = (("Guides", "guides/"), ("For AI assistants", "for-ai/"), ("For humans", "for-humans/"),
       ("Checklist", "checklist/"))
FAMILY = (("secureconfig", "SecureConfig", None), ("opfiles", "OPFiles", "https://opfiles.ai/"),
          ("auditthis", "AuditThis", "https://auditthis.ai/"),
          ("cleanlanguage", "CleanLanguage", "https://cleanlanguage.ai/"),
          ("aiqt", "AIQT", "https://aiqt.ai/"), ("grclibrary", "GRCLibrary", "https://grclibrary.ai/"))
INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)|\*([^*]+)\*|(https?://[^\s)]+[^\s).,;:])")
# Every dash the writing rules exclude: hyphen and non-breaking hyphen (U+2010, U+2011), figure dash,
# en and em dash (U+2012 to U+2014), horizontal bar (U+2015) and the minus sign (U+2212), which the
# pages never need (quantities use digits and words). README and content.json carry none of them.
DASHES = tuple(chr(c) for c in range(0x2010, 0x2016)) + ("\u2212",)
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.I | re.S)
FRAMING = re.compile(r"what\s+this\s+is", re.I)
# An on* attribute: whitespace in a tag, then a name that begins with "on". It is matched against
# each tag with its closed quoted values blanked (blank_values), so a word in a value is not a name.
ON_ATTR = re.compile(r"<[a-z][^>]*\son[a-z-]*[\s>/=]", re.I)
TAG_START = re.compile(r"<[a-z]", re.I)
HTML_SPACE = "\t\n\f\r "  # HTML's whitespace (a CR reaches the tokenizer as a line feed)


class Refused(Exception):
    """A page the build will not write."""


class SourceError(Exception):
    """A source file is missing or not in the shape the build reads."""


# A fence line as install_blocks() reads one: 3 or more backticks or tildes at the start of the
# line, then the rest of the line (the info string, on an opening fence).
FENCE = re.compile(r"(`{3,}|~{3,})(.*)")
# A level-1 or level-2 ATX heading at the start of a line, which ends the install section.
SECTION_END = re.compile(r"#{1,2}(?:[ \t]|$)")
# A fence indented by spaces or tabs, which install_blocks() refuses rather than reads.
INDENTED_FENCE = re.compile(r"[ \t]+(?:`{3}|~{3})")


def install_blocks(text):
    """[(key, line, commands)] for INSTALL_FENCES, in order, read from README.md's install
    section; line is the 1-based line of the block's opening fence. SourceError for anything else.

    This reader is deliberately simple, because the Cloudflare Pages build (scripts/pages-build.sh)
    runs this script, needs only bash and Python, and installs nothing. It reads lines,
    as CommonMark splits them (at \\n, \\r\\n or a lone \\r). The section runs from the 1 line that
    reads INSTALL, trailing spaces or tabs aside, to the next line, outside a fence, that starts a
    level-1 or level-2 ATX heading. A fence opens at the start of a line with 3 or more backticks or
    tildes. The first later line made only of that character, at least as long, with any spaces or
    tabs around it, ends the fence, and the build refuses it unless it is the opening run exactly,
    at the start of the line. A fence
    never closed, and a fence indented by spaces or tabs in the section, are refused. It does not
    know HTML comments, indented code blocks, setext headings, lists or block quotes, so it can read
    a block that CommonMark hides or miss one that CommonMark shows: tools/check_install_blocks.py
    reads the same section with the pinned parser in CI and fails unless both readings agree."""
    where = f"{README} section {INSTALL!r}"
    want = " then ".join(f"a `{info}` block of `{prefix.strip()}` lines"
                         for _, info, prefix in INSTALL_FENCES)
    lines = re.split(r"\r\n?|\n", text)
    heads = [i for i, line in enumerate(lines) if line.rstrip(" \t") == INSTALL]
    if len(heads) != 1:
        raise SourceError(f"{README} has {len(heads)} lines {INSTALL!r}; the build reads the "
                          f"install commands from exactly 1 such section")
    found, i = [], heads[0] + 1
    while i < len(lines) and not SECTION_END.match(lines[i]):
        if INDENTED_FENCE.match(lines[i]):
            raise SourceError(f"{where}: line {i + 1} is an indented fence; the build reads only "
                              f"fences at the start of a line and needs {want}")
        opening = FENCE.fullmatch(lines[i])
        if not opening:
            i += 1
            continue
        run, info, start, body = opening[1], opening[2].strip(), i, []
        i += 1
        while i < len(lines):
            bare = lines[i].strip(" \t")
            if len(bare) >= len(run) and set(bare) == {run[0]}:
                break  # CommonMark closes the fence here
            body.append(lines[i])
            i += 1
        if i == len(lines) or lines[i].rstrip(" \t") != run:
            raise SourceError(f"{where}: the fence {run!r} at line {start + 1} is not closed by a "
                              f"fence of the same character and length; the build needs {want}")
        found.append((start + 1, info, "\n".join(body)))
        i += 1
    if len(found) != len(INSTALL_FENCES):
        raise SourceError(f"{where} holds {len(found)} fenced block"
                          f"{'' if len(found) == 1 else 's'}; the build needs exactly "
                          f"{len(INSTALL_FENCES)}: {want}")
    blocks = []
    for n, ((line, info, body), (key, need, prefix)) in enumerate(zip(found, INSTALL_FENCES), 1):
        if info != need or not body or not all(b.startswith(prefix) for b in body.split("\n")):
            raise SourceError(f"{where}: fenced block {n} (line {line}) does not have info string "
                              f"{need!r} and every line starting {prefix!r}; the build needs {want}")
        blocks.append((key, line, body))
    return blocks


def esc(text):
    return html.escape(text, quote=False)


def attr(text):
    return html.escape(text, quote=True)


class Builder:
    def __init__(self, base, root=ROOT):
        if not (base.startswith("/") and base.endswith("/")):
            raise SourceError(f"--base must start and end with /, not {base!r}")
        self.base = base
        self.staged = base != "/"  # a staged build is noindex everywhere; the root build is not
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
        readme = self.read(README)
        lines = readme.splitlines()
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
        self.install = {key: body for key, _, body in install_blocks(readme)}

    def inputs(self):
        return [p.as_posix() for p in (CONTENT, README, VERSIONED, QUALITY_TSV)]

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

    def plain(self, text):
        """The inline syntax as plain text, for the advisory's plain-text copy: code without its
        backticks, emphasis without its asterisks, and a link as its label followed by its URL in
        parentheses, a root-relative one made absolute on this site's origin. Nothing is
        HTML-escaped."""
        text = self.n(text)
        out, pos = [], 0
        for m in INLINE.finditer(text):
            code, label, target, em, bare = m.groups()
            if bare is not None:
                continue
            out.append(text[pos:m.start()])
            if code is not None:
                out.append(code)
            elif label is not None:
                href = ORIGIN + target if target.startswith("/") else self.url(target)[0]
                out.append(f"{label.strip('`')} ({href})")
            else:
                out.append(em)
            pos = m.end()
        out.append(text[pos:])
        return "".join(out)

    # ---- page parts ----
    def indexable(self, key, path):
        """The head of an indexable page: at the root, its description, canonical URL and link
        previews; a staged build is noindex everywhere and carries none of them."""
        if self.staged:
            return {"noindex": True}
        return {"noindex": False, "description": self.n(self.c[key]["description"]["text"]),
                "canonical": f"{ORIGIN}/{path}", "preview": True}

    def head(self, title, scripts=(), noindex=True, description=None, canonical=None, preview=False):
        b = self.base
        parts = ["<!doctype html>", '<html lang="en" class="site-secureconfig">', "<head>",
                 '<meta charset="utf-8">',
                 '<meta name="viewport" content="width=device-width, initial-scale=1">']
        if noindex:
            parts.append('<meta name="robots" content="noindex, nofollow">')
        parts.append(f"<title>{esc(title)} | SecureConfig.ai</title>")
        if description is not None:
            parts.append(f'<meta name="description" content="{attr(description)}">')
        if preview:
            # The link-preview tags auditthis.ai carries on each indexable page, after the
            # description; og:site_name follows og:type, as auditthis.ai orders it.
            full = f"{title} | SecureConfig.ai"
            og = (("og:type", "website"), ("og:site_name", "SecureConfig.ai"), ("og:url", canonical),
                  ("og:title", full),
                  ("og:description", description), ("og:image", CARD), ("og:image:type", "image/png"),
                  ("og:image:width", "1200"), ("og:image:height", "630"), ("og:image:alt", CARD_ALT))
            tw = (("twitter:card", "summary_large_image"), ("twitter:title", full),
                  ("twitter:description", description), ("twitter:image", CARD),
                  ("twitter:image:alt", CARD_ALT))
            parts += [f'<meta property="{k}" content="{attr(v)}">' for k, v in og]
            parts += [f'<meta name="{k}" content="{attr(v)}">' for k, v in tw]
        parts += [f'<link rel="icon" href="{b}assets/baseline/logos/secureconfig-favicon.svg" '
                  f'type="image/svg+xml">',
                  f'<link rel="apple-touch-icon" href="{b}assets/baseline/logos/secureconfig-touch.png">',
                  # SPECIFICATION 7.33: before the stylesheets and without defer, so a stored scheme
                  # applies before the first paint; data-cfasync before src, for Rocket Loader.
                  f'<script data-cfasync="false" src="{b}assets/baseline/scheme.js"></script>',
                  f'<link rel="stylesheet" href="{b}assets/baseline/fonts.css">',
                  f'<link rel="stylesheet" href="{b}assets/baseline/palettes.css">',
                  f'<link rel="stylesheet" href="{b}assets/baseline/baseline.css">']
        if canonical is not None:
            parts.append(f'<link rel="canonical" href="{attr(canonical)}">')
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
                f'</a><nav class="nav" aria-label="Site">{"".join(items)}</nav>{SWITCH}</header>')

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
        # Baseline 1.11.0 (SPECIFICATION 7.19): vendorreplies.ai's card is always the last project
        # card, after the 6 rainbow cards, with its PNG logo.
        cards.append(f'<li class="slice slice-vr"><a class="card" href="https://vendorreplies.ai/" '
                     f'target="_blank" rel="noopener noreferrer">'
                     f'<img src="{b}assets/baseline/logos/vendorreplies.png" alt="">'
                     f'<span class="cname">VendorReplies<span class="tld">.ai</span></span>{NEWTAB}'
                     f'</a></li>')
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
                f'aria-label="The 7 project sites">{"".join(cards)}</ul><ul class="tail" '
                f'aria-label="Jeff Posluns elsewhere">{tail}</ul>{sig}</div></footer>\n'
                f'<p class="vh" id="copy-status" role="status" aria-live="polite"></p>\n'
                f"</body>\n</html>\n")

    def page(self, title, current, main, scripts=(), noindex=True, description=None, canonical=None,
             preview=False):
        return (self.head(title, scripts, noindex, description, canonical, preview) + "\n" + self.mast(current)
                + "\n" + '<main id="main-content">\n' + main + "\n</main>\n" + self.footer())

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
        # SPECIFICATION 7.24: the links separated by hidden-from-reading middle dots, with 1 ordinary
        # space after each dot span and none before it (from 1.7.0), so the line breaks after a dot.
        about = '<span class="dot" aria-hidden="true">&middot;</span> '.join(
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
        return self.page("Home", "", main, **self.indexable("home", ""))

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
        return self.page("Guides", "guides/", self.doc("Guide index", title, self.rail(), body),
                         **self.indexable("guides", "guides/"))

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
                f'<p>{self.inline(a["files"]["text"])}</p>']
        inst = a["install"]
        body += ['<p class="lbl sec">Install</p>',
                 f'<h2 id="install">{esc(inst["h2"]["text"])}</h2>',
                 f'<p>{self.inline(inst["lead"]["text"])}</p>',
                 f'<p>{self.inline(inst["session"]["text"])}</p>',
                 '<p class="lbl blk">In a session</p>',
                 self.copyblock("install-session", self.install["session"]),
                 f'<p>{self.inline(inst["shell"]["text"])}</p>',
                 '<p class="lbl blk">In a shell</p>',
                 self.copyblock("install-shell", self.install["shell"]),
                 f'<p>{self.inline(inst["copy"]["text"])}</p>',
                 f'<p>{self.inline(inst["always"]["text"])}</p>', self.next_block(a["next"])]
        return self.page("For AI assistants", "for-ai/",
                         self.doc("For AI assistants", a["h1"]["text"], self.rail(), body),
                         scripts=("copy.js",), **self.indexable("for_ai", "for-ai/"))

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
                         scripts=("copy.js", "rail.js"), **self.indexable("for_humans", "for-humans/"))

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
                                  self.rail(), body), **self.indexable("checklist", "checklist/"))

    def disclosure(self):
        d = self.c["disclosure"]
        body = [f'<p class="meta">{self.inline(d["meta"]["text"])}</p>']
        for i, e in enumerate(d["entries"], 1):
            ev = " ".join(self.link(esc(label), target) for label, target in e["evidence"])
            body += [f'<p class="lbl sec">Entry {i}</p>', f'<h2 id="{e["id"]}">{esc(e["title"])}</h2>',
                     f'<p><strong>Claim:</strong> {self.inline(e["claim"])}</p>',
                     f'<p><strong>Limitation:</strong> {self.inline(e["limitation"])}</p>',
                     f"<p><strong>Evidence:</strong> {ev}</p>"]
        # SPECIFICATION 7.20 from 1.6.0: "Your browser" (what the light and dark switch stores)
        # comes before the Security paragraph.
        body += ['<p class="lbl blk">Your browser</p>', f'<p>{self.inline(d["browser"]["text"])}</p>',
                 '<p class="lbl blk">Security</p>', f'<p>{self.inline(d["security"]["text"])}</p>',
                 self.next_block(d["next"])]
        rail = self.rail([(e["id"], e["title"]) for e in d["entries"]])
        return self.page("Disclosure", "disclosure/", self.doc("Disclosure", "Disclosure", rail, body),
                         scripts=("rail.js",), **self.indexable("disclosure", "disclosure/"))

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
        return self.page("Licence", "license/", self.doc("Licence", "CC0 1.0 Universal", self.rail(), body),
                         **self.indexable("license", "license/"))

    def notfound(self):
        nf = self.c["notfound"]
        body = [f'<p class="lead">{self.inline(nf["lead"]["text"])}</p>', self.next_block(nf["next"])]
        return self.page("Page not found", "", self.doc("404", "That page is not here.", self.rail(), body))

    def advisory(self):
        # The unlisted n8n security advisory (the maintainer's instruction). Like the 404 page it is
        # noindex, carries no canonical and no link previews (self.page defaults), and no page links
        # it; tools/check_draft.py admits ADVISORY_PAGE as a noindex page by that exact path, and
        # site/_headers sends X-Robots-Tag: noindex for /advisories/*.
        a = self.c["advisory_n8n"]

        def items(key, ordered=False):
            tag = "ol" if ordered else "ul"
            lis = "\n".join(f"<li>{self.inline(x['text'])}</li>" for x in a[key])
            return f"<{tag}>\n{lis}\n</{tag}>"

        body = [f'<p class="lead">{self.inline(a["status"]["text"])}</p>',
                f'<p>{self.inline(a["intro"]["text"])}</p>',
                '<p class="lbl sec">Title</p>', '<h2 id="title">Title</h2>',
                f'<p><strong>Summary:</strong> {self.inline(a["report_summary"]["text"])}</p>',
                f'<p>{self.inline(a["report_title"]["text"])}</p>',
                '<p class="lbl sec">Affected versions</p>', '<h2 id="affected">Affected versions</h2>',
                items("affected"),
                '<p class="lbl sec">Description</p>', '<h2 id="description">Description</h2>',
                '<p class="lbl blk">Vulnerable code locations, observed in source</p>',
                items("locations"),
                '<p class="lbl blk">Read path, observed in source</p>', items("observed"),
                '<p class="lbl blk">Read path, inference</p>', items("inferred"),
                '<p class="lbl blk">Steps a reviewer would take</p>', items("steps", ordered=True),
                '<p class="lbl blk">Proof of concept</p>', f'<p>{self.inline(a["poc"]["text"])}</p>',
                '<p class="lbl blk">Impact</p>', f'<p>{self.inline(a["impact"]["text"])}</p>',
                '<p class="lbl sec">Reporter</p>', '<h2 id="reporter">Reporter</h2>',
                f'<p>{self.inline(a["reporter_note"]["text"])}</p>', items("reporter"),
                '<p class="lbl sec">CVSS 4.0, provisional</p>',
                '<h2 id="cvss">CVSS 4.0, provisional</h2>',
                f'<p>{self.inline(a["cvss_vector"]["text"])}</p>',
                f'<p>{self.inline(a["cvss_derivation"]["text"])}</p>',
                '<p class="lbl sec">Mitigations</p>', '<h2 id="mitigations">Mitigations</h2>',
                items("mitigations")]
        return self.page("Security advisory: n8n", "",
                         self.doc(a["label"]["text"], a["h1"]["text"], self.rail(), body))

    def advisory_text(self):
        # The advisory's plain-text copy, for attaching to a report (the maintainer's instruction
        # of 2026-11-07): the same content.json entries as advisory(), in the same order and under
        # the same labels, with no HTML and no Markdown. Each paragraph or list item is 1 line.
        a = self.c["advisory_n8n"]

        def items(key, ordered=False):
            return [f"{f'{i}.' if ordered else '-'} {self.plain(x['text'])}"
                    for i, x in enumerate(a[key], 1)]

        def section(title, *blocks):
            return [title.upper(), *blocks]

        def sub(label, *lines):
            return [f"{label}:", *lines]

        parts = [
            [f"{a['label']['text']}: n8n"], [self.plain(a["h1"]["text"])],
            [self.plain(a["status"]["text"])], [self.plain(a["intro"]["text"])],
            section("Summary", self.plain(a["report_summary"]["text"])),
            section("Title", self.plain(a["report_title"]["text"])),
            section("Affected versions", *items("affected")),
            section("Description"),
            sub("Vulnerable code locations, observed in source", *items("locations")),
            sub("Read path, observed in source", *items("observed")),
            sub("Read path, inference", *items("inferred")),
            sub("Steps a reviewer would take", *items("steps", ordered=True)),
            sub("Proof of concept", self.plain(a["poc"]["text"])),
            sub("Impact", self.plain(a["impact"]["text"])),
            section("Reporter", self.plain(a["reporter_note"]["text"]), *items("reporter")),
            section("CVSS 4.0, provisional", self.plain(a["cvss_vector"]["text"]),
                    self.plain(a["cvss_derivation"]["text"])),
            section("Mitigations", *items("mitigations")),
        ]
        return "\n\n".join("\n".join(p) for p in parts) + "\n"

    def quality(self):
        # The published view of the GQS 1.0 compliance matrix (QUALITY.md 3.5). It is noindex (the
        # self.page default), carries no canonical or link previews, and is in no menu or sitemap;
        # the standard, the matrix and the ledger are read on GitHub. The matrix is read from
        # tools/guide_quality.tsv with the standard library, so the page is a fresh build of the
        # TSV and a stale page fails --check, as the guide and rule counts already do. The wide
        # matrix sits in the baseline's scrollable table wrapper so the page itself never scrolls
        # sideways at the overflow check's widths.
        q = self.c["quality"]
        rows = []
        verdicts = []
        for line in self.read(QUALITY_TSV).splitlines():
            if line.startswith("#") or not line.strip():
                continue
            f = line.split("\t")
            rows.append((f[0], f[1], f[2:12], f[12]))
            verdicts.append(f[12])
        ladder = ("EXEMPLARY", "SOLID+", "SOLID", "MINOR-GAPS", "NEEDS-WORK")
        counts = {v: verdicts.count(v) for v in ladder}
        groups = ("M", "A", "B", "C", "D", "E", "F", "G", "H", "I")
        head = ("<th>Guide</th><th>Type</th>"
                + "".join(f"<th>{g}</th>" for g in groups) + "<th>Verdict</th>")
        trs = []
        for guide, gtype, cells, verdict in rows:
            tds = (f'<td><code>{esc(guide)}</code></td><td>{esc(gtype)}</td>'
                   + "".join(f"<td>{esc(c)}</td>" for c in cells)
                   + f"<td>{esc(verdict)}</td>")
            trs.append(f"<tr>{tds}</tr>")
        table = (f'<div class="wide"><div class="tablewrap" tabindex="0"><table><caption class="vh">'
                 f"GQS 1.0 compliance matrix</caption><thead><tr>{head}</tr></thead><tbody>"
                 f"{''.join(trs)}</tbody></table></div></div>")
        dist = "".join(f'<li>{esc(v)}<span class="n">{counts[v]}</span></li>' for v in ladder)
        body = [f'<p class="meta">{self.inline(q["meta"]["text"])}</p>',
                '<p class="lbl blk">Scope</p>', f'<p>{self.inline(q["scope"]["text"])}</p>',
                '<p class="lbl blk">At a glance</p>',
                self.figures(((len(rows), "guides scored"), (counts["EXEMPLARY"], "EXEMPLARY"),
                              (counts["SOLID"], "SOLID"), (counts["MINOR-GAPS"], "MINOR-GAPS"))),
                '<p class="lbl blk">Verdict distribution</p>',
                f'<div class="wide"><ul class="plan">\n{dist}\n</ul></div>',
                f'<p class="lbl sec">Matrix</p>', f'<h2 id="matrix">{len(rows)} guides scored</h2>',
                table, f'<p>{self.inline(q["note"]["text"])}</p>']
        return self.page("Quality", "", self.doc("Guide quality", "The Guide Quality Standard",
                                                 self.rail(), body))

    def build(self):
        # No draft/index.html: the live site carries no /draft/ page (SPECIFICATION 4.1 item 0);
        # the `draft` branch stages the whole site under /draft/ with --base /draft/.
        # ADVISORY_PAGE is the one unlisted noindex page beside the 404 (the maintainer's
        # instruction): noindex, no canonical, linked from nowhere, and in no index or menu.
        pages = {"index.html": self.home(), "guides/index.html": self.guides(),
                 "for-ai/index.html": self.for_ai(), "for-humans/index.html": self.for_humans(),
                 "checklist/index.html": self.checklist(), "disclosure/index.html": self.disclosure(),
                 "license/index.html": self.license(), "404.html": self.notfound(),
                 "quality/index.html": self.quality(), ADVISORY_PAGE: self.advisory()}
        for name, text in pages.items():
            refuse(name, text)
        return pages

    def texts(self):
        """The plain-text files the build writes beside the pages, by path, each refused as
        refuse_text() says; build() returns the pages only."""
        texts = {ADVISORY_TEXT: self.advisory_text()}
        for name, text in texts.items():
            refuse_text(name, text)
        return texts


def blank_values(text, start):
    """The tag that opens at `start`, to its `>` (or the end of the text), with the inside of each
    closed quoted attribute value replaced by "x". The tag is read as HTML's tokenizer reads one in
    the data state: a name runs to whitespace, `/`, `>` or `=`, a quote opens a value only after
    `=`, and a `>` inside a quoted value does not end the tag. An unclosed quote is read as the
    start of an unquoted value, so nothing after it is blanked."""
    n = len(text)
    i = start + 1
    while i < n and text[i] not in HTML_SPACE + "/>":
        i += 1  # the tag name
    out = [text[start:i]]
    while i < n and text[i] != ">":
        if text[i] in HTML_SPACE + "/":
            out.append(text[i])
            i += 1
            continue
        k = i + 1  # an attribute name, whose first character may be "="
        while k < n and text[k] not in HTML_SPACE + "/>=":
            k += 1
        while k < n and text[k] in HTML_SPACE:
            k += 1
        if k < n and text[k] == "=":
            k += 1
            while k < n and text[k] in HTML_SPACE:
                k += 1
            close = text.find(text[k], k + 1) if k < n and text[k] in "\"'" else -1
            if close != -1:
                out += [text[i:k + 1], "x" * (close - k - 1), text[close]]
                i = close + 1
                continue
            while k < n and text[k] not in HTML_SPACE + ">":
                k += 1  # an unquoted value
        out.append(text[i:k])
        i = k
    return "".join(out) + text[i:i + 1]


def refuse(name, text):
    """Raise Refused when a page carries what SPECIFICATION section 12 forbids."""
    why = []
    if any(d in text for d in DASHES):
        why.append("a dash character (U+2010 to U+2015 or U+2212)")
    if re.search(r"<style\b", text, re.I) or STYLE_ATTR.search(text):
        why.append("an inline style or style= attribute")
    for m in SCRIPT_TAG.finditer(text):
        if "src=" not in m.group(1) or m.group(2).strip():
            why.append("an inline script")
    if len(re.findall(r"<script\b", text, re.I)) != len(SCRIPT_TAG.findall(text)):
        why.append("an unclosed or unparsed <script>")
    if VALUED_HANDLER.search(text) or any(ON_ATTR.match(blank_values(text, m.start()))
                                          for m in TAG_START.finditer(text)):
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


# A tag of the markup the pages use, and a character reference: neither belongs in a plain-text
# copy. A placeholder such as `<wf>` in a key layout is text, not a tag, so it is not matched.
TEXT_TAG = re.compile(r"</?(?:a|br|code|div|em|h[1-6]|li|ol|p|pre|span|strong|ul)\b[^>]*>", re.I)
CHAR_REF = re.compile(r"&(?:[a-z][a-z0-9]*|#[0-9]+|#x[0-9a-f]+);", re.I)


def refuse_text(name, text):
    """Raise Refused when a plain-text copy carries a dash character, "what this is" framing, a
    backtick, a Markdown link, a character reference or a tag of the pages' markup."""
    why = []
    if any(d in text for d in DASHES):
        why.append("a dash character (U+2010 to U+2015 or U+2212)")
    if FRAMING.search(text):
        why.append('"what this is" framing')
    if "`" in text:
        why.append("a backtick")
    if "](" in text:
        why.append("a Markdown link")
    if CHAR_REF.search(text):
        why.append("a character reference")
    if TEXT_TAG.search(text):
        why.append("an HTML tag")
    if why:
        raise Refused(f"{name} would contain " + ", ".join(why))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="/")
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
        texts = b.texts()
    except SourceError as exc:
        print(f"  FAIL  {exc}")
        return 2
    except Refused as exc:
        print(f"  FAIL  refused: {exc}")
        return 1
    out = args.out or Path("site") / args.base.lstrip("/")
    out = out if out.is_absolute() else ROOT / out
    written = {**pages, **texts}  # every file this build writes, pages and plain-text copies
    if args.check:
        problems = []
        for name, text in written.items():
            path = out / name
            try:
                if path.read_bytes() != text.encode("utf-8"):
                    problems.append(f"{name} differs from a fresh build")
            except FileNotFoundError:
                problems.append(f"{name} is missing")
            except OSError as exc:
                print(f"  FAIL  cannot read {path}: {exc}")
                return 2
        # Every file under the output folder is a page or plain-text copy this build writes, a
        # copied template file under assets/baseline/ (scripts/copy-baseline.py, pinned by
        # tools/check_baseline_pin.py), or the optional assets/site.css that the baseline README
        # allows for the 2 per-site
        # constants (its grammar is held by tools/check_draft.py). A page is .html or .htm in any
        # case, read as the CSP gate reads one (name_suffix). At the root after promotion the folder
        # also holds the published files, named one by one in PUBLISHED.
        if out.is_dir():
            for path in sorted(p for p in out.rglob("*") if not p.is_dir()):
                rel = path.relative_to(out).as_posix()
                if rel in written or rel.startswith(COPIED) or rel == SITE_CSS:
                    continue
                if name_suffix(path.name) in (".html", ".htm"):
                    problems.append(f"{rel} is not a page this build writes")
                elif args.base != "/":
                    problems.append(f"{rel} is neither a page this build writes nor a copied "
                                    f"template file under {COPIED}")
                elif rel not in PUBLISHED:
                    problems.append(f"{rel} is neither a page this build writes, a copied template "
                                    f"file under {COPIED}, nor a published file in PUBLISHED")
        if problems:
            for p in problems:
                print(f"  FAIL  {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}/{p}; "
                      f"rerun python3 -I -B scripts/build-site.py")
            return 1
        print(f"  ok    the {len(pages)} pages and {len(texts)} plain-text copy under "
              f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} "
              f"match a fresh build (base {args.base})")
        return 0
    for name, text in written.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    print(f"  ok    wrote {len(pages)} pages and {len(texts)} plain-text copy under {out} "
          f"(base {args.base})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
