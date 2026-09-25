# Instant API backends: Strapi, Directus, Hasura, and PostgREST

These tools turn a database or a schema into a ready-made API with little or no code, which is
exactly why AI-assisted projects reach for them. That convenience is also the exposure: one
misconfiguration can put the whole datastore on the internet, and it happens two different ways
here. Strapi and Directus keep their data API closed until you open it, so their risk is the admin
and bootstrap surface, an admin account or a stored credential claimed before you claimed it. Hasura
and PostgREST instead expose whatever a single control allows, an unset admin secret or the grants
held by one database role, and both bind to every interface by default. All four read the secrets
that gate them, admin passwords, API tokens, or the signing keys that mint sessions and tokens, from
environment variables, so a committed Compose file or `.env` is the leak they share. Firebase, Supabase,
PocketBase and Appwrite are the same class from the other direction
([firebase-supabase.md](firebase-supabase.md), [pocketbase.md](pocketbase.md)).

## Strapi

Register the first administrator before the instance is reachable by anyone else. Strapi ships no
default admin password: the first visitor to the admin panel completes a form and becomes the first
administrator, so an admin panel left open to the internet before you register can be claimed by
whoever reaches it first. The server's documented default host is `localhost`, but the generated server
configuration sets `host: env('HOST', '0.0.0.0')`, so it listens on
every interface. Keep the admin panel off the public network until you have registered: on a bare
host set `HOST` to `127.0.0.1` for the bootstrap step; in a container leave the app bound inside the
container and publish its port only to the host loopback (`127.0.0.1:1337:1337`) or firewall it,
because setting the container's own `HOST` to `127.0.0.1` makes the published port unreachable. Only
then expose it, and expose only the intended public API routes: keep the admin panel (`/admin` by default) and
its backend management routes behind a VPN or an access proxy that enforces MFA, since hiding the admin path
does not protect its backend routes. Strapi ships no native multi-factor authentication for the admin panel;
where Strapi SSO is available, require MFA at the identity provider and close local-login bypasses for those
administrator roles ([fronting-auth.md](fronting-auth.md), [mfa.md](mfa.md)).

The data API itself is closed by default. Strapi's documentation states that "all content types are
private by default and need to be either made public or queries need to be authenticated with the
proper permissions", so an unauthenticated request assumes the Public role, which reaches no content
type until an administrator grants it (a denied request returns `403 Forbidden`). Two exposures
remain. Uploaded files are not covered by that default: Strapi serves the Media Library through a
static file middleware based on `koa-static`, which does not authenticate, so files stored with the
default local provider are public even while every content type is private; keep confidential files
out of it or serve them from access-controlled storage. Unless public registration is required, disable end-user sign-up in Settings > Users & Permissions plugin >
Advanced Settings > Enable sign-ups, which controls `POST /api/auth/local/register`; its initial value requires
confirmation against your Strapi release rather than assuming a default. If registration is intentional, review
the configured Default role and its permissions rather than assuming a registered user has only the access you
intended; new end users receive the configured Default role, so review that role's actual permissions before enabling registration.

Strapi also pre-generates Full access and Read-only Content API tokens. Review them under Settings > API
Tokens, delete unused ones, and give any you keep a finite lifetime; a Read-only token still permits `find` and
`findOne`, so use Custom permissions when access must be limited to particular endpoints. These Content API
tokens are separate credentials from administrator tokens, and closing the Public role does not revoke them.

Set unique, randomized values for the application secrets Strapi reads from the environment; the
server configuration documents `APP_KEYS` (the session signing keys), the admin-panel
configuration adds `ADMIN_JWT_SECRET`, `API_TOKEN_SALT` and `TRANSFER_TOKEN_SALT`, and the Users and
Permissions plugin configuration adds `JWT_SECRET`. Protect `ENCRYPTION_KEY` too where it is configured for stored-token encryption. A copied example `.env` lets
anyone holding the signing keys forge sessions or JWTs (the API token salts are not themselves bearer tokens);
store these values as [secrets.md](secrets.md) describes, never in the repository or a client bundle, and rotate
and revoke any that leak.
If the optional GraphQL plugin is installed it exposes `/graphql` with `shadowCRUD` generating queries and
mutations, and it passes Apollo options through `graphql.config.apolloServer`; Apollo enables introspection
unless `NODE_ENV=production`, so set `graphql.config.apolloServer.introspection` and `graphql.config.landingPage`
to `false` when schema browsing is unnecessary. Those settings do not replace resolver authorization. Strapi
terminates no TLS of its own, so front it per [nginx.md](nginx.md) or [caddy.md](caddy.md) and
[fronting-auth.md](fronting-auth.md).

