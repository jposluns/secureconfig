---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "f7b13148f4c7d9b913dcb765e37ff8d0a3a5f76e9be2ec44bb9f2ebb83641205",
  "components": {
    "docs": {
      "name": "PostgreSQL documentation",
      "basis": "unknown",
      "sources": {
        "s4feea1443725": "https://www.postgresql.org/docs/current/runtime-config-connection.html",
        "s8215c4f0b29d": "https://www.postgresql.org/docs/current/ssl-tcp.html",
        "s7a7f6fb3b9ef": "https://www.postgresql.org/docs/current/auth-password.html",
        "s6d49df9638da": "https://www.postgresql.org/docs/current/functions-admin.html",
        "sbb484e8233fe": "https://www.postgresql.org/docs/current/auth-pg-hba-conf.html",
        "sf8b93623c032": "https://www.postgresql.org/docs/current/app-psql.html",
        "s213c900cae6f": "https://www.postgresql.org/docs/current/auth-radius.html",
        "s74d80ffaaf96": "https://www.postgresql.org/docs/current/sql-createrole.html",
        "sc9e1e81c4eb9": "https://www.postgresql.org/docs/current/sql-alterrole.html",
        "sf897d9524ed3": "https://www.postgresql.org/docs/current/role-membership.html",
        "s6c7856c30ba2": "https://www.postgresql.org/docs/current/sql-alterdatabase.html",
        "s4ded00efc4e2": "https://www.postgresql.org/docs/current/sql-set-role.html",
        "s20f27b82b893": "https://www.postgresql.org/docs/current/ddl-priv.html",
        "s230b60e145cf": "https://www.postgresql.org/docs/current/sql-altertable.html",
        "sb2d96220e6f0": "https://www.postgresql.org/docs/current/sql-createschema.html",
        "s65aff299a5a6": "https://www.postgresql.org/docs/current/sql-grant.html",
        "s04e81888353f": "https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html",
        "sb6224f4ac866": "https://www.postgresql.org/docs/current/sql-revoke.html",
        "sdd8b8cfb0e56": "https://www.postgresql.org/docs/current/ddl-schemas.html",
        "s1844713022bf": "https://www.postgresql.org/docs/current/runtime-config-client.html",
        "sec39c317b06f": "https://www.postgresql.org/docs/current/sql-createfunction.html",
        "s0fe66d71aa10": "https://www.postgresql.org/docs/current/sql-alterfunction.html",
        "sb30fe96b6195": "https://www.postgresql.org/docs/current/libpq-ssl.html",
        "sd389a3478bc7": "https://www.postgresql.org/docs/current/libpq-connect.html",
        "sf1b3da55ebd5": "https://www.postgresql.org/docs/current/runtime-config-logging.html",
        "s8df2d48dbc2d": "https://www.postgresql.org/docs/current/sql-createextension.html",
        "s1b4e67e38127": "https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html",
        "s7bb6f68ef52e": "https://www.postgresql.org/docs/current/sql-createtable.html",
        "seed379369be7": "https://www.postgresql.org/docs/current/monitoring-stats.html",
        "s8754b96a6114": "https://www.postgresql.org/docs/current/catalog-pg-authid.html",
        "s3b6607ed7b1a": "https://www.postgresql.org/docs/current/view-pg-hba-file-rules.html",
        "s2ab6c4aebc59": "https://www.postgresql.org/docs/current/view-pg-file-settings.html",
        "s55cbaf1aa910": "https://www.postgresql.org/docs/current/app-postgres.html"
      }
    },
    "docker": {
      "name": "PostgreSQL image source",
      "basis": "d588a44673ea9d123c1acb1a6924de10a27fc315",
      "sources": {
        "sd5180dc544b5": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/Dockerfile#L183-L184",
        "s2e6f9a2e2499": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L105-L138",
        "s595428f208ab": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L268-L286",
        "sb9987ddb368d": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L235",
        "sea8869c4fd61": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L347-L355",
        "s651e63340b47": "https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L92"
      }
    },
    "init": {
      "name": "PostgreSQL initdb source",
      "basis": "REL_17_11",
      "sources": {
        "sd22c3409ddcd": "https://github.com/postgres/postgres/blob/REL_17_11/src/backend/libpq/pg_hba.conf.sample#L113-L117",
        "s311f8c9d4751": "https://github.com/postgres/postgres/blob/REL_17_11/src/bin/initdb/initdb.c#L2550-L2557",
        "s7d7180e2b81f": "https://github.com/postgres/postgres/blob/REL_17_11/src/bin/initdb/initdb.c#L3434-L3435"
      }
    },
    "pg12": {
      "name": "PostgreSQL TLS minimum",
      "basis": "12",
      "sources": {
        "s260cb0b13223": "https://www.postgresql.org/docs/12/release-12.html"
      }
    },
    "pg14": {
      "name": "PostgreSQL SCRAM default",
      "basis": "14",
      "sources": {
        "s624abdbb3a62": "https://www.postgresql.org/docs/14/release-14.html"
      }
    },
    "pg15": {
      "name": "PostgreSQL schema defaults",
      "basis": "15",
      "sources": {
        "s674004a0d3a8": "https://www.postgresql.org/docs/15/release-15.html"
      }
    },
    "pg16": {
      "name": "PostgreSQL membership and require_auth",
      "basis": "16",
      "sources": {
        "s03525343bc49": "https://www.postgresql.org/docs/16/role-membership.html",
        "s2bdad423cced": "https://www.postgresql.org/docs/16/release-16.html"
      }
    },
    "pg18": {
      "name": "PostgreSQL MD5 and logging changes",
      "basis": "18",
      "sources": {
        "se36ec635e2a4": "https://www.postgresql.org/docs/18/release-18.html"
      }
    },
    "audit": {
      "name": "pgAudit source",
      "basis": "dedd42ec3fe880bf581dd578c0df87ed4ad246cd",
      "sources": {
        "s1825bbe4f88c": "https://github.com/pgaudit/pgaudit/blob/dedd42ec3fe880bf581dd578c0df87ed4ad246cd/README.md"
      }
    }
  },
  "claims": {
    "bind": {"text": "Keep listen_addresses local; widening requires a restart and listener inspection.", "components": ["docs"], "sources": ["docs:s4feea1443725"], "status": "REASONED"},
    "server-tls": {"text": "Enable TLS with certificate/key files and a postgres-owned key at mode 600.", "components": ["docs"], "sources": ["docs:s8215c4f0b29d", "docs:s4feea1443725"], "status": "REASONED"},
    "tls-minimum": {"text": "ssl_min_protocol_version sets TLSv1.2; this setting requires PostgreSQL 12+.", "components": ["pg12", "docs"], "sources": ["pg12:s260cb0b13223", "docs:s4feea1443725"], "status": "REASONED"},
    "scram-default": {"text": "password_encryption is scram-sha-256 by default from PostgreSQL 14.", "components": ["pg14", "docs"], "sources": ["pg14:s624abdbb3a62", "docs:s7a7f6fb3b9ef"], "status": "REASONED"},
    "reload": {"text": "pg_reload_conf signals reload, not certificate acceptance; invalid TLS replacements can retain old settings; passphrase reload has extra requirements.", "components": ["docs"], "sources": ["docs:s8215c4f0b29d", "docs:s4feea1443725", "docs:s6d49df9638da"], "status": "REASONED"},
    "image-bind": {"text": "Pinned Debian/Alpine images for 14 through 19 initialize from listen_addresses='*'; restrict published ports.", "components": ["docker"], "sources": ["docker:sd5180dc544b5"], "status": "REASONED"},
    "image-init-auth": {"text": "Pinned initdb defaults to trust for sockets and loopback unless auth arguments override it; recorded tags cover 14.24 through 19 beta 4.", "components": ["init", "docker"], "sources": ["init:sd22c3409ddcd", "init:s311f8c9d4751", "init:s7d7180e2b81f", "docker:s2e6f9a2e2499"], "status": "REASONED"},
    "image-host-auth": {"text": "The entrypoint appends host all all all using POSTGRES_HOST_AUTH_METHOD, defaulting to password_encryption; earlier matching rules win.", "components": ["docker", "docs"], "sources": ["docker:s595428f208ab", "docs:sbb484e8233fe"], "status": "REASONED"},
    "image-password": {"text": "New-directory initialization requires POSTGRES_PASSWORD or its file unless host auth is trust; never select trust for reachable clients.", "components": ["docker"], "sources": ["docker:sb9987ddb368d", "docker:sea8869c4fd61", "docker:s651e63340b47"], "status": "REASONED"},
    "hba": {"text": "host permits plaintext and TLS; hostssl plus SCRAM restricts remote access. Local peer is separate; first-match HBA has no fallback after authentication failure.", "components": ["docs"], "sources": ["docs:sbb484e8233fe"], "status": "REASONED"},
    "hba-reload": {"text": "Unix HBA edits require reload; Windows applies edits to subsequent connections without that same requirement.", "components": ["docs"], "sources": ["docs:sbb484e8233fe"], "status": "REASONED"},
    "password-migration": {"text": "Changing encryption does not convert stored verifiers; use prompted psql password reset. An md5 rule can negotiate SCRAM.", "components": ["docs"], "sources": ["docs:s7a7f6fb3b9ef", "docs:sf8b93623c032"], "status": "REASONED"},
    "md5-deprecation": {"text": "PostgreSQL 18 deprecates MD5 password support.", "components": ["pg18"], "sources": ["pg18:se36ec635e2a4"], "status": "REASONED"},
    "clientcert": {"text": "PostgreSQL 12+ clientcert=verify-full adds CA-validated client identity to SCRAM, matching username/mapping, normally by Common Name.", "components": ["pg12", "docs"], "sources": ["pg12:s260cb0b13223", "docs:sbb484e8233fe"], "status": "REASONED"},
    "mfa": {"text": "Machine certificates do not establish human MFA; RADIUS is an alternative HBA method, not an added SCRAM factor or general interactive MFA flow.", "components": ["docs"], "sources": ["docs:s213c900cae6f", "docs:sbb484e8233fe"], "status": "REASONED"},
    "runtime": {"text": "Separate NOLOGIN owner/runtime roles; remove superuser, database/role creation, replication and RLS bypass from app; review inherited grants.", "components": ["docs"], "sources": ["docs:s74d80ffaaf96", "docs:sc9e1e81c4eb9", "docs:sf897d9524ed3"], "status": "REASONED"},
    "ownership": {"text": "NOLOGIN does not prevent membership access; keep app outside owner roles and transfer existing objects separately from database ownership.", "components": ["docs"], "sources": ["docs:s6c7856c30ba2", "docs:s4ded00efc4e2", "docs:s20f27b82b893", "docs:s230b60e145cf"], "status": "REASONED"},
    "grants": {"text": "Grant runtime schema, table and sequence access only inside its boundary; owner-specific default grants affect future objects, not existing ones.", "components": ["docs"], "sources": ["docs:sb2d96220e6f0", "docs:s65aff299a5a6", "docs:s04e81888353f"], "status": "REASONED"},
    "membership": {"text": "PostgreSQL 16+ membership INHERIT/SET options are distinct; role INHERIT defaults new memberships, and NOINHERIT does not prohibit SET ROLE.", "components": ["pg16"], "sources": ["pg16:s03525343bc49"], "status": "REASONED"},
    "admission": {"text": "PUBLIC receives CONNECT and TEMPORARY by default; restrict each database, preserving required operators. CONNECT revocation affects new sessions only.", "components": ["docs"], "sources": ["docs:s20f27b82b893", "docs:sbb484e8233fe"], "status": "REASONED"},
    "schema-create": {"text": "Revoke unwanted PUBLIC CREATE and optional TEMPORARY; direct grants, ownership and memberships can still confer access; preserve required USAGE.", "components": ["docs"], "sources": ["docs:sb6224f4ac866", "docs:sdd8b8cfb0e56"], "status": "REASONED"},
    "schema-default": {"text": "PostgreSQL 15 new databases remove PUBLIC CREATE on public and use pg_database_owner; upgrades/restores can preserve old rights; CONNECT is unchanged.", "components": ["pg15"], "sources": ["pg15:s674004a0d3a8"], "status": "REASONED"},
    "search-path": {"text": "Trust only owner-writable schemas; set app's login path with pg_temp last. Reconnect; SET ROLE does not apply login defaults and app can change its path.", "components": ["docs"], "sources": ["docs:sdd8b8cfb0e56", "docs:s1844713022bf", "docs:sc9e1e81c4eb9"], "status": "REASONED"},
    "definer": {"text": "SECURITY DEFINER functions need their own safe path and restricted EXECUTE; revoke global default PUBLIC EXECUTE for future owner-created functions.", "components": ["docs"], "sources": ["docs:sec39c317b06f", "docs:s0fe66d71aa10", "docs:s04e81888353f"], "status": "REASONED"},
    "client-tls": {"text": "libpq verify-full checks hostname and CA; require does not check hostname, even when a root CA makes it validate the chain.", "components": ["docs"], "sources": ["docs:sb30fe96b6195"], "status": "REASONED"},
    "gss": {"text": "Set gssencmode=disable when requiring TLS verification; working GSSAPI encryption otherwise can take precedence; other drivers need equivalent settings.", "components": ["docs"], "sources": ["docs:sd389a3478bc7"], "status": "REASONED"},
    "logging": {"text": "Collect connection/disconnection and DDL logs; logging_collector requires restart, log_file_mode is Unix-only, and broader statement logging risks sensitive values.", "components": ["docs"], "sources": ["docs:sf1b3da55ebd5"], "status": "REASONED"},
    "logging-version": {"text": "PostgreSQL 18 log_connections accepts a list; on retains receipt, authentication and authorization logging, not every new option.", "components": ["pg18", "docs"], "sources": ["pg18:se36ec635e2a4", "docs:sf1b3da55ebd5"], "status": "REASONED"},
    "pgaudit": {"text": "pgAudit 18.x targets PostgreSQL 18; match server major, preserve preloads, restart, create extension before pgaudit.log and reconnect; installation is not audit delivery.", "components": ["audit", "docs"], "sources": ["audit:s1825bbe4f88c", "docs:s8df2d48dbc2d", "docs:s1844713022bf"], "status": "REASONED"},
    "verify-password": {"text": "Wrong prompted password succeeds under trust but must fail under password authentication while the correct-password TLS control succeeds.", "components": ["docs"], "sources": ["docs:sbb484e8233fe", "docs:s7a7f6fb3b9ef", "docs:sf8b93623c032"], "status": "REASONED", "verify": [1]},
    "verify-scram": {"text": "libpq 16+ require_auth=scram-sha-256 rejects a non-SCRAM exchange; success proves negotiation, not removal of all md5 rules.", "components": ["pg16", "docs"], "sources": ["pg16:s2bdad423cced", "docs:sd389a3478bc7"], "status": "REASONED", "verify": [1]},
    "verify-plaintext": {"text": "Plaintext succeeds under a permitting host rule; fixed HBA refuses no-encryption access while the same TLS login succeeds.", "components": ["docs"], "sources": ["docs:sbb484e8233fe", "docs:sd389a3478bc7"], "status": "REASONED", "verify": [1]},
    "verify-identity": {"text": "A trusted wrong-host certificate can pass require but must fail verify-full; restore the matching certificate as the positive control.", "components": ["docs"], "sources": ["docs:sb30fe96b6195"], "status": "REASONED", "verify": [1]},
    "verify-clientcert": {"text": "Compare matching and mismatched trusted client identities: verify-ca accepts both, verify-full rejects the mismatch while correct identity/password succeeds.", "components": ["docs"], "sources": ["docs:sbb484e8233fe", "docs:sb30fe96b6195"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Inventory all 5432 listeners including IPv6; wildcard becomes intended addresses after restart, with a successful intended-interface TLS control.", "components": ["docs"], "sources": ["docs:s4feea1443725", "docs:s1b4e67e38127"], "status": "REASONED", "verify": [2]},
    "verify-ownership": {"text": "Real app login reads existing fixtures but cannot ALTER or SET ROLE owner; owner alteration succeeds as the matched control.", "components": ["docs"], "sources": ["docs:s20f27b82b893", "docs:s4ded00efc4e2", "docs:s04e81888353f"], "status": "REASONED"},
    "verify-admission": {"text": "PUBLIC CONNECT permits a nonmember; revocation must produce database permission denial while app connects, not an HBA/password error.", "components": ["docs"], "sources": ["docs:s20f27b82b893"], "status": "REASONED"},
    "verify-creation": {"text": "PUBLIC CREATE and TEMPORARY probes must change from success to privilege denial, retaining administrator and application positive controls.", "components": ["docs"], "sources": ["docs:sdd8b8cfb0e56", "docs:s20f27b82b893", "docs:s7bb6f68ef52e"], "status": "REASONED"},
    "verify-path": {"text": "Trusted/shadow fixtures independently test login and function-local paths; omitted pg_temp permits shadow relations and restoring it returns trusted.", "components": ["docs"], "sources": ["docs:s1844713022bf", "docs:sec39c317b06f"], "status": "REASONED"},
    "verify-execute": {"text": "With admission and schema lookup held constant, PUBLIC EXECUTE removal denies the nonmember while the application function call succeeds.", "components": ["docs"], "sources": ["docs:s65aff299a5a6"], "status": "REASONED"},
    "verify-logs": {"text": "Successful connection, disconnection and DDL produce correlated records only when enabled; SHOW and extension installation do not prove delivery.", "components": ["docs"], "sources": ["docs:sf1b3da55ebd5"], "status": "REASONED"},
    "verify-audit": {"text": "Compare none versus enabled audit classes in fresh app sessions; the same seeded read succeeds and only the enabled state produces its READ event.", "components": ["audit"], "sources": ["audit:s1825bbe4f88c"], "status": "REASONED"},
    "diagnostics": {"text": "pg_stat_ssl describes live sessions; verifier format, HBA/current-file views and superseded settings do not prove negotiated auth or accepted TLS reload.", "components": ["docs"], "sources": ["docs:seed379369be7", "docs:s8754b96a6114", "docs:s3b6607ed7b1a", "docs:s2ab6c4aebc59"], "status": "REASONED"},
    "local-guards": {"text": "Historical shell and argument checks exercised local guards only, without service contact.", "components": ["docs"], "sources": ["docs:sf8b93623c032", "docs:s1b4e67e38127"], "status": "DEMONSTRATED", "evidence": "Unsubstituted blocks exited locally, and 22 guard/argument cases passed using explicit local command spies without contacting a service."},
    "local-parsing": {"text": "Historical PostgreSQL 18.6 parsed 14 configuration values and rejected an invalid Boolean; no certificates, pgAudit, running HBA or SQL were exercised.", "components": ["docs"], "sources": ["docs:s55cbaf1aa910"], "status": "DEMONSTRATED", "evidence": "PostgreSQL 18.6 parsed and returned the 14 configuration values shown in the TLS, logging, and preload blocks using anonymous memory; an invalid Boolean control was rejected."},
    "verify-default-grants": {"text": "Owner-created future tables must be readable with default grants and denied without them while the existing-table control succeeds; recreate fixtures per state.", "components": ["docs"], "sources": ["docs:s04e81888353f"], "status": "REASONED"}
  }
}
---
# PostgreSQL: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| bind: Keep listen_addresses local; widening requires a restart and listener inspection. | PostgreSQL documentation unknown | REASONED |
| server-tls: Enable TLS with certificate/key files and a postgres-owned key at mode 600. | PostgreSQL documentation unknown | REASONED |
| tls-minimum: ssl_min_protocol_version sets TLSv1.2; this setting requires PostgreSQL 12+. | PostgreSQL TLS minimum 12; PostgreSQL documentation unknown | REASONED |
| scram-default: password_encryption is scram-sha-256 by default from PostgreSQL 14. | PostgreSQL SCRAM default 14; PostgreSQL documentation unknown | REASONED |
| reload: pg_reload_conf signals reload, not certificate acceptance; invalid TLS replacements can retain old settings; passphrase reload has extra requirements. | PostgreSQL documentation unknown | REASONED |
| image-bind: Pinned Debian/Alpine images for 14 through 19 initialize from listen_addresses='*'; restrict published ports. | PostgreSQL image source d588a44673ea9d123c1acb1a6924de10a27fc315 | REASONED |
| image-init-auth: Pinned initdb defaults to trust for sockets and loopback unless auth arguments override it; recorded tags cover 14.24 through 19 beta 4. | PostgreSQL initdb source REL_17_11; PostgreSQL image source d588a44673ea9d123c1acb1a6924de10a27fc315 | REASONED |
| image-host-auth: The entrypoint appends host all all all using POSTGRES_HOST_AUTH_METHOD, defaulting to password_encryption; earlier matching rules win. | PostgreSQL image source d588a44673ea9d123c1acb1a6924de10a27fc315; PostgreSQL documentation unknown | REASONED |
| image-password: New-directory initialization requires POSTGRES_PASSWORD or its file unless host auth is trust; never select trust for reachable clients. | PostgreSQL image source d588a44673ea9d123c1acb1a6924de10a27fc315 | REASONED |
| hba: host permits plaintext and TLS; hostssl plus SCRAM restricts remote access. Local peer is separate; first-match HBA has no fallback after authentication failure. | PostgreSQL documentation unknown | REASONED |
| hba-reload: Unix HBA edits require reload; Windows applies edits to subsequent connections without that same requirement. | PostgreSQL documentation unknown | REASONED |
| password-migration: Changing encryption does not convert stored verifiers; use prompted psql password reset. An md5 rule can negotiate SCRAM. | PostgreSQL documentation unknown | REASONED |
| md5-deprecation: PostgreSQL 18 deprecates MD5 password support. | PostgreSQL MD5 and logging changes 18 | REASONED |
| clientcert: PostgreSQL 12+ clientcert=verify-full adds CA-validated client identity to SCRAM, matching username/mapping, normally by Common Name. | PostgreSQL TLS minimum 12; PostgreSQL documentation unknown | REASONED |
| mfa: Machine certificates do not establish human MFA; RADIUS is an alternative HBA method, not an added SCRAM factor or general interactive MFA flow. | PostgreSQL documentation unknown | REASONED |
| runtime: Separate NOLOGIN owner/runtime roles; remove superuser, database/role creation, replication and RLS bypass from app; review inherited grants. | PostgreSQL documentation unknown | REASONED |
| ownership: NOLOGIN does not prevent membership access; keep app outside owner roles and transfer existing objects separately from database ownership. | PostgreSQL documentation unknown | REASONED |
| grants: Grant runtime schema, table and sequence access only inside its boundary; owner-specific default grants affect future objects, not existing ones. | PostgreSQL documentation unknown | REASONED |
| membership: PostgreSQL 16+ membership INHERIT/SET options are distinct; role INHERIT defaults new memberships, and NOINHERIT does not prohibit SET ROLE. | PostgreSQL membership and require_auth 16 | REASONED |
| admission: PUBLIC receives CONNECT and TEMPORARY by default; restrict each database, preserving required operators. CONNECT revocation affects new sessions only. | PostgreSQL documentation unknown | REASONED |
| schema-create: Revoke unwanted PUBLIC CREATE and optional TEMPORARY; direct grants, ownership and memberships can still confer access; preserve required USAGE. | PostgreSQL documentation unknown | REASONED |
| schema-default: PostgreSQL 15 new databases remove PUBLIC CREATE on public and use pg_database_owner; upgrades/restores can preserve old rights; CONNECT is unchanged. | PostgreSQL schema defaults 15 | REASONED |
| search-path: Trust only owner-writable schemas; set app's login path with pg_temp last. Reconnect; SET ROLE does not apply login defaults and app can change its path. | PostgreSQL documentation unknown | REASONED |
| definer: SECURITY DEFINER functions need their own safe path and restricted EXECUTE; revoke global default PUBLIC EXECUTE for future owner-created functions. | PostgreSQL documentation unknown | REASONED |
| client-tls: libpq verify-full checks hostname and CA; require does not check hostname, even when a root CA makes it validate the chain. | PostgreSQL documentation unknown | REASONED |
| gss: Set gssencmode=disable when requiring TLS verification; working GSSAPI encryption otherwise can take precedence; other drivers need equivalent settings. | PostgreSQL documentation unknown | REASONED |
| logging: Collect connection/disconnection and DDL logs; logging_collector requires restart, log_file_mode is Unix-only, and broader statement logging risks sensitive values. | PostgreSQL documentation unknown | REASONED |
| logging-version: PostgreSQL 18 log_connections accepts a list; on retains receipt, authentication and authorization logging, not every new option. | PostgreSQL MD5 and logging changes 18; PostgreSQL documentation unknown | REASONED |
| pgaudit: pgAudit 18.x targets PostgreSQL 18; match server major, preserve preloads, restart, create extension before pgaudit.log and reconnect; installation is not audit delivery. | pgAudit source dedd42ec3fe880bf581dd578c0df87ed4ad246cd; PostgreSQL documentation unknown | REASONED |
| verify-password: Wrong prompted password succeeds under trust but must fail under password authentication while the correct-password TLS control succeeds. | PostgreSQL documentation unknown | REASONED |
| verify-scram: libpq 16+ require_auth=scram-sha-256 rejects a non-SCRAM exchange; success proves negotiation, not removal of all md5 rules. | PostgreSQL membership and require_auth 16; PostgreSQL documentation unknown | REASONED |
| verify-plaintext: Plaintext succeeds under a permitting host rule; fixed HBA refuses no-encryption access while the same TLS login succeeds. | PostgreSQL documentation unknown | REASONED |
| verify-identity: A trusted wrong-host certificate can pass require but must fail verify-full; restore the matching certificate as the positive control. | PostgreSQL documentation unknown | REASONED |
| verify-clientcert: Compare matching and mismatched trusted client identities: verify-ca accepts both, verify-full rejects the mismatch while correct identity/password succeeds. | PostgreSQL documentation unknown | REASONED |
| verify-listeners: Inventory all 5432 listeners including IPv6; wildcard becomes intended addresses after restart, with a successful intended-interface TLS control. | PostgreSQL documentation unknown | REASONED |
| verify-ownership: Real app login reads existing fixtures but cannot ALTER or SET ROLE owner; owner alteration succeeds as the matched control. | PostgreSQL documentation unknown | REASONED |
| verify-admission: PUBLIC CONNECT permits a nonmember; revocation must produce database permission denial while app connects, not an HBA/password error. | PostgreSQL documentation unknown | REASONED |
| verify-creation: PUBLIC CREATE and TEMPORARY probes must change from success to privilege denial, retaining administrator and application positive controls. | PostgreSQL documentation unknown | REASONED |
| verify-path: Trusted/shadow fixtures independently test login and function-local paths; omitted pg_temp permits shadow relations and restoring it returns trusted. | PostgreSQL documentation unknown | REASONED |
| verify-execute: With admission and schema lookup held constant, PUBLIC EXECUTE removal denies the nonmember while the application function call succeeds. | PostgreSQL documentation unknown | REASONED |
| verify-logs: Successful connection, disconnection and DDL produce correlated records only when enabled; SHOW and extension installation do not prove delivery. | PostgreSQL documentation unknown | REASONED |
| verify-audit: Compare none versus enabled audit classes in fresh app sessions; the same seeded read succeeds and only the enabled state produces its READ event. | pgAudit source dedd42ec3fe880bf581dd578c0df87ed4ad246cd | REASONED |
| diagnostics: pg_stat_ssl describes live sessions; verifier format, HBA/current-file views and superseded settings do not prove negotiated auth or accepted TLS reload. | PostgreSQL documentation unknown | REASONED |
| local-guards: Historical shell and argument checks exercised local guards only, without service contact. | PostgreSQL documentation unknown | DEMONSTRATED |
| local-parsing: Historical PostgreSQL 18.6 parsed 14 configuration values and rejected an invalid Boolean; no certificates, pgAudit, running HBA or SQL were exercised. | PostgreSQL documentation unknown | DEMONSTRATED |
| verify-default-grants: Owner-created future tables must be readable with default grants and denied without them while the existing-table control succeeds; recreate fixtures per state. | PostgreSQL documentation unknown | REASONED |
<!-- version-basis:end -->

Default posture: PostgreSQL should not listen on public interfaces at all. Widen `listen_addresses` only for genuine remote clients, and then require both TLS and SCRAM authentication as below.

## 1. Server TLS

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), give the key to the `postgres` user with mode `600`, then in `postgresql.conf`:

