# code-server: browser VS Code without giving away the machine

code-server runs VS Code on a server for use in a browser, and its terminal runs commands on that server. This guide helps your AI assistant configure it securely, including SSH forwarding first, a tailnet or MFA-protected tunnel next, and otherwise a loopback bind behind a TLS proxy adding MFA.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/code-server.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against code-server v4.145.2. Metadata reviewed 2026-11-07; documentation checked November 2026. The guide records 23 claims, all reasoned from cited sources and any earlier-form run, not a live demonstration of the shipped form.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

code-server runs a terminal in the browser, so exposure equals remote code execution. Its own documentation is blunt: never expose it directly to the internet without authentication and encryption.

## 1. Prefer no exposure at all

The code-server docs recommend SSH port forwarding first, which needs no additional setup:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8080:127.0.0.1:8080 user@host   # then open http://127.0.0.1:8080 locally
```

[tailscale.md](tailscale.md) (serve, tailnet-only) and [cloudflare.md](cloudflare.md) (tunnel plus Access with MFA) are the equivalents when SSH is unavailable.

On the Cloudflare path, turn Rocket Loader off for the code-server hostname, scoped with a Configuration Rule rather than zone-wide: the v4.145.2 deployment guide says the scripts Rocket Loader re-injects lack the nonce in code-server's Content Security Policy, so the browser blocks them and the page loads blank (observed in source at v4.145.2; nothing was run). Do not loosen the policy to work around it; the same guide notes that adding `'unsafe-inline'` does not help while a nonce is present (observed in source at v4.145.2).

## 2. If it must be reachable: config.yaml

Edit the generated `~/.config/code-server/config.yaml` in place; creating this file yourself before the first start removes the random password code-server would have generated, and password auth with neither `password` nor `hashed-password` fails to start. This is a partial configuration; keep the generated `password` entry (or set another supported credential):

```yaml
bind-addr: 127.0.0.1:8080     # keep loopback behind a proxy or tunnel
auth: password                # default; keep the generated password in this file
cert: false                   # TLS is off by default; terminate it at the proxy (below)
```

Password attempts are rate-limited (2 per minute plus 12 per hour). Replace the generated password with your own long random value, and treat the config file as a secret ([secrets.md](secrets.md)). Know where the effective credential comes from: the `PASSWORD` and `HASHED_PASSWORD` environment variables override the file (the hashed form wins over plaintext), there is no `--password` command-line flag, and any flag passed to code-server overrides the file. The resulting step is to inspect the launcher (including `--bind-addr` and `--config`, and `CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME` for the config path) rather than assuming the file is authoritative. The listen address has more launcher inputs: `CODE_SERVER_HOST` and `PORT` in the environment override the host and port of `bind-addr`, the `--host` and `--port` flags override those, and `--socket` (whose description says `bind-addr` is then ignored) or `--socket-fd` (described as a pre-bound listening socket to use) selects a different listener. `CS_DISABLE_PROXY` set to `1` or `true` turns on `--disable-proxy`, so check the launcher's environment as well as its flags. The code-server process does not terminate TLS by default (`cert: false`); a bare `--cert` (or `cert: true`) generates a self-signed certificate at `~/.local/share/code-server/self-signed.crt`, while `--cert` with `--cert-key` uses a certificate you supply. For public access, the docs' supported pattern is a reverse proxy with a real certificate: [caddy.md](caddy.md) or [nginx.md](nginx.md) with [free-certificates.md](free-certificates.md), with MFA added at that layer ([mfa.md](mfa.md)) since the built-in login is a single factor. Never disable certificate validation with `-k`.

code-server also proxies other local services through `/proxy/<port>/`, `/absproxy/<port>/` (which does not strip the path prefix), and per-port subdomains under `--proxy-domain`. These routes use code-server's own authentication, so `auth: none` exposes them too, and `--skip-auth-preflight` lets preflight requests through unauthenticated; if you do not need port forwarding, turn it off with `--disable-proxy`, and require your fronting auth and MFA on every enabled path, subdomain, and WebSocket route. Loopback binding only limits inbound reach: the terminal, extensions, and any service code-server proxies can still make outbound requests, so run the process with only the permissions and network it needs and keep it off cloud metadata and internal endpoints ([egress-metadata.md](egress-metadata.md)).

With `--proxy-domain <domain>`, v4.145.2 sets the session cookie's Domain attribute to `<domain>` when you reach code-server on a host under it (observed in source; nothing was run); under browser cookie rules, not code-server source, browsers then send the cookie to hosts under that domain for requests within the cookie's path. At v4.137.0 the same check compared the host with the stored `{{port}}.<domain>` pattern, which an ordinary host never ends with, so this wider scope is new in v4.145.2 (inference from comparing the two tags). The cookie carries a hash derived from the password, and v4.145.2 authenticates requests by checking that cookie (observed in source). Any sibling host under that domain that receives the cookie, subject to its path and ordinary browser cookie rules, can therefore replay it as the code-server authentication cookie (inference from the source); whether the value is also accepted as a login password is not established. Use a proxy domain whose subdomains serve only code-server and its forwarded ports, never one shared with other sites.

In v4.145.2 the session cookie is `httpOnly` (it was not at v4.137.0), a hardening that keeps page scripts from reading it; it keeps `sameSite: "lax"`, and `getCookieOptions` sets no `Secure` attribute at either tag (observed in source at v4.145.2 and v4.137.0; nothing was run). Whether anything else adds `Secure` is not established from the reviewed files, so serve code-server only over HTTPS and inspect the `Set-Cookie` header your browser receives.

Behind a reverse proxy, code-server compares the browser's `Origin` with the forwarded host: in v4.145.2 the hostnames must still match exactly, a default port (`:80` or `:443`) counts as no port, a host taken from `X-Forwarded-Host` without a port gets `X-Forwarded-Port` appended, and the resulting ports must match (observed in source). If WebSocket connections through the proxy fail with 403 Forbidden, which is the origin check's response, set correct proxy headers (`Host`, `X-Forwarded-Host`, `X-Forwarded-Port`) rather than widening `--trusted-origins`: an entry of `"*"` turns the origin check off, and a `*.example.com` entry trusts every subdomain.

v4.145.2 adds two boolean flags with no default assigned in the reviewed CLI source, so both are off unless set (inference). `--disable-file-cache` is described as keeping workspace files out of the browser cache; turn it on when people use shared or untrusted client machines. `--enable-remote-storage` is described as keeping workbench storage on the server instead of in the browser, which would bring that state under your server's data-at-rest controls (inference). Only the two declarations are in the reviewed files, so what either flag does beyond its description is not established, and neither was run.

## 3. Verify

REASONED: following block; listener inventory and direct-origin reachability, per the guide's cited code-server v4.145.2 deployment guide and HTTP controls; no isolated network namespace or external probe host is available, so neither check has run against a live listener. On the code-server host, `ss -tlnp` is a listener inventory in THIS namespace, not a firewall, publication, or authentication check: expect 8080 on loopback or a private address. Then run the following block from an untrusted external host. Any HTTP response there, even a 401, means the origin is reachable, which is a finding on its own, and no HTTP response is inconclusive, so the block cannot exit 0: confirm closure from the host and network firewall policy.

```bash
# REASONED: origin checks follow the cited code-server authentication and proxy
# documentation; no isolated network namespace is available for authorized live listeners.
# Shell syntax and guard checks do not demonstrate origin isolation.
# Direct-origin reachability: connect straight to the public IP and published port while keeping the URL
# hostname for TLS. From an untrusted external host, repeat for every public IPv4/IPv6 address and port.
# This block cannot exit 0: it exits 1 for any HTTP response and 3 for none.
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
  set -- "$1" "$2" "$3" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --connect-to "::$2:$3" -o /dev/null \
    -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "${4%%$'\n'*}" "${4##*$'\n'}"  # curl's write-out line, then its exit status
  printf '%s\n' "$1"
  case "$1" in
    'origin http=000 '*) ;;             # no HTTP code, so curl's exit status below decides
    'origin http='[0123456789][0123456789][0123456789]' '*) set -- "$1" 0 ;;   # an HTTP code is a response even if the transfer then failed
  esac
  if [ "$2" = 0 ]; then
    echo "FINDING: the origin answered HTTP directly, so it is reachable"; set -- 1
  else
    echo "curl exit $2: no HTTP response, which is not a pass; inconclusive"; set -- 3
  fi
  echo "block exit $1; this block has no passing result, so confirm closure from the host and network firewall policy"
  exit "$1"
)
```

```bash
# REASONED: editor and proxy checks follow the cited code-server authentication and proxy
# documentation; no isolated network namespace is available for authorized live listeners.
# Shell syntax and guard checks do not demonstrate authentication.
# Auth discrimination against the SAME editor URL: a proxy 401 proves nothing, so pair an unauthenticated
# request with an authenticated one and confirm the editor in a fresh browser session too.
# Fixed: unauthenticated lands on login or challenge and authenticated reaches the editor. For MFA, confirm
# password-only access cannot open the editor and completing the second factor can. A transport, certificate,
# or unsuccessful positive control is inconclusive, not a pass.
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
  # 2) Authenticated positive control: paste a cookie from a valid browser session; it enters via stdin
  #    (curl --header @-), never argv. The authenticated response must contain the editor.
  #    The hidden prompt keeps it out of shell history and set +x keeps it out of set -x tracing. Stdin
  #    closes the argv channel only: the account owner and root can still read it in the subshell and curl.
  #    The cookie is read before either request, so a refused cookie stops the block before any probe.
  { unset -n code_server_cookie && unset -v code_server_cookie; } 2>/dev/null ||
    { echo 'cannot initialize cookie input; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'Cookie value (name=value; name=value), then Enter: ' code_server_cookie < /dev/tty ||
    { printf '\n'; echo 'cookie input failed; not probing'; exit 3; }
  printf '\n'
  case "$code_server_cookie" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'a valid session cookie is required; not probing'; exit 2 ;;
  esac
  set -- "$1" 0                         # the 2nd value is this block's status so far: 3 (inconclusive) outranks 0
  # 1) Unauthenticated: follow redirects and inspect the FINAL body - login or challenge, never the editor.
  set -- "$1" "$2" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --location --max-redirs 5 --proto-redir '=https' \
    -w '\nunauth http=%{http_code} url=%{url_effective} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3%$'\n'*}" "${3##*$'\n'}"   # the response and its write-out line, then curl's exit status
  printf '%s' "$3"
  [ "$4" = 0 ] || { echo "curl exit $4: the unauthenticated request failed, which is inconclusive, not a pass"; set -- "$1" 3; }
  # 2) The authenticated request, with the cookie read above.
  set -- "$1" "$2" "$(if printf 'Cookie: %s\n' "$code_server_cookie" | \
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      --location --max-redirs 5 --proto-redir '=https' --header @- \
      -w '\nauth http=%{http_code} url=%{url_effective} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3%$'\n'*}" "${3##*$'\n'}"   # the response and its write-out line, then curl's exit status
  printf '%s' "$3"
  set -- "$1" "$2" "$3" "$4" "${3##*auth http=}"  # the final HTTP code and the rest of the write-out line
  case "$4:${5%% *}" in
    0:2??) ;;
    0:*) echo "HTTP ${5%% *} with the cookie: the positive control did not succeed; inconclusive"; set -- "$1" 3 ;;
    *) echo "curl exit $4: the authenticated request failed, which is inconclusive, not a pass"; set -- "$1" 3 ;;
  esac
  echo "block exit $2; both final bodies are not classified, so judge them yourself: login or challenge without the cookie, the editor with it"
  exit "$2"
)
```

REASONED: preceding block; paired editor access and MFA, with the listener inventory and direct-origin block above, per the guide's cited code-server v4.145.2 deployment guide and HTTP controls. No editor, proxy, IdP or external probe host is available; listeners are denied locally. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics and config YAML parsed. Placeholder, missing-assignment, short, empty and embedded-placeholder inputs printed refusal messages without reaching curl stubs; substituted inputs reached the stubs; under a pseudo-terminal, empty, placeholder and control-character cookies exited 2 before the authenticated request, and a fixture cookie exited 0 and reached curl only on stdin as a `Cookie:` header. Those checks and runs used an earlier form: one fence whose exit status was the authenticated request's, with the cookie prompt after the unauthenticated request and a bare exit 2 when the prompt failed. The current direct-origin block exits 1 for any HTTP response and 3 for none. The current editor block reads the cookie before either request and exits 3 if that read fails, if a request fails or if the authenticated request ends on a non-2xx status; it exits 2 on a refused input and otherwise 0, leaving both final bodies for you to judge. On 2026-10-31 both current blocks passed bash -n and ran whole against stubs with no network; ShellCheck 0.11.0 runs on them in the repository's gate suite, not in that review. Live outcomes remain unobserved: exposed access opens the editor anonymously or bypasses MFA; fixed access isolates the origin, challenges anonymous users and requires the second factor while admitting the authenticated control. An unauthenticated editor in a private browser window means whoever finds the URL owns the host. Paste the cookie value alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run.

## Sources (checked November 2026)

- code-server v4.145.2 deployment guide (exposure, TLS and self-signed certificates, reverse proxy, `/proxy`+`/absproxy`+`--proxy-domain` routes, `--skip-auth-preflight`, Cloudflare Rocket Loader and the nonce-based CSP): https://raw.githubusercontent.com/coder/code-server/v4.145.2/docs/guide.md
- code-server v4.145.2 FAQ (config.yaml keys map to flags, `cert: false` default, `hashed-password` precedence, config path from `--config`/`CODE_SERVER_CONFIG`/`XDG_CONFIG_HOME`, flags override the file): https://raw.githubusercontent.com/coder/code-server/v4.145.2/docs/FAQ.md
- code-server v4.145.2 CLI (credentials, defaults, config generation, proxy flags, `--password` rejected on the CLI, `CODE_SERVER_HOST`/`PORT`/`--host`/`--port`/`--socket`/`--socket-fd` listener inputs, `CS_DISABLE_PROXY`, `--trusted-origins`, `--disable-file-cache`, `--enable-remote-storage`): https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/cli.ts
- code-server v4.145.2 HTTP controls (authentication, proxy auth, `--disable-proxy`, session cookie domain and attributes, origin check and trusted origins): https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/http.ts
- code-server v4.145.2 path proxy (`/proxy`, `/absproxy` routing): https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/routes/pathProxy.ts
- code-server v4.145.2 domain proxy (`--proxy-domain` subdomains): https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/routes/domainProxy.ts


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- server: code-server (v4.145.2)

Claims (full source mapping in the JSON block below):

- ssh (REASONED; server): Vendor prefers SSH forwarding; bind the local 8080 forwarding listener to loopback and open the local browser URL.
- rocket-loader (REASONED; server): On the Cloudflare path, turn Rocket Loader off for the code-server hostname, because its re-injected scripts lack the CSP nonce; do not loosen the CSP, since 'unsafe-inline' does not help while a nonce is present (observed in source at v4.145.2, docs/guide.md).
- config (REASONED; server): Edit generated config.yaml and retain a supported credential; precreating it suppresses random-password generation and password auth without either credential fails startup.
- bind (REASONED; server): bind-addr 127.0.0.1:8080 keeps the editor private behind a proxy or tunnel.
- auth-default (REASONED; server): auth defaults password; replace the generated value with a long random secret and protect config.yaml.
- rate-limit (REASONED; server): Password attempts are limited to two per minute plus twelve per hour.
- credential-precedence (REASONED; server): PASSWORD/HASHED_PASSWORD override file credentials and hashed form wins; --password is not a supported CLI flag.
- config-precedence (REASONED; server): CLI flags override config; inspect --bind-addr, --config, CODE_SERVER_CONFIG and XDG_CONFIG_HOME for the effective launcher and file, plus CODE_SERVER_HOST, PORT, --host, --port, --socket and --socket-fd for the listener and CS_DISABLE_PROXY, which turns on --disable-proxy.
- tls-default (REASONED; server): cert defaults false; public access needs authenticated encryption, normally a reverse proxy with a trusted certificate.
- tls-native (REASONED; server): Bare --cert or cert:true generates ~/.local/share/code-server/self-signed.crt; --cert with --cert-key selects supplied material; retain certificate validation.
- mfa (REASONED; server): Built-in login is single-factor; fronting MFA must cover every enabled path, subdomain and WebSocket.
- path-proxy (REASONED; server): /proxy/&lt;port&gt;/ strips its prefix; /absproxy/&lt;port&gt;/ retains it; both use code-server authentication and auth:none exposes them.
- domain-proxy (REASONED; server): --proxy-domain exposes per-port subdomains using code-server authentication; apply fronting policy to each.
- proxy-domain-cookie (REASONED; server): Under --proxy-domain the v4.145.2 session cookie is scoped to that domain and carries a password-derived hash that code-server checks as authentication (observed in source), so a sibling host the browser sends it to, per its path and browser cookie rules, can replay it as the authentication cookie (inference); login-password acceptance is not established. Serve only code-server under that domain.
- cookie-attributes (REASONED; server): The v4.145.2 session cookie is httpOnly with sameSite lax; getCookieOptions sets no Secure attribute at either tag (observed in source at v4.145.2 and v4.137.0), and whether anything else adds Secure is not established.
- origin-check (REASONED; server): The v4.145.2 origin check needs an exact hostname match, treats default ports as none and may append X-Forwarded-Port; fix Host and X-Forwarded-Host/-Port at the proxy instead of widening --trusted-origins, where "*" turns the check off.
- preflight (REASONED; server): --skip-auth-preflight allows unauthenticated preflight requests.
- disable-proxy (REASONED; server): --disable-proxy turns off unneeded port forwarding.
- client-storage-flags (REASONED; server): v4.145.2 declares --disable-file-cache and --enable-remote-storage with no default; use the first on shared or untrusted clients and weigh the second for data at rest (inference); behaviour beyond their descriptions is not established.
- least-privilege (REASONED; server): Loopback limits inbound reach, not terminal/extension/proxied-service outbound access; minimize permissions and egress, including metadata/internal destinations.
- verify-origin (REASONED; server): ss inventories only this namespace; probe each public IPv4/IPv6 and port directly with intended TLS hostname; any HTTP response is reachability, and http=000 is inconclusive.
- verify-editor (REASONED; server): At the same editor URL, anonymous requests must reach login/challenge and valid-session requests the editor; a proxy 401 alone or failed positive control proves nothing.
- verify-mfa (REASONED; server): Password-only access must not open the editor while completing the second factor must; also confirm in a fresh browser.

````json
{
  "schema": 1,
  "checked": "2026-11-07",
  "documentation_checked": "2026-11",
  "body_sha256": "9b98e33f64642356b7ff76e3118b9bf636593a50b889e7cf3edc030618826da5",
  "components": {
    "server": {
      "name": "code-server",
      "basis": "v4.145.2",
      "sources": {
        "s6ab9e06105bb": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/docs/guide.md",
        "s2e220d3db1d3": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/cli.ts",
        "saade6a4c91ce": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/http.ts",
        "s3dc3c79d0206": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/routes/pathProxy.ts",
        "safbb0af6c9bc": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/src/node/routes/domainProxy.ts",
        "sd7cef350aeb5": "https://raw.githubusercontent.com/coder/code-server/v4.145.2/docs/FAQ.md"
      }
    }
  },
  "claims": {
    "ssh": {"text": "Vendor prefers SSH forwarding; bind the local 8080 forwarding listener to loopback and open the local browser URL.", "components": ["server"], "sources": ["server:s6ab9e06105bb"], "status": "REASONED"},
    "rocket-loader": {"text": "On the Cloudflare path, turn Rocket Loader off for the code-server hostname, because its re-injected scripts lack the CSP nonce; do not loosen the CSP, since 'unsafe-inline' does not help while a nonce is present (observed in source at v4.145.2, docs/guide.md).", "components": ["server"], "sources": ["server:s6ab9e06105bb"], "status": "REASONED"},
    "config": {"text": "Edit generated config.yaml and retain a supported credential; precreating it suppresses random-password generation and password auth without either credential fails startup.", "components": ["server"], "sources": ["server:sd7cef350aeb5", "server:s2e220d3db1d3"], "status": "REASONED"},
    "bind": {"text": "bind-addr 127.0.0.1:8080 keeps the editor private behind a proxy or tunnel.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:s2e220d3db1d3"], "status": "REASONED"},
    "auth-default": {"text": "auth defaults password; replace the generated value with a long random secret and protect config.yaml.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:s2e220d3db1d3"], "status": "REASONED"},
    "rate-limit": {"text": "Password attempts are limited to two per minute plus twelve per hour.", "components": ["server"], "sources": ["server:s6ab9e06105bb"], "status": "REASONED"},
    "credential-precedence": {"text": "PASSWORD/HASHED_PASSWORD override file credentials and hashed form wins; --password is not a supported CLI flag.", "components": ["server"], "sources": ["server:sd7cef350aeb5", "server:s2e220d3db1d3"], "status": "REASONED"},
    "config-precedence": {"text": "CLI flags override config; inspect --bind-addr, --config, CODE_SERVER_CONFIG and XDG_CONFIG_HOME for the effective launcher and file, plus CODE_SERVER_HOST, PORT, --host, --port, --socket and --socket-fd for the listener and CS_DISABLE_PROXY, which turns on --disable-proxy.", "components": ["server"], "sources": ["server:sd7cef350aeb5", "server:s2e220d3db1d3"], "status": "REASONED"},
    "tls-default": {"text": "cert defaults false; public access needs authenticated encryption, normally a reverse proxy with a trusted certificate.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:sd7cef350aeb5", "server:s2e220d3db1d3"], "status": "REASONED"},
    "tls-native": {"text": "Bare --cert or cert:true generates ~/.local/share/code-server/self-signed.crt; --cert with --cert-key selects supplied material; retain certificate validation.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:s2e220d3db1d3"], "status": "REASONED"},
    "mfa": {"text": "Built-in login is single-factor; fronting MFA must cover every enabled path, subdomain and WebSocket.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:saade6a4c91ce"], "status": "REASONED"},
    "path-proxy": {"text": "/proxy/<port>/ strips its prefix; /absproxy/<port>/ retains it; both use code-server authentication and auth:none exposes them.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:saade6a4c91ce", "server:s3dc3c79d0206"], "status": "REASONED"},
    "domain-proxy": {"text": "--proxy-domain exposes per-port subdomains using code-server authentication; apply fronting policy to each.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:saade6a4c91ce", "server:safbb0af6c9bc"], "status": "REASONED"},
    "proxy-domain-cookie": {"text": "Under --proxy-domain the v4.145.2 session cookie is scoped to that domain and carries a password-derived hash that code-server checks as authentication (observed in source), so a sibling host the browser sends it to, per its path and browser cookie rules, can replay it as the authentication cookie (inference); login-password acceptance is not established. Serve only code-server under that domain.", "components": ["server"], "sources": ["server:s2e220d3db1d3", "server:saade6a4c91ce", "server:safbb0af6c9bc"], "status": "REASONED"},
    "cookie-attributes": {"text": "The v4.145.2 session cookie is httpOnly with sameSite lax; getCookieOptions sets no Secure attribute at either tag (observed in source at v4.145.2 and v4.137.0), and whether anything else adds Secure is not established.", "components": ["server"], "sources": ["server:saade6a4c91ce"], "status": "REASONED"},
    "origin-check": {"text": "The v4.145.2 origin check needs an exact hostname match, treats default ports as none and may append X-Forwarded-Port; fix Host and X-Forwarded-Host/-Port at the proxy instead of widening --trusted-origins, where \"*\" turns the check off.", "components": ["server"], "sources": ["server:s2e220d3db1d3", "server:saade6a4c91ce"], "status": "REASONED"},
    "preflight": {"text": "--skip-auth-preflight allows unauthenticated preflight requests.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:s2e220d3db1d3"], "status": "REASONED"},
    "disable-proxy": {"text": "--disable-proxy turns off unneeded port forwarding.", "components": ["server"], "sources": ["server:s2e220d3db1d3", "server:saade6a4c91ce"], "status": "REASONED"},
    "client-storage-flags": {"text": "v4.145.2 declares --disable-file-cache and --enable-remote-storage with no default; use the first on shared or untrusted clients and weigh the second for data at rest (inference); behaviour beyond their descriptions is not established.", "components": ["server"], "sources": ["server:s2e220d3db1d3"], "status": "REASONED"},
    "least-privilege": {"text": "Loopback limits inbound reach, not terminal/extension/proxied-service outbound access; minimize permissions and egress, including metadata/internal destinations.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:saade6a4c91ce"], "status": "REASONED"},
    "verify-origin": {"text": "ss inventories only this namespace; probe each public IPv4/IPv6 and port directly with intended TLS hostname; any HTTP response is reachability, and http=000 is inconclusive.", "components": ["server"], "sources": ["server:s6ab9e06105bb"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "At the same editor URL, anonymous requests must reach login/challenge and valid-session requests the editor; a proxy 401 alone or failed positive control proves nothing.", "components": ["server"], "sources": ["server:s6ab9e06105bb", "server:saade6a4c91ce"], "status": "REASONED", "verify": [2]},
    "verify-mfa": {"text": "Password-only access must not open the editor while completing the second factor must; also confirm in a fresh browser.", "components": ["server"], "sources": ["server:s6ab9e06105bb"], "status": "REASONED", "verify": [2]}
  }
}
````
<!-- version-basis:end -->
