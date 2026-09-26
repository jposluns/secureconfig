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
server on `[::]:4317` that does not follow the HTTP host setting (both as of Phoenix 20.16.0), and the vendor Compose also publishes its
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
the IdP is the intended path. Establish and test an approved IdP administrator BEFORE you disable local login
or provider signup: disabling basic auth also disables the local admin password, so once
`PHOENIX_DISABLE_BASIC_AUTH=True` the "replacement admin password works" control in Verify no longer applies -
instead require local password login to FAIL and an approved IdP login with MFA to succeed.

## Helicone (self-hosted)

Helicone self-hosts with Better Auth: account signup and organization membership, not a fixed shared login
(the `test@helicone.ai` / `password` credential is the manual guide's local trial only). Generate a real
`BETTER_AUTH_SECRET` before the first start: the all-in-one image documents the placeholder
`change-me-in-production` and the repository Compose file falls back to `your-secret-key`, and a known
signing secret weakens every session token it protects, so replace whichever example value your deployment
uses. Then restrict who may sign up, and do not expose the dashboard without
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

Langfuse's container deployment does not terminate TLS, so an `https://` URL in front of it is your proxy's,
not Langfuse's. Phoenix (8.29 and later) CAN terminate TLS natively for both HTTP and gRPC - set
`PHOENIX_TLS_ENABLED=True` (it defaults to `False`) with `PHOENIX_TLS_CERT_FILE` and `PHOENIX_TLS_KEY_FILE` -
so its default is TLS off, not TLS unsupported. Later versions add per-protocol overrides
(`PHOENIX_TLS_ENABLED_FOR_HTTP` and `PHOENIX_TLS_ENABLED_FOR_GRPC`, each overriding `PHOENIX_TLS_ENABLED` for
its protocol); check your release. Either way terminate TLS deliberately (natively, or at a reverse proxy or tunnel
per [nginx.md](nginx.md), [caddy.md](caddy.md)), and make sure any plaintext backend port a proxy forwards
to is not separately reachable.

## Verify

```bash
# These checks are REASONED, not demonstrated here: the authoring environment has no running Langfuse,
# Phoenix, Helicone, or OpenTelemetry Collector deployment to probe, so the shell syntax and the guard
# branches were tested locally but the exposed-vs-fixed service responses were not. Backlog row 1.45 tracks
# running them live against each service in both states.
# ss is a listener inventory in THIS namespace - not a firewall, NAT, or authentication check.
ss -tlnp   # inventory 3000/6006/4317/4318 and identify each listener's namespace, host publication, and
           # permitted network paths. A wildcard bind is not itself exposure (Phoenix's gRPC 4317 always
           # binds [::] regardless of PHOENIX_HOST) and a port here can still be published by DNAT, so
           # confirm the actual container publications and firewall, and probe the public IPv4/IPv6 path
           # from another host - this list alone proves neither exposure nor authentication
# Langfuse dashboard: a bare GET of / cannot tell a login page from an exposed project view (both are 200
# and the body is discarded), so confirm it in a FRESH browser session - an unauthenticated visit must
# land on login, not a project. The curl below is only transport reachability.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
  -o /dev/null -w 'dashboard final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' https://langfuse.example.com/
# Langfuse public API auth, matched pair: WITHOUT the key expect 401; WITH a valid project key (public:secret)
# expect 200 whose JSON body carries the EXPECTED project id - the positive control. A 401/200 pair seen
# THROUGH a reverse proxy does not prove Langfuse itself authenticated (a proxy can reject anonymous and
# admit authenticated while its backend stays open), so repeat the pair DIRECTLY against the Langfuse
# listener from an authorized network position, keeping any proxy credentials constant, and separately
# confirm untrusted clients cannot reach that backend. The key reaches curl on stdin via a config file (curl --config -), so it stays out
# of argv and /proc/<pid>/cmdline; still prefer a short-lived project key.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_KEY' 'REPLACE_WITH_SECRET_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the public key on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the secret key on the set -- line above; not probing"; exit ;; esac
  set -- "${1//\\/\\\\}" "${2//\\/\\\\}"
  set -- "${1//\"/\\\"}" "${2//\"/\\\"}"
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
    -w 'projects no-key=%{http_code} exit=%{exitcode}\n' https://langfuse.example.com/api/public/projects
  printf 'user = "%s:%s"\n' "$1" "$2" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 \
    -w '\nprojects with-key=%{http_code} exit=%{exitcode}\n' --config - https://langfuse.example.com/api/public/projects
)
# Collector OTLP/HTTP, matched pair: WITHOUT the configured auth header expect 401/403; then repeat WITH it
# (add -H 'Authorization: Bearer <token>', or -u user:pass for basicauth) and expect a 2xx - the positive
# control. Run the pair DIRECTLY against the receiver to establish RECEIVER authentication (a proxy can
# answer 401/2xx while the receiver is open), and test the public ingress separately. Keep the JSON content
# type (a wrong content type draws a 415 that is not an authentication result). This tests this OTLP/HTTP
# receiver only; test each enabled OTLP/gRPC receiver separately, and note the Phoenix check further below
# targets a DIFFERENT server, not this Collector.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
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
and your replacement admin password works in a second fresh session (or, if you set
`PHOENIX_DISABLE_BASIC_AUTH=True`, local password login is refused entirely and an approved IdP login with
MFA succeeds instead). Then, from a network position that
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
    *) curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 "https://$1/v1/projects" \
         -w '\n[unauth-read] http=%{http_code} exit=%{exitcode} err=%{errormsg}\n'
       ;;
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
with a WRITE-authorized `Authorization: Bearer` key (a system key, or a user key allowed to write traces,
NOT a viewer key) it is admitted (a 2xx). This tests request ADMISSION, not span
persistence, and a valid VIEWER-role key is not a positive control here: Phoenix authenticates a viewer but
rejects a viewer token for OTLP writes with `PERMISSION_DENIED`, so admit only with a system key or a
write-authorized user key. The gRPC OTLP receiver on 4317 is a SEPARATE server with its own
`ApiKeyInterceptor`, not the HTTP `/v1` router, so a protected HTTP path does not prove the gRPC path is
protected: test 4317 separately by invoking `opentelemetry.proto.collector.trace.v1.TraceService/Export`
with an empty `ExportTraceServiceRequest`, first with no metadata (expect `UNAUTHENTICATED`) then with
`authorization: Bearer <write-authorized key>` (expect `OK`). That needs an OTLP gRPC client carrying the
protobuf descriptor (and the CA if TLS is on), so it ships REASONED (backlog row 1.45): with authentication
disabled the same anonymous empty Export returns `OK` (the exposed outcome), and the authenticated,
viewer-rejected, and empty-request behaviours follow Phoenix's gRPC Export handler and `ApiKeyInterceptor`
(see Sources). Because Phoenix's gRPC listener always binds `[::]` regardless of `PHOENIX_HOST`, you cannot
move it to loopback by host
setting: isolate it in a private container network, restrict or omit its host publication, and inspect its
namespace, publications, and firewall separately from the HTTP port. A wildcard listener inside an isolated
namespace is not by itself public exposure.

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
- Langfuse, session-lifetime implementation (`AUTH_SESSION_MAX_AGE` validated as an integer greater than five, default `14 * 24 * 60` = 20160 minutes, vs the 43200 in the docs): https://github.com/langfuse/langfuse/blob/24c949d8dd5617219a8415f80e4c65ad611ff05c/web/src/env.mjs
- Langfuse, self-hosting configuration (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY` and their generation, the bundled MinIO/Postgres/ClickHouse/Redis; checked 2026-09-14): https://langfuse.com/self-hosting/configuration
- Langfuse, self-hosting docker-compose.yml (the `# CHANGEME` example secrets `mysecret`/`mysalt`/all-zero `ENCRYPTION_KEY`, MinIO `minio`/`miniosecret` on host `9090`, langfuse-web on `3000`; checked 2026-09-14): https://github.com/langfuse/langfuse/blob/0dd0a7fbe2feb300b8776f02b3684eeee3fbceab/docker-compose.yml
- Arize Phoenix, authentication (`PHOENIX_ENABLE_AUTH`, `PHOENIX_SECRET`, system and user API keys, `PHOENIX_API_KEY`, the default `admin@localhost` / `admin` account, `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` read only at first-account creation, `/v1/` REST permissions, OAuth2/OIDC identity providers, and the absence of native MFA; read 2026-09-13): https://arize.com/docs/phoenix/self-hosting/features/authentication
- Arize Phoenix, native HTTP and gRPC TLS introduced in 8.29 (2025-04-28): https://arize.com/docs/phoenix/release-notes/04-2025/04-28-2025-tls-support-for-phoenix-server
- Arize Phoenix, TLS configuration implementation (`PHOENIX_TLS_ENABLED` default `False`, `PHOENIX_TLS_CERT_FILE`/`PHOENIX_TLS_KEY_FILE`, and the per-protocol `PHOENIX_TLS_ENABLED_FOR_HTTP`/`PHOENIX_TLS_ENABLED_FOR_GRPC` overrides): https://github.com/Arize-ai/phoenix/blob/080959576563900038688ddf01f3bee110005df5/src/phoenix/config.py
- Helicone, self-hosted deployment (default `test@helicone.ai` / `password` login): https://docs.helicone.ai/getting-started/self-host/manual
- Helicone, all-in-one Docker deployment (Better Auth, `BETTER_AUTH_SECRET` documented default `change-me-in-production`): https://docs.helicone.ai/getting-started/self-host/docker
- Helicone, repository Compose deployment (`BETTER_AUTH_SECRET` fallback `your-secret-key`; backing stores published on host ports `54388:5432`, `18123:8123`, `19000:9000`, `9000`/`9001`, `6379`, `1025`/`8025`): https://github.com/Helicone/helicone/blob/b12ebaccb824ab9778757ca197ff302d97fda421/docker/docker-compose.yml
- Langfuse, headless initialization (`LANGFUSE_INIT_ORG_ID`/`USER_EMAIL`/`USER_PASSWORD`, org-before-user ordering): https://langfuse.com/self-hosting/administration/headless-initialization
- Arize Phoenix, OAuth2 sign-up and basic-auth controls (`PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP` default True, `PHOENIX_DISABLE_BASIC_AUTH`): https://arize.com/docs/phoenix/self-hosting/features/authentication
- OpenTelemetry Collector, localhost default introduced in v0.104.0: https://opentelemetry.io/blog/2024/hardening-the-collector-one/
- OpenTelemetry Collector, `component.UseLocalHostAsDefaultHost` feature-gate removal in v0.112.0: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.112.0/CHANGELOG.md
- OpenTelemetry, Collector security best practices (bind addresses, TLS, authenticator extensions, minimal
  components, non-root): https://opentelemetry.io/docs/security/config-best-practices/
