# Docker and Compose: exposure, TLS, and authentication

Written against Docker Engine minimum boundary 28.0, Moby Docker service unit v28.3.3, Docker firewalld reload fix 28.3.3, systemd unit ordering v262, Git ignore rules v2.49.0, PostgreSQL 17, Caddy v2.11.4, and nginx authentication source release-1.26.3, plus 3 more recorded bases; 8 further sources are pinned to a commit and 8 carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 26 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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

As this guide's assessment, where a port must be published on a routable interface, because other hosts need it but the whole internet does not, the most reliable restriction is upstream of the host, in a cloud security group or a network ACL: it does not depend on Docker's firewall backend, its userland proxy, or the host's boot order. See [cloud-firewalls.md](cloud-firewalls.md) for sourced AWS security-group, Google Cloud VPC firewall and Azure NSG rules; network-ACL configuration is not directly sourced here. On the host itself, filter it in the `DOCKER-USER` iptables chain (Docker's iptables backend only; its nftables backend has no such chain), whose rules Docker evaluates before its own accept rules. Match only new connections, so the rule does not also drop the replies to connections your own containers open, which arrive on the same interface and would otherwise lose their outbound access:

```bash
# IPv4, run as root; replace ext_if with your external interface and the subnet with your own
iptables -I DOCKER-USER -i ext_if -m conntrack --ctstate NEW ! -s 192.0.2.0/24 -j DROP
```

This runs after destination NAT, so an ordinary destination match sees a container's internal IP and port, not the published host IP or port; it also covers every published port arriving on that interface, so scope it to one service with conntrack's `--ctorigdstport` and `--ctdir ORIGINAL` if you need to. As this guide's reasoning, `iptables` covers IPv4 only. Cover native IPv6 forwarding with an equivalent `ip6tables` `DOCKER-USER` rule, but note a second path: publishing without a host IP on an IPv4-only bridge with `--userland-proxy=true` (the default) also makes the port answer on the host's IPv6 addresses through Docker's userland proxy (it maps IPv6 to the container's IPv4). As this guide's reasoning, that connection terminates on a host process, so it traverses the host `INPUT` chain, not `FORWARD`, and a `DOCKER-USER` rule (which lives in `FORWARD`) never sees it. Close that path by publishing to a specific address (`-p 127.0.0.1:3000:3000` or a chosen IPv4), disabling the userland proxy, or restricting the host's IPv6 `INPUT`. Probe IPv4 and IPv6 separately, each from an allowed and a disallowed source. Confirm with `sudo iptables -nvL DOCKER-USER`, watching its counters, and by probing the port from a host outside the allowed subnet, expecting a timeout, and one inside it, expecting a connection. As this guide's assessment, the rule does not survive a reboot and is not in place while the host boots; persist just the DOCKER-USER rules with a startup unit ordered after the Docker service, not a blanket `iptables-persistent` save (which, as this guide's assessment, also captures Docker's own dynamic chains and can break container networking on the next boot), and where the boot-time window matters, rely on the upstream control.

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

Caddy obtains and renews the certificate automatically ([free-certificates.md](free-certificates.md) explains the ACME requirements). As this guide's recommendation, hosts with no inbound ports but a domain you can put on Cloudflare should use [cloudflare.md](cloudflare.md); run the `cloudflared` connector as a container on the app's Compose network and point it at `http://app:3000`. As this guide's recommendation, hosts with no domain at all should use [tailscale.md](tailscale.md) (Serve for private tailnet access or Funnel for public access), or [self-signed.md](self-signed.md) for internal use. Docker documents service-name lookup on the shared Compose network; the `http://app:3000` origin is this guide's inference from that lookup and [cloudflare.md](cloudflare.md)'s HTTP origin example, while the fetched Cloudflare origin parameters show an HTTPS service URL rather than this literal HTTP value. This guide does not show the tunnel-token setup; [cloudflare.md](cloudflare.md) gives the protected `--token-file` path.

## 3. Authentication and secrets

