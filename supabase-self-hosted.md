# Self-hosted Supabase

The self-hosted Supabase Docker stack ships a `.env.example` full of demo secrets, and its own
documentation says plainly: "you should never start your self-hosted Supabase using these defaults."
An unedited `docker compose up` publishes two surfaces to the host. The API gateway (Envoy by default,
Kong as an optional override) publishes port `8000`, which fronts the REST API, Auth, Storage, Edge
Functions and the Studio dashboard as plain HTTP; and the Supavisor connection pooler publishes `5432`
and `6543`, which are pooled PostgreSQL connections. Both are reachable with credentials printed in a
public example file, so the whole database is exposed until you replace them. This guide covers that
deployment; writing the row-level security policies that protect the data once it is reachable is
[firebase-supabase.md](firebase-supabase.md), and the database itself is
[postgresql.md](postgresql.md).

## 1. Regenerate every secret before the first start

The `.env.example` ships literal placeholders: `POSTGRES_PASSWORD` is
`your-super-secret-and-long-postgres-password`, `JWT_SECRET` is
`your-super-secret-jwt-token-with-at-least-32-characters-long`, `DASHBOARD_USERNAME` is `supabase` and
`DASHBOARD_PASSWORD` is `this_password_is_insecure_and_should_be_updated`, the `ANON_KEY` and
`SERVICE_ROLE_KEY` are pre-generated JWTs signed with that demo `JWT_SECRET`, and the S3 storage
credentials (`S3_PROTOCOL_ACCESS_KEY_ID` and `S3_PROTOCOL_ACCESS_KEY_SECRET`) are demo values of their
own. Rotating the two API keys is not enough on its own: because the demo `JWT_SECRET` is public,
anyone can mint a token for any role, including `service_role`, until the secret itself is replaced and
every key derived from it is reissued. Use the vendor's scripts to regenerate the JWT secret and the
keys together (`generate-keys.sh`, and `add-new-auth-keys.sh` for the JWT key pair; an existing
asymmetric setup also carries the secret in `JWT_KEYS`/`JWT_JWKS`, so change those too), set a strong
`DASHBOARD_PASSWORD`, `POSTGRES_PASSWORD` and S3 keys, and store the resulting `.env` as
[secrets.md](secrets.md) describes, never in the repository. On a stack that has already initialized
its database, changing `POSTGRES_PASSWORD` in `.env` alone does not take effect; follow the vendor's
separate database-password change procedure. Supabase's own "secure your services" checklist is the
authoritative list.

## 2. Keep the published ports off the public internet

The compose file publishes the API gateway on `8000` and the Supavisor pooler on `5432` and `6543` to
the host, on every interface. The `db` service has no host mapping of its own, but that is not
isolation: the Docker host can reach a container's ports directly, and the pooler exposes the database
anyway. Map the two published services to loopback (`127.0.0.1:8000:8000`, `127.0.0.1:5432:5432`,
`127.0.0.1:6543:6543`) or firewall them, and reach them over a private network or a tunnel
([docker.md](docker.md), [tunnels.md](tunnels.md)). Docker publishes ports through its own NAT rules,
which bypass a host firewall such as UFW and do not always leave a matching host listening socket, so
confirm the effective mapping with `docker` and test each port from an external vantage rather than
trusting the host's socket table. Neither the gateway nor Supavisor terminates TLS by default, so put a
reverse proxy in front for HTTPS on the API ([nginx.md](nginx.md), [caddy.md](caddy.md),
[fronting-auth.md](fronting-auth.md)); a web proxy does not protect the PostgreSQL wire protocol on
`5432`/`6543`, which needs its own TLS or an encrypted tunnel.

## 3. Treat the service_role key as full database access

