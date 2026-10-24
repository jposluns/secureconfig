# Elasticsearch and OpenSearch: keep security switched on

Elasticsearch and OpenSearch are search engines that index documents and logs for searching. This guide helps your AI assistant keep their security switched on, including TLS and authentication, scoped roles, anonymous access off, CORS off unless a browser needs it, and audit logging on OpenSearch or paid Elasticsearch tiers.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/elasticsearch.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Elasticsearch API 8.x, Elasticsearch reference 8.19, Elasticsearch listener source 8.19.22 and 9.5.4, OpenSearch reference 3.6, OpenSearch S3 reference 3.1, OpenSearch S3 source 3.8.0, OpenSearch GCS source 3.8.0, and OpenSearch Azure source 3.8.0, plus 7 more recorded bases; 3 further sources are pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-10-22; documentation checked September 2026. The guide records 82 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Open Elasticsearch instances produced some of the largest data leaks on record. Modern versions ship secure; the failure mode today is deliberately switching protection off to make an error message go away.

## Elasticsearch (8.0 and later)

The examples below target self-managed Elasticsearch 8.x. TLS, native users, index-scoped RBAC, REST API keys, anonymous-access controls, and CORS settings are available with **free Basic**. LDAP authentication and audit logging require **paid Platinum/Enterprise**. At the time of writing, self-managed Platinum is available to existing customers only. See the [subscription matrix](https://www.elastic.co/subscriptions).

- A fresh install auto-configures security on first start when it runs: authentication is enabled, TLS is set up for HTTP and transport, and a password is generated for the `elastic` superuser. Keep all of it. Auto-configuration is SKIPPED if startup output is redirected, if the config directory is not writable, or if certain security or discovery settings already exist (single-node discovery and a `cluster.initial_master_nodes` naming only the current node are exempted); Debian and RPM packages do not print the password (reset it with `elasticsearch-reset-password -u elastic`). Confirm security actually came up rather than assuming it did. See [automatic security setup](https://www.elastic.co/docs/deploy-manage/security/self-auto-setup).
- Never set `xpack.security.enabled: false`, and never expose a node where TLS (`xpack.security.http.ssl.enabled`) has been turned off. If a client cannot connect, fix the client's CA trust ([self-signed.md](self-signed.md)) or issue a real certificate ([free-certificates.md](free-certificates.md)); do not remove the lock.
- Listener defaults are source-checked at Elasticsearch **8.19.22 and 9.5.4**. `network.host` defaults to `_local_`: loopback addresses on interfaces that are up, including IPv4 and IPv6 where available. `_local:ipv4_` and `_local:ipv6_` restrict the family. HTTP and transport use the network settings unless their own host/bind/publish settings override them: at both versions the HTTP server binds `http.bind_host` (itself defaulting to `http.host`) or, when that is empty, `network.bind_host`, and each transport profile binds its own bind host or, when that is empty, `network.bind_host` (pinned Sources below, with the [networking settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings) reference). Read the effective configuration and route remote access through a private network, VPN or tunnel, with TLS everywhere.
- When security auto-configuration reaches its configuration-writing step, it adds `http.host: 0.0.0.0` only if none of `http.host`, `http.bind_host`, `http.publish_host`, `network.host`, `network.bind_host`, or `network.publish_host` has a value. This condition applies in enrollment mode too. The standard archive/package configuration leaves these unset, so an eligible initial auto-configuration widens HTTP. For transport, the analogous guard checks `transport.host`, `transport.bind_host`, `transport.publish_host`, and the same three network settings. It writes a commented `#transport.host: 0.0.0.0` for a new cluster; enrollment makes that line active only if a discovered transport publish address resolves to a non-loopback address absent from the local host. It does not overwrite existing address settings. See the pinned `AutoConfigureNode` Sources below.
- The official Docker images (8.19.22, 9.4.6 and 9.5.3 at the pinned library commit) ship an `elasticsearch.yml` that sets `network.host: 0.0.0.0`, which Elastic's networking settings reference describes as "The addresses of all available network interfaces". So unless an environment variable, a `-E` setting in the container command after a first argument of `eswrapper` or a path whose last component is `elasticsearch` (the entrypoint drops that argument and passes the rest to the server; a different first argument runs as its own command), or a bind-mounted configuration file overrides it (for example with `transport.host`), transport (9300) listens on them as well as HTTP (9200). Keep security auto-configuration, which sets up transport TLS, and keep 9300 unreachable: do not publish it (`-P` would, because the image EXPOSEs it), do not run the container with host networking, and do not share its network with untrusted containers.

The Elasticsearch Docker source configurations at **8.19.22 and 9.5.4** also explicitly set `network.host: 0.0.0.0`. With that shipped setting present, both auto-configuration address guards above are false: the wildcard comes from the image configuration, without needing an added `http.host` or `transport.host` line. See the pinned Docker configuration Sources below.

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
     https://search.example.com:9200/_security/role/app_reader \
     --data-binary '{ "cluster": ["manage_own_api_key"], "indices": [{"names": ["app-data"], "privileges": ["read"]}] }'
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
     https://search.example.com:9200/_security/api_key \
     --data-binary '{ "name": "app-reader", "expiration": "1d", "role_descriptors": { "app_read": { "cluster": [], "indices": [{"names": ["app-data"], "privileges": ["read"]}] } } }'
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
     https://search.example.com:9200/_plugins/_security/api/roles/app_reader \
     --data-binary '{ "cluster_permissions": [], "index_permissions": [{"index_patterns": ["app-data"], "allowed_actions": ["read"]}], "tenant_permissions": [] }'
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
     https://search.example.com:9200/_plugins/_security/api/apitokens \
     --data-binary '{ "name": "app-reader", "cluster_permissions": [], "index_permissions": [{"index_pattern": ["app-data"], "allowed_actions": ["read"]}], "duration_seconds": 86400 }'
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

**OpenSearch: free Apache-2.0; the cited repository workflow is version 3.6.** Follow OpenSearch's own plugin and credential instructions, including its Azure workflow. This guide's review of the OpenSearch 3.8.0 GCS and Azure plugin-specific settings, blob upload and client construction found no plugin-specific client-side-encryption setting. OpenSearch core accepts repository `crypto_settings` and wraps the non-server-side-encryption blob store in client-side `EncryptedBlobStore` when repository crypto metadata is supplied; its encrypted container encrypts writes before forwarding them. The cited common provider and GCS/Azure `createBlobStore` methods show a path to both repository types, and Azure points to repository-level encryption settings while rejecting per-object `CryptoMetadata`. This guide's assessment is that end-to-end applicability and live encryption behaviour for either type remain **not established here**. The core path requires `key_provider_name` and `key_provider_type` and a registered key-provider plugin of that type; the cited tree includes an `aws-kms` provider. Available providers in a deployment, a universal minimum version for GCS/Azure client-side encryption, and behaviour in unchecked releases remain **not established here**.

This guide's assessment is that **the checked range for the GCS/Azure client-side-encryption reading is 2.10.0 to 3.9.0, and the wrap moves into `BlobStoreProvider` at 3.4.0**. The range starts at 2.10.0, based on the pinned 2.10.0 and 3.0.0 source methods, the 2.10.0 release notes listing the core crypto library, encryption-sdk and crypto-kms plugin, and the pinned 2.9.0 directory listings without the corresponding crypto packages, EncryptedBlobStore or crypto-kms entry. As a source reading without an OpenSearch run, git tree listings at each of the 41 release tags from 1.0.0 to 2.9.0 contain no `EncryptedBlobStore`, `CryptoSettings` or `crypto-kms` path, and at 2.9.0 `BlobStoreRepository.blobStore()` returns the `createBlobStore` result unwrapped, `PutRepositoryRequest` parses only `type` and `settings`, and `RepositoryMetadata` holds no crypto field. This guide then read `BlobStoreRepository`, `MeteredBlobStoreRepository`, `EncryptedBlobStore`, `GoogleCloudStorageRepository` and `AzureRepository` at each of the 31 release tags from 2.10.0 to 3.9.0; other files, including `CryptoSettings`, were read only at the tags their Sources entries name, and a git blob ID comparison extends a reading only where it says so. `CryptoSettings.validate()` is cited at 2.10.0, 3.0.0 and 3.8.0, and `CryptoSettings.java` has the cited 2.10.0 file's git blob ID at 2.11.0 and 2.11.1 and the cited 3.0.0 and 3.8.0 files' at every tag from 2.12.0 to 3.9.0, so `validate()` requires `key_provider_name` and `key_provider_type` at all 31 checked tags. At all 25 tags from 2.10.0 to 3.3.2, `BlobStoreRepository.blobStore()` has the same body: it calls `createBlobStore` and wraps the result in `EncryptedBlobStore` when `metadata.cryptoMetadata()` is non-null. From 3.4.0 to 3.9.0, `blobStore()` returns `blobStore(false)`, which creates a `BlobStoreProvider` and returns that provider's `blobStore(serverSideEncryptionEnabled)`, and `BlobStoreRepository` no longer constructs `EncryptedBlobStore` itself. The provider's `createBlobStore` wraps the repository's `createBlobStore` result in `EncryptedBlobStore` when server-side encryption is off, as `blobStore(false)` requests, and `metadata.cryptoMetadata()` is non-null. This guide read `BlobStoreProvider` at 3.4.0, 3.8.0 and 3.9.0, and the 3.5.0, 3.6.0 and 3.7.0 files have 3.4.0's git blob ID, so the wrap holds in source at every tag from 3.4.0 to 3.9.0. No OpenSearch release tag after 3.9.0 existed when the tag list was checked on 2026-10-22; behaviour in later releases, repository code at release tags before 2.10.0 beyond the absent `EncryptedBlobStore`, `CryptoSettings` and `crypto-kms` paths (that code was read only at 2.9.0), and a universal minimum for deployed GCS/Azure encryption remain **not established here**.

At both **2.10.0 and 3.0.0**, GCS and Azure extend `MeteredBlobStoreRepository` and override `createBlobStore` to return their respective stores; `BlobStoreRepository.blobStore()` calls `createBlobStore` and wraps the result in `EncryptedBlobStore` when `metadata.cryptoMetadata()` is non-null. At both versions the pinned `MeteredBlobStoreRepository` is an abstract class extending `BlobStoreRepository` that declares neither `blobStore()` nor `createBlobStore`; it has no `@Override` method at 2.10.0, and at 3.0.0 overrides only `reload`, which calls `super.reload`. At both versions the pinned `GoogleCloudStorageRepository` and `AzureRepository` class bodies declare no `blobStore()` method; `AzureRepository` overrides `getBlobStore()` only to return `super.getBlobStore()`. This guide infers from those files that the inherited `blobStore()` dispatch reaches the GCS and Azure `createBlobStore` overrides, so both repository types reach the wrap in source at those versions; deployed client-side encryption and live encryption behaviour remain **not established here**. The pinned `CryptoSettings.validate()` methods at both versions require `key_provider_name` and `key_provider_type`; source settings and a wrapper do not establish installed providers or live encryption behaviour. Across all 31 checked tags from 2.10.0 to 3.9.0, `MeteredBlobStoreRepository`, `GoogleCloudStorageRepository` and `AzureRepository` declare no `blobStore()` method, `MeteredBlobStoreRepository` declares no `createBlobStore` and from 2.11.0 has `reload`, which calls `super.reload`, as its only `@Override` method, and `AzureRepository` overrides `getBlobStore()` only to return `super.getBlobStore()`. From 3.7.0 to 3.9.0, both plugin classes also override `getNativeStore()` to return a native object store, which their source comments describe as a native (Rust) store created during construction if a native provider is available; whether that path bypasses the `EncryptedBlobStore` wrap, and whether a deployment uses it, are **not established here**. As a source reading without a run, the 3.7.0 and 3.9.0 `BlobStoreRepository` files contain no native-store reference, and at 3.9.0 a search of the tag for `getNativeStore` finds `IndexService` as its only non-test caller, which resolves the native store of a warm index's remote store repository when the writable-warm feature flag is enabled, the index is warm, its pluggable data format is enabled and a format-aware store directory factory is present. Whether that native store applies repository encryption, and `getNativeStore()` callers at 3.7.0 and 3.8.0, are **not established here**. From 3.5.0 to 3.9.0, and at no earlier checked tag, `BlobStoreRepository` also resolves an index-level `CryptoMetadata` from the settings of the `IndexMetadata` passed to `snapshotShard`, with `CryptoMetadata.fromIndexSettings` (null when that `IndexMetadata` is null). It passes that value through `executeOneFileSnapshot` to `snapshotFile`, which passes it to `writeBlobWithMetadata` for each shard file part, under the source comment "index-level SSE-KMS override". This is a source reading only, without an OpenSearch run. In that source the value comes from index settings, while `blobStore()` hands the repository's own `RepositoryMetadata` to `BlobStoreProvider`, and the shard container that receives the index-level value is obtained from `blobStore()`. This guide has since traced the value through the encrypted container and the GCS/Azure containers, as a source reading without an OpenSearch run. `EncryptedBlobContainer`'s `writeBlobWithMetadata` form that takes `CryptoMetadata`, read at 3.5.0 and 3.8.0 (the 3.6.0, 3.7.0 and 3.9.0 files have 3.8.0's git blob ID), encrypts with the container's repository-level crypto handler and passes the index-level value unchanged to the wrapped container, under the source comment "SSE-KMS settings are passed through to underlying container". At 3.5.0 and 3.9.0, `AzureBlobStore` returns an `AzureBlobContainer` as its blob container, and `AzureBlobContainer`, which has one git blob ID at every tag from 3.5.0 to 3.9.0, throws `UnsupportedOperationException` when that value is non-null, so in source an index-level value that reaches the Azure container, directly or through `EncryptedBlobContainer`, ends that write with the exception. At 3.5.0 and 3.9.0, `GoogleCloudStorageBlobContainer` overrides only the `writeBlobWithMetadata` form without `CryptoMetadata`, which calls `writeBlob`, and `BlobContainer`'s default for the `CryptoMetadata` form calls that form, so the GCS container drops the value. `BlobContainer.java` has a different git blob ID at 3.5.0 to 3.8.0 than at 3.9.0 and was read at 3.5.0 and 3.9.0 only, so GCS handling at 3.6.0 to 3.8.0 is **not established here**. At 3.5.0 and 3.9.0, `CryptoMetadata.fromIndexSettings` returns null unless the index sets `index.store.crypto.key_provider`, with `key_provider_type` defaulting to `aws-kms`. The value's effective behaviour on GCS or Azure objects is **not established here**.

**Index-level key providers and GCS/Azure snapshots (OpenSearch; source reading at 3.5.0 and 3.9.0, without an OpenSearch run).** This guide's advice: do not rely on an index's `index.store.crypto.key_provider` setting to encrypt that index's snapshot shard files in a GCS or Azure repository. At both tags, `BlobStoreRepository` resolves that setting into an index-level `CryptoMetadata` and passes it with each shard-file part to the shard container's `writeBlobWithMetadata`, and `snapshotFile` rethrows an exception from that write. On Azure, `AzureBlobStore` returns an `AzureBlobContainer`, which throws `UnsupportedOperationException` for a non-null value; with repository `crypto_settings`, `EncryptedBlobStore` wraps that container in `EncryptedBlobContainer`, which encrypts with the repository-level handler and passes the value on unchanged, so in source those shard-file writes fail with or without repository `crypto_settings`. On GCS, the container's `writeBlobWithMetadata` form that takes the value is `BlobContainer`'s default, which calls the form without it, and the GCS override of that form calls `writeBlob`, so in source GCS drops the index-level value. On this GCS path, the client-side encryption wrapper is applied only where repository `crypto_settings` are configured, and the effect on stored objects is **not established here**. For encryption you control on either repository type, use repository `crypto_settings` or the provider-side customer-managed encryption this section describes, and if an index carries the setting, confirm that a first test snapshot of that index to that repository finishes with no failed shards before relying on that repository for it. A snapshot that finishes that way does not show that the index-level provider was applied on GCS, or that encryption works on either repository type. Whether an index can carry `index.store.crypto.key_provider` at all (at both tags, the directories this guide read reference it only in `CryptoMetadata.fromIndexSettings`, with no registration of it found there, and other files were not read), what a snapshot reports when a shard-file write fails, behaviour at 3.6.0 to 3.8.0 for this warning, and the effective result on stored objects remain **not established here**.

Do not infer broader absence from Elasticsearch's settings or from failed source retrieval. This guide's advice: Configure required customer-managed encryption through the provider's bucket/account policy and grant the required key access. See [OpenSearch 3.6 snapshot/repository guidance](https://docs.opensearch.org/3.6/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/) and the pinned GCS and Azure implementation Sources below.

Keep repository access private and keys recoverable for the required retention period. Do not rewrite files inside an active repository as an improvised encryption layer. Elasticsearch configuration-file backups are separate from snapshots and should be assessed for encryption; snapshots containing security feature state are sensitive too. See [8.19 backup guidance](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-take-snapshot.html) and [repository-integrity requirements](https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshot-restore.html).

## Kibana and OpenSearch Dashboards

The UI is a separate service, normally on port **5601**. Securing cluster ports 9200/9300 does not configure browser-to-UI TLS.

### Kibana

**Free Basic; minimum version within this guide: Kibana 8.0; settings pinned to 8.19.** No Platinum/Enterprise subscription is required for browser-listener TLS. The cited versions establish support, not the first historical introduction of each setting.

Kibana defaults to HTTP with `server.host: localhost` and `server.port: 5601`, with `server.ssl.enabled: false`. The **9.5.4** HTTP schema defines the host and port defaults; the **8.19.22** sample configuration documents the same values. The Docker configuration templates at **both versions** explicitly set `server.host: "0.0.0.0"`. Check installation overrides, environment, process arguments, and container port publication. See the pinned Kibana Sources below, [8.19 Kibana TLS settings](https://www.elastic.co/guide/en/kibana/8.19/settings.html), and [Docker configuration overrides](https://www.elastic.co/guide/en/kibana/8.19/docker.html).

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

REASONED: verification scope from the recorded authoring limitations; no target cluster, container runtime, node access or audit collector is available. All deployment checks below are **REASONED, not demonstrated**: the authoring environment has no target cluster or Docker/Podman runtime, and no access to the target node or audit collector; the authoring host forbids opening listeners without an isolated network namespace, and has none. Expected outcomes follow the cited vendor behavior; no deployment result is claimed.

DEMONSTRATED: local preparation on 2026-10-05 in private /dev/shm scratch with Bash 5.3.9 and Python 3.14.4. All nine shell blocks passed bash -n and all eight inline Verify JSON payloads parsed. On 2026-10-13 (UTC), with the same Bash release, the initial cluster guard rejected the shipped placeholders, the search.example.com and es.example.com hosts, a host containing an invalid character, a missing CA and a nonnumeric port with exit 1; a valid host with a readable CA reached the first curl call. In a further run on 2026-10-13 (UTC), after the cluster guard gained the REST guard's 1 to 65535 port range check, ports 0, 65536, 99999 and a 20-digit value exited 1 before any curl call, while 1, 9200 and 65535 reached the first curl call; before the change every one of those ports reached it. The REST guard rejected a placeholder, missing body file, unsupported method and relative path with exit 1; valid values reached its curl call. In a further run on 2026-10-13 (UTC), after the cluster, REST and UI guards' `example.com` test was made case-insensitive, each of the three refused `example.com`, `EXAMPLE.COM`, `Example.Com` and `es.EXAMPLE.com` with exit 1 before any curl call and passed `Dummy.Valid.test` to its first curl call unchanged; before the change the three forms that are not all lowercase reached curl in all three guards. The three guards were later extended to refuse `example.net` and `example.org` in any letter case; in a further run on 2026-10-13 (UTC), with Bash 5.3.9, each block saved to a file and run with its commands unchanged except fixture values, and curl, python3 and date stubbed, each of the three refused `example.net`, `EXAMPLE.NET`, `es.Example.Net`, `example.org`, `EXAMPLE.ORG`, `es.Example.Org`, `example.com`, `EXAMPLE.COM`, `Example.Com`, `es.EXAMPLE.com` and `example.network.test` with exit 1 before any curl call and passed `Dummy.Valid.test` to curl unchanged, exiting 0 after 11, 1 and 2 curl calls in the cluster, REST and UI blocks; before the extension the `.net` and `.org` hosts and `example.network.test` reached curl while the `.com` forms were refused. The test is a substring match, so it also refuses longer names that contain `example.net` or `example.org`, such as `example.network.test`. An explicitly substituted curl argument recorder measured those calls, not HTTP responses. A disposable Basic header decoded to audit_probe:deliberately-wrong and had mode 0600; one parsed JSON payload was saved as a mode-0600 body file. These runs do not establish deployment CA identity, account nonexistence or per-request cluster results.

REASONED: introduction to the deployment prerequisites for the cited cluster API checks; local preparation observations are recorded above, while cluster identities and deployed trust remain unavailable. Before running:

- REASONED: substitution and paste procedure for the guarded block; re-run at marking time, the unsubstituted guard refused with exit 1 and substituted values reached the first curl call against a local argument recorder; deployed hostname and certificate coverage is not established here; no deployed cluster or its CA certificate is available in the authoring environment. Substitute your actual hostname, HTTP port, and CA path inside the single quotes on the `set --` line. Paste the whole block. Use a TLS hostname covered by the deployed certificate.
- REASONED: CA selection from the cited product TLS references; no deployed cluster CA or administrator identity is available. Elasticsearch automatic setup supplies `http_ca.crt`. For OpenSearch, use the **deployed production HTTP CA**, such as `/path/production-ca.pem`, and your production administrator's header file. Do not verify production against the demo CA.
- REASONED: fixture control from the cited privilege and document APIs; no seeded target cluster is available. Have an administrator confirm that `app-data` and `other-data` each contain a readable document with ID `rbac-probe`. A missing document is not an RBAC-denial result.
- REASONED: header-file preparation only; re-run at marking time, a disposable Basic header decoded to audit_probe:deliberately-wrong and had mode 0600; no target cluster is available to confirm that the user does not exist. Prepare `/path/audit-probe.header` with a Basic authentication header for a confirmed nonexistent user named `audit_probe` and a deliberately wrong password. Keep all credentials in header files.
- REASONED: identity comparisons from the cited role and API-key references; no target users or keys are available. Run the RBAC requests once with `/path/app-user.header`, then again with `/path/app-key.header`. On OpenSearch before 3.7, only the internal-user check applies.

REASONED: comparison criteria from the cited authorization, CORS and audit references; no target cluster or runtime is available. The expected distinctions are:

| Check | Exposed or misconfigured outcome | Fixed outcome |
| --- | --- | --- |
| REASONED: RBAC comparison from the cited privilege references; no target cluster or scoped identities are available. Application RBAC | A broad application identity reads both known documents. | The scoped identity reads `app-data` with `200` and receives an authorization `403` for `other-data`. A `401`, `404`, or connection error does not demonstrate correct RBAC. See [Elasticsearch privileges](https://www.elastic.co/docs/reference/elasticsearch/security-privileges) and [OpenSearch permissions](https://docs.opensearch.org/latest/security/access-control/permissions/). |
| REASONED: anonymous-access comparison from the cited security settings; no target cluster or effective node configuration is available. Anonymous access | An anonymous read grant returns the permitted document. In Elasticsearch, an enabled anonymous identity lacking permission also returns `401` when `xpack.security.authc.anonymous.authz_exception: false`. | A `401` establishes rejection only for the tested endpoint, not that anonymous access is disabled. After restarting affected nodes, require confirmation that `xpack.security.authc.anonymous.roles` is absent from EVERY node's EFFECTIVE configuration. Removal of the roles setting disables anonymous access; there is no `xpack.security.authc.anonymous.enabled` switch. Also require the previously anonymously readable document control below. For OpenSearch, confirm the live `config.dynamic.http.anonymous_auth_enabled: false` setting. See [Elasticsearch anonymous access](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access), [Elasticsearch security settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings), and [OpenSearch anonymous authentication](https://docs.opensearch.org/latest/security/access-control/anonymous-authentication/). |
| REASONED: origin comparison from the cited CORS settings; no target cluster or browser-origin fixture is available. CORS | An overly broad policy grants the untrusted origin. | No `Access-Control-Allow-Origin` grant for the untrusted origin. If CORS is enabled, the trusted-origin positive control succeeds and grants exactly that origin. If CORS is disabled, neither origin is granted. Judge the headers, not just the status. See [Elasticsearch CORS](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings) and [OpenSearch CORS](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/). |
| REASONED: event comparison from the cited audit references; no cluster, collector or eligible Elasticsearch audit licence is available. Audit | Failed authentication returns `401`, but disabled or suppressed auditing produces no corresponding audit event. | The same failure produces a new Elasticsearch `authentication_failed` or OpenSearch `FAILED_LOGIN` event. A `401` alone does not prove auditing. Elasticsearch requires the paid audit tier. See [Elasticsearch audit events](https://www.elastic.co/docs/reference/elasticsearch/elasticsearch-audit-events) and [OpenSearch audit fields](https://docs.opensearch.org/latest/security/audit-logs/field-reference/). |

REASONED: following block; cluster authorization, TLS, CORS and audit expectations follow the cited vendor documentation; no target cluster, runtime, node or audit collector was available.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SEARCH_HOST' '/path/http_ca.crt' '9200'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "set exactly host, CA file, and HTTP port; not probing"; exit 1; }
  case "$1|$2|$3" in
    *REPLACE_WITH_*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Cc][Oo][Mm]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Nn][Ee][Tt]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Oo][Rr][Gg]*) echo "substitute your deployment; not probing"; exit 1 ;;
  esac
  [ -n "$1" ] || { echo "host required; not probing"; exit 1; }
  case "$1" in ""|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*) echo "use a DNS hostname or IPv4 address; not probing"; exit 1 ;; esac
  [ -r "$2" ] || { echo "readable CA file required; not probing"; exit 1; }
  [ -n "$3" ] || { echo "port required; not probing"; exit 1; }
  case "$3" in *[!0123456789]*) echo "HTTP port must be numeric"; exit 1 ;; esac
  [ "$3" -ge 1 ] && [ "$3" -le 65535 ] || { echo "HTTP port must be 1 to 65535; not probing"; exit 1; }

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
    ""|*[!0123456789abcdef]*) echo "marker generation failed; not probing"; exit 1 ;;
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

