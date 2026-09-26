# Neo4j: listen address, initial password, and TLS on Bolt and HTTPS

A packaged Neo4j 5 listens on `localhost` only by default and ships with authentication on, but with the well-known `neo4j`/`neo4j` credential, Bolt TLS at `DISABLED`, and plaintext HTTP enabled instead of HTTPS. Setting `server.default_listen_address=0.0.0.0` on such an install to "make it reachable" therefore exposes a database with a guessable password over plaintext. These defaults remain documented at the time of writing. The official Docker image is the exception: its entrypoint sets `server.default_listen_address=0.0.0.0` by default, so publishing a container port exposes the listener immediately, subject to the host's port binding and firewall. Do not assume the packaged loopback boundary protects a published container port. Docker's `NEO4J_AUTH=neo4j/REPLACE_WITH_LONG_RANDOM_VALUE` initializes authentication for a NEW database; it does not rotate an existing database's password. Supply credentials through the execution environment or secret-management mechanism, never as literal command-line arguments, and never use `NEO4J_AUTH=none`, which disables authentication. See [network connectors](https://neo4j.com/docs/operations-manual/current/configuration/connectors/), [Docker authentication](https://neo4j.com/docs/operations-manual/current/docker/introduction/), [Docker configuration](https://neo4j.com/docs/operations-manual/current/docker/configuration/), and the [official Neo4j 5 entrypoint](https://raw.githubusercontent.com/neo4j/docker-neo4j/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/docker-entrypoint.sh).

Examples use current configuration names, also used in Neo4j 5 except where a newer option is explicitly marked. Neo4j 4.x names differ. Configuration belongs in `neo4j.conf` unless another file is named.

## 1. Change the initial password before allowing remote access

For a packaged, isolated first start, block network access and retain the loopback listen address. Start with authentication enabled, then change the initial password through prompts:

```bash
(
  unset NEO4J_PASSWORD || { echo "cannot clear NEO4J_PASSWORD"; exit 1; }
  cypher-shell -a bolt://localhost:7687 -u neo4j --change-password
)
```

Enter the initial password and its long, randomly generated replacement at the prompts. This plaintext loopback connection is only for isolated bootstrap before TLS setup. Use certificate-verified TLS for an already configured remote server.

The documented `neo4j-admin dbms set-initial-password` interface is intended for one-time use before the database's first start, not password rotation. Its `--require-password-change=false` option avoids requiring another change at first login. It takes a positional password. The documentation warns that typing a password into the command stores it in shell history. Secret-store substitution and disabling shell history do not remove that password from process arguments such as `/proc/<pid>/cmdline`; there is no documented stdin or password-file option to substitute here. Cypher Shell provides the prompted alternative. For automation, it also documents `NEO4J_PASSWORD`: supply it through the execution environment, never expand it into `-p`. Environment delivery does not protect against every form of local process inspection. See [initial-password configuration](https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/) and [Cypher Shell](https://neo4j.com/docs/operations-manual/current/cypher-shell/).

