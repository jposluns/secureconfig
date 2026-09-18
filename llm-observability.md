# LLM tracing and observability: Langfuse, Phoenix, Helicone, OpenTelemetry Collector

These tools store full prompts, completions, and often the provider API keys used to generate them, so an
exposed dashboard leaks your most sensitive data at once. Several ship with authentication off or with open
signup enabled, so the default install is not safe to expose.

## Langfuse (self-hosted)

Email/password authentication is enabled by default: anyone who can reach the URL can register their own
account unless you turn signup off. Set `AUTH_DISABLE_SIGNUP=true` to block new registrations, including a
user accepting a project invite without an existing account; set `AUTH_DISABLE_USERNAME_PASSWORD=true` to
require SSO instead of a password entirely. Create the first account BEFORE you disable signup (or provision
it headlessly with `LANGFUSE_INIT_ORG_ID`, `LANGFUSE_INIT_USER_EMAIL`, and `LANGFUSE_INIT_USER_PASSWORD` -
a user or project cannot be initialized without also initializing an organization), or you lock yourself
out; then confirm a fresh registration is actually refused. SSO runs through Auth.js against Google, GitHub, GitLab, Azure
AD/Entra ID, Okta, Auth0, Keycloak, or a custom OIDC provider; `NEXTAUTH_URL` must be set correctly for any
method other than email/password. `AUTH_SESSION_MAX_AGE` sets the session lifetime in minutes, and must be an integer greater than five. The current implementation defaults it to 20160 (14 days); the documentation still says 43200 (30 days), so pin your release and check the value you actually get. The ingestion and public API are authenticated
separately from the UI session: a project's public key (username) and secret key (password) are sent as HTTP
Basic Auth, issued from Project Settings, and unrelated to a user's login credentials. Put MFA at the
identity provider per [mfa.md](mfa.md); Langfuse's own login has none.

Those controls all sit on the sign-in flow, and the self-hosting `docker-compose.yml` sits under them: it
ships example secrets marked `# CHANGEME`, and `NEXTAUTH_SECRET` protects the session token, which NextAuth
encrypts and authenticates, so the shipped `mysecret` lets anyone mint a session for any existing account,
administrators included, without the login flow and the SSO or MFA that only guard it. Disabling signup and
enforcing SSO do not help, because they gate account creation and sign-in, not a forged cookie. Two related
secrets ship the same way: `SALT` (`mysalt`) salts the stored API-key hashes, so a known salt speeds offline
cracking of keys lifted from the database; and `ENCRYPTION_KEY`, shipped as 64 hex zeros, encrypts the LLM
provider keys and integration credentials Langfuse stores, so anyone holding that key and a copy of the data
reads them in clear. Generate a fresh random value for each before the first start (`openssl rand -base64 32`
for `NEXTAUTH_SECRET` and `SALT`, `openssl rand -hex 32` for `ENCRYPTION_KEY`) and keep them out of the
repository ([secrets.md](secrets.md)); changing `ENCRYPTION_KEY` later needs a planned re-encryption, and if
the shipped key was ever live, treat the stored provider credentials as exposed and rotate them. The same
compose bundles a MinIO with the well-known `minio`/`miniosecret` login and publishes its S3 API on host port
`9090` on every interface by default, as it does langfuse-web on `3000`, while the bundled Postgres,
ClickHouse, and Redis default to loopback; change that login, update the matching `LANGFUSE_S3_*` access keys
Langfuse uses to reach MinIO, and keep every published port off untrusted networks ([minio.md](minio.md),
[object-storage.md](object-storage.md)).

## Arize Phoenix (self-hosted)

Authentication is disabled by default, "as you may be just trying Phoenix for the very first time or have
Phoenix deployed in a VPC" in the vendor's own words: anyone who reaches the UI has full read and write
access with no login at all. Set `PHOENIX_ENABLE_AUTH=True` and `PHOENIX_SECRET` (a long random value used to
sign session tokens) to turn it on.

