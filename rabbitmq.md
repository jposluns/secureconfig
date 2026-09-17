# RabbitMQ: users, TLS listener, and the guest account

RabbitMQ's default `guest`/`guest` account can only connect from localhost, which protects fresh installs exactly until someone "fixes" it. The documented recommendation is to create real users and delete `guest` or change its password.

## 1. Accounts

```bash
sudo rabbitmqctl add_user 'app' 'REPLACE_WITH_LONG_RANDOM_PASSWORD'
sudo rabbitmqctl set_permissions -p '/' 'app' '.*' '.*' '.*'   # configure, write, read; narrow per app
sudo rabbitmqctl add_user 'ops' 'REPLACE_WITH_A_DIFFERENT_LONG_RANDOM_PASSWORD'
sudo rabbitmqctl set_user_tags 'ops' administrator
sudo rabbitmqctl delete_user 'guest'
```

Scope the permission regexes to what each application actually uses, per [authentication.md](authentication.md). Do not loosen the guest account's localhost restriction. Exported definitions (`rabbitmqctl export_definitions`, or the management `/api/definitions`) contain user password hashes and hashing metadata, which RabbitMQ classifies as sensitive; store any export access-restricted, keep it out of images and version control, and sanitize it before sharing ([secrets.md](secrets.md)).

## 2. TLS listener

`rabbitmq.conf`:

```
listeners.ssl.default = 5671
ssl_options.cacertfile = /etc/rabbitmq/tls/ca.pem
ssl_options.certfile   = /etc/rabbitmq/tls/server.pem
ssl_options.keyfile    = /etc/rabbitmq/tls/server.key
ssl_options.verify     = verify_peer
# mutual TLS; set false to allow password-only clients
ssl_options.fail_if_no_peer_cert = true

# once every client speaks TLS:
listeners.tcp = none
```

Certificates per [self-signed.md](self-signed.md) (internal CA fits brokers well) or [free-certificates.md](free-certificates.md) cover the SERVER certificate; mutual TLS additionally needs a CLIENT certificate carrying `clientAuth` in its extended key usage, chaining to a CA trusted via `ssl_options.cacertfile` (intermediates allowed; the Verify pair below depends on it). Mutual TLS gives a machine client a possession factor, a certificate held by the connecting host, stronger than a password alone but not MFA for a person ([mfa.md](mfa.md)).

## 3. Management UI

The management plugin's web UI is an admin panel: keep it off public interfaces and reach it per [admin-uis.md](admin-uis.md) (SSH forward, tailnet, or Access), with its own TLS when remote.

## 4. epmd and the Erlang distribution port

Two more listeners exist that the AMQP and management ports do not reveal, and they are the most dangerous to expose: epmd (default `4369`, the Erlang Port Mapper Daemon, which maps Erlang node names to ports) and the inter-node Erlang distribution port (default `25672`, the AMQP port plus 20000; `RABBITMQ_DIST_PORT` or a configured port range can move it). The distribution port carries the clustering and CLI-tool protocol.

By default the only credential on the distribution port is the Erlang cookie: a shared secret in the server's `/var/lib/rabbitmq/.erlang.cookie`, with a copy in each CLI user's `$HOME/.erlang.cookie`, owner-only at mode `600` or similar. Passing it on the command line (`--erlang-cookie`) or through `-setcookie` is the least secure way to set it. Any peer that reaches the distribution port and authenticates with the matching cookie is treated as a cluster node or CLI tool with full control of the broker; `rabbitmqctl` works exactly this way, so cookie plus reachability is `rabbitmqctl` for anyone. A default, weak, or leaked cookie on a published distribution port is a remote compromise of the node, not merely a message-queue exposure. Inter-node (distribution) TLS can additionally require a trusted peer certificate; where it is not configured, the cookie is the only barrier.

RabbitMQ's own guidance is to expose these ports only to the hosts and subnets that run other cluster nodes or CLI tools, and not to the public internet. Tutorial `docker-compose.yml` files routinely publish them (`ports: - 25672:25672` and `- 4369:4369`); do not. Bind them to the cluster's private network, firewall them to peer addresses, give the cookie a long random value kept out of the image and the compose file, and if you moved either port, filter for your configured values in the check below.

## 5. Verify

```bash
ss -tlnp   # inventory every listener (5671 AMQPS, 15672 UI, 4369 epmd, 25672 distribution; 5672 gone once listeners.tcp = none). ss shows the BIND, not the firewall: a private-address OR a 0.0.0.0 listener says nothing about who can actually reach it, so test reachability below rather than reading the bind as isolation.
# Test reachability, not the bind. On the set -- line put the broker's PUBLIC address first and its
# PRIVATE distribution address (often a separate interface) second; do NOT reuse one hostname for both,
# since split DNS could let an external load balancer and an internal broker each 'pass'. Positional
# parameters carry them (not shell variables, which a reader's environment could have typed or made
# readonly), and the subshell contains its own exit:
( set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_PUBLIC_ADDR' 'REPLACE_WITH_BROKER_PRIVATE_ADDR'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values (public then private address); not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the broker PUBLIC address on the set -- line; not probing"; exit;; esac
  case "$2" in *REPLACE_WITH_*|"") echo "substitute the broker PRIVATE distribution address on the set -- line; not probing"; exit;; esac
  # epmd 4369, distribution 25672, and the management UI 15672 (15671 if TLS) are the remote-compromise
  # and admin surface (cookie + reach to 25672 = rabbitmqctl). From a NON-PEER host none must accept a
  # TCP connection: a completed connect is a finding; a DNS or routing error is INCONCLUSIVE, not a pass;
  # a refusal can also just mean nothing listens there, so pair it with the peer control below:
  for p in 4369 25672 15672; do nc -vz -w 5 "$1" "$p"; done
  # positive control from an ALLOWED peer against the PRIVATE interface: the cluster ports DO connect,
  # so an external failure above is the firewall or the bind, not a dead port (no public bind required):
  for p in 4369 25672; do nc -vz -w 5 "$2" "$p"; done
)
# the Erlang cookie is the only credential on 25672 when inter-node TLS is off; confirm it is owner-only:
sudo stat -c '%a %U' /var/lib/rabbitmq/.erlang.cookie   # expect 600 (or 400), owner rabbitmq. Mode alone does not prove the value is long/random or absent from your image/compose file

# Positive: a client holding a certificate connects.
# client.pem and client.key are a CLIENT certificate and key issued by the CA in
# ssl_options.cacertfile, with TLS Web Client Authentication in its extended key usage.
# A serverAuth-only certificate signed by that same CA is NOT a substitute, and the
# reason is the extended key usage rather than the chain: the chain verifies either way,
# which is what makes this an easy mistake to make and a hard one to see. A certificate
# carrying both serverAuth and clientAuth does satisfy it, which RabbitMQ documents
# while still recommending separate certificates for the two purposes.
sleep 10 | openssl s_client -connect mq.example.com:5671 -CAfile ca.pem \
  -cert client.pem -key client.key \
  -verify_hostname mq.example.com -verify_return_error
echo "positive run exit $?"

# Negative, and this half is what discriminates: drop -cert and -key, and the broker must
# refuse the connection, because ssl_options.fail_if_no_peer_cert = true requires one.
sleep 10 | openssl s_client -connect mq.example.com:5671 -CAfile ca.pem \
  -verify_hostname mq.example.com -verify_return_error
echo "negative run exit $?"

# "Verification: OK" reports the SERVER certificate only, and it prints in BOTH runs. The
# pass condition is the pair: the first run exits 0 and the second does not. Do
# not match on a particular message. The broker rejects an empty client certificate list
# with a fatal alert. On TLS 1.3 the client can consider its own side finished before that
# alert arrives, and the exact wording comes from whichever TLS stack is reporting it.
# What you are looking for is a non-zero exit from the second run. Note the `sleep 10` on
# BOTH runs: with `</dev/null` s_client reaches end of input and exits before the rejection
# arrives, because on TLS 1.3 the server can only refuse the empty client certificate after
# the client's flight. Measured, that negative run exits 0 and prints a full session block
# four times in five, which is indistinguishable from the positive one. Holding stdin open
# is what makes the refusal observable, and the hold has to outlast the broker's own
# handshake timeout, not just the round trip: `sleep 10` starts at the same moment as
# s_client, before DNS, the TCP connect and the negotiation, so a short hold can be spent
# before the moment it was meant to cover. This check is timing-dependent and says so. If
# BOTH runs exit 0, treat that as inconclusive rather than as a pass, and read the broker
# log, which records the rejection regardless of what the client saw. The positive run
# needs it for the same reason in reverse: with `</dev/null` it exits 0 before a rejection
# of a WRONG client certificate can arrive, so a broken deployment reads as a working one.
# A non-zero exit on the NEGATIVE run is only meaningful if it is the missing-client-certificate
# rejection: a connection error, or a SERVER-certificate verification failure (which
# -verify_return_error also makes fatal), exits non-zero WITHOUT testing fail_if_no_peer_cert, so
# confirm the broker log attributes the refusal to the absent peer certificate.
# Reading "Verification: OK" from the second run as a success is the mistake this pair
# exists to catch. Without -verify_return_error the handshake completes even when the
# server certificate fails to verify, so -CAfile alone proves only that TLS is on. If you
# set fail_if_no_peer_cert = false, the second run succeeds as well and the pair proves
# nothing, because a password is then the client's only identity.
# guest: section 1 DELETED it, so confirm it is gone rather than testing the localhost message:
sudo rabbitmqctl list_users    # 'guest' must not be listed (a failed command is inconclusive, not a pass). (If you instead KEPT guest and only restricted it, a REMOTE guest login fails with "user 'guest' can only connect via localhost".)
# and confirm auth is enforced end to end: a REMOTE login as a real app user over TLS succeeds, an unknown user is refused
```

## Sources (checked September 2026)

- RabbitMQ TLS: https://www.rabbitmq.com/docs/ssl
- RabbitMQ access control (guest restrictions, user commands, recommendation): https://www.rabbitmq.com/docs/access-control
- RabbitMQ networking (epmd on 4369, inter-node distribution on 25672 = node port + 20000, restrict these ports to cluster hosts): https://www.rabbitmq.com/docs/networking
- RabbitMQ CLI tools and the Erlang cookie (shared secret in `.erlang.cookie` or `RABBITMQ_ERLANG_COOKIE`, full control of the node): https://www.rabbitmq.com/docs/cli
- RabbitMQ definitions export (contains user password hashes and hashing metadata; user records are sensitive): https://www.rabbitmq.com/docs/definitions
