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

Next ids: **1.314**, **2.48**, **3.44**, **4.12**.

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
| 1.264 | `gpu-clouds.md`: remaining Vast auth implementation: trace the delegated portal-aio configurator and runtime consumers of OPEN_BUTTON_TOKEN, WEB_PASSWORD, ENABLE_AUTH, AUTH_EXCLUDE and PORTAL_CONFIG, including precedence and route enforcement; account-security sources for RunPod, Vast.ai, Lambda and Modal remain uncited. (M, M) | `[gap]` |
| 1.266 | `paas.md`: remaining managed-tls/listener-port evidence: establish Fly automatic certificate renewal, Railway TLS termination component and listener address/injected-port contract, Heroku Cedar listener address, Vercel Functions listener/port contract, and resolve the ACM Private Spaces wildcard contradiction. (M, M) | `[gap]` |
| 1.268 | `paas.md`: remaining https-redirect/verify-redirect evidence: establish Render's redirect status, Railway's HEAD redirect behaviour and POST status, and Heroku's redirect policy, configuration/application responsibility and status; cited header descriptions do not establish sanitization. (M, M) | `[gap]` |
| 1.269 | `paas.md`: verify-app-auth and verify-secrets: source or label the exact bypass and auth procedures and the bundle scan procedure, and their limits. (M, M) | `[gap]` |
| 1.273 | `nodejs.md`: bind, remaining source gaps: establish Railway's listener address, injected port and TLS termination location, and Heroku Cedar's listener address. (M, M) | `[gap]` |
| 1.276 | `python.md`: bind, remaining source gaps: establish Railway's listener address, injected port and TLS termination location, and Heroku Cedar's listener address. (M, M) | `[gap]` |
| 1.281 | `java.md`: mfa: cite provider/fronting enforcement for the stated MFA setup. (M, M) | `[gap]` |
| 1.282 | `java.md`: client-validation: cite the trust-all API and its scope. (M, M) | `[gap]` |
| 1.283 | `agent-builders.md`: debug-remedy: establish whether the debug_permission change is available in the console UI; API remedy is already cited and UI availability is unestablished. (M, M) | `[gap]` |
| 1.285 | `gitops-controllers.md`: verify-flux: cite curl `--data-binary` behaviour; the six historical GitOps facts remain delegated to row 2.28. (M, M) | `[gap]` |
| 1.286 | `lighttpd.md`: pin lighttpd TLS/key introduction versions for the 1.4.56 protocol defaults and 1.4.53 separate-key syntax, and pin the redirect default transition at 1.4.75. (M, M) | `[gap]` |
| 1.287 | `self-signed.md`: key-permissions: cite filesystem command and mode behaviour for the private-key instructions. (M, M) | `[gap]` |
| 1.288 | `self-signed.md`: verification-bypasses: cite Node.js bypass settings and their scope. (M, M) | `[gap]` |
| 1.289 | `identity-providers.md`: maintain the Supabase `aal2` authorization-policy claim mapping to the source already cited in the guide. (M, S) | `[gap]` |
| 1.290 | `firebase-supabase.md`: local-guards: source the ShellCheck 0.11.0 and other shell/tool versions for the recorded authoring guard run. (M, M) | `[gap]` |
| 1.291 | `pocketbase.md`: source-limits: trace the PocketBase CLI wrapper and Appwrite document read authorization and privileged/API-key requester classification; establish the `--dev` default. (M, M) | `[gap]` |
| 1.292 | `authentication.md`: cloudflare-access: source or narrow the claim that Cloudflare Access can front any application unchanged, including the One-time PIN and SSO options still not established by the cited pages. (M, M) | `[gap]` |
| 1.293 | `authentication.md`: fail2ban: source or narrow the coverage and setup of login panels beyond the cited sshd jail and failure filter. (M, M) | `[gap]` |
| 1.294 | `authentication.md`: transport-authentication: source or narrow the HTML-login boundary for non-HTTP transports, GraphQL/inference/management APIs and webhook replay rejection. (M, M) | `[gap]` |
| 1.295 | `authentication.md`: verify-secret-scan: source or narrow staged, all-ref and merge-commit coverage beyond the cited Gitleaks and `git log -p` material. (M, M) | `[gap]` |
| 1.296 | `docker.md`: secrets: source runtime secret-delivery methods and `.env` exclusion from Git beyond the cited Docker build/history behaviour. (M, M) | `[gap]` |
| 1.297 | `elasticsearch.md`: os-gcs-azure: establish deployed GCS/Azure client-side encryption applicability and minimum versions beyond the cited OpenSearch plugin tree. (M, M) | `[gap]` |
| 1.298 | `machine-auth.md`: key-hash: cite an API-key hash implementation covering algorithm, encoding, comparison and key-generation entropy. (M, M) | `[gap]` |
| 1.299 | `machine-auth.md`: verify-artifacts: source an image-layer scan for contents that `docker history` does not show. (M, M) | `[gap]` |
| 1.300 | `n8n.md`: environment: source or narrow complete host/container environment isolation; the cited `$env` proxy guard does not establish isolation of every node or Code `process.env`. (M, M) | `[gap]` |
| 1.301 | `observability-components.md`: Loki deletion policy and internal paths: trace the exact mode-to-allow mapping for create/list/cancel handlers and the remaining worker-service address wiring. (M, M) | `[gap]` |
| 1.302 | `ollama.md`: profiling: complete the shipped pprof-handler registration source audit beyond the reviewed first-party router and import paths. (M, M) | `[gap]` |
| 1.303 | `python.md`: client-ca: establish whether CPython SSL configuration uses the OpenSSL `SSL_CERT_FILE` override beyond the cited files. (M, M) | `[gap]` |
| 1.304 | `self-hosted-idp.md`: authentik-admin-boundary and authentik-admin-proxy: source the administration listener/permission boundary and complete admin-path restriction scope. (M, M) | `[gap]` |
| 1.305 | `self-hosted-idp.md`: docker-socket-scope: cite Docker daemon privilege and rootless user-scoped blast radius for the socket-access claim. (M, M) | `[gap]` |
| 1.306 | `self-signed.md`: debian-trust and rhel-trust: source the Debian/Ubuntu and RHEL/Fedora trust-store commands for the stated releases beyond the cited Debian trixie, Ubuntu noble and RHEL 9 scope. (M, M) | `[gap]` |
| 1.307 | `identity-providers.md`: provider-authenticators: cite per-provider TOTP compatibility beyond the cited Google prompt and RFC 6238 material. (M, M) | `[gap]` |
| 1.308 | `n8n.md`: verify-api: source or narrow the public-API 401/200 status guarantees beyond the cited auth registry, retaining the responses as expectations without a live run. (M, M) | `[gap]` |
| 1.309 | `n8n.md`: code-execution: establish the from-2.0 Execute Command default boundary beyond the pinned 1.x/2.0.0 snapshots and unversioned changes page. (M, M) | `[gap]` |
| 1.310 | `oidc-integration.md`: github-org-mfa: establish whether a member without 2FA fails the application membership check before treating GitHub organization membership as proof of MFA. (M, M) | `[gap]` |
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
