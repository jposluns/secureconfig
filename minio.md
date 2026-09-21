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

### 3.1. Disable the embedded Console when unnecessary

Once Console-based setup is complete, disable the embedded Console if administration uses `mc` or other API clients. Add this to the protected server environment file on every node and restart AIStor:

```dotenv
MINIO_BROWSER="off"
```

`MINIO_BROWSER_REDIRECT` controls automatic browser redirection to the Console; disabling redirection does not disable the Console. Use `MINIO_BROWSER` for that control. Source: [AIStor Console settings](https://docs.min.io/aistor/reference/aistor-server/settings/console/).

### 3.2. Set a workload-sized API concurrency budget

The automatic request budget is based on available host RAM. If it exceeds what the deployment's storage, CPU, or workload can sustain, configure an explicit value in the server environment on every node and restart AIStor:

```dotenv
MINIO_API_REQUESTS_MAX="64"
```

This is a cluster-wide budget for concurrent S3 and administrative API requests, divided among the nodes. For example, 64 across four nodes gives a request pool of 16 per node. It is neither requests per second nor a TCP-connection limit. The number is an illustrative workload-sizing choice, not a recommendation: measure representative workloads before selecting it. Source: [AIStor core settings](https://docs.min.io/aistor/reference/aistor-server/settings/core/).

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

### 4.1. Map OIDC identities to scoped policies

Authentication does not establish an appropriate authorization boundary. With role-policy mapping, every authentication request using the provider's `RoleArn` receives the configured policies. Assigning a broad policy therefore spreads that access across the identities using that role. Source: [AIStor OIDC access management](https://docs.min.io/aistor/administration/iam/access/oidc-access/).

For an already configured OIDC provider, choose exactly one mapping method. Remove the other method's explicit settings from both the environment and stored configuration; configuring both `role_policy` and `claim_name` is an error. Apply consistent settings across nodes and restart AIStor. Source: [AIStor OIDC identity management](https://docs.min.io/aistor/administration/iam/identity/oidc-identity/).

Use role-policy mapping only when every identity admitted through that role should receive the section 4 application's access:

```dotenv
MINIO_IDENTITY_OPENID_ROLE_POLICY="app-bucket"
```

The `app-bucket` policy must already exist with the intended bucket substitutions. Clients must supply the provider's corresponding `RoleArn` in their STS request. Source: [AIStor OpenID settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/).

Alternatively, select claim mapping when identities need different policies:

```dotenv
MINIO_IDENTITY_OPENID_CLAIM_NAME="policy"
```

Configure the IdP to issue `"policy": "app-bucket"` only for identities entitled to that policy; other identities receive their own existing, narrowly scoped policy names. Treat this claim as an authorization decision controlled by the IdP administrator. A user without an assigned policy has no access. Sources: [AIStor OpenID settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/), [OIDC identity management](https://docs.min.io/aistor/administration/iam/identity/oidc-identity/), and [OIDC access management](https://docs.min.io/aistor/administration/iam/access/oidc-access/).

Do not describe a short `MINIO_STS_DURATION` as a universal maximum. `AssumeRoleWithWebIdentity` accepts explicit `DurationSeconds` values from 900 through 31536000 seconds (365 days); with a usable JWT expiry, an explicit duration takes precedence over that expiry. `MINIO_STS_DURATION` is a default, not this ceiling. AIStor separately documents the native `sts:DurationSeconds` policy condition for restricting WebIdentity credential duration. Sources: [AssumeRoleWithWebIdentity](https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/), [STS settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/sts/), and [access-management condition keys](https://docs.min.io/aistor/administration/iam/access/).

### 4.2. Shorten presigned URLs and cap signature age

A presigned download URL contains access credentials: possession permits its authorized download even when the bucket is private. Generate it with the scoped `app` identity and a short expiry. Save the output in a new file inside an owner-only directory, and share the URL through a protected channel:

```bash
(
  umask 077
  set -C
  mc share download --expire 5m \
    app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT \
    > /path/to/REPLACE_WITH_NEW_SHARE_OUTPUT.txt
)
```

The example requests five minutes instead of `mc share download`'s default seven days. Keep the output out of logs and version control. Source: [AIStor `mc share download`](https://docs.min.io/aistor/reference/cli/mc-share/mc-share-download/).

Add a server-enforced policy restriction as well. AIStor documents support for `s3:signatureAge` and AWS-compatible policy evaluation. The following example uses the referenced S3 semantics: 600000 milliseconds is ten minutes, and `NumericGreaterThan` matches an older signature. Its expected AIStor behaviour remains subject to the REASONED comparison below. Sources: [AIStor access management](https://docs.min.io/aistor/administration/iam/access/) and the supplementary [S3 signature-condition reference](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/bucket-policy-s3-sigv4-conditions.html).

Save this as `/path/to/REPLACE_WITH_SIGNATURE_AGE_POLICY.json`, substituting the section 4 bucket name:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::REPLACE_WITH_APP_BUCKET",
        "arn:aws:s3:::REPLACE_WITH_APP_BUCKET/*"
      ],
      "Condition": {
        "NumericGreaterThan": {
          "s3:signatureAge": "600000"
        }
      }
    }
  ]
}
```

Choose an unused policy name; creating an existing name overwrites its policy. Attach the restriction to the existing non-root application parent user, retaining its `app-bucket` grant:

```bash
mc admin policy create mys3 app-signature-age /path/to/REPLACE_WITH_SIGNATURE_AGE_POLICY.json
mc admin policy attach mys3 app-signature-age --user REPLACE_WITH_APP_USER
```

Sources: [AIStor `mc admin policy create`](https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-create/) and [`mc admin policy attach`](https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-attach/).

A matching explicit deny overrides an allow. This attachment restricts the governed application identity and its inherited access on the named resources; it is not a deployment-wide ban on older presigned URLs. It does not attach the restriction to unrelated identities or OIDC roles, or remove anonymous grants. Review those separately. Source: [AIStor access management](https://docs.min.io/aistor/administration/iam/access/).

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

**OIDC authorization, REASONED:** no live AIStor deployment, configured IdP, or authenticated S3 test client is available here. Use two known private fixtures, one in the application bucket and one outside it, and establish administrative reads of both.

Through an STS-capable SDK client, call `AssumeRoleWithWebIdentity` with `Version=2011-06-15`, a valid `WebIdentityToken`, and the configured `RoleArn` for role-policy mapping; omit `RoleArn` for claim mapping. Load tokens and returned credentials from protected storage, not command-line arguments or logs. Using the returned access key, secret key, and session token, issue `GetObject` for both fixtures.

In a disposable broad-policy comparison, both reads succeed. After applying `app-bucket` mapping and obtaining fresh credentials, the application read must succeed and the other read must be denied by AIStor. For claim mapping, also test an identity without a mapped policy: it must gain no object access. A failed login alone does not demonstrate scoped authorization. Sources: [AIStor OIDC access management](https://docs.min.io/aistor/administration/iam/access/oidc-access/) and [AssumeRoleWithWebIdentity](https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/).

For the duration caveat, use a valid JWT expiring in approximately 20 minutes, `MINIO_STS_DURATION=15m`, and an explicit `DurationSeconds=3600` in a disposable deployment without an additional duration-restricting policy. Inspect the returned expiration and repeat the permitted read after JWT expiry but before STS expiry. The documented expectation is credentials lasting approximately one hour, despite the shorter default and JWT lifetime. This demonstrates the limitation of the default, not a failure of bucket scoping. Source: [AIStor AssumeRoleWithWebIdentity](https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/).

**Presigned URLs, REASONED:** no live AIStor deployment or `mc` is available here. Use a known private fixture and signing credentials that remain valid throughout the comparison. Confirm ordinary signed reads before and after each trial.

Paste whole Bash blocks. Substitute inside the single quotes; values containing a literal apostrophe need proper shell quoting. Disable shell history recording and tracing before handling a real URL. The block keeps the URL out of curl's argv, but does not protect it from history, tracing, or the account owner.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PRESIGNED_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*example.com*|*[[:cntrl:]]*|"") echo "substitute the complete URL without control characters; not probing"; exit ;;
    https://*) ;;
    *) echo "use the deployment HTTPS URL; not probing"; exit ;;
  esac
  set -- "${1//\\/\\\\}"
  set -- "${1//\"/\\\"}"
  printf 'url = "%s"\n' "$1" |
    curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 20 \
      -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --config -
)
```

Use URLs generated for the direct AIStor endpoint; do not alter their signed hostname or path.

1. Test a five-minute URL immediately and again after six minutes. The first GET must succeed; the later GET must fail while a newly generated URL succeeds. This isolates URL expiry before the ten-minute signature-age threshold. Source: [AIStor `mc share download`](https://docs.min.io/aistor/reference/cli/mc-share/mc-share-download/).
2. Separately generate a one-hour URL using the same section 4.2 command with `--expire 1h` and a new output filename. Without the deny policy in a disposable comparison, GETs immediately and after eleven minutes should succeed. Repeat with the deny policy attached: the immediate GET should succeed, but a new GET using that URL after eleven minutes should receive an AIStor denial while a fresh URL still succeeds. This distinguishes the signature-age restriction from the URL's own expiry. Sources: [AIStor supported condition keys](https://docs.min.io/aistor/administration/iam/access/) and [S3 signature-condition semantics](https://docs.aws.amazon.com/AmazonS3/latest/developerguide/bucket-policy-s3-sigv4-conditions.html).

Correlate denials with AIStor's own request or audit evidence. A proxy error, expired signing key, missing object, or network failure does not establish either control.

**Console disabled, REASONED:** no live AIStor deployment or `mc` is available here. Run this on each AIStor host with permission to inspect its listeners. Supply the direct Console URL established by section 3, without credentials or query parameters, and a proven application object:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DIRECT_CONSOLE_HTTPS_URL' 'app/REPLACE_WITH_APP_BUCKET/REPLACE_WITH_KNOWN_PRIVATE_OBJECT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  [ -n "$1" ] && [ -n "$2" ] || { echo "supply both values; not probing"; exit; }
  case "$1|$2" in
    *REPLACE_WITH_*|*example.com*|*[[:cntrl:]]*) echo "substitute deployment values without control characters; not probing"; exit ;;
  esac
  case "$1" in
    https://*) ;;
    *) echo "use the deployment HTTPS Console URL; not probing"; exit ;;
  esac
  mc cat "$2" > /dev/null || { echo "signed S3 read failed; stop"; exit 1; }
  ss -tlnp
  curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

