#!/usr/bin/env python3
"""Check the hosted install surface against the release record.

WHY: the hosted catalog and the latest links point an installer at bytes by digest, and Claude
Code refuses an archive whose digest does not match, so a wrong committed digest breaks every
hosted install and a right one must come from the release record, never from a hand. This gate
holds what is committed to what tools/gen_hosted.py writes from the record, so a hand edit, a
typed zip digest, a stale latest link or a missing staged archive fails the suite offline. The
digests on a release's llms-full.txt and notes lines are checked against nothing, since no gate
compares those lines with any file, so a wrong one, all zeros included, passes.

WHAT IT CHECKS:
  - the cumulative record releases/SHA256SUMS parses (gen_hosted.read_records: a byte copy of
    each release's SHA256SUMS asset, four sha256sum lines per release in the asset's order,
    llms-full.txt, the two zips, then the notes, LF line ends only, newest release first, no
    release repeated, no `-latest` name, and only the zip lines feed the checks below);
  - with no record: site/marketplace.json does not exist, site/_redirects, when present,
    equals the generator's output, which then holds no latest line, and nothing sits in
    site/downloads/; a tree with no record, no zip and no generated file passes, so this half
    of the gate requires nothing of a tree like today's main;
  - with records: site/marketplace.json and site/_redirects each exist and equal the generator's
    output byte for byte, which pins the catalog's url and sha256 to the newest record and the
    two latest links, each 302, to that record's versioned zips, exactly;
  - for every recorded release and each of its zips: the file is staged in site/downloads/
    with the record's SHA-256, or, for a version older than the newest, an allowlist entry of
    tools/redirects_allowlist.txt redirects /downloads/<zip> to that release's GitHub asset at
    https://github.com/jposluns/secureconfig/releases/download/v1.0.<N>/<zip>;
  - every release-asset entry of tools/redirects_allowlist.txt is held to the record in turn:
    it names a recorded zip that is no longer staged, so a reviewed entry cannot send a reader
    to an asset URL the committed record does not name or shadow a staged copy. This gate
    reads only the committed record, never GitHub: what a published release really carries is
    checked at release time, not here (tools/check_draft.py refuses every other source and
    target shape);
  - each recorded zip staged as a regular file is at most DOWNLOAD_MAX bytes, the per-file cap
    that scripts/build-site.py --check holds site/downloads/ to, read from that script; one
    over it is a finding and is never read, and one within it is hashed in chunks;
  - the newest record's zips must be staged, since the latest links and the catalog point at
    hosted copies;
  - every entry under site/downloads/ is one of the record's zips: a file no record names, and
    anything that is not a regular file, a symbolic link included, are refused, so with the
    digest check above every file staged there is a recorded zip whose bytes match the record;
  - the newest record's staged plugin zip holds a plugin.json at its root whose version equals
    the record's version, so the catalog cannot name bytes of another version. A zip that
    cannot be read or has no root plugin.json, and a root plugin.json that is not UTF-8, cannot
    be parsed as JSON (one nested too deeply to parse included) or is not a JSON object, are
    each a finding in 1 FAIL line, never a traceback. So is a root plugin.json whose zip entry
    declares more than MANIFEST_MAX bytes (64 KiB) uncompressed or that is compressed with a
    method other than stored or deflated, and it is not read, so a decompression bomb is a
    finding, never a MemoryError. When the zip gains .claude-plugin/plugin.json, this check will
    be extended to it.

Offline, standard library only, and it writes nothing. Exit 0 ok; 1 on a finding, which
includes a record, an allowlist or a plugin/plugin.json that cannot be used; 2 on a read error,
which includes a plugin/plugin.json that is not UTF-8 or cannot be parsed as JSON, one nested
too deeply to parse among them. Each is reported in FAIL lines.
Usage: python3 -I -B tools/check_hosted.py [--root <repository root>]
"""
import argparse
import hashlib
import importlib.util
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_hosted  # noqa: E402  (the one place the generated content is defined)
from _archives import ARCHIVES, archive_name  # noqa: E402

# The per-file cap on a staged release archive is scripts/build-site.py's DOWNLOAD_MAX, the cap
# its --check holds each file in site/downloads/ to, read from that script so the two cannot
# differ. A staged file over it is a finding and is never read.
_spec = importlib.util.spec_from_file_location(
    "build_site", Path(__file__).resolve().parents[1] / "scripts" / "build-site.py")
_build_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_build_site)
DOWNLOAD_MAX = _build_site.DOWNLOAD_MAX
# A staged file is hashed in chunks of this many bytes, so no read holds a whole zip.
CHUNK = 1024 * 1024
# The cap on a staged plugin zip's root plugin.json, on the size its zip entry declares and on
# the bytes a read decompresses. plugin/plugin.json is under 1 KiB, so 64 KiB leaves room to
# grow while a decompression bomb is refused before it is read.
MANIFEST_MAX = 64 * 1024
# The compression methods whose decompression zipfile bounds on each read: stored data needs
# none, and for deflate it passes the read's size to zlib. For each other method it supports,
# bzip2 and LZMA among them, it decompresses each chunk of compressed data it reads whole,
# however large the output, so a member compressed with one is not read.
BOUNDED_METHODS = (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)

SITE = Path("site")
DOWNLOADS = SITE / "downloads"
# An aged-out zip's redirect: /downloads/<zip> to that release's own GitHub asset, same version
# and same name (the form that keeps every published versioned URL working).
ASSET_RULE = re.compile(r"/downloads/(secureconfig(?:-plugin)?-(1\.0\.[1-9][0-9]*)\.zip) "
                        r"https://github\.com/jposluns/secureconfig/releases/download/"
                        r"v\2/\1 302")


def asset_redirects(rules):
    """The zip names whose /downloads/ URL an allowlist rule redirects to its release asset."""
    return {match.group(1) for rule in rules for match in [ASSET_RULE.fullmatch(rule)] if match}


def staged_size(root, name):
    """The size in bytes of site/downloads/<name>, or None when it is not a regular file (a
    symbolic link, which is not one, is never followed here)."""
    path = root / DOWNLOADS / name
    if path.is_symlink() or not path.is_file():
        return None
    return path.stat().st_size


def staged_digest(root, name):
    """The staged archive's SHA-256, read in chunks of CHUNK bytes, so no read holds the whole
    file. The caller has already checked, with staged_size(), that it is a regular file of at
    most DOWNLOAD_MAX bytes."""
    digest = hashlib.sha256()
    with open(root / DOWNLOADS / name, "rb") as staged:
        while chunk := staged.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def zip_manifest_version(path):
    """The version in the plugin.json at the root of the plugin zip at path, or the reason it
    cannot be used: any archive or manifest it cannot read or use is a reason, never an
    exception. The member is read only when the size its entry declares is at most
    MANIFEST_MAX and its compression method is one in BOUNDED_METHODS, and then by a read of at
    most MANIFEST_MAX + 1 bytes, so a decompression bomb is a reason, never a MemoryError."""
    try:
        with zipfile.ZipFile(path) as archive:
            info = archive.getinfo("plugin.json")
            if info.file_size > MANIFEST_MAX:
                return None, (f"its root plugin.json declares {info.file_size} bytes "
                              f"uncompressed, over the {MANIFEST_MAX}-byte cap on that member, "
                              f"so it is not read")
            # An unsupported method or an encrypted member is refused here, before any data is
            # read, with the exception zipfile raises for it.
            with archive.open(info) as member:
                if info.compress_type not in BOUNDED_METHODS:
                    return None, (f"its root plugin.json uses compression method "
                                  f"{info.compress_type}, which this gate does not read: only a "
                                  f"stored or deflated member is decompressed in bounded steps")
                raw = member.read(MANIFEST_MAX + 1)
            # zipfile stops a member's output at its declared size, so this holds already; the
            # bounded read keeps it true without relying on that.
            if len(raw) > MANIFEST_MAX:
                return None, (f"its root plugin.json decompresses to more than {MANIFEST_MAX} "
                              f"bytes, over the cap on that member, so it is not read further")
    except Exception as exc:  # noqa: BLE001  a zip this cannot read is a finding
        # The file is an untrusted archive of at most DOWNLOAD_MAX bytes, and zipfile and its
        # decompressors raise many unrelated types on damaged ones (BadZipFile, KeyError,
        # ValueError, OSError, NotImplementedError, RuntimeError and zlib.error among them), so
        # any failure to read the one member is a finding; nothing but that read is guarded
        # here.
        return None, f"its root plugin.json cannot be read ({exc})"
    try:
        # Read as UTF-8 only, as plugin/plugin.json is, so a UTF-16 or UTF-32 manifest, or one
        # opening with a byte order mark, which json.loads would accept from bytes, is refused.
        manifest = gen_hosted.json_object(raw.decode("utf-8"), "plugin.json")
    except gen_hosted.HostedError as exc:
        return None, f"its root plugin.json cannot be used ({exc})"
    except ValueError as exc:  # not UTF-8, not JSON, or nested too deeply to parse
        return None, f"its root plugin.json cannot be read ({exc})"
    version = manifest.get("version")
    if not isinstance(version, str):
        return None, "its root plugin.json has no string version"
    return version, None


def generated_findings(root, records):
    """The findings for the generated files: each exists exactly when it has content and equals
    the generator's output byte for byte."""
    findings = []
    for rel, expected, behind in ((gen_hosted.MARKETPLACE,
                                   gen_hosted.marketplace_text(root, records) if records
                                   else None, "no recorded release"),
                                  (gen_hosted.REDIRECTS,
                                   gen_hosted.redirects_text(root, records),
                                   "no recorded release or allowlist entry")):
        path = root / rel
        # Both sides compared as bytes, so a CRLF or lone-CR rewrite, which a text-mode read
        # would fold back onto LF, is a finding too.
        found = path.read_bytes() if path.is_file() else None
        want = expected.encode("utf-8") if expected is not None else None
        if want is None and found is not None:
            findings.append(f"{rel} exists with {behind} behind it; the generator would write "
                            f"nothing for this tree, so remove the file or commit what it "
                            f"should come from")
        elif want is not None and found is None:
            findings.append(f"{rel} is missing; run python3 -I -B tools/gen_hosted.py and commit "
                            f"what it writes")
        elif want != found:
            findings.append(f"{rel} does not equal the generator's output; it is generated and "
                            f"never hand-edited, so run python3 -I -B tools/gen_hosted.py")
    return findings


def allowlist_findings(root, records, rules):
    """The findings for the allowlist's release-asset redirects, each held to the release
    record: the entry names a recorded zip that is no longer staged, so the record vouches for
    every asset URL a reader is sent to (tools/check_draft.py refuses every other asset shape,
    and a still-staged source also fails its shadow rule)."""
    findings = []
    recorded = {name for names in records.values() for name in names}
    for rule in rules:
        matched = ASSET_RULE.fullmatch(rule)
        if not matched:
            continue
        name = matched.group(1)
        if name not in recorded:
            findings.append(f"{gen_hosted.ALLOWLIST} redirects /downloads/{name} to a release "
                            f"asset, but no record names {name}; an entry redirects only a "
                            f"recorded zip, so the record vouches for the asset URL it names")
        elif (root / DOWNLOADS / name).is_file():
            findings.append(f"{gen_hosted.ALLOWLIST} redirects /downloads/{name} to its release "
                            f"asset, but {DOWNLOADS}/{name} is still staged; an entry covers "
                            f"only an aged-out zip, so remove the entry until the zip ages out "
                            f"of {DOWNLOADS}")
    return findings


def record_findings(root, records, rules):
    """The findings for each record's zips: staged with the record's digest, or redirected to
    their release assets when aged out; the newest record's zips staged."""
    findings = []
    redirected = asset_redirects(rules)
    current = gen_hosted.newest(records) if records else None
    for version in sorted(records, key=lambda v: int(v.rsplit(".", 1)[1])):
        for kind in ARCHIVES:
            name = archive_name(kind, version)
            size = staged_size(root, name)
            if size is not None and size > DOWNLOAD_MAX:
                findings.append(f"{DOWNLOADS}/{name} is {size} bytes, over the {DOWNLOAD_MAX}-"
                                f"byte cap on 1 release archive (DOWNLOAD_MAX in "
                                f"scripts/build-site.py), so it is not read")
                continue
            digest = staged_digest(root, name) if size is not None else None
            if digest is None:
                if version == current:
                    findings.append(f"{DOWNLOADS}/{name} is missing; the newest record's zips "
                                    f"are what the latest links and the catalog point at, so "
                                    f"they stay staged")
                elif name not in redirected:
                    findings.append(f"{DOWNLOADS}/{name} is missing and no "
                                    f"{gen_hosted.ALLOWLIST} entry redirects it to its release "
                                    f"asset; every published versioned URL keeps working")
            elif digest != records[version][name]:
                findings.append(f"{DOWNLOADS}/{name} has SHA-256 {digest}, but the release "
                                f"record says {records[version][name]}; the staged file is the "
                                f"released zip's bytes, copied")
    if current:
        name = archive_name(gen_hosted.PLUGIN_KIND, current)
        size = staged_size(root, name)
        # Only a staged regular file within the cap is opened; one over it is a finding above,
        # and a symbolic link is one in staged_findings().
        if size is not None and size <= DOWNLOAD_MAX:
            version, why = zip_manifest_version(root / DOWNLOADS / name)
            if why:
                findings.append(f"{DOWNLOADS}/{name}: {why}")
            elif version != current:
                # The version is the zip's own text, so it is printed escaped (ascii()): no
                # character in it can end the FAIL line, forge another or fail to encode.
                findings.append(f"{DOWNLOADS}/{name} says version {version!a} in its root "
                                f"plugin.json, but its record says {current}; the catalog names "
                                f"one version of one zip")
    return findings


def staged_findings(root, records):
    """The findings for site/downloads/ itself: every entry there is one of the record's zips,
    staged as a regular file (record_findings holds each recorded name's bytes to the record's
    digest), so no unrecorded file sits among the hosted archives."""
    findings = []
    folder = root / DOWNLOADS
    if not folder.is_dir():
        return findings
    recorded = {name for names in records.values() for name in names}
    for entry in sorted(folder.iterdir()):
        shown = ascii(str(DOWNLOADS / entry.name))  # a file name is printed escaped, as above
        # is_file() alone would follow a symbolic link, so a link is refused by its own type.
        if entry.is_symlink() or not entry.is_file():
            findings.append(f"{shown} is not a regular file; {DOWNLOADS} "
                            f"holds the record's zips and nothing else")
        elif entry.name not in recorded:
            findings.append(f"{shown} is staged, but no record names it; "
                            f"every file under {DOWNLOADS} is a recorded release zip, held to "
                            f"its recorded SHA-256 by this gate")
    return findings


def check(root):
    records = gen_hosted.read_records(root)
    rules = gen_hosted.read_allowlist(root)
    return (generated_findings(root, records) + allowlist_findings(root, records, rules)
            + record_findings(root, records, rules) + staged_findings(root, records),
            len(records))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    try:
        findings, count = check(args.root)
    except gen_hosted.HostedError as exc:
        print(f"  FAIL  {exc}")
        return 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"  FAIL  cannot read the record, the allowlist, the plugin manifest or the site: "
              f"{exc}")
        return 2
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    {count} recorded release(s): the generated catalog and redirects match the "
          f"generator's output, and every recorded zip is staged with its recorded SHA-256 or "
          f"redirected to its release asset")
    return 0


if __name__ == "__main__":
    sys.exit(main())
