# Multi-factor authentication (MFA)

Passwords fail through phishing, reuse, and credential stuffing; a second factor keeps a stolen password from becoming access. This guide names the options and the references; it deliberately stops short of per-product walkthroughs, because an AI assistant that knows which option fits can implement it from the linked project documentation. The per-tool guides in this repository state what is viable for each stack.

## What to do (AI assistants)

1. Give every human-facing login on an exposed service a second factor where viable.
2. Prefer, in this order:
   1. Platform-native MFA, or OIDC/SSO login with MFA enforced at the identity provider.
   2. An identity-aware layer in front of the app (Cloudflare Access, or a self-hosted portal below), which adds MFA without changing the app, but only when the layer's own policy, or the identity provider it delegates to, requires a second factor.
   3. App-level TOTP through a library (below).
   4. A hosted MFA service such as Duo.
3. Prefer phishing-resistant factors (WebAuthn/passkeys) over TOTP and push, and any of those over emailed or SMS codes. Neither TOTP nor push is phishing-resistant, and a bare approve/deny push also invites prompt-bombing (MFA fatigue), so a push factor must use number matching or verified push, never a single tap.
4. When implementing TOTP yourself, the required pieces are: a random per-user secret; an `otpauth://` provisioning URI rendered as a QR code for the user's authenticator app; verification of 1 valid code before the factor activates; single-use recovery codes (stored hashed); rate limiting on code attempts; rejection of a code that has already been accepted for its time step (RFC 6238 forbids accepting a code twice); and TOTP secrets encrypted at rest and excluded from the repository (they cannot be hashed, since the server must read them to verify codes). Require the existing factor to be re-verified before a user disables it, replaces it, or mints new recovery codes, so a password-only or stolen session cannot remove MFA.
5. Give administrators a phishing-resistant factor (a passkey or a FIDO2 hardware key) wherever the platform offers one. TOTP is the floor; SMS is not acceptable for administrator accounts.
6. Enrolment is not enforcement. After users enrol, require the factor at the point of access (provider policy such as Conditional Access, Supabase `aal2` in policies, or the app's own check) and test that a password-only session is refused.

## Identity layers and auth proxies (open source)

- **Authelia**: authentication portal that sits in front of a reverse proxy; per its support matrix it integrates with nginx (`auth_request`), Traefik (`forwardAuth`), Caddy (`forward_auth`, 2.5.1 and later), HAProxy (through a Lua module), and Envoy, while Apache and IIS are documented as unsupported. Second factors: TOTP, WebAuthn/passkeys, and mobile push. https://www.authelia.com/
- **authentik**: self-hosted identity provider (OIDC and SAML) with TOTP and WebAuthn factors; apps behind it inherit its MFA. https://goauthentik.io/
- **Keycloak**: full OIDC/SAML identity provider with built-in OTP enrolment; the standard choice when you also need user federation and roles. https://www.keycloak.org/
- **oauth2-proxy**: puts any upstream behind an OIDC/OAuth2 provider; MFA is whatever that provider enforces. https://github.com/oauth2-proxy/oauth2-proxy

## App-level TOTP libraries

Each generates and verifies RFC 6238 codes and pairs with a QR library so users can enrol any authenticator app (Google Authenticator, Microsoft Authenticator, Aegis, FreeOTP, and password managers with TOTP support).

- Python: [pyotp](https://github.com/pyauth/pyotp) with [qrcode](https://pypi.org/project/qrcode/); [django-otp](https://pypi.org/project/django-otp/) integrates this into Django.
- Node.js: [otplib](https://github.com/yeojz/otplib) with [qrcode](https://www.npmjs.com/package/qrcode).
- Go: [pquerna/otp](https://github.com/pquerna/otp), which includes QR image generation.

## SSH and host logins

- [google-authenticator-libpam](https://github.com/google/google-authenticator-libpam): PAM module adding per-user TOTP to SSH and console logins, with QR enrolment in the terminal (`libpam-google-authenticator` package on Debian/Ubuntu).
- Duo Unix (`pam_duo`) adds push-approval MFA to SSH: https://duo.com/docs/duounix
- Make the PAM factor mandatory, or it is not enforced: with `UsePAM yes` and `KbdInteractiveAuthentication yes`, set `AuthenticationMethods publickey,keyboard-interactive:pam` in sshd (the `:pam` device pins the second step to the PAM stack, since a bare `keyboard-interactive` can route to another backend, and requiring the public key first means a key-based login still runs it), drop `nullok` once rollout is done so an un-enrolled user is denied rather than waved through, and set Duo's `failmode=secure` (its default `safe` grants access when Duo is unreachable) with a separately controlled emergency path.

## Hosted MFA

- **Hosted identity providers** (Microsoft Entra ID, Google Workspace, Auth0, Amazon Cognito, Clerk, Supabase Auth, and others) can enforce MFA for the apps that sign in through them, but the enforcement lives in a layer that varies by provider: a tenant or Conditional-Access policy, a per-user requirement, or authorization in your own app and database (Supabase, for example, still admits an `aal1` session unless your policies require `aal2`). Enrolment, or merely enabling a factor, does not enforce it; inspect and test the effective policy. Which tiers include MFA, and which do not, is in [identity-providers.md](identity-providers.md); wiring is in [oidc-integration.md](oidc-integration.md).
- **Duo**: the Duo Free edition covers up to 10 users with MFA and the Duo Mobile authenticator app (per https://duo.com/editions-and-pricing as of September 2026; verify current terms). Its Authentication Proxy speaks RADIUS and LDAP, which retrofits MFA onto VPNs and onto services with RADIUS support.
- **Cloudflare Access** ([cloudflare.md](cloudflare.md)): the emailed one-time PIN proves control of a mailbox only. Either enforce MFA at a connected identity provider (Access inherits it only when that provider's policy requires it for the login), or use Access's own independent MFA to require a second factor (a TOTP authenticator or a WebAuthn key) without relying on the IdP.

Enforcing MFA once at a central identity provider is easier to operate and audit than separate factors per app; prefer it when more than 1 service is involved.

## Passkeys and hardware keys

WebAuthn passkeys and FIDO2 hardware keys (YubiKey and similar) resist phishing because the credential is bound to the site's origin; a look-alike domain gets nothing. Every hosted provider in [identity-providers.md](identity-providers.md) offers them at some tier. When implementing them yourself, use a maintained WebAuthn library rather than parsing attestation by hand, store the credential public key and sign count, and require and verify the user-verification (UV) flag server-side where a passkey stands alone, or the ceremony proves possession only, not a second factor. Treat the sign count as advisory (many synced passkeys always report 0), not a hard clone-block. Keep a recovery path (a second key or single-use recovery codes) so a lost key is not a lockout, but note that for an admin on a phishing-resistant key the printed codes become the weakest, phishable link: prefer a second hardware key, and rate-limit and alert on recovery-code use.

## Where direct MFA is not viable

Unattended machine connections (service-to-service database and model-server APIs) have no interactive second-factor dialogue, though some databases do offer native MFA for an interactive human login (MySQL 8 supports up to three factors; its server-side WebAuthn plugin requires Enterprise Edition). For the unattended connections the pattern is: mutual TLS client certificates as the possession factor for the service itself, and MFA on every human path that reaches the host (SSH, bastions, admin panels). The database guides in this repository apply this pattern.

## Verify

- With only the password, attempt an MFA-protected operation, not just a login: once the factor is enrolled AND enforcement is on (provider policy, Supabase `aal2`, or the app's own check, per rule 6) the operation is refused, and completing the second factor then allows it. Some layers still open a password-only (`aal1`) session and enforce at the operation, so a session opening is not itself a failure; a protected operation that succeeds without a second factor is, and the user is not protected.
- Recovery codes are single-use, and their hashes rather than their values are stored.
- Repeated wrong codes hit a rate limit or lockout.
- Submitting the same valid TOTP code a second time within its time step is refused.
- No TOTP secret or recovery code appears in the repository or its history.
- A departed user's second factor, active sessions, and app-level access are revoked, not only their password changed. Enforcing MFA is not the end; offboarding belongs in the access lifecycle too, and [deployment-lifecycle.md](deployment-lifecycle.md) has the checklist.

## Standards and sources (checked September 2026)

- TOTP: https://www.rfc-editor.org/info/rfc6238/ ; HOTP: https://www.rfc-editor.org/info/rfc4226/
- `otpauth://` key URI format: https://github.com/google/google-authenticator/wiki/Key-Uri-Format
- WebAuthn: https://www.w3.org/TR/webauthn-2/
- Authelia proxy support matrix: https://www.authelia.com/integration/proxies/support/
- Duo editions and pricing: https://duo.com/editions-and-pricing
