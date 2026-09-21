# MongoDB: TLS and authorization

MongoDB's history of mass data leaks comes from 2 settings: binding to all interfaces and running with authorization off. Fix both before anything else, then add TLS. Use a supported MongoDB release and its current security patches. MongoDB 4.2 reached end of life on April 30, 2023; it is not a deployment recommendation. Compatibility note: these examples use `tls` options; older configurations used `ssl` names. Check the [vendor lifecycle schedule](https://www.mongodb.com/legal/support-policy/lifecycles) before deploying.

This guide covers self-managed Community and Enterprise deployments. Tier labels below describe deployment priorities, not MongoDB subscription tiers.

## 1. Enable authorization and create the admin user

In `/etc/mongod.conf`, merge these settings into the existing mappings:

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1        # widen deliberately, e.g. 127.0.0.1,10.0.0.5
security:
  authorization: enabled
```

Restart the package-managed service, then use the localhost exception to create the first administrator. Connect from the server itself with `mongosh`, keeping the listener on loopback until TLS is active. The exception applies to an installation without existing users or roles; it is not an administrative recovery mechanism. See [enable access control](https://www.mongodb.com/docs/manual/tutorial/enable-authentication/).

```javascript
db.getSiblingDB("admin").createUser({
  user: "admin",
  pwd: passwordPrompt(),
  mechanisms: ["SCRAM-SHA-256"],
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
});
```

Creating that first user ends the localhost exception but does not authenticate the current shell. Authenticate before creating anything else: `db.getSiblingDB("admin").auth("admin", passwordPrompt())`.

Complete section 2 before running the application-user commands below. Reconnect as the administrator over TLS, using section 3's SCRAM connection form with username `admin` and authentication database `admin`. While binding remains local, use a certificate hostname that resolves to loopback on the server. `passwordPrompt()` keeps the password out of the command text but does not encrypt the data sent by `createUser()`; TLS protects that transport. See [user creation and its transport warning](https://www.mongodb.com/docs/manual/reference/method/db.createuser/).

### Collection-scoped application roles

Tier 1. Community and Enterprise.

A compromised application can read or modify unrelated data when its account has broader privileges than its workload requires.

Create a separate identity per application, per [authentication.md](authentication.md). The database containing a user is its authentication database; its assigned roles determine access. Use `read` for database-wide readers. Use `readWrite` only when its collection and index management permissions are appropriate. The [vendor's role capability table](https://www.mongodb.com/docs/compass/connect/required-access/) documents those broader permissions.

For narrower access, run this in an authenticated administrative `mongosh` session over TLS:

```javascript
db.getSiblingDB("REPLACE_WITH_APP_DB").createRole({
  role: "REPLACE_WITH_APP_ROLE",
  privileges: [{
    resource: {
      db: "REPLACE_WITH_APP_DB",
      collection: "REPLACE_WITH_COLLECTION"
    },
    actions: ["find", "insert", "update"]
  }],
  roles: []
});

db.getSiblingDB("REPLACE_WITH_APP_DB").createUser({
  user: "REPLACE_WITH_APP_USER",
  pwd: passwordPrompt(),
  mechanisms: ["SCRAM-SHA-256"],
  roles: [{
    role: "REPLACE_WITH_APP_ROLE",
    db: "REPLACE_WITH_APP_DB"
  }]
});
```

This role grants no document deletion, collection dropping, or index management. It does permit creating the named non-capped collection: MongoDB accepts `insert` privilege on that collection for this operation. Provision collections and indexes through a separate deployment identity, and add privileges only for operations the application needs. See [privilege actions](https://www.mongodb.com/docs/manual/reference/privilege-actions/) and [collection creation privileges](https://www.mongodb.com/docs/manual/reference/command/create/).

Both `privileges` and `roles` are required in `createRole()`. A role outside `admin` can grant privileges only within its own database and inherit only roles from that database. See [createRole](https://www.mongodb.com/docs/manual/reference/method/db.createrole/).

At the time of writing, omitting a user's `mechanisms` normally creates both SCRAM-SHA-1 and SCRAM-SHA-256 credentials. Omitting the connection's `authMechanism` permits negotiation to fall back from SCRAM-SHA-256 to SCRAM-SHA-1. The explicit user and client settings here restrict this application to SCRAM-SHA-256; confirm driver compatibility before restricting existing users. See [credential creation](https://www.mongodb.com/docs/manual/reference/method/db.createuser/) and [connection negotiation](https://www.mongodb.com/docs/manual/reference/connection-string-options/).

### Restrict application authentication sources

Tier 1 where remote connections are required. Community and Enterprise.

A stolen credential remains usable from any reachable source unless authentication also checks the connection's origin.

After creating the application user, apply source restrictions from the administrative TLS session. Substitute the application's actual source network and every database listener address through which it must authenticate:

```javascript
db.getSiblingDB("REPLACE_WITH_APP_DB").updateUser(
  "REPLACE_WITH_APP_USER",
  {
    authenticationRestrictions: [{
      clientSource: ["10.20.10.0/24"],
      serverAddress: ["10.20.0.11", "10.20.0.12", "10.20.0.13"]
    }]
  }
);
```

`clientSource` matches the client address MongoDB sees. `serverAddress` matches the local address that accepted the connection. Account for proxies, NAT, routers, failover, and alternate paths. These restrictions govern authentication; they do not prevent TCP connections from reaching the listener.

Keep an administrative recovery path while changing restrictions. Incompatible restrictions inherited through multiple roles can prevent a user from authenticating. See [updateUser authentication restrictions](https://www.mongodb.com/docs/manual/reference/method/db.updateuser/).

MFA: the wire protocol has no TOTP dialogue in Community edition; x.509 client-certificate authentication adds a possession factor held by the connecting machine for direct connections, stronger than a password alone but not MFA for a person. Put human paths to the host, including SSH and admin UIs, behind MFA per [mfa.md](mfa.md). Community supports [SCRAM and x.509 authentication](https://www.mongodb.com/docs/manual/administration/security-checklist/).

## 2. Enable TLS

Get a certificate using [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md). Its SAN must cover the hostname clients use.

For initial installation, run the following as root with an unused destination in an existing, protected directory. Substitute the operating system account and group running `mongod`:

```bash
(
  set -eC
  umask 077
  cat server.crt server.key > /etc/ssl/mongodb/server.pem
  chown REPLACE_WITH_MONGOD_OS_USER:REPLACE_WITH_MONGOD_OS_GROUP /etc/ssl/mongodb/server.pem
  chmod 600 /etc/ssl/mongodb/server.pem
)
```

The creation mask applies before the private key is written. `set -C` refuses to overwrite an existing regular file. This is an initial-install block, not a certificate-rotation procedure. If the service cannot read the PEM, fix ownership and directory access; do not make the private key world-readable. See the Bash documentation for [umask](https://www.gnu.org/s/bash/manual/html_node/Bourne-Shell-Builtins.html) and [redirection](https://www.gnu.org/s/bash/manual/bash.html).

Merge `tls` into the existing `net` mapping, preserving `port`, private binding, and other settings. Do not append a second top-level `net` key:

```yaml
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb/server.pem
    CAFile: /etc/ssl/mongodb/ca.crt
    # SCRAM-only clients work; see section 3 before requiring certificates.
    allowConnectionsWithoutCertificates: true
