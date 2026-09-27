---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "95df257640a05fcefeeff0c6c197d003381716a71cfc62c2e840304653459bb5",
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
        "s6bf1b9443202": "https://firebase.google.com/pricing"
      }
    },
    "auth0": {
      "name": "Auth0 documentation",
      "basis": "unknown",
      "sources": {
        "sc6cc7bcbb422": "https://auth0.com/docs/secure/multi-factor-authentication/adaptive-mfa",
        "s6d62bb8ed8bf": "https://auth0.com/pricing"
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
    "verify-mfa": {"text": "A fresh password-only or social-login-only session must fail at an MFA-protected admin function; completing MFA must permit that same function.", "components": ["entra"], "sources": ["entra:s36db3cb5ed40"], "status": "REASONED"},
    "verify-allowlist": {"text": "An authenticated outside account must be denied while an allowed account reaches the application.", "components": ["github", "aws-identity"], "sources": ["github:s6b78ce27fabc", "aws-identity:sb1894f4f0139"], "status": "REASONED"},
    "verify-logs": {"text": "Correlate provider sign-in records with application authorization decisions; Entra Sign-in logs record logins and Audit logs record configuration changes. A sign-in alone proves no enforcement.", "components": ["entra"], "sources": ["entra:sca079c06e1ac"], "status": "REASONED"}
  }
}
---
# Identity providers: hosted login and MFA for your app and your team

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| entra-free: Entra Free includes MFA and unlimited SaaS SSO as recorded in September 2026. | Microsoft Entra documentation unknown | REASONED |
| entra-defaults: Security defaults require MFA registration for everyone, enforce it for admins and prompt others when Microsoft judges necessary. | Microsoft Entra documentation unknown | REASONED |
| entra-paid: September 2026 USD annual-commitment prices: P1 $7/user/month adds Conditional Access; P2 $10 adds risk-based policies. Verify current pricing. | Microsoft Entra documentation unknown | REASONED |
| google-free: Cloud Identity Free exists; its default license count was not checked for this guide. | Google Cloud Identity pricing unknown | REASONED |
| okta-commercial: Okta Workforce has a $1,500 annual contract minimum and no free production tier, as recorded in September 2026. | Okta pricing unknown | REASONED |
| external-id-free: Entra External ID core features cover the first 50,000 MAU free; keep customer and workforce tenants separate. | Microsoft Entra documentation unknown | REASONED |
| external-id-addons: External ID SMS MFA and machine-to-machine client credentials are billed per transaction as add-ons. | Microsoft Entra documentation unknown | REASONED |
| firebase-base: Base Firebase Authentication provides free email, password and social sign-in; Identity Platform unlocks TOTP MFA. | Firebase documentation unknown | REASONED |
| firebase-blaze: With Identity Platform, Blaze has 50,000 free MAU and 50 SAML/OIDC MAU; SMS is billed per message. | Firebase documentation unknown | REASONED |
| firebase-spark: Spark instead caps use at 3,000 daily active users and 2 SAML/OIDC daily active users; do not confuse these with Blaze MAU allowances. | Firebase documentation unknown | REASONED |
| auth0-free: Auth0 Free has 25,000 MAU, passkeys and unlimited social connections, but no separately licensed MFA factors or enforced step-up policy. | Auth0 documentation unknown | REASONED |
| auth0-paid: MFA factors start on Essentials; B2C Essentials is $35/month for 500 MAU. Adaptive MFA requires Enterprise plus its add-on. | Auth0 documentation unknown | REASONED |
| cognito-free: Cognito Lite and Essentials provide 10,000 free direct-sign-in MAU and 50 free SAML/OIDC MAU. | Amazon Cognito pricing unknown | REASONED |
| cognito-grandfather: Lite pools created by 10:00 a.m. Pacific on 22 November 2024, and qualifying new Lite pools in those accounts, retain 50,000 free MAU. | Amazon Cognito pricing unknown | REASONED |
| cognito-passkeys: Cognito Essentials includes passkeys and costs $0.015/MAU beyond its allowance; Lite lacks passkeys and SNS SMS is separately billed. | Amazon Cognito pricing unknown | REASONED |
| clerk-free: Clerk Hobby covers 50,000 monthly retained users, meaning users returning at least 24 hours after signup, not MAU. | Clerk pricing unknown | REASONED |
| clerk-mfa: Clerk MFA requires Pro or above: $25/month, or $20 with annual billing, as recorded in September 2026. | Clerk pricing unknown | REASONED |
| workos-users: WorkOS AuthKit user management covers the first 1,000,000 MAU free. | WorkOS pricing unknown | REASONED |
| workos-enterprise: WorkOS Enterprise SSO and Directory Sync are separately priced at $125/connection/month for each product's first 15 connections. | WorkOS pricing unknown | REASONED |
| supabase-free: Supabase Free includes 50,000 MAU and TOTP MFA. | Supabase pricing unknown | REASONED |
| supabase-phone: Supabase phone MFA is a paid add-on at $75/month for the first project. | Supabase pricing unknown | REASONED |
| github-membership: GitHub OAuth login must be followed by an organization or team allowlist; OAuth login alone admits any GitHub user. | GitHub OAuth apps unknown | REASONED |
| aws-workforce: IAM Identity Center is a free workforce directory for AWS console and CLI, not a general ALB OIDC provider; use Cognito or an OIDC provider for ALB app login. | AWS IAM Identity Center and ALB unknown | REASONED |
| duo-free: Duo Free supports up to 10 users with MFA and Duo Mobile. | Duo documentation unknown | REASONED |
| duo-proxy: Duo Authentication Proxy supports RADIUS and LDAP for VPNs and other compatible services. | Duo documentation unknown | REASONED |
| duo-failmode: Set failmode=secure for mandatory MFA; default safe admits a primary-authenticated user when Duo is unreachable. Keep a separately controlled emergency path. | Duo documentation unknown | REASONED |
| verify-mfa: A fresh password-only or social-login-only session must fail at an MFA-protected admin function; completing MFA must permit that same function. | Microsoft Entra documentation unknown | REASONED |
| verify-allowlist: An authenticated outside account must be denied while an allowed account reaches the application. | GitHub OAuth apps unknown; AWS IAM Identity Center and ALB unknown | REASONED |
| verify-logs: Correlate provider sign-in records with application authorization decisions; Entra Sign-in logs record logins and Audit logs record configuration changes. A sign-in alone proves no enforcement. | Microsoft Entra documentation unknown | REASONED |
<!-- version-basis:end -->

