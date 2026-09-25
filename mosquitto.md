# Mosquitto (MQTT): no anonymous clients, TLS listener

MQTT brokers back IoT and agent projects, and open brokers leak live telemetry and accept injected commands. Mosquitto's defaults are sane on version 2.0 and later (with a listener defined, anonymous access is off; without any listener it binds the loopback interface only); the job is to keep them sane while adding real listeners.

The no-listener loopback mode allows anonymous clients by default; it is not authenticated. Defining an explicit listener in 2.0 changes the default to rejecting clients unless authentication is configured. See [migrating to 2.0](https://mosquitto.org/documentation/migrating-to-2-0/).

The official Docker images do not all keep those defaults. The `latest`, `2`, `alpine`, `2.1-alpine` and `2.1.2-alpine` tags (Mosquitto 2.1.2 at the pinned library commit) ship their own `/mosquitto/config/mosquitto.conf`: `listener 1883` with `allow_anonymous true`, and `listener 9883` with `protocol http_api`, which serves the web dashboard and a read-only JSON API (`/api/v1/systree`, `/api/v1/listeners` and `/api/v1/version`). Neither listener names an address, so each binds the IPv4 wildcard, and the IPv6 one where the container has IPv6, and as shipped, with no password file, authentication plugin or ACL, both serve clients that give no credentials; publishing 9883 therefore exposes broker telemetry without a login. The `1.6-openssl` and `1.6.15-openssl` tags ship upstream's configuration, every line commented, so 1.6's defaults apply: a listener on 1883 with no address, on the IPv4 wildcard and the IPv6 one where available, that allows anonymous clients. The 2.0 tags (`2.0`, `2.0.22`, `2.0-openssl`, `2.0.22-openssl`, `2-openssl` and `openssl`; Mosquitto 2.0.22) ship upstream's 2.0.22 configuration, also every line commented, and keep 2.0's loopback-only default. To use one of the 2.1 or 1.6 images, mount your own `/mosquitto/config/mosquitto.conf` (or give the container a whole `mosquitto -c <file>` command naming another) that sets `allow_anonymous false` and a password file and drops the 9883 listener or binds it to `127.0.0.1`, and publish 1883 only to host loopback or a private network.

The file-based examples below target Mosquitto 2.0.22 and remain available, but deprecated, in 2.1. At the time of writing, `password_file`, `acl_file`, and `per_listener_settings` are deprecated in 2.1, with removal announced for 3.0. Plan migration to the password-file and ACL-file plugins; section 5 identifies the listener-policy replacements. See the [2.1 release notes](https://mosquitto.org/blog/2026/01/version-2-1-0-released/).

## 1. Credentials per device

Use the `mosquitto_passwd` shipped with your broker version. These commands prompt for passwords; do not use its batch option to put passwords in command arguments. Run the first command only when creating the password file: `-c` overwrites an existing file.

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd device-01     # -c only the first time
sudo mosquitto_passwd /etc/mosquitto/passwd device-02
```

`/etc/mosquitto/conf.d/secure.conf`:

```
per_listener_settings false
allow_anonymous false
password_file /etc/mosquitto/passwd
```

One credential per device, so a leaked unit can be revoked alone; add an `acl_file` to limit each identity to its own topics.

`per_listener_settings false` is valid when all listeners deliberately share authentication and ACL policy. It is deprecated in 2.1 along with `true`; changing the boolean is not the migration. For separate policies on 2.0, use the complete alternative in section 5.

To remove a compromised device, substitute the password-file path and its MQTT username inside the quotes, then paste the whole block:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PASSWORD_FILE' 'REPLACE_WITH_REVOKED_USERNAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not changing anything"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "provide exactly 2 values; not changing anything"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the password-file path"; exit 1 ;;
  esac
  case "$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the revoked username"; exit 1 ;;
    *) sudo mosquitto_passwd -D "$1" "$2" ;;
  esac
)
```

`mosquitto_passwd -D` edits the file; it does not terminate existing connections or update the running broker's loaded credentials. Reload the broker with SIGHUP through your deployment's service-management procedure so new authentication uses the changed file. Incident response also needs connection termination, or a controlled broker restart, and confirmation that the revoked identity cannot reconnect. See [password-file authentication and reload](https://mosquitto.org/documentation/authentication-methods/) and [mosquitto_passwd](https://mosquitto.org/man/mosquitto_passwd-1.html).

Do not assume uniform connection handling on reload: the `password_file` manual says connected clients are unaffected, while the [2.0.22 implementation](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/security_default.c) rechecks connected credentials and disconnects failures. File deletion alone is not connection termination; confirm termination on the deployed version and authentication backend.

## 2. TLS listener

```
listener 8883
cafile   /etc/mosquitto/tls/ca.pem
certfile /etc/mosquitto/tls/server.pem
keyfile  /etc/mosquitto/tls/server.key
# mutual TLS: clients must present certificates
# require_certificate true
```

Port 8883 is the conventional MQTT-over-TLS port. Certificates per [self-signed.md](self-signed.md) (an internal CA suits device fleets) or [free-certificates.md](free-certificates.md). `require_certificate true` makes a client certificate a possession factor for the connecting device, stronger than a password alone but not MFA for a person ([mfa.md](mfa.md)). Remove or firewall any plaintext `listener 1883` that is not strictly local. These snippets take effect only if the running broker loads `/etc/mosquitto/conf.d/` (confirm `include_dir` in the active config); a `listener` change is not applied on a reload signal, so restart the broker and check its startup log after editing.

## 3. Authorize topics, not just connections

Password authentication alone does not restrict topics: without ACLs or another authorization mechanism, authenticated clients can read and write every application topic. Add this to the shared-policy configuration in section 1:

```
acl_file /etc/mosquitto/acl
```

A complete `/etc/mosquitto/acl` for two devices and a separate command controller:

```
# Rules before the first user apply only to anonymous clients.
topic deny $SYS/#

user device-01
topic deny $SYS/#
topic read fleet/device-01/telemetry/#
topic write fleet/device-01/telemetry/#
topic read fleet/device-01/commands/#

user device-02
topic deny $SYS/#
topic read fleet/device-02/telemetry/#
topic write fleet/device-02/telemetry/#
topic read fleet/device-02/commands/#

user controller
topic deny $SYS/#
topic write fleet/device-01/commands/#
topic write fleet/device-02/commands/#
```

Create the controller's separate credential at the password prompt:

```bash
sudo mosquitto_passwd /etc/mosquitto/passwd controller
```

Unlisted access is denied. `user` names the MQTT username, not the client id. A `topic` rule before any `user` applies to anonymous clients, not every user; that is why the explicit `$SYS` denial is repeated under each identity. Reload after changing the password or ACL file. See the [ACL-file syntax](https://mosquitto.org/documentation/plugins/acl-file/) and [authentication reload instructions](https://mosquitto.org/documentation/authentication-methods/).

For a uniform fleet, replace the device-specific telemetry and command-read grants with these patterns, retaining the controller's explicit grants and the `$SYS` deny entries:

```
pattern read fleet/%u/telemetry/#
pattern write fleet/%u/telemetry/#
pattern read fleet/%u/commands/#
```

Patterns apply to all users, regardless of preceding `user` lines. `%u` substitutes the username; `%c` substitutes the client id. Each substitution must occupy a whole topic level: `fleet/%u/telemetry/#` is valid; embedding `%u` inside a level is not. Prefer authenticated `%u` because a client ordinarily chooses its own client id. Provision usernames as single topic levels. See [pattern ACLs](https://mosquitto.org/documentation/plugins/acl-file/).

Keep `$SYS`, the broker's telemetry hierarchy, ungranted to devices. `topic deny $SYS/#` makes that decision explicit for each listed user; it is not a global denial merely because it appears at the top of the file. `deny` was added in 2.0. Subscribing to `#` does not include `$SYS`; testing telemetry isolation requires an explicit `$SYS/#` subscription. See the [2.0 release notes](https://mosquitto.org/blog/2020/12/version-2-0-0-released/) and [broker status and wildcard subscriptions](https://mosquitto.org/man/mosquitto-8.html).

File ACLs filter message access, not SUBSCRIBE requests. An accepted `#` subscription is not by itself an ACL bypass. Test actual delivery and rejected writes with matched authorized delivery, as in Verify. This distinction is explicit in the [2.0.22 built-in ACL implementation](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/security_default.c) and [2.1.2 ACL-file plugin](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/plugins/acl-file/acl_check.c).

## 4. Bound resource use

Authentication does not stop a compromised device exhausting the broker. These defaults were checked against the versioned configuration and source at the time of writing:

| Option | Scope | Default |
| --- | --- | --- |
| `max_connections` | Per listener | `-1`, unlimited by this setting |
| `max_packet_size` | Global; incoming MQTT packet size | Unset in 2.0.22, with no configured cap; 2,000,000 bytes in 2.1 |
| `message_size_limit` | Global; PUBLISH payload size | `0`, no configured payload limit |
| `max_inflight_messages` | Global setting, enforced per client for outgoing QoS 1/2 messages | `20` |
| `max_queued_messages` | Global setting, enforced per client above inflight messages | `1000` in 2.x; `100` before 2.0 |
| `max_queued_bytes` | Global setting, enforced per client for queued outgoing messages | `0`, unlimited by this setting |
| `max_keepalive` | Global; client keepalive ceiling in seconds | `0` in 2.0.22 and 2.1.2, permitting unlimited keepalive |

Sources: [2.0.22 configuration](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/mosquitto.conf), [2.0.22 initialized defaults](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/conf.c), [2.1.2 initialized defaults](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/conf.c), and [the 2.0 queue-default change](https://mosquitto.org/blog/2020/12/version-2-0-0-released/). The 2.0.22 sample configuration's `max_keepalive 65535` commentary is stale; the implementation initializes it to `0`. Do not copy the sample's commented `max_packet_size 0` as an explicit setting: the parser requires a configured value of at least 20.

Illustrative global values:

```
max_packet_size 65536
message_size_limit 32768
max_inflight_messages 10
max_queued_messages 100
max_queued_bytes 1048576
max_keepalive 60
```

Within each explicit listener's configuration, choose a connection limit, for example:

```
max_connections 200
```

These are values to size against real traffic, client counts, reconnect behaviour, and available memory, not universal safe limits. Packet budgets need room for topic names and protocol overhead as well as payloads.

On 2.0.22 TCP listeners, `max_packet_size` rejects oversized packets before incoming-body allocation in the [packet reader](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/lib/packet_mosq.c). The [2.0.22 WebSockets receive callback](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/websockets.c) instead allocates the declared MQTT body without checking this limit before dispatch. The [2.1.2 libwebsockets callback](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/websockets.c) retains this allocation gap; do not generalize across WebSockets implementations. TLS termination does not fix it. Disable affected WebSockets listeners unless an independent boundary enforces the MQTT declared packet length before forwarding it, or use an implementation whose allocation bound has been demonstrated.

`message_size_limit` rejects an oversized PUBLISH without forwarding it, while completing the QoS 1/2 acknowledgement flow; it is not a packet-allocation defence. The [PUBLISH handler](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/handle_publish.c) checks the payload after packet reception.

Queue limits can cause message loss. When both queue limits are set, the first reached limits further queuing. Inflight limits bound concurrent outstanding delivery, not messages per second. A positive `max_keepalive` supplies a server override to MQTT 5 clients requesting an excessive interval; MQTT 3.1.1 clients requesting an incompatible interval are refused with identifier-rejected. Keepalive does not disconnect a client that keeps sending traffic. See the [resource-limit reference](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/man/mosquitto.conf.5.xml).

Mosquitto 2.1 adds these optional global controls; do not put them in a 2.0 configuration:

```
global_max_connections 500
global_max_clients 1000
```

Both default to `-1`. The first bounds connected clients across listeners; the second also counts disconnected persistent sessions. A connection cap alone does not bound that session population. See [global connection and session limits](https://mosquitto.org/man/mosquitto-conf-5.html).

On 2.0, repeatedly connecting with different IDs and leaving persistent sessions can grow broker state despite connection and per-client queue limits. Restrict the allowed identities and client IDs. Choose a global expiration policy, for example `persistent_client_expiration 14d`, to remove sessions that remain disconnected beyond that interval. Expiration is not a hard population cap. See the [2.0.22 expiration reference](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/man/mosquitto.conf.5.xml) and [expiry implementation](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/session_expiry.c).

## 5. Scope every listener, including WebSockets

An explicit `listener 1883` without a bind address listens on all interfaces. The no-listener loopback default does not carry over. Omit plaintext MQTT unless needed locally; if needed, use `listener 1883 127.0.0.1`. `bind_address` is deprecated and affects only the implicit default listener. See [2.0 listener changes](https://mosquitto.org/documentation/migrating-to-2-0/) and the [listener reference](https://mosquitto.org/man/mosquitto-conf-5.html).

For separate policies on 2.0, replace the shared authentication and listener snippets with this alternative; do not append it to them. Put `per_listener_settings true` before every listener and before other security settings, including settings in earlier included files. Create each referenced password and ACL file using the formats above.

```
per_listener_settings true

listener 8883
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
cafile   /etc/mosquitto/tls/ca.pem
certfile /etc/mosquitto/tls/server.pem
keyfile  /etc/mosquitto/tls/server.key
# require_certificate true
max_connections 200

# Optional local plaintext MQTT; omit this entire listener if unnecessary.
listener 1883 127.0.0.1
allow_anonymous false
password_file /etc/mosquitto/passwd-local
acl_file /etc/mosquitto/acl-local
max_connections 20

# Optional local WebSockets; requires a build with WebSockets support.
listener 9001 127.0.0.1
protocol websockets
allow_anonymous false
password_file /etc/mosquitto/passwd-ws
acl_file /etc/mosquitto/acl-ws
max_connections 20
```

Do not merely flip the original `false` to `true`: move each listener's `allow_anonymous`, `password_file`, and `acl_file` into its scope. Keep its TLS directives after that listener as well. The ordering requirement is enforced by the [2.0.22 configuration parser](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/conf.c).

The WebSockets example is local plaintext transport. A public WebSockets endpoint needs TLS plus its own authentication and ACL policy. For broker-terminated TLS, configure `cafile`, `certfile`, and `keyfile` on that WebSockets listener as in section 2, with certificates for its real endpoint. A TLS-terminating proxy must keep the backend private. Do not assume the MQTT listener's TLS configuration protects a separate WebSockets listener. See [protocol and WebSockets TLS settings](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/man/mosquitto.conf.5.xml).

On 2.0.22 WebSockets listeners, `max_connections` is ineffective: the [establishment callback](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/websockets.c) checks `client_count` without incrementing it. The example's `max_connections 20` therefore does not enforce a WebSockets connection cap. Require an independently enforced concurrent-connection limit with no backend bypass, or a version and WebSockets implementation whose cap is demonstrated. The [2.1.2 ChangeLog](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/ChangeLog.txt) records the libwebsockets fix for issue #3455 under 2.1.1; verify the deployed build across disconnect/reconnect cycles. TLS alone supplies neither this cap nor the packet-allocation protection missing in section 4.

Listeners are not separate topic or session namespaces. With per-listener settings, a disconnected persistent client retains the ACL policy of the listener it most recently used. See [per-listener policy behaviour](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/mosquitto.conf).

A valid password does not authorize a client ID: [2.0.22 duplicate-ID handling](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/handle_connect.c) can disconnect another device when a client authenticates with its own credentials but supplies that device's ID. For one connection per identity, set `use_username_as_clientid true` on every applicable listener. It replaces the supplied ID with the authenticated username; a second connection with that username displaces the first. Usernames must identify the same principal globally across all listeners and authentication stores, never different devices. Every other listener must also prevent unauthorized use of those IDs. If multiple connections per identity are needed, require authenticated client-ID authorization before session takeover, with a bounded set of IDs per identity; topic ACLs alone do not provide it. See the [2.0.22 mosquitto.conf(5) entry](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/man/mosquitto.conf.5.xml): this option is per listener and requires a restart, not SIGHUP.

In 2.1, replace `per_listener_settings` with explicit listener policy: `listener_allow_anonymous` controls anonymous access, and `plugin_load` plus `plugin_use` loads and attaches authentication/ACL plugins to selected listeners. Use the `mosquitto_password_file` and `mosquitto_acl_file` plugins for the corresponding file-based controls. Follow the vendor's [replacement procedure](https://mosquitto.org/documentation/listeners/per-listener-settings/); this is a configuration migration, not a boolean change.

## 6. Secure bridges when present

A bridge creates another route into and out of the topic tree. Configure TLS explicitly; putting `:8883` in `address` does not enable bridge TLS.

Store this connection stanza in a protected configuration file loaded by the broker:

```
connection site-01-upstream
address upstream.example.com:8883
bridge_cafile /etc/mosquitto/tls/upstream-ca.pem
bridge_insecure false
remote_username bridge-site-01
remote_password REPLACE_WITH_REMOTE_BRIDGE_PASSWORD
topic fleet/device-01/telemetry/# out 1
topic fleet/device-01/commands/# in 1
try_private true
restart_timeout 10 60
notifications false
# If the remote broker requires a client certificate:
# bridge_certfile /etc/mosquitto/tls/bridge-client.pem
# bridge_keyfile /etc/mosquitto/tls/bridge-client.key
```

`out` forwards local telemetry to the remote broker; `in` brings remote commands into the local broker. Avoid broad `topic # both` forwarding. Require a trusted upstream: locally configured bridge contexts bypass local ACL checks in [2.0.22](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/security_default.c) and [2.1.2](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/plugin_acl_check.c). Bridge topic declarations control routing and subscriptions, not a local ingress ACL; the [2.1.2 incoming remapper](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/bridge_topic.c) returns success for unmatched topics. Neither these declarations nor the remote account's ACL contains a malicious upstream. If upstream trust is insufficient, replace the direct bridge with an independently enforced boundary, such as an isolated gateway that republishes only allowed topics through an ordinary authenticated client subject to the local broker's ACL.

On the trusted remote broker, give this dedicated username only the matching permissions:

```
user bridge-site-01
topic deny $SYS/#
topic write fleet/device-01/telemetry/#
topic read fleet/device-01/commands/#
```

`bridge_insecure false` keeps hostname verification enabled. `try_private true` identifies a bridge to peers that support it, helping loop detection and retained-message handling; it is not authentication. `restart_timeout 10 60` uses reconnect backoff rather than an immediate retry loop. `notifications false` suppresses the bridge's default `$SYS` status publications, so this example needs no `$SYS` write grant. Monitor bridge health through protected logs.

The remote password is plaintext in the configuration file. Restrict that file and its backups as credentials; there is no universal credential-redaction switch to rely on. Add `bridge_certfile` and `bridge_keyfile` only when the remote requires a client certificate.

Syntax and behaviour: [bridge configuration and TLS options](https://mosquitto.org/man/mosquitto-conf-5.html) and the [2.0.22 bridge configuration reference](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/mosquitto.conf).

## 7. Protect the runtime account and files

Use a dedicated runtime account. For a deployment that intentionally enables built-in persistence:

```
user mosquitto
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
```

`persistence_location` only sets the path; persistence defaults to `false`. The example explicitly enables it. When started as root on POSIX systems, `user mosquitto` drops privileges; it does not change the account of an already unprivileged process. Ensure the account exists. See [`user`, persistence, and file logging](https://mosquitto.org/man/mosquitto-conf-5.html).

Protect persistence data, logs, password files, ACL files, TLS private keys, and bridge configuration containing `remote_password`. As deployment guidance, use 0700 private directories and 0600 sensitive files, owned by the account that must access them; these are filesystem modes, not Mosquitto directives. Account for parent-directory traversal and protect backups and log rotation output too. The broker needs to read credentials, ACLs, certificates, and keys, and write its persistence and log locations.

Mosquitto 2.0 drops privileges immediately after reading configuration, earlier than 1.x. Root-readable files alone are therefore insufficient: the required paths must be accessible to the runtime account after the drop. See [privilege-drop changes](https://mosquitto.org/documentation/migrating-to-2-0/).

## 8. Verify

This guide's service checks are **REASONED, not demonstrated**. The authoring environment has no Mosquitto broker or client binaries, container runtime, deployment credentials, or external test hosts. Filesystem and network restrictions prevent provisioning a live comparison here. Broker configuration acceptance and exposed/fixed behaviour remain open under `MOSQUITTO-LIVE-1`.

Local validation covered all seven fenced shell blocks with `bash -n`, ShellCheck 0.11.0, and the repository's strict guard-convention scanner. Guard-only tests rejected 90 invalid positional inputs; five substituted controls reached local markers. These checks exercised shell behaviour, not Mosquitto. No repository files were changed and the whole-corpus gate suite was not run.

Use Mosquitto 2.1 client tools for the commands below, including when testing a 2.0 broker. Their `-o` option selects an explicit configuration file and skips the default client configuration. On 2.0 clients, use protected default configuration files in isolated test accounts instead; `-o` is unavailable. See [client configuration files](https://mosquitto.org/man/mosquitto_sub-1.html).

Prepare an owner-readable file, mode 0600 inside a private directory, for each test identity. For example, `device-01.conf` contains:

```
-u device-01
-P REPLACE_WITH_DEVICE_PASSWORD
```

Prepare corresponding files for `device-02` and `controller`, with their distinct passwords. Create a separate empty `anonymous.conf`. Inspect these files: use only the intended authentication options, with no proxy, insecure TLS, extra subscriptions, fixed client id, or persistent-session options. If mutual TLS is required, add the valid client certificate and key paths to both the authenticated and anonymous test configurations; the latter then tests absence of MQTT username/password. Use a separate configuration without the client certificate for the missing-certificate check.

Paste whole blocks and substitute inside the single quotes. A literal apostrophe needs proper shell escaping. Keep credentials out of command arguments, shell history, recordings, and debug-log sharing. The `-P` line above belongs in the protected file, not the shell.

### Connection authentication and TLS

**REASONED:** No live TLS broker, device credentials, or client certificates are available here. Run both controls against the intended exposed endpoint. The authenticated control must produce successful CONNACK; the anonymous control must be refused at CONNECT. Anonymous CONNACK success is the exposed outcome even if no messages arrive. DNS, TCP, TLS, and local-file failures are inconclusive authentication results. The discriminators come from [authentication configuration](https://mosquitto.org/documentation/authentication-methods/) and [client CONNACK reporting](https://mosquitto.org/man/mosquitto_sub-1.html).

```bash
# These are MANUAL checks: read the -d CONNACK output, not the exit status. mosquitto_sub exits 27 on a
# -W timeout even after a successful connect, and nonzero on a refusal, so each is wrapped to capture its
# status without aborting under set -e. Keep the client config clean: a default mosquitto client config
# (e.g. ~/.config/mosquitto_sub) can carry credentials, a SOCKS proxy, or an --insecure setting, so run
# these where there is none, or inspect it first. If require_certificate true is set, TLS rejects before
# the password check, so add --cert 'client.pem' --key 'client.key' (your paths, inside the quotes) to BOTH controls below and test a
# missing-client-certificate connection separately. -x sets MQTT session expiry (NOT a TLS bypass) and
# --insecure disables hostname verification; use neither here.
# With 2.1 clients, --insecure disables all server-certificate verification.
# Positive control: a valid device connects. Expect "received CONNACK (0)" in the output; establish
# acceptance from that CONNACK separately. Exit 27 is only a timeout, even if messages arrived first.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_BROKER_PUBLIC_HOST' \
    'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_DEVICE_01_CONFIG' 'REPLACE_WITH_ANONYMOUS_CONFIG'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "provide exactly 4 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the broker host"; exit 1 ;;
  esac
  case "$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the CA path"; exit 1 ;;
  esac
  case "$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the device config path"; exit 1 ;;
  esac
  case "$4" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the anonymous config path"; exit 1 ;;
    *)
      if mosquitto_sub -o "$3" -d -W 2 -h "$1" -p 8883 --cafile "$2" -t 'test' -u device-01
      then echo "exit 0; confirm CONNACK (0) above"
      else echo "exit $?; confirm CONNACK separately; 27 means timeout"
      fi
      # Negative control: NO credentials must be refused AT CONNECT, not merely denied the subscription.
      # Expect "received CONNACK (5)" (MQTT 3.1.1 not authorized) or "(135)" (MQTT 5). An anonymous CONNECT
      # that succeeds (CONNACK (0)) and only fails the SUBSCRIBE (e.g. under an acl_file) means the broker
      # still accepts anonymous clients: that is a finding.
      if mosquitto_sub -o "$4" -d -W 2 -h "$1" -p 8883 --cafile "$2" -t 'test'
      then echo "exit 0; FINDING if anonymous CONNACK (0) appears"
      else echo "exit $? (expected: CONNACK 5/135 refusal - confirm above, NOT a SUBACK denial)"
      fi
      ;;
  esac
)
```

The SUBACK warning above concerns the distinction between authentication and authorization. With file ACLs specifically, expect the subscription itself to be accepted and unauthorized message access to be filtered, as section 3 explains. The `test` topic is deliberately ungranted; this first pair establishes CONNECT behaviour only.

Exit 27 is a timeout, including after received messages; it is never shorthand for accepted authentication. See the [client timeout implementation](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/client/sub_client.c). The [2.1 release notes](https://mosquitto.org/blog/2026/01/version-2-1-0-released/) also document the broader effect of `--insecure`.

**REASONED:** Where `require_certificate true` is enabled, repeat the authenticated request with the no-client-certificate configuration. The fixed outcome is TLS rejection before CONNACK, paired with successful connection using the trusted certificate. Acceptance without a certificate is the exposed outcome. This comparison is unavailable here because there is no broker or certificate fixture. See [`require_certificate`](https://mosquitto.org/man/mosquitto-conf-5.html).

### Listener exposure

**REASONED:** No deployed broker namespace or external probe host is available here. Run the inventory on the broker host and the network probe from another host. Check every actual public IPv4 and IPv6 address, including NAT paths.

```bash
ss -tlnp   # inventory the listeners (needs sudo for the process column); ss shows a local BIND, not a
           # firewall or external reachability. There must be no 1883 listener on ANY non-loopback
           # address - 0.0.0.0, ::, or a specific external IP, IPv4 or IPv6 - unless it is firewalled to
           # localhost. The plaintext 1883 listener is the main exposure (section 2), so also probe each
           # public address from ANOTHER host, using the corpus guard so an unsubstituted target cannot
           # masquerade as a pass:
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_BROKER_PUBLIC_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the broker's public host on the set -- line above; not probing" ;;
    *) nc -vz -w 5 "$1" 1883 || true ;;   # refused/timeout = TCP 1883 unreachable from here (the pass); a completed connect means TCP 1883 is reachable off-host. nc sends no MQTT, so this shows reachability, not the service or its encryption; the positive control against the intended endpoint must have succeeded first
  esac
)
```

A DNS failure, wrong destination, or local socket error is not a pass. Confirm the address belongs to this broker and inspect the actual diagnostic. The `|| true` preserves the manual workflow; its resulting shell status certifies nothing. Repeat for port 9001 if using the local-only WebSockets example. The fixed state has no externally reachable plaintext endpoint; a completed external connection is the exposure. See [listener binding behaviour](https://mosquitto.org/documentation/migrating-to-2-0/).

### Actual topic access

**REASONED:** No live broker, scoped identities, or disposable topic fixtures are available here. Use an isolated deployment with the section 3 ACL and the three test credentials. Keep real actuators and command consumers disconnected. Compare the same requests with password authentication alone and with the ACL applied; never remove production ACLs for this test.

With `use_username_as_clientid true`, a separate publisher using an observer's username disconnects that observer. For this policy, reproduce the table below using one long-lived client per identity that both subscribes and publishes, retaining the before-and-after delivery controls. This variant remains REASONED and open under `MOSQUITTO-LIVE-1`; the separate-client commands below cannot demonstrate it. See [session takeover](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/handle_connect.c).

Otherwise, run this observer block in separate terminals once with `device-01.conf` and once with `device-02.conf`. Where client-ID authorization is enforced, give each observer and publisher a distinct authorized ID in its protected test configuration, as an explicit exception to the preparation rule against fixed IDs. Wait for successful CONNACK and SUBACK in both observers before publishing. Keep both running throughout each comparison; repeat the window if either exits.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_BROKER_PUBLIC_HOST' \
    'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_OBSERVER_CONFIG'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "provide exactly 3 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the broker host"; exit 1 ;;
  esac
  case "$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the CA path"; exit 1 ;;
  esac
  case "$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the observer config path"; exit 1 ;;
    *)
      if mosquitto_sub -o "$3" -h "$1" -p 8883 --cafile "$2" \
        -d -v -q 1 -W 60 -t '#' -t "\$SYS/#"
      then echo "exit 0; inspect received topics and this run's markers"
      else echo "exit $?; inspect CONNACK and deliveries; timeout alone proves no ACL result"
      fi
      ;;
  esac
)
```

Run this publisher block for each row below, substituting the selected credential-file path, topic, and a distinct non-secret marker for this run. It does not retain messages.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_BROKER_PUBLIC_HOST' \
    'REPLACE_WITH_CA_FILE' 'REPLACE_WITH_PUBLISHER_CONFIG' \
    'REPLACE_WITH_TEST_TOPIC' 'REPLACE_WITH_NONSECRET_UNIQUE_MARKER'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 5 ] || { echo "provide exactly 5 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the broker host"; exit 1 ;;
  esac
  case "$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the CA path"; exit 1 ;;
  esac
  case "$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the publisher config path"; exit 1 ;;
  esac
  case "$4" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the test topic"; exit 1 ;;
  esac
  case "$5" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute the non-secret marker"; exit 1 ;;
    *)
      if mosquitto_pub -o "$3" -h "$1" -p 8883 --cafile "$2" \
        -d -V mqttv5 -q 1 -t "$4" -m "$5"
      then echo "publisher exited 0; check PUBACK reason and actual observer delivery"
      else echo "publisher exit $?; inspect the broker response, not just this status"
      fi
      ;;
  esac
)
```

| Publisher identity | Topic | Fixed outcome |
| --- | --- | --- |
| `device-01` | `fleet/device-01/telemetry/check` | Device-01 receives its marker; device-02 does not |
| `device-02` | `fleet/device-02/telemetry/check` | Device-02 receives its marker; device-01 does not |
| `controller` | `fleet/device-02/commands/check` | Device-02 receives the authorized command marker |
| `device-01` | `fleet/device-02/commands/check` | Write is denied; device-02 receives no injected marker |
| `controller` | `fleet/device-02/commands/check` | Device-02 receives a fresh authorized marker after the denied attempt |

Without ACLs, the authenticated observers can receive each other's telemetry and device-01 can inject the command. With the ACL, require both isolation and successful authorized deliveries. The controller's before-and-after messages distinguish write denial from a broken observer. MQTT 5 QoS 1 supplies a PUBACK reason for denied writes; actual delivery remains part of the decision. See the [ACL check](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/plugins/acl-file/acl_check.c), [PUBLISH denial handling](https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/handle_publish.c), and [publisher options](https://mosquitto.org/man/mosquitto_pub-1.html).

The explicit `$SYS/#` subscription should receive broker telemetry in the exposed comparison when telemetry publication is enabled, and none under either device's fixed ACL. Require that exposed positive control and the device's authorized live marker; an empty `$SYS` result alone proves nothing. See [broker status publication](https://mosquitto.org/man/mosquitto-8.html).

### Demonstration backlog

| Backlog ID | Status | Required demonstration |
| --- | --- | --- |
| MOSQUITTO-LIVE-1 | OPEN - REASONED; broker configuration acceptance and service behaviour not demonstrated | On pinned 2.0.22 and 2.1.2 deployments, load the applicable configurations and reproduce exposed/fixed authentication, TLS/client-certificate, listener, WebSockets, and actual-message ACL comparisons above. Confirm credential reload and termination of revoked connections. Exercise packet and payload limits separately on TCP and each deployed WebSockets implementation, including declared-length probes without the body; instrument allocation to distinguish rejection before allocation from rejection after receipt. Demonstrate the section 4 WebSockets gap and the chosen boundary or replacement implementation's rejection before oversized allocation, with an accepted packet below the limit. Exercise queue loss and inflight bounds with slow clients, keepalive negotiation/refusal, per-listener connection caps, and 2.1 global connection/session caps. For each listener cap N, hold N connections with distinct authorized identities/IDs and attempt N+1; demonstrate the 2.0.22 WebSockets failure without an independent cap and refusal with the chosen enforcement. Release a slot, confirm a replacement connects, refill to N, and repeat the excess attempt across multiple disconnect/reconnect cycles; distinguish cap refusal from authentication or transport failure. Test device-01 credentials with device-02's active ID: the exposed state disconnects device-02; the fixed state rejects or rewrites the claimant's ID and preserves device-02's connection and delivery. Repeat across listeners, and confirm the documented same-identity takeover when username binding is enabled. Run message ACL comparisons with one publishing/subscribing client per identity under that policy. On 2.0, demonstrate persistent-session growth with varying IDs, the chosen ID restriction, and expiration after the configured disconnected interval; do not treat expiration as a population cap. Where bridges exist, demonstrate trusted TLS and hostname rejection, optional client certificates, scoped inbound/outbound delivery, remote ACL denial, and reconnect backoff. Separately use a controlled upstream that sends outside the configured inbound topics despite its account ACL; demonstrate the direct bridge's missing ingress containment and, where required, denial at the independent boundary with matched allowed delivery. Confirm runtime ownership, readable security files, writable protected state/log paths, and persistence only when enabled. Record versions, WebSockets implementations, commands, diagnostics, matched positive controls, and cleanup without credentials. Configuration inspection alone does not close this row. |

## Sources (checked September 2026)

- Official eclipse-mosquitto Docker images: the tag-to-directory map (library file pinned commit 920b00976e6e8335bab0a3fd293b95b6b2404ce3), and at image source pinned commit 5b74cce8a4fe2a73b57df6c703bfde2cfd535d60 the 2.1-alpine build's 2.1.2 release download, configuration and dashboard install and `CMD`, an entrypoint that only sets data-directory ownership, its `mosquitto.conf` (`listener 1883`, `allow_anonymous true`, `listener 9883` with `protocol http_api`), the README's description of it, and the 2.0-openssl and 1.6-openssl builds installing upstream's `mosquitto.conf`: https://github.com/docker-library/official-images/blob/920b00976e6e8335bab0a3fd293b95b6b2404ce3/library/eclipse-mosquitto#L3-L13, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/Dockerfile#L30, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/Dockerfile#L77-L80, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/Dockerfile#L99-L101, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/mosquitto.conf, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/docker-entrypoint.sh, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.1-alpine/README.md#L27-L28, https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/2.0-openssl/Dockerfile#L69 and https://github.com/eclipse-mosquitto/mosquitto/blob/5b74cce8a4fe2a73b57df6c703bfde2cfd535d60/docker/1.6-openssl/Dockerfile#L66
- Mosquitto 2.1.2 listener with no address (a passive `getaddrinfo` over both families), the `http_api` endpoints and their access check, anonymous success with no authentication plugin, ACL success with no ACL plugin, and the manual's `http_api` entry (pinned tag v2.1.2): https://github.com/eclipse-mosquitto/mosquitto/blob/v2.1.2/src/net.c#L821-L828, https://github.com/eclipse-mosquitto/mosquitto/blob/v2.1.2/src/http_api.c#L336-L378, https://github.com/eclipse-mosquitto/mosquitto/blob/v2.1.2/src/plugin_basic_auth.c#L56-L113, https://github.com/eclipse-mosquitto/mosquitto/blob/v2.1.2/src/plugin_acl_check.c#L141-L201 and https://github.com/eclipse-mosquitto/mosquitto/blob/v2.1.2/man/mosquitto.conf.5.xml#L1663-L1671
- Mosquitto 1.6.15 default listener on 1883 with no address when no listener is configured, and `allow_anonymous` defaulting to true, with upstream's `mosquitto.conf` having no active line (pinned tags v1.6.15 and v2.0.22): https://github.com/eclipse-mosquitto/mosquitto/blob/v1.6.15/src/conf.c#L420-L468, https://github.com/eclipse-mosquitto/mosquitto/blob/v1.6.15/src/net.c#L605-L615, https://github.com/eclipse-mosquitto/mosquitto/blob/v1.6.15/man/mosquitto.conf.5.xml#L167-L185, https://github.com/eclipse-mosquitto/mosquitto/blob/v1.6.15/mosquitto.conf and https://github.com/eclipse-mosquitto/mosquitto/blob/v2.0.22/mosquitto.conf
- mosquitto.conf manual (allow_anonymous defaults, password_file, listener, certfile/keyfile/cafile, require_certificate): https://mosquitto.org/man/mosquitto-conf-5.html
- mosquitto_sub manual (`-d` debug/CONNACK, `-W` timeout, `-u`/`-P`, `--cafile`, `--cert`/`--key`, `-x` session expiry, `--insecure`): https://mosquitto.org/man/mosquitto_sub-1.html
- mosquitto_passwd manual (`-c` creates/overwrites the password file): https://mosquitto.org/man/mosquitto_passwd-1.html
- Migrating to 2.0 (anonymous loopback mode, explicit-listener exposure and authentication, early privilege drop): https://mosquitto.org/documentation/migrating-to-2-0/
- Authentication methods (password files and SIGHUP reload): https://mosquitto.org/documentation/authentication-methods/
- Mosquitto 2.0 release notes (`deny` ACLs and queue-default change): https://mosquitto.org/blog/2020/12/version-2-0-0-released/
- Mosquitto 2.1 release notes (deprecations, announced 3.0 removals, packet-size default, global limits, client TLS behaviour): https://mosquitto.org/blog/2026/01/version-2-1-0-released/
- Replacing per_listener_settings (listener_allow_anonymous, plugin_load, plugin_use, file plugins): https://mosquitto.org/documentation/listeners/per-listener-settings/
- ACL-file plugin (user/topic rules, deny, patterns, username and client-id substitutions): https://mosquitto.org/documentation/plugins/acl-file/
- Mosquitto broker manual ($SYS telemetry, wildcard exclusions, reload signals): https://mosquitto.org/man/mosquitto-8.html
- Mosquitto publisher manual (protected configuration files, QoS, protocol selection, message publishing): https://mosquitto.org/man/mosquitto_pub-1.html
- Mosquitto 2.0.22 sample configuration (listener connection defaults, per-listener policy, bridge options): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/mosquitto.conf
- Mosquitto 2.0.22 configuration implementation (actual resource defaults, numeric validation, per-listener ordering): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/conf.c
- Mosquitto 2.1.2 configuration implementation (actual packet, keepalive, queue, and global-limit defaults): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/src/conf.c
- Mosquitto 2.0.22 configuration manual source (resource-limit mechanisms, listener policy, WebSockets TLS): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/man/mosquitto.conf.5.xml
- Mosquitto 2.0.22 built-in security implementation (message ACL checks, accepted subscriptions, credential rechecks on reload): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/security_default.c
- Mosquitto 2.1.2 ACL-file plugin implementation (subscription acceptance and message-access filtering): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/plugins/acl-file/acl_check.c
- Mosquitto 2.0.22 packet reader (packet-size enforcement before incoming-body allocation): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/lib/packet_mosq.c
- Mosquitto 2.0.22 PUBLISH handler (payload-size checks, denied writes, QoS responses): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.0.22/src/handle_publish.c
- Mosquitto 2.1.2 subscriber implementation (timeout result independent of message receipt): https://raw.githubusercontent.com/eclipse-mosquitto/mosquitto/v2.1.2/client/sub_client.c
