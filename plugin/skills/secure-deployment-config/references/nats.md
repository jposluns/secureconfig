---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "8f17c627f469ebbbc600ed5d802a56587389bcb15d9fe006839b42735b703f1a",
  "components": {
    "server": {
      "name": "NATS Server",
      "basis": "v2.14.7",
      "sources": {
        "s67d42c6498ac": "https://github.com/nats-io/nats-server/releases/tag/v2.14.7",
        "sfcf4d67bc409": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go",
        "s77d2cf7237a9": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/client.go",
        "sdef33959305a": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/monitor.go",
        "sbf04a3dffd21": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/consumer.go",
        "s0015a19a5fb9": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/jetstream_api.go",
        "sfe9cfda67037": "https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/auth_callout.go"
      }
    },
    "commit": {
      "name": "NATS baseline commit",
      "basis": "8d8b69a8c46a46a150eabb7f312607c4d9c58faf",
      "sources": {
        "sa981814d2443": "https://github.com/nats-io/nats-server/commit/8d8b69a8c46a46a150eabb7f312607c4d9c58faf"
      }
    },
    "library": {
      "name": "NATS image catalogue",
      "basis": "dcd3db677d8919c3a42d369bd48a6f1c234b3ae8",
      "sources": {
        "s5820f80dc5e2": "https://github.com/docker-library/official-images/blob/dcd3db677d8919c3a42d369bd48a6f1c234b3ae8/library/nats#L6-L50"
      }
    },
    "image": {
      "name": "NATS image source",
      "basis": "0e72748d3cb553ccdb8c2da7c75ec3b767be51a5",
      "sources": {
        "s63fd80eda93f": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/scratch/nats-server.conf",
        "sf75fdfff87fb": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/nats-server.conf",
        "sb6bb995a1296": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/nanoserver-ltsc2022/nats-server.conf",
        "sb2004ba92e96": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/nats-server.conf",
        "s63901565fdae": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/scratch/nats-server.conf",
        "s052d6780e740": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/nats-server.conf",
        "s942be49c75fa": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/nanoserver-ltsc2022/nats-server.conf",
        "s4152555c0fa5": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/nats-server.conf",
        "sac24f019f564": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/scratch/Dockerfile#L5-L9",
        "s60e57b8083a9": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/Dockerfile#L38-L43",
        "s38262af3382e": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/docker-entrypoint.sh#L7-L9",
        "sa8e0a5d725c4": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/docker-entrypoint.sh#L7-L9",
        "s56fa48bb22a4": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/nanoserver-ltsc2022/Dockerfile#L5-L9",
        "s221e831d1482": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/Dockerfile#L44-L48",
        "sf46270db6983": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/Dockerfile#L44-L48",
        "s242baf7508a4": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/nanoserver-ltsc2022/Dockerfile#L5-L9",
        "s1be190b618be": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/scratch/Dockerfile#L5-L9",
        "s0d4076849de7": "https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/Dockerfile#L38-L43"
      }
    },
    "image-server": {
      "name": "NATS image listener source",
      "basis": "v2.15.0",
      "sources": {
        "se8793d3c33b3": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/const.go#L85-L86",
        "s9860c7a8a315": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/opts.go#L6265-L6266",
        "s4f35f43b860b": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/server.go#L2874-L2880",
        "s6d1b9c207c22": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/server.go#L3132-L3138",
        "s63fb63ed420f": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/route.go#L2752-L2753",
        "s483a2d169cbf": "https://github.com/nats-io/nats-server/blob/v2.15.0/server/util.go#L267-L275"
      }
    },
    "go": {
      "name": "Go socket source",
      "basis": "go1.26.8",
      "sources": {
        "s172a98468ce6": "https://github.com/golang/go/blob/go1.26.8/src/net/ipsock_posix.go#L134-L147"
      }
    },
    "cli": {
      "name": "natscli",
      "basis": "v0.4.0",
      "sources": {
        "s068dbbd154ce": "https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/nats/main.go",
        "sd263b3e2aeb4": "https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/util.go",
        "sc6b88ab2d1f8": "https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/sub_command.go"
      }
    },
    "server-docs": {
      "name": "NATS Server documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "se640dd73f45d": "https://docs.nats.io/learn/security/authentication-basics",
        "s7a81108db86e": "https://docs.nats.io/learn/security/authorization",
        "s468e604fd22d": "https://docs.nats.io/learn/security/operator-mode",
        "s5f9b8e5012ec": "https://docs.nats.io/learn/security/decentralized-auth",
        "s8cba9edd33b5": "https://docs.nats.io/learn/security/accounts-and-multitenancy",
        "sb07c45120b77": "https://docs.nats.io/learn/security/cross-account",
        "see8fdd7cdcf7": "https://docs.nats.io/reference/config/authorization/users/permissions/subscribe/",
        "s3eced14a9c7a": "https://docs.nats.io/reference/config/authorization/users/permissions/allow_responses/",
        "sce86f77690da": "https://docs.nats.io/reference/config/authorization/users/allowed_connection_types",
        "se5f31c6269c9": "https://docs.nats.io/reference/config/authorization/timeout",
        "s54ebf5db9564": "https://docs.nats.io/learn/security/encryption",
        "se9d8f0116aa0": "https://docs.nats.io/reference/config/tls/",
        "s524e33e8c24d": "https://docs.nats.io/learn/monitoring/monitoring-endpoints",
        "scd743849d62e": "https://docs.nats.io/concepts/jetstream",
        "s4532e40c78ec": "https://docs.nats.io/reference/config",
        "s077fb5dcad29": "https://docs.nats.io/reference/config/accounts/limits/",
        "s2aa6be0b95f3": "https://docs.nats.io/reference/config/jetstream/",
        "sac96fc2fd82c": "https://docs.nats.io/reference/config/accounts/jetstream/",
        "sb0a95cb44e8c": "https://docs.nats.io/reference/config/jetstream/request_queue_limit",
        "sccd84f1a4406": "https://docs.nats.io/reference/config/jetstream/domain",
        "s5c67c71c763a": "https://docs.nats.io/reference/config/jetstream/encryption_key",
        "s21378b23fccd": "https://docs.nats.io/reference/config/jetstream/cipher",
        "sebfa61302021": "https://docs.nats.io/reference/config/jetstream/prev_encryption_key",
        "s2e1ad079a3bf": "https://docs.nats.io/reference/config/cluster/",
        "s9371709dd080": "https://docs.nats.io/reference/config/gateway/",
        "se29432096847": "https://docs.nats.io/reference/config/leafnodes/",
        "s812e43517c7c": "https://docs.nats.io/reference/config/leafnodes/authorization/",
        "s65f0d3357c65": "https://docs.nats.io/reference/config/leafnodes/remotes/",
        "s739889828b7d": "https://docs.nats.io/learn/topologies/leaf-nodes",
        "s7255e9ec521c": "https://docs.nats.io/reference/config/mqtt/",
        "sb21fa571a215": "https://docs.nats.io/learn/mqtt/auth-and-clustering",
        "s32c27329e016": "https://docs.nats.io/reference/config/websocket/",
        "s6ce4e35cae81": "https://docs.nats.io/learn/security/auth-callout",
        "sc7f484b67ca6": "https://docs.nats.io/reference/config/authorization/auth_callout",
        "sf02d263ec6e8": "https://docs.nats.io/learn/deployment/hardening"
      }
    }
  },
  "claims": {
    "baseline": {"text": "v2.14.7 and its recorded commit are the review baseline, not a latest-release claim.", "components": ["server", "commit"], "sources": ["server:s67d42c6498ac", "commit:sa981814d2443"], "status": "REASONED"},
    "client-default": {"text": "Client port 4222 defaults to no authentication and wildcard host; select loopback or a private interface.", "components": ["server-docs"], "sources": ["server-docs:se640dd73f45d", "server-docs:s4532e40c78ec"], "status": "REASONED"},
    "image-config": {"text": "Published 2.14/2.15 variants load bundled configuration only with the recorded default command, working directory and mounts.", "components": ["library", "image"], "sources": ["library:s5820f80dc5e2", "image:s63fd80eda93f", "image:sf75fdfff87fb", "image:sb6bb995a1296", "image:sb2004ba92e96", "image:s63901565fdae", "image:s052d6780e740", "image:s942be49c75fa", "image:s4152555c0fa5", "image:sac24f019f564", "image:s60e57b8083a9", "image:s38262af3382e", "image:sa8e0a5d725c4", "image:s56fa48bb22a4", "image:s221e831d1482", "image:sf46270db6983", "image:s242baf7508a4", "image:s1be190b618be", "image:s0d4076849de7"], "status": "REASONED"},
    "image-client": {"text": "Bundled images enable unauthenticated client 4222; mount and explicitly select protected configuration.", "components": ["image"], "sources": ["image:s63fd80eda93f", "image:s63901565fdae"], "status": "REASONED"},
    "image-monitor": {"text": "Bundled images enable unauthenticated monitoring 8222; remove or bind privately.", "components": ["image"], "sources": ["image:s63fd80eda93f", "image:s63901565fdae"], "status": "REASONED"},
    "image-route": {"text": "Bundled route 6222 uses published ruser/T0pS3cr3t and my_cluster; remove or replace with private credentials.", "components": ["image"], "sources": ["image:s63fd80eda93f", "image:s63901565fdae"], "status": "REASONED"},
    "image-bind": {"text": "Bundled listeners without hosts use 0.0.0.0, dual-stack where IPv4-mapped IPv6 is supported; restrict publication.", "components": ["image-server", "go"], "sources": ["image-server:se8793d3c33b3", "image-server:s9860c7a8a315", "image-server:s4f35f43b860b", "image-server:s6d1b9c207c22", "image-server:s63fb63ed420f", "image-server:s483a2d169cbf", "go:s172a98468ce6"], "status": "REASONED"},
    "static-auth": {"text": "Separate password/NKey users may coexist; a user's NKey replaces its password pair, without requiring JWT mode.", "components": ["server-docs"], "sources": ["server-docs:se640dd73f45d"], "status": "REASONED"},
    "passwords": {"text": "Generate bcrypt interactively; protect seeds and password inputs; hashes do not replace TLS.", "components": ["cli", "server-docs"], "sources": ["server-docs:se640dd73f45d", "cli:s068dbbd154ce"], "status": "REASONED"},
    "anonymous": {"text": "no_auth_user admits anonymous clients as a named identity; omit unless deliberate.", "components": ["server", "server-docs"], "sources": ["server-docs:se640dd73f45d", "server:sfcf4d67bc409"], "status": "REASONED"},
    "operator": {"text": "Operator signs account JWTs, accounts sign users; preload resolver accounts and protect signing seeds off the broker.", "components": ["server-docs"], "sources": ["server-docs:s468e604fd22d", "server-docs:s5f9b8e5012ec"], "status": "REASONED"},
    "jwt-proof": {"text": "Non-bearer users prove seed possession by nonce signature; bearer JWT possession is sufficient.", "components": ["server-docs"], "sources": ["server-docs:s5f9b8e5012ec"], "status": "REASONED"},
    "permissions-default": {"text": "Absent user/default permissions means unrestricted account access; explicit permissions replace defaults.", "components": ["server", "server-docs"], "sources": ["server-docs:s7a81108db86e", "server:sfcf4d67bc409"], "status": "REASONED"},
    "allow-lists": {"text": "Publish/subscribe lists are independent; nonempty allows restrict, empty allows do not; matching static deny wins.", "components": ["server", "server-docs"], "sources": ["server-docs:s7a81108db86e", "server:s77d2cf7237a9"], "status": "REASONED"},
    "inboxes": {"text": "Use identity-specific reply inboxes; broad _INBOX.> exposes other clients' replies.", "components": ["server-docs"], "sources": ["server-docs:s7a81108db86e"], "status": "REASONED"},
    "queues": {"text": "Require the assigned queue in subscription permissions; a bare subject grant defeats queue-only restriction.", "components": ["server-docs"], "sources": ["server-docs:see8fdd7cdcf7"], "status": "REASONED"},
    "responses": {"text": "allow_responses can override static publish denial for tracked replies; bound count/expiry, not an absolute subject allow-list.", "components": ["server", "server-docs"], "sources": ["server-docs:s3eced14a9c7a", "server:s77d2cf7237a9"], "status": "REASONED"},
    "tls": {"text": "Client TLS validates endpoint identity; verify requires client certificates but password requirements come from authentication.", "components": ["server", "server-docs"], "sources": ["server-docs:s54ebf5db9564", "server-docs:se9d8f0116aa0", "server:sfcf4d67bc409"], "status": "REASONED"},
    "tls-map": {"text": "verify_and_map derives configured identity from certificate attributes and enables verification itself.", "components": ["server", "server-docs"], "sources": ["server-docs:se9d8f0116aa0", "server:sfcf4d67bc409"], "status": "REASONED"},
    "monitor-default": {"text": "Native monitoring is off unless enabled, conventionally 8222; HTTPS adds transport security, not NATS login or client mTLS.", "components": ["server", "server-docs"], "sources": ["server-docs:s524e33e8c24d", "server:sdef33959305a"], "status": "REASONED"},
    "monitor-data": {"text": "/varz, /connz, /routez and JetStream /jsz disclose metadata; subs/auth query options add details, not authentication.", "components": ["server", "server-docs"], "sources": ["server-docs:s524e33e8c24d", "server:sdef33959305a"], "status": "REASONED"},
    "monitor-boundary": {"text": "Bind monitoring privately; an authenticating proxy needs direct-backend bypass prevention.", "components": ["server-docs"], "sources": ["server-docs:s524e33e8c24d", "server-docs:sf02d263ec6e8"], "status": "REASONED"},
    "jetstream-port": {"text": "JetStream shares the server and monitoring endpoint; it adds no listener of its own.", "components": ["server-docs"], "sources": ["server-docs:scd743849d62e"], "status": "REASONED"},
    "cluster": {"text": "Conditional private 6222 routes have separate credentials/TLS; explicit URLs need credentials; cluster TLS verifies peers.", "components": ["server-docs"], "sources": ["server-docs:s2e1ad079a3bf"], "status": "REASONED"},
    "gateway": {"text": "Conditional private 7222 gateways verify peers; reject_unknown_cluster supplements credentials, not replaces them.", "components": ["server-docs"], "sources": ["server-docs:s9371709dd080"], "status": "REASONED"},
    "peer-urls": {"text": "Match SANs, advertisements and URLs; keep insecure disabled; known-URL certificate checks constrain dynamic growth.", "components": ["server-docs"], "sources": ["server-docs:s2e1ad079a3bf", "server-docs:s9371709dd080"], "status": "REASONED"},
    "leaf": {"text": "Conditional 7422 leaf auth/TLS is independent; static password and operator credentials recipes are alternatives.", "components": ["server-docs"], "sources": ["server-docs:se29432096847", "server-docs:s812e43517c7c", "server-docs:s65f0d3357c65"], "status": "REASONED"},
    "leaf-accounts": {"text": "Outbound account is local; remote credentials select hub account; remotes-only creates no inbound listener.", "components": ["server-docs"], "sources": ["server-docs:s65f0d3357c65"], "status": "REASONED"},
    "connection-default": {"text": "Documented client-connection default is 65,536; configured limits are capacities, not attempt-rate limits.", "components": ["server-docs"], "sources": ["server-docs:s4532e40c78ec"], "status": "REASONED"},
    "payload-default": {"text": "Documented payload default is 1 MiB; max_payload must not exceed max_pending.", "components": ["server-docs"], "sources": ["server-docs:s4532e40c78ec"], "status": "REASONED"},
    "runtime-budgets": {"text": "Set per-server/account connections, per-client subscriptions, control-line/pending limits and TLS/auth/write deadlines for workload.", "components": ["server-docs"], "sources": ["server-docs:se5f31c6269c9", "server-docs:s4532e40c78ec", "server-docs:s077fb5dcad29"], "status": "REASONED"},
    "accounts": {"text": "Top-level users share $G; separate account spaces and restrict exports to intended importing accounts.", "components": ["server-docs"], "sources": ["server-docs:s8cba9edd33b5", "server-docs:sb07c45120b77"], "status": "REASONED"},
    "system-account": {"text": "Default system name is $SYS; selected SYS contains administrative identities, not application users.", "components": ["server", "server-docs"], "sources": ["server-docs:s8cba9edd33b5", "server:sfcf4d67bc409"], "status": "REASONED"},
    "jetstream-server": {"text": "Conditional store_dir and memory/file budgets bound storage, not all process memory or filesystem use.", "components": ["server-docs"], "sources": ["server-docs:s2aa6be0b95f3"], "status": "REASONED"},
    "jetstream-queue": {"text": "request_queue_limit bounds pending JetStream API work, not connection attempts.", "components": ["server-docs"], "sources": ["server-docs:sb0a95cb44e8c"], "status": "REASONED"},
    "jetstream-account": {"text": "Set account memory/file, stream count, required max_bytes, per-stream byte and acknowledgement ceilings; inspect effective reload results.", "components": ["server-docs"], "sources": ["server-docs:sac96fc2fd82c"], "status": "REASONED"},
    "consumer-limit": {"text": "v2.14.7 account max_consumers is enforced per stream, not as a total account consumer count.", "components": ["server", "server-docs"], "sources": ["server-docs:sac96fc2fd82c", "server:sbf04a3dffd21"], "status": "REASONED"},
    "jetstream-auth": {"text": "Core-only users deny API subjects; legitimate JetStream apps need reviewed resource, reply and acknowledgement permissions.", "components": ["server", "server-docs"], "sources": ["server-docs:s7a81108db86e", "server:s0015a19a5fb9"], "status": "REASONED"},
    "domains": {"text": "EDGE/HUB domains select independent JetStream systems, not tenant authorization boundaries.", "components": ["server-docs"], "sources": ["server-docs:sccd84f1a4406", "server-docs:s739889828b7d"], "status": "REASONED"},
    "encryption": {"text": "Conditional server-wide file-store encryption uses protected key material, recommended at least 32 bytes; aes selects AES-GCM.", "components": ["server-docs"], "sources": ["server-docs:s54ebf5db9564", "server-docs:s5c67c71c763a", "server-docs:s21378b23fccd"], "status": "REASONED"},
    "rotation": {"text": "Previous-key transition needs restart and recovery tests; protect keys and backups separately.", "components": ["server-docs"], "sources": ["server-docs:s54ebf5db9564", "server-docs:sebfa61302021"], "status": "REASONED"},
    "mqtt": {"text": "Optional private MQTT TLS needs JetStream, scoped translated subjects, protocol-restricted users and reviewed anonymous overrides.", "components": ["server-docs"], "sources": ["server-docs:sce86f77690da", "server-docs:s7255e9ec521c", "server-docs:sb21fa571a215"], "status": "REASONED"},
    "mqtt-jwt": {"text": "Operator-mode MQTT uses explicitly permitted bearer JWT passwords, not normal NKey nonce proof.", "components": ["server-docs"], "sources": ["server-docs:sb21fa571a215"], "status": "REASONED"},
    "websocket": {"text": "Optional 8443 WSS needs scoped users/inboxes and origin policy; non-browser Origin is not authentication.", "components": ["server-docs"], "sources": ["server-docs:sce86f77690da", "server-docs:s32c27329e016"], "status": "REASONED"},
    "websocket-tls": {"text": "WebSocket TLS is required unless no_tls disables it; protect proxy backends and review listener auth overrides.", "components": ["server-docs"], "sources": ["server-docs:s32c27329e016"], "status": "REASONED"},
    "callout": {"text": "Conditional auth callout needs dedicated AUTH account, narrow bypass users, signed responses and encrypted XKey exchanges.", "components": ["server", "server-docs"], "sources": ["server-docs:s6ce4e35cae81", "server-docs:sc7f484b67ca6", "server:sfe9cfda67037"], "status": "REASONED"},
    "callout-mode": {"text": "Static and operator workflows differ; allowed_accounts is mode-dependent; unavailable authenticator must reject admission.", "components": ["server", "server-docs"], "sources": ["server-docs:s6ce4e35cae81", "server:sfcf4d67bc409"], "status": "REASONED"},
    "files": {"text": "Dedicated non-root broker reads necessary secrets and writes state; application/signing seeds stay with their owners.", "components": ["server-docs"], "sources": ["server-docs:s468e604fd22d", "server-docs:sf02d263ec6e8"], "status": "REASONED"},
    "verify-offline": {"text": "Native parsing/key generation remain unobserved; pair valid parsing fixtures with malformed controls and separately scan placeholders.", "components": ["server", "cli"], "sources": ["server:sfcf4d67bc409", "cli:s068dbbd154ce"], "status": "REASONED"},
    "verify-identity": {"text": "Inspect running identity, effective config/limits, every listener namespace and host publication; file inspection alone is insufficient.", "components": ["server-docs"], "sources": ["server-docs:s4532e40c78ec", "server-docs:sf02d263ec6e8"], "status": "REASONED"},
    "cli-input": {"text": "Clear inherited NATS_* and saved contexts; password uses guarded one-command environment input, still locally readable.", "components": ["cli"], "sources": ["cli:s068dbbd154ce", "cli:sd263b3e2aeb4"], "status": "REASONED", "verify": [1, 2, 3, 4]},
    "verify-auth": {"text": "Require allowed publish, missing/wrong-password rejection, certificate/hostname discrimination and forbidden subject errors.", "components": ["server", "cli", "server-docs"], "sources": ["server-docs:se640dd73f45d", "server-docs:se9d8f0116aa0", "server:s77d2cf7237a9", "cli:sd263b3e2aeb4"], "status": "REASONED", "verify": [1]},
    "verify-delivery": {"text": "Require exact live markers; quiet subscribers and publish success alone prove no delivery.", "components": ["cli", "server-docs"], "sources": ["server-docs:s7a81108db86e", "cli:sc6b88ab2d1f8"], "status": "REASONED", "verify": [2, 3]},
    "verify-queue": {"text": "Assigned queue receives marker; wrong/no queue rejects with matched positive delivery.", "components": ["server", "cli", "server-docs"], "sources": ["server-docs:see8fdd7cdcf7", "server:s77d2cf7237a9", "cli:sc6b88ab2d1f8"], "status": "REASONED", "verify": [2, 3]},
    "verify-response": {"text": "Same worker connection sends one timely reply; extra, expired and unrelated replies must fail.", "components": ["server", "cli", "server-docs"], "sources": ["server-docs:s3eced14a9c7a", "server:s77d2cf7237a9", "cli:sd263b3e2aeb4"], "status": "REASONED", "verify": [4]},
    "verify-accounts": {"text": "Created marker stays in ORDERS; shipped marker reaches ANALYTICS; keep count controls live and reject third-account imports.", "components": ["cli", "server-docs"], "sources": ["server-docs:s8cba9edd33b5", "server-docs:sb07c45120b77", "cli:sc6b88ab2d1f8"], "status": "REASONED", "verify": [2, 3]},
    "verify-system": {"text": "sys-admin gets system response; tenant gets corresponding publish-permission rejection.", "components": ["cli", "server-docs"], "sources": ["server-docs:s8cba9edd33b5", "cli:sd263b3e2aeb4"], "status": "REASONED", "verify": [4]},
    "verify-js-auth": {"text": "Provisioner creates, inspects, retrieves and deletes fixtures; Core-only identity must receive API-subject denials.", "components": ["server", "cli", "server-docs"], "sources": ["server-docs:sac96fc2fd82c", "server:s0015a19a5fb9", "cli:sd263b3e2aeb4"], "status": "REASONED", "verify": [4]},
    "verify-js-limits": {"text": "Test byte reservations, stored bytes, stream/consumer counts and ack ceiling independently with below-limit controls.", "components": ["server", "server-docs"], "sources": ["server-docs:s2aa6be0b95f3", "server-docs:sac96fc2fd82c", "server:sbf04a3dffd21", "server:s0015a19a5fb9"], "status": "REASONED", "verify": [4]},
    "verify-recovery": {"text": "Copied encrypted store must recover with correct key and fail with missing/wrong key; test rotation, not just marker absence.", "components": ["server", "server-docs"], "sources": ["server-docs:s54ebf5db9564", "server-docs:sebfa61302021", "server:s0015a19a5fb9"], "status": "REASONED", "verify": [4]},
    "verify-peers": {"text": "Actual links need cross-server delivery plus credential/certificate/network denials; client-port/TCP/TLS checks do not substitute.", "components": ["server-docs"], "sources": ["server-docs:s2e1ad079a3bf", "server-docs:s9371709dd080", "server-docs:se29432096847"], "status": "REASONED"},
    "verify-monitor": {"text": "Collector retrieves expected JSON; unauthorized direct backend cannot answer; pair refusal with identity/inventory and live control.", "components": ["server-docs"], "sources": ["server-docs:s524e33e8c24d", "server-docs:sf02d263ec6e8"], "status": "REASONED", "verify": [5]},
    "verify-proxy": {"text": "Conditional proxy needs anonymous refusal, authenticated JSON success and direct-backend bypass denial.", "components": ["server-docs"], "sources": ["server-docs:s524e33e8c24d", "server-docs:sf02d263ec6e8"], "status": "REASONED", "verify": [5]},
    "verify-optional": {"text": "Test MQTT translated subjects/bearer identity, WSS origins versus auth, and callout outage, grants and XKey failures separately.", "components": ["server-docs"], "sources": ["server-docs:sce86f77690da", "server-docs:s7255e9ec521c", "server-docs:sb21fa571a215", "server-docs:s32c27329e016", "server-docs:s6ce4e35cae81"], "status": "REASONED"},
    "verify-pressure": {"text": "Bounded workloads distinguish connection/subscription/payload/control-line/timeouts/slow-consumer/API limits with healthy controls.", "components": ["server-docs"], "sources": ["server-docs:se5f31c6269c9", "server-docs:s4532e40c78ec", "server-docs:s077fb5dcad29", "server-docs:sb0a95cb44e8c"], "status": "REASONED"}
  }
}
---
# NATS and JetStream: authentication, TLS, and the monitoring port

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| baseline: v2.14.7 and its recorded commit are the review baseline, not a latest-release claim. | NATS Server v2.14.7; NATS baseline commit 8d8b69a8c46a46a150eabb7f312607c4d9c58faf | REASONED |
| client-default: Client port 4222 defaults to no authentication and wildcard host; select loopback or a private interface. | NATS Server documentation (rolling) unknown | REASONED |
| image-config: Published 2.14/2.15 variants load bundled configuration only with the recorded default command, working directory and mounts. | NATS image catalogue dcd3db677d8919c3a42d369bd48a6f1c234b3ae8; NATS image source 0e72748d3cb553ccdb8c2da7c75ec3b767be51a5 | REASONED |
| image-client: Bundled images enable unauthenticated client 4222; mount and explicitly select protected configuration. | NATS image source 0e72748d3cb553ccdb8c2da7c75ec3b767be51a5 | REASONED |
| image-monitor: Bundled images enable unauthenticated monitoring 8222; remove or bind privately. | NATS image source 0e72748d3cb553ccdb8c2da7c75ec3b767be51a5 | REASONED |
| image-route: Bundled route 6222 uses published ruser/T0pS3cr3t and my_cluster; remove or replace with private credentials. | NATS image source 0e72748d3cb553ccdb8c2da7c75ec3b767be51a5 | REASONED |
| image-bind: Bundled listeners without hosts use 0.0.0.0, dual-stack where IPv4-mapped IPv6 is supported; restrict publication. | NATS image listener source v2.15.0; Go socket source go1.26.8 | REASONED |
| static-auth: Separate password/NKey users may coexist; a user's NKey replaces its password pair, without requiring JWT mode. | NATS Server documentation (rolling) unknown | REASONED |
| passwords: Generate bcrypt interactively; protect seeds and password inputs; hashes do not replace TLS. | natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| anonymous: no_auth_user admits anonymous clients as a named identity; omit unless deliberate. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| operator: Operator signs account JWTs, accounts sign users; preload resolver accounts and protect signing seeds off the broker. | NATS Server documentation (rolling) unknown | REASONED |
| jwt-proof: Non-bearer users prove seed possession by nonce signature; bearer JWT possession is sufficient. | NATS Server documentation (rolling) unknown | REASONED |
| permissions-default: Absent user/default permissions means unrestricted account access; explicit permissions replace defaults. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| allow-lists: Publish/subscribe lists are independent; nonempty allows restrict, empty allows do not; matching static deny wins. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| inboxes: Use identity-specific reply inboxes; broad _INBOX.&gt; exposes other clients' replies. | NATS Server documentation (rolling) unknown | REASONED |
| queues: Require the assigned queue in subscription permissions; a bare subject grant defeats queue-only restriction. | NATS Server documentation (rolling) unknown | REASONED |
| responses: allow_responses can override static publish denial for tracked replies; bound count/expiry, not an absolute subject allow-list. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| tls: Client TLS validates endpoint identity; verify requires client certificates but password requirements come from authentication. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| tls-map: verify_and_map derives configured identity from certificate attributes and enables verification itself. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| monitor-default: Native monitoring is off unless enabled, conventionally 8222; HTTPS adds transport security, not NATS login or client mTLS. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| monitor-data: /varz, /connz, /routez and JetStream /jsz disclose metadata; subs/auth query options add details, not authentication. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| monitor-boundary: Bind monitoring privately; an authenticating proxy needs direct-backend bypass prevention. | NATS Server documentation (rolling) unknown | REASONED |
| jetstream-port: JetStream shares the server and monitoring endpoint; it adds no listener of its own. | NATS Server documentation (rolling) unknown | REASONED |
| cluster: Conditional private 6222 routes have separate credentials/TLS; explicit URLs need credentials; cluster TLS verifies peers. | NATS Server documentation (rolling) unknown | REASONED |
| gateway: Conditional private 7222 gateways verify peers; reject_unknown_cluster supplements credentials, not replaces them. | NATS Server documentation (rolling) unknown | REASONED |
| peer-urls: Match SANs, advertisements and URLs; keep insecure disabled; known-URL certificate checks constrain dynamic growth. | NATS Server documentation (rolling) unknown | REASONED |
| leaf: Conditional 7422 leaf auth/TLS is independent; static password and operator credentials recipes are alternatives. | NATS Server documentation (rolling) unknown | REASONED |
| leaf-accounts: Outbound account is local; remote credentials select hub account; remotes-only creates no inbound listener. | NATS Server documentation (rolling) unknown | REASONED |
| connection-default: Documented client-connection default is 65,536; configured limits are capacities, not attempt-rate limits. | NATS Server documentation (rolling) unknown | REASONED |
| payload-default: Documented payload default is 1 MiB; max_payload must not exceed max_pending. | NATS Server documentation (rolling) unknown | REASONED |
| runtime-budgets: Set per-server/account connections, per-client subscriptions, control-line/pending limits and TLS/auth/write deadlines for workload. | NATS Server documentation (rolling) unknown | REASONED |
| accounts: Top-level users share $G; separate account spaces and restrict exports to intended importing accounts. | NATS Server documentation (rolling) unknown | REASONED |
| system-account: Default system name is $SYS; selected SYS contains administrative identities, not application users. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| jetstream-server: Conditional store_dir and memory/file budgets bound storage, not all process memory or filesystem use. | NATS Server documentation (rolling) unknown | REASONED |
| jetstream-queue: request_queue_limit bounds pending JetStream API work, not connection attempts. | NATS Server documentation (rolling) unknown | REASONED |
| jetstream-account: Set account memory/file, stream count, required max_bytes, per-stream byte and acknowledgement ceilings; inspect effective reload results. | NATS Server documentation (rolling) unknown | REASONED |
| consumer-limit: v2.14.7 account max_consumers is enforced per stream, not as a total account consumer count. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| jetstream-auth: Core-only users deny API subjects; legitimate JetStream apps need reviewed resource, reply and acknowledgement permissions. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| domains: EDGE/HUB domains select independent JetStream systems, not tenant authorization boundaries. | NATS Server documentation (rolling) unknown | REASONED |
| encryption: Conditional server-wide file-store encryption uses protected key material, recommended at least 32 bytes; aes selects AES-GCM. | NATS Server documentation (rolling) unknown | REASONED |
| rotation: Previous-key transition needs restart and recovery tests; protect keys and backups separately. | NATS Server documentation (rolling) unknown | REASONED |
| mqtt: Optional private MQTT TLS needs JetStream, scoped translated subjects, protocol-restricted users and reviewed anonymous overrides. | NATS Server documentation (rolling) unknown | REASONED |
| mqtt-jwt: Operator-mode MQTT uses explicitly permitted bearer JWT passwords, not normal NKey nonce proof. | NATS Server documentation (rolling) unknown | REASONED |
| websocket: Optional 8443 WSS needs scoped users/inboxes and origin policy; non-browser Origin is not authentication. | NATS Server documentation (rolling) unknown | REASONED |
| websocket-tls: WebSocket TLS is required unless no_tls disables it; protect proxy backends and review listener auth overrides. | NATS Server documentation (rolling) unknown | REASONED |
| callout: Conditional auth callout needs dedicated AUTH account, narrow bypass users, signed responses and encrypted XKey exchanges. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| callout-mode: Static and operator workflows differ; allowed_accounts is mode-dependent; unavailable authenticator must reject admission. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| files: Dedicated non-root broker reads necessary secrets and writes state; application/signing seeds stay with their owners. | NATS Server documentation (rolling) unknown | REASONED |
| verify-offline: Native parsing/key generation remain unobserved; pair valid parsing fixtures with malformed controls and separately scan placeholders. | NATS Server v2.14.7; natscli v0.4.0 | REASONED |
| verify-identity: Inspect running identity, effective config/limits, every listener namespace and host publication; file inspection alone is insufficient. | NATS Server documentation (rolling) unknown | REASONED |
| cli-input: Clear inherited NATS_* and saved contexts; password uses guarded one-command environment input, still locally readable. | natscli v0.4.0 | REASONED |
| verify-auth: Require allowed publish, missing/wrong-password rejection, certificate/hostname discrimination and forbidden subject errors. | NATS Server v2.14.7; natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-delivery: Require exact live markers; quiet subscribers and publish success alone prove no delivery. | natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-queue: Assigned queue receives marker; wrong/no queue rejects with matched positive delivery. | NATS Server v2.14.7; natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-response: Same worker connection sends one timely reply; extra, expired and unrelated replies must fail. | NATS Server v2.14.7; natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-accounts: Created marker stays in ORDERS; shipped marker reaches ANALYTICS; keep count controls live and reject third-account imports. | natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-system: sys-admin gets system response; tenant gets corresponding publish-permission rejection. | natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-js-auth: Provisioner creates, inspects, retrieves and deletes fixtures; Core-only identity must receive API-subject denials. | NATS Server v2.14.7; natscli v0.4.0; NATS Server documentation (rolling) unknown | REASONED |
| verify-js-limits: Test byte reservations, stored bytes, stream/consumer counts and ack ceiling independently with below-limit controls. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| verify-recovery: Copied encrypted store must recover with correct key and fail with missing/wrong key; test rotation, not just marker absence. | NATS Server v2.14.7; NATS Server documentation (rolling) unknown | REASONED |
| verify-peers: Actual links need cross-server delivery plus credential/certificate/network denials; client-port/TCP/TLS checks do not substitute. | NATS Server documentation (rolling) unknown | REASONED |
| verify-monitor: Collector retrieves expected JSON; unauthorized direct backend cannot answer; pair refusal with identity/inventory and live control. | NATS Server documentation (rolling) unknown | REASONED |
| verify-proxy: Conditional proxy needs anonymous refusal, authenticated JSON success and direct-backend bypass denial. | NATS Server documentation (rolling) unknown | REASONED |
| verify-optional: Test MQTT translated subjects/bearer identity, WSS origins versus auth, and callout outage, grants and XKey failures separately. | NATS Server documentation (rolling) unknown | REASONED |
| verify-pressure: Bounded workloads distinguish connection/subscription/payload/control-line/timeouts/slow-consumer/API limits with healthy controls. | NATS Server documentation (rolling) unknown | REASONED |
<!-- version-basis:end -->

