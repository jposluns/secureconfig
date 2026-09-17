# PostgreSQL: TLS and authentication

Default posture: PostgreSQL should not listen on public interfaces at all. Widen `listen_addresses` only for genuine remote clients, and then require both TLS and SCRAM authentication as below.

## 1. Server TLS

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), give the key to the `postgres` user with mode `600`, then in `postgresql.conf`:

```
listen_addresses = 'localhost'            # widen deliberately, e.g. 'localhost,10.0.0.5'
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file  = '/etc/ssl/private/server.key'
ssl_min_protocol_version = 'TLSv1.2'      # PostgreSQL 12 and later
password_encryption = scram-sha-256       # default from PostgreSQL 14; set explicitly on older versions
```

The `ssl*` and `password_encryption` settings apply on reload (`SELECT pg_reload_conf();` or `systemctl reload postgresql`); `listen_addresses` can only be set at server start, so a change to it needs `systemctl restart postgresql`, then `ss -tlnp 'sport = :5432'` to confirm the bind.

## 2. Require TLS per connection in pg_hba.conf

`hostssl` matches only TLS connections; plain `host` lines accept cleartext. Remote entries should all be `hostssl` with `scram-sha-256`:

```
# TYPE     DATABASE  USER  ADDRESS        METHOD
local      all       all                  peer
hostssl    app       app   10.0.0.0/24    scram-sha-256
# No 'host ... 0.0.0.0/0 trust' or 'password' lines. Ever.
```

Reload after editing `pg_hba.conf` (`SELECT pg_reload_conf();` or `systemctl reload postgresql`); the new rules do not take effect until the server re-reads the file. Changing `password_encryption` does not re-hash existing passwords: each keeps the format it had when set, so an MD5 one stays MD5 until you re-set it (`\password app`, in a session using `scram-sha-256`) and a SCRAM one stays SCRAM.

For machine-to-machine links, add certificate verification on top of SCRAM: set `ssl_ca_file` in `postgresql.conf` and append `clientcert=verify-full` to the `hostssl` line (PostgreSQL 12 and later).

MFA: the PostgreSQL wire protocol has no TOTP dialogue. For direct connections `clientcert=verify-full` adds a possession factor held by the connecting machine, stronger than a password alone but not MFA for a person; chain the `radius` authentication method to an MFA service (for example the Duo Authentication Proxy) where policy requires it, and put the human paths to the host (SSH, admin UIs) behind MFA per [mfa.md](mfa.md).

## 3. Client side

Require identity verification in the connection settings, in addition to encryption:

```
psql "host=db.example.com dbname=app user=app sslmode=verify-full sslrootcert=/path/ca.crt gssencmode=disable"
```

`sslmode=require` encrypts but does not verify the server's identity; `verify-full` does both. Add `gssencmode=disable`: in a Kerberos/GSSAPI environment libpq prefers GSS encryption over TLS regardless of `sslmode`, so without it a `verify-full` connection can be satisfied by GSS and skip the certificate check entirely. Application connection strings take the same parameters.

## 4. Verify

```bash
psql -h db.example.com -U app -c "SELECT version();" \
  "dbname=app sslmode=verify-full sslrootcert=/path/ca.crt gssencmode=disable"
# negative control: the SAME host, database and role, with a deliberately wrong password
psql "host=db.example.com dbname=app user=app password=REPLACE_WITH_A_DELIBERATELY_WRONG_PASSWORD sslmode=verify-full sslrootcert=/path/ca.crt gssencmode=disable" -c 'SELECT 1;'
# must be REJECTED with: FATAL:  password authentication failed for user "app"
# if it CONNECTS instead, an earlier pg_hba.conf record (a hostssl ... trust line, say) is letting it
# in without a password: the first matching record wins and there is no fall-through, and neither a
# successful TLS handshake nor pg_stat_ssl can see that
# session diagnostics only, not an enforcement test: which live connections use TLS
sudo -u postgres psql -c "SELECT ssl, count(*) FROM pg_stat_ssl JOIN pg_stat_activity USING (pid) GROUP BY ssl;"
# the app role must carry a SCRAM verifier, not a legacy md5 one (the wrong-password test alone cannot tell them apart)
sudo -u postgres psql -c "SELECT rolname, rolpassword LIKE 'SCRAM-SHA-256%' AS scram FROM pg_authid WHERE rolname='app';"
# storage is not the method: prove the login actually negotiates SCRAM, not a cleartext password over TLS from a `password` HBA line (libpq 16 and later)
psql "host=db.example.com dbname=app user=app sslmode=verify-full sslrootcert=/path/ca.crt gssencmode=disable require_auth=scram-sha-256" -c 'SELECT 1;'
# force plaintext from a remote client: pg_hba.conf must REFUSE it (a "no pg_hba.conf entry ... no encryption" error), not merely time out or fail on the password
psql "host=db.example.com dbname=app user=app sslmode=disable gssencmode=disable connect_timeout=5" -c 'SELECT 1;'
ss -tlnp 'sport = :5432'   # ss's own filter, not a grep: loopback only, unless remote access is deliberate
```

The plaintext probe above must be refused by `pg_hba.conf` once only `hostssl` lines cover remote addresses (a "no pg_hba.conf entry ... no encryption" error), not merely time out or fail on the password. The encryption checks prove encryption, not that a password was demanded, which is why the wrong-password attempt has to fail against the same host, database, and role the valid login used, and `pg_stat_ssl` reports only which live sessions use TLS, not which the server would permit.

## Common mistakes

- `listen_addresses = '*'` plus a permissive `host all all 0.0.0.0/0 md5` line pasted from a tutorial.
- `trust` authentication left enabled for remote addresses.
- The superuser (`postgres`) used as the application account; create a least-privilege role instead ([authentication.md](authentication.md)).

## Sources (checked September 2026)

- Secure TCP/IP connections with SSL: https://www.postgresql.org/docs/current/ssl-tcp.html
- pg_hba.conf: https://www.postgresql.org/docs/current/auth-pg-hba-conf.html
- libpq SSL support (sslmode): https://www.postgresql.org/docs/current/libpq-ssl.html
- libpq connection parameters (GSS encryption is preferred over TLS regardless of `sslmode`; set `gssencmode=disable` to force TLS): https://www.postgresql.org/docs/current/libpq-connect.html
- Password authentication (the stored format follows `password_encryption` at the time the password is set; existing passwords are not re-hashed): https://www.postgresql.org/docs/current/auth-password.html
- Connections and authentication (`listen_addresses` "can only be set at server start"): https://www.postgresql.org/docs/current/runtime-config-connection.html
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
