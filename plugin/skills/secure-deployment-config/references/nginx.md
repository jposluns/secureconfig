---
version_basis: {
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "07eda7c75b5cada2d56a730e2c7a33df34730eec5139f55d0545aad278723811",
  "components": {
    "ng": {
      "name": "nginx documentation",
      "basis": "unknown",
      "sources": {
        "s6a0728ca7609": "https://nginx.org/en/docs/http/configuring_https_servers.html",
        "s40bdf1af1596": "https://nginx.org/en/docs/http/ngx_http_core_module.html",
        "sb3bee9429629": "https://nginx.org/en/docs/http/ngx_http_limit_req_module.html",
        "sddc43aac8779": "https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html",
        "sf3430c5a0b22": "https://nginx.org/en/docs/http/ngx_http_proxy_module.html",
        "sf32ce2956917": "https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html",
        "sddacc1191f5f": "https://nginx.org/en/docs/http/ngx_http_realip_module.html"
      }
    },
    "policy": {
      "name": "Mozilla TLS policy",
      "basis": "unknown",
      "sources": {
        "s529b0eabe2ed": "https://ssl-config.mozilla.org/"
      }
    },
    "certbot": {
      "name": "Certbot nginx configurator",
      "basis": "v2.3.0",
      "sources": {
        "s3a02bfe1d7ad": "https://github.com/certbot/certbot/blob/v2.3.0/certbot-nginx/certbot_nginx/_internal/configurator.py#L711"
      }
    },
    "hsts": {
      "name": "HSTS specification",
      "basis": "RFC 6797",
      "sources": {
        "s3f5af5f440f9": "https://www.rfc-editor.org/rfc/rfc6797.html#section-6.1.2"
      }
    },
    "nginx-source": {
      "name": "nginx source",
      "basis": "release-1.26.3",
      "sources": {
        "s0ae4e9bc8d07": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L216-L218",
        "s002242c2d0cd": "https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L470-L480",
        "s305b7194043c": "https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L739-L775",
        "sbea253fd242b": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/v2/ngx_http_v2_module.c#L76-L81",
        "s936193a42402": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_core_module.c#L4181-L4188",
        "sac3cbbf7fc48": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L857-L862",
        "s66c86979411e": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L153-L172",
        "sabb195c173d5": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L788-L802",
        "sa930199b563a": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L74-L80",
        "seb1f8a9d91f9": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L666-L687",
        "sf6eac8f6749d": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796",
        "s3df6e64cd6a3": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_request_module.c#L135-L182",
        "sced570e33c0f": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_request.h#L78-L138",
        "sfafe27857e33": "https://github.com/nginx/nginx/blob/release-1.26.3/src/event/ngx_event_openssl.c#L4568-L4576"
      }
    },
    "authelia": {
      "name": "Authelia nginx integration",
      "basis": "v4.39.28",
      "sources": {
        "s279cd6449b53": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L39-L45",
        "sdf01968ab996": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L245-L247",
        "s237ae14bbb4a": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L517-L519"
      }
    },
    "oauth2-proxy": {
      "name": "oauth2-proxy nginx integration",
      "basis": "v7.15.4",
      "sources": {
        "sc62400f0ea8a": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/integrations/nginx.md#L16-L18"
      }
    },
    "cloudflare-access": {
      "name": "Cloudflare Access web applications",
      "basis": "unknown",
      "sources": {
        "sfe56578bedf4": "https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/"
      }
    },
    "httpd": {
      "name": "Apache httpd source",
      "basis": "2.4.69",
      "sources": {
        "s309ecdd34379": "https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128",
        "sf711558bdf3c": "https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L45",
        "s1c1a101a70e7": "https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295",
        "s4482c55d79a2": "https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L373-L382"
      }
    },
    "debian-apache2": {
      "name": "Debian apache2 packaging",
      "basis": "2.4.69-1",
      "sources": {
        "sc2a26b3a7af5": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-101",
        "s62f6ed2866ab": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/changelog#L1"
      }
    },
    "owasp": {
      "name": "OWASP Password Storage Cheat Sheet",
      "basis": "commit 72865b1e",
      "sources": {
        "s4531e65b6502": "https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13"
      }
    }
  },
  "claims": {
    "certbot": {"text": "The guide says certbot --nginx edits the server block; certificate acquisition is delegated to the linked certificate guides.", "components": ["ng", "certbot"], "sources": ["ng:s6a0728ca7609", "certbot:s3a02bfe1d7ad"], "status": "REASONED"},
    "tls": {"text": "443 IPv4/IPv6 TLS uses certificate chain and private key, TLSv1.2/TLSv1.3 and ssl_prefer_server_ciphers off.", "components": ["ng"], "sources": ["ng:s6a0728ca7609"], "status": "REASONED"},
    "http2": {"text": "At nginx release-1.26.3, http2 on is the HTTP/2 module directive; nginx 1.25.1 introduced it and deprecated the older listen 443 ssl http2 parameter.", "components": ["ng", "nginx-source"], "sources": ["ng:s40bdf1af1596", "nginx-source:s002242c2d0cd", "nginx-source:sbea253fd242b", "nginx-source:s936193a42402"], "status": "REASONED"},
    "tokens": {"text": "server_tokens off suppresses nginx version in headers and error pages.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED"},
    "hsts": {"text": "Send HSTS only after HTTPS works; includeSubDomains commits every subdomain for max-age.", "components": ["ng", "hsts", "nginx-source"], "sources": ["ng:s6a0728ca7609", "hsts:s3f5af5f440f9", "nginx-source:s0ae4e9bc8d07"], "status": "REASONED"},
    "hsts-inheritance": {"text": "At nginx release-1.26.3, a location add_header replaces inherited server headers; always changes response-code coverage, not inheritance.", "components": ["ng", "nginx-source"], "sources": ["ng:s40bdf1af1596", "nginx-source:s0ae4e9bc8d07", "nginx-source:seb1f8a9d91f9", "nginx-source:sf6eac8f6749d"], "status": "REASONED"},
    "proxy": {"text": "Proxy to loopback 127.0.0.1:3000 and set Host, X-Forwarded-For, X-Forwarded-Proto and X-Forwarded-Host.", "components": ["ng"], "sources": ["ng:sf3430c5a0b22"], "status": "REASONED"},
    "forwarded-host": {"text": "Overwrite X-Forwarded-Host: client-set values otherwise pass upstream.", "components": ["ng"], "sources": ["ng:sf3430c5a0b22"], "status": "REASONED"},
    "cipher-policy": {"text": "Use Mozilla for explicit cipher policy; retain the stated protocol floor.", "components": ["ng", "policy"], "sources": ["ng:s6a0728ca7609", "policy:s529b0eabe2ed"], "status": "REASONED"},
    "tickets": {"text": "At nginx release-1.26.3, ssl_session_tickets defaults on; nginx 1.23.2 introduced automatic ticket-key rotation with a shared ssl_session_cache.", "components": ["ng", "nginx-source"], "sources": ["ng:s6a0728ca7609", "nginx-source:sac3cbbf7fc48", "nginx-source:s305b7194043c", "nginx-source:sfafe27857e33"], "status": "REASONED"},
    "redirect": {"text": "Port 80 on IPv4/IPv6 redirects with 301; a default server reflecting $host can redirect unmatched hosts off-site, so use 444 or a canonical host.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED"},
    "password-file": {"text": "At httpd 2.4.69, htpasswd -B selects bcrypt, bare -B uses cost 5, and -C sets the cost; the OWASP cheat sheet at commit 72865b1e recommends at least 10 for legacy bcrypt. Debian apache2 2.4.69-1 packages htpasswd in apache2-utils.", "components": ["ng", "httpd", "owasp", "debian-apache2"], "sources": ["ng:sf32ce2956917", "debian-apache2:sc2a26b3a7af5", "debian-apache2:s62f6ed2866ab", "httpd:s309ecdd34379", "httpd:sf711558bdf3c", "httpd:s1c1a101a70e7", "httpd:s4482c55d79a2", "owasp:s4531e65b6502"], "status": "REASONED"},
    "basic": {"text": "auth_basic and auth_basic_user_file gate the existing proxied location over TLS; preserve its forwarded headers.", "components": ["ng"], "sources": ["ng:sf32ce2956917", "ng:sf3430c5a0b22"], "status": "REASONED"},
    "mtls": {"text": "At nginx release-1.26.3, ssl_client_certificate and ssl_verify_client on configure trusted client-certificate verification.", "components": ["ng", "nginx-source"], "sources": ["ng:s6a0728ca7609", "nginx-source:s66c86979411e", "nginx-source:sabb195c173d5", "nginx-source:sa930199b563a"], "status": "REASONED"},
    "mfa": {"text": "At nginx release-1.26.3, auth_request permits 2xx authentication subresponses and returns 401/403; Authelia v4.39.28 and oauth2-proxy v7.15.4 document nginx auth_request integration, and Cloudflare Access documents protecting self-hosted web applications; the nginx source cited here does not cover those integrations. MFA is this guide's requirement; whether a given installation enforces it depends on its configured portal or Access policy (this guide's assessment).", "components": ["ng", "nginx-source", "authelia", "oauth2-proxy", "cloudflare-access"], "sources": ["ng:sf32ce2956917", "nginx-source:s3df6e64cd6a3", "nginx-source:sced570e33c0f", "authelia:s279cd6449b53", "authelia:sdf01968ab996", "authelia:s237ae14bbb4a", "oauth2-proxy:sc62400f0ea8a", "cloudflare-access:sfe56578bedf4"], "status": "REASONED"},
    "body-limit": {"text": "client_max_body_size defaults to 1m; 10m rejects larger bodies with 413, and 0 disables the check.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED"},
    "rate-limit": {"text": "Per-address limit_req uses a 10r/s zone, burst 20 and nodelay; rejection status defaults to 503.", "components": ["ng"], "sources": ["ng:sb3bee9429629"], "status": "REASONED"},
    "connection-limit": {"text": "limit_conn apiconn 10 caps concurrent connections per client address; it can also return 503.", "components": ["ng"], "sources": ["ng:sddc43aac8779"], "status": "REASONED"},
    "location-auth": {"text": "Keep limits in the authenticated location; sibling locations do not inherit its auth or proxy headers. Repeat auth or inherit it from server; auth_basic off is deliberate.", "components": ["ng"], "sources": ["ng:sf32ce2956917", "ng:s40bdf1af1596", "ng:sf3430c5a0b22"], "status": "REASONED"},
    "read-timeout": {"text": "proxy_read_timeout 60s limits gaps between upstream reads, not total response duration; active streams can continue indefinitely.", "components": ["ng"], "sources": ["ng:sf3430c5a0b22"], "status": "REASONED"},
    "client-address": {"text": "At a direct edge trust the appended last X-Forwarded-For entry; behind a CDN, recover the client with trusted set_real_ip_from and real_ip_header before per-client limits.", "components": ["ng"], "sources": ["ng:sf3430c5a0b22", "ng:sddacc1191f5f", "ng:sb3bee9429629", "ng:sddc43aac8779"], "status": "REASONED"},
    "verify-config": {"text": "Run nginx -t before reload; no configuration-test outcome is recorded.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should return 301 with an HTTPS Location.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS must validate without -k; TLS 1.1-only rejection must be protocol_version, not a generic/local failure; test TLS 1.0 separately.", "components": ["ng"], "sources": ["ng:s6a0728ca7609"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "An open path may return 200; the protected path must reject no credentials with 401/403, and valid credentials reach the app rather than 401.", "components": ["ng"], "sources": ["ng:sf32ce2956917"], "status": "REASONED", "verify": [1]},
    "verify-size": {"text": "Authenticated 9M succeeds normally only after raising the 1m default; 11M returns 413. Disable the check with 0 in isolation to distinguish backend refusal.", "components": ["ng"], "sources": ["ng:s40bdf1af1596"], "status": "REASONED", "verify": [1]},
    "verify-rate": {"text": "Concurrent unauthenticated probes exercise pre-auth limits; 503 does not identify the limiter. Compare both off and each alone with measured arrival rate.", "components": ["ng"], "sources": ["ng:sb3bee9429629", "ng:sddc43aac8779", "ng:sf32ce2956917"], "status": "REASONED", "verify": [1]},
    "verify-backend": {"text": "Inspect every listener: direct public access to backend 3000 bypasses proxy TLS/auth even when front-door probes pass.", "components": ["ng"], "sources": ["ng:sf3430c5a0b22"], "status": "REASONED", "verify": [1]}
  }
}
---
# nginx: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-17; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| certbot: The guide says certbot --nginx edits the server block; certificate acquisition is delegated to the linked certificate guides. | nginx documentation unknown; Certbot nginx configurator v2.3.0 | REASONED |
| tls: 443 IPv4/IPv6 TLS uses certificate chain and private key, TLSv1.2/TLSv1.3 and ssl_prefer_server_ciphers off. | nginx documentation unknown | REASONED |
| http2: At nginx release-1.26.3, http2 on is the HTTP/2 module directive; nginx 1.25.1 introduced it and deprecated the older listen 443 ssl http2 parameter. | nginx documentation unknown; nginx source release-1.26.3 | REASONED |
| tokens: server_tokens off suppresses nginx version in headers and error pages. | nginx documentation unknown | REASONED |
| hsts: Send HSTS only after HTTPS works; includeSubDomains commits every subdomain for max-age. | nginx documentation unknown; HSTS specification RFC 6797; nginx source release-1.26.3 | REASONED |
| hsts-inheritance: At nginx release-1.26.3, a location add_header replaces inherited server headers; always changes response-code coverage, not inheritance. | nginx documentation unknown; nginx source release-1.26.3 | REASONED |
| proxy: Proxy to loopback 127.0.0.1:3000 and set Host, X-Forwarded-For, X-Forwarded-Proto and X-Forwarded-Host. | nginx documentation unknown | REASONED |
| forwarded-host: Overwrite X-Forwarded-Host: client-set values otherwise pass upstream. | nginx documentation unknown | REASONED |
| cipher-policy: Use Mozilla for explicit cipher policy; retain the stated protocol floor. | nginx documentation unknown; Mozilla TLS policy unknown | REASONED |
| tickets: At nginx release-1.26.3, ssl_session_tickets defaults on; nginx 1.23.2 introduced automatic ticket-key rotation with a shared ssl_session_cache. | nginx documentation unknown; nginx source release-1.26.3 | REASONED |
| redirect: Port 80 on IPv4/IPv6 redirects with 301; a default server reflecting $host can redirect unmatched hosts off-site, so use 444 or a canonical host. | nginx documentation unknown | REASONED |
| password-file: At httpd 2.4.69, htpasswd -B selects bcrypt, bare -B uses cost 5, and -C sets the cost; the OWASP cheat sheet at commit 72865b1e recommends at least 10 for legacy bcrypt. Debian apache2 2.4.69-1 packages htpasswd in apache2-utils. | nginx documentation unknown; Apache httpd source 2.4.69; OWASP Password Storage Cheat Sheet commit 72865b1e; Debian apache2 packaging 2.4.69-1 | REASONED |
| basic: auth_basic and auth_basic_user_file gate the existing proxied location over TLS; preserve its forwarded headers. | nginx documentation unknown | REASONED |
| mtls: At nginx release-1.26.3, ssl_client_certificate and ssl_verify_client on configure trusted client-certificate verification. | nginx documentation unknown; nginx source release-1.26.3 | REASONED |
| mfa: At nginx release-1.26.3, auth_request permits 2xx authentication subresponses and returns 401/403; Authelia v4.39.28 and oauth2-proxy v7.15.4 document nginx auth_request integration, and Cloudflare Access documents protecting self-hosted web applications; the nginx source cited here does not cover those integrations. MFA is this guide's requirement; whether a given installation enforces it depends on its configured portal or Access policy (this guide's assessment). | nginx documentation unknown; nginx source release-1.26.3; Authelia nginx integration v4.39.28; oauth2-proxy nginx integration v7.15.4; Cloudflare Access web applications unknown | REASONED |
| body-limit: client_max_body_size defaults to 1m; 10m rejects larger bodies with 413, and 0 disables the check. | nginx documentation unknown | REASONED |
| rate-limit: Per-address limit_req uses a 10r/s zone, burst 20 and nodelay; rejection status defaults to 503. | nginx documentation unknown | REASONED |
| connection-limit: limit_conn apiconn 10 caps concurrent connections per client address; it can also return 503. | nginx documentation unknown | REASONED |
| location-auth: Keep limits in the authenticated location; sibling locations do not inherit its auth or proxy headers. Repeat auth or inherit it from server; auth_basic off is deliberate. | nginx documentation unknown | REASONED |
| read-timeout: proxy_read_timeout 60s limits gaps between upstream reads, not total response duration; active streams can continue indefinitely. | nginx documentation unknown | REASONED |
| client-address: At a direct edge trust the appended last X-Forwarded-For entry; behind a CDN, recover the client with trusted set_real_ip_from and real_ip_header before per-client limits. | nginx documentation unknown | REASONED |
| verify-config: Run nginx -t before reload; no configuration-test outcome is recorded. | nginx documentation unknown | REASONED |
| verify-redirect: HTTP should return 301 with an HTTPS Location. | nginx documentation unknown | REASONED |
| verify-tls: HTTPS must validate without -k; TLS 1.1-only rejection must be protocol_version, not a generic/local failure; test TLS 1.0 separately. | nginx documentation unknown | REASONED |
| verify-auth: An open path may return 200; the protected path must reject no credentials with 401/403, and valid credentials reach the app rather than 401. | nginx documentation unknown | REASONED |
| verify-size: Authenticated 9M succeeds normally only after raising the 1m default; 11M returns 413. Disable the check with 0 in isolation to distinguish backend refusal. | nginx documentation unknown | REASONED |
| verify-rate: Concurrent unauthenticated probes exercise pre-auth limits; 503 does not identify the limiter. Compare both off and each alone with measured arrival rate. | nginx documentation unknown | REASONED |
| verify-backend: Inspect every listener: direct public access to backend 3000 bypasses proxy TLS/auth even when front-door probes pass. | nginx documentation unknown | REASONED |
<!-- version-basis:end -->

