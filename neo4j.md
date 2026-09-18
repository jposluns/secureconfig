# Neo4j: listen address, initial password, and TLS on Bolt and HTTPS

A packaged Neo4j 5 listens on `localhost` only by default and ships with authentication on, but with the well-known `neo4j`/`neo4j` credential, Bolt TLS at `DISABLED`, and plaintext HTTP enabled instead of HTTPS. Setting `server.default_listen_address=0.0.0.0` on such an install to "make it reachable" therefore exposes a database with a guessable password over plaintext. The official Docker image is the exception: its entrypoint sets `server.default_listen_address=0.0.0.0` for you, so a published container port is reachable immediately; set the first password with `NEO4J_AUTH=neo4j/REPLACE_WITH_LONG_RANDOM_VALUE` (never `NEO4J_AUTH=none`, which disables authentication), and note `NEO4J_AUTH` only seeds a NEW database, it does not rotate the credential of an existing one. Setting names below are Neo4j 5; Neo4j 4.x names differ.

## 1. Set the initial password before first start

```bash
neo4j-admin dbms set-initial-password REPLACE_WITH_LONG_RANDOM_VALUE --require-password-change=false
```

This command is for use once, before the database's first start; the default minimum length is 8 characters (`dbms.security.auth_minimum_password_length`, available since Neo4j 5.3). The documentation warns against typing the password on the command line where it lands in shell history: read it into the command from your secret store rather than typing the literal value (or disable history for that command), noting that it can still appear in `/proc/<pid>/cmdline` while this one-time command runs. Leave `dbms.security.auth_enabled` at its default `true`; the documentation reserves turning it off for recovery with all network access blocked.

## 2. Bind deliberately

`server.default_listen_address` supplies the host part for every connector (`server.bolt.listen_address` defaults to `:7687`, `server.http.listen_address` to `:7474`, `server.https.listen_address` to `:7473`). Keep the default `localhost` unless remote clients are deliberate, then prefer a specific private address over `0.0.0.0`. The documentation notes that changing it may expose cluster ports and recommends overriding the cluster `listen_address` settings to `localhost` when clustering is not in use; the backup port (`server.backup.listen_address`, default `127.0.0.1:6362`) must stay off external interfaces. Firewall per [cloud-firewalls.md](cloud-firewalls.md) or [host.md](host.md), and widen only after steps 3 and 4.

```properties
server.default_listen_address=REPLACE_WITH_PRIVATE_IP
```

## 3. TLS on Bolt and HTTPS, HTTP off

Put a PKCS#8 PEM private key and certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)) under the policy directory, owned by `neo4j:neo4j`, key mode `0400`, certificate `0644`; legacy PKCS#1 keys (the PEM header that names an RSA key) are deprecated and must be converted. `server.bolt.tls_level=REQUIRED` refuses unencrypted Bolt (`OPTIONAL` keeps accepting it); `server.http.enabled=false` removes the plaintext 7474 endpoint. For machine clients that can hold certificates, `dbms.ssl.policy.bolt.client_auth=REQUIRE` adds mutual TLS.

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

Create a user per application instead of sharing `neo4j` ([authentication.md](authentication.md)). Role-based access control (built-in roles `reader`, `editor`, `publisher`, `architect`, `admin`, plus custom roles) is documented for Enterprise Edition; Community Edition has native users and passwords but no role management, so it cannot give an application read-only access and the network boundary carries more weight. Failed logins lock an account for `dbms.security.auth_lock_time` (default `5s`) after `dbms.security.auth_max_failed_attempts` (default `3`).

```cypher
CREATE USER app SET PASSWORD 'REPLACE_WITH_LONG_RANDOM_VALUE' CHANGE NOT REQUIRED;
GRANT ROLE reader TO app;    // Enterprise Edition; editor or publisher for writers
```

MFA: native login has no second factor. Enterprise Edition can delegate authentication to an OIDC provider whose policy ENFORCES MFA ([oidc-integration.md](oidc-integration.md)); plain LDAP password authentication (the `simple` bind) is single-factor and is not MFA unless the directory itself enforces a second factor, so confirm that enforcement and that no native or password path bypasses it ([mfa.md](mfa.md)). Otherwise mutual TLS is the possession factor for services, and every human path to the host sits behind MFA.

## 5. Restrict procedures, file import, and outbound requests

Authentication and roles decide who connects and what data they can touch. Enterprise Edition can go further and restrict which procedures a role may run (`EXECUTE` privileges) and its data loading (`LOAD` privileges), but the built-in data roles and default grants do not do that on their own, and Community Edition has no such privileges at all, so the settings below plus network egress controls carry the containment.

- Keep `dbms.security.procedures.unrestricted` empty unless a specific procedure genuinely needs to bypass security (the setting "enables these procedures to bypass security"), and narrow `dbms.security.procedures.allowlist` (default `*`) to only the procedures the workload uses. Install only the plugins you need.
- If APOC is installed, its settings live in `apoc.conf` (not `neo4j.conf`) in Neo4j 5. Leave `apoc.import.file.enabled=false` unless local file import is required, and keep `apoc.import.file.use_neo4j_config=true` so the import-directory checks still apply.
- `LOAD CSV` and APOC procedures such as `apoc.load.json` and `apoc.load.jdbc` make OUTBOUND requests, so a query can be steered at internal services or the cloud metadata endpoint (an SSRF vector Neo4j documents). Set `dbms.security.allow_csv_import_from_file_urls=false` when local `LOAD CSV` from file URLs is not needed (it defaults to `true` in the source, despite one vendor page saying otherwise); restrict the workload's egress so a query cannot reach your internal range or `169.254.169.254` ([egress-metadata.md](egress-metadata.md)); and where supported set `internal.dbms.cypher_ip_blocklist` to block internal CIDRs.

