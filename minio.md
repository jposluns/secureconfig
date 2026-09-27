---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "4db98ad33edbad722c0202564a14187d426550238d69988bdcf4ae85f867d9e8",
  "components": {
    "aistor": {
      "name": "AIStor documentation",
      "basis": "unknown",
      "sources": {
        "s9719f7f2368e": "https://github.com/minio/minio",
        "s676cd1d021a2": "https://github.com/minio/minio/blob/f0b91e5504663c4672da451877857b57c3345295/cmd/common-main.go",
        "s010df9b91c3e": "https://docs.min.io/aistor/reference/aistor-server/settings/root-credentials/",
        "s832ebbd6b12d": "https://docs.min.io/aistor/reference/aistor-server/settings/#file-based-environment-variables",
        "s77cdb5121ee1": "https://docs.min.io/aistor/administration/iam/",
        "s3be1eade5af1": "https://docs.min.io/aistor/administration/iam/access/",
        "s72c067e99d16": "https://docs.min.io/aistor/administration/iam/access/oidc-access/",
        "s2a0ce722d930": "https://docs.min.io/aistor/administration/iam/identity/oidc-identity/",
        "sa62a16f9bfe7": "https://docs.min.io/aistor/installation/linux/network-encryption/",
        "sb9d5614881d7": "https://docs.min.io/aistor/reference/aistor-server/",
        "s410c1a1103fc": "https://docs.min.io/aistor/reference/aistor-server/settings/console/",
        "sedcc92753b24": "https://docs.min.io/aistor/reference/aistor-server/settings/core/",
        "s5e54dfb548ff": "https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/",
        "sce35ebdaa862": "https://docs.min.io/aistor/reference/aistor-server/settings/iam/sts/",
        "sfc2a9f6aaa82": "https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/audit-event-queue/",
        "s077155dd0d0a": "https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/kafka-audit-logs/",
        "s5ffb30993d29": "https://docs.min.io/aistor/reference/aistor-server/settings/metrics-and-logging/webhook-audit-logs/",
        "sd117ab9c22cf": "https://docs.min.io/aistor/reference/aistor-server/settings/server-side-encryption/",
        "sb91d4a3416c9": "https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-get-json/",
        "s9e52474eb6af": "https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/",
        "sdebcaf3c2435": "https://docs.min.io/aistor/administration/console/security-and-access/",
        "s23c3415f6dfd": "https://docs.min.io/aistor/reference/cli/admin/mc-admin-user/mc-admin-user-add/",
        "s5e275951f4af": "https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-create/",
        "s3bd415ac0205": "https://docs.min.io/aistor/reference/cli/admin/mc-admin-policy/mc-admin-policy-attach/",
        "s6e38b824d6a7": "https://docs.min.io/aistor/reference/cli/admin/mc-admin-accesskey/mc-admin-accesskey-create/",
        "scd10702aba20": "https://docs.min.io/aistor/reference/cli/mc-alias/mc-alias-import/",
        "s53d35aac0c14": "https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/",
        "s19e2a1dc1a62": "https://docs.min.io/aistor/reference/cli/mc-share/mc-share-download/",
        "s9f3d8a13f89a": "https://docs.min.io/aistor/installation/linux/server-side-encryption/",
        "s725b0aa69279": "https://docs.min.io/aistor/installation/linux/server-side-encryption/aistor-keymanager/",
        "scb4e8f6b45b9": "https://docs.min.io/aistor/installation/linux/server-side-encryption/minio-key-encryption-service/",
        "s7384f2f26863": "https://docs.min.io/aistor/reference/cli/mc-encrypt/mc-encrypt-set/",
        "s6203e074bac7": "https://docs.min.io/aistor/administration/object-locking-and-immutability/",
        "s8d71fab3c175": "https://docs.min.io/aistor/reference/cli/mc-mb/",
        "sbcb4c73423fb": "https://docs.min.io/aistor/reference/cli/mc-version/mc-version-enable/",
        "sd1b52461f1be": "https://docs.min.io/aistor/reference/cli/mc-retention/mc-retention-set/",
        "sf36b2625325e": "https://docs.min.io/aistor/reference/cli/mc-legalhold/mc-legalhold-set/",
        "sb375aff8811f": "https://docs.min.io/aistor/reference/cli/mc-rm/",
        "s7eb5037577a9": "https://docs.min.io/aistor/operations/monitoring/audit-logging/",
        "s624eb11b369c": "https://docs.min.io/aistor/operations/monitoring/audit-logging/kafka-audit-logging/",
        "s8b922d2cc573": "https://docs.min.io/aistor/operations/monitoring/audit-logging/webhook-audit-logging/",
        "s060498cf1d28": "https://docs.min.io/aistor/reference/cli/mc-cat/",
        "s8aab14fd9241": "https://docs.min.io/aistor/reference/cli/mc-pipe/",
        "sa1b121169978": "https://docs.min.io/aistor/reference/cli/mc-encrypt/mc-encrypt-info/",
        "s0c9db42c9d8d": "https://docs.min.io/aistor/reference/cli/mc-stat/",
        "s79346e27156b": "https://docs.min.io/aistor/reference/cli/mc-retention/mc-retention-info/",
        "s4e625044ee38": "https://docs.min.io/aistor/operations/monitoring/metrics-and-alerts/metrics-v3/"
      }
    },
    "console": {
      "name": "MinIO console source",
      "basis": "f0b91e5504663c4672da451877857b57c3345295",
      "sources": {
        "s676cd1d021a2": "https://github.com/minio/minio/blob/f0b91e5504663c4672da451877857b57c3345295/cmd/common-main.go"
      }
    },
    "aws": {
      "name": "AWS signature-condition semantics",
      "basis": "unknown",
      "sources": {
        "s724c81d09245": "https://docs.aws.amazon.com/AmazonS3/latest/developerguide/bucket-policy-s3-sigv4-conditions.html"
      }
    }
  },
  "claims": {
    "lifecycle": {"text": "Community repository was archived 2026-04-25 and receives no fixes; guide settings target AIStor Free/Enterprise and call for migration.", "components": ["aistor"], "sources": ["aistor:s9719f7f2368e", "aistor:s676cd1d021a2"], "status": "REASONED"},
    "root-files": {"text": "Root credentials come from protected regular 0600 files without whitespace/newlines; set only *_FILE paths, remove overriding direct values and start a fresh process.", "components": ["aistor"], "sources": ["aistor:s010df9b91c3e", "aistor:s832ebbd6b12d"], "status": "REASONED"},
    "root-default": {"text": "Without direct credentials or files, root defaults minioadmin/minioadmin; root is administrative and applications need scoped keys.", "components": ["aistor"], "sources": ["aistor:s77cdb5121ee1", "aistor:s3be1eade5af1", "aistor:s72c067e99d16", "aistor:s2a0ce722d930"], "status": "REASONED"},
    "tls": {"text": "public.crt/private.key under HOME/.minio/certs or certs-dir enable HTTPS; clients trust the CA without disabling verification.", "components": ["aistor"], "sources": ["aistor:sa62a16f9bfe7"], "status": "REASONED"},
    "api-bind": {"text": "API address defaults :9000 across IPv4/IPv6 interfaces; bind explicit loopback/private and expose only intended TLS endpoints.", "components": ["aistor"], "sources": ["aistor:sb9d5614881d7", "aistor:s832ebbd6b12d", "aistor:s410c1a1103fc", "aistor:sedcc92753b24", "aistor:s5e54dfb548ff", "aistor:sce35ebdaa862", "aistor:sfc2a9f6aaa82", "aistor:s077155dd0d0a", "aistor:s5ffb30993d29", "aistor:s010df9b91c3e", "aistor:sd117ab9c22cf"], "status": "REASONED"},
    "console-bind": {"text": "Console address is independent of API binding; unset chooses a logged dynamic port and a hostless address binds wildcard; set explicit private host/port.", "components": ["aistor", "console"], "sources": ["aistor:sb9d5614881d7", "aistor:s832ebbd6b12d", "aistor:s410c1a1103fc", "aistor:sedcc92753b24", "aistor:s5e54dfb548ff", "aistor:sce35ebdaa862", "aistor:sfc2a9f6aaa82", "aistor:s077155dd0d0a", "aistor:s5ffb30993d29", "aistor:s010df9b91c3e", "aistor:sd117ab9c22cf", "console:s676cd1d021a2"], "status": "REASONED"},
    "anonymous": {"text": "Buckets are private unless policy grants access; inspect complete anonymous JSON including uploads, prefixes and conditions, independently of identity policies.", "components": ["aistor"], "sources": ["aistor:sb91d4a3416c9", "aistor:s9e52474eb6af"], "status": "REASONED"},
    "console-disable": {"text": "MINIO_BROWSER=off disables embedded Console after restart on every node; disabling browser redirection alone does not.", "components": ["aistor"], "sources": ["aistor:s410c1a1103fc"], "status": "REASONED"},
    "concurrency": {"text": "Automatic API budget follows RAM; REQUESTS_MAX is cluster-wide concurrent S3/admin requests divided among nodes, not RPS or connections; 64 is only an illustrative choice.", "components": ["aistor"], "sources": ["aistor:sedcc92753b24"], "status": "REASONED"},
    "builtin-policies": {"text": "readonly/writeonly cover deployment-wide object operations; readwrite grants all S3 actions, consoleAdmin adds admin access, and readonly does not list buckets.", "components": ["aistor"], "sources": ["aistor:s3be1eade5af1", "aistor:s72c067e99d16"], "status": "REASONED"},
    "parent": {"text": "Create a non-root app parent in Console with narrow user/group grants; documented mc admin user add requires a positional secret.", "components": ["aistor"], "sources": ["aistor:sdebcaf3c2435", "aistor:s23c3415f6dfd"], "status": "REASONED"},
    "policy": {"text": "Custom app policy grants location/list plus object read/write for one bucket, without deletion/admin; remove unused actions and avoid replacing an existing policy inadvertently.", "components": ["aistor"], "sources": ["aistor:s3be1eade5af1", "aistor:s72c067e99d16", "aistor:s5e275951f4af", "aistor:s3bd415ac0205"], "status": "REASONED"},
    "access-key": {"text": "Create an explicit-parent generated key with 24h expiry and protected output; inline policy only restricts inherited rights and is limited to 4096 bytes; rotate before expiry.", "components": ["aistor"], "sources": ["aistor:s6e38b824d6a7"], "status": "REASONED"},
    "alias": {"text": "Alias import reads protected JSON from stdin; protect imported and mc configuration credentials, and prove authentication with a signed operation.", "components": ["aistor"], "sources": ["aistor:scd10702aba20"], "status": "REASONED"},
    "oidc-role": {"text": "RoleArn mapping assigns configured policies to every admitted identity using the role; choose a narrow existing role policy.", "components": ["aistor"], "sources": ["aistor:s72c067e99d16", "aistor:s5e54dfb548ff"], "status": "REASONED"},
    "oidc-claim": {"text": "Claim mapping uses IdP-controlled policy names; role_policy and claim_name are mutually exclusive, named suffixes are case-sensitive, and only one provider can use claim mapping.", "components": ["aistor"], "sources": ["aistor:s2a0ce722d930", "aistor:s5e54dfb548ff"], "status": "REASONED"},
    "oidc-unmapped": {"text": "Unmapped identities gain no identity-based access, but anonymous bucket grants still apply.", "components": ["aistor"], "sources": ["aistor:s72c067e99d16"], "status": "REASONED"},
    "sts-duration": {"text": "WebIdentity explicit DurationSeconds accepts 900-31536000 and can override JWT expiry; MINIO_STS_DURATION is a default, with sts:DurationSeconds available as a policy restriction.", "components": ["aistor"], "sources": ["aistor:s53d35aac0c14", "aistor:sce35ebdaa862", "aistor:s3be1eade5af1", "aistor:s72c067e99d16"], "status": "REASONED"},
    "presign": {"text": "Presigned URLs are credentials; mc share download defaults seven days, while the example requests five minutes and stores output privately.", "components": ["aistor"], "sources": ["aistor:s19e2a1dc1a62"], "status": "REASONED"},
    "signature-age": {"text": "Explicit deny for signatureAge above 600000 ms restricts the attached parent identity, not unrelated identities/OIDC/anonymous grants; AIStor behavior is reasoned from supported keys and AWS semantics.", "components": ["aistor", "aws"], "sources": ["aistor:s3be1eade5af1", "aistor:s72c067e99d16", "aws:s724c81d09245"], "status": "REASONED"},
    "kms": {"text": "SSE-S3 uses the default external key and SSE-KMS selects a key; configure MinIO KMS endpoint/enclave/key/API key with trusted CA before restarting.", "components": ["aistor"], "sources": ["aistor:s9f3d8a13f89a", "aistor:s725b0aa69279", "aistor:scb4e8f6b45b9"], "status": "REASONED"},
    "kes": {"text": "Legacy KES supports third-party KMS; use certificate/key together with CAPATH, mutually exclusive with KES API key and with MinIO KMS configuration.", "components": ["aistor"], "sources": ["aistor:sd117ab9c22cf", "aistor:scb4e8f6b45b9"], "status": "REASONED"},
    "auto-encryption": {"text": "AUTO_ENCRYPTION defaults on only with a configured key manager and encrypts new writes using SSE-KMS; off needs explicit bucket encryption.", "components": ["aistor"], "sources": ["aistor:sd117ab9c22cf"], "status": "REASONED"},
    "bucket-encryption": {"text": "mc encrypt set selects SSE-KMS key or SSE-S3 default; settings affect subsequent writes, not historical objects or versions.", "components": ["aistor"], "sources": ["aistor:s7384f2f26863"], "status": "REASONED"},
    "backend-encryption": {"text": "Enabling SSE encrypts IAM/configuration backend data irreversibly; startup depends on retained backend key and key-manager access, regardless of automatic object encryption.", "components": ["aistor"], "sources": ["aistor:s725b0aa69279", "aistor:scb4e8f6b45b9"], "status": "REASONED"},
    "object-lock": {"text": "New bucket with-lock enables versioning but no retention duration; AIStor RELEASE.2025-05-20T20-30-00Z+ can retrofit existing versioned buckets, not through Console.", "components": ["aistor"], "sources": ["aistor:s6203e074bac7", "aistor:s8d71fab3c175", "aistor:sbcb4c73423fb"], "status": "REASONED"},
    "retention-modes": {"text": "GOVERNANCE permits authorized bypass; COMPLIANCE prevents protected-version deletion even by root until expiry. Remove bypass permission from application identities.", "components": ["aistor"], "sources": ["aistor:s6203e074bac7"], "status": "REASONED"},
    "retention-default": {"text": "Default retention ignores other flags including recursive and governs new objects without overrides; explicitly protect historical version IDs and inspect retain-until dates.", "components": ["aistor"], "sources": ["aistor:sd1b52461f1be"], "status": "REASONED"},
    "legal-hold": {"text": "Legal hold is indefinite and requires PutObjectLegalHold to set/lift; both hold release and retention expiry are needed when combined.", "components": ["aistor"], "sources": ["aistor:sf36b2625325e"], "status": "REASONED"},
    "delete-marker": {"text": "Ordinary deletes can hide retained versions behind a delete marker; verify exact version IDs.", "components": ["aistor"], "sources": ["aistor:s6203e074bac7", "aistor:sb375aff8811f"], "status": "REASONED"},
    "audit-default": {"text": "No audit destination is enabled by default; publish sensitive records to independently protected remote storage.", "components": ["aistor"], "sources": ["aistor:s7eb5037577a9", "aistor:s624eb11b369c", "aistor:s8b922d2cc573"], "status": "REASONED"},
    "audit-webhook": {"text": "Enable HTTPS webhook with authentication value supplied verbatim, certificate verification and persistent audit queue; restart every node.", "components": ["aistor"], "sources": ["aistor:s5ffb30993d29", "aistor:s8b922d2cc573"], "status": "REASONED"},
    "audit-kafka": {"text": "Kafka TLS defaults off; explicitly enable verified TLS and supported SASL with topic-scoped credentials; example PLAIN is only over TLS.", "components": ["aistor"], "sources": ["aistor:s077155dd0d0a", "aistor:s624eb11b369c"], "status": "REASONED"},
    "audit-queue": {"text": "Persistent per-node queue needs service read/write/list access; delivery retries can lose events when full, and webhook 2xx proves acknowledgement rather than durability.", "components": ["aistor"], "sources": ["aistor:sfc2a9f6aaa82", "aistor:s8b922d2cc573"], "status": "REASONED"},
    "verify-exposure": {"text": "Anonymous service/bucket/object reads must be denied at MinIO with known fixtures; full policy review and actual console-port external probes are independent controls.", "components": ["aistor"], "sources": ["aistor:sb91d4a3416c9", "aistor:sb9d5614881d7", "aistor:s832ebbd6b12d", "aistor:s410c1a1103fc", "aistor:sedcc92753b24", "aistor:s5e54dfb548ff", "aistor:sce35ebdaa862", "aistor:sfc2a9f6aaa82", "aistor:s077155dd0d0a", "aistor:s5ffb30993d29", "aistor:s010df9b91c3e", "aistor:sd117ab9c22cf"], "status": "REASONED", "verify": [1]},
    "verify-scope": {"text": "Root reads both known private fixtures; app reads/writes its own bucket but cannot read the other after anonymous grants are excluded.", "components": ["aistor"], "sources": ["aistor:s3be1eade5af1", "aistor:s72c067e99d16", "aistor:s060498cf1d28", "aistor:s8aab14fd9241"], "status": "REASONED", "verify": [2]},
    "verify-encryption": {"text": "New ordinary write must succeed with intended SSE/key metadata versus a successful unencrypted control; bucket info alone proves no historical-object state.", "components": ["aistor"], "sources": ["aistor:sa1b121169978", "aistor:s0c9db42c9d8d", "aistor:s725b0aa69279"], "status": "REASONED", "verify": [3]},
    "verify-retention": {"text": "Under the same root identity, unlocked exact-version deletion succeeds and COMPLIANCE-protected deletion fails while that version and future retention remain readable.", "components": ["aistor"], "sources": ["aistor:s79346e27156b", "aistor:sb375aff8811f", "aistor:s0c9db42c9d8d"], "status": "REASONED", "verify": [4, 5]},
    "verify-audit": {"text": "Correlate successful write/read and denied read with persisted receiver events and durability; S3 success or webhook acknowledgement alone proves no stored audit.", "components": ["aistor"], "sources": ["aistor:s7eb5037577a9", "aistor:s624eb11b369c", "aistor:s8b922d2cc573"], "status": "REASONED", "verify": [6]},
    "verify-oidc": {"text": "Fresh mapped STS credentials must read only the app fixture versus a broad-policy control; also test an unmapped identity and explicit duration beyond shorter JWT/default.", "components": ["aistor"], "sources": ["aistor:s72c067e99d16", "aistor:s53d35aac0c14"], "status": "REASONED"},
    "verify-url-expiry": {"text": "Same five-minute URL succeeds immediately and fails after six minutes while a new URL works; protect URL stdin and correlate AIStor denial.", "components": ["aistor"], "sources": ["aistor:s19e2a1dc1a62"], "status": "REASONED", "verify": [7]},
    "verify-signature-age": {"text": "One-hour URL should work after eleven minutes without age denial, fail then with the policy, and still work fresh; exclude expiry and transport errors.", "components": ["aistor", "aws"], "sources": ["aistor:s3be1eade5af1", "aistor:s72c067e99d16", "aws:s724c81d09245"], "status": "REASONED", "verify": [7]},
    "verify-console": {"text": "After BROWSER=off restart, verify effective setting, absent Console listener and successful S3 read; redirect-only disablement leaves direct UI available.", "components": ["aistor"], "sources": ["aistor:s410c1a1103fc", "aistor:s060498cf1d28"], "status": "REASONED", "verify": [8]},
    "verify-concurrency": {"text": "Four-node budget 64 should constrain admission to 16 per node under saturating signed load; compare measured inflight/waiting metrics with automatic sizing, not RPS or a guessed rejection code.", "components": ["aistor"], "sources": ["aistor:sedcc92753b24", "aistor:s4e625044ee38"], "status": "REASONED"}
  }
}
---
# MinIO: credentials, TLS, encryption, and object protection

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| lifecycle: Community repository was archived 2026-04-25 and receives no fixes; guide settings target AIStor Free/Enterprise and call for migration. | AIStor documentation unknown | REASONED |
| root-files: Root credentials come from protected regular 0600 files without whitespace/newlines; set only *_FILE paths, remove overriding direct values and start a fresh process. | AIStor documentation unknown | REASONED |
| root-default: Without direct credentials or files, root defaults minioadmin/minioadmin; root is administrative and applications need scoped keys. | AIStor documentation unknown | REASONED |
| tls: public.crt/private.key under HOME/.minio/certs or certs-dir enable HTTPS; clients trust the CA without disabling verification. | AIStor documentation unknown | REASONED |
| api-bind: API address defaults :9000 across IPv4/IPv6 interfaces; bind explicit loopback/private and expose only intended TLS endpoints. | AIStor documentation unknown | REASONED |
| console-bind: Console address is independent of API binding; unset chooses a logged dynamic port and a hostless address binds wildcard; set explicit private host/port. | AIStor documentation unknown; MinIO console source f0b91e5504663c4672da451877857b57c3345295 | REASONED |
| anonymous: Buckets are private unless policy grants access; inspect complete anonymous JSON including uploads, prefixes and conditions, independently of identity policies. | AIStor documentation unknown | REASONED |
| console-disable: MINIO_BROWSER=off disables embedded Console after restart on every node; disabling browser redirection alone does not. | AIStor documentation unknown | REASONED |
| concurrency: Automatic API budget follows RAM; REQUESTS_MAX is cluster-wide concurrent S3/admin requests divided among nodes, not RPS or connections; 64 is only an illustrative choice. | AIStor documentation unknown | REASONED |
| builtin-policies: readonly/writeonly cover deployment-wide object operations; readwrite grants all S3 actions, consoleAdmin adds admin access, and readonly does not list buckets. | AIStor documentation unknown | REASONED |
| parent: Create a non-root app parent in Console with narrow user/group grants; documented mc admin user add requires a positional secret. | AIStor documentation unknown | REASONED |
| policy: Custom app policy grants location/list plus object read/write for one bucket, without deletion/admin; remove unused actions and avoid replacing an existing policy inadvertently. | AIStor documentation unknown | REASONED |
| access-key: Create an explicit-parent generated key with 24h expiry and protected output; inline policy only restricts inherited rights and is limited to 4096 bytes; rotate before expiry. | AIStor documentation unknown | REASONED |
| alias: Alias import reads protected JSON from stdin; protect imported and mc configuration credentials, and prove authentication with a signed operation. | AIStor documentation unknown | REASONED |
| oidc-role: RoleArn mapping assigns configured policies to every admitted identity using the role; choose a narrow existing role policy. | AIStor documentation unknown | REASONED |
| oidc-claim: Claim mapping uses IdP-controlled policy names; role_policy and claim_name are mutually exclusive, named suffixes are case-sensitive, and only one provider can use claim mapping. | AIStor documentation unknown | REASONED |
| oidc-unmapped: Unmapped identities gain no identity-based access, but anonymous bucket grants still apply. | AIStor documentation unknown | REASONED |
| sts-duration: WebIdentity explicit DurationSeconds accepts 900-31536000 and can override JWT expiry; MINIO_STS_DURATION is a default, with sts:DurationSeconds available as a policy restriction. | AIStor documentation unknown | REASONED |
| presign: Presigned URLs are credentials; mc share download defaults seven days, while the example requests five minutes and stores output privately. | AIStor documentation unknown | REASONED |
| signature-age: Explicit deny for signatureAge above 600000 ms restricts the attached parent identity, not unrelated identities/OIDC/anonymous grants; AIStor behavior is reasoned from supported keys and AWS semantics. | AIStor documentation unknown; AWS signature-condition semantics unknown | REASONED |
| kms: SSE-S3 uses the default external key and SSE-KMS selects a key; configure MinIO KMS endpoint/enclave/key/API key with trusted CA before restarting. | AIStor documentation unknown | REASONED |
| kes: Legacy KES supports third-party KMS; use certificate/key together with CAPATH, mutually exclusive with KES API key and with MinIO KMS configuration. | AIStor documentation unknown | REASONED |
| auto-encryption: AUTO_ENCRYPTION defaults on only with a configured key manager and encrypts new writes using SSE-KMS; off needs explicit bucket encryption. | AIStor documentation unknown | REASONED |
| bucket-encryption: mc encrypt set selects SSE-KMS key or SSE-S3 default; settings affect subsequent writes, not historical objects or versions. | AIStor documentation unknown | REASONED |
| backend-encryption: Enabling SSE encrypts IAM/configuration backend data irreversibly; startup depends on retained backend key and key-manager access, regardless of automatic object encryption. | AIStor documentation unknown | REASONED |
| object-lock: New bucket with-lock enables versioning but no retention duration; AIStor RELEASE.2025-05-20T20-30-00Z+ can retrofit existing versioned buckets, not through Console. | AIStor documentation unknown | REASONED |
| retention-modes: GOVERNANCE permits authorized bypass; COMPLIANCE prevents protected-version deletion even by root until expiry. Remove bypass permission from application identities. | AIStor documentation unknown | REASONED |
| retention-default: Default retention ignores other flags including recursive and governs new objects without overrides; explicitly protect historical version IDs and inspect retain-until dates. | AIStor documentation unknown | REASONED |
| legal-hold: Legal hold is indefinite and requires PutObjectLegalHold to set/lift; both hold release and retention expiry are needed when combined. | AIStor documentation unknown | REASONED |
| delete-marker: Ordinary deletes can hide retained versions behind a delete marker; verify exact version IDs. | AIStor documentation unknown | REASONED |
| audit-default: No audit destination is enabled by default; publish sensitive records to independently protected remote storage. | AIStor documentation unknown | REASONED |
| audit-webhook: Enable HTTPS webhook with authentication value supplied verbatim, certificate verification and persistent audit queue; restart every node. | AIStor documentation unknown | REASONED |
| audit-kafka: Kafka TLS defaults off; explicitly enable verified TLS and supported SASL with topic-scoped credentials; example PLAIN is only over TLS. | AIStor documentation unknown | REASONED |
| audit-queue: Persistent per-node queue needs service read/write/list access; delivery retries can lose events when full, and webhook 2xx proves acknowledgement rather than durability. | AIStor documentation unknown | REASONED |
| verify-exposure: Anonymous service/bucket/object reads must be denied at MinIO with known fixtures; full policy review and actual console-port external probes are independent controls. | AIStor documentation unknown | REASONED |
| verify-scope: Root reads both known private fixtures; app reads/writes its own bucket but cannot read the other after anonymous grants are excluded. | AIStor documentation unknown | REASONED |
| verify-encryption: New ordinary write must succeed with intended SSE/key metadata versus a successful unencrypted control; bucket info alone proves no historical-object state. | AIStor documentation unknown | REASONED |
| verify-retention: Under the same root identity, unlocked exact-version deletion succeeds and COMPLIANCE-protected deletion fails while that version and future retention remain readable. | AIStor documentation unknown | REASONED |
| verify-audit: Correlate successful write/read and denied read with persisted receiver events and durability; S3 success or webhook acknowledgement alone proves no stored audit. | AIStor documentation unknown | REASONED |
| verify-oidc: Fresh mapped STS credentials must read only the app fixture versus a broad-policy control; also test an unmapped identity and explicit duration beyond shorter JWT/default. | AIStor documentation unknown | REASONED |
| verify-url-expiry: Same five-minute URL succeeds immediately and fails after six minutes while a new URL works; protect URL stdin and correlate AIStor denial. | AIStor documentation unknown | REASONED |
| verify-signature-age: One-hour URL should work after eleven minutes without age denial, fail then with the policy, and still work fresh; exclude expiry and transport errors. | AIStor documentation unknown; AWS signature-condition semantics unknown | REASONED |
| verify-console: After BROWSER=off restart, verify effective setting, absent Console listener and successful S3 read; redirect-only disablement leaves direct UI available. | AIStor documentation unknown | REASONED |
| verify-concurrency: Four-node budget 64 should constrain admission to 16 per node under saturating signed load; compare measured inflight/waiting metrics with automatic sizing, not RPS or a guessed rejection code. | AIStor documentation unknown | REASONED |
<!-- version-basis:end -->

