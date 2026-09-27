---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "3fbdc6ab2236595ce5a612471d7982a0d8e0364fcb2c2103a72b8aeb729d5441",
  "components": {
    "node": {
      "name": "node_exporter",
      "basis": "v1.12.1",
      "sources": {
        "s9cc780c8cd13": "https://github.com/prometheus/node_exporter/blob/v1.12.1/README.md",
        "s896899f5a500": "https://github.com/prometheus/node_exporter/blob/v1.12.1/node_exporter.go"
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
    "jaeger-docs": {
      "name": "Jaeger documentation",
      "basis": "4d150659ee4ed3ccc69253ec77c368392f59e625",
      "sources": {
        "s2c0a96684979": "https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/configuration.md",
        "s4969c5ffaa59": "https://github.com/jaegertracing/documentation/blob/4d150659ee4ed3ccc69253ec77c368392f59e625/content/docs/v2/2.21/deployment/security.md"
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
        "sfb3d52071e7c": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L193-L248",
        "scf12ae06cdc4": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L373-L390",
        "s970473c2dcdb": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1130-L1138",
        "s6b2f01173a97": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1241-L1262",
        "s44e7547da37d": "https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2532-L2561",
        "s33f320afa73a": "https://github.com/grafana/loki/blob/v3.7.8/go.mod#L55"
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
        "s1b539b8100a3": "https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1577-L1672"
      }
    },
    "go": {
      "name": "Go documentation",
      "basis": "unknown",
      "sources": {
        "sd3b3c1c431ec": "https://pkg.go.dev/crypto/tls#ClientAuthType",
        "s37204ff1b27c": "https://pkg.go.dev/net#Listen"
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
    "push-write": {"text": "Anonymous loopback POST wrote a series visible on metrics and DELETE removed the group.", "components": ["push"], "sources": ["push:s5c9f9745f42d"], "status": "DEMONSTRATED", "evidence": "an unauthenticated `POST /metrics/job/demo` returned `200` and the series appeared on `/metrics`. An unauthenticated `DELETE` of the group returned `202`."},
    "push-pprof": {"text": "pprof is registered outside flag checks and returned 200 on loopback.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "DEMONSTRATED", "evidence": "`/debug/pprof/` is registered outside every flag check in the source, and it answered `200`."},
    "push-admin": {"text": "Admin wipe defaults off; loopback PUT /api/v1/admin/wipe returned 404 without --web.enable-admin-api.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "DEMONSTRATED", "evidence": "`PUT /api/v1/admin/wipe` returned `404` by default."},
    "push-lifecycle": {"text": "Lifecycle shutdown defaults off; leave --web.enable-lifecycle and the admin API disabled.", "components": ["push"], "sources": ["push:s17fa4021d868"], "status": "REASONED"},
    "push-auth": {"text": "Web configuration covers all HTTP endpoints; anonymous push returned 401 and authenticated push 200.", "components": ["push", "toolkit"], "sources": ["push:s5c9f9745f42d", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "an unauthenticated push returned `401` and an authenticated one returned `200`."},
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
    "loki-listeners": {"text": "Empty TCP listen addresses yield wildcard HTTP 3100 and gRPC 9095; IPv4/IPv6 depends on Go/OS support.", "components": ["loki", "dskit", "go"], "sources": ["loki:s9fd7d8bd80e3", "dskit:sb19d54a19636", "dskit:s7848c6311aee", "go:s37204ff1b27c"], "status": "REASONED"},
    "loki-samples": {"text": "Local sample uses gRPC 9096/auth_enabled false; production Docker config uses wildcard 3100/9095/auth_enabled true.", "components": ["loki"], "sources": ["loki:s924fd8ffd310", "loki:s985dfb0ea97c"], "status": "REASONED"},
    "memberlist-bind": {"text": "With the memberlist store, TCP gossip defaults 0.0.0.0:7946; an empty list selects wildcard and an empty list entry is invalid.", "components": ["loki", "dskit"], "sources": ["loki:s33f320afa73a", "dskit:s23d81aeedf07", "dskit:s4d546b0d82d4"], "status": "REASONED"},
    "memberlist-label": {"text": "Cluster labels reject mismatches unless verification is disabled, but matching labels are not credentials; no SecretKey/keyring setting is wired.", "components": ["dskit"], "sources": ["dskit:s052e8107edad", "dskit:scf57b6b1f148"], "status": "REASONED"},
    "memberlist-updates": {"text": "Without TLS, reachable matching-label peers can submit KV/ring state subject to codecs/merge rules; disruption is inferred, not demonstrated.", "components": ["dskit"], "sources": ["dskit:scf57b6b1f148", "dskit:s69c68f3d3e6a", "dskit:s1b539b8100a3"], "status": "REASONED"},
    "memberlist-tls": {"text": "TLS defaults off; enabled transport verifies outgoing servers but leaves incoming ClientAuth at NoClientCert, so it is not mutual peer authentication.", "components": ["dskit", "go"], "sources": ["dskit:s23d81aeedf07", "dskit:s4d546b0d82d4", "dskit:s675104c4819c", "dskit:s99e7e34182f1", "go:sd3b3c1c431ec"], "status": "REASONED"},
    "memberlist-policy": {"text": "Keep tls-insecure-skip-verify false, set expected server name as needed, bind privately and restrict trusted peers even with TLS.", "components": ["dskit"], "sources": ["dskit:s675104c4819c", "dskit:s99e7e34182f1"], "status": "REASONED"},
    "memberlist-advertise": {"text": "Advertise address/port affect discovery, not bind; absent overrides derive an address from the first bind and actual port.", "components": ["dskit"], "sources": ["dskit:s251174df8783", "dskit:s052e8107edad"], "status": "REASONED"},
    "loki-tenants": {"text": "auth_enabled defaults true and requires tenant headers, not credentials; false uses fake, and tenant validation checks syntax/length only.", "components": ["loki", "dskit"], "sources": ["loki:sd13fa86b20d0", "loki:sb5e56f0d6348", "dskit:s3634557bb838", "dskit:s1ca109a7a016"], "status": "REASONED"},
    "loki-grpc-auth": {"text": "Default dskit interceptors lack credentials; Loki has tenant exemptions, and the supplied subset omits full auth-helper implementation.", "components": ["dskit", "loki"], "sources": ["dskit:s38beab6892ea", "dskit:saf57a4cbc682", "loki:s057e686b00bb"], "status": "REASONED"},
    "loki-push-query": {"text": "Reachable clients can push/query without credentials subject to tenant headers and ingest/query policies.", "components": ["loki"], "sources": ["loki:s9f316e1a5fef", "loki:s39c270ed878c"], "status": "REASONED"},
    "loki-config": {"text": "GET /config exposes configuration without a tenant-auth wrapper.", "components": ["loki"], "sources": ["loki:sbe0aa939a44d"], "status": "REASONED"},
    "loki-diagnostics": {"text": "Metrics and pprof routes are registered by default without a tenant-auth wrapper.", "components": ["dskit"], "sources": ["dskit:s761b46738198"], "status": "REASONED"},
    "loki-maintenance": {"text": "Ingester flush/shutdown accept GET/POST; prepare_shutdown accepts POST/GET/DELETE, without tenant-auth wrappers.", "components": ["loki"], "sources": ["loki:sc2b013001317"], "status": "REASONED"},
    "loki-delete": {"text": "Non-worker compactor deletion routes need a supported shipper index, retention and delete-request-store; tenant/policy middleware applies and omitted handlers limit the trace.", "components": ["loki"], "sources": ["loki:s4f3a19f7f08c", "loki:s3d51e1213e70", "loki:s38c1e77fe01e", "loki:s1f38431776f2"], "status": "REASONED"},
    "loki-grpc-bridge": {"text": "Single-binary ingester RPC and HTTP-over-gRPC expose paths that HTTP-only TLS/proxying does not protect.", "components": ["loki", "dskit"], "sources": ["loki:sc2b013001317", "dskit:s5fd7b12bfcf1"], "status": "REASONED"},
    "loki-mtls": {"text": "HTTP/gRPC TLS defaults empty and requires a cert/key pair; configure client CA plus RequireAndVerifyClientCert, not CA alone.", "components": ["dskit"], "sources": ["dskit:sb19d54a19636", "dskit:s0dc9a01e591a", "dskit:sd35a28be4391"], "status": "REASONED"},
    "loki-ring": {"text": "Single-binary overlay uses inmemory ring, loopback instance address and replication_factor 1 instead of default 3; check no gossip listener remains.", "components": ["loki"], "sources": ["loki:s8f06ddfa5291", "loki:s8cf14a90ec61", "loki:sfb3d52071e7c"], "status": "REASONED"},
    "loki-internal": {"text": "Loopback gRPC is a configuration-specific recommendation; verify advertised/dial addresses and successful internal worker, ingester and compactor calls.", "components": ["loki"], "sources": ["loki:s765907d2b4ee", "loki:sfb3d52071e7c", "loki:scf12ae06cdc4", "loki:s970473c2dcdb", "loki:s6b2f01173a97", "loki:s44e7547da37d"], "status": "REASONED"},
    "loki-grpc-tls": {"text": "gRPC TLS requires compatible TLS on every internal client; local users can reach plaintext loopback and mTLS does not supply tenant headers.", "components": ["dskit", "loki"], "sources": ["dskit:sd35a28be4391", "loki:s70975c2655fa"], "status": "REASONED"},
    "loki-proxy": {"text": "An authenticating proxy must overwrite X-Scope-OrgID with its identity and be the only caller that can reach Loki.", "components": ["loki"], "sources": ["loki:s70975c2655fa"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory every TCP/UDP listener; wildcard defaults, all Loki listeners and off-host isolation were not observed.", "components": ["node", "alert", "push", "jaeger", "dskit"], "sources": ["node:s896899f5a500", "alert:s0fd66cba968e", "push:s5c9f9745f42d", "jaeger:s5619bba2be59", "dskit:sb19d54a19636", "dskit:s23d81aeedf07"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "External 200 exposes unauthenticated HTTP; HTTPS 401 shows auth, not isolation. Confirm connection failures and a permitted positive control.", "components": ["security", "toolkit", "jaeger-docs"], "sources": ["security:s3ffe42e99660", "toolkit:sbb86207a38e5", "jaeger-docs:s4969c5ffaa59"], "status": "REASONED", "verify": [2]},
    "verify-loki": {"text": "A tenant-header rejection is not authentication; repeat with an arbitrary X-Scope-OrgID and test both families, gRPC and internal RPCs.", "components": ["loki"], "sources": ["loki:s70975c2655fa", "loki:s057e686b00bb"], "status": "REASONED", "verify": [2]},
    "verify-basic": {"text": "Loopback HTTPS GETs on node/Pushgateway metrics, Alertmanager status and Jaeger v3 services gave no-credential 401 and credentialed 200.", "components": ["node", "push", "alert", "jaeger", "toolkit"], "sources": ["node:s896899f5a500", "push:s5c9f9745f42d", "alert:s120d6ecf3fcd", "jaeger:sc6f47d82b947", "toolkit:sbb86207a38e5"], "status": "DEMONSTRATED", "evidence": "The loopback runs gave exactly that pair over HTTPS for GETs of node_exporter `/metrics`, Pushgateway `/metrics`, Alertmanager `/api/v2/status` and Jaeger `/api/v3/services`.", "verify": [3]},
    "verify-loki-mtls": {"text": "Authorized HTTP mTLS should succeed, untrusted/missing client certs fail handshake and plaintext fail; no Loki listener/TLS run occurred.", "components": ["loki", "dskit"], "sources": ["loki:s70975c2655fa", "dskit:sd35a28be4391"], "status": "REASONED"},
    "verify-secret": {"text": "Basic-auth stdin closes argv exposure only; shell history and tracing can still leak the password. curl diagnostics lack a Sources citation.", "components": ["toolkit"], "sources": ["toolkit:sbb86207a38e5"], "status": "REASONED"}
  }
}
---
# Self-hosted observability components: node_exporter, Alertmanager, Pushgateway, Jaeger, and Loki

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| node-bind: node_exporter defaults to :9100 on all interfaces; private binds are required. | node_exporter v1.12.1; Go documentation unknown | REASONED |
| node-open: Unconfigured loopback metrics and pprof both returned 200 without credentials. | node_exporter v1.12.1 | DEMONSTRATED |
| toolkit-config: --web.config.file enables TLS and bcrypt Basic auth across HTTP paths; the format is experimental and not every exporter uses it. | Exporter toolkit v0.17.1; node_exporter v1.12.1; Alertmanager v0.34.1; Pushgateway v1.11.3 | REASONED |
| node-tls: Loopback HTTP returned 400; HTTPS metrics/pprof rejected absent credentials and accepted correct ones. | node_exporter v1.12.1; Exporter toolkit v0.17.1 | DEMONSTRATED |
| toolkit-mtls: Use RequireAndVerifyClientCert with client_ca_file for verified clients; other client_auth_type values are called insecure by the toolkit. | Exporter toolkit v0.17.1 | REASONED |
| toolkit-reload: The toolkit rereads web configuration per request; password/certificate changes apply without restart. | Exporter toolkit v0.17.1 | REASONED |
| toolkit-clients: Basic auth suits a few users; supply matching credentials/CA to scrapers, pushers and Alertmanager clients, or use client certificates/proxy login. | Exporter toolkit v0.17.1; Alertmanager v0.34.1; Pushgateway v1.11.3 | REASONED |
| alert-bind: Alertmanager HTTP defaults :9093; HA gossip defaults 0.0.0.0:9094 and needs both TCP and UDP. | Alertmanager v0.34.1; Go documentation unknown | REASONED |
| alert-api: Loopback anonymous status, silence creation, reload and pprof succeeded; status carried wildcard CORS. | Alertmanager v0.34.1; Prometheus security model a0d29881382ad1ea20597d34fc4229984b326576 | DEMONSTRATED |
| alert-auth: Web configuration rejected anonymous silence creation and absent/wrong status passwords; valid status credentials succeeded. | Alertmanager v0.34.1; Exporter toolkit v0.17.1 | DEMONSTRATED |
| alert-gossip-off: An empty --cluster.listen-address disabled both gossip socket protocols in the loopback run. | Alertmanager v0.34.1 | DEMONSTRATED |
| alert-gossip-tls: HA gossip is plaintext without experimental --cluster.tls-config; restrict it to peers and configure server/client TLS sections. | Alertmanager v0.34.1 | REASONED |
| alert-proxy: Proxy mutating routes/CORS to reduce CSRF; send Prometheus traffic to every Alertmanager rather than load-balancing it. | Prometheus security model a0d29881382ad1ea20597d34fc4229984b326576; Alertmanager v0.34.1 | REASONED |
| push-bind: Pushgateway defaults :9091; reachable users can forge trusted series, particularly with honor_labels. | Pushgateway v1.11.3; Prometheus security model a0d29881382ad1ea20597d34fc4229984b326576 | REASONED |
| push-write: Anonymous loopback POST wrote a series visible on metrics and DELETE removed the group. | Pushgateway v1.11.3 | DEMONSTRATED |
| push-pprof: pprof is registered outside flag checks and returned 200 on loopback. | Pushgateway v1.11.3 | DEMONSTRATED |
| push-admin: Admin wipe defaults off; loopback PUT /api/v1/admin/wipe returned 404 without --web.enable-admin-api. | Pushgateway v1.11.3 | DEMONSTRATED |
| push-lifecycle: Lifecycle shutdown defaults off; leave --web.enable-lifecycle and the admin API disabled. | Pushgateway v1.11.3 | REASONED |
| push-auth: Web configuration covers all HTTP endpoints; anonymous push returned 401 and authenticated push 200. | Pushgateway v1.11.3; Exporter toolkit v0.17.1 | DEMONSTRATED |
| jaeger-config: No --config selects in-memory all-in-one; receiver/diagnostic hosts use JAEGER_LISTEN_HOST with localhost fallback. | Jaeger v2.21.0; Jaeger documentation 4d150659ee4ed3ccc69253ec77c368392f59e625 | REASONED |
| jaeger-receivers: All-in-one maps OTLP 4317/4318, Jaeger 14250/14268 and UDP 6831/6832, Zipkin 9411 and sampling 5778/5779. | Jaeger v2.21.0 | REASONED |
| jaeger-diagnostics: Health 13133, expvar 27777, zpages 27778 and metrics 8888 follow JAEGER_LISTEN_HOST. | Jaeger v2.21.0 | REASONED |
| jaeger-loopback: The overridden loopback run showed every listed receiver/diagnostic listener, including UDP, on 127.0.0.1. | Jaeger v2.21.0 | DEMONSTRATED |
| jaeger-image: The official image sets JAEGER_LISTEN_HOST=0.0.0.0, exposing these listeners to its interfaces and published ports. | Jaeger v2.21.0 | REASONED |
| jaeger-query: Query HTTP 16686 and gRPC 16685 default wildcard independently of JAEGER_LISTEN_HOST; bind both explicitly. | Jaeger v2.21.0; Jaeger documentation 4d150659ee4ed3ccc69253ec77c368392f59e625 | REASONED |
| jaeger-mcp: All-in-one enables ai.mcp on the query HTTP port at /api/ai/mcp/; remove mcp from ai when unused. | Jaeger v2.21.0 | REASONED |
| jaeger-open: Anonymous loopback v3 services, UI and MCP initialize returned 200; removed v1 services returned 404, not proof of protection. | Jaeger v2.21.0 | DEMONSTRATED |
| jaeger-basic: Query basicauth/server with htpasswd rejected absent/wrong credentials on services, UI and MCP; correct credentials returned 200. | Jaeger v2.21.0; OpenTelemetry basicauth extension v0.160.0 | DEMONSTRATED |
| jaeger-tls: Query HTTP TLS cert_file/key_file gave HTTPS 401/200 and plaintext 400; inferred wiring was tested locally and needs upgrade retesting. | Jaeger v2.21.0; OpenTelemetry configtls v1.66.0 | DEMONSTRATED |
| jaeger-grpc: Query gRPC auth exists but was not demonstrated; restrict it, authenticate remote collectors separately and front human UI access. | Jaeger v2.21.0; Jaeger documentation 4d150659ee4ed3ccc69253ec77c368392f59e625 | REASONED |
| loki-listeners: Empty TCP listen addresses yield wildcard HTTP 3100 and gRPC 9095; IPv4/IPv6 depends on Go/OS support. | Loki v3.7.8; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742; Go documentation unknown | REASONED |
| loki-samples: Local sample uses gRPC 9096/auth_enabled false; production Docker config uses wildcard 3100/9095/auth_enabled true. | Loki v3.7.8 | REASONED |
| memberlist-bind: With the memberlist store, TCP gossip defaults 0.0.0.0:7946; an empty list selects wildcard and an empty list entry is invalid. | Loki v3.7.8; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| memberlist-label: Cluster labels reject mismatches unless verification is disabled, but matching labels are not credentials; no SecretKey/keyring setting is wired. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| memberlist-updates: Without TLS, reachable matching-label peers can submit KV/ring state subject to codecs/merge rules; disruption is inferred, not demonstrated. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| memberlist-tls: TLS defaults off; enabled transport verifies outgoing servers but leaves incoming ClientAuth at NoClientCert, so it is not mutual peer authentication. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742; Go documentation unknown | REASONED |
| memberlist-policy: Keep tls-insecure-skip-verify false, set expected server name as needed, bind privately and restrict trusted peers even with TLS. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| memberlist-advertise: Advertise address/port affect discovery, not bind; absent overrides derive an address from the first bind and actual port. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| loki-tenants: auth_enabled defaults true and requires tenant headers, not credentials; false uses fake, and tenant validation checks syntax/length only. | Loki v3.7.8; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| loki-grpc-auth: Default dskit interceptors lack credentials; Loki has tenant exemptions, and the supplied subset omits full auth-helper implementation. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742; Loki v3.7.8 | REASONED |
| loki-push-query: Reachable clients can push/query without credentials subject to tenant headers and ingest/query policies. | Loki v3.7.8 | REASONED |
| loki-config: GET /config exposes configuration without a tenant-auth wrapper. | Loki v3.7.8 | REASONED |
| loki-diagnostics: Metrics and pprof routes are registered by default without a tenant-auth wrapper. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| loki-maintenance: Ingester flush/shutdown accept GET/POST; prepare_shutdown accepts POST/GET/DELETE, without tenant-auth wrappers. | Loki v3.7.8 | REASONED |
| loki-delete: Non-worker compactor deletion routes need a supported shipper index, retention and delete-request-store; tenant/policy middleware applies and omitted handlers limit the trace. | Loki v3.7.8 | REASONED |
| loki-grpc-bridge: Single-binary ingester RPC and HTTP-over-gRPC expose paths that HTTP-only TLS/proxying does not protect. | Loki v3.7.8; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| loki-mtls: HTTP/gRPC TLS defaults empty and requires a cert/key pair; configure client CA plus RequireAndVerifyClientCert, not CA alone. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| loki-ring: Single-binary overlay uses inmemory ring, loopback instance address and replication_factor 1 instead of default 3; check no gossip listener remains. | Loki v3.7.8 | REASONED |
| loki-internal: Loopback gRPC is a configuration-specific recommendation; verify advertised/dial addresses and successful internal worker, ingester and compactor calls. | Loki v3.7.8 | REASONED |
| loki-grpc-tls: gRPC TLS requires compatible TLS on every internal client; local users can reach plaintext loopback and mTLS does not supply tenant headers. | dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742; Loki v3.7.8 | REASONED |
| loki-proxy: An authenticating proxy must overwrite X-Scope-OrgID with its identity and be the only caller that can reach Loki. | Loki v3.7.8 | REASONED |
| verify-inventory: Inventory every TCP/UDP listener; wildcard defaults, all Loki listeners and off-host isolation were not observed. | node_exporter v1.12.1; Alertmanager v0.34.1; Pushgateway v1.11.3; Jaeger v2.21.0; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| verify-external: External 200 exposes unauthenticated HTTP; HTTPS 401 shows auth, not isolation. Confirm connection failures and a permitted positive control. | Prometheus security model a0d29881382ad1ea20597d34fc4229984b326576; Exporter toolkit v0.17.1; Jaeger documentation 4d150659ee4ed3ccc69253ec77c368392f59e625 | REASONED |
| verify-loki: A tenant-header rejection is not authentication; repeat with an arbitrary X-Scope-OrgID and test both families, gRPC and internal RPCs. | Loki v3.7.8 | REASONED |
| verify-basic: Loopback HTTPS GETs on node/Pushgateway metrics, Alertmanager status and Jaeger v3 services gave no-credential 401 and credentialed 200. | node_exporter v1.12.1; Pushgateway v1.11.3; Alertmanager v0.34.1; Jaeger v2.21.0; Exporter toolkit v0.17.1 | DEMONSTRATED |
| verify-loki-mtls: Authorized HTTP mTLS should succeed, untrusted/missing client certs fail handshake and plaintext fail; no Loki listener/TLS run occurred. | Loki v3.7.8; dskit 8d1c6d34bb5a42b04caa982d68403c5a643bb742 | REASONED |
| verify-secret: Basic-auth stdin closes argv exposure only; shell history and tracing can still leak the password. curl diagnostics lack a Sources citation. | Exporter toolkit v0.17.1 | REASONED |
<!-- version-basis:end -->

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
The supplied source subset lacks the auth helper implementation, so its complete interceptor
behaviour has not been re-traced here. Do not expose gRPC on the strength of `auth_enabled`.

A reachable client without credentials can submit logs through `POST /loki/api/v1/push` and query
through `/loki/api/v1/query` or `/loki/api/v1/query_range`, subject to tenant headers and ingestion
or query policies. `GET /config` exposes configuration; `/metrics` and `/debug/pprof/` are
registered by default. These routes have no tenant-auth wrapper. When the ingester runs,
`GET` or `POST /flush` and `GET` or `POST /ingester/shutdown` call maintenance handlers without
that wrapper; `/ingester/prepare_shutdown` also accepts `POST`, `GET` and `DELETE`.
When the compactor runs outside its worker mode (which returns before these routes are registered), with a TSDB or boltdb-shipper index in the schema (without one it logs that it is not starting and registers nothing, with no error) and `retention_enabled: true` (which also requires `compactor.delete-request-store`, or startup fails), `/loki/api/v1/delete` accepts
`PUT`/`POST` to request deletion, `GET` to list requests and `DELETE` to cancel one.
Those deletion routes do have tenant-header and deletion tenant-policy middleware; availability
does not mean unconditional deletion. The supplied subset lacks those policy and handler
implementations. The gRPC listener registers ingester push/query services in single-binary mode
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
  can override it. The ingester advertises the server gRPC port, and distributor and querier
  construction receive the ingester ring and client configuration. The querier worker receives the
  gRPC listen address and port. A single-binary compactor client uses that listen address and port
  when deletion filtering is enabled. The supplied source subset omits the worker and ingester
  client implementations, so the complete dial path is not established here. Loopback is a
  recommendation for this configuration, not a guarantee for every single-binary deployment:
  verify advertised addresses, worker/frontend/scheduler settings, successful pushes and queries,
  and any compactor calls. Remote components need a private address reachable from their hosts.

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

The non-Loki HTTP results below were demonstrated on 127.0.0.1 against the versions named at the top,
in both the exposed state and the fixed state. All Loki checks are REASONED: the authoring host
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

Exposed, the reasoned expectation is `*:9100` (or `0.0.0.0:`/`[::]:`) for an unconfigured node_exporter,
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

Any `200` is the finding: that service answers the unauthenticated request. For a service that uses
TLS, switch that URL to `https`. A `401` then means its authentication is on. From a host that should
be blocked, a connection refusal or a connect timeout is consistent with isolation. Read the `err`
text to confirm it happened while connecting, not in a local proxy or policy. The write-out fields need
curl 7.75.0 or newer. For Loki, a `401` without a tenant header proves nothing. Repeat the Loki probe
with `-H 'X-Scope-OrgID: anyone'` added, and treat a `200` as exposure.

Run the positive control from a host that should have access, so a dead service is not read as fixed.
The password reaches curl on stdin, not argv. Substitute inside the quotes, and add
`--cacert /path/to/ca.crt` if the certificate is private.

DEMONSTRATED: following block; the recorded loopback HTTPS GETs for node_exporter, Pushgateway, Alertmanager and Jaeger returned 401 without credentials and 200 with them.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
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
- dskit pinned listener and TLS flag defaults: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L189-L212
- Loki v3.7.8 HTTP port override: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L241-L269
- Loki v3.7.8 production Docker listener overrides: https://github.com/grafana/loki/blob/v3.7.8/production/docker/config/loki.yaml#L1-L8
- Loki v3.7.8 auth setup and gRPC exemptions: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L495-L509
- Loki v3.7.8 fake HTTP tenant propagation: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L208-L222
- Loki v3.7.8 push routes and middleware: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L399-L422
- Loki v3.7.8 query frontend middleware and routes: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1307-L1378
- Loki v3.7.8 config route: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/loki.go#L533-L540
- Loki v3.7.8 ingester gRPC services and maintenance routes: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L751-L790
- Loki v3.7.8 conditional deletion routes and middleware (compactor worker mode returns first): https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1866-L1869 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1880-L1883 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1899-L1908 ; https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1935-L1952
- Loki v3.7.8 worker connection inputs: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L571-L580
- Loki v3.7.8 common ring propagation to ingester: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/config_wrapper.go#L193-L248
- Loki v3.7.8 ingester clients receive ring configuration: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L373-L390
- Loki v3.7.8 querier ingester-client construction: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1130-L1138
- Loki v3.7.8 single-binary compactor address: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L1241-L1262
- Loki v3.7.8 conditional compactor gRPC client: https://github.com/grafana/loki/blob/v3.7.8/pkg/loki/modules.go#L2532-L2561
- dskit pinned TLS YAML fields: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L69-L78
- dskit pinned wildcard listener construction: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L309-L332
- dskit pinned server TLS and client-auth construction: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/server/server.go#L357-L395
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
- dskit pinned remote-state merging and codec validation: https://github.com/grafana/dskit/blob/8d1c6d34bb5a42b04caa982d68403c5a643bb742/kv/memberlist/memberlist_client.go#L1577-L1672
- Go `net.Listen` (an empty host listens on all addresses): https://pkg.go.dev/net#Listen
