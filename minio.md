# MinIO: credentials, TLS, encryption, and object protection

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

MinIO's S3 API binds every interface by default: `--address` defaults to `:9000` (all IPv4 and IPv6 addresses), so a default install is reachable from any network the host is on, not loopback-only. Bind it explicitly with `--address 127.0.0.1:9000` (or a private address), and expose public access only via the TLS endpoints above or behind a proxy/tunnel ([nginx.md](nginx.md), [cloudflare.md](cloudflare.md)). The web console is a second listener, configured independently of the S3 API: MinIO serves its embedded console on the address set by `--console-address` (env `MINIO_CONSOLE_ADDRESS`), and left unset it picks a free port at startup and prints the console URL in its log. A console address with no host, whether the default or an explicit `:9001`, binds every interface even when the S3 API is bound to loopback, so the console can be reachable while the API is not. Bind it explicitly with `--console-address 127.0.0.1:9001` (or a private address), keep it off the public internet, and give human logins MFA at the fronting layer ([mfa.md](mfa.md)). Buckets are private unless a policy says otherwise; before exposing anything, inspect every bucket's full anonymous policy with `mc anonymous get-json ALIAS/BUCKET` (it shows the download and upload grants, resource prefixes, and conditions; the GET probes below cannot audit upload permissions or untested objects and prefixes) and remove any unintended anonymous access.

## 4. Create scoped application access

A leaked application key should expose only the application's required objects and operations. Give each application a non-root parent user and its own expiring access key. The built-in `readonly`, `writeonly`, `readwrite`, and `consoleAdmin` policies are broad: the first two allow their respective object operations across the deployment, `readwrite` grants every S3 action, and `consoleAdmin` also grants administrative access. `readonly` does not grant bucket listing.

Create the parent user through the Console's IAM Users screen. The documented `mc admin user add` CLI requires a positional secret and has no stdin secret form, so do not use it to put a password in argv. Give the parent only the required policies; review group memberships too.