Get a certificate first: [free-certificates.md](free-certificates.md) for a public host (note that `certbot --nginx` edits the server block for you), or [self-signed.md](self-signed.md) for internal use.

## 1. HTTPS server block

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;                     # nginx 1.25.1+; on older versions: listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    server_tokens off;            # do not emit the nginx version in headers or error pages

    # Send HSTS only once HTTPS is confirmed working. `includeSubDomains` commits EVERY subdomain to HTTPS
    # for the whole max-age; drop it until each subdomain serves HTTPS, and start with a short max-age.
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://127.0.0.1:3000;      # your app, bound to loopback only
        proxy_set_header Host              $host;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host  $host;   # overwrite; nginx forwards a client-set value by default
    }
}
```

At nginx release-1.26.3, the HTTP/2 module provides `http2 on`; nginx 1.25.1 introduced it and deprecated the older `listen ... http2` parameter ([module](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/v2/ngx_http_v2_module.c#L76-L81), [changelog](https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L470-L480), [listen parser](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_core_module.c#L4181-L4188)).

For explicit cipher lists, generate them with the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) instead of copying from old tutorials; the protocol floor above is the part that must not be omitted. nginx defaults `ssl_session_tickets on`, and un-rotated ticket keys weaken forward secrecy: either set `ssl_session_tickets off`, or on nginx 1.23.2+ give it a shared `ssl_session_cache` so it rotates the ticket keys automatically. At nginx release-1.26.3, the default-on setting and shared-cache rotation are supported by the [SSL module](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L857-L862), [1.23.2 changelog](https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L739-L775) and [rotation code](https://github.com/nginx/nginx/blob/release-1.26.3/src/event/ngx_event_openssl.c#L4568-L4576).

## 2. Redirect HTTP to HTTPS

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

`$host` echoes the client's `Host` header, so if this `:80` block is the `default_server` (explicit, or implicit as the first block for that address and port), a request with `Host: attacker.example.net` is redirected off-site. Give the `default_server` a `return 444;` (or a redirect to the literal canonical host) rather than reflecting `$host`.

## 3. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). To gate a site or path at the proxy, use basic authentication over TLS:

```bash
sudo apt install apache2-utils          # provides htpasswd
sudo htpasswd -B -C 12 -c /etc/nginx/.htpasswd admin   # -C 12 sets bcrypt cost; bare -B is 5, below the OWASP minimum of 10
```

At httpd 2.4.69, `htpasswd -B` selects bcrypt, `-C` sets its cost, and omitting `-C` uses cost 5 ([htpasswd usage](https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128), [default constant](https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L45), [bcrypt call](https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295), [cost option](https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L373-L382)). The OWASP cheat sheet at commit 72865b1e recommends a work factor of at least 10 for legacy bcrypt ([OWASP recommendation](https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13)). Debian's apache2 packaging at 2.4.69-1 ([changelog](https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/changelog#L1)) lists `htpasswd` among the programs in `apache2-utils` ([package description](https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-101)); other distributions may package it differently.

```nginx
    # this is section 1's `location /`, now also carrying the auth directives - do not paste a second
    # `location /`; the proxy_set_header lines must stay, or the app loses Host / the forwarded headers
    location / {
        auth_basic           "Restricted";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host              $host;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host  $host;   # overwrite; nginx forwards a client-set value by default
    }
