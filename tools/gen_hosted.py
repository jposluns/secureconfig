#!/usr/bin/env python3
"""Generate the hosted plugin catalog and the redirect file from the release record.

WHY: the hosted install route serves a catalog, site/marketplace.json, whose one entry points at
the current plugin archive with its SHA-256, and two stable latest links,
/downloads/secureconfig-latest.zip and /downloads/secureconfig-plugin-latest.zip, each a 302
redirect, never a 301, to the current versioned archive. Both files are generated here and never
typed: the digest and the version come from the release record, so a typo cannot point an
install at the wrong bytes. tools/check_hosted.py holds the committed files to this module's
output, and tools/check_draft.py holds site/_redirects to the shapes this module writes.

THE RELEASE RECORD is releases/SHA256SUMS, one cumulative file that gains each release's lines,
newest release first: the records pull request (CONTRIBUTING.md "Releasing" step 9) prepends a
byte copy of the lines of that release's `SHA256SUMS` asset. Each line is `<64 hex>  <name>` as
sha256sum writes it, and one release's lines are that asset's four, in the asset's order
(tools/check_release.py names()): `llms-full.txt`, the skill zip secureconfig-1.0.<N>.zip, the
plugin zip secureconfig-plugin-1.0.<N>.zip, then `RELEASE-NOTES-v1.0.<N>.md`, all of one
version, so a block's release is the version its zip and notes names carry. Only the zip lines
feed the hosted files: an `llms-full.txt` or notes line is recorded but never staged or served
from here. The digest on such a line is checked against nothing: the tree keeps neither file at
the release's bytes, so a wrong digest there, all zeros included, passes. The file is read as
bytes, so a CRLF or lone-CR rewrite is refused, never read as LF. No line names a `-latest`
file: a latest link is a 302 redirect with no bytes of its own.
Any other name, order or line count in a block, a repeated release block, an older release
above a newer one, and anything else under releases/ are refused (HostedError), so a merged,
trimmed or reordered record cannot pass as a byte copy of the assets.

site/marketplace.json names the catalog `secureconfig`, this project's own catalog under its own
name, and lists one plugin whose source is the archive form
`{"source": "archive", "url": "https://secureconfig.ai/downloads/<plugin zip>", "sha256": ...}`
for the newest record. Its name, description and owner come from entry_fields(), which reads
plugin/plugin.json; if those fields ever move, only that function changes.

site/_redirects is written whole, so the whole file is generated and drift-checked: the fixed
HEADER line, then the rule of each entry of tools/redirects_allowlist.txt (the part before the
tab, in file order), then, only when a record exists, the two latest lines, in this order:

    /downloads/secureconfig-latest.zip /downloads/secureconfig-1.0.<N>.zip 302
    /downloads/secureconfig-plugin-latest.zip /downloads/secureconfig-plugin-1.0.<N>.zip 302

An allowlist entry line is `SOURCE TARGET 302<TAB>REASON` with single spaces, printable ASCII
fields (`!` to `~`), a source no other entry carries and a non-empty reason.
tools/check_draft.py reads each entry's source and target in a percent-decoded normal form,
refuses one that does not normalize cleanly, and refuses any `/draft` entry, while
tools/check_hosted.py holds each release-asset entry to the record: a recorded zip that is no
longer staged. With no record and no allowlist entry there is nothing to serve, so neither
file is written. This generator deletes nothing: a stale committed file is a finding for
tools/check_hosted.py, never something quietly removed here.

Exit 0 with each written path printed (or a note that there is nothing to write), 1 when the
record, the allowlist or plugin/plugin.json cannot be used (HostedError), 2 on a read error,
a plugin/plugin.json that cannot be parsed as JSON included.
Usage: python3 -I -B tools/gen_hosted.py [--root <repository root>]
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _archives import ARCHIVES, archive_name  # noqa: E402  (the release's archive kinds)

SITE_ORIGIN = "https://secureconfig.ai"
DOWNLOADS = "downloads"
RECORDS = Path("releases")
RECORD_NAME = "SHA256SUMS"
RECORD_LINE = re.compile(r"([0-9a-f]{64})  (\S+)")
# A record line's name must be some release's archive name; the 1.0.<N> in the name says which
# release the line belongs to. Built from ARCHIVES, so a new kind cannot drift from this list.
NAME_VERSIONS = tuple(re.compile(re.escape(kind.template)
                                 .replace(re.escape("{version}"), r"(1\.0\.[1-9][0-9]*)"))
                      for kind in ARCHIVES)
# The other two names a release's SHA256SUMS asset lists: the committed corpus and the notes.
# With the zips they are the asset's four lines, in this order (tools/check_release.py names()).
LLMS_NAME = "llms-full.txt"
NOTES_TEMPLATE = "RELEASE-NOTES-v{version}.md"
LATEST_SUFFIX = "-latest.zip"
MARKETPLACE = Path("site") / "marketplace.json"
REDIRECTS = Path("site") / "_redirects"
ALLOWLIST = Path("tools") / "redirects_allowlist.txt"
# The rule part of an allowlist entry: three single-space-separated fields ending in the
# literal 302, the first two printable ASCII (`!` to `~`), so no control or invisible character
# rides into site/_redirects. tools/check_draft.py applies the full shape and target rules;
# this module refuses only that shape, and a source a second entry repeats.
ENTRY = re.compile(r"[!-~]+ [!-~]+ 302")
# The one line a hand edit cannot carry unnoticed: tools/check_draft.py requires it first, and
# tools/test_hosted.py holds the two copies of this constant to each other.
HEADER = ("# Generated by tools/gen_hosted.py from releases/ and tools/redirects_allowlist.txt;"
          " do not edit by hand.")
# The plugin zip's kind: the one whose root file is the plugin manifest.
PLUGIN_KIND = next(kind for kind in ARCHIVES if kind.root_file == "plugin.json")
# The most brackets a document json_object reads may hold open at once, counted outside JSON
# strings. json.loads recurses once per level, and whether a deep parse raises RecursionError
# depends on the interpreter build and its stack, so json_object refuses a deeper document
# before parsing it, unless a closing bracket with no open bracket to close comes first, and
# json.loads then fails no deeper than that bracket, so the answer is the same on every Python.
# The documents it reads, the plugin manifests and site-src/content.json, nest only a few levels.
MAX_JSON_DEPTH = 100
# One JSON string (its escapes, and an unterminated string running to the end of the text less a
# last backslash that has no character after it, included) or one bracket, so
# nested_deeper_than skips every bracket inside a string.
JSON_STRING_OR_BRACKET = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"?|[\[\]{}]', re.S)


class HostedError(ValueError):
    """The records, the allowlist or plugin/plugin.json cannot be used; the message says why."""


def name_version(name):
    """The 1.0.<N> a release archive name carries, or None when no kind's name matches."""
    for pattern in NAME_VERSIONS:
        matched = pattern.fullmatch(name)
        if matched:
            return matched.group(1)
    return None


