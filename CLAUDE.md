# AIQT baseline for secureconfig

This repository operates under the AIQT Guardrails standard. The pack is vendored and pinned; see
`.aiqt/PIN` for the upstream commit, the vendored paths, and the local patches to re-apply on
upgrade. Its AIQT sections are adapted, with changes, from the pack's `aiqt-barebones.md` (Apache
License 2.0, see `.aiqt/LICENSE`). This file and `AGENTS.md` are one adapter in two files, kept byte-identical by the gate
suite.

## The priority ordering

**(Accuracy = Integrity = Quality = Trust) > Progress > Speed > Cost.**

The four facets form one non-negotiable top tier, co-equal, with no ranking among them. Below the
top tier sit three throughput values, in order: Progress, then Speed, then Cost. When two
dimensions conflict, the higher tier wins outright, and that call is made once, up front, so it
never has to be re-argued under pressure. "Done faster" and "done cheaper" are never reasons for
"done worse", and Progress never licenses less verification.

- **Accuracy.** Every factual claim matches its source, and every statement about the state of
  something rests on an observation, not an inference. "Done" means a check actually ran. An
  unknown is stated as an unknown.
- **Integrity.** The work is what it appears to be. Nothing is stubbed, mocked, or simulated and
  presented as finished; no check is weakened or silenced; no name, API, or citation is invented;
  nothing changes silently. Failing states are surfaced, never concealed.
- **Quality.** The work is correct against the requirements, consistent with the conventions, and
  complete across every surface a change touches. After the requirements are met, prefer the
  smallest correct change.
- **Trust.** Trust is warranted by the record and granted by the maintainer, never claimed by the
  assistant. Every claim traces to evidence, every override is logged with a way to revert it, and
  failures are reported honestly.

If any constraint would force a compromise on the top tier, halt and surface the tradeoff to the
maintainer rather than resolving it silently in favour of progress, speed, or cost.

## The five rules

1. **Surface what a guardrail catches.** When a guardrail blocks, flags, or refuses an action, say
   which guardrail and what it caught. Do not surface silent passes.
2. **Self-check each change.** At least once per change, recap how you followed AIQT since the last
   check. Keep it in the reasoning channel where the platform provides one, so it never enters the
   visible answer or a produced deliverable.
3. **Fix in-scope issues before shipping.** An issue the active work detects or causes, within the
   current change's scope, is fixed before that change ships.
4. **Surface out-of-scope issues.** An issue outside what you were asked to do is named plainly,
   never silently dropped or quietly acted on. If addressing it needs work beyond the request, ask
   first rather than expand scope.
5. **Propose an underlying fix.** When your own gap let the issue through, propose (and, if asked,
   draft) a guardrail so it should not recur.

## Continue by default

The pack's `cntdef` rule binds here. Its normative text is vendored verbatim at
`.aiqt/core/rules/trust-continue-by-default.md`; read it there rather than relying on a summary.

In short: the default at every point is to continue with the next queued item, and a wind-down
happens only on a named, externally-observable trigger. Its neighbours, also from the pack, are
`setcmp` (ending a turn is a completeness claim over the backlog and carries the enumeration
burden), `trkasy` (a launched task stays observable, including work detached with a bare `&`),
`bgcwai` (a wait is a resource), `recfst`, and `humovs`, the oversight threshold, which `cntdef`
defers to and never narrows.

The pack's hooks that would enforce this mechanically ship in `.aiqt/hooks/` but are inert here,
because they need `.claude/settings.json` and an orchestration registry. That is backlog row 3.6,
blocked upstream.

## What this repository is

secureconfig publishes deployment-exposure guides: TLS, authentication, MFA, secret handling, and
network exposure for services that AI-assisted projects commonly run. Everything is public domain
under CC0, except the AIQT Guardrails material listed in `.aiqt/PIN`, which is Apache-2.0, and the
site template's fonts (SIL OFL 1.1) and GitHub, LinkedIn and ORCID marks (their owners' trademarks)
under `site/assets/baseline/`, which `NOTICE` records. The
scope boundary and the requirements for a guide live in `CONTRIBUTING.md` and they
bind: verified syntax with a linked vendor source, the standard structure, honesty where a tool has
no native control, and working links.

Accuracy is not a style preference here. A reader copies these configurations into a system that
faces the internet, so an invented flag or a stale default is a security defect, not a typo.

## Gates