```

Mutual TLS for machine-to-machine access:

```nginx
    ssl_client_certificate /etc/ssl/certs/internal-ca.crt;
    ssl_verify_client on;
```

At nginx release-1.26.3, these directives configure client-certificate verification ([directive definitions](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L153-L172)), and `ssl_verify_client on` or `optional` without `ssl_client_certificate` fails the [configuration check](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L788-L802) ("no ssl_client_certificate for ssl_verify_client"); `optional_no_ca` ([enum value 3](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L74-L80)) is exempt.

Basic authentication is single-factor. For human-facing sites, add MFA with the `auth_request` mechanism pointed at an [Authelia](https://www.authelia.com/) or [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) portal, or front the site with Cloudflare Access; options in [mfa.md](mfa.md) (this guide's requirement). Whether MFA is enforced in a particular installation depends on the configured portal or Access policy (this guide's assessment). Authelia v4.39.28 requires nginx's `http_auth_request` module ([requirements](https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L39-L45)); its nginx setup includes an auth-request snippet in each protected location ([location guidance](https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L245-L247)) containing `auth_request /internal/authelia/authz;` ([snippet](https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L517-L519)). oauth2-proxy v7.15.4 documents nginx `auth_request` against its authentication endpoint and requires `--reverse-proxy` for this option ([integration](https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/integrations/nginx.md#L16-L18)). Cloudflare Access documents protecting self-hosted web applications by checking requests against Access policies before allowing them through ([web applications](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/)). At nginx release-1.26.3, `auth_request` accepts a subrequest status from `NGX_HTTP_OK` (200) up to `NGX_HTTP_SPECIAL_RESPONSE` (300, exclusive), returns 401 or 403 as received, and answers any other status with 500 ([module handler](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_request_module.c#L135-L182), [status codes](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_request.h#L78-L138)). The nginx source cited here does not cover the Authelia, oauth2-proxy or Cloudflare Access integrations.

## 4. Bound the expensive endpoints

An authenticated caller can still exhaust an inference, upload, or job-submission endpoint, which is
denial of wallet when the endpoint costs GPU time ([authentication.md](authentication.md)). Declare the
zones in the `http` block and apply the limits per location.

```nginx
# add to the http block
limit_req_zone  $binary_remote_addr zone=api:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=apiconn:10m;

