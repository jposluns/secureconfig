#!/usr/bin/env python3
"""Offline, named regressions for scan_credential.sh; no application is simulated."""
import collections
import gzip
import itertools
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time

TOOL = Path(__file__).with_name("scan_credential.sh").resolve()
KEY = b"QA_DUMMY_LITERAL_450_X9"
F = b"FOUND: remove and rotate credential\n"
N = b"NOT FOUND: no literal credential in stated scope\n"
I = b"INCONCLUSIVE: could not complete scan\n"
CASES = []
COUNTS = collections.Counter()
SKIPS = []
SAMPLING = collections.Counter()
# Test-only hooks, read by this file alone and never by the tool under test:
# FORCE_SKIP skips one named case to exercise the skip policy; BLIND makes
# the /proc sampler ignore Git cmdlines to prove the observation requirement.
FORCE_SKIP = os.environ.get("SCAN_CREDENTIAL_TEST_FORCE_SKIP", "")
BLIND = bool(os.environ.get("SCAN_CREDENTIAL_TEST_BLIND"))


def case(name, category, action):
    CASES.append((name, category, action))


def quoted(path):
    raw = os.fsencode(path)
    if all(32 <= c < 127 and c not in (34, 92) for c in raw):
        return raw + b"\n"
    escapes = {9: b"\\t", 10: b"\\n", 13: b"\\r", 34: b'\\"', 92: b"\\\\"}
    return b'"' + b"".join(
        escapes.get(c, bytes([c]) if 32 <= c < 127 else f"\\{c:03o}".encode())
        for c in raw
    ) + b'"\n'


class Fixture:
    def __init__(self, root, template=None):
        self.root = root
        self.env = {
            "PATH": os.environ["PATH"], "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.com",
            "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.com",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00Z",
        }
        if template is None:
            self.git("init", "-q", "-b", "main")
            self.git("config", "commit.gpgsign", "false")
            self.git("config", "color.ui", "false")
            self.write("dist/app.js", b"clean\n")
            self.write("source", b"clean\n")
            self.git("add", "source")
            self.git("commit", "-qm", "clean")
        else:
            # Fixed dates make the template's base commit identical to a
            # per-case init; every case starts from an unmodified copy.
            shutil.copytree(template, self.root, dirs_exist_ok=True)
        self.base = self.git("rev-parse", "HEAD").strip().decode()

    def git(self, *args, data=None):
        p = subprocess.run(["git", *args], cwd=self.root, env=self.env,
                           input=data, capture_output=True, timeout=30)
        assert p.returncode == 0, (args, p.returncode, p.stderr)
        return p.stdout

    def write(self, path, data):
        p = self.root / path
        assert len(str(p)) < 1000, "fixture path exceeds brief limit"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def commit(self, data=KEY, path="source"):
        self.write(path, data)
        self.git("add", "--", path)
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD").strip().decode()

    def expected_history(self, matches):
        # Git chooses ordering; membership and matching paths are fixture facts.
        commits = self.git("rev-list", "--all", "--reflog").decode().splitlines()
        return b"".join(quoted(c + ":" + p) for c in commits for p in matches.get(c, ()))

    def scan(self, status, stdout, *, key=KEY, data=None, out="dist",
             env=None, before="", args=None, stderr=None):
        command = ["bash", str(TOOL), *(args if args is not None else [out])]
        if before:
            command = ["bash", "-c", before + '\nexec bash "$@"', "fixture",
                       str(TOOL), *(args if args is not None else [out])]
        p = subprocess.run(command, cwd=self.root, env={**self.env, **(env or {})},
                           input=key + b"\n" if data is None else data,
                           capture_output=True, timeout=30)
        assert p.returncode == status, (p.returncode, status, p.stdout, p.stderr)
        assert p.stdout == stdout, (p.stdout, stdout, p.stderr)
        assert key not in p.stdout + p.stderr, "dummy credential disclosed"
        if stderr is not None:
            assert p.stderr == stderr, p.stderr
        return p

    def found(self, **kwargs):
        self.write("dist/app.js", KEY)
        self.scan(1, b"dist/app.js\n" + F, **kwargs)


def bundle(f, key=KEY, content=None, path="app.js"):
    (f.root / "dist/app.js").unlink()
    f.write("dist/" + path, key if content is None else content)
    f.scan(1, quoted("dist/" + path) + F, key=key)


case("untracked bundle", "FOUND", lambda f: f.found())
case("absent key", "NOT FOUND", lambda f: f.scan(0, N, stderr=b""))
for name, key in [
    ("regex", b"a.*[x]$^"), ("leading hyphen", b"-credential"),
    ("spaces", b"two words"), ("backslash", b"a\\b"),
    ("unicode", "cle秘密".encode()), ("trailing space", b"key "),
]:
    case(name, "FOUND", lambda f, k=key: bundle(f, k))
for name, content in [
    ("substring", b"prefix" + KEY + b"suffix"),
    ("binary NUL", b"\0" + KEY + b"\0"),
    ("invalid UTF-8 surroundings", b"\xff" + KEY + b"\xfe"),
    ("CRLF content", KEY + b"\r\n"), ("no final newline", KEY),
]:
    case(name, "FOUND", lambda f, c=content: bundle(f, content=c))
for path in [".hidden", "has space", "line\nbreak", "-app", "a*[b]?",
             "\udcff", ".gitignore", ".github/cfg", ".gitattributes", "x.git", ".git2"]:
    case("filename " + repr(path), "FOUND", lambda f, p=path: bundle(f, path=p))
for name, data in [("empty key", b"\n"), ("EOF", b""), ("unterminated", KEY),
                   ("CRLF key", KEY + b"\r\n"), ("tab key", KEY + b"\t\n")]:
    case(name, "INCONCLUSIVE", lambda f, d=data: f.scan(2, I, data=d))


def ignore(f, where):
    if where == "global":
        f.write("excludes", b"dist/\n")
        f.git("config", "core.excludesFile", str(f.root / "excludes"))
    else:
        f.write(where, b"dist/\n")
    f.found()


for where in [".gitignore", ".git/info/exclude", "global"]:
    case("ignored " + where, "FOUND", lambda f, w=where: ignore(f, w))