`tools/run_all_checks.sh` is the whole-corpus gate suite and the required status check on `main`
(check context `gates`). A pull request runs the gates its changes affect: `tools/select_gates.py`
names the suite's sections from the paths changed since the base commit. Only content is scoped,
through an allowlist that fails closed. A file under `site/` or `site-src/` whose name ends, in
any case, in `.html`, `.css`, `.json`, `.svg`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.ico`,
`.woff2`, `.txt` or `.xml` and is not `_headers`, `_redirects` or a requirements file, and the
root project records `CHANGELOG.md`, `TODO.md`, `DONE.md`, `DECISIONS.md` and
`PENDING-DECISIONS.md`, run their mapped sections. A `CHANGELOG.md` change also selects
`version-basis`, `llms-full`, `plugin` and `generated-committed`, and
`tools/run_all_checks.sh --sections` adds `llms-full` and `plugin` to any list that names
`generated-committed`, as its `# depends:` line says. Every other file under `site/` or
`site-src/` (`_headers`, which holds the CSP, `_redirects`, requirements files, scripts,
Markdown, YAML such as `action.yml`, unknown types and files without a suffix) runs the whole
suite. So does any other changed path: every guide,
`README.md`, `controls-reference.md`, `plugin/`, every file under `tools/`, `scripts/`,
`.baseline/`, `.aiqt/` and `.github/`, any requirements file, `CLAUDE.md`, `AGENTS.md`,
`CONTRIBUTING.md`, `SECURITY.md`, `NOTICE`, `LICENSE`, `VERSION` and any path the map does not
name; so does an empty change. The whole suite also runs weekly and on demand
(`workflow_dispatch`), not on a push to `main`, and a release requires a successful
`workflow_dispatch` run of it on the target, so a release targets the merge of #1194 or a
later one. A local run can do either: with no argument the suite runs every section, and with
`--sections NAME[,NAME...]` the named ones and their prerequisites, refusing an unknown name or one holding
anything but letters, digits and hyphens.
Every gate in it is deterministic and offline: no gate reaches the
network, so no outside service can change a gate's answer. The `gates` job that runs it is not
offline. Before the suite starts, `.github/workflows/checks.yml` fetches its pinned actions, Python,
a SHA-256-verified shellcheck, and playwright 1.64.1, locked by npm integrity hash, with its
Chromium, whose download is not checked against a digest, so an outage at GitHub or in those
downloads can fail the check with no change in this repository. Run the suite before pushing. A
local run lints with whatever shellcheck is on PATH and skips the lint, without failing, when none
is installed; CI installs the pinned version and asserts it before the suite runs, so a local
green predicts CI only when the shell-block gate's pass line names that version. The `overflow`
section serves `site/` on 127.0.0.1 and runs the template's `.baseline/check_overflow.js` on every
generated page that answers 200, failing a page that scrolls sideways at 320, 360, 390 or 1512 px
in either scheme; the check refuses every other origin, so it reaches no network. It needs node
and playwright with its Chromium: set `NODE_PATH` to the `node_modules` folder holding playwright
and `PLAYWRIGHT_BROWSERS_PATH` to the folder holding its Chromium. A local run without them prints
a SKIP, never a failure; CI installs the pinned playwright and sets
`SECURECONFIG_REQUIRE_OVERFLOW=1`, under which a missing node or playwright fails. The suite also
compares local Python with CI's pinned `PYTHON_VERSION`: a mismatch or unavailable comparison
prints an advisory SKIP, never a failure, because `html.parser` behaviour can differ between
releases.
A matching release prints an ok line. Before any other gate, the suite checks that its `python3`,
run as `python3 -I -B`, imports the markdown-it-py version that `tools/requirements-gates.txt`
pins and has the installed version that lock pins for every package in it, markdown-it-py and
mdurl, and a match prints an ok line. A mismatch, a missing or broken package, or an unreadable
or unparsable pin prints one FAIL line naming the interpreter, what it found and the pin, and the
suite stops with status 2 before any other gate runs. A missing or mismatched parser is a host
problem, not a code finding: install `tools/requirements-gates.txt` into a venv and put that
venv's `bin` directory first on PATH.

The weekly lychee workflow sweeps external links and stays advisory, because a third-party site
that is down or refuses automated clients must never block a merge.

## Generated files

`site/llms-full.txt` is generated by `scripts/build-llms-full.sh` from the guide list inside that
script. Never hand-edit it. Adding a guide means updating the build script, `site/llms.txt` and
`README.md`, then rerunning `scripts/build-site.py` (the generated Guides page is built from the
README's guide index); the gate suite fails if any of those is missed.
`.aiqt/gensrc.json` records this relationship.

The site's pages (`site/index.html`, each section's `index.html`, `site/404.html` and the
`site/draft/index.html` review page) are generated by `scripts/build-site.py` from
`site-src/content.json` and `README.md`; never hand-edit them, and rerun the script after changing
either. The files under `site/assets/baseline/` are copied from the shared site template by
`scripts/copy-baseline.py` and pinned in `.baseline/pin.toml`; never edit them.

`.claude/settings.json` is merged by `tools/gen_aiqt_settings.py` from the vendored hooks manifest.
It also carries hooks this repository does not own, so never overwrite it by hand.

## Branch protection

`main` requires a pull request, forbids force-push and deletion, and will not merge unless `gates`
passes. GitHub reports a `gates` job skipped on a draft pull request to branch protection as a
success; what keeps that skip from merging is that a draft cannot be merged and that the
orchestrator's merge gate requires a `gates` job that ran and succeeded on the exact head that
merges (`.github/workflows/checks.yml`). Push a branch and open a pull request; there is no
direct path to `main`.
