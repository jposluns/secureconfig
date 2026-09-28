---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "22f20b7abff79d98483b7cee3c739c75055642138fb5b1285c76ba06210d6de3",
  "components": {
    "strapi": {
      "name": "Strapi MFA announcement",
      "basis": "unknown",
      "sources": {
        "sb599a80b159b": "https://strapi.io/blog/strapi-admin-panel-mfa-2fa"
      }
    },
    "directus": {
      "name": "Directus documentation",
      "basis": "unknown",
      "sources": {
        "sf46f66d9d647": "https://directus.com/docs/configuration/general",
        "s95b4deed4c04": "https://directus.com/docs/guides/auth/access-control",
        "sdb5770dacce9": "https://directus.com/docs/configuration/security-limits",
        "sb8f67532c865": "https://directus.com/docs/guides/files/access",
        "sbbbbd61b0406": "https://directus.com/docs/guides/auth/creating-users",
        "s564309fa506c": "https://directus.com/docs/guides/auth/tokens-cookies",
        "sbd072a55a4d8": "https://directus.com/docs/guides/connect/errors"
      }
    },
    "directus-bind": {
      "name": "Directus listener source",
      "basis": "v12.4.1",
      "sources": {
        "se00954e49d12": "https://github.com/directus/directus/blob/v12.4.1/packages/env/src/constants/defaults.ts#L9-L10",
        "s48e8715d5555": "https://github.com/directus/directus/blob/v12.4.1/api/src/server.ts#L169-L182"
      }
    },
    "directus-start": {
      "name": "Directus quickstart",
      "basis": "12.0.2",
      "sources": {
        "s0c25f43df477": "https://directus.com/docs/getting-started/create-a-project"
      }
    },
    "hasura": {
      "name": "Hasura GraphQL Engine documentation",
      "basis": "unknown",
      "sources": {
        "scf6fdeea5567": "https://hasura.io/docs/2.0/deployment/securing-graphql-endpoint/",
        "s5a2b2f9a72fa": "https://hasura.io/docs/2.0/deployment/graphql-engine-flags/reference/",
        "sdd8563e06e4c": "https://hasura.io/docs/2.0/security/disable-graphql-introspection/",
        "se1d13e0328aa": "https://hasura.io/docs/2.0/getting-started/docker-simple/"
      }
    },
    "hasura-start": {
      "name": "Hasura quickstart image",
      "basis": "2.46.0",
      "sources": {
        "s8a898d4830a5": "https://raw.githubusercontent.com/hasura/graphql-engine/5fa3e0d2b617a4ae85f65491c5ff6c056cb612de/install-manifests/docker-compose/docker-compose.yaml"
      }
    },
    "hasura-status": {
      "name": "Hasura authentication-status minimum",
      "basis": "2.48.0",
      "sources": {
        "s236d307db2ed": "https://hasura.io/changelog/community-edition/v2.48.0"
      }
    },
    "postgrest": {
      "name": "PostgREST documentation",
      "basis": "unknown",
      "sources": {
        "sa30c7678f706": "https://postgrest.org/en/stable/references/configuration.html",
        "s212cf1cff4a4": "https://postgrest.org/en/stable/references/auth.html",
        "sf64f1c1843f0": "https://postgrest.org/en/stable/references/errors.html",
        "seeda43197f99": "https://postgrest.org/en/stable/references/api/openapi.html",
        "s94a52b2c0adb": "https://postgrest.org/en/stable/references/admin_server.html"
      }
    },
    "postgrest-bind": {
      "name": "PostgREST listener source",
      "basis": "v16.4",
      "sources": {
        "sf27352fc3094": "https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L556",
        "sb8d27dc6392b": "https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L386",
        "sb1cd23c9b7eb": "https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L357-L360"
      }
    },
    "apollo": {
      "name": "Apollo Server documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sda3bf614c4c1": "https://www.apollographql.com/docs/apollo-server/api/apollo-server#introspection"
      }
    },
    "strapi-rolling": {
      "name": "Strapi documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s14bc6df86824": "https://docs.strapi.io/cms/features/users-permissions",
        "se092a52da156": "https://docs.strapi.io/cms/api/rest",
        "s6e175ebd2b41": "https://docs.strapi.io/cms/quick-start",
        "s98b50551124e": "https://docs.strapi.io/cms/configurations/server",
        "sab01c70ba4b8": "https://docs.strapi.io/cms/configurations/admin-panel",
        "s6a8521b5356a": "https://docs.strapi.io/cms/features/users-permissions#security-configuration",
        "s614dabdcf18c": "https://docs.strapi.io/cms/configurations/middlewares",
        "se877faf6af5f": "https://docs.strapi.io/cms/features/media-library",
        "s138b6fa1d39d": "https://docs.strapi.io/cms/features/api-tokens",
        "s5525cacf37f3": "https://docs.strapi.io/cms/features/sso",
        "sd2464531df4e": "https://docs.strapi.io/cms/plugins/graphql"
      }
    }
  },
  "claims": {
    "strapi-bootstrap": {"text": "No default admin password: privately register the first administrator before exposing /admin or management routes.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s6e175ebd2b41", "strapi-rolling:sab01c70ba4b8"], "status": "REASONED"},
    "strapi-bind": {"text": "Documented localhost differs from generated HOST=0.0.0.0; use host loopback or Docker 127.0.0.1:1337:1337 without binding container loopback.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s98b50551124e"], "status": "REASONED"},
    "strapi-mfa": {"text": "Strapi admin has no native MFA; protect UI and backend management routes with MFA proxy or available SSO, closing local-login bypasses.", "components": ["strapi", "strapi-rolling"], "sources": ["strapi-rolling:s5525cacf37f3", "strapi:sb599a80b159b"], "status": "REASONED"},
    "strapi-public": {"text": "Content types are private by default; Public-role grants determine anonymous access and denied requests normally return 403.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s14bc6df86824", "strapi-rolling:se092a52da156"], "status": "REASONED", "verify": [1]},
    "strapi-files": {"text": "Local Media Library files use unauthenticated static serving despite private content types; use access-controlled storage for confidential files.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s614dabdcf18c", "strapi-rolling:se877faf6af5f"], "status": "REASONED"},
    "strapi-signup": {"text": "Disable unneeded POST /api/auth/local/register signups; the initial sign-up setting remains unconfirmed, and new users receive the configured Default role.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s14bc6df86824"], "status": "REASONED"},
    "strapi-tokens": {"text": "Review pre-generated Full access/Read-only Content API tokens, delete unused tokens and bound lifetimes; use Custom scopes when find/findOne is too broad.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s138b6fa1d39d"], "status": "REASONED"},
    "strapi-secrets": {"text": "Protect and rotate APP_KEYS, ADMIN_JWT_SECRET, API_TOKEN_SALT, TRANSFER_TOKEN_SALT, JWT_SECRET and configured ENCRYPTION_KEY; salts are not bearer tokens.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s98b50551124e", "strapi-rolling:sab01c70ba4b8", "strapi-rolling:s6a8521b5356a", "strapi-rolling:s138b6fa1d39d"], "status": "REASONED"},
    "strapi-graphql": {"text": "Optional /graphql shadowCRUD generates operations; disable unnecessary apolloServer.introspection and landingPage without replacing resolver authorization.", "components": ["apollo", "strapi-rolling"], "sources": ["strapi-rolling:sd2464531df4e", "apollo:sda3bf614c4c1"], "status": "REASONED"},
    "apollo-default": {"text": "Apollo introspection is enabled unless NODE_ENV=production.", "components": ["apollo"], "sources": ["apollo:sda3bf614c4c1"], "status": "REASONED"},
    "strapi-tls": {"text": "Front Strapi with TLS and authentication; the guide records no native TLS termination.", "components": ["strapi-rolling"], "sources": ["strapi-rolling:s98b50551124e"], "status": "REASONED"},
    "directus-bootstrap": {"text": "ADMIN_EMAIL/PASSWORD and optional ADMIN_TOKEN bootstrap admin access; 12.0.2 quickstart also allows browser onboarding, so claim the instance privately.", "components": ["directus", "directus-start"], "sources": ["directus:sf46f66d9d647", "directus-start:s0c25f43df477"], "status": "REASONED"},
    "directus-secret": {"text": "Set a unique protected SECRET; omission generates a random value that does not persist consistently across restarts or replicas.", "components": ["directus"], "sources": ["directus:sdb5770dacce9"], "status": "REASONED"},
    "directus-cookies": {"text": "SESSION_COOKIE_SECURE and REFRESH_TOKEN_COOKIE_SECURE default false; set both true behind HTTPS.", "components": ["directus"], "sources": ["directus:sdb5770dacce9"], "status": "REASONED"},
    "directus-token": {"text": "ADMIN_TOKEN is an unexpiring admin credential independent of interactive MFA; omit unless needed and prefer scoped machine credentials.", "components": ["directus"], "sources": ["directus:sf46f66d9d647", "directus:s564309fa506c"], "status": "REASONED"},
    "directus-mfa": {"text": "Require two-factor authentication for Directus administrator accounts.", "components": ["directus"], "sources": ["directus:s95b4deed4c04", "directus:sdb5770dacce9"], "status": "REASONED"},
    "directus-public": {"text": "Public permissions are off by default; audit actual collection and /assets grants, including separate upload/import/update/delete rights and storage bypasses.", "components": ["directus"], "sources": ["directus:s95b4deed4c04", "directus:sb8f67532c865"], "status": "REASONED", "verify": [1]},
    "verify-directus": {"text": "The paired private-collection request must return the known canary to its authorized identity and 403 with FORBIDDEN to the anonymous caller.", "components": ["directus"], "sources": ["directus:s95b4deed4c04", "directus:sbd072a55a4d8"], "status": "REASONED", "verify": [1]},
    "directus-import": {"text": "IMPORT_IP_DENY_LIST defaults to 0.0.0.0,169.254.169.254; this import-specific setting does not establish Flow or extension egress protection.", "components": ["directus"], "sources": ["directus:sdb5770dacce9"], "status": "REASONED"},
    "directus-signup": {"text": "Registration is disabled by default; empty 204 responses do not establish rejection or account creation.", "components": ["directus"], "sources": ["directus:sbbbbd61b0406"], "status": "REASONED"},
    "directus-introspection": {"text": "GRAPHQL_INTROSPECTION defaults true; disable unnecessary discovery and apply the same roles and policies as REST.", "components": ["directus"], "sources": ["directus:sdb5770dacce9"], "status": "REASONED"},
    "directus-bind": {"text": "At v12.4.1 HOST defaults 0.0.0.0 and PORT 8055; UNIX_SOCKET_PATH replaces both. Use private binding or loopback publication.", "components": ["directus-bind"], "sources": ["directus-bind:se00954e49d12", "directus-bind:s48e8715d5555"], "status": "REASONED"},
    "directus-studio": {"text": "Root redirects to /admin; SERVE_APP hides Studio without replacing API authorization. Terminate TLS in front.", "components": ["directus"], "sources": ["directus:sf46f66d9d647"], "status": "REASONED"},
    "hasura-admin": {"text": "An unset HASURA_GRAPHQL_ADMIN_SECRET permits full admin rights; keep the configured bearer secret server-side and use scoped JWT/webhook client auth.", "components": ["hasura"], "sources": ["hasura:scf6fdeea5567"], "status": "REASONED"},
    "hasura-bind": {"text": "HASURA_GRAPHQL_SERVER_HOST defaults * on 8080; bind privately and terminate TLS in front.", "components": ["hasura"], "sources": ["hasura:s5a2b2f9a72fa"], "status": "REASONED"},
    "hasura-console": {"text": "Binary console default is false, but 2.46.0 quickstart enables / and /console; disable console where unnecessary.", "components": ["hasura", "hasura-start"], "sources": ["hasura:s5a2b2f9a72fa", "hasura-start:s8a898d4830a5"], "status": "REASONED"},
    "hasura-dev": {"text": "Keep HASURA_GRAPHQL_DEV_MODE=false in production.", "components": ["hasura"], "sources": ["hasura:s5a2b2f9a72fa"], "status": "REASONED"},
    "hasura-agent": {"text": "Quickstart publishes data-connector 8081 and literal Postgres credentials; isolate the additional listener and replace credentials.", "components": ["hasura-start"], "sources": ["hasura-start:s8a898d4830a5"], "status": "REASONED"},
    "hasura-apis": {"text": "ENABLED_APIS defaults metadata, graphql, pgdump, config; narrow unused APIs and protect them with the admin secret.", "components": ["hasura"], "sources": ["hasura:s5a2b2f9a72fa"], "status": "REASONED"},
    "hasura-anon": {"text": "Leave UNAUTHORIZED_ROLE unset unless deliberately granting anonymous access.", "components": ["hasura"], "sources": ["hasura:s5a2b2f9a72fa"], "status": "REASONED"},
    "hasura-introspection": {"text": "Introspection is enabled by default; its documented per-role disabling control is self-hosted Enterprise, not assumed available in Community.", "components": ["hasura"], "sources": ["hasura:sdd8563e06e4c"], "status": "REASONED"},
    "postgrest-anon": {"text": "Unset db-anon-role refuses missing JWTs with 401 PGRST302; intended anonymous access needs a dedicated minimal NOLOGIN role.", "components": ["postgrest"], "sources": ["postgrest:sa30c7678f706", "postgrest:s212cf1cff4a4", "postgrest:sf64f1c1843f0"], "status": "REASONED", "verify": [1]},
    "postgrest-invalid": {"text": "Malformed/bad-signature JWTs return 401 PGRST301; expired or invalid-claims JWTs return 401 PGRST303 instead of anonymous fallback.", "components": ["postgrest"], "sources": ["postgrest:s212cf1cff4a4", "postgrest:sf64f1c1843f0"], "status": "REASONED", "verify": [1]},
    "postgrest-grants": {"text": "GRANT/REVOKE govern API access; PUBLIC function EXECUTE, DEFINER functions and owner-privileged views can widen it.", "components": ["postgrest"], "sources": ["postgrest:s212cf1cff4a4"], "status": "REASONED"},
    "postgrest-schema": {"text": "db-schemas defaults public; expose a deliberate API schema and note that root OpenAPI output follows the requesting role privileges.", "components": ["postgrest"], "sources": ["postgrest:sa30c7678f706", "postgrest:seeda43197f99"], "status": "REASONED"},
    "postgrest-secret": {"text": "Set random jwt-secret of at least 32 characters; a supplied token with no secret configured fails with 500 PGRST300.", "components": ["postgrest"], "sources": ["postgrest:sa30c7678f706", "postgrest:sf64f1c1843f0"], "status": "REASONED"},
    "postgrest-bind": {"text": "At v16.4 server-host defaults !4 on 3000; optional admin server inherits that host unless overridden. Isolate both and terminate TLS in front.", "components": ["postgrest", "postgrest-bind"], "sources": ["postgrest:sa30c7678f706", "postgrest-bind:sf27352fc3094", "postgrest-bind:sb8d27dc6392b", "postgrest-bind:sb1cd23c9b7eb", "postgrest:s94a52b2c0adb"], "status": "REASONED"},
    "egress": {"text": "Restrict webhook, Flow, trigger, remote-schema and database-function egress after DNS resolution and redirects; IMPORT_IP_DENY_LIST covers imports only.", "components": ["directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s14bc6df86824", "directus:sdb5770dacce9", "hasura:s5a2b2f9a72fa", "postgrest:s212cf1cff4a4"], "status": "REASONED"},
    "database-boundary": {"text": "Protect database credentials, use dedicated minimal database roles, private listeners and verified encrypted remote database transport.", "components": ["directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s98b50551124e", "directus:sf46f66d9d647", "hasura:s5a2b2f9a72fa", "postgrest:sa30c7678f706"], "status": "REASONED"},
    "human-machine-auth": {"text": "Use MFA at human administrative boundaries, with separately scoped, expiring and revocable machine credentials.", "components": ["strapi", "directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s5525cacf37f3", "strapi:sb599a80b159b", "directus:sdb5770dacce9", "hasura:scf6fdeea5567", "postgrest:s212cf1cff4a4"], "status": "REASONED"},
    "verify-canary": {"text": "Pair authorized canary retrieval with identical anonymous requests; empty/missing/unrelated responses and transport errors are inconclusive.", "components": ["directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:se092a52da156", "directus:s95b4deed4c04", "hasura:scf6fdeea5567", "postgrest:s212cf1cff4a4"], "status": "REASONED", "verify": [1]},
    "verify-hasura": {"text": "Hasura defaults to HTTP 200 even for auth errors; inspect admin-secret-required JSON. PRESERVE_401_ERRORS requires Community 2.48.0, beyond quickstart 2.46.0.", "components": ["hasura", "hasura-status", "hasura-start"], "sources": ["hasura:s5a2b2f9a72fa", "hasura-status:s236d307db2ed", "hasura-start:s8a898d4830a5"], "status": "REASONED", "verify": [1]},
    "verify-retirement": {"text": "Repeat the same successful canary with retired credentials; require authentication failure, not permission/proxy errors. Bootstrap ADMIN_TOKEN edits do not rotate existing users.", "components": ["directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s138b6fa1d39d", "directus:s564309fa506c", "directus:sbd072a55a4d8", "hasura:scf6fdeea5567", "postgrest:s212cf1cff4a4"], "status": "REASONED", "verify": [1]},
    "verify-password": {"text": "Fresh admin login must accept operator-controlled credentials and reject actual old/copied passwords; missing OTP or lockout does not prove retirement.", "components": ["directus", "strapi-rolling"], "sources": ["strapi-rolling:s6e175ebd2b41", "directus:sf46f66d9d647", "directus:sbd072a55a4d8"], "status": "REASONED"},
    "verify-console": {"text": "Enabled Hasura / and /console serve HTML; disabled engine returns JSON not-found. Proxy 404 or a failed positive control is inconclusive.", "components": ["hasura"], "sources": ["hasura:s5a2b2f9a72fa"], "status": "REASONED"},
    "verify-introspection": {"text": "Require an introspection-specific rejection while an ordinary permitted GraphQL query still succeeds.", "components": ["apollo", "directus", "hasura", "strapi-rolling"], "sources": ["strapi-rolling:sd2464531df4e", "apollo:sda3bf614c4c1", "directus:sdb5770dacce9", "hasura:sdd8563e06e4c"], "status": "REASONED"},
    "verify-other-controls": {"text": "Test writes, registration, private files, MFA and outbound fetches separately with authorized/unauthorized fixtures and persisted effects.", "components": ["directus", "hasura", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s14bc6df86824", "strapi-rolling:se877faf6af5f", "strapi-rolling:s138b6fa1d39d", "directus:s95b4deed4c04", "directus:sb8f67532c865", "directus:sbbbbd61b0406", "directus:sdb5770dacce9", "hasura:scf6fdeea5567", "postgrest:s212cf1cff4a4"], "status": "REASONED"},
    "verify-isolation": {"text": "Inventory host/container listeners and mappings; probe every direct IPv4/IPv6 origin with an allowed control. Any HTTP response proves reachability; failures alone do not prove isolation.", "components": ["directus-bind", "hasura", "postgrest-bind", "postgrest", "strapi-rolling"], "sources": ["strapi-rolling:s98b50551124e", "directus-bind:se00954e49d12", "directus-bind:s48e8715d5555", "hasura:s5a2b2f9a72fa", "postgrest-bind:sf27352fc3094", "postgrest-bind:sb8d27dc6392b", "postgrest-bind:sb1cd23c9b7eb", "postgrest:s94a52b2c0adb"], "status": "REASONED", "verify": [2]}
  }
}
---
# Instant API backends: Strapi, Directus, Hasura, and PostgREST

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| strapi-bootstrap: No default admin password: privately register the first administrator before exposing /admin or management routes. | Strapi documentation (rolling) unknown | REASONED |
| strapi-bind: Documented localhost differs from generated HOST=0.0.0.0; use host loopback or Docker 127.0.0.1:1337:1337 without binding container loopback. | Strapi documentation (rolling) unknown | REASONED |
| strapi-mfa: Strapi admin has no native MFA; protect UI and backend management routes with MFA proxy or available SSO, closing local-login bypasses. | Strapi MFA announcement unknown; Strapi documentation (rolling) unknown | REASONED |
| strapi-public: Content types are private by default; Public-role grants determine anonymous access and denied requests normally return 403. | Strapi documentation (rolling) unknown | REASONED |
| strapi-files: Local Media Library files use unauthenticated static serving despite private content types; use access-controlled storage for confidential files. | Strapi documentation (rolling) unknown | REASONED |
| strapi-signup: Disable unneeded POST /api/auth/local/register signups; the initial sign-up setting remains unconfirmed, and new users receive the configured Default role. | Strapi documentation (rolling) unknown | REASONED |
| strapi-tokens: Review pre-generated Full access/Read-only Content API tokens, delete unused tokens and bound lifetimes; use Custom scopes when find/findOne is too broad. | Strapi documentation (rolling) unknown | REASONED |
| strapi-secrets: Protect and rotate APP_KEYS, ADMIN_JWT_SECRET, API_TOKEN_SALT, TRANSFER_TOKEN_SALT, JWT_SECRET and configured ENCRYPTION_KEY; salts are not bearer tokens. | Strapi documentation (rolling) unknown | REASONED |
| strapi-graphql: Optional /graphql shadowCRUD generates operations; disable unnecessary apolloServer.introspection and landingPage without replacing resolver authorization. | Apollo Server documentation (rolling) unknown; Strapi documentation (rolling) unknown | REASONED |
| apollo-default: Apollo introspection is enabled unless NODE_ENV=production. | Apollo Server documentation (rolling) unknown | REASONED |
| strapi-tls: Front Strapi with TLS and authentication; the guide records no native TLS termination. | Strapi documentation (rolling) unknown | REASONED |
| directus-bootstrap: ADMIN_EMAIL/PASSWORD and optional ADMIN_TOKEN bootstrap admin access; 12.0.2 quickstart also allows browser onboarding, so claim the instance privately. | Directus documentation unknown; Directus quickstart 12.0.2 | REASONED |
| directus-secret: Set a unique protected SECRET; omission generates a random value that does not persist consistently across restarts or replicas. | Directus documentation unknown | REASONED |
| directus-cookies: SESSION_COOKIE_SECURE and REFRESH_TOKEN_COOKIE_SECURE default false; set both true behind HTTPS. | Directus documentation unknown | REASONED |
| directus-token: ADMIN_TOKEN is an unexpiring admin credential independent of interactive MFA; omit unless needed and prefer scoped machine credentials. | Directus documentation unknown | REASONED |
| directus-mfa: Require two-factor authentication for Directus administrator accounts. | Directus documentation unknown | REASONED |
| directus-public: Public permissions are off by default; audit actual collection and /assets grants, including separate upload/import/update/delete rights and storage bypasses. | Directus documentation unknown | REASONED |
| verify-directus: The paired private-collection request must return the known canary to its authorized identity and 403 with FORBIDDEN to the anonymous caller. | Directus documentation unknown | REASONED |
| directus-import: IMPORT_IP_DENY_LIST defaults to 0.0.0.0,169.254.169.254; this import-specific setting does not establish Flow or extension egress protection. | Directus documentation unknown | REASONED |
| directus-signup: Registration is disabled by default; empty 204 responses do not establish rejection or account creation. | Directus documentation unknown | REASONED |
| directus-introspection: GRAPHQL_INTROSPECTION defaults true; disable unnecessary discovery and apply the same roles and policies as REST. | Directus documentation unknown | REASONED |
| directus-bind: At v12.4.1 HOST defaults 0.0.0.0 and PORT 8055; UNIX_SOCKET_PATH replaces both. Use private binding or loopback publication. | Directus listener source v12.4.1 | REASONED |
| directus-studio: Root redirects to /admin; SERVE_APP hides Studio without replacing API authorization. Terminate TLS in front. | Directus documentation unknown | REASONED |
| hasura-admin: An unset HASURA_GRAPHQL_ADMIN_SECRET permits full admin rights; keep the configured bearer secret server-side and use scoped JWT/webhook client auth. | Hasura GraphQL Engine documentation unknown | REASONED |
| hasura-bind: HASURA_GRAPHQL_SERVER_HOST defaults * on 8080; bind privately and terminate TLS in front. | Hasura GraphQL Engine documentation unknown | REASONED |
| hasura-console: Binary console default is false, but 2.46.0 quickstart enables / and /console; disable console where unnecessary. | Hasura GraphQL Engine documentation unknown; Hasura quickstart image 2.46.0 | REASONED |
| hasura-dev: Keep HASURA_GRAPHQL_DEV_MODE=false in production. | Hasura GraphQL Engine documentation unknown | REASONED |
| hasura-agent: Quickstart publishes data-connector 8081 and literal Postgres credentials; isolate the additional listener and replace credentials. | Hasura quickstart image 2.46.0 | REASONED |
| hasura-apis: ENABLED_APIS defaults metadata, graphql, pgdump, config; narrow unused APIs and protect them with the admin secret. | Hasura GraphQL Engine documentation unknown | REASONED |
| hasura-anon: Leave UNAUTHORIZED_ROLE unset unless deliberately granting anonymous access. | Hasura GraphQL Engine documentation unknown | REASONED |
| hasura-introspection: Introspection is enabled by default; its documented per-role disabling control is self-hosted Enterprise, not assumed available in Community. | Hasura GraphQL Engine documentation unknown | REASONED |
| postgrest-anon: Unset db-anon-role refuses missing JWTs with 401 PGRST302; intended anonymous access needs a dedicated minimal NOLOGIN role. | PostgREST documentation unknown | REASONED |
| postgrest-invalid: Malformed/bad-signature JWTs return 401 PGRST301; expired or invalid-claims JWTs return 401 PGRST303 instead of anonymous fallback. | PostgREST documentation unknown | REASONED |
| postgrest-grants: GRANT/REVOKE govern API access; PUBLIC function EXECUTE, DEFINER functions and owner-privileged views can widen it. | PostgREST documentation unknown | REASONED |
| postgrest-schema: db-schemas defaults public; expose a deliberate API schema and note that root OpenAPI output follows the requesting role privileges. | PostgREST documentation unknown | REASONED |
| postgrest-secret: Set random jwt-secret of at least 32 characters; a supplied token with no secret configured fails with 500 PGRST300. | PostgREST documentation unknown | REASONED |
| postgrest-bind: At v16.4 server-host defaults !4 on 3000; optional admin server inherits that host unless overridden. Isolate both and terminate TLS in front. | PostgREST documentation unknown; PostgREST listener source v16.4 | REASONED |
| egress: Restrict webhook, Flow, trigger, remote-schema and database-function egress after DNS resolution and redirects; IMPORT_IP_DENY_LIST covers imports only. | Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| database-boundary: Protect database credentials, use dedicated minimal database roles, private listeners and verified encrypted remote database transport. | Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| human-machine-auth: Use MFA at human administrative boundaries, with separately scoped, expiring and revocable machine credentials. | Strapi MFA announcement unknown; Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-canary: Pair authorized canary retrieval with identical anonymous requests; empty/missing/unrelated responses and transport errors are inconclusive. | Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-hasura: Hasura defaults to HTTP 200 even for auth errors; inspect admin-secret-required JSON. PRESERVE_401_ERRORS requires Community 2.48.0, beyond quickstart 2.46.0. | Hasura GraphQL Engine documentation unknown; Hasura authentication-status minimum 2.48.0; Hasura quickstart image 2.46.0 | REASONED |
| verify-retirement: Repeat the same successful canary with retired credentials; require authentication failure, not permission/proxy errors. Bootstrap ADMIN_TOKEN edits do not rotate existing users. | Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-password: Fresh admin login must accept operator-controlled credentials and reject actual old/copied passwords; missing OTP or lockout does not prove retirement. | Directus documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-console: Enabled Hasura / and /console serve HTML; disabled engine returns JSON not-found. Proxy 404 or a failed positive control is inconclusive. | Hasura GraphQL Engine documentation unknown | REASONED |
| verify-introspection: Require an introspection-specific rejection while an ordinary permitted GraphQL query still succeeds. | Apollo Server documentation (rolling) unknown; Directus documentation unknown; Hasura GraphQL Engine documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-other-controls: Test writes, registration, private files, MFA and outbound fetches separately with authorized/unauthorized fixtures and persisted effects. | Directus documentation unknown; Hasura GraphQL Engine documentation unknown; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
| verify-isolation: Inventory host/container listeners and mappings; probe every direct IPv4/IPv6 origin with an allowed control. Any HTTP response proves reachability; failures alone do not prove isolation. | Directus listener source v12.4.1; Hasura GraphQL Engine documentation unknown; PostgREST listener source v16.4; PostgREST documentation unknown; Strapi documentation (rolling) unknown | REASONED |
<!-- version-basis:end -->

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
the same roles and policies as REST. Directus listens on `HOST`, default `0.0.0.0`, and port `8055` (defaults as
of v12.4.1; a `UNIX_SOCKET_PATH` naming a socket path replaces both) and serves the Data Studio (`/` redirects to
`/admin`); on a bare host set `HOST=127.0.0.1`, in Docker publish
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

