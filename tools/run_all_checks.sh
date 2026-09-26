#!/usr/bin/env bash
# Whole-corpus gate suite for secureconfig.
#
# Every gate here is deterministic and offline: no gate reaches the network, so no
# vendor outage or rate limit can change a gate's answer. The CI job that runs this
# suite is not offline: .github/workflows/checks.yml fetches its pinned actions,
# Python and shellcheck before the suite starts, and an outage there can fail the
# job. External link rot is caught separately by the weekly lychee sweep, which
# stays advisory so that a site being down cannot block a merge.
#
# Usage: tools/run_all_checks.sh   (runs from any directory)
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2

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
    CONTRIBUTING.md|SECURITY.md|CLAUDE.md|AGENTS.md|CHANGELOG.md|README.sources.md|TODO.md|DONE.md|DECISIONS.md|PENDING-DECISIONS.md|controls-reference.md) return 0 ;;
    *) return 1 ;;
  esac
}

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

echo "== every guide is wired into the site =="
wired=1
# Strip HTML comments across the whole file (re.S, not a line-at-a-time sed) so a menu link or
# README row commented out across multiple lines does not count as wired.
menu_html=$(python3 - <<'PY'
import re
html = open("site/index.html", encoding="utf-8").read()
print(re.sub(r"<!--.*?-->", "", html, flags=re.S))
PY
)
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
  grep -qE "<a href=\"https://github.com/jposluns/secureconfig/blob/main/$f\"" <<< "$menu_html" \
    || { bad "$f is not linked from the site/index.html menu"; wired=0; }
done
[ "$wired" = 1 ] && ok "every guide is listed in the build script, linked from llms.txt, indexed in README.md, and in the site menu"

echo "== README guide-index categories match the site menu and site/llms.txt =="
# The README's "## Guide index" section, the site's left-hand menu and site/llms.txt are three
# hand-maintained copies of the same category list; nothing else in this suite catches them
# drifting apart. They had drifted: llms.txt carried ten sections of its own against the
# README's twelve, and three independent reviews raised it before anything compared them.
# llms.txt is checked on its guide MEMBERSHIP too, not just its headings, because a guide
# filed under a different category in one file than the other is the same defect one level
# down. Its "Start here" and "Optional" sections are the llms.txt format's own and are exempt.
if cat_diff=$(python3 - <<'PY'
import re, sys

readme = open("README.md", encoding="utf-8").read()
readme = re.sub(r"<!--.*?-->", "", readme, flags=re.S)
m = re.search(r"^## Guide index[ \t]*$", readme, re.M)
if not m:
    print("README.md has no '## Guide index' section")
    sys.exit(1)
rest = readme[m.end():]
m2 = re.search(r"^## ", rest, re.M)
section = rest[:m2.start()] if m2 else rest
readme_cats = re.findall(r"^### (.+?)[ \t]*$", section, re.M)

html = open("site/index.html", encoding="utf-8").read()
html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
excluded = {"On this page", "Reference"}
site_cats = [c for c in re.findall(r'<h2 class="sidenav-h">([^<]*)</h2>', html) if c not in excluded]

llms = open("site/llms.txt", encoding="utf-8").read()
llms = re.sub(r"<!--.*?-->", "", llms, flags=re.S)
exempt = {"Start here", "Optional"}
llms_blocks = re.split(r"^## ", llms, flags=re.M)[1:]
llms_cats, llms_members = [], {}
for block in llms_blocks:
    name = block.split("\n", 1)[0].strip()
    if name in exempt:
        continue
    llms_cats.append(name)
    llms_members[name] = re.findall(r"^- \[([a-z0-9.-]+)\]\(", block, re.M)

readme_members = {}
for block in re.split(r"^### ", section, flags=re.M)[1:]:
    name = block.split("\n", 1)[0].strip()
    readme_members[name] = [g[:-3] for g in
                            re.findall(r"^\|\s*\[([^\]]+\.md)\]\(", block, re.M)]

problems = []
if readme_cats != site_cats:
    problems.append(("site menu", site_cats))
if readme_cats != llms_cats:
    problems.append(("site/llms.txt", llms_cats))

if not problems:
    for name in readme_cats:
        if readme_members.get(name) != llms_members.get(name):
            print(f"category {name!r} lists different guides in README.md and site/llms.txt")
            print("  README:    " + repr(readme_members.get(name)))
            print("  llms.txt:  " + repr(llms_members.get(name)))
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
  ok "README guide-index, the site menu and site/llms.txt carry the same categories"
else
  bad "README guide-index categories do not match the site menu categories"
  printf '%s\n' "$cat_diff" | sed 's/^/          /'
fi

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
      *": [C1-"*|*": [C2-"*)
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

echo "== the bracket-range gate still catches what it claims =="
# Seven of these cases assert what the gate does NOT catch, so the file cannot quietly start
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

echo "== literal quote guards preserve diagnostics and status =="
python3 tools/test_quote_guards.py || fail=1

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