def asset_names(version):
    """The four names of one release's SHA256SUMS asset, in the asset's order: llms-full.txt,
    each zip ARCHIVES lists, then the notes (tools/check_release.py names(), without the asset
    itself, which lists the other four and so never lists its own name)."""
    return (LLMS_NAME, *(archive_name(kind, version) for kind in ARCHIVES),
            NOTES_TEMPLATE.format(version=version))


def read_records(root):
    """{version: {zip name: sha256}} for each release in the cumulative record
    releases/SHA256SUMS, newest release first, or {} when the folder or the file is absent.
    The record is a byte copy of each release's `SHA256SUMS` asset: four lines per release, in
    the asset's order (asset_names()), each ending in LF alone. Only the zip lines are
    returned, since only a zip is hosted. HostedError when the record cannot be used or
    anything else sits under releases/."""
    folder = root / RECORDS
    if not folder.is_dir():
        return {}
    # A file name and a record line's name are untrusted text, so each is printed escaped
    # (ascii()) unless a pattern has already limited it to safe characters, and an expected
    # name built by asset_names() is printed raw: no character in a printed name can end the
    # FAIL line, forge another or fail to encode.
    for entry in sorted(folder.iterdir()):
        if entry.name != RECORD_NAME or not entry.is_file():
            raise HostedError(f"{str(RECORDS / entry.name)!a} is not the cumulative release "
                              f"record {RECORDS}/{RECORD_NAME}, the only entry kept there")
    path = folder / RECORD_NAME
    if not path.is_file():
        return {}
    # Read as bytes: the asset's lines end in LF alone, so a CRLF or lone-CR rewrite is a
    # refusal here, not something a text-mode read would fold back onto LF.
    raw = path.read_bytes()
    if b"\r" in raw:
        n = raw[:raw.index(b"\r")].count(b"\n") + 1
        raise HostedError(f"{RECORDS}/{RECORD_NAME}:{n} holds a carriage return; the record is "
                          f"a byte copy of each release's SHA256SUMS asset, whose lines end in "
                          f"LF alone, so a CRLF or lone-CR rewrite is refused")
    text = raw.decode("utf-8")
    if not text.endswith("\n"):
        raise HostedError(f"{RECORDS}/{RECORD_NAME} does not end with a newline")
    entries = []
    for n, line in enumerate(text.split("\n")[:-1], 1):
        matched = RECORD_LINE.fullmatch(line)
        where = f"{RECORDS}/{RECORD_NAME}:{n}"
        if not matched:
            raise HostedError(f"{where} is not `<64 hex>  <name>` as sha256sum writes it")
        digest, name = matched.group(1), matched.group(2)
        if name.lower().endswith(LATEST_SUFFIX):
            raise HostedError(f"{where} names {name!a}; a latest link is a 302 redirect with "
                              f"no bytes of its own, so no record lists one")
        entries.append((where, digest, name))
    if len(entries) % 4:
        raise HostedError(f"{RECORDS}/{RECORD_NAME} holds {len(entries)} lines, which is not a "
                          f"multiple of four; each release's SHA256SUMS asset holds four lines, "
                          f"prepended whole")
    records = {}
    last = None
    for start in range(0, len(entries), 4):
        block = entries[start:start + 4]
        where, _, name = block[1]
        version = name_version(name)
        if version is None:
            raise HostedError(f"{where} names {name!a}, which is no release archive's name; the "
                              f"second line of a release's block is its skill zip, whose "
                              f"1.0.<N> says which release the block records")
        if version in records:
            raise HostedError(f"{block[0][0]} opens a second v{version} block; the cumulative "
                              f"record holds each release's lines once, together")
        if last is not None and int(version.rsplit(".", 1)[1]) > int(last.rsplit(".", 1)[1]):
            raise HostedError(f"{block[0][0]} puts v{version} after v{last}; the cumulative "
                              f"record holds the newest release first")
        for (where, _, name), want in zip(block, asset_names(version)):
            if name != want:
                raise HostedError(f"{where} names {name!a}, not {want}; a release's block is a "
                                  f"byte copy of the four lines of its SHA256SUMS asset, in the "
                                  f"asset's order")
        records[version] = {name: digest for _, digest, name in block[1:3]}
        last = version
    return records


