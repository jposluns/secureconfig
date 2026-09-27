---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "476384fc20fff9b913a1d3041f29db0e454dffd93bf9cf221b91c8912c14a960",
  "components": {
    "traefik": {
      "name": "Traefik scope",
      "basis": "v2 and v3",
      "sources": {
        "scbc0f2135c78": "https://doc.traefik.io/traefik/"
      }
    },
    "docker": {
      "name": "Traefik Docker provider",
      "basis": "unknown",
      "sources": {
        "se23fe4fe79fa": "https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/"
      }
    },
    "swarm": {
      "name": "Traefik Swarm provider",
      "basis": "unknown",
      "sources": {
        "s256d46f3f558": "https://doc.traefik.io/traefik/reference/install-configuration/providers/swarm/"
      }
    },
    "middleware": {
      "name": "Traefik middleware documentation",
      "basis": "unknown",
      "sources": {
        "sd987195d64dd": "https://doc.traefik.io/traefik/middlewares/http/buffering/",
        "sd20dcba7ebca": "https://doc.traefik.io/traefik/middlewares/http/inflightreq/",
        "scf1b1e35ef5d": "https://doc.traefik.io/traefik/middlewares/http/ratelimit/"
      }
    },
    "curl": {
      "name": "curl write-out minimum",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "entrypoints": {"text": "For Traefik v2/v3, web :80 redirects to HTTPS websecure :443 and an ACME resolver obtains/renews certificates.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "acme-storage": {"text": "Persist acme.json across restarts with mode 600 to retain certificates and avoid repeated issuance/rate limits.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "acme-challenges": {"text": "TLS-ALPN requires inbound 443; HTTP-01 uses 80, while DNS supports wildcards without inbound ports.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "docker-default": {"text": "Docker discovery defaults exposedByDefault to true; set false and opt each intended container in with traefik.enable=true.", "components": ["docker"], "sources": ["docker:se23fe4fe79fa"], "status": "REASONED"},
    "docker-scope": {"text": "Discovery is daemon-wide, not Compose-project scoped; eligible unlabelled containers get routers unless excluded. Missing usable ports skip service creation.", "components": ["docker"], "sources": ["docker:se23fe4fe79fa"], "status": "REASONED"},
    "docker-socket": {"text": "The Docker socket gives daemon control despite :ro; use a restricted socket proxy to limit API access.", "components": ["docker"], "sources": ["docker:se23fe4fe79fa"], "status": "REASONED"},
    "tls-floor": {"text": "Dynamic default TLS options set minVersion VersionTLS12.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "route": {"text": "Docker labels select the app host, websecure, letsencrypt resolver and backend port 3000.", "components": ["traefik", "docker"], "sources": ["traefik:scbc0f2135c78", "docker:se23fe4fe79fa"], "status": "REASONED"},
    "backend-isolation": {"text": "Publish only Traefik 80/443, not the app's 3000, to prevent middleware/TLS bypass.", "components": ["docker"], "sources": ["docker:se23fe4fe79fa"], "status": "REASONED"},
    "basic": {"text": "Attach bcrypt basicAuth to the router; htpasswd -nB -C 12 selects cost 12 rather than bare cost 5; the OWASP minimum is not directly sourced here.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "compose-hash": {"text": "Double each dollar sign in Compose hash labels; file-provider hashes need no such escaping.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "file-provider": {"text": "Load dynamic files with providers.file.directory/filename and reference their middleware from Docker as app-auth@file.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "mfa": {"text": "Basic is single-factor; use forwardAuth with Authelia/oauth2-proxy or front the site with Cloudflare Access for human MFA.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "body-limit": {"text": "Attach buffering.maxRequestBodyBytes=10485760 alongside existing auth/routing labels; it bounds accepted body size.", "components": ["middleware"], "sources": ["middleware:sd987195d64dd"], "status": "REASONED"},
    "buffer-storage": {"text": "memRequestBodyBytes defaults to 1048576 and controls the memory-to-disk threshold independently of maximum accepted body size.", "components": ["middleware"], "sources": ["middleware:sd987195d64dd"], "status": "REASONED"},
    "rate-limit": {"text": "average=10 and burst=20 configure a rate cap, per source by default.", "components": ["middleware"], "sources": ["middleware:scf1b1e35ef5d"], "status": "REASONED"},
    "inflight": {"text": "inflightreq.amount=10 bounds concurrent requests; sourceCriterion defaults to request host rather than client, so configure a per-client cap explicitly.", "components": ["middleware"], "sources": ["middleware:sd20dcba7ebca"], "status": "REASONED"},
    "middleware-order": {"text": "Rate/inflight precede auth to count rejected logins; buffering follows admission controls to avoid buffering rejected uploads.", "components": ["traefik", "middleware"], "sources": ["traefik:scbc0f2135c78", "middleware:sd987195d64dd", "middleware:scf1b1e35ef5d", "middleware:sd20dcba7ebca"], "status": "REASONED"},
    "dashboard": {"text": "Keep api.insecure and unprotected api@internal routers off public entry points or protect the dashboard with auth.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED"},
    "swarm": {"text": "Standalone Docker guidance does not cover Swarm; v3 uses providers.swarm and its separate exposedByDefault also defaults true.", "components": ["swarm"], "sources": ["swarm:s256d46f3f558"], "status": "REASONED"},
    "verify-redirect": {"text": "HTTP should redirect to HTTPS.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Unauthenticated HTTPS should return 401 once auth is attached.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED", "verify": [1]},
    "verify-size": {"text": "Authenticated 1M must reach the app and 11M return 413; 401/000 invalidate the control. Remove app-body in isolation to rule out backend refusal.", "components": ["middleware", "traefik"], "sources": ["middleware:sd987195d64dd", "traefik:scbc0f2135c78"], "status": "REASONED", "verify": [1]},
    "observed-429": {"text": "The guide records only a 429 response; no limiter attribution or exposed/fixed demonstration is established.", "components": ["middleware"], "sources": ["middleware:scf1b1e35ef5d", "middleware:sd20dcba7ebca"], "status": "DEMONSTRATED", "evidence": "A 429 appeared. That is all this shows."},
    "verify-rate": {"text": "Concurrent unauthenticated probes can reach pre-auth limiters; 429 alone cannot distinguish rate, inflight or upstream refusal. Compare each limiter alone against both disabled.", "components": ["middleware"], "sources": ["middleware:scf1b1e35ef5d", "middleware:sd20dcba7ebca"], "status": "REASONED", "verify": [1]},
    "verify-isolation": {"text": "Compose ps covers one project; ss misses NAT-only publication without a userland proxy. Neither finds unintended routes through Traefik.", "components": ["docker"], "sources": ["docker:se23fe4fe79fa"], "status": "REASONED", "verify": [1]},
    "verify-acme": {"text": "Inspect ACME startup errors; failed issuance can leave a self-signed TRAEFIK DEFAULT CERT.", "components": ["traefik"], "sources": ["traefik:scbc0f2135c78"], "status": "REASONED", "verify": [1]},
    "canary-route": {"text": "On a disposable deployment, unlabelled traefik/whoami has one HTTP port; use its generated Host rule and plain HTTP even on :443 because the generated router requests no TLS.", "components": ["docker", "traefik"], "sources": ["docker:se23fe4fe79fa", "traefik:scbc0f2135c78"], "status": "REASONED", "verify": [2]},
    "verify-canary": {"text": "Calibrate exposedByDefault true with 200 and the canary Hostname body; false should give 404. Missing discovery/provider also gives 404, unreachable backend 502/504.", "components": ["docker", "curl"], "sources": ["docker:se23fe4fe79fa", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-app-control": {"text": "In the same run, the app must return 401 or known authenticated 200 while the canary gives 404; app 401 proves routing, not proxy-auth attachment. Keep TLS verification.", "components": ["docker", "traefik", "curl"], "sources": ["docker:se23fe4fe79fa", "traefik:scbc0f2135c78", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [3]}
  }
}
---
# Traefik: automatic TLS and authentication middleware

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| entrypoints: For Traefik v2/v3, web :80 redirects to HTTPS websecure :443 and an ACME resolver obtains/renews certificates. | Traefik scope v2 and v3 | REASONED |
| acme-storage: Persist acme.json across restarts with mode 600 to retain certificates and avoid repeated issuance/rate limits. | Traefik scope v2 and v3 | REASONED |
| acme-challenges: TLS-ALPN requires inbound 443; HTTP-01 uses 80, while DNS supports wildcards without inbound ports. | Traefik scope v2 and v3 | REASONED |
| docker-default: Docker discovery defaults exposedByDefault to true; set false and opt each intended container in with traefik.enable=true. | Traefik Docker provider unknown | REASONED |
| docker-scope: Discovery is daemon-wide, not Compose-project scoped; eligible unlabelled containers get routers unless excluded. Missing usable ports skip service creation. | Traefik Docker provider unknown | REASONED |
| docker-socket: The Docker socket gives daemon control despite :ro; use a restricted socket proxy to limit API access. | Traefik Docker provider unknown | REASONED |
| tls-floor: Dynamic default TLS options set minVersion VersionTLS12. | Traefik scope v2 and v3 | REASONED |
| route: Docker labels select the app host, websecure, letsencrypt resolver and backend port 3000. | Traefik scope v2 and v3; Traefik Docker provider unknown | REASONED |
| backend-isolation: Publish only Traefik 80/443, not the app's 3000, to prevent middleware/TLS bypass. | Traefik Docker provider unknown | REASONED |
| basic: Attach bcrypt basicAuth to the router; htpasswd -nB -C 12 selects cost 12 rather than bare cost 5; the OWASP minimum is not directly sourced here. | Traefik scope v2 and v3 | REASONED |
| compose-hash: Double each dollar sign in Compose hash labels; file-provider hashes need no such escaping. | Traefik scope v2 and v3 | REASONED |
| file-provider: Load dynamic files with providers.file.directory/filename and reference their middleware from Docker as app-auth@file. | Traefik scope v2 and v3 | REASONED |
| mfa: Basic is single-factor; use forwardAuth with Authelia/oauth2-proxy or front the site with Cloudflare Access for human MFA. | Traefik scope v2 and v3 | REASONED |
| body-limit: Attach buffering.maxRequestBodyBytes=10485760 alongside existing auth/routing labels; it bounds accepted body size. | Traefik middleware documentation unknown | REASONED |
| buffer-storage: memRequestBodyBytes defaults to 1048576 and controls the memory-to-disk threshold independently of maximum accepted body size. | Traefik middleware documentation unknown | REASONED |
| rate-limit: average=10 and burst=20 configure a rate cap, per source by default. | Traefik middleware documentation unknown | REASONED |
| inflight: inflightreq.amount=10 bounds concurrent requests; sourceCriterion defaults to request host rather than client, so configure a per-client cap explicitly. | Traefik middleware documentation unknown | REASONED |
| middleware-order: Rate/inflight precede auth to count rejected logins; buffering follows admission controls to avoid buffering rejected uploads. | Traefik scope v2 and v3; Traefik middleware documentation unknown | REASONED |
| dashboard: Keep api.insecure and unprotected api@internal routers off public entry points or protect the dashboard with auth. | Traefik scope v2 and v3 | REASONED |
| swarm: Standalone Docker guidance does not cover Swarm; v3 uses providers.swarm and its separate exposedByDefault also defaults true. | Traefik Swarm provider unknown | REASONED |
| verify-redirect: HTTP should redirect to HTTPS. | Traefik scope v2 and v3 | REASONED |
| verify-auth: Unauthenticated HTTPS should return 401 once auth is attached. | Traefik scope v2 and v3 | REASONED |
| verify-size: Authenticated 1M must reach the app and 11M return 413; 401/000 invalidate the control. Remove app-body in isolation to rule out backend refusal. | Traefik middleware documentation unknown; Traefik scope v2 and v3 | REASONED |
| observed-429: The guide records only a 429 response; no limiter attribution or exposed/fixed demonstration is established. | Traefik middleware documentation unknown | DEMONSTRATED |
| verify-rate: Concurrent unauthenticated probes can reach pre-auth limiters; 429 alone cannot distinguish rate, inflight or upstream refusal. Compare each limiter alone against both disabled. | Traefik middleware documentation unknown | REASONED |
| verify-isolation: Compose ps covers one project; ss misses NAT-only publication without a userland proxy. Neither finds unintended routes through Traefik. | Traefik Docker provider unknown | REASONED |
| verify-acme: Inspect ACME startup errors; failed issuance can leave a self-signed TRAEFIK DEFAULT CERT. | Traefik scope v2 and v3 | REASONED |
| canary-route: On a disposable deployment, unlabelled traefik/whoami has one HTTP port; use its generated Host rule and plain HTTP even on :443 because the generated router requests no TLS. | Traefik Docker provider unknown; Traefik scope v2 and v3 | REASONED |
| verify-canary: Calibrate exposedByDefault true with 200 and the canary Hostname body; false should give 404. Missing discovery/provider also gives 404, unreachable backend 502/504. | Traefik Docker provider unknown; curl write-out minimum 7.75.0 | REASONED |
| verify-app-control: In the same run, the app must return 401 or known authenticated 200 while the canary gives 404; app 401 proves routing, not proxy-auth attachment. Keep TLS verification. | Traefik Docker provider unknown; Traefik scope v2 and v3; curl write-out minimum 7.75.0 | REASONED |
<!-- version-basis:end -->

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

The `providers.docker` block turns on container discovery, and `exposedByDefault: false` is the security-relevant half. Its default is `true`, so a `providers.docker` block without that line builds a router for every eligible container it discovers, not only the one you labelled. The provider reads labels over the Docker socket, so mount it into the Traefik service:

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

Labelling this container `traefik.enable=true` opts it in; it does not keep any other container private. With `exposedByDefault: false` set in section 1, Traefik ignores every container that lacks that label. Without it, discovery is daemon-wide, not scoped to this Compose project, so any other container that exposes a port Traefik can build a service from also gets a router matched by its `Host` header on the same `:443` listener. A container with no usable port is skipped, and the port Traefik picks need not serve usable HTTP; but a router you never requested is the exposure this setting shuts off. The label opts a container in; it never opts others out, so keep it on each application you mean to publish.

Do not also publish the app's port with `ports:`; only Traefik publishes 80 and 443. See [docker.md](docker.md).

## 3. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). At the proxy, attach a basicAuth middleware with bcrypt entries from `htpasswd -nB -C 12 admin` (a bare `-nB` defaults to cost 5, below the OWASP minimum of 10 that [authentication.md](authentication.md) sets):

```yaml
    labels:
      - traefik.http.middlewares.app-auth.basicauth.users=admin:$$2y$$12$$REPLACE_WITH_HASH
      - traefik.http.routers.app.middlewares=app-auth
```

In Compose files every `$` in the hash must be doubled to `$$`. The file-provider equivalent, where no escaping is needed:

```yaml
http:
  middlewares:
    app-auth:
      basicAuth:
        users:
          - "admin:$2y$12$REPLACE_WITH_HASH"
```

Load that dynamic file with `providers.file.directory` (or `providers.file.filename`) in the static config, and when a Docker-labelled router references a file-defined middleware, qualify it as `app-auth@file`. basicAuth is single-factor. For human-facing sites, add MFA with the `forwardAuth` middleware pointed at [Authelia](https://www.authelia.com/) or [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy), or front the site with Cloudflare Access; options in [mfa.md](mfa.md).

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
      - traefik.http.routers.app.middlewares=app-rate,app-inflight,app-auth,app-body
```

Order matters here. `app-rate` and `app-inflight` come before `app-auth` so they bound failed-login attempts: basicAuth short-circuits with a 401 before any middleware listed after it runs, so a limiter placed after auth never counts a rejected attempt. `buffering` reads the request into memory or disk before forwarding it, so it must
come after the admission controls; placed first, an accepted upload consumes the buffer before
`ratelimit` or `inflightreq` has considered it. `maxRequestBodyBytes` sets the largest body accepted;
`memRequestBodyBytes`, which defaults to 1048576, is the separate threshold at which buffering moves
from memory to disk. Raising the first increases what you will buffer, not where that buffer lives. `ratelimit` is per source by default, while `inflightreq` caps concurrent
in-flight requests rather than their rate, and its `sourceCriterion` defaults to the request host rather
than the client, so set it explicitly if you want a per-client cap.

## 5. Verify (REASONED: all Verify scenarios follow the cited Traefik and curl documentation; no live Docker/Traefik canary demonstration is recorded. The recorded 429 alone does not demonstrate limiter attribution. This metadata-only review has no authorized deployment fixture.)

```bash
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI http://app.example.com/     # expect a redirect to https://
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://app.example.com/    # expect 401 without credentials once auth is on
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
                                     # 413. Credentials matter: app-body runs after app-auth, so an
                                     # unauthenticated probe is counted by app-rate/app-inflight but stops
                                     # at 401 before app-body buffers it. A backend with its own limit
                                     # returns the same code, so attributing the refusal needs an isolated
                                     # environment with app-body removed
)
seq 1 40 | xargs -P 40 -I{} curl -q -s -o /dev/null -w '%{http_code}\n' https://app.example.com/ | sort | uniq -c
                                     # No credentials here: app-rate and app-inflight run BEFORE app-auth in the
                                     # middleware chain (section 4), so an unauthenticated flood is counted by the
                                     # limiter, keyed on the client source. A 429 appeared. That is all this shows.
                                     # inflightreq also returns
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

`docker compose ps` and `ss` help find a container that bypasses Traefik with its own `ports:`, though neither is exhaustive: `docker compose ps` lists only this Compose project, and a port published through NAT alone, with Docker's userland proxy disabled, opens no host listening socket for `ss` to show. Neither, in any case, sees a container Traefik routes without your asking: a routed container has no host port publication of its own. To confirm `exposedByDefault: false` actually excludes unlabelled containers, launch an unlabelled canary on Traefik's network and probe the front door. Do this on a disposable copy of the deployment; never make a container deliberately routable on the production host. These canary steps are reasoned from Traefik's documented routing behavior and the exposed-versus-fixed outcomes it predicts; they have not been demonstrated against a live Docker/Traefik deployment here.

```yaml
services:
  canary:
    image: traefik/whoami   # one HTTP port, echoes its own hostname; no traefik.* labels, no ports:
```

`traefik/whoami` listens on a single HTTP port, so Traefik's single-port detection can build a service for it and a routed reply is unmistakable (the body carries a `Hostname:` line). Read the router rule Traefik generated for the canary; its `Host(...)` value is the canary's normalized name, and you pass that value as the `Host:` header below. Probe plain HTTP against the `:443` listener: the auto-generated router never requested TLS, so it answers plain HTTP even there. Run these probe blocks with Bash and curl 7.75.0 or newer, which added the `exitcode` and `errormsg` write-out variables they print.

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

With `exposedByDefault: false` the canary returns `http=404` from Traefik's unmatched-route handler: it was ignored, and that is the pass. Calibrate first on the exposed fixture (temporarily `exposedByDefault: true`), where the canary must return `http=200` with a `Hostname:` body naming the canary itself, not some other service; that proves the probe reaches Traefik through the canary's own router. Without that positive calibration a `404` is not trustworthy: it can equally mean Traefik never discovered the canary or built no matching route. A canary Traefik did discover but cannot reach on its network answers `502` or `504`, not `404`. On production, run the probe only after applying the fix; a canary that answers `200` there is a live exposure to remove, not a passing test.

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

With the authentication from section 3 in place, this unauthenticated probe returns `http=401`: a response, rather than a connection failure or a `404`, means the provider is routing this app. The `401` may come from Traefik's basicAuth or from the app's own login, so it confirms routing, not specifically that the proxy middleware is attached; confirm that separately from the router's `middlewares` in the dashboard or config. (Feed the admin credential to that curl on stdin, as the section 5 Verify block does, to see the app's own authenticated response instead.) The fix is confirmed when, in the same run, the app answers `401` (or your known authenticated `200`) and the canary answers `404`: routing works and the unlabelled container is excluded. A `404` or a connection failure for the app instead means the provider is not routing it. No `-k` here; the app needs a real certificate.

## Common mistakes

- Enabling the Traefik dashboard (`api.insecure=true` or an unprotected `api@internal` router) on a public entry point; keep it off or behind the auth middleware.
- Forgetting to persist `acme.json`, which re-issues certificates on every restart and hits CA rate limits.
- Single `$` in Compose basicauth labels, which breaks the hash silently.
- Enabling the Docker provider but leaving `exposedByDefault` at its default of `true`, which exposes every eligible container it discovers to routing, not only the labelled one; a working HTTP route also needs a reachable HTTP backend on the detected port.
- Assuming this page covers Docker Swarm. It covers standalone Docker; Swarm is a separate provider (`providers.swarm` in Traefik v3) with its own `exposedByDefault`, which also defaults to `true`. Consult the Swarm provider reference for your version before relying on this page under Swarm.

## Sources (checked September 2026)

- Traefik documentation (v2 and v3): https://doc.traefik.io/traefik/ (HTTPS/ACME, routers, and basicAuth middleware sections)
- Docker provider (`exposedByDefault`, socket endpoint): https://doc.traefik.io/traefik/reference/install-configuration/providers/docker/
- Swarm provider (`providers.swarm.exposedByDefault`): https://doc.traefik.io/traefik/reference/install-configuration/providers/swarm/
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- Buffering middleware (`maxRequestBodyBytes`, `memRequestBodyBytes`): https://doc.traefik.io/traefik/middlewares/http/buffering/
- InFlightReq middleware (`amount`): https://doc.traefik.io/traefik/middlewares/http/inflightreq/
- RateLimit middleware (`average`, `burst`, `period`): https://doc.traefik.io/traefik/middlewares/http/ratelimit/
