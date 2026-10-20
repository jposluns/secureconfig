# Machine identity: API keys, client credentials, mutual TLS, and workload identity

Machine identity is how services, CI jobs and other workloads prove who they are without a person signing in. This guide helps your AI assistant choose and configure those credentials securely, including scoped, expiring API keys, OAuth client credentials, mutual TLS, and workload identity federation instead of stored cloud keys.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/machine-auth.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against OAuth client credentials (no recorded version), nginx mTLS release-1.28.0, Apache mTLS 2.4, PostgreSQL client certificates 17, MySQL client certificates 8.4, Redis TLS client authentication 7.4.2, and RabbitMQ TLS client authentication 3.13, plus 8 more recorded bases; 3 further sources are pinned to a commit and 17 carry no recorded version. Metadata reviewed 2026-10-20; documentation checked September 2026. The guide records 37 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Machines cannot do MFA, so their credentials are long-lived by default, and long-lived credentials leak through repositories, container images, and logs. The fix is scoped, short-lived, and where possible credential-free access: a CI job or workload that holds no key cannot leak one. [authentication.md](authentication.md) sets the baseline and [secrets.md](secrets.md) covers handling and leak response; this guide covers the credential types themselves, from the weakest to the one that removes the secret entirely.

## 1. API keys and bearer tokens

The simplest machine credential and the one that leaks most. When your service issues or accepts them:

- One key per client and per environment, generated randomly (commands in [secrets.md](secrets.md)), with the least privilege that client's task needs. A shared key cannot be revoked for one client without breaking the rest.
- Give every key an expiry and rotate on a schedule, with a short overlap during which both keys work, so rotation is routine rather than an outage.
- Send keys only in a header (`Authorization: Bearer ...`) over TLS, never in a URL. RFC 6750 makes TLS mandatory for bearer tokens and says they "SHOULD NOT be passed in page URLs", because URLs land in browser history, proxy logs, and server logs.
- Compare the presented key in constant time: `hmac.compare_digest()` in Python, `crypto.timingSafeEqual()` in Node.js (both arguments must have the same byte length). A plain `==` stops at the first differing byte and leaks timing.
- Where the service only needs to verify the key, as this guide's advice, issue a randomly generated key, store a hash of it and compare against the hash of the presented key. As this guide's advice, show the plaintext once at creation; as this guide's inference, a database dump then does not directly reveal plaintext keys if only hashes are stored and the keys have enough entropy to resist offline guessing.

  One example implementation, not a standard or requirement, is djangorestframework-api-key v3.1.0: its `Sha512ApiKeyHasher` hashes `password.encode()` with SHA-512, hex-encodes the digest and prefixes it with `sha512$$`, without a salt. The library justifies omitting salt for high-entropy keys and warns that this hasher should never be used in Django's `PASSWORD_HASHERS`. Its `verify` hashes the presented value with the same encoding and calls `constant_time_compare` on the encoded hashes. Its `KeyGenerator` defaults to an 8-character prefix and a 32-character secret, calls Django's `get_random_string` for each, joins them as `prefix.secret` and passes that whole key to its hash method; it returns the key, prefix and hash. The cited Django 5.2.18 helper chooses each character using Python's `secrets.choice` from 62 characters: lowercase ASCII letters, uppercase ASCII letters and digits; `constant_time_compare` calls `secrets.compare_digest` after converting both values with `force_bytes`. With those defaults, this guide calculates `32 * log2(62)`, about 190.5 bits for the secret alone, assuming independent uniform choices. As this guide's advice, fast hashes are suitable only for high-entropy random keys, not passwords; the OWASP password-storage citation remains password guidance, not an API-key implementation. These source lines show the example's code, not a deployed service's storage policy or measured timing.

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

API keys, client secrets, and client-certificate keys that cannot be federated away go in a secret manager or the platform's own store ([secrets.md](secrets.md)): AWS Secrets Manager (https://aws.amazon.com/secrets-manager/), Google Cloud Secret Manager (https://docs.cloud.google.com/secret-manager/docs/overview), Azure Key Vault (https://azure.microsoft.com/en-us/products/key-vault), HashiCorp Vault ([vault.md](vault.md); https://developer.hashicorp.com/vault) or OpenBao, its open-source fork under the Linux Foundation (https://openbao.org/), Infisical (https://infisical.com/), Doppler (https://www.doppler.com/), 1Password Secrets Automation (https://www.1password.dev/secrets-automation/), and Bitwarden Secrets Manager (https://bitwarden.com/products/secrets-manager/). As this guide's advice, the workload should authenticate to the store with its platform identity (an instance role, a managed identity, or the federation above) where the selected store and workload support it, so access need not depend on one more long-lived bootstrap key; otherwise protect the store credential as a machine secret.

