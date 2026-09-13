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

Next ids: **1.36**, **2.21**, **3.9**, **4.3**.

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
| 1.10 | `agent-builders.md`: Correct the implication that disabling Dify debugging removes publication: vendor Compose publishes 5003 unconditionally; provide a Compose port reset, inspect the merged configuration, and include 5003 in external verification; Verify step filters ss output by expected ports (`grep -E`), violating  (H, S) [2 families] | `[enhance]` |
| 1.14 | `elasticsearch.md`: Verify line 1 (`curl -s https://...:9200/ # 401 without credentials`) carries no `--cacert`, so against the stock auto-generated certificate it dies on TLS verification instead of printing the 401, inviting exactly the `-k` the corpus forbids; give it the same `--cacert` as the credentialed line; Co (M, S) [2 families] | `[enhance]` |
| 1.15 | `tailscale.md`: Verify has no `ss -tlnp` step, so `tailscale serve --bg localhost:3000` fronting an app bound to `0.0.0.0:3000` passes both Verify lines while the app answers its LAN/VPC directly; add the bind-check every comparable guide carries; "authenticated by membership and your tailnet ACLs" is asserted with (M, S) | `[enhance]` |
| 1.18 | `cloud-firewalls.md`: Verify step 1 ("list rules allowing 0.0.0.0/0") has no runnable command for any provider and all three Sources are documentation roots that carry none of the guide's claims; add the aws/gcloud/az enumeration one-liners and page-level citations (M, S) | `[enhance]` |
| 1.22 | `postgresql.md`: Add a wrong-password rejection check paired with a valid login against the same TCP host, database, and role; successful TLS and `pg_stat_ssl` checks cannot detect an earlier matching `hostssl` rule using `trust` (vendor) (M, S) | `[enhance]` |
| 1.25 | `egress-metadata.md`: Stop declaring curl exit 7 or 28 proof of egress-policy enforcement: connection failure does not identify its cause, and `--max-time` can expire after connection; require connection-phase evidence and policy logs/counters, otherwise report inconclusive (vendor) (M, S) | `[enhance]` |
| 1.34 | `host.md`: `ufw allow OpenSSH` admits the whole internet while cloud-firewalls.md rule 3 says SSH is not public; add the source-restricted form (`ufw allow from REPLACE_WITH_ADMIN_RANGE to any port 22`) or an explicit pointer to brokered access/tailnet (L, XS) | `[enhance]` |
| 1.7 | `firebase-supabase.md`: the "rules are the security" section never warns that a view (owner-rights by default; PostgreSQL CREATE VIEW documents `security_invoker`) or a SECURITY DEFINER function in an exposed schema serves data past every RLS policy through the same public API; add both plus a Verify probe through a view;  (H, S) [2 families] | `[enhance]` |

## Priority 2: Deepen existing guides

A real surface the guide never covers. Correct as far as it goes, and not far enough.

