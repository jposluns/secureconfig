# DECISIONS

Maintainer rulings, recorded so they are not re-litigated. A decision here is settled: it is not
reopened by a later review finding or by a worker's recommendation, only by the maintainer.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

Backlog rows live in `TODO.md`, closed rows in `DONE.md`, and questions awaiting a ruling in
`PENDING-DECISIONS.md`. A row may cite a decision here; a decision never carries a row's status.

Each ruling records the maintainer's reasoning as well as the ruling, and the profile at the end
generalizes across them, so that fewer questions need asking. The profile is the orchestrator's
inference and is fallible; it never substitutes for a ruling on anything irreversible or outward.

## 2026-09-13

- **`ss | grep <port>` in 48 guides:** fix only the checks whose Verify claims nothing ELSE is
  exposed. A filtered check that asks "is this bound to loopback?" is correct for what it claims
  and stays. Judge each of the 48 rather than sweeping. *Reasoning:* a check that is correct for
  what it actually claims is not a defect merely because it shares a shape with checks that are.
  The instinct being corrected is mine, not the corpus's.
- **Order:** AIQT applies, errors first and to empty, then interleave by severity across the
  remaining bands. *Reasoning:* a reader acting on a wrong guide is worse off than a reader with
  no guide, so correctness outranks coverage unconditionally.
- **The six AI-infra gaps** (LocalAI, LangServe, SearxNG, Mem0, text-embeddings-inference, Onyx):
  one guide covering the pattern, with a per-tool table of default port, default authentication,
  and the flag that changes it, rather than six guides. *Reasoning:* where the exposure pattern is
  shared, six guides would repeat one lesson six times and drift apart; a table carries the
  per-tool differences without duplicating the reasoning.
- **Audit cadence:** monthly, and whenever the backlog empties before that. *Reasoning:* periodic
  alone goes stale between runs and event-triggered alone never fires while work is plentiful, so
  both.
- **`VERSION` (row 3.9):** the scheme stays. `CONTRIBUTING.md` gains the authoring step instead:
  open the pull request, write its number into `VERSION`, push, then merge. #48 did this and
  needed no follow-up, which is the evidence the step is sufficient. *Reasoning:* the scheme was
  not what failed; an undocumented step was. A documented step is a smaller change than migrating
  an identifier that appears in every past entry.
- **Changelog coverage (row 3.10):** build it as a REQUIRED gate in `tools/run_all_checks.sh`, not
  an advisory workflow. It must exempt the newest reference, or run against the merge commit,
  because a pull request cannot reference its own number before it is opened. *Reasoning:* the
  check reaches no network, so nothing outside the repository can turn it red, which is the whole
  condition for a required gate here. An advisory check that nobody reads is not a control.
- **Queue order:** drain band 1 to empty before anything else, including the two corpus-wide rows.
  1.37 first because it is small, then 1.36, then 1.38. Band 4 follows, then bands 2 and 3
  interleaved by severity. *Reasoning:* the stated rule beat a throughput argument, overriding my
  recommendation to take the small row and interleave the rest. Recorded in the profile below as a
  correction to my defaults.
- **Literal example addresses (row 1.36):** per-guide judgement, the same treatment as the `ss`
  filters. Change only the probes whose pass depends on the reader having substituted the address;
  leave illustrative uses alone. *Reasoning:* same instinct as the `ss` ruling, applied a second
  time on the same day, which is what makes it a pattern rather than a one-off.
- **Verification depth:** a fourth QA round, and more, is never an issue. Cost and elapsed time are
  not accepted as reasons to stop verifying. *Reasoning:* a review round is cheap against a wrong
  guide reaching a reader, and the rounds in this session each found real defects.
- **Auto-merge:** merge on passing QA and green CI under the standing grant, rather than parking a
  verified pull request. Given after eleven open pull requests accumulated behind a review bar I
  had invented. *Reasoning:* once the evidence bar is met, waiting adds risk rather than removing
  it, because the branch drifts from `main`.
- **Unjustified work is refused, not negotiated:** on a proposed accessibility change the answer
  was "explain why we would need this", and the proposal did not survive the explanation.
  *Reasoning:* a plausible-sounding improvement with no reader harm behind it is scope, not value.
- **Enumerate before ruling:** a question about coverage was answered with a requirement to write
  the whole backlog down first, which is what produced `TODO.md`. *Reasoning:* a ruling on an
  unenumerated set is a guess, and writing it down exposed that eighteen ranked gaps had never
  been recorded at all.
- **Adopting the pack's `cntdef` rule:** vendor the rule file itself and point at it, rather than
  paraphrasing it into `CLAUDE.md`. The full normative body is carried verbatim. *Reasoning:* the
  pack is the source of truth and this repository already vendors from it under a pin, so a
  paraphrase in an auto-loaded instruction file was the wrong shape regardless of the classifier
  that refused it. Verbatim upstream text is auditable against the pack and cannot drift.