Save this custom policy as `/path/to/REPLACE_WITH_APP_POLICY.json`, substituting the same bucket name in both resource entries. It permits bucket listing and object reads and writes in one bucket, with no deletion or administrative grants. Remove any action the application does not need.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::REPLACE_WITH_APP_BUCKET"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": ["arn:aws:s3:::REPLACE_WITH_APP_BUCKET/*"]
    }
  ]
}
```

Configure the administrative alias `mys3` using the stdin import in section 8 before running these commands. Choose an unused policy name and a new output file in an owner-only directory; creating an existing policy name replaces its policy.

```bash
mc admin policy create mys3 app-bucket /path/to/REPLACE_WITH_APP_POLICY.json
mc admin policy attach mys3 app-bucket --user REPLACE_WITH_APP_USER
(
  umask 077
  mc admin accesskey create mys3/ REPLACE_WITH_APP_USER \
    --policy /path/to/REPLACE_WITH_APP_POLICY.json \
    --expiry-duration 24h > /path/to/REPLACE_WITH_NEW_ACCESSKEY_OUTPUT.txt
)
```

The explicit parent username prevents accidentally creating a child of the administrative identity. Omitting the access-key and secret-key options lets AIStor generate the pair. The output contains credentials: transfer them through your secret-management workflow, restrict the file to its owner, and keep it out of logs and version control. Populate the application's alias JSON from that pair using the format in section 8; the creation output is not itself an alias-import document.

The `--policy` document is an inline restriction on the parent's permissions, not an independent grant. It cannot expand access beyond the parent's user and group policies, and its maximum size is 4096 bytes. Check the size after substitution. Arrange rotation before the example's 24-hour expiry; retire the old key through the Console after the application switches.

Identity policies and anonymous bucket policies are separate controls. Review both: a scoped key does not remove an anonymous grant on another bucket.

## 5. Encrypt stored data with a key manager

Stolen storage should not yield readable object data or backend credentials. SSE-S3 uses the deployment's default external key; SSE-KMS supports a selected key for a bucket or write request. Both require a configured key manager. Server-side encryption does not replace TLS or access policy.

Use MinIO KMS for new deployments. KES is the supported legacy integration with an external third-party KMS. Configure exactly one of these alternatives in the protected server environment file on every node, normally `/etc/default/minio`. These are file contents, not command-line arguments. Provision the named keys and authorized identities first, trust the key manager's CA, and restart AIStor after applying the settings.

For MinIO KMS, use the actual endpoint, enclave, default key name, and complete API key issued for the enclave identity:

```dotenv
MINIO_KMS_SERVER="https://kms.example.com:7373"
MINIO_KMS_ENCLAVE="REPLACE_WITH_ENCLAVE"
MINIO_KMS_SSE_KEY="REPLACE_WITH_EXISTING_DEFAULT_KEY_NAME"
MINIO_KMS_API_KEY="REPLACE_WITH_KMS_API_KEY"
MINIO_KMS_AUTO_ENCRYPTION="on"
```

For an existing KES integration, the certificate-based alternative is:

```dotenv
MINIO_KMS_KES_ENDPOINT="https://kes.example.com:7373"
MINIO_KMS_KES_KEY_NAME="REPLACE_WITH_EXISTING_DEFAULT_KEY_NAME"
MINIO_KMS_KES_CERT_FILE="/etc/minio/kes/client.crt"
MINIO_KMS_KES_KEY_FILE="/etc/minio/kes/client.key"
MINIO_KMS_KES_CAPATH="/etc/minio/kes/ca.crt"
MINIO_KMS_AUTO_ENCRYPTION="on"
```

Keep the MinIO KMS and KES configurations mutually exclusive. Within KES, the certificate and private-key settings must be supplied together and are mutually exclusive with `MINIO_KMS_KES_API_KEY`. `MINIO_KMS_KES_CAPATH` identifies the CA certificate used to validate the KES server when needed. Protect the API key, client private key, and environment file.

`MINIO_KMS_AUTO_ENCRYPTION` defaults to `on` when a key manager is configured, automatically encrypting new object writes using SSE-KMS. An unconfigured installation does not acquire encryption merely because this default exists. Setting it to `off` disables that automatic object encryption; configure bucket encryption explicitly if doing so.

Choose the required bucket default. For SSE-KMS with an existing key:

```bash
mc encrypt set sse-kms REPLACE_WITH_EXISTING_BUCKET_KEY_NAME mys3/REPLACE_WITH_BUCKET
```

Alternatively, use SSE-S3 with the deployment's default key:

```bash
mc encrypt set sse-s3 mys3/REPLACE_WITH_BUCKET
```

Enabling SSE also encrypts backend data, including IAM and configuration data. Backend encryption cannot be disabled or reset, and normal startup then depends on access to the key manager and the backend key. Preserve that key and test key-manager recovery; changing the automatic-object-encryption setting does not remove this dependency.

Bucket encryption settings affect subsequent writes. They do not rewrite or establish the encryption state of historical objects; inspect existing versions and plan any required migration separately.

## 6. Protect object versions from deletion

Versioning preserves older writes, but an identity with deletion rights can still remove individual versions. Object locking adds retention to protect those versions.

For a new bucket, enable locking and set a default retention period:

```bash
mc mb --with-lock mys3/REPLACE_WITH_NEW_BUCKET
mc retention set --default GOVERNANCE 30d mys3/REPLACE_WITH_NEW_BUCKET
```

`--with-lock` also enables versioning; it does not itself set a retention period. Choose `GOVERNANCE` or `COMPLIANCE` and an `Nd` duration, such as `30d`, according to the required protection.

AIStor `RELEASE.2025-05-20T20-30-00Z` or later can enable object locking on an existing bucket. Enable versioning first if necessary, then set default retention:

```bash
mc version enable mys3/REPLACE_WITH_EXISTING_BUCKET
mc retention set --default GOVERNANCE 30d mys3/REPLACE_WITH_EXISTING_BUCKET
```

The Console does not support this retrofit. Older releases required locking at bucket creation; that is not a blanket limitation of current AIStor.

`GOVERNANCE` permits authorized bypass. Keep `s3:BypassGovernanceRetention` off application identities and their inherited policies. `COMPLIANCE` prevents deletion of the protected version even by root until retention expires; choose its period before applying it.

`--default` ignores the other flags, including `--recursive`, and supplies retention for new objects without an explicit override. It does not protect historical versions. Apply retention to each required existing version and inspect its resulting retain-until date, especially for older data:

```bash
mc retention set --version-id REPLACE_WITH_VERSION_ID GOVERNANCE 30d \
  mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_OBJECT
