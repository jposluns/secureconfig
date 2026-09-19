# Redis: TLS and authentication

Redis trusts its network by design, so the network boundary and credentials are your job. An exposed unauthenticated Redis leaks its data, and historic attack tooling has also used the CONFIG command against open instances to write files and take over hosts. Applies to Redis 6.0 and later for TLS and ACLs; the server and client must be built with TLS support. Additional controls below carry their minimum versions. See the [Redis security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/) and [TLS documentation](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/).

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

| Backlog ID | Outstanding demonstration | Status |
| --- | --- | --- |
| REDIS-LIVE-1 | In an isolated environment with Redis, TLS certificates, and socket access, record exact versions and demonstrate exposed/fixed listeners, plaintext rejection, authentication, ACL readback, actual CONFIG denial and ACL logging, directional key/channel checks, both persistence methods across restart, and old-user session revocation. Parse the applicable configuration examples with the real Redis server. | Open; REASONED checks above remain un demonstrated. |

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