Turning auth on is not enough. Phoenix creates an administrator account `admin@localhost` with the password
`admin`, so the flip alone leaves a reachable instance with a known admin login. `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`
sets that password, but only on the startup that first creates the account: set it on a brand-new deployment,
before the first start. On any instance that has started before, the variable is inert, and setting it and
restarting changes nothing and reports no error, so never read "I set it and restarted" as proof the password
changed. It is read only on the first startup that creates the admin account; unless you are setting it on a
brand-new deployment's very first start, treat the account as already existing: log in at the UI as
`admin@localhost`, which prompts for a new password, then run the
default-credential check in Verify to prove `admin` is dead. Until that change lands, `admin`/`admin` is a live
admin login, so keep the instance off any untrusted network in the window between the flip and the change.
Once the account exists the variable only holds an admin password in plaintext for no effect; remove it from
your environment files.

Phoenix binds broadly by default: the HTTP UI/REST/OTLP server on `0.0.0.0:6006` and a SEPARATE gRPC OTLP
server on `[::]:4317` that does not follow the HTTP host setting, and the vendor Compose also publishes its
PostgreSQL, so bind or publish both protocols deliberately and keep the database off host interfaces.

Enabling auth on a running instance stops trace collection and blocks all API access until API keys exist, so
mint a key immediately after the flip: a system key (admin-created, acts for the whole instance) or a user key
authenticates API requests via `PHOENIX_API_KEY` sent as an `Authorization: Bearer` header, and collectors and
SDKs need one to keep sending traces. Phoenix has no native MFA, but it can federate to an OAuth2/OIDC identity
provider (its documentation works through Google, AWS Cognito, and Microsoft Entra ID); enforce MFA there, or
add an identity-aware proxy in front per [mfa.md](mfa.md). Two OAuth caveats: `PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP`
defaults to `True`, so any identity the provider will authenticate can provision itself an account unless you
set it `False` and restrict provider membership (test an unapproved identity); and local email/password login
stays available alongside SSO and bypasses the provider's MFA, so set `PHOENIX_DISABLE_BASIC_AUTH=True` once
the IdP is the intended path.

## Helicone (self-hosted)

