# Apache Kafka: SASL_SSL listeners, SCRAM credentials, and ACLs

Kafka's broker defaults are `listeners=PLAINTEXT://:9092`, `security.inter.broker.protocol=PLAINTEXT`, and no authorizer, so anyone who reaches port 9092 can read every topic, produce to it, and create or delete topics with no credential and no encryption. Property names below come from the Kafka 4.x documentation (KRaft mode).

The examples below target Kafka 4.3. Kafka 4.0 and later support KRaft only; the ZooKeeper authorizer note applies to legacy 3.9 deployments. Replace example addresses, certificate subjects, and secrets before deployment.

## 1. Replace the plaintext listener

A client-facing socket should not also be the cluster's replication socket. Give clients, brokers, and controllers distinct listeners. Bind internal listeners to private addresses, restrict their network reachability, and authenticate them even on the private network. Remove the plaintext listener entirely: an unadvertised or loopback-bound socket still accepts direct connections.

This example uses SCRAM over TLS for applications and mutual TLS for internal traffic. Keep step 2's keystore/truststore settings on every node. Each node needs its own certificate, with SANs matching the hostnames used to reach it. Internal truststores must trust the intended internal certificate issuers.

These are security overlays for separate KRaft roles. Retain each node's unique `node.id` and storage configuration. Apply the common settings to brokers and controllers:

```properties
listener.security.protocol.map=CLIENT:SASL_SSL,INTERNAL:SSL,CONTROLLER:SSL
inter.broker.listener.name=INTERNAL
controller.listener.names=CONTROLLER
controller.quorum.bootstrap.servers=controller-1.internal:9094,controller-2.internal:9094,controller-3.internal:9094
listener.name.internal.ssl.client.auth=required
listener.name.controller.ssl.client.auth=required
ssl.endpoint.identification.algorithm=https
```

Broker-specific settings, substituting the broker's real private address and advertised hostnames:

```properties
process.roles=broker
listeners=CLIENT://0.0.0.0:9093,INTERNAL://10.0.0.11:9095
advertised.listeners=CLIENT://kafka.example.com:9093,INTERNAL://broker-1.internal:9095
sasl.enabled.mechanisms=SCRAM-SHA-512
listener.name.client.sasl.enabled.mechanisms=SCRAM-SHA-512
listener.name.client.scram-sha-512.sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required;
```

Restrict access to `CLIENT` to the intended application networks too. Its wildcard bind is not a firewall policy.

Controller-specific settings, substituting that controller's real private address:

```properties
process.roles=controller
listeners=CONTROLLER://10.0.0.21:9094
```

For this layout, advertise only `CLIENT` and `INTERNAL` on brokers; omit `advertised.listeners` from the controller overlay. Broker-only nodes still need the controller listener's protocol mapping and security settings for outbound connections, although they do not bind that listener. The first entry in `controller.listener.names` selects outbound controller traffic.

Replace the previous listener definitions and obsolete listener-prefixed properties. Remove the previous controller PLAIN JAAS configuration, `sasl.mechanism.controller.protocol`, and `sasl.mechanism.inter.broker.protocol`: the internal connections now use certificate authentication. Select the inter-broker listener by name with `inter.broker.listener.name=INTERNAL`; do not also set `security.inter.broker.protocol`. Setting both is a startup error. The shipped configuration already selects an inter-broker listener, so replace that selection.

The prefix in `listener.name.<name>.*` uses the listener name lowercased. Rename every affected prefix when renaming a listener; properties under an unused listener name do not configure the intended listener.

Kafka advises against combined broker/controller roles for critical deployments. If retaining a combined node, its `listeners` must include the controller listener as well as the broker listeners. Keep distinct ports for this layout. The distribution's example controller uses 9093, which this guide assigns to clients; move both the controller binding and quorum bootstrap endpoints to 9094. Otherwise overlapping listener bindings can prevent startup.

