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

# A version is three dot-separated runs of the ASCII digits 0123456789, N.N.N, and nothing else.
# The digits are listed one by one, not written as a range, because in a UTF-8 locale a range in
# [[ =~ ]] can also match other digits, such as Arabic-Indic or superscript ones. The installed and
# the published version are both matched against it before either is compared, printed or written,
# and a value that fails is refused without being shown, since it may carry a terminal escape or be
# very long. [[ =~ ]] anchors ^ and $ to the whole value, not to a line, so a second line cannot
# slip past. The installed version is the plugin.json string itself. Of the published VERSION file,
# exactly one trailing line end (one CR LF, or else one LF) is dropped before the match, and
# everything else, any other whitespace included, must match.
version_re='^[0123456789]+(\.[0123456789]+){2}$'

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

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

# The published version is fetched into a file and read as a whole, so that no byte of it is
# dropped or changed before it is checked. The file is created first so that an empty answer always
# leaves a file to read, whether or not curl creates one for a body of no bytes. A failed fetch
# ends the script here (set -e), and the trap removes the work directory.
: > "$work/VERSION"
curl -fsS --max-time 30 -o "$work/VERSION" "$RAW/VERSION"

# bash drops a NUL byte from a $(...) value, so a file holding one is refused before it is read.
size=$(wc -c < "$work/VERSION")
kept=$(tr -d '\0' < "$work/VERSION" | wc -c)
if [ "$size" -ne "$kept" ]; then
  echo "the published version is not of the form N.N.N; refusing to update, nothing changed" >&2
  exit 1
fi

# The x stops $(...) from removing every trailing newline, so that only the one line end below
# is dropped. A lone trailing CR is kept, and fails the match.
latest=$(cat "$work/VERSION"; printf x)
latest=${latest%x}
case $latest in
  *$'\r\n') latest=${latest%$'\r\n'} ;;
  *$'\n') latest=${latest%$'\n'} ;;
esac
case $latest in
  *[![:space:]]*) ;;
  *)
    echo "could not read the published version; nothing changed" >&2
    exit 1 ;;
esac
if ! [[ $latest =~ $version_re ]]; then
  echo "the published version is not of the form N.N.N; refusing to update, nothing changed" >&2
  exit 1
fi

if [ "$latest" = "$current" ]; then
  echo "already at $current; nothing to do"
  exit 0
fi
echo "installed $current, published $latest"

# The publisher's digest list for the new version. Every file below is checked against it, so a
# truncated download or a file that changed in transit is a refusal rather than a bad guide.
curl -fsS --max-time 30 -o "$work/MANIFEST.sha256" \
  "$RAW/plugin/skills/secureconfig/references/MANIFEST.sha256"

count=0
while read -r _digest name; do
  [ -n "$name" ] || continue
  # A manifest entry names a file to write under "$work"; reject anything that is not a bare
  # guide file name, so "../x" or an absolute path cannot escape the temporary directory even
  # if its recorded digest matches. A name may hold only the ASCII letters and digits, listed one
  # by one rather than as ranges so that the set does not depend on the locale, and ".", "_" and
  # "-". Any bad entry refuses the whole update, leaving the bundle untouched.
  case "$name" in
    *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]* | *..* | .*)
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
