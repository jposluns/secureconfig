#!/usr/bin/env bash
# Whole-corpus gate suite for secureconfig.
#
# Every gate here is deterministic and offline: no gate reaches the network, so no
# vendor outage or rate limit can change a gate's answer. The CI job that runs this
# suite is not offline: .github/workflows/checks.yml fetches its pinned actions,
# Python, shellcheck, and playwright with its Chromium before the suite starts, and
# an outage there can fail the job. External link rot is caught separately by the weekly lychee sweep, which
# stays advisory so that a site being down cannot block a merge.
#
# Usage: tools/run_all_checks.sh [--sections NAME[,NAME...]]   (runs from any directory)
#
# With no argument every section runs. That is the whole-corpus run, which CI makes weekly and on
# demand, and only it ends with "All gates passed.". With --sections, the named sections and their prerequisites run,
# in this file's order; on a pull request tools/select_gates.py names them from the changed paths,
# and names every section when the pull request changes any path other than the root project
# records CHANGELOG.md, TODO.md, DONE.md, DECISIONS.md and PENDING-DECISIONS.md and the files
# under site/ or site-src/ whose names end, in any case, in .html, .css, .json, .svg, .png, .jpg,
# .jpeg, .webp, .ico, .woff2, .txt or .xml and are not _headers, _redirects or a requirements
# file. A section that relies on others has a `# depends: NAME: NEED...` line below, which
# tools/select_gates.py reads too: when the list names it, --sections adds each NEED the list
# lacks, in this file's order, and says so, so a selection that holds generated-committed always
# runs llms-full and plugin, whose rebuilds it relies on. A section is everything from its
# `# section: NAME` line to the next such line or to `# end of sections`. What comes before the
# first section (the helpers, run_gate and the parser preflight) and the summary after the last
# one run either way. A name holding anything but letters, digits and hyphens (a newline
# included), or that is not a section here, is refused with status 2 before any gate runs, and so
# is a `# depends:` line not shaped `NAME: NEED...` or, for a named section, needing a name that
# is not a section here. The named sections are cut out of this file's text, not wrapped in a
# condition, so each section's heading and body are the same in both runs and the tests that cut
# a block out of this file still find it.
#
# generated-committed skips its own rebuild on a clean tree because the llms-full and plugin
# sections before it already rebuilt HEAD.
# depends: generated-committed: llms-full plugin
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

selected_sections=""
if [ "$#" -gt 0 ]; then
  if [ "$#" -ne 2 ] || [ "$1" != --sections ]; then
    printf 'usage: tools/run_all_checks.sh [--sections NAME[,NAME...]]\n' >&2
    exit 2
  fi
  known=$(sed -n 's/^# section: \([a-z0-9-]*\)$/\1/p' tools/run_all_checks.sh)
  rest="$2,"
  while [ -n "$rest" ]; do
    name=${rest%%,*}
    rest=${rest#*,}
    # grep reads a newline in its pattern as a second pattern, so only these characters pass.
    case $name in
      *[!A-Za-z0-9-]*)
        printf "  FAIL  --sections names '%s', which holds a character other than a letter, a digit or a hyphen; no gate ran\n" "$name"
        exit 2 ;;
    esac
    if [ -z "$name" ] || ! grep -qxF -- "$name" <<< "$known"; then
      printf "  FAIL  --sections names '%s', which is not a section of tools/run_all_checks.sh; no gate ran\n" "$name"
      exit 2
    fi
  done
  # What a named section relies on, from the `# depends:` lines above, added in this file's order.
  needed=" "
  while read -r line; do
    case $line in
      [a-z0-9]*': '[a-z0-9]*) ;;
      *)
        printf "  FAIL  the '# depends: %s' line of tools/run_all_checks.sh is not 'NAME: NEED...'; no gate ran\n" "$line"
        exit 2 ;;
    esac
    case ",$2," in
      *",${line%%: *},"*) needed+="${line#*: } " ;;
    esac
  done < <(sed -n 's/^# depends: //p' tools/run_all_checks.sh)
  while read -r need; do
    if [ -n "$need" ] && ! grep -qxF -- "$need" <<< "$known"; then
      printf "  FAIL  a '# depends:' line of tools/run_all_checks.sh needs '%s', which is not a section of it; no gate ran\n" "$need"
      exit 2
    fi
  done < <(tr ' ' '\n' <<< "$needed")
  added=""
  while read -r name; do
    case $needed in *" $name "*) ;; *) continue ;; esac
    case ",$2," in *",$name,"*) continue ;; esac
    added+=",$name"
  done <<< "$known"
  list=$2$added
  # This file with only the selected sections (the named ones and their prerequisites), and
  # selected_sections set for the summary.
  if ! script=$(awk -v want=",$list," -v list="$list" '
      /^# section: / {
        if (!started) { print "selected_sections=" list; started = 1 }
        inside = 1; keep = index(want, "," substr($0, 12) ",") > 0
      }
      /^# end of sections$/ { inside = 0 }
      !inside || keep
    ' tools/run_all_checks.sh) || ! grep -qx '# end of sections' <<< "$script"; then
    printf '  FAIL  could not cut the named sections out of tools/run_all_checks.sh; no gate ran\n'
    exit 2
  fi
  if [ -n "$added" ]; then
    printf 'Sections added: %s, which a named section depends on\n' "${added#,}"
  fi
  printf 'Sections selected: %s\n' "$list"
  # A fresh bash sources the cut copy with this file as its $0 and no arguments, so the cd above
  # lands in the same tree and the copy runs straight through.
  bash -c '. /dev/fd/3' "$PWD/tools/run_all_checks.sh" 3<<< "$script"
  exit $?
fi

fail=0
ok()  { printf '  ok    %s\n' "$1"; }
bad() { printf '  FAIL  %s\n' "$1"; fail=1; }

# Root-level Markdown that is not a single service's guide, so the guide-shape and guide-index
# requirements do not apply to it. Most of these document the repository or govern the assistants
# working in it, and are deliberately absent from llms-full.txt and llms.txt. The exception is
# controls-reference.md: the cross-service reference an assistant needs when a service has no guide.
# It has no per-service Verify or dated Sources, so it is not a guide for shape and index purposes,
# but it IS carried in scripts/build-llms-full.sh and site/llms.txt so an assistant actually
# receives it. README.sources.md holds the citations for the README verification checklist, kept out
# of the README so the front page stays readable, and is therefore NOT carried in llms-full.txt.
not_a_guide() {
  case "$1" in
    CONTRIBUTING.md|SECURITY.md|QUALITY.md|CLAUDE.md|AGENTS.md|CHANGELOG.md|README.sources.md|TODO.md|DONE.md|DECISIONS.md|PENDING-DECISIONS.md|controls-reference.md) return 0 ;;
    *) return 1 ;;
  esac
}

# The runner of the site gates further down. Each gate runs after its self-test, so a gate that
# stopped catching its cases cannot report a pass. A gate that exits 0 while printing a FAIL line
# or without printing an ok line, or that crashes, is a failure. It is defined here, before the
# first section, so a --sections run that skips the sections around it still has it.
# tools/test_gate_runners.py reads this function out of this file and runs it on stand-in gates.
run_gate() {
  local label=$1 out
  shift
  if out=$("$@" 2>&1); then
    printf '%s\n' "$out"
    if grep -q '^  FAIL  ' <<< "$out"; then
      bad "$label printed findings but exited 0"
    elif ! grep -q '^  ok    ' <<< "$out"; then
      bad "$label exited 0 without an ok line"
    fi
  elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$out"; then
    bad "$label crashed"
    printf '%s\n' "$out" | sed 's/^/          /'
  elif grep -q '^  FAIL  ' <<< "$out"; then
    printf '%s\n' "$out"
    fail=1
  else
    bad "$label exited non-zero without reporting a result"
    printf '%s\n' "$out" | sed 's/^/          /'
  fi
}

echo "== gate parser preflight: this python3 has the pinned markdown-it-py =="
# Several gates below need the markdown-it-py that tools/requirements-gates.txt pins. On a host
# whose python3 has another release, each of them printed its own FAIL line and traceback, which
# read like code findings. tools/check_parser_pin.py runs first, in the python3 -I -B form the
# parser gates use, and prints one line. Anything but its ok line stops the suite here with
# status 2, before any other gate runs, so a host problem never reads as a red tree. CI installs
# the pin before the suite starts. The Python-version advisory further down is unchanged.
if preflight=$(python3 -I -B tools/check_parser_pin.py 2>&1); then
  printf '%s\n' "$preflight"
  if grep -q '^  FAIL  ' <<< "$preflight" ||
     ! grep -q '^  ok    gate parser preflight: ' <<< "$preflight"; then
    printf '  FAIL  gate parser preflight exited 0 without its ok line; the suite ran no other gate\n'
    exit 2
  fi
else
  preflight_rc=$?
  printf '%s\n' "$preflight"
  if [ "$preflight_rc" -ne 2 ]; then
    printf '  FAIL  gate parser preflight did not complete (exit %s); the suite ran no other gate\n' "$preflight_rc"
  fi
  exit 2
fi

# section: parser-pin-tests
echo "== the gate parser preflight still refuses what it should =="
if preflight_tests=$(python3 -I -B tools/test_parser_pin.py 2>&1); then
  printf '%s\n' "$preflight_tests"
  if grep -q '^  FAIL  ' <<< "$preflight_tests" ||
     ! grep -qE '^  ok    [0-9]+ recorded tests for the gate parser preflight$' <<< "$preflight_tests"; then
    bad "test_parser_pin.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$preflight_tests"
  bad "test_parser_pin.py failed"
fi

# section: credential-scanner
echo "== credential scanner regressions and shell lint =="
python3 tools/test_scan_credential.py || bad "credential scanner self-test"
if command -v shellcheck >/dev/null 2>&1; then
  shellcheck --norc tools/scan_credential.sh || bad "credential scanner shellcheck"
  shellcheck --norc tools/run_all_checks.sh || bad "gate suite shellcheck"
else
  printf '  SKIP  shellcheck is not installed; shell lint not run\n'
fi

# section: version-basis
echo "== version basis =="
python3 tools/test_version_basis.py || bad "version-basis self-test"
python3 tools/version_basis.py --check || bad "version-basis metadata or summary"

# section: claim-lengths
echo "== claim text stays within the 400-character baseline =="
# Maintainer ruling 2026-10-23 (DECISIONS.md): a claim's text over 400 characters
# fails unless tools/claim_length_baseline.txt lists it at its exact current
# length, and stale entries fail too. A baseline addition or raise is a reviewed
# edit the tree-only gate cannot refuse; the self-test records that limit. The
# self-test runs first, so what runs against the corpus is the shipped gate.
for claim_check in test_claim_lengths.py check_claim_lengths.py; do
  if claim_lengths=$(python3 -I -B "tools/$claim_check" 2>&1); then
    printf '%s\n' "$claim_lengths"
    if grep -q '^  FAIL  ' <<< "$claim_lengths" || ! grep -q '^  ok    ' <<< "$claim_lengths"; then
      bad "$claim_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$claim_lengths"
    bad "$claim_check failed"
  fi
done

# section: sentence-split
echo "== the shared sentence splitter still splits as recorded =="
# Row 3.47: one implementation measures the 400-character rules for guide prose
# (DONE 1.385) and for generated claim-summary sentences (row 1.383). Only its
# self-test runs here; under the maintainer ruling of 2026-10-26 (DECISIONS.md)
# there is no prose-length gate, and this adds none.
if sentence_tests=$(python3 -I -B tools/test_sentence_split.py 2>&1); then
  printf '%s\n' "$sentence_tests"
  if grep -q '^  FAIL  ' <<< "$sentence_tests" ||
     ! grep -qE '^  ok    [0-9]+ recorded tests for the sentence splitter$' <<< "$sentence_tests"; then
    bad "test_sentence_split.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$sentence_tests"
  bad "test_sentence_split.py failed"
