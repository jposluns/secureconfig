# Identity providers: hosted login and MFA for your app and your team

An identity provider runs sign-in for your team or your app's users, as a hosted service or software you run yourself. This guide helps your AI assistant choose one securely, including workforce, customer, developer and self-hosted options, which free tiers include MFA, and an allowlist check after login.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/identity-providers.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Microsoft Entra documentation (no recorded version), Authelia v4.39.28, oauth2-proxy v7.15.4, authentik source version/2026.8.3, Keycloak documentation 26.7.4, Ory Kratos v26.2.0, and Ory Hydra v26.2.0; 10 further sources are pinned to a commit and 14 carry no recorded version. Metadata reviewed 2026-10-20; documentation checked September 2026. The guide records 43 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

[authentication.md](authentication.md) says to prefer SSO or OIDC over local accounts and to enforce MFA at the identity provider. This guide names the providers, states what their free tiers include, and says who each fits. Wiring instructions live in [oidc-integration.md](oidc-integration.md); login placed in front of an app without code changes lives in [cloud-identity-proxies.md](cloud-identity-proxies.md) and [cloudflare.md](cloudflare.md).

Every stated tier and price below was read from the vendor's pricing page in September 2026 and will change; verify against the linked source before relying on it. Prices are USD list prices.

## 1. Decide which kind of identity you need

- **Workforce identity**: your team signs in with the organization's existing accounts (Google Workspace, Microsoft Entra ID, Okta). Use it for admin panels, dashboards, internal tools, and anything only staff should reach. If your organization already runs one of these, use it; do not buy a second directory.
- **Customer identity (CIAM)**: your application's own users sign up and sign in. Use a hosted provider rather than writing password storage, MFA, recovery, and rate limiting yourself.
- **Developer identity**: GitHub (or GitLab) login gates a tool for developers, optionally restricted to an organization. Often the simplest correct choice for a solo or small project.

A login proves who the person is. **It does not decide whether they may use your app.** This guide's advice is to enforce application authorization after login. After any of the providers below, your application (or the fronting layer) still checks that the identity is on an allowlist: a tenant, a hosted domain, a group, or an explicit list of users. Accepting every Google or Microsoft account as "staff" is the recurring mistake; [oidc-integration.md](oidc-integration.md) covers the check.

## 2. Workforce providers

| Provider | Free tier and MFA facts (September 2026) | Fit |
|---|---|---|
| Microsoft Entra ID | Free tier, bundled with Azure and Microsoft 365 subscriptions, includes MFA and unlimited SSO to SaaS apps. Security defaults require every user to register MFA, enforce it for administrators, and prompt other users when Microsoft judges it necessary. P1 at $7 per user per month (annual commitment) adds Conditional Access: require MFA for included users across all resources with an all-users policy that initially runs in Report-only mode and excludes emergency-access accounts; to require repeated reauthentication, also set the separate sign-in-frequency control to Every time, subject to a five-minute prompt tolerance. These controls do not establish a fresh MFA challenge on every resource access. P2 at $10 adds risk-based policies. | Any team already on Microsoft 365. |
| Google Workspace / Cloud Identity | This guide found no Google page stating Sign in with Google (OIDC) pricing (checked October 2026). Google Workspace super administrators can enforce 2-Step Verification in the Admin console for all users, or for a selected organizational unit or configuration group; this guide's assessment is that Cloud Identity uses the same Admin console setting; the cited Workspace page does not show it. Cloud Identity Free exists; its default licence count was not read from a Google page for this guide, so check the source. | Any team already on Workspace. |
| Okta Workforce Identity | Okta Verify supports push, TOTP, and FastPass. A $1,500 annual contract minimum applies and there is no free production tier. | Only when your organization already runs Okta. Not a purchase for a small project. |
| JumpCloud, OneLogin, Ping Identity | Workforce directories in the same class. Tiers not verified for this guide. | Existing enterprise estates only. |

## 3. Customer identity providers

| Provider | Free tier and MFA facts (September 2026) | Notes |
|---|---|---|
| Microsoft Entra External ID | Core features free for the first 50,000 monthly active users (MAU). SMS MFA and machine-to-machine (client credentials) authentication are billed per transaction as add-ons. | Keep the external (customer) tenant separate from the workforce tenant. |
| Google Identity Platform / Firebase Authentication | Email, password, and social sign-in are free in base Firebase Authentication. Upgrading to Authentication with Identity Platform unlocks TOTP MFA and, on the pay-as-you-go Blaze plan, a free tier of 50,000 MAU (50 SAML/OIDC MAU); the no-billing Spark plan is capped much lower, at 3,000 daily active users (2 for SAML/OIDC), so confirm which plan applies before relying on the MAU figure. SMS is billed per message. | Cloud Firestore Security Rules evaluate mobile/web client library requests after authentication; server client libraries bypass them and use IAM. Supabase table grants determine permitted operations and RLS policies determine accessible rows; keep the Supabase `service_role` server-side because it bypasses RLS: [firebase-supabase.md](firebase-supabase.md). |
| Auth0 (Okta) | Free plan: 25,000 MAU, passkeys, and unlimited social connections. **No MFA factors on Free**; MFA factors start with the paid Essentials plan, and Adaptive MFA requires an Enterprise plan plus its add-on. B2C Essentials is $35 per month for 500 MAU. | At the time of writing, Free includes passkeys, which with user verification are multifactor; what Free lacks is Auth0's separately licensed MFA policy (enforced factors and step-up). Enabling passkeys leaves password sign-in available while the database connection permits password authentication. The cited rolling passkey and archived MFA pages do not independently establish Free-tier step-up entitlement. |
| Amazon Cognito | Lite and Essentials tiers: 10,000 MAU free for direct sign-in and 50 MAU free for SAML/OIDC federation (Lite pools created on or before 10:00 a.m. Pacific Time on 22 November 2024, and qualifying new Lite pools in those existing accounts, keep a grandfathered 50,000 MAU free tier). Essentials is $0.015 per MAU beyond that and includes passkeys; Lite does not. SMS goes through SNS and is billed separately. | Pairs with Application Load Balancer authentication ([cloud-identity-proxies.md](cloud-identity-proxies.md)). |
| Clerk | Hobby plan: 50,000 monthly retained users (a user who returns at least 24 hours after signing up; not the same unit as MAU). **MFA is Pro and above** at $25 per month, or $20 billed annually. | "Free plan" does not mean MFA. |
| WorkOS AuthKit | User management free for the first 1,000,000 MAU. Enterprise SSO and Directory Sync are separate products at $125 per connection per month for the first 15 connections each. | Good app login; the per-connection fees are for selling to enterprises. |
| Supabase Auth | Free plan: 50,000 MAU with TOTP MFA included. Phone MFA is a paid add-on at $75 per month for the first project. | This guide's assessment is that TOTP enrolment alone does not enforce MFA. Require the `aal2` level in your authorization policies ([firebase-supabase.md](firebase-supabase.md)). |
| Stytch, Descope, Kinde, Frontegg, Logto, Hanko, Zitadel, Ory, SuperTokens, FusionAuth | Same class. Logto, Hanko, Zitadel, Ory, and SuperTokens are open source with hosted tiers; FusionAuth is proprietary with a free community edition. Tiers not verified for this guide. | Check the current pricing page before choosing. |

## 4. Developer identity

- **GitHub OAuth**: an OAuth app gives login for any GitHub user; restrict to members of your organization or team in the app (or with oauth2-proxy, which has a GitHub provider with org and team restrictions). GitHub Actions OIDC gives workflows short-lived cloud-provider tokens; this guide's assessment is that it is a different mechanism from human OAuth login, covered in [machine-auth.md](machine-auth.md).
- **AWS IAM Identity Center**: the free workforce directory for your team's own AWS console and CLI access. It is not a general OIDC provider for Application Load Balancer authentication; for app login on AWS pair the ALB with Cognito or an OIDC provider from section 3 ([cloud-identity-proxies.md](cloud-identity-proxies.md)).

## 5. Self-hosted identity providers

