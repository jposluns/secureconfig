#!/usr/bin/env python3
"""Hold the line on mutable GitHub source citations in the corpus.

A "Sources (checked <month year>)" line that points at a mutable branch ref,
`raw.githubusercontent.com/<owner>/<repo>/main|master/...` or
`github.com/<owner>/<repo>/blob/main|master/...`, cannot be re-verified: the file
can change the day after merge while the URL still resolves, so both this offline
gate suite and the advisory lychee sweep stay green while the cited evidence
silently drifts. New source citations must pin to a commit SHA or a version tag
(vendor doc-page slugs under docs.<vendor> may stay unpinned).

How URLs are extracted, so a target host or ref that appears inside ANOTHER URL's
components is never counted, and a real citation in any ordinary Markdown form is:

  * A citation must carry a scheme (`https:`/`http:`) or be scheme-relative (`//`).
    Every citation in this corpus is a scheme-qualified working link; a bare
    host-only reference is not a working citation and is deliberately OUT OF SCOPE.
  * Two Markdown destination contexts are handled explicitly. An angle-bracket
    destination `<URL>` runs to the `>`, so a query string that itself contains a
    quote or a second URL stays inside it. Every other URL runs from its scheme to
    the first delimiter, and a parenthesis, square bracket or quote ENDS the run --
    so a Markdown `](url)` closing paren does not glue onto the ref, adjacent
    `[a](u)[b](v)` links are not merged, and the embedded URL of a redirector stays
    part of the outer URL's query.
  * Each extracted URL is parsed with `urllib.parse.urlsplit`, which separates the
    host (userinfo and port stripped, lowercased), the path, the query and the
    fragment. The HOST is matched case-insensitively by exact equality (so
    `GITHUB.COM` is caught and `notgithub.com` is not); only the PATH is inspected
    for the ref segment; and the REF is matched CASE-SENSITIVELY against
    `main`/`master`, because git refs are case-sensitive -- an uppercase `MAIN` may
    be a pinned tag and must not be treated as the mutable default branch.

GitHub URL aliases that serve the same mutable content are covered: the legacy
`raw.github.com` host, the `github.com/.../raw/<ref>/` path alongside `/blob/`, a
leading `www.`, a trailing FQDN dot, and a percent-encoded ref. What is deliberately
NOT covered, and disclosed rather than chased, is out-of-scope by design: this is an
ADVISORY count-cap over the corpus's own citation forms, not a perfect adversarial
URL classifier. A contributor set on smuggling a mutable citation past it (an
IDN/punycode host, an open-redirector chain, a deliberately malformed URL) is not
the threat -- the honest author who pastes a `.../main/...` link is -- and a
committer bent on evasion has far simpler routes than an exotic URL. The gate's
guarantee is that no NEW citation in the ordinary forms this corpus uses can push
the count past the baseline.

Scope: every root-level `.md` file is scanned (guides plus the adapters, CHANGELOG
and TODO), because a mutable citation is a defect wherever it lands; the generated
plugin reference copies live outside the root and would double-count.

Advisory phase (tracked as a corpus-wide pinning sweep; see the pinned-citation
sweep note under the `## 2026-09-20` heading in CHANGELOG.md): pinning the existing
refs is a corpus-wide change tracked separately. Until it lands, this gate reports
the current mutable citations and FAILS only if the count RISES above BASELINE, so
the total can never exceed today's baseline -- a swap of one mutable ref for
another keeps the total and passes, but no net-new mutable citation can be added.
Lower BASELINE as the sweep pins refs; it reaches 0 when the sweep is complete and
the gate becomes a hard no-mutable-refs rule.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

# Hosts that serve a file straight from a git ref. raw.github.com is the legacy
# alias that still redirects to raw.githubusercontent.com with the same
# /<owner>/<repo>/<ref>/... layout.
RAW_HOSTS = {"raw.githubusercontent.com", "raw.github.com"}
# The web host, where a ref-served path sits under /<owner>/<repo>/blob|raw/<ref>/.
GH_HOSTS = {"github.com"}
GH_REF_MARKERS = {"blob", "raw"}
MUTABLE_REFS = {"main", "master"}  # matched case-sensitively: git refs are case-sensitive
_TRAILING_PUNCT = ".,;:!?"          # sentence punctuation that can trail a bare URL

# An angle-bracket Markdown destination: <URL> up to the closing '>'.
_ANGLE = re.compile(r"<((?:https?:)?//[^>\s]*)>")
# Any other URL: scheme (or scheme-relative //) to the first delimiter. A paren,
# square bracket, quote, backtick, angle bracket or whitespace ends the run.
_BARE = re.compile(r"(?:https?:)?//[^\s<>)\]\"'`]+")


def _urls(line: str):
    """Yield each URL on the line, angle-bracket destinations first."""
    urls = [m.group(1) for m in _ANGLE.finditer(line)]
    remainder = _ANGLE.sub(" ", line)  # blank them so the bare scan cannot re-hit
    urls.extend(m.group(0) for m in _BARE.finditer(remainder))
    return urls


def _norm_host(host):
    """Normalise a URL host to its canonical form, or None.

    Hosts are compared after stripping a trailing FQDN dot and a leading `www.`,
    both of which GitHub honours and redirects, so `www.github.com` and
    `github.com.` are treated as `github.com`.
    """
    if host is None:
        return None
    host = host.rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def _mutable_ref(url: str):
    """Return ('raw'|'blob', ref) if url is a mutable-branch citation, else None."""
    url = url.rstrip(_TRAILING_PUNCT)  # a URL ending a sentence keeps its punctuation out
    try:
        parts = urlsplit(url)
    except ValueError:
        return None  # not parseable as a URL: not a citation
    host = _norm_host(parts.hostname)  # lowercased; userinfo and port stripped
    # Percent-decode each path segment so an encoded ref (m%61in) is compared decoded.
    segments = [unquote(s) for s in parts.path.split("/") if s]
    if host in RAW_HOSTS:
        # /<owner>/<repo>/<ref>/...
        if len(segments) >= 3 and segments[2] in MUTABLE_REFS:
            return "raw", segments[2]
    elif host in GH_HOSTS:
        # /<owner>/<repo>/(blob|raw)/<ref>/...
        if len(segments) >= 4 and segments[2] in GH_REF_MARKERS and segments[3] in MUTABLE_REFS:
            kind = "raw" if segments[2] == "raw" else "blob"
            return kind, segments[3]
    return None


def mutable_refs_in(line: str):
    """Yield ('raw'|'blob', ref) for each mutable-ref citation on the line."""
    for url in _urls(line):
        hit = _mutable_ref(url)
        if hit is not None:
            yield hit


def scan(root: Path):
    findings = []
    decode_errors = []
    # Root-level Markdown only (iterdir raises on an unreadable root: fail-closed).
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError as exc:
            decode_errors.append(f"{path.name}: not valid UTF-8 ({exc}); fail-closed")
            continue
        for number, line in enumerate(lines, 1):
            for kind, ref in mutable_refs_in(line):
                findings.append(f"{path.name}:{number}: mutable {kind} GitHub ref ({ref})")
    return findings, decode_errors


def self_test() -> int:
    # (text, expected number of mutable-ref hits on the line)
    cases = [
        # --- ordinary citations ---
        ("https://raw.githubusercontent.com/o/r/main/f.py", 1),
        ("https://raw.githubusercontent.com/o/r/master/f.py", 1),
        ("see https://github.com/o/r/blob/main/docker-compose.yml here", 1),
        ("https://github.com/o/r/blob/master", 1),               # blob dir ref, no file
        ("scheme-relative //github.com/o/r/blob/main/f", 1),
        ("a https://raw.githubusercontent.com/o/r/main/f and https://github.com/o/r/blob/main/g", 2),
        # --- must NOT flag: pinned refs / path-'main' / vendor docs ---
        ("https://raw.githubusercontent.com/apache/kafka/4.3.0/clients/src/main/java/X.java", 0),
        ("https://raw.githubusercontent.com/o/r/6ef7b86748118ceecd95271727c2fa167ce55fec/f", 0),
        ("https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/x.cs", 0),
        ("https://docs.spring.io/spring-boot/main/reference/x.html", 0),
        ("https://github.com/o/r/blob/v1.2.3/f.py", 0),
        ("https://github.com/o/r/tree/main/f", 0),               # tree, not blob (scope)
        # --- host boundary ---
        ("https://notgithub.com/o/r/blob/main/f.py", 0),
        ("https://evilraw.githubusercontent.com.example.com/o/r/main/f", 0),
        # --- case: host insensitive, ref sensitive ---
        ("https://RAW.GITHUBUSERCONTENT.COM/o/r/main/f.py", 1),
        ("https://GitHub.com/o/r/blob/main/f.py", 1),
        ("https://github.com/o/r/blob/MAIN/f.py", 0),            # MAIN is a distinct ref
        ("https://github.com/o/r/blob/MASTER/f.py", 0),
        # --- schemeless is out of scope (not a working citation) ---
        ("raw.githubusercontent.com/o/r/main/f.py", 0),
        ("github.com/o/r/blob/main/f", 0),
        # --- ports / query / fragment (codex round 1) ---
        ("https://github.com:443/o/r/blob/main/f", 1),
        ("https://raw.githubusercontent.com:443/o/r/main/f", 1),
        ("https://example.com?u=https://github.com/o/r/blob/main/f", 0),
        ("https://example.com:443/redir/github.com/o/r/blob/main/f", 0),
        ("https://github.com/o/r?x=/blob/main/f", 0),
        ("https://github.com/o/r/blob/main?raw=1", 1),
        ("https://github.com/o/r/blob/main#readme", 1),
        # --- Markdown link forms (codex round 2) ---
        ("[src](https://github.com/o/r/blob/main/f.py) and text", 1),
        ("[source](https://github.com/a/b/blob/main)", 1),       # closing paren not part of ref
        ("[source](https://raw.githubusercontent.com/a/b/master)", 1),
        ("[one](https://example.org/doc)[two](https://github.com/a/b/blob/main/file)", 1),
        ("[a](https://github.com/x/y/blob/main/f)[b](https://raw.githubusercontent.com/x/y/main/g)", 2),
        # --- exotic authorities (codex round 2) ---
        ("<https://reader@github.com/a/b/blob/main/file>", 1),   # userinfo, real host
        ("<https://localhost/?u=https://github.com/a/b/blob/main/file>", 0),
        ("<https://[::1]/?u=https://github.com/a/b/blob/main/file>", 0),
        ("<https://reader@example.org/?u=https://github.com/a/b/blob/main/file>", 0),
        ("[source](<https://example.org/?q='https://github.com/a/b/blob/main/file>)", 0),
        # --- angle-bracket with parens in path, target embedded in path ---
        ("[src](<https://example.com/a(b)/github.com/o/r/blob/main/f>)", 0),
        # --- GitHub URL aliases and encodings (codex/gemini round 3) ---
        ("See https://github.com/owner/repo/blob/main.", 1),      # trailing sentence punct
        ("https://github.com/owner/repo/blob/m%61in/file.py", 1), # percent-encoded ref
        ("https://github.com/owner/repo/raw/main/file.py", 1),    # /raw/ path alias
        ("https://www.github.com/owner/repo/blob/main/f", 1),     # www. prefix
        ("https://github.com./owner/repo/blob/main/f", 1),        # trailing-dot FQDN
        ("https://raw.github.com/owner/repo/main/file.py", 1),    # legacy raw host
        # aliases must not create false positives on pinned refs
        ("https://github.com/owner/repo/raw/v1.2.3/file.py", 0),
        ("https://raw.github.com/owner/repo/abc1234/file.py", 0),
    ]
    ok = True
    for text, expected in cases:
        got = len(list(mutable_refs_in(text)))
        if got != expected:
            print(f"  self-test FAIL: {text!r} expected {expected} hit(s), got {got}")
            ok = False
    if ok:
        print("PASS: pinned-citation self-test (scheme-qualified mutable main/master "
              "refs caught with case-insensitive host and case-sensitive ref; "
              "ports/query/fragment/userinfo/IPv6 parsed; Markdown link and "
              "angle-bracket forms bounded; pinned refs, path-'main', host look-alikes, "
              "distinct uppercase refs, and embedded targets not flagged)")
        return 0
    print("FAIL: pinned-citation self-test")
    return 1


def main(argv) -> int:
    if "--self-test" in argv:
        return self_test()
    root = Path(__file__).resolve().parents[1]
    try:
        findings, decode_errors = scan(root)
    except OSError as exc:
        print(f"error: cannot scan the tree ({exc}); fail-closed", file=sys.stderr)
        return 2
    if decode_errors:
        for err in decode_errors:
            print(f"  {err}", file=sys.stderr)
        print("FAIL: a Markdown file is not valid UTF-8; cannot scan it for mutable "
              "citations, so failing closed rather than skipping it.", file=sys.stderr)
        return 2
    for finding in findings:
        print(f"  {finding}")
    count = len(findings)
    print(f"{count} mutable GitHub citation(s); baseline {BASELINE} "
          f"(existing refs tracked for pinning by the corpus-wide sweep)")
    if count > BASELINE:
        print(f"FAIL: mutable citation count {count} exceeds baseline {BASELINE}. "
              f"Pin every new GitHub source citation to a commit SHA or version tag, "
              f"never a main/master branch ref.")
        return 1
    print("PASS: mutable GitHub citations do not exceed the tracked baseline")
    return 0


# Existing mutable ref-segment citations across the root Markdown files. Tracked
# for pinning by the corpus-wide sweep; lower this as refs are pinned, to 0 when done.
BASELINE = 35


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
