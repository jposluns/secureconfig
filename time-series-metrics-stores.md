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

The backup and restore RPC on `8088` binds `127.0.0.1` by default; keep it there. Leave the optional Graphite, collectd, OpenTSDB, and UDP inputs disabled unless you are separately securing them, since each is another unauthenticated write path.

## VictoriaMetrics

### Single-node

The HTTP API, UI, and ingest share port `8428`, and single-node VictoriaMetrics has no built-in request authentication: the vendor's own security guidance is to place it behind `vmauth` (its authorization proxy) or a reverse proxy, which is where authentication and TLS belong. Bind the listener privately so only that proxy reaches it:

```text
-httpListenAddr=127.0.0.1:8428
```

A handful of destructive and debug handlers can be gated individually with `-deleteAuthKey` (the `/api/v1/admin/tsdb/delete_series` handler), `-forceMergeAuthKey`, and `-forceFlushAuthKey`. Setting one of these protects that handler; it does not turn the operation on, and it is not a substitute for authenticating the API as a whole.

### Cluster

The cluster splits the surface across ports, all with the same no-native-auth posture: `vminsert` on `8480` takes ingestion, `vmselect` on `8481` takes queries and the UI, and `vmstorage` on `8482` exposes maintenance and metrics, with the native RPC channels on `8400` and `8401`. Keep every component on a private network and route external traffic through `vmauth` with per-route or per-tenant restrictions, so no component answers the internet directly.

## QuestDB

QuestDB opens several protocols, each with its own default. The web console with its REST and SQL endpoints is on `9000`, and its Basic-auth keys `http.user` and `http.password` are unset by default, so the console and REST API answer unauthenticated in the open-source build. The PostgreSQL wire protocol on `8812` ships the default credential pair `admin` / `quest` in `pg.user` and `pg.password`. The InfluxDB line protocol on `9009` (TCP) has `line.tcp.auth.db.path` unset by default, so it accepts unauthenticated writes. Set each of these in the active `server.conf`:

```properties
http.user=REPLACE_WITH_A_NAME
http.password=REPLACE_WITH_A_SECRET
pg.user=REPLACE_WITH_A_NAME
pg.password=REPLACE_WITH_A_SECRET
line.tcp.auth.db.path=conf/auth.txt
```

`line.tcp.auth.db.path` points at a file of P-256 public keys. The minimal health server on `9003` follows the HTTP policy you set. The open-source build has no native TLS, so terminate it at a reverse proxy; QuestDB Enterprise instead uses role-based access control (it refuses to start if the `http.user` and `http.password` keys are set) and its own `tls.enabled` settings.

## The pattern, any of these

Bind every listener to loopback or a private interface, and put authentication and TLS in a layer in front, because none of these engines gives you a complete native authentication story: VictoriaMetrics has none, InfluxDB 1.x ships with it off, and QuestDB leaves it unset. Change every default credential (`admin` / `quest` first), and never place an ingest or query port on the public internet. A browser sign-in or MFA layer in front of the console does not authenticate the PostgreSQL wire or line-protocol ports, which are separate listeners: bind and front those too.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor pages rather than observed, and backlog row 2.32 tracks demonstrating them against live instances in the exposed and fixed states. A transport failure, a redirect, a 404, or a TLS error is inconclusive, never the fixed state.

```bash
sudo ss -tlnp    # read the whole table: 8086, 8428/8480/8481/8482, 9000/8812/9009 only on the
sudo ss -ulnp    # intended private addresses, and no metrics port bound to a public interface
```

```bash
# Per-target discriminator: an exposed store returns data, a fixed one refuses. Substitute a full
# URL for each row below; the guard rejects an unsubstituted placeholder rather than let it time out
# and read like a blocked port.
(
  set -- 'REPLACE_WITH_URL'
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute a full URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) : ;;
    *) echo "expected an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code}\n' "$1"
)
```

Run that block once per target: InfluxDB 2.x `https://tsdb.example.com:8086/api/v2/setup` returns `allowed:true` on an un-set-up instance and `false` once initialized; InfluxDB 1.x `https://tsdb.example.com:8086/query?q=SHOW+DATABASES` returns the database list when `auth-enabled` is off and `401` once it is on; VictoriaMetrics `https://tsdb.example.com:8428/api/v1/query?query=up` returns series when unfronted and `401` behind `vmauth`; QuestDB `https://tsdb.example.com:9000/exec?query=SELECT+1` returns a result set with no `http.user` set and `401` once it is. For the PostgreSQL wire port, confirm separately that `admin` / `quest` is refused with a `psql` connection attempt. A `200` health response, a redirect, or a 404 proves none of this on its own; require an authorized positive control alongside each refusal.

## Common mistakes

- Leaving an InfluxDB 2.x instance un-set-up on a reachable address, so the first stranger to `POST /api/v2/setup` becomes its operator.
- Running InfluxDB 1.x with the default `auth-enabled = false`, which leaves `DROP DATABASE` open to anyone who can reach `8086`.
- Assuming VictoriaMetrics authenticates requests; it does not, and `-deleteAuthKey` and its siblings gate only their own handlers.
- Leaving QuestDB's `admin` / `quest` PostgreSQL credential in place, or fronting only the `9000` console while `8812` and `9009` stay open.
- Terminating TLS and login at a proxy for the web console while the database and ingest protocols keep answering on their own ports.

## Sources (checked September 2026)

- InfluxDB 2.x setup API (`GET /api/v2/setup`, the `allowed` field, `POST` onboarding): https://docs.influxdata.com/influxdb/v2/api/setup/
- InfluxDB 2.x configuration options (`http-bind-address`, `tls-cert`, `tls-key`, `INFLUXD_CONFIG_PATH`): https://docs.influxdata.com/influxdb/v2/reference/config-options/
- InfluxDB 1.x configuration (`[http] auth-enabled` default `false`, `bind-address` `:8086`, backup RPC `127.0.0.1:8088`): https://docs.influxdata.com/influxdb/v1/administration/config/
- InfluxDB 1.x authentication and authorization: https://docs.influxdata.com/influxdb/v1/administration/authentication_and_authorization/
- VictoriaMetrics single-node, security recommendations (port `8428`, no native auth, `vmauth`, `-deleteAuthKey`, `-forceMergeAuthKey`, `-forceFlushAuthKey`): https://docs.victoriametrics.com/victoriametrics/
- VictoriaMetrics cluster (`vminsert` `8480`, `vmselect` `8481`, `vmstorage` `8482`, native RPC `8400`/`8401`): https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/
- vmauth authorization proxy: https://docs.victoriametrics.com/victoriametrics/vmauth/
- QuestDB HTTP server (`9000`, `http.user` / `http.password` unset by default): https://questdb.com/docs/configuration/http-server/
- QuestDB PostgreSQL wire protocol (`8812`, default `admin` / `quest`): https://questdb.com/docs/configuration/postgres-wire-protocol/
- QuestDB ingestion / line protocol (`9009`, `line.tcp.auth.db.path` default none): https://questdb.com/docs/configuration/ingestion/
