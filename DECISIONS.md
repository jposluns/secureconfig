# DECISIONS

Every project Jeff Posluns maintains carries a DECISIONS.md, some public and others in private working directories; the convention is standardized across all of them, not local to this repository. The file gives an AI assistant a working model of how the maintainer decides, and it gives each settled question a single recorded answer so it is never asked again. Read it before proposing anything a past entry already covers.

Maintainer rulings, recorded so they are not re-litigated. A decision here is settled: it is not
reopened by a later review finding or by a worker's recommendation, only by the maintainer.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

Backlog rows live in `TODO.md`, closed rows in `DONE.md`, and questions awaiting a ruling in
`PENDING-DECISIONS.md`. A row may cite a decision here; a decision never carries a row's status.

Each ruling records the maintainer's reasoning as well as the ruling, and the profile at the end
generalizes across them, so that fewer questions need asking. The profile is the orchestrator's
inference and is fallible; it never substitutes for a ruling on anything irreversible or outward.

## Rulings

- **A `TODO.md` row-format gate (ratings and unique ids required), 2026-09-24: declined for now,** on the ground
  that operational tooling will be standardized by the OPF standard. On 2026-09-25 the maintainer applied the same
  ground to
  P1 (the id series), deferring it, and ruled P2 (gating row shape) covered; both are struck in
  `PENDING-DECISIONS.md`. The option chosen for P1 and P2 read: "Treat both as overtaken by the OPF
  standardization ruling"; no other reasoning was given.

