# MySQL and MariaDB: TLS and authentication

Default posture: keep the server on `127.0.0.1` and open it to remote clients only deliberately, with TLS required. Oracle documents MySQL's `bind_address` default as `*`; do not assume a package has already restricted it. [MySQL server variables](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_bind_address).

## 1. Server TLS

MySQL can generate missing certificate/key files at startup under its documented auto-generation conditions. Inspect the effective settings:

```sql
SHOW GLOBAL VARIABLES LIKE '%ssl%';
```

The auto-generated server certificate does not carry your deployment hostname, so the identity-verifying client below (`--ssl-mode=VERIFY_IDENTITY`) rejects it. Install a certificate covering the hostname clients connect to, such as `db.example.com`. [MySQL certificate generation](https://dev.mysql.com/doc/refman/8.4/en/creating-ssl-rsa-files-using-mysql.html).

To use your own certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)) and refuse cleartext TCP connections, set these options in `/etc/mysql/mysql.conf.d/mysqld.cnf`, or the equivalent for your packaging:

```ini
[mysqld]
bind_address = 127.0.0.1
mysqlx_bind_address = 127.0.0.1
require_secure_transport = ON
tls_version = TLSv1.2,TLSv1.3
ssl_ca = /etc/mysql/certs/ca.pem
ssl_cert = /etc/mysql/certs/server-cert.pem
ssl_key = /etc/mysql/certs/server-key.pem
```

Widen the bind addresses only deliberately. Omit `mysqlx_bind_address` on MariaDB. The TLS version list requires a compatible TLS library; MySQL supports TLSv1.3 from 8.0.16 with OpenSSL 1.1.1 or later. MariaDB's TLSv1.3 support also depends on its TLS library. Restart after applying this startup configuration. [MySQL secure connections](https://dev.mysql.com/doc/mysql-secure-deployment-guide/8.0/en/secure-deployment-secure-connections.html), [MariaDB TLS variables](https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/ssltls-system-variables).

Global `require_secure_transport` permits Unix sockets, but MySQL account-level `REQUIRE SSL` takes precedence and prevents that account from connecting through a Unix socket. [MySQL transport requirements](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_require_secure_transport).

