# Self-hosted identity providers: Keycloak and authentik

Keycloak and authentik are self-hosted identity providers that give your apps single sign-on and MFA. This guide helps your AI assistant deploy them securely, including a private bind behind a reverse proxy, a restricted admin surface, authentik's first-run setup finished privately, Keycloak's temporary bootstrap admin replaced, and enforced administrator MFA.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/self-hosted-idp.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Keycloak Admin CLI 26.8.2, Keycloak source 26.8.2, Keycloak release records 26.8.2, authentik source version/2026.8.5, authentik Redis removal 2025.10, and curl documentation curl-8_23_0; 1 further source is pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-11-05; documentation checked September 2026. The guide records 78 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

This guide assesses that a compromised or unavailable self-hosted identity provider takes its dependent services with it. [identity-providers.md](identity-providers.md) covers choosing one; this guide requires patching, tested backups and keeping the provider available (this guide's requirement; the cited files do not prescribe a cadence). At the time of writing, authentik's pinned security policy lists 2026.5.x and 2026.8.x as supported. Whether authentik version/2026.8.4 or version/2026.8.5 fixes security issues is not established here. Keycloak 26.8.2's security policy says that, depending on severity, vulnerabilities may be fixed in the current major.minor release, or lower-severity vulnerabilities or hardening in the following major.minor release; it encourages those unable to upgrade regularly to consider the Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak 26.8.1 fixes vulnerabilities that bear on this guide's MFA advice, so run 26.8.1 or later; section 6 quotes them. Keycloak cautions that realm export alone has backup limitations: consistency is not guaranteed unless all nodes are stopped before the export, and user and admin events, persisted sessions, workflow state and revoked tokens are omitted. The fetched files do not establish a complete backup procedure for either provider, an authentik upgrade procedure, a universal maintenance cadence or a tested restore. This guide covers what the provider exposes once it is running: an administration surface that does not move when you tell it to, a first-boot window in which an unauthenticated visitor can claim the administrator account, and a management port that, once you turn it on, answers without asking who you are.

## 1. Bind privately and front it

Neither product should answer the internet on the port it listens on. Put it behind the reverse proxy you already run ([nginx.md](nginx.md), [caddy.md](caddy.md), [traefik.md](traefik.md)) and bind the service itself to loopback or a private address ([host.md](host.md)).

At authentik tag `version/2026.8.5` (commit `4ec0d19b98da3c329781894cd550da95d3033954`), the shipped Compose server publishes `${COMPOSE_PORT_HTTP:-9000}:9000` and `${COMPOSE_PORT_HTTPS:-9443}:9443`. With those variables unset, both mappings omit a host address and publish on all host interfaces under Docker's default publishing configuration. These are the file's only host publications; it does not publish metrics port 9300. Inside the container, `listen.http` defaults to `[::]:9000` and `listen.https` to `[::]:9443`, wildcard listeners rather than loopback. Host publication and the container's listen address are separate controls. See the pinned Compose and listener-default sources below.

```yaml
# compose.yaml: REPLACE the existing ports list, do not add to it. Compose merges ports by
# address, target, published port and protocol, so a new mapping leaves an old one in place.
# With default variables and Docker publishing defaults, BOTH ports reach every interface.
services:
  server:
    ports:
      - "127.0.0.1:9000:9000"
      - "127.0.0.1:9443:9443"
```

Keycloak in production requires a secure channel. Its production guide states that "all communication to and from Keycloak requires a secure communication channel", and "To prevent several attack vectors, you enable HTTP over TLS, or HTTPS, for that channel." Terminating TLS at the proxy is edge termination, not end-to-end encryption, and it is only acceptable where the hop from proxy to Keycloak cannot be observed: a loopback interface, or a private network segment you control ([free-certificates.md](free-certificates.md) for the public certificate, [host.md](host.md) for the host itself). Both products also keep everything they know in a database, which is inside this boundary and not outside it ([postgresql.md](postgresql.md)).

## 2. Tell Keycloak its hostname, in production mode

Keycloak runs in one of two profiles and they do not have the same defaults. The hostname guide states that "In production profile (`kc.sh|bat start`), either `--hostname` or `--hostname-strict false` must be explicitly configured", and that "This does not apply for dev profile (`kc.sh|bat start-dev`) where `--hostname-strict false` is the default value."

`hostname-strict` is what stops Keycloak building URLs out of whatever `Host` header a request carries. The vendor's own description: "Disables dynamically resolving the hostname from request headers. Should always be set to true in production, unless your reverse proxy overwrites the Host header."

```bash
kc.sh start \
  --hostname https://id.example.com \
  --hostname-admin https://id-admin.internal:8443 \
  --proxy-headers xforwarded \
  --http-enabled=true          # 8080 exists only when you ask for it. Only do this where
                               # the hop from the proxy is loopback or a private segment
```

At Keycloak `26.8.2`, `--http-host` defaults to all addresses (`0.0.0.0`) in production. Set it to the intended loopback or private interface, or use network rules that permit only the proxy, and check the effective listener in Verify step 1.

`start-dev` is not a production deployment with a convenient default. It is a different profile whose default is the one you would otherwise have to ask for.

## 3. `hostname-admin` does not restrict the admin API

This is the control the product does not have, and it is the reason this guide exists.

Setting `--hostname-admin` moves the Administration Console to its own hostname. It does not close the old door. Keycloak states it outright:

> Using the `hostname-admin` option does not prevent accessing the Administration REST API endpoints via the frontend URL specified by the `hostname` option. If you want to restrict access to the Administration REST API, you need to do it on the reverse proxy level.

So the separation has to be enforced by you, at the proxy, on the public hostname. Keycloak's reverse proxy guide says the same thing about routing: "Exposed admin paths lead to an unnecessary attack vector", and lists `/admin/` as a path to expose "Only internally". The same table marks `/realms/master/` as "Only internally" and `/realms/` as exposed, which is why the rule above closes the administrative realm and not the realms your applications use.

```nginx
# In the server block for the PUBLIC hostname id.example.com.
# Applications need the realm endpoints. Nobody on the internet needs /admin/.
location /admin/ {
    return 404;
}

# By this guide's reading, which is not established at 26.8.2, the Admin Console
# AUTHENTICATES against this hostname even when hostname-admin moves its API calls
# elsewhere, because Keycloak builds the console's auth URL from the FRONTEND base URL. So
# a blanket 404 here would lock every administrator out. Restrict by SOURCE instead, which is what
# Keycloak asks for: "restrict access to the authentication protocol endpoints of the
# administrative realm from public IP addresses."
location /realms/master/ {
    allow 203.0.113.0/24;          # where your administrators connect from
    deny  all;

    proxy_pass         http://127.0.0.1:8080;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Forwarded-For   $remote_addr;
    proxy_set_header   X-Forwarded-Proto $scheme;
    proxy_set_header   X-Forwarded-Host  $host;
    proxy_set_header   X-Forwarded-Port  $server_port;
    proxy_set_header   X-Forwarded-Prefix "";
}

location / {
    proxy_pass         http://127.0.0.1:8080;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Forwarded-For   $remote_addr;   # overwrite, never append
    proxy_set_header   X-Forwarded-Proto $scheme;
    proxy_set_header   X-Forwarded-Host  $host;
    proxy_set_header   X-Forwarded-Port  $server_port;
    proxy_set_header   X-Forwarded-Prefix "";
}
```

This is a fragment for the public hostname's existing `server` block, not a replacement for it. Two different things happen on two different hostnames and it is worth being precise about which. The console's API calls go to the admin hostname, because Keycloak states that the "Administration Console implicitly accesses the API using the URL as specified by the `hostname-admin` option". By this guide's reading, its LOGIN does not: Keycloak builds the console's authentication URL from the frontend base URL, so the browser is sent to `id.example.com/realms/master/` to authenticate no matter where the console itself is served. The hostname page as served on 2026-11-05, before 26.8.2 was published, does not say so, so this reading is not established at 26.8.2; step 6 of the Verify section shows where your own console sends the browser. That is why the rule above restricts that path by source address rather than refusing it, and why an earlier version of this guide that refused it outright would have locked out every administrator including the one who applied it. A denied source gets a 403 from nginx rather than a 404, which is what step 5 of the Verify section looks for; if you see a 404 there, the path is being refused outright rather than restricted, and your administrators are locked out along with everyone else.

The admin hostname is a separate `server` block on `id-admin.internal`, reached over a tailnet or an SSH forward per [admin-uis.md](admin-uis.md), and it must proxy `/admin/`, `/resources/` and `/.well-known/`. Add `/js/` as well if you run a version whose console still loads its adapter from there; whether the 26.8.2 console does is not established. Step 6 of the Verify section is the test, and it checks that administrator login still WORKS rather than that something is closed.

Keycloak's 26.8.0 release record says that "The Client Admin API v2, introduced as an experimental feature in Keycloak 26.7, has been promoted to preview", and that "It can now be enabled with `--features=preview` or `--features=client-admin-api:v2`". The path that API is served under at 26.8.2 is not established, so neither is whether the `/admin/` rule above refuses it. If you enable it, find its path and check that the public hostname refuses it.

Keycloak's 26.8.0 release record also says that "In this release, the SCIM API is promoted from preview to supported", for an API that "provides a standards-based interface for managing users and groups within a realm". The server administration guide as served on 2026-11-05, whose page links name version 26.8.1, says the API "is exposed under the following base URL": `http://<host>:<port>/realms/<realm-name>/scim/v2`. That page also says the feature must be enabled on the server and then for each realm, and that the API "requires a bearer token with the appropriate permissions". This guide infers that a realm with SCIM enabled serves this user and group management API on the public hostname, because the rule above refuses `/admin/` while leaving `/realms/` exposed. Whether SCIM is enabled by default at 26.8.2, and the path it is served under at 26.8.2, are not established. If you enable it, find its path and decide at the proxy which clients may reach it.

Overwriting rather than appending matters. Keycloak's reverse proxy guide: "Take extra precautions to ensure that the client address is properly set by your reverse proxy via the `Forwarded` or `X-Forwarded-For` headers. If these headers are incorrectly configured, rogue clients can inject false values and trick Keycloak into thinking the client is connecting from a different IP address than the actual one." An appended header lets a client choose the first value, which is the one most code reads.

Overwrite all five, not the two you were thinking of. `--proxy-headers xforwarded` parses "`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Forwarded-Port`, and `X-Forwarded-Prefix`", and nginx passes through any request header you do not set, so the three you leave alone arrive exactly as the client sent them.

Keycloak also offers `--proxy-trusted-addresses`, and its default is to trust every address. At 26.8.2 the option's description reads "If set, then proxy headers from other addresses will be ignored. By default all addresses are trusted.", and the reverse proxy guide says that by default Keycloak "accepts proxy headers from any source". So with `--proxy-headers` set and this option unset, Keycloak parses forwarded headers from any client that reaches it, not only from your proxy. Set it to your proxy's IP addresses or CIDR ranges; Keycloak's own loopback example is `--proxy-trusted-addresses=127.0.0.1/32,::1/128`. At 26.8.2 the option also accepts an IPv6 address in square brackets, a hostname, and an address or hostname with a `:port` suffix, but for any hostname other than `localhost` its validator logs that "Using hostnames is deprecated and will be removed in a future version", so list addresses. Keycloak is honest about what the option is worth: "this is only weak protection because IP addresses can be spoofed." It is worth setting and it is not a substitute for overwriting the headers.

Without `--proxy-headers`, requests through a proxy fail rather than fall back: "If you are using a reverse proxy for anything other than TLS passthrough and do not set the `proxy-headers` option, then by default you will see 403 Forbidden responses to requests via the proxy that perform origin checking."

## 4. The first-boot window

authentik's initial setup sets the password on the default `akadmin` account; it does not ask the visitor to authenticate as an administrator first. At `version/2026.8.5`, visit the instance root (`/`, with the default web path). While setup is incomplete, it redirects to `/setup`, which plans the flow and redirects to `/if/flow/initial-setup/`. Opening the flow directly in a fresh session is rejected: its expression policy requires the context marker `goauthentik.io/core/setup/started-by` to equal `setup`. This marker comes from the public setup view, not from a credential.

The same policy permits a new plan only when `akadmin` is absent or `not akadmin.has_usable_password()`. The flow selects `akadmin` as the pending user, prompts for email, base URL and password, writes the existing user and logs them in. After completion, the setup view records setup as complete, disables the OOBE blueprints and changes the flow to require a superuser. An unauthenticated visitor who can reach a fresh instance and complete this flow can therefore claim its administrator account. Merely loading the page is not the claim, and the planning-time policy is not a promise that already-started sessions are revoked when a password is set.

Keep both ports unpublished to untrusted clients and keep the public reverse proxy route closed until setup is complete. For manual setup, use the loopback mappings in section 1 and browse locally or through an SSH forward; a proxy on a private container network can instead reach the service with both host mappings removed. Confirm setup is closed in a fresh session before allowing public traffic. This is the first-boot boundary described in [deployment-lifecycle.md](deployment-lifecycle.md).

For unattended setup, supply `AUTHENTIK_BOOTSTRAP_PASSWORD` before first startup through the protected `.env` file already loaded by both Compose services. The pinned startup handler also recognizes `AUTHENTIK_BOOTSTRAP_PASSWORD_HASH` and `AUTHENTIK_BOOTSTRAP_TOKEN`: any nonempty one triggers bootstrap, and successful application of the bootstrap blueprint marks the tenant setup complete. The password-hash form is validated; the source tests specify that the password forms set `akadmin`'s password and the token form supplies an API token. A token is not a browser-login password. Already-setup tenants are skipped, so changing these variables is not password rotation. Verify successful bootstrap and the closed setup route before publication, then remove the bootstrap secret from the startup environment. Protect the file and container-inspection access as described in [secrets.md](secrets.md). These are source-derived conditions, not a live demonstration of startup timing.

Keycloak's equivalent is a credential rather than a window, and it is meant to be thrown away. Its bootstrap admin documentation states that an account created this way "is **temporary**", that "the account should exist only for the duration necessary to perform operations needed to gain permanent and more secure admin access", and that afterwards "the account needs to be removed manually". This guide infers from the manual-removal instruction that the account does not expire on its own. Create a real administrator, enrol MFA on it per [mfa.md](mfa.md), then delete the bootstrap account and treat its password as a secret that was on a command line ([secrets.md](secrets.md)).

## 5. The management port

Keycloak serves health and metrics on a second port. Its management interface documentation states that "Management endpoints such as `/metrics` and `/health` are exposed on the default management port `9000` when metrics and health are enabled", and that "Exposing health and metrics endpoints on the default server is not recommended for security reasons, and you should always use the management interface".

The page does document a control: `https-management-client-auth` "Configures the management interface to require/request client authentication", taking `none`, `request` or `required`, and inheriting from the HTTP options when it is not given. Inheriting is the problem, because nothing in this guide's topology sets client authentication on the HTTP options either, so the effective answer is usually `none`. Setting it to `required` is not a one-line change in this topology, either: client certificates authenticate a TLS connection, and the startup command above enables plain HTTP with no server credentials, so there is no TLS on the management interface to carry them. Giving that port its own certificate and trust store comes first. Whether or not you do, keep 9000 on a private interface, which is the control that works without any of it. Your orchestrator needs `/health/ready`; the internet does not.

At authentik tag `version/2026.8.5`, core modes start the Rust metrics server: the Rust `main` starts it before the per-mode dispatch (healthcheck exits earlier), so proxy mode in a proxy-feature build starts it too. AllInOne and Worker modes start workers and store their handles in that server, and Server and AllInOne modes store the server handle. Its mode-dependent handler renders Prometheus metrics and appends Python metrics for server, worker and all-in-one modes. The router's fallback sends every path, including `/metrics`, to the handler; its wrapper has no authentication layer. The Rust metrics listener binds `listen.metrics` with plain HTTP (default `[::]:9300`) and a Unix socket. A Go web server metrics listener is also present at the tag: it serves `/metrics` with promhttp plus upstream metrics fetched from `<upstreamURL><web path>-/metrics/` and calls `http.ListenAndServe`. `WebServer.Start` calls `runMetricsServer` once per `listen.metrics` address, and the Go `cmd/server` command calls `WebServer.Start`, which this guide's search of the version/2026.8.3 tree found as the only caller chain. The tree's main Dockerfile builds the Rust `authentik` binary with the `core` feature and copies it into the image, whose `ak` entrypoint runs `authentik server` for the `server` command that the shipped Compose server service uses. This guide's search of the version/2026.8.3 tree found no image or release build of `cmd/server`, and a developer debug launch targets it. Neither search was repeated at version/2026.8.5, so their results are not established there. By this trace, the shipped server image's metrics listener is the Rust one. Whether the published image was built from this Dockerfile is NOT ESTABLISHED. The LDAP outpost builds its metrics router with `ak.MetricsRouter()`, which attaches a bare Prometheus handler at `/metrics`, and passes that router to both its HTTP metrics server on each metrics listen address and its Unix-socket server. Section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced. The cited outpost source does not establish its default listen address. The shipped Compose file does not publish 9300, but that does not protect the container-network listener. Restrict metrics reachability to trusted monitoring clients and do not add a public host mapping.

## 6. Enrolment is not enforcement

Every application behind this provider inherits its authentication, which means it inherits the administrator's authentication too. Enrol a phishing-resistant factor on the administrator account before you connect the first application, not after (this guide's requirement; the cited sources do not state this ordering). Both products support TOTP and WebAuthn; authentik's pinned TOTP and WebAuthn setup stages show it has enrolment stages for both factors. [mfa.md](mfa.md) covers the enrolment and the reason to require a hardware key or passkey for administrators specifically.

Enrolling a factor is not the same as requiring one. In Keycloak the requirement lives in the realm's authentication flow: when its default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. Required executions must succeed, but a Required second factor can be enrolled during authentication without proving possession of a preexisting factor. At authentik version/2026.8.5, an Authenticator Validate stage must be bound to the authentication flow; its unconfigured-device action defaults to SKIP. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The cited authentik files describe stage behaviour and flow binding but do not establish an administrator-specific factor policy. Test it the way [mfa.md](mfa.md) says to: open a fresh session with only the administrator password and confirm access is refused.

