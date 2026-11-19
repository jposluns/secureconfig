#!/usr/bin/env python3
"""Cases for tools/gen_hosted.py and tools/check_hosted.py, the hosted install surface.

Each case builds a throwaway root under TMPDIR, with a plugin/plugin.json, the cumulative
release record releases/SHA256SUMS (the four asset lines of each release together, newest
release first, as the release's SHA256SUMS asset lists them), staged
archives under site/downloads/ and, in most cases, the generated site/marketplace.json and
site/_redirects, then runs the generator or the gate on it by path, so nothing touches this
checkout. The accepted roots are a root with no record, no zip and no generated file (what
`main` is before the first hosted release), a generated root with one recorded release, and the
generator run twice, whose outputs are byte-equal. Two more are accepted: a generated root with
two releases in one record, newest first and both staged, and a generated root whose aged-out
release's zips are redirected to their own release assets by allowlist entries. The refusals
cover each half of the gate. The drift half: a generated file with no recorded release behind it (the catalog and a
latest link), a missing generated file with a record behind it, an edited catalog digest, a
latest link edited to 301, and an extra redirect appended. Both generated files are compared
as bytes, so the cases also rewrite each file with CRLF line endings and put a lone CR in
place of the header's LF and between the two latest links. The record half: a staged zip whose
bytes differ from its record, a missing staged archive for the newest release, a newest release
not staged at all even though redirected, an aged-out zip with no redirect, a recorded zip
staged as a symbolic link to identical bytes outside site/, and a staged file in
site/downloads/ that no record names, beside recorded zips and with no record. The record's own
shape: a record naming a -latest file, a block whose plugin zip line names the skill zip again,
a block opening with the skill zip rather than llms-full.txt, a record holding only a block's
first two lines, a corrupted record line, a record without a trailing newline, a CRLF rewrite
of the record and a lone CR in it (the record is read as bytes), a skill zip line carrying no
release archive's name, a release's block repeated after another release's (a duplicate
version), an out-of-order record with the older release first, and a stray entry under
releases/. One case (check_step9) copies a release's SHA256SUMS asset byte for byte, written as
tools/check_release.py writes it with llms-full.txt, the two zips and the notes, and runs
gen_hosted.py, check_hosted.py and scripts/build-site.py --check on that root, each passing:
the documented records procedure of CONTRIBUTING.md Releasing step 9. The allowlist half: an asset redirect naming a
zip no record names, an asset redirect for a recorded zip that is still staged, an allowlist
entry without a reason, an entry whose source a second entry repeats, and an entry with a raw
U+FEFF in its source. The rest: a plugin zip whose root plugin.json version differs from its
record, and, with a record behind it, an unparsable plugin/plugin.json (a read error, exit 2),
one nested too deeply to parse (a read error, exit 2, for the gate and the generator alike) and
one that is a JSON array. The newest record's staged plugin zip is a finding (exit 1) in 1 FAIL
line, never a traceback, when its root plugin.json is nested too deeply to parse, is a JSON
array, is UTF-16 rather than UTF-8 or opens with a UTF-8 byte order mark, and when the zip's
deflated data is damaged or names a compression method zipfile does not support. A staged plugin
zip one byte over scripts/build-site.py's DOWNLOAD_MAX, a zip bomb whose root plugin.json
declares 32 MiB uncompressed and a bzip2 zip bomb whose root plugin.json declares 16 bytes are
each exit 1 in 1 FAIL line, and a staged plugin zip whose root plugin.json is exactly
MANIFEST_MAX bytes long passes. A staged plugin zip of DOWNLOAD_MAX bytes whose central
directory fills it and a valid plugin zip whose central directory is one byte over CENTRAL_MAX
are each exit 1 in 1 FAIL line saying that the zip is not opened, and a valid plugin zip whose
central directory is exactly CENTRAL_MAX bytes passes. A valid plugin zip whose zip64 end record
declares a central directory one byte over CENTRAL_MAX while its end record declares 46 bytes is
exit 1 in 1 FAIL line saying that the zip is not opened too. The newest staged plugin zip's root
plugin.json version is printed escaped, so one that is a lone surrogate and one that carries a
newline and a forged ok line are each exit 1 in exactly 1 FAIL line, with no traceback and no
forged line. One in-process case holds check_draft.REDIRECTS_HEADER to gen_hosted.HEADER, so the
gate and the generator cannot drift apart on the file's first line. In-process cases hold
gen_hosted.json_object to its depth limit, MAX_JSON_DEPTH: an object nested exactly that deep is
read, one a level deeper and one whose deep nesting sits inside one value are nested too deeply to
parse, and a string holding 300000 brackets, an escaped quote and an escaped backslash is read.
One unmatched closing bracket followed by 150 opening ones is refused by json.loads at the first
character, where the depth count stops, and an object holding a 5000-digit integer is a ValueError
(the interpreter's 4300-digit integer limit), never a HostedError.

Nothing here reads git history or the network. Exit 0 ok, 1 on a finding.
"""
import hashlib
import io
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import check_draft  # noqa: E402
import check_hosted  # noqa: E402  (its caps, DOWNLOAD_MAX, MANIFEST_MAX and CENTRAL_MAX)
import gen_hosted  # noqa: E402

