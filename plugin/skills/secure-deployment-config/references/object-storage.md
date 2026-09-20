# Object storage: S3, Cloudflare R2, Google Cloud Storage, Azure Blob, Supabase Storage

AI projects put user uploads, datasets, and model files in buckets, and one public bucket or one over-broad policy leaks every object in it, silently, to anyone who guesses or scrapes a URL. Every provider below now defaults new buckets to private; the work is keeping them that way, granting access per principal, and sharing objects through short-lived signed URLs rather than by making anything public. Self-hosted MinIO is covered in [minio.md](minio.md).

Documentation was checked in September 2026. Defaults below refer to the documented behavior at the time of writing; inspect existing resources and inherited policies rather than assuming they match new-resource defaults. These controls address separate questions: who can read an object, which network routes reach it, whether transport is encrypted, and whether an object can be deleted.

Live behavior has not been demonstrated in this authoring environment: no authorized cloud accounts, buckets, application identities, or network fixtures were supplied. The Verify section marks the outstanding comparisons **REASONED** and records the demonstration debt.

Paste shell blocks whole, including the parentheses, marker, and argument-count checks. Substitute inside the single quotes on each `set --` line. These examples assume genuine shell builtins; a value containing a literal apostrophe needs correct shell quoting rather than direct substitution. Load cloud credentials through the provider's credential mechanism, never as literal keys in command arguments.

## Amazon S3

### 1. Block public access at the account and bucket

New buckets and objects allow no public access, and Object Ownership defaults to "Bucket owner enforced", which disables ACLs; keep it that way and grant access only through bucket policies and IAM. These examples target general purpose buckets. All four bucket Block Public Access settings default to enabled for new buckets. This does not establish an account-level default: inspect the account configuration and any AWS Organizations policy. See [bucket defaults](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingBucket.html) and [Object Ownership](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html).

Turn on all four Block Public Access settings (`BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets`) at the account level as well as per bucket. S3 applies the most restrictive combination across applicable access point, bucket, and effective account settings, including organization enforcement. An account restriction therefore still applies if someone loosens a bucket setting later. Block Public Access neither encrypts objects nor removes stored public grants; disabling it can reactivate those grants. Remove unnecessary public policies and ACL grants as well. See [Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

Before changing an existing bucket to `ObjectOwnership=BucketOwnerEnforced`, migrate ACL-dependent clients and access grants to policies. Uploads that request unsupported ACLs fail; uploads without an ACL, or with `bucket-owner-full-control`, remain supported. ACLs cease participating in authorization, but their stored configuration is not erased. See [the ownership migration behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html).

The following applies the baseline and reads it back. Account changes affect other buckets in that account, so first inventory intentional public workloads and migrate them to the intended delivery architecture.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ACCOUNT_ID' 'REPLACE_WITH_BUCKET'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not configuring"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not configuring"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the account ID; not configuring" ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute the bucket; not configuring" ;;
        *)
          aws s3control put-public-access-block --account-id "$1" \
            --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true || exit
          aws s3api put-public-access-block --bucket "$2" \
            --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true || exit
          aws s3api put-bucket-ownership-controls --bucket "$2" \
            --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerEnforced}]' || exit
          aws s3control get-public-access-block --account-id "$1" || exit
          aws s3api get-public-access-block --bucket "$2" || exit
          aws s3api get-bucket-ownership-controls --bucket "$2" || exit
          aws s3api get-bucket-policy-status --bucket "$2"
          ;;
      esac ;;
  esac
)
```

Expect all four flags to be `true` in both readbacks and ownership to be `BucketOwnerEnforced`. For an attached bucket policy, expect `"IsPublic": false`. A missing policy is a separate state to inspect; an access-denied or failed readback is not evidence of privacy. The command syntax is documented for [account configuration](https://docs.aws.amazon.com/cli/latest/reference/s3control/put-public-access-block.html), [bucket configuration](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-public-access-block.html), and [ownership controls](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-ownership-controls.html).

An Allow in a bucket policy is "public" if it grants to `"Principal": "*"` without a qualifying fixed restriction, such as a specific principal, `aws:SourceVpc`, `aws:SourceArn`, or a sufficiently narrow `aws:SourceIp`. A broad Deny is not a public grant. See [the meaning of public](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

IAM Access Analyzer for S3 lists buckets whose ACL, bucket policy, or access point policy grants public or cross-account access, but only in a Region with an applicable external-access analyzer. An account-level analyzer covers the account; an organization-level analyzer has a different zone of trust. Findings update asynchronously, and archived findings drop out of the active view; create an analyzer in every Region that holds buckets, review archived as well as active findings, and confirm the Block Public Access settings directly rather than treating an empty list as proof. See [IAM Access Analyzer for S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html).

### 2. Give applications and signers only their object permissions

Give each application its own IAM role with only the actions and prefixes it uses ([machine-auth.md](machine-auth.md)). For an application that reads and uploads under `uploads/`, this identity policy is a starting point:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadAndUploadOnly",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::REPLACE_WITH_BUCKET/uploads/*"
    },
    {
      "Sid": "ListUploadsOnly",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::REPLACE_WITH_BUCKET",
      "Condition": {
        "StringLike": {
          "s3:prefix": ["uploads/", "uploads/*"]
        }
      }
    }
  ]
}
```

Remove `s3:PutObject` from a download-only signer. Remove the listing statement if the application already knows object keys. Add deletion, multipart, or KMS permissions only when the actual operation needs them. Avoid `s3:*` and `"Resource": "*"` in application Allow statements. Other attached policies can add permissions, so review the role's effective access. See [identity policy examples](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html) and [prefix conditions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html).

### 3. Require encrypted transport and choose network restrictions separately

Merge this statement into the bucket policy, preserving existing required statements. It denies insecure requests from principals other than AWS services:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::REPLACE_WITH_BUCKET",
        "arn:aws:s3:::REPLACE_WITH_BUCKET/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false",
          "aws:PrincipalIsAWSService": "false"
        }
      }
    }
  ]
}
```

The broad action in this Deny is intentional. The `aws:PrincipalIsAWSService=false` condition avoids breaking service-to-service requests whose network context can be redacted. It does not grant those services access; they still need authorization. See [transport policy conditions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html).

If every consumer must use a particular VPC endpoint, optionally add this separate statement:

```json
{
  "Sid": "DenyOutsideChosenEndpoint",
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": [
    "arn:aws:s3:::REPLACE_WITH_BUCKET",
    "arn:aws:s3:::REPLACE_WITH_BUCKET/*"
  ],
  "Condition": {
    "StringNotEquals": {
      "aws:SourceVpce": "REPLACE_WITH_VPC_ENDPOINT_ID"
    }
  }
}
```

This is an opt-in network boundary, not a universal private-bucket baseline. It can deny console access, external presigned-URL consumers, and integrations that do not traverse that endpoint. Establish the endpoint path and recovery procedure before applying it. A valid signature does not override the Deny. See [VPC endpoint bucket policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html).

### 4. Keep signed access short and plan revocation

Share objects with presigned URLs and a short expiry. The original example becomes `aws s3 presign s3://REPLACE_WITH_BUCKET/model.safetensors --expires-in 600`; the guarded Verify block demonstrates the same operation with a 60-second lifetime. The CLI default is 3600 seconds and maximum is 604800 seconds. The signing principal needs the underlying permission, such as `s3:GetObject`; signing a URL is not proof that the request will be authorized. Temporary credentials can expire before the requested URL lifetime. See [CLI presigning](https://docs.aws.amazon.com/cli/latest/reference/s3/presign.html) and [presigned URL permissions and expiry](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