echo "== local links resolve =="
# Heading slugs of a Markdown file, using the GitHub transformation: lowercase, drop everything but
# letters, digits, spaces and hyphens, then spaces to hyphens.
heading_slugs() {
  # Strip HTML comments and fenced code blocks first so a "# heading-looking" line inside a
  # ```code``` fence (or a commented-out heading) is never mistaken for a real Markdown heading.
  python3 - "$1" <<'PY'
import re, sys

text = open(sys.argv[1], encoding="utf-8").read()
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

echo "== site copy buttons =="
# Every copy button names the <pre> it copies from; a dangling data-copy is a silently dead button.
if missing_copy=$(python3 - <<'PY'
import re, sys
html = open("site/index.html", encoding="utf-8").read()
# Strip HTML comments first so a <pre id="..."> inside a comment cannot satisfy the check.
html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
pre_ids = set()
for attrs in re.findall(r'<pre\b([^>]*)>', html):
    # Require a preceding boundary so this matches a real id="..." attribute, not data-id="...".
    m = re.search(r'(?:^|\s)id="([^"]+)"', attrs)
    if m:
        pre_ids.add(m.group(1))
missing = [c for c in re.findall(r'\bdata-copy="([^"]+)"', html) if c not in pre_ids]
for c in missing:
    print(c)
sys.exit(1 if missing else 0)
PY
); then
  ok "every data-copy button in site/index.html targets a <pre id> that exists"
elif [ -n "$missing_copy" ]; then
  for id in $missing_copy; do
    bad "site/index.html has data-copy=\"$id\" but no <pre id=\"$id\">"
  done
else
  bad "the site copy-button check itself failed to run"
fi


echo "== source citations are pinned, not mutable branch refs =="
# tools/check_pinned_citations.py flags raw.githubusercontent/github-blob citations whose REF segment
# is main or master (a main/master inside a file path is not flagged). Advisory: it fails only when a
# NEW mutable citation pushes the count above its recorded baseline, while the corpus-wide pinning
# sweep proceeds (see the sweep note in CHANGELOG.md). Self-test first, so what runs is the shipped entry point.
pc_st="$(python3 -I -B tools/check_pinned_citations.py --self-test 2>&1)"
if [ $? -eq 0 ] && printf '%s\n' "$pc_st" | grep -q '^PASS'; then
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
echo "== reasoned Verify steps are tracked by a demonstration backlog row =="
# tools/check_reasoned_rows.py: CONTRIBUTING rule 5 makes a demonstration backlog row a condition of the
# reasoned-step allowance ("reasoned is a debt, not a destination"). BLOCKING since 2026-09-24 (maintainer
# ruling): --strict fails the suite on a reasoned guide that no TODO.md/DONE.md demonstration row tracks and
# tools/reasoned_row_baseline.txt does not grandfather (the baseline is now empty). Self-test first so what
# runs is the shipped checker; a failing self-test fails closed.
rr_st="$(python3 -I -B tools/test_reasoned_rows.py 2>&1)"
if [ $? -eq 0 ] && ! printf '%s\n' "$rr_st" | grep -q '^  FAIL  '; then
  ok "reasoned-row self-test"
  rr="$(python3 -I -B tools/check_reasoned_rows.py --strict 2>&1)"
  rr_rc=$?
  if [ "$rr_rc" -eq 0 ]; then
    ok "$(printf '%s\n' "$rr" | tail -1)"
  else
    bad "reasoned Verify steps without a demonstration backlog row (exit $rr_rc):"
    printf '%s\n' "$rr" | sed 's/^/          /'
  fi
else
  bad "reasoned-row self-test failed: $(printf '%s' "$rr_st" | tail -1)"
fi
echo "== every port a guide names is mapped by the exposure index =="
# tools/check_exposure_index.py: a guide that documents a listener exposure-index.md never maps leaves a
# reader holding a scan result with nothing to search on. A fixed set of port shapes (listed in the
# checker's docstring), code blocks included; tools/exposure_index_allowlist.txt excuses non-listener
# matches with a reason, and a stale or redundant entry fails. Self-test first so what runs is the shipped checker; a failing self-test fails closed.
ei_st="$(python3 -I -B tools/test_exposure_index.py 2>&1)"
if [ $? -eq 0 ] && ! printf '%s\n' "$ei_st" | grep -q '^  FAIL  '; then
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
echo "== no committed secrets =="
# Deliberately narrow: only material that is a credential wherever it appears.
# A guide that must show sample key output will trip this; allowlist it here
# rather than widening the guides' exposure.
secret_re='BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22,}|xox[baprs]-[A-Za-z0-9-]{10,}'
if hits=$(grep -rnIE "$secret_re" --exclude-dir=.git . 2>/dev/null) && [ -n "$hits" ]; then
  bad "possible credential material in tracked files:"
  printf '%s\n' "$hits" | sed 's/^/          /'
else
  ok "no private keys or provider tokens found"
fi

echo "== site CSP pins every inline block by hash =="
# The CSP in site/_headers names the sha256 of each inline <script> and <style> in every page
# tools/check_csp_hashes.py lists (the same gate refuses an on* handler on a page, refuses XHTML,
# compressed SVG and symbolic links under site/, and fails any SVG carrying a <script>, an on*
# handler, a javascript: URL or inline style; rows 3.18 and P5), so an edited block cannot ship
# with a stale hash: the browser would then
# refuse to run the script, or refuse to apply the stylesheet and render the page unstyled.
# Both are silent in a diff and obvious to a visitor. This check used to live here as an
# embedded Python heredoc and covered only script-src, while style-src carried
# 'unsafe-inline', which permits any inline style including an injected one.
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

echo "== the CSP hash gate still catches what review found =="
# The gate's first version read the page with regular expressions and a reviewer demonstrated
# six ways that was wrong. It reads the page with html.parser now. One case is a FALSE ALARM
# the old version raised rather than a miss it had, and the file checks that the old approach
# really would have failed it, so the case cannot quietly stop meaning anything.
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

echo
if [ "$fail" = 0 ]; then
  echo "All gates passed."
else
  echo "One or more gates failed."
fi
exit "$fail"
