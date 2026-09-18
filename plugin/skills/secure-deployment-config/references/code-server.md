# code-server: browser VS Code without giving away the machine

code-server runs a terminal in the browser, so exposure equals remote code execution. Its own documentation is blunt: never expose it directly to the internet without authentication and encryption.

## 1. Prefer no exposure at all

The code-server docs recommend SSH port forwarding first, which needs no additional setup:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 user@host   # then open http://127.0.0.1:8080 locally
```

[tailscale.md](tailscale.md) (serve, tailnet-only) and [cloudflare.md](cloudflare.md) (tunnel plus Access with MFA) are the equivalents when SSH is unavailable.

## 2. If it must be reachable: config.yaml

Edit the generated `~/.config/code-server/config.yaml` in place; creating this file yourself before the first start removes the random password code-server would have generated, and password auth with neither `password` nor `hashed-password` fails to start. This is a partial configuration; keep the generated `password` entry (or set another supported credential):

```yaml
bind-addr: 127.0.0.1:8080     # keep loopback behind a proxy or tunnel
auth: password                # default; keep the generated password in this file
cert: false                   # TLS is off by default; terminate it at the proxy (below)
```

Password attempts are rate-limited (2 per minute plus 12 per hour). Replace the generated password with your own long random value, and treat the config file as a secret ([secrets.md](secrets.md)). Know where the effective credential comes from: the `PASSWORD` and `HASHED_PASSWORD` environment variables override the file (the hashed form wins over plaintext), there is no `--password` command-line flag, and any flag passed to code-server overrides the file, so inspect the launcher (including `--bind-addr` and `--config`, and `CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME` for the config path) rather than assuming the file is authoritative. code-server does not terminate TLS by default (`cert: false`); a bare `--cert` (or `cert: true`) generates a self-signed certificate at `~/.local/share/code-server/self-signed.crt`, while `--cert` with `--cert-key` uses a certificate you supply. For public access, the docs' supported pattern is a reverse proxy with a real certificate: [caddy.md](caddy.md) or [nginx.md](nginx.md) with [free-certificates.md](free-certificates.md), with MFA added at that layer ([mfa.md](mfa.md)) since the built-in login is a single factor. Never disable certificate validation with `-k`.

code-server also proxies other local services through `/proxy/<port>/`, `/absproxy/<port>/` (which does not strip the path prefix), and per-port subdomains under `--proxy-domain`. These routes use code-server's own authentication, so `auth: none` exposes them too, and `--skip-auth-preflight` lets preflight requests through unauthenticated; if you do not need port forwarding, turn it off with `--disable-proxy`, and require your fronting auth and MFA on every enabled path, subdomain, and WebSocket route. Loopback binding only limits inbound reach: the terminal, extensions, and any service code-server proxies can still make outbound requests, so run the process with only the permissions and network it needs and keep it off cloud metadata and internal endpoints ([egress-metadata.md](egress-metadata.md)).

## 3. Verify

```bash
# REASONED, not demonstrated here: no running code-server in the authoring environment, so the shell syntax
# and guards were checked locally but the exposed-vs-fixed responses were not. Backlog row 1.78 tracks it.
# ss is a listener inventory in THIS namespace - not a firewall, publication, or authentication check.
ss -tlnp   # expect 8080 on loopback or a private address; then, from another host, probe every PUBLIC
           # IPv4/IPv6 address and any published port directly - ANY HTTP response there (even a 401) means
           # the origin is reachable, which is a finding on its own
(                              # unauthenticated control against the SAME editor URL; a proxy 401 proves nothing
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_EDITOR_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*) echo 'substitute the editor URL; not probing'; exit 2 ;;
    https://*) ;;
    *) echo 'an HTTPS URL is required; not probing'; exit 2 ;;
  esac
  # An unauthenticated visit must land on the login page, not the editor. A discarded-body request cannot tell
  # them apart (both are 200), so keep the body and also confirm it in a fresh browser session.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} url=%{url_effective} exit=%{exitcode}\n' "$1"
)
# Authenticated positive control: repeat with a valid session (send the session cookie via a stdin header,
# curl -H @-, never on the command line) and confirm it reaches the editor. For MFA, confirm password-only
# access fails and completing the second factor permits the same request. Run these from a network position
# permitted to reach the origin, and separately confirm untrusted clients cannot reach the origin directly.
```

An unauthenticated editor in a private browser window means whoever finds the URL owns the host.

## Sources (checked September 2026)

- code-server deployment guide (exposure recommendations, TLS and self-signed certificates, reverse proxy, `/proxy`+`/absproxy`+`--proxy-domain` routes and `--skip-auth-preflight`; checked against v4.137.0): https://coder.com/docs/code-server/guide
- code-server FAQ (config.yaml keys map to flags, `cert: false` default, `hashed-password` precedence, `--config`/`CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME`, flags override the file): https://coder.com/docs/code-server/FAQ
- code-server repository: https://github.com/coder/code-server
