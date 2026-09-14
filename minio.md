# MinIO: root credentials and TLS

MinIO serves S3-compatible object storage; an exposed instance with weak or well-known credentials hands over every bucket. Both the S3 API port and the web console need the same care.

Lifecycle note, as of September 2026: the MinIO community repository on GitHub was archived on 2026-04-25 and carries the notice that it is no longer maintained; MinIO now ships AIStor Free (a standalone edition under a free licence) and AIStor Enterprise. The settings below are documented for AIStor. An archived community build receives no security fixes, so treat running one as a finding and plan the migration.

## 1. Set real root credentials

```bash
export MINIO_ROOT_USER="REPLACE_WITH_ADMIN_NAME"
export MINIO_ROOT_PASSWORD="REPLACE_WITH_LONG_RANDOM_VALUE"
```

Never run with the historic `minioadmin`/`minioadmin` pair; scanners try it constantly. Root credentials are for administration only: create per-application access keys with least-privilege policies (via the console or the `mc` client) so no app holds root ([authentication.md](authentication.md)).

## 2. Enable TLS

MinIO serves HTTPS automatically when it finds a PEM key pair named `public.crt` and `private.key` in `${HOME}/.minio/certs` (or the directory given with `--certs-dir`):

```bash
cp fullchain.pem "${HOME}/.minio/certs/public.crt"
cp privkey.pem   "${HOME}/.minio/certs/private.key"
```

Certificates per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md); clients then use `https://` endpoints and, for self-signed, trust the CA rather than disabling verification.

## 3. Exposure posture

Loopback or private networks by default; public access only via the TLS endpoints above or behind a proxy/tunnel ([nginx.md](nginx.md), [cloudflare.md](cloudflare.md)). The web console is a second listener: MinIO serves its embedded console on the port set by `--console-address` (env `MINIO_CONSOLE_ADDRESS`), conventionally `:9001`, and left unset MinIO assigns it one at startup and prints the console URL in its log. The console binds the same interfaces as the S3 API, so exposing the API exposes the console too. Pin `--console-address :9001` so the port is known and can be filtered, keep the console off the public internet, and give human logins MFA at the fronting layer ([mfa.md](mfa.md)). Buckets are private unless a policy says otherwise; audit anonymous/public bucket policies before exposing anything.

## 4. Verify

```bash
ss -tlnp | grep -E ':(9000|9001) '                     # S3 API 9000 and the console (--console-address, ~9001); private unless deliberate
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/                     # service root: anonymous ListBuckets denied
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/ # per bucket: anonymous listing denied
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/REPLACE_WITH_PRIVATE_OBJECT
curl -q -s -o /dev/null -w '%{http_code}\n' https://s3.example.com:9001/                     # the console on 9001: a 200 from outside means the console is publicly reachable
                                                       # a known private object: 403, never 200. Anonymous policies are set per
                                                       # bucket, so a denial at the service root does not prove any bucket is private
mc alias set mys3 https://s3.example.com:9000 REPLACE_WITH_ACCESS_KEY REPLACE_WITH_SECRET_KEY   # app key works; root key stays unused by apps
```

## Sources (checked September 2026)

- MinIO network encryption (certs directory, public.crt/private.key, --certs-dir): https://docs.min.io/aistor/installation/linux/network-encryption/
- MinIO: https://www.min.io/
- MinIO community repository (archived 2026-04-25, successor editions): https://github.com/minio/minio
- MinIO `mc anonymous set` (anonymous policies are set per bucket and permit actions without authentication): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/
