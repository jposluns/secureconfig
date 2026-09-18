# NATS and JetStream: authentication, TLS, and the monitoring port

NATS accepts client connections on 4222 with no authentication configured by default, and a separately enabled HTTP monitoring endpoint (conventionally 8222) that reveals connected clients, subjects, and traffic with no login of its own. Both need explicit configuration. JetStream (the persistence layer for streams and consumers) is a feature of the same server process: it adds no listening port of its own, and its state surfaces through the same monitoring endpoint (`/jsz`) rather than a dedicated one.

## 1. Require authentication

Inside an `authorization { }` block in the server config, pick one mechanism: a shared token, per-user password, or NKEYS (public-key identity, no password on the wire):

```
authorization {
  users: [
    { user: app, password: "REPLACE_WITH_LONG_RANDOM_PASSWORD" }
    { nkey: UAPZQH4MNJCOVEJFERB3NFSIROQ5RE7CGBEPKAZSB6QB7IQHBKXHZPVP }
  ]
}
```

Decentralized JWT-based auth is documented separately, and its trust hierarchy has two levels: the operator (or an operator signing key) signs account JWTs, and each account (or its signing keys) signs its own user JWTs, so accounts and users are not both signed by the operator. NKey-backed users additionally prove possession of their seed by signing the server's nonce. Do not set `no_auth_user`, which names a user that unauthenticated connections are admitted as, unless an anonymous path is deliberate; it is easy to leave in place after testing and forget it grants access.

The examples above put every user in the shared default account (`$G`), and different usernames alone are not tenant isolation. For real separation, define distinct `accounts` (or operator-managed accounts), each with its own subject space, and share subjects only through reviewed exports and imports. Keep application identities out of the system account (`system_account`, default `$SYS`): its credentials are administrative, reaching server monitoring and management rather than ordinary traffic, so protect them as such.

## 2. Scope what each user can do

A user with no `permissions` block, and no applicable `authorization.default_permissions`, is unrestricted within its account's subject space (explicit user permissions replace the defaults rather than merging with them). Give each identity subject-level allow lists so a compromised credential cannot publish or subscribe everywhere:

```
authorization {
  users: [
    {
      user: order-svc
      password: "REPLACE_WITH_LONG_RANDOM_PASSWORD"
      permissions: {
        publish:   { allow: ["orders.>"] }
        # Use a service-specific inbox prefix, not _INBOX.>, which would allow subscribing to every reply
        # subject in the shared account; set the client's inbox prefix (nats CLI --inbox-prefix) to match.
        subscribe: { allow: ["_INBOX.order-svc.>"] }
      }
    }
  ]
}
```

`publish.allow` and `subscribe.allow` are independent: a publish allow list restricts only publishing and a subscribe allow list only subscribing, so restrict both explicitly. Within either operation, once a NONEMPTY `allow` list is present every subject not on it is denied; an empty `allow` list imposes no restriction, so write an explicit `deny` to lock an operation down. A matching `deny` entry overrides `allow`.

## 3. Enable TLS

```
tls {
  cert_file: "/etc/nats/certs/server-cert.pem"
  key_file:  "/etc/nats/certs/server-key.pem"
  ca_file:   "/etc/nats/certs/ca.pem"
  verify: true
}
```

Certificates per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md). `verify: true` requires and verifies a client certificate against `ca_file` (mutual TLS). `verify_and_map: true` does the same and also derives the connecting user's identity from the certificate (email, DNS, or URI SANs, or the distinguished name); use one or the other, not both.

## 4. Keep the monitoring port private

The HTTP monitoring endpoint is off unless configured (`http_port: 8222` in the config file, or `-m 8222` on the command line; `https_port` serves the same data over TLS). It answers `/varz`, `/connz`, `/routez`, and, with JetStream enabled, `/jsz`, as JSON, and anyone who can reach `:8222` can read `/connz` and enumerate your users, subjects, and traffic. Bind it privately with `http: "127.0.0.1:8222"` (or a specific private interface) rather than a bare `http_port`, or place it behind an authenticating proxy; do not publish it. `https_port` encrypts the same data but does not authenticate it, and the client `verify`/`verify_and_map` settings do not apply to the monitoring endpoint.

## 5. Cluster, leafnode, and gateway routes

