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

Next ids: **1.290**, **2.48**, **3.41**, **4.12**.

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
| 1.199 | `realtime-webhooks.md`: proxy-limits: pin vendor sources for the proxy capability summaries beyond the cited Caddy timeouts, nginx, Traefik and HAProxy (M, M) | `[gap]` |
| 1.200 | `apache.md`: mfa: cite Cloudflare Access application and policy controls for the suggested fronting option (M, M) | `[gap]` |
| 1.201 | `lighttpd.md`: mfa: cite Authelia supported-proxy list and Cloudflare Access for the stated exclusion and MFA fronting option (M, M) | `[gap]` |
| 1.202 | `lighttpd.md`: verify-config and verify-host: cite lighttpd command/service-manager behavior and Apache SNI selection for the comparison (M, M) | `[gap]` |
| 1.203 | `headers.md`: placement: cite proxy header directives and static-host `_headers` handling for the stated controls (M, M) | `[gap]` |
| 1.204 | `headers.md`: all-responses: map the already pinned nginx `add_header` inheritance source to this guide’s response-header claim (M, M) | `[gap]` |
| 1.205 | `docker.md`: auth and verify-auth: pin the authentication-provider and proxy sources for MFA rejection and the 401/403 discriminator (M, M) | `[gap]` |
| 1.206 | `docker.md`: workload: cite Git, USER, capabilities, no-new-privileges, read-only filesystem and socket controls from Docker and Git sources (M, M) | `[gap]` |
| 1.207 | `docker.md`: persistence: cite Docker firewall/INPUT-path behavior and the startup-unit mechanism behind persistence advice (M, M) | `[gap]` |
| 1.208 | `docker.md`: alternate-entry: cite cloudflared, tailnet and self-signed TLS alternatives for the stated entry paths (M, M) | `[gap]` |
| 1.209 | `docker.md`: upstream and verify-redirect: cite cloud security-group/network-ACL and proxy redirect behavior; keep database TLS/authentication source work delegated to the linked guides (M, M) | `[gap]` |
| 1.210 | `container-hardening.md`: docker-socket: cite the Docker privilege model for socket root equivalence (M, M) | `[gap]` |
| 1.211 | `container-hardening.md`: verify-probe: establish what the deployed `busybox:1.36` image actually contains for `nc -z -w 3`; the pinned BusyBox source alone does not map the image (M, M) | `[gap]` |
| 1.212 | `container-hardening.md`: Compose exec and process diagnostics: cite Docker Compose and process-tool behavior used by the checks (M, M) | `[gap]` |
| 1.213 | `host.md`: include-order: pin OpenSSH Include/drop-in, Ubuntu 20.04 and cloud-init history relevant to SSH config ordering (M, M) | `[gap]` |
| 1.214 | `host.md`: brokered-ssh: cite SSM, IAP, Bastion and tailnet broker behavior for the stated alternatives (M, M) | `[gap]` |
| 1.215 | `host.md`: docker-bypass: cite Docker/UFW interaction and its firewall-bypass qualification (M, M) | `[gap]` |
| 1.216 | `host.md`: updates: cite unattended-upgrades and dnf-automatic package/service behavior (M, M) | `[gap]` |
| 1.217 | `host.md`: verify-listeners: cite `ss`, `nc`, SSH and BusyBox behavior for the inventory and reachability tests (M, M) | `[gap]` |
| 1.218 | `cloud-firewalls.md`: ssm, iap and bastion: cite Session Manager, IAP, Bastion and tailnet broker architectures (M, M) | `[gap]` |
| 1.219 | `cloud-firewalls.md`: docker: cite Docker/UFW bypass behavior for host-versus-cloud firewall advice (M, M) | `[gap]` |
| 1.220 | `cloud-firewalls.md`: gcp-policies: cite hierarchical and network firewall policy evaluation order (M, M) | `[gap]` |
| 1.221 | `cloud-firewalls.md`: azure-admin: cite Azure security-admin rule behavior (M, M) | `[gap]` |
| 1.222 | `egress-metadata.md`: cloud-egress: source or narrow the universal/most-providers outbound-default claim and AWS security-group union, NACL and default-egress conjunction (M, M) | `[gap]` |
| 1.223 | `egress-metadata.md`: host-owner: cite owner-match and nftables paths for the host egress controls (M, M) | `[gap]` |
| 1.224 | `egress-metadata.md`: verify-allow: cite unauthenticated STS GET behavior for the stated allow test (M, M) | `[gap]` |
| 1.225 | `cloudflare.md`: prerequisites: pin the free-tier up-to-50-users limit or keep the current-limit qualification explicit (M, M) | `[gap]` |
| 1.226 | `cloudflare.md`: quick: cite Cloudflare Quick Tunnel documentation for the unauthenticated short-lived-test claim (M, M) | `[gap]` |
| 1.227 | `tunnels.md`: pin `ufw status verbose` and `ufw show raw` behavior, the incomplete status view and IPv6; the rolling citation landed but its planned pin did not (M, M) | `[gap]` |
| 1.228 | `authentication.md`: default-deny, individual-credentials and verify-default-accounts: cite product default-account behavior or label the endpoint inventory and account-name checks as guide assessment (M, M) | `[gap]` |
| 1.229 | `authentication.md`: session-cookies: source the cookie-signing claim or label the recommendation at its current scope (M, M) | `[gap]` |
| 1.230 | `authentication.md`: offboarding: source membership, proxy and token revocation delays and time-to-revoke checks (M, M) | `[gap]` |
| 1.231 | `authentication.md`: verify-origin-isolation and verify-cross-user: source proxy isolation and authorization expectations where the current OWASP/Cloudflare citations do not cover the full claim (M, M) | `[gap]` |
| 1.232 | `mfa.md`: push-matching, webauthn-recovery and verify-offboarding: map the already cited NIST SP 800-63B-4 sections to the specific claims; retain their stated limits (M, M) | `[gap]` |
| 1.233 | `mfa.md`: admin-factors and authelia-factors: cite administrator policy and Authelia passkey behavior (M, M) | `[gap]` |
| 1.234 | `mfa.md`: webauthn-library and unattended-mtls: cite library and mTLS deployment behavior or label guidance as assessment (M, M) | `[gap]` |
| 1.235 | `mfa.md`: verify-recovery-history: cite the recovery-code scan behavior and keep run outcomes distinct from expectations (M, M) | `[gap]` |
| 1.236 | `identity-providers.md`: auth0-passkey-policy and admin-passkeys: cite Auth0/passkey tiers, password disablement and WebAuthn policy behavior (M, M) | `[gap]` |
| 1.237 | `identity-providers.md`: entra-every-signin and application-allowlist: cite Entra Conditional Access and Google/Microsoft application allowlists (M, M) | `[gap]` |
| 1.238 | `identity-providers.md`: firebase-data-policy and github-proxy-workloads: cite Firebase Rules and GitHub Actions OIDC behavior (M, M) | `[gap]` |
| 1.239 | `identity-providers.md`: google-org-mfa: pin the remaining OIDC pricing claim while preserving the cited 2SV enforcement scope (M, M) | `[gap]` |
| 1.240 | `identity-providers.md`: self-hosted-mfa: cite maintenance expectations for Keycloak, authentik and Ory beyond their already pinned factor behavior (M, M) | `[gap]` |
| 1.241 | `oidc-integration.md`: client-secret-storage: pin a secret-storage reference for the client-secret handling claim (M, M) | `[gap]` |
| 1.242 | `self-hosted-idp.md`: keycloak-mfa, verify-mfa-password and admin-factor-order: cite Keycloak factor/flow enforcement and authentik factor ordering (M, M) | `[gap]` |
| 1.243 | `self-hosted-idp.md`: http-listener, keycloak-http-opt-in and verify-direct-ports: cite Keycloak 8080/8443 listener behavior; retain curl outcomes as expectations without a live run (M, M) | `[gap]` |
| 1.244 | `self-hosted-idp.md`: authentik-mfa and outpost-boundaries: cite authentik factor/flow binding and outpost listeners (M, M) | `[gap]` |
| 1.245 | `self-hosted-idp.md`: verify-authentik-routes and idp-maintenance: cite replacement-route and maintenance behavior (M, M) | `[gap]` |
| 1.246 | `php.md`: plain-auth: pin plain-PHP throttling and MFA mechanisms or label the recommendation as guide advice (M, M) | `[gap]` |
| 1.247 | `frontend-frameworks.md`: svelte-handle: establish layout coverage, every-request hook and calling-page metadata qualifications from SvelteKit source (M, M) | `[gap]` |
| 1.248 | `frontend-frameworks.md`: verify-host: source non-Vite Host allowlists and platform behavior not established by the pinned SvelteKit/Nuxt paths (M, M) | `[gap]` |
| 1.249 | `web-exposure.md`: apache-listing: cite Debian/Ubuntu Apache defaults and index-list behavior (M, M) | `[gap]` |
| 1.250 | `web-exposure.md`: source-maps: cite the source-map exposure claim and its scope (M, M) | `[gap]` |
| 1.251 | `admin-uis.md`: private: source RedisInsight private/NAT-without-host-listener behavior (M, M) | `[gap]` |
| 1.252 | `low-code-builders.md`: Budibase initialization and validation: pin Budibase sources for the stated setup and authentication behavior (M, M) | `[gap]` |
| 1.253 | `server-admin-panels.md`: pin Proxmox bind/LISTEN_IP/access-list behavior as one versioned conjunction (M, M) | `[gap]` |
| 1.254 | `deployment-lifecycle.md`: tcp-scan: cite non-OpenBSD `nc` behavior used by the check (M, M) | `[gap]` |
| 1.255 | `deployment-lifecycle.md`: initialize-secrets, registration and setup-route: cite application bootstrap and first-owner/setup-route behavior or narrow the universal contract (M, M) | `[gap]` |
| 1.256 | `deployment-lifecycle.md`: fronting-order and clone-secrets: cite deployment-order and clone credential-lifecycle behavior (M, M) | `[gap]` |
| 1.257 | `deployment-lifecycle.md`: retire-credentials and offboarding: source per-layer revocation and delayed invalidation checks (M, M) | `[gap]` |
| 1.258 | `deployment-lifecycle.md`: reverify: source or narrow the claim that restores recreate defaults and reset flags (M, M) | `[gap]` |
| 1.259 | `deployment-lifecycle.md`: certificate-monitor: cite Certbot dry-run behavior for renewal verification (M, M) | `[gap]` |
| 1.260 | `deployment-lifecycle.md`: dns-retirement: cite DNS TTL, resource retention and takeover behavior for the retirement procedure (M, M) | `[gap]` |
| 1.261 | `gpu-clouds.md`: verify-jupyter: cite Jupyter `/api/contents` and the 403/200 expectation with and without a token (M, M) | `[gap]` |
| 1.262 | `gpu-clouds.md`: modal-shared: cite the Shared Endpoints exception (M, M) | `[gap]` |
| 1.263 | `gpu-clouds.md`: listener-auth and remote-desktop: cite Ollama authentication defaults and VNC/noVNC ports and password behavior (M, M) | `[gap]` |
| 1.264 | `gpu-clouds.md`: mfa and verify-inventory: cite platform-account MFA, Vast variables and `ss` namespace scope (M, M) | `[gap]` |
| 1.265 | `mlflow.md`: mfa and proxy-token: cite oauth2-proxy/Cloudflare fronting MFA and Cloudflare service-token header syntax (M, M) | `[gap]` |
| 1.266 | `paas.md`: managed-tls and listener-port: cite Railway TLS/ports, Heroku ACM and injected-port/Fly binding behavior (M, M) | `[gap]` |
| 1.267 | `paas.md`: spaces-creation and spaces-dev: cite organization private visibility and Dev Mode endpoint behavior (M, M) | `[gap]` |
| 1.268 | `paas.md`: https-redirect and verify-redirect: cite exact redirect toggles and expected statuses for each named platform (M, M) | `[gap]` |
| 1.269 | `paas.md`: verify-secrets: source or label the exact bypass/auth/bundle scan procedures and their limits (M, M) | `[gap]` |
| 1.270 | `sqlite.md`: Bash builtins/guards and curl: cite the shell and curl behavior behind the checks (M, M) | `[gap]` |
| 1.271 | `sqlite.md`: grep: cite GNU grep behavior for the SQLite scan and classify an error as inconclusive (M, M) | `[gap]` |
| 1.272 | `sqlite-http-frontends.md`: container-generator: cite Datasette container generator behavior at its pinned version (M, M) | `[gap]` |
| 1.273 | `nodejs.md`: bind: cite platform bind mappings and their deployment scope (M, M) | `[gap]` |
| 1.274 | `nodejs.md`: password: cite Argon2id recommendation and bcrypt library APIs (M, M) | `[gap]` |
| 1.275 | `nodejs.md`: mfa: source the fronting identity layer beyond the already pinned otplib/qrcode examples (M, M) | `[gap]` |
| 1.276 | `python.md`: bind: cite platform bind mappings and their deployment scope (M, M) | `[gap]` |
| 1.277 | `python.md`: password: cite bcrypt API and no-user-store conjunction (M, M) | `[gap]` |
| 1.278 | `python.md`: secrets: cite or label the 32-byte generation choice (M, M) | `[gap]` |
| 1.279 | `go.md`: tokens: pin Token environment handling; preserve the delegation of Token generation to p4.66 (M, M) | `[gap]` |
| 1.280 | `go.md`: mfa: cite the fronting identity layer used for MFA enforcement (M, M) | `[gap]` |
| 1.281 | `java.md`: mfa: cite provider/fronting enforcement for the stated MFA setup (M, M) | `[gap]` |
| 1.282 | `java.md`: client-validation: cite the trust-all API and its scope (M, M) | `[gap]` |
| 1.283 | `agent-builders.md`: debug-remedy: establish whether the debug_permission change is available in the console UI; API remedy is already cited and UI availability is unestablished (M, M) | `[gap]` |
| 1.284 | `dotnet.md`: mfa: cite fronting-layer MFA enforcement (M, M) | `[gap]` |
| 1.285 | `gitops-controllers.md`: verify-flux: cite curl `--data-binary` behavior; the six historical GitOps facts remain delegated to row 2.28 (M, M) | `[gap]` |
| 1.286 | `lighttpd.md`: pin lighttpd TLS/key introduction versions for the 1.4.56 protocol defaults and 1.4.53 separate-key syntax (M, M) | `[gap]` |
| 1.287 | `self-signed.md`: key-permissions: cite filesystem command and mode behavior for the private-key instructions (M, M) | `[gap]` |
| 1.288 | `self-signed.md`: verification-bypasses: cite Node.js bypass settings and their scope (M, M) | `[gap]` |
| 1.289 | `identity-providers.md`: maintain the Supabase `aal2` authorization-policy claim mapping to the source already cited in the guide (M, S) | `[gap]` |
| 2.28 | `gitops-controllers.md`: Complete the remaining source audit of image tag-to-build mapping (Redis, Dex), the application-controller bind address, repo-server service method authorization, Dex API method authorization, whether Redis overwrites its password in argv, and RBAC server-side wiring. (M, M) | `[gap]` |
| 2.29 | `self-hosted-ci-runners.md`: offline inspection outcomes are recorded in the guide. Remaining: verify and cite a pinned vendor source for the `[runners.docker]` `pid_mode` TOML key, corroborated only in rolling GitLab Runner source. (M, M) | `[gap]` |
| 1.117 | `search-engines.md` Verify (#285): the reviewed tools/scan_credential.sh searches client output and local refs/HEAD/reflog commit trees, with tools/test_scan_credential.py retaining dummy positive/negative controls and documented limits. Still open: run a real client pipeline in a disposable copy with a known dummy admin, master or bootstrap key, require detection, then remove it and rebuild cleanly and require scoped absence; retain a separate old-commit positive control and record the stated coverage limits. No real application build was available for the hand-built fixtures. (M, M) | `[gap]` |

## Priority 3: Add missing content

Gaps from the same audit, one row per missing guide. A gap raised by more than one family is
marked, and those are the ones worth taking first.

| ID | Item | Tags |
| --- | --- | --- |
| 3.40 | F-LYCHEE-2026-09-28 remainder after #448: six bare body citations in `agent-builders.md` (two), `jupyter.md`, `mlflow.md`, `sqlite-http-frontends.md` and `workflow-orchestrators.md` remain checked in truncated form until written as autolinks (#447). Then confirm with lychee `--dump` that no cited URL is extracted in truncated form, and confirm the first live weekly sweep. (S, S) | `[gap]` |

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
