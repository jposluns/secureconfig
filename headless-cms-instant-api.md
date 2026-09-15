# Instant API backends: Strapi, Directus, Hasura, and PostgREST

These tools turn a database or a schema into a ready-made API with little or no code, which is
exactly why AI-assisted projects reach for them. That convenience is also the exposure: one
misconfiguration can put the whole datastore on the internet, and it happens two different ways
here. Strapi and Directus keep their data API closed until you open it, so their risk is the admin
and bootstrap surface, an admin account or a stored credential claimed before you claimed it. Hasura
and PostgREST instead expose whatever a single control allows, an unset admin secret or the grants
held by one database role, and both bind to every interface by default. All four read the secrets
that gate them, admin passwords or the signing keys that mint sessions and tokens, from environment
variables, so a committed Compose file or `.env` is the leak they share. Firebase, Supabase,
PocketBase and Appwrite are the same class from the other direction
([firebase-supabase.md](firebase-supabase.md), [pocketbase.md](pocketbase.md)).

## Strapi

Register the first administrator before the instance is reachable by anyone else. Strapi ships no
default admin password: the first visitor to the admin panel completes a form and becomes the first
administrator, so an admin panel left open to the internet before you register can be claimed by
whoever reaches it first. The server's documented default host is `localhost`, but the project
template Strapi generates sets `HOST` to `env('HOST', '0.0.0.0')`, so it listens on
every interface. Keep the admin panel off the public network until you have registered: on a bare
host set `HOST` to `127.0.0.1` for the bootstrap step; in a container leave the app bound inside the
container and publish its port only to the host loopback (`127.0.0.1:1337:1337`) or firewall it,
because setting the container's own `HOST` to `127.0.0.1` makes the published port unreachable. Only
then expose it.

The data API itself is closed by default. Strapi's documentation states that "all content types are
private by default and need to be either made public or queries need to be authenticated with the
proper permissions", so an unauthenticated request assumes the Public role, which reaches no content
type until an administrator grants it (a denied request returns `403 Forbidden`). Two exposures
remain. Uploaded files are not covered by that default: Strapi serves the Media Library through a
static file middleware based on `koa-static`, which does not authenticate, so files stored with the
default local provider are public even while every content type is private; keep confidential files
out of it or serve them from access-controlled storage. And end-user sign-up
(`POST /api/auth/local/register`) is an administrator toggle, so confirm it is set the way you expect
rather than assuming its state; a registered end user takes the Authenticated role, which itself has
no content grants until one is added.

Set unique, randomized values for the application secrets Strapi reads from the environment; the
server configuration documents `APP_KEYS` (the session signing keys), the admin-panel
configuration adds `ADMIN_JWT_SECRET`, `API_TOKEN_SALT` and `TRANSFER_TOKEN_SALT`, and the Users and
Permissions plugin configuration adds `JWT_SECRET`. A copied example `.env` lets anyone holding the same values forge sessions or
tokens; store them as [secrets.md](secrets.md) describes, never in the repository or a client bundle.
Strapi terminates no TLS of its own, so front it per [nginx.md](nginx.md) or [caddy.md](caddy.md) and
[fronting-auth.md](fronting-auth.md).

## Directus

Directus creates its first user from environment variables at first startup: `ADMIN_EMAIL` and
`ADMIN_PASSWORD` set that account, and `ADMIN_TOKEN`, if set, is a static API token carrying that
admin's full rights that does not expire. Because every one of these arrives through the environment,
a committed Compose file or `.env` is an admin-credential leak; set unique operator-controlled values
before first boot and store them per [secrets.md](secrets.md). Leave `ADMIN_TOKEN` unset unless a
machine genuinely needs a static token, prefer a scoped credential where one is needed
([machine-auth.md](machine-auth.md)), and require two-factor authentication on administrator accounts
(a static token still works independently of an interactive login, so treat it as the more dangerous
credential).

Access for unauthenticated callers is closed by default: Directus documents that "all public
permissions are off by default", so the Public role and policy reach no collection until an
administrator enables it. The real exposures are therefore the bootstrap credentials above and any
grant an operator later adds to the Public policy, including file read permissions that make items
served at `/assets` reachable; review those grants rather than assuming the default still holds. The
default port is `8055`. Directus serves no TLS itself, so terminate it in front per
[nginx.md](nginx.md) or [caddy.md](caddy.md) and [fronting-auth.md](fronting-auth.md).

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
since setting it defines what an unauthenticated caller may do.

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
server binds to every IPv4 interface by default (`server-host` defaults to `!4`, on port 3000), so set
`server-host` to `127.0.0.1` for a host-local deployment or keep the port off the public interface;
the optional admin server (`admin-server-port`) defaults to that same host (an `admin-server-host` can override it), so account for it too.
PostgREST terminates no TLS itself; front it per [nginx.md](nginx.md) or [caddy.md](caddy.md).

## Verify