REASONED: preceding block; TLS, RBAC, anonymous-access, CORS and audit comparisons follow the cited Elasticsearch and OpenSearch HTTP TLS, privileges, anonymous authentication, CORS, audit settings and event references. No target cluster, effective node configuration, audit collector or eligible Elasticsearch audit licence is available. Local shell checks are recorded above. The administrative HTTPS control must return `200` and cluster JSON before interpreting the plaintext probe. With HTTP TLS enforced, plaintext must receive no HTTP response. Elasticsearch closes a plaintext connection to its HTTPS listener; OpenSearch's enabled REST TLS allows only HTTPS. Expect `http=000` with a reset or empty reply after connection. DNS failures, timeouts, or an unreachable service are inconclusive. Any actual HTTP status, including `401`, means that endpoint answered over plaintext and is a finding. See [Elasticsearch HTTP TLS settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings) and [OpenSearch REST TLS](https://docs.opensearch.org/latest/security/configuration/tls/).

REASONED: event attribution from the cited audit-event references; no target cluster or audit collector is available. For the audit check, expect `401` and require a matching NEW REST-layer Elasticsearch `authentication_failed` or OpenSearch `FAILED_LOGIN` event. Inspect the receiving node's new `CLUSTERNAME_audit.json` entries or the corresponding OpenSearch audit index and separately collected copy. Match the recorded time interval, `audit_probe` identity, POST method, and `/app-data/_search` path. Run probes separately so each event can be attributed to its request.

REASONED: body-logging comparison from the cited audit settings and fields; no target cluster, collector or eligible Elasticsearch audit licence is available. **Reasoned, not demonstrated:** no target cluster, audit collector, or eligible Elasticsearch audit license is available here. In an isolated test cluster, run the probe with request-body logging enabled, then disabled, generating a fresh marker each time. With Elasticsearch `xpack.security.audit.logfile.events.emit_request_body: true`, require that run's marker in the matching event's `request.body`. With OpenSearch `config.audit.log_request_body: true`, require it in `audit_request_body`. After setting the respective setting to `false`, require another matching new event, with its request-body field absent and that run's marker absent from the event. A bodyless request, a missing event, or absence of a marker without the enabled-state positive control cannot establish request-body exclusion. See [Elasticsearch request-body auditing](https://www.elastic.co/docs/deploy-manage/security/logging-configuration/auditing-search-queries), [Elasticsearch auditing settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/auding-settings), and [OpenSearch audit fields](https://docs.opensearch.org/latest/security/audit-logs/field-reference/).

REASONED: configuration and header checks from the cited audit settings; no effective node configuration or collected events are available. Retain configuration readback: confirm Elasticsearch's effective `xpack.security.audit.logfile.events.emit_request_body: false`, accounting for transient and persistent cluster-setting overrides as well as each node's configuration. Repeat the OpenSearch audit configuration GET above and confirm `config.enabled: true`, `config.audit.enable_rest: true`, `config.audit.log_request_body: false`, and `config.audit.exclude_sensitive_headers: true`. Check that sensitive headers, including the Authorization value sent from the header file, are absent from the matching events and their collected copies in both test states. Header exclusion and body exclusion are separate checks. Restore and read back body logging as disabled after the isolated positive-control test. See [OpenSearch body logging](https://docs.opensearch.org/latest/security/audit-logs/index/) and [audit configuration fields](https://docs.opensearch.org/latest/security/api/audit/update-audit-configuration/).

REASONED: audit-evidence limits from the cited event and collection references; no target collector or events are available. Missing events leave the audit check unresolved until collection delay, filtering, licensing, and configuration have been checked. A `401` alone proves neither audit delivery nor body exclusion.

REASONED: listener inventory from the cited ss manual; target-node access is unavailable. On the node itself, inspect listeners:

```bash
# Reasoned: no access to the target node. Run ON that node; substitute actual ports.
ss -tlnp 'sport = :9200'
ss -tlnp 'sport = :9300'
```

REASONED: listener interpretation from the cited port defaults and Docker configuration; target-node and container-runtime access are unavailable. These use `ss`'s own port filter, avoiding accidental PID matches. For Elasticsearch 8.19.22 and 9.5.4, the source defaults are `9200-9300` for HTTP and `9300-9399` for transport; each binds an available port. The transport upper bound is 9399, not 9400. See the pinned `HttpTransportSettings` and `TransportSettings` Sources below. Inspect the actual ports used by either product. Expect loopback or deliberate private listeners. The exception is an official Docker container on a bridge or user-defined network (not host networking): its bundled `network.host: 0.0.0.0` makes wildcard listeners inside the container the default unless it was overridden, so check instead that 9200 is reachable only from intended clients and 9300 only from cluster peers. With host networking, a wildcard listener is a finding like any other. An unexpected public or wildcard listener is a finding to review against the network controls; no output is inconclusive until the running process and its actual ports are located.

### Residual-control checks

REASONED: deployment scope from the cited product APIs; no target cluster, eligible Elasticsearch licence, storage, repository or UI fixture is available. These additional deployment checks are **REASONED, not demonstrated**. No target Elasticsearch/OpenSearch cluster, eligible Elasticsearch FLS/DLS licence, target storage, provider repository access, or running UI with deployed certificates is available in the authoring environment. Expected outcomes rest on the cited vendor documentation and pinned source readings.

REASONED: fixture and substitution instructions per the cited product APIs and the local preparation recorded above; no isolated test deployment is available in the authoring environment. Use isolated test deployments for exposed-state fixtures. Substitute values inside single quotes and paste whole shell blocks. Values containing a literal apostrophe need proper shell quoting. Keep credentials in the protected header files described above, with tracing disabled. The following blocks assume the shell's normal builtins.

REASONED: body-file and per-request procedure for the REST block below, per the cited product APIs; re-run at marking time, before the guard's `example.com` test was made case-insensitive, the guard in that block refused a placeholder, a missing body file, an unsupported method and a relative path with exit 1 and dispatched valid values to a local argument recorder, and a parsed JSON body was saved as a mode-0600 file; on 2026-10-13 (UTC), with Bash 5.3.9 and a stub curl executable, the edited guard refused `example.com`, `EXAMPLE.COM`, `Example.Com` and `es.EXAMPLE.com` with exit 1 before any curl call and passed `Dummy.Valid.test` to curl unchanged, where before the edit the three forms that are not all lowercase reached curl; after the later extension of the guard to `example.net` and `example.org` in any letter case, a further run on 2026-10-13 (UTC), with Bash 5.3.9, the block saved to a file and run with its commands unchanged except fixture values, and curl, python3 and date stubbed, refused `example.net`, `EXAMPLE.NET`, `es.Example.Net`, `example.org`, `EXAMPLE.ORG`, `es.Example.Org`, `example.com`, `EXAMPLE.COM`, `Example.Com`, `es.EXAMPLE.com` and `example.network.test` with exit 1 before any curl call and passed `Dummy.Valid.test` to its one curl call unchanged, where before the extension the `.net` and `.org` hosts and `example.network.test` reached curl while the `.com` forms were refused; the test is a substring match, so it also refuses longer names that contain `example.net` or `example.org`, such as `example.network.test`; no target cluster is available. For the REST request tables below, save each JSON body in a protected file. Run this block once per request, setting the method, path, and body-file arguments. Use `/dev/null` for a request with no body. Select the administrator or application header file as directed:

REASONED: following block; REST fixture comparisons follow the cited product APIs and restriction rules; no target cluster, eligible Elasticsearch licence or repository access was available.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SEARCH_HOST' 'REPLACE_WITH_CA_FILE' '9200' 'REPLACE_WITH_HEADER_FILE' 'GET' '/REPLACE_WITH_REQUEST_PATH' '/dev/null'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 7 ] || { echo "set host, CA, port, header file, method, path, and body file; not probing"; exit 1; }
  case "$1|$2|$3|$4|$5|$6|$7" in
    *REPLACE_WITH_*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Cc][Oo][Mm]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Nn][Ee][Tt]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Oo][Rr][Gg]*) echo "substitute your deployment; not probing"; exit 1 ;;
  esac
  case "$1" in ""|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*) echo "use a DNS hostname or IPv4 address; not probing"; exit 1 ;; esac
  case "$3" in ""|*[!0123456789]*) echo "numeric port required; not probing"; exit 1 ;; esac
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

