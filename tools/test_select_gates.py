#!/usr/bin/env python3
"""Cases for tools/select_gates.py, the pull-request gate selector.

SCOPED: each case is a changed path of one scoped kind and the exact sections its selection must
be, written out here rather than read from the selector: a page, a page source, a served asset
that is not a script, a palette, site/llms.txt, a name that only begins like a script's, a name
that only ends like `_headers`, a script under site-src/, and each of the root project records
CHANGELOG.md, TODO.md, DONE.md, DECISIONS.md and PENDING-DECISIONS.md. A list of scoped paths,
mixed, selects the union of their sections in the suite's order, and never every section.

EVERY SECTION: each kind of path that is not scoped content selects every section, through the
pattern the case names or through no pattern: the code under site/ (a `_headers` file, the CSP,
or a `_redirects` file at any depth, nested ones included; a file ending in `.js`, `.mjs`, `.cjs`
or `.map` at any depth, in any case, `.JS` and `.js.map` included), a guide (a new one included),
README.md, controls-reference.md, a file under plugin/, tools/, scripts/, .baseline/, .aiqt/ and
.github/, a requirements file at any depth (one under site/ included), CLAUDE.md, AGENTS.md,
CONTRIBUTING.md, SECURITY.md, README.sources.md, NOTICE, LICENSE, VERSION, a guide request, an
unmapped path, a path git quotes, an empty list and a list of blank lines; so do scoped content
beside any of them and a map naming a section the suite does not have.

THE MAP AND THE CHECKOUT: every pattern in the selector's MAP is the first match of at least one
case path, so a pattern added without a case is a finding; every section MAP names is a
`# section: NAME` line of tools/run_all_checks.sh; no section name is used twice; the root
Markdown the suite's not_a_guide list names maps as a project record only for the five records;
every other root Markdown file in this checkout and every file under plugin/, tools/, scripts/,
.baseline/, .aiqt/ and .github/ selects every section; every file under site/ that is code
(named `_headers` or `_redirects`, or ending in `.js`, `.mjs`, `.cjs` or `.map` in any case)
selects every section, and there is at least one; and every other file under site/ and every
file under site-src/ is scoped.

THE COMMAND: `printf 'site/index.html\\n' | python3 tools/select_gates.py` exits 0 and prints the
site selection, one name per line; `site/_headers`, `site/assets/baseline/scheme.js`,
`site/assets/APP.MJS`, `mfa.md`, `tools/check_sitemap.py` and empty input each print every
section.

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
NOT_A_GUIDE = re.search(r"    (CONTRIBUTING\.md\|.*?)\) return 0", SUITE_TEXT)[1].split("|")
RECORDS = ("CHANGELOG.md", "TODO.md", "DONE.md", "DECISIONS.md", "PENDING-DECISIONS.md")
ANY = ("secrets", "local-links", "llms-full-links")
SITE = ("copy-buttons", "baseline-pin", "palette", "site-build", "site-draft", "pages-build",
        "site-csp", "security-txt", "sitemap", "guide-wiring", "guide-categories", "llms-full",
        "generated-committed", "prose-conventions", "aiqt-baseline") + ANY
MARKDOWN = ("bare-urls", "verify-tls", "guard-conventions", "unfiltered-ss", "prose-conventions",
            "shell-blocks", "bracket-ranges", "pinned-citations", "placeholders",
            "aiqt-baseline") + ANY
# The directories whose every file is code, checks or a bundle, and so selects every section.
EVERY_DIRS = ("plugin", "tools", "scripts", ".baseline", ".aiqt", ".github")
# The code under site/, which selects every section: the served headers (the CSP), the redirects
# at any depth, and the served scripts and their source maps in any case.
SITE_CODE_NAMES = ("_headers", "_redirects")
SITE_CODE_ENDINGS = (".js", ".mjs", ".cjs", ".map")


def is_site_code(path):
    """Whether a path under site/ is code rather than content."""
    name = path.rsplit("/", 1)[-1]
    return path.startswith("site/") and (name in SITE_CODE_NAMES
                                         or name.lower().endswith(SITE_CODE_ENDINGS))


# (scoped kind, changed path, the exact sections its selection must be)
SCOPED = (
    ("a page", "site/index.html", SITE),
    ("a nested page", "site/disclosure/index.html", SITE),
    ("a page source", "site-src/content.json", SITE),
    ("a served stylesheet", "site/assets/baseline/fonts.css", SITE),
    ("a served image", "site/assets/baseline/logos/secureconfig.svg", SITE),
    ("a palette", "site/assets/baseline/palettes.css", SITE),
    ("the llms.txt index", "site/llms.txt", SITE),
    ("a name that only begins like a script's", "site/assets/baseline/scheme.json", SITE),
    ("a name that only ends like _headers", "site/docs/old_headers", SITE),
    ("a script under site-src/", "site-src/notes.js", SITE),
    ("CHANGELOG.md", "CHANGELOG.md", MARKDOWN + ("changelog-prs", "changelog-format")),
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
    ("the served headers, the CSP", ["site/_headers"], "site/**/_headers"),
    ("a nested headers file", ["site/guides/_headers"], "site/**/_headers"),
    ("the redirects", ["site/_redirects"], "site/**/_redirects"),
    ("a nested redirects file", ["site/assets/baseline/_redirects"], "site/**/_redirects"),
    ("a served script", ["site/assets/baseline/scheme.js"], "site/**/*.js"),
    ("another served script", ["site/assets/baseline/copy.js"], "site/**/*.js"),
    ("a script at the site's root", ["site/app.js"], "site/**/*.js"),
    ("a script named in upper case", ["site/assets/baseline/APP.JS"], "site/**/*.js"),
    ("an ES module", ["site/assets/baseline/app.mjs"], "site/**/*.mjs"),
    ("an ES module named in mixed case", ["site/assets/APP.Mjs"], "site/**/*.mjs"),
    ("a CommonJS module", ["site/assets/baseline/app.cjs"], "site/**/*.cjs"),
    ("a script's source map", ["site/assets/baseline/scheme.js.map"], "site/**/*.map"),
    ("a source map named in upper case", ["site/assets/baseline/SCHEME.JS.MAP"], "site/**/*.map"),
    ("a served script beside a page", ["site/index.html", "site/assets/baseline/rail.js"], None),
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
    ("the gate requirements", ["tools/requirements-gates.txt"], "**/requirements*"),
    ("the site builder", ["scripts/build-site.py"], None),
    ("the pages build", ["scripts/pages-build.sh"], None),
    ("Markdown under scripts/", ["scripts/card/TAGS.md"], None),
    ("the baseline pin", [".baseline/pin.toml"], None),
    ("a baseline gate", [".baseline/check_palette.py"], None),
    ("the gensrc record", [".aiqt/gensrc.json"], None),
    ("an AIQT hook", [".aiqt/hooks/hooks.json"], None),
    ("a workflow", [".github/workflows/checks.yml"], None),
    ("a new file under .github", [".github/dependabot.yml"], None),
    ("a root requirements file", ["requirements.txt"], "**/requirements*"),
    ("a requirements file under site/", ["site/requirements.txt"], "**/requirements*"),
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
        chosen, notes = sg.select([path], NAMES)
        count += 1
        if sorted(chosen) != sorted(set(want)) or notes[-1].endswith("every section"):
            failures.append(f"{kind} ({path}) should select exactly {sorted(set(want))!r}: "
                            f"{chosen!r}, {notes!r}")
    for paths in SCOPED_LISTS:
        chosen, notes = sg.select(paths, NAMES)
        union = {n for p in paths for _, path, want in SCOPED if path == p for n in want}
        count += 1
        if chosen != [n for n in NAMES if n in union] or chosen == NAMES:
            failures.append(f"{paths!r} should select the union of its paths' sections in suite "
                            f"order: {chosen!r}, {notes!r}")
    for kind, paths, pattern in EVERY:
        chosen, notes = sg.select(paths, NAMES)
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
        wrong = [f for f in files if (sg.sections_for(f)[1] == sg.ALL) != is_site_code(f)]
        count += 1
        if not files or wrong:
            failures.append(f"each of the {len(files)} files under {top}/ should be scoped unless "
                            f"it is code under site/, which selects every section: {wrong!r}")
    code = [f for f in files_under("site") if is_site_code(f)]
    count += 1
    if not code:
        failures.append("no file under site/ is code (`_headers`, `_redirects` or a script or "
                        "source map), so the code cases reach nothing in this checkout")
    chosen, _ = sg.select(["site/index.html", "CHANGELOG.md"], NAMES)
    count += 1
    if chosen != [n for n in NAMES if n in set(chosen)]:
        failures.append(f"the selection is not in the suite's order: {chosen!r}")
    short = [n for n in NAMES if n != "changelog-format"]
    chosen, notes = sg.select(["CHANGELOG.md"], short)
    count += 1
    if chosen != short or "does not have" not in notes[-1]:
        failures.append(f"a map naming a section the suite lacks should select every section: "
                        f"{chosen!r}, {notes!r}")
    return count


def check_command(failures):
    count = 0
    for stdin, want in (("site/index.html\n", sg.select(["site/index.html"], NAMES)[0]),
                        ("site/_headers\n", NAMES), ("site/assets/baseline/scheme.js\n", NAMES),
                        ("site/assets/APP.MJS\n", NAMES), ("mfa.md\n", NAMES),
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
