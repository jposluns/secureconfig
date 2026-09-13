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

Next ids: **1.43**, **2.24**, **3.11**, **4.5**.

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
| 1.42 | Residual placeholder-guard gaps left by #50, all demonstrated by QA and none a regression against what preceded them. A STALE exported `probe_ip` defeats a partial paste, because `${probe_ip:-}` protects an absent variable and not a populated one, so copying from `case` to `esac` without the assignment probes the old target silently. Pre-existing shell attributes defeat the unedited block: `declare -i probe_ip` assigns `0` and `declare -l` lowercases the placeholder, and neither matches the rejection pattern. Netcat reports a denied local socket as exit 1 with no output, so "must fail to connect" still accepts an inconclusive local failure, and BusyBox netcat rejects `-v` outright. `deployment-lifecycle.md`'s port-by-port bullet still holds an unguarded inline `nc` loop: its two commands are offered as alternatives with prose between them, so moving them into one fenced block would change their meaning and needs a rewrite rather than a substitution. Decide whether the guides require copying the complete assignment-and-guard unit, isolate the snippet from shell attributes, and classify local errors and unsupported options as inconclusive in the comment. (M, M) | `[enhance]` |

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
| 1.39 | `tailscale.md`: the default tailnet ACL is permissive, and device identity is not user authorization. The guide should say what an ACL has to do before "reachable only by your tailnet" means what a reader hears. (H, S) | `[enhance]` |
| 1.40 | `firebase-supabase.md`: per-overload RPC negative tests, and a worked pre-15 example of revoking a view from `public`, `anon` and `authenticated` together. (M, S) | `[enhance]` |
| 1.41 | `agent-builders.md`: establish whether Flowise, Langflow and LibreChat ship vendor Compose files a reader would be overriding. If they do, the `!reset` caveat added in #45 is load-bearing for them rather than advisory. Premise unverified per vendor. (M, S) | `[enhance]` |

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
| 3.9 | `VERSION` names the most recently merged pull request, so a bookkeeping pull request has to carry its OWN number, which is knowable only after the pull request is opened. #46 set its predecessor's number and was stale on merge; #47 corrected it. Settled in `DECISIONS.md`: the scheme stays and `CONTRIBUTING.md` gains the authoring step. A second gap found while merging #50 after #51: the scheme assumes pull requests merge in NUMERIC order. When they do not, the literal rule produces a version lower than the one already on `main`, so the value goes backwards, and no gate enforces monotonicity. Decide whether the authoring step gains an ordering rule, whether a monotonicity gate is added, or whether going backwards is accepted as harmless. | process |

## Decisions

Maintainer rulings moved to `DECISIONS.md` on 2026-09-13, in preparation for the OPF operational-files migration (row 3.8). A row may cite a decision there; this file no longer carries them.

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