```

With this CA configuration, clients must present certificates unless `allowConnectionsWithoutCertificates` is `true`. Any certificate presented is still validated. This allows SCRAM-only clients while encrypting their connections. See [TLS certificate validation](https://www.mongodb.com/docs/manual/tutorial/configure-ssl/).

`allowTLS` and `preferTLS` accept both plaintext and TLS connections. Use mixed modes only during a controlled transition; finish with `requireTLS`. See [TLS modes](https://www.mongodb.com/docs/manual/reference/configuration-options/#net.tls.mode).

Restart the package-managed service after changing its configuration, confirm that startup succeeded, and reconnect over TLS before testing or creating application credentials. Widen binding only deliberately, to required private interfaces, with firewall rules limiting access. Configuration-file changes must be applied to the service actually running MongoDB; see [configuration-file startup](https://www.mongodb.com/docs/manual/reference/configuration-options/).

### Authenticate replica-set and sharded-cluster members

Tier 1 for distributed deployments. Community and Enterprise. Skip this subsection for a standalone server.

Application authentication alone does not establish which processes may act as cluster members. Configure internal authentication on every replica-set member and every participating `mongod` and `mongos`, including config servers and routers. Membership credentials do not replace TLS.

MongoDB recommends x.509 membership authentication for production. Merge these settings into the existing `security` and `net.tls` mappings:

```yaml
security:
  clusterAuthMode: x509
  transitionToAuth: false
net:
  tls:
    clusterFile: /etc/ssl/mongodb/member.pem
```

Retain `requireTLS`, `certificateKeyFile`, and `CAFile`. `clusterFile` contains this member's certificate and private key for outgoing internal authentication. Keep its key readable only by the service account.

Under the default membership rules, member certificates need matching `O`, `OU`, and `DC` attributes, with at least one populated, a common issuing CA, and SANs matching the hostnames peers use. If EKU is present, the server certificate needs `serverAuth` and the separate membership certificate needs `clientAuth`. If one certificate serves both purposes, its EKU must include both. Application certificates must use a different membership attribute combination. See [internal authentication](https://www.mongodb.com/docs/manual/core/security-internal-authentication/) and [x.509 membership configuration](https://www.mongodb.com/docs/manual/tutorial/configure-x509-member-authentication/).

Where keyfile authentication is used, generate the shared key once. Run this as root with an unused destination:

```bash
(
  set -eC
  umask 077
  openssl rand -base64 756 > /etc/mongodb-keyfile
  chown REPLACE_WITH_MONGOD_OS_USER:REPLACE_WITH_MONGOD_OS_GROUP /etc/mongodb-keyfile
  chmod 400 /etc/mongodb-keyfile
)
```

Distribute that same file securely to every member and router, setting ownership for each service account. Do not generate independent keys on different members.

Use this configuration instead of the x.509 membership fragment, merging it into the existing `security` mapping:

```yaml
security:
  keyFile: /etc/mongodb-keyfile
  clusterAuthMode: keyFile
  transitionToAuth: false
```

Retain TLS. Unix keyfiles must have no group or world permissions and must be readable by the service account. Keyfiles can contain multiple keys for rotation, but all members must share a common key. See [keyfile requirements and setup](https://www.mongodb.com/docs/manual/tutorial/enforce-keyfile-access-control-in-existing-replica-set/).

These are final configurations, not rolling migration procedures. Follow the vendor's transition procedure for an existing cluster. `transitionToAuth: true` permits unauthenticated operations and does not enforce user access controls. Keep it `false` in the final state. See [transitionToAuth](https://www.mongodb.com/docs/manual/reference/configuration-options/#security.transitionToAuth).

Keep `security.authorization: enabled` on `mongod`. That particular setting is not available on `mongos`; internal authentication enables client access control there. See the [mongod](https://www.mongodb.com/docs/manual/reference/program/mongod/) and [mongos](https://www.mongodb.com/docs/manual/reference/program/mongos/) references.

### Restrict member authentication sources

Tier 1 where remote connections are required. Community and Enterprise.

For this example's three-member cluster, merge the following into `security` on the participating processes:

```yaml
security:
  clusterIpSourceAllowlist:
    - 10.20.0.11/32
    - 10.20.0.12/32
    - 10.20.0.13/32
```

Substitute actual source addresses and include every required member and router, including addresses seen after NAT. The setting was introduced in MongoDB 5.0 and has no effect without authentication. It restricts internal authentication, not application accounts or TCP reachability. See [clusterIpSourceAllowlist](https://www.mongodb.com/docs/manual/reference/configuration-options/#security.clusterIpSourceAllowlist).

## 3. Client side

Connect as the application identity, using the database in which that user was created:

```bash
mongosh --host db.example.com --port 27017 --tls \
  --tlsCAFile /path/ca.crt \
  --username REPLACE_WITH_APP_USER \
  --authenticationDatabase REPLACE_WITH_APP_DB \
  --authenticationMechanism SCRAM-SHA-256 --password
