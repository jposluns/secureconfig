#!/usr/bin/env python3
"""Cases for tools/select_gates.py, the pull-request gate selector.

SCOPED: each case is a changed path of one scoped kind and the exact sections its selection must
be, written out here rather than read from the selector: a page, a page source, a served asset
that is not a script, a palette, site/llms.txt, a name that only begins like a script's, an
`.html`, a `.css` and a `.json` file under site-src/, a page named in upper case, a file under
site/ and one under site-src/ for each allowed ending (SITE_CONTENT, written out here) in upper
case, and each of the root project records CHANGELOG.md (with version-basis, llms-full, plugin and
generated-committed), TODO.md, DONE.md, DECISIONS.md and PENDING-DECISIONS.md. A list of scoped
paths, mixed, selects the union of their sections in the suite's order, and never every section.
Every scoped selection that holds generated-committed holds llms-full and plugin, and so does a
map entry that names generated-committed alone. The needs come from the suite's `# depends:`
lines, which tools/run_all_checks.sh --sections reads too: they are exactly
generated-committed's llms-full and plugin, each a section of the suite, and a line in another
shape, or a second line for one section, is refused.

EVERY SECTION: each kind of path that is not scoped content selects every section, through the
pattern the case names or through no pattern: under site/ or site-src/, every file outside the
allowlist (a `_headers` file, the CSP, or a `_redirects` file at any depth, nested ones, ones
under site-src/ and a `_headers` file at the root included; a script or source map at any depth,
in any case, `.JS` and `.js.map` included; site-src/notes.js, site-src/action.yml,
site-src/guide.md, a name with no suffix, an allowed ending followed by more text), a guide (a
new one included), README.md,
controls-reference.md, a file under plugin/, tools/, scripts/, .baseline/, .aiqt/ and .github/, a
requirements file at any depth (one under site/ included), CLAUDE.md, AGENTS.md, CONTRIBUTING.md,
SECURITY.md, README.sources.md, NOTICE, LICENSE, VERSION, a guide request, an unmapped path, a
path git quotes, an empty list and a list of blank lines; so do scoped content beside any of them
and a map naming a section the suite does not have.

THE MAP AND THE CHECKOUT: every pattern in the selector's MAP is the first match of at least one
case path, so a pattern added without a case is a finding; every section MAP names is a
`# section: NAME` line of tools/run_all_checks.sh; no section name is used twice; the root
Markdown the suite's not_a_guide list names maps as a project record only for the five records;
every other root Markdown file in this checkout and every file under plugin/, tools/, scripts/,
.baseline/, .aiqt/ and .github/ selects every section; every file under site/ and site-src/ is
scoped exactly when it is allowed content (its name ends in an allowed ending in any case, and is
not `_headers`, `_redirects` or a requirements file), and at least one file under site/ is not.

THE COMMAND: `printf 'site/index.html\\n' | python3 tools/select_gates.py` exits 0 and prints the
site selection, one name per line; `site/_headers`, `site/assets/baseline/scheme.js`,
`site/assets/APP.MJS`, `site-src/notes.js`, `mfa.md`, `tools/check_sitemap.py` and empty input
each print every section.

Nothing here reads git history or the network. Exit 0 ok, 1 on a finding.
"""
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import select_gates as sg  # noqa: E402

SUITE_TEXT = sg.SUITE.read_text(encoding="utf-8")
NAMES = sg.suite_sections(SUITE_TEXT)
DEPENDS = sg.suite_depends(SUITE_TEXT)
NOT_A_GUIDE = re.search(r"    (CONTRIBUTING\.md\|.*?)\) return 0", SUITE_TEXT)[1].split("|")
RECORDS = ("CHANGELOG.md", "TODO.md", "DONE.md", "DECISIONS.md", "PENDING-DECISIONS.md")
ANY = ("secrets", "local-links", "llms-full-links")
SITE = ("copy-buttons", "baseline-pin", "palette", "site-build", "site-draft", "pages-build",
        "site-csp", "security-txt", "sitemap", "guide-wiring", "guide-categories", "llms-full",
        "plugin", "generated-committed", "prose-conventions", "aiqt-baseline") + ANY
MARKDOWN = ("bare-urls", "verify-tls", "guard-conventions", "unfiltered-ss", "prose-conventions",
            "shell-blocks", "bracket-ranges", "pinned-citations", "placeholders",
            "aiqt-baseline") + ANY
# CHANGELOG.md also feeds version-basis, which reads its newest dated heading, the two bundle
# builds that run it, and generated-committed.
CHANGELOG = MARKDOWN + ("changelog-prs", "changelog-format", "version-basis", "llms-full",
                        "plugin", "generated-committed")
# The directories whose every file is code, checks or a bundle, and so selects every section.
EVERY_DIRS = ("plugin", "tools", "scripts", ".baseline", ".aiqt", ".github")
# The only endings, in any case, that make a file under site/ or site-src/ content.
SITE_CONTENT = (".html", ".css", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico",
                ".woff2", ".txt", ".xml")


def is_site_content(path):
    """Whether a path under site/ or site-src/ is allowed content rather than every section."""
    name = path.rsplit("/", 1)[-1]
    return (path.startswith(("site/", "site-src/")) and name.lower().endswith(SITE_CONTENT)
            and name not in ("_headers", "_redirects")
            and "requirements" not in name.lower())


# (scoped kind, changed path, the exact sections its selection must be)
SCOPED = (
    ("a page", "site/index.html", SITE),
    ("a nested page", "site/disclosure/index.html", SITE),
    ("a page named in upper case", "site/guides/INDEX.HTML", SITE),
    ("a page source", "site-src/content.json", SITE),
    ("an .html file under site-src/", "site-src/pages/notes.html", SITE),
    ("a .css file under site-src/", "site-src/notes.css", SITE),
    ("a .json file under site-src/", "site-src/notes.json", SITE),
    ("a served stylesheet", "site/assets/baseline/fonts.css", SITE),
    ("a served image", "site/assets/baseline/logos/secureconfig.svg", SITE),
    ("a palette", "site/assets/baseline/palettes.css", SITE),
    ("the llms.txt index", "site/llms.txt", SITE),
    ("a name that only begins like a script's", "site/assets/baseline/scheme.json", SITE),
    *((f"an allowed ending {ending} under {top}/, in upper case",
       f"{top}/assets/x{ending.upper()}", SITE)
      for top in ("site", "site-src") for ending in SITE_CONTENT),
    ("CHANGELOG.md", "CHANGELOG.md", CHANGELOG),
    ("TODO.md", "TODO.md", MARKDOWN + ("todo-rows",)),
    ("DONE.md", "DONE.md", MARKDOWN),
    ("DECISIONS.md", "DECISIONS.md", MARKDOWN),
    ("PENDING-DECISIONS.md", "PENDING-DECISIONS.md", MARKDOWN),
)

# Lists of scoped paths, mixed: each selects the union of its paths' sections.
SCOPED_LISTS = (
    ["site/index.html", "site-src/content.json"],
    ["site/assets/baseline/palettes.css", "CHANGELOG.md"],
    list(RECORDS),
    ["CHANGELOG.md", "TODO.md", "site/index.html", "site-src/content.json"],
)

