# Self-hosted tunnels: frp, WireGuard, and ssh -R

All three expose a private host to the internet without a public IP, the same job [cloudflare.md](cloudflare.md) and [tailscale.md](tailscale.md) do, but with no vendor edge: you run and secure both ends yourself, on a host still hardened per [host.md](host.md). frp with a weak or absent token lets anyone bind proxies through your server; WireGuard has no login at all, only key pairs and the traffic scoping you configure; and `ssh -R` forwards a local port through your own SSH login, kept on the server's loopback by default but reachable by anyone if `GatewayPorts` is widened.

## frp

`frps` (the server) listens for client connections on `bindPort`, default `7000`. Authentication is token-based by default: set the identical `auth.token` in `frps.toml` and every `frpc.toml`, since "client needs to set the same value to pass authentication":

```toml
# frps.toml
bindPort = 7000
auth.token = "REPLACE_WITH_LONG_RANDOM_VALUE"
```

```toml
# frpc.toml
serverAddr = "203.0.113.10"
serverPort = 7000
auth.token = "REPLACE_WITH_LONG_RANDOM_VALUE"
```

frp also supports `auth.method = "oidc"`: frpc obtains a token from an OIDC provider through the Client Credentials Grant and frps validates it by issuer and audience, authenticating frpc to frps instead of using a shared token, useful for centralizing frp auth behind an identity provider. Audience validation is conditional, though: frps skips it when `auth.oidc.audience` is left empty (it sets the token verifier's `SkipClientIDCheck` in that case), so set a nonempty `auth.oidc.audience` and the intended `auth.oidc.issuer` explicitly rather than assuming that selecting `auth.method = "oidc"` binds the token to your server.

Both the shared token and OIDC authenticate `frpc` to `frps`; neither authenticates the callers who reach a service you publish through the tunnel. A registered proxy binds on `proxyBindAddr`, which defaults to the server's `bindAddr` of `0.0.0.0` (as of v0.71.0), so once the proxy is up anyone who can reach that listener reaches the service behind it, exactly as if the app faced a public port directly. Give the published service its own authentication, or keep the proxy on loopback and front it with an authenticated TLS proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)); a strong `auth.token` protects the tunnel, not the service.

From frp v0.50.0, `transport.tls.enable` defaults to `true`, so the connection between `frpc` and `frps` is encrypted out of the box; the gap is verification, not encryption. `frpc` still does not verify `frps`'s certificate by default, so it will encrypt to whatever server answers on `serverAddr`, genuine or not. Set `transport.tls.certFile`/`transport.tls.keyFile` on the server and `transport.tls.trustedCaFile` on every client so `frpc` verifies the server's certificate against a trusted CA, and set `transport.tls.force = true` on the server so it refuses any client that did not negotiate TLS at all.

The `auth` block is schema-optional, and omitting it does not fail closed: frp defaults to the token method with an empty token, and `frps` derives its auth key from that empty string, so a client presenting an empty token authenticates. An unconfigured token is an open door, not a safe default: always set a long random `auth.token` (or OIDC) before exposing `bindPort` to the internet, and never rely on frp for anything without one.

## WireGuard

WireGuard has no username or password; identity is a base64-encoded key pair, generated per peer:

```bash
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

The private key never leaves the peer that generated it; only the public key goes into the other side's configuration. A peer is added to an interface with its public key, an endpoint, and `AllowedIPs`:

```bash
wg set wg0 listen-port 51820 private-key /path/to/private-key peer "REPLACE_WITH_PEER_PUBLIC_KEY" allowed-ips 192.168.88.0/24 endpoint 203.0.113.10:51820
```

`AllowedIPs` is dual-purpose "Cryptokey Routing," but the two purposes are not symmetric. On the sending side it "behaves as a sort of routing table," picking which peer a destination IP goes to. On the receiving side it "behaves as a sort of access control list" for the packet's source address only, dropping a decrypted packet whose source IP does not match the sending peer's configured `AllowedIPs`; it is a spoofing check, not a destination filter, and it is the server's actual restriction on which source address a peer may use. Once a peer is authenticated, its `AllowedIPs` entry places no limit on which destinations that peer is allowed to reach if the server is willing to forward the traffic there. Scope `AllowedIPs` to exactly the address or subnet a peer should be reached at, never `0.0.0.0/0` unless that peer is genuinely meant to be a full-tunnel gateway, and restrict which destinations a peer can reach through the server with a firewall rule on the server itself, matching the same source prefix as that peer's `AllowedIPs` so the peer cannot rotate its source address within that prefix to evade a narrower rule, for example an nftables rule dropping forwarded packets from anywhere in this peer's permitted subnet to a destination outside its intended subnet, with a counter so the rule's effect can be confirmed later:

```bash
nft add rule inet filter forward iifname "wg0" ip saddr 192.168.88.0/24 ip daddr != 192.168.88.0/24 counter drop
```

That rule assumes a base chain hooked to `forward` already exists in table `inet filter` (create one with `nft add chain inet filter forward '{ type filter hook forward priority 0; }'` if you manage nftables directly; an unreferenced regular chain of that name is attached to no hook and receives no traffic). It then governs only traffic the server routes between interfaces: it takes effect only with `net.ipv4.ip_forward` enabled, and because `nft add rule` appends, an earlier `accept` in the same chain short-circuits it, so place it ahead of any such accept. It does not restrict what a peer reaches on the server host itself (a service bound to the `wg0` address or to `0.0.0.0` is reached through the `input` hook and needs its own rule), and as written it matches IPv4 only; add an `ip6 saddr`/`ip6 daddr` counterpart if the peer carries an IPv6 `AllowedIPs`.

By default WireGuard "tries to be as silent as possible when not being used," so the only inbound port a firewall needs to open is the single WireGuard UDP `ListenPort`; everything else on the host stays closed per [host.md](host.md).

## ssh -R (remote forwarding)

`ssh -R 8080:localhost:3000 user@server` is the quickest ad-hoc self-hosted tunnel: it asks the server to forward connections to its own port 8080 back through your SSH session to your `localhost:3000`. Whether that published port is a private convenience or an open door is decided on the server by `GatewayPorts` in `sshd_config`, not by the client.

With the default `GatewayPorts no`, the server binds the forwarded port to loopback, so only the server itself reaches it and nothing is exposed to the network; a client that asks for a public bind, as in `ssh -R '*:8080:localhost:3000' ...`, is quietly overridden back to loopback. `GatewayPorts yes` forces a wildcard bind on every interface regardless of what the client requests. `clientspecified` instead honours the bind address in the request, so under it that same `ssh -R '*:8080:localhost:3000' ...` opens all interfaces while `ssh -R '127.0.0.1:8080:localhost:3000' ...` stays on loopback. SSH authenticates the tunnel session itself, but adds nothing for callers reaching the forwarded port: once that port is on a public interface, if `localhost:3000` has no login of its own, anyone who reaches `server:8080` has it.

To publish such an app, do not widen `GatewayPorts`. Leave it `no` so the forward stays on the server's loopback, and run a reverse proxy on the server that reads `localhost:8080` and exposes only an authenticated TLS listener ([caddy.md](caddy.md), [nginx.md](nginx.md)); the forwarded port itself never faces the network. Setting `GatewayPorts yes` would put port 8080 straight onto the public interface, in front of that proxy rather than behind it. For a persistent tunnel, run the `ssh -R` under `autossh` so it reconnects, and give the login its own key on a restricted account.

## Verify

```bash
# frp positive control: with the correct auth.token, frpc logs 'login to server success' (proving
# reachability and a valid token). frpc then stays in the FOREGROUND; stop it with Ctrl-C before the
# next command. This exercises token auth only; auth.token has no effect under auth.method = "oidc".
frpc -c frpc.toml              # expect a 'login to server success, get run id ...' log line
# negative control: the same config with ONLY the token changed must fail LOGIN for an authentication
# reason. The exact text is version-dependent, so key on the token/auth reason and the ABSENCE of a
# 'login to server success', not a literal string; a config-load, DNS, TLS, or connection error does NOT count
sed 's/^auth\.token[[:space:]]*=.*/auth.token = "WRONG_VALUE"/' frpc.toml > frpc-wrongtoken.toml
frpc -c frpc-wrongtoken.toml   # expect a token-auth failure (e.g. 'token in login doesn't match token from configuration'), no run id
# open-door check: a server whose auth.token is absent or empty accepts an empty token, so confirm your
# frps also REJECTS an empty-token client; a successful login here means your server has no token set
sed 's/^auth\.token[[:space:]]*=.*/auth.token = ""/' frpc.toml > frpc-emptytoken.toml
frpc -c frpc-emptytoken.toml   # expect the same login failure

sudo wg show wg0          # needs privilege; shows the listen-port (51820) + per-peer state, and a recent 'latest handshake' is the liveness signal. wg show reports CONFIGURATION, so also confirm the interface is running:
ip link show wg0          # expect the UP flag in the <...> flags; a WireGuard interface usually shows operational 'state UNKNOWN', which is fine. wg show reporting a port while the interface is administratively down is why this check exists
ss -ulnp                  # read every UDP listener to spot any OTHER, unexpected service; do not rely on it to confirm WireGuard (the in-kernel socket has no owning process to show under -p, and a real host also lists resolved/mDNS)
# ufw must be active with a default-deny (or default-reject) incoming policy, or this proves nothing
# ('inactive' or a default-allow policy would pass it while the port is open):
sudo ufw status verbose
# confirm nothing admits UNAUTHORIZED external traffic to the tunneled service beyond the intended
# tunnel/proxy path, for BOTH IPv4 and IPv6; ufw shows only its own iptables/ip6tables view, so read
# native nftables rules (the forward rule above) separately with 'nft list ruleset':
sudo ufw show raw

# positive control: from the peer, ping a host reachable ONLY through the tunnel (another peer, or a
# server-side address in 192.168.88.0/24 that the peer cannot reach on its own LAN), so a success proves
# WireGuard traversal and server routing rather than a local route
ping -c1 192.168.88.10

# forbidden destination: from the peer, a host the server would otherwise forward to (its own LAN,
# reachable through the tunnel if not for this rule) but outside 192.168.88.0/24, so a failure here
# is attributable to the firewall rule rather than to an address that was never routed or never live
ping -c1 192.168.1.50          # expect 100 percent packet loss (attribution comes from the counter increase below, not this loss on its own)

# confirm the drop is THIS rule acting, not a routing gap or a stale count. The counter lives on the
# SERVER; the traffic comes from the PEER, so this spans two hosts. It is a confirmation aid, not a
# rigorous proof: the counter increments on EVERY matching packet, so run it on an otherwise-idle peer.
# 1) On the SERVER, read the rule's packet counter. The chain header must say 'type filter hook forward'
#    (an unreferenced regular chain gets no traffic) and the grep pins the full match AND the drop verdict
#    so a same-match accept rule is not read instead:
sudo nft list chain inet filter forward | grep -E 'type filter hook forward|iifname "wg0" ip saddr 192.168.88.0/24 ip daddr != 192.168.88.0/24 counter .* drop'
# 2) FROM THE PEER, send the forbidden ping (its own AllowedIPs must include 192.168.1.50, or the packet
#    never leaves for the server to drop):
ping -c1 192.168.1.50
# 3) On the SERVER, read the counter again: the packet count must have INCREASED by that ping:
sudo nft list chain inet filter forward | grep -E 'iifname "wg0" ip saddr 192.168.88.0/24 ip daddr != 192.168.88.0/24 counter .* drop'

# ssh -R: on the SERVER, a forwarded port binds 127.0.0.1 (or [::1]) with GatewayPorts no, never 0.0.0.0
ss -tlnp   # read every listener; 8080: only a loopback address unless you deliberately published it
```

## Sources (checked September 2026)

- frp documentation (setup, server reference): https://gofrp.org/en/docs/
- OpenSSH `sshd_config` (`GatewayPorts` default `no`, `yes` binds all interfaces, `clientspecified`): https://man.openbsd.org/sshd_config#GatewayPorts
- OpenSSH `ssh` (`-R [bind_address:]port:host:hostport` remote forwarding): https://man.openbsd.org/ssh#R
- frp server configuration reference (`bindPort`, `auth.token`, `transport.tls.force`): https://gofrp.org/en/docs/reference/server-configures/
- frp authentication (`auth.token`, `auth.method = "oidc"`): https://gofrp.org/en/docs/features/common/authentication/
- WireGuard quickstart (`wg genkey`, `wg pubkey`, `wg set`, silent-protocol behavior): https://www.wireguard.com/quickstart/
- WireGuard Cryptokey Routing (`AllowedIPs` on send and receive): https://www.wireguard.com/
- frp TLS (`transport.tls.enable` default from v0.50.0, `transport.tls.force`, cert/key/CA roles): https://gofrp.org/en/docs/features/common/network/network-tls/
- nftables manual (forward/input hooks, verdicts, and rule counters): https://netfilter.org/projects/nftables/manpage.html
- frps `bindAddr` default `0.0.0.0`, and an empty `proxyBindAddr` takes `bindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/pkg/config/v1/server.go#L110-L114
- frps TCP proxies listen on `proxyBindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/tcp.go#L76
- frps UDP proxies listen on `proxyBindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/udp.go#L92
- frps HTTP and HTTPS vhost listeners bind `proxyBindAddr` (L303 and L334), sharing the main listener only when `bindAddr` equals `proxyBindAddr` (L229-L235) (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L303