REASONED: preceding block; REST request and response comparisons follow the cited product APIs and restriction rules; no target cluster, eligible Elasticsearch licence or repository access is available. Local file and argument checks are recorded above. Judge the HTTP status and response contents, not the shell's final status alone. A transport failure or `401` is not evidence of correct field/document restrictions.

### Verify field and document restrictions (REASONED: retrieval and aggregation comparisons from the cited Elasticsearch and OpenSearch FLS, DLS and API references; no live clusters or eligible Elasticsearch FLS/DLS licence are available)

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

### Verify storage encryption (REASONED: device-chain and startup comparisons from the cited storage and systemd manuals; no target node, storage or isolated unavailable-mount fixture is available)

**REASONED, not demonstrated:** these inspections do not require a running cluster, but target-node and target-storage access are unavailable here.

Run on the node, with sufficient permission to inspect the intended dm-crypt mapping:

REASONED: following block; storage inspection follows the cited findmnt, lsblk and cryptsetup manuals; target-node and storage access were unavailable.

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

REASONED: following block; startup comparison follows the cited systemd assertions; no isolated service and unavailable-mount fixture was available.

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

### Verify snapshot encryption and key isolation (REASONED: snapshot, restore and object/key comparisons from the cited product and provider references; no live cluster, repository, provider access or KMS test identities are available)

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

REASONED: following block; object encryption and access comparisons follow the cited AWS APIs and KMS permissions; repository, provider and KMS test identities were unavailable.

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

REASONED: UI verification scope from the cited Kibana and Dashboards settings; no running UI, certificates or network test paths are available. **REASONED, not demonstrated:** requires Kibana or OpenSearch Dashboards, deployed certificates, and authorized/prohibited network test paths.

REASONED: TLS comparison from the cited UI settings; no isolated UI deployment or certificates are available. In an isolated exposed fixture, record an HTTP login page or redirect on the actual UI port. After applying the fixed configuration, run:

REASONED: following block; UI TLS comparison follows the cited Kibana and Dashboards settings; no running UI, certificates or network test paths were available.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_HOST' 'REPLACE_WITH_UI_CA_FILE' '5601'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "set UI host, CA file, and port; not probing"; exit 1; }
  case "$1|$2|$3" in *REPLACE_WITH_*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Cc][Oo][Mm]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Nn][Ee][Tt]*|*[Ee][Xx][Aa][Mm][Pp][Ll][Ee].[Oo][Rr][Gg]*) echo "substitute your UI deployment"; exit 1 ;; esac
  case "$1" in ""|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*) echo "use a DNS hostname or IPv4 address"; exit 1 ;; esac
  case "$3" in ""|*[!0123456789]*) echo "numeric UI port required"; exit 1 ;; esac
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

REASONED: TLS response interpretation from the cited UI settings; no running UI or deployed certificates are available. On the authorized path, require successful CA-validated HTTPS with the expected UI response. Plaintext on that TLS listener must not serve the UI; a connection close or explicit protocol rejection can demonstrate rejection. A timeout or DNS failure alone cannot.

REASONED: network comparison from the cited UI binding settings; authorized and prohibited deployment paths are unavailable. For loopback deployments, test locally using a certificate hostname that resolves to the UI's loopback listener. Separately test the real deployment address from the prohibited network, not that client's own loopback. Require the prohibited connection to fail while the authorized path still works, and retain network-control evidence.

REASONED: UI listener inventory from the cited ss manual and UI settings; target-host access is unavailable. On the UI host, inspect the actual listener:

