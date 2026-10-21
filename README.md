# secureconfig

Keep the world and its information more secure, one deployment at a time.

Security guides your AI assistant can follow, verify, and be honest about.

## What this is

A library of short, generic, copy-ready guides covering the full deployment surface of a modern project: certificates and tunnels; human and machine identity, MFA, and secrets; web servers and proxies; language runtimes and frameworks; containers and Kubernetes; hosts, cloud firewalls, PaaS, and rented GPU clouds; databases, storage, and messaging; the AI stack itself (model servers, vector databases, MCP servers, agent and chat UIs, LLM observability); and the operational controls around a deployment, from first run through teardown. At the time of writing that is 102 guides across the 12 categories indexed below, plus [controls-reference.md](controls-reference.md) for any service that has no guide yet.

## The gap and the standard

Publicly reachable services keep shipping with the gap on the deployment surface: services listening on plain HTTP, admin consoles with no login, AI tools exposed on their defaults. These guides close that gap, and they hold themselves to the standard they ask of you. Contributions must take every configuration line from the vendor documentation cited in the guide, and Verify steps declare what they rest on: DEMONSTRATED means the check ran against both the exposed and the fixed state, REASONED means it is derived from cited vendor behaviour and says so, and a reasoned step is never presented as verified. Where a tool has no native control, the guide says so plainly instead of inventing one. Most guides also carry machine-readable front matter recording the sources checked and, where known, the exact versions. An automated gate suite under [tools/](tools/) checks the structure of these declarations on every change, with a recorded list of older steps still being brought in line; whether a demonstration ran or a reasoned step is justified is checked in review, not by the gates.

## Built for AI assistants

