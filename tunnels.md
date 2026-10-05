---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "8d8013942ecc4c0abfd6d8f96b9020acaa065ec51666dcaebe93fc93012c2e6c",
  "components": {
    "frp": {
      "name": "frp documentation",
      "basis": "unknown",
      "sources": {
        "s7800b0cbd057": "https://gofrp.org/en/docs/",
        "seaee50f5c2ba": "https://gofrp.org/en/docs/reference/server-configures/",
        "s7479bbde986d": "https://gofrp.org/en/docs/features/common/authentication/",
        "sdd126f42c07d": "https://gofrp.org/en/docs/features/common/network/network-tls/"
      }
    },
    "frps": {
      "name": "frps source",
      "basis": "v0.71.0",
      "sources": {
        "s89885e642b0b": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/config/v1/server.go#L110-L114",
        "s2cbb0ac0ce1d": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/tcp.go#L76",
        "s0d14a82746a7": "https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L193-L194",
        "s4660388fcc97": "https://github.com/fatedier/frp/blob/v0.71.0/server/visitor/visitor.go#L49-L57",
        "sf9bd235cd56f": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/udp.go#L92-L97",
        "sf34f64f9f242": "https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L303-L321",
        "scc414a949e04": "https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L329-L340",
        "sc8820327b4be": "https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L229-L235",
        "s4ee7a04bc22b": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/stcp.go#L43-L46",
        "s1ab713dcffdf": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/sudp.go#L43-L46",
        "sba4684b85dea": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/proxy.go#L202-L215",
        "sb5db43210eff": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/util/net/listener.go#L25-L37",
        "sa3237f5cd553": "https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/xtcp.go#L63",
        "s9bcd6f277557": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/nathole/controller.go#L125-L139",
        "s43d2e3e185b7": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/auth/oidc.go#L281-L287",
        "sc1e3e11b0618": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/config/v1/server.go#L128-L139",
        "s72151a3006dc": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/auth/token.go#L64-L69",
        "sc982b975a190": "https://github.com/fatedier/frp/blob/v0.71.0/pkg/util/util/util.go#L50-L56"
      }
    },
    "tls-min": {
      "name": "frp TLS default minimum",
      "basis": "v0.50.0",
      "sources": {
        "sdd126f42c07d": "https://gofrp.org/en/docs/features/common/network/network-tls/"
      }
    },
    "wg": {
      "name": "WireGuard",
      "basis": "unknown",
      "sources": {
        "sd41c4b487466": "https://www.wireguard.com/quickstart/",
        "sf75d6938d30e": "https://www.wireguard.com/"
      }
    },
    "nft": {
      "name": "nftables",
      "basis": "unknown",
      "sources": {
        "s0defde7f202b": "https://netfilter.org/projects/nftables/manpage.html"
      }
    },
    "ssh": {
      "name": "OpenSSH",
      "basis": "unknown",
      "sources": {
        "s0fdb398555df": "https://man.openbsd.org/sshd_config#GatewayPorts",
        "s1f80cf6ae7f5": "https://man.openbsd.org/ssh#R"
      }
    },
    "autossh-source": {
      "name": "autossh source",
      "basis": "90a8c2f0129f6fe19ec26c7d0fdbab4bb468f476",
      "sources": {
        "s6398847a2896": "https://github.com/Autossh/autossh/blob/90a8c2f0129f6fe19ec26c7d0fdbab4bb468f476/README#L25-L26"
      }
    },
    "ufw-docs": {
      "name": "Ubuntu Noble ufw manual",
      "basis": "unknown",
      "sources": {
        "scff3a017f30b": "https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html"
      }
    },
    "iproute2-docs": {
      "name": "iproute2 manuals",
      "basis": "v6.12.0",
      "sources": {
        "s8aa0d96d25e7": "https://raw.githubusercontent.com/iproute2/iproute2/v6.12.0/man/man8/ip-link.8.in",
        "s5d50117b1a36": "https://raw.githubusercontent.com/iproute2/iproute2/v6.12.0/man/man8/ss.8"
      }
    },
    "linux-source": {
      "name": "Linux source",
      "basis": "v6.8",
      "sources": {
        "sc7cb2448145d": "https://github.com/torvalds/linux/blob/v6.8/Documentation/networking/operstates.rst#L39-L40",
        "sdfc1a2d0c3cc": "https://github.com/torvalds/linux/blob/v6.8/Documentation/networking/operstates.rst#L58-L61",
        "scd9d50cf72b7": "https://github.com/torvalds/linux/blob/v6.8/drivers/net/wireguard/socket.c#L387-L393",
        "sb02ea8702b2a": "https://github.com/torvalds/linux/blob/v6.8/net/ipv4/udp_tunnel_core.c#L17-L19"
      }
    }
  },
  "claims": {
    "frps-port": {"text": "frps bindPort defaults to 7000.", "components": ["frps"], "sources": ["frps:s89885e642b0b"], "status": "REASONED"},
    "frp-token": {"text": "Token authentication is the default; set the same long random auth.token on frps and every frpc.", "components": ["frp", "frps"], "sources": ["frp:seaee50f5c2ba", "frp:s7479bbde986d", "frps:sc1e3e11b0618", "frps:s72151a3006dc"], "status": "REASONED"},
    "frp-empty": {"text": "Omitted auth defaults to an empty token and accepts empty-token clients; configure token or OIDC before exposure.", "components": ["frp", "frps"], "sources": ["frp:seaee50f5c2ba", "frp:s7479bbde986d", "frps:sc1e3e11b0618", "frps:s72151a3006dc", "frps:sc982b975a190"], "status": "REASONED"},
    "frp-oidc": {"text": "auth.method=oidc uses Client Credentials Grant for frpc-to-frps authentication; set issuer and nonempty audience because an empty audience skips validation.", "components": ["frp", "frps"], "sources": ["frp:s7479bbde986d", "frps:s43d2e3e185b7"], "status": "REASONED"},
    "proxy-bind": {"text": "proxyBindAddr defaults to bindAddr, whose default is 0.0.0.0.", "components": ["frps"], "sources": ["frps:s89885e642b0b"], "status": "REASONED"},
    "proxy-tcp": {"text": "Registered TCP proxies listen on proxyBindAddr.", "components": ["frps"], "sources": ["frps:s2cbb0ac0ce1d"], "status": "REASONED"},
    "proxy-udp": {"text": "Registered UDP proxies listen on proxyBindAddr.", "components": ["frps"], "sources": ["frps:sf9bd235cd56f"], "status": "REASONED"},
    "proxy-http": {"text": "HTTP and HTTPS proxy listeners bind proxyBindAddr.", "components": ["frps"], "sources": ["frps:sf34f64f9f242", "frps:scc414a949e04", "frps:sc8820327b4be"], "status": "REASONED"},
    "proxy-tcpmux": {"text": "tcpmux proxies listen on proxyBindAddr.", "components": ["frps"], "sources": ["frps:s0d14a82746a7"], "status": "REASONED"},
    "proxy-visitors": {"text": "stcp, sudp and xtcp open no listener of their own on frps.", "components": ["frps"], "sources": ["frps:s4660388fcc97", "frps:s4ee7a04bc22b", "frps:s1ab713dcffdf", "frps:sba4684b85dea", "frps:sb5db43210eff", "frps:sa3237f5cd553", "frps:s9bcd6f277557"], "status": "REASONED"},
    "service-auth": {"text": "frp token/OIDC authenticates tunnel clients, not service callers; add app auth or a loopback authenticated TLS proxy.", "components": ["frp", "frps"], "sources": ["frp:s7479bbde986d", "frps:s2cbb0ac0ce1d", "frps:sf9bd235cd56f", "frps:sf34f64f9f242", "frps:s0d14a82746a7"], "status": "REASONED"},
    "tls-default": {"text": "transport.tls.enable defaults true from v0.50.0, encrypting frpc-to-frps traffic.", "components": ["tls-min"], "sources": ["tls-min:sdd126f42c07d"], "status": "REASONED"},
    "tls-verify": {"text": "frpc does not verify frps certificates by default; configure server certFile/keyFile and client trustedCaFile.", "components": ["frp"], "sources": ["frp:sdd126f42c07d"], "status": "REASONED"},
    "tls-force": {"text": "Set server transport.tls.force=true to reject clients that do not negotiate TLS.", "components": ["frp"], "sources": ["frp:seaee50f5c2ba", "frp:sdd126f42c07d"], "status": "REASONED"},
    "wg-keys": {"text": "WireGuard uses per-peer key pairs, not passwords; generate under umask 077 and share only public keys.", "components": ["wg"], "sources": ["wg:sd41c4b487466"], "status": "REASONED"},
    "wg-endpoint": {"text": "wg set configures wg0 listen-port 51820, private key, peer public key, AllowedIPs and UDP endpoint 203.0.113.10:51820.", "components": ["wg"], "sources": ["wg:sd41c4b487466"], "status": "REASONED"},
    "wg-send": {"text": "AllowedIPs selects the sending peer by destination; scope to the peer subnet, using 0.0.0.0/0 only for a full-tunnel gateway.", "components": ["wg"], "sources": ["wg:sf75d6938d30e"], "status": "REASONED"},
    "wg-receive": {"text": "Receiving AllowedIPs checks the decrypted source address, not allowed destinations; enforce destination limits with a server firewall.", "components": ["wg", "nft"], "sources": ["wg:sf75d6938d30e", "nft:s0defde7f202b"], "status": "REASONED"},
    "wg-forward": {"text": "The nftables drop matches the peer's whole allowed source prefix and destinations outside its permitted subnet.", "components": ["wg", "nft"], "sources": ["wg:sf75d6938d30e", "nft:s0defde7f202b"], "status": "REASONED"},
    "nft-hook": {"text": "Use a forward base chain with IP forwarding enabled; append order matters because earlier accepts short-circuit the drop.", "components": ["nft"], "sources": ["nft:s0defde7f202b"], "status": "REASONED"},
    "nft-input": {"text": "Forward rules do not restrict services on the server itself; those need input rules.", "components": ["nft"], "sources": ["nft:s0defde7f202b"], "status": "REASONED"},
    "nft-ipv6": {"text": "The example matches IPv4 only; IPv6 AllowedIPs needs corresponding ip6 source/destination rules.", "components": ["nft"], "sources": ["nft:s0defde7f202b"], "status": "REASONED"},
    "wg-port": {"text": "WireGuard is normally silent when idle; open only its configured UDP ListenPort and keep other inbound services closed.", "components": ["wg"], "sources": ["wg:sd41c4b487466"], "status": "REASONED"},
    "ssh-map": {"text": "ssh -R 8080:localhost:3000 forwards server port 8080 to the client's localhost:3000.", "components": ["ssh"], "sources": ["ssh:s1f80cf6ae7f5"], "status": "REASONED"},
    "ssh-no": {"text": "GatewayPorts defaults no: loopback-only remote forwarding overrides a requested wildcard bind.", "components": ["ssh"], "sources": ["ssh:s0fdb398555df", "ssh:s1f80cf6ae7f5"], "status": "REASONED"},
    "ssh-yes": {"text": "GatewayPorts yes forces wildcard listening regardless of the requested bind.", "components": ["ssh"], "sources": ["ssh:s0fdb398555df"], "status": "REASONED"},
    "ssh-client": {"text": "GatewayPorts clientspecified honours requested wildcard or loopback binding.", "components": ["ssh"], "sources": ["ssh:s0fdb398555df", "ssh:s1f80cf6ae7f5"], "status": "REASONED"},
    "ssh-auth": {"text": "SSH authenticates the tunnel, not callers; retain GatewayPorts no and front localhost:8080 with authenticated TLS.", "components": ["ssh"], "sources": ["ssh:s0fdb398555df", "ssh:s1f80cf6ae7f5"], "status": "REASONED"},
    "ssh-persist": {"text": "Use autossh for reconnection and a dedicated key on a restricted account for persistent forwarding.", "components": ["ssh", "autossh-source"], "sources": ["ssh:s1f80cf6ae7f5", "autossh-source:s6398847a2896"], "status": "REASONED"},
    "verify-token": {"text": "Correct token must log login success; changed and empty tokens must fail authentication, not configuration, DNS, TLS or transport. Stop each foreground client.", "components": ["frp", "frps"], "sources": ["frp:s7479bbde986d", "frps:sc1e3e11b0618", "frps:s72151a3006dc", "frps:sc982b975a190"], "status": "REASONED", "verify": [1]},
    "verify-wg": {"text": "wg show needs privilege; inspect handshake and listen-port, then ip link UP because configuration alone does not prove a running interface.", "components": ["wg", "iproute2-docs", "linux-source"], "sources": ["wg:sd41c4b487466", "iproute2-docs:s8aa0d96d25e7", "linux-source:sc7cb2448145d", "linux-source:sdfc1a2d0c3cc"], "status": "REASONED", "verify": [1]},
    "verify-firewall": {"text": "Inspect all UDP listeners and active default-deny/reject IPv4/IPv6 firewall policy; ufw's view does not replace native nftables inspection.", "components": ["wg", "nft", "ufw-docs", "iproute2-docs", "linux-source"], "sources": ["wg:sd41c4b487466", "nft:s0defde7f202b", "ufw-docs:scff3a017f30b", "iproute2-docs:s5d50117b1a36", "linux-source:scd9d50cf72b7", "linux-source:sb02ea8702b2a"], "status": "REASONED", "verify": [1]},
    "verify-route": {"text": "An allowed ping must traverse WireGuard, not a local route; forbidden-destination loss alone does not identify the firewall cause.", "components": ["wg", "nft"], "sources": ["wg:sf75d6938d30e", "nft:s0defde7f202b"], "status": "REASONED", "verify": [1]},
    "verify-counter": {"text": "Read the server's full-match drop counter before/after the peer's routed forbidden ping; increases aid attribution only on an otherwise-idle peer.", "components": ["wg", "nft"], "sources": ["wg:sf75d6938d30e", "nft:s0defde7f202b"], "status": "REASONED", "verify": [1]},
    "verify-ssh": {"text": "On the SSH server, ss must show forwarded 8080 only on loopback with GatewayPorts no.", "components": ["ssh", "iproute2-docs"], "sources": ["ssh:s0fdb398555df", "ssh:s1f80cf6ae7f5", "iproute2-docs:s5d50117b1a36"], "status": "REASONED", "verify": [1]}
  }
}
---
# Self-hosted tunnels: frp, WireGuard, and ssh -R

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| frps-port: frps bindPort defaults to 7000. | frps source v0.71.0 | REASONED |
| frp-token: Token authentication is the default; set the same long random auth.token on frps and every frpc. | frp documentation unknown; frps source v0.71.0 | REASONED |
| frp-empty: Omitted auth defaults to an empty token and accepts empty-token clients; configure token or OIDC before exposure. | frp documentation unknown; frps source v0.71.0 | REASONED |
| frp-oidc: auth.method=oidc uses Client Credentials Grant for frpc-to-frps authentication; set issuer and nonempty audience because an empty audience skips validation. | frp documentation unknown; frps source v0.71.0 | REASONED |
| proxy-bind: proxyBindAddr defaults to bindAddr, whose default is 0.0.0.0. | frps source v0.71.0 | REASONED |
| proxy-tcp: Registered TCP proxies listen on proxyBindAddr. | frps source v0.71.0 | REASONED |
| proxy-udp: Registered UDP proxies listen on proxyBindAddr. | frps source v0.71.0 | REASONED |
| proxy-http: HTTP and HTTPS proxy listeners bind proxyBindAddr. | frps source v0.71.0 | REASONED |
| proxy-tcpmux: tcpmux proxies listen on proxyBindAddr. | frps source v0.71.0 | REASONED |
| proxy-visitors: stcp, sudp and xtcp open no listener of their own on frps. | frps source v0.71.0 | REASONED |
| service-auth: frp token/OIDC authenticates tunnel clients, not service callers; add app auth or a loopback authenticated TLS proxy. | frp documentation unknown; frps source v0.71.0 | REASONED |
| tls-default: transport.tls.enable defaults true from v0.50.0, encrypting frpc-to-frps traffic. | frp TLS default minimum v0.50.0 | REASONED |
| tls-verify: frpc does not verify frps certificates by default; configure server certFile/keyFile and client trustedCaFile. | frp documentation unknown | REASONED |
| tls-force: Set server transport.tls.force=true to reject clients that do not negotiate TLS. | frp documentation unknown | REASONED |
| wg-keys: WireGuard uses per-peer key pairs, not passwords; generate under umask 077 and share only public keys. | WireGuard unknown | REASONED |
| wg-endpoint: wg set configures wg0 listen-port 51820, private key, peer public key, AllowedIPs and UDP endpoint 203.0.113.10:51820. | WireGuard unknown | REASONED |
| wg-send: AllowedIPs selects the sending peer by destination; scope to the peer subnet, using 0.0.0.0/0 only for a full-tunnel gateway. | WireGuard unknown | REASONED |
| wg-receive: Receiving AllowedIPs checks the decrypted source address, not allowed destinations; enforce destination limits with a server firewall. | WireGuard unknown; nftables unknown | REASONED |
| wg-forward: The nftables drop matches the peer's whole allowed source prefix and destinations outside its permitted subnet. | WireGuard unknown; nftables unknown | REASONED |
| nft-hook: Use a forward base chain with IP forwarding enabled; append order matters because earlier accepts short-circuit the drop. | nftables unknown | REASONED |
| nft-input: Forward rules do not restrict services on the server itself; those need input rules. | nftables unknown | REASONED |
| nft-ipv6: The example matches IPv4 only; IPv6 AllowedIPs needs corresponding ip6 source/destination rules. | nftables unknown | REASONED |
| wg-port: WireGuard is normally silent when idle; open only its configured UDP ListenPort and keep other inbound services closed. | WireGuard unknown | REASONED |
| ssh-map: ssh -R 8080:localhost:3000 forwards server port 8080 to the client's localhost:3000. | OpenSSH unknown | REASONED |
| ssh-no: GatewayPorts defaults no: loopback-only remote forwarding overrides a requested wildcard bind. | OpenSSH unknown | REASONED |
| ssh-yes: GatewayPorts yes forces wildcard listening regardless of the requested bind. | OpenSSH unknown | REASONED |
| ssh-client: GatewayPorts clientspecified honours requested wildcard or loopback binding. | OpenSSH unknown | REASONED |
| ssh-auth: SSH authenticates the tunnel, not callers; retain GatewayPorts no and front localhost:8080 with authenticated TLS. | OpenSSH unknown | REASONED |
| ssh-persist: Use autossh for reconnection and a dedicated key on a restricted account for persistent forwarding. | OpenSSH unknown; autossh source 90a8c2f0129f6fe19ec26c7d0fdbab4bb468f476 | REASONED |
| verify-token: Correct token must log login success; changed and empty tokens must fail authentication, not configuration, DNS, TLS or transport. Stop each foreground client. | frp documentation unknown; frps source v0.71.0 | REASONED |
| verify-wg: wg show needs privilege; inspect handshake and listen-port, then ip link UP because configuration alone does not prove a running interface. | WireGuard unknown; iproute2 manuals v6.12.0; Linux source v6.8 | REASONED |
| verify-firewall: Inspect all UDP listeners and active default-deny/reject IPv4/IPv6 firewall policy; ufw's view does not replace native nftables inspection. | WireGuard unknown; nftables unknown; Ubuntu Noble ufw manual unknown; iproute2 manuals v6.12.0; Linux source v6.8 | REASONED |
| verify-route: An allowed ping must traverse WireGuard, not a local route; forbidden-destination loss alone does not identify the firewall cause. | WireGuard unknown; nftables unknown | REASONED |
| verify-counter: Read the server's full-match drop counter before/after the peer's routed forbidden ping; increases aid attribution only on an otherwise-idle peer. | WireGuard unknown; nftables unknown | REASONED |
| verify-ssh: On the SSH server, ss must show forwarded 8080 only on loopback with GatewayPorts no. | OpenSSH unknown; iproute2 manuals v6.12.0 | REASONED |
<!-- version-basis:end -->

