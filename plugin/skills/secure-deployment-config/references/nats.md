# NATS and JetStream: authentication, TLS, and the monitoring port

NATS accepts client connections on 4222 with no authentication configured by default. A separately enabled HTTP monitoring endpoint, conventionally 8222, reveals connection metadata, subscription subjects, and message/byte counters without a login of its own. Both need explicit configuration. JetStream, the persistence layer for streams and consumers, runs in the same server process: it adds no listening port of its own, and its state surfaces through the same monitoring endpoint at `/jsz`.

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

The HTTP monitoring endpoint is off unless configured, for example with `http_port: 8222` or the server's `-m 8222` option. `https_port` serves the same data over TLS. It answers `/varz`, `/connz`, `/routez`, and, with JetStream enabled, `/jsz`.

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

Service behaviour has **not** been demonstrated here. `nats-server`, `nats`, `nk`, `nsc`, Docker, and Podman are unavailable on the authoring environment's `PATH`; no live broker, certificate fixtures, authentication service, or external peer environment was supplied. The filesystem restrictions prohibit provisioning binaries and writable credential fixtures. The live comparisons below are **REASONED**, and remain in `NATS-LIVE-1`.

Run exposed-state comparisons only in an authorized isolated fixture. Keep the target, identity, payload, and observation window matched while changing the control under test. Record diagnostics and positive controls without secrets. DNS failures, generic timeouts, and local fixture errors are inconclusive.

### V0. Offline checks and their limits

**Demonstrated here:** the five fenced Bash fragments below passed `bash -n` with Bash 5.3.9 and ShellCheck 0.11.0. Guard-only execution rejected 145 invalid input cases and allowed five substituted controls to reach a local marker. Those cases included empty arguments, original and embedded placeholders, angle brackets, `example.com`, wrong argument counts, and missing setup with unrelated caller arguments. No network command ran. This establishes bounded shell and guard evidence, not CLI semantics or general bypass resistance.

The prior guide's reported 14 invalid guard cases and two positive controls concerned its earlier fragments; they are not evidence that the replacement service checks ran.

**Offline-capable, not demonstrated here: native parsing.** With the pinned server and readable certificate, JWT, and include fixtures, run `timeout 10s nats-server -t -c selected.conf`. Repeat for every complete conditional configuration actually selected. Pair each valid fixture with a deliberately malformed configuration or unknown-field negative control. Successful parsing does not establish reachability, authorization, or secure placeholder replacement. See [v2.14.7 configuration-test handling](https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go).

**Offline-capable, not demonstrated here: credential generation.** The NKey commands in section 1 and operator/account/user generation require installed pinned tools and a private writable store. Generation and local inspection need no broker; publication to a resolver and broker acceptance do.

**Separate deployment-file check required:** scan the selected configuration, every included file, and referenced secret inputs for unresolved `REPLACE_WITH_` values and documentation addresses. Inspect generated key/JWT types and references with the appropriate tooling. A password such as `REPLACE_WITH_LONG_RANDOM_PASSWORD` can be syntactically valid, so `-t` is not a placeholder validator. An absence of placeholder text does not establish password strength or key ownership.

### V1. Running identity, effective configuration, and listeners

**REASONED: no running NATS service, service manager fixture, or deployment network namespace is available.**

On the deployment host, run bounded inventory commands such as `timeout 10s ss -tlnp`, with sufficient privilege to identify owners. Read the whole listener inventory, including IPv6. For containers, inspect both the broker's network namespace and host-side published ports.

Inspect the actual process/service identity, loaded configuration path, startup arguments, startup logs, and effective file access. Compare them with sections 6 and 13. Inspect effective limits through the allowed monitoring path and JetStream account information, rather than assuming package defaults.

Exposed versus fixed: root execution, broadly readable secrets, unintended writable paths, and public listeners become the dedicated service identity, necessary file access, and intended bindings. Offline file inspection cannot establish what the running process actually experiences.

