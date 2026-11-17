#!/usr/bin/env python3
"""Cases for tools/gen_hosted.py and tools/check_hosted.py, the hosted install surface.

Each case builds a throwaway root under TMPDIR, with a plugin/plugin.json, the cumulative
release record releases/SHA256SUMS (each release's lines together, newest release first), staged
archives under site/downloads/ and, in most cases, the generated site/marketplace.json and
site/_redirects, then runs the generator or the gate on it by path, so nothing touches this
checkout. The accepted roots are a root with no record, no zip and no generated file (what
`main` is before the first hosted release), a generated root with one recorded release, and the
generator run twice, whose outputs are byte-equal. Two more are accepted: a generated root with
two releases in one record, newest first and both staged, and a generated root whose aged-out
release's zips are redirected to their own release assets by allowlist entries. The refusals
cover each half of the gate. The drift half: a generated file with no recorded release behind it (the catalog and a
latest link), a missing generated file with a record behind it, an edited catalog digest, a
latest link edited to 301, and an extra redirect appended. The record half: a staged zip whose
bytes differ from its record, a missing staged archive for the newest release, a newest release
not staged at all even though redirected, an aged-out zip with no redirect, and a staged file in
site/downloads/ that no record names, beside recorded zips and with no record. The record's own
shape: a record naming a -latest file, a record missing a zip line, a corrupted record line, a
record without a trailing newline, a line whose name carries no version, a release's lines
repeated after another release's (a duplicate version), an out-of-order record with the older
release first, and a stray entry under releases/. The allowlist half: an asset redirect naming a
zip no record names, an asset redirect for a recorded zip that is still staged, and an allowlist
entry without a reason. The rest: a plugin zip whose root plugin.json version differs from its
record. One in-process case holds check_draft.REDIRECTS_HEADER to
gen_hosted.HEADER, so the gate and the generator cannot drift apart on the file's first line.

Nothing here reads git history or the network. Exit 0 ok, 1 on a finding.
"""
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import check_draft  # noqa: E402
import gen_hosted  # noqa: E402

MANIFEST = {"name": "secureconfig", "version": "1.0.7", "description": "guides",
            "author": {"name": "Jeff Posluns", "url": "https://secureconfig.ai"}}
ASSET = ("/downloads/secureconfig-{0}.zip https://github.com/jposluns/secureconfig/releases/"
         "download/v{0}/secureconfig-{0}.zip 302\taged out\n"
         "/downloads/secureconfig-plugin-{0}.zip https://github.com/jposluns/secureconfig/"
         "releases/download/v{0}/secureconfig-plugin-{0}.zip 302\taged out\n")


def plugin_zip(version):
    """A minimal plugin zip: a plugin.json at its root carrying version."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("plugin.json", json.dumps({"version": version}))
    return out.getvalue()


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


def fixture(d, versions=("1.0.7",), stage=None, generate=True, allow=None, zip_version=None):
    """A root with plugin/plugin.json, the cumulative record releases/SHA256SUMS holding the two
    zip lines of each version, newest release first, the zips of the stage versions (every
    version when stage is None) staged in site/downloads/, an optional allowlist, and the
    generated files; the plugin zips carry zip_version (their own version when None) in their
    root plugin.json."""
    write(d, "plugin/plugin.json", json.dumps(MANIFEST))
    if allow is not None:
        write(d, "tools/redirects_allowlist.txt", allow)
    archives = {}
    for version in versions:
        archives[version] = {f"secureconfig-{version}.zip": b"skill " + version.encode(),
                             f"secureconfig-plugin-{version}.zip":
                                 plugin_zip(zip_version or version)}
    lines = []
    for version in sorted(versions, key=lambda v: int(v.rsplit(".", 1)[1]), reverse=True):
        lines += [f"{hashlib.sha256(data).hexdigest()}  {name}"
                  for name, data in archives[version].items()]
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
     "says version 1.0.6 in its root plugin.json", 1),
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
    ("a record missing its plugin zip line",
     lambda d: (fixture(d),
                write_record(d, ["0" * 64 + "  secureconfig-1.0.7.zip"])),
     "does not name secureconfig-plugin-1.0.7.zip", 1),
    ("a stray entry under releases/",
     lambda d: (fixture(d), (d / "releases" / "v1.0.9").mkdir()),
     "is not the cumulative release record", 1),
    ("a corrupted record line",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS", "  secureconfig-1.0.7.zip",
                                 " secureconfig-1.0.7.zip")),
     "is not `<64 hex>  <name>`", 1),
    ("a record line whose name carries no version",
     lambda d: (fixture(d), edit(d, "releases/SHA256SUMS", "  secureconfig-1.0.7.zip",
                                 "  notes.txt")),
     "no release archive's name", 1),
    ("a release's lines repeated after another release's (a duplicate version)",
     lambda d: (fixture(d, versions=("1.0.5", "1.0.7")),
                write_record(d, record_lines(d) + record_lines(d)[:2])),
     "once, together", 1),
    ("an out-of-order record, the older release first",
     lambda d: (fixture(d, versions=("1.0.5", "1.0.7")),
                write_record(d, record_lines(d)[2:] + record_lines(d)[:2])),
     "newest release first", 1),
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
)


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
        fixture(d, versions=("1.0.5", "1.0.7"),
                allow="/old /marketplace.json 302\tthe old URL of the catalog\n")
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
        if lines != [gen_hosted.HEADER, "/old /marketplace.json 302",
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
    count += check_generator(failures)
    if failures:
        for failure in failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {count} recorded cases for the hosted gate and its generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