Each probe below is REASONED, not demonstrated: the authoring environment has no container runtime, so none was
stood up in its exposed and fixed states. Each names its expected exposed and fixed result so it discriminates
when run against a live instance, based on the cited vendor documentation. Give each tool a harmless canary
record whose one field reads `secureconfig-canary`, use curl 7.75.0 or later, and run the paired block once per
applicable endpoint: it sends the same URL and body twice, first with a valid credential and then anonymously,
so the authorized control proves the origin is the service and the canary exists before an application denial
can count as protection. Use a fresh, trusted shell. Enter the authorized header at the block's hidden prompt
(`Authorization: Bearer ...` for Strapi, Directus and PostgREST, or `X-Hasura-Admin-Secret: ...` for Hasura);
press Enter at the negative-header prompt for the anonymous test. Both headers stay in unexported subshell
variables and reach curl on stdin, never in argv or pasted commands. Inherited values are discarded; the
variables are unset after use and the subshell contains early exits. This does not hide credentials from the
account owner or root. Treat an empty result, a missing route, an unrelated error, an HTML page, a TLS error, or a timeout as inconclusive,
never as the fixed state. Substitute your own host for the `example.com` placeholder.

| Tool | Path appended to the deployment's HTTPS origin | JSON body | Expected private-state negative |
|---|---|---|---|
| Strapi | `/api/secureconfig-probes?filters[marker][$eq]=secureconfig-canary&fields[0]=marker` | empty | permission denial, normally 403 |
| Directus | `/items/secureconfig_probe?filter[marker][_eq]=secureconfig-canary&fields=marker` | empty | 403 with `FORBIDDEN` |
| Hasura | `/v1/graphql` | `{"query":"query { secureconfig_probe(where: {marker: {_eq: \"secureconfig-canary\"}}) { marker } }"}` | admin-secret-required JSON error |
| PostgREST | `/secureconfig_probe?select=marker&marker=eq.secureconfig-canary` | empty | 401 with `PGRST302` when the anonymous role is unset |

