# Realtime voice and video infrastructure: LiveKit and coturn

AI voice agents run on self-hosted realtime backends that carry live media, and two of them sit at the network edge: LiveKit, a WebRTC SFU that routes participants' audio, video, and data, and coturn, a TURN/STUN server that relays media when a direct peer path cannot be found. The relay is the sharp edge. A TURN server proxies traffic on a client's behalf, so an unauthenticated or misconfigured one is an *open relay*: an attacker uses it to launder traffic, to reach services on the host's own loopback and private network, and to reflect and amplify UDP toward a victim. LiveKit's edge is different: it will not start without API keys, so the danger is not an anonymous join but a *known or weak* signing secret, which lets anyone mint a token and enter any room to eavesdrop or inject media. [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern both rely on for TLS, and [secrets.md](secrets.md) covers generating and holding the signing material. Values below are illustrative; replace them.

## LiveKit

LiveKit's own HTTP/WebSocket signaling and API listen on `7880`; ICE media uses a separate TCP mux on `7881` and, outside development mode, a UDP range of `50000` to `60000`. With no explicit `bind_addresses`, the server binds the wildcard address on every one of those, and restricting the signaling bind does not restrict the RTC sockets. The embedded TURN service is off by default and, if enabled, needs its ports set explicitly.

Authentication is by API key/secret pairs, and access tokens are HS256 JWTs that carry room grants (`roomJoin`, `room`, `canPublish`, `canSubscribe`, administrative grants such as `roomCreate`) and are signed with the secret. The critical default is that **a normal-mode server refuses to start with no keys configured** (`ValidateKeys()` returns an error), so an exposed instance is not an anonymous free-for-all. The real exposures are the ways a *usable* secret ends up known:

- **Development mode** (`--dev`) injects a hard-coded pair, `devkey` / `secret`, when the key map is empty, and binds signaling to loopback. The local quickstart selects it deliberately. Never run it on an exposed host: anyone can sign a valid admin token.
- **The upstream `config-sample.yaml` ships active `key1: secret1` / `key2: secret2` entries.** These are examples, not generated credentials; remove them from the effective key set.
- **A short secret does not block startup.** Outside development mode a secret under 32 characters only logs an error; it still runs. Treat that log as a finding, and generate a long random secret.

Because a signing secret mints any grant, guard it like a root credential, and note that omitted grants are permissive: `canPublish` and `canSubscribe` default to true, so scope tokens deliberately. Generate a real pair and keep it in a key file rather than the main config:

```yaml
# livekit.yaml: front this with a proxy for wss:// (LiveKit terminates no TLS on signaling)
development: false
port: 7880
bind_addresses: ["127.0.0.1"]
key_file: /etc/livekit/keys.yaml

rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
```

```yaml
# /etc/livekit/keys.yaml: generate the pair (e.g. `livekit-server generate-keys`); replace both
REPLACE_WITH_GENERATED_API_KEY: "REPLACE_WITH_GENERATED_RANDOM_SECRET"
```

Signaling TLS terminates at a reverse proxy or load balancer: the core server calls `Serve`, not `ServeTLS`, and there is no top-level signaling TLS flag, so front it with the [fronting-auth.md](fronting-auth.md) pattern and connect over `wss://`. A few surfaces are easy to leave open beside the main port: Prometheus metrics, when enabled, serve unauthenticated unless you set `prometheus.username`/`password`; the debug and profiling routes carry no grant check; and the embedded TURN service derives its credentials from the same API secret, so a leaked secret also undermines TURN. Webhook receivers must verify both the signing token and the SHA-256 body hash, not merely accept TLS.

Unverified until checked in your deployment: whether a Helm chart or package generator creates or overrides keys and binds, the effective bind of a distribution's sample config, and the JWT-library version your build pins.

## coturn

coturn listens on `3478` for STUN/TURN over both UDP and TCP, and on `5349` for TLS; **DTLS on `5349` has been opt-in since 4.17.0** and is off unless you set `dtls`. Relay endpoints are allocated on demand from `49152` to `65535` (`min-port`/`max-port`). The telnet CLI (`5766`), web admin (`8080`), and Prometheus (`9641`) are each disabled by default and bound to loopback when on. The default listener is *not* loopback-only: coturn enumerates addresses on every interface that is up, so bind it explicitly with `listening-ip`.

The default that matters most is authentication. **With the stock example configuration (no users, and both `lt-cred-mech` and `use-auth-secret` commented out), TURN allocation is anonymous**, which is an open relay. That is the out-of-box example, not every install (the upstream Docker image ships `lt-cred-mech` on, and defining static users implies long-term auth), so confirm the effective config rather than assuming either way. Enable one credential mode and a stable realm:

```ini
# turnserver.conf: long-term credentials
lt-cred-mech
realm=turn.example.com
user=REPLACE_WITH_USER:REPLACE_WITH_RANDOM_PASSWORD

listening-port=3478
tls-listening-port=5349
cert=/etc/coturn/fullchain.pem
pkey=/etc/coturn/private-key.pem

# Relay policy (see below); these are a starting denylist, not a complete one
allow-loopback-peers=false
no-multicast-peers
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255

cli=false
web-admin=false
```

For application-generated time-limited credentials, replace the `lt-cred-mech`/`user` lines with `use-auth-secret` and a `static-auth-secret` (plus the same `realm`); keep that shared secret in the server config, never distribute it to clients. A realm is an operational requirement for both modes, not a hard startup gate: omitting it warns rather than refuses, so set it explicitly.

Relay destination policy is the other half, and its defaults do not fully contain a relay:

- **Loopback** (`127.0.0.0/8`, `::1`) is blocked unless you set `allow-loopback-peers`; leave it off.
- **Zero, link-local (including the `169.254.169.254` metadata address), and IPv6 local scopes** are blocked by built-in checks.
- **RFC 1918 private ranges are *not* blanket-blocked.** Nothing built in stops a relay to `10/8`, `172.16/12`, or `192.168/16`; add explicit `denied-peer-ip` ranges (above) or network policy, or an authenticated user still reaches your internal network.
- **Multicast** is allowed unless `no-multicast-peers` is set.
- `allowed-peer-ip` is an exception list, not a default-deny allowlist: an address it does not name can still be permitted.

STUN Binding stays anonymous even when TURN allocation requires credentials, so closing anonymous allocation does not close reflection and amplification; `secure-stun` requests authenticated Binding, and RFC 5780 (a reflection amplifier) is off by default, so leave it off. The CLI and web admin use their own credentials, not TURN users, so disable them or set `cli-password` and keep them on loopback; do not enable `server-relay`, which drops permission checks on relayed traffic. `--no-cli` is retired in 4.18.0, so use `cli=false`.

Unverified until checked in your deployment: the default service state and effective configuration of any specific distro or container image, the build's TLS/feature availability, and real reflection/amplification factors.

## Shared exposures

- **An open TURN relay reaches your internal network and amplifies UDP.** An anonymous (or abusive authenticated) allocator originates traffic through the relay to any permitted, reachable peer, which is an SSRF-like path into your private network and a UDP amplification vector. Authentication closes anonymous allocation; RFC 1918 denial and network policy are still needed against authenticated abuse.
- **A weak or development LiveKit secret forges room admission.** A known signing secret lets an attacker choose identities and grants, so publishing, subscribing, or administering rooms all become available. Application end-to-end encryption is a separate content boundary, not a substitute for protecting the secret.
- **Plaintext signaling or relay.** Public HTTP/WS exposes signaling and bearer tokens in transit; TURN without TLS/DTLS carries its credentials in the clear. Media transport encryption is a separate layer from this outer transport.
- **STUN reflection and amplification.** Binding responses are unauthenticated regardless of TURN auth, so a spoofed source can reflect UDP toward a victim; response-enlarging features increase the factor.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor sources rather than observed, and backlog row 2.34 tracks demonstrating them against live instances in the exposed and fixed states. A redirect, a `404`, a timeout, or a TLS error is inconclusive, never proof of the fixed state; every negative check needs a working positive control.

```bash
sudo ss -tlnp    # TCP listeners: expect 7880/7881 for LiveKit and 3478/5349 for coturn only, on
sudo ss -aunp    # a private address; and no CLI 5766, web-admin 8080, or metrics 9641/6789 exposed
                 # UDP: the LiveKit 50000-60000 media range and coturn 49152-65535 relay range
                 # appear only during active calls/allocations, not at idle
```

```bash
# LiveKit: an unauthenticated signaling/validation request against the direct listener. Substitute
# the base URL inside the single quotes on the set -- line and paste the whole block so the guard runs.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_LIVEKIT_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the LiveKit base URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) : ;;
    *) echo "expected an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/rtc/validate"
)
```

`/rtc/validate` returns `401` without a valid token; a `200` only proves the token was accepted, not that a media session was established. The load-bearing LiveKit check is a key-rotation test that infrastructure alone cannot fake: mint a correctly scoped token with the old (`devkey`/`secret`, or a retired real) secret and confirm it is *accepted* on an isolated fixture, then confirm the *same token is rejected* after the deployment's key is rotated, while a token signed with the new key is accepted. An expired or wrong-room token is an invalid rotation test. Probe the metrics and debug routes from an untrusted network too; a healthy `/` does not prove they are protected.

For coturn, the discriminator is a TURN **Allocate** exchange, not an HTTP request. Send a well-formed Allocate requesting UDP relay with no credentials: an allocation containing a relayed address is an open relay, while an authentication challenge with no allocation is the fixed state, and a valid-credential allocation is the required positive control, because the initial `401` also occurs during a successful authenticated exchange. Then, authenticated, request `CreatePermission`/`ChannelBind` for an owned RFC 1918 test peer and confirm a `403` with no traffic reaching it (a plain allocation failure or timeout is not evidence of peer policy). Verify TLS separately, and require verification to be fatal so a diagnostic tool does not continue past a bad certificate:

```bash
openssl s_client -connect turn.example.com:5349 -servername turn.example.com \
  -verify_hostname turn.example.com -verify_return_error \
  -CAfile /etc/ssl/certs/ca-certificates.crt </dev/null
```

That proves the certificate and handshake only, not TURN authentication or peer policy; a local socket binding proves neither public reachability nor TLS. Never add `-k`/`--insecure` to any of these.

## Common mistakes

- Running LiveKit in development mode, or leaving the sample `key1: secret1` pairs in the key set, so a public `devkey`/`secret` mints valid admin tokens.
- Treating a short signing secret as safe because the server started: the length check only logs and does not block startup.
- Running coturn with the stock example config (no `lt-cred-mech`, no users), which relays anonymously, an open relay.
- Enabling authentication but forgetting relay policy, so an authenticated user reaches RFC 1918 hosts coturn does not block by default.
- Assuming TURN credentials protect STUN Binding, the CLI, or the web admin; each is a separate anonymous or separately-credentialed surface.
- Publishing coturn's TLS port while leaving plain UDP/TCP `3478` open, so clients still connect without transport encryption.
- Restricting LiveKit's signaling bind and assuming the RTC and embedded-TURN sockets followed; they bind independently.

## Sources (checked September 2026)

- LiveKit ports and firewall reference (`7880`, `7881`, UDP media range): https://docs.livekit.io/transport/self-hosting/ports-firewall/
- LiveKit key validation (`ValidateKeys()` errors on an empty key map; the sub-32-character secret log): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/pkg/config/config.go
- LiveKit development-mode `devkey`/`secret` injection and loopback bind: https://raw.githubusercontent.com/livekit/livekit/v1.13.7/cmd/server/main.go
- LiveKit sample config (`key1: secret1` example pairs; the embedded-TURN and metrics settings): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/config-sample.yaml
- LiveKit tokens and grants (HS256 JWT, room and admin grants, permissive defaults): https://docs.livekit.io/frontends/reference/tokens-grants/
- LiveKit self-hosting deployment (TLS terminates at a proxy; `wss://`): https://docs.livekit.io/transport/self-hosting/deployment/
- coturn example configuration (default anonymous auth, `allow-loopback-peers`, `no-multicast-peers`, `cli`, `cert`/`pkey`, `tls-listening-port`): https://raw.githubusercontent.com/coturn/coturn/4.18.0/examples/etc/turnserver.conf
- coturn option reference (credential modes, `use-auth-secret`, `secure-stun`, `server-relay`, CLI/web-admin, relay port range): https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnserver
- coturn 4.17.0 release notes (DTLS listeners now opt-in, started only with `--dtls`): https://github.com/coturn/coturn/releases/tag/4.17.0
- coturn 4.18.0 release notes (`--no-cli` retired): https://github.com/coturn/coturn/releases/tag/4.18.0
- coturn peer-address classification (loopback, link-local, RFC 1918 handling): https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/server/ns_turn_server.c
- curl manual (the `exitcode` and `errormsg` write-out variables in the Verify probe, both added in curl 7.75.0): https://curl.se/docs/manpage.html