## Verify

Clients and drivers connect with `neo4j+s://`, which verifies the certificate; `neo4j+ssc://` accepts a self-signed certificate without verification and belongs in development only.

```bash
ss -tlnp   # a listener inventory in THIS namespace, not a firewall: expect 7687 (Bolt) and 7473 (HTTPS) on the intended address, 7474 (plain HTTP) ABSENT, and backup 6362 loopback-only; probe the real public IPv4/IPv6 path from another host too
# The probes below all target the same host, so paste the whole block with your Neo4j hostname on the
# set -- line; the guard refuses to run against an unsubstituted placeholder.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NEO4J_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the Neo4j hostname on the set -- line above; not probing"; exit 1 ;; esac
  # TLS + hostname verification on Bolt 7687. Point -CAfile at the CA that signed the server certificate
  # (omit only for a publicly trusted one; a self-signed or internal CA is not in the system store and the
  # check would fail on a correct deployment). Without the verify flags the handshake succeeds against any
  # certificate. This matches client_auth=NONE; with client_auth=REQUIRE add -cert and -key, or the server
  # refuses the connection and "Verification: OK" still prints.
  openssl s_client -connect "$1:7687" -verify_hostname "$1" -verify_return_error -CAfile ca.pem </dev/null
  # HTTP must be OFF: 7474 must not answer. Read the exit code: any HTTP status means 7474 answered (a
  # finding); exit 7 means the connection could not be ESTABLISHED - a refusal from the host you confirmed
  # is reachable is the pass, but a local socket or routing error also gives 7, so treat 7 as inconclusive
  # unless you know the host was reached; 6 is DNS and 28 a timeout, also inconclusive.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w "http7474 code=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "http://$1:7474/"
  # Plaintext Bolt must be refused BEFORE authentication: a wrong password on an OPTIONAL listener still
  # connects and then fails auth, which masquerades as a TLS refusal. Probe the transport with bolt://
  # (not neo4j://, which adds routing discovery); a TLS/connection refusal is the pass, an AUTHENTICATION
  # error means plaintext reached auth (tls_level is not REQUIRED). neo4j/neo4j here are not secrets.
  cypher-shell -a "bolt://$1:7687" -u neo4j -p neo4j 'RETURN 1;'
  # Default credential must be gone: over TLS an authentication failure is the pass, but a "password change
  # required" response means neo4j/neo4j is STILL accepted (a finding; section 1 prevents it).
  cypher-shell -a "neo4j+s://$1:7687" -u neo4j -p neo4j 'RETURN 1;'
  # Application login (positive control): omit -p so cypher-shell prompts for the real password - but clear
  # NEO4J_PASSWORD from the environment first, or cypher-shell reads it instead of prompting. For a private
  # or self-signed CA, cypher-shell needs its OWN trust (import the CA into the JVM/system trust store);
  # -CAfile/--cacert here configure only openssl and curl. Run a bounded query that returns the expected row.
  cypher-shell -a "neo4j+s://$1:7687" -u app 'RETURN 1 AS ok;'
  # HTTPS on 7473 must require auth: no credential must return 401. For the authenticated positive control
  # add --user neo4j, which PROMPTS (never -u neo4j:password, which puts the password in argv and history).
  # --cacert points at the signing CA (omit only for a publicly trusted one).
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 --cacert ca.pem -H 'Content-Type: application/json' -d '{"statements":[{"statement":"RETURN 1"}]}' -w "\nhttps7473-no-auth=%{http_code} exit=%{exitcode}\n" "https://$1:7473/db/neo4j/tx/commit"
)
```

## Common mistakes

- `server.default_listen_address=0.0.0.0` set during installation "to test", with `neo4j`/`neo4j` still in place.
- Bolt TLS configured but left at `server.bolt.tls_level=OPTIONAL`, so `neo4j://` clients keep connecting in plaintext.
- HTTPS enabled while `server.http.enabled` stays `true`, leaving 7474 open beside 7473.

## Sources (checked September 2026)

- Configure network connectors: https://neo4j.com/docs/operations-manual/current/configuration/connectors/
- Ports: https://neo4j.com/docs/operations-manual/current/configuration/ports/
- Set an initial password: https://neo4j.com/docs/operations-manual/current/configuration/set-initial-password/
- SSL framework: https://neo4j.com/docs/operations-manual/current/security/ssl-framework/
- Authentication and authorization: https://neo4j.com/docs/operations-manual/current/authentication-authorization/
- Manage users: https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-users/
- Manage roles: https://neo4j.com/docs/operations-manual/current/authentication-authorization/manage-roles/
- Built-in roles: https://neo4j.com/docs/operations-manual/current/authentication-authorization/built-in-roles/
- Cypher Shell: https://neo4j.com/docs/operations-manual/current/cypher-shell/
- Neo4j Docker introduction (`NEO4J_AUTH`, the `0.0.0.0` default listen address): https://neo4j.com/docs/operations-manual/current/docker/introduction/
- Securing extensions (`dbms.security.procedures.allowlist`/`unrestricted`): https://neo4j.com/docs/operations-manual/current/security/securing-extensions/
- APOC configuration (`apoc.conf`, `apoc.import.file.enabled`): https://neo4j.com/docs/apoc/current/config/
- Protecting against SSRF (LOAD CSV/APOC, metadata subnet, `internal.dbms.cypher_ip_blocklist`): https://neo4j.com/developer/kb/protecting-against-ssrf/
