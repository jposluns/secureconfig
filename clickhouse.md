---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "a04f8a9df4b4a7bd2adf972e0f55453e67d1b1505c6ca31521b47f0b53e3723e",
  "components": {
    "docs": {
      "name": "ClickHouse documentation",
      "basis": "unknown",
      "sources": {
        "sd76f8dcfe61f": "https://clickhouse.com/docs/reference/settings/server-settings/settings/listen#listen_host",
        "s8d4bf69ecb45": "https://clickhouse.com/docs/get-started/setup/self-managed/docker#managing-default-user",
        "sd891987369e6": "https://clickhouse.com/docs/concepts/features/security/network-ports",
        "sd156261650ee": "https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver#interserver_listen_host",
        "sfd95effa4d9b": "https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files",
        "s2ee7469699a5": "https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users",
        "sc7a527d82e50": "https://clickhouse.com/docs/reference/statements/create/user",
        "s324525fe685e": "https://clickhouse.com/docs/concepts/features/security/access-rights",
        "sa133286c107f": "https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_path",
        "s38015aaf3159": "https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_directories",
        "s6b90e2c1092e": "https://clickhouse.com/docs/reference/statements/grant",
        "s25556959ddfa": "https://clickhouse.com/docs/reference/statements/create/role",
        "sd137a7449c51": "https://clickhouse.com/docs/reference/statements/set-role",
        "s26cbbfd750d7": "https://clickhouse.com/docs/reference/statements/create/settings-profile",
        "sae310a80cd58": "https://clickhouse.com/docs/concepts/features/configuration/settings/constraints-on-settings",
        "s02fa1a2ea84b": "https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage",
        "sfd00c9c1a9a1": "https://clickhouse.com/docs/reference/settings/session-settings/max-execution#max_execution_time",
        "sf738cc05299a": "https://clickhouse.com/docs/reference/statements/create/quota",
        "s8d50f48221f7": "https://clickhouse.com/docs/concepts/features/configuration/server-config/quotas",
        "sad8b1924b3ce": "https://clickhouse.com/docs/concepts/features/configuration/settings/permissions-for-queries",
        "sd78f0c21ad7b": "https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls",
        "s4e31b63753ab": "https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-https",
        "s6255e1dd351e": "https://clickhouse.com/docs/reference/settings/server-settings/settings/other#openSSL",
        "s5b738c4b057c": "https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-http",
        "s01de3f86a875": "https://clickhouse.com/docs/concepts/features/interfaces/client",
        "s4d5d0964fabb": "https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users#totp-authentication-configuration",
        "s8db5ea270091": "https://clickhouse.com/docs/reference/functions/table-functions/url",
        "s78d0544db7eb": "https://clickhouse.com/docs/reference/functions/table-functions/file",
        "sbb755048d8c0": "https://clickhouse.com/docs/reference/functions/table-functions/remote",
        "s32fae5e0bf85": "https://clickhouse.com/docs/reference/statements/create/dictionary/sources/http",
        "saa2d39175e49": "https://clickhouse.com/docs/reference/settings/server-settings/settings/remote#remote_url_allow_hosts",
        "scce6af3a28a6": "https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_improvements",
        "sc172859d92a4": "https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_scripts_path",
        "sba7a666c54ee": "https://clickhouse.com/docs/reference/settings/server-settings/settings/user-defined#user_defined_executable_functions_config",
        "s0be4d04f7874": "https://clickhouse.com/docs/reference/functions/table-functions/executable",
        "s247524807405": "https://clickhouse.com/docs/reference/functions/regular-functions/udf",
        "s3ebb0f281977": "https://clickhouse.com/docs/reference/system-tables/overview",
        "sc67e973f5ab7": "https://clickhouse.com/docs/reference/settings/server-settings/settings/query",
        "s41bbbde68a83": "https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/mergetree",
        "s67072795b79e": "https://clickhouse.com/docs/reference/settings/session-settings/log-queries",
        "scfe38c988cb3": "https://clickhouse.com/docs/reference/system-tables/query_log",
        "sde710fc1a785": "https://clickhouse.com/docs/reference/system-tables/session_log",
        "s1b518ea764fb": "https://clickhouse.com/docs/reference/statements/system#system-flush-logs",
        "s5b17854afa6d": "https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/database-audit-log",
        "s6298fa9f4719": "https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/console-audit-log",
        "s3919007d159e": "https://clickhouse.com/docs/concepts/features/interfaces/http",
        "s201098033e10": "https://clickhouse.com/docs/reference/functions/aggregate-functions/uniqExact",
        "sde8cc2811bb5": "https://clickhouse.com/docs/reference/statements/create/table",
        "s463e85e20441": "https://clickhouse.com/docs/reference/engines/table-engines/log-family/tinylog",
        "s2d3e9d1310e4": "https://clickhouse.com/docs/reference/statements/show"
      }
    },
    "config": {
      "name": "ClickHouse server config source",
      "basis": "9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6",
      "sources": {
        "s5bcf465239d6": "https://raw.githubusercontent.com/ClickHouse/ClickHouse/9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6/programs/server/config.xml"
      }
    },
    "users": {
      "name": "ClickHouse users source",
      "basis": "b40982f9416bb4bc2d423d7e75ec384e79494b99",
      "sources": {
        "s20eec88438df": "https://raw.githubusercontent.com/ClickHouse/ClickHouse/b40982f9416bb4bc2d423d7e75ec384e79494b99/programs/server/users.xml"
      }
    },
    "totp": {
      "name": "ClickHouse TOTP introduction",
      "basis": "26.2",
      "sources": {
        "sf7b9d01ede30": "https://clickhouse.com/blog/clickhouse-release-26-02"
      }
    },
    "sources": {
      "name": "ClickHouse privilege registry",
      "basis": "37c6c8c9bfc1de323e9a27711c5649352364bcba",
      "sources": {
        "s04a87783572d": "https://raw.githubusercontent.com/ClickHouse/ClickHouse/37c6c8c9bfc1de323e9a27711c5649352364bcba/src/Access/Common/AccessType.h"
      }
    },
    "curl": {
      "name": "curl documentation",
      "basis": "unknown",
      "sources": {
        "s5345a985007a": "https://curl.se/docs/manpage.html#-H"
      }
    },
    "roles": {
      "name": "ClickHouse role source",
      "basis": "1163c482760fb0204e40f8fb5d81ffa1272bc9ea",
      "sources": {
        "sa66cde5c2b6e": "https://raw.githubusercontent.com/ClickHouse/ClickHouse/1163c482760fb0204e40f8fb5d81ffa1272bc9ea/src/Interpreters/Access/InterpreterSetRoleQuery.cpp"
      }
    }
  },
  "claims": {
    "listen-default": {"text": "Shipped config tries IPv4/IPv6 localhost; widening listen_host can expose services; inspect merged overrides.", "components": ["docs", "config"], "sources": ["docs:sd76f8dcfe61f", "config:s5bcf465239d6"], "status": "REASONED"},
    "default-user": {"text": "Upstream default has empty password, ::/0 origins and access_management; full bootstrap needs additional capabilities.", "components": ["users"], "sources": ["users:s20eec88438df"], "status": "REASONED"},
    "docker-default": {"text": "Official image disables default network access when all three documented initialization variables are unset.", "components": ["docs"], "sources": ["docs:s8d4bf69ecb45"], "status": "REASONED"},
    "ports": {"text": "8123 HTTP, 9000 native, 9004 MySQL, 9005 PostgreSQL and 9009 interserver are documented, not necessarily active.", "components": ["docs"], "sources": ["docs:sd891987369e6", "docs:sd156261650ee"], "status": "REASONED"},
    "interserver-bind": {"text": "interserver_listen_host defaults to listen_host but can independently widen replica exposure.", "components": ["docs"], "sources": ["docs:sd156261650ee"], "status": "REASONED"},
    "xml-merge": {"text": "config.d/users.d retain clickhouse roots; remove/replace inherited entries explicitly and inspect merged configuration.", "components": ["docs"], "sources": ["docs:sfd95effa4d9b"], "status": "REASONED"},
    "passwords": {"text": "Replace inherited password with protected SHA-256 hash and loopback origins; SQL bcrypt has a 72-character limit.", "components": ["docs"], "sources": ["docs:s2ee7469699a5", "docs:sc7a527d82e50"], "status": "REASONED"},
    "bootstrap": {"text": "Complete administrator bootstrap needs access_management, named_collection_control and show_named_collections_secrets.", "components": ["docs"], "sources": ["docs:s2ee7469699a5", "docs:s324525fe685e"], "status": "REASONED"},
    "access-storage": {"text": "Persist SQL access storage; configured user_directories takes precedence over access_control_path.", "components": ["docs"], "sources": ["docs:sa133286c107f", "docs:s38015aaf3159"], "status": "REASONED"},
    "admin": {"text": "Separate SQL administrator gets global grants and restricted HOST IP; host restrictions do not enforce TLS.", "components": ["docs"], "sources": ["docs:s324525fe685e", "docs:sc7a527d82e50", "docs:s6b90e2c1092e"], "status": "REASONED"},
    "reader": {"text": "Table-scoped reader role combines with direct/inherited grants; remove excessive privileges and separate ingestion.", "components": ["docs"], "sources": ["docs:s25556959ddfa", "docs:sd137a7449c51", "docs:s6b90e2c1092e"], "status": "REASONED"},
    "retire-default": {"text": "After matched replacement login and dependency migration, remove temporary bootstrap and inherited default definition.", "components": ["docs"], "sources": ["docs:s324525fe685e", "docs:sfd95effa4d9b"], "status": "REASONED"},
    "profiles": {"text": "Bind locked settings directly to the account so disabling roles cannot remove them; review overlapping profiles.", "components": ["docs"], "sources": ["docs:s26cbbfd750d7", "docs:sae310a80cd58"], "status": "REASONED"},
    "memory": {"text": "Query/per-user memory limits apply per server, are incompletely tracked, and do not bound all process memory.", "components": ["docs"], "sources": ["docs:s02fa1a2ea84b"], "status": "REASONED"},
    "timeout": {"text": "Zero speed-check delay makes timeout elapsed-time based; cancellation checkpoints can exceed the example 30 seconds.", "components": ["docs"], "sources": ["docs:sfd00c9c1a9a1"], "status": "REASONED"},
    "quota": {"text": "Username-keyed cumulative quotas are receiving-server local, reset on restart, and do not limit concurrency; some reads are exempt.", "components": ["docs"], "sources": ["docs:sf738cc05299a", "docs:s8d50f48221f7"], "status": "REASONED"},
    "readonly": {"text": "readonly/allow_ddl do not replace grants; readonly=2 permits more operations and is not a READONLY constraint.", "components": ["docs"], "sources": ["docs:sad8b1924b3ce"], "status": "REASONED"},
    "tls-ports": {"text": "Enable HTTPS 8443/native TLS 9440 and remove plaintext 8123/9000; baseline removes both replication listeners.", "components": ["docs"], "sources": ["docs:sd891987369e6", "docs:sd78f0c21ad7b", "docs:sfd95effa4d9b"], "status": "REASONED"},
    "replica-tls": {"text": "Replica variant uses private HTTPS 9010, matching advertised hostname and verified outbound TLS, while removing 9009.", "components": ["docs"], "sources": ["docs:sd156261650ee", "docs:s4e31b63753ab", "docs:sd78f0c21ad7b", "docs:s6255e1dd351e"], "status": "REASONED"},
    "replica-auth": {"text": "Omitted interserver credentials disable auth; allow_empty true admits anonymous peers; match protected secrets across replicas.", "components": ["docs"], "sources": ["docs:s5b738c4b057c"], "status": "REASONED"},
    "cluster-tls": {"text": "Distributed-query and Keeper paths require separate TLS configuration beyond replication data HTTPS.", "components": ["docs"], "sources": ["docs:sd78f0c21ad7b"], "status": "REASONED"},
    "emulation": {"text": "Remove unused 9004/9005 listeners; PostgreSQL emulation can support TLS.", "components": ["docs"], "sources": ["docs:sd891987369e6", "docs:sfd95effa4d9b"], "status": "REASONED"},
    "client-tls": {"text": "Explicit client trust file and certificate hostname are required; extendedVerification defaults false, so enable it.", "components": ["docs"], "sources": ["docs:s6255e1dd351e", "docs:s01de3f86a875"], "status": "REASONED"},
    "certificate-auth": {"text": "ssl_certificate CN authentication supplies a machine possession factor, separate from human MFA.", "components": ["docs"], "sources": ["docs:sc7a527d82e50"], "status": "REASONED"},
    "totp": {"text": "26.2 introduced XML-user TOTP with password auth; SQL access control lacks it and each code is accepted at most once.", "components": ["docs", "totp"], "sources": ["docs:s4d5d0964fabb", "totp:sf7b9d01ede30"], "status": "REASONED"},
    "source-grants": {"text": "Withhold all source privileges and inherited grants; separate READ/WRITE needs 25.7+, filtering 25.8+, and enable_read_write_grants.", "components": ["docs", "sources"], "sources": ["docs:s6b90e2c1092e", "sources:s04a87783572d"], "status": "REASONED"},
    "source-interfaces": {"text": "url/HTTP dictionaries fetch remote data, file reads under user_files_path, and remote reaches other servers.", "components": ["docs"], "sources": ["docs:s8db5ea270091", "docs:s78d0544db7eb", "docs:sbb755048d8c0", "docs:s32fae5e0bf85"], "status": "REASONED"},
    "url-default": {"text": "Omitted remote_url_allow_hosts allows covered URL hosts; hostname-only permits every port.", "components": ["config", "docs"], "sources": ["config:s5bcf465239d6", "docs:saa2d39175e49"], "status": "REASONED"},
    "url-matching": {"text": "Host matching precedes DNS and applies on redirects; host:port does not require HTTPS or constrain every protocol.", "components": ["docs"], "sources": ["docs:saa2d39175e49"], "status": "REASONED"},
    "engine-grants": {"text": "OSS engine enforcement defaults disabled; enable it and grant only required engines alongside scoped CREATE TABLE.", "components": ["docs"], "sources": ["docs:s6b90e2c1092e", "docs:scce6af3a28a6"], "status": "REASONED"},
    "dictionaries": {"text": "Separate dictionary management from scoped dictGet use; ordinary readers need no management privilege.", "components": ["docs"], "sources": ["docs:s6b90e2c1092e"], "status": "REASONED"},
    "executables": {"text": "Administrator-controlled script/UDF discovery paths restrict modification; existing executable objects still need review.", "components": ["docs"], "sources": ["docs:sc172859d92a4", "docs:sba7a666c54ee", "docs:s0be4d04f7874"], "status": "REASONED"},
    "direct-exec": {"text": "execute_direct runs the approved program directly; zero invokes a shell; neither is a sandbox.", "components": ["docs"], "sources": ["docs:s247524807405"], "status": "REASONED"},
    "log-retention": {"text": "Configure query/session logs and explicit 30-day TTL; deprecated database option is omitted; custom engine conflicts need review.", "components": ["docs"], "sources": ["docs:s3ebb0f281977", "docs:sc67e973f5ab7", "docs:s41bbbde68a83"], "status": "REASONED"},
    "log-profile": {"text": "Lock query logging and sampling settings for each relevant account; overlapping profiles can conflict.", "components": ["docs"], "sources": ["docs:s26cbbfd750d7", "docs:s67072795b79e"], "status": "REASONED"},
    "log-events": {"text": "Query log records activity/errors, not results; session log records login/logout/failure; inspect every serving interface/node.", "components": ["docs"], "sources": ["docs:scfe38c988cb3", "docs:sde710fc1a785", "docs:s1b518ea764fb"], "status": "REASONED"},
    "log-access": {"text": "Require system-table grants, withhold application log access, mask sensitive query text and export to independent storage.", "components": ["docs"], "sources": ["docs:scce6af3a28a6", "docs:sc67e973f5ab7"], "status": "REASONED"},
    "log-upgrades": {"text": "Upgrades can rename old log tables; inspect their retention; no separate immutable OSS audit_log or imported Cloud retention is established.", "components": ["docs"], "sources": ["docs:s3ebb0f281977", "docs:s5b17854afa6d", "docs:s6298fa9f4719"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory intended 8443/9440 and optional private 9010; removed listeners absent; local ss proves no remote isolation/authentication.", "components": ["docs"], "sources": ["docs:sd891987369e6", "docs:sd78f0c21ad7b"], "status": "REASONED", "verify": [1]},
    "verify-http": {"text": "Matched no_password fixture accepts supplied/empty/wrong passwords; fixed HTTPS requires correct password and returns 1.", "components": ["docs", "curl"], "sources": ["docs:sc7a527d82e50", "docs:s3919007d159e", "curl:s5345a985007a"], "status": "REASONED", "verify": [2]},
    "verify-plaintext": {"text": "Any HTTP status on 8123 proves reachability; HTTP 000 needs inventory and successful TLS controls.", "components": ["docs"], "sources": ["docs:sd891987369e6", "docs:sd78f0c21ad7b", "docs:s3919007d159e"], "status": "REASONED", "verify": [2]},
    "verify-native": {"text": "Native wrong password needs authentication error/nonzero exit; correct credentials return 1; transport failures are inconclusive.", "components": ["docs"], "sources": ["docs:sc7a527d82e50", "docs:s01de3f86a875"], "status": "REASONED", "verify": [2, 3]},
    "verify-tables": {"text": "Fixed reader reads populated events and rejects private_events; test allowed/disallowed origins with matched reachable controls.", "components": ["docs"], "sources": ["docs:sc7a527d82e50", "docs:s25556959ddfa", "docs:s6b90e2c1092e"], "status": "REASONED", "verify": [3]},
    "verify-retirement": {"text": "Fresh default login fails after retirement on native/HTTPS while same-origin sql_admin still succeeds.", "components": ["docs"], "sources": ["docs:s324525fe685e", "docs:sfd95effa4d9b", "docs:s01de3f86a875", "docs:s3919007d159e"], "status": "REASONED", "verify": [2, 3]},
    "verify-settings": {"text": "Reject unlocked override; inspect four limits and require successful SET ROLE NONE/DEFAULT with account profile retained.", "components": ["roles", "docs"], "sources": ["roles:sa66cde5c2b6e", "docs:s26cbbfd750d7", "docs:sae310a80cd58", "docs:s02fa1a2ea84b", "docs:sfd00c9c1a9a1"], "status": "REASONED", "verify": [3]},
    "verify-memory": {"text": "Calibrated aggregation fails at lower memory limit while simple read succeeds; test concurrent user budget and timeout separately.", "components": ["docs"], "sources": ["docs:s02fa1a2ea84b", "docs:sfd00c9c1a9a1", "docs:s201098033e10"], "status": "REASONED", "verify": [3]},
    "verify-quota": {"text": "Fresh fixture accepts first two application reads and rejects the third; test restart reset and independent server counters.", "components": ["docs"], "sources": ["docs:sf738cc05299a", "docs:s8d50f48221f7"], "status": "REASONED", "verify": [3]},
    "verify-file": {"text": "Isolate FILE privilege with existing fixture and constant prerequisites; missing-file/readonly errors prove no source denial.", "components": ["docs"], "sources": ["docs:s6b90e2c1092e", "docs:sad8b1924b3ce", "docs:s78d0544db7eb"], "status": "REASONED", "verify": [3]},
    "verify-url": {"text": "Approved HTTPS fixture succeeds and unlisted host gets allow-list rejection; other errors are inconclusive.", "components": ["docs"], "sources": ["docs:saa2d39175e49", "docs:s8db5ea270091"], "status": "REASONED", "verify": [3]},
    "verify-engine": {"text": "With engine enforcement enabled MergeTree succeeds and TinyLog gets engine-privilege denial; remove fixtures between runs.", "components": ["docs"], "sources": ["docs:s6b90e2c1092e", "docs:scce6af3a28a6", "docs:sde8cc2811bb5", "docs:s463e85e20441"], "status": "REASONED", "verify": [3]},
    "verify-logs": {"text": "Require new marker/login-failure records, locked logging, reader denial and admin/collector success with correlated provenance.", "components": ["docs"], "sources": ["docs:scce6af3a28a6", "docs:s67072795b79e", "docs:scfe38c988cb3", "docs:sde710fc1a785", "docs:s1b518ea764fb"], "status": "REASONED", "verify": [3]},
    "verify-retention": {"text": "Inspect table TTLs and historical tables; expired records disappear while recent ones remain in isolated retention test.", "components": ["docs"], "sources": ["docs:s3ebb0f281977", "docs:s41bbbde68a83", "docs:s2d3e9d1310e4"], "status": "REASONED", "verify": [3]},
    "verify-totp": {"text": "Fixed XML human account rejects missing/invalid OTP and accepts password with fresh code; do not reuse positive code.", "components": ["docs"], "sources": ["docs:s4d5d0964fabb"], "status": "REASONED", "verify": [3]}
  }
}
---
# ClickHouse: listen address, the default user, and TLS ports

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| listen-default: Shipped config tries IPv4/IPv6 localhost; widening listen_host can expose services; inspect merged overrides. | ClickHouse documentation unknown; ClickHouse server config source 9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6 | REASONED |
| default-user: Upstream default has empty password, ::/0 origins and access_management; full bootstrap needs additional capabilities. | ClickHouse users source b40982f9416bb4bc2d423d7e75ec384e79494b99 | REASONED |
| docker-default: Official image disables default network access when all three documented initialization variables are unset. | ClickHouse documentation unknown | REASONED |
| ports: 8123 HTTP, 9000 native, 9004 MySQL, 9005 PostgreSQL and 9009 interserver are documented, not necessarily active. | ClickHouse documentation unknown | REASONED |
| interserver-bind: interserver_listen_host defaults to listen_host but can independently widen replica exposure. | ClickHouse documentation unknown | REASONED |
| xml-merge: config.d/users.d retain clickhouse roots; remove/replace inherited entries explicitly and inspect merged configuration. | ClickHouse documentation unknown | REASONED |
| passwords: Replace inherited password with protected SHA-256 hash and loopback origins; SQL bcrypt has a 72-character limit. | ClickHouse documentation unknown | REASONED |
| bootstrap: Complete administrator bootstrap needs access_management, named_collection_control and show_named_collections_secrets. | ClickHouse documentation unknown | REASONED |
| access-storage: Persist SQL access storage; configured user_directories takes precedence over access_control_path. | ClickHouse documentation unknown | REASONED |
| admin: Separate SQL administrator gets global grants and restricted HOST IP; host restrictions do not enforce TLS. | ClickHouse documentation unknown | REASONED |
| reader: Table-scoped reader role combines with direct/inherited grants; remove excessive privileges and separate ingestion. | ClickHouse documentation unknown | REASONED |
| retire-default: After matched replacement login and dependency migration, remove temporary bootstrap and inherited default definition. | ClickHouse documentation unknown | REASONED |
| profiles: Bind locked settings directly to the account so disabling roles cannot remove them; review overlapping profiles. | ClickHouse documentation unknown | REASONED |
| memory: Query/per-user memory limits apply per server, are incompletely tracked, and do not bound all process memory. | ClickHouse documentation unknown | REASONED |
| timeout: Zero speed-check delay makes timeout elapsed-time based; cancellation checkpoints can exceed the example 30 seconds. | ClickHouse documentation unknown | REASONED |
| quota: Username-keyed cumulative quotas are receiving-server local, reset on restart, and do not limit concurrency; some reads are exempt. | ClickHouse documentation unknown | REASONED |
| readonly: readonly/allow_ddl do not replace grants; readonly=2 permits more operations and is not a READONLY constraint. | ClickHouse documentation unknown | REASONED |
| tls-ports: Enable HTTPS 8443/native TLS 9440 and remove plaintext 8123/9000; baseline removes both replication listeners. | ClickHouse documentation unknown | REASONED |
| replica-tls: Replica variant uses private HTTPS 9010, matching advertised hostname and verified outbound TLS, while removing 9009. | ClickHouse documentation unknown | REASONED |
| replica-auth: Omitted interserver credentials disable auth; allow_empty true admits anonymous peers; match protected secrets across replicas. | ClickHouse documentation unknown | REASONED |
| cluster-tls: Distributed-query and Keeper paths require separate TLS configuration beyond replication data HTTPS. | ClickHouse documentation unknown | REASONED |
| emulation: Remove unused 9004/9005 listeners; PostgreSQL emulation can support TLS. | ClickHouse documentation unknown | REASONED |
| client-tls: Explicit client trust file and certificate hostname are required; extendedVerification defaults false, so enable it. | ClickHouse documentation unknown | REASONED |
| certificate-auth: ssl_certificate CN authentication supplies a machine possession factor, separate from human MFA. | ClickHouse documentation unknown | REASONED |
| totp: 26.2 introduced XML-user TOTP with password auth; SQL access control lacks it and each code is accepted at most once. | ClickHouse documentation unknown; ClickHouse TOTP introduction 26.2 | REASONED |
| source-grants: Withhold all source privileges and inherited grants; separate READ/WRITE needs 25.7+, filtering 25.8+, and enable_read_write_grants. | ClickHouse documentation unknown; ClickHouse privilege registry 37c6c8c9bfc1de323e9a27711c5649352364bcba | REASONED |
| source-interfaces: url/HTTP dictionaries fetch remote data, file reads under user_files_path, and remote reaches other servers. | ClickHouse documentation unknown | REASONED |
| url-default: Omitted remote_url_allow_hosts allows covered URL hosts; hostname-only permits every port. | ClickHouse server config source 9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6; ClickHouse documentation unknown | REASONED |
| url-matching: Host matching precedes DNS and applies on redirects; host:port does not require HTTPS or constrain every protocol. | ClickHouse documentation unknown | REASONED |
| engine-grants: OSS engine enforcement defaults disabled; enable it and grant only required engines alongside scoped CREATE TABLE. | ClickHouse documentation unknown | REASONED |
| dictionaries: Separate dictionary management from scoped dictGet use; ordinary readers need no management privilege. | ClickHouse documentation unknown | REASONED |
| executables: Administrator-controlled script/UDF discovery paths restrict modification; existing executable objects still need review. | ClickHouse documentation unknown | REASONED |
| direct-exec: execute_direct runs the approved program directly; zero invokes a shell; neither is a sandbox. | ClickHouse documentation unknown | REASONED |
| log-retention: Configure query/session logs and explicit 30-day TTL; deprecated database option is omitted; custom engine conflicts need review. | ClickHouse documentation unknown | REASONED |
| log-profile: Lock query logging and sampling settings for each relevant account; overlapping profiles can conflict. | ClickHouse documentation unknown | REASONED |
| log-events: Query log records activity/errors, not results; session log records login/logout/failure; inspect every serving interface/node. | ClickHouse documentation unknown | REASONED |
| log-access: Require system-table grants, withhold application log access, mask sensitive query text and export to independent storage. | ClickHouse documentation unknown | REASONED |
| log-upgrades: Upgrades can rename old log tables; inspect their retention; no separate immutable OSS audit_log or imported Cloud retention is established. | ClickHouse documentation unknown | REASONED |
| verify-inventory: Inventory intended 8443/9440 and optional private 9010; removed listeners absent; local ss proves no remote isolation/authentication. | ClickHouse documentation unknown | REASONED |
| verify-http: Matched no_password fixture accepts supplied/empty/wrong passwords; fixed HTTPS requires correct password and returns 1. | ClickHouse documentation unknown; curl documentation unknown | REASONED |
| verify-plaintext: Any HTTP status on 8123 proves reachability; HTTP 000 needs inventory and successful TLS controls. | ClickHouse documentation unknown | REASONED |
| verify-native: Native wrong password needs authentication error/nonzero exit; correct credentials return 1; transport failures are inconclusive. | ClickHouse documentation unknown | REASONED |
| verify-tables: Fixed reader reads populated events and rejects private_events; test allowed/disallowed origins with matched reachable controls. | ClickHouse documentation unknown | REASONED |
| verify-retirement: Fresh default login fails after retirement on native/HTTPS while same-origin sql_admin still succeeds. | ClickHouse documentation unknown | REASONED |
| verify-settings: Reject unlocked override; inspect four limits and require successful SET ROLE NONE/DEFAULT with account profile retained. | ClickHouse role source 1163c482760fb0204e40f8fb5d81ffa1272bc9ea; ClickHouse documentation unknown | REASONED |
| verify-memory: Calibrated aggregation fails at lower memory limit while simple read succeeds; test concurrent user budget and timeout separately. | ClickHouse documentation unknown | REASONED |
| verify-quota: Fresh fixture accepts first two application reads and rejects the third; test restart reset and independent server counters. | ClickHouse documentation unknown | REASONED |
| verify-file: Isolate FILE privilege with existing fixture and constant prerequisites; missing-file/readonly errors prove no source denial. | ClickHouse documentation unknown | REASONED |
| verify-url: Approved HTTPS fixture succeeds and unlisted host gets allow-list rejection; other errors are inconclusive. | ClickHouse documentation unknown | REASONED |
| verify-engine: With engine enforcement enabled MergeTree succeeds and TinyLog gets engine-privilege denial; remove fixtures between runs. | ClickHouse documentation unknown | REASONED |
| verify-logs: Require new marker/login-failure records, locked logging, reader denial and admin/collector success with correlated provenance. | ClickHouse documentation unknown | REASONED |
| verify-retention: Inspect table TTLs and historical tables; expired records disappear while recent ones remain in isolated retention test. | ClickHouse documentation unknown | REASONED |
| verify-totp: Fixed XML human account rejects missing/invalid OTP and accepts password with fresh code; do not reuse positive code. | ClickHouse documentation unknown | REASONED |
<!-- version-basis:end -->

ClickHouse listens on localhost only until you set `listen_host`, but the upstream base configuration ships a `default` user that has an empty password, may connect from any address (`<ip>::/0</ip>`), and holds `access_management`, so widening `listen_host` to `::` or `0.0.0.0` can publish a passwordless administrative account on plaintext HTTP 8123 and native TCP 9000. Packaging, container initialization, and configuration overrides can change these defaults (the official Docker image, for one, disables the `default` user's network access when none of `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, or `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT` is set), so inspect the effective configuration of the version you run rather than assuming either behaviour. Complete the account and TLS setup before widening access. The full administrator bootstrap needs the additional capabilities in step 2. [Access control](https://clickhouse.com/docs/concepts/features/security/access-rights), [Docker default-user behaviour](https://clickhouse.com/docs/get-started/setup/self-managed/docker#managing-default-user).

## 1. Keep `listen_host` narrow

The shipped `config.xml` comments out the `listen_host` examples and defaults to trying IPv4 and IPv6 localhost. For remote clients, name the one private address rather than `::`. Keep only loopback while preparing authentication and TLS; add the private address afterwards. The following shows the relevant children of the existing `<clickhouse>` root, not a replacement for the entire base file:

```xml
<clickhouse>
  <listen_host>127.0.0.1</listen_host>
  <listen_host>REPLACE_WITH_PRIVATE_IP</listen_host>
</clickhouse>
```

Use a `config.d` override for server settings and a `users.d` override for user settings, as named below. Each server or user XML document retains the `<clickhouse>` root. If editing base `config.xml` or `users.xml` instead, modify the existing children in place rather than replacing the whole file.

Remove any inherited wildcard listener when adapting an existing configuration. Inspect the merged configuration rather than assuming an additional narrow entry cancels a broad one. [Listener settings](https://clickhouse.com/docs/reference/settings/server-settings/settings/listen#listen_host), [configuration merging](https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files).

Inventory the listeners actually enabled. Documented port numbers include HTTP 8123, native TCP 9000, MySQL emulation 9004, PostgreSQL emulation 9005, and interserver HTTP 9009; listing a port does not mean it is active. PostgreSQL emulation can also use TLS when configured. Replica communication follows `interserver_listen_host`, which defaults to `listen_host` but can be set separately. Inspect every effective listener before writing firewall rules per [cloud-firewalls.md](cloud-firewalls.md) or [host.md](host.md). [Network ports](https://clickhouse.com/docs/concepts/features/security/network-ports), [interserver listener setting](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver#interserver_listen_host).

## 2. Put a password on `default`, and create real users

Replace the inherited empty password with the SHA-256 hash of a long, separately generated random password, and restrict the bootstrap account to loopback. Install `/etc/clickhouse-server/users.d/default-hardening.xml`:

```xml
<clickhouse>
  <users>
    <default>
      <password remove="remove"/>
      <password_sha256_hex>REPLACE_WITH_THE_SHA256_HEX_OF_A_LONG_RANDOM_PASSWORD</password_sha256_hex>
      <networks replace="replace">
        <ip>::1</ip>
        <ip>127.0.0.1</ip>
      </networks>
      <profile>default</profile>
      <quota>default</quota>
      <access_management>1</access_management>
    </default>
  </users>
</clickhouse>
```

This example replaces the shipped single `<password>` authentication method. Inspect existing customizations before applying it. `password_double_sha1_hex` exists for MySQL-protocol clients; plain `<password>` stores the secret in clear. SQL users also support `bcrypt_password`, with the documented 72-character password limit. Keep passwords out of command-line arguments and shell history. [User settings](https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users), [SQL authentication methods](https://clickhouse.com/docs/reference/statements/create/user#identification).

A shared administrator account makes an application compromise an administrative compromise. Keep the password and loopback restrictions on `default` while creating a separate SQL administrator. `access_management` enables SQL access management, but current documentation requires three capabilities for a complete administrator able to delegate `ALL`. Install this temporary `/etc/clickhouse-server/users.d/bootstrap-admin.xml` override:

```xml
<clickhouse>
  <users>
    <default>
      <access_management>1</access_management>
      <named_collection_control>1</named_collection_control>
      <show_named_collections_secrets>1</show_named_collections_secrets>
    </default>
  </users>
</clickhouse>
```

Ensure the effective SQL access storage is persistent. `access_control_path` specifies that directory when used; if `user_directories` is configured, its storage definitions take precedence and `access_control_path` is not used. Preserve the effective persistent storage across restarts and container replacement. [Administrator bootstrap](https://clickhouse.com/docs/concepts/features/security/access-rights#enabling-sql-driven-access-control-and-account-management), [access storage](https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_directories).

Apply the configuration before bootstrapping. Prepare step 4's TLS listener and client trust configuration while the server remains on loopback, then use the guarded interactive connection in Verify as `default`. Enter its password at the prompt. Create the replacement administrator with a separately generated password hash:

```sql
CREATE USER sql_admin
IDENTIFIED WITH sha256_hash BY 'REPLACE_WITH_ADMIN_SHA256_HEX'
HOST IP '127.0.0.1', IP '::1', IP '10.20.30.10/32';

GRANT ALL ON *.* TO sql_admin WITH GRANT OPTION;
```

Replace `10.20.30.10/32` with the actual administrator workstation address. Both IPv4 and IPv6 loopback permit local administration and the matched retirement check below. The global grant belongs only to this dedicated administrator. `HOST IP` restricts connection origins; it does not require encryption. Enforce TLS through step 4's secure listeners and plaintext-listener removal. The current `CREATE USER` grammar does not document a `REQUIRE SSL` clause. [CREATE USER](https://clickhouse.com/docs/reference/statements/create/user).

After authenticating successfully as `sql_admin`, create a separate reader for an existing application table:

```sql
CREATE ROLE app_read;

GRANT SELECT ON appdb.events TO app_read;

CREATE USER app_reader
IDENTIFIED WITH sha256_hash BY 'REPLACE_WITH_READER_SHA256_HEX'
HOST IP '10.20.40.0/24';

GRANT app_read TO app_reader;
SET DEFAULT ROLE app_read TO app_reader;
```

Use the actual application subnet and table. Keep ingestion permissions in a separate account. Roles combine with direct grants and other enabled roles, so adding a narrow role does not remove existing broad privileges. Review inherited grants as well as direct grants. See [authentication.md](authentication.md). [CREATE ROLE](https://clickhouse.com/docs/reference/statements/create/role), [SET DEFAULT ROLE](https://clickhouse.com/docs/reference/statements/set-role#set-default-role).

After testing the replacement administrator and migrating every dependency on `default`, including any inter-node use, remove `bootstrap-admin.xml` and install `/etc/clickhouse-server/users.d/disable-default.xml`:

```xml
<clickhouse>
  <users>
    <default remove="remove"/>
  </users>
</clickhouse>
```

This removes the inherited XML definition. Inspect the merged configuration, ensure later fragments do not restore it, and perform the fresh-login retirement checks in Verify. Keep the password-protected, loopback-only account until the handoff is demonstrated. [Configuration merging](https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files).

Version note: at the time of writing, current OSS documentation explicitly requires `named_collection_control` and `show_named_collections_secrets` alongside `access_management` for the complete-administrator bootstrap. Do not assume an older deployment's effective permissions match the current shipped configuration.

## 3. Lock query limits and add a quota

An authenticated reader can still exhaust database resources. Assign limits directly to the account, so disabling its active role does not remove the profile. These example budgets are starting values to size for the deployment:

```sql
CREATE SETTINGS PROFILE app_reader_limits
SETTINGS
    readonly = 1 READONLY,
    allow_ddl = 0 READONLY,
    max_memory_usage = 1073741824 READONLY,
    max_memory_usage_for_user = 2147483648 READONLY,
    max_execution_time = 30 READONLY,
    timeout_before_checking_execution_speed = 0 READONLY
TO app_reader;
```

`READONLY` after a setting locks that setting; `readonly = 1` restricts query classes. Review other assigned profiles for conflicting values or constraints. [CREATE SETTINGS PROFILE](https://clickhouse.com/docs/reference/statements/create/settings-profile), [constraints on settings](https://clickhouse.com/docs/concepts/features/configuration/settings/constraints-on-settings).

The memory limits cover one query and one user's queries, respectively, on each server. They are not a complete process-memory bound, and some allocations are not fully tracked. Setting the execution-speed checking delay to zero makes the timeout use elapsed time, but cancellation occurs at supported checkpoints and may exceed 30 seconds. [Memory settings](https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage), [execution-time settings](https://clickhouse.com/docs/reference/settings/session-settings/max-execution#max_execution_time).

Add a separate cumulative budget:

```sql
CREATE QUOTA app_reader_hourly
KEYED BY user_name
FOR INTERVAL 1 HOUR MAX queries = 1000, execution_time = 300
TO app_reader;
```

This quota counts usage per username. It does not limit simultaneous queries. For distributed processing, accumulated usage is held on the receiving server; it is not a shared cluster-wide counter. Changing the receiving server gives another counter, and restarting a server resets quotas. Some system-table reads are exempt from quota accounting, so use an ordinary application table for the quota discriminator in Verify. [CREATE QUOTA](https://clickhouse.com/docs/reference/statements/create/quota), [quota accounting and exceptions](https://clickhouse.com/docs/concepts/features/configuration/server-config/quotas).

Keep the table-scoped grants from step 2. Neither `readonly` nor `allow_ddl` is a complete authorization policy. Current documentation describes exceptions involving backups, temporary tables, named collections, and access-management statements. Do not give this reader those privileges. An ingestion account needs its own profile without `readonly = 1`. [Permissions for queries](https://clickhouse.com/docs/concepts/features/configuration/settings/permissions-for-queries).

Version note: use the documented `READONLY` constraint syntax. Do not substitute `readonly = 2`: it permits additional operations, including settings changes and some operations that write data.

## 4. TLS listeners, plaintext ports off

Get a certificate per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md). Install `/etc/clickhouse-server/config.d/hardening.xml`, adapting the certificate paths. This baseline disables interserver listeners; replicated deployments must apply the replica variant below before restarting:

```xml
<clickhouse>
  <https_port>8443</https_port>
  <tcp_port_secure>9440</tcp_port_secure>
  <http_port remove="remove"/>
  <tcp_port remove="remove"/>
  <interserver_http_port remove="remove"/>
  <interserver_https_port remove="remove"/>
  <openSSL>
    <server>
      <certificateFile>/etc/clickhouse-server/certs/server.crt</certificateFile>
      <privateKeyFile>/etc/clickhouse-server/certs/server.key</privateKeyFile>
      <disableProtocols>sslv2,sslv3</disableProtocols>
      <preferServerCiphers>true</preferServerCiphers>
    </server>
  </openSSL>
</clickhouse>
```

Do not leave the shipped plaintext `interserver_http_port` 9009 inherited. For replicas, replace the two interserver removal entries in the same `hardening.xml` with the corresponding settings below, add the other children to its existing `<clickhouse>` root, and merge `<client>` into its existing `<openSSL>` block. Retain `<openSSL><server>` above for the HTTPS certificate and key. Do not install these alternatives side by side. [Shipped replication listener](https://raw.githubusercontent.com/ClickHouse/ClickHouse/9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6/programs/server/config.xml), [interserver HTTPS settings](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-https).

```xml
<clickhouse>
  <interserver_http_port remove="remove"/>
  <interserver_https_port>9010</interserver_https_port>
  <interserver_listen_host replace="replace">REPLACE_WITH_PRIVATE_IP</interserver_listen_host>
  <interserver_https_host>REPLACE_WITH_REPLICA_CERTIFICATE_HOSTNAME</interserver_https_host>
  <interserver_http_credentials replace="replace">
    <user>replication</user>
    <password>REPLACE_WITH_LONG_RANDOM_REPLICATION_SECRET</password>
    <allow_empty>false</allow_empty>
  </interserver_http_credentials>
  <openSSL>
    <client>
      <caConfig>/etc/clickhouse-server/certs/ca.crt</caConfig>
      <verificationMode>strict</verificationMode>
      <extendedVerification>true</extendedVerification>
      <invalidCertificateHandler>
        <name>RejectCertificateHandler</name>
      </invalidCertificateHandler>
    </client>
  </openSSL>
</clickhouse>
```

Use each replica's private address and certificate-covered hostname; that hostname must resolve to its private address from its peers. Remove inherited wildcard interserver bindings, inspect the merged configuration, and allow 9010 only from replica addresses in the firewall. Install the trusted CA on every server for outbound HTTPS verification. A native client's separate configuration does not configure the server's outbound connections. [Interserver bind](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver#interserver_listen_host), [HTTPS hostname](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-https#interserver_https_host), [OpenSSL verification](https://clickhouse.com/docs/reference/settings/server-settings/settings/other#openSSL).

Require matching `interserver_http_credentials` on every replica, with a separately generated secret and `allow_empty` false. Omitting the credentials section disables replication authentication; setting `allow_empty` true admits unauthenticated peers. These credentials apply to both HTTP and HTTPS and are independent of SQL-user credentials; TLS alone does not supply them. Provision the secret through a secure editor or secret-management mechanism, protect the configuration and its preprocessed copies from other users, and keep it out of argv, shell history, and source control. Coordinate the rollout across replicas before enabling access. [Replication authentication](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-http#interserver_http_credentials).

This secures the replication data listener. Distributed-query and Keeper connections need their own TLS configuration; complete the vendor's [cluster TLS procedure](https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls) for those enabled paths.

Remove unused emulation listeners with `/etc/clickhouse-server/config.d/disable-emulation.xml`:

```xml
<clickhouse>
  <mysql_port remove="remove"/>
  <postgresql_port remove="remove"/>
</clickhouse>
```

PostgreSQL emulation on 9005 can use TLS; the removal above closes an unused interface rather than assuming every connection on that port is plaintext. Inventory other enabled listeners separately. [TLS setup](https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls), [network ports](https://clickhouse.com/docs/concepts/features/security/network-ports).

When editing the base `config.xml` directly, remove or comment out the active plaintext `http_port`, `tcp_port`, and `interserver_http_port` elements, checking that no override re-enables them. Commenting out an element in an override does not remove an inherited setting. The explicit `remove` attributes above do. Inspect the effective merged configuration and apply the listener changes before opening the private address to clients. [Configuration files](https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files).

On each native client machine, install the trusted CA at `/etc/clickhouse-client/ca.crt` and merge this into `~/.config/clickhouse/config.xml`:

```xml
<config>
  <openSSL>
    <client>
      <caConfig>/etc/clickhouse-client/ca.crt</caConfig>
      <verificationMode>strict</verificationMode>
      <extendedVerification>true</extendedVerification>
      <invalidCertificateHandler>
        <name>RejectCertificateHandler</name>
      </invalidCertificateHandler>
    </client>
  </openSSL>
</config>
```

The Verify commands explicitly select this file so a different default configuration cannot silently take precedence. Connect using a hostname covered by the certificate. For local bootstrap and retirement checks, provision a certificate name that resolves to loopback on the server. At the time of writing, the OpenSSL reference lists `extendedVerification` as false by default; enable it explicitly to check the peer name. [Client configuration](https://clickhouse.com/docs/concepts/features/interfaces/client), [OpenSSL verification](https://clickhouse.com/docs/reference/settings/server-settings/settings/other#openSSL).

Users can also authenticate with a client certificate using `IDENTIFIED WITH ssl_certificate CN 'name'`, a possession factor for machine clients; see [machine-auth.md](machine-auth.md). [Certificate authentication](https://clickhouse.com/docs/reference/statements/create/user#identification).

MFA: ClickHouse 26.2 introduced native TOTP. Current documentation supports `time_based_one_time_password` for users defined in XML alongside password authentication, with `secret`, `period`, `digits`, and `algorithm`; SQL-driven access control does not support it. Configure it for supported human accounts and route unsupported human paths, including the host and dashboards, behind an MFA-enforcing layer per [mfa.md](mfa.md). Keep machine authentication separate. Each TOTP code is accepted at most once, so clients that authenticate per request need a fresh code for each authentication; do not reuse a code across a probe loop. [TOTP configuration](https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users#totp-authentication-configuration), [26.2 release](https://clickhouse.com/blog/clickhouse-release-26-02).

## 5. Restrict external sources and executable discovery

SQL that reaches external sources can read local data or use the database's network access. Withhold the blanket `SOURCES` privilege and every individual source privilege from ordinary application accounts, including all source-specific `READ` and `WRITE` grants when enabled. Remove any such access and grant options from direct grants and inherited roles; withholding only the blanket grant does not cancel individual or inherited grants. This covers every source type in the deployed version, including database connectors, message queues, object stores, and local files. Review existing externally backed tables and dictionaries. Separate READ/WRITE source grants require ClickHouse 25.7 or later and `access_control_improvements.enable_read_write_grants`; filtered source grants require 25.8 or later with the same switch. Otherwise, use the documented legacy source privileges. [Source privileges](https://clickhouse.com/docs/reference/statements/grant#sources), [upstream source privilege registry](https://raw.githubusercontent.com/ClickHouse/ClickHouse/37c6c8c9bfc1de323e9a27711c5649352364bcba/src/Access/Common/AccessType.h).

ClickHouse can fetch HTTPS data through `url()` and HTTP dictionaries, read local files through `file()` relative to `user_files_path`, and reach other servers through `remote()`. `file()` is a local-file interface, not an HTTP fetcher. [URL function](https://clickhouse.com/docs/reference/functions/table-functions/url), [file function](https://clickhouse.com/docs/reference/functions/table-functions/file), [remote function](https://clickhouse.com/docs/reference/functions/table-functions/remote), [HTTP dictionary sources](https://clickhouse.com/docs/reference/statements/create/dictionary/sources/http).

For a deployment that requires one approved HTTPS source, install `/etc/clickhouse-server/config.d/external-sources.xml`:

```xml
<clickhouse>
  <remote_url_allow_hosts replace="replace">
    <host>data.example.com:443</host>
  </remote_url_allow_hosts>
  <access_control_improvements>
    <table_engines_require_grant>true</table_engines_require_grant>
  </access_control_improvements>
</clickhouse>
```

Omitting `remote_url_allow_hosts` allows all hosts for the URL interfaces it covers, as the [shipped configuration](https://raw.githubusercontent.com/ClickHouse/ClickHouse/9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6/programs/server/config.xml) documents. Replace the hostname and use an explicit `:443` in the permitted source URL. A hostname-only entry permits every port on that hostname. Matching occurs before DNS resolution and on redirects. This is not a universal restriction on every external protocol, nor does a host-and-port entry itself require HTTPS. Retain network egress restrictions on metadata endpoints and internal addresses per [egress-metadata.md](egress-metadata.md). [URL host allow-list](https://clickhouse.com/docs/reference/settings/server-settings/settings/remote#remote_url_allow_hosts).

For accounts that must create tables, enable engine-grant enforcement before relying on an engine allow-list. Grant only the required engine, for example to a separately provisioned schema-management role:

```sql
GRANT TABLE ENGINE ON MergeTree TO schema_manager;
```

This supplements the role's separately scoped `CREATE TABLE` privilege. It does not grant access to existing tables, restrict every table function, or remove existing grants. At the time of writing, engine-grant enforcement is documented for self-managed OSS and is disabled by default. Roll it out with the grants required by legitimate schema-management jobs. [Engine privileges](https://clickhouse.com/docs/reference/statements/grant#table-engine), [access-control settings](https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_improvements).

Keep dictionary creation and dictionary use separate. Ordinary readers should not receive dictionary-management privileges; grant `dictGet` only on an approved dictionary when required. [Dictionary privileges](https://clickhouse.com/docs/reference/statements/grant#dictget).

Executable functions need an additional filesystem boundary. Install `/etc/clickhouse-server/config.d/executable-paths.xml`:

```xml
<clickhouse>
  <user_scripts_path>/var/lib/clickhouse/approved_scripts/</user_scripts_path>
  <user_defined_executable_functions_config>/etc/clickhouse-server/approved-functions/*.xml</user_defined_executable_functions_config>
</clickhouse>
```

Provision these administrator-controlled directories before applying the configuration. Give the ClickHouse process the access needed to read configuration and execute approved scripts, while preventing application identities from modifying their contents or parent directories. Leave them empty when executable functionality is unused. Review already installed executable tables, dictionaries, and UDFs separately; changing discovery paths is not a SQL sandbox. [Script directory](https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_scripts_path), [executable-UDF configuration path](https://clickhouse.com/docs/reference/settings/server-settings/settings/user-defined#user_defined_executable_functions_config), [executable table function](https://clickhouse.com/docs/reference/functions/table-functions/executable).

For an approved executable UDF, keep this fragment inside its existing `<function>` definition:

```xml
<execute_direct>1</execute_direct>
```

It resolves the configured command from the script directory. Setting it to zero invokes a shell. Direct execution still runs the approved program and does not sandbox that program. There is no `allow_executable_user_defined_functions` setting prescribed by this guide. [Executable UDF configuration](https://clickhouse.com/docs/reference/functions/regular-functions/udf).

## 6. Configure and protect query and session logs

Authentication without retained evidence makes misuse harder to investigate. Configure query and session logging on each server and choose a retention period. Install `/etc/clickhouse-server/config.d/security-logs.xml`:

```xml
<clickhouse>
  <query_log replace="replace">
    <table>query_log</table>
    <partition_by>toYYYYMM(event_date)</partition_by>
    <ttl>event_date + INTERVAL 30 DAY</ttl>
    <flush_interval_milliseconds>7500</flush_interval_milliseconds>
  </query_log>
  <session_log replace="replace">
    <table>session_log</table>
    <partition_by>toYYYYMM(event_date)</partition_by>
    <ttl>event_date + INTERVAL 30 DAY</ttl>
    <flush_interval_milliseconds>7500</flush_interval_milliseconds>
  </session_log>
</clickhouse>
```

Thirty days is an explicit local policy, not an OSS retention default. Current documentation marks the system-log `database` option deprecated and places these tables in `system`, so it is omitted here. Review existing storage customization before replacing either subtree: a custom `engine` definition conflicts with separate `partition_by` and `ttl` settings. [System-log configuration](https://clickhouse.com/docs/reference/system-tables/overview), [query-log configuration](https://clickhouse.com/docs/reference/settings/server-settings/settings/query#query_log).

Prevent the application account from disabling query logging or reducing it to a sample:

```sql
CREATE SETTINGS PROFILE app_reader_logging
SETTINGS
    log_queries = 1 READONLY,
    log_queries_probability = 1 READONLY,
    log_queries_min_query_duration_ms = 0 READONLY,
    log_queries_min_type = 'QUERY_START' READONLY
TO app_reader;
```

Apply an equivalent profile to each account whose queries must be recorded, and review overlapping profiles. [Query logging settings](https://clickhouse.com/docs/reference/settings/session-settings/log-queries).

As an administrator, inspect query activity and authentication failures:

```sql
-- REASONED: no ClickHouse server/client binary or container runtime is available here.
SYSTEM FLUSH LOGS;

SELECT event_time, type, user, address, query_id, query, exception
FROM system.query_log
ORDER BY event_time DESC
LIMIT 50;

SELECT event_time, type, user, client_address, failure_reason
FROM system.session_log
WHERE type = 'LoginFailure'
ORDER BY event_time DESC
LIMIT 50;
```

The query log records query activity and exceptions, not result sets. The session log records login success, login failure, and logout events. Check every serving node and every enabled authentication interface. [Query log](https://clickhouse.com/docs/reference/system-tables/query_log), [session log](https://clickhouse.com/docs/reference/system-tables/session_log), [SYSTEM FLUSH LOGS](https://clickhouse.com/docs/reference/statements/system#system-flush-logs).

Ensure `access_control_improvements.select_from_system_db_requires_grant` is enabled, and keep log-table grants out of application roles. Export security records to independently controlled storage. Query text can contain sensitive values; consider deployment-specific `query_masking_rules`, configured on every participating server. [System-table access control](https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_improvements), [query masking](https://clickhouse.com/docs/reference/settings/server-settings/settings/query#query_masking_rules).

Version note: log schemas can change during upgrades, causing older log tables to be renamed. Verify retention and collection across those tables. ClickHouse's database-audit documentation uses query and session logs; it does not establish a separate immutable OSS `system.audit_log`. The separately documented console audit log concerns ClickHouse Cloud. Do not import Cloud retention defaults into this guide. [System-log upgrades](https://clickhouse.com/docs/reference/system-tables/overview), [database audit logging](https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/database-audit-log), [console audit logging](https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/console-audit-log).

## Verify

Service-level checks below are **REASONED, not demonstrated**. The authoring environment has no ClickHouse server/client binary or container runtime, and no authorized live test deployment was supplied. SQL execution, configuration semantics, and exposed-versus-fixed behaviour remain unobserved. Run the exposed fixtures only in an isolated test deployment.

Paste each whole shell block into Bash, substituting values inside the quotes. The guards reject unresolved placeholders, angle brackets, `example.com`, and empty input. They do not protect a fragment pasted from below the guard.

**REASONED: listener inventory requires the missing ClickHouse deployment and access to its network namespace.** Run this block in the server's actual namespace; the label records your identification and does not switch namespaces:

```bash
# REASONED: no ClickHouse server or container runtime is available here.
# Run in the server's network namespace; substitute its name inside the quotes.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SERVER_NETWORK_NAMESPACE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one namespace label; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the server namespace label; not probing"
      exit 2
      ;;
    *)
      printf 'Inventory of the current namespace, identified by you as %s:\n' "$1"
      ss -tlnp
      ;;
  esac
)
```

The exposed fixture has the plaintext listeners enabled. The fixed deployment should show 8443 and 9440 on the intended addresses, no removed listeners (including plaintext replication 9009), and only other listeners deliberately retained, such as replication HTTPS 9010 on its explicit private address. A node without replication should expose neither 9009 nor 9010. Repeat the inventory on every replica; listener presence does not demonstrate replication authentication. Inspect host/container publication and firewalls separately. `ss` observes the current network namespace; it proves neither remote reachability nor authentication. [Listener configuration](https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls), [port inventory](https://clickhouse.com/docs/concepts/features/security/network-ports).

**REASONED: transport and authentication require the missing server/client runtime and reachable TLS endpoints.** For the exposed authentication fixture, provision the same named account, `app_reader`, with `IDENTIFIED WITH no_password`, the same allowed client origin, and sufficient access to execute `SELECT 1`. This is an isolated alternative to the password-authenticated account in step 2. A stock passwordless `default` account does not establish anything about `app_reader`. Keep the host, certificate, interface, and request constant between fixture states. [Authentication methods](https://clickhouse.com/docs/reference/statements/create/user#identification).

For the correct HTTP request, provision `~/.config/clickhouse/app-reader.headers` through a secure editor or secret-management mechanism, readable only by its owner, with two lines: `X-ClickHouse-User: app_reader` and `X-ClickHouse-Key: ` followed by the actual password. Use a nonempty, single-line password without control characters, different from the deliberate wrong-password value below. Do not put the secret in a shell command. The correct request reads both headers from that protected file on stdin, keeping the password out of curl's argv and shell history. Install the CA and native client configuration from step 4 first. For a certificate trusted by curl's system CA store, omit each `--cacert /etc/clickhouse-client/ca.crt` pair from the HTTP probes; retain certificate verification.

Clients use native TLS on 9440 or HTTPS on 8443. HTTP supports Basic authentication and the `X-ClickHouse-User`/`X-ClickHouse-Key` headers; avoid `user` and `password` URL parameters because intermediaries can log them. The block requires curl 7.75.0 or later for its diagnostic write-out fields. [HTTP authentication](https://clickhouse.com/docs/concepts/features/interfaces/http), [native client](https://clickhouse.com/docs/concepts/features/interfaces/client).

```bash
# REASONED: no ClickHouse server/client binary or container runtime is available here.
# Run from the allowed application network. Substitute the host inside the quotes.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLICKHOUSE_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one host; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute your host inside the quotes; not probing"
      exit 2
      ;;
    *)
      set +e
      [ -r "$HOME/.config/clickhouse/app-reader.headers" ] || {
        echo "provision the protected credential header file first"; exit 2;
      }

      echo '[plaintext HTTP 8123]'
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -o /dev/null -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "http://$1:8123/?query=SELECT%201"

      echo '[HTTPS empty password]'
      printf 'X-ClickHouse-User: app_reader\nX-ClickHouse-Key;\n' |
        curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
          --cacert /etc/clickhouse-client/ca.crt --header @- \
          -w '\nhttp=%{http_code} exit=%{exitcode} remote=%{remote_ip} err=%{errormsg}\n' \
          "https://$1:8443/?query=SELECT%201"

      echo '[HTTPS deliberately wrong password]'
      printf 'X-ClickHouse-User: app_reader\nX-ClickHouse-Key: definitely-not-the-password\n' |
        curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
          --cacert /etc/clickhouse-client/ca.crt --header @- \
          -w '\nhttp=%{http_code} exit=%{exitcode} remote=%{remote_ip} err=%{errormsg}\n' \
          "https://$1:8443/?query=SELECT%201"

      echo '[HTTPS correct password]'
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert /etc/clickhouse-client/ca.crt \
        --header @- \
        -w '\nhttp=%{http_code} exit=%{exitcode} remote=%{remote_ip} err=%{errormsg}\n' \
        "https://$1:8443/?query=SELECT%201" \
        < "$HOME/.config/clickhouse/app-reader.headers"

      echo '[native wrong password: enter a deliberately wrong password]'
      clickhouse-client --config-file "$HOME/.config/clickhouse/config.xml" \
        --host "$1" --port 9440 --secure --user app_reader --query 'SELECT 1' --password
      printf 'native_exit=%s\n' "$?"

      echo '[native correct password: enter the configured password]'
      clickhouse-client --config-file "$HOME/.config/clickhouse/config.xml" \
        --host "$1" --port 9440 --secure --user app_reader --query 'SELECT 1' --password
      printf 'native_exit=%s\n' "$?"
      ;;
  esac
)
```

Any received HTTP status on 8123, including an error status or a status followed by a transfer error, proves that the plaintext port answered. `http=000` is only a transport failure; combine it with the server inventory and successful TLS positive controls before concluding that the listener was removed.

The empty-password request uses curl's `X-ClickHouse-Key;` form to transmit an empty-valued header; a trailing colon without a value would omit the header. [curl header syntax](https://curl.se/docs/manpage.html#-H).

In the deliberately authentication-disabled fixture, empty, wrong, and supplied passwords should all allow the HTTPS `SELECT 1` result. In the fixed state, empty and wrong passwords must produce ClickHouse authentication errors, while the correct password returns `1`. For native TLS, the fixed state must reject the wrong password with an authentication error and nonzero exit, then return `1` with exit zero for the correct password. A DNS, proxy, certificate, or connection error is inconclusive.

**REASONED: interactive SQL checks require the missing server/client runtime.** Use this guarded connection for the remaining checks. For administrator checks, change the quoted username to `sql_admin`; for bootstrap or retirement checks, use `default` as specified below. Enter passwords only at the prompt. [Client connection options](https://clickhouse.com/docs/concepts/features/interfaces/client).

```bash
# REASONED: no ClickHouse server/client binary or container runtime is available here.
# Substitute the host and, for administrative checks, the username inside the quotes.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLICKHOUSE_HOST' 'app_reader'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "supply exactly one host and one user; not connecting"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute your host inside the quotes; not connecting"
      exit 2
      ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute your user inside the quotes; not connecting"
          exit 2
          ;;
        *)
          clickhouse-client --config-file "$HOME/.config/clickhouse/config.xml" \
            --host "$1" --port 9440 --secure --user "$2" --password
          ;;
      esac
      ;;
  esac
)
```

**REASONED: table authorization requires the missing runtime and two populated fixture tables.** In the isolated deployment, have the administrator provision both `appdb.events` and `appdb.private_events`. Run these individually as `app_reader`:

```sql
-- REASONED: table authorization; no server/client runtime or deployment fixtures. Expected outcomes and vendor sources are recorded in this section.
SELECT * FROM appdb.events LIMIT 1;
SELECT * FROM appdb.private_events LIMIT 1;
```

A broadly granted baseline reads both tables. The fixed reader reads `events` and receives an authorization error for `private_events`. A missing table is not a passing denial. Repeat a successful login from the allowed application subnet and a login with the same credentials from a disallowed origin. For the host-restriction discriminator, first demonstrate that both origins can reach and authenticate to the permissive fixture; a fixed-state timeout alone does not prove `HOST IP` enforcement. [User hosts](https://clickhouse.com/docs/reference/statements/create/user#user-host), [roles and combined grants](https://clickhouse.com/docs/reference/statements/create/role).

**REASONED: default retirement requires the missing runtime and access to server loopback.** Before retirement, use the guarded connection locally with the certificate-valid loopback hostname as `default`, enter its configured password, and run `SELECT 1`. After retirement, repeat a fresh connection with the same credentials: it must fail authentication. From the same loopback origin and TLS endpoint, a fresh `sql_admin` connection must still run `SELECT 1` successfully. Repeat the credential check on HTTPS using an owner-only header file for each account and the guarded correct-password request shape above. Inspect the merged configuration for removal of `default`; a rejection from a previously disallowed network proves nothing about retirement. [Default-account handoff](https://clickhouse.com/docs/concepts/features/security/access-rights), [XML removal](https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files).

**REASONED: locked settings and resource enforcement require the missing runtime and a calibrated finite workload.** Run individually as `app_reader`:

```sql
SELECT 1 SETTINGS max_memory_usage = 0;
SELECT getSetting('max_memory_usage');
SELECT getSetting('max_memory_usage_for_user');
SELECT getSetting('max_execution_time');
SELECT getSetting('timeout_before_checking_execution_speed');

SET ROLE NONE;
SELECT getSetting('max_memory_usage');
SET ROLE DEFAULT;
```

An unconstrained baseline accepts the override. The fixed account rejects it and reports `1073741824`, `2147483648`, `30`, and `0` for the four settings. The account-bound memory profile remains effective with its role disabled. `SET ROLE NONE` and `SET ROLE DEFAULT` change the session's active roles and are permitted with `readonly = 1`; they do not use the settings-changing `SET` path. Require both role statements to succeed; an error does not demonstrate profile persistence. [SET ROLE implementation](https://raw.githubusercontent.com/ClickHouse/ClickHouse/1163c482760fb0204e40f8fb5d81ffa1272bc9ea/src/Interpreters/Access/InterpreterSetRoleQuery.cpp). These checks establish settings and constraints, not actual resource enforcement. [Constraints](https://clickhouse.com/docs/concepts/features/configuration/settings/constraints-on-settings), [memory settings and inspection](https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage), [SET ROLE](https://clickhouse.com/docs/reference/statements/set-role).

For a memory discriminator, give the isolated `events` fixture an `x UInt64` column with a finite, recorded number of distinct values. Use:

```sql
-- REASONED: bounded memory comparison; no server/client runtime or deployment fixtures. Expected outcomes and vendor sources are recorded in this section.
SELECT uniqExact(x) FROM appdb.events;
```

Measure a successful baseline, then assign the test reader a locked query-memory budget below that measured peak while retaining enough memory for a simple table read. The same aggregation must fail with a memory-limit error, while `SELECT * FROM appdb.events LIMIT 1` succeeds. Choose small test budgets instead of attempting to exhaust production memory. Test the per-user budget with concurrent copies whose combined measured usage exceeds that budget while each copy remains below its individual limit. Test elapsed-time enforcement separately with a calibrated finite workload and a lower test timeout, retaining a successful shorter-workload control; account for the documented cancellation checkpoints. [Exact distinct aggregation](https://clickhouse.com/docs/reference/functions/aggregate-functions/uniqExact), [memory limits](https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage), [execution-time limits](https://clickhouse.com/docs/reference/settings/session-settings/max-execution#max_execution_time).

**REASONED: quota enforcement requires the missing runtime, a fresh test account, and a fresh quota interval.** Provision `quota_reader` separately with password authentication, an appropriate host restriction, and permission to read the populated `events` fixture. Give it only this test quota:

```sql
CREATE QUOTA verify_reader_hourly
KEYED BY user_name
FOR INTERVAL 1 HOUR MAX queries = 2
TO quota_reader;
```

Through the guarded connection as `quota_reader`, issue these individually without intervening application queries:

```sql
-- REASONED: quota enforcement; no server/client runtime or deployment fixtures. Expected outcomes and vendor sources are recorded in this section.
SELECT * FROM appdb.events LIMIT 1;
SELECT * FROM appdb.events LIMIT 1;
SELECT * FROM appdb.events LIMIT 1;
```

The unrestricted baseline accepts all three. In the fixed fixture, the first two succeed and excess usage is rejected with a quota error. Avoid `SELECT 1` as the quota discriminator: current documentation exempts reads of `system.one` and several quota-inspection tables. Demonstrate restart reset and, when a second test server is available, independent receiving-server counters. [Quota syntax](https://clickhouse.com/docs/reference/statements/create/quota), [quota exceptions and reset behaviour](https://clickhouse.com/docs/concepts/features/configuration/server-config/quotas).

**REASONED: source restrictions require the missing runtime, a harmless local file, and reachable HTTPS fixtures.** Have the administrator place `probe.tsv`, containing a valid `UInt8` row, under the effective `user_files_path`. Run:

```sql
SELECT * FROM file('probe.tsv', 'TSV', 'x UInt8');
```

A source-authorized baseline reads the fixture; `app_reader` must not. To isolate the source privilege itself from `readonly` and table-function prerequisites, repeat with a dedicated test account whose other required permissions remain constant and whose only changed permission is FILE access. Require the corresponding authorization error. A missing file or a read-only-mode error does not establish that source-grant enforcement was tested. [File function](https://clickhouse.com/docs/reference/functions/table-functions/file), [source privileges](https://clickhouse.com/docs/reference/statements/grant#sources), [table functions in read-only mode](https://clickhouse.com/docs/concepts/features/configuration/settings/permissions-for-queries).

For URL allow-list enforcement, use a separately source-authorized test account with the required table-function permissions and two harmless, certificate-valid HTTPS fixtures. Substitute the actual hosts before executing:

```sql
-- REASONED: URL allow-list; no server/client runtime or deployment fixtures. Expected outcomes and vendor sources are recorded in this section.
SELECT * FROM url(
    'https://REPLACE_WITH_APPROVED_SOURCE_HOST:443/probe.tsv',
    'TSV',
    'x UInt8'
);

SELECT * FROM url(
    'https://REPLACE_WITH_UNLISTED_SOURCE_HOST:443/probe.tsv',
    'TSV',
    'x UInt8'
);
```

Both destinations must succeed in the permissive baseline. With the allow-list configured, the approved destination still succeeds and the unlisted destination produces an allow-list rejection. Missing source privileges, DNS failures, certificate failures, and unreachable fixture servers are inconclusive for this check. [URL function](https://clickhouse.com/docs/reference/functions/table-functions/url), [host allow-list matching](https://clickhouse.com/docs/reference/settings/server-settings/settings/remote#remote_url_allow_hosts).

**REASONED: engine-grant enforcement requires the missing runtime and a scratch database.** Give a dedicated test schema user scoped `CREATE TABLE` permission in `scratch`, permission to use `MergeTree`, no permission to use `TinyLog`, and settings that allow DDL. Run individually:

```sql
CREATE TABLE scratch.allowed (x UInt8)
ENGINE = MergeTree ORDER BY x;

CREATE TABLE scratch.denied (x UInt8)
ENGINE = TinyLog;
```

With engine enforcement disabled, both creations succeed. In a fresh fixed fixture with enforcement enabled, `MergeTree` succeeds and `TinyLog` receives an engine-privilege error. Have the administrator remove scratch tables between runs so an existing-table error cannot masquerade as a denial. [Engine privileges](https://clickhouse.com/docs/reference/statements/grant#table-engine), [CREATE TABLE](https://clickhouse.com/docs/reference/statements/create/table).

**REASONED: logging and log protection require the missing runtime and a functioning log collector.** As `app_reader`, run individually:

```sql
SELECT 703307 AS security_probe;
SELECT 1 SETTINGS log_queries = 0;
SELECT * FROM system.query_log LIMIT 1;
SELECT * FROM system.session_log LIMIT 1;
```

Also perform one deliberately wrong-password login using the guarded authentication block. As `sql_admin`, execute step 6's `SYSTEM FLUSH LOGS` and inspection queries.

The disabled-logging baseline lacks new matching records. The fixed state records the marker query and login failure, rejects the logging override, and denies the reader access to the log tables while the administrator can read them. Correlate query ID, node, account, client address, and test time; older rows are not evidence. Repeat authentication-event collection for every enabled interface. Check that the same records reach independently controlled storage. [Query logging settings](https://clickhouse.com/docs/reference/settings/session-settings/log-queries), [query log](https://clickhouse.com/docs/reference/system-tables/query_log), [session log](https://clickhouse.com/docs/reference/system-tables/session_log), [system-table authorization](https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_improvements).

As administrator, inspect the current table definitions:

```sql
-- REASONED: log retention; no server/client runtime or deployment fixtures. Expected outcomes and vendor sources are recorded in this section.
SHOW CREATE TABLE system.query_log;
SHOW CREATE TABLE system.session_log;
```

Confirm the intended TTL and inspect any renamed historical log tables separately. In an isolated retention fixture, confirm expired records are removed through TTL processing while recent records remain; the XML alone does not demonstrate deletion or export durability. [SHOW](https://clickhouse.com/docs/reference/statements/show), [system-log retention and upgrades](https://clickhouse.com/docs/reference/system-tables/overview), [MergeTree TTL](https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/mergetree#ttl).

**REASONED: TOTP requires the missing runtime and an enrolled XML human account.** Use the guarded interactive connection with that account. The password-only baseline succeeds without an OTP. The fixed account must reject missing or invalid OTP authentication and accept the correct password with a fresh valid code. Enter authentication material at prompts; do not reuse a previously accepted code for the positive control. [TOTP authentication](https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users#totp-authentication-configuration).

The service checks remain REASONED from the cited ClickHouse documentation and pinned sources. The following summarizes their scope and missing capabilities, not observed service results.

| Scope | Missing capabilities and exposed/fixed checks |
|---|---|
| Service-level checks | REASONED: check every service-level control above in isolated exposed and fixed ClickHouse deployments. Requires server/client binaries or a container runtime, allowed and disallowed client networks, TLS certificates, populated table and bounded resource fixtures, a fresh quota account, local-file and HTTPS fixtures, a scratch schema user, retained logs and an independent collector, and an enrolled XML TOTP account. Record matched positive controls, exact server/client versions, actual errors, merged configuration, default retirement on both interfaces, resource and quota enforcement, source and engine denials, and log collection/retention. Use a second test server for server-local quota accounting and replication HTTPS. Check replica credential enforcement with missing, wrong, and matching secrets, private binding, removal of 9009, and peer certificate verification. |

Local validation completed during authoring: all 12 XML documents/fragments passed well-formedness parsing; all three shell blocks passed `bash -n` and ShellCheck; the guard-conventions scanner reported no findings. Thirty rejection cases passed under `bash -u`, covering unresolved and embedded placeholders, angle brackets, `example.com`, empty input, missing marker/arguments, and invalid usernames. These checks do not validate ClickHouse configuration semantics or SQL execution. No service probes ran, no files were edited, and `run_all_checks.sh` was not run.

## Common mistakes

- `<listen_host>::</listen_host>` uncommented to reach the server from a laptop, with `default` still passwordless.
- A password set on `default` while `<networks>` still says `::/0`, leaving a privileged account reachable from anywhere.
- `https_port` added while `http_port` 8123 stays open beside it.
- Client TLS enabled while plaintext replication 9009 remains inherited, or replication HTTPS enabled without private binding and interserver credentials.
- Commenting out a setting in an override and expecting the inherited setting to disappear.
- Assuming `access_management` alone permits the complete `GRANT ALL` handoff.
- Adding a narrow role while leaving broad direct grants or inherited roles active.
- Treating `SELECT 1`, a timeout, or an absent fixture as proof of authorization or quota enforcement.
- Treating query logs as immutable audit storage, or assuming Cloud retention applies to OSS.

## Sources (checked September 2026)

- Listen address settings: https://clickhouse.com/docs/reference/settings/server-settings/settings/listen#listen_host
- Shipped server configuration and localhost default: https://raw.githubusercontent.com/ClickHouse/ClickHouse/9363bf26fecd0984e6e4e5a3c5ba2a4aba01cda6/programs/server/config.xml
- Shipped default-user configuration: https://raw.githubusercontent.com/ClickHouse/ClickHouse/b40982f9416bb4bc2d423d7e75ec384e79494b99/programs/server/users.xml
- User settings, password hashes, networks, and bootstrap capabilities: https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users
- Administrator bootstrap and account management: https://clickhouse.com/docs/concepts/features/security/access-rights
- SQL access storage: https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_path
- User directories and access-storage precedence: https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_directories
- CREATE USER and authentication methods: https://clickhouse.com/docs/reference/statements/create/user
- CREATE ROLE and combined privileges: https://clickhouse.com/docs/reference/statements/create/role
- SET ROLE and SET DEFAULT ROLE: https://clickhouse.com/docs/reference/statements/set-role
- Session role changes and their separate execution path: https://raw.githubusercontent.com/ClickHouse/ClickHouse/1163c482760fb0204e40f8fb5d81ffa1272bc9ea/src/Interpreters/Access/InterpreterSetRoleQuery.cpp
- Privileges, external sources, engines, and dictionaries: https://clickhouse.com/docs/reference/statements/grant
- Complete upstream source privilege registry: https://raw.githubusercontent.com/ClickHouse/ClickHouse/37c6c8c9bfc1de323e9a27711c5649352364bcba/src/Access/Common/AccessType.h
- CREATE SETTINGS PROFILE: https://clickhouse.com/docs/reference/statements/create/settings-profile
- Settings constraints and profile interactions: https://clickhouse.com/docs/concepts/features/configuration/settings/constraints-on-settings
- Query and per-user memory limits: https://clickhouse.com/docs/reference/settings/session-settings/max-memory-usage
- Execution-time limits and cancellation checkpoints: https://clickhouse.com/docs/reference/settings/session-settings/max-execution#max_execution_time
- CREATE QUOTA: https://clickhouse.com/docs/reference/statements/create/quota
- Quota accounting, exemptions, and resets: https://clickhouse.com/docs/concepts/features/configuration/server-config/quotas
- Query-class permissions and exceptions: https://clickhouse.com/docs/concepts/features/configuration/settings/permissions-for-queries
- Network ports and PostgreSQL TLS support: https://clickhouse.com/docs/concepts/features/security/network-ports
- Interserver listener address: https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver#interserver_listen_host
- Replication credentials, allow_empty, and plaintext interserver port: https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-http
- Replication HTTPS port and advertised hostname: https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-https
- Configuring TLS: https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls
- OpenSSL certificate and hostname verification: https://clickhouse.com/docs/reference/settings/server-settings/settings/other#openSSL
- Configuration merging, remove, and replace: https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files
- Docker default-user network access: https://clickhouse.com/docs/get-started/setup/self-managed/docker#managing-default-user
- Native client options and configuration: https://clickhouse.com/docs/concepts/features/interfaces/client
- HTTP interface and authentication: https://clickhouse.com/docs/concepts/features/interfaces/http
- curl empty-valued headers and header input from stdin: https://curl.se/docs/manpage.html#-H
- Native TOTP for XML users: https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users#totp-authentication-configuration
- ClickHouse 26.2 TOTP introduction: https://clickhouse.com/blog/clickhouse-release-26-02
- URL host allow-list: https://clickhouse.com/docs/reference/settings/server-settings/settings/remote#remote_url_allow_hosts
- URL table function: https://clickhouse.com/docs/reference/functions/table-functions/url
- File table function and user_files_path: https://clickhouse.com/docs/reference/functions/table-functions/file
- Remote table functions: https://clickhouse.com/docs/reference/functions/table-functions/remote
- HTTP dictionary sources: https://clickhouse.com/docs/reference/statements/create/dictionary/sources/http
- Engine and system-table grant enforcement: https://clickhouse.com/docs/reference/settings/server-settings/settings/access-control#access_control_improvements
- Executable script directory: https://clickhouse.com/docs/reference/settings/server-settings/settings/user#user_scripts_path
- Executable-UDF configuration discovery: https://clickhouse.com/docs/reference/settings/server-settings/settings/user-defined#user_defined_executable_functions_config
- Executable table function: https://clickhouse.com/docs/reference/functions/table-functions/executable
- Executable UDFs and execute_direct: https://clickhouse.com/docs/reference/functions/regular-functions/udf
- System-log configuration, retention, and schema changes: https://clickhouse.com/docs/reference/system-tables/overview
- Query-log configuration and query masking: https://clickhouse.com/docs/reference/settings/server-settings/settings/query
- Query logging session settings: https://clickhouse.com/docs/reference/settings/session-settings/log-queries
- Query-log schema: https://clickhouse.com/docs/reference/system-tables/query_log
- Session-log schema: https://clickhouse.com/docs/reference/system-tables/session_log
- SYSTEM FLUSH LOGS: https://clickhouse.com/docs/reference/statements/system#system-flush-logs
- Database audit logging: https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/database-audit-log
- ClickHouse Cloud console audit logging: https://clickhouse.com/docs/products/cloud/guides/security/audit-logging/console-audit-log
- SELECT and query-level settings: https://clickhouse.com/docs/reference/statements/select
- Exact distinct aggregation for the bounded memory fixture: https://clickhouse.com/docs/reference/functions/aggregate-functions/uniqExact
- CREATE TABLE: https://clickhouse.com/docs/reference/statements/create/table
- MergeTree syntax and TTL: https://clickhouse.com/docs/reference/engines/table-engines/mergetree-family/mergetree
- TinyLog engine: https://clickhouse.com/docs/reference/engines/table-engines/log-family/tinylog
- SHOW statements: https://clickhouse.com/docs/reference/statements/show
