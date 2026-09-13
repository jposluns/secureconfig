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
  # The guide list AND the script it came from: changing build-llms-full.sh changes what this
  # bundle contains, so it is an input to this build and the generated-file record has to say so.
  printf '%s\n' "${files[@]}" scripts/build-llms-full.sh
  exit 0
fi

rm -rf "$dest"
mkdir -p "$dest"
for f in "${files[@]}"; do
  cp "$f" "$dest/$f"
done

# A digest per bundled file, so an adopter's updater can verify what it fetched before replacing
# anything, and so a partial or corrupted download is a refusal rather than a silent downgrade.
( cd "$dest" && sha256sum "${files[@]}" ) > "$dest/MANIFEST.sha256"

echo "wrote $dest (${#files[@]} files)"
