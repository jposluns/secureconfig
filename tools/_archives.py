#!/usr/bin/env python3
"""Build the release's zip archives from the target's own tree, so that two builds of one target
give the same bytes.

The maintainer's OD-1 ruling chose two separate archives (plan-v3 section 1.1). ARCHIVES lists
the archive kinds, so a later kind, such as a combined archive (plan-v3 section 1.11), is a change
to that list and not to the code. Today it lists two:

- the skill zip, `secureconfig-<version>.zip`: every file under `plugin/skills/secureconfig/`
  with that prefix removed, so `SKILL.md` is at the zip's root;
- the plugin zip, `secureconfig-plugin-<version>.zip`: every file under `plugin/` with that
  prefix removed, so the zip's root is the plugin's root.

`<version>` is `VERSION` at the target, `1.0.<N>`, with no `v` and no leading zero in `<N>`, the
names the site build's `--check` admits in `site/downloads/`. No archive name ends in
`-latest.zip`: the latest links are 302 redirects with no bytes of their own, so no build writes
one, and archive_name() refuses one.

The input is the tar stream that `git archive --format=tar <target> plugin` writes, never a
working tree; tools/check_release.py passes it in. Each zip:

- holds file entries only, with no directory entries, sorted by their path in the zip (Python's
  string order);
- dates each entry 1980-01-01 00:00:00, sets its create_system to 3 (Unix), and gives it the
  mode 0644, or 0755 when the tar entry has an execute bit (git records a file as 100644 or
  100755, so that bit is the git mode's);
- compresses each entry with ZIP_DEFLATED at level 9, with no archive comment and no extra
  fields.

A build refuses (ArchiveError) a tar stream it cannot read; a symbolic link, a hard link or any
other entry that is neither a regular file nor a directory; a path that is absolute or holds an
empty, `.` or `..` component; a path given twice; a kind with no file; and a kind whose root file
(`SKILL.md` for the skill, `plugin.json` for the plugin) is missing. The bytes repeat for one
Python and zlib, as the tarball's do.
"""
import io
import re
import stat
import tarfile
import zipfile
from dataclasses import dataclass

# The path tools/check_release.py gives `git archive`; every kind's prefix lies under it.
SOURCE = "plugin"
VERSION_SHAPE = re.compile(r"1\.0\.[1-9][0-9]*")
LATEST_SUFFIX = "-latest.zip"
EPOCH = (1980, 1, 1, 0, 0, 0)
UNIX = 3
FILE_MODE = stat.S_IFREG | 0o644
EXEC_MODE = stat.S_IFREG | 0o755
LEVEL = 9


class ArchiveError(ValueError):
    """A zip could not be built from the tar stream; the message says why."""


@dataclass(frozen=True)
class Kind:
    """One archive kind: its name, with `{version}` for VERSION; the folder in the tar stream it
    holds, ending in `/`; the file its root must hold; and how the release body describes it."""
    template: str
    prefix: str
    root_file: str
    description: str


ARCHIVES = (
    Kind("secureconfig-{version}.zip", "plugin/skills/secureconfig/", "SKILL.md",
         "the skill folder `plugin/skills/secureconfig/` at the target, with `SKILL.md` at the "
         "zip's root"),
    Kind("secureconfig-plugin-{version}.zip", "plugin/", "plugin.json",
         "the `plugin/` folder at the target, with that folder's contents at the zip's root"),
)


def archive_name(kind, version):
    """The kind's file name for version, which is `1.0.<N>`; never a latest name."""
    if not VERSION_SHAPE.fullmatch(version):
        raise ArchiveError(f"the version {version!r} is not 1.0.<N> with ASCII digits and no "
                           "leading zero")
    name = kind.template.format(version=version)
    if name.endswith(LATEST_SUFFIX):
        raise ArchiveError(f"{name} is a latest name; a latest link is a 302 redirect with no "
                           "bytes of its own, so no archive carries one")
    return name


def tree_files(stream):
    """{path: (mode, bytes)} for each regular file in a `git archive --format=tar` stream, the
    mode being FILE_MODE or EXEC_MODE. Directory entries are passed over."""
    files = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(stream), mode="r:") as tar:
            for member in tar:
                path = member.name.rstrip("/") if member.isdir() else member.name
                parts = path.split("/")
                if path.startswith("/") or any(p in ("", ".", "..") for p in parts):
                    raise ArchiveError(f"the tar entry {path!r} is not a plain relative path")
                if member.isdir():
                    continue
                if not member.isfile():
                    raise ArchiveError(f"the tar entry {path!r} is not a regular file (tar type "
                                       f"{member.type!r}); a zip holds regular files only")
                if path in files:
                    raise ArchiveError(f"the tar entry {path!r} appears twice")
                mode = EXEC_MODE if member.mode & 0o111 else FILE_MODE
                files[path] = (mode, tar.extractfile(member).read())
    except tarfile.TarError as exc:
        raise ArchiveError(f"the tar stream cannot be read: {exc}") from exc
    return files


def entries(files, kind):
    """[(path in the zip, mode, bytes)] for kind, sorted by path."""
    picked = sorted((path[len(kind.prefix):], mode, data)
                    for path, (mode, data) in files.items() if path.startswith(kind.prefix))
    if not picked:
        raise ArchiveError(f"the target has no file under {kind.prefix}")
    if kind.root_file not in {path for path, _, _ in picked}:
        raise ArchiveError(f"the target has no {kind.prefix}{kind.root_file}, which the zip "
                           f"needs at its root")
    return picked


def build(files, kind):
    """The zip's bytes for kind from tree_files()'s result."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for path, mode, data in entries(files, kind):
            info = zipfile.ZipInfo(path, date_time=EPOCH)
            info.create_system = UNIX
            info.external_attr = mode << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=LEVEL)
    return out.getvalue()


def build_all(stream, version):
    """[(name, bytes)] for each kind in ARCHIVES, in that order, from one tar stream."""
    names = [archive_name(kind, version) for kind in ARCHIVES]
    files = tree_files(stream)
    return [(name, build(files, kind)) for name, kind in zip(names, ARCHIVES)]
