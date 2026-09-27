---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "47310db5a48cde7e7562570296664009086e3b384571707292cb4f20dcba5ba7",
  "components": {
    "owasp": {
      "name": "OWASP authentication and password storage",
      "basis": "unknown",
      "sources": {
        "sc5f1b11d42f4": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
        "s49e8d76431d9": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
      }
    },
    "oauth": {
      "name": "OAuth security BCP",
      "basis": "RFC 9700",
      "sources": {
        "s4e6d674bf887": "https://www.rfc-editor.org/rfc/rfc9700.html"
      }
    },
    "oidc": {
      "name": "OpenID Connect Core",
      "basis": "1.0",
      "sources": {
        "scfd2790a544c": "https://openid.net/specs/openid-connect-core-1_0.html"
      }
    },
    "nist": {
      "name": "NIST password guidance",
      "basis": "SP 800-63B-4",
      "sources": {
        "sada92c9ac010": "https://pages.nist.gov/800-63-4/sp800-63b.html"
      }
    },
    "htpasswd": {
      "name": "Apache htpasswd",
      "basis": "unknown",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "bcrypt": {
      "name": "Python bcrypt rejection threshold",
      "basis": "5.0.0",
      "sources": {
        "saef7bba61b3a": "https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/CHANGELOG.rst"
      }
    },
    "bcrypt-source": {
      "name": "Python bcrypt changelog",
      "basis": "2b4ba9ac84df972e8e81311d09559af8dc82ef33",
      "sources": {
        "saef7bba61b3a": "https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/CHANGELOG.rst"
      }
    }
  },
  "claims": {
    "tls": {"text": "Protect the login page and whole session with TLS or equivalent strong transport; Basic and bearer credentials require HTTPS.", "components": ["owasp", "oauth"], "sources": ["owasp:sc5f1b11d42f4", "oauth:s4e6d674bf887"], "status": "REASONED"},
    "password-hashing": {"text": "Prefer argon2id, then scrypt; bcrypt is legacy and parameterized PBKDF2 serves FIPS requirements. Never use plaintext, unsalted or fast password hashes.", "components": ["owasp"], "sources": ["owasp:s49e8d76431d9"], "status": "REASONED"},
    "bcrypt-length": {"text": "bcrypt limits input to 72 bytes; Python bcrypt 5.0.0+ raises ValueError while earlier versions truncate. Prefer argon2id or scrypt for long passphrases.", "components": ["bcrypt", "bcrypt-source", "owasp"], "sources": ["bcrypt:saef7bba61b3a", "bcrypt-source:saef7bba61b3a", "owasp:s49e8d76431d9"], "status": "REASONED"},
    "bcrypt-prehash": {"text": "If legacy bcrypt is unavoidable, pre-hash with peppered HMAC then base64, never a bare digest susceptible to password shucking.", "components": ["owasp"], "sources": ["owasp:s49e8d76431d9"], "status": "REASONED"},
    "htpasswd-cost": {"text": "htpasswd -B -C 12 selects bcrypt cost 12; bare -B defaults to 5, below the OWASP minimum of 10.", "components": ["htpasswd", "owasp"], "sources": ["htpasswd:scde9004bb967", "owasp:s49e8d76431d9"], "status": "REASONED"},
    "federation": {"text": "Prefer supported SSO/OIDC and enable MFA wherever available.", "components": ["owasp", "oidc"], "sources": ["owasp:sc5f1b11d42f4", "oidc:scfd2790a544c"], "status": "REASONED"},
    "machine-tokens": {"text": "Use separate least-privilege API tokens, exercise rotation and set expiry where supported.", "components": ["oauth"], "sources": ["oauth:s4e6d674bf887"], "status": "REASONED"},
    "session-identity": {"text": "Use unpredictable session identifiers and regenerate on login or privilege change, invalidating the old identifier.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "session-revocation": {"text": "Invalidate sessions server-side on logout and password change.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "login-throttling": {"text": "Rate-limit authentication with account-aware and aggregate controls alongside source limits; lock or delay failures without enabling denial of access.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "enumeration": {"text": "Keep login, registration and reset responses uniform in message and timing.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "auth-logging": {"text": "Log authentication successes and failures with account and source address; retain logs for investigation.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "privilege": {"text": "Separate administrative and daily-use accounts; restrict database and OS service accounts to the rights the application uses.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "authorization": {"text": "A federated identity still needs an application allowlist before access is granted.", "components": ["oidc", "oauth"], "sources": ["oidc:scfd2790a544c", "oauth:s4e6d674bf887"], "status": "REASONED"},
    "code-pkce": {"text": "Use authorization code flow with PKCE S256, never plain.", "components": ["oauth"], "sources": ["oauth:s4e6d674bf887"], "status": "REASONED"},
    "redirects": {"text": "Require exact-match redirect URIs.", "components": ["oauth"], "sources": ["oauth:s4e6d674bf887"], "status": "REASONED"},
    "state-nonce": {"text": "Generate fresh state and nonce for each transaction, verify both and bind them to the initiating browser session.", "components": ["oauth", "oidc"], "sources": ["oauth:s4e6d674bf887", "oidc:scfd2790a544c"], "status": "REASONED"},
    "id-token-signature": {"text": "Validate ID-token signatures with provider JWKS and a pinned algorithm, never none.", "components": ["oidc"], "sources": ["oidc:scfd2790a544c"], "status": "REASONED"},
    "id-token-claims": {"text": "Validate ID-token issuer, audience and expiry before accepting the identity.", "components": ["oidc"], "sources": ["oidc:scfd2790a544c"], "status": "REASONED"},
    "token-lifecycle": {"text": "Use short-lived access tokens and refresh-token rotation; never put tokens in URLs.", "components": ["oauth"], "sources": ["oauth:s4e6d674bf887"], "status": "REASONED"},
    "account-linking": {"text": "Link accounts by issuer plus subject, never by email alone.", "components": ["oidc"], "sources": ["oidc:scfd2790a544c"], "status": "REASONED"},
    "mfa-enforcement": {"text": "Require MFA at the point of access in provider policy or the app; enrollment alone must not permit password-only access.", "components": ["owasp", "nist"], "sources": ["owasp:sc5f1b11d42f4", "nist:sada92c9ac010"], "status": "REASONED"},
    "control-plane": {"text": "Require MFA on the Git host, cloud, DNS, deployment platform, secret manager and IdP administrator account.", "components": ["owasp", "nist"], "sources": ["owasp:sc5f1b11d42f4", "nist:sada92c9ac010"], "status": "REASONED"},
    "password-length": {"text": "Require at least 8 password characters with enforced MFA, otherwise at least 15; allow long passphrases and all characters without composition or periodic-rotation rules.", "components": ["nist"], "sources": ["nist:sada92c9ac010"], "status": "REASONED"},
    "breached-passwords": {"text": "Screen new and changed passwords against known breaches; a valid breached password defeats hashing and per-IP limits.", "components": ["nist", "owasp"], "sources": ["nist:sada92c9ac010", "owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "recovery": {"text": "Use random, single-use, short-lived, account-bound reset tokens and a pre-verified delivery channel; recovery must preserve MFA.", "components": ["nist", "owasp"], "sources": ["nist:sada92c9ac010", "owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "recovery-reauth": {"text": "Reauthenticate for recovery-address or MFA-factor changes and invalidate outstanding sessions and unused reset tokens on completion.", "components": ["nist", "owasp"], "sources": ["nist:sada92c9ac010", "owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-token-rejection": {"text": "Negative tests reject missing, expired, wrong-issuer and wrong-audience tokens.", "components": ["oidc", "oauth"], "sources": ["oidc:scfd2790a544c", "oauth:s4e6d674bf887"], "status": "REASONED"},
    "default-deny": {"text": "Require authentication on every endpoint not deliberately public, including APIs, health dashboards, admin panels, metrics and message queues; publish an explicit public-path list. General authentication source; no dedicated endpoint-inventory reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "individual-credentials": {"text": "Change or disable vendor default accounts before exposure; give each human an individual account and each service its own credential, and never ship credentials in code, containers or documentation. General authentication source; no product-specific default-account references.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "secret-generation": {"text": "Generate random secrets with openssl rand -base64 32 or Python secrets.token_urlsafe(32). General authentication source; Sources has no OpenSSL or Python reference for these commands.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "secret-storage": {"text": "Load secrets from environment variables or a secret manager; ignore .env before the first commit and scan for leaks before pushing. Rotate secrets exposed in a public repository, chat or log; deletion does not unpublish them. General authentication source; no pinned storage or scanner reference.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "session-cookies": {"text": "Mark session cookies Secure, HttpOnly and SameSite Lax or Strict, and sign them with a strong random secret. General authentication source; no dedicated session-cookie reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "session-timeouts": {"text": "Enforce both idle and absolute session timeouts server-side; cookie expiry alone does not prevent replay. General authentication source; no dedicated session-timeout reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "session-unissued": {"text": "Reject session identifiers the server never issued to prevent session fixation. General authentication source; no dedicated session-management reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "csrf": {"text": "SameSite alone is not a complete CSRF defense: Lax permits a top-level state-changing GET and sibling subdomains can be same-site. Cookie-authenticated state changes need an anti-CSRF token or strict Origin/Sec-Fetch-Site check, and must not use safe methods such as GET. General authentication source; no dedicated CSRF reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "expensive-endpoint-limits": {"text": "Bound inference, uploads and job submission with request-size, concurrency and timeout limits in addition to per-client rate limits; apply these limits to streaming and webhook transports too. General authentication source; no dedicated resource-limit reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "fail2ban": {"text": "The body identifies fail2ban as a low-effort control for SSH and login panels on Linux hosts. General authentication source; no fail2ban vendor reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "federated-allowlist": {"text": "Allowlist tenants, verified hosted-domain claims, organization or group membership, or explicit users after federated login; any Google account is not staff, and Microsoft common requires issuer and tenant validation. General OIDC source; no Google or Microsoft vendor reference in Sources.", "components": ["oidc"], "sources": ["oidc:scfd2790a544c"], "status": "REASONED"},
    "browser-session": {"text": "Prefer a server-side session in an HttpOnly cookie to tokens in browser storage. General authentication source; no dedicated browser-storage reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "transport-authentication": {"text": "Authenticate WebSockets, SSE, GraphQL, gRPC, webhooks, inference and management APIs separately; HTML login does not protect them. Verify webhook sender signatures and reject replays. General authentication source; no transport-specific vendor references in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "offboarding": {"text": "Promptly revoke provider membership, proxy sessions, application sessions and personal tokens when a person leaves; measure and shrink each system's maximum time-to-revoke where immediate revocation is unavailable. General authentication and OAuth sources; no product-specific revocation reference.", "components": ["owasp", "oauth"], "sources": ["owasp:sc5f1b11d42f4", "oauth:s4e6d674bf887"], "status": "REASONED"},
    "verify-transports": {"text": "Use real protocol clients against every non-public path and transport: HTTP returns 401, 403 or a login redirect; gRPC returns UNAUTHENTICATED; SSE is refused; WebSockets reject the upgrade or reject protected operations, disclose no protected data and close on first-message authentication failure. A bare curl GET does not test non-HTTP transports. General authentication source; no protocol-specific reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-secret-scan": {"text": "A secret scanner must find no leaks in the working tree, staged changes and full history; git log -p with a password/secret/API-key grep is supplementary and misses uncommitted files, some refs and secrets without those words. General authentication source; no scanner reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-default-accounts": {"text": "Check that the user store has no admin, test or demo account with a known or empty password. General authentication source; no product-specific default-account reference.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-wrong-tenant": {"text": "Reject a wrong-tenant token in negative tests. General OIDC source; no tenant-specific vendor reference in Sources.", "components": ["oidc"], "sources": ["oidc:scfd2790a544c"], "status": "REASONED"},
    "verify-cross-user": {"text": "Verify that user A cannot read user B's resources. General authentication source; no dedicated authorization reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-origin-isolation": {"text": "Verify that the origin is unreachable except through its fronting layer. General authentication source; no proxy-isolation reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"}
  }
}
---
# Strong authentication baseline

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls: Protect the login page and whole session with TLS or equivalent strong transport; Basic and bearer credentials require HTTPS. | OWASP authentication and password storage unknown; OAuth security BCP RFC 9700 | REASONED |
| password-hashing: Prefer argon2id, then scrypt; bcrypt is legacy and parameterized PBKDF2 serves FIPS requirements. Never use plaintext, unsalted or fast password hashes. | OWASP authentication and password storage unknown | REASONED |
| bcrypt-length: bcrypt limits input to 72 bytes; Python bcrypt 5.0.0+ raises ValueError while earlier versions truncate. Prefer argon2id or scrypt for long passphrases. | Python bcrypt rejection threshold 5.0.0; Python bcrypt changelog 2b4ba9ac84df972e8e81311d09559af8dc82ef33; OWASP authentication and password storage unknown | REASONED |
| bcrypt-prehash: If legacy bcrypt is unavoidable, pre-hash with peppered HMAC then base64, never a bare digest susceptible to password shucking. | OWASP authentication and password storage unknown | REASONED |
| htpasswd-cost: htpasswd -B -C 12 selects bcrypt cost 12; bare -B defaults to 5, below the OWASP minimum of 10. | Apache htpasswd unknown; OWASP authentication and password storage unknown | REASONED |
| federation: Prefer supported SSO/OIDC and enable MFA wherever available. | OWASP authentication and password storage unknown; OpenID Connect Core 1.0 | REASONED |
| machine-tokens: Use separate least-privilege API tokens, exercise rotation and set expiry where supported. | OAuth security BCP RFC 9700 | REASONED |
| session-identity: Use unpredictable session identifiers and regenerate on login or privilege change, invalidating the old identifier. | OWASP authentication and password storage unknown | REASONED |
| session-revocation: Invalidate sessions server-side on logout and password change. | OWASP authentication and password storage unknown | REASONED |
| login-throttling: Rate-limit authentication with account-aware and aggregate controls alongside source limits; lock or delay failures without enabling denial of access. | OWASP authentication and password storage unknown | REASONED |
| enumeration: Keep login, registration and reset responses uniform in message and timing. | OWASP authentication and password storage unknown | REASONED |
| auth-logging: Log authentication successes and failures with account and source address; retain logs for investigation. | OWASP authentication and password storage unknown | REASONED |
| privilege: Separate administrative and daily-use accounts; restrict database and OS service accounts to the rights the application uses. | OWASP authentication and password storage unknown | REASONED |
| authorization: A federated identity still needs an application allowlist before access is granted. | OpenID Connect Core 1.0; OAuth security BCP RFC 9700 | REASONED |
| code-pkce: Use authorization code flow with PKCE S256, never plain. | OAuth security BCP RFC 9700 | REASONED |
| redirects: Require exact-match redirect URIs. | OAuth security BCP RFC 9700 | REASONED |
| state-nonce: Generate fresh state and nonce for each transaction, verify both and bind them to the initiating browser session. | OAuth security BCP RFC 9700; OpenID Connect Core 1.0 | REASONED |
| id-token-signature: Validate ID-token signatures with provider JWKS and a pinned algorithm, never none. | OpenID Connect Core 1.0 | REASONED |
| id-token-claims: Validate ID-token issuer, audience and expiry before accepting the identity. | OpenID Connect Core 1.0 | REASONED |
| token-lifecycle: Use short-lived access tokens and refresh-token rotation; never put tokens in URLs. | OAuth security BCP RFC 9700 | REASONED |
| account-linking: Link accounts by issuer plus subject, never by email alone. | OpenID Connect Core 1.0 | REASONED |
| mfa-enforcement: Require MFA at the point of access in provider policy or the app; enrollment alone must not permit password-only access. | OWASP authentication and password storage unknown; NIST password guidance SP 800-63B-4 | REASONED |
| control-plane: Require MFA on the Git host, cloud, DNS, deployment platform, secret manager and IdP administrator account. | OWASP authentication and password storage unknown; NIST password guidance SP 800-63B-4 | REASONED |
| password-length: Require at least 8 password characters with enforced MFA, otherwise at least 15; allow long passphrases and all characters without composition or periodic-rotation rules. | NIST password guidance SP 800-63B-4 | REASONED |
| breached-passwords: Screen new and changed passwords against known breaches; a valid breached password defeats hashing and per-IP limits. | NIST password guidance SP 800-63B-4; OWASP authentication and password storage unknown | REASONED |
| recovery: Use random, single-use, short-lived, account-bound reset tokens and a pre-verified delivery channel; recovery must preserve MFA. | NIST password guidance SP 800-63B-4; OWASP authentication and password storage unknown | REASONED |
| recovery-reauth: Reauthenticate for recovery-address or MFA-factor changes and invalidate outstanding sessions and unused reset tokens on completion. | NIST password guidance SP 800-63B-4; OWASP authentication and password storage unknown | REASONED |
| verify-token-rejection: Negative tests reject missing, expired, wrong-issuer and wrong-audience tokens. | OpenID Connect Core 1.0; OAuth security BCP RFC 9700 | REASONED |
| default-deny: Require authentication on every endpoint not deliberately public, including APIs, health dashboards, admin panels, metrics and message queues; publish an explicit public-path list. General authentication source; no dedicated endpoint-inventory reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| individual-credentials: Change or disable vendor default accounts before exposure; give each human an individual account and each service its own credential, and never ship credentials in code, containers or documentation. General authentication source; no product-specific default-account references. | OWASP authentication and password storage unknown | REASONED |
| secret-generation: Generate random secrets with openssl rand -base64 32 or Python secrets.token_urlsafe(32). General authentication source; Sources has no OpenSSL or Python reference for these commands. | OWASP authentication and password storage unknown | REASONED |
| secret-storage: Load secrets from environment variables or a secret manager; ignore .env before the first commit and scan for leaks before pushing. Rotate secrets exposed in a public repository, chat or log; deletion does not unpublish them. General authentication source; no pinned storage or scanner reference. | OWASP authentication and password storage unknown | REASONED |
| session-cookies: Mark session cookies Secure, HttpOnly and SameSite Lax or Strict, and sign them with a strong random secret. General authentication source; no dedicated session-cookie reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| session-timeouts: Enforce both idle and absolute session timeouts server-side; cookie expiry alone does not prevent replay. General authentication source; no dedicated session-timeout reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| session-unissued: Reject session identifiers the server never issued to prevent session fixation. General authentication source; no dedicated session-management reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| csrf: SameSite alone is not a complete CSRF defense: Lax permits a top-level state-changing GET and sibling subdomains can be same-site. Cookie-authenticated state changes need an anti-CSRF token or strict Origin/Sec-Fetch-Site check, and must not use safe methods such as GET. General authentication source; no dedicated CSRF reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| expensive-endpoint-limits: Bound inference, uploads and job submission with request-size, concurrency and timeout limits in addition to per-client rate limits; apply these limits to streaming and webhook transports too. General authentication source; no dedicated resource-limit reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| fail2ban: The body identifies fail2ban as a low-effort control for SSH and login panels on Linux hosts. General authentication source; no fail2ban vendor reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| federated-allowlist: Allowlist tenants, verified hosted-domain claims, organization or group membership, or explicit users after federated login; any Google account is not staff, and Microsoft common requires issuer and tenant validation. General OIDC source; no Google or Microsoft vendor reference in Sources. | OpenID Connect Core 1.0 | REASONED |
| browser-session: Prefer a server-side session in an HttpOnly cookie to tokens in browser storage. General authentication source; no dedicated browser-storage reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| transport-authentication: Authenticate WebSockets, SSE, GraphQL, gRPC, webhooks, inference and management APIs separately; HTML login does not protect them. Verify webhook sender signatures and reject replays. General authentication source; no transport-specific vendor references in Sources. | OWASP authentication and password storage unknown | REASONED |
| offboarding: Promptly revoke provider membership, proxy sessions, application sessions and personal tokens when a person leaves; measure and shrink each system's maximum time-to-revoke where immediate revocation is unavailable. General authentication and OAuth sources; no product-specific revocation reference. | OWASP authentication and password storage unknown; OAuth security BCP RFC 9700 | REASONED |
| verify-transports: Use real protocol clients against every non-public path and transport: HTTP returns 401, 403 or a login redirect; gRPC returns UNAUTHENTICATED; SSE is refused; WebSockets reject the upgrade or reject protected operations, disclose no protected data and close on first-message authentication failure. A bare curl GET does not test non-HTTP transports. General authentication source; no protocol-specific reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| verify-secret-scan: A secret scanner must find no leaks in the working tree, staged changes and full history; git log -p with a password/secret/API-key grep is supplementary and misses uncommitted files, some refs and secrets without those words. General authentication source; no scanner reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| verify-default-accounts: Check that the user store has no admin, test or demo account with a known or empty password. General authentication source; no product-specific default-account reference. | OWASP authentication and password storage unknown | REASONED |
| verify-wrong-tenant: Reject a wrong-tenant token in negative tests. General OIDC source; no tenant-specific vendor reference in Sources. | OpenID Connect Core 1.0 | REASONED |
| verify-cross-user: Verify that user A cannot read user B's resources. General authentication source; no dedicated authorization reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| verify-origin-isolation: Verify that the origin is unreachable except through its fronting layer. General authentication source; no proxy-isolation reference in Sources. | OWASP authentication and password storage unknown | REASONED |
<!-- version-basis:end -->

TLS without authentication leaves a service open to the whole internet over an encrypted channel. These rules apply to every service in this repository's guides. Each rule is a requirement unless it is marked `should` or phrased as a preference.

## Rules

1. **Deny by default.** Every endpoint that is not deliberately public must require authentication, including APIs, health dashboards, admin panels, metrics, and message queues. Publish an explicit list of the paths that are public; everything else authenticates.
2. **No default or shared credentials.** Change or disable every vendor default account before exposure. Each human gets an individual account; each service gets its own credential. Never ship credentials in code, containers, or documentation.
3. **TLS first.** Credentials must only cross the network inside TLS, or an equivalent authenticated encrypted transport such as SSH. Serve the login page and the whole authenticated session over HTTPS, not only the credential POST: a network attacker can rewrite an HTTP login page to steal what it submits. HTTP basic authentication and bearer tokens are acceptable only over HTTPS, because both send the secret with every request.
4. **Hash passwords with a modern algorithm.** Prefer argon2id; use scrypt where argon2id is unavailable, bcrypt only for legacy systems, and correctly parameterized PBKDF2 where FIPS compliance requires it (per current OWASP guidance). Never store plaintext, and never use unsalted or fast hashes such as MD5 or SHA-256 for passwords. bcrypt has a 72-byte input limit; an implementation may reject a longer input (Python `bcrypt` 5.0.0+ raises `ValueError`) or silently truncate it (earlier versions do), so prefer argon2id or scrypt for long passphrases. If legacy bcrypt is unavoidable, pre-hash only with a keyed construction (HMAC with a stored pepper, then base64), never a bare digest, which enables password shucking.
   - Node.js: `argon2` or `bcrypt` packages.
   - Python: `argon2-cffi` or `bcrypt`.
   - Shell (for htpasswd files): `htpasswd -B -C 12` (bcrypt; the bare `-B` default cost is 5, below the OWASP minimum of 10).
5. **Generate secrets randomly and keep them out of the repository.**
   ```bash
   openssl rand -base64 32
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Load secrets from environment variables or a secret manager. Add `.env` to `.gitignore` before the first commit, and scan the repository for leaked secrets (for example with gitleaks) before pushing. A secret that has reached a public repository, a chat, or a log is compromised: rotate it, since deleting the file does not unpublish it.
6. **Prefer SSO/OIDC over local accounts** where the product supports it, and enable MFA wherever available. [Cloudflare Access](cloudflare.md) puts SSO or one-time-PIN login in front of any web app without changing the app. Where no native MFA exists, add it with an identity layer, an app-level TOTP library, or a hosted service, per [mfa.md](mfa.md).
7. **Scope machine access.** API clients get their own tokens with the least privilege the task needs, not an admin password. Support and exercise rotation; set expiry where the platform allows it.
8. **Harden sessions.** Set cookies `Secure`, `HttpOnly`, and `SameSite` (`Lax` or `Strict`), sign them with a strong random secret, and enforce an idle and an absolute timeout server-side (a cookie expiry alone does not stop a replayed cookie). Use an unpredictable session identifier, regenerate it (invalidating the old one) on login and on any privilege change, and reject a session ID the server never issued (session fixation). Invalidate sessions server-side on logout and on password change. `SameSite` is not a complete CSRF defense (`Lax` still allows a top-level state-changing GET, and a sibling subdomain can be same-site), so a cookie-authenticated state-changing request must also carry an anti-CSRF token or a strict `Origin`/`Sec-Fetch-Site` check, and must never change state through a safe method such as GET.
9. **Rate-limit authentication endpoints** and lock or delay after repeated failures. Per-client rate limits do not stop distributed credential stuffing (valid breached passwords spread thin across many addresses), so add account-aware and aggregate abuse controls alongside source-based ones, and avoid a lockout an attacker can use to deny a user access. Keep login, registration, and password-reset responses uniform in message and timing so they do not disclose whether an account exists. Log authentication successes and failures with source address and account, and keep the logs long enough to investigate an incident. fail2ban is a low-effort control for SSH and login panels on Linux hosts. Bound expensive endpoints too: inference, uploads, and job submission need request-size, concurrency, and timeout limits in addition to per-client rate limits, because an exposed AI endpoint left without them can burn GPU time and money even while correctly rejecting bad credentials, a failure mode known as denial of wallet. [realtime-webhooks.md](realtime-webhooks.md) covers the streaming and webhook transports these limits also apply to.
10. **Least privilege everywhere.** Separate admin from daily-use accounts, and give database and OS service accounts only the rights the application uses.
11. **Federated login is authentication, not authorization.** After Google, Microsoft, GitHub, or any provider returns an identity, check it against an allowlist (tenant, hosted domain from the verified token claim, organization or group membership, or explicit users) before granting access. Any Google account is not "staff", and Microsoft's multi-tenant `common` endpoint admits every Microsoft account unless the app validates the issuer and tenant. [oidc-integration.md](oidc-integration.md) has the checks; [identity-providers.md](identity-providers.md) has the providers.
12. **OIDC and OAuth hygiene.** Authorization code flow with PKCE (`S256`, never `plain`); exact-match redirect URIs; fresh per-transaction `state` and `nonce`, verified and bound to the initiating browser session; ID tokens validated for signature (keys from the provider's JWKS, algorithm pinned, never `none`), issuer, audience, and expiry; short-lived access tokens with refresh-token rotation; tokens never in URLs. Prefer a server-side session in an `HttpOnly` cookie to tokens in browser storage. Link accounts by issuer plus subject, never by email alone.
13. **Enforce MFA where access is granted, not only where it is enrolled.** A user who enrolled a second factor but can still act with a password-only session is not protected. Require the factor in provider policy or in the app, and test it.
14. **Protect the control plane.** MFA on the Git host, the cloud account, the DNS registrar, the deployment platform, the secret manager, and the identity provider's administrator account. A takeover there bypasses every control inside the app.
15. **Authenticate every transport.** WebSockets, server-sent events, GraphQL, gRPC, webhooks (verify the sender's signature and reject replays), inference endpoints, and management APIs each need their own check. A login on the HTML pages protects none of them. Machine credentials follow [machine-auth.md](machine-auth.md).
16. **Offboard promptly.** When a person leaves, revoke their provider membership, proxy sessions, application sessions, and personal tokens. Know your maximum time-to-revoke for each system where immediate revocation is not available, and treat that number as something to shrink, not a fact to accept. [deployment-lifecycle.md](deployment-lifecycle.md) has the lifecycle checks; [mfa.md](mfa.md) covers revoking the second factor along with the account.
17. **Set a password policy and reject breached passwords.** Require a minimum length of at least 8 characters when a second factor is enforced, otherwise at least 15 (NIST SP 800-63B-4); allow long passphrases and every character, and drop periodic-rotation and composition rules. Screen new and changed passwords against a known-breach corpus (for example the Pwned Passwords range API), because a correct breached password defeats both hashing and per-IP rate limits.
18. **Secure account recovery.** Password and MFA reset is a sensitive authentication surface: issue cryptographically random, single-use, short-lived, account-bound reset tokens; deliver them only to a pre-verified channel; keep the reset response non-enumerating; reauthenticate for a recovery-address or MFA-factor change; and on completion invalidate outstanding sessions and unused reset tokens. Recovery must never silently drop the MFA requirement.

## Quick checks

- A protocol-appropriate unauthenticated request to every non-public path from rule 1 (metrics, health, admin, message-queue UIs) and every transport from rule 15 (WebSocket, SSE, GraphQL, gRPC, webhook, inference, management API), not just the HTML app, is rejected and returns no protected data: an HTTP endpoint gives `401`, `403`, or a login redirect; a gRPC call gives `UNAUTHENTICATED`; an SSE stream is refused; a WebSocket either rejects the upgrade (handshake-time auth) or, with first-message auth, permits the upgrade but rejects protected operations, returns no protected data, and closes the connection on auth failure. A bare `curl` GET does not exercise the non-HTTP transports, so test each with a real client.
- A secret scanner (gitleaks or similar) over the working tree, staged changes, and full history comes back clean; `git log -p | grep -iE 'password|secret|api[_-]?key'` is only a supplementary quick check, since it misses secrets without those words and does not cover uncommitted files or every ref.
- The user store contains no account named `admin`, `test`, or `demo` with a known or empty password.
- Negative tests pass: a missing, expired, wrong-issuer, wrong-audience, or wrong-tenant token is rejected; user A cannot read user B's resources; the origin is unreachable except through its fronting layer.

## Sources (checked September 2026)

- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OAuth 2.0 Security Best Current Practice (RFC 9700): https://www.rfc-editor.org/rfc/rfc9700.html
- OpenID Connect Core 1.0: https://openid.net/specs/openid-connect-core-1_0.html
- NIST SP 800-63B-4 (password length, section 3.1.1.2): https://pages.nist.gov/800-63-4/sp800-63b.html
- Apache htpasswd (bcrypt `-B`; cost `-C`, default 5): https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- pyca/bcrypt changelog (5.0.0 rejects input over 72 bytes): https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/CHANGELOG.rst
