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
# The count is confirmed only in the text a reader sees, by skill_counts() in
# tools/_verify_sections.py, which tools/check_generated_committed.py also calls, and the sentence
# must appear there exactly once, so a commented copy can neither stand in for a missing visible
# sentence nor sit beside a second one. skill_counts() parses SKILL.md's body with the pinned
# CommonMark parser, so the parser, not a hand-written scan, decides what is Markdown code, and a
# "<!--" in code or after a backslash hides nothing. Raw HTML is not read: SKILL.md may hold it
# only as whole HTML comments, which hide their text, and the build refuses any other. Without
# that parser the build refuses too.
visible=$(python3 - "$skill" <<'PY'
import sys
sys.path.insert(0, "tools")
from _verify_sections import SkillHtml, skill_counts
from check_verify_marking import ParserUnavailable
try:
    counts = skill_counts(open(sys.argv[1], encoding="utf-8").read())
except ParserUnavailable as exc:
    sys.exit(f"SKILL.md's guide count is checked with the pinned parser: {exc}; refusing to build")
except SkillHtml as exc:
    sys.exit(f"SKILL.md's guide count cannot be checked: {exc}; refusing to build")
print("\n".join(counts))
PY
)
[ "$visible" = "$count" ] \
  || { echo "SKILL.md guide count did not update to $count; outside HTML comments it must state the sentence \"This skill carries N short guides\" exactly once, not reworded or wrapped" >&2; exit 1; }

# A digest per bundled file, so an adopter's updater can verify what it fetched before replacing
# anything, and so a partial or corrupted download is a refusal rather than a silent downgrade.
( cd "$dest" && sha256sum "${files[@]}" ) > "$dest/MANIFEST.sha256"

echo "wrote $dest (${#files[@]} files)"
