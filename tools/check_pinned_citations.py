#!/usr/bin/env python3
"""Hold the line on mutable GitHub source citations in the guides.

A "Sources (checked <month year>)" line that points at a mutable branch ref,
`raw.githubusercontent.com/<owner>/<repo>/main|master/...` or
`github.com/<owner>/<repo>/blob/main|master/...`, cannot be re-verified: the file
can change the day after merge while the URL still resolves, so both this offline
gate suite and the advisory lychee sweep stay green while the cited evidence
silently drifts. Deepening citations must pin to a commit SHA or a version tag
(vendor doc-page slugs under docs.<vendor> may stay unpinned).

Only the REF SEGMENT is inspected: the ref is the path component right after
`<owner>/<repo>` (or after `.../blob/`), so a legitimate `main` or `master`
appearing inside a file PATH, for example `.../<tag>/clients/src/main/java/...`,
is NOT flagged. Only root-level guide files are scanned; the generated plugin
reference copies mirror them and would double-count.

Advisory phase (backlog TODO 30): pinning the existing refs is a corpus-wide
sweep tracked separately. Until it lands, this gate reports the current mutable
citations and FAILS only if their count rises above BASELINE, so no NEW mutable
citation can be introduced. Lower BASELINE as the sweep pins refs; it reaches 0
when the sweep is complete and the gate becomes a hard no-mutable-refs rule.
"""
import re
import sys
from pathlib import Path

# The ref segment sits right after <owner>/<repo> (raw) or after /blob/ (blob UI).
# [^/\s)]+ stops at the next slash, whitespace, or a closing paren in a Markdown link.
RAW = re.compile(r"raw\.githubusercontent\.com/[^/\s)]+/[^/\s)]+/(?:main|master)/")
BLOB = re.compile(r"github\.com/[^/\s)]+/[^/\s)]+/blob/(?:main|master)/")

# Existing mutable ref-segment citations across the root guides at 2026-09-20.
# Tracked for pinning by backlog TODO 30 (PINNED-CITATIONS); lower this as they are pinned.
BASELINE = 91


def scan(root: Path):
    findings = []
    # Root-level guides only (iterdir raises on an unreadable root: fail-closed).
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            for rx, kind in ((RAW, "raw"), (BLOB, "blob")):
                # Count each citation, so a line carrying two mutable URLs counts as two.
                for _ in rx.finditer(line):
                    findings.append(f"{path.name}:{number}: mutable {kind} GitHub ref")
    return findings


def self_test() -> int:
    cases = [
        ("raw.githubusercontent.com/o/r/main/f.py", True),
        ("raw.githubusercontent.com/o/r/master/f.py", True),
        ("see github.com/o/r/blob/main/docker-compose.yml here", True),
        # pinned tag whose PATH contains 'main' (src/main/java): must NOT flag
        ("raw.githubusercontent.com/apache/kafka/4.3.0/clients/src/main/java/X.java", False),
        # pinned commit SHA: must NOT flag
        ("raw.githubusercontent.com/o/r/6ef7b86748118ceecd95271727c2fa167ce55fec/f", False),
        # pinned version tag: must NOT flag
        ("raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/x.cs", False),
        # a vendor doc page that merely contains 'main' in the path: must NOT flag
        ("docs.spring.io/spring-boot/main/reference/x.html", False),
        # blob with a pinned tag: must NOT flag
        ("github.com/o/r/blob/v1.2.3/f.py", False),
    ]
    ok = True
    for text, should in cases:
        hit = bool(RAW.search(text) or BLOB.search(text))
        if hit != should:
            print(f"  self-test FAIL: {text!r} expected hit={should}, got {hit}")
            ok = False
    if ok:
        print("PASS: pinned-citation self-test (mutable main/master refs caught; "
              "pinned SHAs/tags and path-'main' not flagged)")
        return 0
    print("FAIL: pinned-citation self-test")
    return 1


def main(argv) -> int:
    if "--self-test" in argv:
        return self_test()
    root = Path(__file__).resolve().parents[1]
    try:
        findings = scan(root)
    except OSError as exc:
        print(f"error: cannot scan the tree ({exc}); fail-closed", file=sys.stderr)
        return 2
    for finding in findings:
        print(f"  {finding}")
    count = len(findings)
    print(f"{count} mutable GitHub citation(s); baseline {BASELINE} "
          f"(existing refs tracked for pinning by TODO 30)")
    if count > BASELINE:
        print(f"FAIL: mutable citation count {count} exceeds baseline {BASELINE}. "
              f"Pin every new GitHub source citation to a commit SHA or version tag, "
              f"never a main/master branch ref.")
        return 1
    print("PASS: no new mutable GitHub citations beyond the tracked baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