[authentication.md](authentication.md) says to prefer SSO or OIDC over local accounts and to enforce MFA at the identity provider. This guide names the providers, states what their free tiers include, and says who each fits. Wiring instructions live in [oidc-integration.md](oidc-integration.md); login placed in front of an app without code changes lives in [cloud-identity-proxies.md](cloud-identity-proxies.md) and [cloudflare.md](cloudflare.md).

Every tier and price below was read from the vendor's pricing page in September 2026 and will change; verify against the linked source before relying on it. Prices are USD list prices.

## 1. Decide which kind of identity you need

- **Workforce identity**: your team signs in with the organization's existing accounts (Google Workspace, Microsoft Entra ID, Okta). Use it for admin panels, dashboards, internal tools, and anything only staff should reach. If your organization already runs one of these, use it; do not buy a second directory.
- **Customer identity (CIAM)**: your application's own users sign up and sign in. Use a hosted provider rather than writing password storage, MFA, recovery, and rate limiting yourself.
- **Developer identity**: GitHub (or GitLab) login gates a tool for developers, optionally restricted to an organization. Often the simplest correct choice for a solo or small project.

A login proves who the person is. **It does not decide whether they may use your app.** After any of the providers below, your application (or the fronting layer) still checks that the identity is on an allowlist: a tenant, a hosted domain, a group, or an explicit list of users. Accepting every Google or Microsoft account as "staff" is the recurring mistake; [oidc-integration.md](oidc-integration.md) covers the check.

