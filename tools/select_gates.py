#!/usr/bin/env python3
"""Name the sections of tools/run_all_checks.sh that a pull request's changes affect.

The owner's rulings of 2026-11-03 (DECISIONS.md): CI looks only at what changed, the whole suite
runs weekly, and the scoped path is for web site content changes mandated by the maintainer, such
as simple changes and the colour palette; code is not content. This reads the changed paths, one
per line on standard input, the way `git diff --name-only --no-renames BASE...HEAD` prints them,
and prints the names of the sections to run, one per line in the suite's order, for
`tools/run_all_checks.sh --sections`. On standard error it prints, for each path, the sections it
selected, so the CI log shows why.

SCOPED CONTENT is the only content that runs less than every section, and it is an allowlist
that fails closed: a file under site/ or site-src/ (the pages, their sources, the served
stylesheets, fonts and images, and the palettes) whose name ends, in any case, in one of
SITE_CONTENT (.html, .css, .json, .svg, .png, .jpg, .jpeg, .webp, .ico, .woff2, .txt or .xml)
and is not `_headers`, `_redirects` or a requirements file, and the root project records
CHANGELOG.md, TODO.md, DONE.md, DECISIONS.md and PENDING-DECISIONS.md. Every other file under
site/ or site-src/ runs every section: `_headers` (the CSP and the other served headers) and
`_redirects` at any depth, a requirements file even with a listed suffix, the scripts and their
source maps, Markdown, YAML such as an action.yml, any type not in SITE_CONTENT and a name with
no suffix. Every other path runs every section too: every guide, README.md, controls-reference.md,
plugin/, every file under tools/, scripts/, .baseline/, .aiqt/ and .github/, any requirements
file, CLAUDE.md, AGENTS.md, CONTRIBUTING.md, SECURITY.md, NOTICE, LICENSE, VERSION and any other
path.

THE MAP is MAP below, the one place it is written: a path takes the sections of the first pattern
it matches, and a path that matches no pattern takes every section. Every scoped path also takes
ANY_PATH, the sections that read every file (the secrets scan) or resolve links to any path (a
removed or renamed file can break a link elsewhere). A pattern's `*` matches within one path
segment and `**/` any number of whole segments, including none. An ALL pattern matches in any
case, since matching more paths only runs more sections; a scoped pattern matches case exactly,
except a name ending after a `*` in its last segment, which matches in any case, so
`site/**/*.html` takes INDEX.HTML too. A section belongs to a scoped path when it reads that
path: a project record feeds the Markdown gates, and site/ and site-src/ feed the site gates.
CHANGELOG.md also feeds version-basis, llms-full, plugin and generated-committed:
tools/version_basis.py reads its newest dated heading, and both bundle builds run that check and
list it as an input.

DEPENDS: a section that relies on others has a `# depends: NAME: NEED...` line in the suite, the
one place the table is written; the suite's --sections reads the same lines and adds the needs
itself. generated-committed skips its own rebuild on a clean tree because the llms-full and
plugin sections before it already rebuilt HEAD, so a selection that holds generated-committed
also holds llms-full and plugin. A `# depends:` line in any other shape stops the selection
with exit 2, like an unreadable suite.

FAIL SAFE: every section runs when the list is empty, when a path matches no pattern (a file under
site/ or site-src/ outside the allowlist included), and when a path matches an ALL pattern (a
requirements file, even under site/, and `_headers` or `_redirects` at any depth, which the ALL
patterns name before the site content). A path git quotes (a name with unusual characters)
matches nothing, so it runs every section too. The section names come from the suite's own
`# section: NAME` lines; tools/test_select_gates.py holds MAP to them, and if MAP names one the
suite no longer has, every section runs and a warning says so. The selection only chooses; the
gates still decide. Exit 0 with the names printed, 2 when the suite cannot be read.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tools" / "run_all_checks.sh"
SECTION = re.compile(r"^# section: ([a-z0-9-]+)$", re.M)
# A section's needs: `# depends: NAME: NEED NEED...`, read by the suite's --sections too.
DEPENDS_LINE = re.compile(r"# depends: ([a-z0-9-]+): ([a-z0-9-]+(?: [a-z0-9-]+)*)")

ALL = "ALL"
# Every scoped path: the secrets scan reads every file, and the two link gates resolve links to
# any path in the checkout.
ANY_PATH = ("secrets", "local-links", "llms-full-links")
# The gates that read Markdown wherever it is tracked (each skips some directories of its own).
MARKDOWN = ("bare-urls", "verify-tls", "guard-conventions", "unfiltered-ss", "prose-conventions",
            "shell-blocks", "bracket-ranges", "pinned-citations", "placeholders", "aiqt-baseline")
# The generated site and what checks or builds it, site/llms.txt and site/llms-full.txt included.
SITE = ("copy-buttons", "baseline-pin", "palette", "site-build", "site-draft", "pages-build",
        "site-csp", "security-txt", "sitemap", "guide-wiring", "guide-categories", "llms-full",
        "generated-committed", "prose-conventions", "aiqt-baseline")
# The only name endings, in any case, that make a file under site/ or site-src/ content.
SITE_CONTENT = (".html", ".css", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico",
                ".woff2", ".txt", ".xml")

MAP = (
    # Fail safe: a requirements file at any depth, site/ included, pins packages the gates run on;
    # any name containing "requirements" (dev-requirements.txt included) counts.
    ("**/*requirements*", ALL),
    # The CSP and the other served headers, and the redirects, at any depth.
    ("**/_headers", ALL),
    ("**/_redirects", ALL),
    # Site content, an allowlist: the pages, their sources, the served stylesheets, fonts and
    # images, and the palettes. Any other file under site/ or site-src/ (a script, a source map,
    # Markdown, YAML, an unknown type or a name with no suffix) matches nothing here and runs every
    # section.
    *((f"{top}/**/*{ending}", SITE) for top in ("site", "site-src") for ending in SITE_CONTENT),
    # The root project records. Every other path, code and guides included, matches nothing here
    # and runs every section. tools/version_basis.py reads CHANGELOG.md's newest dated heading,
    # and the llms-full and plugin builds run it.
    ("CHANGELOG.md", MARKDOWN + ("changelog-prs", "changelog-format", "version-basis",
                                 "llms-full", "plugin", "generated-committed")),
    ("TODO.md", MARKDOWN + ("todo-rows",)),
    ("DONE.md", MARKDOWN),
    ("DECISIONS.md", MARKDOWN),
    ("PENDING-DECISIONS.md", MARKDOWN),
)


def pattern_re(pattern, sections):
    """A compiled full-path match for one MAP pattern, in any case when it selects ALL, and
    otherwise in any case only for the ending after its last `*` within the last segment."""
    out, i = [], 0
    last = pattern.rfind("*")
    if 0 <= last < len(pattern) - 1 and "/" not in pattern[last + 1:]:
        tail = pattern[last + 1:]
        pattern = pattern[:last + 1]
    else:
        tail = ""
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    if tail:
        out.append(f"(?i:{re.escape(tail)})")
    return re.compile("".join(out), re.IGNORECASE if sections == ALL else 0)


COMPILED = tuple((pattern, pattern_re(pattern, sections), sections) for pattern, sections in MAP)


def suite_sections(text):
    """The section names of tools/run_all_checks.sh, in its order."""
    return SECTION.findall(text)


def suite_depends(text):
    """Each section's needs from the suite's `# depends:` lines; ValueError for a line in any
    other shape or a section named twice."""
    depends = {}
    for line in re.findall(r"^# depends:.*$", text, re.M):
        match = DEPENDS_LINE.fullmatch(line)
        if not match or match[1] in depends:
            raise ValueError(f"{line!r} is not `# depends: NAME: NEED...` for a new NAME")
        depends[match[1]] = tuple(match[2].split(" "))
    return depends


def sections_for(path):
    """(pattern, sections) for one changed path; (None, ALL) when no pattern matches it."""
    for pattern, compiled, sections in COMPILED:
        if compiled.fullmatch(path):
            return pattern, sections if sections == ALL else sections + ANY_PATH
    return None, ALL


def select(paths, names, depends):
    """The sections to run for these changed paths, in suite order, and one note per path;
    depends is suite_depends of the suite."""
    paths = [p for p in paths if p]
    if not paths:
        return list(names), ["no changed paths: every section"]
    chosen, notes = set(), []
    for path in paths:
        pattern, sections = sections_for(path)
        if sections == ALL:
            why = f"matches {pattern}" if pattern else "not scoped content"
            return list(names), notes + [f"{path}: {why}: every section"]
        chosen.update(sections)
        notes.append(f"{path}: {', '.join(n for n in names if n in sections)}")
    for section, needs in depends.items():
        if section in chosen:
            chosen.update(needs)
    stale = sorted(chosen - set(names))
    if stale:
        return list(names), notes + [f"the map names {stale!r}, which the suite does not have: "
                                     f"every section"]
    return [n for n in names if n in chosen], notes


def main():
    try:
        text = SUITE.read_text(encoding="utf-8")
        names, depends = suite_sections(text), suite_depends(text)
    except (OSError, ValueError) as exc:
        print(f"  FAIL  cannot read {SUITE.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return 2
    if not names:
        print(f"  FAIL  {SUITE.relative_to(ROOT)} has no `# section: NAME` lines", file=sys.stderr)
        return 2
    chosen, notes = select(sys.stdin.read().split("\n"), names, depends)
    for note in notes:
        print(f"select_gates: {note}", file=sys.stderr)
    print("\n".join(chosen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