fi

# section: llms-full
echo "== llms-full.txt is current =="
orig=$(mktemp)
cp site/llms-full.txt "$orig"
trap 'cp "$orig" site/llms-full.txt 2>/dev/null; rm -f "$orig"' EXIT
if bash scripts/build-llms-full.sh >/dev/null 2>&1; then
  if diff -q "$orig" site/llms-full.txt >/dev/null 2>&1; then
    ok "matches a fresh build"
  else
    bad "site/llms-full.txt is stale; run scripts/build-llms-full.sh and commit the result"
  fi
else
  bad "scripts/build-llms-full.sh exited non-zero"
fi
# An unchecked restore could leave a half-written bundle for every later gate to read.
cp "$orig" site/llms-full.txt || { bad "could not restore site/llms-full.txt from $orig"; exit 1; }

# section: llms-full-links
echo "== llms-full.txt links are absolute and name repository paths =="
# site/llms-full.txt is served from https://secureconfig.ai/, where a relative link such as
# (mfa.md) names a page that does not exist, so scripts/build-llms-full.sh rewrites each one to
# https://github.com/jposluns/secureconfig/blob/main/<path> (tree/main/ for a directory). The
# freshness gate above proves the committed file is the build's output. This one runs the
# build's link check, through scripts/build-llms-full.sh --check-links, on the committed file,
# so the build and this gate apply one rule. The check parses the file with the pinned
# markdown-it-py and each piece of raw HTML in it with Python's html.parser. It fails closed on
# any link, image, link reference definition or listed HTML URL attribute whose target is not
# an in-page anchor or a URL with a scheme, and on any link into this repository's main branch
# that names no file or directory in this checkout. The build script's comment above the check
# lists the attributes and the CSS and srcset forms it refuses. Code spans, fenced code and
# indented code are code to the parser and are not checked. Its self-test of mutations and
# clean cases runs first, so what checks the bundle is the shipped rule, and it reads only the
# working tree, so it stays offline. Heading anchors are not checked here; the local-links gate
# below checks them in the guides the bundle is built from.
if llms_links=$(bash scripts/build-llms-full.sh --check-links 2>&1); then
  ok "site/llms-full.txt has no link target the gate cannot certify, and all $llms_links of its links into this repository's main branch name a path in this checkout"
else
  bad "site/llms-full.txt has a link target the gate cannot certify, or a link into this repository that names no path here, or the gate's self-test failed"
  printf '%s\n' "$llms_links" | sed 's/^/          /'
fi

# section: plugin
echo "== the plugin bundle is current =="
# plugin/ is generated from the guides by scripts/build-plugin.sh, the same way
# site/llms-full.txt is, and for the same reason: a bundle that has drifted from the guides ships
# a reader stale configuration while the repository looks correct. The build is byte-deterministic
# (a copy per file), so rebuilding and comparing is the whole check.
plugin_tmp=$(mktemp -d)
cp -a plugin/. "$plugin_tmp/"
if bash scripts/build-plugin.sh >/dev/null 2>&1; then
  if diff -rq "$plugin_tmp" plugin >/dev/null 2>&1; then
    ok "plugin/ matches a fresh build"
  else
    bad "plugin/ is stale; run scripts/build-plugin.sh and commit the result"
  fi
else
  bad "scripts/build-plugin.sh exited non-zero"
fi
rm -rf plugin
cp -a "$plugin_tmp" plugin || { bad "could not restore plugin/ from $plugin_tmp"; exit 1; }
rm -rf "$plugin_tmp"

# section: generated-committed
echo "== the committed generated files match a fresh build of the commit =="
# The two gates above rebuild in the working tree, so they pass when the working tree is right and
# the commit is not: a bundle rebuilt but only partly staged (F-PLUGIN-MANIFEST-PARTIAL-STAGE), or
# a VERSION bump committed without its plugin/plugin.json (F-VERSION-BUMP-NO-REGEN). This gate
# exports HEAD with git archive on every run and checks the committed plugin.json version against
# the committed VERSION. Unless git status shows the working tree is HEAD with no change, in which
# case the gates above already rebuilt HEAD, it also runs the same two builds in the export and
# compares; that skip relies on the llms-full and plugin sections, which --sections adds whenever
# it names this one (the `# depends:` line at the top). The self-test runs first, so what runs is
# the shipped gate.
for generated_check in test_generated_committed.py check_generated_committed.py; do
  if generated_committed=$(python3 -I -B "tools/$generated_check" 2>&1); then
    printf '%s\n' "$generated_committed"
    if grep -q '^  FAIL  ' <<< "$generated_committed" || ! grep -q '^  ok    ' <<< "$generated_committed"; then
      bad "$generated_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$generated_committed"
    bad "$generated_check failed"
  fi
done

# section: gensrc
echo "== the generated-file record matches how they are generated =="
# CLAUDE.md names .aiqt/gensrc.json as the record of which sources produce site/llms-full.txt.
# Adding a guide touches five wiring surfaces and four of them were gated; this was the fifth,
# so a guide added to the build script and forgotten in the manifest left the record wrong and
# nothing said so. The check above proves the bundle is current. This one proves the manifest
# still agrees with what the build script reports as its inputs.
if gensrc=$(python3 tools/check_gensrc.py 2>&1); then
  printf '%s\n' "$gensrc"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$gensrc"; then
    bad "check_gensrc.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$gensrc"; then
  bad "check_gensrc.py crashed; the generated-file record is unverified"
  printf '%s\n' "$gensrc" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$gensrc"; then
  printf '%s\n' "$gensrc"
  fail=1
else
  bad "check_gensrc.py exited non-zero without reporting a gate result"
  printf '%s\n' "$gensrc" | sed 's/^/          /'
fi

# section: gensrc-tests
echo "== the generated-file record gate still catches what review found =="
# The first version of the gate above was naive in both directions, and the two are not
# equally bad: missing a source is a silent pass, while inventing one is a fabricated
# finding against a correct repository, which teaches a maintainer to distrust the suite.
# Each case here is a fixture a reviewer ran against it. They build throwaway repositories
# and invoke the real gate, so what is under test is the shipped entry point.
if gensrc_tests=$(python3 tools/test_gensrc_gate.py 2>&1); then
  printf '%s\n' "$gensrc_tests"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$gensrc_tests"; then
    bad "test_gensrc_gate.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$gensrc_tests"; then
  bad "test_gensrc_gate.py crashed; the record gate is unverified"
  printf '%s\n' "$gensrc_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$gensrc_tests"; then
  printf '%s\n' "$gensrc_tests"
  fail=1
else
  bad "test_gensrc_gate.py exited non-zero without reporting a result"
  printf '%s\n' "$gensrc_tests" | sed 's/^/          /'
fi

# section: bare-urls
echo "== bare double-underscore URLs in tracked root Markdown =="
if bare_urls=$(python3 tools/check_bare_urls.py 2>&1); then
  printf '%s\n' "$bare_urls"
  if grep -q '^  FAIL  ' <<< "$bare_urls"; then
    bad "check_bare_urls.py printed findings but exited 0"
  elif ! grep -qE '^  ok    tracked root Markdown has no bare double-underscore URLs \((pinned parser|lexical fallback)\)$' <<< "$bare_urls"; then
    bad "check_bare_urls.py exited 0 without its expected ok line"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$bare_urls"; then
  bad "check_bare_urls.py crashed; bare URLs are unverified"
  printf '%s\n' "$bare_urls" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$bare_urls"; then
  printf '%s\n' "$bare_urls"
  fail=1
else
  bad "check_bare_urls.py exited non-zero without reporting a gate result"
  printf '%s\n' "$bare_urls" | sed 's/^/          /'
fi

# section: bare-urls-tests
echo "== bare URL gate fixtures =="
if bare_urls_tests=$(python3 tools/test_bare_urls_gate.py 2>&1); then
  printf '%s\n' "$bare_urls_tests"
  if grep -q '^  FAIL  ' <<< "$bare_urls_tests"; then
    bad "test_bare_urls_gate.py printed findings but exited 0"
  elif ! grep -qE '^  ok    bare URL gate: [0-9]+ failures, [0-9]+ exemptions, and bare, href and code-span mutation proofs$|^  SKIP  bare URL parser fixtures: ' <<< "$bare_urls_tests"; then
    bad "test_bare_urls_gate.py exited 0 without its expected ok line"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$bare_urls_tests"; then
  bad "test_bare_urls_gate.py crashed; bare URL fixtures are unverified"
  printf '%s\n' "$bare_urls_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$bare_urls_tests"; then
  printf '%s\n' "$bare_urls_tests"
  fail=1
else
  bad "test_bare_urls_gate.py exited non-zero without reporting a result"
  printf '%s\n' "$bare_urls_tests" | sed 's/^/          /'
fi

# section: guide-wiring
echo "== every guide is wired into the site =="
wired=1
# Strip HTML comments across the whole file (re.S, not a line-at-a-time sed) so a README row
# commented out across multiple lines does not count as wired.
readme_stripped=$(python3 - <<'PY'
import re
text = open("README.md", encoding="utf-8").read()
print(re.sub(r"<!--.*?-->", "", text, flags=re.S))
PY
)
for f in *.md; do
  not_a_guide "$f" && continue
  grep -qF " $f" scripts/build-llms-full.sh || { bad "$f is not listed in scripts/build-llms-full.sh"; wired=0; }
  grep -qF "main/$f" site/llms.txt || { bad "$f is not linked from site/llms.txt"; wired=0; }
  [ "$f" = README.md ] || grep -qE "^\| \[$f\]\($f\) \|" <<< "$readme_stripped" || { bad "$f is not indexed in README.md"; wired=0; }
  # The generated Guides page (scripts/build-site.py) links each guide as a GitHub blob URL; since
  # promotion it is the site's guide index, replacing the old site/index.html menu check.
  grep -qE "<a href=\"https://github.com/jposluns/secureconfig/blob/main/$f\"" site/guides/index.html \
    || { bad "$f is not linked from site/guides/index.html"; wired=0; }
done
[ "$wired" = 1 ] && ok "every guide is listed in the build script, linked from llms.txt, indexed in README.md, and on the generated Guides page"

