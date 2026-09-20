#!/usr/bin/env python3
"""Hold the line on mutable GitHub source citations in the corpus.

A "Sources (checked <month year>)" line that points at a mutable branch ref,
`raw.githubusercontent.com/<owner>/<repo>/main|master/...` or
`github.com/<owner>/<repo>/blob/main|master/...`, cannot be re-verified: the file
can change the day after merge while the URL still resolves, so both this offline
gate suite and the advisory lychee sweep stay green while the cited evidence
silently drifts. New source citations must pin to a commit SHA or a version tag
(vendor doc-page slugs under docs.<vendor> may stay unpinned).

How the scan avoids false positives. Each line is split into whole URL-ish tokens
(optional scheme, a hostname, then a path). A token is examined only when its
HOST equals a target host exactly, compared case-insensitively (so `GITHUB.COM`
is caught and `notgithub.com` is not, because the token's host group greedily
captures the whole label and then fails the equality test). Only the REF SEGMENT
of that token's own path is inspected -- the path component right after
`<owner>/<repo>` for a raw URL, or right after `.../blob/` for a blob URL -- so a
legitimate `main`/`master` appearing deeper in a file path (for example
`.../<tag>/clients/src/main/java/...`), or a target host or ref that appears
inside another URL's path or query string, is never flagged.

Scope: every root-level `.md` file is scanned (guides plus the adapters,
CHANGELOG and TODO), because a mutable citation is a defect wherever it lands and
the generated plugin reference copies live outside the root and would double-count.

Advisory phase (tracked as a corpus-wide pinning sweep; see the pinned-citation
sweep note under the `## 2026-09-20` heading in CHANGELOG.md): pinning the
existing refs is a corpus-wide change tracked separately. Until it lands, this
gate reports the current mutable citations and FAILS only if the count RISES
above BASELINE, so
the total can never exceed today's baseline -- a swap of one mutable ref for
another keeps the total and passes, but no net-new mutable citation can be added.
Lower BASELINE as the sweep pins refs; it reaches 0 when the sweep is complete and
the gate becomes a hard no-mutable-refs rule.
"""
import re
import sys
from pathlib import Path

TARGET_HOSTS = {"raw.githubusercontent.com", "github.com"}
MUTABLE_REFS = {"main", "master"}

# One whole URL-ish token: optional scheme, a greedy hostname label, then a path.
# The greedy host group swallows a leading label such as `not`, so a host that
# merely ends in a target host (notgithub.com) fails the exact-equality test below
# instead of matching a substring. The path stops at whitespace, a closing paren,
# angle bracket, quote, or backtick -- the delimiters used around URLs in Markdown.
TOKEN = re.compile(
    r"(?:https?://)?(?P<host>[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,})(?P<path>/[^\s)>\]\"'`]*)"
)


def _ref_segment(host: str, path: str):
    """Return the mutable ref segment of this URL's own path, or None.

    host is already lowercased. path begins with '/'. Only the ref position is
    examined: segment index 2 (after owner/repo) for a raw URL, or the segment
    right after a 'blob' segment for a github.com blob URL.
    """
    segments = [s for s in path.split("/") if s]
    if host == "raw.githubusercontent.com":
        # /<owner>/<repo>/<ref>/...
        if len(segments) >= 3:
            ref = segments[2]
            if ref.lower() in MUTABLE_REFS:
                return ref
    elif host == "github.com":
        # /<owner>/<repo>/blob/<ref>/...
        if len(segments) >= 4 and segments[2].lower() == "blob":
            ref = segments[3]
            if ref.lower() in MUTABLE_REFS:
                return ref
    return None


def mutable_refs_in(line: str):
    """Yield ('raw'|'blob', ref) for each mutable-ref citation on the line."""
    for match in TOKEN.finditer(line):
        host = match.group("host").lower()
        if host not in TARGET_HOSTS:
            continue
        ref = _ref_segment(host, match.group("path"))
        if ref is not None:
            kind = "raw" if host == "raw.githubusercontent.com" else "blob"
            yield kind, ref


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
        ("raw.githubusercontent.com/o/r/main/f.py", 1),
        ("raw.githubusercontent.com/o/r/master/f.py", 1),
        ("see github.com/o/r/blob/main/docker-compose.yml here", 1),
        # a blob ref with no trailing file (points at a directory) is still mutable
        ("github.com/o/r/blob/master", 1),
        # two mutable citations on one line count as two
        ("a raw.githubusercontent.com/o/r/main/f and github.com/o/r/blob/main/g", 2),
        # pinned tag whose PATH contains 'main' (src/main/java): must NOT flag
        ("raw.githubusercontent.com/apache/kafka/4.3.0/clients/src/main/java/X.java", 0),
        # pinned commit SHA: must NOT flag
        ("raw.githubusercontent.com/o/r/6ef7b86748118ceecd95271727c2fa167ce55fec/f", 0),
        # pinned version tag: must NOT flag
        ("raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/x.cs", 0),
        # a vendor doc page that merely contains 'main' in the path: must NOT flag
        ("docs.spring.io/spring-boot/main/reference/x.html", 0),
        # blob with a pinned tag: must NOT flag
        ("github.com/o/r/blob/v1.2.3/f.py", 0),
        # DEFECT 1a -- host-boundary: a host ENDING in a target host must NOT flag
        ("notgithub.com/o/r/blob/main/f.py", 0),
        ("evilraw.githubusercontent.com.example.com/o/r/main/f", 0),
        # DEFECT 1b -- target host/ref embedded in another URL's PATH must NOT flag
        ("https://example.com/redir/github.com/o/r/blob/main/f.py", 0),
        # DEFECT 1b -- target host/ref embedded in a QUERY STRING must NOT flag
        ("https://example.com/go?u=raw.githubusercontent.com/o/r/main/f", 0),
        # DEFECT 1b -- a pinned raw URL whose deep path embeds github blob/main must NOT flag
        ("raw.githubusercontent.com/o/r/1a2b3c4/docs/github.com/x/blob/main/y", 0),
        # DEFECT 2 -- uppercase host must flag (hosts are case-insensitive)
        ("RAW.GITHUBUSERCONTENT.COM/o/r/main/f.py", 1),
        ("GitHub.com/o/r/blob/MASTER/f.py", 1),
        # scheme-qualified target still flags
        ("https://raw.githubusercontent.com/o/r/main/f.py", 1),
        # a Markdown link: path stops at the closing paren, still flags
        ("[src](https://github.com/o/r/blob/main/f.py) and text", 1),
    ]
    ok = True
    for text, expected in cases:
        got = len(list(mutable_refs_in(text)))
        if got != expected:
            print(f"  self-test FAIL: {text!r} expected {expected} hit(s), got {got}")
            ok = False
    if ok:
        print("PASS: pinned-citation self-test (mutable main/master refs caught "
              "case-insensitively; pinned SHAs/tags, path-'main', host-suffix "
              "look-alikes, and refs embedded in another URL's path/query not flagged)")
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
BASELINE = 91


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
