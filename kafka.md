# Apache Kafka: SASL_SSL listeners, SCRAM credentials, and ACLs

Kafka's broker defaults are `listeners=PLAINTEXT://:9092`, `security.inter.broker.protocol=PLAINTEXT`, and no authorizer, so anyone who reaches port 9092 can read every topic, produce to it, and create or delete topics with no credential and no encryption. Property names below come from the Kafka 4.x documentation (KRaft mode).

## 1. Replace the plaintext listener

In `server.properties`, publish one `SASL_SSL` listener and use it between brokers too. Remove `PLAINTEXT://:9092`; if local tooling still needs it, bind it to `127.0.0.1` and never advertise it. KRaft controllers use their own listener (`controller.listener.names`); map it to `SASL_SSL` in `listener.security.protocol.map` (the documentation's example is `BROKER:SASL_SSL,CONTROLLER:SASL_SSL`) or keep it on a private interface. Kafka's own default `server.properties` puts that controller listener on port 9093, the same port this broker listener uses below, so on a combined broker-and-controller node (`process.roles=broker,controller`) give the controller a different port, or Kafka rejects the duplicate listener port during startup validation ("Each listener must have a different port") and the broker does not start. The prefix in `listener.name.<name>.*` is the listener's name lowercased, so if you rename a listener you must rename the prefix on every such line in this guide; a prefix that matches no listener is silently ignored rather than rejected.

```properties
# combined broker+controller node: the controller listener must ALSO be in listeners and authenticated;
# mapping it to SASL_SSL alone does not authenticate it (the controller SASL mechanism defaults to GSSAPI).
listeners=SASL_SSL://0.0.0.0:9093,CONTROLLER://0.0.0.0:9094
advertised.listeners=SASL_SSL://kafka.example.com:9093
listener.security.protocol.map=SASL_SSL:SASL_SSL,CONTROLLER:SASL_SSL
controller.listener.names=CONTROLLER
inter.broker.listener.name=SASL_SSL
controller.quorum.bootstrap.servers=REPLACE_WITH_CONTROLLER_HOST:9094
sasl.mechanism.controller.protocol=PLAIN
listener.name.controller.sasl.enabled.mechanisms=PLAIN
listener.name.controller.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="controller" password="REPLACE_WITH_LONG_RANDOM_VALUE" user_controller="REPLACE_WITH_LONG_RANDOM_VALUE";
```

Select the inter-broker listener by NAME (`inter.broker.listener.name=SASL_SSL`); do not also set `security.inter.broker.protocol`, because the shipped `server.properties` sets `inter.broker.listener.name=PLAINTEXT` and setting both at once is a startup error. The controller quorum here authenticates with SASL/PLAIN over TLS rather than SCRAM: controller-to-controller SCRAM bootstrap is affected by an unresolved Apache issue (KAFKA-15513), so a multi-controller SCRAM quorum may fail to start; PLAIN keeps the credential in the static JAAS (out of version control), and mutual TLS on the controller listener is the alternative. Move `controller.quorum.bootstrap.servers` to the controller's own port and a certificate-matching hostname (it ships pointing at 9093, which is now the broker's port). If you would rather not authenticate the controller, keep its listener on a private, firewalled interface instead. The exact controller-listener properties are version-sensitive, so confirm them against the listener-configuration reference in Sources.