If you enable clustering, leafnodes, or gateways, each is a SEPARATE listener with its own authentication and TLS that the client `authorization` and top-level `tls` above do not cover, and each defaults its host to `0.0.0.0`. Restrict every one you enable to its intended peers and give it its own credentials and TLS:

- Cluster routes (port `6222`): configure `cluster.tls` and `cluster.authorization` (route authentication uses a username/password, not client-style `users`/`token`); explicitly configured route URLs carry their own credentials.
- Leafnodes (accepted on `7422`): configure `leafnodes.authorization` and `leafnodes.tls`, and bind each accepted leaf to its intended account; an outbound remote's `account`, `credentials`, and `tls` are configured separately.
- Gateways (port `7222`): configure `gateway.tls` and gateway authentication (username/password, not client-style), and supply credentials for each configured remote gateway.

A successful test on the client port `4222` proves nothing about these listeners; test each one independently.

## 6. Resource limits and process privilege

Set `max_connections` and `max_payload` deliberately for the workload; at the time of writing the defaults are 65536 client connections and a 1 MiB payload, and these are capacity limits, not authentication. Run `nats-server` under a dedicated non-root service identity with access only to its config, credentials, TLS private keys, and JetStream storage. For same-host clients, bind `host: "127.0.0.1"` on `port: 4222`; otherwise choose a specific private interface rather than the `0.0.0.0` default.

## Verify

The `nats` CLI reads a saved context and environment variables (`NATS_URL`, `NATS_USER`, `NATS_PASSWORD`, and similar) before falling back to any default, so a credential-free test has to neutralize both or it can silently inherit credentials from whatever context happens to be active.

```bash
# REASONED, not demonstrated here: no NATS runtime in the authoring environment; backlog row 1.81 tracks
# running it live. A DNS, connection, or TLS-validation error is inconclusive for NATS auth, never a pass.
# Substitute the values inside the single quotes on each `set --` line and paste each whole subshell.
ss -tlnp   # inventory: 4222 as intended; 8222 and any route ports (6222/7422/7222) loopback or private only
(
  set +x
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NATS_HOST' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'the set -- line needs exactly 3 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the host; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute the client cert file; not probing'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*) echo 'substitute the client key file; not probing'; exit 2 ;; esac
  srv="nats://$1:4222"; ca=/etc/nats/certs/ca.pem
  # Negatives need no password, so run them in a fully clean environment (env -i). This config is verify:true,
  # which requires BOTH a client certificate and a password; test each requirement:
  # (a) valid cert, no password -> password enforced (expect an authentication rejection):
  env -i PATH="$PATH" nats --no-context --server "$srv" --tlsca "$ca" --tlscert "$2" --tlskey "$3" pub orders.created hi
  # (b) no client certificate -> mTLS enforced (expect a TLS rejection); this is also the anonymous-access
  #     check. With verify_and_map instead, a mapped certificate is the positive control and no or an unmapped
  #     certificate is the negative:
  env -i PATH="$PATH" nats --no-context --server "$srv" --tlsca "$ca" pub orders.created hi
  # Positive controls: strip ambient NATS_* settings (so no NATS_TOKEN/NATS_SOCKS_PROXY/etc. leaks in), then
  # keep the password in the ENVIRONMENT, never argv:
  for v in ${!NATS_@}; do unset "$v" 2>/dev/null || { echo "cannot clear ambient $v (readonly?); not probing"; exit 2; }; done
  # (clears every NATS_* the shell inherited - NATS_TOKEN, NATS_SOCKS_PROXY, NATS_TIMEOUT, NATS_COLOR, ... -
  #  and stops rather than probe if a readonly one cannot be cleared)
  IFS= read -r -s -p 'order-svc password: ' pw < /dev/tty || { echo 'password input failed; not probing'; exit 2; }
  echo
  [ -n "$pw" ] || { echo 'supply a nonempty password; not probing'; exit 2; }
  export NATS_USER=order-svc NATS_PASSWORD="$pw" || { echo 'could not export credentials; not probing'; exit 2; }
  { [ "${NATS_USER-}" = order-svc ] && [ "${NATS_PASSWORD-}" = "$pw" ]; } || { echo 'credentials not set as intended (readonly?); not probing'; exit 2; }
  tlsc=(--tlsca "$ca" --tlscert "$2" --tlskey "$3")
  nats --no-context --server "$srv" "${tlsc[@]}" pub orders.created hi                  # allowed publish: succeeds
  nats --no-context --server "$srv" "${tlsc[@]}" pub billing.charge hi                  # publish outside the allow list: a permissions error
  timeout 6s nats --no-context --server "$srv" "${tlsc[@]}" sub 'billing.>' --count 1   # subscribe outside the allow list: a permissions error; a timeout is inconclusive, not a pass
)
# A SUCCESSFUL subscription is reasoned (row 1.81) and needs a second identity, because order-svc can publish
# orders.> but only subscribe _INBOX.order-svc.>. With a consumer identity allowed to subscribe orders.>, prove
# delivery of a unique marker (a quiet subscriber or a timeout is not proof):
#   # shell 1 - authorized consumer, bounded (password on stdin, not argv):
#   printf '%s' "$CONSUMER_PW" | timeout 6s env -i PATH="$PATH" NATS_USER=REPLACE_WITH_CONSUMER nats --no-context \
#     --server "nats://REPLACE_WITH_NATS_HOST:4222" --tlsca /etc/nats/certs/ca.pem \
#     --tlscert REPLACE_WITH_CONSUMER_CERT --tlskey REPLACE_WITH_CONSUMER_KEY sub 'orders.>' --count 1
#   # shell 2 - order-svc publishes the marker (credentials exactly as in the positive control above):
#   nats --no-context --server "nats://REPLACE_WITH_NATS_HOST:4222" "${tlsc[@]}" pub orders.created "marker-$(date +%s)"
# The consumer must print that marker; if it does not, the result is inconclusive.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MONITOR_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the monitor host; not probing'; exit 2 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8222/connz?subs=true&auth=true"
)
# From outside, ANY http= status means 8222 is reachable (a finding). Only a connection FAILURE (curl exit 7,
# refused) is the intended isolation result; a post-connect timeout is inconclusive, not a pass.
```

