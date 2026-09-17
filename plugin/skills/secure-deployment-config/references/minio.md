# MinIO: root credentials and TLS

MinIO serves S3-compatible object storage; an exposed instance with weak or well-known credentials hands over every bucket. Both the S3 API port and the web console need the same care.

Lifecycle note, as of September 2026: the MinIO community repository on GitHub was archived on 2026-04-25 and carries the notice that it is no longer maintained; MinIO now ships AIStor Free (a standalone edition under a free licence) and AIStor Enterprise. The settings below are documented for AIStor. An archived community build receives no security fixes, so treat running one as a finding and plan the migration.

## 1. Set real root credentials

```bash
export MINIO_ROOT_USER="REPLACE_WITH_ADMIN_NAME"
export MINIO_ROOT_PASSWORD="REPLACE_WITH_LONG_RANDOM_VALUE"
```

Never run with the `minioadmin`/`minioadmin` pair, which is still the built-in default when the root environment variables are unset; scanners try it constantly. Root credentials are for administration only: create per-application access keys with least-privilege policies (via the console or the `mc` client) so no app holds root ([authentication.md](authentication.md)).

## 2. Enable TLS

MinIO serves HTTPS automatically when it finds a PEM key pair named `public.crt` and `private.key` in `${HOME}/.minio/certs` (or the directory given with `--certs-dir`):

```bash
cp fullchain.pem "${HOME}/.minio/certs/public.crt"
cp privkey.pem   "${HOME}/.minio/certs/private.key"
```

Certificates per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md); clients then use `https://` endpoints and, for self-signed, trust the CA rather than disabling verification.

## 3. Exposure posture

MinIO's S3 API binds every interface by default: `--address` defaults to `:9000` (all IPv4 and IPv6 addresses), so a default install is reachable from any network the host is on, not loopback-only. Bind it explicitly with `--address 127.0.0.1:9000` (or a private address), and expose public access only via the TLS endpoints above or behind a proxy/tunnel ([nginx.md](nginx.md), [cloudflare.md](cloudflare.md)). The web console is a second listener, configured independently of the S3 API: MinIO serves its embedded console on the address set by `--console-address` (env `MINIO_CONSOLE_ADDRESS`), and left unset it picks a free port at startup and prints the console URL in its log. A console address with no host, whether the default or an explicit `:9001`, binds every interface even when the S3 API is bound to loopback, so the console can be reachable while the API is not. Bind it explicitly with `--console-address 127.0.0.1:9001` (or a private address), keep it off the public internet, and give human logins MFA at the fronting layer ([mfa.md](mfa.md)). Buckets are private unless a policy says otherwise; before exposing anything, inspect every bucket's full anonymous policy with `mc anonymous get-json ALIAS/BUCKET` (it covers download and upload grants and prefix conditions, none of which a read-only GET probe reaches) and remove any unintended anonymous access.

## 4. Verify

```bash
ss -tlnp   # read every listener; S3 API 9000 and the console (--console-address, ~9001); private unless deliberate
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/                     # service root: anonymous ListBuckets denied
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/ # per bucket: anonymous listing denied
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/REPLACE_WITH_PRIVATE_OBJECT
                                                       # a known private object: 403, never 200. Anonymous policies are set per
                                                       # bucket, so a denial at the service root does not prove any bucket is private
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9001/                     # console: probe the ACTUAL console port from ss above (or the startup-log URL), not a guessed 9001 (an unset --console-address picks a random port). Any response from outside, not only 200, means it is reachable; a refusal, timeout, or TLS error is NOT proof of isolation
mc alias set mys3 https://s3.example.com:9000 REPLACE_WITH_ACCESS_KEY REPLACE_WITH_SECRET_KEY   # credential/signature probe succeeds (mc validates the keys against the server); test the app's required operations separately. Root key stays unused by apps
```

## Sources (checked September 2026)

- MinIO network encryption (certs directory, public.crt/private.key, --certs-dir): https://docs.min.io/aistor/installation/linux/network-encryption/
- MinIO: https://www.min.io/
- MinIO community repository (archived 2026-04-25, successor editions): https://github.com/minio/minio
- MinIO `mc anonymous set` / `mc anonymous get-json` (anonymous policies are set per bucket or prefix, cover download and upload, and permit actions without authentication; get-json inspects the effective policy): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/
- MinIO/AIStor server address flags (`--address` defaults to `:9000` on all interfaces; `--console-address` / `MINIO_CONSOLE_ADDRESS`: a static port for the embedded console UI, or a dynamic one logged at startup when omitted): https://docs.min.io/aistor/reference/aistor-server/
- MinIO console listener in the server source (`--console-address` and its `MINIO_CONSOLE_ADDRESS` env var in `cmd/server-main.go`; `cmd/common-main.go` binds all interfaces when the host is omitted): https://github.com/minio/minio/blob/master/cmd/common-main.go