Two realm settings outlive everything above and neither is touched by it. Keycloak states that "Brute force detection is disabled by default. Enable this feature to protect against brute force attacks", and it is a realm setting rather than a deployment one, so a hardened deployment still accepts unlimited password guesses until you turn it on. And redirect URIs are worth a deliberate pass. Keycloak allows a wildcard at the end of a pattern, which is narrower than it sounds and still widens the set of destinations a token can be sent to; a bare `*` widens it to everything, for anyone who can reach the authorization endpoint, which is everyone. Register exact URIs per [oidc-integration.md](oidc-integration.md), and treat every wildcard as something you chose rather than something you inherited.

Keycloak's release records for 26.7.5 and 26.8.1 list security fixes that bear on this section. The 26.8.2 record, published on 2026-11-05, has an empty body, so whether 26.8.2 fixes security issues is not established. Keycloak 26.8.1 fixes CVE-2026-94218, "2FA setup enforcement bypass via /realms/{realm}/login-actions/restart", and CVE-2026-96445, "Conditional OTP trusts skip headers on untrusted proxy paths". This guide infers from those titles that on earlier releases an enforced second factor can be bypassed under conditions the records do not describe. The records give only the titles, so what each bypass needs, and whether either fix is in a 26.7.x release, are not established. CVE-2026-96445's title also names untrusted proxy paths, which bears on section 3's forwarded-header advice; whether overwriting the headers at the proxy, or setting `--proxy-trusted-addresses`, prevents it is not established. Keycloak 26.7.5 fixes CVE-2026-16103, "Incomplete fix for CVE-2026-9798 (Keycloak CIBA brute-force lockout bypass at token redemption)", and CVE-2026-88770, "Device Authorization Grant issues tokens to brute-force-locked accounts (sibling of CVE-2026-9798)", which bear on the brute force detection above. The 26.8.0, 26.8.1 and 26.8.2 records do not list those two, so whether those releases contain both fixes is not established. Run Keycloak 26.8.1 or later. The 26.7.5, 26.8.0 and 26.8.1 records list 36 other security-fix entries, which this guide assesses bear on no statement it makes; one more 26.8.1 entry under that heading is a flaky-test fix.

## 7. authentik has no equivalent to `hostname-admin`

Section 3 is Keycloak-specific because the control it describes is. At `version/2026.8.5`, authentik routes `/if/admin/` alongside `/if/user/` and flows in its core URL configuration. This guide assesses that authentik has no equivalent to `hostname-admin`: the cited configuration, Go startup code and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. Say that out loud rather than assuming the section above covers both products.

The pinned defaults set HTTP to `[::]:9000`, HTTPS to `[::]:9443` and metrics to `[::]:9300`; the Go `ListenConfig` has no administration field, and the Rust `ListenConfig` holds HTTP, HTTPS and metrics addresses, an optional `debug_tokio` address and trusted-proxy CIDRs. `WebServer.Start` starts configured HTTP, HTTPS and metrics listeners plus a Unix socket; its plain HTTP and Unix listeners serve the same router, whose web-path handler proxies to the application after embedded-outpost handling, and its HTTPS listener wraps a TCP listener in TLS and serves that router too. The tree's main Dockerfile and `ak` entrypoint run the Rust binary instead (section 5). In server mode, Rust startup spawns gunicorn on a Unix socket, then serves one router over plain HTTP on each `listen.http` address, over rustls on each `listen.https` address and on a Unix socket. That router sends requests for embedded-outpost applications to the outpost and the rest to the core router, which answers `/-/health/` itself, serves static assets and forwards everything else, including websocket upgrades, to gunicorn. Worker mode serves a health-check router on `listen.http`; in all-in-one mode the worker starts no HTTP listener of its own. These files show shared application routing, not a separate admin process or port. They do not prove which listeners a deployed build starts; deployed topology beyond the shipped Compose file is NOT ESTABLISHED.

Both interface routes use `BrandDefaultRedirectView`: authenticated external, service-account and internal-service-account users are redirected to a default application or denied; other requests fall through to `InterfaceView`. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.

The API v3 router registers applications' `api_urlpatterns`, including core users, groups, tokens and admin authenticators. The Go API client targets `api/v3` below the configured web path. The settings make the root URL module the root URL configuration, and it mounts each application's URLs under the web path; the API application's mountpoint is `api/` and its URL module mounts `v3/`, so the v3 router is served at `<web path>api/v3/`, which is `/api/v3/` with the default web path `/`. The REST framework settings set `TokenAuthentication` and then REST framework `SessionAuthentication` as the default authentication classes, `ObjectPermissions` as the default permission class and `ObjectFilter` among the default filter backends. Application settings modules and a `data.user_settings` module can update these settings; this guide's search of the version/2026.8.3 tree found no application settings module that does, a result not established at version/2026.8.5, and deployment overrides are NOT ESTABLISHED. Endpoints can replace the defaults: the users and groups viewsets list `TokenAuthentication`, `SessionAuthentication` and `AgentAuth`, and the flow executor sets `AllowAny`; this guide's search of the version/2026.8.3 tree found 66 non-test lines that set authentication or permission classes, a count not established at version/2026.8.5. `TokenAuthentication` recognizes API-intent tokens, OAuth access tokens with the authentik API scope, the managed-outpost secret and the IPC key, rejects inactive users and raises an authentication failure for unrecognized credentials; absent or unsupported authentication can return no user. `ObjectPermissions.has_permission` passes every object-specific request (its comment leaves view checks to `ObjectFilter` and writes to `has_object_permission`) and permits configured creation without an add permission; `has_object_permission` accepts global permissions or configured ownership before delegating to the parent object check; `HasPermission` checks `user.has_perms`. These are authentication and RBAC implementations, not proof that every administration endpoint applies them. `SessionAuthentication` is implemented in Django REST framework, outside the pinned tree, so its behaviour is NOT ESTABLISHED here; a per-endpoint audit and a complete permission boundary remain NOT ESTABLISHED.

Build any network boundary around authentik administration at the proxy using path restrictions. Identify and test the required paths for the deployed version and maintain that list. This guide assesses that the UI is not designed around this separation and that path-based separation is difficult to maintain. The pinned core URLs also show HTTP admin-template fallbacks at `/ws/outpost/<uuid:pk>/` and `/ws/client/`, and a `/ws/client/` websocket route wrapped in authentication middleware; together with the interface routes and API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization. The Rust static router also serves `/if/admin/assets/` under the configured web path (`/` by default) alongside the user, flow and RAC interface assets. The ASGI application routes websockets through a table built from applications' `websocket_urlpatterns` and nested under the web path; this guide's search of the version/2026.8.3 tree found three such modules, giving `/ws/client/`, `/ws/outpost/<uuid:pk>/`, `/ws/rac/<str:token>/` and `/ws/outpost_rac/<str:channel>/` with the default web path `/`. That search was not repeated at version/2026.8.5, so whether that release adds a module is not established. The `/ws/client/` stack resolves the session user, or an anonymous user, and its consumer accepts every connection, joining the user's group only when that user is authenticated. Both outpost routes deny a connection without a bearer token that `TokenAuthentication` accepts; the outpost consumer also requires view permission on that outpost, while the RAC outpost consumer accepts with no outpost-specific check on `/ws/outpost_rac/`. The RAC client consumer accepts, then denies unless the connection token belongs to the session. The flow executor is registered under the API router at `flows/executor/<slug:flow_slug>/` with `AllowAny`; the API schema names that path's GET operation `flows_executor_get`, and the flow interface calls `flowsExecutorGet`, which this guide takes to be the generated client method for that operation, so this guide infers that refusing the whole API prefix would break login. This guide read the Rust server, core and static routers, the root URL module, application mountpoints, the core, flow, API and v3 URL modules, and the websocket table with the three modules found at version/2026.8.3; any path list derived from them is bounded by those tables. This guide's proxy advice is not a vendor-supported path-isolation recipe; complete path coverage remains open.

authentik also reaches past this host. Its Compose file, by default, "mounts the Docker socket to the authentik worker container", which the vendor notes "comes with some inherent security risks", and which exists so authentik can deploy and manage outposts. Docker says only trusted users should control its daemon and that the daemon requires root privileges unless rootless mode is used. This guide assesses access to an ordinary rootful daemon socket as host-root-equivalent control. Docker says rootless mode runs the daemon and containers as a non-root user inside a user namespace, without root privileges; this guide assesses the blast radius as the daemon user and what that account can access. The general authentik installation warning and Docker privilege-model sources do not directly demonstrate host-root equivalence or the user-scoped blast radius. Check the daemon type and restrict socket access. The vendor's own options are a Docker socket proxy or removing the mount and deploying outposts by hand. Whichever you choose, check every deployed outpost's exposure. At version/2026.8.5, authentik supports Proxy, LDAP, RADIUS and RAC outposts. Its embedded Proxy outpost runs inside the main server on the same 9000 and 9443 ports, so it does not add a separate listener port. Managed Docker or Kubernetes outposts, and manually deployed outposts, can run elsewhere. The pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. The pinned `proxy.Dockerfile`, titled the authentik proxy outpost image, builds the Rust `authentik` binary with only the `proxy` feature, has no `go build` step, copies only that binary and sets `/authentik proxy` as its entrypoint. That subcommand starts the Rust proxy outpost, which serves plain HTTP on each `listen.http` address and rustls on each `listen.https` address unless it is the embedded outpost; Rust startup schedules the metrics server on `listen.metrics` before that dispatch, and the file exposes 9000, 9300 and 9443. This guide infers that an image built from that file runs the Rust proxy outpost rather than the cited Go proxy code; whether published images were built from it is NOT ESTABLISHED. The Docker controller maps the outpost's ports to the host unless `docker_map_ports` is false; it defaults to true. The Kubernetes controller reconciles Deployment and Service objects. The LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced. This guide assesses that the Verify probes below do not demonstrate any outpost boundary; check each deployed outpost separately.

## Verify

REASONED: scope of every live check below; the authoring host forbids opening listeners without an isolated network namespace, and has none, and ran neither identity provider. The fenced shell blocks below passed bash -n (Bash 5.3.9) and ShellCheck 0.11.0 at marking time with no diagnostics in an earlier form, which ran steps 1 to 8 as one block; the repository's gate suite runs bash -n and ShellCheck 0.11.0 over their current forms, whose exit statuses were also stub-run under Bash 5.3.9 with curl, ss and docker replaced by local stubs. Those stub runs date from 2026-10-31, and the steps 2 to 5 and step 7 blocks were stub-run again on 2026-11-01 in their current forms, except that step 8's comments, in the step 7 block, were reworded later with no command changed. In those 2026-11-01 runs, under Bash 5.3.9, both blocks refused example.com, example.net, example.org and their subdomains in lower, upper and mixed case with status 2 and no curl call, also after an inherited `shopt -s nocasematch`, `readonly`, `declare -i` or `set -e`, and passed other names, such as notexample.com and example.com.evil.io, to curl. Under dash and busybox sh, both blocks refused every name tried with 2 and "this block needs bash; run it in bash; not probing" before any probe. Live checks here are **REASONED**: the authoring host forbids opening listeners without an isolated network namespace, and has none. This source audit ran neither identity provider. The expected outcomes, including those of the existing checks below, follow the cited vendor documentation and pinned sources; the pinned curl and Keycloak sources support the documented exit codes, timeout options, proxy controls and listener defaults; no deployed outcome was observed. This guide assesses that a password-only refusal for an already-enrolled administrator does not distinguish enrolment from enforcement: Keycloak's default configured-OTP condition and authentik's validation-stage behaviour can both refuse that login. Test a user with no registered factor and inspect the realm flow or authentik stage settings. The runnable Verify commands below retain their existing pass conditions.

REASONED: authentik setup-flow comparison per the cited pinned root redirect, setup view, OOBE policy and source tests at version/2026.8.5; no disposable authentik instance or isolated test network is available in the authoring environment, so the expected redirects and logins were not observed. For authentik's setup check, use a disposable instance in an isolated test network and a fresh browser session. Open `http://127.0.0.1:9000/` locally or through the SSH forward. In the exposed state, with no bootstrap credentials and no usable `akadmin` password, expect the redirects through `/setup` to `/if/flow/initial-setup/`, then the setup form without a login. Complete it with test credentials and confirm those credentials log in as `akadmin`. After setup, a new anonymous session visiting `/setup` must return through the root to authentication rather than offer setup. Repeat on a fresh instance bootstrapped with `AUTHENTIK_BOOTSTRAP_PASSWORD`: expect login with the supplied password and no setup form. A direct visit to the flow is not a sufficient negative check because it is denied even before setup. The pinned root redirect, setup view, OOBE policy and source tests distinguish these outcomes; the tests were read, not executed here.

REASONED: network-boundary comparison per the cited shipped Compose publications at version/2026.8.5; no isolated exposed fixture or untrusted test client is available in the authoring environment, so neither reachability state was observed. For the network boundary, compare section 1's shipped publications with the loopback replacement using step 1 below. In the isolated exposed fixture, an untrusted test client can reach the setup route; with the loopback mappings and public proxy route closed, that client must not reach it, while the local browser still can. Retain this positive control so a stopped service cannot pass as an effective restriction. Confirm that neither configuration publishes 9300; its wildcard listener inside the container remains a separate monitoring-network boundary.

REASONED: authentik replacement-route design from the pinned core, OAuth2 provider, OAuth2 app configuration, root URL, app registry, installed-app settings, API mount and flow files; no deployed authentik route was probed. For authentik, substitute the deployed application's OAuth2 discovery URL as the positive control and confirm that its issuer matches the configured global or per-provider value. Check that an untrusted client cannot reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request. Do not refuse the whole API prefix without tracing login dependencies; confirm that an ordinary user can still complete login. The pinned OAuth2 file defines the per-application discovery suffix and `/if/admin/` is a core route. The pinned OAuth2 app configuration mounts `authentik.providers.oauth2.urls` at `application/o/` and `authentik.providers.oauth2.urls_root` at the root. The pinned settings install that app and name `authentik.root.urls` as the root URL configuration, which mounts each installed authentik app's mountpoints under the web path, so the discovery URL is `<web path>application/o/<slug:application_slug>/.well-known/openid-configuration`, which is `/application/o/<slug:application_slug>/.well-known/openid-configuration` with the default web path `/`. These files place the route in authentik's URL configuration; they do not show that a deployed instance answers it, so the discovery-URL and issuer check above remains the positive control. Section 7's cited files place the v3 router at `<web path>api/v3/`, which is `/api/v3/` with the default web path `/`, and register the flow executor under it at `flows/executor/<slug:flow_slug>/` with `AllowAny`. This guide infers that end-user flow execution uses the API prefix and that refusing the whole prefix would break login, because the flow interface calls `flowsExecutorGet`, which this guide takes to be the generated client method for that operation. No deployed login was observed. The Keycloak-route exclusion in the comments of the steps 2 to 5 fence below is this guide's inference from the fetched authentik route files, not a proof of every mounted route. For authentik, that fence's comments say to request the application's discovery URL in step 2 and to put its expected issuer on the `set --` line, so this discovery-URL and issuer check is the fence's positive control there too.

REASONED: host listener inventory (step 1) in the following block, per the Keycloak listener and cache-port documentation, the pinned authentik listener defaults and the authentik Redis removal notes cited below; the authoring host has no isolated network namespace for listeners and ran neither identity provider, so no listener table was observed. The block exits 2 with `ss is not installed here; not listing sockets` when `ss` is missing, 3 when `ss -tlnp` fails, and otherwise 0, leaving every listener for you to judge against the ports in its comment, because whether 6379 matters depends on your authentik version and the host table does not show a container's own namespace.

```bash
# 1. On the host itself: nothing listens on a public address. Keycloak defaults to HTTPS 8443; HTTP 8080 is enabled explicitly here,
#    and management 9000; authentik serves 9000 and 9443, and metrics on 9300. Three more
#    are easy to forget because they are not the product's front door. 7800 and 57800 are
#    Keycloak's cache transport and failure detection, which carry the sessions and tokens
#    of a clustered deployment; TLS is on by default there for TCP stacks, so this is about
#    reachability rather than plaintext, and a reachable cluster port is still a cluster you
#    did not mean to offer. 6379 is Redis, which authentik used for caching, tasks, the
#    embedded outpost's session store and WebSocket connections. It moved tasks to
#    Postgres in 2025.8 and the rest in 2025.10, which "no longer uses Redis at all", so
#    whether this port matters depends on your version. Check it rather than assume.
(                                       # a subshell, so the exits below end only the subshell
  command -v ss > /dev/null || { echo "ss is not installed here; not listing sockets"; exit 2; }
  if ss -tlnp; then   # read every listener; 6379/7800/8080/8443/9000/9443/9300/57800: 127.0.0.1 or an RFC 1918 address only
    echo "block exit 0; unclassified observation: every listener above is yours to judge against the ports in this block's comment"
    exit 0
  else
    echo "ss -tlnp exit $?: the listener table could not be read; inconclusive (block exit 3)"
    exit 3
  fi
)
```

REASONED: following block; Compose publication cross-check per the shipped Compose file and the Docker Compose CLI reference cited below; no Compose deployment of either provider is available in the authoring environment, so no publication table was observed. Run it from the identity provider's Compose project directory. It exits 2 when `docker` is not installed, which on a host that runs Keycloak without Docker means this check does not apply, or when `docker compose version` fails, which this guide expects without the Compose plugin, 3 when `docker compose ps` fails, and otherwise 0, leaving the published ports for you to judge, since a proxy in the same project publishing 443 is expected.