## Directus

Directus supports bootstrap credentials through `ADMIN_EMAIL` and `ADMIN_PASSWORD`, with an optional
`ADMIN_TOKEN` static API token carrying that admin's full rights that does not expire; its current 12.0.2
quickstart also offers browser onboarding for the first administrator. Keep a fresh instance private until an
operator-controlled administrator has been created and verified, rather than assuming that omitting the
environment variables makes bootstrap inaccessible. Because every one of these arrives through the environment,
a committed Compose file or `.env` is an admin-credential leak; set unique operator-controlled values
before first boot and store them per [secrets.md](secrets.md). Set `SECRET` to a unique, cryptographically
random value stored through your secret manager as well: it signs the sessions and access tokens Directus
mints, so a value copied from an example Compose file lets anyone holding it forge tokens, and if omitted
Directus generates a random value that does not persist consistently across restarts or replicas. Behind HTTPS,
set `SESSION_COOKIE_SECURE=true` and `REFRESH_TOKEN_COOKIE_SECURE=true`; both default to `false`. Leave
`ADMIN_TOKEN` unset unless a
machine genuinely needs a static token, prefer a scoped credential where one is needed
([machine-auth.md](machine-auth.md)), and require two-factor authentication on administrator accounts
(a static token still works independently of an interactive login, so treat it as the more dangerous
credential).

Access for unauthenticated callers is closed by default: Directus documents that "all public
permissions are off by default", so the Public role and policy reach no collection until an
administrator enables it. The real exposures are therefore the bootstrap credentials above and any
grant an operator later adds to the Public policy, including file read permissions that make items
served at `/assets` reachable; review those grants rather than assuming the default still holds, and protect the
underlying upload directory or object-storage bucket too, because a public storage URL can bypass Directus asset
permissions (grant upload, import, update and delete separately from read). Directus registration is disabled by
default; leave it off unless required, and note that its registration flow returns an empty `204` regardless of
outcome, so a response alone is not proof an account was rejected. GraphQL introspection is enabled by default
(`GRAPHQL_INTROSPECTION=true`); set it to `false` when schema discovery is unnecessary, reviewing GraphQL under
the same roles and policies as REST. Directus defaults to `HOST=0.0.0.0` on port `8055` (as of v12.4.1,
unless `UNIX_SOCKET_PATH` is non-empty) and serves the Data Studio (`/` redirects to `/admin`); on a bare host set
`HOST=127.0.0.1`, in Docker publish
`127.0.0.1:8055:8055` or use an unpublished private network, and protect administration after bootstrap
(disabling `SERVE_APP` hides the Studio but does not replace API authorization). Directus serves no TLS itself,
so terminate it in front per [nginx.md](nginx.md) or [caddy.md](caddy.md) and [fronting-auth.md](fronting-auth.md).

## Hasura (GraphQL Engine v2, self-hosted)

Set `HASURA_GRAPHQL_ADMIN_SECRET`. With no admin secret configured, the GraphQL API (and the console,
where it is enabled) is reachable by anyone with full administrative rights: the vendor's own guidance
is to set the secret so "your GraphQL endpoint and the Hasura Console are not publicly accessible",
and the secret grants "full admin rights", so it is a bearer credential that must never be
embedded or distributed in an end-user application, a public bundle, or browser code delivered to
untrusted users ([secrets.md](secrets.md)). The engine binds to every interface by
default (`HASURA_GRAPHQL_SERVER_HOST` defaults to `*`, on port 8080); set it to `127.0.0.1` for a
host-local deployment or keep the published port off the public interface. Hasura terminates no TLS
of its own, so front it per [nginx.md](nginx.md) or [caddy.md](caddy.md).