def shape(f, kind):
    p = f.root / "dist"
    if kind in ("missing", "file root", "symlink root", "empty", "directories only"):
        shutil.rmtree(p)
        if kind == "file root":
            p.write_bytes(KEY)
        elif kind == "symlink root":
            p.symlink_to("source")
        elif kind != "missing":
            p.mkdir()
            if kind == "directories only":
                (p / "child").mkdir()
    elif kind.startswith("symlink"):
        target = {"symlink file": "../source", "symlink directory": "..",
                  "symlink dangling": "absent"}[kind]
        (p / "link").symlink_to(target)
    elif kind == "FIFO":
        os.mkfifo(p / "fifo")
    elif kind == "socket":
        with socket.socket(socket.AF_UNIX) as s:
            try:
                s.bind(str(p / "socket"))
            except PermissionError as e:
                raise unittest_skip("unix-socket-bind-refused", str(e))
    f.scan(2, I)


class unittest_skip(Exception):
    """An environmental impossibility, allowed only per ALLOWED_SKIPS."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


for kind in ["missing", "file root", "symlink root", "empty", "directories only",
             "symlink file", "symlink directory", "symlink dangling", "FIFO", "socket"]:
    case(kind, "INCONCLUSIVE", lambda f, k=kind: shape(f, k))


def denied(f, kind, mode):
    p = f.write("dist/locked/file", KEY) if kind == "directory" else f.root / "dist/app.js"
    if kind == "directory":
        p = p.parent
    p.chmod(mode)
    try:
        if os.access(p, os.R_OK) and (kind != "directory" or os.access(p, os.X_OK)):
            raise unittest_skip("privileged-uid-reads-everything",
                                "permission denial unavailable for this uid")
        f.scan(2, I)
    finally:
        p.chmod(0o700 if kind == "directory" else 0o600)


for kind, mode in [("file", 0), ("directory", 0), ("directory", 0o600)]:
    case(f"unreadable {kind} {mode:o}", "INCONCLUSIVE",
         lambda f, k=kind, m=mode: denied(f, k, m))
for chars in itertools.product(*["gG", "iI", "tT"]):
    spelling = "." + "".join(chars)
    for depth, directory in itertools.product(("", "nested/"), (False, True)):
        def dotgit(f, s=spelling, d=depth, isdir=directory):
            p = f.root / "dist" / d / s
            p.parent.mkdir(parents=True, exist_ok=True)
            if isdir:
                p.mkdir()
                (p / "secret").write_bytes(KEY)
            else:
                p.write_bytes(KEY)
            f.git("config", "core.ignoreCase", "true")
            f.scan(2, I)
        case(f"dotgit {depth}{spelling} {'directory' if directory else 'file'}",
             "INCONCLUSIVE", dotgit)


def nested(f, kind):
    if kind == "repository":
        f.git("init", "-q", "dist/nested")
    else:
        f.write("dist/module/.git", b"gitdir: ../../.git/modules/module\n")
    f.scan(2, I)


for kind in ("repository", "gitfile"):
    case("nested " + kind, "INCONCLUSIVE", lambda f, k=kind: nested(f, k))
for out in (".", ".git", ".git/objects", "dist/../dist", "/tmp", ""):
    case("refuse output " + repr(out), "INCONCLUSIVE",
         lambda f, o=out: f.scan(2, I, out=o))


def output_path(f, path):
    (f.root / "dist").rename(f.root / path)
    f.write(path + "/app.js", KEY)
    f.scan(1, quoted(path + "/app.js") + F, out=path)


for path in ["has space", "[dist]", "*", "?", ":", ":(exclude)"]:
    case("literal output path " + path, "FOUND", lambda f, p=path: output_path(f, p))


def history(f, kind):
    h = f.commit()
    f.git("reset", "--hard", f.base)
    if kind == "old commit":
        f.git("reset", "--hard", h)
        f.commit(b"clean again")
    elif kind == "branch":
        f.git("branch", "other", h)
    elif kind in ("tag", "annotated tag"):
        f.git("tag", *(["-a", "-m", "fixture"] if kind == "annotated tag" else []), "saved", h)
    elif kind in ("notes ref", "namespace ref", "worktree ref", "replace ref"):
        ref = {"notes ref": "refs/notes/fixture", "namespace ref": "refs/namespaces/x/refs/heads/main",
               "worktree ref": "refs/worktree/fixture", "replace ref": "refs/replace/" + f.base}[kind]
        f.git("update-ref", ref, h)
    if kind not in ("reflog only", "old commit", "replace ref"):
        f.git("reflog", "expire", "--expire=all", "--all")
    matches = {h: ["source"]}
    if kind == "replace ref":
        matches[f.base] = ["source"]
    f.scan(1, f.expected_history(matches) + F)


for kind in ["old commit", "reflog only", "branch", "tag", "annotated tag",
             "notes ref", "namespace ref", "worktree ref", "replace ref"]:
    case(kind, "FOUND", lambda f, k=kind: history(f, k))


def stash(f, kind):
    path = "untracked" if kind == "untracked" else "source"
    f.write(path, KEY)
    if kind == "staged":
        f.git("add", path)
    f.git("stash", "push", "-q", *(["-u"] if kind == "untracked" else []))
    f.write("dist/app.js", b"clean\n")
    h = f.git("rev-parse", "refs/stash").strip().decode()
    matches = {h: [path]} if kind != "untracked" else {}
    if kind in ("staged", "untracked"):
        parent = f.git("rev-parse", h + ("^2" if kind == "staged" else "^3")).strip().decode()
        matches[parent] = [path]
    f.scan(1, f.expected_history(matches) + F)


for kind in ["staged", "unstaged", "untracked"]:
    case("stash " + kind, "FOUND", lambda f, k=kind: stash(f, k))


def corruption(f, kind, match=False):
    f.commit()
    blob = f.git("rev-parse", "HEAD:source").strip().decode()
    p = f.root / ".git/objects" / blob[:2] / blob[2:]
    if kind == "missing":
        p.unlink()
    elif kind == "corrupt":
        p.chmod(0o600)
        p.write_bytes(b"bad object")
    else:
        f.write(".git/refs/heads/broken", b"1" * 40 + b"\n")
    if match:
        f.write("dist/app.js", KEY)
    f.scan(2, (b"dist/app.js\n" if match and kind != "broken ref" else b"") + I)


for kind in ["missing", "corrupt", "broken ref"]:
    case(kind + " object", "INCONCLUSIVE", lambda f, k=kind: corruption(f, k))
case("bundle match then corrupt blob", "INCONCLUSIVE", lambda f: corruption(f, "corrupt", True))


def mode(f, mode):
    blob = f.git("hash-object", "-w", "--stdin", data=KEY).strip()
    tree = f.git("hash-object", "--literally", "-w", "-t", "tree", "--stdin",
                 data=mode.encode() + b" regular\0" + bytes.fromhex(blob.decode())).strip()
    h = f.git("commit-tree", tree.decode(), "-m", "raw").strip().decode()
    f.git("update-ref", "refs/heads/raw", h)
    f.scan(1, quoted(h + ":regular") + F)


for m in ["100644", "100755", "100664", "100600", "100645"]:
    case("regular mode " + m, "FOUND", lambda f, m=m: mode(f, m))


def replacement(f, supplies):
    h = f.commit(b"clean old" if supplies else KEY)
    original = f.git("rev-parse", "HEAD:source").strip().decode()
    new = f.git("hash-object", "-w", "--stdin", data=KEY if supplies else b"clean").strip().decode()
    f.git("replace", original, new)
    f.scan(1 if supplies else 0, quoted(h + ":source") + F if supplies else N)


case("replacement supplies key", "FOUND", lambda f: replacement(f, True))
case("documented limit: original hidden by replacement", "LIMIT", lambda f: replacement(f, False))


def limit(f, kind):
    if kind == "gzip-only":
        f.write("dist/app.js", gzip.compress(KEY, mtime=0))
    elif kind == "committed symlink target":
        (f.root / "link").symlink_to(KEY.decode())
        f.git("add", "link")
        f.git("commit", "-qm", "link")
    elif kind == "tag points to blob":
        blob = f.git("hash-object", "-w", "--stdin", data=KEY).strip().decode()
        f.git("tag", "blob", blob)
    elif kind == "submodule":
        h = f.commit()
        f.git("reset", "--hard", f.base)
        f.git("reflog", "expire", "--expire=all", "--all")
        f.git("update-index", "--add", "--cacheinfo", "160000," + h + ",module")
        f.git("commit", "-qm", "gitlink")
    elif kind == "shallow history":
        f.commit()
        h = f.commit(b"clean")
        f.write(".git/shallow", h.encode() + b"\n")
        f.git("reflog", "expire", "--expire=all", "--all")
    elif kind in ("unreachable object", "expired reflog"):
        f.commit()
        f.git("reset", "--hard", f.base)
        f.git("reflog", "expire", "--expire=all", "--all")
    elif kind == "graft hidden ancestry":
        f.commit()
        h = f.commit(b"clean")
        f.git("replace", "--graft", h)
        f.git("reflog", "expire", "--expire=all", "--all")
    elif kind == "UTF-16":
        f.write("dist/app.js", KEY.decode().encode("utf-16"))
    elif kind == "split key":
        f.write("dist/app.js", KEY[:10] + b"\n" + KEY[10:])
    elif kind == "escaped key":
        f.write("dist/app.js", b"".join(f"\\x{b:02x}".encode() for b in KEY))
    elif kind == "runtime injection":
        f.write("dist/app.js", b"window.key = process.env.ADMIN_KEY;")
    elif kind == "LFS payload":
        f.write(".git/lfs/objects/payload", KEY)
        f.commit(b"version https://git-lfs.github.com/spec/v1\noid sha256:" + b"0" * 64 + b"\nsize 23\n")
    f.scan(0, N)


for kind in ["gzip-only", "committed symlink target", "tag points to blob", "submodule",
             "shallow history", "unreachable object", "expired reflog", "graft hidden ancestry",
             "UTF-16", "split key", "escaped key", "runtime injection", "LFS payload"]:
    case("documented limit: " + kind, "LIMIT", lambda f, k=kind: limit(f, k))


# A fresh invoked Bash deliberately changes the old pasted-shell outcomes.
for before in [
    "enable -n printf", "alias printf=false", "alias read=false", "alias git=false",
    "declare -n key=target", "readonly key=old", "declare -rn key=target",
    "export key=old", "declare -i key=8", "readonly IFS", "IFS=x",
    "GLOBIGNORE='*'", "set -o posix", "export POSIXLY_CORRECT=1",
    "set -e", "set -u", "set -f", "shopt -s failglob", "set -o pipefail",
    "shopt -s nocasematch", "set -ax", "GIT_DIR=elsewhere",
    "readonly GIT_DIR=elsewhere", "declare -n GIT_DIR=target",
    "declare -rn GIT_DIR=target", "declare -a GIT_DIR=(x)",
    "declare -A GIT_=([x]=y)",
]:
    case("parent shell " + before, "FOUND", lambda f, b=before: f.found(before=b))
for name in ["printf", "read", "git"]:
    case("exported function " + name, "FOUND",
         lambda f, n=name: f.found(before=n + '() { return 99; }; export -f ' + n))
case("exported compgen function", "INCONCLUSIVE",
     lambda f: f.scan(2, I, before="compgen() { return 99; }; export -f compgen"))
case("BASH_ENV refusal", "INCONCLUSIVE", lambda f: f.scan(2, I, env={"BASH_ENV": "/dev/null"}))


def git_environment(f, variable):
    h = f.commit()
    f.scan(1, quoted(h + ":source") + F, env={variable: "invalid-override"})


for variable in [
    "GIT_", "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_INDEX_FILE",
    "GIT_CEILING_DIRECTORIES", "GIT_TRACE", "GIT_PAGER", "GIT_NO_REPLACE_OBJECTS",
    "GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_ICASE_PATHSPECS",
    "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_GLOBAL", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0",
]:
    case("environment " + variable, "FOUND", lambda f, v=variable: git_environment(f, v))


def configuration(f, setting, value):
    f.git("config", setting, value)
    f.found()


for setting, value in [
    ("grep.lineNumber", "true"), ("grep.column", "true"),
    ("grep.patternType", "extended"), ("grep.extendedRegexp", "true"),
    ("grep.fullName", "true"), ("grep.threads", "2"), ("grep.fallbackToNoIndex", "true"),
    ("pager.grep", "true"), ("core.quotePath", "false"), ("core.ignoreCase", "true"),
    ("core.bigFileThreshold", "1"), ("core.pager", "false"),
]:
    case("configuration " + setting, "FOUND",
         lambda f, s=setting, v=value: configuration(f, s, v))


def attributes(f, value):
    f.write(".gitattributes", ("* " + value + "\n").encode())
    f.git("config", "diff.fixture.textconv", "false")
    f.git("config", "filter.fixture.clean", "cat")
    f.git("config", "filter.fixture.smudge", "cat")
    f.found()


for value in ["-text", "binary", "export-ignore", "-diff", "diff=fixture",
              "filter=fixture", "working-tree-encoding=UTF-16"]:
    case("attributes " + value, "FOUND", lambda f, v=value: attributes(f, v))


def index_flag(f, flag):
    f.git("add", "-f", "dist/app.js")
    f.git("commit", "-qm", "clean output")
    f.git("update-index", flag, "dist/app.js")
    f.found()


for flag in ["--skip-worktree", "--assume-unchanged"]:
    case(flag, "FOUND", lambda f, flag=flag: index_flag(f, flag))


def wide(f, depth, count):
    for i in range(count):
        f.write(f"dist/f{i:05}", b"clean")
    bundle(f, path="d/" * depth + "zzsecret")


for depth, count in [(160, 0), (60, 2000), (0, 5000), (0, 12000)]:
    case(f"tree depth={depth} files={count}", "FOUND",
         lambda f, d=depth, n=count: wide(f, d, n))
for n in [150, 151]:
    def many_commits(f, n=n):
        tree = f.git("rev-parse", "HEAD^{tree}").strip().decode()
        h = f.base
        for i in range(n - 1):
            h = f.git("commit-tree", tree, "-p", h, "-m", str(i)).strip().decode()
        f.git("update-ref", "refs/heads/main", h)
        f.scan(0, N)
    case(f"{n} clean commits", "NOT FOUND", many_commits)


def repo_shape(f, kind):
    if kind == "non-repository":
        shutil.rmtree(f.root / ".git")
        f.scan(2, I)
    elif kind == "empty repository":
        f.git("update-ref", "-d", "refs/heads/main")
        f.git("reflog", "expire", "--expire=all", "--all")
        f.scan(0, N)
    elif kind == "below root":
        old = f.root
        f.root = old / "dist"
        try:
            f.scan(2, I, out=".")
        finally:
            f.root = old
    elif kind == "bare with bundle":
        f.git("config", "core.bare", "true")
        f.found()
    elif kind == "bare without bundle":
        f.git("config", "core.bare", "true")
        shutil.rmtree(f.root / "dist")
        f.scan(2, I)
    else:
        if kind == "detached":
            f.git("checkout", "--detach", "-q")
        elif kind == "packed refs":
            f.git("pack-refs", "--all")
        elif kind == "no reflogs":
            f.git("reflog", "expire", "--expire=all", "--all")
        f.scan(0, N)


for kind in ["non-repository", "below root", "bare without bundle"]:
    case(kind, "INCONCLUSIVE", lambda f, k=kind: repo_shape(f, k))
case("bare with bundle", "FOUND", lambda f: repo_shape(f, "bare with bundle"))
for kind in ["empty repository", "detached", "packed refs", "no reflogs"]:
    case(kind, "NOT FOUND", lambda f, k=kind: repo_shape(f, k))


def warning(f, match):
    if match:
        f.write("dist/app.js", KEY)
    f.git("config", "core.fsync", "invalid")
    f.scan(2, I, stderr=b"")


case("Git warning clean", "INCONCLUSIVE", lambda f: warning(f, False))
case("Git warning matching", "INCONCLUSIVE", lambda f: warning(f, True))


def explain(f, bad):
    if bad:
        (f.root / "dist/link").symlink_to("../source")
    f.scan(2 if bad else 0,
           I + b"CHECK: output-entry\n" if bad else
           b"READY: prerequisites passed; no key read and no content searched\n",
           args=["--explain", "dist"], data=b"")


case("explain refusal without key", "CHECK", lambda f: explain(f, True))
case("explain success without key", "CHECK", lambda f: explain(f, False))


def source_refusal(f):
    p = subprocess.run(["bash", "-c", 'source "$1" dist', "fixture", str(TOOL)],
                       cwd=f.root, env=f.env, input=KEY + b"\n", capture_output=True)
    assert (p.returncode, p.stdout, p.stderr) == (2, I, b"")


case("sourced refusal", "INCONCLUSIVE", source_refusal)


def storage(f, kind):
    h = f.commit()
    if kind == "packed objects":
        f.git("gc", "--quiet")
    elif kind == "valid alternates":
        store = f.root / "store"
        shutil.copytree(f.root / ".git/objects", store)
        shutil.rmtree(f.root / ".git/objects")
        (f.root / ".git/objects/info").mkdir(parents=True)
        f.write(".git/objects/info/alternates", os.fsencode(store) + b"\n")
    elif kind == "broken alternates":
        f.write(".git/objects/info/alternates", os.fsencode(f.root / "absent") + b"\n")
        f.scan(2, I)
        return
    elif kind == "packed refs positive":
        f.git("pack-refs", "--all")
    elif kind == "no reflogs positive":
        f.git("reflog", "expire", "--expire=all", "--all")
    f.scan(1, quoted(h + ":source") + F)


for kind in ["packed objects", "valid alternates", "broken alternates",
             "packed refs positive", "no reflogs positive"]:
    case(kind, "INCONCLUSIVE" if kind == "broken alternates" else "FOUND",
         lambda f, k=kind: storage(f, k))


def sparse(f, sparse_index):
    h = f.commit(path="outside/secret")
    f.git("sparse-checkout", "init", "--cone", *(["--sparse-index"] if sparse_index else []))
    f.git("sparse-checkout", "set", "inside")
    f.write("dist/app.js", KEY)
    f.scan(1, b"dist/app.js\n" + quoted(h + ":outside/secret") + F)


for indexed in (False, True):
    case(f"sparse output and history index={indexed}", "FOUND",
         lambda f, i=indexed: sparse(f, i))


def linked(f, other_ref):
    work = f.root / "linked"
    f.git("worktree", "add", "-q", "--detach", str(work), f.base)
    if other_ref:
        h = f.commit()
        f.git("reset", "--hard", f.base)
        f.git("reflog", "expire", "--expire=all", "--all")
        f.git("-C", str(work), "update-ref", "refs/worktree/private", h)
        f.scan(0, N)
    else:
        h = f.commit()
        f.git("-C", str(work), "reset", "--hard", h)
        f.write("linked/dist/app.js", KEY)
        root = f.root
        f.root = work
        try:
            f.scan(1, b"dist/app.js\n" + quoted(h + ":source") + F)
        finally:
            f.root = root


case("linked worktree", "FOUND", lambda f: linked(f, False))
case("documented limit: other worktree private ref", "LIMIT", lambda f: linked(f, True))


def special_history(f, path):
    blob = f.git("hash-object", "-w", "--stdin", data=KEY).strip().decode()
    if "/" in path:
        parent, leaf = path.split("/")
        tree = f.git("hash-object", "--literally", "-w", "-t", "tree", "--stdin",
                     data=b"100644 " + leaf.encode() + b"\0" + bytes.fromhex(blob)).strip()
        raw = b"40000 " + parent.encode() + b"\0" + bytes.fromhex(tree.decode())
    else:
        raw = b"100644 " + path.encode() + b"\0" + bytes.fromhex(blob)
    tree = f.git("hash-object", "--literally", "-w", "-t", "tree", "--stdin", data=raw).strip()
    h = f.git("commit-tree", tree.decode(), "-m", "special").strip().decode()
    f.git("update-ref", "refs/heads/special", h)
    f.scan(1, quoted(h + ":" + path) + F)


for path in [".git/keyfile", ".GIT/keyfile", ".git"]:
    case("historical " + path, "FOUND", lambda f, p=path: special_history(f, p))


def binary_history(f, size=0):
    h = f.commit(b"\0" + b"x" * size + KEY + b"\0")
    f.scan(1, quoted(h + ":source") + F)


case("binary history", "FOUND", binary_history)
case("64MiB history", "FOUND", lambda f: binary_history(f, 64 * 1024 * 1024))
case("64MiB output", "FOUND",
     lambda f: bundle(f, content=b"x" * (64 * 1024 * 1024) + KEY))
case("64MiB binary output", "FOUND",
     lambda f: bundle(f, content=b"\0" + b"x" * (64 * 1024 * 1024) + KEY))


def hardlink(f):
    f.write("outside", KEY)
    os.link(f.root / "outside", f.root / "dist/link")
    f.scan(1, b"dist/link\n" + F)


case("hard link", "FOUND", hardlink)


def nested_bare(f):
    f.git("init", "--bare", "-q", "dist/bare")
    f.write("dist/bare/secret", KEY)
    f.scan(1, b"dist/bare/secret\n" + F)


case("nested bare repository", "FOUND", nested_bare)


def gitlink_output(f):
    f.git("update-index", "--add", "--cacheinfo", "160000," + f.base + ",dist/module")
    f.git("commit", "-qm", "module")
    f.write("dist/module/app.js", KEY)
    f.scan(1, b"dist/module/app.js\n" + F)


case("gitlink output without gitfile", "FOUND", gitlink_output)


def partial(f, available):
    f.git("config", "uploadpack.allowFilter", "true")
    h = f.commit()
    clone = f.root / "partial"
    f.git("clone", "-q", "--no-checkout", "--filter=blob:none",
          "file://" + str(f.root), str(clone))
    root = f.root
    f.root = clone
    try:
        f.write("dist/app.js", b"clean")
        if not available:
            f.git("remote", "set-url", "origin", "file://" + str(root / "missing"))
        f.scan(1 if available else 2, quoted(h + ":source") + F if available else I)
    finally:
        f.root = root


case("local promisor available", "FOUND", lambda f: partial(f, True))
case("local promisor unavailable", "INCONCLUSIVE", lambda f: partial(f, False))


def wrapper(f, body):
    real = shutil.which("git")
    path = f.write("bin/git", ("#!/usr/bin/env bash\n" + body +
                              '\nexec "' + real + '" "$@"\n').encode())
    path.chmod(0o700)
    return {"PATH": str(path.parent) + ":" + f.env["PATH"]}


def injected(f, stage, status, diagnostic):
    # Fault injection into an external Git executable, never a production stub.
    # All normal operations delegate to real Git; the labelled stage is replaced.
    if stage == "history":
        f.commit()
    condition = {
        "rev-list": '[[ $3 == rev-list ]]',
        "output": '[[ $3 == grep && $4 == --no-index ]]',
        "history": '[[ $3 == grep && $4 != --no-index ]]',
    }[stage]
    emit = "printf '" + diagnostic + "' >&2" if diagnostic else ":"
    env = wrapper(f, "if " + condition + "; then\n" + emit +
                  "\nexit " + str(status) + "\nfi")
    f.scan(2, I, env=env, stderr=b"")


for stage in ("rev-list", "output", "history"):
    for status, diagnostic in [(0, "\\n"), (1, "\\0"), (2, ""), (129, ""),
                               (0, "warning"), (1, "warning")]:
        case(f"fault {stage} status={status} diagnostic={diagnostic!r}", "INCONCLUSIVE",
             lambda f, s=stage, r=status, d=diagnostic: injected(f, s, r, d))


def failed_producer(f):
    env = wrapper(f, 'if [[ $3 == grep ]]; then exit 0; fi')
    f.scan(2, I, key=b"Q" * 131072, env=env, stderr=b"")


case("failed pattern producer", "INCONCLUSIVE", failed_producer)


def race(f):
    env = wrapper(f, 'if [[ $3 == grep && $4 == --no-index ]]; then\n'
                  'rm -f dist/app.js\nln -s ../source dist/app.js\nfi')
    f.write("dist/app.js", KEY)
    f.scan(0, N, env=env)


case("documented limit: changed file after walk", "LIMIT", race)


def terminal(f, setting):
    import pty
    if setting == "core.pager":
        f.git("config", "core.pager", "printf pager-warning >&2")
    if setting == "pager.grep":
        f.git("config", "pager.grep", "printf pager-warning >&2")
    f.write("dist/app.js", KEY)
    try:
        master, slave = pty.openpty()
    except OSError as exc:
        raise unittest_skip("pty-unavailable", str(exc))
    env = {**f.env, "TERM": "dumb" if setting == "TERM=dumb" else "xterm",
           "PAGER": "printf pager-warning >&2", "GIT_PAGER": "printf pager-warning >&2"}
    try:
        p = subprocess.Popen(["bash", str(TOOL), "dist"], cwd=f.root, env=env,
                             stdin=subprocess.PIPE, stdout=slave, stderr=subprocess.PIPE)
        os.close(slave)
        _, err = p.communicate(KEY + b"\n", timeout=30)
        output = b""
        try:
            while True:
                chunk = os.read(master, 4096)
                if not chunk:
                    break
                output += chunk
        except OSError:
            pass  # Linux PTYs report EIO after the slave closes.
        assert (p.returncode, output, err) == (1, (b"dist/app.js\n" + F).replace(b"\n", b"\r\n"), b"")
        assert KEY not in output + err
    finally:
        os.close(master)


for setting in ["TERM=dumb", "core.pager", "pager.grep", "PAGER", "GIT_PAGER"]:
    case("terminal " + setting, "FOUND", lambda f, s=setting: terminal(f, s))


def environment_pair(f, correct):
    h = f.commit()
    target = str(f.root) if correct else str(f.root / "other")
    f.scan(1, quoted(h + ":source") + F,
           env={"GIT_DIR": target + "/.git", "GIT_WORK_TREE": target,
                "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.bare",
                "GIT_CONFIG_VALUE_0": "true"})


case("correct Git environment with config injection", "FOUND", lambda f: environment_pair(f, True))
case("other Git environment with config injection", "FOUND", lambda f: environment_pair(f, False))


def parent_symlink(f):
    (f.root / "alias").symlink_to("dist")
    f.scan(2, I, out="alias/")


case("symlink root trailing slash", "INCONCLUSIVE", parent_symlink)
case("changed case absent", "NOT FOUND",
     lambda f: (f.write("dist/app.js", KEY.lower()), f.scan(0, N)))
case("locale C.UTF-8", "FOUND", lambda f: f.found(env={"LC_ALL": "C.UTF-8"}))

def historical_attributes(f):
    f.write(".gitattributes", b"source binary -text export-ignore diff=fixture\n")
    f.git("config", "diff.fixture.textconv", "false")
    f.git("add", ".gitattributes")
    h = f.commit()
    f.scan(1, quoted(h + ":source") + F)


case("historical attributes and textconv", "FOUND", historical_attributes)


def transcoded(f):
    f.write(".gitattributes", b"source working-tree-encoding=UTF-16\n")
    f.git("add", ".gitattributes")
    h = f.commit(KEY.decode().encode("utf-16"))
    f.scan(1, quoted(h + ":source") + F)


case("transcoded historical content", "FOUND", transcoded)


def startup(f, content):
    p = f.write("startup", content.encode())
    f.scan(2, I, env={"BASH_ENV": str(p)})


for content in ["readonly GIT_DIR=bad\n", "readonly key=old\n",
                "enable -n compgen\n", "shopt -s expand_aliases\nalias compgen=false\n"]:
    case("startup refusal " + content.strip(), "INCONCLUSIVE",
         lambda f, c=content: startup(f, c))
for before in ["set -ax; export SHELLOPTS", "shopt -s failglob; export BASHOPTS",
               "enable -n compgen", "alias compgen=false", "export IFS=x",
               "export GLOBIGNORE='*'", "export GIT_=value"]:
    case("inherited shell " + before, "FOUND", lambda f, b=before: f.found(before=b))


def sampled_scan(f, before, extra):
    """Deepen the history by `extra` commits, run one scan, sample /proc."""
    tree = f.git("rev-parse", "HEAD^{tree}").strip().decode()
    h = f.git("rev-parse", "HEAD").strip().decode()
    for i in range(extra):
        h = f.git("commit-tree", tree, "-p", h, "-m", str(i)).strip().decode()
    f.git("update-ref", "refs/heads/main", h)
    cmd = ["bash", "-c", before + '\nexec bash "$@"', "fixture", str(TOOL), "dist"]
    p = subprocess.Popen(cmd, cwd=f.root, env=f.env, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stats = collections.Counter()
    git_child = False
    try:
        p.stdin.write(KEY + b"\n")
        p.stdin.close()
        p.stdin = None
        until = time.monotonic() + 60
        while p.poll() is None:
            assert time.monotonic() < until, "sampling timed out"
            pending = [p.pid]
            while pending:
                pid = pending.pop()
                base = Path("/proc") / str(pid)
                try:
                    pending.extend(map(int, (base / "task" / str(pid) / "children").read_text().split()))
                except (FileNotFoundError, ProcessLookupError, PermissionError):
                    pass
                is_git = False
                for channel in ("cmdline", "environ"):
                    try:
                        data = (base / channel).read_bytes()
                    except (FileNotFoundError, ProcessLookupError):
                        continue
                    except PermissionError:
                        # The kernel refuses these reads briefly around fork
                        # and exec, same user or not: a missed sample.
                        stats["denied"] += 1
                        continue
                    assert KEY not in data, "dummy in process argv/environment"
                    stats[channel] += 1
                    if channel == "cmdline" and b"--no-pager\0" in data and not BLIND:
                        is_git = True
                    elif channel == "environ" and is_git:
                        git_child = True
        out, err = p.communicate(timeout=5)
        assert (p.returncode, out) == (0, N), (p.returncode, out, err)
        assert KEY not in out + err
    finally:
        if p.poll() is None:
            p.kill()
            p.communicate()
    return stats, git_child


def memory_channels(f, before):
    # Guards the round-1 blocking defect: the key must never appear in the
    # argv or environment of the scanner or any child. Sampling is bounded,
    # not proof against between-sample exposure or process-memory access.
    # One denied read is a missed sample, never a skip; the case passes only
    # after a successful cmdline read and a successful environ read of the
    # Git child (its cmdline carries --no-pager). A quick scan can finish
    # before the sampler catches that child, so the case retries on a deeper
    # fixture, bounded at three attempts of 20, 80 and 320 cumulative
    # commits: each commit adds one per-commit `git grep` child, so the last
    # attempt keeps spawning them long enough for any machine that can look.
    if not Path("/proc/self/cmdline").exists():
        raise unittest_skip("proc-unavailable", "/proc process inspection unavailable")
    totals = collections.Counter()
    attempts = (20,) if BLIND else (20, 60, 240)
    for extra in attempts:
        stats, git_child = sampled_scan(f, before, extra)
        totals.update(stats)
        if totals["cmdline"] and git_child:
            SAMPLING.update(totals)
            return
    SAMPLING.update(totals)
    if not totals["environ"]:
        raise unittest_skip(
            "proc-environ-unread",
            "no environ read of any process succeeded in the whole case "
            f"({totals['denied']} denied, {totals['cmdline']} cmdline reads)")
    raise AssertionError(
        f"sampling never observed the Git child after {len(attempts)} attempts "
        f"({sum(attempts)} cumulative commits): {dict(totals)}")


for label, before in [
    ("normal", ":"), ("disabled printf", "enable -n printf"),
    ("printf function", "printf() { return 99; }; export -f printf"),
    ("read function", "read() { return 99; }; export -f read"),
    ("git function", "git() { return 99; }; export -f git"),
    ("printf alias", "alias printf=false"), ("read alias", "alias read=false"),
    ("git alias", "alias git=false"), ("exported key", "export key=old"),
    ("nameref key", "declare -n key=other"),
    ("inherited allexport", "set -a; export SHELLOPTS"),
]:
    case("process sampling " + label, "CHECK", lambda f, b=before: memory_channels(f, b))


def terminal_read(f, interrupt=False):
    import pty
    import signal
    import termios
    try:
        master, slave = pty.openpty()
    except OSError as exc:
        raise unittest_skip("pty-unavailable", str(exc))
    f.write("dist/app.js", KEY)
    p = subprocess.Popen(["bash", str(TOOL), "dist"], cwd=f.root, env=f.env,
                         stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        until = time.monotonic() + 5
        while termios.tcgetattr(slave)[3] & termios.ECHO:
            assert p.poll() is None and time.monotonic() < until, "silent read not reached"
            time.sleep(0.001)
        if interrupt:
            p.send_signal(signal.SIGINT)
        else:
            os.write(master, KEY + b"\n")
        out, err = p.communicate(timeout=5)
        assert (p.returncode, out, err) == ((2, I, b"") if interrupt else
                                           (1, b"dist/app.js\n" + F, b""))
        os.set_blocking(master, False)
        try:
            echoed = os.read(master, 4096)
        except BlockingIOError:
            echoed = b""
        assert KEY not in out + err + echoed
    finally:
        if p.poll() is None:
            p.kill()
            p.communicate()
        os.close(slave)
        os.close(master)


case("silent terminal input", "FOUND", terminal_read)
case("interrupt during read", "INCONCLUSIVE", lambda f: terminal_read(f, True))


def private_tmp(f):
    tmp = f.root / "private-tmp"
    tmp.mkdir()
    f.found(env={"TMPDIR": str(tmp)})
    assert list(tmp.iterdir()) == []


case("no temporary key file", "CHECK", private_tmp)

def colored(f):
    f.git("config", "color.grep", "always")
    f.git("config", "color.grep.filename", "magenta")
    f.write("dist/app.js", KEY)
    f.scan(1, b"\x1b[35mdist/app.js\x1b[m\n" + F)


case("colored names", "FOUND", colored)


def blob_tag_no_commits(f):
    blob = f.git("hash-object", "-w", "--stdin", data=KEY).strip().decode()
    f.git("tag", "blob", blob)
    f.git("update-ref", "-d", "refs/heads/main")
    f.git("reflog", "expire", "--expire=all", "--all")
    f.scan(0, N)


case("documented limit: blob tag without commits", "LIMIT", blob_tag_no_commits)

def brotli_limit(f):
    # Brotli quality 11, window 22, KEY repeated 100 times. Encoder/decoder
    # round-trip checked when authored; runtime needs no Brotli dependency.
    compressed = bytes.fromhex(
        "1bfb08f8453717ab418351d02068507ef8d3e2c230a19f000063f0dbfd517962adc042780a"
    )
    assert KEY not in compressed
    f.write("dist/app.js", compressed)
    f.scan(0, N)


case("documented limit: Brotli-only", "LIMIT", brotli_limit)


def unfetched(f):
    h = f.commit()
    f.git("branch", "private", h)
    f.git("reset", "--hard", f.base)
    clone = f.root / "single"
    f.git("clone", "-q", "--single-branch", "--branch", "main",
          "file://" + str(f.root), str(clone))
    root = f.root
    f.root = clone
    try:
        f.write("dist/app.js", b"clean")
        f.scan(0, N)
    finally:
        f.root = root


case("documented limit: unfetched branch", "LIMIT", unfetched)
case("rev-list nonzero without diagnostic", "INCONCLUSIVE",
     lambda f: injected(f, "rev-list", 1, ""))


def hostile_executable(f):
    # Sixth limits bullet: stdin keeps the key out of argv and of files the
    # tool creates, but it cannot protect the key from a hostile executable
    # inside the trust boundary; a wrapping git captures its grep stdin.
    real = shutil.which("git")
    env = wrapper(f, 'if [[ $3 == grep ]]; then\ncat > captured\n'
                  'exec "' + real + '" "$@" < captured\nfi')
    f.scan(0, N, env=env)
    assert (f.root / "captured").read_bytes() == KEY + b"\n", "key not captured"


case("documented limit: hostile executable captures key", "LIMIT", hostile_executable)


def explain_stdin(f):
    # --explain must not consume stdin: run it with the key waiting there,
    # and require the key absent from output and still unread afterwards.
    r, w = os.pipe()
    try:
        os.write(w, KEY + b"\n")
        p = subprocess.run(["bash", str(TOOL), "--explain", "dist"], cwd=f.root,
                           env=f.env, stdin=r, capture_output=True, timeout=30)
        ready = b"READY: prerequisites passed; no key read and no content searched\n"
        assert (p.returncode, p.stdout, p.stderr) == (0, ready, b""), (
            p.returncode, p.stdout, p.stderr)
        assert KEY not in p.stdout + p.stderr
        os.set_blocking(r, False)
        assert os.read(r, 4096) == KEY + b"\n", "--explain consumed stdin"
    finally:
        os.close(r)
        os.close(w)


case("explain ignores stdin", "CHECK", explain_stdin)


def old_bash(f):
    # BASH_VERSINFO is readonly, so a current Bash cannot impersonate an
    # older one; this stub pins the guard text in the tool and evaluates the
    # same expression under substituted versions. A failed guard reaches
    # scan_fail, whose INCONCLUSIVE/2 contract the refusal cases observe.
    guard = ("(( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && "
             "BASH_VERSINFO[1] >= 3) )) ||\n    scan_fail bash-version")
    assert guard in TOOL.read_text(), "version guard changed; update this stub"
    expression = guard.rsplit(" ||", 1)[0].replace("BASH_VERSINFO", "V")
    for major, minor, new_enough in [(3, 2, False), (4, 2, False),
                                     (4, 3, True), (5, 0, True)]:
        p = subprocess.run(["bash", "-c", f"V=({major} {minor}); {expression}"],
                           capture_output=True, timeout=30)
        assert (p.returncode == 0) == new_enough, (major, minor, p.returncode)


case("older Bash refusal", "CHECK", old_bash)


def skip_policy(f):
    # Hermetic self-tests of the undeclared-skip rule via the test-only
    # forced-skip hook; no sandbox feature is involved. (a) An allow-listed
    # case skipping for its listed reason passes with a SKIP line; (b) the
    # same case skipping for another reason fails; (c) a case not on the
    # allow-list fails for any skip.
    for name, code, status, line in [
        ("socket", "unix-socket-bind-refused", 0,
         "  SKIP  credential scan socket: forced by SCAN_CREDENTIAL_TEST_FORCE_SKIP"),
        ("socket", "pty-unavailable", 1,
         "  FAIL  credential scan socket: undeclared skip: "
         "forced by SCAN_CREDENTIAL_TEST_FORCE_SKIP"),
        ("absent key", "unix-socket-bind-refused", 1,
         "  FAIL  credential scan absent key: undeclared skip: "
         "forced by SCAN_CREDENTIAL_TEST_FORCE_SKIP"),
    ]:
        p = subprocess.run(
            [sys.executable, __file__, name], capture_output=True, text=True,
            timeout=60,
            env={**os.environ, "SCAN_CREDENTIAL_TEST_FORCE_SKIP": name + "=" + code})
        assert p.returncode == status, (name, code, p.returncode, p.stdout, p.stderr)
        assert line in p.stdout.splitlines(), (name, code, p.stdout)


case("undeclared skip policy", "CHECK", skip_policy)


def sampling_enforcement(f):
    # Sampling that runs but never observes the Git child must fail, not
    # pass or skip: under the blind hook the sampler ignores Git cmdlines,
    # so the child run must exit 1 with the never-observed failure.
    p = subprocess.run(
        [sys.executable, __file__, "process sampling normal"], capture_output=True,
        text=True, timeout=300, env={**os.environ, "SCAN_CREDENTIAL_TEST_BLIND": "1"})
    if "/proc process inspection unavailable" in p.stdout:
        raise unittest_skip("proc-unavailable", "/proc process inspection unavailable")
    if "no environ read of any process succeeded" in p.stdout:
        raise unittest_skip("proc-environ-unread",
                            "no environ read succeeded in the blind child case")
    assert p.returncode == 1, (p.returncode, p.stdout, p.stderr)
    assert "never observed the Git child" in p.stdout, p.stdout


case("sampling observation required", "CHECK", sampling_enforcement)


# Hermetic skip policy: only the cases below may skip, each only for its
# listed environmental reason (the code its unittest_skip raises). Any other
# skip prints an undeclared-skip FAIL and exits 1 in every environment,
# local or CI alike; no CI marker is consulted anywhere in this file.
ALLOWED_SKIPS = {
    # A sandbox can refuse AF_UNIX socket binds inside the fixture tree.
    "socket": {"unix-socket-bind-refused"},
    # chmod cannot revoke access from a privileged (root) runner.
    "unreadable file 0": {"privileged-uid-reads-everything"},
    "unreadable directory 0": {"privileged-uid-reads-everything"},
    "unreadable directory 600": {"privileged-uid-reads-everything"},
    # A minimal container can lack a working pseudo-terminal device.
    "terminal TERM=dumb": {"pty-unavailable"},
    "terminal core.pager": {"pty-unavailable"},
    "terminal pager.grep": {"pty-unavailable"},
    "terminal PAGER": {"pty-unavailable"},
    "terminal GIT_PAGER": {"pty-unavailable"},
    "silent terminal input": {"pty-unavailable"},
    "interrupt during read": {"pty-unavailable"},
    # The ten sampling cases and their enforcement meta-case may skip only
    # when /proc inspection is unavailable outright, or when no environ
    # read of any process succeeded in the whole case; one denied read
    # during sampling is a missed sample, not a skip.
    "process sampling normal": {"proc-unavailable", "proc-environ-unread"},
    "process sampling disabled printf": {"proc-unavailable", "proc-environ-unread"},
    "process sampling printf function": {"proc-unavailable", "proc-environ-unread"},
    "process sampling read function": {"proc-unavailable", "proc-environ-unread"},
    "process sampling git function": {"proc-unavailable", "proc-environ-unread"},
    "process sampling printf alias": {"proc-unavailable", "proc-environ-unread"},
    "process sampling read alias": {"proc-unavailable", "proc-environ-unread"},
    "process sampling git alias": {"proc-unavailable", "proc-environ-unread"},
    "process sampling exported key": {"proc-unavailable", "proc-environ-unread"},
    "process sampling nameref key": {"proc-unavailable", "proc-environ-unread"},
    "process sampling inherited allexport": {"proc-unavailable", "proc-environ-unread"},
    "sampling observation required": {"proc-unavailable", "proc-environ-unread"},
}


def main():
    start = time.monotonic()
    selected = sys.argv[1:]
    forced_name, _, forced_code = FORCE_SKIP.rpartition("=")
    with tempfile.TemporaryDirectory(prefix="credential-template-") as shared:
        template = None
        for name, category, action in CASES:
            if selected and name not in selected:
                continue
            with tempfile.TemporaryDirectory(prefix="credential-") as directory:
                try:
                    if name == forced_name:
                        raise unittest_skip(
                            forced_code, "forced by SCAN_CREDENTIAL_TEST_FORCE_SKIP")
                    if template is None:
                        template = Path(shared) / "repo"
                        template.mkdir()
                        Fixture(template)
                    action(Fixture(Path(directory), template))
                except unittest_skip as exc:
                    if exc.code in ALLOWED_SKIPS.get(name, ()):
                        SKIPS.append(name)
                        print(f"  SKIP  credential scan {name}: {exc}")
                        continue
                    print(f"  FAIL  credential scan {name}: undeclared skip: {exc}")
                    return 1
                except Exception as exc:
                    print(f"  FAIL  credential scan {name}: {exc}")
                    return 1
            COUNTS[category] += 1
    assert sum(COUNTS.values()) or SKIPS, "no cases selected"
    print(f"  ok    credential scan: {sum(COUNTS.values())} cases; "
          f"{len(SKIPS)} skips; {time.monotonic() - start:.2f}s; {dict(COUNTS)}; "
          f"sampling reads: {SAMPLING['cmdline']} cmdline, "
          f"{SAMPLING['environ']} environ, {SAMPLING['denied']} denied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