```bash
# ss on the HOST does not see a container's own namespace, and a published Docker port
# bypasses the host firewall besides, so cross-check what Compose actually published:
(                                       # a subshell, so the exits below end only the subshell
  command -v docker > /dev/null || { echo "docker is not installed here; not listing Compose publications"; exit 2; }
  docker compose version > /dev/null 2>&1 || { echo "docker compose is not available here; not listing Compose publications"; exit 2; }
  if docker compose ps --format 'table {{.Service}}\t{{.Ports}}'; then
    # no 0.0.0.0 or :: on the identity provider's OWN rows. A proxy in the same
    # project publishing 443 is correct and expected. This also sees one Compose
    # project, not every container on the host.
    echo "block exit 0; unclassified observation: the published ports above are yours to judge"
    exit 0
  else
    echo "docker compose ps exit $?: run it from the identity provider's Compose project directory; inconclusive (block exit 3)"
    exit 3
  fi
)
```

REASONED: following block; steps 2 to 5 per the Keycloak hostname, reverse proxy and production documentation and the nginx `location` and `return` documentation cited below; no deployed provider or outside test host is available in the authoring environment, so none of these answers was observed. Run it from a host outside every network you have allowed, with your public host name, the realm your applications use and the issuer you expect on its `set --` line. It refuses with status 2 if a value is left unsubstituted or malformed, if the host is example.com, example.net, example.org or one of their subdomains, if the realm is master, if `python3` is missing, if a proxy variable cannot be cleared or if it is pasted into a shell other than bash, such as dash or busybox sh, where `shopt` does not exist, because the block needs bash. It also refuses with status 2 if the `PASTE_WHOLE_BLOCK` marker that opens its `set --` line is missing, as when that line is left out of the paste, printing "paste the whole block, including its set -- line; not probing", or if that line does not carry exactly three values. Step 2 is the positive control: unless the discovery document's issuer is a JSON string equal in full to the one on the `set --` line, the block reports 3 and does not run steps 3 to 5. Step 3 passes on 404 and is a finding (1) on any 2xx, any 3xx, 401 or 403; step 4 passes on 404 and is a finding on 401; step 5 passes on 403 and is a finding on 200 or 404. Any other code, or a request that fails, is inconclusive (3), and a finding outranks an inconclusive result. The paths are Keycloak's; on authentik, adapt them and the issuer as the block's comments and the authentik paragraph above say. Steps 3 to 5 sample three routes, so the rest of the administration surface and step 6's login stay for you to check, as the block's last line says. Step 6's reason, that Keycloak builds the console's authentication URL from the frontend hostname, is this guide's reading and is not established at 26.8.2 (section 3), so watch where the browser actually goes.

```bash
# Steps 2 to 5 and 7 must run from a host OUTSIDE every network you have allowed, against a
# system you are authorized to test. Neutralize the proxy settings first, all of them:
# curl reads ALL_PROXY and all_proxy as well as per-scheme variables (http_proxy is
# lowercase only), and it reads ~/.curlrc too. This guide assesses that a proxy whose
# egress sits inside an allowed range can make a blocked endpoint appear reachable
# from a location that should have been refused. This block and step 7's clear those
# variables inside their own subshells, so your own shell keeps its settings, and pass
# --noproxy '*' to every curl as well.
# -q as curl's first option ignores ~/.curlrc, which can itself set a proxy or turn verification off.
# Every path below is KEYCLOAK's. authentik does not serve /realms/ or /admin/master/,
# so on authentik substitute its own application and administration URLs. In step 2, request
# your application's OAuth2 discovery URL and put the issuer it should name on the set -- line:
# step 2 passes only when that document's issuer is exactly that value.
(                                       # a subshell, so your own script arguments and proxy settings are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_HOST' 'REPLACE_WITH_YOUR_APP_REALM' 'REPLACE_WITH_YOUR_ISSUER_URL'   # the public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot), the realm your APPLICATIONS use (not master), then the issuer URL step 2 must print: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  case "$2" in
    ""|*REPLACE_WITH_*|master|*/*|*[?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute the realm your applications use (not master; no slash, query, fragment or percent sign) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    ""|*REPLACE_WITH_*|*[[:space:][:cntrl:]]*) echo "substitute the issuer URL your applications expect, exactly as they are configured with it, inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  command -v python3 > /dev/null || { echo "python3 is not installed here, and step 2 needs it to read the issuer; not probing"; exit 2; }
  unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy NO_PROXY no_proxy ||
    { echo "a proxy variable is readonly in this shell and cannot be cleared; not probing"; exit 2; }
  set -- "$1" "$2" "$3" 0               # the 4th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0

  # 2. POSITIVE CONTROL, and the reason every check below means anything: the public
  #    hostname answers from out here. Use the realm your APPLICATIONS use, not master:
  #    section 3 restricts the master realm to your administrators' range, so probing it here
  #    would test the wrong thing and tell you nothing about the realm your applications use.
  # python3 reads the discovery document straight from curl through a pipe, never from a shell capture,
  # which would drop a NUL byte, and exits 4 for an issuer that is not a string or holds a NUL byte.
  set -- "$1" "$2" "$3" "$4" "$(if curl -q -g --noproxy '*' -sS "https://$1/realms/$2/.well-known/openid-configuration" | python3 -c 'import json,sys; d=json.load(sys.stdin.buffer); i=d["issuer"]; isinstance(i, str) or sys.exit(4); chr(0) in i and sys.exit(4); print(i)'; then printf '\n%s %s' "${PIPESTATUS[0]}" "${PIPESTATUS[1]}"; else printf '\n%s %s' "${PIPESTATUS[0]}" "${PIPESTATUS[1]}"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # curl's and python3's exit statuses, then all python3 printed, ending in print's own newline
  set -- "$1" "$2" "$3" "$4" "${5%% *}" "$6" "${5#* }"   # curl's exit status, python3's output, then python3's exit status
  if [ "$5" != 0 ]; then
    echo "curl exit $5: the discovery request failed, so the positive control failed; inconclusive"; set -- "$1" "$2" "$3" 3
  else
    set -- "$1" "$2" "$3" "$4" "$7" "${6%$'\n'}"   # python3's exit status, then the whole issuer without print's newline, so an issuer with a line break in it cannot match
    printf '%s\n' "$6"
    # It must print YOUR issuer URL. A 200 alone proves only that something answered: a wrong
    # upstream or a generic responder satisfies it while the real provider sits exposed
    # elsewhere. If this does not print the issuer you expect, stop reading and fix that first,
    # because every check below will "pass" for the wrong reason.
    if [ "$5" != 0 ]; then
      echo "python3 exit $5: the answer is not a discovery document with an issuer, so the positive control failed; inconclusive"; set -- "$1" "$2" "$3" 3
    elif [ "$6" != "$3" ]; then
      echo "the issuer printed above is not the one on the set -- line, so the positive control failed; inconclusive"; set -- "$1" "$2" "$3" 3
    fi
  fi
  [ "$4" = 0 ] || { echo "block exit 3; steps 3 to 5 did not run: fix step 2 first, because until it prints your issuer their answers mean nothing"; exit 3; }

  # 3. The administration console is closed on the PUBLIC hostname.
  set -- "$1" "$2" "$3" "$4" "$(if curl -q -g --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' "https://$1/admin/master/console/"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%%$'\n'*}"   # curl's exit status, then the HTTP code
  printf '%s\n' "$6"
  # 404 is the pass. A 302 to a login page is NOT a pass: it means the console answered
  # and is offering to authenticate you. Any 2xx, any 3xx, 401 or 403 all mean the path
  # was served by something.
  case "$5:$6" in
    0:404) ;;
    0:2??|0:3??|0:401|0:403) echo "FINDING: the console path answered $6 on the public host name, so something served it"; set -- "$1" "$2" "$3" 1 ;;
    0:*) echo "HTTP $6 from the console path is neither the 404 pass nor a code step 3 reads as served; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
    *) echo "curl exit $5: the console request failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
  esac

  # 4. The administration REST API is closed on that same hostname. hostname-admin does
  #    not do this for you, so this is the step that proves your proxy rule does.
  set -- "$1" "$2" "$3" "$4" "$(if curl -q -g --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' "https://$1/admin/realms/master/users"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%%$'\n'*}"   # curl's exit status, then the HTTP code
  printf '%s\n' "$6"
  # 404 is the pass. 401 means the API answered and asked for a token.
  case "$5:$6" in
    0:404) ;;
    0:401) echo "FINDING: the admin REST API answered 401 on the public host name, so it is still served there"; set -- "$1" "$2" "$3" 1 ;;
    0:*) echo "HTTP $6 from the admin REST API path is neither the 404 pass nor the 401 finding; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
    *) echo "curl exit $5: the admin REST API request failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
  esac

  # 5. The administrative realm's login paths are RESTRICTED, not refused. Section 3 allows
  #    them from your administrators' range and denies everything else, so from out here:
  #    403 is the pass. nginx answers a denied source with 403, not 404.
  #    200 means the allow rule covers the whole internet, or is not there at all.
  #    404 means you used `return 404` rather than an allow rule, which closes the path for
  #    your administrators too; see section 3 for why the console needs it on this hostname.
  set -- "$1" "$2" "$3" "$4" "$(if curl -q -g --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' \
    "https://$1/realms/master/.well-known/openid-configuration"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%%$'\n'*}"   # curl's exit status, then the HTTP code
  printf '%s\n' "$6"
  case "$5:$6" in
    0:403) ;;
    0:200) echo "FINDING: the master realm answered 200 from out here, so the allow rule covers the whole internet or is not there at all"; set -- "$1" "$2" "$3" 1 ;;
    0:404) echo "FINDING: the master realm answered 404, so return 404 closes the path for your administrators too"; set -- "$1" "$2" "$3" 1 ;;
    0:*) echo "HTTP $6 from the master realm is not the 403 pass or a 200 or 404 finding; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
    *) echo "curl exit $5: the master realm request failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
  esac
  # Steps 3 to 5 sample three routes and expect two different answers: 404 from the two
  # /admin/ paths, which are refused outright, and 403 from the master realm, which is
  # restricted by source. Either way they prove those three requests were handled as intended,
  # not that the whole administration surface is. A more specific `location` elsewhere in the
  # same server block can still serve one, so read the effective configuration too.
  echo "block exit $4; steps 3 to 5 sampled three routes, so the rest of the administration surface (read the effective configuration) and step 6 below are yours to check"
  exit "$4"
)

# 6. An administrator can still log in. This is the half the rule in section 3 can break and
#    the half nobody tests. From inside the network you allowed in that rule, complete a REAL
#    login to the console rather than just loading the page:
#    open https://id-admin.internal:8443/admin/master/console/ and authenticate.
#    Watch where the browser goes. It SHOULD be sent to id.example.com/realms/master/ to
#    authenticate, because Keycloak builds the console's auth URL from the frontend hostname,
#    and it should come back. If that request 403s, your allow rule does not cover the address
#    you are coming from. If it 404s instead, `return 404` is still in place on that path,
#    which is the state step 5 warns about and it locks out every administrator. If you are
#    testing from outside the allowed range it SHOULD fail, and that is the rule working
#    rather than a fault.
```

```bash
# 7. The management, metrics and application ports are not routable from out here. All of
#    them: a reader who remapped 9000 and left 9443 published passes every other step.
#    --connect-timeout is separate from -m so the two deadlines are distinguishable in the
#    output, not because it changes the exit code: this guide infers that a port that
#    accepts the connection and then stalls, and one never reached before the deadline,
#    can both end in exit 28. The diagnostic may distinguish them, so print it whole.
#    Run it from the same outside host as steps 2 to 5; like that block, it clears the
#    proxy variables in its own subshell and starts curl with -q and --noproxy '*'.
(                                       # a subshell, so your own script arguments and proxy settings are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_HOST'   # the public host name, no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy NO_PROXY no_proxy ||
    { echo "a proxy variable is readonly in this shell and cannot be cleared; not probing"; exit 2; }
  set -- "$1" 0 8080 8443 9000 9300 9443   # the host, the block's status so far (1, a finding, outranks 3, inconclusive, which outranks 0), then the ports still to probe
  while [ "$#" -gt 2 ]; do
    set -- "$1" "$2" "$3" "$(if curl -q -g --noproxy '*' -sS --connect-timeout 3 -m 8 -o /dev/null -v "http://$1:$3/" 2>&1 >/dev/null; then printf '\n0'; else printf '\n%s' "$?"; fi)" "${@:4}"
    set -- "$1" "$2" "$3" "${4##*$'\n'}" "${4%$'\n'*}" "${@:5}"   # the host, the status so far, this port, curl's exit status, its diagnostic, then the ports still to probe
    echo "=== $3: curl exit $4"
    printf '%s\n' "$5"
    # Exit 0 means curl completed the HTTP operation, so treat it as an answer. Exit 7 reports
    # a connection failure, which is consistent with isolation but not proof of it, and counts only
    # once the diagnostic shows the target you meant. This guide infers that exits 52 and 56 follow an accepted
    # connection, so a listener is reachable; inspect the diagnostic. Other exits require diagnostic review.
    # Exit 28 is a timeout and does NOT settle it on its own: this guide infers that a port
    # that accepted you and then went quiet, and one never reached, can both end there.
    # The whole diagnostic is printed rather than filtered for that reason.
    # Read it yourself. A line saying the connection was established, before a timeout, means
    # something accepted you and then went quiet, which is an answer. Do not reduce this to a
    # grep for a fixed phrase: curl has changed that wording more than once, and an earlier
    # version of this guide matched a phrase current curl no longer prints and then read its
    # absence as proof that nothing was listening. Absence of a line you were looking for is not
    # evidence. If the output does not settle it, the result is inconclusive and has to be
    # chased rather than accepted. A firewall that drops rather than refuses connections
    # gives exit 28 on every port, so this block then ends with 3 and the diagnostics decide it.
    case "$4" in
      0|52|56) echo "FINDING: port $3 accepted the connection from out here (curl exit $4), so a listener is reachable"; set -- "$1" 1 "${@:3}" ;;
      7) echo "port $3: connection failed (curl exit 7), consistent with isolation from this host but not proof of it; it counts only if the diagnostic above shows the target you meant" ;;
      *) echo "port $3: curl exit $4 does not settle it on its own; read the diagnostic above; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 "${@:3}" ;;
    esac
    set -- "$1" "$2" "${@:6}"
  done
  echo "block exit $2; the diagnostics above are yours to read (exit 7 counts only for the target you meant, and a connection established before a timeout is an answer), and step 8 below is a lookup you make yourself"
  exit "$2"
)

# 8. Keycloak's bootstrap admin is gone. This guide infers from manual-removal guidance
#    that it does not expire on its own. Ask for the name
#    rather than listing users: the users endpoint's default result limit is not established
#    at 26.8.2, and a bootstrap account past the end of a capped list looks like a deleted one.
#    kcadm.sh get users -r master -q exact=true -q "username=REPLACE_WITH_BOOTSTRAP_NAME" --fields username,id
#    Keep exact=true and inspect the returned username: this guide treats `username=`
#    without `exact=true` as a non-exact match; the pinned passage documents only the
#    `q=` form. Any default cap applies either way, so an unfiltered list proves
#    nothing about what is not in it. Keep the -q flags in this order as this guide's defensive
#    advice based on a report that exact=true after the username filter did not take
#    effect; the pinned admin CLI documentation does not establish that behaviour, and
#    ordering it defensively costs nothing.
#    Check the master realm's service accounts too: a bootstrap SERVICE account is created
#    by the client-id form of the same mechanism and is not in the user list at all.
```

REASONED: preceding block; step 7's direct port probes, step 8's bootstrap-account lookup, the repeat coverage across addresses and families and the surfaces these blocks do not test, per the cited Keycloak and authentik documentation, pinned sources and curl exit-code documentation. No deployed provider, isolated network namespace for listeners, or public address is available in the authoring environment, so none of the steps ran against a provider. The marking-time bash -n and ShellCheck 0.11.0 passes covered the earlier single-block form; the current blocks are covered by the gate suite's bash -n and ShellCheck 0.11.0 passes and by the stub runs recorded at the top of this section. The pinned curl and Keycloak sources support the documented exit codes, timeout options, proxy controls and listener defaults; no deployed outcome was observed. The step 7 block takes your public host name on its `set --` line and refuses with status 2 if it is left unsubstituted or malformed, if it is example.com, example.net, example.org or one of their subdomains, if a proxy variable cannot be cleared, or if the block is pasted into a shell other than bash, such as dash or busybox sh, where `shopt` does not exist, because the block needs bash. It also refuses with status 2 if the `PASTE_WHOLE_BLOCK` marker that opens its `set --` line is missing, as when that line is left out of the paste, printing "paste the whole block, including its set -- line; not probing", or if that line does not carry exactly one value. It records a finding (1) for a port whose curl exit is 0, 52 or 56, and an inconclusive result (3) for exit 28 or any other exit except 7. It records exit 7 as 0 and prints that the connection failure is consistent with isolation but not proof, counting only once the diagnostic shows the target you meant; behind a firewall that drops rather than refuses connections, it cannot end with 0. One name is not one address, and one address is not one origin. Repeat steps 2 to 5 and 7 for every public address the name carries and in both families, since a host filtered on IPv4 while it answers on IPv6 passes all of them. A CDN or load balancer answering on 443 also says nothing about whether the backend has its own reachable address, so check the origin directly as well. And nothing here tests `id-admin.internal`, the database, or any authentik outpost's boundary, including the embedded outpost's routes on the core server ports; those surfaces need separate checks. The port list is the one this guide's own topology creates, not an inventory: scan the whole range if you want one. Step 8's comments give no value for the users endpoint's default result limit: the 100-result default that an earlier version of them gave cites no Keycloak source and is not established at 26.8.2, and step 8's exact-name lookup does not rest on any default.

## Sources (checked September 2026)