# section: guide-categories
echo "== README guide-index categories match the generated Guides page and site/llms.txt =="
# The README's "## Guide index" section and site/llms.txt are two hand-maintained copies of the
# same category list, and the generated Guides page is built from the README's; nothing else in
# this suite catches them drifting apart. They had drifted: llms.txt carried ten sections of its
# own against the README's twelve, and three independent reviews raised it before anything
# compared them.
# llms.txt is checked on its guide MEMBERSHIP too, not just its headings, because a guide
# filed under a different category in one file than the other is the same defect one level
# down. Its "Start here" and "Optional" sections are the llms.txt format's own and are exempt.
# README.md and site/llms.txt are both hand-written Markdown, not generated, so their sections
# and headings come from the pinned CommonMark parser that the count gate below uses (gate_parser,
# locked in tools/requirements-gates.txt): a "##" section ends at the next level-one or level-two
# heading in any form (ATX with spaces or tabs, indented up to three spaces, or setext), a "###"
# category ends at the next heading of level one, two or three, and a heading-shaped line inside
# a code block is not a heading. The gate fails if the pinned parser is unavailable.
if cat_diff=$(python3 - <<'PY'
import re, sys

sys.path.insert(0, "tools")
from check_verify_marking import ParserUnavailable, gate_parser

# A lock that cannot be read or parsed, or a markdown_it package without the installed version
# metadata of markdown-it-py or mdurl, makes gate_parser() raise something other than
# ParserUnavailable; the gate fails on each in one line naming the cause, never a traceback.
try:
    parser = gate_parser(required=True)
except ParserUnavailable as exc:
    print(f"README.md's and site/llms.txt's sections need the pinned Markdown parser: {exc}")
    sys.exit(1)
except Exception as exc:  # noqa: BLE001  any failure to load the parser fails the gate
    cause = " ".join(f"{type(exc).__name__}: {exc}".split())
    print("README.md's and site/llms.txt's sections need the pinned Markdown parser, which "
          "cannot be loaded from tools/requirements-gates.txt and the installed markdown-it-py "
          f"and mdurl: {cause}")
    sys.exit(1)


def headings(text):
    # The text's lines, and its headings as (tag, nesting level, line map, heading text).
    tokens = parser.parse(text)
    lines = re.sub(r"\r\n?", "\n", text).split("\n")
    return lines, [(t.tag, t.level, t.map, tokens[i + 1].content.strip())
                   for i, t in enumerate(tokens) if t.type == "heading_open"]


def sections(heads, tag, lo, hi, top=False):
    # (heading text, first line under it, end line) for each heading of this tag, ATX or setext,
    # that starts at or after line lo and before line hi; with top, only headings outside any
    # container count. A section ends at the next heading of the same or a higher level in any
    # form, or at hi.
    rank = int(tag[1])
    found = []
    for i, (t, level, (first, start), name) in enumerate(heads):
        if t != tag or not lo <= first < hi or (top and level != 0):
            continue
        stops = [m[0] for u, _, m, _ in heads[i + 1:] if int(u[1]) <= rank and m[0] < hi]
        found.append((name, start, stops[0] if stops else hi))
    return found


def rows(lines, start, end, pattern):
    return re.findall(pattern, "\n".join(lines[start:end]), re.M)


readme = open("README.md", encoding="utf-8").read()
readme = re.sub(r"<!--.*?-->", "", readme, flags=re.S)
readme_lines, readme_heads = headings(readme)
index = [s for s in sections(readme_heads, "h2", 0, len(readme_lines), top=True)
         if s[0] == "Guide index"]
if not index:
    print("README.md has no '## Guide index' section")
    sys.exit(1)
readme_sections = sections(readme_heads, "h3", index[0][1], index[0][2])
readme_cats = [name for name, _, _ in readme_sections]

llms = open("site/llms.txt", encoding="utf-8").read()
llms = re.sub(r"<!--.*?-->", "", llms, flags=re.S)
exempt = {"Start here", "Optional"}
llms_lines, llms_heads = headings(llms)
llms_cats, llms_members = [], {}
for name, start, end in sections(llms_heads, "h2", 0, len(llms_lines), top=True):
    if name in exempt:
        continue
    llms_cats.append(name)
    llms_members[name] = rows(llms_lines, start, end, r"^- \[([a-z0-9.-]+)\]\(")

readme_members = {}
for name, start, end in readme_sections:
    readme_members[name] = [g[:-3] for g in
                            rows(readme_lines, start, end, r"^\|\s*\[([^\]]+\.md)\]\(")]

# The generated Guides page (scripts/build-site.py): its category headings are <h2 id="cat-N">,
# and each category's guides are the GitHub blob links up to the next heading. Since promotion it
# is the site's guide index, so it replaced the old site/index.html menu here.
import html as html_lib
guides_page = open("site/guides/index.html", encoding="utf-8").read()
guides_parts = re.split(r'<h2 id="cat-\d+">([^<]*)</h2>', guides_page)
guides_cats = [html_lib.unescape(c) for c in guides_parts[1::2]]
guides_members = {}
for name, body in zip(guides_cats, guides_parts[2::2]):
    body = body.split("<h2", 1)[0]
    guides_members[name] = re.findall(
        r'<a href="https://github\.com/jposluns/secureconfig/blob/main/([a-z0-9.-]+)\.md"', body)

problems = []
if readme_cats != llms_cats:
    problems.append(("site/llms.txt", llms_cats))
if readme_cats != guides_cats:
    problems.append(("site/guides/index.html", guides_cats))

if not problems:
    for name in readme_cats:
        for label, members in (("site/llms.txt", llms_members),
                               ("site/guides/index.html", guides_members)):
            if readme_members.get(name) != members.get(name):
                print(f"category {name!r} lists different guides in README.md and {label}")
                print("  README:    " + repr(readme_members.get(name)))
                print(f"  {label}:  " + repr(members.get(name)))
                sys.exit(1)
    sys.exit(0)

print("README guide-index categories: " + repr(readme_cats))
for label, other in problems:
    print(f"{label} categories: " + repr(other))
    for i, (a, b) in enumerate(zip(readme_cats, other)):
        if a != b:
            print(f"  first difference at position {i}: README={a!r} {label}={b!r}")
            break
    else:
        print(f"  one list is a prefix of the other; lengths differ "
              f"({len(readme_cats)} vs {len(other)})")
sys.exit(1)
PY
); then
  ok "README guide-index, site/llms.txt and the generated Guides page carry the same categories"
else
  bad "README guide-index categories do not match site/llms.txt or the generated Guides page"
  printf '%s\n' "$cat_diff" | sed 's/^/          /'
fi

# section: guide-counts
echo "== README's stated guide and category counts match the corpus =="
# README.md's "## What this is" section states the corpus size in prose ("that is N guides across
# the M categories indexed below"), and the gates above check category lists and membership but not
# those numerals. The count sentence is matched in any letter case, with any whitespace between
# words, after HTML comment blocks are removed. README.md is read as SKILL.md is, through
# blank_comment_blocks() in tools/_verify_sections.py and the pinned parser below: it may hold
# HTML only as HTML blocks outside any list item or block quote, each one whole HTML comment,
# and each is removed by blanking exactly the lines the parser maps it to once they are confirmed
# to equal its text. Any other raw HTML, an inline comment or a "<!--" in a tag's attribute
# included, fails the gate in one line naming the first line of the block, or the table row,
# that holds it, since raw HTML is not read and so could hide or show text unseen. A "<!--" the
# parser does not read as HTML (in code, a link destination or title, a reference definition, or
# after a backslash) is kept as text, so it hides nothing; a code-blind strip once removed a
# count sentence lying between such a "<!--" and a later "-->". The self-test,
# tools/test_guide_counts.py, runs this section on fixture READMEs first.
# The "## What this is" section must hold exactly one
# match, and any match elsewhere in README.md fails, so a stale copy can neither mask a wrong count
# nor drift unchecked. The guide count is checked against the root guides that
# `python3 tools/_verify_sections.py` lists (counted_guides(): every root regular file *.md
# whose name does not start with ".", outside not_a_guide, less README.md itself).
# scripts/build-plugin.sh and tools/check_generated_committed.py count SKILL.md's guides with
# that same function, so a dot-named file or a directory named *.md cannot make the counts
# differ. The README guide
# index must list exactly that set, once each, so the two definitions of the guide count cannot
# drift apart. The category count is checked against the "###" headings of "## Guide index".
# Both sections and the "###" headings come from the pinned CommonMark parser that the
# Verify-marking gate uses (gate_parser, locked in tools/requirements-gates.txt): a section ends
# at the next level-one or level-two heading in any form (ATX with spaces or tabs, indented up to
# three spaces, or setext), and a heading-shaped line inside a code block is not a heading. The
# gate fails if the pinned parser is unavailable. A reworded, missing or misplaced count sentence
# fails closed rather than passing unchecked.
# The self-test runs this section's text from guide_files=() on, so it never runs itself. The
# parser preflight above has already required the pin, so a skip line here is a failure.
if counts_st=$(python3 -I -B tools/test_guide_counts.py 2>&1); then
  printf '%s\n' "$counts_st"
  if grep -qE '^  (FAIL|skip)  ' <<< "$counts_st" ||
     ! grep -qE '^  ok    [0-9]+ recorded cases for the guide-counts gate$' <<< "$counts_st"; then
    bad "test_guide_counts.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$counts_st"
  bad "test_guide_counts.py failed"
fi
guide_files=()
guide_list=$(python3 tools/_verify_sections.py) || bad "tools/_verify_sections.py could not list the root guides"
[ -z "$guide_list" ] || mapfile -t guide_files <<< "$guide_list"
if count_diff=$(python3 - "${guide_files[@]}" <<'PY'
import re, sys

sys.path.insert(0, "tools")
from check_verify_marking import ParserUnavailable, gate_parser
from _verify_sections import RawHtml, blank_comment_blocks

guides = sys.argv[1:]
raw = open("README.md", encoding="utf-8").read()
form = "that is N guides across the M categories indexed below"
count_re = re.compile(
    r"\bthat\s+is\s+(\d+)\s+guides\s+across\s+the\s+(\d+)\s+categories\s+indexed\s+below\b",
    re.I)
# As in the category gate, a parser that cannot be loaded at all fails the gate in one line
# naming the cause, never a traceback.
try:
    parser = gate_parser(required=True)
except ParserUnavailable as exc:
    print(f"README.md's sections need the pinned Markdown parser: {exc}")
    sys.exit(1)
except Exception as exc:  # noqa: BLE001  any failure to load the parser fails the gate
    cause = " ".join(f"{type(exc).__name__}: {exc}".split())
    print("README.md's sections need the pinned Markdown parser, which cannot be loaded from "
          "tools/requirements-gates.txt and the installed markdown-it-py and mdurl: "
          f"{cause}")
    sys.exit(1)
# The whole HTML comment blocks blanked, as SKILL.md's are; any other raw HTML fails in one line.
try:
    lines = blank_comment_blocks(raw, parser, "README.md")
except RawHtml as exc:
    print(f"README.md: {exc}")
    sys.exit(1)
readme = "\n".join(lines)
tokens = parser.parse(readme)
heads = [(t.tag, t.level, t.map, tokens[i + 1].content.strip())
         for i, t in enumerate(tokens) if t.type == "heading_open"]


def section_of(heading):
    # Line range under a top-level "## heading", ATX or setext, up to the next heading of level 1
    # or 2 in any CommonMark form; a "## " line inside a code block is not a heading.
    for i, (tag, level, (_, start), text) in enumerate(heads):
        if tag == "h2" and level == 0 and text == heading:
            ends = [m[0] for t, _, m, _ in heads[i + 1:] if t in ("h1", "h2")]
            return start, ends[0] if ends else len(lines)
    return None


span = section_of("What this is")
if span is None:
    print("README.md has no '## What this is' section")
    sys.exit(1)
intro = "\n".join(lines[span[0]:span[1]])
stated = count_re.findall(intro)
if len(stated) != 1:
    print(f"README.md's '## What this is' section must state its counts exactly once as "
          f"'{form}' (found {len(stated)}); restore that wording or update this gate")
    sys.exit(1)
elsewhere = len(count_re.findall(readme)) - 1
if elsewhere:
    print(f"README.md states its counts as '{form}' {elsewhere} more time(s) outside "
          f"'## What this is'; remove the stale copy or update this gate")
    sys.exit(1)
stated_guides, stated_cats = (int(n) for n in stated[0])

span = section_of("Guide index")
if span is None:
    print("README.md has no '## Guide index' section")
    sys.exit(1)
section = "\n".join(lines[span[0]:span[1]])
cats = [h for h in heads if h[0] == "h3" and span[0] <= h[2][0] < span[1]]
rows = re.findall(r"^\|\s*\[([^\]]+\.md)\]\(", section, re.M)

problems = []
if len(rows) != len(set(rows)) or set(rows) != set(guides):
    extra = sorted(set(rows) - set(guides))
    missing = sorted(set(guides) - set(rows))
    twice = sorted({r for r in rows if rows.count(r) > 1})
    problems.append(f"README guide index lists {len(rows)} rows but the root has "
                    f"{len(guides)} guides outside not_a_guide; not root guides: {extra!r}; "
                    f"not indexed: {missing!r}; listed more than once: {twice!r}")
if stated_guides != len(guides):
    problems.append(f"README.md states {stated_guides} guides but the root has "
                    f"{len(guides)} guides (counted_guides() in tools/_verify_sections.py)")
if stated_cats != len(cats):
    problems.append(f"README.md states {stated_cats} categories but its '## Guide index' "
                    f"section has {len(cats)} '###' category headings")
if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"{len(guides)} guides across {len(cats)} categories")
PY
); then
  ok "README.md's stated counts match the corpus: $count_diff"