## 2. TLS on the broker

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md); an internal CA fits a cluster) and point the broker at it. Kafka 2.7.0 and later also take PEM: `ssl.keystore.type=PEM` with `ssl.keystore.certificate.chain` and `ssl.keystore.key` (PKCS#8), and `ssl.truststore.type=PEM` with `ssl.truststore.certificates`. Hostname verification (`ssl.endpoint.identification.algorithm`) is on by default since 2.0.0; the documentation discourages blanking it.

```properties
ssl.keystore.location=/var/private/ssl/server.keystore.jks
ssl.keystore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.key.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.truststore.location=/var/private/ssl/server.truststore.jks
ssl.truststore.password=REPLACE_WITH_LONG_RANDOM_VALUE
# Client certificates on the SASL_SSL listener: none (default), requested (optional), or required (mutual TLS).
# The unprefixed ssl.client.auth applies only to SSL listeners, so a SASL_SSL listener needs the listener prefix.
listener.name.sasl_ssl.ssl.client.auth=none
```

## 3. SASL/SCRAM credentials

The documentation says SCRAM should be used only with TLS, hence `SASL_SSL` rather than `SASL_PLAINTEXT`. In KRaft the inter-broker credential must exist before the brokers first start, so create it while formatting storage. Once the cluster is up, give each application its own credential ([authentication.md](authentication.md)) with `kafka-configs.sh`, authenticating as the admin through a properties file like the one in step 5.

```bash
# generate the cluster ID ONCE and reuse the SAME value when formatting every node - a fresh random-uuid
# per node produces mismatched IDs that will not form a cluster:
CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"   # capture once; use the same $CLUSTER_ID on each node
# the shipped combined-node config has no static voter list, so pass a quorum option: --standalone for a
# single combined node, or --initial-controllers / --no-initial-controllers for a multi-node quorum.
bin/kafka-storage.sh format -t "$CLUSTER_ID" -c config/server.properties --standalone \
  --add-scram 'SCRAM-SHA-512=[name="admin",password="REPLACE_WITH_LONG_RANDOM_VALUE"]'
# after the brokers are running:
bin/kafka-configs.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --alter --add-config 'SCRAM-SHA-512=[password=REPLACE_WITH_LONG_RANDOM_VALUE]' \
  --entity-type users --entity-name app
```

```properties
sasl.enabled.mechanisms=SCRAM-SHA-512
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
listener.name.sasl_ssl.scram-sha-512.sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="admin" password="REPLACE_WITH_LONG_RANDOM_VALUE";
```

## 4. Authorization

Without an authorizer every authenticated user can do everything. Enable the KRaft authorizer on every node, keep deny-by-default, and name only the admin as a super user; then grant each principal what it uses (`--producer` and `--consumer` add the matching operation sets).

```properties
authorizer.class.name=org.apache.kafka.metadata.authorizer.StandardAuthorizer
allow.everyone.if.no.acl.found=false
super.users=User:admin
```

```bash
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --add --allow-principal User:app --producer --topic orders
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --add --allow-principal User:app --consumer --topic orders --group app-workers
```

## 5. Client side

`client.properties`, kept out of the repository ([secrets.md](secrets.md)). MFA: the Kafka protocol has no second-factor dialogue; `listener.name.sasl_ssl.ssl.client.auth=required` (mutual TLS; the unprefixed `ssl.client.auth` applies only to `SSL` listeners, and Kafka logs a warning when it is set without the prefix on a `SASL_SSL` broker) is the possession factor for machine clients ([machine-auth.md](machine-auth.md)), and each client then presents its own keystore as in the last three lines below; human paths to the brokers or a management UI go behind MFA per [mfa.md](mfa.md).

```properties
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="app" password="REPLACE_WITH_LONG_RANDOM_VALUE";
ssl.truststore.location=/var/private/ssl/client.truststore.jks
ssl.truststore.password=REPLACE_WITH_LONG_RANDOM_VALUE
# only when the listener requires client certificates
ssl.keystore.location=/var/private/ssl/client.keystore.jks
ssl.keystore.password=REPLACE_WITH_LONG_RANDOM_VALUE
ssl.key.password=REPLACE_WITH_LONG_RANDOM_VALUE
```

## 6. Redpanda (and other Kafka-API-compatible systems)

Redpanda implements the Kafka wire protocol, so the client-side and protocol-level controls above carry over: SASL/SCRAM authentication, TLS, and ACL management through the Kafka API all work the same way against a Redpanda cluster, and the same fronting rules apply too. What does not carry over is how you wire that up on the broker: Redpanda configures brokers through `redpanda.yaml` and the `rpk` CLI, not Kafka's `server.properties`, JAAS configuration files, or `kafka-storage.sh`. Redpanda Console, its bundled web UI, ships without its own login screen: it only gains one once you configure OIDC or basic authentication, and that built-in Console login requires an enterprise licence, so until you configure it anyone who reaches Console reaches the cluster behind it (enabling the enterprise features without a valid licence does not open Console: it restricts access to a licence-expiration page instead). Front Console the same way as any other admin panel: never public, reached through SSH forwarding, a tailnet, or an access proxy, with MFA at that layer. See the [Redpanda security documentation](https://docs.redpanda.com/streaming/current/manage/security/).

## Verify

```bash
ss -tlnp   # a listener inventory in THIS namespace, not a firewall: the broker 9093 (and the controller
           # 9094) on the intended address, no PLAINTEXT listener on a public interface; probe the real
           # public IPv4/IPv6 path from another host too
openssl s_client -connect kafka.example.com:9093 -verify_hostname kafka.example.com \
  -verify_return_error -CAfile ca.pem </dev/null              # prints Verification: OK. Point -CAfile at
                                                              # the CA that signed the broker certificate;
                                                              # omit it only for a publicly trusted one,
                                                              # since an internal CA is not in the system
                                                              # store and the check would fail on a
                                                              # correct cluster. Without the verify flags
                                                              # the handshake succeeds against any
                                                              # certificate and shows only that TLS is on
                                                              # This matches the listener as configured above, which
                                                              # does not require client certificates. If you set
                                                              # listener.name.sasl_ssl.ssl.client.auth=required, add
                                                              # -cert and -key: without them the broker refuses the
                                                              # connection and "Verification: OK" still prints.
# The application checks below are REASONED, not demonstrated in this repo (no broker in the authoring
# environment; the demonstration debt is tracked in the backlog). Run them from an EXTERNAL host.
# 1) A PLAINTEXT (no TLS, no SASL) client must be refused, not served. plain.properties sets only
# security.protocol=PLAINTEXT:
bin/kafka-broker-api-versions.sh --bootstrap-server kafka.example.com:9093 --command-config plain.properties   # must FAIL to connect; a success is a finding, a local/DNS error is inconclusive
# 2) A wrong SCRAM password must be rejected at authentication. wrong.properties is client.properties with
# a deliberately wrong password:
bin/kafka-console-consumer.sh --bootstrap-server kafka.example.com:9093 --command-config wrong.properties \
  --group app-workers --topic orders --max-messages 1 --timeout-ms 10000   # must fail with SaslAuthenticationException
# 3) Deterministic positive control. Grant the app a fresh consumer-group PREFIX so a brand-new group (no
# committed offset) can read, then produce a UNIQUE marker and read it back, comparing the payload:
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --add --allow-principal User:app --operation Read --group verify- --resource-pattern-type prefixed
marker="verify-$(date +%s)-$$"
printf '%s\n' "$marker" | bin/kafka-console-producer.sh --bootstrap-server kafka.example.com:9093 --command-config client.properties --topic orders
bin/kafka-console-consumer.sh --bootstrap-server kafka.example.com:9093 --command-config client.properties \
  --group "$marker" --topic orders --from-beginning --timeout-ms 15000 | grep -qF "$marker" && echo "positive control OK" || echo "positive control FAILED or inconclusive"
# 4) Authorization deny-by-default, isolated to the TOPIC. Create a second low-privilege SCRAM user (low,
# like app in step 3) and grant it ONLY a consumer-group prefix - no topic ACL - then consume a topic with
# no ACL of any pattern. A TopicAuthorizationException is the pass; an empty success means
# allow.everyone.if.no.acl.found is true, and a group error would mean the group ACL is missing not the topic:
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --add --allow-principal User:low --operation Read --group verify-deny- --resource-pattern-type prefixed
bin/kafka-acls.sh --bootstrap-server kafka.example.com:9093 --command-config admin.properties \
  --list --topic REPLACE_WITH_TOPIC_WITH_NO_ACL --resource-pattern-type match   # must show NO ACL for this topic
bin/kafka-console-consumer.sh --bootstrap-server kafka.example.com:9093 --command-config low.properties \
  --group "verify-deny-$$" --topic REPLACE_WITH_TOPIC_WITH_NO_ACL --max-messages 1 --timeout-ms 10000   # must be DENIED with TopicAuthorizationException
```

## Common mistakes

- `SASL_SSL` added as a second listener while `PLAINTEXT://:9092` stays advertised, so clients quietly keep using it.
- Authorizer enabled with `allow.everyone.if.no.acl.found=true` "temporarily". The flag opens only resources that have no ACL at all; existing ACLs are still enforced. That still means every new topic is world-readable and world-writable until someone adds its first ACL, so keep it `false`.

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