def newest(records):
    """The newest recorded version, by <N>."""
    return max(records, key=lambda version: int(version.rsplit(".", 1)[1]))


def nested_deeper_than(text, limit):
    """Whether text opens more than limit brackets (`[` or `{`) at once, counted outside JSON
    strings up to the first closing bracket (`]` or `}`) with no open bracket to close: a
    string's brackets do not nest, an escaped quote does not end it, and json.loads refuses any
    text holding such a closing bracket, so the count stops there."""
    depth = 0
    for match in JSON_STRING_OR_BRACKET.finditer(text):
        token = match.group()
        if token in ("[", "{"):
            depth += 1
            if depth > limit:
                return True
        elif token in ("]", "}"):
            if not depth:
                return False
            depth -= 1
    return False


def json_object(text, where):
    """The JSON object that text, read from where, holds. ValueError when text cannot be parsed
    as JSON: json.JSONDecodeError for text that is not JSON, the plain ValueError json.loads
    raises for an integer with more digits than the interpreter's integer string conversion
    limit allows (4300 by default where there is one), and a ValueError for text nested too
    deeply to parse. HostedError, itself a ValueError, when it parses to anything but an object,
    so a caller that catches ValueError meets no other exception from bad input. Nested too
    deeply to parse means more than MAX_JSON_DEPTH brackets open at once outside strings, as
    nested_deeper_than counts them, refused before parsing, or a parse that raises
    RecursionError."""
    if nested_deeper_than(text, MAX_JSON_DEPTH):
        raise ValueError(f"{where} is nested too deeply to parse as JSON")
    try:
        value = json.loads(text)
    except RecursionError:
        # A backstop only: below MAX_JSON_DEPTH no parse is expected to reach the interpreter's
        # recursion limit, but one that does is the same read error.
        raise ValueError(f"{where} is nested too deeply to parse as JSON") from None
    if not isinstance(value, dict):
        raise HostedError(f"{where} is not a JSON object")
    return value