- **`VERSION` ordering (row 3.9):** `CONTRIBUTING.md`'s authoring step gains an ordering rule,
  merge in numeric order, and where that is not possible the later pull request sets the value. No
  monotonicity gate. *Reasoning:* the rule costs nothing to run and was already applied by hand
  when #50 merged before #52 so the value ended forward; a gate would have blocked that merge
  outright.
- **LangServe (row 2.9) and Mem0 (row 2.16):** keep both, with their premises corrected. LangServe
  is deprecated as of 2024-11-18 in favour of LangGraph Platform and the guide says so while still
  covering it; Mem0 ships authentication ON by default, so its section is written around
  `AUTH_DISABLED=true` rather than a missing default. *Reasoning:* a deployed instance does not
  disappear when its project is deprecated, and a tool that is secure until someone disables it is
  still an exposure this corpus covers, just a different one than the backlog row assumed.
- **Verify vendor facts before planning, not after:** all three AI-infrastructure seeds ran without
  network and marked every vendor fact unverified; opening the pages afterwards overturned two of
  the six row premises. *Reasoning:* a plan built on an unverified premise costs more to unpick
  than the verification costs to do first.
- **The #55 process deviation:** keep the change, and record the deviation. A worker's subagent
  dispatch was refused by the classifier and it ran the same guarded script directly via Bash
  instead. *Reasoning:* the refusal hit a dispatch carrying a long brief rather than the file
  change, the write path stayed open, and the content was already chosen; but a refusal answered by
  changing mechanism belongs on the record rather than absorbed silently, so it is a finding.
- **Residual guard gaps (row 1.42):** close all three. Guides require copying the complete
  assignment-and-guard unit, the interpretation comments classify a local error, an unsupported
  option or unexplained silence as inconclusive rather than a pass, AND each block unsets the
  variable before assigning it. *Reasoning:* `unset` clears a pre-existing `declare -i` or
  `declare -l` attribute and a stale exported value alike, verified across bash, dash and BusyBox
  ash, so one line closes all three demonstrated bypasses instead of documenting them as limits.
- **Onyx (row 2.15), and the pattern behind it:** rewrite the row around the compose choice, and
  open a new row for the pattern itself. Onyx's authentication has been on by default since v4.4.0;
  the exposure is that `docker-compose.dev.yml` publishes seven backing listeners on every
  interface while the prod compose publishes only nginx. *Reasoning:* Onyx's dev compose and Mem0's
  compose both show a guarded front door with the backing store published beside it, no backlog row
  describes that pattern, and it is arguably the new guide's real subject.
- **LocalAI ownership (row 1.8):** the new guide owns LocalAI and `model-servers.md` carries a
  one-sentence pointer; row 1.8 narrows to text-generation-webui coverage plus the
  `model-servers.md` Verify filter defect. *Reasoning:* this file enumerates LocalAI by name and
  outranks a `TODO.md` row, and using the row to override it would be a worker reopening a settled
  ruling, which this file's own contract forbids.
- **The subagent write path (recurring refusal):** add a permission rule allowing execution of the
  guarded helper scripts under the session scratchpad, rather than changing the convention or
  accepting the refusals. *Reasoning:* the classifier is refusing the documented path itself, three
  times now, while the direct run it permits does exactly the same thing; a rule at the actual point
  of refusal keeps the console-clean convention intact instead of eroding it by practice. The
  scripts assert every anchor and abort before any write, so the guard is not what is being relaxed.
- **The AI-infrastructure guide's scope:** one guide with two named internal shapes, auth absent or
  unset for SearxNG, LocalAI, Text Embeddings Inference and LangServe, and a guarded front door with
  the backing store published beside it for Mem0 and Onyx's development compose. *Reasoning:* the
  six no longer share the backlog's premise, but they do share that the run form rather than the
  application's authentication decides what the network sees; two shapes inside one control sequence
  is a named section, not a second guide, and the consolidation ruling enumerated all six.
- **Delivery:** one pull request for the guide, its five wiring surfaces, `exposure-index.md`, the
  `model-servers.md` pointer, the six row closures, the 1.8 narrowing, `SKILL.md`'s guide count and
  both generated artefacts. *Reasoning:* the gates check ordered membership across the build script,
  `llms.txt`, `README.md` and the site menu, so the guide and its wiring cannot land separately
  without a red build, and the changelog gate now expects every pull request to record itself.
- **Reach of the published-backing-store pattern:** the new guide carries the authoritative
  treatment and `agent-builders.md` gains a cross-reference. *Reasoning:* Dify already has its own
  worked example of the same shape, so a pointer costs nothing and duplicating the explanation is
  the drift the consolidation ruling exists to prevent. Not moved to `docker.md`, and not opened as
  a corpus-wide sweep, though the `${VAR:-default}` trap has now appeared in three unrelated tools.