- OpenTelemetry Collector Contrib, `basicauthextension` (htpasswd, `client_auth`, `auth.authenticator` wiring): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/basicauthextension
- Arize Phoenix, gRPC OTLP Export authorization (`ApiKeyInterceptor`: `UNAUTHENTICATED` without a key, `PERMISSION_DENIED` for a viewer token, `OK` with a write-authorized key or when auth is disabled): https://github.com/Arize-ai/phoenix/blob/f11c885c063f1c9b6146693cda401c5d645d8294/src/phoenix/server/bearer_auth.py
- OpenTelemetry Collector, internal Prometheus metrics at `127.0.0.1:8888`: https://opentelemetry.io/docs/collector/internal-telemetry/
- OpenTelemetry Collector, zPages extension (default endpoint `localhost:55679`): https://github.com/open-telemetry/opentelemetry-collector/blob/71f0462d5460ad3055201fd0f17658e56362d63a/extension/zpagesextension/README.md
- OpenTelemetry Collector Contrib, pprof extension (default endpoint `localhost:1777`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/443567a6a00d7cff8cae1432a6fef655d8698e94/extension/pprofextension/README.md
- OpenTelemetry Collector Contrib, health-check extension (default endpoint `localhost:13133`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/d922ffb299c6b9be026f97dd7d6a5f0f507efdeb/extension/healthcheckextension/README.md
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- Phoenix defaults `HOST = "0.0.0.0"`, `PORT = 6006`, `GRPC_PORT = 4317` (pinned tag arize-phoenix-v20.16.0): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/config.py#L3111-L3117
- Phoenix gRPC OTLP server binds `[::]` regardless of the HTTP host (pinned tag arize-phoenix-v20.16.0): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/server/grpc_server.py#L107-L109
