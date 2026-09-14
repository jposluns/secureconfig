# Traefik: automatic TLS and authentication middleware

Applies to Traefik v2 and v3. Traefik obtains and renews certificates itself through ACME resolvers, which suits container deployments.

## 1. Static configuration: entry points, redirect, ACME

`traefik.yml`:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /letsencrypt/acme.json
      tlsChallenge: {}

providers:
  docker:
    exposedByDefault: false
```

`acme.json` must persist across restarts (volume-mount it) and be mode `600`. The TLS-ALPN challenge above needs port 443 reachable from the internet; use `httpChallenge` (port 80) or a `dnsChallenge` (wildcards, no inbound ports) where that fits better.

The `providers.docker` block turns on container discovery, and `exposedByDefault: false` is the security-relevant half. Its default is `true`, so a `providers.docker` block without that line routes every container the daemon can see, not only the one you labelled. The provider reads labels over the Docker socket, so mount it into the Traefik service:

```yaml
services:
  traefik:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

Mounting the socket gives Traefik control of the Docker daemon, which is root-equivalent on the host: a compromised Traefik is a compromised host. The `:ro` marks the socket file read-only; it does not make the Docker API read-only. To limit what Traefik can call, put a read-only Docker socket proxy in front of the socket (see the Docker provider reference under Sources).

Raise the protocol floor with a TLS options block in the dynamic configuration:

```yaml
tls:
  options:
    default:
      minVersion: VersionTLS12
```

## 2. Route a service with TLS (Docker labels)

```yaml
services:
  app:
    image: yourapp
    labels:
      - traefik.enable=true
      - traefik.http.routers.app.rule=Host(`app.example.com`)
      - traefik.http.routers.app.entrypoints=websecure
      - traefik.http.routers.app.tls.certresolver=letsencrypt
      - traefik.http.services.app.loadbalancer.server.port=3000
```

Labelling this container `traefik.enable=true` opts it in; it does not keep any other container private. With `exposedByDefault: false` set in section 1, Traefik ignores every container that lacks that label. Without it, discovery is daemon-wide, not scoped to this Compose project, so a database, cache, admin UI, or queue on the same host also gets a router, answering on the same `:443` listener to anyone who sends the matching `Host` header. The label opts a container in; it never opts others out, so keep it on each application you mean to publish.

Do not also publish the app's port with `ports:`; only Traefik publishes 80 and 443. See [docker.md](docker.md).

## 3. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). At the proxy, attach a basicAuth middleware with bcrypt entries from `htpasswd -nB admin`:

```yaml
    labels:
      - traefik.http.middlewares.app-auth.basicauth.users=admin:$$2y$$05$$REPLACE_WITH_HASH
      - traefik.http.routers.app.middlewares=app-auth
```

In Compose files every `$` in the hash must be doubled to `$$`. The file-provider equivalent, where no escaping is needed:

```yaml
http:
  middlewares:
    app-auth:
      basicAuth:
        users:
          - "admin:$2y$05$REPLACE_WITH_HASH"
```

