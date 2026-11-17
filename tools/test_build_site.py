#!/usr/bin/env python3
"""Cases for scripts/build-site.py: its refusals, its base path, and its --check mode.

The refusals are SPECIFICATION section 12's: a page carrying a dash character (U+2010 to
U+2015, U+2212), an inline style or style= attribute, an inline script, an on* attribute or "what
this is" framing is never written. Each is planted in a real generated page and must be refused,
while the page as generated passes. An on* attribute is a name in a tag: an onload after a quoted
value holding ">" is refused, and the word "on" inside a closed quoted value (a description reading
"Read on GitHub") is not refused.
The base path must reach every internal link and asset at / (the default since promotion) and at
/draft/ (the staging form the `draft` branch uses). The live site carries no /draft/ page
(baseline SPECIFICATION section 4.1 item 0): the root build writes no page under draft/, writes
the same pages as the staged build, and no root page names /draft/. At the root every page is
indexable except the 404 page, which carries the noindex meta; a staged build is noindex
everywhere. At the root each indexable page carries its title, description, the link-preview tags
(og:site_name after og:type) and its canonical in the template's head order, each tag with its
full value (the page title with " | SecureConfig.ai", the description from site-src/content.json,
the card's alt text); the 404 page and every page of a staged build carry no previews or canonical.
Every page, the 404 included, at both bases, carries the light and dark switch
of baseline 1.6.0 (SPECIFICATION 7.33) exactly as the reference pages write it, once, as the last
child of the top bar after its nav, and loads scheme.js once, right after the touch icon and
before the first stylesheet, with data-cfasync="false" before src and no defer or async.
The landing page carries the About line of baseline 1.7.0 (SPECIFICATION 7.24) exactly once, with
1 ordinary space after each dot span and none before it.
The For AI assistants page carries the Claude Code install commands once each, in a copy block,
read from README.md's install section only (site-src/content.json carries none) by the build's
standard-library reader, install_blocks(). A README whose shell block is edited, or edited and
fenced with tildes, or whose in-session block is edited, puts that block on the page, and the
reader reads the same blocks at the same lines with CRLF or CR line endings. The build refuses a
section with the in-session block commented out beside a visible replacement (which it reads as a
third block), mismatched fence lengths on either block (an opening fence longer than its closing
one, or shorter), a third block, the blocks swapped, the shell block holding the in-session
commands, an empty in-session block, an indented fence, and a README with no install section or a
second one. None of these cases needs a Markdown parser. What the reader cannot see, such as a
block hidden in an HTML comment, is for tools/check_install_blocks.py to catch, with its cases in
tools/test_install_blocks.py.
--check must report a one-byte change, an extra page (.html or .htm in any case) and a missing
page at any base; a stray file outside assets/baseline/ other than assets/site.css is refused at
both bases, except at the root a published file (PUBLISHED, such as llms.txt) beside the pages.
At the root it refuses a staged build written under draft/ beside the pages (SPECIFICATION
section 4.1 item 3: `main` never carries the draft).
The unlisted advisory is written at advisories/n8n-2026-11-07-jposluns.html only, with its
one-line summary as the first paragraph under the Title heading and the maintainer's reporter
details. Its plain-text copy, advisories/n8n-2026-11-07-jposluns.txt, is the one text file the
build writes: it carries no HTML or Markdown, the page's section labels in order and every
content.json entry of the advisory; a backtick, a dash character, a tag, a character reference, a
Markdown link or "what this is" framing planted in it is refused; and --check reports a change to
it, its absence and a stray advisories/other.txt beside it.
At the root, --check admits the 2 versioned release archive names in downloads/, refuses a latest
name and a folder there, and exits 2 when downloads/ cannot be listed (skipped when run as root,
which can list it); a staged build refuses any file in downloads/. download_problems() itself
accepts secureconfig-1.0.<N>.zip and secureconfig-plugin-1.0.<N>.zip and a file of exactly the
per-file cap, and refuses both latest names, wrong names and version forms (a non-ASCII digit
first or later among them), a folder (empty, holding a valid archive name, or itself under a valid
name), a symbolic link to a file and to a folder under a valid name, a FIFO under a valid name
(where the platform has os.mkfifo), an oversized file, and a total over the total cap, reported
once. The total counts every regular file with a valid name, an oversized one included, and no
refused entry. downloads/ itself as a symbolic link is refused, a downloads/ that cannot be listed
raises OSError (skipped as root), and the caps are exactly 20 MiB and 200 MiB.
At the root, --check also admits the 2 generated hosted files, `_redirects` and
`marketplace.json`, only when each equals, byte for byte, what tools/gen_hosted.py writes from
the release record and the redirect allowlist read beside the output folder. Those cases cover
both files admitted as generated, an edited catalog digest, an appended redirect, a missing
`_redirects` with a record behind it, a `marketplace.json` left behind with no record, and an
unparsable plugin/plugin.json and one nested too deeply to parse, each with a record behind it
(a read error, exit 2, no traceback). A site-src/content.json nested too deeply to parse and one
that is a JSON array each raise the build's read error, SourceError (exit 2), in process.
"""
import hashlib
import html
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SCRIPT = ROOT / "scripts" / "build-site.py"
sys.path.insert(0, str(TOOLS))
import gen_hosted  # noqa: E402  (writes the byte-exact generated hosted files in fixtures)

spec = importlib.util.spec_from_file_location("build_site", SCRIPT)
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)
ROBOTS_META = '<meta name="robots" content="noindex, nofollow">'
# The switch as baseline 1.6.0's reference pages write it (reference/404.html, line 18), copied
# here by hand so that a drift in the generator's copy is caught.
REFERENCE_SWITCH = (
    '<button class="scheme" type="button" data-scheme-toggle aria-pressed="false" hidden><svg '
    'class="moon" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'focusable="false"><path d="M20.5 14.2A8.5 8.5 0 0 1 9.8 3.5a8.5 8.5 0 1 0 10.7 10.7z"/></svg>'
    '<svg class="sun" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'focusable="false"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 '
    '12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/>'
    '</svg><span class="vh">Dark mode</span></button>')