MANIFEST = {"name": "secureconfig", "version": "1.0.7", "description": "guides",
            "author": {"name": "Jeff Posluns", "url": "https://secureconfig.ai"}}
ASSET = ("/downloads/secureconfig-{0}.zip https://github.com/jposluns/secureconfig/releases/"
         "download/v{0}/secureconfig-{0}.zip 302\taged out\n"
         "/downloads/secureconfig-plugin-{0}.zip https://github.com/jposluns/secureconfig/"
         "releases/download/v{0}/secureconfig-plugin-{0}.zip 302\taged out\n")
# Valid JSON nested far past gen_hosted.MAX_JSON_DEPTH, which json_object refuses before parsing,
# whether or not json.loads could parse it on this interpreter.
NESTED = "[" * 100000 + "]" * 100000 + "\n"
# Valid JSON nested 10 times deeper than gen_hosted.MAX_JSON_DEPTH that fits a staged plugin zip's
# root plugin.json, which check_hosted.MANIFEST_MAX caps (NESTED, at 200001 bytes, does not).
NESTED_MEMBER = ("[" * 1000 + "]" * 1000 + "\n").encode()


def plugin_zip(version, manifest=None, compression=zipfile.ZIP_STORED):
    """A minimal plugin zip: a plugin.json at its root carrying version, or the manifest bytes
    given instead."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=compression) as archive:
        archive.writestr("plugin.json", json.dumps({"version": version}) if manifest is None
                         else manifest)
    return out.getvalue()


def damaged_zip():
    """A plugin zip whose deflated plugin.json data opens with deflate's reserved block type, so
    reading the member raises zlib.error, which zipfile does not wrap."""
    data = bytearray(plugin_zip("1.0.7", compression=zipfile.ZIP_DEFLATED))
    # The data follows the local header: 30 fixed bytes, the name and the extra field.
    start = 30 + int.from_bytes(data[26:28], "little") + int.from_bytes(data[28:30], "little")
    data[start] = 0xFF
    return bytes(data)


def unsupported_zip():
    """A plugin zip whose plugin.json names compression method 99 in both headers, which zipfile
    refuses with NotImplementedError."""
    data = bytearray(plugin_zip("1.0.7"))
    central = data.find(b"PK\x01\x02")
    data[8:10] = data[central + 10:central + 12] = (99).to_bytes(2, "little")
    return bytes(data)


def lying_bzip2_zip(size, declared):
    """A zip bomb: a plugin zip whose root plugin.json is size bytes of "[" compressed with
    bzip2 (48 bytes of compressed data for 8 MiB), with both headers declaring only declared
    bytes uncompressed, so the declared size alone cannot reveal it."""
    data = bytearray(plugin_zip("1.0.7", b"[" * size, compression=zipfile.ZIP_BZIP2))
    central = data.find(b"PK\x01\x02")
    # The uncompressed size is at offset 22 of the local header and 24 of the central one.
    data[22:26] = data[central + 24:central + 28] = declared.to_bytes(4, "little")
    return bytes(data)


def full_directory_zip(size):
    """A file of size bytes that is all central directory, as zipfile reads it: the zero bytes
    left over, then as many 46-byte central directory records as fit, each with an empty name,
    no data and no local header, then a 22-byte end record declaring their total size."""
    count, pad = divmod(size - 22, 46)
    record = struct.pack("<4s4B4HL2L5H2L", b"PK\x01\x02", 20, 0, 20, 0, 0, 0, 0, 33,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    end = struct.pack("<4s4H2LH", b"PK\x05\x06", 0, 0, min(count, 0xFFFF), min(count, 0xFFFF),
                      46 * count, pad, 0)
    return b"\0" * pad + record * count + end


def wide_directory_zip(size):
    """A plugin zip carrying version 1.0.7 whose central directory is exactly size bytes: its
    root plugin.json, then empty members named pad/<n> whose central directory comments, of at
    most 65535 bytes each, fill the rest."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("plugin.json", json.dumps({"version": "1.0.7"}))
        left = size - 46 - len("plugin.json")
        number = 0
        while left:
            info = zipfile.ZipInfo(f"pad/{number:04d}")
            room = left - 46 - len(info.filename)
            # Leave nothing, or room for at least one more record with an empty comment.
            info.comment = b"c" * (room if room <= 65535 else min(65535, room - 54))
            archive.writestr(info, b"")
            left -= 46 + len(info.filename) + len(info.comment)
            number += 1
    data = out.getvalue()
    # The end record, with no archive comment, is the last 22 bytes, its directory size at 12.
    if int.from_bytes(data[-10:-6], "little") != size:
        raise AssertionError(f"wide_directory_zip({size}) built another directory size")
    return data


def zip64_directory_zip(size, declared):
    """wide_directory_zip(size) with a zip64 end record, declaring its central directory of
    exactly size bytes, and that record's locator put before its end record, which then
    declares a central directory of only declared bytes. zipfile reads the zip64 record's size,
    so a gate that read only the end record's would let ZipFile parse the whole directory."""
    data = wide_directory_zip(size)
    end = len(data) - 22
    count = int.from_bytes(data[end + 10:end + 12], "little")
    zip64 = struct.pack("<4sQ2H2L4Q", b"PK\x06\x06", 44, 45, 45, 0, 0, count, count, size,
                        end - size)
    locator = struct.pack("<4sLQL", b"PK\x06\x07", 0, end, 1)
    record = data[end:end + 12] + declared.to_bytes(4, "little") + data[end + 16:]
    return data[:end] + zip64 + locator + record


def padded_manifest(size):
    """A root plugin.json of exactly size bytes carrying version 1.0.7."""
    stub = json.dumps({"version": "1.0.7", "pad": ""})
    return json.dumps({"version": "1.0.7", "pad": "x" * (size - len(stub))}).encode()


def write(d, rel, data):
    path = d / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def run(tool, d):
    r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / tool), "--root", str(d)],
                       capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout + r.stderr).strip()


def fixture(d, versions=("1.0.7",), stage=None, generate=True, allow=None, zip_version=None,
            zip_data=None):
    """A root with plugin/plugin.json, the cumulative record releases/SHA256SUMS holding the
    four asset lines of each version (llms-full.txt, the two zips, then the notes, as the
    release's SHA256SUMS asset lists them), newest release first, the zips of the stage
    versions (every version when stage is None) staged in site/downloads/, an optional
    allowlist, and the generated files; the plugin zips carry zip_version (their own version
    when None) in their root plugin.json, or are the bytes zip_data, recorded as they are, when
    it is given."""
    write(d, "plugin/plugin.json", json.dumps(MANIFEST))
    if allow is not None:
        write(d, "tools/redirects_allowlist.txt", allow)
    archives = {}
    for version in versions:
        archives[version] = {f"secureconfig-{version}.zip": b"skill " + version.encode(),
                             f"secureconfig-plugin-{version}.zip":
                                 zip_data or plugin_zip(zip_version or version)}
    lines = []
    for version in sorted(versions, key=lambda v: int(v.rsplit(".", 1)[1]), reverse=True):
        assets = {"llms-full.txt": b"corpus " + version.encode(),
                  **archives[version],
                  f"RELEASE-NOTES-v{version}.md": b"notes " + version.encode()}
        lines += [f"{hashlib.sha256(data).hexdigest()}  {name}"
                  for name, data in assets.items()]
    if lines:
        write_record(d, lines)
    for version in (versions if stage is None else stage):
        for name, data in archives[version].items():
            write(d, f"site/downloads/{name}", data)
    if generate:
        rc, out = run("gen_hosted.py", d)
        if rc != 0:
            raise AssertionError(f"the generator failed on a fixture: {out!r}")


def edit(d, rel, old, new):
    path = d / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"mutation {old!r} no longer matches {rel}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_record(d, lines):
    write(d, "releases/SHA256SUMS", "\n".join(lines) + "\n")


def record_lines(d):
    return (d / "releases/SHA256SUMS").read_text(encoding="utf-8").split("\n")[:-1]


