#!/usr/bin/env python3
"""Cases for check_guide_quality.py, run on in-memory fixtures (no live corpus, no network).

Two kinds of case. compute_verdict() is exercised against the five verdicts and both NEEDS-WORK
paths (a HIGH-class GAP and three GAPs). validate() is driven with a small fixture matrix and one
mutation per refusal: a bad header, a missing or stray or duplicate row, a bad or misplaced type,
a malformed or wrong-group or repeated or misordered cell, a verdict mismatch, a stale digest, an
EXEMPLARY-while-stale row, and the field-shape refusals, plus a clean pass and the accepted
stale-but-not-exemplary row.
"""
import sys

sys.path.insert(0, "tools")
import check_guide_quality as c  # noqa: E402
import gen_guide_quality as gen  # noqa: E402

DIGEST = {"a.md": "a" * 64, "b.md": "b" * 64,
          "common-mistakes.md": "c" * 64, "exposure-index.md": "e" * 64}
ENROLLED = ["a.md", "b.md", "common-mistakes.md", "exposure-index.md"]

failures = []


def check(msg, cond):
    if not cond:
        failures.append(msg)


def cell(group, text):
    return c.parse_cell(text, group)


def verdict(**cells):
    full = {g: cell(g, cells.get(g, "P")) for g in c.GROUPS}
    return c.compute_verdict(full)


def row(guide, gtype, cells, verd, body, status="current",
        scored_on="2026-11-10", scored_by="tool"):
    return "\t".join([guide, gtype, *cells, verd, body, scored_on, scored_by, status])


# A valid four-row matrix: a.md all PASS (EXEMPLARY), b.md one unscored group (SOLID), two K rows.
P10 = ["P"] * 10
B_CELLS = ["P", "?", "P", "P", "P", "P", "P", "P", "P", "P"]
K_CELLS = ["P", "n/a", "?", "n/a", "n/a", "n/a", "?", "?", "n/a", "?"]
VALID_ROWS = [
    row("a.md", "S", P10, "EXEMPLARY", DIGEST["a.md"]),
    row("b.md", "X", B_CELLS, "SOLID", DIGEST["b.md"]),
    row("common-mistakes.md", "K", K_CELLS, "SOLID", DIGEST["common-mistakes.md"]),
    row("exposure-index.md", "K", K_CELLS, "SOLID", DIGEST["exposure-index.md"]),
]


def matrix(rows):
    return "\n".join([c.HEADER1, c.HEADER2, *rows]) + "\n"


def problems(rows, enrolled=ENROLLED, digests=DIGEST):
    return c.validate(matrix(rows), enrolled, digests)


def clean(rows):
    return problems(rows) == []


def fails_with(rows, marker):
    return any(marker in p for p in problems(rows))