```

The final `--password` prompts without putting the password in argv. See [mongosh authentication options](https://www.mongodb.com/docs/mongodb-shell/reference/options/).

Enable TLS in your driver and configure its CA trust. Many drivers accept `tls=true` and `tlsCAFile` in the connection string, but `tlsCAFile` is not supported by every driver; some require their own TLS/CA option. Keep certificate and hostname validation enabled. Do not ship `tlsAllowInvalidCertificates`; install the CA instead, per [self-signed.md](self-signed.md). See [connection-string TLS options](https://www.mongodb.com/docs/manual/reference/connection-string-options/).

### Alternative: authenticate the application with x.509

Tier 1 for deployments adopting certificate authentication; otherwise Tier 2. Community and Enterprise.

Requiring a trusted certificate without defining its database identity and privileges can leave authentication incomplete or accidentally confer cluster-member privileges.

TLS certificate validation and MongoDB x.509 authentication are separate steps. Register the certificate subject in `$external`, then authenticate with `MONGODB-X509`.

Obtain the RFC2253 subject:

```bash
openssl x509 -in /path/client.pem -inform PEM -subject -nameopt RFC2253
```

Copy only the subject value, excluding the `subject=` prefix and the certificate output. Run this as the user administrator over TLS:

```javascript
db.getSiblingDB("$external").createUser({
  user: "REPLACE_WITH_EXACT_RFC2253_SUBJECT",
  roles: [{
    role: "REPLACE_WITH_APP_ROLE",
    db: "REPLACE_WITH_APP_DB"
  }]
});
```

Connect using that certificate and its private key:

```bash
mongosh --host db.example.com --port 27017 --tls \
  --tlsCAFile /path/ca.crt \
  --tlsCertificateKeyFile /path/client.pem \
  --authenticationDatabase "\$external" \
  --authenticationMechanism MONGODB-X509
```

The escaped dollar sign passes the literal database name `$external`. Without an explicit username, `mongosh` uses the certificate subject. See the [client x.509 procedure](https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/).

Client certificates must be current, meet the documented CA requirements, and contain `digitalSignature` key usage and `clientAuth` EKU. Keep their subjects and membership attributes separate from both server and member certificates. Matching the cluster's membership identity can confer internal privileges. See [client certificate requirements and membership separation](https://www.mongodb.com/docs/manual/core/security-x.509/).

For remote application access, also apply section 1's source restrictions to this `$external` user: use `$external` as the database and the exact RFC2253 subject as the username in `updateUser()`. Restrictions on the SCRAM identity do not transfer automatically to this separate identity.

Once all connecting tools have suitable certificates, merge this change into the existing `net.tls` mapping and restart the service:

```yaml
net:
  tls:
    allowConnectionsWithoutCertificates: false
```

Keep authorization enabled. This switch requires a certificate during TLS establishment; it does not select `MONGODB-X509` or assign database roles. SCRAM clients must also present a valid client certificate after this change.

At the time of writing, MongoDB's TLS documentation requires `allowConnectionsWithoutCertificates: true` for `mongot`. Check that topology before enforcing the certificate requirement. See [TLS certificate validation behavior](https://www.mongodb.com/docs/manual/tutorial/configure-ssl/).

Keep certificate issuance and human MFA guidance in [free-certificates.md](free-certificates.md), [self-signed.md](self-signed.md), and [mfa.md](mfa.md).

## 4. Verify

This guide's service behavior is **REASONED, not demonstrated**. The authoring environment has no `mongod`, `mongosh`, Docker, or Podman, and no available authorized deployment for exposed-versus-fixed tests. The outstanding demonstrations are recorded in `MONGODB-LIVE-1` below.

Local checks did run: Bash parsing, ShellCheck, JavaScript syntax parsing, duplicate-key YAML parsing, and merges for both membership alternatives. Shell-only argument tracing checked probe dispatch; it did not simulate or verify MongoDB behavior. Placeholder tests rejected unchanged tokens, embedded `REPLACE_WITH_` values, angle brackets, empty values, example hosts, shortened assignments, an omitted assignment with ordinary inherited arguments, and a wrong argument count under a modified `IFS`. The JavaScript probe guards also rejected unchanged placeholders before database access.

### Listener exposure

**REASONED:** no MongoDB service is available. The local command was attempted, but the sandbox refused its netlink socket with `Operation not permitted`; that output establishes nothing about listeners.

Run on every database and router host:

```bash
ss -tlnp
```

Read every relevant listener. The exposed state includes an unintended wildcard or public listener. The fixed state listens only on loopback or deliberately selected private addresses. Check the actual configured ports, including any non-default ports, and inspect firewall rules separately. A private listener alone does not prove remote firewall behavior. See [network hardening](https://www.mongodb.com/docs/manual/administration/security-checklist/).

### Guarded connection probes

Use the whole Bash block below. Substitute inside the single quotes on its `set --` lines. Supply all six values even when a mode does not use every value. Use the real hostname covered by the server certificate and a valid application client PEM, never a cluster-member PEM.

The modes are `plaintext`, `tls`, `scram`, `x509`, and `missing-certificate`. `tls` presents a client certificate but omits MongoDB authentication. `--norc` prevents a local startup script from authenticating the shell unexpectedly.

The guard assumes normal Bash builtins. A literal apostrophe requires proper shell escaping rather than direct substitution inside the quotes. Paste the whole block: a fragment starting after its guards cannot be protected, and inherited arguments containing the exact marker and count are indistinguishable from the intended assignment.

**REASONED for every connection mode:** no `mongod`, `mongosh`, Docker, or Podman is available. Expected exposed and fixed outcomes follow each probe below. The options are documented in the [mongosh reference](https://www.mongodb.com/docs/mongodb-shell/reference/options/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'scram' 'REPLACE_WITH_DB_HOST' \
    'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_CLIENT_PEM' \
    'REPLACE_WITH_APP_USER' 'REPLACE_WITH_APP_DB'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || {
    echo "paste the whole block, including set --; not probing"; exit 1;
  }
  shift
  [ "$#" -eq 6 ] || {
    echo "the set -- line needs exactly 6 values; not probing"; exit 1;
  }
  check_values() {
    while [ "$#" -gt 0 ]; do
      case "$1" in
        ""|*REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|*example.net*|*example.org*|*203.0.113.*)
          echo "substitute all placeholders inside the quotes; not probing"; return 1 ;;
      esac
      shift
    done
  }
  check_values "$@" || exit 1

  case "$1" in
    plaintext)
      mongosh --norc --host "$2" --port 27017 \
        --eval 'db.runCommand({ping: 1})' ;;
    tls)
      mongosh --norc --host "$2" --port 27017 --tls \
        --tlsCAFile "$3" --tlsCertificateKeyFile "$4" ;;
    scram)
      mongosh --norc --host "$2" --port 27017 --tls \
        --tlsCAFile "$3" --tlsCertificateKeyFile "$4" \
        --username "$5" --authenticationDatabase "$6" \
        --authenticationMechanism SCRAM-SHA-256 --password ;;
    x509)
      mongosh --norc --host "$2" --port 27017 --tls \
        --tlsCAFile "$3" --tlsCertificateKeyFile "$4" \
        --authenticationDatabase "\$external" \
        --authenticationMechanism MONGODB-X509 ;;
    missing-certificate)
      mongosh --norc --host "$2" --port 27017 --tls \
        --tlsCAFile "$3" --eval 'db.runCommand({ping: 1})' ;;
    *) echo "unknown mode; not probing"; exit 1 ;;
  esac
)
```

