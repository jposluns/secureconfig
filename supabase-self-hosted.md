---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7b148279d78c4f1bf31d47ab41b3c410c6840c43048393bba146da2d7184ac16",
  "components": {
    "docs": {
      "name": "Supabase documentation",
      "basis": "unknown",
      "sources": {
        "s399d0fbba196": "https://supabase.com/docs/guides/self-hosting/docker",
        "s73d939b4644e": "https://supabase.com/docs/guides/api/api-keys",
        "s46cff2590323": "https://supabase.com/docs/guides/database/postgres/row-level-security"
      }
    },
    "env": {
      "name": "Supabase environment source",
      "basis": "eabe06be5b36cf57f2b158bd5093b396606bf801",
      "sources": {
        "sb8e42c6de990": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example",
        "sed49ce6bde76": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L30-L36",
        "sc520e7d9db9f": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L57-L59",
        "sb241a3887d73": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L61-L75",
        "sb600d65cc47b": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L84-L89",
        "s7e03d1d4ecba": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L142-L145",
        "s8f596f22364d": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L174-L196",
        "s8d1a17b9f899": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L301-L305"
      }
    },
    "compose": {
      "name": "Supabase Compose source",
      "basis": "e693f206f5050b0004a86e12e533bb75ba2a9c76",
      "sources": {
        "s3f1258414a91": "https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml",
        "sa2c33e4a4845": "https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml#L68-L72",
        "s6c3ca4c63967": "https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml#L109-L111"
      }
    },
    "compose-env": {
      "name": "Supabase Compose source at environment commit",
      "basis": "eabe06be5b36cf57f2b158bd5093b396606bf801",
      "sources": {
        "saf9bb5a285e5": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L97-L106",
        "s17a0fbd83600": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L138-L177",
        "s960299690b0e": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L435-L472",
        "sd9608b0eac9b": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L532-L573",
        "s3eafc1cb4171": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L68-L72",
        "s083aa9fc8028": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L109-L111"
      }
    },
    "kong": {
      "name": "Supabase Kong configuration source",
      "basis": "eabe06be5b36cf57f2b158bd5093b396606bf801",
      "sources": {
        "s09329687c791": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L27-L33",
        "s4e5dfdd18d97": "https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L454-L467"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s5e1383feef7d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79",
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md",
        "s82a34ee18632": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md"
      }
    }
  },
  "claims": {
    "release": {"text": "Guide version basis self-hosted/v0.8.1 has Envoy v1.39.1 and Auth v2.196.0 at e693f206; environment defaults at eabe06be have different Compose images (Envoy v1.39.0, Auth v2.189.0). Compare installed releases and overrides.", "components": ["docs", "env", "compose", "compose-env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "compose:s3f1258414a91", "compose:sa2c33e4a4845", "compose:s6c3ca4c63967", "compose-env:s3eafc1cb4171", "compose-env:s083aa9fc8028"], "status": "REASONED"},
    "jwt-secrets": {"text": "Replace demo JWT_SECRET and derived ANON_KEY/SERVICE_ROLE_KEY together; the public signing secret permits forged roles even after merely replacing API keys.", "components": ["docs", "env"], "sources": ["docs:s399d0fbba196", "docs:s73d939b4644e", "env:sb8e42c6de990", "env:sed49ce6bde76"], "status": "REASONED"},
    "dashboard-secret": {"text": "Replace shipped supabase / this_password_is_insecure_and_should_be_updated dashboard credentials before first start.", "components": ["docs", "env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "env:sc520e7d9db9f"], "status": "REASONED"},
    "postgres-secret": {"text": "Replace your-super-secret-and-long-postgres-password; initialized databases require utils/db-passwd.sh and service recreation, not an env-only edit.", "components": ["docs", "env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "env:sed49ce6bde76"], "status": "REASONED"},
    "s3-secrets": {"text": "Replace both demo S3_PROTOCOL_ACCESS_KEY_ID and S3_PROTOCOL_ACCESS_KEY_SECRET.", "components": ["docs", "env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "env:sb600d65cc47b"], "status": "REASONED"},
    "encryption-secrets": {"text": "Replace four example encryption keys to the lengths and purposes stated in .env.example: SECRET_KEY_BASE at least 64 for Realtime and Supavisor communications; REALTIME_DB_ENC_KEY exactly 16 for Realtime fields; VAULT_ENC_KEY exactly 32 for Supavisor configuration; PG_META_CRYPTO_KEY at least 32 for Studio connection strings.", "components": ["docs", "env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "env:sb241a3887d73"], "status": "REASONED"},
    "key-generation": {"text": "Use generate-keys.sh and add-new-auth-keys.sh, including JWT_KEYS/JWT_JWKS where present, and protect the resulting env file outside source control.", "components": ["docs"], "sources": ["docs:s399d0fbba196"], "status": "REASONED"},
    "key-retirement": {"text": "Recreate affected services; remove old signing keys from every verifier. Opaque API-key rotation alone does not retire JWT signing keys or user sessions.", "components": ["docs"], "sources": ["docs:s399d0fbba196", "docs:s73d939b4644e"], "status": "REASONED"},
    "gateway-port": {"text": "Default Envoy gateway publishes HTTP 8000 on every interface and fronts API services plus Studio; bind host publication to loopback or firewall it.", "components": ["docs", "compose"], "sources": ["docs:s399d0fbba196", "compose:s3f1258414a91"], "status": "REASONED"},
    "pooler-ports": {"text": "Supavisor publishes 5432 and 6543 on every interface; unpublished db ports remain reachable from the Docker host. Isolate database access independently.", "components": ["compose"], "sources": ["compose:s3f1258414a91"], "status": "REASONED"},
    "kong-port": {"text": "Optional Kong additionally publishes HTTPS 8443; include that mapping in isolation checks.", "components": ["docs"], "sources": ["docs:s399d0fbba196"], "status": "REASONED"},
    "network-check": {"text": "Docker NAT can bypass UFW and lack matching host sockets; inspect effective mappings and test IPv4/IPv6 externally with a working allowed-vantage control.", "components": ["docs", "compose"], "sources": ["docs:s399d0fbba196", "compose:s3f1258414a91"], "status": "REASONED", "verify": [1]},
    "transport": {"text": "Default Envoy and Supavisor supply no TLS termination; HTTPS proxy protects the API, while PostgreSQL wire traffic needs its own TLS or encrypted tunnel.", "components": ["docs", "compose"], "sources": ["docs:s399d0fbba196", "compose:s3f1258414a91"], "status": "REASONED"},
    "egress": {"text": "Constrain Edge Function and Storage URL-fetching egress; inbound JWT verification does not restrict outbound requests.", "components": ["docs"], "sources": ["docs:s399d0fbba196"], "status": "REASONED"},
    "role-secret": {"text": "service_role bypasses RLS but remains subject to SQL privileges; keep service credentials server-side and never ship them to clients.", "components": ["docs"], "sources": ["docs:s73d939b4644e", "docs:s46cff2590323"], "status": "REASONED"},
    "anon-rls": {"text": "Public anon access requires SQL privileges and applicable RLS policies; enabled RLS without a policy returns no rows, missing grants error, and disabled RLS does not constrain granted operations.", "components": ["docs"], "sources": ["docs:s73d939b4644e", "docs:s46cff2590323"], "status": "REASONED"},
    "views": {"text": "Enable RLS on every exposed table and review owner-privileged views that can disclose rows beyond caller policies.", "components": ["docs"], "sources": ["docs:s46cff2590323"], "status": "REASONED"},
    "gateway-routes": {"text": "The environment commit passes dashboard credentials to default Envoy; optional Kong configuration applies those credentials as Basic auth to its catch-all Studio route. Other gateway routes have distinct policies.", "components": ["docs", "compose", "env", "compose-env", "kong"], "sources": ["docs:s399d0fbba196", "compose:s3f1258414a91", "env:sc520e7d9db9f", "compose-env:s3eafc1cb4171", "compose-env:saf9bb5a285e5", "kong:s09329687c791", "kong:s4e5dfdd18d97"], "status": "REASONED"},
    "functions": {"text": "At the environment commit, FUNCTIONS_VERIFY_JWT=false maps to VERIFY_JWT in the Edge Functions main service, with per-function configuration marked TODO; individual functions may authenticate.", "components": ["env", "compose", "compose-env"], "sources": ["env:sb8e42c6de990", "compose:s3f1258414a91", "env:s8d1a17b9f899", "compose-env:s960299690b0e"], "status": "REASONED"},
    "studio-port": {"text": "Studio listens internally on 3000 without host publication; never route around gateway dashboard authentication.", "components": ["compose"], "sources": ["compose:s3f1258414a91"], "status": "REASONED"},
    "signup": {"text": "At the environment commit, DISABLE_SIGNUP=false, ENABLE_PHONE_SIGNUP=true and ENABLE_PHONE_AUTOCONFIRM=true map to Auth settings; registration and phone auto-confirmation are enabled absent other controls.", "components": ["env", "compose", "compose-env"], "sources": ["env:sb8e42c6de990", "compose:s3f1258414a91", "env:s8f596f22364d", "compose-env:s083aa9fc8028", "compose-env:s17a0fbd83600"], "status": "REASONED"},
    "mfa": {"text": "Application-user TOTP needs assurance-level enforcement; it adds no factor to Studio Basic auth, which needs a private or MFA-enforcing administrative boundary.", "components": ["docs"], "sources": ["docs:s399d0fbba196", "docs:s46cff2590323"], "status": "REASONED"},
    "verify-isolation": {"text": "Any external HTTP/database response proves publication; refusal is vantage-specific and timeout inconclusive. Corroborate with mappings and a live allowed control.", "components": ["docs", "compose"], "sources": ["docs:s399d0fbba196", "compose:s3f1258414a91"], "status": "REASONED", "verify": [1]},
    "verify-function": {"text": "Known unauthenticated canary responds to both requests with JWT checking off; with it on, missing Bearer gets 401 and current legacy anon JWT returns the known response.", "components": ["env", "compose", "curl", "compose-env"], "sources": ["env:sb8e42c6de990", "compose:s3f1258414a91", "curl:s5e1383feef7d", "curl:s3db522258e44", "env:s8d1a17b9f899", "compose-env:s960299690b0e"], "status": "REASONED", "verify": [2]},
    "verify-api-keys": {"text": "Compare shipped and current API keys at /auth/v1/settings; current key must return settings JSON. This tests gateway acceptance, not signing-key retirement.", "components": ["docs", "curl"], "sources": ["docs:s399d0fbba196", "docs:s73d939b4644e", "curl:s3db522258e44"], "status": "REASONED"},
    "verify-signing": {"text": "Compare equivalent unexpired service_role JWTs signed by current versus demo secret against one REST canary, retaining a valid apikey; require JWT signature rejection.", "components": ["docs", "curl"], "sources": ["docs:s399d0fbba196", "docs:s73d939b4644e", "docs:s46cff2590323", "curl:s3db522258e44"], "status": "REASONED"},
    "verify-dashboard": {"text": "The optional Kong configuration uses the example dashboard Basic credentials; compare rejection of that pair with a working current credential on a known Studio response.", "components": ["docs", "env", "curl", "compose-env", "kong"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "curl:s82a34ee18632", "env:sc520e7d9db9f", "compose-env:s3eafc1cb4171", "compose-env:saf9bb5a285e5", "kong:s09329687c791", "kong:s4e5dfdd18d97"], "status": "REASONED"},
    "verify-database": {"text": "Check pooler 5432/6543 as postgres.your-tenant-id against postgres using SELECT current_user, current_database(); require demo-password authentication failure and a working control.", "components": ["docs", "env", "compose", "compose-env"], "sources": ["docs:s399d0fbba196", "env:sb8e42c6de990", "compose:s3f1258414a91", "env:sed49ce6bde76", "env:s7e03d1d4ecba", "compose-env:sd9608b0eac9b"], "status": "REASONED"}
  }
}
---
# Self-hosted Supabase

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- docs: Supabase documentation (unknown)
- env: Supabase environment source (eabe06be5b36cf57f2b158bd5093b396606bf801)
- compose: Supabase Compose source (e693f206f5050b0004a86e12e533bb75ba2a9c76)
- compose-env: Supabase Compose source at environment commit (eabe06be5b36cf57f2b158bd5093b396606bf801)
- kong: Supabase Kong configuration source (eabe06be5b36cf57f2b158bd5093b396606bf801)
- curl: curl (curl-8_14_1)

Claims (full source mapping in the front matter):

- release (REASONED; docs, env, compose, compose-env): Guide version basis self-hosted/v0.8.1 has Envoy v1.39.1 and Auth v2.196.0 at e693f206; environment defaults at eabe06be have different Compose images (Envoy v1.39.0, Auth v2.189.0). Compare installed releases and overrides.
- jwt-secrets (REASONED; docs, env): Replace demo JWT_SECRET and derived ANON_KEY/SERVICE_ROLE_KEY together; the public signing secret permits forged roles even after merely replacing API keys.
- dashboard-secret (REASONED; docs, env): Replace shipped supabase / this_password_is_insecure_and_should_be_updated dashboard credentials before first start.
- postgres-secret (REASONED; docs, env): Replace your-super-secret-and-long-postgres-password; initialized databases require utils/db-passwd.sh and service recreation, not an env-only edit.
- s3-secrets (REASONED; docs, env): Replace both demo S3_PROTOCOL_ACCESS_KEY_ID and S3_PROTOCOL_ACCESS_KEY_SECRET.
- encryption-secrets (REASONED; docs, env): Replace four example encryption keys to the lengths and purposes stated in .env.example: SECRET_KEY_BASE at least 64 for Realtime and Supavisor communications; REALTIME_DB_ENC_KEY exactly 16 for Realtime fields; VAULT_ENC_KEY exactly 32 for Supavisor configuration; PG_META_CRYPTO_KEY at least 32 for Studio connection strings.
- key-generation (REASONED; docs): Use generate-keys.sh and add-new-auth-keys.sh, including JWT_KEYS/JWT_JWKS where present, and protect the resulting env file outside source control.
- key-retirement (REASONED; docs): Recreate affected services; remove old signing keys from every verifier. Opaque API-key rotation alone does not retire JWT signing keys or user sessions.
- gateway-port (REASONED; docs, compose): Default Envoy gateway publishes HTTP 8000 on every interface and fronts API services plus Studio; bind host publication to loopback or firewall it.
- pooler-ports (REASONED; compose): Supavisor publishes 5432 and 6543 on every interface; unpublished db ports remain reachable from the Docker host. Isolate database access independently.
- kong-port (REASONED; docs): Optional Kong additionally publishes HTTPS 8443; include that mapping in isolation checks.
- network-check (REASONED; docs, compose): Docker NAT can bypass UFW and lack matching host sockets; inspect effective mappings and test IPv4/IPv6 externally with a working allowed-vantage control.
- transport (REASONED; docs, compose): Default Envoy and Supavisor supply no TLS termination; HTTPS proxy protects the API, while PostgreSQL wire traffic needs its own TLS or encrypted tunnel.
- egress (REASONED; docs): Constrain Edge Function and Storage URL-fetching egress; inbound JWT verification does not restrict outbound requests.
- role-secret (REASONED; docs): service_role bypasses RLS but remains subject to SQL privileges; keep service credentials server-side and never ship them to clients.
- anon-rls (REASONED; docs): Public anon access requires SQL privileges and applicable RLS policies; enabled RLS without a policy returns no rows, missing grants error, and disabled RLS does not constrain granted operations.
- views (REASONED; docs): Enable RLS on every exposed table and review owner-privileged views that can disclose rows beyond caller policies.
- gateway-routes (REASONED; docs, compose, env, compose-env, kong): The environment commit passes dashboard credentials to default Envoy; optional Kong configuration applies those credentials as Basic auth to its catch-all Studio route. Other gateway routes have distinct policies.
- functions (REASONED; env, compose, compose-env): At the environment commit, FUNCTIONS_VERIFY_JWT=false maps to VERIFY_JWT in the Edge Functions main service, with per-function configuration marked TODO; individual functions may authenticate.
- studio-port (REASONED; compose): Studio listens internally on 3000 without host publication; never route around gateway dashboard authentication.
- signup (REASONED; env, compose, compose-env): At the environment commit, DISABLE_SIGNUP=false, ENABLE_PHONE_SIGNUP=true and ENABLE_PHONE_AUTOCONFIRM=true map to Auth settings; registration and phone auto-confirmation are enabled absent other controls.
- mfa (REASONED; docs): Application-user TOTP needs assurance-level enforcement; it adds no factor to Studio Basic auth, which needs a private or MFA-enforcing administrative boundary.
- verify-isolation (REASONED; docs, compose): Any external HTTP/database response proves publication; refusal is vantage-specific and timeout inconclusive. Corroborate with mappings and a live allowed control.
- verify-function (REASONED; env, compose, curl, compose-env): Known unauthenticated canary responds to both requests with JWT checking off; with it on, missing Bearer gets 401 and current legacy anon JWT returns the known response.
- verify-api-keys (REASONED; docs, curl): Compare shipped and current API keys at /auth/v1/settings; current key must return settings JSON. This tests gateway acceptance, not signing-key retirement.
- verify-signing (REASONED; docs, curl): Compare equivalent unexpired service_role JWTs signed by current versus demo secret against one REST canary, retaining a valid apikey; require JWT signature rejection.
- verify-dashboard (REASONED; docs, env, curl, compose-env, kong): The optional Kong configuration uses the example dashboard Basic credentials; compare rejection of that pair with a working current credential on a known Studio response.
- verify-database (REASONED; docs, env, compose, compose-env): Check pooler 5432/6543 as postgres.your-tenant-id against postgres using SELECT current_user, current_database(); require demo-password authentication failure and a working control.
<!-- version-basis:end -->

The self-hosted Supabase Docker stack ships a `.env.example` full of demo secrets ([source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L30-L36)), and its own
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

At eabe06be5b36cf57f2b158bd5093b396606bf801, `.env.example` sets `POSTGRES_PASSWORD` to `your-super-secret-and-long-postgres-password` and `JWT_SECRET` to `your-super-secret-jwt-token-with-at-least-32-characters-long`. Its `ANON_KEY` and `SERVICE_ROLE_KEY` are HS256 JWTs; a local HMAC-SHA256 check verifies both against that `JWT_SECRET` (roles `anon` and `service_role`, issuer `supabase-demo`, issued 1641769200, expires 1799535600). [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L30-L36)
It sets `DASHBOARD_USERNAME=supabase` and `DASHBOARD_PASSWORD=this_password_is_insecure_and_should_be_updated`. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L57-L59) The `S3_PROTOCOL_ACCESS_KEY_ID` and `S3_PROTOCOL_ACCESS_KEY_SECRET` keys are published example values. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L84-L89)
The file comments require `SECRET_KEY_BASE` to be at least 64 characters for Realtime and Supavisor communications, `REALTIME_DB_ENC_KEY` to be exactly 16 for sensitive Realtime fields, `VAULT_ENC_KEY` to be exactly 32 for Supavisor configuration, and `PG_META_CRYPTO_KEY` to be at least 32 for Studio-to-postgres-meta connection strings. Replace all four example values with keys meeting those stated lengths. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L61-L75) Rotating the two API keys is not enough on its own: because the demo `JWT_SECRET` is public,
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

Three defaults need review. Compose passes `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD` to the default Envoy gateway. In the optional Kong configuration, those variables supply Basic auth for the Studio catch-all route. The shipped pair is `supabase` / `this_password_is_insecure_and_should_be_updated`; set a strong password in section 1 and keep the gateway off the public internet. The fetched files do not show Envoy's dashboard route configuration. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L57-L59) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L68-L72) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L97-L106) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L27-L33) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L454-L467) Gateway authentication is route-specific, not blanket: Kong's Studio catch-all route uses the dashboard
Basic-auth pair, REST/GraphQL/Realtime and the protected Auth routes require an API key, and some Auth routes
(verify, callback, JWKS, SAML metadata) are open by design; Storage and Edge Functions bypass the gateway's
API-key check and enforce their own controls. At eabe06be5b36cf57f2b158bd5093b396606bf801, `.env.example` sets `FUNCTIONS_VERIFY_JWT=false`; Compose passes it to `VERIFY_JWT` for the Edge Functions main service and says per-function configuration is pending. As `.env.example` notes, `VERIFY_JWT` applies to all functions; with this default, the main service's JWT verification is disabled, though an individual function may still authenticate. Inventory your functions and choose a verification policy. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L301-L305) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L435-L472) Studio also listens internally on `3000` with no host mapping of its own: never publish that
port or otherwise route around dashboard authentication. The example sets `DISABLE_SIGNUP=false`, `ENABLE_PHONE_SIGNUP=true`, and `ENABLE_PHONE_AUTOCONFIRM=true`; Compose maps these to Auth's `GOTRUE_DISABLE_SIGNUP`, `GOTRUE_EXTERNAL_PHONE_ENABLED`, and `GOTRUE_SMS_AUTOCONFIRM`. This configuration enables registration and phone auto-confirmation unless other controls intervene; rotating secrets does not change these settings. [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L174-L196) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L109-L111) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L138-L177) Set the registration
policy you actually want. Supabase Auth supports TOTP MFA for application users (enforce the required
assurance level in your policies per [firebase-supabase.md](firebase-supabase.md) and [mfa.md](mfa.md)); that
does not add a factor to the dashboard's Basic auth, so put administrative Studio access behind a private path
or an identity-aware proxy that enforces MFA.

## 5. Verify

REASONED: following block; listener/publication inventory and external versus allowed-vantage controls, per the guide's cited Supabase self-hosting with Docker and Supabase docker-compose.yml. No Supabase deployment or container runtime is available, and local listeners are denied. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics. No deployed listener was inspected: exposed ports answer externally; fixed ports are private and still work from an allowed vantage, corroborated by effective publication mappings. Credential outcomes described below also remain unobserved. Each probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so
none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result so
it discriminates against a live instance. These expectations follow the cited vendor documentation, including the check that forges
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
# REASONED: listener expectations follow the cited vendor documentation; no container runtime is available.
# On the host: these published listeners should be bound to loopback or an internal interface.
# Docker publishes through NAT, so also test each port from an external host over IPv4 and IPv6.
ss -tlnp   # read every listener; 8000/5432/6543: loopback or internal only
```

REASONED: preceding block; listener isolation and the canary function comparison, per the guide's cited Supabase docker-compose.yml and Supabase docker .env.example. No Supabase deployment or container runtime is available. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics; five rejected guard cases reached no curl stub, while substituted canary inputs produced two STUB curl lines. No live outcome was observed: fixed listeners are private, and the function's exposed state accepts both requests while JWT enforcement denies the credential-free request and admits the current-token control. The gateway serves plain HTTP on `8000`. Substitute the base URL, function name, and current legacy
`ANON_KEY` JWT inside the single quotes. Use a canary function with a known response and no independent
authentication. With `FUNCTIONS_VERIFY_JWT=false`, both requests should reach it; with verification
enabled, the credential-free request should receive `401` and the Bearer-authenticated request should
return its known response. An arbitrary function can return its own `401`, so that status alone does not
identify the main worker's policy.

REASONED: following block; the canary function comparison follows the cited environment and Compose sources; no container runtime was available for exposed/fixed service runs.

```bash
(                              # a subshell, so your own script arguments are untouched
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The anon JWT you substitute on the set -- line enters shell history; clear that history line afterward.
  # Stdin closes the argv channel only: it does not hide the JWT from set -x tracing, your own account
  # or root.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BASE_URL' 'REPLACE_WITH_A_FUNCTION_NAME' 'REPLACE_WITH_CURRENT_ANON_JWT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the base URL (https://your-proxy, or http://127.0.0.1:8000 for a private-origin check); not probing"; exit 2 ;; esac
  case "$2" in *REPLACE_WITH_*|*FUNCTION_NAME*|"") echo "substitute a function name; not probing"; exit 2 ;; esac
  case "$3" in *REPLACE_WITH_*|"") echo "substitute a current legacy anon JWT; not probing"; exit 2 ;; esac
  case "$3" in *[[:cntrl:]]*) echo "the anon JWT must be one line with no control characters; not probing"; exit 2 ;; esac
  # Compare the credential-free request with a current legacy anon JWT sent as Bearer.
  # Use a canary with a known response and no independent authentication.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nno-key http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/functions/v1/$2"
  printf 'Authorization: Bearer %s\n' "$3" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H @- -w '\nwith-key http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/functions/v1/$2"
)
```

REASONED: preceding block; function authentication and retirement of shipped API, signing, dashboard and database credentials, per the guide's cited Supabase self-hosting with Docker, Supabase docker .env.example, Supabase API keys and curl curl-8_14_1 headers from stdin. No Supabase deployment, container runtime or current credentials are available. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics; guarded canary inputs reached two curl stubs and rejected inputs reached none. On 2026-10-13 UTC a QA review ran the block, extracted to a file and unchanged except for placeholder substitution, against a recording curl stub: it exited 2 with no curl call for an anon JWT with an embedded newline, a carriage return and a tab, and for a placeholder, and exited 0 after two curl calls for a valid dummy JWT, which reached curl only on stdin; the block as it stood before its control-character guard passed an embedded newline to curl (two calls), and the stub received an injected second header line (`X-Injected: yes`) on its stdin. Synthetic JSON/base64url tokens parsed and demo/current fixture keys produced different HMACs; no service verification ran. Exposed services accept the old credentials or unsigned function request; fixed services reject them while current credentials return the stated positive controls. For a port you can still reach, check whether the shipped credentials were replaced, feeding every credential
through stdin rather than argv (`curl --config -` for Basic auth, `curl --header @-` for `apikey`/`Authorization`;
disable shell tracing). Stdin closes the argv channel only: it does not hide a credential typed into a command from shell history, or the credential from your own account's view of the process. Test each shipped API key against `/auth/v1/settings`, then repeat with a current key that must return
settings JSON. This checks gateway acceptance, not retirement of backend signing keys. Separately, test the
same harmless REST canary with two correctly formed, unexpired `service_role` JWTs carrying equivalent claims:
one signed with the current key and one with the demo `JWT_SECRET`. Keep a valid current `apikey` on both
requests. Require the current token to return the known canary result and the demo-signed token to receive a
PostgREST JWT signature-verification rejection; transport errors, gateway denials, and SQL permission failures
are inconclusive. This checks the REST verifier only; check other JWT-verifying services separately. For the optional Kong configuration, the Studio dashboard still accepts the example Basic credentials if the
gateway answers `supabase:this_password_is_insecure_and_should_be_updated` ([source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L57-L59); via `--config -`) with `http=200`
rather than `401`, retrieving a known Studio response as the positive control. The database still accepts the
demo password if `psql` connects to the Supavisor pooler on `5432`/`6543` with the demo `POSTGRES_PASSWORD` ([source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L30-L36)), as
user `postgres.your-tenant-id` (from the example `POOLER_TENANT_ID` passed to Supavisor) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L142-L145) [source](https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L532-L573) and database `postgres`, running
`SELECT current_user, current_database();` before the demo-password rejection counts; once regenerated that
connection fails authentication.

## Sources (checked September 2026)

The guide's `self-hosted/v0.8.1` version basis cites Compose at e693f206f5050b0004a86e12e533bb75ba2a9c76 (Envoy v1.39.1, Auth v2.196.0). The `.env.example` defaults, corresponding Compose wiring, and optional Kong configuration cited below come from eabe06be5b36cf57f2b158bd5093b396606bf801; its Compose file pins Envoy v1.39.0 and Auth v2.189.0. Compare your installed release and every Compose override before applying these defaults.

- Supabase self-hosting with Docker (Envoy gateway, secure your services, changing the database password): https://supabase.com/docs/guides/self-hosting/docker
- Supabase API keys (anon vs service_role, BYPASSRLS, keep secret): https://supabase.com/docs/guides/api/api-keys
- Supabase Row Level Security (a table without RLS is unprotected): https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase docker .env.example (default secrets, keys, FUNCTIONS_VERIFY_JWT, signup and S3 defaults): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example
- Supabase docker .env.example (keys; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L30-L36
- Supabase docker .env.example (dashboard; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L57-L59
- Supabase docker .env.example (crypto; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L61-L75
- Supabase docker .env.example (s3; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L84-L89
- Supabase docker .env.example (pool; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L142-L145
- Supabase docker .env.example (signup; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L174-L196
- Supabase docker .env.example (functions; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/.env.example#L301-L305
- Supabase docker-compose.yml (published ports for the gateway and pooler): https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml
- Supabase docker-compose.yml (dashboard; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L97-L106
- Supabase docker-compose.yml (auth; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L138-L177
- Supabase docker-compose.yml (functions; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L435-L472
- Supabase docker-compose.yml (pool; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L532-L573
- Supabase docker-compose.yml (versions old; e693f206f5050b0004a86e12e533bb75ba2a9c76): https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml#L68-L72
- Supabase docker-compose.yml (auth version old; e693f206f5050b0004a86e12e533bb75ba2a9c76): https://github.com/supabase/supabase/blob/e693f206f5050b0004a86e12e533bb75ba2a9c76/docker/docker-compose.yml#L109-L111
- Supabase docker-compose.yml (versions new; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L68-L72
- Supabase docker-compose.yml (auth version new; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/docker-compose.yml#L109-L111
- Supabase docker/volumes/api/kong.yml (credentials; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L27-L33
- Supabase docker/volumes/api/kong.yml (dashboard; eabe06be5b36cf57f2b158bd5093b396606bf801): https://github.com/supabase/supabase/blob/eabe06be5b36cf57f2b158bd5093b396606bf801/docker/volumes/api/kong.yml#L454-L467
- [curl curl-8_14_1 write-out fields and version requirements (checked October 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79).
- [curl curl-8_14_1 headers from stdin (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- [curl curl-8_14_1 configuration from stdin (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md).