At the time of writing, the default minimum password length is 8 characters. `dbms.security.auth_minimum_password_length` was introduced in 5.3; a minimum is not a recommendation to use an eight-character password. Leave `dbms.security.auth_enabled` at its default `true`. The authentication documentation reserves disabling it for recovery with network access blocked. See [configuration changes in Neo4j 5](https://neo4j.com/docs/upgrade-migration-guide/current/version-5/changelogs/configuration-settings/) and [authentication configuration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/).

## 2. Bind deliberately

`server.default_listen_address` supplies the host when a connector's listen address omits it. At the time of writing, `server.bolt.listen_address` defaults to `:7687`, `server.http.listen_address` to `:7474`, and `server.https.listen_address` to `:7473`. Keep the default `localhost` unless remote clients are deliberate, then prefer a specific private address over `0.0.0.0`. See [network connector configuration](https://neo4j.com/docs/operations-manual/current/configuration/connectors/).

Online backup is Enterprise-only. Its `server.backup.listen_address` defaults to the explicit `127.0.0.1:6362` at the time of writing, so changing the shared listen address does not widen this default; keep it off external interfaces. Community readers should not expect an online-backup listener. See [online backup](https://neo4j.com/docs/operations-manual/current/backup-restore/online-backup/) and the [configuration reference](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/).

Firewall per [cloud-firewalls.md](cloud-firewalls.md) or [host.md](host.md), and widen access only after TLS and authentication are configured.

```properties
server.default_listen_address=REPLACE_WITH_PRIVATE_IP
```

### Enterprise cluster and monitoring listeners (Neo4j 5.26)

The version-5 vendor pages checked on 2026-09-26 identify themselves as **5.26 (LTS)**. The [ports page](https://neo4j.com/docs/operations-manual/5/configuration/ports/#_cluster) says Enterprise opens cluster ports even on a single server, whether or not it is in a multi-process configuration. Do not infer that a standalone Enterprise deployment has only the client and backup listeners. Discovery and routing have the conditions below.

| Traffic | Listen setting and default | Advertised setting and default | Condition |
| --- | --- | --- | --- |
| Discovery v1 | `server.discovery.listen_address=:5000` | `server.discovery.advertised_address=:5000` | When discovery v1 runs; deprecated since 5.23. |
| Transaction shipping and catch-up, also capable of serving backups | `server.cluster.listen_address=:6000` | `server.cluster.advertised_address=:6000` | Enterprise; also discovery v2 when selected. |
| Raft communication | `server.cluster.raft.listen_address=:7000` | `server.cluster.raft.advertised_address=:7000` | Enterprise. |
| Server-side routing over an additional Bolt connector | `server.routing.listen_address=:7688` | `server.routing.advertised_address=:7688` | Server-side routing enabled; `dbms.routing.enabled` defaults to `true`. |

All four listen defaults inherit their host from `server.default_listen_address`, whose packaged default is `localhost`. Their advertised defaults inherit `server.default_advertised_address`, also `localhost`; advertising an address does not restrict a bind. Set advertised addresses to names or private IPs reachable by the other members, and match any changed ports. See the [configuration reference](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/#config_server.cluster.listen_address) and [cluster settings](https://neo4j.com/docs/operations-manual/5/clustering/settings/).

Discovery v2 is documented for deployment from 5.23 and uses 6000 instead of a separate 5000 listener. The 5.26 reference still defaults `dbms.cluster.discovery.version` to `V1_ONLY`; `V2_ONLY` runs only v2, while `V1_OVER_V2` and `V2_OVER_V1` run both. Do not drop 5000 from the inventory merely because the version is 5.23 or later. The selector and v2 endpoints carry introduction labels of 5.22, while the deployment instructions describe v2 from 5.23. See [the selector](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/#config_dbms.cluster.discovery.version) and [deployment instructions](https://neo4j.com/docs/operations-manual/5/clustering/setup/deploy/#cluster-example-configure-a-three-primary-cluster).

Keep cluster ports reachable only by cluster members on a private network, with a firewall allowlist even after enabling TLS. Port 6000 permits **unauthenticated database replication** by default, and a backup client can use it too. Protecting 6362 alone does not protect this data path. For a single-server deployment without clustering, explicitly retain loopback on the cluster listeners even when client connectors need a private remote bind:

```properties
# Enterprise 5.26; discovery setting applies when v1 runs.
server.discovery.listen_address=localhost:5000
server.cluster.listen_address=localhost:6000
server.cluster.raft.listen_address=localhost:7000
server.routing.listen_address=localhost:7688
```

For a cluster, use the intended private interface instead of those loopback hosts. Enable the SSL framework's **`cluster`** scope on every member: it covers discovery, transaction shipping, Raft, and server-side routing, including 7688. The policy is disabled by default, so default cluster traffic has neither TLS encryption nor TLS client-certificate authentication. The documented default `client_auth=REQUIRE` only takes effect once the policy is enabled; a database password does not secure the unauthenticated replication endpoint. See [cluster ports](https://neo4j.com/docs/operations-manual/5/configuration/ports/#_cluster) and [intra-cluster SSL configuration](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-cluster-config).

Before enabling it, create `certificates/cluster`, its `trusted` and `revoked` directories, and install each member's own PKCS#8 PEM `private.key` and matching `public.crt`. Make the key readable only by the Neo4j service account. Populate each member's trust directory with the approved peer certificates or their trusted CA as described by the vendor; retain `trust_all=false`. Cluster certificates must include both **TLS Web Server Authentication** and **TLS Web Client Authentication** in Extended Key Usage, because each member authenticates as a client to its peers. Inspect each member's certificate with `openssl x509 -in public.crt -noout -text` and look for both usages under `X509v3 Extended Key Usage`. In `public.crt`, concatenate PEM certificates leaf first, then toward the root. See the [vendor certificate requirements](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-certificates).

Use the same policy settings on every member, with distinct private keys and certificates:

```properties
dbms.ssl.policy.cluster.enabled=true
dbms.ssl.policy.cluster.base_directory=certificates/cluster
dbms.ssl.policy.cluster.private_key=private.key
dbms.ssl.policy.cluster.public_certificate=public.crt
dbms.ssl.policy.cluster.client_auth=REQUIRE
```

This does not enable TLS on the separate 6362 backup connector, which uses the **`backup`** scope, or replace the client-facing Bolt and HTTPS policies below. See [SSL policy defaults](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-configuration) and [backup SSL](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-backup-config).

**Prometheus is separate from clustering.** Enterprise's `server.metrics.prometheus.enabled` defaults to `false`; if enabled on either a standalone server or a cluster member, `server.metrics.prometheus.endpoint` defaults to the explicit `localhost:2004`. That default does not inherit a widened shared host; an explicitly hostless `:2004` does. No Prometheus scope is listed in the SSL framework, so do not assume the cluster policy protects metrics. Keep it loopback-only or reachable only by authorized monitoring systems. Graphite's `server.metrics.graphite.server=:2003` is an outbound destination, disabled by default, not a Neo4j listener. JMX 3637 and debugging 5005 in the ports table require explicit JVM options; do not enable remote management or debugging as part of this baseline. See [Prometheus settings](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/#config_server.metrics.prometheus.endpoint) and [monitoring ports](https://neo4j.com/docs/operations-manual/5/configuration/ports/#_graphite_monitoring).

**Docker:** at the guide's pinned entrypoint commit, the default `server.default_listen_address=0.0.0.0` applies to both editions and widens all four hostless cluster listen defaults when those listeners run. It does not override explicit listener hosts, the backup default, or the Prometheus default. Enterprise additionally defaults the four cluster advertised addresses to the container hostname and their respective ports, and maps legacy `NEO4J_causal__clustering_*` advertised-address variables to the newer names. Explicit configuration overrides Docker defaults; environment configuration then overrides file values. For a real cluster, use peer-reachable private addresses and the cluster TLS policy, and restrict container-network access as well as host publication. All three Dockerfile variants declare only `EXPOSE 7474 7473 7687`; that declaration is not a listener inventory or firewall. See the [entrypoint](https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/docker-entrypoint.sh#L547-L617) and [Debian Dockerfile](https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/Dockerfile-debian#L53).

For the single-server loopback overrides above, use these Docker environment entries. They are derived from the pinned entrypoint's translation rules: prefix `NEO4J_`, replace each setting underscore with `__`, and each dot with `_`. The entrypoint reverses that translation before writing the setting. See [the naming convention](https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/docker-entrypoint.sh#L549-L555) and [the translation](https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/docker-entrypoint.sh#L607).

| Environment name | Value |
| --- | --- |
| `NEO4J_server_discovery_listen__address` | `localhost:5000` |
| `NEO4J_server_cluster_listen__address` | `localhost:6000` |
| `NEO4J_server_cluster_raft_listen__address` | `localhost:7000` |
| `NEO4J_server_routing_listen__address` | `localhost:7688` |

## 3. TLS on Bolt and HTTPS, HTTP off

Put a PKCS#8 PEM private key and certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)) under each policy directory. Use the service account as owner, normally `neo4j:neo4j`, with key mode `0400` and certificate mode `0644`. Legacy PKCS#1 keys, whose PEM header labels the key type as RSA rather than the generic PKCS#8 form, are deprecated; convert them to the documented PKCS#8 format.

`server.bolt.tls_level=REQUIRED` refuses unencrypted Bolt; `OPTIONAL` continues accepting it. `server.http.enabled=false` removes the plaintext HTTP endpoint. This baseline uses server authentication through TLS and database credentials for clients. For machine clients that can hold certificates, replace `dbms.ssl.policy.bolt.client_auth=NONE` with `dbms.ssl.policy.bolt.client_auth=REQUIRE` to add mutual TLS, and configure the policy's trusted certificates and the clients' certificates and private keys. See the [SSL framework](https://neo4j.com/docs/operations-manual/current/security/ssl-framework/).

```properties
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.base_directory=certificates/bolt
dbms.ssl.policy.bolt.private_key=private.key
dbms.ssl.policy.bolt.public_certificate=public.crt
dbms.ssl.policy.bolt.client_auth=NONE
server.bolt.tls_level=REQUIRED

dbms.ssl.policy.https.enabled=true
dbms.ssl.policy.https.base_directory=certificates/https
dbms.ssl.policy.https.private_key=private.key
dbms.ssl.policy.https.public_certificate=public.crt
dbms.ssl.policy.https.client_auth=NONE
server.https.enabled=true
server.http.enabled=false
```

## 4. Users and roles

Use a separate account per application instead of sharing `neo4j` ([authentication.md](authentication.md)). Community Edition supports multiple native users, but every user has implied administrator privileges. It has no roles or fine-grained privilege system. A separate Community username does not create a restricted database identity. See [Manage users](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-users/).

For native authentication, failed logins trigger `dbms.security.auth_lock_time` after `dbms.security.auth_max_failed_attempts`. At the time of writing, these defaults remain `5s` and `3`. These controls do not establish the lockout policy of an external identity provider. See [authentication configuration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/).

**Enterprise-only: restrict the application's database, labels, and properties.** An application credential should expose only the data it needs. Enterprise supports built-in roles `reader`, `editor`, `publisher`, `architect`, and `admin`, plus custom roles. `editor` and `publisher` provide write capabilities; choose only the required privileges for writers. The built-in `reader` role grants broad graph reads and access across databases; it is not a database-specific application role. Create a custom role for narrower access and keep administrator credentials out of application configuration. The example permits reading two properties on `Product` nodes in the existing `neo4j` database. See [built-in roles](https://neo4j.com/docs/operations-manual/current/authentication-authorization/built-in-roles/), [database access privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/database-administration/), and [MATCH privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/privileges-reads/).

Run this Cypher as an administrator in an interactive session with persistent history disabled. Substitute the password there; do not pass this password-bearing statement as a Cypher Shell command-line argument. The guarded session in Verify can be used with the administrator username and `-d system`.

```cypher
CREATE ROLE catalog_reader;

CREATE USER catalog_app
SET PASSWORD 'REPLACE_WITH_LONG_RANDOM_VALUE' CHANGE NOT REQUIRED
SET HOME DATABASE neo4j;

GRANT ACCESS ON DATABASE neo4j TO catalog_reader;
GRANT MATCH {sku, name} ON GRAPH neo4j NODES Product TO catalog_reader;
GRANT ROLE catalog_reader TO catalog_app;

SHOW USER catalog_app PRIVILEGES AS COMMANDS;
```

Use a fresh application account and role. Adding a narrow role to an existing account does not remove its broader roles. Review all effective privileges, including inherited `PUBLIC` grants, before switching the application. These are current documented user, role, and privilege commands; they do not depend on newer property predicates, tags, or authentication rules. See [Manage roles](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-roles/) and [showing user privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/).

Community Edition cannot enforce these grants. Restrict direct database access to trusted services and enforce end-user authorization in the application or a fronting service that controls the operations exposed.

MFA: native password authentication has no second-factor step. Enterprise can delegate authentication to an OIDC provider whose policy enforces MFA ([oidc-integration.md](oidc-integration.md)). Enterprise's LDAP `simple` authentication uses a username and password; that alone is not MFA. Confirm second-factor enforcement and ensure alternate native or password paths cannot bypass it ([mfa.md](mfa.md)). For services that can hold client certificates, mutual TLS adds a possession factor alongside database credentials. Put every human access path to the host and application behind MFA. See [SSO integration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/sso-integration/) and [LDAP integration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/ldap-integration/).

## 5. Restrict procedures, file import, and outbound requests

Authentication and roles decide who connects and what data they can touch. Enterprise can additionally restrict procedure execution and data loading, but read-only graph access does not provide those restrictions by itself. Community has no equivalent role privileges, so application controls, plugin configuration, and network egress restrictions carry the containment.

**Enterprise-only: deny capabilities the application does not need.** At the time of writing, the default `PUBLIC` role allows procedure execution, user-defined functions, and data loading. For the application above, if it needs ordinary Cypher queries but none of those capabilities, run as an administrator:

```cypher
DENY EXECUTE PROCEDURES * ON DBMS TO catalog_reader;
DENY EXECUTE FUNCTIONS * ON DBMS TO catalog_reader;
DENY LOAD ON ALL DATA TO catalog_reader;

SHOW USER catalog_app PRIVILEGES AS COMMANDS;
```

These denials affect users holding `catalog_reader`; they do not change `PUBLIC` for every user. Built-in Cypher functions remain executable. A narrower `GRANT` cannot override a matching `DENY`. If an application needs selected extensions, design explicit execution grants and review inherited `PUBLIC` privileges instead of appending exceptions to these blanket denials. See [PUBLIC privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/built-in-roles/), [EXECUTE privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/dbms-administration/dbms-execute-privileges/), and [GRANT and DENY semantics](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/).

`LOAD ON ALL DATA` requires Enterprise Neo4j 5.13 or later; CIDR-specific load privileges followed in 5.16. Both are present in current documentation. See [LOAD privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/load-privileges/) and [Neo4j 5 additions](https://neo4j.com/docs/cypher-manual/5/deprecations-additions-removals-compatibility/).

Do not grant application roles boosted execution. APOC documents that boosted procedures can bypass graph and loading restrictions. Keep these additional boundaries:

- Keep `dbms.security.procedures.unrestricted` empty unless a reviewed extension specifically requires access to internal APIs. Unrestricted extensions can bypass security, as the [configuration reference](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/) warns. Narrow `dbms.security.procedures.allowlist` to the procedures and functions the workload needs; its default is `*` at the time of writing. This controls which extensions load, rather than providing Community with per-user execution privileges. Install only necessary plugins. See [securing extensions](https://neo4j.com/docs/operations-manual/current/security/securing-extensions/).
- If APOC is installed, put its settings in `apoc.conf`, not `neo4j.conf`, for Neo4j 5 and later. Retain `apoc.import.file.enabled=false` unless local file import is required, and keep `apoc.import.file.use_neo4j_config=true` so Neo4j's file-access and configured import-directory checks still apply. These are the defaults in the [APOC configuration reference](https://neo4j.com/docs/apoc/current/config/).
- Set `dbms.security.allow_csv_import_from_file_urls=false` when local `LOAD CSV` is unnecessary. The current [Neo4j configuration reference](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/) directly documents its default as `true`. The APOC security overview disagrees on that default and uses an inconsistent APOC setting spelling; use the configuration references for these values and the dotted `apoc.import.file.use_neo4j_config` spelling.
- `LOAD CSV` and APOC procedures such as `apoc.load.json` and `apoc.load.jdbc` can make outbound requests, creating an SSRF risk when queries can select internal destinations. `apoc.load.jdbc` belongs to APOC Extended and requires a compatible JDBC driver; see its [vendor reference](https://neo4j.com/labs/apoc/5/overview/apoc.load/apoc.load.jdbc/). Restrict egress so queries cannot reach internal services or cloud metadata at `169.254.169.254` ([egress-metadata.md](egress-metadata.md)). Where supported, set `internal.dbms.cypher_ip_blocklist` to block internal CIDRs; check compatibility with the installed version and retain network egress restrictions. See [APOC security guidance](https://neo4j.com/docs/apoc/current/security-guidelines/) and [Protecting against SSRF](https://support.neo4j.com/s/article/8584271681427-Protecting-against-Server-Side-Request-Forgery-SSRF), the current destination of the former `https://neo4j.com/developer/kb/protecting-against-ssrf/` URL.

## 6. Bound transaction memory and set a default timeout

An authenticated client can exhaust resources with expensive queries. The following settings are available in Community and Enterprise in the current configuration reference. These values are example budgets, not vendor defaults or universal production sizing:

```ini
db.transaction.timeout=30s
db.memory.transaction.max=64m
db.memory.transaction.total.max=256m
dbms.memory.transaction.total.max=512m
```

The memory limits cover one transaction, all transactions in one database, and all transactions on the server, respectively. Size them against the configured heap and measured workload, leaving room for other heap consumers. Transactions that reach tracked memory limits are terminated. Accounting is estimated and workload-dependent, so these limits do not describe exact process memory consumption. See [transaction memory configuration](https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/) and the [exact settings](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/).

The timeout is a default, not a hard ceiling against hostile clients. A client-supplied transaction timeout can override it with a larger value. Restrict direct database access and enforce application request budgets too. The current Python driver reference specifically distinguishes servers 4.2 through 5.2 inclusive, which ignore overrides larger than the server default. See [transaction timeout behavior](https://neo4j.com/docs/operations-manual/current/database-internals/transaction-management/) and [driver timeout semantics](https://neo4j.com/docs/api/python-driver/current/api.html).

## 7. Retain security events without unnecessary query secrets

**Enterprise-only:** retain `security.log` and `query.log`. With authentication enabled, the security log records login events, administration commands, and authorization failures. Keep successful-login events as well. Configure query logging while suppressing parameter values and obfuscating literals:

```ini
dbms.security.log_successful_authentication=true
db.logs.query.enabled=VERBOSE
db.logs.query.parameter_logging_enabled=false
db.logs.query.obfuscate_literals=true
db.logs.query.early_raw_logging_enabled=false
```

At the time of writing, `VERBOSE` is already the current default and records query starts and finishes. Setting it explicitly records the intended policy. Protect and collect both logs, and review retention and rotation in `conf/server-logs.xml`. See [logging configuration and edition availability](https://neo4j.com/docs/operations-manual/current/monitoring/logging/).

When changing literal obfuscation dynamically, clear cached queries as an administrator so the change affects them immediately:

```cypher
CALL db.clearQueryCaches();
```

On versions supporting error obfuscation, also set:

```ini
db.logs.query.obfuscate_errors=true
```

The Neo4j 5 configuration reference marks `db.logs.query.obfuscate_errors` as introduced in **5.26.21**; the current-series reference marks it as introduced in **2026.01.3**. It is therefore available in Neo4j 5.26.21 and later 5.26 patches, as well as current releases that include it. Check the exact installed version before adding the setting; do not add it to an older release that lacks it. Literal obfuscation alone does not sanitize error details. See the [Neo4j 5 setting](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/#config_db.logs.query.obfuscate_errors) and the [current-series setting](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/#config_db.logs.query.obfuscate_errors).

Obfuscation does not hide every identifier or query detail. Treat the logs as sensitive.

Community provides operational logs and optional HTTP request logging:

```ini
dbms.logs.http.enabled=true
```

Enable HTTP request logging only when an HTTP/HTTPS connector is in use. It does not provide equivalent Bolt, query, or security auditing; collect application and fronting-layer events as well. See [available log files](https://neo4j.com/docs/operations-manual/current/monitoring/logging/).

## Verify

**Service verification status: REASONED, not demonstrated.** The authoring environment has no Neo4j server, Cypher Shell, Docker, or Podman available, and no authorized running deployment was supplied. All service comparisons below require capabilities missing here. Run exposed/fixed comparisons only in disposable test deployments. Record server, edition, client, and plugin versions alongside results.

Local validation of this revision: all seven shell blocks passed `bash -n` and ShellCheck 0.11.0. Guard-only checks exercised placeholder and malformed marker/count rejection in all six guarded blocks. Eight configuration fragments passed basic key/value parsing and duplicate-key checks. These are local syntax checks, not Neo4j configuration validation or service verification. Both generated bundles were rebuilt and the whole-corpus gate suite passed with ShellCheck 0.11.0; no Neo4j service was run.

For each guarded block, replace the hostname inside the single quotes and paste the whole block. The blocks assume ordinary shell builtins; do not insert a literal apostrophe into the quoted substitution. A fragment pasted below the guards is unguarded.

Use `neo4j+s://` for certificate-verified routing connections or `bolt+s://` for a certificate-verified direct connection. The `+ssc` variants, including `neo4j+ssc://`, skip certificate verification and do not establish server identity; reserve them for development. The checks below use direct Bolt to avoid routing discovery obscuring the result. Install the signing CA in the Cypher Shell client's trust store when necessary; OpenSSL's `-CAfile` and curl's `--cacert` do not configure Cypher Shell's trust. See [TLS connection schemes](https://neo4j.com/docs/operations-manual/current/security/ssl-framework/).

### Listener inventory

**REASONED: requires the Neo4j service's network namespace and, for the Enterprise comparisons, a standalone Enterprise server and an Enterprise cluster, unavailable in the authoring environment.** Run this block inside that namespace. The substituted hostname identifies the deployment being inspected; it does not make `ss` inspect a remote machine.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "expected exactly one hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the hostname inside the quotes; not probing"
      exit 1
      ;;
    *)
      # Run inside the Neo4j service's network namespace.
      # The hostname is a confirmation only; ss does not connect to it.
      ss -tlnp
      ;;
  esac
)
```

Compare an exposed disposable installation with the configured state. Expect Bolt 7687 and HTTPS 7473 on the intended address after setup, with plaintext HTTP 7474 absent. If Enterprise online backup is running, confirm 6362 remains loopback-only for this baseline. This backup observation does not apply to Community. Confirm the retained listeners actually serve the positive queries below; an empty inventory is not a secure-service result. See [ports](https://neo4j.com/docs/operations-manual/current/configuration/ports/) and [online backup](https://neo4j.com/docs/operations-manual/current/backup-restore/online-backup/).

**REASONED, Enterprise listener comparisons:** also read every listener for 5000 (discovery v1 only), 6000, 7000, and 7688 (server-side routing), including configured replacement ports and IPv6 bindings. In the exposed disposable state, a widened shared host can expose these even on a standalone server; in the fixed single-server state, expect loopback binds. In a cluster, expect the intended private binds and peer-reachable advertised addresses, with firewall access confined to members. Under `V2_ONLY`, do not require 5000; discovery shares 6000. Check 2004 only if Prometheus is enabled, on loopback or the explicitly restricted monitoring interface. There should be no inbound Graphite 2003 listener from enabling its exporter; investigate any JMX 3637 or debugger 5005 listener against the JVM configuration. Inspect the container's namespace as well as host publication rules for Docker. These expectations follow the [5.26 ports inventory](https://neo4j.com/docs/operations-manual/5/configuration/ports/#_cluster) and [setting defaults](https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/).

### Cluster mutual TLS

**REASONED, not demonstrated: the authoring host forbids opening listeners without an isolated network namespace, and has none.** A disposable Enterprise cluster and its certificates are required. These comparisons remain tracked in TODO row 1.98. A listener inventory does not prove TLS or peer authentication. The vendor's [Nmap cipher enumeration](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-cluster-config) establishes that TLS is offered, not rejection of unauthenticated peers. The OpenSSL procedure below is reasoned from the [documented cluster mutual-authentication policy](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-cluster-config); it is not a vendor-documented cluster-port check.

Run from an allowed peer location against each member and every active cluster listener: 6000, 7000, 5000 when discovery v1 runs, and 7688 when server-side routing runs, or their configured replacements. Substitute the member's certificate DNS name, cluster port, and direct client Bolt TLS URI inside the quotes. The Bolt URI uses the client connector, normally 7687, not the cluster port. Install the Bolt signing CA in Cypher Shell's trust store as described above; the command assumes section 3's Bolt policy and prompts for the administrator password.

Provide `ca.pem` containing the cluster server's trusted signing CA; `member.crt` and `member.key` for a trusted test member; and `untrusted.crt` and `untrusted.key` for an otherwise valid certificate signed by a different CA absent from every member's trust directory. Both certificates need the EKUs above, current validity, and matching keys. Supply each issuing chain in `member-chain.pem` or `untrusted-chain.pem`, starting with the issuing CA; for direct root issuance, use that root certificate. Keep the private keys protected and do not add the untrusted CA to the cluster's trust directory.

Use OpenSSL 3 and a `timeout` command supporting `15s`. `-cert_chain` supplies the client chain, `-verify_hostname` and `-verify_return_error` enforce server verification, and `-ign_eof` keeps the client reading after stdin closes so a later TLS alert is visible. The time limit bounds that wait. See [OpenSSL s_client](https://docs.openssl.org/3.0/man1/openssl-s_client/) and [timeout](https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html).

```bash
(
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLUSTER_DNS_NAME' 'REPLACE_WITH_CLUSTER_PORT' 'REPLACE_WITH_BOLT_TLS_URI'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "expected a DNS name, cluster port, and Bolt TLS URI; not probing"; exit 1; }
  case "$1|$2|$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*)
      echo "substitute all three values inside the quotes; not probing"; exit 1 ;;
  esac
  case "$1" in
    ""|*[!abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-]*) echo "supply the member's certificate DNS name; not probing"; exit 1 ;;
  esac
  case "$2" in
    ""|*[!0123456789]*) echo "supply a numeric cluster port; not probing"; exit 1 ;;
  esac
  [ "${#2}" -le 5 ] && [ "$2" -ge 1 ] && [ "$2" -le 65535 ] || {
    echo "cluster port must be 1 through 65535; not probing"; exit 1;
  }
  case "$3" in
    bolt+s://?*) ;;
    *) echo "supply a direct bolt+s:// URI; not probing"; exit 1 ;;
  esac
  [ -r ca.pem ] && [ -r member.crt ] && [ -r member.key ] &&
    [ -r member-chain.pem ] && [ -r untrusted.crt ] &&
    [ -r untrusted.key ] && [ -r untrusted-chain.pem ] || {
      echo "provide the CA, both certificates, keys, and issuing chains; not probing"; exit 1;
    }
  unset NEO4J_PASSWORD || { echo "cannot clear NEO4J_PASSWORD; not probing"; exit 1; }

  echo "(a) No client certificate"
  timeout 15s openssl s_client -connect "$1:$2" -servername "$1" \
    -verify_hostname "$1" -verify_return_error -CAfile ca.pem \
    -state -brief -ign_eof </dev/null
  printf 'no-client exit=%s\n' "$?"

  echo "(b) Certificate from an untrusted CA"
  timeout 15s openssl s_client -connect "$1:$2" -servername "$1" \
    -verify_hostname "$1" -verify_return_error -CAfile ca.pem \
    -cert untrusted.crt -key untrusted.key -cert_chain untrusted-chain.pem \
    -state -brief -ign_eof </dev/null
  printf 'untrusted-client exit=%s\n' "$?"

  echo "(c) Trusted member certificate"
  timeout 15s openssl s_client -connect "$1:$2" -servername "$1" \
    -verify_hostname "$1" -verify_return_error -CAfile ca.pem \
    -cert member.crt -key member.key -cert_chain member-chain.pem \
    -state -brief -ign_eof </dev/null
  printf 'trusted-client exit=%s\n' "$?"

  echo "(d) Cluster status: enter the administrator password at the prompt"
  cypher-shell -a "$3" -u neo4j -d system 'SHOW SERVERS;'
)
```

**REASONED outcomes:** in a disposable, network-isolated comparison, first enable cluster TLS with `client_auth=NONE` on every member: all three TLS probes should complete a handshake. Then use `client_auth=REQUIRE` with `trust_all=false` on every member: (a) must be rejected for lacking a client certificate, (b) for an untrusted issuer, and (c) must complete the handshake. This TLS-enabled baseline isolates the client-authentication control. Against the default TLS-disabled cluster policy, `s_client` cannot complete a TLS handshake; that failure is not evidence of peer authentication. See [policy settings and defaults](https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-configuration).

For (a) and (b), look for a received fatal TLS alert, such as `certificate required`, `unknown ca`, `bad certificate`, or `handshake failure`; correlate generic alerts with the member's logs to establish the certificate rejection reason. For (c), require a negotiated protocol and cipher, verified server identity, and no subsequent client-certificate rejection. `Verification: OK` alone verifies only the server; in TLS 1.3 a client can print connection details before receiving the server's rejection. Inspect the full output and correlate the member's logs if acceptance is ambiguous. Refusal, DNS failure, reset, local key-loading failure, or timeout alone proves nothing about mutual TLS. Exit 124 only reports that the wait expired, even if the handshake completed first. These probes do not speak the cluster application protocol. See [TLS client-certificate validation](https://www.rfc-editor.org/rfc/rfc8446.html#section-4.4.2.4) and [TLS alerts](https://www.rfc-editor.org/rfc/rfc8446.html#section-6.2).

Run (d) in both states and after enabling the final policy on all members. The documented [`SHOW SERVERS` cluster check](https://neo4j.com/docs/operations-manual/5/clustering/setup/deploy/#cluster-example-configure-a-three-primary-cluster) must return the expected members with state `Enabled` and health `Available`. Missing or unavailable members invalidate the positive control. This checks cluster status, not every replication or routing operation; successful authorized discovery, replication, and routed-query comparisons remain part of TODO row 1.98. A closed port or failed cluster is not evidence that mutual TLS works.

### Transport, default password, and prompted bootstrap

**REASONED: requires an isolated fresh installation, a reachable TLS deployment, client tools, and an external test vantage, unavailable here.** Supply the signing CA as `ca.pem`. For a publicly trusted certificate only, the explicit `-CAfile ca.pem` and `--cacert ca.pem` options and the corresponding file-readability checks may be omitted if the clients' default stores already trust its issuer. Keep them for a private or self-signed CA. Run against the actual deployment hostname, including each relevant public IPv4/IPv6 path from another host.

The first password prompt below is deliberately for the public default password only. Never enter a real password into the plaintext test.

The OpenSSL command and Cypher Shell checks below assume `client_auth=NONE`. If Bolt requires mutual TLS, add `-cert client.crt -key client.key` to the guarded OpenSSL command, using a client certificate trusted by the server. Without it, the server can refuse the client even when OpenSSL prints `Verification: OK` for the server certificate. Use a certificate-capable client with its certificate configured for the remaining Bolt comparisons. Keep `-verify_hostname` and `-verify_return_error`: merely connecting with `s_client` does not enforce the required server identity checks.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "expected exactly one hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the hostname inside the quotes; not probing"
      exit 1
      ;;
    *)
      [ -r ca.pem ] || { echo "provide the signing CA in ca.pem"; exit 1; }
      unset NEO4J_PASSWORD || { echo "cannot clear NEO4J_PASSWORD"; exit 1; }

      openssl s_client -connect "$1:7687" -servername "$1" \
        -verify_hostname "$1" -verify_return_error -CAfile ca.pem </dev/null

      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
        -o /dev/null \
        -w 'http7474=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "http://$1:7474/"

      echo "Plaintext transport test: enter only the public default password neo4j."
      cypher-shell -a "bolt://$1:7687" -u neo4j 'RETURN 1 AS ok;'

      echo "Default-password test over TLS: enter neo4j at the password prompt."
      cypher-shell -a "bolt+s://$1:7687" -u neo4j 'RETURN 1 AS ok;'

      echo "Positive control over TLS: enter the rotated administrator password."
      cypher-shell -a "bolt+s://$1:7687" -u neo4j 'RETURN 1 AS ok;'
      ;;
  esac
)
```

**REASONED comparisons:**

- With Bolt TLS `DISABLED`, the TLS handshake cannot establish the configured TLS service. With the fixed policy, certificate and hostname verification must succeed and the authenticated TLS query must return `ok=1`. A successful handshake alone does not prove that plaintext is refused.
- With plaintext Bolt accepted, the plaintext test reaches authentication: a query result, password-change requirement, or authentication error proves that plaintext reached the service. With `REQUIRED`, it must fail at the transport layer, while the TLS positive control succeeds.
- With the original HTTP endpoint exposed, the 7474 request returns an HTTP status. With the fixed policy, that endpoint must not answer. Curl exit `7` means a connection could not be established; it can also indicate a local socket or routing problem. Exit `6` is DNS failure and `28` is a timeout. These are inconclusive without evidence that the intended host and path were reached. A connection refusal is useful only after confirming the intended host and path, alongside the working TLS service and listener inventory.
- Before bootstrap rotation, the default password is accepted, including a response requiring a password change. After rotation, it must fail authentication while the replacement succeeds. Distinguish a temporary lockout from an invalid password; allow the configured lock period to expire before the positive control. During the isolated bootstrap reproduction, inspect process arguments to confirm the prompted secrets do not appear there.

The expected distinctions follow [connector TLS behavior](https://neo4j.com/docs/operations-manual/current/configuration/connectors/), [initial-password behavior](https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/), and [native authentication](https://neo4j.com/docs/operations-manual/current/authentication-authorization/).

### Interactive application and administrative checks

**REASONED: requires Cypher Shell and the configured deployment, unavailable here.** This session prompts for the application password. `--history disable` requires Cypher Shell 2025.08 or later; earlier shells documenting this option use `--history in-memory` to avoid persistent history.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "expected exactly one hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the hostname inside the quotes; not probing"
      exit 1
      ;;
    *)
      unset NEO4J_PASSWORD || { echo "cannot clear NEO4J_PASSWORD"; exit 1; }
      cypher-shell -a "bolt+s://$1:7687" -u catalog_app -d neo4j --history disable
      ;;
  esac
)
```

For administrative work, replace the non-secret username with the administrator account. Use `-d system` for account and privilege administration and `-d neo4j` for the fixture queries. Community readers must use an existing Community account; the Enterprise setup above does not create a restricted Community account. See [Cypher Shell](https://neo4j.com/docs/operations-manual/current/cypher-shell/).

Start each application comparison with:

```cypher
RETURN 1 AS ok;
```

Expect `ok=1` in both states. Failure to connect or run this query prevents interpreting later denials as successful controls.

### Scoped graph access

**REASONED, Enterprise-only: requires an Enterprise runtime and seeded fixtures, unavailable here.** In an empty disposable `neo4j` database, seed as an administrator:

```cypher
CREATE (:Product {
  sku: 'SECURECONFIG-SKU-1',
  name: 'Secureconfig test product',
  internalNote: 'SECURECONFIG_PRIVATE_PROPERTY_CANARY'
});

CREATE (:SecureconfigPrivateCanary {
  marker: 'SECURECONFIG_PRIVATE_NODE_CANARY'
});
```

As `catalog_app`, run:

```cypher
MATCH (p:Product)
RETURN p.sku, p.name, p.internalNote;

MATCH (n:SecureconfigPrivateCanary)
RETURN count(n);

CREATE (:SecureconfigWriteCanary);
```

Compare a disposable exposed account with broad read/write privileges against the fixed account holding only `catalog_reader` and the reviewed `PUBLIC` privileges.

**REASONED outcomes:** the exposed account reads the property canary, counts the unrelated node, and creates the write canary. With section 4 applied, `sku` and `name` remain readable, `internalNote` appears as `null`, the unrelated-node count is zero, and creation fails authorization. Confirm the fixtures and hidden property exist by running the reads as an administrator. Empty reads alone are insufficient. These restrictions can hide data rather than return authorization errors. See [privilege behavior](https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/) and [access-control limitations](https://neo4j.com/docs/operations-manual/current/authentication-authorization/limitations/).

Review `SHOW USER catalog_app PRIVILEGES AS COMMANDS;` as an administrator in both states. Record inherited privileges as well as the custom role.

### Procedure, function, and LOAD denials

**REASONED, Enterprise-only: requires an Enterprise runtime, a compatible installed UDF, and a known readable CSV fixture, unavailable here.** Test each denial independently against the same account before and after applying it:

```cypher
CALL db.labels();

RETURN apoc.text.join(['SECURECONFIG', 'UDF'], '_') AS canary;

LOAD CSV FROM 'file:///secureconfig-canary.csv' AS row
RETURN count(row);

RETURN 1 AS ok;
```

For the UDF comparison, use a compatible APOC installation with `apoc.text.join` loaded and permitted by the plugin allowlist. The function remains documented but is deprecated in Cypher 25. This fixture is for a disposable test; it is not a reason to install APOC in production. See [apoc.text.join](https://neo4j.com/docs/apoc/current/overview/apoc.text/apoc.text.join/).

Before the denials, require a successful procedure call, the UDF result `SECURECONFIG_UDF`, and the CSV's known nonzero row count. Keep file loading enabled throughout the isolated LOAD privilege comparison so a separate file setting cannot masquerade as privilege enforcement.

After each denial, require an authorization failure for the corresponding operation and a successful `RETURN 1 AS ok;`. Missing procedures, missing functions, unreadable files, and plugin allowlist failures do not demonstrate these privileges. See [db.labels](https://neo4j.com/docs/operations-manual/current/procedures/built-in-procedures/), [EXECUTE privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/dbms-administration/dbms-execute-privileges/), [LOAD privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/load-privileges/), and [LOAD CSV](https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/).

Separately, to test the existing local-file setting, use an account whose LOAD privilege permits this fixture. The same CSV must load when `dbms.security.allow_csv_import_from_file_urls=true` and be rejected when it is `false`, while `RETURN 1 AS ok;` succeeds in both states. Do not attribute that rejection to the role denial.

### Transaction budgets

**REASONED, Community and Enterprise: requires a disposable runtime, calibrated workloads, concurrent clients, and resource measurements, unavailable here.** Substitute positive integer workload sizes before submitting these queries interactively.

A candidate memory workload is:

```cypher
UNWIND range(1, REPLACE_WITH_ROW_COUNT) AS i
WITH collect({value: i}) AS rows
RETURN size(rows) AS rowCount;
```

Calibrate it with sufficient heap and larger test limits so it completes, then test each memory limit separately. For the database and server totals, use concurrent transactions and raise the other test limits enough to isolate the limit under examination. In particular, the example per-database limit can fire before the server limit on a single-database deployment.

**REASONED outcome:** a workload that completes with a larger budget is terminated with a memory-limit error when the isolated tracked limit is exceeded. A small query must still succeed. Record workload size, concurrency, heap, effective limits, and the actual error; an out-of-memory crash or timeout is not evidence of the intended memory guard. See [transaction memory limits](https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/).

A candidate CPU workload for the timeout comparison is:

```cypher
UNWIND range(1, REPLACE_WITH_OUTER_COUNT) AS i
UNWIND range(1, REPLACE_WITH_INNER_COUNT) AS j
RETURN sum(i + j) AS total;
```

Calibrate a workload that completes in more than 30 seconds but less than 60 seconds under a larger test timeout. Keep memory limits from being the terminating condition. Compare a client transaction with no custom timeout under the larger server default, then under `db.transaction.timeout=30s`. The latter should terminate for timeout, while `RETURN 1 AS ok;` still succeeds.

Finally, repeat with an explicit 60-second client timeout. Cypher Shell 2025.12 or later supports adding `--transaction-timeout 60s` to the guarded interactive-session command. On current servers, that override should allow the calibrated workload to exceed the 30-second server default and complete. Record actual timings and errors; do not infer a hard server ceiling. See [transaction timeout behavior](https://neo4j.com/docs/operations-manual/current/database-internals/transaction-management/), [Cypher Shell timeout support](https://neo4j.com/docs/operations-manual/current/cypher-shell/), and [older-server exceptions](https://neo4j.com/docs/api/python-driver/current/api.html).

### Security events and query-log contents

**REASONED, Enterprise-only: requires Enterprise log access and a running deployment, unavailable here.** Generate one failed login, one successful login, the privilege changes above, and the denied write. Correlate the account and timestamps with `security.log`. For successful-login retention, compare the event with successful-login logging disabled and enabled while keeping the authentication operation successful in both states.

In the guarded interactive session, set a non-secret parameter using the Cypher Shell command `:param {canary: 'SECURECONFIG_PARAMETER_CANARY'};`, then run:

```cypher
RETURN 'SECURECONFIG_LITERAL_CANARY' AS literal, $canary AS parameter;
```

Compare a disposable logging configuration that records parameter values and unobfuscated literals with section 7's policy. Clear cached queries as an administrator when changing literal obfuscation dynamically.

**REASONED outcome:** both queries return the expected values. Before the policy, the canaries are visible in the query log; afterward, the corresponding query events remain present but literal and parameter values are absent. Missing log events do not demonstrate obfuscation. See [query and security logging](https://neo4j.com/docs/operations-manual/current/monitoring/logging/) and [Cypher Shell parameters](https://neo4j.com/docs/operations-manual/current/cypher-shell/).

On versions supporting error obfuscation, test it separately with:

```cypher
RETURN date('SECURECONFIG_ERROR_CANARY');
```

This deliberately invalid date should produce a query error. Establish whether the error canary appears in the unprotected log, then enable error obfuscation and require the failure event to remain without that value. If the baseline does not expose the canary, the comparison is inconclusive. See [date parsing](https://neo4j.com/docs/cypher-manual/current/functions/temporal/) and [error obfuscation](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/).

**REASONED, Community HTTP logging: requires a running HTTPS connector and log access, unavailable here.** Compare the authenticated request below with HTTP request logging disabled and enabled. The query must succeed in both states, with the corresponding request recorded when logging is enabled. This tests request logging only; it does not demonstrate Bolt or security auditing.

### HTTPS authentication

**REASONED: requires HTTPS, trusted certificates, a protected credential file, and the Query API, unavailable here.** The transactional HTTP API endpoint `/db/neo4j/tx/commit` was deprecated in 5.26; deprecation does not mean every deployment has removed it. Prefer the Query API when enabled. It arrived in 5.19 and became enabled by default on self-managed installations in 5.25. See the [HTTP API deprecation](https://neo4j.com/docs/http-api/current/) and [Query API availability](https://neo4j.com/docs/query-api/current/).

Provision `neo4j-auth.header` through your secret-management mechanism as an owner-readable-only file containing the complete Authorization header for a valid database account. Do not construct it with a secret-bearing command-line argument. `ca.pem` contains the signing CA. For an interactive authenticated positive control, replacing `--header @neo4j-auth.header` with `--user neo4j` prompts for the password; remove the header-file check for that variant. Never append a password to the username. For publicly trusted certificates, the explicit CA option and file check may be omitted only when curl's default trust store suffices. Skip the HTTPS pairs when HTTPS is deliberately unavailable.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "expected exactly one hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the hostname inside the quotes; not probing"
      exit 1
      ;;
    *)
      [ -r ca.pem ] || { echo "provide the signing CA in ca.pem"; exit 1; }
      [ -r neo4j-auth.header ] || { echo "provide the protected header file"; exit 1; }
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert ca.pem -H 'Content-Type: application/json' \
        --data '{"statement":"RETURN 1 AS ok"}' \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:7473/db/neo4j/query/v2"
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert ca.pem --header @neo4j-auth.header \
        -H 'Content-Type: application/json' \
        --data '{"statement":"RETURN 1 AS ok"}' \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:7473/db/neo4j/query/v2"
      ;;
  esac
)
```

**REASONED outcomes:** an exposed authentication-disabled test service returns the query result anonymously. With authentication enabled, the first request returns 401; the authenticated request must contain the expected `ok=1` result. A Query API 202 response alone does not prove query success: inspect the body for errors and the expected data. A 404 or connection/TLS failure does not prove authentication enforcement. See [authorization responses](https://neo4j.com/docs/query-api/current/authentication-authorization/) and [query response semantics](https://neo4j.com/docs/query-api/current/query/).

For deployments exposing the legacy transactional HTTP API, including Neo4j 5 versions predating the Query API, run this pair as well. When both APIs are enabled, test both. Its JSON uses `statements`, unlike the Query API's singular `statement`. See the [legacy query endpoint](https://neo4j.com/docs/http-api/current/query/) and [legacy authentication](https://neo4j.com/docs/http-api/current/authentication-authorization/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "expected exactly one hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the hostname inside the quotes; not probing"
      exit 1
      ;;
    *)
      [ -r ca.pem ] || { echo "provide the signing CA in ca.pem"; exit 1; }
      [ -r neo4j-auth.header ] || { echo "provide the protected header file"; exit 1; }
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert ca.pem -H 'Content-Type: application/json' \
        --data '{"statements":[{"statement":"RETURN 1 AS ok"}]}' \
        -w '\nlegacy-no-auth=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:7473/db/neo4j/tx/commit"
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert ca.pem --header @neo4j-auth.header \
        -H 'Content-Type: application/json' \
        --data '{"statements":[{"statement":"RETURN 1 AS ok"}]}' \
        -w '\nlegacy-auth=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:7473/db/neo4j/tx/commit"
      ;;
  esac
)
```

**REASONED: requires a deployment with the legacy HTTP API, trusted certificates, and protected credentials, unavailable here.** With authentication disabled in a disposable baseline, the anonymous request returns the query result. With authentication enabled, it must return 401; the authenticated request must return `ok=1` with an empty `errors` array. HTTP 200 alone does not demonstrate query success. A missing endpoint, TLS error, connection failure, or an authentication failure without a working positive control is inconclusive. See [legacy authorization responses](https://neo4j.com/docs/http-api/current/authentication-authorization/) and [legacy query results](https://neo4j.com/docs/http-api/current/query/).

### Verification backlog

The single row below records the outstanding service demonstration debt for this guide. It is not a claim that `TODO.md` was edited.

| ID | Status and completion evidence |
|---|---|
| NEO4J-LIVE-1 | REASONED, not demonstrated. Reproduce all Verify comparisons in disposable Community and Enterprise deployments: prompted bootstrap and process arguments; listeners, TLS, plaintext refusal, and default-password rotation; Enterprise standalone and cluster binds, Docker inheritance, discovery v1/v2, opt-in Prometheus, and cluster TLS rejection of untrusted peers with healthy authorized discovery, replication, and routing; scoped graph reads and denied writes; effective privileges; procedure/UDF/LOAD denials and the separate existing local-file setting; each memory budget and default/client timeout; security events, query literal/parameter/error obfuscation, Community HTTP request logging, and the Query API and legacy transactional HTTP API anonymous/authenticated pairs; mutual TLS where configured. Requires server and client runtimes, an Enterprise cluster as well as a standalone server, fixtures, compatible APOC, trusted certificates, protected credentials, concurrent workloads, log/process access, and an external network vantage. Record versions, exposed/fixed outcomes, matched positive controls, and errors before replacing any REASONED label. |

## Common mistakes

- `server.default_listen_address=0.0.0.0` set during installation "to test", with `neo4j`/`neo4j` still in place.
- Bolt TLS configured but left at `server.bolt.tls_level=OPTIONAL`, so `neo4j://` clients keep connecting in plaintext.
- HTTPS enabled while `server.http.enabled` stays `true`, leaving 7474 open beside 7473.
- Treating a separate Community username as a restricted account, or Enterprise's built-in `reader` as a database-specific role.
- Adding a narrow role without removing broader privileges inherited by the same account.
- Assuming read-only graph access also blocks procedures, UDFs, or data loading.
- Treating a default transaction timeout as an unoverrideable ceiling.
- Treating missing logs, empty query results, or connection failures as successful security checks.

## Sources (checked September 2026)

- Configure network connectors: https://neo4j.com/docs/operations-manual/current/configuration/connectors/
- Ports: https://neo4j.com/docs/operations-manual/current/configuration/ports/
- Set an initial password: https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/
- Exact configuration settings, defaults, editions, and error-obfuscation version: https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/
- Neo4j 5.26 (LTS), fetched 2026-09-26, Enterprise cluster and monitoring ports: https://neo4j.com/docs/operations-manual/5/configuration/ports/#_cluster
- Neo4j 5.26 (LTS) cluster deployment and discovery-version conditions: https://neo4j.com/docs/operations-manual/5/clustering/setup/deploy/#cluster-example-configure-a-three-primary-cluster
- Neo4j 5.26 (LTS) cluster settings and advertised addresses: https://neo4j.com/docs/operations-manual/5/clustering/settings/
- OpenSSL 3 TLS probe options: https://docs.openssl.org/3.0/man1/openssl-s_client/
- TLS 1.3 client-certificate validation and alerts: https://www.rfc-editor.org/rfc/rfc8446.html
- Probe time limit and exit status: https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html
- Neo4j 5.26 (LTS) cluster SSL policy, certificates, and mutual authentication: https://neo4j.com/docs/operations-manual/5/security/ssl-framework/#ssl-cluster-config
- Pinned Dockerfile EXPOSE declarations, Debian: https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/Dockerfile-debian#L53
- Pinned Dockerfile EXPOSE declarations, UBI 8: https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/Dockerfile-ubi8#L90
- Pinned Dockerfile EXPOSE declarations, UBI 9: https://github.com/neo4j/docker-neo4j/blob/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/Dockerfile-ubi9#L89
- Neo4j 5.26 (LTS) configuration reference, listener defaults, and error obfuscation since 5.26.21: https://neo4j.com/docs/operations-manual/5/configuration/configuration-settings/
- Configuration changes in Neo4j 5: https://neo4j.com/docs/upgrade-migration-guide/current/version-5/changelogs/configuration-settings/
- SSL framework and certificate-verified connection schemes: https://neo4j.com/docs/operations-manual/current/security/ssl-framework/
- Authentication and native lockout configuration: https://neo4j.com/docs/operations-manual/current/authentication-authorization/
- Manage users and Community's implied administrator privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-users/
- Manage roles: https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-roles/
- Built-in roles and PUBLIC privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/built-in-roles/
- Database access privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/database-administration/
- MATCH and property-read privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/privileges-reads/
- GRANT, DENY, and showing user privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-privileges/
- Access-control limitations and hidden properties: https://neo4j.com/docs/operations-manual/current/authentication-authorization/limitations/
- Procedure and user-defined function execution privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/dbms-administration/dbms-execute-privileges/
- LOAD privileges: https://neo4j.com/docs/operations-manual/current/authentication-authorization/load-privileges/
- LOAD privilege introduction versions: https://neo4j.com/docs/cypher-manual/5/deprecations-additions-removals-compatibility/
- Cypher Shell prompts, environment credentials, history, parameters, and timeouts: https://neo4j.com/docs/operations-manual/current/cypher-shell/
- Docker introduction and initial authentication: https://neo4j.com/docs/operations-manual/current/docker/introduction/
- Docker configuration and container listen addresses: https://neo4j.com/docs/operations-manual/current/docker/configuration/
- Official Neo4j 5 Docker entrypoint and default listen address: https://raw.githubusercontent.com/neo4j/docker-neo4j/5359427c4f51d0d51cce5b048757a2c21e6f377e/docker-image-src/5/coredb/docker-entrypoint.sh
- Single sign-on integration: https://neo4j.com/docs/operations-manual/current/authentication-authorization/sso-integration/
- LDAP integration: https://neo4j.com/docs/operations-manual/current/authentication-authorization/ldap-integration/
- Securing extensions and plugin loading: https://neo4j.com/docs/operations-manual/current/security/securing-extensions/
- APOC configuration and exact import-setting spelling: https://neo4j.com/docs/apoc/current/config/
- Protecting against SSRF, redirected from the original developer KB URL: https://support.neo4j.com/s/article/8584271681427-Protecting-against-Server-Side-Request-Forgery-SSRF
- APOC Extended JDBC outbound loading: https://neo4j.com/labs/apoc/5/overview/apoc.load/apoc.load.jdbc/
- APOC security, boosted execution, and SSRF: https://neo4j.com/docs/apoc/current/security-guidelines/
- Transaction memory limits and accounting: https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/
- Transaction timeout behavior: https://neo4j.com/docs/operations-manual/current/database-internals/transaction-management/
- Driver transaction timeout overrides and older-server exceptions: https://neo4j.com/docs/api/python-driver/current/api.html
- Logging, edition availability, security events, and rotation: https://neo4j.com/docs/operations-manual/current/monitoring/logging/
- Enterprise online backup: https://neo4j.com/docs/operations-manual/current/backup-restore/online-backup/
- Transactional HTTP API deprecation: https://neo4j.com/docs/http-api/current/
- Legacy transactional HTTP API query payload and results: https://neo4j.com/docs/http-api/current/query/
- Legacy transactional HTTP API authentication: https://neo4j.com/docs/http-api/current/authentication-authorization/
- Query API availability: https://neo4j.com/docs/query-api/current/
- Query API authentication and authorization: https://neo4j.com/docs/query-api/current/authentication-authorization/
- Query API endpoint and response semantics: https://neo4j.com/docs/query-api/current/query/
- Built-in procedures, including db.labels and db.clearQueryCaches: https://neo4j.com/docs/operations-manual/current/procedures/built-in-procedures/
- APOC UDF test and Cypher 25 deprecation: https://neo4j.com/docs/apoc/current/overview/apoc.text/apoc.text.join/
- CREATE fixture syntax: https://neo4j.com/docs/cypher-manual/current/clauses/create/
- LOAD CSV syntax: https://neo4j.com/docs/cypher-manual/current/clauses/load-csv/
- UNWIND workload syntax: https://neo4j.com/docs/cypher-manual/current/clauses/unwind/
- Aggregating functions for fixture counts and workloads: https://neo4j.com/docs/cypher-manual/current/functions/aggregating/
- List functions, including range: https://neo4j.com/docs/cypher-manual/current/functions/list/
- Scalar functions, including size: https://neo4j.com/docs/cypher-manual/current/functions/scalar/
- Temporal date parsing for the error canary: https://neo4j.com/docs/cypher-manual/current/functions/temporal/
