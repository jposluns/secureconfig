---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "113ba06988db5799e83bedf95c20268a5fd5202f80c3a3cc4c87c1c34b2b2dfa",
  "components": {
    "pgb": {
      "name": "PgBouncer documentation",
      "basis": "unknown",
      "sources": {
        "sa5cdd62a9242": "https://www.pgbouncer.org/config.html",
        "s91d48cfb22ae": "https://www.pgbouncer.org/usage.html",
        "scd8f294039fa": "https://www.pgbouncer.org/features.html"
      }
    },
    "pgb-bind": {
      "name": "PgBouncer listener source",
      "basis": "pgbouncer_1_26_0",
      "sources": {
        "s8dc535fd70f7": "https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/src/main.c#L292",
        "sb926a3d2cba4": "https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/src/pooler.c#L495-L498",
        "s6910c5b38697": "https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/include/bouncer.h#L54-L62"
      }
    },
    "pgb-source": {
      "name": "PgBouncer source and fixes",
      "basis": "1.25.2",
      "sources": {
        "s2a1788c4296b": "https://www.pgbouncer.org/changelog.html",
        "sd8ac14670f91": "https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/admin.c",
        "sb9455e4f6c90": "https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/pam.c",
        "sd1ad8c2587a4": "https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/hba.c"
      }
    },
    "pgpool": {
      "name": "Pgpool-II documentation",
      "basis": "unknown",
      "sources": {
        "s7b1cbfaacbb8": "https://www.pgpool.net/docs/latest/en/html/runtime-config-connection.html",
        "s76141317a1b5": "https://www.pgpool.net/docs/latest/en/html/runtime-ssl.html",
        "sa7204f187c7e": "https://www.pgpool.net/docs/latest/en/html/auth-pool-hba-conf.html",
        "sdc3d487af0ae": "https://www.pgpool.net/docs/latest/en/html/configuring-pcp-conf.html",
        "sd1c787b7784e": "https://www.pgpool.net/docs/latest/en/html/config-setting.html",
        "s7847f7feb03b": "https://www.pgpool.net/docs/latest/en/html/auth-methods.html",
        "s5e8db4ad8b4e": "https://www.pgpool.net/docs/latest/en/html/auth-aes-encrypted-password.html",
        "s13f19539cfbf": "https://www.pgpool.net/docs/latest/en/html/pcp-common-options.html"
      }
    },
    "pgpool-source": {
      "name": "Pgpool-II backend handshake",
      "basis": "4.7.2",
      "sources": {
        "saf1078d5bb5c": "https://raw.githubusercontent.com/pgpool/pgpool2/V4_7_2/src/utils/pool_ssl.c"
      }
    },
    "postgres": {
      "name": "PostgreSQL documentation",
      "basis": "unknown",
      "sources": {
        "sbb484e8233fe": "https://www.postgresql.org/docs/current/auth-pg-hba-conf.html",
        "sc39eceeac711": "https://www.postgresql.org/docs/current/functions-info.html",
        "seed379369be7": "https://www.postgresql.org/docs/current/monitoring-stats.html",
        "sf1b3da55ebd5": "https://www.postgresql.org/docs/current/runtime-config-logging.html",
        "s8a1c90f4aa93": "https://www.postgresql.org/docs/current/auth-peer.html",
        "s97264da004c0": "https://www.postgresql.org/docs/current/libpq-envars.html",
        "s198d4780d9a4": "https://www.postgresql.org/docs/current/libpq-pgpass.html",
        "sf8b93623c032": "https://www.postgresql.org/docs/current/app-psql.html",
        "sd389a3478bc7": "https://www.postgresql.org/docs/current/libpq-connect.html"
      }
    },
    "ldap-min": {
      "name": "PgBouncer LDAP minimum",
      "basis": "1.25.0",
      "sources": {
        "sa5cdd62a9242": "https://www.pgbouncer.org/config.html"
      }
    },
    "expiry-fix": {
      "name": "PgBouncer password-expiry fix",
      "basis": "1.24.1",
      "sources": {
        "sa5cdd62a9242": "https://www.pgbouncer.org/config.html"
      }
    }
  },
  "claims": {
    "packet-fix": {"text": "1.25.2 fixes CVE-2026-6664: an unauthenticated malformed SCRAM packet can crash older releases.", "components": ["pgb-source"], "sources": ["pgb-source:s2a1788c4296b"], "status": "REASONED"},
    "backend-fixes": {"text": "1.25.2 fixes CVE-2026-6665 from a malicious backend and CVE-2026-6666 from a backend error lacking SQLSTATE.", "components": ["pgb-source"], "sources": ["pgb-source:s2a1788c4296b"], "status": "REASONED"},
    "console-fix": {"text": "1.25.2 fixes CVE-2026-6667, which allowed any authorized console user to run KILL_CLIENT.", "components": ["pgb-source"], "sources": ["pgb-source:s2a1788c4296b"], "status": "REASONED"},
    "ini-comments": {"text": "PgBouncer ini comments must start their own line; trailing # or ; becomes part of the value.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "pgb-listener": {"text": "Use private listen_addr and port 6432; the 1.26.0 unset default is Unix sockets only except systemd socket activation, whose ListenStream settings override listen_addr.", "components": ["pgb", "pgb-bind"], "sources": ["pgb:sa5cdd62a9242", "pgb-bind:s8dc535fd70f7", "pgb-bind:sb926a3d2cba4", "pgb-bind:s6910c5b38697"], "status": "REASONED"},
    "pgpool-listener": {"text": "Pgpool-II defaults to localhost:9999; listen_addresses is startup-only.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8"], "status": "REASONED"},
    "pcp-listener": {"text": "PCP independently defaults to localhost:9898 through startup-only pcp_listen_addresses and pcp_port.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8"], "status": "REASONED"},
    "pcp-credentials": {"text": "PCP uses separate username:MD5-digest entries in protected pcp.conf; pg_md5 -p prompts, and pool_passwd is not interchangeable.", "components": ["pgpool"], "sources": ["pgpool:sdc3d487af0ae"], "status": "REASONED"},
    "client-tls": {"text": "PgBouncer client TLS defaults disabled; require with a key and certificate rejects non-TLS TCP clients while Unix sockets are exempt.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "client-protocols": {"text": "PgBouncer client_tls_protocols defaults to secure, meaning TLSv1.2 and TLSv1.3.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "client-cert": {"text": "client_tls_sslmode=verify-full and client_tls_ca_file require client certificates; protect the private key at mode 600.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "pgpool-tls": {"text": "Pgpool-II ssl defaults off; enabling it covers both hops but frontend TLS also needs ssl_key and ssl_cert.", "components": ["pgpool"], "sources": ["pgpool:s76141317a1b5"], "status": "REASONED"},
    "pgpool-hostssl": {"text": "Pgpool-II host matches TLS and plaintext; hostssl requires ssl=on or is ignored, and unmatched connections are denied.", "components": ["pgpool"], "sources": ["pgpool:s76141317a1b5", "pgpool:sa7204f187c7e"], "status": "REASONED"},
    "backend-tls": {"text": "PgBouncer server_tls_sslmode defaults prefer, permitting plaintext fallback without certificate checks; require omits certificate validation and verify-ca omits hostname checks.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "backend-verify-full": {"text": "Set PgBouncer server_tls_sslmode=verify-full with server_tls_ca_file to require TLS, a trusted certificate and matching hostname.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "pgpool-ca": {"text": "Pgpool-II ssl_ca_cert or ssl_ca_cert_dir enables backend CA verification; the documentation establishes no hostname check.", "components": ["pgpool"], "sources": ["pgpool:s76141317a1b5"], "status": "REASONED"},
    "pgpool-downgrade": {"text": "Pgpool-II 4.7.2 continues plaintext if the backend declines TLS even with ssl_ca_cert; use a separately authenticated enforcing transport or PgBouncer verify-full.", "components": ["pgpool", "pgpool-source"], "sources": ["pgpool:s76141317a1b5", "pgpool-source:saf1078d5bb5c"], "status": "REASONED"},
    "forced-user": {"text": "A databases user= forces every client into one backend role; omitting it preserves client usernames and separate pools, with force_user visible in SHOW DATABASES.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242", "pgb:s91d48cfb22ae"], "status": "REASONED"},
    "backend-source": {"text": "PostgreSQL HBA sees the pooler backend source after NAT; inet_client_addr returns that source or NULL on Unix sockets. A narrow address rule is not a process identity.", "components": ["pgb", "postgres"], "sources": ["pgb:scd8f294039fa", "postgres:sbb484e8233fe", "postgres:sc39eceeac711"], "status": "REASONED"},
    "client-hba": {"text": "PgBouncer auth_type=hba activates auth_hba_file for per-path peer/SCRAM/TLS rules; choosing a global method instead disables that policy.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "pgpool-hba": {"text": "Pgpool-II enable_pool_hba defaults false, leaving authentication to PostgreSQL; enabling it adds client policy without changing per-user/database pooling.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8", "pgpool:sa7204f187c7e", "pgpool:s7847f7feb03b"], "status": "REASONED"},
    "pgpool-passwords": {"text": "SCRAM needs matching plaintext or AES pool_passwd credentials, not MD5; pg_enc prompts, and AES requires OpenSSL plus service-owned mode-600 .pgpoolkey.", "components": ["pgpool"], "sources": ["pgpool:s7847f7feb03b", "pgpool:s5e8db4ad8b4e"], "status": "REASONED"},
    "pgpool-local": {"text": "Local trust accepts any claimed database identity; unix_socket_directories defaults /tmp and every listed socket directory needs protection.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8", "pgpool:sa7204f187c7e"], "status": "REASONED"},
    "hba-order": {"text": "HBA first-match order governs access; explicit IPv4/IPv6 plaintext rejections stop later permissive rules, not earlier ones.", "components": ["pgpool", "postgres"], "sources": ["pgpool:sa7204f187c7e", "postgres:sbb484e8233fe"], "status": "REASONED"},
    "client-metadata": {"text": "application_name_add_host defaults 0; enabling it adds client address only at connection start and clients can later overwrite application_name.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "log-prefix": {"text": "PostgreSQL log_line_prefix defaults to %m [%p] without application name; include %a to log the diagnostic metadata.", "components": ["postgres"], "sources": ["postgres:sf1b3da55ebd5"], "status": "REASONED"},
    "console-lists": {"text": "The reserved pgbouncer database uses admin_users for full commands and stats_users for read-only SHOW; both default empty.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242", "pgb:s91d48cfb22ae"], "status": "REASONED"},
    "console-any": {"text": "Configuration and usage docs disagree on any; 1.25.2 grants unlisted users console read access and lets clients claim an administrator name without authentication.", "components": ["pgb", "pgb-source"], "sources": ["pgb:sa5cdd62a9242", "pgb:s91d48cfb22ae", "pgb-source:sd8ac14670f91"], "status": "REASONED"},
    "weak-auth": {"text": "trust and any do not authenticate, plain transmits a cleartext password and is deprecated, and auth_type defaults md5.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "console-scram": {"text": "Keep hba with SCRAM rules for pgbadmin and pgbmetrics; metrics credentials must satisfy both HBA and the console allowlist.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "socket-bypass": {"text": "The pgbouncer username can access the console passwordlessly over a Unix socket when the client UID equals the pooler process UID.", "components": ["pgb"], "sources": ["pgb:s91d48cfb22ae"], "status": "REASONED"},
    "peer": {"text": "Peer authentication uses the OS identity; a connection-string user name or password cannot supply that identity.", "components": ["pgb", "postgres"], "sources": ["pgb:sa5cdd62a9242", "postgres:s8a1c90f4aa93"], "status": "REASONED"},
    "auth-file": {"text": "Protect auth_file at mode 600; it can contain plaintext, MD5 or SCRAM secrets, and MD5 cannot satisfy client SCRAM.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "scram-forward": {"text": "Stored-SCRAM backend login needs client SCRAM, no forced user and identical secrets including salt and iteration count; peer does not provide the required exchange.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "auth-query": {"text": "auth_user enables lookup for users absent from auth_file; use a restricted SECURITY DEFINER function with trusted search_path, limited EXECUTE and database placement or auth_dbname.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"},
    "password-expiry": {"text": "CVE-2025-2291 was fixed in 1.24.1; custom auth_query must still check rolvaliduntil.", "components": ["pgb", "expiry-fix"], "sources": ["pgb:sa5cdd62a9242", "expiry-fix:sa5cdd62a9242"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory 6432/9999 on private addresses and PCP 9898 on loopback including IPv6; unexpected listeners are findings.", "components": ["pgb", "pgpool"], "sources": ["pgb:sa5cdd62a9242", "pgpool:s7b1cbfaacbb8"], "status": "REASONED", "verify": [1]},
    "verify-client": {"text": "Plaintext must fail for TLS, verified TLS with the correct password must succeed, and a wrong password must fail authentication; repeat for pgpool-II 9999.", "components": ["pgb", "pgpool", "postgres"], "sources": ["pgb:sa5cdd62a9242", "pgpool:s76141317a1b5", "pgpool:sa7204f187c7e", "postgres:s198d4780d9a4", "postgres:sd389a3478bc7"], "status": "REASONED", "verify": [2]},
    "password-delivery": {"text": "Use mode-600 .pgpass for real passwords; PGPASSWORD can expose credentials through process environments.", "components": ["postgres"], "sources": ["postgres:s97264da004c0", "postgres:s198d4780d9a4"], "status": "REASONED"},
    "verify-pgpool": {"text": "PGPOOL SHOW enable_pool_hba and ssl must both report on; inspect ordered HBA, reload errors and Unix-socket positive/negative credentials.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8", "pgpool:s76141317a1b5", "pgpool:sa7204f187c7e"], "status": "REASONED", "verify": [3]},
    "verify-pcp": {"text": "PCP read with correct prompted credentials must succeed and a wrong password must fail authentication; remote 9898 must be unreachable.", "components": ["pgpool"], "sources": ["pgpool:s7b1cbfaacbb8", "pgpool:sdc3d487af0ae", "pgpool:s13f19539cfbf"], "status": "REASONED", "verify": [3]},
    "verify-pgb-policy": {"text": "RELOAD must succeed before SHOW CONFIG and disk-HBA inspection; confirm hba, TLS modes and pathname, then rerun connection tests.", "components": ["pgb", "postgres"], "sources": ["pgb:sa5cdd62a9242", "pgb:s91d48cfb22ae", "postgres:sf8b93623c032"], "status": "REASONED", "verify": [4]},
    "hba-parser": {"text": "PgBouncer 1.25.2 logs and skips malformed HBA lines without failing RELOAD; parser or access warnings leave verification incomplete.", "components": ["pgb-source"], "sources": ["pgb-source:sd1ad8c2587a4"], "status": "REASONED", "verify": [4]},
    "verify-backend-observation": {"text": "pg_stat_ssl reports negotiated encryption, not certificate enforcement; current_user and inet_client_addr identify backend role and source.", "components": ["postgres"], "sources": ["postgres:sc39eceeac711", "postgres:seed379369be7"], "status": "REASONED", "verify": [5]},
    "verify-direct": {"text": "Direct application-to-database access must fail HBA while permitted pooler egress and application-through-pooler controls succeed; disable GSS precedence and guard host/hostaddr.", "components": ["postgres"], "sources": ["postgres:sbb484e8233fe", "postgres:sd389a3478bc7"], "status": "REASONED", "verify": [6]},
    "verify-backend-enforcement": {"text": "Use fresh backend connections and restored positive controls: PgBouncer verify-full rejects untrusted CA, wrong hostname and TLS refusal; Pgpool-II only establishes CA rejection.", "components": ["pgb", "pgpool", "pgpool-source"], "sources": ["pgb:sa5cdd62a9242", "pgpool:s76141317a1b5", "pgpool-source:saf1078d5bb5c"], "status": "REASONED", "verify": [5]},
    "verify-server-tls": {"text": "SHOW SERVERS tls reports existing TLS or an empty plaintext connection, not whether plaintext would have been refused.", "components": ["pgb"], "sources": ["pgb:s91d48cfb22ae"], "status": "REASONED", "verify": [7]},
    "verify-force-user": {"text": "SHOW DATABASES force_user reveals forced identity; pool counts do not establish role preservation.", "components": ["pgb"], "sources": ["pgb:s91d48cfb22ae"], "status": "REASONED", "verify": [7]},
    "verify-console-unlisted": {"text": "An unlisted console user must fail at login with not allowed; SHOW VERSION success is exposure and transport/DNS/TLS failures are inconclusive.", "components": ["pgb", "pgb-source"], "sources": ["pgb:s91d48cfb22ae", "pgb-source:sd8ac14670f91"], "status": "REASONED", "verify": [8]},
    "verify-console-password": {"text": "The pgbadmin SHOW VERSION pair must succeed with the correct password and fail at login with the wrong one, both against dbname=pgbouncer.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242", "pgb:s91d48cfb22ae"], "status": "REASONED", "verify": [9]},
    "mfa": {"text": "Neither pooler provides native MFA or a PostgreSQL-wire TOTP dialogue; protect human host access separately.", "components": ["pgb", "pgpool"], "sources": ["pgb:sa5cdd62a9242", "pgpool:s7847f7feb03b"], "status": "REASONED"},
    "ldap-pam": {"text": "LDAP arrived in 1.25.0 and can appear in HBA; PAM is global and disables HBA selection, forwarding the supplied password instead of conducting an OTP challenge.", "components": ["pgb", "ldap-min", "pgb-source"], "sources": ["pgb:sa5cdd62a9242", "ldap-min:sa5cdd62a9242", "pgb-source:sb9455e4f6c90"], "status": "REASONED"},
    "mtls-hba": {"text": "Client verify-full and verify-ca are equivalent for certificates and can retain HBA/SCRAM; auth_type=cert takes the certificate username and replaces HBA selection.", "components": ["pgb"], "sources": ["pgb:sa5cdd62a9242"], "status": "REASONED"}
  }
}
---
# Connection poolers: PgBouncer and pgpool-II

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| packet-fix: 1.25.2 fixes CVE-2026-6664: an unauthenticated malformed SCRAM packet can crash older releases. | PgBouncer source and fixes 1.25.2 | REASONED |
| backend-fixes: 1.25.2 fixes CVE-2026-6665 from a malicious backend and CVE-2026-6666 from a backend error lacking SQLSTATE. | PgBouncer source and fixes 1.25.2 | REASONED |
| console-fix: 1.25.2 fixes CVE-2026-6667, which allowed any authorized console user to run KILL_CLIENT. | PgBouncer source and fixes 1.25.2 | REASONED |
| ini-comments: PgBouncer ini comments must start their own line; trailing # or ; becomes part of the value. | PgBouncer documentation unknown | REASONED |
| pgb-listener: Use private listen_addr and port 6432; the 1.26.0 unset default is Unix sockets only except systemd socket activation, whose ListenStream settings override listen_addr. | PgBouncer documentation unknown; PgBouncer listener source pgbouncer_1_26_0 | REASONED |
| pgpool-listener: Pgpool-II defaults to localhost:9999; listen_addresses is startup-only. | Pgpool-II documentation unknown | REASONED |
| pcp-listener: PCP independently defaults to localhost:9898 through startup-only pcp_listen_addresses and pcp_port. | Pgpool-II documentation unknown | REASONED |
| pcp-credentials: PCP uses separate username:MD5-digest entries in protected pcp.conf; pg_md5 -p prompts, and pool_passwd is not interchangeable. | Pgpool-II documentation unknown | REASONED |
| client-tls: PgBouncer client TLS defaults disabled; require with a key and certificate rejects non-TLS TCP clients while Unix sockets are exempt. | PgBouncer documentation unknown | REASONED |
| client-protocols: PgBouncer client_tls_protocols defaults to secure, meaning TLSv1.2 and TLSv1.3. | PgBouncer documentation unknown | REASONED |
| client-cert: client_tls_sslmode=verify-full and client_tls_ca_file require client certificates; protect the private key at mode 600. | PgBouncer documentation unknown | REASONED |
| pgpool-tls: Pgpool-II ssl defaults off; enabling it covers both hops but frontend TLS also needs ssl_key and ssl_cert. | Pgpool-II documentation unknown | REASONED |
| pgpool-hostssl: Pgpool-II host matches TLS and plaintext; hostssl requires ssl=on or is ignored, and unmatched connections are denied. | Pgpool-II documentation unknown | REASONED |
| backend-tls: PgBouncer server_tls_sslmode defaults prefer, permitting plaintext fallback without certificate checks; require omits certificate validation and verify-ca omits hostname checks. | PgBouncer documentation unknown | REASONED |
| backend-verify-full: Set PgBouncer server_tls_sslmode=verify-full with server_tls_ca_file to require TLS, a trusted certificate and matching hostname. | PgBouncer documentation unknown | REASONED |
| pgpool-ca: Pgpool-II ssl_ca_cert or ssl_ca_cert_dir enables backend CA verification; the documentation establishes no hostname check. | Pgpool-II documentation unknown | REASONED |
| pgpool-downgrade: Pgpool-II 4.7.2 continues plaintext if the backend declines TLS even with ssl_ca_cert; use a separately authenticated enforcing transport or PgBouncer verify-full. | Pgpool-II documentation unknown; Pgpool-II backend handshake 4.7.2 | REASONED |
| forced-user: A databases user= forces every client into one backend role; omitting it preserves client usernames and separate pools, with force_user visible in SHOW DATABASES. | PgBouncer documentation unknown | REASONED |
| backend-source: PostgreSQL HBA sees the pooler backend source after NAT; inet_client_addr returns that source or NULL on Unix sockets. A narrow address rule is not a process identity. | PgBouncer documentation unknown; PostgreSQL documentation unknown | REASONED |
| client-hba: PgBouncer auth_type=hba activates auth_hba_file for per-path peer/SCRAM/TLS rules; choosing a global method instead disables that policy. | PgBouncer documentation unknown | REASONED |
| pgpool-hba: Pgpool-II enable_pool_hba defaults false, leaving authentication to PostgreSQL; enabling it adds client policy without changing per-user/database pooling. | Pgpool-II documentation unknown | REASONED |
| pgpool-passwords: SCRAM needs matching plaintext or AES pool_passwd credentials, not MD5; pg_enc prompts, and AES requires OpenSSL plus service-owned mode-600 .pgpoolkey. | Pgpool-II documentation unknown | REASONED |
| pgpool-local: Local trust accepts any claimed database identity; unix_socket_directories defaults /tmp and every listed socket directory needs protection. | Pgpool-II documentation unknown | REASONED |
| hba-order: HBA first-match order governs access; explicit IPv4/IPv6 plaintext rejections stop later permissive rules, not earlier ones. | Pgpool-II documentation unknown; PostgreSQL documentation unknown | REASONED |
| client-metadata: application_name_add_host defaults 0; enabling it adds client address only at connection start and clients can later overwrite application_name. | PgBouncer documentation unknown | REASONED |
| log-prefix: PostgreSQL log_line_prefix defaults to %m [%p] without application name; include %a to log the diagnostic metadata. | PostgreSQL documentation unknown | REASONED |
| console-lists: The reserved pgbouncer database uses admin_users for full commands and stats_users for read-only SHOW; both default empty. | PgBouncer documentation unknown | REASONED |
| console-any: Configuration and usage docs disagree on any; 1.25.2 grants unlisted users console read access and lets clients claim an administrator name without authentication. | PgBouncer documentation unknown; PgBouncer source and fixes 1.25.2 | REASONED |
| weak-auth: trust and any do not authenticate, plain transmits a cleartext password and is deprecated, and auth_type defaults md5. | PgBouncer documentation unknown | REASONED |
| console-scram: Keep hba with SCRAM rules for pgbadmin and pgbmetrics; metrics credentials must satisfy both HBA and the console allowlist. | PgBouncer documentation unknown | REASONED |
| socket-bypass: The pgbouncer username can access the console passwordlessly over a Unix socket when the client UID equals the pooler process UID. | PgBouncer documentation unknown | REASONED |
| peer: Peer authentication uses the OS identity; a connection-string user name or password cannot supply that identity. | PgBouncer documentation unknown; PostgreSQL documentation unknown | REASONED |
| auth-file: Protect auth_file at mode 600; it can contain plaintext, MD5 or SCRAM secrets, and MD5 cannot satisfy client SCRAM. | PgBouncer documentation unknown | REASONED |
| scram-forward: Stored-SCRAM backend login needs client SCRAM, no forced user and identical secrets including salt and iteration count; peer does not provide the required exchange. | PgBouncer documentation unknown | REASONED |
| auth-query: auth_user enables lookup for users absent from auth_file; use a restricted SECURITY DEFINER function with trusted search_path, limited EXECUTE and database placement or auth_dbname. | PgBouncer documentation unknown | REASONED |
| password-expiry: CVE-2025-2291 was fixed in 1.24.1; custom auth_query must still check rolvaliduntil. | PgBouncer documentation unknown; PgBouncer password-expiry fix 1.24.1 | REASONED |
| verify-listeners: Inventory 6432/9999 on private addresses and PCP 9898 on loopback including IPv6; unexpected listeners are findings. | PgBouncer documentation unknown; Pgpool-II documentation unknown | REASONED |
| verify-client: Plaintext must fail for TLS, verified TLS with the correct password must succeed, and a wrong password must fail authentication; repeat for pgpool-II 9999. | PgBouncer documentation unknown; Pgpool-II documentation unknown; PostgreSQL documentation unknown | REASONED |
| password-delivery: Use mode-600 .pgpass for real passwords; PGPASSWORD can expose credentials through process environments. | PostgreSQL documentation unknown | REASONED |
| verify-pgpool: PGPOOL SHOW enable_pool_hba and ssl must both report on; inspect ordered HBA, reload errors and Unix-socket positive/negative credentials. | Pgpool-II documentation unknown | REASONED |
| verify-pcp: PCP read with correct prompted credentials must succeed and a wrong password must fail authentication; remote 9898 must be unreachable. | Pgpool-II documentation unknown | REASONED |
| verify-pgb-policy: RELOAD must succeed before SHOW CONFIG and disk-HBA inspection; confirm hba, TLS modes and pathname, then rerun connection tests. | PgBouncer documentation unknown; PostgreSQL documentation unknown | REASONED |
| hba-parser: PgBouncer 1.25.2 logs and skips malformed HBA lines without failing RELOAD; parser or access warnings leave verification incomplete. | PgBouncer source and fixes 1.25.2 | REASONED |
| verify-backend-observation: pg_stat_ssl reports negotiated encryption, not certificate enforcement; current_user and inet_client_addr identify backend role and source. | PostgreSQL documentation unknown | REASONED |
| verify-direct: Direct application-to-database access must fail HBA while permitted pooler egress and application-through-pooler controls succeed; disable GSS precedence and guard host/hostaddr. | PostgreSQL documentation unknown | REASONED |
| verify-backend-enforcement: Use fresh backend connections and restored positive controls: PgBouncer verify-full rejects untrusted CA, wrong hostname and TLS refusal; Pgpool-II only establishes CA rejection. | PgBouncer documentation unknown; Pgpool-II documentation unknown; Pgpool-II backend handshake 4.7.2 | REASONED |
| verify-server-tls: SHOW SERVERS tls reports existing TLS or an empty plaintext connection, not whether plaintext would have been refused. | PgBouncer documentation unknown | REASONED |
| verify-force-user: SHOW DATABASES force_user reveals forced identity; pool counts do not establish role preservation. | PgBouncer documentation unknown | REASONED |
| verify-console-unlisted: An unlisted console user must fail at login with not allowed; SHOW VERSION success is exposure and transport/DNS/TLS failures are inconclusive. | PgBouncer documentation unknown; PgBouncer source and fixes 1.25.2 | REASONED |
| verify-console-password: The pgbadmin SHOW VERSION pair must succeed with the correct password and fail at login with the wrong one, both against dbname=pgbouncer. | PgBouncer documentation unknown | REASONED |
| mfa: Neither pooler provides native MFA or a PostgreSQL-wire TOTP dialogue; protect human host access separately. | PgBouncer documentation unknown; Pgpool-II documentation unknown | REASONED |
| ldap-pam: LDAP arrived in 1.25.0 and can appear in HBA; PAM is global and disables HBA selection, forwarding the supplied password instead of conducting an OTP challenge. | PgBouncer documentation unknown; PgBouncer LDAP minimum 1.25.0; PgBouncer source and fixes 1.25.2 | REASONED |
| mtls-hba: Client verify-full and verify-ca are equivalent for certificates and can retain HBA/SCRAM; auth_type=cert takes the certificate username and replaces HBA selection. | PgBouncer documentation unknown | REASONED |
<!-- version-basis:end -->

A connection pooler sits in front of PostgreSQL and becomes the thing clients actually connect to. The pooler opens its own connections to the database and reuses them, so every control you configured on the database server ([postgresql.md](postgresql.md)) now governs the pooler's connection rather than the client's, and the pooler's own defaults decide what happens on both hops. Two of those defaults fail open: PgBouncer disables client TLS entirely, and its server-side `prefer` mode drops to plain TCP without an error when TLS is refused.

Default posture: bind the pooler to the interface the application uses and nothing wider, require TLS on the client hop, require a verified server certificate on the database hop, and leave the client's PostgreSQL role intact through the pooler.

Run a current PgBouncer. 1.25.2 fixes four advisories, and they need different things of an attacker. CVE-2026-6664 is the one an unauthenticated remote client can reach on its own: an integer overflow in packet parsing that crashes the process from a malformed SCRAM packet. CVE-2026-6665 needs a malicious PostgreSQL server, and CVE-2026-6666 a server that returns an error response with no SQLSTATE, so both are about what the pooler trusts on the database side rather than the client side. CVE-2026-6667 needs console access, which the vendor notes "itself requires authorization", and it let any console user run `KILL_CLIENT`. That last one matters to section 6 below, which treats `stats_users` as read-only; on an older build it is not.

## 1. What the pooler binds, and on which port

A comment in `pgbouncer.ini` must start its own line. The vendor is explicit: "The characters “;” and “#” are not recognized as special when they appear later in the line." A trailing comment therefore becomes part of the value and the setting is not what it looks like.

```ini
; /etc/pgbouncer/pgbouncer.ini
[pgbouncer]
; The application-facing address. Never * unless this is genuinely public.
; Unset is the default (as of 1.26.0), and it means Unix socket connections
; only, unless a build with systemd support is started by socket activation:
; then the .socket unit's ListenStream= lines decide, and listen_addr is ignored.
listen_addr = 10.0.0.5
listen_port = 6432
unix_socket_dir = /var/run/postgresql
```

Pgpool-II binds `localhost` by default on `port` 9999, and runs a separate control listener whose address is its own setting. Widening `listen_addresses` does not move PCP, and narrowing `listen_addresses` does not confine it either: `pcp_listen_addresses` is independent and also defaults to `localhost`. Both are set at server start only.

```ini
# /etc/pgpool-II/pgpool.conf
listen_addresses = '10.0.0.5'      # default is 'localhost'
port = 9999
pcp_listen_addresses = 'localhost' # independent of the line above; keep it here
pcp_port = 9898
```

PCP is an administration channel with its own credential file, `pcp.conf`, so treat 9898 the way you would treat an admin UI rather than a database port. Create a dedicated PCP administrator in it as `username:MD5-password-digest` (generate the digest with `pg_md5 -p`, which prompts rather than taking the password as an argument); use a unique password, restrict the file to the service account, and keep it out of source control and backups. PCP credentials are separate from database credentials, and `pcp.conf` is not interchangeable with `pool_passwd`.

## 2. Client TLS is off by default, and the database server's TLS does not cover it

PgBouncer's documentation is explicit: for `client_tls_sslmode`, "TLS connections are disabled by default." A database that requires `hostssl` for every remote client gains nothing from that requirement once a pooler is in front of it, because the only remote connection PostgreSQL sees is the pooler's. The clients are on a different, plaintext hop.

```ini
[pgbouncer]
; The default is disable. Over TCP, `require` makes PgBouncer refuse a client
; that will not negotiate TLS; connections over the Unix socket are exempt.
client_tls_sslmode = require
client_tls_key_file = /etc/pgbouncer/tls/pooler.key
client_tls_cert_file = /etc/pgbouncer/tls/pooler.crt
; client_tls_protocols defaults to `secure`, which is TLSv1.2 and TLSv1.3. Leave it.
```

To require client certificates as well, set `client_tls_sslmode = verify-full` and point `client_tls_ca_file` at the CA that issued them. Give the key file mode `600` and the pooler user's ownership, as with any private key ([self-signed.md](self-signed.md), [free-certificates.md](free-certificates.md)).

Pgpool-II uses one switch for both hops: `ssl` is "off" by default, and setting it on "enables the SSL for both the frontend and backend communications". Its documentation notes that `ssl_key` and `ssl_cert` must also be configured for frontend connections to work.

Turning it on makes TLS available and does not require it. A client that declines TLS still connects, because a `pool_hba.conf` `host` record "match[es] either SSL or non-SSL connection attempts". Requiring it means `hostssl` records, and those have their own trap in the other direction: "SSL must be enabled by setting the `ssl` configuration parameter. Otherwise, the `hostssl` record is ignored." A rule you wrote to require TLS is then simply not the rule being applied, and whichever other record matches decides instead. Section 5 has the file.

```ini
ssl = on                        # default is off; covers frontend and backend
ssl_key = '/etc/pgpool-II/tls/pooler.key'
ssl_cert = '/etc/pgpool-II/tls/pooler.crt'
```

## 3. The database hop, where `prefer` fails open

`server_tls_sslmode` decides what the pooler does on its way to PostgreSQL, and its default mode is `prefer`, which the documentation describes as: "TLS connection is always requested first from PostgreSQL. If refused, the connection will be established over plain TCP. Server certificate is not validated."

Two separate failures sit in that sentence. A server that stops offering TLS gets plain TCP instead of an error, and the certificate is not checked even when TLS succeeds. Raising the mode only fixes the first: `require` still says "Server certificate is not validated", and `verify-ca` still says "Server host name is not checked against certificate". Only `verify-full` requires both a valid certificate and a matching host name, which is what `sslmode=verify-full` bought you when the client spoke to PostgreSQL directly.

```ini
[pgbouncer]
; The default is prefer, which falls back to plain TCP and validates nothing.
; require and verify-ca each leave one half of that open.
server_tls_sslmode = verify-full
server_tls_ca_file = /etc/ssl/certs/postgres-ca.crt
```

Pgpool-II's `ssl_ca_cert` and `ssl_ca_cert_dir` are documented as CA files "which can be used to verify the backend server certificates", and with neither set there is nothing to verify against, so set one:

```ini
ssl_ca_cert = '/etc/ssl/certs/postgres-ca.crt'
```

The documentation describes CA verification and does not document a host name check on the backend connection, so do not assume the two products' strictest modes are equivalent: where a host name match matters, PgBouncer's `verify-full` is the one that states it.

One more thing is not established for pgpool-II, and this guide will not claim it. A CA file decides what happens when TLS is negotiated; it does not decide what happens when the backend declines TLS altogether. pgpool-II documents no setting equivalent to PgBouncer's `server_tls_sslmode = require`, and in 4.7.2 `pool_ssl_negotiate_clientserver()` continues without TLS when the backend answers that it will not, even with `ssl_ca_cert` set (the CA governs verification when TLS is negotiated, not whether TLS is negotiated). So this configuration does not meet this guide's requirement for mandatory, host-name-verified upstream TLS, and a backend `pg_hba.conf` rejection of plaintext does not prove pgpool-II refused the downgrade, because a hostile or misconfigured backend need not enforce PostgreSQL's intended policy. Use a separately authenticated transport that enforces TLS on that hop, or the PgBouncer configuration above; if you keep pgpool-II here, test the hop rather than assume it, and record plaintext fallback as a limitation rather than a pass.

## 4. A forced `user=` collapses every client into one PostgreSQL role

In the `[databases]` section, the `user` key changes who the pooler is on the database server: "If `user=` is set, all connections to the destination database will be done with the specified user, meaning that there will be only one pool for this database. Otherwise, PgBouncer logs into the destination database with the client user name, meaning that there will be one pool per user."

That single key undoes per-role access control. Every `GRANT` you wrote, every row-level policy keyed on `current_user`, and every per-user line in `pg_hba.conf` stops discriminating between clients, because there is only one role left. A forced user is a legitimate choice for a single-tenant service with one application account; it is a silent privilege merge anywhere else.

```ini
[databases]
; One pool per user, each client keeping its own role. Note the absent user=.
app = host=db.internal port=5432 dbname=app

; Compare. Every client of this entry becomes svc on the server, whatever they
; authenticated as at the pooler:
;   reports = host=db.internal port=5432 dbname=app user=svc
```

`SHOW DATABASES` reports this directly in its `force_user` column, which is what section 7 checks rather than counting pools.

## 5. `pg_hba.conf` now matches the pooler, so the client rules move into the pooler

PgBouncer opens its own server connections and reuses them across clients, so a server connection is not the client's connection and outlives it. PostgreSQL matches an address-based `pg_hba.conf` record against "the client machine address(es) that this record matches", and the address it sees is the source address of the pooler's backend connection, after any NAT on the way. That need not equal the pooler's listening address, so read it from the database rather than assuming it:

```sql
SELECT inet_client_addr();   -- run through the pooler, on the database server
```

Over a Unix socket the function returns NULL and the `local` rules apply instead.

A line such as `hostssl app app 10.0.0.0/24 scram-sha-256`, which used to restrict a range of clients, now matches whatever the pooler's backend connections come from. Narrowing it to that address is right, and it is worth being exact about what it buys: an address is not an identity. A `/24` still admits its whole range, and even a `/32` can be several workloads sharing one NAT egress, so the rule says where a connection came from and never which process opened it. Installing a pooler also does not stop anything else in the old range connecting directly. Narrow the database server's rules to the address you actually read, put the client-facing restriction where the clients now arrive, and treat the two as separate jobs rather than one moved.

On the database server:

```
# TYPE     DATABASE  USER  ADDRESS        METHOD
hostssl    app       all   10.0.0.5/32    scram-sha-256    # the address the pooler's backend connections come from
```

At the pooler, `auth_type = hba` reads a `pg_hba`-style file so the same per-path distinctions apply to client connections. The documentation gives exactly this use: "This allows different authentication methods for different access paths, for example: connections over Unix socket use the peer authentication method, connections over TCP must use TLS."

```ini
[pgbouncer]
auth_type = hba
auth_hba_file = /etc/pgbouncer/pg_hba.conf
auth_file = /etc/pgbouncer/userlist.txt
```

```
# /etc/pgbouncer/pg_hba.conf
local      all       all                  peer
hostssl    app       app   10.0.0.0/24    scram-sha-256
```

Pgpool-II has the same file and does not read it by default: `enable_pool_hba` is documented as "Default is false", and with it off "the client authentication method is completely managed by PostgreSQL". That does not merge your clients into one role the way a forced `user=` does, because pgpool-II pools per user and database and the backend still authenticates each one. What it means is narrower and still worth fixing: pgpool-II applies no client-facing policy of its own, so it will not refuse a plaintext connection or a client from an address you never meant to serve.

```ini
enable_pool_hba = on            # default is false
pool_passwd = 'pool_passwd'     # a path, relative to the directory holding this file
```

Setting that path does not create the entries. For `scram-sha-256` the vendor's steps are to "Create pool_passwd file entry for database user and password in plain text or AES encrypted format", where `pg_enc` writes the AES form, and it warns that "User name and password must be identical to those registered in the PostgreSQL server". An `md5`-format entry cannot serve SCRAM. AES also needs an OpenSSL-enabled build and a decryption key, `.pgpoolkey`, which pgpool-II requires at mode `600` and owned by the service user; generate the encrypted entries with `pg_enc -m -f /etc/pgpool-II/pgpool.conf -u app -p` run as the service identity, which prompts for the password rather than taking it as an argument. Restrict `pool_passwd` to the service account and keep both files and any backups out of the repository ([secrets.md](secrets.md)). Reload after changing either side.

```
# /etc/pgpool-II/pool_hba.conf
# `host` matches SSL and non-SSL alike, so requiring TLS means hostssl rather than host.
# The two reject lines are not redundant with the default: an unmatched connection is denied
# anyway, but a later permissive rule would match first, and these stop that silently.
local      all       all                        scram-sha-256
hostssl    all       app   10.0.0.0/24          scram-sha-256
hostnossl  all       all   0.0.0.0/0            reject
hostnossl  all       all   ::/0                 reject
```

Three things about that file are easy to get wrong. `local ... trust` is the tempting first line and it is a hole: the vendor says `trust` admits a client under "whatever database user name they specify", and the Unix socket lives in `unix_socket_directories`, which defaults to `/tmp`, so any local account can claim any database identity. Authenticate the local path too, or move the socket somewhere only the application user can reach. The setting is `unix_socket_directories`, which takes a comma-separated list, so restricting it means covering every directory in that list rather than one. The `0.0.0.0/0` rejection covers IPv4 only, which is why the second one is there. And records are read in order, so a permissive rule above these wins; the rejections protect against what comes after them, not before.

A `hostssl` record is ignored entirely while `ssl` is off. That does not by itself open the plaintext path, because "if no record matches, access is denied"; what it means is that the rule you wrote to require TLS is not the rule being applied, so whichever other record does match is deciding instead. Set `ssl = on` first and confirm it took effect.

Because the server no longer sees the client, its logs no longer identify one either. `application_name_add_host` adds "the client host address and port to the application name setting set on connection start", and its default is `0`. It is diagnostic metadata rather than an audit trail: the same page says the value applies "only at the start of a connection" and that after a later `SET application_name` "PgBouncer does not change it again", so a client can overwrite it. PostgreSQL's `log_line_prefix` defaults to `'%m [%p] '`, which carries no application name at all, so turning the setting on changes nothing in the log until `%a` is in the prefix.

```ini
; The default is 0.
application_name_add_host = 1
```

```
# postgresql.conf, on the database server
log_line_prefix = '%m [%p] %a '
```

## 6. The admin console, and the authentication methods that are not authentication

PgBouncer reserves one database name for its control channel: "The database name 'pgbouncer' is reserved for the admin console and cannot be used as a key here." Access is governed by `admin_users` for full commands and `stats_users` for read-only `SHOW` commands, both of which default to empty.

`auth_type = any` removes that gate, and the vendor's two pages disagree about how far. The configuration page says `admin_users` is "Ignored when `auth_type` is `any`, in which case any user name is allowed in as admin". The usage page says "Only users listed in the configuration parameters `admin_users` or `stats_users` are allowed to log in to the console. (Except when `auth_type=any`, then any user is allowed in as a `stats_user`.)" The released 1.25.2 source agrees with the usage page: admin status is granted to names matching `admin_users`, and an `any` connection that matches neither list is admitted without it. Either way `any` is unsafe, because an unauthenticated stranger gets console read access and can also simply claim a listed administrator's name, and this guide states the disagreement rather than picking the reading that suits it. The practical consequence matters for section 7: under `any`, a command with no administrator gate of its own, such as `SHOW VERSION`, SUCCEEDS for a user on neither list. A probe that expects a rejection has to tell one at login from one at the command, because only the first means the console is closed.

The other weak values are described plainly by the vendor: `trust` is "No authentication is done", `any` is "Like the trust method, but the user name given is ignored", and `plain` sends "The clear-text password ... over the wire" and is marked deprecated. The default is `md5`.

Keep `auth_type = hba` from section 5. Setting `auth_type = scram-sha-256` here instead would be a downgrade rather than an upgrade, because `auth_hba_file` is only consulted under `hba`, so the client-range restriction you wrote in section 5 would stop applying. Put the method in the HBA file:

```
# /etc/pgbouncer/pg_hba.conf
hostssl    pgbouncer  pgbadmin    10.0.0.0/24   scram-sha-256
hostssl    pgbouncer  pgbmetrics  10.0.0.0/24   scram-sha-256
hostssl    app        app         10.0.0.0/24   scram-sha-256
local      all        all                       peer
```

```ini
[pgbouncer]
admin_users = pgbadmin
stats_users = pgbmetrics
```

Provision `pgbmetrics` with a SCRAM-compatible credential in `auth_file`, or through the configured `auth_user` lookup; its TCP connection must pass both the HBA rule above and the console allowlist.

One account bypasses all of this by design, and it is worth knowing about: the documentation states that "the user name `pgbouncer` is allowed to log in without password, if the login comes via the Unix socket and the client has same Unix user UID as the running process". Anyone who can run a process as the pooler's Unix user already has the console.

The `local ... peer` line above has the same shape and the same requirement. `peer` takes the identity from the operating system, so `user=pgbadmin` in a connection string does not supply it: the command has to run as an OS user that maps to `pgbadmin`, or it is rejected whatever password it carries.

`auth_file` "may contain both MD5-encrypted and plain-text passwords", so it is a secret file regardless of what you put in it: mode `600`, owned by the pooler's user, and out of the repository ([secrets.md](secrets.md)). Choosing `scram-sha-256` in the HBA file constrains what has to be in there: the documented format is `"username" "password"` where the second field is "either a plain-text, a MD5-hashed password, or a SCRAM secret", and a SCRAM secret is `SCRAM-SHA-256$<iterations>:<salt>$<storedkey>:<serverkey>`. Copying a stored secret across means copying it exactly, salt and iteration count included, or the two sides do not agree. Stored-SCRAM backend login has further prerequisites: SCRAM on the client connection, no forced `[databases] user=`, and identical secrets on both sides; local `peer` authentication does not supply the SCRAM exchange this forwarding needs, and an MD5 entry cannot satisfy a client speaking SCRAM. `auth_query` avoids the file for user passwords by reading them from the database, and the documentation warns that "Direct access to `pg_authid` requires admin rights. It's preferable to use a non-superuser that calls a SECURITY DEFINER function instead." Set `auth_user` to activate the lookup for users absent from `auth_file` (existing `auth_file` entries take precedence). Give the definer function a trusted `search_path`, revoke its execution from `PUBLIC` and grant it only to the lookup role, and install it in each queried database or set `auth_dbname`. Keep the password-expiry check: CVE-2025-2291, fixed in 1.24.1, allowed expired passwords because PgBouncer's `auth_query` did not honour a role's `VALID UNTIL`. The default query was corrected; a custom query must also check `rolvaliduntil`.

## 7. Verify (REASONED: expected pooler outcomes follow the cited documentation and pinned sources; no running pooler/PostgreSQL deployment is available in the authoring environment)

```bash
ss -tlnp   # read every listener; 6432/9999/9898
```

Read that as an inventory rather than a pass. The application ports (`6432`, `9999`) must each be on `127.0.0.1` or a private address; the PCP control port (`9898`) must be loopback-only, IPv6 included, because section 1 keeps `pcp_listen_addresses` on `localhost`. An entry showing `0.0.0.0:9898`, `[::]:9898`, or `9898` on a private address is section 1 not applied, whatever `listen_addresses` says, and any listener you cannot account for is its own finding.

The client hop takes three commands, not one. A single failing connection proves nothing, because a wrong password fails the same way as a refused plaintext connection; and a passing pair proves less than it looks, because a `trust` method in the HBA file lets any password through. Put the real password in `~/.pgpass` at mode `600` rather than the environment, which PostgreSQL says is "not recommended for security reasons" because some systems expose a process's environment to other users.

```bash
# ~/.pgpass, mode 600: hostname:port:database:username:password
# pooler.internal:6432:app:app:REPLACE_WITH_THE_APP_PASSWORD
#
# Self-contained: the TLS requirement is written literally in each connection string (no shared variable a
# later block could inherit empty), and the target host is a guarded positional parameter. Paste the block.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_POOLER_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the pooler host; not probing'; exit 2 ;; esac
  # 1. Must FAIL, and the error must name TLS rather than authentication.
  psql -X "host=$1 port=6432 dbname=app user=app sslmode=disable" -c 'SELECT 1;'
  # 2. Must SUCCEED. The control: the credential is good, so the failure above was the TLS requirement,
  #    not a bad password.
  psql -X "host=$1 port=6432 dbname=app user=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SELECT 1;'
  # 3. Must FAIL on authentication. Without this, a `trust` method in auth_hba_file passes both above while
  #    checking no password at all. The wrong password is a literal here, not a real secret.
  PGPASSWORD=definitely-not-the-password psql -X "host=$1 port=6432 dbname=app user=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SELECT 1;'
)
```

Run the same three against pgpool-II on port 9999 where that is the pooler in front, because nothing above tests its listener. pgpool-II also needs its own effective-policy and admin-channel checks, because the client probes exercise one path and the console inspection below is PgBouncer-specific:

```bash
# REASONED: pgpool-II policy and PCP checks follow the cited pgpool-II documentation;
# no running pgpool-II/PCP deployment is available in the authoring environment.
# Effective pgpool-II policy (through the pooler on 9999):
psql -X "host=pooler.internal port=9999 dbname=app user=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" \
  -c 'PGPOOL SHOW enable_pool_hba;' -c 'PGPOOL SHOW ssl;'
grep -vE '^\s*(#|$)' /etc/pgpool-II/pool_hba.conf   # active rules, in order; first match wins
# Not demonstrated: no running pgpool-II/PCP deployment in the authoring environment.
# Correct credentials must succeed; a wrong password must be refused on
# authentication, and any other error leaves verification incomplete.
# PCP admin channel on loopback: an authenticated read must succeed, a wrong password must be refused.
pcp_node_count -h 127.0.0.1 -p 9898 -U pcpadmin -W   # enter the correct PCP password: succeeds
pcp_node_count -h 127.0.0.1 -p 9898 -U pcpadmin -W   # enter a wrong password: must be refused on authentication
```

`enable_pool_hba` must read `on` and `ssl` must read `on`, or the rules in `pool_hba.conf` are not the policy being applied; inspect the reload logs for parse or file-access errors, confirm remote sources cannot reach 9898 at all, and test the Unix-socket route with valid and invalid credentials. Restart pgpool-II after changing any setting documented as startup-only.

Three commands from one address prove one path. They say nothing about a second `hostssl` line further down the file that ends in `trust`, and nothing at all if `auth_type` is not `hba`, because `auth_hba_file` is then never read and the client-range restriction you wrote is inert while still sitting in the repository looking applied. So read the effective configuration as well as probing it:

```bash
# A failed RELOAD must stop the block, not be masked by a following grep's exit status.
(
  psql -X -w -v ON_ERROR_STOP=1 \
    "host=/var/run/postgresql port=6432 dbname=pgbouncer user=pgbadmin" \
    -c 'RELOAD;' -c 'SHOW CONFIG;' || exit 1
  # Inspect auth_type, auth_hba_file, client_tls_sslmode and server_tls_sslmode above.
  # Then read the effective HBA file (only reached if the reload succeeded):
  grep -vE '^\s*(#|$)' /etc/pgbouncer/pg_hba.conf
)
```

`auth_type` must read `hba` for the file below it to matter. Read the rules in order: the first match wins, so a `trust` line decides for every path that reaches it before something stricter does, while one sitting below a rejection that already covers the same path is unreachable. Judge each line by what reaches it, not by its presence.

The `RELOAD` is not decoration. `SHOW CONFIG` reports the running settings and the file read reports the disk, and those are two different things: PgBouncer evaluates the HBA rules it parsed at load, so an edited file that has not been reloaded leaves the old rules deciding while the clean file sits on disk looking correct. A probe run against that state passes and certifies nothing. Reload first, or treat the file read as evidence about the next restart rather than about now. A successful reload is necessary but not sufficient: PgBouncer logs and skips a malformed HBA line and does not fail the reload for it, so an intended restrictive rule can vanish while a later permissive one still applies. Inspect the reload logs for HBA parsing and file-access errors, confirm the effective HBA pathname, and re-run the positive and negative connection tests after reloading; any parser warning leaves verification incomplete.

For the database hop, know what the probe can and cannot tell you:

```bash
psql -X "host=pooler.internal port=6432 dbname=app user=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c "SELECT current_user, inet_client_addr(), ssl FROM pg_stat_ssl JOIN pg_stat_activity USING (pid) WHERE pid = pg_backend_pid();"
```

`ssl` reports whether the pooler-to-PostgreSQL connection uses SSL. It does not report whether the pooler validated the certificate, so a `t` here is consistent with `server_tls_sslmode = require`, which validates nothing. Certificate validation cannot be observed from the client at all: for PgBouncer configured with `server_tls_sslmode = verify-full`, test enforcement by presenting the pooler with a certificate that should fail, one signed by an untrusted CA and one valid but issued for a different host name, and confirm that it refuses both. It has to be a fresh BACKEND connection rather than a fresh client one: a new client is routinely handed a server connection that was opened earlier, under the old certificate. `inet_client_addr()` is the address section 5 tells you to write into `pg_hba.conf`.

These direct-database checks are REASONED from the cited PostgreSQL HBA documentation, not demonstrated: the authoring environment lacks a running pooler/PostgreSQL deployment with distinct application and pooler source addresses; an exposed database admits the direct application connection while the intended HBA policy rejects it and the permitted controls succeed, and a password, certificate, DNS, or connection failure is inconclusive. Test the bypass the pooler cannot prevent. From an application source that is supposed to go through the pooler, connect to the DATABASE directly with the same credentials and require a rejection, then confirm the permitted pooler egress still connects and the application still connects through the pooler. Give the real destination as `hostaddr` while keeping the certificate host name in `host`, and guard the substituted values:

```bash
# REASONED: direct-database isolation follows the cited PostgreSQL HBA documentation;
# no running pooler/PostgreSQL deployment with distinct application and pooler source addresses is available.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DB_HOSTNAME' 'REPLACE_WITH_DB_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'exactly two values are required; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute a nonempty hostname; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute a nonempty address; not probing'; exit 2 ;; esac
  # From a client that must NOT bypass the pooler: a direct database connection must be REFUSED by pg_hba.
  # gssencmode=disable so libpq cannot prefer GSS and take an HBA rejection on that path for proof while a
  # hostssl path stays open.
  psql -X "host=$1 hostaddr=$2 port=5432 dbname=app user=app gssencmode=disable sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SELECT 1;'
)
```

These backend tests are REASONED from the cited PgBouncer and Pgpool-II TLS documentation, not demonstrated: the authoring environment lacks an isolated running pooler/PostgreSQL deployment. Force and identify a fresh backend connection before each attempt; establish a trusted-certificate control, change one condition, repeat the query above through the relevant pooler port, and restore the control after each case. PgBouncer with `server_tls_sslmode = verify-full` must reject an untrusted CA, a valid certificate for the wrong host name, and a backend that declines TLS. Pgpool-II 4.7.2 with `ssl_ca_cert` must reject an untrusted CA, but does not enforce backend host-name matching or mandatory TLS; record those two as limitations.

Ask the pooler what it negotiated, and what identity it forces:

```bash
psql -X "host=/var/run/postgresql port=6432 dbname=pgbouncer user=pgbadmin" -c 'SHOW SERVERS;' -c 'SHOW DATABASES;'
```

The `tls` column is "A string with TLS connection information, or empty if not using TLS". An empty `tls` on a server row is a plaintext database hop happening right now, which is section 3 caught in the act; it does not by itself distinguish the `prefer` fallback from TLS being disabled outright or from a Unix-socket backend. A non-empty one is weaker still: it says this connection negotiated TLS, not that a plaintext one would have been refused. These are snapshots of established connections, and enforcement is what the configuration file says.

`SHOW DATABASES` answers section 4 directly through its `force_user` column, which names the forced identity where one is set. That is a better test than counting pools, because a pool count only reflects which users have happened to connect.

Finally, the console must reject a user on neither list, and it must reject it at login:

```bash
psql -X "host=pooler.internal port=6432 dbname=pgbouncer user=app sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SHOW VERSION;'
```

That has to fail while connecting, with `not allowed`. `SHOW VERSION` is chosen because it has no administrator gate of its own, so it cannot fail for the wrong reason: if the connection is accepted, the command succeeds and prints a version, which is exactly what `auth_type = any` produces. Read the outcome in three ways rather than two. A refusal at login is the pass. A version printed is a failure, and `auth_type` is the first thing to check. Anything else, a DNS failure, a TLS failure, a refused connection, is inconclusive and has to be resolved before the probe means anything.

None of this tests the privileged name, and testing an unlisted one only proves the list is consulted. `admin_users` is an allowlist of names and says nothing about whether those names have to prove anything, so run the pair against the console itself rather than reusing the application query:

```bash
psql -X "host=pooler.internal port=6432 dbname=pgbouncer user=pgbadmin sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SHOW VERSION;'
PGPASSWORD=definitely-not-the-password psql -X "host=pooler.internal port=6432 dbname=pgbouncer user=pgbadmin sslmode=verify-full sslrootcert=/etc/ssl/certs/ca.crt" -c 'SHOW VERSION;'
```

The first must succeed and the second must be refused at login. Both have to name `dbname=pgbouncer`: changing only the user name on the application probe leaves it asking the `app` database for `SELECT 1`, which tests nothing about the console.

The console commands over the Unix socket are a different path with a different requirement, and `peer` there takes the identity from the operating system.

MFA: neither pooler adds a factor of its own, and the PostgreSQL wire protocol has no TOTP dialogue, so there is nothing here to turn on and the honest answer is that this is not where a second factor goes.

The hooks that exist come with conditions worth knowing before you reach for them. PgBouncer's `auth_type` accepts `pam` and `ldap`, and `ldap` arrived in 1.25.0. Only `ldap` can be named inside `auth_hba_file`; selecting `pam` means setting it globally, which stops the HBA file being consulted and takes the client-range restriction of section 5 with it. PAM is also not an interactive one-time-password conversation here: the released implementation answers a hidden prompt with the same password the client already supplied, so it forwards a credential rather than conducting a challenge.

For a possession factor, `client_tls_sslmode = verify-full` with `client_tls_ca_file` requires a client certificate while leaving `auth_type = hba` and SCRAM in place, which is usually what you want. On that client-facing setting `verify-full` and `verify-ca` are the same thing; taking the user name from the certificate is what `auth_type = cert` does, and that, like `pam`, replaces HBA selection rather than adding to it.

Put the human paths to the host behind MFA per [mfa.md](mfa.md).

## Common mistakes

- Writing a trailing `;` or `#` comment on a `pgbouncer.ini` line. The vendor does not treat either as special after the start of a line, so the comment becomes part of the value and the setting silently is not what it reads as.
- Configuring TLS carefully on PostgreSQL, then putting a pooler in front of it with `client_tls_sslmode` left at its default, so every client connection is plaintext and the database's `hostssl` rules only ever match the pooler.
- Leaving `server_tls_sslmode` at `prefer` and reading a successful connection as an encrypted one. It falls back to plain TCP without an error, and it validates no certificate in any case.
- Treating `require` or `verify-ca` as equivalent to the client-side `sslmode=verify-full` they replaced. Neither checks the host name.
- Widening the database server's `pg_hba.conf` because the old client ranges stopped matching, or assuming that narrowing it to the pooler stops anything else in the old range connecting directly.
- Setting `user=` on a `[databases]` entry for convenience, which merges every client into one role and disables per-role privileges on the server.
- Switching `auth_type` from `hba` to `scram-sha-256` to "tighten" it, which stops `auth_hba_file` being read and drops the client-range restriction with it.
- Writing a `hostssl` rule in `pool_hba.conf` while `ssl` is still off. The record is ignored, so the rule you wrote to require TLS is not the rule being applied; whichever other record matches decides instead, and an unmatched connection is denied.
- Putting a database password in `PGPASSWORD` in a shell you are pasting commands into. Use `~/.pgpass` at mode `600`.
- Setting `listen_addresses` in `pgpool.conf` and expecting PCP to follow. `pcp_listen_addresses` is a separate setting, and `enable_pool_hba` is off by default, so pgpool-II authenticates nobody of its own until you turn it on.

## Sources (checked September 2026)

- PgBouncer configuration, including the ini comment rule, `listen_addr`, `listen_port`, `client_tls_sslmode`, `server_tls_sslmode`, `auth_type`, `auth_file`, `auth_query`, `admin_users`, `stats_users`, `application_name_add_host`, and the `[databases]` `user` key (LDAP since 1.25.0; auth_query fix 1.24.1): https://www.pgbouncer.org/config.html
- PgBouncer `listen_addr` default `""`, and the socket-activation path that ignores it (pinned tag pgbouncer_1_26_0): https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/src/main.c#L292 and https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/src/pooler.c#L495-L498, with `sd_listen_fds()` defined as `(0)` in builds without systemd support: https://github.com/pgbouncer/pgbouncer/blob/pgbouncer_1_26_0/include/bouncer.h#L54-L62
- PgBouncer usage, the admin console and its `SHOW` commands, including who `auth_type=any` admits and the passwordless Unix-socket login: https://www.pgbouncer.org/usage.html
- PgBouncer changelog, for CVE-2026-6664, CVE-2026-6665, CVE-2026-6666 and CVE-2026-6667, all fixed in 1.25.2: https://www.pgbouncer.org/changelog.html
- PgBouncer features and pooling modes: https://www.pgbouncer.org/features.html
- Pgpool-II connection settings (`listen_addresses`, `port`, `pcp_listen_addresses`, `pcp_port`, `enable_pool_hba`): https://www.pgpool.net/docs/latest/en/html/runtime-config-connection.html
- Pgpool-II SSL settings (`ssl`, `ssl_cert`, `ssl_key`, `ssl_ca_cert`, `ssl_ca_cert_dir`): https://www.pgpool.net/docs/latest/en/html/runtime-ssl.html
- Pgpool-II pool_hba.conf: https://www.pgpool.net/docs/latest/en/html/auth-pool-hba-conf.html
- Pgpool-II pcp.conf: https://www.pgpool.net/docs/latest/en/html/configuring-pcp-conf.html
- PostgreSQL pg_hba.conf, for what an address record matches: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html
- PostgreSQL connection information functions (`inet_client_addr`): https://www.postgresql.org/docs/current/functions-info.html
- PostgreSQL statistics views, for what `pg_stat_ssl.ssl` does and does not report: https://www.postgresql.org/docs/current/monitoring-stats.html
- PostgreSQL logging configuration (`log_line_prefix`): https://www.postgresql.org/docs/current/runtime-config-logging.html
- PostgreSQL peer authentication, for why a console user name is not an OS identity: https://www.postgresql.org/docs/current/auth-peer.html
- PostgreSQL environment variables, on `PGPASSWORD` being "not recommended for security reasons": https://www.postgresql.org/docs/current/libpq-envars.html
- PostgreSQL password file, for the `~/.pgpass` format and its permission requirement: https://www.postgresql.org/docs/current/libpq-pgpass.html
- psql, for what `-c` accepts and what `-X` suppresses: https://www.postgresql.org/docs/current/app-psql.html
- PostgreSQL libpq connection parameters (`host`, `hostaddr`, `sslmode`, and GSS encryption precedence): https://www.postgresql.org/docs/current/libpq-connect.html
- PgBouncer 1.25.2 console source, which is what settles the `auth_type = any` disagreement above: https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/admin.c
- PgBouncer 1.25.2 PAM source, for what `pam` does with the supplied password: https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/pam.c
- Pgpool-II parameter syntax, which unlike pgbouncer.ini does treat a trailing `#` as a comment: https://www.pgpool.net/docs/latest/en/html/config-setting.html
- Pgpool-II authentication methods: https://www.pgpool.net/docs/latest/en/html/auth-methods.html
- Pgpool-II 4.7.2 backend SSL handshake (`pool_ssl_negotiate_clientserver` continues without TLS when the backend declines): https://raw.githubusercontent.com/pgpool/pgpool2/V4_7_2/src/utils/pool_ssl.c
- Pgpool-II AES-encrypted passwords and `.pgpoolkey` (`pg_enc`, required key-file permissions): https://www.pgpool.net/docs/latest/en/html/auth-aes-encrypted-password.html
- Pgpool-II PCP common options (`-U`, the `-W` password prompt) used by `pcp_node_count`: https://www.pgpool.net/docs/latest/en/html/pcp-common-options.html
- PgBouncer 1.25.2 HBA parser (logs and skips a malformed line without failing the reload): https://raw.githubusercontent.com/pgbouncer/pgbouncer/pgbouncer_1_25_2/src/hba.c
