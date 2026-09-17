# Redis: TLS and authentication

Redis trusts its network by design, so the network boundary and credentials are your job. An exposed unauthenticated Redis leaks its data, and historic attack tooling has also used the CONFIG command against open instances to write files and take over hosts. Applies to Redis 6.0 and later (TLS and ACLs); the server must be built with TLS support, which mainstream distribution packages include (Redis refuses to start with TLS directives present if the build lacks it).

## 1. Keep it local unless remote access is deliberate

In `redis.conf`:

```
bind 127.0.0.1 -::1                 # the "-" (optional address) needs Redis 6.2+; on 6.0 use "bind 127.0.0.1"
protected-mode yes
```

`protected-mode` restricts Redis to loopback clients only when Redis is on its default with no explicit `bind` AND no password/ACL is set; setting any explicit `bind`, even `bind 0.0.0.0`, takes the instance out of that protection (Redis 7.0 drops the no-explicit-bind condition but still only guards a passwordless default). Treat it as a backstop for the unconfigured default, never as the control; the `bind` and credential below are the control.

## 2. Require a credential

Minimum (single shared password, sent by clients with `AUTH`):

```
requirepass REPLACE_WITH_LONG_RANDOM_PASSWORD
```

Better, per-service ACL users with least privilege (Redis 6 and later):

```
user app on >REPLACE_WITH_LONG_RANDOM_PASSWORD ~app:* +@read +@write -flushall -flushdb -swapdb
```

That grants the `app` user read and write commands scoped to keys matching `app:*`. Key patterns do not constrain commands that take no key argument, so `+@write` otherwise includes `FLUSHALL`, `FLUSHDB`, and `SWAPDB`, which wipe every database regardless of `~app:*`; the rule removes them explicitly. Generate passwords per [authentication.md](authentication.md). The `default` user starts `nopass ~* &* +@all`, so with ACLs as your control you must secure it before any remote exposure: give it a strong password or run `user default off resetpass`. Do that only after every client authenticates as a named user (otherwise you lock services out), and note a connection already authenticated as `default` keeps working until it reconnects.

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
redis-cli -h redis.example.com ping           # over plaintext, ANY reply (PONG, or a NOAUTH/error) means the plaintext port is still open; a "Connection refused" once port 0 is set is the pass, while a name-resolution or timeout failure is inconclusive, not a pass
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
