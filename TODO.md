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

Next ids: **1.313**, **2.48**, **3.41**, **4.12**.

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
| 1.199 | `realtime-webhooks.md`: proxy-limits: pin vendor sources for the proxy capability summaries beyond the cited Caddy timeouts, nginx, Traefik and HAProxy. (M, M) | `[gap]` |
| 1.200 | `apache.md`: mfa: cite Cloudflare Access application and policy controls for the suggested fronting option. (M, M) | `[gap]` |
| 1.201 | `lighttpd.md`: mfa: cite Authelia supported-proxy list and Cloudflare Access for the stated exclusion and MFA fronting option. (M, M) | `[gap]` |
| 1.202 | `lighttpd.md`: verify-config and verify-host: cite lighttpd command/service-manager behaviour and Apache SNI selection for the comparison. (M, M) | `[gap]` |
| 1.203 | `headers.md`: placement: cite proxy header directives and generic static-host `_headers` handling for the stated controls. (M, M) | `[gap]` |
| 1.204 | `headers.md`: all-responses: cite in `headers.md` Sources the nginx `add_header` inheritance source pinned in `nginx.md` for this response-header claim. (M, M) | `[gap]` |
| 1.205 | `docker.md`: auth and verify-auth: pin the authentication-provider and proxy sources for MFA rejection and the 401/403 discriminator. (M, M) | `[gap]` |
| 1.207 | `docker.md`: persistence: cite Docker firewall/INPUT-path behaviour and the startup-unit mechanism behind persistence advice. (M, M) | `[gap]` |
| 1.208 | `docker.md`: alternate-entry: cite cloudflared, tailnet and self-signed TLS alternatives for the stated entry paths. (M, M) | `[gap]` |
| 1.209 | `docker.md`: upstream and verify-redirect: cite cloud security-group/network-ACL and proxy redirect behaviour; keep database TLS/authentication source work delegated to the linked guides. (M, M) | `[gap]` |
| 1.210 | `container-hardening.md`: docker-socket: cite the Docker privilege model for socket root equivalence. (M, M) | `[gap]` |
| 1.211 | `container-hardening.md`: verify-probe: establish what the deployed `busybox:1.36` image actually contains for `nc -z -w 3`; the pinned BusyBox source alone does not map the image. (M, M) | `[gap]` |
| 1.212 | `container-hardening.md`: Compose exec and process diagnostics: cite Docker Compose and process-tool behaviour used by the checks. (M, M) | `[gap]` |
| 1.213 | `host.md`: include-order: pin OpenSSH Include/drop-in, Ubuntu 20.04 and cloud-init history relevant to SSH config ordering. (M, M) | `[gap]` |
| 1.214 | `host.md`: brokered-ssh: cite SSM, IAP, Bastion and tailnet broker behaviour for the stated alternatives. (M, M) | `[gap]` |
| 1.215 | `host.md`: docker-bypass: cite Docker/UFW interaction and its firewall-bypass qualification. (M, M) | `[gap]` |
| 1.216 | `host.md`: updates: cite unattended-upgrades and dnf-automatic package/service behaviour. (M, M) | `[gap]` |
| 1.217 | `host.md`: verify-listeners: cite `ss`, `nc`, SSH and BusyBox behaviour for the inventory and reachability tests. (M, M) | `[gap]` |
| 1.218 | `cloud-firewalls.md`: ssm, iap and bastion: cite Session Manager, IAP, Bastion and tailnet broker architectures. (M, M) | `[gap]` |
| 1.219 | `cloud-firewalls.md`: docker: cite Docker/UFW bypass behaviour for host-versus-cloud firewall advice. (M, M) | `[gap]` |
| 1.220 | `cloud-firewalls.md`: gcp-policies: cite hierarchical and network firewall policy evaluation order. (M, M) | `[gap]` |
| 1.221 | `cloud-firewalls.md`: azure-admin: cite Azure security-admin rule behaviour. (M, M) | `[gap]` |
| 1.222 | `egress-metadata.md`: cloud-egress: source or narrow the universal/most-providers outbound-default claim and AWS security-group union, NACL and default-egress conjunction. (M, M) | `[gap]` |
| 1.223 | `egress-metadata.md`: host-owner: cite owner-match and nftables paths for the host egress controls. (M, M) | `[gap]` |
| 1.224 | `egress-metadata.md`: verify-allow: cite unauthenticated STS GET behaviour for the stated allow test. (M, M) | `[gap]` |
| 1.225 | `cloudflare.md`: prerequisites: pin the free-tier up-to-50-users limit or keep the current-limit qualification explicit. (M, M) | `[gap]` |
| 1.226 | `cloudflare.md`: quick: cite Cloudflare Quick Tunnel documentation for the unauthenticated short-lived-test claim. (M, M) | `[gap]` |
| 1.227 | `tunnels.md`: pin `ufw status verbose` and `ufw show raw` behaviour, the incomplete status view and IPv6; the rolling citation landed but its planned pin did not. (M, M) | `[gap]` |
| 1.230 | `authentication.md`: offboarding: source membership, proxy and token revocation delays and time-to-revoke checks. (M, M) | `[gap]` |
| 1.231 | `authentication.md`: verify-origin-isolation: source the proxy isolation expectation beyond the current Cloudflare citations, retaining the deployed-origin result as a test expectation. (M, M) | `[gap]` |
| 1.232 | `mfa.md`: push-matching, webauthn-recovery and verify-offboarding: source verified push, the administrator second-hardware-key preference and operator alert, and app-level authorization revocation; map the sections of the NIST SP 800-63B-4 document already in Sources (the cited URL targets section 3.1.2) to the portions they support (citation-location maintenance, not missing support): section 3.1.3 for the authentication-fatigue rationale for secret transfer, section 3.2.5 for the non-phishing-resistance of OTP and out-of-band authenticators, sections 3.1.3.1 and 3.1.3.3 for the email prohibition and PSTN restriction, sections 4.2.1.1 and 4.2.3 for recovery-code throttling and recovery notification, and section 4.5 for invalidation of enrolled authenticators when the subscriber no longer meets eligibility requirements. (M, M) | `[gap]` |
| 1.233 | `mfa.md`: admin-factors and authelia-factors: cite administrator policy and Authelia passkey behaviour. (M, M) | `[gap]` |
| 1.234 | `mfa.md`: webauthn-library and unattended-mtls: cite library and mTLS deployment behaviour or label guidance as assessment. (M, M) | `[gap]` |
| 1.235 | `mfa.md`: verify-recovery-history: cite the recovery-code scan behaviour. (M, M) | `[gap]` |
| 1.236 | `identity-providers.md`: auth0-passkey-policy and admin-passkeys: cite Auth0/passkey tiers, password disablement and WebAuthn policy behaviour. (M, M) | `[gap]` |
| 1.237 | `identity-providers.md`: entra-every-signin and application-allowlist: cite Entra Conditional Access and Google/Microsoft application allowlists. (M, M) | `[gap]` |
| 1.238 | `identity-providers.md`: firebase-data-policy and github-proxy-workloads: cite Firebase Rules and GitHub Actions OIDC behaviour. (M, M) | `[gap]` |
| 1.239 | `identity-providers.md`: google-org-mfa: pin the remaining OIDC pricing claim while preserving the cited 2SV enforcement scope. (M, M) | `[gap]` |
| 1.240 | `identity-providers.md`: self-hosted-mfa: cite maintenance expectations for Keycloak, authentik and Ory beyond their already pinned factor behaviour. (M, M) | `[gap]` |
| 1.241 | `oidc-integration.md`: client-secret-storage: pin a secret-storage reference for the client-secret handling claim. (M, M) | `[gap]` |
| 1.242 | `self-hosted-idp.md`: keycloak-bootstrap, keycloak-mfa, verify-mfa-password and admin-factor-order: cite Keycloak factor/flow enforcement and authentik factor ordering. (M, M) | `[gap]` |
| 1.243 | `self-hosted-idp.md`: http-listener, keycloak-http-opt-in, verify-direct-ports and verify-proxy-neutralization: cite Keycloak 8080/8443 listener behaviour and curl exit 0 and 28, timeout, proxy-setting and curlrc behaviour; retain curl outcomes as expectations without a live run. (M, M) | `[gap]` |
| 1.244 | `self-hosted-idp.md`: authentik-mfa and outpost-boundaries: cite authentik factor/flow binding and outpost listeners. (M, M) | `[gap]` |
| 1.245 | `self-hosted-idp.md`: verify-authentik-routes and idp-maintenance: cite replacement-route and maintenance behaviour. (M, M) | `[gap]` |
| 1.246 | `php.md`: plain-auth: pin plain-PHP throttling and MFA mechanisms or label the recommendation as guide advice. (M, M) | `[gap]` |
| 1.247 | `frontend-frameworks.md`: svelte-handle: establish layout coverage, every-request hook and calling-page metadata qualifications from SvelteKit source. (M, M) | `[gap]` |
| 1.248 | `frontend-frameworks.md`: verify-host: source non-Vite Host allowlists and platform behaviour not established by the pinned SvelteKit/Nuxt paths. (M, M) | `[gap]` |
| 1.249 | `web-exposure.md`: apache-listing: cite Debian/Ubuntu Apache defaults and index-list behaviour. (M, M) | `[gap]` |
| 1.250 | `web-exposure.md`: source-maps: cite the source-map exposure claim and its scope. (M, M) | `[gap]` |
| 1.251 | `admin-uis.md`: private: source RedisInsight private/NAT-without-host-listener behaviour. (M, M) | `[gap]` |
| 1.252 | `low-code-builders.md`: Budibase initialization and validation: pin Budibase sources for the stated setup and authentication behaviour. (M, M) | `[gap]` |
| 1.253 | `server-admin-panels.md`: pin Proxmox bind/LISTEN_IP/access-list behaviour as one versioned conjunction. (M, M) | `[gap]` |
| 1.254 | `deployment-lifecycle.md`: tcp-scan: cite non-OpenBSD `nc` behaviour used by the check. (M, M) | `[gap]` |
| 1.255 | `deployment-lifecycle.md`: initialize-secrets, registration and setup-route: cite application bootstrap and first-owner/setup-route behaviour or narrow the universal contract. (M, M) | `[gap]` |
| 1.256 | `deployment-lifecycle.md`: fronting-order and clone-secrets: cite deployment-order and clone credential-lifecycle behaviour. (M, M) | `[gap]` |
| 1.257 | `deployment-lifecycle.md`: retire-credentials and offboarding: source per-layer revocation and delayed invalidation checks. (M, M) | `[gap]` |
| 1.258 | `deployment-lifecycle.md`: reverify: source or narrow the claim that restores recreate defaults and reset flags. (M, M) | `[gap]` |
| 1.259 | `deployment-lifecycle.md`: certificate-monitor: cite Certbot dry-run behaviour for renewal verification. (M, M) | `[gap]` |
| 1.260 | `deployment-lifecycle.md`: dns-retirement: cite DNS TTL, resource retention and takeover behaviour for the retirement procedure. (M, M) | `[gap]` |
| 1.261 | `gpu-clouds.md`: verify-jupyter: cite Jupyter `/api/contents` and the 403/200 expectation with and without a token. (M, M) | `[gap]` |
| 1.262 | `gpu-clouds.md`: modal-shared: cite the Shared Endpoints exception. (M, M) | `[gap]` |
| 1.263 | `gpu-clouds.md`: listener-auth and remote-desktop: cite Ollama authentication defaults and VNC/noVNC ports and password behaviour. (M, M) | `[gap]` |
| 1.264 | `gpu-clouds.md`: mfa and verify-inventory: cite platform-account MFA, Vast variables and `ss` namespace scope. (M, M) | `[gap]` |
| 1.265 | `mlflow.md`: mfa and proxy-token: cite oauth2-proxy/Cloudflare fronting MFA and Cloudflare service-token header syntax. (M, M) | `[gap]` |
| 1.266 | `paas.md`: managed-tls and listener-port: cite Railway TLS/ports, Heroku ACM and injected-port/Fly binding behaviour. (M, M) | `[gap]` |
| 1.267 | `paas.md`: spaces-creation and spaces-dev: cite organization private visibility and Dev Mode endpoint behaviour. (M, M) | `[gap]` |
| 1.268 | `paas.md`: https-redirect and verify-redirect: cite exact redirect toggles and expected statuses for each named platform. (M, M) | `[gap]` |
| 1.269 | `paas.md`: verify-app-auth and verify-secrets: source or label the exact bypass and auth procedures and the bundle scan procedure, and their limits. (M, M) | `[gap]` |
| 1.270 | `sqlite.md`: Bash builtins/guards and curl: cite the shell and curl behaviour behind the checks. (M, M) | `[gap]` |
| 1.271 | `sqlite.md`: grep: cite GNU grep behaviour for the SQLite scan. (M, M) | `[gap]` |
| 1.272 | `sqlite-http-frontends.md`: container-generator: cite Datasette container generator behaviour at its pinned version. (M, M) | `[gap]` |
| 1.273 | `nodejs.md`: bind: cite platform bind mappings and their deployment scope. (M, M) | `[gap]` |
| 1.274 | `nodejs.md`: password: cite Argon2id recommendation and bcrypt library APIs. (M, M) | `[gap]` |
| 1.275 | `nodejs.md`: mfa: source the fronting identity layer beyond the already pinned otplib/qrcode examples. (M, M) | `[gap]` |
| 1.276 | `python.md`: bind: cite platform bind mappings and their deployment scope. (M, M) | `[gap]` |
| 1.277 | `python.md`: password: cite bcrypt API and no-user-store conjunction. (M, M) | `[gap]` |
| 1.278 | `python.md`: secrets: cite or label the 32-byte generation choice. (M, M) | `[gap]` |
| 1.279 | `go.md`: tokens: pin Token environment handling; preserve the delegation of Token generation to p4.66. (M, M) | `[gap]` |
| 1.280 | `go.md`: mfa: cite the fronting identity layer used for MFA enforcement. (M, M) | `[gap]` |
| 1.281 | `java.md`: mfa: cite provider/fronting enforcement for the stated MFA setup. (M, M) | `[gap]` |
| 1.282 | `java.md`: client-validation: cite the trust-all API and its scope. (M, M) | `[gap]` |
| 1.283 | `agent-builders.md`: debug-remedy: establish whether the debug_permission change is available in the console UI; API remedy is already cited and UI availability is unestablished. (M, M) | `[gap]` |
| 1.284 | `dotnet.md`: mfa: cite fronting-layer MFA enforcement. (M, M) | `[gap]` |
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
| 3.39 | Render Sources with a pinned CommonMark parser in `tools/version_basis.py` (for example markdown-it-py, installed and SHA-verified in CI like shellcheck; local runs SKIP with an advisory when absent) and check rendered link targets against component URLs, replacing the line-grammar approximation of #420. Seven review rounds on #420 each found a new exotic construct the regex approach missed; residuals are listed in CONTRIBUTING. (M, M) | `[gap]` |

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
