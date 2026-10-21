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

Written against Keycloak Admin CLI 26.7.4, Keycloak source 26.7.4, authentik source version/2026.8.3, authentik Redis removal 2025.10, and curl documentation curl-8_23_0; 1 further source is pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-10-20; documentation checked September 2026. The guide records 69 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

This guide assesses that a compromised or unavailable self-hosted identity provider takes its dependent services with it. [identity-providers.md](identity-providers.md) covers choosing one; this guide requires patching, tested backups and keeping the provider available (this guide's requirement; the cited files do not prescribe a cadence). At the time of writing, authentik's pinned security policy lists 2026.5.x and 2026.8.x as supported. Keycloak 26.7.4's security policy says that, depending on severity, vulnerabilities may be fixed in the current major.minor release, or lower-severity vulnerabilities or hardening in the following major.minor release; it encourages those unable to upgrade regularly to consider the Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak cautions that realm export alone has backup limitations: consistency is not guaranteed unless all nodes are stopped before the export, and user and admin events, persisted sessions, workflow state and revoked tokens are omitted. The fetched files do not establish a complete backup procedure for either provider, an authentik upgrade procedure, a universal maintenance cadence or a tested restore. This guide covers what the provider exposes once it is running: an administration surface that does not move when you tell it to, a first-boot window in which an unauthenticated visitor can claim the administrator account, and a management port that, once you turn it on, answers without asking who you are.

## 1. Bind privately and front it

Neither product should answer the internet on the port it listens on. Put it behind the reverse proxy you already run ([nginx.md](nginx.md), [caddy.md](caddy.md), [traefik.md](traefik.md)) and bind the service itself to loopback or a private address ([host.md](host.md)).

At authentik tag `version/2026.8.3` (commit `e5a0d2f7572cb776eee7a3e9355937ce38973761`), the shipped Compose server publishes `${COMPOSE_PORT_HTTP:-9000}:9000` and `${COMPOSE_PORT_HTTPS:-9443}:9443`. With those variables unset, both mappings omit a host address and publish on all host interfaces under Docker's default publishing configuration. These are the file's only host publications; it does not publish metrics port 9300. Inside the container, `listen.http` defaults to `[::]:9000` and `listen.https` to `[::]:9443`, wildcard listeners rather than loopback. Host publication and the container's listen address are separate controls. See the pinned Compose and listener-default sources below.

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

At Keycloak `26.7.4`, `--http-host` defaults to all addresses (`0.0.0.0`) in production. Set it to the intended loopback or private interface, or use network rules that permit only the proxy, and check the effective listener in Verify step 1.

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

# The Admin Console AUTHENTICATES against this hostname even when hostname-admin moves its
# API calls elsewhere: Keycloak builds the console's auth URL from the FRONTEND base URL. So
# a blanket 404 here locks every administrator out. Restrict by SOURCE instead, which is what
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

This is a fragment for the public hostname's existing `server` block, not a replacement for it. Two different things happen on two different hostnames and it is worth being precise about which. The console's API calls go to the admin hostname, because Keycloak states that the "Administration Console implicitly accesses the API using the URL as specified by the `hostname-admin` option". Its LOGIN does not: Keycloak builds the console's authentication URL from the frontend base URL, so the browser is sent to `id.example.com/realms/master/` to authenticate no matter where the console itself is served. That is why the rule above restricts that path by source address rather than refusing it, and why an earlier version of this guide that refused it outright would have locked out every administrator including the one who applied it. A denied source gets a 403 from nginx rather than a 404, which is what step 5 of the Verify section looks for; if you see a 404 there, the path is being refused outright rather than restricted, and your administrators are locked out along with everyone else.

The admin hostname is a separate `server` block on `id-admin.internal`, reached over a tailnet or an SSH forward per [admin-uis.md](admin-uis.md), and it must proxy `/admin/`, `/resources/` and `/.well-known/`. Add `/js/` as well if you run a version whose console still loads its adapter from there. Step 6 of the Verify section is the test, and it is the only step that checks something still WORKS rather than something is closed.

Overwriting rather than appending matters. Keycloak's reverse proxy guide: "Take extra precautions to ensure that the client address is properly set by your reverse proxy via the `Forwarded` or `X-Forwarded-For` headers. If these headers are incorrectly configured, rogue clients can inject false values and trick Keycloak into thinking the client is connecting from a different IP address than the actual one." An appended header lets a client choose the first value, which is the one most code reads.

Overwrite all five, not the two you were thinking of. `--proxy-headers xforwarded` parses "`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Forwarded-Port`, and `X-Forwarded-Prefix`", and nginx passes through any request header you do not set, so the three you leave alone arrive exactly as the client sent them. Keycloak also offers `--proxy-trusted-addresses`, which accepts forwarded headers only from the proxy's own addresses, and is honest about what that is worth: "this is only weak protection because IP addresses can be spoofed." It is worth setting and it is not a substitute for overwriting the headers.

Without `--proxy-headers`, requests through a proxy fail rather than fall back: "If you are using a reverse proxy for anything other than TLS passthrough and do not set the `proxy-headers` option, then by default you will see 403 Forbidden responses to requests via the proxy that perform origin checking."

## 4. The first-boot window

authentik's initial setup sets the password on the default `akadmin` account; it does not ask the visitor to authenticate as an administrator first. At `version/2026.8.3`, visit the instance root (`/`, with the default web path). While setup is incomplete, it redirects to `/setup`, which plans the flow and redirects to `/if/flow/initial-setup/`. Opening the flow directly in a fresh session is rejected: its expression policy requires the context marker `goauthentik.io/core/setup/started-by` to equal `setup`. This marker comes from the public setup view, not from a credential.

The same policy permits a new plan only when `akadmin` is absent or `not akadmin.has_usable_password()`. The flow selects `akadmin` as the pending user, prompts for email, base URL and password, writes the existing user and logs them in. After completion, the setup view records setup as complete, disables the OOBE blueprints and changes the flow to require a superuser. An unauthenticated visitor who can reach a fresh instance and complete this flow can therefore claim its administrator account. Merely loading the page is not the claim, and the planning-time policy is not a promise that already-started sessions are revoked when a password is set.

Keep both ports unpublished to untrusted clients and keep the public reverse proxy route closed until setup is complete. For manual setup, use the loopback mappings in section 1 and browse locally or through an SSH forward; a proxy on a private container network can instead reach the service with both host mappings removed. Confirm setup is closed in a fresh session before allowing public traffic. This is the first-boot boundary described in [deployment-lifecycle.md](deployment-lifecycle.md).

For unattended setup, supply `AUTHENTIK_BOOTSTRAP_PASSWORD` before first startup through the protected `.env` file already loaded by both Compose services. The pinned startup handler also recognizes `AUTHENTIK_BOOTSTRAP_PASSWORD_HASH` and `AUTHENTIK_BOOTSTRAP_TOKEN`: any nonempty one triggers bootstrap, and successful application of the bootstrap blueprint marks the tenant setup complete. The password-hash form is validated; the source tests specify that the password forms set `akadmin`'s password and the token form supplies an API token. A token is not a browser-login password. Already-setup tenants are skipped, so changing these variables is not password rotation. Verify successful bootstrap and the closed setup route before publication, then remove the bootstrap secret from the startup environment. Protect the file and container-inspection access as described in [secrets.md](secrets.md). These are source-derived conditions, not a live demonstration of startup timing.

Keycloak's equivalent is a credential rather than a window, and it is meant to be thrown away. Its bootstrap admin documentation states that an account created this way "is **temporary**", that "the account should exist only for the duration necessary to perform operations needed to gain permanent and more secure admin access", and that afterwards "the account needs to be removed manually". This guide infers from the manual-removal instruction that the account does not expire on its own. Create a real administrator, enrol MFA on it per [mfa.md](mfa.md), then delete the bootstrap account and treat its password as a secret that was on a command line ([secrets.md](secrets.md)).

## 5. The management port

Keycloak serves health and metrics on a second port. Its management interface documentation states that "Management endpoints such as `/metrics` and `/health` are exposed on the default management port `9000` when metrics and health are enabled", and that "Exposing health and metrics endpoints on the default server is not recommended for security reasons, and you should always use the management interface".

The page does document a control: `https-management-client-auth` "Configures the management interface to require/request client authentication", taking `none`, `request` or `required`, and inheriting from the HTTP options when it is not given. Inheriting is the problem, because nothing in this guide's topology sets client authentication on the HTTP options either, so the effective answer is usually `none`. Setting it to `required` is not a one-line change in this topology, either: client certificates authenticate a TLS connection, and the startup command above enables plain HTTP with no server credentials, so there is no TLS on the management interface to carry them. Giving that port its own certificate and trust store comes first. Whether or not you do, keep 9000 on a private interface, which is the control that works without any of it. Your orchestrator needs `/health/ready`; the internet does not.

At authentik tag `version/2026.8.3`, core modes start the Rust metrics server: the Rust `main` starts it before the per-mode dispatch (healthcheck exits earlier), so proxy mode in a proxy-feature build starts it too. AllInOne and Worker modes start workers and store their handles in that server, and Server and AllInOne modes store the server handle. Its mode-dependent handler renders Prometheus metrics and appends Python metrics for server, worker and all-in-one modes. The router's fallback sends every path, including `/metrics`, to the handler; its wrapper has no authentication layer. The Rust metrics listener binds `listen.metrics` with plain HTTP (default `[::]:9300`) and a Unix socket. A Go web server metrics listener is also present at the tag: it serves `/metrics` with promhttp plus upstream metrics fetched from `<upstreamURL><web path>-/metrics/` and calls `http.ListenAndServe`. `WebServer.Start` calls `runMetricsServer` once per `listen.metrics` address, and the Go `cmd/server` command calls `WebServer.Start`, which this guide's search found as the only caller chain. The tree's main Dockerfile builds the Rust `authentik` binary with the `core` feature and copies it into the image, whose `ak` entrypoint runs `authentik server` for the `server` command that the shipped Compose server service uses; this guide's search found no image or release build of `cmd/server` in the pinned tree; a developer debug launch targets it. By this trace, the shipped server image's metrics listener is the Rust one. Whether the published image was built from this Dockerfile is NOT ESTABLISHED. The LDAP outpost builds its metrics router with `ak.MetricsRouter()`, which attaches a bare Prometheus handler at `/metrics`, and passes that router to both its HTTP metrics server on each metrics listen address and its Unix-socket server; section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced; the cited outpost source does not establish its default listen address. The shipped Compose file does not publish 9300, but that does not protect the container-network listener. Restrict metrics reachability to trusted monitoring clients and do not add a public host mapping.

## 6. Enrolment is not enforcement

Every application behind this provider inherits its authentication, which means it inherits the administrator's authentication too. Enrol a phishing-resistant factor on the administrator account before you connect the first application, not after (this guide's requirement; the cited sources do not state this ordering). Both products support TOTP and WebAuthn; authentik's pinned TOTP and WebAuthn setup stages show it has enrolment stages for both factors. [mfa.md](mfa.md) covers the enrolment and the reason to require a hardware key or passkey for administrators specifically.

Enrolling a factor is not the same as requiring one. In Keycloak the requirement lives in the realm's authentication flow: when its default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. Required executions must succeed, but a Required second factor can be enrolled during authentication without proving possession of a preexisting factor. At authentik version/2026.8.3, an Authenticator Validate stage must be bound to the authentication flow; its unconfigured-device action defaults to SKIP. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The cited authentik files describe stage behaviour and flow binding but do not establish an administrator-specific factor policy. Test it the way [mfa.md](mfa.md) says to: open a fresh session with only the administrator password and confirm access is refused.

Two realm settings outlive everything above and neither is touched by it. Keycloak states that "Brute force detection is disabled by default. Enable this feature to protect against brute force attacks", and it is a realm setting rather than a deployment one, so a hardened deployment still accepts unlimited password guesses until you turn it on. And redirect URIs are worth a deliberate pass. Keycloak allows a wildcard at the end of a pattern, which is narrower than it sounds and still widens the set of destinations a token can be sent to; a bare `*` widens it to everything, for anyone who can reach the authorization endpoint, which is everyone. Register exact URIs per [oidc-integration.md](oidc-integration.md), and treat every wildcard as something you chose rather than something you inherited.

## 7. authentik has no equivalent to `hostname-admin`

Section 3 is Keycloak-specific because the control it describes is. At `version/2026.8.3`, authentik routes `/if/admin/` alongside `/if/user/` and flows in its core URL configuration. This guide assesses that authentik has no equivalent to `hostname-admin`: the cited configuration, Go startup code and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. Say that out loud rather than assuming the section above covers both products.

