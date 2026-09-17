# Elasticsearch and OpenSearch: keep security switched on

Open Elasticsearch instances produced some of the largest data leaks on record. Modern versions ship secure; the failure mode today is deliberately switching protection off to make an error message go away.

## Elasticsearch (8.0 and later)

- A fresh install auto-configures security on first start when it runs: authentication is enabled, TLS is set up for HTTP and transport, and a password is generated for the `elastic` superuser. Keep all of it. Auto-configuration is SKIPPED if startup output is redirected, if the config directory is not writable, or if certain security or discovery settings already exist (single-node discovery and a `cluster.initial_master_nodes` naming only the current node are exempted); Debian and RPM packages do not print the password (reset it with `elasticsearch-reset-password -u elastic`). Confirm security actually came up rather than assuming it did.
- Never set `xpack.security.enabled: false`, and never expose a node where TLS (`xpack.security.http.ssl.enabled`) has been turned off. If a client cannot connect, fix the client's CA trust ([self-signed.md](self-signed.md)) or issue a real certificate ([free-certificates.md](free-certificates.md)); do not remove the lock.
- `network.host` defaults to `_local_`, but leaving it alone does not make the node private: security auto-configuration writes `http.host: 0.0.0.0` into `elasticsearch.yml`, which overrides that default for HTTP. Read the effective setting rather than assuming the default, and let remote access go through the same decision as any database: private network, VPN or tunnel, TLS everywhere.
- Create least-privilege users and API keys per application instead of shipping `elastic` credentials ([authentication.md](authentication.md)).

## OpenSearch

- The security plugin provides authentication and TLS; never run with it disabled, including in Docker examples.
- Recent versions require an initial admin password at install (the `OPENSEARCH_INITIAL_ADMIN_PASSWORD` environment variable for the demo configuration; verify the exact mechanism for your version). Make it long and random.
- The demo configuration also seeds `internal_users.yml` with seven built-in accounts (`admin`, `anomalyadmin`, `kibanaserver`, `kibanaro`, `logstash`, `readall`, `snapshotrestore`), meant for evaluation only. `OPENSEARCH_INITIAL_ADMIN_PASSWORD` sets the `admin` password and nothing else, so the other six keep the credentials shipped in the demo file. Before any real deployment, replace those users with your own or remove the demo accounts; on a cluster that has already initialized, editing the file is not enough, apply the change with `securityadmin.sh`, since the live configuration is the `.opendistro_security` index, not the file on disk. Then confirm each demo login is refused.
- The demo configuration installs demo TLS certificates for evaluation; replace them with your own before any real deployment.

## Verify

```bash
curl -q -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\nhttp=%{http_code}\n' \
  --cacert /path/http_ca.crt https://search.example.com:9200/          # expect http=401 without credentials: auth is enforced
curl -q -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\nhttp=%{http_code}\n' --cacert /path/http_ca.crt https://search.example.com:9200/ -u elastic
                                                    # prompts, then returns 200 and cluster JSON with the right password.
                                                    # For OpenSearch use ITS admin user and demo CA (admin + root-ca.pem),
                                                    # not elastic/http_ca.crt. Verify the certificate against the CA your
                                                    # installer generated (Elasticsearch writes http_ca.crt on first start;
                                                    # the OpenSearch demo installs its own) and never pass -k here: -k
                                                    # accepts a substituted certificate as readily as yours, and this line
                                                    # sends credentials over whatever it accepted
curl -q -sS --noproxy '*' --connect-timeout 5 --max-time 10 \
  -w '\nhttp=%{http_code} time_connect=%{time_connect}\n' http://search.example.com:9200/
                                                    # plaintext must get NO HTTP response. With HTTP TLS on, ES closes the
                                                    # connection on a plaintext request (it logs 'received plaintext http
                                                    # traffic on an https channel'), so curl gets http=000 (reset/empty
                                                    # reply) - the PASS (the https probe above already proved the port is
                                                    # up). ANY http_code here is a finding: 200 + cluster JSON (no auth),
                                                    # 401 on an auth-enabled node still serving plaintext (auth on but TLS
                                                    # off is still an exposure), or any other status - the node answered
                                                    # over plaintext, so TLS is off. The body is shown to see what answered
ss -tlnp 'sport = :9200'                            # ss's own filter, not a grep (which would also match a pid of
                                                    # 9200). http.port defaults to the RANGE 9200-9300 and binds the
                                                    # first free port, so set your node's ACTUAL HTTP port here, and also
                                                    # check the transport listener (default 9300-9400); loopback or
                                                    # private only, unless deliberate
```

An unauthenticated `GET /` returning cluster JSON is the classic finding; so is `_cat/indices` listing your data to the world.

## Sources (checked September 2026)

- Elasticsearch security configuration (current docs home for cluster security): https://www.elastic.co/docs/deploy-manage/security
- OpenSearch demo security configuration: https://docs.opensearch.org/latest/security/configuration/demo-configuration/
- OpenSearch security, `internal_users.yml` demo accounts (the seven shipped users admin/anomalyadmin/kibanaserver/kibanaro/logstash/readall/snapshotrestore; checked 2026-09-14): https://github.com/opensearch-project/security/blob/main/config/internal_users.yml
- OpenSearch security, applying configuration changes (`securityadmin.sh`, the `.opendistro_security` index holds the live config; checked 2026-09-14): https://docs.opensearch.org/latest/security/configuration/security-admin/
- Elasticsearch, automatic TLS setup for self-managed clusters (the generated `http_ca.crt` used to verify TLS from a client): https://www.elastic.co/docs/deploy-manage/security/self-auto-setup
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
- Elasticsearch networking settings (`network.host` "Defaults to `_local_`"; security auto-configuration "will add `http.host: 0.0.0.0`"; `http.port` "Defaults to `9200-9300`"): https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings
- Elasticsearch security settings (`xpack.security.enabled`, `xpack.security.http.ssl.enabled`): https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/security-settings