Two defaults are worth knowing. The server binary ships with the console off
(`HASURA_GRAPHQL_ENABLE_CONSOLE` defaults to `false`, and it is served on `/` and `/console` when
enabled), but the vendor's quickstart Compose file turns it on, so a stack started from that file
serves the console until you set it back to `false`; keep `HASURA_GRAPHQL_DEV_MODE` at `false` in
production as well. That same quickstart Compose also publishes a separate data-connector agent on
port 8081 and carries literal PostgreSQL credentials, so treat 8081 as another listener to keep off
the public interface and replace those credentials. And `HASURA_GRAPHQL_ENABLED_APIS` defaults to
`metadata, graphql, pgdump, config`, so the metadata, pgdump and config APIs are served alongside
GraphQL; once the admin secret is set they require it, but narrow the list if your deployment does
not use them. Leave `HASURA_GRAPHQL_UNAUTHORIZED_ROLE` unset unless anonymous access is intended,
since setting it defines what an unauthenticated caller may do. Hasura also enables GraphQL introspection by
default; the documented per-role control to disable it is a self-hosted Enterprise feature, so do not assume
Community Edition can turn it off, and authenticate access and review each role's schema and data permissions
regardless. Client applications should use scoped JWT or webhook authentication, never the admin secret.

## PostgREST

PostgREST's access control is not one of its own flags: it is the PostgreSQL `GRANT` and `REVOKE`
statements on the roles it uses, so its posture is only as tight as the database privileges behind it
([postgresql.md](postgresql.md)). A request with no JSON Web Token runs as the role named by
`db-anon-role` (`PGRST_DB_ANON_ROLE`); that role has no default, and when it is unset an
unauthenticated request is refused with `PGRST302` (HTTP 401). A token that is present but does not
verify is rejected rather than downgraded to the anonymous role: a malformed or bad-signature token
returns `PGRST301` (HTTP 401) and an expired token or one failing claims validation returns `PGRST303`
(HTTP 401).

For a private API, leave `db-anon-role` unset. Where anonymous access is intended, point it at a
dedicated `NOLOGIN` role whose grants are enumerated and minimal, never a broad or superuser-adjacent
role, because whatever that role can read or write is what the internet can, and audit the
authenticator and authenticated roles the same way (function `EXECUTE` defaults to `PUBLIC`, and
`SECURITY DEFINER` functions and owner-privileged views can widen access beyond the table grants). Set
`db-schemas` to a schema built for the API rather than leaving it at its default of `public`. Note
that PostgREST serves an OpenAPI description at the root path whose contents follow the requesting
role's privileges by default, so a broad anonymous role also broadens what an unauthenticated caller
can enumerate. Set `jwt-secret` (`PGRST_JWT_SECRET`) to a cryptographically random value of at least 32
characters; if a token is sent while it is unset, the request fails with `PGRST300` (HTTP 500). The
server binds to every IPv4 interface by default (`server-host` defaults to `!4`, on port 3000, as of v16.4), so set
`server-host` to `127.0.0.1` for a host-local deployment or keep the port off the public interface;
the optional admin server (`admin-server-port`) defaults to that same host (an `admin-server-host` can override it), so account for it too.
PostgREST terminates no TLS itself; front it per [nginx.md](nginx.md) or [caddy.md](caddy.md).

## Across all four

Three of the four call outward on demand (Strapi webhooks, Directus Flows, Hasura event triggers, Actions and
remote schemas), and PostgREST can through a database function or extension, so restrict each service's outbound
access to the destinations it needs and block cloud metadata, loopback, link-local and unrelated private
networks, applying the restriction after DNS resolution and across redirects ([egress-metadata.md](egress-metadata.md)).
Directus documents an `IMPORT_IP_DENY_LIST` defaulting to `0.0.0.0,169.254.169.254`, but that import-specific
control is not evidence that every extension or Flow is equally constrained. Store database passwords and
credential-bearing connection strings per [secrets.md](secrets.md), including backups and exported
configuration; give each service a dedicated database account with only the privileges it needs, keep the
database listener private, and for a remote database require encrypted transport with server-certificate
verification (frontend HTTPS does not secure the database connection). Require MFA for human administration
throughout: an MFA-enforcing proxy or SSO for Strapi, enforced administrator 2FA for Directus, and MFA at the
identity provider or access boundary for Hasura and PostgREST, since an admin secret or bearer JWT is not itself
a second factor; give machine credentials their own scope, expiry and revocation ([mfa.md](mfa.md),
[machine-auth.md](machine-auth.md)).

## Verify

Each probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so none was
stood up in its exposed and fixed states. Each names its expected exposed and fixed result so it discriminates
when run against a live instance; backlog row 2.25 tracks demonstrating them. Give each tool a harmless canary
record whose one field reads `secureconfig-canary`, use curl 7.75.0 or later, and run the paired block once per
applicable endpoint: it sends the same URL and body twice, first with a valid credential and then anonymously,
so the authorized control proves the origin is the service and the canary exists before an application denial
can count as protection. Load the authorized header into `CMS_PROBE_HEADER` from your secret manager or an
interactive prompt, never on the command line (`Authorization: Bearer ...` for Strapi, Directus and PostgREST,
or `X-Hasura-Admin-Secret: ...` for Hasura); leave `CMS_NEGATIVE_HEADER` unset for the anonymous test. Treat an
empty result, a missing route, an unrelated error, an HTML page, a TLS error, or a timeout as inconclusive,
never as the fixed state. Substitute your own host for the `example.com` placeholder.

| Tool | Path appended to the deployment's HTTPS origin | JSON body | Expected private-state negative |
|---|---|---|---|
| Strapi | `/api/secureconfig-probes?filters[marker][$eq]=secureconfig-canary&fields[0]=marker` | empty | permission denial, normally 403 |
| Directus | `/items/secureconfig_probe?filter[marker][_eq]=secureconfig-canary&fields=marker` | empty | 403 with `FORBIDDEN` |
| Hasura | `/v1/graphql` | `{"query":"query { secureconfig_probe(where: {marker: {_eq: \"secureconfig-canary\"}}) { marker } }"}` | admin-secret-required JSON error |
| PostgREST | `/secureconfig_probe?select=marker&marker=eq.secureconfig-canary` | empty | 401 with `PGRST302` when the anonymous role is unset |

```bash
(
  set +x                                  # keep the credential out of any shell trace
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_CANARY_URL' ''
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'the set -- line needs a URL and a JSON body (empty for GET); not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*example.com*|*example.net*|*example.org*)
      echo 'substitute your own canary URL inside the quotes; not probing'; exit 2 ;;
    https://*) ;;
    *) echo 'use an https:// URL; not probing'; exit 2 ;;
  esac
  case "${CMS_PROBE_HEADER-}" in
    ''|*REPLACE_WITH_*) echo 'load a valid control header into CMS_PROBE_HEADER; not probing'; exit 2 ;;
  esac
  printf '%s\n' 'AUTHORIZED CONTROL (must return the canary):'
  if [ -z "$2" ]; then
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --header @- "$1" <<< "$CMS_PROBE_HEADER" || exit 2
  else
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -H 'Content-Type: application/json' --data-raw "$2" \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --header @- "$1" <<< "$CMS_PROBE_HEADER" || exit 2
  fi
  printf '%s\n' 'NEGATIVE (anonymous unless CMS_NEGATIVE_HEADER is set):'
  if [ -z "$2" ]; then
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --header @- "$1" <<< "${CMS_NEGATIVE_HEADER-}" || exit 2
  else
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -H 'Content-Type: application/json' --data-raw "$2" \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --header @- "$1" <<< "${CMS_NEGATIVE_HEADER-}" || exit 2
  fi
  printf '%s\n' 'Requests done; compare both bodies. Exit 0 is not a security verdict.'
)
```

Read the body, not the bare status. The Strapi and Directus probes only cover the one collection you point them
at, since both deny by default; run them against the collections you actually opened and read the full grant
list in the tool (the Directus access policies, the Strapi role permission matrix). Hasura answers HTTP 200 even
for an authorization error by default (its `HASURA_GRAPHQL_PRESERVE_401_ERRORS` flag, Community Edition 2.48.0
and later, preserves authentication failures as HTTP 401 instead; the quickstart Compose ships 2.46.0), so the
fixed state is the admin-secret-required message in the JSON. For PostgREST, repeat the negative with an
invalid token by setting `CMS_NEGATIVE_HEADER='Authorization: Bearer not-a-real-jwt'` and expect `PGRST301`,
which confirms a bad token is rejected rather than treated as anonymous; a missing or expired token gives
`PGRST302` or `PGRST303`.