- Keycloak production configuration, including the TLS requirement and separating the admin REST API and console (checked November 2026): https://www.keycloak.org/server/configuration-production
- Keycloak hostname options, including the production and dev profile defaults for `hostname-strict`, and the statement that `hostname-admin` does not restrict the Administration REST API (checked November 2026): https://www.keycloak.org/server/hostname
- Keycloak reverse proxy configuration, including `proxy-headers`, `proxy-trusted-addresses`, the forwarded-header warning, and the exposed-paths table (checked November 2026): https://www.keycloak.org/server/reverseproxy
- Keycloak bootstrap and recovery admin accounts, including that the account is temporary and must be removed manually (checked November 2026): https://www.keycloak.org/server/bootstrap-admin-recovery
- Keycloak management interface and the default management port 9000 (checked November 2026): https://www.keycloak.org/server/management-interface
- authentik Docker Compose installation and operational setup instructions (version-specific behavior is pinned below) (checked November 2026): https://docs.goauthentik.io/install-config/install/docker-compose/
- authentik monitoring, including the separate metrics port 9300 and that the metrics carry no authentication (checked November 2026): https://docs.goauthentik.io/sys-mgmt/ops/monitoring
- authentik `version/2026.8.5` shipped Compose, image tag, both publications and the services' `.env` inputs (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/compose.yml#L1-L67
- authentik `version/2026.8.5` HTTP, HTTPS and metrics wildcard defaults (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/default.yml#L36-L48
- authentik `version/2026.8.5` shared server and worker metrics router and plain HTTP metrics listener (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/metrics/mod.rs#L70-L100
- authentik `version/2026.8.5` core metrics startup and worker registration (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/main.rs#L99-L122
- authentik `version/2026.8.5` mode-dependent Prometheus metrics handler (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/metrics/handlers.rs#L12-L42
- authentik `version/2026.8.5` metrics router wrapper middleware (no authentication layer) (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-axum/src/router.rs#L36-L59
- authentik `version/2026.8.5` outpost Prometheus handler, metrics listen address and Unix socket serving (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/ak/metrics.go#L18-L72
- authentik `version/2026.8.5` LDAP and LDAPS listener startup, LDAP outpost metrics router and its HTTP and Unix-socket servers (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/ldap/ldap.go#L91-L121
- authentik `version/2026.8.5` Go web server metrics listener present at the tag (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/web/metrics.go#L22-L52
- authentik `version/2026.8.5` administration, user and flow URL routes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L36-L75
- authentik `version/2026.8.5` Go listener configuration fields (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/config/struct.go#L53-L62
- authentik `version/2026.8.5` Go listener startup and API client prefix (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/web.go#L132-L183
- authentik `version/2026.8.5` Go plain HTTP and Unix listeners sharing the router (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/web.go#L229-L288
- authentik `version/2026.8.5` Go application web-path proxy and embedded-outpost handling (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/proxy.go#L47-L127
- authentik `version/2026.8.5` interface rendering and user-type redirect or denial (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/views/interface.py#L54-L89
- authentik `version/2026.8.5` core route entries, API registrations and websocket route (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L36-L112
- authentik `version/2026.8.5` API v3 application registration and URL assembly (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/api/v3/urls.py#L18-L58
- authentik `version/2026.8.5` Bearer parsing, IPC user and token authentication (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/api/authentication.py#L33-L166
- authentik `version/2026.8.5` object and named RBAC permission implementations (checked November 2026): https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/rbac/permissions.py#L15-L60
- authentik `version/2026.8.5` Rust main metrics startup before mode dispatch and per-mode handle storage (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/main.rs#L57-L135
- authentik `version/2026.8.5` Go `cmd/server` command calling `NewWebServer` and `WebServer.Start`, and the developer debug launch configuration targeting it (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/cmd/server/server.go#L25-L73 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/.vscode/launch.json#L37-L42
- authentik `version/2026.8.5` main Dockerfile Rust `authentik` binary built with the `core` feature (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/Dockerfile#L126-L142
- authentik `version/2026.8.5` main image binary copy and `ak` entrypoint (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/Dockerfile#L234-L252
- authentik `version/2026.8.5` `ak` entrypoint running the Rust binary for server, worker and all-in-one, and the function that executes that command (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L16-L33 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L35-L54 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L92-L94
- authentik `version/2026.8.5` Rust server gunicorn Unix-socket backend (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/mod.rs#L86-L106
- authentik `version/2026.8.5` Rust server embedded-outpost routing and HTTP, HTTPS and Unix listeners (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/mod.rs#L260-L352
- authentik `version/2026.8.5` Rust core router websocket upgrade forwarding (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/core.rs#L153-L155
- authentik `version/2026.8.5` Rust core router health, static and gunicorn routes under the web path (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/core.rs#L277-L320
- authentik `version/2026.8.5` shared plain HTTP, Unix-socket and rustls server runners (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-axum/src/server.rs#L22-L170
- authentik `version/2026.8.5` Rust worker-mode HTTP listener and health router (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/worker/mod.rs#L347-L361 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/worker/healthcheck.rs#L66-L76
- authentik `version/2026.8.5` Rust listen configuration fields (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/schema.rs#L203-L214
- authentik `version/2026.8.5` Go TLS listener serving the shared router (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/web/web_tls.go#L46-L72
- authentik `version/2026.8.5` REST framework default authentication, permission and filter classes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L240-L252
- authentik `version/2026.8.5` root URL configuration and ASGI application settings (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L320-L339
- authentik `version/2026.8.5` app and user settings modules updating REST framework settings (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L566-L609
- authentik `version/2026.8.5` API app `api/` mountpoint and `v3/` mount (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/api/apps.py#L6-L13 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/api/urls.py#L7-L9
- authentik `version/2026.8.5` default web path (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/default.yml#L162-L166
- authentik `version/2026.8.5` Rust configuration loader embedding `default.yml` as its first source, and the Python `SEARCH_PATHS` loader reading `default.yml` first (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/mod.rs#L24-L24 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/mod.rs#L71-L89 . More authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/config.py#L26-L28 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/config.py#L86-L111
- authentik `version/2026.8.5` websocket routing table and ASGI protocol router (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/websocket.py#L14-L34 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/asgi.py#L75-L83
- authentik `version/2026.8.5` websocket session authentication stack and client message consumer (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/asgi_middleware.py#L42-L84 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/ws/consumer.py#L38-L52
- authentik `version/2026.8.5` outpost websocket route, bearer-token middleware and outpost permission check (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/urls.py#L16-L23 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/channels.py#L13-L43 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/consumer.py#L73-L83
- authentik `version/2026.8.5` RAC websocket routes, client connection-token check and outpost consumer acceptance (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/urls.py#L30-L43 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/consumer_client.py#L63-L96 . More authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/consumer_outpost.py#L14-L16
- authentik `version/2026.8.5` flow executor API route and `AllowAny` permission (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/urls.py#L36-L50 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/views/executor.py#L101-L104
- authentik `version/2026.8.5` flow interface call to the flow executor API, and the API schema's `flows_executor_get` operation for the executor path (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/web/src/flow/FlowExecutor.ts#L224-L228 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/schema.yml#L9288-L9290
- authentik `version/2026.8.5` Rust static interface asset routes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/static.rs#L159-L168
- authentik `version/2026.8.5` users and groups viewset authentication classes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/api/users.py#L650-L654 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/api/groups.py#L406-L410
- authentik `version/2026.8.5` root redirect before authentication and setup/flow URL routes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/views/interface.py#L44-L51 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L59-L70
- authentik `version/2026.8.5` setup planning, completion flag and post-setup superuser requirement (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/setup/views.py#L35-L92
- authentik `version/2026.8.5` OOBE prompts, pending user, started-by/usable-password policy and stage/policy bindings (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/blueprints/default/flow-oobe.yaml#L8-L194
- authentik `version/2026.8.5` flow authentication default, planning-time policy check and continuation of existing session plans. The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/models.py#L183-L187 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/planner.py#L263-L292 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/views/executor.py#L175-L196
- authentik `version/2026.8.5` bootstrap environment handling and failure/skip conditions (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/setup/signals.py#L18-L48
- authentik `version/2026.8.5` source tests specifying setup redirects, anonymous password setup, direct-flow denial and bootstrap password/token behavior (read, not run) (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/tests/test_setup.py#L26-L130 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/tests/test_setup.py#L168-L245
- authentik `version/2026.8.5` TOTP setup stage (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_totp/models.py#L29-L44
- authentik `version/2026.8.5` WebAuthn setup stage (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_webauthn/models.py#L90-L113
- authentik `version/2026.8.5` OutpostConfig definition and Docker port-mapping default (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/models.py#L53-L85
- authentik `version/2026.8.5` outpost types (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/models.py#L99-L105
- authentik `version/2026.8.5` outpost deployment and provider types (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/index.mdx#L6-L13
- authentik `version/2026.8.5` Docker, Kubernetes and manual outpost deployment (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/index.mdx#L30-L48
- authentik `version/2026.8.5` embedded proxy outpost and shared server ports (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/embedded/embedded.mdx#L5-L15
- authentik `version/2026.8.5` proxy outpost HTTP, HTTPS and metrics listeners (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/proxyv2/proxyv2.go#L172-L202
- authentik `version/2026.8.5` proxy outpost image build of the Rust `authentik` binary with the `proxy` feature, its title, binary copy, exposed ports and `/authentik proxy` entrypoint, and the Rust proxy outpost subcommand and its HTTP and HTTPS listeners (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/proxy.Dockerfile#L29-L42 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/proxy.Dockerfile#L51-L78 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/outpost/proxy/mod.rs#L44-L119
- authentik `version/2026.8.5` RADIUS outpost and metrics listeners (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/radius/radius.go#L100-L125
- authentik `version/2026.8.5` Docker outpost controller conditional port mapping (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/controllers/docker.py#L218-L230
- authentik `version/2026.8.5` Kubernetes outpost Deployment and Service reconcilers (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/controllers/kubernetes.py#L65-L88
- authentik `version/2026.8.5` OAuth2 provider discovery suffix (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/urls.py#L53-L63
- authentik `version/2026.8.5` global and per-provider issuer modes (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/models.py#L115-L122
- authentik `version/2026.8.5` issuer URL construction (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/models.py#L365-L378
- authentik `version/2026.8.5` application URL mounting and web path (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/urls.py#L18-L48
- authentik `version/2026.8.5` OAuth2 provider app mountpoints, `urls` at `application/o/` and `urls_root` at the root (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/apps.py#L12-L15
- authentik `version/2026.8.5` app registry iteration over installed `authentik` app configurations (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/utils/reflection.py#L46-L52
- authentik `version/2026.8.5` OAuth2 provider app in the tenant apps, and the installed apps built from the shared and tenant apps (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L83-L108 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L612-L613
- authentik `version/2026.8.5` security-policy supported-version table at the time of writing (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/SECURITY.md#L25-L32
- Keycloak `26.8.2` security-policy upgrade guidance (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/SECURITY.md#L42-L48
- Keycloak `26.8.2` realm export backup limitations and stop-node conditions (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/importExport.adoc#L11-L16
- Docker Engine security, daemon root requirement, trusted daemon users and host filesystem access (checked October 2026): https://docs.docker.com/engine/security/
- Docker Engine rootless mode, daemon and containers without root privileges (checked October 2026): https://docs.docker.com/engine/security/rootless/
- Docker daemon privileges, trusted control and host filesystem access, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112
- Docker rootless non-root daemon and containers in a user namespace, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/rootless/_index.md#L8-L21
- Docker Compose CLI reference for `docker compose version`, which shows the Docker Compose version information (checked October 2026): https://docs.docker.com/reference/cli/docker/compose/version/
- Docker Compose CLI reference for `docker compose ps` and its `--format` option, which takes `table`, `table TEMPLATE`, `json` or a Go template (checked October 2026): https://docs.docker.com/reference/cli/docker/compose/ps/
- curl `curl-8_23_0` exit-code list, defining exit 7 as a connection failure: https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L23-L24
- Keycloak `26.8.2` Admin CLI user filtering example and its non-exact matching note (no documented flag-order behaviour) (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/admin-cli.adoc#L1034-L1045
- Keycloak server administration guide, brute force detection ("Brute force detection is disabled by default"), unspecific redirect URIs, and the SCIM API's base URL, enablement and bearer-token requirement (checked November 2026): https://www.keycloak.org/docs/latest/server_admin/index.html
- nginx `location` selection and the `return` directive: https://nginx.org/en/docs/http/ngx_http_core_module.html#location , https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return
- Keycloak configuring distributed caches, including the default cache ports 7800 (`cache-embedded-network-bind-port`, unicast data transmission) and 57800 (`jgroups.fd.port-offset`, failure detection), and that "Encryption using TLS is enabled by default for TCP-based transport stacks" (checked November 2026): https://www.keycloak.org/server/caching
- authentik 2025.10 release notes, removing the Redis dependency ("authentik no longer uses Redis at all") (checked November 2026): https://docs.goauthentik.io/releases/2025.10/
- authentik source `version/2026.8.5`, MFA response validation (including empty-response rejection), successful-validation continuation and remembered-MFA cookie handling (checked November 2026). The authentik `version/2026.8.5` sources (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L67-L166 , https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L368-L443
- Keycloak `26.8.2` bootstrap-admin-recovery.adoc L9-L11 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/bootstrap-admin-recovery.adoc#L9-L11
- Keycloak `26.8.2` flows.adoc L35 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L35-L35
- Keycloak `26.8.2` flows.adoc L37-L57 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L37-L57
- Keycloak `26.8.2` flows.adoc L135-L143 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L135-L143
- Keycloak `26.8.2` webauthn.adoc L19-L28 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L19-L28
- Keycloak `26.8.2` webauthn.adoc L51-L55 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L51-L55
- Keycloak `26.8.2` con-required-actions.adoc L6-L20 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/users/con-required-actions.adoc#L6-L20
- Keycloak `26.8.2` HttpOptions.java L14-L18 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L14-L18
- Keycloak `26.8.2` HttpOptions.java L32-L42 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L32-L42
- Keycloak `26.8.2` reverseproxy.adoc L122-L132 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L122-L132
- Keycloak `26.8.2` reverseproxy.adoc L72-L76, restricting network access to the proxy and `--proxy-trusted-addresses` as weak protection (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L72-L76
- Keycloak `26.8.2` reverseproxy.adoc L200-L242, trusted proxies: the accept-from-any-source default, the address formats, bracketed IPv6, the hostname deprecation and the CIDR examples (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L200-L242
- Keycloak `26.8.2` ProxyOptions.java L23-L26, the `proxy-trusted-addresses` description and its all-addresses-trusted default (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/ProxyOptions.java#L23-L26
- Keycloak `26.8.2` ProxyPropertyMappers.java L61-L67 and L71-L109, the `proxy-trusted-addresses` mapping and its address validator with the hostname deprecation warning (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/runtime/src/main/java/org/keycloak/quarkus/runtime/configuration/mappers/ProxyPropertyMappers.java#L61-L67 , https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/runtime/src/main/java/org/keycloak/quarkus/runtime/configuration/mappers/ProxyPropertyMappers.java#L71-L109
- authentik `version/2026.8.5` stages/authenticator_validate/models.py L15-L21 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/models.py#L15-L21
- authentik `version/2026.8.5` stages/authenticator_validate/models.py L45-L50 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/models.py#L45-L50
- authentik `version/2026.8.5` stage.py L279-L289 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L279-L289
- authentik `version/2026.8.5` stage.py L292-L317 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L292-L317
- authentik `version/2026.8.5` flows/models.py L254-L262 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/models.py#L254-L262
- authentik `version/2026.8.5` planner.py L339-L345 (checked November 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/planner.py#L339-L345
- curl `curl-8_23_0` _EXITCODES.md L7-L8 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L7-L8
- curl `curl-8_23_0` _EXITCODES.md L72-L74 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L72-L74
- curl `curl-8_23_0` _EXITCODES.md L111-L120 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L111-L120
- curl `curl-8_23_0` connect-timeout.md L19-L28 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/connect-timeout.md#L19-L28
- curl `curl-8_23_0` max-time.md L19-L23 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/max-time.md#L19-L23
- curl `curl-8_23_0` _ENVIRONMENT.md L3-L10 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_ENVIRONMENT.md#L3-L10
- curl `curl-8_23_0` _ENVIRONMENT.md L12-L29 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_ENVIRONMENT.md#L12-L29
- curl `curl-8_23_0` noproxy.md L18-L23 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23
- curl `curl-8_23_0` disable.md L18-L20 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L18-L20
- curl `curl-8_23_0` disable.md L5 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L5
- curl `curl-8_23_0` verbose.md L21-L25 (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/verbose.md#L21-L25
- Keycloak `26.8.2` otp-policies.adoc L17-L21 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L17-L21
- Keycloak `26.8.2` HttpOptions.java L20-L23 (checked November 2026): https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L20-L23
- Keycloak release records for 26.7.5, 26.8.0, 26.8.1 and 26.8.2, including their security fixes, the 26.8.0 Admin API v2 preview and SCIM API promotion, and the 26.8.2 record's empty body (checked November 2026): https://github.com/keycloak/keycloak/releases/tag/26.7.5 , https://github.com/keycloak/keycloak/releases/tag/26.8.0 , https://github.com/keycloak/keycloak/releases/tag/26.8.1 , https://github.com/keycloak/keycloak/releases/tag/26.8.2


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- keycloak-admin-cli: Keycloak Admin CLI (26.8.2)
- keycloak-source: Keycloak source (26.8.2)
- keycloak-releases: Keycloak release records (26.8.2)
- authentik: authentik source (version/2026.8.5)
- redis-removal: authentik Redis removal (2025.10)
- keycloak: Keycloak documentation (unknown)
- authentik-docs: authentik operational documentation (unknown)
- docker-engine: Docker Engine security documentation (unknown)
- nginx: nginx documentation (unknown)
- curl: curl documentation (curl-8_23_0)
- docker-engine-pinned: Docker Engine security documentation (4e9a5751518ed8223a8dcde53693badddd72604f)

Claims (full source mapping in the JSON block below):

- private-boundary (REASONED; keycloak, authentik-docs): Bind the IdP privately behind a reverse proxy; keep the database inside the same protected boundary.
- authentik-publications (REASONED; authentik): Shipped Compose publishes 9000:9000 and 9443:9443 by default without host addresses, exposing all host interfaces under Docker publishing defaults; it does not publish 9300.
- authentik-web-binds (REASONED; authentik): listen.http and listen.https default to [::]:9000 and [::]:9443 inside the container, independently of host publication.
- authentik-loopback (REASONED; authentik, authentik-docs): Replace the Compose ports list with 127.0.0.1:9000:9000 and 127.0.0.1:9443:9443; adding entries can retain old publications.
- production-tls (REASONED; keycloak): Keycloak production requires a secure channel; edge TLS termination needs a protected loopback or controlled private proxy hop.
- hostname-defaults (REASONED; keycloak): Production start requires explicit hostname or hostname-strict false; start-dev defaults hostname-strict false. Keep strict hostname resolution in production unless the proxy overwrites Host.
- http-listener (REASONED; keycloak, keycloak-source): The example starts Keycloak with HTTPS frontend/admin hostnames, xforwarded parsing and http-enabled=true for backend HTTP on default port 8080 on a protected proxy hop; the HTTPS port defaults to 8443. At 26.8.2, the HTTP listener option defaults false but is enabled by default in development mode. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.
- admin-hostname (REASONED; keycloak): hostname-admin selects the console/API hostname but does not restrict the Administration REST API through the frontend URL.
- admin-deny (REASONED; keycloak, nginx): Deny /admin/ on the public hostname at the proxy; the sample returns 404.
- master-realm (REASONED; keycloak): Restrict /realms/master/ by administrator source network while keeping application /realms/ exposed; by this guide's reading, not established at 26.8.2, a blanket denial locks out administrators.
- admin-login-route (REASONED; keycloak): Console API calls use hostname-admin; by this guide's reading, not established at 26.8.2, console authentication uses the frontend master realm. The private admin proxy also needs /admin/, /resources/ and /.well-known/, and /js/ for consoles that still load from it, which is not established for 26.8.2.
- forwarded-headers (REASONED; keycloak): Overwrite all five X-Forwarded-For/Proto/Host/Port/Prefix headers and Host; appending or passing client values permits spoofing.
- proxy-trust (REASONED; keycloak, keycloak-source): At 26.8.2, proxy-trusted-addresses defaults to trusting all addresses, so Keycloak accepts proxy headers from any source; if set, headers from other addresses are ignored. List the proxy's IP addresses or CIDR ranges, since hostnames are deprecated. It is weak protection because IP addresses can be spoofed, not a substitute for header overwriting.
- proxy-origin (REASONED; keycloak): Without proxy-headers, non-passthrough proxied requests that perform origin checks return 403 by default.
- setup-routing (REASONED; authentik): Before setup, authentik root redirects via /setup to /if/flow/initial-setup/; a fresh direct flow visit lacks the public setup marker and is denied.
- setup-claim (REASONED; authentik): Initial setup plans only when akadmin is absent or lacks a usable password, then prompts email/base URL/password, writes akadmin and logs in the visitor.
- setup-completion (REASONED; authentik): Completion records setup done, disables OOBE blueprints and requires a superuser; planning-time checks do not promise revocation of already-started sessions.
- setup-isolation (REASONED; authentik, authentik-docs): Keep both web ports and public proxy route closed to untrusted clients until setup is complete; use loopback or a private container network and confirm closure in a fresh session.
- bootstrap-inputs (REASONED; authentik): Before first startup, protected .env can provide AUTHENTIK_BOOTSTRAP_PASSWORD, PASSWORD_HASH or TOKEN; any nonempty input triggers bootstrap and successful blueprint application completes setup.
- bootstrap-lifecycle (REASONED; authentik): Hash form is validated; password forms set akadmin password and token form supplies an API token, not a browser password. Already-setup tenants are skipped, so these inputs are not rotation.
- bootstrap-cleanup (REASONED; authentik): Verify bootstrap and setup closure before publication, then remove the bootstrap secret from the startup environment and protect file/container-inspection access.
- keycloak-bootstrap (REASONED; keycloak, keycloak-source): Keycloak bootstrap admin is temporary and needs manual removal after establishing permanent, more secure, MFA-protected admin access (this guide's requirement); this guide infers from the manual-removal instruction that it does not expire on its own. MFA protection requires a factor in the authentication flow, not only enrolment.
- keycloak-management (REASONED; keycloak): Enabled Keycloak health and metrics use management port 9000; keep it private and use /health/ready for the orchestrator.
- management-mtls (REASONED; keycloak): https-management-client-auth accepts none/request/required and inherits HTTP settings; this plaintext topology needs management TLS credentials and trust before client certificates can authenticate it.
- authentik-metrics (REASONED; authentik): At version/2026.8.5, the Rust core metrics listener uses plain HTTP with default [::]:9300, and the main Dockerfile ships the Rust binary run by ak; whether published images were built from it is NOT ESTABLISHED. The shipped Compose file does not publish 9300, but the container-network listener still needs restriction.
- authentik-go-metrics (REASONED; authentik): At version/2026.8.5, a Go web server metrics listener is also present: cmd/server calls WebServer.Start, which calls runMetricsServer per listen.metrics address. A version/2026.8.3 search, not repeated since, found no image or release build of cmd/server; a developer debug launch targets it. The main Dockerfile ships the Rust binary; whether published images were built from it is NOT ESTABLISHED.
- authentik-metrics-startup (REASONED; authentik): At version/2026.8.5, the Rust main starts the metrics server before the per-mode dispatch (healthcheck exits earlier), including proxy mode in proxy-feature builds; Server and AllInOne store the server handle, Worker and AllInOne the worker handles. Whether the published image was built from the tree's Dockerfile is NOT ESTABLISHED.
- worker-outpost-metrics (REASONED; authentik): At version/2026.8.5, worker startup uses the same Rust metrics server as server mode; its handler serves Prometheus metrics on listen.metrics (default [::]:9300) via plain HTTP, with no authentication layer in the router wrapper. The LDAP outpost builds its metrics router with a bare Prometheus handler at /metrics and serves it on each metrics listen address and a Unix socket; section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced. Restrict to monitoring clients.
- keycloak-mfa (REASONED; keycloak, keycloak-source): Enrol administrator TOTP or WebAuthn and require the factor in the realm authentication flow. When Keycloak's default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. A Required second factor can instead be enrolled during authentication without proving possession of a preexisting factor, so test an administrator with no registered factor and inspect the flow.
- brute-force-default (REASONED; keycloak): Keycloak brute-force detection is disabled by default and must be enabled per realm.
- redirect-wildcards (REASONED; keycloak): Keycloak permits trailing redirect-URI wildcards and bare *; deliberately register exact URIs instead.
- docker-socket (REASONED; authentik-docs, authentik): authentik Compose mounts the worker Docker socket for outpost management; use a socket proxy or remove the mount and manage outposts manually.
- cache-ports (REASONED; keycloak): Keycloak cache transport uses 7800 and failure detection 57800; TCP stacks enable TLS by default but still need private reachability.
- redis-history (REASONED; redis-removal): Redis 6379 is relevant to older authentik: tasks moved in 2025.8 and remaining uses in 2025.10, which removes Redis entirely.
- verify-setup (REASONED; authentik): On a disposable instance, complete anonymous root-to-setup flow and confirm akadmin login; after setup or password bootstrap, fresh /setup visits must return to authentication. Source tests were read, not run.
- verify-publication (REASONED; authentik): Compare exposed and loopback publications: untrusted clients lose setup access while a local browser still reaches it. Neither configuration publishes 9300.
- verify-inventory (REASONED; authentik, keycloak): Inspect all listeners plus Compose publications: host ss misses container namespaces, Compose ps sees one project, and proxy 443 publication is expected.
- verify-issuer (REASONED; keycloak): From outside allowed networks, application-realm discovery must print the expected issuer before negative route checks are interpreted; an arbitrary 200 is insufficient.
- verify-console (REASONED; keycloak, nginx): Public /admin/master/console/ must return 404; 2xx, 3xx, 401 and 403 do not show that the console path is closed.
- verify-admin-api (REASONED; keycloak, nginx): Public /admin/realms/master/users must return 404; 401 means the API still answers and requests a token.
- verify-master (REASONED; keycloak, nginx): Outside allowed sources, master-realm discovery must return 403; 200 exposes it and 404 indicates blanket denial. Review effective locations beyond these sampled routes.
- verify-admin-login (REASONED; keycloak): An allowed administrator must complete a real login through the private console and observe where it authenticates, which by this guide's reading, not established at 26.8.2, is the frontend master realm; the network restriction on that path must admit the administrator, and outside sources must fail.
- verify-direct-ports (REASONED; keycloak, authentik, curl, keycloak-source): Probe 8080/8443/9000/9300/9443 directly: curl exit 0 reports a completed operation, 7 reports a connection failure, and 28 is an inconclusive timeout requiring full diagnostics to distinguish accepted-then-stalled from unreachable. Treat a connection failure as the desired isolation outcome only after checking the diagnostic and target; this guide infers that exits 52 and 56 follow an accepted connection, so a listener is reachable. Other exits require diagnostic review. The connection and full-transfer deadlines differ. The checks remain REASONED expectations, not observed outcomes.
- verify-bootstrap-removal (REASONED; keycloak, keycloak-admin-cli): Look up the bootstrap username with exact=true rather than a user list, whose 100-result default is not established at 26.8.2, inspect the returned username, and separately check bootstrap service accounts. Keycloak documents non-exact matching for its -q q=username: filter; this guide keeps the -q order (exact=true first) as defensive advice based on a report, not documented ordering behaviour.
- verify-address-coverage (REASONED; keycloak, authentik-docs): Repeat external checks for every public IPv4/IPv6 address and the origin; private admin, database and outposts need separate checks, and the listed ports are not a full inventory.
- authentik-mfa (REASONED; authentik-docs, authentik): authentik has TOTP and WebAuthn setup stages; enrol a phishing-resistant administrator factor before connecting the first app and require it through an Authenticator Validate stage bound to the authentication flow (this guide's requirement; the cited sources do not state this ordering). A registered device alone does not establish the flow binding. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The pinned validate-stage and flow-binding sources support these behaviours but do not establish an administrator-specific factor policy.
- authentik-admin-boundary (REASONED; authentik): At version/2026.8.5, /if/admin/, /if/user/ and flows share core routing. This guide assesses that authentik has no equivalent to hostname-admin: the cited configuration, Go startup and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. The permission boundary remains unestablished.
- authentik-admin-listeners (REASONED; authentik): At version/2026.8.5, defaults are HTTP [::]:9000, HTTPS [::]:9443 and metrics [::]:9300; Go startup adds these configured listeners and a Unix socket, and its plain HTTP, HTTPS and Unix listeners share the application proxy router after outpost handling. These files show shared routing, not a separate admin port, and do not prove which listeners a deployed build starts.
- authentik-admin-interface (REASONED; authentik): At version/2026.8.5, both interface routes redirect authenticated external, service-account and internal-service-account users to a default app or deny them; other requests fall through. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.
- authentik-admin-api-mount (REASONED; authentik): At version/2026.8.5, API v3 registers application API routes, including core users, groups, tokens and admin authenticators. The root URL configuration mounts each app under the web path; the API app mounts api/ and then v3/, so the v3 router is at &lt;web path&gt;api/v3/, /api/v3/ by default, matching the Go client's api/v3 prefix. Endpoint permission wiring is not established by these files.
- authentik-admin-api-auth (REASONED; authentik): At version/2026.8.5, TokenAuthentication recognizes API-intent tokens, API-scoped OAuth tokens, the managed-outpost secret and IPC key; it rejects inactive users and unrecognized credentials, but absent or unsupported authentication can return no user. This does not establish session authentication or every endpoint adopting this class.
- authentik-admin-rbac (REASONED; authentik): At version/2026.8.5, ObjectPermissions' request check passes object-lookup requests (its comment leaves view checks to ObjectFilter, writes to the object check) and permits configured creation without add permission; the object check accepts global permissions or configured ownership before delegating. HasPermission checks user.has_perms; endpoint wiring and permission boundary stay unestablished.
- authentik-admin-proxy (REASONED; authentik): Build any network boundary around authentik administration at the proxy using path restrictions; identify and test required paths for the deployed version and maintain the list. This guide assesses that the UI is not designed around this separation and path-based separation is difficult to maintain; this is not a vendor-supported recipe, and the cited files give no complete path list.
- authentik-admin-paths (REASONED; authentik): At version/2026.8.5, core URLs show /if/admin/, /if/user/, flows, HTTP admin-template fallbacks at /ws/outpost/&lt;uuid:pk&gt;/ and /ws/client/, and a /ws/client/ websocket route wrapped in authentication middleware. With the API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization.
- authentik-rust-listeners (REASONED; authentik): At version/2026.8.5, the main Dockerfile ships the Rust binary run by ak. Server mode runs gunicorn on a Unix socket and serves one router over HTTP on listen.http, rustls on listen.https and a Unix socket, sending embedded-outpost apps to the outpost and the rest via the core router to gunicorn. Worker mode serves health checks on listen.http. Deployed topology beyond Compose is NOT ESTABLISHED.
- authentik-api-defaults (REASONED; authentik): At version/2026.8.5, REST framework defaults are TokenAuthentication then SessionAuthentication, ObjectPermissions and an ObjectFilter backend; settings modules can update them, and a version/2026.8.3 search, not repeated since, found no app settings module doing so. Users and groups add AgentAuth; the flow executor uses AllowAny. SessionAuthentication and deployment overrides are NOT ESTABLISHED.
- authentik-admin-websockets (REASONED; authentik): At version/2026.8.5, the websocket modules a version/2026.8.3 search found give /ws/client/, /ws/outpost/&lt;uuid:pk&gt;/, /ws/rac/&lt;str:token&gt;/ and /ws/outpost_rac/&lt;str:channel&gt;/ under the web path; others are not established. The /ws/client/ route resolves a session or anonymous user and accepts every connection; the RAC client consumer on /ws/rac/ accepts, then denies tokens not bound to the session.
- authentik-outpost-websockets (REASONED; authentik): At version/2026.8.5, under the configured web path (default / shown), the /ws/outpost/ and /ws/outpost_rac/ websocket routes deny a connection unless TokenAuthentication accepts its bearer token; /ws/outpost/ also needs outpost view permission, while /ws/outpost_rac/'s RAC outpost consumer accepts with no outpost-specific check.
- authentik-admin-api-shared (REASONED; authentik): At version/2026.8.5, the API router registers the flow executor at flows/executor/&lt;slug:flow_slug&gt;/ with AllowAny, the API schema names that path's GET flows_executor_get, and the flow interface calls flowsExecutorGet, read here as that GET's generated client method, so this guide infers refusing the whole API prefix would break login.
- authentik-admin-static-paths (REASONED; authentik): At version/2026.8.5, the Rust static router also serves /if/admin/assets/ under the configured web path (shown with the default /) alongside the user, flow and RAC interface assets. Path lists from the routing tables this guide read are bounded by those tables; complete path coverage remains open.
- verify-mfa-password (REASONED; keycloak, authentik-docs, authentik, keycloak-source): For both providers, open a fresh session with only the administrator password and confirm access is refused after factor enforcement. This guide assesses that an already-enrolled administrator's password-only refusal does not distinguish enrolment from enforcement; test a user with no registered factor and inspect the flow or stage settings. Keycloak's default conditional 2FA, when reached (a successful Cookie execution skips it), prompts for configured OTP unless passwordless WebAuthn already authenticated the user; the default flow's WebAuthn Authenticator execution is disabled by default; and a Required factor the user lacks can be enrolled during authentication. At authentik version/2026.8.5, the unconfigured-device action defaults to SKIP; DENY refuses a user with no allowed device. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. Bind the validation stage to the authentication flow.
- management-auth-default (REASONED; keycloak): In this plain-HTTP Keycloak topology no HTTP client authentication is configured, so inherited management client authentication is usually none; required needs management TLS credentials and trust first.
- docker-socket-scope (REASONED; authentik-docs, authentik, docker-engine, docker-engine-pinned): Docker's daemon requires root unless rootless (daemon and containers run non-root); only trusted users should control it. For authentik's shipped Compose worker socket, check daemon type and restrict access: this guide assesses ordinary rootful access as host-root-equivalent and rootless blast radius as the daemon user and what it can access; sources do not directly demonstrate either assessment.
- outpost-boundaries (REASONED; authentik-docs, authentik): At version/2026.8.5, authentik supports Proxy, LDAP, RADIUS and RAC outposts. The embedded Proxy outpost runs in the main server and shares ports 9000 and 9443 rather than opening another port; managed or manually deployed outposts can run elsewhere. This guide requires separate exposure checks for each deployed outpost and assesses that its Verify probes do not demonstrate them.
- outpost-proxy-image (REASONED; authentik): At version/2026.8.5, proxy.Dockerfile, titled the authentik proxy outpost image, builds the Rust authentik binary with only the proxy feature, has no go build step, copies only that binary and runs /authentik proxy. This guide infers that an image built from it runs the Rust proxy outpost, not the cited Go proxy code; whether published images were built from it is NOT ESTABLISHED.
- outpost-proxy-listeners (REASONED; authentik): At version/2026.8.5, the authentik proxy subcommand starts the Rust proxy outpost, which serves plain HTTP on each listen.http address and rustls on each listen.https address unless it is the embedded outpost; Rust startup schedules the metrics server on listen.metrics before mode dispatch. Pinned defaults are [::]:9000, [::]:9443 and [::]:9300, and proxy.Dockerfile exposes 9000, 9300 and 9443.
- outpost-deployment-listeners (REASONED; authentik): At version/2026.8.5, the pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. The Docker controller maps the outpost's ports to the host unless docker_map_ports is false; docker_map_ports defaults to true. The Kubernetes controller reconciles Deployment and Service objects. LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced.
- verify-proxy-neutralization (REASONED; keycloak, curl): Run external probes outside every allowed network; unset HTTP/HTTPS/ALL/NO_PROXY variables in both cases and use curl -q --noproxy '*' to bypass proxies and curlrc, which this guide assesses could otherwise make blocked endpoints appear reachable through allowed egress. Curl's HTTP proxy environment variable is lowercase only; -q must be curl's first option.
- verify-authentik-routes (REASONED; authentik-docs, authentik): The fenced paths are Keycloak-specific; the exclusion of Keycloak paths from authentik is this guide's inference from the fetched route files, not an exhaustive route proof. For authentik, use a deployed application's actual OAuth2 discovery URL as the positive control and confirm its configured issuer. A responding status alone is not the positive-control pass condition.
- verify-authentik-admin-routes (REASONED; authentik-docs, authentik): For authentik, an untrusted client must not reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request.
- verify-authentik-login-api (REASONED; authentik): Do not refuse the whole authentik API prefix without tracing login dependencies; confirm an ordinary user can still complete login. At version/2026.8.5 the v3 router is at &lt;web path&gt;api/v3/ (/api/v3/ by default) and registers the flow executor with AllowAny; the flow interface calls flowsExecutorGet, taken here as its generated client method, so this guide infers that login uses the API prefix.
- verify-authentik-oauth2-routes (REASONED; authentik): At version/2026.8.5 the installed OAuth2 app mounts its urls module, which defines the per-application discovery suffix, at application/o/ and urls_root at the root; the root URL module mounts installed authentik apps' mountpoints under the web path, so the prefix is &lt;web path&gt;application/o/, /application/o/ by default. The issuer can be global or per-provider; /if/admin/ is a core route.
- admin-factor-order (REASONED; keycloak, authentik-docs, keycloak-source, authentik): Enrol a phishing-resistant factor on the administrator account of either provider before connecting the first application and enforce it in the flow (this guide's requirement; the cited sources do not state this ordering). Keycloak documents Required executions; authentik version/2026.8.5 binds ordered stages to flows, but the cited files do not establish an administrator-specific factor policy.
- keycloak-http-opt-in (REASONED; keycloak, keycloak-source): In the production example, backend plain HTTP on default port 8080 exists only when explicitly enabled with --http-enabled=true; confine that hop to loopback or a controlled private segment. At 26.8.2, the HTTP listener option defaults false but is enabled by default in development mode, and HTTPS defaults to port 8443. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.
- idp-maintenance (REASONED; keycloak, authentik-docs, authentik, keycloak-source): This guide requires patching, tested backups and keeping a self-hosted identity provider available (the cited files prescribe no cadence) and assesses that a compromised or unavailable provider takes its dependent services with it. The cited sources establish no complete Keycloak or authentik backup procedure, authentik upgrade procedure, universal maintenance cadence or tested restore.
- keycloak-security-fixes (REASONED; keycloak-releases): The 26.7.5 and 26.8.1 records list section 6's fixes: 26.8.1 fixes CVE-2026-94218 (2FA setup enforcement bypass) and CVE-2026-96445 (Conditional OTP skip headers on untrusted proxy paths); 26.7.5 fixes brute-force lockout bypasses CVE-2026-16103 and CVE-2026-88770, not in the 26.8.x records. The 26.8.2 record is empty. Run 26.8.1 or later; each bypass's detail and backports are not established.
- keycloak-admin-api-v2 (REASONED; keycloak-releases): Keycloak 26.8.0 promotes the Client Admin API v2 to preview, enabled with --features=preview or --features=client-admin-api:v2; the path it is served under at 26.8.2, and so whether the public /admin/ refusal covers it, are not established.
- keycloak-scim-api (REASONED; keycloak-releases, keycloak): Keycloak 26.8.0 promotes the SCIM API, for managing a realm's users and groups, to supported. The server administration guide served on 2026-11-05 (26.8.1 page links) gives its base URL under /realms/, ending /scim/v2, enabled per server and realm, needing a bearer token. This guide infers an enabled realm serves it on the public hostname; its 26.8.2 default and path are not established.

````json
{
  "schema": 1,
  "checked": "2026-11-05",
  "documentation_checked": "2026-09",
  "body_sha256": "79832298dfada5ca705cb835741acda822b85de7a994dd7455bfa35102fc381b",
  "components": {
    "keycloak-admin-cli": {
      "name": "Keycloak Admin CLI",
      "basis": "26.8.2",
      "sources": {
        "s8b4e40148629": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/admin-cli.adoc#L1034-L1045"
      }
    },
    "keycloak-source": {
      "name": "Keycloak source",
      "basis": "26.8.2",
      "sources": {
        "sd5a9fd571726": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/bootstrap-admin-recovery.adoc#L9-L11",
        "se54a2a6e7d47": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L35-L35",
        "sff5c9a23ec46": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L37-L57",
        "s277571a617ec": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/flows.adoc#L135-L143",
        "s6e859a060525": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L19-L28",
        "sdc09746a23d8": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L51-L55",
        "sde43d0e31c0f": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/users/con-required-actions.adoc#L6-L20",
        "sa452e5c860cd": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L14-L18",
        "s32a00c2c8803": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L32-L42",
        "sb3476e7a2eb2": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L122-L132",
        "s3f7c345f457f": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L17-L21",
        "s7fdfa4997898": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L20-L23",
        "s94317d53483b": "https://github.com/keycloak/keycloak/blob/26.8.2/SECURITY.md#L42-L48",
        "s14164b9cc6c3": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/importExport.adoc#L11-L16",
        "scf439f41b910": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L72-L76",
        "sa0feb9279213": "https://github.com/keycloak/keycloak/blob/26.8.2/docs/guides/server/reverseproxy.adoc#L200-L242",
        "s5261cce9086f": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/config-api/src/main/java/org/keycloak/config/ProxyOptions.java#L23-L26",
        "s7d1570c7fded": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/runtime/src/main/java/org/keycloak/quarkus/runtime/configuration/mappers/ProxyPropertyMappers.java#L61-L67",
        "s217fa09da7aa": "https://github.com/keycloak/keycloak/blob/26.8.2/quarkus/runtime/src/main/java/org/keycloak/quarkus/runtime/configuration/mappers/ProxyPropertyMappers.java#L71-L109"
      }
    },
    "keycloak-releases": {
      "name": "Keycloak release records",
      "basis": "26.8.2",
      "sources": {
        "s32d0f0981b58": "https://github.com/keycloak/keycloak/releases/tag/26.7.5",
        "s46d0047d5606": "https://github.com/keycloak/keycloak/releases/tag/26.8.0",
        "sd570d95abe70": "https://github.com/keycloak/keycloak/releases/tag/26.8.1",
        "s614ddc99af91": "https://github.com/keycloak/keycloak/releases/tag/26.8.2"
      }
    },
    "authentik": {
      "name": "authentik source",
      "basis": "version/2026.8.5",
      "sources": {
        "s2a37351e0dbc": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/setup/signals.py#L18-L48",
        "sbfdadaefea47": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/setup/views.py#L35-L92",
        "s01be08361cc2": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/tests/test_setup.py#L168-L245",
        "s67916683010a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/tests/test_setup.py#L26-L130",
        "s746914604076": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L59-L70",
        "s313f1f9b5bc9": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L36-L75",
        "s85e90df8c571": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/views/interface.py#L44-L51",
        "s0f24d2fd939d": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/models.py#L183-L187",
        "s1153450d2162": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/planner.py#L263-L292",
        "s189836c36e3a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/views/executor.py#L175-L196",
        "se669fb431f33": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/default.yml#L36-L48",
        "seebef88f2110": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/blueprints/default/flow-oobe.yaml#L8-L194",
        "s4fc8280e760f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/metrics/mod.rs#L70-L100",
        "sed8d69a749a7": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/main.rs#L99-L122",
        "sa2dcdc13cd29": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/metrics/handlers.rs#L12-L42",
        "s5c36281a2a21": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-axum/src/router.rs#L36-L59",
        "sf577784d5ebc": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/ak/metrics.go#L18-L72",
        "sb8dece660959": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/ldap/ldap.go#L91-L121",
        "s0350a6463f9c": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/web/metrics.go#L22-L52",
        "scc60a0e302d1": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/compose.yml#L1-L67",
        "s2986fcb4cb32": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L67-L166",
        "s16ad051165b7": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L368-L443",
        "se89f1e7b7d18": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/models.py#L15-L21",
        "sf19de9022fee": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/models.py#L45-L50",
        "s77bfc5116d72": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L279-L289",
        "sdf8b8d567281": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_validate/stage.py#L292-L317",
        "s68ce378d011e": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/models.py#L254-L262",
        "s6500fae4a5ac": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/planner.py#L339-L345",
        "s506b3d80d9ce": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_totp/models.py#L29-L44",
        "sd5b24af3593a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/stages/authenticator_webauthn/models.py#L90-L113",
        "s6be1839a0a33": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/models.py#L53-L85",
        "s6ee73dbd270c": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/models.py#L99-L105",
        "s741c951134bd": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/index.mdx#L6-L13",
        "s0249923fde2f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/index.mdx#L30-L48",
        "sf4642b40524f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/website/docs/add-secure-apps/outposts/embedded/embedded.mdx#L5-L15",
        "s0c4d3f60ff27": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/proxyv2/proxyv2.go#L172-L202",
        "s030a7cc6a274": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/outpost/radius/radius.go#L100-L125",
        "s25612b8e4bc3": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/urls.py#L53-L63",
        "s1b0b1b6332d8": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/models.py#L115-L122",
        "s42b24ec40c5a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/models.py#L365-L378",
        "s073e329f067a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/urls.py#L18-L48",
        "s304feb3be14f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/oauth2/apps.py#L12-L15",
        "s37a8db510590": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/utils/reflection.py#L46-L52",
        "s2d86a3e9d60d": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L83-L108",
        "s8d3ff0842282": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L612-L613",
        "sceae009a9d08": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/SECURITY.md#L25-L32",
        "s63fcd0ce5a18": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/controllers/docker.py#L218-L230",
        "sb24757cb27e6": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/controllers/kubernetes.py#L65-L88",
        "s8012ab258605": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/config/struct.go#L53-L62",
        "s70d2fe895b7b": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/web.go#L132-L183",
        "s63d78b9d40d8": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/web.go#L229-L288",
        "s6c3afec54d75": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/internal/web/proxy.go#L47-L127",
        "s169ffaaa70fc": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/views/interface.py#L54-L89",
        "s98f257d3ede1": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/urls.py#L36-L112",
        "s2cdcdb3b510b": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/api/v3/urls.py#L18-L58",
        "s68d603b9d5bc": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/api/authentication.py#L33-L166",
        "s9f2178a64542": "https://github.com/goauthentik/authentik/blob/4ec0d19b98da3c329781894cd550da95d3033954/authentik/rbac/permissions.py#L15-L60",
        "s6e40a30f1d99": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/main.rs#L57-L135",
        "sdacc5da217ab": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/cmd/server/server.go#L25-L73",
        "s675653f9e0f8": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/Dockerfile#L126-L142",
        "sd3e2ba0c6343": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/Dockerfile#L234-L252",
        "s8329bf6c67f8": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L16-L33",
        "s2dc55e93d595": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L92-L94",
        "s5af5d9143036": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/mod.rs#L86-L106",
        "s3e1090638af8": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/mod.rs#L260-L352",
        "s14e51acafd6f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/core.rs#L153-L155",
        "s906b273aa104": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/core.rs#L277-L320",
        "sa01f6c27bc59": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-axum/src/server.rs#L22-L170",
        "sdb8c87fa0cfc": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/worker/mod.rs#L347-L361",
        "s949377fe0d94": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/worker/healthcheck.rs#L66-L76",
        "sb8906abab13c": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/schema.rs#L203-L214",
        "s1626a6c0776a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/internal/web/web_tls.go#L46-L72",
        "s7c88d077f919": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L240-L252",
        "s12fcc19f34ee": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L320-L339",
        "s19f8c9e313eb": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/settings.py#L566-L609",
        "sc84a7d5db870": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/api/apps.py#L6-L13",
        "sa06907a58b4e": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/api/urls.py#L7-L9",
        "sf668b16f361a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/default.yml#L162-L166",
        "s62327707b202": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/websocket.py#L14-L34",
        "s9e012ed398d4": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/asgi.py#L75-L83",
        "s5b1985e0936f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/asgi_middleware.py#L42-L84",
        "s6d275572bf62": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/root/ws/consumer.py#L38-L52",
        "sf02ba388bb2f": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/urls.py#L16-L23",
        "s02f5150b41d1": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/channels.py#L13-L43",
        "s369c9cffd8f5": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/outposts/consumer.py#L73-L83",
        "s4b92525713bb": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/urls.py#L30-L43",
        "s6b20bb333911": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/consumer_client.py#L63-L96",
        "s033849961834": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/urls.py#L36-L50",
        "s3ea4b10861b1": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/flows/views/executor.py#L101-L104",
        "s1ff44bd506fd": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/web/src/flow/FlowExecutor.ts#L224-L228",
        "s247ca79b6f6c": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/server/static.rs#L159-L168",
        "s402352aa9811": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/api/users.py#L650-L654",
        "sb2bc7f868825": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/core/api/groups.py#L406-L410",
        "s07817f9dd888": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/ak#L35-L54",
        "s430f8fb6719e": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/.vscode/launch.json#L37-L42",
        "s331ad7f37dac": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/providers/rac/consumer_outpost.py#L14-L16",
        "s9eece0a5a170": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/schema.yml#L9288-L9290",
        "sb69f89fd29f8": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/mod.rs#L24-L24",
        "s3d85bc9743c4": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/packages/ak-common/src/config/mod.rs#L71-L89",
        "s86eb476b495a": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/config.py#L26-L28",
        "s3d8996ccb579": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/authentik/lib/config.py#L86-L111",
        "s82a97fe0acf2": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/proxy.Dockerfile#L29-L42",
        "s9082a2dbb6c5": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/lifecycle/container/proxy.Dockerfile#L51-L78",
        "s4a31ab9f5ec9": "https://github.com/goauthentik/authentik/blob/version/2026.8.5/src/outpost/proxy/mod.rs#L44-L119"
      }
    },
    "redis-removal": {
      "name": "authentik Redis removal",
      "basis": "2025.10",
      "sources": {
        "seaa0a9896153": "https://docs.goauthentik.io/releases/2025.10/"
      }
    },
    "keycloak": {
      "name": "Keycloak documentation",
      "basis": "unknown",
      "sources": {
        "sefec90245fa1": "https://www.keycloak.org/docs/latest/server_admin/index.html",
        "sbbd55dcb81cd": "https://www.keycloak.org/server/bootstrap-admin-recovery",
        "s44e24ad4e579": "https://www.keycloak.org/server/caching",
        "s2f5f079c5e00": "https://www.keycloak.org/server/configuration-production",
        "se5538391cf9f": "https://www.keycloak.org/server/hostname",
        "s4b5df6f4ef2e": "https://www.keycloak.org/server/management-interface",
        "sffc6123bea5c": "https://www.keycloak.org/server/reverseproxy"
      }
    },
    "authentik-docs": {
      "name": "authentik operational documentation",
      "basis": "unknown",
      "sources": {
        "sb44156cde339": "https://docs.goauthentik.io/install-config/install/docker-compose/"
      }
    },
    "docker-engine": {
      "name": "Docker Engine security documentation",
      "basis": "unknown",
      "sources": {
        "s18f59818e451": "https://docs.docker.com/engine/security/",
        "s7e61efb4dd59": "https://docs.docker.com/engine/security/rootless/"
      }
    },
    "nginx": {
      "name": "nginx documentation",
      "basis": "unknown",
      "sources": {
        "sf7458f108aca": "https://nginx.org/en/docs/http/ngx_http_core_module.html#location",
        "s8d8f3323b468": "https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return"
      }
    },
    "curl": {
      "name": "curl documentation",
      "basis": "curl-8_23_0",
      "sources": {
        "s9d0c5b92e9a4": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L23-L24",
        "s25c3e6e61c14": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L7-L8",
        "s9c78f229c8ba": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L72-L74",
        "sc7945d33c78d": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L111-L120",
        "s977c1ef288cc": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/connect-timeout.md#L19-L28",
        "sc39d43ba6e58": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/max-time.md#L19-L23",
        "sde07f1edf2dc": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_ENVIRONMENT.md#L3-L10",
        "s75e3807878ff": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_ENVIRONMENT.md#L12-L29",
        "s508454c45cf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23",
        "s2278b86c08a6": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L18-L20",
        "sc8658f8a2e89": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L5",
        "s9380fc35e98e": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/verbose.md#L21-L25"
      }
    },
    "docker-engine-pinned": {
      "name": "Docker Engine security documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "secebea1a69ab": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112",
        "s8eab393a61c6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/rootless/_index.md#L8-L21"
      }
    }
  },
  "claims": {
    "private-boundary": {"text": "Bind the IdP privately behind a reverse proxy; keep the database inside the same protected boundary.", "components": ["keycloak", "authentik-docs"], "sources": ["keycloak:s2f5f079c5e00", "authentik-docs:sb44156cde339"], "status": "REASONED"},
    "authentik-publications": {"text": "Shipped Compose publishes 9000:9000 and 9443:9443 by default without host addresses, exposing all host interfaces under Docker publishing defaults; it does not publish 9300.", "components": ["authentik"], "sources": ["authentik:scc60a0e302d1"], "status": "REASONED"},
    "authentik-web-binds": {"text": "listen.http and listen.https default to [::]:9000 and [::]:9443 inside the container, independently of host publication.", "components": ["authentik"], "sources": ["authentik:se669fb431f33"], "status": "REASONED"},
    "authentik-loopback": {"text": "Replace the Compose ports list with 127.0.0.1:9000:9000 and 127.0.0.1:9443:9443; adding entries can retain old publications.", "components": ["authentik", "authentik-docs"], "sources": ["authentik:scc60a0e302d1", "authentik-docs:sb44156cde339"], "status": "REASONED"},
    "production-tls": {"text": "Keycloak production requires a secure channel; edge TLS termination needs a protected loopback or controlled private proxy hop.", "components": ["keycloak"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "hostname-defaults": {"text": "Production start requires explicit hostname or hostname-strict false; start-dev defaults hostname-strict false. Keep strict hostname resolution in production unless the proxy overwrites Host.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f"], "status": "REASONED"},
    "http-listener": {"text": "The example starts Keycloak with HTTPS frontend/admin hostnames, xforwarded parsing and http-enabled=true for backend HTTP on default port 8080 on a protected proxy hop; the HTTPS port defaults to 8443. At 26.8.2, the HTTP listener option defaults false but is enabled by default in development mode. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.", "components": ["keycloak", "keycloak-source"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c", "keycloak-source:sa452e5c860cd", "keycloak-source:s32a00c2c8803", "keycloak-source:sb3476e7a2eb2", "keycloak-source:s7fdfa4997898"], "status": "REASONED"},
    "admin-hostname": {"text": "hostname-admin selects the console/API hostname but does not restrict the Administration REST API through the frontend URL.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f"], "status": "REASONED"},
    "admin-deny": {"text": "Deny /admin/ on the public hostname at the proxy; the sample returns 404.", "components": ["keycloak", "nginx"], "sources": ["keycloak:sffc6123bea5c", "nginx:s8d8f3323b468"], "status": "REASONED"},
    "master-realm": {"text": "Restrict /realms/master/ by administrator source network while keeping application /realms/ exposed; by this guide's reading, not established at 26.8.2, a blanket denial locks out administrators.", "components": ["keycloak"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "admin-login-route": {"text": "Console API calls use hostname-admin; by this guide's reading, not established at 26.8.2, console authentication uses the frontend master realm. The private admin proxy also needs /admin/, /resources/ and /.well-known/, and /js/ for consoles that still load from it, which is not established for 26.8.2.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "forwarded-headers": {"text": "Overwrite all five X-Forwarded-For/Proto/Host/Port/Prefix headers and Host; appending or passing client values permits spoofing.", "components": ["keycloak"], "sources": ["keycloak:sffc6123bea5c"], "status": "REASONED"},
    "proxy-trust": {"text": "At 26.8.2, proxy-trusted-addresses defaults to trusting all addresses, so Keycloak accepts proxy headers from any source; if set, headers from other addresses are ignored. List the proxy's IP addresses or CIDR ranges, since hostnames are deprecated. It is weak protection because IP addresses can be spoofed, not a substitute for header overwriting.", "components": ["keycloak", "keycloak-source"], "sources": ["keycloak:sffc6123bea5c", "keycloak-source:scf439f41b910", "keycloak-source:sa0feb9279213", "keycloak-source:s5261cce9086f", "keycloak-source:s7d1570c7fded", "keycloak-source:s217fa09da7aa"], "status": "REASONED"},
    "proxy-origin": {"text": "Without proxy-headers, non-passthrough proxied requests that perform origin checks return 403 by default.", "components": ["keycloak"], "sources": ["keycloak:sffc6123bea5c"], "status": "REASONED"},
    "setup-routing": {"text": "Before setup, authentik root redirects via /setup to /if/flow/initial-setup/; a fresh direct flow visit lacks the public setup marker and is denied.", "components": ["authentik"], "sources": ["authentik:s85e90df8c571", "authentik:s746914604076", "authentik:sbfdadaefea47", "authentik:seebef88f2110"], "status": "REASONED"},
    "setup-claim": {"text": "Initial setup plans only when akadmin is absent or lacks a usable password, then prompts email/base URL/password, writes akadmin and logs in the visitor.", "components": ["authentik"], "sources": ["authentik:seebef88f2110"], "status": "REASONED"},
    "setup-completion": {"text": "Completion records setup done, disables OOBE blueprints and requires a superuser; planning-time checks do not promise revocation of already-started sessions.", "components": ["authentik"], "sources": ["authentik:sbfdadaefea47", "authentik:s0f24d2fd939d", "authentik:s1153450d2162", "authentik:s189836c36e3a"], "status": "REASONED"},
    "setup-isolation": {"text": "Keep both web ports and public proxy route closed to untrusted clients until setup is complete; use loopback or a private container network and confirm closure in a fresh session.", "components": ["authentik", "authentik-docs"], "sources": ["authentik:scc60a0e302d1", "authentik:sbfdadaefea47", "authentik-docs:sb44156cde339"], "status": "REASONED"},
    "bootstrap-inputs": {"text": "Before first startup, protected .env can provide AUTHENTIK_BOOTSTRAP_PASSWORD, PASSWORD_HASH or TOKEN; any nonempty input triggers bootstrap and successful blueprint application completes setup.", "components": ["authentik"], "sources": ["authentik:s2a37351e0dbc", "authentik:scc60a0e302d1"], "status": "REASONED"},
    "bootstrap-lifecycle": {"text": "Hash form is validated; password forms set akadmin password and token form supplies an API token, not a browser password. Already-setup tenants are skipped, so these inputs are not rotation.", "components": ["authentik"], "sources": ["authentik:s2a37351e0dbc", "authentik:s01be08361cc2"], "status": "REASONED"},
    "bootstrap-cleanup": {"text": "Verify bootstrap and setup closure before publication, then remove the bootstrap secret from the startup environment and protect file/container-inspection access.", "components": ["authentik"], "sources": ["authentik:s2a37351e0dbc", "authentik:scc60a0e302d1"], "status": "REASONED"},
    "keycloak-bootstrap": {"text": "Keycloak bootstrap admin is temporary and needs manual removal after establishing permanent, more secure, MFA-protected admin access (this guide's requirement); this guide infers from the manual-removal instruction that it does not expire on its own. MFA protection requires a factor in the authentication flow, not only enrolment.", "components": ["keycloak", "keycloak-source"], "sources": ["keycloak:sbbd55dcb81cd", "keycloak:sefec90245fa1", "keycloak-source:sd5a9fd571726", "keycloak-source:sff5c9a23ec46", "keycloak-source:sdc09746a23d8"], "status": "REASONED"},
    "keycloak-management": {"text": "Enabled Keycloak health and metrics use management port 9000; keep it private and use /health/ready for the orchestrator.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "management-mtls": {"text": "https-management-client-auth accepts none/request/required and inherits HTTP settings; this plaintext topology needs management TLS credentials and trust before client certificates can authenticate it.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "authentik-metrics": {"text": "At version/2026.8.5, the Rust core metrics listener uses plain HTTP with default [::]:9300, and the main Dockerfile ships the Rust binary run by ak; whether published images were built from it is NOT ESTABLISHED. The shipped Compose file does not publish 9300, but the container-network listener still needs restriction.", "components": ["authentik"], "sources": ["authentik:s4fc8280e760f", "authentik:sed8d69a749a7", "authentik:sa2dcdc13cd29", "authentik:s5c36281a2a21", "authentik:se669fb431f33", "authentik:scc60a0e302d1", "authentik:s675653f9e0f8", "authentik:sd3e2ba0c6343", "authentik:s8329bf6c67f8", "authentik:s07817f9dd888", "authentik:s2dc55e93d595"], "status": "REASONED"},
    "authentik-go-metrics": {"text": "At version/2026.8.5, a Go web server metrics listener is also present: cmd/server calls WebServer.Start, which calls runMetricsServer per listen.metrics address. A version/2026.8.3 search, not repeated since, found no image or release build of cmd/server; a developer debug launch targets it. The main Dockerfile ships the Rust binary; whether published images were built from it is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s0350a6463f9c", "authentik:s70d2fe895b7b", "authentik:sdacc5da217ab", "authentik:s430f8fb6719e", "authentik:s675653f9e0f8", "authentik:sd3e2ba0c6343"], "status": "REASONED"},
    "authentik-metrics-startup": {"text": "At version/2026.8.5, the Rust main starts the metrics server before the per-mode dispatch (healthcheck exits earlier), including proxy mode in proxy-feature builds; Server and AllInOne store the server handle, Worker and AllInOne the worker handles. Whether the published image was built from the tree's Dockerfile is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s6e40a30f1d99", "authentik:sed8d69a749a7", "authentik:s675653f9e0f8", "authentik:sd3e2ba0c6343", "authentik:s8329bf6c67f8", "authentik:s07817f9dd888", "authentik:s2dc55e93d595", "authentik:scc60a0e302d1"], "status": "REASONED"},
    "worker-outpost-metrics": {"text": "At version/2026.8.5, worker startup uses the same Rust metrics server as server mode; its handler serves Prometheus metrics on listen.metrics (default [::]:9300) via plain HTTP, with no authentication layer in the router wrapper. The LDAP outpost builds its metrics router with a bare Prometheus handler at /metrics and serves it on each metrics listen address and a Unix socket; section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced. Restrict to monitoring clients.", "components": ["authentik"], "sources": ["authentik:s4fc8280e760f", "authentik:sed8d69a749a7", "authentik:sa2dcdc13cd29", "authentik:s5c36281a2a21", "authentik:sf577784d5ebc", "authentik:sb8dece660959", "authentik:se669fb431f33", "authentik:s0c4d3f60ff27", "authentik:s030a7cc6a274"], "status": "REASONED"},
    "keycloak-mfa": {"text": "Enrol administrator TOTP or WebAuthn and require the factor in the realm authentication flow. When Keycloak's default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. A Required second factor can instead be enrolled during authentication without proving possession of a preexisting factor, so test an administrator with no registered factor and inspect the flow.", "components": ["keycloak", "keycloak-source"], "sources": ["keycloak:sefec90245fa1", "keycloak-source:sff5c9a23ec46", "keycloak-source:se54a2a6e7d47", "keycloak-source:s277571a617ec", "keycloak-source:sdc09746a23d8", "keycloak-source:sde43d0e31c0f", "keycloak-source:s6e859a060525", "keycloak-source:s3f7c345f457f"], "status": "REASONED"},
    "brute-force-default": {"text": "Keycloak brute-force detection is disabled by default and must be enabled per realm.", "components": ["keycloak"], "sources": ["keycloak:sefec90245fa1"], "status": "REASONED"},
    "redirect-wildcards": {"text": "Keycloak permits trailing redirect-URI wildcards and bare *; deliberately register exact URIs instead.", "components": ["keycloak"], "sources": ["keycloak:sefec90245fa1"], "status": "REASONED"},
    "docker-socket": {"text": "authentik Compose mounts the worker Docker socket for outpost management; use a socket proxy or remove the mount and manage outposts manually.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:scc60a0e302d1"], "status": "REASONED"},
    "cache-ports": {"text": "Keycloak cache transport uses 7800 and failure detection 57800; TCP stacks enable TLS by default but still need private reachability.", "components": ["keycloak"], "sources": ["keycloak:s44e24ad4e579"], "status": "REASONED"},
    "redis-history": {"text": "Redis 6379 is relevant to older authentik: tasks moved in 2025.8 and remaining uses in 2025.10, which removes Redis entirely.", "components": ["redis-removal"], "sources": ["redis-removal:seaa0a9896153"], "status": "REASONED"},
    "verify-setup": {"text": "On a disposable instance, complete anonymous root-to-setup flow and confirm akadmin login; after setup or password bootstrap, fresh /setup visits must return to authentication. Source tests were read, not run.", "components": ["authentik"], "sources": ["authentik:s67916683010a", "authentik:s01be08361cc2", "authentik:sbfdadaefea47"], "status": "REASONED"},
    "verify-publication": {"text": "Compare exposed and loopback publications: untrusted clients lose setup access while a local browser still reaches it. Neither configuration publishes 9300.", "components": ["authentik"], "sources": ["authentik:scc60a0e302d1", "authentik:se669fb431f33"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect all listeners plus Compose publications: host ss misses container namespaces, Compose ps sees one project, and proxy 443 publication is expected.", "components": ["authentik", "keycloak"], "sources": ["authentik:scc60a0e302d1", "authentik:se669fb431f33", "keycloak:s44e24ad4e579", "keycloak:s4b5df6f4ef2e"], "status": "REASONED", "verify": [1, 2]},
    "verify-issuer": {"text": "From outside allowed networks, application-realm discovery must print the expected issuer before negative route checks are interpreted; an arbitrary 200 is insufficient.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED", "verify": [3]},
    "verify-console": {"text": "Public /admin/master/console/ must return 404; 2xx, 3xx, 401 and 403 do not show that the console path is closed.", "components": ["keycloak", "nginx"], "sources": ["keycloak:sffc6123bea5c", "nginx:s8d8f3323b468"], "status": "REASONED", "verify": [3]},
    "verify-admin-api": {"text": "Public /admin/realms/master/users must return 404; 401 means the API still answers and requests a token.", "components": ["keycloak", "nginx"], "sources": ["keycloak:se5538391cf9f", "nginx:s8d8f3323b468"], "status": "REASONED", "verify": [3]},
    "verify-master": {"text": "Outside allowed sources, master-realm discovery must return 403; 200 exposes it and 404 indicates blanket denial. Review effective locations beyond these sampled routes.", "components": ["keycloak", "nginx"], "sources": ["keycloak:s2f5f079c5e00", "nginx:sf7458f108aca"], "status": "REASONED", "verify": [3]},
    "verify-admin-login": {"text": "An allowed administrator must complete a real login through the private console and observe where it authenticates, which by this guide's reading, not established at 26.8.2, is the frontend master realm; the network restriction on that path must admit the administrator, and outside sources must fail.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED", "verify": [3]},
    "verify-direct-ports": {"text": "Probe 8080/8443/9000/9300/9443 directly: curl exit 0 reports a completed operation, 7 reports a connection failure, and 28 is an inconclusive timeout requiring full diagnostics to distinguish accepted-then-stalled from unreachable. Treat a connection failure as the desired isolation outcome only after checking the diagnostic and target; this guide infers that exits 52 and 56 follow an accepted connection, so a listener is reachable. Other exits require diagnostic review. The connection and full-transfer deadlines differ. The checks remain REASONED expectations, not observed outcomes.", "components": ["keycloak", "authentik", "curl", "keycloak-source"], "sources": ["curl:s9d0c5b92e9a4", "keycloak:s4b5df6f4ef2e", "keycloak:sffc6123bea5c", "authentik:scc60a0e302d1", "authentik:s4fc8280e760f", "authentik:se669fb431f33", "keycloak-source:s32a00c2c8803", "curl:s25c3e6e61c14", "curl:s9c78f229c8ba", "curl:sc7945d33c78d", "curl:s977c1ef288cc", "curl:sc39d43ba6e58", "curl:s9380fc35e98e"], "status": "REASONED", "verify": [4]},
    "verify-bootstrap-removal": {"text": "Look up the bootstrap username with exact=true rather than a user list, whose 100-result default is not established at 26.8.2, inspect the returned username, and separately check bootstrap service accounts. Keycloak documents non-exact matching for its -q q=username: filter; this guide keeps the -q order (exact=true first) as defensive advice based on a report, not documented ordering behaviour.", "components": ["keycloak", "keycloak-admin-cli"], "sources": ["keycloak:sbbd55dcb81cd", "keycloak:sefec90245fa1", "keycloak-admin-cli:s8b4e40148629"], "status": "REASONED", "verify": [4]},
    "verify-address-coverage": {"text": "Repeat external checks for every public IPv4/IPv6 address and the origin; private admin, database and outposts need separate checks, and the listed ports are not a full inventory.", "components": ["keycloak", "authentik-docs"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c", "authentik-docs:sb44156cde339"], "status": "REASONED", "verify": [3, 4]},
    "authentik-mfa": {"text": "authentik has TOTP and WebAuthn setup stages; enrol a phishing-resistant administrator factor before connecting the first app and require it through an Authenticator Validate stage bound to the authentication flow (this guide's requirement; the cited sources do not state this ordering). A registered device alone does not establish the flow binding. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The pinned validate-stage and flow-binding sources support these behaviours but do not establish an administrator-specific factor policy.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:sf19de9022fee", "authentik:s77bfc5116d72", "authentik:sdf8b8d567281", "authentik:s68ce378d011e", "authentik:s6500fae4a5ac", "authentik:se89f1e7b7d18", "authentik:s506b3d80d9ce", "authentik:sd5b24af3593a"], "status": "REASONED"},
    "authentik-admin-boundary": {"text": "At version/2026.8.5, /if/admin/, /if/user/ and flows share core routing. This guide assesses that authentik has no equivalent to hostname-admin: the cited configuration, Go startup and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. The permission boundary remains unestablished.", "components": ["authentik"], "sources": ["authentik:s313f1f9b5bc9", "authentik:s98f257d3ede1", "authentik:s8012ab258605", "authentik:s70d2fe895b7b", "authentik:sb8906abab13c", "authentik:s3e1090638af8"], "status": "REASONED"},
    "authentik-admin-listeners": {"text": "At version/2026.8.5, defaults are HTTP [::]:9000, HTTPS [::]:9443 and metrics [::]:9300; Go startup adds these configured listeners and a Unix socket, and its plain HTTP, HTTPS and Unix listeners share the application proxy router after outpost handling. These files show shared routing, not a separate admin port, and do not prove which listeners a deployed build starts.", "components": ["authentik"], "sources": ["authentik:se669fb431f33", "authentik:s8012ab258605", "authentik:s70d2fe895b7b", "authentik:s63d78b9d40d8", "authentik:s6c3afec54d75", "authentik:s1626a6c0776a"], "status": "REASONED"},
    "authentik-admin-interface": {"text": "At version/2026.8.5, both interface routes redirect authenticated external, service-account and internal-service-account users to a default app or deny them; other requests fall through. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.", "components": ["authentik"], "sources": ["authentik:s98f257d3ede1", "authentik:s169ffaaa70fc"], "status": "REASONED"},
    "authentik-admin-api-mount": {"text": "At version/2026.8.5, API v3 registers application API routes, including core users, groups, tokens and admin authenticators. The root URL configuration mounts each app under the web path; the API app mounts api/ and then v3/, so the v3 router is at <web path>api/v3/, /api/v3/ by default, matching the Go client's api/v3 prefix. Endpoint permission wiring is not established by these files.", "components": ["authentik"], "sources": ["authentik:s98f257d3ede1", "authentik:s2cdcdb3b510b", "authentik:s70d2fe895b7b", "authentik:s073e329f067a", "authentik:s12fcc19f34ee", "authentik:sc84a7d5db870", "authentik:sa06907a58b4e", "authentik:sf668b16f361a", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED"},
    "authentik-admin-api-auth": {"text": "At version/2026.8.5, TokenAuthentication recognizes API-intent tokens, API-scoped OAuth tokens, the managed-outpost secret and IPC key; it rejects inactive users and unrecognized credentials, but absent or unsupported authentication can return no user. This does not establish session authentication or every endpoint adopting this class.", "components": ["authentik"], "sources": ["authentik:s68d603b9d5bc"], "status": "REASONED"},
    "authentik-admin-rbac": {"text": "At version/2026.8.5, ObjectPermissions' request check passes object-lookup requests (its comment leaves view checks to ObjectFilter, writes to the object check) and permits configured creation without add permission; the object check accepts global permissions or configured ownership before delegating. HasPermission checks user.has_perms; endpoint wiring and permission boundary stay unestablished.", "components": ["authentik"], "sources": ["authentik:s9f2178a64542"], "status": "REASONED"},
    "authentik-admin-proxy": {"text": "Build any network boundary around authentik administration at the proxy using path restrictions; identify and test required paths for the deployed version and maintain the list. This guide assesses that the UI is not designed around this separation and path-based separation is difficult to maintain; this is not a vendor-supported recipe, and the cited files give no complete path list.", "components": ["authentik"], "sources": ["authentik:s313f1f9b5bc9", "authentik:s98f257d3ede1", "authentik:s2cdcdb3b510b", "authentik:s70d2fe895b7b"], "status": "REASONED"},
    "authentik-admin-paths": {"text": "At version/2026.8.5, core URLs show /if/admin/, /if/user/, flows, HTTP admin-template fallbacks at /ws/outpost/<uuid:pk>/ and /ws/client/, and a /ws/client/ websocket route wrapped in authentication middleware. With the API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization.", "components": ["authentik"], "sources": ["authentik:s98f257d3ede1", "authentik:s70d2fe895b7b"], "status": "REASONED"},
    "authentik-rust-listeners": {"text": "At version/2026.8.5, the main Dockerfile ships the Rust binary run by ak. Server mode runs gunicorn on a Unix socket and serves one router over HTTP on listen.http, rustls on listen.https and a Unix socket, sending embedded-outpost apps to the outpost and the rest via the core router to gunicorn. Worker mode serves health checks on listen.http. Deployed topology beyond Compose is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s675653f9e0f8", "authentik:sd3e2ba0c6343", "authentik:s8329bf6c67f8", "authentik:s07817f9dd888", "authentik:s2dc55e93d595", "authentik:scc60a0e302d1", "authentik:s5af5d9143036", "authentik:s3e1090638af8", "authentik:s14e51acafd6f", "authentik:s906b273aa104", "authentik:sa01f6c27bc59", "authentik:sdb8c87fa0cfc", "authentik:s949377fe0d94", "authentik:se669fb431f33"], "status": "REASONED"},
    "authentik-api-defaults": {"text": "At version/2026.8.5, REST framework defaults are TokenAuthentication then SessionAuthentication, ObjectPermissions and an ObjectFilter backend; settings modules can update them, and a version/2026.8.3 search, not repeated since, found no app settings module doing so. Users and groups add AgentAuth; the flow executor uses AllowAny. SessionAuthentication and deployment overrides are NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s7c88d077f919", "authentik:s19f8c9e313eb", "authentik:s402352aa9811", "authentik:sb2bc7f868825", "authentik:s3ea4b10861b1"], "status": "REASONED"},
    "authentik-admin-websockets": {"text": "At version/2026.8.5, the websocket modules a version/2026.8.3 search found give /ws/client/, /ws/outpost/<uuid:pk>/, /ws/rac/<str:token>/ and /ws/outpost_rac/<str:channel>/ under the web path; others are not established. The /ws/client/ route resolves a session or anonymous user and accepts every connection; the RAC client consumer on /ws/rac/ accepts, then denies tokens not bound to the session.", "components": ["authentik"], "sources": ["authentik:s62327707b202", "authentik:s9e012ed398d4", "authentik:sf668b16f361a", "authentik:s98f257d3ede1", "authentik:s5b1985e0936f", "authentik:s6d275572bf62", "authentik:s4b92525713bb", "authentik:s6b20bb333911", "authentik:sf02ba388bb2f", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED"},
    "authentik-outpost-websockets": {"text": "At version/2026.8.5, under the configured web path (default / shown), the /ws/outpost/ and /ws/outpost_rac/ websocket routes deny a connection unless TokenAuthentication accepts its bearer token; /ws/outpost/ also needs outpost view permission, while /ws/outpost_rac/'s RAC outpost consumer accepts with no outpost-specific check.", "components": ["authentik"], "sources": ["authentik:s62327707b202", "authentik:sf02ba388bb2f", "authentik:s02f5150b41d1", "authentik:s369c9cffd8f5", "authentik:s4b92525713bb", "authentik:s331ad7f37dac", "authentik:sf668b16f361a", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED"},
    "authentik-admin-api-shared": {"text": "At version/2026.8.5, the API router registers the flow executor at flows/executor/<slug:flow_slug>/ with AllowAny, the API schema names that path's GET flows_executor_get, and the flow interface calls flowsExecutorGet, read here as that GET's generated client method, so this guide infers refusing the whole API prefix would break login.", "components": ["authentik"], "sources": ["authentik:s033849961834", "authentik:s3ea4b10861b1", "authentik:s9eece0a5a170", "authentik:s1ff44bd506fd", "authentik:s073e329f067a", "authentik:s2cdcdb3b510b"], "status": "REASONED"},
    "authentik-admin-static-paths": {"text": "At version/2026.8.5, the Rust static router also serves /if/admin/assets/ under the configured web path (shown with the default /) alongside the user, flow and RAC interface assets. Path lists from the routing tables this guide read are bounded by those tables; complete path coverage remains open.", "components": ["authentik"], "sources": ["authentik:s247ca79b6f6c", "authentik:s906b273aa104", "authentik:s3e1090638af8", "authentik:s073e329f067a", "authentik:s2cdcdb3b510b", "authentik:s62327707b202", "authentik:s98f257d3ede1", "authentik:s033849961834", "authentik:sf668b16f361a", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED"},
    "verify-mfa-password": {"text": "For both providers, open a fresh session with only the administrator password and confirm access is refused after factor enforcement. This guide assesses that an already-enrolled administrator's password-only refusal does not distinguish enrolment from enforcement; test a user with no registered factor and inspect the flow or stage settings. Keycloak's default conditional 2FA, when reached (a successful Cookie execution skips it), prompts for configured OTP unless passwordless WebAuthn already authenticated the user; the default flow's WebAuthn Authenticator execution is disabled by default; and a Required factor the user lacks can be enrolled during authentication. At authentik version/2026.8.5, the unconfigured-device action defaults to SKIP; DENY refuses a user with no allowed device. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. Bind the validation stage to the authentication flow.", "components": ["keycloak", "authentik-docs", "authentik", "keycloak-source"], "sources": ["keycloak:sefec90245fa1", "authentik-docs:sb44156cde339", "authentik:s2986fcb4cb32", "authentik:s16ad051165b7", "keycloak-source:sff5c9a23ec46", "keycloak-source:s277571a617ec", "authentik:sf19de9022fee", "authentik:s77bfc5116d72", "authentik:sdf8b8d567281", "authentik:s68ce378d011e", "authentik:s6500fae4a5ac", "authentik:se89f1e7b7d18"], "status": "REASONED"},
    "management-auth-default": {"text": "In this plain-HTTP Keycloak topology no HTTP client authentication is configured, so inherited management client authentication is usually none; required needs management TLS credentials and trust first.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "docker-socket-scope": {"text": "Docker's daemon requires root unless rootless (daemon and containers run non-root); only trusted users should control it. For authentik's shipped Compose worker socket, check daemon type and restrict access: this guide assesses ordinary rootful access as host-root-equivalent and rootless blast radius as the daemon user and what it can access; sources do not directly demonstrate either assessment.", "components": ["authentik-docs", "authentik", "docker-engine", "docker-engine-pinned"], "sources": ["authentik-docs:sb44156cde339", "authentik:scc60a0e302d1", "docker-engine:s18f59818e451", "docker-engine:s7e61efb4dd59", "docker-engine-pinned:secebea1a69ab", "docker-engine-pinned:s8eab393a61c6"], "status": "REASONED"},
    "outpost-boundaries": {"text": "At version/2026.8.5, authentik supports Proxy, LDAP, RADIUS and RAC outposts. The embedded Proxy outpost runs in the main server and shares ports 9000 and 9443 rather than opening another port; managed or manually deployed outposts can run elsewhere. This guide requires separate exposure checks for each deployed outpost and assesses that its Verify probes do not demonstrate them.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s6ee73dbd270c", "authentik:s741c951134bd", "authentik:s0249923fde2f", "authentik:sf4642b40524f"], "status": "REASONED"},
    "outpost-proxy-image": {"text": "At version/2026.8.5, proxy.Dockerfile, titled the authentik proxy outpost image, builds the Rust authentik binary with only the proxy feature, has no go build step, copies only that binary and runs /authentik proxy. This guide infers that an image built from it runs the Rust proxy outpost, not the cited Go proxy code; whether published images were built from it is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s82a97fe0acf2", "authentik:s9082a2dbb6c5", "authentik:s4a31ab9f5ec9", "authentik:s6e40a30f1d99", "authentik:s0c4d3f60ff27"], "status": "REASONED"},
    "outpost-proxy-listeners": {"text": "At version/2026.8.5, the authentik proxy subcommand starts the Rust proxy outpost, which serves plain HTTP on each listen.http address and rustls on each listen.https address unless it is the embedded outpost; Rust startup schedules the metrics server on listen.metrics before mode dispatch. Pinned defaults are [::]:9000, [::]:9443 and [::]:9300, and proxy.Dockerfile exposes 9000, 9300 and 9443.", "components": ["authentik"], "sources": ["authentik:s4a31ab9f5ec9", "authentik:s6e40a30f1d99", "authentik:s4fc8280e760f", "authentik:sa01f6c27bc59", "authentik:se669fb431f33", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s82a97fe0acf2", "authentik:s9082a2dbb6c5"], "status": "REASONED"},
    "outpost-deployment-listeners": {"text": "At version/2026.8.5, the pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. The Docker controller maps the outpost's ports to the host unless docker_map_ports is false; docker_map_ports defaults to true. The Kubernetes controller reconciles Deployment and Service objects. LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced.", "components": ["authentik"], "sources": ["authentik:s0c4d3f60ff27", "authentik:s030a7cc6a274", "authentik:se669fb431f33", "authentik:sb8dece660959", "authentik:s63fcd0ce5a18", "authentik:s6be1839a0a33", "authentik:sb24757cb27e6"], "status": "REASONED"},
    "verify-proxy-neutralization": {"text": "Run external probes outside every allowed network; unset HTTP/HTTPS/ALL/NO_PROXY variables in both cases and use curl -q --noproxy '*' to bypass proxies and curlrc, which this guide assesses could otherwise make blocked endpoints appear reachable through allowed egress. Curl's HTTP proxy environment variable is lowercase only; -q must be curl's first option.", "components": ["keycloak", "curl"], "sources": ["keycloak:sffc6123bea5c", "curl:sde07f1edf2dc", "curl:s75e3807878ff", "curl:s508454c45cf1", "curl:s2278b86c08a6", "curl:sc8658f8a2e89"], "status": "REASONED", "verify": [3, 4]},
    "verify-authentik-routes": {"text": "The fenced paths are Keycloak-specific; the exclusion of Keycloak paths from authentik is this guide's inference from the fetched route files, not an exhaustive route proof. For authentik, use a deployed application's actual OAuth2 discovery URL as the positive control and confirm its configured issuer. A responding status alone is not the positive-control pass condition.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s313f1f9b5bc9", "authentik:s25612b8e4bc3", "authentik:s1b0b1b6332d8", "authentik:s42b24ec40c5a", "authentik:s073e329f067a"], "status": "REASONED", "verify": [3]},
    "verify-authentik-admin-routes": {"text": "For authentik, an untrusted client must not reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s313f1f9b5bc9", "authentik:s2cdcdb3b510b"], "status": "REASONED", "verify": [3]},
    "verify-authentik-login-api": {"text": "Do not refuse the whole authentik API prefix without tracing login dependencies; confirm an ordinary user can still complete login. At version/2026.8.5 the v3 router is at <web path>api/v3/ (/api/v3/ by default) and registers the flow executor with AllowAny; the flow interface calls flowsExecutorGet, taken here as its generated client method, so this guide infers that login uses the API prefix.", "components": ["authentik"], "sources": ["authentik:s073e329f067a", "authentik:sc84a7d5db870", "authentik:sa06907a58b4e", "authentik:s2cdcdb3b510b", "authentik:s033849961834", "authentik:s3ea4b10861b1", "authentik:s9eece0a5a170", "authentik:s1ff44bd506fd", "authentik:sf668b16f361a", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED", "verify": [3]},
    "verify-authentik-oauth2-routes": {"text": "At version/2026.8.5 the installed OAuth2 app mounts its urls module, which defines the per-application discovery suffix, at application/o/ and urls_root at the root; the root URL module mounts installed authentik apps' mountpoints under the web path, so the prefix is <web path>application/o/, /application/o/ by default. The issuer can be global or per-provider; /if/admin/ is a core route.", "components": ["authentik"], "sources": ["authentik:s25612b8e4bc3", "authentik:s1b0b1b6332d8", "authentik:s42b24ec40c5a", "authentik:s313f1f9b5bc9", "authentik:s073e329f067a", "authentik:s304feb3be14f", "authentik:s37a8db510590", "authentik:s2d86a3e9d60d", "authentik:s8d3ff0842282", "authentik:s12fcc19f34ee", "authentik:sf668b16f361a", "authentik:sb69f89fd29f8", "authentik:s3d85bc9743c4", "authentik:s86eb476b495a", "authentik:s3d8996ccb579"], "status": "REASONED"},
    "admin-factor-order": {"text": "Enrol a phishing-resistant factor on the administrator account of either provider before connecting the first application and enforce it in the flow (this guide's requirement; the cited sources do not state this ordering). Keycloak documents Required executions; authentik version/2026.8.5 binds ordered stages to flows, but the cited files do not establish an administrator-specific factor policy.", "components": ["keycloak", "authentik-docs", "keycloak-source", "authentik"], "status": "REASONED", "sources": ["keycloak:sefec90245fa1", "authentik-docs:sb44156cde339", "keycloak-source:sff5c9a23ec46", "authentik:s68ce378d011e", "authentik:s6500fae4a5ac", "authentik:sf19de9022fee", "authentik:s77bfc5116d72"]},
    "keycloak-http-opt-in": {"text": "In the production example, backend plain HTTP on default port 8080 exists only when explicitly enabled with --http-enabled=true; confine that hop to loopback or a controlled private segment. At 26.8.2, the HTTP listener option defaults false but is enabled by default in development mode, and HTTPS defaults to port 8443. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.", "components": ["keycloak", "keycloak-source"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c", "keycloak-source:sa452e5c860cd", "keycloak-source:s32a00c2c8803", "keycloak-source:sb3476e7a2eb2", "keycloak-source:s7fdfa4997898"], "status": "REASONED"},
    "idp-maintenance": {"text": "This guide requires patching, tested backups and keeping a self-hosted identity provider available (the cited files prescribe no cadence) and assesses that a compromised or unavailable provider takes its dependent services with it. The cited sources establish no complete Keycloak or authentik backup procedure, authentik upgrade procedure, universal maintenance cadence or tested restore.", "components": ["keycloak", "authentik-docs", "authentik", "keycloak-source"], "sources": ["keycloak:s2f5f079c5e00", "authentik-docs:sb44156cde339", "authentik:sceae009a9d08", "keycloak-source:s94317d53483b", "keycloak-source:s14164b9cc6c3"], "status": "REASONED"},
    "keycloak-security-fixes": {"text": "The 26.7.5 and 26.8.1 records list section 6's fixes: 26.8.1 fixes CVE-2026-94218 (2FA setup enforcement bypass) and CVE-2026-96445 (Conditional OTP skip headers on untrusted proxy paths); 26.7.5 fixes brute-force lockout bypasses CVE-2026-16103 and CVE-2026-88770, not in the 26.8.x records. The 26.8.2 record is empty. Run 26.8.1 or later; each bypass's detail and backports are not established.", "components": ["keycloak-releases"], "sources": ["keycloak-releases:s32d0f0981b58", "keycloak-releases:s46d0047d5606", "keycloak-releases:sd570d95abe70", "keycloak-releases:s614ddc99af91"], "status": "REASONED"},
    "keycloak-admin-api-v2": {"text": "Keycloak 26.8.0 promotes the Client Admin API v2 to preview, enabled with --features=preview or --features=client-admin-api:v2; the path it is served under at 26.8.2, and so whether the public /admin/ refusal covers it, are not established.", "components": ["keycloak-releases"], "sources": ["keycloak-releases:s46d0047d5606"], "status": "REASONED"},
    "keycloak-scim-api": {"text": "Keycloak 26.8.0 promotes the SCIM API, for managing a realm's users and groups, to supported. The server administration guide served on 2026-11-05 (26.8.1 page links) gives its base URL under /realms/, ending /scim/v2, enabled per server and realm, needing a bearer token. This guide infers an enabled realm serves it on the public hostname; its 26.8.2 default and path are not established.", "components": ["keycloak-releases", "keycloak"], "sources": ["keycloak-releases:s46d0047d5606", "keycloak:sefec90245fa1"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
