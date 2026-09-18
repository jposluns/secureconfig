# Streamlit: TLS and authentication

Streamlit apps have no access control unless you add it, and `streamlit run` listens on all interfaces on port `8501` by default (`server.address` unset, `server.port` `8501`). Decide both layers before exposing an app.

## 1. TLS

Preferred: keep Streamlit on loopback and terminate TLS in a reverse proxy or tunnel ([caddy.md](caddy.md), [nginx.md](nginx.md), [cloudflare.md](cloudflare.md)):

```toml
# .streamlit/config.toml
[server]
address = "127.0.0.1"
```

Point the proxy at `127.0.0.1:8501` and forward the WebSocket upgrade Streamlit depends on, applying the proxy's authentication to the upgrade as well as to ordinary requests (a separately unprotected WebSocket location bypasses the boundary) and preserving the browser's `Origin` header. For nginx, inside the authenticated `location /` block:

```nginx
proxy_pass http://127.0.0.1:8501;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_set_header Host $host;
```

Streamlit can serve HTTPS itself via `server.sslCertFile` and `server.sslKeyFile`, but its own documentation says not to use this in production ("It has not gone through security audits or performance tests") and to prefer a reverse proxy or load balancer. Treat the built-in TLS as a development convenience only:

```toml
[server]
sslCertFile = "/path/cert.pem"
sslKeyFile  = "/path/key.pem"
```

Leave `server.enableXsrfProtection` and `server.enableCORS` at their defaults (both `true`). Advice to disable them so uploads or embedding work behind a proxy removes protection rather than fixing the proxy; correct the proxy's forwarded headers and WebSocket upgrade instead. XSRF does not enable CORS or require a token when opening a WebSocket. Disabling CORS permits cross-origin WebSockets even with XSRF enabled. Keep both enabled; configure `server.corsAllowedOrigins` with origins and `server.allowedHosts` with hostnames. Configuring native authentication separately enables both protections. These are cross-site controls, not user authentication ([cors.md](cors.md)). Configuration precedence runs command-line over environment variables over the project `.streamlit/config.toml` (relative to the service's working directory) over the global config, so inspect the launch configuration actually in effect and restart after changing server settings; restrict writes to app code and configuration to deployment administrators, and note that `client.toolbarMode` only changes menu visibility and is not an authorization boundary.

## 2. Native login (OIDC)

Streamlit 1.64.0 provides `st.login()`, `st.logout()`, and `st.user` for OpenID Connect authentication against Google, Microsoft Entra ID, Okta, or any OIDC provider (`st.login()` and `st.logout()` were introduced in 1.42.0; `st.user` was introduced in 1.45.0, replacing `st.experimental_user`); install the `Authlib` package (1.3.2 or later) in the app's environment, without which the `[auth]` block errors. Configuration lives in `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "https://app.example.com/oauth2callback"
cookie_secret = "REPLACE_WITH_LONG_RANDOM_STRING"
client_id = "REPLACE_WITH_THE_CLIENT_ID"
client_secret = "REPLACE_WITH_THE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Authenticate and authorize before rendering protected data or performing side effects: with `st.navigation`, put the shared gate in the entrypoint before executing the selected page; with independent page scripts, gate every protected page; and recheck authorization inside privileged callbacks before their side effects. `st.login()` on its own accepts any account the provider will authenticate (with Google, any Google account), so check who logged in before showing anything:

```python
import streamlit as st

ALLOWED_DOMAIN = "example.com"

if not st.user.is_logged_in:
    st.login()
    st.stop()

if st.user.get("hd") != ALLOWED_DOMAIN:
    st.error("This account is not authorized for this app.")
    st.stop()

if not st.user.get("email_verified"):
    st.error("This account's email is not verified.")
    st.stop()

st.write(f"Hello, {st.user.name}")
```

Streamlit copies the ID token claims onto `st.user`, readable via `st.user.get(...)` or `st.user["..."]`. The `hd` (hosted domain) claim is the trusted Workspace-domain check (matching [oidc-integration.md](oidc-integration.md)): Google sets it only for Workspace and Cloud-organization accounts, and it is absent for consumer gmail.com accounts. For a small fixed user set, an explicit allowlist of addresses is the alternative. Allowlist rules and claim checks are in [oidc-integration.md](oidc-integration.md).

Notes from the Streamlit docs: this is authentication only (identity, not per-resource authorization), the identity cookie lasts 30 days and that period is not configurable, and `secrets.toml` holds the client secret, so it must never be committed. `st.secrets` exposes secrets to server-side app code but does not make them safe to display, so never render or log secret values; exclude `.streamlit/secrets.toml` from Git and image build contexts, restrict its filesystem access to the service and deployment administrators, keep it outside any served directory, and rotate an exposed client or cookie secret. In Streamlit 1.64.0, `client.showErrorDetails` accepts `"full"` (default), `"stacktrace"`, `"type"`, and `"none"`; the deprecated booleans `true` and `false` map to `"full"` and `"stacktrace"`. Set `showErrorDetails = "none"` under `[client]` to hide exception details from browsers; details remain in the console logs.

MFA: `st.login()` delegates authentication to the OIDC provider, so enforce MFA there (Google, Microsoft Entra ID, Okta, Keycloak, and authentik all support it). Without OIDC, front the app per section 3. Options in [mfa.md](mfa.md).

## 3. Alternatives when OIDC is not available

- Basic auth at a reverse proxy in front of a loopback-bound app ([nginx.md](nginx.md), [caddy.md](caddy.md)).
- Cloudflare Access in front of a tunnel ([cloudflare.md](cloudflare.md)), which adds SSO or one-time-PIN login without touching the app.