All three expose a private host to the internet without a public IP, the same job [cloudflare.md](cloudflare.md) and [tailscale.md](tailscale.md) do, but with no vendor edge: you run and secure both ends yourself, on a host still hardened per [host.md](host.md). frp with a weak or absent token lets anyone bind proxies through your server; WireGuard has no login at all, only key pairs and the traffic scoping you configure; and `ssh -R` forwards a local port through your own SSH login, kept on the server's loopback by default but reachable by anyone if `GatewayPorts` is widened.

## frp

`frps` (the server) listens for client connections on `bindPort`, default `7000` (as of v0.71.0). Authentication is token-based by default: set the identical `auth.token` in `frps.toml` and every `frpc.toml`, since "client needs to set the same value to pass authentication":

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

Both the shared token and OIDC authenticate `frpc` to `frps`; neither authenticates the callers who reach a service you publish through the tunnel. A registered tcp, udp, http, https or tcpmux proxy listens on `proxyBindAddr`, which defaults to the server's `bindAddr` of `0.0.0.0` (as of v0.71.0), so once the proxy is up anyone who can reach that listener reaches the service behind it, exactly as if the app faced a public port directly. An stcp, sudp or xtcp proxy opens no listener of its own on frps. Give the published service its own authentication, or keep the proxy on loopback and front it with an authenticated TLS proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)); a strong `auth.token` protects the tunnel, not the service.

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

