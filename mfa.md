# Multi-factor authentication (MFA)

Multi-factor authentication (MFA) asks for proof beyond a password, such as an authenticator-app code, a passkey or a hardware key. This guide helps your AI assistant choose and enforce it for each human login on an exposed service where viable, preferring platform or identity-provider MFA, with machine access handled separately.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/mfa.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against TOTP standard (no recorded version), authentik source version/2026.8.3, Keycloak documentation 26.7.4, oauth2-proxy documentation v7.15.4, Caddy forward_auth minimum 2.5.1, google-authenticator-libpam source 1.11, and MySQL multifactor authentication 8.0 and 8.4, plus 9 more recorded bases; 14 further sources are pinned to a commit and 13 carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 35 claims: 2 demonstrated by a check that ran and 33 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Passwords fail through phishing, reuse, and credential stuffing; a second factor keeps a stolen password from becoming access. This guide names the options and the references; it deliberately stops short of per-product walkthroughs, because an AI assistant that knows which option fits can implement it from the linked project documentation. The per-tool guides in this repository state what is viable for each stack.

## What to do (AI assistants)

1. Give every human-facing login on an exposed service a second factor where viable.
2. Prefer, in this order:
   1. Platform-native MFA, or OIDC/SSO login with MFA enforced at the identity provider.
   2. An identity-aware layer in front of the app (Cloudflare Access, or a self-hosted portal below), which adds MFA without changing the app, but only when the layer's own policy, or the identity provider it delegates to, requires a second factor.
   3. App-level TOTP through a library (below).
   4. A hosted MFA service such as Duo.