# add to the server block from section 1
client_max_body_size 10m;                   # 413 above this; the default is 1m

# add INSIDE the existing `location /` from sections 1 and 3. Do not paste a new
# location block: this one already carries auth_basic and the proxy_set_header
# directives, and a location without them is unauthenticated and loses the
# forwarded headers. A sibling location does not inherit either.
limit_req  zone=api burst=20 nodelay;       # 503 once the burst is spent
limit_conn apiconn 10;                      # concurrent connections per client address
proxy_read_timeout 60s;
```

Put the limits in the location that already carries authentication. nginx selects the single most
specific matching location and does not inherit `auth_basic` from a less specific one, so adding a
separate `location /api/` for the limits would create a route that is rate limited and unauthenticated.
If you do split them out, repeat the `auth_basic` directives in each location, or move them to the
`server` level so every location inherits them.

`proxy_read_timeout` bounds the gap between successive reads from the upstream, not the total duration
of a response. A stream that keeps sending stays alive indefinitely under a 60s value; a stream that
stalls for 61s is cut. Choose it from the longest acceptable silence, and note that raising it lengthens
that tolerance rather than removing the timeout.

Mind the client address these headers carry. At a direct internet edge the block above appends the peer to `X-Forwarded-For` with `$proxy_add_x_forwarded_for`, so the app must read the LAST entry (the one nginx added), never the client-controlled first one. And if nginx sits behind a CDN or another proxy (for example fronting the site with Cloudflare Access, above), `$binary_remote_addr` is the CDN's edge IP, not the client's, so all callers arriving via the same edge IP share one `limit_req`/`limit_conn` bucket: the limits blur across clients or throttle real users, and a client-supplied `X-Forwarded-For` reaches the app, to be trusted if the app reads its first entry. Recover the real client address with `set_real_ip_from <cdn-ranges>` and `real_ip_header CF-Connecting-IP` (or `X-Forwarded-For`) from `ngx_http_realip_module`, so the limit key and the logged address are the client rather than the edge.

## 5. Verify (REASONED: all Verify scenarios follow the cited nginx documentation; this guide records no exposed/fixed deployment run. This metadata-only review has no authorized nginx deployment fixture.)

```bash
sudo nginx -t && sudo systemctl reload nginx
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI http://example.com/        # expect 301 with a https:// Location
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI --max-time 10 https://example.com/       # TLS must verify with NO -k (a cert error means TLS is misconfigured); status is 200 if / is open, or 401 if you applied section 3's auth to it
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -s -o /dev/null -w '%{http_code}\n' --max-time 10 https://example.com/                        # if section 3's auth is applied: an uncredentialed request must be 401/403, never 200
(
  # The admin password reaches curl through a config file on stdin (curl
  # --config -), never through argv: -u admin:PASSWORD is world-readable via
  # ps and /proc/<pid>/cmdline on a shared host. Paste the whole parenthesised
  # block, including its set -- line. (The TLS-floor and size-prep steps sit
  # inside the same block only so the password is entered once.)
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The password you substitute on the set -- line enters shell history.
  # Clear that history line afterward.
  # Stdin closes the argv channel only: it does not hide the password from
  # set -x tracing or your own account's view of the process.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PASSWORD'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the admin password on the set -- line above; not probing"; exit ;; esac
  set -- "${1//\\/\\\\}"
  set -- "${1//\"/\\\"}"
  printf 'user = "admin:%s"\n' "$1" | curl -q -s -o /dev/null -w '%{http_code}\n' --max-time 10 --config - https://example.com/   # with credentials: your app's response, never 401
  curl -q -s -o /dev/null -w 'http=%{http_code} err=%{errormsg}\n' --max-time 10 --tlsv1.1 --tls-max 1.1 https://example.com/   # protocol floor: offering only TLS 1.1 MUST be rejected. The pass is specifically a `protocol_version` alert (the server refuses the version); a generic handshake failure (for example no shared cipher) or a local "could not load"/policy error is inconclusive, not proof. This shows the 1.1 boundary; the same TLSv1.2+ floor also refuses 1.0, which you confirm separately with `--tlsv1.0 --tls-max 1.0`
  head -c 9M  /dev/zero > /tmp/under.bin && head -c 11M /dev/zero > /tmp/over.bin
  printf 'user = "admin:%s"\n' "$1" | curl -q -s -o /dev/null -w '%{http_code}\n' --max-time 20 --config - --data-binary @/tmp/under.bin https://example.com/
                                    # positive control: must be your app's normal response to this POST
                                    # (for example 200/204/405), never 413. A 401 means the credentials, not
                                    # the size limit, were exercised, and a 000 means transport failed: either voids the control
  printf 'user = "admin:%s"\n' "$1" | curl -q -s -o /dev/null -w '%{http_code}\n' --config - --data-binary @/tmp/over.bin  https://example.com/
                                    # 413. The 9M control is the discriminating half: nginx's default
                                    # client_max_body_size is 1m, so 9M is refused until `10m` is set,
                                    # while 11M returns 413 either way. Neither status says WHICH layer
                                    # refused: a backend with its own limit produces the same codes. To
                                    # attribute it to nginx, set `client_max_body_size 0` in an isolated
                                    # environment, which disables the check entirely; commenting the
                                    # directive out only restores the 1m default and still returns 413
)
seq 1 40 | xargs -P 40 -I{} curl -q -s -o /dev/null -w '%{http_code}\n' https://example.com/ | sort | uniq -c
                                    # Run them CONCURRENTLY and WITHOUT credentials: nginx evaluates
                                    # limit_req in the PREACCESS phase, before auth_basic in the ACCESS
                                    # phase, so an unauthenticated flood still exercises the limiter, which
                                    # is keyed on $binary_remote_addr (the client address). Expect 503s
                                    # (the limiter rejecting; limit_req_status defaults to 503) mixed with
                                    # 401s if section 3's auth covers /, or with 200s if it does not.
                                    # A 503 is not conclusive on its own: `limit_conn` also returns
                                    # 503, and an upstream under load returns it too, so this does not
                                    # establish that either nginx limiter fired. Attributing it needs an
                                    # isolated environment with both limiters disabled as a baseline,
                                    # then each enabled alone, with the arrival rate actually measured