# (every-section kind, changed paths, the MAP pattern a single path must match first, or None)
EVERY = (
    ("the served headers, the CSP", ["site/_headers"], "**/_headers"),
    ("a nested headers file", ["site/guides/_headers"], "**/_headers"),
    ("a headers file under site-src/", ["site-src/_headers"], "**/_headers"),
    ("a headers file at the root", ["_headers"], "**/_headers"),
    ("the redirects", ["site/_redirects"], "**/_redirects"),
    ("a nested redirects file", ["site/assets/baseline/_redirects"], "**/_redirects"),
    ("a redirects file under site-src/", ["site-src/_redirects"], "**/_redirects"),
    ("a served script", ["site/assets/baseline/scheme.js"], None),
    ("another served script", ["site/assets/baseline/copy.js"], None),
    ("a script at the site's root", ["site/app.js"], None),
    ("a script named in upper case", ["site/assets/baseline/APP.JS"], None),
    ("an ES module", ["site/assets/baseline/app.mjs"], None),
    ("an ES module named in mixed case", ["site/assets/APP.Mjs"], None),
    ("a CommonJS module", ["site/assets/baseline/app.cjs"], None),
    ("a script's source map", ["site/assets/baseline/scheme.js.map"], None),
    ("a source map named in upper case", ["site/assets/baseline/SCHEME.JS.MAP"], None),
    ("a script under site-src/", ["site-src/notes.js"], None),
    ("an action under site-src/", ["site-src/action.yml"], None),
    ("Markdown under site-src/", ["site-src/guide.md"], None),
    ("Markdown under site/", ["site/assets/baseline/NOTICE.md"], None),
    ("a name with no suffix under site-src/", ["site-src/Makefile"], None),
    ("a name with no suffix under site/", ["site/assets/baseline/LICENSE"], None),
    ("a name that only ends like _headers", ["site/docs/old_headers"], None),
    ("an allowed ending followed by more text", ["site/index.html.bak"], None),
    ("a served script beside a page", ["site/index.html", "site/assets/baseline/rail.js"], None),
    ("Markdown under site-src/ beside a page source",
     ["site-src/content.json", "site-src/guide.md"], None),
    ("the served headers beside a palette", ["site/assets/baseline/palettes.css", "site/_headers"],
     None),
    ("a guide", ["mfa.md"], None),
    ("the exposure index", ["exposure-index.md"], None),
    ("a new guide", ["new-service.md"], None),
    ("README.md", ["README.md"], None),
    ("controls-reference.md", ["controls-reference.md"], None),
    ("the plugin manifest", ["plugin/plugin.json"], None),
    ("a plugin reference", ["plugin/skills/secure-deployment-config/references/nginx.md"], None),
    ("the runner", ["tools/run_all_checks.sh"], None),
    ("the selector", ["tools/select_gates.py"], None),
    ("the selector's test", ["tools/test_select_gates.py"], None),
    ("a gate", ["tools/check_sitemap.py"], None),
    ("a site gate", ["tools/check_csp_hashes.py"], None),
    ("a shared helper", ["tools/_markdown.py"], None),
    ("a version-basis list", ["tools/version_basis_guides.txt"], None),
    ("a tools fixture", ["tools/fixtures/lychee.json"], None),
    ("the gate requirements", ["tools/requirements-gates.txt"], "**/*requirements*"),
    ("the site builder", ["scripts/build-site.py"], None),
    ("the pages build", ["scripts/pages-build.sh"], None),
    ("Markdown under scripts/", ["scripts/card/TAGS.md"], None),
    ("the baseline pin", [".baseline/pin.toml"], None),
    ("a baseline gate", [".baseline/check_palette.py"], None),
    ("the gensrc record", [".aiqt/gensrc.json"], None),
    ("an AIQT hook", [".aiqt/hooks/hooks.json"], None),
    ("a workflow", [".github/workflows/checks.yml"], None),
    ("a new file under .github", [".github/dependabot.yml"], None),
    ("a root requirements file", ["requirements.txt"], "**/*requirements*"),
    ("a requirements file under site/", ["site/requirements.txt"], "**/*requirements*"),
    ("a dev-requirements file under site-src/", ["site-src/dev-requirements.txt"], "**/*requirements*"),
    ("CLAUDE.md", ["CLAUDE.md"], None),
    ("AGENTS.md", ["AGENTS.md"], None),
    ("CONTRIBUTING.md", ["CONTRIBUTING.md"], None),
    ("SECURITY.md", ["SECURITY.md"], None),
    ("README.sources.md", ["README.sources.md"], None),
    ("NOTICE", ["NOTICE"], None),
    ("LICENSE", ["LICENSE"], None),
    ("VERSION", ["VERSION"], None),
    ("a guide request", ["requests/TEMPLATE.md"], None),
    (".gitignore", [".gitignore"], None),
    ("an unmapped path", ["docs/notes.txt"], None),
    ("Markdown in an unmapped directory", ["docs/guide.md"], None),
    ("a path git quotes", ['"site/caf\\303\\251.html"'], None),
    ("site content beside a guide", ["site/index.html", "nginx.md"], None),
    ("a project record beside a tool", ["CHANGELOG.md", "tools/check_todo_rows.py"], None),
    ("a scoped path after an unscoped one", ["NOTICE", "CHANGELOG.md"], None),
    ("an empty list", [], None),
    ("a list of blank lines", ["", ""], None),
)


