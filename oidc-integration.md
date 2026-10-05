---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "0fbdb26cd9543b1a76a5e56447edb35e4b10ea2d54b0d7016c2448c3ce59f2fc",
  "components": {
    "oauth": {
      "name": "OAuth security BCP and PKCE",
      "basis": "unknown",
      "sources": {
        "sde329701b60c": "https://www.rfc-editor.org/info/rfc9700/",
        "scb6a61add96b": "https://www.rfc-editor.org/rfc/rfc7636.html"
      }
    },
    "core": {
      "name": "OpenID Connect Core",
      "basis": "1.0",
      "sources": {
        "scfd2790a544c": "https://openid.net/specs/openid-connect-core-1_0.html"
      }
    },
    "discovery": {
      "name": "OpenID Connect Discovery",
      "basis": "1.0",
      "sources": {
        "s85a922f6cf28": "https://openid.net/specs/openid-connect-discovery-1_0.html"
      }
    },
    "logout": {
      "name": "OpenID Connect RP-Initiated Logout",
      "basis": "1.0",
      "sources": {
        "s9cbf9365b369": "https://openid.net/specs/openid-connect-rpinitiated-1_0.html"
      }
    },
    "google": {
      "name": "Google identity documentation",
      "basis": "unknown",
      "sources": {
        "s4f815acc2976": "https://developers.google.com/identity/openid-connect/openid-connect",
        "s4e673839253c": "https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification"
      }
    },
    "entra": {
      "name": "Microsoft Entra documentation",
      "basis": "unknown",
      "sources": {
        "s024236a981bf": "https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens#validate-the-issuer",
        "sc592f9f58893": "https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference",
        "s46eca003125d": "https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference",
        "s6bed41a98a09": "https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app",
        "s21141e7818fc": "https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc",
        "s78a2bccc8dab": "https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-mfa-strength"
      }
    },
    "github": {
      "name": "GitHub OAuth and REST documentation",
      "basis": "unknown",
      "sources": {
        "sce29d52054f5": "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps",
        "s996a4496ed25": "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app",
        "sf0d89c2d1756": "https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps",
        "s06cab1763f65": "https://docs.github.com/en/rest/orgs/members",
        "s36328325db87": "https://docs.github.com/en/rest/teams/members"
      }
    },
    "okta": {
      "name": "Okta documentation",
      "basis": "unknown",
      "sources": {
        "s380f2ddc93a1": "https://developer.okta.com/docs/api/openapi/okta-oauth/guides/overview",
        "s06b93a8255e7": "https://developer.okta.com/docs/concepts/oauth-openid/",
        "s2935e4fa2dea": "https://developer.okta.com/docs/concepts/policies/",
        "s0abd0d40c095": "https://developer.okta.com/docs/guides/customize-tokens-groups-claim/main/",
        "s012a67c2b0ea": "https://developer.okta.com/docs/guides/sign-into-web-app-redirect/-/main/"
      }
    },
    "openid-client": {
      "name": "openid-client",
      "basis": "unknown",
      "sources": {
        "sa67c9c6498a8": "https://github.com/panva/openid-client"
      }
    },
    "authjs": {
      "name": "Auth.js",
      "basis": "unknown",
      "sources": {
        "scb72ef455167": "https://authjs.dev/",
        "s57969fbce700": "https://authjs.dev/concepts/session-strategies"
      }
    },
    "authlib": {
      "name": "Authlib",
      "basis": "unknown",
      "sources": {
        "s8e3650e799b8": "https://docs.authlib.org/en/stable/oauth2/client/web/flask.html"
      }
    },
    "go-oidc": {
      "name": "go-oidc",
      "basis": "unknown",
      "sources": {
        "s60cc1d7a8fe6": "https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc"
      }
    },
    "owasp-docs": {
      "name": "OWASP Cheat Sheet Series",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "s0562e4dc23f2": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L163",
        "sa5f6e96a876c": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L317",
        "s41cb2204a4e2": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L201",
        "s4f0aa80b1ef6": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/HTML5_Security_Cheat_Sheet.md#L53"
      }
    }
  },
  "claims": {
    "code-flow": {"text": "Use server-side authorization code flow with PKCE; RFC 9700 requires PKCE for public clients and recommends it for others, and discourages implicit grant.", "components": ["oauth"], "sources": ["oauth:sde329701b60c", "oauth:scb6a61add96b"], "status": "REASONED"},
    "redirect-match": {"text": "Register an exact callback URI including scheme, host, path and trailing slash; avoid prefix and wildcard matching.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "transaction-binding": {"text": "Generate state bound to the browser session, nonce and S256 code_challenge for each authorization; request openid email profile.", "components": ["oauth", "core"], "sources": ["oauth:scb6a61add96b", "core:scfd2790a544c"], "status": "REASONED"},
    "code-exchange": {"text": "Exchange the code server-side with client secret and the code_verifier that produced the challenge.", "components": ["oauth", "core"], "sources": ["oauth:scb6a61add96b", "core:scfd2790a544c"], "status": "REASONED"},
    "token-signature": {"text": "Validate the ID-token signature against provider JWKS using a pinned algorithm; Core defaults to RS256 unless another was registered.", "components": ["core", "discovery"], "sources": ["core:scfd2790a544c", "discovery:s85a922f6cf28"], "status": "REASONED"},
    "token-issuer": {"text": "Require iss to equal the configured issuer before trusting claims.", "components": ["core"], "sources": ["core:scfd2790a544c"], "status": "REASONED"},
    "token-audience": {"text": "aud must include the client ID and no untrusted additional audience; confirm azp equals the client ID where present.", "components": ["core"], "sources": ["core:scfd2790a544c"], "status": "REASONED"},
    "token-expiry-nonce": {"text": "Require unexpired exp and nonce equal to the value sent.", "components": ["core"], "sources": ["core:scfd2790a544c"], "status": "REASONED"},
    "token-leaks": {"text": "Keep codes and tokens out of logs, traces and analytics; set callback Referrer-Policy: no-referrer and redirect to a clean URL.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "refresh-tokens": {"text": "No offline access is requested, but provider-specific refresh tokens must remain server-side secrets, go only to the token endpoint and be revoked on offboarding.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "account-linking": {"text": "Link by issuer and sub, not mutable or non-unique email, phone_number or preferred_username.", "components": ["core", "google", "entra"], "sources": ["core:scfd2790a544c", "google:s4f815acc2976", "entra:sc592f9f58893"], "status": "REASONED"},
    "logout": {"text": "Destroy the server session and cookie; where advertised, redirect to end_session_endpoint with id_token_hint and registered post_logout_redirect_uri; Entra uses /oauth2/v2.0/logout.", "components": ["logout", "entra", "owasp-docs"], "sources": ["logout:s9cbf9365b369", "entra:s21141e7818fc", "owasp-docs:sa5f6e96a876c"], "status": "REASONED"},
    "discovery": {"text": "Fetch issuer/.well-known/openid-configuration for endpoints and jwks_uri; tenant-specific issuer must match, with Entra common/organizations handled separately.", "components": ["discovery", "entra"], "sources": ["discovery:s85a922f6cf28", "entra:s024236a981bf"], "status": "REASONED"},
    "google-allowlist": {"text": "Require verified ID-token hd to equal the Workspace domain; absent hd is rejection and the request parameter is not access control.", "components": ["google"], "sources": ["google:s4f815acc2976"], "status": "REASONED"},
    "entra-allowlist": {"text": "Require allowed tid and tenant-specific iss; prefer Single tenant only. organizations accepts any Entra tenant, common also personal accounts; key identity by oid or sub plus tid.", "components": ["entra"], "sources": ["entra:sc592f9f58893", "entra:s6bed41a98a09", "entra:s21141e7818fc"], "status": "REASONED"},
    "github-identity": {"text": "GitHub OAuth has no discovery or ID token; fetch GET https://api.github.com/user and key identity by numeric id, not login.", "components": ["github"], "sources": ["github:sce29d52054f5"], "status": "REASONED"},
    "github-org": {"text": "With read:org, GET /user/memberships/orgs/<org> must return 200 and state active; 404 is unaffiliated.", "components": ["github"], "sources": ["github:sf0d89c2d1756", "github:s06cab1763f65"], "status": "REASONED"},
    "github-team": {"text": "With read:org, GET /orgs/<org>/teams/<team_slug>/memberships/<username> must return 200 and state active; pending is an unaccepted invitation and 404 is no membership.", "components": ["github"], "sources": ["github:sf0d89c2d1756", "github:s36328325db87"], "status": "REASONED"},
    "okta-groups": {"text": "Add an ID-token groups claim on the org authorization server and request groups scope; require a named group. More than 100 groups fails, so narrow the filter.", "components": ["okta"], "sources": ["okta:s0abd0d40c095"], "status": "REASONED"},
    "default-deny": {"text": "Reject and log identities outside the allowlist before creating a session; do not create pending accounts by default.", "components": ["google", "entra", "okta"], "sources": ["google:s4f815acc2976", "entra:sc592f9f58893", "okta:s0abd0d40c095"], "status": "REASONED"},
    "google-registration": {"text": "Register a Google OAuth client and exact callback; discovery is https://accounts.google.com/.well-known/openid-configuration and iss is https://accounts.google.com or accounts.google.com.", "components": ["google"], "sources": ["google:s4f815acc2976"], "status": "REASONED"},
    "entra-registration": {"text": "Register a Web application, callback and client secret; prefer tenant-specific /v2.0/.well-known/openid-configuration discovery for single-tenant apps.", "components": ["entra"], "sources": ["entra:s6bed41a98a09", "entra:s21141e7818fc"], "status": "REASONED"},
    "entra-template": {"text": "For common/organizations, substitute GUID tid into the issuer template, match iss exactly, restrict signing keys by issuer scope and enforce the tenant allowlist.", "components": ["entra"], "sources": ["entra:s024236a981bf"], "status": "REASONED"},
    "github-registration": {"text": "Register an OAuth app callback; authorize at /login/oauth/authorize with read:user read:org, state and S256 PKCE; exchange at /login/oauth/access_token with secret, code, verifier and redirect_uri.", "components": ["github"], "sources": ["github:sce29d52054f5", "github:s996a4496ed25", "github:sf0d89c2d1756"], "status": "REASONED"},
    "github-callback-default": {"text": "Always send redirect_uri: omission selects the first callback. Apps with one callback before August 3, 2026 retain wildcard matching; disable it for exact matching.", "components": ["github"], "sources": ["github:sce29d52054f5"], "status": "REASONED"},
    "okta-registration": {"text": "Create an OIDC Web Application with sign-in/out URIs and narrowed assignment; use org discovery or /oauth2/<authorizationServerId> discovery, with iss matching the prefix.", "components": ["okta"], "sources": ["okta:s380f2ddc93a1", "okta:s012a67c2b0ea"], "status": "REASONED"},
    "openid-client-signature": {"text": "Call enableNonRepudiationChecks: openid-client otherwise trusts token-endpoint TLS in code flow; retain verifier, state and nonce in the initiating browser's server session.", "components": ["openid-client"], "sources": ["openid-client:sa67c9c6498a8"], "status": "REASONED"},
    "authjs-config": {"text": "Auth.js uses AUTH_<PROVIDER>_ID/SECRET and Okta/Entra ISSUER, with /api/auth/callback/<provider>; add the allowlist in signIn and override Entra common with the tenant issuer.", "components": ["authjs"], "sources": ["authjs:scb72ef455167"], "status": "REASONED"},
    "authjs-revocation": {"text": "Auth.js JWT-cookie logout leaves a copied token valid until exp unless blocked; use database sessions or a blocklist for server-side revocation.", "components": ["authjs"], "sources": ["authjs:s57969fbce700"], "status": "REASONED"},
    "authlib-config": {"text": "Authlib registration uses Google discovery, openid profile email and S256; authorize_redirect and authorize_access_token implement the callback flow.", "components": ["authlib"], "sources": ["authlib:s8e3650e799b8"], "status": "REASONED"},
    "go-oidc-verifier": {"text": "go-oidc verifies signature, issuer, audience and expiry; compare idToken.Nonce separately and leave SkipIssuerCheck off.", "components": ["go-oidc"], "sources": ["go-oidc:s60cc1d7a8fe6"], "status": "REASONED"},
    "entra-mfa": {"text": "Require authentication strength through Entra Conditional Access; check ID-token and optional-claims documentation before relying on amr=mfa.", "components": ["entra"], "sources": ["entra:s78a2bccc8dab", "entra:sc592f9f58893", "entra:s46eca003125d"], "status": "REASONED"},
    "google-mfa": {"text": "Enforce Workspace 2-Step Verification in policy; no Google ID-token MFA claim was verified for this guide.", "components": ["google"], "sources": ["google:s4e673839253c"], "status": "REASONED"},
    "okta-mfa": {"text": "Use Okta authentication and global-session policies; its amr includes pwd, mfa, otp and hwk.", "components": ["okta"], "sources": ["okta:s2935e4fa2dea", "okta:s380f2ddc93a1"], "status": "REASONED"},
    "verify-discovery": {"text": "The discovery probe reads Google issuer and jwks_uri; this does not demonstrate application authorization.", "components": ["google", "discovery"], "sources": ["google:s4f815acc2976", "discovery:s85a922f6cf28"], "status": "REASONED", "verify": [1]},
    "verify-anonymous": {"text": "Unauthenticated /admin must return 401 or a 302 to provider/login, never 200 or protected content; an unrelated redirect is not success.", "components": ["core"], "sources": ["core:scfd2790a544c"], "status": "REASONED", "verify": [1]},
    "verify-allowlist": {"text": "A valid account outside the Google domain, Entra tenant, GitHub organization or Okta group authenticates at the provider but is rejected and logged by the app.", "components": ["google", "entra", "github", "okta"], "sources": ["google:s4f815acc2976", "entra:sc592f9f58893", "github:s06cab1763f65", "okta:s0abd0d40c095"], "status": "REASONED"},
    "verify-redirect": {"text": "Changing redirect_uri host or adding a path segment must cause a provider error without redirection.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "verify-state": {"text": "A changed callback state must be rejected.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "verify-token": {"text": "Accept a valid ID-token control and reject one-property fixtures for expiry beyond skew, wrong aud/azp and broken signature in the token-validation path, not the code callback.", "components": ["core"], "sources": ["core:scfd2790a544c"], "status": "REASONED"},
    "verify-logout": {"text": "After logout a protected page returns to login and a copied old cookie stops authorizing; JWT sessions need database replacement or a revocation check.", "components": ["authjs", "logout", "owasp-docs"], "sources": ["authjs:s57969fbce700", "logout:s9cbf9365b369", "owasp-docs:sa5f6e96a876c"], "status": "REASONED"},
    "server-session": {"text": "After token validation and allowlist authorization, create a server-side session and give the browser only a session cookie marked Secure, HttpOnly and SameSite. Auth.js session-strategies is the nearest general session source; no dedicated reference for the complete cookie policy in Sources.", "components": ["authjs", "owasp-docs"], "sources": ["authjs:s57969fbce700", "owasp-docs:s0562e4dc23f2"], "status": "REASONED"},
    "browser-token-storage": {"text": "Do not store ID or access tokens in localStorage or script-readable cookies; this server-side login recipe has no browser need for them. General OAuth security source; no dedicated browser-storage reference in Sources.", "components": ["oauth", "owasp-docs"], "sources": ["oauth:sde329701b60c", "owasp-docs:s41cb2204a4e2", "owasp-docs:s4f0aa80b1ef6"], "status": "REASONED"},
    "client-secret-storage": {"text": "Keep the client secret in an environment variable or secret manager, never a repository or image. General OAuth security source; no dedicated secret-storage reference in Sources.", "components": ["oauth"], "sources": ["oauth:sde329701b60c"], "status": "REASONED"},
    "github-org-mfa": {"text": "GitHub OAuth has no ID token, so MFA depends on what the organization requires of its members. OAuth authorization and organization-membership references only; Sources has no GitHub organization-MFA-policy reference.", "components": ["github"], "sources": ["github:sce29d52054f5", "github:s06cab1763f65"], "status": "REASONED"},
    "authjs-session-storage": {"text": "Auth.js stores an encrypted JWT or database session ID in an HttpOnly cookie; use database sessions or a server blocklist when copied-cookie revocation is required.", "components": ["authjs"], "sources": ["authjs:s57969fbce700"], "status": "REASONED"},
    "mfa-session-check": {"text": "An app may additionally refuse an ID-token session showing no second factor only where the provider documents that claim; do not assume a portable MFA claim across providers.", "components": ["entra", "okta"], "sources": ["entra:sc592f9f58893", "entra:s46eca003125d", "okta:s380f2ddc93a1"], "status": "REASONED"}
  }
}
---
# OIDC login: wiring Google, Microsoft Entra, GitHub, and Okta into your app

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| code-flow: Use server-side authorization code flow with PKCE; RFC 9700 requires PKCE for public clients and recommends it for others, and discourages implicit grant. | OAuth security BCP and PKCE unknown | REASONED |
| redirect-match: Register an exact callback URI including scheme, host, path and trailing slash; avoid prefix and wildcard matching. | OAuth security BCP and PKCE unknown | REASONED |
| transaction-binding: Generate state bound to the browser session, nonce and S256 code_challenge for each authorization; request openid email profile. | OAuth security BCP and PKCE unknown; OpenID Connect Core 1.0 | REASONED |
| code-exchange: Exchange the code server-side with client secret and the code_verifier that produced the challenge. | OAuth security BCP and PKCE unknown; OpenID Connect Core 1.0 | REASONED |
| token-signature: Validate the ID-token signature against provider JWKS using a pinned algorithm; Core defaults to RS256 unless another was registered. | OpenID Connect Core 1.0; OpenID Connect Discovery 1.0 | REASONED |
| token-issuer: Require iss to equal the configured issuer before trusting claims. | OpenID Connect Core 1.0 | REASONED |
| token-audience: aud must include the client ID and no untrusted additional audience; confirm azp equals the client ID where present. | OpenID Connect Core 1.0 | REASONED |
| token-expiry-nonce: Require unexpired exp and nonce equal to the value sent. | OpenID Connect Core 1.0 | REASONED |
| token-leaks: Keep codes and tokens out of logs, traces and analytics; set callback Referrer-Policy: no-referrer and redirect to a clean URL. | OAuth security BCP and PKCE unknown | REASONED |
| refresh-tokens: No offline access is requested, but provider-specific refresh tokens must remain server-side secrets, go only to the token endpoint and be revoked on offboarding. | OAuth security BCP and PKCE unknown | REASONED |
| account-linking: Link by issuer and sub, not mutable or non-unique email, phone_number or preferred_username. | OpenID Connect Core 1.0; Google identity documentation unknown; Microsoft Entra documentation unknown | REASONED |
| logout: Destroy the server session and cookie; where advertised, redirect to end_session_endpoint with id_token_hint and registered post_logout_redirect_uri; Entra uses /oauth2/v2.0/logout. | OpenID Connect RP-Initiated Logout 1.0; Microsoft Entra documentation unknown; OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| discovery: Fetch issuer/.well-known/openid-configuration for endpoints and jwks_uri; tenant-specific issuer must match, with Entra common/organizations handled separately. | OpenID Connect Discovery 1.0; Microsoft Entra documentation unknown | REASONED |
| google-allowlist: Require verified ID-token hd to equal the Workspace domain; absent hd is rejection and the request parameter is not access control. | Google identity documentation unknown | REASONED |
| entra-allowlist: Require allowed tid and tenant-specific iss; prefer Single tenant only. organizations accepts any Entra tenant, common also personal accounts; key identity by oid or sub plus tid. | Microsoft Entra documentation unknown | REASONED |
| github-identity: GitHub OAuth has no discovery or ID token; fetch GET https://api.github.com/user and key identity by numeric id, not login. | GitHub OAuth and REST documentation unknown | REASONED |
| github-org: With read:org, GET /user/memberships/orgs/&lt;org&gt; must return 200 and state active; 404 is unaffiliated. | GitHub OAuth and REST documentation unknown | REASONED |
| github-team: With read:org, GET /orgs/&lt;org&gt;/teams/&lt;team_slug&gt;/memberships/&lt;username&gt; must return 200 and state active; pending is an unaccepted invitation and 404 is no membership. | GitHub OAuth and REST documentation unknown | REASONED |
| okta-groups: Add an ID-token groups claim on the org authorization server and request groups scope; require a named group. More than 100 groups fails, so narrow the filter. | Okta documentation unknown | REASONED |
| default-deny: Reject and log identities outside the allowlist before creating a session; do not create pending accounts by default. | Google identity documentation unknown; Microsoft Entra documentation unknown; Okta documentation unknown | REASONED |
| google-registration: Register a Google OAuth client and exact callback; discovery is https://accounts.google.com/.well-known/openid-configuration and iss is https://accounts.google.com or accounts.google.com. | Google identity documentation unknown | REASONED |
| entra-registration: Register a Web application, callback and client secret; prefer tenant-specific /v2.0/.well-known/openid-configuration discovery for single-tenant apps. | Microsoft Entra documentation unknown | REASONED |
| entra-template: For common/organizations, substitute GUID tid into the issuer template, match iss exactly, restrict signing keys by issuer scope and enforce the tenant allowlist. | Microsoft Entra documentation unknown | REASONED |
| github-registration: Register an OAuth app callback; authorize at /login/oauth/authorize with read:user read:org, state and S256 PKCE; exchange at /login/oauth/access_token with secret, code, verifier and redirect_uri. | GitHub OAuth and REST documentation unknown | REASONED |
| github-callback-default: Always send redirect_uri: omission selects the first callback. Apps with one callback before August 3, 2026 retain wildcard matching; disable it for exact matching. | GitHub OAuth and REST documentation unknown | REASONED |
| okta-registration: Create an OIDC Web Application with sign-in/out URIs and narrowed assignment; use org discovery or /oauth2/&lt;authorizationServerId&gt; discovery, with iss matching the prefix. | Okta documentation unknown | REASONED |
| openid-client-signature: Call enableNonRepudiationChecks: openid-client otherwise trusts token-endpoint TLS in code flow; retain verifier, state and nonce in the initiating browser's server session. | openid-client unknown | REASONED |
| authjs-config: Auth.js uses AUTH_&lt;PROVIDER&gt;_ID/SECRET and Okta/Entra ISSUER, with /api/auth/callback/&lt;provider&gt;; add the allowlist in signIn and override Entra common with the tenant issuer. | Auth.js unknown | REASONED |
| authjs-revocation: Auth.js JWT-cookie logout leaves a copied token valid until exp unless blocked; use database sessions or a blocklist for server-side revocation. | Auth.js unknown | REASONED |
| authlib-config: Authlib registration uses Google discovery, openid profile email and S256; authorize_redirect and authorize_access_token implement the callback flow. | Authlib unknown | REASONED |
| go-oidc-verifier: go-oidc verifies signature, issuer, audience and expiry; compare idToken.Nonce separately and leave SkipIssuerCheck off. | go-oidc unknown | REASONED |
| entra-mfa: Require authentication strength through Entra Conditional Access; check ID-token and optional-claims documentation before relying on amr=mfa. | Microsoft Entra documentation unknown | REASONED |
| google-mfa: Enforce Workspace 2-Step Verification in policy; no Google ID-token MFA claim was verified for this guide. | Google identity documentation unknown | REASONED |
| okta-mfa: Use Okta authentication and global-session policies; its amr includes pwd, mfa, otp and hwk. | Okta documentation unknown | REASONED |
| verify-discovery: The discovery probe reads Google issuer and jwks_uri; this does not demonstrate application authorization. | Google identity documentation unknown; OpenID Connect Discovery 1.0 | REASONED |
| verify-anonymous: Unauthenticated /admin must return 401 or a 302 to provider/login, never 200 or protected content; an unrelated redirect is not success. | OpenID Connect Core 1.0 | REASONED |
| verify-allowlist: A valid account outside the Google domain, Entra tenant, GitHub organization or Okta group authenticates at the provider but is rejected and logged by the app. | Google identity documentation unknown; Microsoft Entra documentation unknown; GitHub OAuth and REST documentation unknown; Okta documentation unknown | REASONED |
| verify-redirect: Changing redirect_uri host or adding a path segment must cause a provider error without redirection. | OAuth security BCP and PKCE unknown | REASONED |
| verify-state: A changed callback state must be rejected. | OAuth security BCP and PKCE unknown | REASONED |
| verify-token: Accept a valid ID-token control and reject one-property fixtures for expiry beyond skew, wrong aud/azp and broken signature in the token-validation path, not the code callback. | OpenID Connect Core 1.0 | REASONED |
| verify-logout: After logout a protected page returns to login and a copied old cookie stops authorizing; JWT sessions need database replacement or a revocation check. | Auth.js unknown; OpenID Connect RP-Initiated Logout 1.0; OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| server-session: After token validation and allowlist authorization, create a server-side session and give the browser only a session cookie marked Secure, HttpOnly and SameSite. Auth.js session-strategies is the nearest general session source; no dedicated reference for the complete cookie policy in Sources. | Auth.js unknown; OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| browser-token-storage: Do not store ID or access tokens in localStorage or script-readable cookies; this server-side login recipe has no browser need for them. General OAuth security source; no dedicated browser-storage reference in Sources. | OAuth security BCP and PKCE unknown; OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| client-secret-storage: Keep the client secret in an environment variable or secret manager, never a repository or image. General OAuth security source; no dedicated secret-storage reference in Sources. | OAuth security BCP and PKCE unknown | REASONED |
| github-org-mfa: GitHub OAuth has no ID token, so MFA depends on what the organization requires of its members. OAuth authorization and organization-membership references only; Sources has no GitHub organization-MFA-policy reference. | GitHub OAuth and REST documentation unknown | REASONED |
| authjs-session-storage: Auth.js stores an encrypted JWT or database session ID in an HttpOnly cookie; use database sessions or a server blocklist when copied-cookie revocation is required. | Auth.js unknown | REASONED |
| mfa-session-check: An app may additionally refuse an ID-token session showing no second factor only where the provider documents that claim; do not assume a portable MFA claim across providers. | Microsoft Entra documentation unknown; Okta documentation unknown | REASONED |
<!-- version-basis:end -->

Adding "Sign in with Google" takes an afternoon; the recurring defects are in what happens after the redirect comes back: an unvalidated ID token, an account matched by email, or an app that admits every Google or Microsoft account in existence because nobody checked whose it was. This guide gives the one flow every recipe shares, the exact claim to check per provider, the registration steps, and library pointers. Choosing a provider is covered in [identity-providers.md](identity-providers.md); login placed in front of an app without code changes is covered in [cloud-identity-proxies.md](cloud-identity-proxies.md). Authorizing an MCP client to a remote server layers additional obligations on this flow and is covered in [mcp-clients.md](mcp-clients.md).

## 1. The flow every recipe uses

Authorization code flow with PKCE from a server-side (confidential) client. RFC 9700 requires PKCE for public clients and recommends it for all others, web applications included; it requires exact string matching of redirect URIs at the authorization server; and it says clients should not use the implicit grant (`response_type=token`).

1. Register the exact callback URL at the provider (scheme, host, path, trailing slash). Prefix or wildcard matching is what makes redirect-based code theft work.
2. Send a random `state` bound to the browser session and a random `nonce` on every authorization request, plus `code_challenge` with `code_challenge_method=S256`. Scopes: `openid email profile`.
3. Exchange the code at the token endpoint from the server, with the client secret and the `code_verifier` that produced the `code_challenge`. Never from the browser.
4. Validate the ID token before trusting any claim (OpenID Connect Core section 3.1.3.7): the signature against the key set at the provider's `jwks_uri`, using an algorithm you pinned (Core says RS256 unless you registered another; the discovery document lists the provider's `id_token_signing_alg_values_supported`) rather than whatever the token header names; `iss` exactly equals the issuer you configured; `aud` contains your client ID and lists no audience you do not trust (per OIDC Core, reject a token carrying an untrusted additional audience, and where an `azp` claim is present confirm it equals your client ID); `exp` is in the future; `nonce` equals the one you sent.
5. Start a server-side session and give the browser only a session cookie marked `Secure`, `HttpOnly`, and `SameSite` per [authentication.md](authentication.md). Do not put ID or access tokens in `localStorage` or a script-readable cookie; nothing in the browser needs them. Keep authorization codes and tokens out of server logs, traces, and analytics, set `Referrer-Policy: no-referrer` on the callback, and redirect to a clean URL so the code does not linger in browser history or a `Referer` header. This login recipe does not request offline access, but refresh-token issuance is provider-specific, so treat any refresh token you receive as a server-side secret, send it only to the token endpoint, and revoke it on offboarding.
6. Link the identity to a local account by the pair (issuer, `sub`). OpenID Connect Core section 5.7 says `email`, `phone_number`, and `preferred_username` are not guaranteed unique and may change; Google and Microsoft document the same for their `email` claims. Matching by email alone lets a re-used or unverified address take over an account.
7. Logout: destroy the server-side session and expire the cookie; where the discovery document lists an `end_session_endpoint`, also redirect there with `id_token_hint` and a registered `post_logout_redirect_uri` (Entra: `/oauth2/v2.0/logout`).

The discovery document at `<issuer>/.well-known/openid-configuration` supplies the endpoints and `jwks_uri`; for tenant-specific discovery its `issuer` value must be identical to the prefix you fetched it from (Entra's tenant-independent `common`/`organizations` metadata instead returns a templated issuer, handled below). Every library in section 4 reads it for you.

## 2. Login is not authorization

The provider proves who the person is. Whether they may use your app is your check, run after token validation and before the session exists, against an allowlist. The claim differs per provider:

- **Google**: the `hd` claim in the ID token must equal your Workspace domain (`example.com`). The `hd` request parameter only optimizes the account picker; Google's documentation says not to rely on it for access control and to validate the returned `hd` claim. Treat a missing `hd` claim as a rejection.
- **Microsoft Entra**: the `tid` claim must be your tenant ID and `iss` must be `https://login.microsoftonline.com/<tenant-id>/v2.0`. Register the app as **Single tenant only** when only your organization signs in. The `organizations` authority accepts any Entra tenant and `common` also accepts personal accounts; the issuer then varies per tenant, so an app on those authorities that does not check `tid` (or the GUID in `iss`) admits every Microsoft account. Microsoft documents `email` and `preferred_username` as mutable and unfit for authorization; key the local account on `oid` or `sub` plus `tid`.
- **GitHub**: GitHub OAuth apps speak OAuth 2.0, not OpenID Connect; there is no discovery document and no ID token. After the token exchange call `GET https://api.github.com/user` for the identity, then check `GET /user/memberships/orgs/<org>` (200 with `"state": "active"` means a member; 404 means not affiliated) or a team with `GET /orgs/<org>/teams/<team_slug>/memberships/<username>` (200 with `"state": "active"`; the REST reference documents `pending` for an unaccepted invitation, and 404 means no membership). Both need the `read:org` scope. Key the local account on the numeric `id` from `/user`, not the `login`.
- **Okta**: add a `groups` claim to the ID token (org authorization server: **Applications > Applications >** your app **> Sign On**, edit the OpenID Connect ID Token section, filter **Matches regex** `.*`; the client must also request the `groups` scope) and require membership of a named group. The claim holds at most 100 groups and the request fails beyond that; use a narrower filter in large orgs.

The default for an identity that passes none of these is to reject and log it, never to create a pending account an admin later forgets to review.

## 3. Register the app at each provider

The client secret is a secret: environment variable or secret manager, never a repository or an image ([secrets.md](secrets.md)). Substitute the callback path your library expects for `https://app.example.com/auth/callback`.

- **Google**: Google Cloud console **Clients** page (`https://console.developers.google.com/auth/clients`); create an OAuth client and add the redirect URI. The match is exact, including scheme, case, and trailing slash. Discovery: `https://accounts.google.com/.well-known/openid-configuration`; `iss` is `https://accounts.google.com` or `accounts.google.com`.
- **Microsoft Entra**: Microsoft Entra admin center, **Entra ID > App registrations > New registration**; under **Supported account types** choose **Single tenant only** unless you are building for other organizations. Then **Authentication > Add a platform > Web** and add the redirect URI. Record the Application (client) ID and create a client secret. Discovery: `https://login.microsoftonline.com/<tenant>/v2.0/.well-known/openid-configuration` with `<tenant>` your directory (tenant) ID; prefer this tenant-specific form for a single-tenant app. `common` and `organizations` return a templated issuer `https://login.microsoftonline.com/{tenantid}/v2.0`, so validate by substituting the token's `tid` into the template, confirming `tid` is a GUID and the result equals `iss` exactly, restricting the signing key by its published `issuer` scope, and enforcing your tenant allowlist; never relax issuer validation to make `common` work.
- **GitHub**: profile picture **> Settings > Developer settings > OAuth apps > New OAuth App**; set the Authorization callback URL. Authorize at `https://github.com/login/oauth/authorize` with `client_id`, `redirect_uri`, `scope=read:user read:org`, `state`, and PKCE (`code_challenge` with `code_challenge_method=S256`; GitHub does not accept `plain`); exchange at `https://github.com/login/oauth/access_token` with `client_id`, `client_secret`, `code`, the `code_verifier` that produced the challenge, and the same `redirect_uri`. Always send `redirect_uri`; when it is absent GitHub uses the first registered callback. Apps that had a single callback URL before August 3, 2026 keep wildcard matching for it, which accepts any subdomain or subdirectory of the registered host; disable wildcard matching in the app settings so the callback must match exactly.
- **Okta**: Admin Console, **Applications and Resources > Applications > Create App Integration**, sign-in method **OIDC - OpenID Connect**, type **Web Application**; set the sign-in and sign-out redirect URIs and the assignment (Okta's guide allows everyone in the org; narrow it to a group). Client ID and secret are on the **General** tab under Client Credentials. Discovery: `https://<org>.okta.com/.well-known/openid-configuration` for the org authorization server, `https://<org>.okta.com/oauth2/<authorizationServerId>/.well-known/openid-configuration` for a custom one; `iss` equals that prefix.

## 4. Libraries

Use a maintained library; do not hand-parse JWTs. The snippets are from each library's documentation; the section 2 check is yours to add.

- **Node, [openid-client](https://github.com/panva/openid-client)** (`npm install openid-client`):
  ```javascript
  let config = await client.discovery(server, clientId, clientSecret)
  client.enableNonRepudiationChecks(config)   // enforce rule 4's ID-token signature check; by default openid-client trusts the token-endpoint TLS channel for the code flow
  let code_verifier = client.randomPKCECodeVerifier()
  let code_challenge = await client.calculatePKCECodeChallenge(code_verifier)
  let state = client.randomState()
  let nonce = client.randomNonce()
  let redirectTo = client.buildAuthorizationUrl(config, { redirect_uri, scope, code_challenge, code_challenge_method: 'S256', state, nonce })
  // callback (store code_verifier, state, and nonce in the initiating browser's server-side session, not local variables):
  let tokens = await client.authorizationCodeGrant(config, currentUrl, { pkceCodeVerifier: code_verifier, expectedState: state, expectedNonce: nonce })
  ```
- **Node, [Auth.js](https://authjs.dev/)** (`npm install next-auth@beta` for Next.js; SvelteKit and Express integrations exist): providers `next-auth/providers/google`, `github`, `okta`, and `microsoft-entra-id`, configured through `AUTH_<PROVIDER>_ID`, `AUTH_<PROVIDER>_SECRET`, and for Okta and Entra `AUTH_<PROVIDER>_ISSUER`; callbacks land on `/api/auth/callback/<provider>`. Sessions are an encrypted JWT, or a database session ID, in an `HttpOnly` cookie. With the JWT strategy, sign-out destroys the cookie but the token itself stays valid until `exp` unless your server keeps a blocklist (Auth.js documents this limitation); use database sessions, or the blocklist just mentioned, so logout invalidates a copied cookie rather than leaving it valid until `exp` ([authentication.md](authentication.md) requires logout to invalidate the session server-side). Set `AUTH_MICROSOFT_ENTRA_ID_ISSUER` to your tenant's `/v2.0` issuer: the documented default is `common`. Put the section 2 check in the `signIn` callback.
- **Python, [Authlib](https://docs.authlib.org/)** (`pip install Authlib`; Flask, Django, Starlette, FastAPI):
  ```python
  oauth.register('google', client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET',
      server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
      client_kwargs={'scope': 'openid profile email', 'code_challenge_method': 'S256'})
  # login:    return oauth.google.authorize_redirect(redirect_uri)
  # callback: token = oauth.google.authorize_access_token(); claims = token['userinfo']
  ```
- **Go, [go-oidc](https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc)** (`github.com/coreos/go-oidc/v3/oidc`):
  ```go
  provider, err := oidc.NewProvider(ctx, "https://accounts.google.com")
  verifier := provider.Verifier(&oidc.Config{ClientID: clientID})
  idToken, err := verifier.Verify(ctx, rawIDToken)   // signature, issuer, audience, expiry
  ```
  The package documents that it does not check the nonce value: compare `idToken.Nonce` to the one you stored. Leave `SkipIssuerCheck` off.

## 5. Where MFA comes from

Your app does not run the second factor; the provider does, under its policy: Conditional Access in Entra (**Entra ID > Conditional Access > Policies**, grant **Require authentication strength**; a P1 feature per [identity-providers.md](identity-providers.md)), 2-Step Verification in the Google Admin console (**Security > Authentication > 2-step verification**, Enforcement **On**), and authentication policies plus the global session policy in Okta. Ordering and options in [mfa.md](mfa.md).

An app can additionally refuse a session whose ID token shows no second factor, where the provider documents the claim. Okta's `amr` array carries values such as `pwd`, `mfa`, `otp`, and `hwk`. For Entra, check the ID token claims reference and the optional claims reference for the `amr` claim and its `mfa` value before relying on it. For Google, enforce 2SV in Workspace; no ID token MFA claim was verified for this guide. GitHub OAuth has no ID token, so MFA is whatever the organization requires of its members.

## Verify

REASONED: discovery and anonymous-admin probes follow the Google OIDC and OpenID Connect sources below; the protected-endpoint check needs an application deployment, which was not supplied for this metadata review. The guide records no live outcome; expected anonymous rejection is stated in the block.

```bash
curl -q -s https://accounts.google.com/.well-known/openid-configuration | jq -r '.issuer, .jwks_uri'
curl -q -sS -D - -o /dev/null https://app.example.com/admin   # unauthenticated GET: 401, or a 302 whose Location is the provider/login (not an unrelated app route), never 200 or app content
```

Negative tests matter more than the happy path:

- Sign in with a valid account outside the allowlist (a personal Gmail, another Entra tenant, a GitHub user outside the org, an Okta user outside the group): the provider authenticates, your app refuses and logs the identity.
- Edit `redirect_uri` in the authorization URL (add a path segment or change the host): the provider shows an error and never redirects.
- Change `state` on the callback URL: your app rejects the callback.
- Feed your rule-4 ID-token validation path (not the callback, which receives a code and never an ID token) a valid token as a positive control, then fixtures each differing in one property: expired beyond the allowed clock skew, a validly signed token with a wrong `aud`/`azp`, and an otherwise-valid token with a broken signature. It must accept the control and reject every fixture.
- Log out, then reload a protected page: it redirects to login. With database sessions the old session cookie no longer works; with JWT sessions it works until `exp`, so use database sessions or a revocation check; a copied pre-logout cookie must stop authorizing requests after logout, per [authentication.md](authentication.md).

## Sources (checked September 2026)

- RFC 9700, OAuth 2.0 Security Best Current Practice: https://www.rfc-editor.org/info/rfc9700/
- OpenID Connect Core 1.0 (ID token validation 3.1.3.7, claim stability 5.7): https://openid.net/specs/openid-connect-core-1_0.html ; Discovery 1.0: https://openid.net/specs/openid-connect-discovery-1_0.html ; RP-Initiated Logout 1.0: https://openid.net/specs/openid-connect-rpinitiated-1_0.html
- RFC 7636 (PKCE; the `code_verifier` is required at the token endpoint when a `code_challenge` was sent): https://www.rfc-editor.org/rfc/rfc7636.html
- Microsoft Entra token issuer validation (the `common`/`organizations` templated issuer and the signing-key issuer scope): https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens#validate-the-issuer
- Google OpenID Connect (discovery URL, `hd`, `sub` versus `email`, token validation): https://developers.google.com/identity/openid-connect/openid-connect
- Google Workspace: deploy 2-Step Verification: https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification
- Microsoft identity platform: register an application: https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app ; OpenID Connect (discovery, `{tenant}` values, redirect URI, sign-out): https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc
- Microsoft identity platform: ID token claims reference (`tid`, `iss`, `oid`, `sub`, `email`): https://learn.microsoft.com/en-us/entra/identity-platform/id-token-claims-reference ; optional claims reference (`amr`, `mfa` value): https://learn.microsoft.com/en-us/entra/identity-platform/optional-claims-reference
- Microsoft Entra Conditional Access: require MFA for all users: https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-mfa-strength
- GitHub OAuth apps: authorizing: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps ; creating: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app ; scopes: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- GitHub REST: organization members: https://docs.github.com/en/rest/orgs/members ; team members: https://docs.github.com/en/rest/teams/members
- Okta: OAuth 2.0 and OpenID Connect overview: https://developer.okta.com/docs/concepts/oauth-openid/ ; OIDC API reference (discovery, issuer, `amr`, `groups`): https://developer.okta.com/docs/api/openapi/okta-oauth/guides/overview
- Okta: add a groups claim: https://developer.okta.com/docs/guides/customize-tokens-groups-claim/main/ ; sign users in to your web application: https://developer.okta.com/docs/guides/sign-into-web-app-redirect/-/main/ ; policies concept: https://developer.okta.com/docs/concepts/policies/
- openid-client: https://github.com/panva/openid-client
- Auth.js (installation, providers): https://authjs.dev/ ; session strategies (a JWT cannot be expired early without a blocklist): https://authjs.dev/concepts/session-strategies
- Authlib Flask client: https://docs.authlib.org/en/stable/oauth2/client/web/flask.html
- go-oidc: https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc
- OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd: session cookie attributes (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L163
- OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd: server-side session invalidation (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L317
- OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd: browser token storage (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L201
- OWASP Cheat Sheet Series 668ba7db3d0da5868b8a0305c259f7f6914a6ecd: local storage and HttpOnly cookies (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/HTML5_Security_Cheat_Sheet.md#L53