REASONED: following block; the cited frp authentication, WireGuard quickstart/Cryptokey Routing, nftables and OpenSSH documentation defines the checks below. This read-only review cannot provision paired tunnel hosts or privileged network/firewall control; the guide records no live run.

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
- frps `bindAddr` default `0.0.0.0` and `bindPort` default `7000`, and an empty `proxyBindAddr` takes `bindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/pkg/config/v1/server.go#L110-L114
- frps TCP proxies listen on `proxyBindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/tcp.go#L76
- frps UDP proxies listen on `proxyBindAddr` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/udp.go#L92-L97
- frps HTTP and HTTPS vhost listeners bind `proxyBindAddr` (L303 and L334), sharing the main listener only when `bindAddr` equals `proxyBindAddr` (L229-L235) (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L303-L321, https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L329-L340 and https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L229-L235
- frps tcpmux HTTP CONNECT listener binds `proxyBindAddr` at `tcpmuxHTTPConnectPort` (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/service.go#L193-L194
- frps stcp and sudp proxies register an in-process visitor listener (`server/visitor/visitor.go` L49-L57, `NewInternalListener`), and xtcp registers with the NAT-hole controller (`server/proxy/xtcp.go` L63); none opens a socket (pinned tag v0.71.0): https://github.com/fatedier/frp/blob/v0.71.0/server/visitor/visitor.go#L49-L57, https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/stcp.go#L43-L46, https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/sudp.go#L43-L46, https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/proxy.go#L202-L215, https://github.com/fatedier/frp/blob/v0.71.0/pkg/util/net/listener.go#L25-L37, https://github.com/fatedier/frp/blob/v0.71.0/server/proxy/xtcp.go#L63 and https://github.com/fatedier/frp/blob/v0.71.0/pkg/nathole/controller.go#L125-L139
- autossh SSH monitoring and restart (pinned commit 90a8c2f0129f6fe19ec26c7d0fdbab4bb468f476, checked October 2026): https://github.com/Autossh/autossh/blob/90a8c2f0129f6fe19ec26c7d0fdbab4bb468f476/README#L25-L26
- Ubuntu Noble ufw manual, status verbose, show raw and IPv4/IPv6 rule visibility (rolling documentation, checked October 2026): https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html
- iproute2 ip-link manual, "ip link show - display device attributes"; the device name "specifies the network device to show." (pinned tag v6.12.0, checked October 2026): https://raw.githubusercontent.com/iproute2/iproute2/v6.12.0/man/man8/ip-link.8.in
- Linux administrative IFF_UP flag (pinned tag v6.8, checked October 2026): https://github.com/torvalds/linux/blob/v6.8/Documentation/networking/operstates.rst#L39-L40
- Linux operational UNKNOWN state (pinned tag v6.8, checked October 2026): https://github.com/torvalds/linux/blob/v6.8/Documentation/networking/operstates.rst#L58-L61
- iproute2 ss manual, UDP/TCP listeners (`-l`: "Display only listening sockets"), numeric output (`-n`: "Do not try to resolve service names.") and process display (`-p`: "Show process using socket.") (pinned tag v6.12.0, checked October 2026): https://raw.githubusercontent.com/iproute2/iproute2/v6.12.0/man/man8/ss.8
- Linux WireGuard UDP socket creation (pinned tag v6.8, checked October 2026): https://github.com/torvalds/linux/blob/v6.8/drivers/net/wireguard/socket.c#L387-L393
- Linux UDP tunnel kernel socket creation (pinned tag v6.8, checked October 2026): https://github.com/torvalds/linux/blob/v6.8/net/ipv4/udp_tunnel_core.c#L17-L19
- frps OIDC verifier skips audience checking when Audience is empty (pinned tag v0.71.0, checked October 2026): https://github.com/fatedier/frp/blob/v0.71.0/pkg/auth/oidc.go#L281-L287
- frps optional token field and default token method (pinned tag v0.71.0, checked October 2026): https://github.com/fatedier/frp/blob/v0.71.0/pkg/config/v1/server.go#L128-L139
- frps login auth-key comparison (pinned tag v0.71.0, checked October 2026; empty-token acceptance is REASONED with the configuration and key derivation): https://github.com/fatedier/frp/blob/v0.71.0/pkg/auth/token.go#L64-L69
- frp auth-key derivation from token and timestamp (pinned tag v0.71.0, checked October 2026; predictable empty-token keys are REASONED from this implementation): https://github.com/fatedier/frp/blob/v0.71.0/pkg/util/util/util.go#L50-L56