MariaDB introduced `require_secure_transport` in 10.5.2. MariaDB 11.4 changed automatic TLS setup and client verification; its zero-configuration behavior requires compatible server and client versions and authentication plugins. Do not assume older clients receive the same protection. Explicit CA-based configuration remains useful across mixed deployments. [MariaDB transport requirements](https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#require_secure_transport), [MariaDB automatic TLS](https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/zero-configuration-ssl).

MySQL 8.0, 8.4, 9.7 and 26.7 enable the X Plugin by default. It has a separate listener: `mysqlx_port` defaults to `33060`, and `mysqlx_bind_address` defaults to `*`, every interface. The classic protocol's `bind_address` does not restrict it. Set both bind addresses, as above, or disable an unused X Plugin with `mysqlx = OFF`. These X Plugin options require a restart. [MySQL 8.0 X Plugin options](https://dev.mysql.com/doc/refman/8.0/en/x-plugin-options-system-variables.html), [MySQL 8.4 X Plugin options](https://dev.mysql.com/doc/refman/8.4/en/x-plugin-options-system-variables.html), [MySQL 9.7 X Plugin options](https://dev.mysql.com/doc/refman/9.7/en/x-plugin-options-system-variables.html), [MySQL 26.7 X Plugin options](https://dev.mysql.com/doc/refman/26.7/en/x-plugin-options-system-variables.html).

MariaDB does not implement MySQL's X Protocol. Omit MySQL-specific X Plugin options: an unknown option can prevent MariaDB from starting. [MariaDB protocol differences](https://mariadb.com/docs/server/reference/clientserver-protocol/mariadb-protocol-differences-with-mysql), [MariaDB startup troubleshooting](https://mariadb.com/docs/server/server-management/starting-and-stopping-mariadb/what-to-do-if-mariadb-doesnt-start).

The official Docker images start wider. The MySQL images (8.4, 9.7 and innovation at the pinned commit) install Oracle's Docker server package, whose `my.cnf` (checked in the 8.4.9, 9.7.2 and 26.7.0 sources) sets no bind address, so `bind_address` and `mysqlx_bind_address` keep their `*` defaults (in 8.4, 9.7 and 26.7 alike) and the classic and X Protocol ports (3306 and 33060 by default) listen on every address, unless an argument or an option file (such as one mounted in `/etc/mysql/conf.d/`) changes that: a bind address, `skip_networking`, or `mysqlx=OFF` for the X Protocol port. The MariaDB images (10.6 through 13.1) comment out every `bind-address` line in the Ubuntu variants' configuration, including the package's `127.0.0.1`, and the UBI variants' packaged configuration leaves it commented, so unless an argument or an option file sets a bind address or `skip_networking`, the server listens on the IPv4 wildcard address, and on the IPv6 one where the container has IPv6. When either entrypoint initializes a new data directory, the root host (`MYSQL_ROOT_HOST`; on MariaDB, `MARIADB_ROOT_HOST` or `MYSQL_ROOT_HOST`; `_FILE` forms accepted) is `%` when neither the variable nor its `_FILE` form supplies a value (a `_FILE` naming an empty file leaves it empty, and then no remote root account is created), and for any non-empty value other than `localhost` the entrypoint creates a root account for that host (`root@'%'` by default) with `GRANT ALL ON *.* ... WITH GRANT OPTION` (MariaDB also grants `PROXY`) and the root password. Initialization requires a root password (on MariaDB, or its hash), a random one, or the empty-password variable (`MYSQL_ALLOW_EMPTY_PASSWORD`; MariaDB also accepts `MARIADB_ALLOW_EMPTY_ROOT_PASSWORD`). With none of the others set, any non-empty value of that variable, even `no`, lets initialization proceed, and the remote root account is created with an empty password. Set a root password or a random one, set the root host to `localhost` unless remote root is needed, never set the empty-password variable, and publish the ports only to host loopback or a private network.

## 2. Per-account requirements

Require TLS, or a client certificate, at the account level as a second control. For existing accounts:

```sql
ALTER USER 'app'@'10.0.0.10' REQUIRE SSL;
-- Alternatively, for an existing batch account using mutual TLS:
ALTER USER 'batch'@'10.0.0.11' REQUIRE X509;
```

Use the source address the database actually sees. MySQL deprecates `%` and `_` wildcards in account host values; prefer explicit addresses and use a deliberate network range only when required. [MySQL account names](https://dev.mysql.com/doc/refman/8.4/en/account-names.html), [MySQL account requirements](https://dev.mysql.com/doc/refman/8.4/en/alter-user.html).

### Create a scoped runtime account

A compromised application should reach only the tables and operations it needs. Create a separate runtime account for the application's source host; keep migrations and account administration in separate accounts.

The SQL below is an administrative template. Replace secret placeholders with generated secrets satisfying the configured policy, and enter password-bearing SQL through an authenticated client's input. Never put it in a shell command or a client `-e` argument. Client login passwords use the interactive `-p` prompt with no value.

MySQL 8.0/8.4:

```sql
CREATE USER 'app'@'10.0.0.10'
  IDENTIFIED WITH caching_sha2_password BY 'REPLACE_WITH_RANDOM_SECRET'
  REQUIRE SSL;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON app.orders TO 'app'@'10.0.0.10';
```

Remove operations the application does not need. Repeat grants for individual required tables. Do not substitute `*.*`, `ALL PRIVILEGES`, or `WITH GRANT OPTION`. Creating this account does not remove an existing `'app'@'%'` account or its privileges; review and retire the old account after cutover. [MySQL CREATE USER](https://dev.mysql.com/doc/refman/8.4/en/create-user.html), [MySQL GRANT](https://dev.mysql.com/doc/refman/8.4/en/grant.html).

For MariaDB 10.4+ deployments whose clients support `ed25519`, install the authentication plugin once if absent, then create the account:

```sql
INSTALL SONAME 'auth_ed25519';

CREATE USER 'app'@'10.0.0.10'
  IDENTIFIED VIA ed25519 USING PASSWORD('REPLACE_WITH_RANDOM_SECRET')
  REQUIRE SSL;

GRANT SELECT, INSERT, UPDATE, DELETE
  ON app.orders TO 'app'@'10.0.0.10';
```

Check connector compatibility before migration. MariaDB added the `PASSWORD()` form for `ed25519` in 10.4. Its ordinary `IDENTIFIED BY` behavior is not MySQL's `caching_sha2_password` default. [MariaDB ed25519](https://mariadb.com/docs/server/reference/plugins/authentication-plugins/authentication-plugin-ed25519), [MariaDB CREATE USER](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/create-user), [MariaDB GRANT](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/grant).

### Remove anonymous access and installation leftovers

Anonymous accounts and leftover test-schema grants can provide access outside the application's intended account boundary. On a new installation, use the vendor's interactive hardening utility.

MySQL:

```bash
mysql_secure_installation
```

MariaDB:

```bash
mariadb-secure-installation
```

Select removal of anonymous users, unused remote root accounts, and the disposable `test` database and associated access grants. On an existing deployment, first confirm that the database is disposable and preserve a working administrative access path. The utilities prompt for credentials and choices; do not add a password argument. [MySQL hardening utility](https://dev.mysql.com/doc/refman/8.4/en/mysql-secure-installation.html), [MariaDB hardening utility](https://mariadb.com/docs/server/clients-and-utilities/deployment-tools/mariadb-secure-installation).

Inventory before and after, through an administrative session:

```sql
SELECT User, Host
FROM mysql.user
WHERE User = '' OR User = 'root';

SELECT User, Host, Db
FROM mysql.db
WHERE User = '' OR Db LIKE 'test%';
```

Inspect the rows individually. The second query intentionally includes similarly named application databases; it is an inventory, not a deletion list. Removing `test` alone does not establish that grants permitting future `test_...` databases have disappeared. Do not edit grant tables directly. [MySQL grant tables](https://dev.mysql.com/doc/refman/8.4/en/grant-tables.html), [MySQL cleanup behavior](https://dev.mysql.com/doc/refman/8.4/en/mysql-secure-installation.html).

Initial accounts depend on installation method. MariaDB 10.4+ normally supports local root administration through Unix-socket authentication; do not replace it with password authentication merely to follow an older checklist. In MariaDB 10.4+, `mysql.user` is a compatibility view, suitable for this inventory. [MariaDB installation guidance](https://mariadb.com/docs/server/clients-and-utilities/deployment-tools/mariadb-secure-installation), [MariaDB user view](https://mariadb.com/docs/server/reference/system-tables/the-mysql-database-tables/mysql-user-table).

### Roles and inherited privileges

Where several accounts share privileges, use a role instead of the direct table grant.

MySQL 8.0/8.4:

```sql
CREATE ROLE app_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.orders TO app_runtime;
GRANT app_runtime TO 'app'@'10.0.0.10';
SET DEFAULT ROLE app_runtime TO 'app'@'10.0.0.10';
```

MariaDB:

```sql
CREATE ROLE app_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.orders TO app_runtime;
GRANT app_runtime TO 'app'@'10.0.0.10';
SET DEFAULT ROLE app_runtime FOR 'app'@'10.0.0.10';
```

Assignment and activation are separate. MariaDB uses `FOR` and permits one current role, including inherited privileges; MySQL supports multiple active roles. Do not give the application role administration rights. [MySQL roles](https://dev.mysql.com/doc/refman/8.4/en/roles.html), [MariaDB default roles](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/set-default-role), [MariaDB role activation](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/set-role).

Withhold `FILE`, `SUPER`, account-management privileges, and unnecessary global privileges. On MySQL, withhold administrative dynamic privileges such as `SYSTEM_VARIABLES_ADMIN` and `ROLE_ADMIN`; on 8.4, this also includes `SET_ANY_DEFINER` and `ALLOW_NONEXISTENT_DEFINER`. The older `SET_USER_ID` privilege was removed in MySQL 8.4. MariaDB's corresponding definer privilege is `SET USER`, available from 10.5. [MySQL privileges](https://dev.mysql.com/doc/refman/8.4/en/privileges-provided.html), [MySQL 8.4 changes](https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html), [MariaDB privileges](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/grant#set-user).

On MariaDB 10.11+, also inspect privileges inherited by every account through `PUBLIC`:

```sql
SHOW GRANTS FOR PUBLIC;
```

Revoke an unintended grant at the scope where it was granted. For example, if this specific table grant exists:

```sql
REVOKE SELECT ON app.orders FROM PUBLIC;
```

This affects all users. First preserve intentional access with explicit grants. A table-level revoke does not remove a broader database-level grant. [MariaDB PUBLIC privileges](https://mariadb.com/docs/server/security/user-account-management/roles/system-users-roles-and-privileges), [MariaDB GRANT and version availability](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/grant).

### Authentication versions

Account hygiene also follows [authentication.md](authentication.md). MySQL 8.0 and 8.4 default to `caching_sha2_password` for new accounts, but existing accounts retain their configured authentication plugin. `mysql_native_password` was deprecated in 8.0.34, disabled by default in 8.4, and removed in 9.0. [MySQL 8.0 authentication](https://dev.mysql.com/doc/refman/8.0/en/caching-sha2-pluggable-authentication.html), [MySQL 8.4 authentication](https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html), [native authentication lifecycle](https://dev.mysql.com/doc/refman/8.4/en/native-pluggable-authentication.html).

For an existing MySQL account, coordinate the password and client cutover:

```sql
ALTER USER 'app'@'10.0.0.10'
  IDENTIFIED WITH caching_sha2_password BY 'REPLACE_WITH_NEW_RANDOM_SECRET';
```

Use an administrative session for this migration. [MySQL ALTER USER](https://dev.mysql.com/doc/refman/8.4/en/alter-user.html).

MariaDB now documents a server-side `caching_sha2_password` plugin in Community Server 12.1 and Enterprise Server 11.8. This does not make MySQL authentication syntax, defaults, or older MariaDB deployments interchangeable. [MariaDB SHA-256 authentication](https://mariadb.com/docs/server/reference/plugins/authentication-plugins/authentication-plugin-sha-256).

### Validate passwords and prevent reuse

Reject weak replacement passwords and prevent recent passwords from being reused. These controls complement the account's authentication plugin.

On MySQL 8.4, inspect the existing validation implementation first:

```sql
SHOW GLOBAL VARIABLES LIKE 'validate_password%';
```

Some Oracle packages enable the component automatically. If an older validation plugin is installed, follow the documented transition before using component settings. The component uses dotted names such as `validate_password.length`; the older plugin uses different names. MySQL 8.0 also provides the component. [Component installation](https://dev.mysql.com/doc/refman/8.4/en/validate-password-installation.html), [component migration](https://dev.mysql.com/doc/refman/8.4/en/validate-password-transitioning.html), [MySQL 8.0 component](https://dev.mysql.com/doc/refman/8.0/en/validate-password.html).

Install the component once if absent, then set the policy:

```sql
INSTALL COMPONENT 'file://component_validate_password';

SET PERSIST validate_password.length = 16;
SET PERSIST validate_password.policy = 'MEDIUM';

SET PERSIST password_history = 6;
SET PERSIST password_reuse_interval = 365;
```

The length and reuse values are example policy choices, not vendor defaults. `MEDIUM` checks length and configured character-class requirements. `SET PERSIST` applies values now and retains them across restarts. [Validation variables](https://dev.mysql.com/doc/refman/8.4/en/validate-password-options-variables.html), [persistent settings](https://dev.mysql.com/doc/refman/8.4/en/set-variable.html).

Account-specific history settings override global policy. For an existing named administrative account:

```sql
ALTER USER 'operator'@'10.0.0.20'
  PASSWORD HISTORY DEFAULT
  PASSWORD REUSE INTERVAL DEFAULT
  PASSWORD REQUIRE CURRENT;
```

`PASSWORD REQUIRE CURRENT` protects ordinary self-service password changes; privileged administrators can reset passwords without supplying the old password. Where organizational policy requires expiration:

```sql
ALTER USER 'operator'@'10.0.0.20'
  PASSWORD EXPIRE INTERVAL 180 DAY;
```

Do not apply unattended expiration to application accounts without a working rotation process. For externally authenticated MySQL accounts, password management belongs in the external identity system. [MySQL password management](https://dev.mysql.com/doc/refman/8.4/en/password-management.html).

MariaDB uses different plugins. On MariaDB 10.11/11.4, install each absent plugin once:

```sql
INSTALL SONAME 'simple_password_check';
INSTALL SONAME 'password_reuse_check';

SET GLOBAL simple_password_check_minimal_length = 16;
SET GLOBAL password_reuse_check_interval = 365;
SET GLOBAL strict_password_validation = ON;
```

Persist their settings in the server option file:

```ini
[mariadb]
simple_password_check_minimal_length = 16
password_reuse_check_interval = 365
strict_password_validation = ON
secure_timestamp = replication
```

MariaDB's reuse plugin provides a time-based policy, not MySQL's `PASSWORD HISTORY 6` syntax. Its interval defaults to zero, meaning unlimited retention, not disabled checking. Keep strict validation enabled so supplying password hashes cannot bypass the installed validators. [Simple Password Check](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/simple-password-check-plugin), [reuse interval](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password_reuse_check_interval).

Reuse checking appeared in MariaDB 10.7. Use a maintained release with plugin version 2.0; upgrading from its older storage format invalidated previously recorded reuse protection. MariaDB also supports the per-account expiration statement above when policy requires it. [Password Reuse Check](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password-reuse-check-plugin), [MariaDB password expiry](https://mariadb.com/docs/server/security/user-account-management/user-password-expiry).

For MariaDB password expiration and temporal controls to resist session-clock tampering, set `secure_timestamp` to `YES` or `replication`, as in the option file above. The default `NO` lets any user use `SET TIMESTAMP` to advance the session clock before changing a password, recording a future last-change time and evading expiration. `YES` pins timestamps to the system clock; `replication` permits only replication threads to adjust them. Use `replication` on replicas, since `YES` can cause discrepancies with statement-based replication. This is a startup-only setting: restart and check the effective value before relying on expiration. Review existing password-change timestamps for prior tampering. [MariaDB password expiry bypass](https://mariadb.com/docs/server/security/user-account-management/user-password-expiry), [MariaDB secure_timestamp](https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#secure_timestamp).

The account, role, and password controls above are Community-available. Plugin examples require the relevant installed libraries and compatible clients.

MFA: MySQL 8.0.27 and later support up to three authentication factors per account; internal credential-storage plugins cannot supply factors 2 and 3. The device plugin is FIDO from 8.0.27, deprecated as of 8.0.35 and removed in 8.4. WebAuthn replaces it from 8.2 onward, including 8.4 LTS. Both server-side device plugins are Enterprise-only. On Community builds, `REQUIRE X509` adds possession of a machine-held certificate to password authentication, but does not establish MFA for a person; put human access paths behind MFA per [mfa.md](mfa.md). [MySQL MFA](https://dev.mysql.com/doc/refman/8.0/en/multifactor-authentication.html), [FIDO](https://dev.mysql.com/doc/refman/8.0/en/fido-pluggable-authentication.html), [WebAuthn](https://dev.mysql.com/doc/refman/8.4/en/webauthn-pluggable-authentication.html), [8.4 removals](https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html).

## 3. File-loading restrictions

File-loading features can expose files readable by the client or database service. Disable `LOCAL` loading unless an identified import workflow requires it:

```ini
[mysqld]
local_infile = OFF

[mysql]
local-infile = 0
```

The server and client settings protect different ends of the connection. Configure application connectors separately; the command-line client's option group does not configure application libraries. MySQL 8.4 already disables server-side `local_infile` by default, but an explicit setting documents the policy. [MySQL LOCAL security](https://dev.mysql.com/doc/refman/8.4/en/load-data-local-security.html).

For MySQL 8.0/8.4, disable the server-file operations governed by `secure_file_priv` when unnecessary:

```ini
[mysqld]
secure_file_priv = NULL
```

`NULL` disables these operations; an empty value removes the restriction. If imports or exports are required, use an existing restricted directory instead. Restart after changing this startup-only setting. [MySQL file restrictions](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_secure_file_priv).

For MariaDB, use a dedicated existing directory, readable and writable only as needed by the service and authorized operators:

```ini
[mysqld]
local_infile = OFF
secure_file_priv = /var/lib/mysql-files
```

MariaDB documents a pathname restriction, not MySQL's `NULL` disable value. Do not copy that value across products. Its `secure_file_priv` setting also requires a restart, and its server-side `local_infile` default is `ON`. [MariaDB server variables](https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#secure_file_priv).

Continue withholding `FILE` from runtime accounts. `LOAD DATA LOCAL` does not require MySQL's `FILE` privilege, so withholding it does not replace disabling local loading. These are core/free controls; test import, restore, and MySQL Shell loading workflows before rollout because some require `LOCAL`. [MySQL LOAD DATA](https://dev.mysql.com/doc/refman/8.4/en/load-data.html), [MariaDB LOAD DATA](https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/inserting-loading-data/load-data-into-tables-or-index/load-data-infile).

## 4. Client side

Require server identity verification in addition to encryption.

Paste each shell block whole. Substitute inside the single quotes on its `set --` line; values containing a literal apostrophe need correct shell escaping. Use absolute paths for certificate files. The guards assume ordinary shell builtins and do not protect a fragment pasted from below the guards.

For the MySQL client:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DATABASE_HOST' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "supply exactly 2 values; not connecting"; exit 1; }
  case "$1$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace every placeholder; not connecting"; exit 1 ;;
    *)
      [ -n "$1" ] || { echo "argument 1 is empty; not connecting"; exit 1; }
      [ -n "$2" ] || { echo "argument 2 is empty; not connecting"; exit 1; }
      [ -f "$2" ] || { echo "CA must be a regular file"; exit 1; }
      [ -r "$2" ] || { echo "CA must be readable"; exit 1; }
      mysql --protocol=TCP --host="$1" --port=3306 --user=app -p \
        --ssl-mode=VERIFY_IDENTITY --ssl-ca="$2"
      ;;
  esac
)
```

`--ssl-mode=REQUIRED` encrypts without certificate verification. `VERIFY_CA` verifies the certificate chain; `VERIFY_IDENTITY` also checks the hostname. Connector options in application code follow the same distinction. [MySQL encrypted connections](https://dev.mysql.com/doc/refman/8.4/en/using-encrypted-connections.html).

For MariaDB clients, use `mariadb` and replace `--ssl-mode=VERIFY_IDENTITY` with `--ssl --ssl-verify-server-cert`, retaining the CA option and guards. Do not assume MySQL-specific flags are accepted. [MariaDB client options](https://mariadb.com/docs/server/clients-and-utilities/mariadb-client/mariadb-command-line-client).

The existing `batch` account's `REQUIRE X509` also needs a client certificate and key. With the MySQL client:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DATABASE_HOST' 'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "supply exactly 4 values; not connecting"; exit 1; }
  case "$1$2$3$4" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace every placeholder; not connecting"; exit 1 ;;
    *)
      [ -n "$1" ] || { echo "argument 1 is empty; not connecting"; exit 1; }
      [ -n "$2" ] || { echo "argument 2 is empty; not connecting"; exit 1; }
      [ -n "$3" ] || { echo "argument 3 is empty; not connecting"; exit 1; }
      [ -n "$4" ] || { echo "argument 4 is empty; not connecting"; exit 1; }
      [ -f "$2" ] || { echo "CA must be a regular file"; exit 1; }
      [ -r "$2" ] || { echo "CA must be readable"; exit 1; }
      [ -f "$3" ] || { echo "certificate must be a regular file"; exit 1; }
      [ -r "$3" ] || { echo "certificate must be readable"; exit 1; }
      [ -f "$4" ] || { echo "key must be a regular file"; exit 1; }
      [ -r "$4" ] || { echo "key must be readable"; exit 1; }
      mysql --protocol=TCP --host="$1" --port=3306 --user=batch -p \
        --ssl-mode=VERIFY_IDENTITY --ssl-ca="$2" \
        --ssl-cert="$3" --ssl-key="$4"
      ;;
  esac
)
```

Apply the same MariaDB client substitution when appropriate. Restrict access to the private key. A CA file alone does not satisfy `REQUIRE X509`. [MySQL client certificates](https://dev.mysql.com/doc/refman/8.4/en/using-encrypted-connections.html), [MariaDB certificate options](https://mariadb.com/docs/server/clients-and-utilities/mariadb-client/mariadb-command-line-client).

## 5. Verify

Service behavior below is **REASONED, not demonstrated**. The authoring environment has a read-only filesystem, no MySQL/MariaDB client or server binaries, no Docker/Podman runtime, and no supplied writable deployment or database credentials. No available authorized environment could reproduce the exposed and fixed service states.

Locally, all seven shell blocks passed `bash -n` and ShellCheck. Guard-only execution under `bash -u` rejected 119 tested invalid-input cases across the five guarded blocks, including an empty value in every argument position, embedded placeholders, angle brackets, example hostnames, missing/wrong markers, and incorrect argument counts. Each guard also accepted one valid dispatch case. These tests exercised guards only; no database behavior was simulated.

All five INI fragments parsed with an in-memory INI parser. This checks basic structure, not vendor option acceptance. Native configuration parsing and restart behavior remain REASONED because the server binaries and writable deployment are unavailable.

The snapshot's C2 scanner does not classify `mysql`, `mariadb`, or `ss` as probes. A supplemental in-memory check added those command names, accepted these guarded blocks, and detected a deliberately unguarded probe before the guard. No gate or repository file was changed.

### TLS and account requirements

**REASONED: missing a writable deployment, compatible clients, known-good credentials, and deployment certificates.**

Through an administrative session, inspect both global and account requirements:

```sql
SHOW GLOBAL VARIABLES LIKE 'require_secure_transport';
SELECT User, Host, ssl_type FROM mysql.user;
```

The fixed configuration must report secure transport enabled and the intended accounts' TLS requirements. In an exposed test deployment with both controls removed, these observations differ. Account requirements and global requirements must be assessed separately; one does not demonstrate the other. [MySQL transport enforcement](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_require_secure_transport), [MySQL grant-table fields](https://dev.mysql.com/doc/refman/8.4/en/grant-tables.html).

At the interactive client prompt, `\s` displays this session's SSL cipher. It does not establish server-wide enforcement or hostname verification. [MySQL client commands](https://dev.mysql.com/doc/refman/8.4/en/mysql-commands.html).

Run the following from the application's permitted source host. Replace the product with `mysql` or `mariadb`. Both commands use the same host, port, account, and known-good password.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PRODUCT' 'REPLACE_WITH_DATABASE_HOST' 'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "supply exactly 3 values; not connecting"; exit 1; }
  case "$1$2$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace every placeholder; not connecting"; exit 1 ;;
    *)
      [ -n "$1" ] || { echo "argument 1 is empty; not connecting"; exit 1; }
      [ -n "$2" ] || { echo "argument 2 is empty; not connecting"; exit 1; }
      [ -n "$3" ] || { echo "argument 3 is empty; not connecting"; exit 1; }
      [ -f "$3" ] || { echo "CA must be a regular file"; exit 1; }
      [ -r "$3" ] || { echo "CA must be readable"; exit 1; }
      case "$1" in
        mysql)
          mysql --protocol=TCP --host="$2" --port=3306 --user=app -p \
            --connect-timeout=5 --ssl-mode=VERIFY_IDENTITY --ssl-ca="$3" \
            -e "SELECT 1; SELECT CURRENT_USER(); SHOW SESSION STATUS LIKE 'Ssl_cipher';" \
            || { echo "positive control failed; stop"; exit 1; }
          if mysql --protocol=TCP --host="$2" --port=3306 --user=app -p \
            --connect-timeout=5 --ssl-mode=DISABLED -e 'SELECT 1;'
          then
            echo "FAIL: cleartext connection succeeded"; exit 1
          else
            echo "inspect the refusal and requirements; failure alone is not a pass"
          fi
          ;;
        mariadb)
          mariadb --protocol=TCP --host="$2" --port=3306 --user=app -p \
            --connect-timeout=5 --ssl --ssl-verify-server-cert --ssl-ca="$3" \
            -e "SELECT 1; SELECT CURRENT_USER(); SHOW SESSION STATUS LIKE 'Ssl_cipher';" \
            || { echo "positive control failed; stop"; exit 1; }
          if mariadb --protocol=TCP --host="$2" --port=3306 --user=app -p \
            --connect-timeout=5 --disable-ssl -e 'SELECT 1;'
          then
            echo "FAIL: cleartext connection succeeded"; exit 1
          else
            echo "inspect the refusal and requirements; failure alone is not a pass"
          fi
          ;;
        *) echo "product must be mysql or mariadb"; exit 1 ;;
      esac
      ;;
  esac
)
```

The positive control must succeed, identify the intended account through `CURRENT_USER()`, and show a nonempty session cipher. Enter the same known-good password when prompted; then inspect the server's refusal.

MySQL error 1045 is generic access denial, not standalone proof of TLS enforcement. Error 3159 specifically identifies global secure-transport enforcement. A timeout, wrong password, unknown option, certificate-loading error, or authentication-plugin failure is inconclusive. The block deliberately does not print a pass merely because the negative command failed. [Password prompting](https://dev.mysql.com/doc/refman/8.4/en/connection-options.html), [1045 definition](https://dev.mysql.com/doc/mysql-errors/8.4/en/server-error-reference.html#error_er_access_denied_error), [3159 definition](https://dev.mysql.com/doc/mysql-errors/8.4/en/server-error-reference.html#error_er_secure_transport_required).

In an isolated exposed-state test, both TLS restrictions are absent and the same cleartext request must succeed. If `caching_sha2_password` instead needs an unavailable RSA exchange after its cache is cleared, that failure does not demonstrate TLS policy. Repeat the positive control and resolve authentication prerequisites before drawing a conclusion. [MySQL authentication exchange](https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html).

For server identity, repeat the positive connection against the same reachable endpoint using a valid but unrelated CA file, or a test hostname resolving to that endpoint but absent from its certificate. Expect certificate verification failure; restore the correct CA and hostname and require success. [MySQL certificate verification](https://dev.mysql.com/doc/refman/8.4/en/using-encrypted-connections.html).

For the existing `batch` account, compare a connection with its valid client certificate to an otherwise matched connection without one. Run from its permitted source host, using the same known-good password at both prompts. This MySQL client block disables option-file and login-path loading so the negative cannot inherit a certificate. [MySQL option-file controls](https://dev.mysql.com/doc/refman/8.4/en/option-file-options.html).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DATABASE_HOST' 'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_CLIENT_CERT_FILE' 'REPLACE_WITH_CLIENT_KEY_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "supply exactly 4 values; not connecting"; exit 1; }
  case "$1$2$3$4" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace every placeholder; not connecting"; exit 1 ;;
    *)
      [ -n "$1" ] || { echo "argument 1 is empty; not connecting"; exit 1; }
      [ -n "$2" ] || { echo "argument 2 is empty; not connecting"; exit 1; }
      [ -n "$3" ] || { echo "argument 3 is empty; not connecting"; exit 1; }
      [ -n "$4" ] || { echo "argument 4 is empty; not connecting"; exit 1; }
      [ -f "$2" ] || { echo "CA must be a regular file"; exit 1; }
      [ -r "$2" ] || { echo "CA must be readable"; exit 1; }
      [ -f "$3" ] || { echo "certificate must be a regular file"; exit 1; }
      [ -r "$3" ] || { echo "certificate must be readable"; exit 1; }
      [ -f "$4" ] || { echo "key must be a regular file"; exit 1; }
      [ -r "$4" ] || { echo "key must be readable"; exit 1; }
      mysql --no-defaults --no-login-paths --protocol=TCP --host="$1" --port=3306 --user=batch -p \
        --ssl-mode=VERIFY_IDENTITY --ssl-ca="$2" \
        --ssl-cert="$3" --ssl-key="$4" --connect-timeout=5 \
        -e "SELECT 1; SELECT CURRENT_USER(); SHOW SESSION STATUS LIKE 'Ssl_cipher';" \
        || { echo "certificate positive control failed; stop"; exit 1; }
      if mysql --no-defaults --no-login-paths --protocol=TCP \
        --host="$1" --port=3306 --user=batch -p --connect-timeout=5 \
        --ssl-mode=VERIFY_IDENTITY --ssl-ca="$2" -e 'SELECT 1;'
      then
        echo "FAIL: connection without a client certificate succeeded"; exit 1
      else
        echo "inspect the certificate requirement and refusal; failure alone is not a pass"
      fi
      ;;
  esac
)
```

The certificate-bearing positive must succeed as the intended `batch` account with a nonempty cipher. In an isolated baseline where that same account has only `REQUIRE SSL`, the certificate-free command must also succeed. After enforcing `REQUIRE X509` (or `SUBJECT`/`ISSUER`, which imply X509), that same command must be rejected for lacking the required client certificate while the positive still succeeds. Inspect the effective account requirement and refusal; generic error 1045 alone does not establish the cause. Wrong credentials, connectivity failures, or failed server-certificate verification are inconclusive. A missing-certificate test distinguishes certificate-required policy from SSL-only policy; to test a specific subject or issuer restriction, also use a valid certificate with a non-matching subject or issuer and require rejection. [MySQL account certificate requirements](https://dev.mysql.com/doc/refman/8.4/en/create-user.html#create-user-tls).

For MariaDB, adapt the whole block using `mariadb --no-defaults`, omit MySQL's `--no-login-paths`, and replace `--ssl-mode=VERIFY_IDENTITY` with `--ssl --ssl-verify-server-cert` in both commands. Retain the CA, certificate/key positive, certificate-free negative, password prompts, and guards. [MariaDB client options](https://mariadb.com/docs/server/clients-and-utilities/mariadb-client/mariadb-command-line-client).

### Listeners

**REASONED: missing access to the database server's network namespace and its writable listener configuration.**

Run on the database server, using its actual `hostname` output:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DATABASE_SERVER_HOSTNAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly 1 value; not connecting"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace every placeholder; not connecting"; exit 1 ;;
    *)
      [ -n "$1" ] || { echo "argument 1 is empty; not connecting"; exit 1; }
      [ "$(hostname)" = "$1" ] || { echo "run on the named database server"; exit 1; }
      ss -tlnp
      ;;
  esac
)
```

Read every listener, including configured nondefault ports. In the exposed state, classic protocol or X Protocol listens on an unintended interface. In the fixed loopback deployment, classic protocol remains available on loopback, and X Protocol is either loopback-only or disabled. For deliberate remote access, require only the intended private interfaces. Pair this observation with a successful connection from the permitted location; no listener at all can mean a stopped service. [MySQL listener configuration](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_bind_address), [X Plugin listener configuration](https://dev.mysql.com/doc/refman/8.4/en/x-plugin-options-system-variables.html).

### Scoped grants and cleanup

**REASONED: missing a writable deployment, administrative credentials, and disposable tables for exposed/fixed comparisons.**

As an administrator, inspect the runtime account:

```sql
SHOW GRANTS FOR 'app'@'10.0.0.10';
```

On MySQL, always check the server-wide role settings, even if the account uses direct grants:

```sql
SELECT @@GLOBAL.mandatory_roles, @@GLOBAL.activate_all_roles_on_login;
```

`SHOW GRANTS FOR 'app'@'10.0.0.10'` omits mandatory roles and does not expand role privileges. Combine its explicitly granted roles with every existing role in `@@GLOBAL.mandatory_roles`. Mandatory roles are treated as granted to every account; they still require activation. With `activate_all_roles_on_login=ON`, all granted roles, including mandatory roles, activate at login. Otherwise, only default roles activate at login; the session can activate other granted roles with `SET ROLE`. [MySQL roles and activation](https://dev.mysql.com/doc/refman/8.4/en/roles.html).

Expand the full combined list with `SHOW GRANTS ... USING`, preserving each role's host part. If `app_runtime` is the only granted role and there are no mandatory roles:

```sql
SHOW GRANTS FOR 'app'@'10.0.0.10' USING 'app_runtime'@'%';
```

When other explicit or mandatory roles exist, append all of them as comma-separated role names in that same `USING` clause. Inspect inherited roles too. The resulting privileges describe access available with those roles activated, not necessarily the roles active in a particular session. Plain `SHOW GRANTS` in the application's own session includes mandatory role assignments, but still needs `USING` to expand role privileges. [MySQL SHOW GRANTS](https://dev.mysql.com/doc/refman/8.4/en/show-grants.html).

In MariaDB, inspect each granted role and recursively inspect roles it inherits:

```sql
SHOW GRANTS FOR app_runtime;
```

MariaDB permits one current role plus its inherited privileges; do not use MySQL's multiple-role activation or `SHOW GRANTS ... USING` audit there. Also repeat `SHOW GRANTS FOR PUBLIC` on MariaDB 10.11+, since its grants apply to every account independently of the selected role. A `USAGE ON *.*` line denotes no privileges; it is not equivalent to a global data-access grant. [MariaDB SHOW GRANTS](https://mariadb.com/docs/server/reference/sql-statements/administrative-sql-statements/show/show-grants), [MariaDB roles](https://mariadb.com/docs/server/security/user-account-management/roles/roles_overview), [MariaDB role activation](https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/set-role), [MariaDB PUBLIC privileges](https://mariadb.com/docs/server/security/user-account-management/roles/system-users-roles-and-privileges).

For a behavioral comparison, use an isolated fixture with existing, populated `app.orders` and `app.private_probe` tables. From a fresh application connection:

```sql
SELECT CURRENT_USER();
SELECT CURRENT_ROLE();
SELECT 1 FROM app.orders LIMIT 1;
SELECT 1 FROM app.private_probe LIMIT 1;
```

The positive read of `orders` must succeed. With an exposed broad read grant, the second table read succeeds too; with the scoped grant, it must receive a privilege denial. A nonexistent table or failed login is not the expected denial. Repeat the reads in the same disposable MySQL session after `SET ROLE ALL;`, and inspect `CURRENT_ROLE()` again, so an inactive mandatory or granted role cannot hide broader access. On MariaDB, repeat with each granted role activated individually using `SET ROLE role_name;`, substituting its actual name. Repeat required application operations on disposable fixtures, and inspect grants for unnecessary operations and inherited privileges. [MySQL table privileges](https://dev.mysql.com/doc/refman/8.4/en/grant.html).

Repeat the two installation inventories from section 2 before and after cleanup. The fixed inventory has no anonymous accounts, no unused remote root accounts, and no unintended anonymous or test-schema grants. Deliberately retained administrative accounts and similarly named application databases must remain identifiable. Preserve a successful administrative login and the runtime positive control across cleanup. [MySQL cleanup behavior](https://dev.mysql.com/doc/refman/8.4/en/mysql-secure-installation.html), [MariaDB cleanup behavior](https://mariadb.com/docs/server/clients-and-utilities/deployment-tools/mariadb-secure-installation).

### File-loading restrictions

**REASONED: missing a writable deployment, client/server fixture files, and a disposable import table.**

Inspect effective server settings after restart:

```sql
SHOW GLOBAL VARIABLES LIKE 'local_infile';
SHOW GLOBAL VARIABLES LIKE 'secure_file_priv';
```

Expect `local_infile` to be `OFF`. Expect MySQL's `secure_file_priv` to be SQL `NULL` under the disable policy, or the deliberately selected directory under an import policy. MariaDB must report the configured restricted directory.

For behavioral tests, prepare a disposable one-column integer table named `app.import_probe` and files containing one integer per line. Use a dedicated test account with the table privileges needed for these tests. First prove that ordinary insertion works:

```sql
INSERT INTO app.import_probe VALUES (1);
```

With a known-readable client fixture, replace the path and run:

```sql
LOAD DATA LOCAL INFILE '/REPLACE_WITH_CLIENT_FIXTURE_PATH'
  INTO TABLE app.import_probe;
```

In the isolated exposed state, enable `LOCAL` on both client and server and require this exact load to succeed. To test the server control, keep that client enabled and disable only server `local_infile`; require a local-loading-disabled error. To test the client control, keep the isolated server enabled and reconnect with the client setting disabled. Do not configure a permitted local-load directory exception for that test. The ordinary insertion must still succeed. Restore both disabled settings afterward. [MySQL LOCAL controls and errors](https://dev.mysql.com/doc/refman/8.4/en/load-data-local-security.html), [MariaDB LOCAL loading](https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/inserting-loading-data/load-data-into-tables-or-index/load-data-infile).

For server-file restrictions, use a dedicated test account with `FILE` and the necessary table privilege; never grant `FILE` to the runtime account:

```sql
LOAD DATA INFILE '/var/lib/mysql-files/probe.tsv'
  INTO TABLE app.import_probe;
```

For MySQL, first require this known-readable file to load under a policy permitting that directory; after restarting with `secure_file_priv = NULL`, the same statement must be refused while ordinary insertion still works.

For MariaDB, retain successful loading from the permitted directory and attempt the same statement with a known-readable fixture outside it. That outside-directory load must succeed in the isolated unrestricted baseline and fail under the directory restriction. Missing files, operating-system permission failures, and missing SQL privileges do not demonstrate `secure_file_priv`. [MySQL server-file policy](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_secure_file_priv), [MariaDB server-file policy](https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#secure_file_priv).

### Password validation and reuse

**REASONED: missing a writable deployment, installed validation libraries, and a disposable password-managed account.**

On MySQL, inspect policy and account overrides:

```sql
SHOW GLOBAL VARIABLES LIKE 'validate_password.%';

SHOW GLOBAL VARIABLES
WHERE Variable_name IN ('password_history', 'password_reuse_interval');

SELECT User, Host, Password_reuse_history, Password_reuse_time,
       Password_require_current, password_lifetime
FROM mysql.user
WHERE User = 'operator' AND Host = '10.0.0.20';
```

Require the selected global values and account inheritance settings. MySQL's nullable account history fields distinguish inherited policy from explicit overrides. Repeat after restart to check persistence. [MySQL password management](https://dev.mysql.com/doc/refman/8.4/en/password-management.html), [MySQL grant-table fields](https://dev.mysql.com/doc/refman/8.4/en/grant-tables.html).

On MariaDB:

```sql
SHOW PLUGINS;

SHOW GLOBAL VARIABLES
WHERE Variable_name IN (
  'simple_password_check_minimal_length',
  'password_reuse_check_interval',
  'strict_password_validation',
  'secure_timestamp'
);
```

Require both validation plugins to be active and the selected values to survive restart. Require `secure_timestamp` to report `REPLICATION` for the example configuration, or `YES` for a deliberate non-replica policy; `NO` leaves the expiration bypass open. Confirm the installed reuse plugin is version 2.0 through the deployment's plugin metadata. [MariaDB validation plugin](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/simple-password-check-plugin), [MariaDB reuse plugin](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password-reuse-check-plugin).

For behavioral checks, provision a disposable `policy_probe` account with the same authentication plugin and inherited policy as the account being tested. Through an administrative session, use the applicable statement repeatedly.

MySQL:

```sql
ALTER USER 'policy_probe'@'10.0.0.20'
  IDENTIFIED WITH caching_sha2_password BY 'REPLACE_WITH_TEST_PASSWORD';
```

MariaDB:

```sql
ALTER USER 'policy_probe'@'10.0.0.20'
  IDENTIFIED VIA ed25519 USING PASSWORD('REPLACE_WITH_TEST_PASSWORD');
```

In the isolated exposed state without validation, a deliberately weak test value such as `x` is accepted. With validation enabled, it must be rejected while a fresh generated password satisfying the policy succeeds.

For reuse, set two distinct policy-compliant test passwords in sequence, then attempt the first again. Without reuse protection the third change succeeds; with protection enabled and history recorded under that policy, it must fail. A third fresh password must succeed. Keep the authentication plugin unchanged throughout, and do not use production credentials. These tests distinguish validation and history enforcement from a general inability to change passwords. [MySQL validation behavior](https://dev.mysql.com/doc/refman/8.4/en/validate-password.html), [MySQL password reuse](https://dev.mysql.com/doc/refman/8.4/en/password-management.html), [MariaDB password changes](https://mariadb.com/docs/server/reference/plugins/authentication-plugins/authentication-plugin-ed25519), [MariaDB reuse behavior](https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password-reuse-check-plugin).

Verification debt:

| ID | Status | Required demonstration |
| --- | --- | --- |
| MYSQL-LIVE-1 | Open; REASONED | Provide isolated writable MySQL 8.4 and MariaDB 10.11/11.4 deployments, compatible clients, administrative access, certificates, files, and disposable accounts/tables. Demonstrate exposed and fixed outcomes for TLS and account requirements, listeners, scoped grants, cleanup, file loading, and password policies; run native configuration checks and restart tests. Record versions, requests, positive controls, refusals, and observed outcomes before removing REASONED labels. |

## Common mistakes

- Creating `'app'@'%'` with a weak password to fix a connection error, then never tightening access.
- Creating a narrower account but leaving an older broad account usable.
- Skipping `require_secure_transport` because "the network is internal"; internal networks are where lateral movement happens.
- Shipping a client with `--ssl-mode=DISABLED` to silence certificate errors instead of installing the CA ([self-signed.md](self-signed.md)).
- Treating error 1045, a timeout, or a password prompt as proof of TLS enforcement.
- Binding `bind_address` to loopback but leaving the separately enabled MySQL X Plugin exposed. Set `mysqlx_bind_address` too, or disable an unused X Plugin.
- On MariaDB deployments using systemd socket activation, assuming `bind_address` controls sockets created by `mariadb.socket`. Configure the socket unit's listening addresses, or disable socket activation, and inspect effective listeners. [MariaDB systemd socket activation](https://mariadb.com/docs/server/server-management/starting-and-stopping-mariadb/systemd/configuring).
- Copying MySQL's `secure_file_priv = NULL`, dotted validation settings, or role activation syntax into MariaDB.
- Assuming global password policy overrides account-specific settings.
- Treating schema-name hiding as the access boundary. MySQL normally limits `SHOW DATABASES` according to privileges, and global privileges can broaden visibility. Reduce grants and remove unintended test access. [MySQL SHOW DATABASES](https://dev.mysql.com/doc/refman/8.4/en/show-databases.html).

## Sources (checked September 2026)

- Official MySQL Docker images (8.4, 9.7 and innovation, with identical entrypoints; shown for 8.4; pinned commit 2f988f198f35d25b1454fa2504a0e4c348100549): the `mysql-community-server-minimal` install and `my.cnf` edits (socket and `!includedir /etc/mysql/conf.d/`, no bind), `EXPOSE 3306 33060` and `CMD ["mysqld"]`; the entrypoint's password requirement, `file_env 'MYSQL_ROOT_HOST' '%'`, and the `root@'${MYSQL_ROOT_HOST}'` account with `GRANT ALL ... WITH GRANT OPTION`, created only when a new data directory is initialized: https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/Dockerfile.oracle#L61-L89, https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/Dockerfile.oracle#L120-L123, https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/docker-entrypoint.sh#L138-L147, https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/docker-entrypoint.sh#L223-L240, https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/docker-entrypoint.sh#L276-L285 and https://github.com/docker-library/mysql/blob/2f988f198f35d25b1454fa2504a0e4c348100549/8.4/docker-entrypoint.sh#L380-L390
- MySQL's Docker server package `my.cnf`, which sets no bind address (pinned tag mysql-8.4.9; the same in mysql-9.7.2 and mysql-26.7.0): https://github.com/mysql/mysql-server/blob/mysql-8.4.9/packaging/rpm-docker/my.cnf.in and https://github.com/mysql/mysql-server/blob/mysql-8.4.9/packaging/rpm-docker/mysql.spec.in#L298
- Official MariaDB Docker images (10.6 through 13.1, Ubuntu and UBI; shown for 11.8; pinned commit 1a4c8e99f7816c8d97df11eee52098522dc770cf): the Ubuntu build comments out every `bind-address` line and runs `CMD ["mariadbd"]`, the UBI build installs the `MariaDB-server` package and copies in `docker.cnf`, and the entrypoint's password requirement, `MARIADB_`/`MYSQL_` variable merging, root host default `%` and `root@'${MARIADB_ROOT_HOST}'` account: https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/Dockerfile#L125-L127, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/Dockerfile#L141-L144, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8-ubi/Dockerfile#L37, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8-ubi/Dockerfile#L96, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/docker.cnf, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/docker-entrypoint.sh#L44-L52, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/docker-entrypoint.sh#L168-L170, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/docker-entrypoint.sh#L269, https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/docker-entrypoint.sh#L287-L288 and https://github.com/MariaDB/mariadb-docker/blob/1a4c8e99f7816c8d97df11eee52098522dc770cf/11.8/docker-entrypoint.sh#L394-L409
- MariaDB packaged `bind-address` (Debian `127.0.0.1`, RPM commented out) and the unset bind that listens on the IPv4 wildcard and, where available, the IPv6 one (pinned tag mariadb-11.8.9; the packaged settings, the `*` handling and the bind loop are the same at every shipped version, 10.6.28 through 13.1.1): https://github.com/MariaDB/server/blob/mariadb-11.8.9/debian/additions/mariadb.conf.d/50-server.cnf#L27, https://github.com/MariaDB/server/blob/mariadb-11.8.9/support-files/rpm/server.cnf#L40, https://github.com/MariaDB/server/blob/mariadb-11.8.9/sql/mysqld.cc#L2436-L2439, https://github.com/MariaDB/server/blob/mariadb-11.8.9/sql/mysqld.cc#L2482-L2493 and https://github.com/MariaDB/server/blob/mariadb-11.8.9/sql/mysqld.cc#L2540-L2552
- MySQL 9.7 and 26.7 `bind_address` and `mysqlx_bind_address` defaults (`*`), with the X Plugin enabled by default: https://dev.mysql.com/doc/refman/9.7/en/server-system-variables.html#sysvar_bind_address, https://dev.mysql.com/doc/refman/26.7/en/server-system-variables.html#sysvar_bind_address, https://dev.mysql.com/doc/refman/9.7/en/x-plugin-options-system-variables.html and https://dev.mysql.com/doc/refman/26.7/en/x-plugin-options-system-variables.html
- `skip_networking` stops TCP listening: the MySQL manual, the X Plugin creating no TCP listener when it is `ON` (pinned tag mysql-8.4.9; the same in mysql-9.7.2 and mysql-26.7.0), and the MariaDB manual: https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html#sysvar_skip_networking, https://github.com/mysql/mysql-server/blob/mysql-8.4.9/plugin/x/src/ngs/socket_acceptors_task.cc#L145-L163 and https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#skip_networking
- MySQL encrypted connections: https://dev.mysql.com/doc/refman/8.4/en/using-encrypted-connections.html
- MySQL secure deployment and TLS protocol support: https://dev.mysql.com/doc/mysql-secure-deployment-guide/8.0/en/secure-deployment-secure-connections.html
- MySQL automatic certificate generation: https://dev.mysql.com/doc/refman/8.4/en/creating-ssl-rsa-files-using-mysql.html
- MySQL server variables, including bind_address, require_secure_transport, and secure_file_priv: https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html
- MySQL 8.0 X Plugin options and defaults: https://dev.mysql.com/doc/refman/8.0/en/x-plugin-options-system-variables.html
- MySQL 8.4 X Plugin options and defaults: https://dev.mysql.com/doc/refman/8.4/en/x-plugin-options-system-variables.html
- MySQL CREATE USER: https://dev.mysql.com/doc/refman/8.4/en/create-user.html
- MySQL ALTER USER: https://dev.mysql.com/doc/refman/8.4/en/alter-user.html
- MySQL GRANT: https://dev.mysql.com/doc/refman/8.4/en/grant.html
- MySQL account names and host matching: https://dev.mysql.com/doc/refman/8.4/en/account-names.html
- MySQL roles: https://dev.mysql.com/doc/refman/8.4/en/roles.html
- MySQL privileges: https://dev.mysql.com/doc/refman/8.4/en/privileges-provided.html
- MySQL 8.4 changes and removals: https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html
- MySQL installation hardening: https://dev.mysql.com/doc/refman/8.4/en/mysql-secure-installation.html
- MySQL grant tables: https://dev.mysql.com/doc/refman/8.4/en/grant-tables.html
- MySQL SHOW GRANTS: https://dev.mysql.com/doc/refman/8.4/en/show-grants.html
- MySQL 8.0 caching SHA-2 authentication: https://dev.mysql.com/doc/refman/8.0/en/caching-sha2-pluggable-authentication.html
- MySQL 8.4 caching SHA-2 authentication: https://dev.mysql.com/doc/refman/8.4/en/caching-sha2-pluggable-authentication.html
- MySQL native authentication lifecycle: https://dev.mysql.com/doc/refman/8.4/en/native-pluggable-authentication.html
- MySQL 8.0 password validation component: https://dev.mysql.com/doc/refman/8.0/en/validate-password.html
- MySQL password validation behavior: https://dev.mysql.com/doc/refman/8.4/en/validate-password.html
- MySQL validation component installation: https://dev.mysql.com/doc/refman/8.4/en/validate-password-installation.html
- MySQL validation component migration: https://dev.mysql.com/doc/refman/8.4/en/validate-password-transitioning.html
- MySQL validation variables: https://dev.mysql.com/doc/refman/8.4/en/validate-password-options-variables.html
- MySQL variable assignment and persistence: https://dev.mysql.com/doc/refman/8.4/en/set-variable.html
- MySQL password management: https://dev.mysql.com/doc/refman/8.4/en/password-management.html
- MySQL LOCAL loading security: https://dev.mysql.com/doc/refman/8.4/en/load-data-local-security.html
- MySQL LOAD DATA syntax and privileges: https://dev.mysql.com/doc/refman/8.4/en/load-data.html
- MySQL option-file syntax and groups: https://dev.mysql.com/doc/refman/8.4/en/option-files.html
- MySQL option-file command-line controls: https://dev.mysql.com/doc/refman/8.4/en/option-file-options.html
- MySQL connection options and password prompting: https://dev.mysql.com/doc/refman/8.4/en/connection-options.html
- MySQL client options: https://dev.mysql.com/doc/refman/8.4/en/mysql-command-options.html
- MySQL interactive client commands: https://dev.mysql.com/doc/refman/8.4/en/mysql-commands.html
- MySQL server errors: https://dev.mysql.com/doc/mysql-errors/8.4/en/server-error-reference.html
- MySQL session cipher status: https://dev.mysql.com/doc/refman/8.4/en/server-status-variables.html#statvar_Ssl_cipher
- MySQL SHOW VARIABLES: https://dev.mysql.com/doc/refman/8.4/en/show-variables.html
- MySQL SELECT syntax: https://dev.mysql.com/doc/refman/8.4/en/select.html
- MySQL INSERT syntax: https://dev.mysql.com/doc/refman/8.4/en/insert.html
- MySQL SHOW DATABASES semantics: https://dev.mysql.com/doc/refman/8.4/en/show-databases.html
- MySQL multifactor authentication: https://dev.mysql.com/doc/refman/8.0/en/multifactor-authentication.html
- MySQL FIDO authentication: https://dev.mysql.com/doc/refman/8.0/en/fido-pluggable-authentication.html
- MySQL WebAuthn authentication: https://dev.mysql.com/doc/refman/8.4/en/webauthn-pluggable-authentication.html
- MariaDB TLS overview: https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/secure-connections-overview
- MariaDB TLS configuration: https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/securing-connections-for-client-and-server
- MariaDB automatic TLS requirements: https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/zero-configuration-ssl
- MariaDB TLS variables: https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/ssltls-system-variables
- MariaDB server variables: https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables
- MariaDB ed25519 authentication: https://mariadb.com/docs/server/reference/plugins/authentication-plugins/authentication-plugin-ed25519
- MariaDB SHA-256 authentication availability: https://mariadb.com/docs/server/reference/plugins/authentication-plugins/authentication-plugin-sha-256
- MariaDB CREATE USER: https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/create-user
- MariaDB ALTER USER: https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/alter-user
- MariaDB GRANT and privilege availability: https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/grant
- MariaDB roles overview: https://mariadb.com/docs/server/security/user-account-management/roles/roles_overview
- MariaDB SHOW GRANTS: https://mariadb.com/docs/server/reference/sql-statements/administrative-sql-statements/show/show-grants
- MariaDB SET DEFAULT ROLE: https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/set-default-role
- MariaDB SET ROLE: https://mariadb.com/docs/server/reference/sql-statements/account-management-sql-statements/set-role
- MariaDB PUBLIC role: https://mariadb.com/docs/server/security/user-account-management/roles/system-users-roles-and-privileges
- MariaDB installation hardening: https://mariadb.com/docs/server/clients-and-utilities/deployment-tools/mariadb-secure-installation
- MariaDB mysql.user compatibility view: https://mariadb.com/docs/server/reference/system-tables/the-mysql-database-tables/mysql-user-table
- MariaDB mysql.db grant table: https://mariadb.com/docs/server/reference/system-tables/the-mysql-database-tables/mysql-db-table
- MariaDB Simple Password Check: https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/simple-password-check-plugin
- MariaDB Password Reuse Check and version notes: https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password-reuse-check-plugin
- MariaDB password reuse interval: https://mariadb.com/docs/server/reference/plugins/password-validation-plugins/password_reuse_check_interval
- MariaDB secure_timestamp and session-clock restrictions: https://mariadb.com/docs/server/server-management/variables-and-modes/server-system-variables#secure_timestamp
- MariaDB password expiry: https://mariadb.com/docs/server/security/user-account-management/user-password-expiry
- MariaDB LOAD DATA: https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/inserting-loading-data/load-data-into-tables-or-index/load-data-infile
- MariaDB client options: https://mariadb.com/docs/server/clients-and-utilities/mariadb-client/mariadb-command-line-client
- MariaDB protocol differences: https://mariadb.com/docs/server/reference/clientserver-protocol/mariadb-protocol-differences-with-mysql
- MariaDB startup troubleshooting: https://mariadb.com/docs/server/server-management/starting-and-stopping-mariadb/what-to-do-if-mariadb-doesnt-start
- MariaDB systemd socket activation: https://mariadb.com/docs/server/server-management/starting-and-stopping-mariadb/systemd/configuring
