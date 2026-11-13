#!/usr/bin/env bash
# Refresh the bundled guides to the latest published release, or report that none is available.
#
# The plugin bundles its guides so that it works with no network at all. That is the whole point
# of bundling, and the cost is that the bundle freezes at the version recorded in plugin.json.
# This script is the other half: run it when you DO have network, on whatever schedule suits you.
#
# It reads the latest published GitHub release, never the moving main branch: it asks the GitHub
# API for that release's tag and then downloads the manifest and the guides from that tag. A
# release is cut only after the release checks pass, and its tag is never moved once published.
#
# It will not leave you worse off than it found you. Everything is fetched and verified into a
# temporary directory first, and the installed bundle is replaced only once every file has matched
# the digest the publisher recorded for it. Any failure before that replacement leaves the working
# bundle untouched. The manifest is read once, as bytes, by one python3 -I program, as a closed
# format: a manifest that is over 65536 bytes or holds a NUL or CR byte, any line that is not exactly
# 64 lowercase hex digits, two spaces and the name of a .md guide, and a repeated name are each a
# failure. The same program then checks each fetched guide's SHA-256, computed with hashlib,
# against the digest from that one read, and refuses a missing or an extra file. No sha256sum runs.
# It never replaces the bundle with an older release than the one installed.
set -euo pipefail

REPO="https://raw.githubusercontent.com/jposluns/secureconfig"
API="https://api.github.com/repos/jposluns/secureconfig/releases/latest"
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
# everything else, any other whitespace included, must match. A release tag is a "v" and then such
# a version, matched the same way before it is used in a URL or compared.
version_re='^[0123456789]+(\.[0123456789]+){2}$'
tag_re='^v[0123456789]+(\.[0123456789]+){2}$'