- **The permission rule for the helper path: hold, and gather evidence first.** Reversing the
  earlier ruling on my own report that the evidence had weakened: several dispatches since have gone
  through with no refusal, so the three blocks may have been content-shaped rather than mechanism-
  shaped. *Reasoning:* a rule added against a misdiagnosed cause fixes nothing and quietly widens
  permissions; record each refusal with the brief that triggered it and bring back a cause.
- **Authoring the AI-infrastructure guide:** dispatch drafts to TWO families, then adjudicate and
  write as sole writer. *Reasoning:* overruled my recommendation to author directly. Two independent
  drafts are the strongest defence against a single blind spot on the largest unit attempted here,
  and the cost is a round trip on work whose plan and facts are already settled.
- **Untested Verify checks:** they ship, and each says plainly in the guide that it is reasoned
  rather than demonstrated. *Reasoning:* CONTRIBUTING rule 3 is honesty over coverage, and this
  corpus already states plainly where a tool has no native control; a reader who knows which checks
  are proven can weigh them, while a uniform-looking guide hides the distinction from the only
  person it matters to.
- **Bands 2 and 3 ordering:** strictly by the severity already recorded on each row, H before M
  before L, ties broken by effort so cheap high-severity work lands first. No re-audit first.
  *Reasoning:* the rows carry the judgement of the audit that produced them, and re-auditing before
  acting would defer every fix behind a fresh survey.

## Profile: predicting these rulings

Maintained by the orchestrator, not the maintainer. This is inference from observed rulings, and
it is fallible: it exists so that fewer questions need asking, not so that questions stop being
asked. A prediction here never substitutes for a ruling on anything irreversible or outward-facing.
Where a prediction has been wrong, the miss is recorded, because the misses are the useful part.

### Observed patterns

Every pattern below cites a ruling recorded above in this file. A pattern whose evidence is not recorded here does not belong in this list: an unverifiable prediction about the maintainer is worse than no prediction, because it cannot be checked and it compounds.

1. **Per-case judgement beats the blanket sweep.** Ruled twice, on the `ss | grep` filters and on
   literal example addresses. The reasoning both times: a check that is correct for what it
   actually claims stays, even when it shares a shape with checks that are wrong. Predict: any
   proposal phrased as "fix all N instances of X" draws "judge each of the N".

2. **Enforcement over advice, where enforcement is deterministic and offline.** Ruled on the
   changelog-coverage gate (required, not advisory) and earlier on the llms.txt alignment (add a
   gate). Predict: when a check CAN be a required gate without reaching the network, it should be.

3. **The smaller structural change, when a process step will do.** Ruled on `VERSION`: keep the
   scheme, add an authoring step to `CONTRIBUTING.md`. Predict: a proposal to change a scheme,
   format, or identifier loses to a proposal to document the step that was missed, unless the
   scheme is the thing that is broken.

4. **Strict order over pragmatic interleaving.** Ruled that band 1 drains to empty before anything
   else, INCLUDING two corpus-wide rows I had flagged as slow. This overrode my own recommendation,
   which was to take the small row and interleave the rest.
   **Correction to my own defaults: my recommendations lean too pragmatic. When the choice is
   between the stated rule and a throughput argument, predict the stated rule.**

5. **Verification has no ceiling.** Stated directly: a fourth round and more is never an issue.
   Cost and elapsed time are not accepted as reasons to stop verifying. Predict: never propose
   fewer QA rounds to save time; propose the round and say what it is for.

6. **Consolidate rather than proliferate.** Ruled that six AI-infra gaps become one guide covering
   the shared pattern with a per-tool table, not six guides. Predict: N similar artefacts draw one
   artefact with a table, unless they genuinely diverge.

7. **The reasoning comes before the action, and an unjustified premise gets challenged.** On a
   proposed accessibility change the response was not yes or no but "explain why we would need
   this", and the proposal did not survive the explanation. Predict: present the reasoning and the
   evidence, not the recommendation alone, and expect a weak premise to be rejected rather than
   waved through.

8. **Write it down before ruling on it.** A coverage question was answered with a requirement to
   produce the full backlog first. Predict: a question that asks for a ruling on an unenumerated
   set gets sent back until the set is enumerated.

9. **Throughput is welcome where quality is already evidenced.** Standing grant to auto-merge on
   passing QA and green CI, and an explicit correction when merged-ready work sat unmerged.
   Predict: once the evidence bar is met, do not wait for permission that has already been given.

### Where this profile has been wrong

- 2026-09-13, queue order. I recommended taking the small band 1 row and interleaving the rest by
  severity. The ruling was to drain band 1 entirely first. See pattern 4; my defaults were the
  error, not the ruling.
- 2026-09-13, authoring the AI-infrastructure guide. I recommended authoring directly rather than
  dispatching drafts, on the grounds that I hold the verified facts and would re-verify a draft
  anyway. The ruling was two independent drafts. That is the SECOND time a recommendation of mine
  was overruled toward more rigour, after queue order the same day, which is pattern 4 holding
  twice. The correction stands and is now evidenced rather than inferred: where the choice is
  between a cheaper path and a more thorough one, predict the more thorough one.