mc legalhold set --version-id REPLACE_WITH_VERSION_ID \
  mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_OBJECT
```

The second command adds an indefinite legal hold. Only an identity with `s3:PutObjectLegalHold` can set or lift it; keep that permission restricted. A version with both protections remains locked until retention has expired and the legal hold has been lifted.

An ordinary delete can still create a delete marker that hides the object from an unversioned read. Verify the retained version by its exact version ID.

## 7. Publish audit logs outside the object store

Without an independent audit trail, misuse can leave no durable record outside the affected deployment. AIStor publishes no audit logs by default. Configure a remote receiver and protect its authentication, storage, and administrative access; records can contain sensitive request details, hostnames, IP addresses, object names, and headers.

For an authenticated HTTPS webhook, add these settings to the protected server environment file on every node:

```dotenv
MINIO_AUDIT_WEBHOOK_ENABLE="on"
MINIO_AUDIT_WEBHOOK_ENDPOINT="https://audit.example.com/minio/events"
MINIO_AUDIT_WEBHOOK_AUTH_TOKEN="Bearer REPLACE_WITH_RECEIVER_TOKEN"
MINIO_AUDIT_WEBHOOK_TLS_SKIP_VERIFY="false"
MINIO_AUDIT_QUEUE_DIR="/var/lib/minio/audit-queue"
```

The authentication value is sent as supplied; include `Bearer` only when the receiver expects that scheme. Trust the receiver's CA and keep TLS certificate verification enabled.

Alternatively, configure an authenticated Kafka target with credentials limited to the audit topic:

```dotenv
MINIO_AUDIT_KAFKA_ENABLE="on"
MINIO_AUDIT_KAFKA_BROKERS="kafka.example.com:9093"
MINIO_AUDIT_KAFKA_TOPIC="minio-audit"
MINIO_AUDIT_KAFKA_TLS="on"
MINIO_AUDIT_KAFKA_TLS_SKIP_VERIFY="false"
MINIO_AUDIT_KAFKA_SASL="on"
MINIO_AUDIT_KAFKA_SASL_USERNAME="REPLACE_WITH_AUDIT_PRODUCER"
MINIO_AUDIT_KAFKA_SASL_PASSWORD="REPLACE_WITH_KAFKA_PASSWORD"
MINIO_AUDIT_KAFKA_SASL_MECHANISM="plain"
MINIO_AUDIT_QUEUE_DIR="/var/lib/minio/audit-queue"
```

Use the broker's actual TLS listener and supported SASL mechanism. Kafka TLS defaults to `off`, so enable it explicitly; the example uses SASL PLAIN only over verified TLS.

For either target, provision `MINIO_AUDIT_QUEUE_DIR` on persistent storage on each node. The AIStor service account needs read, write, and directory-listing access; restrict other access. Restart AIStor to apply the environment settings.

AIStor retries failed delivery, but events can be permanently lost when the queue fills. Monitor receiver availability, queue capacity, and delivery failures. A webhook 2xx means the receiver acknowledged the request; it does not prove durable storage, and AIStor cannot recover an acknowledged event that the receiver failed to store. Keep receiver retention and deletion rights independent of application access to the object store.

## 8. Verify

Substitute deployment-specific values and use harmless private fixtures. Run checks in stages, confirming every expected-success operation before interpreting a denial. A timeout, TLS failure, invalid credential, missing object, or proxy-generated error is not evidence that the intended security control worked.

REASONED in this authoring environment: the existing probes below are retained, but their live outcomes were not demonstrated here. There is no `minio` or `mc` binary, container runtime, deployed KMS, or audit receiver available for these checks.

Prepare `/path/to/REPLACE_WITH_ADMIN_ALIAS.json` as an owner-only credential file with these fields:

```json
{
  "url": "https://s3.example.com:9000",
  "accessKey": "REPLACE_WITH_ACCESS_KEY",
  "secretKey": "REPLACE_WITH_SECRET_KEY",
  "api": "s3v4",
  "path": "auto"
}
```

Use root credentials in `mys3` only for the administrative comparisons below. Protect both the imported file and the resulting local `mc` configuration. Importing an alias is configuration, not proof of working authentication; confirm signed operations against MinIO's own endpoint.

```bash
ss -tlnp   # read every listener; S3 API 9000 and the console (--console-address, ~9001); private unless deliberate
curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' https://s3.example.com:9000/                     # service root: anonymous ListBuckets denied
curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/ # per bucket: anonymous listing denied
curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' https://s3.example.com:9000/REPLACE_WITH_BUCKET/REPLACE_WITH_PRIVATE_OBJECT
                                                       # a known private object: 403, never 200, and the 403 must come from MinIO (behind a proxy a 403 may be the proxy's, so probe MinIO's direct origin). Anonymous policies are set per
                                                       # bucket, so a denial at the service root does not prove any bucket is private
curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' https://s3.example.com:9001/                     # console: probe the ACTUAL console port from ss above (or the startup-log URL), not a guessed 9001 (an unset --console-address picks a random port). Any response from outside, not only 200, means it is reachable; a refusal, timeout, or TLS error is NOT proof of isolation
mc alias import mys3 < /path/to/REPLACE_WITH_ADMIN_ALIAS.json
```

For the exposure probes, an anonymous grant can produce successful listing or object reads; the private configuration must deny those operations at MinIO itself. Inspect every full anonymous policy as described in section 3, including upload grants. Listener inspection and probes from the relevant external network are both needed to assess console exposure. Sources: server address flags and anonymous-policy references below.

**Scoped access, REASONED:** no `minio`, `mc`, or container runtime is available here. Prepare two different buckets containing known, harmless private objects. The application's policy must name only the application bucket. Build the app alias JSON with the generated scoped key and the same endpoint, `api`, and `path` fields as above.

```bash
mc alias import app < /path/to/REPLACE_WITH_APP_ALIAS.json
mc anonymous get-json mys3/REPLACE_WITH_APP_BUCKET
mc anonymous get-json mys3/REPLACE_WITH_OTHER_BUCKET
mc cat mys3/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT
mc cat mys3/REPLACE_WITH_OTHER_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT
mc cat app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT
printf '%s\n' 'scoped write probe' | mc pipe app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_UNIQUE_PROBE_OBJECT
mc cat app/REPLACE_WITH_OTHER_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT
```

Confirm the policy reviews exclude anonymous access to both fixtures. Root must read both known objects. The scoped key must read its own fixture and write its probe, but MinIO must deny its read of the other bucket's known object. A root or overly broad application key would read both. A generic denial alone is insufficient: the successful reads establish the objects, endpoint, and working credentials. Sources: access management, access-key creation, `mc cat`, and `mc pipe`.

**Encryption, REASONED:** no `minio`, `mc`, or KMS is available here. After configuring a working key manager and the intended bucket default, write a new object without a client encryption override:

```bash
mc encrypt info mys3/REPLACE_WITH_BUCKET
printf '%s\n' 'encryption probe' | mc pipe mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_NEW_ENCRYPTION_PROBE
mc stat mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_NEW_ENCRYPTION_PROBE
```

Confirm the bucket default and the newly written object's SSE metadata, including the intended KMS key for SSE-KMS. In a disposable unencrypted comparison deployment with no key manager, a successful ordinary write lacks SSE metadata; after the control is configured, the new write must carry it. A failed write proves neither state. `mc encrypt info` reports bucket configuration, not historical-object encryption, and absence of a bucket rule does not prove plaintext when server-wide automatic encryption applies. Sources: `mc encrypt info`, `mc encrypt set`, `mc stat`, and the MinIO KMS setup guide.

**Retention, REASONED:** no `minio`, `mc`, or container runtime is available here. Use a newly created disposable bucket with locking enabled and no default retention. Stop if creation or either write fails. These fixtures compare an unlocked version with a protected version under the same root identity.

```bash
mc mb --with-lock mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET
printf '%s\n' 'unlocked control' | mc pipe mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
printf '%s\n' 'retained probe' | mc pipe mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc stat mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
mc stat mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
```

Record the exact version IDs from the successful object inspections. Substitute them below. The protected fixture receives a one-day COMPLIANCE lock and cannot be deleted early, including by root.

```bash
mc retention set --version-id REPLACE_WITH_PROTECTED_VERSION COMPLIANCE 1d \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc retention info --version-id REPLACE_WITH_PROTECTED_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc stat --version-id REPLACE_WITH_CONTROL_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
mc rm --version-id REPLACE_WITH_CONTROL_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
mc stat --version-id REPLACE_WITH_CONTROL_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
mc rm --version-id REPLACE_WITH_PROTECTED_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc stat --version-id REPLACE_WITH_PROTECTED_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc retention info --version-id REPLACE_WITH_PROTECTED_VERSION \
  mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