```ini
listen_addresses = 'localhost'            # widen deliberately, e.g. 'localhost,10.0.0.5'
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_min_protocol_version = 'TLSv1.2'       # PostgreSQL 12 and later
password_encryption = 'scram-sha-256'      # default from PostgreSQL 14
```

For the TLS settings shown and `password_encryption`, reload the configuration from an administrative connection:

```sql
SELECT pg_reload_conf();
```

A true result means the reload signal was sent; it does not establish that replacement certificate files were accepted. Invalid TLS files during reload can leave the previous TLS configuration active. Inspect the server logs and reconnect. Passphrase-protected keys have additional reload requirements involving `ssl_passphrase_command_supports_reload`; do not assume every `ssl*` setting behaves identically. See [server TLS file handling](https://www.postgresql.org/docs/current/ssl-tcp.html) and [TLS configuration](https://www.postgresql.org/docs/current/runtime-config-connection.html).

Changing `listen_addresses` requires a server restart through the deployment's service manager. Confirm the resulting listeners with the guarded `ss` check under Verify. The historical version boundaries above are documented in the [PostgreSQL 12](https://www.postgresql.org/docs/12/release-12.html) and [PostgreSQL 14](https://www.postgresql.org/docs/14/release-14.html) release notes.

The official Docker images (PostgreSQL 14 through 19, Debian and Alpine, at the pinned commit) start wider. Their build sets `listen_addresses = '*'` in the sample configuration that a new data directory is initialized from. When the entrypoint initializes a new data directory, it runs initdb with no authentication method beyond what `POSTGRES_INITDB_ARGS` supplies, so initdb's default, `trust` in every release checked (14.24, 15.19, 16.15, 17.11, 18.6 and 19 beta 4), applies to the local-socket rule unless those arguments pass `--auth-local` or `--auth` (`-A`), and to the loopback (`127.0.0.1/32`, `::1/128`) rules unless they pass `--auth-host` or `--auth` (`-A`); it then appends `host all all all` with `POSTGRES_HOST_AUTH_METHOD`, which defaults to the server's `password_encryption` setting. `pg_hba.conf` uses the first rule that matches, so with initdb's default, loopback connections inside the container's network namespace need no password (with `--network host`, or in a Kubernetes pod, that namespace is shared), and other addresses get the `POSTGRES_HOST_AUTH_METHOD` method, a password method by default. The entrypoint refuses to initialize without `POSTGRES_PASSWORD` (or `POSTGRES_PASSWORD_FILE`) unless `POSTGRES_HOST_AUTH_METHOD=trust`, and `trust` lets every address that reaches the port connect without a password. Publish the port only to host loopback or a private network, give `POSTGRES_INITDB_ARGS` an `--auth-host` and `--auth-local` method if loopback should need a password too, and never set `POSTGRES_HOST_AUTH_METHOD=trust`.

## 2. Require TLS per connection in pg_hba.conf

`host` matches both TLS and non-TLS TCP connections; it does not require encryption. `hostssl` matches only TLS. Use `hostssl` with `scram-sha-256` for the intended remote application connections:

```conf
# TYPE     DATABASE  USER  ADDRESS        METHOD
local      all       all                  peer
hostssl    app       app   10.0.0.0/24     scram-sha-256
# Do not leave broader matching host, trust or password rules elsewhere.
```

Inspect the complete rule order, including included files. PostgreSQL uses the first matching record, with no fall-through after authentication failure. On this guide's Unix-style deployment, reload after editing `pg_hba.conf`; Windows applies HBA edits to subsequent new connections without the same reload requirement. See the [HBA reference](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html).

Changing `password_encryption` does not convert existing password verifiers. In an administrative psql session using `scram-sha-256`, reset the application's password with `\password app`, which prompts without embedding the password in SQL or command-line arguments. PostgreSQL 18 deprecates MD5 password support. An HBA entry named `md5` can still negotiate SCRAM when the stored verifier is SCRAM; checking the negotiated method does not prove that every `md5` entry was removed. See [password authentication](https://www.postgresql.org/docs/current/auth-password.html), [psql password changes](https://www.postgresql.org/docs/current/app-psql.html) and the [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html).

For machine-to-machine links, add client certificate verification on top of SCRAM: configure `ssl_ca_file` with the CA that signs the client certificates, then append `clientcert=verify-full` to the applicable `hostssl` line. This option is available from PostgreSQL 12. It checks the certificate identity against the requested database username or a configured mapping. By default, that identity is the certificate Common Name, not the client's DNS hostname. Provision certificates accordingly. See [client certificate HBA options](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html).

MFA: a client certificate adds a possession factor held by the connecting machine, but does not by itself establish MFA for a person. `radius` is an alternative HBA authentication method, not a second method appended to SCRAM. PostgreSQL documents username/password validation with Access Accept or Access Reject, not a general interactive MFA conversation. Use an external MFA integration only with documentation and a test for its compatible flow. Put human access to SSH and administrative UIs behind MFA per [mfa.md](mfa.md). See [RADIUS authentication](https://www.postgresql.org/docs/current/auth-radius.html).

## 3. Separate runtime privileges from object ownership

A compromised application account should not be able to administer other roles, create databases, bypass row policies, or alter the objects it uses. Keep ownership in a separate `NOLOGIN` role and grant runtime privileges through another group role.

Run the following as an administrator authorized for these operations. This example assumes database `app` and login `app` already exist; `app_owner`, `app_runtime`, and schema `app_data` are new.

```sql
CREATE ROLE app_owner NOLOGIN;
CREATE ROLE app_runtime NOLOGIN;

ALTER ROLE app LOGIN INHERIT
  NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS;

GRANT app_runtime TO app;
ALTER DATABASE app OWNER TO app_owner;
```

`NOLOGIN` prevents direct login, not access through membership. Do not grant `app_owner` or another privileged role to `app`, directly or indirectly. Changing role attributes does not remove existing memberships or unrelated grants; review those separately. See [CREATE ROLE](https://www.postgresql.org/docs/current/sql-createrole.html), [ALTER ROLE](https://www.postgresql.org/docs/current/sql-alterrole.html), [role membership](https://www.postgresql.org/docs/current/role-membership.html) and [ALTER DATABASE](https://www.postgresql.org/docs/current/sql-alterdatabase.html).

While connected administratively to database `app`:

```sql
CREATE SCHEMA app_data AUTHORIZATION app_owner;
GRANT USAGE ON SCHEMA app_data TO app_runtime;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA app_data TO app_runtime;
GRANT USAGE
  ON ALL SEQUENCES IN SCHEMA app_data TO app_runtime;

ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app_data
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner IN SCHEMA app_data
  GRANT USAGE ON SEQUENCES TO app_runtime;
```

Use schema-wide grants only when every affected object belongs to the application's access boundary. Otherwise, grant privileges on named objects. Default privileges affect future objects created by `app_owner` in this database, not existing objects or objects created under another role. See [CREATE SCHEMA](https://www.postgresql.org/docs/current/sql-createschema.html), [GRANT](https://www.postgresql.org/docs/current/sql-grant.html) and [ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).

Run migrations from a separate authorized administrative connection that can select the owner role:

```sql
SET ROLE app_owner;
-- Run migrations here, using schema-qualified object names.
RESET ROLE;
```

For an existing application table, transfer ownership explicitly, substituting its actual qualified name:

```sql
ALTER TABLE app_data.records OWNER TO app_owner;
```

Changing database ownership does not transfer ownership of its tables. Inventory and transfer existing objects individually. Ownership includes powers that ordinary privilege revocation cannot remove. See [SET ROLE](https://www.postgresql.org/docs/current/sql-set-role.html), [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) and [object ownership](https://www.postgresql.org/docs/current/ddl-priv.html).

These are core controls. PostgreSQL 16+ has per-membership `INHERIT` and `SET` options. The role-level `INHERIT` attribute supplies the default for the new membership granted above; it does not repair an existing membership's options. Role-level `NOINHERIT` must not be treated as preventing `SET ROLE`. See [PostgreSQL 16 role membership](https://www.postgresql.org/docs/16/role-membership.html).

## 4. Restrict database admission and schema creation

PostgreSQL grants database `CONNECT` and `TEMPORARY` to `PUBLIC` by default. Restrict admission explicitly. Before committing, also preserve access for the administrative, monitoring, backup, and migration roles the deployment requires.

```sql
BEGIN;
REVOKE CONNECT ON DATABASE app FROM PUBLIC;
GRANT CONNECT ON DATABASE app TO app_runtime;
COMMIT;
```

Repeat for each database requiring restricted admission. `CONNECT` is checked when a connection starts; revocation does not disconnect existing sessions. Both HBA authentication and database privileges must permit a new connection. See [database privileges](https://www.postgresql.org/docs/current/ddl-priv.html) and [HBA database access](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html).

While connected administratively to `app`, remove public schema creation rights:

```sql
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

If the application does not need temporary tables:

```sql
REVOKE TEMPORARY ON DATABASE app FROM PUBLIC;
```

Revocation from `PUBLIC` does not remove privileges granted directly to a role or obtained through another membership. Do not revoke `USAGE` on `public` indiscriminately if applications need objects installed there. See [schema privileges](https://www.postgresql.org/docs/current/ddl-schemas.html) and [REVOKE](https://www.postgresql.org/docs/current/sql-revoke.html).

PostgreSQL 15 changed the defaults for new databases: `PUBLIC` no longer receives `CREATE` on schema `public`, and `pg_database_owner` owns that schema. Upgrades and restores can preserve earlier permissions and ownership. This change did not remove default database `CONNECT`. See the [PostgreSQL 15 migration notes](https://www.postgresql.org/docs/15/release-15.html).

## 5. Secure schema lookup and privileged functions

A schema on `search_path` is trusted code territory: users who can create objects there can redirect unqualified lookups. Keep application schemas writable only by trusted owners and qualify object names in migrations.

```sql
ALTER ROLE app IN DATABASE app
  SET search_path = pg_catalog, app_data, pg_temp;
```

Reconnect to use the new default. `SET ROLE` does not apply the target role's login settings. Explicitly placing `pg_temp` last prevents temporary relations from taking precedence over trusted relations. This is a session default, not a restriction preventing the application from changing its own path. See [schema search paths](https://www.postgresql.org/docs/current/ddl-schemas.html), the [search_path reference](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-SEARCH-PATH) and [ALTER ROLE defaults](https://www.postgresql.org/docs/current/sql-alterrole.html).

A `SECURITY DEFINER` function needs its own safe path and restricted execution privileges. While connected to `app`, run the following as its owner or an authorized administrator. It assumes an existing application function `app_data.lookup_record(bigint)`; substitute its actual name and input argument types.

```sql
BEGIN;
ALTER FUNCTION app_data.lookup_record(bigint)
  SET search_path = pg_catalog, app_data, pg_temp;
REVOKE EXECUTE ON FUNCTION app_data.lookup_record(bigint) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app_data.lookup_record(bigint) TO app_runtime;
COMMIT;

ALTER DEFAULT PRIVILEGES FOR ROLE app_owner
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
```

For new functions, establish execution privileges in the same transaction as creation. The default-privilege revocation deliberately omits `IN SCHEMA`: a schema-specific revocation cannot subtract the global default `PUBLIC EXECUTE` grant. It applies to future functions created by `app_owner` in the current database; review existing functions separately.

These changes harden name resolution and execution access. They do not establish that the function's implementation is safe, or justify changing an ordinary function into a `SECURITY DEFINER` function. See [safe SECURITY DEFINER functions](https://www.postgresql.org/docs/current/sql-createfunction.html), [ALTER FUNCTION](https://www.postgresql.org/docs/current/sql-alterfunction.html) and [default privilege scope](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).

These are core controls. PostgreSQL 15's public-schema change does not make arbitrary user-writable schemas safe.

## 6. Client side

Require server identity verification as well as encryption. For libpq clients, use `sslmode=verify-full`, `sslrootcert=REPLACE_WITH_CA_FILE`, and `gssencmode=disable`. The guarded psql block under Verify supplies these settings and prompts for the password.

`sslmode=require` does not verify the server hostname. When a root CA file exists, libpq's compatibility behaviour makes `require` validate the certificate chain like `verify-ca`; applications should still request `verify-full` explicitly. See [libpq TLS verification](https://www.postgresql.org/docs/current/libpq-ssl.html).

Keep `gssencmode=disable` when testing or requiring TLS certificate verification: otherwise, working GSSAPI encryption can take precedence over TLS regardless of `sslmode`. Libpq-based clients accept these connection parameters; other drivers have their own interfaces and must be configured accordingly. See [libpq connection parameters](https://www.postgresql.org/docs/current/libpq-connect.html).

## 7. Record connection activity and administrative SQL

Configure a collected log destination and record connections, disconnections, and DDL. For a Unix-style deployment without an existing managed log destination:

```ini
log_destination = 'stderr'
logging_collector = on
log_file_mode = 0600
log_line_prefix = '%m [%p] %u@%d %r '
log_connections = on
log_disconnections = on
log_statement = 'ddl'
```

Enabling `logging_collector` requires a restart. Retest with fresh connections. If the deployment already collects PostgreSQL logs, use that destination and configure equivalent access restrictions instead of replacing it. `log_file_mode` controls collector-created files on Unix; Windows ignores it.

`ddl` excludes ordinary reads and writes. `mod` adds data-changing statements; `all` adds reads, increasing volume and the risk of recording sensitive values. Restrict log access and establish retention. Core statement logging is not a complete audit trail.

These are core settings. PostgreSQL 18 accepts a list for `log_connections`; `on` remains supported and enables receipt, authentication, and authorization logging. It does not enable every new connection-log option. See the [logging reference](https://www.postgresql.org/docs/current/runtime-config-logging.html).

### Optional: pgAudit for detailed audit records

pgAudit is an external, open-source extension. Install the release matching the server major version. Add it to the existing preload list, preserving other entries:

```ini
# This value assumes the existing list is empty.
shared_preload_libraries = 'pgaudit'
```

Restart, then connect as a superuser to each database requiring the extension. For database `app`:

```sql
CREATE EXTENSION pgaudit;
ALTER DATABASE app SET pgaudit.log = 'read,write,ddl,role';
```

Create the extension before setting `pgaudit.log`. Reconnect to apply the database default. Choose audit classes for the actual requirement and measure volume. Installing the extension alone does not demonstrate auditing.

At the time of writing, pgAudit 18.x targets PostgreSQL 18. Package and managed-service availability need separate checks. Its parameters are extension parameters, not PostgreSQL core settings. See the [official pgAudit 18 documentation](https://github.com/pgaudit/pgaudit/blob/dedd42ec3fe880bf581dd578c0df87ed4ad246cd/README.md), [CREATE EXTENSION](https://www.postgresql.org/docs/current/sql-createextension.html) and [shared_preload_libraries](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-SHARED-PRELOAD-LIBRARIES).

## 8. Verify

This revision's service checks are **REASONED, not demonstrated**. The authoring environment has psql 18.6 and PostgreSQL server binaries, but is read-only and has no authorized writable test deployment. Neither Docker nor Podman was found on `PATH`. Missing binaries are not the reason for the service-test limitation. Earlier execution evidence is not recorded in this file; this does not establish whether a previous author ran the earlier probes.

Local checks performed: both shell blocks passed `bash -n` and ShellCheck. Unsubstituted blocks exited locally, and 22 guard/argument cases passed using explicit local command spies without contacting a service. PostgreSQL 18.6 parsed and returned the 14 configuration values shown in the TLS, logging, and preload blocks using anonymous memory; an invalid Boolean control was rejected. This did not load certificates or pgAudit, parse HBA through a running server, or execute SQL.

Demonstrate exposed configurations only in an isolated disposable deployment. Record the server/client versions, fixture, commands, output, and relevant server logs for both states. A DNS error, timeout, missing CA file, or unrelated authentication failure does not prove enforcement.

### 8.1. TLS and authentication (REASONED: TLS/authentication comparisons from cited PostgreSQL documentation; no authorized writable deployment or certificate fixtures.)

**REASONED: no authorized writable PostgreSQL deployment with TLS, credentials, and controllable HBA rules.**

Use the same actual host, port, database, and role for each matched pair. This example uses port `5432`; change every occurrence if the deployment uses another port. Substitute inside the single quotes and paste the whole block. The compact connection strings require a hostname and CA path without whitespace, literal quotes, or backslashes.

The fourth value selects `tls`, `wrong`, `scram`, `plaintext`, or an interactive `sql` session. `wrong` uses the same connection settings as `tls`; enter a deliberately incorrect password at its prompt. Every password is entered at a prompt, never in argv.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DB_HOST' 'REPLACE_WITH_CA_FILE' 'app' 'tls'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "supply host, CA file, role and mode; not probing"; exit 1; }
  case "$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute every placeholder; not probing"; exit 1 ;;
  esac
  case "$2" in
    *"'"*) echo "use a CA path without whitespace, quotes or backslashes; not probing"; exit 1 ;;
    *[[:space:]]*|*\\*) echo "use a CA path without whitespace, quotes or backslashes; not probing"; exit 1 ;;
  esac
  case "$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_]*) echo "supply a simple role name; not probing"; exit 1 ;;
  esac
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute every placeholder; not probing"; exit 1 ;;
    *)
      case "$1" in
        *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.:-]*) echo "use a single hostname or IP address; not probing"; exit 1 ;;
      esac
      [ -f "$2" ] || { echo "CA file is missing; not probing"; exit 1; }
      [ -r "$2" ] || { echo "CA file is unreadable; not probing"; exit 1; }
      case "$4" in
        tls|wrong)
          psql -X -W -v ON_ERROR_STOP=1 \
            "host=$1 port=5432 dbname=app user=$3 sslmode=verify-full sslrootcert=$2 gssencmode=disable connect_timeout=5" \
            -c 'SELECT version();'
          ;;
        scram)
          psql -X -W -v ON_ERROR_STOP=1 \
            "host=$1 port=5432 dbname=app user=$3 sslmode=verify-full sslrootcert=$2 gssencmode=disable connect_timeout=5 require_auth=scram-sha-256" \
            -c 'SELECT 1;'
          ;;
        plaintext)
          psql -X -W -v ON_ERROR_STOP=1 \
            "host=$1 port=5432 dbname=app user=$3 sslmode=disable gssencmode=disable connect_timeout=5" \
            -c 'SELECT 1;'
          ;;
        sql)
          psql -X -W -v ON_ERROR_STOP=1 \
            "host=$1 port=5432 dbname=app user=$3 sslmode=verify-full sslrootcert=$2 gssencmode=disable connect_timeout=5"
          ;;
        *) echo "choose tls, wrong, scram, plaintext or sql; not probing"; exit 1 ;;
      esac
      ;;
  esac
)
```

Run each mode separately so an expected failure cannot skip the next positive control.

| Check | Exposed fixture and expected result | Fixed result and matched positive control |
| --- | --- | --- |
| Password demand | An earlier matching `trust` rule lets `wrong` connect despite the incorrect prompted password. | `wrong` fails with password authentication failure; `tls` with the correct password still succeeds. |
| Negotiated SCRAM | A matching `password` rule allows the ordinary `tls` login, but `scram` rejects the non-SCRAM exchange. | `scram` succeeds with the correct password. This requires libpq 16+ and proves the negotiated method, not removal of every HBA entry named `md5`. |
| TLS enforcement | A matching plaintext-permitting `host` rule lets `plaintext` connect using disposable valid credentials. | `plaintext` receives an HBA refusal indicating no matching entry and no encryption; `tls` still succeeds. |
| Server hostname verification | On the disposable endpoint, install an otherwise trusted certificate for the wrong hostname. In the exposed client comparison, change only the `tls` branch's `sslmode` to `require`; it can connect. | Restore `verify-full`; the wrong-name certificate causes a hostname-verification failure. A trusted certificate for the actual hostname makes the same `tls` command succeed. |

The first-match rule, SCRAM negotiation, and TLS-mode distinctions are documented in the [HBA reference](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html), [password authentication](https://www.postgresql.org/docs/current/auth-password.html), [libpq parameters](https://www.postgresql.org/docs/current/libpq-connect.html) and [libpq TLS verification](https://www.postgresql.org/docs/current/libpq-ssl.html). The client version boundary is documented in the [PostgreSQL 16 release notes](https://www.postgresql.org/docs/16/release-16.html).

If using `clientcert=verify-full`, also test with two trusted, otherwise valid client certificates: one matching the requested database identity and one not matching it or any configured mapping. Run `tls` with each, supplying the certificate through the test client's normal libpq certificate configuration. With exposed `clientcert=verify-ca`, both identities can pass certificate validation; fixed `verify-full` rejects the mismatched identity while the matching certificate and correct password still connect. **REASONED: the writable deployment and client-certificate fixture are unavailable.** See [client certificate options](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html) and [libpq client certificates](https://www.postgresql.org/docs/current/libpq-ssl.html).

### 8.2. Listener binding (REASONED: listener comparison from cited PostgreSQL and ss documentation; no authorized writable deployment.)

**REASONED: no authorized writable deployment in which to change and inspect PostgreSQL listeners.**

Run on the database host, substituting the intended bind address. Inspect every returned listener, including IPv6.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_EXPECTED_BIND_ADDRESS'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply the expected bind address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute every placeholder; not probing"; exit 1 ;;
    *)
      printf 'Expected listener address: %s; inspect every returned row.\n' "$1"
      ss -tlnp 'sport = :5432'
      ;;
  esac
)
```

In the exposed disposable fixture, `listen_addresses = '*'` produces wildcard listeners on available IP interfaces. After setting the intended loopback/private addresses and restarting, only the intended addresses should remain. Pair this observation with a successful `tls` connection through an intended interface; no listener at all is not a passing result. See [listen_addresses](https://www.postgresql.org/docs/current/runtime-config-connection.html) and [ss](https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html).

### 8.3. Runtime access and ownership (REASONED: ownership and grant comparisons from cited PostgreSQL documentation; no authorized writable cluster.)

**REASONED: no authorized writable cluster for ownership, membership, and default-grant fixtures.**

Use actual `app` logins through the wrapper's `sql` mode for application checks. A superuser session followed by `SET ROLE app` does not test login-time settings or connection admission.

In the disposable database, create and seed an existing-object probe from the separate migration connection:

```sql
SET ROLE app_owner;
CREATE TABLE app_data.security_probe (id integer PRIMARY KEY);
INSERT INTO app_data.security_probe VALUES (1);
GRANT SELECT, INSERT, UPDATE, DELETE
  ON app_data.security_probe TO app_runtime;
RESET ROLE;
```

As the real `app` login, this positive control must return the seeded row in both states:

```sql
SELECT * FROM app_data.security_probe;
```

Run each negative probe separately. If a statement fails inside a transaction, issue `ROLLBACK;` before continuing, or close that session.

```sql
BEGIN;
ALTER TABLE app_data.security_probe ADD COLUMN probe integer;
ROLLBACK;
```

In a separate `app` session:

```sql
SET ROLE app_owner;
```

With exposed table ownership or owner-role membership, alteration can succeed; membership permitting role selection also allows `SET ROLE app_owner`. Fixed runtime access must deny both while preserving the read. Pair the denied alteration with the same transactional alteration run successfully from the authorized migration connection as `app_owner`.

To check future grants, create another table as `app_owner` after configuring default privileges, without a manual grant:

```sql
SET ROLE app_owner;
CREATE TABLE app_data.security_probe_future (id integer PRIMARY KEY);
INSERT INTO app_data.security_probe_future VALUES (2);
RESET ROLE;
```

As `app`:

```sql
SELECT * FROM app_data.security_probe_future;
```

The fixed state returns the seeded row. In the comparison fixture without the default table grant, this future-table read is denied while the explicitly granted existing-table read still succeeds. Recreate the fixture for each state; changing defaults does not repair a table already created.

These expected distinctions follow [ownership privileges](https://www.postgresql.org/docs/current/ddl-priv.html), [SET ROLE](https://www.postgresql.org/docs/current/sql-set-role.html) and [default grants](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).

### 8.4. Database admission and schema creation (REASONED: admission and creation comparisons from cited PostgreSQL documentation; no disposable cluster or nonmember login.)

**REASONED: no authorized writable cluster with a disposable nonmember login and controllable HBA/ACLs.**

Administratively create a disposable login:

```sql
CREATE ROLE app_probe_nonmember LOGIN;
```

Set its disposable password with psql's interactive `\password app_probe_nonmember`. Give it matching SCRAM HBA access to `app` from the test client, but no runtime membership or separate `CONNECT` grant.

Run the wrapper with mode `tls` and role `app_probe_nonmember`, then with role `app`. With exposed `PUBLIC CONNECT`, both connect. After the admission changes, the nonmember must receive a database permission denial while `app` still connects. A password failure or missing HBA entry is not the admission discriminator. See [CONNECT privileges](https://www.postgresql.org/docs/current/ddl-priv.html).

As `app`, separately test public schema creation:

```sql
BEGIN;
CREATE TABLE public.security_creation_probe (id integer);
ROLLBACK;
```

With exposed `PUBLIC CREATE`, creation succeeds. After revocation, it must fail for insufficient schema privileges. Run the same transactional creation successfully as an authorized administrator to show that the schema and operation are usable. If `app` still succeeds, inspect ownership, direct grants, and memberships. See [schema privileges](https://www.postgresql.org/docs/current/ddl-schemas.html).

If temporary-table creation was revoked, also run as `app`:

```sql
BEGIN;
CREATE TEMP TABLE security_temp_probe (id integer);
ROLLBACK;
```

The exposed default permits creation; the fixed state denies it. Pair the denial with a successful `SELECT * FROM app_data.security_probe;` as `app` and successful temporary-table creation from an authorized administrative connection. See [TEMPORARY privileges](https://www.postgresql.org/docs/current/ddl-priv.html) and [CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html).

### 8.5. Schema lookup and function execution (REASONED: lookup and execution comparisons from cited PostgreSQL documentation; no writable cluster or function fixtures.)

**REASONED: no authorized writable cluster for trusted/shadow tables and privileged-function fixtures.**

Create this test-only fixture administratively in the disposable database:

```sql
BEGIN;
SET ROLE app_owner;

CREATE TABLE app_data.security_lookup_probe (
  id integer PRIMARY KEY,
  marker text
);
INSERT INTO app_data.security_lookup_probe VALUES (1, 'trusted');

CREATE FUNCTION app_data.security_lookup_probe_fn()
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, app_data, pg_temp
AS $$
  SELECT marker FROM security_lookup_probe WHERE id = 1;
$$;

REVOKE EXECUTE ON FUNCTION app_data.security_lookup_probe_fn() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION app_data.security_lookup_probe_fn() TO app_runtime;

RESET ROLE;
COMMIT;
```

For this isolated lookup test only, an administrator must grant `TEMPORARY` to `app` if the optional revocation in step 4 removed it:

```sql
GRANT TEMPORARY ON DATABASE app TO app;
```

Open a fresh real `app` session with mode `sql`. Inspect the login default, then create a distinguishable temporary relation. Grant its read privilege to the function owner so a permission error cannot conceal an unsafe lookup.

```sql
SHOW search_path;

CREATE TEMP TABLE security_lookup_probe (
  id integer PRIMARY KEY,
  marker text
);
INSERT INTO pg_temp.security_lookup_probe VALUES (1, 'shadow');
GRANT SELECT ON pg_temp.security_lookup_probe TO app_owner;

SELECT marker FROM security_lookup_probe WHERE id = 1;
SELECT app_data.security_lookup_probe_fn();
```

With the fixed login path and function-local path, both queries must return `trusted`. For the exposed login-path comparison, set the disposable session's path without an explicit `pg_temp` entry:

```sql
SET search_path = pg_catalog, app_data;
SELECT marker FROM security_lookup_probe WHERE id = 1;
SELECT app_data.security_lookup_probe_fn();
```

The ordinary unqualified query now returns `shadow`; the fixed function must still return `trusted`.

For the independent exposed function-path comparison, change only the test function administratively:

```sql
ALTER FUNCTION app_data.security_lookup_probe_fn()
  SET search_path = pg_catalog, app_data;
```

Reconnect as `app`, recreate the temporary fixture and its grant, and call the function again. It now returns `shadow`. Restore the function-local path:

```sql
ALTER FUNCTION app_data.security_lookup_probe_fn()
  SET search_path = pg_catalog, app_data, pg_temp;
```

Repeat through a fresh `app` session with the same temporary fixture; the result must return to `trusted`. The documented reason is that omitting `pg_temp` searches temporary relations first. See [search_path](https://www.postgresql.org/docs/current/runtime-config-client.html#GUC-SEARCH-PATH) and [safe SECURITY DEFINER functions](https://www.postgresql.org/docs/current/sql-createfunction.html).

For the execution-privilege test, retain the fixed function path. Administratively admit the disposable nonmember and give it schema lookup access, isolating function execution from admission and schema failures:

```sql
GRANT CONNECT ON DATABASE app TO app_probe_nonmember;
GRANT USAGE ON SCHEMA app_data TO app_probe_nonmember;
GRANT EXECUTE ON FUNCTION app_data.security_lookup_probe_fn() TO PUBLIC;
```

Through separate real `app` and `app_probe_nonmember` connections, run:

```sql
SELECT app_data.security_lookup_probe_fn();
```

Both succeed in this exposed fixture. Administratively apply:

```sql
REVOKE EXECUTE ON FUNCTION app_data.security_lookup_probe_fn() FROM PUBLIC;
```

The same call must then fail for the nonmember with a function permission denial, while `app` still returns `trusted`. This tests the [EXECUTE privilege](https://www.postgresql.org/docs/current/sql-grant.html).

Discard the disposable fixture after testing. The temporary-table and nonmember admission grants above are test prerequisites, not production grants.

### 8.6. Core logging (REASONED: log-delivery comparison from cited PostgreSQL documentation; no writable cluster or collected logs.)

**REASONED: no authorized writable cluster and accessible collected log destination.**

Through a fresh real `app` connection, run and then disconnect:

```sql
SELECT 1;
```

From the separate migration connection:

```sql
SET ROLE app_owner;
BEGIN;
CREATE TABLE app_data.audit_probe (id integer);
ROLLBACK;
RESET ROLE;
```

Compare a disposable fixture with connection/disconnection logging disabled and `log_statement = 'none'` against step 7. Both operations must succeed in both states. The fixed state must produce the connection, disconnection, and DDL records in the actual collected destination, correlated by time, process, role, and database. The corresponding records are absent in the exposed fixture.

`ddl` need not record the successful `SELECT 1` statement. Inspect actual records; `SHOW` output alone does not demonstrate delivery. See the [logging reference](https://www.postgresql.org/docs/current/runtime-config-logging.html).

### 8.7. Optional pgAudit (REASONED: audit-event comparison from cited pgAudit documentation; no writable cluster with pgAudit and logs.)

**REASONED: no authorized writable cluster with pgAudit and access to its server-side logs.**

As the real `app` login:

```sql
SELECT * FROM app_data.security_probe;
```

Compare fresh sessions with the effective `pgaudit.log` setting disabled (`none`) and with the selected audit classes enabled. The seeded query must succeed in both states. An appropriate server-side `READ` audit event, correlated to that query and session, must appear in the enabled state and be absent from the disabled state. Confirm effective settings for this login; role-specific defaults can override database defaults.

Extension installation alone is not a passing result. See the [pgAudit session audit documentation](https://github.com/pgaudit/pgaudit/blob/dedd42ec3fe880bf581dd578c0df87ed4ad246cd/README.md).

### 8.8. Supplemental diagnostics (REASONED: diagnostics from cited PostgreSQL documentation; no authorized target service.)

**REASONED: no authorized target service on which to execute these administrative queries.**

Run through an authorized administrative connection. These provide context for the paired tests; they are not independent enforcement proofs.

```sql
SELECT ssl, count(*)
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
GROUP BY ssl;

SELECT rolname, rolpassword LIKE 'SCRAM-SHA-256%' AS scram
FROM pg_authid
WHERE rolname = 'app';

SELECT line_number, error
FROM pg_hba_file_rules
WHERE error IS NOT NULL;

SELECT name, setting, applied, error
FROM pg_file_settings
WHERE error IS NOT NULL OR NOT applied;
```

`pg_stat_ssl` describes live connections, not connections the server would permit. The `pg_authid` query reports only a verifier-format Boolean, not the password verifier itself; require a row for `app` with `scram` true, then separately test negotiated SCRAM.

`pg_hba_file_rules` describes current file contents, not necessarily the last successfully loaded rules. `pg_file_settings` also describes current files; an unapplied entry can be superseded by a later entry without being an error. Neither view proves which HBA rule authenticated a session or that replacement TLS files were accepted. See [connection statistics](https://www.postgresql.org/docs/current/monitoring-stats.html), [pg_authid](https://www.postgresql.org/docs/current/catalog-pg-authid.html), [pg_hba_file_rules](https://www.postgresql.org/docs/current/view-pg-hba-file-rules.html) and [pg_file_settings](https://www.postgresql.org/docs/current/view-pg-file-settings.html).

### Verification scope

| Check scope | Status and missing prerequisite | Deployment comparison |
| --- | --- | --- |
| Service checks 8.1-8.8 | REASONED from the cited PostgreSQL and pgAudit documentation; not demonstrated. An authorized writable disposable PostgreSQL deployment, TLS/client-certificate fixtures, nonmember credentials, collected logs, and pgAudit for the optional check are unavailable. | Run each applicable exposed/fixed comparison and matched positive control above through real authenticated logins. Record versions, configurations, commands, results, and correlated server logs. Include the earlier `trust` rule, plaintext-permitting `host` rule, and non-SCRAM password exchange fixtures. Record diagnostic output without treating it as enforcement proof. |

## Common mistakes

- `listen_addresses = '*'` plus a permissive `host all all 0.0.0.0/0 md5` line pasted from a tutorial.
- `trust` authentication left enabled for remote addresses.
- The superuser (`postgres`) used as the application account; create a least-privilege role instead ([authentication.md](authentication.md)).
- Giving the application membership in its owner role, which defeats the separation between runtime access and migrations.
- Assuming PostgreSQL 15 repaired public-schema permissions in an upgraded or restored database.
- Treating a successful reload signal, a stored SCRAM verifier, or an installed audit extension as proof of enforcement.

## Sources (checked September 2026)

- Official PostgreSQL Docker images (14 through 19, Debian and Alpine; shown for 19/bookworm; pinned commit d588a44673ea9d123c1acb1a6924de10a27fc315): the build's `listen_addresses = '*'` edit to postgresql.conf.sample, `CMD ["postgres"]`, the entrypoint's initdb call with no authentication method beyond `POSTGRES_INITDB_ARGS`, the init-only password check (`POSTGRES_PASSWORD` read with `file_env`), and the appended `host all all all` line defaulting to `password_encryption`: https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/Dockerfile#L183-L184, https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/Dockerfile#L223-L224, https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L92, https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L105-L138, https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L235, https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L268-L286 and https://github.com/docker-library/postgres/blob/d588a44673ea9d123c1acb1a6924de10a27fc315/19/bookworm/docker-entrypoint.sh#L347-L355
- initdb's default authentication method `trust` when none is given, and the sample `pg_hba.conf` loopback rules that take it (pinned tag REL_17_11; the same default in REL_14_24, REL_15_19, REL_16_15, REL_18_6 and REL_19_BETA4): https://github.com/postgres/postgres/blob/REL_17_11/src/bin/initdb/initdb.c#L2550-L2557, https://github.com/postgres/postgres/blob/REL_17_11/src/bin/initdb/initdb.c#L3434-L3435 and https://github.com/postgres/postgres/blob/REL_17_11/src/backend/libpq/pg_hba.conf.sample#L113-L117
- Secure TCP/IP connections with SSL and TLS file reload behaviour: https://www.postgresql.org/docs/current/ssl-tcp.html
- Connections and authentication settings: https://www.postgresql.org/docs/current/runtime-config-connection.html
- HBA matching, reload behaviour, and client certificate options: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html
- Password authentication and SCRAM negotiation through md5 HBA entries: https://www.postgresql.org/docs/current/auth-password.html
- RADIUS authentication: https://www.postgresql.org/docs/current/auth-radius.html
- Libpq TLS verification and client certificates: https://www.postgresql.org/docs/current/libpq-ssl.html
- Libpq connection parameters: https://www.postgresql.org/docs/current/libpq-connect.html
- CREATE ROLE: https://www.postgresql.org/docs/current/sql-createrole.html
- ALTER ROLE and login defaults: https://www.postgresql.org/docs/current/sql-alterrole.html
- Role membership: https://www.postgresql.org/docs/current/role-membership.html
- ALTER DATABASE: https://www.postgresql.org/docs/current/sql-alterdatabase.html
- CREATE SCHEMA: https://www.postgresql.org/docs/current/sql-createschema.html
- GRANT: https://www.postgresql.org/docs/current/sql-grant.html
- REVOKE: https://www.postgresql.org/docs/current/sql-revoke.html
- ALTER DEFAULT PRIVILEGES: https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html
- SET ROLE and RESET ROLE: https://www.postgresql.org/docs/current/sql-set-role.html
- Object ownership and default privileges: https://www.postgresql.org/docs/current/ddl-priv.html
- Schemas, privileges, and search paths: https://www.postgresql.org/docs/current/ddl-schemas.html
- Client defaults, search_path, and shared_preload_libraries: https://www.postgresql.org/docs/current/runtime-config-client.html
- CREATE FUNCTION and safe SECURITY DEFINER functions: https://www.postgresql.org/docs/current/sql-createfunction.html
- ALTER FUNCTION: https://www.postgresql.org/docs/current/sql-alterfunction.html
- Logging configuration: https://www.postgresql.org/docs/current/runtime-config-logging.html
- Official pgAudit 18 documentation: https://github.com/pgaudit/pgaudit/blob/dedd42ec3fe880bf581dd578c0df87ed4ad246cd/README.md
- CREATE EXTENSION: https://www.postgresql.org/docs/current/sql-createextension.html
- CREATE TABLE and temporary tables: https://www.postgresql.org/docs/current/sql-createtable.html
- ALTER TABLE and ownership transfer: https://www.postgresql.org/docs/current/sql-altertable.html
- INSERT: https://www.postgresql.org/docs/current/sql-insert.html
- SELECT: https://www.postgresql.org/docs/current/sql-select.html
- BEGIN: https://www.postgresql.org/docs/current/sql-begin.html
- COMMIT: https://www.postgresql.org/docs/current/sql-commit.html
- ROLLBACK: https://www.postgresql.org/docs/current/sql-rollback.html
- SHOW: https://www.postgresql.org/docs/current/sql-show.html
- psql invocation, password prompts, and password changes: https://www.postgresql.org/docs/current/app-psql.html
- PostgreSQL server configuration inspection: https://www.postgresql.org/docs/current/app-postgres.html
- System administration functions including pg_reload_conf: https://www.postgresql.org/docs/current/functions-admin.html
- System information functions including version: https://www.postgresql.org/docs/current/functions-info.html
- Aggregate functions including count: https://www.postgresql.org/docs/current/functions-aggregate.html
- Pattern matching with LIKE: https://www.postgresql.org/docs/current/functions-matching.html
- Connection statistics including pg_stat_ssl and pg_stat_activity: https://www.postgresql.org/docs/current/monitoring-stats.html
- Password verifier catalog fields: https://www.postgresql.org/docs/current/catalog-pg-authid.html
- HBA file diagnostics: https://www.postgresql.org/docs/current/view-pg-hba-file-rules.html
- Configuration file diagnostics: https://www.postgresql.org/docs/current/view-pg-file-settings.html
- PostgreSQL 12 TLS parameter and client certificate changes: https://www.postgresql.org/docs/12/release-12.html
- PostgreSQL 14 password_encryption default change: https://www.postgresql.org/docs/14/release-14.html
- PostgreSQL 15 public-schema permission and ownership changes: https://www.postgresql.org/docs/15/release-15.html
- PostgreSQL 16 membership options: https://www.postgresql.org/docs/16/role-membership.html
- PostgreSQL 16 require_auth introduction: https://www.postgresql.org/docs/16/release-16.html
- PostgreSQL 18 MD5 deprecation and connection logging changes: https://www.postgresql.org/docs/18/release-18.html
- ss listener options and sport filter: https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html