Basic auth or an emailed one-time PIN alone is not a second factor: for a sensitive app require MFA at the proxy or Access policy, disable alternative login methods that bypass it, and keep the Streamlit origin unreachable directly ([mfa.md](mfa.md)). A password typed into a plain `st.text_input` and compared in the script is not authentication; it ships no session management, no hashing, and no rate limiting.

## 4. Uploads, static files, and egress

`st.file_uploader` defaults to a 200 MB per-file limit, configured globally by `server.maxUploadSize`; an explicit per-widget `max_upload_size` overrides it. Lower the global limit, review every widget override, and rate-limit at the proxy; extension and MIME filters are best-effort, not content validation, and uploaded content must never be executed. `server.enableStaticServing` (default `false`) serves every file under the app's `static/` directory through `/app/static/`, a route answered by the server rather than your script, so an `st.login()` gate does not cover it: leave it off unless that directory holds only public files, and never place secrets or private data there. TLS and login do not sandbox Python, so never pass user input to `eval`, `exec`, a shell, or unsafe deserialization, and run the service with least filesystem privilege and minimal credentials (injection defense itself is application security, beyond this deployment guide's scope). If the app fetches user-supplied URLs, constrain the host's egress and block cloud metadata and unrelated internal networks per [egress-metadata.md](egress-metadata.md).

## 5. Verify

Reasoned, not demonstrated: the authoring environment has no Streamlit runtime or container runtime and cannot create listening sockets, so these describe the expected exposed and fixed outcomes rather than observed ones, and backlog row 2.36 tracks demonstrating them against a live 1.64.0 deployment. Use curl 7.75.0 or newer; never add `-k`. Substitute the public HTTPS origin, without a trailing slash, and the server's public address inside the single quotes on their respective `set --` lines, and paste each complete subshell.

```bash
ss -tlnp   # listeners on the origin host; 8501 must be 127.0.0.1 behind a proxy, not a public interface
# 1) TLS on the public origin, then the fronting-proxy anonymous check. A transport error (nonzero exit,
#    including a timeout) is inconclusive, not a pass. Native st.login serves an anonymous 200 on the index
#    BY DESIGN and gates inside the script over the websocket, so judge that pattern by the browser checks
#    below, not this HTTP status.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_HTTPS_ORIGIN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one origin; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute your HTTPS origin; not probing"; exit 2 ;;
    https://*) ;;
    *) echo "use an HTTPS origin; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
    -w 'tls=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/" || exit "$?"
  # Authentication-proxy deployments only: inspect this route's policy and response.
  # Native st.login permits anonymous index requests; use the browser controls below.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -D - \
    -w '\nanon=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/_stcore/health"
)
# 3) From another host, port 8501 must not answer directly, or the proxy is bypassable. Any HTTP code,
#    including a 200 "ok", means 8501 answered externally (the finding); a refused or no-route connection
#    is consistent with closure but not proof; a DNS or local socket error or a timeout is inconclusive.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVER_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the server's public address on the set -- line above; not probing"; exit 2 ;;
    *) curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8501/_stcore/health" ;;
  esac
)
```

Then check the application gate in a browser, using the same scheme, hostname, port, and protected page for every comparison. In a fresh profile with no session an anonymous visitor must not see protected content or reach a protected operation; an allowed user who completes the provider's MFA must; and a valid identity outside the allowlist (for the `hd` check, a consumer account) must be denied with nothing rendered. Visit every protected page directly, including administrative ones. A login page, a blank page, or a broken websocket is not a positive control. In an isolated test deployment only, place `st.write("SECURECONFIG_AUTH_CANARY")` after the gate, disable the applicable authentication boundary, and confirm the anonymous visit then reveals the canary; restore protection afterward, and never disable authentication on a public deployment. For a fronting proxy, confirm an unauthenticated websocket upgrade is also denied and that an authenticated browser can establish it.

## Sources (checked September 2026)

Source-checked on 2026-09-18 against Streamlit 1.64.0, the current release at the time of writing; `server.address` defaults to unset (all interfaces) and `server.port` to `8501`, and the explicit loopback setting above is required for the fronting-proxy pattern. `st.login()` has been available since the 1.42.0 series.

- config.toml reference (server.address, server.sslCertFile, server.sslKeyFile, and the production warning): https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- Authentication concepts (st.login, st.logout, st.user, [auth] keys, default scope, stated limitations): https://docs.streamlit.io/develop/concepts/connections/authentication
- st.user API reference (claims copied from the ID token, `st.user.email`): https://docs.streamlit.io/develop/api-reference/user/st.user
- Streamlit release notes (1.64.0 current; st.login since the 1.42.0 series): https://docs.streamlit.io/develop/quick-reference/release-notes
- st.login reference (OIDC, Authlib 1.3.2+ dependency): https://docs.streamlit.io/develop/api-reference/user/st.login
- Configuration options and precedence (command line over env over project over global; restart on server changes): https://docs.streamlit.io/develop/concepts/configuration/options
- config.toml (enableCORS, enableXsrfProtection, maxUploadSize, enableStaticServing, showErrorDetails): https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- Static file serving (server.enableStaticServing default false, served by the server not the script): https://docs.streamlit.io/develop/concepts/configuration/serving-static-files
- st.file_uploader (maxUploadSize per-file limit; filters are not content validation): https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
- Secrets management and security reminders (never render or log secrets): https://docs.streamlit.io/develop/concepts/connections/security-reminders
- App health endpoint (/_stcore/health, no authentication): https://docs.streamlit.io/deploy/tutorials/docker
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- curl manual (write-out variables require 7.75.0+): https://curl.se/docs/manpage.html
