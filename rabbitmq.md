# RabbitMQ: users, TLS listener, and the guest account

RabbitMQ's default `guest`/`guest` account can only connect from localhost, which protects fresh installs exactly until someone "fixes" it. The documented recommendation is to create real users and delete `guest` or change its password.

The settings below were checked against the current RabbitMQ 4.3 documentation in September 2026. These controls are available in open source RabbitMQ; no commercial edition is required. The export command specifically requires a current `rabbitmqadmin` v2, not v1.

## 1. Accounts

An unrestricted application grant on `/` lets a compromised application manipulate unrelated resources in that shared vhost. Give each application and environment its own user and vhost. For initial provisioning:

```bash
sudo rabbitmqctl add_vhost 'app-prod'
sudo rabbitmqctl add_user 'app'
# Enter a generated password at the interactive prompt.
# Permission order: configure, write, read.
sudo rabbitmqctl set_permissions -p 'app-prod' 'app' \
  '^app[.].*$' '^app[.].*$' '^app[.].*$'
sudo rabbitmqctl set_user_tags 'app'

sudo rabbitmqctl add_user 'ops'
# Enter a different generated password at the interactive prompt.
sudo rabbitmqctl set_user_tags 'ops' administrator

sudo rabbitmqctl add_user 'observer'
# Enter a third generated password at the interactive prompt.
sudo rabbitmqctl set_user_tags 'observer' monitoring
sudo rabbitmqctl set_permissions -p 'app-prod' 'observer' '^$' '^$' '^$'

sudo rabbitmqctl delete_user 'guest'
```

For existing accounts or vhosts, omit their creation commands. Provision the required topology in `app-prod`, migrate clients to that vhost, then remove the application's old grant:

```bash
sudo rabbitmqctl clear_permissions -p '/' 'app'
sudo rabbitmqctl list_user_permissions 'app'
```

The patterns permit resource names beginning `app.`. They exclude the default exchange, whose permission-check name is `amq.default`. Queue binding requires write permission on the queue and read permission on the exchange. Reconnect clients after permission changes. Review patterns explicitly for applications using generated queue names or shared resources; see [authentication.md](authentication.md). These commands manage RabbitMQ's internal authorization store; external backends need their own rules. Vhosts provide logical isolation, not dedicated CPU or memory. See [resource permissions](https://www.rabbitmq.com/docs/access-control) and [vhost isolation](https://www.rabbitmq.com/docs/vhosts).

Retain `ops` for administration and use `observer` for monitoring. Tags do not grant resource permissions; the observer's three `^$` patterns prevent message and topology operations. `set_user_tags` replaces existing tags.

| Tag | Relevant authority |
|---|---|
| No tags | No management-plugin access. |
| `management` | Management access within permitted vhosts. |
| `monitoring` | Management access plus cluster-wide operational visibility. |
| `policymaker` | Management access plus policy/parameter management in permitted vhosts. |
| `administrator` | Monitoring and policymaker authority plus user, vhost, and permission administration. |