- **Flower's unix socket.** The maintainer, on Flower creating its socket with mode `0777`: "this is the type of
  thing that could be easily changed. we should advise checking permissions and adjusting to optimal." So the
  guide advises how to check and tighten the permissions that govern access, rather than only stating the
  default (#339).

- **Verify marking: a corpus convention.** Every Verify step states explicitly whether it was demonstrated or
  reasoned, and the convention is enforced corpus-wide (row 3.20). This overrode my recommendation, which was
  per-guide judgement with demonstration-debt rows. No reasoning was given beyond the option's text: "Require every
  Verify step to state demonstrated or reasoned explicitly, enforced corpus-wide."

- **The CSP-hash gate's scope:** refuse any `.xhtml` under `site/`, and scan SVG documents, failing on `<script>`
  or an `on*` handler (row 3.18). No reasoning was given beyond the option chosen.

- **The weekly lychee sweep:** fail only on dead links (404s). Redirects are listed but do not fail the job (row
  3.19). No reasoning was given beyond the option chosen.

- **The vendored AIQT files' licence.** The guides stay CC0. The AIQT Guardrails material the repository vendors or
  adapts, as `.aiqt/PIN` lists it, is Apache-2.0: the pack's LICENSE and NOTICE are vendored into `.aiqt/`, and the
  CC0 statements in README, CONTRIBUTING, SECURITY and CLAUDE.md/AGENTS.md name the exception (#343). Review found
  that the earlier pin predated the pack's move to Apache-2.0, so the maintainer ruled to re-pin to an Apache-era
  commit, rather than grant Apache-2.0 to the pinned versions or label them CC BY-SA 4.0. The maintainer first asked
  whether relicensing the repository to Apache-2.0 would be easier; the answer given was that it would put
  redistribution conditions on configuration readers copy, and that earlier releases stay CC0 regardless. They then
  chose to keep CC0 with the exception. No other reasoning was given.

- **A retroactive full-panel review of #255 and #256:** run it against their current text. This overrode my
  recommendation, which was to close it without one. No reasoning was given. Its findings are rows 1.136 and 3.17.

- **P4, container ports: option A.** A container port behind a remapped publication is cited in the exposure index
  like any other mention, not allowlisted (#341). *Reasoning (as the chosen option put it):* "a scan from inside
  the container network or a pod sees the container port, so a reader who looks it up should reach the guide."

- **P3, trap clearing: option A.** Every block that holds a secret clears `trap - DEBUG RETURN ERR`,
  positional-parameter blocks included, and rule 7's fifth condition is reworded to match (#340, row 1.134). The
  same day the maintainer ruled on #340's scope: the two `ai-infra-services.md` credential blocks it touched move
  their header from curl's argv to stdin in #340 itself, and secret-bearing blocks that a trap line cannot fix
  (row 1.135 lists them: secrets already in the reader's environment, exports, and secrets on command lines) are
  recorded as that row
  and handled in per-block pull requests, argv breaches first (the `nextjs.md` `curl -b` cookie and
  `SESSION_SECRET` in grep's argv); each remaining block is judged on its own: prompt for the secret, read it from
  a file, or state it as an assumption. *Reasoning:* the maintainer stated none beyond the questions as put to
  them. P3 asked whether positional-parameter blocks should clear inherited traps as the guarded-read blocks
  already did. The scope question said the ai-infra blocks' `-H "$4"` puts the header in curl's argv, breaking
  rule 7.

- **Rule 7's trap scope and hostile-shell limits, 2026-09-24: the ERR trap is included, and two limits are stated
  as assumptions.** Blocks clear `trap - DEBUG RETURN ERR`, and rule 7 requires all three. Review of #309 showed
  that an inherited ERR trap under `set -E` reads the secret when a command fails, and the author reproduced it.
  The two limits are an inherited `shopt -s extdebug`, under which a DEBUG trap can skip the `trap -` line, and
  inherited functions named like the block's commands, which run inside the subshell and see the secret. Rule 7
  and the guides name both and say to run the block from a clean shell (`bash --norc`). To be carried in the
  rule 7 pull request after #309. No reasoning was recorded beyond that evidence.

- **Rule 7's IFS guard and DEBUG trap (row 1.133), 2026-09-24: both required.** Rule 7's guarded-read exception
  gains a clause requiring the readonly-IFS refusal (`{ unset -n IFS; } 2>/dev/null || refuse`) before the read;
  every block then current already complied (#301, #303, #306). Every guarded block also gets `trap - DEBUG RETURN`
  at the top of its subshell, and rule 7 requires it. The author reproduced the leak, a DEBUG trap that saw the
  secret, and the fix, under which nothing printed. About 15 blocks, each to be tested with the harness. To be
  carried in one CONTRIBUTING-plus-guides pull request after #309. No reasoning was recorded beyond that evidence.

- **Rule 7's environment exception covers a tool with no stdin input, 2026-09-24.** Before the ruling, a check of
  pinned sources found that natscli is not environment-only (a context JSON `password` field, `--password=file://`
  after v0.3.2, and a fisk `@argfile`); that surreal's `--pass` is environment-only, but the root user can instead
  be defined in an `--import-file`; and that nomad v2.0.7 is environment-only, with no stdin or file form, and
  `nomad login` does not save the token. The option chosen, "No-stdin framing": the exception covers a tool that
  offers no stdin input for the secret, makes no claim that the environment is the tool's only non-argv input, and
  states no file preference. Tools are named only where verified at a tag. The `nats.md`, `nomad-consul.md` and
  `surrealdb.md` conversions proceed with the prefix form plus its guard, carried in #299 round 4. No reasoning
  was recorded.

- **Rule 7's prefix assignment needs a guard, 2026-09-24.** Bash prints "readonly variable" for a prefix assignment
  to a readonly variable, then runs the tool with the inherited value, so a probe silently tests the reader's
  credential. Before the prefix form, the block clears the name in the subshell (`unset -n` then `unset -v`) and
  fails closed if that fails. Carried in #299 round 3. No reasoning was recorded beyond that evidence.

- **Exposure-index citations for a product that a row's "May be" cell does not name, 2026-09-24: add the product
  to that cell.** Only names are added. Carried in #300 round 2. No reasoning was recorded.

- **Rule 7 and tools that take the secret only from the environment (decision D1), 2026-09-24: a one-command
  prefix assignment.** The question named natscli (`NATS_PASSWORD`), `nomad` (`NOMAD_TOKEN`) and `surreal start`
  (`SURREAL_PASS`), while amended rule 7 says "never exported". The ruling allows `TOOL_VAR="$v" tool ...`, never
  `export`, with the caveat that the process's `/proc/<pid>/environ` is readable by the same user. To land in a
  CONTRIBUTING pull request, followed by the `nats.md` blocks, the `nomad-consul.md` example and the `surrealdb.md`
  block. The guard and premise rulings above refined it the same day. No reasoning was recorded beyond the
  question's point that argv would be worse.

- **A QA stopping rule, 2026-09-24: adopted as policy.** Once a pull request converges to SHIP from both families,
  non-blocking notes carry forward to the next pull request or a `TODO.md` row. Blocking findings, and in-scope
  issues the round itself caused, are still fixed first. No reasoning was recorded.

- **Two CONTRIBUTING lines on demonstrated steps, 2026-09-24: adopt both.** Every QA brief states an exposed run,
  a fixed run and the observation for each demonstrated step. Adding a Verify run means rereading the guide's
  run-provenance sentence. To land in a CONTRIBUTING pull request. No reasoning was recorded.

- **Rule 7 and named-variable keys, 2026-09-24: amend rule 7.** It allows one subshell-local variable read with
  `read -r -s`, guarded: `set +x`, unset first, never exported. Blocks that take the secret from the environment,
  such as `sqlite.md`'s `TURSO_AUTH_TOKEN` (row 1.123), are converted. To land in the same CONTRIBUTING pull
  request as the two lines above. *Reasoning:* `read` cannot target positional parameters, so this is the only way
  to read the key.

- **Exposure-index citations, 2026-09-24: a one-off pass.** A single content pull request adds the roughly 60
  missing guide citations to the port rows. An advisory report of uncited pairs is optional. No reasoning was
  recorded.

- **Six pending questions closed as overtaken by later work, 2026-09-24,** each verified against the repository
  first: the CSP-hash orphan pins (row 3.15, raised 2026-09-15), because row 3.15 is in `DONE.md`; the `ss | grep`
  sweep (2026-09-15), because no guide still filters `ss` through grep; the `mcp-servers.md` re-pin (2026-09-17),
  because the guide cites MCP 2026-07-28 throughout; the `-u` credential-quoting sweep (2026-09-17), because
  `check_guard_conventions.py` enforces it and no guide has the pattern; the Argo Workflows section (2026-09-18),
  because it is present in `workflow-orchestrators.md`; and a grammar question on #277, because #277 merged. The
  maintainer had directed the `mcp-servers.md` re-pin to go ahead; #221 carried it and added rows 1.83 and 1.84 for
  follow-up.

- **No listener-opening demonstrations until isolation exists, 2026-09-24.** No demonstration opens a listener
  until a loopback-only network namespace or equivalent isolation exists on the authoring host. An earlier ruling
  the same day, after a Ray wildcard-bind incident, added a sourced reasoned note to `ray.md` (#290). The remaining
  demonstration rows stay reasoned (2.31 to 2.35, 2.37, 2.40 to 2.43, and debt rows 1.108, 1.112, 1.114, 1.117,
  1.118 and 1.121), and work continues on the non-listener backlog. The revert path is a maintainer ruling once
  isolation exists. No reasoning was recorded.

- **The pinned-citation gate (#254), 2026-09-21: ship it advisory, with disclosure.** #254 merges as it stands; the
  docstring of `tools/check_pinned_citations.py` discloses obfuscated-Markdown and exotic evasions as a
  review obligation, matching the `check_shell_blocks` and guard-conventions precedent, and one CONTRIBUTING line
  may name that obligation. Because `main` had moved past the branch's `VERSION`, the branch was re-versioned above
  `main` before merge, for version monotonicity. No reasoning was recorded.

- **CONTRIBUTING rule 5 gains an environment-capability carve-out, 2026-09-19 (#229).** Option (C), codify the
  deviation: an all-reasoned service guide is permitted when the authoring environment genuinely cannot stand the
  service up, tracked by a backlog row, and it is never presented as verified. #229 ships reasoned with debt, and
  the amendment and the "un demonstrated" typo fix are folded into it, so that the guide and the authorizing rule
  land atomically, with no window in which the guide is live against the unamended rule. The amendment legitimizes
  #227 and #228 retroactively, with no revert. #229's squash commit message names only the `redis.md` change;
  `CHANGELOG.md` records the amendment. No reasoning was recorded for the carve-out itself.

- **Row 3.14 and `--strict-guards`, 2026-09-19: no general lexical auto-gate, and fix the false positive (#225).**
  Row 3.14 is recorded as won't-implement as a general lexical auto-gate, and `_strict_if_guards` stops flagging a
  probe already covered by an effective C2 sentinel guard (the `mosquitto.md` false positive); `--strict-guards`
  stays the opt-in manual audit tool. The first fix over-suppressed, skipping a probe that uses `$1` under a `case`
  that guards `$2`, so the maintainer chose to build bounded subject-operand matching into the strict rule only,
  leaving the main C2 output byte-identical. Round 2 left two contrived under-flags that the corpus does not
  contain, and the maintainer chose ship-and-disclose: those two, and function-parameter rebinding, are listed in
  the gate's KNOWN REMAINING BYPASSES. Row 3.14 closed in #225. The stated reason for leaving the general gate
  unimplemented is that there are no corpus true positives to gain and it would need value flow plus a
  sentinel-identification contract; no other reasoning was recorded.

- **No `Co-Authored-By` trailer in this repository's git commits, 2026-09-19.** Option (a), effective immediately.
  The attribution line in a GitHub pull request body is unaffected: it is not a git commit trailer, and `cmtidn`, a
  git-command hook, does not scan it. *Reasoning:* it keeps the pending activation of the AIQT hooks (row 3.6) from
  denying commits on `cmtidn`.

- **The C2 guard-conventions rule, 2026-09-18: fix the findings, then enforce (#220).** The first ruling was to
  work the roughly 31 probe-outside-guard findings across about nine guides down in staged pull requests, to keep
  the required gate at `--no-c2` until the corpus is clean, to revisit enforcing C2 only then, and to queue this
  after the credential-in-argv sweep. Later the same day the maintainer chose option A, the full sweep in one pull
  request: #220 fixed the recognizer to inspect every `case`-pattern alternative, waived standalone
  placeholder-free probes, guarded the three real placeholder-reaching defects (in `mcp-servers.md` and
  `model-servers.md`) and removed `--no-c2`. C2 has been enforced on `main` since #220 shipped on 2026-09-19. No
  reasoning was recorded.

- **Credentials in curl's argv, 2026-09-18: a gate rule and a corpus sweep in one pull request (#217).** Option A:
  `check_guard_conventions.py` gains a rule that flags, inside a fenced bash block, a credential placeholder
  (`-u <user>:REPLACE_WITH_*`) and the broader credential-in-argv class (tokens and signed URLs carrying a
  substituted secret in curl's argv), and the corpus is swept to safe handling (single quotes, stdin or a config
  file) as fix plus recurrence guard. The `pocketbase.md` HEAD-asserts-content and `fronting-auth.md`
  timeout-conclusion items are separate probe-quality observations, outside the rule's scope. When the new gate
  revealed the true scope, the maintainer ruled "Full sweep now": every real-credential locus, beyond the guides
  first named, is rewritten to stdin (`--config -` or `--header @-`) in #217, superseding the argv-mitigation notes
  some guides carried, and dummy negative controls that are not real secrets (in `litellm.md`, `ollama.md` and
  `mlflow.md`) are waived with `# guard-conventions: allow <reason>`. The rule and the sweep are coupled, since any
  unwaived locus turns the gate red. No reasoning was recorded.

- **An Argo Workflows section in `workflow-orchestrators.md`, 2026-09-18 (#218).** Option A: a separate follow-up
  pull request adds the section, covering the auth-mode boundary (`--auth-mode=client` is the default since v3.0,
  and `server` mode gives clients unauthenticated access under the server's Kubernetes identity), port 2746,
  service account scoping, SSO and RBAC, and a matched `/api/v1/workflows` probe, and the guide's title names six
  tools. It is audited by two families like any guide change. No reasoning was recorded.

- **The guard-conventions gate (row 3.11), 2026-09-14: the narrow, zero-false-positive gate.** Option (a):
  keep C1-MISSING-Q, narrow C1-MISSING-G to unglobbed `[` or `{` URLs, register the gate with `--no-c2`, open a
  tracked row for reworking C2, and fix the two real missing-`-q` defects in a split pull request. Implementation
  was to proceed with independent verifiers. C2 was enforced later (#220, above). No reasoning was recorded.

- **Ship the 86th guide (`ai-infra-services.md`, #60) with Verify checks 2 to 7 marked reasoned,
  tracked by backlog row 2.24.** The rule 5 this pull request tightened says a service that runs in a
  container on ordinary hardware is not impractical to stand up, and two QA families called the mark's
  stated prerequisite, "no container runtime in the authoring environment", a fig leaf; on the rule's
  plain reading they are right, because the missing runtime is a property of the authoring host, not
  of the services. Ship anyway: the guide's factual content is verified at source and survived five QA
  rounds, what is unproven is only the checks' discrimination against live deployments, and the
  Demonstration-status paragraph states that shortfall plainly with row 2.24 carrying the debt.
  *Reasoning:* a factually-sound guide whose single gap is disclosed and tracked serves a reader
  better than withholding it, and better than amending the rule to pass the work, which was the
  rejected option and would weaken a control the same change had just tightened. *Profile:* the
  maintainer ships a disclosed-and-tracked shortfall rather than holding for perfection, of a piece
  with the standing "honesty over coverage" and "a reader with a flagged guide beats no guide"
  rulings; and will not weaken a control to clear a blocker, even one the assistant itself proposed.

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

- Queue order. I recommended taking the small band 1 row and interleaving the rest by
  severity. The ruling was to drain band 1 entirely first. See pattern 4; my defaults were the
  error, not the ruling.
- Authoring the AI-infrastructure guide. I recommended authoring directly rather than
  dispatching drafts, on the grounds that I hold the verified facts and would re-verify a draft
  anyway. The ruling was two independent drafts. That is the SECOND time a recommendation of mine
  was overruled toward more rigour, after queue order the same day, which is pattern 4 holding
  twice. The correction stands and is now evidenced rather than inferred: where the choice is
  between a cheaper path and a more thorough one, predict the more thorough one.
- Verify marking and the retroactive review, both on 2026-09-25. I recommended per-guide judgement for Verify
  marking; the ruling was a corpus-wide, enforced convention, which is pattern 2 (enforcement over advice)
  outweighing pattern 1 (per-case judgement). I recommended closing a retroactive review of two merged pull
  requests without one; the ruling was to run it, and it found defects in both (rows 1.136 and 3.17). Both are
  pattern 4 again: where the choice is between a cheaper path and a more thorough one, predict the more thorough one.
