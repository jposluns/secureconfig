# HAProxy: TLS termination and authentication

HAProxy's public frontend, its stats interface, its runtime API, and any directly reachable backend are separate exposure surfaces; protect and verify each one you enable. These examples target a maintained HAProxy 3.0 installation.

Get a certificate first ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)). This example combines the certificate chain and its matching private key in one PEM file (HAProxy also supports separately loaded keys):

```bash
sudo mkdir -p /etc/haproxy/certs && sudo chmod 700 /etc/haproxy/certs
# Write the combined PEM to a root-only temp file (umask 077 keeps it mode 600), then rename it into place,
# so the private key is never briefly world-readable and a failure leaves nothing half-written.
sudo bash -c 'umask 077; tmp=$(mktemp /etc/haproxy/certs/.pem.XXXXXX) || exit 1
  cat /etc/letsencrypt/live/example.com/fullchain.pem \
      /etc/letsencrypt/live/example.com/privkey.pem > "$tmp" || { rm -f "$tmp"; exit 1; }
  mv "$tmp" /etc/haproxy/certs/example.com.pem'
```

Re-run the concatenation from a certbot deploy hook so renewals reach HAProxy.

## 1. Terminate TLS and redirect HTTP

```haproxy
global
    ssl-default-bind-options ssl-min-ver TLSv1.2
    # Preserve the package's service hardening; for a root-started deployment, drop privileges and jail the
    # workers (provision the account and an empty root-owned /var/lib/haproxy first).
    user haproxy
    group haproxy
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock user root group root mode 600 level admin

defaults
    mode http
    timeout connect 5s
    timeout client  30s
    timeout server  30s
    timeout http-request 10s

frontend web
    bind :80
    bind :443 ssl crt /etc/haproxy/certs/example.com.pem
    http-request redirect scheme https code 301 unless { ssl_fc }
    http-after-response set-header Strict-Transport-Security "max-age=31536000" if { ssl_fc }
    default_backend app

backend app
    server app1 127.0.0.1:3000 check
```

`ssl-min-ver` is available on maintained HAProxy 3.0. For explicit cipher lists, `ssl-default-bind-ciphers` configures TLS 1.2 and `ssl-default-bind-ciphersuites` configures TLS 1.3; the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) is a policy source, not the authority for HAProxy syntax. `http-after-response` (HAProxy 2.2+) sets the HSTS header on HAProxy's own generated responses, such as the 401 and 413 below, which `http-response` would miss; add `includeSubDomains` only once every affected subdomain is served over HTTPS. The backend here is plaintext on loopback; for a remote backend, require and verify its certificate, for example `server app1 app.internal:443 ssl verify required ca-file /etc/ssl/certs/internal-ca.crt verifyhost app.internal check`.

## 2. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). At the proxy, define a userlist with a crypt(3)-hashed password and demand it:

```bash
openssl passwd -6        # prompts, outputs a $6$ SHA-512 crypt hash
```

```haproxy
userlist admins
    user admin password $6$REPLACE_WITH_HASH

backend app
    http-request auth realm Restricted unless { http_auth(admins) }
    server app1 127.0.0.1:3000 check
```

Hashed `password` entries rely on the system's crypt(3); `$6$` works on glibc-based Linux. Avoid `insecure-password`, which stores the password in cleartext in the configuration file. For machine-to-machine access, client certificates are stronger: add `verify required ca-file /etc/ssl/certs/internal-ca.crt` to the `bind :443` line.

