# Realtime voice and video infrastructure: LiveKit and coturn

AI voice agents run on self-hosted realtime backends that carry live media, and two of them sit at the network edge: LiveKit, a WebRTC SFU that routes participants' audio, video, and data, and coturn, a TURN/STUN server that relays media when a direct peer path cannot be found. The relay is the sharp edge. A TURN server proxies traffic on a client's behalf, so an unauthenticated or misconfigured one is an *open relay*: an attacker uses it to launder traffic, to reach services on the host's own loopback and private network, and to reflect and amplify UDP toward a victim. LiveKit's edge is different: it will not start without API keys, so the danger is not an anonymous join but a *known or weak* signing secret, which lets anyone mint a token and enter any room to eavesdrop or inject media. [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern both rely on for TLS, and [secrets.md](secrets.md) covers generating and holding the signing material. Values below are illustrative; replace them.

## LiveKit

LiveKit's HTTP/WebSocket signaling and API listen on `7880`, and ICE media uses a separate TCP mux on `7881`; outside development mode the UDP media sockets are allocated from a range of `50000` to `60000` (development mode instead uses a single UDP mux port, `7882`). With no explicit `bind_addresses`, the signaling and RTC TCP listeners bind the wildcard address, and the UDP media sockets bind each eligible interface address; restricting the signaling bind does not restrict the RTC sockets, which is why a relay or media port can be reachable while signaling is on loopback. The embedded TURN service is off by default and, if enabled, needs its ports set explicitly.

Authentication is by API key/secret pairs, and access tokens are HS256 JWTs that carry room grants (`roomJoin`, `room`, `canPublish`, `canSubscribe`, administrative grants such as `roomCreate`) and are signed with the secret. The critical default is that **a normal-mode server refuses to start with no keys configured** (`ValidateKeys()` returns an error), so an exposed instance is not an anonymous free-for-all. The real exposures are the ways a *usable* secret ends up known:

- **Development mode** (`--dev`) injects a hard-coded pair, `devkey` / `secret`, when the key map is empty, and (when no bind is supplied) defaults signaling to loopback. The local quickstart selects it deliberately. Never run it on an exposed host: anyone can sign a valid admin token.
- **The upstream `config-sample.yaml` ships uncommented `key1: secret1` and `key2: secret2` entries.** These are examples, not generated credentials; remove every one from the effective key set.
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

LiveKit refuses a key file that is readable by others, so the server will not start if the file is group- or world-readable; create it `0600`, owned by the service account. Signaling TLS terminates at a reverse proxy or load balancer: the core server calls `Serve`, not `ServeTLS`, and there is no top-level signaling TLS flag, so front it with the [fronting-auth.md](fronting-auth.md) pattern and connect over `wss://`. A few surfaces are easy to leave open beside the main port: Prometheus metrics, when enabled, serve unauthenticated unless you set `prometheus.username`/`password`; the debug and profiling routes (`/debug/pprof/`, `/debug/goroutine`, `/debug/rooms`) carry no grant check and, with `debug_handler.port` set, listen on their own port; and the embedded TURN service derives its credentials from the same API secret, so a leaked secret also undermines TURN. Webhook receivers must verify both the signing token and the SHA-256 body hash, not merely accept TLS.

Unverified until checked in your deployment: whether a Helm chart or package generator creates or overrides keys and binds, the effective bind of a distribution's sample config, and the JWT-library version your build pins.

## coturn

coturn listens on `3478` for STUN/TURN over both UDP and TCP, and on `5349` for TLS; **DTLS on `5349` has been opt-in since 4.17.0** and is off unless you set `dtls`. Relay endpoints are allocated on demand from `49152` to `65535` (`min-port`/`max-port`). Three side surfaces are each off until enabled: the telnet CLI (`5766`) and web admin (`8080`) bind loopback when on, but **Prometheus (`9641`) binds a wildcard address when enabled and serves metrics with no authentication**; pin it with `prometheus-address=127.0.0.1` if you use it. The default listener is *not* loopback-only: coturn enumerates addresses on every interface that is up.

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

# Relay policy: a starting denylist, not a complete one. Deny the metadata address and every
# private range explicitly; do not rely on coturn's built-in scope checks alone across versions.
allow-loopback-peers=false
no-multicast-peers
denied-peer-ip=169.254.0.0-169.254.255.255
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255
denied-peer-ip=fc00::-fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
denied-peer-ip=fe80::-febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff

cli=false
web-admin=false
```

For application-generated time-limited credentials, replace the `lt-cred-mech`/`user` lines with `use-auth-secret` and a `static-auth-secret` (plus the same `realm`); keep that shared secret in the server config, never distribute it to clients. A realm is an operational requirement for both modes, not a hard startup gate: omitting it warns rather than refuses, so set it explicitly.

Two properties of that config are worth stating plainly. First, **enabling TLS is not the same as requiring it**: coturn autodetects protocols across ports and still accepts plaintext STUN/TURN on `3478` (and even on the TLS-numbered port). Opening `5349` proves TLS is *available*, not that encryption is *mandatory*. To require encrypted client transport, drop the plaintext client listeners with `no-tcp` and `no-udp`, keeping TLS; because that removes the plain-UDP path, enable `dtls` so UDP clients can still connect over DTLS, or accept that clients are TLS-over-TCP only. This affects client transport, not the UDP relay to peers. Second, the relay destination policy does not fully contain a relay by default:

- **Loopback** (`127.0.0.0/8`, `::1`) is blocked unless you set `allow-loopback-peers`; leave it off.
- **RFC 1918, IPv4 link-local (`169.254.0.0/16`, which includes the `169.254.169.254` cloud-metadata address), and IPv6 local scopes** must be denied explicitly, as in the block above. Current coturn also rejects several of these through built-in scope checks, but distro and version behaviour has varied, so the explicit `denied-peer-ip` lines are what this guide relies on. Missing them, an authenticated user (or, on the stock config, an anonymous one) reaches your internal network and the metadata endpoint.
- **Multicast** is allowed unless `no-multicast-peers` is set.
- `allowed-peer-ip` is an exception list, not a default-deny allowlist: an address it does not name can still be permitted.

STUN Binding stays anonymous even when TURN allocation requires credentials, and closing anonymous allocation does not close reflection: an unauthenticated request still draws a `401` challenge response that can itself reflect and amplify toward a spoofed source. `unauthorized-ratelimit` (off by default) bounds that, `secure-stun` requests authenticated Binding, and RFC 5780 (a reflection amplifier) is off by default, so leave it off. The two admin surfaces authenticate separately from TURN users and from each other: the CLI uses `cli-password`, while the web admin uses its own provisioned admin accounts, so setting `cli-password` does not secure the web admin. Disable both (`cli=false`, `web-admin=false`) or keep them on loopback, keep `web-admin-listen-on-workers` off, and do not enable `server-relay`, which drops permission checks on relayed traffic. `--no-cli` is retired in 4.18.0, so use `cli=false`.

Unverified until checked in your deployment: the default service state and effective configuration of any specific distro or container image, the build's TLS/feature availability, and real reflection/amplification factors.

## Shared exposures

- **An open TURN relay reaches your internal network and amplifies UDP.** An anonymous (or abusive authenticated) allocator originates traffic through the relay to any permitted, reachable peer, which is an SSRF-like path into your private network and the cloud-metadata endpoint, plus a UDP amplification vector. Authentication closes anonymous allocation; explicit `denied-peer-ip` policy and network controls are still needed against authenticated abuse.
- **A weak or development LiveKit secret forges room admission.** A known signing secret lets an attacker choose identities and grants, so publishing, subscribing, or administering rooms all become available. Application end-to-end encryption is a separate content boundary, not a substitute for protecting the secret.
- **Plaintext signaling or relay.** Public HTTP/WS exposes signaling and bearer tokens in transit. Plaintext TURN does not send the long-term password itself (the protocol proves knowledge of it through a challenge and message integrity), but it exposes usernames and protocol metadata and permits offline guessing against a weak password, so terminate TLS and require it. Media transport encryption is a separate layer again.
- **STUN reflection and amplification.** Binding and `401`-challenge responses are unauthenticated regardless of TURN auth, so a spoofed source can reflect UDP toward a victim; rate limiting and disabling response-enlarging features reduce it, but authenticating allocation does not remove it.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor sources rather than observed, and backlog row 2.34 tracks demonstrating them against live instances in the exposed and fixed states. A redirect, a `404`, a timeout, or a TLS error is inconclusive, never proof of the fixed state; every negative check needs a working positive control.

```bash
sudo ss -tlnp    # Read the bind address per port, do not just confirm the port. LiveKit signaling 7880
sudo ss -aunp    # should be on loopback (behind the proxy); RTC 7881 and coturn 3478/5349 are expected
                 # PUBLIC (a relay and media are useless if unreachable), so their public bind is normal,
                 # not the finding. The findings are: a wildcard-bound 7880, or any exposed CLI 5766,
                 # web-admin 8080, or metrics 9641/6789. coturn 3478 is a persistent listener; the LiveKit
                 # 50000-60000 media range and coturn 49152-65535 relay range appear only during active
                 # calls/allocations. A private bind is not external isolation: confirm reachability from
                 # off-host separately, since NAT or Docker forwarding can publish a loopback-bound port.
```

```bash
# LiveKit reachability/auth diagnostic against the direct listener. This ONLY shows the endpoint requires
# a token; it does NOT prove the dev/known secret is gone (see the rotation test below). Substitute the
# base URL inside the single quotes on the set -- line and paste the whole block so the guard runs.
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

The **decisive** LiveKit check is a key-rotation test that discriminates the exposed state, because an unauthenticated `/rtc/validate` returns `401` whether or not the dev key is still in use. Mint a correctly scoped token signed with the old (`devkey`/`secret`, or a retired real) secret with a JWT tool or `livekit-cli`, confirm it is *accepted* on an isolated development fixture, then confirm the *same token is rejected* against the deployment after its key is rotated, while a token signed with the new key is accepted. An expired or wrong-room token is an invalid rotation test, and the isolated fixture is what keeps the dev secret off the public instance. Separately probe the metrics and debug routes (and any `debug_handler.port`) and the embedded TURN sockets from an untrusted network; a healthy `/` proves none of them protected.

For coturn, the discriminator is a TURN **Allocate** exchange, not an HTTP request. Send a well-formed Allocate requesting UDP relay with no credentials: an allocation containing a relayed address means anonymous allocation is open, while an authentication challenge with no allocation means it is closed (the required positive control is a valid-credential allocation, because the initial `401` also occurs during a successful authenticated exchange). Closing anonymous allocation is not the whole fix: authenticated, request `CreatePermission`/`ChannelBind` for an owned RFC 1918 or `169.254.169.254` test peer and confirm a `403` with no traffic reaching it, across the denied ranges and both address families (a plain allocation failure or timeout is not evidence of peer policy). Verify TLS separately, and require verification to be fatal so a diagnostic tool does not continue past a bad certificate:

```bash
openssl s_client -connect turn.example.com:5349 -servername turn.example.com \
  -verify_hostname turn.example.com -verify_return_error \
  -CAfile /etc/ssl/certs/ca-certificates.crt </dev/null
```

That proves the certificate and handshake only, not TURN authentication, peer policy, or that plaintext is refused; also send plain STUN/TURN to `3478` and to `5349` and confirm it is rejected once `no-tcp`/`no-udp` are set. A local socket binding proves neither public reachability nor TLS. Never add `-k`/`--insecure` to any of these.

## Common mistakes

- Running LiveKit in development mode, or leaving the sample `key1: secret1` or `key2: secret2` pairs in the key set, so a public secret mints valid admin tokens; check every retained development and sample pair, not just `devkey`.
- Treating a short signing secret as safe because the server started: the length check only logs and does not block startup.
- Creating the LiveKit key file group- or world-readable, which stops the server from starting.
- Running coturn with the stock example config (no `lt-cred-mech`, no users), which relays anonymously, an open relay.
- Enabling authentication but forgetting relay policy, so an authenticated user reaches RFC 1918 hosts and the `169.254.169.254` metadata endpoint that coturn does not reliably block for you.
- Opening the coturn TLS port but leaving plain `3478` (and TLS-port plaintext) accepted because `no-tcp`/`no-udp` were not set, so clients still connect unencrypted.
- Assuming TURN credentials protect STUN Binding, the CLI, or the web admin, or that `cli-password` secures the web admin; each is a separate surface, and coturn's Prometheus exporter binds a wildcard address unauthenticated.
- Restricting LiveKit's signaling bind and assuming the RTC and embedded-TURN sockets followed; they bind independently.

## Sources (checked September 2026)

- LiveKit ports and firewall reference (`7880`, `7881`, UDP media range, single-port mux): https://docs.livekit.io/transport/self-hosting/ports-firewall/
- LiveKit key validation (`ValidateKeys()` errors on an empty key map and on a key file readable by others; the sub-32-character secret log): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/pkg/config/config.go
- LiveKit development-mode `devkey`/`secret` injection and conditional loopback bind: https://raw.githubusercontent.com/livekit/livekit/v1.13.7/cmd/server/main.go
- LiveKit sample config (uncommented `key1: secret1` / `key2: secret2`; embedded-TURN, metrics, and debug settings): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/config-sample.yaml
- LiveKit tokens and grants (HS256 JWT, room and admin grants, permissive defaults): https://docs.livekit.io/frontends/reference/tokens-grants/
- LiveKit self-hosting deployment (TLS terminates at a proxy; `wss://`): https://docs.livekit.io/transport/self-hosting/deployment/
- coturn example configuration (anonymous default, `allow-loopback-peers`, `no-multicast-peers`, `no-tcp`/`no-udp`, `cli`/`web-admin` defaults, `prometheus-address`, `unauthorized-ratelimit`, `cert`/`pkey`, `tls-listening-port`): https://raw.githubusercontent.com/coturn/coturn/4.18.0/examples/etc/turnserver.conf
- coturn option reference (credential modes, `use-auth-secret`, `secure-stun`, `server-relay`, CLI and web-admin auth, relay port range): https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnserver
- coturn 4.17.0 release notes (DTLS listeners now opt-in, started only with `--dtls`): https://github.com/coturn/coturn/releases/tag/4.17.0
- coturn 4.18.0 release notes (`--no-cli` retired): https://github.com/coturn/coturn/releases/tag/4.18.0
- coturn peer-address classification and policy (loopback, link-local, RFC 1918, multicast handling): https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/server/ns_turn_server.c
- curl manual (the `exitcode` and `errormsg` write-out variables in the Verify probe, both added in curl 7.75.0): https://curl.se/docs/manpage.html