REASONED: following block; paired canary, token and credential-retirement probes follow the cited vendor documentation; the authoring environment has no container runtime for exposed/fixed service fixtures.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n CMS_PROBE_HEADER CMS_NEGATIVE_HEADER &&
    unset -v CMS_PROBE_HEADER CMS_NEGATIVE_HEADER; } 2>/dev/null ||
    { echo 'cannot clear CMS header variables in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
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
  IFS= read -r -s -p 'Authorized header (input hidden): ' CMS_PROBE_HEADER ||
    { echo 'header input failed; not probing'; exit 2; }
  printf '\n'
  case "$CMS_PROBE_HEADER" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply a valid control header without control characters; not probing'; exit 2 ;;
  esac
  IFS= read -r -s -p 'Negative header (empty for anonymous, input hidden): ' CMS_NEGATIVE_HEADER ||
    { echo 'header input failed; not probing'; exit 2; }
  printf '\n'
  case "$CMS_NEGATIVE_HEADER" in
    *REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply a negative header without control characters, or leave it empty; not probing'; exit 2 ;;
  esac
  printf '%s\n' 'AUTHORIZED CONTROL (must return the canary):'
  if [ -z "$2" ]; then
    printf '%s\n' "$CMS_PROBE_HEADER" |
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        --header @- "$1" || exit 2
  else
    printf '%s\n' "$CMS_PROBE_HEADER" |
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -H 'Content-Type: application/json' --data-raw "$2" \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        --header @- "$1" || exit 2
  fi
  unset -v CMS_PROBE_HEADER
  printf '%s\n' 'NEGATIVE (anonymous when the negative-header prompt was empty):'
  if [ -z "$2" ]; then
    printf '%s\n' "${CMS_NEGATIVE_HEADER-}" |
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        --header @- "$1" || exit 2
  else
    printf '%s\n' "${CMS_NEGATIVE_HEADER-}" |
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -H 'Content-Type: application/json' --data-raw "$2" \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        --header @- "$1" || exit 2
  fi
  unset -v CMS_NEGATIVE_HEADER
  printf '%s\n' 'Requests done; compare both bodies. Exit 0 is not a security verdict.'
)
```

Read the body, not the bare status. The Strapi and Directus probes only cover the one collection you point them
at, since both deny by default; run them against the collections you actually opened and read the full grant
list in the tool (the Directus access policies, the Strapi role permission matrix). Hasura answers HTTP 200 even
for an authorization error by default (its `HASURA_GRAPHQL_PRESERVE_401_ERRORS` flag, Community Edition 2.48.0
and later, preserves authentication failures as HTTP 401 instead; the quickstart Compose ships 2.46.0), so the
fixed state is the admin-secret-required message in the JSON. For PostgREST, repeat the negative with an
invalid token by entering `Authorization: Bearer not-a-real-jwt` at the negative-header prompt and expect `PGRST301`,
which confirms a bad token is rejected rather than treated as anonymous; a missing or expired token gives
`PGRST302` or `PGRST303`.

A malformed token discriminates nothing about the real credentials, so also test the ones this deployment
actually uses. Repeat the paired request using the old credential after retirement: a deleted Strapi Content API token, a
Directus static token replaced or cleared on the existing user through the Data Studio or Users API, a Hasura
admin secret removed from the running configuration, or an otherwise valid, unexpired canary JWT signed with a
key the verifier no longer accepts. Changing Directus's bootstrap `ADMIN_TOKEN` environment variable alone is
not a rotation procedure for an existing user's token. Enter the old credential's header at the negative-header prompt,
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

REASONED: following block; direct-origin isolation probes follow the cited listener documentation and pins; the authoring environment has no container runtime for exposed/fixed service fixtures.

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

- Strapi Users and Permissions, public role and sign-up (rolling documentation, checked September 2026): https://docs.strapi.io/cms/features/users-permissions
- Strapi REST API, content types private by default (rolling documentation, checked September 2026): https://docs.strapi.io/cms/api/rest
- Strapi quick start, first administrator (rolling documentation, checked September 2026): https://docs.strapi.io/cms/quick-start
- Strapi server configuration, HOST, PORT and APP_KEYS (rolling documentation, checked September 2026): https://docs.strapi.io/cms/configurations/server
- Strapi admin-panel configuration, ADMIN_JWT_SECRET, API_TOKEN_SALT and TRANSFER_TOKEN_SALT (rolling documentation, checked September 2026): https://docs.strapi.io/cms/configurations/admin-panel
- Strapi Users and Permissions security configuration, `JWT_SECRET` (rolling documentation, checked September 2026): https://docs.strapi.io/cms/features/users-permissions#security-configuration
- Strapi middlewares, public static file serving via koa-static (rolling documentation, checked September 2026): https://docs.strapi.io/cms/configurations/middlewares
- Strapi Media Library, upload providers (rolling documentation, checked September 2026): https://docs.strapi.io/cms/features/media-library
- Directus configuration, first admin user (ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_TOKEN; PORT default 8055): https://directus.com/docs/configuration/general
- Directus `HOST` default `0.0.0.0` and `PORT` default 8055, and the branch that replaces them when `UNIX_SOCKET_PATH` names a socket path (pinned tag v12.4.1): https://github.com/directus/directus/blob/v12.4.1/packages/env/src/constants/defaults.ts#L9-L10 and https://github.com/directus/directus/blob/v12.4.1/api/src/server.ts#L169-L182
- Directus access control (public permissions off by default): https://directus.com/docs/guides/auth/access-control
- Hasura securing the GraphQL endpoint: https://hasura.io/docs/2.0/deployment/securing-graphql-endpoint/
- Hasura GraphQL Engine flags reference (SERVER_HOST, ENABLE_CONSOLE, ENABLED_APIS, DEV_MODE, UNAUTHORIZED_ROLE): https://hasura.io/docs/2.0/deployment/graphql-engine-flags/reference/
- PostgREST configuration reference (db-anon-role, db-schemas, server-host, jwt-secret): https://postgrest.org/en/stable/references/configuration.html
- PostgREST `server-host` default `!4` (L556), `server-port` default 3000 (L386), and `admin-server-host` falling back to `server-host` (L357-L360) (pinned tag v16.4): https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L556, https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L386 and https://github.com/PostgREST/postgrest/blob/v16.4/src/library/PostgREST/Config.hs#L357-L360
- PostgREST authentication and roles: https://postgrest.org/en/stable/references/auth.html
- PostgREST error codes (PGRST300 to PGRST303): https://postgrest.org/en/stable/references/errors.html
- PostgREST OpenAPI output at the root path: https://postgrest.org/en/stable/references/api/openapi.html
- PostgREST admin server (optional health/metrics listener): https://postgrest.org/en/stable/references/admin_server.html
- Strapi API tokens, pre-generated Full access and Read-only tokens, scopes and lifetime (rolling documentation, checked September 2026): https://docs.strapi.io/cms/features/api-tokens
- Strapi SSO, administrator single sign-on (rolling documentation, checked September 2026): https://docs.strapi.io/cms/features/sso
- Directus security and limits (`SECRET`, cookie flags, `IMPORT_IP_DENY_LIST`): https://directus.com/docs/configuration/security-limits
- Directus file access (asset permissions and storage bypass): https://directus.com/docs/guides/files/access
- Hasura disable GraphQL introspection (self-hosted Enterprise control): https://hasura.io/docs/2.0/security/disable-graphql-introspection/
- Hasura Community Edition 2.48.0 release notes (`HASURA_GRAPHQL_PRESERVE_401_ERRORS`): https://hasura.io/changelog/community-edition/v2.48.0
- Strapi GraphQL plugin (endpoint, shadowCRUD, apolloServer, landingPage) (rolling documentation, checked September 2026): https://docs.strapi.io/cms/plugins/graphql
- Apollo Server introspection default (rolling documentation, checked September 2026): https://www.apollographql.com/docs/apollo-server/api/apollo-server#introspection
- Strapi 5 administrator MFA options (vendor statement, September 2026): https://strapi.io/blog/strapi-admin-panel-mfa-2fa
- Directus quickstart (12.0.2 Compose and browser onboarding): https://directus.com/docs/getting-started/create-a-project
- Directus registration (disabled by default; empty 204 response): https://directus.com/docs/guides/auth/creating-users
- Directus static tokens (scope, persistence and management): https://directus.com/docs/guides/auth/tokens-cookies
- Directus error codes (authentication versus permission failures): https://directus.com/docs/guides/connect/errors
- Hasura v2 Docker quickstart (selects the stable Compose manifest): https://hasura.io/docs/2.0/getting-started/docker-simple/
- Hasura stable quickstart Compose (2.46.0 when checked): https://raw.githubusercontent.com/hasura/graphql-engine/5fa3e0d2b617a4ae85f65491c5ff6c056cb612de/install-manifests/docker-compose/docker-compose.yaml
