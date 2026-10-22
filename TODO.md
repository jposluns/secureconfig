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

Next ids: **1.321**, **2.48**, **3.44**, **4.12**.

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
| 1.291 | `pocketbase.md`: source-limits, remaining adapter and deployment gaps: trace Mongo, Redis, Memory and Pool getDocument/find authorization and establish which adapter a deployment uses; SQL getDocument/find, collection-grant skip, non-skip document-security filtering, disabled-status bypass and the Postgres predicate override are now cited. (M, M) | `[gap]` |
| 1.294 | `authentication.md`: transport-authentication, remaining source gaps: establish the HTML-login boundary for non-HTTP transports (RFC 6455's handshake-authentication and `Origin` sections, OWASP's WebSocket cookie and `Origin` lines and WHATWG's EventSource `withCredentials` credentials mode are now cited for the WebSocket and SSE parts; the general rule remains this guide's requirement), how a GraphQL request is to be authenticated (accepted credentials and middleware checks, and the mechanism for GraphQL not served over HTTP; graphql.org's placement of GraphQL after all authentication middleware now cites the mechanism over HTTP, the GraphQL over HTTP working draft puts authentication security out of scope, and Apollo Server and Hasura are cited only as vendor examples), and authentication boundaries for non-REST inference and management APIs, including whether a given gRPC server verifies call credentials (grpc-go's authentication example and go-grpc-middleware v2.3.3 now cite server-installed verification in grpc-go terms, and pinned source readings of vLLM v0.30.0, Triton, Text Embeddings Inference and argocd-server are cited as per-server data points; other servers, the general boundary and deployed behaviour remain open); GraphQL's recommendation that execution begin after authentication middleware confirms the user's identity and gRPC channel, call and composite credentials are now cited, and applying the gRPC credentials to inference and management APIs is this guide's inference. REST-style inference/management controls remain guide requirements based on generic REST guidance. Comprehensive webhook replay rejection, including repeats within the accepted window, remains an application requirement beyond the cited Stripe timestamp tolerance and Standard Webhooks ID/deduplication guidance, and no universal webhook-ID retention period is established (the specification's five-minute ID-storage example is not one). A deployed application's authentication and comprehensive replay rejection remain unestablished deployment behaviour. (M, M) | `[gap]` |
| 1.297 | `elasticsearch.md`: os-gcs-azure, remaining applicability and version gaps: establish deployed GCS/Azure client-side encryption, installed key providers, behaviour before 2.10.0 and after 3.9.0, the `BlobStoreProvider` wrap at 3.4.0 to 3.7.0 and 3.9.0, whether the GCS/Azure `getNativeStore()` path added at 3.7.0 bypasses the wrap, the index-level `CryptoMetadata` that `BlobStoreRepository` passes to `writeBlobWithMetadata` from 3.5.0 (whether it applies to GCS/Azure (including at 3.8.0, where the `BlobStoreProvider`, `EncryptedBlobContainer` and `AzureBlobContainer` lines are cited only for the repository-level path and the value is not traced through them), how it interacts with repository `crypto_settings` and the `EncryptedBlobStore` wrap, and its effective behaviour), and `CryptoSettings.validate()` requirements at the checked tags other than 2.10.0, 3.0.0 and 3.8.0, where it is not established; the five repository and wrap classes are now read at all 31 release tags from 2.10.0 to 3.9.0, with `BlobStoreRepository.blobStore()` wrapping directly through 3.3.2 and delegating to `BlobStoreProvider` from 3.4.0 and `BlobStoreRepository` passing an index-level `CryptoMetadata` resolved from index settings to `writeBlobWithMetadata` from 3.5.0 (cited at 3.5.0 and 3.9.0 as a source reading without an OpenSearch run), and that checked range is not a universal deployed minimum. (M, M) | `[gap]` |
| 1.299 | `machine-auth.md`: verify-artifacts, remaining gaps: an observed Trivy v0.76.0 and Gitleaks v8.19.0 run on this guide's API key formats, including the `gitleaks detect` commands the guide gives from source reading; Gitleaks' detect-step behaviour (its keyword, entropy and stopword steps were emulated without its detection code); detection coverage of other key formats a project issues; and detection behaviour in other releases. Trivy v0.76.0 image secret scanning is cited, including base-layer skipping and rule/configuration exclusions, and default-rule coverage of the guide's three API key formats is recorded as a Python `re` computation, not a scanner run, for Trivy at 531360e5 (no built-in rule matched) and Gitleaks v8.19.0 (only `generic-api-key`, after a keyword assignment), so a clean scan does not establish absence of keys. (M, M) | `[gap]` |
| 1.300 | `n8n.md`: environment, remaining gap: establish incoming `envProviderState` production and contents, Python effective module access, complete Code `process.env` isolation, internal-mode runners, other nodes, other launcher versions and deployed configuration; pinned n8n 2.40.6 runner controls, including the Python `runner_env_deny` setting and its default, and launcher 1.5.1 environment preparation are now cited, without claiming complete host/container isolation. (M, M) | `[gap]` |
| 1.301 | `observability-components.md`: remaining Loki internal-path evidence: complete per-module start-up behaviour, Kafka consumer, Kafka-only and partition-ingester paths, and every other RPC hop; effective addresses, successful internal/compactor calls, live reachability, the internal server's effective gRPC listener, what the ingester querier and ingesters return for the inverted ingester interval that the querier sends for a negative store lookback other than `-1` when now minus it is after the selection end, including the results of the ingesters' index lookup at its start and their chunk iterators' behaviour for it, whether an ingester wrapper set in code (`Ingester.Wrapper`, no YAML key) passes `Query` and `QuerySample` to the ingester and what it returns, and eventual deletion remain unverified. Deletion mode admission, worker-service address wiring, GetInstancePort precedence, ring reads and lifecycler KV writes, `ring.DoUntilQuorum`, DNS/ring watchers, the processor manager, client pools, push and querier callers, the distributor Kafka write path, internal-server registration, the querier's ingester call with that inverted interval for selections that pass request validation and reach interval construction, the ingester querier's gRPC call with it, and, without a configured wrapper, the ingester's skipped store query and in-memory chunk selection for it are now cited. (M, M) | `[gap]` |
| 1.302 | `ollama.md`: profiling, remaining build-variant and deployment gap: establish whether v0.34.2 builds for GOOS/GOARCH, cgo and tag-set combinations other than the runs listed below (including other GOOS/GOARCH pairs, cgo-on builds for windows arm64 and freebsd, openbsd, netbsd and solaris amd64, and the `updater_live` and `release,library` tag sets on other platforms or with cgo on) or with other tag sets (including `appengine`, `os400`, tag combinations and dependency modules' own tags) import `net/http/pprof` or `runtime/pprof`, and whether the served mux would expose pprof handlers in such builds; the default-tag `go list` graphs for linux, darwin and windows amd64 and linux and darwin arm64, cgo on and off, and for windows arm64 and freebsd, openbsd, netbsd and solaris amd64, cgo off, list neither, as do cgo-off graphs with `-tags updater_live` (windows amd64, darwin arm64) and `-tags release,library` (linux amd64), and the tree's other custom tags gate only test files. Shipped-binary pprof availability remains unestablished and requires observation. (M, M) | `[gap]` |
| 1.303 | `python.md`: client-ca, remaining deployment gap: establish the OpenSSL release linked by a given CPython build, platform-specific default stores (including Windows or macOS builds), and whether its deployed SSL configuration takes the default-path call and loads the intended CAs; CPython path and environment-variable reporting, its call into OpenSSL, and the openssl-4.0.3 overrides with their set-user-ID/set-group-ID exclusion are now cited. (M, M) | `[gap]` |
| 1.306 | `self-signed.md`: debian-trust and rhel-trust, remaining release gaps: source the trust-store commands for Debian/Ubuntu releases beyond trixie/bookworm/bullseye and resolute/noble/jammy/focal (including Debian forky, whose requested manpage URL redirected to the `testing` path, so no forky-specific page was obtained), RHEL releases beyond 8 and 9 (including 10, whose page at the cited RHEL 8 and 9 path shape returned 404), Fedora releases beyond 41/42/43/44 and whether the cited Fedora 45 branch is a released Fedora, and CentOS Stream releases beyond 8/9/10; the cited Fedora rawhide development branch is not a released Fedora and CentOS Stream is not RHEL, so uncovered releases remain this guide's assessment. (M, M) | `[gap]` |
| 1.310 | `oidc-integration.md`: github-org-mfa and github-org-mfa-api, remaining gap: observe the organization-membership API responses for a member without 2FA, and establish whether a given application's membership check fails for that account, before treating membership as proof of MFA. The pinned REST API description's list-members `2fa_disabled` filter, membership-check 204 response and `GET /user/memberships/orgs/<org>` entry (the authenticated user's membership if active or pending, 404 if unaffiliated, 403 for a blocked GitHub App, no 2FA condition stated) are now cited as an API description, not observed behaviour. (M, M) | `[gap]` |
| 1.311 | `ai-infra-services.md`: onyx-auth-type, remaining runtime and documentation gaps: establish the September 2026 record that removal was planned for v4.5 and any documentation-side removal record; the cited call sites do not establish runtime authentication selection at v4.5.0 and v4.9.2; those tags retain the cited legacy startup calls. (M, M) | `[gap]` |
| 1.312 | `vector-databases.md`: remaining hosted-console evidence gaps: establish any Pinecone console MFA control and Pinecone MFA enforcement, deployed identity-provider MFA enforcement for Pinecone, Qdrant Cloud, Weaviate Cloud and Zilliz Cloud SSO, and any Qdrant Cloud console MFA control. Also establish how Zilliz Cloud organization-level MFA enforcement applies to SSO users and to Google- or GitHub-linked accounts, which the Zilliz MFA page does not say. The cited documentation does not establish any of these. The cited Qdrant Cloud, Weaviate Cloud and Zilliz Cloud documentation, including the published pages, does not establish live-console behaviour; publication/release timing and Weaviate MFA enforcement UI details remain unverified. Retain the advice to require an MFA-enforcing identity provider wherever SSO is used and confirm enforcement. (M, M) | `[gap]` |
| 1.320 | `secrets.md`: scanners, remaining run and source gaps: observe `gitleaks git .` and `gitleaks dir .` at v8.19.0 and at 8.19.1 or later, read the other v8.19.0 `cmd/` files for any `source` flag registration, and read `detect`'s own source before v8.19.0, including releases before v8.18.0; `git`/`dir` positional-path handling at every tag from v8.19.1 to v8.30.1 and the v8.18.4 README's `detect`, `--no-git` and `--source` are now cited by source reading without a run. (M, S) | `[gap]` |
| 2.28 | `gitops-controllers.md`: remaining image provenance, Redis environment and RBAC coverage gaps: establish which build recipe produced `public.ecr.aws/docker/library/redis:8.2.3-alpine` (the pinned trees name none, and the earlier docker-library-redis bcbc6921 reading was not rechecked here), whether the published `ghcr.io/dexidp/dex:v2.45.1` image came from Dex v2.45.1's release workflow, whether Redis 8.2.3's title overwrite also clears the `REDIS_PASSWORD` environment copy, per-handler RBAC coverage in `argocd-server`, and whether grpc-go passes the registered service implementation as the value the `go-grpc-middleware/v2` auth interceptors check for `AuthFuncOverride`. The application-controller bind address, repo-server and Dex API method authorization, Redis's argument overwrite, the server's RBAC wiring and the `go-grpc-middleware/v2` v2.3.3 auth interceptors' `AuthFuncOverride` handling are now cited from the pinned sources. (M, M) | `[gap]` |
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