The pinned defaults set HTTP to `[::]:9000`, HTTPS to `[::]:9443` and metrics to `[::]:9300`; the Go `ListenConfig` has no administration field, and the Rust `ListenConfig` holds HTTP, HTTPS and metrics addresses, an optional `debug_tokio` address and trusted-proxy CIDRs. `WebServer.Start` starts configured HTTP, HTTPS and metrics listeners plus a Unix socket; its plain HTTP and Unix listeners serve the same router, whose web-path handler proxies to the application after embedded-outpost handling, and its HTTPS listener wraps a TCP listener in TLS and serves that router too. The tree's main Dockerfile and `ak` entrypoint run the Rust binary instead (section 5). In server mode, Rust startup spawns gunicorn on a Unix socket, then serves one router over plain HTTP on each `listen.http` address, over rustls on each `listen.https` address and on a Unix socket. That router sends requests for embedded-outpost applications to the outpost and the rest to the core router, which answers `/-/health/` itself, serves static assets and forwards everything else, including websocket upgrades, to gunicorn. Worker mode serves a health-check router on `listen.http`; in all-in-one mode the worker starts no HTTP listener of its own. These files show shared application routing, not a separate admin process or port. They do not prove which listeners a deployed build starts; deployed topology beyond the shipped Compose file is NOT ESTABLISHED.

Both interface routes use `BrandDefaultRedirectView`: authenticated external, service-account and internal-service-account users are redirected to a default application or denied; other requests fall through to `InterfaceView`. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.

The API v3 router registers applications' `api_urlpatterns`, including core users, groups, tokens and admin authenticators. The Go API client targets `api/v3` below the configured web path. The settings make the root URL module the root URL configuration, and it mounts each application's URLs under the web path; the API application's mountpoint is `api/` and its URL module mounts `v3/`, so the v3 router is served at `<web path>api/v3/`, which is `/api/v3/` with the default web path `/`. The REST framework settings set `TokenAuthentication` and then REST framework `SessionAuthentication` as the default authentication classes, `ObjectPermissions` as the default permission class and `ObjectFilter` among the default filter backends. Application settings modules and a `data.user_settings` module can update these settings; this guide's search found no application settings module that does, and deployment overrides are NOT ESTABLISHED. Endpoints can replace the defaults: the users and groups viewsets list `TokenAuthentication`, `SessionAuthentication` and `AgentAuth`, and the flow executor sets `AllowAny`; this guide's search found 66 non-test lines that set authentication or permission classes. `TokenAuthentication` recognizes API-intent tokens, OAuth access tokens with the authentik API scope, the managed-outpost secret and the IPC key, rejects inactive users and raises an authentication failure for unrecognized credentials; absent or unsupported authentication can return no user. `ObjectPermissions.has_permission` passes every object-specific request (its comment leaves view checks to `ObjectFilter` and writes to `has_object_permission`) and permits configured creation without an add permission; `has_object_permission` accepts global permissions or configured ownership before delegating to the parent object check; `HasPermission` checks `user.has_perms`. These are authentication and RBAC implementations, not proof that every administration endpoint applies them. `SessionAuthentication` is implemented in Django REST framework, outside the pinned tree, so its behaviour is NOT ESTABLISHED here; a per-endpoint audit and a complete permission boundary remain NOT ESTABLISHED.

Build any network boundary around authentik administration at the proxy using path restrictions. Identify and test the required paths for the deployed version and maintain that list. This guide assesses that the UI is not designed around this separation and that path-based separation is difficult to maintain. The pinned core URLs also show HTTP admin-template fallbacks at `/ws/outpost/<uuid:pk>/` and `/ws/client/`, and a `/ws/client/` websocket route wrapped in authentication middleware; together with the interface routes and API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization. The Rust static router also serves `/if/admin/assets/` alongside the user, flow and RAC interface assets. The ASGI application routes websockets through a table built from applications' `websocket_urlpatterns` and nested under the web path; this guide's search found three such modules, giving `/ws/client/`, `/ws/outpost/<uuid:pk>/`, `/ws/rac/<str:token>/` and `/ws/outpost_rac/<str:channel>/` with the default web path `/`. The `/ws/client/` stack resolves the session user, or an anonymous user, and its consumer accepts every connection, joining the user's group only when that user is authenticated. Both outpost routes deny a connection without a bearer token that `TokenAuthentication` accepts; the outpost consumer also requires view permission on that outpost, while the RAC outpost consumer accepts with no outpost-specific check on `/ws/outpost_rac/`. The RAC client consumer accepts, then denies unless the connection token belongs to the session. The flow executor is registered under the API router at `flows/executor/<slug:flow_slug>/` with `AllowAny`; the API schema names that path's GET operation `flows_executor_get`, and the flow interface calls `flowsExecutorGet`, which this guide takes to be the generated client method for that operation, so this guide infers that refusing the whole API prefix would break login. This guide read the Rust server, core and static routers, the root URL module, application mountpoints, the core, flow, API and v3 URL modules, and the websocket table with its three modules; any path list derived from them is bounded by those tables. This guide's proxy advice is not a vendor-supported path-isolation recipe; complete path coverage remains open.

authentik also reaches past this host. Its Compose file, by default, "mounts the Docker socket to the authentik worker container", which the vendor notes "comes with some inherent security risks", and which exists so authentik can deploy and manage outposts. Docker says only trusted users should control its daemon and that the daemon requires root privileges unless rootless mode is used. This guide assesses access to an ordinary rootful daemon socket as host-root-equivalent control. Docker says rootless mode runs the daemon and containers as a non-root user inside a user namespace, without root privileges; this guide assesses the blast radius as the daemon user and what that account can access. The general authentik installation warning and Docker privilege-model sources do not directly demonstrate host-root equivalence or the user-scoped blast radius. Check the daemon type and restrict socket access. The vendor's own options are a Docker socket proxy or removing the mount and deploying outposts by hand. Whichever you choose, check every deployed outpost's exposure. At version/2026.8.3, authentik supports Proxy, LDAP, RADIUS and RAC outposts. Its embedded Proxy outpost runs inside the main server on the same 9000 and 9443 ports, so it does not add a separate listener port. Managed Docker or Kubernetes outposts, and manually deployed outposts, can run elsewhere. The pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. This guide did not trace whether the deployed Proxy outpost image runs the cited Go proxy code at this tag. The Docker controller maps the outpost's ports to the host unless `docker_map_ports` is false; it defaults to true. The Kubernetes controller reconciles Deployment and Service objects. The LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced. This guide assesses that the Verify probes below do not demonstrate any outpost boundary; check each deployed outpost separately.

## Verify

REASONED: scope of every live check below; the authoring host forbids opening listeners without an isolated network namespace, and has none, and ran neither identity provider, while the fenced shell blocks below passed bash -n (Bash 5.3.9) and ShellCheck 0.11.0 at marking time with no diagnostics. Live checks here are **REASONED**: the authoring host forbids opening listeners without an isolated network namespace, and has none. This source audit ran neither identity provider. The expected outcomes, including those of the existing checks below, follow the cited vendor documentation and pinned sources; the pinned curl and Keycloak sources support the documented exit codes, timeout options, proxy controls and listener defaults; no deployed outcome was observed. This guide assesses that a password-only refusal for an already-enrolled administrator does not distinguish enrolment from enforcement: Keycloak's default configured-OTP condition and authentik's validation-stage behaviour can both refuse that login. Test a user with no registered factor and inspect the realm flow or authentik stage settings. The runnable Verify commands below retain their existing pass conditions.

REASONED: authentik setup-flow comparison per the cited pinned root redirect, setup view, OOBE policy and source tests at version/2026.8.3; no disposable authentik instance or isolated test network is available in the authoring environment, so the expected redirects and logins were not observed. For authentik's setup check, use a disposable instance in an isolated test network and a fresh browser session. Open `http://127.0.0.1:9000/` locally or through the SSH forward. In the exposed state, with no bootstrap credentials and no usable `akadmin` password, expect the redirects through `/setup` to `/if/flow/initial-setup/`, then the setup form without a login. Complete it with test credentials and confirm those credentials log in as `akadmin`. After setup, a new anonymous session visiting `/setup` must return through the root to authentication rather than offer setup. Repeat on a fresh instance bootstrapped with `AUTHENTIK_BOOTSTRAP_PASSWORD`: expect login with the supplied password and no setup form. A direct visit to the flow is not a sufficient negative check because it is denied even before setup. The pinned root redirect, setup view, OOBE policy and source tests distinguish these outcomes; the tests were read, not executed here.

REASONED: network-boundary comparison per the cited shipped Compose publications at version/2026.8.3; no isolated exposed fixture or untrusted test client is available in the authoring environment, so neither reachability state was observed. For the network boundary, compare section 1's shipped publications with the loopback replacement using step 1 below. In the isolated exposed fixture, an untrusted test client can reach the setup route; with the loopback mappings and public proxy route closed, that client must not reach it, while the local browser still can. Retain this positive control so a stopped service cannot pass as an effective restriction. Confirm that neither configuration publishes 9300; its wildcard listener inside the container remains a separate monitoring-network boundary.

REASONED: authentik replacement-route design from the pinned core, OAuth2 provider and root URL files; no deployed authentik route was probed. For authentik, substitute the deployed application's OAuth2 discovery URL as the positive control and confirm that its issuer matches the configured global or per-provider value. Check that an untrusted client cannot reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request. Do not refuse the whole API prefix without tracing login dependencies; confirm that an ordinary user can still complete login. The pinned OAuth2 file defines the per-application discovery suffix and `/if/admin/` is a core route. The fetched root module mounts application URLs dynamically; these files do not establish the full `/application/o/` prefix or `/api/v3/` route. These files do not establish whether end-user flow execution uses the API prefix. The Keycloak-route exclusion in the following fence is this guide's inference from the fetched authentik route files, not a proof of every mounted route. For authentik, the discovery-URL and issuer check replaces the following fence comment's allowance to use any endpoint you expect to answer.

REASONED: listener, routing, login, port-isolation and bootstrap-removal checks follow the vendor documentation and pinned sources below; the authoring host has no isolated network namespace for listeners and ran neither identity provider; the pinned curl and Keycloak sources support the documented exit codes, timeout options, proxy controls and listener defaults; no deployed outcome was observed. Expected outcomes and positive controls are recorded in the block.

