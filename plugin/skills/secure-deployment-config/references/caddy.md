# Caddy: TLS and authentication

Caddy is a web server that hosts sites and passes requests to applications behind it. This guide helps your AI assistant configure it securely, including automatic HTTPS for public domains, its local CA for internal hosts, authentication, request size limits (stock builds lack rate limiting), and a private admin API.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/caddy.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Caddy admin source v2.11.4, systemd manual v262, and Let's Encrypt expiration-email notice 2025; 7 further sources are pinned to a commit and 1 carries no recorded version. Metadata reviewed 2026-09-27; documentation checked September 2026. The guide records 31 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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

`basic_auth` is single-factor. For human-facing sites, add MFA with the `forward_auth` directive (Caddy 2.5 and later) pointed at an [Authelia](https://www.authelia.com/) portal, or front the site with Cloudflare Access. Cloudflare docs at c896795b describe identity-provider MFA and independent Access MFA; the governing setting follows policy over application over organization, so configure it to require MFA ([MFA requirements](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L17-L85)). As this guide reasons, fronting with Cloudflare Access only helps if the origin is locked down: Caddy still answers on 443, so a client that discovers the origin IP connects directly and bypasses Access unless you close direct ingress (a tunnel, or Authenticated Origin Pulls plus a Cloudflare-IP firewall) and validate the Access JWT at the origin ([JWT validation](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17); [tunnel `access` setting](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L196-L215)), per [cloudflare.md](cloudflare.md). Options in [mfa.md](mfa.md).

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

The official [2.11.4 runtime tag map](https://github.com/docker-library/official-images/blob/d82ca5102fa6735be29d5e1fc6ce03af77eb091e/library/caddy#L7-L65) maps [2.11.4-alpine](https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/alpine/Dockerfile#L59-L63), [2.11.4-windowsservercore-ltsc2022](https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2022/Dockerfile#L42-L47), [2.11.4-windowsservercore-ltsc2025](https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows/ltsc2025/Dockerfile#L42-L47), [2.11.4-nanoserver-ltsc2022](https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2022/Dockerfile#L27-L32), [2.11.4-nanoserver-ltsc2025](https://github.com/caddyserver/caddy-docker/blob/fba2853501d36e8a72f946ac8cb7ff64d07e48f2/2.11/windows-nanoserver/ltsc2025/Dockerfile#L27-L32) to Dockerfiles at fba28535. Each lists 2019 in `EXPOSE` and runs the default Caddyfile, which has no `admin` option; as shipped, with no mounted configuration that sets `admin` and no `CADDY_ADMIN`, the admin API listens on `localhost:2019`. On Docker Engine on Linux, ordinary bridge networking keeps that address on the container's own loopback. Host networking shares the host's network namespace, while `--network container:<name|id>` shares another container's networking stack, including its loopback. Treat processes in that shared namespace as potential admin clients. Do not set `admin 0.0.0.0:2019` (or `CADDY_ADMIN`) to make that port work, do not publish it, and do not run the container with host networking or share its namespace with untrusted containers; run `caddy` commands inside the container instead, for example with `docker exec`.

On a host where untrusted workloads share the machine, loopback is not enough, because any local process can reach `127.0.0.1:2019`. Bind the endpoint to a permissioned Unix socket instead, in the same global options block from section 1 (a Caddyfile has only one), so only processes that can open the socket file reconfigure Caddy:

```caddy
{
    email admin@example.com
    admin unix//run/caddy/admin.sock   # defaults to mode 0200 (owner-only); append |0600 to set the mode explicitly
}
```

The caddyserver/dist [service unit at 33ae08ff](https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/init/caddy.service#L22-L32) runs as `caddy` and has no `RuntimeDirectory=` setting. To give that user a directory for the socket under `/run`, add a drop-in with `sudo systemctl edit caddy`:

```ini
[Service]
RuntimeDirectory=caddy
```

The [systemd v262 manual](https://github.com/systemd/systemd/blob/v262/man/systemd.exec.xml#L1558-L1660) says `RuntimeDirectory=caddy` creates `/run/caddy` when the unit starts, owns it according to `User=`/`Group=`, and removes it when the unit stops unless preservation is configured. The switch from the default TCP endpoint to the socket needs `sudo systemctl restart caddy`, not a reload: this is the guide's reasoning that a restart creates the runtime directory and binds the socket in one step. After that, `caddy reload`, and the [dist unit's `ExecReload` at 33ae08ff](https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/init/caddy.service#L22-L32), apply config through this API by reading the admin address from the Caddyfile, so the socket keeps reload working. Disabling the endpoint with `admin off` turns off API reload, so under systemd a config change then needs `systemctl restart caddy` (a manual `caddy run` process started without `--resume` can instead reload the startup config file with `SIGUSR1`; a change made through the admin API, or a `caddy reload` with a different file or adapter, disables signal reloads, so check the logs to confirm the reload took).

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
  # Stdin closes the argv channel only: it does not hide the password from
  # set -x tracing or your own account's view of the process.
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
- Automatic HTTPS (rolling documentation, checked September 2026): https://caddyserver.com/docs/automatic-https
- Caddy admin API (default `localhost:2019`, `POST /load` and `/config/` replace or edit the whole config, requires no credentials with only Host/Origin header checks, the permissioned-unix-socket warning for untrusted-workload hosts; rolling documentation, checked September 2026): https://caddyserver.com/docs/api
- Caddy `admin` global option (`admin off`, an address, or `admin unix//...`; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/options
- `request_body` directive (`max_size`; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/request_body
- Caddyfile directive list, which carries no `rate_limit` entry (rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives
- caddy-ratelimit, the community module that adds rate limiting (pinned README): https://raw.githubusercontent.com/mholt/caddy-ratelimit/5625512f24f6f59d6f64fb3aafe5eecff0b286db/README.md
- basic_auth directive (renamed from basicauth in Caddy v2.8.0; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/basic_auth
- tls directive (rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/tls
- reverse_proxy directive (X-Forwarded-* ignored from untrusted sources by default; `trusted_proxies`; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Caddy conventions (unix socket default mode 0200, `|<mode>` suffix; rolling documentation, checked September 2026): https://caddyserver.com/docs/conventions
- header directive (HSTS; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/header
- forward_auth directive (rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/forward_auth
- Caddy command-line signals (SIGUSR1 reload conditions; rolling documentation, checked September 2026): https://caddyserver.com/docs/command-line#signals
- Let's Encrypt ending expiration-notification emails (2025): https://letsencrypt.org/2025/01/22/ending-expiration-emails/
- Request matchers (path, wildcards, multiple paths; rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/matchers
- Caddy admin API default `DefaultAdminListen = "localhost:2019"` (pinned tag v2.11.4): https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L1433
- caddyserver/dist service unit (pinned commit 33ae08ff08d168572df2956ed14fbc4949880d94, checked October 2026): https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/init/caddy.service#L22-L32
- systemd execution manual (pinned v262, checked October 2026): https://github.com/systemd/systemd/blob/v262/man/systemd.exec.xml#L1558-L1660
- Cloudflare Access MFA requirements (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L17-L85
- Cloudflare Access JWT validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17
- Cloudflare Tunnel `access` setting, `cloudflared` validating the Access JWT (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L196-L215
- Docker networking documentation at 4e9a5751518ed8223a8dcde53693badddd72604f (container loopback, host namespace sharing, and the `--network container:` loopback example; the Linux bridge/host distinction above is inferred from these documented namespace semantics): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/_index.md#L286, https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/drivers/host.md#L11-L13, https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/_index.md#L302-L325


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- admin: Caddy admin source (v2.11.4)
- images: Caddy Docker source (fba2853501d36e8a72f946ac8cb7ff64d07e48f2)
- dist: Default Caddyfile source (33ae08ff08d168572df2956ed14fbc4949880d94)
- docs-rolling: Caddy documentation (rolling) (unknown)
- service: caddyserver/dist service unit (33ae08ff08d168572df2956ed14fbc4949880d94)
- ratelimit-source: caddy-ratelimit source (5625512f24f6f59d6f64fb3aafe5eecff0b286db)
- tags: Official image tag map (d82ca5102fa6735be29d5e1fc6ce03af77eb091e)
- docker-network: Docker networking documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- systemd: systemd manual (v262)
- cloudflare: Cloudflare docs (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- letsencrypt-notice: Let's Encrypt expiration-email notice (2025)

Claims (full source mapping in the JSON block below):

- auto-https (REASONED; docs-rolling): Caddy 2 obtains and renews public certificates and redirects HTTP to HTTPS; DNS must point here and the example requires public 80/443.
- issuers (REASONED; docs-rolling): Public certificates come from Let's Encrypt or ZeroSSL and renew automatically.
- renewal-monitoring (REASONED; docs-rolling, letsencrypt-notice): Set the ACME email contact but monitor renewal yourself: Let's Encrypt stopped expiration emails.
- backend (REASONED; docs-rolling): reverse_proxy sends traffic to 127.0.0.1:3000; keep the app private to prevent TLS/auth bypass.
- hsts (REASONED; docs-rolling): Caddy sends no HSTS automatically; add it only after HTTPS works across every included subdomain.
- forwarded (REASONED; docs-rolling): Caddy ignores untrusted client X-Forwarded-* by default; configure trusted_proxies behind a trusted CDN/proxy.
- internal-tls (REASONED; docs-rolling): tls internal uses a local CA; clients must trust its root, with caddy trust for the local host. tls also accepts explicit cert/key files.
- basic (REASONED; docs-rolling): basic_auth uses hashed passwords from caddy hash-password; it was named basicauth before v2.8.0 and remains single-factor.
- path-auth (REASONED; docs-rolling): Protect /admin and /admin/* together: path matches are exact and multiple paths are OR'ed.
- mfa (REASONED; docs-rolling, cloudflare): forward_auth (Caddy 2.5+) can delegate human authentication to Authelia; Cloudflare Access is a proposed layer that enforces MFA when its governing Access setting (policy over application over organization) requires it.
- access-origin (REASONED; docs-rolling, cloudflare): Cloudflare Access can require MFA when configured; the guide reasons that direct origin ingress can bypass Access, so restrict it; validate the Access JWT at the origin, which a tunnel's `access` setting has `cloudflared` do. Caddy still answers directly on 443.
- body-limit (REASONED; docs-rolling): Add request_body max_size 10MB inside the existing authenticated site; replacing the site without basic_auth makes it public.
- rate-limit (REASONED; docs-rolling, ratelimit-source): The standard build has no rate_limit directive; use a compiled community caddy-ratelimit module or an upstream layer.
- admin-bind (REASONED; admin, docs-rolling): The admin API defaults to localhost:2019 as of v2.11.4; never publish it or reverse-proxy to it.
- admin-authority (REASONED; docs-rolling): Reachable unauthenticated admin clients can replace config at POST /load, edit /config/ or stop with POST /stop.
- admin-isolation (REASONED; docs-rolling): Host/Origin checks are not process isolation; local untrusted workloads require a permissioned Unix socket.
- docker-admin (REASONED; tags, images, dist, admin): The official 2.11.4 Alpine, Windows Server Core 2022/2025, and Nano Server 2022/2025 runtime tags map to fba28535 Dockerfiles that EXPOSE 2019 and run the default Caddyfile without admin; absent overrides, the endpoint stays namespace-local.
- admin-override (REASONED; admin, dist, docs-rolling): A mounted admin setting or CADDY_ADMIN changes the address; do not set 0.0.0.0:2019 to make publication work.
- namespace (REASONED; images, dist, admin, docker-network, docs-rolling): The shipped admin default is localhost:2019. On Docker Engine on Linux, bridge networking keeps loopback container-local; host or container networking shares a namespace, so treat its processes as potential admin clients.
- admin-socket (REASONED; docs-rolling): admin unix//run/caddy/admin.sock uses owner-only mode 0200 by default; append &#124;0600 to set it explicitly.
- runtime-directory (REASONED; docs-rolling, service, systemd): The dist service at 33ae08ff runs as caddy without RuntimeDirectory; systemd v262 creates /run/caddy for RuntimeDirectory=caddy at service start and owns it as caddy. Restart for the socket switch is guide reasoning.
- reload (REASONED; docs-rolling, service): The dist service at 33ae08ff uses caddy reload --config /etc/caddy/Caddyfile --force; API reload uses the Caddyfile admin address. With admin off, guide reasoning requires systemd restart.
- signal-reload (REASONED; docs-rolling): A manual run without --resume may reload startup config via SIGUSR1; API changes or reload with a different file/adapter disable signal reloads.
- on-demand (REASONED; docs-rolling): Do not enable unrestricted on_demand TLS without an ask endpoint or host allowlist; this guide does not enable it.
- verify-config (REASONED; docs-rolling): Validate /etc/caddy/Caddyfile; no validation outcome is recorded.
- verify-redirect (REASONED; docs-rolling): HTTP should redirect to HTTPS.
- verify-auth (REASONED; docs-rolling): With site-wide auth, HTTPS without credentials returns 401.
- verify-scope (REASONED; docs-rolling): The @admin variant must return 401 for /admin and /admin/x, but an app response rather than 401 for a non-admin path.
- verify-size (REASONED; docs-rolling): Authenticated 1M reaches the app and 11M returns 413; 401/000 void the control. Auth can prevent body reads; remove request_body in isolation to attribute refusal.
- verify-backend (REASONED; docs-rolling): Read all listeners: app 3000 must be loopback-only even if proxy checks pass.
- verify-admin (REASONED; docs-rolling): TCP admin must bind only loopback; absent 2019 requires confirming admin off or a socket. Check Unix socket existence and owner restrictions separately.

````json
{
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "eed115dc2c26e54a446ea9a84398c1854c897f304005b983d79c201a37b58ccd",
  "components": {
    "admin": {
      "name": "Caddy admin source",
      "basis": "v2.11.4",
      "sources": {
        "s35044463fa67": "https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L1433",
        "s2bbcf239df02": "https://github.com/caddyserver/caddy/blob/v2.11.4/admin.go#L58-L67"
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
    "docs-rolling": {
      "name": "Caddy documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s434e7b7d7f63": "https://caddyserver.com/docs/automatic-https",
        "s3923477355fb": "https://caddyserver.com/docs/api",
        "sdbcd496895d6": "https://caddyserver.com/docs/caddyfile/options",
        "s31af5ed45a20": "https://caddyserver.com/docs/caddyfile/directives/request_body",
        "sec59a61934c5": "https://caddyserver.com/docs/caddyfile/directives",
        "sbc2bd9599bd1": "https://caddyserver.com/docs/caddyfile/directives/basic_auth",
        "s2e47c3139bd2": "https://caddyserver.com/docs/caddyfile/directives/tls",
        "s3865a73ccda3": "https://caddyserver.com/docs/caddyfile/directives/reverse_proxy",
        "s82efc39a8130": "https://caddyserver.com/docs/conventions",
        "s5a6da5adf385": "https://caddyserver.com/docs/caddyfile/directives/header",
        "s8df93f3e3d4c": "https://caddyserver.com/docs/caddyfile/directives/forward_auth",
        "sf12ad47e81b5": "https://caddyserver.com/docs/command-line#signals",
        "s38b1b78ce980": "https://caddyserver.com/docs/caddyfile/matchers"
      }
    },
    "service": {
      "name": "caddyserver/dist service unit",
      "basis": "33ae08ff08d168572df2956ed14fbc4949880d94",
      "sources": {
        "se70d276b03a1": "https://github.com/caddyserver/dist/blob/33ae08ff08d168572df2956ed14fbc4949880d94/init/caddy.service#L22-L32"
      }
    },
    "ratelimit-source": {
      "name": "caddy-ratelimit source",
      "basis": "5625512f24f6f59d6f64fb3aafe5eecff0b286db",
      "sources": {
        "s093420cd3d2f": "https://raw.githubusercontent.com/mholt/caddy-ratelimit/5625512f24f6f59d6f64fb3aafe5eecff0b286db/README.md"
      }
    },
    "tags": {
      "name": "Official image tag map",
      "basis": "d82ca5102fa6735be29d5e1fc6ce03af77eb091e",
      "sources": {
        "sdc8aca42f5e2": "https://github.com/docker-library/official-images/blob/d82ca5102fa6735be29d5e1fc6ce03af77eb091e/library/caddy#L7-L65"
      }
    },
    "docker-network": {
      "name": "Docker networking documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "se1437c0f19fb": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/_index.md#L286",
        "sfce645f8b46e": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/drivers/host.md#L11-L13",
        "sfd29f33e4108": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/_index.md#L302-L325"
      }
    },
    "systemd": {
      "name": "systemd manual",
      "basis": "v262",
      "sources": {
        "see108b0e0bba": "https://github.com/systemd/systemd/blob/v262/man/systemd.exec.xml#L1558-L1660"
      }
    },
    "cloudflare": {
      "name": "Cloudflare docs",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s6f6104362214": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L17-L85",
        "s81e5dd28d3e5": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17",
        "sa7c8d635bfd5": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L196-L215"
      }
    },
    "letsencrypt-notice": {
      "name": "Let's Encrypt expiration-email notice",
      "basis": "2025",
      "sources": {
        "sdf68595235d4": "https://letsencrypt.org/2025/01/22/ending-expiration-emails/"
      }
    }
  },
  "claims": {
    "auto-https": {"text": "Caddy 2 obtains and renews public certificates and redirects HTTP to HTTPS; DNS must point here and the example requires public 80/443.", "components": ["docs-rolling"], "sources": ["docs-rolling:s434e7b7d7f63"], "status": "REASONED"},
    "issuers": {"text": "Public certificates come from Let's Encrypt or ZeroSSL and renew automatically.", "components": ["docs-rolling"], "sources": ["docs-rolling:s434e7b7d7f63"], "status": "REASONED"},
    "renewal-monitoring": {"text": "Set the ACME email contact but monitor renewal yourself: Let's Encrypt stopped expiration emails.", "components": ["docs-rolling", "letsencrypt-notice"], "sources": ["docs-rolling:sdbcd496895d6", "letsencrypt-notice:sdf68595235d4"], "status": "REASONED"},
    "backend": {"text": "reverse_proxy sends traffic to 127.0.0.1:3000; keep the app private to prevent TLS/auth bypass.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3865a73ccda3"], "status": "REASONED"},
    "hsts": {"text": "Caddy sends no HSTS automatically; add it only after HTTPS works across every included subdomain.", "components": ["docs-rolling"], "sources": ["docs-rolling:s5a6da5adf385", "docs-rolling:s434e7b7d7f63"], "status": "REASONED"},
    "forwarded": {"text": "Caddy ignores untrusted client X-Forwarded-* by default; configure trusted_proxies behind a trusted CDN/proxy.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3865a73ccda3"], "status": "REASONED"},
    "internal-tls": {"text": "tls internal uses a local CA; clients must trust its root, with caddy trust for the local host. tls also accepts explicit cert/key files.", "components": ["docs-rolling"], "sources": ["docs-rolling:s2e47c3139bd2", "docs-rolling:s434e7b7d7f63"], "status": "REASONED"},
    "basic": {"text": "basic_auth uses hashed passwords from caddy hash-password; it was named basicauth before v2.8.0 and remains single-factor.", "components": ["docs-rolling"], "sources": ["docs-rolling:sbc2bd9599bd1"], "status": "REASONED"},
    "path-auth": {"text": "Protect /admin and /admin/* together: path matches are exact and multiple paths are OR'ed.", "components": ["docs-rolling"], "sources": ["docs-rolling:s38b1b78ce980", "docs-rolling:sbc2bd9599bd1"], "status": "REASONED"},
    "mfa": {"text": "forward_auth (Caddy 2.5+) can delegate human authentication to Authelia; Cloudflare Access is a proposed layer that enforces MFA when its governing Access setting (policy over application over organization) requires it.", "components": ["docs-rolling", "cloudflare"], "sources": ["docs-rolling:s8df93f3e3d4c", "cloudflare:s6f6104362214"], "status": "REASONED"},
    "access-origin": {"text": "Cloudflare Access can require MFA when configured; the guide reasons that direct origin ingress can bypass Access, so restrict it; validate the Access JWT at the origin, which a tunnel's `access` setting has `cloudflared` do. Caddy still answers directly on 443.", "components": ["docs-rolling", "cloudflare"], "sources": ["docs-rolling:s3865a73ccda3", "cloudflare:s6f6104362214", "cloudflare:s81e5dd28d3e5", "cloudflare:sa7c8d635bfd5"], "status": "REASONED"},
    "body-limit": {"text": "Add request_body max_size 10MB inside the existing authenticated site; replacing the site without basic_auth makes it public.", "components": ["docs-rolling"], "sources": ["docs-rolling:s31af5ed45a20", "docs-rolling:sbc2bd9599bd1"], "status": "REASONED"},
    "rate-limit": {"text": "The standard build has no rate_limit directive; use a compiled community caddy-ratelimit module or an upstream layer.", "components": ["docs-rolling", "ratelimit-source"], "sources": ["docs-rolling:sec59a61934c5", "ratelimit-source:s093420cd3d2f"], "status": "REASONED"},
    "admin-bind": {"text": "The admin API defaults to localhost:2019 as of v2.11.4; never publish it or reverse-proxy to it.", "components": ["admin", "docs-rolling"], "sources": ["admin:s35044463fa67", "admin:s2bbcf239df02", "docs-rolling:s3923477355fb"], "status": "REASONED"},
    "admin-authority": {"text": "Reachable unauthenticated admin clients can replace config at POST /load, edit /config/ or stop with POST /stop.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3923477355fb"], "status": "REASONED"},
    "admin-isolation": {"text": "Host/Origin checks are not process isolation; local untrusted workloads require a permissioned Unix socket.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3923477355fb", "docs-rolling:sdbcd496895d6"], "status": "REASONED"},
    "docker-admin": {"text": "The official 2.11.4 Alpine, Windows Server Core 2022/2025, and Nano Server 2022/2025 runtime tags map to fba28535 Dockerfiles that EXPOSE 2019 and run the default Caddyfile without admin; absent overrides, the endpoint stays namespace-local.", "components": ["tags", "images", "dist", "admin"], "sources": ["tags:sdc8aca42f5e2", "images:s0f0994ef9fac", "images:s2dce0bbf3a70", "images:sd2c1b05a8088", "images:sf3e9c2d4e0cd", "images:s6c800a156eac", "images:sc5c82704d33f", "images:sc1cb0e1fb9eb", "images:s11528dfcc516", "images:s70b76475a281", "dist:s433758a90af0", "admin:s35044463fa67", "admin:s2bbcf239df02", "images:sc5dd3f9746fe"], "status": "REASONED"},
    "admin-override": {"text": "A mounted admin setting or CADDY_ADMIN changes the address; do not set 0.0.0.0:2019 to make publication work.", "components": ["admin", "dist", "docs-rolling"], "sources": ["docs-rolling:sdbcd496895d6", "admin:s35044463fa67", "admin:s2bbcf239df02", "dist:s433758a90af0"], "status": "REASONED"},
    "namespace": {"text": "The shipped admin default is localhost:2019. On Docker Engine on Linux, bridge networking keeps loopback container-local; host or container networking shares a namespace, so treat its processes as potential admin clients.", "components": ["images", "dist", "admin", "docker-network", "docs-rolling"], "sources": ["docs-rolling:s3923477355fb", "images:s0f0994ef9fac", "images:s2dce0bbf3a70", "images:sd2c1b05a8088", "images:sf3e9c2d4e0cd", "images:sc5dd3f9746fe", "images:s6c800a156eac", "images:sc5c82704d33f", "images:sc1cb0e1fb9eb", "images:s11528dfcc516", "images:s70b76475a281", "dist:s433758a90af0", "admin:s35044463fa67", "docker-network:se1437c0f19fb", "docker-network:sfce645f8b46e", "docker-network:sfd29f33e4108"], "status": "REASONED"},
    "admin-socket": {"text": "admin unix//run/caddy/admin.sock uses owner-only mode 0200 by default; append |0600 to set it explicitly.", "components": ["docs-rolling"], "sources": ["docs-rolling:sdbcd496895d6", "docs-rolling:s82efc39a8130"], "status": "REASONED"},
    "runtime-directory": {"text": "The dist service at 33ae08ff runs as caddy without RuntimeDirectory; systemd v262 creates /run/caddy for RuntimeDirectory=caddy at service start and owns it as caddy. Restart for the socket switch is guide reasoning.", "components": ["docs-rolling", "service", "systemd"], "sources": ["docs-rolling:sdbcd496895d6", "service:se70d276b03a1", "systemd:see108b0e0bba"], "status": "REASONED"},
    "reload": {"text": "The dist service at 33ae08ff uses caddy reload --config /etc/caddy/Caddyfile --force; API reload uses the Caddyfile admin address. With admin off, guide reasoning requires systemd restart.", "components": ["docs-rolling", "service"], "sources": ["docs-rolling:sdbcd496895d6", "docs-rolling:sf12ad47e81b5", "service:se70d276b03a1"], "status": "REASONED"},
    "signal-reload": {"text": "A manual run without --resume may reload startup config via SIGUSR1; API changes or reload with a different file/adapter disable signal reloads.", "components": ["docs-rolling"], "sources": ["docs-rolling:sf12ad47e81b5"], "status": "REASONED"},
    "on-demand": {"text": "Do not enable unrestricted on_demand TLS without an ask endpoint or host allowlist; this guide does not enable it.", "components": ["docs-rolling"], "sources": ["docs-rolling:s434e7b7d7f63"], "status": "REASONED"},
    "verify-config": {"text": "Validate /etc/caddy/Caddyfile; no validation outcome is recorded.", "components": ["docs-rolling"], "sources": ["docs-rolling:sf12ad47e81b5"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should redirect to HTTPS.", "components": ["docs-rolling"], "sources": ["docs-rolling:s434e7b7d7f63"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "With site-wide auth, HTTPS without credentials returns 401.", "components": ["docs-rolling"], "sources": ["docs-rolling:sbc2bd9599bd1"], "status": "REASONED", "verify": [1]},
    "verify-scope": {"text": "The @admin variant must return 401 for /admin and /admin/x, but an app response rather than 401 for a non-admin path.", "components": ["docs-rolling"], "sources": ["docs-rolling:s38b1b78ce980", "docs-rolling:sbc2bd9599bd1"], "status": "REASONED", "verify": [1]},
    "verify-size": {"text": "Authenticated 1M reaches the app and 11M returns 413; 401/000 void the control. Auth can prevent body reads; remove request_body in isolation to attribute refusal.", "components": ["docs-rolling"], "sources": ["docs-rolling:s31af5ed45a20", "docs-rolling:sbc2bd9599bd1", "docs-rolling:sec59a61934c5"], "status": "REASONED", "verify": [1]},
    "verify-backend": {"text": "Read all listeners: app 3000 must be loopback-only even if proxy checks pass.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3865a73ccda3"], "status": "REASONED", "verify": [1]},
    "verify-admin": {"text": "TCP admin must bind only loopback; absent 2019 requires confirming admin off or a socket. Check Unix socket existence and owner restrictions separately.", "components": ["docs-rolling"], "sources": ["docs-rolling:s3923477355fb", "docs-rolling:sdbcd496895d6", "docs-rolling:s82efc39a8130"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
