# Neo4j: listen address, initial password, and TLS on Bolt and HTTPS

A packaged Neo4j 5 listens on `localhost` only by default and ships with authentication on, but with the well-known `neo4j`/`neo4j` credential, Bolt TLS at `DISABLED`, and plaintext HTTP enabled instead of HTTPS. Setting `server.default_listen_address=0.0.0.0` on such an install to "make it reachable" therefore exposes a database with a guessable password over plaintext. These defaults remain documented at the time of writing. The official Docker instructions publish container ports for access from the host; do not assume the packaged loopback boundary protects a published container port. Docker's `NEO4J_AUTH=neo4j/REPLACE_WITH_LONG_RANDOM_VALUE` initializes authentication for a NEW database; it does not rotate an existing database's password. Supply credentials through the execution environment or secret-management mechanism, never as literal command-line arguments, and never use `NEO4J_AUTH=none`. See [network connectors](https://neo4j.com/docs/operations-manual/current/configuration/connectors/) and [Docker authentication](https://neo4j.com/docs/operations-manual/current/docker/introduction/).

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

The documented `neo4j-admin dbms set-initial-password` interface takes a positional password. Secret-store substitution and disabling shell history do not remove that password from process arguments; there is no documented stdin or password-file option to substitute here. Cypher Shell provides the prompted alternative. For automation, it also documents `NEO4J_PASSWORD`: supply it through the execution environment, never expand it into `-p`. Environment delivery does not protect against every form of local process inspection. See [initial-password configuration](https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/) and [Cypher Shell](https://neo4j.com/docs/operations-manual/current/cypher-shell/).

At the time of writing, the default minimum password length is 8 characters. `dbms.security.auth_minimum_password_length` was introduced in 5.3; a minimum is not a recommendation to use an eight-character password. Leave `dbms.security.auth_enabled` at its default `true`. The authentication documentation reserves disabling it for recovery with network access blocked. See [configuration changes in Neo4j 5](https://neo4j.com/docs/upgrade-migration-guide/current/version-5/changelogs/configuration-settings/) and [authentication configuration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/).

## 2. Bind deliberately

`server.default_listen_address` supplies the host when a connector's listen address omits it. At the time of writing, `server.bolt.listen_address` defaults to `:7687`, `server.http.listen_address` to `:7474`, and `server.https.listen_address` to `:7473`. Keep the default `localhost` unless remote clients are deliberate, then prefer a specific private address over `0.0.0.0`. Changing the shared address can also expose cluster ports; Neo4j recommends explicitly binding cluster listeners to `localhost` when clustering is not in use. See [network connector configuration](https://neo4j.com/docs/operations-manual/current/configuration/connectors/).

Online backup is Enterprise-only. Its `server.backup.listen_address` defaults to `127.0.0.1:6362` at the time of writing; keep it off external interfaces. Community readers should not expect an online-backup listener. See [online backup](https://neo4j.com/docs/operations-manual/current/backup-restore/online-backup/) and the [configuration reference](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/).

Firewall per [cloud-firewalls.md](cloud-firewalls.md) or [host.md), and widen access only after TLS and authentication are configured.

```ini
server.default_listen_address=REPLACE_WITH_PRIVATE_IP
```

## 3. TLS on Bolt and HTTPS, HTTP off

Put a PKCS#8 PEM private key and certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)) under each policy directory. Use the service account as owner, normally `neo4j:neo4j`, with key mode `0400` and certificate mode `0644`. Convert legacy PKCS#1 private keys to the documented PKCS#8 format.

`server.bolt.tls_level=REQUIRED` refuses unencrypted Bolt; `OPTIONAL` continues accepting it. `server.http.enabled=false` removes the plaintext HTTP endpoint. This baseline uses server authentication through TLS and database credentials for clients. See the [SSL framework](https://neo4j.com/docs/operations-manual/current/security/ssl-framework/).

```ini
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

**Enterprise-only: restrict the application's database, labels, and properties.** An application credential should expose only the data it needs. Enterprise's built-in `reader` role grants broad graph reads and access across databases; it is not a database-specific application role. Create a custom role for narrower access and keep administrator credentials out of application configuration. The example permits reading two properties on `Product` nodes in the existing `neo4j` database. See [built-in roles](https://neo4j.com/docs/operations-manual/current/authentication-authorization/built-in-roles/), [database access privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/database-administration/), and [MATCH privileges](https://neo4j.com/docs/operations-manual/current/authentication-authorization/privileges-reads/).

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

MFA: native password authentication has no second-factor step. Enterprise can delegate authentication to an OIDC provider whose policy enforces MFA ([oidc-integration.md](oidc-integration.md)). Enterprise's LDAP `simple` authentication uses a username and password; that alone is not MFA. Confirm second-factor enforcement and ensure alternate native or password paths cannot bypass it ([mfa.md](mfa.md)). Put human access to the host and application behind MFA. See [SSO integration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/sso-integration/) and [LDAP integration](https://neo4j.com/docs/operations-manual/current/authentication-authorization/ldap-integration/).

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

- Keep `dbms.security.procedures.unrestricted` empty unless a reviewed extension specifically requires access to internal APIs. Narrow `dbms.security.procedures.allowlist` to the procedures and functions the workload needs; its default is `*` at the time of writing. This controls which extensions load, rather than providing Community with per-user execution privileges. Install only necessary plugins. See [securing extensions](https://neo4j.com/docs/operations-manual/current/security/securing-extensions/).
- If APOC is installed, put its settings in `apoc.conf`, not `neo4j.conf`, for Neo4j 5 and later. Retain `apoc.import.file.enabled=false` unless local file import is required, and keep `apoc.import.file.use_neo4j_config=true`. These are the defaults in the [APOC configuration reference](https://neo4j.com/docs/apoc/current/config/).
- Set `dbms.security.allow_csv_import_from_file_urls=false` when local `LOAD CSV` is unnecessary. The current [Neo4j configuration reference](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/) directly documents its default as `true`. The APOC security overview disagrees on that default and uses an inconsistent APOC setting spelling; use the configuration references for these values and the dotted `apoc.import.file.use_neo4j_config` spelling.
- `LOAD CSV` and URL-loading extensions such as `apoc.load.json` can make outbound requests. Restrict egress so queries cannot reach internal services or cloud metadata at `169.254.169.254` ([egress-metadata.md](egress-metadata.md)). The current [APOC security guidance](https://neo4j.com/docs/apoc/current/security-guidelines/) also documents `internal.dbms.cypher_ip_blocklist` for Community SSRF mitigation. Check compatibility with the installed version and retain network egress restrictions.

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

The configuration reference marks this setting as introduced in **2026.01.3**. Do not add it to Neo4j 5 or another version that lacks it. Literal obfuscation alone does not sanitize error details. See the [error-obfuscation setting](https://neo4j.com/docs/operations-manual/current/configuration/configuration-settings/).

Obfuscation does not hide every identifier or query detail. Treat the logs as sensitive.

Community provides operational logs and optional HTTP request logging:

```ini
dbms.logs.http.enabled=true
```

Enable HTTP request logging only when an HTTP/HTTPS connector is in use. It does not provide equivalent Bolt, query, or security auditing; collect application and fronting-layer events as well. See [available log files](https://neo4j.com/docs/operations-manual/current/monitoring/logging/).

## Verify

**Service verification status: REASONED, not demonstrated.** The authoring environment has no Neo4j server, Cypher Shell, Docker, or Podman available, and no authorized running deployment was supplied. All service comparisons below require capabilities missing here. Run exposed/fixed comparisons only in disposable test deployments. Record server, edition, client, and plugin versions alongside results.

Local validation was run: the five shell blocks passed `bash -n` and ShellCheck 0.11.0, and the repository's guard scanner reported no findings. Guard-only tests rejected eight placeholder cases and three malformed marker/count cases, and accepted one substituted hostname. All four guarded blocks rejected their original placeholders before reaching probes. Six configuration fragments passed basic key/value parsing and duplicate-key checks. These are local syntax checks, not Neo4j configuration validation or service verification.

For each guarded block, replace the hostname inside the single quotes and paste the whole block. The blocks assume ordinary shell builtins; do not insert a literal apostrophe into the quoted substitution. A fragment pasted below the guards is unguarded.

Use `neo4j+s://` for certificate-verified routing connections or `bolt+s://` for a certificate-verified direct connection. The `+ssc` variants skip certificate verification and do not establish server identity. The checks below use direct Bolt to avoid routing discovery obscuring the result. Install the signing CA in the Cypher Shell client's trust store when necessary; OpenSSL's `-CAfile` and curl's `--cacert` do not configure Cypher Shell's trust. See [TLS connection schemes](https://neo4j.com/docs/operations-manual/current/security/ssl-framework/).

### Listener inventory

**REASONED: requires the Neo4j service's network namespace, unavailable here.** Run this block inside that namespace. The substituted hostname identifies the deployment being inspected; it does not make `ss` inspect a remote machine.

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

### Transport, default password, and prompted bootstrap

**REASONED: requires an isolated fresh installation, a reachable TLS deployment, client tools, and an external test vantage, unavailable here.** Supply the signing CA as `ca.pem`. Run against the actual deployment hostname, including each relevant public IPv4/IPv6 path from another host.

The first password prompt below is deliberately for the public default password only. Never enter a real password into the plaintext test.

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
- With the original HTTP endpoint exposed, the 7474 request returns an HTTP status. With the fixed policy, that endpoint must not answer. A timeout, DNS failure, or local routing failure is inconclusive. A connection refusal is useful only after confirming the intended host and path, alongside the working TLS service and listener inventory.
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

Provision `neo4j-auth.header` through your secret-management mechanism as an owner-readable-only file containing the complete Authorization header for a valid database account. Do not construct it with a secret-bearing command-line argument. `ca.pem` contains the signing CA. Skip this pair when HTTPS is deliberately unavailable.

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

### Verification backlog

The single row below records the outstanding service demonstration debt for this guide. It is not a claim that `TODO.md` was edited.

| ID | Status and completion evidence |
|---|---|
| NEO4J-LIVE-1 | REASONED, not demonstrated. Reproduce all Verify comparisons in disposable Community and Enterprise deployments: prompted bootstrap and process arguments; listeners, TLS, plaintext refusal, and default-password rotation; scoped graph reads and denied writes; effective privileges; procedure/UDF/LOAD denials and the separate existing local-file setting; each memory budget and default/client timeout; security events, query literal/parameter/error obfuscation, Community HTTP request logging, and the Query API anonymous/authenticated pair. Requires server and client runtimes, Enterprise capability, fixtures, compatible APOC, trusted certificates, protected credentials, concurrent workloads, log/process access, and an external network vantage. Record versions, exposed/fixed outcomes, matched positive controls, and errors before replacing any REASONED label. |

## Common mistakes

- `server.default_listen_address=0.0.0.0` set during installation "to test", with `neo4j`/`neo4j` still in place.
- Bolt TLS configured but left at `server.bolt.tls_level=OPTIONAL`, so plaintext clients keep connecting.
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
- Single sign-on integration: https://neo4j.com/docs/operations-manual/current/authentication-authorization/sso-integration/
- LDAP integration: https://neo4j.com/docs/operations-manual/current/authentication-authorization/ldap-integration/
- Securing extensions and plugin loading: https://neo4j.com/docs/operations-manual/current/security/securing-extensions/
- APOC configuration and exact import-setting spelling: https://neo4j.com/docs/apoc/current/config/
- APOC security, boosted execution, and SSRF: https://neo4j.com/docs/apoc/current/security-guidelines/
- Transaction memory limits and accounting: https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/
- Transaction timeout behavior: https://neo4j.com/docs/operations-manual/current/database-internals/transaction-management/
- Driver transaction timeout overrides and older-server exceptions: https://neo4j.com/docs/api/python-driver/current/api.html
- Logging, edition availability, security events, and rotation: https://neo4j.com/docs/operations-manual/current/monitoring/logging/
- Enterprise online backup: https://neo4j.com/docs/operations-manual/current/backup-restore/online-backup/
- Transactional HTTP API deprecation: https://neo4j.com/docs/http-api/current/
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