```bash
# Steps 2 to 5 and 7 must run from a host OUTSIDE every network you have allowed, against a
# system you are authorized to test. Neutralize the proxy settings first, all of them:
# curl reads ALL_PROXY and all_proxy as well as per-scheme variables (http_proxy is
# lowercase only), and it reads ~/.curlrc too. This guide assesses that a proxy whose
# egress sits inside an allowed range can make a blocked endpoint appear reachable
# from a location that should have been refused.
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy NO_PROXY no_proxy
# A function, not a variable: an unquoted $CURL would glob-expand the * against whatever is
# in the reader's current directory, and the command would quietly stop disabling the proxy.
# -q as curl's first option ignores ~/.curlrc, which can itself set a proxy or turn verification off.
probe() { curl -q --noproxy '*' -sS "$@"; }
# Every path below is KEYCLOAK's. authentik does not serve /realms/ or /admin/master/,
# so on authentik substitute its own application and administration URLs; step 2's job is
# to prove this host reaches that name at all, and any endpoint you expect to answer does it.

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
ss -tlnp   # read every listener; 6379/7800/8080/8443/9000/9443/9300/57800: 127.0.0.1 or an RFC 1918 address only
# ss on the HOST does not see a container's own namespace, and a published Docker port
# bypasses the host firewall besides, so cross-check what Compose actually published:
docker compose ps --format 'table {{.Service}}\t{{.Ports}}'
# no 0.0.0.0 or :: on the identity provider's OWN rows. A proxy in the same
# project publishing 443 is correct and expected. This also sees one Compose
# project, not every container on the host.

# 2. POSITIVE CONTROL, and the reason every check below means anything: the public
#    hostname answers from out here. Use the realm your APPLICATIONS use, not master:
#    section 3 restricts the master realm to your administrators' range, so probing it here
#    would test the wrong thing and tell you nothing about the realm your applications use.
probe https://id.example.com/realms/apps/.well-known/openid-configuration \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["issuer"])'
# It must print YOUR issuer URL. A 200 alone proves only that something answered: a wrong
# upstream or a generic responder satisfies it while the real provider sits exposed
# elsewhere. If this does not print the issuer you expect, stop reading and fix that first,
# because every check below will "pass" for the wrong reason.

# 3. The administration console is closed on the PUBLIC hostname.
probe -o /dev/null -w '%{http_code}\n' https://id.example.com/admin/master/console/
# 404 is the pass. A 302 to a login page is NOT a pass: it means the console answered
# and is offering to authenticate you. Any 2xx, any 3xx, 401 or 403 all mean the path
# was served by something.

# 4. The administration REST API is closed on that same hostname. hostname-admin does
#    not do this for you, so this is the step that proves your proxy rule does.
probe -o /dev/null -w '%{http_code}\n' https://id.example.com/admin/realms/master/users
# 404 is the pass. 401 means the API answered and asked for a token.

# 5. The administrative realm's login paths are RESTRICTED, not refused. Section 3 allows
#    them from your administrators' range and denies everything else, so from out here:
#    403 is the pass. nginx answers a denied source with 403, not 404.
#    200 means the allow rule covers the whole internet, or is not there at all.
#    404 means you used `return 404` rather than an allow rule, which closes the path for
#    your administrators too; see section 3 for why the console needs it on this hostname.
probe -o /dev/null -w '%{http_code}\n' \
  https://id.example.com/realms/master/.well-known/openid-configuration
# Steps 3 to 5 sample three routes and expect two different answers: 404 from the two
# /admin/ paths, which are refused outright, and 403 from the master realm, which is
# restricted by source. Either way they prove those three requests were handled as intended,
# not that the whole administration surface is. A more specific `location` elsewhere in the
# same server block can still serve one, so read the effective configuration too.

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

# 7. The management, metrics and application ports are not routable from out here. All of
#    them: a reader who remapped 9000 and left 9443 published passes every other step.
#    --connect-timeout is separate from -m so the two deadlines are distinguishable in the
#    output, not because it changes the exit code: this guide infers that a port that
#    accepts the connection and then stalls, and one never reached before the deadline,
#    can both end in exit 28. The diagnostic may distinguish them, so print it whole.
for p in 8080 8443 9000 9300 9443; do
  err=$(probe --connect-timeout 3 -m 8 -o /dev/null -v "http://id.example.com:$p/" 2>&1 >/dev/null)
  rc=$?
  echo "=== $p: curl exit $rc"
  printf '%s\n' "$err"
done
# Exit 0 means curl completed the HTTP operation, so treat it as an answer. Exit 7 reports
# a connection failure. Treat that as the isolation outcome you want only after checking
# the diagnostic and target. This guide infers that exits 52 and 56 follow an accepted
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
# chased rather than accepted.

# 8. Keycloak's bootstrap admin is gone. This guide infers from manual-removal guidance
#    that it does not expire on its own. Ask for the name
#    rather than listing users: the users endpoint returns at most 100 by default, and a
#    bootstrap account on page two looks exactly like a deleted one.
#    kcadm.sh get users -r master -q exact=true -q "username=REPLACE_WITH_BOOTSTRAP_NAME" --fields username,id
#    Keep exact=true and inspect the returned username: this guide treats `username=`
#    without `exact=true` as a non-exact match; the pinned passage documents only the
#    `q=` form. The result is capped at 100 either way, so an unfiltered list proves
#    nothing about what is not in it. Keep the -q flags in this order as this guide's defensive
#    advice based on a report that exact=true after the username filter did not take
#    effect; the pinned admin CLI documentation does not establish that behaviour, and
#    ordering it defensively costs nothing.
#    Check the master realm's service accounts too: a bootstrap SERVICE account is created
#    by the client-id form of the same mechanism and is not in the user list at all.
```

REASONED: preceding block; all eight steps of that fence, including the listener inventory, routing, administrative login, port isolation and bootstrap-account removal checks, and the repeat coverage across addresses and families and the surfaces that block does not test, per the cited Keycloak and authentik documentation and pinned sources; no deployed provider, isolated network namespace for listeners, or public address is available in the authoring environment, so none of the steps ran; the pinned curl and Keycloak sources support the documented exit codes, timeout options, proxy controls and listener defaults; no deployed outcome was observed. One name is not one address, and one address is not one origin. Repeat steps 2 to 5 and 7 for every public address the name carries and in both families, since a host filtered on IPv4 while it answers on IPv6 passes all of them. A CDN or load balancer answering on 443 also says nothing about whether the backend has its own reachable address, so check the origin directly as well. And nothing here tests `id-admin.internal`, the database, or any authentik outpost's boundary, including the embedded outpost's routes on the core server ports; those surfaces need separate checks. The port list is the one this guide's own topology creates, not an inventory: scan the whole range if you want one.

## Sources (checked September 2026)

