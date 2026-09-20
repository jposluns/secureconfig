#!/usr/bin/env python3
"""Hold the line on mutable GitHub source citations in the corpus.

A "Sources (checked <month year>)" line that points at a mutable branch ref,
`raw.githubusercontent.com/<owner>/<repo>/main|master/...` or
`github.com/<owner>/<repo>/blob/main|master/...`, cannot be re-verified: the file
can change the day after merge while the URL still resolves, so both this offline
gate suite and the advisory lychee sweep stay green while the cited evidence
silently drifts. New source citations must pin to a commit SHA or a version tag
(vendor doc-page slugs under docs.<vendor> may stay unpinned).

How the scan avoids false positives AND false negatives. Each line is split into
whole URL tokens: an optional scheme, an authority (a dotted host with an optional
`:port`), and then a single run of path/query/fragment characters, so a query
string, a fragment, a port, or a parenthesised path segment stays part of the SAME
URL and is never re-scanned as if it were a fresh URL. Each token is parsed with
`urllib.parse.urlsplit`, which separates the host, the path, the query and the
fragment properly:

  * the HOST is compared case-insensitively (hosts are case-insensitive, so
    `GITHUB.COM` is caught) and by EXACT equality (a greedy host label means
    `notgithub.com` is its own host, not a `github.com` suffix), and a target host
    or ref appearing inside another URL's path or query is never matched because
    that inner text is part of the outer token;
  * only the PATH is inspected -- never the query or fragment -- for the ref
    segment: the component right after `<owner>/<repo>` for a raw URL, or right
    after `.../blob/` for a blob URL, so a legitimate `main`/`master` deeper in a
    file path (for example `.../<tag>/clients/src/main/java/...`) is not flagged;
  * the REF is matched CASE-SENSITIVELY against `main`/`master`. Git refs are
    case-sensitive -- `refs/tags/MAIN` and `refs/heads/main` are different refs --
    so an uppercase `MAIN` may be a pinned tag and must NOT be treated as the
    mutable default branch.

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
from urllib.parse import urlsplit

TARGET_HOSTS = {"raw.githubusercontent.com", "github.com"}
MUTABLE_REFS = {"main", "master"}  # matched case-sensitively: git refs are case-sensitive

# One whole URL token. The left look-behind refuses a start glued to a host/path
# character, so a match cannot begin in the middle of a longer host (notgithub.com)
# or at a host-looking segment inside another URL's path. The optional scheme is
# part of the token, so a scheme-qualified URL still starts at its scheme. The rest
# is a single run beginning at the first `/`, `?` or `#` and ending only at
# whitespace, an angle bracket, a quote or a backtick -- parentheses are allowed, so
# an angle-bracket Markdown destination that contains them stays one token.
URL_TOKEN = re.compile(
    r"""(?xi)
    (?<![A-Za-z0-9._%+@:/~-])
    (?:https?://|//)?
    (?P<authority>[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?::\d+)?)
    (?P<rest>[/?\#][^\s<>"'`]*)?
    """
)


def _ref_segment(host: str, path: str):
    """Return the mutable ref of this URL's own path, or None.

    host is lowercased (from urlsplit). path is the URL path with query and
    fragment already stripped. Only the ref position is examined.
    """
    segments = [s for s in path.split("/") if s]
    if host == "raw.githubusercontent.com":
        # /<owner>/<repo>/<ref>/...
        if len(segments) >= 3 and segments[2] in MUTABLE_REFS:
            return segments[2]
    elif host == "github.com":
        # /<owner>/<repo>/blob/<ref>/...
        if len(segments) >= 4 and segments[2] == "blob" and segments[3] in MUTABLE_REFS:
            return segments[3]
    return None


def mutable_refs_in(line: str):
    """Yield ('raw'|'blob', ref) for each mutable-ref citation on the line."""
    for match in URL_TOKEN.finditer(line):
        authority = match.group("authority")
        rest = match.group("rest") or ""
        # Reconstruct as a scheme-relative URL so urlsplit fills netloc, and it
        # then separates host/port, path, query and fragment for us.
        parts = urlsplit("//" + authority + rest)
        host = parts.hostname  # lowercased, port stripped; None if unparseable
        if host not in TARGET_HOSTS:
            continue
        ref = _ref_segment(host, parts.path)
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
        ("https://raw.githubusercontent.com/o/r/main/f.py", 1),
        ("https://raw.githubusercontent.com/o/r/master/f.py", 1),
        ("see https://github.com/o/r/blob/main/docker-compose.yml here", 1),
        # schemeless still flags
        ("raw.githubusercontent.com/o/r/main/f.py", 1),
        # a blob ref with no trailing file (points at a directory) is still mutable
        ("github.com/o/r/blob/master", 1),
        # two mutable citations on one line count as two
        ("a raw.githubusercontent.com/o/r/main/f and github.com/o/r/blob/main/g", 2),
        # pinned tag whose PATH contains 'main' (src/main/java): must NOT flag
        ("raw.githubusercontent.com/apache/kafka/4.3.0/clients/src/main/java/X.java", 0),
        # pinned commit SHA / version tag: must NOT flag
        ("raw.githubusercontent.com/o/r/6ef7b86748118ceecd95271727c2fa167ce55fec/f", 0),
        ("raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/x.cs", 0),
        # vendor doc page that merely contains 'main' in the path: must NOT flag
        ("docs.spring.io/spring-boot/main/reference/x.html", 0),
        # blob with a pinned tag: must NOT flag
        ("github.com/o/r/blob/v1.2.3/f.py", 0),
        # host-boundary: a host ENDING in a target host must NOT flag
        ("notgithub.com/o/r/blob/main/f.py", 0),
        ("evilraw.githubusercontent.com.example.com/o/r/main/f", 0),
        # uppercase host must flag (hosts are case-insensitive)
        ("RAW.GITHUBUSERCONTENT.COM/o/r/main/f.py", 1),
        ("GitHub.com/o/r/blob/main/f.py", 1),
        # ref is case-SENSITIVE: MAIN / MASTER are distinct refs and must NOT flag
        ("github.com/o/r/blob/MAIN/f.py", 0),
        ("https://github.com/o/r/blob/MASTER/f.py", 0),
        # Markdown link: path stops at the closing paren, still flags
        ("[src](https://github.com/o/r/blob/main/f.py) and text", 1),
        # --- codex regression cases (ports, query, fragment, embedding) ---
        # a port must not break detection (was a false negative)
        ("https://github.com:443/o/r/blob/main/f", 1),
        ("https://raw.githubusercontent.com:443/o/r/main/f", 1),
        # target host embedded in another URL's QUERY must NOT flag
        ("https://example.com?u=https://github.com/o/r/blob/main/f", 0),
        # target host embedded in another URL's PATH (with a port) must NOT flag
        ("https://example.com:443/redir/github.com/o/r/blob/main/f", 0),
        # a QUERY that merely contains /blob/main/ must NOT flag
        ("https://github.com/o/r?x=/blob/main/f", 0),
        # a real blob ref carrying a query or fragment must STILL flag
        ("https://github.com/o/r/blob/main?raw=1", 1),
        ("https://github.com/o/r/blob/main#readme", 1),
        # angle-bracket Markdown destination containing parens, target embedded in path
        ("[src](<https://example.com/a(b)/github.com/o/r/blob/main/f>)", 0),
    ]
    ok = True
    for text, expected in cases:
        got = len(list(mutable_refs_in(text)))
        if got != expected:
            print(f"  self-test FAIL: {text!r} expected {expected} hit(s), got {got}")
            ok = False
    if ok:
        print("PASS: pinned-citation self-test (mutable main/master refs caught with "
              "case-insensitive host and case-sensitive ref; ports/queries/fragments "
              "parsed; pinned SHAs/tags, path-'main', host-suffix look-alikes, distinct "
              "uppercase refs, and refs embedded in another URL's path/query not flagged)")
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
