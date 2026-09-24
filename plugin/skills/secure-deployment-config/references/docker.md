# Docker and Compose: exposure, TLS, and authentication

Containers are where accidental exposure happens most. Two Docker behaviours cause it:

1. `ports: - "3000:3000"` (or `-p 3000:3000`) publishes on every host address, `0.0.0.0` and `[::]`.
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

That host-IP restriction is a reliable boundary only on Docker Engine 28.0 and later. Before 28.0, under the default bridge configuration, a neighbour on the same layer-2 segment could reach a port mapped to a loopback address, a remote host could reach a container on a published port despite the host-IP binding, and an unpublished container port was reachable by routing directly to the container; 28.0 fixed all three. Check the running Engine version (`docker version --format '{{.Server.Version}}'`, not the client's); on an older engine, treat the address in a publish string as a convenience, not a boundary, and restrict the port in the `DOCKER-USER` chain below or upstream of the host (a cloud security group or a network ACL), since a host firewall like UFW or firewalld does not reach a published port (see the top of this guide).

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

```bash
docker compose ps                     # project-scoped: only the proxy shows a published (0.0.0.0 or a host IP) binding; review every container on the host, IPv6 included
ss -tulnp                             # host sockets (TCP and UDP); socket visibility varies by Docker version and config, so a socket listing alone does not prove reachability
curl -q -sI http://app.example.com/      # expect a redirect to https://
curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://app.example.com/api  # unauthenticated: expect 401 or 403, never 200 (then confirm an authorized request succeeds)
```

Test from a second machine on a different network where possible; the UFW bypass means testing the firewall from the host itself proves nothing about published ports. The `curl` checks above exercise the proxy's redirect and auth, not the backend, so also probe each restricted host address and published port directly (for example port 3000) from an allowed and a disallowed source, IPv4 and IPv6 separately: a loopback-bound or firewalled backend must show unreachable while the proxy stays reachable.

## Sources (checked September 2026)

- Docker packet filtering and firewalls: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Docker with iptables, for the `DOCKER-USER` chain (processed before Docker's own rules; matches container addresses after DNAT): https://docs.docker.com/engine/network/firewall-iptables/
- Docker Engine 28.0 release notes, for the published-port and loopback-mapping hardening: https://docs.docker.com/engine/release-notes/28/
- Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker port publishing (with no host address, "the Docker daemon publishes ports to all host addresses (0.0.0.0 and [::])"): https://docs.docker.com/engine/network/port-publishing/