## Common mistakes

- Leaving `no_auth_user` set after testing, which quietly readmits anonymous clients.
- Exposing 8222 (or `https_port`) on a public interface because it "is just monitoring."
- A user with no `permissions` block and no applicable `default_permissions`, which is unrestricted within its account rather than denied.

## Sources (checked September 2026)

- Securing NATS overview: https://docs.nats.io/learn/security/
- Authentication basics (token, user/password, nkeys, no_auth_user): https://docs.nats.io/learn/security/authentication-basics
- Authorization (subject permissions, allow/deny): https://docs.nats.io/learn/security/authorization
- Encryption and TLS (tls block, and TLS authentication with verify vs verify_and_map; NATS merged its
  mutual-TLS page into this one): https://docs.nats.io/learn/security/encryption
- Monitoring (http_port/https_port, /varz, /connz, /routez, /jsz): https://docs.nats.io/learn/monitoring/monitoring-endpoints
- JetStream concepts: https://docs.nats.io/concepts/jetstream
- Configuration reference (`system_account` default `$SYS`, `max_connections` 64K, `max_payload` 1MB, client `host`/`port` defaults): https://docs.nats.io/reference/config
- Cluster configuration (route port 6222, `cluster.tls`, `cluster.authorization`): https://docs.nats.io/reference/config/cluster
- Leafnode configuration (port 7422, `leafnodes.authorization`/`.tls`, remotes): https://docs.nats.io/reference/config/leafnodes
- Gateway configuration (port 7222, `gateway.tls`, gateway authorization): https://docs.nats.io/reference/config/gateway/
- Accounts and multitenancy (`$G`, `$SYS`, accounts, exports/imports): https://docs.nats.io/learn/security/accounts-and-multitenancy
- Deployment hardening (non-root, sandboxing): https://docs.nats.io/learn/deployment/hardening
- Decentralized authentication (operator-signs-account, account-signs-user JWT hierarchy): https://docs.nats.io/learn/security/decentralized-auth
- natscli flag and context definitions (`--no-context`, `--inbox-prefix`, and the `NATS_*` environment bindings): https://github.com/nats-io/natscli/blob/main/nats/main.go
- nats-server service unit (`User=nats`/`Group=nats` non-root execution): https://github.com/nats-io/nats-server/blob/main/util/nats-server.service
