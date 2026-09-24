# Exposure index: ports this corpus documents, and where to look them up

You ran a scan and something is listening. This page narrows the search.

A port number does not identify a service. IANA says so about its own registry: traffic on a registered
port need not belong to the service assigned to it, and many of the numbers below are registered to
something other than the service you will find there. Use the owning process from `ss`, not the number, to decide what you
are looking at; the number only tells you which guides are worth opening.

A port missing from this table is not a port nobody has reviewed. It is a port this page does not list.
Identify the process, then search the corpus by service name.

## How to use this

1. `sudo ss -tlnp` to get the listening sockets **and the process that owns each one**. Without `sudo`
   you get the ports but not the process names for sockets owned by other users, which is most of them.
2. Find the port below and open the guides named. More than one may apply.
3. Run **that guide's** Verify section. This page's Verify does not replace it, and cannot: a port being
   bound privately says nothing about whether the service behind it authenticates anyone.

## What binds what, according to this corpus

Rows say what *may* be listening. Where a guide documents a published container mapping rather than the
application's own listener, the row says so, because `-p 3000:8080` means two different ports and only
one of them is the application's.

Rows are ordered by their first port number or the start of a range. Related ports may share a row, and ranges can overlap other entries.

The Default credential column records what the cited guides say a fresh install ships with: a
well-known account, an empty or placeholder password, no authentication at all, a secure default
such as a generated token, or another posture the guide states, such as a shared secret or a listener
that sits outside the login. It reports the guides, not the vendors. "not stated" means the cited guides are silent, which is not the same as
safe, and "varies by service; see the guides" means the row covers services whose defaults differ.
Open the guide before relying on either, because defaults change between releases.

