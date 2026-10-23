# Self-hosted observability components: node_exporter, Alertmanager, Pushgateway, Jaeger, and Loki

node_exporter, Alertmanager, Pushgateway, Jaeger and Loki are monitoring services that usually run beside Prometheus, handling host metrics, alerts, pushed metrics, traces and logs. This guide helps your AI assistant configure each securely, including private listeners, each component's TLS and authentication options switched on, and a login proxy for browsers.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/observability-components.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against node_exporter v1.12.1, Alertmanager v0.34.1, Pushgateway v1.11.3, Jaeger v2.21.0, Loki v3.7.8, Exporter toolkit v0.17.1, OpenTelemetry configtls v1.66.0, and OpenTelemetry basicauth extension v0.160.0, plus 1 more recorded basis; 3 further sources are pinned to a commit and 1 carries no recorded version. Metadata reviewed 2026-10-20; documentation checked September 2026. The guide records 98 claims: 14 demonstrated by a check that ran and 84 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

The Prometheus server has its own section in [admin-uis.md](admin-uis.md). This guide covers the pieces
that usually run next to it, and each of them is an unauthenticated HTTP service by default. node_exporter
hands out a map of the host and a Go profiler. Alertmanager lets anyone create silences, so a real
incident stays quiet. Pushgateway lets anyone write or delete series that Prometheus then trusts. Jaeger's
query port serves every trace, and in v2 an MCP server on the same port. Loki answers any client that
names a tenant. None of them has a login screen or MFA. The three Prometheus-family tools can require
TLS client certificates or bcrypt basic auth natively, Loki can require client certificates but has no
login of its own, and Jaeger can take an OpenTelemetry authenticator, but all of these controls are off
until you configure them. Keep every listener private
([docker.md](docker.md), [cloud-firewalls.md](cloud-firewalls.md), [tunnels.md](tunnels.md)), and front
anything a person reaches with a browser per [fronting-auth.md](fronting-auth.md),
[nginx.md](nginx.md) or [caddy.md](caddy.md). Versions checked: node_exporter v1.12.1, Alertmanager
v0.34.1, Pushgateway v1.11.3, Jaeger v2.21.0, and Loki v3.7.8.

## Prometheus exporters and the shared web configuration

node_exporter listens on port 9100, and its `--web.listen-address` default is `:9100`. An address with
no host part binds every interface. The exporter serves `/metrics` without authentication. The v1.12.1
binary imports Go's `net/http/pprof` and serves the default mux, so `/debug/pprof/` also answers. On a
loopback run, both paths returned `200` with no credentials. The metrics show mounts, interfaces,
kernel and hardware, and the profiler exposes the command line and heap data. The Prometheus security
model says exporters "generally only talk to one configured instance with a preset set of
commands/requests", so the concern is disclosure rather than control. It is still a free survey of the
host for anyone who reaches the port.

node_exporter, Alertmanager and Pushgateway share one fix. The exporter-toolkit web configuration file,
passed with `--web.config.file`, turns on TLS and bcrypt basic auth for every HTTP path the process
serves. The toolkit calls the format experimental. Keep the listener private as well, even with the
file in place.

```yaml
# web.yml, passed as --web.config.file=/etc/prometheus/web.yml
tls_server_config:
  cert_file: /etc/prometheus/tls/server.crt
  key_file: /etc/prometheus/tls/server.key
  # For client certificates instead of (or as well as) passwords:
  # client_auth_type: RequireAndVerifyClientCert
  # client_ca_file: /etc/prometheus/tls/clients-ca.crt
basic_auth_users:
  # bcrypt hash; the toolkit docs suggest: htpasswd -nBC 10 "" | tr -d ':\n'
  scrape: REPLACE_WITH_A_BCRYPT_HASH
```

With this file on the v1.12.1 loopback run, plain HTTP to the port got `400`. HTTPS without credentials
got `401` on both `/metrics` and `/debug/pprof/`, and HTTPS with the right credentials got `200`. The
toolkit says that `client_auth_type` values other than `RequireAndVerifyClientCert` are insecure. It
reads the file on every request, so a changed password or certificate applies without a restart. It
also advises that basic auth is "meant for simple use cases, with a few users", and points to client
certificates or a reverse proxy beyond that. Give Prometheus's scrape job the matching
credentials and CA certificate. Other exporters built on the exporter
toolkit take the same `--web.config.file` flag, but check each exporter's own `--help`, because not
every exporter uses the toolkit.

## Alertmanager

Alertmanager serves its UI and API on `:9093`, all interfaces. Its HA gossip listener is on by default,
at `--cluster.listen-address` default `0.0.0.0:9094`, and the README says gossip needs both TCP and UDP.
The security model is direct: "Any user with access to the Alertmanager HTTP endpoint has access to its
data. They can create and resolve alerts. They can create, modify and delete silences." It also warns
that Alertmanager serves `/api/v2` with `Access-Control-Allow-Origin: *`, which "grants API access to
any website visited by a browser capable of reaching the service".

On the v0.34.1 loopback run with no web configuration, each of these succeeded without credentials:
`GET /api/v2/status` returned `200`, `POST /api/v2/silences` created a silence and returned `200`, and
`POST /-/reload` returned `200`. `GET /debug/pprof/` also returned `200`. The status response carried
`Access-Control-Allow-Origin: *`. The management API documents `/-/reload` with no gating flag.

- **HTTP:** use the same `--web.config.file` as above. With it, the loopback runs returned `401` to an
  unauthenticated silence creation and to an unauthenticated or wrong-password status read, and `200` to
  an authenticated status read. Give Prometheus's Alertmanager client the matching credentials and CA, or
  alerts stop arriving. Alertmanager's own docs call its TLS and basic auth experimental.
- **Gossip:** a single instance does not need it, so set `--cluster.listen-address=` (empty) to stop
  Alertmanager listening for peers. On a loopback run with it empty, Alertmanager held no TCP or UDP
  socket on 9094. An HA pair needs the port reachable by its peers only. Its gossip is plaintext unless you pass
  `--cluster.tls-config` (experimental), a file with `tls_server_config` and `tls_client_config`
  sections, described in Alertmanager's HTTPS documentation.
- **Behind a proxy:** the security model's API Security section, which covers every Prometheus
  component, suggests blocking the mutating paths at a reverse proxy to prevent CSRF, and setting CORS
  headers there for the read-only ones. The README warns not to load-balance
  Prometheus-to-Alertmanager traffic. Point Prometheus at every Alertmanager instead.

## Pushgateway

Pushgateway listens on `:9091`. The security model states the exposure: "Any user with access to the
Pushgateway HTTP endpoint can create, modify and delete the metrics contained within. As the Pushgateway
is usually scraped with `honor_labels` enabled, this means anyone with access to the Pushgateway can
create any time series in Prometheus." That reaches your alerting and dashboards. A forged series can
hide an outage or trigger a false page.

On the v1.11.3 loopback run, an unauthenticated `POST /metrics/job/demo` returned `200` and the series
appeared on `/metrics`. An unauthenticated `DELETE` of the group returned `202`. `/debug/pprof/` is
registered outside every flag check in the source, and it answered `200`. The admin API (which includes
wipe) is off unless you pass `--web.enable-admin-api`, and `PUT /api/v1/admin/wipe` returned `404` by
default. Lifecycle shutdown is off unless you pass `--web.enable-lifecycle`. Leave both flags off.

The same `--web.config.file` protects Pushgateway. The README says the settings "affect all HTTP
endpoints", including `/metrics`, the push API, the admin API and the web UI. With the file in place,
an unauthenticated push returned `401` and an authenticated one returned `200`. Give pushing jobs their
own credentials, and scrape with credentials too.

## Jaeger (v2)

Jaeger v2 run with no `--config` uses its built-in all-in-one configuration, with in-memory storage. In
that configuration, the collector receivers take their host from `${env:JAEGER_LISTEN_HOST:-localhost}`.
That covers OTLP on 4317 and 4318, Jaeger gRPC and Thrift HTTP on 14250 and 14268, Jaeger Thrift over
UDP on 6831 and 6832, Zipkin on 9411, remote sampling on 5778 and 5779, health on 13133, expvar on
27777, zpages on 27778, and self-metrics on 8888 (the loopback run showed each of them, UDP included,
on 127.0.0.1). The docs explain that `JAEGER_LISTEN_HOST` is "useful when running Jaeger in a container
and it needs to be `0.0.0.0`", and the project's v2.21.0 Dockerfile sets `ENV JAEGER_LISTEN_HOST=0.0.0.0`,
so in the official image every one of these listens on every interface and a published port reaches it.

The query service is the exception. The all-in-one file does not set `jaeger_query` endpoints, and the
code default is `":" + port`. That makes the UI and query API `:16686` and query gRPC `:16685`, both on
every interface, whether or not `JAEGER_LISTEN_HOST` is set. The documentation's own example sets them to
`0.0.0.0:16686` and `0.0.0.0:16685`. The v2.21.0 all-in-one also enables MCP (`ai: mcp: {}`), which the
source says serves "Jaeger telemetry MCP server at <basePath>/api/ai/mcp/ on the query port". An exposed
query port therefore gives an AI client the same unauthenticated trace access.

On a v2.21.0 loopback run, every query surface answered without credentials: `GET /api/v3/services`
returned `200`, the UI at `/` returned `200`, and an MCP `initialize` POST to `/api/ai/mcp/` returned
`200`. The v1 `/api/services` returned `404`; the v2.21.0 release notes list "remove v1 http endpoints the ui
no longer calls". Probe the
v3 path, or a 404 will read as a pass. Traces carry URLs, SQL, headers and whatever else the
instrumentation recorded.

Bind the query endpoints explicitly and add an authenticator. Jaeger's security page lists TLS and mTLS
for query clients and points to proxies for user login. The v2.21.0 build includes the OpenTelemetry
`basicauth` extension, and the query `http` block is an OpenTelemetry HTTP server configuration, so it
takes an `auth.authenticator`:

```yaml
extensions:
  basicauth/server:
    htpasswd:
      file: /etc/jaeger/htpasswd   # htpasswd-format entries; bcrypt ones worked on the loopback run
  jaeger_query:
    http:
      endpoint: 10.0.0.5:16686     # a private address, not the ":16686" default
      tls:
        cert_file: /etc/jaeger/tls/server.crt
        key_file: /etc/jaeger/tls/server.key
      auth:
        authenticator: basicauth/server
    grpc:
      endpoint: 127.0.0.1:16685
    storage:
      traces: some_storage
service:
  extensions: [basicauth/server, jaeger_storage, jaeger_query]  # keep your other extensions
```

On the loopback run with `basicauth/server` on the query `http` server, `/api/v3/services`, the UI and
the MCP endpoint each returned `401` without credentials and `401` with a wrong password. Each returned
`200` with the right credentials. With the `tls` block added (the OpenTelemetry `cert_file` and
`key_file` settings), HTTPS without credentials got `401`, HTTPS with them `200`, and plain HTTP `400`;
leave `tls` out and the password crosses the network in cleartext. That wiring is inferred from the OpenTelemetry types. Jaeger's
documentation does not describe it, so re-test it after an upgrade. Keep the gRPC query port on
loopback unless a client needs it: its server configuration also has an `auth` setting, which was
not demonstrated here. Remove `mcp` from `ai` if nothing uses it. For per-user login, front the UI with an
authenticating proxy per [fronting-auth.md](fronting-auth.md). Collector receivers that must accept
spans from other hosts need their own authenticator, as described for the OpenTelemetry Collector in
[llm-observability.md](llm-observability.md).

## Grafana Loki

Loki's documentation leaves no doubt: "Grafana Loki does not come with any included authentication
layer. You must run an authenticating reverse proxy in front of your services." At Loki v3.7.8 with
dskit `8d1c6d34bb5a42b04caa982d68403c5a643bb742`, `server.http-listen-address` and
`server.grpc-listen-address` default to empty. `server.http-listen-port` defaults to 3100 in Loki,
overriding dskit's 80; `server.grpc-listen-port` keeps dskit's 9095. Both listen networks default to
`tcp`. dskit passes the address and port through `net.JoinHostPort` to `net.Listen`: an empty
address becomes `:3100` or `:9095`, a wildcard listener. IPv4 and IPv6 coverage depends on the
host's Go/OS networking support; do not assume IPv6 is excluded. These are source-derived defaults,
not observed sockets. The shipped `cmd/loki/loki-local-config.yaml` instead sets gRPC 9096 and
`auth_enabled: false`; `production/docker/config/loki.yaml` explicitly sets both addresses to
`0.0.0.0`, ports 3100/9095 and `auth_enabled: true`. Read your effective configuration.

With memberlist as the ring store, Loki v3.7.8 uses dskit
`8d1c6d34bb5a42b04caa982d68403c5a643bb742`: its TCP-only gossip transport defaults to
`memberlist.bind-port` 7946 and `memberlist.bind-addr` 0.0.0.0 (a wildcard bind). An omitted or
empty bind-address list selects 0.0.0.0; an empty string inside the list is invalid. TLS defaults
to off, and gossip has no peer authentication without it. `memberlist.cluster-label` adds a label
to outgoing messages and rejects mismatched incoming labels unless
`memberlist.cluster-label-verification-disabled` is true. Treat that label as protection against
accidental cluster mixing, not as a credential: a peer can send the same label. This dskit wiring
exposes no HashiCorp memberlist `SecretKey` or keyring setting. Without TLS, a reachable peer speaking
the protocol and matching any configured label can join the gossip cluster and submit KV updates, including ring
tokens and instance states, subject to the codec and merge rules. Disrupted ingestion or queries are
a consequence inferred from that state-sharing path, not demonstrated here.

`memberlist.tls-enabled` enables TLS, but at this pin it does **not** require or verify incoming
client certificates. The transport reuses dskit's `ClientConfig`: `memberlist.tls-cert-path` and
`memberlist.tls-key-path` supply its certificate and key, while `memberlist.tls-ca-path` populates
`RootCAs` for outgoing server verification, not `ClientCAs`. `ClientAuth` stays at Go's default
`NoClientCert`; no memberlist setting here selects `RequireAndVerifyClientCert`. Keep
`memberlist.tls-insecure-skip-verify` false (the default); `memberlist.tls-server-name` can set the
expected server certificate name. TLS with these settings is not mutual peer authentication. Bind
`memberlist.bind-addr` (YAML `memberlist.bind_addr`, a list) to the private cluster network and restrict
access to trusted cluster peers with network controls, even with TLS enabled. If incoming client
certificate verification is required, enforce it through a separate authenticated transport boundary.
`memberlist.advertise-addr` and `memberlist.advertise-port` select the IP and port announced to peers,
for example through NAT; they do not restrict the listener. Without an explicit advertise address,
the transport derives an address from the first bind (a private IP for 0.0.0.0) and advertises its
actual bound port. Set an explicit reachable cluster IP when that automatic choice is unsuitable.

`auth_enabled: true`, the default, selects multi-tenancy, not authentication. Tenant-scoped
HTTP handlers require `X-Scope-OrgID`, but the header does not prove the caller owns that tenant.
dskit's tenant validation checks syntax and length, not identity or permission. With
`auth_enabled: false`, Loki uses tenant `fake`. A missing-header rejection is not a login gate.
dskit's default gRPC interceptor chain has no credential authentication; Loki adds its auth setup,
with explicit tenant-check exemptions for health, frontend worker, scheduler and other internal RPCs.
The complete interceptor behaviour has not been re-traced here. Do not expose gRPC on the
strength of `auth_enabled`.

A reachable client without credentials can submit logs through `POST /loki/api/v1/push` and query
through `/loki/api/v1/query` or `/loki/api/v1/query_range`, subject to tenant headers and ingestion
or query policies. `GET /config` exposes configuration; `/metrics` and `/debug/pprof/` are
registered by default. These routes have no tenant-auth wrapper. When the ingester runs,
`GET` or `POST /flush` and `GET` or `POST /ingester/shutdown` call maintenance handlers without
that wrapper; `/ingester/prepare_shutdown` also accepts `POST`, `GET` and `DELETE`.
When the compactor runs outside its worker mode (which returns before these routes are registered), with a TSDB or boltdb-shipper index in the schema (without one it logs that it is not starting and registers nothing, with no error) and `retention_enabled: true` (which also requires `compactor.delete-request-store`, or startup fails), `/loki/api/v1/delete` accepts
`PUT`/`POST` to request deletion, `GET` to list requests and `DELETE` to cancel one.
Those routes wrap HTTP tenant middleware and deletion `TenantMiddleware`. The latter rejects a
missing/invalid tenant or policy error with HTTP 400, and a tenant for which `validDeletionLimit`
returns false with HTTP 403. A caller reaching the route with a tenant context that passes this
check may use the handlers; tenant headers alone do not authenticate the caller. Limits name
`disabled`, `filter-only` and `filter-and-delete`, default to `filter-and-delete`, and expose
per-tenant overrides. The flag help says the API is available for `filter-only` and
`filter-and-delete` when retention is on. In v3.7.8, `validDeletionLimit` reads
the tenant's `DeletionMode`, passes it to `deletionmode.ParseMode`, and returns
`DeleteEnabled()`: true for `filter-only` and `filter-and-delete`, false for `disabled`.
Parsing accepts only those exact strings; any other value returns an error. Thus, after
tenant validation, the same middleware allows create, list and cancel for either enabled
mode, returns HTTP 403 for `disabled`, and HTTP 400 for an unrecognized mode.
This is source reasoning about admission to the handlers, not observed responses or proof
of eventual deletion. A permitted
`PUT`/`POST` validates the query and time range, returns HTTP 400 for bad inputs or 500 for store
failure, and returns HTTP 204 with `X-Delete-Request-ID` after the request is stored. `GET` lists
that tenant's requests as JSON, with 500 on store failure. When both `start` and `end`
are supplied, an invalid value writes HTTP 400 without stopping the handler. `DELETE` looks
up a request under the tenant ID: an ID the store does not find returns 404; processed
requests return 400; partially completed or overdue
requests return 400 unless `force=true`; store failure returns 500; removal returns 204. A stored
request does not establish eventual deletion. The gRPC listener registers ingester push/query services in single-binary mode
and an HTTP-over-gRPC bridge to the HTTP router. HTTP-only TLS or a proxy in front of 3100 therefore
does not protect all paths to these services. These exposure consequences are REASONED, not live
attack results.

There are two fixes, and you can use both:

