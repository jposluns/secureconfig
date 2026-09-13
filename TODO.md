# TODO

Forward-looking backlog for secureconfig. Closed items move to `DONE.md`; nothing is deleted.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

## How items are numbered

Every open item is one index row in the band below that fits it. **Ids are permanent and never
reused**, including when an item is dropped, superseded, or its work reverted, and they are
decoupled from the band so an item can move band without changing identity.

Series: **1.x** fix a defect, **2.x** add missing content, **3.x** tooling and process,
**4.x** the site and adopter-facing surfaces.

Each row carries `(severity, effort)`. Severity is what a reader loses: **H** a wrong or missing
control on something commonly exposed, **M** a real gap with a workaround, **L** cosmetic or
internal. Effort is **XS** minutes, **S** under an hour, **M** a session, **L** several sessions,
**XL** a project.

Next ids: **1.6**, **2.3**, **3.3**, **4.2**.

## Queueing

Band 1 first, then 2, highest severity within each. Maintainer direction supersedes the order at
any time. Items blocked on another project are not picked, they are waited on.

## Priority 1: Fix defects

| ID | Item | Tags |
| --- | --- | --- |

## Priority 2: Add missing content

| ID | Item | Tags |
| --- | --- | --- |
| 2.4 | Coverage audit in flight: three families are auditing all 85 guides for gaps and for enhancements; its findings land here as individual rows (H, M) | `[audit]` |

## Priority 3: Tooling and process

| ID | Item | Tags |
| --- | --- | --- |
| 3.3 | Complete the `(#N)` pull-request references in `CHANGELOG.md`: PRs 3, 4, 5 and 7 are referenced nowhere, which means mapping historical bullets to the PR that shipped them (L, M) | `[changelog]` |
| 3.4 | Changelog close-out for #35, #38, #39, #40 and re-pin `VERSION`, which is stale at 1.0.37 (M, S) | `[changelog]` |
| 3.5 | Dispatch cross-family QA against a throwaway copy rather than the live worktree, so a snapshot is frozen without anyone waiting (M, XS) | `[process]` |

## Priority 4: Site and adopters

| ID | Item | Tags |
| --- | --- | --- |
| 4.2 | `site/index.html` menu group labels are `<p class="sidenav-h">`, so heading navigation skips all thirteen; promote them to real headings (L, XS) | `[a11y]` |

## Blocked upstream

| ID | Item | Waiting on |
| --- | --- | --- |
| 3.6 | Activate the AIQT hooks: `.claude/settings.json` is classifier-gated and `tools/gen_aiqt_settings.py` merges rather than overwrites | the guardrails versioning work |
| 3.7 | Re-pin `.aiqt/` to a tag: currently pinned to a `main` commit because the only tag predates the commits this repository depends on | guardrails publishing a tag |
| 3.8 | Adopt the DevProcess / OPF operational-files standard. Deferred by the maintainer on 2026-09-12; `TODO.md` stays at the repository root and the adoption script will ingest it. See the note below | the OPF tooling release |

### On 3.8, so it is not re-derived

Read from `.aiqt/core/opf/OPF-SPEC.md` and `OPF-QUICKSTART.md` rather than from a summary:

- There is **no TODO.md to DONE.md migration** under OPF. Both are deterministic generated views
  rendered from one store of versioned TOML records. An item is a `backlog_item` record; closing
  it is a state transition (`open` to `active` to `done`, or to `dropped` when declined) plus one
  worklog entry. Nothing hand-edits a generated view. The two files in this repository today are
  hand-kept and will be imported, not converted in place.
- Ids are permanent and never reused, which is the convention this file already follows.
- A declined item stays a record in the terminal `dropped` state with its reason, which is why
  `DONE.md` carries dropped rows rather than deleting them.
- Default store location is `.working/`, with `CHANGELOG.md` and `VERSION` staying at the product
  root and `VERSION` becoming generated. The maintainer has directed that this file stay at the
  root meanwhile; guardrails has captured that as an adoption-tooling requirement.
- The tooling ships in a later pack release. Adopting by hand today would mean maintaining a TOML
  store **and** rendering its views by hand with no `opf doctor` to catch drift between them,
  which is two hand-kept copies of one truth and the defect class this repository already runs
  three freshness gates against.
