# Redis: TLS and authentication

Redis trusts its network by design, so the network boundary and credentials are your job. An exposed unauthenticated Redis leaks its data, and historic attack tooling has also used the CONFIG command against open instances to write files and take over hosts. Applies to Redis 6.0 and later for TLS and ACLs; the server and client must be built with TLS support. Additional controls below carry their minimum versions. See the [Redis security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/) and [TLS documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/).

This guide targets upstream Redis 6.0 and later. The existing configuration references through 8.2.1 pin syntax and historical behaviour, not a deployment version. Sections 9-15 add deployment-exposure controls for replication, Sentinel, and Redis Cluster, reviewed against upstream Redis 8.10.1. Version-specific examples carry their own qualifications; the Redis 8.10 peer-name control does not belong in a generic Redis 6.0+ configuration. These HA findings establish no equivalent Valkey or Redis Enterprise behaviour; the Valkey compatibility note remains separate.

## 1. Keep it local unless remote access is deliberate

In `redis.conf`:

```
# Redis 6.2+: "-" makes an address optional if it is absent from local interfaces.
# An address already in use still fails startup.
# Redis 6.0: use "bind 127.0.0.1" instead.
# Keep comments on separate lines.
bind 127.0.0.1 -::1
protected-mode yes
```

`protected-mode` confines clients to the loopback interfaces and Unix sockets, but only while the default user still has its `nopass` flag and, on Redis 6.0/6.2, no explicit `bind` is configured. Redis 7.0 keeps the `nopass` condition and drops the `bind` condition. On Redis 6.0/6.2, setting any explicit `bind` disables this protected-mode restriction; a wildcard bind such as `bind 0.0.0.0` then permits remote passwordless access while the default user remains `on nopass`, whereas a loopback-only `bind 127.0.0.1` still confines access to the local host. Treat protected mode as a backstop for the unconfigured default; the bind address and credentials are the controls. The pinned [6.2 configuration](https://raw.githubusercontent.com/redis/redis/6.2.14/redis.conf) and [7.0 configuration](https://raw.githubusercontent.com/redis/redis/7.0.15/redis.conf) document the version difference.

The official Docker images change the protected-mode default. Their build, from redis/docker-library-redis, patches Redis so `protected-mode` defaults to `no`; this holds for every image on the repository's default branch at the pinned commit (6.2 through 7.4, Debian and Alpine) and for the 8.10.2 release tag, the only 8.x build checked. Their default command runs `redis-server` with no configuration file, so the compiled-in defaults apply; in the 7.4.8 and 8.10.2 builds those are `bind * -::*` (every IPv4 address, and every IPv6 address where the container has IPv6) and a `default` user that is `on`, `nopass` and `+@all`. A container from those images, started without a configuration file or arguments of its own, therefore accepts unauthenticated connections from any address that reaches it, with the `default` user's `+@all` permissions (commands that Redis disables by default, such as `DEBUG` and `MODULE` on 7.0 and later, stay disabled; see section 5). Start it with a configuration file carrying the credential settings in section 2 (a loopback `bind` inside the container would also block published traffic), and publish only to host loopback or a private network.

## 2. Require a credential

Minimum, using a single shared password sent by clients with `AUTH`:

```
requirepass REPLACE_WITH_LONG_RANDOM_PASSWORD
```

Better, per-service ACL users with least privilege, supported since Redis 6:

```
user app on >REPLACE_WITH_LONG_RANDOM_PASSWORD ~app:* +@read +@write -flushall -flushdb -swapdb
```

That grants the `app` user the read and write command categories, and `~app:*` restricts only the key arguments those commands take, to keys named `app:*`. It does not confine commands that take no key: `+@write` still includes `FLUSHALL` (clears every database), `FLUSHDB` (clears the current database), `SWAPDB` (swaps two databases), and, on Redis 7 and later, the FUNCTION write subcommands (`FUNCTION LOAD`, `FUNCTION DELETE`, `FUNCTION FLUSH`, `FUNCTION RESTORE`) that manage global libraries. `+@read` still includes keyspace-walking commands such as `KEYS`, `SCAN`, and `RANDOMKEY` that range outside `app:*`.

The `-flushall -flushdb -swapdb` above removes those three commands only, not every keyless write. For real least privilege, allowlist only the commands the app uses, for example `~app:* +get +set`, and expand that list deliberately. Apply that replacement with `reset`, as shown in section 3, rather than adding it to an existing broad policy. See the [ACL rules](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) and the command references in Sources.

Generate passwords per [authentication.md](authentication.md). The `default` user starts `on nopass ~* +@all` (Redis 6.2 adds `&*` for Pub/Sub channels), so with ACLs as your control you must secure it before any remote exposure: give it a strong password, or set `user default off resetpass` in `redis.conf` or the ACL file and apply it on a running server with `ACL SETUSER default off resetpass`. Do that only after every client authenticates as a named user and a separate named administrator has been tested. A connection already authenticated as `default` keeps working until it disconnects; section 3 covers revocation. See the [ACL authentication and user-state rules](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

MFA: Redis has no second-factor dialogue. For machine clients, `tls-auth-clients yes` (mutual TLS, below) adds a possession factor, a certificate, alongside the password; that is stronger than a password alone but it is not MFA for a person. Human paths to the host go behind MFA per [mfa.md](mfa.md).

On Redis 8.6+, the certificate-plus-password description assumes certificate-to-user automatic authentication is disabled. Redis 8.6 introduced `tls-auth-clients-user`, which defaults to `off`; enabling it can authenticate a connection without a separate password exchange. On Redis 8.6+, keep this setting `off` for the guide's certificate-plus-password and unauthenticated-certificate `NOAUTH` checks. Earlier releases do not support this directive; omit it entirely, because an unknown configuration directive prevents startup. See the [8.6 release notes](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.6-release-notes/), [pinned certificate authentication configuration](https://raw.githubusercontent.com/redis/redis/8.6.0/redis.conf), and [registered default](https://raw.githubusercontent.com/redis/redis/8.6.0/src/config.c).

## 3. Make ACL restrictions durable and replace old permissions explicitly

`ACL SETUSER` modifies an existing user incrementally. A narrower-looking command does not remove earlier passwords, key patterns, or command grants. Start a replacement policy with `reset`; on Redis 7+, that also clears selectors, which otherwise provide alternative grants. Rules are processed from left to right. See [ACL SETUSER](https://redis.io/docs/latest/commands/acl-setuser/).

Use a separate administrative account, called `ops` here, with the permissions needed for the management commands below. Test its login before changing application users or disabling `default`. Connect over TLS using section 7 with `--user ops`.

The following is input at the Redis prompt, not a shell command. Replace the password placeholder there. Do not put the password or the complete `ACL SETUSER` command in the shell invocation's arguments.

```
ACL SETUSER app reset on >REPLACE_WITH_LONG_RANDOM_PASSWORD resetchannels ~app:* +get +set
```

This example requires Redis 6.2+ because of `resetchannels`. For Redis 6.0, omit that token; channel ACLs are unavailable there. Explicitly resetting channels avoids inheriting the Redis 6.2 `allchannels` default. Redis 7.0 changed that default to `resetchannels`. See the [pinned ACL configuration](https://raw.githubusercontent.com/redis/redis/8.2.1/redis.conf).

Keep CLI history disabled as shown in section 7. Passwords entered in ACL commands can still appear on the terminal or in session recordings. Protect configuration and ACL files, including their password hashes.

Choose one persistence method:

- **Users in `redis.conf`:** after checking the runtime policy, run `CONFIG REWRITE` from the administrative Redis prompt. Redis must have been started with a configuration file and must be able to write it. Require an `OK` response. This rewrites other runtime configuration too, so review the resulting file. See [CONFIG REWRITE](https://redis.io/docs/latest/commands/config-rewrite/).
- **Users in an external ACL file:** configure the following in `redis.conf`, and move all `user` definitions, including the administrator and secured `default` user, into that file. Redis refuses to start if inline `user` definitions and `aclfile` are both configured.

```
aclfile /etc/redis/users.acl
```

With `aclfile` configured, run `ACL SAVE` to persist runtime ACL changes. If instead you edit the ACL file, run `ACL LOAD` to replace the runtime rules from it. Require `OK`; an invalid file leaves the previous runtime rules in place. `CONFIG REWRITE` does not perform `ACL SAVE`. Do not combine this mode with `requirepass`: configure the default user's credential in the ACL file instead. See [ACL persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#use-an-external-acl-file), [ACL SAVE](https://redis.io/docs/latest/commands/acl-save/), and [ACL LOAD](https://redis.io/docs/latest/commands/acl-load/).

Keep the deployment's configuration source synchronized with the saved policy so a redeployment does not restore old permissions.

For a cutover from an old named user, first authenticate and test the replacement user. Then, from the separate administrator's Redis prompt, disable the old user and close its sessions:

```
ACL SETUSER app-old off resetpass
CLIENT KILL USER app-old SKIPME no
```

Replace `app-old` with the actual retired username. Disabling the user prevents new authentication; `CLIENT KILL` closes existing authenticated connections. Its integer reply is the number closed, which may be zero. Persist the disabled user with the chosen method. When retiring `default`, use `default` in both commands after migrating every client. See [user disabling](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) and [CLIENT KILL](https://redis.io/docs/latest/commands/client-kill/).

If retaining the username while changing its password, existing connections are not forced to authenticate again. After applying the replacement policy, use `CLIENT KILL USER app SKIPME no` from the separate administrator to force reconnection, and account for the resulting application interruption.

## 4. Separate read/write key permissions and Pub/Sub channel permissions

Redis 7.0+ supports `%R~pattern` for reading key values and `%W~pattern` for writing keys. Ordinary `~pattern` grants both. Command permission is also required; a key pattern alone grants no commands. Avoid adding a broader `~app:*` grant that would defeat the intended separation. See [key permissions](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#key-permissions).

For a worker that reads inputs, writes outputs, and publishes events, enter this replacement policy at the administrative Redis prompt:

```
ACL SETUSER app-worker reset on >REPLACE_WITH_DISTINCT_WORKER_PASSWORD resetchannels %R~app:input:* %W~app:output:* &app:events:* +get +set +publish
```

Persist it using section 3. The intended permissions are:

| Operation | Result |
| --- | --- |
| `GET app:input:probe` | Allowed |
| `SET app:output:probe value` | Allowed |
| `SET app:input:probe value` | Denied |
| `GET app:output:probe` | Denied |
| `PUBLISH app:events:probe value` | Allowed |
| `PUBLISH other:events:probe value` | Denied |

Key permissions and channel permissions are separate. `~app:*` does not restrict Pub/Sub channels; `&app:events:*` does not grant access to keys. Channel patterns require Redis 6.2+. Start with `resetchannels`, then add only the necessary channel patterns and commands. For an application without Pub/Sub, keep `resetchannels` and grant no Pub/Sub commands. See [ACL SETUSER channel rules](https://redis.io/docs/latest/commands/acl-setuser/).

The worker above cannot subscribe. If a subscriber needs `SUBSCRIBE`, grant it deliberately. If it needs `PSUBSCRIBE`, its requested pattern must literally match an allowed channel pattern; an apparently narrower glob is not sufficient. See the [Pub/Sub ACL rules](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#acl-rules).

## 5. Lock down runtime configuration, debugging, modules, and scripting

Keep administrative capabilities out of application users. The explicit command allowlists above already exclude them. When reviewing a broader policy, subtract administrative, dangerous, and scripting categories after any grants. For the selector-free `app` policy established in section 3, this administrative Redis command makes the exclusions explicit on Redis 7+:

```
ACL SETUSER app -@admin -@dangerous -@scripting -config -debug -module -script -function
```

On Redis 6.x, omit `-function`, because Redis Functions arrived in Redis 7.0. Persist the result. For an existing policy with unknown selectors, rebuild it with `reset` first; subtracting from the root rules does not remove an alternative selector's grants. See [ACL SETUSER](https://redis.io/docs/latest/commands/acl-setuser/).

`-@admin -@dangerous` alone does not disable scripting. For example, `EVAL`, `EVALSHA`, and `FCALL` belong to `@scripting`; FUNCTION library writes also belong to `@write`. Removing `SCRIPT` and `FUNCTION` alone does not remove the separate execution commands. Use `-@scripting` when the application needs no scripting, including the read-only execution variants. See [EVAL](https://redis.io/docs/latest/commands/eval/), [EVALSHA](https://redis.io/docs/latest/commands/evalsha/), [FCALL](https://redis.io/docs/latest/commands/fcall/), and [FUNCTION LOAD](https://redis.io/docs/latest/commands/function-load/).

If scripting is required, add only the execution commands the application needs and review its key permissions. Keep script and function management with the deployment administrator.

On Redis 7.0+, keep these startup settings in `redis.conf`:

```
enable-debug-command no
enable-module-command no
```

At the time of writing, `no` is the default in the pinned configuration. The alternatives are `yes` and `local`; a local connection is still an application connection that needs appropriate ACLs. These settings supplement command permissions. Disabling runtime module management does not remove modules loaded at startup or deny their own commands. Retain explicit command allowlists and review any modules enabled by the deployment. See the [pinned startup configuration](https://raw.githubusercontent.com/redis/redis/8.2.1/redis.conf).

`rename-command` is deprecated. Use ACLs to restrict commands instead of relying on renamed commands as an access boundary. See [Redis command restrictions](https://redis.io/docs/latest/operate/oss_and_stack/management/security/#disallowing-specific-commands).

## 6. Enable TLS

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), then replace the plaintext port with a TLS listener:

```
# No plaintext listener.
port 0
tls-port 6379
tls-cert-file    /etc/redis/tls/server.crt
tls-key-file     /etc/redis/tls/server.key
tls-ca-cert-file /etc/redis/tls/ca.crt
# The default is yes: require a client certificate.
# This deliberate downgrade relies on the password/ACL control in section 2.
tls-auth-clients no
```

Set `tls-auth-clients yes` for machine-to-machine deployments where clients can hold certificates; it is stronger than passwords alone. With `yes`, clients must also pass `--cert client.crt --key client.key`, or the TLS handshake is rejected before any `AUTH`. Confirm that a missing or untrusted client certificate is refused. See [Redis TLS](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/).

For HA deployments, the deliberate `tls-auth-clients no` above also removes the client-certificate requirement for incoming replicas on the data listener. Use section 13's mutual TLS settings for those connections. Enabling the client TLS listener alone does not enable outgoing replication TLS or cluster-bus TLS. The TLS cluster bus always requires a peer certificate, regardless of the data listener's `tls-auth-clients` setting. See the [replication TLS documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/) and pinned [cluster accept implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c).

## 7. Client side

Replace the host inside the single quotes with your Redis hostname, such as `redis.example.com`, and paste the whole block. `--askpass` reads the password from standard input with masking, keeping it out of process arguments. Use `--user ops` for administrative sessions.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_REDIS_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not connecting"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 host; not connecting"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute your Redis host; not connecting"; exit 1 ;;
    *)
      REDISCLI_HISTFILE=/dev/null redis-cli --tls \
        --cacert /etc/redis/tls/ca.crt -h "$1" -p 6379 --user app --askpass
      ;;
  esac
)
```

With `tls-auth-clients yes`, also add `--cert /etc/redis/tls/client.crt --key /etc/redis/tls/client.key` to the TLS invocation.

The client sends the named-user `AUTH` exchange. At the Redis prompt:

```
GET app:probe
```

`GET app:probe` is allowed by both the introductory ACL and the narrowed policy in section 3; `(nil)` is a successful read of a missing key. `PING` sits in the `@connection` and `@fast` categories, which neither policy grants, so it fails for `app`. Application clients take equivalent TLS and credential options; point them at the CA rather than disabling verification. See [Redis CLI](https://redis.io/docs/latest/develop/tools/cli/), [AUTH](https://redis.io/docs/latest/commands/auth/), [GET](https://redis.io/docs/latest/commands/get/), and [PING](https://redis.io/docs/latest/commands/ping/).

## 8. Verify

The deployment checks below are **REASONED, not demonstrated**. The authoring environment has no `redis-server`, `redis-cli`, Docker, or Podman, and denies socket inspection. No live deployment was supplied. Shell syntax and placeholder rejection were checked locally; Redis configuration parsing and exposed/fixed runtime behaviour remain outstanding in the backlog row below.

**REASONED: listener inventory.** On the Redis host, inspect every listener:

```bash
ss -tlnp
```

For the local-only configuration, Redis TCP listeners should be on loopback. An unintended wildcard or external-interface listener fails that configuration's check. Deliberate remote access needs the intended private listener and network restrictions. A socket-inspection error is inconclusive. The bind behaviour follows the [pinned configuration](https://raw.githubusercontent.com/redis/redis/8.2.1/redis.conf).

**REASONED: plaintext and unauthenticated TLS checks.** Run from a client location that should reach Redis. Substitute the actual hostname inside the quotes. For mutual TLS, add the client certificate and key options to the TLS command.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_REDIS_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 host; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute your Redis host; not probing"; exit 1 ;;
    *)
      unset REDISCLI_AUTH || exit 1
      redis-cli -h "$1" -p 6379 ping
      redis-cli --tls --cacert /etc/redis/tls/ca.crt -h "$1" -p 6379 ping
      ;;
  esac
)
```

Any RESP reply to the plaintext command, including `PONG`, `NOAUTH`, or another Redis error, means plaintext Redis is still available at that endpoint. With `port 0` and `tls-port 6379`, TCP 6379 remains open for TLS: expect the plaintext connection to close or reset without a RESP reply. A timeout, name-resolution failure, or connection refusal alone proves nothing. Confirm that the TLS command reaches the same endpoint.

For the secured default user in this guide, the unauthenticated TLS request should return `NOAUTH`. An exposed `default on nopass +@all` returns `PONG` when the connection is otherwise permitted. With mutual TLS, a missing client certificate fails before this authentication check. Then authenticate as `app` using section 7 and confirm `GET app:probe` succeeds. These distinctions follow the [TLS listener documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/) and [ACL default-user rules](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/).

**REASONED: ACL readback and denied-privilege review.** In the separate administrative session:

```
ACL GETUSER app
ACL GETUSER default
ACL LOG 20
```

After sections 3 and 5, `app` should be enabled, have a password hash without `nopass`, allow only `GET` and `SET`, have only `~app:*`, and have no channel grants or selectors. `default` should be disabled or separately password-protected. Redis may normalize the command-rule representation; compare effective permissions. Unexpected categories, wildcard patterns, additional passwords, or selectors need investigation. Do not publish the password hashes from the readback. See [ACL GETUSER](https://redis.io/docs/latest/commands/acl-getuser/).

In a fresh session authenticated as `app`, run this non-destructive check:

```
GET app:probe
CONFIG GET bind
```

The first command is the positive control. The second must return `NOPERM` for the policy above. An overprivileged account with CONFIG access returns the bind configuration instead. `NOAUTH`, connection errors, and unknown-command errors do not demonstrate the intended ACL denial. `CONFIG GET` reads configuration without changing it. See [CONFIG GET](https://redis.io/docs/latest/commands/config-get/).

Back in the administrative session:

```
ACL LOG 20
```

Look for the corresponding denied CONFIG command, the `app` username, and a recent event age. Review unexpected `auth`, `command`, `key`, and `channel` failures. Record relevant events before any reset; do not clear the log as part of this check. The log is bounded and held in memory, so an empty result is not proof that no failures occurred. See [ACL LOG](https://redis.io/docs/latest/commands/acl-log/) and the [pinned ACL-log configuration](https://raw.githubusercontent.com/redis/redis/8.2.1/redis.conf).

**REASONED: read/write and channel policy checks, Redis 7.0+.** If section 4's worker is configured, run these from the administrative session:

```
ACL GETUSER app-worker
ACL DRYRUN app-worker GET app:input:probe
ACL DRYRUN app-worker SET app:output:probe value
ACL DRYRUN app-worker SET app:input:probe value
ACL DRYRUN app-worker GET app:output:probe
ACL DRYRUN app-worker PUBLISH app:events:probe value
ACL DRYRUN app-worker PUBLISH other:events:probe value
```

Expect `OK` for reading inputs, writing outputs, and publishing within the allowed channel pattern. Expect permission-denial descriptions for the other three requests. An overly broad policy would also allow those forbidden requests. `ACL DRYRUN` checks permission without executing the request, so these checks neither write keys nor publish messages. It does not demonstrate successful authentication or replace the actual denied CONFIG request above. See [ACL DRYRUN](https://redis.io/docs/latest/commands/acl-dryrun/).

**REASONED: persistence and revocation.** During a planned restart of a disposable test instance, repeat `ACL GETUSER app`, `ACL GETUSER default`, and the applicable permission checks. A runtime-only change reverts; the persisted policy survives. After retiring `app-old`, its existing connection must close and a fresh authentication attempt must fail. Use section 7's masked prompt with the old username to test this, without putting its password in arguments. See [ACL persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#use-an-external-acl-file) and [CLIENT KILL](https://redis.io/docs/latest/commands/client-kill/).

The following checks cover sections 9-15. All are **REASONED, not demonstrated**: the authoring environment has no `redis-server`, `redis-cli`, Docker, or Podman, and no live HA topology was supplied. Run exposed-state comparisons only in a disposable isolated environment. Redis-prompt commands below are not shell commands. Use section 7's guarded connection block, masked password prompt, and disabled CLI history for authenticated data-server sessions, changing the username as directed. Certificate and key options name files; never put their contents or passwords in process arguments. References below to disabling certificate-to-user automatic authentication apply only to Redis 8.6+, as explained in section 2. Earlier releases lack that setting; do not add the directive to their configuration.

**REASONED: replication authentication and promotion, section 9.** No live primary/replica pair or failover topology was available. Compare an unsecured primary accepting an uncredentialed replica with a secured primary rejecting missing or wrong replication credentials. After restoring correct credentials, run this in an administrative session on the replica:

```
INFO replication
```

Require `master_link_status:up`, then write a disposable canary through an authorized primary session and read it from the replica. Separately repeat the unauthenticated data-listener check against the replica: it must reject the request even though its outbound replication login succeeds. See the [replication authentication implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/replication.c), [replica authentication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/#setting-a-replica-to-authenticate-to-a-master), and [INFO replication fields](https://redis.io/docs/latest/commands/info/).

On Redis 7+, run these at the administrative Redis prompt:

```
ACL DRYRUN replication PSYNC ? -1
ACL DRYRUN app PSYNC ? -1
```

Expect `OK` for `replication` and a permission-denial description for the guide's restricted `app` user. These are permission checks, not synchronization tests. They need one server; synchronization needs two processes; preserving authentication through promotion needs a live failover exercise with the checks repeated after roles change. See [ACL DRYRUN](https://redis.io/docs/latest/commands/acl-dryrun/) and the [replica command requirements](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#acl-rules-for-sentinel-and-replicas).

**REASONED: Sentinel listener, incoming authentication, and peers, section 10.** No live Sentinel or peer group was available. Repeat the unfiltered `ss -tlnp` inventory on the Sentinel host and account for its separate 26379 listener. Against Sentinel itself, compare this request before and after securing incoming authentication, while holding the transport configuration constant:

```
SENTINEL GET-MASTER-ADDR-BY-NAME mymaster
```

An exposed instance returns the monitored endpoint; the secured instance returns `NOAUTH` without Redis authentication, then permits discovery with valid credentials. Supply a trusted client certificate when mutual TLS is required, with certificate-to-user automatic authentication disabled for this comparison. The guarded Sentinel probe below supplies the TLS form. Authenticate as `discovery` and confirm administrative subcommands are denied with `NOPERM`; a read-only administrative check is `SENTINEL CONFIG GET '*'` on Redis 6.2+. A connection error or `NOAUTH` does not demonstrate the discovery user's ACL denial. See the [Sentinel command and authentication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#configuring-sentinel-instances-with-authentication).

One Sentinel suffices for listener and incoming-authentication checks. From an administrative Sentinel session, use `SENTINEL SENTINELS mymaster` to inspect peer announcements, and verify actual authenticated peer communication with multiple Sentinels. Announcement readback alone does not establish reachability. See the [pinned peer and announcement settings](https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf).

**REASONED: Sentinel monitored-server permissions and failover, section 11.** No live data server or Sentinel topology was available. In a data-server session authenticated as `sentinel-monitor`, run:

```
PING
GET app:probe
PUBLISH unrelated:probe value
```

Expect `PONG`, then `NOPERM` for both the key read and unrelated-channel publish. An unrestricted account permits the latter operations. Review `ACL LOG 20` from the separate administrator during monitoring; preserve relevant denials without clearing the log. These permission checks need one data server. See the [Sentinel-specific channel and command policy](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#redis-access-control-list-authentication).

In a disposable Sentinel and primary/replica topology, missing or wrong `sentinel auth-pass` must prevent successful authenticated monitoring; correct credentials must restore it. Exercise promotion, then confirm Sentinel monitoring and replication continue with the former replica as primary. The [pinned authentication implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c) uses the monitored primary's credentials for its replicas too.

**REASONED: cluster-bus exposure and announcements, section 12.** No cluster-enabled process or multi-node topology was available. Repeat unfiltered `ss -tlnp`, then run this through an authenticated administrative data-port session:

```
CLUSTER NODES
```

Inspect the advertised address and `@bus-port`. Compare bus connectivity from an unauthorized network with connectivity from an allowed peer: an exposed bus permits the former, while the fixed network boundary denies it and retains the working peer path. Failure from outside is meaningful only alongside a working authorized path and listener/network-policy evidence. A missing Redis `PING` response is not evidence that the binary bus is blocked. One cluster-enabled process can demonstrate its listener; working membership and advertised reachability need multiple nodes. See [CLUSTER NODES](https://redis.io/docs/latest/commands/cluster-nodes/), [cluster networking](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/#redis-cluster-tcp-ports), and the [pinned listener and announcement implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c).

For the **REASONED** section 12 network comparison, no live bus endpoint or authorized and unauthorized probe locations were available. Run this concrete TCP probe from both locations, using OpenBSD `nc`. Substitute the actual host and bus port inside the quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLUSTER_HOST' 'REPLACE_WITH_BUS_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 1 host and 1 port; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host; not probing"; exit 1 ;;
  esac
  case "$2" in
    *[!0-9]*|"") echo "substitute a numeric port; not probing"; exit 1 ;;
  esac
  [ "$2" -ge 1 ] && [ "$2" -le 65535 ] || { echo "port must be 1-65535; not probing"; exit 1; }
  if nc -vz -w 5 "$1" "$2"; then
    echo "TCP connected; the bus port is reachable from here"
  else
    printf 'TCP probe exit=%s; compare with the allowed-peer control\n' "$?"
  fi
)
```

An exposed network boundary permits a TCP connection from the unauthorized location. The fixed boundary denies that connection while retaining the allowed peer's successful connection to the intended listener. A local tool error, name-resolution failure, or failed allowed-peer control is inconclusive. This probes TCP reachability only, not TLS, certificate acceptance, or cluster membership. See the [cluster networking requirements](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/#redis-cluster-tcp-ports).

**REASONED: replication encryption and incoming certificates, section 13.** No live primary/replica pair, certificate fixtures, or connection evidence was available. Use a disposable pair connected directly, without a TLS-terminating proxy. Correlate the primary's actual listener, the replica's established connection, and successful replication. `INFO replication` reports link status, not encryption.

At the primary's authenticated administrative Redis prompt:

```
CONFIG GET port
CONFIG GET tls-port
```

For the fixed configuration, require `port` to be `0` and record the nonzero `tls-port`. At the replica's authenticated administrative Redis prompt:

```
CONFIG GET tls-replication
INFO replication
```

Require `tls-replication` to be `yes`, `master_host` and `master_port` to identify that primary's TLS endpoint, and `master_link_status:up`. On the replica host, inspect established connections:

```bash
ss -tnp
```

Identify the replica process's established connection to the recorded primary address and TLS port. Use an account permitted to see process information. Missing process information or a socket-inspection error is inconclusive.

From an allowed client location, probe that same primary endpoint. Substitute a DNS hostname or IPv4 address and the recorded TLS port inside the quotes. Use the installed CA and client certificate paths. The commands deliberately omit Redis credentials; on Redis 8.6+, keep certificate-to-user automatic authentication disabled for this comparison.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PRIMARY_HOST' 'REPLACE_WITH_PRIMARY_TLS_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 1 host and 1 port; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host; not probing"; exit 1 ;;
  esac
  case "$2" in
    *[!0-9]*|"") echo "substitute a numeric port; not probing"; exit 1 ;;
  esac
  [ "$2" -ge 1 ] && [ "$2" -le 65535 ] || { echo "port must be 1-65535; not probing"; exit 1; }
  unset REDISCLI_AUTH || exit 1
  printf '\nNo client certificate\n'
  if timeout 10s redis-cli --tls --cacert /etc/redis/tls/ha-ca.crt \
      -h "$1" -p "$2" PING; then
    echo "inspect the RESP reply; exit=0 alone is not a pass"
  else
    printf 'probe exit=%s; inspect the TLS or authentication error\n' "$?"
  fi
  printf '\nTrusted client certificate, positive control\n'
  if timeout 10s redis-cli --tls --cacert /etc/redis/tls/ha-ca.crt \
      --cert /etc/redis/tls/client.crt --key /etc/redis/tls/client.key \
      -h "$1" -p "$2" PING; then
    echo "inspect the RESP reply; exit=0 alone is not a pass"
  else
    printf 'probe exit=%s; inspect the TLS or authentication error\n' "$?"
  fi
)
```

With `tls-auth-clients yes`, require a TLS certificate rejection for the first request and `NOAUTH` for the trusted-certificate positive control. In the isolated comparison with `tls-auth-clients no`, both requests reach `NOAUTH`. This tests the data listener's certificate requirement, which also applies to incoming replicas; it does not authenticate a replication session. A timeout, missing certificate file, or unreachable endpoint is inconclusive.

To confirm current synchronization, write a fresh disposable value at an authorized primary Redis prompt:

```
SET app:ha-tls-probe tls-check-1
```

Then read it at an authorized replica Redis prompt:

```
GET app:ha-tls-probe
```

Require the newly written value, changing it on each repetition. In the exposed comparison, use `tls-replication no` and the primary's plaintext endpoint: replication and the canary can still succeed, while the connection terminates on the plaintext listener. In the fixed comparison, require the active replica connection to terminate on the primary's TLS-only listener, the successful TLS positive control, and the fresh canary together. Neither link status nor a separate successful TLS probe alone proves that replication is encrypted. See the [TLS replication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/), [pinned listener implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/server.c), [INFO replication fields](https://redis.io/docs/latest/commands/info/), and [Redis CLI options](https://redis.io/docs/latest/develop/tools/cli/).

**REASONED: cluster-bus client certificates, section 13.** No live TLS cluster-bus listener or certificate fixtures were available. From an allowed peer location, probe the actual bus port with no certificate, an otherwise valid certificate from an untrusted CA, and a trusted certificate. If Redis 8.10+ peer-name checking is enabled, both certificate fixtures must contain the expected name so this comparison isolates CA trust.

These OpenSSL probes require TLS 1.2 to be enabled on the test endpoint and GNU `timeout`. They select TLS 1.2 so a completed handshake includes the server's acceptance of the client certificate. Do not weaken a TLS 1.3-only deployment for this check; these particular probes are inconclusive there. Use protected PEM fixture files at the paths below, replace the DNS hostname or IPv4 address and actual bus port inside the quotes, and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLUSTER_HOST' 'REPLACE_WITH_BUS_PORT' 'REPLACE_WITH_EXPECTED_PEER_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 1 host, 1 port, and 1 expected peer name; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host; not probing"; exit 1 ;;
  esac
  case "$2" in
    *[!0-9]*|"") echo "substitute a numeric port; not probing"; exit 1 ;;
  esac
  [ "$2" -ge 1 ] && [ "$2" -le 65535 ] || { echo "port must be 1-65535; not probing"; exit 1; }
  case "$3" in
    *REPLACE_WITH_*|"") echo "substitute the expected peer name; not probing"; exit 1 ;;
  esac
  printf '\nNo client certificate\n'
  if timeout 10s openssl s_client -connect "$1:$2" -tls1_2 -brief \
      -verify_hostname "$3" -verify_return_error -CAfile /etc/redis/tls/ha-ca.crt </dev/null; then
    echo "probe exit=0; inspect the handshake result"
  else
    printf 'probe exit=%s; inspect the TLS error\n' "$?"
  fi
  printf '\nUntrusted client certificate\n'
  if timeout 10s openssl s_client -connect "$1:$2" -tls1_2 -brief \
      -verify_hostname "$3" -verify_return_error -CAfile /etc/redis/tls/ha-ca.crt \
      -cert /etc/redis/tls/untrusted-client.crt -key /etc/redis/tls/untrusted-client.key </dev/null; then
    echo "probe exit=0; inspect the handshake result"
  else
    printf 'probe exit=%s; inspect the TLS error\n' "$?"
  fi
  printf '\nTrusted client certificate, positive control\n'
  if timeout 10s openssl s_client -connect "$1:$2" -tls1_2 -brief \
      -verify_hostname "$3" -verify_return_error -CAfile /etc/redis/tls/ha-ca.crt \
      -cert /etc/redis/tls/ha-client.crt -key /etc/redis/tls/ha-client.key </dev/null; then
    echo "probe exit=0; inspect the handshake result"
  else
    printf 'probe exit=%s; inspect the TLS error\n' "$?"
  fi
)
```

Require certificate-related TLS rejection for the first two probes and a completed, verified TLS handshake for the trusted positive control. Repeat with data-port `tls-auth-clients no` and `yes`; the bus must require a trusted certificate in both cases. A timeout, local file error, protocol-version mismatch, or failed server-certificate verification does not demonstrate rejection of the client certificate.

An exposed plaintext bus has no TLS certificate gate and will fail the TLS positive control; that failure must not be mistaken for a protected bus. Use the section 12 TCP reachability comparison separately. OpenSSL does not speak the binary cluster protocol, so a successful handshake establishes neither cluster membership nor working node-to-node traffic. Listener checks need one cluster-enabled process; working cluster transport needs multiple nodes. See the [pinned cluster certificate requirement](https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c) and [TLS cluster documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/).

**REASONED: Sentinel TLS and outgoing connections, section 14.** No live Sentinel or data-node topology was available. Repeat the plaintext/TLS discriminator on 26379, not only on the Redis data port. The following block assumes the Redis 6.2+ `discovery` account, the monitored group `mymaster`, and certificate-to-user automatic authentication disabled. For the password-only Sentinel arrangement, use `--user default` instead. Replace the host inside the single quotes and use the installed certificate file paths, then paste the whole block:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SENTINEL_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 host; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute your Sentinel host; not probing"; exit 1 ;;
    *)
      unset REDISCLI_AUTH || exit 1
      timeout 10s redis-cli -h "$1" -p 26379 SENTINEL GET-MASTER-ADDR-BY-NAME mymaster
      timeout 10s redis-cli --tls --cacert /etc/redis/tls/ha-ca.crt \
        --cert /etc/redis/tls/client.crt --key /etc/redis/tls/client.key \
        -h "$1" -p 26379 SENTINEL GET-MASTER-ADDR-BY-NAME mymaster
      REDISCLI_HISTFILE=/dev/null timeout 10s redis-cli --tls \
        --cacert /etc/redis/tls/ha-ca.crt \
        --cert /etc/redis/tls/client.crt --key /etc/redis/tls/client.key \
        -h "$1" -p 26379 --user discovery --askpass \
        SENTINEL GET-MASTER-ADDR-BY-NAME mymaster
      ;;
  esac
)
```

Any RESP reply to the first request proves plaintext Redis protocol is available at that endpoint. With the TLS-only configuration, expect no plaintext RESP reply; the trusted-certificate TLS request without Redis credentials must reach `NOAUTH`, and the authenticated request must return the monitored endpoint. A timeout, resolution error, or connection refusal alone proves nothing. Repeat the TLS requests without a client certificate and with an untrusted certificate; both must fail under `tls-auth-clients yes`. Restore the trusted certificate and valid credentials as the positive control. See [Sentinel TLS](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/#sentinel), [Sentinel authentication](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#configuring-sentinel-instances-with-authentication), and [Redis CLI options](https://redis.io/docs/latest/develop/tools/cli/).

One Sentinel can demonstrate its incoming listener. Outgoing TLS, peer discovery, and failover need a live Sentinel/data-node topology and independent connection evidence; success on 26379 does not prove those outgoing connections use TLS. See the [pinned outgoing connection and advertisement implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c).

The Sentinel shell block above passed local Bash syntax and ShellCheck checks. With `set -u`, it rejected the unchanged placeholder, an embedded placeholder, an empty host, a marker-only assignment, an omitted assignment with no inherited arguments, and an extra host argument before any connection command ran. These local checks did not demonstrate Redis behaviour.

**REASONED: enforced HA peer identity, Redis 8.10+, section 15.** No Redis 8.10 runtime, certificate fixtures, or HA endpoints were available. Prepare two otherwise valid client certificates signed by the same trusted CA: one matching the configured HA identity and one that does not match it through either SAN or CN fallback. Keep certificate purpose, validity, CA trust, and Redis credentials constant.

For incoming identity enforcement, target the TLS cluster-bus port. An ordinary client handshake to the data port does not exercise this incoming peer-name restriction. At the test node's authenticated administrative data-port prompt, first establish the isolated comparison without the restriction:

```
CONFIG SET tls-expected-peer-name ""
```

Run the following block, then enable the intended identity at that same administrative prompt and run the block again:

```
CONFIG SET tls-expected-peer-name redis-ha.example.com
```

Replace the example identity consistently with the identity issued to intended HA nodes. Require `OK` from each configuration change. The shell block uses the same TLS 1.2, GNU `timeout`, and protected PEM-file prerequisites as the preceding bus-certificate check. Substitute the DNS hostname or IPv4 address and actual bus port inside the quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLUSTER_HOST' 'REPLACE_WITH_BUS_PORT' 'REPLACE_WITH_EXPECTED_PEER_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 1 host, 1 port, and 1 expected peer name; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host; not probing"; exit 1 ;;
  esac
  case "$2" in
    *[!0-9]*|"") echo "substitute a numeric port; not probing"; exit 1 ;;
  esac
  [ "$2" -ge 1 ] && [ "$2" -le 65535 ] || { echo "port must be 1-65535; not probing"; exit 1; }
  case "$3" in
    *REPLACE_WITH_*|"") echo "substitute the expected peer name; not probing"; exit 1 ;;
  esac
  printf '\nSame CA, wrong peer name\n'
  if timeout 10s openssl s_client -connect "$1:$2" -tls1_2 -brief \
      -verify_hostname "$3" -verify_return_error -CAfile /etc/redis/tls/ha-ca.crt \
      -cert /etc/redis/tls/wrong-name-client.crt -key /etc/redis/tls/wrong-name-client.key </dev/null; then
    echo "probe exit=0; inspect the handshake result"
  else
    printf 'probe exit=%s; inspect the TLS error\n' "$?"
  fi
  printf '\nSame CA, matching peer name, positive control\n'
  if timeout 10s openssl s_client -connect "$1:$2" -tls1_2 -brief \
      -verify_hostname "$3" -verify_return_error -CAfile /etc/redis/tls/ha-ca.crt \
      -cert /etc/redis/tls/matching-name-client.crt -key /etc/redis/tls/matching-name-client.key </dev/null; then
    echo "probe exit=0; inspect the handshake result"
  else
    printf 'probe exit=%s; inspect the TLS error\n' "$?"
  fi
)
```

Without the name restriction, require both handshakes to complete. With enforcement enabled, require the wrong-name handshake to be rejected and the matching-name handshake to complete. Correlate rejection with the accepting node's certificate-verification error. An unrelated failure or a failed positive control is inconclusive. Inspect startup warnings indicating that this build does not enforce peer-name verification; accepting the wrong-name certificate with the setting enabled fails this enforcement check. See the [pinned identity configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf) and [enforcement and warning paths](https://raw.githubusercontent.com/redis/redis/8.10.1/src/tls.c).

Test outbound replication separately in a disposable Redis 8.10+ pair. Prepare matching-name and wrong-name server certificates from the same CA, with valid server-authentication purposes. At the primary's authenticated administrative prompt, install the wrong-name fixture:

```
CONFIG SET tls-cert-file /etc/redis/tls/wrong-name-server.crt tls-key-file /etc/redis/tls/wrong-name-server.key
```

Require `OK`. At the replica's authenticated administrative prompt, remove the name restriction and force a fresh connection:

```
CONFIG SET tls-expected-peer-name ""
CLIENT KILL TYPE master
INFO replication
```

Repeat `INFO replication` until the connection attempt completes; require `master_link_status:up` as the unrestricted control. Then enable the intended identity on the replica and force another connection:

```
CONFIG SET tls-expected-peer-name redis-ha.example.com
CLIENT KILL TYPE master
INFO replication
```

Require the new connection to fail with a certificate-name verification error in the replica's log. A down link without that evidence is inconclusive. At the primary's administrative prompt, restore the matching fixture:

```
CONFIG SET tls-cert-file /etc/redis/tls/matching-name-server.crt tls-key-file /etc/redis/tls/matching-name-server.key
```

Require `OK`, then repeat `INFO replication` on the replica and the fresh canary check above; both must recover. These commands intentionally reconnect replication and belong only in the isolated comparison. Keep the intended name restriction enabled afterward. File paths are arguments, but private-key contents and passwords are not. See [CONFIG SET](https://redis.io/docs/latest/commands/config-set/), the [pinned modifiable TLS settings](https://raw.githubusercontent.com/redis/redis/8.10.1/src/config.c), [CLIENT KILL](https://redis.io/docs/latest/commands/client-kill/), and [INFO replication fields](https://redis.io/docs/latest/commands/info/).

Small isolated endpoints can exercise these handshakes without a complete functioning cluster. Proving the full HA trust boundary requires testing every connection class, including outgoing cluster-bus and `MIGRATE` connections and Sentinel separately. Do not expect the directive to reject the wrong-name certificate on Sentinel's reviewed outgoing path; verify Sentinel's dedicated trust boundary independently. That exception is derived from the [pinned Sentinel source](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c), not a runtime demonstration.

| Backlog ID | Outstanding demonstration | Status |
| --- | --- | --- |
| REDIS-LIVE-1 | In an isolated environment with Redis, TLS certificates, and socket access, record exact versions and demonstrate exposed/fixed listeners, plaintext rejection, authentication, ACL readback, actual CONFIG denial and ACL logging, directional key/channel checks, both persistence methods across restart, and old-user session revocation. Parse the applicable configuration examples with the real Redis server. Also demonstrate the seven HA checks: (1) replication credential rejection, successful synchronization and canary transfer, replica listener authentication, Redis 7+ replication ACL checks, and authentication through promotion; (2) Sentinel listener restrictions, incoming authentication, discovery-user denials, announcements, and authenticated peer communication; (3) Sentinel monitored-server command/channel restrictions, ACL logging, credential failure/recovery, and monitoring through failover; (4) cluster-bus listener and announcement correctness with denied unauthorized and working authorized paths; (5) replication encryption using correlated TLS listener, established-connection, and fresh canary evidence, incoming replica certificate requirements, and mandatory TLS cluster-bus certificates; (6) Sentinel plaintext rejection, incoming certificate/password checks, outgoing TLS, peer discovery, and failover; (7) Redis 8.10+ same-CA wrong-name rejection with matching-certificate positive controls, outbound replication and incoming bus tests, build-warning inspection, and every remaining connection class including Sentinel's separate trust boundary. Parse the added server, ACL, and Sentinel examples on their stated versions and record exact Redis versions and TLS build capabilities. | Open; REASONED checks above remain undemonstrated. |

## 9. Authenticate replication through role changes

Within this guide's Redis 6.0+ scope, an unsecured default user permits replication commands as well as ordinary commands once the network permits access. A dedicated replication user requires data-server ACLs, available since Redis 6.0. The required replication commands are `PING`, `REPLCONF`, and `PSYNC`. See the [ACL rules for replicas](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#acl-rules-for-sentinel-and-replicas).

For the password-only arrangement, configure both directions on every member eligible to become primary:

```
requirepass REPLACE_WITH_DATA_PASSWORD
masterauth REPLACE_WITH_DATA_PASSWORD
```

`requirepass` protects incoming access. `masterauth` supplies an outbound credential; it does not protect the replica's own listener. Configure both on potential primaries so authentication survives role changes. See the [pinned replication configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf) and [Sentinel authentication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#redis-access-control-list-authentication).

Prefer a dedicated replication account, provisioned on every potential primary. Put this rule in the ACL persistence surface chosen in section 3:

```
user replication reset on >REPLACE_WITH_REPLICATION_PASSWORD +ping +replconf +psync
```

Put the outbound credentials in each data member's server configuration:

```
masteruser replication
masterauth REPLACE_WITH_REPLICATION_PASSWORD
```

Retain the secured default user and separate administrator from sections 2 and 3. The replication account receives the full replication stream: omitting key-pattern grants does not restrict it to an application prefix. The pinned [configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf) documents both credential directives; the [replication implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/replication.c) sends username/password authentication when configured and aborts the handshake on authentication failure. See also [persistent replica authentication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/#setting-a-replica-to-authenticate-to-a-master).

## 10. Secure Sentinel's separate listener and peer authentication

Sentinel has a separate listener, normally TCP 26379. Its shipped configuration disables protected mode and supplies no active authentication rule. Protecting the Redis data port does not protect Sentinel. Password-only Sentinel authentication is available throughout this guide's Redis 6.0+ scope; Sentinel ACLs require Redis 6.2+. See the [pinned Sentinel configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf) and [Sentinel authentication documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#configuring-sentinel-instances-with-authentication).

For a representative private Sentinel address, the password-only arrangement is:

```
bind 10.0.0.11
port 26379
requirepass REPLACE_WITH_SENTINEL_PASSWORD
sentinel announce-ip 10.0.0.11
sentinel announce-port 26379
```

Restrict network access to the required Sentinel peers, discovery clients, and administrators. Use the same Sentinel password across peers in this arrangement, with a credential distinct from the data-server password. The announcement directives publish discovery information; they neither bind sockets nor enforce access restrictions. Section 14 replaces the plaintext listener with TLS. See the [pinned listener, announcement, and password settings](https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf).

Alternatively, on Redis 6.2+, use ACL authentication. Retain the private bind and announcements, and use these account rules instead of the password-only `requirepass` arrangement:

```
user sentinel-peer reset on >REPLACE_WITH_SENTINEL_PEER_PASSWORD &* +@all
user discovery reset on >REPLACE_WITH_DISCOVERY_PASSWORD +ping +sentinel|get-master-addr-by-name
user default off resetpass
```

Configure Sentinel's outgoing peer credentials separately:

```
sentinel sentinel-user sentinel-peer
sentinel sentinel-pass REPLACE_WITH_SENTINEL_PEER_PASSWORD
```

Provision the peer account consistently across the Sentinel group. Establish and test administrative access before disabling `default`. The peer account above has administrative authority; the discovery account permits only `PING` and `SENTINEL GET-MASTER-ADDR-BY-NAME`. Add other commands only when the actual client library needs them. Use the chosen ACL persistence surface for `user` rules and Sentinel configuration for peer credentials. Choose ACL authentication or the password-only arrangement rather than combining their examples. See the [pinned ACL and peer settings](https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf).

## 11. Give Sentinel dedicated monitored-server credentials

Sentinel's own password does not authenticate it to Redis data servers. Monitored-instance credentials are initially unset. Leaving data servers unauthenticated to permit monitoring exposes them; giving Sentinel an application or unrestricted administrator credential grants unnecessary authority. The monitored-server ACL mechanism requires Redis 6.0+, while the channel-restricted policy below requires Redis 6.2+. See the [pinned credential settings](https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf) and [Sentinel-specific ACL documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#redis-access-control-list-authentication).

On every Sentinel monitoring the group named `mymaster`:

```
sentinel auth-user mymaster sentinel-monitor
sentinel auth-pass mymaster REPLACE_WITH_MONITOR_PASSWORD
```

On every data member of that group, provision the same dedicated account in the ACL persistence surface chosen in section 3:

```
user sentinel-monitor reset on >REPLACE_WITH_MONITOR_PASSWORD resetchannels &__sentinel__:hello +ping +info +role +multi +exec +slaveof +subscribe +publish +config|rewrite +client|setname +client|kill +script|kill
```

This policy is adapted from the current Sentinel-specific vendor example and reviewed for Redis 8.10.1. It permits the reserved discovery channel specifically, rather than every Pub/Sub channel. It remains a powerful operational account. Redis 6.0 cannot enforce this channel restriction; do not describe an account there as having equivalent channel isolation. See the [Sentinel ACL requirements](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#redis-access-control-list-authentication).

For password-only data servers, omit `auth-user` and set `auth-pass` to their `requirepass` value. Sentinel uses the monitored primary's credentials for its replicas too, so provision them on every member eligible for either role. Its monitored-server credentials are distinct from its Sentinel-peer credentials. See `sentinelSendAuthIfNeeded` in the [pinned implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c).

## 12. Restrict the cluster bus and announce private endpoints

Cluster mode is opt-in. When enabled, it adds a binary node-to-node listener for discovery, failure detection, and failover coordination. Restrict this listener separately throughout this guide's Redis 6.0+ scope. Its default port is the data port plus 10000, normally 16379 beside 6379. Data-port password authentication does not provide a RESP `AUTH` gate on the binary bus. See the [cluster networking documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/#redis-cluster-tcp-ports).

For an existing TLS cluster using section 13, this explicit listener and announcement example targets Redis 8.10.1; it is not a claim that every directive is available on every Redis 6.x release:

```
bind 10.0.0.11
cluster-port 16379
cluster-announce-ip 10.0.0.11
cluster-announce-port 0
cluster-announce-tls-port 6379
cluster-announce-bus-port 16379
```

Permit the bus only between cluster nodes. Permit the data port to intended clients and nodes that need it. `cluster-port` selects the actual bus listener; `cluster-announce-*` publishes endpoint information and is not a firewall. Account for remapping rather than assuming the externally reachable bus port retains the 10000 offset. See the [pinned cluster and NAT configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf).

In TLS cluster mode, the default offset is based on `tls-port`; the bus uses the configured bind addresses. The listener and announced endpoints must both match the intended deployment. See `defaultClientPort`, `deriveAnnouncedPorts`, and `clusterInitLast` in the [pinned cluster implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c).

## 13. Enable TLS for replication and cluster traffic

Redis 6.0+ with TLS support needs separate switches for outgoing replication and cluster traffic. Enabling the client TLS listener does not enable either one; both switches default to disabled. See the [TLS documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/) and [pinned defaults](https://raw.githubusercontent.com/redis/redis/8.10.1/src/config.c).

On all applicable data nodes, retain section 6's certificate, key, and CA configuration and use:

```
port 0
tls-port 6379
tls-replication yes
tls-auth-clients yes
```

On cluster nodes, also configure:

```
tls-cluster yes
```

Where replication is configured explicitly, point `replicaof` at the primary's TLS endpoint. `tls-auth-clients yes` is already the Redis default; restoring it from section 6's deliberate `no` requires incoming replicas, as well as ordinary clients, to present trusted certificates. Retain replication credentials from section 9, subject to the certificate-to-user authentication qualification in section 2. See the [pinned TLS and replication settings](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf).

Redis normally reuses its certificate for outgoing connections. On Redis 6.2+, if certificates have separate server and client purposes, configure `tls-client-cert-file` and `tls-client-key-file` for the outgoing certificate and key. Readers on Redis releases before 6.2 must instead use one certificate suitable for both server and client authentication, configured through `tls-cert-file` and `tls-key-file`. Omit both `tls-client-*` directives on those releases: an unknown configuration directive prevents startup. Compare the pinned [6.0.20 certificate configuration](https://raw.githubusercontent.com/redis/redis/6.0.20/redis.conf) with the [6.2.0 certificate configuration](https://raw.githubusercontent.com/redis/redis/6.2.0/redis.conf).

The TLS cluster bus always requests and requires a peer certificate. Its accept path explicitly uses `TLS_CLIENT_AUTH_YES`; setting data-port `tls-auth-clients no` does not disable cluster-bus certificate authentication. See `clusterAcceptHandler` in the [pinned implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c).

## 14. Configure TLS on Sentinel and its outgoing connections

Sentinel is a separate process; data-node TLS configuration does not configure it. On Redis 6.0+ with TLS support, a nonzero `tls-port` creates Sentinel's incoming TLS listener independently of `tls-replication`. The `tls-replication yes` setting selects TLS for outgoing connections to monitored servers and Sentinel peers. It also selects the configured TLS port for Sentinel's default port advertisement; an explicit `sentinel announce-port` overrides that choice. Configure both `tls-port` and `tls-replication yes` for end-to-end TLS, and set `port 0` to disable the plaintext listener. See `initListeners` in the [pinned server implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/server.c), and `sentinelReconnectInstance` and `sentinelSendHello` in the [pinned Sentinel implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c).

In each Sentinel's configuration:

```
port 0
tls-port 26379
tls-replication yes
tls-auth-clients yes
tls-cert-file /etc/redis/tls/sentinel.crt
tls-key-file /etc/redis/tls/sentinel.key
tls-ca-cert-file /etc/redis/tls/ha-ca.crt
sentinel announce-port 26379
```

Retain section 10's private bind and chosen authentication arrangement, and section 11's monitored-server credentials. Set `sentinel monitor` to the primary's TLS data port. Provision certificates and trust for Sentinel-to-data-server connections, Sentinel-to-Sentinel connections, and discovery clients. `tls-cluster` is not Sentinel's TLS switch. Certificate directives are documented in the [pinned Redis configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf); `sentinelReconnectInstance`, `instanceLinkNegotiateTLS`, and `sentinelSendHello` in the [pinned Sentinel implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c) establish the outgoing TLS selection and TLS-port advertisement.

## 15. Restrict trusted HA peer identities

Redis 8.10 introduced server-to-server certificate-name authentication. The setting is unset by default, leaving CA validation without this additional peer-name restriction. This control is newer than the guide's existing 8.2.1 configuration references and must not be added to the generic Redis 6.0+ baseline. See the [8.10 release notes](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.10-release-notes/) and [pinned peer-name configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf).

On Redis 8.10+ builds that enforce the feature:

```
tls-expected-peer-name redis-ha.example.com
```

Replace the example identity with the intended HA trust-group name. Issue intended nodes certificates containing that shared identity in their SANs, including the outgoing client certificates. This adds identity checking to CA validation for outgoing replication, cluster-bus, and `MIGRATE` connections, and incoming cluster-bus connections. It identifies membership in the configured trust group, not a unique certificate-to-node-ID mapping. See the [pinned configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf) and [`tlsSetVerifyName` and its callers](https://raw.githubusercontent.com/redis/redis/8.10.1/src/tls.c).

Two limits apply:

- Builds with `TLS_NO_PEER_NAME_VERIFICATION` warn and continue without enforcing the name; CA validation still applies. Configuration readback alone does not prove enforcement. See the [pinned TLS implementation](https://raw.githubusercontent.com/redis/redis/8.10.1/src/tls.c).
- Sentinel's outgoing `instanceLinkNegotiateTLS` path creates an SSL object and invokes hiredis directly without applying this name check. This is a source-derived conclusion from Redis 8.10.1, not a demonstrated runtime result. Do not rely on this directive to protect Sentinel's outgoing peer identity. See the [separate Sentinel TLS path](https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c).

Use a dedicated HA trust boundary for Sentinel and releases without this identity control. Do not trust a general-purpose CA whose other certificate holders should not be able to impersonate HA peers. The [pinned configuration](https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf) explains why shared CA trust alone is insufficient.

## Common mistakes

- Commenting out `bind`, which listens everywhere, while `requirepass` is still empty.
- One `requirepass` value shared across environments and committed to the repository.
- TLS enabled but the plaintext `port` left open alongside it; set `port 0`.
- Adding a narrower ACL without resetting old grants or reviewing selectors.
- Saving `redis.conf` while runtime ACL changes belong in an external ACL file.
- Disabling a user and assuming its existing connections have been disconnected.
- Treating key patterns as restrictions on Pub/Sub channels or keyless commands.

## Valkey

Valkey, the community fork of Redis, uses the same `requirepass`, ACL, and TLS configuration concepts described above. Apply the version-appropriate controls and check the installed release's syntax and defaults. See the Valkey [security](https://valkey.io/topics/security/), [ACL](https://valkey.io/topics/acl/), and [TLS](https://valkey.io/topics/tls/) documentation.

The upstream Redis HA controls and source-derived limitations in sections 9-15 have not been established for Valkey. Verify those controls separately against the installed Valkey release before applying them.

## Sources (checked September 2026)

The tagged configuration files below pin syntax and historical behaviour; they are not recommendations to install those patch releases.

- Redis security model, authentication, and deprecated command renaming: https://redis.io/docs/latest/operate/oss_and_stack/management/security/
- Redis configuration format: https://redis.io/docs/latest/operate/oss_and_stack/management/config/
- Redis TLS build support, listeners, and client certificates: https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/
- Redis ACL rules, categories, selectors, key/channel permissions, and persistence: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/
- Redis 8.2.1 pinned configuration, including ACL-file compatibility and debug/module defaults: https://raw.githubusercontent.com/redis/redis/8.2.1/redis.conf
- Redis 6.0.20 pinned bind and protected-mode configuration: https://raw.githubusercontent.com/redis/redis/6.0.20/redis.conf
- Redis 6.2.14 pinned optional-bind syntax and protected-mode configuration: https://raw.githubusercontent.com/redis/redis/6.2.14/redis.conf
- Redis 7.0.15 pinned protected-mode and hardened-command configuration: https://raw.githubusercontent.com/redis/redis/7.0.15/redis.conf
- Official Redis Docker images (redis/docker-library-redis): the build patch that sets the `protected-mode` default to 0, and `CMD ["redis-server"]`, present in every Dockerfile on the default branch at commit 584feaab6cd12a77866c121beff1bb16ff239486 (6.2 through 7.4, shown here for 7.4 Debian and Alpine, 7.2 and 6.2) and at release tag v8.10.2: https://github.com/redis/docker-library-redis/blob/584feaab6cd12a77866c121beff1bb16ff239486/7.4/debian/Dockerfile#L85-L90, https://github.com/redis/docker-library-redis/blob/584feaab6cd12a77866c121beff1bb16ff239486/7.4/debian/Dockerfile#L146-L150, https://github.com/redis/docker-library-redis/blob/584feaab6cd12a77866c121beff1bb16ff239486/7.4/alpine/Dockerfile#L79-L84, https://github.com/redis/docker-library-redis/blob/584feaab6cd12a77866c121beff1bb16ff239486/7.2/debian/Dockerfile#L85-L90, https://github.com/redis/docker-library-redis/blob/584feaab6cd12a77866c121beff1bb16ff239486/6.2/debian/Dockerfile#L85-L90, https://github.com/redis/docker-library-redis/blob/v8.10.2/debian/Dockerfile#L70-L75, https://github.com/redis/docker-library-redis/blob/v8.10.2/debian/Dockerfile#L127-L130 and https://github.com/redis/docker-library-redis/blob/v8.10.2/alpine/Dockerfile#L82-L87
- Redis compiled defaults, `bind` `* -::*`, `protected-mode` 1, and the `default` user `on nopass +@all` (pinned tags 7.4.8 and 8.10.2): https://github.com/redis/redis/blob/7.4.8/src/server.h#L119-L120, https://github.com/redis/redis/blob/7.4.8/src/config.c#L3055, https://github.com/redis/redis/blob/7.4.8/src/acl.c#L1407-L1415, https://github.com/redis/redis/blob/8.10.2/src/server.h#L138-L139, https://github.com/redis/redis/blob/8.10.2/src/config.c#L3403 and https://github.com/redis/redis/blob/8.10.2/src/acl.c#L1430-L1438
- Redis CLI connection flags, masked password input, TLS options, and history control: https://redis.io/docs/latest/develop/tools/cli/
- AUTH named-user and default-user authentication: https://redis.io/docs/latest/commands/auth/
- ACL SETUSER replacement rules and version history: https://redis.io/docs/latest/commands/acl-setuser/
- CONFIG REWRITE persistence and prerequisites: https://redis.io/docs/latest/commands/config-rewrite/
- ACL SAVE persistence to the configured ACL file: https://redis.io/docs/latest/commands/acl-save/
- ACL LOAD replacement and failure behaviour: https://redis.io/docs/latest/commands/acl-load/
- CLIENT KILL user filtering and SKIPME behaviour: https://redis.io/docs/latest/commands/client-kill/
- ACL GETUSER effective-policy readback: https://redis.io/docs/latest/commands/acl-getuser/
- ACL LOG failure reasons and retrieval: https://redis.io/docs/latest/commands/acl-log/
- ACL DRYRUN checks without command execution: https://redis.io/docs/latest/commands/acl-dryrun/
- CONFIG GET read-only configuration inspection: https://redis.io/docs/latest/commands/config-get/
- GET and SET syntax and key access: https://redis.io/docs/latest/commands/get/ and https://redis.io/docs/latest/commands/set/
- PING command categories: https://redis.io/docs/latest/commands/ping/
- Global database write commands: https://redis.io/docs/latest/commands/flushall/ and https://redis.io/docs/latest/commands/flushdb/ and https://redis.io/docs/latest/commands/swapdb/
- Keyspace enumeration commands: https://redis.io/docs/latest/commands/keys/ and https://redis.io/docs/latest/commands/scan/ and https://redis.io/docs/latest/commands/randomkey/
- Global function-library write commands: https://redis.io/docs/latest/commands/function-load/ and https://redis.io/docs/latest/commands/function-delete/ and https://redis.io/docs/latest/commands/function-flush/ and https://redis.io/docs/latest/commands/function-restore/
- Script and function execution categories: https://redis.io/docs/latest/commands/eval/ and https://redis.io/docs/latest/commands/evalsha/ and https://redis.io/docs/latest/commands/fcall/
- Read-only scripting variants: https://redis.io/docs/latest/commands/eval_ro/ and https://redis.io/docs/latest/commands/evalsha_ro/ and https://redis.io/docs/latest/commands/fcall_ro/
- Pub/Sub publishing and subscriptions: https://redis.io/docs/latest/commands/publish/ and https://redis.io/docs/latest/commands/subscribe/ and https://redis.io/docs/latest/commands/psubscribe/
- Valkey security, ACLs, and TLS: https://valkey.io/topics/security/ and https://valkey.io/topics/acl/ and https://valkey.io/topics/tls/
- Redis 8.10.1 pinned server configuration: https://raw.githubusercontent.com/redis/redis/8.10.1/redis.conf
- Redis 6.2.0 separate outgoing TLS certificate and key configuration: https://raw.githubusercontent.com/redis/redis/6.2.0/redis.conf
- Redis 8.10.1 independent TCP and TLS listener initialization: https://raw.githubusercontent.com/redis/redis/8.10.1/src/server.c
- CONFIG SET runtime configuration changes and multiple-parameter syntax: https://redis.io/docs/latest/commands/config-set/
- Redis 8.10.1 pinned Sentinel configuration: https://raw.githubusercontent.com/redis/redis/8.10.1/sentinel.conf
- Redis 8.10.1 registered TLS and certificate-authentication defaults: https://raw.githubusercontent.com/redis/redis/8.10.1/src/config.c
- Redis 8.6.0 tls-auth-clients-user introduction and default: https://raw.githubusercontent.com/redis/redis/8.6.0/redis.conf
- Redis 8.6 release notes and tls-auth-clients-user introduction: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.6-release-notes/
- Redis 8.10.1 replication authentication implementation: https://raw.githubusercontent.com/redis/redis/8.10.1/src/replication.c
- Redis 8.10.1 Sentinel authentication, outgoing TLS, and announcements: https://raw.githubusercontent.com/redis/redis/8.10.1/src/sentinel.c
- Redis 8.10.1 cluster listeners, announcements, and mandatory TLS peer certificates: https://raw.githubusercontent.com/redis/redis/8.10.1/src/cluster_legacy.c
- Redis 8.10.1 peer-name enforcement and build opt-out: https://raw.githubusercontent.com/redis/redis/8.10.1/src/tls.c
- Replica ACL command requirements: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/#acl-rules-for-sentinel-and-replicas
- Persistent replica authentication: https://redis.io/docs/latest/operate/oss_and_stack/management/replication/#setting-a-replica-to-authenticate-to-a-master
- Sentinel incoming and peer authentication: https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#configuring-sentinel-instances-with-authentication
- Sentinel monitored-server ACL and channel requirements: https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/#redis-access-control-list-authentication
- Cluster data and bus networking: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/#redis-cluster-tcp-ports
- Sentinel TLS configuration: https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/#sentinel
- Redis 8.10 release notes and peer-name feature boundary: https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/release-notes/redisce/redisos-8.10-release-notes/
- Replication status fields: https://redis.io/docs/latest/commands/info/
- Cluster advertised addresses and bus ports: https://redis.io/docs/latest/commands/cluster-nodes/