basicAuth is single-factor. For human-facing sites, add MFA with the `forwardAuth` middleware pointed at [Authelia](https://www.authelia.com/) or [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy), or front the site with Cloudflare Access; options in [mfa.md](mfa.md).

## 4. Bound the expensive endpoints

Three middlewares, attached to the router alongside the auth middleware from section 3.

```yaml
    # ADD these to the labels you already have. Do not replace that list:
    # section 2 carries the router rule, entrypoints, certresolver and service
    # port, and section 3 carries basicauth.users. A labels block without them
    # breaks routing and authentication.
    labels:
      - traefik.http.middlewares.app-body.buffering.maxRequestBodyBytes=10485760
      - traefik.http.middlewares.app-inflight.inflightreq.amount=10
      - traefik.http.middlewares.app-rate.ratelimit.average=10
      - traefik.http.middlewares.app-rate.ratelimit.burst=20
      # replace the section 3 middlewares= line with this one
      - traefik.http.routers.app.middlewares=app-auth,app-rate,app-inflight,app-body
```

Order matters here. `buffering` reads the request into memory or disk before forwarding it, so it must
come after the admission controls; placed first, an accepted upload consumes the buffer before
`ratelimit` or `inflightreq` has considered it. `maxRequestBodyBytes` sets the largest body accepted;
`memRequestBodyBytes`, which defaults to 1048576, is the separate threshold at which buffering moves
from memory to disk. Raising the first increases what you will buffer, not where that buffer lives. `ratelimit` is per source by default, while `inflightreq` caps concurrent
in-flight requests rather than their rate, and its `sourceCriterion` defaults to the request host rather
than the client, so set it explicitly if you want a per-client cap.

## 5. Verify

```bash
curl -q -sI http://app.example.com/     # expect a redirect to https://
curl -q -sI https://app.example.com/    # expect 401 without credentials once auth is on
head -c 1M /dev/zero > /tmp/under.bin && head -c 11M /dev/zero > /tmp/over.bin
curl -q -s -o /dev/null -w '%{http_code}\n' -u admin:REPLACE_WITH_PASSWORD --data-binary @/tmp/under.bin https://app.example.com/
                                     # positive control: under the limit, must NOT be 413
curl -q -s -o /dev/null -w '%{http_code}\n' -u admin:REPLACE_WITH_PASSWORD --data-binary @/tmp/over.bin  https://app.example.com/
                                     # 413. Credentials matter: app-auth is first in the middleware
                                     # chain, so an unauthenticated probe stops at 401 before any limit
                                     # sees the body. A backend with its own limit returns the same
                                     # code, so attributing the refusal needs an isolated environment
                                     # with app-body removed
seq 1 40 | xargs -P 40 -I{} curl -q -s -o /dev/null -w '%{http_code}\n' -u admin:REPLACE_WITH_PASSWORD https://app.example.com/ | sort | uniq -c
                                     # A 429 appeared. That is all this shows. inflightreq also returns
                                     # 429, and an upstream under load can too, so this does not
                                     # establish that ratelimit fired. Attributing it needs an isolated
                                     # environment with both disabled as a baseline, then each enabled
                                     # alone, with the arrival rate actually measured
rm -f /tmp/under.bin /tmp/over.bin
docker compose ps                    # only Traefik publishes ports; the app's 3000 must NOT be published
sudo ss -tlnp                        # read the whole listener table, do not grep it down to the port you
                                     # expect (that hides an unexpected listener): only Traefik should
                                     # answer on the host. A backend answering on 3000 directly bypasses
                                     # Traefik's TLS and its authentication middleware
```

Check the Traefik log for ACME errors on first start; issuance failures otherwise surface as a self-signed "TRAEFIK DEFAULT CERT" in the browser.

`docker compose ps` and `ss` catch a container that bypasses Traefik with its own `ports:`, but neither can see a container Traefik routes without your asking: a routed container has no host port publication of its own. To confirm `exposedByDefault: false` actually excludes unlabelled containers, launch an unlabelled canary on Traefik's network and probe the front door. Do this on a disposable copy of the deployment; never make a container deliberately routable on the production host.

```yaml
services:
  canary:
    image: traefik/whoami   # one HTTP port, echoes its own hostname; no traefik.* labels, no ports:
```

`traefik/whoami` listens on a single HTTP port, so Traefik's single-port detection can build a service for it and a routed reply is unmistakable (the body carries a `Hostname:` line). Read the router rule Traefik generated for the canary; its `Host(...)` value is the canary's normalized name, and you pass that value as the `Host:` header below. Probe plain HTTP against the `:443` listener: the auto-generated router never requested TLS, so it answers plain HTTP even there.

```bash
(                              # a subshell, so your own shell arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_TRAEFIK_HOST' 'REPLACE_WITH_HTTPS_PORT' 'REPLACE_WITH_CANARY_HOST_HEADER'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2:$3" in
    *REPLACE_WITH_*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H "Host: $3" \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:$2/"
)
```

With `exposedByDefault: false` the canary returns `http=404` from Traefik's unmatched-route handler: it was ignored, and that is the pass. Calibrate first on the exposed fixture (temporarily `exposedByDefault: true`), where the canary must return `http=200` with the whoami `Hostname:` body; that proves the probe reaches Traefik. Without that positive calibration a `404` is not trustworthy, because it equally means the canary never joined Traefik's network. On production, run the probe only after applying the fix; a canary that answers `200` there is a live exposure to remove, not a passing test.

A `404` for the canary also appears when the whole Docker provider is off, which breaks all routing. Confirm the provider still works by probing the app itself, published only over HTTPS:

```bash
(                              # a subshell, so your own shell arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_APP_HOST' 'REPLACE_WITH_HTTPS_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1:$2/"
)
```

The app must return its known `http=200`; do not accept just any `200`. The fix is confirmed when, in the same run, the app answers `200` and the canary answers `404`: routing works and the unlabelled container is excluded. No `-k` here, the app needs a real certificate.

## Common mistakes

- Enabling the Traefik dashboard (`api.insecure=true` or an unprotected `api@internal` router) on a public entry point; keep it off or behind the auth middleware.
- Forgetting to persist `acme.json`, which re-issues certificates on every restart and hits CA rate limits.
- Single `$` in Compose basicauth labels, which breaks the hash silently.
- Enabling the Docker provider but leaving `exposedByDefault` at its default of `true`, which publishes every discovered container rather than only the labelled one.
- Assuming this page covers Docker Swarm. It covers standalone Docker; Swarm is a separate provider (`providers.swarm` in Traefik v3) with its own `exposedByDefault`, which also defaults to `true`. Consult the Swarm provider reference for your version before relying on this page under Swarm.

## Sources (checked September 2026)

- Traefik documentation: https://doc.traefik.io/traefik/ (HTTPS/ACME, routers, and basicAuth middleware sections)
- Docker provider (`exposedByDefault`, socket endpoint): https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/
- Buffering middleware (`maxRequestBodyBytes`, `memRequestBodyBytes`): https://doc.traefik.io/traefik/middlewares/http/buffering/
- InFlightReq middleware (`amount`): https://doc.traefik.io/traefik/middlewares/http/inflightreq/
- RateLimit middleware (`average`, `burst`, `period`): https://doc.traefik.io/traefik/middlewares/http/ratelimit/
