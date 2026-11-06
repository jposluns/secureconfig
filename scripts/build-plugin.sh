#!/usr/bin/env bash
# Build the Agent Plugin's bundled references from the guides.
#
# The plugin ships every guide inside itself rather than pointing at raw URLs, so an assistant
# with no network still has them. That freezes the content at the version in plugin.json, which
# is why each guide keeps its own "Sources (checked <month year>)" section and why SKILL.md tells
# the reader to check a default against the vendor page when it matters to the decision.
#
# The file list is NOT maintained here. It is whatever scripts/build-llms-full.sh reports under
# --list-guides, so "what counts as a guide" has one definition and the two bundles cannot drift.
set -euo pipefail

cd "$(dirname "$0")/.."
dest="plugin/skills/secure-deployment-config/references"

mapfile -t files < <(bash scripts/build-llms-full.sh --list-guides)
if [ "${#files[@]}" -eq 0 ]; then
  echo "build-llms-full.sh --list-guides reported nothing" >&2
  exit 1
fi

if [ "${1:-}" = "--list-inputs" ]; then
  # The guide list, the script it came from, and VERSION: changing build-llms-full.sh changes what
  # this bundle contains, and VERSION sets plugin.json's version below, so all three are inputs to
  # this build and the generated-file record has to say so.
  printf '%s\n' "${files[@]}" scripts/build-llms-full.sh VERSION \
    tools/version_basis.py tools/version_basis_guides.txt tools/version_basis_sources_baseline.txt tools/_markdown.py tools/check_guide_shape.py tools/check_verify_marking.py tools/_verify_sections.py CHANGELOG.md
  exit 0
fi

# The checks below read the guides and SKILL.md with the pinned CommonMark parser, through
# gate_parser() in tools/check_verify_marking.py. When that parser cannot be loaded at all, from a
# lock it cannot read or parse or from a markdown_it package without the installed version
# metadata of markdown-it-py or mdurl, gate_parser() raises something other than
# ParserUnavailable. The version-basis check below already refuses a lock it cannot read or parse
# in one line of its own, but it does not catch the PackageNotFoundError of missing metadata,
# which ends it in a traceback, so the build refuses each of these here first, in one line naming
# the cause. An absent or mismatched parser, which raises ParserUnavailable, is left to the checks
# below, which refuse it in their own words.
python3 - <<'PY'
import sys
sys.path.insert(0, "tools")
from check_verify_marking import ParserUnavailable, gate_parser
try:
    gate_parser(required=True)
except ParserUnavailable:
    pass
except Exception as exc:
    cause = " ".join(f"{type(exc).__name__}: {exc}".split())
    sys.exit("the pinned parser cannot be loaded from tools/requirements-gates.txt and the "
             f"installed markdown-it-py and mdurl: {cause}; refusing to build")
PY

# Each reference is a whole validated guide, in either supported layout.
python3 tools/version_basis.py --check

rm -rf "$dest"
mkdir -p "$dest"
for f in "${files[@]}"; do
  cp "$f" "$dest/$f"
done

# Keep the plugin manifest's version in lockstep with the repository VERSION (1.0.<pull request
# number>), so an adopter's updater can tell a refreshed bundle from an earlier one and never has to
# read stale configuration behind a version that says it is current. The whole-corpus staleness gate
# re-runs this build in the working tree and diffs its output, so a plugin.json whose version has
# drifted from VERSION there is caught as a stale bundle. The gate in
# tools/check_generated_committed.py also checks the committed plugin.json against the
# committed VERSION, and rebuilds the committed tree
# when the working tree differs from it, so a bump committed without this rebuild is caught too.
version=$(cat VERSION)
printf '%s' "$version" | grep -qxE '1\.0\.[0-9]+' \
  || { echo "VERSION is '$version', not the expected 1.0.<number>; refusing to build" >&2; exit 1; }
# sed -i edits in place and preserves the file's mode, unlike a mktemp temp file whose 0600 would
# follow the mv. The pattern is anchored to the top-level two-space-indented key so a nested
# "version" (in a future dependency block) is never rewritten.
sed -i "s/^\(  \"version\": \)\"[^\"]*\"/\1\"$version\"/" plugin/plugin.json
# A no-match sed exits 0 and changes nothing, and the staleness gate cannot see that (its rebuild
# no-ops identically), so the version would drift silently. Confirm the intended line is present and
# fail loudly if the manifest was reformatted so the pattern stopped matching.
grep -qF "  \"version\": \"$version\"," plugin/plugin.json \
  || { echo "plugin.json version did not update to $version; its version line may have been reformatted" >&2; exit 1; }