# Each python3 -I below runs in isolated mode: the current directory and the PYTHON* variables
# stay out of the import path, so a json.py where this is run from is never imported.
plugin_json="$(cd "$here/../.." && pwd)/plugin.json"
current=$(python3 -I -c '
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        version = json.load(fh).get("version")
except (OSError, ValueError, AttributeError, RecursionError, MemoryError):
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

# The latest published release, from the GitHub API. That endpoint never answers with a draft or a
# pre-release, and answers 404 when there is no release, which curl -f turns into a failure. The
# answer is untrusted text: only its tag_name is used, and only after the tag form check below.
# The body is read through a bounded read, and a release object that says it is a draft or a
# pre-release, or lacks those fields, is refused.
: > "$work/release.json"
if ! curl -fsS --max-time 30 -o "$work/release.json" "$API"; then
  echo "could not read the latest published release (none is published, GitHub refused the request, as it does at a rate limit, or it did not answer); nothing changed" >&2
  exit 1
fi
tag=$(python3 -I -c '
import json, sys
try:
    with open(sys.argv[1], "rb") as fh:
        raw = fh.read(1048577)
    data = json.loads(raw) if len(raw) <= 1048576 else None
except (OSError, ValueError, RecursionError, MemoryError):
    data = None
tag = data.get("tag_name") if isinstance(data, dict) else None
ok = (isinstance(tag, str) and tag.isascii() and tag.isprintable()
      and data.get("draft") is False and data.get("prerelease") is False)
print(tag if ok else "")
' "$work/release.json")
if ! [[ $tag =~ $tag_re ]]; then
  echo "the latest release has no tag of the form vN.N.N; refusing to update, nothing changed" >&2
  exit 1
fi
tag_version=${tag#v}

# Numeric comparison of two validated versions, part by part, by length and then text after the
# leading zeros, so that no digit run is ever converted to an integer. Prints lt, eq or gt.
order=$(python3 -I -c '
import sys
def key(version):
    return [(len(part.lstrip("0")), part.lstrip("0")) for part in version.split(".")]
a, b = key(sys.argv[1]), key(sys.argv[2])
print("lt" if a < b else "gt" if a > b else "eq")
' "$tag_version" "$current")
case $order in
  eq)
    echo "already at $current; nothing to do"
    exit 0 ;;
  lt)
    # Never downgrade: a bundle ahead of the latest release, as one taken from main between
    # releases is, is left as it is.
    echo "installed $current is newer than the latest release $tag_version; nothing to do"
    exit 0 ;;
esac

RAW="$REPO/refs/tags/$tag"

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

# A release tag is "v" plus VERSION at the tagged commit, so a VERSION that differs from its tag
# is a mislabelled or damaged release, and nothing is installed from it.
if [ "$latest" != "$tag_version" ]; then
  echo "the VERSION file at the release tag does not match the tag; refusing to update, nothing changed" >&2
  exit 1
fi
echo "installed $current, published $latest"

# The publisher's digest list for the new version. Every guide below is checked against it, so a
# truncated download or a file that changed in transit is a refusal rather than a bad guide.
curl -fsS --max-time 30 -o "$work/MANIFEST.sha256" \
  "$RAW/plugin/skills/secureconfig/references/MANIFEST.sha256"

# The manifest is opened and read once, as bytes, by the one python3 -I program below, which both
# validates it and, after the fetch, checks the fetched guides. bash never parses the manifest and
# no sha256sum runs. The validate step refuses the whole update, with the bundle untouched, if the
# manifest is over 65536 bytes, holds any NUL or CR byte, or has a line that is not exactly 64
# lowercase hex digits (listed one by one, so the set does not depend on the locale), two spaces
# and a name. A name may hold only the ASCII letters and digits, ".", "_" and "-", is at most 100
# characters, must end in ".md", may not be MANIFEST.sha256, contain "..", start with ".", or
# repeat an earlier name; an empty manifest is refused too. A last line with no line end is read
# and validated like any other. A refusal names the line number and never the name. It writes two files from that single read: names, one validated name per line,
# which the loop below reads, and digests, the digest and name of each line, which the verify step
# reads. The verify step lists guides/ and refuses a missing or an extra file, then compares the
# SHA-256 of each file there, computed with hashlib, with the digest from that same read.
manifest_tool='
import hashlib, os, re, stat, sys

MAX_MANIFEST = 65536
LINE = re.compile(rb"([0123456789abcdef]{64})  ([^ ]+)")
NAME = re.compile(rb"[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]{1,100}")


def refuse(why):
    sys.stderr.write(why + "; refusing to update, nothing changed\n")
    sys.exit(1)


def validate(manifest, names_path, digests_path):
    try:
        with open(manifest, "rb") as fh:
            data = fh.read(MAX_MANIFEST + 1)
    except OSError:
        refuse("could not read the manifest")
    if len(data) > MAX_MANIFEST:
        refuse("the manifest is larger than 65536 bytes")
    if b"\0" in data or b"\r" in data:
        refuse("the manifest holds a NUL or CR byte")
    if not data:
        refuse("the manifest lists no guides")
    if data.endswith(b"\n"):
        data = data[:-1]
    seen = set()
    entries = []
    for number, line in enumerate(data.split(b"\n"), 1):
        found = LINE.fullmatch(line)
        if not found:
            refuse("the manifest has a line that is not 64 lowercase hex digits, two spaces and a guide name.md (line %d)" % number)
        digest, name = found.groups()
        if (not NAME.fullmatch(name) or b".." in name or name.startswith(b".")
                or name == b"MANIFEST.sha256"):
            refuse("the manifest lists an unexpected file name (line %d)" % number)
        if not name.endswith(b".md"):
            refuse("the manifest lists a file that is not a .md guide (line %d)" % number)
        if name in seen:
            refuse("the manifest lists a file name twice (line %d)" % number)
        seen.add(name)
        entries.append((digest.decode("ascii"), name.decode("ascii")))
    with open(names_path, "w", encoding="ascii") as fh:
        for digest, name in entries:
            fh.write(name + "\n")
    with open(digests_path, "w", encoding="ascii") as fh:
        for digest, name in entries:
            fh.write(digest + "  " + name + "\n")


def verify(guides, digests_path):
    with open(digests_path, encoding="ascii") as fh:
        entries = [line.rstrip("\n").split("  ") for line in fh]
    if sorted(os.listdir(guides)) != sorted(name for digest, name in entries):
        refuse("a guide is missing, or a file that the manifest does not list was fetched")
    for digest, name in entries:
        path = os.path.join(guides, name)
        try:
            if not stat.S_ISREG(os.lstat(path).st_mode):
                refuse("a fetched guide is not a regular file")
            with open(path, "rb") as fh:
                body = fh.read()
        except OSError:
            refuse("a fetched guide could not be read")
        if hashlib.sha256(body).hexdigest() != digest:
            refuse("a fetched guide did not match its published digest")


if sys.argv[1] == "validate":
    validate(sys.argv[2], sys.argv[3], sys.argv[4])
else:
    verify(sys.argv[2], sys.argv[3])
'
python3 -I -c "$manifest_tool" validate "$work/MANIFEST.sha256" "$work/names" "$work/digests"

# The guides are fetched into "$work/guides", a folder apart from the manifest. The names come from
# the validated list, one per line, and hold only the characters above, so none can be a path.
mkdir "$work/guides"
count=0
while IFS= read -r name; do
  curl -fsS --max-time 60 -o "$work/guides/$name" "$RAW/$name"
  count=$((count + 1))
done < "$work/names"

python3 -I -c "$manifest_tool" verify "$work/guides" "$work/digests"

rm -rf "$refs.new"
mkdir -p "$refs.new"
cp "$work/guides"/*.md "$work/MANIFEST.sha256" "$refs.new/"
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