- **mTLS on the servers.** dskit's `server.http_tls_config` and `server.grpc_tls_config` each
  accept `cert_file`, `key_file`, `client_ca_file` and `client_auth_type`; YAML also accepts
  inline `cert`, `key` and `client_ca`. All default to empty, so both listeners serve plaintext
  by default. TLS is constructed only when both a certificate and a key are supplied. A CA file
  alone does not enable TLS or require a client certificate. Unlike memberlist's transport above,
  both server configs pass client-auth policy and client CAs to the TLS builder. Set
  `client_auth_type: RequireAndVerifyClientCert` and the trusted client CA to require verified
  client certificates. The example enables HTTP mTLS and recommends loopback gRPC for one process
  with no remote gRPC clients; check ingestion and queries with your effective configuration:

  ```yaml
  # Overlay on a working single-binary config (keep your storage and schema_config).
  common:
    instance_addr: 127.0.0.1   # advertised address must be reachable on the gRPC bind
    replication_factor: 1      # one instance; the default is 3
    ring:
      kvstore:
        store: inmemory        # single binary: no memberlist gossip listener
  server:
    http_listen_address: 10.0.0.6
    grpc_listen_address: 127.0.0.1   # single-process recommendation; verify internal clients
    http_tls_config:
      cert_file: /etc/loki/tls/server.crt
      key_file: /etc/loki/tls/server.key
      client_auth_type: RequireAndVerifyClientCert
      client_ca_file: /etc/loki/tls/clients-ca.crt
  ```

  `common.instance_addr` supplies common ring and frontend addresses; explicit component settings
  can override it. `modules.go` sets the ingester lifecycler's listen port to the server gRPC listen
  port, which Loki replaces with the bound port when it is configured as 0 (the ingester
  module depends on `Server`, and dskit's module manager initializes a module's dependencies
  before the module itself). The lifecycler takes its advertised port from
  `GetInstancePort(cfg.Port, cfg.ListenPort)`, which returns a positive configured `Port`
  (default 0; a configured common ring copies its `instance_port` into it) and otherwise that
  listen port. The advertised address is the configured `Addr`, or else one that
  `netutil.GetFirstAddressOf` selects from the configured interfaces, joined with that port.
  The lifecycler registers this address in the ring, and distributor and querier construction
  receive the ring and ingester client settings.
  Distributors select ingester ring entries for writes; queriers select ring entries for reads.
  Both obtain clients by each entry's advertised address, and the ingester client calls `grpc.Dial`
  with dskit gRPC client options. `modules.go` builds the server gRPC listen address and port,
  target flags, scheduler ring and worker configuration into the worker service configuration and
  passes it to `querier.InitWorkerService`. In v3.7.8 `worker_service.go`, standalone means
  the frontend, scheduler, read and all target flags are all false. In that case, a nil
  scheduler ring and empty frontend and scheduler addresses return no worker service;
  otherwise the worker configuration and ring are passed to `NewQuerierWorker`.
  Outside that standalone case, if the ring is nil and both addresses are empty, the initializer
  sets `FrontendAddress` to the server gRPC port with the nonempty gRPC listen address,
  or `127.0.0.1` when that listen address is empty, then passes the configuration and ring
  to `NewQuerierWorker`. This automatic branch warns that unresponsive queries may need
  explicit worker configuration.
  The querier worker selects the scheduler ring first, then an explicit scheduler address,
  then a frontend address, which may be explicit or automatically set above.
  It constructs ring/DNS watchers. Each DNS lookup period, the ring watcher requests the scheduler
  ring's `Write` replication set for key 0 and, only when that set is non-empty, reports addresses
  added to or removed from its previous list. The DNS watcher hands the lookup period to dskit's
  resolver as its polling frequency and resolves the address with no SRV service name: an IP
  address is reported once, and a host name is re-resolved by host lookup each period, with
  dskit's default port 443 when the address names no port.
  `AddressAdded` passes a target to `connect`, whose
  `grpc.DialContext` uses `QuerySchedulerGRPCClientConfig` for scheduler connections or
  `NewQueryFrontendGRPCClientConfig` for frontend connections.
  `AddressAdded` then passes that connection to a processor manager, which runs processor
  goroutines on it (`processQueriesOnSingleStream`); the worker divides its maximum concurrency
  among managers, at least one each. `AddressRemoved` stops a manager, which notifies the remote
  end of shutdown and closes the connection.
  A direct frontend processor opens `Process` on the supplied connection; a scheduler
  processor opens `QuerierLoop` on it. Scheduler requests carry `FrontendAddress` into
  the result path, which asks the frontend pool for that address and calls `QueryResult`;
  the pool's client factory calls `grpc.Dial` with `NewQueryFrontendGRPCClientConfig`.
  These are source call sites; this guide does not infer successful connections from them.
  The scheduler processor's frontend pool has no service discovery and health-checks its clients
  every 5 seconds with a 1-second timeout. dskit client pools cache one client per address and
  create it through the pool factory on first use. A pool with health checks enabled removes a
  client whose health check keeps failing past the grace period. Health checks are always enabled
  for the frontend pool and, through `health_check_ingesters` (default true), for the ingester
  pools; Loki sets no grace period in these pools, so the first failed check removes the client.
  The distributor and querier ingester pools also remove clients whose addresses are no longer
  among the healthy ring entries.
  Lifecyclers write their instance entry, including the advertised address, into the ring key by
  KV compare-and-swap at ring initialization and on each heartbeat. The KV backend is `consul`,
  `etcd`, a process-wide `inmemory` store, `memberlist` or `multi` (plus a test-only `mock`). Ring
  clients read and then watch the same key and build replication sets from its entries:
  distributors take a `WriteNoExtend` set per stream, and queriers, outside partition-ingester
  queries, take the healthy `Read` set and call `ring.DoUntilQuorum`, which runs the per-ingester
  call in parallel until its quorum condition is met or too many calls fail; each call takes a
  pooled client by the entry's address.
  Push HTTP handlers call `PushWithResolver`; outside the `all`, `write` and `ingester` targets
  the distributor also registers the gRPC `Pusher` service. Kafka writes are off by default
  and ingester writes are on. With Kafka writes on, the distributor requires a partition ring,
  creates a Kafka writer client and produces each stream's records to an active partition.
  Queriers send the ingester interval of a log selection to the ingester querier when
  `query_store_only` is unset and the selection ends within the ingester lookback, which is
  `query_ingesters_within` (0 sends every selection) unless the ingester's
  `query_store_max_look_back_period` is nonzero when the querier module initializes and
  replaces it. Without the `all` target, a configured 0 stays 0 and `query_ingesters_within`
  applies. When the target list includes `all` but none of `querier`, `ruler`, `read`,
  `index-gateway` or `backend`, and the active or next schema period uses a boltdb-shipper or
  TSDB index, the store module, which the querier module depends on and the module manager
  initializes first, turns a configured 0 into a computed minimum that then replaces
  `query_ingesters_within`. That minimum is the ingester's maximum chunk age plus
  21 minutes, the index cache validity and three resync intervals of that index's shipper.
  The setting's flag help limits it to boltdb-shipper or TSDB indexes with the `filesystem`
  object store, and the same `all`-target store setup rejects a nonzero value with any other
  object store. With the `filesystem` object store, that setup also rejects a positive value
  below the computed minimum and keeps `-1` and any other negative value unchanged. The flag
  help documents `-1` as infinite, which sends every selection to ingesters and none directly to
  the store; the querier treats only exactly `-1` that way, querying ingesters for the whole
  selection and skipping its store query. A positive value, once the querier module copies it,
  limits the querier's own store query to the part of a selection before now minus that value,
  and a selection starting after that point goes to ingesters only. For any other negative
  value, now minus that value lies in the future, and the querier sets the end of any store
  request it makes to that point without clamping it to the selection's end, whereas the ingester
  leaves the start of its own store request unchanged for `-1` and every other negative value.
  From this source reading, without a Loki run, when that future point is after the selection's
  end, the querier's interval code also starts the ingester interval there and ends it at the
  selection's end without checking their order, and, unless `query_store_only` is set, the
  querier sends that inverted interval to the ingester querier for log and sample selections that
  pass the querier's request validation and reach interval construction. Under those `all`-target
  conditions, the ingester itself also queries the store for the log and sample selections it
  serves: the ingester module depends on the store module, so the module manager initializes the
  store first and the ingester receives the adjusted configuration. The ingester moves the start
  of each store request up to now minus a positive lookback, leaves it unchanged for `-1` and
  other negative values, and skips the store query when that adjusted start is after the
  selection's end. From the same source reading, the ingester querier passes the inverted
  interval to the gRPC `Query` or `QuerySample` call of each ingester it queries, which the
  ingester module registers the ingester, or a wrapper that Go code embedding Loki may set (the
  field has no YAML key), to serve. Without a configured wrapper, the ingester itself serves
  those calls: since it never moves a store request's start earlier, it makes no store query for
  that interval whatever its own lookback, and its in-memory query looks up streams in its index
  at the interval's start and skips each chunk unless the chunk's bounds start no later than the
  selection's end and end no earlier than that future point. From the same source reading, in that
  case the ingester adds every stream to each index it builds (a bit-prefix index for TSDB schema
  periods, an inverted index for others), and the lookup uses the interval's start only to pick the
  index of the schema period containing it, for a future start the latest period starting at or
  before it; it matches label matchers and shard without reading time, so the inverted interval
  causes no lookup error. In the same reading, no stream, chunk or head-block iterator swaps or
  clamps the interval: a chunk, block or head block is read only if it starts no later than the
  selection's end and ends no earlier than that future point, and the ordered head block's log
  iterator drops every entry before the start or at or after the end. By that reading, the chunk's
  time-range filters, used for block entries in both directions, the head block in forward log
  queries and all sample queries, skip entries before the start but accept an entry timestamped
  exactly at the start before testing the end, so, in this guide's assessment, they pass only
  entries dated exactly at that future point. From the same source reading, the distributor
  validates each pushed entry against a context built from `time.Now()`: a timestamp strictly
  newer than now plus the tenant's `creation_grace_period` (default 10m) is rejected as too far
  in the future, so one exactly at that bound passes, and `reject_old_samples` (default true)
  rejects entries older than now minus `reject_old_samples_max_age` (default 7d); after
  validation, with `increment_duplicate_timestamp` on (default false), the distributor sets
  each different-line duplicate after the first to the previous stored entry's timestamp plus
  one nanosecond, so a push of n such entries at the bound can store the last one n-1
  nanoseconds past it. The ingester's own push chain, from its gRPC push through stream
  validation and append, compares entry timestamps with stream state and the schema
  configuration that stream creation reads, never the clock: it skips duplicates of the
  stream's last line, applies rate limits, drops entries below the stream's highest timestamp
  minus half `max_chunk_age` (default 2h) when unordered writes (default true) are on, and in
  the ordered path rejects an entry older than the head block's newest or, when the head block
  is empty with earlier cut blocks, than the previous block's maximum, so, in source, this push
  chain imposes no clock-relative upper bound on a stored entry's timestamp. In this guide's
  assessment, when the negative lookback's magnitude is at most the tenant's creation grace
  period, the inverted interval's start lies at or before the latest timestamp the distributor
  accepts at the query's moment, so an ingester can hold an entry dated exactly at that start;
  the comparison assumes the querier and distributor read one reference clock and the tenant's
  grace period is unchanged, since an entry keeping its submitted timestamp must pass
  validation while now plus that grace period still reaches the start. For a larger magnitude,
  a direct ingester gRPC push is one route this reading establishes; the Kafka
  partition-ingester consumer pushes each consumed record into the same push code, a path
  otherwise untraced here, and the distributor's duplicate-timestamp shifts are not ruled out.
  No Loki run has observed an ingester holding or returning such an entry. By that reading too,
  backward log queries do not time-filter the head block, and the
  unordered head block queries its vendored go-datastructures v1.1.7 range tree from the interval's
  start to one nanosecond before its end, both inclusive; for the inverted interval that query
  returns no entry, so the head block yields nothing. From the same source reading, when the
  ingester's `Query` or `QuerySample` code gets an iterator that yields nothing without an error
  and the request context is not yet done, it sends one batch with no streams or series, carrying
  its query statistics and warnings, and returns no error unless that send returns an error other
  than the exact value `context.Canceled`. If the context is already done before the send, that
  code skips it with no error; it never aborts a send in progress, and what the send returns if the
  context ends during it is not traced. The ingester querier's per-ingester iterator records those
  statistics and warnings, yields nothing and ends without an error at the end of the stream, while
  any other receive error propagates, and the querier merges the per-ingester iterators with any
  store query it makes for the selection. A source-reading word search for `Wrapper` in Loki's
  `pkg`, `cmd`, `integration`, `tools` and `clients` trees at v3.7.8 finds only that field's
  declaration, its one-method `Wrap` interface and the ingester module's nil check and `Wrap` call,
  besides a code comment and two Bootstrap stylesheet source maps; nothing in those trees sets it.
  So what the ingester querier and ingesters return for the interval is still not established and
  has not been observed, and what a wrapper set outside those trees does is not traced.
  `Run` initializes the target modules through the module manager and starts the resulting
  services together. The internal server module exists only when `internal-server.enable` is
  true (default false); it is then inserted before `Server` in each module dependency list that
  names `Server`, and its HTTP listener defaults to `localhost:3101`. It serves routes including
  `/ready` and the buildinfo route and, when their modules run, `/ring`, `/memberlist` and the
  compactor's handler prefix. Its flags register no gRPC listen address or port. This guide
  infers from dskit's listener code that, unless YAML sets them, its gRPC listener uses an empty
  address and port 0, an any-address listener on an OS-chosen port that carries the
  HTTP-over-gRPC bridge to the internal router; this has not been observed.
  `common.instance_addr` also
  sets `MemberlistKV.AdvertiseAddr` when set; memberlist gossip is separate from these gRPC
  calls. A single-binary compactor client uses the server gRPC listen address and port when deletion
  filtering is enabled. Loopback remains this guide's recommendation for this configuration, not a guarantee for
  every single-binary deployment: verify effective
  advertised and dial addresses, worker/frontend/scheduler settings, successful pushes and queries,
  and any compactor calls. This guide's assessment is that these cited paths do not establish
  complete per-module start-up behaviour, the Kafka consumer, Kafka-only and partition-ingester
  paths, every other RPC hop, or live reachability. Remote components need a private address
  reachable from their hosts.

  Keep gRPC restricted to trusted callers: plaintext loopback is still reachable by local users.
  Enabling `grpc_tls_config` also requires compatible TLS settings on every internal gRPC client,
  including client certificates when required; changing the server alone can break internal RPCs.
  This HTTP mTLS overlay does not configure those clients. mTLS does not set `X-Scope-OrgID`;
  your agent or proxy must still supply the tenant header when multi-tenancy is enabled.
  With the `inmemory` ring, check that no gossip listener is present. With memberlist, apply the
  separate private-cluster and trusted-peer restrictions above.

  **REASONED:** all Loki socket, push/query, administrative-route and TLS/client-certificate checks
  here follow the cited documentation and pinned sources: the authoring host forbids opening listeners without an isolated network
  namespace, and has none. Expected HTTP mTLS outcomes are a successful authorized request, handshake
  rejection without a trusted client certificate, and refusal of plaintext application requests.
  Check both IPv4 and IPv6 exposure, gRPC reachability and internal RPC success.
  No Loki listener or TLS test was run for this audit.
- **An authenticating proxy that owns the tenant header.** The vendor's nginx example sets
  `proxy_set_header X-Scope-OrgID $remote_user;` so that "nginx overwrites any tenant header sent by the
  client". Keep Loki itself reachable only from that proxy. See [nginx.md](nginx.md) and
  [fronting-auth.md](fronting-auth.md).

## Verify

REASONED: following block; this introduction and the TCP and UDP listener inventory below for every port it names, per the guide's cited node_exporter v1.12.1 source, Alertmanager v0.34.1 README, Pushgateway v1.11.3 README, Jaeger v2.21.0 ports and dskit pinned wildcard listener construction entries. No second host and no isolated network namespace were available, so no wildcard bind was observed. During marking review (October 2026) the block passed bash -n under bash 5.3.9, and its two commands, run without sudo on the review host as ss -tlnp and ss -ulnp (iproute2 6.19.0), accepted their flags and showed none of the named TCP or UDP ports listening, with an empty process column, so they tested no target; the sudo form was not run. Exposed, a listed port shows a wildcard bind; fixed, loopback or a private address. The non-Loki loopback HTTP runs on 127.0.0.1 against the versions named at the top
are declared DEMONSTRATED at the credential block below and were not repeated in this marking review. All Loki checks are REASONED: the authoring host
forbids opening listeners without an isolated network namespace, and has none. The default
all-interfaces binds were not observed, so they are
reasoned: the authoring host forbids binding every interface, so each run overrode the address to
127.0.0.1. The binds follow from each binary's `--help` default (`:9100`, `:9093`, `0.0.0.0:9094`,
`:9091`) and from source (Loki's empty listen addresses; Jaeger's `":" + port` query default). Go
listens on every interface for an address with no host. The probes from a second host are reasoned
too: the authoring environment had no second host, so the refusal or timeout expected there was not
observed. On the host:

```bash
# REASONED: listener inventory expectations follow the cited sources and recorded loopback runs; wildcard binds and Loki listeners were not observed.
sudo ss -tlnp   # loopback or a private address only: 9100 9093 9094 9091 3100 9095 7946, and
                # Jaeger's 16686 16685 4317 4318 14250 14268 9411 5778 5779 13133 27777 27778 8888
sudo ss -ulnp   # Alertmanager gossip also uses UDP 9094; Jaeger's Thrift receivers UDP 6831 and 6832
```

REASONED: preceding block; the expected inventory results for every TCP and UDP port the block names, per the same cited listener sources; no wildcard bind was observed because no isolated network namespace was available. The following block's guard was run with a stub curl: unchanged, it printed its substitute-the-service-address refusal. Exposed, the reasoned expectation is `*:9100` (or `0.0.0.0:`/`[::]:`) for an unconfigured node_exporter,
and likewise for the others. Fixed means a loopback or private address. Then probe from a host that
should not have access. The block refuses to run until you substitute the address.

