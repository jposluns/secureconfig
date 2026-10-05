---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-10",
  "body_sha256": "244e41fe5f5e792b05f6d0b76d999db50ceb8a0a30c8ea7bc040320f3cdda923",
  "components": {
    "streamlit": {
      "name": "Streamlit",
      "basis": "1.64.0",
      "sources": {
        "s208ef00c9507": "https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/config.py#L1016-L1036",
        "s7e4fdd54875d": "https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L80-L98",
        "s41a3660b1c7b": "https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L139-L160",
        "s50b333f0759f": "https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L363-L400",
        "sa98504c29424": "https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server_config.py#L55-L57",
        "s9d96cdf36131": "https://pypi.org/project/streamlit/1.64.0/"
      }
    },
    "ssrf": {
      "name": "OWASP SSRF guidance",
      "basis": "unknown",
      "sources": {
        "s7eb820e1e53b": "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "authlib": {
      "name": "Authlib minimum",
      "basis": "1.3.2",
      "sources": {
        "s9d96cdf36131": "https://pypi.org/project/streamlit/1.64.0/"
      }
    },
    "httpx": {
      "name": "httpx minimum",
      "basis": "0.24.1",
      "sources": {
        "s9d96cdf36131": "https://pypi.org/project/streamlit/1.64.0/"
      }
    },
    "streamlit-rolling": {
      "name": "Streamlit documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s560ba59f10f9": "https://docs.streamlit.io/develop/api-reference/configuration/config.toml",
        "s5b7392df2d3a": "https://docs.streamlit.io/develop/concepts/connections/authentication",
        "s3f8bf05ddb38": "https://docs.streamlit.io/develop/api-reference/user/st.user",
        "s1322a5f1d6a0": "https://docs.streamlit.io/develop/api-reference/user/st.login",
        "s91c471ec9924": "https://docs.streamlit.io/develop/concepts/configuration/options",
        "s6f8f2b27ef37": "https://docs.streamlit.io/develop/concepts/configuration/serving-static-files",
        "sd09e0d235dd6": "https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader",
        "s720555b11b6e": "https://docs.streamlit.io/develop/concepts/connections/security-reminders",
        "s66e514173b37": "https://docs.streamlit.io/deploy/tutorials/docker"
      }
    },
    "release-notes": {
      "name": "Streamlit release notes",
      "basis": "unknown",
      "sources": {
        "s6f6f9b0b14c2": "https://docs.streamlit.io/develop/quick-reference/release-notes",
        "se2c98289aac5": "https://docs.streamlit.io/develop/quick-reference/release-notes/2025#version-1420"
      }
    },
    "caddy": {
      "name": "Caddy",
      "basis": "v2.11.4",
      "sources": {
        "sb0b62262df7b": "https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/builtins.go#L58-L88",
        "s9702adeb8c11": "https://raw.githubusercontent.com/caddyserver/caddy/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go",
        "s6b8d900baeb9": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/caddyfile.go#L29-L36"
      }
    },
    "oauth2-proxy": {
      "name": "oauth2-proxy",
      "basis": "v7.15.4",
      "sources": {
        "s088c1baa445d": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/pkg/apis/options/options.go#L141"
      }
    },
    "keycloak": {
      "name": "Keycloak",
      "basis": "26.7.4",
      "sources": {
        "sf802dc9c4313": "https://raw.githubusercontent.com/keycloak/keycloak/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc",
        "se52072c97d20": "https://github.com/keycloak/keycloak/blob/26.7.4/services/src/main/java/org/keycloak/protocol/oidc/mappers/UserAttributeMapper.java#L96-L104"
      }
    }
  },
  "claims": {
    "bind-default": {"text": "server.address is unset and binds wildcard: try :: when IPv6 is supported, then 0.0.0.0 if unavailable; wildcard behavior was not demonstrated.", "components": ["streamlit"], "sources": ["streamlit:s208ef00c9507", "streamlit:s7e4fdd54875d", "streamlit:s41a3660b1c7b"], "status": "REASONED"},
    "port-default": {"text": "server.port defaults 8501 and may try 100 following ports when not explicitly set; explicitly configure 8501 to prevent that fallback.", "components": ["streamlit"], "sources": ["streamlit:s208ef00c9507", "streamlit:s50b333f0759f", "streamlit:sa98504c29424"], "status": "REASONED"},
    "private-bind": {"text": "Loopback proxy configuration keeps Streamlit on 127.0.0.1:8501; observed inventory is local, not proof of external isolation.", "components": ["streamlit", "streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9", "streamlit:s208ef00c9507"], "status": "DEMONSTRATED", "evidence": "On the loopback runs, with `server.address` set to `127.0.0.1`, `ss` showed Streamlit only on `127.0.0.1:8501`."},
    "proxy-websocket": {"text": "Proxy authentication must cover WebSocket upgrades as well as HTTP; a separately unprotected /_stcore/stream can expose app output despite index/health 401.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s66e514173b37"], "status": "DEMONSTRATED", "evidence": "the index and the health route still returned `401`, but an anonymous client that opened `/_stcore/stream` and asked for a script run received the app's output, the canary."},
    "native-tls": {"text": "sslCertFile/sslKeyFile provide native TLS for development; vendor recommends a production reverse proxy, with WebSocket upgrade and browser Origin preserved.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9"], "status": "REASONED"},
    "xsrf": {"text": "enableXsrfProtection defaults true; it does not enable CORS or require a token when opening a WebSocket.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9"], "status": "REASONED"},
    "cors": {"text": "enableCORS defaults true; disabling it permits cross-origin WebSockets even with XSRF; use corsAllowedOrigins and allowedHosts, and native auth separately enables both protections.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9"], "status": "REASONED"},
    "config": {"text": "Effective precedence is CLI, environment, project config relative to working directory, then global; restart for server changes and restrict deployment writes.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s91c471ec9924"], "status": "REASONED"},
    "toolbar": {"text": "client.toolbarMode affects menu visibility, not authorization.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9"], "status": "REASONED"},
    "oidc-versions": {"text": "st.login/st.logout date from 1.42.0; st.user from 1.45.0 replaces experimental_user; 1.64.0 auth extra needs Authlib>=1.3.2 and httpx>=0.24.1.", "components": ["streamlit", "authlib", "httpx", "streamlit-rolling", "release-notes"], "sources": ["release-notes:s6f6f9b0b14c2", "release-notes:se2c98289aac5", "streamlit-rolling:s1322a5f1d6a0", "streamlit:s9d96cdf36131", "authlib:s9d96cdf36131", "httpx:s9d96cdf36131"], "status": "REASONED"},
    "oidc-dependencies": {"text": "Recorded loopback login with Authlib but without httpx failed; install the complete auth extra.", "components": ["streamlit"], "sources": ["streamlit:s9d96cdf36131"], "status": "DEMONSTRATED", "evidence": "every browser login attempt got `Internal Server Error`, with `ModuleNotFoundError: No module named 'httpx'` in Streamlit's log."},
    "oidc-config": {"text": "secrets.toml auth config supplies redirect_uri, cookie_secret, client_id/client_secret and metadata URL; st.login authenticates identity, not resource authorization.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s1322a5f1d6a0"], "status": "REASONED"},
    "page-gates": {"text": "Gate protected pages before rendering/side effects, before st.navigation page execution, and recheck authorization inside privileged callbacks.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "REASONED"},
    "native-gate": {"text": "In the recorded Keycloak claim fixture, native login plus hd/email_verified checks admitted the allowed user and denied other-domain, missing-hd and unverified users.", "components": ["streamlit-rolling", "keycloak"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s3f8bf05ddb38", "keycloak:se52072c97d20"], "status": "DEMONSTRATED", "evidence": "The user in another domain, and the user with no `hd` attribute, saw \"This account is not authorized for this app.\""},
    "email-gate": {"text": "Recorded native gate denied unverified email; login without hd/email checks allowed the exposed fixture's other-domain and unverified users.", "components": ["streamlit-rolling", "keycloak"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s3f8bf05ddb38", "keycloak:se52072c97d20"], "status": "DEMONSTRATED", "evidence": "The unverified user saw \"This account's email is not verified.\""},
    "claims": {"text": "st.user contains ID-token claims; Google hd identifies Workspace/Cloud accounts and is absent for consumer accounts; explicit address allowlisting is an alternative.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s3f8bf05ddb38"], "status": "REASONED"},
    "cookie": {"text": "Native identity cookie lasts 30 days and the lifetime is not configurable.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "REASONED"},
    "secrets": {"text": "Keep secrets.toml out of Git, build contexts and served directories; restrict access, never render/log st.secrets, and rotate exposed client/cookie secrets.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s720555b11b6e"], "status": "REASONED"},
    "errors": {"text": "showErrorDetails defaults full; stacktrace/type/none are alternatives, deprecated true/false map to full/stacktrace; none hides browser details while console logs retain them.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9"], "status": "REASONED"},
    "mfa": {"text": "OIDC MFA must be enforced at the provider; Basic auth or emailed PIN alone is not MFA, and alternative login paths/direct origin must not bypass policy.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "REASONED"},
    "password-widget": {"text": "A plain text_input password comparison provides no session management, hashing or rate limiting.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "REASONED"},
    "uploads": {"text": "file_uploader defaults 200 MB per file via maxUploadSize; widget max_upload_size overrides it; filters are best-effort, not content validation; rate-limit and never execute uploads.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9", "streamlit-rolling:sd09e0d235dd6"], "status": "REASONED"},
    "static-default": {"text": "enableStaticServing defaults false; enabled /app/static/ is served outside script login, so static/ must contain only public files.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9", "streamlit-rolling:s6f8f2b27ef37"], "status": "REASONED"},
    "static-test": {"text": "Recorded static serving bypassed st.stop; enabled returned marker text and disabled returned app HTML, both 200, so inspect the body.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s6f8f2b27ef37"], "status": "DEMONSTRATED", "evidence": "with `server.enableStaticServing` on, the script called `st.stop()` at once, yet `/app/static/public.txt` returned the file with `200` and `text/plain`. With it off, the same path returned `200` with the app's HTML page, not the file."},
    "execution-egress": {"text": "TLS/login do not sandbox Python; use least privilege and minimal credentials, avoid executing inputs, and restrict URL-fetch egress including metadata/internal networks.", "components": ["ssrf", "streamlit-rolling"], "sources": ["streamlit-rolling:s720555b11b6e", "ssrf:s7eb820e1e53b"], "status": "REASONED"},
    "verify-tls": {"text": "Recorded native TLS returned 200 with the trusted test CA and failed trust with exit 60; never use -k.", "components": ["curl", "streamlit-rolling"], "sources": ["streamlit-rolling:s560ba59f10f9", "curl:s2b2686afaf41"], "status": "DEMONSTRATED", "evidence": "**Block 1 against native TLS:** `tls=200` with the test CA trusted. With curl not trusting the certificate it stopped at `tls=000 exit=60`."},
    "verify-proxy": {"text": "Recorded Caddy loopback Basic-auth comparison returned exposed health 200/ok versus fixed 401; wrong credentials also failed and valid sessions received the canary.", "components": ["streamlit-rolling", "caddy"], "sources": ["streamlit-rolling:s5b7392df2d3a", "streamlit-rolling:s66e514173b37", "caddy:sb0b62262df7b", "caddy:s9702adeb8c11", "caddy:s6b8d900baeb9"], "status": "DEMONSTRATED", "evidence": "Block 1 got `401` on both requests, and a wrong credential also got `401`."},
    "verify-oidc-proxy": {"text": "Recorded oauth2-proxy/Keycloak fixture redirected anonymous health and WebSocket requests; an allowed user reached the canary after password/TOTP, with other-domain 403.", "components": ["streamlit-rolling", "oauth2-proxy", "keycloak"], "sources": ["streamlit-rolling:s5b7392df2d3a", "oauth2-proxy:s088c1baa445d", "keycloak:sf802dc9c4313"], "status": "DEMONSTRATED", "evidence": "The anonymous health request got a `302`, and an anonymous websocket upgrade was redirected to the provider's authorization endpoint instead of upgraded."},
    "verify-native-browser": {"text": "Native anonymous index is intentionally 200; browser comparisons must check protected content, valid users, domain/email denial and MFA rather than index status.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "DEMONSTRATED", "evidence": "The anonymous index returned `200` by design, and the anonymous browser was sent to the provider's sign-in page."},
    "verify-mfa": {"text": "Recorded allowed native user reached the canary after TOTP; wrong code retained the provider's code prompt, using a loopback Keycloak fixture rather than Google.", "components": ["streamlit-rolling", "keycloak"], "sources": ["streamlit-rolling:s5b7392df2d3a", "keycloak:sf802dc9c4313"], "status": "DEMONSTRATED", "evidence": "The allowed user rendered the canary after enrolling and then entering TOTP codes; a wrong code kept them at the one-time-code prompt."},
    "verify-external": {"text": "From another host any direct 8501 HTTP response is an exposure; refusal/no-route is not proof and DNS/local errors/timeouts are inconclusive; second-host vantage was unavailable.", "components": ["streamlit", "curl", "streamlit-rolling"], "sources": ["streamlit:s208ef00c9507", "streamlit:s7e4fdd54875d", "streamlit-rolling:s66e514173b37", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-local-reachability": {"text": "Recorded same-host probe distinguished a listening address from another loopback address; it does not demonstrate the external scenario.", "components": ["curl", "streamlit-rolling"], "sources": ["streamlit-rolling:s66e514173b37", "curl:s2b2686afaf41"], "status": "DEMONSTRATED", "evidence": "**Block 3 from the same host:** `http=200` against the address Streamlit listened on, and `exit=7` against another loopback address."},
    "verify-pages": {"text": "Test every protected page and operation with anonymous, allowed and disallowed users, restoring an isolated exposed canary comparison; broken WebSockets or blank pages are not positive controls.", "components": ["streamlit-rolling"], "sources": ["streamlit-rolling:s5b7392df2d3a"], "status": "REASONED"},
    "curl-version": {"text": "Use curl 7.75.0+ for diagnostic variables and keep certificate validation enabled.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED"},
    "verify-fence": {"text": "Combined fence remains REASONED because wildcard binding and second-host isolation were unavailable; the recorded loopback sub-results are separate historical demonstrated claims.", "components": ["streamlit", "curl", "streamlit-rolling"], "sources": ["streamlit:s208ef00c9507", "streamlit:s7e4fdd54875d", "streamlit-rolling:s66e514173b37", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]}
  }
}
---
# Streamlit: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-10 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| bind-default: server.address is unset and binds wildcard: try :: when IPv6 is supported, then 0.0.0.0 if unavailable; wildcard behavior was not demonstrated. | Streamlit 1.64.0 | REASONED |
| port-default: server.port defaults 8501 and may try 100 following ports when not explicitly set; explicitly configure 8501 to prevent that fallback. | Streamlit 1.64.0 | REASONED |
| private-bind: Loopback proxy configuration keeps Streamlit on 127.0.0.1:8501; observed inventory is local, not proof of external isolation. | Streamlit 1.64.0; Streamlit documentation (rolling) unknown | DEMONSTRATED |
| proxy-websocket: Proxy authentication must cover WebSocket upgrades as well as HTTP; a separately unprotected /_stcore/stream can expose app output despite index/health 401. | Streamlit documentation (rolling) unknown | DEMONSTRATED |
| native-tls: sslCertFile/sslKeyFile provide native TLS for development; vendor recommends a production reverse proxy, with WebSocket upgrade and browser Origin preserved. | Streamlit documentation (rolling) unknown | REASONED |
| xsrf: enableXsrfProtection defaults true; it does not enable CORS or require a token when opening a WebSocket. | Streamlit documentation (rolling) unknown | REASONED |
| cors: enableCORS defaults true; disabling it permits cross-origin WebSockets even with XSRF; use corsAllowedOrigins and allowedHosts, and native auth separately enables both protections. | Streamlit documentation (rolling) unknown | REASONED |
| config: Effective precedence is CLI, environment, project config relative to working directory, then global; restart for server changes and restrict deployment writes. | Streamlit documentation (rolling) unknown | REASONED |
| toolbar: client.toolbarMode affects menu visibility, not authorization. | Streamlit documentation (rolling) unknown | REASONED |
| oidc-versions: st.login/st.logout date from 1.42.0; st.user from 1.45.0 replaces experimental_user; 1.64.0 auth extra needs Authlib&gt;=1.3.2 and httpx&gt;=0.24.1. | Streamlit 1.64.0; Authlib minimum 1.3.2; httpx minimum 0.24.1; Streamlit documentation (rolling) unknown; Streamlit release notes unknown | REASONED |
| oidc-dependencies: Recorded loopback login with Authlib but without httpx failed; install the complete auth extra. | Streamlit 1.64.0 | DEMONSTRATED |
| oidc-config: secrets.toml auth config supplies redirect_uri, cookie_secret, client_id/client_secret and metadata URL; st.login authenticates identity, not resource authorization. | Streamlit documentation (rolling) unknown | REASONED |
| page-gates: Gate protected pages before rendering/side effects, before st.navigation page execution, and recheck authorization inside privileged callbacks. | Streamlit documentation (rolling) unknown | REASONED |
| native-gate: In the recorded Keycloak claim fixture, native login plus hd/email_verified checks admitted the allowed user and denied other-domain, missing-hd and unverified users. | Streamlit documentation (rolling) unknown; Keycloak 26.7.4 | DEMONSTRATED |
| email-gate: Recorded native gate denied unverified email; login without hd/email checks allowed the exposed fixture's other-domain and unverified users. | Streamlit documentation (rolling) unknown; Keycloak 26.7.4 | DEMONSTRATED |
| claims: st.user contains ID-token claims; Google hd identifies Workspace/Cloud accounts and is absent for consumer accounts; explicit address allowlisting is an alternative. | Streamlit documentation (rolling) unknown | REASONED |
| cookie: Native identity cookie lasts 30 days and the lifetime is not configurable. | Streamlit documentation (rolling) unknown | REASONED |
| secrets: Keep secrets.toml out of Git, build contexts and served directories; restrict access, never render/log st.secrets, and rotate exposed client/cookie secrets. | Streamlit documentation (rolling) unknown | REASONED |
| errors: showErrorDetails defaults full; stacktrace/type/none are alternatives, deprecated true/false map to full/stacktrace; none hides browser details while console logs retain them. | Streamlit documentation (rolling) unknown | REASONED |
| mfa: OIDC MFA must be enforced at the provider; Basic auth or emailed PIN alone is not MFA, and alternative login paths/direct origin must not bypass policy. | Streamlit documentation (rolling) unknown | REASONED |
| password-widget: A plain text_input password comparison provides no session management, hashing or rate limiting. | Streamlit documentation (rolling) unknown | REASONED |
| uploads: file_uploader defaults 200 MB per file via maxUploadSize; widget max_upload_size overrides it; filters are best-effort, not content validation; rate-limit and never execute uploads. | Streamlit documentation (rolling) unknown | REASONED |
| static-default: enableStaticServing defaults false; enabled /app/static/ is served outside script login, so static/ must contain only public files. | Streamlit documentation (rolling) unknown | REASONED |
| static-test: Recorded static serving bypassed st.stop; enabled returned marker text and disabled returned app HTML, both 200, so inspect the body. | Streamlit documentation (rolling) unknown | DEMONSTRATED |
| execution-egress: TLS/login do not sandbox Python; use least privilege and minimal credentials, avoid executing inputs, and restrict URL-fetch egress including metadata/internal networks. | OWASP SSRF guidance unknown; Streamlit documentation (rolling) unknown | REASONED |
| verify-tls: Recorded native TLS returned 200 with the trusted test CA and failed trust with exit 60; never use -k. | curl minimum write-out version 7.75.0; Streamlit documentation (rolling) unknown | DEMONSTRATED |
| verify-proxy: Recorded Caddy loopback Basic-auth comparison returned exposed health 200/ok versus fixed 401; wrong credentials also failed and valid sessions received the canary. | Streamlit documentation (rolling) unknown; Caddy v2.11.4 | DEMONSTRATED |
| verify-oidc-proxy: Recorded oauth2-proxy/Keycloak fixture redirected anonymous health and WebSocket requests; an allowed user reached the canary after password/TOTP, with other-domain 403. | Streamlit documentation (rolling) unknown; oauth2-proxy v7.15.4; Keycloak 26.7.4 | DEMONSTRATED |
| verify-native-browser: Native anonymous index is intentionally 200; browser comparisons must check protected content, valid users, domain/email denial and MFA rather than index status. | Streamlit documentation (rolling) unknown | DEMONSTRATED |
| verify-mfa: Recorded allowed native user reached the canary after TOTP; wrong code retained the provider's code prompt, using a loopback Keycloak fixture rather than Google. | Streamlit documentation (rolling) unknown; Keycloak 26.7.4 | DEMONSTRATED |
| verify-external: From another host any direct 8501 HTTP response is an exposure; refusal/no-route is not proof and DNS/local errors/timeouts are inconclusive; second-host vantage was unavailable. | Streamlit 1.64.0; curl minimum write-out version 7.75.0; Streamlit documentation (rolling) unknown | REASONED |
| verify-local-reachability: Recorded same-host probe distinguished a listening address from another loopback address; it does not demonstrate the external scenario. | curl minimum write-out version 7.75.0; Streamlit documentation (rolling) unknown | DEMONSTRATED |
| verify-pages: Test every protected page and operation with anonymous, allowed and disallowed users, restoring an isolated exposed canary comparison; broken WebSockets or blank pages are not positive controls. | Streamlit documentation (rolling) unknown | REASONED |
| curl-version: Use curl 7.75.0+ for diagnostic variables and keep certificate validation enabled. | curl minimum write-out version 7.75.0 | REASONED |
| verify-fence: Combined fence remains REASONED because wildcard binding and second-host isolation were unavailable; the recorded loopback sub-results are separate historical demonstrated claims. | Streamlit 1.64.0; curl minimum write-out version 7.75.0; Streamlit documentation (rolling) unknown | REASONED |
<!-- version-basis:end -->

Streamlit apps have no access control unless you add it, and `streamlit run` listens on all interfaces on port `8501` by default (as of 1.64.0: `server.address` unset, which falls back to `0.0.0.0` and tries `::` first when Python supports IPv6, falling back to `0.0.0.0` if IPv6 is unavailable; `server.port` `8501`, and when that port is busy and was not set explicitly, Streamlit tries up to 100 following ports). Decide both layers before exposing an app.

## 1. TLS

Preferred: keep Streamlit on loopback and terminate TLS in a reverse proxy or tunnel ([caddy.md](caddy.md), [nginx.md](nginx.md), [cloudflare.md](cloudflare.md)):

```toml
# .streamlit/config.toml
[server]
address = "127.0.0.1"
port = 8501   # set explicitly: an unset port moves to 8502 and up when 8501 is busy, past the proxy and these checks
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

Streamlit 1.64.0 provides `st.login()`, `st.logout()`, and `st.user` for OpenID Connect authentication against Google, Microsoft Entra ID, Okta, or any OIDC provider (`st.login()` and `st.logout()` were introduced in 1.42.0; `st.user` was introduced in 1.45.0, replacing `st.experimental_user`); install Streamlit's `auth` extra in the app's environment (`pip install "streamlit[auth]"`), which in 1.64.0 requires `Authlib` 1.3.2 or later and `httpx` 0.24.1 or later; without Authlib the `[auth]` block errors, and in the loopback run with Authlib installed but not httpx every browser login attempt got `Internal Server Error`, with `ModuleNotFoundError: No module named 'httpx'` in Streamlit's log. Configuration lives in `.streamlit/secrets.toml`:

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

Verification status: the checks below were demonstrated on loopback against Streamlit 1.64.0 (the PyPI wheel, its SHA-256 equal to PyPI's published digest), with native `st.login`, and behind Caddy v2.11.4 and oauth2-proxy v7.15.4, using Keycloak 26.7.4 as the OIDC provider, in the exposed and fixed states. The wildcard bind and block 3's external vantage are REASONED and marked at their steps; the end of this section records what was observed. Use curl 7.75.0 or newer; never add `-k`. Substitute the public HTTPS origin, without a trailing slash, and the server's public address inside the single quotes on their respective `set --` lines, and paste each complete subshell.

```bash
# REASONED: whole-block scope includes wildcard binding and second-host reachability, unavailable in the recorded loopback runs; demonstrated sub-results and source reasoning are recorded below.
ss -tlnp   # listeners on the origin host; 8501 must be 127.0.0.1 behind a proxy, not a public interface
           # (loopback runs saw 127.0.0.1:8501; the default wildcard bind is REASONED: the host forbids it)
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
#    REASONED from another host: the loopback runs had one host and no second network (see below).
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

On the loopback runs, with `server.address` set to `127.0.0.1`, `ss` showed Streamlit only on `127.0.0.1:8501`. With the address unset, `streamlit config show` lists it as unset, and Streamlit 1.64.0's source tries the IPv6 wildcard `::` first in that case when `socket.has_ipv6` holds, retrying `0.0.0.0` if IPv6 is unavailable (`_get_bind_address` and `_bind_server_socket` in `web/server/starlette/starlette_server.py`). That bind is REASONED, because the host forbids listening on every interface. The runs used Caddy and oauth2-proxy on `127.0.0.1:8443`, with TLS files from a private test CA that curl trusted through `CURL_CA_BUNDLE`, and a headless Chrome 154 with an SPKI exception for the test certificate's key.

The Keycloak realm was served over plain HTTP on loopback. Section 2's example uses an HTTPS metadata URL, as a real provider should. The realm had four users, and three of them had an `hd` user attribute, which a user-attribute mapper, standing in for Google's, maps to an `hd` claim:
- an allowed user in `example.com` with a verified email and TOTP required;
- a verified user in another domain;
- an `example.com` user whose email was not verified;
- a verified `example.com` user with no `hd` user attribute, standing in for a consumer account without the claim.

What each run observed:

- **Block 1 against native TLS:** `tls=200` with the test CA trusted. With curl not trusting the certificate it stopped at `tls=000 exit=60`.
- **Proxy with no authentication (exposed):** block 1 printed `tls=200`, then `anon=200` with the body `ok`, which is the finding. A websocket upgrade to `/_stcore/stream` got `101` anonymously, and an anonymous browser rendered the canary.
- **[caddy.md](caddy.md)'s `basic_auth` covering every route (fixed):**
  - Block 1 got `401` on both requests, and a wrong credential also got `401`.
  - An app session over the websocket was refused with `401` anonymously and with the wrong credential, and received the canary with the right one.
  - The anonymous browser and the browser sending the wrong credential saw an empty page; the browser sending the credential rendered the canary.
- **Websocket path in a separate unauthenticated location (exposed):** the index and the health route still returned `401`, but an anonymous client that opened `/_stcore/stream` and asked for a script run received the app's output, the canary. That is the bypass section 1 describes.
- **oauth2-proxy with Keycloak, restricted to `example.com` (fixed):**
  - The anonymous health request got a `302`, and an anonymous websocket upgrade was redirected to the provider's authorization endpoint instead of upgraded.
  - The anonymous browser stopped at the provider's sign-in page.
  - The allowed user rendered the canary after the password and a TOTP code; with a wrong code the provider kept them at the one-time-code prompt ("Invalid authenticator code.").
  - The user in another domain got oauth2-proxy's `403 Forbidden`.
  - The unverified user got oauth2-proxy's `500 Internal Server Error` page, with oauth2-proxy logging "email in id_token … isn't verified".
- **oauth2-proxy with `--email-domain='*'` (exposed allowlist):** the user in another domain rendered the canary.
- **Native `st.login` with section 2's gate** (the guide's code, with only the final `Hello` line replaced by the canary):
  - The anonymous index returned `200` by design, and the anonymous browser was sent to the provider's sign-in page.
  - The allowed user rendered the canary after enrolling and then entering TOTP codes; a wrong code kept them at the one-time-code prompt.
  - The user in another domain, and the user with no `hd` attribute, saw "This account is not authorized for this app."
  - The unverified user saw "This account's email is not verified."
  - None of those three saw the canary.