A malformed token discriminates nothing about the real credentials, so also test the ones this deployment
actually uses. Repeat the paired request using the old credential after retirement: a deleted Strapi Content API token, a
Directus static token replaced or cleared on the existing user through the Data Studio or Users API, a Hasura
admin secret removed from the running configuration, or an otherwise valid, unexpired canary JWT signed with a
key the verifier no longer accepts. Changing Directus's bootstrap `ADMIN_TOKEN` environment variable alone is
not a rotation procedure for an existing user's token. Load the old credential into `CMS_NEGATIVE_HEADER`,
keeping the valid control, origin, path and body unchanged, and require an application authentication failure
attributable to the retired credential; a permission denial, proxy rejection or unrelated error does not
establish revocation. For administrator passwords, use a fresh browser session at the same login origin: the
operator-controlled password must authenticate while the old or copied one fails credential validation, and a
missing OTP, account lockout or proxy denial does not establish that the old password was rejected. There is no
universal default Strapi administrator password or pre-generated token value; confirm the actual bootstrap
values for this deployment.

A served console page is not itself the exposure; the data-API probe is what shows whether admin operations are
gated. As a reasoned console check, request `GET /console` and `GET /` on the same Hasura origin as the
successful control: with the console enabled in an isolated baseline it returns HTML, and after disabling it the
engine returns a JSON not-found; a proxy-generated 404 or a failed control is inconclusive. Where introspection
must be off, send `{"query":"{ __schema { queryType { name } } }"}` to the GraphQL endpoint and require an
introspection-specific rejection while an ordinary permitted query still succeeds there. The read canary does
not test writes, registration, media, MFA or egress: in an isolated test dataset repeat each configured create,
update, delete, upload and RPC with authorized and unauthorized identities and check the resulting datastore
state; verify registration with a disposable identity and inspect whether an account was created; verify a
private file with an authorized retrieval before an anonymous one, including any direct storage URL; verify MFA
by comparing a completed second factor with password-only access; and exercise a URL-fetching integration
against an allowed and an operator-controlled forbidden destination, confirming the forbidden one receives no
request.