### Plaintext versus TLS

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman is available.

Run `scram` mode from a permitted application source as the TLS positive control, then repeat the whole block with mode `plaintext` against the same endpoint.

With plaintext accepted, the plaintext `ping` succeeds. With `requireTLS`, it must not complete over plaintext while the TLS control succeeds. A refusal or timeout alone is inconclusive; inspect the failure and server evidence to distinguish TLS rejection from an unreachable host. `ping` tests connectivity, not authorization. See [TLS modes](https://www.mongodb.com/docs/manual/reference/configuration-options/#net.tls.mode) and [ping](https://www.mongodb.com/docs/manual/reference/command/ping/).

### Unauthenticated collection access

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman is available.

Open a fresh session using `tls` mode, then substitute and run:

```javascript
(() => {
  const appDB = "REPLACE_WITH_APP_DB";
  const collection = "REPLACE_WITH_COLLECTION";
  if ([appDB, collection].some(v => !v || /REPLACE_WITH_|[<>]/.test(v))) {
    throw new Error("Substitute database and collection; not probing");
  }
  const status = db.runCommand({connectionStatus: 1});
  if (status.ok !== 1 || status.authInfo.authenticatedUsers.length !== 0) {
    throw new Error("Use a fresh TLS session without MongoDB authentication");
  }
  printjson(db.getSiblingDB(appDB).runCommand({
    find: collection, filter: {}, limit: 1, singleBatch: true
  }));
})();
```

Use an existing application collection. With authorization disabled, the read succeeds. With authorization enabled, it must fail with `Unauthorized`, code `13`. Pair this with the authenticated collection read below.

Once certificates are mandatory, this probe must still present a valid application client certificate while omitting MongoDB authentication. Otherwise it only tests the TLS certificate requirement. `connectionStatus` confirms that the session has no authenticated MongoDB identity. See [connectionStatus](https://www.mongodb.com/docs/manual/reference/command/connectionstatus/), [find privileges](https://www.mongodb.com/docs/manual/reference/privilege-actions/), and [error codes](https://www.mongodb.com/docs/manual/reference/error-codes/).

Do not substitute `listDatabases` as proof of collection access. Its results depend on privileges and `authorizedDatabases`. A timeout, closed shell, empty output, or unrelated error is not an authorization denial. See [listDatabases behavior](https://www.mongodb.com/docs/manual/reference/command/listdatabases/).

### Application role: allow its collection, deny unrelated access and deletion

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman is available.

Use a disposable test deployment with two existing ordinary collections and the application's actual role configuration. The probe document must satisfy the collection's validation rules. Choose a fresh probe ID for each run. Use `scram` mode as the application identity, then run:

```javascript
(() => {
  const appDB = "REPLACE_WITH_APP_DB";
  const own = "REPLACE_WITH_COLLECTION";
  const other = "REPLACE_WITH_OTHER_COLLECTION";
  const probeId = "REPLACE_WITH_UNIQUE_PROBE_ID";
  if ([appDB, own, other, probeId].some(v => !v || /REPLACE_WITH_|[<>]/.test(v))) {
    throw new Error("Substitute all probe values; not probing");
  }
  if (own === other) throw new Error("Use two different collections");
  const target = db.getSiblingDB(appDB);
  function allow(command) {
    const result = target.runCommand(command);
    if (result.ok !== 1 || result.writeErrors?.length || result.writeConcernError) {
      printjson(result);
      throw new Error("Expected successful operation");
    }
    return result;
  }
  function deny(command) {
    let result;
    try {
      result = target.runCommand(command);
    } catch (error) {
      if (error.code === 13) {
        print("DENY: Unauthorized (13)");
        return;
      }
      throw error;
    }
    if (result.ok !== 0 || result.code !== 13) {
      printjson(result);
      throw new Error("Expected Unauthorized (13)");
    }
    print("DENY: Unauthorized (13)");
  }

  const inserted = allow({
    insert: own, documents: [{_id: probeId, secureconfigProbe: 1}]
  });
  if (inserted.n !== 1) throw new Error("Expected one inserted document");
  const updated = allow({
    update: own,
    updates: [{
      q: {_id: probeId},
      u: {$set: {secureconfigProbe: 2}},
      multi: false,
      upsert: false
    }]
  });
  if (updated.n !== 1) throw new Error("Expected one matched document");
  const read = allow({
    find: own, filter: {_id: probeId}, limit: 1, singleBatch: true
  });
  if (read.cursor.firstBatch.length !== 1 ||
      read.cursor.firstBatch[0].secureconfigProbe !== 2) {
    throw new Error("Expected to read the updated probe document");
  }
  print("ALLOW: insert, update, find on own collection");

  deny({find: other, filter: {}, limit: 1, singleBatch: true});
  deny({insert: other, documents: [{_id: probeId, secureconfigProbe: 1}]});
  deny({delete: own, deletes: [{q: {_id: probeId}, limit: 1}]});
})();
```

The fixed role must allow insertion, update, and reading of the probe document, then deny the other collection's read and insert and deny deletion from its own collection.

In the exposed comparison, database-wide `readWrite` allows those operations and the denial checks must fail. The script stops at its first unexpected result; demonstrate each denial separately against that exposed state. Have the deployment identity clean up probe documents afterward, including any written to the other collection during an exposed-state test.

The command shapes and results are documented under [find](https://www.mongodb.com/docs/manual/reference/command/find/), [insert](https://www.mongodb.com/docs/manual/reference/command/insert/), [update](https://www.mongodb.com/docs/manual/reference/command/update/), and [delete](https://www.mongodb.com/docs/manual/reference/command/delete/). The required actions are documented under [privilege actions](https://www.mongodb.com/docs/manual/reference/privilege-actions/).

### Authentication-source restrictions

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman, or separate permitted and excluded source hosts, is available.

Run the guarded `scram` connection with the same valid credentials from a permitted source and an excluded source. First establish TLS reachability from each using `tls` mode and the valid client certificate.

Without the user restriction, authentication from both sources succeeds. With the restriction applied, the permitted source authenticates and can read its collection; the excluded source must receive a MongoDB authentication failure. A TLS error or timeout does not demonstrate the restriction.

In the permitted session, inspect:

```javascript
db.runCommand({connectionStatus: 1});
```

Confirm the expected application user and authentication database, then run the collection checks. Test `serverAddress` on its own: hold the permitted source, valid credentials, and client certificate constant, and connect through both an allowed listener address and a reachable listener address you will exclude. Before `serverAddress` is applied, authentication must succeed through both, which proves the excluded listener is reachable. After applying `serverAddress`, authentication must fail through the excluded listener and continue to succeed through the allowed one; MongoDB matches `serverAddress` against the address that accepted the connection. Repeating the probes through permitted listeners only would pass with `serverAddress` omitted, so it does not demonstrate the restriction, and a TLS error or timeout against the excluded listener does not either. See [source and listener address matching](https://www.mongodb.com/docs/manual/reference/method/db.updateuser/#authentication-restrictions) and [authenticated identity reporting](https://www.mongodb.com/docs/manual/reference/command/connectionstatus/).

### x.509 identity and certificate requirement

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman, or deployment-issued client certificates, is available.

Use the guarded connection block for these cases:

- `x509` with a valid registered client certificate: authentication must succeed. Run `connectionStatus` and confirm the exact subject in `$external`, then repeat the collection-role checks.
- `x509` with a valid, trusted application certificate whose subject is not registered: TLS must be acceptable, but MongoDB authentication must fail. Use a different subject with no cluster-membership attributes. Pair it with the registered-certificate success; an expired or untrusted certificate only tests TLS validation.
- `missing-certificate`: with `allowConnectionsWithoutCertificates: true`, the TLS `ping` can succeed without MongoDB authentication. With the setting `false`, the server must reject the certificate-less TLS connection while the registered-certificate control succeeds.

For the identity demonstration, the same trusted certificate fails x.509 authentication before its subject is registered and succeeds afterward with only the assigned role. Missing-certificate rejection after enforcement demonstrates the TLS requirement separately. Repeat the unauthenticated collection probe with a valid certificate to demonstrate authorization as well.

See [x.509 user registration](https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/) and [certificate validation behavior](https://www.mongodb.com/docs/manual/tutorial/configure-ssl/).

### Distributed membership

**REASONED:** no `mongod`, `mongosh`, Docker, or Podman, or multi-host cluster, is available.

In an isolated replica-set test, compare a configured member with valid membership credentials against that member using wrong credentials, and compare permitted versus excluded member source addresses. Keep the application-facing TLS configuration constant.

From a separate operator session with the `replSetGetStatus` privilege, inspect:

```javascript
db.adminCommand({replSetGetStatus: 1});
```

The fixed configuration must permit valid members and reject invalid membership authentication or excluded sources. Correlate member health with explicit authentication failures in the participating processes' diagnostic output; an unhealthy member alone could reflect a network failure. Compare with an isolated exposed deployment lacking membership authentication and, separately, one lacking the source restriction. Include router-to-shard and config-server paths when demonstrating a sharded deployment.

See [internal membership authentication](https://www.mongodb.com/docs/manual/core/security-internal-authentication/), [member source restrictions](https://www.mongodb.com/docs/manual/reference/configuration-options/#security.clusterIpSourceAllowlist), and [replica-set status](https://www.mongodb.com/docs/manual/reference/command/replsetgetstatus/).

### Verify Enterprise auditing

**REASONED:** no MongoDB Enterprise deployment or readable audit destination is available.

In an isolated Enterprise fixture with the auditing configuration from section 5, perform a successful authentication, a failed authentication, a collection creation, and a permitted collection read, then inspect the audit destination. Confirm the successful-authorization-check setting first:

```javascript
db.adminCommand({getParameter: 1, auditAuthorizationSuccess: 1});
```

With no destination configured, no audit records are produced. With the destination configured, authentication and authorization failures are recorded, while successful authorization checks (the `authCheck` action) appear only once `auditAuthorizationSuccess` is `true`, and an authentication-only filter records nothing else. The presence of an audit file alone proves neither event coverage nor successful-operation auditing; correlate each record with the test identity, operation, and time. See [auditing](https://www.mongodb.com/docs/v8.0/core/auditing/) and [the auditAuthorizationSuccess parameter](https://www.mongodb.com/docs/v8.0/reference/parameters/).

### Verify diagnostic-log redaction

**REASONED:** no MongoDB Enterprise binaries, running test server, or process-log access is available.

Set the log verbosity to 1 in both fixtures so the operation is logged regardless of latency, insert a harmless canary, read the corresponding entry in the process log, then restore the previous verbosity:

```javascript
db.setLogLevel(1);
db.clients.insertOne({name: "Probe", note: "SECURECONFIG_REDACTION_CANARY"});
```

Without redaction, the canary value appears in the matching log entry. With `security.redactClientLogData` enabled, the entry still exists but its attached values are shown as `###`, while metadata such as error and operation codes and line numbers remains visible. A missing log entry is inconclusive on its own. See [the redactClientLogData parameter](https://www.mongodb.com/docs/v8.0/reference/parameters/) and the [log-redaction example](https://www.mongodb.com/docs/v8.0/administration/monitoring/).

### Verify storage encryption

**REASONED:** no MongoDB Enterprise binaries, disposable data directory, or KMIP endpoint is available.

Create equivalent unencrypted and encrypted fixtures, each holding a known document, then confirm on disposable copies that the encrypted data files require the key configuration while a correctly configured server reads them. Inspect the startup log for the key-manager initialization:

```bash
grep -iE 'encryption.*key|key manager' /var/log/mongodb/mongod.log
```

With encryption enabled, the log records that the encryption key manager initialized; with a mismatched KMIP server identity or a missing key, initialization fails and the server does not start. The unencrypted fixture reopens with no key. Do not treat the absence of plaintext under `strings` as proof of encryption, since compression alone can produce that result. See the [encryption-at-rest reference](https://www.mongodb.com/docs/v8.0/core/security-encryption-at-rest/) and the [configure-encryption procedure](https://www.mongodb.com/docs/v8.0/tutorial/configure-encryption/).

### Verify field-level encryption (CSFLE)

**REASONED:** no MongoDB deployment, encryption-capable driver, or provisioned data-encryption key is available.

CSFLE is verified with distinct client handles, not a single shell session, because a client configured for automatic encryption also decrypts on read. Through an encryption-configured client, insert a known canary into a protected collection and retain the returned `_id`; on the Community explicit path, encrypt the field value with `ClientEncryption.encrypt()` before the write. Read that document by `_id` through a client configured without automatic decryption: against an ordinary collection the field is plaintext, while against the protected collection it is encrypted binary data, and a key-authorized client recovers the original value. A plaintext write attempted against a server-side `$jsonSchema` that requires encryption is rejected. A denied read alone does not demonstrate field encryption, and a read through the same automatic-encryption client silently decrypts the field, so it cannot serve as the exposed control. See [CSFLE](https://www.mongodb.com/docs/v8.0/core/csfle/), its [manual-encryption reference](https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/manual-encryption/), and [CSFLE client options](https://www.mongodb.com/docs/v8.0/core/csfle/reference/csfle-options-clients/).

### Verify Queryable Encryption

**REASONED:** no replica-set or sharded MongoDB deployment, encryption-capable driver, or provisioned key is available.

Create a Queryable Encryption collection with an `encryptedFields` definition and compare it against an ordinary collection, using distinct client handles as for CSFLE. Through the configured client, insert a canary and retain its `_id`; on the Community explicit path, encrypt values explicitly. Read by `_id` through a client configured without decryption: the ordinary collection returns plaintext, the encrypted collection ciphertext, and the configured client recovers the value. The configured client still matches a supported encrypted equality query on a string field. A range query is a separate fixture: it requires the encrypted field to be a numeric or date type (`int`, `long`, `double`, `decimal`, or `date`), not a string, with documents inside and outside the tested interval. A plaintext write against the declared encrypted fields is rejected. Missing results or a connection error alone do not establish confidentiality. See [Queryable Encryption](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/), its [limitations](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/limitations/), the [manual-encryption reference](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/fundamentals/manual-encryption/), and [supported operations](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/supported-operations/).

| Backlog ID | Status | Outstanding demonstration |
| --- | --- | --- |
| MONGODB-LIVE-1 | Open; service behavior not yet demonstrated | On an authorized isolated deployment with MongoDB binaries, certificates, listener-inspection permission, and permitted/excluded source hosts, demonstrate exposed versus fixed listener binding, plaintext/TLS behavior, unauthenticated collection access with a valid client certificate, collection-role allows and denials, user source/listener restrictions, registered/unregistered/missing client-certificate cases, membership credentials, and member/router source restrictions. Record commands, versions, responses, and positive controls. The sections 5 to 9 controls are also REASONED: on an authorized MongoDB Enterprise deployment with an audit destination, encryption keys or a KMIP endpoint, and an encryption-capable driver, additionally demonstrate audit records for authentication and authorization events with auditAuthorizationSuccess off and on, diagnostic-log redaction of a canary value, encrypted versus plaintext storage fixtures under local-key and KMIP configurations, and CSFLE and Queryable Encryption field ciphertext with a permitted encrypted query and a rejected plaintext write. |

## 5. Enable Enterprise auditing with deliberate event coverage

MongoDB Enterprise provides an auditing facility for `mongod` and `mongos`; MongoDB Community has no equivalent, and the diagnostic log is not a substitute. Without a configured destination, no audit records are produced. Configure a destination on every process, including each shard and config-server member, since one unaudited process leaves a gap. See [MongoDB 8.0 auditing](https://www.mongodb.com/docs/v8.0/core/auditing/).

```yaml
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
```

A failed audit write can terminate the process, so confirm the destination is writable during deployment validation. Omitting a filter records every auditable event; a filter such as `auditLog.filter: '{"atype": "authenticate"}'` records only that event type and deliberately excludes the rest. See [configure auditing](https://www.mongodb.com/docs/v8.0/tutorial/configure-auditing/) and [audit filters](https://www.mongodb.com/docs/v8.0/tutorial/configure-audit-filters/).

Recording successful authorization checks is a separate decision. `auditAuthorizationSuccess` defaults to `false`, so the audit system logs only authorization failures until it is enabled, and enabling it carries a performance cost:

```yaml
setParameter:
  auditAuthorizationSuccess: true
```

Set it only where the accountability requirement justifies the overhead. See the [auditAuthorizationSuccess parameter](https://www.mongodb.com/docs/v8.0/reference/parameters/).

## 6. Redact document values from the diagnostic log

`redactClientLogData` is a MongoDB Enterprise feature; MongoDB Community does not offer it. Without redaction, logged operations can carry document field values into the diagnostic log, where a reader who is not a database user can see them. The documented startup routes are the `--redactClientLogData` flag or the configuration setting; keep the configuration setting so it survives restarts:

```yaml
security:
  redactClientLogData: true
```

Redaction replaces the values accompanying a log message with `###`. Metadata such as error and operation codes, line numbers, and source-file names remain visible, and the documentation scopes redaction to the diagnostic log; do not rely on it for the audit log. MongoDB documents using it together with encryption at rest and TLS. See the [redactClientLogData parameter](https://www.mongodb.com/docs/v8.0/reference/parameters/), the [mongod flag reference](https://www.mongodb.com/docs/v8.0/reference/program/mongod/), and the [log-redaction example](https://www.mongodb.com/docs/v8.0/administration/monitoring/).

## 7. Encrypt the storage engine with a managed key

MongoDB Enterprise 3.2 introduced native encryption for the WiredTiger storage engine; MongoDB Community has no native equivalent and depends on host or filesystem encryption. `security.enableEncryption` defaults to `false`. Native encryption cannot encrypt existing data: enable it on a fresh member and populate it through initial sync or the documented migration, rather than restarting a populated data directory with the flag set. See [encryption at rest](https://www.mongodb.com/docs/v8.0/core/security-encryption-at-rest/).

For a local key file:

```yaml
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb/storage-master.key
```

This key encrypts storage and is unrelated to `security.keyFile`, which authenticates cluster members in section 2. The local key procedure does not support key rotation. See the [encryption configuration options](https://www.mongodb.com/docs/v8.0/reference/configuration-options/).

MongoDB recommends a KMIP key server over a local key file. Keep `enableEncryption: true` and replace the key file with a `security.kmip` block:

```yaml
security:
  enableEncryption: true
  kmip:
    serverName: kmip.example.internal
    port: 5696
    serverCAFile: /etc/mongodb/kmip-ca.pem
    clientCertificateFile: /etc/mongodb/kmip-client.pem
```

The client PEM holds the client certificate and its private key. Supply `security.kmip.keyIdentifier` only to adopt an existing key when first enabling encryption; otherwise MongoDB requests a new key from the server. See the [configure encryption procedure](https://www.mongodb.com/docs/v8.0/tutorial/configure-encryption/).

## 8. Encrypt selected fields with client-side field level encryption

Transport TLS and storage encryption still leave ordinary field values readable by a sufficiently privileged database or host user. Client-side field level encryption (CSFLE) encrypts chosen fields in the driver before they reach the server; there is no `mongod` switch. Explicit CSFLE is available in MongoDB Community, Enterprise Advanced, and Atlas, while automatic encryption requires Enterprise or Atlas. Automatic decryption is available in Community. See [CSFLE](https://www.mongodb.com/docs/v8.0/core/csfle/) and [manual encryption](https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/manual-encryption/).

Automatic CSFLE configures the client with an `autoEncryption` object naming the key-vault namespace, the KMS providers, and a local `schemaMap` that marks the encrypted fields. Supply that schema locally: a schema fetched only from the server lets a compromised server drop the encryption requirement and induce plaintext writes. For the Community explicit path, set `bypassAutoEncryption: true` and call `ClientEncryption.encrypt()` before writing, encrypting query values explicitly as well. A randomized algorithm does not support equality matching on the field; the deterministic variant does, at the cost of revealing which stored values are equal. Consider a server-side `$jsonSchema` that rejects plaintext writes to the encrypted fields, and keep master-key access separate from ordinary database access. See the [automatic-encryption schemas](https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/automatic-encryption/), [CSFLE client options](https://www.mongodb.com/docs/v8.0/core/csfle/reference/csfle-options-clients/), and [CSFLE encryption algorithms](https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/encryption-algorithms/).

## 9. Query encrypted fields with Queryable Encryption

Queryable Encryption (QE) encrypts fields in the driver while still allowing the server to run supported queries against the ciphertext. Equality queries became generally available in MongoDB 7.0 and range queries in MongoDB 8.0; the 6.0 public preview is incompatible with the generally available format and is not a production baseline. As with CSFLE, automatic encryption requires Enterprise or Atlas, while explicit QE and automatic decryption are available in Community. See the [7.0 GA release notes](https://www.mongodb.com/docs/v8.0/release-notes/7.0/), the [8.0 range-query release notes](https://www.mongodb.com/docs/v8.0/release-notes/8.0/), [Queryable Encryption](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/), and the [QE manual encryption edition split](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/fundamentals/manual-encryption/).

QE requires a new encrypted collection created with an `encryptedFields` definition; an existing collection cannot have QE turned on in place, and one collection cannot combine CSFLE and QE. Automatic clients set `autoEncryption` with the key-vault namespace, the KMS providers, and a local `encryptedFieldsMap`. For the Community explicit path, set `bypassQueryAnalysis: true` and drive `ClientEncryption` directly. QE supports replica sets and sharded clusters, not standalones. Do not carry forward legacy `rangePreview` recipes; that option was removed in 8.0. See the [QE limitations](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/limitations/), [QE client options](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/qe-options-clients/), the [8.0 compatibility notes](https://www.mongodb.com/docs/v8.0/release-notes/8.0-compatibility/), and the [manual-encryption reference](https://www.mongodb.com/docs/v8.0/core/queryable-encryption/fundamentals/manual-encryption/).

## Common mistakes

- `bindIp: 0.0.0.0` set to fix a connection problem, with `authorization` still unset; this is the classic leaked-database configuration.
- Authorization enabled but every service sharing the `admin` account.
- TLS on the server while the connection string still says `tls=false` because a container healthcheck was easier that way.
- Appending another `net` or `security` mapping instead of merging settings.
- Leaving `transitionToAuth: true` after a migration.
- Treating a trusted TLS certificate as an authenticated, least-privilege MongoDB user.
- Issuing application certificates with cluster-member attributes.
- Treating a timeout or `listDatabases` output as proof of collection authorization.
- Assuming MongoDB Community offers Enterprise auditing, `redactClientLogData`, or native storage encryption.
- Enabling storage encryption on a populated data directory and assuming the existing files become encrypted.
- Trusting a server-supplied CSFLE schema, which a compromised server can weaken to induce plaintext writes.
- Combining CSFLE and Queryable Encryption on one collection, or carrying a legacy `rangePreview` recipe into 8.0.

## Sources (checked September 2026)

- MongoDB security checklist and Community authentication support: https://www.mongodb.com/docs/manual/administration/security-checklist/
- MongoDB release lifecycle schedule: https://www.mongodb.com/legal/support-policy/lifecycles
- Enable access control and bootstrap the administrator: https://www.mongodb.com/docs/manual/tutorial/enable-authentication/
- Configuration-file startup and network, TLS, and security options: https://www.mongodb.com/docs/manual/reference/configuration-options/
- mongod options and authorization: https://www.mongodb.com/docs/manual/reference/program/mongod/
- mongos options and internal authentication: https://www.mongodb.com/docs/manual/reference/program/mongos/
- Authenticate the current shell with db.auth(): https://www.mongodb.com/docs/manual/reference/method/db.auth/
- Create users, restrict SCRAM mechanisms, and protect credential transport: https://www.mongodb.com/docs/manual/reference/method/db.createuser/
- Create custom roles and understand their scope: https://www.mongodb.com/docs/manual/reference/method/db.createrole/
- Privilege actions for collection operations: https://www.mongodb.com/docs/manual/reference/privilege-actions/
- Built-in role capabilities for database, collection, and index operations: https://www.mongodb.com/docs/compass/connect/required-access/
- Collection creation and insert privilege: https://www.mongodb.com/docs/manual/reference/command/create/
- Update users and apply authentication restrictions: https://www.mongodb.com/docs/manual/reference/method/db.updateuser/
- Configure TLS and client-certificate validation: https://www.mongodb.com/docs/manual/tutorial/configure-ssl/
- Internal membership authentication and certificate requirements: https://www.mongodb.com/docs/manual/core/security-internal-authentication/
- Configure x.509 membership authentication: https://www.mongodb.com/docs/manual/tutorial/configure-x509-member-authentication/
- Keyfile setup, permissions, and existing-cluster transition: https://www.mongodb.com/docs/manual/tutorial/enforce-keyfile-access-control-in-existing-replica-set/
- Register and authenticate x.509 client identities: https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication/
- x.509 certificate requirements and client/member separation: https://www.mongodb.com/docs/manual/core/security-x.509/
- mongosh connection, TLS, authentication, and password-prompt options: https://www.mongodb.com/docs/mongodb-shell/reference/options/
- Connection-string TLS options and SCRAM negotiation: https://www.mongodb.com/docs/manual/reference/connection-string-options/
- Connectivity probe using ping: https://www.mongodb.com/docs/manual/reference/command/ping/
- Authenticated identities reported by connectionStatus: https://www.mongodb.com/docs/manual/reference/command/connectionstatus/
- Collection read command: https://www.mongodb.com/docs/manual/reference/command/find/
- Collection insert command and write results: https://www.mongodb.com/docs/manual/reference/command/insert/
- Collection update command and write results: https://www.mongodb.com/docs/manual/reference/command/update/
- Collection delete command: https://www.mongodb.com/docs/manual/reference/command/delete/
- MongoDB authorization and authentication error codes: https://www.mongodb.com/docs/manual/reference/error-codes/
- listDatabases privilege-dependent behavior: https://www.mongodb.com/docs/manual/reference/command/listdatabases/
- Replica-set status and required privilege: https://www.mongodb.com/docs/manual/reference/command/replsetgetstatus/
- MongoDB 8.0 Enterprise auditing: https://www.mongodb.com/docs/v8.0/core/auditing/
- MongoDB 8.0 configure auditing and destinations: https://www.mongodb.com/docs/v8.0/tutorial/configure-auditing/
- MongoDB 8.0 audit filters: https://www.mongodb.com/docs/v8.0/tutorial/configure-audit-filters/
- MongoDB 8.0 server parameters (auditAuthorizationSuccess, redactClientLogData): https://www.mongodb.com/docs/v8.0/reference/parameters/
- MongoDB 8.0 mongod redactClientLogData flag: https://www.mongodb.com/docs/v8.0/reference/program/mongod/
- MongoDB 8.0 encryption at rest: https://www.mongodb.com/docs/v8.0/core/security-encryption-at-rest/
- MongoDB 8.0 encryption configuration options: https://www.mongodb.com/docs/v8.0/reference/configuration-options/
- MongoDB 8.0 configure encryption and KMIP procedure: https://www.mongodb.com/docs/v8.0/tutorial/configure-encryption/
- MongoDB 8.0 client-side field level encryption: https://www.mongodb.com/docs/v8.0/core/csfle/
- MongoDB 8.0 CSFLE manual (explicit) encryption: https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/manual-encryption/
- MongoDB 8.0 CSFLE automatic-encryption schemas: https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/automatic-encryption/
- MongoDB 8.0 CSFLE client options: https://www.mongodb.com/docs/v8.0/core/csfle/reference/csfle-options-clients/
- MongoDB 8.0 Queryable Encryption: https://www.mongodb.com/docs/v8.0/core/queryable-encryption/
- MongoDB 8.0 Queryable Encryption 7.0 GA release notes: https://www.mongodb.com/docs/v8.0/release-notes/7.0/
- MongoDB 8.0 Queryable Encryption limitations: https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/limitations/
- MongoDB 8.0 Queryable Encryption client options: https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/qe-options-clients/
- MongoDB 8.0 Queryable Encryption manual encryption (edition split): https://www.mongodb.com/docs/v8.0/core/queryable-encryption/fundamentals/manual-encryption/
- MongoDB 8.0 Queryable Encryption supported operations (range BSON types): https://www.mongodb.com/docs/v8.0/core/queryable-encryption/reference/supported-operations/
- MongoDB 8.0 log-redaction example: https://www.mongodb.com/docs/v8.0/administration/monitoring/
- MongoDB 8.0 CSFLE encryption algorithms: https://www.mongodb.com/docs/v8.0/core/csfle/fundamentals/encryption-algorithms/
- MongoDB 8.0 release notes (Queryable Encryption range queries): https://www.mongodb.com/docs/v8.0/release-notes/8.0/
- MongoDB 8.0 compatibility notes (rangePreview removal): https://www.mongodb.com/docs/v8.0/release-notes/8.0-compatibility/
- Bash file-creation mask: https://www.gnu.org/s/bash/manual/html_node/Bourne-Shell-Builtins.html
- Bash redirection and noclobber behavior: https://www.gnu.org/s/bash/manual/bash.html
