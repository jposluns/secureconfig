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
| 1.211 | `container-hardening.md`: verify-probe, remaining image evidence: establish which nc options the amd64 `busybox:1.36` binary contains, read from its built configuration or binary rather than inferred from 1.36.1 Kconfig defaults and from the c1375496 `Dockerfile.builder` that the imported image is only inferred to come from, and what the non-amd64 `busybox:1.36` variants contain for `nc -z -w 3`. (M, M) | `[gap]` |
| 1.264 | `gpu-clouds.md`: remaining account-MFA evidence: establish RunPod factor methods, setup steps and enforcement, Vast.ai team-wide enforcement, Lambda-native factor methods, setup steps and enforcement, whether Lambda or Modal SSO can be made the only sign-in path, Modal SSO availability for a given workspace or plan, and any Modal customer-account second-factor control or Modal-side MFA enforcement; the cited Lambda and Modal SSO pages establish sign-in through the IdP, not MFA enforcement, and the cited Modal MFA requirement covers employees only. (M, M) | `[gap]` |
| 1.266 | `paas.md`: remaining managed-tls/listener-port evidence: establish Fly automatic certificate renewal, its timing and renewal-failure handling, Heroku Cedar's listener address and any Vercel Functions listener address or port, and resolve the ACM Private Spaces wildcard contradiction for the non-Cedar generation (this guide's assessment). Fly's current custom-domain page ties issuance and renewal to domain verification, Heroku's pages document `PORT` binding and Vercel's Functions overview documents request handlers, without closing these gaps; in this guide's assessment, the ACM page's three wildcard statements agree only for Cedar. (M, M) | `[gap]` |
| 1.268 | `paas.md`: remaining https-redirect/verify-redirect evidence: establish Render's redirect status, Railway's HEAD redirect behaviour and POST status, and Heroku's redirect policy, configuration/application responsibility and status; Render's static-site rule 301 and Heroku's ACM challenge-path handling do not close these gaps, and cited header descriptions do not establish sanitization. (M, M) | `[gap]` |
| 1.283 | `agent-builders.md`: debug-remedy, remaining UI and external-RBAC gaps: establish which roles hold `plugin.plugin_preferences` under external or enterprise RBAC and where the console renders a plugin-permission or plugin-preferences editor, including any other rendering location; the pinned fallback lists and role mapping establish owner/admin membership with external RBAC disabled, and CategoryMarketplacePanel wires canInstallPlugin to List.showInstallButton when expanded and neither loading nor showing an installed-ID error, not a preferences editor. (M, M) | `[gap]` |
| 1.290 | `firebase-supabase.md`: local-guards: establish the unrecorded bash and other tool/parser versions for the historical authoring guard and syntax runs; the ShellCheck v0.11.0 release is cited, but does not attest to the historical host binary. (M, M) | `[gap]` |
| 1.291 | `pocketbase.md`: source-limits, remaining adapter and deployment gaps: trace Mongo, Redis, Memory and Pool getDocument/find authorization and establish which adapter a deployment uses; SQL getDocument/find, collection-grant skip, non-skip document-security filtering, disabled-status bypass and the Postgres predicate override are now cited. (M, M) | `[gap]` |
| 1.294 | `authentication.md`: transport-authentication, remaining source gaps: establish the HTML-login boundary for non-HTTP transports, how a GraphQL request is to be authenticated (mechanism, accepted credentials and middleware checks), and authentication boundaries for non-REST inference and management APIs, including whether a given gRPC server verifies call credentials; GraphQL's recommendation that execution begin after authentication middleware confirms the user's identity and gRPC channel, call and composite credentials are now cited, and applying the gRPC credentials to inference and management APIs is this guide's inference. REST-style inference/management controls remain guide requirements based on generic REST guidance. Comprehensive webhook replay rejection, including repeats within the accepted window, remains an application requirement beyond the cited Stripe timestamp tolerance and Standard Webhooks ID/deduplication guidance, and no universal webhook-ID retention period is established (the specification's five-minute ID-storage example is not one). A deployed application's authentication and comprehensive replay rejection remain unestablished deployment behaviour. (M, M) | `[gap]` |
| 1.297 | `elasticsearch.md`: os-gcs-azure, remaining applicability and version gaps: establish deployed GCS/Azure client-side encryption, installed key providers, the MeteredBlobStoreRepository hierarchy and dispatch at 2.10.0/3.0.0, and behaviour in unchecked releases; 2.10.0 is the earliest checked core crypto-settings/wrap release, not a universal deployed minimum. (M, M) | `[gap]` |
| 1.299 | `machine-auth.md`: verify-artifacts, remaining coverage and version gaps: establish detection coverage for this project's key format and behaviour in other releases; Trivy v0.76.0 image secret scanning is now cited, including base-layer skipping and rule/configuration exclusions, so a clean scan does not establish absence of keys. (M, M) | `[gap]` |
| 1.300 | `n8n.md`: environment, remaining gap: establish incoming `envProviderState` production and contents, Python `runner_env_deny` configuration/default and effective module access, complete Code `process.env` isolation, internal-mode runners, other nodes, other launcher versions and deployed configuration; pinned n8n 2.40.6 runner controls and launcher 1.5.1 environment preparation are now cited, without claiming complete host/container isolation. (M, M) | `[gap]` |
| 1.301 | `observability-components.md`: remaining Loki internal-path evidence: GetInstancePort precedence, DNS/ring watcher internals, dskit ring reads, complete service start-up wiring, KV writes, ring.DoUntilQuorum, Kafka/partition-ingester paths, querier/distributor request callers, ingester/frontend client pool internals, processor manager and remaining RPC hops; effective addresses, successful internal/compactor calls, live reachability and eventual deletion remain unverified. Deletion mode admission and worker-service address wiring are now cited. (M, M) | `[gap]` |
| 1.302 | `ollama.md`: profiling, remaining dependency and deployment gap: establish whether any module dependency imports `net/http/pprof` and whether the served mux would expose its handlers; this guide's assessment from a search of non-test first-party v0.34.2 Go source is that first-party code registers no pprof handler. Shipped-binary pprof availability remains unestablished and requires observation. (M, M) | `[gap]` |
| 1.303 | `python.md`: client-ca, remaining deployment gap: establish the OpenSSL release linked by a given CPython build, platform-specific default stores (including Windows or macOS builds), and whether its deployed SSL configuration takes the default-path call and loads the intended CAs; CPython path and environment-variable reporting, its call into OpenSSL, and the openssl-4.0.3 overrides with their set-user-ID/set-group-ID exclusion are now cited. (M, M) | `[gap]` |
| 1.304 | `self-hosted-idp.md`: authentik-admin-boundary and authentik-admin-proxy, remaining gaps: establish the effective API mount prefix, session authentication and endpoint-specific authentication/RBAC wiring, HTTPS serving and deployed listener topology, and a complete admin-path restriction list including websocket authorization; reconcile the metrics text saying invocation was not traced with `WebServer.Start` calling `runMetricsServer`, tracing listener identity and deployed startup; pinned configuration, Go startup/proxy, interface views, API registration, token authentication and RBAC implementations are now cited. (M, M) | `[gap]` |
| 1.306 | `self-signed.md`: debian-trust and rhel-trust, remaining release gaps: source the trust-store commands for Debian/Ubuntu releases beyond trixie/bookworm and noble/jammy, RHEL releases beyond 9 (including 8 and 10), released Fedora and CentOS Stream releases beyond 8/10; the cited Fedora rawhide development branch is not a released Fedora and CentOS Stream is not RHEL, so uncovered releases remain this guide's assessment. (M, M) | `[gap]` |
| 1.307 | `identity-providers.md`: provider-authenticators, remaining gap: cite compatibility beyond the documented Entra OATH TOTP, Okta Google Authenticator (once added by an admin), Okta Custom TOTP (if enabled for the org) and Google Account use of Google's own Authenticator app, including other providers and arbitrary apps; the Entra page does not specify software-app algorithms or periods, and the Google page does not specify algorithms or periods; Custom TOTP's standard-token and single-enrolment limits apply to that feature, and its page requires matching HMAC and shared-secret encoding settings but only lists a configurable time step; uncovered compatibility remains this guide's assessment. (M, M) | `[gap]` |
| 1.308 | `n8n.md`: verify-api, remaining source gap: establish GET /api/v1/workflows route security and list-success implementation/status; the pinned registry, express-openapi-validator 5.5.3 and n8n error path now support this guide's conditional 401 assessment for a selected security failure without a status, including a pre-handler scheme check. The spec's declared schemes were not fetched; controller-owned routes can respond before validator security, and the cited `workflows.handler.ts` only returns a workflow version. Retain rejection (for example 401) and 200 workflow JSON as unobserved expectations, with proxy status changes possible. (M, M) | `[gap]` |
| 1.310 | `oidc-integration.md`: github-org-mfa, remaining gap: establish whether the organization-membership API still reports a non-compliant member without 2FA as a member and whether that account fails the application membership check before treating membership as proof of MFA; both cited organization and GitHub Enterprise Server policies say members without 2FA retain membership; neither those policies nor this guide establish the membership API response or application-check result for such a member. (M, M) | `[gap]` |
| 1.311 | `ai-infra-services.md`: onyx-auth-type, remaining runtime and documentation gaps: establish the September 2026 record that removal was planned for v4.5 and any documentation-side removal record; the cited call sites do not establish runtime authentication selection at v4.5.0 and v4.9.2; those tags retain the cited legacy startup calls, and their tag names are not commit pins. (M, M) | `[gap]` |
| 1.312 | `vector-databases.md`: remaining hosted-console evidence gaps: establish any Pinecone console MFA control and Pinecone MFA enforcement, deployed identity-provider MFA enforcement for Pinecone, Qdrant Cloud, Weaviate Cloud and Zilliz Cloud SSO, any Qdrant Cloud console MFA control, and how Zilliz Cloud organization-level MFA enforcement applies to SSO users and to Google- or GitHub-linked accounts, which the Zilliz MFA page does not say; the cited documentation does not establish these. The cited Qdrant Cloud, Weaviate Cloud and Zilliz Cloud documentation, including the published pages, does not establish live-console behaviour; publication/release timing and Weaviate MFA enforcement UI details remain unverified. Retain the advice to require an MFA-enforcing identity provider wherever SSO is used and confirm enforcement. (M, M) | `[gap]` |
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
