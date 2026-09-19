# nginx: TLS and authentication

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

For explicit cipher lists, generate them with the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) instead of copying from old tutorials; the protocol floor above is the part that must not be omitted. nginx defaults `ssl_session_tickets on`, and un-rotated ticket keys weaken forward secrecy: either set `ssl_session_tickets off`, or on nginx 1.23.2+ give it a shared `ssl_session_cache` so it rotates the ticket keys automatically.

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

Basic authentication is single-factor. For human-facing sites, add MFA with the `auth_request` mechanism pointed at an [Authelia](https://www.authelia.com/) or [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) portal, or front the site with Cloudflare Access; options in [mfa.md](mfa.md).

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

## 5. Verify

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
- `add_header` in a `location` block silently drops ALL headers inherited from `server`. That is inheritance, which `always` does not change (`always` changes which response codes the header is added to, not inheritance). Keep HSTS at the `server` level, and if a `location` needs its own `add_header`, re-declare HSTS inside it too.
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
