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
own, and the stack ships placeholder encryption secrets a step titled "regenerate every secret" must also cover: `SECRET_KEY_BASE` (at least 64 characters), `REALTIME_DB_ENC_KEY` (exactly 16), `VAULT_ENC_KEY` (exactly 32, which protects Supavisor's stored configuration, not the Postgres Vault extension's master key), and `PG_META_CRYPTO_KEY` (at least 32); the vendor generator sets these, so replace them manually only to those lengths. Rotating the two API keys is not enough on its own: because the demo `JWT_SECRET` is public,
anyone can mint a token for any role, including `service_role`, until the secret itself is replaced and
every key derived from it is reissued. Use the vendor's scripts to regenerate the JWT secret and the
keys together (`generate-keys.sh`, and `add-new-auth-keys.sh` for the JWT key pair; an existing
asymmetric setup also carries the secret in `JWT_KEYS`/`JWT_JWKS`, so change those too), set a strong
`DASHBOARD_PASSWORD`, `POSTGRES_PASSWORD` and S3 keys, and store the resulting `.env` as
[secrets.md](secrets.md) describes, never in the repository. Editing `.env` does not change running containers: after regenerating secrets and keys, recreate the affected
services (`sh run.sh recreate`) and confirm the old credentials are rejected. Removing the old HS256 secret
from every verifier invalidates the legacy API JWTs and user access tokens signed by it, and regenerating the
asymmetric key pair invalidates tokens signed by the previous pair; rotating only the newer opaque
`sb_publishable_*`/`sb_secret_*` keys does not rotate signing keys or invalidate user sessions. On a stack that
has already initialized its database, changing `POSTGRES_PASSWORD` in `.env` alone does not take effect; follow
the vendor's separate database-password change procedure (`sh utils/db-passwd.sh`, then recreate services). Supabase's own "secure your services" checklist is the
authoritative list.

## 2. Keep the published ports off the public internet

The compose file publishes the API gateway on `8000` and the Supavisor pooler on `5432` and `6543` to
the host, on every interface. The `db` service has no host mapping of its own, but that is not
isolation: the Docker host can reach a container's ports directly, and the pooler exposes the database
anyway. The optional Kong override additionally publishes HTTPS on `8443`, so include it when Kong is enabled. Map the
published services to loopback (`127.0.0.1:8000:8000`, `127.0.0.1:5432:5432`, `127.0.0.1:6543:6543`, and
`127.0.0.1:8443:8443` under Kong) or firewall them, and reach them over a private network or a tunnel
([docker.md](docker.md), [tunnels.md](tunnels.md)). Docker publishes ports through its own NAT rules,
which bypass a host firewall such as UFW and do not always leave a matching host listening socket, so
confirm the effective mapping with `docker` and test each port from an external vantage rather than
trusting the host's socket table. In the default Envoy deployment, neither the gateway nor Supavisor terminates TLS; the optional Kong override additionally provides an HTTPS listener on `8443`, so put a
reverse proxy in front for HTTPS on the API ([nginx.md](nginx.md), [caddy.md](caddy.md),
[fronting-auth.md](fronting-auth.md)); a web proxy does not protect the PostgreSQL wire protocol on
`5432`/`6543`, which needs its own TLS or an encrypted tunnel. If Edge Functions or Storage integrations fetch
user-controlled URLs, restrict the workload's egress to the destinations it needs and block cloud metadata and
unrelated internal services per [egress-metadata.md](egress-metadata.md); inbound JWT verification does not
constrain outbound requests.

## 3. Treat the service_role key as full database access

The `SERVICE_ROLE_KEY` is not an API convenience: the role it names has the PostgreSQL `BYPASSRLS`
attribute, so it "skips every Row Level Security policy" and has full read and write access to your
data (it is not a database superuser, but for handling purposes treat it as one). It is a server-side
secret only; Supabase's documentation says never to put one in a browser, a shipped application, or
source control, because disclosure of a secret key compromises the project's data. The `anon`
key is the opposite: it is meant to be public and is constrained by row-level security. That protection depends on SQL privileges and, when enabled, RLS. For an ordinary API role subject to RLS,
reading rows requires the applicable schema and table or column privileges plus a policy permitting those
rows. With those privileges present, RLS enabled, and no applicable policy, a `SELECT` returns no rows;
missing privileges instead produce a permission error. With RLS never enabled, the
operations the role is granted are unrestricted by row policy and readable or writable through the `anon` key.
`service_role` bypasses RLS but is still subject to SQL privileges. Enable RLS on every exposed table and write policies per
[firebase-supabase.md](firebase-supabase.md); a view can still serve its owner's rows past RLS, which
that guide also covers. The same `service_role` and `anon` roles apply on the self-hosted stack.

## 4. Close the authentication defaults you did not choose

Three defaults ship open. The Studio dashboard is served through the gateway and gated only by the
HTTP basic-auth pair `DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD`, whose shipped value
(`supabase` / `this_password_is_insecure_and_should_be_updated`) is a published credential; set a
strong password in section 1, and keep the gateway off the public internet regardless, since basic
auth is only as private as the connection carrying it. Gateway authentication is route-specific, not blanket: Studio's catch-all route is gated by the dashboard
Basic-auth pair, REST/GraphQL/Realtime and the protected Auth routes require an API key, and some Auth routes
(verify, callback, JWKS, SAML metadata) are open by design; Storage and Edge Functions bypass the gateway's
API-key check and enforce their own controls. Edge Functions ship with `FUNCTIONS_VERIFY_JWT=false`, so the
main worker applies no JWT check and every deployed function is callable unauthenticated (an individual
function may still authenticate) until you set a verification policy; inventory your functions and decide each
one's policy. Studio also listens internally on `3000` with no host mapping of its own: never publish that
port or otherwise route around the gateway's dashboard authentication. And user registration ships open: `DISABLE_SIGNUP` is
`false` with `ENABLE_PHONE_SIGNUP` and `ENABLE_PHONE_AUTOCONFIRM` both `true`, so anyone can create an
account, phone sign-ups self-confirm, and rotating secrets does not close this. Set the registration
policy you actually want. Supabase Auth supports TOTP MFA for application users (enforce the required
assurance level in your policies per [firebase-supabase.md](firebase-supabase.md) and [mfa.md](mfa.md)); that
does not add a factor to the dashboard's Basic auth, so put administrative Studio access behind a private path
or an identity-aware proxy that enforces MFA.