NATS accepts client connections on 4222 with no authentication configured by default. A separately enabled HTTP monitoring endpoint, conventionally 8222, reveals connection metadata, subscription subjects, and message/byte counters without a login of its own. Both need explicit configuration. JetStream, the persistence layer for streams and consumers, runs in the same server process: it adds no listening port of its own, and its state surfaces through the same monitoring endpoint at `/jsz`.

The official Docker images open more than these defaults. Every published `nats` tag (2.14 and 2.15; scratch, Alpine, Nano Server and Windows Server Core at the pinned commit), run with its default command, its default working directory (scratch and Windows name the file by a relative path, so it loads only when the working directory is where the image copies it: `/` on scratch, `C:\` on Windows) and no configuration mounted over the bundled one (`/nats-server.conf` on scratch, `/etc/nats/nats-server.conf` on Alpine, `C:\nats-server.conf` on Windows), loads a bundled `nats-server.conf` that sets `port: 4222` with no client authorization, `monitor_port: 8222`, and a `cluster` block on port 6222 whose route authorization is user `ruser` with password `T0pS3cr3t`, which the image source publishes along with the cluster name `my_cluster`. None of the three sets a host, so each listens on `0.0.0.0`, which the Go runtime opens as a dual-stack socket where the host supports IPv4-mapped IPv6 addresses. Anything that can reach the container on those ports (another container on its network, a published port, or host networking) therefore gets unauthenticated client access, unauthenticated monitoring, and route connections authorized by public credentials. Passing arguments replaces the default command, so the bundled configuration is not loaded unless the arguments name it again with `--config` or `-c`. Mount your own configuration and pass it with `--config`: set client authentication, bind monitoring to `127.0.0.1` or remove it, and drop the `cluster` block unless its route credentials are private. Publish only 4222, and only to host loopback or a private network.

The review baseline is **NATS Server v2.14.7**, tag commit `8d8b69a8c46a46a150eabb7f312607c4d9c58faf`, and **natscli v0.4.0**. This is a pinned review baseline, not a claim that these are the latest releases. Stable documentation can describe newer versions; version-sensitive conclusions below also use the pinned implementation.

The fragments explain individual controls and conditional alternatives. Section 14 assembles one selected static-account configuration for the Verify identities. Replace every placeholder before deployment. All example capacities and time budgets are workload-dependent.

## 1. Require authentication and separate credential ownership

Tier-1 rationale: separate identities and signing authority limit the consequences of a leaked application credential.

Static authentication supports a shared token, password users, and public NKey identities. Prefer individually scoped identities over a shared token. Separate password and NKey users may coexist in a `users` list; an individual NKey entry replaces that identity's `user`/`password` pair. Static NKey authentication does not require JWT infrastructure.

For example, these are alternative application entries to place inside the intended account's `users` list:

```text
{
  user: app
  password: "REPLACE_WITH_LONG_RANDOM_PASSWORD"
  permissions {
    publish: { allow: ["orders.created"] }
    subscribe: { deny: [">"] }
  }
}

{
  nkey: "REPLACE_WITH_GENERATED_PUBLIC_USER_NKEY"
  permissions {
    publish: { allow: ["orders.created"] }
    subscribe: { deny: [">"] }
  }
}
```

Generate your own public user NKey and substitute it. An illustrative public key is not a credential-generation procedure. The vendor documents `nats auth nkey gen user --output user.nk` and `nats auth nkey show user.nk`; generation and inspection are offline operations, but require the pinned CLI and a private writable directory. The seed file belongs to the client, while the server stores the public key.

For password users, store a bcrypt hash instead of a plaintext password where possible. `nats server passwd` prompts interactively; do not pass a password through its command-line arguments. Substitute the resulting hash in the server's `password` field, and give the original password to the client through its protected secret configuration. Bcrypt protects stored passwords, not their transmission, so retain TLS.

Do not set `no_auth_user`, which admits unauthenticated connections as a named user, unless an anonymous path is deliberate. It is easy to leave this setting behind after testing.

**Conditional: operator-mode JWT authentication.** Use this separate configuration approach when delegated account administration is needed. Replace static account/user declarations with generated JWT configuration, retaining the listener, TLS, monitoring, and resource controls:

```text
operator: "/etc/nats/operator.jwt"
system_account: "REPLACE_WITH_GENERATED_SYSTEM_ACCOUNT_PUBLIC_KEY"

resolver {
  type: full
  dir: "/var/lib/nats/resolver"
}

resolver_preload {
  REPLACE_WITH_GENERATED_SYSTEM_ACCOUNT_PUBLIC_KEY: "REPLACE_WITH_SIGNED_SYSTEM_ACCOUNT_JWT"
}
```

The two system-account public-key placeholders must identify the same generated account, whose signed JWT is preloaded. The resolver also needs the appropriate application account JWTs before their users can authenticate.

The trust hierarchy has two signing levels: the operator, or an operator signing key, signs account JWTs; each account, or its signing keys, signs user JWTs. Accounts and users are not both signed by the operator. Ordinary non-bearer users prove possession of their seed by signing the server's nonce. Bearer JWTs are an explicit exception: possession of the JWT is sufficient.

Clients can use a protected credentials file through `--creds /protected/app.creds`. The file contains a user seed and remains secret. The Verify probes use environment bindings so credential values and credentials-file paths need not appear in command arguments. Keep operator/account signing seeds on the provisioning system, not the broker. JWT authentication does not inherently restrict subjects: encode and review user permissions separately.

Exposed versus fixed: one shared secret identifies every application; individually scoped credentials and, where needed, delegated signing authority separate their access and revocation.

See [authentication basics](https://docs.nats.io/learn/security/authentication-basics), [operator mode](https://docs.nats.io/learn/security/operator-mode), and [decentralized authentication](https://docs.nats.io/learn/security/decentralized-auth).

## 2. Scope subjects, queue groups, and replies

Tier-1 rationale: compromised application credentials should reach only their assigned messages and necessary replies.

A user with no `permissions` block and no applicable `default_permissions` is unrestricted within its account. Explicit user permissions replace defaults rather than merging with them. A top-level user list can use `authorization.default_permissions`; account-local defaults belong to the corresponding account.

The selected `order-svc` identity publishes order subjects and subscribes only to its own reply inbox:

```text
{
  user: order-svc
  password: "REPLACE_WITH_ORDER_SVC_BCRYPT_HASH"
  permissions {
    publish: {
      allow: ["orders.>"]
      deny: ["$SYS.>", "$JS.API.>", "$JS.*.API.>"]
    }
    # Set the client's inbox prefix to _INBOX.order-svc.
    # Do not grant _INBOX.>, which includes other clients' replies.
    subscribe: { allow: ["_INBOX.order-svc.>"] }
  }
}
```

The publisher-only `app` example in section 1 remains separate: it cannot subscribe, including to replies. Do not give it request/reply work without reviewing its inbox permissions.

`publish.allow` and `subscribe.allow` are independent. Restrict both operations explicitly. For ordinary static permissions, a **nonempty** allow list denies subjects outside that list; an empty allow list imposes no restriction. Use an explicit deny, such as `subscribe: { deny: [">"] }`, to prohibit an operation.

For a request-handling worker, require the assigned queue group and bound reply permissions:

```text
{
  user: order-worker
  password: "REPLACE_WITH_ORDER_WORKER_BCRYPT_HASH"
  permissions {
    publish: { deny: [">"] }
    subscribe: { allow: ["orders.lookup order-workers"] }
    allow_responses: { max: 1, expires: "2s" }
  }
}
```

Do not add a bare `"orders.lookup"` subscription grant: it defeats the queue-only restriction.

A matching static deny overrides a static allow. **`allow_responses` is an exception to treating that rule as absolute:** a tracked response can be permitted after the static publish check denies it. The worker above can send one timely reply despite its static publish deny. Requesters influence reply subjects, so this feature is not an absolute reply-subject allow list. The response count and expiry are workload-dependent policy choices.

Exposed versus fixed: broad subscriptions and reply publishing become queue-specific delivery and bounded replies.

See [authorization](https://docs.nats.io/learn/security/authorization), [subscription permissions](https://docs.nats.io/reference/config/authorization/users/permissions/subscribe/), [response permissions](https://docs.nats.io/reference/config/authorization/users/permissions/allow_responses/), and [v2.14.7 permission enforcement](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/client.go).

## 3. Enable TLS

Tier-1 rationale: authenticate the endpoint and protect credentials and messages in transit.

```text
tls {
  cert_file: "/etc/nats/certs/server-cert.pem"
  key_file:  "/etc/nats/certs/server-key.pem"
  ca_file:   "/etc/nats/certs/ca.pem"
  verify: true
  timeout: "2s"
}
```

Certificates per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md). Clients must validate both the CA chain and the intended server identity.

`verify: true` requires and verifies a client certificate against `ca_file`. It does not itself require a NATS password: that additional requirement comes from the selected authentication configuration. The password-user configuration in section 14 requires both a trusted client certificate and the corresponding password.

`verify_and_map: true` also verifies the certificate and derives a configured user's identity from certificate attributes, including supported email, DNS, or URI SANs, or the distinguished name. Choose and document the intended recipe. `verify_and_map` enables verification itself; setting both options true is not inherently invalid.

Exposed versus fixed: plaintext or an unverified endpoint becomes an authenticated TLS connection, with client certificates required where configured.

See [encryption and TLS](https://docs.nats.io/learn/security/encryption), the [TLS reference](https://docs.nats.io/reference/config/tls/), and the [v2.14.7 TLS parser](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go).

## 4. Keep the monitoring port private

Tier-1 rationale: monitoring discloses deployment-wide metadata outside application account permissions.

The HTTP monitoring endpoint is off unless configured (the official Docker images' bundled configuration configures it; see the introduction), for example with `http_port: 8222` or the server's `-m 8222` option. `https_port` serves the same data over TLS. It answers `/varz`, `/connz`, `/routez`, and, with JetStream enabled, `/jsz`.

For same-host collection:

```text
http: "127.0.0.1:8222"
```

Otherwise bind a deliberately restricted private interface. Avoid a bare `http_port` that leaves the binding implicit. For remote HTTP access, use an authenticating proxy and prevent direct access to its backend from unauthorized networks, including through container port publication.

`/connz` exposes connection metadata and counters, not captured message payloads. Query parameters request additional details: `subs=true` requests subscription subjects and `auth=true` requests identity information. **`auth=true` does not enable authentication.**

The native monitoring endpoint has no NATS user/password or JWT login. HTTPS encrypts transport but does not add that login, and client `verify`/`verify_and_map` settings do not protect monitoring with mTLS. Authenticated system-account monitoring over NATS is a separate path; enabling it does not secure an exposed HTTP port.

Exposed versus fixed: anonymous external JSON retrieval becomes access confined to the intended collector or authenticated front end, with direct backend bypass denied.

See [monitoring endpoints](https://docs.nats.io/learn/monitoring/monitoring-endpoints), [deployment hardening](https://docs.nats.io/learn/deployment/hardening), and the [v2.14.7 monitoring implementation](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/monitor.go).

## 5. Secure cluster, leafnode, and gateway connections separately

Tier-1 rationale: an unauthorized peer can create an additional route into trusted message traffic.

Enable only the links the deployment needs. An inbound cluster, leafnode, or gateway listener has its own authentication and TLS, independent of client `authorization` and top-level `tls`. Their default host is `0.0.0.0`; explicitly bind enabled listeners to intended private interfaces and restrict network peers.

All addresses and secrets below are placeholders or illustrative private addresses. Store credential-bearing URLs in protected configuration, never command arguments.

**Conditional: cluster routes, conventionally 6222.**

```text
cluster {
  name: ORDERS_CLUSTER
  listen: "10.0.0.10:6222"
  authorization {
    user: route
    password: "REPLACE_WITH_ROUTE_PASSWORD"
  }
  tls {
    cert_file: "/etc/nats/certs/route-cert.pem"
    key_file: "/etc/nats/certs/route-key.pem"
    ca_file: "/etc/nats/certs/peer-ca.pem"
  }
  routes: [
    "nats-route://route:REPLACE_WITH_URL_ENCODED_ROUTE_PASSWORD@route-b.example.com:6222"
  ]
}
```

Cluster TLS always requires peer certificate verification. Explicit `routes` URLs do not automatically obtain credentials from `cluster.authorization`; supply the remote credentials in each configured URL. Cluster authorization supports a username/password, not client-style `users` or `token`.

**Conditional: gateways, conventionally 7222.**

```text
gateway {
  name: EAST
  listen: "10.0.0.10:7222"
  reject_unknown_cluster: true
  authorization {
    user: gateway
    password: "REPLACE_WITH_GATEWAY_PASSWORD"
  }
  tls {
    cert_file: "/etc/nats/certs/gateway-cert.pem"
    key_file: "/etc/nats/certs/gateway-key.pem"
    ca_file: "/etc/nats/certs/peer-ca.pem"
  }
  gateways: [
    {
      name: WEST
      urls: [
        "nats://gateway:REPLACE_WITH_URL_ENCODED_REMOTE_GATEWAY_PASSWORD@gateway-west.example.com:7222"
      ]
    }
  ]
}
```

Gateway TLS also verifies peer certificates. `reject_unknown_cluster: true` restricts accepted cluster names; it does not replace credentials or TLS. Gateway authorization likewise does not support client-style `users` or `token`.

For both links, certificate SANs, advertised addresses, and explicit URLs must agree. Keep outgoing TLS `insecure` disabled. If the CA trusts more machines than should join, assess `verify_cert_and_check_known_urls: true` inside the link's TLS block. This additional restriction requires a reviewed set of known URLs and constrains dynamic growth.

**Conditional: accepted leafnodes, conventionally 7422.** A static-authentication hub can bind its leaf identity to an account:

```text
leafnodes {
  listen: "10.0.0.10:7422"
  authorization {
    user: leaf-orders
    password: "REPLACE_WITH_LEAF_PASSWORD"
    account: ORDERS
  }
  tls {
    cert_file: "/etc/nats/certs/leaf-server-cert.pem"
    key_file: "/etc/nats/certs/leaf-server-key.pem"
    ca_file: "/etc/nats/certs/peer-ca.pem"
    verify: true
  }
}
```

The hub must define `ORDERS`. Use matching username/password credentials in a protected remote URL when connecting to this static hub.

For a separate **operator-mode hub** that accepts a generated leaf user credential, the outbound leaf instead uses:

```text
leafnodes {
  remotes: [
    {
      url: "tls://hub.example.com:7422"
      account: ORDERS
      credentials: "/etc/nats/creds/orders-leaf.creds"
      tls {
        cert_file: "/etc/nats/certs/leaf-client-cert.pem"
        key_file: "/etc/nats/certs/leaf-client-key.pem"
        ca_file: "/etc/nats/certs/peer-ca.pem"
      }
    }
  ]
}
```

These static-hub and operator-hub authentication recipes are alternatives. A `.creds` file does not authenticate against the static password entry above.

The remote's `account` selects the **local** account on the leaf. Remote credentials determine the identity and account accepted by the hub. An outbound-only leaf needs no inbound leaf listener; a `remotes`-only configuration does not create one.

Exposed versus fixed: reachable plaintext or insufficiently authenticated peer links require permitted networks, the link's credentials, and its TLS policy. A successful test on client port 4222 proves nothing about these links.

See the [cluster](https://docs.nats.io/reference/config/cluster/), [gateway](https://docs.nats.io/reference/config/gateway/), [leafnode](https://docs.nats.io/reference/config/leafnodes/), [leaf authorization](https://docs.nats.io/reference/config/leafnodes/authorization/), and [leaf remotes](https://docs.nats.io/reference/config/leafnodes/remotes/) references.

## 6. Bound resources and process privilege

Tier-1 rationale: stalled connections and compromised authenticated clients should have finite resource budgets.

Set resource limits deliberately. At the September 2026 review baseline, the vendor reference documents defaults of **65,536 client connections (`64K`)** and **1 MiB payload (`1MB`)**. These are capacity limits, not authentication. Package configuration and service arguments can override them; inspect the effective deployment.

The following are workload-dependent examples, not recommended values for every deployment:

```text
max_connections: 1024
max_subscriptions: 256
max_control_line: 4KB
max_payload: 1MB
max_pending: 8MB
write_deadline: "2s"

authorization {
  timeout: "2s"
}
```

The selected TLS block also uses `timeout: "2s"`. For multi-tenancy, assess this account-local budget:

```text
limits {
  max_connections: 128
}
```

`max_subscriptions` bounds subscriptions per client connection. `max_payload` must not exceed `max_pending`. A connection count is not a connection-attempt rate limit. Slow-consumer handling may disconnect clients or lose Core NATS delivery; overly short deadlines can harm healthy clients.

Run `nats-server` as a dedicated non-root service identity. For same-host clients, use:

```text
host: "127.0.0.1"
port: 4222
```

For remote clients, choose a specific private interface instead of the default `0.0.0.0`, and apply network restrictions. Section 13 separates readable secrets from writable broker state.

Exposed versus fixed: excessive connections, subscriptions, queued output, and stalled handshakes encounter explicit budgets while healthy clients retain service.

See [runtime configuration](https://docs.nats.io/reference/config), [authorization timeout](https://docs.nats.io/reference/config/authorization/timeout), [account limits](https://docs.nats.io/reference/config/accounts/limits/), and [deployment hardening](https://docs.nats.io/learn/deployment/hardening).

## 7. Isolate accounts and reserve the system account for administration

Tier-1 rationale: a compromised tenant must not reach another tenant's messages or server administration.

Different usernames alone are not tenant isolation. A top-level user list places its users in the shared default account, `$G`. Define distinct accounts, each with its own subject space, and share only reviewed subjects.

This boundary fragment is incorporated with actual users in section 14:

```text
accounts {
  ORDERS {
    exports: [
      { stream: "orders.shipped", accounts: [ANALYTICS] }
    ]
  }
  ANALYTICS {
    imports: [
      { stream: { account: ORDERS, subject: "orders.shipped" } }
    ]
  }
  SYS {}
}
system_account: SYS
```

An export without an `accounts` restriction is public to other accounts that import it. The explicit restriction above permits only `ANALYTICS`. A Core NATS `stream` export shares messages; it is not automatically a JetStream stream export.

Keep application identities out of the system account. The default system-account name is `$SYS`; the selected configuration explicitly chooses the separately declared `SYS` account. Its credentials reach server monitoring and management and must be treated as administrative credentials.

A `$SYS.>` deny in an application account is useful defence in depth, but does not replace correct account membership and export/import boundaries.

Exposed versus fixed: unrelated users in `$G`, or publicly importable exports, become separate subject spaces with one reviewed sharing path and separate administration.

See [accounts and multitenancy](https://docs.nats.io/learn/security/accounts-and-multitenancy) and [cross-account configuration](https://docs.nats.io/learn/security/cross-account).

## 8. Bound JetStream storage and separate its administration

Tier-1 rationale: application credentials must not consume deployment-wide persistence capacity or implicitly authorize deletion, replay, and reconfiguration.

**Conditional: when JetStream is required**, set server storage budgets:

```text
jetstream {
  store_dir: "/var/lib/nats/jetstream"
  max_memory_store: 256MB
  max_file_store: 2GB
  request_queue_limit: 1000
}
```

Inside each account that needs persistence:

```text
jetstream {
  max_memory: 64MB
  max_file: 512MB
  max_streams: 10
  max_consumers: 20
  max_bytes_required: true
  memory_max_stream_bytes: 32MB
  disk_max_stream_bytes: 128MB
  max_ack_pending: 1000
}
```

Every capacity here is workload-dependent. Server storage budgets are not total process-memory or filesystem quotas; reserve operational headroom. `request_queue_limit` bounds pending JetStream API work, not client connection attempts.

**`max_consumers` is not a total account-wide consumer count.** In v2.14.7, the selected account limit is enforced against a stream's consumer count. Test the deployed stream types and effective limits. A successful reload alone does not prove a reduced account budget took effect: inspect the effective account limits and logs, especially when existing reservations exceed the proposed budget.

Retain narrow application publish/subscribe lists. Give administrative API subjects only to provisioning identities. A Core-only identity can explicitly deny:

```text
publish {
  allow: ["orders.>"]
  deny: ["$JS.API.>", "$JS.*.API.>"]
}
```

A JetStream application instead needs individually reviewed API grants for named resources, appropriate reply subscriptions, and acknowledgement permissions. A blanket API deny breaks legitimate JetStream clients. Broad `$JS.API.>` access can authorize operations such as stream deletion and stored-message retrieval.

**Conditional: independent JetStream systems across leaf and hub deployments.** Add distinct domains to their existing server JetStream blocks, for example `domain: EDGE` and `domain: HUB`, and select the intended system with CLI `--js-domain EDGE` or `--js-domain HUB`. Domains select JetStream systems; they are not tenant authorization boundaries. Account isolation and subject permissions still apply.

Exposed versus fixed: insufficiently bounded persistence gains account budgets, required stream sizes, object limits, and separate provisioning credentials.

See [server JetStream configuration](https://docs.nats.io/reference/config/jetstream/), [account JetStream limits](https://docs.nats.io/reference/config/accounts/jetstream/), [request queue limits](https://docs.nats.io/reference/config/jetstream/request_queue_limit), [v2.14.7 consumer enforcement](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/consumer.go), [API subjects](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/jetstream_api.go), and [JetStream across leaf nodes](https://docs.nats.io/learn/topologies/leaf-nodes).

## 9. Encrypt sensitive JetStream storage when required

Tier-1 rationale: copying persistence files should not directly disclose stored message content.

**Conditional: for sensitive persisted messages**, add these fields to the existing server JetStream block:

```text
encryption_key: $JS_ENCRYPTION_KEY
cipher: aes
```

Provision `JS_ENCRYPTION_KEY` through a protected service secret. The vendor recommends at least 32 bytes of key material. `cipher: aes` selects AES-GCM when that is the deployment policy.

This is server-wide file-store data and metadata encryption, not per-account encryption or protection from an authorized running broker. Protect recovery keys separately from data, and independently protect backups.

Rotation requires the documented previous-key transition and restart. During that transition the existing JetStream block includes:

```text
encryption_key: $JS_ENCRYPTION_KEY
prev_encryption_key: $JS_PREVIOUS_ENCRYPTION_KEY
cipher: aes
```

Follow the vendor's full transition and recovery procedure before retiring the old key. Do not infer successful rotation or recoverability from startup alone.

Exposed versus fixed: unencrypted persistence becomes encrypted file-store data and metadata, with tested recovery and key rotation.

See the [encryption-key reference](https://docs.nats.io/reference/config/jetstream/encryption_key), [previous-key reference](https://docs.nats.io/reference/config/jetstream/prev_encryption_key), and [encryption and rotation guidance](https://docs.nats.io/learn/security/encryption).

## 10. Keep MQTT conditional and scoped

Tier-1 rationale: an optional protocol listener must not bypass identity and subject boundaries.

Leave MQTT unconfigured unless required. When enabled, give it a private listener and its own TLS configuration:

```text
mqtt {
  listen: "10.0.0.10:8883"
  tls {
    cert_file: "/etc/nats/certs/mqtt-cert.pem"
    key_file: "/etc/nats/certs/mqtt-key.pem"
    ca_file: "/etc/nats/certs/ca.pem"
  }
}
```

Add individually scoped device users inside the intended account:

```text
{
  user: device-01
  password: "REPLACE_WITH_DEVICE_01_BCRYPT_HASH"
  allowed_connection_types: ["MQTT"]
  permissions {
    publish: { allow: ["devices.device-01.telemetry"] }
    subscribe: { allow: ["devices.device-01.command"] }
  }
}
```

Review the translated NATS subjects for the MQTT topics your clients use. Remove unintended MQTT-specific and top-level `no_auth_user` settings. Restrict existing Core users to `allowed_connection_types: ["STANDARD"]` if they must not use additional protocol listeners.

MQTT requires JetStream, so its account and server persistence budgets apply. MQTT cannot perform the normal NKey nonce-signature exchange. Operator-mode MQTT uses an explicitly permitted bearer user JWT as the password; possession is sufficient, making TLS and secret handling essential.

Exposed versus fixed: an additional anonymous or overly broad device listener becomes authenticated, protocol-restricted access to reviewed subjects.

See [MQTT configuration](https://docs.nats.io/reference/config/mqtt/), [MQTT authentication](https://docs.nats.io/learn/mqtt/auth-and-clustering), and [connection-type restrictions](https://docs.nats.io/reference/config/authorization/users/allowed_connection_types).

## 11. Keep WebSockets conditional and check browser origins

Tier-1 rationale: browser-accessible messaging needs authenticated transport and an explicit browser-origin policy.

Leave WebSockets unconfigured unless required. An example listener is:

```text
websocket {
  listen: "10.0.0.10:8443"
  tls {
    cert_file: "/etc/nats/certs/websocket-cert.pem"
    key_file: "/etc/nats/certs/websocket-key.pem"
  }
  handshake_timeout: "2s"
  allowed_origins: ["https://app.example.com"]
}
```

Replace the example origin with the deployed application origin. Alternatively, choose `same_origin: true` when the application and WebSocket endpoint have the required same-origin relationship.

Scope browser users inside their account:

```text
{
  user: browser-orders
  password: "REPLACE_WITH_BROWSER_USER_BCRYPT_HASH"
  allowed_connection_types: ["WEBSOCKET"]
  permissions {
    publish: { allow: ["orders.lookup"] }
    subscribe: { allow: ["_INBOX.browser-orders.>"] }
  }
}
```

The client must use the matching inbox prefix. Provision browser credentials according to the application's identity model; do not distribute one permanent shared credential to every browser.

Origin checks are not client authentication. Non-browser clients can omit or construct `Origin`. TLS is required unless explicitly disabled with `no_tls`; if a proxy terminates TLS, its backend path must be inaccessible to unauthorized clients. Review listener-specific authorization and `no_auth_user` overrides.

Exposed versus fixed: unintended websites or a directly reachable plaintext backend become an authenticated WSS endpoint with an explicit browser-origin policy and protected backend.

See [WebSocket configuration](https://docs.nats.io/reference/config/websocket/) and [connection-type restrictions](https://docs.nats.io/reference/config/authorization/users/allowed_connection_types).

## 12. Isolate auth callout when external authentication is required

Tier-1 rationale: an external authenticator must not expose submitted credentials or become an unrestricted impersonation interface.

**Conditional: only for deployments that need external identity integration**, configure a dedicated authentication-service account and narrowly listed bypass identities. This static-server fragment replaces the corresponding authentication configuration; it is not an extra checkbox to append to section 14:

```text
authorization {
  timeout: "2s"
  auth_callout {
    issuer: "REPLACE_WITH_GENERATED_CALLOUT_ISSUER_PUBLIC_ACCOUNT_NKEY"
    account: AUTH
    auth_users: [auth-svc]
    xkey: "REPLACE_WITH_GENERATED_CALLOUT_PUBLIC_XKEY"
  }
}

accounts {
  AUTH {
    users: [
      {
        user: auth-svc
        password: "REPLACE_WITH_AUTH_SERVICE_BCRYPT_HASH"
        permissions {
          publish: { deny: [">"] }
          subscribe: { allow: ["$SYS.REQ.USER.AUTH"] }
          allow_responses: { max: 1, expires: "2s" }
        }
      }
    ]
  }
  ORDERS {}
  ANALYTICS {}
}
```

Keep application users out of `AUTH`. The issuer is a public key; the authentication service holds the corresponding signing material and the private XKey in its protected runtime configuration. XKey encryption protects callout payloads. The service must validate requests and return correctly signed responses assigning intended accounts and permissions.

This requires a functioning authentication service. Test service outage as rejected admission. Static-server configuration and operator-mode account-JWT configuration are different workflows. `allowed_accounts` is not a universal target-account restriction: its meaning depends on the mode. Review the appropriate workflow before using it.

Exposed versus fixed: ordinary users cannot observe authentication exchanges, excessive identities cannot bypass delegation, and the exchange is isolated and encrypted.

See [auth callout](https://docs.nats.io/learn/security/auth-callout), [configuration fields](https://docs.nats.io/reference/config/authorization/auth_callout), [v2.14.7 parsing](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go), and [response validation](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/auth_callout.go).

## 13. Give each process only its required files

Tier-1 rationale: local file access must not turn broker compromise into credential theft across applications or tenants.

Use private directories and owner-readable secret files, typically `0700` and `0600`, with ownership appropriate to the process that needs them. These are deployment policies, not NATS directives.

| Material | Required access |
| --- | --- |
| Server configuration, TLS private keys, and link credentials | Readable by the dedicated broker service identity; writable only by the deployment authority where practical |
| JetStream storage and operator resolver state | Writable by the broker in designated state directories |
| Application `.creds` and user-seed files | Readable by their owning application, without granting the broker access to every application's seed |
| Operator/account signing seeds and provisioning store | Restricted to the provisioning system |
| Outbound leaf `.creds` | A legitimate broker-readable exception because the broker itself authenticates the outbound link |

Check parent-directory permissions, backup copies, secret delivery, and the actual service identity. Systemd sandboxing must leave required state paths writable. Do not assume a packaged service unit has the intended identity and restrictions without inspecting the running deployment.

Exposed versus fixed: broadly readable credentials and unnecessary signing keys on the broker become access limited to each process's required material.

See [deployment hardening](https://docs.nats.io/learn/deployment/hardening) and [credential and signing-store handling](https://docs.nats.io/learn/security/operator-mode).

## 14. Assemble one selected configuration

This selected example uses static password users, separate accounts, client mTLS, loopback client access, loopback monitoring, and JetStream for `ORDERS`. It supplies every identity used by the primary Verify commands. For remote clients, replace the loopback client binding with the intended private interface and enforce the corresponding network policy.

All capacities and timeouts are workload-dependent examples. Replace every password placeholder with a separately generated bcrypt hash. Clients supply the corresponding original password.

Optional operator mode, encryption at rest, peer links, MQTT, WebSockets, and auth callout are not enabled here. Apply their separate recipes only when required. A Core-only deployment can omit both the server and account JetStream blocks.

```text
host: "127.0.0.1"
port: 4222
http: "127.0.0.1:8222"

max_connections: 1024
max_subscriptions: 256
max_control_line: 4KB
max_payload: 1MB
max_pending: 8MB
write_deadline: "2s"

authorization {
  timeout: "2s"
}

tls {
  cert_file: "/etc/nats/certs/server-cert.pem"
  key_file: "/etc/nats/certs/server-key.pem"
  ca_file: "/etc/nats/certs/ca.pem"
  verify: true
  timeout: "2s"
}

jetstream {
  store_dir: "/var/lib/nats/jetstream"
  max_memory_store: 256MB
  max_file_store: 2GB
  request_queue_limit: 1000
}

accounts {
  ORDERS {
    limits { max_connections: 128 }

    jetstream {
      max_memory: 64MB
      max_file: 512MB
      max_streams: 10
      max_consumers: 20
      max_bytes_required: true
      memory_max_stream_bytes: 32MB
      disk_max_stream_bytes: 128MB
      max_ack_pending: 1000
    }

    users: [
      {
        user: order-svc
        password: "REPLACE_WITH_ORDER_SVC_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: {
            allow: ["orders.>"]
            deny: ["$SYS.>", "$JS.API.>", "$JS.*.API.>"]
          }
          subscribe: { allow: ["_INBOX.order-svc.>"] }
        }
      }
      {
        user: order-consumer
        password: "REPLACE_WITH_ORDER_CONSUMER_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: { deny: [">"] }
          subscribe: { allow: ["orders.>"] }
        }
      }
      {
        user: order-worker
        password: "REPLACE_WITH_ORDER_WORKER_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: { deny: [">"] }
          subscribe: { allow: ["orders.lookup order-workers"] }
          allow_responses: { max: 1, expires: "2s" }
        }
      }
      {
        user: orders-provisioner
        password: "REPLACE_WITH_ORDERS_PROVISIONER_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: { allow: ["$JS.API.>"] }
          subscribe: { allow: ["_INBOX.orders-provisioner.>"] }
        }
      }
    ]

    exports: [
      { stream: "orders.shipped", accounts: [ANALYTICS] }
    ]
  }

  ANALYTICS {
    limits { max_connections: 128 }
    users: [
      {
        user: analytics-reader
        password: "REPLACE_WITH_ANALYTICS_READER_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: { deny: [">"] }
          subscribe: { allow: ["orders.>"] }
        }
      }
    ]
    imports: [
      { stream: { account: ORDERS, subject: "orders.shipped" } }
    ]
  }

  SYS {
    limits { max_connections: 128 }
    users: [
      {
        user: sys-admin
        password: "REPLACE_WITH_SYS_ADMIN_BCRYPT_HASH"
        allowed_connection_types: ["STANDARD"]
        permissions {
          publish: { allow: ["$SYS.REQ.>"] }
          subscribe: { allow: ["_INBOX.sys-admin.>"] }
        }
      }
    ]
  }
}