| ID | Item | Tags |
| --- | --- | --- |
| 1.11 | `llm-observability.md`: Add Phoenix administrator bootstrap before exposure: authentication creates `admin@localhost` with password `admin`; configure `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` before first startup or change the existing password, then verify default credentials fail (vendor) (H, S) | `[enhance]` |
| 1.12 | `traefik.md`: Add Docker-provider configuration with `providers.docker.exposedByDefault=false` and verify unintended containers have no routes; the default is true, so labelling the intended application does not exclude other containers (vendor) (H, S) | `[enhance]` |
| 1.13 | `devops-uis.md`: GitLab CE, the most-deployed self-hosted forge and a recurring RCE target, is absent; add a section covering the initial root password file, sign-up restriction, and instance visibility defaults (defaults unverified offline); Explain that Node-RED `adminAuth` protects the editor/admin API; protect p (M, S) [2 families] | `[enhance]` |
| 1.16 | `minio.md`: the web console listener (`--console-address`, conventionally 9001) is never named and Verify greps only 9000, so an internet-exposed console passes every check; name the flag and port, probe it, and add the exposure-index row (M, XS) | `[enhance]` |
| 1.17 | `rabbitmq.md`: epmd 4369 and Erlang distribution 25672 are absent although the shared Erlang cookie is their only credential and grants remote command execution when published, which tutorial compose files commonly do (vendor clustering docs not opened offline); add the ports, the cookie rule, and exposure-index r (M, S) | `[enhance]` |
| 1.19 | `web-exposure.md`: directory listing is never covered: Debian/Ubuntu Apache defaults include `Options Indexes` on /var/www (unverified offline), turning "unguessable" dump filenames into a browsable index; add Indexes/autoindex deny rules and a Verify request against a directory URL (M, XS) | `[enhance]` |
| 1.20 | `ruby.md`: Sidekiq Web is commonly mounted at /sidekiq with no constraint, exposing job arguments (often credentials) and queue control to anyone who reaches it; add the authenticated-mount pattern and a Verify probe of the path (M, XS) | `[enhance]` |
| 1.21 | `mysql.md`: Add an explicit `mysqlx_bind_address` or disable X Plugin when unused; MySQL 8.4 enables it by default on a separate wildcard listener at 33060, which `bind_address` does not constrain; verify both listeners (vendor) (M, S) | `[enhance]` |
| 1.23 | `nodejs.md`: Bound `trust proxy` to the actual proxy topology and require forwarded-header sanitization; an unconditional hop count permits unsafe trust when shorter paths exist, and forwarded host/protocol values affect Express request properties (vendor) (M, S) | `[enhance]` |
| 1.24 | `n8n.md`: Add authentication for private Webhook nodes using their Basic, Header, or JWT options, and verify known production webhook URLs reject unauthenticated requests; the existing workflows-API check does not establish webhook protection (vendor) (M, S) | `[enhance]` |
| 1.26 | `gradio.md`: Add deployment file-access controls: narrowly scope `allowed_paths` and static directories, exclude secrets with `blocked_paths`, and explain that cached files are shared across app users; include a harmless file-access isolation check (vendor) (M, S) | `[enhance]` |
| 1.27 | `caddy.md`: Cover the configuration-changing admin API on localhost:2019, ensure it is never publicly published, and document a permissioned Unix socket when untrusted workloads share the host; verify the effective admin listener (vendor) (M, S) | `[enhance]` |
| 1.28 | `ollama.md`: Verify step filters ss output by expected port (`grep 11434`), violating the rule against filtering (M, XS) | `[enhance]` |
| 1.29 | `memcached.md`: Verify step filters ss output by expected port (`grep 11211`), violating the rule against filtering (M, XS) | `[enhance]` |
| 1.30 | `tunnels.md`: `ssh -R` is the most common ad-hoc self-hosted tunnel and is absent: a remote forward on a server with `GatewayPorts` widened publishes the app unauthenticated, and the guide's own scope statement ("self-hosted tunnels") promises this case (L, S) | `[enhance]` |
| 1.31 | `python.md`: no warning that `python -m http.server` binds all interfaces by default and serves the working directory, `.env` included (Python http.server docs, not opened offline), a frequent quick-share suggestion the Vite section of frontend-frameworks.md already covers for its own ecosystem (L, XS) | `[enhance]` |
| 1.32 | `admin-uis.md`: Adminer, the single-file database panel scanners probe constantly at /adminer.php, is missing from the panel list; one paragraph with the never-public rule and its lack of its own account store (L, XS) | `[enhance]` |
| 1.33 | `secrets.md`: no mention that terraform.tfstate, kubeconfigs with embedded client keys, and ~/.docker/config.json are plaintext credential files that belong in .gitignore and in scanner scope alongside .env and *.pem (L, XS) | `[enhance]` |
| 1.35 | `gpu-clouds.md`: template-shipped desktop listeners (noVNC/VNC in ComfyUI and desktop images) are not mentioned; they are often password-less and land on the platform's public port mapping like any other listener (template defaults unverified offline) (L, S) | `[enhance]` |
| 1.6 | `docker.md`: the DOCKER-USER iptables chain, the vendor-documented way to filter published ports when loopback publishing is not viable, never appears even though it is documented on the packet-filtering page the guide already cites (not re-opened offline); Qualify localhost publication with Docker’s pre-28.0.0  (H, S) [3 families] | `[enhance]` |
| 1.8 | `model-servers.md`: LocalAI and text-generation-webui are absent; both are commonly deployed with `--listen`-style flags and have native key/auth options worth stating or honestly denying (unverified offline); Verify step filters ss output by expected ports (`grep -E`), violating the rule against filtering (H, S) [2 families] | `[enhance]` |
| 1.9 | `vector-databases.md`: Explicitly restrict Qdrant cluster port 6335 to cluster peers and include it in Verify, whose port filter currently omits it; API keys and bearer tokens never protect internal cluster communication (vendor); Verify never probes the backend ports directly from outside, leaving published container por (H, S) [2 families] | `[enhance]` |

## Priority 3: Add missing content

Gaps from the same audit, one row per missing guide. A gap raised by more than one family is
marked, and those are the ones worth taking first.

