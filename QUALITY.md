# secureconfig Guide Quality Standard (GQS 1.0)

This is the published standard every secureconfig guide is held to. `CONTRIBUTING.md` ("What a
guide needs", rules 1 to 9) is the binding floor: a guide that fails it does not ship, and the gate
suite (`tools/run_all_checks.sh`) enforces the mechanical part of that floor. This standard sits
above both. It names the ceiling, makes it scorable, and gives each guide a verdict and, where it
falls short, the named criterion that stops it.

GQS 1.0 is machine-checkable where it can be and judged by hand where it cannot. The scored matrix
of every guide is `tools/guide_quality.tsv`, published at `/quality/` on the site; the structural
gate over that matrix is the `guide-quality` section of `tools/run_all_checks.sh`. A criterion that
a parser would only pretend to score is scored by a reader, not faked.

## 0. Definitions

**Guide types.** Every guide is one of four types, and several criteria read differently per type.

| Type | Meaning | Examples |
|---|---|---|
| S | Single tool or product family, numbered steps | `jupyter.md`, `vault.md`, `redis.md` |
| C | Catalogue, one H2 per tool, shared Verify | `admin-uis.md`, `devops-uis.md`, `model-servers.md` |
| X | Cross-cutting control or concept | `cors.md`, `authentication.md`, `secrets.md` |
| K | Checklist or index, links to fixes, no own Verify or Sources | `common-mistakes.md`, `exposure-index.md` |

**Enforcement classes.** Each criterion carries one of three labels.

- **GATE**: a section of `tools/run_all_checks.sh` fails the tree when the criterion fails. No
  reader scores it; the cell is PASS when the suite is green and the guide has no grandfathered
  entry.
- **TOOL**: a deterministic script can compute it today, but no gate blocks on it yet. Section 3.6
  lists which of these should become gates.
- **JUDGMENT**: a reader with the guide and its sources decides. A guide is scored independently by
  two readers before it graduates.

**Cell levels.** `PASS`, `PARTIAL`, `GAP`, `n/a` (only where a criterion defines it), and `?` (not
yet scored). Group G (readability) has no GAP level: GAP is reserved for failures that can mislead
a reader or leave a deployment exposed, and readability never does that on its own.

**HIGH-class GAP.** A GAP on M1, A1 (wrong bind), A2, B1, B2 (control exists), C1 (wrong absence),
C2 (lint sold as demonstration), E2, or E3 is HIGH-class. One HIGH-class GAP makes the verdict
NEEDS-WORK regardless of every other cell, because each of these is a defect a reader can copy into
an internet-facing system.

## 1. Master criteria

Thirty criteria in ten groups. Each gives a one-line definition, the enforcement class, and what
PASS, PARTIAL and GAP look like. The ids are the compliance-table columns.

### Group M: Mechanical floor

**M1 Gate-green and baseline-free.** GATE.
Every section of `tools/run_all_checks.sh` passes on the tree, the guide has no entry in any
baseline or allow file, and every `guard-conventions: allow` line in the guide carries a reason.
- PASS: suite green, no deferred-work entry, every waiver reasoned.
- PARTIAL: suite green, but a deferred-work entry remains or a waiver lacks a reason.
- GAP (HIGH): the suite fails on this guide. Unmergeable, so this is only ever seen on a branch.

A deferred-work entry records something the guide still owes (a Verify-marking baseline entry for a
paragraph that would attach to a DEMONSTRATED fence or a step with no concrete command, or an
over-length claim awaiting a split). A reasoned waiver records a deliberate, reviewed exception and
does not count against M1 (a bracket-range or exposure-index allow entry with its reason, or a
DEMONSTRATED evidence text grandfathered by design).

### Group A: Coverage

**A1 Listener inventory.** JUDGMENT.
Every listener the vendor documents (primary, admin or management API, metrics, cluster or peer,
debug or profiling, UNIX sockets, embedded stores) is named with its default bind and port and told
what to do with it: keep loopback, front it, or disable it.
- PASS: every documented listener addressed; the exposure index carries each port.
- PARTIAL: the primary listener is right, a secondary one is not mentioned.
- GAP: the primary listener's default bind is not stated or is stated wrong (HIGH when wrong).
- n/a: type X guides with no listener, type K.

**A2 Five-control walk per tool.** JUDGMENT.
For every tool the guide covers, each of bind or exposure, TLS, authentication (including first-run
and default credentials and open signup), MFA, and secret handling (keys at rest, well-known
default secrets, rotation) is either configured with verified syntax or stated absent under C1.
- PASS: five of five resolved for every tool.
- PARTIAL: one control unresolved for one tool.
- GAP (HIGH): bind, TLS or authentication unresolved for any tool, or two or more controls unresolved.
- n/a: type K; for type X the walk reads as the control's own facets.

**A3 Tool-specific hazards.** JUDGMENT.
The controls peculiar to this tool that an attacker reaches first are addressed: generated
initial-credential files, signup defaults, webhook or outbound SSRF allowances, privileged
executors and Docker-socket access, debug or profiling routes, tokens that bypass interactive MFA,
secret keys shipped with well-known defaults, public share links, bundled registries.
- PASS: the walk is complete; nothing a sibling guide covers for a comparable tool is missing.
- PARTIAL: one or two omissions a sibling covers, none leaving a default-exposed path.
- GAP: an omission that leaves a default-exposed path, or three or more omissions.

**A4 Sibling parity.** JUDGMENT.
In a type C guide, and in a type X guide that configures several products, every tool's section
resolves the same control walk, and any deliberate asymmetry is explained in the section.
- PASS: symmetric, or asymmetries stated.
- PARTIAL: one tool materially thinner with no explanation.
- GAP: a tool section at a fraction of its siblings' walk.
- n/a: type S, type K.

**A5 Login-abuse control.** JUDGMENT.
For every interactive password login the guide configures, a brute-force, lockout or rate-limit
control is named: native, at the fronting proxy, or a fail2ban filter by name; or its absence is
stated and `authentication.md` rule 9 is linked.
- PASS: named for every password login.
- PARTIAL: named for some logins only.
- GAP: not named anywhere and the tool has a password login.
- n/a: no password login in the guide.

### Group B: Accuracy and citation

**B1 Token trace.** JUDGMENT (the fence-to-claim and claim-to-source structure is GATE).
Every flag, key, environment variable, CLI option, SQL statement and stated default appears on a
cited page or in a pinned source file.
- PASS: zero misses in the trace.
- PARTIAL: a token's cited page does not carry it but another canonical vendor page does.
- GAP (HIGH): a token or default not in any vendor material, or stated wrong.

**B2 Source authority.** JUDGMENT.
Whether a control exists, and what it defaults to, is decided from the vendor's reference,
configuration reference, CLI reference, or source at a pin, never from a quickstart, tutorial or
blog. A "no native control" statement cites the reference page or a source trace.
- PASS: every existence and default statement rests on reference-grade material.
- PARTIAL: a statement rests on a tutorial page while a reference page exists.
- GAP: absence inferred from an introductory page (HIGH when the control exists).

**B3 Pin and rolling discipline.** GATE for new mutable GitHub refs and for the basis in each
Sources item; JUDGMENT for the rest.
Source files are cited at a tag or commit; vendor documentation pages are labelled
`(rolling documentation, checked <Month Year>)` or carry the documented version; a demonstration
names the binary version it ran.
- PASS: every item pinned or labelled rolling with a month; every pin confirmed to exist upstream.
- PARTIAL: rolling pages unlabelled, or a tool with numbered releases cited only through rolling pages.
- GAP: a mutable ref grandfathered in the baseline, or a pinned tag not confirmed upstream (HIGH when claims rest on it).

**B4 Internal consistency.** TOOL for the generated header and counts; JUDGMENT for the rest.
The header sentence equals the JSON tallies, prose and claim texts do not contradict, Verify
declarations describe the fence they attach to, and the H1 names what the body covers.
- PASS: no inconsistency found.
- PARTIAL: a wording inconsistency.
- GAP: a body-versus-claim contradiction, or a declaration that describes a different check than its fence.

### Group C: Honesty and marking

**C1 Absent-control statement.** JUDGMENT.
Where a tool lacks native TLS, authentication, MFA, rate limiting or at-rest secret protection, the
guide says so in one plain sentence, gives the fronting-layer pattern with a link to the house
guide, and cites the reference that shows the absence.
- PASS: every absent control stated this way.
- PARTIAL: absence implied but not stated.
- GAP (HIGH): an invented option, or "no native control" stated for a control that exists.

**C2 Marking truthfulness.** GATE for presence of a declaration with provenance text; JUDGMENT for
its truth.
Every REASONED declaration names the specific unavailable prerequisite, the command or request, the
expected exposed and fixed outcomes, and the cited passage that distinguishes them. Every
DEMONSTRATED declaration records both runs, what each observed, and the binary version. Local
`bash -n`, ShellCheck and stub runs are labelled as syntax or guard checks and never presented as
service behaviour.
- PASS: every unit meets this.
- PARTIAL: a boilerplate prerequisite with no named missing capability, or expected outcomes missing on some units.
- GAP (HIGH): DEMONSTRATED without both runs recorded, or a lint run presented as a demonstration.

**C3 Time-sensitive hedges.** JUDGMENT.
Pricing, tiers, plan features, defaults the vendor has announced will change, near-future dated
commitments and pending advisories each carry "at the time of writing" or a date, a source pointer,
and (for a dated commitment) a re-verify TODO row.
- PASS: every volatile fact hedged and pointed; dated items have rows.
- PARTIAL: hedge present, no TODO row for a dated commitment.
- GAP: a volatile fact stated as timeless.
- n/a: no volatile facts.

**C4 Demonstration decision.** JUDGMENT.
A Verify fence is DEMONSTRATED when an authorized environment could reproduce the exposed state (the
binary obtainable, a loopback listener permitted, the exposed configuration reproducible), and
REASONED only under `CONTRIBUTING.md` rule 5's allowance with the prerequisite named.
- PASS: the decision is right for every fence.
- PARTIAL: a feasible loopback stand-up skipped for a fence that needs only the binary, with a record.
- GAP: REASONED used to skip feasible work with no recorded reason, or a demonstrated binary version not recorded.
- n/a: type K.

### Group D: Version basis and currency

**D1 Release basis for version-gated statements.** JUDGMENT.
Every "since X", "X+", "the default changed in X", release-specific default and "fixed in X"
statement rests on a component whose basis is a tag, release or commit; a rolling documentation
component never anchors a version-gated claim alone.
- PASS: every version-gated claim anchored to a non-unknown basis.
- PARTIAL: anchored to a rolling component while a pinned component for the same tool exists.
- GAP: the body reasons about releases with no recorded release basis.
- n/a: no version-gated statements.

**D2 Currency within policy.** TOOL (host-run and networked, not a gate).
Each pinned component is at the latest upstream release found on the scoring date, or at the latest
plus the last release of the previous major where the two differ (ruling of 2026-11-04).
- PASS: no component behind on the scoring date; no open version-currency row.
- PARTIAL: a minor release behind with an open row.
- GAP: a major release behind with no row, or a basis the scorer could not confirm exists upstream.
- n/a: no pinned components.

**D3 Date coherence.** TOOL candidate (deterministic; not a gate today).
The Sources heading month equals the JSON `documentation_checked` month and names the month of the
whole-guide documentation pass; a per-item "(checked <Month Year>)" marks a later item-level
recheck only; no item month is earlier than the heading month.
- PASS: coherent under this rule.
- PARTIAL: later item months present with no statement of what the heading month means.
- GAP: an item dated earlier than the heading, or a heading month later than any documentation read.

### Group E: Verification depth

**E1 Per-control check.** JUDGMENT (`CONTRIBUTING.md` rule 9).
Every setup step or tool section that binds, restricts, requires, disables or rotates something has
at least one concrete Verify check naming the command or request, where it runs, and the outcome
that tells the exposed state from the fixed one.
- PASS: every control mapped to a check.
- PARTIAL: a tool or control covered only by the generic listener inventory.
- GAP: a control section with no check at all.
- n/a: type K.

**E2 Discriminating checks.** GATE for unfiltered `ss` and TLS-verification flags; JUDGMENT for the rest.
Each fence has a positive control; treats transport or TLS failure, redirects and a proxy's 401 as
inconclusive, never as fixed; reads the body or the specific header rather than the status alone;
and uses the status convention (0 pass or unclassified, 1 finding, 2 guard refusal, 3 inconclusive).
- PASS: every fence meets this.
- PARTIAL: legacy fences ending 0 on a finding or lacking a positive control, with the guide saying so.
- GAP (HIGH): a check that passes while the service is still reachable.

**E3 Guard and secret handling beyond the gate.** GATE for argv credentials and reserved hosts;
JUDGMENT for the rest.
The `PASTE_WHOLE_BLOCK` marker and count guard, reserved-name refusal, control-character refusal,
`trap - DEBUG RETURN ERR` and the clean-shell statement at every block that takes a secret,
credentials on stdin, and the fail-closed clear guard before a prefix assignment.
- PASS: every block meets this.
- PARTIAL: a legacy guard shape noted in the guide.
- GAP (HIGH): a secret in argv without the exception's burden met, or a guard that warns and then runs anyway.

### Group F: Structure and conventions

**F1 Title and headings.** TOOL candidate for the Verify heading and H1 coverage; JUDGMENT for the rest.
The H1 names every tool with its own section (type C) or the product and its headline controls
(type S); the Verify H2 is plain ("## N. Verify") with its declaration in the first paragraph or on
its `###` children; every heading declaration is at most two sentences; ATX headings only.
- PASS: all of the above.
- PARTIAL: the declaration sits in the Verify H2, or a heading carries a multi-paragraph declaration.
- GAP: the H1 omits tools the guide covers.

**F2 House shape for the type.** GATE for Verify and Sources presence and the generated top block;
JUDGMENT for order and content.
Each type has its shape: type S numbered steps in the order bind, TLS, authentication, MFA, secrets,
then tool-specific controls, Verify, optional Common mistakes, Sources, AI section; type C per-tool
H2 sections with a shared Verify; type X rules or sections with Verify; type K a checklist linking fixes.
- PASS: the type's shape, with inline source links on every step.
- PARTIAL: order deviations, or a step with its source only in Sources.
- GAP: no risk statement, or Verify or Sources missing.

### Group G: Readability (PASS or PARTIAL only)

**G1 No boilerplate repetition.** TOOL candidate.
A sentence or clause of 80 characters or more is not repeated verbatim more than twice in a guide; a
limitation that applies across a Verify section is stated once at the top and referenced.
- PASS: no such sentence appears more than twice.
- PARTIAL: three or more occurrences.

**G2 Reader voice.** JUDGMENT.
No authoring or QA vocabulary (TODO row numbers, review rounds, drafter names), no internal process
references, configuration before commentary, and a reader can execute each step without reading its
provenance.
- PASS: none found.
- PARTIAL: authoring vocabulary present, or provenance narrative interleaved with the steps.

**G3 Provenance placement.** JUDGMENT.
Authoring records (`bash -n`, ShellCheck versions, stub matrices, form histories, lint counts) live
in one subsection at the end of Verify, and each fence or heading declaration points there in at
most two sentences.
- PASS: one record subsection; short declarations.
- PARTIAL: the subsection exists but the detail is also copied into every heading declaration, or records are scattered.

### Group H: AI-assistant section

**H1 Claim inventory completeness.** GATE for fence mapping, evidence quotes, component use and
claim length; JUDGMENT for coverage.
Every control section's substantive assertions have a claim; every component source is referenced by
at least one claim; version qualifications in claim texts match the body.
- PASS: complete, zero unreferenced sources.
- PARTIAL: unreferenced sources listed, or a control section with no claim.
- GAP: a stated control with no claim and no source.

**H2 Intro and header read correctly.** JUDGMENT (the header sentence itself is generated).
The intro paragraph names the tool, says the guide helps the reader's AI assistant, and lists the
headline controls accurately against the body; the generated header's tallies read correctly.
- PASS: accurate.
- PARTIAL: a stale or inaccurate headline-control list, or a tally wording that misleads.
- GAP: the intro describes a different scope than the body.

### Group I: Links and cross-guide coherence

**I1 External citations canonical and alive.** TOOL (weekly link sweep, advisory); JUDGMENT for canonicality.
Each Sources item is the vendor's reference, configuration or CLI page, a source file at a pin, a
standard, or a vendor announcement; a blog post is cited only for a fact no canonical page states,
and is labelled; the last weekly sweep reports no dead link in the guide.
- PASS: canonical throughout, sweep clean.
- PARTIAL: a moved or redirected page, or a labelled blog citation.
- GAP: a dead link, or a blog as the sole authority for a control.

**I2 Cross-guide consistency and non-duplication.** GATE for local links and exposure-index ports;
JUDGMENT for the rest.
Shared controls link the house guide plus one local sentence; the same fact in two guides carries
the same basis; `exposure-index.md` and `common-mistakes.md` carry the guide's ports and recurring
mistakes where they fit.
- PASS: linked, consistent, indexed.
- PARTIAL: duplicated text drifting from the house guide, or a sibling-basis mismatch.
- GAP: contradictory guidance between two guides.

### Summary of enforcement classes

| Class | Criteria |
|---|---|
| GATE (whole or in part) | M1, B3, C2, E2, E3, F2, H1, I2 |
| TOOL (host-run or advisory today; gate candidates in 3.6) | B4, D2, D3, F1, G1, I1 |
| JUDGMENT only | A1, A2, A3, A4, A5, B1, B2, C1, C3, C4, D1, E1, G2, G3, H2 |

Fifteen criteria are pure judgment. That is the honest shape of this corpus: the gates already hold
the floor hard, and what separates EXEMPLARY from SOLID is almost entirely coverage, authority,
demonstration decisions and readability, none of which a parser can see.

## 2. Types of decisions

The recurring decisions every guide makes, with the house answer or the deciding factors. A scorer
uses these to judge whether a guide decided correctly; an author uses them before writing.

**1. Single-tool guide or catalogue section.**
A tool gets its own guide (type S) when its five-control walk plus its tool-specific hazards need
more than roughly eight controls, when it has its own release train, or when it has three or more
hazards of the A3 kind. A catalogue section (type C) is for a tool whose whole posture is "bind
privately, change the default credential, front it with authentication and TLS". A new guide is
typed at seed time by this test, and the type is recorded in its compliance row.

**2. When to split a version-basis component.**
Split when two releases differ in a documented behaviour the guide states, when a source file is
pinned and a documentation page is rolling for the same product, and when a demonstration ran at a
different version than the sources cite. Do not split when the two releases are identical: keep only
the latest (the 2026-11-04 ruling). A component with basis `unknown` is for rolling documentation
only; a tool with numbered releases gets a basis.

**3. Version-pin strategy.**
Three legitimate pins, chosen per fact. A source pin (tag or commit) when the fact is behaviour in
code. A rolling documentation citation, labelled with its month, when the fact is the vendor's
instruction and the page carries no version. A demonstration pin, the binary version that ran, which
stays where it was even when the source citations move. Never a `main` or `master` ref (gate). When
moving a source pin, re-read every claim it anchors and say in the CHANGELOG which facts were
re-confirmed.

**4. REASONED or DEMONSTRATED, and when a stand-up is feasible.**
DEMONSTRATED is required when an authorized environment can obtain the binary, open a loopback
listener and reproduce the exposed configuration; `CONTRIBUTING.md` rule 5 says a service is not
impractical to stand up merely because it runs in a container or because the binary is absent where
it could be obtained. A REASONED declaration whose only prerequisite is "no listener on this host"
is PARTIAL on C4 unless the guide also says why a demonstration was unavailable for that service.
REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form; it is an accepted end state when labelled and never converts an unknown into a verified result.

**5. What belongs in Verify and what belongs in prose.**
Verify holds runnable, guarded fences, one per control or one that classifies several, plus the
sentences a reader needs to substitute values and read results, plus the declarations. Why a control
matters stays in the step that sets it. Authoring records go in one closing subsection (G3). A Verify
fence tests the exposed state as well as the fixed one; a line that says "confirm the setting took
effect" is not a check (rule 9).

**6. A control the tool lacks.**
Say it in one sentence, cite the reference or source trace that shows it, give the fronting pattern
with a link, record it as a claim, and point at OWASP only where the gap is application security
rather than deployment exposure. Never infer absence from a quickstart. Never invent an option to
fill the hole.

**7. In scope or out of scope.**
In: bind and exposure, TLS, authentication, MFA, secret handling, and the controls that follow from
them for the deployed service (login abuse, listener-level resource limits where the tool exposes
them, audit logging where it is the control that detects the exposure, webhook and outbound SSRF
allowances, secrets in CI logs and artifacts, executor privilege). Out: injection, deserialization,
business logic, dependency hygiene, general observability. A borderline control is included when a
sibling guide includes it for a comparable tool; parity decides.

**8. Cross-guide reference or duplication.**
Link the house guide and add one local sentence with the tool-specific name. Where two guides state
the same fact, they carry the same basis, and the guide that moves first opens a row for the other.
Facts that must stay in step across guides get one shared re-verify row that names both.

**9. Time-sensitive vendor facts.**
Pricing, tiers, plan features, defaults the vendor says will change, and dated commitments carry "at
the time of writing (<Month Year>)" or the date, a source pointer, a claim, and a re-verify row with
the date. Advisories are cited by id with the affected and fixed ranges and the release the guide
verified.

**10. The two date fields.**
`documentation_checked` and the Sources heading name the month of the whole-guide documentation
pass. A per-item "(checked <Month Year>)" is added only when that item was re-read later; an item is
never dated earlier than the heading. "Metadata reviewed" is the last review of the claim inventory
and establishes no new documentation check.

**11. Placeholder choice.**
A reserved address (`203.0.113.10`, `app.example.com`) in configuration and illustrations, where an
unreplaced value yields a visible wrong result; `REPLACE_WITH_...` on a guarded `set --` line in any
probe whose pass is "nothing answered", with the command inside the guard (rule 6). A reserved name
is never a probe target (gate C4).

**12. Title, headings and numbering.**
Type S: the H1 names the product and its headline controls; steps are numbered and Verify is a
numbered step. Type C: the H1 lists every tool that has a section; sections are per-tool H2s; Verify
is a plain H2. Declarations never ride on the Verify H2. Every catalogue section's tool name also
appears in the intro paragraph.

**13. Common mistakes section.**
Optional. Include it when the guide's recurring mistakes are not already rows in
`common-mistakes.md`; otherwise add the row there and link it. Never both without the local section
pointing at the shared row.

**14. Exit-status convention for Verify fences.**
New and changed fences use 0 pass or unclassified, 1 finding, 2 guard refusal, 3 inconclusive, exit
once after cleanup, a finding outranks inconclusive. A legacy fence that ends differently is brought
in line when its block is next touched, and the guide says which fences are legacy until then.

**15. Where a secret goes in a probe.**
Stdin (`--header @-`, `--config -`) wherever the tool offers it; a one-command prefix assignment with
the fail-closed clear guard where the tool reads the environment and has no stdin input; argv only
under rule 7's third exception with its pinned trace, disclosure and two run conditions. A deliberate
non-secret test value stays in argv with a reasoned waiver line.

## 3. The matrix and the verdict

The scored matrix of every enrolled guide is `tools/guide_quality.tsv`, the source of truth, with a
row per guide and a cell per criterion group; the `guide-quality` gate section holds it well-formed.
The published view is the `/quality/` page on the site. A findings ledger,
`tools/guide_quality_ledger.tsv`, carries the long-form detail behind each non-PASS cell and is
advisory in GQS 1.0.

**Cell grammar.** A cell holds the worst level in the group followed by the ids of every non-PASS
criterion:

```
P                      every criterion in the group PASS or n/a
PARTIAL(A3,A5)         worst level PARTIAL; these criteria are PARTIAL
GAP(A2) PARTIAL(A3)    worst level GAP; GAP ids first, then PARTIAL ids
?(I1)                  a criterion not yet scored; blocks EXEMPLARY, counts as PARTIAL for the verdict
n/a                    every criterion in the group n/a for this type
```

**Verdict.** Rule-based, never a sum, because a sum hides a HIGH-class GAP behind twenty PASS cells.

| Verdict | Rule |
|---|---|
| NEEDS-WORK | any HIGH-class GAP (section 0), or three or more GAPs of any class |
| MINOR-GAPS | one or two GAPs, none HIGH-class |
| SOLID | zero GAPs; at least one PARTIAL or `?` in groups A to F, H, or I2 |
| SOLID+ | zero GAPs; every PARTIAL and `?` is in G1, G2, G3, I1 or D2 |
| EXEMPLARY | every cell PASS or n/a, and a second reader found nothing |

A verdict never decays on its own; it is re-scored when the guide changes or when the standard's
version changes. A cell not yet scored is `?`, which counts as PARTIAL and blocks EXEMPLARY, so a
guide reaches EXEMPLARY only once every cell is a real PASS or n/a.

## 3.6 What can be machine-checked

Each candidate is deterministic and offline, reads the tree only, and is monotonic in time. The
`guide-quality` gate over `tools/guide_quality.tsv` is the first: every guide has exactly one row,
cells use the grammar above, the verdict column equals the rule computation, and a row's recorded
body digest equals the guide's current `body_sha256` or the row is marked `stale`. The remaining
candidates (a Verify-heading declaration check, an H1-coverage check for type C, a Sources-month
coherence check, a repeated-sentence counter, and an unknown-basis heuristic) land as the hardening
lane clears each class. A criterion that a parser could only pretend to score (A1 to A5, B1, B2, C1,
C3, C4, E1, G2, G3, H2) stays a judgment, because a heuristic that pretends to score coverage would
produce the false confidence this repository's own `CONTRIBUTING.md` warns against.