- Keycloak production configuration, including the TLS requirement and separating the admin REST API and console: https://www.keycloak.org/server/configuration-production
- Keycloak hostname options, including the production and dev profile defaults for `hostname-strict`, and the statement that `hostname-admin` does not restrict the Administration REST API: https://www.keycloak.org/server/hostname
- Keycloak reverse proxy configuration, including `proxy-headers`, `proxy-trusted-addresses`, the forwarded-header warning, and the exposed-paths table: https://www.keycloak.org/server/reverseproxy
- Keycloak bootstrap and recovery admin accounts, including that the account is temporary and must be removed manually: https://www.keycloak.org/server/bootstrap-admin-recovery
- Keycloak management interface and the default management port 9000: https://www.keycloak.org/server/management-interface
- authentik Docker Compose installation and operational setup instructions (version-specific behavior is pinned below): https://docs.goauthentik.io/install-config/install/docker-compose/
- authentik monitoring, including the separate metrics port 9300 and that the metrics carry no authentication: https://docs.goauthentik.io/sys-mgmt/ops/monitoring
- authentik `version/2026.8.3` shipped Compose, image tag, both publications and the services' `.env` inputs: https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/compose.yml#L1-L67
- authentik `version/2026.8.3` HTTP, HTTPS and metrics wildcard defaults: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/lib/default.yml#L36-L48
- authentik `version/2026.8.3` shared server and worker metrics router and plain HTTP metrics listener: https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/metrics/mod.rs#L70-L100
- authentik `version/2026.8.3` core metrics startup and worker registration: https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/main.rs#L99-L122
- authentik `version/2026.8.3` mode-dependent Prometheus metrics handler: https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/metrics/handlers.rs#L12-L42
- authentik `version/2026.8.3` metrics router wrapper middleware (no authentication layer): https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-axum/src/router.rs#L36-L59
- authentik `version/2026.8.3` outpost Prometheus handler, metrics listen address and Unix socket serving: https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/ak/metrics.go#L18-L72
- authentik `version/2026.8.3` LDAP and LDAPS listener startup, LDAP outpost metrics router and its HTTP and Unix-socket servers: https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/ldap/ldap.go#L91-L121
- authentik `version/2026.8.3` Go web server metrics listener present at the tag: https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/web/metrics.go#L22-L52
- authentik `version/2026.8.3` administration, user and flow URL routes: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L36-L75
- authentik `version/2026.8.3` Go listener configuration fields (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/config/struct.go#L53-L62
- authentik `version/2026.8.3` Go listener startup and API client prefix (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/web.go#L132-L183
- authentik `version/2026.8.3` Go plain HTTP and Unix listeners sharing the router (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/web.go#L229-L288
- authentik `version/2026.8.3` Go application web-path proxy and embedded-outpost handling (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/proxy.go#L47-L127
- authentik `version/2026.8.3` interface rendering and user-type redirect or denial (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/views/interface.py#L54-L89
- authentik `version/2026.8.3` core route entries, API registrations and websocket route (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L36-L112
- authentik `version/2026.8.3` API v3 application registration and URL assembly (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/api/v3/urls.py#L18-L58
- authentik `version/2026.8.3` Bearer parsing, IPC user and token authentication (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/api/authentication.py#L33-L166
- authentik `version/2026.8.3` object and named RBAC permission implementations (checked October 2026): https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/rbac/permissions.py#L15-L60
- authentik `version/2026.8.3` Rust main metrics startup before mode dispatch and per-mode handle storage (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/main.rs#L57-L135
- authentik `version/2026.8.3` Go `cmd/server` command calling `NewWebServer` and `WebServer.Start`, and the developer debug launch configuration targeting it (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/cmd/server/server.go#L25-L73 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/.vscode/launch.json#L37-L42
- authentik `version/2026.8.3` main Dockerfile Rust `authentik` binary built with the `core` feature (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/Dockerfile#L126-L142
- authentik `version/2026.8.3` main image binary copy and `ak` entrypoint (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/Dockerfile#L234-L252
- authentik `version/2026.8.3` `ak` entrypoint running the Rust binary for server, worker and all-in-one, and the function that executes that command (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L16-L33 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L35-L54 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L92-L94
- authentik `version/2026.8.3` Rust server gunicorn Unix-socket backend (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/mod.rs#L86-L106
- authentik `version/2026.8.3` Rust server embedded-outpost routing and HTTP, HTTPS and Unix listeners (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/mod.rs#L260-L352
- authentik `version/2026.8.3` Rust core router websocket upgrade forwarding (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/core.rs#L153-L155
- authentik `version/2026.8.3` Rust core router health, static and gunicorn routes under the web path (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/core.rs#L277-L320
- authentik `version/2026.8.3` shared plain HTTP, Unix-socket and rustls server runners (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-axum/src/server.rs#L22-L170
- authentik `version/2026.8.3` Rust worker-mode HTTP listener and health router (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/worker/mod.rs#L347-L361 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/worker/healthcheck.rs#L66-L76
- authentik `version/2026.8.3` Rust listen configuration fields (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-common/src/config/schema.rs#L184-L190
- authentik `version/2026.8.3` Go TLS listener serving the shared router (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/web/web_tls.go#L46-L72
- authentik `version/2026.8.3` REST framework default authentication, permission and filter classes (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L240-L252
- authentik `version/2026.8.3` root URL configuration and ASGI application settings (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L320-L339
- authentik `version/2026.8.3` app and user settings modules updating REST framework settings (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L566-L609
- authentik `version/2026.8.3` API app `api/` mountpoint and `v3/` mount (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/api/apps.py#L6-L13 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/api/urls.py#L7-L9
- authentik `version/2026.8.3` default web path (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/lib/default.yml#L162-L166
- authentik `version/2026.8.3` websocket routing table and ASGI protocol router (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/websocket.py#L14-L34 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/asgi.py#L75-L83
- authentik `version/2026.8.3` websocket session authentication stack and client message consumer (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/asgi_middleware.py#L42-L84 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/ws/consumer.py#L38-L52
- authentik `version/2026.8.3` outpost websocket route, bearer-token middleware and outpost permission check (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/urls.py#L16-L23 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/channels.py#L13-L43 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/consumer.py#L73-L83
- authentik `version/2026.8.3` RAC websocket routes, client connection-token check and outpost consumer acceptance (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/urls.py#L30-L43 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/consumer_client.py#L63-L96 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/consumer_outpost.py#L14-L16
- authentik `version/2026.8.3` flow executor API route and `AllowAny` permission (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/urls.py#L36-L50 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/views/executor.py#L101-L104
- authentik `version/2026.8.3` flow interface call to the flow executor API, and the API schema's `flows_executor_get` operation for the executor path (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/web/src/flow/FlowExecutor.ts#L221-L225 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/schema.yml#L9288-L9290
- authentik `version/2026.8.3` Rust static interface asset routes (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/static.rs#L159-L168
- authentik `version/2026.8.3` users and groups viewset authentication classes (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/api/users.py#L650-L654 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/api/groups.py#L406-L410
- authentik `version/2026.8.3` root redirect before authentication and setup/flow URL routes: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/views/interface.py#L44-L51 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L59-L70
- authentik `version/2026.8.3` setup planning, completion flag and post-setup superuser requirement: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/setup/views.py#L35-L92
- authentik `version/2026.8.3` OOBE prompts, pending user, started-by/usable-password policy and stage/policy bindings: https://github.com/goauthentik/authentik/blob/version/2026.8.3/blueprints/default/flow-oobe.yaml#L8-L194
- authentik `version/2026.8.3` flow authentication default, planning-time policy check and continuation of existing session plans: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/models.py#L183-L187 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/planner.py#L261-L290 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/views/executor.py#L175-L196
- authentik `version/2026.8.3` bootstrap environment handling and failure/skip conditions: https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/setup/signals.py#L18-L48
- authentik `version/2026.8.3` source tests specifying setup redirects, anonymous password setup, direct-flow denial and bootstrap password/token behavior (read, not run): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/tests/test_setup.py#L26-L130 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/tests/test_setup.py#L168-L245
- authentik `version/2026.8.3` TOTP setup stage (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_totp/models.py#L29-L44
- authentik `version/2026.8.3` WebAuthn setup stage (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_webauthn/models.py#L90-L113
- authentik `version/2026.8.3` OutpostConfig definition and Docker port-mapping default (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/models.py#L53-L85
- authentik `version/2026.8.3` outpost types (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/models.py#L99-L105
- authentik `version/2026.8.3` outpost deployment and provider types (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/index.mdx#L6-L13
- authentik `version/2026.8.3` Docker, Kubernetes and manual outpost deployment (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/index.mdx#L30-L48
- authentik `version/2026.8.3` embedded proxy outpost and shared server ports (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/embedded/embedded.mdx#L5-L15
- authentik `version/2026.8.3` proxy outpost HTTP, HTTPS and metrics listeners (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/proxyv2/proxyv2.go#L172-L202
- authentik `version/2026.8.3` RADIUS outpost and metrics listeners (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/radius/radius.go#L100-L125
- authentik `version/2026.8.3` Docker outpost controller conditional port mapping (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/controllers/docker.py#L218-L230
- authentik `version/2026.8.3` Kubernetes outpost Deployment and Service reconcilers (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/controllers/kubernetes.py#L65-L88
- authentik `version/2026.8.3` OAuth2 provider discovery suffix (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/urls.py#L53-L63
- authentik `version/2026.8.3` global and per-provider issuer modes (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/models.py#L115-L122
- authentik `version/2026.8.3` issuer URL construction (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/models.py#L365-L378
- authentik `version/2026.8.3` application URL mounting and web path (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/urls.py#L18-L48
- authentik `version/2026.8.3` security-policy supported-version table at the time of writing (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/SECURITY.md#L25-L32
- Keycloak `26.7.4` security-policy upgrade guidance (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/SECURITY.md#L42-L48
- Keycloak `26.7.4` realm export backup limitations and stop-node conditions (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/importExport.adoc#L11-L16
- Docker Engine security, daemon root requirement, trusted daemon users and host filesystem access (checked October 2026): https://docs.docker.com/engine/security/
- Docker Engine rootless mode, daemon and containers without root privileges (checked October 2026): https://docs.docker.com/engine/security/rootless/
- Docker daemon privileges, trusted control and host filesystem access, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112
- Docker rootless non-root daemon and containers in a user namespace, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/rootless/_index.md#L8-L21
- curl `curl-8_23_0` exit-code list, defining exit 7 as a connection failure: https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/_EXITCODES.md#L23-L24
- Keycloak `26.7.4` Admin CLI user filtering example and its non-exact matching note (no documented flag-order behaviour): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/admin-cli.adoc#L1034-L1045
- Keycloak server administration guide, brute force detection ("Brute force detection is disabled by default") and unspecific redirect URIs: https://www.keycloak.org/docs/latest/server_admin/index.html
- nginx `location` selection and the `return` directive: https://nginx.org/en/docs/http/ngx_http_core_module.html#location , https://nginx.org/en/docs/http/ngx_http_rewrite_module.html#return
- Keycloak configuring distributed caches, including the default cache ports 7800 (`cache-embedded-network-bind-port`, unicast data transmission) and 57800 (`jgroups.fd.port-offset`, failure detection), and that "Encryption using TLS is enabled by default for TCP-based transport stacks": https://www.keycloak.org/server/caching
- authentik 2025.10 release notes, removing the Redis dependency ("authentik no longer uses Redis at all"): https://docs.goauthentik.io/releases/2025.10/
- authentik source `version/2026.8.3`, MFA response validation (including empty-response rejection), successful-validation continuation and remembered-MFA cookie handling (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L67-L166 , https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L368-L443
- Keycloak `26.7.4` bootstrap-admin-recovery.adoc L9-L11 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/bootstrap-admin-recovery.adoc#L9-L11
- Keycloak `26.7.4` flows.adoc L35 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L35-L35
- Keycloak `26.7.4` flows.adoc L37-L57 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L37-L57
- Keycloak `26.7.4` flows.adoc L135-L143 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L135-L143
- Keycloak `26.7.4` webauthn.adoc L19-L28 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L19-L28
- Keycloak `26.7.4` webauthn.adoc L51-L55 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L51-L55
- Keycloak `26.7.4` con-required-actions.adoc L6-L20 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/users/con-required-actions.adoc#L6-L20
- Keycloak `26.7.4` HttpOptions.java L13-L17 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L13-L17
- Keycloak `26.7.4` HttpOptions.java L31-L41 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L31-L41
- Keycloak `26.7.4` reverseproxy.adoc L119-L129 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/reverseproxy.adoc#L119-L129
- authentik `version/2026.8.3` stages/authenticator_validate/models.py L15-L21 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/models.py#L15-L21
- authentik `version/2026.8.3` stages/authenticator_validate/models.py L45-L50 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/models.py#L45-L50
- authentik `version/2026.8.3` stage.py L279-L289 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L279-L289
- authentik `version/2026.8.3` stage.py L292-L317 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L292-L317
- authentik `version/2026.8.3` flows/models.py L254-L262 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/models.py#L254-L262
- authentik `version/2026.8.3` planner.py L337-L343 (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/planner.py#L337-L343
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
- Keycloak `26.7.4` otp-policies.adoc L17-L21 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L17-L21
- Keycloak `26.7.4` HttpOptions.java L19-L22 (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L19-L22


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- keycloak-admin-cli: Keycloak Admin CLI (26.7.4)
- keycloak-2674: Keycloak source (26.7.4)
- authentik: authentik source (version/2026.8.3)
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
- http-listener (REASONED; keycloak, keycloak-2674): The example starts Keycloak with HTTPS frontend/admin hostnames, xforwarded parsing and http-enabled=true for backend HTTP on default port 8080 on a protected proxy hop; the HTTPS port defaults to 8443. At 26.7.4, the HTTP listener option defaults false but is enabled by default in development mode. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.
- admin-hostname (REASONED; keycloak): hostname-admin selects the console/API hostname but does not restrict the Administration REST API through the frontend URL.
- admin-deny (REASONED; keycloak, nginx): Deny /admin/ on the public hostname at the proxy; the sample returns 404.
- master-realm (REASONED; keycloak): Restrict /realms/master/ by administrator source network while keeping application /realms/ exposed; a blanket denial locks out administrators.
- admin-login-route (REASONED; keycloak): Console API calls use hostname-admin but console authentication uses the frontend master realm; the private admin proxy also needs /admin/, /resources/, /.well-known/ and version-dependent /js/.
- forwarded-headers (REASONED; keycloak): Overwrite all five X-Forwarded-For/Proto/Host/Port/Prefix headers and Host; appending or passing client values permits spoofing.
- proxy-trust (REASONED; keycloak): proxy-trusted-addresses limits accepted forwarded headers to proxy addresses but is weak protection, not a substitute for header overwriting.
- proxy-origin (REASONED; keycloak): Without proxy-headers, non-passthrough proxied requests that perform origin checks return 403 by default.
- setup-routing (REASONED; authentik): Before setup, authentik root redirects via /setup to /if/flow/initial-setup/; a fresh direct flow visit lacks the public setup marker and is denied.
- setup-claim (REASONED; authentik): Initial setup plans only when akadmin is absent or lacks a usable password, then prompts email/base URL/password, writes akadmin and logs in the visitor.
- setup-completion (REASONED; authentik): Completion records setup done, disables OOBE blueprints and requires a superuser; planning-time checks do not promise revocation of already-started sessions.
- setup-isolation (REASONED; authentik, authentik-docs): Keep both web ports and public proxy route closed to untrusted clients until setup is complete; use loopback or a private container network and confirm closure in a fresh session.
- bootstrap-inputs (REASONED; authentik): Before first startup, protected .env can provide AUTHENTIK_BOOTSTRAP_PASSWORD, PASSWORD_HASH or TOKEN; any nonempty input triggers bootstrap and successful blueprint application completes setup.
- bootstrap-lifecycle (REASONED; authentik): Hash form is validated; password forms set akadmin password and token form supplies an API token, not a browser password. Already-setup tenants are skipped, so these inputs are not rotation.
- bootstrap-cleanup (REASONED; authentik): Verify bootstrap and setup closure before publication, then remove the bootstrap secret from the startup environment and protect file/container-inspection access.
- keycloak-bootstrap (REASONED; keycloak, keycloak-2674): Keycloak bootstrap admin is temporary and needs manual removal after establishing permanent, more secure, MFA-protected admin access (this guide's requirement); this guide infers from the manual-removal instruction that it does not expire on its own. MFA protection requires a factor in the authentication flow, not only enrolment.
- keycloak-management (REASONED; keycloak): Enabled Keycloak health and metrics use management port 9000; keep it private and use /health/ready for the orchestrator.
- management-mtls (REASONED; keycloak): https-management-client-auth accepts none/request/required and inherits HTTP settings; this plaintext topology needs management TLS credentials and trust before client certificates can authenticate it.
- authentik-metrics (REASONED; authentik): At version/2026.8.3, the Rust core metrics listener uses plain HTTP with default [::]:9300, and the main Dockerfile ships the Rust binary run by ak; whether published images were built from it is NOT ESTABLISHED. The shipped Compose file does not publish 9300, but the container-network listener still needs restriction.
- authentik-go-metrics (REASONED; authentik): At version/2026.8.3, a Go web server metrics listener is also present: cmd/server calls WebServer.Start, which calls runMetricsServer per listen.metrics address. No image or release build of cmd/server was found in the pinned tree; a developer debug launch targets it. The main Dockerfile ships the Rust binary instead; whether published images were built from it is NOT ESTABLISHED.
- authentik-metrics-startup (REASONED; authentik): At version/2026.8.3, the Rust main starts the metrics server before the per-mode dispatch (healthcheck exits earlier), including proxy mode in proxy-feature builds; Server and AllInOne store the server handle, Worker and AllInOne the worker handles. Whether the published image was built from the tree's Dockerfile is NOT ESTABLISHED.
- worker-outpost-metrics (REASONED; authentik): At version/2026.8.3, worker startup uses the same Rust metrics server as server mode; its handler serves Prometheus metrics on listen.metrics (default [::]:9300) via plain HTTP, with no authentication layer in the router wrapper. The LDAP outpost builds its metrics router with a bare Prometheus handler at /metrics and serves it on each metrics listen address and a Unix socket; section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced. Restrict to monitoring clients.
- keycloak-mfa (REASONED; keycloak, keycloak-2674): Enrol administrator TOTP or WebAuthn and require the factor in the realm authentication flow. When Keycloak's default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. A Required second factor can instead be enrolled during authentication without proving possession of a preexisting factor, so test an administrator with no registered factor and inspect the flow.
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
- verify-admin-login (REASONED; keycloak): An allowed administrator must complete real login through the private console and frontend master realm; outside sources must fail.
- verify-direct-ports (REASONED; keycloak, authentik, curl, keycloak-2674): Probe 8080/8443/9000/9300/9443 directly: curl exit 0 reports a completed operation, 7 reports a connection failure, and 28 is an inconclusive timeout requiring full diagnostics to distinguish accepted-then-stalled from unreachable. Treat a connection failure as the desired isolation outcome only after checking the diagnostic and target; this guide infers that exits 52 and 56 follow an accepted connection, so a listener is reachable. Other exits require diagnostic review. The connection and full-transfer deadlines differ. The checks remain REASONED expectations, not observed outcomes.
- verify-bootstrap-removal (REASONED; keycloak, keycloak-admin-cli): Look up the bootstrap username with exact=true rather than a default 100-result user list, inspect the returned username, and separately check bootstrap service accounts. Keycloak documents non-exact matching for its -q q=username: filter; this guide keeps the -q order (exact=true first) as defensive advice based on a report, not documented ordering behaviour.
- verify-address-coverage (REASONED; keycloak, authentik-docs): Repeat external checks for every public IPv4/IPv6 address and the origin; private admin, database and outposts need separate checks, and the listed ports are not a full inventory.
- authentik-mfa (REASONED; authentik-docs, authentik): authentik has TOTP and WebAuthn setup stages; enrol a phishing-resistant administrator factor before connecting the first app and require it through an Authenticator Validate stage bound to the authentication flow (this guide's requirement; the cited sources do not state this ordering). A registered device alone does not establish the flow binding. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The pinned validate-stage and flow-binding sources support these behaviours but do not establish an administrator-specific factor policy.
- authentik-admin-boundary (REASONED; authentik): At version/2026.8.3, /if/admin/, /if/user/ and flows share core routing. This guide assesses that authentik has no equivalent to hostname-admin: the cited configuration, Go startup and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. The permission boundary remains unestablished.
- authentik-admin-listeners (REASONED; authentik): At version/2026.8.3, defaults are HTTP [::]:9000, HTTPS [::]:9443 and metrics [::]:9300; Go startup adds these configured listeners and a Unix socket, and its plain HTTP, HTTPS and Unix listeners share the application proxy router after outpost handling. These files show shared routing, not a separate admin port, and do not prove which listeners a deployed build starts.
- authentik-admin-interface (REASONED; authentik): At version/2026.8.3, both interface routes redirect authenticated external, service-account and internal-service-account users to a default app or deny them; other requests fall through. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.
- authentik-admin-api-mount (REASONED; authentik): At version/2026.8.3, API v3 registers application API routes, including core users, groups, tokens and admin authenticators. The root URL configuration mounts each app under the web path; the API app mounts api/ and then v3/, so the v3 router is at &lt;web path&gt;api/v3/, /api/v3/ by default, matching the Go client's api/v3 prefix. Endpoint permission wiring is not established by these files.
- authentik-admin-api-auth (REASONED; authentik): At version/2026.8.3, TokenAuthentication recognizes API-intent tokens, API-scoped OAuth tokens, the managed-outpost secret and IPC key; it rejects inactive users and unrecognized credentials, but absent or unsupported authentication can return no user. This does not establish session authentication or every endpoint adopting this class.
- authentik-admin-rbac (REASONED; authentik): At version/2026.8.3, ObjectPermissions' request check passes object-lookup requests (its comment leaves view checks to ObjectFilter, writes to the object check) and permits configured creation without add permission; the object check accepts global permissions or configured ownership before delegating. HasPermission checks user.has_perms; endpoint wiring and permission boundary stay unestablished.
- authentik-admin-proxy (REASONED; authentik): Build any network boundary around authentik administration at the proxy using path restrictions; identify and test required paths for the deployed version and maintain the list. This guide assesses that the UI is not designed around this separation and path-based separation is difficult to maintain; this is not a vendor-supported recipe, and the cited files give no complete path list.
- authentik-admin-paths (REASONED; authentik): At version/2026.8.3, core URLs show /if/admin/, /if/user/, flows, HTTP admin-template fallbacks at /ws/outpost/&lt;uuid:pk&gt;/ and /ws/client/, and a /ws/client/ websocket route wrapped in authentication middleware. With the API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization.
- authentik-rust-listeners (REASONED; authentik): At version/2026.8.3, the main Dockerfile ships the Rust binary run by ak. Server mode runs gunicorn on a Unix socket and serves one router over HTTP on listen.http, rustls on listen.https and a Unix socket, sending embedded-outpost apps to the outpost and the rest via the core router to gunicorn. Worker mode serves health checks on listen.http. Deployed topology beyond Compose is NOT ESTABLISHED.
- authentik-api-defaults (REASONED; authentik): At version/2026.8.3, REST framework defaults are TokenAuthentication then SessionAuthentication, ObjectPermissions and an ObjectFilter backend; app and user settings modules can update them, and no app settings module was found doing so. Users and groups add AgentAuth; the flow executor uses AllowAny. SessionAuthentication's implementation and deployment overrides are NOT ESTABLISHED.
- authentik-admin-websockets (REASONED; authentik): At version/2026.8.3, websocket routes under the web path (/ws/... by default) are /ws/client/, /ws/outpost/&lt;uuid:pk&gt;/, /ws/rac/&lt;str:token&gt;/ and /ws/outpost_rac/&lt;str:channel&gt;/. /ws/client/ resolves a session or anonymous user and accepts every connection; the RAC client consumer on /ws/rac/ accepts, then denies the connection when its token is not bound to the session.
- authentik-outpost-websockets (REASONED; authentik): At version/2026.8.3, under the configured web path (shown with the default /), the /ws/outpost/ and /ws/outpost_rac/ websocket routes deny a connection without a bearer token that TokenAuthentication accepts; /ws/outpost/ also requires outpost view permission, while the RAC outpost consumer accepts with no outpost-specific check on /ws/outpost_rac/.
- authentik-admin-api-shared (REASONED; authentik): At version/2026.8.3, the flow executor is registered under the API router at flows/executor/&lt;slug:flow_slug&gt;/ with AllowAny, the API schema names that path's GET flows_executor_get, and the flow interface calls flowsExecutorGet, taken here as that operation's generated client method, so this guide infers that refusing the whole API prefix would break login.
- authentik-admin-static-paths (REASONED; authentik): At version/2026.8.3, the Rust static router also serves /if/admin/assets/ under the configured web path (shown with the default /) alongside the user, flow and RAC interface assets. Path lists from the routing tables this guide read are bounded by those tables; complete path coverage remains open.
- verify-mfa-password (REASONED; keycloak, authentik-docs, authentik, keycloak-2674): For both providers, open a fresh session with only the administrator password and confirm access is refused after factor enforcement. This guide assesses that an already-enrolled administrator's password-only refusal does not distinguish enrolment from enforcement; test a user with no registered factor and inspect the flow or stage settings. Keycloak's default conditional 2FA, when reached (a successful Cookie execution skips it), prompts for configured OTP unless passwordless WebAuthn already authenticated the user; the default flow's WebAuthn Authenticator execution is disabled by default; and a Required factor the user lacks can be enrolled during authentication. At authentik version/2026.8.3, the unconfigured-device action defaults to SKIP; DENY refuses a user with no allowed device. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. Bind the validation stage to the authentication flow.
- management-auth-default (REASONED; keycloak): In this plain-HTTP Keycloak topology no HTTP client authentication is configured, so inherited management client authentication is usually none; required needs management TLS credentials and trust first.
- docker-socket-scope (REASONED; authentik-docs, authentik, docker-engine, docker-engine-pinned): Docker's daemon requires root unless rootless (daemon and containers run non-root); only trusted users should control it. For authentik's shipped Compose worker socket, check daemon type and restrict access: this guide assesses ordinary rootful access as host-root-equivalent and rootless blast radius as the daemon user and what it can access; sources do not directly demonstrate either assessment.
- outpost-boundaries (REASONED; authentik-docs, authentik): At version/2026.8.3, authentik supports Proxy, LDAP, RADIUS and RAC outposts. The embedded Proxy outpost runs in the main server and shares ports 9000 and 9443; managed or manually deployed outposts can run elsewhere. The pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. This guide did not trace whether the deployed Proxy outpost image runs the cited Go proxy code at this tag. The Docker controller maps the outpost's ports to the host unless docker_map_ports is false; it defaults to true. The Kubernetes controller reconciles Deployment and Service objects. LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced. This guide requires separate exposure checks for each deployed outpost and assesses that its Verify probes do not demonstrate them; the embedded outpost shares the core server ports rather than opening another port.
- verify-proxy-neutralization (REASONED; keycloak, curl): Run external probes outside every allowed network; unset HTTP/HTTPS/ALL/NO_PROXY variables in both cases and use curl -q --noproxy '*' to bypass proxies and curlrc, which this guide assesses could otherwise make blocked endpoints appear reachable through allowed egress. Curl's HTTP proxy environment variable is lowercase only; -q must be curl's first option.
- verify-authentik-routes (REASONED; authentik-docs, authentik): The fenced paths are Keycloak-specific; the exclusion of Keycloak paths from authentik is this guide's inference from the fetched route files, not an exhaustive route proof. For authentik, use a deployed application's actual OAuth2 discovery URL as the positive control and confirm its configured issuer; an untrusted client must not reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request. Do not refuse the whole API prefix without tracing login dependencies; confirm that an ordinary user can still complete login. At version/2026.8.3 the OAuth2 URL module defines the per-application discovery suffix and the issuer can be global or per-provider; /if/admin/ is a core route. The fetched root module mounts application URLs dynamically, so these files do not establish the full /application/o/ prefix or /api/v3/ route. These files do not establish whether end-user flow execution uses the API prefix. A responding status alone is not the positive-control pass condition.
- admin-factor-order (REASONED; keycloak, authentik-docs, keycloak-2674, authentik): Enrol a phishing-resistant factor on the administrator account of either provider before connecting the first application and enforce it in the flow (this guide's requirement; the cited sources do not state this ordering). Keycloak documents Required executions; authentik version/2026.8.3 binds ordered stages to flows, but the cited files do not establish an administrator-specific factor policy.
- keycloak-http-opt-in (REASONED; keycloak, keycloak-2674): In the production example, backend plain HTTP on default port 8080 exists only when explicitly enabled with --http-enabled=true; confine that hop to loopback or a controlled private segment. At 26.7.4, the HTTP listener option defaults false but is enabled by default in development mode, and HTTPS defaults to port 8443. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.
- idp-maintenance (REASONED; keycloak, authentik-docs, authentik, keycloak-2674): This guide requires patching, tested backups and keeping a self-hosted identity provider available (this guide's requirement; the cited files do not prescribe a cadence). This guide assesses that a compromised or unavailable self-hosted identity provider takes its dependent services with it. At the time of writing, authentik's version/2026.8.3 security policy lists 2026.5.x and 2026.8.x as supported; Keycloak 26.7.4's security policy says that, depending on severity, vulnerabilities may be fixed in the current major.minor release, or lower-severity vulnerabilities or hardening in the following major.minor release; it encourages those unable to upgrade regularly to consider the Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak cautions that realm export alone has backup limitations: consistency is not guaranteed unless all nodes are stopped before the export, and user and admin events, persisted sessions, workflow state and revoked tokens are omitted. These sources do not establish a complete backup procedure for either provider, an authentik upgrade procedure, a universal maintenance cadence or a tested restore.

````json
{
  "schema": 1,
  "checked": "2026-10-20",
  "documentation_checked": "2026-09",
  "body_sha256": "6e3bce4a31664c097cfa8a3a1ad4cb0b97959550fb400ec7d15b1a3c7333e660",
  "components": {
    "keycloak-admin-cli": {
      "name": "Keycloak Admin CLI",
      "basis": "26.7.4",
      "sources": {
        "s5ac2f5372c57": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/admin-cli.adoc#L1034-L1045"
      }
    },
    "keycloak-2674": {
      "name": "Keycloak source",
      "basis": "26.7.4",
      "sources": {
        "s1fb3333c07a5": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/bootstrap-admin-recovery.adoc#L9-L11",
        "sd063782d3773": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L35-L35",
        "se3124b00898b": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L37-L57",
        "s363518a7ce4e": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/flows.adoc#L135-L143",
        "sfb37d49fcd4b": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L19-L28",
        "sc8bd753b9527": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/webauthn.adoc#L51-L55",
        "s5f753a0620d2": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/users/con-required-actions.adoc#L6-L20",
        "s07c5f54d49d7": "https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L13-L17",
        "s631013c7f55c": "https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L31-L41",
        "s13a81516d2b4": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/reverseproxy.adoc#L119-L129",
        "s68519e76f8c8": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L17-L21",
        "sf10fbdd955bd": "https://github.com/keycloak/keycloak/blob/26.7.4/quarkus/config-api/src/main/java/org/keycloak/config/HttpOptions.java#L19-L22",
        "s694bac50be88": "https://github.com/keycloak/keycloak/blob/26.7.4/SECURITY.md#L42-L48",
        "s85c8eccedd6a": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/importExport.adoc#L11-L16"
      }
    },
    "authentik": {
      "name": "authentik source",
      "basis": "version/2026.8.3",
      "sources": {
        "s0acea2a7f75f": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/setup/signals.py#L18-L48",
        "s865b0b9b23cc": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/setup/views.py#L35-L92",
        "s7ad14bbb32f2": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/tests/test_setup.py#L168-L245",
        "sd73827ef7cf2": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/tests/test_setup.py#L26-L130",
        "sd7afd3968b71": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L59-L70",
        "s348351d7d65e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L36-L75",
        "s34e83c639478": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/views/interface.py#L44-L51",
        "s9448abb2f46e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/models.py#L183-L187",
        "s14fd7774b1bc": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/planner.py#L261-L290",
        "s9d78a6f8341a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/views/executor.py#L175-L196",
        "sb6abd20b147e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/lib/default.yml#L36-L48",
        "s1703fbdd4af2": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/blueprints/default/flow-oobe.yaml#L8-L194",
        "s6ef2a53196aa": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/metrics/mod.rs#L70-L100",
        "sbd91cec2c31b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/main.rs#L99-L122",
        "se88010d6d96b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/metrics/handlers.rs#L12-L42",
        "sbf6b0257ceee": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-axum/src/router.rs#L36-L59",
        "sf6c661b51ec1": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/ak/metrics.go#L18-L72",
        "sb5dbba465354": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/ldap/ldap.go#L91-L121",
        "safa24c359f2d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/web/metrics.go#L22-L52",
        "s20f8787bddf2": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/compose.yml#L1-L67",
        "s6b4af3243161": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L67-L166",
        "s4ce54a5b84c8": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L368-L443",
        "sd44d285958df": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/models.py#L15-L21",
        "seb7e2b93f90d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/models.py#L45-L50",
        "s6562dd778e9e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L279-L289",
        "s0af3ecd559b6": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L292-L317",
        "s4502a88a3ace": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/models.py#L254-L262",
        "s0d77ce39834b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/planner.py#L337-L343",
        "s4ebd0cc01832": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_totp/models.py#L29-L44",
        "s24e69eaacb04": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_webauthn/models.py#L90-L113",
        "see76fb8454ce": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/models.py#L53-L85",
        "s7ae2d123b0f2": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/models.py#L99-L105",
        "s126d3ca5ebeb": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/index.mdx#L6-L13",
        "se716e28f85db": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/index.mdx#L30-L48",
        "s7a25610cceaa": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/add-secure-apps/outposts/embedded/embedded.mdx#L5-L15",
        "sca0f5839c601": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/proxyv2/proxyv2.go#L172-L202",
        "s8fc4619c4d4b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/outpost/radius/radius.go#L100-L125",
        "s9f8f5dfeca92": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/urls.py#L53-L63",
        "s2b2c994a59e6": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/models.py#L115-L122",
        "s91525f4e30dc": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/oauth2/models.py#L365-L378",
        "s5a70f3599721": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/urls.py#L18-L48",
        "s926fad656b61": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/SECURITY.md#L25-L32",
        "s71722cfad526": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/controllers/docker.py#L218-L230",
        "sfb87a6898f29": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/controllers/kubernetes.py#L65-L88",
        "sd02909e948ae": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/config/struct.go#L53-L62",
        "sddf26c6bdc5c": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/web.go#L132-L183",
        "s9c8058b95d3c": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/web.go#L229-L288",
        "s427c0d034db0": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/internal/web/proxy.go#L47-L127",
        "sda44b474a18b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/views/interface.py#L54-L89",
        "s3e60cde54f52": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/urls.py#L36-L112",
        "se0352eb4cba5": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/api/v3/urls.py#L18-L58",
        "sc39e062f1417": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/api/authentication.py#L33-L166",
        "sccd0d60249a7": "https://github.com/goauthentik/authentik/blob/e5a0d2f7572cb776eee7a3e9355937ce38973761/authentik/rbac/permissions.py#L15-L60",
        "s318165203c9d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/main.rs#L57-L135",
        "s619cee70c0ba": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/cmd/server/server.go#L25-L73",
        "sce0e5699f78f": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/Dockerfile#L126-L142",
        "sb1c63be23964": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/container/Dockerfile#L234-L252",
        "s99d9d5b23e9a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L16-L33",
        "scc468aa2294d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L92-L94",
        "s4cf169f29540": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/mod.rs#L86-L106",
        "sce4e17d31a9e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/mod.rs#L260-L352",
        "s60d269cdd686": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/core.rs#L153-L155",
        "s9b5f3bca8761": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/core.rs#L277-L320",
        "sa28f81f21b1d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-axum/src/server.rs#L22-L170",
        "s15c00e95792d": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/worker/mod.rs#L347-L361",
        "s70fd69dc00dc": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/worker/healthcheck.rs#L66-L76",
        "seb9056af7a7b": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/packages/ak-common/src/config/schema.rs#L184-L190",
        "sa2fe855c9416": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/internal/web/web_tls.go#L46-L72",
        "s8e634e5a47bd": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L240-L252",
        "s61c7672e8c51": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L320-L339",
        "s5635e9e0c9be": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/settings.py#L566-L609",
        "sbe6392bdb300": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/api/apps.py#L6-L13",
        "s3e274c13f369": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/api/urls.py#L7-L9",
        "sce23f2109660": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/lib/default.yml#L162-L166",
        "s66c517125520": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/websocket.py#L14-L34",
        "se23cfb7021b4": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/asgi.py#L75-L83",
        "s4e91718909bd": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/asgi_middleware.py#L42-L84",
        "s455913b95a83": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/root/ws/consumer.py#L38-L52",
        "s2ea54ff41b58": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/urls.py#L16-L23",
        "sd50a3c0e1d5a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/channels.py#L13-L43",
        "sd7bc33be13a7": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/outposts/consumer.py#L73-L83",
        "s5f0e15341809": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/urls.py#L30-L43",
        "sde79042b101e": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/consumer_client.py#L63-L96",
        "s805bd431630c": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/urls.py#L36-L50",
        "sfc21d0891247": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/flows/views/executor.py#L101-L104",
        "s3b6031f49229": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/web/src/flow/FlowExecutor.ts#L221-L225",
        "se6949824fb7c": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/src/server/static.rs#L159-L168",
        "sb99c372bb642": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/api/users.py#L650-L654",
        "sa76f25db4854": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/core/api/groups.py#L406-L410",
        "s866a7dcd455a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/lifecycle/ak#L35-L54",
        "s3b480458ab74": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/.vscode/launch.json#L37-L42",
        "s1392b147416c": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/providers/rac/consumer_outpost.py#L14-L16",
        "sb7089c82fae9": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/schema.yml#L9288-L9290"
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
    "authentik-publications": {"text": "Shipped Compose publishes 9000:9000 and 9443:9443 by default without host addresses, exposing all host interfaces under Docker publishing defaults; it does not publish 9300.", "components": ["authentik"], "sources": ["authentik:s20f8787bddf2"], "status": "REASONED"},
    "authentik-web-binds": {"text": "listen.http and listen.https default to [::]:9000 and [::]:9443 inside the container, independently of host publication.", "components": ["authentik"], "sources": ["authentik:sb6abd20b147e"], "status": "REASONED"},
    "authentik-loopback": {"text": "Replace the Compose ports list with 127.0.0.1:9000:9000 and 127.0.0.1:9443:9443; adding entries can retain old publications.", "components": ["authentik", "authentik-docs"], "sources": ["authentik:s20f8787bddf2", "authentik-docs:sb44156cde339"], "status": "REASONED"},
    "production-tls": {"text": "Keycloak production requires a secure channel; edge TLS termination needs a protected loopback or controlled private proxy hop.", "components": ["keycloak"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "hostname-defaults": {"text": "Production start requires explicit hostname or hostname-strict false; start-dev defaults hostname-strict false. Keep strict hostname resolution in production unless the proxy overwrites Host.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f"], "status": "REASONED"},
    "http-listener": {"text": "The example starts Keycloak with HTTPS frontend/admin hostnames, xforwarded parsing and http-enabled=true for backend HTTP on default port 8080 on a protected proxy hop; the HTTPS port defaults to 8443. At 26.7.4, the HTTP listener option defaults false but is enabled by default in development mode. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.", "components": ["keycloak", "keycloak-2674"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c", "keycloak-2674:s07c5f54d49d7", "keycloak-2674:s631013c7f55c", "keycloak-2674:s13a81516d2b4", "keycloak-2674:sf10fbdd955bd"], "status": "REASONED"},
    "admin-hostname": {"text": "hostname-admin selects the console/API hostname but does not restrict the Administration REST API through the frontend URL.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f"], "status": "REASONED"},
    "admin-deny": {"text": "Deny /admin/ on the public hostname at the proxy; the sample returns 404.", "components": ["keycloak", "nginx"], "sources": ["keycloak:sffc6123bea5c", "nginx:s8d8f3323b468"], "status": "REASONED"},
    "master-realm": {"text": "Restrict /realms/master/ by administrator source network while keeping application /realms/ exposed; a blanket denial locks out administrators.", "components": ["keycloak"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "admin-login-route": {"text": "Console API calls use hostname-admin but console authentication uses the frontend master realm; the private admin proxy also needs /admin/, /resources/, /.well-known/ and version-dependent /js/.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED"},
    "forwarded-headers": {"text": "Overwrite all five X-Forwarded-For/Proto/Host/Port/Prefix headers and Host; appending or passing client values permits spoofing.", "components": ["keycloak"], "sources": ["keycloak:sffc6123bea5c"], "status": "REASONED"},
    "proxy-trust": {"text": "proxy-trusted-addresses limits accepted forwarded headers to proxy addresses but is weak protection, not a substitute for header overwriting.", "components": ["keycloak"], "sources": ["keycloak:sffc6123bea5c"], "status": "REASONED"},
    "proxy-origin": {"text": "Without proxy-headers, non-passthrough proxied requests that perform origin checks return 403 by default.", "components": ["keycloak"], "sources": ["keycloak:sffc6123bea5c"], "status": "REASONED"},
    "setup-routing": {"text": "Before setup, authentik root redirects via /setup to /if/flow/initial-setup/; a fresh direct flow visit lacks the public setup marker and is denied.", "components": ["authentik"], "sources": ["authentik:s34e83c639478", "authentik:sd7afd3968b71", "authentik:s865b0b9b23cc", "authentik:s1703fbdd4af2"], "status": "REASONED"},
    "setup-claim": {"text": "Initial setup plans only when akadmin is absent or lacks a usable password, then prompts email/base URL/password, writes akadmin and logs in the visitor.", "components": ["authentik"], "sources": ["authentik:s1703fbdd4af2"], "status": "REASONED"},
    "setup-completion": {"text": "Completion records setup done, disables OOBE blueprints and requires a superuser; planning-time checks do not promise revocation of already-started sessions.", "components": ["authentik"], "sources": ["authentik:s865b0b9b23cc", "authentik:s9448abb2f46e", "authentik:s14fd7774b1bc", "authentik:s9d78a6f8341a"], "status": "REASONED"},
    "setup-isolation": {"text": "Keep both web ports and public proxy route closed to untrusted clients until setup is complete; use loopback or a private container network and confirm closure in a fresh session.", "components": ["authentik", "authentik-docs"], "sources": ["authentik:s20f8787bddf2", "authentik:s865b0b9b23cc", "authentik-docs:sb44156cde339"], "status": "REASONED"},
    "bootstrap-inputs": {"text": "Before first startup, protected .env can provide AUTHENTIK_BOOTSTRAP_PASSWORD, PASSWORD_HASH or TOKEN; any nonempty input triggers bootstrap and successful blueprint application completes setup.", "components": ["authentik"], "sources": ["authentik:s0acea2a7f75f", "authentik:s20f8787bddf2"], "status": "REASONED"},
    "bootstrap-lifecycle": {"text": "Hash form is validated; password forms set akadmin password and token form supplies an API token, not a browser password. Already-setup tenants are skipped, so these inputs are not rotation.", "components": ["authentik"], "sources": ["authentik:s0acea2a7f75f", "authentik:s7ad14bbb32f2"], "status": "REASONED"},
    "bootstrap-cleanup": {"text": "Verify bootstrap and setup closure before publication, then remove the bootstrap secret from the startup environment and protect file/container-inspection access.", "components": ["authentik"], "sources": ["authentik:s0acea2a7f75f", "authentik:s20f8787bddf2"], "status": "REASONED"},
    "keycloak-bootstrap": {"text": "Keycloak bootstrap admin is temporary and needs manual removal after establishing permanent, more secure, MFA-protected admin access (this guide's requirement); this guide infers from the manual-removal instruction that it does not expire on its own. MFA protection requires a factor in the authentication flow, not only enrolment.", "components": ["keycloak", "keycloak-2674"], "sources": ["keycloak:sbbd55dcb81cd", "keycloak:sefec90245fa1", "keycloak-2674:s1fb3333c07a5", "keycloak-2674:se3124b00898b", "keycloak-2674:sc8bd753b9527"], "status": "REASONED"},
    "keycloak-management": {"text": "Enabled Keycloak health and metrics use management port 9000; keep it private and use /health/ready for the orchestrator.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "management-mtls": {"text": "https-management-client-auth accepts none/request/required and inherits HTTP settings; this plaintext topology needs management TLS credentials and trust before client certificates can authenticate it.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "authentik-metrics": {"text": "At version/2026.8.3, the Rust core metrics listener uses plain HTTP with default [::]:9300, and the main Dockerfile ships the Rust binary run by ak; whether published images were built from it is NOT ESTABLISHED. The shipped Compose file does not publish 9300, but the container-network listener still needs restriction.", "components": ["authentik"], "sources": ["authentik:s6ef2a53196aa", "authentik:sbd91cec2c31b", "authentik:se88010d6d96b", "authentik:sbf6b0257ceee", "authentik:sb6abd20b147e", "authentik:s20f8787bddf2", "authentik:sce0e5699f78f", "authentik:sb1c63be23964", "authentik:s99d9d5b23e9a", "authentik:s866a7dcd455a", "authentik:scc468aa2294d"], "status": "REASONED"},
    "authentik-go-metrics": {"text": "At version/2026.8.3, a Go web server metrics listener is also present: cmd/server calls WebServer.Start, which calls runMetricsServer per listen.metrics address. No image or release build of cmd/server was found in the pinned tree; a developer debug launch targets it. The main Dockerfile ships the Rust binary instead; whether published images were built from it is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:safa24c359f2d", "authentik:sddf26c6bdc5c", "authentik:s619cee70c0ba", "authentik:s3b480458ab74", "authentik:sce0e5699f78f", "authentik:sb1c63be23964"], "status": "REASONED"},
    "authentik-metrics-startup": {"text": "At version/2026.8.3, the Rust main starts the metrics server before the per-mode dispatch (healthcheck exits earlier), including proxy mode in proxy-feature builds; Server and AllInOne store the server handle, Worker and AllInOne the worker handles. Whether the published image was built from the tree's Dockerfile is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s318165203c9d", "authentik:sbd91cec2c31b", "authentik:sce0e5699f78f", "authentik:sb1c63be23964", "authentik:s99d9d5b23e9a", "authentik:s866a7dcd455a", "authentik:scc468aa2294d", "authentik:s20f8787bddf2"], "status": "REASONED"},
    "worker-outpost-metrics": {"text": "At version/2026.8.3, worker startup uses the same Rust metrics server as server mode; its handler serves Prometheus metrics on listen.metrics (default [::]:9300) via plain HTTP, with no authentication layer in the router wrapper. The LDAP outpost builds its metrics router with a bare Prometheus handler at /metrics and serves it on each metrics listen address and a Unix socket; section 7 cites pinned proxy, LDAP and RADIUS listener code, but RAC listeners were not traced. Restrict to monitoring clients.", "components": ["authentik"], "sources": ["authentik:s6ef2a53196aa", "authentik:sbd91cec2c31b", "authentik:se88010d6d96b", "authentik:sbf6b0257ceee", "authentik:sf6c661b51ec1", "authentik:sb5dbba465354", "authentik:sb6abd20b147e", "authentik:sca0f5839c601", "authentik:s8fc4619c4d4b"], "status": "REASONED"},
    "keycloak-mfa": {"text": "Enrol administrator TOTP or WebAuthn and require the factor in the realm authentication flow. When Keycloak's default conditional 2FA sub-flow is reached, it asks for OTP if the user has a configured OTP credential; a successful Cookie execution skips the sub-flow, and passwordless WebAuthn authentication can avoid 2FA. Its WebAuthn Authenticator execution is disabled by default. A Required second factor can instead be enrolled during authentication without proving possession of a preexisting factor, so test an administrator with no registered factor and inspect the flow.", "components": ["keycloak", "keycloak-2674"], "sources": ["keycloak:sefec90245fa1", "keycloak-2674:se3124b00898b", "keycloak-2674:sd063782d3773", "keycloak-2674:s363518a7ce4e", "keycloak-2674:sc8bd753b9527", "keycloak-2674:s5f753a0620d2", "keycloak-2674:sfb37d49fcd4b", "keycloak-2674:s68519e76f8c8"], "status": "REASONED"},
    "brute-force-default": {"text": "Keycloak brute-force detection is disabled by default and must be enabled per realm.", "components": ["keycloak"], "sources": ["keycloak:sefec90245fa1"], "status": "REASONED"},
    "redirect-wildcards": {"text": "Keycloak permits trailing redirect-URI wildcards and bare *; deliberately register exact URIs instead.", "components": ["keycloak"], "sources": ["keycloak:sefec90245fa1"], "status": "REASONED"},
    "docker-socket": {"text": "authentik Compose mounts the worker Docker socket for outpost management; use a socket proxy or remove the mount and manage outposts manually.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s20f8787bddf2"], "status": "REASONED"},
    "cache-ports": {"text": "Keycloak cache transport uses 7800 and failure detection 57800; TCP stacks enable TLS by default but still need private reachability.", "components": ["keycloak"], "sources": ["keycloak:s44e24ad4e579"], "status": "REASONED"},
    "redis-history": {"text": "Redis 6379 is relevant to older authentik: tasks moved in 2025.8 and remaining uses in 2025.10, which removes Redis entirely.", "components": ["redis-removal"], "sources": ["redis-removal:seaa0a9896153"], "status": "REASONED"},
    "verify-setup": {"text": "On a disposable instance, complete anonymous root-to-setup flow and confirm akadmin login; after setup or password bootstrap, fresh /setup visits must return to authentication. Source tests were read, not run.", "components": ["authentik"], "sources": ["authentik:sd73827ef7cf2", "authentik:s7ad14bbb32f2", "authentik:s865b0b9b23cc"], "status": "REASONED"},
    "verify-publication": {"text": "Compare exposed and loopback publications: untrusted clients lose setup access while a local browser still reaches it. Neither configuration publishes 9300.", "components": ["authentik"], "sources": ["authentik:s20f8787bddf2", "authentik:sb6abd20b147e"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect all listeners plus Compose publications: host ss misses container namespaces, Compose ps sees one project, and proxy 443 publication is expected.", "components": ["authentik", "keycloak"], "sources": ["authentik:s20f8787bddf2", "authentik:sb6abd20b147e", "keycloak:s44e24ad4e579", "keycloak:s4b5df6f4ef2e"], "status": "REASONED", "verify": [1]},
    "verify-issuer": {"text": "From outside allowed networks, application-realm discovery must print the expected issuer before negative route checks are interpreted; an arbitrary 200 is insufficient.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED", "verify": [1]},
    "verify-console": {"text": "Public /admin/master/console/ must return 404; 2xx, 3xx, 401 and 403 do not show that the console path is closed.", "components": ["keycloak", "nginx"], "sources": ["keycloak:sffc6123bea5c", "nginx:s8d8f3323b468"], "status": "REASONED", "verify": [1]},
    "verify-admin-api": {"text": "Public /admin/realms/master/users must return 404; 401 means the API still answers and requests a token.", "components": ["keycloak", "nginx"], "sources": ["keycloak:se5538391cf9f", "nginx:s8d8f3323b468"], "status": "REASONED", "verify": [1]},
    "verify-master": {"text": "Outside allowed sources, master-realm discovery must return 403; 200 exposes it and 404 indicates blanket denial. Review effective locations beyond these sampled routes.", "components": ["keycloak", "nginx"], "sources": ["keycloak:s2f5f079c5e00", "nginx:sf7458f108aca"], "status": "REASONED", "verify": [1]},
    "verify-admin-login": {"text": "An allowed administrator must complete real login through the private console and frontend master realm; outside sources must fail.", "components": ["keycloak"], "sources": ["keycloak:se5538391cf9f", "keycloak:sffc6123bea5c"], "status": "REASONED", "verify": [1]},
    "verify-direct-ports": {"text": "Probe 8080/8443/9000/9300/9443 directly: curl exit 0 reports a completed operation, 7 reports a connection failure, and 28 is an inconclusive timeout requiring full diagnostics to distinguish accepted-then-stalled from unreachable. Treat a connection failure as the desired isolation outcome only after checking the diagnostic and target; this guide infers that exits 52 and 56 follow an accepted connection, so a listener is reachable. Other exits require diagnostic review. The connection and full-transfer deadlines differ. The checks remain REASONED expectations, not observed outcomes.", "components": ["keycloak", "authentik", "curl", "keycloak-2674"], "sources": ["curl:s9d0c5b92e9a4", "keycloak:s4b5df6f4ef2e", "keycloak:sffc6123bea5c", "authentik:s20f8787bddf2", "authentik:s6ef2a53196aa", "authentik:sb6abd20b147e", "keycloak-2674:s631013c7f55c", "curl:s25c3e6e61c14", "curl:s9c78f229c8ba", "curl:sc7945d33c78d", "curl:s977c1ef288cc", "curl:sc39d43ba6e58", "curl:s9380fc35e98e"], "status": "REASONED", "verify": [1]},
    "verify-bootstrap-removal": {"text": "Look up the bootstrap username with exact=true rather than a default 100-result user list, inspect the returned username, and separately check bootstrap service accounts. Keycloak documents non-exact matching for its -q q=username: filter; this guide keeps the -q order (exact=true first) as defensive advice based on a report, not documented ordering behaviour.", "components": ["keycloak", "keycloak-admin-cli"], "sources": ["keycloak:sbbd55dcb81cd", "keycloak:sefec90245fa1", "keycloak-admin-cli:s5ac2f5372c57"], "status": "REASONED", "verify": [1]},
    "verify-address-coverage": {"text": "Repeat external checks for every public IPv4/IPv6 address and the origin; private admin, database and outposts need separate checks, and the listed ports are not a full inventory.", "components": ["keycloak", "authentik-docs"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c", "authentik-docs:sb44156cde339"], "status": "REASONED", "verify": [1]},
    "authentik-mfa": {"text": "authentik has TOTP and WebAuthn setup stages; enrol a phishing-resistant administrator factor before connecting the first app and require it through an Authenticator Validate stage bound to the authentication flow (this guide's requirement; the cited sources do not state this ordering). A registered device alone does not establish the flow binding. For a user with no allowed device, DENY refuses access. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. The pinned validate-stage and flow-binding sources support these behaviours but do not establish an administrator-specific factor policy.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:seb7e2b93f90d", "authentik:s6562dd778e9e", "authentik:s0af3ecd559b6", "authentik:s4502a88a3ace", "authentik:s0d77ce39834b", "authentik:sd44d285958df", "authentik:s4ebd0cc01832", "authentik:s24e69eaacb04"], "status": "REASONED"},
    "authentik-admin-boundary": {"text": "At version/2026.8.3, /if/admin/, /if/user/ and flows share core routing. This guide assesses that authentik has no equivalent to hostname-admin: the cited configuration, Go startup and Rust server startup show no separate administration listener, not an exhaustive proof of deployed topology. The permission boundary remains unestablished.", "components": ["authentik"], "sources": ["authentik:s348351d7d65e", "authentik:s3e60cde54f52", "authentik:sd02909e948ae", "authentik:sddf26c6bdc5c", "authentik:seb9056af7a7b", "authentik:sce4e17d31a9e"], "status": "REASONED"},
    "authentik-admin-listeners": {"text": "At version/2026.8.3, defaults are HTTP [::]:9000, HTTPS [::]:9443 and metrics [::]:9300; Go startup adds these configured listeners and a Unix socket, and its plain HTTP, HTTPS and Unix listeners share the application proxy router after outpost handling. These files show shared routing, not a separate admin port, and do not prove which listeners a deployed build starts.", "components": ["authentik"], "sources": ["authentik:sb6abd20b147e", "authentik:sd02909e948ae", "authentik:sddf26c6bdc5c", "authentik:s9c8058b95d3c", "authentik:s427c0d034db0", "authentik:sa2fe855c9416"], "status": "REASONED"},
    "authentik-admin-interface": {"text": "At version/2026.8.3, both interface routes redirect authenticated external, service-account and internal-service-account users to a default app or deny them; other requests fall through. These view classes show no administrator-permission check, so this guide does not treat loading the admin template as proof of authorization.", "components": ["authentik"], "sources": ["authentik:s3e60cde54f52", "authentik:sda44b474a18b"], "status": "REASONED"},
    "authentik-admin-api-mount": {"text": "At version/2026.8.3, API v3 registers application API routes, including core users, groups, tokens and admin authenticators. The root URL configuration mounts each app under the web path; the API app mounts api/ and then v3/, so the v3 router is at <web path>api/v3/, /api/v3/ by default, matching the Go client's api/v3 prefix. Endpoint permission wiring is not established by these files.", "components": ["authentik"], "sources": ["authentik:s3e60cde54f52", "authentik:se0352eb4cba5", "authentik:sddf26c6bdc5c", "authentik:s5a70f3599721", "authentik:s61c7672e8c51", "authentik:sbe6392bdb300", "authentik:s3e274c13f369", "authentik:sce23f2109660"], "status": "REASONED"},
    "authentik-admin-api-auth": {"text": "At version/2026.8.3, TokenAuthentication recognizes API-intent tokens, API-scoped OAuth tokens, the managed-outpost secret and IPC key; it rejects inactive users and unrecognized credentials, but absent or unsupported authentication can return no user. This does not establish session authentication or every endpoint adopting this class.", "components": ["authentik"], "sources": ["authentik:sc39e062f1417"], "status": "REASONED"},
    "authentik-admin-rbac": {"text": "At version/2026.8.3, ObjectPermissions' request check passes object-lookup requests (its comment leaves view checks to ObjectFilter, writes to the object check) and permits configured creation without add permission; the object check accepts global permissions or configured ownership before delegating. HasPermission checks user.has_perms; endpoint wiring and permission boundary stay unestablished.", "components": ["authentik"], "sources": ["authentik:sccd0d60249a7"], "status": "REASONED"},
    "authentik-admin-proxy": {"text": "Build any network boundary around authentik administration at the proxy using path restrictions; identify and test required paths for the deployed version and maintain the list. This guide assesses that the UI is not designed around this separation and path-based separation is difficult to maintain; this is not a vendor-supported recipe, and the cited files give no complete path list.", "components": ["authentik"], "sources": ["authentik:s348351d7d65e", "authentik:s3e60cde54f52", "authentik:se0352eb4cba5", "authentik:sddf26c6bdc5c"], "status": "REASONED"},
    "authentik-admin-paths": {"text": "At version/2026.8.3, core URLs show /if/admin/, /if/user/, flows, HTTP admin-template fallbacks at /ws/outpost/<uuid:pk>/ and /ws/client/, and a /ws/client/ websocket route wrapped in authentication middleware. With the API client prefix, these are paths to investigate, not a complete restriction list or proof of websocket authorization.", "components": ["authentik"], "sources": ["authentik:s3e60cde54f52", "authentik:sddf26c6bdc5c"], "status": "REASONED"},
    "authentik-rust-listeners": {"text": "At version/2026.8.3, the main Dockerfile ships the Rust binary run by ak. Server mode runs gunicorn on a Unix socket and serves one router over HTTP on listen.http, rustls on listen.https and a Unix socket, sending embedded-outpost apps to the outpost and the rest via the core router to gunicorn. Worker mode serves health checks on listen.http. Deployed topology beyond Compose is NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:sce0e5699f78f", "authentik:sb1c63be23964", "authentik:s99d9d5b23e9a", "authentik:s866a7dcd455a", "authentik:scc468aa2294d", "authentik:s20f8787bddf2", "authentik:s4cf169f29540", "authentik:sce4e17d31a9e", "authentik:s60d269cdd686", "authentik:s9b5f3bca8761", "authentik:sa28f81f21b1d", "authentik:s15c00e95792d", "authentik:s70fd69dc00dc", "authentik:sb6abd20b147e"], "status": "REASONED"},
    "authentik-api-defaults": {"text": "At version/2026.8.3, REST framework defaults are TokenAuthentication then SessionAuthentication, ObjectPermissions and an ObjectFilter backend; app and user settings modules can update them, and no app settings module was found doing so. Users and groups add AgentAuth; the flow executor uses AllowAny. SessionAuthentication's implementation and deployment overrides are NOT ESTABLISHED.", "components": ["authentik"], "sources": ["authentik:s8e634e5a47bd", "authentik:s5635e9e0c9be", "authentik:sb99c372bb642", "authentik:sa76f25db4854", "authentik:sfc21d0891247"], "status": "REASONED"},
    "authentik-admin-websockets": {"text": "At version/2026.8.3, websocket routes under the web path (/ws/... by default) are /ws/client/, /ws/outpost/<uuid:pk>/, /ws/rac/<str:token>/ and /ws/outpost_rac/<str:channel>/. /ws/client/ resolves a session or anonymous user and accepts every connection; the RAC client consumer on /ws/rac/ accepts, then denies the connection when its token is not bound to the session.", "components": ["authentik"], "sources": ["authentik:s66c517125520", "authentik:se23cfb7021b4", "authentik:sce23f2109660", "authentik:s3e60cde54f52", "authentik:s4e91718909bd", "authentik:s455913b95a83", "authentik:s5f0e15341809", "authentik:sde79042b101e", "authentik:s2ea54ff41b58"], "status": "REASONED"},
    "authentik-outpost-websockets": {"text": "At version/2026.8.3, under the configured web path (shown with the default /), the /ws/outpost/ and /ws/outpost_rac/ websocket routes deny a connection without a bearer token that TokenAuthentication accepts; /ws/outpost/ also requires outpost view permission, while the RAC outpost consumer accepts with no outpost-specific check on /ws/outpost_rac/.", "components": ["authentik"], "sources": ["authentik:s66c517125520", "authentik:s2ea54ff41b58", "authentik:sd50a3c0e1d5a", "authentik:sd7bc33be13a7", "authentik:s5f0e15341809", "authentik:s1392b147416c", "authentik:sce23f2109660"], "status": "REASONED"},
    "authentik-admin-api-shared": {"text": "At version/2026.8.3, the flow executor is registered under the API router at flows/executor/<slug:flow_slug>/ with AllowAny, the API schema names that path's GET flows_executor_get, and the flow interface calls flowsExecutorGet, taken here as that operation's generated client method, so this guide infers that refusing the whole API prefix would break login.", "components": ["authentik"], "sources": ["authentik:s805bd431630c", "authentik:sfc21d0891247", "authentik:sb7089c82fae9", "authentik:s3b6031f49229", "authentik:s5a70f3599721", "authentik:se0352eb4cba5"], "status": "REASONED"},
    "authentik-admin-static-paths": {"text": "At version/2026.8.3, the Rust static router also serves /if/admin/assets/ under the configured web path (shown with the default /) alongside the user, flow and RAC interface assets. Path lists from the routing tables this guide read are bounded by those tables; complete path coverage remains open.", "components": ["authentik"], "sources": ["authentik:se6949824fb7c", "authentik:s9b5f3bca8761", "authentik:sce4e17d31a9e", "authentik:s5a70f3599721", "authentik:se0352eb4cba5", "authentik:s66c517125520", "authentik:s3e60cde54f52", "authentik:s805bd431630c", "authentik:sce23f2109660"], "status": "REASONED"},
    "verify-mfa-password": {"text": "For both providers, open a fresh session with only the administrator password and confirm access is refused after factor enforcement. This guide assesses that an already-enrolled administrator's password-only refusal does not distinguish enrolment from enforcement; test a user with no registered factor and inspect the flow or stage settings. Keycloak's default conditional 2FA, when reached (a successful Cookie execution skips it), prompts for configured OTP unless passwordless WebAuthn already authenticated the user; the default flow's WebAuthn Authenticator execution is disabled by default; and a Required factor the user lacks can be enrolled during authentication. At authentik version/2026.8.3, the unconfigured-device action defaults to SKIP; DENY refuses a user with no allowed device. CONFIGURE errors and refuses when no configuration stage is set, inserts one stage when exactly one is set, or offers a choice when several are set; with a configuration stage set, only DENY refuses that user. Bind the validation stage to the authentication flow.", "components": ["keycloak", "authentik-docs", "authentik", "keycloak-2674"], "sources": ["keycloak:sefec90245fa1", "authentik-docs:sb44156cde339", "authentik:s6b4af3243161", "authentik:s4ce54a5b84c8", "keycloak-2674:se3124b00898b", "keycloak-2674:s363518a7ce4e", "authentik:seb7e2b93f90d", "authentik:s6562dd778e9e", "authentik:s0af3ecd559b6", "authentik:s4502a88a3ace", "authentik:s0d77ce39834b", "authentik:sd44d285958df"], "status": "REASONED"},
    "management-auth-default": {"text": "In this plain-HTTP Keycloak topology no HTTP client authentication is configured, so inherited management client authentication is usually none; required needs management TLS credentials and trust first.", "components": ["keycloak"], "sources": ["keycloak:s4b5df6f4ef2e"], "status": "REASONED"},
    "docker-socket-scope": {"text": "Docker's daemon requires root unless rootless (daemon and containers run non-root); only trusted users should control it. For authentik's shipped Compose worker socket, check daemon type and restrict access: this guide assesses ordinary rootful access as host-root-equivalent and rootless blast radius as the daemon user and what it can access; sources do not directly demonstrate either assessment.", "components": ["authentik-docs", "authentik", "docker-engine", "docker-engine-pinned"], "sources": ["authentik-docs:sb44156cde339", "authentik:s20f8787bddf2", "docker-engine:s18f59818e451", "docker-engine:s7e61efb4dd59", "docker-engine-pinned:secebea1a69ab", "docker-engine-pinned:s8eab393a61c6"], "status": "REASONED"},
    "outpost-boundaries": {"text": "At version/2026.8.3, authentik supports Proxy, LDAP, RADIUS and RAC outposts. The embedded Proxy outpost runs in the main server and shares ports 9000 and 9443; managed or manually deployed outposts can run elsewhere. The pinned Go proxy code listens on configured HTTP, HTTPS and metrics addresses. This guide did not trace whether the deployed Proxy outpost image runs the cited Go proxy code at this tag. The Docker controller maps the outpost's ports to the host unless docker_map_ports is false; it defaults to true. The Kubernetes controller reconciles Deployment and Service objects. LDAP and RADIUS listener code is also pinned, but RAC listeners were not traced. This guide requires separate exposure checks for each deployed outpost and assesses that its Verify probes do not demonstrate them; the embedded outpost shares the core server ports rather than opening another port.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s7ae2d123b0f2", "authentik:s126d3ca5ebeb", "authentik:se716e28f85db", "authentik:s7a25610cceaa", "authentik:sca0f5839c601", "authentik:s8fc4619c4d4b", "authentik:sb6abd20b147e", "authentik:sb5dbba465354", "authentik:s71722cfad526", "authentik:see76fb8454ce", "authentik:sfb87a6898f29"], "status": "REASONED"},
    "verify-proxy-neutralization": {"text": "Run external probes outside every allowed network; unset HTTP/HTTPS/ALL/NO_PROXY variables in both cases and use curl -q --noproxy '*' to bypass proxies and curlrc, which this guide assesses could otherwise make blocked endpoints appear reachable through allowed egress. Curl's HTTP proxy environment variable is lowercase only; -q must be curl's first option.", "components": ["keycloak", "curl"], "sources": ["keycloak:sffc6123bea5c", "curl:sde07f1edf2dc", "curl:s75e3807878ff", "curl:s508454c45cf1", "curl:s2278b86c08a6", "curl:sc8658f8a2e89"], "status": "REASONED", "verify": [1]},
    "verify-authentik-routes": {"text": "The fenced paths are Keycloak-specific; the exclusion of Keycloak paths from authentik is this guide's inference from the fetched route files, not an exhaustive route proof. For authentik, use a deployed application's actual OAuth2 discovery URL as the positive control and confirm its configured issuer; an untrusted client must not reach the chosen administration route while an allowed administrator can. Check the administration API surface you choose to restrict separately: an untrusted client must be refused while an authorized administrator on the allowed network can complete an API request. Do not refuse the whole API prefix without tracing login dependencies; confirm that an ordinary user can still complete login. At version/2026.8.3 the OAuth2 URL module defines the per-application discovery suffix and the issuer can be global or per-provider; /if/admin/ is a core route. The fetched root module mounts application URLs dynamically, so these files do not establish the full /application/o/ prefix or /api/v3/ route. These files do not establish whether end-user flow execution uses the API prefix. A responding status alone is not the positive-control pass condition.", "components": ["authentik-docs", "authentik"], "sources": ["authentik-docs:sb44156cde339", "authentik:s348351d7d65e", "authentik:s9f8f5dfeca92", "authentik:s2b2c994a59e6", "authentik:s91525f4e30dc", "authentik:s5a70f3599721"], "status": "REASONED", "verify": [1]},
    "admin-factor-order": {"text": "Enrol a phishing-resistant factor on the administrator account of either provider before connecting the first application and enforce it in the flow (this guide's requirement; the cited sources do not state this ordering). Keycloak documents Required executions; authentik version/2026.8.3 binds ordered stages to flows, but the cited files do not establish an administrator-specific factor policy.", "components": ["keycloak", "authentik-docs", "keycloak-2674", "authentik"], "status": "REASONED", "sources": ["keycloak:sefec90245fa1", "authentik-docs:sb44156cde339", "keycloak-2674:se3124b00898b", "authentik:s4502a88a3ace", "authentik:s0d77ce39834b", "authentik:seb7e2b93f90d", "authentik:s6562dd778e9e"]},
    "keycloak-http-opt-in": {"text": "In the production example, backend plain HTTP on default port 8080 exists only when explicitly enabled with --http-enabled=true; confine that hop to loopback or a controlled private segment. At 26.7.4, the HTTP listener option defaults false but is enabled by default in development mode, and HTTPS defaults to port 8443. In production, http-host defaults to 0.0.0.0, so constrain the bind or network reachability.", "components": ["keycloak", "keycloak-2674"], "sources": ["keycloak:s2f5f079c5e00", "keycloak:sffc6123bea5c", "keycloak-2674:s07c5f54d49d7", "keycloak-2674:s631013c7f55c", "keycloak-2674:s13a81516d2b4", "keycloak-2674:sf10fbdd955bd"], "status": "REASONED"},
    "idp-maintenance": {"text": "This guide requires patching, tested backups and keeping a self-hosted identity provider available (this guide's requirement; the cited files do not prescribe a cadence). This guide assesses that a compromised or unavailable self-hosted identity provider takes its dependent services with it. At the time of writing, authentik's version/2026.8.3 security policy lists 2026.5.x and 2026.8.x as supported; Keycloak 26.7.4's security policy says that, depending on severity, vulnerabilities may be fixed in the current major.minor release, or lower-severity vulnerabilities or hardening in the following major.minor release; it encourages those unable to upgrade regularly to consider the Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak cautions that realm export alone has backup limitations: consistency is not guaranteed unless all nodes are stopped before the export, and user and admin events, persisted sessions, workflow state and revoked tokens are omitted. These sources do not establish a complete backup procedure for either provider, an authentik upgrade procedure, a universal maintenance cadence or a tested restore.", "components": ["keycloak", "authentik-docs", "authentik", "keycloak-2674"], "sources": ["keycloak:s2f5f079c5e00", "authentik-docs:sb44156cde339", "authentik:s926fad656b61", "keycloak-2674:s694bac50be88", "keycloak-2674:s85c8eccedd6a"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
