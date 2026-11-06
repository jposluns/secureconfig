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
"""
import html
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SCRIPT = ROOT / "scripts" / "build-site.py"
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
        hidden = name == "404.html"
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
        if name == "404.html":
            if 'property="og:' in head or 'name="twitter:' in head:
                failures.append(f"base /: {name} carries link-preview tags")
            if 'rel="canonical"' in head or 'name="description"' in head:
                failures.append("base /: 404.html carries a canonical or a description")
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
          f"tree under the root's draft/, and the staged strays")
    return 0


if __name__ == "__main__":
    sys.exit(main())