REASONED: following block; external probes follow the cited listener and authentication sources; the authoring environment had no second host and no Loki listener was run.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVICE_ADDRESS'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the service address on the set -- line above; not probing" ;;
    *) for u in "http://$1:9100/metrics" "http://$1:9093/api/v2/status" "http://$1:9091/metrics" \
                "http://$1:16686/api/v3/services" "http://$1:3100/config"; do
         curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
           -w "$u http=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "$u"
       done ;;
  esac
)
```

REASONED: preceding block; the second-host probes of node_exporter, Alertmanager, Pushgateway, Jaeger and Loki and the Loki tenant-header repeat, per the guide's cited Prometheus security model, Exporter toolkit v0.17.1 web configuration, Jaeger 2.21 security and Loki v3.7.8 authentication entries. The authoring environment had no second host and no Loki listener. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ran with a stub curl and no network: without its set -- line it printed the paste-the-whole-block refusal, and with 203.0.113.10 substituted the stub received the five URLs in order. The expected exposed and fixed results are those stated here. Any `200` is the finding: that service answers the unauthenticated request. For a service that uses
TLS, switch that URL to `https`. A `401` then means its authentication is on. From a host that should
be blocked, a connection refusal or a connect timeout is consistent with isolation. Read the `err`
text to confirm it happened while connecting, not in a local proxy or policy. The write-out fields need
curl 7.75.0 or newer. For Loki, a `401` without a tenant header proves nothing. Repeat the Loki probe
with `-H 'X-Scope-OrgID: anyone'` added, and treat a `200` as exposure.

REASONED: the positive-control and stdin-password instructions for the following credential pair, per the guide's cited Exporter toolkit v0.17.1 web configuration entry. The pair itself is declared below from the guide's recorded loopback runs; this marking review did not repeat them. During marking review (October 2026) that block passed bash -n under bash 5.3.9 and ran with a stub curl and no network: unchanged, it printed its substitute-the-URL refusal; an http:// URL drew the use-an-https-URL refusal; a user containing a colon was refused; and with dummy values the password reached curl only on stdin as an escaped user line, never in argv. Exposed, the request without credentials returns 200; fixed, 401 without and 200 with credentials. Run the positive control from a host that should have access, so a dead service is not read as fixed.
The password reaches curl on stdin, not argv. Substitute inside the quotes, and add
`--cacert /path/to/ca.crt` if the certificate is private.

DEMONSTRATED: following block; the recorded loopback HTTPS GETs for node_exporter, Pushgateway, Alertmanager and Jaeger returned 401 without credentials and 200 with them.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The password you substitute on the set -- line enters shell history.
  # Clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_URL' 'REPLACE_WITH_USER' 'REPLACE_WITH_PASSWORD'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the URL (https://...) on the set -- line above; not probing"; exit ;; esac
  case "$1" in https://*) ;; *) echo "use an https:// URL: basic auth over plain HTTP sends the password in cleartext; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*|*:*) echo "substitute the user (no colon) on the set -- line above; not probing"; exit ;; esac
  case "$3" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the password on the set -- line above; not probing"; exit ;; esac
  set -- "$1" "${2//\\/\\\\}" "${3//\\/\\\\}"
  set -- "$1" "${2//\"/\\\"}" "${3//\"/\\\"}"
  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
    -w 'no credentials: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
  printf 'user = "%s:%s"\n' "$2" "$3" | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
    -w 'with credentials: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --config - "$1"
)
```

Fixed, `no credentials` is `401` and `with credentials` is `200`. The loopback runs gave exactly that
pair over HTTPS for GETs of node_exporter `/metrics`, Pushgateway `/metrics`, Alertmanager
`/api/v2/status` and Jaeger `/api/v3/services`. For Loki under mTLS, the REASONED equivalent is `--cert` and `--key` on an authorized client
(`200`) against the same request without them, which fails in the handshake. This closes the argv
channel only. The password can still reach shell history or `set -x` output, and stdin does not hide it
from your own account's view of the process.

## Sources (checked September 2026)