def main():
    # compute_verdict: the five verdicts and both NEEDS-WORK paths.
    check("all PASS is EXEMPLARY", verdict() == "EXEMPLARY")
    check("an unknown blocks EXEMPLARY to SOLID", verdict(A="?") == "SOLID")
    check("a polish-only PARTIAL is SOLID+", verdict(D="PARTIAL(D2)", G="PARTIAL(G1)") == "SOLID+")
    check("an I1 unknown alone is SOLID+", verdict(I="?(I1)") == "SOLID+")
    check("an I2 unknown holds at SOLID", verdict(I="?(I2)") == "SOLID")
    check("one non-HIGH GAP is MINOR-GAPS", verdict(D="GAP(D3)") == "MINOR-GAPS")
    check("two non-HIGH GAPs is MINOR-GAPS", verdict(D="GAP(D1,D3)") == "MINOR-GAPS")
    check("a HIGH-class GAP is NEEDS-WORK", verdict(A="GAP(A2)") == "NEEDS-WORK")
    check("three GAPs is NEEDS-WORK", verdict(A="GAP(A3,A4,A5)") == "NEEDS-WORK")

    # parse_cell: valid shapes and refusals.
    check("n/a parses", cell("A", "n/a") == (set(), set(), set()))
    check("bare ? expands to the group", cell("A", "?")[2] == {"A1", "A2", "A3", "A4", "A5"})
    check("ordered combo parses",
          cell("A", "GAP(A2) PARTIAL(A3) ?(A5)") == ({"A2"}, {"A3"}, {"A5"}))
    for group, text, why in [
        ("A", "XYZ", "malformed token"),
        ("A", "PARTIAL(B1)", "wrong-group id"),
        ("A", "GAP(A1,A1)", "repeated id in one segment"),
        ("A", "PARTIAL(A1) ?(A1)", "repeated id across segments"),
        ("A", "PARTIAL(A1) GAP(A2)", "misordered segments"),
        ("A", "GAP(A1) GAP(A2)", "two GAP segments"),
        ("M", "P ?", "P is not a segment"),
    ]:
        try:
            cell(group, text)
            check(f"{why} must raise CellError ({text!r})", False)
        except c.CellError:
            pass

    # validate: a clean pass and the refusals.
    check("the valid matrix passes", clean(VALID_ROWS))

    bad1 = matrix(VALID_ROWS).replace(c.HEADER1, "# gqs\t9.9", 1)
    check("an unknown schema version fails",
          any("schema line" in p for p in c.validate(bad1, ENROLLED, DIGEST)))
    bad2 = matrix(VALID_ROWS).replace(c.HEADER2, "# columns: guide\ttype\twrong", 1)
    check("a drifted column header fails",
          any("column header" in p for p in c.validate(bad2, ENROLLED, DIGEST)))

    check("a missing row fails", fails_with(VALID_ROWS[:3], "have no row"))
    stray = VALID_ROWS + [row("z.md", "S", P10, "EXEMPLARY", "f" * 64)]
    check("a stray row fails", fails_with(stray, "not an enrolled guide"))
    dup = VALID_ROWS + [VALID_ROWS[0]]
    check("a duplicate row fails", fails_with(dup, "duplicate row"))

    bad_type = [row("a.md", "Q", P10, "EXEMPLARY", DIGEST["a.md"])] + VALID_ROWS[1:]
    check("a bad type fails", fails_with(bad_type, "not one of"))
    a_as_k = [row("a.md", "K", P10, "EXEMPLARY", DIGEST["a.md"])] + VALID_ROWS[1:]
    check("a non-index guide typed K fails", fails_with(a_as_k, "reserved for"))
    k_as_s = VALID_ROWS[:2] + [
        row("common-mistakes.md", "S", K_CELLS, "SOLID", DIGEST["common-mistakes.md"]),
        VALID_ROWS[3]]
    check("an index guide not typed K fails", fails_with(k_as_s, "reserved for"))

    malformed = [row("a.md", "S", ["XYZ"] + P10[1:], "EXEMPLARY", DIGEST["a.md"])] + VALID_ROWS[1:]
    check("a malformed cell fails", fails_with(malformed, "is not GAP"))
    wrong_group = [row("a.md", "S", ["P", "PARTIAL(B1)"] + P10[2:], "SOLID", DIGEST["a.md"])] \
        + VALID_ROWS[1:]
    check("a wrong-group id fails", fails_with(wrong_group, "does not belong to group A"))

    mism = [row("a.md", "S", P10, "SOLID", DIGEST["a.md"])] + VALID_ROWS[1:]
    check("a verdict mismatch fails", fails_with(mism, "does not match the rule"))

    stale_digest = [row("a.md", "S", P10, "EXEMPLARY", "0" * 64)] + VALID_ROWS[1:]
    check("a current row with a wrong digest fails",
          fails_with(stale_digest, "does not match the guide's recorded digest"))
    stale_ok = [row("a.md", "S", B_CELLS, "SOLID", "0" * 64, status="stale")] + VALID_ROWS[1:]
    check("a stale, non-EXEMPLARY row with any digest passes", clean(stale_ok))
    stale_exemplary = [row("a.md", "S", P10, "EXEMPLARY", DIGEST["a.md"], status="stale")] \
        + VALID_ROWS[1:]
    check("a stale EXEMPLARY row fails", fails_with(stale_exemplary, "cannot be EXEMPLARY"))

    short = [VALID_ROWS[0].rsplit("\t", 1)[0]] + VALID_ROWS[1:]
    check("a short row fails", fails_with(short, "columns, expected"))
    bad_body = [row("a.md", "S", P10, "EXEMPLARY", "nothex")] + VALID_ROWS[1:]
    check("a non-hex digest fails", fails_with(bad_body, "64 hex"))
    bad_date = [row("a.md", "S", P10, "EXEMPLARY", DIGEST["a.md"], scored_on="2026/11/10")] \
        + VALID_ROWS[1:]
    check("a bad scored_on fails", fails_with(bad_date, "YYYY-MM-DD"))
    no_by = [row("a.md", "S", P10, "EXEMPLARY", DIGEST["a.md"], scored_by="")] + VALID_ROWS[1:]
    check("an empty scored_by fails", fails_with(no_by, "scored_by is empty"))
    bad_status = [row("a.md", "S", P10, "EXEMPLARY", DIGEST["a.md"], status="maybe")] \
        + VALID_ROWS[1:]
    check("a bad status fails", fails_with(bad_status, "is not one of"))

    # gen_guide_quality merge: the mechanical leads (M1, D3, F1, G1) are recomputed from the tree,
    # every judgment criterion keeps its recorded value, and a guide with no prior row gets `?`.
    # These cases FAIL on the old behaviour, which hardcoded `?` for every judgment cell and
    # overwrote the matrix on every run.
    # A freshly computed row for a non-K guide: judgment groups `?`, the leads from the tree.
    FRESH = {"M": "PARTIAL(M1)", "A": "?", "B": "?", "C": "?", "D": "PARTIAL(D3)",
             "E": "?", "F": "?", "G": "?", "H": "?", "I": "?"}
    # A recorded row carrying hand-entered judgment scores (and a now-stale D3 lead).
    OLD = {"M": "P", "A": "GAP(A2)", "B": "PARTIAL(B1)", "C": "?", "D": "GAP(D1) PARTIAL(D3)",
           "E": "?", "F": "?", "G": "?", "H": "?", "I": "?"}

    # (a) A hand-entered judgment cell survives a gen run unchanged.
    merged = gen.merge_cells(FRESH, OLD)
    check("a hand-entered A judgment cell survives the merge", merged["A"] == "GAP(A2)")
    check("a hand-entered B judgment cell survives the merge", merged["B"] == "PARTIAL(B1)")

    # (b) A mechanical lead is recomputed from the tree, never left stale.
    fresh_gap = dict(FRESH, D="GAP(D3)")
    check("the D3 lead is recomputed from the tree, not preserved stale",
          gen.merge_cells(fresh_gap, OLD)["D"] == "GAP(D1,D3)")
    check("the M1 lead takes the freshly computed value",
          gen.merge_cells(FRESH, dict(OLD, M="PARTIAL(M1)"))["M"] == "PARTIAL(M1)")

    # (c) A newly enrolled guide with no prior row gets `?` judgment cells, leads from the tree.
    new = gen.merge_cells(FRESH, None)
    check("a new guide's A cell is unscored", new["A"] == "?")
    check("a new guide's B cell is unscored", new["B"] == "?")
    check("a new guide's D3 lead still comes from the tree", new["D"] == "PARTIAL(D3)")

    # (d) The verdict is recomputed from the merged cells (GAP(A2) is HIGH-class -> NEEDS-WORK;
    # the all-fresh row with only PARTIAL leads is SOLID).
    def verdict_of(cells):
        return c.compute_verdict({g: c.parse_cell(cells[g], g) for g in c.GROUPS})
    check("a preserved HIGH-class GAP drives the merged verdict to NEEDS-WORK",
          verdict_of(gen.merge_cells(FRESH, OLD)) == "NEEDS-WORK")
    check("an all-fresh non-K row is SOLID", verdict_of(gen.merge_cells(FRESH, None)) == "SOLID")

    # Cell round-trips: the serializer reproduces each grammar shape (byte-stability).
    for group, text in [("M", "P"), ("A", "?"), ("F", "PARTIAL(F1)"),
                        ("A", "GAP(A2) PARTIAL(A3) ?(A5)"), ("D", "GAP(D1,D3)")]:
        check(f"serialize round-trips {text!r} in {group}",
              gen.serialize_cell(gen.cell_levels(text, group), group) == text)

    # A structural n/a from the tree wins over any recorded cell.
    check("a tree n/a wins over a recorded judgment cell",
          gen.merge_group("A", "n/a", "GAP(A2)") == "n/a")

    total = 50
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of {total} guide-quality self-test cases failed")
        return 1
    print(f"PASS: {total} of {total} guide-quality self-test cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