## 5. Verify

Each probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so
none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result so
it discriminates against a live instance; backlog row 2.27 tracks demonstrating them, including forging
a token with the demo `JWT_SECRET`, which is the check that proves the secret itself was rotated rather
than just the shipped keys swapped. There are two layers to check. First, from an external host none of these ports should answer at all: any HTTP or database response means the
port is published and is itself the finding, whatever the credentials do next. A refused connection is a failed
connection from that vantage rather than proof of durable firewall enforcement, and a timeout is inconclusive
(a wrong destination or dropped route looks the same), so corroborate a blocked port with the effective Docker
mapping, and confirm the service is actually live from an allowed vantage. The
credential checks below apply to a port you can still reach, because you have not isolated it yet or are
testing from an allowed internal vantage, and show whether the demo credentials were replaced. If you
front the gateway with a reverse proxy for HTTPS, aim the HTTP checks at that proxy rather than the raw
`8000`. Read the `err` field, since a transport failure is only conclusive when it is a connection
refusal from that vantage, and the write-out fields need curl 7.75.0 or newer.

```bash
# On the host: these published listeners should be bound to loopback or an internal interface.
# Docker publishes through NAT, so also test each port from an external host over IPv4 and IPv6.
ss -tlnp   # read every listener; 8000/5432/6543: loopback or internal only
```

The gateway serves plain HTTP on `8000`. Substitute the base URL, function name, and current legacy
`ANON_KEY` JWT inside the single quotes. Use a canary function with a known response and no independent
authentication. With `FUNCTIONS_VERIFY_JWT=false`, both requests should reach it; with verification
enabled, the credential-free request should receive `401` and the Bearer-authenticated request should
return its known response. An arbitrary function can return its own `401`, so that status alone does not
identify the main worker's policy.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BASE_URL' 'REPLACE_WITH_A_FUNCTION_NAME' 'REPLACE_WITH_CURRENT_ANON_JWT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the base URL (https://your-proxy, or http://127.0.0.1:8000 for a private-origin check); not probing"; exit 2 ;; esac
  case "$2" in *REPLACE_WITH_*|*FUNCTION_NAME*|"") echo "substitute a function name; not probing"; exit 2 ;; esac
  case "$3" in *REPLACE_WITH_*|"") echo "substitute a current legacy anon JWT; not probing"; exit 2 ;; esac
  # Compare the credential-free request with a current legacy anon JWT sent as Bearer.
  # Use a canary with a known response and no independent authentication.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nno-key http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/functions/v1/$2"
  printf 'Authorization: Bearer %s\n' "$3" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H @- -w '\nwith-key http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/functions/v1/$2"
)
```

For a port you can still reach, check whether the shipped credentials were replaced, feeding every credential
through stdin rather than argv (`curl --config -` for Basic auth, `curl --header @-` for `apikey`/`Authorization`;
disable shell tracing). Test each shipped API key against `/auth/v1/settings`, then repeat with a current key that must return
settings JSON. This checks gateway acceptance, not retirement of backend signing keys. Separately, test the
same harmless REST canary with two correctly formed, unexpired `service_role` JWTs carrying equivalent claims:
one signed with the current key and one with the demo `JWT_SECRET`. Keep a valid current `apikey` on both
requests. Require the current token to return the known canary result and the demo-signed token to receive a
PostgREST JWT signature-verification rejection; transport errors, gateway denials, and SQL permission failures
are inconclusive. This checks the REST verifier only; check other JWT-verifying services separately. The Studio dashboard still accepts the default Basic auth if the
gateway answers `supabase:this_password_is_insecure_and_should_be_updated` (via `--config -`) with `http=200`
rather than `401`, retrieving a known Studio response as the positive control. The database still accepts the
demo password if `psql` connects to the Supavisor pooler on `5432`/`6543` with the demo `POSTGRES_PASSWORD`, as
user `postgres.your-tenant-id` (the demo `POOLER_TENANT_ID`) and database `postgres`, running
`SELECT current_user, current_database();` before the demo-password rejection counts; once regenerated that
connection fails authentication.

## Sources (checked September 2026)

At the time of writing these deployment defaults are checked against `self-hosted/v0.8.1` (Envoy v1.39.1, Auth v2.196.0); compare your installed release and every Compose override before applying them.

- Supabase self-hosting with Docker (Envoy gateway, secure your services, changing the database password): https://supabase.com/docs/guides/self-hosting/docker
- Supabase API keys (anon vs service_role, BYPASSRLS, keep secret): https://supabase.com/docs/guides/api/api-keys
- Supabase Row Level Security (a table without RLS is unprotected): https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase docker .env.example (default secrets, keys, FUNCTIONS_VERIFY_JWT, signup and S3 defaults): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example
- Supabase docker-compose.yml (published ports for the gateway and pooler): https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml
