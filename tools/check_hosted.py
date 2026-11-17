#!/usr/bin/env python3
"""Check the hosted install surface against the release record.

WHY: the hosted catalog and the latest links point an installer at bytes by digest, and Claude
Code refuses an archive whose digest does not match, so a wrong committed digest breaks every
hosted install and a right one must come from the release record, never from a hand. This gate
holds what is committed to what tools/gen_hosted.py writes from the record, so a hand edit, a
typed digest, a stale latest link or a missing staged archive fails the suite offline.

WHAT IT CHECKS:
  - the cumulative record releases/SHA256SUMS parses (gen_hosted.read_records: sha256sum lines
    whose names carry each release's version, one block per release, newest release first, both
    zips named per release, nothing named twice, no `-latest` name);
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
  - the newest record's zips must be staged, since the latest links and the catalog point at
    hosted copies;
  - every entry under site/downloads/ is one of the record's zips: a file no record names, and
    anything that is not a regular file, a symbolic link included, are refused, so with the
    digest check above every file staged there is a recorded zip whose bytes match the record;
  - the newest record's staged plugin zip holds a plugin.json at its root whose version equals
    the record's version, so the catalog cannot name bytes of another version. When the zip
    gains .claude-plugin/plugin.json, this check will be extended to it.

Offline, standard library only, and it writes nothing. Exit 0 ok, 1 on a finding, 2 on a read
error. Usage: python3 -I -B tools/check_hosted.py [--root <repository root>]
"""
import argparse
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_hosted  # noqa: E402  (the one place the generated content is defined)
from _archives import ARCHIVES, archive_name  # noqa: E402

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


def staged_digest(root, name):
    """The staged archive's SHA-256, or None when site/downloads/<name> is not a regular file
    (a symbolic link, which is not one, is never followed here)."""
    path = root / DOWNLOADS / name
    if path.is_symlink() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zip_manifest_version(data):
    """The version in the plugin.json at a plugin zip's root, or the reason it cannot be read."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            manifest = json.loads(archive.read("plugin.json"))
    except (KeyError, ValueError, zipfile.BadZipFile) as exc:
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
            digest = staged_digest(root, name)
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
        path = root / DOWNLOADS / name
        if path.is_file():
            version, why = zip_manifest_version(path.read_bytes())
            if why:
                findings.append(f"{DOWNLOADS}/{name}: {why}")
            elif version != current:
                findings.append(f"{DOWNLOADS}/{name} says version {version} in its root "
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
        # is_file() alone would follow a symbolic link, so a link is refused by its own type.
        if entry.is_symlink() or not entry.is_file():
            findings.append(f"{DOWNLOADS}/{entry.name} is not a regular file; {DOWNLOADS} "
                            f"holds the record's zips and nothing else")
        elif entry.name not in recorded:
            findings.append(f"{DOWNLOADS}/{entry.name} is staged, but no record names it; "
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