For an additional age limit, optionally merge this statement into the bucket policy:

```json
{
  "Sid": "DenyOldSignatures",
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": "arn:aws:s3:::REPLACE_WITH_BUCKET/*",
  "Condition": {
    "NumericGreaterThan": {
      "s3:signatureAge": "600000"
    }
  }
}
```

`600000` is ten minutes in milliseconds. This example limits signature age; it does not change the URL's encoded expiry, and its effect must be checked against other signed workloads. Revoking or deactivating the signing credentials invalidates dependent URLs; an effective IAM or bucket-policy denial can also stop access. S3 does not have Azure's container stored-access-policy mechanism. See [presigned URL restrictions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

### 5. Keep encryption enabled; use KMS when key control is required

All new object uploads already receive SSE-S3 encryption unless another supported encryption configuration applies. SSE-KMS is optional when you need KMS key control. Changing the bucket default does not retroactively encrypt or re-encrypt existing objects. See [default bucket encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html).

For SSE-KMS, the `put-bucket-encryption` configuration has this shape after substituting an appropriate key ARN:

```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "REPLACE_WITH_KMS_KEY_ARN"
      },
      "BucketKeyEnabled": true
    }
  ]
}
```

Apply it through the documented [bucket-encryption operation](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-encryption.html), with the required key policy and application permissions. `BucketKeyEnabled` is disabled by default for general purpose buckets; enabling it reduces KMS request costs. It is not a public-access barrier. Encryption does not repair public permissions. See [the encryption rule reference](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ServerSideEncryptionRule.html) and [S3 Bucket Keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html).

### 6. Add recovery, retention, and audit after fixing exposure

S3 Versioning is disabled by default. Enable it when recovery from overwrites or deletion is required, and account for retained versions. Once enabled, versioning can be suspended but the bucket cannot return to its original unversioned state. See [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html).

Object Lock requires versioning. Once Object Lock is enabled, it cannot be disabled and versioning cannot be suspended. `GOVERNANCE` retention can be bypassed by a principal with `s3:BypassGovernanceRetention` that explicitly requests the bypass. `COMPLIANCE` retention cannot be shortened or bypassed by an ordinary administrator or the account root user. Choose retention periods deliberately; test governance behavior before committing to compliance retention. Locks protect object versions, not confidentiality, and do not prevent a new version or delete marker being added. See [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) and [its irreversible configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html).

MFA Delete adds MFA requirements to permanent version deletion and changes to versioning state. Only the bucket owner's root account can enable it. It is configured through the CLI or API, not the console; it is not MFA for object reads. MFA Delete is incompatible with lifecycle configurations. Do not place root access keys or a real MFA code into a copied command. See [MFA Delete](https://docs.aws.amazon.com/AmazonS3/latest/userguide/MultiFactorAuthenticationDelete.html).

Enable server access logging to a separate destination bucket and configure CloudTrail S3 data events for the object operations you need to audit. Both are off by default; CloudTrail management-event history is not an object-access log. See [server logging setup](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html) and [CloudTrail S3 data events](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html).

With ACLs disabled on the log destination, grant `logging.s3.amazonaws.com` `s3:PutObject` on the intended log prefix through a destination bucket policy, constrained by the source bucket ARN and source account. Do not use ACL target grants. For delivery to an S3 bucket, the destination must be in the same account and Region; do not select an Object Lock destination or create recursive logging. Delivery is delayed, so issue a known fixture request and look for its record rather than treating an empty log as proof that nothing happened. See [log-delivery permissions and prerequisites](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html).

## Cloudflare R2

### 1. Close every unintended public route

Buckets are never publicly accessible by default; public access is an explicit step, either a custom domain you control or a Cloudflare-managed `r2.dev` subdomain, which is rate-limited and for development only. Under the bucket's Settings, keep the Public Development URL disabled. To disable an enabled URL, select Disable, type `disallow`, and confirm. Disabling one route leaves other enabled routes unchanged. See [public bucket settings](https://developers.cloudflare.com/r2/buckets/public-buckets/).

Attaching no custom domain is a valid baseline for a bucket accessed only through authenticated APIs or presigned URLs. A custom domain can also be protected with Cloudflare Access or WAF token authentication; it need not be anonymously public. Keep `r2.dev` disabled when using those protections, or callers can bypass the protected hostname. Check every attached domain and any application route that serves the bucket. See [custom-domain access controls](https://developers.cloudflare.com/r2/buckets/public-buckets/) and [protecting R2 with Cloudflare Access](https://developers.cloudflare.com/r2/tutorials/cloudflare-access/).

### 2. Scope application tokens by permission and bucket

Create R2 API tokens with the least permission: `Object Read only` or `Object Read & Write` scoped to explicit buckets for applications. `Admin Read & Write` can create and delete buckets and change their configuration and belongs with operators; `Admin Read only` can inspect buckets and read objects but not create or delete buckets. The secret access key is shown once, so store it in a secret manager ([secrets.md](secrets.md)). See [R2 token permissions](https://developers.cloudflare.com/r2/api/tokens/).

An Account API token can still be bucket-scoped when given object permissions. Account versus User API token describes the token's ownership and lifecycle; it does not by itself establish resource scope. Inspect the resource permissions and selected buckets. Give a download signer read-only object access rather than administrative permissions. See [token creation and resource scope](https://developers.cloudflare.com/r2/api/tokens/).

### 3. Use short presigned URLs and explicit browser CORS

R2 supports S3 presigned URLs, generated with your R2 token and SigV4, valid from 1 second to 7 days (604800 seconds); keep uploads and downloads on these rather than on an anonymously public bucket. In the JavaScript signing example, `expiresIn` is the lifetime in seconds; choose it explicitly, for example `600`.

Presigned URLs work on the R2 S3 API domain, not custom domains. Do not replace the signed hostname with your custom hostname. A protected custom domain uses its own Access or WAF authentication flow. See [R2 presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/).

For browser clients, add a bucket CORS policy with the application's exact origins, operations, and request headers. In the dashboard's CORS Policy JSON editor, this example permits reads and uploads from one origin:

```json
[
  {
    "AllowedOrigins": ["https://app.example.com"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["Content-Type"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 600
  }
]
```

Replace the origin with the application's real HTTPS origin, remove unused methods, and add only headers the client actually sends. This is the dashboard format; Wrangler's configuration format differs. CORS is a browser control, not authorization: a non-browser client can use an otherwise valid presigned URL regardless of the allowed origin. See [R2 CORS configuration](https://developers.cloudflare.com/r2/buckets/cors/).

### 4. Treat lifecycle deletion as housekeeping

The default lifecycle rule expires incomplete multipart uploads seven days after initiation; it does not expire completed objects. Add explicit object-expiration rules when appropriate. Expiration is asynchronous: objects are typically removed within roughly 24 hours of their expiration time, and changes can take longer to affect existing objects. Lifecycle deletion is not immediate credential revocation. Close an exposed route or revoke the relevant token when access must stop. See [object lifecycles](https://developers.cloudflare.com/r2/buckets/object-lifecycles/) and [API token lifecycle](https://developers.cloudflare.com/r2/api/tokens/).

## Google Cloud Storage

### 1. Disable ACL authorization and enforce public access prevention

Enable uniform bucket-level access so ACLs are disabled and only IAM grants access; after 90 consecutive days it cannot be turned off. Migrate ACL-only grants before enabling it. The `gcloud storage buckets create` CLI flag defaults to `False`, so private-by-default does not mean uniform access is already enabled. See [uniform access](https://docs.cloud.google.com/storage/docs/uniform-bucket-level-access) and [the CLI creation default](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/create).

Enforce public access prevention on the bucket, and enforce the organization-policy constraint `constraints/storage.publicAccessPrevention` at the appropriate organization, folder, or project. With prevention active, attempts to grant `allUsers` or `allAuthenticatedUsers` fail with `412 Precondition Failed`, and anonymous requests to data get `401` or `403`. A bucket shows `enforced` or `inherited`; the API default is `inherited`, which protects the bucket only when an effective enforcing organization policy applies. See [public access prevention](https://docs.cloud.google.com/storage/docs/public-access-prevention), [the bucket API defaults](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets), and [organization-policy setup](https://docs.cloud.google.com/storage/docs/using-public-access-prevention).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BUCKET'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not configuring"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not configuring"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the bucket; not configuring" ;;
    *)
      gcloud storage buckets update "gs://$1" \
        --uniform-bucket-level-access --public-access-prevention || exit
      gcloud storage buckets describe "gs://$1"
      ;;
  esac
)
```

These are boolean CLI flags. The description should show uniform access enabled and public access prevention enforced; the corresponding API fields are `iamConfiguration.uniformBucketLevelAccess.enabled=true` and `iamConfiguration.publicAccessPrevention="enforced"`. See [bucket update](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/update), [bucket description](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/describe), and [uniform-access setup](https://docs.cloud.google.com/storage/docs/using-uniform-bucket-level-access).

### 2. Limit IAM grants by object prefix and time

Bucket IAM conditions require uniform bucket-level access. Use `resource.name.startsWith` for an object prefix and `request.time` for a grant deadline. An example conditional read binding is:

```json
{
  "version": 3,
  "bindings": [
    {
      "role": "roles/storage.objectViewer",
      "members": [
        "serviceAccount:REPLACE_WITH_SERVICE_ACCOUNT_EMAIL"
      ],
      "condition": {
        "title": "ReadUploadsUntilExpiry",
        "expression": "resource.name.startsWith('projects/_/buckets/REPLACE_WITH_BUCKET/objects/uploads/') && request.time < timestamp('REPLACE_WITH_UTC_EXPIRY')"
      }
    }
  ],
  "etag": "REPLACE_WITH_CURRENT_POLICY_ETAG"
}
```

Replace the expiry with an RFC 3339 UTC timestamp. Fetch the current policy with requested policy version 3, preserve its `etag` and required bindings, and merge the conditional binding into it. Write policy version 3; do not replace an existing policy blindly with this example. See [conditional policy management](https://docs.cloud.google.com/storage/docs/access-control/using-iam-permissions).

A prefix condition cannot restrict `storage.objects.list` to matching objects: listing is authorized against the bucket. The object-prefix condition above does not grant a filtered listing capability. Avoid separately granting unrestricted listing if names must remain private, and inspect project-level grants that can independently authorize access. See [IAM conditions and their limitations](https://docs.cloud.google.com/storage/docs/access-control/iam).

### 3. Use an authorized signer and a short duration

Signed URLs (V4) expire after at most 604800 seconds (7 days). `gcloud storage sign-url --duration=1h` signs with a service account, through `--impersonate-service-account`, an activated service account, or a key file, rather than ordinary `gcloud auth login` user credentials alone. The default duration is one hour. System-managed signing permits at most 12 hours because its signing key might not remain valid longer. Seven-day signing works with either `--private-key-file` or an account authorized through `gcloud auth activate-service-account`. See [the sign-url reference](https://docs.cloud.google.com/sdk/gcloud/reference/storage/sign-url).

Grant the signing service account the required object permission and grant the caller only the signing or impersonation permissions it needs. Public access prevention does not apply to signed URLs, so keep their durations short. Do not create a long-lived service-account key merely to obtain a longer link lifetime. See [signing prerequisites](https://docs.cloud.google.com/storage/docs/access-control/signing-urls-with-helpers) and [signed URLs](https://docs.cloud.google.com/storage/docs/access-control/signed-urls).

### 4. Set transport policy without inventing a bucket HTTPS switch

Use HTTPS for application requests and signed URLs. Where organization policy is available, configure `gcp.restrictTLSVersion` with denied values `TLS_VERSION_1` and `TLS_VERSION_1_1` to reject those older TLS versions for covered requests.

This guide has no source-verified bucket setting equivalent to S3's `aws:SecureTransport` Deny for rejecting plaintext HTTP. A minimum TLS-version policy is not proof that plaintext HTTP is blocked. The documented TLS constraint also does not apply to public Cloud Storage objects served from the Google Front End cache. See [TLS-version restrictions and their scope](https://docs.cloud.google.com/docs/security/compliance/restrict-tls-versions).

### 5. Add CMEK only when you need customer-controlled keys

Google-managed encryption is the default. For CMEK, select a Cloud KMS key in a compatible location and first grant the bucket project's Cloud Storage service agent `roles/cloudkms.cryptoKeyEncrypterDecrypter` on that key. Then set the bucket default through the Encryption configuration or the `gcloud storage buckets update` flag `--default-encryption-key=projects/REPLACE_WITH_PROJECT/locations/REPLACE_WITH_LOCATION/keyRings/REPLACE_WITH_KEY_RING/cryptoKeys/REPLACE_WITH_KEY`. See [standard encryption](https://docs.cloud.google.com/storage/docs/encryption/default-keys) and [CMEK setup](https://docs.cloud.google.com/storage/docs/encryption/using-customer-managed-keys).

The default key applies to subsequent writes that do not select another encryption method. It does not re-encrypt existing objects; those require a rewrite. Encryption does not repair public permissions: authorized reads are decrypted by the service. See [CMEK behavior and key replacement](https://docs.cloud.google.com/storage/docs/encryption/customer-managed-keys).

## Azure Blob Storage

### 1. Deny anonymous access and migrate away from Shared Key

Anonymous access is prohibited by default for Resource Manager storage accounts. Keep the account property `allowBlobPublicAccess` at `false` ("Allow Blob anonymous access: Disabled" under Settings > Configuration); it overrides any container set to Container or Blob access, so a per-container mistake cannot open data. Containers are private by default. The documented default interpretation of `allowBlobPublicAccess` is false; inspect existing accounts explicitly. See [anonymous-access remediation](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent) and [the property reference](https://learn.microsoft.com/en-us/javascript/api/%40azure/arm-storage/storageaccountpropertiesupdateparameters?view=azure-node-latest).

Before setting `allowSharedKeyAccess=false`, grant the application a Microsoft Entra data role at the narrowest useful scope, such as Storage Blob Data Reader on its container, and demonstrate an authorized read using that identity. A management-plane role alone is not a substitute for a Blob data role. See [assigning Blob data roles](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access).

An unset or null `allowSharedKeyAccess` permits Shared Key authorization, just like `true`. Setting it to `false` rejects account-key-authorized requests, including service SAS and account SAS, while permitting properly authorized user delegation SAS. It does not prevent someone holding an account key from computing a SAS; it prevents using that SAS for authorization. See [preventing Shared Key authorization](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent).

Azure Policy with the `Microsoft.Storage/storageAccounts/allowBlobPublicAccess` field audits or denies accounts that allow anonymous access. See [governing anonymous access](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent).

### 2. Require HTTPS and restrict the network route

Set `supportsHttpsTrafficOnly=true` in the storage-account resource and `minimumTlsVersion="TLS1_2"`. The CLI uses `--https-only true` and reports `enableHttpsTrafficOnly`; these are representations of the secure-transfer control. HTTPS-only rejects HTTP requests independently of authorization. See [secure transfer](https://learn.microsoft.com/en-us/azure/storage/common/storage-require-secure-transfer) and [storage-account resource properties](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts).

Azure documents TLS 1.2 as the service minimum from February 3, 2026. Keep the explicit TLS 1.2 setting and check clients rather than relying on an old unset-property interpretation. See [the TLS migration notice](https://learn.microsoft.com/en-us/azure/storage/common/transport-layer-security-configure-migrate-to-tls2) and [minimum TLS configuration](https://learn.microsoft.com/en-us/azure/storage/common/transport-layer-security-configure-minimum-version).

After granting and testing the Entra data role, apply the authorization and transport baseline:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_STORAGE_ACCOUNT' 'REPLACE_WITH_RESOURCE_GROUP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not configuring"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not configuring"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the storage account; not configuring" ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute the resource group; not configuring" ;;
        *)
          az storage account update --name "$1" --resource-group "$2" \
            --allow-blob-public-access false --allow-shared-key-access false \
            --https-only true --min-tls-version TLS1_2 || exit
          az storage account show --name "$1" --resource-group "$2" \
            --query allowBlobPublicAccess --output tsv || exit
          az storage account show --name "$1" --resource-group "$2" \
            --query '{sharedKey:allowSharedKeyAccess,httpsOnly:enableHttpsTrafficOnly,tls:minimumTlsVersion,publicNetwork:publicNetworkAccess,networkRules:networkRuleSet,sasPolicy:sasPolicy}'
          ;;
      esac ;;
  esac
)
```

The first readback must be `false`; the remaining authorization and transport values must show Shared Key disabled, HTTPS required, and TLS 1.2. See [the account CLI reference](https://learn.microsoft.com/en-us/cli/azure/storage/account).

Configure network access separately. Set `networkAcls.defaultAction=Deny` with only the required network rules, or set `publicNetworkAccess=Disabled` for a private-endpoint deployment. The corresponding account-update CLI options are `--default-action Deny` and `--public-network-access Disabled`. Review firewall exceptions as well as the default action. These restrictions can also deny legitimate external SAS consumers. See [storage network access](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security).

For private access, create and approve a private endpoint for the `blob` subresource and configure private DNS, normally `privatelink.blob.core.windows.net`, for the client's network. Continue using the normal account Blob hostname; DNS should resolve it to the private endpoint inside that network. A private endpoint alone leaves the public route available, so also restrict or disable public network access. See [private endpoints and DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints).

### 3. Use user delegation SAS and enforce the intended lifetime

Prefer a user delegation SAS secured by Microsoft Entra credentials over service or account SAS signed with the account key. Use HTTPS only, grant the least permission, such as read-only access to one blob, and use near-term expiry. See [the SAS overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview).

The CLI operation is `az storage blob generate-sas` with `--auth-mode login --as-user`. Supply the intended `--account-name`, `--container-name`, and `--name`, use `--permissions r --https-only`, and provide explicit UTC `--start` and `--expiry` values. A user delegation SAS cannot exceed seven days or outlive its delegation key. See [user delegation SAS creation](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-cli) and [blob CLI parameters](https://learn.microsoft.com/en-us/cli/azure/storage/blob).

The signer needs data permissions on the target and `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey` at account scope or above. For a container-scoped reader, use a separate account-scoped Storage Blob Delegator assignment when needed rather than broadening all its data access. See [delegation-key permissions](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas).

Configure the account's SAS expiration policy with a short upper interval and expiration action `Block`. The default action, `Log`, permits out-of-policy use and records it only when Azure Monitor diagnostics are configured; it does not enforce the interval. `Block` denies supported requests with an excessive validity interval or missing signed start. The CLI options are `--sas-exp` and `--sas-expiration-action Block`. Accounts with missing access-key creation times can require key rotation before policy configuration succeeds. See [SAS expiration policies](https://learn.microsoft.com/en-us/azure/storage/common/sas-expiration-policy).

The expiration action is not supported for service SAS associated with a stored access policy or user delegation SAS through the HDFS endpoint. It does apply to supported Blob user delegation SAS requests. The delegation key's own lifetime is separate, and a longer account policy cannot extend the seven-day user delegation limit. See [policy exceptions](https://learn.microsoft.com/en-us/azure/storage/common/sas-expiration-policy).

Plan revocation by SAS type:

- For a retained service-SAS integration, a container stored access policy can revoke associated SAS by removing the policy, changing its identifier, or expiring it. Preserve unrelated policies when updating the container ACL. Account SAS and user delegation SAS do not use that mechanism. See [stored access policies](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy) and [SAS types](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview).
- For user delegation SAS, `az storage account revoke-delegation-keys` revokes all delegation keys for the account, affecting every dependent SAS. Revocation and RBAC changes can be delayed by caching; test the saved URL again rather than declaring immediate success. See [the revoke command](https://learn.microsoft.com/en-us/cli/azure/storage/account) and [user delegation revocation](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas).
- For account-key SAS without a stored policy, plan signing-key rotation and its wider application impact. Keeping `allowSharedKeyAccess=false` rejects account-key-authorized requests regardless of whether a SAS can still be generated. See [Shared Key prevention](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent).

### 4. Apply retention deliberately

Container immutability provides write-once, read-many retention. A newly created time-based retention policy starts unlocked, allowing testing and adjustment. Locking is irreversible: the locked policy cannot be deleted or shortened, although permitted extensions remain possible. Test with disposable data before locking a production policy. Retention does not prevent authorized or anonymous reads and therefore follows the exposure fixes above. See [immutable storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview) and [container retention configuration](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope).

## Supabase Storage

### 1. Keep sensitive buckets private

Buckets are private by default; a public bucket means anyone with the URL can read the file, so use one only for assets that are meant to be public. Make the intent explicit when creating a bucket:

```javascript
const { data, error } = await supabase.storage.createBucket(
  'REPLACE_WITH_PRIVATE_BUCKET',
  { public: false }
);
if (error) throw error;
```

`false` is the private default. Public buckets bypass access controls for retrieving and serving files; uploads, deletes, moves, and copies still undergo access checks. A restrictive SELECT policy cannot make a public asset URL private. See [bucket access models](https://supabase.com/docs/guides/storage/buckets/fundamentals) and [createBucket](https://supabase.com/docs/reference/javascript/file-buckets-createbucket).

### 2. Scope every operation policy to the bucket and caller

Access to a private bucket is governed by row level security policies on `storage.objects`, and without policies Storage allows no uploads at all. Application-table RLS does not secure Storage. Write policies per operation and scope them to the intended bucket and owner. The existing ownership example needs the bucket predicate:

```sql
create policy "Individual user Access"
on storage.objects for select
to authenticated
using (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (select auth.jwt()->>'sub') = owner_id
);
```

If this policy already exists, amend its predicate rather than adding another permissive policy. Audit other policies that could independently allow cross-bucket access. `owner_id` records the creating user's JWT subject; ownership alone does not enforce authorization. Objects created through a service credential or the dashboard might not have the end-user ownership this policy expects. See [Storage ownership](https://supabase.com/docs/guides/storage/security/ownership) and [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).

SELECT is not upload permission. For objects named under the authenticated user's UUID, add a separate INSERT policy:

```sql
create policy "Upload own files"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (storage.foldername(name))[1] = (select auth.uid())::text
  and (select auth.jwt()->>'sub') = owner_id
);
```

Use an authenticated user's Storage request for this ownership model. The path condition matches the companion [firebase-supabase.md](firebase-supabase.md) guide; the owner predicate also keeps the original ownership-based read model consistent. See [Storage access control](https://supabase.com/docs/guides/storage/security/access-control) and [path helpers](https://supabase.com/docs/guides/storage/schema/helper-functions).

Only if overwrites and deletion are intended, add their separate policies:

```sql
create policy "Update own files"
on storage.objects for update
to authenticated
using (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (select auth.jwt()->>'sub') = owner_id
)
with check (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (storage.foldername(name))[1] = (select auth.uid())::text
  and (select auth.jwt()->>'sub') = owner_id
);

create policy "Delete own files"
on storage.objects for delete
to authenticated
using (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (select auth.jwt()->>'sub') = owner_id
);
```

Upsert additionally needs SELECT and UPDATE. UPDATE checks both the existing row through `USING` and its proposed state through `WITH CHECK`; keep the bucket boundary in both. Storage operations can require more than one SQL permission: moving needs SELECT and UPDATE, copying needs SELECT and INSERT, and deletion needs SELECT and DELETE. See [upload and upsert permissions](https://supabase.com/docs/guides/storage/security/access-control), [update](https://supabase.com/docs/reference/javascript/file-buckets-update), [move](https://supabase.com/docs/reference/javascript/file-buckets-move), [copy](https://supabase.com/docs/reference/javascript/file-buckets-copy), and [remove](https://supabase.com/docs/reference/javascript/file-buckets-remove).

### 3. Issue short signed URLs and protect service credentials

Share private objects with `supabase.storage.from('bucket').createSignedUrl('path.pdf', 3600)` from server code after authorizing the caller. The expiry argument is seconds; `3600` is an example, not a default:

```javascript
const { data, error } = await supabase.storage
  .from('REPLACE_WITH_PRIVATE_BUCKET')
  .createSignedUrl('path.pdf', 3600);
if (error) throw error;
```

`getPublicUrl` works for public buckets; constructing a public URL does not authorize a private download. Storage signed URLs use a dedicated internal signing key and stay valid until expiry even if you rotate or revoke Auth keys, disable legacy Auth keys, or migrate Auth signing algorithms. If signed URLs must be revoked, contact Supabase support. See [downloads and signing-key independence](https://supabase.com/docs/guides/storage/serving/downloads) and [createSignedUrl](https://supabase.com/docs/reference/javascript/file-buckets-createsignedurl).

The service-role key bypasses RLS and never reaches a browser. Server secret keys also carry privileged access; neither is an end-user credential. A privileged signing endpoint must enforce its own bucket, object, and caller authorization before issuing a URL. Follow [firebase-supabase.md](firebase-supabase.md) and the privileged-credential guidance in [pocketbase.md](pocketbase.md). See [Supabase API keys](https://supabase.com/docs/guides/api/api-keys).

## Verify

These comparisons require controlled cloud resources and harmless fixture objects. No live cloud comparison below was run during authoring. Demonstrate exposed and fixed behavior on disposable fixtures without exposing production data. A transport failure, missing object, failed signing operation, or absent permission to inspect configuration is inconclusive.

### 1. Check signed-link lifetimes

**REASONED:** No authorized signing identities or fixture buckets were supplied. For each provider, issue a short-lived GET link for a known object, require successful access before expiry, then repeat the same saved URL after expiry and require denial. A newly generated URL is not an expiry test. The documented limits distinguish the intended behavior:

| Provider | Expiry control | Documented default and limit |
| --- | --- | --- |
| S3 | `aws s3 presign --expires-in` | Default 3600 seconds; maximum 604800. Signing credentials can expire sooner. [CLI](https://docs.aws.amazon.com/cli/latest/reference/s3/presign.html). |
| R2 | JavaScript signer `expiresIn` | Set explicitly; supported lifetime 1-604800 seconds. Use the S3 API domain. [Presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/). |
| GCS | `gcloud storage sign-url --duration` | Default 1h; maximum 12h with system-managed signing, or 7d with `--private-key-file` or an activated service account. [CLI](https://docs.cloud.google.com/sdk/gcloud/reference/storage/sign-url). |
| Azure | `generate-sas --auth-mode login --as-user`, with explicit start and expiry | User delegation maximum 7d, bounded by the delegation key and any applicable stricter policy. [Creation](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-cli). |
| Supabase | `createSignedUrl(path, seconds)` | Supply seconds explicitly; 3600 is an example, not a default. Auth-key rotation does not revoke the link. [Reference](https://supabase.com/docs/reference/javascript/file-buckets-createsignedurl), [revocation caveat](https://supabase.com/docs/guides/storage/serving/downloads). |

### 2. Prove authorized S3 access, anonymous denial, and expiry

**REASONED:** No S3 account, signing role, or known object was supplied. On a deliberately exposed disposable fixture, an unsigned GET returns its bytes; after the public-access baseline, that same unsigned GET must be denied while an authorized HTTPS GET succeeds. The saved signed URL must subsequently fail after expiry. See [public-access behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html) and [presigned URL behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

Use the same bucket and object in both arguments, with the correct regional endpoint. First prove the object exists and is readable WITH authorization, so a later anonymous denial is about access, not a missing object. S3 also returns `403` for an object you cannot list. Presigning signs a GET, so test with GET.

```bash
(
  set -- PASTE_WHOLE_BLOCK 's3://REPLACE_WITH_BUCKET/model.safetensors' 'https://REPLACE_WITH_BUCKET.s3.REPLACE_WITH_REGION.amazonaws.com/model.safetensors'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the S3 URI; not probing" ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
          echo "substitute the same object's unsigned HTTPS URL; not probing" ;;
        https://*)
          # First prove the object exists and is readable WITH authorization.
          # S3 also returns 403 for an object you cannot list. presign signs a GET.
          set -- "$2" "$(aws s3 presign "$1" --expires-in 60)"
          case "$2" in
            *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'"'*|*\\*)
              echo "signing failed or returned an unsafe URL; not probing" ;;
            https://*)
              # The URL is a credential. The builtin printf feeds curl on stdin, never argv.
              # AWS percent-encodes the URL; quotes, backslashes and controls were rejected.
              set -- "$1" "$2" "$(printf 'url = "%s"\n' "$2" |
                curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
                  -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --config -)"
              printf '%s\n' "$3"
              case "$3" in
                "http=200 exit=0 "*)
                  # Then the SAME object's unsigned URL must be denied; expected S3 403.
                  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
                    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
                  # And the saved signed URL must stop working once it expires.
                  sleep 61
                  printf 'url = "%s"\n' "$2" |
                    curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
                      -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --config -
                  ;;
                *) echo "authorized control failed; no access-control conclusion" ;;
              esac ;;
            *) echo "signing did not return HTTPS; not probing" ;;
          esac ;;
        *) echo "use the canonical unsigned HTTPS object URL; not probing" ;;
      esac ;;
  esac
)
```

Expected sequence: authorized `200`, anonymous `403`, then denial of the expired signed URL. A DNS, TLS, proxy, or local curl error is inconclusive. Client proxies are disabled so a proxy cannot answer for S3. One object is not the whole bucket: repeat for other keys, prefixes, and enabled access paths.

The signed URL stays out of curl's process arguments because the shell's builtin `printf` supplies it through stdin. This does not protect it from shell tracing, copied terminal output, or the account owner's process inspection. Keep `set -x` off. The curl status fields require curl 7.75.0 or later.

### 3. Check known objects on every other enabled route

**REASONED:** No R2, GCS, Azure, or Supabase fixture accounts or URLs were supplied. Use the following GET probe first with an authorized signed URL, then with the same object's unsigned URL. It prints headers and the response body, so use only harmless fixture data. Preserve the successful authorized control and the denial response. For expiry or revocation checks, repeat the saved signed URL.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_FIXTURE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute a complete fixture URL without control characters; not probing" ;;
    https://*)
      set -- "${1//\\/\\\\}"
      set -- "${1//\"/\\\"}"
      printf 'url = "%s"\n' "$1" |
        curl -q -g -sS -i --noproxy '*' --connect-timeout 5 --max-time 20 \
          -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --config -
      ;;
    *) echo "use an HTTPS fixture URL; not probing" ;;
  esac
)
```

A pasted signed URL can enter shell history even though it is absent from curl's arguments. Use a shell session configured not to retain credentials, and do not record signed URLs in test reports.

| Provider | Required comparison |
| --- | --- |
| R2 | **REASONED:** No bucket, Access application, or domain fixtures were supplied. GET the same known key through the S3 API signed URL, `r2.dev`, and every custom domain. An exposed route serves the fixture without authorization. Fixed `r2.dev` must not serve it; protected custom domains must deny or challenge an unauthorized caller while the authorized Access or WAF flow succeeds. A login page with status 200 is not the object: inspect bytes and redirects. [Public routes](https://developers.cloudflare.com/r2/buckets/public-buckets/), [Access protection](https://developers.cloudflare.com/r2/tutorials/cloudflare-access/). |
| GCS | **REASONED:** No bucket or IAM fixture was supplied. GET the known object's unsigned URL before and after prevention: an exposed public object returns bytes; enforced prevention denies anonymous access with `401` or `403`. Its valid signed URL can still succeed, so signed success does not mean prevention failed. [Prevention behavior](https://docs.cloud.google.com/storage/docs/public-access-prevention). |
| Azure | **REASONED:** No storage account or request-version fixtures were supplied. GET a known blob anonymously and with authorization before and after account-level denial. Require anonymous denial and a successful authorized control. The remediation page documents `401` or `409` depending on request version; the configuration page describes `403`. Do not declare one universal code: inspect the error, request/service version, and returned bytes. [Remediation](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent), [configuration](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-configure). |
| Supabase | **REASONED:** No project or user sessions were supplied. Request the known file through its public asset URL before and after making the fixture bucket private. Exposed returns the file; fixed returns an error, not the file. An authorized private download or deliberately issued signed URL must still succeed. [Bucket access](https://supabase.com/docs/guides/storage/buckets/fundamentals), [downloads](https://supabase.com/docs/guides/storage/serving/downloads). |

### 4. Inspect effective settings, permissions, and independent controls

**REASONED:** No cloud inventories or deployed client bundles were supplied. The provider's public-access view must show no unintended public access: IAM Access Analyzer for S3, with an analyzer in every bucket Region, has no unexplained active or archived public findings; GCS descriptions show prevention `enforced`, or `inherited` with an effective enforcing `storage.publicAccessPrevention` policy; the Azure Resource Graph inventory of `allowBlobPublicAccess` shows `false` on every account; and R2 has no Public Development URL and no unprotected custom domain. `inherited` alone is not a pass. Compare against deliberately exposed fixtures whose settings and requests reveal the exposure. See [S3 analysis](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html), [GCS policy inspection](https://docs.cloud.google.com/storage/docs/using-public-access-prevention), [Azure inventory](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent), and [R2 routes](https://developers.cloudflare.com/r2/buckets/public-buckets/).

| Control | Required exposed/fixed comparison |
| --- | --- |
| S3 policy scope and transport | **REASONED:** No IAM roles or controlled HTTP/VPC fixtures were supplied. As the application role, request `GetObject` inside and outside `uploads/`, and `ListObjectsV2` with allowed and unrelated prefixes. The broad-policy fixture permits excess access; the scoped role permits only intended requests. On an isolated harmless fixture, compare authenticated HTTP and HTTPS GETs before and after the transport Deny. Use disposable credentials confined to that fixture, never production credentials over HTTP. If the endpoint Deny is selected, repeat the authorized HTTPS GET inside and outside that endpoint. [IAM policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html), [transport conditions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html), [endpoint restrictions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html). |
| R2 token scope and CORS | **REASONED:** No application token or browser fixture was supplied. Use the token to GET a known object in its permitted bucket and another bucket, and attempt an upload with a read-only token. Broad credentials permit excess operations; scoped credentials deny them. In a browser, request a presigned upload from allowed and unrelated origins with the intended method and headers. Correct CORS permits the intended browser flow; it does not prevent a non-browser caller using a valid signature. [Tokens](https://developers.cloudflare.com/r2/api/tokens/), [CORS](https://developers.cloudflare.com/r2/buckets/cors/). |
| GCS conditions and TLS | **REASONED:** No conditional service account or organization-policy fixture was supplied. GET known objects inside and outside the prefix before and after the grant deadline; only the intended object and time window should work after broad grants are removed. Separately attempt object listing; do not accept an assumed prefix-filtered result. Compare a controlled GET to `https://storage.googleapis.com/REPLACE_WITH_BUCKET/REPLACE_WITH_OBJECT` using TLS 1.1 and TLS 1.2 under the documented TLS test procedure. Require the provider's policy denial for the restricted version and a successful supported-version control; a local TLS-library failure proves nothing about the policy. This does not test plaintext HTTP rejection. [Conditions](https://docs.cloud.google.com/storage/docs/access-control/iam), [TLS testing](https://docs.cloud.google.com/docs/security/compliance/restrict-tls-versions). |
| Azure authorization and network | **REASONED:** No Entra identity, SAS fixtures, private endpoint, or external host was supplied. GET the same known blob using Entra authorization, user delegation SAS, and account/service SAS before and after Shared Key denial. The first two remain usable with sufficient permissions; account-key authorization is rejected. Check account readbacks, then repeat an authorized HTTPS GET inside and outside the selected network boundary. The private client must resolve the normal Blob hostname to the private endpoint and succeed; an excluded public client must be denied. A private endpoint without public-route restriction is the exposed comparison. [Shared Key behavior](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent), [network access](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security), [private DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints). |
| Supabase operation and bucket scope | **REASONED:** No project with two buckets and two user sessions was supplied. As each user, call `download`, `upload`, `update`, `move`, `copy`, and `remove` on disposable objects owned by each user in both buckets. The original owner-only policy admits owned rows across buckets; corrected policies admit only the intended bucket and operations. Confirm that SELECT alone does not authorize upload, and that optional UPDATE/DELETE policies are absent when those operations are unwanted. Run a separate privileged-server control; its RLS bypass is not evidence that end-user policies work. [Access control](https://supabase.com/docs/guides/storage/security/access-control), [ownership](https://supabase.com/docs/guides/storage/security/ownership), [API keys](https://supabase.com/docs/guides/api/api-keys). |
| Revocation and Azure SAS policy | **REASONED:** No disposable signing credentials or diagnostic workspace was supplied. Save a working fixture URL, revoke its applicable signer permission/key or Azure stored policy/delegation key, and repeat the same GET after documented propagation. For Azure, use a still-unexpired SAS whose interval exceeds the configured limit: `Log` permits it and diagnostics record out-of-policy use; `Block` denies supported requests. Include the documented HDFS and stored-policy exceptions. For Supabase, Auth-key rotation must not be reported as Storage URL revocation; compare expiry or support-assisted revocation instead. [S3 URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html), [Azure policy](https://learn.microsoft.com/en-us/azure/storage/common/sas-expiration-policy), [delegation revocation](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas), [Supabase signing](https://supabase.com/docs/guides/storage/serving/downloads). |
| Encryption, retention, and audit | **REASONED:** No KMS keys, retention fixtures, or logging destinations were supplied. Inspect a new object's encryption metadata after selecting the intended default; compare an existing object's unchanged key before a deliberate rewrite. With S3 versioning enabled, overwrite a harmless fixture and retrieve its prior version. Compare permanent deletion of an unlocked version with a retained version, including authorized governance bypass versus compliance denial. For Azure, test an unlocked disposable retention policy before locking. Issue a known S3 object GET/PUT and locate the data-event and access-log records after delivery. Inspect R2 lifecycle rules and observe a disposable expired object's eventual deletion; do not count the lifecycle deadline as immediate revocation. [S3 encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html), [GCS CMEK](https://docs.cloud.google.com/storage/docs/encryption/customer-managed-keys), [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html), [Azure retention](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope), [CloudTrail](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html), [access logging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html), [R2 lifecycle](https://developers.cloudflare.com/r2/buckets/object-lifecycles/). |

**REASONED:** No actual application credential inventory, repository deployment secrets, or client bundle was supplied. Application credentials must be scoped to one bucket or prefix, and no root, account-key, or service-role credential may appear in client code or the repository. Inspect the deployed bundle and its source maps, and compare with a disposable positive-control build containing a known dummy credential so the inspection can detect the condition it claims to exclude. See [machine-auth.md](machine-auth.md), [secrets.md](secrets.md), and [Supabase credential privileges](https://supabase.com/docs/guides/api/api-keys).

### Demonstration backlog

All five bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring. Local guard tests refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments, and omitted or shortened `set --` lines in 50 cases. The repository's guard-convention scanner reported no findings on these blocks. All seven JSON examples parsed, and the two JavaScript examples passed syntax checking.

These are local syntax and guard results only. SQL policies were source-traced but not executed against Supabase. No live cloud behavior, deployed-bundle inspection, or whole-corpus gate result is claimed.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| OBJECT-STORAGE-LIVE | Demonstrate every REASONED comparison above with controlled S3, R2, GCS, Azure, and Supabase accounts; harmless objects; narrowly scoped application and signing identities; organization-policy access; TLS and private-network fixtures; KMS keys; retention and logging fixtures; Azure diagnostics; two Supabase users and buckets; and the deployed client build. Record effective settings, CLI/SDK versions, operations, identities, response/error codes and request versions, object-byte controls, expiry/revocation timing, logs, and disposable-data cleanup. Include S3 account and bucket readbacks, ACL migration, transport and endpoint denials, signature-age policy, versioning/Object Lock/MFA Delete behavior, Azure SAS-policy exceptions and delegation revocation, GCS conditional IAM and signing modes, every R2 route and CORS flow, and Supabase cross-bucket and per-operation denials. Never retain usable signed URLs or credentials in the record. | Open; live behavior is reasoned, not demonstrated. |

## Common mistakes

- Making a bucket public to fix a broken download link, when the fix was a signed URL.
- A presigned URL or SAS with a multi-day expiry pasted into a chat or ticket; it is a credential until it expires.
- Treating Block Public Access, encryption, HTTPS, a private endpoint, and retention as interchangeable controls.
- Assuming a new-bucket default proves the state of an existing bucket or account.
- Removing public grants only from the visible policy while leaving another route, ACL, inherited grant, or permissive RLS policy effective.
- Protecting an R2 custom domain while leaving `r2.dev` enabled.
- Calling GCS `inherited` public access prevention a pass without inspecting the effective organization policy.
- Expecting a GCS object-prefix condition to filter bucket listing.
- Disabling Azure Shared Key before granting and testing the replacement Entra data role.
- Treating Azure SAS `Log` as enforcement, or assuming Shared Key denial prevents offline SAS generation.
- Using an error for a nonexistent object as proof that anonymous access is blocked.
- Rotating Supabase Auth keys and assuming existing Storage signed URLs were revoked.
- Enabling irreversible retention before testing recovery, deletion, and operational requirements.

## Sources (checked September 2026)

- S3 Block Public Access (four settings, defaults, meaning of "public", IAM Access Analyzer): https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html and https://docs.aws.amazon.com/AmazonS3/latest/userguide/configuring-block-public-access-bucket.html
- S3 Object Ownership (Bucket owner enforced default, ACLs disabled): https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html
- AWS CLI `s3 presign` (`--expires-in` default and maximum): https://docs.aws.amazon.com/cli/latest/reference/s3/presign.html
- Cloudflare R2 public buckets, API tokens, presigned URLs: https://developers.cloudflare.com/r2/buckets/public-buckets/ , https://developers.cloudflare.com/r2/api/tokens/ , https://developers.cloudflare.com/r2/api/s3/presigned-urls/
- Google Cloud Storage uniform bucket-level access, public access prevention, signed URLs, `gcloud storage sign-url`: https://docs.cloud.google.com/storage/docs/uniform-bucket-level-access , https://docs.cloud.google.com/storage/docs/using-uniform-bucket-level-access , https://docs.cloud.google.com/storage/docs/public-access-prevention , https://docs.cloud.google.com/storage/docs/access-control/signed-urls , https://docs.cloud.google.com/sdk/gcloud/reference/storage/sign-url
- Azure Blob anonymous access remediation and SAS overview: https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent and https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview
- Supabase Storage buckets, access control, and downloads: https://supabase.com/docs/guides/storage/buckets/fundamentals , https://supabase.com/docs/guides/storage/security/access-control , https://supabase.com/docs/guides/storage/serving/downloads
- [S3 general purpose bucket defaults](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingBucket.html).
- [Account Block Public Access update](https://docs.aws.amazon.com/cli/latest/reference/s3control/put-public-access-block.html) and [readback](https://docs.aws.amazon.com/cli/latest/reference/s3control/get-public-access-block.html).
- [Bucket Block Public Access update](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-public-access-block.html), [readback](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-public-access-block.html), and [policy status](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-bucket-policy-status.html).
- [Ownership update](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-ownership-controls.html) and [readback](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-bucket-ownership-controls.html).
- [IAM Access Analyzer for S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html).
- [S3 application IAM policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html).
- [S3 transport, service-principal exceptions, and prefix conditions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html).
- [S3 VPC endpoint policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html).
- [S3 presigned URL permissions, expiry, revocation, and signature age](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).
- [S3 default encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html), [encryption CLI](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-encryption.html), [encryption-rule defaults](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ServerSideEncryptionRule.html), and [Bucket Keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html).
- [S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html), [Object Lock modes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html), [irreversible Object Lock configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-configure.html), and [MFA Delete](https://docs.aws.amazon.com/AmazonS3/latest/userguide/MultiFactorAuthenticationDelete.html).
- [S3 server access logging](https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html), [destination policy and setup](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enable-server-access-logging.html), and [CloudTrail S3 data events](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cloudtrail-logging-s3-info.html).
- [R2 with Cloudflare Access](https://developers.cloudflare.com/r2/tutorials/cloudflare-access/), [CORS](https://developers.cloudflare.com/r2/buckets/cors/), and [object lifecycles](https://developers.cloudflare.com/r2/buckets/object-lifecycles/).
- [GCS CLI creation defaults](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/create), [bucket update](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/update), [bucket description](https://docs.cloud.google.com/sdk/gcloud/reference/storage/buckets/describe), and [bucket API fields](https://docs.cloud.google.com/storage/docs/json_api/v1/buckets).
- [GCS public access prevention and organization-policy setup](https://docs.cloud.google.com/storage/docs/using-public-access-prevention).
- [GCS IAM conditions and listing limitations](https://docs.cloud.google.com/storage/docs/access-control/iam) and [version-3 policy management](https://docs.cloud.google.com/storage/docs/access-control/using-iam-permissions).
- [GCS signed-URL authorization prerequisites](https://docs.cloud.google.com/storage/docs/access-control/signing-urls-with-helpers).
- [Google Cloud TLS-version organization policy and limitations](https://docs.cloud.google.com/docs/security/compliance/restrict-tls-versions).
- [GCS standard encryption](https://docs.cloud.google.com/storage/docs/encryption/default-keys), [CMEK behavior](https://docs.cloud.google.com/storage/docs/encryption/customer-managed-keys), and [service-agent and default-key setup](https://docs.cloud.google.com/storage/docs/encryption/using-customer-managed-keys).
- [Azure anonymous-access configuration and response-code caveat](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-configure).
- [Azure account property defaults](https://learn.microsoft.com/en-us/javascript/api/%40azure/arm-storage/storageaccountpropertiesupdateparameters?view=azure-node-latest) and [storage-account resource properties](https://learn.microsoft.com/en-us/azure/templates/microsoft.storage/storageaccounts).
- [Azure Shared Key prevention](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent) and [scoped Blob data roles](https://learn.microsoft.com/en-us/azure/storage/blobs/assign-azure-role-data-access).
- [Azure secure transfer](https://learn.microsoft.com/en-us/azure/storage/common/storage-require-secure-transfer), [minimum TLS configuration](https://learn.microsoft.com/en-us/azure/storage/common/transport-layer-security-configure-minimum-version), and [February 2026 TLS migration](https://learn.microsoft.com/en-us/azure/storage/common/transport-layer-security-configure-migrate-to-tls2).
- [Azure network restrictions](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security) and [private endpoints and DNS](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints).
- [Azure account CLI, SAS-policy flags, and delegation-key revocation](https://learn.microsoft.com/en-us/cli/azure/storage/account) and [Blob CLI SAS parameters](https://learn.microsoft.com/en-us/cli/azure/storage/blob).
- [Azure user delegation SAS CLI](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-cli), [permissions and revocation semantics](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas), [SAS expiration policy](https://learn.microsoft.com/en-us/azure/storage/common/sas-expiration-policy), and [stored access policy revocation](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy).
- [Azure immutable storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview) and [container retention configuration](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope).
- [Supabase createBucket](https://supabase.com/docs/reference/javascript/file-buckets-createbucket) and [createSignedUrl](https://supabase.com/docs/reference/javascript/file-buckets-createsignedurl).
- [Supabase ownership](https://supabase.com/docs/guides/storage/security/ownership), [Storage path helpers](https://supabase.com/docs/guides/storage/schema/helper-functions), [RLS policy behavior](https://supabase.com/docs/guides/database/postgres/row-level-security), and [privileged API keys](https://supabase.com/docs/guides/api/api-keys).
- [Supabase update](https://supabase.com/docs/reference/javascript/file-buckets-update), [move](https://supabase.com/docs/reference/javascript/file-buckets-move), [copy](https://supabase.com/docs/reference/javascript/file-buckets-copy), and [remove](https://supabase.com/docs/reference/javascript/file-buckets-remove).
