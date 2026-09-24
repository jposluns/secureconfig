# Fronting auth: putting login and MFA in front of an app that has none (oauth2-proxy, Authelia, Pomerium)

Many self-hosted apps (internal tools, dashboards, webhook receivers) ship with no login at all. The fix is the same shape every time: the app binds to loopback, a proxy in front does authentication and MFA, and it passes the app a verified identity, which the app must not accept from anywhere else. This guide is what [mfa.md](mfa.md), [nginx.md](nginx.md), [traefik.md](traefik.md), and [caddy.md](caddy.md) point at.

## 1. The pattern

1. **Bind the app to loopback**, `127.0.0.1`, never `0.0.0.0` or `::`. Bind the auth service so only the fronting proxy reaches it too: loopback when it shares the host, or a private container network with no published port when it does not (oauth2-proxy's `--http-address` defaults to `127.0.0.1:4180` as of v7.15.4; Authelia's `server.address` defaults to `tcp://:9091/` as of v4.39.28, an empty host that it passes to Go's `net.Listen`, which then listens on every local address, so restrict it), never a public interface. If the app also answers directly, the login page in front of it is decorative.
2. **A proxy authenticates first**: oauth2-proxy, Authelia, or Pomerium checks the session before the request reaches the app; an unauthenticated request never gets there.
3. **The proxy passes identity in a header and the app reads that header** instead of running its own login. The header must be one the proxy sets on every request from its own verified response, so the proxy overwrites any value a client sent: nginx `X-User`/`X-Email` in the example below, oauth2-proxy's `X-Auth-Request-User` carried through Traefik, Authelia's `Remote-User`. The app must never read a header the proxy does not set, because nginx and Traefik forward the client's other headers unchanged.
4. **The app must trust only the exact header the proxy sets, and reject any other.** Network isolation, only the proxy can reach the app, stops a direct client from setting the header; but a client can also send a header *through* the proxy, and the proxy overwrites only the one header it sets while forwarding the rest, so the app must read that one header and no other. The managed-cloud version of this same bypass risk is in [cloud-identity-proxies.md](cloud-identity-proxies.md).

## 2. oauth2-proxy: auth in front of an OIDC/OAuth2 provider

Core flags (env vars use the `OAUTH2_PROXY_` prefix): `--provider` (`oidc`, `google`, `github`, and others), `--client-id`/`--client-secret` from the IdP, `--email-domain` (a domain, or `*` for any authenticated user), `--upstream` (the app address, or `static://202` when a forward-auth proxy handles the actual proxying), and `--cookie-secret`, which must be exactly 16, 24, or 32 bytes, optionally base64-encoded: `openssl rand -base64 32 | tr -- '+/' '-_'`.

nginx uses `auth_request`, which requires oauth2-proxy's `--reverse-proxy` flag; forwarding the identity headers below also requires `--set-xauthrequest` (it makes oauth2-proxy set `X-Auth-Request-User` and `X-Auth-Request-Email` on its own `/oauth2/auth` response, which the `auth_request_set` lines then read):

```nginx
location /oauth2/ {
    proxy_pass       http://127.0.0.1:4180;
    proxy_set_header Host                    $host;
    proxy_set_header X-Real-IP               $remote_addr;
    proxy_set_header X-Auth-Request-Redirect $request_uri;
}
location = /oauth2/auth {
    proxy_pass       http://127.0.0.1:4180;
    proxy_set_header Host             $host;
    proxy_set_header X-Real-IP        $remote_addr;
    proxy_set_header X-Forwarded-Uri  $request_uri;
    proxy_set_header Content-Length   "";
    proxy_pass_request_body           off;
}
location / {
    auth_request /oauth2/auth;
    error_page 401 = @oauth2_signin;
    auth_request_set $user  $upstream_http_x_auth_request_user;
    auth_request_set $email $upstream_http_x_auth_request_email;
    proxy_set_header X-User  $user;
    proxy_set_header X-Email $email;
    proxy_pass http://127.0.0.1:3000;
}
location @oauth2_signin {
    return 302 /oauth2/sign_in?rd=$scheme://$host$request_uri;
}
```

Traefik uses a `forwardAuth` middleware at oauth2-proxy's `/oauth2/auth`, with `--upstream=static://202`, `--reverse-proxy=true`, and `--set-xauthrequest` (so oauth2-proxy sets `X-Auth-Request-User`/`X-Auth-Request-Email` on its `/oauth2/auth` response) set on oauth2-proxy. `authResponseHeaders` must list every identity header the app trusts, because Traefik copies only those from the auth response onto the request (replacing any the client sent) and forwards the client's other headers untouched:

```yaml
http:
  middlewares:
    oauth-auth:
      forwardAuth:
        address: "http://oauth2-proxy:4180/oauth2/auth"
        trustForwardHeader: true
        authResponseHeaders: [X-Auth-Request-User, X-Auth-Request-Email, X-Auth-Request-Access-Token, Authorization]
```

Attach the middleware to every router that serves the protected app: Traefik applies a middleware only where a router references it, so add `middlewares: [oauth-auth]` on the router in the file provider, or the label `traefik.http.routers.<app>.middlewares=oauth-auth@file`. A middleware that is defined but never referenced protects nothing.

## 3. Authelia: a portal that does the second factor

Authelia is a login portal with built-in TOTP and WebAuthn, sitting behind the proxy rather than replacing it. Per its support page, nginx, Traefik, Caddy (2.5.1+), HAProxy (via a Lua module), Envoy, Skipper, NGINX Proxy Manager, and SWAG are supported; Apache and IIS are documented as having no compatible module and are not supported.

nginx calls a dedicated `auth-request` endpoint (its `auth_request` module cannot forward the method and body the way the others' forward-auth middlewares do). That endpoint must be defined; Authelia's own snippets (`authelia-location.conf` and `authelia-authrequest.conf`) show it as:

```nginx
resolver 127.0.0.11 valid=30s;
set $upstream_authelia http://authelia:9091/api/authz/auth-request;
location /internal/authelia/authz {
    internal;
    proxy_pass $upstream_authelia;
    proxy_set_header X-Original-Method $request_method;
    proxy_set_header X-Original-URL $scheme://$host$request_uri;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header Content-Length "";
    proxy_set_header Connection "";
    proxy_pass_request_body off;
}

# in the protected location block:
auth_request /internal/authelia/authz;
auth_request_set $user   $upstream_http_remote_user;
auth_request_set $groups $upstream_http_remote_groups;
auth_request_set $name   $upstream_http_remote_name;
auth_request_set $email  $upstream_http_remote_email;
proxy_set_header Remote-User   $user;
proxy_set_header Remote-Groups $groups;
proxy_set_header Remote-Name   $name;
proxy_set_header Remote-Email  $email;
auth_request_set $redirection_url $upstream_http_location;
error_page 401 =302 $redirection_url;
```

nginx needs a way to resolve the `authelia` hostname at request time since `proxy_pass` here targets
a variable rather than a static address, so the `resolver` line above (or a matching `upstream`
block) is required; Authelia's nginx integration assumes a Docker DNS resolver is available for
this, per Authelia's nginx integration guide. The `auth_request_set`/`proxy_set_header Remote-*` pairs set the app's identity headers from Authelia's response and, because nginx forwards client request headers to the upstream by default, overwrite any `Remote-User` a caller tried to send directly; without them, and without the network isolation from section 1, a client that reached the app could assert `Remote-User: admin` itself. The Traefik and Caddy examples below carry the same identity headers through `authResponseHeaders` and `copy_headers`.

Traefik and Caddy call `/api/authz/forward-auth` instead:

```yaml
- traefik.http.middlewares.authelia.forwardauth.address=http://authelia:9091/api/authz/forward-auth
- traefik.http.middlewares.authelia.forwardauth.authResponseHeaders=Remote-User,Remote-Groups,Remote-Email,Remote-Name
```

```caddyfile
forward_auth authelia:9091 {
    uri /api/authz/forward-auth
    copy_headers Remote-User Remote-Groups Remote-Email Remote-Name
}
```

Authelia needs its own random session secret and access-control rules (which paths need `one_factor` vs `two_factor`); its second factor is TOTP, WebAuthn/passkeys, or Duo mobile push.

## 4. Pomerium: the proxy is the access layer

Pomerium is an identity-aware proxy rather than a sidecar to nginx: it terminates the connection, authenticates the user, and enforces policy in one process. An IdP goes under `idp_provider`, `idp_provider_url`, `idp_client_id`, and `idp_client_secret`; each app is a route carrying its own `policy` (which users, domains, or claims may reach it), rather than a shared middleware bolted onto an existing proxy. Choose Pomerium over the two above when you want routing, TLS, and access control in one process instead of an auth check layered in front of nginx, Traefik, or Caddy.

## 5. MFA and identity source

oauth2-proxy's MFA is whatever its OIDC/OAuth provider enforces; Pomerium's is whatever its `idp_provider` enforces; only Authelia enforces a second factor itself. See [mfa.md](mfa.md) (enrolment is not enforcement) and [identity-providers.md](identity-providers.md) for which hosted providers' tiers include MFA.

## Verify

```bash
ss -tlnp   # read every listener; app 3000, oauth2-proxy 4180, Authelia 9091 reachable only by the proxy (loopback, or a private container network), never a public interface
# each must be unreachable from another host. Read err, not the number: it must name a refusal or timeout reaching
# YOUR address. An HTTP code means the app answered. A resolver failure, a local socket error, or a
# timeout that did not come from the remote address is inconclusive, never a pass.
(                                             # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) for p in 3000 4180 9091; do   # app, oauth2-proxy, Authelia: each must be unreachable from another host
         curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
           -w "port=$p http=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "http://$1:$p/"
       done
       curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         -H 'X-User: admin' "http://$1:3000/" ;;   # forged header the nginx app trusts, straight at the app
  esac
)
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://app.example.com/             # no session: a 401, or a 302 whose Location is the sign-in page (/oauth2/sign_in or the portal); any other 302 is not a pass
```

After a real login through the proxy, confirm a session reaches the app and the app-side log shows the identity header the proxy set, not the forged one above. The direct forged header on the probe above is refused at the network level, because the app is reachable only through the proxy. A header sent *through* the proxy is the separate risk: it is defeated only because the proxy overwrites the exact header the app trusts (nginx `X-User`/`X-Email`, the Traefik `authResponseHeaders`, Authelia's `Remote-*`) with its verified value. Confirm that overwrite: with a valid session, replay a request through the proxy that adds the trusted header (`-H 'X-User: admin'` for the nginx example, `-H 'X-Auth-Request-User: admin'` for the Traefik example, `-H 'Remote-User: admin'` for Authelia) and check the app-side log still shows your real identity, not `admin`. If it shows `admin`, the proxy is not overwriting that header and any authenticated user can impersonate anyone.

## Common mistakes

- The app also listens on a public interface next to the proxy, so a direct request skips authentication entirely.
- The app trusts `X-Auth-Request-User` or `Remote-User` from any caller, not only from the proxy.
- oauth2-proxy's `--cookie-secret` reused across environments or committed to the repository.
- Deploying Authelia behind Apache or IIS, which it does not support.

## Sources (checked September 2026)

- oauth2-proxy configuration overview (flags, cookie-secret length): https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview
- oauth2-proxy nginx integration: https://oauth2-proxy.github.io/oauth2-proxy/configuration/integrations/nginx/
- oauth2-proxy Traefik integration: https://oauth2-proxy.github.io/oauth2-proxy/configuration/integrations/traefik/
- Traefik forwardAuth middleware (authResponseHeaders replaces only the listed headers; others pass through): https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth/
- Authelia proxy integration introduction: https://www.authelia.com/integration/proxies/introduction/
- Authelia proxy support matrix (Apache and IIS unsupported): https://www.authelia.com/integration/proxies/support/
- Authelia nginx integration: https://www.authelia.com/integration/proxies/nginx/
- Authelia Traefik integration: https://www.authelia.com/integration/proxies/traefik/
- Authelia Caddy integration: https://www.authelia.com/integration/proxies/caddy/
- Authelia second-factor introduction: https://www.authelia.com/configuration/second-factor/introduction/
- Pomerium identity provider settings: https://www.pomerium.com/docs/reference/identity-provider-settings
- Pomerium documentation: https://www.pomerium.com/docs
- oauth2-proxy `--http-address` default `127.0.0.1:4180` (pinned tag v7.15.4): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/pkg/apis/options/legacy_options.go#L494
- Authelia `server.address` default `tcp://:9091/` (pinned tag v4.39.28): https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/server.go#L90-L92
- Authelia listens with `net.Listen(a.Network(), a.NetworkAddress())` (`types_addresses_nix.go` L37), where `NetworkAddress()` returns the URL's host and port, `:9091` for the default (`types_address.go` L480) (pinned tag v4.39.28): https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/types_addresses_nix.go#L37
- Go `net.Listen` with an empty host listens on all available unicast and anycast addresses of the local system: https://pkg.go.dev/net#Listen
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
