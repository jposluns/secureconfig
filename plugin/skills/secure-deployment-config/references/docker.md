---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "9e9abd4af1684b644bf1bdc1e4cf84a0be849eb0edeff32c1c8de692075071c3",
  "components": {
    "engine": {
      "name": "Docker Engine networking",
      "basis": "unknown",
      "sources": {
        "s351180c6678f": "https://docs.docker.com/engine/network/packet-filtering-firewalls/",
        "s2fecb6db5480": "https://docs.docker.com/engine/network/firewall-iptables/",
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "boundary": {
      "name": "Docker Engine minimum boundary",
      "basis": "28.0",
      "sources": {
        "s50eb099eac95": "https://docs.docker.com/engine/release-notes/28/"
      }
    },
    "compose": {
      "name": "Compose networking",
      "basis": "unknown",
      "sources": {
        "sae565a19136c": "https://docs.docker.com/compose/how-tos/networking/"
      }
    }
  },
  "claims": {
    "publish": {"text": "Omitting the host address publishes 3000:3000 on 0.0.0.0 and [::].", "components": ["engine"], "sources": ["engine:s1e53417c513d"], "status": "REASONED"},
    "host-firewall": {"text": "Docker programs firewall rules directly; UFW or firewalld blocking a host port does not establish published-port isolation.", "components": ["engine"], "sources": ["engine:s351180c6678f"], "status": "REASONED"},
    "private-network": {"text": "Omit app/database ports; Compose peers use service names. The example uses postgres:17 at db:5432; no PostgreSQL source is listed.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "loopback": {"text": "Publish local access as 127.0.0.1:3000:3000; check the running server version, with Engine 28.0 as the stated boundary.", "components": ["engine", "boundary"], "sources": ["engine:s1e53417c513d", "boundary:s50eb099eac95"], "status": "REASONED"},
    "old-loopback": {"text": "Before 28.0, same-L2 neighbours could reach loopback publications under the default bridge configuration.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "old-host-bind": {"text": "Before 28.0, remote hosts could reach published container ports despite the host-IP binding.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "old-unpublished": {"text": "Before 28.0, direct routing could reach unpublished container ports; 28.0 fixed the stated default-bridge exposures.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "upstream": {"text": "Use an upstream security group or network ACL for routable publications and boot-time protection; provider configuration is not sourced here.", "components": ["engine"], "sources": ["engine:s351180c6678f"], "status": "REASONED"},
    "docker-user": {"text": "On the iptables backend, DOCKER-USER precedes Docker accepts; the nftables backend has no such chain. Match NEW traffic from outside the allowed subnet.", "components": ["engine"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480"], "status": "REASONED"},
    "dnat": {"text": "DOCKER-USER sees post-DNAT container destinations; conntrack original destination port and ORIGINAL direction scope a published service.", "components": ["engine"], "sources": ["engine:s2fecb6db5480"], "status": "REASONED"},
    "ipv6": {"text": "Native IPv6 forwarding needs ip6tables; the IPv6-to-IPv4 userland-proxy path terminates on host INPUT and bypasses DOCKER-USER.", "components": ["engine"], "sources": ["engine:s2fecb6db5480", "engine:s1e53417c513d"], "status": "REASONED"},
    "proxy-path": {"text": "Close the userland-proxy path with an explicit publish address, disabled userland proxy or IPv6 INPUT restrictions; test both address families and sources.", "components": ["engine"], "sources": ["engine:s1e53417c513d", "engine:s2fecb6db5480"], "status": "REASONED"},
    "persistence": {"text": "Guide recommends persisting only DOCKER-USER rules after Docker startup, avoiding blanket dynamic-chain saves; startup-unit details lack a direct source.", "components": ["engine"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480"], "status": "REASONED"},
    "tls": {"text": "Example caddy:2 publishes 80:80 and 443:443, mounts Caddyfile read-only and persists data/config, proxying app:3000 with automatic certificates; no Caddy source is listed.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "alternate-entry": {"text": "Cloudflared to http://app:3000, Tailscale or internal self-signed TLS are linked alternatives; no direct vendor sources for these alternatives are listed.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "auth": {"text": "Proxy authentication and human MFA supplement application login; no authentication-provider source is listed.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "secrets": {"text": "Use runtime environment files or Compose secrets, exclude .env from Git, and avoid image ENV/build-argument secrets; no direct secret-handling source is listed.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "workload": {"text": "Use a non-root USER and the linked capability, no-new-privileges, read-only-root and Docker-socket guidance; no workload-control source is listed here.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "database": {"text": "Database TLS and authentication remain necessary for connections from outside the Compose network; database vendor sources are in linked guides.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "verify-publish": {"text": "Compose ps is project-scoped; inventory every host container and TCP/UDP socket, including IPv6. Socket visibility alone does not prove reachability.", "components": ["compose", "engine"], "sources": ["compose:sae565a19136c", "engine:s1e53417c513d"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should redirect to HTTPS; the guide records an expected result, with no direct proxy citation or run.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Unauthenticated HTTPS /api should return 401 or 403, never 200; confirm authorized success separately. The proxy discriminator has no direct source here.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED", "verify": [1]},
    "verify-isolation": {"text": "Probe each restricted host address and publication from allowed/disallowed sources in both families; backend isolation must coexist with proxy reachability.", "components": ["engine"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480", "engine:s1e53417c513d"], "status": "REASONED", "verify": [1]}
  }
}
---
# Docker and Compose: exposure, TLS, and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| publish: Omitting the host address publishes 3000:3000 on 0.0.0.0 and [::]. | Docker Engine networking unknown | REASONED |
| host-firewall: Docker programs firewall rules directly; UFW or firewalld blocking a host port does not establish published-port isolation. | Docker Engine networking unknown | REASONED |
| private-network: Omit app/database ports; Compose peers use service names. The example uses postgres:17 at db:5432; no PostgreSQL source is listed. | Compose networking unknown | REASONED |
| loopback: Publish local access as 127.0.0.1:3000:3000; check the running server version, with Engine 28.0 as the stated boundary. | Docker Engine networking unknown; Docker Engine minimum boundary 28.0 | REASONED |
| old-loopback: Before 28.0, same-L2 neighbours could reach loopback publications under the default bridge configuration. | Docker Engine minimum boundary 28.0 | REASONED |
| old-host-bind: Before 28.0, remote hosts could reach published container ports despite the host-IP binding. | Docker Engine minimum boundary 28.0 | REASONED |
| old-unpublished: Before 28.0, direct routing could reach unpublished container ports; 28.0 fixed the stated default-bridge exposures. | Docker Engine minimum boundary 28.0 | REASONED |
| upstream: Use an upstream security group or network ACL for routable publications and boot-time protection; provider configuration is not sourced here. | Docker Engine networking unknown | REASONED |
| docker-user: On the iptables backend, DOCKER-USER precedes Docker accepts; the nftables backend has no such chain. Match NEW traffic from outside the allowed subnet. | Docker Engine networking unknown | REASONED |
| dnat: DOCKER-USER sees post-DNAT container destinations; conntrack original destination port and ORIGINAL direction scope a published service. | Docker Engine networking unknown | REASONED |
| ipv6: Native IPv6 forwarding needs ip6tables; the IPv6-to-IPv4 userland-proxy path terminates on host INPUT and bypasses DOCKER-USER. | Docker Engine networking unknown | REASONED |
| proxy-path: Close the userland-proxy path with an explicit publish address, disabled userland proxy or IPv6 INPUT restrictions; test both address families and sources. | Docker Engine networking unknown | REASONED |
| persistence: Guide recommends persisting only DOCKER-USER rules after Docker startup, avoiding blanket dynamic-chain saves; startup-unit details lack a direct source. | Docker Engine networking unknown | REASONED |
| tls: Example caddy:2 publishes 80:80 and 443:443, mounts Caddyfile read-only and persists data/config, proxying app:3000 with automatic certificates; no Caddy source is listed. | Compose networking unknown | REASONED |
| alternate-entry: Cloudflared to http://app:3000, Tailscale or internal self-signed TLS are linked alternatives; no direct vendor sources for these alternatives are listed. | Compose networking unknown | REASONED |
| auth: Proxy authentication and human MFA supplement application login; no authentication-provider source is listed. | Compose networking unknown | REASONED |
| secrets: Use runtime environment files or Compose secrets, exclude .env from Git, and avoid image ENV/build-argument secrets; no direct secret-handling source is listed. | Compose networking unknown | REASONED |
| workload: Use a non-root USER and the linked capability, no-new-privileges, read-only-root and Docker-socket guidance; no workload-control source is listed here. | Compose networking unknown | REASONED |
| database: Database TLS and authentication remain necessary for connections from outside the Compose network; database vendor sources are in linked guides. | Compose networking unknown | REASONED |
| verify-publish: Compose ps is project-scoped; inventory every host container and TCP/UDP socket, including IPv6. Socket visibility alone does not prove reachability. | Compose networking unknown; Docker Engine networking unknown | REASONED |
| verify-redirect: HTTP should redirect to HTTPS; the guide records an expected result, with no direct proxy citation or run. | Compose networking unknown | REASONED |
| verify-auth: Unauthenticated HTTPS /api should return 401 or 403, never 200; confirm authorized success separately. The proxy discriminator has no direct source here. | Compose networking unknown | REASONED |
| verify-isolation: Probe each restricted host address and publication from allowed/disallowed sources in both families; backend isolation must coexist with proxy reachability. | Docker Engine networking unknown | REASONED |
<!-- version-basis:end -->

Containers are where accidental exposure happens most. Two Docker behaviours cause it:

1. `ports: - "3000:3000"` (or `-p 3000:3000`) publishes on every host address, `0.0.0.0` and `[::]`, at the time of writing.
2. On Linux, Docker programs iptables/nftables directly, so published ports are reachable **even when UFW or firewalld says the port is blocked**. A `ufw deny 3000` rule does not protect a published container port.

## 1. Publish nothing except the TLS proxy

Bind anything that must be reachable from the host to loopback, and give everything else no `ports:` entry at all; containers on the same Compose network reach each other by service name without published ports.

```yaml
services:
  app:
    build: .
    # no ports: entry; only the proxy is published
  db:
    image: postgres:17
    # no ports: entry; the app reaches it at db:5432 on the internal network
```

Where a host-published port is genuinely needed for local access:

```yaml
    ports:
      - "127.0.0.1:3000:3000"
```

That host-IP restriction requires Docker Engine 28.0 or later, with the firewalld-reload caveat below. Before 28.0, under the default bridge configuration, a neighbour on the same layer-2 segment could reach a port mapped to a loopback address, a remote host could reach a container on a published port despite the host-IP binding, and an unpublished container port was reachable by routing directly to the container if the host's forwarding policy allowed it; 28.0 fixed all three. Check the running Engine version (`docker version --format '{{.Server.Version}}'`, not the client's); on an older engine, treat the address in a publish string as a convenience, not a boundary, and restrict the port in the `DOCKER-USER` chain below or upstream of the host (a cloud security group or a network ACL), since a host firewall like UFW or firewalld does not reach a published port (see the top of this guide).

On Linux, when Docker Engine runs in the host's network namespace with firewalld running, Engine 28.2.x and 28.3.0 through 28.3.2 failed to restore container-address filtering rules after a firewalld reload. A remote host with a route to the bridge network could then reach published ports at container addresses, including loopback-only publications; unpublished ports remained filtered. Where firewalld is used, run Engine 28.3.3 or later, which fixes this regression (CVE-2025-54388, GHSA-x4rx-4gw3-53p4). Rootless Mode and Docker Desktop are unaffected by this regression.

Where a port must be published on a routable interface, because other hosts need it but the whole internet does not, the most reliable restriction is upstream of the host, in a cloud security group or a network ACL: it does not depend on Docker's firewall backend, its userland proxy, or the host's boot order. On the host itself, filter it in the `DOCKER-USER` iptables chain (Docker's iptables backend only; its nftables backend has no such chain), whose rules Docker evaluates before its own accept rules. Match only new connections, so the rule does not also drop the replies to connections your own containers open, which arrive on the same interface and would otherwise lose their outbound access:

```bash
# IPv4, run as root; replace ext_if with your external interface and the subnet with your own
iptables -I DOCKER-USER -i ext_if -m conntrack --ctstate NEW ! -s 192.0.2.0/24 -j DROP
```

This runs after destination NAT, so an ordinary destination match sees a container's internal IP and port, not the published host IP or port; it also covers every published port arriving on that interface, so scope it to one service with conntrack's `--ctorigdstport` and `--ctdir ORIGINAL` if you need to. `iptables` covers IPv4 only. Cover native IPv6 forwarding with an equivalent `ip6tables` `DOCKER-USER` rule, but note a second path: publishing without a host IP on an IPv4-only bridge also makes the port answer on the host's IPv6 addresses through Docker's userland proxy (it maps IPv6 to the container's IPv4). That connection terminates on a host process, so it traverses the host `INPUT` chain, not `FORWARD`, and a `DOCKER-USER` rule (which lives in `FORWARD`) never sees it. Close that path by publishing to a specific address (`-p 127.0.0.1:3000:3000` or a chosen IPv4), disabling the userland proxy, or restricting the host's IPv6 `INPUT`. Probe IPv4 and IPv6 separately, each from an allowed and a disallowed source. Confirm with `sudo iptables -nvL DOCKER-USER`, watching its counters, and by probing the port from a host outside the allowed subnet, expecting a timeout, and one inside it, expecting a connection. The rule does not survive a reboot and is not in place while the host boots; persist just the DOCKER-USER rules with a startup unit ordered after the Docker service, not a blanket `iptables-persistent` save (which also captures Docker's own dynamic chains and can break container networking on the next boot), and where the boot-time window matters, rely on the upstream control.

## 2. Terminate TLS in one proxy container

Caddy is the least configuration ([caddy.md](caddy.md)); nginx ([nginx.md](nginx.md)) and Traefik ([traefik.md](traefik.md)) work the same way. A complete pattern:

```yaml
services:
  app:
    build: .

  caddy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

`Caddyfile`:

```caddyfile
app.example.com {
    reverse_proxy app:3000
}
```

Caddy obtains and renews the certificate automatically ([free-certificates.md](free-certificates.md) explains the ACME requirements). Hosts with no inbound ports but a domain you can put on Cloudflare should use [cloudflare.md](cloudflare.md); run the `cloudflared` connector as a container and point it at `http://app:3000`. Hosts with no domain at all should use [tailscale.md](tailscale.md), or [self-signed.md](self-signed.md) for internal use.

## 3. Authentication and secrets

- The proxy is the natural place for a first authentication gate (basic auth per the proxy guides, or Cloudflare Access); the application still needs its own login for anything multi-user ([authentication.md](authentication.md)). The proxy is also where MFA attaches for human-facing services ([mfa.md](mfa.md)).
- Pass secrets at runtime through environment files or Docker/Compose secrets. Never bake them into the image: `ENV API_KEY=...` in a Dockerfile ships the key to every registry the image touches, and `docker history` shows build arguments.
- Keep `.env` in `.gitignore`, and run containers as a non-root user (`USER` in the Dockerfile) so a compromised app is not root in the container. Non-root is the start, not the whole of workload hardening: dropping capabilities, `--security-opt no-new-privileges`, a read-only root filesystem, and never mounting the Docker socket are in [container-hardening.md](container-hardening.md).
- Databases in containers still need their own TLS and authentication when anything outside the Compose network connects: see [postgresql.md](postgresql.md), [mysql.md](mysql.md), [mongodb.md](mongodb.md), and [redis.md](redis.md).

## 4. Verify

REASONED: publication, redirect, authentication and external isolation checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited Docker networking sources and linked proxy guides; this read-only review has no authorized deployment or external probe hosts.

```bash
docker compose ps                     # project-scoped: only the proxy shows a published (0.0.0.0/[::] or a host IP) binding; review every container on the host, IPv6 included
ss -tulnp                             # host sockets (TCP and UDP); socket visibility varies by Docker version and config, so a socket listing alone does not prove reachability
curl -q -sI http://app.example.com/      # expect a redirect to https://
curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://app.example.com/api  # unauthenticated: expect 401 or 403, never 200 (then confirm an authorized request succeeds)
```

Test from a second machine on a different network where possible; the UFW bypass means testing the firewall from the host itself proves nothing about published ports. The `curl` checks above exercise the proxy's redirect and auth, not the backend, so also probe each restricted host address and published port directly (for example port 3000) from an allowed and a disallowed source, IPv4 and IPv6 separately: a loopback-bound or firewalled backend must show unreachable while the proxy stays reachable.

REASONED: this firewalld reload check follows the Impact section of GHSA-x4rx-4gw3-53p4 and the pinned v28.3.3 rule-restoration source. It has not been demonstrated here because the authoring environment has no Docker runtime, firewalld or external test host. For a loopback-published HTTP backend using default NAT bridge filtering, confirm that the backend answers locally. From a second host with a route through the Docker host to the bridge subnet, run `curl -q -g --noproxy '*' --connect-timeout 3 --max-time 5 -v http://172.17.0.2:3000/`, replacing the address and port with the actual container address and container port. Repeat with a fresh connection after running `sudo firewall-cmd --reload` on the Docker host. Without another control masking the regression, an affected host changes from blocked to connectable; a fixed host remains blocked. Any successful TCP connection, including an HTTP 401 or 403 response, demonstrates reachability. A failed probe alone does not establish that the Engine is patched: confirm the route, target and backend health. Repeat for configured IPv6 addresses and the restricted host-address publications, and confirm that the TLS proxy remains reachable.

## Sources (checked September 2026)

- Docker packet filtering and firewalls: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Docker with iptables, for the `DOCKER-USER` chain (processed before Docker's own rules; matches container addresses after DNAT): https://docs.docker.com/engine/network/firewall-iptables/
- Docker Engine 28.0 release notes, for the published-port and loopback-mapping hardening: https://docs.docker.com/engine/release-notes/28/
- Docker Engine 28.3.3 security fix: https://docs.docker.com/engine/release-notes/28/#2833 and affected-version advisory: https://github.com/moby/moby/security/advisories/GHSA-x4rx-4gw3-53p4
- Moby v28.3.3, `reapplyPerPortIptables` restores endpoint rules after firewalld reload: https://raw.githubusercontent.com/moby/moby/v28.3.3/libnetwork/drivers/bridge/port_mapping_linux.go
- Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker port publishing (with no host address, "the Docker daemon publishes ports to all host addresses (0.0.0.0 and [::])"): https://docs.docker.com/engine/network/port-publishing/
