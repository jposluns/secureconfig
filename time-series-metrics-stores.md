# Time-series and metrics stores: InfluxDB, VictoriaMetrics, and QuestDB

A metrics store ingests over HTTP and answers queries over an HTTP API, and most ship a web console beside it. Several of them either authenticate nothing by default or ship a known default credential, so an instance that is reachable from off-host lets a stranger read your operational and business series, write false points that poison dashboards and alerts, or delete history. This guide covers three that AI-assisted projects commonly stand up. The controls are the same shape in each: bind the listeners privately, put authentication and TLS in front where the engine has none of its own, and change every default credential. [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern these lean on, [secrets.md](secrets.md) covers the tokens and passwords, and [mfa.md](mfa.md) is the account layer. All ports below bind all interfaces (`0.0.0.0`) unless noted, and native TLS is off unless you configure it. Replace every illustrative address and name.

## InfluxDB

### OSS 2.x

The HTTP API, the UI, and the write endpoint all share port `8086`. You cannot turn authentication off or on with a flag: a fresh instance is instead *un-set-up*, and `GET /api/v2/setup` returns `allowed: true` until someone completes onboarding. Whoever reaches an exposed, un-initialized instance first can `POST /api/v2/setup` to create the initial user, organization, and an all-access operator token, which is a full takeover. Complete setup privately, then hand applications *scoped* tokens rather than the operator token. Bind the listener privately and enable TLS in the config file (located through `INFLUXD_CONFIG_PATH`):

```yaml
http-bind-address: "127.0.0.1:8086"
tls-cert: "/etc/ssl/influxdb.crt"
tls-key: "/etc/ssl/influxdb.key"
```

### OSS 1.x

Port `8086` again carries query, write, and administrative statements, and the `[http]` setting `auth-enabled` is `false` by default. An unauthenticated caller can therefore read every database, write points, and run destructive statements such as `DROP DATABASE`. Create an administrator user first, then require authentication and turn on HTTPS:

```toml
[http]
  bind-address = "127.0.0.1:8086"
  auth-enabled = true
  https-enabled = true
  https-certificate = "/etc/ssl/influxdb.crt"
  https-private-key = "/etc/ssl/influxdb.key"
```

Enabling `auth-enabled` does not by itself authenticate the Prometheus remote-read API; set `prom-read-auth-enabled = true` as well, since it defaults to `false` and has no effect until `auth-enabled` is on. The backup and restore RPC on `8088` binds `127.0.0.1` by default; keep it there. Leave the optional Graphite, collectd, OpenTSDB, and UDP inputs disabled unless you are separately securing them, since each is another unauthenticated write path.

## VictoriaMetrics

### Single-node

The HTTP API, UI, and ingest share port `8428`. VictoriaMetrics has built-in HTTP Basic authentication, disabled by default: set `-httpAuth.username` and `-httpAuth.password` to require one static credential across the whole HTTP API (authentication is off while they are empty), and `-tls`, `-tlsCertFile`, and `-tlsKeyFile` to serve HTTPS. That single all-or-nothing credential is enough to close an open instance; for per-route rules, multiple tenants, or rate limiting, the vendor directs you to front it with `vmauth` (its authorization proxy) or a reverse proxy. Bind the listener privately either way:

```text
-httpListenAddr=127.0.0.1:8428
-httpAuth.username=REPLACE_WITH_A_NAME
-httpAuth.password=REPLACE_WITH_A_SECRET
-tls -tlsCertFile=/etc/ssl/vm.crt -tlsKeyFile=/etc/ssl/vm.key
```

A handful of destructive and debug handlers can be gated individually with `-deleteAuthKey` (the `/api/v1/admin/tsdb/delete_series` handler), `-forceMergeAuthKey`, and `-forceFlushAuthKey`. Setting one of these protects that handler; it does not turn the operation on, and it does not authenticate the API as a whole.

### Cluster

At v1.152.0-cluster, the open-source cluster splits HTTP across three components: `vminsert` takes ingestion on `-httpListenAddr=:8480`, `vmselect` takes queries and the UI on `:8481`, and `vmstorage` exposes maintenance and metrics on `:8482`. These are the fallback addresses when no `-httpListenAddr` is supplied. Each binds every IPv4 interface by default; `-enableTCP6` also enables IPv6. Each HTTP component accepts `-httpAuth.username` and `-httpAuth.password`, both empty by default; Basic authentication is disabled while the username is empty.

On `vmstorage`, `-vminsertAddr=:8400` and `-vmselectAddr=:8401` also bind every IPv4 interface by default. These native RPC listeners have no authentication or native TLS in this open-source build. Their handshake checks a protocol identifier and negotiates compression, not a credential. A caller speaking the protocol can write arbitrary series through `8400`, or read and delete series through `8401`; the latter also exposes tenant enumeration, metric-name registration and usage-statistics reset. HTTP Basic auth, endpoint auth keys and `vmauth` do not protect these sockets. Bind `-vminsertAddr` and `-vmselectAddr` to each storage node's cluster-network IP and restrict access to trusted cluster members with firewall or network-policy rules. A private address alone is not an access control. The optional `-clusternativeListenAddr` on `vminsert` and `vmselect` is empty (disabled) by default; restrict it to the same trusted network if enabled for a multi-level cluster.

The HTTP maintenance and disclosure handlers have their own keys:

- On `vmstorage` (`8482`), `-snapshotAuthKey` gates `/snapshot/create`, `/snapshot/list`, `/snapshot/delete` and `/snapshot/delete_all`; `-forceMergeAuthKey` gates `/internal/force_merge`; `-forceFlushAuthKey` gates `/internal/force_flush`; and `-logNewSeriesAuthKey` gates `/internal/log_new_series`.
- On `vmselect` (`8481`), `-deleteAuthKey` gates POSTs to `/delete/{accountID}/prometheus/api/v1/admin/tsdb/delete_series` and `/select/{accountID}/graphite/tags/delSeries`. `-search.resetCacheAuthKey` gates `/internal/resetRollupResultCache`, and `-metricNamesStatsResetAuthKey` gates `/admin/api/v1/admin/status/metric_names_stats/reset`.
- On all three HTTP components, `-metricsAuthKey`, `-flagsAuthKey` and `-pprofAuthKey` gate `/metrics`, `/flags` and `/debug/pprof/*`, respectively.

These keys default to empty. An empty endpoint key falls back to HTTP Basic auth, so the handler is unauthenticated when `-httpAuth.username` is also empty. A nonempty endpoint key requires a matching `authKey` request parameter and overrides Basic auth for that handler; it does not add a second authentication requirement or authenticate other routes. Bind every HTTP component privately and route external traffic through `vmauth` over HTTPS with per-route or per-tenant restrictions, allowing only the operations clients need.

## QuestDB

QuestDB opens several protocols, each with its own default. The web console with its REST and SQL endpoints is on `9000`, and its Basic-auth keys `http.user` and `http.password` are unset by default, so the console and REST API answer unauthenticated in the open-source build. The PostgreSQL wire protocol on `8812` ships the default credential pair `admin` / `quest` in `pg.user` and `pg.password`. The InfluxDB line protocol on `9009` (TCP) has `line.tcp.auth.db.path` unset by default, so it accepts unauthenticated writes. Set each of these in the active `server.conf`:

```properties
http.user=REPLACE_WITH_A_NAME
http.password=REPLACE_WITH_A_SECRET
pg.user=REPLACE_WITH_A_NAME
pg.password=REPLACE_WITH_A_SECRET
line.tcp.auth.db.path=conf/auth.txt
```

`line.tcp.auth.db.path` points at a file of P-256 public keys. The minimal health server on `9003` follows the HTTP policy you set. The open-source build has no native TLS, so terminate it at a reverse proxy; QuestDB Enterprise instead uses role-based access control (since Enterprise 4.0.0 it refuses to start if the `http.user` and `http.password` keys are set) and its own `tls.enabled` settings.

## The pattern, any of these

Bind every listener to loopback or a private interface, and put authentication and TLS in a layer in front, because none of these engines authenticates by default: VictoriaMetrics ships its Basic auth empty, InfluxDB 1.x ships `auth-enabled` off, and QuestDB leaves its console keys and ILP auth unset while shipping a default database credential. Change every default credential (`admin` / `quest` first), and never place an ingest or query port on the public internet. A browser sign-in or MFA layer in front of the console does not authenticate the PostgreSQL wire or line-protocol ports, which are separate listeners: bind and front those too.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor pages rather than observed, and backlog row 2.32 tracks demonstrating them against live instances in the exposed and fixed states. A transport failure, a redirect, a 404, or a TLS error is inconclusive, never the fixed state.

```bash
sudo ss -tlnp    # read the whole table: 8086 and loopback 8088; 8428, 8480, 8481, 8482 and native
sudo ss -ulnp    # RPC 8400, 8401; 9000, 9003, 8812, 9009, each only on its intended private
                 # address, and no metrics or ingest port bound to a public interface
```

**REASONED, not demonstrated:** the VictoriaMetrics cluster RPC check needs a running cluster and probe hosts inside and outside its protected network, unavailable in the authoring environment (no container runtime). Row 2.32 tracks this demonstration. The `ss` inventory above identifies local binds; it does not prove that `8400` and `8401` are unreachable from outside the cluster network. From an outside host, substitute each storage node's actual IP below and run the whole block. Repeat from a trusted cluster host as the positive control. Use any configured replacement ports too, including enabled `-clusternativeListenAddr` listeners. The pinned RPC listener and handshake sources below explain why reachability matters.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_STORAGE_NODE_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the storage node IP; not probing"; exit 2 ;;
  esac
  python3 - "$1" <<'PY'
import ipaddress
import socket
import sys

_, host = sys.argv
ipaddress.ip_address(host)
for port in (8400, 8401):
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"{host}:{port}: TCP REACHABLE")
    except OSError as exc:
        print(f"{host}:{port}: connection failed: {exc}; not proof of isolation")
