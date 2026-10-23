#!/usr/bin/env python3
"""Refuse version-basis claim text over 400 characters unless baselined.

Maintainer ruling 2026-10-23 (P6 option C, recorded in DECISIONS.md): every
claim's `text`, as stored in each enrolled guide's version-basis data, is
limited to 400 characters unless tools/claim_length_baseline.txt lists that
claim at exactly its current length.

Length is counted in Unicode code points: len() of the string that
version_basis.split() decodes from the guide's strict JSON metadata. That is
the unit the backlog and DONE rows already quote (TODO row 1.326's nine
gpu-clouds.md figures among them), it does not change with the file's UTF-8
byte length or with JSON string escaping, and it needs no locale, encoding
table or third-party module, so one claim has one length on every host.

The baseline has one TAB-separated entry per over-length claim: guide file,
claim id, and that claim's exact current length. Entries are sorted by guide
then claim id, without duplicates; '#' comment lines and blank lines are
skipped. Baseline lines are split on LF alone, and a line carrying any other
control or line-separator character (CR, form feed, U+0085, U+2028, U+2029
and the rest of Unicode categories Cc, Zl and Zp, tab excepted) is refused,
so no entry can hide behind a character that an editor or str.splitlines()
treats as a line break. The baseline fails closed when an entry is malformed
or out of order, names an unenrolled guide or a claim the guide no longer
has, or records a length at or under 400. A claim over 400 with no entry
fails, and so does any entry whose recorded length differs from the claim's
current length: longer means the claim grew past its allowance; shorter means
the entry is stale and must be shrunk to the new length, or removed once the
claim is at or under 400. Recording the exact length, rather than a ceiling,
is what makes the ratchet one-way against an unchanged baseline: a claim
shortened from 450 to 420 cannot quietly regrow toward 450 inside an old
allowance, the same shrink-or-remove contract as the Verify-marking and
Sources baselines. There is no automatic refresh; shrinking the baseline is a
reviewed edit in the same change that shortens the claim.

The gate reads the current tree only, so it cannot refuse a change that also
edits the baseline: adding an entry for a new over-length claim, or raising
an entry alongside its grown claim, passes and only review can refuse it.
The ruling's term "the baseline only shrinks" is upheld by that review, not
by this gate; the self-test records this limit so it is not quietly claimed.

Deterministic and offline: it reads only tools/version_basis_guides.txt, the
enrolled guides and the baseline, parsing metadata with version_basis.split(),
the same parse the version-basis gate uses. It measures length only; every
other claim rule stays with tools/version_basis.py --check. An unreadable
input or unparseable guide is an error, not a pass.
"""
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from version_basis import split  # noqa: E402

LIMIT = 400
GUIDE_RE = re.compile(r"[a-z][a-z0-9-]*\.md")
CLAIM_RE = re.compile(r"[a-z][a-z0-9-]*")


def claim_lengths(root, names):
    """Measure every enrolled claim; a guide the gate cannot read fails closed."""
    lengths = {}
    for name in names:
        text = (root / name).read_bytes().decode("utf-8")
        try:
            data, _ = split(text)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"{name}: unreadable version_basis metadata: {exc}") from exc
        if data is None or not isinstance(data.get("claims"), dict) or not data["claims"]:
            raise ValueError(f"{name}: missing version_basis claims")
        for claim_id, claim in data["claims"].items():
            if not isinstance(claim, dict) or not isinstance(claim.get("text"), str):
                raise ValueError(f"{name}: claim {claim_id} has no text string")
            lengths[(name, claim_id)] = len(claim["text"])
    return lengths


def baseline_entries(path, findings):
    """Parse the baseline; any malformed, control-bearing or unsorted line is a finding."""
    entries = {}
    previous = None
    # Split on LF alone: read_text()'s universal newlines and str.splitlines()
    # both treat more characters as line breaks, which could turn the tail of a
    # '#' comment line into a live entry.
    for number, line in enumerate(path.read_bytes().decode("utf-8").split("\n"), 1):
        controls = sorted({ch for ch in line if ch != "\t"
                           and unicodedata.category(ch) in ("Cc", "Zl", "Zp")})
        if controls:
            findings.append(f"claim-length baseline line {number}: control or "
                            f"line-separator character {controls[0]!r} is not allowed")
            continue
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if (len(fields) != 3 or not GUIDE_RE.fullmatch(fields[0])
                or not CLAIM_RE.fullmatch(fields[1])
                or not re.fullmatch(r"[1-9][0-9]*", fields[2])
                or int(fields[2]) <= LIMIT):
            findings.append(f"claim-length baseline line {number}: malformed entry "
                            f"(guide TAB claim TAB length over {LIMIT}): {line!r}")
            continue
        key = (fields[0], fields[1])
        if previous is not None and key <= previous:
            findings.append(f"claim-length baseline line {number}: entries must be "
                            f"sorted by guide then claim id, without duplicates: {line!r}")
        previous = key
        entries[key] = int(fields[2])
    return entries


def main(argv):
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    findings = []
    try:
        names = (root / "tools/version_basis_guides.txt").read_text(encoding="utf-8").splitlines()
        if (not names or len(names) != len(set(names))
                or not all(GUIDE_RE.fullmatch(name) for name in names)):
            raise ValueError("tools/version_basis_guides.txt is empty, duplicated or malformed")
        lengths = claim_lengths(root, names)
        entries = baseline_entries(root / "tools/claim_length_baseline.txt", findings)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f"  FAIL  cannot check claim lengths: {exc}")
        return 2
    if findings:
        # A baseline that cannot be trusted is never compared against.
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    enrolled = set(names)
    over = {key for key, length in lengths.items() if length > LIMIT}
    for key in sorted(entries.keys() | over):
        guide, claim = key
        recorded, actual = entries.get(key), lengths.get(key)
        if recorded is None:
            findings.append(f"{guide}: claim {claim}: {actual} characters exceeds the "
                            f"{LIMIT}-character limit and has no baseline entry")
        elif guide not in enrolled:
            findings.append(f"{guide}: claim {claim}: baseline entry names an "
                            f"unenrolled guide; remove it (limit {LIMIT})")
        elif actual is None:
            findings.append(f"{guide}: claim {claim}: baseline entry names a claim "
                            f"the guide no longer has; remove it (limit {LIMIT})")
        elif actual > recorded:
            findings.append(f"{guide}: claim {claim}: grew to {actual} characters from "
                            f"its baselined {recorded} (limit {LIMIT})")
        elif actual <= LIMIT:
            findings.append(f"{guide}: claim {claim}: now {actual} characters, at or "
                            f"under the {LIMIT}-character limit; remove its stale baseline entry")
        elif actual < recorded:
            findings.append(f"{guide}: claim {claim}: shrank to {actual} characters from "
                            f"its baselined {recorded}; shrink the entry to {actual} "
                            f"(limit {LIMIT})")
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    claim lengths: {len(lengths)} claims across {len(names)} enrolled "
          f"guides; {len(over)} baselined over {LIMIT} characters in "
          f"{len({guide for guide, _ in over})} guides; all over-length claims match "
          f"their baseline entries")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
