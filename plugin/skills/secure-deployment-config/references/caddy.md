---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "e4ea10976bad434d5112a09a1ea7f33d383b101ed29cdcc6da8d3e357b1deca7",
  "components": {
    "docs": {
      "name": "Caddy documentation",
      "basis": "2",
      "sources": {
        "s434e7b7d7f63": "https://caddyserver.com/docs/automatic-https",
        "s3923477355fb": "https://caddyserver.com/docs/api",
        "sdbcd496895d6": "https://caddyserver.com/docs/caddyfile/options",
        "s31af5ed45a20": "https://caddyserver.com/docs/caddyfile/directives/request_body",
        "sec59a61934c5": "https://caddyserver.com/docs/caddyfile/directives",
        "s5f03427bc3ed": "https://github.com/mholt/caddy-ratelimit",
        "sbc2bd9599bd1": "https://caddyserver.com/docs/caddyfile/directives/basic_auth",
        "s2e47c3139bd2": "https://caddyserver.com/docs/caddyfile/directives/tls",
        "s3865a73ccda3": "https://caddyserver.com/docs/caddyfile/directives/reverse_proxy",
        "s82efc39a8130": "https://caddyserver.com/docs/conventions",
        "s5a6da5adf385": "https://caddyserver.com/docs/caddyfile/directives/header",
        "s8df93f3e3d4c": "https://caddyserver.com/docs/caddyfile/directives/forward_auth",
        "sf12ad47e81b5": "https://caddyserver.com/docs/command-line#signals",
        "sdf68595235d4": "https://letsencrypt.org/2025/01/22/ending-expiration-emails/",
        "s38b1b78ce980": "https://caddyserver.com/docs/caddyfile/matchers"
      }
    },
    "admin": {
      "name": "Caddy admin source",
      "basis": "v2.11.4",
      "sources": {
        "s35044463fa67": "https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L1433",
        "s2bbcf239df02": "https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L58-L67"
      }
    },
    "tags": {
      "name": "Official image tag map",
      "basis": "d82ca5102fa6735be29d5e1fc6ce03af77eb091e",
      "sources": {
        "sdc8aca42f5e2": "https://github.com/docker-library/official-images/blob/d82ca5102fa6735be29d5e1fc6ce03af77eb091e/library/caddy#L7-L65"
      }
    },
    "images": {
      "name": "Caddy Docker source",
      "basis": "fba2853501d36e8a72f946ac8cb7ff64d07e48f2",
      "sources": {
        "s0f0994ef9fac": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L17",
        "s2dce0bbf3a70": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L59-L63",
        "sd2c1b05a8088": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2022/Dockerfile#L27-L32",
        "sf3e9c2d4e0cd": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2022/Dockerfile#L8",
        "sc5dd3f9746fe": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2025/Dockerfile#L27-L32",
        "s6c800a156eac": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2025/Dockerfile#L8",
        "sc5c82704d33f": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2022/Dockerfile#L10",
        "sc1cb0e1fb9eb": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2022/Dockerfile#L42-L47",
        "s11528dfcc516": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2025/Dockerfile#L10",
        "s70b76475a281": "https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2025/Dockerfile#L42-L47"
      }
    },
    "dist": {
      "name": "Default Caddyfile source",
      "basis": "33ae08ff08d168572df2956ed14fbc4949880d94",
      "sources": {
        "s433758a90af0": "https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/config/Caddyfile"
      }
    },
    "basic": {
      "name": "Caddy basic_auth rename",
      "basis": "v2.8.0",
      "sources": {
        "sbc2bd9599bd1": "https://caddyserver.com/docs/caddyfile/directives/basic_auth"
      }
    },
    "forward": {
      "name": "Caddy forward_auth minimum",
      "basis": "2.5",
      "sources": {
        "s8df93f3e3d4c": "https://caddyserver.com/docs/caddyfile/directives/forward_auth"
      }
    }
  },
  "claims": {
    "auto-https": {"text": "Caddy 2 obtains and renews public certificates and redirects HTTP to HTTPS; DNS must point here and the example requires public 80/443.", "components": ["docs"], "sources": ["docs:s434e7b7d7f63"], "status": "REASONED"},
    "issuers": {"text": "Public certificates come from Let's Encrypt or ZeroSSL and renew automatically.", "components": ["docs"], "sources": ["docs:s434e7b7d7f63"], "status": "REASONED"},
    "renewal-monitoring": {"text": "Set the ACME email contact but monitor renewal yourself: Let's Encrypt stopped expiration emails.", "components": ["docs"], "sources": ["docs:sdbcd496895d6", "docs:sdf68595235d4"], "status": "REASONED"},
    "backend": {"text": "reverse_proxy sends traffic to 127.0.0.1:3000; keep the app private to prevent TLS/auth bypass.", "components": ["docs"], "sources": ["docs:s3865a73ccda3"], "status": "REASONED"},
    "hsts": {"text": "Caddy sends no HSTS automatically; add it only after HTTPS works across every included subdomain.", "components": ["docs"], "sources": ["docs:s5a6da5adf385", "docs:s434e7b7d7f63"], "status": "REASONED"},
    "forwarded": {"text": "Caddy ignores untrusted client X-Forwarded-* by default; configure trusted_proxies behind a trusted CDN/proxy.", "components": ["docs"], "sources": ["docs:s3865a73ccda3"], "status": "REASONED"},
    "internal-tls": {"text": "tls internal uses a local CA; clients must trust its root, with caddy trust for the local host. tls also accepts explicit cert/key files.", "components": ["docs"], "sources": ["docs:s2e47c3139bd2", "docs:s434e7b7d7f63"], "status": "REASONED"},
    "basic": {"text": "basic_auth uses hashed passwords from caddy hash-password; it was named basicauth before v2.8.0 and remains single-factor.", "components": ["docs", "basic"], "sources": ["docs:sbc2bd9599bd1", "basic:sbc2bd9599bd1"], "status": "REASONED"},
    "path-auth": {"text": "Protect /admin and /admin/* together: path matches are exact and multiple paths are OR'ed.", "components": ["docs"], "sources": ["docs:s38b1b78ce980", "docs:sbc2bd9599bd1"], "status": "REASONED"},
    "mfa": {"text": "forward_auth (Caddy 2.5+) can delegate human authentication to Authelia; Cloudflare Access is another proposed layer.", "components": ["docs", "forward"], "sources": ["docs:s8df93f3e3d4c", "forward:s8df93f3e3d4c"], "status": "REASONED"},
    "access-origin": {"text": "Cloudflare Access requires closing direct origin ingress and validating its JWT; Caddy still answers directly on 443. Sources omit Cloudflare controls.", "components": ["docs"], "sources": ["docs:s3865a73ccda3"], "status": "REASONED"},
    "body-limit": {"text": "Add request_body max_size 10MB inside the existing authenticated site; replacing the site without basic_auth makes it public.", "components": ["docs"], "sources": ["docs:s31af5ed45a20", "docs:sbc2bd9599bd1"], "status": "REASONED"},
    "rate-limit": {"text": "The standard build has no rate_limit directive; use a compiled community caddy-ratelimit module or an upstream layer.", "components": ["docs"], "sources": ["docs:sec59a61934c5", "docs:s5f03427bc3ed"], "status": "REASONED"},
    "admin-bind": {"text": "The admin API defaults to localhost:2019 as of v2.11.4; never publish it or reverse-proxy to it.", "components": ["admin", "docs"], "sources": ["admin:s35044463fa67", "admin:s2bbcf239df02", "docs:s3923477355fb"], "status": "REASONED"},
    "admin-authority": {"text": "Reachable unauthenticated admin clients can replace config at POST /load, edit /config/ or stop with POST /stop.", "components": ["docs"], "sources": ["docs:s3923477355fb"], "status": "REASONED"},
    "admin-isolation": {"text": "Host/Origin checks are not process isolation; local untrusted workloads require a permissioned Unix socket.", "components": ["docs"], "sources": ["docs:s3923477355fb", "docs:sdbcd496895d6"], "status": "REASONED"},
    "docker-admin": {"text": "Official 2.11.4 Alpine and Windows runtime images EXPOSE 2019 but ship a Caddyfile without admin; absent overrides, the endpoint stays namespace-local.", "components": ["tags", "images", "dist", "admin"], "sources": ["tags:sdc8aca42f5e2", "images:s0f0994ef9fac", "images:s2dce0bbf3a70", "images:sd2c1b05a8088", "images:sf3e9c2d4e0cd", "images:sc5dd3f9746fe", "images:s6c800a156eac", "images:sc5c82704d33f", "images:sc1cb0e1fb9eb", "images:s11528dfcc516", "images:s70b76475a281", "dist:s433758a90af0", "admin:s35044463fa67", "admin:s2bbcf239df02"], "status": "REASONED"},
    "admin-override": {"text": "A mounted admin setting or CADDY_ADMIN changes the address; do not set 0.0.0.0:2019 to make publication work.", "components": ["docs", "admin", "dist"], "sources": ["docs:sdbcd496895d6", "admin:s35044463fa67", "admin:s2bbcf239df02", "dist:s433758a90af0"], "status": "REASONED"},
    "namespace": {"text": "Bridge publication cannot reach container loopback; host/shared namespaces permit local peers. Avoid untrusted namespace sharing and run CLI commands inside the container.", "components": ["docs", "images"], "sources": ["docs:s3923477355fb", "images:s0f0994ef9fac", "images:s2dce0bbf3a70", "images:sd2c1b05a8088", "images:sf3e9c2d4e0cd", "images:sc5dd3f9746fe", "images:s6c800a156eac", "images:sc5c82704d33f", "images:sc1cb0e1fb9eb", "images:s11528dfcc516", "images:s70b76475a281"], "status": "REASONED"},
    "admin-socket": {"text": "admin unix//run/caddy/admin.sock uses owner-only mode 0200 by default; append |0600 to set it explicitly.", "components": ["docs"], "sources": ["docs:sdbcd496895d6", "docs:s82efc39a8130"], "status": "REASONED"},
    "runtime-directory": {"text": "The packaged caddy user needs RuntimeDirectory=caddy for /run/caddy; restart creates it and binds the socket. Sources omit the service unit/systemd manual.", "components": ["docs"], "sources": ["docs:sdbcd496895d6"], "status": "REASONED"},
    "reload": {"text": "API reload uses the Caddyfile admin address; admin off disables it and systemd then requires restart.", "components": ["docs"], "sources": ["docs:sdbcd496895d6", "docs:sf12ad47e81b5"], "status": "REASONED"},
    "signal-reload": {"text": "A manual run without --resume may reload startup config via SIGUSR1; API changes or reload with a different file/adapter disable signal reloads.", "components": ["docs"], "sources": ["docs:sf12ad47e81b5"], "status": "REASONED"},
    "on-demand": {"text": "Do not enable unrestricted on_demand TLS without an ask endpoint or host allowlist; this guide does not enable it.", "components": ["docs"], "sources": ["docs:s434e7b7d7f63"], "status": "REASONED"},
    "verify-config": {"text": "Validate /etc/caddy/Caddyfile; no validation outcome is recorded.", "components": ["docs"], "sources": ["docs:sf12ad47e81b5"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should redirect to HTTPS.", "components": ["docs"], "sources": ["docs:s434e7b7d7f63"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "With site-wide auth, HTTPS without credentials returns 401.", "components": ["docs"], "sources": ["docs:sbc2bd9599bd1"], "status": "REASONED", "verify": [1]},
    "verify-scope": {"text": "The @admin variant must return 401 for /admin and /admin/x, but an app response rather than 401 for a non-admin path.", "components": ["docs"], "sources": ["docs:s38b1b78ce980", "docs:sbc2bd9599bd1"], "status": "REASONED", "verify": [1]},
    "verify-size": {"text": "Authenticated 1M reaches the app and 11M returns 413; 401/000 void the control. Auth can prevent body reads; remove request_body in isolation to attribute refusal.", "components": ["docs"], "sources": ["docs:s31af5ed45a20", "docs:sbc2bd9599bd1", "docs:sec59a61934c5"], "status": "REASONED", "verify": [1]},
    "verify-backend": {"text": "Read all listeners: app 3000 must be loopback-only even if proxy checks pass.", "components": ["docs"], "sources": ["docs:s3865a73ccda3"], "status": "REASONED", "verify": [1]},
    "verify-admin": {"text": "TCP admin must bind only loopback; absent 2019 requires confirming admin off or a socket. Check Unix socket existence and owner restrictions separately.", "components": ["docs"], "sources": ["docs:s3923477355fb", "docs:sdbcd496895d6", "docs:s82efc39a8130"], "status": "REASONED", "verify": [1]}
  }
}
---
# Caddy: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| auto-https: Caddy 2 obtains and renews public certificates and redirects HTTP to HTTPS; DNS must point here and the example requires public 80/443. | Caddy documentation 2 | REASONED |
| issuers: Public certificates come from Let's Encrypt or ZeroSSL and renew automatically. | Caddy documentation 2 | REASONED |
| renewal-monitoring: Set the ACME email contact but monitor renewal yourself: Let's Encrypt stopped expiration emails. | Caddy documentation 2 | REASONED |
| backend: reverse_proxy sends traffic to 127.0.0.1:3000; keep the app private to prevent TLS/auth bypass. | Caddy documentation 2 | REASONED |
| hsts: Caddy sends no HSTS automatically; add it only after HTTPS works across every included subdomain. | Caddy documentation 2 | REASONED |
| forwarded: Caddy ignores untrusted client X-Forwarded-* by default; configure trusted_proxies behind a trusted CDN/proxy. | Caddy documentation 2 | REASONED |
| internal-tls: tls internal uses a local CA; clients must trust its root, with caddy trust for the local host. tls also accepts explicit cert/key files. | Caddy documentation 2 | REASONED |
| basic: basic_auth uses hashed passwords from caddy hash-password; it was named basicauth before v2.8.0 and remains single-factor. | Caddy documentation 2; Caddy basic_auth rename v2.8.0 | REASONED |
| path-auth: Protect /admin and /admin/* together: path matches are exact and multiple paths are OR'ed. | Caddy documentation 2 | REASONED |
| mfa: forward_auth (Caddy 2.5+) can delegate human authentication to Authelia; Cloudflare Access is another proposed layer. | Caddy documentation 2; Caddy forward_auth minimum 2.5 | REASONED |
| access-origin: Cloudflare Access requires closing direct origin ingress and validating its JWT; Caddy still answers directly on 443. Sources omit Cloudflare controls. | Caddy documentation 2 | REASONED |
| body-limit: Add request_body max_size 10MB inside the existing authenticated site; replacing the site without basic_auth makes it public. | Caddy documentation 2 | REASONED |
| rate-limit: The standard build has no rate_limit directive; use a compiled community caddy-ratelimit module or an upstream layer. | Caddy documentation 2 | REASONED |
| admin-bind: The admin API defaults to localhost:2019 as of v2.11.4; never publish it or reverse-proxy to it. | Caddy admin source v2.11.4; Caddy documentation 2 | REASONED |
| admin-authority: Reachable unauthenticated admin clients can replace config at POST /load, edit /config/ or stop with POST /stop. | Caddy documentation 2 | REASONED |
| admin-isolation: Host/Origin checks are not process isolation; local untrusted workloads require a permissioned Unix socket. | Caddy documentation 2 | REASONED |
| docker-admin: Official 2.11.4 Alpine and Windows runtime images EXPOSE 2019 but ship a Caddyfile without admin; absent overrides, the endpoint stays namespace-local. | Official image tag map d82ca5102fa6735be29d5e1fc6ce03af77eb091e; Caddy Docker source fba2853501d36e8a72f946ac8cb7ff64d07e48f2; Default Caddyfile source 33ae08ff08d168572df2956ed14fbc4949880d94; Caddy admin source v2.11.4 | REASONED |
| admin-override: A mounted admin setting or CADDY_ADMIN changes the address; do not set 0.0.0.0:2019 to make publication work. | Caddy documentation 2; Caddy admin source v2.11.4; Default Caddyfile source 33ae08ff08d168572df2956ed14fbc4949880d94 | REASONED |
| namespace: Bridge publication cannot reach container loopback; host/shared namespaces permit local peers. Avoid untrusted namespace sharing and run CLI commands inside the container. | Caddy documentation 2; Caddy Docker source fba2853501d36e8a72f946ac8cb7ff64d07e48f2 | REASONED |
| admin-socket: admin unix//run/caddy/admin.sock uses owner-only mode 0200 by default; append &#124;0600 to set it explicitly. | Caddy documentation 2 | REASONED |
| runtime-directory: The packaged caddy user needs RuntimeDirectory=caddy for /run/caddy; restart creates it and binds the socket. Sources omit the service unit/systemd manual. | Caddy documentation 2 | REASONED |
| reload: API reload uses the Caddyfile admin address; admin off disables it and systemd then requires restart. | Caddy documentation 2 | REASONED |
| signal-reload: A manual run without --resume may reload startup config via SIGUSR1; API changes or reload with a different file/adapter disable signal reloads. | Caddy documentation 2 | REASONED |
| on-demand: Do not enable unrestricted on_demand TLS without an ask endpoint or host allowlist; this guide does not enable it. | Caddy documentation 2 | REASONED |
| verify-config: Validate /etc/caddy/Caddyfile; no validation outcome is recorded. | Caddy documentation 2 | REASONED |
| verify-redirect: HTTP should redirect to HTTPS. | Caddy documentation 2 | REASONED |
| verify-auth: With site-wide auth, HTTPS without credentials returns 401. | Caddy documentation 2 | REASONED |
| verify-scope: The @admin variant must return 401 for /admin and /admin/x, but an app response rather than 401 for a non-admin path. | Caddy documentation 2 | REASONED |
| verify-size: Authenticated 1M reaches the app and 11M returns 413; 401/000 void the control. Auth can prevent body reads; remove request_body in isolation to attribute refusal. | Caddy documentation 2 | REASONED |
| verify-backend: Read all listeners: app 3000 must be loopback-only even if proxy checks pass. | Caddy documentation 2 | REASONED |
| verify-admin: TCP admin must bind only loopback; absent 2019 requires confirming admin off or a socket. Check Unix socket existence and owner restrictions separately. | Caddy documentation 2 | REASONED |
<!-- version-basis:end -->

Caddy 2 obtains, installs, and renews publicly trusted certificates automatically and redirects HTTP to HTTPS by default. For a new deployment with a public domain, it is the shortest correct path to HTTPS: no ACME client, no renewal timer, no redirect block.

## 1. Public site with automatic HTTPS

`/etc/caddy/Caddyfile`:

```caddyfile
{
    email admin@example.com        # ACME account contact (Let's Encrypt no longer emails expiry notices; monitor renewal yourself)
}

app.example.com {
    reverse_proxy 127.0.0.1:3000
    header Strict-Transport-Security "max-age=31536000; includeSubDomains"   # Caddy sets no HSTS on its own; add once every subdomain serves HTTPS (includeSubDomains/preload are hard to undo)
}
```

Requirements: the DNS record points at this host, and ports 80 and 443 are reachable from the internet. Start or reload:

```bash
sudo systemctl reload caddy
```

That is the whole certificate setup: certificates come from Let's Encrypt or ZeroSSL and renew automatically. Two things automatic HTTPS does not do on its own: it does not send HSTS (the `header Strict-Transport-Security` line above adds it, so a browser stays on HTTPS after the first visit rather than being downgradable before the redirect), and it does not trust client-supplied `X-Forwarded-*` headers (Caddy ignores them by default to prevent spoofing; if Caddy runs behind a CDN or another proxy, set `trusted_proxies` so it honours them).

## 2. Internal hosts without a public domain

`tls internal` makes Caddy issue from its own local CA instead of a public one:

```caddyfile
app.internal {
    tls internal
    reverse_proxy 127.0.0.1:3000
}
```

Clients must trust Caddy's root CA (on the Caddy host itself, `caddy trust` installs it into the local trust store). Distribution of that trust to other machines follows [self-signed.md](self-signed.md). To use certificate files you generated yourself instead: `tls /path/cert.pem /path/key.pem`.

## 3. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). At the proxy, use `basic_auth` (named `basicauth` before Caddy v2.8.0). Hash the password first:

```bash
caddy hash-password        # prompts, outputs a bcrypt hash
```

```caddyfile
app.example.com {
    basic_auth {
        admin $2a$14$REPLACE_WITH_HASH_FROM_caddy_hash-password
    }
    reverse_proxy 127.0.0.1:3000
}
```

To protect only part of a site, wrap the directive in a matcher:

```caddyfile
    @admin path /admin /admin/*
    basic_auth @admin {
        admin $2a$14$REPLACE_WITH_HASH
    }
```

Path matches are exact, and `/admin/*` alone does not match `/admin` itself, so list both forms; multiple paths in one matcher are OR'ed.

`basic_auth` is single-factor. For human-facing sites, add MFA with the `forward_auth` directive (Caddy 2.5 and later) pointed at an [Authelia](https://www.authelia.com/) portal, or front the site with Cloudflare Access. Fronting with Cloudflare Access only helps if the origin is locked down: Caddy still answers on 443, so a client that discovers the origin IP connects directly and bypasses Access unless you close direct ingress (a tunnel, or Authenticated Origin Pulls plus a Cloudflare-IP firewall) and validate the Access JWT at the origin, per [cloudflare.md](cloudflare.md). Options in [mfa.md](mfa.md).

## 4. Bound the expensive endpoints

Caddy caps request bodies natively. **It has no rate limiting in the standard build**: `rate_limit` is
not a Caddyfile directive, and rate limiting requires the community `caddy-ratelimit` module compiled in
with xcaddy, or a layer in front of Caddy. Do not assume a stock Caddy is rate limited, and do not
follow a `rate_limit` example without checking that your binary has that module.

Add `request_body` to the site block you already have, rather than pasting a fresh one: the `basic_auth`
directive from section 3 lives in that block, and a site block without it is a public route.

```caddy
# add to the existing app.example.com site block from sections 1 and 3.
# Do not replace that block: basic_auth lives there, and a site block
# without it is a public route.
request_body {
    max_size 10MB
}
```

## 5. The admin API

Caddy runs a local admin API, by default on `localhost:2019` (as of v2.11.4), that requires no credentials: anything that can reach it replaces the whole configuration with `POST /load`, edits it path by path under `/config/`, or stops the server with `POST /stop`. Its Host and Origin header checks block a browser on another site, but they are not process isolation, so the endpoint's safety rests on the loopback bind. Never publish it: do not reverse-proxy a route to `:2019`, and never move it to a public address.

The official Docker runtime images (2.11.4: Alpine, Windows Server Core and Nano Server) list 2019 in `EXPOSE`, but their default Caddyfile has no `admin` option, so as shipped, with no mounted configuration that sets `admin` and no `CADDY_ADMIN`, the admin API listens on the loopback of the container's network namespace. On a bridge or user-defined network that is the container's own loopback, out of reach of the published port; with host networking it is the host's loopback, reachable by every process on the host, and containers that share the namespace (the other containers in a Kubernetes pod, or one started with `--network container:`) reach it too. Do not set `admin 0.0.0.0:2019` (or `CADDY_ADMIN`) to make that port work, do not publish it, and do not run the container with host networking or share its namespace with untrusted containers; run `caddy` commands inside the container instead, for example with `docker exec`.

On a host where untrusted workloads share the machine, loopback is not enough, because any local process can reach `127.0.0.1:2019`. Bind the endpoint to a permissioned Unix socket instead, in the same global options block from section 1 (a Caddyfile has only one), so only processes that can open the socket file reconfigure Caddy:

```caddy
{
    email admin@example.com
    admin unix//run/caddy/admin.sock   # defaults to mode 0200 (owner-only); append |0600 to set the mode explicitly
}
```

The packaged service runs as the `caddy` user, which cannot create a socket under root-owned `/run`, so give it a runtime directory with `sudo systemctl edit caddy`:

```ini
[Service]
RuntimeDirectory=caddy
```

systemd creates `/run/caddy` owned by `caddy` when the service starts, so the switch from the default TCP endpoint to the socket needs `sudo systemctl restart caddy`, not a reload: the restart makes the runtime directory and binds the socket in one step. After that, `caddy reload`, and so `sudo systemctl reload caddy`, applies config through this API by reading the admin address from the Caddyfile, so the socket keeps reload working. Disabling the endpoint with `admin off` turns off API reload, so under systemd a config change then needs `systemctl restart caddy` (a manual `caddy run` process started without `--resume` can instead reload the startup config file with `SIGUSR1`; a change made through the admin API, or a `caddy reload` with a different file or adapter, disables signal reloads, so check the logs to confirm the reload took).

## 6. Verify (REASONED: all Verify scenarios follow the cited Caddy documentation and pinned admin/image sources; this guide records no exposed/fixed deployment run. This metadata-only review has no authorized Caddy deployment fixture.)

```bash
caddy validate --config /etc/caddy/Caddyfile
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI http://app.example.com/     # expect a redirect to https://
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://app.example.com/    # expect 401 without credentials once auth is on
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sS -o /dev/null -w '%{http_code}\n' https://app.example.com/admin     # with the @admin matcher variant: 401
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sS -o /dev/null -w '%{http_code}\n' https://app.example.com/admin/x   # 401 as well
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sS -o /dev/null -w '%{http_code}\n' https://app.example.com/          # to prove the matcher SCOPES auth to /admin (not the whole site), a non-/admin path must NOT return 401: it reaches the app (a 200, or the app's own redirect or 404). A 401 here means auth is applied site-wide, not scoped to /admin
head -c 1M /dev/zero > /tmp/under.bin && head -c 11M /dev/zero > /tmp/over.bin
(
  # curl reads the admin password from a config stream on stdin (--config -),
  # never argv (-u admin:PASSWORD is readable in ps / /proc/<pid>/cmdline).
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The password you substitute on the set -- line enters shell history.
  # Clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PASSWORD'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the admin password on the set -- line above; not probing"; exit ;; esac
  set -- "${1//\\/\\\\}"
  set -- "${1//\"/\\\"}"
  printf 'user = "admin:%s"\n' "$1" | curl -q -s -o /dev/null -w '%{http_code}\n' --config - --data-binary @/tmp/under.bin https://app.example.com/
                                     # positive control: under the limit, expect the app's own normal response (a 2xx, or its own 404/redirect), never 413; a 401 means the credentials, not the size limit, were exercised and a 000 means transport failed, either of which voids the control
  printf 'user = "admin:%s"\n' "$1" | curl -q -s -o /dev/null -w '%{http_code}\n' --config - --data-binary @/tmp/over.bin  https://app.example.com/
                                     # 413. Supply credentials: an unauthenticated probe returns 401 and
                                     # tells you nothing about max_size. Caddy's default order puts
                                     # request_body ahead of basic_auth, but the limit is enforced when a
                                     # later handler reads past it, and authentication stops the proxy
                                     # handler reading at all. A backend with its own limit returns the
                                     # same code, so attributing the refusal needs an isolated
                                     # environment with request_body removed
)
rm -f /tmp/under.bin /tmp/over.bin
ss -tlnp   # read every listener; 3000: the app itself: 127.0.0.1 only, never 0.0.0.0. Every check above
                                     # passes while the app also answers directly on port 3000, which
                                     # bypasses Caddy's TLS and its authentication
ss -tlnp   # read every listener; the admin API on TCP: only 127.0.0.1:2019 or [::1]:2019, never a
                                     # public address. A missing 2019 line is not a pass on its own: it also
                                     # means you moved it to a unix socket or set admin off, so confirm which
ls -l /run/caddy/admin.sock          # if you bound it to a unix socket: it exists and is owner-restricted
                                     # (a stream socket, so it does not show in ss -tlnp; use ss -xlp to list it)
```

## Common mistakes

- The app also listens on a public interface, bypassing Caddy; bind it to `127.0.0.1`.
- Blocking port 80 at the firewall: Caddy needs it for the HTTP-01 challenge and for the automatic redirect.
- Enabling on-demand TLS without an `ask` endpoint or a host allowlist: this guide does not use it, but an unrestricted `on_demand` lets anyone point a hostname at the server to mint certificates and exhaust resources.
- Putting the literal password in the Caddyfile; `basic_auth` takes the bcrypt hash, not the password.

## Sources (checked September 2026)

- Official Caddy Docker images: the tag map (library file pinned commit d82ca5102fa6735be29d5e1fc6ce03af77eb091e), and at image source pinned commit fba2853501d36e8a72f946ac8cb7ff64d07e48f2 each runtime image's Caddyfile download, `EXPOSE 2019` and `CMD`, with the default Caddyfile at caddyserver/dist pinned commit 33ae08ff08d168572df2956ed14fbc4949880d94 and the `CADDY_ADMIN` variable that sets the admin address (pinned tag v2.11.4): https://github.com/docker-library/official-images/blob/d82ca5102fa6735be29d5e1fc6ce03af77eb091e/library/caddy#L7-L65, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L17, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L59-L63, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2022/Dockerfile#L10, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2022/Dockerfile#L42-L47, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2025/Dockerfile#L10, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2025/Dockerfile#L42-L47, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2022/Dockerfile#L8, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2022/Dockerfile#L27-L32, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2025/Dockerfile#L8, https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2025/Dockerfile#L27-L32, https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/config/Caddyfile and https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L58-L67
- Automatic HTTPS (Caddy 2): https://caddyserver.com/docs/automatic-https
- Caddy admin API (default `localhost:2019`, `POST /load` and `/config/` replace or edit the whole config, requires no credentials with only Host/Origin header checks, the permissioned-unix-socket warning for untrusted-workload hosts): https://caddyserver.com/docs/api
- Caddy `admin` global option (`admin off`, an address, or `admin unix//...`): https://caddyserver.com/docs/caddyfile/options
- `request_body` directive (`max_size`): https://caddyserver.com/docs/caddyfile/directives/request_body
- Caddyfile directive list, which carries no `rate_limit` entry: https://caddyserver.com/docs/caddyfile/directives
- caddy-ratelimit, the community module that adds rate limiting: https://github.com/mholt/caddy-ratelimit
- basic_auth directive (renamed from basicauth in Caddy v2.8.0): https://caddyserver.com/docs/caddyfile/directives/basic_auth
- tls directive: https://caddyserver.com/docs/caddyfile/directives/tls
- reverse_proxy directive (X-Forwarded-* ignored from untrusted sources by default; `trusted_proxies`): https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Caddy conventions (unix socket default mode 0200, `|<mode>` suffix): https://caddyserver.com/docs/conventions
- header directive (HSTS): https://caddyserver.com/docs/caddyfile/directives/header
- forward_auth directive (Caddy 2.5 and later): https://caddyserver.com/docs/caddyfile/directives/forward_auth
- Caddy command-line signals (SIGUSR1 reload conditions): https://caddyserver.com/docs/command-line#signals
- Let's Encrypt ending expiration-notification emails (2025): https://letsencrypt.org/2025/01/22/ending-expiration-emails/
- Request matchers (path, wildcards, multiple paths): https://caddyserver.com/docs/caddyfile/matchers
- Caddy admin API default `DefaultAdminListen = "localhost:2019"` (pinned tag v2.11.4): https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L1433
