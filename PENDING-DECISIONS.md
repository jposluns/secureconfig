# PENDING DECISIONS

Questions awaiting a maintainer ruling. This file exists for unattended operation: a question that
needs a ruling must not block the queue and must not be answered by guessing, so it is written
here with the options and a recommendation, work continues on everything that does not depend on
it, and this file is the agenda at the next attended boundary.

A question graduates to `DECISIONS.md` when ruled, and is struck from here the same change. A
question that turns out not to need a ruling is struck with the reason, so it is not re-raised.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

## Open

### P1. Should the id series stop being numeric?

**Raised** 2026-09-13, by two defects in one day.

The id series is subject-based (`1.x` an existing guide, `2.x` missing content, `3.x` tooling,
`4.x` the site) and is independent of the priority band. Both are small integers, and for band 1
they coincide, so the band number reads as a plausible series number. Six rows were added using
the band number as the series and nothing caught it. The wrong ids had already merged, so they are
retired rather than recycled, which costs more than the original error.

- **A. Rename the series to letters** (`G` guide, `C` content, `T` tooling, `S` site), so `G.39`
  and `T.10` cannot be confused with a band. Existing ids would need a recorded mapping, and
  `DONE.md` holds ids that must keep resolving.
- **B. Gate the pairing instead.** Keep numeric ids and add a check that a row's series is
  consistent with the bands it is allowed to sit in. Cheaper, and it catches the error rather than
  making it unlikely.
- **C. Do nothing.** The rule is documented and now understood. Costs nothing if it does not recur.

**Recommendation: B.** A gate catches the error; a rename only makes it less likely, and it forces
a migration across two files of permanent identifiers whose whole value is that they never change.

### P2. Should backlog row shape be gated?

**Raised** 2026-09-13, alongside P1.

`TODO.md` and `DONE.md` are excluded from the guide gates because they are not guides, and nothing
replaced those checks. Eight rows were added omitting the `(severity, effort)` marker and putting
free prose in the `Tags` column instead of the closed vocabulary. Thirty-nine existing rows carried
both. The suite was silent.

- **A. Add a row-shape gate:** every row parses as
  `| id | text (severity, effort) | \`[tag]\` |`, ids are unique across `TODO.md` and `DONE.md`,
  no id is reused, and every tag is in the vocabulary. Deterministic and offline.
- **B. Gate ids only.** Uniqueness and non-reuse are the properties that cannot be repaired later;
  a missing severity marker can be filled in whenever it is noticed.
- **C. Do nothing**, and rely on review.

**Recommendation: A**, folded into the same change as P1's gate if P1 is answered B, since both
parse the same rows.

### P4. Should a container port behind a remapped publication be cited in the exposure index, or allowlisted?

**Raised** 2026-09-25, by the #311 review.

The index treats these inconsistently. It cites five container ports behind a publication: Vaultwarden's container port 80 (since #19) and Text Embeddings Inference's (`8080:80`, #300) on the 80, 443 row; the Mem0 API's (`8888:8000`, #300) on row 8000; and Open WebUI's (`127.0.0.1:3000:8080`, since #19) and SearxNG's (`8888:8080`, #300) on row 8080. #311 allowlisted three others instead, `ai-infra-services.md 9001` (Onyx `9005:9001`) and `llm-observability.md` 5432 and 8123 (Helicone `54388:5432`, `18123:8123`), each with a reason naming the host-port row that cites the guide.

- **A. Cite container ports too** (recommended): a scan from inside the container network or a pod sees the container port, so a reader who looks it up should reach the guide. The three allowlist entries become citations, with the product named in "May be".
- **B. Allowlist container ports consistently**, and move the five cited ones (Vaultwarden 80, Text Embeddings Inference 80, Mem0 8000, Open WebUI 8080, SearxNG 8080) to the allowlist.
- **C. Leave as is.**

No other work depends on it.

## Struck

Nothing yet.