## 2. Workforce providers

| Provider | Free tier and MFA facts (September 2026) | Fit |
|---|---|---|
| Microsoft Entra ID | Free tier, bundled with Azure and Microsoft 365 subscriptions, includes MFA and unlimited SSO to SaaS apps. Security defaults require every user to register MFA, enforce it for administrators, and prompt other users when Microsoft judges it necessary. P1 at $7 per user per month (annual commitment) adds Conditional Access, which is how you require MFA for everyone on every sign-in; P2 at $10 adds risk-based policies. | Any team already on Microsoft 365. |
| Google Workspace / Cloud Identity | Sign in with Google (OIDC) costs nothing per app. Enforcing 2-Step Verification for the whole organization is an admin-console setting in Workspace or Cloud Identity. Cloud Identity Free exists; its default licence count was not read from a Google page for this guide, so check the source. | Any team already on Workspace. |
| Okta Workforce Identity | Okta Verify supports push, TOTP, and FastPass. A $1,500 annual contract minimum applies and there is no free production tier. | Only when your organization already runs Okta. Not a purchase for a small project. |
| JumpCloud, OneLogin, Ping Identity | Workforce directories in the same class. Tiers not verified for this guide. | Existing enterprise estates only. |

## 3. Customer identity providers

| Provider | Free tier and MFA facts (September 2026) | Notes |
|---|---|---|
| Microsoft Entra External ID | Core features free for the first 50,000 monthly active users (MAU). SMS MFA and machine-to-machine (client credentials) authentication are billed per transaction as add-ons. | Keep the external (customer) tenant separate from the workforce tenant. |
| Google Identity Platform / Firebase Authentication | Email, password, and social sign-in are free in base Firebase Authentication. Upgrading to Authentication with Identity Platform unlocks TOTP MFA and, on the pay-as-you-go Blaze plan, a free tier of 50,000 MAU (50 SAML/OIDC MAU); the no-billing Spark plan is capped much lower, at 3,000 daily active users (2 for SAML/OIDC), so confirm which plan applies before relying on the MAU figure. SMS is billed per message. | Rules and RLS still decide data access: [firebase-supabase.md](firebase-supabase.md). |
| Auth0 (Okta) | Free plan: 25,000 MAU, passkeys, and unlimited social connections. **No MFA factors on Free**; MFA factors start with the paid Essentials plan, and Adaptive MFA requires an Enterprise plan plus its add-on. B2C Essentials is $35 per month for 500 MAU. | Free includes passkeys, which with verified user verification are themselves phishing-resistant multifactor; what Free lacks is Auth0's separately licensed MFA policy (enforced factors and step-up), and enabling passkeys does not disable password sign-in. |
| Amazon Cognito | Lite and Essentials tiers: 10,000 MAU free for direct sign-in and 50 MAU free for SAML/OIDC federation (Lite pools created on or before 10:00 a.m. Pacific Time on 22 November 2024, and qualifying new Lite pools in those existing accounts, keep a grandfathered 50,000 MAU free tier). Essentials is $0.015 per MAU beyond that and includes passkeys; Lite does not. SMS goes through SNS and is billed separately. | Pairs with Application Load Balancer authentication ([cloud-identity-proxies.md](cloud-identity-proxies.md)). |
| Clerk | Hobby plan: 50,000 monthly retained users (a user who returns at least 24 hours after signing up; not the same unit as MAU). **MFA is Pro and above** at $25 per month, or $20 billed annually. | "Free plan" does not mean MFA. |
| WorkOS AuthKit | User management free for the first 1,000,000 MAU. Enterprise SSO and Directory Sync are separate products at $125 per connection per month for the first 15 connections each. | Good app login; the per-connection fees are for selling to enterprises. |
| Supabase Auth | Free plan: 50,000 MAU with TOTP MFA included. Phone MFA is a paid add-on at $75 per month for the first project. | Enrolment is not enforcement: require the `aal2` level in your policies ([firebase-supabase.md](firebase-supabase.md)). |
| Stytch, Descope, Kinde, Frontegg, Logto, Hanko, Zitadel, Ory, SuperTokens, FusionAuth | Same class. Logto, Hanko, Zitadel, Ory, and SuperTokens are open source with hosted tiers; FusionAuth is proprietary with a free community edition. Tiers not verified for this guide. | Check the current pricing page before choosing. |