else
  bad "README.md's stated guide or category count does not match the corpus"
  printf '%s\n' "$count_diff" | sed 's/^/          /'
fi

# section: guide-shape
echo "== every guide has a Verify section and dated Sources =="
# The structural half of the CONTRIBUTING rule that a guide must hand the reader runnable checks and
# dated, cited sources. What a reader copies from here faces the internet, so a guide that ships with
# no Verify step at all is a defect, not an omission. The gate deliberately does NOT claim to prove
# that a Verify step DISCRIMINATES (fails while the service is still exposed) or that a config line
# appears on the page it cites; both stay authoring obligations enforced by review.
if guide_shape=$(python3 tools/check_guide_shape.py 2>&1); then
  printf '%s\n' "$guide_shape"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  # Aligned with the two gates below; not new behaviour for this gate.
  if grep -q '^  FAIL  ' <<< "$guide_shape"; then
    bad "check_guide_shape.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$guide_shape"; then
  # A crash, INCLUDING one that printed some FAIL lines before dying. The gate did not
  # finish, so its findings are incomplete and must never read as a complete verdict.
  bad "check_guide_shape.py crashed; its findings are incomplete"
  printf '%s\n' "$guide_shape" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$guide_shape"; then
  # The gate reported its own findings, already in this suite's FAIL format.
  printf '%s\n' "$guide_shape"
  fail=1
else
  # Exited non-zero saying nothing useful: a kill, or an empty failure.
  bad "check_guide_shape.py exited non-zero without reporting a gate result"
  printf '%s\n' "$guide_shape" | sed 's/^/          /'
fi

# section: verify-tls
echo "== no code block disables TLS verification =="
# Three Verify blocks passed curl -k before anything checked, while three other files in this corpus
# told the reader not to. A probe that skips certificate verification is satisfied by a substituted
# certificate as readily as by the right one, so the TLS half of such a check certifies nothing. This
# gate reads only fenced code blocks, never prose, so a guide may still NAME the flag in a sentence to
# warn against it.
if verify_safety=$(python3 tools/check_verify_safety.py 2>&1); then
  printf '%s\n' "$verify_safety"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$verify_safety"; then
    bad "check_verify_safety.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$verify_safety"; then
  bad "check_verify_safety.py crashed; its findings are incomplete"
  printf '%s\n' "$verify_safety" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$verify_safety"; then
  printf '%s\n' "$verify_safety"
  fail=1
else
  bad "check_verify_safety.py exited non-zero without reporting a gate result"
  printf '%s\n' "$verify_safety" | sed 's/^/          /'
fi

# section: guard-conventions
echo "== the curl guard conventions: -q leads every probe, and a glob URL carries -g =="
st_out="$(python3 -I -B tools/check_guard_conventions.py --self-test 2>&1)"
st_status=$?
printf '%s\n' "$st_out"
case "$st_out" in
  *"GATE guard-conventions-selftest: PASS"*)
    if [ "$st_status" -ne 0 ]; then
      bad "guard-conventions self-test printed PASS but exited $st_status"
    fi
    ;;
  *"GATE guard-conventions-selftest: FAIL"*)
    fail=1
    ;;
  *)
    bad "guard-conventions self-test crashed or exited without a gate result (exit $st_status)"
    ;;
esac

gc_out="$(python3 -I -B tools/check_guard_conventions.py --min-curls 176 . 2>&1)"
gc_status=$?
printf '%s\n' "$gc_out"
case "$gc_out" in
  *"GATE guard-conventions: PASS"*)
    if [ "$gc_status" -ne 0 ]; then
      bad "guard-conventions printed PASS but exited $gc_status"
    fi
    case "$gc_out" in
      *": [C1-"*|*": [C2-"*|*": [C3-"*|*": [C4-"*)
        bad "guard-conventions printed findings alongside a PASS result" ;;
    esac
    ;;
  *"GATE guard-conventions: FAIL"*)
    fail=1
    if [ "$gc_status" -eq 0 ]; then
      bad "guard-conventions reported FAIL but exited 0"
    fi
    ;;
  *)
    bad "guard-conventions crashed or exited without a gate result (exit $gc_status)"
    ;;
esac

# section: unfiltered-ss
echo "== ss listener probes are unfiltered (no ss | grep) =="
ss_st_out="$(python3 -I -B tools/check_unfiltered_ss.py --self-test 2>&1)"
ss_st_status=$?
printf '%s\n' "$ss_st_out"
case "$ss_st_out" in
  *"GATE unfiltered-ss-selftest: PASS"*)
    if [ "$ss_st_status" -ne 0 ]; then
      bad "unfiltered-ss self-test printed PASS but exited $ss_st_status"
    fi
    ;;
  *"GATE unfiltered-ss-selftest: FAIL"*)
    fail=1
    ;;
  *)
    bad "unfiltered-ss self-test crashed or exited without a gate result (exit $ss_st_status)"
    ;;
esac

ss_out="$(python3 -I -B tools/check_unfiltered_ss.py . 2>&1)"
ss_status=$?
printf '%s\n' "$ss_out"
case "$ss_out" in
  *"GATE unfiltered-ss: PASS"*)
    if [ "$ss_status" -ne 0 ]; then
      bad "unfiltered-ss printed PASS but exited $ss_status"
    fi
    case "$ss_out" in
      *": [SS-GREP-FILTER]"*)
        bad "unfiltered-ss printed findings alongside a PASS result" ;;
    esac
    ;;
  *"GATE unfiltered-ss: FAIL"*)
    fail=1
    if [ "$ss_status" -eq 0 ]; then
      bad "unfiltered-ss reported FAIL but exited 0"
    fi
    ;;
  *)
    bad "unfiltered-ss crashed or exited without a gate result (exit $ss_status)"
    ;;
esac

# section: changelog-prs
echo "== every merged pull request is recorded in the changelog =="
if changelog_prs=$(python3 tools/check_changelog_prs.py 2>&1); then
  printf '%s\n' "$changelog_prs"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$changelog_prs"; then
    bad "check_changelog_prs.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$changelog_prs"; then
  bad "check_changelog_prs.py crashed; the changelog coverage is unverified"
  printf '%s\n' "$changelog_prs" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$changelog_prs"; then
  printf '%s\n' "$changelog_prs"
  fail=1
else
  bad "check_changelog_prs.py exited non-zero without reporting a gate result"
  printf '%s\n' "$changelog_prs" | sed 's/^/          /'
fi

# section: changelog-prs-tests
echo "== the changelog-coverage gate still catches what it claims =="
if changelog_tests=$(python3 tools/test_changelog_prs.py 2>&1); then
  printf '%s\n' "$changelog_tests"
  if grep -q '^  FAIL  ' <<< "$changelog_tests"; then
    bad "test_changelog_prs.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$changelog_tests"; then
  bad "test_changelog_prs.py crashed; the changelog-coverage gate is unverified"
  printf '%s\n' "$changelog_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$changelog_tests"; then
  printf '%s\n' "$changelog_tests"
  fail=1
else
  bad "test_changelog_prs.py exited non-zero without reporting a result"
  printf '%s\n' "$changelog_tests" | sed 's/^/          /'
fi

# section: changelog-format
echo "== CHANGELOG dated headings: a blank line after each, newest first, one per date =="
# Row 3.45: a dated heading without the blank line after it slipped through on 2026-10-23,
# and six older ones lacked it. The gate reads CHANGELOG.md only, not the git history, so a
# history error in the coverage gate above cannot hide a format finding. The self-test runs
# first, so what runs against the changelog is the shipped gate.
for changelog_check in test_changelog_format.py check_changelog_format.py; do
  if changelog_format=$(python3 -I -B "tools/$changelog_check" 2>&1); then
    printf '%s\n' "$changelog_format"
    if grep -q '^  FAIL  ' <<< "$changelog_format" || ! grep -q '^  ok    ' <<< "$changelog_format"; then
      bad "$changelog_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$changelog_format"
    bad "$changelog_check failed"
  fi
done

# section: release-tests
echo "== the release check still refuses what it claims =="
# tools/check_release.py runs in the release procedure (CONTRIBUTING.md "Releasing"), not here:
# it needs a built release directory and runs this suite in a worktree of the target. Its
# self-test runs here so the shipped rule is tested on every pull request that changes it and on
# every whole-suite run. The self-test builds
# throwaway repositories with fixed commit dates and stays offline; the fixtures sit in
# October 2026 and in 2099, a date that has not ended, which a release may now target.
if release_tests=$(python3 -I -B tools/test_release.py 2>&1); then
  printf '%s\n' "$release_tests"
  if grep -q '^  FAIL  ' <<< "$release_tests" ||
     ! grep -qE '^  ok    [0-9]+ recorded cases for the release check$' <<< "$release_tests"; then
    bad "test_release.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$release_tests"
  bad "test_release.py failed"
fi

# section: todo-rows
echo "== TODO.md: one backlog row per line =="
# Finding F-TODO-ROW-CONCATENATION: a lost line break joins two banded-table rows onto one line,
# and Markdown renders the second inside the first row's last cell. #71 committed one, joining
# rows 1.13 and 1.19. The self-test runs first, so what runs against TODO.md is the shipped gate.
for todo_check in test_todo_rows.py check_todo_rows.py; do
  if todo_rows=$(python3 -I -B "tools/$todo_check" 2>&1); then
    printf '%s\n' "$todo_rows"
    if grep -q '^  FAIL  ' <<< "$todo_rows" || ! grep -q '^  ok    ' <<< "$todo_rows"; then
      bad "$todo_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$todo_rows"
    bad "$todo_check failed"
  fi
done

# section: prose-conventions
echo "== prose conventions: Oxford -ize and house placeholders =="
# A corpus-wide -ize conversion missed a word because its word list was incomplete, and the same word
# was written into a new guide hours later. A placeholder outside the house set reached the corpus and
# stayed. Both are closed lists, so this catches what it names and nothing else. Quoted and backticked
# spans are exempt from the SPELLING check only, so a changelog entry can quote the old spelling.
if prose_conv=$(python3 tools/check_prose_conventions.py 2>&1); then
  printf '%s\n' "$prose_conv"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$prose_conv"; then
    bad "check_prose_conventions.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$prose_conv"; then
  bad "check_prose_conventions.py crashed; its findings are incomplete"
  printf '%s\n' "$prose_conv" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$prose_conv"; then
  printf '%s\n' "$prose_conv"
  fail=1
else
  bad "check_prose_conventions.py exited non-zero without reporting a gate result"
  printf '%s\n' "$prose_conv" | sed 's/^/          /'
fi

# section: shell-blocks
echo "== every fenced bash block is shell =="
# Nothing in this suite checked whether the shell in a Verify block parses, and a reader
# pastes these into a terminal. What it catches is five real defects this corpus was
# carrying. What it does NOT catch is stated in its own docstring and in CONTRIBUTING rule 6:
# `head -c 11m`, and an angle-bracket placeholder, whose check was deleted after five rules
# for it were each beaten by legal shell. It now also proves shellcheck actually ran, rather
# than trusting an exit code that a silenced binary also returns.
if shellblocks=$(python3 tools/check_shell_blocks.py 2>&1); then
  printf '%s\n' "$shellblocks"
  # A gate that exits 0 while printing findings would otherwise read as a pass. A SKIP line
  # is not a finding: shellcheck may not be installed locally, which the gate says plainly.
  # CI installs and asserts the pinned shellcheck before this runs, so it never skips there.
  if grep -q '^  FAIL  ' <<< "$shellblocks"; then
    bad "check_shell_blocks.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$shellblocks"; then
  bad "check_shell_blocks.py crashed; the bash blocks are unchecked"
  printf '%s\n' "$shellblocks" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$shellblocks"; then
  printf '%s\n' "$shellblocks"
  fail=1