- As this guide's assessment, the proxy is the natural place for a first authentication gate (basic auth per the proxy guides, or Cloudflare Access); the application still needs its own login for anything multi-user ([authentication.md](authentication.md)). The proxy is also where MFA attaches for human-facing services ([mfa.md](mfa.md)): Cloudflare Access policies can require a second factor, and an Authelia portal can handle authentication behind Caddy `forward_auth`, nginx `auth_request` or Traefik `forwardAuth`. Require MFA in the governing policy or portal; as this guide's assessment, basic auth alone is single-factor.
- Pass secrets at runtime through environment files or Docker/Compose secrets. Docker's Compose documentation advises against using environment variables to pass sensitive information such as passwords into containers and recommends secrets instead, noting that environment variables are often available to all processes, that access to them can be hard to track, and that they can be printed in logs when debugging errors; its `env_file` page also describes a separate environment file as a more organized and secure way to manage sensitive information, because the file need not sit in the project root. Offering environment files here is this guide's advice, and as this guide's assessment they are the weaker of the two runtime methods named here. Compose mounts each secret as a file under `/run/secrets/`, named after the secret, supports secrets on Linux containers only, and grants access per service. Docker Swarm secrets are available only to swarm services, not to standalone containers; Docker documents them as encrypted in transit and at rest in the swarm, accessible only to services granted explicit access while their tasks run, and mounted decrypted in an in-memory filesystem, by default under `/run/secrets/` in Linux containers. Docker also documents that a container's environment is not set until the service configuration has an explicit entry for it, such as the `environment` or `env_file` attribute, and that the `.env` file in the project directory, the default method for setting variables, defines variables for interpolation in the Compose file, which an `environment` entry such as `DEBUG=${DEBUG}` can then pass into the container. As this guide's reasoning, a value in that `.env` file therefore reaches a container only through such an entry or an `env_file` entry that names the file. Never bake secrets into the image. Never put secrets in Dockerfile `ENV` or `ARG`: Docker documents that both are exposed in the final image; `ENV` also persists in containers from the image, and build arguments may persist in image metadata, provenance attestations and image history. As this guide's assessment, baking a key into an image ships it to every registry the image touches. `docker image history` shows the image's history, including creation commands; as this guide's assessment, the cited reference does not establish that every argument value is shown. For build-time secrets, use a temporary secret mount for the build instruction and do not copy or print the secret into the image.
- Keep `.env` in `.gitignore` (this guide's advice; Git ignores matching untracked files, while already tracked files are unaffected), and run containers as a non-root user (`USER` in the Dockerfile); as this guide's assessment, this means a compromised app is not root in the container. As this guide's advice, non-root is the start, not the whole of workload hardening: dropping capabilities (`cap_drop`), `--security-opt no-new-privileges` (or Compose `security_opt`), a read-only root filesystem (Compose `read_only`), and never mounting the Docker socket are in [container-hardening.md](container-hardening.md). Docker documents these option names, that only trusted users should control the daemon, and that Unix permissions can limit access to its control socket; the linked guide's hardening consequences, including the mounted-socket path, remain this guide's assessment.
- Databases in containers still need their own TLS and authentication when anything outside the Compose network connects: see [postgresql.md](postgresql.md), [mysql.md](mysql.md), [mongodb.md](mongodb.md), and [redis.md](redis.md).

## 4. Verify

REASONED: publication, redirect, authentication and external isolation checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited Docker networking sources and linked proxy guides; this read-only review has no authorized deployment or external probe hosts. For the unauthenticated API probe, expect 401 from Caddy or nginx basic auth; Caddy `forward_auth` admits auth-service 2xx, but its rejection status is not established by the fetched lines. Expect 401/403 from nginx `auth_request`; the cited Authelia nginx configuration converts its 401 to a 302 login redirect. Traefik `forwardAuth` passes through its auth service's non-2xx status, including a login redirect; Traefik `basicAuth` calls `RequireAuth`, whose response the fetched lines do not show, so 401 is this guide's expectation rather than a status established by the fetched middleware. For Cloudflare Access, this guide expects a 302 login redirect in the configuration described in [cloudflare.md](cloudflare.md); the fetched Cloudflare lines do not establish that status. A 3xx passes only when its printed location is the gate's own login portal (for Cloudflare Access, your team's `*.cloudflareaccess.com`), never the application's own login. The command fails on any 2xx; any status other than the gate's expected rejection or a 3xx to its portal is not a pass; and an authorized request must succeed separately.

```bash
docker compose ps                     # project-scoped: only the proxy shows a published (0.0.0.0/[::] or a host IP) binding; review every container on the host, IPv6 included
ss -tulnp                             # host sockets (TCP and UDP); socket visibility varies by Docker version and config, so a socket listing alone does not prove reachability
curl -q -sI http://app.example.com/      # expect a redirect to https:// with Caddy automatic HTTPS, or after configuring nginx or Traefik to redirect
( set -o pipefail; curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code} loc=%{redirect_url}\n' https://app.example.com/api | awk '{ print; if ($1 ~ /^http=2/) { print "FAIL: unauthenticated /api returned " substr($1, 6); exit 1 } }' )  # unauthenticated: inspect the gate's rejection and portal location; then confirm an authorized request succeeds
```

REASONED: preceding block; publication and socket inventory, HTTPS redirect, unauthenticated API rejection and authorized API success follow the cited Docker networking sources and linked proxy guides, as do the external isolation probes this paragraph describes; no Docker runtime or external probe hosts are available, and no exposed/fixed result is recorded. Test from a second machine on a different network where possible; the UFW bypass means testing the firewall from the host itself proves nothing about published ports. The `curl` checks above exercise the proxy's redirect and auth, not the backend, so also probe each restricted host address and published port directly (for example port 3000) from an allowed and a disallowed source, IPv4 and IPv6 separately: a loopback-bound or firewalled backend must show unreachable while the proxy stays reachable.

REASONED: this firewalld reload check follows the Impact section of GHSA-x4rx-4gw3-53p4 and the pinned v28.3.3 rule-restoration source. It has not been demonstrated here because the authoring environment has no Docker runtime, firewalld or external test host. For a loopback-published HTTP backend using default NAT bridge filtering, confirm that the backend answers locally. From a second host with a route through the Docker host to the bridge subnet, run `curl -q -g --noproxy '*' --connect-timeout 3 --max-time 5 -v http://172.17.0.2:3000/`, replacing the address and port with the actual container address and container port. Repeat with a fresh connection after running `sudo firewall-cmd --reload` on the Docker host. Without another control masking the regression, an affected host changes from blocked to connectable; a fixed host remains blocked. Any successful TCP connection, including an HTTP 401 or 403 response, demonstrates reachability. A failed probe alone does not establish that the Engine is patched: confirm the route, target and backend health. Repeat for configured IPv6 addresses and the restricted host-address publications, and confirm that the TLS proxy remains reachable.

## Sources (checked September 2026)