PY
)
```

An exposed listener is expected to report `TCP REACHABLE` from outside; this is an exposure failure even if an HTTP request to that port fails, since RPC is not HTTP. In the fixed state, outside connections must be blocked while the trusted-host control still connects to both running listeners. A timeout or refusal alone is inconclusive: confirm the target, running listener and firewall or network-policy rule responsible. A `401` from `vmauth` says nothing about RPC isolation.

```bash
# Per-target discriminator against the default plaintext listener: an exposed store returns the named
# body or a 200, a fixed one behind auth returns 401. Substitute a full URL on the set -- line
# and paste the whole block so the guard runs; use `http://` for the exposed check and the hardened `https://` entrypoint for the re-run, and the body is kept because one target discriminates on it.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute a full URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) : ;;
    *) echo "expected an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

Run that block once per target, over `http://` against the default plaintext listener. InfluxDB 2.x `http://tsdb.example.com:8086/api/v2/setup` returns a body containing `"allowed":true` on an un-set-up instance and `"allowed":false` once initialized; the HTTP status is `200` either way, so read the body, not the code. InfluxDB 1.x `http://tsdb.example.com:8086/query?q=SHOW+DATABASES` returns the database list when `auth-enabled` is off and `401` once it is on. VictoriaMetrics `http://tsdb.example.com:8428/api/v1/query?query=up` returns series until `-httpAuth.username` is set or it sits behind `vmauth`, then `401`. QuestDB `http://tsdb.example.com:9000/exec?query=SELECT+1` returns a result set with no `http.user` set and `401` once it is. For the PostgreSQL wire port, confirm separately that `admin` / `quest` is refused with a `psql` connection attempt. Once authentication and TLS are in front, re-run against the `https://` entrypoint to confirm the `401`, and separately confirm the plaintext port is closed from outside, since a `401` from the proxy does not prove the backend listener is unreachable. A `200` health response, a redirect, or a 404 proves none of this on its own.