REASONED: following block; UI listener inspection follows the cited UI settings and ss manual; target-host access was unavailable.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "set exactly one UI port; not probing"; exit 1; }
  case "$1" in ""|*[!0123456789]*) echo "substitute the numeric UI port"; exit 1 ;; esac
  [ "$1" -ge 1 ] && [ "$1" -le 65535 ] || exit 1
  # REASONED: no access to the target UI host. Run on that host.
  ss -tlnp "sport = :$1"
)
```

REASONED: binding, backend TLS and cookie inspection from the cited UI settings; no UI host, cluster connection or session fixture is available. Require the intended loopback/private bind. Inspect container port publication, selected configuration, environment, and process arguments too. Confirm the UI-to-cluster connection still uses HTTPS and full verification; successful browser TLS alone does not establish that. For Dashboards, confirm `opensearch_security.cookie.secure: true` and the Secure attribute on its session cookie. See [Kibana 8.19 settings](https://www.elastic.co/guide/en/kibana/8.19/settings.html), [Kibana Docker overrides](https://www.elastic.co/guide/en/kibana/8.19/docker.html), and [Dashboards 3.6 TLS settings](https://docs.opensearch.org/3.6/install-and-configure/install-dashboards/tls/).

REASONED: exposure interpretation from the cited cluster authentication references; no target cluster is available. An unauthenticated `GET /` returning cluster JSON is the classic finding; so is `_cat/indices` listing your data to the world.

REASONED: deployment expectations and source-audit limits recorded in this guide; no target deployment is available, and OpenSearch GCS/Azure end-to-end repository crypto applicability, live behaviour, available deployed key providers, minimum versions and later-release behaviour remain unestablished. The deployment checks below remain REASONED from the cited vendor documentation and pinned sources. This guide reviewed the OpenSearch 3.8.0 GCS/Azure plugin sources and core repository crypto path; live encryption behaviour remains untested.

| Scope | Exposed/fixed checks and retained source work | Status |
| --- | --- | --- |
| Cluster checks | Run every check against exposed and fixed states in isolated Elasticsearch 8.x and OpenSearch test clusters, including OpenSearch 3.7+ keys and an eligible Elasticsearch audit license. Include the Elasticsearch counterexample: anonymous roles remain configured, authz_exception is false, and the anonymous identity lacks permission for both / and app-data, so both probes return 401 while a document in another permitted index remains anonymously readable with 200. Record that document and its contents, remove anonymous.roles, restart affected nodes, confirm its absence from every node's effective configuration, and require the same document request to return 401 while an administrator still retrieves it with 200. Also check fresh failed-authentication audit events with a unique harmless JSON marker present when body logging is enabled and absent when disabled; retain configuration-readback and sensitive-header-exclusion checks. Record versions, effective configuration, HTTP responses, listener output, and matching newly collected audit events. | REASONED: target clusters, container runtime, and audit collection are unavailable in the authoring environment. |
| Listener defaults | Check Elasticsearch and Kibana 8.19.22 and 9.5.4 listener addresses and actual ports in exposed and fixed states. Include archive/package initial setup, Docker configuration, enrollment with local and remote peers, explicit address overrides, available IPv4/IPv6 loopback addresses, and container publication. Retain effective settings and authorized/prohibited network results. | REASONED: the authoring host forbids opening listeners without an isolated network namespace, and has none. Existing cluster/runtime and target-access blockers still apply. |
| FLS/DLS | Check the two-tenant fixture on Elasticsearch 8.19 with an eligible Platinum/Enterprise licence and OpenSearch 3.8.0. Record unrestricted and restricted search, direct GET, `_source`, requested-field, secret-aggregation, and allowed-aggregation results. Retain administrator fixture controls, effective roles/settings, and actual application-credential results. Record documented inference limitations separately from ordinary retrieval results. | REASONED: live clusters and an eligible Elasticsearch FLS/DLS licence are unavailable. |
| Storage | Record actual data-path mount/device chains before and after encryption. Check refusal to start when the required encrypted mount is unavailable and successful startup after restoration. Cover logs, swap, and local snapshot storage; use provider volume/key metadata where applicable. | REASONED: target-node, target-storage, and service-manager fixture access are unavailable. |
| REASONED: whole row; live snapshot, key-metadata and KMS-denial checks per the cited snapshot and repository references, with clusters, repositories and provider or KMS test identities unavailable. Snapshots and source audit | On both products, take and restore a harmless snapshot. Record new and retained object encryption/key metadata, authorized and unauthorized object downloads, and a KMS-dependent denial with a working positive control. Record the OpenSearch version and explicit S3 encryption settings. Separately verify OpenSearch GCS/Azure client-side-encryption capability in the deployed version before asserting support or absence; this guide reviewed the 3.8.0 plugin sources and core repository crypto path. | REASONED for live checks: clusters, repositories and provider/KMS test identities are unavailable. End-to-end GCS/Azure repository crypto applicability, available deployed key providers, minimum versions and later-release behaviour remain unestablished. |
| UI | Check exposed HTTP and fixed CA-validated HTTPS for Kibana 8.19 and Dashboards 3.8.0. Record plaintext rejection, listener addresses, container overrides/publication, prohibited-network denial with an authorized positive control, backend full verification, and the Dashboards Secure cookie. | REASONED: UI processes, deployed certificates, target hosts, and network test paths are unavailable. |

## Sources (checked September 2026)

- Official Elasticsearch Docker images: the tag map (library file pinned commit 8480a06d8ca03ca7da29a469fdbddb5f9f31df61), and for each published branch the bundled `elasticsearch.yml` with `network.host: 0.0.0.0` and the Dockerfile lines that copy it and `EXPOSE 9200 9300` (8.19 at pinned commit 0208be14db8ebd2e40442d328e8f79921368c5a9, 9.4 at 25fdea1109a231cedf9d1d3cf78bbb7fce488561, 9.5 at 18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a), the entrypoint lines that pass `-E` arguments through to the server after a first argument of `eswrapper` or a path whose last component is `elasticsearch`, Elastic's Docker configuration page for environment-variable settings and bind-mounted configuration, and its networking settings reference for `0.0.0.0`: https://github.com/docker-library/official-images/blob/8480a06d8ca03ca7da29a469fdbddb5f9f31df61/library/elasticsearch#L2-L19, https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/config/elasticsearch.yml, https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/Dockerfile#L38, https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/Dockerfile#L123, https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/config/elasticsearch.yml, https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/Dockerfile#L57, https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/Dockerfile#L99, https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/config/elasticsearch.yml, https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/Dockerfile#L57, https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/Dockerfile#L99, https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/bin/docker-entrypoint.sh#L10-L22, https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/bin/docker-entrypoint.sh#L84, https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/bin/docker-entrypoint.sh#L10-L22, https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/bin/docker-entrypoint.sh#L84, https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/bin/docker-entrypoint.sh#L10-L22, https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/bin/docker-entrypoint.sh#L84, https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-configure and https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings
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
- GCS plugin settings, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStoragePlugin.java#L125-L144
- GCS repository settings, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L74-L84
- GCS blob upload, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L259-L266, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L289-L291, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L370-L373
- GCS client construction, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageService.java#L247-L285
- Azure plugin settings, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepositoryPlugin.java#L133-L153
- Azure repository settings, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L75-L107
- Azure blob upload, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L351-L394
- Azure client construction, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureStorageService.java#L195-L239
- GCS/Azure blob-store creation and Azure repository-level encryption hint, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L147-L150, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L185-L200
- OpenSearch core repository crypto path, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/action/admin/cluster/repositories/put/PutRepositoryRequest.java#L248-L271, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L54-L63, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L44-L96, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1073-L1085, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L39-L51, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L94-L110, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/crypto/CryptoHandlerRegistry.java#L144-L167, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/crypto-kms/src/main/java/org/opensearch/crypto/kms/CryptoKmsPlugin.java#L26-L27
- GCS and Azure repository inheritance from BlobStoreRepository, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49, https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1098
- OpenSearch 2.10.0 repository crypto validation and conditional wrap, MeteredBlobStoreRepository class, GCS/Azure superclass declarations, store creation and class bodies (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L52-L61, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L764-L788, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L56, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L126-L129, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L68, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L164-L179, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L56-L154, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L68-L195, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L51-L81
- OpenSearch 3.0.0 repository crypto validation and conditional wrap, MeteredBlobStoreRepository class, GCS/Azure superclass declarations, store creation and class bodies (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L54-L63, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L989-L1013, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L121-L124, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L159-L174, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199, https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74
- OpenSearch BlobStoreRepository.blobStore() conditional wrap, MeteredBlobStoreRepository class and GCS/Azure class bodies, tag 3.3.2 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.3.2/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1054-L1078, https://github.com/opensearch-project/OpenSearch/blob/3.3.2/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74, https://github.com/opensearch-project/OpenSearch/blob/3.3.2/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158, https://github.com/opensearch-project/OpenSearch/blob/3.3.2/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199
- OpenSearch BlobStoreRepository.blobStore() delegation to BlobStoreProvider, MeteredBlobStoreRepository class and GCS/Azure class bodies, tag 3.4.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1062-L1084, https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74, https://github.com/opensearch-project/OpenSearch/blob/3.4.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158, https://github.com/opensearch-project/OpenSearch/blob/3.4.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199
- OpenSearch BlobStoreRepository repository metadata field, blobStore() delegation, shard-container lookup, snapshotShard IndexMetadata parameter, index-level CryptoMetadata resolution, handoff through executeOneFileSnapshot to snapshotFile and writeBlobWithMetadata call, tag 3.5.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L219, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1063-L1085, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L2977-L2979, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L3950-L3962, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4147-L4148, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4155-L4189, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4819-L4870, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4958-L4964
- OpenSearch GCS/Azure class bodies and getNativeStore() overrides, tag 3.7.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60-L195, https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L191-L194, https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72-L236, https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L232-L235
- OpenSearch BlobStoreRepository.blobStore() delegation to BlobStoreProvider, MeteredBlobStoreRepository class and GCS/Azure class bodies, tag 3.9.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1063-L1085, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60-L195, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72-L236
- OpenSearch BlobStoreRepository repository metadata field, shard-container lookup, snapshotShard IndexMetadata parameter, index-level CryptoMetadata resolution, handoff through executeOneFileSnapshot to snapshotFile and writeBlobWithMetadata call, tag 3.9.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L219, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L2982-L2984, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L3955-L3967, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4152-L4153, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4160-L4194, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4824-L4875, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4963-L4969
- OpenSearch 2.10.0 release notes: core crypto library, encryption-sdk and crypto-kms additions (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L27, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L33, https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L35
- OpenSearch 2.9.0 directory listings without the crypto packages, EncryptedBlobStore and crypto-kms entries (checked October 2026): https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/action/admin/cluster, https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/common/blobstore, https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch, https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/plugins
- OpenSearch BlobStoreProvider blobStore(), createBlobStore() wrap and initBlobStore(), tag 3.4.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L41-L85
- OpenSearch BlobStoreProvider blobStore(), createBlobStore() wrap and initBlobStore(), tag 3.9.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L44-L96
- OpenSearch EncryptedBlobContainer encrypted writes and CryptoMetadata forwarding, tag 3.5.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L94-L170
- OpenSearch EncryptedBlobContainer CryptoMetadata forwarding, tag 3.8.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L147-L170
- OpenSearch BlobStoreRepository file without a native-store reference, tag 3.7.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.7.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1-L4970
- OpenSearch BlobStoreRepository file without a native-store reference, IndexService warm remote-store getNativeStore() call, GCS and Azure blob container creation, GCS writeBlobWithMetadata override, BlobContainer CryptoMetadata default, AbstractBlobContainer body and CryptoMetadata.fromIndexSettings, tag 3.9.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1-L4970, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/index/IndexService.java#L794-L812, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/index/IndexService.java#L1429-L1440, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L137-L140, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L173-L176, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobContainer.java#L49-L109, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/BlobContainer.java#L201-L212, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/support/AbstractBlobContainer.java#L43-L56, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/cluster/metadata/CryptoMetadata.java#L114-L124
- OpenSearch GCS and Azure blob container creation, GCS writeBlobWithMetadata override, BlobContainer CryptoMetadata default, AbstractBlobContainer body, AzureBlobContainer superclass, Azure CryptoMetadata rejection, EncryptedBlobStore container wrap and CryptoMetadata.fromIndexSettings, tag 3.5.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L137-L140, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L173-L176, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobContainer.java#L49-L109, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/BlobContainer.java#L200-L211, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/support/AbstractBlobContainer.java#L43-L56, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L63, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67, https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/cluster/metadata/CryptoMetadata.java#L114-L124
- OpenSearch AzureBlobContainer superclass, Azure CryptoMetadata rejection, EncryptedBlobStore container wrap and EncryptedBlobContainer CryptoMetadata forwarding, tag 3.9.0 (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L63, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67, https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L147-L170
- OpenSearch 2.9.0 BlobStoreRepository.blobStore(), PutRepositoryRequest source parsing and RepositoryMetadata fields without crypto handling (checked October 2026): https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L738-L759, https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/action/admin/cluster/repositories/put/PutRepositoryRequest.java#L215-L230, https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/cluster/metadata/RepositoryMetadata.java#L54-L66
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
- Elasticsearch network setting definitions: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L28-L42), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L28-L42).
- Elasticsearch default bind fallback: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L112-L121), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L112-L121); loopback token resolution: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L233-L239), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L233-L239).
- Elasticsearch listener callers that apply the fallback: HTTP [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/http/AbstractHttpServerTransport.java#L132-L140), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/http/AbstractHttpServerTransport.java#L136-L144); transport profiles [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/transport/TcpTransport.java#L1073-L1075), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/transport/TcpTransport.java#L1079-L1081).
- Elasticsearch loopback addresses on interfaces that are up, without an address-family filter: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkUtils.java#L142-L173), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkUtils.java#L147-L178).
- Elasticsearch HTTP host/bind/publish settings and `9200-9300` port default: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/http/HttpTransportSettings.java#L70-L89), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/http/HttpTransportSettings.java#L64-L83).
- Elasticsearch transport host/bind/publish settings and `9300-9399` port default: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/transport/TransportSettings.java#L34-L62), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/transport/TransportSettings.java#L34-L57).
- Elasticsearch auto-configuration HTTP and transport address guards, writes, and enrollment condition: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L788-L821), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L800-L833); remote-peer test: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L876-L891), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L888-L903).
- Elasticsearch standard configuration leaves network and HTTP settings commented: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/distribution/src/config/elasticsearch.yml#L51-L63), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/distribution/src/config/elasticsearch.yml#L51-L63); Docker configuration sets `network.host: 0.0.0.0`: [8.19.22](https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/distribution/docker/src/docker/config/elasticsearch.yml#L1-L2), [9.5.4](https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/distribution/docker/src/docker/config/elasticsearch.yml#L1-L2).
- Kibana host and port schema defaults: [9.5.4](https://github.com/elastic/kibana/blob/abf4eb613d64cdb3a6290671ce1cb67399677ab3/src/core/packages/http/server-internal/src/http_config.ts#L146-L155); sample configuration: [8.19.22](https://github.com/elastic/kibana/blob/fd8e6f336cd7a18d0fd805de4608e1e38e0da163/config/kibana.yml#L4-L11), [9.5.4](https://github.com/elastic/kibana/blob/abf4eb613d64cdb3a6290671ce1cb67399677ab3/config/kibana.yml#L4-L11).
- Kibana Docker wildcard host configuration: [8.19.22](https://github.com/elastic/kibana/blob/fd8e6f336cd7a18d0fd805de4608e1e38e0da163/src/dev/build/tasks/os_packages/docker_generator/templates/kibana_yml.template.ts#L22-L26), [9.5.4](https://github.com/elastic/kibana/blob/abf4eb613d64cdb3a6290671ce1cb67399677ab3/src/dev/build/tasks/os_packages/docker_generator/templates/kibana_yml.template.ts#L22-L26).


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- es-api: Elasticsearch API (8.x)
- es819: Elasticsearch reference (8.19)
- es8: Elasticsearch listener source (8.19.22)
- es9: Elasticsearch listener source (9.5.4)
- os36: OpenSearch reference (3.6)
- os31: OpenSearch S3 reference (3.1)
- os38: OpenSearch S3 source (3.8.0)
- gcs38: OpenSearch GCS source (3.8.0)
- azure38: OpenSearch Azure source (3.8.0)
- corecrypto38: OpenSearch repository crypto source (3.8.0)
- dash: OpenSearch Dashboards (3.8.0)
- dash36: Dashboards TLS reference (3.6)
- es: Elasticsearch documentation (unknown)
- images: Elasticsearch Docker library (8480a06d8ca03ca7da29a469fdbddb5f9f31df61)
- os: OpenSearch documentation (unknown)
- os-license-source: OpenSearch Security licence source (4ba3cc0e2ebec61b726b227fdf51e55f4a502182)
- os-users-source: OpenSearch demo users source (03a224d16045a8f561e2d7d84b8765c95309524c)
- kb: Kibana reference (8.19)
- kb8: Kibana source (8.19.22)
- kb9: Kibana source (9.5.4)
- cloud: Cloud provider documentation (unknown)
- host: Host inspection documentation (unknown)
- corecrypto210: OpenSearch repository crypto source (2.10.0)
- corecrypto300: OpenSearch repository crypto source (3.0.0)
- corecrypto290: OpenSearch crypto directory source (2.9.0)
- repo290: OpenSearch repository source (2.9.0)
- corecrypto332: OpenSearch repository crypto source (3.3.2)
- corecrypto340: OpenSearch repository crypto source (3.4.0)
- corecrypto350: OpenSearch repository crypto source (3.5.0)
- corecrypto370: OpenSearch repository crypto source (3.7.0)
- corecrypto390: OpenSearch repository crypto source (3.9.0)

Claims (full source mapping in the JSON block below):

- es-tier (REASONED; es): Self-managed 8.x TLS, native users, RBAC, REST keys, anonymous controls and CORS are free Basic; LDAP/audit and FLS/DLS require Platinum/Enterprise, with current Platinum restricted to existing customers.
- es-auto (REASONED; es): Eligible initial startup enables auth, HTTP/transport TLS and elastic password; redirected output, unwritable config or existing settings can skip setup, with stated discovery exceptions; packages require password reset.
- es-tls (REASONED; es): Keep xpack.security.enabled and HTTP TLS enabled; repair CA trust/certificates instead of disabling protection.
- es-bind (REASONED; es8, es9): network.host defaults `_local_` on up interfaces across available families; family-specific tokens and HTTP/profile bind overrides apply before network fallback.
- es-http-range (REASONED; es8, es9): HTTP defaults to an available port in 9200-9300, subject to effective host/bind/publish settings.
- es-transport-range (REASONED; es8, es9): Transport defaults to an available port in 9300-9399; inspect effective profile and actual listener ports.
- es-auto-http (REASONED; es8, es9): Auto-configuration writes http.host=0.0.0.0 only when none of the three HTTP or three network address settings has a value, including enrollment.
- es-auto-transport (REASONED; es8, es9): Transport address guard respects existing settings; new-cluster wildcard is commented and enrollment activates it only for a discovered nonlocal, nonloopback publish address.
- es-docker (REASONED; images, es): Pinned image map covers 8.19.22/9.4.6/9.5.3; shipped network.host=0.0.0.0 widens API and transport unless overridden. EXPOSE includes 9300, so avoid -P, host networking and untrusted peers.
- es-source-docker (REASONED; es8, es9): Source configurations at 8.19.22/9.5.4 also set network.host wildcard, making both auto-configuration address guards false.
- es-role (REASONED; es-api): Give each app an index-read role and dedicated native user; manage_own_api_key permits self-issued keys without broader index access, and superuser is not an app role.
- credential-files (REASONED; host): Use protected 0600 header/request/response files and verified CA input; base64 Basic is not encryption and file input does not prevent file readers or tracing.
- es-key (REASONED; es-api): Explicit API-key role descriptors intersect creator permissions; omitted descriptors inherit a snapshot, omitted expiration never expires, and an API key cannot create another privileged key.
- es-ldap (REASONED; es): Optional paid LDAP mapping binds the specific realm and group DN; native-user roles are assigned through the user API.
- es-fls (REASONED; es819): 8.19 field_security.grant restricts concrete fields, not aliases; metadata remains accessible and omission grants all fields. Minimum guide scope 8.0 is not an introduction claim.
- es-dls (REASONED; es819): 8.19 query restricts documents; omission removes DLS. Keep tenant readers read-only and remove unrestricted roles that combine to defeat restrictions.
- es-fls-limits (REASONED; es819): DLS has aggregate/scoring inference channels and query/API restrictions including joins, lookups, percolate and date now; test actual queries and prefer separate indices for stronger isolation.
- es-key-review (REASONED; es819): Review previously issued key permission snapshots separately after changing roles; role edits alone do not establish repaired key restrictions.
- es-anonymous (REASONED; es): Remove anonymous.roles from every effective node configuration and restart; no roles disables anonymous access. A tested 401 alone cannot prove it is globally off.
- es-cors (REASONED; es): CORS defaults disabled; if needed configure exact origin, methods and headers, restart nodes and retain authorization.
- es-audit (REASONED; es): Audit defaults disabled; enable on each 8.x node with restart and collect CLUSTERNAME_audit.json independently. Dynamic enablement documented for 9.5+ does not apply to 8.x.
- es-audit-body (REASONED; es): Request-body emission defaults false; keep it off and avoid event exclusions/ignore policies suppressing authentication_failed.
- os-tier (REASONED; os-license-source): OpenSearch Security is free Apache-2.0 with no paid security tier; keep authentication and TLS enabled.
- os-demo-users (REASONED; os, os-users-source): From 2.12 demo setup requires initial admin password but only changes admin; six other seeded users retain demo credentials until removed/replaced and applied to the live security index.
- os-tls (REASONED; os): Replace demo certificates; REST TLS defaults false underneath demo setup and requires plugins.security.ssl.http.enabled=true with production certificates.
- os-rbac (REASONED; os): Create a custom index-read role and internal user with explicit mapping; Security REST administration requires its own authorization and other mappings may add grants.
- os-api-key (REASONED; os): Native scoped keys require 3.7+ and security administrators; enable api_tokens and explicit lifetime/count limits, using index_pattern and duration_seconds rather than Elasticsearch fields.
- os-key-default (REASONED; os): Omitted token duration uses max_duration_seconds, documented default 7776000; example caps at 86400 with 100 tokens, and returned token is retrievable only once.
- os-apply (REASONED; os): securityadmin applies local configuration to the live index; back up first, use file/type-limited upload, production CA/admin certificate and hostname verification because stale files overwrite live changes.
- os-fls (REASONED; os36): 3.6 FLS/DLS recipe uses JSON-string dls and visible tenant_id in fls; review all roles and inclusion/exclusion interactions, not Elasticsearch role-combination assumptions.
- os-dls (REASONED; os36): dfm_empty_overrides_all affects unrestricted-role precedence; DLS does not constrain writes and adaptive filter-level DLS limits APIs/cross-cluster search. Tokens need independent restriction tests.
- os-anonymous (REASONED; os): Set live anonymous_auth_enabled=false while preserving authentication domains; update through securityadmin, not just local YAML.
- os-cors (REASONED; os): CORS defaults false; exact-origin static settings go in opensearch.yml and require restart, independently of authentication.
- os-audit (REASONED; os): Auditing needs destination and enabled config; internal_opensearch stores daily audit indexes, while shipped enabled=true alone records nothing without storage type.
- os-audit-body (REASONED; os): Read live audit config, enable REST and disable request-body logging via admin-certificate PATCH; preserve defaults and do not suppress FAILED_LOGIN.
- os-audit-headers (REASONED; os): exclude_sensitive_headers defaults true; readonly REST fields require complete audit-file application. Read back enabled, REST, body=false and headers=true separately.
- storage (REASONED; es819, os): Use OS/provider encryption below path.data, including logs/swap/local snapshots; path.data only selects a directory and encryption-at-rest support is not a product encryption switch.
- mount-enforcement (REASONED; host): RequiresMountsFor plus AssertPathIsMountPoint prevents ordinary-directory fallback with systemd; reload manager and verify encrypted device chain separately.
- snapshot-boundary (REASONED; es, os31, cloud): Ordinary snapshots use free Basic/OpenSearch; remote repository encryption is independent of node disks and authorized server-side downloads are decrypted.
- cloud-defaults (REASONED; cloud): New AWS S3, GCS and Azure objects are encrypted server-side by default; assess historical objects and customer key ownership separately.
- es-s3 (REASONED; es819): 8.19 server_side_encryption defaults false; true requests AES256 SSE-S3, not client encryption. Omit it when using bucket-default KMS and verify resulting metadata.
- os-s3 (REASONED; os31, os38): 3.1 removed server_side_encryption; server_side_encryption_type accepts AES256/aws:kms/bucket_default. Default changed from bucket_default to AES256 in 3.8; explicitly select intended mode.
- os-s3-kms (REASONED; os31, cloud): Explicit KMS repository mode uses server_side_encryption_kms_key_id ARN with object/KMS permissions; this is server-side encryption and settings are not Elasticsearch-compatible.
- es-gcs-azure (REASONED; es819): 8.19 GCS/Azure setting lists document no client-side-encryption switch; configure provider key policy and access. GCS supplied keys remain server-side and Azure keys/SAS are authentication.
- os-gcs-azure (REASONED; os36, cloud): Follow the OpenSearch 3.6 plugin/credential workflow, including Azure; this guide's advice is to configure required customer-managed encryption through provider policy and grant key access. Do not infer broader absence from Elasticsearch settings or failed source retrieval.
- os-gcs-azure-settings (REASONED; gcs38, azure38): This guide's review of OpenSearch 3.8.0 GCS/Azure plugin-specific settings, blob upload and client construction found no plugin-specific client-side-encryption setting.
- os-gcs-azure-core (REASONED; gcs38, azure38, corecrypto38): In the cited OpenSearch 3.8.0 core path, crypto_settings triggers client-side EncryptedBlobStore wrapping of a non-server-side-encryption store and encryption before writes. Common provider and GCS/Azure createBlobStore methods show a path to both types and Azure rejects per-object CryptoMetadata; this guide assesses end-to-end applicability and live behaviour as unestablished.
- os-gcs-azure-providers (REASONED; corecrypto38): The cited 3.8.0 path requires key_provider_name, key_provider_type and a registered provider of that type; the tree includes aws-kms. This guide's assessment: deployed providers, end-to-end applicability, live behaviour, a universal GCS/Azure minimum and unchecked-release behaviour remain unestablished.
- os-gcs-azure-versions (REASONED; corecrypto210, corecrypto300, corecrypto290, corecrypto332, corecrypto340, corecrypto390, corecrypto38): This guide's assessment from pinned 2.10.0/3.0.0 methods, 2.10.0 release notes and 2.9.0 listings without crypto entries: the checked range with repository crypto settings starts at 2.10.0. Across 31 tags to 3.9.0, blobStore() wraps through 3.3.2 and from 3.4.0 delegates to BlobStoreProvider, which wraps; other releases and a universal deployed GCS/Azure minimum remain unestablished.
- os-gcs-azure-path (REASONED; corecrypto210, corecrypto300): At 2.10.0/3.0.0, GCS/Azure extend MeteredBlobStoreRepository, an abstract BlobStoreRepository subclass declaring neither blobStore() nor createBlobStore, and implement createBlobStore; BlobStoreRepository.blobStore() wraps its result when crypto metadata is non-null. This guide infers both reach the wrap in source; deployed encryption, installed providers and unchecked releases are unestablished.
- os-gcs-azure-blobstore (REASONED; corecrypto210, corecrypto300, corecrypto332, corecrypto340, corecrypto370, corecrypto390, corecrypto38): At every checked tag 2.10.0 to 3.9.0, the pinned GoogleCloudStorageRepository, AzureRepository and MeteredBlobStoreRepository class bodies declare no blobStore() method; AzureRepository overrides getBlobStore() only to return super.getBlobStore(). This guide's inference that GCS and Azure reach the encryption wrap also relies on that absence and, from 3.4.0, on BlobStoreProvider's wrap.
- os-gcs-azure-range (REASONED; corecrypto210, corecrypto300, corecrypto332, corecrypto340, corecrypto390, corecrypto38): At all 25 checked OpenSearch tags 2.10.0 to 3.3.2, BlobStoreRepository.blobStore() has the same body, wrapping the createBlobStore() result in EncryptedBlobStore when crypto metadata is non-null. From 3.4.0 to 3.9.0 it returns blobStore(false) via BlobStoreProvider, which wraps likewise with server-side encryption off (source reading at 3.4.0, 3.8.0, 3.9.0; 3.5.0 to 3.7.0 share 3.4.0's blob ID).
- os-gcs-azure-native (REASONED; corecrypto370, corecrypto390): From 3.7.0 to 3.9.0, the checked GoogleCloudStorageRepository and AzureRepository also override getNativeStore() to return a native object store that the constructor sets when a native provider supplies a live one. Whether that path bypasses the EncryptedBlobStore wrap, and deployed use of it, are not established here.
- os-gcs-azure-index (REASONED; corecrypto350, corecrypto390): At checked OpenSearch tags 3.5.0 to 3.9.0 only, BlobStoreRepository passes CryptoMetadata from index settings to writeBlobWithMetadata for shard files, commented as an index-level SSE-KMS override; repository metadata feeds BlobStoreProvider separately. Source reading, no run: its effective behaviour is unestablished, as is GCS handling of it at 3.6.0 to 3.8.0.
- os-gcs-azure-index-wrap (REASONED; corecrypto350, corecrypto38): From source reading without a run, EncryptedBlobContainer's writeBlobWithMetadata form taking CryptoMetadata, read at 3.5.0 and 3.8.0 and sharing 3.8.0's git blob ID at 3.6.0, 3.7.0 and 3.9.0, encrypts with the repository-level crypto handler and passes the index-level CryptoMetadata unchanged to the wrapped container.
- os-gcs-azure-index-azure (REASONED; azure38, corecrypto350, corecrypto38, corecrypto390): From source reading without a run, AzureBlobContainer, with one git blob ID at every tag 3.5.0 to 3.9.0, throws UnsupportedOperationException when writeBlobWithMetadata receives non-null CryptoMetadata, so an index-level value reaching it, directly or through EncryptedBlobContainer, ends that shard-file write with the exception in source.
- os-gcs-azure-index-gcs (REASONED; corecrypto350, corecrypto390): From source reading at 3.5.0 and 3.9.0 without a run, GoogleCloudStorageBlobContainer overrides only the writeBlobWithMetadata form without CryptoMetadata, which calls writeBlob, and BlobContainer's default for the CryptoMetadata form calls it, so GCS drops the index-level CryptoMetadata. BlobContainer differs from the 3.9.0 file at 3.6.0 to 3.8.0, where GCS handling is unestablished.
- os-gcs-azure-index-setting (REASONED; corecrypto350, corecrypto390): From source reading at 3.5.0 and 3.9.0, CryptoMetadata.fromIndexSettings returns null unless the index setting index.store.crypto.key_provider is set, with key_provider_type defaulting to aws-kms, so in the snapshot path only such indices pass a non-null index-level value to writeBlobWithMetadata.
- os-gcs-azure-index-advice (REASONED; corecrypto350, corecrypto390): This guide's advice, from source reading at 3.5.0 and 3.9.0 without a run: do not rely on index.store.crypto.key_provider to encrypt GCS/Azure snapshots. Shard-file writes pass its CryptoMetadata to the container, which Azure rejects with UnsupportedOperationException, directly or through EncryptedBlobContainer, and GCS drops; settability and effective behaviour are unestablished.
- os-gcs-azure-native-use (REASONED; corecrypto370, corecrypto390): From source reading without a run, BlobStoreRepository has no native-store reference at 3.7.0 or 3.9.0, and a search of 3.9.0 finds IndexService as the only non-test getNativeStore() caller, for a warm index's remote store repository. Whether the native store applies repository encryption, and callers at 3.7.0 and 3.8.0, are not established here.
- os-gcs-azure-pre210 (REASONED; repo290, corecrypto290): From source reading, git tree listings at the 41 OpenSearch release tags 1.0.0 to 2.9.0 contain no EncryptedBlobStore, CryptoSettings or crypto-kms path; at 2.9.0, blobStore() returns createBlobStore() unwrapped, PutRepositoryRequest parses only type and settings, and RepositoryMetadata has no crypto field.
- os-gcs-azure-validate (REASONED; corecrypto210, corecrypto300, corecrypto38): From source reading and git blob IDs, CryptoSettings.java at 2.11.0 and 2.11.1 matches the cited 2.10.0 file and at every tag 2.12.0 to 3.9.0 the cited 3.0.0 and 3.8.0 files, so validate() requires key_provider_name and key_provider_type at all 31 checked tags 2.10.0 to 3.9.0; no run.
- snapshot-integrity (REASONED; es819): Keep repositories private and keys recoverable; do not rewrite active repository files. Configuration backups are separate and security-state snapshots are sensitive.
- kibana-default (REASONED; kb, kb8, kb9): Kibana defaults HTTP localhost:5601 with server TLS disabled; 8.19.22/9.5.4 Docker templates explicitly use wildcard host, requiring override/publication review.
- kibana-tls (REASONED; kb): Free Basic 8.19 server.ssl certificate/key protects incoming UI traffic; elasticsearch.ssl CA/full verification protects the separate backend hop.
- dash-default (REASONED; dash): Dashboards 3.8.0 sample defaults localhost:5601 with server TLS disabled; inspect installation/container overrides.
- dash-tls (REASONED; dash36): Dashboards server.ssl protects UI, cookie.secure restricts session cookie to HTTPS, and opensearch.ssl CA/full verification protects the backend hop; restart after changes.
- ui-network (REASONED; kb, dash36): UI binding is independent of 9200/9300; loopback suits only a same-namespace proxy, while private access requires intended interface, matching certificates and network restrictions.
- verify-rbac (REASONED; es, os): Known app-data/other-data documents distinguish broad access from scoped 200/403 for user and key; 401/404/errors are inconclusive and pre-3.7 OpenSearch uses the user only.
- verify-anonymous (REASONED; es, os): Require effective anonymous settings on every node plus a formerly anonymous-readable known document becoming 401 while admin still gets 200; endpoint-specific 401 alone is insufficient.
- verify-tls (REASONED; es, os): Admin HTTPS must return 200/cluster JSON before interpreting plaintext; TLS listener must return no HTTP status, with DNS/timeouts/unreachable states inconclusive.
- verify-cors (REASONED; es, os): Inspect preflight headers: no grant to untrusted origin, exact grant for trusted enabled origin; with CORS disabled neither is granted.
- verify-audit (REASONED; es, os): Fresh failed-authentication probe must correlate with new authentication_failed/FAILED_LOGIN in node and independent collector records; 401 alone proves no delivery.
- verify-audit-body (REASONED; es, os): Compare unique marker present with body logging enabled and absent from a new matching event when disabled; independently verify header exclusion and effective configuration.
- verify-listeners (REASONED; es8, es9, host): Locate actual running listeners/ports and inspect publication; intentional bridge-container wildcard differs from host-network exposure and no output alone is inconclusive.
- verify-fls-dls (REASONED; es819, os36): Two-tenant fixture compares unrestricted and actual restricted credentials through search, GET, requested fields and aggregations, with allowed-field and administrator controls; no inference-proof claim.
- verify-storage (REASONED; host): Data-path device chain must traverse intended encryption mapping; unrelated mapping or successful unlocked reads proves nothing, and provider volumes need their own metadata.
- verify-mount (REASONED; host): Isolated unavailable-mount fixture must fail startup for that reason without writes to the ordinary directory; restored encrypted mount must start successfully.
- verify-snapshot (REASONED; es819, os36): Harmless explicit-index snapshot/restore must complete and preserve both fixtures without global/security state; timeouts need operation-state inspection before retry.
- verify-object-key (REASONED; cloud): Inspect actual new/retained repository object mode/key; controlled object-read and KMS-only denial need provider evidence plus authorized controls. Repository verify proves neither encryption nor isolation.
- verify-ui (REASONED; kb, dash36, host): Require expected CA-validated HTTPS and rejected plaintext UI after an exposed HTTP fixture; verify prohibited-network denial with authorized success and effective private binding.
- verify-ui-backend (REASONED; kb, dash36): Browser TLS does not prove backend full verification or Dashboards Secure cookie; inspect both separately with effective settings and publication.

````json
{
  "schema": 1,
  "checked": "2026-10-22",
  "documentation_checked": "2026-09",
  "body_sha256": "9a65ace06f9b08f91e0664ab1c5714f957a50cb461bedd3452d452a9cd450509",
  "components": {
    "es-api": {
      "name": "Elasticsearch API",
      "basis": "8.x",
      "sources": {
        "s088db4f93f33": "https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role",
        "s0c10cfba4d6b": "https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role-mapping",
        "sb82b2da8da5d": "https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-user",
        "sbec1f2938348": "https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-create-api-key"
      }
    },
    "es819": {
      "name": "Elasticsearch reference",
      "basis": "8.19",
      "sources": {
        "s805957cad810": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-level-security.html",
        "s52adbc714b10": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/document-level-security.html",
        "s15feb5b3e00c": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/field-and-document-access-control.html",
        "se332a9504a82": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/security-limitations.html",
        "s03b37cd41154": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/tune-for-search-speed.html",
        "s1ce03cd781c3": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/path-settings-overview.html",
        "s3cac63e6ba14": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-s3.html",
        "s28a1fe315963": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-gcs.html",
        "s6279b842bc10": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/repository-azure.html",
        "sb98bd971e2f6": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-take-snapshot.html",
        "s93987af8201d": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshot-restore.html",
        "s3e5630e4430d": "https://www.elastic.co/guide/en/elasticsearch/reference/8.19/snapshots-restore-snapshot.html"
      }
    },
    "es8": {
      "name": "Elasticsearch listener source",
      "basis": "8.19.22",
      "sources": {
        "sa56cdc9270ea": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L112-L121",
        "s46c7adfdc6c4": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L233-L239",
        "s8ca2413b2af3": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L28-L42",
        "s59c2dd10f083": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/http/HttpTransportSettings.java#L70-L89",
        "s0310c5c2e42f": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/server/src/main/java/org/elasticsearch/transport/TransportSettings.java#L34-L62",
        "s6e6cf4d739bd": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L788-L821",
        "s70c493fe7770": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L876-L891",
        "s8d4c513fdf84": "https://github.com/elastic/elasticsearch/blob/3b2a41103de35e0af4064d647974032fcc1bcde9/distribution/docker/src/docker/config/elasticsearch.yml#L1-L2"
      }
    },
    "es9": {
      "name": "Elasticsearch listener source",
      "basis": "9.5.4",
      "sources": {
        "s666c63ad2a02": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L112-L121",
        "s429c675c1092": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L233-L239",
        "sa27fc323d90c": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/common/network/NetworkService.java#L28-L42",
        "s8fded6a7640c": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/http/HttpTransportSettings.java#L64-L83",
        "s1f0a06e68675": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/server/src/main/java/org/elasticsearch/transport/TransportSettings.java#L34-L57",
        "scf100fafec80": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L800-L833",
        "s0ba542d80d53": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/x-pack/plugin/security/cli/src/main/java/org/elasticsearch/xpack/security/cli/AutoConfigureNode.java#L888-L903",
        "sa4fd281c6186": "https://github.com/elastic/elasticsearch/blob/9170df19cae1adb107b7b489b4d82dec66d7a337/distribution/docker/src/docker/config/elasticsearch.yml#L1-L2"
      }
    },
    "os36": {
      "name": "OpenSearch reference",
      "basis": "3.6",
      "sources": {
        "s42d975e3cd92": "https://docs.opensearch.org/3.6/security/access-control/field-level-security/",
        "sade7ff6b2bb3": "https://docs.opensearch.org/3.6/security/access-control/document-level-security/",
        "sf0940d73ed6e": "https://docs.opensearch.org/3.6/tuning-your-cluster/availability-and-recovery/snapshots/snapshot-restore/"
      }
    },
    "os31": {
      "name": "OpenSearch S3 reference",
      "basis": "3.1",
      "sources": {
        "s089decb3330d": "https://docs.opensearch.org/3.1/api-reference/snapshots/create-repository/"
      }
    },
    "os38": {
      "name": "OpenSearch S3 source",
      "basis": "3.8.0",
      "sources": {
        "sc57180db39be": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-s3/src/main/java/org/opensearch/repositories/s3/S3Repository.java"
      }
    },
    "gcs38": {
      "name": "OpenSearch GCS source",
      "basis": "3.8.0",
      "sources": {
        "s631e8e354e26": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStoragePlugin.java#L125-L144",
        "s9ff434d5553c": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L74-L84",
        "s7e94d736aed9": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L259-L266",
        "s1f1e29ea0106": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L289-L291",
        "sfe65ec0f6f8c": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L370-L373",
        "s90d52029d8d8": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L147-L150",
        "sfa59a5382e57": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageService.java#L247-L285"
      }
    },
    "azure38": {
      "name": "OpenSearch Azure source",
      "basis": "3.8.0",
      "sources": {
        "s85d096884518": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepositoryPlugin.java#L133-L153",
        "sc2902fffc253": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L75-L107",
        "s22bd450a8a30": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L351-L394",
        "sa4a6997abb47": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157",
        "s287622988f18": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L185-L200",
        "sdea961e1b3be": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureStorageService.java#L195-L239"
      }
    },
    "corecrypto38": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.8.0",
      "sources": {
        "sb8b00bcc45a2": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/action/admin/cluster/repositories/put/PutRepositoryRequest.java#L248-L271",
        "s6599b9d988eb": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L54-L63",
        "s72395c1b171c": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L44-L96",
        "s85afe5ff10ee": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1073-L1085",
        "sa01a018a581d": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L39-L51",
        "s248fbcd97369": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67",
        "s0ed030669257": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L94-L110",
        "s726bdb2f7cab": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/crypto/CryptoHandlerRegistry.java#L144-L167",
        "s73ce68ed27f1": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/crypto-kms/src/main/java/org/opensearch/crypto/kms/CryptoKmsPlugin.java#L26-L27",
        "sc99eb8d33be7": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60",
        "sef269e173cbc": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72",
        "s2ee18ff27a14": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49",
        "sb739f2d2b9bb": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1098",
        "s6624e4bb01fd": "https://github.com/opensearch-project/OpenSearch/blob/3.8.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L147-L170"
      }
    },
    "dash": {
      "name": "OpenSearch Dashboards",
      "basis": "3.8.0",
      "sources": {
        "sae1b7f23ca6c": "https://raw.githubusercontent.com/opensearch-project/OpenSearch-Dashboards/3.8.0/config/opensearch_dashboards.yml"
      }
    },
    "dash36": {
      "name": "Dashboards TLS reference",
      "basis": "3.6",
      "sources": {
        "sea686fca5804": "https://docs.opensearch.org/3.6/install-and-configure/install-dashboards/tls/"
      }
    },
    "es": {
      "name": "Elasticsearch documentation",
      "basis": "unknown",
      "sources": {
        "sad43b70af67a": "https://www.elastic.co/subscriptions",
        "s64e4e307f36c": "https://www.elastic.co/docs/deploy-manage/security/self-auto-setup",
        "se8bbf661f24e": "https://www.elastic.co/docs/reference/elasticsearch/command-line-tools/reset-password",
        "sce3095052f8d": "https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings",
        "s38b60fd8e2bf": "https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-configure",
        "sc3d6362bc8f4": "https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/ldap",
        "s0c10cfba4d6b": "https://www.elastic.co/docs/api/doc/elasticsearch/v8/operation/operation-security-put-role-mapping",
        "s204396515260": "https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access",
        "s0f65658e7273": "https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings",
        "s2882d7d6f2fc": "https://www.elastic.co/docs/deploy-manage/security/logging-configuration/enabling-audit-logs",
        "s5603a653318d": "https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/auding-settings",
        "s4fb9bf780cf5": "https://www.elastic.co/pdf/subscriptions-2025-07-29.pdf",
        "see6eaa520863": "https://www.elastic.co/docs/reference/elasticsearch/security-privileges",
        "sfc6fef9020b3": "https://www.elastic.co/docs/reference/elasticsearch/elasticsearch-audit-events"
      }
    },
    "images": {
      "name": "Elasticsearch Docker library",
      "basis": "8480a06d8ca03ca7da29a469fdbddb5f9f31df61",
      "sources": {
        "s09177781dc63": "https://github.com/docker-library/official-images/blob/8480a06d8ca03ca7da29a469fdbddb5f9f31df61/library/elasticsearch#L2-L19",
        "sae45a2b7731f": "https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/config/elasticsearch.yml",
        "sab290cdf87a1": "https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/config/elasticsearch.yml",
        "s7088372053e9": "https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/config/elasticsearch.yml",
        "s0c3512f7e923": "https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/Dockerfile#L123",
        "s1683d032b409": "https://github.com/elastic/dockerfiles/blob/0208be14db8ebd2e40442d328e8f79921368c5a9/elasticsearch/Dockerfile#L38",
        "s6c51d507efec": "https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/Dockerfile#L57",
        "s5c4452cc7b82": "https://github.com/elastic/dockerfiles/blob/18bba4670aa9212cd0c5e8aeff5aa2f23d7f652a/elasticsearch/Dockerfile#L99",
        "s849d2f17dbc8": "https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/Dockerfile#L57",
        "s30233ea32bf6": "https://github.com/elastic/dockerfiles/blob/25fdea1109a231cedf9d1d3cf78bbb7fce488561/elasticsearch/Dockerfile#L99"
      }
    },
    "os": {
      "name": "OpenSearch documentation",
      "basis": "unknown",
      "sources": {
        "s73e416ebf765": "https://docs.opensearch.org/latest/security/configuration/demo-configuration/",
        "s4e3281cb3d23": "https://docs.opensearch.org/latest/security/configuration/tls/",
        "s07ddf2781a70": "https://docs.opensearch.org/latest/security/access-control/users-roles/",
        "s204396515260": "https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/anonymous-access",
        "sc3d6362bc8f4": "https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/ldap",
        "s0e349fff0934": "https://docs.opensearch.org/latest/security/api/roles/create-role/",
        "s4f63d2563816": "https://docs.opensearch.org/latest/security/api/users/create-user/",
        "s1a9aa4907daf": "https://docs.opensearch.org/latest/security/api/role-mappings/create-role-mapping/",
        "sfbdd4a41adf5": "https://docs.opensearch.org/latest/security/access-control/api-keys/",
        "sa596b3a14984": "https://docs.opensearch.org/latest/security/api/api-keys/create/",
        "s40051274ea31": "https://docs.opensearch.org/latest/security/configuration/security-admin/",
        "sc921fd158473": "https://docs.opensearch.org/latest/security/configuration/configuration/",
        "s4142fe7a4236": "https://docs.opensearch.org/latest/security/authentication-backends/basic-authc/",
        "s3f64f7b4cf84": "https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/network-settings/",
        "s2f39d5e48027": "https://docs.opensearch.org/latest/security/audit-logs/index/",
        "seafbd3b9677e": "https://docs.opensearch.org/latest/security/api/audit/patch-audit-configuration/",
        "s0d675c5ecd3c": "https://docs.opensearch.org/latest/security/api/audit/update-audit-configuration/",
        "seafc6e5e5595": "https://docs.opensearch.org/latest/security/api/audit/get-audit-configuration/",
        "s9ddd20a83871": "https://docs.opensearch.org/3.0/troubleshoot/#encryption-at-rest",
        "sbd093eef861b": "https://docs.opensearch.org/latest/security/access-control/permissions/",
        "s7d28cfa527a1": "https://docs.opensearch.org/latest/security/access-control/anonymous-authentication/",
        "sbad13e007c8f": "https://docs.opensearch.org/latest/security/audit-logs/field-reference/"
      }
    },
    "os-license-source": {
      "name": "OpenSearch Security licence source",
      "basis": "4ba3cc0e2ebec61b726b227fdf51e55f4a502182",
      "sources": {
        "s6e10cf9ec35a": "https://github.com/opensearch-project/security/blob/4ba3cc0e2ebec61b726b227fdf51e55f4a502182/LICENSE.txt"
      }
    },
    "os-users-source": {
      "name": "OpenSearch demo users source",
      "basis": "03a224d16045a8f561e2d7d84b8765c95309524c",
      "sources": {
        "se8c473c01153": "https://github.com/opensearch-project/security/blob/03a224d16045a8f561e2d7d84b8765c95309524c/config/internal_users.yml"
      }
    },
    "kb": {
      "name": "Kibana reference",
      "basis": "8.19",
      "sources": {
        "s0fe3c0d2e958": "https://www.elastic.co/guide/en/kibana/8.19/settings.html",
        "sf71765842118": "https://www.elastic.co/guide/en/kibana/8.19/docker.html"
      }
    },
    "kb8": {
      "name": "Kibana source",
      "basis": "8.19.22",
      "sources": {
        "sd77254a631b1": "https://github.com/elastic/kibana/blob/fd8e6f336cd7a18d0fd805de4608e1e38e0da163/config/kibana.yml#L4-L11",
        "s14662915ed7e": "https://github.com/elastic/kibana/blob/fd8e6f336cd7a18d0fd805de4608e1e38e0da163/src/dev/build/tasks/os_packages/docker_generator/templates/kibana_yml.template.ts#L22-L26"
      }
    },
    "kb9": {
      "name": "Kibana source",
      "basis": "9.5.4",
      "sources": {
        "sd0f70697a909": "https://github.com/elastic/kibana/blob/abf4eb613d64cdb3a6290671ce1cb67399677ab3/src/core/packages/http/server-internal/src/http_config.ts#L146-L155",
        "s39aaa733de4b": "https://github.com/elastic/kibana/blob/abf4eb613d64cdb3a6290671ce1cb67399677ab3/src/dev/build/tasks/os_packages/docker_generator/templates/kibana_yml.template.ts#L22-L26"
      }
    },
    "cloud": {
      "name": "Cloud provider documentation",
      "basis": "unknown",
      "sources": {
        "s710600aeb168": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-encryption-faq.html",
        "sdc6a5af591ff": "https://docs.cloud.google.com/storage/docs/encryption",
        "saeb8db497f20": "https://learn.microsoft.com/en-us/azure/storage/common/storage-service-encryption",
        "se1e1c91f80b4": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html",
        "se54783905d19": "https://docs.aws.amazon.com/cli/latest/reference/s3api/head-object.html",
        "sc53339f5429f": "https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html"
      }
    },
    "host": {
      "name": "Host inspection documentation",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html",
        "s64522c42b5bc": "https://man7.org/linux/man-pages/man5/systemd.unit.5.html",
        "s1b4e67e38127": "https://manpages.ubuntu.com/manpages/noble/man8/ss.8.html",
        "s42b4720299f5": "https://man7.org/linux/man-pages/man8/findmnt.8.html",
        "sd23c3d0f42a7": "https://man7.org/linux/man-pages/man8/lsblk.8.html",
        "s252144371961": "https://man7.org/linux/man-pages/man8/cryptsetup-status.8.html",
        "s9823c4e9efa4": "https://man7.org/linux/man-pages/man1/systemctl.1.html"
      }
    },
    "corecrypto210": {
      "name": "OpenSearch repository crypto source",
      "basis": "2.10.0",
      "sources": {
        "s023fb522ed72": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L52-L61",
        "scd89fded9c2c": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L764-L788",
        "s1753e87e88dc": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L56",
        "s0ead2431acaf": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L126-L129",
        "sc0efd9a1f6ae": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L68",
        "sf884a4d2d3de": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L164-L179",
        "sa2c0bdc87a61": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L56-L154",
        "sd5b6e9a0dcbf": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L68-L195",
        "s727ebb33c49f": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L51-L81",
        "sff599e8b12c9": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L27",
        "se48bbb367fc8": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L33",
        "s5a5e01f70ec4": "https://github.com/opensearch-project/OpenSearch/blob/eee49cb340edc6c4d489bcd9324dda571fc8dc03/release-notes/opensearch.release-notes-2.10.0.md#L35"
      }
    },
    "corecrypto300": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.0.0",
      "sources": {
        "s3c28c995eb5e": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/action/admin/cluster/crypto/CryptoSettings.java#L54-L63",
        "s93b4c5889273": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L989-L1013",
        "sab6693a23f6b": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58",
        "sc211cd4c1f4c": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L121-L124",
        "s1917cf59aef1": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70",
        "s25b324a4f06c": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L159-L174",
        "s2666ebb6c559": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158",
        "s9e2a009146a3": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199",
        "se0f7b814bf36": "https://github.com/opensearch-project/OpenSearch/blob/dc4efa821904cc2d7ea7ef61c0f577d3fc0d8be9/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74"
      }
    },
    "corecrypto290": {
      "name": "OpenSearch crypto directory source",
      "basis": "2.9.0",
      "sources": {
        "s3a525ebc7971": "https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/action/admin/cluster",
        "sead7f18b1232": "https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/common/blobstore",
        "s024162999a7b": "https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch",
        "s44e4cbf700e2": "https://github.com/opensearch-project/OpenSearch/tree/1164221ee2b8ba3560f0ff492309867beea28433/plugins"
      }
    },
    "repo290": {
      "name": "OpenSearch repository source",
      "basis": "2.9.0",
      "sources": {
        "s1429acf43e09": "https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L738-L759",
        "s29b704159bed": "https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/action/admin/cluster/repositories/put/PutRepositoryRequest.java#L215-L230",
        "sde8f172dc83a": "https://github.com/opensearch-project/OpenSearch/blob/1164221ee2b8ba3560f0ff492309867beea28433/server/src/main/java/org/opensearch/cluster/metadata/RepositoryMetadata.java#L54-L66"
      }
    },
    "corecrypto332": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.3.2",
      "sources": {
        "sc9bf4ddcb6b8": "https://github.com/opensearch-project/OpenSearch/blob/3.3.2/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1054-L1078",
        "sc698b1eaf1b9": "https://github.com/opensearch-project/OpenSearch/blob/3.3.2/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74",
        "sc966e4e32c2d": "https://github.com/opensearch-project/OpenSearch/blob/3.3.2/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158",
        "scbde9cb6c4f2": "https://github.com/opensearch-project/OpenSearch/blob/3.3.2/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199"
      }
    },
    "corecrypto340": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.4.0",
      "sources": {
        "s2710220c82ef": "https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1062-L1084",
        "s93515a5194f1": "https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74",
        "s583f753b638a": "https://github.com/opensearch-project/OpenSearch/blob/3.4.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L58-L158",
        "saeb525d0d79c": "https://github.com/opensearch-project/OpenSearch/blob/3.4.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L70-L199",
        "s91e8f2833946": "https://github.com/opensearch-project/OpenSearch/blob/3.4.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L41-L85"
      }
    },
    "corecrypto350": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.5.0",
      "sources": {
        "s62de82f8d4cb": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L219",
        "s61bf5c7bfd08": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1063-L1085",
        "s72ddf836f1b8": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L2977-L2979",
        "s57654075d803": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L3950-L3962",
        "s68ca8d1a394b": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4147-L4148",
        "s0140e5bf55b1": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4155-L4189",
        "s1c12f9fcef29": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4819-L4870",
        "s7ef8ce8a4ac4": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4958-L4964",
        "s95b294817514": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L94-L170",
        "s8d7160a829ab": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L137-L140",
        "s7bc6ade23073": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L173-L176",
        "sfe634bf6d4ab": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobContainer.java#L49-L109",
        "sb54cc172630f": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/BlobContainer.java#L200-L211",
        "s506f986010d1": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/support/AbstractBlobContainer.java#L43-L56",
        "s4ed93634b781": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L63",
        "s69354bfdd8f2": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157",
        "sac7d3cdfc8be": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67",
        "scaf794c9d5af": "https://github.com/opensearch-project/OpenSearch/blob/3.5.0/server/src/main/java/org/opensearch/cluster/metadata/CryptoMetadata.java#L114-L124"
      }
    },
    "corecrypto370": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.7.0",
      "sources": {
        "sad5d975fe638": "https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60-L195",
        "s8e950b4d9a68": "https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L191-L194",
        "s60ec9ebfbf05": "https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72-L236",
        "s3aebcdd4cb2c": "https://github.com/opensearch-project/OpenSearch/blob/3.7.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L232-L235",
        "sc98196d18b9d": "https://github.com/opensearch-project/OpenSearch/blob/3.7.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1-L4970"
      }
    },
    "corecrypto390": {
      "name": "OpenSearch repository crypto source",
      "basis": "3.9.0",
      "sources": {
        "se6ddbbe96249": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1063-L1085",
        "sc5bf05ecf0ea": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/MeteredBlobStoreRepository.java#L49-L74",
        "s00eccfed064d": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageRepository.java#L60-L195",
        "se96a858ba821": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureRepository.java#L72-L236",
        "sb290569596b4": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L219",
        "se3aad09d8497": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L2982-L2984",
        "s37f9458d6d94": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L3955-L3967",
        "s0f9808fc0616": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4152-L4153",
        "sf18e2d0fe0ca": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4160-L4194",
        "s14212c0feb93": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4824-L4875",
        "sf2a546029708": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L4963-L4969",
        "sadf2ab29004a": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreProvider.java#L44-L96",
        "s1a6b8421dc88": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/repositories/blobstore/BlobStoreRepository.java#L1-L4970",
        "sec74049ea092": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/index/IndexService.java#L794-L812",
        "s087ff902509f": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/index/IndexService.java#L1429-L1440",
        "s999b7dcb4962": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobContainer.java#L49-L109",
        "sc2b83444a4d8": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/BlobContainer.java#L201-L212",
        "sd4b63b629d2a": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/support/AbstractBlobContainer.java#L43-L56",
        "s880359b13972": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/cluster/metadata/CryptoMetadata.java#L114-L124",
        "sd4ffb3ed8742": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-gcs/src/main/java/org/opensearch/repositories/gcs/GoogleCloudStorageBlobStore.java#L137-L140",
        "s772ecf3c6791": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobStore.java#L173-L176",
        "sf11ab30b7e98": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L63",
        "s3fb393e9a1cf": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/plugins/repository-azure/src/main/java/org/opensearch/repositories/azure/AzureBlobContainer.java#L140-L157",
        "s17887e310f78": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobStore.java#L60-L67",
        "sd098c5f679f0": "https://github.com/opensearch-project/OpenSearch/blob/3.9.0/server/src/main/java/org/opensearch/common/blobstore/EncryptedBlobContainer.java#L147-L170"
      }
    }
  },
  "claims": {
    "es-tier": {"text": "Self-managed 8.x TLS, native users, RBAC, REST keys, anonymous controls and CORS are free Basic; LDAP/audit and FLS/DLS require Platinum/Enterprise, with current Platinum restricted to existing customers.", "components": ["es"], "sources": ["es:sad43b70af67a"], "status": "REASONED"},
    "es-auto": {"text": "Eligible initial startup enables auth, HTTP/transport TLS and elastic password; redirected output, unwritable config or existing settings can skip setup, with stated discovery exceptions; packages require password reset.", "components": ["es"], "sources": ["es:s64e4e307f36c", "es:se8bbf661f24e"], "status": "REASONED"},
    "es-tls": {"text": "Keep xpack.security.enabled and HTTP TLS enabled; repair CA trust/certificates instead of disabling protection.", "components": ["es"], "sources": ["es:sce3095052f8d"], "status": "REASONED"},
    "es-bind": {"text": "network.host defaults `_local_` on up interfaces across available families; family-specific tokens and HTTP/profile bind overrides apply before network fallback.", "components": ["es8", "es9"], "sources": ["es8:sa56cdc9270ea", "es8:s46c7adfdc6c4", "es8:s8ca2413b2af3", "es9:s666c63ad2a02", "es9:s429c675c1092", "es9:sa27fc323d90c"], "status": "REASONED"},
    "es-http-range": {"text": "HTTP defaults to an available port in 9200-9300, subject to effective host/bind/publish settings.", "components": ["es8", "es9"], "sources": ["es8:s59c2dd10f083", "es9:s8fded6a7640c"], "status": "REASONED"},
    "es-transport-range": {"text": "Transport defaults to an available port in 9300-9399; inspect effective profile and actual listener ports.", "components": ["es8", "es9"], "sources": ["es8:s0310c5c2e42f", "es9:s1f0a06e68675"], "status": "REASONED"},
    "es-auto-http": {"text": "Auto-configuration writes http.host=0.0.0.0 only when none of the three HTTP or three network address settings has a value, including enrollment.", "components": ["es8", "es9"], "sources": ["es8:s6e6cf4d739bd", "es9:scf100fafec80"], "status": "REASONED"},
    "es-auto-transport": {"text": "Transport address guard respects existing settings; new-cluster wildcard is commented and enrollment activates it only for a discovered nonlocal, nonloopback publish address.", "components": ["es8", "es9"], "sources": ["es8:s6e6cf4d739bd", "es8:s70c493fe7770", "es9:scf100fafec80", "es9:s0ba542d80d53"], "status": "REASONED"},
    "es-docker": {"text": "Pinned image map covers 8.19.22/9.4.6/9.5.3; shipped network.host=0.0.0.0 widens API and transport unless overridden. EXPOSE includes 9300, so avoid -P, host networking and untrusted peers.", "components": ["images", "es"], "sources": ["images:s09177781dc63", "images:sae45a2b7731f", "images:sab290cdf87a1", "images:s7088372053e9", "images:s0c3512f7e923", "images:s1683d032b409", "images:s6c51d507efec", "images:s5c4452cc7b82", "images:s849d2f17dbc8", "images:s30233ea32bf6", "es:s38b60fd8e2bf"], "status": "REASONED"},
    "es-source-docker": {"text": "Source configurations at 8.19.22/9.5.4 also set network.host wildcard, making both auto-configuration address guards false.", "components": ["es8", "es9"], "sources": ["es8:s8d4c513fdf84", "es9:sa4fd281c6186"], "status": "REASONED"},
    "es-role": {"text": "Give each app an index-read role and dedicated native user; manage_own_api_key permits self-issued keys without broader index access, and superuser is not an app role.", "components": ["es-api"], "sources": ["es-api:s088db4f93f33", "es-api:s0c10cfba4d6b", "es-api:sb82b2da8da5d"], "status": "REASONED"},
    "credential-files": {"text": "Use protected 0600 header/request/response files and verified CA input; base64 Basic is not encryption and file input does not prevent file readers or tracing.", "components": ["host"], "sources": ["host:s2b2686afaf41"], "status": "REASONED"},
    "es-key": {"text": "Explicit API-key role descriptors intersect creator permissions; omitted descriptors inherit a snapshot, omitted expiration never expires, and an API key cannot create another privileged key.", "components": ["es-api"], "sources": ["es-api:sbec1f2938348"], "status": "REASONED"},
    "es-ldap": {"text": "Optional paid LDAP mapping binds the specific realm and group DN; native-user roles are assigned through the user API.", "components": ["es"], "sources": ["es:sc3d6362bc8f4", "es:s0c10cfba4d6b"], "status": "REASONED"},
    "es-fls": {"text": "8.19 field_security.grant restricts concrete fields, not aliases; metadata remains accessible and omission grants all fields. Minimum guide scope 8.0 is not an introduction claim.", "components": ["es819"], "sources": ["es819:s805957cad810"], "status": "REASONED"},
    "es-dls": {"text": "8.19 query restricts documents; omission removes DLS. Keep tenant readers read-only and remove unrestricted roles that combine to defeat restrictions.", "components": ["es819"], "sources": ["es819:s52adbc714b10", "es819:s15feb5b3e00c"], "status": "REASONED"},
    "es-fls-limits": {"text": "DLS has aggregate/scoring inference channels and query/API restrictions including joins, lookups, percolate and date now; test actual queries and prefer separate indices for stronger isolation.", "components": ["es819"], "sources": ["es819:se332a9504a82"], "status": "REASONED"},
    "es-key-review": {"text": "Review previously issued key permission snapshots separately after changing roles; role edits alone do not establish repaired key restrictions.", "components": ["es819"], "sources": ["es819:s15feb5b3e00c"], "status": "REASONED"},
    "es-anonymous": {"text": "Remove anonymous.roles from every effective node configuration and restart; no roles disables anonymous access. A tested 401 alone cannot prove it is globally off.", "components": ["es"], "sources": ["es:s204396515260"], "status": "REASONED"},
    "es-cors": {"text": "CORS defaults disabled; if needed configure exact origin, methods and headers, restart nodes and retain authorization.", "components": ["es"], "sources": ["es:s0f65658e7273"], "status": "REASONED"},
    "es-audit": {"text": "Audit defaults disabled; enable on each 8.x node with restart and collect CLUSTERNAME_audit.json independently. Dynamic enablement documented for 9.5+ does not apply to 8.x.", "components": ["es"], "sources": ["es:s2882d7d6f2fc"], "status": "REASONED"},
    "es-audit-body": {"text": "Request-body emission defaults false; keep it off and avoid event exclusions/ignore policies suppressing authentication_failed.", "components": ["es"], "sources": ["es:s5603a653318d"], "status": "REASONED"},
    "os-tier": {"text": "OpenSearch Security is free Apache-2.0 with no paid security tier; keep authentication and TLS enabled.", "components": ["os-license-source"], "sources": ["os-license-source:s6e10cf9ec35a"], "status": "REASONED"},
    "os-demo-users": {"text": "From 2.12 demo setup requires initial admin password but only changes admin; six other seeded users retain demo credentials until removed/replaced and applied to the live security index.", "components": ["os", "os-users-source"], "sources": ["os:s73e416ebf765", "os-users-source:se8c473c01153"], "status": "REASONED"},
    "os-tls": {"text": "Replace demo certificates; REST TLS defaults false underneath demo setup and requires plugins.security.ssl.http.enabled=true with production certificates.", "components": ["os"], "sources": ["os:s4e3281cb3d23"], "status": "REASONED"},
    "os-rbac": {"text": "Create a custom index-read role and internal user with explicit mapping; Security REST administration requires its own authorization and other mappings may add grants.", "components": ["os"], "sources": ["os:s07ddf2781a70", "os:s204396515260", "os:sc3d6362bc8f4", "os:s0e349fff0934", "os:s4f63d2563816", "os:s1a9aa4907daf"], "status": "REASONED"},
    "os-api-key": {"text": "Native scoped keys require 3.7+ and security administrators; enable api_tokens and explicit lifetime/count limits, using index_pattern and duration_seconds rather than Elasticsearch fields.", "components": ["os"], "sources": ["os:sfbdd4a41adf5", "os:sa596b3a14984"], "status": "REASONED"},
    "os-key-default": {"text": "Omitted token duration uses max_duration_seconds, documented default 7776000; example caps at 86400 with 100 tokens, and returned token is retrievable only once.", "components": ["os"], "sources": ["os:sa596b3a14984"], "status": "REASONED"},
    "os-apply": {"text": "securityadmin applies local configuration to the live index; back up first, use file/type-limited upload, production CA/admin certificate and hostname verification because stale files overwrite live changes.", "components": ["os"], "sources": ["os:s40051274ea31"], "status": "REASONED"},
    "os-fls": {"text": "3.6 FLS/DLS recipe uses JSON-string dls and visible tenant_id in fls; review all roles and inclusion/exclusion interactions, not Elasticsearch role-combination assumptions.", "components": ["os36"], "sources": ["os36:s42d975e3cd92", "os36:sade7ff6b2bb3"], "status": "REASONED"},
    "os-dls": {"text": "dfm_empty_overrides_all affects unrestricted-role precedence; DLS does not constrain writes and adaptive filter-level DLS limits APIs/cross-cluster search. Tokens need independent restriction tests.", "components": ["os36"], "sources": ["os36:sade7ff6b2bb3"], "status": "REASONED"},
    "os-anonymous": {"text": "Set live anonymous_auth_enabled=false while preserving authentication domains; update through securityadmin, not just local YAML.", "components": ["os"], "sources": ["os:sc921fd158473", "os:s4142fe7a4236"], "status": "REASONED"},
    "os-cors": {"text": "CORS defaults false; exact-origin static settings go in opensearch.yml and require restart, independently of authentication.", "components": ["os"], "sources": ["os:s3f64f7b4cf84"], "status": "REASONED"},
    "os-audit": {"text": "Auditing needs destination and enabled config; internal_opensearch stores daily audit indexes, while shipped enabled=true alone records nothing without storage type.", "components": ["os"], "sources": ["os:s2f39d5e48027"], "status": "REASONED"},
    "os-audit-body": {"text": "Read live audit config, enable REST and disable request-body logging via admin-certificate PATCH; preserve defaults and do not suppress FAILED_LOGIN.", "components": ["os"], "sources": ["os:seafbd3b9677e", "os:s0d675c5ecd3c"], "status": "REASONED"},
    "os-audit-headers": {"text": "exclude_sensitive_headers defaults true; readonly REST fields require complete audit-file application. Read back enabled, REST, body=false and headers=true separately.", "components": ["os"], "sources": ["os:seafc6e5e5595", "os:s0d675c5ecd3c"], "status": "REASONED"},
    "storage": {"text": "Use OS/provider encryption below path.data, including logs/swap/local snapshots; path.data only selects a directory and encryption-at-rest support is not a product encryption switch.", "components": ["es819", "os"], "sources": ["es819:s03b37cd41154", "es819:s1ce03cd781c3", "os:s9ddd20a83871"], "status": "REASONED"},
    "mount-enforcement": {"text": "RequiresMountsFor plus AssertPathIsMountPoint prevents ordinary-directory fallback with systemd; reload manager and verify encrypted device chain separately.", "components": ["host"], "sources": ["host:s64522c42b5bc"], "status": "REASONED"},
    "snapshot-boundary": {"text": "Ordinary snapshots use free Basic/OpenSearch; remote repository encryption is independent of node disks and authorized server-side downloads are decrypted.", "components": ["es", "os31", "cloud"], "sources": ["es:s4fb9bf780cf5", "os31:s089decb3330d", "cloud:s710600aeb168"], "status": "REASONED"},
    "cloud-defaults": {"text": "New AWS S3, GCS and Azure objects are encrypted server-side by default; assess historical objects and customer key ownership separately.", "components": ["cloud"], "sources": ["cloud:s710600aeb168", "cloud:sdc6a5af591ff", "cloud:saeb8db497f20"], "status": "REASONED"},
    "es-s3": {"text": "8.19 server_side_encryption defaults false; true requests AES256 SSE-S3, not client encryption. Omit it when using bucket-default KMS and verify resulting metadata.", "components": ["es819"], "sources": ["es819:s3cac63e6ba14"], "status": "REASONED"},
    "os-s3": {"text": "3.1 removed server_side_encryption; server_side_encryption_type accepts AES256/aws:kms/bucket_default. Default changed from bucket_default to AES256 in 3.8; explicitly select intended mode.", "components": ["os31", "os38"], "sources": ["os31:s089decb3330d", "os38:sc57180db39be"], "status": "REASONED"},
    "os-s3-kms": {"text": "Explicit KMS repository mode uses server_side_encryption_kms_key_id ARN with object/KMS permissions; this is server-side encryption and settings are not Elasticsearch-compatible.", "components": ["os31", "cloud"], "sources": ["os31:s089decb3330d", "cloud:se1e1c91f80b4"], "status": "REASONED"},
    "es-gcs-azure": {"text": "8.19 GCS/Azure setting lists document no client-side-encryption switch; configure provider key policy and access. GCS supplied keys remain server-side and Azure keys/SAS are authentication.", "components": ["es819"], "sources": ["es819:s28a1fe315963", "es819:s6279b842bc10"], "status": "REASONED"},
    "os-gcs-azure": {"text": "Follow the OpenSearch 3.6 plugin/credential workflow, including Azure; this guide's advice is to configure required customer-managed encryption through provider policy and grant key access. Do not infer broader absence from Elasticsearch settings or failed source retrieval.", "components": ["os36", "cloud"], "sources": ["os36:sf0940d73ed6e", "cloud:sdc6a5af591ff", "cloud:saeb8db497f20"], "status": "REASONED"},
    "os-gcs-azure-settings": {"text": "This guide's review of OpenSearch 3.8.0 GCS/Azure plugin-specific settings, blob upload and client construction found no plugin-specific client-side-encryption setting.", "components": ["gcs38", "azure38"], "sources": ["gcs38:s631e8e354e26", "gcs38:s9ff434d5553c", "gcs38:s7e94d736aed9", "gcs38:s1f1e29ea0106", "gcs38:sfe65ec0f6f8c", "gcs38:sfa59a5382e57", "azure38:s85d096884518", "azure38:sc2902fffc253", "azure38:s22bd450a8a30", "azure38:sdea961e1b3be"], "status": "REASONED"},
    "os-gcs-azure-core": {"text": "In the cited OpenSearch 3.8.0 core path, crypto_settings triggers client-side EncryptedBlobStore wrapping of a non-server-side-encryption store and encryption before writes. Common provider and GCS/Azure createBlobStore methods show a path to both types and Azure rejects per-object CryptoMetadata; this guide assesses end-to-end applicability and live behaviour as unestablished.", "components": ["gcs38", "azure38", "corecrypto38"], "sources": ["gcs38:s90d52029d8d8", "azure38:sa4a6997abb47", "azure38:s287622988f18", "corecrypto38:sb8b00bcc45a2", "corecrypto38:s72395c1b171c", "corecrypto38:s85afe5ff10ee", "corecrypto38:sa01a018a581d", "corecrypto38:s248fbcd97369", "corecrypto38:s0ed030669257", "corecrypto38:sc99eb8d33be7", "corecrypto38:sef269e173cbc", "corecrypto38:s2ee18ff27a14", "corecrypto38:sb739f2d2b9bb"], "status": "REASONED"},
    "os-gcs-azure-providers": {"text": "The cited 3.8.0 path requires key_provider_name, key_provider_type and a registered provider of that type; the tree includes aws-kms. This guide's assessment: deployed providers, end-to-end applicability, live behaviour, a universal GCS/Azure minimum and unchecked-release behaviour remain unestablished.", "components": ["corecrypto38"], "sources": ["corecrypto38:s6599b9d988eb", "corecrypto38:s726bdb2f7cab", "corecrypto38:s73ce68ed27f1"], "status": "REASONED"},
    "os-gcs-azure-versions": {"text": "This guide's assessment from pinned 2.10.0/3.0.0 methods, 2.10.0 release notes and 2.9.0 listings without crypto entries: the checked range with repository crypto settings starts at 2.10.0. Across 31 tags to 3.9.0, blobStore() wraps through 3.3.2 and from 3.4.0 delegates to BlobStoreProvider, which wraps; other releases and a universal deployed GCS/Azure minimum remain unestablished.", "components": ["corecrypto210", "corecrypto300", "corecrypto290", "corecrypto332", "corecrypto340", "corecrypto390", "corecrypto38"], "sources": ["corecrypto210:s023fb522ed72", "corecrypto210:scd89fded9c2c", "corecrypto300:s3c28c995eb5e", "corecrypto300:s93b4c5889273", "corecrypto210:sff599e8b12c9", "corecrypto210:se48bbb367fc8", "corecrypto210:s5a5e01f70ec4", "corecrypto290:s3a525ebc7971", "corecrypto290:sead7f18b1232", "corecrypto290:s024162999a7b", "corecrypto290:s44e4cbf700e2", "corecrypto332:sc9bf4ddcb6b8", "corecrypto340:s2710220c82ef", "corecrypto390:se6ddbbe96249", "corecrypto38:s85afe5ff10ee", "corecrypto38:s72395c1b171c", "corecrypto340:s91e8f2833946", "corecrypto390:sadf2ab29004a"], "status": "REASONED"},
    "os-gcs-azure-path": {"text": "At 2.10.0/3.0.0, GCS/Azure extend MeteredBlobStoreRepository, an abstract BlobStoreRepository subclass declaring neither blobStore() nor createBlobStore, and implement createBlobStore; BlobStoreRepository.blobStore() wraps its result when crypto metadata is non-null. This guide infers both reach the wrap in source; deployed encryption, installed providers and unchecked releases are unestablished.", "components": ["corecrypto210", "corecrypto300"], "sources": ["corecrypto210:scd89fded9c2c", "corecrypto210:s1753e87e88dc", "corecrypto210:s0ead2431acaf", "corecrypto210:sc0efd9a1f6ae", "corecrypto210:sf884a4d2d3de", "corecrypto210:s727ebb33c49f", "corecrypto300:s93b4c5889273", "corecrypto300:sab6693a23f6b", "corecrypto300:sc211cd4c1f4c", "corecrypto300:s1917cf59aef1", "corecrypto300:s25b324a4f06c", "corecrypto300:se0f7b814bf36"], "status": "REASONED"},
    "os-gcs-azure-blobstore": {"text": "At every checked tag 2.10.0 to 3.9.0, the pinned GoogleCloudStorageRepository, AzureRepository and MeteredBlobStoreRepository class bodies declare no blobStore() method; AzureRepository overrides getBlobStore() only to return super.getBlobStore(). This guide's inference that GCS and Azure reach the encryption wrap also relies on that absence and, from 3.4.0, on BlobStoreProvider's wrap.", "components": ["corecrypto210", "corecrypto300", "corecrypto332", "corecrypto340", "corecrypto370", "corecrypto390", "corecrypto38"], "sources": ["corecrypto210:sa2c0bdc87a61", "corecrypto210:sd5b6e9a0dcbf", "corecrypto210:s727ebb33c49f", "corecrypto300:s2666ebb6c559", "corecrypto300:s9e2a009146a3", "corecrypto300:se0f7b814bf36", "corecrypto332:sc698b1eaf1b9", "corecrypto332:sc966e4e32c2d", "corecrypto332:scbde9cb6c4f2", "corecrypto340:s93515a5194f1", "corecrypto340:s583f753b638a", "corecrypto340:saeb525d0d79c", "corecrypto370:sad5d975fe638", "corecrypto370:s60ec9ebfbf05", "corecrypto390:sc5bf05ecf0ea", "corecrypto390:s00eccfed064d", "corecrypto390:se96a858ba821", "corecrypto340:s91e8f2833946", "corecrypto390:sadf2ab29004a", "corecrypto38:s72395c1b171c"], "status": "REASONED"},
    "os-gcs-azure-range": {"text": "At all 25 checked OpenSearch tags 2.10.0 to 3.3.2, BlobStoreRepository.blobStore() has the same body, wrapping the createBlobStore() result in EncryptedBlobStore when crypto metadata is non-null. From 3.4.0 to 3.9.0 it returns blobStore(false) via BlobStoreProvider, which wraps likewise with server-side encryption off (source reading at 3.4.0, 3.8.0, 3.9.0; 3.5.0 to 3.7.0 share 3.4.0's blob ID).", "components": ["corecrypto210", "corecrypto300", "corecrypto332", "corecrypto340", "corecrypto390", "corecrypto38"], "sources": ["corecrypto210:scd89fded9c2c", "corecrypto300:s93b4c5889273", "corecrypto332:sc9bf4ddcb6b8", "corecrypto340:s2710220c82ef", "corecrypto390:se6ddbbe96249", "corecrypto38:s85afe5ff10ee", "corecrypto38:s72395c1b171c", "corecrypto340:s91e8f2833946", "corecrypto390:sadf2ab29004a"], "status": "REASONED"},
    "os-gcs-azure-native": {"text": "From 3.7.0 to 3.9.0, the checked GoogleCloudStorageRepository and AzureRepository also override getNativeStore() to return a native object store that the constructor sets when a native provider supplies a live one. Whether that path bypasses the EncryptedBlobStore wrap, and deployed use of it, are not established here.", "components": ["corecrypto370", "corecrypto390"], "sources": ["corecrypto370:sad5d975fe638", "corecrypto370:s8e950b4d9a68", "corecrypto370:s60ec9ebfbf05", "corecrypto370:s3aebcdd4cb2c", "corecrypto390:s00eccfed064d", "corecrypto390:se96a858ba821"], "status": "REASONED"},
    "os-gcs-azure-index": {"text": "At checked OpenSearch tags 3.5.0 to 3.9.0 only, BlobStoreRepository passes CryptoMetadata from index settings to writeBlobWithMetadata for shard files, commented as an index-level SSE-KMS override; repository metadata feeds BlobStoreProvider separately. Source reading, no run: its effective behaviour is unestablished, as is GCS handling of it at 3.6.0 to 3.8.0.", "components": ["corecrypto350", "corecrypto390"], "sources": ["corecrypto350:s62de82f8d4cb", "corecrypto350:s61bf5c7bfd08", "corecrypto350:s72ddf836f1b8", "corecrypto350:s57654075d803", "corecrypto350:s68ca8d1a394b", "corecrypto350:s0140e5bf55b1", "corecrypto350:s1c12f9fcef29", "corecrypto350:s7ef8ce8a4ac4", "corecrypto390:se6ddbbe96249", "corecrypto390:sb290569596b4", "corecrypto390:se3aad09d8497", "corecrypto390:s37f9458d6d94", "corecrypto390:s0f9808fc0616", "corecrypto390:sf18e2d0fe0ca", "corecrypto390:s14212c0feb93", "corecrypto390:sf2a546029708"], "status": "REASONED"},
    "os-gcs-azure-index-wrap": {"text": "From source reading without a run, EncryptedBlobContainer's writeBlobWithMetadata form taking CryptoMetadata, read at 3.5.0 and 3.8.0 and sharing 3.8.0's git blob ID at 3.6.0, 3.7.0 and 3.9.0, encrypts with the repository-level crypto handler and passes the index-level CryptoMetadata unchanged to the wrapped container.", "components": ["corecrypto350", "corecrypto38"], "sources": ["corecrypto350:s95b294817514", "corecrypto38:s6624e4bb01fd", "corecrypto38:s0ed030669257", "corecrypto38:sa01a018a581d", "corecrypto38:s248fbcd97369"], "status": "REASONED"},
    "os-gcs-azure-index-azure": {"text": "From source reading without a run, AzureBlobContainer, with one git blob ID at every tag 3.5.0 to 3.9.0, throws UnsupportedOperationException when writeBlobWithMetadata receives non-null CryptoMetadata, so an index-level value reaching it, directly or through EncryptedBlobContainer, ends that shard-file write with the exception in source.", "components": ["azure38", "corecrypto350", "corecrypto38", "corecrypto390"], "sources": ["azure38:sa4a6997abb47", "corecrypto350:s95b294817514", "corecrypto350:s1c12f9fcef29", "corecrypto38:s6624e4bb01fd", "corecrypto390:s14212c0feb93", "corecrypto390:s772ecf3c6791"], "status": "REASONED"},
    "os-gcs-azure-index-gcs": {"text": "From source reading at 3.5.0 and 3.9.0 without a run, GoogleCloudStorageBlobContainer overrides only the writeBlobWithMetadata form without CryptoMetadata, which calls writeBlob, and BlobContainer's default for the CryptoMetadata form calls it, so GCS drops the index-level CryptoMetadata. BlobContainer differs from the 3.9.0 file at 3.6.0 to 3.8.0, where GCS handling is unestablished.", "components": ["corecrypto350", "corecrypto390"], "sources": ["corecrypto350:sfe634bf6d4ab", "corecrypto350:sb54cc172630f", "corecrypto350:s506f986010d1", "corecrypto350:s8d7160a829ab", "corecrypto390:s999b7dcb4962", "corecrypto390:sc2b83444a4d8", "corecrypto390:sd4b63b629d2a", "corecrypto390:sd4ffb3ed8742"], "status": "REASONED"},
    "os-gcs-azure-index-setting": {"text": "From source reading at 3.5.0 and 3.9.0, CryptoMetadata.fromIndexSettings returns null unless the index setting index.store.crypto.key_provider is set, with key_provider_type defaulting to aws-kms, so in the snapshot path only such indices pass a non-null index-level value to writeBlobWithMetadata.", "components": ["corecrypto350", "corecrypto390"], "sources": ["corecrypto350:scaf794c9d5af", "corecrypto350:s7ef8ce8a4ac4", "corecrypto350:s1c12f9fcef29", "corecrypto390:s880359b13972", "corecrypto390:sf2a546029708", "corecrypto390:s14212c0feb93"], "status": "REASONED"},
    "os-gcs-azure-index-advice": {"text": "This guide's advice, from source reading at 3.5.0 and 3.9.0 without a run: do not rely on index.store.crypto.key_provider to encrypt GCS/Azure snapshots. Shard-file writes pass its CryptoMetadata to the container, which Azure rejects with UnsupportedOperationException, directly or through EncryptedBlobContainer, and GCS drops; settability and effective behaviour are unestablished.", "components": ["corecrypto350", "corecrypto390"], "sources": ["corecrypto350:s68ca8d1a394b", "corecrypto350:s0140e5bf55b1", "corecrypto350:s1c12f9fcef29", "corecrypto350:s7ef8ce8a4ac4", "corecrypto350:scaf794c9d5af", "corecrypto350:s61bf5c7bfd08", "corecrypto350:s72ddf836f1b8", "corecrypto350:s7bc6ade23073", "corecrypto350:s4ed93634b781", "corecrypto350:s69354bfdd8f2", "corecrypto350:s506f986010d1", "corecrypto350:sac7d3cdfc8be", "corecrypto350:s95b294817514", "corecrypto350:s8d7160a829ab", "corecrypto350:sfe634bf6d4ab", "corecrypto350:sb54cc172630f", "corecrypto390:s0f9808fc0616", "corecrypto390:sf18e2d0fe0ca", "corecrypto390:s14212c0feb93", "corecrypto390:sf2a546029708", "corecrypto390:s880359b13972", "corecrypto390:se6ddbbe96249", "corecrypto390:se3aad09d8497", "corecrypto390:s772ecf3c6791", "corecrypto390:sf11ab30b7e98", "corecrypto390:s3fb393e9a1cf", "corecrypto390:sd4b63b629d2a", "corecrypto390:s17887e310f78", "corecrypto390:sd098c5f679f0", "corecrypto390:sd4ffb3ed8742", "corecrypto390:s999b7dcb4962", "corecrypto390:sc2b83444a4d8"], "status": "REASONED"},
    "os-gcs-azure-native-use": {"text": "From source reading without a run, BlobStoreRepository has no native-store reference at 3.7.0 or 3.9.0, and a search of 3.9.0 finds IndexService as the only non-test getNativeStore() caller, for a warm index's remote store repository. Whether the native store applies repository encryption, and callers at 3.7.0 and 3.8.0, are not established here.", "components": ["corecrypto370", "corecrypto390"], "sources": ["corecrypto370:sc98196d18b9d", "corecrypto390:s1a6b8421dc88", "corecrypto390:sec74049ea092", "corecrypto390:s087ff902509f"], "status": "REASONED"},
    "os-gcs-azure-pre210": {"text": "From source reading, git tree listings at the 41 OpenSearch release tags 1.0.0 to 2.9.0 contain no EncryptedBlobStore, CryptoSettings or crypto-kms path; at 2.9.0, blobStore() returns createBlobStore() unwrapped, PutRepositoryRequest parses only type and settings, and RepositoryMetadata has no crypto field.", "components": ["repo290", "corecrypto290"], "sources": ["repo290:s1429acf43e09", "repo290:s29b704159bed", "repo290:sde8f172dc83a", "corecrypto290:s3a525ebc7971", "corecrypto290:sead7f18b1232", "corecrypto290:s024162999a7b", "corecrypto290:s44e4cbf700e2"], "status": "REASONED"},
    "os-gcs-azure-validate": {"text": "From source reading and git blob IDs, CryptoSettings.java at 2.11.0 and 2.11.1 matches the cited 2.10.0 file and at every tag 2.12.0 to 3.9.0 the cited 3.0.0 and 3.8.0 files, so validate() requires key_provider_name and key_provider_type at all 31 checked tags 2.10.0 to 3.9.0; no run.", "components": ["corecrypto210", "corecrypto300", "corecrypto38"], "sources": ["corecrypto210:s023fb522ed72", "corecrypto300:s3c28c995eb5e", "corecrypto38:s6599b9d988eb"], "status": "REASONED"},
    "snapshot-integrity": {"text": "Keep repositories private and keys recoverable; do not rewrite active repository files. Configuration backups are separate and security-state snapshots are sensitive.", "components": ["es819"], "sources": ["es819:sb98bd971e2f6", "es819:s93987af8201d"], "status": "REASONED"},
    "kibana-default": {"text": "Kibana defaults HTTP localhost:5601 with server TLS disabled; 8.19.22/9.5.4 Docker templates explicitly use wildcard host, requiring override/publication review.", "components": ["kb", "kb8", "kb9"], "sources": ["kb:s0fe3c0d2e958", "kb8:sd77254a631b1", "kb8:s14662915ed7e", "kb9:sd0f70697a909", "kb9:s39aaa733de4b"], "status": "REASONED"},
    "kibana-tls": {"text": "Free Basic 8.19 server.ssl certificate/key protects incoming UI traffic; elasticsearch.ssl CA/full verification protects the separate backend hop.", "components": ["kb"], "sources": ["kb:s0fe3c0d2e958"], "status": "REASONED"},
    "dash-default": {"text": "Dashboards 3.8.0 sample defaults localhost:5601 with server TLS disabled; inspect installation/container overrides.", "components": ["dash"], "sources": ["dash:sae1b7f23ca6c"], "status": "REASONED"},
    "dash-tls": {"text": "Dashboards server.ssl protects UI, cookie.secure restricts session cookie to HTTPS, and opensearch.ssl CA/full verification protects the backend hop; restart after changes.", "components": ["dash36"], "sources": ["dash36:sea686fca5804"], "status": "REASONED"},
    "ui-network": {"text": "UI binding is independent of 9200/9300; loopback suits only a same-namespace proxy, while private access requires intended interface, matching certificates and network restrictions.", "components": ["kb", "dash36"], "sources": ["kb:sf71765842118", "dash36:sea686fca5804"], "status": "REASONED"},
    "verify-rbac": {"text": "Known app-data/other-data documents distinguish broad access from scoped 200/403 for user and key; 401/404/errors are inconclusive and pre-3.7 OpenSearch uses the user only.", "components": ["es", "os"], "sources": ["es:see6eaa520863", "os:sbd093eef861b"], "status": "REASONED", "verify": [1]},
    "verify-anonymous": {"text": "Require effective anonymous settings on every node plus a formerly anonymous-readable known document becoming 401 while admin still gets 200; endpoint-specific 401 alone is insufficient.", "components": ["es", "os"], "sources": ["es:s204396515260", "os:s7d28cfa527a1"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "Admin HTTPS must return 200/cluster JSON before interpreting plaintext; TLS listener must return no HTTP status, with DNS/timeouts/unreachable states inconclusive.", "components": ["es", "os"], "sources": ["es:sce3095052f8d", "os:s4e3281cb3d23"], "status": "REASONED", "verify": [1]},
    "verify-cors": {"text": "Inspect preflight headers: no grant to untrusted origin, exact grant for trusted enabled origin; with CORS disabled neither is granted.", "components": ["es", "os"], "sources": ["es:s0f65658e7273", "os:s3f64f7b4cf84"], "status": "REASONED", "verify": [1]},
    "verify-audit": {"text": "Fresh failed-authentication probe must correlate with new authentication_failed/FAILED_LOGIN in node and independent collector records; 401 alone proves no delivery.", "components": ["es", "os"], "sources": ["es:sfc6fef9020b3", "os:sbad13e007c8f"], "status": "REASONED", "verify": [1]},
    "verify-audit-body": {"text": "Compare unique marker present with body logging enabled and absent from a new matching event when disabled; independently verify header exclusion and effective configuration.", "components": ["es", "os"], "sources": ["es:s5603a653318d", "os:sbad13e007c8f"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Locate actual running listeners/ports and inspect publication; intentional bridge-container wildcard differs from host-network exposure and no output alone is inconclusive.", "components": ["es8", "es9", "host"], "sources": ["es8:s59c2dd10f083", "es9:s1f0a06e68675", "host:s1b4e67e38127"], "status": "REASONED", "verify": [2]},
    "verify-fls-dls": {"text": "Two-tenant fixture compares unrestricted and actual restricted credentials through search, GET, requested fields and aggregations, with allowed-field and administrator controls; no inference-proof claim.", "components": ["es819", "os36"], "sources": ["es819:s805957cad810", "es819:s52adbc714b10", "os36:s42d975e3cd92", "os36:sade7ff6b2bb3"], "status": "REASONED", "verify": [3]},
    "verify-storage": {"text": "Data-path device chain must traverse intended encryption mapping; unrelated mapping or successful unlocked reads proves nothing, and provider volumes need their own metadata.", "components": ["host"], "sources": ["host:s42b4720299f5", "host:sd23c3d0f42a7", "host:s252144371961"], "status": "REASONED", "verify": [4]},
    "verify-mount": {"text": "Isolated unavailable-mount fixture must fail startup for that reason without writes to the ordinary directory; restored encrypted mount must start successfully.", "components": ["host"], "sources": ["host:s64522c42b5bc", "host:s9823c4e9efa4"], "status": "REASONED", "verify": [5]},
    "verify-snapshot": {"text": "Harmless explicit-index snapshot/restore must complete and preserve both fixtures without global/security state; timeouts need operation-state inspection before retry.", "components": ["es819", "os36"], "sources": ["es819:sb98bd971e2f6", "es819:s3e5630e4430d", "os36:sf0940d73ed6e"], "status": "REASONED", "verify": [3]},
    "verify-object-key": {"text": "Inspect actual new/retained repository object mode/key; controlled object-read and KMS-only denial need provider evidence plus authorized controls. Repository verify proves neither encryption nor isolation.", "components": ["cloud"], "sources": ["cloud:se54783905d19", "cloud:sc53339f5429f", "cloud:se1e1c91f80b4"], "status": "REASONED", "verify": [6]},
    "verify-ui": {"text": "Require expected CA-validated HTTPS and rejected plaintext UI after an exposed HTTP fixture; verify prohibited-network denial with authorized success and effective private binding.", "components": ["kb", "dash36", "host"], "sources": ["kb:s0fe3c0d2e958", "dash36:sea686fca5804", "host:s1b4e67e38127"], "status": "REASONED", "verify": [7, 8]},
    "verify-ui-backend": {"text": "Browser TLS does not prove backend full verification or Dashboards Secure cookie; inspect both separately with effective settings and publication.", "components": ["kb", "dash36"], "sources": ["kb:s0fe3c0d2e958", "dash36:sea686fca5804"], "status": "REASONED", "verify": [7, 8]}
  }
}
````
<!-- version-basis:end -->