- Docker build variables (`ENV` persists in containers; build arguments may persist in metadata, provenance and history), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/variables.md#L17-L52
- Docker build secrets (temporary mounts for build instructions), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/secrets.md#L13-L22
- Docker image history command (image history and creation-command output), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118
- Docker Compose secrets (environment-variable risks, file under `/run/secrets/`, Linux containers only, per-service access), at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/use-secrets.md#L16-L28
- Docker Compose container environment (explicit entry required; advice against environment variables for sensitive information), at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/set-environment-variables.md#L11-L15
- Docker Compose `env_file` attribute and separate environment files, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/set-environment-variables.md#L61-L71
- Docker Compose `.env` file for interpolation in the project directory, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/variable-interpolation.md#L78-L80
- Docker Compose `.env` variable referenced in the `environment` attribute, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/variable-interpolation.md#L105-L117
- Docker Swarm secrets (swarm services only, encrypted in transit and at rest, explicit access), at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/swarm/secrets.md#L11-L34
- Docker Swarm secret mount in an in-memory filesystem under `/run/secrets/`, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/swarm/secrets.md#L87-L92
- Git v2.49.0 ignore rules for untracked and tracked files (checked October 2026): https://github.com/git/git/blob/v2.49.0/Documentation/gitignore.adoc#L15-L18
- Docker Dockerfile `USER` instruction, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/_vendor/github.com/moby/buildkit/frontend/dockerfile/docs/reference.md#L2448-L2463
- Docker Compose `cap_drop` option, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L224-L233
- Docker Compose `read_only` option, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L1892-L1894
- Docker Compose `security_opt` and `no-new-privileges` spellings, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L2008-L2021
- Docker run `--security-opt no-new-privileges`, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L2495-L2502
- Docker daemon control-socket access and host filesystem control, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112
- Docker iptables and ip6tables daemon options, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/firewall-iptables.md#L8-L15
- Docker iptables DOCKER-USER and FORWARD chains, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/firewall-iptables.md#L17-L42
- Docker IPv6-to-IPv4 userland-proxy mapping, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/port-publishing.md#L60-L62
- Docker port publishing with an explicit host address, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/port-publishing.md#L33-L38
- Docker firewall rules and warning against modifying Docker-created rules, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L11-L15
- Moby Docker service unit, at v28.3.3 (checked October 2026): https://github.com/moby/moby/blob/v28.3.3/contrib/init/systemd/docker.service#L1-L9
- systemd After= unit ordering, at v262 (checked October 2026): https://github.com/systemd/systemd/blob/v262/man/systemd.unit.xml#L826-L838
- Docker packet filtering and firewalls: https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Docker with iptables, for the `DOCKER-USER` chain (processed before Docker's own rules; matches container addresses after DNAT): https://docs.docker.com/engine/network/firewall-iptables/
- Docker Engine 28.0 release notes, for the published-port and loopback-mapping hardening: https://docs.docker.com/engine/release-notes/28/
- Docker Engine 28.3.3 security fix: https://docs.docker.com/engine/release-notes/28/#2833 and affected-version advisory (OSV copy of the July 2025 Moby advisory): https://osv.dev/vulnerability/GHSA-x4rx-4gw3-53p4
- Moby 28.3.3 (pinned tag v28.3.3), `reapplyPerPortIptables` restores endpoint rules after firewalld reload: https://raw.githubusercontent.com/moby/moby/v28.3.3/libnetwork/drivers/bridge/port_mapping_linux.go
- Compose networking: https://docs.docker.com/compose/how-tos/networking/
- Docker port publishing (with no host address, "the Docker daemon publishes ports to all host addresses (0.0.0.0 and [::])"): https://docs.docker.com/engine/network/port-publishing/
- PostgreSQL 17 connection settings and default TCP port (checked October 2026): https://www.postgresql.org/docs/17/runtime-config-connection.html
- Caddy image fba2853501d36e8a72f946ac8cb7ff64d07e48f2 data/config paths, exposed ports and Caddyfile command (checked October 2026): https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L44-L45, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L56-L59, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L63
- Caddy v2.11.4 automatic certificate management and reverse_proxy syntax (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L67, https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L60
- Caddy v2.11.4 authentication handler and 401 rejection (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/caddyauth.go#L84-L120
- Caddy v2.11.4 basic-auth missing-credential path (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/basicauth.go#L142-L163
- Caddy v2.11.4 forward_auth accepted-response handler (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/forwardauth/caddyfile.go#L174-L194
- Caddy v2.11.4 automatic redirect setup (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L234-L240
- Caddy v2.11.4 HTTPS redirect route (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L544-L575
- nginx release-1.26.3 missing basic-auth credentials (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_basic_module.c#L122-L129
- nginx release-1.26.3 basic-auth 401 challenge (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_basic_module.c#L317-L348
- nginx release-1.26.3 auth_request status handling (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_request_module.c#L135-L182
- Traefik v3.5.0 basicAuth failure path (checked October 2026): https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/basic_auth.go#L67-L99
- Traefik v3.5.0 forwardAuth keeps the auth service redirect (checked October 2026): https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/forward.go#L93-L99
- Traefik v3.5.0 forwardAuth rejection status passthrough (checked October 2026): https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/forward.go#L233-L262
- Cloudflare Access MFA policy enforcement (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L17-L85
- Cloudflare Access self-hosted application protection (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54
- Authelia v4.39.28 supported proxy integration (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L32
- Authelia v4.39.28 nginx portal redirect (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L537-L541
- AWS security-group rules (rolling reference reused from `cloud-firewalls.md`; not rechecked here): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Google Cloud VPC firewall rules (rolling reference reused from `cloud-firewalls.md`; not rechecked here): https://docs.cloud.google.com/firewall/docs/using-firewalls
- Azure NSG rule properties (rolling reference reused from `cloud-firewalls.md`; not rechecked here): https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get
- cloudflared 2026.9.3 tunnel daemon without firewall openings (checked October 2026): https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L1-L5
- cloudflared 2026.9.3 Docker image (checked October 2026): https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L26-L33
- cloudflared 2026.9.3 container entry point (checked October 2026): https://github.com/cloudflare/cloudflared/blob/2026.9.3/Dockerfile#L40-L42
- Cloudflare Tunnel origin service URL example at c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L31-L49
- Cloudflare Tunnel published application domain prerequisite at c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel.mdx#L27-L37
- Docker Compose service-name lookup at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/networking.md#L13-L17
- Tailscale Serve private tailnet entry (rolling reference reused from `tailscale.md`; not rechecked here): https://tailscale.com/kb/1242/tailscale-serve
- Tailscale Funnel public entry (rolling reference reused from `tailscale.md`; not rechecked here): https://tailscale.com/kb/1223/funnel
- OpenSSL documentation index (rolling reference reused from `self-signed.md`; not rechecked here): https://docs.openssl.org/


<!-- version-basis:start -->
## About the AI assistant section below

The rest of this file is generated by the repository's tooling and written for AI assistants rather than for people. It records the versions this guide was written against, the guide's claims with a status for each (demonstrated by a check that ran, or reasoned from the cited sources), and the mapping from each claim to its sources. You are welcome to read it, but it is dense and can be hard to take in.

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/docker.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- boundary: Docker Engine minimum boundary (28.0)
- moby-unit: Moby Docker service unit (v28.3.3)
- reload: Docker firewalld reload fix (28.3.3)
- docker-build: Docker build and image history documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- docker-secrets: Docker runtime secrets and environment documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- engine: Docker Engine networking (unknown)
- engine-pinned: Docker Engine networking documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- compose: Compose networking (unknown)
- docker-workload: Docker workload documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- reload-advisory: Docker firewalld reload advisory (unknown)
- compose-pinned: Docker Compose networking documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- systemd-unit: systemd unit ordering (v262)
- git-ignore: Git ignore rules (v2.49.0)
- postgresql: PostgreSQL (17)
- caddy-image: Caddy image (fba2853501d36e8a72f946ac8cb7ff64d07e48f2)
- caddy: Caddy (v2.11.4)
- nginx-auth: nginx authentication source (release-1.26.3)
- traefik-auth: Traefik authentication source (v3.5.0)
- cloudflare-access: Cloudflare Access documentation (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- authelia-proxy: Authelia proxy integration (v4.39.28)
- aws-firewall: AWS security group rules (unknown)
- gcp-firewall: Google Cloud VPC firewall rules (unknown)
- azure-firewall: Azure network security group rules (unknown)
- cloudflared-image: cloudflared container image (2026.9.3)
- cloudflare-tunnel: Cloudflare Tunnel documentation (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- tailscale-entry: Tailscale entry documentation (unknown)
- self-signed-entry: OpenSSL documentation (rolling) (unknown)

Claims (full source mapping in the JSON block below):

- publish (REASONED; engine): Omitting the host address publishes 3000:3000 on 0.0.0.0 and [::].
- host-firewall (REASONED; engine): Docker programs firewall rules directly; UFW or firewalld blocking a host port does not establish published-port isolation.
- private-network (REASONED; compose, postgresql): Omit app/database ports; Compose peers use service names. The example uses postgres:17 at db:5432.
- loopback (REASONED; engine, boundary, reload, reload-advisory): Publish local access as 127.0.0.1:3000:3000; check the running server version. Engine 28.0 is the minimum boundary, with 28.3.3 or later required where firewalld is used.
- old-loopback (REASONED; boundary): Before 28.0, same-L2 neighbours could reach loopback publications under the default bridge configuration.
- old-host-bind (REASONED; boundary): Before 28.0, remote hosts could reach published container ports despite the host-IP binding.
- old-unpublished (REASONED; boundary): Before 28.0, direct routing could reach unpublished container ports; 28.0 fixed the stated default-bridge exposures.
- upstream (REASONED; engine, aws-firewall, gcp-firewall, azure-firewall): Use an upstream security group or network ACL for routable publications and boot-time protection. AWS security groups, Google Cloud VPC firewall rules and Azure NSGs have rolling sources; network-ACL configuration and boot-time independence remain this guide's assessment.
- docker-user (REASONED; engine): On the iptables backend, DOCKER-USER precedes Docker accepts; the nftables backend has no such chain. Match NEW traffic from outside the allowed subnet.
- dnat (REASONED; engine): DOCKER-USER sees post-DNAT container destinations; conntrack original destination port and ORIGINAL direction scope a published service.
- ipv6 (REASONED; engine, engine-pinned): As this guide's reasoning, native IPv6 forwarding needs ip6tables; Docker documents IPv6-to-IPv4 userland-proxy mapping when no host IP is given, the bridge is IPv4-only and `--userland-proxy=true` (the default), and places DOCKER-USER in FORWARD. As this guide's reasoning, the proxy path terminates on host INPUT and bypasses DOCKER-USER.
- proxy-path (REASONED; engine, engine-pinned): Close the userland-proxy path with an explicit publish address, disabled userland proxy or IPv6 INPUT restrictions; test both address families and sources. Docker documents the explicit-address option and conditional userland-proxy mapping; the INPUT restriction and probes are this guide's reasoning and advice.
- persistence (REASONED; engine, engine-pinned, moby-unit, systemd-unit): As this guide's advice, persist only DOCKER-USER rules after Docker startup, avoiding blanket dynamic-chain saves. Moby identifies docker.service and systemd documents After= ordering; as this guide's assessment, rule non-persistence, the boot-time gap, what iptables-persistent captures and its potential to break container networking have no direct source here.
- tls (REASONED; compose, caddy-image, caddy): Example caddy:2 publishes 80:80 and 443:443, mounts Caddyfile read-only and persists data/config, proxying app:3000 with automatic certificates.
- alternate-entry (REASONED; compose, cloudflared-image, cloudflare-tunnel, compose-pinned, tailscale-entry, self-signed-entry): As this guide's advice, hosts with no inbound ports and a domain they can put on Cloudflare use a cloudflared container, while hosts with no domain at all use Tailscale or internal self-signed TLS. Cloudflare documents a tunnel daemon that needs no firewall openings, a container image, an HTTPS origin service URL and a domain prerequisite; Docker documents Compose service-name lookup. The http://app:3000 origin target on a shared Compose network is this guide's inference, not shown literally by the fetched Cloudflare lines. The tunnel-token setup is not shown here; the Tailscale and OpenSSL references are rolling, and the self-signed fallback remains this guide's advice.
- auth (REASONED; compose, caddy, nginx-auth, traefik-auth, cloudflare-access, authelia-proxy): As this guide's assessment, proxy authentication and human MFA supplement application login. Caddy and nginx basic authentication reject missing credentials; nginx auth_request returns 401/403; Traefik basicAuth calls RequireAuth and forwardAuth passes through non-2xx; Cloudflare Access policies can require MFA, and Authelia can sit behind the proxy. Require MFA in the governing policy or portal; as this guide's assessment, basic auth alone is single-factor. The Caddy forward_auth rejection status, exact Traefik basicAuth status and Cloudflare Access anonymous status are not established by these fetched lines.
- secrets (REASONED; compose, docker-build, docker-secrets, git-ignore): Use runtime environment files (this guide's advice; weaker, as its assessment) or Compose secrets under /run/secrets (Linux only) or Swarm secrets (swarm services only); as this guide's advice, keep .env in .gitignore (tracked files are unaffected). Never put secrets in Dockerfile ENV/ARG; use temporary build secret mounts; as its assessment, never bake secrets into images or copy or print build secrets into them, and history is not shown to list every argument value.
- workload (REASONED; compose, git-ignore, docker-workload): Keep .env in .gitignore, which ignores matching untracked files but not tracked files. Use a non-root Dockerfile USER; as this guide's assessment, a compromised app then is not root in the container. Drop capabilities, use no-new-privileges and a read-only root filesystem, and never mount the Docker socket. Docker sources establish the option names, that only trusted users should control the daemon, and that Unix permissions can limit access to its control socket; the linked guide's hardening consequences, including the mounted-socket path, remain this guide's assessment.
- database (REASONED; compose): Database TLS and authentication remain necessary for connections from outside the Compose network; database vendor sources are in linked guides.
- verify-publish (REASONED; compose, engine): Compose ps is project-scoped; inventory every host container and TCP/UDP socket, including IPv6. Socket visibility alone does not prove reachability.
- verify-redirect (REASONED; compose, caddy): Verify that HTTP redirects to HTTPS: Caddy v2.11.4 configures an automatic HTTPS redirect; as this guide's configuration-dependent expectation, nginx and Traefik require a configured redirect. This is an expectation, not an observed deployment result.
- verify-auth (REASONED; compose, caddy, nginx-auth, traefik-auth, authelia-proxy, cloudflare-access): Verify unauthenticated HTTPS /api rejection with printed status and redirect location; the probe itself fails on any 2xx. A 3xx passes only when the location is the gate's own login portal, never the application's own login; verify authorized success separately. Caddy basic auth and nginx auth_basic expect 401; Caddy forward_auth admits auth-service 2xx, but its rejection status is not established by the fetched lines. nginx auth_request returns 401 or 403, while the cited Authelia nginx configuration turns 401 into 302 to its portal. Traefik forwardAuth passes through a rejecting auth service's status, including a login redirect; Traefik basicAuth's 401 is this guide's expectation because the fetched code calls RequireAuth, whose response these lines do not show. Cloudflare Access's anonymous 302 login redirect is this guide's assessment per cloudflare.md, not established by the fetched Cloudflare lines.
- verify-isolation (REASONED; engine): Probe each restricted host address and publication from allowed/disallowed sources in both families; backend isolation must coexist with proxy reachability.
- firewalld-reload (REASONED; reload, reload-advisory): Engine 28.2.x and 28.3.0 through 28.3.2 fail to restore container-address filtering after firewalld reload; 28.3.3 fixes CVE-2025-54388 (GHSA-x4rx-4gw3-53p4).
- firewalld-scope (REASONED; reload, reload-advisory): The regression affects Linux Engine in the host network namespace with firewalld: routed remote hosts can reach published container ports, including loopback publications; unpublished ports stay filtered. Rootless Mode and Docker Desktop are unaffected.
- verify-firewalld-reload (REASONED; reload, reload-advisory): Confirm local backend health, then curl the container address from a second host with a bridge-subnet route before and after sudo firewall-cmd --reload. Without masking controls, affected hosts change from blocked to connectable; fixed hosts stay blocked. Any TCP connection, including HTTP 401/403, shows reachability; failure alone does not prove patching. Check route, target, IPv6, restricted host publications and continued proxy reachability.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "a1e8744915744f9595b2c2c207ef00d91b7262897e0d15c73446a0e62068f0cc",
  "components": {
    "boundary": {
      "name": "Docker Engine minimum boundary",
      "basis": "28.0",
      "sources": {
        "s50eb099eac95": "https://docs.docker.com/engine/release-notes/28/"
      }
    },
    "moby-unit": {
      "name": "Moby Docker service unit",
      "basis": "v28.3.3",
      "sources": {
        "s6aa0d2fb34cf": "https://github.com/moby/moby/blob/v28.3.3/contrib/init/systemd/docker.service#L1-L9"
      }
    },
    "reload": {
      "name": "Docker firewalld reload fix",
      "basis": "28.3.3",
      "sources": {
        "s567a65842b29": "https://docs.docker.com/engine/release-notes/28/#2833",
        "seaf4197aafaa": "https://raw.githubusercontent.com/moby/moby/v28.3.3/libnetwork/drivers/bridge/port_mapping_linux.go"
      }
    },
    "docker-build": {
      "name": "Docker build and image history documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "sd8afa286c173": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/variables.md#L17-L52",
        "s07e00829f121": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/secrets.md#L13-L22",
        "s6283b172a5c6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118"
      }
    },
    "docker-secrets": {
      "name": "Docker runtime secrets and environment documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "s81d857265c7c": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/use-secrets.md#L16-L28",
        "sd9dc0a9c4c0d": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/set-environment-variables.md#L11-L15",
        "sb9dd4c26439c": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/set-environment-variables.md#L61-L71",
        "s65e97e494341": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/variable-interpolation.md#L78-L80",
        "s04a382307f48": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/environment-variables/variable-interpolation.md#L105-L117",
        "s05ba8904bab4": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/swarm/secrets.md#L11-L34",
        "s9c3b613c7e5a": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/swarm/secrets.md#L87-L92"
      }
    },
    "engine": {
      "name": "Docker Engine networking",
      "basis": "unknown",
      "sources": {
        "s351180c6678f": "https://docs.docker.com/engine/network/packet-filtering-firewalls/",
        "s2fecb6db5480": "https://docs.docker.com/engine/network/firewall-iptables/",
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "engine-pinned": {
      "name": "Docker Engine networking documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "sd22373a822c3": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/firewall-iptables.md#L8-L15",
        "s024cfadb4bb8": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/firewall-iptables.md#L17-L42",
        "s1c82ff316a7e": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/port-publishing.md#L60-L62",
        "sb3dacfbaf7e1": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/port-publishing.md#L33-L38",
        "sc244607b20e4": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L11-L15"
      }
    },
    "compose": {
      "name": "Compose networking",
      "basis": "unknown",
      "sources": {
        "sae565a19136c": "https://docs.docker.com/compose/how-tos/networking/"
      }
    },
    "docker-workload": {
      "name": "Docker workload documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "s2fa3b3cd70e6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/_vendor/github.com/moby/buildkit/frontend/dockerfile/docs/reference.md#L2448-L2463",
        "s8000f273883e": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L224-L233",
        "sb94d21792cd4": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L1892-L1894",
        "s28ce092b2589": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/reference/compose-file/services.md#L2008-L2021",
        "s738280652c95": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L2495-L2502",
        "secebea1a69ab": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112"
      }
    },
    "reload-advisory": {
      "name": "Docker firewalld reload advisory",
      "basis": "unknown",
      "sources": {
        "s424f3c4f8285": "https://osv.dev/vulnerability/GHSA-x4rx-4gw3-53p4"
      }
    },
    "compose-pinned": {
      "name": "Docker Compose networking documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "seb7ab83ee20e": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/compose/how-tos/networking.md#L13-L17"
      }
    },
    "systemd-unit": {
      "name": "systemd unit ordering",
      "basis": "v262",
      "sources": {
        "s71dce3a476cd": "https://github.com/systemd/systemd/blob/v262/man/systemd.unit.xml#L826-L838"
      }
    },
    "git-ignore": {
      "name": "Git ignore rules",
      "basis": "v2.49.0",
      "sources": {
        "s5f377f0fdbd8": "https://github.com/git/git/blob/v2.49.0/Documentation/gitignore.adoc#L15-L18"
      }
    },
    "postgresql": {
      "name": "PostgreSQL",
      "basis": "17",
      "sources": {
        "s44c2e898e585": "https://www.postgresql.org/docs/17/runtime-config-connection.html"
      }
    },
    "caddy-image": {
      "name": "Caddy image",
      "basis": "fba2853501d36e8a72f946ac8cb7ff64d07e48f2",
      "sources": {
        "sbbb7746f7545": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L44-L45",
        "sb126b380b9cf": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L56-L59",
        "seea3a2adc92a": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L63"
      }
    },
    "caddy": {
      "name": "Caddy",
      "basis": "v2.11.4",
      "sources": {
        "s5520ee906a7f": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L67",
        "sfa5c7dc047dc": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L60",
        "s32fb97ff942b": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/caddyauth.go#L84-L120",
        "sd698097c71f4": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/basicauth.go#L142-L163",
        "s87dc43d9819d": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/forwardauth/caddyfile.go#L174-L194",
        "sd267d297d661": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L234-L240",
        "s32a5119bce5b": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L544-L575"
      }
    },
    "nginx-auth": {
      "name": "nginx authentication source",
      "basis": "release-1.26.3",
      "sources": {
        "s44cecab17a23": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_basic_module.c#L122-L129",
        "s91b029555086": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_basic_module.c#L317-L348",
        "s3df6e64cd6a3": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_request_module.c#L135-L182"
      }
    },
    "traefik-auth": {
      "name": "Traefik authentication source",
      "basis": "v3.5.0",
      "sources": {
        "s5f9a13d720c8": "https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/basic_auth.go#L67-L99",
        "sfe588a6dd6a3": "https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/forward.go#L93-L99",
        "sbc20b015d928": "https://github.com/traefik/traefik/blob/v3.5.0/pkg/middlewares/auth/forward.go#L233-L262"
      }
    },
    "cloudflare-access": {
      "name": "Cloudflare Access documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s6f6104362214": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L17-L85",
        "s7cafe1b17afd": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54"
      }
    },
    "authelia-proxy": {
      "name": "Authelia proxy integration",
      "basis": "v4.39.28",
      "sources": {
        "s5ca02c783843": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L32",
        "s31a83fce2b6e": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L537-L541"
      }
    },
    "aws-firewall": {
      "name": "AWS security group rules",
      "basis": "unknown",
      "sources": {
        "s5594f61a25d6": "https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html"
      }
    },
    "gcp-firewall": {
      "name": "Google Cloud VPC firewall rules",
      "basis": "unknown",
      "sources": {
        "s1c06c98a99c9": "https://docs.cloud.google.com/firewall/docs/using-firewalls"
      }
    },
    "azure-firewall": {
      "name": "Azure network security group rules",
      "basis": "unknown",
      "sources": {
        "scde5b083d938": "https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get"
      }
    },
    "cloudflared-image": {
      "name": "cloudflared container image",
      "basis": "2026.9.3",
      "sources": {
        "se79f4a693e7a": "https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L1-L5",
        "s8b0cac0c9e3c": "https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L26-L33",
        "s5c722efb03b3": "https://github.com/cloudflare/cloudflared/blob/2026.9.3/Dockerfile#L40-L42"
      }
    },
    "cloudflare-tunnel": {
      "name": "Cloudflare Tunnel documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s253af0f0386c": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L31-L49",
        "sbd8e87e6c172": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel.mdx#L27-L37"
      }
    },
    "tailscale-entry": {
      "name": "Tailscale entry documentation",
      "basis": "unknown",
      "sources": {
        "s8a8000573b13": "https://tailscale.com/kb/1242/tailscale-serve",
        "sbe30f8121245": "https://tailscale.com/kb/1223/funnel"
      }
    },
    "self-signed-entry": {
      "name": "OpenSSL documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s211b1e6e4aa4": "https://docs.openssl.org/"
      }
    }
  },
  "claims": {
    "publish": {"text": "Omitting the host address publishes 3000:3000 on 0.0.0.0 and [::].", "components": ["engine"], "sources": ["engine:s1e53417c513d"], "status": "REASONED"},
    "host-firewall": {"text": "Docker programs firewall rules directly; UFW or firewalld blocking a host port does not establish published-port isolation.", "components": ["engine"], "sources": ["engine:s351180c6678f"], "status": "REASONED"},
    "private-network": {"text": "Omit app/database ports; Compose peers use service names. The example uses postgres:17 at db:5432.", "components": ["compose", "postgresql"], "sources": ["compose:sae565a19136c", "postgresql:s44c2e898e585"], "status": "REASONED"},
    "loopback": {"text": "Publish local access as 127.0.0.1:3000:3000; check the running server version. Engine 28.0 is the minimum boundary, with 28.3.3 or later required where firewalld is used.", "components": ["engine", "boundary", "reload", "reload-advisory"], "sources": ["engine:s1e53417c513d", "boundary:s50eb099eac95", "reload:s567a65842b29", "reload-advisory:s424f3c4f8285"], "status": "REASONED"},
    "old-loopback": {"text": "Before 28.0, same-L2 neighbours could reach loopback publications under the default bridge configuration.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "old-host-bind": {"text": "Before 28.0, remote hosts could reach published container ports despite the host-IP binding.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "old-unpublished": {"text": "Before 28.0, direct routing could reach unpublished container ports; 28.0 fixed the stated default-bridge exposures.", "components": ["boundary"], "sources": ["boundary:s50eb099eac95"], "status": "REASONED"},
    "upstream": {"text": "Use an upstream security group or network ACL for routable publications and boot-time protection. AWS security groups, Google Cloud VPC firewall rules and Azure NSGs have rolling sources; network-ACL configuration and boot-time independence remain this guide's assessment.", "components": ["engine", "aws-firewall", "gcp-firewall", "azure-firewall"], "sources": ["engine:s351180c6678f", "aws-firewall:s5594f61a25d6", "gcp-firewall:s1c06c98a99c9", "azure-firewall:scde5b083d938"], "status": "REASONED"},
    "docker-user": {"text": "On the iptables backend, DOCKER-USER precedes Docker accepts; the nftables backend has no such chain. Match NEW traffic from outside the allowed subnet.", "components": ["engine"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480"], "status": "REASONED"},
    "dnat": {"text": "DOCKER-USER sees post-DNAT container destinations; conntrack original destination port and ORIGINAL direction scope a published service.", "components": ["engine"], "sources": ["engine:s2fecb6db5480"], "status": "REASONED"},
    "ipv6": {"text": "As this guide's reasoning, native IPv6 forwarding needs ip6tables; Docker documents IPv6-to-IPv4 userland-proxy mapping when no host IP is given, the bridge is IPv4-only and `--userland-proxy=true` (the default), and places DOCKER-USER in FORWARD. As this guide's reasoning, the proxy path terminates on host INPUT and bypasses DOCKER-USER.", "components": ["engine", "engine-pinned"], "sources": ["engine:s2fecb6db5480", "engine:s1e53417c513d", "engine-pinned:sd22373a822c3", "engine-pinned:s024cfadb4bb8", "engine-pinned:s1c82ff316a7e"], "status": "REASONED"},
    "proxy-path": {"text": "Close the userland-proxy path with an explicit publish address, disabled userland proxy or IPv6 INPUT restrictions; test both address families and sources. Docker documents the explicit-address option and conditional userland-proxy mapping; the INPUT restriction and probes are this guide's reasoning and advice.", "components": ["engine", "engine-pinned"], "sources": ["engine:s1e53417c513d", "engine:s2fecb6db5480", "engine-pinned:sb3dacfbaf7e1", "engine-pinned:s1c82ff316a7e", "engine-pinned:s024cfadb4bb8"], "status": "REASONED"},
    "persistence": {"text": "As this guide's advice, persist only DOCKER-USER rules after Docker startup, avoiding blanket dynamic-chain saves. Moby identifies docker.service and systemd documents After= ordering; as this guide's assessment, rule non-persistence, the boot-time gap, what iptables-persistent captures and its potential to break container networking have no direct source here.", "components": ["engine", "engine-pinned", "moby-unit", "systemd-unit"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480", "engine-pinned:sc244607b20e4", "engine-pinned:s024cfadb4bb8", "moby-unit:s6aa0d2fb34cf", "systemd-unit:s71dce3a476cd"], "status": "REASONED"},
    "tls": {"text": "Example caddy:2 publishes 80:80 and 443:443, mounts Caddyfile read-only and persists data/config, proxying app:3000 with automatic certificates.", "components": ["compose", "caddy-image", "caddy"], "sources": ["compose:sae565a19136c", "caddy-image:sbbb7746f7545", "caddy-image:sb126b380b9cf", "caddy-image:seea3a2adc92a", "caddy:s5520ee906a7f", "caddy:sfa5c7dc047dc"], "status": "REASONED"},
    "alternate-entry": {"text": "As this guide's advice, hosts with no inbound ports and a domain they can put on Cloudflare use a cloudflared container, while hosts with no domain at all use Tailscale or internal self-signed TLS. Cloudflare documents a tunnel daemon that needs no firewall openings, a container image, an HTTPS origin service URL and a domain prerequisite; Docker documents Compose service-name lookup. The http://app:3000 origin target on a shared Compose network is this guide's inference, not shown literally by the fetched Cloudflare lines. The tunnel-token setup is not shown here; the Tailscale and OpenSSL references are rolling, and the self-signed fallback remains this guide's advice.", "components": ["compose", "cloudflared-image", "cloudflare-tunnel", "compose-pinned", "tailscale-entry", "self-signed-entry"], "sources": ["compose:sae565a19136c", "cloudflared-image:se79f4a693e7a", "cloudflared-image:s8b0cac0c9e3c", "cloudflared-image:s5c722efb03b3", "cloudflare-tunnel:s253af0f0386c", "cloudflare-tunnel:sbd8e87e6c172", "compose-pinned:seb7ab83ee20e", "tailscale-entry:s8a8000573b13", "tailscale-entry:sbe30f8121245", "self-signed-entry:s211b1e6e4aa4"], "status": "REASONED"},
    "auth": {"text": "As this guide's assessment, proxy authentication and human MFA supplement application login. Caddy and nginx basic authentication reject missing credentials; nginx auth_request returns 401/403; Traefik basicAuth calls RequireAuth and forwardAuth passes through non-2xx; Cloudflare Access policies can require MFA, and Authelia can sit behind the proxy. Require MFA in the governing policy or portal; as this guide's assessment, basic auth alone is single-factor. The Caddy forward_auth rejection status, exact Traefik basicAuth status and Cloudflare Access anonymous status are not established by these fetched lines.", "components": ["compose", "caddy", "nginx-auth", "traefik-auth", "cloudflare-access", "authelia-proxy"], "sources": ["compose:sae565a19136c", "caddy:s32fb97ff942b", "caddy:sd698097c71f4", "caddy:s87dc43d9819d", "nginx-auth:s44cecab17a23", "nginx-auth:s91b029555086", "nginx-auth:s3df6e64cd6a3", "traefik-auth:s5f9a13d720c8", "traefik-auth:sfe588a6dd6a3", "traefik-auth:sbc20b015d928", "cloudflare-access:s6f6104362214", "cloudflare-access:s7cafe1b17afd", "authelia-proxy:s5ca02c783843"], "status": "REASONED"},
    "secrets": {"text": "Use runtime environment files (this guide's advice; weaker, as its assessment) or Compose secrets under /run/secrets (Linux only) or Swarm secrets (swarm services only); as this guide's advice, keep .env in .gitignore (tracked files are unaffected). Never put secrets in Dockerfile ENV/ARG; use temporary build secret mounts; as its assessment, never bake secrets into images or copy or print build secrets into them, and history is not shown to list every argument value.", "components": ["compose", "docker-build", "docker-secrets", "git-ignore"], "sources": ["compose:sae565a19136c", "docker-build:sd8afa286c173", "docker-build:s07e00829f121", "docker-build:s6283b172a5c6", "docker-secrets:s81d857265c7c", "docker-secrets:sd9dc0a9c4c0d", "docker-secrets:sb9dd4c26439c", "docker-secrets:s65e97e494341", "docker-secrets:s04a382307f48", "docker-secrets:s05ba8904bab4", "docker-secrets:s9c3b613c7e5a", "git-ignore:s5f377f0fdbd8"], "status": "REASONED"},
    "workload": {"text": "Keep .env in .gitignore, which ignores matching untracked files but not tracked files. Use a non-root Dockerfile USER; as this guide's assessment, a compromised app then is not root in the container. Drop capabilities, use no-new-privileges and a read-only root filesystem, and never mount the Docker socket. Docker sources establish the option names, that only trusted users should control the daemon, and that Unix permissions can limit access to its control socket; the linked guide's hardening consequences, including the mounted-socket path, remain this guide's assessment.", "components": ["compose", "git-ignore", "docker-workload"], "sources": ["compose:sae565a19136c", "git-ignore:s5f377f0fdbd8", "docker-workload:s2fa3b3cd70e6", "docker-workload:s8000f273883e", "docker-workload:sb94d21792cd4", "docker-workload:s28ce092b2589", "docker-workload:s738280652c95", "docker-workload:secebea1a69ab"], "status": "REASONED"},
    "database": {"text": "Database TLS and authentication remain necessary for connections from outside the Compose network; database vendor sources are in linked guides.", "components": ["compose"], "sources": ["compose:sae565a19136c"], "status": "REASONED"},
    "verify-publish": {"text": "Compose ps is project-scoped; inventory every host container and TCP/UDP socket, including IPv6. Socket visibility alone does not prove reachability.", "components": ["compose", "engine"], "sources": ["compose:sae565a19136c", "engine:s1e53417c513d"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "Verify that HTTP redirects to HTTPS: Caddy v2.11.4 configures an automatic HTTPS redirect; as this guide's configuration-dependent expectation, nginx and Traefik require a configured redirect. This is an expectation, not an observed deployment result.", "components": ["compose", "caddy"], "sources": ["compose:sae565a19136c", "caddy:sd267d297d661", "caddy:s32a5119bce5b"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Verify unauthenticated HTTPS /api rejection with printed status and redirect location; the probe itself fails on any 2xx. A 3xx passes only when the location is the gate's own login portal, never the application's own login; verify authorized success separately. Caddy basic auth and nginx auth_basic expect 401; Caddy forward_auth admits auth-service 2xx, but its rejection status is not established by the fetched lines. nginx auth_request returns 401 or 403, while the cited Authelia nginx configuration turns 401 into 302 to its portal. Traefik forwardAuth passes through a rejecting auth service's status, including a login redirect; Traefik basicAuth's 401 is this guide's expectation because the fetched code calls RequireAuth, whose response these lines do not show. Cloudflare Access's anonymous 302 login redirect is this guide's assessment per cloudflare.md, not established by the fetched Cloudflare lines.", "components": ["compose", "caddy", "nginx-auth", "traefik-auth", "authelia-proxy", "cloudflare-access"], "sources": ["compose:sae565a19136c", "caddy:s32fb97ff942b", "caddy:sd698097c71f4", "caddy:s87dc43d9819d", "nginx-auth:s44cecab17a23", "nginx-auth:s91b029555086", "nginx-auth:s3df6e64cd6a3", "traefik-auth:s5f9a13d720c8", "traefik-auth:sfe588a6dd6a3", "traefik-auth:sbc20b015d928", "authelia-proxy:s31a83fce2b6e", "cloudflare-access:s7cafe1b17afd"], "status": "REASONED", "verify": [1]},
    "verify-isolation": {"text": "Probe each restricted host address and publication from allowed/disallowed sources in both families; backend isolation must coexist with proxy reachability.", "components": ["engine"], "sources": ["engine:s351180c6678f", "engine:s2fecb6db5480", "engine:s1e53417c513d"], "status": "REASONED", "verify": [1]},
    "firewalld-reload": {"text": "Engine 28.2.x and 28.3.0 through 28.3.2 fail to restore container-address filtering after firewalld reload; 28.3.3 fixes CVE-2025-54388 (GHSA-x4rx-4gw3-53p4).", "components": ["reload", "reload-advisory"], "sources": ["reload:s567a65842b29", "reload-advisory:s424f3c4f8285", "reload:seaf4197aafaa"], "status": "REASONED"},
    "firewalld-scope": {"text": "The regression affects Linux Engine in the host network namespace with firewalld: routed remote hosts can reach published container ports, including loopback publications; unpublished ports stay filtered. Rootless Mode and Docker Desktop are unaffected.", "components": ["reload", "reload-advisory"], "sources": ["reload:s567a65842b29", "reload-advisory:s424f3c4f8285"], "status": "REASONED"},
    "verify-firewalld-reload": {"text": "Confirm local backend health, then curl the container address from a second host with a bridge-subnet route before and after sudo firewall-cmd --reload. Without masking controls, affected hosts change from blocked to connectable; fixed hosts stay blocked. Any TCP connection, including HTTP 401/403, shows reachability; failure alone does not prove patching. Check route, target, IPv6, restricted host publications and continued proxy reachability.", "components": ["reload", "reload-advisory"], "sources": ["reload-advisory:s424f3c4f8285", "reload:seaf4197aafaa"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
