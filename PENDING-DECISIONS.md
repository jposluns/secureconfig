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

P6 is open. P3, P4 and P5 were ruled on 2026-09-25 and are recorded in `DECISIONS.md` (P5 was put to the
maintainer directly from the row 3.18 plan and ruled the same day, so it was never listed here; the id is taken);
P1 and P2 are struck below.

### P6. Should a claim-length gate be added, and with what limit?

**Raised** 2026-10-22, by #796, which recorded the ruling and the measurement of the longest claims.

The maintainer's 2026-10-18 claim-length ruling in `DECISIONS.md`, "Brief rule now, gate later", has draft briefs
require each claim to be a one- or two-sentence summary that keeps its qualifiers, and reconsiders a length gate
"after the new layout is live and the longest claims are measured". The ruling names no number; about 400
characters is the working figure briefs use, and CONTRIBUTING.md and the gates set no claim-length limit. At
349a642b, 104 claims in 32 of the 100 guides in `tools/version_basis_guides.txt` exceed 400 characters, nine of
them in `gpu-clouds.md` (row 1.326). The longest claims are now measured; whether the new layout is live, the
ruling's other precondition, has not been established.

- **A. No gate.** Keep the brief rule and rely on review. Costs nothing; an over-length claim is caught only if
  a reviewer measures it.
- **B. Gate new or changed claims only.** Refuse a claim over the limit when a change adds or edits it, compared
  with the base branch. Existing claims stay until touched, but any edit to one of the 104 forces it to be
  shortened in that change, and the check needs the base revision, not just the tree.
- **C. Baseline gate.** Refuse any claim over the limit unless it is listed in a checked-in baseline of the
  existing over-length claims, and refuse a listed claim that grows. Deterministic and offline; the baseline only
  shrinks, as rows such as 1.326 shorten claims.
- **D. Sentence-count check.** Refuse a claim of more than two sentences, which is the measure the ruling's
  wording names, instead of or alongside a character limit. Sentence splitting is heuristic (versions, file names
  and abbreviations contain full stops), two long sentences still pass, and existing claims still need B or C.

**Recommendation (advisory, not a ruling): C at 400 characters**, once the maintainer judges the new layout live.
It stops new over-length claims without forcing unrelated rewrites, and it runs offline on the tree alone. B makes
any edit to a long claim a forced rewrite, and D checks the ruling's sentence count but not length.

Tracked as backlog row 3.44. Row 1.326 does not depend on it.

## Struck

- **P1. Should the id series stop being numeric?** Struck 2026-09-25: the maintainer deferred it to the OPF
  standard, on the same ground as their 2026-09-24 decision on a row-format gate (recorded in `DECISIONS.md`). It
  was not ruled on its merits; ids stay numeric in the meantime.
- **P2. Should backlog row shape be gated?** Struck 2026-09-25: the maintainer ruled it covered by that same
  2026-09-24 decision.
