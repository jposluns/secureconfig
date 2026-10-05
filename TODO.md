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

Next ids: **1.193**, **2.48**, **3.41**, **4.12**.

Retired without ever naming an item, and never to be issued: **2.21** to **2.23** and **4.3** to **4.4**, assigned in error on 2026-09-13 when the band number was used in place of the series.

## Queueing

**AIQT: fix issues first.** Band 1 is worked to empty before anything else is picked, whatever
the severity of what is waiting in the other bands. After band 1 is clear, take the highest
severity across bands 2 and 3 together rather than finishing a band.

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
| 1.179 | F-SOURCES-GAPS: resolve the 173 distinct residual facts (177 guide-level entries across 54 guides) after #430 to #439: 171 consolidation residuals plus two unlanded READY facts. Of these, 167 remain owned here and six GitOps facts remain owned by row 2.28. Recheck unfetched pins, obtain qualifying pins, reword unsupported claims, and preserve delegation and run-evidence limits. `rabbitmq.md`: OTP 27 minimum, management wildcard HTTP 15672, Docker guest loopback exception; `clickhouse.md`: listener/default-user/networks/access-management conjunction; `vector-databases.md`: four hosted-console MFA arrangements and universal self-hosted "none/only" claim; `streamlit.md`: Google `hd` hosted-domain and consumer-account semantics; `n8n.md`: first-owner setup, complete host/container environment isolation, `/rest/login`, public-API 401/200, webhook missing-credential 401/403; `supabase-self-hosted.md`: `.env.example` demo secrets/signup/JWT/storage defaults; `firebase-supabase.md`: ShellCheck 0.11.0 authoring run; `pocketbase.md`: backup archive contents, legacy Appwrite collection/document grants and `documentSecurity`, creator/omitted-permission behavior; `workflow-orchestrators.md`: Prefect stored-secret retrieval, FAB 3.9.0 auth backends/public-role handling, Fernet generation/empty/lost-key conjunction, independently protected Codec Server; `observability-components.md`: Loki delete-policy/handler behavior, complete worker and ingester dial paths; `self-hosted-error-trackers.md`: GlitchTip account versus organization membership; `realtime-webhooks.md`: Caddy body limit plus absence of standard rate limiter; `realtime-voice-infra.md`: webhook JWT/SHA-256 verification; `nginx.md`: HTTP/2 introduction and older syntax, tickets default on plus rotation since 1.23.2, header inheritance, htpasswd syntax/cost/package/OWASP conjunction, auth_request plus Authelia/oauth2-proxy/Cloudflare MFA; `apache.md`: distro commands/packages, Authelia absence, mod_auth_openidc/provider MFA and Cloudflare; `caddy.md`: packaged user/reload/RuntimeDirectory, Cloudflare MFA/JWT/origin restrictions, image tag map/runtime conjunction; `traefik.md`: htpasswd/OWASP comparison, BasicAuth short-circuit before later middleware; `haproxy.md`: certificate deploy hook, Cloudflare MFA; `lighttpd.md`: htpasswd packages/hash compatibility, Authelia support-list absence/Cloudflare MFA, TLS/key introduction versions, "only three" loaded modules and redirect transition, Host auth/Apache SNI comparison; `free-certificates.md`: Origin CA free/lifetime/absolute usability claim, Certbot plugin/renewal/reconfigure coverage; `self-signed.md`: Debian/Ubuntu and RHEL/Fedora trust stores, RFC 9525 SAN/CN identification (p2.57, unconfirmed); `headers.md`: proxy header controls, generic static-host `_headers`, curl redirect/protocol/output conjunction; `docker.md`: auth/MFA rejection expectations, runtime/build secrets/history, Git/USER/capabilities/no-new-privileges/read-only/socket conjunction, firewall persistence/INPUT-path/startup advice, cloudflared/tailnet alternatives; `container-hardening.md`: socket root equivalence, BusyBox `nc -z -w 3`, kubectl merge/container-name behavior, Compose exec plus process diagnostics; `host.md`: SSH Include/drop-ins/cloud-init, SSM/IAP/Bastion/tailnet, Docker/UFW bypass, unattended-upgrades/dnf-automatic, ss/nc/SSH tests/BusyBox; `cloud-firewalls.md`: broker architectures, Docker/UFW bypass, GCP evaluation order, Azure admin rules; `egress-metadata.md`: universal outbound default, AWS group union/NACL/default-egress conjunction, owner match/nftables path, unauthenticated STS GET; `cloudflare.md`: free tier up to 50 users, Quick Tunnels unauthenticated; `authentication.md`: default/shared account names, Cloudflare fronts any app unchanged, HTML login protects no other transport, webhook replay, fail2ban; `mfa.md`: authentik MFA inheritance, Keycloak capabilities, oauth2-proxy MFA, Google PAM/package, Google organization enforcement, Duo RADIUS/LDAP, universal hosted passkeys and counter wording, MySQL, universal TOTP compatibility; `identity-providers.md`: authentik inheritance, Keycloak description, Google organization enforcement, undifferentiated Ory claim, Google prompts, universal TOTP compatibility; `oidc-integration.md`: GitHub organization membership proves MFA; `self-hosted-idp.md`: authentik admin separation/permissions, rootful socket power, rootless blast radius, curl exit 7, kcadm argument ordering; `secrets.md`: ENV/ARG/history/build secrets, Bash secrecy, GNU grep; `machine-auth.md`: API-key hashing, Docker history, AWS Secrets Manager, Google Secret Manager, Azure Key Vault, OpenBao capabilities/Linux Foundation attribution, 1Password, Bitwarden; `neo4j.md`: six guard-only blocks reportedly executed; `surrealdb.md`: Bash "never exported", procfs access/lifetime; `php.md`: curl minimum, plain-PHP throttling/MFA; `frontend-frameworks.md`: layout coverage, every-request hook, calling-page metadata, SvelteKit scheme, universal Host/proxy/cookie/Nuxt behavior; `web-exposure.md`: distro Apache defaults/index list, source maps, grep behavior; `admin-uis.md`: RedisInsight, OWASP minimum, NAT without host listener; `low-code-builders.md`: NocoDB release has no binaries, LiteLLM sample-key 200/401, Budibase initialization/validation; `server-admin-panels.md`: Proxmox bind/LISTEN_IP/access-list conjunction; `deployment-lifecycle.md`: universal first-owner/setup contract, credential rotation/revocation, offboarding/delayed invalidation, restores recreate defaults/reset flags, Certbot dry run, DNS retirement/TTL/procedure; `gpu-clouds.md`: Jupyter 403/200 pair, Shared Endpoints exception, account MFA, Ollama no auth, VNC/noVNC ports/passwords, Vast variables; `mlflow.md`: external MFA/oauth2-proxy/Cloudflare headers; `paas.md`: Railway TLS/ports, Heroku ACM, universal injected port/Fly, organization private visibility, Dev Mode, exact redirect/bypass/auth/bundle procedures; `sqlite.md`: Bash builtins/guards, Git history "permanently", grep, curl; `sqlite-http-frontends.md`: sqlite-web implementation, Datasette container generator, Bash guards; `nodejs.md`: platform bind mappings, ports below 1024, Argon2id recommendation/bcrypt APIs, token comparison, TLS environment variable/connection option/extra CA conjunction; `python.md`: platform mappings, bcrypt/no-user-store conjunction, slowapi, HTTPX CA environment, CPython/OpenSSL CA behavior; `go.md`: Token generation/environment handling (p4.66, generation delegated); `java.md`: MFA enforcement, trust-all scope; `gitops-controllers.md` (row 2.28): controller bind, notifications bind, repo RPC authorization, certificate fallback, Dex runtime authorization, Redis image bind. Row 1.178 still tracks the Browserless default. (M, XL) | `[gap]` |
| 1.173 | `self-hosted-idp.md` (#382), authentik `version/2026.8.3`: The server metrics handler and the bootstrap blueprint are pinned in source; the worker and outpost metrics handlers remain documentation-backed, so trace them at the tag if further source auditing is wanted. (H, M) | `[gap]` |
| 2.28 | `gitops-controllers.md`: Complete the missing-source audit of controller binds, repo-server RPC authorization and certificate fallback, Dex runtime authentication and authorization, the Redis image bind and password initializer, and the RBAC fallback before claiming those fully traced. (M, M) | `[gap]` |
| 2.29 | `self-hosted-ci-runners.md` (#130, reworked #213): run the `tomllib` config inspection (privileged/services_privileged/`host` tcp:// daemon/autoscaler one-job limits) offline against exposed and fixed fixtures. (M, M) | `[gap]` |
| 1.117 | `search-engines.md` Verify (#285): supply a concrete, credential-safe grep of a real client bundle and repository history for the admin, master or bootstrap key, with a disposable build containing a known dummy credential as the positive control. The loopback runs had no client bundle. (M, M) | `[gap]` |
| 1.139 | `realtime-voice-infra.md`: `turnserver.conf` holds the TURN password in plaintext. Document the hashed-key alternative and whether `turnadmin`'s key derivation takes the password in argv at coturn 4.18.0 (from the #353 plan, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.140 | `realtime-voice-infra.md`: evaluate a TURN allocation client that takes the password outside argv (stdin, a file or the environment), verified at a pinned tag, to replace `turnutils_uclient -w` in the allocation test, as CONTRIBUTING rule 7's third exception asks (from #354, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.141 | Create-once key writers (`model-servers.md`'s llama.cpp, SGLang, vLLM and text-generation-webui blocks, and the LobeChat and Stable Diffusion WebUI writers in `chat-uis.md` and `image-gen-uis.md`): a default ACL on the target directory is inherited by new files and defeats `umask 077`, so a key file can be group-readable while the guide says `0600`. Refuse a directory carrying a default ACL (`getfacl`) and assert the file's mode after the write, verifying setfacl/getfacl behaviour first (from the #355 review, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.144 | CONTRIBUTING rule 7's `read` exception and every block that uses it (among them `search-engines.md`, which CONTRIBUTING names as the model block): `read -r` takes only the first line of a paste, so a secret pasted with a newline leaves every later line for the reader's shell to run. Add one warning sentence to the rule (paste the secret alone) and apply it to every read-exception block (from the #356 review, maintainer ruling 2026-09-25). (L, M) | `[gap]` |
| 1.147 | `model-servers.md` Verify: the vLLM `/invocations` probe's subshell opens with `set -- 'REPLACE_WITH_A_REAL_SERVED_MODEL'`, with neither rule 6's `PASTE_WHOLE_BLOCK` marker nor its value count, so a paste that drops the `set --` line probes with the calling shell's own first argument when it has one. Give it the marker line (`set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_A_REAL_SERVED_MODEL'`), the marker check, `shift` and `[ "$#" -eq 1 ]`, as the key probe above it has (maintainer ruling 2026-09-26T00:27Z). (M, XS) | `[gap]` |
| 1.149 | `vector-databases.md`: check how the Milvus Helm chart and the Operator expose 9091 (a Service, and on which type), at a pinned chart and Operator version. Found in #361 review. (M, S) | `[gap]` |

## Priority 3: Add missing content

Gaps from the same audit, one row per missing guide. A gap raised by more than one family is
marked, and those are the ones worth taking first.

| ID | Item | Tags |
| --- | --- | --- |
| 3.40 | Weekly link check false positives: lychee truncates URLs at a double underscore (`__init__.py` sources in jupyter.md, litellm.md and sqlite-http-frontends.md were reported as 404 at their parent directory) and fetches configuration-value API base URLs (api.openai.com/v1 in open-webui.md). Fix the extraction or configuration and exclude configuration-value URLs, with recorded cases so a real 404 still fails (F-LYCHEE-2026-09-28). (S, S) | `[gap]` |

## Priority 4: Tooling and process

| ID | Item | Tags |
| --- | --- | --- |
| 3.30 | Extend the fenced-block Verify-marking gate planned in #389 to list items, table rows and prose units, with the same baseline-and-ratchet mechanism (maintainer ruling, 2026-09-26). (M, L) | `[gap]` |
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