3. Prefer phishing-resistant factors (WebAuthn/passkeys) over TOTP and push, and any of those over emailed or SMS codes. Neither TOTP nor push is phishing-resistant, and a bare approve/deny push also invites prompt-bombing (MFA fatigue), so a push factor must use number matching or verified push, never a single tap. This guide requires checking the effective push flow or choosing another factor: for Authenticator MFA push in the MFA scenario, Entra requires number matching but permits Yes/No on the same device in Microsoft apps, and Duo documents verified code entry for supported flows but gives conflicting statements about Duo Unix support (see Sources). The cross-method preference is this guide's assessment.
4. When implementing TOTP yourself, the required pieces are: a random per-user secret; an `otpauth://` provisioning URI rendered as a QR code for the user's authenticator app; verification of 1 valid code before the factor activates; single-use recovery codes (stored hashed); rate limiting on code attempts; rejection of a code that has already been accepted for its time step (RFC 6238 forbids accepting a code twice); and TOTP secrets encrypted at rest and excluded from the repository (they cannot be hashed, since the server must read them to verify codes). Require the existing factor to be re-verified before a user disables it, replaces it, or mints new recovery codes, so a password-only or stolen session cannot remove MFA.
5. Give administrators a phishing-resistant factor (a passkey or a FIDO2 hardware key) wherever the platform offers one. Guide advice: TOTP is the floor. This guide requires that administrator accounts not use SMS. OWASP advises MFA for privileged users and against SMS for high-value applications; Microsoft Entra recommends phishing-resistant MFA for its administrator roles, while NIST SP 800-63B-4 section 2.2.2 requires federal staff, contractors and partners to use phishing-resistant authentication for federal systems and AAL2 verifiers to offer a phishing-resistant option.
6. Enrolment is not enforcement. After users enrol, require the factor at the point of access (provider policy such as Conditional Access, Supabase `aal2` in policies, or the app's own check) and test that a password-only session is refused.

## Identity layers and auth proxies (open source)

- **Authelia**: authentication portal that sits in front of a reverse proxy; per its support matrix it integrates with nginx (`auth_request`), Traefik (`forwardAuth`), Caddy (`forward_auth`, 2.5.1 and later), HAProxy (through a Lua module), and Envoy, while Apache and IIS are documented as unsupported. Second factors: TOTP, WebAuthn security keys, and Duo mobile push. Authelia v4.39.28 also documents passkey login; it counts as a single factor, and by default prompts for a password when the request requires MFA. https://www.authelia.com/
- **authentik**: its authenticator-validation stage rejects a response unless the login's device challenges include a compatible class: code responses check TOTP, static, SMS and email as one group, while WebAuthn and Duo each check their own class. Guide advice: require the validation stage in each protected login flow and test that a first-factor-only attempt is denied. https://goauthentik.io/
- **Keycloak**: its OTP policy configures time-based (TOTP) and counter-based generators and QR-code setup for authenticator apps. Guide advice: require OTP in each protected authentication flow and test enforcement after enrolment. https://www.keycloak.org/
- **oauth2-proxy**: configures an OAuth provider for login and routes requests to configured upstream endpoints. Guide advice: require MFA in the provider policy for this login and test that access without the second factor is denied. https://github.com/oauth2-proxy/oauth2-proxy

The authentik source, Keycloak documentation and oauth2-proxy documentation cited in Sources do not demonstrate automatic MFA inheritance or a deployed policy.

## App-level TOTP libraries

Each generates and verifies RFC 6238 codes and pairs with a QR library so users can enrol a compatible TOTP authenticator app (examples in this guide's assessment: Google Authenticator, Microsoft Authenticator, Aegis, FreeOTP, and password managers with TOTP support).

- Python: [pyotp](https://github.com/pyauth/pyotp) with [qrcode](https://pypi.org/project/qrcode/); [django-otp](https://pypi.org/project/django-otp/) integrates this into Django.
- Node.js: [otplib](https://github.com/yeojz/otplib) with [qrcode](https://www.npmjs.com/package/qrcode).
- Go: [pquerna/otp](https://github.com/pquerna/otp), which includes QR image generation.

## SSH and host logins

- [google-authenticator-libpam](https://github.com/google/google-authenticator-libpam): PAM module supporting per-account TOTP. Guide assessment: it protects only the logins whose PAM services include it. Its `google-authenticator` setup command displays a QR code when libqrencode is available. Debian trixie and Ubuntu noble list the `libpam-google-authenticator` package as 20191231-based builds; the behaviour above is cited at tag `1.11`.
- Duo Unix (`pam_duo`) adds push-approval MFA to SSH: https://duo.com/docs/duounix.
  The pinned `pam_duo.8` documents `verified_push` (default `no`), which cannot be combined with `autopush` (see Sources).
- Make the PAM factor mandatory, or it is not enforced: with `UsePAM yes` and `KbdInteractiveAuthentication yes`, set `AuthenticationMethods publickey,keyboard-interactive:pam` in sshd (the `:pam` device pins the second step to the PAM stack, since a bare `keyboard-interactive` can route to another backend, and requiring the public key first means a key-based login still runs it). Guide advice: drop `nullok` once rollout is done so this module rejects accounts without a secret file. Set Duo's `failmode=secure` (its default `safe` grants access when Duo is unreachable) with a separately controlled emergency path.

## Hosted MFA

- **Hosted identity providers** (Microsoft Entra ID, Google Workspace (administrators can require 2-Step Verification for selected users or groups), Auth0, Amazon Cognito, Clerk, Supabase Auth, and others) offer MFA controls for sign-ins. Guide assessment: an app using one is protected only when its effective provider or app policy requires the second factor for that sign-in. Enforcement lives in a layer that varies by provider: a tenant or Conditional-Access policy, a per-user requirement, or authorization in your own app and database (Supabase, for example, still admits an `aal1` session unless your policies require `aal2`). Enrolment, or merely enabling a factor, does not enforce it; inspect and test the effective policy. Which tiers include MFA, and which do not, is in [identity-providers.md](identity-providers.md); wiring is in [oidc-integration.md](oidc-integration.md).
- **Duo**: the Duo Free edition covers up to 10 users with MFA and the Duo Mobile authenticator app (per https://duo.com/editions-and-pricing as of September 2026; verify current terms). Its Authentication Proxy receives authentication requests from devices and applications via RADIUS or LDAP and contacts Duo for secondary authentication; guide advice: verify that each intended service sends its sign-ins through the proxy and requires the second factor.
- **Cloudflare Access** ([cloudflare.md](cloudflare.md)): the emailed one-time PIN proves control of a mailbox only. Either enforce MFA at a connected identity provider (Access inherits it only when that provider's policy requires it for the login), or use Access's own independent MFA to require a second factor (a TOTP authenticator or a WebAuthn key) without relying on the IdP.

Enforcing MFA once at a central identity provider is easier to operate and audit than separate factors per app; prefer it when more than 1 service is involved.

## Passkeys and hardware keys

WebAuthn passkeys and FIDO2 hardware keys (YubiKey and similar) resist phishing because the credential is bound to the site's origin; a look-alike domain gets nothing. Guide assessment: some hosted providers in [identity-providers.md](identity-providers.md) offer passkeys or security keys; check the provider and tier. When implementing them yourself, this guide advises using a maintained WebAuthn library rather than parsing attestation by hand (for example, py_webauthn v3.0.1, SimpleWebAuthn v14.0.3, or go-webauthn v0.18.2, whose pinned READMEs describe WebAuthn implementations), store the credential public key and sign count, and require and verify the user-verification (UV) flag server-side where a passkey stands alone, or the ceremony proves possession only, not a second factor. Guide advice: treat the sign count as a clone-risk signal, not an automatic clone block; WebAuthn permits a zero value when an authenticator does not implement a signature counter. Keep a recovery path (a second key or single-use recovery codes) so a lost key is not a lockout, but note that for an admin on a phishing-resistant key the printed codes become the weakest, phishable link: prefer a second hardware key (this guide's recommendation), rate-limit recovery-code attempts (NIST SP 800-63B-4 section 4.2.1.1 subjects saved recovery codes to the throttling requirements in section 3.2.2), and notify the account holder whenever a recovery code is used (section 4.2.3 requires every account recovery to send a notification to the subscriber or their designee). This guide also recommends alerting your own operators on recovery-code use; that is not a NIST requirement.

## Where direct MFA is not viable

In this guide's assessment, unattended machine connections (service-to-service database and model-server APIs) have no interactive second-factor dialogue, though some databases do offer native MFA for an interactive human login (MySQL 8.0 from 8.0.27, and MySQL 8.4, support up to three authentication factors; in MySQL 8.4 its server-side WebAuthn plugin is included only in Enterprise Edition, while the client-side plugin is included in all distributions). For the unattended connections this guide advises the pattern: mutual TLS client certificates as the possession factor for the service itself, and MFA on every human path that reaches the host (SSH, bastions, admin panels). OWASP documents client-certificate authentication and says to validate the server's identity and trust configuration independently. The [PostgreSQL](postgresql.md) and [MySQL](mysql.md) guides apply client-certificate controls; the PostgreSQL guide also directs human SSH and administrative UI access to MFA.

## Verify

- REASONED: operation-level enforcement per the guide's cited Supabase documentation entries on server-side MFA enforcement and on restrictive RLS requiring aal2, and the cited Microsoft Entra Conditional Access MFA authentication-strength requirement, with the expected refusal without and success with the second factor stated in this item; no deployed application, identity provider or enrolled test account is available in the authoring environment, and this item names no command, so no part of it ran locally. With only the password, attempt an MFA-protected operation, not just a login: once the factor is enrolled AND enforcement is on (provider policy, Supabase `aal2`, or the app's own check, per rule 6) the operation is refused, and completing the second factor then allows it. Some layers still open a password-only (`aal1`) session and enforce at the operation, so a session opening is not itself a failure; a protected operation that succeeds without a second factor is, and the user is not protected.
- REASONED: recovery-code handling per the guide's cited NIST SP 800-63B-4 look-up secrets entry, whose section 3.1.2.2 requires single successful use and hashed storage (reread in the local reference copy at marking time); no deployed application or credential store is available in the authoring environment, so neither a refused reuse nor the stored form was observed, and this item names no command. A reused code that works or a stored plaintext code is the exposed state. Recovery codes are single-use, and their hashes rather than their values are stored.
- REASONED: attempt throttling per the guide's cited HOTP (RFC 4226) and TOTP (RFC 6238) entries; no deployed application with an enrolled test account is available in the authoring environment, so no wrong codes were sent, and this item names no command. Unlimited wrong attempts are the exposed state and a rate limit or lockout the fixed one. Repeated wrong codes hit a rate limit or lockout.
- REASONED: replay refusal per the guide's cited TOTP (RFC 6238) entry; no deployed application with an enrolled test account is available in the authoring environment, so no code was submitted, and this item names no command. A second acceptance of the same code is the exposed state and its refusal the fixed one. Submitting the same valid TOTP code a second time within its time step is refused.
- DEMONSTRATED: repository and history search on disposable fixture repositories at marking time: a known-value search (git log --all -S over history, grep -rF outside .git over the working tree) found a planted synthetic base32 TOTP secret and three recovery codes in exposed repositories, in history after deletion and in the working tree, and found none of them in a clean control. Gitleaks 8.30.1 with default rules flagged the TOTP secret only when it was assigned to a SECRET-named variable and missed a bare base32 value and all three recovery codes, so a clean gitleaks run does not satisfy this item. For a new repository, search each known plaintext value with `git log --all -S'REPLACE_WITH_KNOWN_VALUE'` and `grep -rF --exclude-dir=.git -- 'REPLACE_WITH_KNOWN_VALUE' .`; Git selects commits whose occurrence count changes across refs and HEAD, and grep recursively searches fixed strings outside `.git`. Replace `REPLACE_WITH_KNOWN_VALUE` with each known plaintext value before running either command; empty output with the unsubstituted placeholder proves nothing. The search needs the plaintext values; by inference from the documented `--all` scope, reflog-only and unreachable commits are outside this scan, and `-S` misses unchanged occurrence counts. Without `--diff-merges` (except with `--first-parent`), merge commits do not match `-S`, and `-S` does not search commit or tag messages. This demonstrates the search, not that any given repository is clean. No TOTP secret or recovery code appears in the repository or its history.
- A departed user's second factor, active sessions, and app-level access are revoked, not only their password changed. Enforcing MFA is not the end; offboarding belongs in the access lifecycle too, and [deployment-lifecycle.md](deployment-lifecycle.md) has the checklist.

## Standards and sources (checked September 2026)

- TOTP: https://www.rfc-editor.org/info/rfc6238/ ; HOTP: https://www.rfc-editor.org/info/rfc4226/
- `otpauth://` key URI format: https://github.com/google/google-authenticator/wiki/Key-Uri-Format
- WebAuthn: https://www.w3.org/TR/webauthn-2/
- MySQL 8.0 multifactor authentication (support from 8.0.27; checked October 2026): https://dev.mysql.com/doc/refman/8.0/en/multifactor-authentication.html
- MySQL 8.4 multifactor authentication (up to three factors; checked October 2026): https://dev.mysql.com/doc/refman/8.4/en/multifactor-authentication.html
- MySQL 8.4 WebAuthn authentication (server-side plugin only in Enterprise Edition; client-side plugin in all distributions; checked October 2026): https://dev.mysql.com/doc/refman/8.4/en/webauthn-pluggable-authentication.html
- Authelia proxy support matrix (Caddy 2.5.1 and later): https://www.authelia.com/integration/proxies/support/
- Duo editions and pricing: https://duo.com/editions-and-pricing
- Duo Verified Push policy (rolling documentation, checked October 2026): https://duo.com/docs/policy#verified-push
- google-authenticator-libpam `1.11`, per-account OTP and conditional QR enrolment (checked October 2026): https://github.com/google/google-authenticator-libpam/blob/1.11/README.md#L45-L70
- google-authenticator-libpam `1.11`, per-account secret and `nullok` behaviour (checked October 2026): https://github.com/google/google-authenticator-libpam/blob/1.11/man/pam_google_authenticator.8.md#L16-L29
- Debian trixie `libpam-google-authenticator` package, `20191231-2.1` (rolling package record, checked October 2026): https://packages.debian.org/trixie/libpam-google-authenticator
- Ubuntu noble `libpam-google-authenticator` package, `20191231-2build1` (rolling package record, checked October 2026): https://packages.ubuntu.com/noble/libpam-google-authenticator
- Duo Authentication Proxy RADIUS and LDAP modes (rolling documentation, checked October 2026): https://duo.com/docs/authproxy-reference
- Google Workspace 2-Step Verification policy (rolling documentation, checked October 2026): https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification
- authentik source `version/2026.8.3`, authenticator-validation stage and allowed device classes (checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L80-L108
- Keycloak documentation `26.7.4`, OTP policy and QR-code setup (checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L2-L21
- oauth2-proxy documentation `v7.15.4`, configured OAuth provider (checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L94-L108
- oauth2-proxy documentation `v7.15.4`, configured upstream endpoints (checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L274
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, application session revocation (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L58-L62
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, application deprovisioning and session limits (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L137-L147
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, removal of app user and group assignments (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/manage-application-permissions.md#L91-L113
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, revocation of user-consented app permissions through Graph or PowerShell (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/manage-application-permissions.md#L40-L50
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, mTLS client-certificate authentication and server validation (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md#L217-L221
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, revocation of unneeded or compromised secrets (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L218
- pquerna/otp source `617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870`, TOTP enrollment validation (checked October 2026): https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L27-L30
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, reauthentication before factor changes (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L154-L155
- NIST digital identity guidelines `SP 800-63B-4`, single-use look-up secrets and hashed storage (checked October 2026): https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#look-up-secrets
- NIST digital identity guidelines `SP 800-63B-4`, section 2.2.2 (AAL2 phishing resistance), sections 3.1.3, 3.2.5, 3.1.3.1 and 3.1.3.3 (push fatigue, phishing resistance, email and PSTN), 3.1.2, 4.1.2.1, 4.2.1.1 and 4.2.3 (recovery), and 4.5 (authenticator invalidation); PDF (checked October 2026): https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b-4.pdf
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, MFA for privileged users (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L40
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, SMS caution for high-value applications (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L304-L309
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, recovery codes and alternate factors (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L142-L143
- Authelia source `v4.39.28`, passkey login factor behaviour (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/webauthn.md#L69-L75
- Authelia source `v4.39.28`, TOTP, WebAuthn security keys and Duo push factors (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31
- py_webauthn source `v3.0.1`, server-side registration and authentication verification (checked October 2026): https://github.com/duo-labs/py_webauthn/blob/v3.0.1/README.md#L4-L25
- SimpleWebAuthn source `v14.0.3`, server and browser packages (checked October 2026): https://github.com/MasterKale/SimpleWebAuthn/blob/v14.0.3/README.md#L15-L21
- go-webauthn source `v0.18.2`, Go WebAuthn library (checked October 2026): https://github.com/go-webauthn/webauthn/blob/v0.18.2/README.md#L10-L13
- PyOTP source `cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1`, OTP generation, verification and RFC 6238 support (checked October 2026): https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/README.rst#L4-L9
- Python qrcode source `f92c007498d796e4825638b7d50c14ea51e5457a`, QR code generation (checked October 2026): https://github.com/lincolnloop/python-qrcode/blob/f92c007498d796e4825638b7d50c14ea51e5457a/README.rst#L5-L8
- django-otp source `88cf4970423b11f29d6840311f53378d007a3d63`, Django integration and HOTP/TOTP implementations (checked October 2026): https://github.com/django-otp/django-otp/blob/88cf4970423b11f29d6840311f53378d007a3d63/README.rst#L16-L28
- otplib source `c5c11be2a50fd864b587854bff6d97c5f8aa9c84`, HOTP/TOTP and Node support (checked October 2026): https://github.com/yeojz/otplib/blob/c5c11be2a50fd864b587854bff6d97c5f8aa9c84/README.md#L13
- Node qrcode source `3848ed2c17de5bcdead487417dbf14c5dd017f8d`, QR code generation (checked October 2026): https://github.com/soldair/node-qrcode/blob/3848ed2c17de5bcdead487417dbf14c5dd017f8d/README.md#L2
- pquerna/otp source `617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870`, TOTP/HOTP generation, validation and QR images (checked October 2026): https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L15-L18
- OpenSSH portable source `V_9_9_P2`, ordered authentication methods and the PAM device (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L197-L211
- OpenSSH portable source `V_9_9_P2`, UsePAM and keyboard-interactive authentication (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L2017-L2026
- Duo Unix source `91e3c987f256afdb166b26be777cef6e1ab2af11`, pam_duo failmode and push approval (checked October 2026): https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L44-L53
- Duo Unix source `91e3c987f256afdb166b26be777cef6e1ab2af11`, pam_duo `verified_push` and `autopush` options (checked October 2026): https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L60-L63
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, administrator phishing-resistant MFA policy (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-admin-phish-resistant-mfa.md#L12-L21
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Conditional Access MFA authentication-strength requirement (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Authenticator push number matching (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L12
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Authenticator MFA number entry (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L26-L28
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, same-device Yes/No exception (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L96-L100
- Auth0 archived documentation `5258d17ede3eea0ed0e330d15f8921a542564f68`, factor enablement and separate MFA enforcement choice (checked October 2026): https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12
- Auth0 MFA documentation, current factor and enforcement policy documentation (rolling documentation, checked October 2026): https://auth0.com/docs/secure/multi-factor-authentication/enable-mfa
- Amazon Cognito API source `2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da`, required versus optional MFA (checked October 2026): https://github.com/aws/aws-sdk-go-v2/blob/2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da/service/cognitoidentityprovider/api_op_SetUserPoolMfaConfig.go#L67-L76
- Clerk documentation `26ef3ace7508d46d6242c377e830a7791b0a2fdb`, application-wide versus user-selected MFA (checked October 2026): https://github.com/clerk/clerk-docs/blob/26ef3ace7508d46d6242c377e830a7791b0a2fdb/docs/guides/configure/auth-strategies/sign-up-sign-in-options.mdx#L168-L171
- Supabase documentation `10c7379c970ae4d2f30f3158194061cf5ffb8fc5`, server-side MFA enforcement beyond enrollment UI (checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L94-L96
- Supabase documentation `10c7379c970ae4d2f30f3158194061cf5ffb8fc5`, restrictive RLS requiring aal2 (checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L200
- Cloudflare documentation `c896795b8e8bab68d05ae78d64c9cbcda1fdb104`, email one-time PIN login (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15
- Cloudflare documentation `c896795b8e8bab68d05ae78d64c9cbcda1fdb104`, independent MFA with TOTP and WebAuthn security keys (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24
- Git documentation `v2.56.0`, --all includes refs and HEAD (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/rev-list-options.adoc#L167-L169
- Git documentation `v2.56.0`, -S occurrence-count search (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/diff-options.adoc#L650-L653
- Git documentation `v2.56.0`, -S move and unchanged-count limits (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/gitdiffcore.adoc#L251-L259
- Git documentation `v2.56.0`, merge-commit -S limit and first-parent exception (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L130-L135
- GNU grep documentation `v3.12`, recursive search (lines 757-769) (checked October 2026): https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n757
- GNU grep documentation `v3.12`, fixed-string search (lines 1150-1156) (checked October 2026): https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1150
- GNU grep documentation `v3.12`, directory exclusion (lines 734-740) (checked October 2026): https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n734


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- totp: TOTP standard (unknown)
- hotp: HOTP standard (unknown)
- uri: Authenticator key URI format (unknown)
- webauthn: WebAuthn standard (unknown)
- authelia: Authelia proxy support (unknown)
- authentik-source: authentik source (version/2026.8.3)
- keycloak-source: Keycloak documentation (26.7.4)
- oauth2-proxy-source: oauth2-proxy documentation (v7.15.4)
- caddy-min: Caddy forward_auth minimum (2.5.1)
- duo: Duo editions (unknown)
- duo-push-policy: Duo Verified Push policy (unknown)
- ssh-pam: SSH and PAM MFA (citation gap) (unknown)
- google-authenticator-libpam-source: google-authenticator-libpam source (1.11)
- google-authenticator-libpam-packages: google-authenticator-libpam package records (unknown)
- duo-proxy-docs: Duo Authentication Proxy documentation (unknown)
- google-workspace-docs: Google Workspace 2SV documentation (unknown)
- supabase: Supabase Auth MFA (citation gap) (unknown)
- access: Cloudflare Access MFA (citation gap) (unknown)
- mysql: MySQL multifactor authentication (8.0)
- mysql-8-4: MySQL multifactor authentication (8.4)
- mysql-webauthn: MySQL WebAuthn authentication (8.4)
- entra-docs: Microsoft Entra documentation (231747abc59ae3d50c74e215c1cdd592eb980723)
- owasp-docs: OWASP cheat sheets (668ba7db3d0da5868b8a0305c259f7f6914a6ecd)
- otp-source: pquerna/otp source (617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870)
- nist: NIST digital identity guidelines (SP 800-63B-4)
- authelia-source: Authelia source (v4.39.28)
- pyotp-source: PyOTP source (cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1)
- python-qrcode-source: Python qrcode source (f92c007498d796e4825638b7d50c14ea51e5457a)
- django-otp-source: django-otp source (88cf4970423b11f29d6840311f53378d007a3d63)
- otplib-source: otplib source (c5c11be2a50fd864b587854bff6d97c5f8aa9c84)
- node-qrcode-source: Node qrcode source (3848ed2c17de5bcdead487417dbf14c5dd017f8d)
- openssh-source: OpenSSH portable source (V_9_9_P2)
- duo-unix-source: Duo Unix source (91e3c987f256afdb166b26be777cef6e1ab2af11)
- auth0-docs: Auth0 archived documentation (5258d17ede3eea0ed0e330d15f8921a542564f68)
- auth0-rolling: Auth0 MFA documentation (unknown)
- cognito-api-source: Amazon Cognito API source (2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da)
- clerk-docs: Clerk documentation (26ef3ace7508d46d6242c377e830a7791b0a2fdb)
- supabase-docs: Supabase documentation (10c7379c970ae4d2f30f3158194061cf5ffb8fc5)
- cf-docs: Cloudflare documentation (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- webauthn-python: py_webauthn source (v3.0.1)
- webauthn-node: SimpleWebAuthn source (v14.0.3)
- webauthn-go: go-webauthn source (v0.18.2)
- git-docs: Git documentation (v2.56.0)
- grep-docs: GNU grep documentation (v3.12)

Claims (full source mapping in the JSON block below):

- totp-secret (REASONED; totp): Generate a random per-user TOTP secret; verification requires the recoverable secret rather than its hash.
- totp-provisioning (REASONED; uri): Provision the authenticator with an otpauth:// URI rendered as a QR code.
- totp-storage (REASONED; totp): Encrypt TOTP secrets at rest and exclude them from the repository.
- totp-throttling (REASONED; hotp, totp): Rate-limit code attempts; repeated wrong codes must hit a rate limit or lockout.
- totp-replay (REASONED; totp): Reject an already accepted code within its time step; Verify submits the same valid code twice and expects refusal on reuse.
- authelia-proxies (REASONED; authelia, caddy-min): Authelia integrates with nginx auth_request, Traefik forwardAuth, Caddy forward_auth from 2.5.1, HAProxy via Lua and Envoy; Apache and IIS are unsupported.
- duo-free (REASONED; duo): Duo Free covers up to 10 users with MFA and Duo Mobile as recorded in September 2026; verify current terms.
- webauthn-origin (REASONED; webauthn): Prefer WebAuthn/passkeys and FIDO2 keys for phishing resistance: credentials are bound to the site origin.
- webauthn-verification (REASONED; webauthn): Store the credential public key and sign count; require and verify UV server-side when a passkey stands alone.
- hosted-passkeys (REASONED; webauthn): Guide assessment: some hosted identity providers offer passkeys or security keys; check the provider and tier before relying on availability. The linked identity-providers guide gives examples; the WebAuthn standard does not establish universal provider coverage.
- webauthn-counter (REASONED; webauthn): Guide advice: treat sign count as a clone-risk signal, not an automatic clone block; WebAuthn permits zero when an authenticator does not implement a signature counter.
- verify-secret-storage (DEMONSTRATED; totp): Check that no TOTP secret appears in the repository or its history.
- mfa-enforcement (REASONED; totp, entra-docs, auth0-docs, auth0-rolling, cognito-api-source, clerk-docs, supabase-docs): Give every exposed human-facing login a second factor where viable; prefer native or IdP-enforced MFA, then an identity layer whose own or upstream policy requires MFA, app-level TOTP, then a hosted MFA service. Enrollment alone is not enforcement.
- push-matching (REASONED; webauthn, duo, duo-unix-source, entra-docs, nist, duo-push-policy): Prefer WebAuthn/passkeys over TOTP or push, and those over email or SMS codes. TOTP and push are not phishing-resistant; push must use number matching or verified push, never bare approve/deny, to resist prompt-bombing. NIST SP 800-63B-4 sections 3.1.3, 3.2.5, 3.1.3.1 and 3.1.3.3 support the fatigue, phishing and email/PSTN rationale. For Authenticator MFA push in the MFA scenario, Entra requires number matching; its same-device Microsoft app flow can show Yes/No. Duo's Verified Duo Push uses code entry in supported flows, but its policy both lists Duo Unix v2.2.0 and later as supported and says verification has no effect in Duo Unix. The pinned pam_duo.8 documents verified_push (default no), which cannot be combined with autopush. This guide requires checking the effective push flow or choosing another factor; the cross-method preference is this guide's assessment. The cited Duo editions source covers editions and pricing only.
- totp-activation (REASONED; totp, otp-source): Verify one valid TOTP code before activating the factor.
- recovery-codes (REASONED; totp, nist, owasp-docs): Issue single-use recovery codes and store hashes rather than the code values; Verify checks both storage and refusal on reuse.
- factor-changes (REASONED; totp, owasp-docs): Require re-verification of the existing factor before disabling or replacing it or minting new recovery codes, so a password-only or stolen session cannot remove MFA.
- admin-factors (REASONED; webauthn, owasp-docs, entra-docs, nist): Give administrators a phishing-resistant passkey or FIDO2 key wherever offered; TOTP is the floor and SMS is unacceptable for administrator accounts. OWASP advises MFA for privileged users; Microsoft Entra recommends phishing-resistant MFA for its administrator roles, and NIST SP 800-63B-4 section 2.2.2 requires it for federal staff, contractors and partners accessing federal systems and requires an AAL2 phishing-resistant option. The TOTP floor is this guide's advice; this guide requires that administrator accounts not use SMS, and OWASP advises against SMS for high-value applications.
- authelia-factors (REASONED; authelia, authelia-source): The body lists TOTP, WebAuthn security keys and Duo mobile push as Authelia second factors. Authelia v4.39.28 also documents passkey login, which counts as a single factor and by default prompts for a password when the request requires MFA.
- identity-layer-factors (REASONED; authentik-source, keycloak-source, oauth2-proxy-source): The authentik validation stage rejects a response unless the login's device challenges include a compatible class; Keycloak documents OTP policy for time-based (TOTP) and counter-based generators; oauth2-proxy configures an OAuth provider and routes to upstream endpoints. Requiring MFA in each protected login flow or provider policy and testing second-factor enforcement is this guide's advice.
- totp-libraries (REASONED; totp, pyotp-source, python-qrcode-source, django-otp-source, otplib-source, node-qrcode-source, otp-source): The body lists pyotp with qrcode and django-otp, Node otplib with qrcode, and pquerna/otp with QR generation as RFC 6238 implementation options. Each library generates and verifies RFC 6238 codes and pairs with a QR library so users can enrol a compatible TOTP authenticator app.
- ssh-pam-enforcement (REASONED; ssh-pam, openssh-source): Make SSH PAM MFA mandatory with UsePAM yes, KbdInteractiveAuthentication yes and AuthenticationMethods publickey,keyboard-interactive:pam; :pam pins the second step to PAM and the public-key-first sequence still runs it for key-based login.
- ssh-nullok (REASONED; google-authenticator-libpam-source, google-authenticator-libpam-packages): Guide advice: remove nullok after rollout so accounts without a secret file are denied by this PAM module. google-authenticator-libpam is a PAM module supporting per-account TOTP. Guide assessment: it protects only the logins whose PAM services include it. Its setup command displays a QR code when libqrencode is available. Debian trixie and Ubuntu noble list libpam-google-authenticator as 20191231-based builds; the behaviour above is cited at tag 1.11.
- duo-unix-failmode (REASONED; duo, duo-unix-source): Duo Unix pam_duo adds SSH push MFA; set failmode=secure for mandatory MFA because default safe grants access when Duo is unreachable, and keep a separately controlled emergency path. The pinned pam_duo.8 also documents verified_push (default no), which cannot be combined with autopush.
- supabase-assurance (REASONED; supabase, supabase-docs): Supabase admits an aal1 session unless app and database policies require aal2; enrollment or enabling a factor is not enforcement, so inspect and test the effective policy.
- google-workspace-enforcement (REASONED; google-workspace-docs): Google Workspace administrators can require 2-Step Verification for selected users or groups. Guide assessment: an app using a hosted provider is protected only when its effective provider or app policy requires the second factor for that sign-in. Guide advice: inspect and test the effective policy for each protected sign-in.
- duo-proxy (REASONED; duo-proxy-docs): Duo Authentication Proxy receives requests from devices and applications via RADIUS or LDAP and contacts Duo for secondary authentication. Guide advice: verify that each intended service sends its sign-ins through the proxy and requires the second factor.
- access-mfa (REASONED; access, cf-docs): An Access emailed one-time PIN proves mailbox control only; require MFA at the connected IdP for this login or Access independent MFA with TOTP or a WebAuthn key.
- webauthn-library (REASONED; webauthn, webauthn-python, webauthn-node, webauthn-go): When implementing WebAuthn yourself, this guide advises using a maintained WebAuthn library rather than hand-parsing attestation. The pinned py_webauthn, SimpleWebAuthn and go-webauthn READMEs document server-side WebAuthn implementation options; the recommendation to use a maintained library is this guide's assessment, not a README requirement.
- webauthn-recovery (REASONED; webauthn, nist, owasp-docs): Keep a second key or single-use recovery codes to avoid lost-key lockout; for administrators on phishing-resistant keys, prefer a second hardware key because printed codes are phishable, rate-limit recovery-code attempts, notify the account holder of recovery-code use, and alert operators on it. NIST SP 800-63B-4 section 4.1.2.1 supports two means of authentication in general; section 3.1.2 says look-up secrets are not phishing-resistant; sections 4.2.1.1 and 4.2.3 support saved recovery-code throttling and account-recovery notification to the subscriber or their designee. The administrator second-hardware-key preference and operator alert are this guide's recommendations; NIST does not require an operator alert; no pinned reference establishes the administrator-specific preference or operator alert.
- mysql-factors (REASONED; mysql, mysql-8-4, mysql-webauthn): Guide assessment: some databases offer native MFA for an interactive human login. MySQL 8.0 from 8.0.27, and MySQL 8.4, support up to three authentication factors; in MySQL 8.4 the server-side WebAuthn authentication plugin is included only in Enterprise Edition, while the client-side plugin is included in all distributions.
- unattended-mtls (REASONED; totp, webauthn, owasp-docs): Guide assessment: unattended database and model-server API connections have no interactive second-factor dialogue. Guide advice: use mutual TLS client certificates as the service's possession factor and MFA on human paths through SSH, bastions and admin panels. OWASP documents that mTLS authenticates the client with a certificate and proof of its private key and requires independent server-identity validation. The possession-factor interpretation and human-path requirement are this guide's advice; the PostgreSQL and MySQL guides document client-certificate controls.
- verify-mfa-operation (REASONED; totp, supabase-docs): After enrollment and enforcement, a password-only attempt at an MFA-protected operation must fail and completing the second factor must allow it. Opening an aal1 session alone is not a failure when enforcement occurs at the operation.
- verify-recovery-history (DEMONSTRATED; totp, git-docs, grep-docs): Verify requires that no TOTP secret or recovery code appears in the repository or its history. Git --all includes refs and HEAD, while -S selects occurrence-count changes; GNU grep -rF --exclude-dir=.git recursively searches fixed strings outside .git. This known-value scan needs plaintext values; empty output with an unsubstituted placeholder proves nothing. By inference from the documented --all scope, it does not cover reflog-only or unreachable commits; -S also misses unchanged occurrence counts. Without --diff-merges (except with --first-parent), merge commits do not match -S, and -S does not search commit or tag messages. A clean result is not proof that an arbitrary repository is clean.
- verify-offboarding (REASONED; totp, entra-docs, owasp-docs, nist): Verify that a departed user's second factor, active sessions and app-level access are revoked; changing only the password is insufficient. NIST SP 800-63B-4 section 4.5 requires CSPs to promptly invalidate authenticators when the CSP determines that the subscriber no longer meets its eligibility requirements. Entra documents removal of application user and group assignments, revocation of user-consented app permissions through Graph or PowerShell, application deprovisioning and application-controlled session revocation; its identity-session revocation alone cannot revoke an application-issued session token. The deployed offboarding outcome remains a test expectation, and the cited documents do not establish it for a particular application.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "06aa1823fd416e66292de6a4594877e96b12339c020f4993a15d12b494420fc2",
  "components": {
    "totp": {
      "name": "TOTP standard",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "hotp": {
      "name": "HOTP standard",
      "basis": "unknown",
      "sources": {
        "s05c8bf9b6329": "https://www.rfc-editor.org/info/rfc4226/"
      }
    },
    "uri": {
      "name": "Authenticator key URI format",
      "basis": "unknown",
      "sources": {
        "s4c73b28585c7": "https://github.com/google/google-authenticator/wiki/Key-Uri-Format"
      }
    },
    "webauthn": {
      "name": "WebAuthn standard",
      "basis": "unknown",
      "sources": {
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "authelia": {
      "name": "Authelia proxy support",
      "basis": "unknown",
      "sources": {
        "s1409ac8fe3d9": "https://www.authelia.com/integration/proxies/support/"
      }
    },
    "authentik-source": {
      "name": "authentik source",
      "basis": "version/2026.8.3",
      "sources": {
        "s18275a7072e9": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L80-L108"
      }
    },
    "keycloak-source": {
      "name": "Keycloak documentation",
      "basis": "26.7.4",
      "sources": {
        "s1e55f7daaa0d": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L2-L21"
      }
    },
    "oauth2-proxy-source": {
      "name": "oauth2-proxy documentation",
      "basis": "v7.15.4",
      "sources": {
        "sa403e3d826b4": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L94-L108",
        "se7a200583def": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L274"
      }
    },
    "caddy-min": {
      "name": "Caddy forward_auth minimum",
      "basis": "2.5.1",
      "sources": {
        "s1409ac8fe3d9": "https://www.authelia.com/integration/proxies/support/"
      }
    },
    "duo": {
      "name": "Duo editions",
      "basis": "unknown",
      "sources": {
        "sb2b87daf72f0": "https://duo.com/editions-and-pricing"
      }
    },
    "duo-push-policy": {
      "name": "Duo Verified Push policy",
      "basis": "unknown",
      "sources": {
        "s4358799e0562": "https://duo.com/docs/policy#verified-push"
      }
    },
    "ssh-pam": {
      "name": "SSH and PAM MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "google-authenticator-libpam-source": {
      "name": "google-authenticator-libpam source",
      "basis": "1.11",
      "sources": {
        "s7df1bfd61fef": "https://github.com/google/google-authenticator-libpam/blob/1.11/README.md#L45-L70",
        "s9ad5ca394e81": "https://github.com/google/google-authenticator-libpam/blob/1.11/man/pam_google_authenticator.8.md#L16-L29"
      }
    },
    "google-authenticator-libpam-packages": {
      "name": "google-authenticator-libpam package records",
      "basis": "unknown",
      "sources": {
        "sf33e01264f1d": "https://packages.debian.org/trixie/libpam-google-authenticator",
        "s598691ba0908": "https://packages.ubuntu.com/noble/libpam-google-authenticator"
      }
    },
    "duo-proxy-docs": {
      "name": "Duo Authentication Proxy documentation",
      "basis": "unknown",
      "sources": {
        "s4fa84e377f72": "https://duo.com/docs/authproxy-reference"
      }
    },
    "google-workspace-docs": {
      "name": "Google Workspace 2SV documentation",
      "basis": "unknown",
      "sources": {
        "s4e673839253c": "https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification"
      }
    },
    "supabase": {
      "name": "Supabase Auth MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "access": {
      "name": "Cloudflare Access MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/",
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "mysql": {
      "name": "MySQL multifactor authentication",
      "basis": "8.0",
      "sources": {
        "sa937d1361fe1": "https://dev.mysql.com/doc/refman/8.0/en/multifactor-authentication.html"
      }
    },
    "mysql-8-4": {
      "name": "MySQL multifactor authentication",
      "basis": "8.4",
      "sources": {
        "s56ada201b676": "https://dev.mysql.com/doc/refman/8.4/en/multifactor-authentication.html"
      }
    },
    "mysql-webauthn": {
      "name": "MySQL WebAuthn authentication",
      "basis": "8.4",
      "sources": {
        "s807a77fa8872": "https://dev.mysql.com/doc/refman/8.4/en/webauthn-pluggable-authentication.html"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s1341b9dbdad1": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L58-L62",
        "s2c2f323edbd0": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57",
        "sda22c238526b": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L12",
        "s6889fae58a3a": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L26-L28",
        "s3f868ef35f58": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L96-L100",
        "s9f91c67f6011": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/manage-application-permissions.md#L91-L113",
        "s46eea4e600ea": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/manage-application-permissions.md#L40-L50",
        "s4e0a25001a1c": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L137-L147",
        "s2ee634f73c4b": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-admin-phish-resistant-mfa.md#L12-L21"
      }
    },
    "owasp-docs": {
      "name": "OWASP cheat sheets",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "se60f5c9f1c55": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L218",
        "s2940f630fb71": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L154-L155",
        "sa72b5658a19b": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L142-L143",
        "s95dac24ad579": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L40",
        "sc030e5ded4b9": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L304-L309",
        "s078b5519d6e8": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Transport_Layer_Security_Cheat_Sheet.md#L217-L221"
      }
    },
    "otp-source": {
      "name": "pquerna/otp source",
      "basis": "617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870",
      "sources": {
        "s7c4c6d57f705": "https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L27-L30",
        "s9dc96c06d6a0": "https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L15-L18"
      }
    },
    "nist": {
      "name": "NIST digital identity guidelines",
      "basis": "SP 800-63B-4",
      "sources": {
        "s4e1146860142": "https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#look-up-secrets",
        "s2a689905c161": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b-4.pdf"
      }
    },
    "authelia-source": {
      "name": "Authelia source",
      "basis": "v4.39.28",
      "sources": {
        "sfeb54a05c30d": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31",
        "s38726e46de86": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/webauthn.md#L69-L75"
      }
    },
    "pyotp-source": {
      "name": "PyOTP source",
      "basis": "cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1",
      "sources": {
        "sff126dae123b": "https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/README.rst#L4-L9"
      }
    },
    "python-qrcode-source": {
      "name": "Python qrcode source",
      "basis": "f92c007498d796e4825638b7d50c14ea51e5457a",
      "sources": {
        "s9481cd1c5c1c": "https://github.com/lincolnloop/python-qrcode/blob/f92c007498d796e4825638b7d50c14ea51e5457a/README.rst#L5-L8"
      }
    },
    "django-otp-source": {
      "name": "django-otp source",
      "basis": "88cf4970423b11f29d6840311f53378d007a3d63",
      "sources": {
        "s3b66277026d8": "https://github.com/django-otp/django-otp/blob/88cf4970423b11f29d6840311f53378d007a3d63/README.rst#L16-L28"
      }
    },
    "otplib-source": {
      "name": "otplib source",
      "basis": "c5c11be2a50fd864b587854bff6d97c5f8aa9c84",
      "sources": {
        "s1cfb4a0cb98d": "https://github.com/yeojz/otplib/blob/c5c11be2a50fd864b587854bff6d97c5f8aa9c84/README.md#L13"
      }
    },
    "node-qrcode-source": {
      "name": "Node qrcode source",
      "basis": "3848ed2c17de5bcdead487417dbf14c5dd017f8d",
      "sources": {
        "s427c06d742cf": "https://github.com/soldair/node-qrcode/blob/3848ed2c17de5bcdead487417dbf14c5dd017f8d/README.md#L2"
      }
    },
    "openssh-source": {
      "name": "OpenSSH portable source",
      "basis": "V_9_9_P2",
      "sources": {
        "sf299a4e3603a": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L197-L211",
        "s862f0df9ce84": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L2017-L2026"
      }
    },
    "duo-unix-source": {
      "name": "Duo Unix source",
      "basis": "91e3c987f256afdb166b26be777cef6e1ab2af11",
      "sources": {
        "s1ea7669082c6": "https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L44-L53",
        "sc183734b371e": "https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L60-L63"
      }
    },
    "auth0-docs": {
      "name": "Auth0 archived documentation",
      "basis": "5258d17ede3eea0ed0e330d15f8921a542564f68",
      "sources": {
        "sda6cf0f32c03": "https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12"
      }
    },
    "auth0-rolling": {
      "name": "Auth0 MFA documentation",
      "basis": "unknown",
      "sources": {
        "s22eb9266f40c": "https://auth0.com/docs/secure/multi-factor-authentication/enable-mfa"
      }
    },
    "cognito-api-source": {
      "name": "Amazon Cognito API source",
      "basis": "2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da",
      "sources": {
        "s20a38c138333": "https://github.com/aws/aws-sdk-go-v2/blob/2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da/service/cognitoidentityprovider/api_op_SetUserPoolMfaConfig.go#L67-L76"
      }
    },
    "clerk-docs": {
      "name": "Clerk documentation",
      "basis": "26ef3ace7508d46d6242c377e830a7791b0a2fdb",
      "sources": {
        "s965680da0841": "https://github.com/clerk/clerk-docs/blob/26ef3ace7508d46d6242c377e830a7791b0a2fdb/docs/guides/configure/auth-strategies/sign-up-sign-in-options.mdx#L168-L171"
      }
    },
    "supabase-docs": {
      "name": "Supabase documentation",
      "basis": "10c7379c970ae4d2f30f3158194061cf5ffb8fc5",
      "sources": {
        "sfae0cdf9b1b6": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L94-L96",
        "s4fe1e36a064b": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L200"
      }
    },
    "cf-docs": {
      "name": "Cloudflare documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s9f8bead847d2": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15",
        "s7e793d13cf31": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24"
      }
    },
    "webauthn-python": {
      "name": "py_webauthn source",
      "basis": "v3.0.1",
      "sources": {
        "s74d684e16405": "https://github.com/duo-labs/py_webauthn/blob/v3.0.1/README.md#L4-L25"
      }
    },
    "webauthn-node": {
      "name": "SimpleWebAuthn source",
      "basis": "v14.0.3",
      "sources": {
        "sc50f8c0c3a95": "https://github.com/MasterKale/SimpleWebAuthn/blob/v14.0.3/README.md#L15-L21"
      }
    },
    "webauthn-go": {
      "name": "go-webauthn source",
      "basis": "v0.18.2",
      "sources": {
        "s290e0174a612": "https://github.com/go-webauthn/webauthn/blob/v0.18.2/README.md#L10-L13"
      }
    },
    "git-docs": {
      "name": "Git documentation",
      "basis": "v2.56.0",
      "sources": {
        "s903a3c765e70": "https://github.com/git/git/blob/v2.56.0/Documentation/rev-list-options.adoc#L167-L169",
        "sc68f7234f5e1": "https://github.com/git/git/blob/v2.56.0/Documentation/diff-options.adoc#L650-L653",
        "s7d93c14a69a6": "https://github.com/git/git/blob/v2.56.0/Documentation/gitdiffcore.adoc#L251-L259",
        "sa87ce1942f01": "https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L130-L135"
      }
    },
    "grep-docs": {
      "name": "GNU grep documentation",
      "basis": "v3.12",
      "sources": {
        "sfdd7a73eab39": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n757",
        "scd528c854b46": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1150",
        "s64678780d667": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n734"
      }
    }
  },
  "claims": {
    "totp-secret": {"text": "Generate a random per-user TOTP secret; verification requires the recoverable secret rather than its hash.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-provisioning": {"text": "Provision the authenticator with an otpauth:// URI rendered as a QR code.", "components": ["uri"], "sources": ["uri:s4c73b28585c7"], "status": "REASONED"},
    "totp-storage": {"text": "Encrypt TOTP secrets at rest and exclude them from the repository.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-throttling": {"text": "Rate-limit code attempts; repeated wrong codes must hit a rate limit or lockout.", "components": ["hotp", "totp"], "sources": ["hotp:s05c8bf9b6329", "totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-replay": {"text": "Reject an already accepted code within its time step; Verify submits the same valid code twice and expects refusal on reuse.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "authelia-proxies": {"text": "Authelia integrates with nginx auth_request, Traefik forwardAuth, Caddy forward_auth from 2.5.1, HAProxy via Lua and Envoy; Apache and IIS are unsupported.", "components": ["authelia", "caddy-min"], "sources": ["authelia:s1409ac8fe3d9", "caddy-min:s1409ac8fe3d9"], "status": "REASONED"},
    "duo-free": {"text": "Duo Free covers up to 10 users with MFA and Duo Mobile as recorded in September 2026; verify current terms.", "components": ["duo"], "sources": ["duo:sb2b87daf72f0"], "status": "REASONED"},
    "webauthn-origin": {"text": "Prefer WebAuthn/passkeys and FIDO2 keys for phishing resistance: credentials are bound to the site origin.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "webauthn-verification": {"text": "Store the credential public key and sign count; require and verify UV server-side when a passkey stands alone.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "hosted-passkeys": {"text": "Guide assessment: some hosted identity providers offer passkeys or security keys; check the provider and tier before relying on availability. The linked identity-providers guide gives examples; the WebAuthn standard does not establish universal provider coverage.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "webauthn-counter": {"text": "Guide advice: treat sign count as a clone-risk signal, not an automatic clone block; WebAuthn permits zero when an authenticator does not implement a signature counter.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "verify-secret-storage": {"text": "Check that no TOTP secret appears in the repository or its history.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "DEMONSTRATED", "evidence": "a known-value search (git log --all -S over history, grep -rF outside .git over the working tree) found a planted synthetic base32 TOTP secret and three recovery codes in exposed repositories, in history after deletion and in the working tree, and found none of them in a clean control."},
    "mfa-enforcement": {"text": "Give every exposed human-facing login a second factor where viable; prefer native or IdP-enforced MFA, then an identity layer whose own or upstream policy requires MFA, app-level TOTP, then a hosted MFA service. Enrollment alone is not enforcement.", "components": ["totp", "entra-docs", "auth0-docs", "auth0-rolling", "cognito-api-source", "clerk-docs", "supabase-docs"], "sources": ["totp:s3190460e5d2d", "entra-docs:s2c2f323edbd0", "auth0-docs:sda6cf0f32c03", "auth0-rolling:s22eb9266f40c", "cognito-api-source:s20a38c138333", "clerk-docs:s965680da0841", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "push-matching": {"text": "Prefer WebAuthn/passkeys over TOTP or push, and those over email or SMS codes. TOTP and push are not phishing-resistant; push must use number matching or verified push, never bare approve/deny, to resist prompt-bombing. NIST SP 800-63B-4 sections 3.1.3, 3.2.5, 3.1.3.1 and 3.1.3.3 support the fatigue, phishing and email/PSTN rationale. For Authenticator MFA push in the MFA scenario, Entra requires number matching; its same-device Microsoft app flow can show Yes/No. Duo's Verified Duo Push uses code entry in supported flows, but its policy both lists Duo Unix v2.2.0 and later as supported and says verification has no effect in Duo Unix. The pinned pam_duo.8 documents verified_push (default no), which cannot be combined with autopush. This guide requires checking the effective push flow or choosing another factor; the cross-method preference is this guide's assessment. The cited Duo editions source covers editions and pricing only.", "components": ["webauthn", "duo", "duo-unix-source", "entra-docs", "nist", "duo-push-policy"], "sources": ["webauthn:sef2c27817118", "duo:sb2b87daf72f0", "duo-unix-source:sc183734b371e", "entra-docs:sda22c238526b", "entra-docs:s6889fae58a3a", "entra-docs:s3f868ef35f58", "nist:s2a689905c161", "duo-push-policy:s4358799e0562"], "status": "REASONED"},
    "totp-activation": {"text": "Verify one valid TOTP code before activating the factor.", "components": ["totp", "otp-source"], "sources": ["totp:s3190460e5d2d", "otp-source:s7c4c6d57f705"], "status": "REASONED"},
    "recovery-codes": {"text": "Issue single-use recovery codes and store hashes rather than the code values; Verify checks both storage and refusal on reuse.", "components": ["totp", "nist", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "nist:s4e1146860142", "owasp-docs:sa72b5658a19b"], "status": "REASONED"},
    "factor-changes": {"text": "Require re-verification of the existing factor before disabling or replacing it or minting new recovery codes, so a password-only or stolen session cannot remove MFA.", "components": ["totp", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "owasp-docs:s2940f630fb71"], "status": "REASONED"},
    "admin-factors": {"text": "Give administrators a phishing-resistant passkey or FIDO2 key wherever offered; TOTP is the floor and SMS is unacceptable for administrator accounts. OWASP advises MFA for privileged users; Microsoft Entra recommends phishing-resistant MFA for its administrator roles, and NIST SP 800-63B-4 section 2.2.2 requires it for federal staff, contractors and partners accessing federal systems and requires an AAL2 phishing-resistant option. The TOTP floor is this guide's advice; this guide requires that administrator accounts not use SMS, and OWASP advises against SMS for high-value applications.", "components": ["webauthn", "owasp-docs", "entra-docs", "nist"], "sources": ["webauthn:sef2c27817118", "owasp-docs:s95dac24ad579", "owasp-docs:sc030e5ded4b9", "entra-docs:s2ee634f73c4b", "nist:s2a689905c161"], "status": "REASONED"},
    "authelia-factors": {"text": "The body lists TOTP, WebAuthn security keys and Duo mobile push as Authelia second factors. Authelia v4.39.28 also documents passkey login, which counts as a single factor and by default prompts for a password when the request requires MFA.", "components": ["authelia", "authelia-source"], "sources": ["authelia:s1409ac8fe3d9", "authelia-source:sfeb54a05c30d", "authelia-source:s38726e46de86"], "status": "REASONED"},
    "identity-layer-factors": {"text": "The authentik validation stage rejects a response unless the login's device challenges include a compatible class; Keycloak documents OTP policy for time-based (TOTP) and counter-based generators; oauth2-proxy configures an OAuth provider and routes to upstream endpoints. Requiring MFA in each protected login flow or provider policy and testing second-factor enforcement is this guide's advice.", "components": ["authentik-source", "keycloak-source", "oauth2-proxy-source"], "sources": ["authentik-source:s18275a7072e9", "keycloak-source:s1e55f7daaa0d", "oauth2-proxy-source:sa403e3d826b4", "oauth2-proxy-source:se7a200583def"], "status": "REASONED"},
    "totp-libraries": {"text": "The body lists pyotp with qrcode and django-otp, Node otplib with qrcode, and pquerna/otp with QR generation as RFC 6238 implementation options. Each library generates and verifies RFC 6238 codes and pairs with a QR library so users can enrol a compatible TOTP authenticator app.", "components": ["totp", "pyotp-source", "python-qrcode-source", "django-otp-source", "otplib-source", "node-qrcode-source", "otp-source"], "sources": ["totp:s3190460e5d2d", "pyotp-source:sff126dae123b", "python-qrcode-source:s9481cd1c5c1c", "django-otp-source:s3b66277026d8", "otplib-source:s1cfb4a0cb98d", "node-qrcode-source:s427c06d742cf", "otp-source:s9dc96c06d6a0"], "status": "REASONED"},
    "ssh-pam-enforcement": {"text": "Make SSH PAM MFA mandatory with UsePAM yes, KbdInteractiveAuthentication yes and AuthenticationMethods publickey,keyboard-interactive:pam; :pam pins the second step to PAM and the public-key-first sequence still runs it for key-based login.", "components": ["ssh-pam", "openssh-source"], "sources": ["ssh-pam:s3190460e5d2d", "openssh-source:sf299a4e3603a", "openssh-source:s862f0df9ce84"], "status": "REASONED"},
    "ssh-nullok": {"text": "Guide advice: remove nullok after rollout so accounts without a secret file are denied by this PAM module. google-authenticator-libpam is a PAM module supporting per-account TOTP. Guide assessment: it protects only the logins whose PAM services include it. Its setup command displays a QR code when libqrencode is available. Debian trixie and Ubuntu noble list libpam-google-authenticator as 20191231-based builds; the behaviour above is cited at tag 1.11.", "components": ["google-authenticator-libpam-source", "google-authenticator-libpam-packages"], "sources": ["google-authenticator-libpam-source:s7df1bfd61fef", "google-authenticator-libpam-source:s9ad5ca394e81", "google-authenticator-libpam-packages:sf33e01264f1d", "google-authenticator-libpam-packages:s598691ba0908"], "status": "REASONED"},
    "duo-unix-failmode": {"text": "Duo Unix pam_duo adds SSH push MFA; set failmode=secure for mandatory MFA because default safe grants access when Duo is unreachable, and keep a separately controlled emergency path. The pinned pam_duo.8 also documents verified_push (default no), which cannot be combined with autopush.", "components": ["duo", "duo-unix-source"], "sources": ["duo:sb2b87daf72f0", "duo-unix-source:s1ea7669082c6", "duo-unix-source:sc183734b371e"], "status": "REASONED"},
    "supabase-assurance": {"text": "Supabase admits an aal1 session unless app and database policies require aal2; enrollment or enabling a factor is not enforcement, so inspect and test the effective policy.", "components": ["supabase", "supabase-docs"], "sources": ["supabase:s3190460e5d2d", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "google-workspace-enforcement": {"text": "Google Workspace administrators can require 2-Step Verification for selected users or groups. Guide assessment: an app using a hosted provider is protected only when its effective provider or app policy requires the second factor for that sign-in. Guide advice: inspect and test the effective policy for each protected sign-in.", "components": ["google-workspace-docs"], "sources": ["google-workspace-docs:s4e673839253c"], "status": "REASONED"},
    "duo-proxy": {"text": "Duo Authentication Proxy receives requests from devices and applications via RADIUS or LDAP and contacts Duo for secondary authentication. Guide advice: verify that each intended service sends its sign-ins through the proxy and requires the second factor.", "components": ["duo-proxy-docs"], "sources": ["duo-proxy-docs:s4fa84e377f72"], "status": "REASONED"},
    "access-mfa": {"text": "An Access emailed one-time PIN proves mailbox control only; require MFA at the connected IdP for this login or Access independent MFA with TOTP or a WebAuthn key.", "components": ["access", "cf-docs"], "sources": ["access:s3190460e5d2d", "access:sef2c27817118", "cf-docs:s9f8bead847d2", "cf-docs:s7e793d13cf31"], "status": "REASONED"},
    "webauthn-library": {"text": "When implementing WebAuthn yourself, this guide advises using a maintained WebAuthn library rather than hand-parsing attestation. The pinned py_webauthn, SimpleWebAuthn and go-webauthn READMEs document server-side WebAuthn implementation options; the recommendation to use a maintained library is this guide's assessment, not a README requirement.", "components": ["webauthn", "webauthn-python", "webauthn-node", "webauthn-go"], "sources": ["webauthn:sef2c27817118", "webauthn-python:s74d684e16405", "webauthn-node:sc50f8c0c3a95", "webauthn-go:s290e0174a612"], "status": "REASONED"},
    "webauthn-recovery": {"text": "Keep a second key or single-use recovery codes to avoid lost-key lockout; for administrators on phishing-resistant keys, prefer a second hardware key because printed codes are phishable, rate-limit recovery-code attempts, notify the account holder of recovery-code use, and alert operators on it. NIST SP 800-63B-4 section 4.1.2.1 supports two means of authentication in general; section 3.1.2 says look-up secrets are not phishing-resistant; sections 4.2.1.1 and 4.2.3 support saved recovery-code throttling and account-recovery notification to the subscriber or their designee. The administrator second-hardware-key preference and operator alert are this guide's recommendations; NIST does not require an operator alert; no pinned reference establishes the administrator-specific preference or operator alert.", "components": ["webauthn", "nist", "owasp-docs"], "sources": ["webauthn:sef2c27817118", "nist:s4e1146860142", "nist:s2a689905c161", "owasp-docs:sa72b5658a19b"], "status": "REASONED"},
    "mysql-factors": {"text": "Guide assessment: some databases offer native MFA for an interactive human login. MySQL 8.0 from 8.0.27, and MySQL 8.4, support up to three authentication factors; in MySQL 8.4 the server-side WebAuthn authentication plugin is included only in Enterprise Edition, while the client-side plugin is included in all distributions.", "components": ["mysql", "mysql-8-4", "mysql-webauthn"], "sources": ["mysql:sa937d1361fe1", "mysql-8-4:s56ada201b676", "mysql-webauthn:s807a77fa8872"], "status": "REASONED"},
    "unattended-mtls": {"text": "Guide assessment: unattended database and model-server API connections have no interactive second-factor dialogue. Guide advice: use mutual TLS client certificates as the service's possession factor and MFA on human paths through SSH, bastions and admin panels. OWASP documents that mTLS authenticates the client with a certificate and proof of its private key and requires independent server-identity validation. The possession-factor interpretation and human-path requirement are this guide's advice; the PostgreSQL and MySQL guides document client-certificate controls.", "components": ["totp", "webauthn", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "webauthn:sef2c27817118", "owasp-docs:s078b5519d6e8"], "status": "REASONED"},
    "verify-mfa-operation": {"text": "After enrollment and enforcement, a password-only attempt at an MFA-protected operation must fail and completing the second factor must allow it. Opening an aal1 session alone is not a failure when enforcement occurs at the operation.", "components": ["totp", "supabase-docs"], "sources": ["totp:s3190460e5d2d", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "verify-recovery-history": {"text": "Verify requires that no TOTP secret or recovery code appears in the repository or its history. Git --all includes refs and HEAD, while -S selects occurrence-count changes; GNU grep -rF --exclude-dir=.git recursively searches fixed strings outside .git. This known-value scan needs plaintext values; empty output with an unsubstituted placeholder proves nothing. By inference from the documented --all scope, it does not cover reflog-only or unreachable commits; -S also misses unchanged occurrence counts. Without --diff-merges (except with --first-parent), merge commits do not match -S, and -S does not search commit or tag messages. A clean result is not proof that an arbitrary repository is clean.", "components": ["totp", "git-docs", "grep-docs"], "sources": ["totp:s3190460e5d2d", "git-docs:s903a3c765e70", "git-docs:sc68f7234f5e1", "git-docs:s7d93c14a69a6", "git-docs:sa87ce1942f01", "grep-docs:sfdd7a73eab39", "grep-docs:scd528c854b46", "grep-docs:s64678780d667"], "status": "DEMONSTRATED", "evidence": "a known-value search (git log --all -S over history, grep -rF outside .git over the working tree) found a planted synthetic base32 TOTP secret and three recovery codes in exposed repositories, in history after deletion and in the working tree, and found none of them in a clean control."},
    "verify-offboarding": {"text": "Verify that a departed user's second factor, active sessions and app-level access are revoked; changing only the password is insufficient. NIST SP 800-63B-4 section 4.5 requires CSPs to promptly invalidate authenticators when the CSP determines that the subscriber no longer meets its eligibility requirements. Entra documents removal of application user and group assignments, revocation of user-consented app permissions through Graph or PowerShell, application deprovisioning and application-controlled session revocation; its identity-session revocation alone cannot revoke an application-issued session token. The deployed offboarding outcome remains a test expectation, and the cited documents do not establish it for a particular application.", "components": ["totp", "entra-docs", "owasp-docs", "nist"], "sources": ["totp:s3190460e5d2d", "entra-docs:s1341b9dbdad1", "entra-docs:s9f91c67f6011", "entra-docs:s46eea4e600ea", "entra-docs:s4e0a25001a1c", "owasp-docs:se60f5c9f1c55", "nist:s2a689905c161"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