Monitoring and policymaker are separate extensions of management access. Resource listings remain limited to vhosts with a permission entry. Review existing observer grants on other vhosts as well. See [management roles](https://www.rabbitmq.com/docs/management) and [tag replacement](https://www.rabbitmq.com/docs/man/rabbitmqctl.8).

Do not loosen the guest account's localhost restriction. Exported definitions contain password hashes and hashing metadata; keep exports access-restricted and out of images and version control ([secrets.md](secrets.md)). Definitions imports are privileged provisioning input: a stale or untrusted file can introduce accounts, grants, policies, or plugin parameters.

For boot provisioning, use a reviewed local file in `rabbitmq.conf`:

```ini
definitions.import_backend = local_filesystem
definitions.local.path = /etc/rabbitmq/definitions/approved.json
```

Keep the directory administrator-owned and the file readable by RabbitMQ but not writable by it. Review accounts, permissions, policies, and runtime parameters before deployment. Core boot imports do not require management. They do not overwrite existing broker definitions, so they cannot reconcile or revoke stale grants. A blank node importing definitions does not create the default user and vhost; the approved file must supply the intended accounts and vhosts. See [boot import behaviour](https://www.rabbitmq.com/docs/definitions).

Runtime imports through `rabbitmqadmin definitions import` or `POST /api/definitions` merge with existing state: omitted objects remain, conflicting mutable objects are overwritten, and conflicting immutable queues, exchanges, and bindings retain their existing definitions. An error can leave a partial import. Do not treat runtime import as full reconciliation either. See [HTTP API import semantics](https://www.rabbitmq.com/docs/http-api-reference#post-apidefinitions).

For a reduced export, provision `$HOME/.rabbitmqadmin.conf` as an owner-only TOML file through your secret-management workflow. Replace the illustrative hostname and password, preserving valid TOML escaping:

```toml
[secureconfig]
hostname = "management.example.com"
port = 15671
username = "ops"
password = "REPLACE_WITH_OPS_PASSWORD"
```

Run this in a private directory, using a new output pathname:

```bash
( umask 077
  if [ -e ./definitions.redacted.json ] || [ -L ./definitions.redacted.json ]; then
    echo "choose a new export pathname; refusing to overwrite"
    exit 1
  fi
  rabbitmqadmin --config "$HOME/.rabbitmqadmin.conf" --node secureconfig \
    --use-tls --tls-ca-cert-file /etc/rabbitmq/tls/ca.pem \
    definitions export --file ./definitions.redacted.json \
    --transformations exclude_users,exclude_permissions,exclude_runtime_parameters
)
```

The v2 transformations remove users, permissions, and runtime parameters. Keep the result private pending review: arbitrary plugin data can still contain secrets. A sanitized export is not a complete account-recovery backup. See [export transformations](https://www.rabbitmq.com/docs/definitions) and [rabbitmqadmin configuration and TLS](https://www.rabbitmq.com/docs/management-cli).

## 2. TLS listener

In `rabbitmq.conf`, replace `listeners.ssl.default` with the private listener below; do not retain a wildcard TLS listener alongside it. Substitute the broker's private IPv4 address:

```ini
listeners.ssl.1 = REPLACE_WITH_BROKER_PRIVATE_IP:5671
ssl_options.cacertfile = /etc/rabbitmq/tls/ca.pem
ssl_options.certfile = /etc/rabbitmq/tls/server.pem
ssl_options.keyfile = /etc/rabbitmq/tls/server.key
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true

# After migrating every client to TLS:
listeners.tcp = none
```

Certificates per [self-signed.md](self-signed.md) (an internal CA fits brokers well) or [free-certificates.md](free-certificates.md) cover the server certificate. Use a separate client certificate with `clientAuth` extended key usage and a chain trusted by `ssl_options.cacertfile`. Intermediate chains must fit `ssl_options.depth`; the documented default is 1. The Verify examples assume a client certificate issued directly by the trusted CA. Mutual TLS supplies a machine possession factor, not human MFA ([mfa.md](mfa.md)).

Requiring a trusted client certificate does not map it to a RabbitMQ username. Clients here still authenticate with their RabbitMQ username and password. Certificate-to-user authentication requires the separate certificate authentication plugin and the SASL `EXTERNAL` mechanism; it is not configured by these listener settings. See [TLS verification and certificate usage](https://www.rabbitmq.com/docs/ssl) and [certificate-based user authentication](https://www.rabbitmq.com/docs/access-control).

## 3. Management UI

The management plugin's web UI is an admin panel: keep it off public interfaces and reach it per [admin-uis.md](admin-uis.md) (SSH forward, tailnet, or Access), with its own TLS when remote. First add its independent restricted listener configuration to `rabbitmq.conf`, substituting the broker's private IPv4 address:

```ini
management.tcp.ip = 127.0.0.1
management.tcp.port = 15672

management.ssl.ip = REPLACE_WITH_BROKER_PRIVATE_IP
management.ssl.port = 15671
management.ssl.cacertfile = /etc/rabbitmq/tls/ca.pem
management.ssl.certfile = /etc/rabbitmq/tls/management.pem
management.ssl.keyfile = /etc/rabbitmq/tls/management.key
```

Start or restart the node through your deployment's service manager with this configuration in place BEFORE enabling the plugin. `rabbitmq.conf` changes require a node restart; editing the file alone does not update a running node. The plugin reads the effective listener configuration when it starts. Enabling it on a running broker starts it immediately; without listener restrictions, HTTP listens on all interfaces at port `15672`. See [configuration application](https://www.rabbitmq.com/docs/configure#when-will-configuration-file-changes-be-applied) and [plugin activation](https://www.rabbitmq.com/docs/plugins#different-ways-to-enable-plugins).

Only after that start/restart succeeds, enable the plugin if it is not already enabled:

```bash
sudo rabbitmq-plugins enable rabbitmq_management
```

If the plugin is already enabled, apply the restricted configuration and restart the node before it becomes reachable, or keep management access firewalled until the restart and listener verification in check 2 are complete.

This deliberately retains HTTP on loopback and exposes HTTPS only on the selected private address. Restrict HTTPS reachability to administration hosts. The management certificate must cover the management hostname. AMQP `ssl_options` do not configure management TLS.

Standard internal-user HTTP authentication uses RabbitMQ credentials. Use the observer role from section 1 for monitoring and keep `ops` separate. Human MFA guidance remains in [admin-uis.md](admin-uis.md) and [mfa.md](mfa.md). See [management HTTPS and listener configuration](https://www.rabbitmq.com/docs/management) and [HTTP API authentication](https://www.rabbitmq.com/docs/http-api-reference).

## 4. epmd and the Erlang distribution port

Two more listeners exist beyond AMQP and management: epmd, the Erlang Port Mapper Daemon, defaults to `4369`; the distribution listener defaults to `25672`, derived from `RABBITMQ_NODE_PORT` plus 20000. The latter carries clustering and CLI traffic. Pin its private IPv4 address and port in `rabbitmq.conf`:

```ini
distribution.listener.interface = REPLACE_WITH_BROKER_PRIVATE_IP
distribution.listener.port_range.min = 25672
distribution.listener.port_range.max = 25672
```

When RabbitMQ starts epmd, supply this in the actual service/container launch environment, not merely an unrelated interactive shell:

```bash
export ERL_EPMD_ADDRESS='REPLACE_WITH_BROKER_PRIVATE_IP'
```

Changing `ERL_EPMD_ADDRESS` requires stopping both RabbitMQ and epmd before starting them with the new environment. Restarting RabbitMQ alone is insufficient. Socket-activated epmd instead needs its `epmd.socket` binding configured. epmd implicitly retains loopback access. Use a private address reachable by cluster peers; loopback-only distribution suits a single node with local CLI access.

Bindings do not replace firewall rules. Allow these ports only from cluster peers and authorized CLI hosts; do not publish them publicly in Compose port mappings. Remote CLI tools also use their own distribution-port range, by default `35672` through `35682`; restrict the actual range to the necessary peers. See [networking and epmd lifecycle](https://www.rabbitmq.com/docs/networking).

The Erlang cookie is a shared secret granting powerful node and CLI access. On typical Unix installations the server uses `/var/lib/rabbitmq/.erlang.cookie`, and CLI users use `$HOME/.erlang.cookie`. Keep matching copies owner-only, normally mode `600`, with a long random value supplied through secret management. Keep it out of images and Compose files, and never pass its value through command-line arguments. Cookie possession plus distribution reachability can give full broker control. See [CLI authentication](https://www.rabbitmq.com/docs/cli).

Restart the node through your deployment's service manager after applying listener configuration, including the separate epmd lifecycle change where needed.

## 5. Verify

Service behaviour has not been demonstrated in the authoring environment. The nine service checks below are REASONED: RabbitMQ/Erlang binaries, `rabbitmqadmin`, Pika, Docker, and Podman are absent, and no broker or external peer test environment was supplied. Outstanding demonstrations are tracked in `RABBITMQ-LIVE-1` below.

Use Bash and paste whole guarded blocks. Substitute inside the single quotes on each `set --` line, retaining the quotes; do not insert literal apostrophes. The guards assume real shell builtins. A fragment pasted below its guard is unguarded, and inherited arguments identical to the marker and expected values cannot be distinguished from a complete paste. Use curl 7.75.0 or newer for the diagnostic write-out fields. `--user` below contains only a username and prompts for the password; do not append a password.

**1. Accounts and roles - REASONED: no `rabbitmqctl` or broker is available.** Run after migration and reconnecting clients:

```bash
sudo rabbitmqctl list_users
sudo rabbitmqctl list_user_permissions 'app'
sudo rabbitmqctl list_permissions -p 'app-prod'
sudo rabbitmqctl list_vhosts
```

Compare the exposed state's unrestricted `/` grant and excessive operator privileges with the fixed state: `app` has only the intended `app-prod` grant, `observer` has `monitoring` without `administrator` and three `^$` patterns, and `guest` is absent. A failed listing proves nothing. Confirm an existing ungranted vhost for the protocol test below; do not substitute a nonexistent vhost. The [CLI permission commands](https://www.rabbitmq.com/docs/man/rabbitmqctl.8) expose these records; checks 4 and 6 test their effect.

**2. Listener and cookie inventory - REASONED: no RabbitMQ node, epmd, or deployed cookie is available.** After the restart:

```bash
sudo rabbitmq-diagnostics -s listeners
ss -tlnp
epmd -names
sudo stat -c '%a %U' /var/lib/rabbitmq/.erlang.cookie
```

Expect AMQPS on the selected private address at `5671`, HTTPS there at `15671`, HTTP only on `127.0.0.1:15672`, distribution on the private address at `25672`, and no plaintext AMQP listener on `5672`. epmd should bind privately and on loopback; `epmd -names` reports the registered distribution port, not epmd's interface bindings. Inspect all `ss` output, including IPv6 and additional plugin listeners. The exposed comparison has wildcard/public listeners or plaintext AMQP still enabled.

On the conventional installation above, the cookie should be owned by `rabbitmq` and mode `600` or `400`; broader access is a finding. Mode alone does not prove randomness or absence from images. Listener addresses alone do not establish firewall isolation. These expectations follow [listener configuration](https://www.rabbitmq.com/docs/networking) and [cookie permissions](https://www.rabbitmq.com/docs/cli).

**3. Reachability - REASONED: no broker, administration host, application host, or cluster peer is available.** Inventory actual ports first; update every corresponding probe if any port differs, and add probes for extra listeners.

From an external non-peer host, target the broker's public address:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_PUBLIC_ADDR'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "need exactly 1 public address; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the public address; not probing"; exit 1 ;;
    *)
      for p in 4369 25672 15672 15671 5671; do
        nc -vz -w 5 "$1" "$p"
      done
      # Removed plaintext AMQP is checked separately.
      nc -vz -w 5 "$1" 5672
    ;;
  esac
)
```

From hosts allowed by the corresponding firewall rules, target the private address. Execute the cluster, application, and administration commands on their respective allowed hosts if those roles are separate:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_PRIVATE_ADDR'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "need exactly 1 private address; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the private address; not probing"; exit 1 ;;
    *)
      # Run from an allowed cluster/CLI host.
      for p in 4369 25672; do nc -vz -w 5 "$1" "$p"; done
      # Run these from the respective allowed application and administration hosts.
      nc -vz -w 5 "$1" 5671
      nc -vz -w 5 "$1" 15671
      # Neither listener should accept connections on the private interface.
      nc -vz -w 5 "$1" 15672
      nc -vz -w 5 "$1" 5672
    ;;
  esac
)
```

From an allowed CLI host with its owner-only matching cookie file, also require an authenticated distribution connection to the same broker. Supply its actual node name, such as the deployed `rabbit@` name. This form assumes short node names; add `--longnames` for a deployment using long names. The documented [diagnostics ping](https://www.rabbitmq.com/docs/man/rabbitmq-diagnostics.8) checks authentication as well as reachability:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BROKER_NODE_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "need exactly 1 node name; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the broker node name; not probing"; exit 1 ;;
    *)
      sudo rabbitmq-diagnostics -n "$1" ping
    ;;
  esac
)
```

On the broker itself, confirm that the retained HTTP management listener works with authentication:

```bash
curl -q -g --noproxy '*' --connect-timeout 5 --max-time 20 \
  -sS --user observer -o /dev/null \
  -w 'loopback http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'http://127.0.0.1:15672/api/overview'
```

The exposed state accepts prohibited external connections; the fixed state refuses them while the allowed private ports connect and the loopback API returns HTTP 200. Pair these TCP controls with the authenticated API and AMQP checks below. Public and private targets must identify the same broker; do not reuse one split-DNS hostname for both. DNS/routing errors, a dead service, or an unidentified endpoint make a failure inconclusive.

For removed plaintext AMQP, first demonstrate a connection to its old listener in an isolated exposed deployment, then show both its absence from the fixed listener inventory and refusal on `5672`, with authenticated AMQPS still working. This distinguishes listener removal from a stopped broker. See [RabbitMQ ports and binding](https://www.rabbitmq.com/docs/networking).

**4. Management authentication and roles - REASONED: no broker or management endpoint is available.** From an allowed administration host, use the management certificate's hostname:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MANAGEMENT_HOSTNAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "need exactly 1 hostname; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the management hostname; not probing"; exit 1 ;;
    *)

      # Username only: curl prompts for the password.
      curl -q -g --noproxy '*' --cacert /etc/rabbitmq/tls/ca.pem \
        --connect-timeout 5 --max-time 20 -sS --user observer \
        -w 'observer http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:15671/api/overview"
      curl -q -g --noproxy '*' --cacert /etc/rabbitmq/tls/ca.pem \
        --connect-timeout 5 --max-time 20 -sS \
        -w 'anonymous http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:15671/api/overview"

      # Paired administrative authority check; each password is prompted separately.
      curl -q -g --noproxy '*' --cacert /etc/rabbitmq/tls/ca.pem \
        --connect-timeout 5 --max-time 20 -sS --user ops \
        -w 'ops http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:15671/api/users"
      curl -q -g --noproxy '*' --cacert /etc/rabbitmq/tls/ca.pem \
        --connect-timeout 5 --max-time 20 -sS --user observer \
        -w 'observer http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:15671/api/users"
    ;;
  esac
)
```

Require HTTP 200 for the observer's overview and the administrator's user listing. The anonymous overview must return an authentication refusal, and the observer's user listing must return an authorization refusal; inspect the response body and correlate authentication failures before accepting a denial. Transport failures, HTTP 000, redirects, and server errors are inconclusive. Retain output privately because administrative responses may contain sensitive account metadata.

An exposed management listener can still require authentication: external reachability is tested separately in check 3. For the excessive-role comparison, an observer carrying `administrator` can list users; after correction it retains overview access but loses that administrative access. If anonymous overview access succeeds through the deployed path, that is an additional finding. See [management roles](https://www.rabbitmq.com/docs/management) and the [overview and users endpoints](https://www.rabbitmq.com/docs/http-api-reference).

**5. Mutual TLS - REASONED: no broker, trusted test certificates, or broker logs are available.** From an allowed application host, place `ca.pem`, `client.pem`, and the protected `client.key` in the working directory. Use a valid client certificate with `clientAuth`, not a server-only certificate:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_AMQP_HOSTNAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "need exactly 1 hostname; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the AMQP hostname; not probing"; exit 1 ;;
    *)

      # Keep stdin open to allow a delayed TLS rejection to arrive.
      if sleep 10 | openssl s_client -connect "$1:5671" -servername "$1" \
        -CAfile ca.pem -cert client.pem -key client.key \
        -verify_hostname "$1" -verify_return_error; then
        echo "certificate-present run exited 0; inspect the handshake and broker log"
      else
        echo "positive control failed; the pair is inconclusive"
        exit 1
      fi

      if sleep 10 | openssl s_client -connect "$1:5671" -servername "$1" \
        -CAfile ca.pem -verify_hostname "$1" -verify_return_error; then
        echo "certificate-absent run exited 0; required rejection was not demonstrated"
        exit 1
      else
        echo "negative run failed; require a matching missing-client-certificate broker log"
      fi
    ;;
  esac
)
```

`Verification: OK` describes verification of the server certificate only. Require a successful certificate-present handshake plus a certificate-absent failure attributed by the broker to the missing client certificate. A DNS error, TCP failure, server-certificate failure, or unrelated timeout is not the required rejection.

Keeping stdin open helps expose delayed TLS 1.3 alerts; ten seconds is a timing-dependent observation window, not a guarantee. Both runs exiting zero is inconclusive. If the positive run closes because no AMQP protocol handshake followed, use the protocol client in check 6 and broker logs to resolve it. In the isolated exposed comparison with client certificates optional, the certificate-absent handshake succeeds too. See [peer verification](https://www.rabbitmq.com/docs/ssl).

**6. AMQP authentication and authorization - REASONED: no RabbitMQ broker or Pika client package is available.** Run with Python 3 and Pika 1.x using the TLS files from check 5. Passwords are prompted from the terminal. Use an isolated test deployment: the script creates a uniquely named durable queue and direct exchange and deletes them on normal completion; inspect and remove its `app.secureconfig.*` fixtures after an interrupted run.

The positive control declares, binds, publishes, and retrieves a message as `app`. Separate channels test resource denials. The shared queue is durable because RabbitMQ 4.3 disables transient non-exclusive queues by default; an exclusive queue would make the observer's read test ambiguous. The script uses the [documented permission model](https://www.rabbitmq.com/docs/access-control), [channel error codes](https://www.rabbitmq.com/docs/channels), [queue rules](https://www.rabbitmq.com/docs/queues), and [Pika's blocking client](https://pika.readthedocs.io/en/stable/modules/adapters/blocking.html).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_AMQP_HOSTNAME' 'REPLACE_WITH_EXISTING_UNGRANTED_VHOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "need hostname and existing ungranted vhost; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the AMQP hostname; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|"") echo "substitute the ungranted vhost; not probing"; exit 1 ;;
        *)
          python3 - "$1" "$2" <<'PY'
import getpass
import ssl
import sys
import uuid
import warnings

import pika

warnings.simplefilter("error", getpass.GetPassWarning)
host, other_vhost = sys.argv[1:]
context = ssl.create_default_context(cafile="ca.pem")
context.load_cert_chain("client.pem", "client.key")
app_password = getpass.getpass("app password: ")
observer_password = getpass.getpass("observer password: ")
findings = []

def connect(user, password, vhost):
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=host, port=5671, virtual_host=vhost,
        credentials=pika.PlainCredentials(user, password),
        ssl_options=pika.SSLOptions(context, host),
        socket_timeout=5, stack_timeout=15, blocked_connection_timeout=15))

def denied_operation(connection, label, operation):
    channel = connection.channel()
    channel.confirm_delivery()
    try:
        operation(channel)
    except pika.exceptions.ChannelClosedByBroker as exc:
        if exc.reply_code != 403:
            raise
        print(label + ": ACCESS_REFUSED; correlate with the broker log")
    else:
        findings.append(label)
        print(label + ": UNEXPECTED ALLOW")
    finally:
        if channel.is_open:
            channel.close()

def denied_connection(user, password, vhost, expected_error, label):
    try:
        connection = connect(user, password, vhost)
    except expected_error:
        print(label + ": refused; require the matching broker-log reason")
    else:
        connection.close()
        findings.append(label)
        print(label + ": UNEXPECTED ALLOW")

name = "app.secureconfig." + uuid.uuid4().hex
with connect("app", app_password, "app-prod") as app:
    channel = app.channel()
    channel.exchange_declare(exchange=name, exchange_type="direct", durable=True)
    try:
        channel.queue_declare(queue=name, durable=True,
                              arguments={"x-queue-type": "classic"})
        try:
            channel.queue_bind(queue=name, exchange=name, routing_key="verify")
            channel.confirm_delivery()
            channel.basic_publish(exchange=name, routing_key="verify",
                                  body=b"secureconfig", mandatory=True)
            method, properties, body = channel.basic_get(queue=name, auto_ack=True)
            if method is None or body != b"secureconfig":
                raise RuntimeError("positive message round trip failed")
            print("app: authenticated; declare, bind, publish and get succeeded")

            denied_operation(app, "app unrelated queue", lambda ch:
                ch.queue_declare(queue="unrelated." + uuid.uuid4().hex,
                                 exclusive=True))
            denied_operation(app, "app default exchange", lambda ch:
                ch.basic_publish(exchange="", routing_key=name,
                                 body=b"denial probe", mandatory=True))

            with connect("observer", observer_password, "app-prod") as observer:
                print("observer: authenticated to app-prod")
                denied_operation(observer, "observer configure", lambda ch:
                    ch.queue_declare(queue=name + ".observer", exclusive=True))
                denied_operation(observer, "observer publish", lambda ch:
                    ch.basic_publish(exchange=name, routing_key="verify",
                                     body=b"denial probe", mandatory=True))
                denied_operation(observer, "observer get", lambda ch:
                    ch.basic_get(queue=name, auto_ack=True))

            denied_connection("secureconfig-unknown-" + uuid.uuid4().hex,
                              "deliberately-invalid", "app-prod",
                              pika.exceptions.ProbableAuthenticationError,
                              "unknown user")
            denied_connection("app", app_password, other_vhost,
                              pika.exceptions.ProbableAccessDeniedError,
                              "app ungranted vhost")
        finally:
            if app.is_open:
                app.channel().queue_delete(queue=name)
    finally:
        if app.is_open:
            app.channel().exchange_delete(exchange=name)

if findings:
    raise SystemExit("unexpectedly allowed: " + ", ".join(findings))
print("Expected results observed by this run; retain the matching broker logs.")
PY
        ;;
      esac
    ;;
  esac
)
```

Require the positive message round trip and observer authentication, then resource-specific `403 ACCESS_REFUSED` responses. Unknown-user and ungranted-vhost connection errors must have matching broker-log reasons; Pika's `Probable*` exception names are not proof by themselves. Unexpected exceptions are inconclusive, not authorization successes.

For the exposed comparison, use an isolated fixture with unrestricted application permissions in `app-prod` and the second existing vhost, and an observer with excessive resource grants. The same script should report unexpected allows for those operations. An unknown user should still be refused when authentication is working in either state. The fixed deployment must retain the positive operations while removing those unexpected allows. Reconnect between states.

**7. Definitions provisioning and export - REASONED: no blank broker, `rabbitmqadmin`, or exported definitions file is available.** Boot an isolated blank node using the approved file and boot settings from section 1, then run:

```bash
sudo rabbitmqctl list_users
sudo rabbitmqctl list_permissions -p 'app-prod'

python3 - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("definitions.redacted.json").read_text())
if not isinstance(data, dict):
    raise SystemExit("not a definitions object")
for field in ("users", "permissions", "topic_permissions",
              "parameters", "global_parameters"):
    if data.get(field):
        raise SystemExit("review required: non-empty " + field)
print("Selected sensitive sections are absent or empty; review all other content.")
PY
```

Compare users and grants with the approved list, including absence of `guest`. For the exposed comparison, use a separately reviewed test fixture containing an unwanted test account or grant and confirm that the inventory detects it. Then repeat on another blank node with the approved file; importing over the first node is not reconciliation.

Run section 1's reduced export and compare it with a private untransformed export from the same test broker containing known test users, vhost grants, topic permissions, and runtime parameters. The selected sections must be removed or empty in the reduced JSON. The local JSON check is deliberately conservative: any retained topic permissions or global parameters also require review. Review all remaining fields for secrets; empty selected sections do not establish that the whole document is safe to share. See [definitions import and export](https://www.rabbitmq.com/docs/definitions) and [exported definition contents](https://www.rabbitmq.com/docs/http-api-reference#get-apidefinitions).

**8. Inter-node and CLI distribution TLS - REASONED: no Erlang runtime, RabbitMQ broker, or multi-node cluster is available.** On an authorized test cluster with the section 6 configuration, from an authorized CLI host holding the matching cookie and substituting the deployed long node name for `rabbit@node1.internal`:

```bash
sudo rabbitmq-diagnostics --longnames -n rabbit@node1.internal ping
sudo rabbitmqctl --longnames -n rabbit@node1.internal cluster_status
```

With plaintext distribution a plaintext CLI authenticates; with TLS required, a plaintext CLI connection fails on the transport, while a CLI given the matching `RABBITMQ_CTL_ERL_ARGS` succeeds, and a CLI presenting a missing or untrusted client certificate is rejected. Two configured nodes must form a cluster over the selected TLS transport, and a plaintext node must not join. Correlate a failure with the TLS logs; a wrong cookie, bad DNS, or a stopped node is inconclusive, and `ping` and `cluster_status` alone do not prove every peer link is encrypted. See the [inter-node TLS guide](https://www.rabbitmq.com/docs/clustering-ssl).

**9. Topic-exchange routing-key authorization - REASONED: no RabbitMQ broker or AMQP client is available.** On an authorized broker with an administrator-provisioned `app.shared.topic` exchange, hold the section 1 resource permissions constant and vary only whether the section 7 topic permission exists:

```bash
sudo rabbitmqctl list_topic_permissions -p 'app-prod'
```

As the `app` user with publisher confirms, publish to `tenant1.created` and to `tenant2.created`, and bind a queue with each routing key, then repeat with `#` and `tenant1.#`. With no topic permission every publish and binding succeeds; with the section 7 permission `tenant1.created` succeeds while `tenant2.created`, `#`, and `tenant1.#` are refused with a broker-attributed `ACCESS_REFUSED`. Require that broker refusal rather than a client-side timeout; the listing shows the stored policy, not enforcement. Also test the exchange-to-exchange bypass across both grants. Under the baseline grant, where the `app` user can declare exchanges, it declares its own exchange, binds it to `app.shared.topic` with `tenant2.created`, and publishes through it; the message reaches the shared exchange, confirming that topic authorization alone is insufficient. Under the hardened grant, the configure denial makes the declaration fail before it is attempted and the scoped read and write grants leave no existing exchange the application may bind, so the route does not exist. See the [topic authorization reference](https://www.rabbitmq.com/docs/access-control#topic-authorisation).

Local authoring checks, completed without a broker:

| Check | Observed result |
|---|---|
| Bash parsing and ShellCheck | All runnable Bash blocks passed `bash -n` and ShellCheck 0.11.0; an intentional SC2086 canary confirmed that lint diagnostics were active. |
| Placeholder guards | 32 cases stopped locally under `bash -u`: unreplaced values, each empty value, embedded `REPLACE_WITH_*`, marker-only assignment, and omitted assignment with inherited non-marker arguments. |
| TOML | The example parsed with Python `tomllib`. |
| Embedded Python | Both programs passed Python syntax parsing. |
| RabbitMQ configuration | Key/value structure checked locally and settings traced to current vendor docs; native configuration/schema parsing remains unconfirmed because RabbitMQ and Erlang are absent. |

No broker, container, or whole-corpus gate suite was run. Local syntax checks do not demonstrate service behaviour.

| ID | Outstanding demonstration | Status |
|---|---|---|
| RABBITMQ-LIVE-1 | Demonstrate checks 1-9 against isolated exposed and fixed states: scoped grants and vhost refusal; monitoring versus administration and message operations; listener/epmd bindings, cookie permissions, external denial and allowed-peer controls including 15671 and removed 5672; management authenticated/anonymous responses; mutual TLS and AMQP user authentication; approved blank-node imports and reduced exports; plaintext versus TLS-required inter-node and CLI distribution, with rejection of a missing or untrusted client certificate; and topic-exchange routing-key authorization, with a broker ACCESS_REFUSED for an out-of-pattern publish or binding. Include native RabbitMQ configuration parsing/startup and retain commands, versions, outputs, and matching broker logs. | OPEN: missing RabbitMQ/Erlang, rabbitmqadmin, Pika, container runtime, test certificates, and peer infrastructure in the authoring environment. |

## 6. Encrypt inter-node and CLI distribution traffic with TLS

Section 4 binds the Erlang distribution port privately but leaves that traffic in plaintext. Distribution carries clustering messages and the full authority of `rabbitmqctl` and `rabbitmq-diagnostics`, so encrypt it with mutually authenticated TLS across every node and CLI host. This is an Erlang runtime mechanism, not a `rabbitmq.conf` setting: it is selected through `rabbitmq-env.conf` and a separate Erlang-term options file, and requires at least Erlang/OTP 27 for RabbitMQ 4.3 (this example targets OTP 27). See the [inter-node TLS guide](https://www.rabbitmq.com/docs/clustering-ssl) and the [OTP distribution-over-TLS reference](https://www.erlang.org/docs/27/apps/ssl/ssl_distribution.html).

In `/etc/rabbitmq/rabbitmq-env.conf`, select the TLS distribution module for both the server and the CLI tools, pointing each at the options file:

```bash
# shellcheck disable=SC2034  # rabbitmq-env.conf is sourced by RabbitMQ; these variables are read externally
ERL_SSL_PATH="REPLACE_WITH_INSTALLED_SSL_EBIN_DIRECTORY"
SERVER_ADDITIONAL_ERL_ARGS="-pa $ERL_SSL_PATH -proto_dist inet_tls -ssl_dist_optfile /etc/rabbitmq/inter_node_tls.config"
RABBITMQ_CTL_ERL_ARGS="-pa $ERL_SSL_PATH -proto_dist inet_tls -ssl_dist_optfile /etc/rabbitmq/inter_node_tls.config"
```

Determine the installed Erlang `ssl` application `ebin` directory on the host rather than copying a version-specific example. `SERVER_ADDITIONAL_ERL_ARGS` configures the broker's distribution; `RABBITMQ_CTL_ERL_ARGS` gives `rabbitmqctl` and `rabbitmq-diagnostics` the matching configuration so CLI connections are not refused. In a systemd or container launch environment the server variable's prefixed form is `RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS`. See the [pinned launch-variable handling](https://raw.githubusercontent.com/rabbitmq/rabbitmq-server/v4.3.6/deps/rabbit/scripts/rabbitmq-env).

In `/etc/rabbitmq/inter_node_tls.config`, require and verify peer certificates in both directions, because a node both accepts and initiates distribution connections:

```erlang
[
  {server, [
    {cacertfile, "/etc/rabbitmq/distribution/ca.pem"},
    {certfile, "/etc/rabbitmq/distribution/server.pem"},
    {keyfile, "/etc/rabbitmq/distribution/server.key"},
    {verify, verify_peer},
    {fail_if_no_peer_cert, true}
  ]},
  {client, [
    {cacertfile, "/etc/rabbitmq/distribution/ca.pem"},
    {certfile, "/etc/rabbitmq/distribution/client.pem"},
    {keyfile, "/etc/rabbitmq/distribution/client.key"},
    {verify, verify_peer}
  ]}
].
```

Provision credentials readable by the effective process identity on every node and CLI host. Peer verification checks the certificate against the hostname portion of the target Erlang node name (the part after the `@`), so issue each distribution certificate with a subject or SAN DNS identity matching that hostname rather than assuming the AMQP hostname certificate satisfies it. This outbound hostname verification is distinct from the inbound client-certificate trust that `verify_peer` and `fail_if_no_peer_cert` enforce; never disable either to resolve a mismatch. Plan a coordinated switch: distribution endpoints with mismatched transports cannot communicate, so a plaintext node and a TLS node will not form a cluster during a rolling change. TLS does not remove the Erlang cookie, epmd, or firewall requirements from section 4. See the [OTP distribution semantics](https://www.erlang.org/docs/27/apps/ssl/ssl_distribution.html) and the [OTP 27 distribution TLS implementation](https://raw.githubusercontent.com/erlang/otp/OTP-27.0/lib/ssl/src/inet_tls_dist.erl).

## 7. Restrict routing keys on shared topic exchanges

Section 1 bounds which exchanges and queues a user may configure, write, and read, but on a shared topic exchange those permissions do not restrict which routing keys a user may publish or bind. Topic authorization adds that layer. It is off until configured: with no topic permission set, RabbitMQ authorizes every topic operation, subject only to the section 1 resource permissions. Topic authorization has been available since [RabbitMQ 3.7](https://github.com/rabbitmq/rabbitmq-server/releases/tag/v3.7.0). See the [topic authorization documentation](https://www.rabbitmq.com/docs/access-control#topic-authorisation).

Topic permissions are broker records managed with `rabbitmqctl`, not entries in `rabbitmq.conf` or `advanced.config`. For an administrator-provisioned topic exchange `app.shared.topic` where the `app` user should publish and bind only its own tenant's routing keys, grant the scoped topic permission. The argument order is the user, then the exchange, then the write and read patterns:

```bash
sudo rabbitmqctl set_topic_permissions -p 'app-prod' 'app' \
  'app.shared.topic' \
  '^tenant1[.][a-z0-9_-]+$' \
  '^tenant1[.][a-z0-9_-]+$'
```

The write pattern gates publishing and the read pattern gates the routing keys a binding may use; both are regular expressions, not AMQP topic wildcards, so this example admits exact `tenant1.<name>` keys and excludes `#` and `*` subscriptions. Consumers still read from their queues under ordinary queue permissions, so topic authorization does not filter messages already sitting in an accessible queue, nor does it remove existing broad bindings: audit current bindings and queue grants, and reconnect clients after changing them. Topic authorization checks routing keys only on a direct publish to the topic exchange; if the section 1 resource grant lets the application declare its own exchanges, it can bind one to the shared exchange and route a disallowed key through it without the topic write check, because a resource-name grant does not distinguish an exchange from a queue, so for strong tenant isolation the administrator must own every route into the shared exchange: deny the application configure permission so it cannot declare a relay exchange, keep its read and write grants scoped to its own resources so it cannot bind an exchange it does not own into the shared exchange, and provision its queues and topology administratively. Clearing a topic permission returns that exchange to the unrestricted default; it is not a deny rule. Other authorization backends enforce their own topic rules. See the [topic authorization reference](https://www.rabbitmq.com/docs/access-control#topic-authorisation) and the [rabbitmqctl command reference](https://www.rabbitmq.com/docs/man/rabbitmqctl.8).

## Sources (checked September 2026)

- RabbitMQ access control, guest restrictions, interactive user creation, and resource permissions: https://www.rabbitmq.com/docs/access-control
- RabbitMQ virtual hosts and logical isolation: https://www.rabbitmq.com/docs/vhosts
- RabbitMQ CLI user, vhost, permission, and tag commands: https://www.rabbitmq.com/docs/man/rabbitmqctl.8
- RabbitMQ inter-node TLS (distribution over TLS): https://www.rabbitmq.com/docs/clustering-ssl
- Erlang/OTP 27 distribution over TLS: https://www.erlang.org/docs/27/apps/ssl/ssl_distribution.html
- OTP 27 distribution TLS implementation (hostname verification): https://raw.githubusercontent.com/erlang/otp/OTP-27.0/lib/ssl/src/inet_tls_dist.erl
- RabbitMQ v4.3.6 launch-variable handling (rabbitmq-env): https://raw.githubusercontent.com/rabbitmq/rabbitmq-server/v4.3.6/deps/rabbit/scripts/rabbitmq-env
- RabbitMQ 3.7.0 release notes (topic authorization introduction): https://github.com/rabbitmq/rabbitmq-server/releases/tag/v3.7.0
- RabbitMQ management listeners, HTTPS, and roles: https://www.rabbitmq.com/docs/management
- RabbitMQ configuration files and restart requirements: https://www.rabbitmq.com/docs/configure
- RabbitMQ plugin activation: https://www.rabbitmq.com/docs/plugins
- RabbitMQ plugin enable command: https://www.rabbitmq.com/docs/man/rabbitmq-plugins.8
- RabbitMQ HTTP API authentication and endpoints: https://www.rabbitmq.com/docs/http-api-reference
- RabbitMQ TLS, peer verification, certificate usage, and verification depth: https://www.rabbitmq.com/docs/ssl
- RabbitMQ networking, epmd lifecycle, private bindings, and distribution ports: https://www.rabbitmq.com/docs/networking
- RabbitMQ diagnostics, remote node selection, and authenticated ping: https://www.rabbitmq.com/docs/man/rabbitmq-diagnostics.8
- RabbitMQ CLI authentication and Erlang cookie handling: https://www.rabbitmq.com/docs/cli
- RabbitMQ definitions imports, sensitive exports, and export transformations: https://www.rabbitmq.com/docs/definitions
- RabbitMQ administration CLI v2 configuration and TLS flags: https://www.rabbitmq.com/docs/management-cli
- RabbitMQ queues, durability, and exclusive queue behaviour: https://www.rabbitmq.com/docs/queues
- RabbitMQ channel exceptions and access-refused errors: https://www.rabbitmq.com/docs/channels
- Pika TLS context and client certificate example: https://pika.readthedocs.io/en/stable/examples/tls_server_authentication.html
- Pika connection parameters: https://pika.readthedocs.io/en/stable/modules/parameters.html
- Pika blocking connection and channel methods: https://pika.readthedocs.io/en/stable/modules/adapters/blocking.html
- Pika authentication and authorization exceptions: https://pika.readthedocs.io/en/stable/modules/exceptions.html
- curl password prompts, TLS validation, and diagnostic flags: https://curl.se/docs/manpage.html