# (description, build(d), expected text, expected exit) for check_hosted.py.
CASES = (
    ("no record, no zip and no generated file (main before the first hosted release)",
     lambda d: fixture(d, versions=()), "0 recorded release", 0),
    ("one recorded release with its zips staged and the generated files",
     lambda d: fixture(d), "1 recorded release", 0),
    ("two releases in one cumulative record, newest release first and both staged",
     lambda d: fixture(d, versions=("1.0.5", "1.0.7")), "2 recorded release", 0),
    ("site/marketplace.json with no recorded release behind it",
     lambda d: (fixture(d, versions=()), write(d, "site/marketplace.json", "{}\n")),
     "exists with no recorded release", 1),
    ("a latest link with no recorded release behind it",
     lambda d: (fixture(d, versions=()),
                write(d, "site/_redirects", gen_hosted.HEADER + "\n"
                      + "\n".join(gen_hosted.latest_lines("1.0.7")) + "\n")),
     "exists with no recorded release", 1),
    ("a staged zip whose bytes differ from the record",
     lambda d: (fixture(d),
                write(d, "site/downloads/secureconfig-plugin-1.0.7.zip", plugin_zip("1.0.8"))),
     "but the release record says", 1),
    ("a latest link edited to 301",
     lambda d: (fixture(d), edit(d, "site/_redirects", " 302\n", " 301\n")),
     "does not equal the generator's output", 1),
    ("an extra redirect appended to site/_redirects",
     lambda d: (fixture(d), edit(d, "site/_redirects",
                                 "/downloads/secureconfig-latest.zip",
                                 "/x / 302\n/downloads/secureconfig-latest.zip")),
     "does not equal the generator's output", 1),
    ("an edited catalog digest",
     lambda d: (fixture(d), edit(d, "site/marketplace.json", '"sha256": "', '"sha256": "0')),
     "does not equal the generator's output", 1),
    ("a missing staged archive for the newest record",
     lambda d: (fixture(d), (d / "site/downloads/secureconfig-1.0.7.zip").unlink()),
     "the newest record's zips", 1),
    ("the newest record not staged at all, even though redirected",
     lambda d: fixture(d, stage=(), allow=ASSET.format("1.0.7")),
     "the newest record's zips", 1),
    ("a plugin zip whose root plugin.json version differs from its record",
     lambda d: fixture(d, zip_version="1.0.6"),
     "says version '1.0.6' in its root plugin.json", 1),
    ("an aged-out release redirected to its own release assets",
     lambda d: fixture(d, versions=("1.0.5", "1.0.7"), stage=("1.0.7",),
                       allow=ASSET.format("1.0.5")),
     "2 recorded release", 0),
    ("an aged-out release with no redirect",
     lambda d: fixture(d, versions=("1.0.5", "1.0.7"), stage=("1.0.7",)),
     "entry redirects it to its release asset", 1),
    ("a record naming a -latest file",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS",
                                 "  secureconfig-1.0.7.zip", "  secureconfig-latest.zip")),
     "no record lists one", 1),
    ("a record whose plugin zip line names the skill zip again",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS", "  secureconfig-plugin-1.0.7.zip",
                                 "  secureconfig-1.0.7.zip")),
     "not secureconfig-plugin-1.0.7.zip", 1),
    ("a record holding only a release's first two asset lines",
     lambda d: (fixture(d), write_record(d, record_lines(d)[:2])),
     "not a multiple of four", 1),
    ("a stray entry under releases/",
     lambda d: (fixture(d), (d / "releases" / "v1.0.9").mkdir()),
     "is not the cumulative release record", 1),
    ("a corrupted record line",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS", "  secureconfig-1.0.7.zip",
                                 " secureconfig-1.0.7.zip")),
     "is not `<64 hex>  <name>`", 1),
    ("a record whose skill zip line carries no release archive's name",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS", "  secureconfig-1.0.7.zip",
                                 "  notes.txt")),
     "no release archive's name", 1),
    ("a record whose block opens with the skill zip, not llms-full.txt",
     lambda d: (fixture(d), write_record(d, record_lines(d)[1:] + record_lines(d)[:1])),
     "not llms-full.txt", 1),
    ("a release's block repeated after another release's (a duplicate version)",
     lambda d: (fixture(d, versions=("1.0.5", "1.0.7")),
                write_record(d, record_lines(d) + record_lines(d)[:4])),
     "once, together", 1),
    ("an out-of-order record, the older release first",
     lambda d: (fixture(d, versions=("1.0.5", "1.0.7")),
                write_record(d, record_lines(d)[4:] + record_lines(d)[:4])),
     "newest release first", 1),
    # The record is read as bytes, so a CRLF or lone-CR rewrite is refused, never read as LF.
    ("the record rewritten with CRLF line endings",
     lambda d: (fixture(d), write(d, "releases/SHA256SUMS",
                                  (d / "releases/SHA256SUMS").read_bytes()
                                  .replace(b"\n", b"\r\n"))),
     "holds a carriage return", 1),
    ("the record with a lone CR in place of its first LF",
     lambda d: (fixture(d), write(d, "releases/SHA256SUMS",
                                  (d / "releases/SHA256SUMS").read_bytes()
                                  .replace(b"\n", b"\r", 1))),
     "holds a carriage return", 1),
    ("an allowlist entry without a reason",
     lambda d: fixture(d, versions=(), allow="/old / 302\n", generate=False),
     "non-empty reason", 1),
    ("an asset redirect naming a zip no record names",
     lambda d: fixture(d, allow=ASSET.format("1.0.99")),
     "no record names", 1),
    ("an asset redirect for a recorded zip that is still staged",
     lambda d: fixture(d, versions=("1.0.5", "1.0.7"), allow=ASSET.format("1.0.5")),
     "is still staged", 1),
    ("a record without a trailing newline",
     lambda d: (fixture(d), write(d, "releases/SHA256SUMS", "\n".join(record_lines(d)))),
     "does not end with a newline", 1),
    ("an unrecorded file staged in site/downloads/ beside recorded zips",
     lambda d: (fixture(d), write(d, "site/downloads/extra.zip", "x\n")),
     "no record names it", 1),
    ("a staged zip with no record at all",
     lambda d: (fixture(d, versions=()), write(d, "site/downloads/extra.zip", "x\n")),
     "no record names it", 1),
    # The generated files are compared as bytes, so a line-ending rewrite, which a text-mode
    # read would fold back onto LF, is a finding.
    ("site/_redirects rewritten with CRLF line endings",
     lambda d: (fixture(d), write(d, "site/_redirects",
                                  (d / "site/_redirects").read_bytes().replace(b"\n", b"\r\n"))),
     "does not equal the generator's output", 1),
    ("site/_redirects with a lone CR in place of the header's LF",
     lambda d: (fixture(d), write(d, "site/_redirects",
                                  (d / "site/_redirects").read_bytes().replace(b"\n", b"\r", 1))),
     "does not equal the generator's output", 1),
    ("site/_redirects with a lone CR between the two latest links",
     lambda d: (fixture(d), write(d, "site/_redirects",
                                  (d / "site/_redirects").read_bytes().replace(
                                      b"302\n/downloads/secureconfig-plugin-latest.zip",
                                      b"302\r/downloads/secureconfig-plugin-latest.zip"))),
     "does not equal the generator's output", 1),
    ("site/marketplace.json rewritten with CRLF line endings",
     lambda d: (fixture(d), write(d, "site/marketplace.json",
                                  (d / "site/marketplace.json").read_bytes()
                                  .replace(b"\n", b"\r\n"))),
     "does not equal the generator's output", 1),
    ("a recorded zip staged as a symbolic link to identical bytes outside site/",
     lambda d: (fixture(d),
                write(d, "elsewhere.zip",
                      (d / "site/downloads/secureconfig-1.0.7.zip").read_bytes()),
                (d / "site/downloads/secureconfig-1.0.7.zip").unlink(),
                (d / "site/downloads/secureconfig-1.0.7.zip").symlink_to(d / "elsewhere.zip")),
     "is not a regular file", 1),
    ("an allowlist entry whose source a second entry repeats",
     lambda d: fixture(d, versions=(),
                       allow="/a /index.html 302\tmoved\n/a /checklist/ 302\tmoved again\n",
                       generate=False),
     "repeats the source", 1),
    ("an allowlist entry with a raw U+FEFF in its source",
     lambda d: fixture(d, versions=(), allow="/draft﻿ /index.html 302\tan old link\n",
                       generate=False),
     "printable ASCII", 1),
    # A plugin/plugin.json that is not JSON is a read error and one that is not an object is
    # unusable: each is reported in 1 FAIL line, never a traceback.
    ("an unparsable plugin/plugin.json with a record behind it",
     lambda d: (fixture(d), write(d, "plugin/plugin.json", "{\n")),
     "cannot read the record, the allowlist, the plugin manifest or the site", 2),
    ("a plugin/plugin.json that is a JSON array, with a record behind it",
     lambda d: (fixture(d), write(d, "plugin/plugin.json", "[]\n")),
     "is not a JSON object", 1),
    ("a plugin/plugin.json nested too deeply to parse, with a record behind it",
     lambda d: (fixture(d), write(d, "plugin/plugin.json", NESTED)),
     "nested too deeply to parse", 2),
    # The newest record's staged plugin zip is held to its record's version: a zip or a root
    # plugin.json the gate cannot read or use is a finding in 1 FAIL line, never a traceback.
    ("a staged plugin zip whose root plugin.json is nested too deeply to parse",
     lambda d: fixture(d, zip_data=plugin_zip("1.0.7", NESTED_MEMBER)),
     "its root plugin.json cannot be read (plugin.json is nested too deeply to parse as JSON)",
     1),
    ("a staged plugin zip whose root plugin.json is a JSON array",
     lambda d: fixture(d, zip_data=plugin_zip("1.0.7", b"[]\n")),
     "its root plugin.json cannot be used (plugin.json is not a JSON object)", 1),
    ("a staged plugin zip whose root plugin.json is UTF-16, not UTF-8",
     lambda d: fixture(d, zip_data=plugin_zip("1.0.7",
                                              json.dumps({"version": "1.0.7"}).encode("utf-16"))),
     "its root plugin.json cannot be read ('utf-8' codec can't decode", 1),
    ("a staged plugin zip whose root plugin.json opens with a UTF-8 byte order mark",
     lambda d: fixture(d, zip_data=plugin_zip("1.0.7", b"\xef\xbb\xbf"
                                              + json.dumps({"version": "1.0.7"}).encode())),
     "its root plugin.json cannot be read (Unexpected UTF-8 BOM", 1),
    ("a staged plugin zip whose deflated plugin.json data is damaged",
     lambda d: fixture(d, zip_data=damaged_zip()),
     "its root plugin.json cannot be read (Error -3 while decompressing data", 1),
    ("a staged plugin zip whose plugin.json names an unsupported compression method",
     lambda d: fixture(d, zip_data=unsupported_zip()),
     "its root plugin.json cannot be read (That compression method is not supported)", 1),
)