Basic authentication here is single-factor. For human-facing sites, add MFA with an [Authelia](https://www.authelia.com/) portal (HAProxy is supported through Authelia's Lua module) or by fronting the site with Cloudflare Access; options in [mfa.md](mfa.md).

## 3. Bound the expensive endpoints

The timeouts in section 1 are half of this. Add a concurrency cap with `maxconn`, which in `global` is
the maximum per-process concurrent connections and in a frontend caps that frontend.

HAProxy has **no single request-body-size directive**. The rule below uses the `req.body_size` fetch,
which the manual defines as the *advertised* length of the body, so for a request carrying
`Content-Length` it reads that value and can reject without waiting for the request body. Two limits are worth knowing.
It needs no request buffering; do not add `option http-buffer-request` for it, because the manual says
that option waits until either the whole body is received or the request buffer is full, which buffers
the upload you are trying to refuse. And for a chunked request, which advertises no length, the manual
says the fetch returns the size of the available data instead, which without buffering is only what has
arrived so far, so this rule does not meaningfully bound a chunked upload. Enforce the real limit at the
application and treat this as a front-door guard against the common case.

```haproxy
# add to the existing global section
maxconn 4096

# add to `frontend web` from section 1. Do not paste a new frontend: that one
# carries bind, the HTTPS redirect, the HSTS header and default_backend.
maxconn 2000
http-request deny deny_status 413 if { req.body_size gt 10485760 }
```

## 4. The management plane: stats and the runtime API

The stats page and the runtime API are separate from proxied traffic and easy to leave open. Inventory both in every loaded configuration, and leave each disabled unless needed.

The stats page is disabled unless a configuration enables it (in a `frontend`, `listen`, `backend`, or `defaults`), and enabling it authenticates nothing on its own: an unauthenticated page leaks operational detail, and `stats admin` additionally lets a caller enable, disable, or drain backends. Inventory every loaded configuration, omit `stats admin` from a monitoring page, keep any admin page private, and reuse the hashed userlist rather than a cleartext `stats auth`:

```haproxy
listen monitoring
    bind 127.0.0.1:8404 ssl crt /etc/haproxy/certs/example.com.pem
    mode http
    stats enable
    stats uri /stats
    stats http-request auth unless { http_auth(admins) }
```

The runtime API (the `stats socket` added to `global` above) is not enabled by default, and its default command level is `operator`; `level admin` grants authority, not authentication. Keep it a root-owned local Unix socket at mode `600` and never expose it as an unauthenticated TCP socket, because HTTP stats authentication does not protect it.

## 5. Verify

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg && sudo systemctl reload haproxy
# REASONED, not demonstrated here: no HAProxy runtime in the authoring environment, so the shell was checked
# but the exposed-vs-fixed responses were not. Backlog row 1.80 tracks running it live. A transport, TLS, or
# DNS error is inconclusive, never a pass.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell: no inherited extdebug, no function named like a command below
  set +x +a                                     # never trace or export the credential read below
  { unset -n pw && unset -v pw; } 2>/dev/null ||
    { echo 'a readonly pw is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the host; not probing'; exit 2 ;; esac
  IFS= read -r -s -p 'admin password: ' pw < /dev/tty || exit 2; echo
  case "$pw" in ''|*[[:cntrl:]]*) echo 'supply the admin password; not probing'; exit 2 ;; esac
  pw=${pw//\\/\\\\}; pw=${pw//\"/\\\"}   # escape \ and " so curl --config parsing keeps the exact password
  base=(-sS --noproxy '*' --connect-timeout 5 --max-time 30)
  # 1) HTTP must redirect to HTTPS.
  curl -q -g "${base[@]}" -D - -o /dev/null -w 'redirect http=%{http_code}\n' "http://$1/"   # expect 301 + https Location
  # 2) Auth triple against ONE protected resource. No creds and wrong creds must be 401; valid creds the app's
  #    expected success. The password reaches curl through stdin config (curl --config -), never argv.
  curl -q -g "${base[@]}" -o /dev/null -w 'no-creds http=%{http_code}\n' "https://$1/"
  printf 'user = "admin:%s"\n' 'definitely-wrong' | curl -q -g "${base[@]}" --config - -o /dev/null -w 'bad-creds http=%{http_code}\n' "https://$1/"
  printf 'user = "admin:%s"\n' "$pw"              | curl -q -g "${base[@]}" --config - -o /dev/null -w 'valid http=%{http_code}\n' "https://$1/"
  # 3) Body-size guard, BOTH cases with valid creds so a 401 cannot masquerade as the result. Payloads live in
  #    a private temp dir removed on exit.
  tmp=$(mktemp -d) || { echo 'no tempdir; not probing'; exit 2; }
  trap 'rm -rf "$tmp"' EXIT
  head -c 1M /dev/zero > "$tmp/under.bin"  || { echo 'payload write failed'; exit 2; }
  head -c 11M /dev/zero > "$tmp/over.bin" || { echo 'payload write failed'; exit 2; }
  for f in under over; do
    printf 'user = "admin:%s"\n' "$pw" | curl -q -g "${base[@]}" --config - --data-binary @"$tmp/$f.bin" \
      -o /dev/null -w "$f http=%{http_code}\n" "https://$1/"
  done
  # under: the app's success, not 413; over: 413. req.body_size reads the advertised Content-Length, which curl
  # sets here; a chunked upload advertises none and is not covered. A backend can return 413 too, so to
  # attribute the refusal to HAProxy, in an isolated fixture remove ONLY the http-request deny line and
  # confirm the over upload then reaches the app.
)
ss -tlnp   # inventory: the backend (3000) must be 127.0.0.1 only, never 0.0.0.0 - the checks above pass while
           # the backend also answers directly on 3000, bypassing HAProxy's TLS and auth. Confirm the runtime
           # socket is a root-owned mode-600 Unix socket (ls -l /run/haproxy/admin.sock), not a TCP listener.
```

Verify each management surface you enabled, reasoned the same way (backlog row 1.80): the stats listener with
an unauthenticated request (refused) and a valid-credential request (returns the statistics) against that
listener specifically; the runtime socket by its ownership and mode and an unauthorized local identity
(permission denied), since `show cli level` reporting `admin` is the authorized level, not proof of access
control; and, where `verify required` is set, client certificates (no certificate and an untrusted one
rejected at TLS, a trusted one admitted with `--cert`/`--key`, server verification kept on).

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell: no inherited extdebug, no function named like a command below
  set +x +a
  { unset -n sp && unset -v sp; } 2>/dev/null ||
    { echo 'a readonly sp is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the host; not probing'; exit 2 ;; esac
  base=(-sS --noproxy '*' --connect-timeout 5 --max-time 15)
  # Stats listener (run on the HAProxy machine; --resolve keeps the certificate hostname while connecting to
  # the loopback bind): no credentials must be refused; valid credentials return the statistics.
  curl -q -g "${base[@]}" --resolve "$1:8404:127.0.0.1" -o /dev/null -w 'stats no-creds=%{http_code}\n' "https://$1:8404/stats"
  IFS= read -r -s -p 'stats admin password: ' sp < /dev/tty || exit 2; echo
  case "$sp" in ''|*[[:cntrl:]]*) echo 'supply the stats password; not probing'; exit 2 ;; esac
  sp=${sp//\\/\\\\}; sp=${sp//\"/\\\"}
  printf 'user = "admin:%s"\n' "$sp" | curl -q -g "${base[@]}" --resolve "$1:8404:127.0.0.1" --config - -o /dev/null -w 'stats auth=%{http_code}\n' "https://$1:8404/stats"
  # mTLS, only if `bind ... verify required`: no cert and an untrusted cert must be rejected at TLS; a trusted
  # cert must be admitted (it may still return 401 if Basic auth is also configured). The path guards keep a
  # local file error from standing in for a server rejection.
  curl -q -g "${base[@]}" -o /dev/null -w 'mtls no-cert=%{http_code} exit=%{exitcode}\n' "https://$1/"
  for pair in 'REPLACE_WITH_UNTRUSTED_CRT:REPLACE_WITH_UNTRUSTED_KEY:untrusted' 'REPLACE_WITH_TRUSTED_CRT:REPLACE_WITH_TRUSTED_KEY:trusted'; do
    crt=${pair%%:*}; rest=${pair#*:}; key=${rest%%:*}; label=${rest##*:}
    case "$crt$key" in *REPLACE_WITH_*) echo "substitute the $label cert and key; not probing"; continue ;; esac
    if [ -r "$crt" ] && [ -r "$key" ]; then
      curl -q -g "${base[@]}" --cert "$crt" --key "$key" \
        -o /dev/null -w "mtls $label=%{http_code} exit=%{exitcode}\n" "https://$1/"
    else
      echo "$label cert or key not readable; not probing"
    fi
  done
)
# Runtime socket: root-owned mode-600 Unix socket, and an unauthorized local identity must be denied.
ls -l /run/haproxy/admin.sock                                       # expect srw------- root root
# guard-conventions: allow fixed local HAProxy admin socket /run/haproxy/admin.sock; no reader-substituted target
printf 'show info\n' | sudo socat - /run/haproxy/admin.sock | head -1   # authorized (root): prints info
sudo -u nobody socat - /run/haproxy/admin.sock < /dev/null         # unauthorized identity: expect permission denied
```

## Common mistakes

- Copying only `fullchain.pem` into the combined crt file used here; that file needs the matching private key too (HAProxy can instead load a separate adjacent key file, but this example uses the combined form).
- Renewing the certificate without rebuilding the combined PEM or reloading HAProxy.
- Backends reachable directly on `0.0.0.0`, bypassing the proxy; bind them to `127.0.0.1` and confirm with `ss -tlnp`.

## Sources (checked September 2026)

- HAProxy 3.0 Configuration Manual (`bind ssl crt`/`verify`, `ssl-default-bind-options`/`-ciphers`/`-ciphersuites`, `maxconn`, `req.body_size`, `http-request deny deny_status`, `http-after-response`, `timeout http-request`, `stats enable`/`auth`/`admin`, `user`/`group`/`chroot`): https://docs.haproxy.org/3.0/configuration.html
- HAProxy 3.0 Management Guide (runtime API over the `stats socket`, command levels, reload): https://docs.haproxy.org/3.0/management.html
- HAProxy supported releases: https://www.haproxy.org/
- HAProxy statistics dashboard (`stats enable`/`auth`/`admin` capabilities): https://www.haproxy.com/documentation/haproxy-configuration-tutorials/alerts-and-monitoring/statistics/
- Authelia HAProxy integration (MFA portal): https://www.authelia.com/integration/proxies/haproxy/
- Mozilla SSL Configuration Generator (TLS policy, not HAProxy syntax): https://ssl-config.mozilla.org/