# The About line as baseline 1.7.0's SPECIFICATION section 7.24 writes it, copied here by hand: 1
# ordinary space after each dot span and none before it, so the line breaks only after a dot.
DOT = '<span class="dot" aria-hidden="true">&middot;</span>'
ABOUT_LINE = (
    f'<p class="about"><a href="/disclosure/">Disclosure</a>{DOT} <a href="/license/">Licence</a>'
    f'{DOT} <a href="https://posluns.ca/privacy/" target="_blank" rel="noopener noreferrer">Privacy'
    f'<span class="vh"> (opens in a new tab)</span></a>{DOT} <a href="https://posluns.ca/security/" '
    'target="_blank" rel="noopener noreferrer">Security<span class="vh"> (opens in a new tab)</span>'
    '</a></p>')
# Each page with link previews at the root: its title and the site-src/content.json key of its
# description.
PREVIEWS = {"index.html": ("Home", "home"), "guides/index.html": ("Guides", "guides"),
            "for-ai/index.html": ("For AI assistants", "for_ai"),
            "for-humans/index.html": ("For humans", "for_humans"),
            "checklist/index.html": ("Checklist", "checklist"),
            "disclosure/index.html": ("Disclosure", "disclosure"),
            "license/index.html": ("Licence", "license")}
# The pages that are noindex at the root and carry no link previews, canonical or description: the
# 404 page and the one unlisted advisory (the maintainer's instruction), both built like the 404.
ADVISORY = "advisories/n8n-2026-11-07-jposluns.html"
# The quality matrix page is noindex by the GQS-ADOPT decision: no canonical, previews, menu entry
# or sitemap row, built like the 404 and the advisory.
NOINDEX_NAMES = {"404.html", ADVISORY, "quality/index.html"}
# The advisory's plain-text copy, which the build writes beside the pages (Builder.texts).
ADVISORY_TEXT = "advisories/n8n-2026-11-07-jposluns.txt"


def refused(text):
    try:
        build_site.refuse("page", text)
    except build_site.Refused as exc:
        return str(exc)
    return None


def run(*args):
    r = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), *args], capture_output=True,
                       text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def build_from_readme(text, readme):
    """(Builder, None) for the repository's sources with README.md replaced by text, or
    (None, the refusal); a text equal to README.md is an error in the case itself."""
    if text == readme:
        return None, "the case's edit did not change README.md"
    root = Path(tempfile.mkdtemp())
    try:
        for rel in (build_site.CONTENT, build_site.VERSIONED):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, root / rel)
        (root / "README.md").write_text(text, encoding="utf-8")
        try:
            return build_site.Builder("/", root=root), None
        except build_site.SourceError as exc:
            return None, str(exc)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def content_cases():
    """The failures for a site-src/content.json the build cannot use: valid JSON nested past the
    interpreter's recursion limit and a JSON array each raise SourceError, the build's read
    error (exit 2), never another exception."""
    failures = []
    for desc, text, expected in (
            ("nested too deeply to parse", "[" * 100000 + "]" * 100000 + "\n",
             "nested too deeply to parse as JSON"),
            ("a JSON array", "[]\n", "is not a JSON object")):
        root = Path(tempfile.mkdtemp())
        try:
            for rel in (build_site.VERSIONED, build_site.README):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            (root / build_site.CONTENT).parent.mkdir(parents=True)
            (root / build_site.CONTENT).write_text(text, encoding="utf-8")
            try:
                build_site.Builder("/", root=root)
                why = None
            except build_site.SourceError as exc:
                why = str(exc)
            except Exception as exc:  # noqa: BLE001  an escaping exception is the failure
                why = f"{type(exc).__name__} escaped"
        finally:
            shutil.rmtree(root, ignore_errors=True)
        if why is None or expected not in why:
            failures.append(f"a site-src/content.json {desc} is not a read error naming "
                            f"{expected!r}: {why!r}")
    return failures


