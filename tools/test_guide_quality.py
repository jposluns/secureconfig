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
import _markdown  # noqa: E402
import check_guide_quality as c  # noqa: E402
import check_exposure_index as cei  # noqa: E402
import gen_guide_quality as gen  # noqa: E402

DIGEST = {"a.md": "a" * 64, "b.md": "b" * 64,
          "common-mistakes.md": "c" * 64, "exposure-index.md": "e" * 64}
ENROLLED = ["a.md", "b.md", "common-mistakes.md", "exposure-index.md"]

failures = []
cases = [0]


def check(msg, cond):
    cases[0] += 1
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
        raised = False
        try:
            cell(group, text)
        except c.CellError:
            raised = True
        check(f"{why} must raise CellError ({text!r})", raised)

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

    # D3 and corpus rule O3 (maintainer rulings of 2026-11-25): the convention sentence on its own
    # line directly under the Sources heading states the heading month's meaning, so later item
    # months are P; earlier ones stay GAP. The P cases FAIL on the code before O3, which scored
    # every later item month PARTIAL(D3) whatever the section said.
    conv = gen.SOURCES_CONVENTION
    head = "# G\n\nBody.\n\n## Sources (checked October 2026)\n\n"
    later_item = "- Item (checked November 2026): https://example.com/a\n"
    earlier_item = "- Item (checked September 2026): https://example.com/b\n"
    tail = "\n## Next\n\nchecked December 2026 outside Sources.\n"
    check("the convention sentence is wording B of the 2026-11-25 ruling, at most 400 characters",
          conv.startswith("The month in this heading is the month of the whole-guide")
          and conv.endswith("so the later month applies to that item only.") and len(conv) <= 400)
    check("the convention sentence itself carries no item month",
          gen.d3(head + conv + "\n\n- Item: https://example.com/c\n") == ("P", 0, 0))
    check("the sentence under the heading with later item months is P",
          gen.d3(head + conv + "\n\n" + later_item + tail) == ("P", 0, 0))
    check("the sentence under the heading with an earlier item month is still GAP(D3)",
          gen.d3(head + conv + "\n\n" + earlier_item + later_item)
          == ("GAP(D3)", 1, 1))
    check("later item months with no sentence are PARTIAL(D3)",
          gen.d3(head + later_item + tail) == ("PARTIAL(D3)", 0, 1))
    for label, near in [
            ("a changed word", conv.replace("whole-guide", "guide-wide")),
            ("a dropped final full stop", conv[:-1]),
            ("straight quotes made curly", conv.replace('"checked"', "\u201cchecked\u201d")),
            ("a trailing space", conv + " "),
            ("a carriage return", conv + "\r"),
            ("a leading list marker", "- " + conv),
            ("lowercase", conv.lower()),
            ("a line break inside it", conv.replace(", and an item", ",\nand an item")),
            ("a following sentence on its line", conv + " Items are pinned.")]:
        check(f"a near-miss sentence ({label}) with later item months is PARTIAL(D3)",
              gen.d3(head + near + "\n\n" + later_item) == ("PARTIAL(D3)", 0, 1))
    check("the sentence after the first item, not directly under the heading, is PARTIAL(D3)",
          gen.d3(head + later_item + "\n" + conv + "\n") == ("PARTIAL(D3)", 0, 1))
    check("the sentence with no blank line before it is PARTIAL(D3)",
          gen.d3(head[:-1] + conv + "\n\n" + later_item) == ("PARTIAL(D3)", 0, 1))
    check("the sentence with no blank line after it is PARTIAL(D3)",
          gen.d3(head + conv + "\n" + later_item) == ("PARTIAL(D3)", 0, 1))
    check("the sentence outside the Sources section is PARTIAL(D3)",
          gen.d3("# G\n\n" + conv + "\n\n## Sources (checked October 2026)\n\n" + later_item)
          == ("PARTIAL(D3)", 0, 1))
    check("the sentence under another heading after Sources is PARTIAL(D3)",
          gen.d3(head + later_item + "\n## Notes\n\n" + conv + "\n") == ("PARTIAL(D3)", 0, 1))
    check("a bespoke meaning sentence, as vector-databases.md words its own, is PARTIAL(D3)",
          gen.d3(head + "The October 2026 date records the guide-wide documentation check.\n\n"
                 + later_item) == ("PARTIAL(D3)", 0, 1))
    check("the sentence with no Sources heading is n/a",
          gen.d3("# G\n\n" + conv + "\n\n" + later_item) == ("n/a", 0, 0))

    # A structural n/a from the tree wins over any recorded cell.
    check("a tree n/a wins over a recorded judgment cell",
          gen.merge_group("A", "n/a", "GAP(A2)") == "n/a")

    # M1 counts exact guide-field entries: not reason text, comments, or a guide name inside another.
    allow, claims = gen.BASELINES[4], gen.BASELINES[2]
    FILES = {allow: "README.md 80  # links free-certificates.md\n",
             claims: "# docker.md note\ndocker.md\tauth\t617\ndocker.md\tauth\t617\n"
                     "ghost.md\tx\t1\n\n"}
    check("a guide named only in reason text is not an M1 entry",
          gen.m1_count("free-certificates.md", FILES) == 0)
    check("the exact guide field counts, each duplicate once, comment lines never",
          gen.m1_count("docker.md", FILES) == 2)
    check("a suffix of another guide's name is not an M1 entry", gen.m1_count("host.md", FILES) == 0)
    check("an allowlist guide field with no reason counts",
          gen.m1_count("docker.md", {allow: "docker.md 80\n"}) == 1)
    check("a commented-out allowlist line does not count",
          gen.m1_count("docker.md", {allow: "#docker.md 80\n"}) == 0)
    check("a whitespace-only allowlist line names no guide", gen.entry_guide(allow, "   ") is None)
    check("a whitespace-only TAB-file line names no guide", gen.entry_guide(claims, "   ") is None)

    # The allowlist is read as the gate's own loader reads it: the expected value is what
    # check_exposure_index.load_allowlist returns for the same text, not a literal.
    class _GateFile:
        def __init__(self, text):
            self.text = text

        def read_text(self, encoding=None):
            return self.text

    class _GateRoot:
        def __init__(self, text):
            self.text = text

        def __truediv__(self, rel):
            return _GateFile(self.text)

    def gate_count(guide, text):
        return sum(1 for g, _port in cei.load_allowlist(_GateRoot(text)) if g == guide)

    for label, text, expected in [
            ("a line with no port", "docker.md  # r\n", 0),
            ("a line with three tokens", "docker.md 80 81\n", 0),
            ("a line with a non-numeric port", "docker.md http\n", 0),
            ("a duplicated guide and port pair", "docker.md 80\ndocker.md 80\n", 1),
            ("two ports for one guide", "docker.md 80\ndocker.md 81\n", 2)]:
        got = gen.m1_count("docker.md", {allow: text})
        check(f"M1 counts {label} as the gate does ({expected})",
              got == gate_count("docker.md", text) == expected)

    # M1 under the maintainer's rulings of 2026-11-14 (QUALITY.md M1): deferred-work entries and
    # waivers without a reason count, and a reasoned waiver does not. The reasoned-waiver cases
    # FAIL on the #1309 behaviour, which counted every entry in the five files.
    bracket = gen.BRACKET_ALLOW
    span, block = "sha256:" + "0" * 64, "sha256:" + "1" * 64
    reasoned_bracket = f"docker.md\t{span}\t{block}\ta JSON request body, not a pattern\n"
    check("each of the five files is deferred work or a waiver, and none is both",
          set(gen.BASELINES) == gen.DEFERRED_WORK | gen.WAIVERS
          and not gen.DEFERRED_WORK & gen.WAIVERS)
    check("a reasoned allowlist waiver is not an M1 entry",
          gen.m1_count("docker.md", {allow: "docker.md 80  # outbound: not a listener\n"}) == 0)
    check("a reasoned allowlist line is still parsed as the gate parses it",
          [gen.allow_entry("docker.md 80  # r")]
          == list(cei.load_allowlist(_GateRoot("docker.md 80  # r\n"))) == [("docker.md", 80)])
    check("a reasoned bracket-range waiver is not an M1 entry",
          gen.m1_count("docker.md", {bracket: reasoned_bracket}) == 0)
    for label, text in [("no `#`", "docker.md 80\n"), ("nothing after `#`", "docker.md 80  #\n"),
                        ("only spaces after `#`", "docker.md 80  #   \n")]:
        check(f"an allowlist waiver with {label} is an M1 entry",
              gen.m1_count("docker.md", {allow: text}) == 1)
    check("an allowlist pair counts once when any of its lines has no reason",
          gen.m1_count("docker.md", {allow: "docker.md 80  # r\ndocker.md 80\ndocker.md 80\n"})
          == 1)
    for label, text in [("no reason field", f"docker.md\t{span}\t{block}\n"),
                        ("an empty reason field", f"docker.md\t{span}\t{block}\t\n"),
                        ("a whitespace-only reason", f"docker.md\t{span}\t{block}\t  \n")]:
        check(f"a bracket-range waiver with {label} is an M1 entry",
              gen.m1_count("docker.md", {bracket: text}) == 1)
    check("only the unreasoned bracket-range line of the guide counts",
          gen.m1_count("docker.md", {bracket: reasoned_bracket + f"docker.md\t{span}\t{block}\n"
                                     + f"ghost.md\t{span}\t{block}\n"}) == 1)
    verify = gen.BASELINES[0]
    for path in sorted(gen.DEFERRED_WORK - {verify}):
        check(f"a {path} entry is deferred work and counts, whatever its other fields",
              gen.m1_count("docker.md", {path: "docker.md\tx\t1\tkept by design\n"}) == 1)

    # Row 3.64 and the maintainer's ruling of about 2026-11-14T21:59Z: a Verify-marking baseline
    # entry with a reason in its optional fifth TAB field is kept by design and does not count,
    # and one without a reason is still deferred work. The reasoned cases FAIL on the #1318
    # behaviour, which counted every entry in that file. Each unreasoned case sits beside a
    # reasoned entry and expects 1, so it fails on that behaviour (2) too. The file-name case
    # cannot tell the two apart: it only pins the fixture's premise, which both share.
    unit = "docker.md\tprose\t" + "2" * 64 + "\t1"
    check("the Verify-marking baseline is the file with the optional fifth-field reason",
          verify == "tools/verify_marking_baseline.txt")
    check("a reasoned Verify-marking baseline entry is not an M1 entry",
          gen.m1_count("docker.md", {verify: unit + "\tevidence for a DEMONSTRATED claim\n"}) == 0)
    beside = unit.replace("2", "4") + "\tby design\n"
    for label, text in [("no reason field", unit + "\n"), ("an empty reason field", unit + "\t\n"),
                        ("a whitespace-only reason", unit + "\t  \n"),
                        ("text in the count field only", "docker.md\tx\t1\tkept by design\n")]:
        check(f"a Verify-marking baseline entry with {label} beside a reasoned one is an M1 entry",
              gen.m1_count("docker.md", {verify: beside + text}) == 1)
    check("only the unreasoned Verify-marking line of the guide counts",
          gen.m1_count("docker.md", {verify: unit + "\tby design\n" + unit.replace("2", "3")
                                     + "\n" + unit.replace("docker", "ghost") + "\n"}) == 1)

    # Row 3.106: a reason made only of invisible format characters (Unicode category Cf) is no
    # reason in any of the three files, judged by the one rule, _markdown.reason_present. The
    # invisible cases FAIL on the code before row 3.106, whose str.strip() test kept each of these
    # characters and so counted 0; the ordinary and wrapped cases pass on both.
    for label, reason in [("U+200B", "\u200b"), ("U+FEFF", "\ufeff"), ("U+2060", "\u2060"),
                          ("U+200B, U+2060 and spaces", " \u200b \u2060 ")]:
        check(f"an allowlist waiver whose reason is only {label} is an M1 entry",
              gen.m1_count("docker.md", {allow: f"docker.md 80  #{reason}\n"}) == 1)
        check(f"a bracket-range waiver whose reason is only {label} is an M1 entry",
              gen.m1_count("docker.md", {bracket: f"docker.md\t{span}\t{block}\t{reason}\n"}) == 1)
        check(f"a Verify-marking baseline entry whose reason is only {label} is an M1 entry",
              gen.m1_count("docker.md", {verify: unit + f"\t{reason}\n"}) == 1)
    for label, reason in [("an ordinary reason", "outbound: not a listener"),
                          ("an ordinary reason wrapped in U+200B", "\u200bnot a listener\u200b")]:
        check(f"an allowlist waiver with {label} is not an M1 entry",
              gen.m1_count("docker.md", {allow: f"docker.md 80  # {reason}\n"}) == 0)
        check(f"a bracket-range waiver with {label} is not an M1 entry",
              gen.m1_count("docker.md", {bracket: f"docker.md\t{span}\t{block}\t{reason}\n"}) == 0)
        check(f"a Verify-marking baseline entry with {label} is not an M1 entry",
              gen.m1_count("docker.md", {verify: unit + f"\t{reason}\n"}) == 0)
    rule = getattr(_markdown, "reason_present", None)
    check("the M1 reader uses the shared rule, which counts Cf, Zs, Zl, Zp and whitespace as blank",
          rule is not None and getattr(gen, "reason_present", None) is rule
          and not any(rule(ch) for ch in "\u200b\ufeff\u2060\u00ad\u00a0\u3000\u2028\u2029\t\n\r")
          and rule("x") and rule("\u3164"))

    # m1() maps the count to its cell; ROOT is swapped for an in-memory tree, so nothing is written.
    class _Text:
        def __init__(self, text):
            self.text = text

        def read_text(self, encoding=None):
            return self.text

    class _Root(dict):
        def __truediv__(self, rel):
            return _Text(self.get(rel, ""))

    real_root = gen.ROOT
    gen.ROOT = _Root(FILES)
    try:
        check("no M1 entries is P", gen.m1("free-certificates.md") == ("P", 0))
        check("M1 entries are PARTIAL(M1) with their count",
              gen.m1("docker.md") == ("PARTIAL(M1)", 2))
        waived = {allow: "docker.md 80  # outbound: not a listener\n", bracket: reasoned_bracket}
        gen.ROOT = _Root(waived)
        check("a guide whose only entries are reasoned waivers is P on M1",
              gen.m1("docker.md") == ("P", 0))
        gen.ROOT = _Root({**waived, claims: "docker.md\tauth\t617\n"})
        check("a deferred-work entry beside reasoned waivers is PARTIAL(M1) with count 1",
              gen.m1("docker.md") == ("PARTIAL(M1)", 1))
        gen.ROOT = _Root({**waived, verify: unit + "\tevidence for a DEMONSTRATED claim\n"})
        check("a reasoned Verify-marking entry beside reasoned waivers is P on M1",
              gen.m1("docker.md") == ("P", 0))
    finally:
        gen.ROOT = real_root

    total = cases[0]
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of {total} guide-quality self-test cases failed")
        return 1
    print(f"PASS: {total} of {total} guide-quality self-test cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