Keycloak, authentik, Zitadel, and Authelia ([mfa.md](mfa.md)) have documented OTP, authenticator validation, or OIDC capabilities. Keycloak documents OTP policy, QR-code setup, and time-based and counter-based generators; authentik's validation stage rejects a response unless the login's device challenges include a compatible class, checking code classes as one group and WebAuthn and Duo each by class. Ory Kratos provides identity and self-service login with TOTP, WebAuthn, and lookup-secret strategies; Ory Hydra is an OAuth 2.0 and OpenID Connect server that connects to an existing identity provider through a login and consent app; Ory Network is hosted. Self-hosted, these options give you OIDC and MFA without a vendor (this guide's assessment where the cited ranges do not show it). Guide advice: require MFA in each protected login or authentication flow and test that first-factor-only access is denied. Depending on severity, Keycloak may fix vulnerabilities in the current major.minor release, or address lower severity vulnerabilities or hardening in the following major.minor release. It encourages those unable to upgrade regularly to consider Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak documents an upgrade order and limits to realm export as backup; authentik publishes security advisories and documents an upgrade sequence and PostgreSQL backup; Ory says Apache 2.0 security patches are only for its latest release, and Hydra's migration guide calls for a database backup before a historical SQL migration. This guide cites no Kratos upgrade or backup procedure and no Zitadel or Authelia maintenance source. Guide advice: for a self-hosted deployment, patch, back up, and keep the identity service highly available; this guide's assessment is that a compromised or down identity provider takes every dependent app with it. For a small project a hosted tier above is usually the smaller correct change.

## 6. MFA products

- **Duo**: the Duo Free edition covers up to 10 users with MFA and the Duo Mobile app. Its Authentication Proxy speaks RADIUS and LDAP, which retrofits MFA onto VPNs and services with RADIUS support; for mandatory MFA set `failmode=secure`, since the default `safe` admits a primary-authenticated user when Duo is unreachable, and keep a separately controlled emergency path.
- **Provider-native authenticators**: Microsoft Authenticator (Entra), Okta Verify (Okta), Google prompts (Google Account sign-in on a signed-in phone); a prompt is a second factor when used in addition to the password for 2-Step Verification, and can also replace a password. Guide assessment: an RFC 6238 authenticator app can be used where the provider offers TOTP. The cited cases cover Entra OATH TOTP, Okta Google Authenticator/Custom TOTP and Google's own Authenticator app for Google Account sign-in; compatibility beyond these cases, including other providers and arbitrary apps, remains uncited.

  - Entra permits third-party OATH TOTP apps using an Entra-generated seed and programmable hardware tokens using a software setup seed; its hardware preview supports SHA-1 and SHA-256 with 30- or 60-second periods, while HOTP is unsupported. The cited page does not specify software-app algorithms or periods.

  - After an admin adds it as an accepted factor, Okta accepts Google Authenticator's six-digit TOTP as a second factor. Custom TOTP, if enabled for the org, uses per-user seeds in hardware/software tokens and a factor profile via the Factors API, with HMAC and shared-secret encoding settings matching the implementation and a configured time step. Custom TOTP supports only standard OTP tokens and one enrolment per user; the pages do not establish arbitrary app compatibility.

  - With 2-Step Verification set up, Google Account sign-in can use Google Authenticator codes, including offline generation. The cited page does not establish other authenticator apps' compatibility or specify algorithms or periods.
- **Hardware keys and passkeys**: YubiKey and other FIDO2 keys, and platform passkeys, are the phishing-resistant factor. Microsoft Entra, Auth0, Okta, Keycloak and Zitadel document passkey or WebAuthn support; check each provider's tier before relying on it, and require phishing-resistant hardware keys or platform passkeys for administrators ([mfa.md](mfa.md)). The Auth0 pricing page lists passkeys on Free (September 2026), and Okta's passkey guide uses an Integrator Free Plan org; the cited pages do not establish production-tier availability for the five providers.

## 7. Poor fits for a small project

Zscaler Private Access, HashiCorp Boundary, Ping Identity, OneLogin, and Okta as a new purchase are enterprise products with enterprise pricing and sales-led onboarding. They are listed so an assistant recognizes them when a customer already has them, not as recommendations.

## Verify

- REASONED: paired administrator MFA access, per the guide's cited Microsoft Entra security defaults and Conditional Access policy and Supabase MFA enforcement. No provider tenant, administrator test account or protected admin function is available; this item supplies no local command or configuration to execute. No login was observed. Exposed access permits a password-only or social-login-only session; fixed access denies that same admin function until MFA completes and then permits it. With only the password (or only a social login) an administrator cannot reach an admin function once MFA is required at the provider; test with a fresh session, and confirm the same admin function DOES succeed once MFA is completed, so the denial is MFA enforcement and not an unrelated failure.
- REASONED: allowed and excluded account comparison, per the guide's cited oauth2-proxy v7.15.4 GitHub organization/team restrictions and username exception, Google ID-token hosted-domain claim and Microsoft Entra tenant and application assignment documentation; group-based assignment requires Entra P1 or P2 at the time of writing. No connected application or allowed/excluded provider accounts are available; this item supplies no local command or configuration to execute. No login was observed. Exposed authorization admits a valid outside account; fixed authorization rejects it while admitting an allowed account. A valid account from outside your allowlist (a personal Gmail, a different tenant, a non-member GitHub user) is rejected after login, not admitted, while an allowed account does reach the app, so the rejection is the allowlist and not a broken login path.
- REASONED: correlation of sign-in assurance and application authorization, per the guide's cited Microsoft Entra sign-in logs and Microsoft Entra security defaults. No provider test events or application decision logs are available; this item supplies no local command or configuration to execute. No logs were inspected. Exposed decisions admit insufficient assurance or an outside account; fixed decisions require the factor and deny the outside account, corroborated with sign-in records rather than inferred from login success alone. Correlate each test against the provider's sign-in log (in Microsoft Entra this is Sign-in logs, not Audit logs, which record configuration changes) and your application's authorization decision: confirm the required factor or assurance level was met and that the outside account was denied. A log entry alone shows only that a sign-in happened, not that MFA or the allowlist was enforced.

## Sources (checked September 2026)

- Microsoft Entra pricing (Free, P1, P2, External ID free MAU): https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing
- Microsoft Entra External ID billing model: https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing
- Microsoft Entra security defaults: https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults
- Google Cloud Identity pricing: https://cloud.google.com/identity/pricing
- Google Workspace 2-Step Verification deployment (checked October 2026): https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification
- Google Account prompts (checked October 2026): https://support.google.com/accounts/answer/7026266
- Firebase pricing (Authentication and Identity Platform allowances): https://firebase.google.com/pricing
- Okta pricing: https://www.okta.com/pricing/
- Auth0 pricing: https://auth0.com/pricing
- Amazon Cognito pricing: https://aws.amazon.com/cognito/pricing/
- Clerk pricing: https://clerk.com/pricing
- WorkOS pricing: https://workos.com/pricing
- Supabase pricing: https://supabase.com/pricing
- Duo editions and pricing: https://duo.com/editions-and-pricing
- GitHub OAuth apps: https://docs.github.com/en/apps/oauth-apps
- AWS IAM Identity Center: https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html ; its OIDC service (AWS CLI and native clients): https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/Welcome.html
- Application Load Balancer user authentication (OIDC-compliant IdP or Cognito user pool): https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html
- Firebase Authentication limits (Spark-plan daily-active-user caps, distinct from the Blaze MAU free tier): https://firebase.google.com/docs/auth
- Duo Authentication Proxy reference (`failmode` default `safe`): https://duo.com/docs/authproxy-reference
- Auth0 Adaptive MFA (requires an Enterprise plan plus the add-on): https://auth0.com/docs/secure/multi-factor-authentication/adaptive-mfa
- Microsoft Entra sign-in logs (sign-ins live in Sign-in logs; Audit logs record configuration changes): https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins
- Authelia v4.39.28 second factors (TOTP, WebAuthn and Duo push; checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L23-L31
- Authelia v4.39.28 OpenID Connect provider (open beta; checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/identity-providers/openid-connect/provider.md#L25-L28
- Supabase MFA enforcement (pinned commit 10c7379c970ae4d2f30f3158194061cf5ffb8fc5, checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L96
- Supabase `aal2` authorization policy (pinned commit 10c7379c970ae4d2f30f3158194061cf5ffb8fc5, checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L196
- Okta Verify TOTP, push and FastPass (pinned commit a4f65eea34b89af7f2f543e43a74a0dfbc709cd0, checked October 2026): https://github.com/okta/okta-developer-docs/blob/a4f65eea34b89af7f2f543e43a74a0dfbc709cd0/packages/@okta/vuepress-site/docs/guides/authenticators-okta-verify/main/index.md#L29
- oauth2-proxy v7.15.4 GitHub organization/team restrictions and username exception (checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/providers/github.md#L10-L14
- Zitadel OIDC and MFA capabilities (pinned commit ab3b44cd743709649e46f7708da2f6a6a70bc227, checked October 2026): https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/README.md#L121-L123
- Zitadel MFA methods (pinned commit ab3b44cd743709649e46f7708da2f6a6a70bc227, checked October 2026): https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/apps/docs/content/guides/integrate/login-ui/mfa.mdx#L15-L19
- Microsoft Authenticator passkey, passwordless and MFA support (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/concept-authentication-authenticator-app.md#L14
- authentik validation stage and device classes (version/2026.8.3, checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L80-L108
- authentik security advisory publication (version/2026.8.3, checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/SECURITY.md#L19-L23
- authentik upgrade sequence and database backup (version/2026.8.3, checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/install-config/upgrade.mdx#L27-L31
- authentik PostgreSQL backup (version/2026.8.3, checked October 2026): https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/sys-mgmt/ops/backup-restore.mdx#L10-L18
- Keycloak OTP policy and QR-code setup (26.7.4, checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L2-L21
- Keycloak security fix releases by severity and long-term support alternative for those unable to upgrade regularly (26.7.4, checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/SECURITY.md#L44-L48
- Keycloak upgrade order (26.7.4, checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/upgrading/topics/intro.adoc#L5-L12
- Keycloak realm export backup limits (26.7.4, checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/importExport.adoc#L13-L15
- Ory Kratos identity and MFA (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/README.md#L37-L45
- Ory Kratos Apache 2.0 security patch support (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/SECURITY.md#L44-L51
- Ory Kratos deployment options and Ory Network (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/README.md#L78-L90
- Ory Kratos TOTP second-factor strategy (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/totp/strategy.go#L109-L122
- Ory Kratos WebAuthn assurance strategy (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/webauthn/strategy.go#L124-L130
- Ory Kratos lookup-secret second-factor strategy (v26.2.0, checked October 2026): https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/lookup/strategy.go#L82-L122
- Ory Hydra connects to an existing identity provider through a login and consent app; OAuth 2.0 and OpenID Connect (v26.2.0, checked October 2026): https://github.com/ory/hydra/blob/v26.2.0/README.md#L49-L72
- Ory Hydra Apache 2.0 security patch support (v26.2.0, checked October 2026): https://github.com/ory/hydra/blob/v26.2.0/SECURITY.md#L44-L51
- Ory Hydra historical migration backup instruction (v26.2.0, checked October 2026): https://github.com/ory/hydra/blob/v26.2.0/UPGRADE.md#L233-L236
- Ory Hydra deployment options and Ory Network (v26.2.0, checked October 2026): https://github.com/ory/hydra/blob/v26.2.0/README.md#L126-L136
- Auth0 passkey login and password coexistence (rolling documentation, basis unknown; checked October 2026): https://auth0.com/docs/authenticate/database-connections/passkeys#offer-passwords-and-passkeys-at-login
- Auth0 WebAuthn user verification and MFA (rolling documentation, basis unknown; checked October 2026): https://auth0.com/docs/secure/multi-factor-authentication/fido-authentication-with-webauthn#webauthn-as-multi-factor-authentication
- Auth0 archived factor enablement and Always enforcement (pinned commit 5258d17ede3eea0ed0e330d15f8921a542564f68, checked October 2026): https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12-L26
- Microsoft Entra all-users Conditional Access MFA policy (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L35-L60
- Microsoft Entra Every time sign-in frequency (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L28-L43
- Microsoft Entra sign-in frequency reauthentication (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L65-L66
- Microsoft Entra Every time five-minute prompt tolerance (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L99-L101
- Microsoft Entra ID token issuer and tenant restriction (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/id-token-claims-reference.md#L40
- Microsoft Entra enterprise application user and group assignment (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/assign-user-or-group-access-portal.md#L16-L22
- Google OpenID Connect hosted-domain claim (rolling documentation, basis unknown; checked October 2026): https://developers.google.com/identity/openid-connect/openid-connect#validatinganidtoken
- Firebase Security Rules for data access (rolling documentation, basis unknown; checked October 2026): https://firebase.google.com/docs/rules/basics#production-ready_rules
- Cloud Firestore mobile/web client request scope (rolling documentation, basis unknown; checked October 2026): https://firebase.google.com/docs/firestore/security/get-started#writing_rules
- Cloud Firestore server client library bypass and IAM (rolling documentation, basis unknown; checked October 2026): https://firebase.google.com/docs/firestore/security/get-started
- Supabase table grants and RLS policies (pinned commit 10c7379c970ae4d2f30f3158194061cf5ffb8fc5, checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/database/postgres/row-level-security.mdx#L28-L60
- GitHub Actions OIDC for workflow cloud access (pinned commit cb051611377a0d2904411e6157154e9b4953d870, checked October 2026): https://github.com/github/docs/blob/cb051611377a0d2904411e6157154e9b4953d870/content/actions/concepts/security/openid-connect.md#L19-L23
- Okta passkey authenticator policies (pinned commit a4f65eea34b89af7f2f543e43a74a0dfbc709cd0, checked October 2026): https://github.com/okta/okta-developer-docs/blob/a4f65eea34b89af7f2f543e43a74a0dfbc709cd0/packages/@okta/vuepress-site/docs/guides/custom-passkeys/main/index.md#L17-L21
- Keycloak passkey login (26.7.4, checked October 2026): https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/passkeys.adoc#L5-L8
- Zitadel passkeys (pinned commit ab3b44cd743709649e46f7708da2f6a6a70bc227, checked October 2026): https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/apps/docs/content/concepts/features/passkeys.mdx#L7-L15
- Microsoft Entra OATH TOTP software apps, seeds and hardware preview (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/concept-authentication-oath-tokens.md#L15-L27
- Okta Google Authenticator TOTP factor added by an admin (rolling documentation, basis unknown; checked October 2026): https://help.okta.com/en-us/content/topics/security/mfa/google-authenticator.htm
- Okta Custom TOTP enablement, shared secrets, factor settings and limits specific to Custom TOTP (rolling documentation, basis unknown; checked October 2026): https://help.okta.com/en-us/content/topics/security/mfa-totp-seed.htm
- Google Authenticator app codes for Google Account 2-Step Verification (rolling documentation, basis unknown; checked October 2026): https://support.google.com/accounts/answer/1066447


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- entra: Microsoft Entra documentation (unknown)
- google: Google Cloud Identity pricing (unknown)
- google-docs: Google 2-Step Verification and prompts documentation (unknown)
- okta: Okta pricing (unknown)
- firebase: Firebase documentation (unknown)
- auth0: Auth0 documentation (unknown)
- cognito: Amazon Cognito pricing (unknown)
- clerk: Clerk pricing (unknown)
- workos: WorkOS pricing (unknown)
- supabase: Supabase pricing (unknown)
- github: GitHub OAuth apps (unknown)
- aws-identity: AWS IAM Identity Center and ALB (unknown)
- duo: Duo documentation (unknown)
- authelia-source: Authelia (v4.39.28)
- supabase-docs: Supabase MFA documentation (10c7379c970ae4d2f30f3158194061cf5ffb8fc5)
- okta-docs: Okta Verify documentation (a4f65eea34b89af7f2f543e43a74a0dfbc709cd0)
- oauth2-proxy: oauth2-proxy (v7.15.4)
- zitadel-source: Zitadel documentation (ab3b44cd743709649e46f7708da2f6a6a70bc227)
- authentik-source: authentik source (version/2026.8.3)
- keycloak-source: Keycloak documentation (26.7.4)
- ory-kratos: Ory Kratos (v26.2.0)
- ory-hydra: Ory Hydra (v26.2.0)
- google-oidc-docs: Google OpenID Connect documentation (unknown)
- okta-passkey-docs: Okta passkey documentation (a4f65eea34b89af7f2f543e43a74a0dfbc709cd0)
- supabase-rls-docs: Supabase RLS documentation (10c7379c970ae4d2f30f3158194061cf5ffb8fc5)
- auth0-mfa-source: Auth0 archived MFA documentation (5258d17ede3eea0ed0e330d15f8921a542564f68)
- entra-conditional: Microsoft Entra Conditional Access documentation (231747abc59ae3d50c74e215c1cdd592eb980723)
- entra-allowlist: Microsoft Entra token and application access documentation (231747abc59ae3d50c74e215c1cdd592eb980723)
- github-docs: GitHub Actions documentation (cb051611377a0d2904411e6157154e9b4953d870)
- entra-docs: Microsoft Authenticator documentation (231747abc59ae3d50c74e215c1cdd592eb980723)
- okta-totp-docs: Okta TOTP documentation (unknown)

Claims (full source mapping in the JSON block below):

- entra-free (REASONED; entra): Entra Free includes MFA and unlimited SaaS SSO as recorded in September 2026.
- entra-defaults (REASONED; entra): Security defaults require MFA registration for everyone, enforce it for admins and prompt others when Microsoft judges necessary.
- entra-paid (REASONED; entra): September 2026 USD annual-commitment prices: P1 $7/user/month adds Conditional Access; P2 $10 adds risk-based policies. Verify current pricing.
- google-free (REASONED; google): Cloud Identity Free exists; its default license count was not checked for this guide.
- okta-commercial (REASONED; okta): Okta Workforce has a $1,500 annual contract minimum and no free production tier, as recorded in September 2026.
- external-id-free (REASONED; entra): Entra External ID core features cover the first 50,000 MAU free; keep customer and workforce tenants separate.
- external-id-addons (REASONED; entra): External ID SMS MFA and machine-to-machine client credentials are billed per transaction as add-ons.
- firebase-base (REASONED; firebase): Base Firebase Authentication provides free email, password and social sign-in; Identity Platform unlocks TOTP MFA.
- firebase-blaze (REASONED; firebase): With Identity Platform, Blaze has 50,000 free MAU and 50 SAML/OIDC MAU; SMS is billed per message.
- firebase-spark (REASONED; firebase): Spark instead caps use at 3,000 daily active users and 2 SAML/OIDC daily active users; do not confuse these with Blaze MAU allowances.
- auth0-free (REASONED; auth0): Auth0 Free has 25,000 MAU, passkeys and unlimited social connections, but no separately licensed MFA factors or enforced step-up policy.
- auth0-paid (REASONED; auth0): MFA factors start on Essentials; B2C Essentials is $35/month for 500 MAU. Adaptive MFA requires Enterprise plus its add-on.
- cognito-free (REASONED; cognito): Cognito Lite and Essentials provide 10,000 free direct-sign-in MAU and 50 free SAML/OIDC MAU.
- cognito-grandfather (REASONED; cognito): Lite pools created by 10:00 a.m. Pacific on 22 November 2024, and qualifying new Lite pools in those accounts, retain 50,000 free MAU.
- cognito-passkeys (REASONED; cognito): Cognito Essentials includes passkeys and costs $0.015/MAU beyond its allowance; Lite lacks passkeys and SNS SMS is separately billed.
- clerk-free (REASONED; clerk): Clerk Hobby covers 50,000 monthly retained users, meaning users returning at least 24 hours after signup, not MAU.
- clerk-mfa (REASONED; clerk): Clerk MFA requires Pro or above: $25/month, or $20 with annual billing, as recorded in September 2026.
- workos-users (REASONED; workos): WorkOS AuthKit user management covers the first 1,000,000 MAU free.
- workos-enterprise (REASONED; workos): WorkOS Enterprise SSO and Directory Sync are separately priced at $125/connection/month for each product's first 15 connections.
- supabase-free (REASONED; supabase): Supabase Free includes 50,000 MAU and TOTP MFA.
- supabase-phone (REASONED; supabase): Supabase phone MFA is a paid add-on at $75/month for the first project.
- github-membership (REASONED; github): GitHub OAuth login must be followed by an organization or team allowlist; OAuth login alone admits any GitHub user.
- aws-workforce (REASONED; aws-identity): IAM Identity Center is a free workforce directory for AWS console and CLI, not a general ALB OIDC provider; use Cognito or an OIDC provider for ALB app login.
- duo-free (REASONED; duo): Duo Free supports up to 10 users with MFA and Duo Mobile.
- duo-proxy (REASONED; duo): Duo Authentication Proxy supports RADIUS and LDAP for VPNs and other compatible services.
- duo-failmode (REASONED; duo): Set failmode=secure for mandatory MFA; default safe admits a primary-authenticated user when Duo is unreachable. Keep a separately controlled emergency path.
- verify-mfa (REASONED; entra, entra-conditional): REASONED; no provider tenant, administrator test account or an MFA-protected admin function is available, and no login was observed. A fresh password-only or social-login-only session must fail at the protected admin function; completing MFA must permit that same function, proving the denial was MFA enforcement.
- verify-allowlist (REASONED; github, aws-identity, google-oidc-docs, entra-allowlist): REASONED; no connected application or allowed/excluded provider accounts are available, and no login was observed. An authenticated outside account must be denied after login while an allowed account reaches the application, proving the denial was the allowlist rather than a broken login path. Google documents the hd claim; Microsoft documents tenant issuer restriction and enterprise-application assignment, with group-based assignment requiring P1 or P2 at the time of writing.
- verify-logs (REASONED; entra): REASONED; no provider test events or application decision logs are available, and no logs were inspected. Correlate provider sign-in records with application authorization decisions: the required factor or assurance level must be met and the outside account denied. Entra Sign-in logs record logins and Audit logs record configuration changes; a sign-in alone proves no enforcement.
- google-org-mfa (REASONED; google, google-docs): Google Workspace super administrators can enforce 2-Step Verification in the Admin console for all users, or for a selected organizational unit or configuration group; this guide's assessment is that Cloud Identity uses the same Admin console setting; the cited Workspace page does not show it; this guide found no Google page stating Sign in with Google (OIDC) pricing (checked October 2026). The deployment page establishes the enforcement scope; Sign in with Google (OIDC) pricing remains a source gap.
- okta-verify-factors (REASONED; okta, okta-docs): Okta Verify supports push, TOTP and FastPass.
- auth0-passkey-policy (REASONED; auth0, auth0-mfa-source): At the time of writing, Auth0 Free includes passkeys but lacks its separately licensed MFA policy for enforced factors and step-up; with user verification, WebAuthn is multifactor. Enabling passkeys leaves password sign-in available while the database connection permits password authentication. The cited rolling passkey and archived MFA pages do not independently establish Free-tier step-up entitlement.
- supabase-aal2 (REASONED; supabase-docs): Require aal2 in Supabase authorization policies. This guide's assessment is that TOTP enrollment alone does not enforce MFA.
- entra-every-signin (REASONED; entra, entra-conditional): At the time of writing, Entra P1 adds Conditional Access. An all-users, all-resources policy, initially in Report-only mode and excluding emergency-access accounts, requires MFA for included users when enforced; a separate Every time sign-in-frequency control requires repeated reauthentication, subject to a five-minute prompt tolerance. Security defaults instead prompt non-admin users when necessary. The cited passages do not establish a fresh MFA challenge on every resource access.
- application-allowlist (REASONED; github, aws-identity, google-oidc-docs, entra-allowlist): Guide advice: after any provider login, the application or fronting layer must check a tenant, hosted-domain, group or explicit-user allowlist; accepting every Google or Microsoft account as staff is not authorization. Google documents the ID-token hd claim; Microsoft documents tenant issuer restriction and enterprise-application group assignment, which requires P1 or P2 at the time of writing. No fetched Google Workspace application-access page establishes a native admin-console allowlist.
- firebase-data-policy (REASONED; firebase, supabase-rls-docs): Cloud Firestore Security Rules evaluate mobile/web client library requests after authentication; server client libraries bypass the Rules and use IAM. Supabase table grants decide permitted operations and RLS policies decide accessible rows. Supabase service_role bypasses RLS and must stay server-side.
- github-proxy-workloads (REASONED; github, oauth2-proxy, github-docs): oauth2-proxy's GitHub provider can restrict organizations and teams; GitHub Actions OIDC gives workflows short-lived cloud-provider tokens. This guide's assessment is that workload OIDC is separate from human GitHub OAuth login.
- provider-authenticators (REASONED; entra, okta, google-docs, okta-docs, entra-docs, okta-totp-docs): Microsoft Authenticator and Okta Verify are provider-native; Google Account prompts on signed-in phones can replace a password or, used with it, be a 2-Step Verification second factor. Guide assessment: an RFC 6238 app can be used where the provider offers TOTP; beyond cited Entra OATH TOTP, Okta TOTP and Google's own Authenticator cases, other providers and arbitrary apps remain uncited.
- provider-authenticators-entra (REASONED; entra-docs): Entra permits third-party OATH TOTP apps using an Entra-generated seed and programmable hardware tokens using a software setup seed; its hardware preview supports SHA-1 and SHA-256 with 30- or 60-second periods, while HOTP is unsupported. The cited page does not specify software-app algorithms or periods.
- provider-authenticators-okta (REASONED; okta-totp-docs): After an admin adds it as an accepted factor, Okta accepts Google Authenticator's six-digit TOTP as a second factor. Custom TOTP, if enabled for the org, uses per-user seeds in hardware/software tokens and a factor profile via the Factors API, with HMAC and shared-secret encoding settings matching the implementation and a configured time step. Custom TOTP supports only standard OTP tokens and one enrolment per user; the pages do not establish arbitrary app compatibility.
- provider-authenticators-google (REASONED; google-docs): With 2-Step Verification set up, Google Account sign-in can use Google Authenticator codes, including offline generation. The cited page does not establish other authenticator apps' compatibility or specify algorithms or periods.
- admin-passkeys (REASONED; entra-docs, auth0, okta-passkey-docs, keycloak-source, zitadel-source): Microsoft Entra, Auth0, Okta, Keycloak and Zitadel document passkey or WebAuthn support. Guide advice: check each provider's tier before relying on availability and require phishing-resistant hardware keys or platform passkeys for administrators. The Auth0 pricing page lists passkeys on Free (September 2026), and Okta's passkey guide uses an Integrator Free Plan org; the cited pages do not establish production-tier availability for the five providers.
- self-hosted-mfa (REASONED; entra, authelia-source, zitadel-source, authentik-source, keycloak-source, ory-kratos, ory-hydra): Keycloak, authentik, Zitadel and Authelia have documented OTP, authenticator validation or OIDC capabilities; Keycloak documents OTP policy, QR-code setup and time-based and counter-based generators; authentik's validation stage rejects a response unless the login's device challenges include a compatible class, checking code classes as one group and WebAuthn and Duo each by class. Ory Kratos provides identity and self-service login with TOTP, WebAuthn and lookup-secret strategies; Ory Hydra is an OAuth 2.0 and OpenID Connect server that connects to an existing identity provider through a login and consent app; Ory Network is hosted. Self-hosted, these options give you OIDC and MFA without a vendor (this guide's assessment where the cited ranges do not show it). Guide advice: require MFA in each protected login or authentication flow and test that first-factor-only access is denied. Depending on severity, Keycloak may fix vulnerabilities in the current major.minor release, or address lower severity vulnerabilities or hardening in the following major.minor release. It encourages those unable to upgrade regularly to consider Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak documents an upgrade order and limits to realm export as backup; authentik publishes security advisories and documents an upgrade sequence and PostgreSQL backup; Ory says Apache 2.0 security patches are only for its latest release, and Hydra's migration guide calls for a database backup before a historical SQL migration. This guide cites no Kratos upgrade or backup procedure and no Zitadel or Authelia maintenance source. Guide advice: for a self-hosted deployment, patch, back up and keep the identity service highly available; this guide's assessment is that a compromised or down identity provider takes every dependent app with it. For a small project a hosted tier above is usually the smaller correct change.

````json
{
  "schema": 1,
  "checked": "2026-10-20",
  "documentation_checked": "2026-09",
  "body_sha256": "8b4a467ebcc4075f78d6120f620c5b1ac11aac832b45f2eb74e1c1b928eeea8c",
  "components": {
    "entra": {
      "name": "Microsoft Entra documentation",
      "basis": "unknown",
      "sources": {
        "s0ee5939cfc03": "https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing",
        "s36db3cb5ed40": "https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults",
        "sca079c06e1ac": "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins",
        "s6fa089f8a7c6": "https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing"
      }
    },
    "google": {
      "name": "Google Cloud Identity pricing",
      "basis": "unknown",
      "sources": {
        "s78598c90d854": "https://cloud.google.com/identity/pricing"
      }
    },
    "google-docs": {
      "name": "Google 2-Step Verification and prompts documentation",
      "basis": "unknown",
      "sources": {
        "s4e673839253c": "https://knowledge.workspace.google.com/admin/security/deploy-2-step-verification",
        "see25fce3a7a3": "https://support.google.com/accounts/answer/7026266",
        "s2c23c2e40308": "https://support.google.com/accounts/answer/1066447"
      }
    },
    "okta": {
      "name": "Okta pricing",
      "basis": "unknown",
      "sources": {
        "sc0f6f4461955": "https://www.okta.com/pricing/"
      }
    },
    "firebase": {
      "name": "Firebase documentation",
      "basis": "unknown",
      "sources": {
        "s69c4a65e512f": "https://firebase.google.com/docs/auth",
        "s6bf1b9443202": "https://firebase.google.com/pricing",
        "s5368f5c06957": "https://firebase.google.com/docs/rules/basics#production-ready_rules",
        "sd6071548f6fe": "https://firebase.google.com/docs/firestore/security/get-started",
        "s75d5ea2efd58": "https://firebase.google.com/docs/firestore/security/get-started#writing_rules"
      }
    },
    "auth0": {
      "name": "Auth0 documentation",
      "basis": "unknown",
      "sources": {
        "sc6cc7bcbb422": "https://auth0.com/docs/secure/multi-factor-authentication/adaptive-mfa",
        "s6d62bb8ed8bf": "https://auth0.com/pricing",
        "s5794c9fb8add": "https://auth0.com/docs/authenticate/database-connections/passkeys#offer-passwords-and-passkeys-at-login",
        "s7ecf8ee3e9ba": "https://auth0.com/docs/secure/multi-factor-authentication/fido-authentication-with-webauthn#webauthn-as-multi-factor-authentication"
      }
    },
    "cognito": {
      "name": "Amazon Cognito pricing",
      "basis": "unknown",
      "sources": {
        "se7b30a68d1e3": "https://aws.amazon.com/cognito/pricing/"
      }
    },
    "clerk": {
      "name": "Clerk pricing",
      "basis": "unknown",
      "sources": {
        "s7d9e2e6a67d5": "https://clerk.com/pricing"
      }
    },
    "workos": {
      "name": "WorkOS pricing",
      "basis": "unknown",
      "sources": {
        "s339abf65cec2": "https://workos.com/pricing"
      }
    },
    "supabase": {
      "name": "Supabase pricing",
      "basis": "unknown",
      "sources": {
        "sf91e99d7738c": "https://supabase.com/pricing"
      }
    },
    "github": {
      "name": "GitHub OAuth apps",
      "basis": "unknown",
      "sources": {
        "s6b78ce27fabc": "https://docs.github.com/en/apps/oauth-apps"
      }
    },
    "aws-identity": {
      "name": "AWS IAM Identity Center and ALB",
      "basis": "unknown",
      "sources": {
        "sb1894f4f0139": "https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html",
        "s2f9843a0d8ba": "https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/Welcome.html",
        "s1b0f37773563": "https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html"
      }
    },
    "duo": {
      "name": "Duo documentation",
      "basis": "unknown",
      "sources": {
        "s4fa84e377f72": "https://duo.com/docs/authproxy-reference",
        "sb2b87daf72f0": "https://duo.com/editions-and-pricing"
      }
    },
    "authelia-source": {
      "name": "Authelia",
      "basis": "v4.39.28",
      "sources": {
        "se61b694f1b18": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L23-L31",
        "sa874f6497a22": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/identity-providers/openid-connect/provider.md#L25-L28"
      }
    },
    "supabase-docs": {
      "name": "Supabase MFA documentation",
      "basis": "10c7379c970ae4d2f30f3158194061cf5ffb8fc5",
      "sources": {
        "sf7aaaf9af229": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L96",
        "sa9ece8e2f60a": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L196"
      }
    },
    "okta-docs": {
      "name": "Okta Verify documentation",
      "basis": "a4f65eea34b89af7f2f543e43a74a0dfbc709cd0",
      "sources": {
        "sbad1704aaf36": "https://github.com/okta/okta-developer-docs/blob/a4f65eea34b89af7f2f543e43a74a0dfbc709cd0/packages/@okta/vuepress-site/docs/guides/authenticators-okta-verify/main/index.md#L29"
      }
    },
    "oauth2-proxy": {
      "name": "oauth2-proxy",
      "basis": "v7.15.4",
      "sources": {
        "s6d5e39ce93b5": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/providers/github.md#L10-L14"
      }
    },
    "zitadel-source": {
      "name": "Zitadel documentation",
      "basis": "ab3b44cd743709649e46f7708da2f6a6a70bc227",
      "sources": {
        "s729880406dc3": "https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/README.md#L121-L123",
        "sd1f3f5ccaffa": "https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/apps/docs/content/guides/integrate/login-ui/mfa.mdx#L15-L19",
        "s27d60b6057d3": "https://github.com/zitadel/zitadel/blob/ab3b44cd743709649e46f7708da2f6a6a70bc227/apps/docs/content/concepts/features/passkeys.mdx#L7-L15"
      }
    },
    "authentik-source": {
      "name": "authentik source",
      "basis": "version/2026.8.3",
      "sources": {
        "s18275a7072e9": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/authentik/stages/authenticator_validate/stage.py#L80-L108",
        "sf805a10ca50a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/SECURITY.md#L19-L23",
        "s8f5e451e02b4": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/install-config/upgrade.mdx#L27-L31",
        "s7d192a1be39a": "https://github.com/goauthentik/authentik/blob/version/2026.8.3/website/docs/sys-mgmt/ops/backup-restore.mdx#L10-L18"
      }
    },
    "keycloak-source": {
      "name": "Keycloak documentation",
      "basis": "26.7.4",
      "sources": {
        "s1e55f7daaa0d": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/otp-policies.adoc#L2-L21",
        "s676048230ec9": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/server_admin/topics/authentication/passkeys.adoc#L5-L8",
        "s25457fd213fc": "https://github.com/keycloak/keycloak/blob/26.7.4/SECURITY.md#L44-L48",
        "s83557a0c1a35": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/documentation/upgrading/topics/intro.adoc#L5-L12",
        "s8e1361985790": "https://github.com/keycloak/keycloak/blob/26.7.4/docs/guides/server/importExport.adoc#L13-L15"
      }
    },
    "ory-kratos": {
      "name": "Ory Kratos",
      "basis": "v26.2.0",
      "sources": {
        "sa1328330301d": "https://github.com/ory/kratos/blob/v26.2.0/README.md#L37-L45",
        "s0208175a002a": "https://github.com/ory/kratos/blob/v26.2.0/README.md#L78-L90",
        "s557dc3b182b7": "https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/totp/strategy.go#L109-L122",
        "sd666b62f8a70": "https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/webauthn/strategy.go#L124-L130",
        "s3d2d98558214": "https://github.com/ory/kratos/blob/v26.2.0/selfservice/strategy/lookup/strategy.go#L82-L122",
        "s3e746241fd0d": "https://github.com/ory/kratos/blob/v26.2.0/SECURITY.md#L44-L51"
      }
    },
    "ory-hydra": {
      "name": "Ory Hydra",
      "basis": "v26.2.0",
      "sources": {
        "s7735ed8cb7ad": "https://github.com/ory/hydra/blob/v26.2.0/README.md#L49-L72",
        "s9e834fe62236": "https://github.com/ory/hydra/blob/v26.2.0/README.md#L126-L136",
        "se08c1e7174df": "https://github.com/ory/hydra/blob/v26.2.0/SECURITY.md#L44-L51",
        "s58dac2f41ea0": "https://github.com/ory/hydra/blob/v26.2.0/UPGRADE.md#L233-L236"
      }
    },
    "google-oidc-docs": {
      "name": "Google OpenID Connect documentation",
      "basis": "unknown",
      "sources": {
        "sce9a29f93b69": "https://developers.google.com/identity/openid-connect/openid-connect#validatinganidtoken"
      }
    },
    "okta-passkey-docs": {
      "name": "Okta passkey documentation",
      "basis": "a4f65eea34b89af7f2f543e43a74a0dfbc709cd0",
      "sources": {
        "s567594b07020": "https://github.com/okta/okta-developer-docs/blob/a4f65eea34b89af7f2f543e43a74a0dfbc709cd0/packages/@okta/vuepress-site/docs/guides/custom-passkeys/main/index.md#L17-L21"
      }
    },
    "supabase-rls-docs": {
      "name": "Supabase RLS documentation",
      "basis": "10c7379c970ae4d2f30f3158194061cf5ffb8fc5",
      "sources": {
        "sdb0688cb20c8": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/database/postgres/row-level-security.mdx#L28-L60"
      }
    },
    "auth0-mfa-source": {
      "name": "Auth0 archived MFA documentation",
      "basis": "5258d17ede3eea0ed0e330d15f8921a542564f68",
      "sources": {
        "sf926337e245b": "https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12-L26"
      }
    },
    "entra-conditional": {
      "name": "Microsoft Entra Conditional Access documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s9bf89b3e9f66": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L35-L60",
        "sc657c943e436": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L28-L43",
        "sb1623e284d92": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L65-L66",
        "se292d57dc695": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/howto-conditional-access-session-lifetime.md#L99-L101"
      }
    },
    "entra-allowlist": {
      "name": "Microsoft Entra token and application access documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "sb49c822a58e5": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/id-token-claims-reference.md#L40",
        "sfdfe9683e4ff": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/enterprise-apps/assign-user-or-group-access-portal.md#L16-L22"
      }
    },
    "github-docs": {
      "name": "GitHub Actions documentation",
      "basis": "cb051611377a0d2904411e6157154e9b4953d870",
      "sources": {
        "s4d638483756e": "https://github.com/github/docs/blob/cb051611377a0d2904411e6157154e9b4953d870/content/actions/concepts/security/openid-connect.md#L19-L23"
      }
    },
    "entra-docs": {
      "name": "Microsoft Authenticator documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "sa319646e1a02": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/concept-authentication-authenticator-app.md#L14",
        "s4d3f93f998dd": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/concept-authentication-oath-tokens.md#L15-L27"
      }
    },
    "okta-totp-docs": {
      "name": "Okta TOTP documentation",
      "basis": "unknown",
      "sources": {
        "s90c65e21037a": "https://help.okta.com/en-us/content/topics/security/mfa/google-authenticator.htm",
        "sd0899fd16083": "https://help.okta.com/en-us/content/topics/security/mfa-totp-seed.htm"
      }
    }
  },
  "claims": {
    "entra-free": {"text": "Entra Free includes MFA and unlimited SaaS SSO as recorded in September 2026.", "components": ["entra"], "sources": ["entra:s6fa089f8a7c6"], "status": "REASONED"},
    "entra-defaults": {"text": "Security defaults require MFA registration for everyone, enforce it for admins and prompt others when Microsoft judges necessary.", "components": ["entra"], "sources": ["entra:s36db3cb5ed40"], "status": "REASONED"},
    "entra-paid": {"text": "September 2026 USD annual-commitment prices: P1 $7/user/month adds Conditional Access; P2 $10 adds risk-based policies. Verify current pricing.", "components": ["entra"], "sources": ["entra:s6fa089f8a7c6"], "status": "REASONED"},
    "google-free": {"text": "Cloud Identity Free exists; its default license count was not checked for this guide.", "components": ["google"], "sources": ["google:s78598c90d854"], "status": "REASONED"},
    "okta-commercial": {"text": "Okta Workforce has a $1,500 annual contract minimum and no free production tier, as recorded in September 2026.", "components": ["okta"], "sources": ["okta:sc0f6f4461955"], "status": "REASONED"},
    "external-id-free": {"text": "Entra External ID core features cover the first 50,000 MAU free; keep customer and workforce tenants separate.", "components": ["entra"], "sources": ["entra:s6fa089f8a7c6", "entra:s0ee5939cfc03"], "status": "REASONED"},
    "external-id-addons": {"text": "External ID SMS MFA and machine-to-machine client credentials are billed per transaction as add-ons.", "components": ["entra"], "sources": ["entra:s0ee5939cfc03"], "status": "REASONED"},
    "firebase-base": {"text": "Base Firebase Authentication provides free email, password and social sign-in; Identity Platform unlocks TOTP MFA.", "components": ["firebase"], "sources": ["firebase:s69c4a65e512f", "firebase:s6bf1b9443202"], "status": "REASONED"},
    "firebase-blaze": {"text": "With Identity Platform, Blaze has 50,000 free MAU and 50 SAML/OIDC MAU; SMS is billed per message.", "components": ["firebase"], "sources": ["firebase:s6bf1b9443202"], "status": "REASONED"},
    "firebase-spark": {"text": "Spark instead caps use at 3,000 daily active users and 2 SAML/OIDC daily active users; do not confuse these with Blaze MAU allowances.", "components": ["firebase"], "sources": ["firebase:s69c4a65e512f"], "status": "REASONED"},
    "auth0-free": {"text": "Auth0 Free has 25,000 MAU, passkeys and unlimited social connections, but no separately licensed MFA factors or enforced step-up policy.", "components": ["auth0"], "sources": ["auth0:s6d62bb8ed8bf"], "status": "REASONED"},
    "auth0-paid": {"text": "MFA factors start on Essentials; B2C Essentials is $35/month for 500 MAU. Adaptive MFA requires Enterprise plus its add-on.", "components": ["auth0"], "sources": ["auth0:s6d62bb8ed8bf", "auth0:sc6cc7bcbb422"], "status": "REASONED"},
    "cognito-free": {"text": "Cognito Lite and Essentials provide 10,000 free direct-sign-in MAU and 50 free SAML/OIDC MAU.", "components": ["cognito"], "sources": ["cognito:se7b30a68d1e3"], "status": "REASONED"},
    "cognito-grandfather": {"text": "Lite pools created by 10:00 a.m. Pacific on 22 November 2024, and qualifying new Lite pools in those accounts, retain 50,000 free MAU.", "components": ["cognito"], "sources": ["cognito:se7b30a68d1e3"], "status": "REASONED"},
    "cognito-passkeys": {"text": "Cognito Essentials includes passkeys and costs $0.015/MAU beyond its allowance; Lite lacks passkeys and SNS SMS is separately billed.", "components": ["cognito"], "sources": ["cognito:se7b30a68d1e3"], "status": "REASONED"},
    "clerk-free": {"text": "Clerk Hobby covers 50,000 monthly retained users, meaning users returning at least 24 hours after signup, not MAU.", "components": ["clerk"], "sources": ["clerk:s7d9e2e6a67d5"], "status": "REASONED"},
    "clerk-mfa": {"text": "Clerk MFA requires Pro or above: $25/month, or $20 with annual billing, as recorded in September 2026.", "components": ["clerk"], "sources": ["clerk:s7d9e2e6a67d5"], "status": "REASONED"},
    "workos-users": {"text": "WorkOS AuthKit user management covers the first 1,000,000 MAU free.", "components": ["workos"], "sources": ["workos:s339abf65cec2"], "status": "REASONED"},
    "workos-enterprise": {"text": "WorkOS Enterprise SSO and Directory Sync are separately priced at $125/connection/month for each product's first 15 connections.", "components": ["workos"], "sources": ["workos:s339abf65cec2"], "status": "REASONED"},
    "supabase-free": {"text": "Supabase Free includes 50,000 MAU and TOTP MFA.", "components": ["supabase"], "sources": ["supabase:sf91e99d7738c"], "status": "REASONED"},
    "supabase-phone": {"text": "Supabase phone MFA is a paid add-on at $75/month for the first project.", "components": ["supabase"], "sources": ["supabase:sf91e99d7738c"], "status": "REASONED"},
    "github-membership": {"text": "GitHub OAuth login must be followed by an organization or team allowlist; OAuth login alone admits any GitHub user.", "components": ["github"], "sources": ["github:s6b78ce27fabc"], "status": "REASONED"},
    "aws-workforce": {"text": "IAM Identity Center is a free workforce directory for AWS console and CLI, not a general ALB OIDC provider; use Cognito or an OIDC provider for ALB app login.", "components": ["aws-identity"], "sources": ["aws-identity:sb1894f4f0139", "aws-identity:s2f9843a0d8ba", "aws-identity:s1b0f37773563"], "status": "REASONED"},
    "duo-free": {"text": "Duo Free supports up to 10 users with MFA and Duo Mobile.", "components": ["duo"], "sources": ["duo:sb2b87daf72f0"], "status": "REASONED"},
    "duo-proxy": {"text": "Duo Authentication Proxy supports RADIUS and LDAP for VPNs and other compatible services.", "components": ["duo"], "sources": ["duo:s4fa84e377f72"], "status": "REASONED"},
    "duo-failmode": {"text": "Set failmode=secure for mandatory MFA; default safe admits a primary-authenticated user when Duo is unreachable. Keep a separately controlled emergency path.", "components": ["duo"], "sources": ["duo:s4fa84e377f72"], "status": "REASONED"},
    "verify-mfa": {"text": "REASONED; no provider tenant, administrator test account or an MFA-protected admin function is available, and no login was observed. A fresh password-only or social-login-only session must fail at the protected admin function; completing MFA must permit that same function, proving the denial was MFA enforcement.", "components": ["entra", "entra-conditional"], "sources": ["entra:s36db3cb5ed40", "entra-conditional:s9bf89b3e9f66"], "status": "REASONED"},
    "verify-allowlist": {"text": "REASONED; no connected application or allowed/excluded provider accounts are available, and no login was observed. An authenticated outside account must be denied after login while an allowed account reaches the application, proving the denial was the allowlist rather than a broken login path. Google documents the hd claim; Microsoft documents tenant issuer restriction and enterprise-application assignment, with group-based assignment requiring P1 or P2 at the time of writing.", "components": ["github", "aws-identity", "google-oidc-docs", "entra-allowlist"], "sources": ["github:s6b78ce27fabc", "aws-identity:sb1894f4f0139", "google-oidc-docs:sce9a29f93b69", "entra-allowlist:sb49c822a58e5", "entra-allowlist:sfdfe9683e4ff"], "status": "REASONED"},
    "verify-logs": {"text": "REASONED; no provider test events or application decision logs are available, and no logs were inspected. Correlate provider sign-in records with application authorization decisions: the required factor or assurance level must be met and the outside account denied. Entra Sign-in logs record logins and Audit logs record configuration changes; a sign-in alone proves no enforcement.", "components": ["entra"], "sources": ["entra:sca079c06e1ac"], "status": "REASONED"},
    "google-org-mfa": {"text": "Google Workspace super administrators can enforce 2-Step Verification in the Admin console for all users, or for a selected organizational unit or configuration group; this guide's assessment is that Cloud Identity uses the same Admin console setting; the cited Workspace page does not show it; this guide found no Google page stating Sign in with Google (OIDC) pricing (checked October 2026). The deployment page establishes the enforcement scope; Sign in with Google (OIDC) pricing remains a source gap.", "components": ["google", "google-docs"], "sources": ["google:s78598c90d854", "google-docs:s4e673839253c"], "status": "REASONED"},
    "okta-verify-factors": {"text": "Okta Verify supports push, TOTP and FastPass.", "components": ["okta", "okta-docs"], "sources": ["okta:sc0f6f4461955", "okta-docs:sbad1704aaf36"], "status": "REASONED"},
    "auth0-passkey-policy": {"text": "At the time of writing, Auth0 Free includes passkeys but lacks its separately licensed MFA policy for enforced factors and step-up; with user verification, WebAuthn is multifactor. Enabling passkeys leaves password sign-in available while the database connection permits password authentication. The cited rolling passkey and archived MFA pages do not independently establish Free-tier step-up entitlement.", "components": ["auth0", "auth0-mfa-source"], "sources": ["auth0:s6d62bb8ed8bf", "auth0:s5794c9fb8add", "auth0:s7ecf8ee3e9ba", "auth0-mfa-source:sf926337e245b"], "status": "REASONED"},
    "supabase-aal2": {"text": "Require aal2 in Supabase authorization policies. This guide's assessment is that TOTP enrollment alone does not enforce MFA.", "components": ["supabase-docs"], "sources": ["supabase-docs:sf7aaaf9af229", "supabase-docs:sa9ece8e2f60a"], "status": "REASONED"},
    "entra-every-signin": {"text": "At the time of writing, Entra P1 adds Conditional Access. An all-users, all-resources policy, initially in Report-only mode and excluding emergency-access accounts, requires MFA for included users when enforced; a separate Every time sign-in-frequency control requires repeated reauthentication, subject to a five-minute prompt tolerance. Security defaults instead prompt non-admin users when necessary. The cited passages do not establish a fresh MFA challenge on every resource access.", "components": ["entra", "entra-conditional"], "sources": ["entra:s6fa089f8a7c6", "entra:s36db3cb5ed40", "entra-conditional:s9bf89b3e9f66", "entra-conditional:sc657c943e436", "entra-conditional:sb1623e284d92", "entra-conditional:se292d57dc695"], "status": "REASONED"},
    "application-allowlist": {"text": "Guide advice: after any provider login, the application or fronting layer must check a tenant, hosted-domain, group or explicit-user allowlist; accepting every Google or Microsoft account as staff is not authorization. Google documents the ID-token hd claim; Microsoft documents tenant issuer restriction and enterprise-application group assignment, which requires P1 or P2 at the time of writing. No fetched Google Workspace application-access page establishes a native admin-console allowlist.", "components": ["github", "aws-identity", "google-oidc-docs", "entra-allowlist"], "sources": ["github:s6b78ce27fabc", "aws-identity:sb1894f4f0139", "google-oidc-docs:sce9a29f93b69", "entra-allowlist:sb49c822a58e5", "entra-allowlist:sfdfe9683e4ff"], "status": "REASONED"},
    "firebase-data-policy": {"text": "Cloud Firestore Security Rules evaluate mobile/web client library requests after authentication; server client libraries bypass the Rules and use IAM. Supabase table grants decide permitted operations and RLS policies decide accessible rows. Supabase service_role bypasses RLS and must stay server-side.", "components": ["firebase", "supabase-rls-docs"], "sources": ["firebase:s5368f5c06957", "firebase:sd6071548f6fe", "firebase:s75d5ea2efd58", "supabase-rls-docs:sdb0688cb20c8"], "status": "REASONED"},
    "github-proxy-workloads": {"text": "oauth2-proxy's GitHub provider can restrict organizations and teams; GitHub Actions OIDC gives workflows short-lived cloud-provider tokens. This guide's assessment is that workload OIDC is separate from human GitHub OAuth login.", "components": ["github", "oauth2-proxy", "github-docs"], "sources": ["github:s6b78ce27fabc", "oauth2-proxy:s6d5e39ce93b5", "github-docs:s4d638483756e"], "status": "REASONED"},
    "provider-authenticators": {"text": "Microsoft Authenticator and Okta Verify are provider-native; Google Account prompts on signed-in phones can replace a password or, used with it, be a 2-Step Verification second factor. Guide assessment: an RFC 6238 app can be used where the provider offers TOTP; beyond cited Entra OATH TOTP, Okta TOTP and Google's own Authenticator cases, other providers and arbitrary apps remain uncited.", "components": ["entra", "okta", "google-docs", "okta-docs", "entra-docs", "okta-totp-docs"], "sources": ["entra:s36db3cb5ed40", "okta:sc0f6f4461955", "google-docs:see25fce3a7a3", "okta-docs:sbad1704aaf36", "entra-docs:sa319646e1a02", "entra-docs:s4d3f93f998dd", "okta-totp-docs:s90c65e21037a", "okta-totp-docs:sd0899fd16083", "google-docs:s2c23c2e40308"], "status": "REASONED"},
    "provider-authenticators-entra": {"text": "Entra permits third-party OATH TOTP apps using an Entra-generated seed and programmable hardware tokens using a software setup seed; its hardware preview supports SHA-1 and SHA-256 with 30- or 60-second periods, while HOTP is unsupported. The cited page does not specify software-app algorithms or periods.", "components": ["entra-docs"], "sources": ["entra-docs:s4d3f93f998dd"], "status": "REASONED"},
    "provider-authenticators-okta": {"text": "After an admin adds it as an accepted factor, Okta accepts Google Authenticator's six-digit TOTP as a second factor. Custom TOTP, if enabled for the org, uses per-user seeds in hardware/software tokens and a factor profile via the Factors API, with HMAC and shared-secret encoding settings matching the implementation and a configured time step. Custom TOTP supports only standard OTP tokens and one enrolment per user; the pages do not establish arbitrary app compatibility.", "components": ["okta-totp-docs"], "sources": ["okta-totp-docs:s90c65e21037a", "okta-totp-docs:sd0899fd16083"], "status": "REASONED"},
    "provider-authenticators-google": {"text": "With 2-Step Verification set up, Google Account sign-in can use Google Authenticator codes, including offline generation. The cited page does not establish other authenticator apps' compatibility or specify algorithms or periods.", "components": ["google-docs"], "sources": ["google-docs:s2c23c2e40308"], "status": "REASONED"},
    "admin-passkeys": {"text": "Microsoft Entra, Auth0, Okta, Keycloak and Zitadel document passkey or WebAuthn support. Guide advice: check each provider's tier before relying on availability and require phishing-resistant hardware keys or platform passkeys for administrators. The Auth0 pricing page lists passkeys on Free (September 2026), and Okta's passkey guide uses an Integrator Free Plan org; the cited pages do not establish production-tier availability for the five providers.", "components": ["entra-docs", "auth0", "okta-passkey-docs", "keycloak-source", "zitadel-source"], "sources": ["entra-docs:sa319646e1a02", "auth0:s6d62bb8ed8bf", "auth0:s5794c9fb8add", "okta-passkey-docs:s567594b07020", "keycloak-source:s676048230ec9", "zitadel-source:s27d60b6057d3"], "status": "REASONED"},
    "self-hosted-mfa": {"text": "Keycloak, authentik, Zitadel and Authelia have documented OTP, authenticator validation or OIDC capabilities; Keycloak documents OTP policy, QR-code setup and time-based and counter-based generators; authentik's validation stage rejects a response unless the login's device challenges include a compatible class, checking code classes as one group and WebAuthn and Duo each by class. Ory Kratos provides identity and self-service login with TOTP, WebAuthn and lookup-secret strategies; Ory Hydra is an OAuth 2.0 and OpenID Connect server that connects to an existing identity provider through a login and consent app; Ory Network is hosted. Self-hosted, these options give you OIDC and MFA without a vendor (this guide's assessment where the cited ranges do not show it). Guide advice: require MFA in each protected login or authentication flow and test that first-factor-only access is denied. Depending on severity, Keycloak may fix vulnerabilities in the current major.minor release, or address lower severity vulnerabilities or hardening in the following major.minor release. It encourages those unable to upgrade regularly to consider Red Hat build of Keycloak, which offers long-term support for specific versions. Keycloak documents an upgrade order and limits to realm export as backup; authentik publishes security advisories and documents an upgrade sequence and PostgreSQL backup; Ory says Apache 2.0 security patches are only for its latest release, and Hydra's migration guide calls for a database backup before a historical SQL migration. This guide cites no Kratos upgrade or backup procedure and no Zitadel or Authelia maintenance source. Guide advice: for a self-hosted deployment, patch, back up and keep the identity service highly available; this guide's assessment is that a compromised or down identity provider takes every dependent app with it. For a small project a hosted tier above is usually the smaller correct change.", "components": ["entra", "authelia-source", "zitadel-source", "authentik-source", "keycloak-source", "ory-kratos", "ory-hydra"], "sources": ["entra:s36db3cb5ed40", "authelia-source:se61b694f1b18", "authelia-source:sa874f6497a22", "zitadel-source:s729880406dc3", "authentik-source:sf805a10ca50a", "authentik-source:s8f5e451e02b4", "authentik-source:s7d192a1be39a", "zitadel-source:sd1f3f5ccaffa", "authentik-source:s18275a7072e9", "keycloak-source:s1e55f7daaa0d", "keycloak-source:s25457fd213fc", "keycloak-source:s83557a0c1a35", "keycloak-source:s8e1361985790", "ory-kratos:sa1328330301d", "ory-kratos:s3e746241fd0d", "ory-kratos:s0208175a002a", "ory-kratos:s557dc3b182b7", "ory-kratos:sd666b62f8a70", "ory-kratos:s3d2d98558214", "ory-hydra:s7735ed8cb7ad", "ory-hydra:se08c1e7174df", "ory-hydra:s58dac2f41ea0", "ory-hydra:s9e834fe62236"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
