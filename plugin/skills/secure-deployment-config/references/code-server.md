---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "4b7909609575ae28f5a11bc5fe3984e12f1f003ae3b474f77359b3d0bd667a50",
  "components": {
    "server": {
      "name": "code-server",
      "basis": "v4.137.0",
      "sources": {
        "sc5e7573dedcf": "https://raw.githubusercontent.com/coder/code-server/v4.137.0/docs/guide.md",
        "s411972e92499": "https://coder.com/docs/code-server/FAQ",
        "sbe2b1714f8d5": "https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/cli.ts",
        "s5c5105b71096": "https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/http.ts",
        "s1ccbd73ebb52": "https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/routes/pathProxy.ts",
        "s60678f2e26e9": "https://raw.githubusercontent.com/coder/code-server/v4.137.0/src/node/routes/domainProxy.ts"
      }
    }
  },
  "claims": {
    "ssh": {"text": "Vendor prefers SSH forwarding; bind the local 8080 forwarding listener to loopback and open the local browser URL.", "components": ["server"], "sources": ["server:sc5e7573dedcf"], "status": "REASONED"},
    "config": {"text": "Edit generated config.yaml and retain a supported credential; precreating it suppresses random-password generation and password auth without either credential fails startup.", "components": ["server"], "sources": ["server:s411972e92499", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "bind": {"text": "bind-addr 127.0.0.1:8080 keeps the editor private behind a proxy or tunnel.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "auth-default": {"text": "auth defaults password; replace the generated value with a long random secret and protect config.yaml.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "rate-limit": {"text": "Password attempts are limited to two per minute plus twelve per hour.", "components": ["server"], "sources": ["server:sc5e7573dedcf"], "status": "REASONED"},
    "credential-precedence": {"text": "PASSWORD/HASHED_PASSWORD override file credentials and hashed form wins; --password is not a supported CLI flag.", "components": ["server"], "sources": ["server:s411972e92499", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "config-precedence": {"text": "CLI flags override config; inspect --bind-addr, --config, CODE_SERVER_CONFIG and XDG_CONFIG_HOME for the effective launcher and file.", "components": ["server"], "sources": ["server:s411972e92499", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "tls-default": {"text": "cert defaults false; public access needs authenticated encryption, normally a reverse proxy with a trusted certificate.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s411972e92499", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "tls-native": {"text": "Bare --cert or cert:true generates ~/.local/share/code-server/self-signed.crt; --cert with --cert-key selects supplied material; retain certificate validation.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "mfa": {"text": "Built-in login is single-factor; fronting MFA must cover every enabled path, subdomain and WebSocket.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s5c5105b71096"], "status": "REASONED"},
    "path-proxy": {"text": "/proxy/<port>/ strips its prefix; /absproxy/<port>/ retains it; both use code-server authentication and auth:none exposes them.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s5c5105b71096", "server:s1ccbd73ebb52"], "status": "REASONED"},
    "domain-proxy": {"text": "--proxy-domain exposes per-port subdomains using code-server authentication; apply fronting policy to each.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s5c5105b71096", "server:s60678f2e26e9"], "status": "REASONED"},
    "preflight": {"text": "--skip-auth-preflight allows unauthenticated preflight requests.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:sbe2b1714f8d5"], "status": "REASONED"},
    "disable-proxy": {"text": "--disable-proxy turns off unneeded port forwarding.", "components": ["server"], "sources": ["server:sbe2b1714f8d5", "server:s5c5105b71096"], "status": "REASONED"},
    "least-privilege": {"text": "Loopback limits inbound reach, not terminal/extension/proxied-service outbound access; minimize permissions and egress, including metadata/internal destinations.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s5c5105b71096"], "status": "REASONED"},
    "verify-origin": {"text": "ss inventories only this namespace; probe each public IPv4/IPv6 and port directly with intended TLS hostname; any HTTP response is reachability, and http=000 is inconclusive.", "components": ["server"], "sources": ["server:sc5e7573dedcf"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "At the same editor URL, anonymous requests must reach login/challenge and valid-session requests the editor; a proxy 401 alone or failed positive control proves nothing.", "components": ["server"], "sources": ["server:sc5e7573dedcf", "server:s5c5105b71096"], "status": "REASONED", "verify": [1]},
    "verify-mfa": {"text": "Password-only access must not open the editor while completing the second factor must; also confirm in a fresh browser.", "components": ["server"], "sources": ["server:sc5e7573dedcf"], "status": "REASONED", "verify": [1]}
  }
}
---
# code-server: browser VS Code without giving away the machine

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| ssh: Vendor prefers SSH forwarding; bind the local 8080 forwarding listener to loopback and open the local browser URL. | code-server v4.137.0 | REASONED |
| config: Edit generated config.yaml and retain a supported credential; precreating it suppresses random-password generation and password auth without either credential fails startup. | code-server v4.137.0 | REASONED |
| bind: bind-addr 127.0.0.1:8080 keeps the editor private behind a proxy or tunnel. | code-server v4.137.0 | REASONED |
| auth-default: auth defaults password; replace the generated value with a long random secret and protect config.yaml. | code-server v4.137.0 | REASONED |
| rate-limit: Password attempts are limited to two per minute plus twelve per hour. | code-server v4.137.0 | REASONED |
| credential-precedence: PASSWORD/HASHED_PASSWORD override file credentials and hashed form wins; --password is not a supported CLI flag. | code-server v4.137.0 | REASONED |
| config-precedence: CLI flags override config; inspect --bind-addr, --config, CODE_SERVER_CONFIG and XDG_CONFIG_HOME for the effective launcher and file. | code-server v4.137.0 | REASONED |
| tls-default: cert defaults false; public access needs authenticated encryption, normally a reverse proxy with a trusted certificate. | code-server v4.137.0 | REASONED |
| tls-native: Bare --cert or cert:true generates ~/.local/share/code-server/self-signed.crt; --cert with --cert-key selects supplied material; retain certificate validation. | code-server v4.137.0 | REASONED |
| mfa: Built-in login is single-factor; fronting MFA must cover every enabled path, subdomain and WebSocket. | code-server v4.137.0 | REASONED |
| path-proxy: /proxy/&lt;port&gt;/ strips its prefix; /absproxy/&lt;port&gt;/ retains it; both use code-server authentication and auth:none exposes them. | code-server v4.137.0 | REASONED |
| domain-proxy: --proxy-domain exposes per-port subdomains using code-server authentication; apply fronting policy to each. | code-server v4.137.0 | REASONED |
| preflight: --skip-auth-preflight allows unauthenticated preflight requests. | code-server v4.137.0 | REASONED |
| disable-proxy: --disable-proxy turns off unneeded port forwarding. | code-server v4.137.0 | REASONED |
| least-privilege: Loopback limits inbound reach, not terminal/extension/proxied-service outbound access; minimize permissions and egress, including metadata/internal destinations. | code-server v4.137.0 | REASONED |
| verify-origin: ss inventories only this namespace; probe each public IPv4/IPv6 and port directly with intended TLS hostname; any HTTP response is reachability, and http=000 is inconclusive. | code-server v4.137.0 | REASONED |
| verify-editor: At the same editor URL, anonymous requests must reach login/challenge and valid-session requests the editor; a proxy 401 alone or failed positive control proves nothing. | code-server v4.137.0 | REASONED |
| verify-mfa: Password-only access must not open the editor while completing the second factor must; also confirm in a fresh browser. | code-server v4.137.0 | REASONED |
<!-- version-basis:end -->

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
# REASONED: editor, origin and proxy checks follow the cited code-server authentication and proxy
# documentation; no isolated network namespace is available for authorized live listeners.
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
    ''|*[!0123456789]*) echo 'a numeric published port is required; not probing'; exit 2 ;;
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
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
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
  { unset -n code_server_cookie && unset -v code_server_cookie; } 2>/dev/null ||
    { echo 'cannot initialize cookie input; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
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