## 4. Developer identity

- **GitHub OAuth**: an OAuth app gives login for any GitHub user; restrict to members of your organization or team in the app (or with oauth2-proxy, which has a GitHub provider with org and team restrictions). GitHub Actions OIDC is a different mechanism for workloads, covered in [machine-auth.md](machine-auth.md).
- **AWS IAM Identity Center**: the free workforce directory for your team's own AWS console and CLI access. It is not a general OIDC provider for Application Load Balancer authentication; for app login on AWS pair the ALB with Cognito or an OIDC provider from section 3 ([cloud-identity-proxies.md](cloud-identity-proxies.md)).

## 5. Self-hosted identity providers

Keycloak, authentik, Zitadel, Ory, and Authelia ([mfa.md](mfa.md)) give you OIDC and MFA without a vendor. They also give you a server to patch, back up, and keep highly available: a compromised or down identity provider takes every app with it. For a small project a hosted tier above is usually the smaller correct change.

## 6. MFA products

- **Duo**: the Duo Free edition covers up to 10 users with MFA and the Duo Mobile app. Its Authentication Proxy speaks RADIUS and LDAP, which retrofits MFA onto VPNs and services with RADIUS support; for mandatory MFA set `failmode=secure`, since the default `safe` admits a primary-authenticated user when Duo is unreachable, and keep a separately controlled emergency path.
- **Provider-native authenticators**: Microsoft Authenticator (Entra), Okta Verify (Okta), Google prompts (Google). Any RFC 6238 authenticator app works where a provider offers TOTP.
- **Hardware keys and passkeys**: YubiKey and other FIDO2 keys, and platform passkeys, are the phishing-resistant factor. Most of the providers above document passkey or WebAuthn support; check the tier before relying on it, and require it for administrators ([mfa.md](mfa.md)).

## 7. Poor fits for a small project

Zscaler Private Access, HashiCorp Boundary, Ping Identity, OneLogin, and Okta as a new purchase are enterprise products with enterprise pricing and sales-led onboarding. They are listed so an assistant recognizes them when a customer already has them, not as recommendations.

## Verify

- With only the password (or only a social login) an administrator cannot reach an admin function once MFA is required at the provider; test with a fresh session, and confirm the same admin function DOES succeed once MFA is completed, so the denial is MFA enforcement and not an unrelated failure.
- A valid account from outside your allowlist (a personal Gmail, a different tenant, a non-member GitHub user) is rejected after login, not admitted, while an allowed account does reach the app, so the rejection is the allowlist and not a broken login path.
- Correlate each test against the provider's sign-in log (in Microsoft Entra this is Sign-in logs, not Audit logs, which record configuration changes) and your application's authorization decision: confirm the required factor or assurance level was met and that the outside account was denied. A log entry alone shows only that a sign-in happened, not that MFA or the allowlist was enforced.

## Sources (checked September 2026)

- Microsoft Entra pricing (Free, P1, P2, External ID free MAU): https://www.microsoft.com/en-us/security/business/microsoft-entra-pricing
- Microsoft Entra External ID billing model: https://learn.microsoft.com/en-us/entra/external-id/external-identities-pricing
- Microsoft Entra security defaults: https://learn.microsoft.com/en-us/entra/fundamentals/security-defaults
- Google Cloud Identity pricing: https://cloud.google.com/identity/pricing
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
