---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "c68fdbadfd0e17511c4a80123ba99cccaae5a7f7b0abc38afc273abd2462e313",
  "components": {
    "oauth": {
      "name": "OAuth client credentials",
      "basis": "unknown",
      "sources": {
        "s65b02b1812cc": "https://datatracker.ietf.org/doc/html/rfc6749#section-4.4"
      }
    },
    "bearer": {
      "name": "Bearer token guidance",
      "basis": "unknown",
      "sources": {
        "sefd3dd623da3": "https://www.rfc-editor.org/info/rfc6750/"
      }
    },
    "jwt": {
      "name": "JWT access-token profile",
      "basis": "unknown",
      "sources": {
        "sc36d79fcad94": "https://www.rfc-editor.org/rfc/rfc9068.html"
      }
    },
    "python": {
      "name": "Python hmac",
      "basis": "unknown",
      "sources": {
        "s7a54556e5dac": "https://docs.python.org/3/library/hmac.html"
      }
    },
    "node": {
      "name": "Node.js crypto",
      "basis": "unknown",
      "sources": {
        "s96b80e6816a2": "https://nodejs.org/api/crypto.html"
      }
    },
    "entra": {
      "name": "Entra External ID",
      "basis": "unknown",
      "sources": {
        "s0ee5939cfc03": "https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing"
      }
    },
    "github": {
      "name": "GitHub Actions OIDC",
      "basis": "unknown",
      "sources": {
        "s65bfc1e3ee0d": "https://docs.github.com/en/actions/concepts/security/openid-connect",
        "s653a0d94dd2f": "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws",
        "sa8ed4c86a8ea": "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-google-cloud-platform",
        "s80d46a4f675c": "https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure"
      }
    },
    "aws": {
      "name": "AWS IAM and credential action",
      "basis": "unknown",
      "sources": {
        "s6fff7087bca4": "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html",
        "se185ac33f225": "https://github.com/aws-actions/configure-aws-credentials"
      }
    },
    "google": {
      "name": "Google Cloud federation and auth action",
      "basis": "unknown",
      "sources": {
        "s03844cd0246a": "https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines",
        "s0f874cc5b70e": "https://docs.cloud.google.com/iam/docs/workload-identity-federation",
        "saa567d0c2c78": "https://github.com/google-github-actions/auth"
      }
    },
    "azure": {
      "name": "Azure federation and login",
      "basis": "unknown",
      "sources": {
        "sb7a38a36ac47": "https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation",
        "sc70c3d4b8844": "https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust",
        "s231245f7e96b": "https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect"
      }
    },
    "spiffe": {
      "name": "SPIFFE and SPIRE",
      "basis": "unknown",
      "sources": {
        "s96e9b9e2739d": "https://spiffe.io/",
        "sfa39616d8260": "https://spiffe.io/docs/latest/spire-about/"
      }
    },
    "pki": {
      "name": "Certificate revocation",
      "basis": "unknown",
      "sources": {
        "s93ee2b4751f8": "https://www.rfc-editor.org/info/rfc5280/"
      }
    }
  },
  "claims": {
    "key-scope": {"text": "Issue a random least-privilege key per client and environment so one client can be revoked independently.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "key-lifetime": {"text": "Give keys expiries and scheduled rotation with a short overlap for continuity.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "bearer-transport": {"text": "Send bearer keys in Authorization headers over mandatory TLS; URLs leak through history and logs.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "constant-time": {"text": "Use hmac.compare_digest or crypto.timingSafeEqual rather than plain equality; the guide requires equal byte lengths.", "components": ["python", "node"], "sources": ["python:s7a54556e5dac", "node:s96b80e6816a2"], "status": "REASONED"},
    "key-hash": {"text": "Where only verification is needed, store key hashes and show plaintext once; this is guide advice, without a hash-implementation source in Sources.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "client-grant": {"text": "Confidential clients authenticate with grant_type=client_credentials for access tokens; refresh tokens SHOULD NOT be issued, so re-authenticate.", "components": ["oauth"], "sources": ["oauth:s65b02b1812cc"], "status": "REASONED"},
    "token-scope": {"text": "Request the narrowest scope or provider audience and bound access-token lifetime and reach.", "components": ["oauth", "bearer"], "sources": ["oauth:s65b02b1812cc", "bearer:sefd3dd623da3"], "status": "REASONED"},
    "jwt-validation": {"text": "Validate access-token signature, reject alg none, check exact issuer, API audience and expiry, require at+jwt for JWT access tokens, and enforce scopes.", "components": ["jwt"], "sources": ["jwt:sc36d79fcad94"], "status": "REASONED"},
    "m2m-billing": {"text": "As of September 2026, Entra External ID M2M is billed per transaction as an add-on; hourly renewal is roughly 720 monthly transactions.", "components": ["entra"], "sources": ["entra:s0ee5939cfc03"], "status": "REASONED"},
    "client-secret": {"text": "Client credentials still need long-lived-secret protection unless replaced by federation supported by the provider.", "components": ["oauth", "azure"], "sources": ["oauth:s65b02b1812cc", "azure:sb7a38a36ac47"], "status": "REASONED"},
    "mtls-identity": {"text": "Use a separate short-lived certificate per client and keep CA keys off signed servers; mTLS is a possession factor, not human MFA.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-nginx": {"text": "nginx uses ssl_verify_client on in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-apache": {"text": "Apache uses SSLVerifyClient require in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-postgres": {"text": "PostgreSQL uses clientcert=verify-full in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-mysql": {"text": "MySQL uses REQUIRE X509 in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-redis": {"text": "Redis uses tls-auth-clients yes in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-rabbitmq": {"text": "RabbitMQ uses ssl_options.fail_if_no_peer_cert = true in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-mosquitto": {"text": "Mosquitto uses require_certificate true in the linked service guide; the cited RFC covers certificate revocation, not this product directive.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-revocation": {"text": "Replacing a key does not reject the old certificate; revoke with checked CRL/OCSP, remove it from an allowlist or wait for expiry, and test refusal.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "oidc-token": {"text": "GitHub id-token: write permits short-lived OIDC tokens from token.actions.githubusercontent.com; restrict trust to the exact repository and branch or environment.", "components": ["github"], "sources": ["github:s65bfc1e3ee0d"], "status": "REASONED"},
    "aws-action": {"text": "configure-aws-credentials uses role-to-assume and aws-region and defaults its audience to sts.amazonaws.com.", "components": ["aws"], "sources": ["aws:se185ac33f225"], "status": "REASONED"},
    "aws-trust": {"text": "AWS trust uses AssumeRoleWithWebIdentity and exact aud/sub conditions; IAM rejects absent or wildcard-only sub, and broad subjects admit outside repositories.", "components": ["aws", "github"], "sources": ["aws:s6fff7087bca4", "github:s653a0d94dd2f"], "status": "REASONED"},
    "google-provider": {"text": "Create an OIDC provider with the GitHub issuer, subject/repository mappings and an owner plus branch/environment condition.", "components": ["google"], "sources": ["google:s03844cd0246a", "google:s0f874cc5b70e"], "status": "REASONED"},
    "google-binding": {"text": "Grant workloadIdentityUser to the exact repository principalSet; prefer immutable numeric repository and owner IDs over reusable names.", "components": ["google"], "sources": ["google:s03844cd0246a", "google:s0f874cc5b70e"], "status": "REASONED"},
    "google-action": {"text": "google-github-actions/auth takes workload_identity_provider and service_account.", "components": ["google", "github"], "sources": ["google:saa567d0c2c78", "github:sa8ed4c86a8ea"], "status": "REASONED"},
    "azure-trust": {"text": "Configure the exact GitHub issuer, repository branch/environment subject and api://AzureADTokenExchange audience; wildcards are unsupported and wrong subjects fail at exchange.", "components": ["azure"], "sources": ["azure:sb7a38a36ac47", "azure:sc70c3d4b8844"], "status": "REASONED"},
    "azure-action": {"text": "azure/login needs client-id, tenant-id and subscription-id for OIDC, without a stored client secret.", "components": ["azure", "github"], "sources": ["azure:s231245f7e96b", "github:s80d46a4f675c"], "status": "REASONED"},
    "subject-format": {"text": "The guide records an immutable default subject with owner/repository IDs for repositories created after July 15, 2026; inspect the actual claim before writing trust.", "components": ["github"], "sources": ["github:s65bfc1e3ee0d"], "status": "REASONED"},
    "action-pins": {"text": "Pin actions to full commit SHAs; tags and branches can move to different code.", "components": ["github"], "sources": ["github:s65bfc1e3ee0d", "github:s653a0d94dd2f", "github:sa8ed4c86a8ea", "github:s80d46a4f675c"], "status": "REASONED"},
    "workload-attestation": {"text": "SPIFFE/SPIRE provides attested short-lived workload identities without a stored secret.", "components": ["spiffe"], "sources": ["spiffe:s96e9b9e2739d", "spiffe:sfa39616d8260"], "status": "REASONED"},
    "secret-store": {"text": "Store unavoidable machine secrets in the listed secret managers and use platform identity to authenticate, avoiding another long-lived bootstrap key.", "components": ["azure", "google", "aws"], "sources": ["azure:sb7a38a36ac47", "google:s03844cd0246a", "aws:s6fff7087bca4"], "status": "REASONED"},
    "verify-scope": {"text": "A protected header-file staging key must receive 401/403 in production while succeeding in staging; otherwise denial does not establish environment scoping.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "verify-expiry": {"text": "Revoked or expired credentials must be rejected with a service-log record identifying the client.", "components": ["bearer", "jwt"], "sources": ["bearer:sefd3dd623da3", "jwt:sc36d79fcad94"], "status": "REASONED"},
    "verify-ci": {"text": "Repository Actions secrets should hold no long-lived cloud credentials and the workflow must declare id-token: write.", "components": ["github"], "sources": ["github:s65bfc1e3ee0d", "github:s653a0d94dd2f", "github:sa8ed4c86a8ea", "github:s80d46a4f675c"], "status": "REASONED"},
    "verify-trust": {"text": "Inspect AWS sub, Google repository binding and Azure subject for exact repository plus branch/environment restriction without broad wildcard suffixes.", "components": ["aws", "google", "azure"], "sources": ["aws:s6fff7087bca4", "google:s03844cd0246a", "google:s0f874cc5b70e", "azure:sc70c3d4b8844"], "status": "REASONED"},
    "verify-artifacts": {"text": "History, working-tree and image-layer scans must show no keys; docker history alone misses copied files. Sources cites confidentiality guidance, not these scanner commands.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "verify-mtls": {"text": "Reject missing, untrusted, expired, revoked and, where identity authorization applies, unauthorized certificates while the authorized client succeeds.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"}
  }
}
---
# Machine identity: API keys, client credentials, mutual TLS, and workload identity

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| key-scope: Issue a random least-privilege key per client and environment so one client can be revoked independently. | Bearer token guidance unknown | REASONED |
| key-lifetime: Give keys expiries and scheduled rotation with a short overlap for continuity. | Bearer token guidance unknown | REASONED |
| bearer-transport: Send bearer keys in Authorization headers over mandatory TLS; URLs leak through history and logs. | Bearer token guidance unknown | REASONED |
| constant-time: Use hmac.compare_digest or crypto.timingSafeEqual rather than plain equality; the guide requires equal byte lengths. | Python hmac unknown; Node.js crypto unknown | REASONED |
| key-hash: Where only verification is needed, store key hashes and show plaintext once; this is guide advice, without a hash-implementation source in Sources. | Bearer token guidance unknown | REASONED |
| client-grant: Confidential clients authenticate with grant_type=client_credentials for access tokens; refresh tokens SHOULD NOT be issued, so re-authenticate. | OAuth client credentials unknown | REASONED |
| token-scope: Request the narrowest scope or provider audience and bound access-token lifetime and reach. | OAuth client credentials unknown; Bearer token guidance unknown | REASONED |
| jwt-validation: Validate access-token signature, reject alg none, check exact issuer, API audience and expiry, require at+jwt for JWT access tokens, and enforce scopes. | JWT access-token profile unknown | REASONED |
| m2m-billing: As of September 2026, Entra External ID M2M is billed per transaction as an add-on; hourly renewal is roughly 720 monthly transactions. | Entra External ID unknown | REASONED |
| client-secret: Client credentials still need long-lived-secret protection unless replaced by federation supported by the provider. | OAuth client credentials unknown; Azure federation and login unknown | REASONED |
| mtls-identity: Use a separate short-lived certificate per client and keep CA keys off signed servers; mTLS is a possession factor, not human MFA. | Certificate revocation unknown | REASONED |
| mtls-nginx: nginx uses ssl_verify_client on in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-apache: Apache uses SSLVerifyClient require in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-postgres: PostgreSQL uses clientcert=verify-full in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-mysql: MySQL uses REQUIRE X509 in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-redis: Redis uses tls-auth-clients yes in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-rabbitmq: RabbitMQ uses ssl_options.fail_if_no_peer_cert = true in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-mosquitto: Mosquitto uses require_certificate true in the linked service guide; the cited RFC covers certificate revocation, not this product directive. | Certificate revocation unknown | REASONED |
| mtls-revocation: Replacing a key does not reject the old certificate; revoke with checked CRL/OCSP, remove it from an allowlist or wait for expiry, and test refusal. | Certificate revocation unknown | REASONED |
| oidc-token: GitHub id-token: write permits short-lived OIDC tokens from token.actions.githubusercontent.com; restrict trust to the exact repository and branch or environment. | GitHub Actions OIDC unknown | REASONED |
| aws-action: configure-aws-credentials uses role-to-assume and aws-region and defaults its audience to sts.amazonaws.com. | AWS IAM and credential action unknown | REASONED |
| aws-trust: AWS trust uses AssumeRoleWithWebIdentity and exact aud/sub conditions; IAM rejects absent or wildcard-only sub, and broad subjects admit outside repositories. | AWS IAM and credential action unknown; GitHub Actions OIDC unknown | REASONED |
| google-provider: Create an OIDC provider with the GitHub issuer, subject/repository mappings and an owner plus branch/environment condition. | Google Cloud federation and auth action unknown | REASONED |
| google-binding: Grant workloadIdentityUser to the exact repository principalSet; prefer immutable numeric repository and owner IDs over reusable names. | Google Cloud federation and auth action unknown | REASONED |
| google-action: google-github-actions/auth takes workload_identity_provider and service_account. | Google Cloud federation and auth action unknown; GitHub Actions OIDC unknown | REASONED |
| azure-trust: Configure the exact GitHub issuer, repository branch/environment subject and api://AzureADTokenExchange audience; wildcards are unsupported and wrong subjects fail at exchange. | Azure federation and login unknown | REASONED |
| azure-action: azure/login needs client-id, tenant-id and subscription-id for OIDC, without a stored client secret. | Azure federation and login unknown; GitHub Actions OIDC unknown | REASONED |
| subject-format: The guide records an immutable default subject with owner/repository IDs for repositories created after July 15, 2026; inspect the actual claim before writing trust. | GitHub Actions OIDC unknown | REASONED |
| action-pins: Pin actions to full commit SHAs; tags and branches can move to different code. | GitHub Actions OIDC unknown | REASONED |
| workload-attestation: SPIFFE/SPIRE provides attested short-lived workload identities without a stored secret. | SPIFFE and SPIRE unknown | REASONED |
| secret-store: Store unavoidable machine secrets in the listed secret managers and use platform identity to authenticate, avoiding another long-lived bootstrap key. | Azure federation and login unknown; Google Cloud federation and auth action unknown; AWS IAM and credential action unknown | REASONED |
| verify-scope: A protected header-file staging key must receive 401/403 in production while succeeding in staging; otherwise denial does not establish environment scoping. | Bearer token guidance unknown | REASONED |
| verify-expiry: Revoked or expired credentials must be rejected with a service-log record identifying the client. | Bearer token guidance unknown; JWT access-token profile unknown | REASONED |
| verify-ci: Repository Actions secrets should hold no long-lived cloud credentials and the workflow must declare id-token: write. | GitHub Actions OIDC unknown | REASONED |
| verify-trust: Inspect AWS sub, Google repository binding and Azure subject for exact repository plus branch/environment restriction without broad wildcard suffixes. | AWS IAM and credential action unknown; Google Cloud federation and auth action unknown; Azure federation and login unknown | REASONED |
| verify-artifacts: History, working-tree and image-layer scans must show no keys; docker history alone misses copied files. Sources cites confidentiality guidance, not these scanner commands. | Bearer token guidance unknown | REASONED |
| verify-mtls: Reject missing, untrusted, expired, revoked and, where identity authorization applies, unauthorized certificates while the authorized client succeeds. | Certificate revocation unknown | REASONED |
<!-- version-basis:end -->

Machines cannot do MFA, so their credentials are long-lived by default, and long-lived credentials leak through repositories, container images, and logs. The fix is scoped, short-lived, and where possible credential-free access: a CI job or workload that holds no key cannot leak one. [authentication.md](authentication.md) sets the baseline and [secrets.md](secrets.md) covers handling and leak response; this guide covers the credential types themselves, from the weakest to the one that removes the secret entirely.

## 1. API keys and bearer tokens

The simplest machine credential and the one that leaks most. When your service issues or accepts them:

- One key per client and per environment, generated randomly (commands in [secrets.md](secrets.md)), with the least privilege that client's task needs. A shared key cannot be revoked for one client without breaking the rest.
- Give every key an expiry and rotate on a schedule, with a short overlap during which both keys work, so rotation is routine rather than an outage.
- Send keys only in a header (`Authorization: Bearer ...`) over TLS, never in a URL. RFC 6750 makes TLS mandatory for bearer tokens and says they "SHOULD NOT be passed in page URLs", because URLs land in browser history, proxy logs, and server logs.
- Compare the presented key in constant time: `hmac.compare_digest()` in Python, `crypto.timingSafeEqual()` in Node.js (both arguments must have the same byte length). A plain `==` stops at the first differing byte and leaks timing.
- Where the service only needs to verify the key, store a hash of it and compare against the hash of the presented key. Show the plaintext once at creation; a database dump then yields no usable keys.

## 2. OAuth 2.0 client credentials

For service-to-service calls to an identity provider or an API that supports it, use the client credentials grant (RFC 6749 section 4.4): the client authenticates to the token endpoint with `grant_type=client_credentials` and receives a short-lived access token; RFC 6749 says a refresh token SHOULD NOT be issued (obtain another by re-authenticating with the client credentials), and the grant is for confidential clients only. Request the narrowest `scope` (or audience, where the provider uses one) the call needs, so a stolen token is bounded in time and reach, and validate the token on the receiving side as an access token, not an ID token: verify its signature against the issuer's keys (rejecting `alg: none`), the exact issuer, an `aud` that names your API, and expiry, and for a JWT access token require the `at+jwt` type so an ID token cannot be substituted, then enforce the scopes the call needs (RFC 9068). The client secret is still a long-lived credential: store it per section 5, or replace it with a federated credential per section 4 where the provider allows. Hosted providers may bill this flow: Microsoft Entra External ID charges machine-to-machine authentication per transaction as an add-on, so a token refresh every hour is roughly 720 billable transactions a month (as of September 2026; tiers in [identity-providers.md](identity-providers.md)).

## 3. Mutual TLS

A client certificate from your own internal CA ([self-signed.md](self-signed.md)) is a possession factor for a machine: the private key never crosses the wire, and a replaced client key cuts off one client, not all of them. Replacing a key does not by itself reject the old certificate: revoke it (a CRL or OCSP the server checks), remove it from an explicit allowlist, or let it expire, and test that the old credential is refused (RFC 5280 covers revocation). It is not human MFA, and [mfa.md](mfa.md) still applies to every human path that reaches the host. The service guides already carry the server-side directives: `ssl_verify_client on` in [nginx.md](nginx.md), `SSLVerifyClient require` in [apache.md](apache.md), `clientcert=verify-full` in [postgresql.md](postgresql.md), `REQUIRE X509` in [mysql.md](mysql.md), `tls-auth-clients yes` in [redis.md](redis.md), `ssl_options.fail_if_no_peer_cert = true` in [rabbitmq.md](rabbitmq.md), and `require_certificate true` in [mosquitto.md](mosquitto.md). Issue one certificate per client, keep the CA key off the servers it signs for, and set short lifetimes so a lost key expires rather than lingers.

## 4. Workload identity federation: no long-lived cloud keys in CI

A GitHub Actions job can request a short-lived OIDC token (`permissions: id-token: write`) issued by `https://token.actions.githubusercontent.com` with a `sub` claim such as `repo:octo-org/octo-repo:ref:refs/heads/main` or `repo:octo-org/octo-repo:environment:prod`. The cloud provider trusts that issuer and exchanges the token for temporary credentials, so the repository stores no cloud key at all. The key point is the trust condition: every GitHub repository uses the same issuer, so a federation trust that admits any repository is a leaked key with extra steps. Condition on the exact repository and on the branch or environment.

**AWS.** The `aws-actions/configure-aws-credentials` step takes `role-to-assume` and `aws-region` and sends `sts.amazonaws.com` as the audience by default. The role's trust policy does the restricting:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": { "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:example-org/example-repo:ref:refs/heads/main"
    } }
  }]
}
```

IAM refuses a trust policy whose `sub` condition is absent or only a wildcard, and AWS warns that a condition wider than your organization lets "GitHub Actions from organizations or repositories outside of your control" assume the role.

**Google Cloud.** Create a Workload Identity Pool provider with `gcloud iam workload-identity-pools providers create-oidc` using `--issuer-uri="https://token.actions.githubusercontent.com"`, an `--attribute-mapping` such as `google.subject=assertion.sub,attribute.repository=assertion.repository`, and an `--attribute-condition` that pins the branch or environment as well as the owner, such as `assertion.repository_owner == 'example-org' && assertion.ref == 'refs/heads/main'` (the owner alone still admits every branch of every repo it owns, the boundary section 4 warns against). Then grant `roles/iam.workloadIdentityUser` on the service account to `principalSet://iam.googleapis.com/<POOL_RESOURCE_NAME>/attribute.repository/example-org/example-repo`, which names the exact repository. Google recommends conditions on the numeric `repository_id` and `repository_owner_id` claims over names, since a name can be re-registered by someone else. The `google-github-actions/auth` step takes `workload_identity_provider` and `service_account`.

**Azure.** Add a federated credential on the app registration or user-assigned managed identity with issuer `https://token.actions.githubusercontent.com`, subject `repo:example-org/example-repo:environment:production` (or `repo:example-org/example-repo:ref:refs/heads/main`), and audience `api://AzureADTokenExchange`, for example `az ad app federated-credential create --id <APP_ID> --parameters credential.json`. Wildcards are not supported and the subject must match exactly; a wrong subject is accepted at creation and fails only at exchange time, with no error message. The `azure/login` step then needs only `client-id`, `tenant-id`, and `subscription-id`; there is no client secret to store.

Two cautions. GitHub documents an immutable default `sub` format that includes owner and repository IDs for repositories created after July 15, 2026 (as of September 2026), so read the claim your token actually carries before writing the condition. And pin every action to a full-length commit SHA, not a release tag or branch, which a compromised upstream can move to point at new code. Inside a cluster, [SPIFFE/SPIRE](https://spiffe.io/) is the equivalent: attested, short-lived identities issued to workloads without a stored secret.

## 5. Store the machine credentials that must exist

API keys, client secrets, and client-certificate keys that cannot be federated away go in a secret manager or the platform's own store ([secrets.md](secrets.md)): AWS Secrets Manager (https://aws.amazon.com/secrets-manager/), Google Cloud Secret Manager (https://docs.cloud.google.com/secret-manager/docs/overview), Azure Key Vault (https://azure.microsoft.com/en-us/products/key-vault), HashiCorp Vault ([vault.md](vault.md); https://developer.hashicorp.com/vault) or OpenBao, its open-source fork under the Linux Foundation (https://openbao.org/), Infisical (https://infisical.com/), Doppler (https://www.doppler.com/), 1Password Secrets Automation (https://www.1password.dev/secrets-automation/), and Bitwarden Secrets Manager (https://bitwarden.com/products/secrets-manager/). The workload should authenticate to the store with its platform identity (an instance role, a managed identity, or the federation above) so the store does not become one more long-lived key.

## Verify

- A key issued to another client or environment is rejected: with the key in a mode-`0600` header file kept out of version control (never on the command line, per section 1), `curl -q -sS -o /dev/null -w '%{http_code}\n' -H @staging.header https://api.example.com/v1/status` against production returns `401` or `403`, never `200`, while the same key does succeed in its own staging environment (so the denial is environment scoping, not a broken key or endpoint).
- A revoked or expired key or token is rejected the same way, and the rejection appears in the service log with the client identity.
- The CI job holds no long-lived cloud key: the repository's Actions secrets contain no `AWS_SECRET_ACCESS_KEY`, service-account JSON, or Azure client secret, and the workflow declares `permissions: id-token: write`.
- The federation trust condition names the exact repository: the AWS `sub` condition, the Google `attribute.repository` binding, and the Azure `subject` each contain `example-org/example-repo` and pin the branch or environment, and none ends in a wildcard (`repo:example-org/*`, `repo:example-org/example-repo:*`, or a bare `*`) that would admit another repo, branch, or environment.
- `gitleaks git .` (plus a working-tree scan) and `docker history --no-trunc REPLACE_WITH_IMAGE` (plus a scan of the image layers, since history shows build steps, not files copied in) show no key ([secrets.md](secrets.md), [docker.md](docker.md)).
- An mTLS service refuses a client that presents no certificate, an untrusted or expired certificate, and (where it authorizes on identity) a validly-signed but unauthorized certificate, and refuses a certificate once revoked, while the authorized client still connects.

## Sources (checked September 2026)

- OAuth 2.0 client credentials grant (RFC 6749 section 4.4): https://datatracker.ietf.org/doc/html/rfc6749#section-4.4
- OAuth 2.0 bearer token usage, TLS and URL rules (RFC 6750 sections 5.2 and 5.3): https://www.rfc-editor.org/info/rfc6750/
- JWT profile for OAuth 2.0 access tokens (RFC 9068 section 4: validate signature, `iss`, `aud`, `exp`, and the `at+jwt` type): https://www.rfc-editor.org/rfc/rfc9068.html
- Python `hmac.compare_digest`: https://docs.python.org/3/library/hmac.html ; Node.js `crypto.timingSafeEqual`: https://nodejs.org/api/crypto.html
- Microsoft Entra External ID billing model (M2M add-on): https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing
- GitHub: about security hardening with OpenID Connect (claims, subject formats): https://docs.github.com/en/actions/concepts/security/openid-connect
- GitHub: configuring OpenID Connect in AWS: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws ; in Google Cloud: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-google-cloud-platform ; in Azure: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-azure
- AWS IAM: configuring a role for the GitHub OIDC identity provider (trust policy, `sub` restriction): https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html
- aws-actions/configure-aws-credentials: https://github.com/aws-actions/configure-aws-credentials
- Google Cloud: Workload Identity Federation with deployment pipelines (GitHub Actions attribute mapping and conditions): https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines ; attribute conditions: https://docs.cloud.google.com/iam/docs/workload-identity-federation
- google-github-actions/auth: https://github.com/google-github-actions/auth
- Microsoft Entra: workload identity federation: https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation ; creating the trust on an app (subject formats, audience, exact match): https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation-create-trust
- Azure: authenticate from GitHub Actions by OpenID Connect (`azure/login`): https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect
- SPIFFE and SPIRE: https://spiffe.io/ and https://spiffe.io/docs/latest/spire-about/
- RFC 5280 (certificate revocation): https://www.rfc-editor.org/info/rfc5280/
- Secret manager vendor pages: linked inline in section 5.
