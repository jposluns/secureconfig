---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "e973dfddb64ac911d0733967f4f6ec873f38131c6a1370386ab75909860e478b",
  "components": {
    "aws": {
      "name": "AWS ALB",
      "basis": "unknown",
      "sources": {
        "sb1894f4f0139": "https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html"
      }
    },
    "iap": {
      "name": "Google Cloud IAP",
      "basis": "unknown",
      "sources": {
        "saafdfc163fce": "https://docs.cloud.google.com/iap/docs/concepts-overview",
        "s4aebf47a7647": "https://docs.cloud.google.com/iap/docs/signed-headers-howto",
        "s4033073bd65d": "https://docs.cloud.google.com/iap/docs/enabling-cloud-run",
        "s241e0f3cc6a3": "https://docs.cloud.google.com/iap/docs/load-balancer-howto",
        "s35eb8e8a02a9": "https://docs.cloud.google.com/iap/docs/external-identities"
      }
    },
    "azure": {
      "name": "Azure authentication",
      "basis": "unknown",
      "sources": {
        "s5c4dc1862d97": "https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization",
        "s409d91a5181f": "https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities",
        "sba51f0a6aa9e": "https://learn.microsoft.com/en-us/azure/container-apps/authentication",
        "scc78dfba88dd": "https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-authorization"
      }
    },
    "cf": {
      "name": "Cloudflare Access",
      "basis": "unknown",
      "sources": {
        "s882e71a17d0e": "https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/",
        "s06747cf7388c": "https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/independent-mfa/"
      }
    },
    "ngrok": {
      "name": "ngrok",
      "basis": "unknown",
      "sources": {
        "sa9c57301ff54": "https://ngrok.com/docs/gateway/traffic-policy/actions/oauth",
        "sc18d7af3967e": "https://ngrok.com/docs/gateway/traffic-policy/actions/oidc",
        "s93e9bbd8127f": "https://ngrok.com/docs/gateway/agent/cli"
      }
    },
    "vercel": {
      "name": "Vercel",
      "basis": "unknown",
      "sources": {
        "se6089d5c4e96": "https://vercel.com/docs/deployment-protection",
        "se36c5ca2a8db": "https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication",
        "sf7c5fffb3f97": "https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/password-protection"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "vercel-announcement": {
      "name": "Vercel production-protection announcement",
      "basis": "2026-09-09",
      "sources": {
        "s7836e043434a": "https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan"
      }
    }
  },
  "claims": {
    "origin": {"text": "Origins must accept only proxy traffic through loopback, security-group restriction or ingress controls; direct access bypasses login.", "components": ["aws", "iap"], "sources": ["aws:sb1894f4f0139", "iap:s4033073bd65d"], "status": "REASONED"},
    "assertions": {"text": "Verify signed identity assertions before use; Azure's protected-header guarantee applies only to requests through its platform.", "components": ["aws", "iap", "cf", "azure"], "sources": ["aws:sb1894f4f0139", "iap:s4aebf47a7647", "cf:s882e71a17d0e", "azure:s409d91a5181f"], "status": "REASONED"},
    "mfa-idp": {"text": "ALB, IAP, Azure, ngrok and Vercel inherit MFA from the identity provider; enforce it there.", "components": ["aws", "iap", "azure", "ngrok", "vercel"], "sources": ["aws:sb1894f4f0139", "iap:saafdfc163fce", "azure:s5c4dc1862d97", "ngrok:sa9c57301ff54", "ngrok:sc18d7af3967e", "vercel:se36c5ca2a8db"], "status": "REASONED"},
    "mfa-access": {"text": "Cloudflare Access can enforce independent TOTP or WebAuthn MFA without IdP enforcement.", "components": ["cf"], "sources": ["cf:s06747cf7388c"], "status": "REASONED"},
    "authorization": {"text": "Authentication proves identity; application or proxy policy must still authorize access.", "components": ["aws", "iap", "ngrok"], "sources": ["aws:sb1894f4f0139", "iap:s35eb8e8a02a9", "ngrok:sa9c57301ff54"], "status": "REASONED"},
    "fail-closed": {"text": "Missing auth configuration, an unreachable auth service or unmatched route must never pass an unauthenticated request through.", "components": ["aws", "azure"], "sources": ["aws:sb1894f4f0139", "azure:s5c4dc1862d97"], "status": "REASONED"},
    "alb-actions": {"text": "authenticate-oidc or authenticate-cognito precedes forward and works only on HTTPS listeners.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-anonymous": {"text": "OnUnauthenticatedRequest defaults authenticate; allow forwards without claims, and deny returns HTTP 401.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-session": {"text": "SessionTimeout defaults seven days and permits a one-second minimum; the example selects 3600 seconds.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-callback": {"text": "The IdP redirect URL is the load-balancer DNS/CNAME over HTTPS at /oauth2/idpresponse.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-jwt": {"text": "Verify ES256 x-amzn-oidc-data using the regional public-key endpoint and key ID; bind signer ARN/client in the JWT header and check expiry.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-legacy": {"text": "Unsigned x-amzn-oidc-accesstoken and x-amzn-oidc-identity must not supply trusted identity.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "alb-target": {"text": "Restrict target security groups to the ALB security group; use HTTPS targets when claims need last-hop encryption.", "components": ["aws"], "sources": ["aws:sb1894f4f0139"], "status": "REASONED"},
    "iap-backends": {"text": "IAP protects supported App Engine, Cloud Run, Compute Engine, GKE and on-premises backends, not backend buckets.", "components": ["iap"], "sources": ["iap:saafdfc163fce", "iap:s241e0f3cc6a3"], "status": "REASONED"},
    "iap-iam": {"text": "Google Accounts and Workforce Identity Federation require IAP-secured Web App User IAM access.", "components": ["iap"], "sources": ["iap:saafdfc163fce"], "status": "REASONED"},
    "iap-customer": {"text": "Identity Platform customer identities bypass IAM authorization; the app must authorize verified assertion claims.", "components": ["iap"], "sources": ["iap:s35eb8e8a02a9"], "status": "REASONED"},
    "iap-jwt": {"text": "Verify ES256 x-goog-iap-jwt-assertion with Google's IAP JWKs, issuer https://cloud.google.com/iap and the resource audience.", "components": ["iap"], "sources": ["iap:s4aebf47a7647"], "status": "REASONED"},
    "iap-audience": {"text": "IAP audience paths differ for backendServices, regional Cloud Run services and App Engine apps.", "components": ["iap"], "sources": ["iap:s4aebf47a7647", "iap:s4033073bd65d"], "status": "REASONED"},
    "iap-unsigned": {"text": "Unsigned authenticated-user-email/id headers are forgeable when IAP is bypassed; use the JWT.", "components": ["iap"], "sources": ["iap:s4aebf47a7647"], "status": "REASONED"},
    "iap-run": {"text": "Load-balancer IAP does not protect run.app; enable IAP on Cloud Run or disable the default URL/restrict ingress.", "components": ["iap"], "sources": ["iap:s4033073bd65d"], "status": "REASONED"},
    "iap-firewall": {"text": "Compute Engine and GKE firewalls must block access that bypasses the load balancer.", "components": ["iap"], "sources": ["iap:s241e0f3cc6a3"], "status": "REASONED"},
    "azure-providers": {"text": "Easy Auth fronts the app without code changes; documented providers include Entra, Facebook, Google, X, GitHub, Apple preview and custom OIDC.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "azure-require": {"text": "Require authentication rejects anonymously with 302, 401, 403 or 404; Allow unauthenticated requests delegates the decision to the app.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "azure-https": {"text": "Enabling Easy Auth redirects to HTTPS regardless of the app setting; do not disable requireHttps in V2 configuration.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "azure-paths": {"text": "Authentication covers every path unless excluded paths are configured.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "azure-headers": {"text": "X-MS-CLIENT-PRINCIPAL carries Base64 claims with ID/NAME/IDP headers; external requests cannot set these platform headers.", "components": ["azure"], "sources": ["azure:s409d91a5181f"], "status": "REASONED"},
    "azure-me": {"text": "/.auth/me is available with the token store enabled.", "components": ["azure"], "sources": ["azure:s409d91a5181f"], "status": "REASONED"},
    "azure-tenant": {"text": "Entra defaults to allowing any tenant user to obtain a token; restrict the app registration to assigned users when needed.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "container-auth": {"text": "Container Apps uses per-replica auth sidecars, supported social/Entra/OIDC providers, Require/Allow choices and protected principal headers.", "components": ["azure"], "sources": ["azure:sba51f0a6aa9e"], "status": "REASONED"},
    "container-https": {"text": "Container Apps authentication requires HTTPS-only ingress with allowInsecure disabled.", "components": ["azure"], "sources": ["azure:sba51f0a6aa9e"], "status": "REASONED"},
    "static-login": {"text": "Static Web Apps preconfigures GitHub and Entra on all plans at /.auth/login/github and /.auth/login/aad; custom providers replace defaults.", "components": ["azure"], "sources": ["azure:scc78dfba88dd"], "status": "REASONED"},
    "static-roles": {"text": "Signed-in Static Web Apps users have anonymous and authenticated roles; staticwebapp.config.json route rules restrict by role.", "components": ["azure"], "sources": ["azure:scc78dfba88dd"], "status": "REASONED"},
    "static-tenant": {"text": "The preconfigured Static Web Apps Entra provider accepts any Microsoft account; a custom provider is needed for one tenant.", "components": ["azure"], "sources": ["azure:scc78dfba88dd"], "status": "REASONED"},
    "cf-jwt": {"text": "Prefer Cf-Access-Jwt-Assertion over the non-guaranteed CF_Authorization cookie; validate team certs, application AUD and team-domain issuer.", "components": ["cf"], "sources": ["cf:s882e71a17d0e"], "status": "REASONED"},
    "cf-rotation": {"text": "Access rotates signing keys every six weeks with seven-day previous-key validity; fetch endpoint keys instead of hard-coding.", "components": ["cf"], "sources": ["cf:s882e71a17d0e"], "status": "REASONED"},
    "ngrok-login": {"text": "Traffic-policy oauth or openid-connect redirects to the provider; OIDC uses issuer_url, client_id, client_secret and scopes.", "components": ["ngrok"], "sources": ["ngrok:sa9c57301ff54", "ngrok:sc18d7af3967e"], "status": "REASONED"},
    "ngrok-deny": {"text": "OAuth login alone admits unintended accounts; a deny expression must match identities outside the email/domain allowlist.", "components": ["ngrok"], "sources": ["ngrok:sa9c57301ff54"], "status": "REASONED"},
    "ngrok-managed": {"text": "Empty client_id/client_secret selects ngrok's managed OAuth app for supported providers.", "components": ["ngrok"], "sources": ["ngrok:sa9c57301ff54"], "status": "REASONED"},
    "ngrok-cli": {"text": "Use ngrok http 3000 --traffic-policy-file policy.yml; legacy OAuth allow-domain/email flags are deprecated.", "components": ["ngrok"], "sources": ["ngrok:s93e9bbd8127f"], "status": "REASONED"},
    "ngrok-origin": {"text": "Bind the app to 127.0.0.1 so a direct VM address cannot bypass ngrok login.", "components": ["ngrok"], "sources": ["ngrok:s93e9bbd8127f"], "status": "REASONED"},
    "vercel-members": {"text": "Deployment Protection is not end-user login; Vercel Authentication admits members/viewers, approved requesters, share links and automation bypass.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:se36c5ca2a8db"], "status": "REASONED"},
    "vercel-scope": {"text": "Standard Protection excludes production domains; configure All Deployments. The guide records free availability on every plan from September 9, 2026.", "components": ["vercel", "vercel-announcement"], "sources": ["vercel:se6089d5c4e96", "vercel:se36c5ca2a8db", "vercel-announcement:s7836e043434a"], "status": "REASONED"},
    "vercel-exception": {"text": "A domain Protection Exception disables protection for existing and future deployments; remove unintended exceptions.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "vercel-password": {"text": "At writing, Password Protection is Enterprise-included or USD 20/month/project on Pro; USD 150 legacy is existing-Pro only; Hobby lacks it.", "components": ["vercel"], "sources": ["vercel:sf7c5fffb3f97"], "status": "REASONED"},
    "vercel-enterprise": {"text": "Trusted IPs and Passport are Enterprise-only at the time of writing.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "verify-origin": {"text": "An external direct-port-3000 probe must refuse/time out at the intended address; HTTP proves exposure and resolver/local errors are inconclusive.", "components": ["aws", "iap", "curl"], "sources": ["aws:sb1894f4f0139", "iap:s4033073bd65d", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-anonymous": {"text": "Anonymous proxy requests must redirect to the IdP or return 401/403.", "components": ["aws", "azure"], "sources": ["aws:sb1894f4f0139", "azure:s5c4dc1862d97"], "status": "REASONED", "verify": [1]},
    "verify-headers": {"text": "Forged unsigned identity headers through the proxy must still yield a login challenge or denial, never admin identity.", "components": ["aws", "iap", "azure"], "sources": ["aws:sb1894f4f0139", "iap:s4aebf47a7647", "azure:s409d91a5181f"], "status": "REASONED", "verify": [1]},
    "verify-signature": {"text": "At the origin, accept a valid assertion then reject a well-formed changed claim with the original signature; proxy overwrite or malformed JSON proves nothing.", "components": ["aws", "iap", "cf"], "sources": ["aws:sb1894f4f0139", "iap:s4aebf47a7647", "cf:s882e71a17d0e"], "status": "REASONED"},
    "verify-platform": {"text": "Probe a real route at run.app or the Vercel production domain: require the platform challenge; app content bypasses auth and 404/transport errors are inconclusive.", "components": ["iap", "vercel"], "sources": ["iap:s4033073bd65d", "vercel:se6089d5c4e96", "vercel:se36c5ca2a8db"], "status": "REASONED"},
    "verify-outage": {"text": "Break authorization and require denial of a fresh unauthenticated request; established-session survival is a separate test.", "components": ["aws", "azure"], "sources": ["aws:sb1894f4f0139", "azure:s5c4dc1862d97"], "status": "REASONED"}
  }
}
---
# Identity-aware proxies: login in front of the app with no code change

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| origin: Origins must accept only proxy traffic through loopback, security-group restriction or ingress controls; direct access bypasses login. | AWS ALB unknown; Google Cloud IAP unknown | REASONED |
| assertions: Verify signed identity assertions before use; Azure's protected-header guarantee applies only to requests through its platform. | AWS ALB unknown; Google Cloud IAP unknown; Cloudflare Access unknown; Azure authentication unknown | REASONED |
| mfa-idp: ALB, IAP, Azure, ngrok and Vercel inherit MFA from the identity provider; enforce it there. | AWS ALB unknown; Google Cloud IAP unknown; Azure authentication unknown; ngrok unknown; Vercel unknown | REASONED |
| mfa-access: Cloudflare Access can enforce independent TOTP or WebAuthn MFA without IdP enforcement. | Cloudflare Access unknown | REASONED |
| authorization: Authentication proves identity; application or proxy policy must still authorize access. | AWS ALB unknown; Google Cloud IAP unknown; ngrok unknown | REASONED |
| fail-closed: Missing auth configuration, an unreachable auth service or unmatched route must never pass an unauthenticated request through. | AWS ALB unknown; Azure authentication unknown | REASONED |
| alb-actions: authenticate-oidc or authenticate-cognito precedes forward and works only on HTTPS listeners. | AWS ALB unknown | REASONED |
| alb-anonymous: OnUnauthenticatedRequest defaults authenticate; allow forwards without claims, and deny returns HTTP 401. | AWS ALB unknown | REASONED |
| alb-session: SessionTimeout defaults seven days and permits a one-second minimum; the example selects 3600 seconds. | AWS ALB unknown | REASONED |
| alb-callback: The IdP redirect URL is the load-balancer DNS/CNAME over HTTPS at /oauth2/idpresponse. | AWS ALB unknown | REASONED |
| alb-jwt: Verify ES256 x-amzn-oidc-data using the regional public-key endpoint and key ID; bind signer ARN/client in the JWT header and check expiry. | AWS ALB unknown | REASONED |
| alb-legacy: Unsigned x-amzn-oidc-accesstoken and x-amzn-oidc-identity must not supply trusted identity. | AWS ALB unknown | REASONED |
| alb-target: Restrict target security groups to the ALB security group; use HTTPS targets when claims need last-hop encryption. | AWS ALB unknown | REASONED |
| iap-backends: IAP protects supported App Engine, Cloud Run, Compute Engine, GKE and on-premises backends, not backend buckets. | Google Cloud IAP unknown | REASONED |
| iap-iam: Google Accounts and Workforce Identity Federation require IAP-secured Web App User IAM access. | Google Cloud IAP unknown | REASONED |
| iap-customer: Identity Platform customer identities bypass IAM authorization; the app must authorize verified assertion claims. | Google Cloud IAP unknown | REASONED |
| iap-jwt: Verify ES256 x-goog-iap-jwt-assertion with Google's IAP JWKs, issuer https://cloud.google.com/iap and the resource audience. | Google Cloud IAP unknown | REASONED |
| iap-audience: IAP audience paths differ for backendServices, regional Cloud Run services and App Engine apps. | Google Cloud IAP unknown | REASONED |
| iap-unsigned: Unsigned authenticated-user-email/id headers are forgeable when IAP is bypassed; use the JWT. | Google Cloud IAP unknown | REASONED |
| iap-run: Load-balancer IAP does not protect run.app; enable IAP on Cloud Run or disable the default URL/restrict ingress. | Google Cloud IAP unknown | REASONED |
| iap-firewall: Compute Engine and GKE firewalls must block access that bypasses the load balancer. | Google Cloud IAP unknown | REASONED |
| azure-providers: Easy Auth fronts the app without code changes; documented providers include Entra, Facebook, Google, X, GitHub, Apple preview and custom OIDC. | Azure authentication unknown | REASONED |
| azure-require: Require authentication rejects anonymously with 302, 401, 403 or 404; Allow unauthenticated requests delegates the decision to the app. | Azure authentication unknown | REASONED |
| azure-https: Enabling Easy Auth redirects to HTTPS regardless of the app setting; do not disable requireHttps in V2 configuration. | Azure authentication unknown | REASONED |
| azure-paths: Authentication covers every path unless excluded paths are configured. | Azure authentication unknown | REASONED |
| azure-headers: X-MS-CLIENT-PRINCIPAL carries Base64 claims with ID/NAME/IDP headers; external requests cannot set these platform headers. | Azure authentication unknown | REASONED |
| azure-me: /.auth/me is available with the token store enabled. | Azure authentication unknown | REASONED |
| azure-tenant: Entra defaults to allowing any tenant user to obtain a token; restrict the app registration to assigned users when needed. | Azure authentication unknown | REASONED |
| container-auth: Container Apps uses per-replica auth sidecars, supported social/Entra/OIDC providers, Require/Allow choices and protected principal headers. | Azure authentication unknown | REASONED |
| container-https: Container Apps authentication requires HTTPS-only ingress with allowInsecure disabled. | Azure authentication unknown | REASONED |
| static-login: Static Web Apps preconfigures GitHub and Entra on all plans at /.auth/login/github and /.auth/login/aad; custom providers replace defaults. | Azure authentication unknown | REASONED |
| static-roles: Signed-in Static Web Apps users have anonymous and authenticated roles; staticwebapp.config.json route rules restrict by role. | Azure authentication unknown | REASONED |
| static-tenant: The preconfigured Static Web Apps Entra provider accepts any Microsoft account; a custom provider is needed for one tenant. | Azure authentication unknown | REASONED |
| cf-jwt: Prefer Cf-Access-Jwt-Assertion over the non-guaranteed CF_Authorization cookie; validate team certs, application AUD and team-domain issuer. | Cloudflare Access unknown | REASONED |
| cf-rotation: Access rotates signing keys every six weeks with seven-day previous-key validity; fetch endpoint keys instead of hard-coding. | Cloudflare Access unknown | REASONED |
| ngrok-login: Traffic-policy oauth or openid-connect redirects to the provider; OIDC uses issuer_url, client_id, client_secret and scopes. | ngrok unknown | REASONED |
| ngrok-deny: OAuth login alone admits unintended accounts; a deny expression must match identities outside the email/domain allowlist. | ngrok unknown | REASONED |
| ngrok-managed: Empty client_id/client_secret selects ngrok's managed OAuth app for supported providers. | ngrok unknown | REASONED |
| ngrok-cli: Use ngrok http 3000 --traffic-policy-file policy.yml; legacy OAuth allow-domain/email flags are deprecated. | ngrok unknown | REASONED |
| ngrok-origin: Bind the app to 127.0.0.1 so a direct VM address cannot bypass ngrok login. | ngrok unknown | REASONED |
| vercel-members: Deployment Protection is not end-user login; Vercel Authentication admits members/viewers, approved requesters, share links and automation bypass. | Vercel unknown | REASONED |
| vercel-scope: Standard Protection excludes production domains; configure All Deployments. The guide records free availability on every plan from September 9, 2026. | Vercel unknown; Vercel production-protection announcement 2026-09-09 | REASONED |
| vercel-exception: A domain Protection Exception disables protection for existing and future deployments; remove unintended exceptions. | Vercel unknown | REASONED |
| vercel-password: At writing, Password Protection is Enterprise-included or USD 20/month/project on Pro; USD 150 legacy is existing-Pro only; Hobby lacks it. | Vercel unknown | REASONED |
| vercel-enterprise: Trusted IPs and Passport are Enterprise-only at the time of writing. | Vercel unknown | REASONED |
| verify-origin: An external direct-port-3000 probe must refuse/time out at the intended address; HTTP proves exposure and resolver/local errors are inconclusive. | AWS ALB unknown; Google Cloud IAP unknown; curl minimum write-out version 7.75.0 | REASONED |
| verify-anonymous: Anonymous proxy requests must redirect to the IdP or return 401/403. | AWS ALB unknown; Azure authentication unknown | REASONED |
| verify-headers: Forged unsigned identity headers through the proxy must still yield a login challenge or denial, never admin identity. | AWS ALB unknown; Google Cloud IAP unknown; Azure authentication unknown | REASONED |
| verify-signature: At the origin, accept a valid assertion then reject a well-formed changed claim with the original signature; proxy overwrite or malformed JSON proves nothing. | AWS ALB unknown; Google Cloud IAP unknown; Cloudflare Access unknown | REASONED |
| verify-platform: Probe a real route at run.app or the Vercel production domain: require the platform challenge; app content bypasses auth and 404/transport errors are inconclusive. | Google Cloud IAP unknown; Vercel unknown | REASONED |
| verify-outage: Break authorization and require denial of a fresh unauthenticated request; established-session survival is a separate test. | AWS ALB unknown; Azure authentication unknown | REASONED |
<!-- version-basis:end -->

An identity-aware proxy puts a login page in front of an application without changing the application: the cloud's load balancer, platform edge, or tunnel authenticates the user against an identity provider and forwards the request with the user's identity in headers. [cloudflare.md](cloudflare.md) documents the pattern for Cloudflare Access; this guide covers the equivalents in AWS, Google Cloud, Azure, ngrok, and Vercel. The pattern fails in two ways: the origin stays reachable around the proxy, or the app trusts an identity header anyone can type. Both are addressed below.

## 1. Rules common to every proxy

1. **The origin accepts traffic only from the proxy.** Bind to loopback behind a tunnel, reference the load balancer's security group, or restrict ingress to the load balancer. If the app also answers directly, the login page is decorative ([cloud-firewalls.md](cloud-firewalls.md)).
2. **The app never trusts a plain identity header.** Where the proxy provides a signed assertion (AWS, Google Cloud, Cloudflare), verify its signature, issuer, audience, and expiry before using any claim. Where the platform documents that clients cannot set the identity headers (Azure), that guarantee holds only for requests that arrived through the platform.
3. **MFA comes from the identity provider behind the proxy, with one exception.** For ALB, IAP, Azure, ngrok, and Vercel, enforce the second factor at the IdP and the proxy inherits it. Cloudflare Access is the exception: it can enforce independent MFA (a TOTP authenticator app, or a WebAuthn security key or biometric) directly in Access without the IdP doing so ([mfa.md](mfa.md), [identity-providers.md](identity-providers.md)).
4. Authorization is still yours: the proxy proves who the user is, and the app or the proxy policy decides what they may do ([authentication.md](authentication.md)).
5. **Fail closed.** The auth layer must deny when it cannot reach a decision: missing auth configuration, an unreachable authorization service, and an unmatched route must never fall through to the app unauthenticated. Test this with a fresh, unauthenticated request against a protected route while the authorization service is unreachable, and require denial, not pass-through; an already-authenticated session is a separate question, since a proxy is not guaranteed to recheck the identity provider on every request.

## 2. AWS Application Load Balancer

A listener rule with an `authenticate-oidc` (any OIDC provider) or `authenticate-cognito` (Cognito user pool, including social and SAML federation) action, followed by a `forward` action. Both action types work only on HTTPS listeners. The `OnUnauthenticatedRequest` field takes `authenticate` (the default: redirect to the IdP), `allow` (forward without claims, for pages with a public view), or `deny` (HTTP 401). `SessionTimeout` defaults to 7 days and can be set as short as 1 second. The IdP must allow `https://<load-balancer-dns-or-cname>/oauth2/idpresponse` as a redirect URL.

```json
{ "Type": "authenticate-oidc",
  "AuthenticateOidcConfig": {
    "Issuer": "https://idp.example.com", "AuthorizationEndpoint": "...", "TokenEndpoint": "...",
    "UserInfoEndpoint": "...", "ClientId": "...", "ClientSecret": "REPLACE_WITH_LONG_RANDOM_VALUE",
    "SessionTimeout": 3600, "OnUnauthenticatedRequest": "deny" },
  "Order": 1 }
```

The load balancer forwards the user claims to targets in `x-amzn-oidc-data`, a JWT signed with ES256. The app must verify that signature (public key from `https://public-keys.auth.elb.<region>.amazonaws.com/<key-id>`, key ID from the JWT header), confirm that the `signer` field in the JWT header is your load balancer's ARN (ALB's audience binding is this signer ARN together with the `client` field, both in the JWT header, not a payload `aud` claim), and confirm the token's `exp` has not passed, before using any claim; AWS publishes the `aws-jwt-verify` library, which performs these checks for you. `x-amzn-oidc-accesstoken` and `x-amzn-oidc-identity` are unsigned legacy headers and cannot be verified, so never use them for identity. Restrict the targets' security group to accept traffic only from the load balancer's security group, and use an HTTPS target group if the claims must be encrypted on the last hop.

## 3. Google Cloud Identity-Aware Proxy

IAP protects App Engine, Cloud Run, Compute Engine, GKE, and on-premises applications served through a supported backend; it does not support backend buckets, so Cloud Storage served directly through a backend bucket is not IAP-gated (Cloud Storage served through an IAP-protected Cloud Run backend is). With Google Accounts or an external IdP through Workforce Identity Federation, a user reaches the app only if they hold the **IAP-secured Web App User** IAM role on the resource. With customer identities through Identity Platform, IAM does not govern access at all: the app must authorize on the claims in the verified IAP assertion, because the IAM role is not enforced in that mode.

IAP adds `x-goog-iap-jwt-assertion`, an ES256 JWT. Verify the signature against the keys at `https://www.gstatic.com/iap/verify/public_key-jwk`, check `iss` is `https://cloud.google.com/iap`, and check `aud` matches your resource (`/projects/PROJECT_NUMBER/global/backendServices/SERVICE_ID` for a backend service, `/projects/PROJECT_NUMBER/locations/REGION/services/SERVICE_NAME` for Cloud Run, `/projects/PROJECT_NUMBER/apps/PROJECT_ID` for App Engine). The unsigned `x-goog-authenticated-user-email` and `x-goog-authenticated-user-id` headers can be forged by anyone who bypasses IAP; Google's docs describe the JWT as the secure alternative.

Bypass is the main risk. Google's docs say to verify whether backend resources can be reached directly when IAP is enabled on a load balancer, and that IAP on a load balancer secures only traffic through that load balancer, not traffic that reaches a Cloud Run service through its `run.app` URL. Either enable IAP directly on the Cloud Run service (the documented recommendation, no load balancer needed), or disable the default URL or restrict ingress so only the load balancer reaches it. For Compute Engine and GKE, firewall rules must block traffic that does not come through the load balancer.

## 4. Azure App Service and Azure Functions

Built-in authentication ("Easy Auth") is a platform module in front of the app; per the docs no SDK, language, or application code change is required. Providers: Microsoft Entra, Facebook, Google, X, GitHub, Apple (preview at the time of writing), and any OpenID Connect provider. Under **Settings > Authentication**, choose **Require authentication** to reject unauthenticated traffic (as an HTTP 302 redirect to the provider, recommended for websites; or 401, recommended for APIs; or 403 or 404), or **Allow unauthenticated requests** to let the app decide. Enabling the feature redirects all requests to HTTPS regardless of the app's enforce-HTTPS setting (`requireHttps` in the V2 configuration can turn this off; do not). Requiring authentication applies to every path; exceptions need a configuration file with excluded paths.

The app receives the identity in `X-MS-CLIENT-PRINCIPAL` (Base64 JSON of the claims), `X-MS-CLIENT-PRINCIPAL-ID`, `X-MS-CLIENT-PRINCIPAL-NAME`, and `X-MS-CLIENT-PRINCIPAL-IDP`, with `/.auth/me` available when the token store is on. The docs state that external requests are not allowed to set these headers, so they are present only if App Service set them. With the Entra provider, any user in the tenant can obtain a token by default; restrict the app registration to assigned users if that is not intended.

**Azure Container Apps** uses the same authentication system, run as a sidecar container on each replica, with Microsoft Entra ID, Facebook, GitHub, Google, X, and custom OpenID Connect providers, and the same **Require authentication** / **Allow unauthenticated access** choice and `X-MS-CLIENT-PRINCIPAL-*` headers that external requests cannot set. The docs require HTTPS only: `allowInsecure` must be disabled on the ingress.

**Azure Static Web Apps** authenticates with GitHub and Microsoft Entra ID out of the box on all plans (a registered custom provider replaces the preconfigured ones; X is no longer preconfigured). Sign-in is at `/.auth/login/github` or `/.auth/login/aad`, signed-in users hold the `anonymous` and `authenticated` roles, and route rules in `staticwebapp.config.json` restrict paths by role. The preconfigured Entra provider accepts any Microsoft account; to limit sign-in to one tenant, configure a custom Entra provider.

## 5. Cloudflare Access

Set up the tunnel and Access policy per [cloudflare.md](cloudflare.md). Then have the app validate the `Cf-Access-Jwt-Assertion` header (preferred over the `CF_Authorization` cookie, which is not guaranteed to be passed) against the public keys at `https://<team-name>.cloudflareaccess.com/cdn-cgi/access/certs`, checking that `aud` equals the application's AUD tag and `iss` is your team domain. Access rotates the signing key every 6 weeks with the previous key valid for 7 days, so fetch keys from the endpoint rather than hard-coding them.

## 6. ngrok

ngrok's traffic policy `oauth` action (providers include `google`, `github`, and `microsoft`) and `openid-connect` action (`issuer_url`, `client_id`, `client_secret`, `scopes`) redirect unauthenticated visitors to the provider, so a local tool becomes public only behind a login. Restrict who gets through with an expression on the identity the action exposes:

```yaml
on_http_request:
  - actions:
      - type: oauth
        config:
          provider: google
  - expressions:
      - "!actions.ngrok.oauth.identity.email.endsWith('@example.com')"
    actions:
      - type: deny
        config:
          status_code: 403
```

Use `!(actions.ngrok.oauth.identity.email in ['alice@example.com'])` for an explicit list; the negation matters, because the expression must be true for the `deny` to fire, so it has to match everyone you are turning away, not the one you are letting in. Leaving `client_id` and `client_secret` empty uses ngrok's managed OAuth application for the supported providers. Run with `ngrok http 3000 --traffic-policy-file policy.yml`; the older `--oauth`, `--oauth-allow-domain`, and `--oauth-allow-email` agent flags are marked deprecated in favour of traffic policy. Bind the app to `127.0.0.1` so the tunnel is its only path (rule 1); if the agent host is a cloud VM with the app on `0.0.0.0`, the login is decorative.

## 7. Vercel Deployment Protection

Vercel's protection guards a deployment from the public; it is not your application's user login. **Vercel Authentication** (all plans) admits logged-in team or project members with at least a viewer role, users granted access on request, holders of a shareable link, and automation with the bypass header. **Standard Protection** covers preview deployments and generated deployment URLs but not production domains; the **All Deployments** scope closes that gap, and Vercel's September 9, 2026 change made pairing it with Vercel Authentication free on every plan, including Hobby, rather than Pro and Enterprise only (per Vercel's Deployment Protection changelog; confirm current availability in your own dashboard). Until All Deployments protection is configured, the production domain stays public on every plan. A **Deployment Protection Exception** on a domain disables protection there for existing and future deployments, so review and remove any unintended exception rather than assuming All Deployments covers every URL. **Password Protection** is included on Enterprise and, at the time of writing, available on Pro at USD 20 per month per protected project (the older USD 150 per month Advanced Deployment Protection package is legacy, kept only for existing Pro teams), and is not offered on Hobby; Trusted IPs and Passport (your own IdP) are Enterprise only.

## Verify

REASONED: following block; the cited ALB, IAP and Azure authentication/header documentation defines origin isolation, anonymous denial and forged-header rejection. This read-only review cannot provision the cloud origin, IdP and external probe host; no live result is recorded. Expected responses and inconclusive failures are stated below.

```bash
# origin direct. Run this from a host OUTSIDE your cloud network (your laptop on a public connection,
# not the instance or a VPC peer), so the probe actually crosses the cloud boundary you are testing. Read err,
# not the number: it must name a refusal or timeout reaching YOUR address. An HTTP code means the origin
# answered. A resolver failure, a local socket error, or a timeout that did not come from the remote
# address is inconclusive, never a pass.
(                                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/" ;;
  esac
)
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://app.example.com/                       # via proxy, no session: 302 to the IdP, or 401/403
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -s -H "x-amzn-oidc-identity: admin" \
     -H "X-MS-CLIENT-PRINCIPAL-NAME: admin" \
     -H "X-Goog-Authenticated-User-Email: admin@example.com" \
     https://app.example.com/whoami                      # still the login redirect or a 401/403; never "admin"
```

After logging in, confirm that the app's own identity check reads the signed assertion (`x-amzn-oidc-data`, `x-goog-iap-jwt-assertion`, `Cf-Access-Jwt-Assertion`) and rejects a forged one. Test directly, because the proxy overwrites the header, so a through-proxy test proves nothing: from the origin host, or a host inside the allowed security group, first send a request carrying a valid, unexpired assertion and confirm the app accepts it (the positive control), then send one whose signature is unchanged but a non-authorizing claim is altered while the token stays well formed (valid JSON and base64url), and require rejection: `curl -q -s --noproxy '*' -H 'x-amzn-oidc-data: <valid assertion, one claim changed, signature kept>' http://127.0.0.1:3000/whoami`. Keep the token well formed, because an app that never checks the signature would still reject a token mangled into malformed JSON, which would not prove verification.

- Reach the app's own default platform hostname from outside your cloud network and confirm it does not serve your app. Fetch a real app route (not just `/`) at your Cloud Run `run.app` URL or your Vercel production domain: `curl -q -s --noproxy '*' -D - 'https://REPLACE_WITH_YOUR_PLATFORM_URL/an-app-route'`, and read the status line, headers, and body together. A pass is the platform's own challenge, never your app's content: for Cloud Run a 302 redirect to a Google or IAP sign-in, or a 401 from IAP (IAP returns 401 rather than a 302 when the request does not advertise HTML, i.e. no `Accept: text/html` header); for Vercel the Vercel authentication page. A 200 serving your app's own content means the platform URL bypasses the proxy; a 404 or a transport error is inconclusive, never a pass, because a missing service also returns 404.
- Stop the authorization service, or break its configuration, and send a fresh, unauthenticated request to a protected route: it must be denied, never passed through to the app. This checks that an undecidable auth state fails closed; it does not test whether an already-established session survives the outage, since a proxy is not required to recheck the identity provider on every request.

## Common mistakes

- Enabling IAP or ALB authentication while the Cloud Run `run.app` URL, the instance's public IP, or a second listener still serves the app directly.
- Reading `x-amzn-oidc-identity`, `X-Goog-Authenticated-User-Email`, or a similar unsigned header as the user identity.
- Treating Vercel Authentication as end-user login, or leaving production on Standard Protection and assuming it is covered.
- Using the ngrok `oauth` action without a `deny` rule on email or domain, which lets anyone with a Google account in.

## Sources (checked September 2026)

- AWS, Authenticate users using an Application Load Balancer: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html
- Google Cloud IAP overview: https://docs.cloud.google.com/iap/docs/concepts-overview
- Google Cloud IAP, securing your app with signed headers: https://docs.cloud.google.com/iap/docs/signed-headers-howto
- Google Cloud IAP, enabling IAP for Cloud Run: https://docs.cloud.google.com/iap/docs/enabling-cloud-run
- Google Cloud IAP, supported load balancer backends (backend buckets not supported): https://docs.cloud.google.com/iap/docs/load-balancer-howto
- Google Cloud IAP, external identities and Identity Platform (IAM not used for access control): https://docs.cloud.google.com/iap/docs/external-identities
- Azure App Service authentication and authorization: https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization
- Azure App Service, work with user identities (headers): https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-user-identities
- Azure Container Apps authentication: https://learn.microsoft.com/en-us/azure/container-apps/authentication
- Azure Static Web Apps authentication and authorization: https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-authorization
- Cloudflare Access, validate JWTs: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/
- Cloudflare Access, independent MFA: https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/independent-mfa/
- ngrok traffic policy OAuth action: https://ngrok.com/docs/gateway/traffic-policy/actions/oauth
- ngrok traffic policy OpenID Connect action: https://ngrok.com/docs/gateway/traffic-policy/actions/oidc
- ngrok agent CLI (`ngrok http` flags): https://ngrok.com/docs/gateway/agent/cli
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Vercel Authentication: https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication
- Vercel Password Protection (pricing): https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/password-protection
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- Vercel production protection on every plan (announcement dated 2026-09-09, checked October 2026): https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan
