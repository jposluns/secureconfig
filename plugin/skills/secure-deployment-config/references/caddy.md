# Caddy: TLS and authentication

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

Caddy runs a local admin API, by default on `localhost:2019`, that requires no credentials: anything that can reach it replaces the whole configuration with `POST /load`, edits it path by path under `/config/`, or stops the server with `POST /stop`. Its Host and Origin header checks block a browser on another site, but they are not process isolation, so the endpoint's safety rests on the loopback bind. Never publish it: do not reverse-proxy a route to `:2019`, and never move it to a public address.

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

## 6. Verify

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

- Automatic HTTPS: https://caddyserver.com/docs/automatic-https
- Caddy admin API (default `localhost:2019`, `POST /load` and `/config/` replace or edit the whole config, requires no credentials with only Host/Origin header checks, the permissioned-unix-socket warning for untrusted-workload hosts): https://caddyserver.com/docs/api
- Caddy `admin` global option (`admin off`, an address, or `admin unix//...`): https://caddyserver.com/docs/caddyfile/options
- `request_body` directive (`max_size`): https://caddyserver.com/docs/caddyfile/directives/request_body
- Caddyfile directive list, which carries no `rate_limit` entry: https://caddyserver.com/docs/caddyfile/directives
- caddy-ratelimit, the community module that adds rate limiting: https://github.com/mholt/caddy-ratelimit
- basic_auth directive: https://caddyserver.com/docs/caddyfile/directives/basic_auth
- tls directive: https://caddyserver.com/docs/caddyfile/directives/tls
- reverse_proxy directive (X-Forwarded-* ignored from untrusted sources by default; `trusted_proxies`): https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Caddy conventions (unix socket default mode 0200, `|<mode>` suffix): https://caddyserver.com/docs/conventions
- header directive (HSTS): https://caddyserver.com/docs/caddyfile/directives/header
- forward_auth directive: https://caddyserver.com/docs/caddyfile/directives/forward_auth
- Caddy command-line signals (SIGUSR1 reload conditions): https://caddyserver.com/docs/command-line#signals
- Let's Encrypt ending expiration-notification emails (2025): https://letsencrypt.org/2025/01/22/ending-expiration-emails/
- Request matchers (path, wildcards, multiple paths): https://caddyserver.com/docs/caddyfile/matchers