| Port | May be | Default credential | Documented in |
| --- | --- | --- | --- |
| 22 | SSH, which should not be publicly reachable | not stated | [cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md) |
| 25 | SMTP relay or MX; the exposure to index is an open relay, not the port itself | not stated | [transactional-email-posture.md](transactional-email-posture.md) |
| 53 | Cluster DNS, in the Kubernetes NetworkPolicy egress rules, over both UDP and TCP | not stated | [container-hardening.md](container-hardening.md) |
| 80, 443 | Usually the TLS proxy, but also native HTTPS listeners in the language guides, and Vaultwarden's container port 80 | varies by service; see the guides | [nginx.md](nginx.md), [caddy.md](caddy.md), [haproxy.md](haproxy.md), [traefik.md](traefik.md), [apache.md](apache.md), [lighttpd.md](lighttpd.md), [go.md](go.md), [dotnet.md](dotnet.md), [devops-uis.md](devops-uis.md) |
| 81 | Nginx Proxy Manager admin UI (the proxy itself is on 80 and 443) | Default admin user created on first run; change it at first login | [devops-uis.md](devops-uis.md) |
| 465 | SMTP submission over implicit TLS; transport is encrypted from the first byte, authorization is still separate | not stated | [transactional-email-posture.md](transactional-email-posture.md) |
| 587 | SMTP submission with STARTTLS; opportunistic TLS can be stripped, exposing the credential | not stated | [transactional-email-posture.md](transactional-email-posture.md) |
| 1025, 8025 | Helicone Compose backing-service host publications; the guide names MailHog among the backing services but does not assign a protocol to each of these ports | Published independently of the dashboard login | [llm-observability.md](llm-observability.md) |
| 1234 | LM Studio local server | No authentication required by default | [model-servers.md](model-servers.md) |
| 1337 | Strapi HTTP server and admin panel; the first visitor to the admin panel becomes the administrator while no account exists yet | No default admin password; first admin-panel visitor becomes administrator | [headless-cms-instant-api.md](headless-cms-instant-api.md) |
| 1777 | OpenTelemetry Collector pprof diagnostic extension, when enabled | Collector ships with no security until configured | [llm-observability.md](llm-observability.md) |
| 1880 | Node-RED editor and admin API, which have no authentication by default | No authentication by default | [devops-uis.md](devops-uis.md) |
| 1883 | MQTT, plaintext | Mosquitto 2.0+: no-listener mode anonymous on loopback; explicit listener rejects unauthenticated | [mosquitto.md](mosquitto.md) |
| 2019 | Caddy admin API, which requires no credentials and defaults to localhost | No credentials required | [caddy.md](caddy.md) |
| 2375 | Docker API, plaintext and unauthenticated | Unauthenticated; anyone reaching the socket controls the host | [devops-uis.md](devops-uis.md) |
| 2376 | Docker API over TLS. The port is a convention, not proof of client-certificate authentication: `--tls` and `--tlsverify` are different settings | No client-certificate check without `--tlsverify` | [devops-uis.md](devops-uis.md), [docker.md](docker.md) |
| 2379, 2380 | etcd client and peer ports on a Kubernetes control-plane node. Every Secret in the cluster is here, unencrypted unless encryption at rest is configured | not stated | [kubernetes.md](kubernetes.md) |
| 2746 | Argo Server (Argo Workflows API and UI) | Client auth mode (caller's Kubernetes token) by default since v3.0 | [workflow-orchestrators.md](workflow-orchestrators.md) |
| 3000 | The most crowded port here: 23 guides in this corpus mention it, and the most likely owners are Metabase, Dagster, Gitea, Dokploy, Next.js, SvelteKit's Node adapter (which defaults to `0.0.0.0`), Rails, Flowise, OpenHands, Langfuse, TGI, and the backend behind most proxy examples. Open WebUI's 3000 is a **published host port** mapping to container 8080; and PostgREST, which binds all IPv4 interfaces here by default; and browserless, which is unauthenticated when its TOKEN is unset | varies by service; see the guides | [nextjs.md](nextjs.md), [frontend-frameworks.md](frontend-frameworks.md), [ruby.md](ruby.md), [bi-dashboards.md](bi-dashboards.md), [workflow-orchestrators.md](workflow-orchestrators.md), [devops-uis.md](devops-uis.md), [open-webui.md](open-webui.md), [llm-observability.md](llm-observability.md), [model-servers.md](model-servers.md), [agent-builders.md](agent-builders.md), [chat-uis.md](chat-uis.md), [mcp-servers.md](mcp-servers.md), [fronting-auth.md](fronting-auth.md), [headless-cms-instant-api.md](headless-cms-instant-api.md), [headless-browser-services.md](headless-browser-services.md) |
| 3001 | AnythingLLM, or Uptime Kuma | varies by service; see the guides | [chat-uis.md](chat-uis.md), [devops-uis.md](devops-uis.md) |
| 3080 | LibreChat | First registered account becomes admin | [agent-builders.md](agent-builders.md) |
| 3100 | Grafana Loki's HTTP API, on every interface by default; `auth_enabled` is tenancy, not authentication | No built-in authentication; any `X-Scope-OrgID` value is accepted | [observability-components.md](observability-components.md) |
| 3210 | LobeChat | Registration allowlist `AUTH_ALLOWED_EMAILS` empty by default: any email registers | [chat-uis.md](chat-uis.md) |
| 3306 | MySQL and MariaDB | Varies by install method; MariaDB 10.4+ local root via Unix socket | [mysql.md](mysql.md), [cloud-firewalls.md](cloud-firewalls.md) |
| 3389 | RDP, mentioned only as an omitted inventory check in the cloud-firewall guide | not stated | [cloud-firewalls.md](cloud-firewalls.md) |
| 3478 | coturn STUN/TURN over UDP and TCP | Stock example config: anonymous TURN allocation (Docker image ships `lt-cred-mech` on) | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 4000 | LiteLLM proxy | At the time of writing, refuses to start without a master key or with `sk-1234`; older or overridden deployments can run without authentication; UI user `admin`, and with `UI_PASSWORD` unset the master key logs in | [litellm.md](litellm.md) |
| 4180 | oauth2-proxy | not stated | [fronting-auth.md](fronting-auth.md) |
| 4200 | Prefect server | No default authentication | [workflow-orchestrators.md](workflow-orchestrators.md) |
| 4222 | NATS client connections | No authentication configured by default | [nats.md](nats.md) |
| 4317, 4318 | OTLP gRPC and OTLP HTTP receivers, including Jaeger v2's, on localhost in its all-in-one configuration | Collector ships with no security until configured; Jaeger: not stated | [llm-observability.md](llm-observability.md), [observability-components.md](observability-components.md) |
| 4369 | epmd, the Erlang Port Mapper Daemon, which maps Erlang node names to distribution ports (RabbitMQ and other Erlang or Elixir clustered services) | not stated | [rabbitmq.md](rabbitmq.md) |
| 4442, 4443 | Selenium Grid event bus in distributed mode, which Nodes use to register and which the Router's basic auth does not cover | Grid ships with no authentication; Router basic auth does not cover the bus | [headless-browser-services.md](headless-browser-services.md) |
| 4444 | Selenium Grid Router, Hub, or Standalone, plus the Grid web UI on the same port, with no authentication by default | No authentication by default; Router basic-auth credentials unset | [headless-browser-services.md](headless-browser-services.md) |
| 5000 | Redash, MLflow tracking server, or a .NET Kestrel default | varies by service; see the guides | [bi-dashboards.md](bi-dashboards.md), [mlflow.md](mlflow.md), [dotnet.md](dotnet.md) |
| 5001 | Dify backend API, in the guide's in-container request example | not stated for this port; Dify's `INIT_PASSWORD` is empty by default, so on a reachable host the first visitor to `/install` owns the instance | [agent-builders.md](agent-builders.md) |
| 5003 | Dify's plugin daemon debugging port, published by the supplied Compose configuration unless you remove or restrict that mapping | not stated | [agent-builders.md](agent-builders.md) |
| 5349 | coturn TLS listener; DTLS is opt-in since 4.17.0, and this port number does not prove encryption is mandatory | Stock example config: anonymous TURN allocation | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 5432 | PostgreSQL, and pgvector on the same port; the Supabase self-hosted Supavisor pooler also publishes it | varies by service; see the guides | [postgresql.md](postgresql.md), [vector-databases.md](vector-databases.md), [cloud-firewalls.md](cloud-firewalls.md), [supabase-self-hosted.md](supabase-self-hosted.md) |
| 5553, 5556, 5557, 5559 | Selenium Grid distributed components: Distributor, Session Map, event bus HTTP, and New Session Queue; these listeners are not protected by the Router's basic auth | Unauthenticated listeners; Grid ships with no authentication | [headless-browser-services.md](headless-browser-services.md) |
| 5555 | Flower, the Celery monitor, or a Selenium Grid Node | Flower: auth disabled unless configured; Selenium Node: Grid ships no auth | [workflow-orchestrators.md](workflow-orchestrators.md), [headless-browser-services.md](headless-browser-services.md) |
| 5601 | Kibana, which defaults to HTTP on `localhost:5601` with `server.ssl.enabled: false` (its Docker image changes the host default to `0.0.0.0`), and OpenSearch Dashboards, whose 3.8.0 sample configuration also uses localhost and port 5601 with server TLS disabled | not stated | [elasticsearch.md](elasticsearch.md) |
| 5671, 5672 | AMQP over TLS, and AMQP plaintext | `guest`/`guest`, usable only from localhost | [rabbitmq.md](rabbitmq.md) |
| 5678 | n8n | Owner account set up on first run; unclaimed instance open to first visitor | [n8n.md](n8n.md) |
| 5766 | coturn telnet CLI, disabled by default and bound to loopback when enabled | Off by default; loopback when enabled; authenticated by `cli-password`, separately from the web admin | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 5778, 5779 | Jaeger v2 remote sampling, HTTP and gRPC, on localhost in the all-in-one configuration | not stated | [observability-components.md](observability-components.md) |
| 5900, 7900 | VNC and noVNC in the Selenium Docker browser images, started by default with the vendor example password `secret` | VNC on by default; vendor example password `secret` | [headless-browser-services.md](headless-browser-services.md) |
| 5901 | VNC in a GPU desktop template example; an example port, not a platform-wide default | Template-dependent; may default to weak or empty password | [gpu-clouds.md](gpu-clouds.md) |
| 6001, 6002 | Coolify real-time updates and terminal | not stated | [devops-uis.md](devops-uis.md) |
| 6006 | Arize Phoenix | Auth disabled by default; when enabled, `admin@localhost`/`admin` | [llm-observability.md](llm-observability.md) |
| 6060 | A Go service's pprof and expvar diagnostics listener, bound to loopback in the guide's example | not stated | [go.md](go.md) |
| 6080 | noVNC web interface in a GPU desktop template example; an example port, not a platform-wide default | Template-dependent; may default to weak or empty password | [gpu-clouds.md](gpu-clouds.md) |
| 6222 | NATS cluster routes, a separate listener with its own authentication and TLS | not stated | [nats.md](nats.md) |
| 6333, 6334, 6335 | Qdrant REST, gRPC, and internal cluster gRPC | Not secure by default; 6335 is never protected by an API key through v1.17.x, and on v1.18.0 and later only with `service.enforce_internal_auth`, which is off by default | [vector-databases.md](vector-databases.md) |
| 6362 | Neo4j backup | not stated | [neo4j.md](neo4j.md) |
| 6379 | Redis, Valkey, or the Ray head node | varies by service; see the guides | [redis.md](redis.md), [ray.md](ray.md), [cloud-firewalls.md](cloud-firewalls.md) |
| 6432 | PgBouncer, whose client-side TLS is disabled by default | Default `auth_type` is `md5`; `pgbouncer` user passwordless over the Unix socket for a client running as the pooler's Unix UID | [connection-poolers.md](connection-poolers.md), [postgresql.md](postgresql.md) |
| 6443 | The Kubernetes API server on a self-managed cluster. Managed providers usually serve it on 443 instead, so its absence here proves nothing | not stated | [kubernetes.md](kubernetes.md) |
| 6543 | The Supabase self-hosted Supavisor transaction pooler, a direct database connection published beside 5432 | Shipped demo `POSTGRES_PASSWORD` | [supabase-self-hosted.md](supabase-self-hosted.md) |
| 6789 | Metrics port mentioned only in the realtime voice guide's Verify inventory; service attribution and default status are not established there | not stated | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 7000 | frp server | Empty token by default; empty-token client authenticates | [tunnels.md](tunnels.md) |
| 7222 | NATS gateways, a separate listener with its own authentication and TLS | not stated | [nats.md](nats.md) |
| 7233 | Temporal frontend gRPC | Default `noopAuthorizer` allows every request | [workflow-orchestrators.md](workflow-orchestrators.md) |
| 7422 | NATS accepted leafnode connections, a separate listener with its own authentication and TLS | not stated | [nats.md](nats.md) |
| 7473, 7474, 7687 | Neo4j HTTPS, HTTP, and Bolt | `neo4j`/`neo4j` initial credential, auth on (packaged Neo4j 5) | [neo4j.md](neo4j.md) |
| 7700 | Meilisearch HTTP API; the binary defaults to localhost, while the official Docker image binds all interfaces | Unauthenticated until a master key is set (dev mode) | [search-engines.md](search-engines.md) |
| 7800 | Keycloak clustered cache transport, carrying sessions and tokens; TLS is on by default for TCP stacks | not stated | [self-hosted-idp.md](self-hosted-idp.md) |
| 7860 | Gradio, Stable Diffusion WebUI, or Langflow | varies by service; see the guides | [gradio.md](gradio.md), [image-gen-uis.md](image-gen-uis.md), [agent-builders.md](agent-builders.md) |
| 7880 | LiveKit HTTP/WebSocket signaling and API, which need a TLS proxy | Refuses to start without keys; `--dev` injects `devkey`/`secret` when the key map is empty; the upstream `config-sample.yaml` ships example pairs `key1: secret1` and `key2: secret2` | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 7881 | LiveKit ICE media TCP mux, separate from signaling | not stated | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 7882/UDP | LiveKit development-mode media mux; outside development mode the documented default is the 50000 to 60000 media range | not stated | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 7946 | Grafana Loki memberlist gossip when memberlist is the ring store, on 0.0.0.0 by default, over TCP | not stated | [observability-components.md](observability-components.md) |
| 8000 | SurrealDB, Chroma, Triton HTTP, Coolify, Vaultwarden outside Docker, Portainer's Edge agent tunnel, the Supabase self-hosted API gateway (Kong) which fronts the whole stack, or GlitchTip's web, API, and open self-signup | varies by service; see the guides | [surrealdb.md](surrealdb.md), [vector-databases.md](vector-databases.md), [model-servers.md](model-servers.md), [devops-uis.md](devops-uis.md), [supabase-self-hosted.md](supabase-self-hosted.md), [self-hosted-error-trackers.md](self-hosted-error-trackers.md) |
| 8001, 8002 | Triton gRPC and Triton Prometheus metrics; and Datasette's CLI default HTTP listener on 8001, loopback by default (an overridden bind or a published container mapping is the exposure) | varies by service; see the guides | [model-servers.md](model-servers.md), [sqlite-http-frontends.md](sqlite-http-frontends.md) |
| 8055 | Directus HTTP API and admin app | Bootstrap admin via `ADMIN_EMAIL`/`ADMIN_PASSWORD` or browser onboarding; public access off | [headless-cms-instant-api.md](headless-cms-instant-api.md) |
| 8080 | llama.cpp, Weaviate HTTP, Airflow, code-server, Open WebUI's container port, Dify's nginx when mapped to `127.0.0.1:8080`, Spring Boot, Go, and the Vast.ai Jupyter deployment; Keycloak's HTTP port, which exists only when `--http-enabled=true`; and Hasura GraphQL Engine v2, which binds every interface by default; and Argo CD's argocd-server pod listener, fronted by its Service on 80 and 443; and sqlite-web's CLI default HTTP listener, loopback by default (an overridden bind or a published container mapping is the exposure) | varies by service; see the guides | [model-servers.md](model-servers.md), [vector-databases.md](vector-databases.md), [workflow-orchestrators.md](workflow-orchestrators.md), [code-server.md](code-server.md), [open-webui.md](open-webui.md), [agent-builders.md](agent-builders.md), [java.md](java.md), [go.md](go.md), [gpu-clouds.md](gpu-clouds.md), [self-hosted-idp.md](self-hosted-idp.md), [headless-cms-instant-api.md](headless-cms-instant-api.md), [gitops-controllers.md](gitops-controllers.md), [sqlite-http-frontends.md](sqlite-http-frontends.md) |
| 8081 | Hasura's bundled data-connector agent, published beside the engine by the vendor quickstart Compose | not stated | [headless-cms-instant-api.md](headless-cms-instant-api.md) |
| 8083 | Argo CD argocd-server metrics, separate from its API and UI listener | not stated | [gitops-controllers.md](gitops-controllers.md) |
| 8086 | InfluxDB HTTP API, UI, and write endpoint (2.x and 1.x); 1.x ships with `auth-enabled = false`, and an un-set-up 2.x instance can be seized through `/api/v2/setup` | 1.x: `auth-enabled = false`; 2.x: first `/api/v2/setup` caller takes over | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8088 | Apache Superset | Admin password created at first run; change it | [bi-dashboards.md](bi-dashboards.md) |
| 8090 | PocketBase `serve`, which binds `127.0.0.1:8090` when no domain is given | Installer URL with superuser token printed in startup log | [pocketbase.md](pocketbase.md) |
| 8093 | The GitLab Runner interactive session server, its documented example listen address, which exists only when `[session_server]` is configured | not stated | [self-hosted-ci-runners.md](self-hosted-ci-runners.md) |
| 8107 | Typesense peering service, which should be restricted to cluster members | not stated | [search-engines.md](search-engines.md) |
| 8108 | Typesense API, which binds all interfaces by default | Operator bootstrap key required at startup; no keyless mode | [search-engines.md](search-engines.md) |
| 8123 | ClickHouse HTTP, plaintext | Base config: `default` user with an empty password, allowed to connect from any address; packaging can change it | [clickhouse.md](clickhouse.md) |
| 8188 | ComfyUI | No built-in login | [image-gen-uis.md](image-gen-uis.md) |
| 8200 | HashiCorp Vault API, and its UI at `/ui` on the same listener when `ui = true`; TLS is assumed by default, and `sys/health` and `sys/seal-status` answer unauthenticated | Initial root token: unlimited, no expiry; health/seal-status unauthenticated | [vault.md](vault.md) |
| 8201 | HashiCorp Vault cluster port, for server-to-server request forwarding and Raft over mutually authenticated TLS; a peer surface, never a client endpoint | not stated | [vault.md](vault.md) |
| 8222 | NATS monitoring endpoints | No login of its own | [nats.md](nats.md) |
| 8233 | Temporal Web UI as started by `temporal server start-dev`, which is the context this corpus documents | not stated | [workflow-orchestrators.md](workflow-orchestrators.md) |
| 8265 | Ray dashboard | No login unless token auth enabled (off by default) | [ray.md](ray.md) |
| 8400, 8401 | VictoriaMetrics cluster native RPC channels, separate from vmstorage's HTTP maintenance and metrics listener | No authentication by default | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8404 | HAProxy HTTPS stats listener in the configured example; a chosen port, and stats are disabled unless configured | Stats disabled unless configured; enabling authenticates nothing on its own | [haproxy.md](haproxy.md) |
| 8428 | VictoriaMetrics single-node HTTP API, UI, and ingest, with `-httpAuth.username`/`-httpAuth.password` Basic auth disabled by default | Basic auth disabled by default | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8432 | Mem0 Compose PostgreSQL publication: host port 8432 maps to container port 5432 | not stated | [ai-infra-services.md](ai-infra-services.md) |
| 8443 | ClickHouse HTTPS, the Kubernetes Dashboard forwarding example, and the configured HTTPS listeners in the Gradio, Python, Java and Ruby guides; Keycloak's HTTPS port | varies by service; see the guides | [clickhouse.md](clickhouse.md), [devops-uis.md](devops-uis.md), [gradio.md](gradio.md), [python.md](python.md), [java.md](java.md), [ruby.md](ruby.md), [self-hosted-idp.md](self-hosted-idp.md) |
| 8480 | VictoriaMetrics cluster `vminsert` HTTP ingestion, Basic auth disabled by default | Basic auth disabled by default | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8481 | VictoriaMetrics cluster `vmselect` HTTP query and UI, Basic auth disabled by default | Basic auth disabled by default | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8482 | VictoriaMetrics cluster `vmstorage` HTTP maintenance and metrics (native RPC on 8400 and 8401) | Basic auth disabled by default | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8501 | Streamlit | No access control unless you add it | [streamlit.md](streamlit.md) |
| 8812 | QuestDB PostgreSQL wire protocol, shipping the default credential `admin` / `quest` | `admin` / `quest` | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 8883 | MQTT over TLS | Mosquitto 2.0+: explicit listener rejects unauthenticated clients | [mosquitto.md](mosquitto.md) |
| 8888 | Jupyter, including RunPod deployments. The Vast.ai Jupyter launch mode uses 8080 instead; also Jaeger v2's self-metrics, on localhost in its all-in-one configuration | Jupyter: auth on by default via generated token; Jaeger: not stated | [jupyter.md](jupyter.md), [gpu-clouds.md](gpu-clouds.md), [observability-components.md](observability-components.md) |
| 9000 | ClickHouse native TCP (plaintext), MinIO's S3 API, PHP-FPM, TGI's Prometheus listener, or Portainer's legacy HTTP port; Keycloak's management port serving `/health` and `/metrics`, authentik's HTTP port, QuestDB's web console, REST, and SQL endpoints whose Basic-auth keys are unset by default, or the Sentry self-hosted web and API, published here by the bundled nginx | varies by service; see the guides | [clickhouse.md](clickhouse.md), [minio.md](minio.md), [php.md](php.md), [model-servers.md](model-servers.md), [devops-uis.md](devops-uis.md), [self-hosted-idp.md](self-hosted-idp.md), [time-series-metrics-stores.md](time-series-metrics-stores.md), [self-hosted-error-trackers.md](self-hosted-error-trackers.md) |
| 9001 | MinIO's web console (the `--console-address` / `MINIO_CONSOLE_ADDRESS` port, conventionally 9001) | `minioadmin`/`minioadmin` when root variables unset | [minio.md](minio.md) |
| 9003 | QuestDB minimal HTTP health and metrics server, which follows the HTTP authentication policy you set (unauthenticated when `http.user` is unset) | Unauthenticated while `http.user` is unset | [time-series-metrics-stores.md](time-series-metrics-stores.md) |
| 9004, 9005, 9010 | ClickHouse MySQL compatibility, PostgreSQL compatibility, and interserver replica traffic over HTTPS (the HTTP interserver port 9009 is listed separately) | SQL (9004, 9005): base config `default` user with an empty password, allowed to connect from any address; replication (9010): unauthenticated unless `interserver_http_credentials` is set, and independent of SQL users; packaging can change these | [clickhouse.md](clickhouse.md) |
| 9009 | QuestDB InfluxDB line protocol (TCP), which accepts unauthenticated writes unless `line.tcp.auth.db.path` is set; also ClickHouse interserver replica traffic over HTTP | varies by service; see the guides | [time-series-metrics-stores.md](time-series-metrics-stores.md), [clickhouse.md](clickhouse.md) |
| 9090 | InvokeAI, and the Prometheus server, which listens on `0.0.0.0:9090` by default with no authentication | No authentication by default (Prometheus; InvokeAI single-user mode) | [image-gen-uis.md](image-gen-uis.md), [admin-uis.md](admin-uis.md) |
| 9091 | Milvus WebUI, Authelia, or Prometheus Pushgateway, whose default `:9091` binds every interface | varies by service; see the guides | [vector-databases.md](vector-databases.md), [fronting-auth.md](fronting-auth.md), [observability-components.md](observability-components.md) |
| 9092, 9093 | Kafka plaintext and SASL_SSL listeners. Which port carries which is configured, not fixed. Alertmanager's UI and API also default to `:9093`, every interface | Kafka broker default PLAINTEXT on 9092: no credential, no authorizer; Alertmanager: no authentication by default | [kafka.md](kafka.md), [observability-components.md](observability-components.md) |
| 9094 | Kafka KRaft controller listener in the guide's configured SASL_SSL example; the port is chosen, not fixed; also Alertmanager HA gossip, on by default at `0.0.0.0:9094`, TCP and UDP | Kafka: not stated; Alertmanager gossip: plaintext unless `--cluster.tls-config` | [kafka.md](kafka.md), [observability-components.md](observability-components.md) |
| 9095 | Kafka's `INTERNAL` listener in the guide's example configuration, on a private address; also Grafana Loki's gRPC server, on every interface by default | Kafka: not stated; Loki: no built-in authentication | [kafka.md](kafka.md), [observability-components.md](observability-components.md) |
| 9100 | Prometheus node_exporter, whose default `:9100` binds every interface | No authentication by default | [observability-components.md](observability-components.md) |
| 9200 to 9300 | Elasticsearch HTTP default range, binding the first free port; OpenSearch HTTP on 9200 | varies by service; see the guides | [elasticsearch.md](elasticsearch.md) |
| 9222 | Chrome or Chromium DevTools Protocol remote debugging, an endpoint with no authentication whose reachability is full browser takeover | No authentication of any kind | [headless-browser-services.md](headless-browser-services.md) |
| 9252 | The GitLab Runner Prometheus metrics endpoint, served with no built-in authorization, which exists only when a metrics `listen_address` is configured | No built-in authorization | [self-hosted-ci-runners.md](self-hosted-ci-runners.md) |
| 9292 | Puma standalone, whose default bind is all interfaces; and the Flux notification-controller webhook receiver, in-cluster behind the `webhook-receiver` Service | varies by service; see the guides | [ruby.md](ruby.md), [gitops-controllers.md](gitops-controllers.md) |
| 9300 to 9400 | Elasticsearch transport default range; authentik's unauthenticated Prometheus metrics on 9300 | varies by service; see the guides | [elasticsearch.md](elasticsearch.md), [self-hosted-idp.md](self-hosted-idp.md) |
| 9411 | Jaeger v2 Zipkin receiver, on localhost in the all-in-one configuration | not stated | [observability-components.md](observability-components.md) |
| 9440 | ClickHouse native TCP over TLS | Base config: `default` user with an empty password, allowed to connect from any address; packaging can change it | [clickhouse.md](clickhouse.md) |
| 9443 | Portainer HTTPS UI, authentik's HTTPS port | varies by service; see the guides | [devops-uis.md](devops-uis.md), [self-hosted-idp.md](self-hosted-idp.md) |
| 9641 | coturn Prometheus metrics, disabled by default; when enabled, it binds a wildcard address and serves without authentication | Off by default; when enabled, no authentication | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 9898 | Pgpool-II's PCP administration channel, which has its own credential file | Its own credential file, `pcp.conf`, separate from database credentials | [connection-poolers.md](connection-poolers.md) |
| 9999 | Pgpool-II | `enable_pool_hba` off by default: Pgpool authenticates nobody itself | [connection-poolers.md](connection-poolers.md), [postgresql.md](postgresql.md) |
| 10001 | Ray Client server, which executes code | Unauthenticated code execution unless token auth enabled (off by default) | [ray.md](ray.md) |
| 10002 to 19999 | Ray worker ports, allocated across this whole range by default, plus several randomized ports. Anything in this range on a Ray node may be a worker rather than the service the row below suggests | Ray token authentication (2.52.0 and later) is disabled by default as of 2.58.0 | [ray.md](ray.md) |
| 10250 | The Kubernetes kubelet API, which runs commands in containers. It also falls inside the Ray worker range above | Flag-configured: anonymous auth on; file-configured (kubeadm, managed): off | [kubernetes.md](kubernetes.md) |
| 10255 | The Kubernetes kubelet read-only port, which serves with no authentication or authorization | No authentication or authorization; on by flag default, off by file default | [kubernetes.md](kubernetes.md) |
| 10256 | Kubernetes kube-proxy health, on worker nodes | not stated | [kubernetes.md](kubernetes.md) |
| 10257, 10259 | The Kubernetes controller manager and scheduler, on control-plane nodes | not stated | [kubernetes.md](kubernetes.md) |
| 11211 | Memcached. Check UDP as well as TCP | No authentication by default | [memcached.md](memcached.md) |
| 11434 | Ollama | No native inbound authentication | [ollama.md](ollama.md) |
| 11435 | The Ollama guide's local policy proxy, an nginx listener on `127.0.0.1:11435` for the inference-only deployment | not stated | [ollama.md](ollama.md) |
| 13133 | OpenTelemetry Collector health-check extension, when enabled; also Jaeger v2's health check, on localhost in its all-in-one configuration | Collector ships with no security until configured; Jaeger: not stated | [llm-observability.md](llm-observability.md), [observability-components.md](observability-components.md) |
| 14250, 14268 | Jaeger v2 gRPC and Thrift HTTP receivers, on localhost in the all-in-one configuration | not stated | [observability-components.md](observability-components.md) |
| 15671 | RabbitMQ management UI over TLS, as noted in the guide's listener inventory | `guest`/`guest`, usable only from localhost | [rabbitmq.md](rabbitmq.md) |
| 15672 | RabbitMQ management UI | `guest`/`guest`, usable only from localhost | [rabbitmq.md](rabbitmq.md) |
| 16379 | Redis Cluster's node-to-node bus (`cluster-port 16379` in the guide's example), which is opt-in and needs its own restriction | No AUTH gate; data-port password does not apply | [redis.md](redis.md) |
| 16685, 16686 | Jaeger v2 query gRPC and the UI and query API (with MCP at `/api/ai/mcp/` in the all-in-one configuration), on every interface by default | No authentication by default | [observability-components.md](observability-components.md) |
| 18123 | Helicone Compose ClickHouse HTTP publication: host port 18123 maps to container port 8123; it also falls inside the Ray worker range | Published independently of the dashboard login; the guide says to rotate the Compose example storage credentials | [llm-observability.md](llm-observability.md) |
| 19000 | Helicone Compose backing-service publication: host port 19000 maps to container port 9000, but the guide does not explicitly attribute this mapping to a service; it also falls inside the Ray worker range | Published independently of the dashboard login | [llm-observability.md](llm-observability.md) |
| 19530 | Milvus gRPC | Authentication must be enabled with `common.security.authorizationEnabled`; once on, built-in `root`/`Milvus` | [vector-databases.md](vector-databases.md) |
| 20202 | LiteFS HTTP replication API, including database export/import and administrative operations | not stated | [sqlite.md](sqlite.md) |
| 25672 | RabbitMQ inter-node and CLI Erlang distribution (default, the AMQP port plus 20000); by default the Erlang cookie is its only credential and grants full control of the node | The Erlang cookie, a shared secret; cookie plus reachability can give full broker control | [rabbitmq.md](rabbitmq.md) |
| 26379 | Redis Sentinel's separate listener; its shipped configuration disables protected mode and supplies no active authentication rule | Shipped config: protected mode off, no active authentication rule | [redis.md](redis.md) |
| 27017 | MongoDB | Authorization must be enabled (`authorization: enabled`); on an installation with no existing users or roles, the localhost exception lets a local client create the first administrator | [mongodb.md](mongodb.md), [cloud-firewalls.md](cloud-firewalls.md) |
| 27777, 27778 | Jaeger v2 expvar and zpages, on localhost in the all-in-one configuration | not stated | [observability-components.md](observability-components.md) |
| 30000 to 32767 | Kubernetes NodePort range over TCP and UDP; SGLang on 30000 | varies by service; see the guides | [kubernetes.md](kubernetes.md), [model-servers.md](model-servers.md) |
| 33060 | MySQL X Protocol, a separate listener whose bind is not controlled by bind_address; MariaDB does not implement it | not stated | [mysql.md](mysql.md) |
| 35672 to 35682 | RabbitMQ remote CLI tools' own Erlang distribution-port range (default); the guide says to restrict the actual range to the necessary peers | The Erlang cookie, a shared secret granting node and CLI access | [rabbitmq.md](rabbitmq.md) |
| 49152 to 65535 | coturn relay endpoints, allocated on demand; this range overlaps the LiveKit media range and other entries | not stated | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 50000 to 60000/UDP | LiveKit media sockets outside development mode, allocated during active calls | not stated | [realtime-voice-infra.md](realtime-voice-infra.md) |
| 50051 | Weaviate gRPC | Anonymous access enabled by default | [vector-databases.md](vector-databases.md) |
| 51820/UDP | WireGuard, in the configured example here. The port is chosen, not assigned | No username or password; key pairs only | [tunnels.md](tunnels.md) |
| 54388 | Helicone Compose PostgreSQL publication: host port 54388 maps to container port 5432 | Published independently of the dashboard login; the guide says to rotate the Compose example storage credentials | [llm-observability.md](llm-observability.md) |
| 55679 | OpenTelemetry Collector zPages diagnostic extension, when enabled | Collector ships with no security until configured | [llm-observability.md](llm-observability.md) |
| 57800 | Keycloak clustered cache failure detection; TLS is on by default for TCP stacks | not stated | [self-hosted-idp.md](self-hosted-idp.md) |