# SKILL.md states the same version in its metadata and the guide count in "This skill carries N
# short guides", and nothing rewrote either, so both drifted. The count is the length of
# counted_guides() in tools/_verify_sections.py, the list the guide-counts gate in
# tools/run_all_checks.sh and tools/check_generated_committed.py count too, so the README and
# SKILL.md counts have one definition. The version sed is limited to the front matter (line 1,
# which is "---", to the next "---" line) and, inside it, to the "metadata:" mapping (that line
# to the next line that does not start with a space). Each value is confirmed afterwards for the
# reason given for plugin.json above, and the version in that same scope, so a version-shaped
# line elsewhere in the file neither takes the rewrite nor passes the confirmation.
skill="plugin/skills/secure-deployment-config/SKILL.md"
count=$(python3 -c 'import sys; from pathlib import Path; sys.path.insert(0, "tools"); from _verify_sections import counted_guides; print(len(counted_guides(Path("."))))')
printf '%s' "$count" | grep -qxE '[1-9][0-9]*' \
  || { echo "the guide count is '$count', not a positive number; refusing to build" >&2; exit 1; }
sed -i -e "1,/^---\$/ { /^metadata:\$/,/^[^ ]/ s/^\(  version: \)\"[^\"]*\"\$/\1\"$version\"/ }" \
  -e "s/\(This skill carries \)[0-9][0-9]*\( short guides\)/\1$count\2/" "$skill"
# Every "  version:" line of the metadata mapping in the front matter, then the closing "---"; this
# prints nothing when line 1 is not "---", and no "---" when the front matter does not close.
metadata=$(sed -n -e '1 { /^---$/!q }' -e '2,$ { /^---$/ { p; q }; /^metadata:$/,/^[^ ]/ { /^  version:/p } }' "$skill")
[ "$metadata" = "  version: \"$version\""$'\n'"---" ] \
  || { echo "SKILL.md version did not update to $version; its front matter must open and close with a \"---\" line and its metadata must hold exactly one line '  version: \"...\"'" >&2; exit 1; }
# The count is confirmed in SKILL.md's source, front matter included, less the whole HTML comments
# that stand as HTML blocks of their own outside any list item or block quote in its body, by
# skill_counts() in tools/_verify_sections.py, which tools/check_generated_committed.py also
# calls, and the sentence must appear there exactly once, so a copy in a removed comment can
# neither stand in for a missing sentence nor sit beside a second one; a copy in code, a title, a
# destination, a label, an info string or the front matter counts, wrapped or not. The sed above
# rewrites the sentence only on one line, so that one copy must also stand on one line as
# written, with 1 space between its words, and a lone sentence wrapped across lines, split across
# blocks or around a comment block is refused, as the regex this replaced refused it.
# skill_counts() parses SKILL.md's body with the pinned CommonMark parser only to tell which lines
# are such a comment, so a "<!--" in code or after a backslash hides nothing. Raw HTML is not
# read: the body may hold it only as those comment blocks, which hide their text, and the build
# refuses any other, inline HTML included, naming the first line of the block, or the table row,
# that holds it. The front matter is not parsed, so the build refuses any "<!--" there, naming
# its line. Without that parser the build refuses too.
visible=$(python3 - "$skill" <<'PY'
import sys
sys.path.insert(0, "tools")
from _verify_sections import SkillHtml, skill_counts
from check_verify_marking import ParserUnavailable
try:
    counts, written = skill_counts(open(sys.argv[1], encoding="utf-8").read())
except ParserUnavailable as exc:
    sys.exit(f"SKILL.md's guide count is checked with the pinned parser: {exc}; refusing to build")
except SkillHtml as exc:
    sys.exit(f"SKILL.md's guide count cannot be checked: {exc}; refusing to build")
# Printed only when every counted copy stands on one line as written, so a copy wrapped across
# lines or blocks fails the comparison below.
print("\n".join(counts) if written == counts else "")
PY
)
[ "$visible" = "$count" ] \
  || { echo "SKILL.md guide count did not update to $count; outside the HTML comment blocks of its body, front matter included, and including in code, titles, destinations and labels, it must state the sentence \"This skill carries N short guides\" exactly once, not reworded or wrapped" >&2; exit 1; }

# A digest per bundled file, so an adopter's updater can verify what it fetched before replacing
# anything, and so a partial or corrupted download is a refusal rather than a silent downgrade.
( cd "$dest" && sha256sum "${files[@]}" ) > "$dest/MANIFEST.sha256"

echo "wrote $dest (${#files[@]} files)"