else
  bad "check_shell_blocks.py exited non-zero without reporting a gate result"
  printf '%s\n' "$shellblocks" | sed 's/^/          /'
fi

# section: python-version
echo "== local Python release matches CI =="
# Advisory like the shellcheck SKIP above: html.parser can change between releases.
# Never set fail here, including when the workflow or the interpreter cannot be read.
if ! python3 - <<'PY'
import re
import sys
from pathlib import Path

def notice(message):
    print(f"  SKIP  {message}")

workflow = Path(".github/workflows/checks.yml")
try:
    lines = workflow.read_text(encoding="utf-8").splitlines()
except (OSError, UnicodeError) as exc:
    notice(f"Python version comparison unavailable: cannot read {workflow}: {exc}")
else:
    pattern = r'[ \t]*PYTHON_VERSION: "([0-9]+\.[0-9]+\.[0-9]+)"[ \t]*'
    # Threat model (maintainer ruling, 2026-09-26, after #360's ruling (B)): this advisory notice guards
    # against ACCIDENTAL edits to checks.yml, not adversarial YAML. It is a stdlib text scan, not a YAML
    # parser, so a pin-looking line inside a block scalar with no real pin, a \u-escaped key, aliases or a
    # multi-document file can still mislead it. Such states are out of scope; a real missing pin also
    # breaks setup-python's `${{ env.PYTHON_VERSION }}` reference loudly in CI.
    # Count every PYTHON_VERSION token except references (env.PYTHON_VERSION, $PYTHON_VERSION,
    # ${PYTHON_VERSION}), so a second pin in any YAML form (quoted, spaced, flow mapping) is seen.
    keys = re.findall(r'(?<![.$\w])(?<!\$\{)PYTHON_VERSION(?!\w)', "\n".join(lines))
    pins = [line for line in lines if re.fullmatch(r'[ \t]*PYTHON_VERSION: "([0-9]+\.[0-9]+\.[0-9]+)"[ \t]*', line)]
    match = re.fullmatch(pattern, pins[0]) if len(keys) == 1 and len(pins) == 1 else None
    if match is None:
        notice('Python version comparison unavailable: expected exactly one '
               'PYTHON_VERSION: "X.Y.Z" line in .github/workflows/checks.yml '
               f'(found {len(keys)} PYTHON_VERSION keys and {len(pins)} pin lines)')
    else:
        pinned = match.group(1)
        running = sys.version.split()[0]
        if running == pinned:
            print(f"  ok    python3 {running} matches CI's pinned PYTHON_VERSION")
        else:
            notice(f"python3 {running} differs from CI's pinned PYTHON_VERSION {pinned}; "
                   "html.parser behaviour may differ, so a local green predicts CI less well")
PY
then
  printf '  SKIP  Python version comparison unavailable: python3 did not complete\n'
fi

# section: python-version-tests
echo "== the Python-version notice still reports without failing =="
if python_notice_tests=$(python3 tools/test_python_version_notice.py 2>&1); then
  printf '%s\n' "$python_notice_tests"
  if grep -q '^  FAIL  ' <<< "$python_notice_tests" ||
     ! grep -qE '^  ok    [0-9]+ recorded cases for the Python-version notice$' <<< "$python_notice_tests"; then
    bad "test_python_version_notice.py did not report a clean self-test"
  fi
else
  bad "test_python_version_notice.py failed"
  printf '%s\n' "$python_notice_tests"
fi

# section: shell-blocks-tests
echo "== the shell-block gate still catches what it claims =="
# Two of these cases assert what the gate does NOT catch, which are the very defects that
# prompted it. They are recorded so the file cannot quietly start claiming that coverage.
if shellblock_tests=$(python3 tools/test_shell_blocks.py 2>&1); then
  printf '%s\n' "$shellblock_tests"
  if grep -q '^  FAIL  ' <<< "$shellblock_tests"; then
    bad "test_shell_blocks.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$shellblock_tests"; then
  bad "test_shell_blocks.py crashed; the shell-block gate is unverified"
  printf '%s\n' "$shellblock_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$shellblock_tests"; then
  printf '%s\n' "$shellblock_tests"
  fail=1
else
  bad "test_shell_blocks.py exited non-zero without reporting a result"
  printf '%s\n' "$shellblock_tests" | sed 's/^/          /'
fi

# section: bracket-ranges
echo "== no bracket range in a fenced bash block works as a validator =="
# Outside the C locale GNU grep, GNU sed and bash [[ =~ ]] let a range such as [A-Za-z] or
# [0-9a-f] match non-ASCII letters and digits, so a guard written with one accepts values it
# claims to refuse; bash case is ASCII only while globasciiranges is on. The #356 review found
# it and the row 3.25 sweep found 87 more. Every range needs a spelled-out set or a
# tools/bracket_ranges_allow.txt entry for a non-validator. Quote-affected regions run to the
# last close in a conservative joined reading and may span physical lines; the docstring lists
# this over-flagging and the remaining misses. The locale-dependent development fuzzer is
# deliberately not part of these deterministic offline gates.
if bracket_ranges=$(python3 tools/check_bracket_ranges.py 2>&1); then
  printf '%s\n' "$bracket_ranges"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$bracket_ranges"; then
    bad "check_bracket_ranges.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$bracket_ranges"; then
  bad "check_bracket_ranges.py crashed; the bracket ranges are unchecked"
  printf '%s\n' "$bracket_ranges" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$bracket_ranges"; then
  printf '%s\n' "$bracket_ranges"
  fail=1
else
  bad "check_bracket_ranges.py exited non-zero without reporting a gate result"
  printf '%s\n' "$bracket_ranges" | sed 's/^/          /'
fi

# section: bracket-ranges-tests
echo "== the bracket-range gate still catches what it claims =="
# Eight of these cases assert what the gate does NOT catch, so the file cannot quietly start
# claiming that coverage.
if bracket_range_tests=$(python3 tools/test_bracket_ranges.py 2>&1); then
  printf '%s\n' "$bracket_range_tests"
  if grep -q '^  FAIL  ' <<< "$bracket_range_tests"; then
    bad "test_bracket_ranges.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$bracket_range_tests"; then
  bad "test_bracket_ranges.py crashed; the bracket-range gate is unverified"
  printf '%s\n' "$bracket_range_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$bracket_range_tests"; then
  printf '%s\n' "$bracket_range_tests"
  fail=1
else
  bad "test_bracket_ranges.py exited non-zero without reporting a result"
  printf '%s\n' "$bracket_range_tests" | sed 's/^/          /'
fi

# section: quote-guards
echo "== literal quote guards preserve diagnostics and status =="
python3 tools/test_quote_guards.py || fail=1

# section: convention-gates-tests
echo "== the convention gates still catch what review found =="
# The two gates above were broken repeatedly across rounds of cross-family review, and
# several of those rounds broke something an earlier round had fixed. Each case in this
# file is an input a reviewer actually ran, recorded so that a future change lands on a
# named prior finding instead of silently reopening it. It checks the gates, not the corpus.
if gate_tests=$(python3 tools/test_convention_gates.py 2>&1); then
  printf '%s\n' "$gate_tests"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$gate_tests"; then
    bad "test_convention_gates.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$gate_tests"; then
  bad "test_convention_gates.py crashed; the gates are unverified"
  printf '%s\n' "$gate_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$gate_tests"; then
  printf '%s\n' "$gate_tests"
  fail=1
else
  bad "test_convention_gates.py exited non-zero without reporting a result"
  printf '%s\n' "$gate_tests" | sed 's/^/          /'
fi

