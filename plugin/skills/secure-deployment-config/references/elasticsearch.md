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

### Field-level and document-level security

**Paid Platinum/Enterprise; unavailable with Basic. Minimum version within this guide: Elasticsearch 8.0; syntax pinned to 8.19.** FLS/DLS predate 8.0; their first historical release is not established here. At the time of writing, self-managed Platinum is available to existing customers only. Basic security became free in 6.8.0 and 7.1.0, explicitly excluding FLS/DLS. The default Elasticsearch distribution remains under ELv2; the additional AGPL source option does not make subscription features free. See the [dated subscription matrix](https://www.elastic.co/pdf/subscriptions-2025-07-29.pdf), [current subscription terms](https://www.elastic.co/subscriptions), [free-security announcement](https://www.elastic.co/blog/security-for-elasticsearch-is-now-free), and [licensing explanation](https://www.elastic.co/pricing/faq/licensing).

The existing `app_reader` role permits reading every document and field in `app-data`. Where tenants or sensitive fields share an index, restrict both documents and fields. Map `tenant_id` as `keyword`, then create a separate read-only role:

```http
PUT /_security/role/app_tenant_a_reader
{
  "cluster": [],
  "indices": [
    {
      "names": ["app-data"],
      "privileges": ["read"],
      "field_security": {
        "grant": ["tenant_id", "title", "category"]
      },
      "query": {
        "term": {
          "tenant_id": "tenant-a"
        }
      }
    }
  ]
}
```

`field_security.grant` selects readable fields; `query` selects readable documents. Use concrete field names, not field aliases. Some metadata fields remain accessible. Omitting field permissions permits all fields; omitting `query` removes DLS for that index permission entry. See the [8.19 role API](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-api-put-role.html), [FLS](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-level-security.html), and [DLS](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/document-level-security.html).

Assign this role to the application identity **instead of also retaining unrestricted `app_reader` access**. Elasticsearch combines grants across roles: unrestricted access to the same index can defeat these restrictions. Keep the account read-only. Review application API keys separately, including permissions captured when they were created; do not assume changing a user role repairs previously issued credentials. See [8.19 access-control and role-combination rules](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-and-document-access-control.html).

DLS does not remove every inference channel. Elasticsearch documents global scoring statistics and search requests that can reveal aggregate information about inaccessible documents. DLS role queries cannot use `has_child`, `has_parent`, terms lookup, indexed-shape lookup, or `percolate`; date ranges cannot use `now`. DLS also affects suggesters, profiling, and other APIs. Test the application's actual queries and aggregations. Prefer separate indices when stronger tenant or confidentiality isolation is required. See [8.19 security limitations](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-limitations.html).

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

The controls below are provided by **free Apache-2.0 OpenSearch Security**, with no paid security tier. Native scoped API keys have an additional version requirement: **OpenSearch 3.7 or later**. See the [Security plugin license](https://github.com/opensearch-project/security/blob/4ba3cc0e2ebec61b726b227fdf51e55f4a502182/LICENSE.txt).

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

### Field-level and document-level security

**Free Apache-2.0 OpenSearch Security; no paid feature tier. The FLS/DLS role schema is documented from OpenSearch 3.0 and applies across this guide's 3.x scope; the citations below are pinned to 3.6 and the behaviour is reviewed current to 3.8.0.** The role API was introduced in 1.0, and DLS appears in the 1.0 archive. These establish earlier availability, not the introduction release of every combined behavior below. See the [3.6 Security API](https://docs.opensearch.org/3.6/security/access-control/api/), [1.0 DLS archive](https://docs.opensearch.org/1.0/security-plugin/access-control/document-level-security/), and [3.8.0.0 Security licence](https://raw.githubusercontent.com/opensearch-project/security/3.8.0.0/LICENSE.txt).

The existing `app_reader` role permits reading every document and field in `app-data`. Map `tenant_id` as `keyword`, then create a separate read-only role using OpenSearch's schema:

```http
PUT /_plugins/_security/api/roles/app_tenant_a_reader
{
  "cluster_permissions": [],
  "index_permissions": [
    {
      "index_patterns": ["app-data"],
      "allowed_actions": ["read"],
      "dls": "{\"term\":{\"tenant_id\":\"tenant-a\"}}",
      "fls": ["tenant_id", "title", "category"]
    }
  ],
  "tenant_permissions": []
}
```

`dls` is a JSON-encoded string. Keep `tenant_id` visible in `fls`: fields used by DLS must remain readable. Map the dedicated application identity to this role and review every other effective role and mapping. Do not mix FLS inclusion and exclusion rules across roles without checking their documented interaction. See [3.6 FLS](https://docs.opensearch.org/3.6/security/access-control/field-level-security/) and [3.6 DLS](https://docs.opensearch.org/3.6/security/access-control/document-level-security/).

OpenSearch's role-combination behavior differs from Elasticsearch's. In particular, `plugins.security.dfm_empty_overrides_all` affects whether a role without DLS overrides a restricted role. Inspect the effective setting and test the actual identity. DLS does not constrain writes, so grant no write permissions to this reader.

Use the dedicated internal-user credential for this recipe. The earlier API-token example contains its own index permissions; assigning this role to a user does not establish that the token enforces equivalent restrictions. Any application token must independently pass the restricted-access checks below before use.

OpenSearch's adaptive DLS uses filter-level evaluation for terms-lookup queries. Filter-level DLS permits retrieval through `get`, `search`, `mget`, and `msearch`, and limits cross-cluster search. Review the application's exact queries and aggregations against these OpenSearch-specific restrictions. Do not substitute Elasticsearch's limitations or claim that FLS/DLS eliminates every inference channel. Prefer separate indices when stronger isolation is required. See [3.6 DLS modes, role composition, and limitations](https://docs.opensearch.org/3.6/security/access-control/document-level-security/).

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

## Storage encryption

**Both products: operating-system or storage-provider control, with no paid product feature tier required. Minimum versions within scope: Elasticsearch 8.0 and OpenSearch 3.0.** Elasticsearch guidance is pinned to 8.19; the cited OpenSearch encryption guidance is explicitly the 3.0 archive.

TLS and authentication do not encrypt files on an unencrypted node volume. Use host/block-storage encryption, such as Linux dm-crypt, independently of the search security configuration. Elasticsearch documents dm-crypt beneath its data path; OpenSearch assigns encryption at rest to the operating system. Elastic's subscription row is **"Encryption at rest support"**, not a native encryption switch or a licence requirement for using dm-crypt. See [Elasticsearch 8.19 storage guidance](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/tune-for-search-speed.html), [OpenSearch 3.0 encryption guidance](https://docs.opensearch.org/3.0/troubleshoot/#encryption-at-rest), and the [dated subscription matrix](https://www.elastic.co/pdf/subscriptions-2025-07-29.pdf).

Provision the encrypted volume before deploying data. Mount it at `/srv/search-data`, then select that directory in the respective `elasticsearch.yml` or `opensearch.yml`:

```yaml
path.data: /srv/search-data
```

**`path.data` selects a directory; it does not enable encryption.** For an existing deployment, plan the storage migration and recovery procedure before changing the path. Include logs, swap, and local snapshot storage in the encryption assessment. See [Elasticsearch 8.19 path settings](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/path-settings-overview.html) and [OpenSearch 3.6 configuration settings](https://docs.opensearch.org/3.6/install-and-configure/configuring-opensearch/configuration-system/).

Prevent startup from silently using an ordinary directory when the intended mount is unavailable. For a systemd deployment with `/srv/search-data` configured as a dedicated mount, add this service drop-in to the relevant Elasticsearch or OpenSearch unit:

```ini
[Unit]
RequiresMountsFor=/srv/search-data
AssertPathIsMountPoint=/srv/search-data
```

Reload systemd after installing the drop-in. The dependency requires the configured mount; the assertion rejects an ordinary directory. Neither proves that the mounted device is encrypted: verify the device chain separately. Other service managers need equivalent startup enforcement. See [systemd mount dependencies and assertions](https://man7.org/linux/man-pages/man5/systemd.unit.5.html).

## Snapshot repository encryption

**Elasticsearch: ordinary snapshot/restore is available with free Basic; the examples target 8.x and are pinned to 8.19. OpenSearch: free Apache-2.0; the S3 encryption syntax below requires 3.1 or later, with the changed default pinned to 3.8.0.** These are ordinary repositories, separate from paid Elasticsearch searchable-snapshot features. Provider storage and KMS charges are separate from product subscription tiers. See the [dated subscription matrix](https://www.elastic.co/pdf/subscriptions-2025-07-29.pdf) and [OpenSearch 3.1 repository API](https://docs.opensearch.org/3.1/api-reference/snapshots/create-repository/).

An encrypted node disk does not protect a remote snapshot repository. Server-side encryption also does not prevent a principal with the necessary object and key permissions from downloading decrypted contents.

Distinguish three properties:

- **Server-side encryption:** the storage provider encrypts stored objects and decrypts authorized reads.
- **Customer-managed keys:** the customer controls the encryption key and its permissions; this can still be server-side encryption.
- **Client-side encryption:** data is encrypted before upload, requiring a compatible reader and separately managed decryption keys.

Do not describe new AWS S3, GCS, or Azure objects as generally plaintext by default. AWS encrypts new S3 uploads automatically, GCS always applies server-side encryption, and Azure Storage encryption is enabled by default. Assess retained objects and required key ownership separately. See [AWS defaults](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html), [GCS encryption distinctions](https://docs.cloud.google.com/storage/docs/encryption), and [Azure Storage encryption](https://learn.microsoft.com/en-us/azure/storage/common/storage-service-encryption).

### Elasticsearch S3

**Free Basic; minimum version within this guide: 8.0; syntax pinned to 8.19.** After configuring repository credentials through the documented secure client settings, this requests SSE-S3:

```http
PUT /_snapshot/private_s3
{
  "type": "s3",
  "settings": {
    "bucket": "REPLACE_WITH_BUCKET",
    "server_side_encryption": true
  }
}
```

Elasticsearch 8.19's `server_side_encryption` defaults to `false`; `true` requests server-side AES256 encryption. Neither value enables client-side encryption. `false` does not mean AWS stores plaintext.

For customer-managed KMS encryption through the bucket default, omit this AES256 request, configure the intended bucket encryption/key policy, and verify the resulting object metadata. Do not add SSE-S3 blindly to a repository intended to use bucket-default KMS. See [8.19 S3 repository settings](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-s3.html).

### OpenSearch S3

**Free Apache-2.0; minimum version for this syntax: 3.1.** OpenSearch removed `server_side_encryption` in 3.1. Use `server_side_encryption_type`, which accepts `AES256`, `aws:kms`, or `bucket_default`. The default was `bucket_default` in 3.1 and changed to **`AES256` in 3.8**. See the [3.1 repository settings](https://docs.opensearch.org/3.1/api-reference/snapshots/create-repository/) and [3.8.0-tagged implementation](https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-s3/src/main/java/org/opensearch/repositories/s3/S3Repository.java).

For an explicit customer-managed KMS key:

```http
PUT /_snapshot/private_s3
{
  "type": "s3",
  "settings": {
    "bucket": "REPLACE_WITH_BUCKET",
    "server_side_encryption_type": "aws:kms",
    "server_side_encryption_kms_key_id": "REPLACE_WITH_KMS_KEY_ARN"
  }
}
```

Grant the repository principal the required object-store and KMS permissions. The ARN identifies a key; do not supply key material. This remains server-side encryption. To follow the bucket's encryption policy instead, explicitly select `bucket_default`, especially when upgrading to 3.8. Do not copy these OpenSearch settings into Elasticsearch. See [AWS SSE-KMS permissions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html).

### GCS, Azure, and repository integrity

**Elasticsearch: free Basic; minimum version within this guide: 8.0; declarations pinned to 8.19.** With the appropriate secure client credentials configured:

```http
PUT /_snapshot/private_gcs
{
  "type": "gcs",
  "settings": {
    "bucket": "REPLACE_WITH_BUCKET"
  }
}
```

```http
PUT /_snapshot/private_azure
{
  "type": "azure",
  "settings": {
    "container": "REPLACE_WITH_CONTAINER"
  }
}
```

The complete Elasticsearch 8.19 setting lists document no client-side-encryption switch for these repositories. Configure required customer-managed encryption through the provider's bucket/account policy and grant the required key access. GCS customer-supplied encryption keys are also a server-side mechanism. Azure account keys and SAS tokens authenticate requests; they do not establish client-side encryption. See [8.19 GCS settings](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-gcs.html), [8.19 Azure settings](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-azure.html), and [GCS encryption distinctions](https://docs.cloud.google.com/storage/docs/encryption).

**OpenSearch: free Apache-2.0; the cited repository workflow is version 3.6.** Follow OpenSearch's own plugin and credential instructions, including its Azure workflow. A tag-pinned review of OpenSearch's GCS/Azure client-side-encryption implementations remains outstanding. Their capability and minimum version are **not established here**; do not infer absence from Elasticsearch's settings or from failed source retrieval. See [OpenSearch 3.6 snapshot/repository guidance](https://docs.opensearch.org/3.6/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/).

Keep repository access private and keys recoverable for the required retention period. Do not rewrite files inside an active repository as an improvised encryption layer. Elasticsearch configuration-file backups are separate from snapshots and should be assessed for encryption; snapshots containing security feature state are sensitive too. See [8.19 backup guidance](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-take-snapshot.html) and [repository-integrity requirements](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshot-restore.html).

## Kibana and OpenSearch Dashboards

The UI is a separate service, normally on port **5601**. Securing cluster ports 9200/9300 does not configure browser-to-UI TLS.

### Kibana

**Free Basic; minimum version within this guide: Kibana 8.0; settings pinned to 8.19.** No Platinum/Enterprise subscription is required for browser-listener TLS. The cited versions establish support, not the first historical introduction of each setting.

Kibana defaults to HTTP on `localhost:5601`, with `server.ssl.enabled: false`. Its Docker image changes the host default to `0.0.0.0`. Check installation overrides, environment, and process arguments. See [8.19 Kibana settings](https://www.elastic.co/guide/en/kibana/8.19/settings.html) and [Docker defaults](https://www.elastic.co/guide/en/kibana/8.19/docker.html).

Merge into `kibana.yml`, preserving the existing server identity and authentication configuration:

```yaml
server.host: "127.0.0.1"
server.port: 5601
server.ssl.enabled: true
server.ssl.certificate: /etc/search-ui/tls/server.crt
server.ssl.key: /etc/search-ui/tls/server.key

elasticsearch.hosts: ["https://search.example.com:9200"]
elasticsearch.ssl.certificateAuthorities: ["/path/http_ca.crt"]
elasticsearch.ssl.verificationMode: full
```

The `server.ssl.*` settings protect incoming browser or proxy connections. The `elasticsearch.ssl.*` settings protect the separate Kibana-to-Elasticsearch connection. Keep full certificate and hostname verification on that connection. See [8.19 inbound and outbound TLS settings](https://www.elastic.co/guide/en/kibana/8.19/settings.html).

### OpenSearch Dashboards

**Free Apache-2.0; the TLS recipe is documented from at least OpenSearch Dashboards 2.19 and applies across this guide's 3.x scope; defaults are checked against 3.8.0.**

The 3.8.0 sample configuration identifies localhost, port 5601, and disabled server TLS. Check installation and container overrides separately. See the [3.8.0-tagged configuration](https://raw.githubusercontent.com/opensearch-project/OpenSearch-Dashboards/3.8.0/config/opensearch_dashboards.yml).

Merge into `opensearch_dashboards.yml`, preserving the existing server identity and authentication configuration:

```yaml
server.host: "127.0.0.1"
server.port: 5601
server.ssl.enabled: true
server.ssl.certificate: /etc/search-ui/tls/server.crt
server.ssl.key: /etc/search-ui/tls/server.key
opensearch_security.cookie.secure: true

opensearch.hosts: ["https://search.example.com:9200"]
opensearch.ssl.certificateAuthorities: ["/path/production-ca.pem"]
opensearch.ssl.verificationMode: full
```

`server.ssl.*` protects the UI listener; `opensearch_security.cookie.secure` restricts the security cookie to HTTPS. `opensearch.ssl.*` controls the separate connection to OpenSearch. Retain full certificate and hostname verification. See [Dashboards 3.6 TLS settings](https://docs.opensearch.org/3.6/install-and-configure/install-dashboards/tls/).

For either UI, loopback binding suits a proxy in the same network namespace. For direct private-network access, select the intended private interface and restrict network access. A proxy in another container does not share the UI container's loopback. Use certificates matching the hostname used by clients or the proxy, protect private-key files, and restart the UI after applying settings.

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
| Anonymous access | An anonymous read grant returns the permitted document. In Elasticsearch, an enabled anonymous identity lacking permission also returns `401` when `xpack.security.authc.anonymous.authz_exception: false`. | A `401` establishes rejection only for the tested endpoint, not that anonymous access is disabled. After restarting affected nodes, require confirmation that `xpack.security.authc.anonymous.roles` is absent from EVERY node's EFFECTIVE configuration. Removal of the roles setting disables anonymous access; there is no `xpack.security.authc.anonymous.enabled` switch. Also require the previously anonymously readable document control below. For OpenSearch, confirm the live `config.dynamic.http.anonymous_auth_enabled: false` setting. See [Elasticsearch anonymous access](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access), [Elasticsearch security settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings), and [OpenSearch anonymous authentication](https://docs.opensearch.org/latest/security/access-control/anonymous-authentication/). |
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

  # Reasoned: no target cluster or container runtime. Endpoint-specific check.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" "https://$1:$3/app-data/_doc/rbac-probe"

  # Effective configuration means what each restarted process actually loaded:
  # inspect its selected config directory, flattened and nested YAML, resolved
  # environment substitutions, and startup overrides. Record every node and
  # its restart. Inspecting one local file is insufficient. Settings omitted
  # from a filtered Nodes Info response are not proof of absence.
  # Require xpack.security.enabled: true and anonymous.roles absent everywhere.

  # Positive discriminator: use the URL-encoded path of a document previously
  # observed returning 200 and its expected contents WITHOUT credentials.
  # Establish that exposed-state control only in an isolated test cluster.
  # Substitute inside the quotes, retaining the leading slash.
  set -- "$1" "$2" "$3" '/REPLACE_WITH_KNOWN_DOCUMENT_PATH'
  case "${4-}" in
    *REPLACE_WITH_*|"") echo "known document path required; not probing"; exit 1 ;;
    /*) ;;
    *) echo "document path must start with /; not probing"; exit 1 ;;
  esac
  # Administrator must still retrieve that same document with 200 and its
  # expected contents; deletion or a different document invalidates the control.
  curl -q -g -sS --fail-with-body --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" --header @/path/admin.header "https://$1:$3$4" || exit 1
  # Reasoned: exposed anonymous read grant -> 200 and expected document;
  # roles removed and every node restarted -> 401. Other outcomes unresolved.
  # For OpenSearch, apply and read back anonymous_auth_enabled: false instead.
  # Without the recorded exposed-state success, this discriminator is unresolved.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    --cacert "$2" "https://$1:$3$4"

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
  # Requires python3. Generate and record a fresh harmless marker for each run.
  set -- "$1" "$2" "$3" "$(python3 -c 'import uuid; print(uuid.uuid4().hex)')"
  case "$4" in
    ""|*[!0-9a-f]*) echo "marker generation failed; not probing"; exit 1 ;;
  esac
  [ "${#4}" -eq 32 ] || { echo "invalid marker; not probing"; exit 1; }
  printf 'audit body marker=%s\n' "$4"
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  printf '{"query":{"term":{"audit_probe_marker":"%s"}}}\n' "$4" |
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --cacert "$2" --header @/path/audit-probe.header \
      --header 'Content-Type: application/json' --request POST \
      --data-binary @- "https://$1:$3/app-data/_search"
  date -u '+%Y-%m-%dT%H:%M:%SZ'
)
```

The administrative HTTPS control must return `200` and cluster JSON before interpreting the plaintext probe. With HTTP TLS enforced, plaintext must receive no HTTP response. Elasticsearch closes a plaintext connection to its HTTPS listener; OpenSearch's enabled REST TLS allows only HTTPS. Expect `http=000` with a reset or empty reply after connection. DNS failures, timeouts, or an unreachable service are inconclusive. Any actual HTTP status, including `401`, means that endpoint answered over plaintext and is a finding. See [Elasticsearch HTTP TLS settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings) and [OpenSearch REST TLS](https://docs.opensearch.org/latest/security/configuration/tls/).

For the audit check, expect `401` and require a matching NEW REST-layer Elasticsearch `authentication_failed` or OpenSearch `FAILED_LOGIN` event. Inspect the receiving node's new `CLUSTERNAME_audit.json` entries or the corresponding OpenSearch audit index and separately collected copy. Match the recorded time interval, `audit_probe` identity, POST method, and `/app-data/_search` path. Run probes separately so each event can be attributed to its request.

**Reasoned, not demonstrated:** no target cluster, audit collector, or eligible Elasticsearch audit license is available here. In an isolated test cluster, run the probe with request-body logging enabled, then disabled, generating a fresh marker each time. With Elasticsearch `xpack.security.audit.logfile.events.emit_request_body: true`, require that run's marker in the matching event's `request.body`. With OpenSearch `config.audit.log_request_body: true`, require it in `audit_request_body`. After setting the respective setting to `false`, require another matching new event, with its request-body field absent and that run's marker absent from the event. A bodyless request, a missing event, or absence of a marker without the enabled-state positive control cannot establish request-body exclusion. See [Elasticsearch request-body auditing](https://www.elastic.co/docs/deploy-manage/security/logging-configuration/auditing-search-queries), [Elasticsearch auditing settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/auding-settings), and [OpenSearch audit fields](https://docs.opensearch.org/latest/security/audit-logs/field-reference/).

Retain configuration readback: confirm Elasticsearch's effective `xpack.security.audit.logfile.events.emit_request_body: false`, accounting for transient and persistent cluster-setting overrides as well as each node's configuration. Repeat the OpenSearch audit configuration GET above and confirm `config.enabled: true`, `config.audit.enable_rest: true`, `config.audit.log_request_body: false`, and `config.audit.exclude_sensitive_headers: true`. Check that sensitive headers, including the Authorization value sent from the header file, are absent from the matching events and their collected copies in both test states. Header exclusion and body exclusion are separate checks. Restore and read back body logging as disabled after the isolated positive-control test. See [OpenSearch body logging](https://docs.opensearch.org/latest/security/audit-logs/index/) and [audit configuration fields](https://docs.opensearch.org/latest/security/api/audit/update-audit-configuration/).

Missing events leave the audit check unresolved until collection delay, filtering, licensing, and configuration have been checked. A `401` alone proves neither audit delivery nor body exclusion.

On the node itself, inspect listeners:

```bash
# Reasoned: no access to the target node. Run ON that node; substitute actual ports.
ss -tlnp 'sport = :9200'
ss -tlnp 'sport = :9300'
```

These use `ss`'s own port filter, avoiding accidental PID matches. For Elasticsearch, HTTP defaults to the range `9200-9300` and transport to `9300-9400`; each binds an available port. Inspect the actual ports used by either product. Expect loopback or deliberate private listeners. An unexpected public or wildcard listener is a finding to review against the network controls; no output is inconclusive until the running process and its actual ports are located.

### Residual-control checks

These additional deployment checks are **REASONED, not demonstrated**. No target Elasticsearch/OpenSearch cluster, eligible Elasticsearch FLS/DLS licence, target storage, provider repository access, or running UI with deployed certificates is available in the authoring environment. Demonstration remains part of `ES-OS-VERIFY-1`.

Use isolated test deployments for exposed-state fixtures. Substitute values inside single quotes and paste whole shell blocks. Values containing a literal apostrophe need proper shell quoting. Keep credentials in the protected header files described above, with tracing disabled. The following blocks assume the shell's normal builtins.

For the REST request tables below, save each JSON body in a protected file. Run this block once per request, setting the method, path, and body-file arguments. Use `/dev/null` for a request with no body. Select the administrator or application header file as directed:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SEARCH_HOST' 'REPLACE_WITH_CA_FILE' '9200' 'REPLACE_WITH_HEADER_FILE' 'GET' '/REPLACE_WITH_REQUEST_PATH' '/dev/null'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 7 ] || { echo "set host, CA, port, header file, method, path, and body file; not probing"; exit 1; }
  case "$1|$2|$3|$4|$5|$6|$7" in
    *REPLACE_WITH_*|*example.com*) echo "substitute your deployment; not probing"; exit 1 ;;
  esac
  case "$1" in ""|*[!A-Za-z0-9.-]*) echo "use a DNS hostname or IPv4 address; not probing"; exit 1 ;; esac
  case "$3" in ""|*[!0-9]*) echo "numeric port required; not probing"; exit 1 ;; esac
  [ "$3" -ge 1 ] && [ "$3" -le 65535 ] || exit 1
  [ -r "$2" ] && [ -r "$4" ] && [ -r "$7" ] || { echo "readable CA, header, and body files required"; exit 1; }
  case "$5" in GET|POST|PUT) ;; *) echo "unsupported method; not probing"; exit 1 ;; esac
  case "$6" in /*) ;; *) echo "request path must start with /; not probing"; exit 1 ;; esac
  # REASONED: no target cluster, eligible ES licence, or repository access.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 120 \
    --cacert "$2" --header "@$4" --header 'Content-Type: application/json' \
    --request "$5" --data-binary "@$7" \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
    "https://$1:$3$6"
)
```

Judge the HTTP status and response contents, not the shell's final status alone. A transport failure or `401` is not evidence of correct field/document restrictions.

### Verify field and document restrictions

**REASONED, not demonstrated:** requires both live products and an eligible Elasticsearch FLS/DLS licence.

In an isolated cluster where `app-data` does not already exist, use the administrator header and REST block to create this harmless fixture:

| Method | Path | JSON body |
| --- | --- | --- |
| `PUT` | `/app-data` | `{"mappings":{"properties":{"tenant_id":{"type":"keyword"},"title":{"type":"keyword"},"category":{"type":"keyword"},"secret":{"type":"keyword"}}}}` |
| `PUT` | `/app-data/_doc/fls-a?refresh=true` | `{"tenant_id":"tenant-a","title":"A","category":"public-a","secret":"fixture-secret-a"}` |
| `PUT` | `/app-data/_doc/fls-b?refresh=true` | `{"tenant_id":"tenant-b","title":"B","category":"public-b","secret":"fixture-secret-b"}` |

Require successful creation responses. These markers are deliberately harmless, not real secrets. See the [Elasticsearch 8.19 create-index API](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/indices-create-index.html), [index-document API](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/docs-index_.html), [OpenSearch 3.6 create-index API](https://docs.opensearch.org/3.6/api-reference/index-apis/create-index/), and [index-document API](https://docs.opensearch.org/3.6/api-reference/document-apis/index-document/).

Run the following requests first as an identity with the existing unrestricted `app_reader` role, then as the restricted application identity:

| Method | Path | JSON body |
| --- | --- | --- |
| `POST` | `/app-data/_search` | `{"query":{"match_all":{}},"fields":["tenant_id","title","category","secret"]}` |
| `GET` | `/app-data/_doc/fls-a` | No body |
| `GET` | `/app-data/_doc/fls-b` | No body |
| `POST` | `/app-data/_search` | `{"size":0,"aggs":{"values":{"terms":{"field":"secret"}}}}` |
| `POST` | `/app-data/_search` | `{"size":0,"aggs":{"values":{"terms":{"field":"category"}}}}` |

The unrestricted control must retrieve both documents and both secret markers, including the secret aggregation buckets. With the restricted identity:

- Search returns only `fls-a`; neither `_source` nor requested `fields` contains a secret marker.
- Direct retrieval returns `fls-a` without `secret`, while `fls-b` is not retrievable.
- The secret aggregation discloses neither secret value. Record the exact response; a failed query alone does not demonstrate working FLS.
- The allowed `category` aggregation succeeds and returns `public-a`, excluding `public-b`.
- The administrator still retrieves `fls-b` and its original marker, ruling out a missing fixture.

A `401`, unavailable index, or broken allowed-field query leaves the result unresolved. Repeat with the actual application credential, including any API key intended for production, and retain its effective permission configuration.

These checks exercise ordinary retrieval and aggregations; they do not prove absence of statistical inference channels. The distinctions follow [Elasticsearch 8.19 FLS](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-level-security.html), [DLS](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/document-level-security.html), [search syntax](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/search-search.html), [OpenSearch 3.6 FLS](https://docs.opensearch.org/3.6/security/access-control/field-level-security/), [DLS](https://docs.opensearch.org/3.6/security/access-control/document-level-security/), and [search syntax](https://docs.opensearch.org/3.6/api-reference/search-apis/search/).

### Verify storage encryption

**REASONED, not demonstrated:** these inspections do not require a running cluster, but target-node and target-storage access are unavailable here.

Run on the node, with sufficient permission to inspect the intended dm-crypt mapping:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DATA_PATH' 'REPLACE_WITH_CRYPT_MAPPING'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "set data path and mapping name; not probing"; exit 1; }
  case "$1|$2" in *REPLACE_WITH_*) echo "substitute your storage; not probing"; exit 1 ;; esac
  case "$1" in /*) ;; *) echo "absolute data path required"; exit 1 ;; esac
  case "$2" in ""|-*|*/*) echo "mapping name required"; exit 1 ;; esac
  [ -d "$1" ] || { echo "data directory missing; unresolved"; exit 1; }
  # REASONED: no access to the target node or encrypted storage.
  findmnt -T "$1" || exit 1
  lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINTS || exit 1
  cryptsetup status "$2"
)
```

Compare the exposed unencrypted volume with the fixed volume. Require the actual data path's mount/device chain to traverse the intended encrypted mapping. An unrelated active mapping is insufficient. For provider-managed volume encryption, inspect the actual attached volume's encryption and key metadata instead; the guest may not expose a dm-crypt device. Successful reads through an unlocked filesystem neither prove nor disprove encryption at rest. See [findmnt](https://man7.org/linux/man-pages/man8/findmnt.8.html), [lsblk](https://man7.org/linux/man-pages/man8/lsblk.8.html), and [cryptsetup status](https://man7.org/linux/man-pages/man8/cryptsetup-status.8.html).

**REASONED, not demonstrated:** in an isolated systemd fixture, stop the service and make the required test mount unavailable, including preventing automatic remount. Run the following with the test service unit. Do not perform this fault injection on production storage.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SERVICE_UNIT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "set exactly one service unit; not probing"; exit 1; }
  case "$1" in ""|-*|*REPLACE_WITH_*|*/*) echo "substitute the test service unit"; exit 1 ;; esac
  # REASONED: isolated target service and unavailable-mount fixture absent.
  systemctl start "$1"
  systemctl --no-pager status "$1"
)
```

Without startup enforcement, an otherwise valid fixture may start on the ordinary underlying directory. With the mount dependency/assertion, require the start job to fail specifically because the mount is unavailable, with no search process writing into that directory. Restore the intended encrypted mount and require successful startup as the positive control. Permission errors or unrelated startup failures are inconclusive. See [systemd assertions](https://man7.org/linux/man-pages/man5/systemd.unit.5.html) and [systemctl](https://man7.org/linux/man-pages/man1/systemctl.1.html).

### Verify snapshot encryption and key isolation

**REASONED, not demonstrated:** requires a live cluster, configured repository, provider access, and controlled test identities.

Using the administrator header and REST block, snapshot only the harmless fixture. Select an unused snapshot name and an unused restore index; the names below are for the isolated fixture.

| Method | Path | JSON body |
| --- | --- | --- |
| `PUT` | `/_snapshot/private_s3/encryption-probe?wait_for_completion=true` | `{"indices":"app-data","include_global_state":false}` |
| `GET` | `/_snapshot/private_s3/encryption-probe` | No body |
| `POST` | `/_snapshot/private_s3/encryption-probe/_restore?wait_for_completion=true` | `{"indices":"app-data","include_global_state":false,"include_aliases":false,"rename_pattern":"app-data","rename_replacement":"restored-app-data"}` |
| `GET` | `/restored-app-data/_doc/fls-a` | No body |
| `GET` | `/restored-app-data/_doc/fls-b` | No body |

Require snapshot success, completed restore, and both original fixture documents. A client timeout does not establish failure or success; inspect operation state before retrying. The explicit index selection and `include_global_state: false` avoid restoring security state in this fixture. See [Elasticsearch 8.19 snapshot creation](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-take-snapshot.html), [restore](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-restore-snapshot.html), and [OpenSearch 3.6 snapshot/restore](https://docs.opensearch.org/3.6/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/).

For AWS S3, identify actual newly written repository objects through the provider inventory or console. With AWS CLI v2 and preconfigured profiles, inspect a known object and attempt a download:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_AWS_PROFILE' 'REPLACE_WITH_BUCKET' 'REPLACE_WITH_OBJECT_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "set profile, bucket, and object key; not probing"; exit 1; }
  case "$1|$2|$3" in *REPLACE_WITH_*) echo "substitute the test object and identity"; exit 1 ;; esac
  [ -n "$1" ] && [ -n "$2" ] && [ -n "$3" ] || exit 1
  # REASONED: no repository, provider credentials, or KMS test identities.
  aws --profile "$1" --no-cli-pager s3api head-object --bucket "$2" --key "$3"
  aws --profile "$1" --no-cli-pager s3api get-object --bucket "$2" --key "$3" /dev/null
)
```

The profile name and object key are identifiers, not credentials or encryption-key material. Load authentication through the protected AWS credential mechanism. See [HeadObject](https://docs.aws.amazon.com/cli/latest/reference/s3api/head-object.html) and [GetObject](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html).

Require the following distinctions:

| Check | Exposed or misconfigured outcome | Fixed outcome |
| --- | --- | --- |
| Encryption/key policy | Objects use an unintended mode or key, even if provider default encryption is active. | Actual object metadata matches the required mode; for KMS, `SSEKMSKeyId` identifies the intended customer-managed key. |
| Repository access | A deliberately overprivileged test principal downloads the known object. | After removing that access, the same principal cannot download it, while the authorized principal still can. |
| KMS isolation | The controlled principal can decrypt the known KMS object. | Removing the necessary KMS permission causes the same operation to fail for that reason, while its S3 read permission remains and a permitted identity succeeds. |

Use provider authorization/audit evidence to distinguish KMS denial from S3 denial, missing objects, expired credentials, or network errors. If caching or another effective grant prevents a clean KMS negative control, leave that check unresolved.

Inspect retained objects as well as newly written ones; changing a default does not prove old objects were rewritten. For GCS/Azure repositories, retain equivalent object-encryption/key metadata and authorized/unauthorized download evidence from those providers. A successful repository `_verify` request establishes neither encryption mode nor key isolation. Server-side-encrypted downloads normally return decrypted contents; this is not a client-side-encryption test. See [AWS encryption behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html) and [SSE-KMS authorization](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html).

### Verify the separate UI listener

**REASONED, not demonstrated:** requires Kibana or OpenSearch Dashboards, deployed certificates, and authorized/prohibited network test paths.

In an isolated exposed fixture, record an HTTP login page or redirect on the actual UI port. After applying the fixed configuration, run:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_HOST' 'REPLACE_WITH_UI_CA_FILE' '5601'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "set UI host, CA file, and port; not probing"; exit 1; }
  case "$1|$2|$3" in *REPLACE_WITH_*|*example.com*) echo "substitute your UI deployment"; exit 1 ;; esac
  case "$1" in ""|*[!A-Za-z0-9.-]*) echo "use a DNS hostname or IPv4 address"; exit 1 ;; esac
  case "$3" in ""|*[!0-9]*) echo "numeric UI port required"; exit 1 ;; esac
  [ "$3" -ge 1 ] && [ "$3" -le 65535 ] || exit 1
  [ -r "$2" ] || { echo "readable UI CA file required"; exit 1; }
  # REASONED: no running UI, deployed certificates, or network test paths.
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --cacert "$2" --output /dev/null --dump-header - \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1:$3/"
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    --output /dev/null --dump-header - \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:$3/"
)
```

On the authorized path, require successful CA-validated HTTPS with the expected UI response. Plaintext on that TLS listener must not serve the UI; a connection close or explicit protocol rejection can demonstrate rejection. A timeout or DNS failure alone cannot.

For loopback deployments, test locally using a certificate hostname that resolves to the UI's loopback listener. Separately test the real deployment address from the prohibited network, not that client's own loopback. Require the prohibited connection to fail while the authorized path still works, and retain network-control evidence.

On the UI host, inspect the actual listener:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "set exactly one UI port; not probing"; exit 1; }
  case "$1" in ""|*[!0-9]*) echo "substitute the numeric UI port"; exit 1 ;; esac
  [ "$1" -ge 1 ] && [ "$1" -le 65535 ] || exit 1
  # REASONED: no access to the target UI host. Run on that host.
  ss -tlnp "sport = :$1"
)
```

Require the intended loopback/private bind. Inspect container port publication, selected configuration, environment, and process arguments too. Confirm the UI-to-cluster connection still uses HTTPS and full verification; successful browser TLS alone does not establish that. For Dashboards, confirm `opensearch_security.cookie.secure: true` and the Secure attribute on its session cookie. See [Kibana 8.19 settings](https://www.elastic.co/guide/en/kibana/8.19/settings.html), [Kibana Docker overrides](https://www.elastic.co/guide/en/kibana/8.19/docker.html), and [Dashboards 3.6 TLS settings](https://docs.opensearch.org/3.6/install-and-configure/install-dashboards/tls/).

An unauthenticated `GET /` returning cluster JSON is the classic finding; so is `_cat/indices` listing your data to the world.

| Demonstration backlog | Required work | Status |
| --- | --- | --- |
| ES-OS-VERIFY-1 | Demonstrate every check against exposed and fixed states in isolated Elasticsearch 8.x and OpenSearch test clusters, including OpenSearch 3.7+ keys and an eligible Elasticsearch audit license. Include the Elasticsearch counterexample: anonymous roles remain configured, authz_exception is false, and the anonymous identity lacks permission for both / and app-data, so both probes return 401 while a document in another permitted index remains anonymously readable with 200. Record that document and its contents, remove anonymous.roles, restart affected nodes, confirm its absence from every node's effective configuration, and require the same document request to return 401 while an administrator still retrieves it with 200. Also demonstrate fresh failed-authentication audit events with a unique harmless JSON marker present when body logging is enabled and absent when disabled; retain configuration-readback and sensitive-header-exclusion checks. Record versions, effective configuration, HTTP responses, listener output, and matching newly collected audit events. | Open: target clusters, container runtime, and audit collection are unavailable in the authoring environment. |
| ES-OS-VERIFY-1, FLS/DLS extension | Demonstrate the two-tenant fixture on Elasticsearch 8.19 with an eligible Platinum/Enterprise licence and OpenSearch 3.8.0. Record unrestricted and restricted search, direct GET, `_source`, requested-field, secret-aggregation, and allowed-aggregation results. Retain administrator fixture controls, effective roles/settings, and actual application-credential results. Record documented inference limitations separately from ordinary retrieval results. | Open: live clusters and an eligible Elasticsearch FLS/DLS licence are unavailable. |
| ES-OS-VERIFY-1, storage extension | Record actual data-path mount/device chains before and after encryption. Demonstrate refusal to start when the required encrypted mount is unavailable and successful startup after restoration. Cover logs, swap, and local snapshot storage; use provider volume/key metadata where applicable. | Open: target-node, target-storage, and service-manager fixture access are unavailable. |
| ES-OS-VERIFY-1, snapshot extension | On both products, take and restore a harmless snapshot. Record new and retained object encryption/key metadata, authorized and unauthorized object downloads, and a KMS-dependent denial with a working positive control. Record the OpenSearch version and explicit S3 encryption settings. Separately complete tag-pinned inspection of OpenSearch GCS/Azure client-side-encryption capability before asserting support or absence. | Open: clusters, repositories, provider/KMS test identities, and the identified implementation evidence are unavailable. |
| ES-OS-VERIFY-1, UI extension | Demonstrate exposed HTTP and fixed CA-validated HTTPS for Kibana 8.19 and Dashboards 3.8.0. Record plaintext rejection, listener addresses, container overrides/publication, prohibited-network denial with an authorized positive control, backend full verification, and the Dashboards Secure cookie. | Open: UI processes, deployed certificates, target hosts, and network test paths are unavailable. |

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
- OpenSearch Security Apache-2.0 license: https://github.com/opensearch-project/security/blob/4ba3cc0e2ebec61b726b227fdf51e55f4a502182/LICENSE.txt
- OpenSearch demo security configuration and initial admin password: https://docs.opensearch.org/latest/security/configuration/demo-configuration/
- OpenSearch shipped demo accounts: https://github.com/opensearch-project/security/blob/03a224d16045a8f561e2d7d84b8765c95309524c/config/internal_users.yml
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
- Elastic distribution/source licensing: https://www.elastic.co/pricing/faq/licensing
- Basic security introduction and FLS/DLS exclusion: https://www.elastic.co/blog/security-for-elasticsearch-is-now-free
- Dated subscription matrix: https://www.elastic.co/pdf/subscriptions-2025-07-29.pdf
- Current subscription terms and Platinum availability: https://www.elastic.co/subscriptions
- Elasticsearch 8.19 role API: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-api-put-role.html
- Elasticsearch 8.19 access control and role composition: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-and-document-access-control.html
- Elasticsearch 8.19 FLS: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-level-security.html
- Elasticsearch 8.19 DLS: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/document-level-security.html
- Elasticsearch 8.19 security limitations: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-limitations.html
- OpenSearch Security licence, tag 3.8.0.0: https://raw.githubusercontent.com/opensearch-project/security/3.8.0.0/LICENSE.txt
- OpenSearch 3.6 Security API and role schema: https://docs.opensearch.org/3.6/security/access-control/api/
- OpenSearch 1.0 DLS archive: https://docs.opensearch.org/1.0/security-plugin/access-control/document-level-security/
- OpenSearch 3.6 FLS: https://docs.opensearch.org/3.6/security/access-control/field-level-security/
- OpenSearch 3.6 DLS, modes, and role composition: https://docs.opensearch.org/3.6/security/access-control/document-level-security/
- Elasticsearch 8.19 dm-crypt-backed storage: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/tune-for-search-speed.html
- Elasticsearch 8.19 path settings: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/path-settings-overview.html
- OpenSearch 3.6 configuration settings (path.data): https://docs.opensearch.org/3.6/install-and-configure/configuring-opensearch/configuration-system/
- OpenSearch 3.0 encryption-at-rest guidance: https://docs.opensearch.org/3.0/troubleshoot/#encryption-at-rest
- Elasticsearch 8.19 S3 repository: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-s3.html
- OpenSearch 3.1 repository API and encryption-setting change: https://docs.opensearch.org/3.1/api-reference/snapshots/create-repository/
- OpenSearch S3 implementation, tag 3.8.0: https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-s3/src/main/java/org/opensearch/repositories/s3/S3Repository.java
- Elasticsearch 8.19 GCS repository: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-gcs.html
- Elasticsearch 8.19 Azure repository: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-azure.html
- OpenSearch 3.6 snapshot/repository workflow: https://docs.opensearch.org/3.6/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/
- AWS S3 default encryption and retained objects: https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html
- AWS SSE-KMS permissions: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html
- GCS encryption distinctions: https://docs.cloud.google.com/storage/docs/encryption
- Azure Storage encryption: https://learn.microsoft.com/en-us/azure/storage/common/storage-service-encryption
- Elasticsearch 8.19 snapshot creation and configuration backups: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-take-snapshot.html
- Elasticsearch 8.19 repository integrity: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshot-restore.html
- Elasticsearch 8.19 restore: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-restore-snapshot.html
- Kibana 8.19 settings: https://www.elastic.co/guide/en/kibana/8.19/settings.html
- Kibana 8.19 Docker defaults and overrides: https://www.elastic.co/guide/en/kibana/8.19/docker.html
- Dashboards configuration, tag 3.8.0: https://raw.githubusercontent.com/opensearch-project/OpenSearch-Dashboards/3.8.0/config/opensearch_dashboards.yml
- Dashboards 3.6 TLS and cookie settings: https://docs.opensearch.org/3.6/install-and-configure/install-dashboards/tls/
- Elasticsearch 8.19 create index: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/indices-create-index.html
- Elasticsearch 8.19 index document: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/docs-index_.html
- Elasticsearch 8.19 search: https://www.elastic.co/guide/en/elasticsearch/reference/8.19/search-search.html
- OpenSearch 3.6 create index: https://docs.opensearch.org/3.6/api-reference/index-apis/create-index/
- OpenSearch 3.6 index document: https://docs.opensearch.org/3.6/api-reference/document-apis/index-document/
- OpenSearch 3.6 search: https://docs.opensearch.org/3.6/api-reference/search-apis/search/
- AWS CLI HeadObject: https://docs.aws.amazon.com/cli/latest/reference/s3api/head-object.html
- AWS CLI GetObject: https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html
- Mount inspection: https://man7.org/linux/man-pages/man8/findmnt.8.html
- Block-device inspection: https://man7.org/linux/man-pages/man8/lsblk.8.html
- Encryption-mapping inspection: https://man7.org/linux/man-pages/man8/cryptsetup-status.8.html
- systemd mount dependencies and assertions: https://man7.org/linux/man-pages/man5/systemd.unit.5.html
- systemd start/status commands: https://man7.org/linux/man-pages/man1/systemctl.1.html
- curl options and file input: https://curl.se/docs/manpage.html
- Listener inspection: https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html