## Verify

**This is a baseline inventory, not a security check, and not a proof of completeness.** It gives you a
list of the listeners and routes it discovered. It cannot establish that the list is complete: a
container on a bridge network publishes no host port and holds its sockets in another network
namespace, and a container on routed IPv6 accepts traffic on its own address whatever the host
publishes. Reconcile what you find here against your interface addresses, container addresses and
namespaces, and your routing and publishing configuration before believing the inventory is whole.

It establishes nothing at all about whether those services are safe to expose, and no checklist on an
index page can. That claim belongs to each service's own guide, and even there the Verify blocks are
worked examples over sampled URLs, not an enumeration of your application's sensitive routes.

```bash
sudo ss -tlnp                    # listening TCP sockets, with the owning process
sudo ss -tlunp                   # again including UDP, which Memcached and WireGuard answer on
sudo ss -aunp                    # all UDP sockets, including non-listening sockets
docker ps --format '{{.Names}}\t{{.Ports}}'   # published container ports, which the host view can miss
```

Repeat the [all-UDP-sockets check](https://man7.org/linux/man-pages/man8/ss.8.html) during active calls or
relay allocations, because media and relay sockets may be absent while idle.

`ss` reports sockets in its own network namespace, so a container's listeners are not all visible from
the host. A diagnostic such as `Cannot open netlink socket` means the command failed: empty output with
a zero exit status is not a pass.

From a second machine on a different network, against a host **you own or are authorized to test**.
Run these against every public address the host answers on, not just one; a host with several
interfaces or a NAT address beside an elastic address has several inbound paths. Substitute a literal
address, and check the target Nmap prints before you read the result: the
placeholder below is a hostname as far as Nmap is concerned, and if it resolves in your environment
Nmap will scan whatever it resolved to.

```bash
sudo nmap -Pn -p- REPLACE_WITH_A_LITERAL_IPV4_ADDRESS            # TCP over IPv4
sudo nmap -Pn -6 -p- REPLACE_WITH_A_LITERAL_IPV6_ADDRESS         # TCP over IPv6, which the line above never covers
sudo nmap -Pn -sU --top-ports 100 REPLACE_WITH_A_LITERAL_IPV4_ADDRESS      # UDP, preliminary only
sudo nmap -Pn -6 -sU --top-ports 100 REPLACE_WITH_A_LITERAL_IPV6_ADDRESS   # UDP over IPv6
```

UDP scanning needs privilege and returns `open|filtered` when it cannot distinguish the two, so a
clean-looking UDP result is weaker evidence than a clean TCP one. Treat the top-100 scan as a first
pass and probe the UDP ports your own inventory names.

Four things to establish, and none of them is "the service is secure":

1. **Every listening socket is attributed**, to a named owning process or to an identified kernel
   service or interface. Kernel WireGuard is the case that breaks process attribution: it owns its UDP
   socket in the kernel, so `ss -p` names no process and `sudo` does not create one. A port appearing
   in the table above is a hint about which guides to read, not an identification of what is running.
2. **Every socket's bind address is deliberate.** `127.0.0.1`, `::1`, a private address or a tailnet
   address, unless you can say why it is public.
3. **Every inbound route is inventoried, not just the ones a port scan finds.** A scan of your public
   address says nothing about an outbound tunnel. An application on loopback reached through
   [tunnels.md](tunnels.md), [cloudflare.md](cloudflare.md) or [tailscale.md](tailscale.md) is exposed
   at that hostname while your host shows no open inbound port at all. List every hostname, every
   literal address the host answers on including container addresses, every tunnel, proxy and alternate
   virtual host, and every URL path a proxy routes to a different backend. Each is its own route, and a
   scan by hostname does not cover a request made to a bare address.
4. **Each reachable service has been through its own guide**, by every route from condition 3, not only
   the ones the scan surfaced. Those guides are where the authentication and TLS checks live.

Then keep going: enumerate your own sensitive routes and request each one anonymously and as an
unauthorized user. A deployment can satisfy all four conditions above and still serve private data from
an endpoint no guide here knows the name of.

## Sources (checked September 2026)

- `ss` manual, including that it reports sockets within a network namespace:
  https://man7.org/linux/man-pages/man8/ss.8.html
- Nmap port specification, for `-p-` and `--top-ports`:
  https://nmap.org/book/man-port-specification.html
- Nmap host discovery, for `-Pn`: https://nmap.org/book/man-host-discovery.html
- Nmap target specification, for how a target string is resolved:
  https://nmap.org/book/man-target-specification.html
- Nmap scan techniques, for `-sU` and the `open|filtered` state:
  https://nmap.org/book/man-port-scanning-techniques.html
- Nmap miscellaneous options, for `-6`: https://nmap.org/book/man-misc-options.html
- Nmap legal issues, on scanning only hosts you are authorized to scan:
  https://nmap.org/book/legal-issues.html
- Docker `container ls`, for `--format` and the `.Names` and `.Ports` placeholders:
  https://docs.docker.com/reference/cli/docker/container/ls/
- Docker port publishing, for the `-p host:container` mapping this page distinguishes:
  https://docs.docker.com/engine/network/port-publishing/
- Docker daemon protection, for the difference between `--tls` and `--tlsverify` noted on port 2376:
  https://docs.docker.com/engine/security/protect-access/
- IANA Service Name and Transport Protocol Port Number Registry, including its statement that traffic on
  a port need not belong to the assigned service:
  https://www.iana.org/assignments/service-names-port-numbers
- RFC 6335, which defines the registry and the dynamic and private range 49152 to 65535:
  https://www.rfc-editor.org/rfc/rfc6335.html
- Defaults, configured examples, published host-port mappings, and ranges above are documented in the
  linked guides, which cite their vendor sources. Example ports and inventory-only mentions are not
  claims about application defaults; incomplete attribution is stated in the row.