Helicone self-hosts with Better Auth: account signup and organization membership, not a fixed shared login
(the `test@helicone.ai` / `password` credential is the manual guide's local trial only). Generate a real
`BETTER_AUTH_SECRET` before the first start, because its documented default is `change-me-in-production`,
which lets anyone forge a session; then restrict who may sign up, and do not expose the dashboard without
your own layer in front. Helicone is several services, not one: its Docker Compose publishes the backing
stores - PostgreSQL, ClickHouse, MinIO/S3, Redis, and MailHog - on host ports independent of the dashboard
login (for example `54388:5432` and `18123:8123`), so an identity proxy on the UI leaves those wide open;
remove or loopback-scope every backing publication and rotate the example storage credentials
([minio.md](minio.md), [object-storage.md](object-storage.md)). Ingestion runs through the separate AI Gateway
and the provider keys in its environment, not the web session; store those per [secrets.md](secrets.md). The
Jawn service and the S3 store also hold your data, so protect every service, not just the dashboard and
gateway: keep them all on a private network or behind an identity-aware fronting layer
([fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md), [caddy.md](caddy.md)) with MFA ([mfa.md](mfa.md)).

## OpenTelemetry Collector

The Collector is the pipe these tools (and others) receive traces through, and it ships with no security
applied until you configure it. The project's own hardening guidance: bind receivers to a specific interface
or `localhost` (for example `127.0.0.1:4317`). The default host for Collector component servers became `localhost` in v0.104.0 (earlier versions bound all
interfaces); the `component.UseLocalHostAsDefaultHost` feature gate that governed that transition was
stabilized and then REMOVED in v0.112.0, so on current versions the localhost default is simply in effect. A
distribution's own configuration can still override a component's default. Set the endpoint explicitly on any version
rather than trusting the default, and widen it only where a proxy or
mesh in front needs the wider bind; require TLS on every receiver and exporter; and attach an authenticator
extension, such as `basicauth` (htpasswd-style credentials, or a static `client_auth` username/password for
outgoing calls) or `bearertokenauth` (a static or file-backed token sent as an `Authorization` header), to any
receiver that accepts data from outside the host. Declaring an authenticator extension is not enough to enforce it: list it under `service.extensions` so it
starts, then attach it to EACH receiver protocol with an `auth.authenticator` key naming the extension.
Inventory the other listeners too - the internal Prometheus metrics endpoint (`127.0.0.1:8888` by default)
and any enabled diagnostic extensions (zPages `55679`, pprof `1777`, health-check `13133`) are also surface.
Build or run only the receivers, processors, and exporters you use, since every enabled component is attack
surface, and run the process as a non-root user.

Neither Langfuse nor Phoenix terminates TLS itself, so an `https://` URL in front of them is your proxy's,
not theirs: put TLS at a reverse proxy or tunnel ([nginx.md](nginx.md), [caddy.md](caddy.md)) and make sure
the plaintext backend port it forwards to is not separately reachable.

## Verify

```bash
# These checks are REASONED, not demonstrated here (no deployment in the authoring environment; backlog
# row 1.45 tracks running them live, in both the exposed and fixed states).
# ss is a listener inventory in THIS namespace - not a firewall, NAT, or authentication check.
ss -tlnp   # expect 3000/6006/4317/4318 bound to loopback or a private address, never 0.0.0.0; but a port
           # here can still be published by DNAT and a wildcard bind can be safe when unpublished, so
           # confirm the actual container publications and firewall, and probe the public IPv4/IPv6 path
           # from another host - this list alone proves neither exposure nor authentication
# Langfuse dashboard: a bare GET of / cannot tell a login page from an exposed project view (both are 200
# and the body is discarded), so confirm it in a FRESH browser session - an unauthenticated visit must
# land on login, not a project. The curl below is only transport reachability.
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
  -o /dev/null -w 'dashboard final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' https://langfuse.example.com/
# Langfuse public API auth, matched pair: WITHOUT the key expect 401 from Langfuse; WITH a valid project
# key (public:secret) expect 200 returning the project list - the positive control proving Langfuse, not a
# fronting proxy, answered (an outer-proxy 401 says nothing about Langfuse). The key enters argv/history
# via -u, so use a short-lived project key and clear the line.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'projects no-key=%{http_code} exit=%{exitcode}\n' https://langfuse.example.com/api/public/projects
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'projects with-key=%{http_code} exit=%{exitcode}\n' -u REPLACE_WITH_PUBLIC_KEY:REPLACE_WITH_SECRET_KEY https://langfuse.example.com/api/public/projects
# Collector OTLP/HTTP, matched pair: WITHOUT the configured auth header expect 401/403; then repeat WITH it
# (add -H 'Authorization: Bearer <token>', or -u user:pass for basicauth) and expect a 2xx - the positive
# control. Keep the JSON content type (a wrong content type draws a 415 that is not an authentication
# result). This tests OTLP/HTTP only; the gRPC receiver on 4317 is separate (below).
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'otlp no-auth=%{http_code} exit=%{exitcode}\n' -H 'Content-Type: application/json' -d '{"resourceSpans":[]}' \
  https://otel-collector.internal:4318/v1/traces
```

For Phoenix specifically, prove the default admin credential is dead and that the read API does not answer an
anonymous request. **These checks are reasoned, not demonstrated** (no Phoenix instance in the authoring
environment; backlog row 1.45 tracks running them against a live instance in both states). The credential
check is manual, because the vendor documents only the UI login flow and a scripted guess against the wrong
endpoint can read a `404` as a rejection: in a fresh browser session with no saved Phoenix cookies, try once
to log in as `admin@localhost` with the password `admin`. **Exposed:** it logs in. **Fixed:** it is rejected,
and your replacement admin password works in a second fresh session. Then, from a network position that
legitimately reaches Phoenix (a connection failure proves nothing about authentication), probe the read API
anonymously (the probe prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer):

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PHOENIX_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing"; exit 1 ;;
    *) curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w '\n[unauth-read] http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         "https://$1/v1/projects" ;;
  esac
)
```

**Exposed:** `/v1/projects` returns project data with no credential (a `2xx`). **Fixed:** the anonymous request
is rejected with `401` or `403`. Anything else (a `404`, a redirect to a login page, a `415`, or a transport
error) is inconclusive and does not prove authentication is on; fall back to the credential check above and to
the listener inventory. Substitute a bracketed literal for an IPv6 host in the URL, for example `[::1]:6006`.

The OTLP/HTTP ingestion path CAN be probed without hand-encoding a span: an empty `ExportTraceServiceRequest`
is a zero-length protobuf body, so send `--data-binary ''` with `Content-Type: application/x-protobuf` to
`/v1/traces` on the HTTP port (6006) and read the status - anonymously it must be rejected (401/403), and
with a valid `Authorization: Bearer` key it is admitted (a 2xx). This tests request ADMISSION, not span
persistence. The gRPC OTLP receiver on 4317 is a SEPARATE server with its own `ApiKeyInterceptor`, not the
HTTP `/v1` router, so a protected HTTP path does not prove the gRPC path is protected: test 4317 separately
(an OTLP gRPC client with and without the key) or keep it bound to loopback or a private address and behind
the authenticated ingress. Confirm the `ss` table shows both OTLP ports (HTTP 6006 and gRPC 4317) bound
loopback or private.

A dashboard that renders traces, prompts, or provider keys without a login is a finding; so is an OTLP port
that accepts spans with no credential at all.

## Common mistakes

- Leaving Phoenix's or Helicone's auth off "because it's just internal" on a host with a public IP.
- Enabling `PHOENIX_ENABLE_AUTH` without creating an API key first, which locks out collectors mid-flight.
- Leaving Phoenix's default `admin@localhost` / `admin` in place after turning auth on, or trusting `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` to have changed it on an instance whose admin account already existed, where the variable is silently inert.
- Publishing the OTLP gRPC/HTTP ports (4317/4318) to `0.0.0.0` because a docker-compose example did.
- Assuming an ingestion key protects the UI, or a UI login protects the ingestion endpoint; they are
  separate credentials in Langfuse and Phoenix alike.

## Sources (checked September 2026)

- Langfuse, authentication and SSO (signup default, `AUTH_DISABLE_SIGNUP`, `AUTH_DISABLE_USERNAME_PASSWORD`,
  SSO providers, `AUTH_SESSION_MAX_AGE`, `NEXTAUTH_URL`): https://langfuse.com/self-hosting/security/authentication-and-sso
- Langfuse, public API authentication (Basic Auth with project public/secret key): https://langfuse.com/docs/api-and-data-platform/features/public-api
- Langfuse, self-hosting configuration (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY` and their generation, the bundled MinIO/Postgres/ClickHouse/Redis; checked 2026-09-14): https://langfuse.com/self-hosting/configuration
- Langfuse, self-hosting docker-compose.yml (the `# CHANGEME` example secrets `mysecret`/`mysalt`/all-zero `ENCRYPTION_KEY`, MinIO `minio`/`miniosecret` on host `9090`, langfuse-web on `3000`; checked 2026-09-14): https://github.com/langfuse/langfuse/blob/main/docker-compose.yml
- Arize Phoenix, authentication (`PHOENIX_ENABLE_AUTH`, `PHOENIX_SECRET`, system and user API keys, `PHOENIX_API_KEY`, the default `admin@localhost` / `admin` account, `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` read only at first-account creation, `/v1/` REST permissions, OAuth2/OIDC identity providers, and the absence of native MFA; read 2026-09-13): https://arize.com/docs/phoenix/self-hosting/features/authentication
- Helicone, self-hosted deployment (default `test@helicone.ai` / `password` login): https://docs.helicone.ai/getting-started/self-host/manual
- Helicone, Docker self-host (Better Auth, `BETTER_AUTH_SECRET` default `change-me-in-production`, published backing stores): https://docs.helicone.ai/getting-started/self-host/docker
- Langfuse, headless initialization (`LANGFUSE_INIT_ORG_ID`/`USER_EMAIL`/`USER_PASSWORD`, org-before-user ordering): https://langfuse.com/self-hosting/administration/headless-initialization
- Arize Phoenix, OAuth2 sign-up and basic-auth controls (`PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP` default True, `PHOENIX_DISABLE_BASIC_AUTH`): https://arize.com/docs/phoenix/self-hosting/features/authentication
- OpenTelemetry Collector, localhost-default history (v0.104.0 default, v0.112.0 gate removal): https://opentelemetry.io/blog/2024/hardening-the-collector-one/
- OpenTelemetry, Collector security best practices (bind addresses, TLS, authenticator extensions, minimal
  components, non-root): https://opentelemetry.io/docs/security/config-best-practices/
- OpenTelemetry Collector Contrib, `basicauthextension` (htpasswd, `client_auth`, `auth.authenticator` wiring): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/basicauthextension
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