## Common mistakes

- Leaving an InfluxDB 2.x instance un-set-up on a reachable address, so the first stranger to `POST /api/v2/setup` becomes its operator.
- Running InfluxDB 1.x with the default `auth-enabled = false`, which leaves `DROP DATABASE` open to anyone who can reach `8086`.
- Leaving VictoriaMetrics reachable with its `-httpAuth.username` and `-httpAuth.password` empty (the default), or assuming `-deleteAuthKey` and its siblings authenticate the API when they gate only their own handlers.
- Leaving QuestDB's `admin` / `quest` PostgreSQL credential in place, or fronting only the `9000` console while `8812` and `9009` stay open.
- Terminating TLS and login at a proxy for the web console while the database and ingest protocols keep answering on their own ports.

## Sources (checked September 2026)

- InfluxDB 2.x setup API (`GET /api/v2/setup`, the `allowed` field, `POST` onboarding): https://docs.influxdata.com/influxdb/v2/api/setup/
- InfluxDB 2.x configuration options (`http-bind-address`, `tls-cert`, `tls-key`, `INFLUXD_CONFIG_PATH`): https://docs.influxdata.com/influxdb/v2/reference/config-options/
- InfluxDB 1.x configuration (`[http] auth-enabled` default `false`, `bind-address` `:8086`, backup RPC `127.0.0.1:8088`): https://docs.influxdata.com/influxdb/v1/administration/config/
- InfluxDB 1.x authentication and authorization: https://docs.influxdata.com/influxdb/v1/administration/authentication_and_authorization/
- VictoriaMetrics single-node, security recommendations (port `8428`, `-httpAuth.username`/`-httpAuth.password` Basic auth disabled by default, `-tls`/`-tlsCertFile`/`-tlsKeyFile`, `vmauth`, `-deleteAuthKey`, `-forceMergeAuthKey`, `-forceFlushAuthKey`): https://docs.victoriametrics.com/victoriametrics/
- VictoriaMetrics v1.152.0-cluster HTTP fallback binds: [vminsert](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L161-L167), [vmselect](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L150-L158), [vmstorage and RPC startup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L221-L244); [RPC address defaults and storage auth-key flags](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L46-L68).
- VictoriaMetrics v1.152.0-cluster TCP bind implementation and IPv4 default: [listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/netutil/tcplistener.go#L16-L43), [network selection](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/netutil/tcplistener.go#L79-L85); optional cluster-native listeners: [vminsert](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L53-L54), [vmselect](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L77-L78).
- VictoriaMetrics v1.152.0-cluster RPC handshake: [protocol identifiers](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L17-L23), [insert hello check](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L77-L109), [select hello check](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L137-L158), [compression negotiation without credentials](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L203-L233).
- VictoriaMetrics v1.152.0-cluster RPC capabilities: [storage writes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/vmstorage.go#L109-L124), [plaintext select listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/vmselectapi/server.go#L94-L101), [RPC dispatch including deletion, registration and reset](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/vmselectapi/server.go#L558-L588), [storage deletion and mutations](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/vmstorage.go#L318-L352).
- VictoriaMetrics v1.152.0-cluster HTTP auth: [flags and HTTP TLS scope](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L38-L57), [metrics, flags and pprof routes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L461-L510), [endpoint-key precedence and Basic-auth fallback](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L534-L573).
- VictoriaMetrics v1.152.0-cluster maintenance: [storage handler auth routing](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L279-L288), [merge, flush, logging and snapshots](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L307-L420), [select cache resets](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L269-L296), [rollup-cache key](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/prometheus/prometheus.go#L57-L60), [Graphite deletion](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L580-L594), [Prometheus deletion](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L867-L884).
- VictoriaMetrics cluster security recommendations (private network, HTTPS auth proxy and endpoint allowlists): https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/#security
- vmauth authorization proxy: https://docs.victoriametrics.com/victoriametrics/vmauth/
- QuestDB HTTP server (`9000`, `http.user` / `http.password` unset by default): https://questdb.com/docs/configuration/http-server/
- QuestDB PostgreSQL wire protocol (`8812`, default `admin` / `quest`): https://questdb.com/docs/configuration/postgres-wire-protocol/
- QuestDB ingestion / line protocol (`9009`, `line.tcp.auth.db.path` default none): https://questdb.com/docs/configuration/ingestion/
