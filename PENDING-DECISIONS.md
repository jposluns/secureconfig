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

Nothing is open. P3 and P4 were ruled on 2026-09-25 and are recorded in `DECISIONS.md`; P1 and P2 are struck below.

## Struck

- **P1. Should the id series stop being numeric?** Struck 2026-09-25: the maintainer deferred it to the OPF
  standard, on the same ground as their 2026-09-24 decision on a row-format gate (recorded in `DECISIONS.md`). It
  was not ruled on its merits; ids stay numeric in the meantime.
- **P2. Should backlog row shape be gated?** Struck 2026-09-25: the maintainer ruled it covered by that same
  2026-09-24 decision.