This repository gives an AI assistant the security steps to apply and a way to be honest about what it verified. The guides are written for machine consumption: stable raw URLs, a machine-readable index at [secureconfig.ai/llms.txt](https://secureconfig.ai/llms.txt), every guide in one file at [secureconfig.ai/llms-full.txt](https://secureconfig.ai/llms-full.txt), baseline rules an assistant can apply directly (next section), a decision guide mapping deployments to guides, and a verification checklist that requires reporting what could not be tested rather than asserting a pass.

## The maintainer

Jeff Posluns has spent more than 30 years in technology and security and wants to help keep the world and its information more secure. He built this library from that experience and uses his own AI tooling to keep expanding and updating it, with automated checks so it keeps its accuracy as it grows. Everything here is free and in the public domain.

The guides are dedicated to the public domain under CC0; the one exception, vendored AIQT Guardrails material, is licensed under the Apache License 2.0 (see [Licence](#licence)).

## Use it

- With an AI assistant: tell it to secure your project using the guides at [github.com/jposluns/secureconfig](https://github.com/jposluns/secureconfig), or copy a ready-made task from [secureconfig.ai](https://secureconfig.ai); have it finish with the verification checklist below and report anything it could not test.
- By hand: start with the decision guide below, apply every guide that fits, and run the verification checklist.
- To contribute: open a GitHub issue or send a pull request (reaching Jeff any other way also works). To request a guide for an application with no guide yet, add a file to [requests/](requests/README.md) per its template, one application per pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

The site at [secureconfig.ai](https://secureconfig.ai), served from [site/](site/) through Cloudflare Pages, is the short public pointer to these guides.

## Instructions for AI development assistants

If you are an AI assistant configuring, generating, or reviewing a service, apply these rules:

1. Treat every service as internet-reachable unless you have confirmed otherwise. Bind services to `127.0.0.1` by default and expose them only through a TLS-terminating layer that requires authentication; keep backend, admin, and AI-tool services private.
2. Choose the certificate and access path before configuring exposure. A public DNS name with reachable ports 80 and 443: [free-certificates.md](free-certificates.md). A Cloudflare-managed domain with no inbound ports: [cloudflare.md](cloudflare.md). A tailnet with no public domain: [tailscale.md](tailscale.md). Internal or development use only: [self-signed.md](self-signed.md).
3. Apply every guide that fits the deployment, not just one. Select the service or framework, its host or platform, containers where used, plus identity, secrets, and the operational controls below. For a service with no guide, run the alignment assessment in [controls-reference.md](controls-reference.md), which distils the control patterns common to every guide, and verify the service's native controls against the vendor documentation; then request a guide by adding a file to the requests directory (https://github.com/jposluns/secureconfig/tree/main/requests) so the service is covered next time.
4. Redirect HTTP to HTTPS, or do not listen on HTTP at all.
5. Require authentication on every non-public endpoint. Never ship default or hardcoded credentials. Add MFA to human logins where viable per [mfa.md](mfa.md); where a tool has no native login, put one in front per [fronting-auth.md](fronting-auth.md).
6. A successful login is not authorization. Check the returned identity against an allowlist (tenant, hosted domain, group, or explicit users) before granting access. Choose the provider per [identity-providers.md](identity-providers.md), wire it per [oidc-integration.md](oidc-integration.md), or put login in front of the app per [cloud-identity-proxies.md](cloud-identity-proxies.md).
7. Keep secrets out of the repository and load them from the environment or a secret manager per [secrets.md](secrets.md); give each service and agent its own scoped credentials per [machine-auth.md](machine-auth.md).
8. Contain what an exposed or compromised service can reach. Block unneeded outbound access and lock down cloud metadata per [egress-metadata.md](egress-metadata.md), and never serve dotfiles, database dumps, or client secrets per [web-exposure.md](web-exposure.md).
9. AI and data tools (model servers, vector databases, MCP servers, agent builders, chat and image UIs, MLflow, Ray) vary in their defaults and native controls, and many need authentication and TLS configured explicitly. Keep them on loopback and apply the matching guide before any exposure.
10. Run the verification checklist below and each selected guide's Verify steps before reporting the work as complete. Report any item you could not test instead of asserting that it passed.

Fetch guides raw with `https://raw.githubusercontent.com/jposluns/secureconfig/<default-branch>/<guide>.md` (for example `.../main/nginx.md`). Every guide concatenated into a single file: https://secureconfig.ai/llms-full.txt (also [site/llms-full.txt](site/llms-full.txt) in this repository); the machine-readable index is https://secureconfig.ai/llms.txt

## Decision guide

Choose every route that applies; a deployment usually needs both service-specific guides and shared controls.

- Public web app with its own domain: [free-certificates.md](free-certificates.md), then the guide for your web server or proxy, then [authentication.md](authentication.md).
- App on a home server or behind NAT, with a domain you can put on Cloudflare: [cloudflare.md](cloudflare.md). The tunnel removes the need for open inbound ports and Access adds login in front of the app. With no domain at all: [tailscale.md](tailscale.md) (Serve for tailnet-only access, Funnel only with the app's own login), or [self-signed.md](self-signed.md) for internal use.
- Internal tool, staging, or local development: [self-signed.md](self-signed.md), with authentication still enabled.
- Human login or SSO: [identity-providers.md](identity-providers.md) to choose one and [self-hosted-idp.md](self-hosted-idp.md) if you run it yourself, [oidc-integration.md](oidc-integration.md) for app integration; [cloud-identity-proxies.md](cloud-identity-proxies.md) or [fronting-auth.md](fronting-auth.md) for login in front; [mfa.md](mfa.md) for the second factor, with an explicit access policy.
- Service-to-service or agent access: [machine-auth.md](machine-auth.md), [secrets.md](secrets.md).
- AI or agent deployment: the matching model-server, MCP, agent-builder, vector-database, UI, or observability guide, plus [gpu-clouds.md](gpu-clouds.md) where applicable and [egress-metadata.md](egress-metadata.md) for outbound and metadata.
- Containers and clusters: [docker.md](docker.md), [container-hardening.md](container-hardening.md), [kubernetes.md](kubernetes.md), [gitops-controllers.md](gitops-controllers.md), [self-hosted-ci-runners.md](self-hosted-ci-runners.md), then the host, cloud, PaaS, or GPU guide.
- Databases, caches, queues, and model servers: keep them off public interfaces entirely where possible; the per-tool guides cover TLS and authentication for the cases where network exposure is unavoidable.
- Databases, storage, and messaging: the service guide, plus [object-storage.md](object-storage.md), [firebase-supabase.md](firebase-supabase.md), [pocketbase.md](pocketbase.md), or [headless-cms-instant-api.md](headless-cms-instant-api.md) where access depends on storage or data rules.
- A pooler, proxy, or bouncer in front of a database: [connection-poolers.md](connection-poolers.md). Adding one moves the client-facing TLS and host rules off the database server and onto the pooler, which has its own defaults.
- Web application exposure: [web-exposure.md](web-exposure.md), [headers.md](headers.md), [cors.md](cors.md), [realtime-webhooks.md](realtime-webhooks.md).
- First deployment, preview, or teardown: [deployment-lifecycle.md](deployment-lifecycle.md), then [common-mistakes.md](common-mistakes.md).

## Guide index

### Certificates and tunnels

| Guide | Covers |
|---|---|
| [free-certificates.md](free-certificates.md) | Free publicly trusted certificates via ACME (Let's Encrypt, ZeroSSL), issuance, and automated renewal |
| [self-signed.md](self-signed.md) | OpenSSL and mkcert certificates when a public CA is not an option, plus distributing trust to clients |
| [cloudflare.md](cloudflare.md) | Cloudflare Tunnel and Zero Trust Access: authenticated external access with no open inbound ports |
| [tailscale.md](tailscale.md) | Tailscale serve (tailnet-only) and funnel (public) with automatic TLS |
| [tunnels.md](tunnels.md) | frp, WireGuard, and ssh -R, self-hosted tunnels when there is no public IP |

### Identity, authentication, and secrets

| Guide | Covers |
|---|---|
| [authentication.md](authentication.md) | Password storage, MFA, API keys, sessions, rate limiting, and secret handling |
| [identity-providers.md](identity-providers.md) | Hosted identity and MFA: Entra ID, Google, Okta, Entra External ID, Firebase and Identity Platform, Auth0, Cognito, Clerk, WorkOS, Supabase Auth, Duo; free tiers and who each fits |
| [self-hosted-idp.md](self-hosted-idp.md) | Self-hosted Keycloak and authentik: separating the admin surface at the proxy, the first-boot admin window, and the management port |
| [oidc-integration.md](oidc-integration.md) | OIDC login wiring for Google, Microsoft Entra, GitHub, and Okta: PKCE, redirect URIs, token validation, and the allowlist check |
| [cloud-identity-proxies.md](cloud-identity-proxies.md) | Login in front of the app with no code change: AWS ALB, Google IAP, Azure App Service, Cloudflare Access, ngrok, Vercel |
| [fronting-auth.md](fronting-auth.md) | oauth2-proxy, Authelia, Pomerium: login and MFA in front of an app that has none |
| [mfa.md](mfa.md) | MFA options: identity layers with QR-code TOTP enrolment, app libraries, SSH modules, Duo |
| [machine-auth.md](machine-auth.md) | Machine identity: API keys, client credentials, mutual TLS, workload identity federation, secret managers |
| [secrets.md](secrets.md) | Secrets: repository hygiene, scanning, rotation after a leak, sops/age |
| [vault.md](vault.md) | HashiCorp Vault: dev mode, listener TLS, seal custody, audit devices, retiring the initial root token, path-scoped ACL policies, bounded AppRole credentials and tokens, response-wrapped secret delivery, and authenticated metrics/profiling |

### Web servers and proxies

| Guide | Covers |
|---|---|
| [apache.md](apache.md) | Apache HTTP Server: TLS, redirect, HSTS, basic auth, client certificates |
| [nginx.md](nginx.md) | nginx: TLS, redirect, HSTS, basic auth, client certificates, reverse proxy |
| [lighttpd.md](lighttpd.md) | lighttpd: TLS via mod_openssl, redirect, basic auth |
| [caddy.md](caddy.md) | Caddy: automatic HTTPS, internal CA, basic auth |
| [haproxy.md](haproxy.md) | HAProxy: TLS termination, redirect, HSTS, basic auth |
| [traefik.md](traefik.md) | Traefik: ACME resolvers, HTTPS redirection, basic auth middleware |

### Languages and frameworks

| Guide | Covers |
|---|---|
| [nodejs.md](nodejs.md) | Node.js and Express: HTTPS server, security headers, sessions, password hashing |
| [python.md](python.md) | Flask, FastAPI/Uvicorn, Gunicorn, Django: TLS options and secure settings |
| [nextjs.md](nextjs.md) | Next.js: sessions, Route Handlers, Server Actions, Auth.js and Better Auth, Vercel |
| [go.md](go.md) | Go net/http: TLS, proxy layout, bcrypt, cookies, client TLS discipline |
| [dotnet.md](dotnet.md) | ASP.NET Core and Kestrel: HTTPS, HSTS, forwarded headers, Identity, cookies |
| [java.md](java.md) | Spring Boot: server.ssl, forwarded headers, Spring Security, session cookies |
| [php.md](php.md) | PHP and Laravel: password_hash, session cookies, trusted proxies, forced HTTPS |
| [ruby.md](ruby.md) | Rails and Puma: force_ssl, trusted proxies, has_secure_password, credentials |
| [frontend-frameworks.md](frontend-frameworks.md) | SvelteKit, Nuxt, Vite: server-route auth, sessions, public-env prefixes |

### Containers and Kubernetes

| Guide | Covers |
|---|---|
| [docker.md](docker.md) | Docker and Compose: safe port publishing, the UFW bypass problem, TLS termination |
| [kubernetes.md](kubernetes.md) | Gateway API with a maintained controller, cert-manager TLS, entry-point authentication; ingress-nginx is retired |
| [gitops-controllers.md](gitops-controllers.md) | Argo CD and Flux: cluster-admin blast radius, the initial admin secret, RBAC, and the Flux webhook receiver |
| [self-hosted-ci-runners.md](self-hosted-ci-runners.md) | GitHub Actions runner and GitLab Runner: untrusted code is remote code execution; ephemeral one-job workers, no privileged executor, tokens as credentials |
| [container-hardening.md](container-hardening.md) | Non-root, dropped capabilities, read-only root, network segmentation |

### Hosts and cloud platforms

| Guide | Covers |
|---|---|
| [host.md](host.md) | Host baseline: SSH hardening, firewall default-deny, brute-force protection, updates |
| [cloud-firewalls.md](cloud-firewalls.md) | Security groups and VPC rules: no 0.0.0.0/0 on databases, SSH posture |
| [paas.md](paas.md) | Render, Fly.io, Vercel, and similar: platform TLS, your auth and secrets |
| [gpu-clouds.md](gpu-clouds.md) | RunPod, Vast.ai, Lambda, Modal: exposed ports and differing firewall and auth defaults per platform |

### Databases, storage, and messaging

| Guide | Covers |
|---|---|
| [postgresql.md](postgresql.md) | PostgreSQL: server TLS, SCRAM authentication, pg_hba rules, verified client connections, runtime-vs-owner privilege separation, restricted CONNECT and schema CREATE, secure search_path, and connection/DDL audit logging |
| [connection-poolers.md](connection-poolers.md) | PgBouncer and pgpool-II: client TLS that is off by default, a server hop that falls back to plaintext, and the pg_hba rules a pooler stops matching |
| [mysql.md](mysql.md) | MySQL and MariaDB: required TLS transport, per-user TLS, modern auth plugins, scoped least-privilege accounts, anonymous/test/remote-root cleanup, local_infile and secure_file_priv restrictions, and password validation/reuse |
| [mongodb.md](mongodb.md) | MongoDB: requireTLS, authorization, bind address, least-privilege roles with explicit SCRAM-SHA-256, replica/cluster membership auth, per-user source restrictions, and x.509 client identities |
| [redis.md](redis.md) | Redis: TLS, requirepass, bind/protected-mode, and least-privilege ACLs with durable rules, key/channel scoping, and runtime command lockdown |
| [sqlite.md](sqlite.md) | SQLite in deployment, the file is the exposure; Turso tokens; Litestream |
| [sqlite-http-frontends.md](sqlite-http-frontends.md) | Datasette and sqlite-web: SQLite HTTP exposure, loopback binding, authentication, TLS, and verification |
| [surrealdb.md](surrealdb.md) | SurrealDB, root credentials, bind address, access levels, TLS |
| [time-series-metrics-stores.md](time-series-metrics-stores.md) | InfluxDB, VictoriaMetrics, and QuestDB: default-off auth, default credentials, and fronting |
| [elasticsearch.md](elasticsearch.md) | Elasticsearch and OpenSearch: keep built-in security on, scoped roles and API keys, anonymous/CORS lockdown, audit logging |
| [clickhouse.md](clickhouse.md) | ClickHouse: user passwords, secure ports, network restrictions, SQL-driven RBAC with table-scoped roles, query/memory limits and quotas, external-source restrictions, and protected query/session logs |
| [neo4j.md](neo4j.md) | Neo4j: initial password, Bolt and HTTPS TLS, auth stays on, scoped Enterprise roles with label/property grants, procedure/function/load denials, transaction memory and timeout limits, and security-event logging |
| [memcached.md](memcached.md) | Memcached: no auth by default; private binding and UDP off, dedicated unprivileged account, connection and item-memory limits, disabled cache-wide flush and key enumeration, SASL and TLS where built in |
| [search-engines.md](search-engines.md) | Meilisearch and Typesense, master key, scoped search keys, production mode |
| [minio.md](minio.md) | MinIO (AIStor): root and scoped credentials, TLS, server-side encryption, object locking, and audit logging |
| [object-storage.md](object-storage.md) | S3, R2, GCS, Azure Blob, Supabase Storage: private by default, scoped credentials, signed URLs |
| [firebase-supabase.md](firebase-supabase.md) | Firebase rules and Supabase RLS: ownership rules across Firestore/RTDB/Storage, Data-API and key hygiene, function/Storage/Realtime authorization, App Check, and signup controls |
| [supabase-self-hosted.md](supabase-self-hosted.md) | The self-hosted Docker stack: replace the demo keys and dashboard password, keep the published ports private |
| [pocketbase.md](pocketbase.md) | PocketBase and Appwrite: API and collection rules are the security, plus auth-record and file-field protection, operator and console lockdown, settings encryption, rate limits, and hostname and upload controls |
| [headless-cms-instant-api.md](headless-cms-instant-api.md) | Strapi, Directus, Hasura, and PostgREST: one control gates the whole datastore |
| [rabbitmq.md](rabbitmq.md) | RabbitMQ: users and permissions, TLS listener, guest account, vhost isolation and resource limits, management HTTPS, monitoring/admin role separation, concrete private bindings, and safe definitions import |
| [mosquitto.md](mosquitto.md) | Mosquitto (MQTT): per-device credentials, TLS listener, mutual TLS, topic ACLs with `$SYS` isolation, connection/packet/queue limits, per-listener scoping, bridge security, and runtime hardening |
| [kafka.md](kafka.md) | Apache Kafka: SASL_SSL listeners, SCRAM credentials, ACLs, client/replication/controller listener separation, per-role least-privilege ACLs, user quotas and connection limits, and authorization audit logging |
| [nats.md](nats.md) | NATS and JetStream, auth, TLS, and the unauthenticated monitoring port |

### AI and agent infrastructure

| Guide | Covers |
|---|---|
| [ollama.md](ollama.md) | Ollama: no built-in auth or TLS; protect it with a proxy or tunnel |
| [model-servers.md](model-servers.md) | llama.cpp, vLLM, TGI, SGLang, Triton, LM Studio: loopback, API keys, TLS in front |
| [litellm.md](litellm.md) | LiteLLM proxy: master key, per-app virtual keys, per-key spend and rate limits, model-access allowlists, key expiry and revocation, admin/route separation, egress and pass-through limits, and request-content log redaction |
| [vector-databases.md](vector-databases.md) | Qdrant, Weaviate, Milvus, Chroma, pgvector: API keys, TLS, what has no native auth |
| [mcp-servers.md](mcp-servers.md) | MCP servers: stdio versus Streamable HTTP, loopback, Origin checks, OAuth 2.1 or a fronting layer |
| [mcp-clients.md](mcp-clients.md) | MCP clients: authorization-response iss validation, metadata issuer identity, Client ID Metadata Documents and application_type, refresh-token confidentiality, OAuth-discovery SSRF |
| [ray.md](ray.md) | Ray: dashboard, Jobs, and Client ports execute code; isolate, token auth, SSH forward |
| [mlflow.md](mlflow.md) | MLflow tracking server: no auth by default; basic-auth app, TLS in front |
| [llm-observability.md](llm-observability.md) | Langfuse, Phoenix, Helicone, OpenTelemetry Collector: they hold prompts and keys |
| [agent-builders.md](agent-builders.md) | Dify, Flowise, Langflow, LibreChat: admin setup, API keys, fronting TLS |
| [ai-infra-services.md](ai-infra-services.md) | SearxNG, LocalAI, Text Embeddings Inference, LangServe, Mem0, Onyx: what the run form publishes, and the store published beside the front door |
| [workflow-orchestrators.md](workflow-orchestrators.md) | Prefect, Dagster, Airflow, Temporal, Flower, Argo: keep off the public internet and require auth |
| [headless-browser-services.md](headless-browser-services.md) | Chrome DevTools Protocol, Selenium Grid, browserless, Playwright: an exposed browser port is remote code execution |
| [realtime-voice-infra.md](realtime-voice-infra.md) | LiveKit and coturn: WebRTC SFU signing keys and the TURN open-relay default, RFC 1918 relay policy, TLS |

### App UIs and dev tools

| Guide | Covers |
|---|---|
| [open-webui.md](open-webui.md) | Open WebUI: signup control, pending role, fronting TLS, persistent signing key, trusted-proxy and OAuth boundaries, tool and code-execution limits, model and admin-data access control, API-key restrictions, and retrieval/SSRF limits |
| [chat-uis.md](chat-uis.md) | AnythingLLM, LobeChat, Chainlit, OpenHands: open by default; front with login |
| [image-gen-uis.md](image-gen-uis.md) | ComfyUI, A1111, InvokeAI, Fooocus: keep on loopback and add a login before exposing |
| [gradio.md](gradio.md) | Gradio: launch() auth and TLS, share-link risks, file-access and cache isolation, optional-execution-surface and API-visibility controls, queue and resource limits, URL-fetch SSRF limits, external auth, and flagging/telemetry controls |
| [streamlit.md](streamlit.md) | Streamlit: TLS options, native OIDC login, reverse proxy deployment |
| [jupyter.md](jupyter.md) | Jupyter Server, Lab, and Notebook: hashed password and TLS, unprivileged execution, origin/XSRF/DNS-rebinding protection, JupyterHub identities and per-user isolation, and auth by default |
| [n8n.md](n8n.md) | n8n: listen address, native TLS, owner setup, MFA enforcement |
| [code-server.md](code-server.md) | code-server: SSH forwarding first, password auth, TLS |
| [self-hosted-error-trackers.md](self-hosted-error-trackers.md) | Sentry and GlitchTip: registration defaults, event-data leakage, reverse-proxy TLS |

### Dashboards and admin consoles

| Guide | Covers |
|---|---|
| [admin-uis.md](admin-uis.md) | phpMyAdmin, pgAdmin, mongo-express, Grafana, Prometheus: never public |
| [observability-components.md](observability-components.md) | node_exporter, Alertmanager, Pushgateway, Jaeger, Loki: unauthenticated by default; never public |
| [devops-uis.md](devops-uis.md) | Portainer, Coolify, Dokploy, Nginx Proxy Manager, Vaultwarden, Kubernetes Dashboard, Jenkins, Gitea, Uptime Kuma, Docker API: never public |
| [bi-dashboards.md](bi-dashboards.md) | Metabase, Superset, Redash: never public; least-privilege database user |
| [low-code-builders.md](low-code-builders.md) | NocoDB, Baserow, Appsmith, Budibase, Windmill: first-run admin, open signup, sample secrets |
| [server-admin-panels.md](server-admin-panels.md) | Cockpit, Webmin, Proxmox VE: root-level host panels on every address, no default second factor |
| [nomad-consul.md](nomad-consul.md) | Nomad, Consul: APIs with ACLs off by default, anonymous bootstrap, Consul's allow default |

### Web application controls

| Guide | Covers |
|---|---|
| [cors.md](cors.md) | CORS: exact origins, never * with credentials |
| [headers.md](headers.md) | Security headers: HSTS, CSP, and companions for your app |
| [realtime-webhooks.md](realtime-webhooks.md) | WebSocket, SSE, and webhook authentication |
| [transactional-email-posture.md](transactional-email-posture.md) | SPF, DKIM, DMARC, SMTP submission, and open-relay posture for the mail a deployment sends |

### Exposure and deployment operations

| Guide | Covers |
|---|---|
| [web-exposure.md](web-exposure.md) | Files a web server must never serve: dotfiles, .git, dumps, client secrets |
| [egress-metadata.md](egress-metadata.md) | Egress control and cloud metadata (IMDSv2), stop an agent exfiltrating credentials |
| [deployment-lifecycle.md](deployment-lifecycle.md) | Verify from outside, safe first-run order, previews, and teardown |
| [exposure-index.md](exposure-index.md) | Narrow an open port to the guides worth reading, then identify the process |
| [common-mistakes.md](common-mistakes.md) | The recurring findings, each linked to its fix |

## Verification checklist

Run the applicable checks below and the Verify steps in every selected guide. Replace `REPLACE_WITH_YOUR_HOST` in every command below with your own host before running anything. The placeholder is deliberate: an earlier version used `example.com`, which resolves and serves HTTPS, so check 3 succeeded for every reader whatever state their deployment was in. The commands use `-sS` so that an unreplaced placeholder prints `curl: (6) Could not resolve host` rather than failing silently. That is a visible failure, not a guarantee: a resolver that answers every name, or a proxy in your environment, can still put a real destination behind the placeholder, so substitute it rather than relying on the error. Record each result as pass, fail, untested, or not applicable, with evidence or a reason; report a control as verified only for the checks that passed.

1. REASONED: public HTTP listener check; local marking review (October 2026, Bash 5.3.9) ran `bash -n` and ShellCheck 0.11.0 on the checklist command samples with exit 0 and no output, and a stubbed `ss -tlnp` printed `stub ss args: -tlnp` (exit 0). A live HTTP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Per README.sources.md entry 1 (ss(8); host.md; common-mistakes.md), an exposed public plain HTTP listener appears in `ss`; in the fixed state `ss` still lists the service's known TLS port, while no public plaintext listener appears except a redirect-only listener. The working controls are an HTTPS answer under item 3 and, where HTTP is offered, the redirect status and HTTPS Location under item 2; `ss` alone cannot establish either behaviour. No exposed or fixed deployment was observed. No plaintext listener on a public interface: `ss -tlnp` (Linux) shows nothing bound to `0.0.0.0` or a public address on a plain HTTP port, except a listener whose only job is to redirect to HTTPS.
2. REASONED: HTTP redirect check; local marking review (October 2026, Bash 5.3.9) ran `bash -n` and ShellCheck 0.11.0 with exit 0 and no output; a curl stub printed the `-sS -o /dev/null -w` arguments and `http://REPLACE_WITH_YOUR_HOST/` (exit 0). A live HTTP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Per README.sources.md entry 2 (RFC 9110, HTTP Semantics; curl manual), the exposed HTTP route serves without an HTTPS redirect; the fixed route returns a redirect status and HTTPS Location. No live response was observed. Where HTTP is offered, the redirect works: `curl -sS -o /dev/null -w '%{http_code} %{redirect_url}\n' http://REPLACE_WITH_YOUR_HOST/` returns `301` or `308` (the preferred permanent redirects), or `302`/`307` where a framework issues them, always with a `Location: https://...` header.
3. REASONED: HTTPS certificate check; local marking review (October 2026, Bash 5.3.9) ran `bash -n` and ShellCheck 0.11.0 with exit 0 and no output; a curl stub printed the `-sS -o /dev/null -w` arguments and `https://REPLACE_WITH_YOUR_HOST/` (exit 0). A live HTTPS deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Per README.sources.md entry 3 (curl manual), an exposed invalid certificate makes verified curl fail, while a fixed trusted certificate lets curl succeed without `-k`. No certificate was tested. TLS works: `curl -sS -o /dev/null -w '%{http_code}\n' https://REPLACE_WITH_YOUR_HOST/` succeeds without `-k`.
4. REASONED: TLS 1.1 refusal check; local marking review (October 2026, Bash 5.3.9, OpenSSL 3.5.5) ran `bash -n` and ShellCheck 0.11.0 with exit 0 and no output; a stub printed `stub openssl args: s_client -connect REPLACE_WITH_YOUR_HOST:443 -tls1_1` (exit 0), while local `openssl ciphers -s -tls1_1` exited 0 with only a newline, so that client cannot distinguish server refusal here. A live TLS deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. A client or scanner capable of offering TLS 1.1 and a live TLS 1.2 service control were also unavailable to this review. Per README.sources.md entry 4 (openssl-s_client; RFC 8996, Deprecating TLS 1.0 and TLS 1.1; OpenSSL config), an exposed TLS 1.1 server negotiates when a capable client offers it; a fixed server refuses that offer while a TLS 1.2 control succeeds. Neither state was observed. Old protocols are refused: `openssl s_client -connect REPLACE_WITH_YOUR_HOST:443 -tls1_1` fails to negotiate (TLS 1.2 is the minimum everywhere in these guides). Confirm the refusal came from the server and not from your own client: a local OpenSSL build, or a `MinProtocol` setting in its configuration, can refuse TLS 1.1 before any offer is sent, which looks identical. Check that your client can still offer TLS 1.1 at all, or use an external scanner that does.
5. Authentication is enforced: an unauthenticated request to any non-public path returns `401`, `403`, or a login redirect, never data. Test the API paths as well as the home page.
6. No default credentials remain, and no secret (password, key, token, certificate private key) is committed to the repository. Scan before pushing, for example with gitleaks.
7. Where ACME is used, renewal is automated: `sudo certbot renew --dry-run` passes AND something is actually scheduled to run it. The dry run proves the command works, not that it will ever be invoked, so check the scheduler too: `systemctl list-timers` shows an active certbot timer with a next run, or the packaged cron entry is present. Servers that manage renewal themselves (Caddy, Traefik) need no timer; confirm a completed renewal in their logs instead.
8. For public endpoints: scanned with the [Qualys SSL Labs test](https://www.ssllabs.com/ssltest/) or [testssl.sh](https://github.com/testssl/testssl.sh).
9. Human-facing logins carry a second factor where the stack supports one; [mfa.md](mfa.md) lists the options, and the per-tool guides state what is viable.
10. Probe from outside the deployment network, from a second host: cloud-firewall and Docker-publishing mistakes only show from outside. Shodan or Censys can corroborate, but they report what a scanner last observed rather than what is listening now, so a port published since their last pass will not appear; treat them as a second opinion, never as a substitute for a live probe. See [deployment-lifecycle.md](deployment-lifecycle.md).
11. Where login comes from an identity provider, an authenticated identity outside the allowed tenant, domain, group, or users is denied; test with such an account, not only an anonymous request.

Sources for these checks are listed in [README.sources.md](README.sources.md), numbered to match the items above.

## Scope and currency

The guides use placeholders that you must replace. `example.com` and `app.example.com` stand in for a name, and `203.0.113.10` for an address, wherever the value is configuration or illustration. That is usually a wrong value that fails visibly, though not always: an unreplaced certificate SAN generates a perfectly valid certificate for the wrong address. Where leaving the placeholder in place would instead look like a passing check, the guides use a `REPLACE_WITH_A_NAME` form and the check itself rejects the unsubstituted value rather than trusting it to fail. The verification checklist above uses that second form for exactly that reason. Configuration syntax was checked against the vendor documentation cited in each guide as of September 2026; directives and dashboard menu locations change, so verify version-specific items against the current documentation for your installed version. Each guide lists its sources.

Scope: deployment exposure, including TLS, human and machine authentication, MFA, access restrictions, secrets, and inbound and outbound network access, from first deployment through teardown. General application security, including injection, deserialization, and business logic flaws, belongs to the OWASP resources linked throughout the guides. LLM-specific application risks such as prompt injection are covered by the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/). To propose a tool or guide, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Everything in this repository (the guides, the configuration samples, and the site) is dedicated to the public domain under [CC0 1.0 Universal](LICENSE). Copy and reuse it freely; no attribution is required. The one exception is the AIQT Guardrails material that [`.aiqt/PIN`](https://github.com/jposluns/secureconfig/blob/main/.aiqt/PIN) lists (the files vendored under `.aiqt/` and `tools/`, and the AIQT sections adapted into `CLAUDE.md` and `AGENTS.md`), which is licensed under the Apache License 2.0 (see [`.aiqt/LICENSE`](https://github.com/jposluns/secureconfig/blob/main/.aiqt/LICENSE) and [`.aiqt/NOTICE`](https://github.com/jposluns/secureconfig/blob/main/.aiqt/NOTICE)).