rm -f /tmp/under.bin /tmp/over.bin
ss -tlnp   # read every listener; 3000: the app itself: 127.0.0.1 only, never 0.0.0.0. All the checks
                                    # above pass while the app also answers directly on port 3000,
                                    # which bypasses this proxy's TLS and its authentication. That
                                    # bypass is the first common mistake below, and the first item in
                                    # common-mistakes.md
```

## Common mistakes

- The app still listens on `0.0.0.0:3000` next to the proxy, so the proxy's TLS and auth are bypassed. Bind the app to `127.0.0.1` and confirm with `ss -tlnp`.
- `add_header` in a `location` block silently drops ALL headers inherited from `server`. That is inheritance, which `always` does not change (`always` changes which response codes the header is added to, not inheritance). Keep HSTS at the `server` level, and if a `location` needs its own `add_header`, re-declare HSTS inside it too. At nginx release-1.26.3, the [header merge code](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L666-L687) inherits parent headers only when the child has no header list, and the first `add_header` at a level creates that level's own list ([directive handler](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796)).
- A default `server` block that still serves plain HTTP for unmatched hosts; give the catch-all `default_server` a `return 444;` (or a redirect to the literal canonical host), not the `$host`-reflecting redirect above.
- `auth_basic` on `/` but a later `location` (for example `/static`) that re-opens access; `auth_basic off` should be a deliberate exception, not an accident.

## Sources (checked September 2026)

- Configuring HTTPS servers: https://nginx.org/en/docs/http/configuring_https_servers.html
- Core module (`client_max_body_size`): https://nginx.org/en/docs/http/ngx_http_core_module.html
- Request rate limiting (`limit_req_zone`, `limit_req`, `burst`, `nodelay`): https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- Connection limiting (`limit_conn_zone`, `limit_conn`): https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html
- Proxy module (`proxy_read_timeout`, and `proxy_send_timeout` and `proxy_connect_timeout` if you add them): https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- ngx_http_auth_basic_module: https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
- Real IP module (`set_real_ip_from`, `real_ip_header`) for nginx behind a CDN or proxy: https://nginx.org/en/docs/http/ngx_http_realip_module.html
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
- Certbot v2.3.0 nginx server-block installation (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot-nginx/certbot_nginx/_internal/configurator.py#L711
- RFC 6797 HSTS policy lifetime and subdomains (checked October 2026): https://www.rfc-editor.org/rfc/rfc6797.html#section-6.1.2
- nginx release-1.26.3 header-filter `always` handling (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L216-L218
- nginx release-1.26.3 changes http2 (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L470-L480
- nginx release-1.26.3 changes tickets (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/docs/xml/nginx/changes.xml#L739-L775
- nginx release-1.26.3 http2 (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/v2/ngx_http_v2_module.c#L76-L81
- nginx release-1.26.3 listen http2 (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_core_module.c#L4181-L4188
- nginx release-1.26.3 ssl tickets (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L857-L862
- nginx release-1.26.3 ssl mtls (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L153-L172
- nginx release-1.26.3 ssl mtls check (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L788-L802
- nginx release-1.26.3 ssl_verify_client values (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_ssl_module.c#L74-L80
- nginx release-1.26.3 headers merge (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L666-L687
- nginx release-1.26.3 add_header list creation (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796
- nginx release-1.26.3 auth request (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_auth_request_module.c#L135-L182
- nginx release-1.26.3 HTTP status codes (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_request.h#L78-L138
- Authelia v4.39.28 nginx module requirements (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L39-L45
- Authelia v4.39.28 nginx protected locations (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L245-L247
- Authelia v4.39.28 nginx auth_request snippet (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/nginx.md#L517-L519
- oauth2-proxy v7.15.4 nginx auth_request integration (checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/integrations/nginx.md#L16-L18
- Cloudflare Access web applications (unversioned page, checked October 2026): https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/
- nginx release-1.26.3 ticket rotation (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/event/ngx_event_openssl.c#L4568-L4576
- Apache httpd 2.4.69 htpasswd (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128
- Apache httpd 2.4.69 bcrypt default (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L45
- Apache httpd 2.4.69 bcrypt use (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295
- Apache httpd 2.4.69 bcrypt cost (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L373-L382
- Debian apache2 2.4.69-1 `apache2-utils` package description listing htpasswd (checked October 2026): https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-101
- Debian apache2 packaging version 2.4.69-1 (checked October 2026): https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/changelog#L1
- OWASP Password Storage Cheat Sheet at commit 72865b1e (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13