The `SERVICE_ROLE_KEY` is not an API convenience: the role it names has the PostgreSQL `BYPASSRLS`
attribute, so it "skips every Row Level Security policy" and has full read and write access to your
data (it is not a database superuser, but for handling purposes treat it as one). It is a server-side
secret only; Supabase's documentation says never to put one in a browser, a shipped application, or
source control, because "exposing a secret key puts all of your project's data at risk". The `anon`
key is the opposite: it is meant to be public and is constrained by row-level security. That
protection only exists where you turn it on: a table with RLS enabled and no policy denies access,
which is the safe default, but a table with RLS never enabled is readable and writable through the
`anon` key. Enable RLS on every exposed table and write policies per
[firebase-supabase.md](firebase-supabase.md); a view can still serve its owner's rows past RLS, which
that guide also covers. The same `service_role` and `anon` roles apply on the self-hosted stack.

## 4. Close the authentication defaults you did not choose

Three defaults ship open. The Studio dashboard is served through the gateway and gated only by the
HTTP basic-auth pair `DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD`, whose shipped value
(`supabase` / `this_password_is_insecure_and_should_be_updated`) is a published credential; set a
strong password in section 1, and keep the gateway off the public internet regardless, since basic
auth is only as private as the connection carrying it. Edge Functions ship with
`FUNCTIONS_VERIFY_JWT=false`, and the gateway does not apply the API key to the `/functions/v1/` route,
so every deployed function is callable unauthenticated until you set a verification policy; inventory
your functions and decide each one's policy. And user registration ships open: `DISABLE_SIGNUP` is
`false` with `ENABLE_PHONE_SIGNUP` and `ENABLE_PHONE_AUTOCONFIRM` both `true`, so anyone can create an
account, phone sign-ups self-confirm, and rotating secrets does not close this. Set the registration
policy you actually want.

## 5. Verify

Each probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so
none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result so
it discriminates against a live instance; backlog row 2.27 tracks demonstrating them, including forging
a token with the demo `JWT_SECRET`, which is the check that proves the secret itself was rotated rather
than just the shipped keys swapped. Run each from an external vantage and read the `err` field: a
transport failure is inconclusive unless it is a connection refusal from that vantage, and the write-out
fields need curl 7.75.0 or newer.

```bash
# On the host: these published listeners should be bound to loopback or an internal interface.
# Docker publishes through NAT, so also test each port from an external host over IPv4 and IPv6.
ss -tlnp | grep -E ':(8000|5432|6543) '   # loopback or internal only
```

The gateway serves plain HTTP on `8000`. The block below calls an Edge Functions route without any
credential; substitute your own host and a function name. An exposed stack runs the function and
answers (`http=200`, or a function error, but not `401`), because `FUNCTIONS_VERIFY_JWT` is `false`; a
stack that enforces verification answers `401`.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_HOST' 'REPLACE_WITH_A_FUNCTION_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|*YOUR_HOST*|"") echo "substitute your host on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|*FUNCTION_NAME*|"") echo "substitute a function name on the set -- line above; not probing"; exit ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8000/functions/v1/$2"
)
```

Two more checks confirm the other surfaces, each the finding when it succeeds and refused only once the
port is private. The Studio dashboard is exposed if the gateway answers a request carrying the default
basic-auth `supabase:this_password_is_insecure_and_should_be_updated` (a `-u` argument against
`http://REPLACE_WITH_YOUR_HOST:8000/`) with `http=200` rather than `401`. The database is exposed if
`psql` connects to the Supavisor pooler on `5432` or `6543` with the demo `POSTGRES_PASSWORD`, as user
`postgres.POOLER_TENANT_ID` and database `postgres`; once the password is regenerated that connection
fails authentication rather than refusing at the TCP level.

## Sources (checked September 2026)

- Supabase self-hosting with Docker (Envoy gateway, secure your services, changing the database password): https://supabase.com/docs/guides/self-hosting/docker
- Supabase API keys (anon vs service_role, BYPASSRLS, keep secret): https://supabase.com/docs/guides/api/api-keys
- Supabase Row Level Security (a table without RLS is unprotected): https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase docker .env.example (default secrets, keys, FUNCTIONS_VERIFY_JWT, signup and S3 defaults): https://github.com/supabase/supabase/blob/master/docker/.env.example
- Supabase docker-compose.yml (published ports for the gateway and pooler): https://github.com/supabase/supabase/blob/master/docker/docker-compose.yml
