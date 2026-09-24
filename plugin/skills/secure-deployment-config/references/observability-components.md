# Self-hosted observability components: node_exporter, Alertmanager, Pushgateway, Jaeger, and Loki

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
and it needs to be `0.0.0.0`", so in a container every one of these listens on every interface, and a
published port reaches it.

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
layer. You must run an authenticating reverse proxy in front of your services." The HTTP listener is on
3100 and gRPC on 9095. The listen addresses default to empty, which means every interface. The shipped
`loki-local-config.yaml` uses gRPC 9096 and `auth_enabled: false`, so read your own file, not the
defaults. With memberlist as the ring store, gossip listens on 7946, all interfaces by default, without
TLS unless you set `memberlist.tls-enabled`.

`auth_enabled: true`, the default, is multi-tenancy, not authentication. Loki requires an `X-Scope-OrgID`
header and trusts whatever value the client sends. On the v3.7.8 loopback run with `auth_enabled: true`,
a request without the header got `401`. A request naming any tenant could read labels (`200`) and push
logs (`204`). Do not read that `401` as a login. `GET /config` (the running configuration) and
`/debug/pprof/` answered `200` with no header at all. The API reference adds that "authorization is not
part of the Loki API", and it lists `/flush`, `/ingester/shutdown` (which terminates the process by
default) and the log-deletion endpoints with no gate.

There are two fixes, and you can use both:

- **mTLS on the servers.** The authentication docs describe `http_tls_config` and `grpc_tls_config`
  under `server`, and advise `RequireAndVerifyClientCert` for the strictest setting:

  ```yaml
  server:
    http_listen_address: 10.0.0.6
    grpc_listen_address: 10.0.0.6
    http_tls_config:
      cert_file: /etc/loki/tls/server.crt
      key_file: /etc/loki/tls/server.key
      client_auth_type: RequireAndVerifyClientCert
      client_ca_file: /etc/loki/tls/clients-ca.crt
    grpc_tls_config:   # "accepts the same options for the gRPC server"
      cert_file: /etc/loki/tls/server.crt
      key_file: /etc/loki/tls/server.key
      client_auth_type: RequireAndVerifyClientCert
      client_ca_file: /etc/loki/tls/clients-ca.crt
  ```

  On the loopback run, a client with a certificate from that CA got `200`. A client without one was
  refused in the handshake (curl exit 56, `tlsv13 alert certificate required`), with or without a tenant
  header. Plain HTTP got `400`. With both blocks and both listeners on 127.0.0.1, the gRPC port refused
  a TLS client without a certificate (`tlsv13 alert certificate required`) and rejected plaintext HTTP/2.
  Configure gRPC too: an HTTP-only fix leaves 9095 on every interface in plaintext. mTLS does not set
  `X-Scope-OrgID`, so your agent or proxy still does.
- **An authenticating proxy that owns the tenant header.** The vendor's nginx example sets
  `proxy_set_header X-Scope-OrgID $remote_user;` so that "nginx overwrites any tenant header sent by the
  client". Keep Loki itself reachable only from that proxy. See [nginx.md](nginx.md) and
  [fronting-auth.md](fronting-auth.md).

## Verify

The HTTP results below were demonstrated on 127.0.0.1 against the versions named at the top, in both the
exposed state and the fixed state. The default all-interfaces binds were not observed, so they are
reasoned: the authoring host forbids binding every interface, so each run overrode the address to
127.0.0.1. The binds follow from each binary's `--help` default (`:9100`, `:9093`, `0.0.0.0:9094`,
`:9091`) and from source (Loki's empty listen addresses; Jaeger's `":" + port` query default). Go
listens on every interface for an address with no host. The probes from a second host are reasoned
too: the authoring environment had no second host, so the refusal or timeout expected there was not
observed. Backlog row 1.108 tracks observing both. On the host:

```bash
sudo ss -tlnp   # loopback or a private address only: 9100 9093 9094 9091 3100 9095 7946, and
                # Jaeger's 16686 16685 4317 4318 14250 14268 9411 5778 5779 13133 27777 27778 8888
sudo ss -ulnp   # Alertmanager gossip also uses UDP 9094; Jaeger's Thrift receivers UDP 6831 and 6832
```

Exposed, the reasoned expectation is `*:9100` (or `0.0.0.0:`/`[::]:`) for an unconfigured node_exporter,
and likewise for the others. Fixed means a loopback or private address. Then probe from a host that
should not have access. The block refuses to run until you substitute the address.

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

Any `200` is the finding: that service answers the unauthenticated request. For a service that uses
TLS, switch that URL to `https`. A `401` then means its authentication is on. From a host that should
be blocked, a connection refusal or a connect timeout is consistent with isolation. Read the `err`
text to confirm it happened while connecting, not in a local proxy or policy. The write-out fields need
curl 7.75.0 or newer. For Loki, a `401` without a tenant header proves nothing. Repeat the Loki probe
with `-H 'X-Scope-OrgID: anyone'` added, and treat a `200` as exposure.

Run the positive control from a host that should have access, so a dead service is not read as fixed.
The password reaches curl on stdin, not argv. Substitute inside the quotes, and add
`--cacert /path/to/ca.crt` if the certificate is private.

```bash
(
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
`/api/v2/status` and Jaeger `/api/v3/services`. For Loki under mTLS, the equivalent is `--cert` and `--key` on an authorized client
(`200`) against the same request without them, which fails in the handshake. This closes the argv
channel only. The password can still reach shell history or `set -x` output.

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
- Jaeger v2.21.0 release notes (v1 HTTP endpoints removed): https://github.com/jaegertracing/jaeger/releases/tag/v2.21.0
- OpenTelemetry Collector configtls v1.66.0, as pinned by Jaeger v2.21.0 (`cert_file`, `key_file`): https://github.com/open-telemetry/opentelemetry-collector/blob/cd3455cf3a7f672208140b1ebb1581c542b2b0ed/config/configtls/README.md
- OpenTelemetry Collector contrib v0.160.0 basicauth extension (`htpasswd`, `authenticator`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.160.0/extension/basicauthextension/README.md
- Loki v3.7.8 authentication (no built-in auth, tenancy header, mTLS, nginx tenant header): https://github.com/grafana/loki/blob/v3.7.8/docs/sources/operations/authentication.md
- Loki v3.7.8 HTTP API (`/config`, `/flush`, `/ingester/shutdown`, deletion): https://github.com/grafana/loki/blob/v3.7.8/docs/sources/reference/loki-http-api.md
- Loki v3.7.8 `auth.enabled` default and port 3100: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go
- Loki v3.7.8 sample local configuration: https://github.com/grafana/loki/blob/v3.7.8/cmd/loki/loki-local-config.yaml
- dskit as pinned by Loki v3.7.8 (gRPC 9095, empty listen addresses): https://github.com/grafana/dskit/blob/8d1c6d34bb5a/server/server.go
- dskit memberlist transport (port 7946, bind default 0.0.0.0, `memberlist.tls-enabled`): https://github.com/grafana/dskit/blob/8d1c6d34bb5a/kv/memberlist/tcp_transport.go
- Go `net.Listen` (an empty host listens on all addresses): https://pkg.go.dev/net#Listen
