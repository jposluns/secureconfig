#!/usr/bin/env python3
"""Cases for scripts/build-site.py: its refusals, its base path, and its --check mode.

The refusals are SPECIFICATION section 12's: a page carrying a dash character (U+2010 to
U+2015, U+2212), an inline style or style= attribute, an inline script, an on* attribute or "what
this is" framing is never written. Each is planted in a real generated page and must be refused,
while the page as generated passes.
The base path must reach every internal link and asset at /draft/ and at /, and --check must
report a one-byte change, an extra page (.html or .htm in any case), a stray file outside
assets/baseline/ and a missing page in a build it did not write.
"""
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


def main():
    failures = []
    pages = build_site.Builder("/draft/").build()
    home = pages["index.html"]
    rail_page = pages["disclosure/index.html"]
    plants = [
        ("a static aria-current on a rail link",
         rail_page.replace('<li><a href="#d-1">', '<li><a href="#d-1" aria-current="true">', 1),
         "static aria-current"),
        ("a section rail without rail.js",
         rail_page.replace('<script src="/draft/assets/baseline/rail.js" defer></script>\n', "", 1),
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
         home.replace("</head>", '<script src="/draft/x.js">x()</script></head>', 1), "inline script"),
        ("an onclick attribute", home.replace('<p class="intro">', '<p class="intro" onclick="x()">', 1),
         "on* attribute"),
        ("a valueless onload attribute", home.replace("<body>", "<body onload>", 1), "on* attribute"),
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

    # The base path reaches every internal link and asset.
    root_pages = build_site.Builder("/").build()
    for base, built in (("/draft/", pages), ("/", root_pages)):
        for name, text in built.items():
            for needle in (f'href="{base}assets/baseline/baseline.css"', f'href="{base}guides/"',
                           f'src="{base}assets/baseline/logos/secureconfig.svg"'):
                if needle not in text:
                    failures.append(f"base {base}: {name} lacks {needle}")
    if "/draft/" in "".join(root_pages.values()):
        failures.append("base /: a page still names /draft/")
    if 'name="robots"' in root_pages["index.html"]:
        failures.append("base /: the home page still carries the draft's noindex")
    if 'name="robots"' not in root_pages["404.html"]:
        failures.append("base /: the 404 page lost its noindex")

    # --check against a build it did not write.
    d = Path(tempfile.mkdtemp())
    try:
        out = d / "draft"
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
        # QA round 1 of #1182: a page is .html or .htm in any case, and only assets/baseline/ may
        # hold files this build does not write.
        (out / "Extra.HTM").write_text("<p>x</p>", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "Extra.HTM is not a page this build writes" not in text:
            failures.append(f"--check missed an extra .HTM page: {text!r}")
        (out / "Extra.HTM").unlink()
        (out / "assets").mkdir()
        (out / "assets" / "live.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "assets/live.css is neither a page this build writes" not in text:
            failures.append(f"--check missed a stray file outside assets/baseline/: {text!r}")
        (out / "assets" / "live.css").unlink()
        (out / "assets" / "baseline").mkdir()
        (out / "assets" / "baseline" / "baseline.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check refused a file under assets/baseline/, which the pin gate "
                            f"owns: {text!r}")
        # QA round 2: the optional assets/site.css (baseline README) is allowed beside the pages;
        # tools/check_draft.py holds its grammar.
        (out / "assets" / "site.css").write_text(".statement { --sw: 13.9; }\n", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 0:
            failures.append(f"--check refused assets/site.css, which the baseline allows: {text!r}")
        (out / "assets" / "other.css").write_text("p{}", encoding="utf-8")
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "assets/other.css is neither" not in text:
            failures.append(f"--check accepted assets/other.css beside site.css: {text!r}")
        shutil.rmtree(out / "assets")
        (out / "404.html").unlink()
        rc, text = run("--check", "--out", str(out))
        if rc != 1 or "404.html is missing" not in text:
            failures.append(f"--check missed a missing page: {text!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    rc, text = run("--base", "draft")
    if rc != 2 or "must start and end with /" not in text:
        failures.append(f"a base path without slashes was accepted: {text!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(plants)} planted refusals, the base path at /draft/ and /, and --check on a "
          f"changed, an extra .html and .HTM page, a stray file, an allowed site.css and a missing page")
    return 0


if __name__ == "__main__":
    sys.exit(main())
