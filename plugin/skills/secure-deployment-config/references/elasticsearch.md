# Elasticsearch and OpenSearch: keep security switched on

Open Elasticsearch instances produced some of the largest data leaks on record. Modern versions ship secure; the failure mode today is deliberately switching protection off to make an error message go away.

## Elasticsearch (8.0 and later)

- A fresh install auto-configures security on first start: authentication is enabled, TLS is set up for HTTP and transport, and a password is generated for the `elastic` superuser. Keep all of it.
- Never set `xpack.security.enabled: false`, and never expose a node where TLS (`xpack.security.http.ssl`) has been turned off. If a client cannot connect, fix the client's CA trust ([self-signed.md](self-signed.md)) or issue a real certificate ([free-certificates.md](free-certificates.md)); do not remove the lock.
- `network.host` defaults to `_local_`, but leaving it alone does not make the node private: security auto-configuration writes `http.host: 0.0.0.0` into `elasticsearch.yml`, which overrides that default for HTTP. Read the effective setting rather than assuming the default, and let remote access go through the same decision as any database: private network, VPN or tunnel, TLS everywhere.
- Create least-privilege users and API keys per application instead of shipping `elastic` credentials ([authentication.md](authentication.md)).

## OpenSearch

- The security plugin provides authentication and TLS; never run with it disabled, including in Docker examples.
- Recent versions require an initial admin password at install (the `OPENSEARCH_INITIAL_ADMIN_PASSWORD` environment variable for the demo configuration; verify the exact mechanism for your version). Make it long and random.
- The demo configuration also seeds `internal_users.yml` with seven built-in accounts (`admin`, `anomalyadmin`, `kibanaserver`, `kibanaro`, `logstash`, `readall`, `snapshotrestore`), meant for evaluation only. `OPENSEARCH_INITIAL_ADMIN_PASSWORD` sets the `admin` password and nothing else, so the other six keep the credentials shipped in the demo file. Before any real deployment, replace those users with your own or remove the demo accounts; on a cluster that has already initialized, editing the file is not enough, apply the change with `securityadmin.sh`, since the live configuration is the `.opendistro_security` index, not the file on disk. Then confirm each demo login is refused.
- The demo configuration installs demo TLS certificates for evaluation; replace them with your own before any real deployment.

## Verify

```bash
curl -q -s --cacert /path/http_ca.crt https://search.example.com:9200/   # 401 without credentials
curl -q -s --cacert /path/http_ca.crt https://search.example.com:9200/ -u elastic
                                                    # prompts, then 200 with the right password. Verify the certificate
                                                    # against the CA your installer generated (Elasticsearch writes
                                                    # http_ca.crt on first start; the OpenSearch demo configuration
                                                    # installs its own) and never pass -k here: -k accepts a substituted
                                                    # certificate exactly as readily as yours, and this line sends
                                                    # credentials over whatever it accepted
curl -q -s -o /dev/null --connect-timeout 5 --max-time 10 \
  -w 'http=%{http_code} time_connect=%{time_connect}\n' http://search.example.com:9200/
                                                    # plaintext must NOT answer: expect a connection failure or a
                                                    # protocol error, never cluster JSON
ss -tlnp 'sport = :9200'                            # ss's own filter, not a grep, which also matches
                                                    # a pid of 9200: loopback or private only, unless deliberate
```

An unauthenticated `GET /` returning cluster JSON is the classic finding; so is `_cat/indices` listing your data to the world.

## Sources (checked September 2026)

- Elasticsearch security configuration (current docs home for cluster security): https://www.elastic.co/docs/deploy-manage/security
- OpenSearch demo security configuration: https://docs.opensearch.org/latest/security/configuration/demo-configuration/
- OpenSearch security, `internal_users.yml` demo accounts (the seven shipped users admin/anomalyadmin/kibanaserver/kibanaro/logstash/readall/snapshotrestore; checked 2026-09-14): https://github.com/opensearch-project/security/blob/main/config/internal_users.yml
- OpenSearch security, applying configuration changes (`securityadmin.sh`, the `.opendistro_security` index holds the live config; checked 2026-09-14): https://docs.opensearch.org/latest/security/configuration/security-admin/
- Elasticsearch, automatic TLS setup for self-managed clusters (the generated `http_ca.crt` used to verify TLS from a client): https://www.elastic.co/docs/deploy-manage/security/self-auto-setup
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
- Elasticsearch networking settings (`network.host` "Defaults to `_local_`"; security auto-configuration "will add `http.host: 0.0.0.0`"): https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/networking-settings
