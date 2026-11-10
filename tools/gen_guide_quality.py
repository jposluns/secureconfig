#!/usr/bin/env python3
"""Seed or refresh the mechanical cells of tools/guide_quality.tsv (GQS 1.0, Phase A).

This computes the four tool-derived group cells for every enrolled guide and leaves every
judgment cell as `?` (unscored). It is the committed, offline port of the audit's gen_table.py;
it reads the tree only. The judgment cells (groups A, B, C, E, H, I, and the non-tool parts of
the rest) are NOT scored here: two families score those by hand and edit the TSV directly
(QUALITY.md section 1, 3.6). So this regenerates a Phase-A seed; once a judgment cell is filled,
the TSV is the source of truth and is not overwritten by a rerun.

The four mechanical leads (QUALITY.md 3.6):
  M (M1): the count of entries across the five baseline and allow files; zero is P, else PARTIAL(M1).
  D (D3): the Sources heading month against each item month; an earlier item is GAP(D3), a later
          one with no stated meaning is PARTIAL(D3), otherwise P (n/a when there is no Sources).
  F (F1): PARTIAL(F1) when a Verify H2 carries its declaration, else `?` (the rest is judgment).
  G (G1): PARTIAL(G1) when a sentence of 80+ characters repeats more than twice, else `?`.

Usage: python3 -I -B tools/gen_guide_quality.py            writes the TSV and the ledger
       python3 -I -B tools/gen_guide_quality.py --stdout   prints the TSV, writes nothing
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "tools")
import check_guide_quality as c  # noqa: E402

ROOT = c.ROOT
TSV = c.TSV
LEDGER = ROOT / "tools" / "guide_quality_ledger.tsv"
SCORED_ON = "2026-11-10"
SCORED_BY = "tool"

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}

BASELINES = ["tools/verify_marking_baseline.txt", "tools/version_basis_sources_baseline.txt",
             "tools/claim_length_baseline.txt", "tools/bracket_ranges_allow.txt",
             "tools/exposure_index_allowlist.txt"]

# Provisional type assignment from the 2026-11-09 audit (gen_table.py), confirmed by the hardening
# lane. Everything not named here is type S; the two K index guides are pinned in check_guide_quality.
TYPE_C = {
    "admin-uis.md", "devops-uis.md", "model-servers.md", "server-admin-panels.md", "chat-uis.md",
    "agent-builders.md", "ai-infra-services.md", "bi-dashboards.md", "image-gen-uis.md",
    "low-code-builders.md", "llm-observability.md", "observability-components.md",
    "workflow-orchestrators.md", "vector-databases.md", "time-series-metrics-stores.md", "tunnels.md",
    "search-engines.md", "sqlite-http-frontends.md", "self-hosted-error-trackers.md",
    "self-hosted-idp.md", "identity-providers.md", "connection-poolers.md",
    "headless-cms-instant-api.md", "headless-browser-services.md", "gitops-controllers.md",
    "realtime-voice-infra.md", "self-hosted-ci-runners.md", "nomad-consul.md", "elasticsearch.md",
    "paas.md", "gpu-clouds.md", "cloud-firewalls.md", "cloud-identity-proxies.md",
    "object-storage.md", "firebase-supabase.md", "frontend-frameworks.md", "pocketbase.md",
    "mcp-clients.md",
}
TYPE_X = {
    "cors.md", "headers.md", "authentication.md", "mfa.md", "secrets.md", "self-signed.md",
    "free-certificates.md", "oidc-integration.md", "machine-auth.md", "container-hardening.md",
    "egress-metadata.md", "web-exposure.md", "deployment-lifecycle.md",
    "transactional-email-posture.md", "realtime-webhooks.md", "fronting-auth.md", "host.md",
}


def gtype(guide):
    if guide in c.K_GUIDES:
        return "K"
    if guide in TYPE_C:
        return "C"
    if guide in TYPE_X:
        return "X"
    return "S"


def m1(guide):
    n = 0
    for b in BASELINES:
        for line in (ROOT / b).read_text(encoding="utf-8").splitlines():
            if guide in line:
                n += 1
    return ("P", 0) if n == 0 else ("PARTIAL(M1)", n)


def f1(text):
    for line in text.splitlines():
        if re.match(r"^## [0-9. ]*Verify\b.*\((?:REASONED|DEMONSTRATED):", line) or \
           re.match(r"^## [0-9. ]*Verify\b.*: (?:REASONED|DEMONSTRATED):", line):
            return "PARTIAL(F1)"
    return "?"


def month_key(name, year):
    return int(year) * 12 + MONTHS[name]


def d3(text):
    m = re.search(r"^## Sources \(checked ([A-Z][a-z]+) (\d{4})\)", text, re.M)
    if not m:
        return "n/a", 0, 0
    head = month_key(m.group(1), m.group(2))
    body = text[m.end():]
    nxt = re.search(r"^## ", body, re.M)
    sources = body[:nxt.start()] if nxt else body
    earlier = later = 0
    for mm in re.finditer(r"checked ([A-Z][a-z]+) (20\d\d)", sources):
        if mm.group(1) not in MONTHS:
            continue
        k = month_key(mm.group(1), mm.group(2))
        if k < head:
            earlier += 1
        elif k > head:
            later += 1
    if earlier:
        return "GAP(D3)", earlier, later
    if later:
        return "PARTIAL(D3)", earlier, later
    return "P", 0, 0


def g1(text):
    out, fence = [], False
    for line in text.splitlines():
        if line.startswith("```") or line.startswith("````"):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    prose = " ".join(out)
    sents = [s.strip() for s in re.split(r"(?<=[.;])\s+", prose)]
    counts = Counter(s for s in sents if len(s) >= 80)
    rep = [(s, n) for s, n in counts.items() if n > 2]
    if not rep:
        return "?", 0, 0
    return "PARTIAL(G1)", len(rep), max(n for _, n in rep)


def cells_for(guide, text):
    """The ten group cells and the ledger facts for one guide."""
    t = gtype(guide)
    m_cell, m_n = m1(guide)
    facts = {}
    if t == "K":
        cells = {"M": m_cell, "A": "n/a", "B": "?", "C": "n/a", "D": "n/a", "E": "n/a",
                 "F": "?", "G": "?", "H": "n/a", "I": "?"}
    else:
        d_cell, d_earlier, d_later = d3(text)
        f_cell = f1(text)
        g_cell, g_rep, g_max = g1(text)
        cells = {"M": m_cell, "A": "?", "B": "?", "C": "?", "D": d_cell, "E": "?",
                 "F": f_cell, "G": g_cell, "H": "?", "I": "?"}
        if d_cell != "P" and d_cell != "n/a":
            facts["D3"] = (d_cell.split("(")[0], d_earlier, d_later)
        if f_cell != "?":
            facts["F1"] = ("PARTIAL", 0, 0)
        if g_cell != "?":
            facts["G1"] = ("PARTIAL", g_rep, g_max)
    if m_cell != "P":
        facts["M1"] = ("PARTIAL", m_n, 0)
    return cells, facts


LEDGER_FINDING = {
    "M1": "entries across the five baseline and allow files, to sort into deferred work and reasoned waivers",
    "D3": "Sources item month(s) out of step with the heading month",
    "F1": "the Verify declaration sits on the Verify H2",
    "G1": "a sentence of 80+ characters repeats more than twice",
}
LEDGER_FIX = {
    "M1": "sort each entry into a deferred-work item or a reasoned waiver, then score M1",
    "D3": "settle the Sources heading-month wording in the corpus D3 sweep",
    "F1": "move the declaration to the Verify H2's first paragraph or its H3 children",
    "G1": "state the shared limitation once at the top of Verify and reference it",
}


def build():
    enrolled = c.enrolled_guides()
    rows, ledger = [], []
    for guide in sorted(enrolled):
        text = (ROOT / guide).read_text(encoding="utf-8")
        cells, facts = cells_for(guide, text)
        parsed = {g: c.parse_cell(cells[g], g) for g in c.GROUPS}
        verdict = c.compute_verdict(parsed)
        body = c.recorded_digest(guide)
        rows.append("\t".join([guide, gtype(guide), *[cells[g] for g in c.GROUPS],
                               verdict, body, SCORED_ON, SCORED_BY, "current"]))
        for crit in ("M1", "D3", "F1", "G1"):
            if crit not in facts:
                continue
            level, a, b = facts[crit]
            if crit == "M1":
                detail = f"{a} {LEDGER_FINDING[crit]}"
            elif crit == "D3":
                detail = (f"{a} item(s) dated earlier than the heading"
                          if level == "GAP" else f"{b} item(s) dated later than the heading; "
                          "meaning unstated")
            elif crit == "G1":
                detail = f"{a} sentence(s) repeated, max {b} times"
            else:
                detail = LEDGER_FINDING[crit]
            high = "yes" if crit in c.HIGH and level == "GAP" else "no"
            ledger.append("\t".join([guide, crit, level, high, "", detail,
                                     LEDGER_FIX[crit], "", SCORED_ON, "", "computed"]))
    tsv = "\n".join([c.HEADER1, c.HEADER2, *rows]) + "\n"
    ledger_header = ("# gqs\t1.0 ledger (advisory)\n# columns: guide\tcriterion\tlevel\t"
                     "high_class\tlines\tfinding\tfix\ttodo_row\topened\tclosed_by_pr\tbasis")
    ledger_tsv = "\n".join([ledger_header, *ledger]) + "\n"
    return tsv, ledger_tsv


def main():
    tsv, ledger_tsv = build()
    if "--stdout" in sys.argv[1:]:
        sys.stdout.write(tsv)
        return 0
    TSV.write_text(tsv, encoding="utf-8")
    LEDGER.write_text(ledger_tsv, encoding="utf-8")
    rows = tsv.count("\n") - 2
    print(f"wrote {TSV} ({rows} rows) and {LEDGER} ({ledger_tsv.count(chr(10)) - 2} ledger rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