| ID | Item | Tags |
| --- | --- | --- |
| 2.5 | Guide for headless-cms-instant-api (Strapi, Directus, Hasura, PostgREST): commonly AI-deployed app backends with no guide: Hasura serves its whole GraphQL surface when no admin secret is set, Strapi's first `/admin` visitor registers the admin, PostgREST exposure hangs entirely on the anonymous role (defaults unverified offline) (H, L) [2 families] | `[gap]` |
| 2.6 | Guide for headless-browser-services (Selenium Grid, Playwright server, browserless, Chrome CDP :9222): agent and scraping stacks run these; Selenium Grid listens on all interfaces with no auth and an exposed CDP port hands over cookies and code execution (defaults unverified offline); no guide and no exposure-index rows (H, M) [2 families] | `[gap]` |
| 2.7 | Guide for supabase-self-hosted: firebase-supabase.md covers only the hosted rules layer; the self-hosted Docker stack ships demo JWT secret, demo anon/service_role keys, and a default dashboard basic-auth pair, so an unedited `docker compose up` publishes full database access (defaults from vendor .env.example; page not opened offline, so verify while authoring) (H, M) | `[gap]` |
| 2.8 | Guide for SearxNG: AI search tool often deployed without auth by default (H, S) | `[gap]` |
| 2.9 | Guide for LangServe: Exposes LangChain runnables as REST APIs, often without auth by default (H, M) | `[gap]` |
| 2.10 | Guide for LocalAI: Drop-in OpenAI replacement API often exposed without auth (H, M) | `[gap]` |
| 2.11 | Guide for gitops-controllers (Argo CD, Flux): cluster-admin-equivalent surface kubernetes.md never touches: Argo CD's initial admin password Secret and its quickstart-exposed UI/API decide who can deploy anything into the cluster (unverified offline) (M, M) | `[gap]` |
| 2.12 | Guide for self-hosted-ci-runners (GitHub Actions runner, GitLab Runner): a runner on a public repo executes fork-PR code on your host and registration tokens are credentials; corpus covers Jenkins but not the runner class AI-assisted projects actually attach to github.com/gitlab.com (unverified offline) (M, M) | `[gap]` |
| 2.13 | Guide for transactional-email-posture (SPF/DKIM/DMARC, SMTP submission credentials, open relay): password-reset and invite mail is part of the auth path of most deployments and spoofable senders undermine it; the corpus contains no SMTP/DMARC content at all (M, M) | `[gap]` |
| 2.14 | Guide for Vault deployment: The secret-store recommendation lacks a deployment guide covering TLS, sealing, audit logging, and retirement of the initial root token (vendor) (M, L) | `[gap]` |
| 2.15 | Guide for Onyx (formerly Danswer): Enterprise RAG server with complex default exposure (M, L) | `[gap]` |
| 2.16 | Guide for Mem0: Agent memory store with a REST API often exposed without auth (M, M) | `[gap]` |
| 2.17 | Guide for Text Embeddings Inference: HuggingFace embedding server with no native auth (M, S) | `[gap]` |
| 2.18 | Guide for time-series-metrics-stores (InfluxDB, VictoriaMetrics, QuestDB): monitoring stores beyond the Prometheus note in admin-uis.md; VictoriaMetrics single-node and the QuestDB web console ship without authentication (defaults unverified offline) (L, M) | `[gap]` |
| 2.19 | Guide for self-hosted-error-trackers (Sentry, GlitchTip): hold stack traces, environment values, and user PII for every wired app; same never-public class as llm-observability.md but uncovered (L, M) | `[gap]` |
| 2.20 | Guide for realtime-voice-infra (LiveKit self-hosted, coturn): voice-agent deployments are increasingly common and add API-key, WebRTC, and TURN relay surfaces none of the existing guides map (L, M) | `[gap]` |

## Priority 4: Tooling and process

| ID | Item | Tags |
| --- | --- | --- |
| 3.3 | Complete the `(#N)` pull-request references in `CHANGELOG.md`: PRs 3, 4, 5 and 7 are referenced nowhere, which means mapping historical bullets to the PR that shipped them (L, M) | `[changelog]` |

## Decisions on record

Taken by the maintainer on 2026-09-13, recorded so they are not re-litigated:

- **`ss | grep <port>` in 48 guides:** fix only the checks whose Verify claims nothing ELSE is
  exposed. A filtered check that asks "is this bound to loopback?" is correct for what it claims
  and stays. Judge each of the 48 rather than sweeping.
- **Order:** AIQT applies, errors first and to empty, then interleave by severity across the
  remaining bands.
- **The six AI-infra gaps** (LocalAI, LangServe, SearxNG, Mem0, text-embeddings-inference, Onyx):
  one guide covering the pattern, with a per-tool table of default port, default authentication,
  and the flag that changes it, rather than six guides.
- **Audit cadence:** monthly, and whenever the backlog empties before that.

## Priority 5: Site and adopters

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