# section: local-links
echo "== local links resolve =="
# Heading slugs of a Markdown file, using the GitHub transformation: lowercase, drop everything but
# letters, digits, spaces and hyphens, then spaces to hyphens.
heading_slugs() {
  # Strip HTML comments and fenced code blocks first so a "# heading-looking" line inside a
  # ```code``` fence (or a commented-out heading) is never mistaken for a real Markdown heading.
  python3 - "$1" <<'PY'
import re, sys

text = open(sys.argv[1], encoding="utf-8").read()
sys.path.insert(0, "tools")
from version_basis import PROMPT_ANCHOR, mask_top
try:
    if mask_top(text, sys.argv[1]) != text:
        print(PROMPT_ANCHOR)
except (ValueError, TypeError, KeyError):
    pass  # Invalid generated content cannot supply the prompt anchor.
text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

in_fence = False
for line in text.splitlines():
    if line.strip().startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    m = re.match(r"#{1,}[ \t]+(.*)$", line)
    if not m:
        continue
    slug = m.group(1).lower()
    slug = re.sub(r"[^a-z0-9 -]", "", slug)
    slug = slug.replace(" ", "-")
    print(slug)
PY
}
links=1
while IFS= read -r target; do
  [ -n "$target" ] || continue
  path=${target%%#*}
  [ -n "$path" ] || continue
  if [ ! -e "$path" ]; then
    bad "broken link target: $target"
    links=0
    continue
  fi
  case "$target" in
    *"#"*)
      anchor=${target#*#}
      if [ -n "$anchor" ] && [ "${path##*.}" = "md" ]; then
        if ! heading_slugs "$path" | grep -qx -- "$anchor"; then
          bad "missing anchor #$anchor in $path"
          links=0
        fi
      fi
      ;;
  esac
done < <(grep -hoE '\]\([^)]+\)' ./*.md \
         | sed 's/^](//; s/)$//' \
         | grep -vE '^(https?:|mailto:|#)' \
         | sort -u)

# Same-document anchors: ](#heading) must name a heading in the file that contains it.
for f in *.md; do
  while IFS= read -r anchor; do
    [ -n "$anchor" ] || continue
    if ! heading_slugs "$f" | grep -qx -- "$anchor"; then
      bad "missing anchor #$anchor in $f"
      links=0
    fi
  done < <(grep -oE '\]\(#[^)]+\)' "$f" | sed 's/^](#//; s/)$//' | sort -u)
done

while IFS= read -r ref; do
  [ -n "$ref" ] || continue
  case "$ref" in
    /*) target="site$ref" ;;
    *)  target="site/$ref" ;;
  esac
  if [ ! -e "${target%%#*}" ]; then
    bad "site/index.html references a missing file: $ref"
    links=0
  fi
done < <(grep -oE '(href|src)="[^"]*"' site/index.html \
         | sed 's/^[a-z]*="//; s/"$//' \
         | grep -vE '^(https?:|mailto:|#|data:)' \
         | sort -u)

# Non-root sanctioned Markdown (requests/*.md): resolve each target relative to the file's OWN
# directory, so a same-directory link like ](TEMPLATE.md) and a parent link like ](../foo.md) both
# check the right path. The root loop above resolves relative to the repo root and would mis-resolve
# these. requests/*.md (added in #82) is the first sanctioned non-root Markdown.
for f in requests/*.md; do
  [ -e "$f" ] || continue
  dir=$(dirname "$f")
  while IFS= read -r target; do
    [ -n "$target" ] || continue
    path=${target%%#*}
    [ -n "$path" ] || continue
    case "$path" in
      /*)
        # A leading slash would resolve against requests/ (dir/$path collapses the double slash),
        # silently passing against the wrong file. requests/ links are repo-relative by convention.
        bad "absolute link target in $f: $target (use a repo-relative path)"
        links=0
        continue
        ;;
    esac
    if [ ! -e "$dir/$path" ]; then
      bad "broken link target in $f: $target"
      links=0
      continue
    fi
    case "$target" in
      *"#"*)
        anchor=${target#*#}
        if [ -n "$anchor" ] && [ "${path##*.}" = "md" ]; then
          if ! heading_slugs "$dir/$path" | grep -qx -- "$anchor"; then
            bad "missing anchor #$anchor in $dir/$path"
            links=0
          fi
        fi
        ;;
    esac
  done < <(grep -hoE '\]\([^)]+\)' "$f" \
           | sed 's/^](//; s/)$//' \
           | grep -vE '^(https?:|mailto:|#)' \
           | sort -u)
  while IFS= read -r anchor; do
    [ -n "$anchor" ] || continue
    if ! heading_slugs "$f" | grep -qx -- "$anchor"; then
      bad "missing anchor #$anchor in $f"
      links=0
    fi
  done < <(grep -oE '\]\(#[^)]+\)' "$f" | sed 's/^](#//; s/)$//' | sort -u)
done

[ "$links" = 1 ] && ok "every local link target and heading anchor resolves"

# section: copy-buttons
echo "== site copy buttons =="
# Every copy button names the <pre> it copies from; a dangling data-copy is a silently dead button.
# Every .html page under site/ is read, the 404 included; each finding names its page.
if missing_copy=$(python3 - <<'PY'
import re, sys
from pathlib import Path
missing = []
for page in sorted(Path("site").rglob("*.html")):
    html = page.read_text(encoding="utf-8")
    # Strip HTML comments first so a <pre id="..."> inside a comment cannot satisfy the check.
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    pre_ids = set()
    for attrs in re.findall(r'<pre\b([^>]*)>', html):
        # Require a preceding boundary so this matches a real id="..." attribute, not data-id="...".
        m = re.search(r'(?:^|\s)id="([^"]+)"', attrs)
        if m:
            pre_ids.add(m.group(1))
    missing += [f"{page}:{c}" for c in re.findall(r'\bdata-copy="([^"]+)"', html) if c not in pre_ids]
for c in missing:
    print(c)
sys.exit(1 if missing else 0)
PY
); then
  ok "every data-copy button in the site's pages targets a <pre id> that exists"
elif [ -n "$missing_copy" ]; then
  for entry in $missing_copy; do
    bad "${entry%%:*} has data-copy=\"${entry#*:}\" but no matching <pre id>"
  done
else
  bad "the site copy-button check itself failed to run"
fi


# section: pinned-citations
echo "== source citations are pinned, not mutable branch refs =="
# tools/check_pinned_citations.py flags raw.githubusercontent/github-blob citations whose REF segment
# is main or master (a main/master inside a file path is not flagged). Advisory: it fails only when a
# NEW mutable citation pushes the count above its recorded baseline, while the corpus-wide pinning
# sweep proceeds (see the sweep note in CHANGELOG.md). Self-test first, so what runs is the shipped entry point.
if pc_st="$(python3 -I -B tools/check_pinned_citations.py --self-test 2>&1)" &&
   printf '%s\n' "$pc_st" | grep -q '^PASS'; then
  ok "pinned-citation self-test"
else
  bad "pinned-citation self-test failed: $(printf '%s' "$pc_st" | tail -1)"
fi
pc="$(python3 -I -B tools/check_pinned_citations.py 2>&1)"
pc_rc=$?
if [ "$pc_rc" -eq 0 ]; then
  ok "$(printf '%s\n' "$pc" | tail -1)"
elif [ "$pc_rc" -eq 1 ]; then
  bad "a new mutable GitHub citation was added; pin it to a commit SHA or version tag:"
  printf '%s\n' "$pc" | sed 's/^/          /'
else
  bad "the pinned-citation gate could not complete (exit $pc_rc); failing closed:"
  printf '%s\n' "$pc" | sed 's/^/          /'
fi
# section: verify-marking
echo "== Verify fences, list items, table rows and prose declare demonstration or reasoning =="
# Keep retained exemptions visible; a baseline pass is not full corpus compliance.
# Run on its own, an absent/mismatched parser emits one SKIP and fence checks still run, but
# each guide whose intro recognition needs the parser is then a finding, so it exits 1; in
# this suite, the parser preflight at the top stops before this gate is reached.
# CI requires the pin even when this suite is invoked outside the workflow.
vm_args=(--strict)
if [ -n "${CI:-}" ]; then vm_args+=(--require-parser); fi
if vm_st=$(python3 -I -B tools/test_verify_marking.py 2>&1); then
  printf '%s\n' "$vm_st"
  if grep -q '^  FAIL  ' <<< "$vm_st" || ! grep -qE '^  ok    [0-9]+ Verify-marking fixture cases$' <<< "$vm_st"; then
    bad "Verify-marking self-test exited 0 without a clean result"
  elif vm=$(python3 -I -B tools/check_verify_marking.py "${vm_args[@]}" 2>&1); then
    printf '%s\n' "$vm"
    if grep -q '^  FAIL  ' <<< "$vm" || ! grep -q '^  ok    Verify marking:' <<< "$vm"; then
      bad "Verify-marking gate exited 0 without a clean result"
    fi
  else
    printf '%s\n' "$vm"
    bad "Verify-marking gate failed"
  fi
else
  printf '%s\n' "$vm_st"
  bad "Verify-marking self-test failed"
fi
# section: exposure-index
echo "== every port a guide names is mapped by the exposure index =="
# tools/check_exposure_index.py: a guide that documents a listener exposure-index.md never maps leaves a
# reader holding a scan result with nothing to search on. A fixed set of port shapes (listed in the
# checker's docstring), code blocks included; tools/exposure_index_allowlist.txt excuses non-listener
# matches with a reason, and a stale or redundant entry fails. Self-test first so what runs is the shipped checker; a failing self-test fails closed.
if ei_st="$(python3 -I -B tools/test_exposure_index.py 2>&1)" &&
   ! printf '%s\n' "$ei_st" | grep -q '^  FAIL  '; then
  ok "exposure-index self-test"
  ei="$(python3 -I -B tools/check_exposure_index.py 2>&1)"
  ei_rc=$?
  if [ "$ei_rc" -eq 0 ]; then
    ok "$(printf '%s\n' "$ei" | tail -1)"
  else
    bad "exposure-index gaps (exit $ei_rc):"
    printf '%s\n' "$ei" | sed 's/^/          /'
  fi
else
  bad "exposure-index self-test failed: $(printf '%s' "$ei_st" | tail -1)"
fi

# section: guide-quality
echo "== every guide has a well-formed guide-quality row with a computed verdict =="
# tools/check_guide_quality.py holds tools/guide_quality.tsv (the GQS 1.0 compliance matrix,
# QUALITY.md) well-formed: a known header, exactly one row per enrolled guide, valid types with K
# reserved for the two index guides, each group cell in the QUALITY.md 3.2 grammar, the verdict
# column equal to the 3.3 rule computation (a `?` cell counts as PARTIAL and blocks EXEMPLARY), and
# each row's body digest matching the guide's recorded body_sha256 (or the K file's whole-file
# sha256) unless the row is marked stale. Deterministic, offline, tree-only. The findings ledger
# (tools/guide_quality_ledger.tsv) is advisory in GQS 1.0 and is not checked here. Self-test first
# so what runs is the shipped checker; a failing self-test fails closed.
if gq_st="$(python3 -I -B tools/test_guide_quality.py 2>&1)" &&
   ! printf '%s\n' "$gq_st" | grep -q '^  FAIL  '; then
  ok "guide-quality self-test"
  gq="$(python3 -I -B tools/check_guide_quality.py 2>&1)"
  gq_rc=$?
  if [ "$gq_rc" -eq 0 ]; then
    ok "$(printf '%s\n' "$gq" | tail -1)"
  else
    bad "guide-quality findings (exit $gq_rc):"
    printf '%s\n' "$gq" | sed 's/^/          /'
  fi
else
  bad "guide-quality self-test failed: $(printf '%s' "$gq_st" | tail -1)"
fi

# section: walker
echo "== shared walker scans tracked files only =="
if walker=$(python3 -B tools/test_walk.py 2>&1); then
  printf '%s\n' "$walker"
  if grep -q '^  FAIL  ' <<< "$walker" || ! grep -q '^  ok    ' <<< "$walker"; then
    bad "test_walk.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$walker"
  bad "test_walk.py failed"
fi

# section: placeholders
echo "== no leftover authoring placeholders =="
# The self-test exercises failing fixtures and clean inputs through the real gate.
# The corpus run then checks tracked Markdown and VERSION, including TODO and DONE.
for placeholder_check in test_no_placeholders.py check_no_placeholders.py; do
  if placeholders=$(python3 -I -B "tools/$placeholder_check" 2>&1); then
    printf '%s\n' "$placeholders"
    if grep -q '^  FAIL  ' <<< "$placeholders" || ! grep -q '^  ok    ' <<< "$placeholders"; then
      bad "$placeholder_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$placeholders"
    bad "$placeholder_check failed"
  fi
done

# section: secrets
echo "== no committed secrets =="
# Deliberately narrow: only material that is a credential wherever it appears.
# A guide that must show sample key output will trip this; allowlist it here
# rather than widening the guides' exposure.
secret_re='BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,}|xox[baprs]-[A-Za-z0-9-]{10,}'
hits=$(grep -rnIE "$secret_re" --exclude-dir=.git . 2>&1)
secret_rc=$?
case "$secret_rc" in
  0)
    bad "possible credential material in the working tree:"
    printf '%s\n' "$hits" | sed 's/^/          /'
    ;;
  1)
    ok "no private keys or provider tokens found"
    ;;
  *)
    bad "cannot complete secrets scan (grep exit $secret_rc):"
    printf '%s\n' "$hits" | sed '/^[[:space:]]*$/d; s/^/          /'
    ;;
esac

# section: secrets-tests
echo "== secrets scan fails closed on read errors =="
if secret_tests=$(python3 -I -B tools/test_secrets_scan.py 2>&1); then
  printf '%s\n' "$secret_tests"
  if grep -q '^  FAIL  ' <<< "$secret_tests" || ! grep -q '^  ok    ' <<< "$secret_tests"; then
    bad "test_secrets_scan.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$secret_tests"
  bad "test_secrets_scan.py failed"
fi

# The generated site under site/ (baseline SPECIFICATION section 4.1 item 5, promoted). The site
# gates below run through run_gate, defined before the first section, and the pages are checked
# fresh before the CSP gate reads them.
# section: gate-runners
echo "== run_gate and scripts/pages-build.sh still fail closed =="
# tools/test_gate_runners.py runs run_gate, read out of this file, on stand-in gates, and runs
# scripts/pages-build.sh, as committed and in its promoted form at /, with a stand-in python3 that
# reports 3.10 or 3.11; its docstring lists the cases. It runs no real gate. It is checked here
# directly rather than through run_gate, so a broken run_gate cannot pass its own test.
if gate_runners=$(python3 -I -B tools/test_gate_runners.py 2>&1); then
  printf '%s\n' "$gate_runners"
  if grep -q '^  FAIL  ' <<< "$gate_runners" ||
     ! grep -qE '^  ok    [0-9]+ run_gate cases and [0-9]+ pages-build\.sh cases ' <<< "$gate_runners"; then
    bad "test_gate_runners.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$gate_runners"
  bad "test_gate_runners.py failed"
fi

# section: select-gates-tests
echo "== the pull-request gate selector maps paths to sections and fails safe =="
# tools/select_gates.py names the sections a pull request runs. Its cases cover each scoped kind of
# content, each kind of path that selects every section, an unmapped path and an empty list, and
# hold its map to the section names in this file and to the files in the checkout. It reads no git
# history and no network.
if select_tests=$(python3 -I -B tools/test_select_gates.py 2>&1); then
  printf '%s\n' "$select_tests"
  if grep -q '^  FAIL  ' <<< "$select_tests" ||
     ! grep -qE '^  ok    [0-9]+ recorded cases for the gate selector$' <<< "$select_tests"; then
    bad "test_select_gates.py exited 0 without a clean ok result"
  fi
else
  printf '%s\n' "$select_tests"
  bad "test_select_gates.py failed"
fi

# section: check-updates-tests
echo "== the skill's version-currency check and guide updater, tested offline =="
# tools/test_check_updates.py runs plugin/skills/secureconfig/scripts/check-updates.py on fixture
# guides and on stub answers for the GitHub API. It refuses every real connection, so this section
# stays offline like the rest of the suite; the script's own --check-online run is never tested here.
run_gate test_check_updates.py python3 -I -B tools/test_check_updates.py
# tools/test_update_guides.py runs plugin/skills/secureconfig/scripts/update-guides.sh in a temporary
# plugin tree with a curl shim first on PATH that serves fixture files; no socket or listener opens.
run_gate test_update_guides.py python3 -I -B tools/test_update_guides.py

# section: baseline-pin
echo "== the copied site template files match their pin =="
run_gate test_baseline_pin.py python3 -I -B tools/test_baseline_pin.py
run_gate test_copy_baseline.py python3 -I -B tools/test_copy_baseline.py
run_gate check_baseline_pin.py python3 -I -B tools/check_baseline_pin.py

# section: palette
echo "== the site palette passes the template's contrast gate =="
# From baseline 1.6.0 the palette gate is mandatory on every site (SPECIFICATION section 4 item 3).
# .baseline/check_palette.py is the template's own file, copied and pinned (the gate above holds it
# to its pin), so it prints its contrast tables and a RESULT line rather than an ok line, and
# run_gate's ok-line rule does not fit it. Its contract is its exit code (baseline 1.6.1 README):
# 0 pass, 1 fail or unreadable input, 2 usage error. This decides by the exit code only, never by
# the wording of the printed lines, and prints the gate's output in every case; any code other than
# 0 fails, a crash (1) or a signal included. Only the message reads the output: an exit 1 whose
# output holds a `Traceback (most recent call last):` line says the gate crashed, since Python exits
# 1 on an uncaught exception. secureconfig.ai has no site-palette.css.
# scripts/pages-build.sh runs the same call under set -e.
if palette=$(python3 -I -B .baseline/check_palette.py --site secureconfig --palettes site/assets/baseline/palettes.css 2>&1); then
  printf '%s\n' "$palette"
  ok "check_palette.py: the secureconfig palette passes in both schemes"
else
  palette_rc=$?
  printf '%s\n' "$palette"
  case "$palette_rc" in
    1)
      if grep -qxF 'Traceback (most recent call last):' <<< "$palette"; then
        bad "check_palette.py exited 1 with a Python traceback: the gate crashed; the palette is unverified"
      else
        bad "check_palette.py exited 1: a palette check failed or its input could not be read"
      fi
      ;;
    2) bad "check_palette.py exited 2, a usage error; the palette is unverified" ;;
    *) bad "check_palette.py exited $palette_rc, an unexpected error; the palette is unverified" ;;
  esac
fi

# section: overflow
echo "== no site page scrolls sideways at the template's widths =="
# Baseline 1.8.0's overflow check (SPECIFICATION section 4 item 3, recommended there), a gate here
# by the maintainer's ruling of 2026-11-04. .baseline/check_overflow.js is the template's own file,
# copied and pinned like the palette gate, and its contract is its exit code: 0 pass, 1 a failing
# case or a page it could not load, 2 a usage error; this decides by the exit code only, as the
# palette block does, and any other code fails. It loads each page in headless Chromium at its
# default widths (320, 360, 390 and 1512 px) in both schemes and refuses every request to an origin
# other than --base. That routing covers the HTTP requests a page makes, so with site/ served on
# 127.0.0.1, and the site self-contained (the site-draft section), it reaches no network. It needs
# node and the playwright package with its Chromium, installed before the suite: put playwright's
# node_modules folder on NODE_PATH and its browsers folder on PLAYWRIGHT_BROWSERS_PATH. When node is
# not on PATH, cannot load playwright, or finds no file at the path of the headless Chromium shell
# that a headless launch runs (asked through node, without launching it), a local run prints a SKIP
# and passes; CI installs the pinned playwright from tools/overflow/ and sets
# SECURECONFIG_REQUIRE_OVERFLOW=1, under which that is a failure. tools/test_gate_runners.py runs
# this section on stand-ins for node and the check.
# The pages, the one place they are listed: every generated page that answers 200; 404.html is the
# not-found page and is not listed, and the live site carries no /draft/ page (baseline
# SPECIFICATION section 4.1 item 0: drafts are built on the `draft` branch), so a page under
# site/draft/ is unlisted and fails here as well as in the site-draft section. The unlisted advisory
# page /advisories/n8n-2026-11-07-jposluns.html is a real generated page that answers 200, so it IS
# listed and checked; it is the one non-folder path in the list, named by its own file rather than
# an index.html. Its plain-text copy (.txt) is not a page, so this list neither names nor reads it. A
# listed folder page whose index.html is missing fails before the server starts, since http.server
# would answer its path with a directory listing. Every other .html or .htm file under site/ (in any
# case, at any depth, outside assets/, whose files scripts/build-site.py does not write) that is not
# a listed page fails, so a new page cannot go unchecked.
overflow_pages=(/ /advisories/n8n-2026-11-07-jposluns.html /checklist/ /disclosure/ /for-ai/ /for-humans/ /guides/ /license/ /quality/)
overflow_missing=""
for overflow_path in "${overflow_pages[@]}"; do
  # A folder path (ending with /) names its index.html; the one non-folder page, the unlisted
  # /advisories/n8n-2026-11-07-jposluns.html, names its own file. Either way a missing file is
  # reported, by exact path.
  case $overflow_path in
    */) overflow_file="site${overflow_path}index.html" ;;
    *)  overflow_file="site${overflow_path}" ;;
  esac
  if [ ! -f "$overflow_file" ]; then
    overflow_missing+=" $overflow_file"
  fi
