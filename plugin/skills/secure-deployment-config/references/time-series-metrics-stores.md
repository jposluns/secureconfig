---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "fc6d9b11f3c0464ea416b8c52c97ebf7bff9342962307ba1264880dd3472243a",
  "components": {
    "influx2": {
      "name": "InfluxDB OSS",
      "basis": "2.x",
      "sources": {
        "sc9e982673a2c": "https://docs.influxdata.com/influxdb/v2/api/setup/",
        "s51be52d52f2d": "https://docs.influxdata.com/influxdb/v2/reference/config-options/"
      }
    },
    "influx1": {
      "name": "InfluxDB OSS",
      "basis": "1.x",
      "sources": {
        "s5b36c54676cf": "https://docs.influxdata.com/influxdb/v1/administration/config/",
        "s33366bcde097": "https://docs.influxdata.com/influxdb/v1/administration/authentication_and_authorization/"
      }
    },
    "single": {
      "name": "VictoriaMetrics single-node",
      "basis": "v1.152.0",
      "sources": {
        "sa2064b7f7fde": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/victoria-metrics/main.go#L91-L114",
        "s466b138f957d": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/victoria-metrics/main.go#L137-L201",
        "s249469a9efa7": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/netutil/tcplistener.go#L16-L43",
        "s987c110a0edf": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/netutil/tcplistener.go#L79-L85",
        "s6b03d23b3093": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L38-L57",
        "s29f1814c0fd1": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L385-L419",
        "sf2990c7273c4": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L425-L510",
        "s79f8b1e8eaad": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L534-L573",
        "s2517f5aeb932": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/flagutil/password.go#L16-L30",
        "saecbf1f05812": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L138-L303",
        "s42d2b0ce4a7e": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/deployment/docker/compose-vm-single.yml#L18-L37",
        "s93fe4e7a4f06": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L49-L70",
        "s0d0b471d6432": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/graphite/server.go#L46-L53",
        "see5f5b942c00": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/influx/server.go#L46-L52",
        "sebc8d4060c41": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/opentsdb/server.go#L49-L60",
        "s6390a3764ab9": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/opentsdbhttp/server.go#L88-L92",
        "sd99ec4d08863": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmstorage/main.go#L38-L46",
        "sb6dcdcc221e4": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmselect/main.go#L33-L37"
      }
    },
    "cluster": {
      "name": "VictoriaMetrics cluster",
      "basis": "v1.152.0-cluster",
      "sources": {
        "saab5425284b6": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L161-L167",
        "s479ca0b4df35": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L150-L158",
        "sbbabc9e0412a": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L221-L244",
        "s3a9a2abdad17": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L46-L68",
        "sd22646cb0be5": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/netutil/tcplistener.go#L79-L85",
        "s3e4eb7d48b66": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L203-L233",
        "s92f08e888601": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/vmselectapi/server.go#L558-L588",
        "s429c413cd3cb": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L53-L54",
        "s57e2ac042ad3": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L77-L78",
        "sc2940f50c072": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L38-L57",
        "sf4856285e76b": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L534-L573",
        "s82e2718b5417": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L307-L420",
        "s0cd1a9b994b9": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L269-L296",
        "sc6f6632ae4c1": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L580-L594",
        "sc65ed9e63bfa": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L867-L884",
        "se1ccf8033c97": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L461-L510",
        "sb0412a061355": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/prometheus/prometheus.go#L57-L60"
      }
    },
    "rpc": {
      "name": "VictoriaMetrics cluster source",
      "basis": "e4b1d55683f0da20410dc765787bd4e9b5afa0da",
      "sources": {
        "sca91785d878c": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L78-L144",
        "sdba733140e0c": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L255-L267",
        "sb17dce5a1339": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/netutil/tcplistener.go#L107-L140",
        "sa18d26bb1269": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/flagutil/password.go#L21-L30"
      }
    },
    "proxy": {
      "name": "VictoriaMetrics security/vmauth documentation",
      "basis": "unknown",
      "sources": {
        "s185272dd320f": "https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/#security",
        "s79ed3b00108a": "https://docs.victoriametrics.com/victoriametrics/vmauth/"
      }
    },
    "quest": {
      "name": "QuestDB documentation",
      "basis": "unknown",
      "sources": {
        "s3a0487771c1a": "https://questdb.com/docs/configuration/http-server/",
        "s9c38998f3725": "https://questdb.com/docs/configuration/postgres-wire-protocol/",
        "se0fda155b33d": "https://questdb.com/docs/configuration/ingestion/",
        "s19f43451ff2b": "https://questdb.com/docs/configuration/http-min-server/"
      }
    },
    "single-commit": {
      "name": "VictoriaMetrics single-node source commit",
      "basis": "540b91da031aa8b7d53d3784693bb451e2be980a",
      "sources": {
        "sa2064b7f7fde": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/victoria-metrics/main.go#L91-L114"
      }
    },
    "image": {
      "name": "VictoriaMetrics shipped Compose image",
      "basis": "v1.151.0",
      "sources": {
        "s42d2b0ce4a7e": "https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/deployment/docker/compose-vm-single.yml#L18-L37"
      }
    },
    "enterprise": {
      "name": "QuestDB Enterprise qualification",
      "basis": "4.0.0",
      "sources": {
        "s3a0487771c1a": "https://questdb.com/docs/configuration/http-server/"
      }
    }
  },
  "claims": {
    "influx2-setup": {"text": "8086 shares API/UI/write; private onboarding creates operator user/org/token, setup allowed changes true to false, scoped app tokens.", "components": ["influx2"], "sources": ["influx2:sc9e982673a2c"], "status": "REASONED"},
    "influx2-tls": {"text": "INFLUXD_CONFIG_PATH selects config; http-bind-address, tls-cert and tls-key set private HTTPS.", "components": ["influx2"], "sources": ["influx2:s51be52d52f2d"], "status": "REASONED"},
    "influx1-auth": {"text": "8086 auth defaults off; create admin then set bind-address, auth-enabled and HTTPS certificate/key fields.", "components": ["influx1"], "sources": ["influx1:s5b36c54676cf", "influx1:s33366bcde097"], "status": "REASONED"},
    "influx1-other": {"text": "prom-read-auth-enabled=false by default; set it true with auth-enabled for remote-read auth; 8088 backup RPC defaults loopback; optional unauthenticated ingest stays disabled.", "components": ["influx1"], "sources": ["influx1:s5b36c54676cf"], "status": "REASONED"},
    "vm-bind": {"text": "Single-node HTTP fallback :8428, tcp4 default, enableTCP6 false; explicit private bind and TLS flags.", "components": ["single", "single-commit"], "sources": ["single:sa2064b7f7fde", "single:s249469a9efa7", "single:s987c110a0edf", "single:s6b03d23b3093", "single-commit:sa2064b7f7fde"], "status": "REASONED"},
    "vm-image": {"text": "Source tag ships Compose using image v1.151.0, wildcard 8428 publication and additional ingest listeners.", "components": ["single", "image"], "sources": ["single:s42d2b0ce4a7e", "image:s42d2b0ce4a7e"], "status": "REASONED"},
    "vm-basic": {"text": "Empty username disables Basic auth even with password; ordinary query/UI/HTTP ingest and aliases share the credential.", "components": ["single"], "sources": ["single:s6b03d23b3093", "single:s79f8b1e8eaad", "single:s2517f5aeb932", "single:saecbf1f05812"], "status": "REASONED"},
    "vm-exempt": {"text": "Health/ping/readiness/robots/favicon, OPTIONS and prefix handling exemptions differ from authenticated ready and influx/health.", "components": ["single"], "sources": ["single:s29f1814c0fd1", "single:sf2990c7273c4", "single:saecbf1f05812"], "status": "REASONED"},
    "vm-keys": {"text": "Registered endpoint keys default empty and fall back to Basic; nonempty authKey replaces Basic, wrong/missing gives 401; other aliases may require both.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sf2990c7273c4", "single:s79f8b1e8eaad", "single:s2517f5aeb932", "single:s93fe4e7a4f06", "single:sd99ec4d08863", "single:sb6dcdcc221e4"], "status": "REASONED"},
    "vm-optional": {"text": "Graphite/Influx/OpenTSDB/native-query listeners default disabled; no TLS, and only OpenTSDB HTTP put checks Basic.", "components": ["single"], "sources": ["single:s93fe4e7a4f06", "single:s0d0b471d6432", "single:see5f5b942c00", "single:sebc8d4060c41", "single:s6390a3764ab9", "single:sd99ec4d08863"], "status": "REASONED"},
    "cluster-http": {"text": "vminsert/vmselect/vmstorage fall back to 8480/8481/8482 on IPv4 wildcard; optional IPv6, empty Basic credentials and HTTP-only TLS.", "components": ["cluster", "rpc"], "sources": ["cluster:saab5425284b6", "cluster:s479ca0b4df35", "cluster:sbbabc9e0412a", "cluster:sd22646cb0be5", "cluster:sc2940f50c072", "rpc:sa18d26bb1269"], "status": "REASONED"},
    "cluster-rpc": {"text": "8400/8401 wildcard RPC has no credentials/TLS; handshake/compression permits writes, reads, deletion and metadata mutations, outside HTTP auth.", "components": ["cluster", "rpc"], "sources": ["cluster:s3a9a2abdad17", "cluster:s3e4eb7d48b66", "cluster:s92f08e888601", "rpc:sca91785d878c", "rpc:sdba733140e0c", "rpc:sb17dce5a1339"], "status": "REASONED"},
    "cluster-native": {"text": "Optional clusternativeListenAddr is disabled by default; restrict enabled native listeners to trusted cluster peers.", "components": ["cluster", "proxy"], "sources": ["cluster:s429c413cd3cb", "cluster:s57e2ac042ad3", "proxy:s185272dd320f"], "status": "REASONED"},
    "cluster-key-snapshot": {"text": "vmstorage: -snapshotAuthKey gates /snapshot/create, /snapshot/list, /snapshot/delete and /snapshot/delete_all.", "components": ["cluster"], "sources": ["cluster:s82e2718b5417"], "status": "REASONED"},
    "cluster-key-merge": {"text": "vmstorage: -forceMergeAuthKey gates /internal/force_merge.", "components": ["cluster"], "sources": ["cluster:s82e2718b5417"], "status": "REASONED"},
    "cluster-key-flush": {"text": "vmstorage: -forceFlushAuthKey gates /internal/force_flush.", "components": ["cluster"], "sources": ["cluster:s82e2718b5417"], "status": "REASONED"},
    "cluster-key-logging": {"text": "vmstorage: -logNewSeriesAuthKey gates /internal/log_new_series.", "components": ["cluster"], "sources": ["cluster:s82e2718b5417"], "status": "REASONED"},
    "cluster-key-delete": {"text": "vmselect: -deleteAuthKey gates POSTs to /delete/{accountID}/prometheus/api/v1/admin/tsdb/delete_series and /select/{accountID}/graphite/tags/delSeries.", "components": ["cluster"], "sources": ["cluster:sc6f6632ae4c1", "cluster:sc65ed9e63bfa"], "status": "REASONED"},
    "cluster-key-cache": {"text": "vmselect: -search.resetCacheAuthKey gates /internal/resetRollupResultCache.", "components": ["cluster"], "sources": ["cluster:s0cd1a9b994b9", "cluster:sb0412a061355"], "status": "REASONED"},
    "cluster-key-stats": {"text": "vmselect: -metricNamesStatsResetAuthKey gates /admin/api/v1/admin/status/metric_names_stats/reset.", "components": ["cluster"], "sources": ["cluster:s0cd1a9b994b9"], "status": "REASONED"},
    "cluster-key-metrics": {"text": "All three HTTP components: -metricsAuthKey gates /metrics.", "components": ["cluster"], "sources": ["cluster:se1ccf8033c97"], "status": "REASONED"},
    "cluster-key-flags": {"text": "All three HTTP components: -flagsAuthKey gates /flags.", "components": ["cluster"], "sources": ["cluster:se1ccf8033c97"], "status": "REASONED"},
    "cluster-key-pprof": {"text": "All three HTTP components: -pprofAuthKey gates /debug/pprof/*.", "components": ["cluster"], "sources": ["cluster:se1ccf8033c97"], "status": "REASONED"},
    "cluster-precedence": {"text": "Empty keys fall back to Basic; nonempty keys replace it, not add a factor or protect other routes; allowlist proxy routes.", "components": ["cluster", "rpc", "proxy"], "sources": ["cluster:sf4856285e76b", "rpc:sa18d26bb1269", "proxy:s185272dd320f", "proxy:s79ed3b00108a"], "status": "REASONED"},
    "quest-http": {"text": "9000 HTTP/console/SQL defaults unauthenticated; set http.user/password in server.conf. 9003 health requires auth when HTTP does by default; http.health.check.authentication.required=false disables that health check requirement.", "components": ["quest"], "sources": ["quest:s3a0487771c1a", "quest:s19f43451ff2b"], "status": "REASONED"},
    "quest-pg": {"text": "8812 PostgreSQL wire defaults admin/quest; replace pg.user/password and protect its separate listener.", "components": ["quest"], "sources": ["quest:s9c38998f3725"], "status": "REASONED"},
    "quest-ilp": {"text": "9009 TCP writes default unauthenticated; line.tcp.auth.db.path selects P-256 public-key file.", "components": ["quest"], "sources": ["quest:se0fda155b33d"], "status": "REASONED"},
    "quest-tls": {"text": "OSS requires proxy TLS; Enterprise uses RBAC/tls.enabled and rejects HTTP credential keys since stated Enterprise 4.0.0.", "components": ["quest", "enterprise"], "sources": ["quest:s3a0487771c1a", "enterprise:s3a0487771c1a"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory TCP/UDP and every enabled listener; local binds do not prove external isolation.", "components": ["influx1", "single", "cluster", "quest"], "sources": ["influx1:s5b36c54676cf", "single:s93fe4e7a4f06", "cluster:s3a9a2abdad17", "quest:s3a0487771c1a", "quest:s9c38998f3725", "quest:se0fda155b33d"], "status": "REASONED", "verify": [1]},
    "verify-rpc": {"text": "Actual storage IPs must refuse outside TCP while permitted hosts connect; protocol is not HTTP and failure alone proves no isolation.", "components": ["cluster", "rpc", "proxy"], "sources": ["cluster:s3a9a2abdad17", "cluster:s3e4eb7d48b66", "rpc:sca91785d878c", "proxy:s185272dd320f"], "status": "REASONED", "verify": [2]},
    "verify-http": {"text": "Setup body, Influx1 database list/401, VM query/401 and Quest SQL/401 discriminate per target; redirects/errors are inconclusive.", "components": ["influx2", "influx1", "single", "quest"], "sources": ["influx2:sc9e982673a2c", "influx1:s33366bcde097", "single:s79f8b1e8eaad", "quest:s3a0487771c1a"], "status": "REASONED", "verify": [3]},
    "verify-extra": {"text": "Reject default PG credential separately; repeat HTTPS auth and plaintext isolation; console MFA does not protect native protocols.", "components": ["quest", "proxy"], "sources": ["quest:s9c38998f3725", "proxy:s185272dd320f"], "status": "REASONED", "verify": [3]},
    "verify-keys": {"text": "Read-only snapshot/list and metrics probes test empty/Basic/endpoint-key cases; health exemptions and optional listeners need separate checks.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sf2990c7273c4", "single:s79f8b1e8eaad"], "status": "REASONED", "verify": [3]},
    "key-snapshot": {"text": "snapshotAuthKey gates snapshot create/list/delete/delete_all and admin TSDB snapshot.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sd99ec4d08863"], "status": "REASONED"},
    "key-delete": {"text": "deleteAuthKey gates Prometheus delete_series and Graphite delSeries aliases.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sb6dcdcc221e4"], "status": "REASONED"},
    "key-merge": {"text": "forceMergeAuthKey gates internal/force_merge.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sd99ec4d08863"], "status": "REASONED"},
    "key-flush": {"text": "forceFlushAuthKey gates internal/force_flush.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sd99ec4d08863"], "status": "REASONED"},
    "key-cache": {"text": "search.resetCacheAuthKey gates internal/resetRollupResultCache.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sb6dcdcc221e4"], "status": "REASONED"},
    "key-logging": {"text": "logNewSeriesAuthKey gates internal/log_new_series.", "components": ["single"], "sources": ["single:s466b138f957d"], "status": "REASONED"},
    "key-stats": {"text": "metricNamesStatsResetAuthKey gates admin/status/metric_names_stats/reset.", "components": ["single"], "sources": ["single:s466b138f957d", "single:sb6dcdcc221e4"], "status": "REASONED"},
    "key-config": {"text": "configAuthKey gates config and API status/config with Prometheus aliases.", "components": ["single"], "sources": ["single:s466b138f957d", "single:s93fe4e7a4f06"], "status": "REASONED"},
    "key-reload": {"text": "reloadAuthKey gates -/reload and Prometheus alias.", "components": ["single"], "sources": ["single:s466b138f957d", "single:s93fe4e7a4f06"], "status": "REASONED"},
    "key-metrics": {"text": "metricsAuthKey gates metrics.", "components": ["single"], "sources": ["single:sf2990c7273c4"], "status": "REASONED"},
    "key-flags": {"text": "flagsAuthKey gates flags.", "components": ["single"], "sources": ["single:sf2990c7273c4"], "status": "REASONED"},
    "key-pprof": {"text": "pprofAuthKey gates debug/pprof/* including trailing slash.", "components": ["single"], "sources": ["single:sf2990c7273c4"], "status": "REASONED"}
  }
}
---
# Time-series and metrics stores: InfluxDB, VictoriaMetrics, and QuestDB

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| influx2-setup: 8086 shares API/UI/write; private onboarding creates operator user/org/token, setup allowed changes true to false, scoped app tokens. | InfluxDB OSS 2.x | REASONED |
| influx2-tls: INFLUXD_CONFIG_PATH selects config; http-bind-address, tls-cert and tls-key set private HTTPS. | InfluxDB OSS 2.x | REASONED |
| influx1-auth: 8086 auth defaults off; create admin then set bind-address, auth-enabled and HTTPS certificate/key fields. | InfluxDB OSS 1.x | REASONED |
| influx1-other: prom-read-auth-enabled=false by default; set it true with auth-enabled for remote-read auth; 8088 backup RPC defaults loopback; optional unauthenticated ingest stays disabled. | InfluxDB OSS 1.x | REASONED |
| vm-bind: Single-node HTTP fallback :8428, tcp4 default, enableTCP6 false; explicit private bind and TLS flags. | VictoriaMetrics single-node v1.152.0; VictoriaMetrics single-node source commit 540b91da031aa8b7d53d3784693bb451e2be980a | REASONED |
| vm-image: Source tag ships Compose using image v1.151.0, wildcard 8428 publication and additional ingest listeners. | VictoriaMetrics single-node v1.152.0; VictoriaMetrics shipped Compose image v1.151.0 | REASONED |
| vm-basic: Empty username disables Basic auth even with password; ordinary query/UI/HTTP ingest and aliases share the credential. | VictoriaMetrics single-node v1.152.0 | REASONED |
| vm-exempt: Health/ping/readiness/robots/favicon, OPTIONS and prefix handling exemptions differ from authenticated ready and influx/health. | VictoriaMetrics single-node v1.152.0 | REASONED |
| vm-keys: Registered endpoint keys default empty and fall back to Basic; nonempty authKey replaces Basic, wrong/missing gives 401; other aliases may require both. | VictoriaMetrics single-node v1.152.0 | REASONED |
| vm-optional: Graphite/Influx/OpenTSDB/native-query listeners default disabled; no TLS, and only OpenTSDB HTTP put checks Basic. | VictoriaMetrics single-node v1.152.0 | REASONED |
| cluster-http: vminsert/vmselect/vmstorage fall back to 8480/8481/8482 on IPv4 wildcard; optional IPv6, empty Basic credentials and HTTP-only TLS. | VictoriaMetrics cluster v1.152.0-cluster; VictoriaMetrics cluster source e4b1d55683f0da20410dc765787bd4e9b5afa0da | REASONED |
| cluster-rpc: 8400/8401 wildcard RPC has no credentials/TLS; handshake/compression permits writes, reads, deletion and metadata mutations, outside HTTP auth. | VictoriaMetrics cluster v1.152.0-cluster; VictoriaMetrics cluster source e4b1d55683f0da20410dc765787bd4e9b5afa0da | REASONED |
| cluster-native: Optional clusternativeListenAddr is disabled by default; restrict enabled native listeners to trusted cluster peers. | VictoriaMetrics cluster v1.152.0-cluster; VictoriaMetrics security/vmauth documentation unknown | REASONED |
| cluster-key-snapshot: vmstorage: -snapshotAuthKey gates /snapshot/create, /snapshot/list, /snapshot/delete and /snapshot/delete_all. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-merge: vmstorage: -forceMergeAuthKey gates /internal/force_merge. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-flush: vmstorage: -forceFlushAuthKey gates /internal/force_flush. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-logging: vmstorage: -logNewSeriesAuthKey gates /internal/log_new_series. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-delete: vmselect: -deleteAuthKey gates POSTs to /delete/{accountID}/prometheus/api/v1/admin/tsdb/delete_series and /select/{accountID}/graphite/tags/delSeries. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-cache: vmselect: -search.resetCacheAuthKey gates /internal/resetRollupResultCache. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-stats: vmselect: -metricNamesStatsResetAuthKey gates /admin/api/v1/admin/status/metric_names_stats/reset. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-metrics: All three HTTP components: -metricsAuthKey gates /metrics. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-flags: All three HTTP components: -flagsAuthKey gates /flags. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-key-pprof: All three HTTP components: -pprofAuthKey gates /debug/pprof/*. | VictoriaMetrics cluster v1.152.0-cluster | REASONED |
| cluster-precedence: Empty keys fall back to Basic; nonempty keys replace it, not add a factor or protect other routes; allowlist proxy routes. | VictoriaMetrics cluster v1.152.0-cluster; VictoriaMetrics cluster source e4b1d55683f0da20410dc765787bd4e9b5afa0da; VictoriaMetrics security/vmauth documentation unknown | REASONED |
| quest-http: 9000 HTTP/console/SQL defaults unauthenticated; set http.user/password in server.conf. 9003 health requires auth when HTTP does by default; http.health.check.authentication.required=false disables that health check requirement. | QuestDB documentation unknown | REASONED |
| quest-pg: 8812 PostgreSQL wire defaults admin/quest; replace pg.user/password and protect its separate listener. | QuestDB documentation unknown | REASONED |
| quest-ilp: 9009 TCP writes default unauthenticated; line.tcp.auth.db.path selects P-256 public-key file. | QuestDB documentation unknown | REASONED |
| quest-tls: OSS requires proxy TLS; Enterprise uses RBAC/tls.enabled and rejects HTTP credential keys since stated Enterprise 4.0.0. | QuestDB documentation unknown; QuestDB Enterprise qualification 4.0.0 | REASONED |
| verify-inventory: Inventory TCP/UDP and every enabled listener; local binds do not prove external isolation. | InfluxDB OSS 1.x; VictoriaMetrics single-node v1.152.0; VictoriaMetrics cluster v1.152.0-cluster; QuestDB documentation unknown | REASONED |
| verify-rpc: Actual storage IPs must refuse outside TCP while permitted hosts connect; protocol is not HTTP and failure alone proves no isolation. | VictoriaMetrics cluster v1.152.0-cluster; VictoriaMetrics cluster source e4b1d55683f0da20410dc765787bd4e9b5afa0da; VictoriaMetrics security/vmauth documentation unknown | REASONED |
| verify-http: Setup body, Influx1 database list/401, VM query/401 and Quest SQL/401 discriminate per target; redirects/errors are inconclusive. | InfluxDB OSS 2.x; InfluxDB OSS 1.x; VictoriaMetrics single-node v1.152.0; QuestDB documentation unknown | REASONED |
| verify-extra: Reject default PG credential separately; repeat HTTPS auth and plaintext isolation; console MFA does not protect native protocols. | QuestDB documentation unknown; VictoriaMetrics security/vmauth documentation unknown | REASONED |
| verify-keys: Read-only snapshot/list and metrics probes test empty/Basic/endpoint-key cases; health exemptions and optional listeners need separate checks. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-snapshot: snapshotAuthKey gates snapshot create/list/delete/delete_all and admin TSDB snapshot. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-delete: deleteAuthKey gates Prometheus delete_series and Graphite delSeries aliases. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-merge: forceMergeAuthKey gates internal/force_merge. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-flush: forceFlushAuthKey gates internal/force_flush. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-cache: search.resetCacheAuthKey gates internal/resetRollupResultCache. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-logging: logNewSeriesAuthKey gates internal/log_new_series. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-stats: metricNamesStatsResetAuthKey gates admin/status/metric_names_stats/reset. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-config: configAuthKey gates config and API status/config with Prometheus aliases. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-reload: reloadAuthKey gates -/reload and Prometheus alias. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-metrics: metricsAuthKey gates metrics. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-flags: flagsAuthKey gates flags. | VictoriaMetrics single-node v1.152.0 | REASONED |
| key-pprof: pprofAuthKey gates debug/pprof/* including trailing slash. | VictoriaMetrics single-node v1.152.0 | REASONED |
<!-- version-basis:end -->

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

At v1.152.0 single-node (commit `540b91da031aa8b7d53d3784693bb451e2be980a`), the HTTP API, UI and HTTP ingest share the fallback address `-httpListenAddr=:8428` when no address is supplied. It listens on every IPv4 interface by default (`tcp4`); `-enableTCP6`, default `false`, enables IPv6 too. The shipped `deployment/docker/compose-vm-single.yml` publishes `8428:8428` without a host IP, so it requests publication on every host interface by default. That example selects image v1.151.0, despite being shipped at source tag v1.152.0; it also enables and publishes additional ingest listeners.

HTTP Basic authentication uses `-httpAuth.username` and `-httpAuth.password`, both empty by default. It is disabled whenever the username is empty, even if a password is set. With a username set, one credential covers ordinary query, UI and HTTP ingest routes, including `/api/v1/import`, `/api/v1/import/csv`, `/api/v1/import/native`, the `/api/v1/import/prometheus` prefix and their supported `/prometheus` aliases, remote write, InfluxDB writes, OpenTelemetry, DataDog, New Relic and Zabbix ingestion. These ingest routes have no separate endpoint auth key.

Basic auth does not cover `/health`, `/ping`, `/-/healthy`, `/-/ready`, `/robots.txt` or any path ending in `/favicon.ico`. `/ready` and `/influx/health` do pass through Basic auth. The wrapper also answers `OPTIONS` before authentication, and handles an optional `-http.pathPrefix` redirect or missing-prefix error before authentication. Paths here are relative to that configured prefix. These responses do not demonstrate protection of data or administrative operations.

Bind the HTTP listener privately, and configure HTTPS with `-tls`, `-tlsCertFile` and `-tlsKeyFile`:

```text
-httpListenAddr=127.0.0.1:8428
-httpAuth.username=REPLACE_WITH_A_NAME
-httpAuth.password=REPLACE_WITH_A_SECRET
-tls -tlsCertFile=/etc/ssl/vm.crt -tlsKeyFile=/etc/ssl/vm.key
```

The following handlers check their own keys. Every key defaults to empty:

| Handler | Flag |
| --- | --- |
| `/snapshot/create`, `/snapshot/list`, `/snapshot/delete`, `/snapshot/delete_all`, and creation through `/api/v1/admin/tsdb/snapshot` | `-snapshotAuthKey` |
| POST `/api/v1/admin/tsdb/delete_series` and `/prometheus/api/v1/admin/tsdb/delete_series`; POST `/tags/delSeries` and `/graphite/tags/delSeries` | `-deleteAuthKey` |
| `/internal/force_merge` | `-forceMergeAuthKey` |
| `/internal/force_flush` | `-forceFlushAuthKey` |
| `/internal/resetRollupResultCache` | `-search.resetCacheAuthKey` |
| `/internal/log_new_series` | `-logNewSeriesAuthKey` |
| `/api/v1/admin/status/metric_names_stats/reset` | `-metricNamesStatsResetAuthKey` |
| `/config`, `/api/v1/status/config`, and their `/prometheus` aliases | `-configAuthKey` |
| `/-/reload` and `/prometheus/-/reload` | `-reloadAuthKey` |
| `/metrics` | `-metricsAuthKey` |
| `/flags` | `-flagsAuthKey` |
| `/debug/pprof/*` (with the slash after `pprof`) | `-pprofAuthKey` |

For these registered routes, an empty key falls back to Basic auth, leaving the operation unauthenticated if the username is also empty. A nonempty key requires a matching `authKey` request parameter and skips Basic auth; it replaces that check rather than adding a second credential. Missing or wrong keys return `401`, even with correct Basic credentials. The override is limited to the registered paths: another alias accepted by an application handler can still require Basic auth before its endpoint-key check. Setting a key does not enable the operation or protect other routes. Keep administrative, configuration and debug routes private, and use `vmauth` or a reverse proxy with TLS and per-route restrictions for client access.

Other listener flags are `-graphiteListenAddr` (TCP and UDP), `-influxListenAddr` (TCP and UDP), `-opentsdbListenAddr` (TCP and UDP, with both telnet and HTTP put on TCP), `-opentsdbHTTPListenAddr` (HTTP over TCP), and `-vmselectAddr` (cluster-native query RPC). All default to empty and are disabled while empty. Leave them disabled unless needed; bind enabled listeners privately and restrict access to trusted clients separately from the main HTTP listener. None of these listeners is given a TLS configuration, so the HTTP `-tls` settings never apply to them. `-httpAuth.*` Basic auth is checked only on OpenTSDB HTTP put requests (`-opentsdbHTTPListenAddr`, and the HTTP branch of `-opentsdbListenAddr`); Graphite, InfluxDB line protocol over TCP and UDP, and OpenTSDB telnet and UDP accept data with no authentication at all.

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

`line.tcp.auth.db.path` points at a file of P-256 public keys. The [minimal health server](https://questdb.com/docs/configuration/http-min-server/) on `9003` requires authentication when the HTTP server does by default (`http.health.check.authentication.required=true`); setting this option to `false` independently permits unauthenticated health checks. The open-source build has no native TLS, so terminate it at a reverse proxy; QuestDB Enterprise instead uses role-based access control (since Enterprise 4.0.0 it refuses to start if the `http.user` and `http.password` keys are set) and its own `tls.enabled` settings.

## The pattern, any of these

Bind every listener to loopback or a private interface, and put authentication and TLS in a layer in front, because none of these engines authenticates by default: VictoriaMetrics ships its Basic auth empty, InfluxDB 1.x ships `auth-enabled` off, and QuestDB leaves its console keys and ILP auth unset while shipping a default database credential. Change every default credential (`admin` / `quest` first), and never place an ingest or query port on the public internet. A browser sign-in or MFA layer in front of the console does not authenticate the PostgreSQL wire or line-protocol ports, which are separate listeners: bind and front those too.

## Verify

Every probe below is **REASONED, not demonstrated**: the authoring host forbids opening listeners without an isolated network namespace, and has none. Outcomes are derived from the cited vendor sources rather than observed; backlog row 2.32 tracks live exposed and fixed demonstrations. A transport failure, a redirect, a 404, a 405 or a TLS error is inconclusive, never the fixed state.

```bash
# REASONED: listener inventory; no isolated network namespace for listeners on the authoring host (row 2.32). Expected outcomes and vendor sources are recorded below.
sudo ss -tlnp    # read the whole table: 8086 and loopback 8088; 8428, 8480, 8481, 8482 and native
sudo ss -ulnp    # RPC 8400, 8401; 9000, 9003, 8812, 9009, each only on its intended private
                 # address, and no metrics or ingest port bound to a public interface
```

**REASONED, not demonstrated:** the VictoriaMetrics cluster RPC check needs a running cluster and probe hosts inside and outside its protected network, unavailable because the authoring host forbids opening listeners without an isolated network namespace, and has none. Row 2.32 tracks this demonstration. The `ss` inventory above identifies local binds; it does not prove that `8400` and `8401` are unreachable from outside the cluster network. From an outside host, substitute each storage node's actual IP below and run the whole block. Repeat from a trusted cluster host as the positive control. Use any configured replacement ports too, including enabled `-clusternativeListenAddr` listeners. The pinned RPC listener and handshake sources below explain why reachability matters.

```bash
# REASONED: cluster RPC isolation and trusted-host control; no isolated network namespace for listeners on the authoring host (row 2.32). Expected outcomes and vendor sources are recorded below.
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
# REASONED: HTTP setup, authentication and endpoint-key probes; no isolated network namespace for listeners on the authoring host (row 2.32). Expected outcomes and vendor sources are recorded below.
# Per-target discriminator: InfluxDB 2.x setup returns 200 in both states; read allowed
# (true before setup, false after). The other named data endpoints should return 401 with auth.
# Substitute a full URL on the set -- line
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

**REASONED, not demonstrated:** for v1.152.0 single-node, use the guarded URL block above against `/snapshot/list` and `/metrics` with no credentials. With empty endpoint keys and an empty Basic username, expect `200` and snapshot JSON or metrics text; with a Basic username set and the keys still empty, expect `401`. With nonempty endpoint keys, a request lacking `authKey` must return `401`. In an isolated deployment, also confirm that a correct endpoint key succeeds without Basic credentials, that Basic credentials alone cannot satisfy a nonempty endpoint key, and that ordinary query and ingest requests still require Basic auth. Do not use snapshot creation, deletion or ingestion as a read-only probe. `/health` and `/-/ready` remain unauthenticated under native Basic auth; their success is not a failed data-auth check. Include every enabled optional listener in the `ss` inventory and outside-network isolation checks. The authoring host forbids opening listeners without an isolated network namespace, and has none; row 2.32 retains these demonstrations.

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
- VictoriaMetrics v1.152.0 single-node (commit 540b91da031aa8b7d53d3784693bb451e2be980a) [HTTP fallback and startup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/victoria-metrics/main.go#L91-L114), [registered key routes and dispatch](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/victoria-metrics/main.go#L137-L201), [TCP listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/netutil/tcplistener.go#L16-L43) and [IPv4/IPv6 selection](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/netutil/tcplistener.go#L79-L85).
- VictoriaMetrics v1.152.0 [HTTP auth and TLS flags](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L38-L57), [prefix and OPTIONS handling](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L385-L419), [built-in exemptions and key routes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L425-L510), [key precedence and Basic fallback](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/httpserver/httpserver.go#L534-L573), and [empty password/key defaults](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/flagutil/password.go#L16-L30).
- VictoriaMetrics v1.152.0 [storage key flags and optional RPC address](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmstorage/main.go#L38-L46), [logging key](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmstorage/main.go#L111), [conditional RPC startup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmstorage/main.go#L184-L197), and [maintenance and snapshot handlers](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmstorage/main.go#L250-L375).
- VictoriaMetrics v1.152.0 [query-side key flags](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmselect/main.go#L33-L37), [alias normalization](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmselect/main.go#L99-L111), [rollup-cache reset](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmselect/main.go#L174-L179), and [deletion and metric-name reset](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vmselect/main.go#L377-L435).
- VictoriaMetrics v1.152.0 [optional ingest listeners and config/reload keys](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L49-L70), [conditional listener startup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L90-L107), [HTTP ingest routes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L138-L303), and [configuration, reload and authenticated readiness handlers](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/app/vminsert/main.go#L351-L387).
- VictoriaMetrics v1.152.0 (shipped image v1.151.0) [shipped Compose image, publications and listener flags](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/deployment/docker/compose-vm-single.yml#L18-L37).
- VictoriaMetrics v1.152.0 raw ingest listeners (no TLS configuration; Basic auth only on OpenTSDB HTTP): [Graphite](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/graphite/server.go#L46-L53), [InfluxDB](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/influx/server.go#L46-L52), [OpenTSDB mixed listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/opentsdb/server.go#L49-L60), [OpenTSDB HTTP listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/opentsdbhttp/server.go#L36-L36) and [its Basic-auth check](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0/lib/ingestserver/opentsdbhttp/server.go#L88-L92).
- VictoriaMetrics v1.152.0-cluster HTTP fallback binds: [vminsert](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L161-L167), [vmselect](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L150-L158), [vmstorage and RPC startup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L221-L244); [RPC address defaults and storage auth-key flags](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L46-L68).
- VictoriaMetrics v1.152.0-cluster TCP bind implementation and IPv4 default: [listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/netutil/tcplistener.go#L16-L43), [network selection](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/netutil/tcplistener.go#L79-L85); optional cluster-native listeners: [vminsert](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vminsert/main.go#L53-L54), [vmselect](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L77-L78).
- VictoriaMetrics v1.152.0-cluster RPC handshake: [protocol identifiers](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L17-L23), [insert hello check](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L77-L109), [select hello check](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L137-L158), [compression negotiation without credentials](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/handshake/handshake.go#L203-L233).
- VictoriaMetrics v1.152.0-cluster RPC capabilities: [storage writes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/vmstorage.go#L109-L124), [plaintext select listener](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/vmselectapi/server.go#L94-L101), [RPC dispatch including deletion, registration and reset](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/vmselectapi/server.go#L558-L588), [storage deletion and mutations](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/vmstorage.go#L318-L352).
- VictoriaMetrics v1.152.0-cluster insert accept-to-write path: [listener and handshake setup](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L54-L75), [accept, handshake and connection processing](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L78-L144), [legacy and RPC dispatch](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L172-L226), [storage write callbacks](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/vminsertapi/server.go#L255-L267); [nil TLS config returns a plaintext connection](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/netutil/tcplistener.go#L107-L140) (vmstorage passes nil at the RPC startup cited above).
- VictoriaMetrics v1.152.0-cluster HTTP auth: [flags and HTTP TLS scope](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L38-L57), [metrics, flags and pprof routes](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L461-L510), [endpoint-key precedence and Basic-auth fallback](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/lib/httpserver/httpserver.go#L534-L573).
- VictoriaMetrics v1.152.0-cluster password and auth-key defaults: [NewPassword stores an empty string](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/flagutil/password.go#L21-L30), [Get reads it unchanged when no source is configured](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/e4b1d55683f0da20410dc765787bd4e9b5afa0da/lib/flagutil/password.go#L54-L68).
- VictoriaMetrics v1.152.0-cluster maintenance: [storage handler auth routing](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L279-L288), [merge, flush, logging and snapshots](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmstorage/main.go#L307-L420), [select cache resets](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L269-L296), [rollup-cache key](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/prometheus/prometheus.go#L57-L60), [Graphite deletion](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L580-L594), [Prometheus deletion](https://github.com/VictoriaMetrics/VictoriaMetrics/blob/v1.152.0-cluster/app/vmselect/main.go#L867-L884).
- VictoriaMetrics cluster security recommendations (private network, HTTPS auth proxy and endpoint allowlists): https://docs.victoriametrics.com/victoriametrics/cluster-victoriametrics/#security
- vmauth authorization proxy: https://docs.victoriametrics.com/victoriametrics/vmauth/
- QuestDB HTTP server (Enterprise 4.0.0 qualification recorded above; `9000`, `http.user` / `http.password` unset by default): https://questdb.com/docs/configuration/http-server/
- QuestDB PostgreSQL wire protocol (`8812`, default `admin` / `quest`): https://questdb.com/docs/configuration/postgres-wire-protocol/
- QuestDB ingestion / line protocol (`9009`, `line.tcp.auth.db.path` default none): https://questdb.com/docs/configuration/ingestion/

- QuestDB minimal HTTP server (`9003`, `http.health.check.authentication.required` defaults to `true`; `false` permits unauthenticated health checks): https://questdb.com/docs/configuration/http-min-server/
