---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "9915085829c36ca53782817836eb41ac022af029043ac183aeb440631b02ec36",
  "components": {
    "owasp": {
      "name": "OWASP authentication and password storage",
      "basis": "unknown",
      "sources": {
        "sc5f1b11d42f4": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
        "s49e8d76431d9": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
      }
    },
    "owasp-p1": {
      "name": "OWASP authorization, secrets and session guidance",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "sa68227c175a9": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L30-L38",
        "s5f5e10a9e4c2": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L93-L99",
        "s5fd4accb6988": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L7",
        "s6ea90d0c28e9": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L313",
        "se0eb20386574": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L462-L464",
        "se49462b39c11": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L131-L149"
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
    },
    "openssl": {
      "name": "OpenSSL rand",
      "basis": "3.5",
      "sources": {
        "s86919b215ba1": "https://docs.openssl.org/3.5/man1/openssl-rand/"
      }
    },
    "python": {
      "name": "Python secrets",
      "basis": "3.13",
      "sources": {
        "sd2e8196eaa96": "https://docs.python.org/3.13/library/secrets.html#secrets.token_urlsafe"
      }
    },
    "gitleaks-source": {
      "name": "Gitleaks scanning modes",
      "basis": "b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b",
      "sources": {
        "s44a3edaa543d": "https://github.com/gitleaks/gitleaks/blob/b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b/README.md#L172-L189"
      }
    },
    "git": {
      "name": "Git ignore rules",
      "basis": "v2.49.0",
      "sources": {
        "s5f377f0fdbd8": "https://github.com/git/git/blob/v2.49.0/Documentation/gitignore.adoc#L15-L18"
      }
    },
    "owasp-docs": {
      "name": "OWASP security guidance",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "seb866a1f94e9": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L214-L218",
        "s0562e4dc23f2": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L163",
        "s0b82bc050cf3": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L265-L267",
        "sf069993cc3d7": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L275",
        "sa5f6e96a876c": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L317",
        "s4779e856ef9d": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L323-L331",
        "s4f0aa80b1ef6": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/HTML5_Security_Cheat_Sheet.md#L53",
        "s232e483ac72b": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L149",
        "sc088939103f0": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L17-L26",
        "sa7544ec9e1d7": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L197",
        "seb3129173dbb": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L226",
        "s3369d9106dce": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Denial_of_Service_Cheat_Sheet.md#L80",
        "sd6d35bd1b67d": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Denial_of_Service_Cheat_Sheet.md#L110-L113"
      }
    },
    "api-security": {
      "name": "OWASP API Security",
      "basis": "2023",
      "sources": {
        "s213afc24aadb": "https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/"
      }
    },
    "google-oidc": {
      "name": "Google OpenID Connect",
      "basis": "rolling",
      "sources": {
        "s4f815acc2976": "https://developers.google.com/identity/openid-connect/openid-connect"
      }
    },
    "entra-multitenant": {
      "name": "Microsoft Entra multitenant token validation",
      "basis": "49b84e07023770128d83039c07eafb84ff1de1df",
      "sources": {
        "s5e0242f87cb7": "https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/howto-convert-app-to-be-multi-tenant.md#L43-L63",
        "s95719206c226": "https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/access-tokens.md#L179-L187"
      }
    },
    "cloudflare-access": {
      "name": "Cloudflare Access and origin configuration",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "sfddb92e438ca": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16",
        "s7cafe1b17afd": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54",
        "s81e5dd28d3e5": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17",
        "s65c224a2e655": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L59-L67",
        "sa012410f91eb": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L198-L206",
        "sbf4ecbd5ffc1": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L16-L37"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra revocation model",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s983f45259faa": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62"
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
    "session-identity": {"text": "Use unpredictable session identifiers and regenerate on login or privilege change, invalidating the old identifier.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s0b82bc050cf3", "owasp-docs:sf069993cc3d7"], "status": "REASONED"},
    "session-revocation": {"text": "Invalidate sessions server-side on logout and password change.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:sf069993cc3d7", "owasp-docs:sa5f6e96a876c"], "status": "REASONED"},
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
    "default-deny": {"text": "Every endpoint that is not deliberately public must require authentication, applying OWASP's deny-by-default principle. Require authentication for APIs, health dashboards, admin panels, metrics, and message queues, and publish an explicit list of public paths (this guide's recommendation; the cited passage does not cover this).", "components": ["owasp", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "owasp-p1:sa68227c175a9"], "status": "REASONED"},
    "individual-credentials": {"text": "Change or disable every vendor default account before exposure. Each human gets an individual account; each service gets its own credential. Never ship credentials in code, containers or documentation. OWASP notes that services sharing one secret make the source of a compromise or leak hard to identify; vendor default accounts, individual human and service credentials, and keeping credentials out of code, containers and documentation are this guide's recommendations.", "components": ["owasp", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "owasp-p1:s5fd4accb6988"], "status": "REASONED"},
    "secret-generation": {"text": "Generate random secrets with openssl rand -base64 32 or Python secrets.token_urlsafe(32).", "components": ["owasp", "openssl", "python"], "sources": ["owasp:sc5f1b11d42f4", "openssl:s86919b215ba1", "python:sd2e8196eaa96"], "status": "REASONED"},
    "secret-storage": {"text": "Prefer a secret manager (this guide's recommendation; OWASP lists secret managers as one option). For containers, OWASP advises environment variables only when mounted files or a secret-store fetch are not possible. Ignore .env before the first commit and scan for leaks before pushing. Rotate secrets exposed in a public repository, chat or log; deletion does not unpublish them.", "components": ["owasp", "gitleaks-source", "git", "owasp-docs", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "gitleaks-source:s44a3edaa543d", "git:s5f377f0fdbd8", "owasp-docs:seb866a1f94e9", "owasp-p1:s6ea90d0c28e9", "owasp-p1:se0eb20386574"], "status": "REASONED"},
    "session-cookies": {"text": "Mark session cookies Secure, HttpOnly and SameSite Lax or Strict; signing them with a strong random secret is this guide's recommendation, not covered by the cited passage.", "components": ["owasp", "owasp-docs", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s0562e4dc23f2", "owasp-p1:se49462b39c11"], "status": "REASONED"},
    "session-timeouts": {"text": "Enforce both idle and absolute session timeouts server-side; cookie expiry alone does not prevent replay.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s4779e856ef9d"], "status": "REASONED"},
    "session-unissued": {"text": "Reject session identifiers the server never issued to prevent session fixation.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s0b82bc050cf3"], "status": "REASONED"},
    "csrf": {"text": "SameSite alone is not a complete CSRF defense: Lax permits a top-level state-changing GET and sibling subdomains can be same-site. Cookie-authenticated state changes need an anti-CSRF token or strict Origin/Sec-Fetch-Site check, and must not use safe methods such as GET.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s232e483ac72b", "owasp-docs:sc088939103f0", "owasp-docs:sa7544ec9e1d7", "owasp-docs:seb3129173dbb"], "status": "REASONED"},
    "expensive-endpoint-limits": {"text": "Bound inference, uploads and job submission with request-size, concurrency and timeout limits in addition to per-client rate limits; apply these limits to streaming and webhook transports too.", "components": ["owasp", "api-security", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "api-security:s213afc24aadb", "owasp-docs:s3369d9106dce", "owasp-docs:sd6d35bd1b67d"], "status": "REASONED"},
    "fail2ban": {"text": "The body identifies fail2ban as a low-effort control for SSH and login panels on Linux hosts. General authentication source; no fail2ban vendor reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "federated-allowlist": {"text": "After federated login, this guide recommends checking an application allowlist of tenants, hosted domains, organization or group membership, or explicit users; a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the hd claim in the validated ID token; an email domain or request hd parameter is insufficient. Microsoft common serves organizational and personal accounts; validate the token issuer, signing-key issuer and tid, then apply the application tenant allowlist. Vendor sources support the Google hd check and Microsoft token validation; the full allowlist and staff determination are this guide's recommendations.", "components": ["oidc", "google-oidc", "entra-multitenant"], "sources": ["oidc:scfd2790a544c", "google-oidc:s4f815acc2976", "entra-multitenant:s5e0242f87cb7", "entra-multitenant:s95719206c226"], "status": "REASONED"},
    "cloudflare-access": {"text": "Cloudflare Access can place an authentication layer in front of a self-hosted web application. Cloudflare recommends creating the Access application before the tunnel route and says that without one the published application is available to anyone on the Internet. Validate the Access JWT at the origin; for Tunnel, configure origin TLS verification and Access JWT checking, and use Full (strict) for a directly proxied HTTPS origin where applicable. One-time PIN, SSO choice and unchanged application code are not established by these fetched pages.", "components": ["cloudflare-access"], "sources": ["cloudflare-access:sfddb92e438ca", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:s81e5dd28d3e5", "cloudflare-access:s65c224a2e655", "cloudflare-access:sa012410f91eb", "cloudflare-access:sbf4ecbd5ffc1"], "status": "REASONED"},
    "browser-session": {"text": "Prefer a server-side session in an HttpOnly cookie to tokens in browser storage.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s4f0aa80b1ef6"], "status": "REASONED"},
    "transport-authentication": {"text": "Authenticate WebSockets, SSE, GraphQL, gRPC, webhooks, inference and management APIs separately; HTML login does not protect them. Verify webhook sender signatures and reject replays. General authentication source; no transport-specific vendor references in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "offboarding": {"text": "When a person leaves, revoke provider membership, proxy and application sessions, and personal tokens; measure and shrink maximum time-to-revoke where immediate revocation is unavailable. These are this guide's operational recommendations. The cited Microsoft source addresses Entra application sessions only; no cited source establishes a specific provider-membership or token-revocation mechanism or measured delay.", "components": ["owasp", "oauth", "owasp-docs", "entra-docs"], "sources": ["owasp:sc5f1b11d42f4", "oauth:s4e6d674bf887", "owasp-docs:seb866a1f94e9", "entra-docs:s983f45259faa"], "status": "REASONED"},
    "verify-transports": {"text": "Use real protocol clients against every non-public path and transport: HTTP returns 401, 403 or a login redirect; gRPC returns UNAUTHENTICATED; SSE is refused; WebSockets reject the upgrade or reject protected operations, disclose no protected data and close on first-message authentication failure. A bare curl GET does not test non-HTTP transports. General authentication source; no protocol-specific reference in Sources.", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-secret-scan": {"text": "A secret scanner must find no leaks in the working tree, staged changes and full history; git log -p with a password/secret/API-key grep is supplementary and misses uncommitted files, some refs and secrets without those words. The Gitleaks source covers history and directory scans; staged-change scanning and git log -p behaviour are not cited.", "components": ["owasp", "gitleaks-source"], "sources": ["owasp:sc5f1b11d42f4", "gitleaks-source:s44a3edaa543d"], "status": "REASONED"},
    "verify-default-accounts": {"text": "Check that the user store has no admin, test or demo account with a known or empty password. This is the guide's recommendation; the OWASP Authentication Cheat Sheet does not list these account names (checked at commit 72865b1e).", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-wrong-tenant": {"text": "Expect a wrong-tenant token to be rejected in an application negative test after issuer and tid validation and the application tenant allowlist. Microsoft documents the validation rules; this guide recommends the allowlist and test, and no deployed rejection was observed.", "components": ["oidc", "entra-multitenant"], "sources": ["oidc:scfd2790a544c", "entra-multitenant:s95719206c226"], "status": "REASONED"},
    "verify-cross-user": {"text": "Verify that user A cannot read user B's resources. OWASP describes horizontal privilege escalation and object-specific access checks.", "components": ["owasp", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "owasp-p1:s5f5e10a9e4c2"], "status": "REASONED"},
    "verify-origin-isolation": {"text": "Expect direct origin access to fail in a deployment negative test. Cloudflare describes Access policy enforcement, origin IP protection for publicly routable origins, JWT validation and Tunnel access checks; these docs do not establish that a particular origin is unreachable.", "components": ["owasp", "cloudflare-access"], "sources": ["owasp:sc5f1b11d42f4", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:s81e5dd28d3e5", "cloudflare-access:sa012410f91eb"], "status": "REASONED"}
  }
}
---
# Strong authentication baseline

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls: Protect the login page and whole session with TLS or equivalent strong transport; Basic and bearer credentials require HTTPS. | OWASP authentication and password storage unknown; OAuth security BCP RFC 9700 | REASONED |
| password-hashing: Prefer argon2id, then scrypt; bcrypt is legacy and parameterized PBKDF2 serves FIPS requirements. Never use plaintext, unsalted or fast password hashes. | OWASP authentication and password storage unknown | REASONED |
| bcrypt-length: bcrypt limits input to 72 bytes; Python bcrypt 5.0.0+ raises ValueError while earlier versions truncate. Prefer argon2id or scrypt for long passphrases. | Python bcrypt rejection threshold 5.0.0; Python bcrypt changelog 2b4ba9ac84df972e8e81311d09559af8dc82ef33; OWASP authentication and password storage unknown | REASONED |
| bcrypt-prehash: If legacy bcrypt is unavoidable, pre-hash with peppered HMAC then base64, never a bare digest susceptible to password shucking. | OWASP authentication and password storage unknown | REASONED |
| htpasswd-cost: htpasswd -B -C 12 selects bcrypt cost 12; bare -B defaults to 5, below the OWASP minimum of 10. | Apache htpasswd unknown; OWASP authentication and password storage unknown | REASONED |
| federation: Prefer supported SSO/OIDC and enable MFA wherever available. | OWASP authentication and password storage unknown; OpenID Connect Core 1.0 | REASONED |
| machine-tokens: Use separate least-privilege API tokens, exercise rotation and set expiry where supported. | OAuth security BCP RFC 9700 | REASONED |
| session-identity: Use unpredictable session identifiers and regenerate on login or privilege change, invalidating the old identifier. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| session-revocation: Invalidate sessions server-side on logout and password change. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
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
| default-deny: Every endpoint that is not deliberately public must require authentication, applying OWASP's deny-by-default principle. Require authentication for APIs, health dashboards, admin panels, metrics, and message queues, and publish an explicit list of public paths (this guide's recommendation; the cited passage does not cover this). | OWASP authentication and password storage unknown; OWASP authorization, secrets and session guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| individual-credentials: Change or disable every vendor default account before exposure. Each human gets an individual account; each service gets its own credential. Never ship credentials in code, containers or documentation. OWASP notes that services sharing one secret make the source of a compromise or leak hard to identify; vendor default accounts, individual human and service credentials, and keeping credentials out of code, containers and documentation are this guide's recommendations. | OWASP authentication and password storage unknown; OWASP authorization, secrets and session guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| secret-generation: Generate random secrets with openssl rand -base64 32 or Python secrets.token_urlsafe(32). | OWASP authentication and password storage unknown; OpenSSL rand 3.5; Python secrets 3.13 | REASONED |
| secret-storage: Prefer a secret manager (this guide's recommendation; OWASP lists secret managers as one option). For containers, OWASP advises environment variables only when mounted files or a secret-store fetch are not possible. Ignore .env before the first commit and scan for leaks before pushing. Rotate secrets exposed in a public repository, chat or log; deletion does not unpublish them. | OWASP authentication and password storage unknown; Gitleaks scanning modes b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b; Git ignore rules v2.49.0; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd; OWASP authorization, secrets and session guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| session-cookies: Mark session cookies Secure, HttpOnly and SameSite Lax or Strict; signing them with a strong random secret is this guide's recommendation, not covered by the cited passage. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd; OWASP authorization, secrets and session guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| session-timeouts: Enforce both idle and absolute session timeouts server-side; cookie expiry alone does not prevent replay. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| session-unissued: Reject session identifiers the server never issued to prevent session fixation. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| csrf: SameSite alone is not a complete CSRF defense: Lax permits a top-level state-changing GET and sibling subdomains can be same-site. Cookie-authenticated state changes need an anti-CSRF token or strict Origin/Sec-Fetch-Site check, and must not use safe methods such as GET. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| expensive-endpoint-limits: Bound inference, uploads and job submission with request-size, concurrency and timeout limits in addition to per-client rate limits; apply these limits to streaming and webhook transports too. | OWASP authentication and password storage unknown; OWASP API Security 2023; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| fail2ban: The body identifies fail2ban as a low-effort control for SSH and login panels on Linux hosts. General authentication source; no fail2ban vendor reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| federated-allowlist: After federated login, this guide recommends checking an application allowlist of tenants, hosted domains, organization or group membership, or explicit users; a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the hd claim in the validated ID token; an email domain or request hd parameter is insufficient. Microsoft common serves organizational and personal accounts; validate the token issuer, signing-key issuer and tid, then apply the application tenant allowlist. Vendor sources support the Google hd check and Microsoft token validation; the full allowlist and staff determination are this guide's recommendations. | OpenID Connect Core 1.0; Google OpenID Connect rolling; Microsoft Entra multitenant token validation 49b84e07023770128d83039c07eafb84ff1de1df | REASONED |
| cloudflare-access: Cloudflare Access can place an authentication layer in front of a self-hosted web application. Cloudflare recommends creating the Access application before the tunnel route and says that without one the published application is available to anyone on the Internet. Validate the Access JWT at the origin; for Tunnel, configure origin TLS verification and Access JWT checking, and use Full (strict) for a directly proxied HTTPS origin where applicable. One-time PIN, SSO choice and unchanged application code are not established by these fetched pages. | Cloudflare Access and origin configuration c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| browser-session: Prefer a server-side session in an HttpOnly cookie to tokens in browser storage. | OWASP authentication and password storage unknown; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| transport-authentication: Authenticate WebSockets, SSE, GraphQL, gRPC, webhooks, inference and management APIs separately; HTML login does not protect them. Verify webhook sender signatures and reject replays. General authentication source; no transport-specific vendor references in Sources. | OWASP authentication and password storage unknown | REASONED |
| offboarding: When a person leaves, revoke provider membership, proxy and application sessions, and personal tokens; measure and shrink maximum time-to-revoke where immediate revocation is unavailable. These are this guide's operational recommendations. The cited Microsoft source addresses Entra application sessions only; no cited source establishes a specific provider-membership or token-revocation mechanism or measured delay. | OWASP authentication and password storage unknown; OAuth security BCP RFC 9700; OWASP security guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd; Microsoft Entra revocation model 231747abc59ae3d50c74e215c1cdd592eb980723 | REASONED |
| verify-transports: Use real protocol clients against every non-public path and transport: HTTP returns 401, 403 or a login redirect; gRPC returns UNAUTHENTICATED; SSE is refused; WebSockets reject the upgrade or reject protected operations, disclose no protected data and close on first-message authentication failure. A bare curl GET does not test non-HTTP transports. General authentication source; no protocol-specific reference in Sources. | OWASP authentication and password storage unknown | REASONED |
| verify-secret-scan: A secret scanner must find no leaks in the working tree, staged changes and full history; git log -p with a password/secret/API-key grep is supplementary and misses uncommitted files, some refs and secrets without those words. The Gitleaks source covers history and directory scans; staged-change scanning and git log -p behaviour are not cited. | OWASP authentication and password storage unknown; Gitleaks scanning modes b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b | REASONED |
| verify-default-accounts: Check that the user store has no admin, test or demo account with a known or empty password. This is the guide's recommendation; the OWASP Authentication Cheat Sheet does not list these account names (checked at commit 72865b1e). | OWASP authentication and password storage unknown | REASONED |
| verify-wrong-tenant: Expect a wrong-tenant token to be rejected in an application negative test after issuer and tid validation and the application tenant allowlist. Microsoft documents the validation rules; this guide recommends the allowlist and test, and no deployed rejection was observed. | OpenID Connect Core 1.0; Microsoft Entra multitenant token validation 49b84e07023770128d83039c07eafb84ff1de1df | REASONED |
| verify-cross-user: Verify that user A cannot read user B's resources. OWASP describes horizontal privilege escalation and object-specific access checks. | OWASP authentication and password storage unknown; OWASP authorization, secrets and session guidance 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| verify-origin-isolation: Expect direct origin access to fail in a deployment negative test. Cloudflare describes Access policy enforcement, origin IP protection for publicly routable origins, JWT validation and Tunnel access checks; these docs do not establish that a particular origin is unreachable. | OWASP authentication and password storage unknown; Cloudflare Access and origin configuration c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
<!-- version-basis:end -->

TLS without authentication leaves a service open to the whole internet over an encrypted channel. These rules apply to every service in this repository's guides. Each rule is a requirement unless it is marked `should` or phrased as a preference.

## Rules

1. **Deny by default.** Every endpoint that is not deliberately public must require authentication, applying OWASP's [deny-by-default principle](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L30-L38). Require authentication for APIs, health dashboards, admin panels, metrics, and message queues, and publish an explicit list of public paths (this guide's recommendation; the cited passage does not cover this); everything else authenticates.
2. **No default or shared credentials.** OWASP notes that [shared secrets hinder attribution](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L7). Change or disable every vendor default account before exposure. Each human gets an individual account; each service gets its own credential. Never ship credentials in code, containers, or documentation (these are this guide's recommendations; the cited passage does not cover them).
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
   Prefer a secret manager (this guide's recommendation; OWASP lists [secret managers](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L313) as one option). For containers, OWASP advises [environment variables only when mounted files or a secret-store fetch are not possible](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L462-L464). Add `.env` to `.gitignore` before the first commit, and scan the repository for leaked secrets (for example with gitleaks) before pushing. A secret that has reached a public repository, a chat, or a log is compromised: rotate it, since deleting the file does not unpublish it.
6. **Prefer SSO/OIDC over local accounts** where the product supports it, and enable MFA wherever available. [Cloudflare Access](cloudflare.md) can place an authentication layer in front of a self-hosted web application. Create the Access application before the tunnel route; without it, the published application is available to anyone on the Internet. Validate the Access JWT at the origin. For a Tunnel route, configure origin TLS verification and Access JWT checking; for a directly proxied HTTPS origin, use Full (strict) where applicable. Where no native MFA exists, add it with an identity layer, an app-level TOTP library, or a hosted service, per [mfa.md](mfa.md).
7. **Scope machine access.** API clients get their own tokens with the least privilege the task needs, not an admin password. Support and exercise rotation; set expiry where the platform allows it.
8. **Harden sessions.** Set cookies `Secure`, `HttpOnly`, and `SameSite` (`Lax` or `Strict`) (per [OWASP session-cookie guidance](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L131-L149)), sign them with a strong random secret (this guide's recommendation; the cited passage does not cover signing), and enforce an idle and an absolute timeout server-side (a cookie expiry alone does not stop a replayed cookie). Use an unpredictable session identifier, regenerate it (invalidating the old one) on login and on any privilege change, and reject a session ID the server never issued (session fixation). Invalidate sessions server-side on logout and on password change. `SameSite` is not a complete CSRF defense (`Lax` still allows a top-level state-changing GET, and a sibling subdomain can be same-site), so a cookie-authenticated state-changing request must also carry an anti-CSRF token or a strict `Origin`/`Sec-Fetch-Site` check, and must never change state through a safe method such as GET.
9. **Rate-limit authentication endpoints** and lock or delay after repeated failures. Per-client rate limits do not stop distributed credential stuffing (valid breached passwords spread thin across many addresses), so add account-aware and aggregate abuse controls alongside source-based ones, and avoid a lockout an attacker can use to deny a user access. Keep login, registration, and password-reset responses uniform in message and timing so they do not disclose whether an account exists. Log authentication successes and failures with source address and account, and keep the logs long enough to investigate an incident. fail2ban is a low-effort control for SSH and login panels on Linux hosts. Bound expensive endpoints too: inference, uploads, and job submission need request-size, concurrency, and timeout limits in addition to per-client rate limits, because an exposed AI endpoint left without them can burn GPU time and money even while correctly rejecting bad credentials, a failure mode known as denial of wallet. [realtime-webhooks.md](realtime-webhooks.md) covers the streaming and webhook transports these limits also apply to.
10. **Least privilege everywhere.** Separate admin from daily-use accounts, and give database and OS service accounts only the rights the application uses.
11. **Federated login is authentication, not authorization.** After Google, Microsoft, GitHub, or any provider returns an identity, this guide recommends checking an application allowlist (tenant, hosted domain, organization or group membership, or explicit users) before granting access; a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the `hd` claim in the validated ID token against an accepted domain; neither the email domain nor the request `hd` parameter controls access. Microsoft's multi-tenant `common` endpoint serves organizational and personal accounts. Validate the token issuer, signing-key issuer, and `tid`, then apply the application tenant allowlist. [oidc-integration.md](oidc-integration.md) has the checks; [identity-providers.md](identity-providers.md) has the providers.
12. **OIDC and OAuth hygiene.** Authorization code flow with PKCE (`S256`, never `plain`); exact-match redirect URIs; fresh per-transaction `state` and `nonce`, verified and bound to the initiating browser session; ID tokens validated for signature (keys from the provider's JWKS, algorithm pinned, never `none`), issuer, audience, and expiry; short-lived access tokens with refresh-token rotation; tokens never in URLs. Prefer a server-side session in an `HttpOnly` cookie to tokens in browser storage. Link accounts by issuer plus subject, never by email alone.
13. **Enforce MFA where access is granted, not only where it is enrolled.** A user who enrolled a second factor but can still act with a password-only session is not protected. Require the factor in provider policy or in the app, and test it.
14. **Protect the control plane.** MFA on the Git host, the cloud account, the DNS registrar, the deployment platform, the secret manager, and the identity provider's administrator account. A takeover there bypasses every control inside the app.
15. **Authenticate every transport.** WebSockets, server-sent events, GraphQL, gRPC, webhooks (verify the sender's signature and reject replays), inference endpoints, and management APIs each need their own check. A login on the HTML pages protects none of them. Machine credentials follow [machine-auth.md](machine-auth.md).
16. **Offboard promptly.** When a person leaves, revoke their provider membership, proxy sessions, application sessions, and personal tokens (this guide's recommendation; the cited Microsoft Entra source covers application sessions only). Measure each system's maximum time-to-revoke where immediate revocation is unavailable, and work to shrink it (this guide's recommendation; no delay was measured here). [deployment-lifecycle.md](deployment-lifecycle.md) has the lifecycle checks; [mfa.md](mfa.md) covers revoking the second factor along with the account.
17. **Set a password policy and reject breached passwords.** Require a minimum length of at least 8 characters when a second factor is enforced, otherwise at least 15 (NIST SP 800-63B-4); allow long passphrases and every character, and drop periodic-rotation and composition rules. Screen new and changed passwords against a known-breach corpus (for example the Pwned Passwords range API), because a correct breached password defeats both hashing and per-IP rate limits.
18. **Secure account recovery.** Password and MFA reset is a sensitive authentication surface: issue cryptographically random, single-use, short-lived, account-bound reset tokens; deliver them only to a pre-verified channel; keep the reset response non-enumerating; reauthenticate for a recovery-address or MFA-factor change; and on completion invalidate outstanding sessions and unused reset tokens. Recovery must never silently drop the MFA requirement.

## Quick checks

- REASONED: unauthenticated-rejection comparisons per the cited OWASP Authentication Cheat Sheet, with the expected rejections stated in this item; no deployed service exposing these paths and transports is available in the authoring environment, so no request was sent. A protocol-appropriate unauthenticated request to every non-public path from rule 1 (metrics, health, admin, message-queue UIs) and every transport from rule 15 (WebSocket, SSE, GraphQL, gRPC, webhook, inference, management API), not just the HTML app, is rejected and returns no protected data: an HTTP endpoint gives `401`, `403`, or a login redirect; a gRPC call gives `UNAUTHENTICATED`; an SSE stream is refused; a WebSocket either rejects the upgrade (handshake-time auth) or, with first-message auth, permits the upgrade but rejects protected operations, returns no protected data, and closes the connection on auth failure. A bare `curl` GET does not exercise the non-HTTP transports, so test each with a real client.
- DEMONSTRATED: scanner discrimination on disposable fixture repositories at marking time, with gitleaks 8.30.1: a planted randomized key was reported by the history, working-tree and staged scans (exit 9, leaks found: 1; gitleaks exits 9 only when invoked with --exit-code 9, and its default exit status on leaks is 1, re-observed at marking time across the history, working-tree and staged scan modes with gitleaks 8.30.1, with exit 0 on clean scans) and a clean control repository reported no leaks (exit 0), while the supplementary git log pattern matched a password-named diff and missed a renamed key, as this item warns; this demonstrates the checks, not that any given repository is clean. A secret scanner (gitleaks or similar) over the working tree, staged changes, and full history comes back clean; `git log -p | grep -iE 'password|secret|api[_-]?key'` is only a supplementary quick check, since it misses secrets without those words and does not cover uncommitted files or every ref.
- REASONED: default-account inspection recommended by this guide; no deployed user store is available in the authoring environment, so no account listing was read. The user store contains no account named `admin`, `test`, or `demo` with a known or empty password.
- REASONED: negative-test expectations per the cited OAuth 2.0 Security Best Current Practice (RFC 9700) and OpenID Connect Core 1.0; no deployed application, token issuer or fronting layer is available in the authoring environment, so none of these rejections was observed. The wrong-tenant expectation follows Microsoft's issuer and `tid` validation rules plus this guide's tenant-allowlist recommendation. The cross-user expectation follows the [pinned OWASP Authorization Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L93-L99). Cloudflare describes Access policy enforcement and origin IP protection, origin JWT validation, and Tunnel Access JWT checking; origin isolation remains a deployment test expectation. Negative tests should pass: a missing, expired, wrong-issuer, wrong-audience, or wrong-tenant token is rejected; user A cannot read user B's resources; direct access to the origin fails.

## Sources (checked September 2026)

- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP deny-by-default authorization (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L30-L38
- OWASP object-level authorization (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L93-L99
- OWASP shared-secret attribution (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L7
- OWASP secret-manager storage (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L313
- OWASP environment-variable caveat (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L462-L464
- OWASP session-cookie attributes (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L131-L149
- OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OAuth 2.0 Security Best Current Practice (RFC 9700): https://www.rfc-editor.org/rfc/rfc9700.html
- OpenID Connect Core 1.0: https://openid.net/specs/openid-connect-core-1_0.html
- NIST SP 800-63B-4 (password length, section 3.1.1.2): https://pages.nist.gov/800-63-4/sp800-63b.html
- Apache htpasswd (bcrypt `-B`; cost `-C`, default 5): https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- pyca/bcrypt changelog (5.0.0 rejects input over 72 bytes): https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/CHANGELOG.rst
- OpenSSL 3.5 rand and base64 output (checked October 2026): https://docs.openssl.org/3.5/man1/openssl-rand/
- Python 3.13 secrets.token_urlsafe (checked October 2026): https://docs.python.org/3.13/library/secrets.html#secrets.token_urlsafe
- Gitleaks git, directory and stdin scanning (pinned commit b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b, checked October 2026): https://github.com/gitleaks/gitleaks/blob/b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b/README.md#L172-L189
- Git v2.49.0 ignore rules exclude untracked files (checked October 2026): https://github.com/git/git/blob/v2.49.0/Documentation/gitignore.adoc#L15-L18
- OWASP compromised credentials and secret revocation (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L214-L218
- OWASP Secure, HttpOnly and SameSite attributes (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L163
- OWASP random session IDs and strict verification (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L265-L267
- OWASP session-ID renewal and invalidation after privilege changes (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L275
- OWASP server-side session invalidation on logout (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L317
- OWASP server-side idle and absolute session timeouts (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L323-L331
- OWASP browser storage and session identifiers (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/HTML5_Security_Cheat_Sheet.md#L53
- OWASP SameSite limitations (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L149
- OWASP CSRF tokens, origin checks and safe methods (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L17-L26
- OWASP Fetch Metadata cross-site policy (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L197
- OWASP Fetch Metadata sibling-domain trust (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md#L226
- OWASP API4:2023 resource and spending limits (checked October 2026): https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/
- OWASP request-size limits (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Denial_of_Service_Cheat_Sheet.md#L80
- OWASP connection timeouts and concurrent resource limits (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Denial_of_Service_Cheat_Sheet.md#L110-L113
- Microsoft Entra application-session revocation (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62
- Google OpenID Connect hosted-domain claim (rolling, checked October 2026): https://developers.google.com/identity/openid-connect/openid-connect
- Microsoft Entra multitenant common endpoint and issuer handling (pinned commit 49b84e07023770128d83039c07eafb84ff1de1df, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/howto-convert-app-to-be-multi-tenant.md#L43-L63
- Microsoft Entra multitenant token validation (pinned commit 49b84e07023770128d83039c07eafb84ff1de1df, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/access-tokens.md#L179-L187
- Cloudflare Access self-hosted application (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16
- Cloudflare Access origin connection and token validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54
- Cloudflare Access JWT validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17
- Cloudflare Tunnel origin parameters (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L198-L206
- Cloudflare Full (strict) SSL mode (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L16-L37
- Cloudflare Tunnel origin TLS verification (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L59-L67
