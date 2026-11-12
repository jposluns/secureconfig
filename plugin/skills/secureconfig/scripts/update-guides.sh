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

# A version is three dot-separated runs of decimal digits, N.N.N, and nothing else. The installed
# and the published version are both matched against it before either is compared, printed or
# written, and a value that fails is refused without being shown, since it may carry a terminal
# escape or be very long. [[ =~ ]] anchors to the whole value, so a second line cannot slip past.
version_re='^[0-9]+(\.[0-9]+){2}$'

# Each python3 -I below runs in isolated mode: the current directory and the PYTHON* variables
# stay out of the import path, so a json.py where this is run from is never imported.
plugin_json="$(cd "$here/../.." && pwd)/plugin.json"
current=$(python3 -I -c '
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        version = json.load(fh).get("version")
except (OSError, ValueError, AttributeError):
    version = None
ok = isinstance(version, str) and version.isascii() and version.isprintable()
print(version if ok else "")
' "$plugin_json")
if ! [[ $current =~ $version_re ]]; then
  echo "plugin.json records no version of the form N.N.N; refusing to update, nothing changed" >&2
  exit 1
fi

latest=$(curl -fsS --max-time 30 "$RAW/VERSION" | tr -d '[:space:]')
if [ -z "$latest" ]; then
  echo "could not read the published version; nothing changed" >&2
  exit 1
fi
if ! [[ $latest =~ $version_re ]]; then
  echo "the published version is not of the form N.N.N; refusing to update, nothing changed" >&2
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
  "$RAW/plugin/skills/secureconfig/references/MANIFEST.sha256"

count=0
while read -r _digest name; do
  [ -n "$name" ] || continue
  # A manifest entry names a file to write under "$work"; reject anything that is not a bare
  # guide file name, so "../x" or an absolute path cannot escape the temporary directory even
  # if its recorded digest matches. Any bad entry refuses the whole update, leaving the bundle
  # untouched.
  case "$name" in
    *[!A-Za-z0-9._-]* | *..* | .*)
      echo "the manifest lists an unexpected file name ($name); refusing to update" >&2
      exit 1 ;;
  esac
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

python3 -I - "$plugin_json" "$latest" <<'PY'
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