system_account: SYS
```

`orders-provisioner` deliberately holds account-level JetStream administration; it is not an application credential or a system-account identity. `sys-admin` has the system request permissions used below, rather than unrestricted application access.

`analytics-reader` can subscribe to its account's `orders.>` space, but the only imported ORDERS subject is `orders.shipped`. Its wildcard does not import other ORDERS subjects.

## Verify

REASONED: verification scope from the recorded authoring limitations and cited sources. Service behaviour has **not** been demonstrated here. `nats-server`, `nats`, `nk`, `nsc`, Docker, and Podman are unavailable on the authoring environment's `PATH`; no live broker, certificate fixtures, authentication service, or external peer environment was supplied. The filesystem restrictions prohibit provisioning binaries and writable credential fixtures. The live comparisons below are **REASONED** from the cited documentation and pinned sources.

REASONED: comparison procedure from the paired controls below; no live broker or external test fixture is available. Run exposed-state comparisons only in an authorized isolated fixture. Keep the target, identity, payload, and observation window matched while changing the control under test. Record diagnostics and positive controls without secrets. DNS failures, generic timeouts, and local fixture errors are inconclusive.

### V0. Offline checks and their limits

**Demonstrated here:** the five fenced Bash fragments below passed `bash -n` with Bash 5.3.9 and ShellCheck 0.11.0. Guard-only execution rejected 145 invalid input cases and allowed five substituted controls to reach a local marker. Those cases included empty arguments, original and embedded placeholders, angle brackets, `example.com`, wrong argument counts, and missing setup with unrelated caller arguments. No network command ran. This establishes bounded shell and guard evidence, not CLI semantics or general bypass resistance.

The prior guide's reported 14 invalid guard cases and two positive controls concerned its earlier fragments; they are not evidence that the replacement service checks ran.

REASONED: native-parsing procedure from the linked v2.14.7 configuration-test source; the pinned server and certificate, JWT and include fixtures are unavailable. **Offline-capable, not demonstrated here: native parsing.** With the pinned server and readable certificate, JWT, and include fixtures, run `timeout 10s nats-server -t -c selected.conf`. Repeat for every complete conditional configuration actually selected. Pair each valid fixture with a deliberately malformed configuration or unknown-field negative control. Successful parsing does not establish reachability, authorization, or secure placeholder replacement. See [v2.14.7 configuration-test handling](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go).

REASONED: generation procedure from the cited NATS key and JWT documentation; pinned tools and credential fixtures are unavailable. **Offline-capable, not demonstrated here: credential generation.** The NKey commands in section 1 and operator/account/user generation require installed pinned tools and a private writable store. Generation and local inspection need no broker; publication to a resolver and broker acceptance do.

REASONED: file-review scope from the configuration and credential recipes above; no selected deployment files or generated credentials were supplied. **Separate deployment-file check required:** scan the selected configuration, every included file, and referenced secret inputs for unresolved `REPLACE_WITH_` values and documentation addresses. Inspect generated key/JWT types and references with the appropriate tooling. A password such as `REPLACE_WITH_LONG_RANDOM_PASSWORD` can be syntactically valid, so `-t` is not a placeholder validator. An absence of placeholder text does not establish password strength or key ownership.

### V1. Running identity, effective configuration, and listeners (REASONED: inventory and isolation expectations from the linked hardening and configuration references; no running service or deployment namespace)

**REASONED: no running NATS service, service manager fixture, or deployment network namespace is available.**

On the deployment host, run bounded inventory commands such as `timeout 10s ss -tlnp`, with sufficient privilege to identify owners. Read the whole listener inventory, including IPv6. For containers, inspect both the broker's network namespace and host-side published ports.

Inspect the actual process/service identity, loaded configuration path, startup arguments, startup logs, and effective file access. Compare them with sections 6 and 13. Inspect effective limits through the allowed monitoring path and JetStream account information, rather than assuming package defaults.

Exposed versus fixed: root execution, broadly readable secrets, unintended writable paths, and public listeners become the dedicated service identity, necessary file access, and intended bindings. Offline file inspection cannot establish what the running process actually experiences.

Inventory 4222, 8222, and every enabled peer or protocol listener, including 6222, 7422, 7222, MQTT, and WebSockets. Use the actual configured ports. See [hardening](https://docs.nats.io/learn/deployment/hardening) and [configuration](https://docs.nats.io/reference/config).

### V2. Authentication, TLS, and out-of-scope subjects (REASONED: authentication, TLS and subject-permission comparisons from the cited NATS and pinned CLI sources; no broker, CLI or certificate fixtures)

**REASONED: no pinned CLI/server, trusted client/server certificates, or broker logs are available.**

The CLI reads saved contexts and environment settings before defaults. Each block clears inherited `NATS_*` settings and uses `--no-context`. This prevents a supposedly anonymous check from silently inheriting a token, user, seed, credentials file, or proxy setting. A fully clean `env -i` launch is another way to isolate ambient settings, but required credentials must still be supplied deliberately.

Paste the whole subshell after substituting all four values. These probes accept a DNS hostname or IPv4 address, without a scheme, port, or embedded credentials. TLS paths and the username are exported inside the guarded subshell. The password is read from the terminal and never exported or passed as a command argument: natscli v0.4.0 offers no stdin input for it and binds `--password` to `NATS_PASSWORD`, so each `nats` command that needs it receives it as a one-command `NATS_PASSWORD="$pw"` prefix assignment. That moves the password out of argv, not out of reach: it can remain readable through `/proc/<pid>/environ` by the same user and by root while that `nats` command, or the `timeout` that runs it, is running. Environment secrets still require a trusted local execution account.

The first publish is the allowed control. The subsequent operations deliberately test missing credentials, a wrong password, a missing client certificate, and forbidden publish/subscribe subjects. Inspect each command's diagnostics; the block's final exit status is not a combined verdict.

```bash
# REASONED: authentication, TLS and subject permissions; no pinned server/CLI, broker or certificate fixtures. Expected outcomes and vendor sources are recorded in this section.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
  { unset -n v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA &&
    unset -v v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA; } 2>/dev/null ||
    { echo 'cannot clear the variables this block uses; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  for v in "${!NATS_@}"; do
    { unset -n "$v" && unset -v "$v"; } 2>/dev/null || { echo "cannot clear ambient $v; not probing"; exit 2; }
  done
  for f in "$2" "$3" "$4"; do
    [ -r "$f" ] || { echo 'a TLS fixture is unreadable; not probing'; exit 2; }
  done
  export NATS_CERT="$2" NATS_KEY="$3" NATS_CA="$4"
  srv="nats://$1:4222"
  IFS= read -r -s -t 60 -p 'order-svc password: ' pw < /dev/tty || { echo 'password input failed'; exit 2; }
  printf '\n'
  case "$pw" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'supply a real password'; exit 2 ;; esac
  export NATS_USER=order-svc || { echo 'credential export failed'; exit 2; }
  [ "$NATS_USER" = order-svc ] || { echo 'username mismatch'; exit 2; }
  opts=(--no-context --server "$srv" --timeout 3s --inbox-prefix _INBOX.order-svc)
  NATS_PASSWORD="$pw" timeout 10s nats "${opts[@]}" pub orders.created hi || { echo 'positive control failed; stop'; exit 1; }
  unset NATS_USER
  timeout 10s nats "${opts[@]}" pub orders.created hi
  export NATS_USER=order-svc
  NATS_PASSWORD="wrong-$pw" timeout 10s nats "${opts[@]}" pub orders.created hi
  unset NATS_CERT NATS_KEY
  NATS_PASSWORD="$pw" timeout 10s nats "${opts[@]}" pub orders.created hi
  export NATS_CERT="$2" NATS_KEY="$3"
  NATS_PASSWORD="$pw" timeout 10s nats "${opts[@]}" pub billing.charge hi
  NATS_PASSWORD="$pw" timeout 6s nats "${opts[@]}" sub 'billing.>' --count 1
)
```

Exposed versus fixed:

- With password authentication absent, omitted/wrong credentials can be admitted; the fixed password-user recipe must report an authentication rejection.
- Without required client verification, a client lacking a trusted certificate can be admitted; the fixed recipe must reject the missing certificate. Repeat the complete block with an untrusted but readable client certificate/key pair: its initial positive-control command must instead fail with the corresponding TLS diagnostic.
- A client that fails to check server identity can accept the wrong endpoint identity. Repeat against an authorized DNS alias that reaches the same test listener but is absent from the server certificate SANs. Require a hostname-validation diagnostic, while the correct hostname succeeds.
- Broad permissions permit `billing.charge` publication and `billing.>` subscription; the fixed `order-svc` must produce the corresponding permission violations.

If using `verify_and_map` instead, the positive control is a correctly mapped certificate; absent, untrusted, and unmapped certificates are distinct negative cases. Do not describe a password as mandatory for that alternative.

See [authentication](https://docs.nats.io/learn/security/authentication-basics), [TLS](https://docs.nats.io/reference/config/tls/), [authorization](https://docs.nats.io/learn/security/authorization), and [pinned CLI credential handling](https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/util.go).

### V3. Actual delivery, queue restrictions, and bounded replies (REASONED: delivery, queue, reply and request-helper procedures from the cited permissions and pinned CLI sources; no broker or client fixtures)

**REASONED: no broker, pinned CLI, two authenticated clients, or response-test client is available.**

A successful publish message or a quiet subscriber is insufficient proof of delivery. In a quiet fixture, start terminal 1, wait for subscription establishment, then run terminal 2 while terminal 1 is still active. The consumer must print the exact marker from terminal 2.

Terminal 1 is self-contained and reads its password inside the guarded subshell. Piping a password to `nats sub` does not configure authentication; in CLI v0.4.0, a username without a password is treated as a token.

```bash
# REASONED: subscriber delivery control; no pinned server/CLI, broker or certificate fixtures. Expected outcomes and vendor sources are recorded in this section.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CONSUMER_CERT_FILE' 'REPLACE_WITH_CONSUMER_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
  { unset -n v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA &&
    unset -v v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA; } 2>/dev/null ||
    { echo 'cannot clear the variables this block uses; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  for v in "${!NATS_@}"; do
    { unset -n "$v" && unset -v "$v"; } 2>/dev/null || { echo "cannot clear ambient $v; not probing"; exit 2; }
  done
  for f in "$2" "$3" "$4"; do
    [ -r "$f" ] || { echo 'a TLS fixture is unreadable; not probing'; exit 2; }
  done
  export NATS_CERT="$2" NATS_KEY="$3" NATS_CA="$4"
  srv="nats://$1:4222"
  IFS= read -r -s -t 60 -p 'order-consumer password: ' pw < /dev/tty || { echo 'password input failed'; exit 2; }
  printf '\n'
  case "$pw" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'supply a real password'; exit 2 ;; esac
  export NATS_USER=order-consumer || { echo 'credential export failed'; exit 2; }
  NATS_PASSWORD="$pw" timeout 45s nats --no-context --server "$srv" --timeout 3s sub 'orders.>' --count 1
)
```

Terminal 2 independently establishes its target, TLS configuration, and credentials; it cannot inherit variables from terminal 1's subshell:

```bash
# REASONED: publisher delivery control; no pinned server/CLI, broker or certificate fixtures. Expected outcomes and vendor sources are recorded in this section.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
  { unset -n v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA &&
    unset -v v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA; } 2>/dev/null ||
    { echo 'cannot clear the variables this block uses; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  for v in "${!NATS_@}"; do
    { unset -n "$v" && unset -v "$v"; } 2>/dev/null || { echo "cannot clear ambient $v; not probing"; exit 2; }
  done
  for f in "$2" "$3" "$4"; do
    [ -r "$f" ] || { echo 'a TLS fixture is unreadable; not probing'; exit 2; }
  done
  export NATS_CERT="$2" NATS_KEY="$3" NATS_CA="$4"
  srv="nats://$1:4222"
  IFS= read -r -s -t 60 -p 'order-svc password: ' pw < /dev/tty || { echo 'password input failed'; exit 2; }
  printf '\n'
  case "$pw" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'supply a real password'; exit 2 ;; esac
  export NATS_USER=order-svc || { echo 'credential export failed'; exit 2; }
  marker=$(date +%s%N) || { echo 'marker generation failed; not publishing'; exit 2; }
  [ -n "$marker" ] || { echo 'marker generation failed; not publishing'; exit 2; }
  marker="marker-$marker"
  printf 'Expected delivery: %s\n' "$marker"
  NATS_PASSWORD="$pw" timeout 10s nats --no-context --server "$srv" --timeout 3s \
    --inbox-prefix _INBOX.order-svc pub orders.created "$marker"
)
```

For queue comparisons, rerun the complete consumer block with the `order-worker` identity, its password and certificate fixtures, and replace the final subscription arguments with `sub orders.lookup --queue order-workers --count 1`. Publish a unique marker to `orders.lookup` using the complete publisher block. Then repeat with `--queue other-workers` and with no queue option. The exposed broad subscription grant accepts these forms; the fixed worker must receive through `order-workers` and reject the other forms. Test both acceptance and actual marker delivery. Do not grant the worker a bare `orders.lookup` permission to make a failing test pass.

The following self-contained request block is also used by V4 and V5. Its last three inputs are identity, subject, and JSON body. Keep subjects such as `$SYS.REQ.SERVER.PING` and `$JS.API.INFO` single-quoted on the `set --` line. The inbox prefix matches the selected identity.

```bash
# REASONED: request/reply, account and JetStream checks; no pinned server/CLI, broker or certificate fixtures. Expected outcomes and vendor sources are recorded in this section.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE' 'REPLACE_WITH_CA_FILE' 'order-svc' 'orders.lookup' '{}'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 7 ] || { echo 'provide exactly 7 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$5" in order-svc|orders-provisioner|sys-admin) ;; *) echo 'select a listed test identity'; exit 2 ;; esac
  case "$6" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the request subject'; exit 2 ;; esac
  case "$7" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the request body'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
  { unset -n v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA &&
    unset -v v f pw srv opts marker NATS_USER NATS_PASSWORD NATS_CERT NATS_KEY NATS_CA; } 2>/dev/null ||
    { echo 'cannot clear the variables this block uses; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  for v in "${!NATS_@}"; do
    { unset -n "$v" && unset -v "$v"; } 2>/dev/null || { echo "cannot clear ambient $v; not probing"; exit 2; }
  done
  for f in "$2" "$3" "$4"; do
    [ -r "$f" ] || { echo 'a TLS fixture is unreadable; not probing'; exit 2; }
  done
  export NATS_CERT="$2" NATS_KEY="$3" NATS_CA="$4"
  srv="nats://$1:4222"
  IFS= read -r -s -t 60 -p "$5 password: " pw < /dev/tty || { echo 'password input failed'; exit 2; }
  printf '\n'
  case "$pw" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'supply a real password'; exit 2 ;; esac
  export NATS_USER="$5" || { echo 'credential export failed'; exit 2; }
  NATS_PASSWORD="$pw" timeout 10s nats --no-context --server "$srv" --timeout 3s \
    --inbox-prefix "_INBOX.$5" request "$6" "$7"
)
```

**Response-permission comparison, REASONED: a client capable of retaining the worker connection and inspecting permission errors is unavailable.** Use a protocol/client fixture with a 20-second total bound and 3-second operation deadlines:

1. Authenticate as `order-worker`, subscribe to `orders.lookup` in queue `order-workers`, and flush the subscription.
2. Issue the request above. On the same worker connection that receives it, publish `ok` to its received reply subject within two seconds. The requester must receive it.
3. Publish a second reply on that same subject and require a permission violation.
4. Receive a fresh request, wait beyond its two-second grant, and require rejection of the late reply.
5. Attempt an unrelated publication to `billing.charge` on the worker connection and require a permission violation.

The wire operations are a queue `SUB orders.lookup order-workers 1`, followed by `PUB` to the reply subject delivered in the received `MSG`; the two-byte reply frame is `PUB <received-reply> 2\r\nok\r\n`. Substitute the actual reply subject inside the protocol client. A new CLI connection cannot reuse the first connection's response grant.

In an exposed broad-publish configuration, extra, expired, and unrelated publications can succeed. In the fixed configuration only the first timely tracked reply succeeds. Recall that a dynamic response grant can authorize a subject otherwise denied statically.

See [subscription permissions](https://docs.nats.io/reference/config/authorization/users/permissions/subscribe/), [response permissions](https://docs.nats.io/reference/config/authorization/users/permissions/allow_responses/), [pinned CLI subscription flags](https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/sub_command.go), and [server enforcement](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/client.go).

### V4. Accounts, approved sharing, and system requests (REASONED: account isolation, sharing and system-request comparisons from the cited account and CLI sources; no multi-account broker or client fixtures)

**REASONED: no multi-account broker, system credential, or concurrent client fixture is available.**

Use the complete consumer block separately as `order-consumer` and `analytics-reader`, with their own credentials and TLS fixtures, but raise the ORDERS consumer's final subscription to `--count 2` so it stays subscribed across both markers below: in natscli v0.4.0 a subscriber unsubscribes and exits as soon as it reaches its `--count`, so a `--count 1` ORDERS consumer would exit after the first marker and never observe the second. Keep `analytics-reader` at `--count 1`, since it should receive only the shipped marker. Publish an `orders.created` marker from `order-svc`.

Exposed versus fixed: identities placed together in `$G` can receive the same allowed subject. In the selected fixed configuration, the ORDERS consumer receives `orders.created`, while the ANALYTICS subscriber does not. Then publish a fresh `orders.shipped` marker: both must receive it through the approved export/import. The shipped-message positive control must use the same ANALYTICS subscription setup as the isolation check; silence alone is inconclusive.

For an administrative comparison, use the request block with `sys-admin`, subject `$SYS.REQ.SERVER.PING`, and body `{}`. Require a system response. Repeat with `order-svc` and its own credentials and inbox prefix: require the corresponding publish-permission rejection. An exposed application identity with administrative account membership and grants can receive the administrative response; the fixed tenant identity cannot.

If validating private-export restrictions, add an isolated third test account with a matching import. An unrestricted export permits that sharing; `accounts: [ANALYTICS]` must prevent it. Confirm successful sharing to ANALYTICS in the same run.

See [accounts](https://docs.nats.io/learn/security/accounts-and-multitenancy) and [cross-account sharing](https://docs.nats.io/learn/security/cross-account).

### V5. JetStream authority and effective limits (REASONED: JetStream authority and limit comparisons from the cited account, consumer and API sources; no server, CLI or disposable store)

**REASONED: no JetStream server, pinned CLI, or disposable persistence fixture is available. Conditional on JetStream being enabled.**

Use the guarded request block with the following concrete subjects and bodies. Start from an isolated empty test account/store; `SC_TEST` and the other names below are disposable test resources. Record API response bodies, not only CLI exit status.

| Identity and request | Exposed versus fixed comparison |
| --- | --- |
| `orders-provisioner`: `$JS.API.INFO`, `{}` | Obtain effective account limits and usage. Repeat after reload and correlate logs; a successful reload without changed effective limits is insufficient. |
| `orders-provisioner`: `$JS.API.STREAM.CREATE.SC_TEST`, `{"name":"SC_TEST","subjects":["orders.test"],"storage":"file","num_replicas":1,"max_bytes":1048576,"discard":"new"}` | A below-limit stream must be created successfully. These are workload-dependent test capacities. |
| `order-svc`: the same create request, or `$JS.API.STREAM.INFO.SC_TEST`, `{}` | An exposed broadly authorized application can administer/inspect persistence; the fixed Core-only identity must receive an API-subject permission violation. |
| `orders-provisioner`: `$JS.API.STREAM.MSG.GET.SC_TEST`, `{"seq":1}` | After publishing a marker to `orders.test` with the complete publisher block, the provisioner can retrieve it. Repeat as `order-svc`; the fixed Core-only identity must be denied. |
| `orders-provisioner`: `$JS.API.STREAM.CREATE.SC_UNBOUNDED`, `{"name":"SC_UNBOUNDED","subjects":["orders.unbounded"],"storage":"file","num_replicas":1}` | An insufficiently bounded account accepts a stream without a byte cap; `max_bytes_required: true` must reject it. |
| `orders-provisioner`: `$JS.API.STREAM.CREATE.SC_BIG`, `{"name":"SC_BIG","subjects":["orders.big"],"storage":"file","num_replicas":1,"max_bytes":268435456}` | An exposed account can reserve this larger stream; the selected 128MB file-stream ceiling must reject it. |
| `orders-provisioner`: `$JS.API.CONSUMER.DURABLE.CREATE.SC_TEST.C01`, `{"stream_name":"SC_TEST","config":{"durable_name":"C01","ack_policy":"explicit","max_ack_pending":1000}}` | A below-limit consumer must succeed. Repeat with unique matching names through `C20`; the next must be rejected by the selected per-stream account consumer limit. |
| On a fresh disposable stream, or after deleting a consumer so the per-stream consumer count is not the cause, create one consumer with `max_ack_pending: 1000`, then repeat the same operation with `max_ack_pending: 1001` | The below-limit consumer must be created successfully; the `1001` request must be rejected specifically by the selected consumer acknowledgement ceiling, not by the per-stream consumer count reached above. Confirm the same `1001` request is accepted once only the acknowledgement ceiling is relaxed. |
| `order-svc`, then `orders-provisioner`: `$JS.API.STREAM.DELETE.SC_TEST`, `{}` | The fixed application must be denied; the provisioner must delete the disposable stream successfully. Recreate the fixture if an exposed application successfully deleted it. |

Also create small, uniquely named streams with distinct subjects until reaching the configured stream count, then require rejection of the next. Keep their aggregate storage reservations below the account budget so the test measures stream count.

Test memory and file account budgets separately. Reserve below-limit streams first, then request one more reservation exceeding `max_memory` or `max_file` while keeping individual stream sizes and stream count valid. Require the corresponding resource error. Exercise server budgets across enough independently budgeted accounts; a single account hitting its own limit does not prove the server-wide limit.

For stored-byte enforcement, publish bounded messages into the disposable `SC_TEST` stream until its byte limit is reached. Its `discard: "new"` test policy makes further storage rejection distinguishable from automatic eviction. Observe JetStream publish acknowledgements through a fixture identity with the necessary inbox grant. Keep each test batch bounded, and record successful storage before the rejection.

Use a 30-second bound per isolated load-test batch and finite message/object counts. Clean up all test streams and consumers, inspect for leftovers after interruptions, and record cleanup. If domains are configured, repeat against the intended explicit API domain or the corresponding CLI `--js-domain`; verify that switching domains selects the intended system without changing tenant authorization.

See [account limits and reload caveats](https://docs.nats.io/reference/config/accounts/jetstream/), [consumer enforcement](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/consumer.go), and [API subjects](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/jetstream_api.go).

### V6. Encryption and recovery (REASONED: encrypted-store recovery comparisons from the linked encryption and rotation references; no runtime, stores or recovery keys)

**REASONED: no JetStream runtime, disposable encrypted stores, recovery keys, or writable fixtures are available. Conditional on encryption being selected.**

Use separate disposable unencrypted and encrypted stores. Create `SC_TEST`, publish a unique marker to `orders.test`, and retrieve it through `$JS.API.STREAM.MSG.GET.SC_TEST` with `{"seq":1}` using the guarded request block and provisioning identity.

Stop the fixture before inspecting copied persistence files. Compare the unencrypted and encrypted stores, then restart the encrypted copy with the correct key and retrieve the same marker. Repeat recovery from copies with a missing and a wrong key; require that the original stored data cannot be recovered under those conditions, with matching diagnostics. Do not mistake an empty newly initialized store for recovery.

Test the documented `prev_encryption_key` transition, restart, and subsequent recovery with the new key, including the documented removal of the previous key after migration. Bound each startup/recovery attempt to 30 seconds and use copies so failed tests do not destroy the sole recoverable data.

Exposed versus fixed: a copied plaintext store discloses data; the encrypted store requires the appropriate key and remains recoverable through the tested procedure. Absence of a plaintext marker alone proves neither complete encryption coverage nor recoverability.

See [encryption and rotation](https://docs.nats.io/learn/security/encryption) and [previous-key configuration](https://docs.nats.io/reference/config/jetstream/prev_encryption_key).

### V7. Actual cluster, gateway, and leaf peers (REASONED: peer admission and delivery comparisons from the linked cluster, gateway and leaf references; no peer servers, certificates or test networks)

**REASONED: no peer servers, peer certificate fixtures, or allowed/disallowed peer networks are available. Conditional on each enabled link.**

Use actual pinned servers and complete peer configurations, with bounded fixture runs such as `timeout 30s nats-server -c peer-test.conf`. Credentials belong in protected configuration files. Change one peer control at a time:

| Link | Positive control and exposed versus fixed comparison |
| --- | --- |
| Cluster | Establish the intended route with matching credentials and trusted certificates; confirm `/routez`, logs, and cross-server marker delivery. Repeat with wrong explicit-route credentials, an untrusted certificate, and a disallowed source network. An insufficiently protected route admits the peer; the fixed route rejects it with the matching diagnostic. |
| Gateway | Establish the intended named cluster link; confirm `/gatewayz`, logs, and marker delivery. Repeat with wrong credentials, an untrusted certificate, a disallowed network, and an unknown cluster name. Unknown-name rejection supplements authentication. |
| Leaf | Establish the intended local-account to hub-account link; confirm `/leafz`, logs, and marker delivery. Repeat with wrong credentials, an untrusted certificate, and a disallowed network. Verify that an unintended account does not receive the marker. For an outbound-only leaf, inventory the absence of an inbound leaf listener. |

If known-URL certificate checking is selected, compare a permitted peer certificate/URL with a certificate trusted by the CA but outside the approved URL set. Record the healthy link before and after negative tests.

A client-port test, TCP connection alone, or successful TLS handshake without message routing cannot substitute for these comparisons. See the [cluster](https://docs.nats.io/reference/config/cluster/), [gateway](https://docs.nats.io/reference/config/gateway/), and [leaf](https://docs.nats.io/reference/config/leafnodes/) references.

### V8. Monitoring reachability and proxy bypass (REASONED: collector, observer and proxy-bypass comparisons from the linked monitoring and hardening references; no service, observer or proxy fixtures)

**REASONED: no monitoring service, intended collector, external observer, or authenticating proxy fixture is available.**

First complete the listener inventory in V1. Run this whole block from the intended collector with its permitted target, then from the unauthorized observer with the inventoried externally reachable address. For the selected loopback binding, the collector runs on the broker host and targets `127.0.0.1`.

```bash
# REASONED: monitoring reachability; no pinned server/CLI, broker or certificate fixtures. Expected outcomes and vendor sources are recorded in this section.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MONITOR_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'provide exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the monitor host'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
  for endpoint in varz 'connz?subs=true&auth=true' routez jsz; do
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      "http://$1:8222/$endpoint"
  done
)
```

Exposed versus fixed: an anonymous external observer retrieves JSON in the exposed state; the fixed collector still retrieves the expected JSON, while the external observer cannot directly reach the backend.

Any actual HTTP response from the direct backend proves reachability, even if it is an error. For the selected loopback listener, connection refusal, commonly curl exit 7, is the expected external result, but it counts only alongside the matched collector success, correct target, and listener inventory. A stopped service or wrong target also refuses. DNS errors and post-connect timeouts are inconclusive. A firewall-drop design needs matching firewall evidence and the same positive controls; a timeout alone is insufficient.

**Conditional proxy comparison, REASONED: no proxy or identity-provider fixture is available.** Send `GET /connz?subs=true&auth=true` to the intended HTTPS proxy with a 5-second connection timeout and 20-second total bound. Require unauthenticated rejection and authenticated JSON success, using the proxy's protected credential mechanism. Then run the direct-backend block from the unauthorized network and require bypass denial. An intentionally reachable authenticating proxy is not an exposed anonymous backend.

See [monitoring endpoints](https://docs.nats.io/learn/monitoring/monitoring-endpoints) and [hardening](https://docs.nats.io/learn/deployment/hardening).

### V9. Enabled MQTT, WebSockets, and auth callout (REASONED: optional-protocol comparisons from the linked MQTT, WebSocket and auth-callout references; no clients, listeners or authentication fixture)

**REASONED: no optional-protocol clients, listeners, browser fixture, or authentication service are available. Run only the applicable comparisons.**

Use clients with protected credential inputs, a 3-second operation deadline, and a 20-second overall bound per case.

| Conditional feature | Concrete comparison |
| --- | --- |
| MQTT | Send an MQTT `CONNECT` using the scoped device credentials, then `PUBLISH` a unique marker to `devices/device-01/telemetry` and subscribe to `devices/device-01/command`. Confirm translated-subject delivery with authorized peers. Repeat without credentials, with wrong credentials, and with another device's subjects. An exposed listener admits anonymous/broad access; the fixed listener rejects it. Attempt the same device identity through the Core listener and require the connection-type restriction. |
| Operator-mode MQTT | Use the explicitly permitted bearer user JWT as the MQTT password through protected client configuration. Compare valid and invalid JWTs, account placement, and subject permissions. This tests bearer admission, not nonce-signature proof. |
| WebSockets | Perform a WSS upgrade with the approved browser `Origin`, authenticate as the scoped browser user, and request `orders.lookup` using its matching inbox prefix. Repeat with an unapproved origin while keeping credentials valid, and with invalid credentials while keeping the origin approved. An exposed origin policy permits the unwanted browser connection; the fixed policy rejects it. Separately test a non-browser client omitting `Origin`: it must still authenticate. Test direct backend access if TLS terminates at a proxy. |
| Auth callout | Connect with valid external credentials, then invalid credentials, and verify the returned account and subject grants through marker delivery and forbidden-subject attempts. Stop the authentication service in the isolated fixture and repeat admission: the fixed deployment must reject the new connection. Attempt an ordinary-user subscription to `$SYS.REQ.USER.AUTH`; it must not expose the exchange. Verify that only the narrowly listed service identity bypasses delegation. |

For callout encryption, verify that the service can process exchanges with the matching private XKey, while a wrong key fails to produce accepted authentication responses. Do not log submitted credentials or decrypted payloads.

See [MQTT authentication](https://docs.nats.io/learn/mqtt/auth-and-clustering), [WebSocket configuration](https://docs.nats.io/reference/config/websocket/), and [auth callout](https://docs.nats.io/learn/security/auth-callout).

### V10. Connection pressure and slow consumers (REASONED: bounded capacity comparisons from the linked runtime, account and request-queue references; no load client, isolated broker or diagnostics)

**REASONED: no load client, isolated broker, or matching runtime diagnostics are available.**

Use a fixture client that holds and counts actual authenticated connections, with secrets supplied through protected inputs. Bound each test run to 30 seconds and close every connection on completion.

- Hold the selected account's 128 connections, require rejection of the next, release one, and admit a replacement. Compare with an exposed higher/unbounded account budget.
- Test the server's 1024 connection limit across enough test accounts whose combined account budgets permit reaching it. The three account budgets in section 14 cannot by themselves exercise that server ceiling. Alternatively, select smaller recorded limits in an isolated fixture. Require the next-connection rejection, release/replacement success, and matching diagnostics.
- On one authenticated connection, establish 256 permitted subscriptions with distinct subscription IDs, then attempt the next. Compare subscription-limit rejection with the exposed higher/unbounded state.
- Compare a valid below-limit `PUB` with a payload over the selected 1MB limit, and a valid control line with one over 4KB. Require the relevant rejection, keeping a healthy client active.
- Open a connection and stall the required TLS handshake; separately complete TLS and stall NATS authentication. Require the configured timeout diagnostics while a normal client connects successfully.
- Establish an authorized subscriber, stop reading, and publish a finite workload sufficient to exercise pending-output or write-deadline enforcement. Compare the exposed larger/unbounded backlog with fixed slow-consumer handling, and retain a healthy subscriber that receives its marker.
- If JetStream is enabled, exercise API pressure above and below the selected request-queue budget with bounded concurrent requests, matching server diagnostics, and a healthy-client control.

These are capacity tests, not proof of a connection-attempt rate limit. A client disconnect alone is not evidence of the intended limit without matching diagnostics and a successful below-limit control.

See [runtime limits](https://docs.nats.io/reference/config), [account limits](https://docs.nats.io/reference/config/accounts/limits/), and [JetStream request queues](https://docs.nats.io/reference/config/jetstream/request_queue_limit).

### Verification scope and local work

REASONED: scope of the original authoring record and its shell-only evidence. The whole-corpus gate suite was not run for this drop-in generation. Shell checks do not demonstrate NATS configuration parsing or service behaviour.

| Check scope | Status | Procedure and prerequisites |
| --- | --- | --- |
| REASONED: service-comparison scope from the cited NATS sources and V0-V10 prerequisites; no broker fixtures. Service behaviour | REASONED from the cited NATS Server v2.14.7 and natscli v0.4.0 sources and vendor documentation; not demonstrated | On an authorized deployment pinned to NATS Server v2.14.7 and natscli v0.4.0, run V0-V10 and every applicable conditional comparison against isolated exposed and fixed states. Record server/client/tool versions, complete substituted configurations, commands or protocol requests, responses, matching server logs, effective limits, positive controls, and cleanup without secrets. Configuration inspection or successful `-t` alone does not demonstrate service behaviour. |
| REASONED: local-work scope from V0 and its cited sources; pinned tools and credential fixtures are unavailable. Native parsing and key generation | Outstanding in this environment; retained local work | Run the offline-capable checks above with the pinned tools and readable certificate, JWT, include, and credential fixtures. |

## Common mistakes

- Leaving `no_auth_user` set after testing, which quietly readmits anonymous clients.
- Exposing 8222 or `https_port` on a public interface because it "is just monitoring."
- A user with no `permissions` block and no applicable `default_permissions`, which is unrestricted within its account rather than denied.
- Treating separate usernames in `$G` as tenant isolation, or omitting `accounts` from an export that should be private.
- Assuming an empty allow list denies everything, or that a static publish deny always defeats `allow_responses`.
- Adding a plain subject grant beside a queue-specific grant, thereby admitting non-queue subscriptions.
- Reusing `_INBOX.>` across applications or forgetting the client's matching inbox prefix.
- Giving Core-only applications JetStream administrative API access, or treating a JetStream domain as an account boundary.
- Treating `max_consumers` as a total account-wide count, or reload success as proof that reduced limits became effective.
- Assuming client TLS protects peer listeners or monitoring, or that an outbound-only leaf must expose an inbound listener.
- Securing a monitoring proxy while leaving its backend directly reachable.
- Enabling MQTT, WebSockets, or auth callout without reviewing their separate identity paths and overrides.
- Leaving operator/account signing seeds or unrelated application credentials readable by the broker.
- Treating a timeout, absent plaintext marker, successful parse, or quiet subscriber as a demonstrated security control.

## Sources (checked September 2026)

- Official `nats` Docker images: the tag-to-directory map for 2.14 and 2.15 (library file pinned commit dcd3db677d8919c3a42d369bd48a6f1c234b3ae8), and at image source pinned commit 0e72748d3cb553ccdb8c2da7c75ec3b767be51a5 the bundled `nats-server.conf` (the same in every published directory), the scratch and Alpine configuration copy, `ENTRYPOINT` and `CMD`, the Alpine entrypoint, and the Nano Server and Windows Server Core `ENTRYPOINT` and `CMD` (cited for both 2.15 and 2.14), and the server release each image carries (2.15.0 and 2.14.7: each Alpine and Windows Server Core build sets `NATS_SERVER` and downloads that release, and each scratch and Nano Server build copies the binary from the matching image; each variant's lines are cited for both versions): https://github.com/docker-library/official-images/blob/dcd3db677d8919c3a42d369bd48a6f1c234b3ae8/library/nats#L6-L50, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/scratch/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/nanoserver-ltsc2022/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/scratch/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/nanoserver-ltsc2022/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/nats-server.conf, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/scratch/Dockerfile#L5-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/Dockerfile#L38-L43, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/docker-entrypoint.sh#L7-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/docker-entrypoint.sh#L7-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/nanoserver-ltsc2022/Dockerfile#L5-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/Dockerfile#L44-L48, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/Dockerfile#L44-L48, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/nanoserver-ltsc2022/Dockerfile#L5-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/scratch/Dockerfile#L5-L9, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/Dockerfile#L38-L43, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/Dockerfile#L3, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/alpine3.22/Dockerfile#L28, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/Dockerfile#L7, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/windowsservercore-ltsc2022/Dockerfile#L18, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/scratch/Dockerfile#L4, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.15.x/nanoserver-ltsc2022/Dockerfile#L4, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/Dockerfile#L3, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/alpine3.22/Dockerfile#L28, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/Dockerfile#L7, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/windowsservercore-ltsc2022/Dockerfile#L18, https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/scratch/Dockerfile#L4 and https://github.com/nats-io/nats-docker/blob/0e72748d3cb553ccdb8c2da7c75ec3b767be51a5/2.14.x/nanoserver-ltsc2022/Dockerfile#L4
- NATS Server listen defaults (pinned tag v2.15.0; the same at v2.14.7): `DEFAULT_HOST` of `0.0.0.0`, `monitor_port` read as `http_port`, the `-c` and `--config` flags, the client and monitoring host defaults, the cluster host default, and the client, monitoring and route listeners opened with Go's `tcp` listen: https://github.com/nats-io/nats-server/blob/v2.15.0/server/const.go#L85-L86, https://github.com/nats-io/nats-server/blob/v2.15.0/server/opts.go#L1292, https://github.com/nats-io/nats-server/blob/v2.15.0/server/opts.go#L6265-L6266, https://github.com/nats-io/nats-server/blob/v2.15.0/server/opts.go#L6012-L6019, https://github.com/nats-io/nats-server/blob/v2.15.0/server/opts.go#L6042-L6045, https://github.com/nats-io/nats-server/blob/v2.15.0/server/server.go#L2874-L2880, https://github.com/nats-io/nats-server/blob/v2.15.0/server/server.go#L3132-L3138, https://github.com/nats-io/nats-server/blob/v2.15.0/server/route.go#L2752-L2753 and https://github.com/nats-io/nats-server/blob/v2.15.0/server/util.go#L267-L275
- Go's wildcard `tcp` listen opening one dual-stack socket where IPv4-mapped addresses are supported (pinned tag go1.26.8, the toolchain in both versions' go.mod): https://github.com/golang/go/blob/go1.26.8/src/net/ipsock_posix.go#L134-L147
- NATS Server v2.14.7 release: https://github.com/nats-io/nats-server/releases/tag/v2.14.7
- Exact server tag commit: https://github.com/nats-io/nats-server/commit/8d8b69a8c46a46a150eabb7f312607c4d9c58faf
- Securing NATS overview: https://docs.nats.io/learn/security/
- Authentication basics, password hashes, NKeys, tokens, and anonymous admission (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/authentication-basics
- Authorization and subject permissions (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/authorization
- Operator mode, resolver setup, credentials, and signing-store handling (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/operator-mode
- Decentralized authentication and signing hierarchy (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/decentralized-auth
- Accounts and multitenancy (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/accounts-and-multitenancy
- Cross-account exports and imports (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/cross-account
- Subscription and queue permissions (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/authorization/users/permissions/subscribe/
- Bounded response permissions (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/authorization/users/permissions/allow_responses/
- Connection-type restrictions (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/authorization/users/allowed_connection_types
- Authorization timeout (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/authorization/timeout
- Encryption, TLS authentication, and JetStream key rotation (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/encryption
- TLS reference and listener applicability (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/tls/
- Monitoring endpoints and query parameters (rolling documentation, checked September 2026): https://docs.nats.io/learn/monitoring/monitoring-endpoints
- JetStream concepts (rolling documentation, checked September 2026): https://docs.nats.io/concepts/jetstream
- Runtime configuration, defaults, bindings, and system account (rolling documentation, checked September 2026): https://docs.nats.io/reference/config
- Account connection limits (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/accounts/limits/
- Server JetStream configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/
- Account JetStream limits and reload caveats (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/accounts/jetstream/
- JetStream request queue limit (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/request_queue_limit
- JetStream domain (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/domain
- JetStream encryption key (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/encryption_key
- JetStream cipher selection (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/cipher
- JetStream previous encryption key (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/jetstream/prev_encryption_key
- Cluster configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/cluster/
- Gateway configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/gateway/
- Leafnode configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/leafnodes/
- Leafnode authorization and account binding (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/leafnodes/authorization/
- Leafnode remotes and local account selection (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/leafnodes/remotes/
- JetStream across leaf nodes (rolling documentation, checked September 2026): https://docs.nats.io/learn/topologies/leaf-nodes
- MQTT configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/mqtt/
- MQTT authentication and clustering (rolling documentation, checked September 2026): https://docs.nats.io/learn/mqtt/auth-and-clustering
- WebSocket configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/websocket/
- Auth callout workflows (rolling documentation, checked September 2026): https://docs.nats.io/learn/security/auth-callout
- Auth callout configuration (rolling documentation, checked September 2026): https://docs.nats.io/reference/config/authorization/auth_callout
- Deployment hardening, non-root service identity, and sandboxing (rolling documentation, checked September 2026): https://docs.nats.io/learn/deployment/hardening
- Server v2.14.7 configuration parser and configuration-test handling: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go
- Server v2.14.7 client and response-permission enforcement: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/client.go
- Server v2.14.7 consumer-limit enforcement: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/consumer.go
- Server v2.14.7 JetStream API subjects and domain mappings: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/jetstream_api.go
- Server v2.14.7 monitoring fields and handlers: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/monitor.go
- Server v2.14.7 auth-callout response validation: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/auth_callout.go
- natscli v0.4.0 flags, contexts, inbox prefixes, domains, and environment bindings: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/nats/main.go
- natscli v0.4.0 credential-option handling: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/util.go
- natscli v0.4.0 subscription and queue flags: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/sub_command.go
