# MySQL and MariaDB: TLS and authentication

Default posture: keep the server on `127.0.0.1` (the packaged default on Debian/Ubuntu) and open it to remote clients only deliberately, with TLS required.

## 1. Server TLS

MySQL 8 generates a CA and server certificate in the data directory at initialization and enables TLS automatically; check with:

```sql
SHOW GLOBAL VARIABLES LIKE '%ssl%';
```

To use your own certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)) and to refuse all cleartext connections, set in `/etc/mysql/mysql.conf.d/mysqld.cnf` (or the equivalent for your packaging):

```ini
[mysqld]
bind_address = 127.0.0.1          # widen deliberately
mysqlx_bind_address = 127.0.0.1   # the X Protocol (33060) is a SEPARATE listener; bind_address does not cover it
require_secure_transport = ON
tls_version = TLSv1.2,TLSv1.3
ssl_ca   = /etc/mysql/certs/ca.pem
ssl_cert = /etc/mysql/certs/server-cert.pem
ssl_key  = /etc/mysql/certs/server-key.pem
```

`require_secure_transport` rejects any TCP connection that is not TLS (Unix-socket connections remain allowed). Recent MariaDB versions support the same option; verify availability for your release.

MySQL 8.4 enables the X Plugin by default, and it is a second listener with its own port (`mysqlx_port`, default `33060`) and its own bind address (`mysqlx_bind_address`, default `*`, every interface). The `bind_address` above governs only the classic protocol on 3306, so a server you carefully bound to loopback still answers the X Protocol on every interface until you set `mysqlx_bind_address` as well, shown above. If you do not use the X Protocol (the X DevAPI / document-store interface), turn the plugin off instead with `mysqlx = OFF`.

## 2. Per-account requirements

Require TLS (or a client certificate) at the account level as a second control:

```sql
ALTER USER 'app'@'10.0.0.%' REQUIRE SSL;
-- or, for mutual TLS:
ALTER USER 'batch'@'10.0.0.%' REQUIRE X509;
```

Account hygiene per [authentication.md](authentication.md): keep the default `caching_sha2_password` plugin for new accounts (MySQL 8) rather than re-enabling `mysql_native_password`, remove anonymous accounts, and give the application a least-privilege user, never `root`.

MFA: MySQL 8.0.27 and later support up to 3 authentication factors per account, with factors 2 and 3 supplied by external plugins. The device plugin is FIDO from 8.0.27 (deprecated as of 8.0.35, removed in 8.4) and WebAuthn, which replaces it, from 8.2 onward including 8.4 LTS; in both cases the server-side plugin ships only in Enterprise Edition. On Community builds, `REQUIRE X509` client certificates add a possession factor held by the connecting machine, stronger than a password alone but not MFA for a person; put human access paths behind MFA per [mfa.md](mfa.md).

## 3. Client side

Require identity verification of the server in addition to encryption:

```bash
mysql --host db.example.com --user app -p \
  --ssl-mode=VERIFY_IDENTITY --ssl-ca=/path/ca.pem
```

`--ssl-mode=REQUIRED` encrypts without identity verification; `VERIFY_CA`/`VERIFY_IDENTITY` verify the certificate (MySQL clients; MariaDB clients use `--ssl-verify-server-cert`). Connector options in application code follow the same distinction.

## 4. Verify

```sql
SHOW GLOBAL VARIABLES LIKE 'require_secure_transport';
SELECT user, host, ssl_type FROM mysql.user;      -- REQUIRE settings per account
\s                                                 -- in the client: the SSL line shows the cipher
```

```bash
ss -tlnp | grep -E ':(3306|33060) '   # classic protocol 3306 and the X Protocol 33060: both loopback, unless remote access is deliberate
```

## Common mistakes

- Creating `'app'@'%'` with a weak password to fix a connection error, then never tightening the host mask.
- `require_secure_transport = ON` skipped because "the network is internal"; internal networks are where lateral movement happens.
- Shipping the client with `--ssl-mode=DISABLED` to silence certificate errors instead of installing the CA ([self-signed.md](self-signed.md)).
- Binding `bind_address` to loopback but leaving `mysqlx_bind_address` at its default `*`, so MySQL 8.4 still answers the X Protocol on 33060 on every interface. Set `mysqlx_bind_address` too, or `mysqlx = OFF` if you do not use it.

## Sources (checked September 2026)

- MySQL encrypted connections: https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html
- MySQL X Plugin options (`mysqlx_bind_address` default `*`, `mysqlx_port` 33060, `mysqlx` enable state, all independent of `bind_address`): https://dev.mysql.com/doc/refman/8.4/en/x-plugin-options-system-variables.html
- MySQL multifactor authentication: https://dev.mysql.com/doc/refman/8.0/en/multifactor-authentication.html
- MariaDB TLS documentation: https://mariadb.com/docs/server/security/encryption/data-in-transit-encryption/secure-connections-overview
- WebAuthn pluggable authentication (MySQL 8.4): https://dev.mysql.com/doc/refman/8.4/en/webauthn-pluggable-authentication.html
- FIDO pluggable authentication (MySQL 8.0, deprecated as of 8.0.35): https://dev.mysql.com/doc/refman/8.0/en/fido-pluggable-authentication.html
- What is new in MySQL 8.4 (`authentication_fido` plugins removed): https://dev.mysql.com/doc/refman/8.4/en/mysql-nutshell.html