The quorum example is for a dynamic KRaft quorum. Do not combine it with a static `controller.quorum.voters` configuration. An existing static quorum needs the documented migration procedure, not just replacement of its voter list with bootstrap addresses. See [KRaft process roles and quorum provisioning](https://kafka.apache.org/43/operations/kraft/) and [listener configuration](https://kafka.apache.org/43/security/listener-configuration/).

Retain the controller SCRAM caution narrowly: at the time of writing, [KAFKA-15513](https://issues.apache.org/jira/browse/KAFKA-15513) remains unresolved, lists affected versions 3.5.1 and 3.6.0, and lists no fixed version. It describes controller-to-controller SCRAM bootstrap failures; it does not establish a reproduced failure on every Kafka 4.3 deployment. Internal mutual TLS avoids relying on controller SCRAM bootstrap here.

Apply step 4's deny-by-default authorizer and authorize the actual internal certificate principals before starting a new quorum. Controllers must be authenticated and private.

## 2. TLS on the broker

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md); an internal CA fits a cluster) and point the broker at it. Kafka 2.7.0 and later also take PEM: `ssl.keystore.type=PEM` with `ssl.keystore.certificate.chain` and `ssl.keystore.key` (PKCS#8), and `ssl.truststore.type=PEM` with `ssl.truststore.certificates`. Hostname verification (`ssl.endpoint.identification.algorithm`) is on by default since 2.0.0; the documentation discourages blanking it.

Keep these settings in the service-owned server properties file, with mode 0600 established before populating it. Protect keystores, private keys, JAAS files, client properties, and secret provisioning files the same way; restrict their parent directories. Passwords belong in those files, never in command-line arguments.

```properties
ssl.keystore.location=/var/private/ssl/server.keystore.jks
ssl.keystore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.key.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.truststore.location=/var/private/ssl/server.truststore.jks
ssl.truststore.password=REPLACE_WITH_LONG_RANDOM_VALUE
# Client certificates on CLIENT: none (default), requested (optional), or required (mutual TLS).
# On a SASL_SSL listener this property needs the listener prefix.
listener.name.client.ssl.client.auth=none
```

Install the keystore/truststore settings on controllers too, using each node's own files. The last line belongs on brokers exposing `CLIENT`; it does not override the required client certificates on `INTERNAL` and `CONTROLLER`.

The unprefixed `ssl.client.auth` applies to `SSL` listeners; a `SASL_SSL` listener needs the listener-prefixed setting. `requested` permits clients without certificates and is not equivalent to `required`.

For PEM, store passwords are not supported; an encrypted PKCS#8 key uses `ssl.key.password`. Keep the inline PEM material in a protected properties file if using that form.

Do not copy the old TLSv1/TLSv1.1 examples still present on the SSL page. The generated Kafka 4.3 reference gives `TLSv1.2,TLSv1.3` as the `ssl.enabled.protocols` default. See [SSL configuration](https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/) and the [broker configuration reference](https://kafka.apache.org/43/configuration/broker-configs/).

## 3. SASL/SCRAM credentials

The documentation says SCRAM should be used only with TLS, hence `SASL_SSL` rather than `SASL_PLAINTEXT`. Give each application role its own credential ([authentication.md](authentication.md)). Keep SCRAM-SHA-512 and the listener JAAS configuration from step 1.

KRaft SCRAM identities reside in the metadata log. Protect controller storage, snapshots/backups, and controller access. Legacy ZooKeeper credential-store descriptions do not describe this deployment.

If inter-broker communication uses SCRAM, its credentials must exist before brokers start. This guide instead uses internal mutual TLS, so no inter-broker SCRAM password is needed during storage formatting.

For a new dynamic quorum, generate the cluster ID once and reuse that exact value on every node. The following bootstraps only the first controller:

```bash
# Run ONCE; retain the same cluster ID for every node.
CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)" || exit 1
printf 'Cluster ID: %s\n' "$CLUSTER_ID"
# First controller only, when bootstrapping a new dynamic quorum with one voter:
bin/kafka-storage.sh format --cluster-id "$CLUSTER_ID" \
  --config config/controller.properties --standalone
```

Do not run `--standalone` independently on every controller. Follow the documented membership workflow to add the remaining controllers before relying on quorum redundancy. New brokers and controllers joining an existing dynamic quorum are formatted with the same cluster ID and `--no-initial-controllers`. Alternatively, bootstrap multiple controllers with `--initial-controllers`, using the same complete `id@hostname:port:directory-id` list on every initial controller and a distinct directory ID for each controller. Generate directory IDs separately from the shared cluster ID. Formatting is for new storage, not an authentication migration on an existing cluster. See [KRaft provisioning](https://kafka.apache.org/43/operations/kraft/).

Before starting the nodes, configure the certificate super users in step 4. Then use an administrative mTLS client on the private broker `INTERNAL` listener to provision the first SCRAM administrator. Its restricted `bootstrap-admin.properties` contains:

```properties
security.protocol=SSL
ssl.truststore.location=/var/private/ssl/client.truststore.jks
ssl.truststore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.keystore.location=/var/private/ssl/bootstrap-admin.keystore.jks
ssl.keystore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.key.password=REPLACE_WITH_LONG_RANDOM_VALUE
```

The client certificate must have the exact bootstrap administrator principal authorized in step 4.

Create separate service-owned, mode-0600 files for `admin`, `orders-writer`, and `orders-reader`, establishing permissions before writing secrets. For example, `/etc/kafka/secrets/orders-writer.scram.properties` contains:

```properties
SCRAM-SHA-512=iterations=8192,password=REPLACE_WITH_LONG_RANDOM_VALUE
```

Use a different long random password in each file. This is Java properties syntax: there are no square brackets around the value. The inline `--add-config` parser removes brackets; the `--add-config-file` path does not. Preserve any necessary Java properties escaping when inserting a real secret.

Bootstrap the administrator through the private listener:

```bash
bin/kafka-configs.sh --bootstrap-server broker-1.internal:9095 \
  --command-config bootstrap-admin.properties \
  --alter --entity-type users --entity-name admin \
  --add-config-file /etc/kafka/secrets/admin.scram.properties
```

Create `admin.properties` using step 7's SASL client configuration with username `admin` and its own password. Once that credential works, provision the application roles:

```bash
bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --alter --entity-type users --entity-name orders-writer \
  --add-config-file /etc/kafka/secrets/orders-writer.scram.properties

bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --alter --entity-type users --entity-name orders-reader \
  --add-config-file /etc/kafka/secrets/orders-reader.scram.properties
```

On an already running cluster, an existing authorized administrator can use these file-based commands directly. Keep provisioning files and diagnostic output private: malformed SCRAM input can be included in CLI error messages. Do not substitute a file's contents into `--add-scram` or `--add-config`; that still puts the password in argv. The storage tool is not used here as a password-file interface.

The empty server-side SCRAM login module options in step 1 are intentional: these brokers accept application SCRAM connections but authenticate their own internal connections with certificates. See [SASL/SCRAM configuration and credential storage](https://kafka.apache.org/43/security/authentication-using-sasl/) and [ConfigCommand's file loading and SCRAM parser](https://github.com/apache/kafka/blob/4.3.0/core/src/main/scala/kafka/admin/ConfigCommand.scala).

## 4. Authorization

Without an authorizer every authenticated user can do everything. Enable the KRaft authorizer on every broker and controller and keep deny-by-default. A fresh quorum also needs its internal node identities authorized before ACL metadata is available.

Enumerate the exact certificate principals for every broker, every controller, and the bootstrap administrator. The following is an example only where the certificates' complete subjects are exactly the shown CNs:

```properties
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
allow.everyone.if.no.acl.found=false
super.users=User:admin;User:CN=broker-1;User:CN=controller-1;User:CN=controller-2;User:CN=controller-3;User:CN=bootstrap-admin
```

Expand the list for the actual cluster. A certificate subject containing other components needs its complete principal, not just its CN. The separator between super users is a semicolon, because certificate subjects can contain commas. Never add application principals. Protect node and bootstrap administrator private keys as administrative credentials. See [KIP-801 bootstrapping](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/195728007/KIP-801+Implement+an+Authorizer+that+stores+metadata+in+__cluster_metadata).

For a legacy ZooKeeper deployment on Kafka 3.9, the authorizer class is `kafka.security.authorizer.AclAuthorizer`, not `kafka.security.auth.SimpleAclAuthorizer`. Do not substitute that class into Kafka 4.3. See the [3.9 authorization reference](https://kafka.apache.org/39/security/authorization-and-acls/).

A producer credential should not also read orders, and a consumer credential should not write them. Provision separate `orders-writer` and `orders-reader` identities. Create topics through an administrative workflow and grant applications only the operations they need.

Disable automatic topic creation in the broker configuration:

```properties
auto.create.topics.enable=false
```

Create `orders` administratively before starting the applications, using the partition count and replication factor appropriate to the deployment. Grant the application roles:

```bash
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --add --allow-principal User:orders-writer \
  --operation Write --operation Describe \
  --topic orders --resource-pattern-type literal

bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --add --allow-principal User:orders-reader \
  --operation Read --operation Describe \
  --topic orders --resource-pattern-type literal

bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --add --allow-principal User:orders-reader \
  --operation Read --group app-workers --resource-pattern-type literal
```

Replace the old grants rather than accumulating permissions. After migrating the application, remove the previous shared `User:app` grants:

```bash
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --remove --allow-principal User:app --producer \
  --topic orders --resource-pattern-type literal

bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --remove --allow-principal User:app --consumer \
  --topic orders --group app-workers --resource-pattern-type literal
```

Inspect matching wildcard and prefix ACLs, including grants to `User:*`, and cluster-level grants. Removing these literal grants does not remove permissions conferred elsewhere. Retire the old shared credential after its remaining uses have been removed.

The `--producer` convenience option grants topic `Create` as well as `Write` and `Describe`; use the explicit grants above for the new writer. Disabling automatic creation alone does not remove explicit creation rights.

If the producer uses transactions, additionally authorize its specific transaction identity:

```bash
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --add --allow-principal User:orders-writer \
  --operation Write --transactional-id orders-writer-1 \
  --resource-pattern-type literal
```

Use that identity as the producer's `transactional.id`. Do not automatically add cluster-wide `IdempotentWrite`: Kafka 4.3.0's non-transactional producer initialization also accepts a principal with topic `Write` permission. The manual's authorization table is less precise on this point; the tagged [InitProducerId implementation](https://github.com/apache/kafka/blob/4.3.0/core/src/main/scala/kafka/server/KafkaApis.scala) supplies the distinction.

See [Authorization and ACLs](https://kafka.apache.org/43/security/authorization-and-acls/) and [multi-tenancy topic-creation controls](https://kafka.apache.org/43/operations/multi-tenancy/).

## 5. Bound authenticated traffic and connection pressure

Authentication does not stop a compromised application from exhausting broker resources. Set quotas by authenticated user, and limit connections on the client listener. Tune these example values against normal traffic before rollout.

```bash
bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --alter --entity-type users --entity-name orders-writer \
  --add-config 'producer_byte_rate=1048576,request_percentage=25'

bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --alter --entity-type users --entity-name orders-reader \
  --add-config 'consumer_byte_rate=2097152,request_percentage=25'
```

These byte rates apply per broker. `request_percentage=25` permits processing time equivalent to 25 percent of one thread, accumulated across the broker's network and request-handler I/O threads. It is not 25 percent of the whole machine.

A client chooses its own `client.id`; use authenticated-user quotas as the primary boundary. Inspect more-specific user/client quotas and user/default-client overrides, which take precedence over a user-only quota. See [setting quotas](https://kafka.apache.org/43/operations/basic-kafka-operations/) and [quota grouping, precedence, and enforcement](https://kafka.apache.org/43/design/design/).

In broker `server.properties`:

```properties
listener.name.client.max.connections=500
listener.name.client.max.connection.creation.rate=50
```

The first limit bounds simultaneous client connections; the second bounds new connections per second. They act on connection pressure before a client has necessarily authenticated. Keep replication on its separate listener. Kafka 4.3 supports these listener-specific limits; inter-broker connections have documented exceptions to broker-wide limits. These controls supplement network filtering and do not prevent upstream network saturation. See the [connection-limit configuration reference](https://kafka.apache.org/43/configuration/broker-configs/).

For a tenant that is separately authorized to create, delete, or alter topics, an additional conditional quota is:

```bash
bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 \
  --command-config admin.properties \
  --alter --entity-type users --entity-name topic-provisioner \
  --add-config 'controller_mutation_rate=10'
```

This bounds partition mutations, not ordinary message throughput, and does not grant topic-management permissions. See [multi-tenancy quotas and rate limiting](https://kafka.apache.org/43/operations/multi-tenancy/).

## 6. Retain authorization decisions

Authentication failures and authorization denials need an operational record. Kafka provides authorizer logging; it is not a complete audit trail of every administrative change or message. Authentication failures occur before authorization and need separate collection from the normal broker/controller logs.

In the distribution's `config/log4j2.yaml`, replace the existing `kafka.authorizer.logger` entry under `Configuration.Loggers.Logger` with the following, matching the surrounding indentation. Retain the existing `AuthorizerAppender`:

```yaml
- name: kafka.authorizer.logger
  level: DEBUG
  additivity: false
  AppenderRef:
    ref: AuthorizerAppender
```

Collect `kafka-authorizer.log` from brokers and controllers, alongside their normal server logs. Protect the collector and retention policy independently of broker access. Estimate logging volume before enabling allowed-access records.

Kafka 4.0 migrated to Log4j2; do not paste legacy `log4j.logger...` syntax into its YAML configuration. The tagged 4.3.0 distribution defines this logger, appender, and filename.

`StandardAuthorizer` logs explicitly requested denials at INFO and allowed access at DEBUG when the corresponding audit flag is set. Some filtering and introspection decisions use TRACE instead. DEBUG therefore does not mean every authorization evaluation.

The manual does not document this logger's full configuration. This recipe is additionally checked against the [tagged logging configuration](https://github.com/apache/kafka/blob/4.3.0/config/log4j2.yaml), [StandardAuthorizer's audit implementation](https://github.com/apache/kafka/blob/4.3.0/metadata/src/main/java/org/apache/kafka/metadata/authorizer/StandardAuthorizerData.java#L257), and the [Action audit-logging API](https://kafka.apache.org/43/javadoc/org/apache/kafka/server/authorizer/Action.html). The migration is documented in [upgrading to Kafka 4.0](https://kafka.apache.org/43/getting-started/upgrade/).

## 7. Client side

Keep `client.properties` out of the repository ([secrets.md](secrets.md)), owned by the account that needs it, with mode 0600 established before writing secrets. Use separate copies as `orders-writer.properties` and `orders-reader.properties`, with the corresponding username and distinct password. Keep `admin.properties` separate from application deployments.

MFA: the Kafka protocol has no second-factor dialogue. `listener.name.client.ssl.client.auth=required` adds mutual TLS as a possession control for machine clients ([machine-auth.md](machine-auth.md)); the unprefixed `ssl.client.auth` applies only to `SSL` listeners, and Kafka warns when it is set without the prefix on a `SASL_SSL` broker. Each client then presents its own keystore as in the last three lines below. Human paths to brokers or a management UI go behind MFA per [mfa.md](mfa.md).

Example `orders-writer.properties`:

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="orders-writer" password="REPLACE_WITH_LONG_RANDOM_VALUE";
ssl.truststore.location=/var/private/ssl/client.truststore.jks
ssl.truststore.password=REPLACE_WITH_LONG_RANDOM_VALUE
# only when the listener requires client certificates
ssl.keystore.location=/var/private/ssl/client.keystore.jks
ssl.keystore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.key.password=REPLACE_WITH_LONG_RANDOM_VALUE
```

For the reader, change the username to `orders-reader` and use its password. For the administrator, use `admin` and its password. Omit the optional keystore lines when client certificates are not required. Leave hostname verification enabled.

The commands below use Kafka 4.3's `--command-config` option, including on the console producer and consumer. Older distributions may use different client-file flags; use the CLI shipped with the documented version.

## 8. Redpanda (and other Kafka-API-compatible systems)

Redpanda implements the Kafka wire protocol, so the client-side and protocol-level controls above carry over: SASL/SCRAM authentication, TLS, and ACL management through the Kafka API all work the same way against a Redpanda cluster, and the same fronting rules apply too. What does not carry over is how you wire that up on the broker: Redpanda configures brokers through `redpanda.yaml` and the `rpk` CLI, not Kafka's `server.properties`, JAAS configuration files, or `kafka-storage.sh`. Redpanda Console, its bundled web UI, ships without its own login screen: it only gains one once you configure OIDC or basic authentication, and that built-in Console login requires an enterprise licence, so until you configure it anyone who reaches Console reaches the cluster behind it (enabling the enterprise features without a valid licence does not open Console: it restricts access to a licence-expiration page instead). Front Console the same way as any other admin panel: never public, reached through SSH forwarding, a tailnet, or an access proxy, with MFA at that layer. See the [Redpanda security documentation](https://docs.redpanda.com/streaming/current/manage/security/).

Check Redpanda's own references for listener separation, quotas, and logging; the Kafka server configuration additions above are not Redpanda configuration.

## Verify

This guide has not been demonstrated against a running Kafka cluster. The service checks below are **REASONED**: the authoring environment has no Kafka distribution/runtime, live broker/controller quorum, node certificates, external test hosts, or deployed log collector. The repository is read-only. These missing capabilities prevent the exposed/fixed service comparisons here.

Locally, the shell blocks passed `bash -n`, ShellCheck, and the repository's guard-convention scanner. YAML parsing, properties lexical checks, and the bracket-free SCRAM value's match against the tagged parser expression were checked. For each of the ten guarded blocks, six unsafe inputs were exercised: the original placeholder, an embedded placeholder, each angle bracket, an `example.com` hostname, and an empty value. All rejected without executing a probe. Isolated positive controls confirmed that a substituted value reaches each guard's intended arm. These are bounded local results, not a claim of aggregate bypass resistance or Kafka enforcement.

Substitute inside the single quotes and paste each whole block. A literal apostrophe requires proper shell escaping. Run external checks from another host over the actual public IPv4 and IPv6 paths; run the listener inventory in each Kafka node's network namespace.

Use an isolated test deployment with an administratively created `orders` fixture for commands that produce records or create topics. Provision the named credentials and ACLs first. The single-replica temporary topics below are disposable test fixtures, not a production replication recommendation. Keep diagnostics private. If a block stops early, remove its temporary ACLs and topics using the printed names.

### Listener inventory and client TLS

**REASONED:** No Kafka node namespace, deployed certificate, or external network vantage is available here. On an exposed deployment, the inventory can show a plaintext or publicly bound internal listener. The fixed inventory should show client 9093, private broker-internal 9095, and private controller 9094 only where their roles require them. `ss` is an inventory in this namespace, not proof of firewall enforcement.

The client TLS positive control must validate the broker hostname and certificate chain. A plaintext endpoint cannot complete this TLS exchange. A certificate error is a TLS defect; a DNS or local failure is inconclusive. Sources: [listener configuration](https://kafka.apache.org/43/security/listener-configuration/), [Kafka SSL](https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/), and [OpenSSL s_client](https://docs.openssl.org/3.5/man1/openssl-s_client/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker hostname; not probing" ;;
    *)
      ss -tlnp || { echo "listener inventory failed"; exit 1; }
      openssl s_client -connect "$1:9093" -servername "$1" \
        -verify_hostname "$1" -verify_return_error -CAfile ca.pem </dev/null \
        || { echo "TLS check failed; inspect the diagnostic"; exit 1; }
      ;;
  esac
)
```

Point `ca.pem` at the CA that signed the broker certificate. Omit `-CAfile` only when using an appropriate public CA already trusted by OpenSSL. Without the verification flags, a completed handshake shows only that TLS is present.

This probe matches the default client listener above, which does not require client certificates. If setting `listener.name.client.ssl.client.auth=required`, add the client's `-cert` and `-key`, and use `-pass file:client-key.pass` for an encrypted key. Protect that password file. `Verification: OK` alone does not prove the broker accepted the client certificate; it can appear before the server rejects the connection.

### Internal mutual TLS and network isolation

**REASONED:** No private broker listener, certificate fixtures, or allowed/disallowed network vantage is available here. Prepare `internal-no-cert.properties` from `bootstrap-admin.properties` with all client keystore/key settings removed. Prepare `internal-untrusted-cert.properties` with an otherwise valid client certificate signed by a CA the broker does not trust; retain the correct server truststore.

On the same allowed private path, the valid administrator certificate must permit the positive Kafka control. Missing and untrusted client certificates must fail at TLS. With client-certificate enforcement absent, the TLS handshake may succeed even if the authorizer subsequently rejects an anonymous principal; an authorization failure is not proof of mutual TLS. Inspect the TLS diagnostic and broker logs. Source: [Kafka SSL client authentication](https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_INTERNAL_BROKER_HOST:9095'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      bin/kafka-broker-api-versions.sh --bootstrap-server "$1" \
        --command-config bootstrap-admin.properties \
        || { echo "valid internal mTLS control failed"; exit 1; }
      if bin/kafka-broker-api-versions.sh --bootstrap-server "$1" \
        --command-config internal-no-cert.properties; then
        echo "FINDING: internal Kafka access without a client certificate"
        exit 1
      else
        echo "Inspect for a TLS client-certificate rejection; other failures are inconclusive"
      fi
      if bin/kafka-broker-api-versions.sh --bootstrap-server "$1" \
        --command-config internal-untrusted-cert.properties; then
        echo "FINDING: internal Kafka access with an untrusted client certificate"
        exit 1
      else
        echo "Inspect for a TLS trust rejection; other failures are inconclusive"
      fi
      ;;
  esac
)
```

Repeat the valid-certificate control from a network that must not reach `INTERNAL`. The exposed state is reachable from that network; the fixed state blocks it while the allowed-network control still works. Correlate blocked attempts with network policy evidence: a timeout alone cannot distinguish filtering from a broken route.

**REASONED:** No controller listener, node certificate, or controller logs are available here. Test each controller with a valid node certificate, then without a certificate. Fixed TLS must accept the valid certificate and reject the missing one; an exposed listener without client-certificate enforcement can complete both handshakes. Source: [controller listeners](https://kafka.apache.org/43/security/listener-configuration/) and [OpenSSL verification](https://docs.openssl.org/3.5/man1/openssl-s_client/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CONTROLLER_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one controller hostname; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the controller hostname; not probing" ;;
    *)
      openssl s_client -connect "$1:9094" -servername "$1" \
        -verify_hostname "$1" -verify_return_error -CAfile ca.pem \
        -cert node.crt -key node.key -pass file:node-key.pass </dev/null \
        || { echo "node-certificate TLS control failed"; exit 1; }
      if openssl s_client -connect "$1:9094" -servername "$1" \
        -verify_hostname "$1" -verify_return_error -CAfile ca.pem </dev/null; then
        echo "No-certificate result needs TLS alert and controller-log inspection"
      else
        echo "Inspect for a missing-client-certificate TLS alert"
      fi
      ;;
  esac
)
```

Also repeat with an untrusted node certificate and from disallowed networks. Inspect the full exchange and server logs; `s_client` status and server-certificate verification alone are insufficient evidence of client acceptance. Successful TLS does not demonstrate quorum or replication health. Those comparisons remain in the backlog row below.

### Plaintext refusal and wrong-password rejection

Create `plain.properties` containing only:

```properties
security.protocol=PLAINTEXT
```

Create `wrong.properties` from `orders-reader.properties`, changing only its password to a deliberately incorrect value. Use a seeded `orders` fixture with records available at the `app-workers` group's current offsets for the matched authenticated consumer control.

**REASONED:** No live broker or external client host is available here. The authenticated control must work first. A plaintext Kafka service would answer the plaintext tool; the fixed `SASL_SSL` listener must not serve it. The wrong-password consumer must report `SaslAuthenticationException`; an empty result, timeout, group denial, DNS error, or local failure is not that result. Sources: [SASL/SCRAM](https://kafka.apache.org/43/security/authentication-using-sasl/), [broker API versions CLI](https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/BrokerApiVersionsCommand.java), and [console-consumer options](https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/consumer/ConsoleConsumerOptions.java).

Kafka 4.3.0's [ConsoleConsumer implementation](https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/consumer/ConsoleConsumer.java) catches and logs exceptions from `receive()` inside `process()`, then returns; only exceptions escaping to `main()` cause its explicit exit with status 1. A consumer's exit status therefore does not prove denial. Both consumer denial checks below inspect the specific exception in stderr, regardless of exit status; records returned by a denied probe are a finding.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      umask 077
      set -- "$1" "$(mktemp -d)"
      [ -d "$2" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Results: %s\n' "$2"
      bin/kafka-broker-api-versions.sh --bootstrap-server "$1" \
        --command-config orders-reader.properties \
        || { echo "authenticated positive control failed"; exit 1; }
      if bin/kafka-broker-api-versions.sh --bootstrap-server "$1" \
        --command-config plain.properties >"$2/plain.log" 2>&1; then
        echo "FINDING: plaintext Kafka is served"
        exit 1
      else
        echo "Plaintext failed; inspect plain.log and broker logs to exclude local, DNS and routing errors"
      fi
      bin/kafka-console-consumer.sh --bootstrap-server "$1" \
        --command-config orders-reader.properties --group app-workers \
        --topic orders --from-beginning --max-messages 1 --timeout-ms 10000 \
        >"$2/authenticated.out" 2>"$2/authenticated.log" \
        || { echo "authenticated consumer control failed; inspect authenticated.log"; exit 1; }
      [ -s "$2/authenticated.out" ] \
        || { echo "authenticated consumer returned no records; not probing denial"; exit 1; }
      bin/kafka-console-consumer.sh --bootstrap-server "$1" \
        --command-config wrong.properties --group app-workers \
        --topic orders --from-beginning --max-messages 1 --timeout-ms 10000 \
        >"$2/wrong.out" 2>"$2/wrong.log" \
        || printf 'Consumer exit=%s; checking wrong.log for the specific denial\n' "$?"
      if [ -s "$2/wrong.out" ]; then
        echo "FINDING: wrong-password consumer returned records"
        exit 1
      fi
      grep -F 'SaslAuthenticationException' "$2/wrong.log" >/dev/null \
        || { echo "not the expected authentication denial; inspect wrong.log"; exit 1; }
      echo "wrong password rejected at SASL authentication"
      ;;
  esac
)
```

### Marker round trip and split application permissions

**REASONED:** No live broker, test topic, or application identities are available here. The matched positive control produces a unique marker as the writer and reads that exact marker as the reader using a fresh consumer group. Then the same reader identity attempts a write. An overprivileged reader can write; the fixed reader receives `TopicAuthorizationException`.

Only the negative producer probe disables idempotence, so a producer-ID authorization check does not mask the topic-write check. This is a test override, not an application configuration recommendation. Sources: [ACL operations](https://kafka.apache.org/43/security/authorization-and-acls/), [producer configuration](https://kafka.apache.org/43/configuration/producer-configs/), and the tagged console-tool sources in Sources.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      umask 077
      set -- "$1" "verify-$(date +%s)-$$" "$(mktemp -d)"
      [ -d "$3" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Results: %s\n' "$3"
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --add --allow-principal User:orders-reader --operation Read \
        --group "$2" --resource-pattern-type prefixed \
        || { echo "temporary group ACL failed"; exit 1; }
      printf '%s\n' "$2" | bin/kafka-console-producer.sh \
        --bootstrap-server "$1" --command-config orders-writer.properties \
        --topic orders --sync \
        || { echo "writer positive control failed"; exit 1; }
      if bin/kafka-console-consumer.sh --bootstrap-server "$1" \
        --command-config orders-reader.properties --group "$2" --topic orders \
        --from-beginning --timeout-ms 15000 >"$3/records" 2>"$3/consumer.log"; then
        echo "consumer exited normally"
      else
        echo "Consumer exited nonzero; inspect consumer.log, including any idle timeout"
      fi
      grep -Fx -- "$2" "$3/records" >/dev/null \
        || { echo "marker missing: positive control FAILED or inconclusive"; exit 1; }
      echo "positive control OK: exact marker received"
      if printf '%s\n' "$2-denied" | bin/kafka-console-producer.sh \
        --bootstrap-server "$1" --command-config orders-reader.properties \
        --command-property enable.idempotence=false \
        --topic orders --sync >"$3/reader-write.log" 2>&1; then
        echo "FINDING: reader produced a record"
        exit 1
      else
        grep -F 'TopicAuthorizationException' "$3/reader-write.log" >/dev/null \
          || { echo "not the expected topic denial; inspect reader-write.log"; exit 1; }
        echo "reader write denied at topic authorization"
      fi
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --remove --allow-principal User:orders-reader --operation Read \
        --group "$2" --resource-pattern-type prefixed \
        || { echo "remove the temporary group ACL manually"; exit 1; }
      ;;
  esac
)
```

The consumer timeout is an idle timeout, not a wall-clock limit. Use a quiet test fixture. Receiving the exact marker proves that round trip even if the consumer subsequently exits on idle timeout; it does not turn unrelated errors into success. Preserve and inspect stderr separately.

### Topic deny-by-default with an authenticated low-privilege user

Provision `low` through the same restricted-file SCRAM procedure as step 3. Its `low.properties` uses its own valid credential. It must not be a super user or have other grants.

**REASONED:** No live authorizer, low-privilege identity, or seeded topic is available here. This block creates and seeds a real temporary topic, grants `low` a fresh group prefix and a temporary topic `Read`, and proves that `low` receives the marker. It then removes only the topic permission and checks the same topic with a fresh group.

After ACL propagation, the fixed state must report `TopicAuthorizationException`. In an isolated exposed configuration with no matching topic ACL and `allow.everyone.if.no.acl.found=true`, the marker can be read. A group error tests the wrong boundary. Empty output, offsets, and timeouts remain inconclusive. Source: [behavior without ACLs and matching resource patterns](https://kafka.apache.org/43/security/authorization-and-acls/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      umask 077
      set -- "$1" "verify-deny-$(date +%s)-$$" "$(mktemp -d)"
      [ -d "$3" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Test topic/group: %s; results: %s\n' "$2" "$3"
      bin/kafka-topics.sh --bootstrap-server "$1" --command-config admin.properties \
        --create --topic "$2" --partitions 1 --replication-factor 1 \
        || { echo "isolated test-topic creation failed"; exit 1; }
      printf '%s\n' "$2" | bin/kafka-console-producer.sh \
        --bootstrap-server "$1" --command-config admin.properties --topic "$2" --sync \
        || { echo "seeding the test topic failed"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --add --allow-principal User:low --operation Read \
        --group "$2" --resource-pattern-type prefixed \
        || { echo "low user's group ACL failed"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --add --allow-principal User:low --operation Read \
        --topic "$2" --resource-pattern-type literal \
        || { echo "temporary positive-control topic ACL failed"; exit 1; }
      bin/kafka-console-consumer.sh --bootstrap-server "$1" \
        --command-config low.properties --group "$2-positive" --topic "$2" \
        --from-beginning --max-messages 1 --timeout-ms 10000 \
        >"$3/positive" 2>"$3/positive.log" \
        || { echo "low-user positive control failed"; exit 1; }
      grep -Fx -- "$2" "$3/positive" >/dev/null \
        || { echo "low-user positive marker missing"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --remove --allow-principal User:low --operation Read \
        --topic "$2" --resource-pattern-type literal \
        || { echo "temporary topic ACL removal failed"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --list --topic "$2" --resource-pattern-type match \
        || { echo "matching ACL inspection failed"; exit 1; }
      printf 'Type NO_TOPIC_ACLS only after confirming no matching topic ACL remains: '
      read -r REPLY || { echo "ACL confirmation unavailable"; exit 1; }
      [ "$REPLY" = NO_TOPIC_ACLS ] || { echo "ACL precondition not confirmed"; exit 1; }
      bin/kafka-console-consumer.sh --bootstrap-server "$1" \
        --command-config low.properties --group "$2-negative" --topic "$2" \
        --from-beginning --max-messages 1 --timeout-ms 10000 \
        >"$3/negative" 2>"$3/negative.log" \
        || printf 'Consumer exit=%s; checking negative.log for the specific denial\n' "$?"
      if grep -Fx -- "$2" "$3/negative" >/dev/null; then
        echo "FINDING: low user read the marker without a matching topic ACL"
        exit 1
      fi
      if [ -s "$3/negative" ]; then
        echo "FINDING: low user returned records without a matching topic ACL"
        exit 1
      fi
      grep -F 'TopicAuthorizationException' "$3/negative.log" >/dev/null \
        || { echo "not the expected topic denial; inspect negative.log"; exit 1; }
      echo "topic deny-by-default observed"
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --remove --allow-principal User:low --operation Read \
        --group "$2" --resource-pattern-type prefixed \
        || { echo "remove the temporary group ACL manually"; exit 1; }
      bin/kafka-topics.sh --bootstrap-server "$1" --command-config admin.properties \
        --delete --topic "$2" || { echo "remove the test topic manually"; exit 1; }
      ;;
  esac
)
```

The ACL inspection must show no literal, wildcard, or prefix match for the temporary topic. Do not remove unrelated production ACLs to manufacture that condition. Run the comparison in an isolated fixture. A successful unauthorized read is a finding, but attributing it specifically to `allow.everyone.if.no.acl.found` also requires checking the effective authorizer configuration.

### Application topic creation

**REASONED:** No live cluster with the application roles is available here. First complete the writer/reader marker control above. An overprivileged writer can create a new topic; the fixed writer must receive a topic authorization denial, while the administrator can create that same topic. This tests explicit creation rights independently of automatic creation. Sources: [ACL protocol operations](https://kafka.apache.org/43/security/authorization-and-acls/) and [topic administration](https://kafka.apache.org/43/operations/basic-kafka-operations/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      umask 077
      set -- "$1" "verify-create-$(date +%s)-$$" "$(mktemp -d)"
      [ -d "$3" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Test topic: %s; results: %s\n' "$2" "$3"
      if bin/kafka-topics.sh --bootstrap-server "$1" \
        --command-config orders-writer.properties \
        --create --topic "$2" --partitions 1 --replication-factor 1 \
        >"$3/create.log" 2>&1; then
        echo "FINDING: application created a topic"
        exit 1
      else
        grep -F 'TopicAuthorizationException' "$3/create.log" >/dev/null \
          || { echo "not the expected creation denial; inspect create.log"; exit 1; }
      fi
      bin/kafka-topics.sh --bootstrap-server "$1" --command-config admin.properties \
        --create --topic "$2" --partitions 1 --replication-factor 1 \
        || { echo "admin creation control failed"; exit 1; }
      echo "application creation denied; matching admin creation succeeded"
      bin/kafka-topics.sh --bootstrap-server "$1" --command-config admin.properties \
        --delete --topic "$2" || { echo "remove the test topic manually"; exit 1; }
      ;;
  esac
)
```

Repeat for the reader identity. This new-name probe must be combined with ACL inspection: an old literal `Create` grant on `orders` could permit recreating `orders` while still denying the new test name.

### ACL, quota, and connection-limit inspection

**REASONED:** No live admin endpoint is available here. These commands inspect configuration; they do not demonstrate enforcement. Expected exposed state: overly broad matching grants, application `Create`, missing quotas, or unrestricted client connection settings. Expected fixed state: the intended topic/group grants, no application creation grants, explicit user quotas, and the client limits from step 5.

The successful administrative descriptions establish that the inspection path works; the marker and denial comparisons above test application behavior. Sources: [ACL listing](https://kafka.apache.org/43/security/authorization-and-acls/), [quota description](https://kafka.apache.org/43/operations/basic-kafka-operations/), and [broker configuration](https://kafka.apache.org/43/configuration/broker-configs/).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --list --topic orders --resource-pattern-type match \
        || { echo "ACL inspection failed"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --list --group app-workers --resource-pattern-type match \
        || { echo "group ACL inspection failed"; exit 1; }
      bin/kafka-acls.sh --bootstrap-server "$1" --command-config admin.properties \
        --list --cluster || { echo "cluster ACL inspection failed"; exit 1; }
      bin/kafka-configs.sh --bootstrap-server "$1" --command-config admin.properties \
        --describe --entity-type users --entity-name orders-writer \
        || { echo "writer quota inspection failed"; exit 1; }
      bin/kafka-configs.sh --bootstrap-server "$1" --command-config admin.properties \
        --describe --entity-type users --entity-name orders-reader \
        || { echo "reader quota inspection failed"; exit 1; }
      bin/kafka-configs.sh --bootstrap-server "$1" --command-config admin.properties \
        --describe --entity-type users --entity-type clients \
        || { echo "user/client quota override inspection failed"; exit 1; }
      bin/kafka-configs.sh --bootstrap-server "$1" --command-config admin.properties \
        --describe --entity-type brokers --all \
        || { echo "effective broker configuration inspection failed"; exit 1; }
      ;;
  esac
)
```

Inspect every broker's effective values and their configuration sources. For a transactional writer, also inspect matching ACLs for its transaction identity. If using the conditional topic-provisioner quota, describe that user too.

### Bounded quota comparison

**REASONED:** No isolated Kafka workload environment or quota metrics are available here. On an isolated one-partition `orders` fixture, run this identical bounded producer workload before and after applying the writer quota. Keep authentication and ACLs fixed. The baseline must be capable of exceeding the configured byte rate; otherwise the comparison is inconclusive.

Both runs must deliver the requested records without authorization or delivery errors. With no applicable quota, quota throttle time should remain zero; with the workload exceeding the fixed quota, `produce-throttle-time-avg` or `produce-throttle-time-max` should become nonzero. Inspect request-quota metrics separately to distinguish request-time throttling from bandwidth throttling. A low-rate successful marker round trip is the positive control that the fixed system still serves the application. Sources: [quota enforcement](https://kafka.apache.org/43/design/design/), [monitoring metrics](https://kafka.apache.org/43/operations/monitoring/), and [ProducerPerformance options](https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/ProducerPerformance.java).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_HOST:9093'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one broker endpoint; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the broker endpoint; not probing" ;;
    *)
      bin/kafka-producer-perf-test.sh --bootstrap-server "$1" \
        --command-config orders-writer.properties --topic orders \
        --num-records 100000 --record-size 1024 --throughput -1 --print-metrics \
        || { echo "bounded workload failed; inspect authentication, authorization and delivery errors"; exit 1; }
      ;;
  esac
)
```

This producer workload does not demonstrate consumer quotas, controller mutation quotas, or connection-limit enforcement. Those need their own bounded workloads. In particular, compare accepted client connections and connection-creation throttling around the configured limits while confirming that replication and quorum operation remain healthy; a TCP connect result or a configuration listing alone is insufficient.

### Authorization logging

**REASONED:** No live authorizer or collected logs are available here. Run the marker/write-denial pair above in a quiet test window, then inspect only that window's collected authorizer log. Correlate timestamps, client host, principal, operation, resource, and outcome so old records cannot satisfy the check.

At INFO, the requested denial should be present while the allowed write is absent. At DEBUG, both should be present. If the denied record is also absent, logger routing or collection has failed; absence of an allowed record alone is not proof of the intended INFO behavior. Sources: [StandardAuthorizer audit messages](https://github.com/apache/kafka/blob/4.3.0/metadata/src/main/java/org/apache/kafka/metadata/authorizer/StandardAuthorizerData.java) and [the logging configuration](https://github.com/apache/kafka/blob/4.3.0/config/log4j2.yaml).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_COLLECTED_AUTHORIZER_LOG'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one log path; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the log path; not probing" ;;
    *)
      grep -F 'Principal = User:orders-writer is Allowed operation = WRITE' "$1" \
        | grep -F 'on resource = Topic:LITERAL:orders' \
        || { echo "allowed write record missing"; exit 1; }
      grep -F 'Principal = User:orders-reader is Denied operation = WRITE' "$1" \
        | grep -F 'on resource = Topic:LITERAL:orders' \
        || { echo "denied write record missing"; exit 1; }
      ;;
  esac
)
```

The block checks the DEBUG outcome. Repeat the same requests at INFO to establish the matched comparison. Check controller log collection with known controller-authorized operations as well. The wrong-password probe belongs in the authentication-failure review of normal server logs, not in an expectation that the authorizer records failed authentication.

### Demonstration backlog

No existing Kafka live-demonstration row was found in the reviewed backlog. This single row carries the original probes and the new controls together.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| KAFKA-LIVE-1 | Demonstrate every REASONED check above on a pinned Kafka deployment. Cover namespace inventory and real IPv4/IPv6 exposure; client TLS and plaintext refusal; correct and wrong SCRAM credentials; marker round trip; authenticated low-user topic denial with no matching ACL; writer/reader separation and application-create denial with administrator success; allowed/disallowed networks for each listener; valid, missing, and untrusted internal certificates; healthy replication and controller quorum after bootstrap; producer, consumer, request-time, and conditional partition-mutation quotas with matched bounded workloads and throttle metrics; simultaneous-connection and connection-creation limits while internal traffic remains healthy; and INFO/DEBUG authorization records collected from brokers and controllers, plus authentication-failure records. Record commands, versions, diagnostics, matched positive controls, and cleanup. Configuration inspection alone does not close this row. | Open; service behavior is reasoned, not demonstrated. |

## Common mistakes

- `SASL_SSL` added as a second listener while `PLAINTEXT://:9092` stays advertised, so clients quietly keep using it.
- Authorizer enabled with `allow.everyone.if.no.acl.found=true` "temporarily". The flag opens only resources that have no ACL at all; existing ACLs are still enforced. That still means every new topic is world-readable and world-writable until someone adds its first ACL, so keep it `false`.
- Treating an unadvertised, loopback, or private controller socket as a substitute for authentication.
- Starting a deny-by-default quorum before authorizing its actual node certificate principals.
- Adding narrow writer/reader ACLs without removing the old shared, wildcard, prefix, or cluster-level grants.
- Assuming `auto.create.topics.enable=false` removes an application's explicit `Create` permission.
- Treating a quota listing as an enforcement test, or DEBUG authorizer logging as a complete audit trail.
- Treating an empty consumer result, a timeout, or `Verification: OK` alone as proof of the intended security boundary.

## Sources (checked September 2026)

- Kafka security overview: https://kafka.apache.org/43/security/security-overview/
- Listener configuration (controller listener, combined-node requirement, protocol map): https://kafka.apache.org/43/security/listener-configuration/
- Encryption and authentication using SSL: https://kafka.apache.org/43/security/encryption-and-authentication-using-ssl/
- Authentication using SASL (SCRAM): https://kafka.apache.org/43/security/authentication-using-sasl/
- Authorization and ACLs (`allow.everyone.if.no.acl.found`, resource-pattern-type): https://kafka.apache.org/43/security/authorization-and-acls/
- KRaft provisioning / storage formatting (`--standalone`, cluster ID reuse): https://kafka.apache.org/43/operations/kraft/
- Broker configuration reference (defaults for `listeners`, `sasl.enabled.mechanisms`, `inter.broker.listener.name`): https://kafka.apache.org/43/configuration/broker-configs/
- SSL client authentication on `SASL_SSL` listeners needs the listener prefix (source, `ChannelBuilders.java`, tagged 4.3.0): https://raw.githubusercontent.com/apache/kafka/4.3.0/clients/src/main/java/org/apache/kafka/common/network/ChannelBuilders.java
- Redpanda security documentation: https://docs.redpanda.com/streaming/current/manage/security/
- Redpanda Console authentication (built-in login requires an enterprise licence): https://docs.redpanda.com/streaming/current/console/config/security/authentication/
- Apache Kafka controller SCRAM bootstrap issue (KAFKA-15513): https://issues.apache.org/jira/browse/KAFKA-15513
- Kafka 3.9 authorization and ZooKeeper AclAuthorizer: https://kafka.apache.org/39/security/authorization-and-acls/
- KIP-801 authorizer bootstrapping and early-start listeners: https://cwiki.apache.org/confluence/spaces/KAFKA/pages/195728007/KIP-801+Implement+an+Authorizer+that+stores+metadata+in+__cluster_metadata
- Basic Kafka operations, topic administration, and quota commands: https://kafka.apache.org/43/operations/basic-kafka-operations/
- Multi-tenancy, topic-creation controls, and partition-mutation quotas: https://kafka.apache.org/43/operations/multi-tenancy/
- Quota grouping, precedence, request-time accounting, and enforcement: https://kafka.apache.org/43/design/design/
- Producer configuration, idempotence, and transactional identity: https://kafka.apache.org/43/configuration/producer-configs/
- Consumer configuration and client security properties: https://kafka.apache.org/43/configuration/consumer-configs/
- Admin client configuration and security properties: https://kafka.apache.org/43/configuration/admin-configs/
- Kafka upgrades, ZooKeeper removal, and the Log4j2 migration: https://kafka.apache.org/43/getting-started/upgrade/
- Kafka monitoring and quota-throttle metrics: https://kafka.apache.org/43/operations/monitoring/
- ConfigCommand file loading, SCRAM parsing, and configuration descriptions, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/core/src/main/scala/kafka/admin/ConfigCommand.scala
- InitProducerId authorization, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/core/src/main/scala/kafka/server/KafkaApis.scala
- Distribution server configuration and example listener ports, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/config/server.properties
- Distribution Log4j2 configuration, authorizer appender, and log filenames, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/config/log4j2.yaml
- StandardAuthorizer audit levels and message fields, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/metadata/src/main/java/org/apache/kafka/metadata/authorizer/StandardAuthorizerData.java
- Authorizer Action audit-logging flags: https://kafka.apache.org/43/javadoc/org/apache/kafka/server/authorizer/Action.html
- Console producer options, configuration files, and synchronous sends, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/ConsoleProducer.java
- Console consumer options, configuration files, groups, and timeouts, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/consumer/ConsoleConsumerOptions.java
- Console consumer exception logging and exit behavior, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/consumer/ConsoleConsumer.java
- Broker API versions CLI options, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/BrokerApiVersionsCommand.java
- Topic administration CLI options and error handling, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/TopicCommand.java
- Producer performance CLI options and metrics, tagged 4.3.0: https://github.com/apache/kafka/blob/4.3.0/tools/src/main/java/org/apache/kafka/tools/ProducerPerformance.java
- OpenSSL s_client certificate and hostname verification: https://docs.openssl.org/3.5/man1/openssl-s_client/
- OpenSSL file-based private-key passphrases: https://docs.openssl.org/3.5/man1/openssl-passphrase-options/