MinIO serves S3-compatible object storage; an exposed instance with weak or well-known credentials hands over every bucket. Both the S3 API port and the web console need the same care.

Lifecycle note, as of September 2026: the MinIO community repository on GitHub was archived on 2026-04-25 and carries the notice that it is no longer maintained; MinIO now ships AIStor Free (a standalone edition under a free licence) and AIStor Enterprise. The settings below are documented for AIStor. An archived community build receives no security fixes, so treat running one as a finding and plan the migration.

## 1. Set real root credentials

Provision `/etc/minio/root-user` and `/etc/minio/root-password` through your secret manager before starting the server. Each must be a regular file owned by the server account, mode `0600`, under a directory other accounts cannot traverse, write to or replace, with no ACL granting them access. Each contains only its credential, with no whitespace or trailing newline. Keep these files and their backups out of source control.

In the server's launch configuration, set only the file paths:

```dotenv
MINIO_ROOT_USER_FILE=/etc/minio/root-user
MINIO_ROOT_PASSWORD_FILE=/etc/minio/root-password
```

AIStor reads these files at startup. Remove `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from the launch environment and any environment file: a direct value takes precedence over its `_FILE` counterpart. Start a fresh server process after changing its launch configuration. This assumes the protected files already exist and the launcher supplies these path variables; it does not create credentials or start a server. The shell and launch arguments contain only paths, while the server account and root can still read the credential files and server memory. See the vendor's [file-based settings](https://docs.min.io/aistor/reference/aistor-server/settings/#file-based-environment-variables) and [root credential file requirements](https://docs.min.io/aistor/reference/aistor-server/settings/root-credentials/).

Never run with the `minioadmin`/`minioadmin` pair, which is still the built-in default when neither direct root credentials nor credential files are supplied; scanners try it constantly. Root credentials are for administration only: create per-application access keys with least-privilege policies (via the console or the `mc` client) so no app holds root ([authentication.md](authentication.md)).

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

For an already configured OIDC provider, choose exactly one mapping method. Remove the other method's explicit settings from both the environment and stored configuration; configuring both `role_policy` and `claim_name` is an error. Apply consistent settings across nodes and restart AIStor. The examples below set the default configuration. For a named configuration, append `_` followed by its case-sensitive name to each variable (for example `MINIO_IDENTITY_OPENID_ROLE_POLICY_PARTNERS` for a configuration named `PARTNERS`). When that configuration uses role-policy mapping, have clients supply its `RoleArn` in their STS request. Claim mapping can serve only one OIDC provider per deployment; every other provider must use role-policy mapping. Sources: [AIStor OIDC identity management](https://docs.min.io/aistor/administration/iam/identity/oidc-identity/), [OpenID settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/) (multiple configurations), and [OIDC access management](https://docs.min.io/aistor/administration/iam/access/oidc-access/).

Use role-policy mapping only when every identity admitted through that role should receive the section 4 application's access:

```dotenv
MINIO_IDENTITY_OPENID_ROLE_POLICY="app-bucket"
```

The `app-bucket` policy must already exist with the intended bucket substitutions. Clients must supply the provider's corresponding `RoleArn` in their STS request. Source: [AIStor OpenID settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/).

Alternatively, select claim mapping when identities need different policies:

```dotenv
MINIO_IDENTITY_OPENID_CLAIM_NAME="policy"
```

Configure the IdP to issue `"policy": "app-bucket"` only for identities entitled to that policy; other identities receive their own existing, narrowly scoped policy names. Treat this claim as an authorization decision controlled by the IdP administrator. An identity whose token maps to no policy gains no identity-based access; an anonymous bucket policy (sections 3 and 4) still grants its access to anyone. Sources: [AIStor OpenID settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/openid/), [OIDC identity management](https://docs.min.io/aistor/administration/iam/identity/oidc-identity/), and [OIDC access management](https://docs.min.io/aistor/administration/iam/access/oidc-access/).

Do not describe a short `MINIO_STS_DURATION` as a universal maximum. `AssumeRoleWithWebIdentity` accepts explicit `DurationSeconds` values from 900 through 31536000 seconds (365 days); with a usable JWT expiry, an explicit duration takes precedence over that expiry. `MINIO_STS_DURATION` is a default, not this ceiling. AIStor separately documents the native `sts:DurationSeconds` policy condition for restricting WebIdentity credential duration. Sources: [AssumeRoleWithWebIdentity](https://docs.min.io/aistor/developers/security-token-service/assumerolewithwebidentity/), [STS settings](https://docs.min.io/aistor/reference/aistor-server/settings/iam/sts/), and [access-management condition keys](https://docs.min.io/aistor/administration/iam/access/).

### 4.2. Shorten presigned URLs and cap signature age

A presigned download URL contains access credentials: possession permits its authorized download even when the bucket is private. Generate it with the scoped `app` identity and a short expiry; if the `app` alias does not exist yet, import it from the section 4 access key with the stdin form in section 8 (`mc alias import app < /path/to/REPLACE_WITH_APP_ALIAS.json`). Save the output in a new file inside an owner-only directory, and share the URL through a protected channel:

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

REASONED: following block; alias JSON follows the cited mc alias import schema; no minio or mc binary or live endpoint was available.

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

REASONED: following block; exposure and alias-import expectations follow the cited server and anonymous-policy documentation; no minio, mc or container runtime was available.

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

REASONED: following block; scoped-access comparisons follow the cited access-management and mc documentation; no minio, mc or container runtime was available.

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

REASONED: following block; encryption comparison follows the cited KMS, encrypt and stat documentation; no live deployment or KMS was available.

```bash
mc encrypt info mys3/REPLACE_WITH_BUCKET
printf '%s\n' 'encryption probe' | mc pipe mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_NEW_ENCRYPTION_PROBE
mc stat mys3/REPLACE_WITH_BUCKET/REPLACE_WITH_NEW_ENCRYPTION_PROBE
```

Confirm the bucket default and the newly written object's SSE metadata, including the intended KMS key for SSE-KMS. In a disposable unencrypted comparison deployment with no key manager, a successful ordinary write lacks SSE metadata; after the control is configured, the new write must carry it. A failed write proves neither state. `mc encrypt info` reports bucket configuration, not historical-object encryption, and absence of a bucket rule does not prove plaintext when server-wide automatic encryption applies. Sources: `mc encrypt info`, `mc encrypt set`, `mc stat`, and the MinIO KMS setup guide.

**Retention, REASONED:** no `minio`, `mc`, or container runtime is available here. Use a newly created disposable bucket with locking enabled and no default retention. Stop if creation or either write fails. These fixtures compare an unlocked version with a protected version under the same root identity.

REASONED: following block; retention fixtures follow the cited object-locking and mc documentation; no live deployment was available.

```bash
mc mb --with-lock mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET
printf '%s\n' 'unlocked control' | mc pipe mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
printf '%s\n' 'retained probe' | mc pipe mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
mc stat mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/control.txt
mc stat mys3/REPLACE_WITH_NEW_RETENTION_TEST_BUCKET/protected.txt
```

Record the exact version IDs from the successful object inspections. Substitute them below. The protected fixture receives a one-day COMPLIANCE lock and cannot be deleted early, including by root.

REASONED: following block; exact-version deletion comparison follows the cited retention, rm and stat documentation; no live deployment was available.

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

REASONED: following block; durable delivery comparison follows the cited audit documentation; no live deployment or receiver was available.

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

REASONED: following block; URL expiry and signature-age comparisons follow the cited share-download and policy documentation; no live AIStor or mc was available.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
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

REASONED: following block; Console disablement follows the cited Console settings; no live AIStor or mc was available.

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

REASONED from the cited AIStor documentation: the exposure probes and all four service checks against exposed and fixed states on live AIStor with `mc`, a KMS, and an independent durable audit receiver; record versions, commands, outcomes, and receiver evidence. These capabilities were unavailable in the authoring environment.

REASONED from the cited AIStor documentation: OIDC role-policy and claim-policy scoping, including an unmapped identity and explicit STS duration overriding a shorter default and JWT expiry; five-minute presigned-URL expiry and independent signature-age denial before a longer URL expires; embedded Console disablement with successful S3 access and a redirect-only comparison; and cluster-wide API concurrency budgeting divided among nodes under measured load. Add an IdP, authenticated STS/S3 test client, load client, and per-node metrics collection to the existing prerequisites. Record AIStor and client RELEASE tags, redacted requests, effective settings, positive controls, denials, timing, listener evidence, and load measurements. All four additions are REASONED, not demonstrated.

## Sources (checked September 2026)

- AIStor root credential files and file-variable precedence: https://docs.min.io/aistor/reference/aistor-server/settings/root-credentials/ and https://docs.min.io/aistor/reference/aistor-server/settings/#file-based-environment-variables
- MinIO network encryption (certs directory, public.crt/private.key, --certs-dir): https://docs.min.io/aistor/installation/linux/network-encryption/
- MinIO: https://www.min.io/
- MinIO community repository (archived 2026-04-25, successor editions): https://github.com/minio/minio
- MinIO `mc anonymous set` (anonymous policies are set per bucket or prefix, cover download and upload, and permit actions without authentication): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-set/
- MinIO `mc anonymous get-json` (retrieve a bucket's anonymous policy as JSON to inspect grants, prefixes, and conditions): https://docs.min.io/aistor/reference/cli/mc-anonymous/mc-anonymous-get-json/
- MinIO/AIStor server address flags (`--address` defaults to `:9000` on all interfaces; `--console-address` / `MINIO_CONSOLE_ADDRESS`: a static port for the embedded console UI, or a dynamic one logged at startup when omitted): https://docs.min.io/aistor/reference/aistor-server/
- MinIO console listener in the server source (`--console-address` and its `MINIO_CONSOLE_ADDRESS` env var in `cmd/server-main.go`; `cmd/common-main.go` binds all interfaces when the host is omitted): https://github.com/minio/minio/blob/f0b91e5504663c4672da451877857b57c3345295/cmd/common-main.go
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
