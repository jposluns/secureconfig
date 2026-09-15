#!/usr/bin/env bash
# Build the Agent Plugin's bundled references from the guides.
#
# The plugin ships every guide inside itself rather than pointing at raw URLs, so an assistant
# with no network still has them. That freezes the content at the version in plugin.json, which
# is why each guide keeps its own "Sources (checked <month year>)" section and why SKILL.md tells
# the reader to check a default against the vendor page when it matters to the decision.
#
# The file list is NOT maintained here. It is whatever scripts/build-llms-full.sh reports under
# --list-inputs, so "what counts as a guide" has one definition and the two bundles cannot drift.
set -euo pipefail

cd "$(dirname "$0")/.."
dest="plugin/skills/secure-deployment-config/references"

mapfile -t files < <(bash scripts/build-llms-full.sh --list-inputs)
if [ "${#files[@]}" -eq 0 ]; then
  echo "build-llms-full.sh --list-inputs reported nothing" >&2
  exit 1
fi

if [ "${1:-}" = "--list-inputs" ]; then
  # The guide list, the script it came from, and VERSION: changing build-llms-full.sh changes what
  # this bundle contains, and VERSION sets plugin.json's version below, so all three are inputs to
  # this build and the generated-file record has to say so.
  printf '%s\n' "${files[@]}" scripts/build-llms-full.sh VERSION
  exit 0
fi

rm -rf "$dest"
mkdir -p "$dest"
for f in "${files[@]}"; do
  cp "$f" "$dest/$f"
done

# Keep the plugin manifest's version in lockstep with the repository VERSION (1.0.<pull request
# number>), so an adopter's updater can tell a refreshed bundle from an earlier one and never has to
# read stale configuration behind a version that says it is current. The whole-corpus staleness gate
# re-runs this build and diffs its output, so a plugin.json whose version has drifted from VERSION is
# caught as a stale bundle; there is no separate version gate to keep in step.
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

# A digest per bundled file, so an adopter's updater can verify what it fetched before replacing
# anything, and so a partial or corrupted download is a refusal rather than a silent downgrade.
( cd "$dest" && sha256sum "${files[@]}" ) > "$dest/MANIFEST.sha256"

echo "wrote $dest (${#files[@]} files)"
