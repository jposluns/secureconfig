# TODO

Forward-looking backlog for secureconfig. Closed items move to `DONE.md`; nothing is deleted.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

## How items are numbered

Every open item is one index row in the band below that fits it. **Ids are permanent and never
reused**, including when an item is dropped, superseded, or its work reverted, and they are
decoupled from the band so an item can move band without changing identity.

Series: **1.x** an existing guide, whether the row is an error or a deepening, **2.x** missing
content, **3.x** tooling and process, **4.x** the site and adopter-facing surfaces. A row moves
band without changing its id, which is the point of decoupling the two.

Each row carries `(severity, effort)`. Severity is what a reader loses: **H** a wrong or missing
control on something commonly exposed, **M** a real gap with a workaround, **L** cosmetic or
internal. Effort is **XS** minutes, **S** under an hour, **M** a session, **L** several sessions,
**XL** a project.

Next ids: **1.318**, **2.48**, **3.44**, **4.12**.

Retired without ever naming an item, and never to be issued: **2.21** to **2.23** and **4.3** to **4.4**, assigned in error on 2026-09-13 when the band number was used in place of the series.

## Queueing

**AIQT: fix issues first.** Band 1 is worked to empty before anything else is picked, whatever
the severity of what is waiting in the other bands. After band 1 is clear, band 4 follows, then
take the highest severity across bands 2 and 3 together rather than finishing a band (see "Queue
order" in `DECISIONS.md`). Band 5 comes last, only when bands 1 to 4 are clear (see "Band 5
position in the queue" in `DECISIONS.md`).

Maintainer direction supersedes the order at any time. Items blocked on another project are not
picked, they are waited on.

## Priority 1: Errors

A guide that asserts something false, or a Verify step that cannot discriminate. These are worked
first and to empty, because a reader acting on a wrong guide is worse off than a reader with no
guide. Found by the 2026-09-13 coverage audit; `[N families]` means raised independently by that
many.

| ID | Item | Tags |
| --- | --- | --- |

## Priority 2: Deepen existing guides

A real surface the guide never covers. Correct as far as it goes, and not far enough.

| ID | Item | Tags |
| --- | --- | --- |
| 1.211 | `container-hardening.md`: verify-probe: establish what the deployed `busybox:1.36` image actually contains for `nc -z -w 3`; the pinned BusyBox source alone does not map the image. (M, M) | `[gap]` |
| 1.264 | `gpu-clouds.md`: remaining account-MFA evidence: establish RunPod factor methods, setup steps and enforcement, Vast.ai team-wide enforcement, Lambda factor methods, setup steps and enforcement, and Modal SSO availability and customer-account second-factor controls or MFA enforcement through workspace SSO; the cited Modal MFA requirement covers employees only. (M, M) | `[gap]` |
| 1.266 | `paas.md`: remaining managed-tls/listener-port evidence: establish Fly automatic certificate renewal, Heroku Cedar listener address, Vercel Functions listener/port contract, and resolve the ACM Private Spaces wildcard contradiction. (M, M) | `[gap]` |
| 1.268 | `paas.md`: remaining https-redirect/verify-redirect evidence: establish Render's redirect status, Railway's HEAD redirect behaviour and POST status, and Heroku's redirect policy, configuration/application responsibility and status; Render's static-site rule 301 and Heroku's ACM challenge-path handling do not close these gaps, and cited header descriptions do not establish sanitization. (M, M) | `[gap]` |
| 1.273 | `nodejs.md`: bind, remaining source gaps: establish Heroku Cedar's listener address. (M, M) | `[gap]` |
| 1.276 | `python.md`: bind, remaining source gaps: establish Heroku Cedar's listener address. (M, M) | `[gap]` |
| 1.283 | `agent-builders.md`: debug-remedy, remaining UI gap: establish which roles hold the `plugin.plugin_preferences` workspace permission key and where the console renders the plugin-permission or plugin-preferences control; the cited pinned files show the key list and client-side UI flags, including the legacy debug-permission path; the cited pinned files do not show which roles hold the key or where the control is rendered. (M, M) | `[gap]` |
| 1.290 | `firebase-supabase.md`: local-guards: establish the unrecorded bash and other tool/parser versions for the historical authoring guard and syntax runs; the ShellCheck v0.11.0 release is cited, but does not attest to the historical host binary. (M, M) | `[gap]` |
| 1.291 | `pocketbase.md`: source-limits, remaining adapter gap: trace what the utopia-php/database adapter's getDocument and find do with the shared authorization instance, including any document-permission filtering (with or without a collection grant, and the non-skip find branch when documentSecurity is enabled), and what disabled authorization status bypasses there; permission-role extraction/matching, getDocument collection/document read checks, find collection checks/adapter dispatch and Authorization status/skip are now cited. (M, M) | `[gap]` |
| 1.294 | `authentication.md`: transport-authentication, remaining source gaps: establish the HTML-login boundary for non-HTTP transports, general GraphQL authentication beyond introspection advice, and authentication boundaries for non-REST inference and management APIs; REST-style inference/management controls remain guide requirements based on generic REST guidance, and comprehensive webhook replay rejection, including repeats within the accepted window, remains an application requirement beyond the cited Standard Webhooks ID/deduplication guidance, not established deployment behaviour. (M, M) | `[gap]` |
| 1.297 | `elasticsearch.md`: os-gcs-azure: establish deployed GCS/Azure client-side encryption applicability and minimum versions beyond the cited OpenSearch plugin tree. (M, M) | `[gap]` |
| 1.298 | `machine-auth.md`: key-hash: cite an API-key hash implementation covering algorithm, encoding, comparison and key-generation entropy. (M, M) | `[gap]` |
| 1.299 | `machine-auth.md`: verify-artifacts: source an image-layer scan for contents that `docker history` does not show. (M, M) | `[gap]` |
| 1.300 | `n8n.md`: environment: source or narrow complete host/container environment isolation; the cited `$env` proxy guard does not establish isolation of every node or Code `process.env`. (M, M) | `[gap]` |
| 1.301 | `observability-components.md`: Loki deletion policy and internal paths: trace the exact mode-to-allow mapping for create/list/cancel handlers and the remaining worker-service address wiring. (M, M) | `[gap]` |
| 1.302 | `ollama.md`: profiling: complete the shipped pprof-handler registration source audit beyond the reviewed first-party router and import paths. (M, M) | `[gap]` |
| 1.303 | `python.md`: client-ca: establish whether CPython SSL configuration uses the OpenSSL `SSL_CERT_FILE` override beyond the cited files. (M, M) | `[gap]` |
| 1.304 | `self-hosted-idp.md`: authentik-admin-boundary and authentik-admin-proxy: source the administration listener/permission boundary and complete admin-path restriction scope. (M, M) | `[gap]` |
| 1.306 | `self-signed.md`: debian-trust and rhel-trust: source the Debian/Ubuntu and RHEL/Fedora trust-store commands for the stated releases beyond the cited Debian trixie, Ubuntu noble and RHEL 9 scope. (M, M) | `[gap]` |
| 1.307 | `identity-providers.md`: provider-authenticators: cite per-provider TOTP compatibility beyond the cited Google prompt and RFC 6238 material. (M, M) | `[gap]` |
| 1.308 | `n8n.md`: verify-api: source or narrow the public-API 401/200 status guarantees beyond the cited auth registry, retaining the responses as expectations without a live run. (M, M) | `[gap]` |
| 1.309 | `n8n.md`: code-execution: establish the from-2.0 Execute Command default boundary beyond the pinned 1.x/2.0.0 snapshots and unversioned changes page. (M, M) | `[gap]` |
| 1.310 | `oidc-integration.md`: github-org-mfa, remaining gap: establish whether the organization-membership API still reports a non-compliant member without 2FA as a member and whether that account fails the application membership check before treating membership as proof of MFA; both cited organization and GitHub Enterprise Server policies say members without 2FA retain membership; neither those policies nor this guide establish the membership API response or application-check result for such a member. (M, M) | `[gap]` |
| 1.311 | `ai-infra-services.md`: onyx-auth-type: establish the stated v4.5 removal boundary beyond the pinned v4.3.13 and v4.4.0 snapshots and tag-name identity. (M, M) | `[gap]` |
| 1.312 | `vector-databases.md`: source or narrow the hosted-console MFA arrangements for Pinecone, Qdrant Cloud, Weaviate Cloud and Zilliz that the cited pages do not establish. (M, M) | `[gap]` |
| 2.28 | `gitops-controllers.md`: Complete the remaining source audit of image tag-to-build mapping (Redis, Dex), the application-controller bind address, repo-server service method authorization, Dex API method authorization, whether Redis overwrites its password in argv, and RBAC server-side wiring. (M, M) | `[gap]` |
| 2.29 | `self-hosted-ci-runners.md`: offline inspection outcomes are recorded in the guide. Remaining: verify and cite a pinned vendor source for the `[runners.docker]` `pid_mode` TOML key, corroborated only in rolling GitLab Runner source. (M, M) | `[gap]` |
| 1.117 | `search-engines.md` Verify (#285): the reviewed tools/scan_credential.sh searches client output and local refs/HEAD/reflog commit trees, with tools/test_scan_credential.py retaining dummy positive/negative controls and documented limits. Still open: run a real client pipeline in a disposable copy with a known dummy admin, master or bootstrap key, require detection, then remove it and rebuild cleanly and require scoped absence; retain a separate old-commit positive control and record the stated coverage limits. No real application build was available for the hand-built fixtures. (M, M) | `[gap]` |

## Priority 3: Add missing content

Gaps from the same audit, one row per missing guide. A gap raised by more than one family is
marked, and those are the ones worth taking first.

| ID | Item | Tags |
| --- | --- | --- |
| 3.40 | F-LYCHEE-2026-09-28 remainder after #448: the six bare body citations in `agent-builders.md` (two), `jupyter.md`, `mlflow.md`, `sqlite-http-frontends.md` and `workflow-orchestrators.md` were written as autolinks (#447), and seven later bare `__main__.py` and `__init__.py` citations in `agent-builders.md` and `free-certificates.md` were written as autolinks (#620). Remaining: confirm with lychee `--dump` that no cited URL is extracted in truncated form, and confirm the first live weekly sweep after these changes (scheduled 2026-10-19). (S, S) | `[gap]` |

## Priority 4: Tooling and process

| ID | Item | Tags |
| --- | --- | --- |
| 3.43 | `tools/check_bare_urls.py`: follow up three fail-closed extra findings from #623 QA that CONTRIBUTING does not yet disclose: an angle-bracket destination written with escaped or entity underscores reports a finding because the angle form is compared without unescaping; URL characters directly after an inline link or image, as in `[t](https://example.com/__x)x`, are read as part of a bare URL and report a finding; and a character reference for `)` in a destination, such as `&#41;`, reports a finding. Fix each in code with a regression fixture, or disclose it in CONTRIBUTING with a fixture pinning its outcome. (M, S) | `[gap]` |

## Decisions

Maintainer rulings moved to `DECISIONS.md` on 2026-09-13, in preparation for the OPF operational-files migration (row 3.8). A row may cite a decision there; this file no longer carries them.

## Priority 5: Site and adopters

| ID | Item | Tags |
| --- | --- | --- |

## Blocked upstream

| ID | Item | Waiting on |
| --- | --- | --- |
| 3.6 | Activate the AIQT hooks: `.claude/settings.json` is classifier-gated and `tools/gen_aiqt_settings.py` merges rather than overwrites (L, S) | the guardrails versioning work |
| 3.7 | Re-pin `.aiqt/` to a tag: currently pinned to a `main` commit because the only tag predates the commits this repository depends on (L, XS) | guardrails publishing a tag |
| 3.8 | Adopt the DevProcess / OPF operational-files standard. Deferred by the maintainer on 2026-09-12; `TODO.md` stays at the repository root and the adoption script will ingest it. See the note below (L, M) | the OPF tooling release |

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