- node_exporter v1.12.1 README (port 9100, `--web.config.file`): https://github.com/prometheus/node_exporter/blob/v1.12.1/README.md
- node_exporter v1.12.1 source (`:9100` default, `net/http/pprof` import): https://github.com/prometheus/node_exporter/blob/v1.12.1/node_exporter.go
- Exporter toolkit v0.17.1 web configuration (`tls_server_config`, `client_auth_type`, `basic_auth_users`, experimental status): https://github.com/prometheus/exporter-toolkit/blob/v0.17.1/docs/web-configuration.md
- Prometheus security model (exporters, Alertmanager, Pushgateway, CORS, API Security): https://github.com/prometheus/docs/blob/a0d29881382ad1ea20597d34fc4229984b326576/docs/operating/security.md
- Alertmanager v0.34.1 README (cluster listen address, TCP and UDP, load-balancing warning): https://github.com/prometheus/alertmanager/blob/v0.34.1/README.md
- Alertmanager v0.34.1 HTTPS and gossip TLS (`--web.config.file`, `--cluster.tls-config`): https://github.com/prometheus/alertmanager/blob/v0.34.1/docs/https.md
- Alertmanager v0.34.1 management API (`/-/reload`): https://github.com/prometheus/alertmanager/blob/v0.34.1/docs/management_api.md
- Pushgateway v1.11.3 README (port 9091, TLS and basic auth scope, DELETE, admin API): https://github.com/prometheus/pushgateway/blob/v1.11.3/README.md
- Pushgateway v1.11.3 source (admin and lifecycle flags, pprof route): https://github.com/prometheus/pushgateway/blob/v1.11.3/main.go
- Jaeger 2.21 configuration (`JAEGER_LISTEN_HOST`, `jaeger_query` endpoints): https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/configuration.md
- Jaeger 2.21 security (TLS and mTLS for query clients, proxy guidance): https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/security.md
- Jaeger v2.21.0 all-in-one configuration: https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/internal/all-in-one.yaml
- Jaeger v2.21.0 query defaults and MCP (`PortToHostPort`, `ai.mcp`): https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/internal/extension/jaegerquery/internal/flags.go
- Jaeger v2.21.0 ports: https://github.com/jaegertracing/jaeger/blob/v2.21.0/ports/ports.go
- Jaeger v2.21.0 Dockerfile (`ENV JAEGER_LISTEN_HOST=0.0.0.0`): https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/Dockerfile
- Jaeger v2.21.0 release notes (v1 HTTP endpoints removed): https://github.com/jaegertracing/jaeger/releases/tag/v2.21.0
- OpenTelemetry Collector configtls v1.66.0, as pinned by Jaeger v2.21.0 (`cert_file`, `key_file`): https://github.com/open-telemetry/opentelemetry-collector/blob/cd3455cf3a7f672208140b1ebb1581c542b2b0ed/config/configtls/README.md
- OpenTelemetry Collector contrib v0.160.0 basicauth extension (`htpasswd`, `authenticator`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.160.0/extension/basicauthextension/README.md
- Loki v3.7.8 authentication (no built-in auth, tenancy header, mTLS, nginx tenant header): https://github.com/grafana/loki/blob/v3.7.8/docs/sources/operations/authentication.md
- Loki v3.7.8 HTTP API (`/config`, `/flush`, `/ingester/shutdown`, deletion): https://github.com/grafana/loki/blob/v3.7.8/docs/sources/reference/loki-http-api.md
- Loki v3.7.8 `auth.enabled` default and fake tenant: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L150-L162
- Loki v3.7.8 common config (`common.replication-factor` default 3): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/common/common.go
- Loki v3.7.8 config wrapper (`common.instance_addr` copied into component addresses): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L162-L174
- Loki v3.7.8 sample local configuration: https://github.com/grafana/loki/blob/v3.7.8/cmd/loki/loki-local-config.yaml#L1-L16
- dskit pinned listener and TLS flag defaults, and the `server.register-instrumentation` default (true; that default was read in the module tree extracted from the downloaded dskit v0.0.0-20260209132809-8d1c6d34bb5a zip, whose proxy-reported origin is the commit this link pins, and the zip was not compared with that commit's git tree): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L189-L212
- Loki v3.7.8 HTTP port override: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L241-L269
- Loki v3.7.8 production Docker listener overrides: https://github.com/grafana/loki/blob/v3.7.8/production/docker/config/loki.yaml#L1-L8
- Loki v3.7.8 auth setup and gRPC exemptions: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L495-L509
- Loki v3.7.8 fake HTTP tenant propagation: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L208-L222
- Loki v3.7.8 push routes and middleware: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L399-L422
- Loki v3.7.8 query frontend middleware and routes: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1307-L1378
- Loki v3.7.8 config route: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L533-L540
- Loki v3.7.8 ingester gRPC services and maintenance routes: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L751-L790
- Loki v3.7.8 conditional deletion routes and middleware (compactor worker mode returns first): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1866-L1869 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1880-L1883 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1899-L1908 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1935-L1952
- Loki v3.7.8 deletion tenant-policy middleware: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/tenant_request_handler.go#L10-L34
- Loki v3.7.8 deletion create handler: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L49-L110
- Loki v3.7.8 deletion list handler: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L134-L190
- Loki v3.7.8 deletion cancel handler: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L259-L303
- Loki v3.7.8 deletion mode defaults: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L450-L453
- Loki v3.7.8 tenant deletion mode override: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L1128-L1132
- Loki v3.7.8 worker address selection and discovery: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L117-L182
- Loki v3.7.8 worker gRPC dial: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L222-L245
- Loki v3.7.8 worker gRPC dial options: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L297-L310
- Loki v3.7.8 frontend stream: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/frontend_processor.go#L49-L80
- Loki v3.7.8 scheduler stream: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L87-L164
- Loki v3.7.8 scheduler request handling and reply to the frontend address: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L183-L244
- Loki v3.7.8 scheduler response gRPC dial: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L246-L335
- Loki v3.7.8 frontend client pool construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L57
- Loki v3.7.8 ingester client dial: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/client/client.go#L65-L91
- Loki v3.7.8 ingester lifecycler construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L358-L365
- Loki v3.7.8 querier ingester client factory: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L58-L74
- Loki v3.7.8 querier ingester call: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L187-L220
- Loki v3.7.8 distributor ingester client factory: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L249-L253
- Loki v3.7.8 distributor ingester ring assignment: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L344
- Loki v3.7.8 distributor client and ring parameters: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L231-L236
- Loki v3.7.8 distributor push dispatch: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L900-L921
- Loki v3.7.8 distributor per-ingester push task: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1216-L1231
- Loki v3.7.8 distributor ring selection: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L879-L893
- Loki v3.7.8 distributor ingester push: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1258-L1271
- Loki v3.7.8 distributor ingester client pool: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L346
- Loki v3.7.8 worker connection inputs: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L571-L580
- Loki v3.7.8 worker service initializer call: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L734-L740
- Loki v3.7.8 common ring propagation to ingester: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L193-L248
- Loki v3.7.8 ingester clients receive ring configuration: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L373-L390
- Loki v3.7.8 ingester ring built from the lifecycler ring configuration and ring key: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L271-L272
- Loki v3.7.8 querier ingester-client construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1130-L1138
- Loki v3.7.8 single-binary compactor address: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1241-L1262
- Loki v3.7.8 conditional compactor gRPC client: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2532-L2561
- dskit pinned TLS YAML fields: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L69-L78
- dskit pinned wildcard listener construction: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L309-L332
- dskit pinned server TLS and client-auth construction: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L357-L395
- dskit pinned instrumentation registration gate (`if cfg.RegisterInstrumentation`), read in the module tree extracted from the downloaded dskit v0.0.0-20260209132809-8d1c6d34bb5a zip, whose proxy-reported origin is the commit this link pins; the zip was not compared with that commit's git tree: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L411-L412
- dskit pinned default gRPC interceptor chain: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L433-L468
- dskit pinned metrics and pprof routes: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L577-L583
- dskit pinned HTTP-over-gRPC bridge: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L673-L681
- dskit pinned HTTP tenant propagation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/middleware/http_auth.go#L13-L23
- dskit pinned gRPC tenant propagation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/middleware/grpc_auth.go#L36-L57
- dskit pinned tenant syntax validation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/tenant/tenant.go#L85-L99
- Loki v3.7.8 dskit dependency pin: https://github.com/grafana/loki/blob/v3.7.8/go.mod#L55
- dskit pinned transport flags (bind list, port 7946, TLS off): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L41-L86
- dskit pinned listener construction (empty list becomes 0.0.0.0, invalid address rejection, shared TLS config): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L133-L197
- dskit pinned advertise address and port selection: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L394-L451
- dskit pinned cluster-label and advertise flags: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L229-L232
- dskit pinned memberlist wiring (TCP transport, delegate and labels; no SecretKey or keyring configuration): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L457-L520
- dskit pinned TLS fields and defaults: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/crypto/tls/tls.go#L27-L64
- dskit pinned TLS construction (RootCAs and certificates; ClientAuth and ClientCAs unset): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/crypto/tls/tls.go#L86-L175
- Go TLS ClientAuthType (NoClientCert default and RequireAndVerifyClientCert semantics): https://pkg.go.dev/crypto/tls#ClientAuthType
- dskit pinned incoming KV updates and propagation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1383-L1470
- dskit pinned gRPC dial options: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcclient/grpcclient.go#L125-L134
- dskit pinned ring lifecycler advertised address: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L189-L229
- dskit pinned ring lifecycler registration: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L709-L723
- dskit pinned lifecycler ring entry update: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L778-L781
- dskit pinned lifecycler loop calling ring initialization: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L541-L544
- dskit pinned lifecycler ring initialization entry: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L681
- dskit pinned remote-state merging and codec validation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1577-L1672
- Go `net.Listen` (an empty host listens on all addresses): https://pkg.go.dev/net#Listen
- [Loki v3.7.8 tenant middleware, fake tenant, and gRPC exemptions (checked October 2026)](https://raw.githubusercontent.com/grafana/loki/v3.7.8/pkg/util/fakeauth/fake_auth.go).
- [curl curl-8_14_1 write-out fields and version requirements (checked October 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79).
- Loki v3.7.8 deletion limit-to-mode call chain: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/util.go#L24-L36
- Loki v3.7.8 deletion mode names: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletionmode/mode.go#L15-L24
- Loki v3.7.8 deletion mode parsing and DeleteEnabled: https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletionmode/mode.go#L38-L56
- Loki v3.7.8 worker service configuration and standalone predicate: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker_service.go#L18-L42
- Loki v3.7.8 worker service address fallback and constructor calls: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker_service.go#L56-L112
- Loki v3.7.8 scheduler processor frontend client configuration and factory: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L37-L59
- Loki v3.7.8 bound gRPC port replacing a configured 0: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L224-L230
- dskit pinned instance address and GetInstancePort precedence: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/util.go#L16-L39
- dskit pinned lifecycler address and port flags: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L97-L100
- dskit pinned lifecycler heartbeat: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L602-L606
- dskit pinned lifecycler ring initialization write: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L697-L725
- dskit pinned lifecycler heartbeat write: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L950-L973
- dskit pinned KV backend selection: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/client.go#L137-L176
- dskit pinned ring KV client construction: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L319-L334
- dskit pinned ring initial read and watch: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L379-L411
- dskit pinned ring replication set for a key: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L497-L544
- dskit pinned healthy replication set for an operation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L711-L792
- dskit pinned DoUntilQuorum: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/replication_set.go#L157-L316
- dskit pinned pool address factory: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L43-L49
- dskit pinned client pool construction and client creation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L95-L165
- dskit pinned stale and unhealthy client removal: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L238-L318
- dskit pinned ring service discovery for client pools: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/ring_service_discovery.go#L9-L25
- dskit pinned DNS target parsing and resolution: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L76-L171
- dskit pinned DNS SRV skip, host lookup and polling: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L191-L268
- Loki v3.7.8 module start-up in Run: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L562-L664
- Loki v3.7.8 server and conditional internal-server module registration: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L750-L761
- Loki v3.7.8 module dependencies: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L816-L867
- Loki v3.7.8 internal-server dependency insertion: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L923-L941
- Loki v3.7.8 internal-server flags: https://github.com/grafana/loki/blob/v3.7.8/pkg/server/internal_server.go#L10-L33
- Loki v3.7.8 internal-server construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L245-L268
- Loki v3.7.8 server service running the server: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2646-L2664
- Loki v3.7.8 ring routes on both servers: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L276-L279
- Loki v3.7.8 push HTTP handlers: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/http.go#L28-L38
- Loki v3.7.8 push handler dispatch: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/http.go#L151
- Loki v3.7.8 distributor gRPC Push: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L552-L558
- Loki v3.7.8 distributor Kafka and ingester write flags: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L127-L136
- Loki v3.7.8 distributor Kafka writer construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L293-L308
- Loki v3.7.8 distributor Kafka dispatch: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L860-L867
- Loki v3.7.8 distributor Kafka record production: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1296-L1326
- Loki v3.7.8 distributor push validation context time: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L589-L592
- Loki v3.7.8 distributor per-entry validation call: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L690-L695
- Loki v3.7.8 distributor duplicate-timestamp reference initialized to the first entry's timestamp: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L686
- Loki v3.7.8 distributor duplicate-timestamp increment after validation: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L749-L758
- Loki v3.7.8 validation context timestamp bounds: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/validator.go#L66-L71
- Loki v3.7.8 entry timestamp validation (old and future checks): https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/validator.go#L94-L113
- Loki v3.7.8 `reject_old_samples` default: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L327
- Loki v3.7.8 `increment_duplicate_timestamp` default: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L328
- Loki v3.7.8 `reject_old_samples_max_age` and `creation_grace_period` defaults: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L351-L354
- Loki v3.7.8 `creation_grace_period` override getter (future meaning): https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L751-L754
- Loki v3.7.8 `unordered_writes` default: https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L362
- Loki v3.7.8 ingester `max_chunk_age` default: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L162
- Loki v3.7.8 ingester gRPC push to its tenant instance: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1001-L1024
- Loki v3.7.8 ingester Kafka consumer factory (the ingester as pusher): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L395
- Loki v3.7.8 Kafka consumer storing the pusher it pushes into: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/kafka_consumer.go#L53-L71
- Loki v3.7.8 Kafka consumer record push into the ingester: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/kafka_consumer.go#L150-L159
- Loki v3.7.8 ingester instance push to streams: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L231-L261
- Loki v3.7.8 stream creation chunk format from the entries' minimum timestamp: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L316
- Loki v3.7.8 chunk format selection from the schema configuration: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L423-L440
- Loki v3.7.8 ingester stream push (validate, then store): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L186-L247
- Loki v3.7.8 ingester stream entry validation (duplicate, rate limit, too far behind): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L401-L461
- Loki v3.7.8 ingester stream store and ordered append: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L339-L384
- Loki v3.7.8 ordered head block append: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L186-L200
- Loki v3.7.8 ordered chunk append previous-block check: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L872-L874
- Loki v3.7.8 querier store and ingester flags: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L77-L81
- Loki v3.7.8 querier ingester interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L176-L198
- Loki v3.7.8 querier sample ingester interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L242-L261
- Loki v3.7.8 querier intervals built from its configuration: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L302-L304
- Loki v3.7.8 ingester querier ring and partition sets: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L168-L186
- Loki v3.7.8 ingester client pool with ring discovery: https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/clientpool/ingester_client_pool.go#L30-L46
- Loki v3.7.8 processor manager: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/processor_manager.go#L35-L89
- Loki v3.7.8 worker watchers: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L157-L196
- Loki v3.7.8 worker address removal and concurrency: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L247-L295
- Loki v3.7.8 ring watcher: https://github.com/grafana/loki/blob/v3.7.8/pkg/util/ring_watcher.go#L14-L117
- Loki v3.7.8 DNS watcher: https://github.com/grafana/loki/blob/v3.7.8/pkg/util/dns_watcher.go#L30-L83
- dskit pinned DNS default port and resolver polling frequency: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L18-L36
- Loki v3.7.8 ingester pool health-check flag (`health_check_ingesters` default true): https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/clientpool/ingester_client_pool.go#L26
- dskit pinned module initialization (dependencies before the module): https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/modules/modules.go#L116-L156
- Loki v3.7.8 querier ingester and store intervals: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/intervals.go#L9-L104
- Loki v3.7.8 ingester store lookback copied to the querier: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L540-L542
- Loki v3.7.8 ingester store lookback flag (`-1` for infinite): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L163
- Loki v3.7.8 querier store query skipped without a store interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L200-L212
- Loki v3.7.8 querier sample store query skipped without a store interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L263-L272
- Loki v3.7.8 `-1` store lookback returning no store interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/intervals.go#L23-L25
- Loki v3.7.8 store module shipper setup for an object-storage index: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L910-L918
- Loki v3.7.8 all-target shipper store setup applying the store lookback: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1060-L1112
- Loki v3.7.8 store lookback check (0 becomes the minimum; nonzero rejected without the `filesystem` object store): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2573-L2588
- Loki v3.7.8 shipper delays, minimum store lookback and resync interval: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2607-L2639
- Loki v3.7.8 boltdb shard period (15 minutes): https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/stores/shipper/indexshipper/boltdb/table.go#L27
- Loki v3.7.8 index upload interval (1 minute): https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/stores/shipper/indexshipper/shipper.go#L45
- Loki v3.7.8 active schema period and object-storage index check: https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/config/schema_config.go#L345-L378
- Loki v3.7.8 store and querier module registration: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L770-L771
- Loki v3.7.8 module dependency registration: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L943-L947
- Loki v3.7.8 target-list membership check (`isTarget`): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L387-L389
- Loki v3.7.8 ingester log query merging a store query: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1102-L1119
- Loki v3.7.8 ingester sample query merging a store query: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1175-L1191
- Loki v3.7.8 ingester store query range (`QueryStore` gate; `-1` leaves the start unchanged): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1640-L1660
- Loki v3.7.8 querier log request validation: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L158-L169
- Loki v3.7.8 querier sample request validation: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L224-L235
- Loki v3.7.8 ingester querier log and sample calls: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L234-L264
- Loki v3.7.8 ingester registered as the gRPC Querier service: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L768-L773
- Loki v3.7.8 generated Querier `Query` and `QuerySample` handlers: https://github.com/grafana/loki/blob/v3.7.8/pkg/logproto/logproto.pb.go#L6166-L6193
- Loki v3.7.8 ingester log query of its tenant instance: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1093-L1100
- Loki v3.7.8 ingester sample query of its tenant instance: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1160-L1168
- Loki v3.7.8 ingester instance log query over matching streams: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L519-L532
- Loki v3.7.8 ingester instance sample query over matching streams: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L587-L610
- Loki v3.7.8 ingester index lookup at the request start: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L962-L975
- Loki v3.7.8 ingester stream chunk skip for log queries: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L588-L594
- Loki v3.7.8 ingester stream chunk skip for sample queries: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L635-L641
- Loki v3.7.8 ingester instance index construction (`NewMultiInvertedIndex`): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L152-L163
- Loki v3.7.8 ingester stream creation adding the stream to the index: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L312-L314
- Loki v3.7.8 ingester stream creation by fingerprint adding the stream to the index: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L404-L405
- Loki v3.7.8 ingester per-period index construction and add to every built index: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/multi.go#L26-L73
- Loki v3.7.8 ingester per-period index lookup and period selection: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/multi.go#L84-L117
- Loki v3.7.8 inverted index lookup by matchers and shard: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/index.go#L159-L183
- Loki v3.7.8 bit-prefix index lookup by matchers and shard: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/bitprefix.go#L131-L169
- Loki v3.7.8 ingester stream log chunk iterator call: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L601-L607
- Loki v3.7.8 ingester stream sample chunk iterator call: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L648-L650
- Loki v3.7.8 chunk log iterator (block skip, head block, time-range filters): https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1005-L1087
- Loki v3.7.8 chunk sample iterator (block skip, head block, time-range filter): https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1090-L1147
- Loki v3.7.8 ordered head block log iterator bounds and entry filter: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1310-L1328
- Loki v3.7.8 ordered head block sample iterator bounds: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1380-L1397
- Loki v3.7.8 unordered head block range-tree interval and query: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L185-L210
- Loki v3.7.8 unordered head block construction with a one-dimension range tree: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L69-L75
- Loki v3.7.8 unordered head block log iterator over the range-tree query: https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L260-L310
- Loki v3.7.8 go-datastructures v1.1.7 requirement: https://github.com/grafana/loki/blob/v3.7.8/go.mod#L19
- Loki v3.7.8 vendored go-datastructures range-tree inclusive-interval contract: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/interface.go#L38-L47
- Loki v3.7.8 vendored go-datastructures range-tree constructor: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/orderedtree.go#L259-L263
- Loki v3.7.8 vendored go-datastructures range-tree apply and Query: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/orderedtree.go#L180-L225
- Loki v3.7.8 vendored go-datastructures range-tree node search: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/ordered.go#L25-L30
- Loki v3.7.8 vendored go-datastructures range-tree bounded scan: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/ordered.go#L81-L98
- Loki v3.7.8 vendored go-datastructures range-tree entries pool and `NewEntries`: https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/entries.go#L21-L45
- Loki v3.7.8 entry time-range filter: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L478-L509
- Loki v3.7.8 sample time-range filter: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L681-L716
- Loki v3.7.8 ingester log batch send: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L1104-L1143
- Loki v3.7.8 ingester sample batch send: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L1145-L1179
- Loki v3.7.8 ingester log query batch limit and send call: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1121-L1129
- Loki v3.7.8 ingester sample query send call: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1193-L1195
- Loki v3.7.8 log batch read: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L681-L716
- Loki v3.7.8 sample batch read: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L718-L753
- Loki v3.7.8 ingester querier log stream iterator: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L362-L388
- Loki v3.7.8 ingester querier sample stream iterator: https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L480-L505
- Loki v3.7.8 querier log iterator merge: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L213-L216
- Loki v3.7.8 querier sample iterator merge: https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L274
- Loki v3.7.8 ingester `Wrapper` field (`yaml:"-"`): https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L126-L127
- Loki v3.7.8 ingester `Wrapper` interface: https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L210-L212
- Loki v3.7.8 internal-server memberlist route: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1814-L1816
- Loki v3.7.8 compactor handler prefix on both servers: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1928-L1933
- [curl curl-8_14_1 custom headers (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- [curl curl-8_14_1 configuration from stdin (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md).


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- node: node_exporter (v1.12.1)
- alert: Alertmanager (v0.34.1)
- push: Pushgateway (v1.11.3)
- jaeger: Jaeger (v2.21.0)
- loki: Loki (v3.7.8)
- jaeger-docs: Jaeger documentation (4d150659ee4ed3ccc69253ec77c368392f59e625)
- toolkit: Exporter toolkit (v0.17.1)
- security: Prometheus security model (a0d29881382ad1ea20597d34fc4229984b326576)
- tls: OpenTelemetry configtls (v1.66.0)
- basic: OpenTelemetry basicauth extension (v0.160.0)
- dskit: dskit (8d1c6d34bb5a42b04caa982d68403c5a643bb742)
- go: Go documentation (unknown)
- curl: curl (curl-8_14_1)

Claims (full source mapping in the JSON block below):

- node-bind (REASONED; node, go): node_exporter defaults to :9100 on all interfaces; private binds are required.
- node-open (DEMONSTRATED; node): Unconfigured loopback metrics and pprof both returned 200 without credentials.
- toolkit-config (REASONED; toolkit, node, alert, push): --web.config.file enables TLS and bcrypt Basic auth across HTTP paths; the format is experimental and not every exporter uses it.
- node-tls (DEMONSTRATED; node, toolkit): Loopback HTTP returned 400; HTTPS metrics/pprof rejected absent credentials and accepted correct ones.
- toolkit-mtls (REASONED; toolkit): Use RequireAndVerifyClientCert with client_ca_file for verified clients; other client_auth_type values are called insecure by the toolkit.
- toolkit-reload (REASONED; toolkit): The toolkit rereads web configuration per request; password/certificate changes apply without restart.
- toolkit-clients (REASONED; toolkit, alert, push): Basic auth suits a few users; supply matching credentials/CA to scrapers, pushers and Alertmanager clients, or use client certificates/proxy login.
- alert-bind (REASONED; alert, go): Alertmanager HTTP defaults :9093; HA gossip defaults 0.0.0.0:9094 and needs both TCP and UDP.
- alert-api (DEMONSTRATED; alert, security): Loopback anonymous status, silence creation, reload and pprof succeeded; status carried wildcard CORS.
- alert-auth (DEMONSTRATED; alert, toolkit): Web configuration rejected anonymous silence creation and absent/wrong status passwords; valid status credentials succeeded.
- alert-gossip-off (DEMONSTRATED; alert): An empty --cluster.listen-address disabled both gossip socket protocols in the loopback run.
- alert-gossip-tls (REASONED; alert): HA gossip is plaintext without experimental --cluster.tls-config; restrict it to peers and configure server/client TLS sections.
- alert-proxy (REASONED; security, alert): Proxy mutating routes/CORS to reduce CSRF; send Prometheus traffic to every Alertmanager rather than load-balancing it.
- push-bind (REASONED; push, security): Pushgateway defaults :9091; reachable users can forge trusted series, particularly with honor_labels.
- push-write (DEMONSTRATED; push): Anonymous loopback POST wrote a series visible on metrics; an anonymous DELETE of the group returned 202.
- push-pprof (DEMONSTRATED; push): Anonymous loopback GET /debug/pprof/ returned 200.
- push-pprof-registration (REASONED; push): The pinned source registers /debug/pprof/ outside every flag check.
- push-admin (DEMONSTRATED; push): Admin wipe defaults off; loopback PUT /api/v1/admin/wipe returned 404 without --web.enable-admin-api.
- push-lifecycle (REASONED; push): Lifecycle shutdown defaults off; leave --web.enable-lifecycle and the admin API disabled.
- push-auth (DEMONSTRATED; push, toolkit): With web configuration, anonymous push returned 401 and authenticated push 200.
- push-auth-scope (REASONED; push): The README says web configuration affects all HTTP endpoints: metrics, push API, admin API and web UI.
- jaeger-config (REASONED; jaeger, jaeger-docs): No --config selects in-memory all-in-one; receiver/diagnostic hosts use JAEGER_LISTEN_HOST with localhost fallback.
- jaeger-receivers (REASONED; jaeger): All-in-one maps OTLP 4317/4318, Jaeger 14250/14268 and UDP 6831/6832, Zipkin 9411 and sampling 5778/5779.
- jaeger-diagnostics (REASONED; jaeger): Health 13133, expvar 27777, zpages 27778 and metrics 8888 follow JAEGER_LISTEN_HOST.
- jaeger-loopback (DEMONSTRATED; jaeger): The overridden loopback run showed every listed receiver/diagnostic listener, including UDP, on 127.0.0.1.
- jaeger-image (REASONED; jaeger): The official image sets JAEGER_LISTEN_HOST=0.0.0.0, exposing these listeners to its interfaces and published ports.
- jaeger-query (REASONED; jaeger, jaeger-docs): Query HTTP 16686 and gRPC 16685 default wildcard independently of JAEGER_LISTEN_HOST; bind both explicitly.
- jaeger-mcp (REASONED; jaeger): All-in-one enables ai.mcp on the query HTTP port at /api/ai/mcp/; remove mcp from ai when unused.
- jaeger-open (DEMONSTRATED; jaeger): Anonymous loopback v3 services, UI and MCP initialize returned 200; removed v1 services returned 404, not proof of protection.
- jaeger-basic (DEMONSTRATED; jaeger, basic): Query basicauth/server with htpasswd rejected absent/wrong credentials on services, UI and MCP; correct credentials returned 200.
- jaeger-tls (DEMONSTRATED; jaeger, tls): Query HTTP TLS cert_file/key_file gave HTTPS 401/200 and plaintext 400; inferred wiring was tested locally and needs upgrade retesting.
- jaeger-grpc (REASONED; jaeger, jaeger-docs): Query gRPC auth exists but was not demonstrated; restrict it, authenticate remote collectors separately and front human UI access.
- loki-listeners (REASONED; loki, dskit, go): From source reading and Go's net.Listen documentation, empty TCP listen addresses yield wildcard HTTP 3100 and gRPC 9095; IPv4/IPv6 depends on Go/OS support.
- loki-samples (REASONED; loki): Local sample uses gRPC 9096/auth_enabled false; production Docker config uses wildcard 3100/9095/auth_enabled true.
- memberlist-bind (REASONED; loki, dskit): With the memberlist store, TCP gossip defaults 0.0.0.0:7946; an empty list selects wildcard and an empty list entry is invalid.
- memberlist-label (REASONED; dskit): Cluster labels reject mismatches unless verification is disabled, but matching labels are not credentials; no SecretKey/keyring setting is wired.
- memberlist-updates (REASONED; dskit): Without TLS, reachable matching-label peers can submit KV/ring state subject to codecs/merge rules; disruption is inferred, not demonstrated.
- memberlist-tls (REASONED; dskit, go): TLS defaults off; enabled transport verifies outgoing servers but leaves incoming ClientAuth at NoClientCert, so it is not mutual peer authentication.
- memberlist-policy (REASONED; dskit): Keep tls-insecure-skip-verify false, set expected server name as needed, bind privately and restrict trusted peers even with TLS.
- memberlist-advertise (REASONED; dskit): Advertise address/port affect discovery, not bind; absent overrides derive an address from the first bind and actual port.
- loki-tenants (REASONED; loki, dskit): From source reading, auth_enabled defaults true and requires tenant headers, not credentials; false uses fake, and tenant validation checks syntax/length only.
- loki-grpc-auth (REASONED; dskit, loki): From source reading, default dskit interceptors lack credentials; Loki has tenant exemptions; complete interceptor behaviour was not re-traced.
- loki-push-query (REASONED; loki): From source reading, reachable clients can push/query without credentials subject to tenant headers and ingest/query policies.
- loki-config (REASONED; loki): From source reading, GET /config exposes configuration without a tenant-auth wrapper.
- loki-diagnostics (REASONED; dskit): From source reading, metrics and pprof routes are registered by default without a tenant-auth wrapper.
- loki-maintenance (REASONED; loki): From source reading, ingester flush/shutdown accept GET/POST; prepare_shutdown accepts POST/GET/DELETE, without tenant-auth wrappers.
- loki-delete (REASONED; loki): Non-worker compactor deletion routes require a supported shipper index, retention and a delete-request store; tenant and deletion-policy middleware gate create/list/cancel. After tenant validation, filter-only and filter-and-delete pass, disabled gets 403 and an unrecognized mode gets 400, by source reasoning, not observed responses; admission does not establish eventual deletion.
- loki-delete-mode (REASONED; loki): In v3.7.8, validDeletionLimit parses the tenant's DeletionMode; only the exact strings disabled, filter-only and filter-and-delete parse, and DeleteEnabled is true for the latter two. TenantMiddleware returns 400 for tenant or parsing errors, 403 for disabled, otherwise invokes the handler; this is source reasoning, not observed responses.
- loki-grpc-bridge (REASONED; loki, dskit): From source reading, single-binary ingester RPC and HTTP-over-gRPC expose paths that HTTP-only TLS/proxying does not protect.
- loki-mtls (REASONED; dskit): From source reading, HTTP/gRPC TLS defaults empty and requires a cert/key pair; configure client CA plus RequireAndVerifyClientCert, not CA alone.
- loki-ring (REASONED; loki): This guide's single-binary overlay uses inmemory ring, loopback instance address and replication_factor 1 instead of default 3 (from source reading); check no gossip listener remains.
- loki-internal (REASONED; loki): From source reading, querier worker init gets server gRPC listen address/port, target flags, scheduler ring and worker config; ingester lifecycler listen port is the gRPC listen port.
- loki-internal-dials (REASONED; loki, dskit): Worker and distributor/querier ingester dial sites are traced by source reading; loopback gRPC is this guide's configuration-specific advice; verify advertised/dial addresses, internal worker/ingester success, any compactor calls and live reachability.
- loki-worker-init (REASONED; loki): From source reading, with frontend, scheduler, read and all targets off, InitWorkerService returns no worker if the scheduler ring and both addresses are unset. Otherwise it passes worker config and ring to NewQuerierWorker; outside that standalone case, unset ring/addresses trigger a frontend address using the gRPC port and a nonempty listen address, else 127.0.0.1.
- loki-worker-dials (REASONED; loki): From source reading, workers prefer scheduler ring, scheduler address, then frontend address; AddressAdded calls grpc.DialContext with that client's options, handing it to a processor manager. Frontend Process and scheduler QuerierLoop open on a supplied connection; scheduler results go to the message's FrontendAddress via grpc.Dial with frontend options; success unverified.
- loki-instance-port (REASONED; loki, dskit): From source reading, GetInstancePort returns a positive configured lifecycler port, else the listen port, which Loki sets to the server gRPC listen port or the bound port when that is 0; a configured common ring copies its instance_port into the lifecycler port. The advertised address is the configured address, else one chosen from the configured interfaces.
- loki-ring-kv (REASONED; dskit): From source reading, lifecyclers CAS their entry, with the advertised address, into the ring key at initialization and on heartbeat; KV backends are consul, etcd, process-wide inmemory, memberlist or multi, plus test-only mock.
- loki-ring-reads (REASONED; dskit, loki): From source reading, ring clients read then watch the ring key; distributors take per-stream write sets and queriers, outside partition-ingester queries, the healthy read set via ring.DoUntilQuorum.
- loki-client-pools (REASONED; loki, dskit): From source reading, dskit pools cache one client per address, created on first use. With health checks on (frontend pool; ingester pools by default), one failed check removes a client, as Loki sets no grace period.
- loki-client-pools-discovery (REASONED; loki, dskit): From source reading, ingester pools drop addresses missing from healthy ring entries; the frontend pool has no discovery and checks every 5s. Pooling does not establish effective addresses or successful calls.
- loki-worker-watchers (REASONED; loki, dskit): From source reading, ring watchers take the scheduler ring's key-0 Write set each lookup period and reconcile only non-empty results; DNS watchers poll at that period with no SRV name, report an IP target once and re-resolve host names, with dskit's default port 443 if none is given.
- loki-worker-managers (REASONED; loki): From source reading, addresses that the worker's ring or DNS watchers add get processor managers sharing max concurrency, at least one each; removal notifies the peer and closes the connection.
- loki-request-callers (REASONED; loki): From source reading, push HTTP handlers call PushWithResolver; outside all, write and ingester targets the distributor also registers gRPC Pusher. Kafka writes default off, ingester writes on; Kafka writes need a partition ring and produce to an active partition.
- loki-ingester-query-window (REASONED; loki): From source reading, without query_store_only, Loki queriers query ingesters for selections ending within the ingester store lookback if it is nonzero when the querier module initializes, else query_ingesters_within (0: all); a -1 lookback, documented as infinite, sends every selection to ingesters and none directly to the store.
- loki-ingester-lookback-all (REASONED; loki, dskit): From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, and the active or next schema period uses a boltdb-shipper or TSDB index, the store module, initialized before the querier module that depends on it, turns a configured 0 ingester store lookback into a computed minimum that replaces query_ingesters_within; without all, 0 stays 0.
- loki-ingester-lookback-minimum (REASONED; loki): From source reading, Loki's computed minimum ingester store lookback is the ingester's maximum chunk age plus 21 minutes (a 15-minute boltdb shard period, 1-minute index upload interval and 5-minute buffer), the index cache validity and three resync intervals of the active or next period's shipper index.
- loki-ingester-lookback-store (REASONED; loki): From source reading, Loki's query_store_max_look_back_period flag help limits it to boltdb-shipper/TSDB indexes with the filesystem object store; the all target's boltdb-shipper/TSDB store setup rejects a nonzero value with any other object store.
- loki-ingester-store-all (REASONED; loki, dskit): From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, and the active or next schema period uses a boltdb-shipper or TSDB index, the ingester, initialized after the store module it depends on, also queries the store for the log and sample selections it serves, except when the lookback-adjusted start is after the selection end.
- loki-ingester-store-range (REASONED; loki): From source reading, when a Loki ingester queries the store for a log or sample selection, it moves the start of the store request up to now minus a positive store lookback, leaves it unchanged for -1 and other negative values, and skips the store query when that adjusted start is after the selection end.
- loki-ingester-lookback-bounds (REASONED; loki): From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, its boltdb-shipper or TSDB store setup with the filesystem object store rejects a positive query_store_max_look_back_period below the computed minimum and passes -1 and any other negative value through calculateMaxLookBack unchanged.
- loki-querier-store-window (REASONED; loki): From source reading, when the ingester store lookback that the Loki querier module copies at initialization is positive, the querier limits its own store query to the part of a selection before now minus that lookback, querying only ingesters when the selection starts after that point; exactly -1 instead skips the store and sends the whole selection to ingesters.
- loki-querier-store-negative (REASONED; loki): From source reading, when the ingester store lookback that the Loki querier module copies at initialization is negative but not -1, now minus that lookback lies in the future, and the querier sets the end of any store request to that point without clamping it to the selection end, unlike the Loki ingester, which leaves its store request start unchanged for every negative lookback.
- loki-querier-ingester-inverted (REASONED; loki): From source reading, if a Loki selection passing request validation reaches interval construction and the querier's initialization copy of the ingester store lookback is negative but not -1 with now minus it past the selection end, the querier starts its ingester interval there, ends it at the selection end without an order check and sends it to its ingester querier unless query_store_only is set.
- loki-ingester-inverted-call (REASONED; loki): From source reading, Loki's ingester querier passes the log or sample request it receives, including an inverted interval from the querier, to the gRPC Query or QuerySample call of each ingester it queries, and the ingester module registers the ingester, or a wrapper that Go code embedding Loki may set, as the Querier service whose generated handlers decode the request and call those methods.
- loki-ingester-inverted-store (REASONED; loki): From source reading, without a configured wrapper, a Loki ingester serving a log or sample request whose start is after its end makes no store query for it, whatever its store lookback: its store-request code moves a start only later, to now minus a positive lookback, and returns no store request when that adjusted start is after the end.
- loki-ingester-inverted-memory (REASONED; loki): From source reading, without a configured wrapper, a Loki ingester's in-memory log or sample query looks up streams in its index at the request start and, for each matching stream, skips every chunk unless the chunk's bounds start no later than the request end and end no earlier than the request start, so for an inverted interval it keeps only chunks covering the span from that end to that start.
- loki-ingester-inverted-lookup (REASONED; loki): From source reading, a Loki v3.7.8 ingester adds every stream to each index it builds, and its index lookup uses an inverted interval's start only to pick the index of the schema period containing it, for a future start the latest period starting at or before it; the lookup matches label matchers and shard without reading time, so the interval's order causes no lookup error.
- loki-ingester-inverted-iterators (REASONED; loki): From source reading, Loki v3.7.8's ingester stream, chunk and head-block iterators neither swap nor clamp an inverted interval: they read a chunk, block or head block only if it starts no later than the interval's end and ends no earlier than its start, and the ordered head block's log iterator drops each entry before the start or at or after the end.
- loki-ingester-inverted-time-filter (REASONED; loki): From source reading, Loki v3.7.8's chunk time-range filters, used for block entries in both directions, the head block in forward log queries and all sample queries, skip entries before the start but accept one timestamped exactly at it before testing the end; in this guide's assessment, they pass only such entries for an inverted interval.
- loki-push-future-bound (REASONED; loki): From source reading, Loki v3.7.8's distributor validates each pushed entry against a context built from time.Now(): a timestamp strictly newer than now plus the tenant's creation_grace_period (default 10m) is rejected as too far in the future, so one exactly at that bound passes. reject_old_samples (default true) rejects entries older than now minus reject_old_samples_max_age (default 7d).
- loki-ingester-push-validation (REASONED; loki): From source reading, Loki v3.7.8's ingester gRPC push chain compares timestamps with stream state and schema configuration, never the clock, with no future timestamp bound. Unordered writes (default true) drop entries below the stream's highest timestamp minus half max_chunk_age (default 2h); ordered appends reject those older than the head block's newest or, head empty, the last block's maximum.
- loki-ingester-inverted-hold (REASONED; loki): From the cited source reading without a Loki run, in this guide's assessment an ingester can hold an entry dated exactly at the inverted interval's future start when the negative lookback's magnitude is at most creation_grace_period, on one clock, grace period unchanged. For a larger magnitude a direct ingester gRPC push can; Kafka consumer pushes and duplicate-timestamp shifts are not ruled out.
- loki-ingester-inverted-unordered (REASONED; loki): From source reading, Loki v3.7.8's backward log queries do not time-filter a chunk's head block, and the unordered head block queries its vendored go-datastructures v1.1.7 range tree from an interval's start to one nanosecond before its end, both inclusive. For an inverted interval that query returns no entry, so the head block yields nothing.
- loki-ingester-empty-send (REASONED; loki): From source reading, when Loki v3.7.8's ingester Query or QuerySample code gets an error-free iterator yielding nothing, it sends one empty batch with query statistics and warnings unless the request context is already done, failing only on a Send error other than context.Canceled. The ingester querier's per-ingester iterator records those, yields nothing and ends cleanly at the stream's end.
- loki-querier-inverted-merge (REASONED; loki): From source reading, a Loki v3.7.8 querier merges the ingester querier's per-ingester iterators for a log or sample selection with the iterator of any store query it makes for that selection, which it skips when query_ingester_only is set or it builds no store interval; a log selection with only one iterator gets that iterator unmerged.
- loki-ingester-wrapper-search (REASONED; loki): From source reading, a word search for Wrapper in Loki v3.7.8's pkg, cmd, integration, tools and clients trees finds only Ingester.Wrapper's declaration (no YAML key), its one-method Wrap interface and initIngester's nil check and Wrap call, besides a code comment and stylesheet source maps; nothing there sets it, and initIngester registers Wrap's result only when it is set.
- loki-querier-ingester-inverted-result (REASONED; loki): Source reading of Loki's querier, ingester querier and ingester query code, with no Loki run, does not establish what they return for the inverted ingester interval a negative store lookback besides -1 yields: in this guide's assessment ingesters can hold entries dated exactly at its start when the lookback's magnitude is within the grace period, on one clock, grace unchanged; no run observed it.
- loki-internal-server (REASONED; loki, dskit): From source reading, Run initializes target modules and starts them together. internal_server is off by default; when enabled it precedes Server and its HTTP listener defaults to localhost:3101.
- loki-internal-server-grpc (REASONED; loki, dskit, go): From source reading and Go's net.Listen documentation, the internal server's flags register no gRPC address or port, so by inference, when enabled, unless YAML sets them, dskit opens an any-address gRPC listener on an OS-chosen port carrying the HTTP bridge; not observed.
- loki-internal-routes (REASONED; loki): When enabled, the internal server's HTTP router serves routes including /ready and buildinfo and, when their modules run, /ring, /memberlist and the compactor handler prefix; these are source registrations, not observed responses.
- loki-grpc-tls (REASONED; dskit, loki): Inferred from dskit's server TLS source, gRPC TLS requires compatible TLS on every internal client; local users can reach plaintext loopback and, per Loki's authentication documentation, mTLS does not supply tenant headers.
- loki-proxy (REASONED; loki): An authenticating proxy must overwrite X-Scope-OrgID with its identity and be the only caller that can reach Loki.
- verify-inventory (REASONED; node, alert, push, jaeger, dskit): Inventory every TCP/UDP listener; wildcard defaults, all Loki listeners and off-host isolation were not observed.
- verify-external (REASONED; security, toolkit, jaeger-docs): External 200 exposes unauthenticated HTTP; HTTPS 401 shows auth, not isolation. Confirm connection failures and a permitted positive control.
- verify-loki (REASONED; loki, curl): A tenant-header rejection is not authentication; repeat with an arbitrary X-Scope-OrgID and test both families, gRPC and internal RPCs.
- verify-basic (DEMONSTRATED; node, push, alert, jaeger, toolkit): Loopback HTTPS GETs on node/Pushgateway metrics, Alertmanager status and Jaeger v3 services gave no-credential 401 and credentialed 200.
- verify-loki-mtls (REASONED; loki, dskit): Authorized HTTP mTLS should succeed, untrusted/missing client certs fail handshake and plaintext fail; no Loki listener/TLS run occurred.
- verify-secret (REASONED; toolkit, curl): Basic-auth stdin closes argv exposure only; shell history, tracing and your own account's view of the process can still leak the password.

````json
{
  "schema": 1,
  "checked": "2026-10-20",
  "documentation_checked": "2026-09",
  "body_sha256": "21eee118d39e6a462edbfc64a89d6fa26018127a2cb88564b8d54385ef62a54a",
  "components": {
    "node": {
      "name": "node_exporter",
      "basis": "v1.12.1",
      "sources": {
        "s9cc780c8cd13": "https://github.com/prometheus/node_exporter/blob/v1.12.1/README.md",
        "s896899f5a500": "https://github.com/prometheus/node_exporter/blob/v1.12.1/node_exporter.go"
      }
    },
    "alert": {
      "name": "Alertmanager",
      "basis": "v0.34.1",
      "sources": {
        "s0fd66cba968e": "https://github.com/prometheus/alertmanager/blob/v0.34.1/README.md",
        "s120d6ecf3fcd": "https://github.com/prometheus/alertmanager/blob/v0.34.1/docs/https.md",
        "s2f25ecba24e9": "https://github.com/prometheus/alertmanager/blob/v0.34.1/docs/management_api.md"
      }
    },
    "push": {
      "name": "Pushgateway",
      "basis": "v1.11.3",
      "sources": {
        "s5c9f9745f42d": "https://github.com/prometheus/pushgateway/blob/v1.11.3/README.md",
        "s17fa4021d868": "https://github.com/prometheus/pushgateway/blob/v1.11.3/main.go"
      }
    },
    "jaeger": {
      "name": "Jaeger",
      "basis": "v2.21.0",
      "sources": {
        "s5619bba2be59": "https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/internal/all-in-one.yaml",
        "sc6f47d82b947": "https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/internal/extension/jaegerquery/internal/flags.go",
        "s15354f575fde": "https://github.com/jaegertracing/jaeger/blob/v2.21.0/ports/ports.go",
        "sb0d71eec9578": "https://github.com/jaegertracing/jaeger/blob/v2.21.0/cmd/jaeger/Dockerfile",
        "s9cba9ed883db": "https://github.com/jaegertracing/jaeger/releases/tag/v2.21.0"
      }
    },
    "loki": {
      "name": "Loki",
      "basis": "v3.7.8",
      "sources": {
        "s70975c2655fa": "https://github.com/grafana/loki/blob/v3.7.8/docs/sources/operations/authentication.md",
        "s303881c903ca": "https://github.com/grafana/loki/blob/v3.7.8/docs/sources/reference/loki-http-api.md",
        "sd13fa86b20d0": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L150-L162",
        "s8f06ddfa5291": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/common/common.go",
        "s8cf14a90ec61": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L162-L174",
        "s924fd8ffd310": "https://github.com/grafana/loki/blob/v3.7.8/cmd/loki/loki-local-config.yaml#L1-L16",
        "s9fd7d8bd80e3": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L241-L269",
        "s985dfb0ea97c": "https://github.com/grafana/loki/blob/v3.7.8/production/docker/config/loki.yaml#L1-L8",
        "s057e686b00bb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L495-L509",
        "sb5e56f0d6348": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L208-L222",
        "s9f316e1a5fef": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L399-L422",
        "s39c270ed878c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1307-L1378",
        "sbe0aa939a44d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L533-L540",
        "sc2b013001317": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L751-L790",
        "s4f3a19f7f08c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1866-L1869",
        "s3d51e1213e70": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1880-L1883",
        "s38c1e77fe01e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1899-L1908",
        "s1f38431776f2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1935-L1952",
        "s765907d2b4ee": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L571-L580",
        "sf3955ae90da4": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L734-L740",
        "sfb3d52071e7c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L193-L248",
        "scf12ae06cdc4": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L373-L390",
        "s0ce56d38618e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L271-L272",
        "s970473c2dcdb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1130-L1138",
        "s6b2f01173a97": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1241-L1262",
        "s44e7547da37d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2532-L2561",
        "s33f320afa73a": "https://github.com/grafana/loki/blob/v3.7.8/go.mod#L55",
        "s3ff15746c2c9": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/tenant_request_handler.go#L10-L34",
        "s14f65483dd4d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L49-L110",
        "s0bde2f8abe97": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L134-L190",
        "saf8f37e04b71": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/request_handler.go#L259-L303",
        "s6feced2aa907": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L450-L453",
        "se1440b6eb37a": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L1128-L1132",
        "s79ea72562a9f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L117-L182",
        "s634e6599df5e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L222-L245",
        "s10b95cd4cab8": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L297-L310",
        "s82a976e6b93c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/frontend_processor.go#L49-L80",
        "s47c05209cd31": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L87-L164",
        "s18cd3a035b38": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L183-L244",
        "s1d59e1184191": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L246-L335",
        "s5b3705652693": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L57",
        "s9d106cc379de": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/client/client.go#L65-L91",
        "s8b3d57f01355": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L358-L365",
        "s88661a4514b3": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L58-L74",
        "sb0ae3e30f690": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L187-L220",
        "s074f98761044": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L249-L253",
        "s00520a857797": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L344",
        "s7b1d1f183610": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L231-L236",
        "sc5574f33c47c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L900-L921",
        "s4554d31a5d15": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1216-L1231",
        "s51e0f640a169": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L879-L893",
        "sa19fa92e5d02": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1258-L1271",
        "sfc4788e520b8": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L346",
        "s7786b9105acc": "https://raw.githubusercontent.com/grafana/loki/v3.7.8/pkg/util/fakeauth/fake_auth.go",
        "sae57ccde5dc6": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletion/util.go#L24-L36",
        "s86b57bdedee7": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletionmode/mode.go#L15-L24",
        "sc37c5a5a63b4": "https://github.com/grafana/loki/blob/v3.7.8/pkg/compactor/deletionmode/mode.go#L38-L56",
        "s99ac9c7561c2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker_service.go#L18-L42",
        "s61ecb8af773e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker_service.go#L56-L112",
        "sde741c787b71": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/scheduler_processor.go#L37-L59",
        "seea78f4f5adb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L224-L230",
        "sb7c90a61ae40": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L562-L664",
        "scf7d98f51caa": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L750-L761",
        "sf4c3469d7ee1": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L816-L867",
        "sd4f78f9689f6": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L923-L941",
        "sd46d55125044": "https://github.com/grafana/loki/blob/v3.7.8/pkg/server/internal_server.go#L10-L33",
        "sf19909de84b7": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L245-L268",
        "s309318e5a59c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2646-L2664",
        "s319f6b7b5340": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L276-L279",
        "s543d4de072bb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/http.go#L28-L38",
        "s3d6bf0891af0": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/http.go#L151",
        "sd28855900a87": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L552-L558",
        "sa59140ca5c4c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L127-L136",
        "s9a87cce410e5": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L293-L308",
        "s846c370c416f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L860-L867",
        "s51bcdc31e69d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L1296-L1326",
        "s8f53a03e764f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L77-L81",
        "sdc0d0e6ad95d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L176-L198",
        "s10870cc18ddc": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L242-L261",
        "scba306dcdc0c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L302-L304",
        "s2e89e4162342": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L168-L186",
        "s5ab3c47cb0fc": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/clientpool/ingester_client_pool.go#L30-L46",
        "sb8f98248ef1a": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/processor_manager.go#L35-L89",
        "scc6c338ac167": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L157-L196",
        "s6a02e080cabb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/worker/worker.go#L247-L295",
        "s02c83c5d9dda": "https://github.com/grafana/loki/blob/v3.7.8/pkg/util/ring_watcher.go#L14-L117",
        "sc26dc660fa21": "https://github.com/grafana/loki/blob/v3.7.8/pkg/util/dns_watcher.go#L30-L83",
        "s21675bf85b75": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/clientpool/ingester_client_pool.go#L26",
        "s529cd9a944d9": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/intervals.go#L9-L104",
        "sf2a4759294c3": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L540-L542",
        "s23d3deffe096": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L163",
        "s86fc597288e2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L200-L212",
        "se3f01b0b8f64": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L263-L272",
        "s23599866ad90": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/intervals.go#L23-L25",
        "se82f6c344ae2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L910-L918",
        "sa4685cf34525": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1060-L1112",
        "s937747b2754f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2573-L2588",
        "s362660480c60": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2607-L2639",
        "s7e25cfebaa93": "https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/stores/shipper/indexshipper/boltdb/table.go#L27",
        "s425030dbbf09": "https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/stores/shipper/indexshipper/shipper.go#L45",
        "s086d15529b4c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/storage/config/schema_config.go#L345-L378",
        "sc311d25f20e8": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L770-L771",
        "s3e8d9a35ec33": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L943-L947",
        "s9a971cf72e10": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L387-L389",
        "s21c205d034b9": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1102-L1119",
        "sd6184d6a8a46": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1175-L1191",
        "s51ab6a62a6bd": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1640-L1660",
        "sb5b69814231d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L158-L169",
        "s23b8da8ac6be": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L224-L235",
        "s61e16a1ac1f0": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/ingester_querier.go#L234-L264",
        "sf253d44e375f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L768-L773",
        "sfb58949fa28c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/logproto/logproto.pb.go#L6166-L6193",
        "se2f420694eb9": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1093-L1100",
        "se913abf5bf85": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1160-L1168",
        "se1f0d83f115c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L519-L532",
        "s2a80da1a36e8": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L587-L610",
        "sadb084375296": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L962-L975",
        "s0b40d7d25a3f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L588-L594",
        "se34169c8b133": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L635-L641",
        "sb6c261fe940d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1814-L1816",
        "s81d8d94c3cea": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1928-L1933",
        "sd5967b880c33": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L152-L163",
        "sc87fdc20cb58": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L312-L314",
        "s11cbfc4fcf89": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L404-L405",
        "sf674ae88a12c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/multi.go#L26-L73",
        "s6bc46c6500c2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/multi.go#L84-L117",
        "s140b0adc6723": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/index.go#L159-L183",
        "s19918b3b217b": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/index/bitprefix.go#L131-L169",
        "se3affc4818e6": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L601-L607",
        "s693d6421c2f0": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L648-L650",
        "sd5181aa115e4": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1005-L1087",
        "scc80bfb6f547": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1090-L1147",
        "s05d6c5fc01a2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1310-L1328",
        "s291928ddc0b1": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L1380-L1397",
        "s33683997e787": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L185-L210",
        "s69faadc4a015": "https://github.com/grafana/loki/blob/v3.7.8/go.mod#L19",
        "s18bc063957e1": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L69-L75",
        "sf185bec82940": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/unordered.go#L260-L310",
        "s015710936d80": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/interface.go#L38-L47",
        "saf4f45f2d5c7": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/orderedtree.go#L259-L263",
        "sd8ad9fae3598": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/orderedtree.go#L180-L225",
        "sd82568caaafc": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/ordered.go#L25-L30",
        "s996300b7bdcf": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/ordered.go#L81-L98",
        "s9a133bb92cd3": "https://github.com/grafana/loki/blob/v3.7.8/vendor/github.com/Workiva/go-datastructures/rangetree/entries.go#L21-L45",
        "s0dbdc425ddbb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L478-L509",
        "s05d6bac1c352": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L681-L716",
        "s76e4e638e936": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L1104-L1143",
        "s5732ba30414b": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L1145-L1179",
        "sa1a1efa48033": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1121-L1129",
        "s00b4ce2d9a6a": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1193-L1195",
        "s9f438349ea61": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L681-L716",
        "sf89b7c829a53": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L718-L753",
        "s6c74d0f4adb3": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/entry_iterator.go#L362-L388",
        "sdf678b8f143f": "https://github.com/grafana/loki/blob/v3.7.8/pkg/iter/sample_iterator.go#L480-L505",
        "s2d763a8942ef": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L213-L216",
        "s6f04b102b391": "https://github.com/grafana/loki/blob/v3.7.8/pkg/querier/querier.go#L274",
        "s24cd2d4a2bce": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L126-L127",
        "sd7efa15100d2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L210-L212",
        "sa66ae191eb87": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L589-L592",
        "s883c99aaf259": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L690-L695",
        "s03a9eb3c1800": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/validator.go#L66-L71",
        "s7be82cdc7279": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/validator.go#L94-L113",
        "sc1c59c06ac21": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L327",
        "s9acb77638396": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L351-L354",
        "s7e5e17b46be6": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L751-L754",
        "sfc254eaeb3c3": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L362",
        "s19e37d99684b": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L162",
        "sa5963eda217e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L1001-L1024",
        "s02173d6919e0": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L231-L261",
        "s6d778dd956ad": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L186-L247",
        "s3683552f47e7": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L401-L461",
        "s48eb47bcb74e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/stream.go#L339-L384",
        "s1d09c7438f6c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L186-L200",
        "s93219a6da66c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L749-L758",
        "s9c1fabf63f70": "https://github.com/grafana/loki/blob/v3.7.8/pkg/distributor/distributor.go#L686",
        "se9b1d3173a5a": "https://github.com/grafana/loki/blob/v3.7.8/pkg/validation/limits.go#L328",
        "s9044377b42e9": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/ingester.go#L395",
        "sd2ef570a75c2": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/kafka_consumer.go#L53-L71",
        "sd01827189b1e": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/kafka_consumer.go#L150-L159",
        "s6259f9f6561b": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L316",
        "sef39e72a9288": "https://github.com/grafana/loki/blob/v3.7.8/pkg/ingester/instance.go#L423-L440",
        "s631c8b46da80": "https://github.com/grafana/loki/blob/v3.7.8/pkg/chunkenc/memchunk.go#L872-L874"
      }
    },
    "jaeger-docs": {
      "name": "Jaeger documentation",
      "basis": "4d150659ee4ed3ccc69253ec77c368392f59e625",
      "sources": {
        "s2c0a96684979": "https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/configuration.md",
        "s4969c5ffaa59": "https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/security.md"
      }
    },
    "toolkit": {
      "name": "Exporter toolkit",
      "basis": "v0.17.1",
      "sources": {
        "sbb86207a38e5": "https://github.com/prometheus/exporter-toolkit/blob/v0.17.1/docs/web-configuration.md"
      }
    },
    "security": {
      "name": "Prometheus security model",
      "basis": "a0d29881382ad1ea20597d34fc4229984b326576",
      "sources": {
        "s3ffe42e99660": "https://github.com/prometheus/docs/blob/a0d29881382ad1ea20597d34fc4229984b326576/docs/operating/security.md"
      }
    },
    "tls": {
      "name": "OpenTelemetry configtls",
      "basis": "v1.66.0",
      "sources": {
        "s11d519172812": "https://github.com/open-telemetry/opentelemetry-collector/blob/cd3455cf3a7f672208140b1ebb1581c542b2b0ed/config/configtls/README.md"
      }
    },
    "basic": {
      "name": "OpenTelemetry basicauth extension",
      "basis": "v0.160.0",
      "sources": {
        "s881d8805b6c6": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.160.0/extension/basicauthextension/README.md"
      }
    },
    "dskit": {
      "name": "dskit",
      "basis": "8d1c6d34bb5a42b04caa982d68403c5a643bb742",
      "sources": {
        "sb19d54a19636": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L189-L212",
        "s0dc9a01e591a": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L69-L78",
        "s7848c6311aee": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L309-L332",
        "sd35a28be4391": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L357-L395",
        "se0830c9ea1b5": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L411-L412",
        "s38beab6892ea": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L433-L468",
        "s761b46738198": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L577-L583",
        "s5fd7b12bfcf1": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L673-L681",
        "s3634557bb838": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/middleware/http_auth.go#L13-L23",
        "saf57a4cbc682": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/middleware/grpc_auth.go#L36-L57",
        "s1ca109a7a016": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/tenant/tenant.go#L85-L99",
        "s23d81aeedf07": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L41-L86",
        "s4d546b0d82d4": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L133-L197",
        "s251174df8783": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/tcp_transport.go#L394-L451",
        "s052e8107edad": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L229-L232",
        "scf57b6b1f148": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L457-L520",
        "s675104c4819c": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/crypto/tls/tls.go#L27-L64",
        "s99e7e34182f1": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/crypto/tls/tls.go#L86-L175",
        "s69c68f3d3e6a": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1383-L1470",
        "sb0955f4c2ebd": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcclient/grpcclient.go#L125-L134",
        "s74daabf65e98": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L189-L229",
        "s172528a7c1bf": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L709-L723",
        "s433134153d1d": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L778-L781",
        "s1786ff0496f6": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L541-L544",
        "sc8780cfc9e85": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L681",
        "s1b539b8100a3": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1577-L1672",
        "sd7b8bf6bbca6": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/util.go#L16-L39",
        "sa7d343f48dc5": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L97-L100",
        "s04a225bbac7b": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L602-L606",
        "s59c2aa3eb502": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L697-L725",
        "sbd4dba4be513": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/lifecycler.go#L950-L973",
        "s8145c89a12ee": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/client.go#L137-L176",
        "sf68c98707951": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L319-L334",
        "s05d533c42177": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L379-L411",
        "s16cda83ea984": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L497-L544",
        "s48b2d449a388": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/ring.go#L711-L792",
        "s2a947b05938f": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/replication_set.go#L157-L316",
        "s0b92cab27eeb": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L43-L49",
        "sa35a10f1fa8b": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L95-L165",
        "s6224eeb93eb9": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/pool.go#L238-L318",
        "s79f868b8ee48": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/ring/client/ring_service_discovery.go#L9-L25",
        "s7077c6b93703": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L76-L171",
        "s77d6a067cd74": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L191-L268",
        "sfbd1b87a9a0c": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/grpcutil/dns_resolver.go#L18-L36",
        "s96305c045ce4": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/modules/modules.go#L116-L156"
      }
    },
    "go": {
      "name": "Go documentation",
      "basis": "unknown",
      "sources": {
        "sd3b3c1c431ec": "https://pkg.go.dev/crypto/tls#ClientAuthType",
        "s37204ff1b27c": "https://pkg.go.dev/net#Listen"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s5e1383feef7d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79",
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md",
        "s82a34ee18632": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md"
      }
    }
  },
  "claims": {
    "node-bind": {"text": "node_exporter defaults to :9100 on all interfaces; private binds are required.", "components": ["node", "go"], "sources": ["node:s9cc780c8cd13", "node:s896899f5a500", "go:s37204ff1b27c"], "status": "REASONED"},
    "node-open": {"text": "Unconfigured loopback metrics and pprof both returned 200 without credentials.", "components": ["node"], "sources": ["node:s896899f5a500"], "status": "DEMONSTRATED", "evidence": "On a loopback run, both paths returned `200` with no credentials."},
    "toolkit-config": {"text": "--web.config.file enables TLS and bcrypt Basic auth across HTTP paths; the format is experimental and not every exporter uses it.", "components": ["toolkit", "node", "alert", "push"], "sources": ["toolkit:sbb86207a38e5", "node:s9cc780c8cd13", "alert:s120d6ecf3fcd", "push:s5c9f9745f42d"], "status": "REASONED"},
    "node-tls": {"text": "Loopback HTTP returned 400; HTTPS metrics/pprof rejected absent credentials and accepted correct ones.", "components": ["node", "toolkit"], "sources": ["node:s896899f5a500", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "HTTPS without credentials got `401` on both `/metrics` and `/debug/pprof/`, and HTTPS with the right credentials got `200`."},
    "toolkit-mtls": {"text": "Use RequireAndVerifyClientCert with client_ca_file for verified clients; other client_auth_type values are called insecure by the toolkit.", "components": ["toolkit"], "sources": ["toolkit:sbb86207a38e5"], "status": "REASONED"},
    "toolkit-reload": {"text": "The toolkit rereads web configuration per request; password/certificate changes apply without restart.", "components": ["toolkit"], "sources": ["toolkit:sbb86207a38e5"], "status": "REASONED"},
    "toolkit-clients": {"text": "Basic auth suits a few users; supply matching credentials/CA to scrapers, pushers and Alertmanager clients, or use client certificates/proxy login.", "components": ["toolkit", "alert", "push"], "sources": ["toolkit:sbb86207a38e5", "alert:s120d6ecf3fcd", "push:s5c9f9745f42d"], "status": "REASONED"},
    "alert-bind": {"text": "Alertmanager HTTP defaults :9093; HA gossip defaults 0.0.0.0:9094 and needs both TCP and UDP.", "components": ["alert", "go"], "sources": ["alert:s0fd66cba968e", "go:s37204ff1b27c"], "status": "REASONED"},
    "alert-api": {"text": "Loopback anonymous status, silence creation, reload and pprof succeeded; status carried wildcard CORS.", "components": ["alert", "security"], "sources": ["alert:s2f25ecba24e9", "security:s3ffe42e99660"], "status": "DEMONSTRATED", "evidence": "`GET /api/v2/status` returned `200`, `POST /api/v2/silences` created a silence and returned `200`, and `POST /-/reload` returned `200`. `GET /debug/pprof/` also returned `200`."},
    "alert-auth": {"text": "Web configuration rejected anonymous silence creation and absent/wrong status passwords; valid status credentials succeeded.", "components": ["alert", "toolkit"], "sources": ["alert:s120d6ecf3fcd", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "the loopback runs returned `401` to an unauthenticated silence creation and to an unauthenticated or wrong-password status read, and `200` to an authenticated status read."},
    "alert-gossip-off": {"text": "An empty --cluster.listen-address disabled both gossip socket protocols in the loopback run.", "components": ["alert"], "sources": ["alert:s0fd66cba968e"], "status": "DEMONSTRATED", "evidence": "On a loopback run with it empty, Alertmanager held no TCP or UDP socket on 9094."},
    "alert-gossip-tls": {"text": "HA gossip is plaintext without experimental --cluster.tls-config; restrict it to peers and configure server/client TLS sections.", "components": ["alert"], "sources": ["alert:s120d6ecf3fcd"], "status": "REASONED"},
    "alert-proxy": {"text": "Proxy mutating routes/CORS to reduce CSRF; send Prometheus traffic to every Alertmanager rather than load-balancing it.", "components": ["security", "alert"], "sources": ["security:s3ffe42e99660", "alert:s0fd66cba968e"], "status": "REASONED"},
    "push-bind": {"text": "Pushgateway defaults :9091; reachable users can forge trusted series, particularly with honor_labels.", "components": ["push", "security"], "sources": ["push:s5c9f9745f42d", "security:s3ffe42e99660"], "status": "REASONED"},
    "push-write": {"text": "Anonymous loopback POST wrote a series visible on metrics; an anonymous DELETE of the group returned 202.", "components": ["push"], "sources": ["push:s5c9f9745f42d"], "status": "DEMONSTRATED", "evidence": "an unauthenticated `POST /metrics/job/demo` returned `200` and the series appeared on `/metrics`. An unauthenticated `DELETE` of the group returned `202`."},
    "push-pprof": {"text": "Anonymous loopback GET /debug/pprof/ returned 200.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "DEMONSTRATED", "evidence": "it answered `200`"},
    "push-pprof-registration": {"text": "The pinned source registers /debug/pprof/ outside every flag check.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "REASONED"},
    "push-admin": {"text": "Admin wipe defaults off; loopback PUT /api/v1/admin/wipe returned 404 without --web.enable-admin-api.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "DEMONSTRATED", "evidence": "`PUT /api/v1/admin/wipe` returned `404` by default."},
    "push-lifecycle": {"text": "Lifecycle shutdown defaults off; leave --web.enable-lifecycle and the admin API disabled.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "REASONED"},
    "push-auth": {"text": "With web configuration, anonymous push returned 401 and authenticated push 200.", "components": ["push", "toolkit"], "sources": ["push:s5c9f9745f42d", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "an unauthenticated push returned `401` and an authenticated one returned `200`."},
    "push-auth-scope": {"text": "The README says web configuration affects all HTTP endpoints: metrics, push API, admin API and web UI.", "components": ["push"], "sources": ["push:s5c9f9745f42d"], "status": "REASONED"},
    "jaeger-config": {"text": "No --config selects in-memory all-in-one; receiver/diagnostic hosts use JAEGER_LISTEN_HOST with localhost fallback.", "components": ["jaeger", "jaeger-docs"], "sources": ["jaeger:s5619bba2be59", "jaeger-docs:s2c0a96684979"], "status": "REASONED"},
    "jaeger-receivers": {"text": "All-in-one maps OTLP 4317/4318, Jaeger 14250/14268 and UDP 6831/6832, Zipkin 9411 and sampling 5778/5779.", "components": ["jaeger"], "sources": ["jaeger:s5619bba2be59", "jaeger:s15354f575fde"], "status": "REASONED"},
    "jaeger-diagnostics": {"text": "Health 13133, expvar 27777, zpages 27778 and metrics 8888 follow JAEGER_LISTEN_HOST.", "components": ["jaeger"], "sources": ["jaeger:s5619bba2be59", "jaeger:s15354f575fde"], "status": "REASONED"},
    "jaeger-loopback": {"text": "The overridden loopback run showed every listed receiver/diagnostic listener, including UDP, on 127.0.0.1.", "components": ["jaeger"], "sources": ["jaeger:s5619bba2be59"], "status": "DEMONSTRATED", "evidence": "the loopback run showed each of them, UDP included, on 127.0.0.1"},
    "jaeger-image": {"text": "The official image sets JAEGER_LISTEN_HOST=0.0.0.0, exposing these listeners to its interfaces and published ports.", "components": ["jaeger"], "sources": ["jaeger:sb0d71eec9578"], "status": "REASONED"},
    "jaeger-query": {"text": "Query HTTP 16686 and gRPC 16685 default wildcard independently of JAEGER_LISTEN_HOST; bind both explicitly.", "components": ["jaeger", "jaeger-docs"], "sources": ["jaeger:sc6f47d82b947", "jaeger:s15354f575fde", "jaeger-docs:s2c0a96684979"], "status": "REASONED"},
    "jaeger-mcp": {"text": "All-in-one enables ai.mcp on the query HTTP port at /api/ai/mcp/; remove mcp from ai when unused.", "components": ["jaeger"], "sources": ["jaeger:s5619bba2be59", "jaeger:sc6f47d82b947"], "status": "REASONED"},
    "jaeger-open": {"text": "Anonymous loopback v3 services, UI and MCP initialize returned 200; removed v1 services returned 404, not proof of protection.", "components": ["jaeger"], "sources": ["jaeger:s9cba9ed883db", "jaeger:sc6f47d82b947"], "status": "DEMONSTRATED", "evidence": "`GET /api/v3/services` returned `200`, the UI at `/` returned `200`, and an MCP `initialize` POST to `/api/ai/mcp/` returned `200`."},
    "jaeger-basic": {"text": "Query basicauth/server with htpasswd rejected absent/wrong credentials on services, UI and MCP; correct credentials returned 200.", "components": ["jaeger", "basic"], "sources": ["jaeger:sc6f47d82b947", "basic:s881d8805b6c6"], "status": "DEMONSTRATED", "evidence": "`/api/v3/services`, the UI and the MCP endpoint each returned `401` without credentials and `401` with a wrong password. Each returned `200` with the right credentials."},
    "jaeger-tls": {"text": "Query HTTP TLS cert_file/key_file gave HTTPS 401/200 and plaintext 400; inferred wiring was tested locally and needs upgrade retesting.", "components": ["jaeger", "tls"], "sources": ["jaeger:sc6f47d82b947", "tls:s11d519172812"], "status": "DEMONSTRATED", "evidence": "HTTPS without credentials got `401`, HTTPS with them `200`, and plain HTTP `400`"},
    "jaeger-grpc": {"text": "Query gRPC auth exists but was not demonstrated; restrict it, authenticate remote collectors separately and front human UI access.", "components": ["jaeger", "jaeger-docs"], "sources": ["jaeger:sc6f47d82b947", "jaeger-docs:s4969c5ffaa59"], "status": "REASONED"},
    "loki-listeners": {"text": "From source reading and Go's net.Listen documentation, empty TCP listen addresses yield wildcard HTTP 3100 and gRPC 9095; IPv4/IPv6 depends on Go/OS support.", "components": ["loki", "dskit", "go"], "sources": ["loki:s9fd7d8bd80e3", "dskit:sb19d54a19636", "dskit:s7848c6311aee", "go:s37204ff1b27c"], "status": "REASONED"},
    "loki-samples": {"text": "Local sample uses gRPC 9096/auth_enabled false; production Docker config uses wildcard 3100/9095/auth_enabled true.", "components": ["loki"], "sources": ["loki:s924fd8ffd310", "loki:s985dfb0ea97c"], "status": "REASONED"},
    "memberlist-bind": {"text": "With the memberlist store, TCP gossip defaults 0.0.0.0:7946; an empty list selects wildcard and an empty list entry is invalid.", "components": ["loki", "dskit"], "sources": ["loki:s33f320afa73a", "dskit:s23d81aeedf07", "dskit:s4d546b0d82d4"], "status": "REASONED"},
    "memberlist-label": {"text": "Cluster labels reject mismatches unless verification is disabled, but matching labels are not credentials; no SecretKey/keyring setting is wired.", "components": ["dskit"], "sources": ["dskit:s052e8107edad", "dskit:scf57b6b1f148"], "status": "REASONED"},
    "memberlist-updates": {"text": "Without TLS, reachable matching-label peers can submit KV/ring state subject to codecs/merge rules; disruption is inferred, not demonstrated.", "components": ["dskit"], "sources": ["dskit:scf57b6b1f148", "dskit:s69c68f3d3e6a", "dskit:s1b539b8100a3"], "status": "REASONED"},
    "memberlist-tls": {"text": "TLS defaults off; enabled transport verifies outgoing servers but leaves incoming ClientAuth at NoClientCert, so it is not mutual peer authentication.", "components": ["dskit", "go"], "sources": ["dskit:s23d81aeedf07", "dskit:s4d546b0d82d4", "dskit:s675104c4819c", "dskit:s99e7e34182f1", "go:sd3b3c1c431ec"], "status": "REASONED"},
    "memberlist-policy": {"text": "Keep tls-insecure-skip-verify false, set expected server name as needed, bind privately and restrict trusted peers even with TLS.", "components": ["dskit"], "sources": ["dskit:s675104c4819c", "dskit:s99e7e34182f1"], "status": "REASONED"},
    "memberlist-advertise": {"text": "Advertise address/port affect discovery, not bind; absent overrides derive an address from the first bind and actual port.", "components": ["dskit"], "sources": ["dskit:s251174df8783", "dskit:s052e8107edad"], "status": "REASONED"},
    "loki-tenants": {"text": "From source reading, auth_enabled defaults true and requires tenant headers, not credentials; false uses fake, and tenant validation checks syntax/length only.", "components": ["loki", "dskit"], "sources": ["loki:sd13fa86b20d0", "loki:sb5e56f0d6348", "dskit:s3634557bb838", "dskit:s1ca109a7a016"], "status": "REASONED"},
    "loki-grpc-auth": {"text": "From source reading, default dskit interceptors lack credentials; Loki has tenant exemptions; complete interceptor behaviour was not re-traced.", "components": ["dskit", "loki"], "sources": ["dskit:s38beab6892ea", "dskit:saf57a4cbc682", "loki:s057e686b00bb", "loki:s7786b9105acc"], "status": "REASONED"},
    "loki-push-query": {"text": "From source reading, reachable clients can push/query without credentials subject to tenant headers and ingest/query policies.", "components": ["loki"], "sources": ["loki:s9f316e1a5fef", "loki:s39c270ed878c"], "status": "REASONED"},
    "loki-config": {"text": "From source reading, GET /config exposes configuration without a tenant-auth wrapper.", "components": ["loki"], "sources": ["loki:sbe0aa939a44d"], "status": "REASONED"},
    "loki-diagnostics": {"text": "From source reading, metrics and pprof routes are registered by default without a tenant-auth wrapper.", "components": ["dskit"], "sources": ["dskit:sb19d54a19636", "dskit:se0830c9ea1b5", "dskit:s761b46738198"], "status": "REASONED"},
    "loki-maintenance": {"text": "From source reading, ingester flush/shutdown accept GET/POST; prepare_shutdown accepts POST/GET/DELETE, without tenant-auth wrappers.", "components": ["loki"], "sources": ["loki:sc2b013001317"], "status": "REASONED"},
    "loki-delete": {"text": "Non-worker compactor deletion routes require a supported shipper index, retention and a delete-request store; tenant and deletion-policy middleware gate create/list/cancel. After tenant validation, filter-only and filter-and-delete pass, disabled gets 403 and an unrecognized mode gets 400, by source reasoning, not observed responses; admission does not establish eventual deletion.", "components": ["loki"], "sources": ["loki:s4f3a19f7f08c", "loki:s3d51e1213e70", "loki:s38c1e77fe01e", "loki:s1f38431776f2", "loki:s3ff15746c2c9", "loki:s14f65483dd4d", "loki:s0bde2f8abe97", "loki:saf8f37e04b71", "loki:s6feced2aa907", "loki:se1440b6eb37a", "loki:sae57ccde5dc6", "loki:s86b57bdedee7", "loki:sc37c5a5a63b4"], "status": "REASONED"},
    "loki-delete-mode": {"text": "In v3.7.8, validDeletionLimit parses the tenant's DeletionMode; only the exact strings disabled, filter-only and filter-and-delete parse, and DeleteEnabled is true for the latter two. TenantMiddleware returns 400 for tenant or parsing errors, 403 for disabled, otherwise invokes the handler; this is source reasoning, not observed responses.", "components": ["loki"], "sources": ["loki:s3ff15746c2c9", "loki:sae57ccde5dc6", "loki:s86b57bdedee7", "loki:sc37c5a5a63b4"], "status": "REASONED"},
    "loki-grpc-bridge": {"text": "From source reading, single-binary ingester RPC and HTTP-over-gRPC expose paths that HTTP-only TLS/proxying does not protect.", "components": ["loki", "dskit"], "sources": ["loki:sc2b013001317", "dskit:s5fd7b12bfcf1"], "status": "REASONED"},
    "loki-mtls": {"text": "From source reading, HTTP/gRPC TLS defaults empty and requires a cert/key pair; configure client CA plus RequireAndVerifyClientCert, not CA alone.", "components": ["dskit"], "sources": ["dskit:sb19d54a19636", "dskit:s0dc9a01e591a", "dskit:sd35a28be4391"], "status": "REASONED"},
    "loki-ring": {"text": "This guide's single-binary overlay uses inmemory ring, loopback instance address and replication_factor 1 instead of default 3 (from source reading); check no gossip listener remains.", "components": ["loki"], "sources": ["loki:s8f06ddfa5291", "loki:s8cf14a90ec61", "loki:sfb3d52071e7c"], "status": "REASONED"},
    "loki-internal": {"text": "From source reading, querier worker init gets server gRPC listen address/port, target flags, scheduler ring and worker config; ingester lifecycler listen port is the gRPC listen port.", "components": ["loki"], "sources": ["loki:s765907d2b4ee", "loki:sf3955ae90da4", "loki:sc2b013001317"], "status": "REASONED"},
    "loki-internal-dials": {"text": "Worker and distributor/querier ingester dial sites are traced by source reading; loopback gRPC is this guide's configuration-specific advice; verify advertised/dial addresses, internal worker/ingester success, any compactor calls and live reachability.", "components": ["loki", "dskit"], "sources": ["loki:s00520a857797", "dskit:s433134153d1d", "loki:s7b1d1f183610", "loki:sc5574f33c47c", "loki:s4554d31a5d15", "dskit:s1786ff0496f6", "dskit:sc8780cfc9e85", "loki:s18cd3a035b38", "loki:s5b3705652693", "loki:sfc4788e520b8", "loki:sc2b013001317", "loki:s765907d2b4ee", "loki:sf3955ae90da4", "loki:sfb3d52071e7c", "loki:s8cf14a90ec61", "loki:scf12ae06cdc4", "loki:s0ce56d38618e", "loki:s970473c2dcdb", "loki:s6b2f01173a97", "loki:s44e7547da37d", "loki:s79ea72562a9f", "loki:s634e6599df5e", "loki:s10b95cd4cab8", "loki:s82a976e6b93c", "loki:s47c05209cd31", "loki:s1d59e1184191", "loki:s9d106cc379de", "loki:s8b3d57f01355", "loki:s88661a4514b3", "loki:sb0ae3e30f690", "loki:s074f98761044", "loki:s51e0f640a169", "loki:sa19fa92e5d02", "dskit:sb0955f4c2ebd", "dskit:s74daabf65e98", "dskit:s172528a7c1bf", "dskit:scf57b6b1f148"], "status": "REASONED"},
    "loki-worker-init": {"text": "From source reading, with frontend, scheduler, read and all targets off, InitWorkerService returns no worker if the scheduler ring and both addresses are unset. Otherwise it passes worker config and ring to NewQuerierWorker; outside that standalone case, unset ring/addresses trigger a frontend address using the gRPC port and a nonempty listen address, else 127.0.0.1.", "components": ["loki"], "sources": ["loki:s765907d2b4ee", "loki:sf3955ae90da4", "loki:s99ac9c7561c2", "loki:s61ecb8af773e"], "status": "REASONED"},
    "loki-worker-dials": {"text": "From source reading, workers prefer scheduler ring, scheduler address, then frontend address; AddressAdded calls grpc.DialContext with that client's options, handing it to a processor manager. Frontend Process and scheduler QuerierLoop open on a supplied connection; scheduler results go to the message's FrontendAddress via grpc.Dial with frontend options; success unverified.", "components": ["loki"], "sources": ["loki:s79ea72562a9f", "loki:s634e6599df5e", "loki:s10b95cd4cab8", "loki:s82a976e6b93c", "loki:s47c05209cd31", "loki:s18cd3a035b38", "loki:s1d59e1184191", "loki:s5b3705652693", "loki:sde741c787b71", "loki:sb8f98248ef1a"], "status": "REASONED"},
    "loki-instance-port": {"text": "From source reading, GetInstancePort returns a positive configured lifecycler port, else the listen port, which Loki sets to the server gRPC listen port or the bound port when that is 0; a configured common ring copies its instance_port into the lifecycler port. The advertised address is the configured address, else one chosen from the configured interfaces.", "components": ["loki", "dskit"], "sources": ["dskit:sd7b8bf6bbca6", "dskit:sa7d343f48dc5", "dskit:s74daabf65e98", "loki:seea78f4f5adb", "loki:sc2b013001317", "loki:sfb3d52071e7c", "loki:sf4c3469d7ee1", "dskit:s96305c045ce4"], "status": "REASONED"},
    "loki-ring-kv": {"text": "From source reading, lifecyclers CAS their entry, with the advertised address, into the ring key at initialization and on heartbeat; KV backends are consul, etcd, process-wide inmemory, memberlist or multi, plus test-only mock.", "components": ["dskit"], "sources": ["dskit:s04a225bbac7b", "dskit:s59c2aa3eb502", "dskit:sbd4dba4be513", "dskit:s1786ff0496f6", "dskit:s8145c89a12ee"], "status": "REASONED"},
    "loki-ring-reads": {"text": "From source reading, ring clients read then watch the ring key; distributors take per-stream write sets and queriers, outside partition-ingester queries, the healthy read set via ring.DoUntilQuorum.", "components": ["dskit", "loki"], "sources": ["dskit:sf68c98707951", "dskit:s05d533c42177", "dskit:s16cda83ea984", "dskit:s48b2d449a388", "dskit:s2a947b05938f", "loki:s51e0f640a169", "loki:sb0ae3e30f690", "loki:s2e89e4162342"], "status": "REASONED"},
    "loki-client-pools": {"text": "From source reading, dskit pools cache one client per address, created on first use. With health checks on (frontend pool; ingester pools by default), one failed check removes a client, as Loki sets no grace period.", "components": ["loki", "dskit"], "sources": ["dskit:s0b92cab27eeb", "dskit:sa35a10f1fa8b", "dskit:s6224eeb93eb9", "loki:s5ab3c47cb0fc", "loki:sfc4788e520b8", "loki:s88661a4514b3", "loki:sde741c787b71", "loki:s21675bf85b75"], "status": "REASONED"},
    "loki-client-pools-discovery": {"text": "From source reading, ingester pools drop addresses missing from healthy ring entries; the frontend pool has no discovery and checks every 5s. Pooling does not establish effective addresses or successful calls.", "components": ["loki", "dskit"], "sources": ["dskit:sa35a10f1fa8b", "dskit:s6224eeb93eb9", "dskit:s79f868b8ee48", "loki:s5ab3c47cb0fc", "loki:sfc4788e520b8", "loki:s88661a4514b3", "loki:sde741c787b71"], "status": "REASONED"},
    "loki-worker-watchers": {"text": "From source reading, ring watchers take the scheduler ring's key-0 Write set each lookup period and reconcile only non-empty results; DNS watchers poll at that period with no SRV name, report an IP target once and re-resolve host names, with dskit's default port 443 if none is given.", "components": ["loki", "dskit"], "sources": ["loki:scc6c338ac167", "loki:s02c83c5d9dda", "loki:sc26dc660fa21", "dskit:s7077c6b93703", "dskit:s77d6a067cd74", "dskit:sfbd1b87a9a0c"], "status": "REASONED"},
    "loki-worker-managers": {"text": "From source reading, addresses that the worker's ring or DNS watchers add get processor managers sharing max concurrency, at least one each; removal notifies the peer and closes the connection.", "components": ["loki"], "sources": ["loki:s634e6599df5e", "loki:sb8f98248ef1a", "loki:s6a02e080cabb", "loki:scc6c338ac167", "loki:s02c83c5d9dda", "loki:sc26dc660fa21"], "status": "REASONED"},
    "loki-request-callers": {"text": "From source reading, push HTTP handlers call PushWithResolver; outside all, write and ingester targets the distributor also registers gRPC Pusher. Kafka writes default off, ingester writes on; Kafka writes need a partition ring and produce to an active partition.", "components": ["loki"], "sources": ["loki:s9f316e1a5fef", "loki:s543d4de072bb", "loki:s3d6bf0891af0", "loki:sd28855900a87", "loki:sa59140ca5c4c", "loki:s9a87cce410e5", "loki:s846c370c416f", "loki:s51bcdc31e69d"], "status": "REASONED"},
    "loki-ingester-query-window": {"text": "From source reading, without query_store_only, Loki queriers query ingesters for selections ending within the ingester store lookback if it is nonzero when the querier module initializes, else query_ingesters_within (0: all); a -1 lookback, documented as infinite, sends every selection to ingesters and none directly to the store.", "components": ["loki"], "sources": ["loki:s8f53a03e764f", "loki:sdc0d0e6ad95d", "loki:s529cd9a944d9", "loki:sf2a4759294c3", "loki:s23d3deffe096", "loki:s23599866ad90", "loki:s86fc597288e2", "loki:se3f01b0b8f64"], "status": "REASONED"},
    "loki-ingester-lookback-all": {"text": "From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, and the active or next schema period uses a boltdb-shipper or TSDB index, the store module, initialized before the querier module that depends on it, turns a configured 0 ingester store lookback into a computed minimum that replaces query_ingesters_within; without all, 0 stays 0.", "components": ["loki", "dskit"], "sources": ["loki:s086d15529b4c", "loki:se82f6c344ae2", "loki:sa4685cf34525", "loki:s9a971cf72e10", "loki:s937747b2754f", "loki:sf2a4759294c3", "loki:sf4c3469d7ee1", "loki:sc311d25f20e8", "loki:s3e8d9a35ec33", "loki:sb7c90a61ae40", "dskit:s96305c045ce4"], "status": "REASONED"},
    "loki-ingester-lookback-minimum": {"text": "From source reading, Loki's computed minimum ingester store lookback is the ingester's maximum chunk age plus 21 minutes (a 15-minute boltdb shard period, 1-minute index upload interval and 5-minute buffer), the index cache validity and three resync intervals of the active or next period's shipper index.", "components": ["loki"], "sources": ["loki:sa4685cf34525", "loki:s362660480c60", "loki:s7e25cfebaa93", "loki:s425030dbbf09"], "status": "REASONED"},
    "loki-ingester-lookback-store": {"text": "From source reading, Loki's query_store_max_look_back_period flag help limits it to boltdb-shipper/TSDB indexes with the filesystem object store; the all target's boltdb-shipper/TSDB store setup rejects a nonzero value with any other object store.", "components": ["loki"], "sources": ["loki:s23d3deffe096", "loki:se82f6c344ae2", "loki:sa4685cf34525", "loki:s937747b2754f"], "status": "REASONED"},
    "loki-ingester-store-all": {"text": "From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, and the active or next schema period uses a boltdb-shipper or TSDB index, the ingester, initialized after the store module it depends on, also queries the store for the log and sample selections it serves, except when the lookback-adjusted start is after the selection end.", "components": ["loki", "dskit"], "sources": ["loki:se82f6c344ae2", "loki:sa4685cf34525", "loki:s9a971cf72e10", "loki:s086d15529b4c", "loki:s937747b2754f", "loki:s21c205d034b9", "loki:sd6184d6a8a46", "loki:s51ab6a62a6bd", "loki:sf4c3469d7ee1", "dskit:s96305c045ce4", "loki:sc2b013001317"], "status": "REASONED"},
    "loki-ingester-store-range": {"text": "From source reading, when a Loki ingester queries the store for a log or sample selection, it moves the start of the store request up to now minus a positive store lookback, leaves it unchanged for -1 and other negative values, and skips the store query when that adjusted start is after the selection end.", "components": ["loki"], "sources": ["loki:s51ab6a62a6bd", "loki:s21c205d034b9", "loki:sd6184d6a8a46"], "status": "REASONED"},
    "loki-ingester-lookback-bounds": {"text": "From source reading, when Loki's target list includes all but none of querier, ruler, read, index-gateway or backend, its boltdb-shipper or TSDB store setup with the filesystem object store rejects a positive query_store_max_look_back_period below the computed minimum and passes -1 and any other negative value through calculateMaxLookBack unchanged.", "components": ["loki"], "sources": ["loki:se82f6c344ae2", "loki:sa4685cf34525", "loki:s937747b2754f"], "status": "REASONED"},
    "loki-querier-store-window": {"text": "From source reading, when the ingester store lookback that the Loki querier module copies at initialization is positive, the querier limits its own store query to the part of a selection before now minus that lookback, querying only ingesters when the selection starts after that point; exactly -1 instead skips the store and sends the whole selection to ingesters.", "components": ["loki"], "sources": ["loki:sf2a4759294c3", "loki:s529cd9a944d9", "loki:sdc0d0e6ad95d", "loki:s86fc597288e2", "loki:se3f01b0b8f64"], "status": "REASONED"},
    "loki-querier-store-negative": {"text": "From source reading, when the ingester store lookback that the Loki querier module copies at initialization is negative but not -1, now minus that lookback lies in the future, and the querier sets the end of any store request to that point without clamping it to the selection end, unlike the Loki ingester, which leaves its store request start unchanged for every negative lookback.", "components": ["loki"], "sources": ["loki:sf2a4759294c3", "loki:s529cd9a944d9", "loki:sdc0d0e6ad95d", "loki:s86fc597288e2", "loki:se3f01b0b8f64", "loki:s51ab6a62a6bd"], "status": "REASONED"},
    "loki-querier-ingester-inverted": {"text": "From source reading, if a Loki selection passing request validation reaches interval construction and the querier's initialization copy of the ingester store lookback is negative but not -1 with now minus it past the selection end, the querier starts its ingester interval there, ends it at the selection end without an order check and sends it to its ingester querier unless query_store_only is set.", "components": ["loki"], "sources": ["loki:sf2a4759294c3", "loki:s529cd9a944d9", "loki:scba306dcdc0c", "loki:sdc0d0e6ad95d", "loki:s10870cc18ddc", "loki:s8f53a03e764f", "loki:sb5b69814231d", "loki:s23b8da8ac6be"], "status": "REASONED"},
    "loki-ingester-inverted-call": {"text": "From source reading, Loki's ingester querier passes the log or sample request it receives, including an inverted interval from the querier, to the gRPC Query or QuerySample call of each ingester it queries, and the ingester module registers the ingester, or a wrapper that Go code embedding Loki may set, as the Querier service whose generated handlers decode the request and call those methods.", "components": ["loki"], "sources": ["loki:sdc0d0e6ad95d", "loki:s10870cc18ddc", "loki:s61e16a1ac1f0", "loki:sf253d44e375f", "loki:sfb58949fa28c"], "status": "REASONED"},
    "loki-ingester-inverted-store": {"text": "From source reading, without a configured wrapper, a Loki ingester serving a log or sample request whose start is after its end makes no store query for it, whatever its store lookback: its store-request code moves a start only later, to now minus a positive lookback, and returns no store request when that adjusted start is after the end.", "components": ["loki"], "sources": ["loki:s51ab6a62a6bd", "loki:s21c205d034b9", "loki:sd6184d6a8a46"], "status": "REASONED"},
    "loki-ingester-inverted-memory": {"text": "From source reading, without a configured wrapper, a Loki ingester's in-memory log or sample query looks up streams in its index at the request start and, for each matching stream, skips every chunk unless the chunk's bounds start no later than the request end and end no earlier than the request start, so for an inverted interval it keeps only chunks covering the span from that end to that start.", "components": ["loki"], "sources": ["loki:se2f420694eb9", "loki:se913abf5bf85", "loki:se1f0d83f115c", "loki:s2a80da1a36e8", "loki:sadb084375296", "loki:s0b40d7d25a3f", "loki:se34169c8b133"], "status": "REASONED"},
    "loki-ingester-inverted-lookup": {"text": "From source reading, a Loki v3.7.8 ingester adds every stream to each index it builds, and its index lookup uses an inverted interval's start only to pick the index of the schema period containing it, for a future start the latest period starting at or before it; the lookup matches label matchers and shard without reading time, so the interval's order causes no lookup error.", "components": ["loki"], "sources": ["loki:sd5967b880c33", "loki:sc87fdc20cb58", "loki:s11cbfc4fcf89", "loki:sf674ae88a12c", "loki:s6bc46c6500c2", "loki:s140b0adc6723", "loki:s19918b3b217b", "loki:sadb084375296"], "status": "REASONED"},
    "loki-ingester-inverted-iterators": {"text": "From source reading, Loki v3.7.8's ingester stream, chunk and head-block iterators neither swap nor clamp an inverted interval: they read a chunk, block or head block only if it starts no later than the interval's end and ends no earlier than its start, and the ordered head block's log iterator drops each entry before the start or at or after the end.", "components": ["loki"], "sources": ["loki:se3affc4818e6", "loki:s693d6421c2f0", "loki:sd5181aa115e4", "loki:scc80bfb6f547", "loki:s05d6c5fc01a2", "loki:s291928ddc0b1", "loki:s33683997e787", "loki:s0b40d7d25a3f", "loki:se34169c8b133"], "status": "REASONED"},
    "loki-ingester-inverted-time-filter": {"text": "From source reading, Loki v3.7.8's chunk time-range filters, used for block entries in both directions, the head block in forward log queries and all sample queries, skip entries before the start but accept one timestamped exactly at it before testing the end; in this guide's assessment, they pass only such entries for an inverted interval.", "components": ["loki"], "sources": ["loki:sd5181aa115e4", "loki:scc80bfb6f547", "loki:s0dbdc425ddbb", "loki:s05d6bac1c352"], "status": "REASONED"},
    "loki-push-future-bound": {"text": "From source reading, Loki v3.7.8's distributor validates each pushed entry against a context built from time.Now(): a timestamp strictly newer than now plus the tenant's creation_grace_period (default 10m) is rejected as too far in the future, so one exactly at that bound passes. reject_old_samples (default true) rejects entries older than now minus reject_old_samples_max_age (default 7d).", "components": ["loki"], "sources": ["loki:sa66ae191eb87", "loki:s883c99aaf259", "loki:s03a9eb3c1800", "loki:s7be82cdc7279", "loki:sc1c59c06ac21", "loki:s9acb77638396", "loki:s7e5e17b46be6"], "status": "REASONED"},
    "loki-ingester-push-validation": {"text": "From source reading, Loki v3.7.8's ingester gRPC push chain compares timestamps with stream state and schema configuration, never the clock, with no future timestamp bound. Unordered writes (default true) drop entries below the stream's highest timestamp minus half max_chunk_age (default 2h); ordered appends reject those older than the head block's newest or, head empty, the last block's maximum.", "components": ["loki"], "sources": ["loki:sa5963eda217e", "loki:s02173d6919e0", "loki:s6d778dd956ad", "loki:s3683552f47e7", "loki:s48eb47bcb74e", "loki:s1d09c7438f6c", "loki:s631c8b46da80", "loki:s6259f9f6561b", "loki:sef39e72a9288", "loki:sfc254eaeb3c3", "loki:s19e37d99684b"], "status": "REASONED"},
    "loki-ingester-inverted-hold": {"text": "From the cited source reading without a Loki run, in this guide's assessment an ingester can hold an entry dated exactly at the inverted interval's future start when the negative lookback's magnitude is at most creation_grace_period, on one clock, grace period unchanged. For a larger magnitude a direct ingester gRPC push can; Kafka consumer pushes and duplicate-timestamp shifts are not ruled out.", "components": ["loki"], "sources": ["loki:s529cd9a944d9", "loki:s7be82cdc7279", "loki:s03a9eb3c1800", "loki:s9acb77638396", "loki:sa66ae191eb87", "loki:sa5963eda217e", "loki:s3683552f47e7", "loki:s9044377b42e9", "loki:sd2ef570a75c2", "loki:sd01827189b1e", "loki:s9c1fabf63f70", "loki:s93219a6da66c", "loki:se9b1d3173a5a"], "status": "REASONED"},
    "loki-ingester-inverted-unordered": {"text": "From source reading, Loki v3.7.8's backward log queries do not time-filter a chunk's head block, and the unordered head block queries its vendored go-datastructures v1.1.7 range tree from an interval's start to one nanosecond before its end, both inclusive. For an inverted interval that query returns no entry, so the head block yields nothing.", "components": ["loki"], "sources": ["loki:sd5181aa115e4", "loki:s33683997e787", "loki:s69faadc4a015", "loki:s18bc063957e1", "loki:sf185bec82940", "loki:s015710936d80", "loki:saf4f45f2d5c7", "loki:sd8ad9fae3598", "loki:sd82568caaafc", "loki:s996300b7bdcf", "loki:s9a133bb92cd3"], "status": "REASONED"},
    "loki-ingester-empty-send": {"text": "From source reading, when Loki v3.7.8's ingester Query or QuerySample code gets an error-free iterator yielding nothing, it sends one empty batch with query statistics and warnings unless the request context is already done, failing only on a Send error other than context.Canceled. The ingester querier's per-ingester iterator records those, yields nothing and ends cleanly at the stream's end.", "components": ["loki"], "sources": ["loki:s76e4e638e936", "loki:s5732ba30414b", "loki:sa1a1efa48033", "loki:s00b4ce2d9a6a", "loki:s9f438349ea61", "loki:sf89b7c829a53", "loki:s6c74d0f4adb3", "loki:sdf678b8f143f", "loki:s61e16a1ac1f0"], "status": "REASONED"},
    "loki-querier-inverted-merge": {"text": "From source reading, a Loki v3.7.8 querier merges the ingester querier's per-ingester iterators for a log or sample selection with the iterator of any store query it makes for that selection, which it skips when query_ingester_only is set or it builds no store interval; a log selection with only one iterator gets that iterator unmerged.", "components": ["loki"], "sources": ["loki:s8f53a03e764f", "loki:sdc0d0e6ad95d", "loki:s86fc597288e2", "loki:s2d763a8942ef", "loki:s10870cc18ddc", "loki:se3f01b0b8f64", "loki:s6f04b102b391", "loki:s61e16a1ac1f0", "loki:s529cd9a944d9"], "status": "REASONED"},
    "loki-ingester-wrapper-search": {"text": "From source reading, a word search for Wrapper in Loki v3.7.8's pkg, cmd, integration, tools and clients trees finds only Ingester.Wrapper's declaration (no YAML key), its one-method Wrap interface and initIngester's nil check and Wrap call, besides a code comment and stylesheet source maps; nothing there sets it, and initIngester registers Wrap's result only when it is set.", "components": ["loki"], "sources": ["loki:s24cd2d4a2bce", "loki:sd7efa15100d2", "loki:sf253d44e375f"], "status": "REASONED"},
    "loki-querier-ingester-inverted-result": {"text": "Source reading of Loki's querier, ingester querier and ingester query code, with no Loki run, does not establish what they return for the inverted ingester interval a negative store lookback besides -1 yields: in this guide's assessment ingesters can hold entries dated exactly at its start when the lookback's magnitude is within the grace period, on one clock, grace unchanged; no run observed it.", "components": ["loki"], "sources": ["loki:s529cd9a944d9", "loki:sdc0d0e6ad95d", "loki:s10870cc18ddc", "loki:s61e16a1ac1f0", "loki:sadb084375296", "loki:s0b40d7d25a3f", "loki:se34169c8b133", "loki:sd5181aa115e4", "loki:s33683997e787", "loki:s69faadc4a015", "loki:sa66ae191eb87", "loki:s7be82cdc7279", "loki:s9acb77638396"], "status": "REASONED"},
    "loki-internal-server": {"text": "From source reading, Run initializes target modules and starts them together. internal_server is off by default; when enabled it precedes Server and its HTTP listener defaults to localhost:3101.", "components": ["loki", "dskit"], "sources": ["loki:sb7c90a61ae40", "loki:scf7d98f51caa", "loki:sf4c3469d7ee1", "loki:sd4f78f9689f6", "loki:sd46d55125044", "loki:s9fd7d8bd80e3", "loki:sf19909de84b7", "loki:s319f6b7b5340", "dskit:s7848c6311aee"], "status": "REASONED"},
    "loki-internal-server-grpc": {"text": "From source reading and Go's net.Listen documentation, the internal server's flags register no gRPC address or port, so by inference, when enabled, unless YAML sets them, dskit opens an any-address gRPC listener on an OS-chosen port carrying the HTTP bridge; not observed.", "components": ["loki", "dskit", "go"], "sources": ["loki:scf7d98f51caa", "loki:sd46d55125044", "loki:s9fd7d8bd80e3", "loki:sf19909de84b7", "loki:s309318e5a59c", "dskit:s7848c6311aee", "dskit:s5fd7b12bfcf1", "go:s37204ff1b27c"], "status": "REASONED"},
    "loki-internal-routes": {"text": "When enabled, the internal server's HTTP router serves routes including /ready and buildinfo and, when their modules run, /ring, /memberlist and the compactor handler prefix; these are source registrations, not observed responses.", "components": ["loki"], "sources": ["loki:sb7c90a61ae40", "loki:s319f6b7b5340", "loki:sb6c261fe940d", "loki:s81d8d94c3cea"], "status": "REASONED"},
    "loki-grpc-tls": {"text": "Inferred from dskit's server TLS source, gRPC TLS requires compatible TLS on every internal client; local users can reach plaintext loopback and, per Loki's authentication documentation, mTLS does not supply tenant headers.", "components": ["dskit", "loki"], "sources": ["dskit:sd35a28be4391", "loki:s70975c2655fa"], "status": "REASONED"},
    "loki-proxy": {"text": "An authenticating proxy must overwrite X-Scope-OrgID with its identity and be the only caller that can reach Loki.", "components": ["loki"], "sources": ["loki:s70975c2655fa"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory every TCP/UDP listener; wildcard defaults, all Loki listeners and off-host isolation were not observed.", "components": ["node", "alert", "push", "jaeger", "dskit"], "sources": ["node:s896899f5a500", "alert:s0fd66cba968e", "push:s5c9f9745f42d", "jaeger:s5619bba2be59", "dskit:sb19d54a19636", "dskit:s23d81aeedf07"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "External 200 exposes unauthenticated HTTP; HTTPS 401 shows auth, not isolation. Confirm connection failures and a permitted positive control.", "components": ["security", "toolkit", "jaeger-docs"], "sources": ["security:s3ffe42e99660", "toolkit:sbb86207a38e5", "jaeger-docs:s4969c5ffaa59"], "status": "REASONED", "verify": [2]},
    "verify-loki": {"text": "A tenant-header rejection is not authentication; repeat with an arbitrary X-Scope-OrgID and test both families, gRPC and internal RPCs.", "components": ["loki", "curl"], "sources": ["loki:s70975c2655fa", "loki:s057e686b00bb", "curl:s3db522258e44"], "status": "REASONED", "verify": [2]},
    "verify-basic": {"text": "Loopback HTTPS GETs on node/Pushgateway metrics, Alertmanager status and Jaeger v3 services gave no-credential 401 and credentialed 200.", "components": ["node", "push", "alert", "jaeger", "toolkit"], "sources": ["node:s896899f5a500", "push:s5c9f9745f42d", "alert:s120d6ecf3fcd", "jaeger:sc6f47d82b947", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "The loopback runs gave exactly that pair over HTTPS for GETs of node_exporter `/metrics`, Pushgateway `/metrics`, Alertmanager `/api/v2/status` and Jaeger `/api/v3/services`.", "verify": [3]},
    "verify-loki-mtls": {"text": "Authorized HTTP mTLS should succeed, untrusted/missing client certs fail handshake and plaintext fail; no Loki listener/TLS run occurred.", "components": ["loki", "dskit"], "sources": ["loki:s70975c2655fa", "dskit:sd35a28be4391"], "status": "REASONED"},
    "verify-secret": {"text": "Basic-auth stdin closes argv exposure only; shell history, tracing and your own account's view of the process can still leak the password.", "components": ["toolkit", "curl"], "sources": ["toolkit:sbb86207a38e5", "curl:s5e1383feef7d", "curl:s82a34ee18632"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