- **Native `st.login` exposed states:**
  - With only the `st.login()` check and no `hd` or email check, the user in another domain and the unverified user each rendered the canary.
  - With no gate at all, an anonymous browser rendered it.
- **Block 3 from the same host:** `http=200` against the address Streamlit listened on, and `exit=7` against another loopback address.
- **Static serving:** with `server.enableStaticServing` on, the script called `st.stop()` at once, yet `/app/static/public.txt` returned the file with `200` and `text/plain`. With it off, the same path returned `200` with the app's HTML page, not the file. Judge a static-route probe by its body, not its status.

REASONED from the cited Streamlit 1.64.0 source and the recorded loopback observations:
- an external vantage for block 3, since there was one host with no second network;
- the default wildcard bind, since the host forbids binding every interface.

## Sources (checked October 2026)

Source-checked on 2026-09-18 against Streamlit 1.64.0, the current release at the time of writing; `server.address` defaults to unset (all interfaces) and `server.port` to `8501`, and the explicit loopback setting above is required for the fronting-proxy pattern. `st.login()` has been available since the 1.42.0 series.

- Streamlit config.toml reference, server.address, server.sslCertFile, server.sslKeyFile and the production warning (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- Streamlit `server.address` default unset and `server.port` default `8501` (pinned tag 1.64.0): https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/config.py#L1016-L1036
- Streamlit's unset address falls back to `DEFAULT_SERVER_ADDRESS` `0.0.0.0` and is tried as `::` when `socket.has_ipv6` (pinned tag 1.64.0): https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L80-L98
- Streamlit retries `0.0.0.0` when binding `::` fails with an IPv6-unavailable error (pinned tag 1.64.0): https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L139-L160
- Streamlit's port search: `configured_port + attempt` for up to `MAX_PORT_SEARCH_RETRIES` (100) retries after the configured port, exiting instead on a busy (`EADDRINUSE`) or permission-denied (`EACCES`) port that was set explicitly (a value from `config.toml` counts; `config.py` `is_manually_set`) (pinned tag 1.64.0): https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server.py#L363-L400, with `MAX_PORT_SEARCH_RETRIES: Final = 100` defined in `starlette_server_config.py`: https://github.com/streamlit/streamlit/blob/1.64.0/lib/streamlit/web/server/starlette/starlette_server_config.py#L55-L57
- Streamlit authentication concepts, st.login, st.logout, st.user, [auth] keys, default scope and stated limitations (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/concepts/connections/authentication
- Streamlit st.user API reference, claims copied from the ID token and `st.user.email` (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/api-reference/user/st.user
- Streamlit release notes (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/quick-reference/release-notes
- Streamlit 2025 release notes, st.login and st.logout introduced in 1.42.0: https://docs.streamlit.io/develop/quick-reference/release-notes/2025#version-1420
- Streamlit st.login reference, OIDC and Authlib 1.3.2+ dependency (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/api-reference/user/st.login
- Streamlit 1.64.0 package metadata (the `auth` extra requires `Authlib>=1.3.2` and `httpx>=0.24.1`): https://pypi.org/project/streamlit/1.64.0/
- Streamlit configuration options and precedence, command line over env over project over global; restart on server changes (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/concepts/configuration/options
- Streamlit config.toml, enableCORS, enableXsrfProtection, maxUploadSize, enableStaticServing and showErrorDetails (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- Streamlit static file serving, server.enableStaticServing default false; served by the server, not the script (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/concepts/configuration/serving-static-files
- Streamlit st.file_uploader, maxUploadSize per-file limit; filters are not content validation (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
- Streamlit secrets management and security reminders, never render or log secrets (rolling documentation, checked September 2026): https://docs.streamlit.io/develop/concepts/connections/security-reminders
- Streamlit app health endpoint, /_stcore/health without authentication (rolling documentation, checked September 2026): https://docs.streamlit.io/deploy/tutorials/docker
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- curl manual (write-out variables require 7.75.0+): https://curl.se/docs/manpage.html
- Caddy bind, certificate files, and reverse-proxy configuration (pinned tag v2.11.4): https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/builtins.go#L58-L88, https://raw.githubusercontent.com/caddyserver/caddy/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go
- Caddy basic_auth configuration and default bcrypt hashing (pinned tag v2.11.4): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/caddyauth/caddyfile.go#L29-L36
- oauth2-proxy email-domain restriction and wildcard configuration (pinned tag v7.15.4): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/pkg/apis/options/options.go#L141
- Keycloak TOTP policy and user-attribute-to-token-claim mapper used by the recorded fixture (pinned tag 26.7.4): https://raw.githubusercontent.com/keycloak/keycloak/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc, https://github.com/keycloak/keycloak/blob/26.7.4/services/src/main/java/org/keycloak/protocol/oidc/mappers/UserAttributeMapper.java#L96-L104