done
overflow_unlisted=""
while IFS= read -r -d '' overflow_page; do
  overflow_path=${overflow_page#site}
  case $overflow_path in
    */index.html) overflow_path=${overflow_path%index.html} ;;
  esac
  case " ${overflow_pages[*]} " in
    *" $overflow_path "*) ;;
    *) overflow_unlisted+=" $overflow_page" ;;
  esac
done < <(find site -path site/assets -prune -o -type f \( -iname '*.html' -o -iname '*.htm' \) ! -path site/404.html -print0 | sort -z)
if [ -n "$overflow_unlisted" ]; then
  bad "the overflow check's page list does not name the generated page(s)$overflow_unlisted"
fi
# The server and the check run in the background of this shell, which waits for them, so its HUP,
# INT and TERM traps run at once and stop both by the PIDs started here (kill, then wait). The
# traps then reset themselves and send this shell the same signal, so it dies by that signal, as
# a shell running any other section does, and the suite's EXIT trap still runs. A signal that
# arrives while a launch is under way, before its PID is recorded, is held in overflow_signal and
# acted on once the PID is. A Ctrl-C reaches this shell, since the INT goes to the whole foreground
# group. Under --sections this shell is the cut copy, a child of the suite's own shell, so a TERM
# sent only to the suite's PID does not reach it.
overflow_pid=""
overflow_check_pid=""
overflow_dir=""
overflow_starting=""
overflow_signal=""
# shellcheck disable=SC2329  # only the HUP, INT and TERM trap strings below call it, unseen by shellcheck
overflow_trap() {
  overflow_signal=$1
  if [ -z "$overflow_starting" ]; then
    overflow_stop
    overflow_die "$1"
  fi
}
overflow_started() {
  overflow_starting=""
  if [ -n "$overflow_signal" ]; then
    overflow_stop
    overflow_die "$overflow_signal"
  fi
}
overflow_die() {
  trap - HUP INT TERM
  kill -s "$1" "$BASHPID"
}
overflow_stop() {
  if [ -n "$overflow_check_pid" ]; then
    kill "$overflow_check_pid" 2>/dev/null
    wait "$overflow_check_pid" 2>/dev/null
    overflow_check_pid=""
  fi
  if [ -n "$overflow_pid" ]; then
    kill "$overflow_pid" 2>/dev/null
    wait "$overflow_pid" 2>/dev/null
    overflow_pid=""
  fi
  if [ -n "$overflow_dir" ]; then
    rm -f "$overflow_dir/server.log" "$overflow_dir/check.out"
    rmdir "$overflow_dir" 2>/dev/null
    overflow_dir=""
  fi
}
# Exit 0 when the executable a headless chromium.launch() runs exists: playwright 1.64.1 launches
# its chromium-headless-shell there, not the full Chromium that chromium.executablePath() reports,
# so this asks the registry of the playwright-core that playwright loads for that executable's path.
# It loads playwright and launches nothing.
overflow_browser='require("playwright"); const core = require(require.resolve("playwright-core/lib/coreBundle", { paths: [require.resolve("playwright")] })); process.exit(require("fs").existsSync(core.registry.registry.findExecutable("chromium-headless-shell").executablePath()) ? 0 : 1)'
if [ -n "$overflow_missing" ]; then
  bad "the overflow check's page list names page(s) with no generated file:$overflow_missing; run python3 -I -B scripts/build-site.py; the pages are unverified"
elif ! command -v node >/dev/null 2>&1 || ! node -e "$overflow_browser" >/dev/null 2>&1; then
  if [ "${SECURECONFIG_REQUIRE_OVERFLOW:-}" = 1 ]; then
    bad "check_overflow.js needs node, the playwright package and its headless Chromium shell, and one of them was not found while SECURECONFIG_REQUIRE_OVERFLOW=1; the pages are unverified"
  else
    printf '  SKIP  node, the playwright package or its headless Chromium shell was not found; overflow check not run. To run it, set NODE_PATH to the node_modules folder holding playwright and PLAYWRIGHT_BROWSERS_PATH to the folder holding its Chromium\n'
  fi
elif ! overflow_dir=$(mktemp -d); then
  overflow_dir=""
  bad "check_overflow.js did not start: mktemp could not create a folder for the server log; the pages are unverified"
else
  trap 'overflow_trap HUP' HUP
  trap 'overflow_trap INT' INT
  trap 'overflow_trap TERM' TERM
  # Port 0 lets the kernel pick a free port, which -u makes http.server print at once; the loop
  # waits until the server answers.
  overflow_starting=1
  python3 -I -B -u -m http.server 0 --bind 127.0.0.1 --directory site > "$overflow_dir/server.log" 2>&1 &
  overflow_pid=$!
  overflow_started
  overflow_port=""
  overflow_status=""
  for _ in $(seq 100); do
    if ! kill -0 "$overflow_pid" 2>/dev/null; then
      break
    fi
    if [ -z "$overflow_port" ]; then
      overflow_port=$(sed -n 's/^Serving HTTP on 127\.0\.0\.1 port \([0-9][0-9]*\) .*/\1/p' "$overflow_dir/server.log")
    fi
    if [ -n "$overflow_port" ] &&
       { printf 'HEAD / HTTP/1.0\r\n\r\n' >&9 && IFS= read -r -t 5 overflow_status <&9; } 2>/dev/null 9<> "/dev/tcp/127.0.0.1/$overflow_port"; then
      case $overflow_status in
        'HTTP/1.'?' 200 '*) break ;;
      esac
    fi
    overflow_status=""
    sleep 0.1
  done
  if [ -z "$overflow_status" ]; then
    printf 'overflow: the local server for site/ did not answer in time; the end of its output:\n'
    tail -n 20 "$overflow_dir/server.log" | sed 's/^/          /'
    bad "check_overflow.js did not start, as the lines above say; the pages are unverified"
  else
    overflow_starting=1
    node .baseline/check_overflow.js --base "http://127.0.0.1:$overflow_port" "${overflow_pages[@]}" > "$overflow_dir/check.out" 2>&1 &
    overflow_check_pid=$!
    overflow_started
    wait "$overflow_check_pid"
    overflow_rc=$?
    overflow_check_pid=""
    cat "$overflow_dir/check.out"
    case "$overflow_rc" in
      0) ok "check_overflow.js: the ${#overflow_pages[@]} site pages pass at every default width in both schemes" ;;
      1) bad "check_overflow.js exited 1: a page scrolls sideways, has a table box past the window edge, throws a script error or answers with an HTTP error, or the check could not load a page or run" ;;
      2) bad "check_overflow.js exited 2, a usage error; the pages are unverified" ;;
      *) bad "check_overflow.js exited $overflow_rc, an unexpected error; the pages are unverified" ;;
    esac
  fi
  overflow_stop
  trap - HUP INT TERM