def check_cases(failures):
    count = 0
    for kind, path, want in SCOPED:
        chosen, notes = sg.select([path], NAMES, DEPENDS)
        count += 1
        if sorted(chosen) != sorted(set(want)) or notes[-1].endswith("every section"):
            failures.append(f"{kind} ({path}) should select exactly {sorted(set(want))!r}: "
                            f"{chosen!r}, {notes!r}")
    for paths in SCOPED_LISTS:
        chosen, notes = sg.select(paths, NAMES, DEPENDS)
        union = {n for p in paths for _, path, want in SCOPED if path == p for n in want}
        count += 1
        if chosen != [n for n in NAMES if n in union] or chosen == NAMES:
            failures.append(f"{paths!r} should select the union of its paths' sections in suite "
                            f"order: {chosen!r}, {notes!r}")
    # generated-committed skips its rebuild on a clean tree because llms-full and plugin ran.
    for paths in [[path] for _, path, _ in SCOPED] + list(SCOPED_LISTS):
        chosen, _ = sg.select(paths, NAMES, DEPENDS)
        count += 1
        if "generated-committed" in chosen and not {"llms-full", "plugin"} <= set(chosen):
            failures.append(f"{paths!r} selects generated-committed without llms-full and "
                            f"plugin: {chosen!r}")
    saved = sg.COMPILED
    alone = ("generated-committed",)
    sg.COMPILED = (("x.md", sg.pattern_re("x.md", alone), alone),)
    try:
        chosen, _ = sg.select(["x.md"], NAMES, DEPENDS)
    finally:
        sg.COMPILED = saved
    count += 1
    if not {"generated-committed", "llms-full", "plugin"} <= set(chosen) or chosen == NAMES:
        failures.append(f"a map entry naming generated-committed alone should also select "
                        f"llms-full and plugin: {chosen!r}")
    for kind, paths, pattern in EVERY:
        chosen, notes = sg.select(paths, NAMES, DEPENDS)
        count += 1
        if chosen != NAMES or not notes[-1].endswith("every section"):
            failures.append(f"{kind} ({paths!r}) should select every section: {chosen!r}, "
                            f"{notes!r}")
        if len(paths) == 1 and sg.sections_for(paths[0]) != (pattern, sg.ALL):
            failures.append(f"{kind} ({paths[0]}) should select every section through "
                            f"{pattern!r}: {sg.sections_for(paths[0])!r}")
    return count


def files_under(top):
    """The files under one directory of this checkout, as paths relative to the root."""
    base = sg.ROOT / top
    return sorted(p.relative_to(sg.ROOT).as_posix() for p in base.rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts)