## Verify

- REASONED: environment-scoping comparison per the guide's cited RFC 6750 bearer token usage, with the expected 401 or 403 in production and success in staging stated in this item; no staging and production API deployment is available in the authoring environment, so no request reached a service. At marking time the command passed bash -n (Bash 5.3.9) and ShellCheck 0.11.0 with no diagnostics, and run against a stub curl from a mode-0600 header file holding a synthetic key, it passed the header file by name and the key did not appear in its arguments. A key issued to another client or environment is rejected: with the key in a mode-`0600` header file kept out of version control (never on the command line, per section 1), `curl -q -sS -o /dev/null -w '%{http_code}\n' -H @staging.header https://api.example.com/v1/status` against production returns `401` or `403`, never `200`, while the same key does succeed in its own staging environment (so the denial is environment scoping, not a broken key or endpoint).
- REASONED: revocation and expiry rejection per the guide's cited RFC 6750 bearer token usage and RFC 9068 access-token profile, with the expected rejection and the client-identified log record stated in this item, so acceptance or a missing log record is the exposed state; no deployed service, token issuer or service log is available in the authoring environment, and this item names no command, so no part of it ran locally. A revoked or expired key or token is rejected the same way, and the rejection appears in the service log with the client identity.
- REASONED: CI credential posture per the guide's cited GitHub pages on security hardening with OpenID Connect and on configuring it in AWS, Google Cloud and Azure, with the fixed state stated in this item, so a long-lived cloud key among the secrets or a missing id-token: write is the exposed state; no GitHub repository or Actions settings are available in the authoring environment, so no secrets list or workflow was read, and this item names no command and the guide gives no workflow file to parse, so no part of it ran locally. The CI job holds no long-lived cloud key: the repository's Actions secrets contain no `AWS_SECRET_ACCESS_KEY`, service-account JSON, or Azure client secret, and the workflow declares `permissions: id-token: write`.
- REASONED: trust-condition inspection per the guide's cited AWS IAM page on configuring a role for the GitHub OIDC identity provider, Google Cloud Workload Identity Federation pages and Microsoft Entra workload identity federation pages; no AWS, Google Cloud or Azure account is available in the authoring environment, so no live trust was read. At marking time jq 1.8.1 read section 4's AWS trust policy, whose sub value met this item's criteria, while copies with the sub set to repo:example-org/*, repo:example-org/example-repo:* or a bare * and one with no sub each failed them. Run in jq on section 4's inline Google and Azure values, the same criteria found that both Azure subjects, repo:example-org/example-repo:environment:production and repo:example-org/example-repo:ref:refs/heads/main, met them; the Google principalSet binding names example-org/example-repo with no trailing wildcard but pins no branch or environment, and the attribute condition pins the owner and refs/heads/main but names no repository, so the Google check is met only by the binding and the condition together. The federation trust condition names the exact repository: the AWS `sub` condition and the Azure `subject` each contain `example-org/example-repo` and pin the branch or environment, while the Google `attribute.repository` binding and its attribute condition together restrict access to `example-org/example-repo` and the branch or environment, and none ends in a wildcard (`repo:example-org/*`, `repo:example-org/example-repo:*`, or a bare `*`) that would admit another repo, branch, or environment.
- `gitleaks git .` (plus a working-tree scan) and `docker history --no-trunc REPLACE_WITH_IMAGE` show no key. Docker history lists an image's history, including creation commands and sizes; as this guide's assessment, also scan the image layers, which must show no key, because the history output is not a contents audit and does not show the contents of files copied into the image ([secrets.md](secrets.md), [docker.md](docker.md)).
- REASONED: mTLS refusal per the guide's cited RFC 5280 and the cited nginx, Apache, PostgreSQL, MySQL, Redis, RabbitMQ and Mosquitto client-certificate sources, with the expected refusals and the authorized connection stated in this item; none of the cited services is deployed in the authoring environment, so none of them was tested. At marking time openssl verify (OpenSSL 3.5.5) on local fixtures accepted the authorized client certificate and rejected one from an untrusted CA (error 20), the same client certificate checked at a time after its expiry (error 10) and a revoked certificate checked against the CA's CRL (error 23), which verified OK when the CRL was not checked. On 127.0.0.1 with throwaway fixtures, openssl s_server without client-certificate verification returned HTTP 200 to an s_client that presented no certificate; with -Verify 1 -verify_return_error it refused that client with a certificate required alert over TLS 1.3, refused a client certificate from an untrusted CA with an unknown ca alert, and returned HTTP 200 to the authorized client. The unauthorized-identity case needs a service that authorizes on certificate identity, and no such service is deployed in the authoring environment, so it was not run. An mTLS service refuses a client that presents no certificate, an untrusted or expired certificate, and (where it authorizes on identity) a validly-signed but unauthorized certificate, and refuses a certificate once revoked, while the authorized client still connects.

