# Tailscale: serve and funnel

Tailscale gives the same no-open-inbound-ports posture as [cloudflare.md](cloudflare.md), built on WireGuard with device identity as the access control. Two commands matter, and they differ in exactly one thing: who can reach the service.

## 1. tailscale serve: tailnet-only (authenticated by membership)

```bash
tailscale serve --bg localhost:3000
```

- Traffic **through this proxy** is reachable only by devices in your tailnet, so that path is authenticated by device identity and your tailnet ACLs. `serve` does not change how the application binds, though: an application still listening on `0.0.0.0:3000` keeps answering its LAN or VPC address directly, past the tailnet.
- That reach is only as tight as your tailnet policy. A new tailnet's default policy lets every device in the tailnet (`action` accept, `src` `*`, `dst` `*:*`), plus anyone you have shared the node with, connect to this service. Restrict it by removing the default allow-all rule and granting only the intended users, groups, or tags to this host and the port `serve` listens on (a grant is preferred; ACLs remain supported); adding a narrower rule alongside allow-all does not revoke it, because Tailscale rules are additive accepts.
- Tailnet reach is network access, not application authorization: an admin panel behind `serve` must still authenticate and authorize its own users, through its own login or by deliberately consuming the identity headers `serve` forwards. Trusting those headers is safe only where you trust every process on the Serve host: the loopback bind above stops other machines, but any local process can still reach `127.0.0.1:3000` and forge them (Tailscale notes that binding to localhost limits tampering to other services on the Serve device, it does not eliminate it). Requests from tagged devices carry no user identity, so give those another method or reject them.
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
```

From another machine on the same LAN or VPC (run this from OUTSIDE the host), confirm the app does not answer its direct address:

```bash
set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_HOST_LAN_OR_VPC_IP'   # replace inside the quotes, keeping them
[ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
shift
[ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
case "$1" in
  *REPLACE_WITH_*|"") echo "substitute the host's LAN or VPC address on the set -- line above; not probing" ;;
  *) curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
       -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/" ;;
esac
# A reply (http=200/301/...) means the app still answers past the tailnet on 0.0.0.0; a refused or timed-out connection (err set, http=000) means it is loopback-bound.
```

Then confirm the tailnet path works and that the section-1 restriction actually holds:

```bash
tailscale serve status
curl -q -sI https://host.tailnet.ts.net/            # from an ALLOWED tailnet device: works
```

An allowed device connects under both the default allow-all policy and a correctly scoped one, so a request that works here does not prove the section-1 restriction took hold. Assert it in the tailnet policy file's `tests` (an `accept` from the intended identity to this host and port, and a `deny` from an excluded tailnet identity); Tailscale rejects a policy file whose `tests` fail. From a non-tailnet network the serve URL is unreachable while a funnel URL is reachable, so a funneled app must gate every request with its own login.

## Sources (checked September 2026)

- Tailscale serve: https://tailscale.com/kb/1242/tailscale-serve
- Tailscale funnel: https://tailscale.com/kb/1223/funnel
- Tailscale ACL policy examples, for the default allow-all policy (`action` accept, `src` `*`, `dst` `*:*`) and scoping access from a source to a destination: https://tailscale.com/docs/reference/examples/acls
- Tailscale serve identity headers, that binding the backend to localhost limits tampering to other services on the Serve device (it does not authenticate the calling process): https://tailscale.com/kb/1312/serve
- Tailscale policy-file `tests`, that a policy file whose assertions fail is rejected: https://tailscale.com/docs/reference/syntax/policy-file#tests
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