fi

# section: site-build
echo "== the site pages are a fresh build of their sources =="
run_gate test_build_site.py python3 -I -B tools/test_build_site.py
run_gate "build-site.py --check" python3 -I -B scripts/build-site.py --check

# section: install-blocks
echo "== the site build reads README.md's install section as the pinned parser does =="
# scripts/build-site.py reads the install commands with a small standard-library fence reader,
# because the Cloudflare Pages build that runs it needs only bash and Python and installs nothing.
# This gate, CI only, reads the same section with the pinned parser and fails unless it finds
# exactly the blocks the build read, with the same content, so an HTML comment or an indented
# block cannot change what the page shows unnoticed. The self-test runs first, so what runs
# against README.md is the shipped gate.
run_gate test_install_blocks.py python3 -I -B tools/test_install_blocks.py
run_gate check_install_blocks.py python3 -I -B tools/check_install_blocks.py

# section: site-draft
echo "== the site is self-contained, only the 404 is noindex, and there is no /draft/ =="
run_gate test_draft.py python3 -I -B tools/test_draft.py
run_gate check_draft.py python3 -I -B tools/check_draft.py

# section: pages-build
echo "== the Pages build check's Python files parse as Python 3.11 =="
run_gate test_pages_build.py python3 -I -B tools/test_pages_build.py

# section: site-csp
echo "== every site page fits the template page model and the CSP is the shared policy =="
# Since promotion tools/check_csp_hashes.py holds every page under site/ to the template page
# model: no inline <style> or <script> at all (a page's scripts are the generator's same-origin
# baseline forms: deferred files, and from baseline 1.6.0 the 1 scheme.js head script), no style=
# attribute, no on* handler, only the template's elements; and it
# requires site/_headers to carry exactly the shared template policy of baseline SPECIFICATION
# section 9, under /* alone, with no second policy, no detach and no X-Robots-Tag. The same gate
# refuses XHTML, compressed SVG and symbolic links under site/, and fails any SVG carrying a
# <script>, an on* handler, a javascript: URL or inline style (rows 3.18 and P5). The hash model
# it enforced on the old hand-written pages, and #1181's temporary 'unsafe-inline' acceptance,
# left with those pages: there is no inline block anywhere to pin or permit.
if csp=$(python3 tools/check_csp_hashes.py 2>&1); then
  printf '%s\n' "$csp"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$csp"; then
    bad "check_csp_hashes.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$csp"; then
  bad "check_csp_hashes.py crashed; the CSP hashes are unverified"
  printf '%s\n' "$csp" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$csp"; then
  printf '%s\n' "$csp"
  fail=1
else
  bad "check_csp_hashes.py exited non-zero without reporting a gate result"
  printf '%s\n' "$csp" | sed 's/^/          /'
fi

# section: site-csp-tests
echo "== the CSP page-model gate still catches what review found =="
# Five review rounds (#352) taught the gate's page model where html.parser and a browser part
# company, and the test file keeps every one of those refusals, retargeted to the generated
# pages; its docstring records which hash-model case groups retired at promotion and why.
if csp_tests=$(python3 tools/test_csp_hashes.py 2>&1); then
  printf '%s\n' "$csp_tests"
  if grep -q '^  FAIL  ' <<< "$csp_tests"; then
    bad "test_csp_hashes.py printed findings but exited 0"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$csp_tests"; then
  bad "test_csp_hashes.py crashed; the CSP hash gate is unverified"
  printf '%s\n' "$csp_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$csp_tests"; then
  printf '%s\n' "$csp_tests"
  fail=1
else
  bad "test_csp_hashes.py exited non-zero without reporting a result"
  printf '%s\n' "$csp_tests" | sed 's/^/          /'
fi

# section: security-txt
echo "== site/.well-known/security.txt carries the owner's six fields =="
# W3 (the owner's decision of 2026-11-03): the repository serves security.txt and Cloudflare's own
# security.txt feature is off, so a wrong contact or policy URL would ship with nothing to say so.
# tools/check_security_txt.py compares the file with the six fields and values it records. It reads
# no network and no clock, so whether the live domain serves the file, and whether Expires has
# passed, are not checked here. The self-test runs first, so what runs against the file is the
# shipped gate.
for security_txt_check in test_security_txt.py check_security_txt.py; do
  if security_txt=$(python3 -I -B "tools/$security_txt_check" 2>&1); then
    printf '%s\n' "$security_txt"
    if grep -q '^  FAIL  ' <<< "$security_txt" || ! grep -q '^  ok    ' <<< "$security_txt"; then
      bad "$security_txt_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$security_txt"
    bad "$security_txt_check failed"
  fi
done

# section: sitemap
echo "== site/sitemap.xml lists the live pages dated by their last change, and robots.txt names it =="
# W4 (the owner's decision A6 of 2026-11-03): sitemap.xml lists every indexable live page with a
# lastmod and no /draft/ page (the live site carries none), and robots.txt carries one Sitemap
# line. tools/check_sitemap.py parses the sitemap with expat and maps each loc to its page under
# site/, reading no git history.
# tools/check_sitemap_lastmod.py then requires each lastmod to equal the date of the last commit
# that changed its page (git log -1 --format=%cs), or today's UTC date for a listed page with
# uncommitted or staged changes, and fails closed in a shallow clone or a tree without its
# history, so this suite needs the full history that CI's checkout fetches. Each self-test runs
# before its gate, so what runs against the files is the shipped gate.
for sitemap_check in test_sitemap.py check_sitemap.py test_sitemap_lastmod.py check_sitemap_lastmod.py; do
  if sitemap=$(python3 -I -B "tools/$sitemap_check" 2>&1); then
    printf '%s\n' "$sitemap"
    if grep -q '^  FAIL  ' <<< "$sitemap" || ! grep -q '^  ok    ' <<< "$sitemap"; then
      bad "$sitemap_check exited 0 without a clean ok result"
    fi
  else
    printf '%s\n' "$sitemap"
    bad "$sitemap_check failed"
  fi
done

# section: workflow-pins
echo "== workflow actions are pinned to full commit SHAs =="
# Row 3.17 (#348) pinned every workflow `uses:` to a full commit SHA with a `# vX.Y.Z` comment naming
# the release, and nothing held it there: the next `@v4` would have merged green. This fails a tag, a
# branch, a short or uppercase SHA, a missing or malformed release comment, and a Docker action not
# pinned by digest, in the workflows and in every action.yml. It reads the files line by line and
# refuses any YAML construct it does not model rather than guess; its docstring says why that is sound.
if workflow_pins=$(python3 tools/check_workflow_pins.py 2>&1); then
  printf '%s\n' "$workflow_pins"
  # A gate that exits 0 while printing findings would otherwise read as a pass.
  if grep -q '^  FAIL  ' <<< "$workflow_pins"; then
    bad "check_workflow_pins.py printed findings but exited 0"
  elif ! grep -qE '^  ok    [0-9]+ uses: lines across [0-9]+ files ' <<< "$workflow_pins"; then
    # An exit 0 counts only with the gate's ok line, which it prints only after checking something.
    bad "check_workflow_pins.py exited 0 without printing its ok line"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$workflow_pins"; then
  bad "check_workflow_pins.py crashed; the workflow pins are unverified"
  printf '%s\n' "$workflow_pins" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$workflow_pins"; then
  printf '%s\n' "$workflow_pins"
  fail=1
else
  bad "check_workflow_pins.py exited non-zero without reporting a gate result"
  printf '%s\n' "$workflow_pins" | sed 's/^/          /'
fi

# section: workflow-pins-tests
echo "== the workflow-pin gate still catches what it claims =="
# Every check in the gate has a case here that fails when the check is removed. Some cases assert a
# PASS instead, because a gate that alarms on them would be switched off: a `run: |` block of shell
# punctuation, a commented-out step, and the word `uses` in a step name among them.
if workflow_pin_tests=$(python3 tools/test_workflow_pins.py 2>&1); then
  printf '%s\n' "$workflow_pin_tests"
  if grep -q '^  FAIL  ' <<< "$workflow_pin_tests"; then
    bad "test_workflow_pins.py printed findings but exited 0"
  elif ! grep -qE '^  ok    [0-9]+ recorded cases for the workflow-pin gate' <<< "$workflow_pin_tests"; then
    bad "test_workflow_pins.py exited 0 without printing its ok line"
  fi
elif grep -qE '^Traceback \(most recent call last\):|^[A-Za-z_.]+Error: ' <<< "$workflow_pin_tests"; then
  bad "test_workflow_pins.py crashed; the workflow-pin gate is unverified"
  printf '%s\n' "$workflow_pin_tests" | sed 's/^/          /'
elif grep -q '^  FAIL  ' <<< "$workflow_pin_tests"; then
  printf '%s\n' "$workflow_pin_tests"
  fail=1
else
  bad "test_workflow_pins.py exited non-zero without reporting a result"
  printf '%s\n' "$workflow_pin_tests" | sed 's/^/          /'
fi

# section: lychee-tests
echo "== weekly link reports fail closed on incomplete sweeps =="
if lychee_tests=$(python3 -I -B tools/test_lychee_report.py 2>&1); then
  printf '%s\n' "$lychee_tests"
  if ! grep -qE '^  ok    [0-9]+ lychee fixture cases$' <<< "$lychee_tests"; then
    bad "lychee report fixtures exited 0 without a result"
  fi
else
  printf '%s\n' "$lychee_tests"
  bad "lychee report fixtures failed"
fi

# section: citation-sweep-import
echo "== the advisory citation sweep still imports =="
# NOT a gate on the citations themselves: report_citation_drift.py reaches the network and can
# never run in this suite. But it imports SOURCES_RE, headings and section_body from
# check_guide_shape.py, and renaming or reshaping any of those would leave every gate green and
# break the weekly run with a traceback nobody sees until Monday. Importing the module is
# offline, costs nothing, and is the cheapest thing that keeps the two in step.
# Calling sources_text exercises the borrowed signatures too: importing a name proves it still
# exists, and a reviewer showed that reshaping one of them keeps the import green and fails at
# the call, which is the same Monday-morning traceback one level down.
if imp=$(cd tools && python3 -c 'import report_citation_drift as r; r.sources_text("")' 2>&1); then
  ok "report_citation_drift.py still imports what it borrows from check_guide_shape.py"
else
  bad "report_citation_drift.py no longer imports; the weekly citation sweep would fail: $imp"
fi

# section: aiqt-baseline
echo "== AIQT baseline =="
# The vendored gates derive the repo root from their own location, so they operate on this tree.
# AIQT_SITE_HOST retargets the upstream helpers from their aiqt.ai default; AIQT_NEWTAB_ROOTS limits the
# new-tab gate to this repository's site/ (a local patch; upstream also requires opf/site/). See .aiqt/PIN.
export AIQT_SITE_HOST=secureconfig.ai
export AIQT_NEWTAB_ROOTS=site
for gate in check_site check_no_dashes check_newtab; do
  if out=$(python3 "tools/${gate}.py" 2>&1); then
    ok "${gate}"
  else
    bad "${gate}"
    printf '%s\n' "$out" | sed 's/^/          /'
  fi
done
if cmp -s CLAUDE.md AGENTS.md; then
  ok "CLAUDE.md and AGENTS.md are identical"
else
  bad "CLAUDE.md and AGENTS.md have diverged; they are one adapter in two files"
fi
python3 tools/gen_aiqt_settings.py --check || fail=1

# end of sections
echo
if [ "$fail" = 0 ] && [ -n "$selected_sections" ]; then
  echo "All selected gates passed ($selected_sections); the other sections did not run."
elif [ "$fail" = 0 ]; then
  echo "All gates passed."
else
  echo "One or more gates failed."
fi
exit "$fail"
