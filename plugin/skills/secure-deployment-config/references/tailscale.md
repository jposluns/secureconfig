# Tailscale: serve and funnel

Tailscale gives the same no-open-inbound-ports posture as [cloudflare.md](cloudflare.md), built on WireGuard with device identity as the access control. Two commands matter, and they differ in exactly one thing: who can reach the service.

## 1. tailscale serve: tailnet-only (authenticated by membership)

```bash
tailscale serve --bg localhost:3000
```

- Traffic **through this proxy** is reachable only by devices in your tailnet, so that path is authenticated by device identity and your tailnet ACLs. `serve` does not change how the application binds, though: an application still listening on `0.0.0.0:3000` keeps answering its LAN or VPC address directly, past the tailnet.
- Bind the fronted application to `127.0.0.1:3000` so the tailnet is the only way in.
- HTTPS uses an automatically provisioned TLS certificate for the machine's tailnet name.
- `--bg` keeps it running in the background; without it, the share stops with the session.

This is the right default for admin panels, dashboards, Jupyter, and internal tools: no certificate work, no public exposure at all.

## 2. tailscale funnel: public internet (bring your own auth)

```bash
tailscale funnel 3000
```

- Publishes the service to the entire internet at your `*.ts.net` hostname, TLS included.
- Funnel itself adds **no per-request authentication**; the relay does not even decrypt your traffic. Anything funneled needs application-level login per [authentication.md](authentication.md) and, for human logins, [mfa.md](mfa.md), exactly as if it sat behind any public proxy.
- Prerequisites per the docs: HTTPS certificates enabled for the tailnet, a `funnel` node attribute in the tailnet policy file, and MagicDNS.

## 3. Choosing between them

Serve for anything private (most things). Funnel or [cloudflare.md](cloudflare.md) for genuinely public services; Cloudflare Access adds managed login in front, which funnel does not, so prefer Access when the public service is for a defined set of people. Command syntax changed in Tailscale v1.52; on older clients consult `tailscale serve --help`.

## 4. Verify

```bash
ss -tlnp 'sport = :3000'                          # ss's own filter, not a grep: the address column
                                                  # must read 127.0.0.1:3000, never 0.0.0.0:3000 or [::]:3000
curl -s -o /dev/null --connect-timeout 5 --max-time 10 \
  -w 'http=%{http_code} time_connect=%{time_connect}\n' http://10.0.0.5:3000/
# the host's own LAN or VPC address. An HTTP status here means the app answers past the tailnet; time_connect at 0.000000 means nothing connected
tailscale serve status
curl -sI https://host.tailnet.ts.net/            # from a tailnet device: works
# From a non-tailnet network: serve URL unreachable; funnel URL reachable, so its app login must gate it.
```

## Sources (checked September 2026)

- Tailscale serve: https://tailscale.com/kb/1242/tailscale-serve
- Tailscale funnel: https://tailscale.com/kb/1223/funnel
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