```

Before deletion, confirm the protected version has COMPLIANCE retention with a future retain-until date and the control version exists. Deleting the unlocked control must succeed, and its subsequent inspection must report that specific version absent. Deleting the protected version must fail, while its subsequent inspection and retention query must still succeed for the same version ID. If both deletes fail, the test has not isolated retention. A delete marker or an unversioned read does not establish whether the retained version survived. Sources: object locking, `mc mb`, `mc retention set`, `mc retention info`, `mc rm`, and `mc stat`.

**Audit delivery, REASONED:** no `minio`, `mc`, or audit receiver is available here. After enabling the chosen target and restarting AIStor, use a unique object name and record the test time. Reuse the proven private object in the forbidden bucket for the denied request.

```bash
printf '%s\n' 'audit delivery probe' | mc pipe app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_UNIQUE_AUDIT_OBJECT
mc cat app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_UNIQUE_AUDIT_OBJECT
mc cat app/REPLACE_WITH_OTHER_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT
```

Query the receiver's persisted records for the matching bucket, object, operation, time, identity, status, and request ID. Confirm records for both the successful operations and the denied read, and confirm they remain available from durable storage, for example after restarting the receiver. With no target configured, these S3 requests can complete without any external audit record. With delivery configured, the matching records must actually be stored at the receiver. An S3 200 proves nothing about logging; a webhook 2xx proves only acknowledgement. Sources: audit logging, webhook delivery, and Kafka delivery.

Backlog row (open): demonstrate the exposure probes and all four service checks against exposed and fixed states on live AIStor with `mc`, a KMS, and an independent durable audit receiver; record versions, commands, outcomes, and receiver evidence. These capabilities were unavailable in the authoring environment.

## Sources (checked September 2026)

- MinIO network encryption (certs directory, public.crt/private.key, --certs-dir): https://docs.min.io/aistor/installation/linux/network-encryption/
- MinIO: https://www.min.io/
- MinIO community repository (archived 2026-04-25, successor editions): https://github.com/minio/minio
- MinIO `mc anonymous set` (anonymous policies are set per bucket or prefix, cover download and upload, and permit actions without authentication): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/
- MinIO `mc anonymous get-json` (retrieve a bucket's anonymous policy as JSON to inspect grants, prefixes, and conditions): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-get-json/
- MinIO/AIStor server address flags (`--address` defaults to `:9000` on all interfaces; `--console-address` / `MINIO_CONSOLE_ADDRESS`: a static port for the embedded console UI, or a dynamic one logged at startup when omitted): https://docs.min.io/aistor/reference/aistor-server/
- MinIO console listener in the server source (`--console-address` and its `MINIO_CONSOLE_ADDRESS` env var in `cmd/server-main.go`; `cmd/common-main.go` binds all interfaces when the host is omitted): https://github.com/minio/minio/blob/master/cmd/common-main.go
- AIStor identity and access management (root defaults and child access keys): https://docs.min.io/aistor/administration/iam/
- AIStor Console security and access (user creation and key rotation): https://docs.min.io/aistor/administration/console/security-and-access/
- AIStor access management (built-in policies, custom policy structure, actions, and resources): https://docs.min.io/aistor/administration/iam/access/
- AIStor `mc admin user add` (positional secret): https://docs.min.io/aistor/reference/cli/admin/mc-admin-user/mc-admin-user-add/
- AIStor `mc admin policy create`: https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-create/
- AIStor `mc admin policy attach`: https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-attach/
- AIStor `mc admin accesskey create` (parent, generated credentials, expiry duration, and inline-policy limit): https://docs.min.io/aistor/reference/cli/admin/mc-admin-accesskey/mc-admin-accesskey-create/
- AIStor `mc alias import` (stdin and JSON fields): https://docs.min.io/aistor/reference/cli/mc-alias/mc-alias-import/
- AIStor server-side encryption (SSE types and key-manager choices): https://docs.min.io/aistor/installation/linux/server-side-encryption/
- AIStor encryption settings (MinIO KMS, KES credentials, and conditional automatic encryption): https://docs.min.io/aistor/reference/aistor-server/settings/server-side-encryption/
- AIStor MinIO KMS setup (environment settings, backend dependency, and object verification): https://docs.min.io/aistor/installation/linux/server-side-encryption/aistor-keymanager/
- AIStor KES setup (external KMS, backend IAM/configuration encryption, and startup dependency): https://docs.min.io/aistor/installation/linux/server-side-encryption/minio-key-encryption-service/
- AIStor `mc encrypt set` (SSE-KMS key selection, SSE-S3, and historical objects): https://docs.min.io/aistor/reference/cli/mc-encrypt/mc-encrypt-set/
- AIStor `mc encrypt info`: https://docs.min.io/aistor/reference/cli/mc-encrypt/mc-encrypt-info/
- AIStor object locking (existing buckets, Console limitation, retention modes, and delete markers): https://docs.min.io/aistor/administration/object-locking-and-immutability/
- AIStor `mc mb` (`--with-lock` enables versioning without setting retention): https://docs.min.io/aistor/reference/cli/mc-mb/
- AIStor `mc version enable`: https://docs.min.io/aistor/reference/cli/mc-version/mc-version-enable/
- AIStor `mc retention set` (default retention, existing buckets, ignored flags, and version IDs): https://docs.min.io/aistor/reference/cli/mc-retention/mc-retention-set/
- AIStor `mc retention info`: https://docs.min.io/aistor/reference/cli/mc-retention/mc-retention-info/
- AIStor `mc legalhold set`: https://docs.min.io/aistor/reference/cli/mc-legalhold/mc-legalhold-set/
- AIStor `mc rm` (specific-version deletion): https://docs.min.io/aistor/reference/cli/mc-rm/
- AIStor `mc stat` (metadata and specific-version inspection): https://docs.min.io/aistor/reference/cli/mc-stat/
- AIStor `mc cat`: https://docs.min.io/aistor/reference/cli/mc-cat/
- AIStor `mc pipe`: https://docs.min.io/aistor/reference/cli/mc-pipe/
- AIStor audit logging (no default destination, queue loss, persistent queue, and event fields): https://docs.min.io/aistor/operations/monitoring/audit-logging/
- AIStor webhook audit settings (authentication and certificate verification): https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/webhook-audit-logs/
- AIStor webhook audit delivery (environment settings and acknowledgement limits): https://docs.min.io/aistor/operations/monitoring/audit-logging/webhook-audit-logging/
- AIStor Kafka audit settings (TLS defaults off and SASL authentication): https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/kafka-audit-logs/
- AIStor Kafka audit delivery (environment settings and restart): https://docs.min.io/aistor/operations/monitoring/audit-logging/kafka-audit-logging/
- AIStor global audit event queue: https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/audit-event-queue/