With the Console enabled, establish that its UI is served. After applying `MINIO_BROWSER=off` and restarting, confirm that the running service received that setting, the embedded Console listener is absent, and signed S3 reads still succeed. A failed request to the previous URL alone is insufficient. Disabling only `MINIO_BROWSER_REDIRECT` leaves the direct Console available. Sources: [AIStor Console settings](https://docs.min.io/aistor/reference/aistor-server/settings/console/) and [`mc cat`](https://docs.min.io/aistor/reference/cli/mc-cat/).

**API concurrency, REASONED:** no live multi-node AIStor deployment, authenticated load client, or metrics collector is available here. In a disposable four-node deployment, compare automatic sizing with the illustrative explicit budget of 64. Verify the effective setting on every node after restart.

Have the load client issue signed `GetObject` requests for `REPLACE_WITH_APP_BUCKET/REPLACE_WITH_LARGE_PRIVATE_FIXTURE`, first individually, then with 128 concurrent requests distributed evenly across the four nodes. Use sufficiently long transfers to observe simultaneous processing. Keep credentials in the client's protected credential store.

The automatic comparison must actually admit more than 16 simultaneous requests per node to discriminate this example. With the explicit budget, expect the per-node request pools to constrain admission to 16; client concurrency or throughput alone cannot establish enforcement. Source: [AIStor core settings](https://docs.min.io/aistor/reference/aistor-server/settings/core/).

Record `minio_api_requests_inflight_total` and `minio_api_requests_waiting_total` by server, alongside client outcomes and latency. Account for concurrent administrative traffic. If the client, network, or storage cannot saturate the pools, record the comparison as inconclusive. Do not infer an RPS limit or require an undocumented HTTP rejection code. Source: [AIStor metrics v3 reference](https://docs.min.io/aistor/operations/monitoring/metrics-and-alerts/metrics-v3/).

Backlog row (open): demonstrate the exposure probes and all four service checks against exposed and fixed states on live AIStor with `mc`, a KMS, and an independent durable audit receiver; record versions, commands, outcomes, and receiver evidence. These capabilities were unavailable in the authoring environment.

MINIO-LIVE additions (open): demonstrate OIDC role-policy and claim-policy scoping, including an unmapped identity and explicit STS duration overriding a shorter default and JWT expiry; five-minute presigned-URL expiry and independent signature-age denial before a longer URL expires; embedded Console disablement with successful S3 access and a redirect-only comparison; and cluster-wide API concurrency budgeting divided among nodes under measured load. Add an IdP, authenticated STS/S3 test client, load client, and per-node metrics collection to the existing prerequisites. Record AIStor and client RELEASE tags, redacted requests, effective settings, positive controls, denials, timing, listener evidence, and load measurements. All four additions remain REASONED until those comparisons are demonstrated.

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
- AIStor Console settings (disablement and browser redirection): https://docs.min.io/aistor/reference/aistor-server/settings/console/
- AIStor core settings (automatic and explicit cluster-wide concurrency budgets): https://docs.min.io/aistor/reference/aistor-server/settings/core/
- AIStor OIDC access management (role and claim mapping): https://docs.min.io/aistor/administration/iam/access/oidc-access/
- AIStor OIDC identity management (mutually exclusive mappings and restart): https://docs.min.io/aistor/administration/iam/identity/oidc-identity/
- AIStor OpenID settings (role policy and claim name): https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/
- AIStor AssumeRoleWithWebIdentity (duration bounds and JWT-expiry precedence): https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/
- AIStor STS settings (default duration): https://docs.min.io/aistor/reference/aistor-server/settings/iam/sts/
- AIStor `mc share download` (presigned credentials and expiry): https://docs.min.io/aistor/reference/cli/mc-share/mc-share-download/
- AWS S3 signature-condition reference (supplementary semantics for AIStor's documented condition key): https://docs.aws.amazon.com/AmazonS3/latest/developerguide/bucket-policy-s3-sigv4-conditions.html
- AIStor metrics v3 (active and queued requests): https://docs.min.io/aistor/operations/monitoring/metrics-and-alerts/metrics-v3/
- AIStor release artifacts (server and client RELEASE baselines): https://docs.min.io/aistor/operations/release-artifacts/
