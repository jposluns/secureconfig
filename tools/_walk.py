#!/usr/bin/env python3
"""Shared fail-closed enumeration of tracked working-tree files for the gate scanners.

Git supplies paths, as in check_no_placeholders.py; untracked and ignored-only files and
untracked directories are never visited. Git and a readable checkout are required. There
is no filesystem-walk fallback. Callers retain their own content checks and error exits.
"""
# LOCAL PATCH (secureconfig, 2026-09-26): enumerate tracked paths instead of walking directories.
# Modified from AIQT Guardrails ad60d25 under Apache-2.0; see .aiqt/PIN.
import os
import stat
import subprocess
from pathlib import Path


def walk_files(root, skip_dirs=frozenset(), suffixes=None):
    """Yield tracked files under root, with root preserved as supplied by the caller.

    Skip any path component in skip_dirs, including a file basename. Suffix matching is
    case-sensitive. Git lists paths relative to its cwd, including when root is a subtree.
    Directory symlinks and submodule directories are not descended. Missing or inaccessible
    selected paths raise OSError, as do Git failures; callers fail closed on that exception.
    """
    root = Path(root)
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--cached"], cwd=root, check=True,
            capture_output=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise OSError(
            f"cannot list tracked files under {root}: git ls-files requires Git and a "
            f"readable checkout ({exc})"
        ) from exc
    tracked = {Path(os.fsdecode(name)) for name in result.stdout.split(b"\0") if name}
    for relative in sorted(tracked):
        if any(part in skip_dirs for part in relative.parts):
            continue
        if suffixes is not None and relative.suffix not in suffixes:
            continue
        # os.walk did not follow directory symlinks below root. Keep that boundary.
        if any(root.joinpath(*relative.parts[:i]).is_symlink()
               for i in range(1, len(relative.parts))):
            continue
        path = root / relative
        # stat, not is_file/is_dir: inaccessible or missing tracked paths must raise.
        if not stat.S_ISDIR(path.stat().st_mode):
            yield path