def check_map(failures):
    count = 0
    first = {sg.sections_for(path)[0] for _, path, _ in SCOPED}
    first |= {sg.sections_for(p)[0] for _, paths, _ in EVERY for p in paths}
    unexercised = [p for p, _ in sg.MAP if p not in first]
    count += 1
    if unexercised:
        failures.append(f"MAP patterns no case reaches as a first match: {unexercised!r}")
    named = {n for _, sections in sg.MAP if sections != sg.ALL for n in sections}
    named |= set(sg.ANY_PATH)
    count += 1
    if named - set(NAMES):
        failures.append(f"MAP names sections the suite does not have: {sorted(named - set(NAMES))!r}")
    count += 1
    if len(NAMES) != len(set(NAMES)) or len(NAMES) < 50:
        failures.append(f"the suite's section names are duplicated or too few: {NAMES!r}")
    markers = re.findall(r"^# section: .*$", SUITE_TEXT, re.M)
    count += 1
    if len(markers) != len(NAMES):
        failures.append(f"a `# section:` line is not `# section: NAME`: "
                        f"{[m for m in markers if not sg.SECTION.fullmatch(m)]!r}")
    count += 1
    if DEPENDS != {"generated-committed": ("llms-full", "plugin")}:
        failures.append(f"the suite's `# depends:` lines should give generated-committed exactly "
                        f"llms-full and plugin: {DEPENDS!r}")
    needs = {n for section, wanted in DEPENDS.items() for n in (section, *wanted)}
    count += 1
    if needs - set(NAMES):
        failures.append(f"a `# depends:` line names sections the suite does not have: "
                        f"{sorted(needs - set(NAMES))!r}")
    for text in ("# depends: generated-committed llms-full plugin\n",
                 "# depends: generated-committed: llms-full, plugin\n",
                 "# depends: generated-committed:\n",
                 "# depends: a: b\n# depends: a: c\n"):
        count += 1
        try:
            sg.suite_depends(text)
        except ValueError:
            continue
        failures.append(f"a `# depends:` line in another shape, or a second one for a section, "
                        f"should be refused: {text!r}")
    count += 1
    if SUITE_TEXT.count("\n# end of sections\n") != 1:
        failures.append("tools/run_all_checks.sh does not have exactly 1 `# end of sections` line")
    for name in NOT_A_GUIDE:
        pattern, sections = sg.sections_for(name)
        count += 1
        if name in RECORDS:
            ok = pattern == name and sections != sg.ALL and "guide-shape" not in sections
        else:
            ok = (pattern, sections) == (None, sg.ALL)
        if not ok:
            failures.append(f"{name} is in the suite's not_a_guide list but maps as {pattern!r}: "
                            f"{sections!r}")
    count += 1
    if set(RECORDS) - set(NOT_A_GUIDE):
        failures.append(f"project records missing from the suite's not_a_guide list: "
                        f"{sorted(set(RECORDS) - set(NOT_A_GUIDE))!r}")
    others = sorted(p.name for p in sg.ROOT.glob("*.md") if p.name not in RECORDS)
    scoped = [(g, sg.sections_for(g)) for g in others if sg.sections_for(g)[1] != sg.ALL]
    count += 1
    if len(others) < 10 or scoped:
        failures.append(f"each of the {len(others)} root Markdown files other than the project "
                        f"records should select every section: {scoped!r}")
    for top in EVERY_DIRS:
        files = files_under(top)
        scoped = [f for f in files if sg.sections_for(f)[1] != sg.ALL]
        count += 1
        if not files or scoped:
            failures.append(f"each of the {len(files)} files under {top}/ should select every "
                            f"section: {scoped!r}")
    for top in ("site", "site-src"):
        files = files_under(top)
        wrong = [f for f in files if (sg.sections_for(f)[1] == sg.ALL) == is_site_content(f)]
        count += 1
        if not files or wrong:
            failures.append(f"each of the {len(files)} files under {top}/ should be scoped exactly "
                            f"when it is allowed content: {wrong!r}")
    other = [f for f in files_under("site") if not is_site_content(f)]
    count += 1
    if not other:
        failures.append("every file under site/ is allowed content, so the refusal cases reach "
                        "nothing in this checkout")
    chosen, _ = sg.select(["site/index.html", "CHANGELOG.md"], NAMES, DEPENDS)
    count += 1
    if chosen != [n for n in NAMES if n in set(chosen)]:
        failures.append(f"the selection is not in the suite's order: {chosen!r}")
    short = [n for n in NAMES if n != "changelog-format"]
    chosen, notes = sg.select(["CHANGELOG.md"], short, DEPENDS)
    count += 1
    if chosen != short or "does not have" not in notes[-1]:
        failures.append(f"a map naming a section the suite lacks should select every section: "
                        f"{chosen!r}, {notes!r}")
    return count


def check_command(failures):
    count = 0
    for stdin, want in (("site/index.html\n", sg.select(["site/index.html"], NAMES, DEPENDS)[0]),
                        ("site/_headers\n", NAMES), ("site/assets/baseline/scheme.js\n", NAMES),
                        ("site/assets/APP.MJS\n", NAMES), ("site-src/notes.js\n", NAMES),
                        ("mfa.md\n", NAMES),
                        ("tools/check_sitemap.py\n", NAMES), ("", NAMES)):
        r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "select_gates.py")],
                           input=stdin, capture_output=True, text=True, timeout=60)
        count += 1
        if r.returncode != 0 or r.stdout.split("\n")[:-1] != want or "select_gates: " not in r.stderr:
            failures.append(f"select_gates.py on {stdin!r}: exit {r.returncode}, stdout "
                            f"{r.stdout!r}, stderr {r.stderr!r}")
    return count


def main():
    failures = []
    count = check_cases(failures) + check_map(failures) + check_command(failures)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {count} recorded cases for the gate selector")
    return 0


if __name__ == "__main__":
    sys.exit(main())
