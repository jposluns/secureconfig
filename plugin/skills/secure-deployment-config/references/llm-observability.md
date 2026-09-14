# LLM tracing and observability: Langfuse, Phoenix, Helicone, OpenTelemetry Collector

These tools store full prompts, completions, and often the provider API keys used to generate them, so an
exposed dashboard leaks your most sensitive data at once. Several ship with authentication off or with open
signup enabled, so the default install is not safe to expose.

## Langfuse (self-hosted)

Email/password authentication is enabled by default: anyone who can reach the URL can register their own
account unless you turn signup off. Set `AUTH_DISABLE_SIGNUP=true` to block new registrations, including a
user accepting a project invite without an existing account; set `AUTH_DISABLE_USERNAME_PASSWORD=true` to
require SSO instead of a password entirely. SSO runs through Auth.js against Google, GitHub, GitLab, Azure
AD/Entra ID, Okta, Auth0, Keycloak, or a custom OIDC provider; `NEXTAUTH_URL` must be set correctly for any
method other than email/password. `AUTH_SESSION_MAX_AGE` sets the session lifetime in minutes (default
43200, thirty days; five minutes is the enforced floor). The ingestion and public API are authenticated
separately from the UI session: a project's public key (username) and secret key (password) are sent as HTTP
Basic Auth, issued from Project Settings, and unrelated to a user's login credentials. Put MFA at the
identity provider per [mfa.md](mfa.md); Langfuse's own login has none.

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

Enabling auth on a running instance stops trace collection and blocks all API access until API keys exist, so
mint a key immediately after the flip: a system key (admin-created, acts for the whole instance) or a user key
authenticates API requests via `PHOENIX_API_KEY` sent as an `Authorization: Bearer` header, and collectors and
SDKs need one to keep sending traces. Phoenix has no native MFA, but it can federate to an OAuth2/OIDC identity
provider (its documentation works through Google, AWS Cognito, and Microsoft Entra ID); enforce MFA there, or
add an identity-aware proxy in front per [mfa.md](mfa.md).

## Helicone (self-hosted)

The manual self-host guide's default login is `test@helicone.ai` / `password`, documented as a local trial
credential; the fetched setup and manual-deployment pages do not cover changing it for production, disabling
signup, or any hardening steps for exposing the dashboard beyond a laptop, so treat that gap as unverified
rather than assuming a safe default exists. Do not expose this UI without your own layer in front. Ingestion
runs through the separate AI Gateway component and provider keys configured in its environment, not through
the web session; store those keys per [secrets.md](secrets.md), never in the repository. Keep both the
dashboard and the gateway on a private network or behind an identity-aware fronting layer
([fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md), [caddy.md](caddy.md)) with MFA ([mfa.md](mfa.md)).

## OpenTelemetry Collector

The Collector is the pipe these tools (and others) receive traces through, and it ships with no security
applied until you configure it. The project's own hardening guidance: bind receivers to a specific interface
or `localhost` (for example `127.0.0.1:4317`). From Collector v0.110.0 the default host for every server in
Collector components is `localhost`; on earlier versions the default was all interfaces, and the
`component.UseLocalHostAsDefaultHost` feature gate switches it. Set the endpoint explicitly on any version
rather than trusting the default, and widen it only where a proxy or
mesh in front needs the wider bind; require TLS on every receiver and exporter; and attach an authenticator
extension, such as `basicauth` (htpasswd-style credentials, or a static `client_auth` username/password for
outgoing calls) or `bearertokenauth` (a static or file-backed token sent as an `Authorization` header), to any
receiver that accepts data from outside the host. An extension is wired to a receiver with an `auth.authenticator`
key naming the extension. Build or run only the receivers, processors, and exporters you use, since every
enabled component is attack surface, and run the process as a non-root user.

## Verify

```bash
ss -tlnp | grep -E ':(3000|6006|4317|4318) '                          # loopback or private only, never 0.0.0.0
curl -q -sS -o /dev/null -w '%{http_code}\n' https://langfuse.example.com/   # dashboard: login page or 401, never the project view
                                                                        # /api/public/health returns health status by design and is
                                                                        # not an access-control check; it proves nothing here
curl -q -sS -o /dev/null -w '%{http_code}\n' https://langfuse.example.com/api/public/projects
                                                                        # 401 without -u public-key:secret-key
curl -q -sS -o /dev/null -w '%{http_code}\n' https://otel-collector.internal:4318/v1/traces \
  -H 'Content-Type: application/json' -d '{"resourceSpans":[]}'
                                                                        # 401 or 403 without the configured auth header. The content
                                                                        # type matters: with curl's default form encoding the Collector
                                                                        # answers 415 on the body alone, before authentication, so the
                                                                        # rejection would prove nothing
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
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing" ;;
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

The OTLP trace-ingestion path is not probed with `curl` here, because a valid OTLP payload is protobuf and
hand-writing one in a one-line probe is not practical. Phoenix authenticates the `/v1` router, traces included,
so the write path's exposure tracks the read API's: govern it with the listener inventory (the `ss` table must
show the OTLP port bound to loopback or a private address) and by keeping the write path behind the
authenticated ingress.

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
- Arize Phoenix, authentication (`PHOENIX_ENABLE_AUTH`, `PHOENIX_SECRET`, system and user API keys, `PHOENIX_API_KEY`, the default `admin@localhost` / `admin` account, `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` read only at first-account creation, `/v1/` REST permissions, OAuth2/OIDC identity providers, and the absence of native MFA; read 2026-09-13): https://arize.com/docs/phoenix/self-hosting/features/authentication
- Helicone, self-hosted deployment (default `test@helicone.ai` / `password` login): https://docs.helicone.ai/getting-started/self-host/manual
- OpenTelemetry, Collector security best practices (bind addresses, TLS, authenticator extensions, minimal
  components, non-root): https://opentelemetry.io/docs/security/config-best-practices/
- OpenTelemetry Collector Contrib, `basicauthextension` (htpasswd, `client_auth`, `auth.authenticator` wiring): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/extension/basicauthextension
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
