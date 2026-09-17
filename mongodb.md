# MongoDB: TLS and authorization

MongoDB's history of mass data leaks comes from 2 settings: binding to all interfaces and running with authorization off. Fix both before anything else, then add TLS. Applies to MongoDB 4.2 and later (`tls` options; earlier versions used `ssl` names).

## 1. Enable authorization and create the admin user

In `/etc/mongod.conf`:

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1        # widen deliberately, e.g. 127.0.0.1,10.0.0.5
security:
  authorization: enabled
```

Restart, then use the localhost exception to create the first administrator (connect from the server itself with `mongosh`):

```javascript
use admin
db.createUser({
  user: "admin",
  pwd: passwordPrompt(),
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})
```

Creating that first user ends the localhost exception but does not authenticate the current shell, so authenticate as the administrator before creating anything else: `db.getSiblingDB("admin").auth("admin", passwordPrompt())`. Then create a separate least-privilege user per application (for example `readWrite` on its own database), per [authentication.md](authentication.md). Modern MongoDB authenticates with SCRAM-SHA-256 by default.

MFA: the wire protocol has no TOTP dialogue in Community edition; x.509 client-certificate authentication adds a possession factor held by the connecting machine for direct connections, stronger than a password alone but not MFA for a person, and human paths to the host (SSH, admin UIs) go behind MFA per [mfa.md](mfa.md).

## 2. Enable TLS

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), concatenate certificate and key into one PEM, and require TLS:

```bash
cat server.crt server.key > /etc/ssl/mongodb/server.pem
chown mongodb:mongodb /etc/ssl/mongodb/server.pem   # the mongod service user must own it
chmod 600 /etc/ssl/mongodb/server.pem               # mongodb-owned 600 is readable by mongod and no one else; if mongod cannot read it, fix ownership, do NOT chmod 644 (that exposes the private key)
```

```yaml
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb/server.pem
    # validates any certificate a client or cluster member presents
    CAFile: /etc/ssl/mongodb/ca.crt
    # clients authenticate with SCRAM over TLS; set false when every client holds a certificate
    allowConnectionsWithoutCertificates: true
```

With `CAFile` set, `mongod` expects every client to present a certificate unless `allowConnectionsWithoutCertificates: true`; the setting still validates any certificate a client does present, and it is what lets the SCRAM-only `mongosh` connections below work. `requireTLS` rejects plain connections outright; the transitional modes (`allowTLS`, `preferTLS`) exist for rolling upgrades only.

## 3. Client side

```bash
mongosh "mongodb://admin@db.example.com:27017/?authSource=admin&tls=true" \
  --tlsCAFile /path/ca.crt
```

Enable TLS in your driver and point it at the CA. Many drivers accept `tls=true` and `tlsCAFile` in the connection string, but `tlsCAFile` is not supported by every driver, so some need their own driver-specific TLS/CA option; keep certificate and hostname validation on. Do not ship `tlsAllowInvalidCertificates`; install the CA instead ([self-signed.md](self-signed.md)).

## 4. Verify

```bash
ss -tlnp   # read every listener; 27017: loopback only, unless remote access is deliberate
# substitute your real host for db.example.com below; probing the unchanged placeholder proves nothing
mongosh --host db.example.com --eval 'db.runCommand({ping:1})'                                                       # plaintext: with requireTLS it must NOT connect. The signal that matters is a SUCCESSFUL plaintext connect (TLS not enforced); a bare refusal also happens when the host is unreachable, so a refusal alone is not proof
mongosh "mongodb://db.example.com/?tls=true" --tlsCAFile ca.crt --eval 'db.adminCommand({listDatabases:1})'          # TLS reachable but UNauthenticated: must fail with an authorization error
mongosh "mongodb://admin@db.example.com/?authSource=admin&tls=true" --tlsCAFile ca.crt --eval 'db.adminCommand({listDatabases:1})'   # positive control: authenticated over TLS must SUCCEED and list databases
```

The unauthenticated `listDatabases` must fail with a MongoDB authorization error while the authenticated one succeeds and lists databases; a timeout, a closed shell, or empty output is not that authorization error and does not count as a pass.

## Common mistakes

- `bindIp: 0.0.0.0` set to fix a connection problem, with `authorization` still unset; this is the classic leaked-database configuration.
- Authorization enabled but every service sharing the `admin` account.
- TLS on the server while the connection string still says `tls=false` because a container healthcheck was easier that way.

## Sources (checked September 2026)

- MongoDB security checklist: https://www.mongodb.com/docs/manual/administration/security-checklist/
- Configure TLS/SSL for mongod: https://www.mongodb.com/docs/manual/tutorial/configure-ssl/
- Enable access control: https://www.mongodb.com/docs/manual/tutorial/enable-authentication/
- Configuration file options (`net.tls.CAFile`, `net.tls.allowConnectionsWithoutCertificates`): https://www.mongodb.com/docs/manual/reference/configuration-options/