# (description, root plugin.json version of the newest staged plugin zip, expected text): the
# version is the zip's own text, so the gate prints it escaped, and each case is exit 1 in
# exactly 1 FAIL line, with no traceback and no line the version forged.
ESCAPED_CASES = (
    ("a staged plugin zip whose root plugin.json version is a lone surrogate",
     "\ud800", "says version '\\ud800' in its root plugin.json"),
    ("a staged plugin zip whose root plugin.json version carries a newline and a forged ok line",
     "9.9.9\n  ok    1 recorded release(s): forged",
     "says version '9.9.9\\n  ok    1 recorded release(s): forged' in its root plugin.json"),
)


def check_escaped(failures):
    """ESCAPED_CASES: exit 1 and a single output line, the FAIL line carrying the escaped
    version (run() strips the leading spaces of the first line)."""
    for desc, version, expected in ESCAPED_CASES:
        d = Path(tempfile.mkdtemp())
        try:
            fixture(d, zip_version=version)
            rc, out = run("check_hosted.py", d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        lines = out.splitlines()
        if rc != 1 or len(lines) != 1 or not lines[0].startswith("FAIL  ") or expected not in out:
            failures.append(f"{desc}: expected exit 1 in 1 FAIL line containing {expected!r}, "
                            f"got {rc}: {out!r}")
    return len(ESCAPED_CASES)


def check_caps(failures):
    """The gate's size caps, each on a fixture whose staged files and record agree: a staged
    plugin zip of DOWNLOAD_MAX + 1 bytes (scripts/build-site.py's per-file cap), a zip bomb
    whose root plugin.json declares 32 MiB uncompressed in under 32 KiB of deflated data, and
    a zip bomb whose bzip2 root plugin.json declares 16 bytes but decompresses to 8 MiB, are
    each exit 1 in exactly 1 FAIL line, never a traceback or a MemoryError. A root plugin.json
    of exactly MANIFEST_MAX bytes is read and passes. A staged plugin zip of DOWNLOAD_MAX bytes
    whose central directory fills it, 455902 records, and a valid plugin zip whose central
    directory is one byte over CENTRAL_MAX are each exit 1 in exactly 1 FAIL line saying that
    the zip is not opened, and a valid plugin zip whose central directory is exactly CENTRAL_MAX
    bytes is opened and passes. A valid plugin zip whose zip64 end record declares a central
    directory one byte over CENTRAL_MAX while its end record declares 46 bytes, a directory
    zipfile would read whole, is exit 1 in exactly 1 FAIL line too, which gives the zip64
    record's size."""
    over = check_hosted.DOWNLOAD_MAX + 1
    cap = check_hosted.MANIFEST_MAX
    central = check_hosted.CENTRAL_MAX
    filled = (check_hosted.DOWNLOAD_MAX - 22) // 46 * 46
    cases = (
        ("a staged plugin zip one byte over DOWNLOAD_MAX", b"\0" * over,
         f"secureconfig-plugin-1.0.7.zip is {over} bytes, over the "
         f"{check_hosted.DOWNLOAD_MAX}-byte cap on 1 release archive", 1),
        ("a zip bomb whose root plugin.json declares 32 MiB uncompressed",
         plugin_zip("1.0.7", b"[" * (32 * 1024 * 1024), compression=zipfile.ZIP_DEFLATED),
         f"its root plugin.json declares {32 * 1024 * 1024} bytes uncompressed, over the "
         f"{cap}-byte cap on that member, so it is not read", 1),
        ("a bzip2 zip bomb whose root plugin.json declares 16 bytes and decompresses to 8 MiB",
         lying_bzip2_zip(8 * 1024 * 1024, 16),
         "its root plugin.json uses compression method 12, which this gate does not read", 1),
        ("a root plugin.json of exactly MANIFEST_MAX bytes",
         plugin_zip("1.0.7", padded_manifest(cap), compression=zipfile.ZIP_DEFLATED),
         "1 recorded release", 0),
        ("a staged plugin zip of DOWNLOAD_MAX bytes whose central directory fills it",
         full_directory_zip(check_hosted.DOWNLOAD_MAX),
         f"its end record, or its zip64 end record when it has one, declares a central "
         f"directory of {filled} bytes, over the "
         f"{central}-byte cap on it, so the zip is not opened", 1),
        ("a plugin zip whose central directory is one byte over CENTRAL_MAX",
         wide_directory_zip(central + 1),
         f"its end record, or its zip64 end record when it has one, declares a central "
         f"directory of {central + 1} bytes, over the "
         f"{central}-byte cap on it, so the zip is not opened", 1),
        ("a plugin zip whose central directory is exactly CENTRAL_MAX bytes",
         wide_directory_zip(central), "1 recorded release", 0),
        ("a plugin zip whose zip64 end record declares a central directory one byte over "
         "CENTRAL_MAX while its end record declares 46 bytes",
         zip64_directory_zip(central + 1, 46),
         f"its end record, or its zip64 end record when it has one, declares a central "
         f"directory of {central + 1} bytes, over the "
         f"{central}-byte cap on it, so the zip is not opened", 1),
    )
    for desc, data, expected, want in cases:
        d = Path(tempfile.mkdtemp())
        try:
            fixture(d, zip_data=data)
            rc, out = run("check_hosted.py", d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        lines = out.splitlines()
        if (rc != want or expected not in out or "Traceback" in out or "MemoryError" in out
                or (want == 1 and (len(lines) != 1 or not lines[0].startswith("FAIL  ")))):
            failures.append(f"{desc}: expected exit {want} in 1 line containing {expected!r}, "
                            f"got {rc}: {out[:400]!r}")
    return len(cases)


def check_generator(failures):
    """The generator's own behaviour: nothing to write, byte-equal reruns, exact content."""
    count = 0
    d = Path(tempfile.mkdtemp())
    try:
        fixture(d, versions=(), generate=False)
        rc, out = run("gen_hosted.py", d)
        count += 1
        if rc != 0 or "nothing to write" not in out or (d / "site").exists():
            failures.append(f"the generator on a root with no record should write nothing: "
                            f"{rc}, {out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d = Path(tempfile.mkdtemp())
    try:
        fixture(d, generate=False)
        write(d, "plugin/plugin.json", NESTED)
        rc, out = run("gen_hosted.py", d)
        count += 1
        if (rc != 2 or "nested too deeply to parse" not in out
                or "Traceback (most recent call last):" in out):
            failures.append(f"the generator on a plugin/plugin.json nested too deeply to parse "
                            f"should exit 2 in 1 FAIL line: {rc}, {out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    d = Path(tempfile.mkdtemp())
    try:
        # The entry's target is a published file beside the pages, which check_draft.py admits
        # as a gated target (the generated catalog and the host's config files are not).
        fixture(d, versions=("1.0.5", "1.0.7"),
                allow="/old /llms.txt 302\tthe old URL of the index\n")
        write(d, "site/llms.txt", "secureconfig\n")
        first = {rel: (d / rel).read_bytes() for rel in ("site/marketplace.json",
                                                         "site/_redirects")}
        rc, out = run("gen_hosted.py", d)
        second = {rel: (d / rel).read_bytes() for rel in first}
        count += 1
        if rc != 0 or first != second:
            failures.append(f"two generator runs are not byte-equal: {rc}, {out!r}")
        catalog = json.loads(first["site/marketplace.json"])
        entry = catalog["plugins"][0]["source"]
        record = (d / "releases/SHA256SUMS").read_text(encoding="utf-8")
        count += 1
        if (catalog["name"] != "secureconfig"
                or entry["url"] != "https://secureconfig.ai/downloads/"
                                   "secureconfig-plugin-1.0.7.zip"
                or f"{entry['sha256']}  secureconfig-plugin-1.0.7.zip" not in record):
            failures.append(f"the catalog does not carry the newest record's url and sha256: "
                            f"{catalog!r}")
        lines = first["site/_redirects"].decode("utf-8").split("\n")
        count += 1
        if lines != [gen_hosted.HEADER, "/old /llms.txt 302",
                     "/downloads/secureconfig-latest.zip "
                     "/downloads/secureconfig-1.0.7.zip 302",
                     "/downloads/secureconfig-plugin-latest.zip "
                     "/downloads/secureconfig-plugin-1.0.7.zip 302", ""]:
            failures.append(f"site/_redirects is not the header, the allowlist rule and the two "
                            f"newest latest links: {lines!r}")
        rc, out = run("check_draft.py", d)
        count += 1
        if "site/_redirects" in out:
            failures.append(f"check_draft.py reports the generated site/_redirects: {out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    count += 1
    if gen_hosted.HEADER != check_draft.REDIRECTS_HEADER:
        failures.append("gen_hosted.HEADER and check_draft.REDIRECTS_HEADER differ; the gate "
                        "would refuse every generated site/_redirects")
    return count


def check_step9(failures):
    """The records procedure of CONTRIBUTING.md Releasing step 9 on a real asset's bytes: the
    release's SHA256SUMS asset lists llms-full.txt, the two zips and the notes, in that order,
    exactly as tools/check_release.py sums() writes it; a byte copy of it is the whole record,
    the zips are staged, and gen_hosted.py, check_hosted.py and scripts/build-site.py --check
    each pass. The site build writes its pages into the fixture's site/ first, so its --check
    reads the record, the staged zips and the generated files beside them."""
    count = 0
    d = Path(tempfile.mkdtemp())
    try:
        write(d, "plugin/plugin.json", json.dumps(MANIFEST))
        version = "1.0.7"
        staged = {f"secureconfig-{version}.zip": b"skill " + version.encode(),
                  f"secureconfig-plugin-{version}.zip": plugin_zip(version)}
        files = [("llms-full.txt", b"corpus\n"), *staged.items(),
                 (f"RELEASE-NOTES-v{version}.md", b"# notes\n")]
        # The asset's bytes as tools/check_release.py sums() writes them for names() minus the
        # asset itself, which lists the other four.
        asset = "".join(f"{hashlib.sha256(data).hexdigest()}  {name}\n"
                        for name, data in files).encode("ascii")
        write(d, "releases/SHA256SUMS", asset)
        for name, data in staged.items():
            write(d, f"site/downloads/{name}", data)
        count += 1
        if (d / "releases/SHA256SUMS").read_bytes() != asset:
            failures.append("the record is not the asset's bytes, so no byte copy was tested")
        rc, out = run("gen_hosted.py", d)
        count += 1
        if rc != 0:
            failures.append(f"gen_hosted.py refused a record that is a byte copy of a release's "
                            f"SHA256SUMS asset: {rc}, {out!r}")
        rc, out = run("check_hosted.py", d)
        count += 1
        if rc != 0 or "1 recorded release" not in out:
            failures.append(f"check_hosted.py refused the step 9 root: {rc}, {out!r}")
        build = TOOLS.parent / "scripts" / "build-site.py"
        built = subprocess.run([sys.executable, "-I", "-B", str(build), "--out",
                                str(d / "site")], capture_output=True, text=True, timeout=300)
        count += 1
        if built.returncode != 0:
            failures.append(f"the site build into the step 9 root failed: "
                            f"{(built.stdout + built.stderr).strip()!r}")
        checked = subprocess.run([sys.executable, "-I", "-B", str(build), "--check", "--out",
                                  str(d / "site")], capture_output=True, text=True, timeout=300)
        count += 1
        if checked.returncode != 0:
            failures.append(f"build-site.py --check refused the step 9 root: "
                            f"{(checked.stdout + checked.stderr).strip()!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return count


def check_depth(failures):
    """gen_hosted.json_object at its depth limit, in process: the depth counts brackets open at
    once outside strings, up to the first closing bracket with no open bracket to close, so the
    result never depends on how deep json.loads can recurse."""
    limit = gen_hosted.MAX_JSON_DEPTH
    deep = "[" * 100000 + "]" * 100000
    cases = (
        ("an object nested exactly MAX_JSON_DEPTH deep",
         '{"a": ' + "[" * (limit - 1) + "]" * (limit - 1) + "}", None),
        ("an object nested one level deeper than MAX_JSON_DEPTH",
         '{"a": ' + "[" * limit + "]" * limit + "}", "nested too deeply to parse as JSON"),
        ("an object whose deep nesting sits inside one value",
         '{"name": "secureconfig", "deep": ' + deep + "}", "nested too deeply to parse as JSON"),
        # The escaped quote must not end the string and the escaped backslash must not escape the
        # closing quote; a reader that got either wrong would count the brackets after it.
        ("a string holding 300000 brackets, an escaped quote and an escaped backslash",
         '{"s": "' + deep + '\\"' + "{" * 100000 + '\\\\", "t": "' + "[" * (limit + 1) + '"}',
         None),
        # The count stops at the first closing bracket with no open bracket to close, where
        # json.loads fails, so 150 brackets opened after it, past the limit, are never counted.
        ("an unmatched closing bracket followed by 150 opening ones",
         "]" + "[" * 150, "Expecting value: line 1 column 1 (char 0)"),
        ("an object holding a 5000-digit integer",
         '{"n": ' + "1" * 5000 + "}", "for integer string conversion"),
    )
    for desc, text, expected in cases:
        try:
            value = gen_hosted.json_object(text, "case.json")
            why = None
        except gen_hosted.HostedError as exc:
            value, why = None, f"HostedError: {exc}"
        except ValueError as exc:
            value, why = None, str(exc)
        except RecursionError:
            value, why = None, "RecursionError escaped"
        if expected is None and not isinstance(value, dict):
            failures.append(f"json_object refused {desc}: {why!r}")
        elif expected is not None and (why is None or why.startswith("HostedError")
                                       or expected not in why):
            failures.append(f"json_object did not refuse {desc} as {expected!r}: {why!r}")
    return len(cases)


def main():
    failures = []
    count = 0
    for desc, build, expected, want in CASES:
        d = Path(tempfile.mkdtemp())
        try:
            build(d)
            rc, out = run("check_hosted.py", d)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        count += 1
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    count += check_escaped(failures)
    count += check_caps(failures)
    count += check_generator(failures)
    count += check_step9(failures)
    count += check_depth(failures)
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {count} recorded cases for the hosted gate and its generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