Finally, inspect host listeners, container networking, published ports and firewall rules: `ss -tlnp` shows the
listeners on ports 1337, 8055, 8080, 8081 and 3000 (plus any configured PostgREST admin port) in this network
namespace only, which is not proof of external isolation. From an untrusted vantage, first confirm the same
origin responds from an allowed one, then probe each configured origin and port directly with the guarded block
below, over IPv4 and IPv6 (put a literal IPv6 address in brackets). Any HTTP response, including 401, 403 or
404, proves reachability; a timeout, DNS failure or TLS error does not prove isolation. Keep the optional
PostgREST admin server private independently of application JWT permissions.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DIRECT_ORIGIN_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 origin URL; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*example.com*|*example.net*|*example.org*|*203.0.113.*|*198.51.100.*|*192.0.2.*|*2001:db8*)
      echo 'substitute the real origin URL inside the quotes; not probing'; exit 2 ;;
    http://*|https://*) ;;
    *) echo 'give a complete http:// or https:// URL; not probing'; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1" || {
      echo 'any received HTTP status still means reachable; otherwise this failure is inconclusive'
      exit 2
    }
  echo 'an HTTP response means the origin is reachable, including 401, 403 and 404'
  exit 1
)
```

## Sources (checked September 2026)

Version boundary at the time of writing: Strapi 5 documentation; current Directus documentation (its quickstart uses 12.0.2); Hasura GraphQL Engine v2.x (the quickstart Compose names 2.46.0, and the authentication-status option requires Community Edition 2.48.0); PostgREST documentation identifying itself as version 16. These documentation URLs are rolling references unless a release is named; the Strapi sign-up default is left explicitly unconfirmed until a release-specific source establishes it.

- Strapi Users and Permissions (public role, sign-up): https://docs.strapi.io/cms/features/users-permissions
- Strapi REST API (content types private by default): https://docs.strapi.io/cms/api/rest
- Strapi quick start (first administrator): https://docs.strapi.io/cms/quick-start
- Strapi server configuration (HOST, PORT, APP_KEYS): https://docs.strapi.io/cms/configurations/server
- Strapi admin-panel configuration (ADMIN_JWT_SECRET, API_TOKEN_SALT, TRANSFER_TOKEN_SALT): https://docs.strapi.io/cms/configurations/admin-panel
- Strapi Users and Permissions security configuration (`JWT_SECRET`): https://docs.strapi.io/cms/features/users-permissions#security-configuration
- Strapi middlewares (public static file serving via koa-static): https://docs.strapi.io/cms/configurations/middlewares
- Strapi Media Library (upload providers): https://docs.strapi.io/cms/features/media-library
- Directus configuration, first admin user (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_TOKEN; PORT default 8055): https://directus.com/docs/configuration/general
- Directus `HOST` default `0.0.0.0` and `PORT` default 8055, and the branch that replaces them when `UNIX_SOCKET_PATH` is non-empty (pinned tag v12.4.1): https://github.com/directus/directus/blob/v12.4.1/packages/env/src/constants/defaults.ts#L9-L10 and https://github.com/directus/directus/blob/v12.4.1/api/src/server.ts#L169-L182
- Directus access control (public permissions off by default): https://directus.com/docs/guides/auth/access-control
- Hasura securing the GraphQL endpoint: https://hasura.io/docs/2.0/deployment/securing-graphql-endpoint/
- Hasura GraphQL Engine flags reference (SERVER_HOST, ENABLE_CONSOLE, ENABLED_APIS, DEV_MODE, UNAUTHORIZED_ROLE): https://hasura.io/docs/2.0/deployment/graphql-engine-flags/reference/
- PostgREST configuration reference (db-anon-role, db-schemas, server-host, jwt-secret): https://postgrest.org/en/stable/references/configuration.html
- PostgREST `server-host` default `!4` (L556), `server-port` default 3000 (L386), and `admin-server-host` falling back to `server-host` (L357-L360) (pinned tag v16.4): https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L556
- PostgREST authentication and roles: https://postgrest.org/en/stable/references/auth.html
- PostgREST error codes (PGRST300 to PGRST303): https://postgrest.org/en/stable/references/errors.html
- PostgREST OpenAPI output at the root path: https://postgrest.org/en/stable/references/api/openapi.html
- PostgREST admin server (optional health/metrics listener): https://postgrest.org/en/stable/references/admin_server.html
- Strapi API tokens (pre-generated Full access and Read-only tokens, scopes, lifetime): https://docs.strapi.io/cms/features/api-tokens
- Strapi SSO (administrator single sign-on): https://docs.strapi.io/cms/features/sso
- Directus security and limits (`SECRET`, cookie flags, `IMPORT_IP_DENY_LIST`): https://directus.com/docs/configuration/security-limits
- Directus file access (asset permissions and storage bypass): https://directus.com/docs/guides/files/access
- Hasura disable GraphQL introspection (self-hosted Enterprise control): https://hasura.io/docs/2.0/security/disable-graphql-introspection/
- Hasura Community Edition 2.48.0 release notes (`HASURA_GRAPHQL_PRESERVE_401_ERRORS`): https://hasura.io/changelog/community-edition/v2.48.0
- Strapi 5 GraphQL plugin (endpoint, shadowCRUD, apolloServer, landingPage): https://docs.strapi.io/cms/plugins/graphql
- Apollo Server 4-5 introspection default: https://www.apollographql.com/docs/apollo-server/api/apollo-server#introspection
- Strapi 5 administrator MFA options (vendor statement, September 2026): https://strapi.io/blog/strapi-admin-panel-mfa-2fa
- Directus quickstart (12.0.2 Compose and browser onboarding): https://directus.com/docs/getting-started/create-a-project
- Directus registration (disabled by default; empty 204 response): https://directus.com/docs/guides/auth/creating-users
- Directus static tokens (scope, persistence and management): https://directus.com/docs/guides/auth/tokens-cookies
- Directus error codes (authentication versus permission failures): https://directus.com/docs/guides/connect/errors
- Hasura v2 Docker quickstart (selects the stable Compose manifest): https://hasura.io/docs/2.0/getting-started/docker-simple/
- Hasura stable quickstart Compose (2.46.0 when checked): https://raw.githubusercontent.com/hasura/graphql-engine/5fa3e0d2b617a4ae85f65491c5ff6c056cb612de/install-manifests/docker-compose/docker-compose.yaml
