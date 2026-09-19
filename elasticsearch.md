# Elasticsearch and OpenSearch: keep security switched on

Open Elasticsearch instances produced some of the largest data leaks on record. Modern versions ship secure; the failure mode today is deliberately switching protection off to make an error message go away.

## Elasticsearch (8.0 and later)

The examples below target self-managed Elasticsearch 8.x. TLS, native users, index-scoped RBAC, REST API keys, anonymous-access controls, and CORS settings are available with **free Basic**. LDAP authentication and audit logging require **paid Platinum/Enterprise**. At the time of writing, self-managed Platinum is available to existing customers only. See the [subscription matrix](https://www.elastic.co/subscriptions).

- A fresh install auto-configures security on first start when it runs: authentication is enabled, TLS is set up for HTTP and transport, and a password is generated for the `elastic` superuser. Keep all of it. Auto-configuration is SKIPPED if startup output is redirected, if the config directory is not writable, or if certain security or discovery settings already exist (single-node discovery and a `cluster.initial_master_nodes` naming only the current node are exempted); Debian and RPM packages do not print the password (reset it with `elasticsearch-reset-password -u elastic`). Confirm security actually came up rather than assuming it did. See [automatic security setup](https://www.elastic.co/docs/deploy-manage/security/self-auto-setup).
- Never set `xpack.security.enabled: false`, and never expose a node where TLS (`xpack.security.http.ssl.enabled`) has been turned off. If a client cannot connect, fix the client's CA trust ([self-signed.md](self-signed.md)) or issue a real certificate ([free-certificates.md](free-certificates.md)); do not remove the lock.
- `network.host` defaults to `_local_`, but leaving it alone does not make the node private: security auto-configuration writes `http.host: 0.0.0.0` into `elasticsearch.yml`, which overrides that default for HTTP. Read the effective setting rather than assuming the default, and let remote access go through the same decision as any database: private network, VPN or tunnel, TLS everywhere. See [networking settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings).

### Application RBAC and scoped credentials

**Free Basic.** Give each application its own identity and index-scoped role ([authentication.md](authentication.md)). The `superuser` role grants broad cluster and data access, including security administration; do not give it to applications. See [built-in roles](https://www.elastic.co/docs/reference/elasticsearch/roles).

For both products' examples, substitute the host, port, and file paths before use. Use curl 7.76.0 or later. Provision credential files in an owner-only directory, with file permissions `0600`:

- `/path/admin.header`: one complete `Authorization: Basic ...` header for the selected product's administrator.
- `/path/app-user.header`: the same header format for the dedicated application user.
- `/path/app-key.header`: one complete `Authorization: ApiKey ...` header for its issued key.

For Basic authentication, the value is base64 of `username:password`; base64 is not encryption. Prepare these files through your secret manager or a protected local workflow, without putting secrets in shell command arguments or history. Keep request-body and key-response files equally protected, including files that already exist. File input keeps secrets out of curl's argv; it does not protect them from readers of those files or from verbose request tracing.

1. As an administrator with `manage_security`, create a role that reads only `app-data`. `manage_own_api_key` lets the dedicated user issue its own keys; it does not grant access to other indexes. See the [role API](https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role).

   ```bash
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/http_ca.crt --header @/path/admin.header \
     --header 'Content-Type: application/json' --request PUT \
     --data-binary @- https://search.example.com:9200/_security/role/app_reader <<'JSON'
   {
     "cluster": ["manage_own_api_key"],
     "indices": [{"names": ["app-data"], "privileges": ["read"]}]
   }
   JSON
   ```

2. Create `/path/es-app-user.json` with the following structure. Replace the password placeholder inside that protected file with a unique random password before submitting it. The [native-user API](https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-user) accepts the password in the JSON request body.

   ```json
   {"password":"REPLACE_WITH_RANDOM_PASSWORD","roles":["app_reader"]}
   ```

   ```bash
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/http_ca.crt --header @/path/admin.header \
     --header 'Content-Type: application/json' --request PUT \
     --data-binary @/path/es-app-user.json \
     https://search.example.com:9200/_security/user/app_reader
   ```

3. Authenticate as that native user to create the application key. The explicit descriptor grants only reads of `app-data`; it does not copy the user's key-management privilege.

   ```bash
   (umask 077
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/http_ca.crt --header @/path/app-user.header \
     --header 'Content-Type: application/json' --request POST \
     --output /path/es-app-key-response.json \
     --data-binary @- https://search.example.com:9200/_security/api_key <<'JSON'
   {
     "name": "app-reader",
     "expiration": "1d",
     "role_descriptors": {
       "app_read": {
         "cluster": [],
         "indices": [{"names": ["app-data"], "privileges": ["read"]}]
       }
     }
   }
   JSON
   )
   ```

   Effective key permissions are the intersection of `role_descriptors` and the creator's permissions captured at creation. Omitting descriptors inherits a snapshot of the creator's permissions; omitting `expiration` makes a non-expiring key. Authenticate key creation with the native user's credentials: an API key cannot create another privileged key. Store the response's `encoded` value in `/path/app-key.header` after `Authorization: ApiKey `. See [Create an API key](https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-create-api-key).

Optional LDAP mapping is a **paid Platinum/Enterprise realm** example, not a requirement for the free native-user setup. With an existing, securely configured realm named `ldap1`, an administrator can map a specific directory group to the role:

```http
PUT /_security/role_mapping/app_ldap
{
  "enabled": true,
  "roles": ["app_reader"],
  "rules": {
    "all": [
      {"field": {"realm.name": "ldap1"}},
      {"field": {"groups": "cn=app-readers,ou=groups,dc=example,dc=com"}}
    ]
  }
}
```

Use the actual realm and group DN. Native users receive their roles through the user API above; this mapping is for directory identities. See [LDAP authentication](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/ldap) and the [role-mapping API](https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role-mapping).

### Anonymous access off and narrow CORS

**Free Basic.** Remove `xpack.security.authc.anonymous.roles` from `elasticsearch.yml`, including any equivalent nested configuration. With no anonymous roles specified, anonymous access is disabled and requests without credentials receive `401`. Apply the static configuration change by restarting affected nodes. See [anonymous access](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access).

`http.cors.enabled` defaults to `false`; leave it disabled unless a browser application needs direct cross-origin access. If needed, configure one exact origin, including scheme and any non-default port. For a read-only browser client:

```yaml
http.cors.enabled: true
http.cors.allow-origin: "https://app.example.com"
http.cors.allow-methods: "GET,OPTIONS"
http.cors.allow-headers: "Authorization,Content-Type"
```

These are static settings in `elasticsearch.yml`. Restart affected nodes. Do not use `*` or a broad origin regex. CORS controls browser access; authentication and index permissions still apply. See [HTTP CORS settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings).

### Audit logging

**Paid Platinum/Enterprise; unavailable with Basic.** Audit logging is disabled by default. On Elasticsearch 8.x, put this in `elasticsearch.yml` on every node and perform a rolling restart:

```yaml
xpack.security.audit.enabled: true
xpack.security.audit.logfile.events.emit_request_body: false
```

Events go to `CLUSTERNAME_audit.json` in each node's log directory. The dynamic-enable support documented for **9.5 and later does not apply to 8.x**. See [enabling audit logs](https://www.elastic.co/docs/deploy-manage/security/logging-configuration/enabling-audit-logs).

Keep request-body emission disabled, its default. Bodies can contain sensitive application data. The default included events contain `authentication_failed`; ensure custom event exclusions or ignore policies do not suppress the failures you need to detect. See [auditing settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/auding-settings).

Collect audit files into a separately protected logging destination. Restrict access and retention administration separately from application credentials.

## OpenSearch

The controls below are provided by **free Apache-2.0 OpenSearch Security**, with no paid security tier. Native scoped API keys have an additional version requirement: **OpenSearch 3.7 or later**. See the [Security plugin license](https://github.com/opensearch-project/security/blob/main/LICENSE.txt).

- The security plugin provides authentication and TLS; never run with it disabled, including in Docker examples.
- Starting with 2.12, new installations using the demo configuration require an initial admin password through `OPENSEARCH_INITIAL_ADMIN_PASSWORD`. Make it long and random. See [demo configuration](https://docs.opensearch.org/latest/security/configuration/demo-configuration/).
- The demo configuration also seeds `internal_users.yml` with seven built-in accounts (`admin`, `anomalyadmin`, `kibanaserver`, `kibanaro`, `logstash`, `readall`, `snapshotrestore`), meant for evaluation only. `OPENSEARCH_INITIAL_ADMIN_PASSWORD` sets the `admin` password and nothing else, so the other six keep the credentials shipped in the demo file. Before any real deployment, replace those users with your own or remove the demo accounts; on a cluster that has already initialized, editing the file is not enough, apply the change with `securityadmin.sh`, since the live configuration is the `.opendistro_security` index, not the file on disk. Then confirm each demo login is refused.
- The demo configuration installs demo TLS certificates for evaluation; replace them with your own before any real deployment. Keep REST TLS enabled with `plugins.security.ssl.http.enabled: true` and your deployed certificates. The underlying REST TLS setting defaults to `false`; the presence of the Security plugin alone is not proof that HTTPS is enabled. See [TLS configuration](https://docs.opensearch.org/latest/security/configuration/tls/).

### Application RBAC and scoped credentials

**Free Apache-2.0.** The `all_access` role grants broad cluster, index, and tenant access. Give applications a custom role instead. Use an administrator authorized for the Security REST API; ordinary RBAC permissions alone do not grant access to those administration endpoints. See [users and roles](https://docs.opensearch.org/latest/security/access-control/users-roles/) and [API permissions](https://docs.opensearch.org/latest/security/access-control/api/).

1. Create an index-scoped role through the [role API](https://docs.opensearch.org/latest/security/api/roles/create-role/):

   ```bash
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/production-ca.pem --header @/path/admin.header \
     --header 'Content-Type: application/json' --request PUT \
     --data-binary @- https://search.example.com:9200/_plugins/_security/api/roles/app_reader <<'JSON'
   {
     "cluster_permissions": [],
     "index_permissions": [{"index_patterns": ["app-data"], "allowed_actions": ["read"]}],
     "tenant_permissions": []
   }
   JSON
   ```

2. Prepare `/path/os-app-user.json` as a protected request-body file. Replace its password placeholder before submitting:

   ```json
   {"password":"REPLACE_WITH_RANDOM_PASSWORD","backend_roles":[]}
   ```

   Create the internal user and map it to the role. These endpoints create or replace resources; use new application-specific names and review existing mappings before replacing them. See the [user API](https://docs.opensearch.org/latest/security/api/users/create-user/) and [role-mapping API](https://docs.opensearch.org/latest/security/api/role-mappings/create-role-mapping/).

   ```bash
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/production-ca.pem --header @/path/admin.header \
     --header 'Content-Type: application/json' --request PUT \
     --data-binary @/path/os-app-user.json \
     https://search.example.com:9200/_plugins/_security/api/internalusers/app_reader

   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/production-ca.pem --header @/path/admin.header \
     --header 'Content-Type: application/json' --request PUT \
     --data-binary @- https://search.example.com:9200/_plugins/_security/api/rolesmapping/app_reader <<'JSON'
   {"users":["app_reader"],"backend_roles":[],"hosts":[]}
   JSON
   ```

   Review other mappings too: this mapping does not remove grants received through another role.

3. **For native scoped API keys, require 3.7+.** Earlier versions can use the dedicated internal user's credentials over TLS. On 3.7+, merge the following into `config/opensearch-security/config.yml`, preserving existing authentication domains and other settings. These example limits cap key lifetime at one day and outstanding tokens at 100:

   ```yaml
   config:
     dynamic:
       api_tokens:
         enabled: true
         max_duration_seconds: 86400
         max_tokens: 100
   ```

   Apply configuration-file changes with `securityadmin.sh`. Run from the OpenSearch installation directory, substitute the actual cluster name, and use the deployed CA and a separate admin certificate whose DN is configured in `plugins.security.authcz.admin_dn`. Keep hostname verification enabled.

   ```bash
   ./plugins/opensearch-security/tools/securityadmin.sh \
     -h search.example.com -p 9200 -cn search-cluster \
     -cacert /path/production-ca.pem \
     -cert /path/security-admin.pem -key /path/security-admin-key.pem \
     -f config/opensearch-security/config.yml -t config
   ```

   The key path names a protected PKCS#8 file; no key contents or passphrase belong in argv. Back up the live security configuration before applying files: uploading a configuration type replaces that type, and stale files can overwrite REST changes. Use `-f` and `-t` to limit the upload. See [applying configuration changes](https://docs.opensearch.org/latest/security/configuration/security-admin/).

   Only security administrators create these keys. Create one with explicit permissions:

   ```bash
   (umask 077
   curl -q -g -sS --fail-with-body --noproxy '*' \
     --cacert /path/production-ca.pem --header @/path/admin.header \
     --header 'Content-Type: application/json' --request POST \
     --output /path/os-app-key-response.json \
     --data-binary @- https://search.example.com:9200/_plugins/_security/api/apitokens <<'JSON'
   {
     "name": "app-reader",
     "cluster_permissions": [],
     "index_permissions": [{"index_pattern": ["app-data"], "allowed_actions": ["read"]}],
     "duration_seconds": 86400
   }
   JSON
   )
   ```

   The token API uses **`index_pattern`**, singular, while the role API uses **`index_patterns`**. Lifetime is **`duration_seconds`**, not Elasticsearch's `expiration`. If omitted, lifetime uses `max_duration_seconds`, whose documented default is 7,776,000 seconds; the configuration above explicitly reduces it. Store the returned `token` once, in `/path/app-key.header` after `Authorization: ApiKey `. It cannot be retrieved again. See [API-key configuration](https://docs.opensearch.org/latest/security/access-control/api-keys/) and [Create API Key](https://docs.opensearch.org/latest/security/api/api-keys/create/).

### Anonymous access off and narrow CORS

**Free Apache-2.0.** In the security `config.yml`, set `config.dynamic.http.anonymous_auth_enabled: false`. Preserve a working authentication domain. For example, merge this into an existing internal-user configuration, keeping its `_meta` section and other required settings:

```yaml
config:
  dynamic:
    http:
      anonymous_auth_enabled: false
    authc:
      basic_internal_auth_domain:
        http_enabled: true
        transport_enabled: true
        order: 0
        http_authenticator:
          type: basic
          challenge: true
        authentication_backend:
          type: intern
```

Preserve any other authentication domains in use. Reapply the complete updated `config.yml` with the `securityadmin.sh` command above; editing the local file alone does not change the live configuration. See [security backend configuration](https://docs.opensearch.org/latest/security/configuration/configuration/) and [HTTP basic authentication](https://docs.opensearch.org/latest/security/authentication-backends/basic-authc/).

`http.cors.enabled` defaults to `false`. Leave it disabled unless necessary. If a browser client needs it, put the following in `opensearch.yml` and restart affected nodes:

```yaml
http.cors.enabled: true
http.cors.allow-origin: "https://app.example.com"
http.cors.allow-methods: "GET,OPTIONS"
http.cors.allow-headers: "Authorization,Content-Type"
```

Use the actual exact origin, never `*` or a broad regex. Keep authentication enforced. See [HTTP CORS settings](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/).

### Audit logging

**Free Apache-2.0.** Audit logging needs both a storage destination and an enabled audit configuration. Set this in `opensearch.yml` on each node, then restart affected nodes:

```yaml
plugins.security.audit.type: internal_opensearch
```

This stores events in the current cluster, by default in daily `auditlog-YYYY.MM.dd` indexes. The shipped audit configuration has `config.enabled: true`, but without a storage type it does not record events. See [audit logging](https://docs.opensearch.org/latest/security/audit-logs/index/).

Read the live configuration, then enable REST auditing and disable request-body logging. Use the production admin certificate for the audit PATCH operation:

```bash
curl -q -g -sS --fail-with-body --noproxy '*' \
  --cacert /path/production-ca.pem \
  --cert /path/security-admin.pem --key /path/security-admin-key.pem \
  https://search.example.com:9200/_plugins/_security/api/audit

curl -q -g -sS --fail-with-body --noproxy '*' \
  --cacert /path/production-ca.pem \
  --cert /path/security-admin.pem --key /path/security-admin-key.pem \
  --header 'Content-Type: application/json' --request PATCH \
  --data-binary @- https://search.example.com:9200/_plugins/_security/api/audit <<'JSON'
[
  {"op":"add","path":"/config/enabled","value":true},
  {"op":"add","path":"/config/audit/enable_rest","value":true},
  {"op":"add","path":"/config/audit/log_request_body","value":false}
]
JSON
```

Keep `config.audit.exclude_sensitive_headers` set to `true`, its documented default. If the live value is false, merge this into the full `config/opensearch-security/audit.yml`:

```yaml
config:
  audit:
    exclude_sensitive_headers: true
```

Apply that complete file with the same `securityadmin.sh` certificate arguments, replacing the file/type arguments with `-f config/opensearch-security/audit.yml -t audit`. Preserve the enabled and request-body settings. The GET response's `_readonly` list identifies fields that REST updates cannot change; do not treat a rejected PATCH as success. Repeat GET and confirm `enabled: true`, `enable_rest: true`, `log_request_body: false`, and `exclude_sensitive_headers: true`. See [GET audit configuration](https://docs.opensearch.org/latest/security/api/audit/get-audit-configuration/), [PATCH audit configuration](https://docs.opensearch.org/latest/security/api/audit/patch-audit-configuration/), and [audit configuration fields](https://docs.opensearch.org/latest/security/api/audit/update-audit-configuration/).

Ensure audit exclusions do not suppress `FAILED_LOGIN` or the identities and requests being tested. Collect audit events into a separately protected logging destination; application credentials must not be able to alter the evidence.

## Verify

All deployment checks below are **reasoned, not demonstrated**: the authoring environment has no target cluster or Docker/Podman runtime, and no access to the target node or audit collector. Expected outcomes follow the cited vendor behavior; deployment demonstration remains outstanding.

Before running:

- Substitute your actual hostname, HTTP port, and CA path inside the single quotes on the `set --` line. Paste the whole block. Use a TLS hostname covered by the deployed certificate.
- Elasticsearch automatic setup supplies `http_ca.crt`. For OpenSearch, use the **deployed production HTTP CA**, such as `/path/production-ca.pem`, and your production administrator's header file. Do not verify production against the demo CA.
- Have an administrator confirm that `app-data` and `other-data` each contain a readable document with ID `rbac-probe`. A missing document is not an RBAC-denial result.
- Prepare `/path/audit-probe.header` with a Basic authentication header for a confirmed nonexistent user named `audit_probe` and a deliberately wrong password. Keep all credentials in header files.
- Run the RBAC requests once with `/path/app-user.header`, then again with `/path/app-key.header`. On OpenSearch before 3.7, only the internal-user check applies.

The expected distinctions are:

| Check | Exposed or misconfigured outcome | Fixed outcome |
| --- | --- | --- |
| Application RBAC | A broad application identity reads both known documents. | The scoped identity reads `app-data` with `200` and receives an authorization `403` for `other-data`. A `401`, `404`, or connection error does not demonstrate correct RBAC. See [Elasticsearch privileges](https://www.elastic.co/docs/reference/elasticsearch/security-privileges) and [OpenSearch permissions](https://docs.opensearch.org/latest/security/access-control/permissions/). |
| Anonymous access | Disabled security or an anonymous read grant permits the no-credential document request. | No-credential requests are rejected with `401` for the configurations above. Checking `/` alone cannot rule out anonymous access granted only to an index. See [Elasticsearch anonymous access](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access) and [OpenSearch anonymous authentication](https://docs.opensearch.org/latest/security/access-control/anonymous-authentication/). |
| CORS | An overly broad policy grants the untrusted origin. | No `Access-Control-Allow-Origin` grant for the untrusted origin. If CORS is enabled, the trusted-origin positive control succeeds and grants exactly that origin. If CORS is disabled, neither origin is granted. Judge the headers, not just the status. See [Elasticsearch CORS](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings) and [OpenSearch CORS](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/). |
| Audit | Failed authentication returns `401`, but disabled or suppressed auditing produces no corresponding audit event. | The same failure produces a new Elasticsearch `authentication_failed` or OpenSearch `FAILED_LOGIN` event. A `401` alone does not prove auditing. Elasticsearch requires the paid audit tier. See [Elasticsearch audit events](https://www.elastic.co/docs/reference/elasticsearch/elasticsearch-audit-events) and [OpenSearch audit fields](https://docs.opensearch.org/latest/security/audit-logs/field-reference/). |

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SEARCH_HOST' '/path/http_ca.crt' '9200'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "set exactly host, CA file, and HTTP port; not probing"; exit 1; }
  case "$1|$2|$3" in
    *REPLACE_WITH_*|*search.example.com*) echo "substitute your deployment; not probing"; exit 1 ;;
  esac
  [ -n "$1" ] || { echo "host required; not probing"; exit 1; }
  [ -r "$2" ] || { echo "readable CA file required; not probing"; exit 1; }
  [ -n "$3" ] || { echo "port required; not probing"; exit 1; }
  case "$3" in *[!0-9]*) echo "HTTP port must be numeric"; exit 1 ;; esac

  # Reasoned: no target cluster or container runtime. Anonymous root probe.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" "https://$1:$3/"

  # Reasoned: no target cluster or container runtime. Administrative HTTPS control.
  # Elasticsearch: its HTTP CA (http_ca.crt from automatic setup).
  # OpenSearch: its deployed production HTTP CA and a production admin identity.
  curl -q -g -sS --fail-with-body --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" --header @/path/admin.header "https://$1:$3/" || exit 1

  # Reasoned: no target cluster or container runtime. Plaintext TLS probe.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' \
    "http://$1:$3/"

  # Reasoned: no target cluster or container runtime.
  # Test app-user.header, then repeat these two requests with app-key.header.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" --header @/path/app-user.header "https://$1:$3/app-data/_doc/rbac-probe"
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" --header @/path/app-user.header "https://$1:$3/other-data/_doc/rbac-probe"

  # Reasoned: no target cluster or container runtime. Anonymous access to data.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" "https://$1:$3/app-data/_doc/rbac-probe"

  # Reasoned: no target cluster or container runtime.
  # Browser preflights send no credentials.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    --cacert "$2" --include --request OPTIONS \
    --header 'Origin: https://untrusted.example.org' \
    --header 'Access-Control-Request-Method: GET' \
    --header 'Access-Control-Request-Headers: authorization' \
    "https://$1:$3/app-data/_doc/rbac-probe"
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    --cacert "$2" --include --request OPTIONS \
    --header 'Origin: https://app.example.com' \
    --header 'Access-Control-Request-Method: GET' \
    --header 'Access-Control-Request-Headers: authorization' \
    "https://$1:$3/app-data/_doc/rbac-probe"

  # Reasoned: no cluster, audit collector, or eligible ES audit license here.
  # audit-probe.header contains Basic auth for a nonexistent audit_probe user.
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" --header @/path/audit-probe.header "https://$1:$3/"
)
```

The administrative HTTPS control must return `200` and cluster JSON before interpreting the plaintext probe. With HTTP TLS enforced, plaintext must receive no HTTP response. Elasticsearch closes a plaintext connection to its HTTPS listener; OpenSearch's enabled REST TLS allows only HTTPS. Expect `http=000` with a reset or empty reply after connection. DNS failures, timeouts, or an unreachable service are inconclusive. Any actual HTTP status, including `401`, means that endpoint answered over plaintext and is a finding. See [Elasticsearch HTTP TLS settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings) and [OpenSearch REST TLS](https://docs.opensearch.org/latest/security/configuration/tls/).

For the audit check, inspect the receiving node's new `CLUSTERNAME_audit.json` entries or the corresponding OpenSearch audit index and separately collected copy. Match the recorded time, `audit_probe` identity, and request path. Require a new matching event, not an older failure. Verify that sensitive headers and request bodies are excluded. Missing events leave the audit check unresolved until collection delay, filtering, licensing, and configuration have been checked.

On the node itself, inspect listeners:

```bash
# Reasoned: no access to the target node. Run ON that node; substitute actual ports.
ss -tlnp 'sport = :9200'
ss -tlnp 'sport = :9300'
```

These use `ss`'s own port filter, avoiding accidental PID matches. For Elasticsearch, HTTP defaults to the range `9200-9300` and transport to `9300-9400`; each binds an available port. Inspect the actual ports used by either product. Expect loopback or deliberate private listeners. An unexpected public or wildcard listener is a finding to review against the network controls; no output is inconclusive until the running process and its actual ports are located.

An unauthenticated `GET /` returning cluster JSON is the classic finding; so is `_cat/indices` listing your data to the world.

| Demonstration backlog | Required work | Status |
| --- | --- | --- |
| ES-OS-VERIFY-1 | Demonstrate every check against exposed and fixed states in isolated Elasticsearch 8.x and OpenSearch test clusters, including OpenSearch 3.7+ keys and an eligible Elasticsearch audit license. Record versions, effective configuration, HTTP responses, listener output, and matching newly collected audit events. | Open: target clusters, container runtime, and audit collection are unavailable in the authoring environment. |

## Sources (checked September 2026)

- Elasticsearch self-managed subscription tiers and current Platinum availability: https://www.elastic.co/subscriptions
- Elasticsearch current subscription matrix PDF: https://www.elastic.co/pdf/subscriptions-2026-08-04.pdf
- Elasticsearch automatic security setup, skip conditions, and generated HTTP CA: https://www.elastic.co/docs/deploy-manage/security/self-auto-setup
- Elasticsearch password-reset command: https://www.elastic.co/docs/reference/elasticsearch/command-line-tools/reset-password
- Elasticsearch networking defaults and CORS settings: https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings
- Elasticsearch security settings, HTTP TLS, and anonymous configuration: https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings
- Elasticsearch built-in roles and superuser breadth: https://www.elastic.co/docs/reference/elasticsearch/roles
- Elasticsearch security privileges: https://www.elastic.co/docs/reference/elasticsearch/security-privileges
- Elasticsearch 8.x create or update role API: https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role
- Elasticsearch 8.x native-user API: https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-user
- Elasticsearch 8.x API-key creation, permission intersection, and expiration: https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-create-api-key
- Elasticsearch LDAP authentication: https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/ldap
- Elasticsearch 8.x role-mapping API: https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role-mapping
- Elasticsearch anonymous access and rejection without configured roles: https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access
- Elasticsearch audit enablement and the 9.5 dynamic-setting boundary: https://www.elastic.co/docs/deploy-manage/security/logging-configuration/enabling-audit-logs
- Elasticsearch auditing settings and request-body default: https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/auding-settings
- Elasticsearch audit event names and attributes: https://www.elastic.co/docs/reference/elasticsearch/elasticsearch-audit-events
- Elasticsearch 8.x document retrieval API: https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-get
- OpenSearch Security Apache-2.0 license: https://github.com/opensearch-project/security/blob/main/LICENSE.txt
- OpenSearch demo security configuration and initial admin password: https://docs.opensearch.org/latest/security/configuration/demo-configuration/
- OpenSearch shipped demo accounts: https://github.com/opensearch-project/security/blob/main/config/internal_users.yml
- OpenSearch TLS settings and admin certificates: https://docs.opensearch.org/latest/security/configuration/tls/
- OpenSearch applying security configuration files: https://docs.opensearch.org/latest/security/configuration/security-admin/
- OpenSearch users, roles, and all_access breadth: https://docs.opensearch.org/latest/security/access-control/users-roles/
- OpenSearch Security REST API permissions: https://docs.opensearch.org/latest/security/access-control/api/
- OpenSearch create or update role API: https://docs.opensearch.org/latest/security/api/roles/create-role/
- OpenSearch internal-user API: https://docs.opensearch.org/latest/security/api/users/create-user/
- OpenSearch role-mapping API: https://docs.opensearch.org/latest/security/api/role-mappings/create-role-mapping/
- OpenSearch API-key introduction in 3.7 and api_tokens configuration: https://docs.opensearch.org/latest/security/access-control/api-keys/
- OpenSearch API-key creation, index_pattern, and duration_seconds: https://docs.opensearch.org/latest/security/api/api-keys/create/
- OpenSearch security backend configuration: https://docs.opensearch.org/latest/security/configuration/configuration/
- OpenSearch HTTP basic authentication domain: https://docs.opensearch.org/latest/security/authentication-backends/basic-authc/
- OpenSearch anonymous authentication: https://docs.opensearch.org/latest/security/access-control/anonymous-authentication/
- OpenSearch networking and CORS settings: https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/
- OpenSearch audit enablement, destinations, and categories: https://docs.opensearch.org/latest/security/audit-logs/index/
- OpenSearch audit configuration GET and read-only fields: https://docs.opensearch.org/latest/security/api/audit/get-audit-configuration/
- OpenSearch audit configuration PATCH: https://docs.opensearch.org/latest/security/api/audit/patch-audit-configuration/
- OpenSearch audit configuration fields and defaults: https://docs.opensearch.org/latest/security/api/audit/update-audit-configuration/
- OpenSearch audit event fields: https://docs.opensearch.org/latest/security/audit-logs/field-reference/
- OpenSearch security permissions: https://docs.opensearch.org/latest/security/access-control/permissions/
- OpenSearch read action group: https://docs.opensearch.org/latest/security/access-control/default-action-groups/
- OpenSearch document retrieval API: https://docs.opensearch.org/latest/api-reference/document-apis/get-documents/
- curl options, header-file input, and request-body file input: https://curl.se/docs/manpage.html
- ss listener and port-filter syntax: https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html
