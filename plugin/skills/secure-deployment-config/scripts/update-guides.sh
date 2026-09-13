#!/usr/bin/env bash
# Refresh the bundled guides to the latest published version, or report that none is available.
#
# The plugin bundles its guides so that it works with no network at all. That is the whole point
# of bundling, and the cost is that the bundle freezes at the version recorded in plugin.json.
# This script is the other half: run it when you DO have network, on whatever schedule suits you.
#
# It will not leave you worse off than it found you. Everything is fetched and verified into a
# temporary directory first, and the installed bundle is replaced only once every file has matched
# the digest the publisher recorded for it. Any failure leaves the working bundle untouched.
set -euo pipefail

RAW="https://raw.githubusercontent.com/jposluns/secureconfig/main"
here="$(cd "$(dirname "$0")/.." && pwd)"
refs="$here/references"

plugin_json="$(cd "$here/../.." && pwd)/plugin.json"
current=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("version","0"))' \
  "$plugin_json")

latest=$(curl -fsS --max-time 30 "$RAW/VERSION" | tr -d '[:space:]')
if [ -z "$latest" ]; then
  echo "could not read the published version; nothing changed" >&2
  exit 1
fi

if [ "$latest" = "$current" ]; then
  echo "already at $current; nothing to do"
  exit 0
fi
echo "installed $current, published $latest"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# The publisher's digest list for the new version. Every file below is checked against it, so a
# truncated download or a file that changed in transit is a refusal rather than a bad guide.
curl -fsS --max-time 30 -o "$work/MANIFEST.sha256" \
  "$RAW/plugin/skills/secure-deployment-config/references/MANIFEST.sha256"

count=0
while read -r _digest name; do
  [ -n "$name" ] || continue
  curl -fsS --max-time 60 -o "$work/$name" "$RAW/$name"
  count=$((count + 1))
done < "$work/MANIFEST.sha256"

( cd "$work" && sha256sum --quiet --check MANIFEST.sha256 ) || {
  echo "a fetched guide did not match its published digest; nothing changed" >&2
  exit 1
}

cp "$work/MANIFEST.sha256" "$work/.verified"
rm -rf "$refs.new"
mkdir -p "$refs.new"
cp "$work"/*.md "$work/MANIFEST.sha256" "$refs.new/"
rm -rf "$refs"
mv "$refs.new" "$refs"

python3 - "$plugin_json" "$latest" <<'PY'
import json, sys
path, version = sys.argv[1], sys.argv[2]
with open(path) as fh:
    data = json.load(fh)
data["version"] = version
with open(path, "w") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
PY

echo "updated $count guides and re-pinned to $latest"