def entry_fields(root):
    """The catalog's name, description and owner, read from plugin/plugin.json. If these fields
    ever move, only this function changes."""
    text = (root / "plugin" / "plugin.json").read_text(encoding="utf-8")
    manifest = json_object(text, "plugin/plugin.json")
    fields = {"name": manifest.get("name"), "description": manifest.get("description"),
              "author": manifest.get("author")}
    if (not all(isinstance(value, str) and value for value in
                (fields["name"], fields["description"]))
            or not isinstance(fields["author"], dict)
            or not all(isinstance(fields["author"].get(key), str) and fields["author"].get(key)
                       for key in ("name", "url"))):
        raise HostedError("plugin/plugin.json needs non-empty string name and description fields "
                          "and an author object with non-empty string name and url fields")
    return {"name": fields["name"], "description": fields["description"],
            "owner": {"name": fields["author"]["name"], "url": fields["author"]["url"]}}


def marketplace_text(root, records):
    """site/marketplace.json for the newest record: one entry, the archive source, the url and
    sha256 copied from that record."""
    version = newest(records)
    name = archive_name(PLUGIN_KIND, version)
    fields = entry_fields(root)
    catalog = {
        "name": fields["name"],
        "owner": fields["owner"],
        "plugins": [{
            "name": fields["name"],
            "description": fields["description"],
            "source": {"source": "archive",
                       "url": f"{SITE_ORIGIN}/{DOWNLOADS}/{name}",
                       "sha256": records[version][name]},
        }],
    }
    return json.dumps(catalog, indent=2) + "\n"


def read_allowlist(root):
    """The rule of each entry of tools/redirects_allowlist.txt (the part before the tab), in file
    order, or [] when the file is absent; HostedError for a line that could not be an entry, or
    for a source a second entry repeats."""
    path = root / ALLOWLIST
    if not path.is_file():
        return []
    rules, sources = [], {}
    for n, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        rule, sep, reason = line.partition("\t")
        if not sep or not reason or reason != reason.strip() or not ENTRY.fullmatch(rule):
            raise HostedError(f"{ALLOWLIST}:{n} is not `SOURCE TARGET 302<TAB>REASON` with "
                              f"single spaces, printable ASCII fields and a non-empty reason")
        source = rule.split(" ", 1)[0]
        first = sources.setdefault(source, n)
        if first != n:
            raise HostedError(f"{ALLOWLIST}:{n} repeats the source {source} of line {first}; a "
                              f"host applies the first rule whose source matches, so no two "
                              f"entries share a source")
        rules.append(rule)
    return rules


def latest_lines(version):
    """The two latest lines for one version, the skill link then the plugin link, each 302."""
    return [f"/{DOWNLOADS}/{kind.template.format(version='latest')} "
            f"/{DOWNLOADS}/{archive_name(kind, version)} 302" for kind in ARCHIVES]


def redirects_text(root, records):
    """The whole site/_redirects: HEADER, the allowlist rules, then, when a record exists, the
    two latest lines; None when there is nothing to serve."""
    lines = [HEADER, *read_allowlist(root)]
    if records:
        lines += latest_lines(newest(records))
    if lines == [HEADER]:
        return None
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    try:
        records = read_records(args.root)
        redirects = redirects_text(args.root, records)
        wrote = []
        if records:
            (args.root / MARKETPLACE).parent.mkdir(parents=True, exist_ok=True)
            (args.root / MARKETPLACE).write_text(marketplace_text(args.root, records),
                                                 encoding="utf-8")
            wrote.append(str(MARKETPLACE))
        if redirects is not None:
            (args.root / REDIRECTS).parent.mkdir(parents=True, exist_ok=True)
            (args.root / REDIRECTS).write_text(redirects, encoding="utf-8")
            wrote.append(str(REDIRECTS))
    except HostedError as exc:
        print(f"  FAIL  {exc}")
        return 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"  FAIL  cannot read the record, the allowlist or the manifest: {exc}")
        return 2
    if wrote:
        print(f"  ok    wrote {' and '.join(wrote)} from {len(records)} recorded release(s)")
    else:
        print("  ok    no recorded release and no allowlist entry, so there is nothing to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