Inventory 4222, 8222, and every enabled peer or protocol listener, including 6222, 7422, 7222, MQTT, and WebSockets. Use the actual configured ports. See [hardening](https://docs.nats.io/learn/deployment/hardening) and [configuration](https://docs.nats.io/reference/config).

### V2. Authentication, TLS, and out-of-scope subjects

**REASONED: no pinned CLI/server, trusted client/server certificates, or broker logs are available.**

The CLI reads saved contexts and environment settings before defaults. Each block clears inherited `NATS_*` settings and uses `--no-context`. This prevents a supposedly anonymous check from silently inheriting a token, user, seed, credentials file, or proxy setting. A fully clean `env -i` launch is another way to isolate ambient settings, but required credentials must still be supplied deliberately.

Paste the whole subshell after substituting all four values. These probes accept a DNS hostname or IPv4 address, without a scheme, port, or embedded credentials. TLS paths and the username are exported inside the guarded subshell. The password is read from the terminal and never exported or passed as a command argument: natscli v0.4.0 offers no stdin input for it and binds `--password` to `NATS_PASSWORD`, so each `nats` command that needs it receives it as a one-command `NATS_PASSWORD="$pw"` prefix assignment. That moves the password out of argv, not out of reach: it can remain readable through `/proc/<pid>/environ` by the same user and by root while that `nats` command, or the `timeout` that runs it, is running. Environment secrets still require a trusted local execution account.

The first publish is the allowed control. The subsequent operations deliberately test missing credentials, a wrong password, a missing client certificate, and forbidden publish/subscribe subjects. Inspect each command's diagnostics; the block's final exit status is not a combined verdict.

```bash
(
  set +x +a
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!A-Za-z0-9.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
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

### V3. Actual delivery, queue restrictions, and bounded replies

**REASONED: no broker, pinned CLI, two authenticated clients, or response-test client is available.**

A successful publish message or a quiet subscriber is insufficient proof of delivery. In a quiet fixture, start terminal 1, wait for subscription establishment, then run terminal 2 while terminal 1 is still active. The consumer must print the exact marker from terminal 2.

Terminal 1 is self-contained and reads its password inside the guarded subshell. Piping a password to `nats sub` does not configure authentication; in CLI v0.4.0, a username without a password is treated as a token.

```bash
(
  set +x +a
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CONSUMER_CERT_FILE' 'REPLACE_WITH_CONSUMER_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!A-Za-z0-9.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
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
(
  set +x +a
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'provide exactly 4 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the host'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the certificate path'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the key path'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the CA path'; exit 2 ;; esac
  case "$1" in *[!A-Za-z0-9.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
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
  marker="marker-$(date +%s%N)"
  printf 'Expected delivery: %s\n' "$marker"
  NATS_PASSWORD="$pw" timeout 10s nats --no-context --server "$srv" --timeout 3s \
    --inbox-prefix _INBOX.order-svc pub orders.created "$marker"
)
```

For queue comparisons, rerun the complete consumer block with the `order-worker` identity, its password and certificate fixtures, and replace the final subscription arguments with `sub orders.lookup --queue order-workers --count 1`. Publish a unique marker to `orders.lookup` using the complete publisher block. Then repeat with `--queue other-workers` and with no queue option. The exposed broad subscription grant accepts these forms; the fixed worker must receive through `order-workers` and reject the other forms. Test both acceptance and actual marker delivery. Do not grant the worker a bare `orders.lookup` permission to make a failing test pass.

The following self-contained request block is also used by V4 and V5. Its last three inputs are identity, subject, and JSON body. Keep subjects such as `$SYS.REQ.SERVER.PING` and `$JS.API.INFO` single-quoted on the `set --` line. The inbox prefix matches the selected identity.

```bash
(
  set +x +a
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
  case "$1" in *[!A-Za-z0-9.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
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

### V4. Accounts, approved sharing, and system requests

**REASONED: no multi-account broker, system credential, or concurrent client fixture is available.**

Use the complete consumer block separately as `order-consumer` and `analytics-reader`, with their own credentials and TLS fixtures, but raise the ORDERS consumer's final subscription to `--count 2` so it stays subscribed across both markers below: in natscli v0.4.0 a subscriber unsubscribes and exits as soon as it reaches its `--count`, so a `--count 1` ORDERS consumer would exit after the first marker and never observe the second. Keep `analytics-reader` at `--count 1`, since it should receive only the shipped marker. Publish an `orders.created` marker from `order-svc`.

Exposed versus fixed: identities placed together in `$G` can receive the same allowed subject. In the selected fixed configuration, the ORDERS consumer receives `orders.created`, while the ANALYTICS subscriber does not. Then publish a fresh `orders.shipped` marker: both must receive it through the approved export/import. The shipped-message positive control must use the same ANALYTICS subscription setup as the isolation check; silence alone is inconclusive.

For an administrative comparison, use the request block with `sys-admin`, subject `$SYS.REQ.SERVER.PING`, and body `{}`. Require a system response. Repeat with `order-svc` and its own credentials and inbox prefix: require the corresponding publish-permission rejection. An exposed application identity with administrative account membership and grants can receive the administrative response; the fixed tenant identity cannot.

If validating private-export restrictions, add an isolated third test account with a matching import. An unrestricted export permits that sharing; `accounts: [ANALYTICS]` must prevent it. Confirm successful sharing to ANALYTICS in the same run.

See [accounts](https://docs.nats.io/learn/security/accounts-and-multitenancy) and [cross-account sharing](https://docs.nats.io/learn/security/cross-account).

### V5. JetStream authority and effective limits

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

### V6. Encryption and recovery

**REASONED: no JetStream runtime, disposable encrypted stores, recovery keys, or writable fixtures are available. Conditional on encryption being selected.**

Use separate disposable unencrypted and encrypted stores. Create `SC_TEST`, publish a unique marker to `orders.test`, and retrieve it through `$JS.API.STREAM.MSG.GET.SC_TEST` with `{"seq":1}` using the guarded request block and provisioning identity.

Stop the fixture before inspecting copied persistence files. Compare the unencrypted and encrypted stores, then restart the encrypted copy with the correct key and retrieve the same marker. Repeat recovery from copies with a missing and a wrong key; require that the original stored data cannot be recovered under those conditions, with matching diagnostics. Do not mistake an empty newly initialized store for recovery.

Test the documented `prev_encryption_key` transition, restart, and subsequent recovery with the new key, including the documented removal of the previous key after migration. Bound each startup/recovery attempt to 30 seconds and use copies so failed tests do not destroy the sole recoverable data.

Exposed versus fixed: a copied plaintext store discloses data; the encrypted store requires the appropriate key and remains recoverable through the tested procedure. Absence of a plaintext marker alone proves neither complete encryption coverage nor recoverability.

See [encryption and rotation](https://docs.nats.io/learn/security/encryption) and [previous-key configuration](https://docs.nats.io/reference/config/jetstream/prev_encryption_key).

### V7. Actual cluster, gateway, and leaf peers

**REASONED: no peer servers, peer certificate fixtures, or allowed/disallowed peer networks are available. Conditional on each enabled link.**

Use actual pinned servers and complete peer configurations, with bounded fixture runs such as `timeout 30s nats-server -c peer-test.conf`. Credentials belong in protected configuration files. Change one peer control at a time:

| Link | Positive control and exposed versus fixed comparison |
| --- | --- |
| Cluster | Establish the intended route with matching credentials and trusted certificates; confirm `/routez`, logs, and cross-server marker delivery. Repeat with wrong explicit-route credentials, an untrusted certificate, and a disallowed source network. An insufficiently protected route admits the peer; the fixed route rejects it with the matching diagnostic. |
| Gateway | Establish the intended named cluster link; confirm `/gatewayz`, logs, and marker delivery. Repeat with wrong credentials, an untrusted certificate, a disallowed network, and an unknown cluster name. Unknown-name rejection supplements authentication. |
| Leaf | Establish the intended local-account to hub-account link; confirm `/leafz`, logs, and marker delivery. Repeat with wrong credentials, an untrusted certificate, and a disallowed network. Verify that an unintended account does not receive the marker. For an outbound-only leaf, inventory the absence of an inbound leaf listener. |

If known-URL certificate checking is selected, compare a permitted peer certificate/URL with a certificate trusted by the CA but outside the approved URL set. Record the healthy link before and after negative tests.

A client-port test, TCP connection alone, or successful TLS handshake without message routing cannot substitute for these comparisons. See the [cluster](https://docs.nats.io/reference/config/cluster/), [gateway](https://docs.nats.io/reference/config/gateway/), and [leaf](https://docs.nats.io/reference/config/leafnodes/) references.

### V8. Monitoring reachability and proxy bypass

**REASONED: no monitoring service, intended collector, external observer, or authenticating proxy fixture is available.**

First complete the listener inventory in V1. Run this whole block from the intended collector with its permitted target, then from the unauthorized observer with the inventoried externally reachable address. For the selected loopback binding, the collector runs on the broker host and targets `127.0.0.1`.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MONITOR_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'provide exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*) echo 'substitute the monitor host'; exit 2 ;; esac
  case "$1" in *[!A-Za-z0-9.-]*|-*) echo 'use a DNS hostname or IPv4 address only'; exit 2 ;; esac
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

### V9. Enabled MQTT, WebSockets, and auth callout

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

### V10. Connection pressure and slow consumers

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

### Demonstration backlog

The whole-corpus gate suite was not run for this drop-in generation. Shell checks do not demonstrate NATS configuration parsing or service behaviour.

| ID | Status | Closure requirement |
| --- | --- | --- |
| NATS-LIVE-1 | OPEN: service behaviour REASONED; native parsing and key generation also outstanding in this environment | On an authorized deployment pinned to NATS Server v2.14.7 and natscli v0.4.0, run V0-V10 and every applicable conditional comparison against isolated exposed and fixed states. Record server/client/tool versions, complete substituted configurations, commands or protocol requests, responses, matching server logs, effective limits, positive controls, and cleanup without secrets. Cross-reference or replace existing demonstration row 1.81 so the original checks remain tracked. Configuration inspection or successful `-t` alone cannot close this row. |

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

- NATS Server v2.14.7 release: https://github.com/nats-io/nats-server/releases/tag/v2.14.7
- Exact server tag commit: https://github.com/nats-io/nats-server/commit/8d8b69a8c46a46a150eabb7f312607c4d9c58faf
- Securing NATS overview: https://docs.nats.io/learn/security/
- Authentication basics, password hashes, NKeys, tokens, and anonymous admission: https://docs.nats.io/learn/security/authentication-basics
- Authorization and subject permissions: https://docs.nats.io/learn/security/authorization
- Operator mode, resolver setup, credentials, and signing-store handling: https://docs.nats.io/learn/security/operator-mode
- Decentralized authentication and signing hierarchy: https://docs.nats.io/learn/security/decentralized-auth
- Accounts and multitenancy: https://docs.nats.io/learn/security/accounts-and-multitenancy
- Cross-account exports and imports: https://docs.nats.io/learn/security/cross-account
- Subscription and queue permissions: https://docs.nats.io/reference/config/authorization/users/permissions/subscribe/
- Bounded response permissions: https://docs.nats.io/reference/config/authorization/users/permissions/allow_responses/
- Connection-type restrictions: https://docs.nats.io/reference/config/authorization/users/allowed_connection_types
- Authorization timeout: https://docs.nats.io/reference/config/authorization/timeout
- Encryption, TLS authentication, and JetStream key rotation: https://docs.nats.io/learn/security/encryption
- TLS reference and listener applicability: https://docs.nats.io/reference/config/tls/
- Monitoring endpoints and query parameters: https://docs.nats.io/learn/monitoring/monitoring-endpoints
- JetStream concepts: https://docs.nats.io/concepts/jetstream
- Runtime configuration, defaults, bindings, and system account: https://docs.nats.io/reference/config
- Account connection limits: https://docs.nats.io/reference/config/accounts/limits/
- Server JetStream configuration: https://docs.nats.io/reference/config/jetstream/
- Account JetStream limits and reload caveats: https://docs.nats.io/reference/config/accounts/jetstream/
- JetStream request queue limit: https://docs.nats.io/reference/config/jetstream/request_queue_limit
- JetStream domain: https://docs.nats.io/reference/config/jetstream/domain
- JetStream encryption key: https://docs.nats.io/reference/config/jetstream/encryption_key
- JetStream cipher selection: https://docs.nats.io/reference/config/jetstream/cipher
- JetStream previous encryption key: https://docs.nats.io/reference/config/jetstream/prev_encryption_key
- Cluster configuration: https://docs.nats.io/reference/config/cluster/
- Gateway configuration: https://docs.nats.io/reference/config/gateway/
- Leafnode configuration: https://docs.nats.io/reference/config/leafnodes/
- Leafnode authorization and account binding: https://docs.nats.io/reference/config/leafnodes/authorization/
- Leafnode remotes and local account selection: https://docs.nats.io/reference/config/leafnodes/remotes/
- JetStream across leaf nodes: https://docs.nats.io/learn/topologies/leaf-nodes
- MQTT configuration: https://docs.nats.io/reference/config/mqtt/
- MQTT authentication and clustering: https://docs.nats.io/learn/mqtt/auth-and-clustering
- WebSocket configuration: https://docs.nats.io/reference/config/websocket/
- Auth callout workflows: https://docs.nats.io/learn/security/auth-callout
- Auth callout configuration: https://docs.nats.io/reference/config/authorization/auth_callout
- Deployment hardening, non-root service identity, and sandboxing: https://docs.nats.io/learn/deployment/hardening
- Server v2.14.7 configuration parser and configuration-test handling: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/opts.go
- Server v2.14.7 client and response-permission enforcement: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/client.go
- Server v2.14.7 consumer-limit enforcement: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/consumer.go
- Server v2.14.7 JetStream API subjects and domain mappings: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/jetstream_api.go
- Server v2.14.7 monitoring fields and handlers: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/monitor.go
- Server v2.14.7 auth-callout response validation: https://raw.githubusercontent.com/nats-io/nats-server/v2.14.7/server/auth_callout.go
- natscli v0.4.0 flags, contexts, inbox prefixes, domains, and environment bindings: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/nats/main.go
- natscli v0.4.0 credential-option handling: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/util.go
- natscli v0.4.0 subscription and queue flags: https://raw.githubusercontent.com/nats-io/natscli/v0.4.0/cli/sub_command.go
