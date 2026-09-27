---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "8f982007c825bfe550710fa6931ad65e909cb45a316c22769329974aa96c47bf",
  "components": {
    "oauth": {
      "name": "oauth2-proxy",
      "basis": "v7.15.4",
      "sources": {
        "sb098baafd79a": "https://raw.githubusercontent.com/oauth2-proxy/oauth2-proxy/v7.15.4/docs/docs/configuration/overview.md",
        "s00027714276b": "https://raw.githubusercontent.com/oauth2-proxy/oauth2-proxy/v7.15.4/docs/docs/configuration/integrations/traefik.md",
        "sa987fae1c9ef": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/pkg/apis/options/legacy_options.go#L494"
      }
    },
    "authelia": {
      "name": "Authelia",
      "basis": "v4.39.28",
      "sources": {
        "s064d1e72c1e8": "https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/server.go#L90-L92",
        "sbec86d37ea1c": "https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/types_addresses_nix.go#L37"
      }
    },
    "traefik": {
      "name": "Traefik",
      "basis": "unknown",
      "sources": {
        "s7f6f6200de1f": "https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth/"
      }
    },
    "go": {
      "name": "Go net.Listen",
      "basis": "unknown",
      "sources": {
        "s37204ff1b27c": "https://pkg.go.dev/net#Listen"
      }
    },
    "pomerium": {
      "name": "Pomerium",
      "basis": "unknown",
      "sources": {
        "s181907d16ed1": "https://www.pomerium.com/docs/reference/identity-provider-settings",
        "s4ed306cb118e": "https://www.pomerium.com/docs"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "oauth-rolling": {
      "name": "oauth2-proxy documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sdcd74a9cd9c6": "https://oauth2-proxy.github.io/oauth2-proxy/configuration/integrations/nginx/"
      }
    },
    "authelia-rolling": {
      "name": "Authelia documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s0cb4f49871b5": "https://www.authelia.com/integration/proxies/introduction/",
        "s1409ac8fe3d9": "https://www.authelia.com/integration/proxies/support/",
        "s4af41b2fed9f": "https://www.authelia.com/integration/proxies/nginx/",
        "sfb8ce161d56a": "https://www.authelia.com/integration/proxies/traefik/",
        "sd5437cbc4328": "https://www.authelia.com/integration/proxies/caddy/",
        "scd46ff77c737": "https://www.authelia.com/configuration/second-factor/introduction/"
      }
    }
  },
  "claims": {
    "isolate": {"text": "Bind app and auth service to loopback or an unpublished private container network; only the fronting proxy may reach them.", "components": ["oauth", "oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "oauth:s00027714276b", "authelia-rolling:s0cb4f49871b5"], "status": "REASONED"},
    "oauth-bind": {"text": "oauth2-proxy --http-address defaults to 127.0.0.1:4180.", "components": ["oauth"], "sources": ["oauth:sa987fae1c9ef"], "status": "REASONED"},
    "authelia-bind": {"text": "Authelia server.address defaults tcp://:9091/; its empty host reaches Go net.Listen and binds every local address.", "components": ["authelia", "go"], "sources": ["authelia:s064d1e72c1e8", "authelia:sbec86d37ea1c", "go:s37204ff1b27c"], "status": "REASONED"},
    "authenticate": {"text": "oauth2-proxy, Authelia or Pomerium must check the session before forwarding to the app.", "components": ["pomerium", "oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "authelia-rolling:s0cb4f49871b5", "pomerium:s4ed306cb118e"], "status": "REASONED"},
    "header-trust": {"text": "The app must trust only headers overwritten from verified proxy responses; other client headers pass through, so isolation alone is insufficient.", "components": ["oauth", "traefik", "oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "oauth:s00027714276b", "authelia-rolling:s4af41b2fed9f", "traefik:s7f6f6200de1f"], "status": "REASONED"},
    "oauth-provider": {"text": "OAUTH2_PROXY_ environment variables map core flags; configure provider and IdP client-id/client-secret.", "components": ["oauth"], "sources": ["oauth:sb098baafd79a"], "status": "REASONED"},
    "oauth-domain": {"text": "--email-domain restricts a domain; * admits any authenticated user.", "components": ["oauth"], "sources": ["oauth:sb098baafd79a"], "status": "REASONED"},
    "oauth-upstream": {"text": "--upstream targets the app, or static://202 when another proxy handles forwarding.", "components": ["oauth"], "sources": ["oauth:sb098baafd79a", "oauth:s00027714276b"], "status": "REASONED"},
    "oauth-cookie": {"text": "--cookie-secret must be 16, 24 or 32 bytes, optionally base64-encoded; generate randomly and do not reuse or commit it.", "components": ["oauth"], "sources": ["oauth:sb098baafd79a"], "status": "REASONED"},
    "oauth-nginx": {"text": "nginx auth_request at /oauth2/auth needs --reverse-proxy; --set-xauthrequest supplies User/Email response headers.", "components": ["oauth-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6"], "status": "REASONED"},
    "oauth-nginx-identity": {"text": "nginx maps verified X-Auth-Request-User/Email to X-User/Email before forwarding to 127.0.0.1:3000.", "components": ["oauth-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6"], "status": "REASONED"},
    "oauth-signin": {"text": "The nginx example forwards /oauth2/ to 127.0.0.1:4180 and redirects auth 401 to /oauth2/sign_in with the return URL.", "components": ["oauth-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6"], "status": "REASONED"},
    "oauth-traefik": {"text": "Traefik forwardAuth calls oauth2-proxy:4180/oauth2/auth with static://202, reverse-proxy and set-xauthrequest enabled.", "components": ["oauth"], "sources": ["oauth:s00027714276b"], "status": "REASONED"},
    "traefik-headers": {"text": "authResponseHeaders must include every trusted identity header; only those replace client values, with other headers forwarded unchanged.", "components": ["traefik", "oauth"], "sources": ["traefik:s7f6f6200de1f", "oauth:s00027714276b"], "status": "REASONED"},
    "traefik-attach": {"text": "Attach oauth-auth to every protected router; defining middleware without a router reference protects nothing.", "components": ["oauth", "traefik"], "sources": ["oauth:s00027714276b", "traefik:s7f6f6200de1f"], "status": "REASONED"},
    "authelia-support": {"text": "Authelia supports the listed nginx, Traefik, Caddy, HAProxy/Lua, Envoy, Skipper, NGINX Proxy Manager and SWAG integrations, not Apache/IIS.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s1409ac8fe3d9"], "status": "REASONED"},
    "caddy-min": {"text": "Authelia's documented Caddy support requires 2.5.1+.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s1409ac8fe3d9"], "status": "REASONED"},
    "authelia-nginx": {"text": "nginx uses the dedicated /api/authz/auth-request endpoint through an internal location with original method/URL and no request body.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s4af41b2fed9f"], "status": "REASONED"},
    "authelia-dns": {"text": "Variable proxy_pass needs runtime DNS resolution or a matching upstream; the shown 127.0.0.11 resolver assumes Docker DNS.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s4af41b2fed9f"], "status": "REASONED"},
    "authelia-identity": {"text": "nginx copies verified Remote-User/Groups/Name/Email and uses the auth Location for 401 redirection; trusted client headers must be overwritten.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s4af41b2fed9f"], "status": "REASONED"},
    "authelia-traefik": {"text": "Traefik calls authelia:9091/api/authz/forward-auth and copies the four Remote-* identity headers.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:sfb8ce161d56a"], "status": "REASONED"},
    "authelia-caddy": {"text": "Caddy forward_auth calls authelia:9091 with /api/authz/forward-auth and copies the four Remote-* identity headers.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:sd5437cbc4328"], "status": "REASONED"},
    "authelia-session": {"text": "Authelia needs a random session secret and path access rules selecting one_factor or two_factor.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:s0cb4f49871b5", "authelia-rolling:s4af41b2fed9f"], "status": "REASONED"},
    "authelia-mfa": {"text": "Authelia enforces TOTP, WebAuthn/passkeys or Duo push itself.", "components": ["authelia-rolling"], "sources": ["authelia-rolling:scd46ff77c737"], "status": "REASONED"},
    "pomerium-idp": {"text": "Pomerium combines routing, TLS and access control; configure idp_provider, idp_provider_url, idp_client_id and idp_client_secret.", "components": ["pomerium"], "sources": ["pomerium:s181907d16ed1", "pomerium:s4ed306cb118e"], "status": "REASONED"},
    "pomerium-policy": {"text": "Each Pomerium route carries policy restricting users, domains or claims.", "components": ["pomerium"], "sources": ["pomerium:s4ed306cb118e"], "status": "REASONED"},
    "idp-mfa": {"text": "oauth2-proxy and Pomerium rely on MFA enforced by their identity provider.", "components": ["oauth", "pomerium"], "sources": ["oauth:sb098baafd79a", "pomerium:s181907d16ed1"], "status": "REASONED"},
    "verify-listeners": {"text": "Inspect every listener: app 3000, oauth2-proxy 4180 and Authelia 9091 must be reachable only by the proxy.", "components": ["oauth", "authelia"], "sources": ["oauth:sa987fae1c9ef", "authelia:s064d1e72c1e8", "authelia:sbec86d37ea1c"], "status": "REASONED", "verify": [1]},
    "verify-direct": {"text": "From another host, all three ports must refuse/time out at the actual address; HTTP proves exposure and local/resolver failures are inconclusive.", "components": ["curl", "oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "authelia-rolling:s0cb4f49871b5", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-forged-direct": {"text": "A forged X-User sent directly to app port 3000 must be refused by network isolation.", "components": ["curl", "oauth-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-login": {"text": "Without a session, expect 401 or a 302 to the sign-in page; other redirects do not pass. A real session must reach the app.", "components": ["oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "authelia-rolling:s4af41b2fed9f"], "status": "REASONED", "verify": [1]},
    "verify-overwrite": {"text": "With a valid session, replay a forged trusted identity header through each proxy; the app log must show the real identity, not admin.", "components": ["oauth", "traefik", "oauth-rolling", "authelia-rolling"], "sources": ["oauth-rolling:sdcd74a9cd9c6", "oauth:s00027714276b", "authelia-rolling:s4af41b2fed9f", "authelia-rolling:sfb8ce161d56a", "authelia-rolling:sd5437cbc4328", "traefik:s7f6f6200de1f"], "status": "REASONED"}
  }
}
---
# Fronting auth: putting login and MFA in front of an app that has none (oauth2-proxy, Authelia, Pomerium)

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| isolate: Bind app and auth service to loopback or an unpublished private container network; only the fronting proxy may reach them. | oauth2-proxy v7.15.4; oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
| oauth-bind: oauth2-proxy --http-address defaults to 127.0.0.1:4180. | oauth2-proxy v7.15.4 | REASONED |
| authelia-bind: Authelia server.address defaults tcp://:9091/; its empty host reaches Go net.Listen and binds every local address. | Authelia v4.39.28; Go net.Listen unknown | REASONED |
| authenticate: oauth2-proxy, Authelia or Pomerium must check the session before forwarding to the app. | Pomerium unknown; oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
| header-trust: The app must trust only headers overwritten from verified proxy responses; other client headers pass through, so isolation alone is insufficient. | oauth2-proxy v7.15.4; Traefik unknown; oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
| oauth-provider: OAUTH2_PROXY_ environment variables map core flags; configure provider and IdP client-id/client-secret. | oauth2-proxy v7.15.4 | REASONED |
| oauth-domain: --email-domain restricts a domain; * admits any authenticated user. | oauth2-proxy v7.15.4 | REASONED |
| oauth-upstream: --upstream targets the app, or static://202 when another proxy handles forwarding. | oauth2-proxy v7.15.4 | REASONED |
| oauth-cookie: --cookie-secret must be 16, 24 or 32 bytes, optionally base64-encoded; generate randomly and do not reuse or commit it. | oauth2-proxy v7.15.4 | REASONED |
| oauth-nginx: nginx auth_request at /oauth2/auth needs --reverse-proxy; --set-xauthrequest supplies User/Email response headers. | oauth2-proxy documentation (rolling) unknown | REASONED |
| oauth-nginx-identity: nginx maps verified X-Auth-Request-User/Email to X-User/Email before forwarding to 127.0.0.1:3000. | oauth2-proxy documentation (rolling) unknown | REASONED |
| oauth-signin: The nginx example forwards /oauth2/ to 127.0.0.1:4180 and redirects auth 401 to /oauth2/sign_in with the return URL. | oauth2-proxy documentation (rolling) unknown | REASONED |
| oauth-traefik: Traefik forwardAuth calls oauth2-proxy:4180/oauth2/auth with static://202, reverse-proxy and set-xauthrequest enabled. | oauth2-proxy v7.15.4 | REASONED |
| traefik-headers: authResponseHeaders must include every trusted identity header; only those replace client values, with other headers forwarded unchanged. | Traefik unknown; oauth2-proxy v7.15.4 | REASONED |
| traefik-attach: Attach oauth-auth to every protected router; defining middleware without a router reference protects nothing. | oauth2-proxy v7.15.4; Traefik unknown | REASONED |
| authelia-support: Authelia supports the listed nginx, Traefik, Caddy, HAProxy/Lua, Envoy, Skipper, NGINX Proxy Manager and SWAG integrations, not Apache/IIS. | Authelia documentation (rolling) unknown | REASONED |
| caddy-min: Authelia's documented Caddy support requires 2.5.1+. | Authelia documentation (rolling) unknown | REASONED |
| authelia-nginx: nginx uses the dedicated /api/authz/auth-request endpoint through an internal location with original method/URL and no request body. | Authelia documentation (rolling) unknown | REASONED |
| authelia-dns: Variable proxy_pass needs runtime DNS resolution or a matching upstream; the shown 127.0.0.11 resolver assumes Docker DNS. | Authelia documentation (rolling) unknown | REASONED |
| authelia-identity: nginx copies verified Remote-User/Groups/Name/Email and uses the auth Location for 401 redirection; trusted client headers must be overwritten. | Authelia documentation (rolling) unknown | REASONED |
| authelia-traefik: Traefik calls authelia:9091/api/authz/forward-auth and copies the four Remote-* identity headers. | Authelia documentation (rolling) unknown | REASONED |
| authelia-caddy: Caddy forward_auth calls authelia:9091 with /api/authz/forward-auth and copies the four Remote-* identity headers. | Authelia documentation (rolling) unknown | REASONED |
| authelia-session: Authelia needs a random session secret and path access rules selecting one_factor or two_factor. | Authelia documentation (rolling) unknown | REASONED |
| authelia-mfa: Authelia enforces TOTP, WebAuthn/passkeys or Duo push itself. | Authelia documentation (rolling) unknown | REASONED |
| pomerium-idp: Pomerium combines routing, TLS and access control; configure idp_provider, idp_provider_url, idp_client_id and idp_client_secret. | Pomerium unknown | REASONED |
| pomerium-policy: Each Pomerium route carries policy restricting users, domains or claims. | Pomerium unknown | REASONED |
| idp-mfa: oauth2-proxy and Pomerium rely on MFA enforced by their identity provider. | oauth2-proxy v7.15.4; Pomerium unknown | REASONED |
| verify-listeners: Inspect every listener: app 3000, oauth2-proxy 4180 and Authelia 9091 must be reachable only by the proxy. | oauth2-proxy v7.15.4; Authelia v4.39.28 | REASONED |
| verify-direct: From another host, all three ports must refuse/time out at the actual address; HTTP proves exposure and local/resolver failures are inconclusive. | curl minimum write-out version 7.75.0; oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
| verify-forged-direct: A forged X-User sent directly to app port 3000 must be refused by network isolation. | curl minimum write-out version 7.75.0; oauth2-proxy documentation (rolling) unknown | REASONED |
| verify-login: Without a session, expect 401 or a 302 to the sign-in page; other redirects do not pass. A real session must reach the app. | oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
| verify-overwrite: With a valid session, replay a forged trusted identity header through each proxy; the app log must show the real identity, not admin. | oauth2-proxy v7.15.4; Traefik unknown; oauth2-proxy documentation (rolling) unknown; Authelia documentation (rolling) unknown | REASONED |
<!-- version-basis:end -->

Many self-hosted apps (internal tools, dashboards, webhook receivers) ship with no login at all. The fix is the same shape every time: the app binds to loopback, a proxy in front does authentication and MFA, and it passes the app a verified identity, which the app must not accept from anywhere else. This guide is what [mfa.md](mfa.md), [nginx.md](nginx.md), [traefik.md](traefik.md), and [caddy.md](caddy.md) point at.

## 1. The pattern

1. **Bind the app to loopback**, `127.0.0.1`, never `0.0.0.0` or `::`. Bind the auth service so only the fronting proxy reaches it too: loopback when it shares the host, or a private container network with no published port when it does not (oauth2-proxy's `--http-address` defaults to `127.0.0.1:4180` as of v7.15.4; Authelia's `server.address` defaults to `tcp://:9091/` as of v4.39.28, whose host-and-port, `:9091` with an empty host, Authelia passes to Go's `net.Listen`, which then listens on every local address, so restrict it), never a public interface. If the app also answers directly, the login page in front of it is decorative.
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

REASONED: following block; the cited oauth2-proxy/Authelia integrations, pinned listener defaults and curl manual define isolation, direct-header refusal and anonymous challenges. This read-only review cannot provision the proxy, backend, IdP and external probe host; no live outcome is recorded. Expected responses and inconclusive failures are stated below.

```bash
ss -tlnp   # read every listener; app 3000, oauth2-proxy 4180, Authelia 9091 reachable only by the proxy (loopback, or a private container network), never a public interface
# each must be unreachable from another host. Read err, not the number: it must name a refusal or timeout reaching
# YOUR address. An HTTP code means the app answered. A resolver failure, a local socket error, or a
# timeout that did not come from the remote address is inconclusive, never a pass.
(                                             # a subshell, so your own script arguments are untouched
  set +e   # expected refusals must not skip later probes under an inherited set -e
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

- oauth2-proxy configuration overview, flags and cookie-secret length (pinned tag v7.15.4): https://raw.githubusercontent.com/oauth2-proxy/oauth2-proxy/v7.15.4/docs/docs/configuration/overview.md
- oauth2-proxy nginx integration (rolling documentation, checked September 2026): https://oauth2-proxy.github.io/oauth2-proxy/configuration/integrations/nginx/
- oauth2-proxy Traefik integration (pinned tag v7.15.4): https://raw.githubusercontent.com/oauth2-proxy/oauth2-proxy/v7.15.4/docs/docs/configuration/integrations/traefik.md
- Traefik forwardAuth middleware (authResponseHeaders replaces only the listed headers; others pass through): https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth/
- Authelia proxy integration introduction (rolling documentation, checked September 2026): https://www.authelia.com/integration/proxies/introduction/
- Authelia proxy support matrix, Apache and IIS unsupported; Caddy support minimum (rolling documentation, checked September 2026): https://www.authelia.com/integration/proxies/support/
- Authelia nginx integration (rolling documentation, checked September 2026): https://www.authelia.com/integration/proxies/nginx/
- Authelia Traefik integration (rolling documentation, checked September 2026): https://www.authelia.com/integration/proxies/traefik/
- Authelia Caddy integration (rolling documentation, checked September 2026): https://www.authelia.com/integration/proxies/caddy/
- Authelia second-factor introduction (rolling documentation, checked September 2026): https://www.authelia.com/configuration/second-factor/introduction/
- Pomerium identity provider settings: https://www.pomerium.com/docs/reference/identity-provider-settings
- Pomerium documentation: https://www.pomerium.com/docs
- oauth2-proxy `--http-address` default `127.0.0.1:4180` (pinned tag v7.15.4): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/pkg/apis/options/legacy_options.go#L494
- Authelia `server.address` default `tcp://:9091/` (pinned tag v4.39.28): https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/server.go#L90-L92
- Authelia listens with `net.Listen(a.Network(), a.NetworkAddress())` (`types_addresses_nix.go` L37), where `NetworkAddress()` returns the URL's host and port, `:9091` for the default (`types_address.go` L480) (pinned tag v4.39.28): https://github.com/authelia/authelia/blob/v4.39.28/internal/configuration/schema/types_addresses_nix.go#L37
- Go `net.Listen` with an empty host listens on all available unicast and anycast addresses of the local system: https://pkg.go.dev/net#Listen
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
