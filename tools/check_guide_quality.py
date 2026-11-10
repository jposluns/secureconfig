#!/usr/bin/env python3
"""Fail when tools/guide_quality.tsv is not a well-formed GQS 1.0 compliance matrix.

tools/guide_quality.tsv is the source of truth for the Guide Quality Standard (QUALITY.md, GQS
1.0): one row per enrolled guide, ten group cells (M, A, B, C, D, E, F, G, H, I), a computed
verdict, the body digest the row was scored at, and the scoring metadata. This gate checks that
the matrix is structurally sound; it does not and cannot score the judgment criteria, which two
families score by hand (QUALITY.md section 1). A cell not yet scored carries `?`, which this gate
accepts and which blocks the EXEMPLARY verdict.

WHAT THIS CHECKS, all deterministic, tree-only and offline:
  1. Header: line 1 is `# gqs<TAB>1.0`; line 2 is the exact column header. An unknown schema
     version is refused.
  2. Row set: exactly the enrolled guides, one row each. The enrolled set is the guides in
     tools/version_basis_guides.txt plus the two type-K index guides (common-mistakes.md,
     exposure-index.md). A missing, stray or duplicated row fails.
  3. Type: one of S, C, X, K. Type K is reserved for the two index guides and neither may carry
     another type; every other guide may not be K.
  4. Cell grammar (QUALITY.md 3.2): each group cell is `P`, `n/a`, a bare `?`, or an ordered
     sequence of `GAP(ids)`, `PARTIAL(ids)` and `?(ids)` segments (GAP first, then PARTIAL, then
     `?`), whose ids all belong to that group (an A cell names only A1..A5, and so on).
  5. Verdict (QUALITY.md 3.3): the verdict column equals the rule computation from the ten cells,
     with `?` counted as PARTIAL (so any `?` blocks EXEMPLARY).
  6. Staleness: each row's body_sha256 equals the guide's recorded digest (the AI-assistant
     JSON body_sha256 for an enrolled guide, or the sha256 of the whole file for a K guide), or
     the row's status is `stale`. A `stale` row is never EXEMPLARY.

The findings ledger (tools/guide_quality_ledger.tsv) is advisory in GQS 1.0 and is not checked
here. The checker exits non-zero and prints one `  FAIL  ` line per finding, or a single summary
line on success, in the suite's house style.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "tools" / "guide_quality.tsv"
VERSIONED = ROOT / "tools" / "version_basis_guides.txt"

# The two type-K index guides, enrolled but not carried in version_basis_guides.txt. They have no
# AI-assistant JSON, so their digest is the sha256 of the whole file (QUALITY.md 2, K exception).
K_GUIDES = ("common-mistakes.md", "exposure-index.md")

SCHEMA = "1.0"
HEADER1 = "# gqs\t" + SCHEMA
GROUPS = ("M", "A", "B", "C", "D", "E", "F", "G", "H", "I")
HEADER2 = ("# columns: guide\ttype\t" + "\t".join(GROUPS)
           + "\tverdict\tbody_sha256\tscored_on\tscored_by\tstatus")
COLUMNS = 2 + len(GROUPS) + 5  # guide, type, ten groups, verdict, body_sha256, scored_on/by, status

TYPES = ("S", "C", "X", "K")
VERDICTS = ("NEEDS-WORK", "MINOR-GAPS", "SOLID", "SOLID+", "EXEMPLARY")
STATUSES = ("current", "stale")

# The criteria of each group, in id order (QUALITY.md 1).
GROUP_CRITERIA = {
    "M": ("M1",),
    "A": ("A1", "A2", "A3", "A4", "A5"),
    "B": ("B1", "B2", "B3", "B4"),
    "C": ("C1", "C2", "C3", "C4"),
    "D": ("D1", "D2", "D3"),
    "E": ("E1", "E2", "E3"),
    "F": ("F1", "F2"),
    "G": ("G1", "G2", "G3"),
    "H": ("H1", "H2"),
    "I": ("I1", "I2"),
}

# A GAP on one of these criteria is HIGH-class (QUALITY.md 0): one makes the verdict NEEDS-WORK.
# The group cell cannot carry a sub-criterion qualifier ("A1 wrong bind"), so any GAP on a
# HIGH-listed id is treated as HIGH-class, which can only over-escalate, never hide a defect.
HIGH = frozenset({"M1", "A1", "A2", "B1", "B2", "C1", "C2", "E2", "E3"})

# A PARTIAL or `?` only on these criteria is polish, not a fix owed: it earns SOLID+ (QUALITY.md
# 3.3). A PARTIAL or `?` anywhere else holds the guide at SOLID.
SOLID_PLUS = frozenset({"G1", "G2", "G3", "I1", "D2"})

_IDS = re.compile(r"^[A-Z][0-9](?:,[A-Z][0-9])*$")


class CellError(ValueError):
    """A group cell that does not parse the QUALITY.md 3.2 grammar."""


def parse_cell(cell, group):
    """Return (gaps, partials, unknowns) sets of criterion ids for one group cell.

    A bare `?` means the whole group is unscored and expands to every criterion in the group.
    `n/a` contributes nothing. Raises CellError on a malformed cell or an id outside the group.
    """
    valid = set(GROUP_CRITERIA[group])
    if cell == "n/a" or cell == "P":
        return set(), set(), set()
    if cell == "?":
        return set(), set(), set(valid)
    gaps, partials, unknowns = set(), set(), set()
    seen = []
    for seg in cell.split(" "):
        m = re.fullmatch(r"(GAP|PARTIAL|\?)\(([^()]*)\)", seg)
        if not m:
            raise CellError(f"segment {seg!r} is not GAP(...), PARTIAL(...) or ?(...)")
        kind, ids = m.group(1), m.group(2)
        if not _IDS.fullmatch(ids):
            raise CellError(f"segment {seg!r} has a malformed id list")
        bucket = {"GAP": gaps, "PARTIAL": partials, "?": unknowns}[kind]
        for cid in ids.split(","):
            if cid not in valid:
                raise CellError(f"id {cid} does not belong to group {group}")
            if cid in gaps | partials | unknowns:
                raise CellError(f"id {cid} appears twice in the cell")
            bucket.add(cid)
        seen.append(kind)
    order = {"GAP": 0, "PARTIAL": 1, "?": 2}
    if any(order[seen[i]] >= order[seen[i + 1]] for i in range(len(seen) - 1)):
        raise CellError("segments must be ordered GAP, then PARTIAL, then ?, each at most once")
    return gaps, partials, unknowns


def compute_verdict(cells):
    """The rule-based verdict (QUALITY.md 3.3) from the ten parsed group cells.

    cells maps each group letter to the (gaps, partials, unknowns) triple parse_cell returns.
    `?` (an unknown) counts as PARTIAL and blocks EXEMPLARY.
    """
    gaps, nonpass = set(), set()
    for gap, partial, unknown in cells.values():
        gaps |= gap
        nonpass |= partial | unknown
    if gaps & HIGH or len(gaps) >= 3:
        return "NEEDS-WORK"
    if gaps:
        return "MINOR-GAPS"
    if not nonpass:
        return "EXEMPLARY"
    if nonpass <= SOLID_PLUS:
        return "SOLID+"
    return "SOLID"


def enrolled_guides():
    """The enrolled guide set: version_basis_guides.txt plus the two K index guides."""
    listed = [line.strip() for line in VERSIONED.read_text(encoding="utf-8").splitlines()
              if line.strip()]
    return listed + list(K_GUIDES)


def recorded_digest(guide):
    """The digest a TSV row must carry for `guide` to be current.

    A K guide: the sha256 of the whole file. An enrolled guide: the body_sha256 recorded in its
    AI-assistant JSON, which the version-basis gate already holds equal to the stripped body.
    """
    path = ROOT / guide
    data = path.read_bytes()
    if guide in K_GUIDES:
        return hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8")
    found = re.findall(r'^[ \t]*"body_sha256":[ \t]*"([0-9a-f]{64})"', text, re.M)
    if len(found) != 1:
        raise ValueError(f"{guide}: expected exactly one body_sha256 field, found {len(found)}")
    return found[0]


def validate(text, enrolled, digests):
    """Return the list of findings for the TSV `text`.

    enrolled is the ordered enrolled-guide list; digests maps each guide to its expected digest.
    This function reads nothing from disk, so the self-test drives it with fixtures.
    """
    problems = []
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    if len(lines) < 2:
        return ["guide_quality.tsv has no header"]
    if lines[0] != HEADER1:
        problems.append(f"line 1 must be {HEADER1!r} (the gqs schema line), not {lines[0]!r}")
    if lines[1] != HEADER2:
        problems.append("line 2 is not the exact column header; the schema may have drifted")
    if problems:
        return problems  # Without a known header the rows cannot be read safely.

    enrolled_set = set(enrolled)
    k_set = set(K_GUIDES)
    seen = {}
    for n, line in enumerate(lines[2:], start=3):
        if line.startswith("#"):
            problems.append(f"line {n}: a comment after the header is not allowed")
            continue
        fields = line.split("\t")
        if len(fields) != COLUMNS:
            problems.append(f"line {n}: {len(fields)} columns, expected {COLUMNS}")
            continue
        guide, gtype = fields[0], fields[1]
        cell_strs = fields[2:12]
        verdict, body, scored_on, scored_by, status = fields[12:17]
        if guide in seen:
            problems.append(f"line {n}: duplicate row for {guide} (first at line {seen[guide]})")
            continue
        seen[guide] = n
        if guide not in enrolled_set:
            problems.append(f"line {n}: {guide} is not an enrolled guide")
            continue
        if gtype not in TYPES:
            problems.append(f"line {n}: {guide} has type {gtype!r}, not one of {TYPES}")
        if (guide in k_set) != (gtype == "K"):
            problems.append(f"line {n}: type K is reserved for {K_GUIDES} and required there; "
                            f"{guide} has type {gtype!r}")
        cells = {}
        cell_ok = True
        for group, cell in zip(GROUPS, cell_strs):
            try:
                cells[group] = parse_cell(cell, group)
            except CellError as exc:
                problems.append(f"line {n}: {guide} group {group} cell {cell!r}: {exc}")
                cell_ok = False
        if status not in STATUSES:
            problems.append(f"line {n}: {guide} status {status!r} is not one of {STATUSES}")
        if not re.fullmatch(r"[0-9a-f]{64}", body):
            problems.append(f"line {n}: {guide} body_sha256 is not 64 hex characters")
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", scored_on):
            problems.append(f"line {n}: {guide} scored_on {scored_on!r} is not YYYY-MM-DD")
        if not scored_by:
            problems.append(f"line {n}: {guide} scored_by is empty")
        if cell_ok and verdict not in VERDICTS:
            problems.append(f"line {n}: {guide} verdict {verdict!r} is not one of {VERDICTS}")
        elif cell_ok:
            expected = compute_verdict(cells)
            if verdict != expected:
                problems.append(f"line {n}: {guide} verdict {verdict!r} does not match the rule "
                                f"computation {expected!r} from its cells")
        # Staleness: a current row's digest must match; a stale row must not be EXEMPLARY.
        expected_digest = digests.get(guide)
        if status == "current" and expected_digest is not None and body != expected_digest:
            problems.append(f"line {n}: {guide} body_sha256 does not match the guide's recorded "
                            f"digest; rescore the row or mark it stale")
        if status == "stale" and verdict == "EXEMPLARY":
            problems.append(f"line {n}: {guide} is stale and cannot be EXEMPLARY")
    missing = sorted(enrolled_set - set(seen))
    if missing:
        problems.append(f"{len(missing)} enrolled guide(s) have no row: {missing}")
    return problems


def main():
    try:
        text = TSV.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  FAIL  cannot read {TSV}: {exc}")
        return 1
    try:
        enrolled = enrolled_guides()
        digests = {g: recorded_digest(g) for g in enrolled}
    except (OSError, ValueError) as exc:
        print(f"  FAIL  cannot assemble the enrolled-guide digests: {exc}")
        return 1
    problems = validate(text, enrolled, digests)
    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
        return 1
    rows = len(text.rstrip("\n").split("\n")) - 2
    print(f"  ok    guide-quality: {rows} rows, one per enrolled guide, grammar and verdicts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