def sized(path, size):
    """Write a file of size bytes at path, sparse where the file system allows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.truncate(size)


def download_cases():
    """(failures, count) for the release archive rule: download_problems() on fixture downloads/
    folders, and the exact cap values. Each case maps a name under downloads/ to a size, or to None
    for a symbolic link to a valid archive outside it, "folder" for an empty folder, "folder link"
    for a symbolic link to a folder outside it, or "fifo" for a FIFO, and expects the problems
    whose text starts with each given prefix, in order."""
    failures, count = [], 0

    def case(label, files, want, link_folder=False, **caps):
        nonlocal count
        count += 1
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "site"
            out.mkdir()
            if link_folder:
                sized(Path(d) / "elsewhere" / "secureconfig-1.0.1234.zip", 100)
                (out / "downloads").symlink_to(Path(d) / "elsewhere", target_is_directory=True)
            for name, size in files.items():
                entry = out / "downloads" / name
                entry.parent.mkdir(parents=True, exist_ok=True)
                if size is None:
                    sized(Path(d) / "target.zip", 100)
                    entry.symlink_to(Path(d) / "target.zip")
                elif size == "folder":
                    entry.mkdir()
                elif size == "folder link":
                    sized(Path(d) / "target" / "secureconfig-1.0.1234.zip", 100)
                    entry.symlink_to(Path(d) / "target", target_is_directory=True)
                elif size == "fifo":
                    os.mkfifo(entry)
                else:
                    sized(entry, size)
            got = build_site.download_problems(out, **caps)
        if len(got) != len(want) or not all(g.startswith(w) for w, g in zip(want, got)):
            failures.append(f"downloads/, {label}: expected problems starting {want!r}, got {got!r}")

    big = build_site.DOWNLOAD_MAX
    case("a valid skill zip name", {"secureconfig-1.0.1234.zip": 100}, [])
    case("a valid plugin zip name", {"secureconfig-plugin-1.0.1234.zip": 100}, [])
    case("both valid names together", {"secureconfig-1.0.1.zip": 100,
                                       "secureconfig-plugin-1.0.1.zip": 100}, [])
    case("the skill latest name", {"secureconfig-latest.zip": 100},
         ["downloads/secureconfig-latest.zip is a latest name"])
    case("the plugin latest name, empty", {"secureconfig-plugin-latest.zip": 0},
         ["downloads/secureconfig-plugin-latest.zip is a latest name"])
    for name in ("secureconfig-v1.0.1234.zip", "secureconfig-1.0.01234.zip", "secureconfig-1.0.0.zip",
                 "secureconfig-1.1.1234.zip", "secureconfig-1.0.zip", "secureconfig-1.0.1234.0.zip",
                 "secureconfig-plugin-1.0.12a.zip", "secureconfig-1.0.１２.zip",
                 "secureconfig-1.0.١٢.zip", "secureconfig-1.0.1١٢.zip",
                 "secureconfig-plugin-1.0.1２.zip", "SECURECONFIG-1.0.1234.zip",
                 "secureconfig-1.0.1234.ZIP", "secureconfig-1.0.1234.zip.gz",
                 "secureconfig-skill-1.0.1234.zip", "other-1.0.1234.zip", "notes.txt"):
        case(f"the wrong name or version form {name!r}", {name: 100},
             [f"downloads/{name} is not a release archive name"])
    # Only the top level is read: any folder is refused as a folder, and nothing in it is read.
    case("an empty folder", {"old": "folder"}, ["downloads/old is a folder"])
    case("a folder holding a valid archive name", {"old/secureconfig-1.0.1234.zip": 100},
         ["downloads/old is a folder"])
    case("a folder under a valid name", {"secureconfig-1.0.1234.zip": "folder"},
         ["downloads/secureconfig-1.0.1234.zip is a folder"])
    case("a symbolic link to a folder under a valid name",
         {"secureconfig-1.0.1234.zip": "folder link"},
         ["downloads/secureconfig-1.0.1234.zip is not a regular file"])
    if hasattr(os, "mkfifo"):
        case("a FIFO under a valid name", {"secureconfig-plugin-1.0.1234.zip": "fifo"},
             ["downloads/secureconfig-plugin-1.0.1234.zip is not a regular file"])
    case("a file of exactly the per-file cap", {"secureconfig-1.0.1234.zip": big}, [])
    case("an oversized file", {"secureconfig-plugin-1.0.1234.zip": big + 1},
         [f"downloads/secureconfig-plugin-1.0.1234.zip is {big + 1} bytes, over the {big}-byte cap"])
    case("an oversized file, which counts towards the total",
         {"secureconfig-1.0.1.zip": 11, "secureconfig-plugin-1.0.1.zip": 10},
         ["downloads/secureconfig-1.0.1.zip is 11 bytes, over the 10-byte cap",
          "downloads/ holds 21 bytes of release archives, over the 20-byte cap"],
         max_file=10, max_total=20)
    case("files totalling exactly the total cap",
         {"secureconfig-1.0.1.zip": 10, "secureconfig-plugin-1.0.1.zip": 10,
          "secureconfig-1.0.2.zip": 5}, [], max_file=10, max_total=25)
    case("files over the total cap",
         {"secureconfig-1.0.1.zip": 10, "secureconfig-plugin-1.0.1.zip": 10,
          "secureconfig-1.0.2.zip": 6},
         ["downloads/ holds 26 bytes of release archives, over the 25-byte cap"],
         max_file=10, max_total=25)
    case("a refused name, which does not count towards the total",
         {"secureconfig-1.0.1.zip": 10, "secureconfig-latest.zip": 20},
         ["downloads/secureconfig-latest.zip is a latest name"], max_file=10, max_total=25)
    case("a symbolic link under a valid name", {"secureconfig-1.0.1234.zip": None},
         ["downloads/secureconfig-1.0.1234.zip is not a regular file"])
    case("downloads/ as a symbolic link", {}, ["downloads/ is a symbolic link"], link_folder=True)
    count += 1
    with tempfile.TemporaryDirectory() as d:
        if build_site.download_problems(Path(d)) != []:
            failures.append("downloads/: a root with no downloads/ folder has problems")
    if os.geteuid() != 0:  # root lists a folder whatever its mode, so this needs a non-root user
        count += 1
        with tempfile.TemporaryDirectory() as d:
            sized(Path(d) / "downloads" / "secureconfig-1.0.1234.zip", 100)
            (Path(d) / "downloads").chmod(0o300)
            try:
                got = build_site.download_problems(Path(d))
                failures.append(f"downloads/: a folder that cannot be listed gave {got!r}, "
                                f"not OSError")
            except OSError:
                pass
            finally:
                (Path(d) / "downloads").chmod(0o700)
    count += 1
    # Cloudflare Pages' limit on 1 file is 25 MiB (to verify online); the total holds several files.
    if not 0 < big < 25 * 1024 * 1024 or not big < build_site.DOWNLOADS_TOTAL_MAX:
        failures.append(f"downloads/: the caps {big} and {build_site.DOWNLOADS_TOTAL_MAX} are not "
                        f"a per-file cap below 25 MiB and a larger total cap")
    count += 1
    # The CHANGELOG and the pull request state these exact values, so a change to either fails here.
    if (big, build_site.DOWNLOADS_TOTAL_MAX) != (20 * 1024 * 1024, 200 * 1024 * 1024):
        failures.append(f"downloads/: the caps {big} and {build_site.DOWNLOADS_TOTAL_MAX} are not "
                        f"20 MiB and 200 MiB")
    return failures, count


def main():
    failures = []
    try:
        builder = build_site.Builder("/")
    except build_site.SourceError as exc:
        print(f"  FAIL  the site cannot be built from this checkout's sources: {exc}")
        return 1
    pages = builder.build()
    home = pages["index.html"]
    rail_page = pages["disclosure/index.html"]
    plants = [
        ("a static aria-current on a rail link",
         rail_page.replace('<li><a href="#d-1">', '<li><a href="#d-1" aria-current="true">', 1),
         "static aria-current"),
        ("a section rail without rail.js",
         rail_page.replace('<script src="/assets/baseline/rail.js" defer></script>\n', "", 1),
         "without rail.js"),
        ("an en dash", home.replace("Start here", "Start–here", 1), "dash character"),
        ("an em dash", home.replace("Start here", "Start—here", 1), "dash character"),
        ("a hyphen character U+2010", home.replace("Start here", "Start‐here", 1), "dash character"),
        ("a figure dash", home.replace("Start here", "Start‒here", 1), "dash character"),
        ("a horizontal bar", home.replace("Start here", "Start―here", 1), "dash character"),
        ("a minus sign", home.replace("Start here", "Start−here", 1), "dash character"),
        ("a style block", home.replace("</head>", "<style>p{}</style></head>", 1), "inline style"),
        ("a style= attribute", home.replace('<p class="intro">', '<p class="intro" style="x">', 1),
         "inline style"),
        ("an inline script", home.replace("</head>", "<script>x()</script></head>", 1), "inline script"),
        ("a script with a src and a body",
         home.replace("</head>", '<script src="/x.js">x()</script></head>', 1), "inline script"),
        ("an onclick attribute", home.replace('<p class="intro">', '<p class="intro" onclick="x()">', 1),
         "on* attribute"),
        ("a valueless onload attribute", home.replace("<body>", "<body onload>", 1), "on* attribute"),
        # The on* check reads attribute names, so a ">" inside a quoted value does not end the tag,
        # and a word in a closed quoted value hides no name after it.
        ('an onload after a quoted value holding ">"',
         home.replace('<p class="intro">', '<p class="intro" title="a>b" onload>', 1), "on* attribute"),
        ('an onload after a quoted value reading "read on"',
         home.replace('<p class="intro">', '<p class="intro" title="read on" onload>', 1),
         "on* attribute"),
        ("an on after a quote that never closes", home + '<p title="read on>', "on* attribute"),
        ('"what this is" framing', home.replace("Start here", "What this is", 1), "what this is"),
    ]
    for desc, text, expected in plants:
        if text == home:
            failures.append(f"{desc}: the plant did not change the page")
            continue
        why = refused(text)
        if why is None or expected not in why:
            failures.append(f"{desc}: expected a refusal naming {expected!r}, got {why!r}")
    for name, text in pages.items():
        if refused(text) is not None:
            failures.append(f"{name} as generated is refused: {refused(text)}")
    # The unlisted advisory (the maintainer's instruction of 2026-11-07): written at its dated name
    # only, with the one-line summary as the first paragraph under the Title heading, before the
    # detailed title, and the reporter details the maintainer gave.
    a = builder.c["advisory_n8n"]
    if ADVISORY not in pages or "advisories/n8n.html" in pages:
        failures.append(f"the build does not write the advisory at {ADVISORY} only: {sorted(pages)}")
    else:
        adv = pages[ADVISORY]
        title_block = ('<h2 id="title">Title</h2>\n<p><strong>Summary:</strong> '
                       f'{builder.inline(a["report_summary"]["text"])}</p>\n'
                       f'<p>{builder.inline(a["report_title"]["text"])}</p>')
        if adv.count(title_block) != 1:
            failures.append(f"{ADVISORY} does not carry the Summary paragraph first under the "
                            f"Title heading, before the detailed title, exactly once")
        for item in ("Name: Jeff Posluns", "Email: jeff@posluns.ca", "GitHub handle: jposluns"):
            if adv.count(f"<li>{item}</li>") != 1:
                failures.append(f"{ADVISORY} does not carry the reporter item {item!r} once")
        if "left blank" in adv:
            failures.append(f"{ADVISORY} still carries a blank reporter field")
    # Its plain-text copy: the only text the build writes, refused by nothing, with no HTML and no
    # Markdown, the same labels in the page's order, and every content.json entry of the advisory.
    texts = builder.texts()
    if sorted(texts) != [ADVISORY_TEXT]:
        failures.append(f"the build's plain-text copies are {sorted(texts)}, not [{ADVISORY_TEXT!r}]")
    txt = texts.get(ADVISORY_TEXT, "")
    for bad in ("`", "<p>", "<li>", "<strong>", "<code>", "&lt;", "&gt;", "&amp;", "](", "**"):
        if bad in txt:
            failures.append(f"{ADVISORY_TEXT} carries {bad!r}, which a plain-text copy does not")
    labels = ("SUMMARY\n", "TITLE\n", "AFFECTED VERSIONS\n", "DESCRIPTION\n",
              "Vulnerable code locations, observed in source:\n", "Read path, observed in source:\n",
              "Read path, inference:\n", "Steps a reviewer would take:\n", "Proof of concept:\n",
              "Impact:\n", "REPORTER\n", "CVSS 4.0, PROVISIONAL\n", "MITIGATIONS\n")
    at = [txt.find("\n\n" + label) for label in labels]
    if -1 in at or at != sorted(at):
        failures.append(f"{ADVISORY_TEXT} lacks its section labels in the page's order "
                        f"(missing {[lb for lb, i in zip(labels, at) if i == -1]!r})")
    entries = [v for v in a.values() if isinstance(v, dict)] + [
        x for v in a.values() if isinstance(v, list) for x in v]
    for entry in entries:
        if builder.plain(entry["text"]) not in txt:
            failures.append(f"{ADVISORY_TEXT} lacks the advisory entry {entry['text'][:60]!r}")
    for desc, plant, expected in (
            ("a backtick", txt + "`x`\n", "a backtick"),
            ("an en dash", txt + "a–b\n", "dash character"),
            ("a paragraph tag", txt + "<p>x</p>\n", "an HTML tag"),
            ("a character reference", txt + "a &lt; b\n", "a character reference"),
            ("a Markdown link", txt + "[x](https://example.com/)\n", "a Markdown link"),
            ('"what this is" framing', txt + "What this is\n", "what this is")):
        try:
            build_site.refuse_text(ADVISORY_TEXT, plant)
            failures.append(f"{ADVISORY_TEXT} with {desc} was not refused")
        except build_site.Refused as exc:
            if expected not in str(exc):
                failures.append(f"{ADVISORY_TEXT} with {desc} was refused for another reason: {exc}")
    # #1189 drafting: a description may use the word "on" inside its quoted value.
    worded = home.replace('<meta name="description" content="',
                          '<meta name="description" content="Read on GitHub. ', 1)
    if worded == home or refused(worded) is not None:
        failures.append(f'a description reading "Read on GitHub" was refused: {refused(worded)!r}')
    # Baseline 1.7.0 (SPECIFICATION 7.24): the landing page's About line exactly as the
    # specification writes it, with 1 ordinary space after each dot span and none before it.
    if home.count(ABOUT_LINE) != 1:
        failures.append("base /: index.html does not carry the About line of SPECIFICATION 7.24 "
                        "(1 space after each dot span, none before it) exactly once")

    # The Claude Code install commands have 1 source, the README's install section: the For AI
    # assistants page carries each of its 2 fenced blocks once, in a copy block, content.json
    # carries no commands, an edited README block is what the page shows, and a section that is not
    # exactly the in-session block then the shell block is refused.
    for_ai = pages["for-ai/index.html"]
    install = builder.c["for_ai"]["install"]
    pids = {"session": "install-session", "shell": "install-shell"}
    for key, pid in pids.items():
        if "commands" in install[key]:
            failures.append(f"site-src/content.json for_ai.install.{key} carries commands; they "
                            f"come from README.md only")
        if for_ai.count(builder.copyblock(pid, builder.install[key])) != 1:
            failures.append(f"for-ai/index.html does not carry the {key} install commands once "
                            f"in the copy block {pid}")
    if for_ai.count('<h2 id="install">Install in Claude Code</h2>') != 1:
        failures.append("for-ai/index.html does not carry the install heading once")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    session, shell = builder.install["session"], builder.install["shell"]
    session_block = f"```text\n{session}\n```\n"
    shell_block = f"```bash\n{shell}\n```\n"
    install_cases = 0
    if readme.count(session_block) != 1 or readme.count(shell_block) != 1:
        failures.append("README.md does not hold the install blocks the build read, each once as a "
                        "```text and a ```bash block, so the install cases were not run")
    else:
        edited_shell = shell + " --scope project"
        wrong = "/plugin install wrong@wrong"
        # (README text, the part of the refusal that names its reason)
        refused_cases = {
            "the in-session block commented out beside a visible replacement":
                (readme.replace(session_block,
                                f"<!--\n{session_block}-->\n\n```text\n{wrong}\n```\n", 1),
                 "holds 3 fenced blocks"),
            "mismatched fence lengths on the in-session block":
                (readme.replace(session_block, f"````text\n{session}\n```\n", 1),
                 "is not closed"),
            "mismatched fence lengths on the shell block":
                (readme.replace(shell_block, f"````bash\n{shell}\n```\n", 1), "is not closed"),
            "a closing fence longer than the opening one":
                (readme.replace(session_block, f"```text\n{session}\n````\n", 1),
                 "is not closed"),
            "an empty in-session block":
                (readme.replace(session_block, "```text\n```\n", 1), "fenced block 1"),
            "the shell block indented in a list item":
                (readme.replace(shell_block, "- From a shell:\n\n  " + shell_block.replace(
                    "\n", "\n  ").rstrip(" ") + "\n", 1), "is an indented fence"),
            "a third block":
                (readme.replace(shell_block, shell_block + "\n```bash\nclaude plugin install "
                                "other@other\n```\n", 1), "holds 3 fenced blocks"),
            "the blocks swapped":
                (readme.replace(session_block, "\0", 1).replace(shell_block, session_block, 1)
                 .replace("\0", shell_block, 1), "fenced block 1"),
            "the shell block given the in-session commands":
                (readme.replace(shell_block, f"```bash\n{session}\n```\n", 1), "fenced block 2"),
            "no install section":
                (readme.replace(build_site.INSTALL + "\n", "## Installing\n", 1), "has 0 lines"),
            "a second install section":
                (readme + f"\n{build_site.INSTALL}\n\n{session_block}\n{shell_block}",
                 "has 2 lines"),
        }
        # (README text, key, the commands the page must then carry for that key)
        followed_cases = {
            "the shell block edited":
                (readme.replace(shell_block, f"```bash\n{edited_shell}\n```\n", 1), "shell",
                 edited_shell),
            "the shell block edited and fenced with tildes":
                (readme.replace(shell_block, f"~~~bash\n{edited_shell}\n~~~\n", 1), "shell",
                 edited_shell),
            "the in-session block edited":
                (readme.replace(session_block, f"```text\n{wrong}\n```\n", 1), "session", wrong),
        }
        # The build reads README.md with universal newlines, so the reader itself is given each
        # line ending CommonMark knows: it must read the same blocks, at the same lines.
        for ending in ("\r\n", "\r"):
            install_cases += 1
            try:
                got = build_site.install_blocks(readme.replace("\n", ending))
            except build_site.SourceError as exc:
                got = str(exc)
            if got != build_site.install_blocks(readme):
                failures.append(f"install source, line endings {ending!r}: install_blocks() read "
                                f"{got!r}")
        for desc, (text, reason) in refused_cases.items():
            install_cases += 1
            built, error = build_from_readme(text, readme)
            if error is None:
                failures.append(f"install source, {desc}: the build accepted it")
            elif "Install in Claude Code" not in error or reason not in error:
                failures.append(f"install source, {desc}: refused for another reason than "
                                f"{reason!r}: {error}")
        for desc, (text, key, want) in followed_cases.items():
            install_cases += 1
            built, error = build_from_readme(text, readme)
            if error is not None:
                failures.append(f"install source, {desc}: refused: {error}")
                continue
            page = built.for_ai()
            if built.install[key] != want or page.count(built.copyblock(pids[key], want)) != 1:
                failures.append(f"install source, {desc}: the page does not carry the README's "
                                f"{key} block {want!r} once, in its copy block")
            if built.copyblock(pids[key], builder.install[key]) in page:
                failures.append(f"install source, {desc}: the page still carries the {key} "
                                f"commands the README no longer shows")

    # The base path reaches every internal link and asset, at the root and in the staging form.
    staged_pages = build_site.Builder("/draft/").build()
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        for name, text in built.items():
            for needle in (f'href="{base}assets/baseline/baseline.css"', f'href="{base}guides/"',
                           f'src="{base}assets/baseline/logos/secureconfig.svg"'):
                if needle not in text:
                    failures.append(f"base {base}: {name} lacks {needle}")

    # Baseline 1.6.0 (SPECIFICATION 7.33): the switch on every page, the 404 included, as the
    # last child of the top bar, and scheme.js between the touch icon and the
    # first stylesheet, without defer or async.
    for base, built in (("/draft/", staged_pages), ("/", pages)):
        script = f'<script data-cfasync="false" src="{base}assets/baseline/scheme.js"></script>'
        head = (f'secureconfig-touch.png">\n{script}\n'
                f'<link rel="stylesheet" href="{base}assets/baseline/fonts.css">\n')
        for name, text in built.items():
            if text.count(REFERENCE_SWITCH) != 1 or f"</nav>{REFERENCE_SWITCH}</header>" not in text:
                failures.append(f"base {base}: {name} does not carry the reference switch exactly "
                                f"once as the last child of header.mast, after nav.nav")
            if text.count("scheme.js") != 1 or text.count(head) != 1:
                failures.append(f"base {base}: {name} does not load scheme.js once, after the touch "
                                f"icon and before the first stylesheet, as {script}")

    # The live site carries no /draft/ page (SPECIFICATION 4.1 item 0): the root build writes no
    # page under draft/ and the same pages as the staged build, and no root page names /draft/.
    # At the root only the 404 page is noindex; a staged build is noindex everywhere.
    for name in pages:
        if name.casefold().startswith("draft/"):
            failures.append(f"base /: the build writes {name}; the live site carries no /draft/ page")
    if sorted(pages) != sorted(staged_pages):
        failures.append(f"the root and staged builds write different pages: {sorted(pages)} and "
                        f"{sorted(staged_pages)}")
    if "draft" in builder.c:
        failures.append("site-src/content.json still carries a draft entry")
    for name, text in pages.items():
        hidden = name in NOINDEX_NAMES
        if (ROBOTS_META in text) is not hidden:
            failures.append(f"base /: {name} {'lost' if hidden else 'still carries'} the noindex meta")
        if "/draft/" in text:
            failures.append(f"base /: {name} names /draft/")
    for name, text in staged_pages.items():
        if ROBOTS_META not in text:
            failures.append(f"base /draft/: {name} lacks the noindex meta")

    # At the root each indexable page carries its title and description, then
    # the link previews (og:site_name after og:type, as auditthis.ai orders it), then the icons and
    # stylesheets, then their canonical URL, each tag with its full value; the 404 page carries no
    # link previews, canonical or description, and no page of a staged build carries link previews
    # or a canonical.
    for name, text in pages.items():
        head = text.split("</head>", 1)[0]
        if name in NOINDEX_NAMES:
            if 'property="og:' in head or 'name="twitter:' in head:
                failures.append(f"base /: {name} carries link-preview tags")
            if 'rel="canonical"' in head or 'name="description"' in head:
                failures.append(f"base /: {name} carries a canonical or a description")
            continue
        url = build_site.ORIGIN + "/" + name[:-len("index.html")]
        # #1189 QA: the full value of each tag, not its prefix.
        title, key = PREVIEWS[name]
        full = html.escape(f"{title} | SecureConfig.ai", quote=True)
        desc = html.escape(builder.n(builder.c[key]["description"]["text"]), quote=True)
        alt = html.escape(build_site.CARD_ALT, quote=True)
        needles = (f"<title>{title} | SecureConfig.ai</title>",
                   f'<meta name="description" content="{desc}">',
                   '<meta property="og:type" content="website">',
                   '<meta property="og:site_name" content="SecureConfig.ai">',
                   f'<meta property="og:url" content="{url}">',
                   f'<meta property="og:title" content="{full}">',
                   f'<meta property="og:description" content="{desc}">',
                   f'<meta property="og:image" content="{build_site.CARD}">',
                   '<meta property="og:image:type" content="image/png">',
                   '<meta property="og:image:width" content="1200">',
                   '<meta property="og:image:height" content="630">',
                   f'<meta property="og:image:alt" content="{alt}">',
                   '<meta name="twitter:card" content="summary_large_image">',
                   f'<meta name="twitter:title" content="{full}">',
                   f'<meta name="twitter:description" content="{desc}">',
                   f'<meta name="twitter:image" content="{build_site.CARD}">',
                   f'<meta name="twitter:image:alt" content="{alt}">', '<link rel="icon" ',
                   '<script data-cfasync="false" src="/assets/baseline/scheme.js"></script>',
                   '<link rel="stylesheet" href="/assets/baseline/baseline.css">',
                   f'<link rel="canonical" href="{url}">')
        at = [head.find(n) for n in needles]
        if -1 in at or at != sorted(at):
            missing = [n for n, i in zip(needles, at) if i == -1]
            failures.append(f"base /: {name} lacks the head's description, link previews and "
                            f"canonical in order (missing {missing!r})")
    for name, text in staged_pages.items():
        if 'rel="canonical"' in text or 'property="og:' in text or 'name="twitter:' in text:
            failures.append(f"base /draft/: {name} carries a canonical or link-preview tags")

    # --check against a build it did not write, at the root base (the default).
    d = Path(tempfile.mkdtemp())
    try:
        out = d / "root"
        rc, text = run("--out", str(out))
        if rc != 0:
            failures.append(f"a build into a scratch folder failed: {text!r}")
        rc, text = run("--check", "--out", str(out))
        if rc != 0 or "match a fresh build" not in text:
            failures.append(f"--check on a fresh build did not pass: {text!r}")
        target = out / "guides" / "index.html"
        data = bytearray(target.read_bytes())
        data[100] ^= 1
        target.write_bytes(bytes(data))
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "guides/index.html differs" not in text:
            failures.append(f"--check missed a one-byte change: {text!r}")
        run("--out", str(out))
        # The advisory's plain-text copy is written and verified like a page.
        copy = out / ADVISORY_TEXT
        if not copy.is_file() or copy.read_bytes() != texts.get(ADVISORY_TEXT, "").encode("utf-8"):
            failures.append(f"the build did not write {ADVISORY_TEXT} as Builder.texts() gives it")
        else:
            copy.write_bytes(copy.read_bytes() + b"x")
            rc, text = run("--check", "--out", str(out))
            if rc != 1 or f"{ADVISORY_TEXT} differs from a fresh build" not in text:
                failures.append(f"--check missed a change to the plain-text copy: {text!r}")
            copy.unlink()
            rc, text = run("--check", "--out", str(out))
            if rc != 1 or f"{ADVISORY_TEXT} is missing" not in text:
                failures.append(f"--check missed a missing plain-text copy: {text!r}")
            # Only that exact .txt is admitted: another file beside it is a stray.
            (out / "advisories" / "other.txt").write_text("x\n", encoding="utf-8")
            run("--out", str(out))
            rc, text = run("--check", "--out", str(out))
            if rc != 1 or "advisories/other.txt is neither a page this build writes" not in text:
                failures.append(f"--check at the root accepted a stray advisories/other.txt: {text!r}")
            (out / "advisories" / "other.txt").unlink()
        run("--out", str(out))
        (out / "extra").mkdir()
        (out / "extra" / "index.html").write_text("<p>x</p>", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "extra/index.html is not a page this build writes" not in text:
            failures.append(f"--check missed an extra page: {text!r}")
        shutil.rmtree(out / "extra")
        # QA round 1 of #1182: a page is .html or .htm in any case.
        (out / "Extra.HTM").write_text("<p>x</p>", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "Extra.HTM is not a page this build writes" not in text:
            failures.append(f"--check missed an extra .HTM page: {text!r}")
        (out / "Extra.HTM").unlink()
        # At the root base the published files (PUBLISHED) sit beside the pages and pass --check.
        (out / "llms.txt").write_text("# index\n", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check at the root refused a published file beside the pages: {text!r}")
        (out / "llms.txt").unlink()
        # #1189 QA: any other file at the root is refused, so a stray script cannot ship.
        for stray in ("assets/other.js", "notes.txt"):
            (out / stray).parent.mkdir(exist_ok=True)
            (out / stray).write_text("x\n", encoding="utf-8")
            rc, text = run("--check", "--out", str(out))
            if rc != 1 or f"{stray} is neither a page this build writes" not in text:
                failures.append(f"--check at the root accepted a stray {stray}: {text!r}")
            (out / stray).unlink()
        # At the root the 2 versioned release archive names pass in downloads/, and a latest name
        # there is refused; download_cases() holds the rest of download_problems()'s rule.
        archive = b"PK\x05\x06" + bytes(18)  # an empty zip: its end of central directory only
        (out / "downloads").mkdir()
        for name in ("secureconfig-1.0.1234.zip", "secureconfig-plugin-1.0.1234.zip"):
            (out / "downloads" / name).write_bytes(archive)
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check at the root refused the 2 versioned release archives: {text!r}")
        (out / "downloads" / "secureconfig-latest.zip").write_bytes(archive)
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "downloads/secureconfig-latest.zip is a latest name" not in text:
            failures.append(f"--check at the root accepted downloads/secureconfig-latest.zip: {text!r}")
        (out / "downloads" / "secureconfig-latest.zip").unlink()
        (out / "downloads" / "old").mkdir()
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "downloads/old is a folder" not in text:
            failures.append(f"--check at the root accepted an empty folder downloads/old: {text!r}")
        (out / "downloads" / "old").rmdir()
        # A downloads/ that cannot be listed is a read error (exit 2), not an empty folder. Root
        # lists a folder whatever its mode, so this case runs only as another user.
        if os.geteuid() != 0:
            (out / "downloads").chmod(0o300)
            try:
                rc, text = run("--check", "--out", str(out))
            finally:
                (out / "downloads").chmod(0o700)
            if rc != 2 or "cannot read" not in text:
                failures.append(f"--check at the root did not exit 2 on a downloads/ it cannot "
                                f"list: {rc} {text!r}")
        shutil.rmtree(out / "downloads")
        # The 2 generated hosted files are admitted at the root only when each equals, byte for
        # byte, what tools/gen_hosted.py writes from the release record and the allowlist read
        # beside the output folder; an edited copy, a missing one and one with nothing behind
        # it are refused, so the records pull request's committed files pass and nothing else.
        digest = hashlib.sha256(b"zip bytes\n").hexdigest()
        (d / "plugin").mkdir()
        (d / "plugin" / "plugin.json").write_text(json.dumps(
            {"name": "secureconfig", "description": "guides",
             "author": {"name": "Jeff Posluns", "url": "https://secureconfig.ai"}}),
            encoding="utf-8")
        (d / "releases").mkdir()
        record = (f"{digest}  secureconfig-1.0.1234.zip\n"
                  f"{digest}  secureconfig-plugin-1.0.1234.zip\n")
        (d / "releases" / "SHA256SUMS").write_text(record, encoding="utf-8")
        (d / "tools").mkdir()
        (d / "tools" / "redirects_allowlist.txt").write_text(
            "/old / 302\tthe old URL of the landing page\n", encoding="utf-8")
        (out / "downloads").mkdir()
        for name in ("secureconfig-1.0.1234.zip", "secureconfig-plugin-1.0.1234.zip"):
            (out / "downloads" / name).write_bytes(b"zip bytes\n")
        records = gen_hosted.read_records(d)
        (out / "_redirects").write_text(gen_hosted.redirects_text(d, records), encoding="utf-8")
        (out / "marketplace.json").write_text(gen_hosted.marketplace_text(d, records),
                                              encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check at the root refused the generated hosted files: {text!r}")
        # An unparsable plugin/plugin.json with a record behind it is a read error (exit 2) in 1
        # FAIL line, never a traceback.
        manifest = (d / "plugin" / "plugin.json").read_bytes()
        (d / "plugin" / "plugin.json").write_text("{\n", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 2 or "the plugin manifest" not in text or "Traceback" in text:
            failures.append(f"--check at the root did not exit 2 with 1 FAIL line on an "
                            f"unparsable plugin/plugin.json: {rc} {text!r}")
        # So is valid JSON nested past the interpreter's recursion limit, which json.loads
        # cannot parse.
        (d / "plugin" / "plugin.json").write_text("[" * 100000 + "]" * 100000 + "\n",
                                                  encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 2 or "nested too deeply to parse" not in text or "Traceback" in text:
            failures.append(f"--check at the root did not exit 2 with 1 FAIL line on a "
                            f"plugin/plugin.json nested too deeply to parse: {rc} {text!r}")
        (d / "plugin" / "plugin.json").write_bytes(manifest)
        data = (out / "marketplace.json").read_bytes()
        (out / "marketplace.json").write_bytes(data.replace(b'"sha256": "', b'"sha256": "0'))
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "marketplace.json does not equal what tools/gen_hosted.py writes" not in text:
            failures.append(f"--check at the root accepted an edited marketplace.json: {text!r}")
        (out / "marketplace.json").write_bytes(data)
        (out / "_redirects").write_bytes((out / "_redirects").read_bytes() + b"/x / 302\n")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "_redirects does not equal what tools/gen_hosted.py writes" not in text:
            failures.append(f"--check at the root accepted an edited _redirects: {text!r}")
        (out / "_redirects").unlink()
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "_redirects is missing" not in text:
            failures.append(f"--check at the root missed a missing _redirects: {text!r}")
        shutil.rmtree(d / "releases")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "marketplace.json exists, but" not in text:
            failures.append(f"--check at the root accepted a marketplace.json with no record "
                            f"behind it: {text!r}")
        (out / "marketplace.json").unlink()
        shutil.rmtree(out / "downloads")
        shutil.rmtree(d / "plugin")
        shutil.rmtree(d / "tools")
        # SPECIFICATION 4.1 items 0 and 3: the staged build written under draft/ beside the root
        # pages, as on the `draft` branch, is refused at the root, page and copied file alike.
        rc, text = run("--base", "/draft/", "--out", str(out / "draft"))
        if rc != 0:
            failures.append(f"a staged build under the root's draft/ failed: {text!r}")
        (out / "draft" / "assets" / "baseline").mkdir(parents=True)
        (out / "draft" / "assets" / "baseline" / "baseline.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if (rc != 1 or "draft/index.html is not a page this build writes" not in text
                or "draft/assets/baseline/baseline.css is neither" not in text):
            failures.append(f"--check at the root accepted a staged tree under draft/: {text!r}")
        shutil.rmtree(out / "draft")
        (out / "404.html").unlink()
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "404.html is missing" not in text:
            failures.append(f"--check missed a missing page: {text!r}")

        # The staging form refuses a stray file outside assets/baseline/ and allows the optional
        # assets/site.css (baseline README); tools/check_draft.py holds its grammar.
        staged = d / "draft"
        rc, text = run("--base", "/draft/", "--out", str(staged))
        if rc != 0:
            failures.append(f"a staged build into a scratch folder failed: {text!r}")
        # A staged build carries no release archive: downloads/ is a stray there.
        sized(staged / "downloads" / "secureconfig-1.0.1234.zip", 22)
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 1 or "downloads/secureconfig-1.0.1234.zip is neither" not in text:
            failures.append(f"staged --check accepted a release archive in downloads/: {text!r}")
        shutil.rmtree(staged / "downloads")
        (staged / "assets").mkdir()
        (staged / "assets" / "live.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 1 or "assets/live.css is neither a page this build writes" not in text:
            failures.append(f"staged --check missed a stray file outside assets/baseline/: {text!r}")
        (staged / "assets" / "live.css").unlink()
        (staged / "assets" / "baseline").mkdir()
        (staged / "assets" / "baseline" / "baseline.css").write_text("p{}", encoding="utf-8")
        (staged / "assets" / "site.css").write_text(".statement { --sw: 13.9; }\n", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 0:
            failures.append(f"staged --check refused assets/baseline/ or site.css, which are "
                            f"allowed: {text!r}")
        (staged / "assets" / "other.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--base", "/draft/", "--out", str(staged))
        if rc != 1 or "assets/other.css is neither" not in text:
            failures.append(f"staged --check accepted assets/other.css beside site.css: {text!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    rc, text = run("--base", "draft")
    if rc != 2 or "must start and end with /" not in text:
        failures.append(f"a base path without slashes was accepted: {text!r}")
    more, downloads = download_cases()
    failures += more
    failures += content_cases()

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(plants)} planted refusals and a description using the word on, the base "
          f"path at / and /draft/ with no /draft/ page at the root, the root's indexability, link "
          f"previews at their full values and canonicals, none on a staged build, the light and dark "
          f"switch and scheme.js on every page at both bases, the landing page's About line, the "
          f"install commands read from README.md only, with {install_cases} install-section cases "
          f"(mismatched fence lengths, an indented fence, a third block, the blocks swapped, the "
          f"shell block edited, CRLF and CR line endings and more), and "
          f"--check on a changed, an extra "
          f".html and .HTM page, a missing page, a root-base published file and strays, a staged "
          f"tree under the root's draft/, and the staged strays; the advisory at its dated name "
          f"with its summary and reporter details, and its plain-text copy (no markup, the "
          f"page's labels in order, every entry, 6 planted refusals, and --check on its change, "
          f"its absence and a stray .txt beside it); release archives in downloads/ (--check on "
          f"the 2 versioned names, a latest name and a folder at the root"
          f"{', a downloads/ it cannot list (exit 2)' if os.geteuid() != 0 else ''} and a staged "
          f"stray, and {downloads} release archive rule cases, the download_problems() fixtures "
          f"and the exact caps: both names, both latest names, wrong version forms, folders, "
          f"symbolic links{', a FIFO' if hasattr(os, 'mkfifo') else ''}"
          f"{', an unlistable folder' if os.geteuid() != 0 else ''}, an oversized file counted in "
          f"the total, the total cap and the 20 MiB and 200 MiB values)")
    print("  ok    the 2 generated hosted files at the root: admitted when byte-equal to the "
          "generator's output, refused when edited, missing or with no record behind them, and "
          "an unparsable plugin/plugin.json and one nested too deeply to parse each a read error "
          "(exit 2); a site-src/content.json nested too deeply to parse and one that is a JSON "
          "array each a read error")
    if os.geteuid() == 0:
        print("  note  run as root, so the 2 unlistable downloads/ cases were skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