## Sources (checked September 2026)

- Docker image history command (image history and creation-command output), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118
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
- OWASP Password Storage Cheat Sheet (hashes can be guessed; password guidance is not an API-key hash implementation), at 1a78ae3e443cef156e947f87e892efbcc62876ee (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Password_Storage_Cheat_Sheet.md#L21-L47
- djangorestframework-api-key v3.1.0 example (Django helper imports and prefix-dot-secret format; SHA-512, hexadecimal encoding, no-salt rationale, password warning and hash comparison; default key generation and preferred-hasher dispatch), checked October 2026: https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L9-L13 ; https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L21-L44 ; https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L47-L82
- Django 5.2.18 crypto helpers (Python secrets import, 62-character alphabet, secrets.choice generation and secrets.compare_digest comparison), checked October 2026: https://github.com/django/django/blob/5.2.18/django/utils/crypto.py#L7-L10 ; https://github.com/django/django/blob/5.2.18/django/utils/crypto.py#L48-L67
- OWASP Secrets Management Cheat Sheet (central storage and management), at 1a78ae3e443cef156e947f87e892efbcc62876ee (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Secrets_Management_Cheat_Sheet.md#L5-L7
- AWS Secrets Manager overview (rolling, checked October 2026): https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- Google Cloud Secret Manager overview (rolling, checked October 2026): https://docs.cloud.google.com/secret-manager/docs/overview
- Azure Key Vault overview (rolling, checked October 2026): https://learn.microsoft.com/en-us/azure/key-vault/general/overview
- OpenBao README (secret storage), v2.7.1 (checked October 2026): https://github.com/openbao/openbao/blob/v2.7.1/README.md#L47-L51
- OpenBao website (fork and Linux Foundation OpenSSF attribution; rolling, checked October 2026): https://openbao.org/
- 1Password Secrets Automation (rolling, checked October 2026): https://www.1password.dev/secrets-automation/
- Bitwarden Secrets Manager overview (rolling, checked October 2026): https://bitwarden.com/help/secrets-manager-overview/
- nginx release-1.28.0 `ssl_verify_client` directive and `on` value (checked October 2026): https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_ssl_module.c#L76-L78 ; https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_ssl_module.c#L162-L167
- Apache 2.4 `SSLVerifyClient require` (checked October 2026): https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslverifyclient
- PostgreSQL 17 certificate authentication and `clientcert=verify-full` (checked October 2026): https://www.postgresql.org/docs/17/auth-cert.html
- MySQL 8.4 `CREATE USER` TLS options (`REQUIRE X509`) (checked October 2026): https://dev.mysql.com/doc/refman/8.4/en/create-user.html
- Redis 7.4.2 TLS client-certificate requirement and `tls-auth-clients yes` configuration (checked October 2026): https://github.com/redis/redis/blob/7.4.2/redis.conf#L240-L241 ; https://github.com/redis/redis/blob/7.4.2/src/config.c#L99-L103 ; https://github.com/redis/redis/blob/7.4.2/src/config.c#L3239
- RabbitMQ 3.13 TLS (`ssl_options.fail_if_no_peer_cert`, peer verification and CA configuration) (checked October 2026): https://www.rabbitmq.com/docs/3.13/ssl
- Mosquitto v2.0.21 `require_certificate true` (checked October 2026): https://github.com/eclipse-mosquitto/mosquitto/blob/v2.0.21/man/mosquitto.conf.5.xml#L74-L76
- Gitleaks v8.19.0 Git-history and directory scanning commands (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md#L181 ; https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md#L188
- HashiCorp Vault v1.20.0 secret storage and access control (checked October 2026): https://github.com/hashicorp/vault/blob/v1.20.0/README.md#L18
- Infisical v0.165.16 secrets and configuration management (checked October 2026): https://github.com/Infisical/infisical/blob/v0.165.16/README.md#L48
- Doppler CLI 3.76.6 secrets and configuration access (checked October 2026): https://github.com/DopplerHQ/cli/blob/3.76.6/README.md#L3


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- oauth: OAuth client credentials (unknown)
- bearer: Bearer token guidance (unknown)
- jwt: JWT access-token profile (unknown)
- entra: Entra External ID (unknown)
- github: GitHub Actions OIDC (unknown)
- aws: AWS IAM and credential action (unknown)
- google: Google Cloud federation and auth action (unknown)
- azure: Azure federation and login (unknown)
- spiffe: SPIFFE and SPIRE (unknown)
- pki: Certificate revocation (unknown)
- nginx-mtls: nginx mTLS (release-1.28.0)
- apache-mtls: Apache mTLS (2.4)
- postgres-mtls: PostgreSQL client certificates (17)
- mysql-mtls: MySQL client certificates (8.4)
- redis-mtls: Redis TLS client authentication (7.4.2)
- rabbitmq-mtls: RabbitMQ TLS client authentication (3.13)
- mosquitto-mtls: Mosquitto TLS client authentication (v2.0.21)
- vault: HashiCorp Vault (v1.20.0)
- infisical: Infisical (v0.165.16)
- doppler-cli: Doppler CLI (3.76.6)
- openbao-release: OpenBao README (v2.7.1)
- openbao-site: OpenBao website (unknown)
- onepassword: 1Password Secrets Automation (unknown)
- bitwarden: Bitwarden Secrets Manager (unknown)
- aws-store: AWS Secrets Manager overview (unknown)
- google-store: Google Cloud Secret Manager overview (unknown)
- azure-store: Azure Key Vault overview (unknown)
- gitleaks: Gitleaks scan commands (v8.19.0)
- python: Python hmac (unknown)
- node: Node.js crypto (unknown)
- docker-build: Docker build and image history documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- owasp-password: OWASP Password Storage Cheat Sheet (1a78ae3e443cef156e947f87e892efbcc62876ee)
- owasp-secrets: OWASP Secrets Management Cheat Sheet (1a78ae3e443cef156e947f87e892efbcc62876ee)
- drf-api-key: djangorestframework-api-key (v3.1.0)
- django-crypto: Django crypto helpers (5.2.18)

Claims (full source mapping in the JSON block below):

- key-scope (REASONED; bearer): Issue a random least-privilege key per client and environment so one client can be revoked independently.
- key-lifetime (REASONED; bearer): Give keys expiries and scheduled rotation with a short overlap for continuity.
- bearer-transport (REASONED; bearer): Send bearer keys in Authorization headers over mandatory TLS; URLs leak through history and logs.
- constant-time (REASONED; python, node): Use hmac.compare_digest or crypto.timingSafeEqual rather than plain equality; the guide requires equal byte lengths.
- key-hash (REASONED; bearer, owasp-password, owasp-secrets, drf-api-key, django-crypto): As this guide's advice, where only verification is needed, store random-key hashes, compare presented-key hashes and show plaintext once at creation; as this guide's inference, hash-only dumps do not directly reveal plaintext keys with enough entropy to resist offline guessing. The cited SHA-512 code is an example, not a standard or requirement, for high-entropy random keys, not passwords.
- client-grant (REASONED; oauth): Confidential clients authenticate with grant_type=client_credentials for access tokens; refresh tokens SHOULD NOT be issued, so re-authenticate.
- token-scope (REASONED; oauth, bearer): Request the narrowest scope or provider audience and bound access-token lifetime and reach.
- jwt-validation (REASONED; jwt): Validate access-token signature, reject alg none, check exact issuer, API audience and expiry, require at+jwt for JWT access tokens, and enforce scopes.
- m2m-billing (REASONED; entra): As of September 2026, Entra External ID M2M is billed per transaction as an add-on; hourly renewal is roughly 720 monthly transactions.
- client-secret (REASONED; oauth, azure): Client credentials still need long-lived-secret protection unless replaced by federation supported by the provider.
- mtls-identity (REASONED; pki): Use a separate short-lived certificate per client and keep CA keys off signed servers; mTLS is a possession factor, not human MFA.
- mtls-nginx (REASONED; pki, nginx-mtls): nginx uses ssl_verify_client on in the linked service guide.
- mtls-apache (REASONED; pki, apache-mtls): Apache uses SSLVerifyClient require in the linked service guide.
- mtls-postgres (REASONED; pki, postgres-mtls): PostgreSQL uses clientcert=verify-full in the linked service guide.
- mtls-mysql (REASONED; pki, mysql-mtls): MySQL uses REQUIRE X509 in the linked service guide.
- mtls-redis (REASONED; pki, redis-mtls): Redis uses tls-auth-clients yes in the linked service guide.
- mtls-rabbitmq (REASONED; pki, rabbitmq-mtls): RabbitMQ uses ssl_options.fail_if_no_peer_cert = true in the linked service guide.
- mtls-mosquitto (REASONED; pki, mosquitto-mtls): Mosquitto uses require_certificate true in the linked service guide.
- mtls-revocation (REASONED; pki): Replacing a key does not reject the old certificate; revoke with checked CRL/OCSP, remove it from an allowlist or wait for expiry, and test refusal.
- oidc-token (REASONED; github): GitHub id-token: write permits short-lived OIDC tokens from token.actions.githubusercontent.com; restrict trust to the exact repository and branch or environment.
- aws-action (REASONED; aws): configure-aws-credentials uses role-to-assume and aws-region and defaults its audience to sts.amazonaws.com.
- aws-trust (REASONED; aws, github): AWS trust uses AssumeRoleWithWebIdentity and exact aud/sub conditions; IAM rejects absent or wildcard-only sub, and broad subjects admit outside repositories.
- google-provider (REASONED; google): Create an OIDC provider with the GitHub issuer, subject/repository mappings and an owner plus branch/environment condition.
- google-binding (REASONED; google): Grant workloadIdentityUser to the exact repository principalSet; prefer immutable numeric repository and owner IDs over reusable names.
- google-action (REASONED; google, github): google-github-actions/auth takes workload_identity_provider and service_account.
- azure-trust (REASONED; azure): Configure the exact GitHub issuer, repository branch/environment subject and api://AzureADTokenExchange audience; wildcards are unsupported and wrong subjects fail at exchange.
- azure-action (REASONED; azure, github): azure/login needs client-id, tenant-id and subscription-id for OIDC, without a stored client secret.
- subject-format (REASONED; github): The guide records an immutable default subject with owner/repository IDs for repositories created after July 15, 2026; inspect the actual claim before writing trust.
- action-pins (REASONED; github): Pin actions to full commit SHAs; tags and branches can move to different code.
- workload-attestation (REASONED; spiffe): SPIFFE/SPIRE provides attested short-lived workload identities without a stored secret.
- secret-store (REASONED; azure, google, aws, vault, infisical, doppler-cli, owasp-secrets, aws-store, google-store, azure-store, openbao-release, openbao-site, onepassword, bitwarden): Store unavoidable machine secrets in the listed secret managers. As this guide's advice, authenticate with platform identity where the selected store and workload support it, so access need not depend on another long-lived bootstrap key; otherwise protect the required store credential.
- verify-scope (REASONED; bearer): A protected header-file staging key must receive 401/403 in production while succeeding in staging; otherwise denial does not establish environment scoping.
- verify-expiry (REASONED; bearer, jwt): Revoked or expired credentials must be rejected with a service-log record identifying the client.
- verify-ci (REASONED; github): Repository Actions secrets should hold no long-lived cloud credentials and the workflow must declare id-token: write.
- verify-trust (REASONED; aws, google, azure): Inspect AWS sub, Azure subject, and the Google repository binding together with its attribute condition, for exact repository plus branch/environment restriction without broad wildcard suffixes.
- verify-artifacts (REASONED; bearer, gitleaks, docker-build): History, working-tree and image-layer scans must show no keys; docker history lists an image's history; as this guide's assessment, it is not a contents audit and does not show the contents of files copied into the image, so a separate image-layer scan is required. Sources cites Gitleaks history and directory scans, but no image-layer scanning tool.
- verify-mtls (REASONED; pki): Reject missing, untrusted, expired, revoked and, where identity authorization applies, unauthorized certificates while the authorized client succeeds.

````json
{
  "schema": 1,
  "checked": "2026-10-20",
  "documentation_checked": "2026-09",
  "body_sha256": "2389e3a202e32e72a14b42bc06894be01c386595a22eef3cab52509cad512de5",
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
    },
    "nginx-mtls": {
      "name": "nginx mTLS",
      "basis": "release-1.28.0",
      "sources": {
        "saba09cebd9dc": "https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_ssl_module.c#L76-L78",
        "se19e48aec677": "https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_ssl_module.c#L162-L167"
      }
    },
    "apache-mtls": {
      "name": "Apache mTLS",
      "basis": "2.4",
      "sources": {
        "s011c9b11bbf6": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslverifyclient"
      }
    },
    "postgres-mtls": {
      "name": "PostgreSQL client certificates",
      "basis": "17",
      "sources": {
        "sece82dc43429": "https://www.postgresql.org/docs/17/auth-cert.html"
      }
    },
    "mysql-mtls": {
      "name": "MySQL client certificates",
      "basis": "8.4",
      "sources": {
        "s4009a8e12cba": "https://dev.mysql.com/doc/refman/8.4/en/create-user.html"
      }
    },
    "redis-mtls": {
      "name": "Redis TLS client authentication",
      "basis": "7.4.2",
      "sources": {
        "s37a9d8a0e34f": "https://github.com/redis/redis/blob/7.4.2/redis.conf#L240-L241",
        "sc437a14c713a": "https://github.com/redis/redis/blob/7.4.2/src/config.c#L99-L103",
        "se86d20ae4ca9": "https://github.com/redis/redis/blob/7.4.2/src/config.c#L3239"
      }
    },
    "rabbitmq-mtls": {
      "name": "RabbitMQ TLS client authentication",
      "basis": "3.13",
      "sources": {
        "s617e896b6f53": "https://www.rabbitmq.com/docs/3.13/ssl"
      }
    },
    "mosquitto-mtls": {
      "name": "Mosquitto TLS client authentication",
      "basis": "v2.0.21",
      "sources": {
        "sf7dad152fc94": "https://github.com/eclipse-mosquitto/mosquitto/blob/v2.0.21/man/mosquitto.conf.5.xml#L74-L76"
      }
    },
    "vault": {
      "name": "HashiCorp Vault",
      "basis": "v1.20.0",
      "sources": {
        "sc7513679fe7e": "https://github.com/hashicorp/vault/blob/v1.20.0/README.md#L18"
      }
    },
    "infisical": {
      "name": "Infisical",
      "basis": "v0.165.16",
      "sources": {
        "s725a4ac24a82": "https://github.com/Infisical/infisical/blob/v0.165.16/README.md#L48"
      }
    },
    "doppler-cli": {
      "name": "Doppler CLI",
      "basis": "3.76.6",
      "sources": {
        "se354d6243027": "https://github.com/DopplerHQ/cli/blob/3.76.6/README.md#L3"
      }
    },
    "openbao-release": {
      "name": "OpenBao README",
      "basis": "v2.7.1",
      "sources": {
        "sdb9d182ed195": "https://github.com/openbao/openbao/blob/v2.7.1/README.md#L47-L51"
      }
    },
    "openbao-site": {
      "name": "OpenBao website",
      "basis": "unknown",
      "sources": {
        "s76158fafba22": "https://openbao.org/"
      }
    },
    "onepassword": {
      "name": "1Password Secrets Automation",
      "basis": "unknown",
      "sources": {
        "s96e614a22cd0": "https://www.1password.dev/secrets-automation/"
      }
    },
    "bitwarden": {
      "name": "Bitwarden Secrets Manager",
      "basis": "unknown",
      "sources": {
        "se179d6bd5c04": "https://bitwarden.com/help/secrets-manager-overview/"
      }
    },
    "aws-store": {
      "name": "AWS Secrets Manager overview",
      "basis": "unknown",
      "sources": {
        "s81b41c17ad57": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"
      }
    },
    "google-store": {
      "name": "Google Cloud Secret Manager overview",
      "basis": "unknown",
      "sources": {
        "scd27be211781": "https://docs.cloud.google.com/secret-manager/docs/overview"
      }
    },
    "azure-store": {
      "name": "Azure Key Vault overview",
      "basis": "unknown",
      "sources": {
        "seb86b29f4951": "https://learn.microsoft.com/en-us/azure/key-vault/general/overview"
      }
    },
    "gitleaks": {
      "name": "Gitleaks scan commands",
      "basis": "v8.19.0",
      "sources": {
        "s6310bf73dd3e": "https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md#L181",
        "s3809c36cec88": "https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md#L188"
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
    "docker-build": {
      "name": "Docker build and image history documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "s6283b172a5c6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118"
      }
    },
    "owasp-password": {
      "name": "OWASP Password Storage Cheat Sheet",
      "basis": "1a78ae3e443cef156e947f87e892efbcc62876ee",
      "sources": {
        "scfb73a9d1029": "https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Password_Storage_Cheat_Sheet.md#L21-L47"
      }
    },
    "owasp-secrets": {
      "name": "OWASP Secrets Management Cheat Sheet",
      "basis": "1a78ae3e443cef156e947f87e892efbcc62876ee",
      "sources": {
        "s3acb98020188": "https://github.com/OWASP/CheatSheetSeries/blob/1a78ae3e443cef156e947f87e892efbcc62876ee/cheatsheets/Secrets_Management_Cheat_Sheet.md#L5-L7"
      }
    },
    "drf-api-key": {
      "name": "djangorestframework-api-key",
      "basis": "v3.1.0",
      "sources": {
        "s13cac8efb2c8": "https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L9-L13",
        "s5776d8150ed6": "https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L21-L44",
        "s6b7803ec22e6": "https://github.com/florimondmanca/djangorestframework-api-key/blob/v3.1.0/src/rest_framework_api_key/crypto.py#L47-L82"
      }
    },
    "django-crypto": {
      "name": "Django crypto helpers",
      "basis": "5.2.18",
      "sources": {
        "sa74f4eec0332": "https://github.com/django/django/blob/5.2.18/django/utils/crypto.py#L7-L10",
        "sefce580872b0": "https://github.com/django/django/blob/5.2.18/django/utils/crypto.py#L48-L67"
      }
    }
  },
  "claims": {
    "key-scope": {"text": "Issue a random least-privilege key per client and environment so one client can be revoked independently.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "key-lifetime": {"text": "Give keys expiries and scheduled rotation with a short overlap for continuity.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "bearer-transport": {"text": "Send bearer keys in Authorization headers over mandatory TLS; URLs leak through history and logs.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "constant-time": {"text": "Use hmac.compare_digest or crypto.timingSafeEqual rather than plain equality; the guide requires equal byte lengths.", "components": ["python", "node"], "sources": ["python:s7a54556e5dac", "node:s96b80e6816a2"], "status": "REASONED"},
    "key-hash": {"text": "As this guide's advice, where only verification is needed, store random-key hashes, compare presented-key hashes and show plaintext once at creation; as this guide's inference, hash-only dumps do not directly reveal plaintext keys with enough entropy to resist offline guessing. The cited SHA-512 code is an example, not a standard or requirement, for high-entropy random keys, not passwords.", "components": ["bearer", "owasp-password", "owasp-secrets", "drf-api-key", "django-crypto"], "sources": ["bearer:sefd3dd623da3", "owasp-password:scfb73a9d1029", "owasp-secrets:s3acb98020188", "drf-api-key:s13cac8efb2c8", "drf-api-key:s5776d8150ed6", "drf-api-key:s6b7803ec22e6", "django-crypto:sa74f4eec0332", "django-crypto:sefce580872b0"], "status": "REASONED"},
    "client-grant": {"text": "Confidential clients authenticate with grant_type=client_credentials for access tokens; refresh tokens SHOULD NOT be issued, so re-authenticate.", "components": ["oauth"], "sources": ["oauth:s65b02b1812cc"], "status": "REASONED"},
    "token-scope": {"text": "Request the narrowest scope or provider audience and bound access-token lifetime and reach.", "components": ["oauth", "bearer"], "sources": ["oauth:s65b02b1812cc", "bearer:sefd3dd623da3"], "status": "REASONED"},
    "jwt-validation": {"text": "Validate access-token signature, reject alg none, check exact issuer, API audience and expiry, require at+jwt for JWT access tokens, and enforce scopes.", "components": ["jwt"], "sources": ["jwt:sc36d79fcad94"], "status": "REASONED"},
    "m2m-billing": {"text": "As of September 2026, Entra External ID M2M is billed per transaction as an add-on; hourly renewal is roughly 720 monthly transactions.", "components": ["entra"], "sources": ["entra:s0ee5939cfc03"], "status": "REASONED"},
    "client-secret": {"text": "Client credentials still need long-lived-secret protection unless replaced by federation supported by the provider.", "components": ["oauth", "azure"], "sources": ["oauth:s65b02b1812cc", "azure:sb7a38a36ac47"], "status": "REASONED"},
    "mtls-identity": {"text": "Use a separate short-lived certificate per client and keep CA keys off signed servers; mTLS is a possession factor, not human MFA.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"},
    "mtls-nginx": {"text": "nginx uses ssl_verify_client on in the linked service guide.", "components": ["pki", "nginx-mtls"], "sources": ["pki:s93ee2b4751f8", "nginx-mtls:saba09cebd9dc", "nginx-mtls:se19e48aec677"], "status": "REASONED"},
    "mtls-apache": {"text": "Apache uses SSLVerifyClient require in the linked service guide.", "components": ["pki", "apache-mtls"], "sources": ["pki:s93ee2b4751f8", "apache-mtls:s011c9b11bbf6"], "status": "REASONED"},
    "mtls-postgres": {"text": "PostgreSQL uses clientcert=verify-full in the linked service guide.", "components": ["pki", "postgres-mtls"], "sources": ["pki:s93ee2b4751f8", "postgres-mtls:sece82dc43429"], "status": "REASONED"},
    "mtls-mysql": {"text": "MySQL uses REQUIRE X509 in the linked service guide.", "components": ["pki", "mysql-mtls"], "sources": ["pki:s93ee2b4751f8", "mysql-mtls:s4009a8e12cba"], "status": "REASONED"},
    "mtls-redis": {"text": "Redis uses tls-auth-clients yes in the linked service guide.", "components": ["pki", "redis-mtls"], "sources": ["pki:s93ee2b4751f8", "redis-mtls:s37a9d8a0e34f", "redis-mtls:sc437a14c713a", "redis-mtls:se86d20ae4ca9"], "status": "REASONED"},
    "mtls-rabbitmq": {"text": "RabbitMQ uses ssl_options.fail_if_no_peer_cert = true in the linked service guide.", "components": ["pki", "rabbitmq-mtls"], "sources": ["pki:s93ee2b4751f8", "rabbitmq-mtls:s617e896b6f53"], "status": "REASONED"},
    "mtls-mosquitto": {"text": "Mosquitto uses require_certificate true in the linked service guide.", "components": ["pki", "mosquitto-mtls"], "sources": ["pki:s93ee2b4751f8", "mosquitto-mtls:sf7dad152fc94"], "status": "REASONED"},
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
    "secret-store": {"text": "Store unavoidable machine secrets in the listed secret managers. As this guide's advice, authenticate with platform identity where the selected store and workload support it, so access need not depend on another long-lived bootstrap key; otherwise protect the required store credential.", "components": ["azure", "google", "aws", "vault", "infisical", "doppler-cli", "owasp-secrets", "aws-store", "google-store", "azure-store", "openbao-release", "openbao-site", "onepassword", "bitwarden"], "sources": ["azure:sb7a38a36ac47", "google:s03844cd0246a", "aws:s6fff7087bca4", "vault:sc7513679fe7e", "infisical:s725a4ac24a82", "doppler-cli:se354d6243027", "owasp-secrets:s3acb98020188", "aws-store:s81b41c17ad57", "google-store:scd27be211781", "azure-store:seb86b29f4951", "openbao-release:sdb9d182ed195", "openbao-site:s76158fafba22", "onepassword:s96e614a22cd0", "bitwarden:se179d6bd5c04"], "status": "REASONED"},
    "verify-scope": {"text": "A protected header-file staging key must receive 401/403 in production while succeeding in staging; otherwise denial does not establish environment scoping.", "components": ["bearer"], "sources": ["bearer:sefd3dd623da3"], "status": "REASONED"},
    "verify-expiry": {"text": "Revoked or expired credentials must be rejected with a service-log record identifying the client.", "components": ["bearer", "jwt"], "sources": ["bearer:sefd3dd623da3", "jwt:sc36d79fcad94"], "status": "REASONED"},
    "verify-ci": {"text": "Repository Actions secrets should hold no long-lived cloud credentials and the workflow must declare id-token: write.", "components": ["github"], "sources": ["github:s65bfc1e3ee0d", "github:s653a0d94dd2f", "github:sa8ed4c86a8ea", "github:s80d46a4f675c"], "status": "REASONED"},
    "verify-trust": {"text": "Inspect AWS sub, Azure subject, and the Google repository binding together with its attribute condition, for exact repository plus branch/environment restriction without broad wildcard suffixes.", "components": ["aws", "google", "azure"], "sources": ["aws:s6fff7087bca4", "google:s03844cd0246a", "google:s0f874cc5b70e", "azure:sc70c3d4b8844"], "status": "REASONED"},
    "verify-artifacts": {"text": "History, working-tree and image-layer scans must show no keys; docker history lists an image's history; as this guide's assessment, it is not a contents audit and does not show the contents of files copied into the image, so a separate image-layer scan is required. Sources cites Gitleaks history and directory scans, but no image-layer scanning tool.", "components": ["bearer", "gitleaks", "docker-build"], "sources": ["bearer:sefd3dd623da3", "gitleaks:s6310bf73dd3e", "gitleaks:s3809c36cec88", "docker-build:s6283b172a5c6"], "status": "REASONED"},
    "verify-mtls": {"text": "Reject missing, untrusted, expired, revoked and, where identity authorization applies, unauthorized certificates while the authorized client succeeds.", "components": ["pki"], "sources": ["pki:s93ee2b4751f8"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