Each probe below is reasoned, not demonstrated: the authoring environment has no container runtime,
so none was stood up in its exposed and fixed states. Each names its expected exposed and fixed
result so it discriminates when run against a live instance; backlog row 2.25 tracks demonstrating
them. Give each a harmless canary record (a row, item or content-type entry whose one field reads
`secureconfig-canary`) and run an authorized request for the same record as a positive control, so a
probe that returns nothing because the service is down is not misread as "fixed". Treat an empty
result, an unrelated error, an HTML page, or a transport failure as inconclusive, never as the fixed
state. Substitute your own host for the `example.com` placeholder.

```bash
# Strapi: point this at a content type you have opened; exposed returns the canary, the default 403s.
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://cms.example.com/api/secureconfig-probes'
# Directus: point this at a collection whose Public policy you granted; exposed returns the canary,
# the default answers 403 FORBIDDEN.
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://cms.example.com/items/secureconfig_probe?filter[marker][_eq]=secureconfig-canary&fields=marker'
# Hasura data API: no admin secret returns data; fixed returns an admin-secret-required error IN THE BODY.
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H 'Content-Type: application/json' \
  -d '{"query":"query { secureconfig_probe(where: {marker: {_eq: \"secureconfig-canary\"}}) { marker } }"}' \
  'https://graphql.example.com/v1/graphql'
# Hasura console: the recommended posture disables it, so this should return a JSON not-found; a 200
# HTML page means the console is still served (login-gated if the secret is set, open if not).
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://graphql.example.com/console'
# PostgREST: no Authorization header; exposed returns the canary, fixed answers PGRST302 (401).
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://api.example.com/secureconfig_probe?select=marker&marker=eq.secureconfig-canary'
```

The Strapi and Directus probes only tell you about the one collection you point them at, since both
deny by default; run them against the collections you actually opened, and read the full grant list
in the tool (the Directus access policies, the Strapi role permission matrix) rather than trusting a
single canary. Read the body, not the bare status: Hasura's GraphQL API answers HTTP 200 even for an authorization
error by default (Hasura documents this and the `HASURA_GRAPHQL_PRESERVE_401_ERRORS` flag that
returns 401 for authentication failures instead), so the fixed state is the admin-secret-required
message in the JSON. A served console page is not itself the exposure; the data-API probe above is
what shows whether admin operations are gated.
For PostgREST, repeat the data probe with `-H 'Authorization: Bearer not-a-real-jwt'` and expect
`PGRST301`, which confirms a bad token is rejected rather than treated as anonymous. When anonymous
access is deliberate, an HTTP check cannot tell an intended grant from an over-broad one, so read the
privileges directly in the database, including role membership, function `EXECUTE`, and any
row-level policies, not only table grants. Finally, on the host, `sudo ss -tlnp` should show the
listeners on ports 1337, 8055, 8080, 8081 and 3000 bound to loopback or an internal interface rather
than a wildcard address; because Docker publishes ports through NAT rules that a host socket listing
can miss, also inspect the Compose published ports and probe each host port from an external vantage,
over IPv4 and IPv6.

## Sources (checked September 2026)

- Strapi Users and Permissions (public role, sign-up): https://docs.strapi.io/cms/features/users-permissions
- Strapi REST API (content types private by default): https://docs.strapi.io/cms/api/rest
- Strapi quick start (first administrator): https://docs.strapi.io/cms/quick-start
- Strapi server configuration (HOST, PORT, APP_KEYS): https://docs.strapi.io/cms/configurations/server
- Strapi admin-panel configuration (ADMIN_JWT_SECRET, API_TOKEN_SALT, TRANSFER_TOKEN_SALT): https://docs.strapi.io/cms/configurations/admin-panel
- Strapi plugins configuration (Users and Permissions JWT_SECRET): https://docs.strapi.io/cms/configurations/plugins
- Strapi middlewares (public static file serving via koa-static): https://docs.strapi.io/cms/configurations/middlewares
- Strapi Media Library (upload providers): https://docs.strapi.io/cms/features/media-library
- Directus configuration, first admin user (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_TOKEN; PORT default 8055): https://directus.com/docs/configuration/general
- Directus access control (public permissions off by default): https://directus.com/docs/guides/auth/access-control
- Hasura securing the GraphQL endpoint: https://hasura.io/docs/2.0/deployment/securing-graphql-endpoint/
- Hasura GraphQL Engine flags reference (SERVER_HOST, ENABLE_CONSOLE, ENABLED_APIS, DEV_MODE, UNAUTHORIZED_ROLE): https://hasura.io/docs/2.0/deployment/graphql-engine-flags/reference/
- PostgREST configuration reference (db-anon-role, db-schemas, server-host, jwt-secret): https://postgrest.org/en/stable/references/configuration.html
- PostgREST authentication and roles: https://postgrest.org/en/stable/references/auth.html
- PostgREST error codes (PGRST300 to PGRST303): https://postgrest.org/en/stable/references/errors.html
- PostgREST OpenAPI output at the root path: https://postgrest.org/en/stable/references/api/openapi.html
