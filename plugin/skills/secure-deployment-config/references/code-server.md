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
# UNVERIFIED: live exposed-versus-fixed results remain outstanding in TODO row 1.78.
# Shell syntax and guard checks do not demonstrate authentication or origin isolation.
# ss is a listener inventory in THIS namespace - not a firewall, publication, or authentication check.
ss -tlnp   # expect 8080 on loopback or a private address; then probe the public origin directly (below):
           # ANY HTTP response there (even a 401) means the origin is reachable, which is a finding on its own
# Direct-origin reachability: connect straight to the public IP and published port while keeping the URL
# hostname for TLS. From an untrusted external host, repeat for every public IPv4/IPv6 address and port.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ORIGIN_URL' 'REPLACE_WITH_PUBLIC_IP' 'REPLACE_WITH_PUBLISHED_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'exactly three values are required; not probing'; exit 2; }
  case "$1|$2|$3" in
    *REPLACE_WITH_*) echo 'substitute all values inside the quotes; not probing'; exit 2 ;;
  esac
  case "$1" in
    http://*|https://*) ;;
    *) echo 'an HTTP or HTTPS origin URL is required; not probing'; exit 2 ;;
  esac
  [ -n "$2" ] || { echo 'a public IP is required; not probing'; exit 2; }
  case "$3" in
    ''|*[!0-9]*) echo 'a numeric published port is required; not probing'; exit 2 ;;
  esac
  # bracket an IPv6 literal in REPLACE_WITH_PUBLIC_IP. Any HTTP response (incl 401/403) = a finding;
  # http=000 is not a pass (a certificate, timeout, or local error is inconclusive). Never add -k.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --connect-to "::$2:$3" -o /dev/null \
    -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
# Auth discrimination against the SAME editor URL: a proxy 401 proves nothing, so pair an unauthenticated
# request with an authenticated one and confirm the editor in a fresh browser session too.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_EDITOR_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*) echo 'substitute the editor URL; not probing'; exit 2 ;;
    https://*) ;;
    *) echo 'an HTTPS URL is required; not probing'; exit 2 ;;
  esac
  # 1) Unauthenticated: follow redirects and inspect the FINAL body - login or challenge, never the editor.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --location --max-redirs 5 --proto-redir '=https' \
    -w '\nunauth http=%{http_code} url=%{url_effective} exit=%{exitcode} err=%{errormsg}\n' "$1"
  # 2) Authenticated positive control: paste a cookie from a valid browser session; it enters via stdin
  #    (curl --header @-), never argv. The authenticated response must contain the editor.
  set +x +a
  { unset -n code_server_cookie && unset -v code_server_cookie; } 2>/dev/null ||
    { echo 'cannot initialize cookie input; not probing'; exit 2; }
  IFS= read -r -s -p 'Cookie value (name=value; name=value), then Enter: ' code_server_cookie < /dev/tty || exit 2
  printf '\n'
  case "$code_server_cookie" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'a valid session cookie is required; not probing'; exit 2 ;;
  esac
  printf 'Cookie: %s\n' "$code_server_cookie" |
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      --location --max-redirs 5 --proto-redir '=https' --header @- \
      -w '\nauth http=%{http_code} url=%{url_effective} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
# Fixed: unauthenticated lands on login or challenge and authenticated reaches the editor. For MFA, confirm
# password-only access cannot open the editor and completing the second factor can. A transport, certificate,
# or unsuccessful positive control is inconclusive, not a pass.
```

An unauthenticated editor in a private browser window means whoever finds the URL owns the host.

## Sources (checked September 2026)

- code-server v4.137.0 deployment guide (exposure, TLS and self-signed certificates, reverse proxy, `/proxy`+`/absproxy`+`--proxy-domain` routes, `--skip-auth-preflight`): https://raw.githubusercontent.com/coder/code-server/v4.137.0/docs/guide.md
- code-server FAQ (config.yaml keys map to flags, `cert: false` default, `hashed-password` precedence, config path from `--config`/`CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME`, flags override the file): https://coder.com/docs/code-server/FAQ
- code-server v4.137.0 CLI (credentials, defaults, config generation, proxy flags, `--password` rejected on the CLI): https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/cli.ts
- code-server v4.137.0 HTTP controls (authentication, proxy auth, `--disable-proxy`): https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/http.ts
- code-server v4.137.0 path proxy (`/proxy`, `/absproxy` routing): https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/routes/pathProxy.ts
- code-server v4.137.0 domain proxy (`--proxy-domain` subdomains): https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/routes/domainProxy.ts
