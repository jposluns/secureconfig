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

frp also supports `auth.method = "oidc"`: frpc obtains a token from an OIDC provider through the Client Credentials Grant and frps validates it by issuer and audience, authenticating frpc to frps instead of using a shared token, useful for centralizing frp auth behind an identity provider.

From frp v0.50.0, `transport.tls.enable` defaults to `true`, so the connection between `frpc` and `frps` is encrypted out of the box; the gap is verification, not encryption. `frpc` still does not verify `frps`'s certificate by default, so it will encrypt to whatever server answers on `serverAddr`, genuine or not. Set `transport.tls.certFile`/`transport.tls.keyFile` on the server and `transport.tls.trustedCaFile` on every client so `frpc` verifies the server's certificate against a trusted CA, and set `transport.tls.force = true` on the server so it refuses any client that did not negotiate TLS at all.

The `auth` block is schema-optional, and the frp documentation does not state what a server does when it is left out entirely. Treat an unconfigured token as an open door rather than assuming a safe default: always set `auth.token` (or OIDC) before exposing `bindPort` to the internet, and never rely on frp for anything without one.

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

By default WireGuard "tries to be as silent as possible when not being used," so the only inbound port a firewall needs to open is the single WireGuard UDP `ListenPort`; everything else on the host stays closed per [host.md](host.md).

## ssh -R (remote forwarding)

`ssh -R 8080:localhost:3000 user@server` is the quickest ad-hoc self-hosted tunnel: it asks the server to forward connections to its own port 8080 back through your SSH session to your `localhost:3000`. Whether that published port is a private convenience or an open door is decided on the server by `GatewayPorts` in `sshd_config`, not by the client.

With the default `GatewayPorts no`, the server binds the forwarded port to loopback, so only the server itself reaches it and nothing is exposed to the network; a client that asks for a public bind, as in `ssh -R '*:8080:localhost:3000' ...`, is quietly overridden back to loopback. `GatewayPorts yes` forces a wildcard bind on every interface regardless of what the client requests. `clientspecified` instead honours the bind address in the request, so under it that same `ssh -R '*:8080:localhost:3000' ...` opens all interfaces while `ssh -R '127.0.0.1:8080:localhost:3000' ...` stays on loopback. SSH authenticates the tunnel session itself, but adds nothing for callers reaching the forwarded port: once that port is on a public interface, if `localhost:3000` has no login of its own, anyone who reaches `server:8080` has it.

To publish such an app, do not widen `GatewayPorts`. Leave it `no` so the forward stays on the server's loopback, and run a reverse proxy on the server that reads `localhost:8080` and exposes only an authenticated TLS listener ([caddy.md](caddy.md), [nginx.md](nginx.md)); the forwarded port itself never faces the network. Setting `GatewayPorts yes` would put port 8080 straight onto the public interface, in front of that proxy rather than behind it. For a persistent tunnel, run the `ssh -R` under `autossh` so it reconnects, and give the login its own key on a restricted account.

## Verify

```bash
# frp: a client with the wrong token is rejected, not connected
frpc -c frpc-wrongtoken.toml   # expect an authentication failure, no proxy registered

ss -ulnp   # read every listener; 51820: WireGuard: only the one UDP port listening
sudo ufw status verbose        # no other inbound rule added for the tunneled service

# positive control: from the peer, a destination inside its intended subnet must succeed, proving
# the tunnel and routing both work
ping -c1 192.168.88.10

# forbidden destination: from the peer, a host the server would otherwise forward to (its own LAN,
# reachable through the tunnel if not for this rule) but outside 192.168.88.0/24, so a failure here
# is attributable to the firewall rule rather than to an address that was never routed or never live
ping -c1 192.168.1.50          # expect 100 percent packet loss

# confirm the drop is the firewall rule acting, not a routing gap: its counter must be nonzero
sudo nft list ruleset | grep -A1 'saddr 192.168.88.0/24'   # packets and bytes both greater than 0

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
