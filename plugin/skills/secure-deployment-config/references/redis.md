# Redis: TLS and authentication

Redis trusts its network by design, so the network boundary and credentials are your job. An exposed unauthenticated Redis leaks its data, and historic attack tooling has also used the CONFIG command against open instances to write files and take over hosts. Applies to Redis 6.0 and later (TLS and ACLs); the server must be built with TLS support, which mainstream distribution packages include (Redis refuses to start with TLS directives present if the build lacks it).

## 1. Keep it local unless remote access is deliberate

In `redis.conf`:

```
# Redis 6.2+: a "-" prefix makes the next address optional, so Redis still starts if that address is absent from local interfaces (an address already in use still fails startup).
# Redis 6.0 has no such prefix; there, use "bind 127.0.0.1" on the next line instead (redis.conf has no inline comments).
bind 127.0.0.1 -::1
protected-mode yes
```

`protected-mode` confines clients to the loopback interfaces and Unix sockets, but only while the default user still has its `nopass` flag and (on Redis 6.0/6.2) no explicit `bind` is configured; Redis 7.0 keeps the `nopass` condition and drops the `bind` one. On Redis 6.0/6.2, setting any explicit `bind` disables this protected-mode restriction; a wildcard bind such as `bind 0.0.0.0` then permits remote passwordless access while the default user remains `on nopass`, whereas a loopback-only `bind 127.0.0.1` still confines access to the local host. Treat it as a backstop for the unconfigured default, never as the control; the `bind` and credential below are the control.

## 2. Require a credential

Minimum (single shared password, sent by clients with `AUTH`):

```
requirepass REPLACE_WITH_LONG_RANDOM_PASSWORD
```

Better, per-service ACL users with least privilege (Redis 6 and later):

```
user app on >REPLACE_WITH_LONG_RANDOM_PASSWORD ~app:* +@read +@write -flushall -flushdb -swapdb
```

That grants the `app` user the read and write command categories, and `~app:*` restricts only the key arguments those commands take, to keys named `app:*`. It does not confine commands that take no key: `+@write` still includes `FLUSHALL` (clears every database), `FLUSHDB` (clears the current database), `SWAPDB` (swaps two databases), and, on Redis 7 and later, the FUNCTION write subcommands (`FUNCTION LOAD`, `FUNCTION DELETE`, `FUNCTION FLUSH`, `FUNCTION RESTORE`) that manage global libraries; `+@read` still includes keyspace-walking commands such as `KEYS`, `SCAN`, and `RANDOMKEY` that range outside `app:*`. The `-flushall -flushdb -swapdb` above removes those three commands only, not every keyless write (the FUNCTION write subcommands remain on Redis 7+), so for real least privilege allowlist only the commands the app uses, for example `~app:* +get +set`, and expand that list deliberately. Generate passwords per [authentication.md](authentication.md). The `default` user starts `on nopass ~* +@all` (Redis 6.2 adds `&*` for pub/sub channels), so with ACLs as your control you must secure it before any remote exposure: give it a strong password, or set `user default off resetpass` in `redis.conf` or the ACL file and apply it on a running server with `ACL SETUSER default off resetpass`. Do that only after every client authenticates as a named user (otherwise you lock services out), and note a connection already authenticated as `default` keeps working until it reconnects.

MFA: Redis has no second-factor dialogue. For machine clients, `tls-auth-clients yes` (mutual TLS, below) adds a possession factor (a certificate) alongside the password; that is stronger than a password alone but it is not MFA for a person. Human paths to the host go behind MFA per [mfa.md](mfa.md).

## 3. Enable TLS

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), then replace the plaintext port with a TLS listener:

```
# no plaintext listener at all
port 0
tls-port 6379
tls-cert-file    /etc/redis/tls/server.crt
tls-key-file     /etc/redis/tls/server.key
tls-ca-cert-file /etc/redis/tls/ca.crt
# Redis defaults to tls-auth-clients yes (require a client certificate = mutual TLS); the `no` below is a
# deliberate downgrade, safe here only because requirepass/ACL from section 2 is the control. Set `yes` for mTLS.
tls-auth-clients no
```

Set `tls-auth-clients yes` for machine-to-machine deployments where clients can hold certificates; it is stronger than passwords alone. With `yes`, clients must also pass `--cert client.crt --key client.key` (below), or the TLS handshake is rejected before any `AUTH`, and confirm that a missing or untrusted client certificate is refused.

## 4. Client side

```bash
redis-cli --tls --cacert /etc/redis/tls/ca.crt -h redis.example.com -p 6379
# with tls-auth-clients yes, also pass: --cert /etc/redis/tls/client.crt --key /etc/redis/tls/client.key
> AUTH app REPLACE_WITH_PASSWORD
> GET app:probe
```

`GET app:probe` is allowed by `~app:* +@read` (a `(nil)` reply is a success); `PING` sits in the `@connection` and `@fast` categories, which the ACL above does not grant, so it fails for `app`. Application clients take equivalent TLS and credential options; point them at the CA rather than disabling verification.

## 5. Verify

```bash
ss -tlnp   # read every listener; 6379: loopback only, unless remote access is deliberate
redis-cli -h redis.example.com ping           # any RESP reply (PONG, or a NOAUTH/error) means a plaintext listener is still open. With port 0 and tls-port 6379, TCP 6379 stays open as the TLS listener, so a plaintext client should get a protocol or connection error (reset or closed), not a RESP reply and not "Connection refused"; also confirm a CA-validated TLS connection to the same port succeeds. A name-resolution, timeout, or refused result alone is inconclusive
redis-cli --tls --cacert ca.crt -h redis.example.com ping   # NOAUTH until AUTH; with tls-auth-clients yes, add --cert/--key or the handshake is rejected first
```

## Common mistakes

- Commenting out `bind` (which listens everywhere) while `requirepass` is still empty.
- One `requirepass` value shared across environments and committed to the repository.
- TLS enabled but the plaintext `port` left open alongside it; set `port 0`.

## Valkey

Valkey, the community fork of Redis, uses the same `requirepass`, ACL, and TLS configuration described above without changes; apply this guide's steps directly. See [valkey.io](https://valkey.io/).

## Sources (checked September 2026)

- Redis documentation (security, TLS, and ACL pages): https://redis.io/docs/latest/
- redis.conf self-documented example in the Redis source distribution: https://github.com/redis/redis
- Redis configuration (directive format `keyword argument1 argument2 ... argumentN`): https://redis.io/docs/latest/operate/oss_and_stack/management/config/
- PING command reference (ACL categories `@fast`, `@connection`): https://redis.io/docs/latest/commands/ping/
- Valkey: https://valkey.io/
