# Strong authentication baseline

Authentication is how a service confirms who is asking before allowing access. This guide helps your AI assistant apply the baseline rules on every service, including deny by default, no default or shared credentials, credentials only over TLS or an equivalent such as SSH, modern password hashing, and rate-limited logins.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/authentication.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against OWASP authentication and password storage (no recorded version), OAuth security BCP RFC 9700, OpenID Connect Core 1.0, NIST password guidance SP 800-63B-4, Python bcrypt rejection threshold 5.0.0, OpenSSL rand 3.5, Python secrets 3.13, and Git ignore rules v2.49.0, plus 12 more recorded bases; 16 further sources are pinned to a commit and 6 carry no recorded version. Metadata reviewed 2026-10-21; documentation checked September 2026. The guide records 54 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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
6. **Prefer SSO/OIDC over local accounts** where the product supports it, and enable MFA wherever available. [Cloudflare Access](cloudflare.md) can place an authentication layer in front of a self-hosted web application published through Access; the cited pages show that pattern, not that any application works behind it unchanged (this guide's assessment; no application-compatibility list is cited). For the login step, Cloudflare documents [integrating your organization's identity provider](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/index.mdx#L14-L18), with multiple identity providers usable simultaneously and a [generic OIDC connector](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/generic-oidc.mdx#L15) for identity providers not already set in Access, and sending a [one-time PIN to approved email addresses](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15) as an alternative; OTP login and the identity provider of your choice can be configured simultaneously so users select their own authentication method. Create the Access application before the tunnel route; without it, the published application is available to anyone on the Internet. Validate the Access JWT at the origin. For a Tunnel route, configure origin TLS verification and Access JWT checking; for a directly proxied HTTPS origin, use Full (strict) where applicable. Where no native MFA exists, add it with an identity layer, an app-level TOTP library, or a hosted service, per [mfa.md](mfa.md).
7. **Scope machine access.** API clients get their own tokens with the least privilege the task needs, not an admin password. Support and exercise rotation; set expiry where the platform allows it.
8. **Harden sessions.** Set cookies `Secure`, `HttpOnly`, and `SameSite` (`Lax` or `Strict`) (per [OWASP session-cookie guidance](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Session_Management_Cheat_Sheet.md#L131-L149)), sign them with a strong random secret (this guide's recommendation; the cited passage does not cover signing), and enforce an idle and an absolute timeout server-side (a cookie expiry alone does not stop a replayed cookie). Use an unpredictable session identifier, regenerate it (invalidating the old one) on login and on any privilege change, and reject a session ID the server never issued (session fixation). Invalidate sessions server-side on logout and on password change. `SameSite` is not a complete CSRF defense (`Lax` still allows a top-level state-changing GET, and a sibling subdomain can be same-site), so a cookie-authenticated state-changing request must also carry an anti-CSRF token or a strict `Origin`/`Sec-Fetch-Site` check, and must never change state through a safe method such as GET.
9. **Rate-limit authentication endpoints** and lock or delay after repeated failures. Per-client rate limits do not stop distributed credential stuffing (valid breached passwords spread thin across many addresses), so add account-aware and aggregate abuse controls alongside source-based ones, and avoid a lockout an attacker can use to deny a user access. Keep login, registration, and password-reset responses uniform in message and timing so they do not disclose whether an account exists. Log authentication successes and failures with source address and account, and keep the logs long enough to investigate an incident. For SSH on Linux hosts, enable the relevant fail2ban jail (guide requirement): the shipped `sshd` jail uses an `sshd` failure filter, and jails are [disabled by default](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L152-L167). Beyond SSH, fail2ban 1.1.1 ships the [`nginx-http-auth` jail](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L370-L376) using the nginx error log and the [`webmin-auth` jail](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L491-L495) using `syslog_authpriv` with `syslog_backend`. The `nginx-http-auth` [normal-mode patterns](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-http-auth.conf#L9-L37) match password-mismatch, user-not-found and authentication-failure messages with a client address; its comments say an extensive search of all nginx authentication failures has not been done. The `webmin-auth` [patterns](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/webmin-auth.conf#L4-L20) match the shown Webmin `Non-existent login` and `Invalid login` messages with a source host. Enable only the relevant jails in local configuration and, for file backends, set `logpath` to the matching logs; the shipped entries are starting points, so confirm the selected filter matches your deployment's failures (this guide's advice based on those settings). These files establish the listed jails and patterns, not coverage of a particular panel's log format or ease of setup (this guide's assessment); other login panels still require suitable filters and logs. Bound expensive endpoints too: inference, uploads, and job submission need request-size, concurrency, and timeout limits in addition to per-client rate limits, because an exposed AI endpoint left without them can burn GPU time and money even while correctly rejecting bad credentials, a failure mode known as denial of wallet. [realtime-webhooks.md](realtime-webhooks.md) covers the streaming and webhook transports these limits also apply to.
10. **Least privilege everywhere.** Separate admin from daily-use accounts, and give database and OS service accounts only the rights the application uses.
11. **Federated login is authentication, not authorization.** After Google, Microsoft, GitHub, or any provider returns an identity, check it against an application allowlist (tenant, hosted domain, organization or group membership, or explicit users) before granting access (this guide's recommendation); a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the `hd` claim in the validated ID token against an accepted domain; neither the email domain nor the request `hd` parameter controls access. Microsoft's multi-tenant `common` endpoint serves organizational and personal accounts. Validate the token issuer, signing-key issuer, and `tid`, then apply the application tenant allowlist. [oidc-integration.md](oidc-integration.md) has the checks; [identity-providers.md](identity-providers.md) has the providers.
12. **OIDC and OAuth hygiene.** Authorization code flow with PKCE (`S256`, never `plain`); exact-match redirect URIs; fresh per-transaction `state` and `nonce`, verified and bound to the initiating browser session; ID tokens validated for signature (keys from the provider's JWKS, algorithm pinned, never `none`), issuer, audience, and expiry; short-lived access tokens with refresh-token rotation; tokens never in URLs. Prefer a server-side session in an `HttpOnly` cookie to tokens in browser storage. Link accounts by issuer plus subject, never by email alone.
13. **Enforce MFA where access is granted, not only where it is enrolled.** A user who enrolled a second factor but can still act with a password-only session is not protected. Require the factor in provider policy or in the app, and test it.
14. **Protect the control plane.** MFA on the Git host, the cloud account, the DNS registrar, the deployment platform, the secret manager, and the identity provider's administrator account. A takeover there bypasses every control inside the app.
15. **Authenticate every transport.** WebSockets, server-sent events, GraphQL, gRPC, webhooks (verify the sender's signature and reject replays), inference endpoints, and management APIs each need their own authentication check (this guide's requirement). Do not rely on the HTML login to protect them (this guide's requirement); the cited protocol sources do not establish that an HTML login protects these endpoints (this guide's assessment). RFC 6455 says the protocol [does not prescribe how servers authenticate clients during the WebSocket handshake](https://www.rfc-editor.org/rfc/rfc6455.html#section-10.5) and that the WebSocket server can use any client authentication mechanism available to a generic HTTP server, such as cookies, HTTP authentication or TLS authentication; a server meant to process input only from certain sites [SHOULD verify the `Origin` field](https://www.rfc-editor.org/rfc/rfc6455.html#section-10.2) and answer an unacceptable origin with `403 Forbidden`. OWASP says [WebSockets have no built-in authentication and browsers include cookies in WebSocket handshake requests](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L74), exposing them to cross-site WebSocket hijacking, and to [validate the `Origin` header on every handshake against an explicit allowlist of trusted origins](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L85). WHATWG's EventSource constructor [sets the credentials mode for connection requests to `include` when `withCredentials` is true](https://html.spec.whatwg.org/multipage/server-sent-events.html) (living standard, last updated 20 October 2026 when checked). These sources show that browser credentials such as a login cookie can reach a WebSocket or SSE endpoint, not that the endpoint checks them (this guide's assessment). Stripe's webhook helper checks the [signature](https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L182-L216) and a [timestamp tolerance](https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L357-L410); comprehensive replay rejection remains this guide's application requirement, not a guarantee from those checks (this guide's assessment). OWASP's [GraphQL access-control list](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L190-L198) recommends checking authorization for requested data, on both edges and nodes, disabling introspection queries system-wide in any production or publicly accessible environments, and disabling GraphiQL and similar schema exploration tools in those environments. For publicly consumed APIs, its separate [introspection/GraphiQL advice](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L287-L290) is to consider disabling introspection for unauthenticated or unauthorized users, not a general GraphQL authentication boundary (this guide's assessment). GraphQL's [authorization page](https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L5) says GraphQL execution should begin after authentication middleware confirms the user's identity and passes that information to the GraphQL layer; its [example](https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L22) has that middleware check the user's credentials and add their identity to the request's `context` object for every field resolver, and its [recap](https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L89-L92) says authorization logic should be delegated to the business logic layer and that, after execution begins, a GraphQL server should decide whether the client is authorized to access data for the included fields. These lines place authentication before GraphQL execution and pass the authenticated user through `context`; they do not say how to authenticate a GraphQL request, which credentials to accept or what the middleware must check (this guide's assessment). For GraphQL served over HTTP, graphql.org's serving page says [GraphQL should be placed after all authentication middleware](https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L21) so that it has the same session and user information as the other HTTP endpoint handlers, and its [recap](https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L132) says the server should handle user authentication before a GraphQL request is validated. The GraphQL over HTTP working draft says a server [MAY forbid a request, for example to require authentication, and SHOULD then use the relevant `4xx` or `5xx` status code; that decision SHOULD NOT be based on the contents of a well-formed GraphQL-over-HTTP request](https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L115-L118); its [security section](https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L705-L720) puts general security concerns out of scope and does not repeat authorization and authentication security. Over HTTP, then, graphql.org recommends authenticating a GraphQL request with the application's own HTTP authentication middleware, as for its other endpoints (this guide's reading of those lines); which credentials to accept and what that middleware must check remain this guide's requirements under rules 7, 8 and 12, and these pages do not cover GraphQL over a non-HTTP transport (this guide's assessment). As vendor examples only, Apollo Server's [authentication page](https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L25-L62) has a `context` function extract a user token from the HTTP `Authorization` header and add the user to `contextValue`, with an [API-wide variant](https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L79-L135) that throws an `UNAUTHENTICATED` error so the operation is not executed; Hasura says to [configure an admin secret key](https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/deployment/securing-graphql-endpoint.mdx#L14-L15) so that its GraphQL endpoint and Console are not publicly accessible, and describes a [JWT mode](https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/auth/overview.mdx#L63-L66) that integrates with an existing authentication service (documentation source files at pinned commits; the published pages carried the same statements when checked in October 2026). OWASP requires [access control at each non-public REST endpoint](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L35-L38), describing authentication, authorization and session management and recommending centralized user authentication with local endpoint access decisions; it also calls for [strong authentication when management endpoints must be Internet-accessible](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L167-L170). Apply those REST controls to REST-style inference and management APIs (this guide's requirement and reasoning; the passage does not name inference APIs). gRPC's authentication guide distinguishes [channel credentials, such as SSL credentials, from call credentials attached to a call](https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L62-L74), and says the two can be combined so that the call credentials' authentication data is sent with every call made on the channel. It says [SSL/TLS authenticates the server and encrypts the data exchanged](https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L23-L26), with optional client certificates for mutual authentication, and its description of [token-based authentication with Google](https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L38-L46) says that mechanism must in general be used as well as SSL/TLS on the channel, adding that most gRPC language implementations will not let you send credentials on an unencrypted channel. For OAuth, it says [the token is always part of per-call credentials](https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L122-L131), normally sent in the HTTP Authorization header, and that the server verifies it, in most implementations with a server-side interceptor. Applying these credentials to inference or management APIs served over gRPC is this guide's inference; the file does not mention those APIs and does not establish that a given server verifies call credentials (this guide's assessment). In grpc-go terms, the authentication example's README says that [on the server side users usually get the token and verify it inside an interceptor, returning `codes.Unauthenticated` for an invalid token](https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/README.md#L49-L62), and its [server](https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/server/main.go#L57-L65) installs that interceptor with `grpc.UnaryInterceptor`; go-grpc-middleware v2.3.3's [unary](https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L26-L50) and [stream](https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L52-L70) auth interceptors run an application-supplied `AuthFunc`, or a service's `AuthFuncOverride`, before the handler. An example and a middleware library show verification by code the server installs; they do not establish that grpc-go, or any other gRPC implementation, lacks a built-in check (this guide's assessment). From source reading of pinned code, verification differs by server: vLLM v0.30.0's gRPC launcher [creates its server without an interceptor and binds it with `add_insecure_port`](https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/grpc_server.py#L87-L118) (see [model-servers.md](model-servers.md)); Triton [runs a call only when the client metadata carries the configured restricted header key and value, otherwise returning `UNAVAILABLE`](https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.cc#L194-L225), for the API groups `--grpc-restricted-protocol` names (see [model-servers.md](model-servers.md)); Text Embeddings Inference [adds an `authorization` check returning `unauthenticated` to its info, tokenize, embed, predict and rerank services only when an API key is set, and never to health or reflection](https://github.com/huggingface/text-embeddings-inference/blob/1bb59202500e5f69dd8be63dd1604f7625124fbe/router/src/grpc/server.rs#L1472-L1508) (a reading new to this guide; [ai-infra-services.md](ai-infra-services.md) cites that file only for the gRPC build's metrics exporter); and argocd-server's [gRPC interceptor chains](https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L961-L985) call a default [authentication function](https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1537-L1576) that returns without checking credentials when auth is disabled and otherwise attempts token authentication, rejecting the call after a claims error unless settings load and anonymous access is enabled, in which case it permits the call anonymously. Services that override that function are the exception: the server [imports its auth interceptors from `go-grpc-middleware/v2`](https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L37), which Argo CD's `go.mod` pins at v2.3.3 according to [gitops-controllers.md](gitops-controllers.md), and in v2.3.3 those interceptors run a service's `AuthFuncOverride` in place of the default function when the service implements it (that guide records the overriding services; it did not compare the `go.sum` module hash or fetch grpc-go, which supplies the service value). These are inference and management data points, not a general boundary, and whether a deployed server verifies call credentials needs a live test with a real gRPC client (this guide's assessment). For browser WebSocket clients using tokens, OWASP says to [withhold protected data until token validation succeeds and close on authentication failure or timeout](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L118-L120), and to [check authorization for each action](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L128). Standard Webhooks specifies [authenticating the payload, timestamp and stable event identifier](https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L133-L143), with the identifier usable to process an event only once even after malicious repeats, and recommends both [timestamp tolerance and webhook-id deduplication](https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L233-L234). Reject repeats within the accepted timestamp window too (this guide's requirement and reasoning from the separate tolerance and idempotency checks); the specification's five-minute ID-storage example does not establish a universal retention period or comprehensive deployed replay rejection (this guide's assessment). These are standards, guidance and source readings, not established deployment behaviour: which credentials a GraphQL request is to carry, what its authentication middleware must check and how GraphQL over a non-HTTP transport is authenticated, a general HTML-login boundary for non-HTTP transports, authentication boundaries for non-REST inference and management APIs in general and on servers not read here, and a deployed application's authentication and comprehensive replay rejection remain unestablished (this guide's assessment); GraphQL, inference and management APIs still require their own authentication checks. Machine credentials follow [machine-auth.md](machine-auth.md).
16. **Offboard promptly.** When a person leaves, revoke their provider membership, proxy sessions, application sessions, and personal tokens (this guide's recommendation). Microsoft Entra documents blocking new sign-ins and revoking refresh tokens, but says the application must revoke its own session; its access-token lifetime varies, and CAE critical-event enforcement can take up to 15 minutes for supported services. Cloudflare Access documents per-user session revocation, but an active IdP profile can start a new session; after user logout, previously issued tokens stop being accepted in 20-30 seconds. OAuth2 Proxy and Authelia document session-cookie expiry, but the cited passages do not establish immediate per-user revocation for those proxies. RFC 7009 specifies immediate token invalidation with possible propagation delay and conditional access-token revocation support. The fetched sources do not establish a provider-membership removal mechanism or this deployment's measured maximum time-to-revoke. Measure each system's maximum time-to-revoke where immediate revocation is unavailable, and work to shrink it (this guide's recommendation; no delay was measured here). [deployment-lifecycle.md](deployment-lifecycle.md) has the lifecycle checks; [mfa.md](mfa.md) covers revoking the second factor along with the account.
17. **Set a password policy and reject breached passwords.** Require a minimum length of at least 8 characters when a second factor is enforced, otherwise at least 15 (NIST SP 800-63B-4); allow long passphrases and every character, and drop periodic-rotation and composition rules. Screen new and changed passwords against a known-breach corpus (for example the Pwned Passwords range API), because a correct breached password defeats both hashing and per-IP rate limits.
18. **Secure account recovery.** Password and MFA reset is a sensitive authentication surface: issue cryptographically random, single-use, short-lived, account-bound reset tokens; deliver them only to a pre-verified channel; keep the reset response non-enumerating; reauthenticate for a recovery-address or MFA-factor change; and on completion invalidate outstanding sessions and unused reset tokens. Recovery must never silently drop the MFA requirement.

## Quick checks

- REASONED: offboarding timing is this guide's test expectation, informed by the cited [Microsoft Entra session model](https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62), [Cloudflare Access session revocation](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L159-L186), and [RFC 7009 token revocation](https://www.rfc-editor.org/rfc/rfc7009.html#section-2.1). No deployed IdP, proxy, application, token issuer or account is available in the authoring environment, so no revocation request or protected-resource replay was run. With a disposable account, first confirm that an authenticated request to a protected resource succeeds with each provider, proxy and application session and personal token. Remove provider membership and revoke the sessions and tokens, then replay the same protected-resource request with each old credential at recorded intervals until it is refused and returns no protected data; record the elapsed time for every layer and compare each result with its configured maximum time-to-revoke. Before revocation the matched request must succeed; after revocation each old credential must be refused and return no protected data. The check fails if an old credential is still accepted or returns protected data beyond its configured maximum time-to-revoke, or if measured elapsed time to refusal exceeds that maximum. These are deployment test expectations, not observed results.
- REASONED: unauthenticated-rejection comparisons per the cited OWASP Authentication Cheat Sheet, with the expected rejections stated in this item; no deployed service exposing these paths and transports is available in the authoring environment, so no request was sent. A protocol-appropriate unauthenticated request to every non-public path from rule 1 (metrics, health, admin, message-queue UIs) and every transport from rule 15 (WebSocket, SSE, GraphQL, gRPC, webhook, inference, management API), not just the HTML app, is rejected and returns no protected data: an HTTP endpoint gives `401`, `403`, or a login redirect; a gRPC call gives `UNAUTHENTICATED` for missing or invalid credentials (`PERMISSION_DENIED` for an identified caller lacking permission); an SSE stream is refused; a WebSocket either rejects the upgrade (handshake-time auth) or, with first-message auth, permits the upgrade but rejects protected operations, returns no protected data, and closes the connection on auth failure. These are test expectations, not observed service responses. A bare `curl` GET does not exercise the non-HTTP transports, so test each with a real client.
- DEMONSTRATED: scanner discrimination on disposable fixture repositories at marking time, with gitleaks 8.30.1: a planted randomized key was reported by the history, working-tree and staged scans (exit 9, leaks found: 1; gitleaks exits 9 only when invoked with --exit-code 9, and its default exit status on leaks is 1, re-observed at marking time across the history, working-tree and staged scan modes with gitleaks 8.30.1, with exit 0 on clean scans) and a clean control repository reported no leaks (exit 0), while the supplementary git log pattern matched a password-named diff and missed a renamed key, as this item warns; this demonstrates the checks, not that any given repository is clean. A secret scanner (gitleaks or similar) over the working tree, staged changes, and full history comes back clean; Gitleaks documents directory and Git scans plus pre-commit use, and while the fetched README does not specify a separate staged-scan mode, `cmd/git.go` at v8.30.1 defines `--staged` ("scan staged commits (good for pre-commit)") and `--pre-commit` flags that build a Git diff command instead of the Git log command, so verify staged, all-ref and merge-commit coverage with the selected scanner and configuration. The README says the `git` command scans `git log -p` patches and that `--log-opts` configures that command, with `--log-opts="--all commitA..commitB"` as its range example; Git documents `--all` as listing all the refs in `refs/`, along with `HEAD`, and documents that merge commits show no diff, even with `--patch`, unless a `--diff-merges` variant (including short `-m`) is given or `--first-parent` is in use, so passing `--all` and such a variant through `--log-opts` is this guide's route to all-ref and merge-commit history; those lines show the flags and `git log` options, not that the scanner reports leaks from every resulting diff or ref (this guide's assessment), which is why the coverage check above stays required. `git log -p | grep -iE 'password|secret|api[_-]?key'` is only a supplementary quick check, since it misses secrets without those words and does not cover uncommitted files, every ref, or changes that appear only in merge commits; per the cited Git lines, `git log -p -m --all` would extend the patch stream to all refs and merge diffs while keeping the word-list and uncommitted-file misses, and no such extended run is recorded here (the historical fixture run used the command as shown).
- REASONED: default-account inspection recommended by this guide; no deployed user store is available in the authoring environment, so no account listing was read. The user store contains no account named `admin`, `test`, or `demo` with a known or empty password.
- REASONED: negative-test expectations per the cited OAuth 2.0 Security Best Current Practice (RFC 9700) and OpenID Connect Core 1.0; no deployed application, token issuer or fronting layer is available in the authoring environment, so none of these rejections was observed. The wrong-tenant expectation follows Microsoft's issuer and `tid` validation rules plus this guide's tenant-allowlist recommendation. The cross-user expectation follows the [pinned OWASP Authorization Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Authorization_Cheat_Sheet.md#L93-L99). Cloudflare describes Access policy enforcement, origin JWT validation and Tunnel Access JWT checking, and says a publicly routable origin needs its IP protected by other methods. OAuth2 Proxy documents upstream identity headers and warns that when `--reverse-proxy` is enabled and `--trusted-proxy-ip` is unset, a client that can reach OAuth2 Proxy directly may be able to spoof forwarded headers; Authelia uses session cookies to authorize protected websites. Google IAP says bypassing it permits forged unsigned identity headers; its signed-header how-to says to verify the JWT header, payload and signature to secure an app with the IAP JWT, and calls signed headers secondary security; AWS ALB requires verification of its signed claims header and signer ARN. Origin isolation remains a deployment test expectation; none of these documents establishes the reachability of a particular origin. Negative tests should pass: a missing, expired, wrong-issuer, wrong-audience, or wrong-tenant token is rejected; user A cannot read user B's resources; the origin is unreachable except through its fronting layer.

## Sources (checked September 2026)

- fail2ban default disabled setting (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L152-L167
- fail2ban sshd jail configuration (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L271-L279
- fail2ban sshd filter (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/sshd.conf#L104-L111
- fail2ban 1.1.1 nginx HTTP-auth jail (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L370-L376
- fail2ban 1.1.1 nginx HTTP-auth patterns and coverage caveat (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-http-auth.conf#L9-L37
- fail2ban 1.1.1 Webmin authentication jail (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L491-L495
- fail2ban 1.1.1 Webmin authentication patterns and examples (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/webmin-auth.conf#L4-L20
- gRPC authentication and permission status codes (checked October 2026): https://github.com/grpc/grpc/blob/v1.84.0/doc/statuscodes.md#L13-L24
- WebSocket opening handshake (RFC 6455, checked October 2026): https://www.rfc-editor.org/rfc/rfc6455.html#section-1.3
- WebSocket closing handshake (RFC 6455, checked October 2026): https://www.rfc-editor.org/rfc/rfc6455.html#section-1.4
- WebSocket client authentication left to the server (RFC 6455, checked October 2026): https://www.rfc-editor.org/rfc/rfc6455.html#section-10.5
- WebSocket Origin verification (RFC 6455, checked October 2026): https://www.rfc-editor.org/rfc/rfc6455.html#section-10.2
- WHATWG EventSource failure handling and withCredentials credentials mode (living standard last updated 20 October 2026, checked October 2026): https://html.spec.whatwg.org/multipage/server-sent-events.html
- Stripe webhook signature computation (checked October 2026): https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L182-L216
- Stripe webhook signature and timestamp tolerance (checked October 2026): https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L357-L410
- OWASP GraphQL data, edge and node authorization and production/public introspection and GraphiQL disabling (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L190-L198
- OWASP GraphQL introspection and authentication scope (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L287-L290
- OWASP non-public REST endpoint access control (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L35-L38
- OWASP management endpoint authentication (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L167-L170
- OWASP WebSocket token authentication (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L118-L120
- OWASP WebSocket per-action authorization (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L128
- OWASP WebSocket lack of built-in authentication and handshake cookies (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L74
- OWASP WebSocket Origin allowlist validation (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L85
- Standard Webhooks signed metadata and stable event identifiers (pinned commit 7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b, checked October 2026): https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L133-L143
- Standard Webhooks timestamp tolerance and ID deduplication (pinned commit 7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b, checked October 2026): https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L233-L234
- GraphQL execution after authentication (pinned commit be061651a39b9b85115bf3e430d516eab9610cee, checked October 2026): https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L5
- GraphQL authentication middleware and request context (pinned commit be061651a39b9b85115bf3e430d516eab9610cee, checked October 2026): https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L22
- GraphQL authorization in the business logic layer (pinned commit be061651a39b9b85115bf3e430d516eab9610cee, checked October 2026): https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L89-L92
- GraphQL placement after all authentication middleware (pinned commit be061651a39b9b85115bf3e430d516eab9610cee, checked October 2026): https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L21
- GraphQL user authentication before request validation (pinned commit be061651a39b9b85115bf3e430d516eab9610cee, checked October 2026): https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L132
- GraphQL over HTTP working draft, forbidding requests to require authentication (pinned commit d438b209d60fa3d34b0530b605e60d5640c7ef9b, checked October 2026): https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L115-L118
- GraphQL over HTTP working draft, security scope (pinned commit d438b209d60fa3d34b0530b605e60d5640c7ef9b, checked October 2026): https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L705-L720
- Apollo Server authentication and context example (pinned commit 0c22029c2af47d3829e730e9820c01cef0557627, checked October 2026): https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L25-L62
- Apollo Server API-wide `UNAUTHENTICATED` error variant (pinned commit 0c22029c2af47d3829e730e9820c01cef0557627, checked October 2026): https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L79-L135
- Hasura GraphQL endpoint admin secret (pinned commit 216ee9a960a54181dabc2257a2e7925a1fb87bbd, checked October 2026): https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/deployment/securing-graphql-endpoint.mdx#L14-L15
- Hasura authentication overview and JWT mode (pinned commit 216ee9a960a54181dabc2257a2e7925a1fb87bbd, checked October 2026): https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/auth/overview.mdx#L63-L66
- gRPC SSL/TLS server and mutual authentication (pinned commit d90b5f947a481a063a6eae7043a8891c910762a8, checked October 2026): https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L23-L26
- gRPC token-based authentication with SSL/TLS (pinned commit d90b5f947a481a063a6eae7043a8891c910762a8, checked October 2026): https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L38-L46
- gRPC channel, call and composite credentials (pinned commit d90b5f947a481a063a6eae7043a8891c910762a8, checked October 2026): https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L62-L74
- gRPC OAuth per-call credentials and server-side verification (pinned commit d90b5f947a481a063a6eae7043a8891c910762a8, checked October 2026): https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L122-L131
- grpc-go authentication example, server-side token verification in an interceptor (v1.82.2, checked October 2026): https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/README.md#L49-L62
- grpc-go authentication example server installing a unary interceptor (v1.82.2, checked October 2026): https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/server/main.go#L57-L65
- go-grpc-middleware unary auth interceptor and AuthFuncOverride (v2.3.3, checked October 2026): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L26-L50
- go-grpc-middleware stream auth interceptor and AuthFuncOverride (v2.3.3, checked October 2026): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L52-L70
- vLLM gRPC server without an interceptor on an insecure port (v0.30.0, checked October 2026): https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/grpc_server.py#L87-L118
- Triton gRPC restricted-protocol header check (pinned commit 546a78766fb112128aa0b10a70c55f4f39c3b1df, checked October 2026): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.cc#L194-L225
- Argo CD gRPC interceptor chains (pinned commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579, checked October 2026): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L961-L985
- Argo CD authentication function, disabled auth and anonymous access (pinned commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579, checked October 2026): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1537-L1576
- Argo CD import of the `go-grpc-middleware/v2` auth interceptors (pinned commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579, checked October 2026): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L37
- Text Embeddings Inference gRPC API-key interceptor (pinned commit 1bb59202500e5f69dd8be63dd1604f7625124fbe, checked October 2026): https://github.com/huggingface/text-embeddings-inference/blob/1bb59202500e5f69dd8be63dd1604f7625124fbe/router/src/grpc/server.rs#L1472-L1508
- Git log patch and merge-diff behaviour (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L127-L141
- Git log default revision range (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L102-L109
- Gitleaks Git, directory and stdin modes (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L193-L215
- Gitleaks pre-commit use (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L110-L134
- Gitleaks git command staged, pre-commit and log-opts flags (v8.30.1, checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L14-L20
- Gitleaks staged diff versus log command selection (v8.30.1, checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L64-L77
- Git rev-list --all refs listing (checked October 2026): https://github.com/git/git/blob/v2.56.0/Documentation/rev-list-options.adoc#L167-L169
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
- Microsoft Entra account disablement and refresh-token revocation (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L96-L106
- Microsoft Entra access-token lifetime (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/access-tokens.md#L54-L60
- Microsoft Entra continuous access evaluation delay (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/concept-continuous-access-evaluation.md#L21-L25
- Cloudflare Access session revocation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L159-L186
- Cloudflare Access user logout delay (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L190-L195
- OAuth2 Proxy cookie expiry and refresh (v7.15.4, checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L126-L130
- OAuth2 Proxy trusted proxy IPs (v7.15.4, checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L197
- OAuth2 Proxy upstream identity headers (v7.15.4, checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L143-L151
- Authelia session authorization (v4.39.28, checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L24-L25
- Authelia session expiration (v4.39.28, checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L220-L221
- OAuth 2.0 token revocation (RFC 7009) (checked October 2026): https://www.rfc-editor.org/rfc/rfc7009.html#section-2.1
- Google IAP signed-header verification (checked October 2026): https://docs.cloud.google.com/iap/docs/signed-headers-howto#securing_iap_headers
- AWS ALB signed claims verification (checked October 2026): https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html#user-claims-encoding
- Google OpenID Connect hosted-domain claim (checked October 2026): https://developers.google.com/identity/openid-connect/openid-connect
- Microsoft Entra multitenant common endpoint and issuer handling (pinned commit 49b84e07023770128d83039c07eafb84ff1de1df, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/howto-convert-app-to-be-multi-tenant.md#L43-L63
- Microsoft Entra multitenant token validation (pinned commit 49b84e07023770128d83039c07eafb84ff1de1df, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/49b84e07023770128d83039c07eafb84ff1de1df/docs/identity-platform/access-tokens.md#L179-L187
- Cloudflare Access self-hosted application (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16
- Cloudflare Access origin connection and token validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54
- Cloudflare Access JWT validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L15-L17
- Cloudflare Tunnel origin parameters (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L198-L206
- Cloudflare Full (strict) SSL mode (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L16-L37
- Cloudflare Tunnel origin TLS verification (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L59-L67
- Cloudflare identity provider options (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/index.mdx#L14-L18
- Cloudflare generic OIDC connector (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/generic-oidc.mdx#L15
- Cloudflare Access one-time PIN login (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- owasp: OWASP authentication and password storage (unknown)
- owasp-p1: OWASP authorization, secrets and session guidance (668ba7db3d0da5868b8a0305c259f7f6914a6ecd)
- oauth: OAuth security BCP (RFC 9700)
- oidc: OpenID Connect Core (1.0)
- nist: NIST password guidance (SP 800-63B-4)
- htpasswd: Apache htpasswd (unknown)
- bcrypt: Python bcrypt rejection threshold (5.0.0)
- bcrypt-source: Python bcrypt changelog (2b4ba9ac84df972e8e81311d09559af8dc82ef33)
- openssl: OpenSSL rand (3.5)
- python: Python secrets (3.13)
- gitleaks-source: Gitleaks scanning modes (b58d3f102cf3a2c84cb7f923d05c25c9b1aed84b)
- git: Git ignore rules (v2.49.0)
- owasp-docs: OWASP security guidance (668ba7db3d0da5868b8a0305c259f7f6914a6ecd)
- api-security: OWASP API Security (2023)
- google-oidc: Google OpenID Connect (unknown)
- entra-multitenant: Microsoft Entra multitenant token validation (49b84e07023770128d83039c07eafb84ff1de1df)
- cloudflare-access: Cloudflare Access and origin configuration (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- fail2ban-jail: fail2ban (1.1.1)
- grpc-status: gRPC (v1.84.0)
- websocket-rfc: WebSocket RFC (RFC 6455)
- sse-spec: WHATWG server-sent events (unknown)
- stripe-webhooks: stripe-node (v18.5.0)
- git-log: Git (v2.56.0)
- gitleaks-p3: Gitleaks (v8.30.1)
- entra-docs: Microsoft Entra revocation model (231747abc59ae3d50c74e215c1cdd592eb980723)
- oauth2-proxy: OAuth2 Proxy (v7.15.4)
- authelia: Authelia (v4.39.28)
- oauth-revocation: OAuth 2.0 Token Revocation RFC (unknown)
- google-iap: Google Identity-Aware Proxy (unknown)
- aws-alb: AWS Application Load Balancer authentication (unknown)
- standard-webhooks: Standard Webhooks (7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b)
- graphql-docs: GraphQL authorization and serving documentation (be061651a39b9b85115bf3e430d516eab9610cee)
- grpc-auth: gRPC authentication guide (d90b5f947a481a063a6eae7043a8891c910762a8)
- graphql-over-http: GraphQL over HTTP working draft (d438b209d60fa3d34b0530b605e60d5640c7ef9b)
- apollo-server: Apollo Server documentation (0c22029c2af47d3829e730e9820c01cef0557627)
- hasura: Hasura GraphQL Engine documentation (216ee9a960a54181dabc2257a2e7925a1fb87bbd)
- grpc-go-example: grpc-go authentication example (v1.82.2)
- grpc-middleware: go-grpc-middleware (v2.3.3)
- vllm: vLLM (v0.30.0)
- triton: Triton Inference Server (546a78766fb112128aa0b10a70c55f4f39c3b1df)
- argo-cd: Argo CD (c9c369efcc5b2a0bd720803f8d14a1c3eaddf579)
- tei-grpc: Text Embeddings Inference (1bb59202500e5f69dd8be63dd1604f7625124fbe)

Claims (full source mapping in the JSON block below):

- tls (REASONED; owasp, oauth): Protect the login page and whole session with TLS or equivalent strong transport; Basic and bearer credentials require HTTPS.
- password-hashing (REASONED; owasp): Prefer argon2id, then scrypt; bcrypt is legacy and parameterized PBKDF2 serves FIPS requirements. Never use plaintext, unsalted or fast password hashes.
- bcrypt-length (REASONED; bcrypt, bcrypt-source, owasp): bcrypt limits input to 72 bytes; Python bcrypt 5.0.0+ raises ValueError while earlier versions truncate. Prefer argon2id or scrypt for long passphrases.
- bcrypt-prehash (REASONED; owasp): If legacy bcrypt is unavoidable, pre-hash with peppered HMAC then base64, never a bare digest susceptible to password shucking.
- htpasswd-cost (REASONED; htpasswd, owasp): htpasswd -B -C 12 selects bcrypt cost 12; bare -B defaults to 5, below the OWASP minimum of 10.
- federation (REASONED; owasp, oidc): Prefer supported SSO/OIDC and enable MFA wherever available.
- machine-tokens (REASONED; oauth): Use separate least-privilege API tokens, exercise rotation and set expiry where supported.
- session-identity (REASONED; owasp, owasp-docs): Use unpredictable session identifiers and regenerate on login or privilege change, invalidating the old identifier.
- session-revocation (REASONED; owasp, owasp-docs): Invalidate sessions server-side on logout and password change.
- login-throttling (REASONED; owasp): Rate-limit authentication with account-aware and aggregate controls alongside source limits; lock or delay failures without enabling denial of access.
- enumeration (REASONED; owasp): Keep login, registration and reset responses uniform in message and timing.
- auth-logging (REASONED; owasp): Log authentication successes and failures with account and source address; retain logs for investigation.
- privilege (REASONED; owasp): Separate administrative and daily-use accounts; restrict database and OS service accounts to the rights the application uses.
- authorization (REASONED; oidc, oauth): A federated identity still needs an application allowlist before access is granted. The allowlist is this guide's recommendation.
- code-pkce (REASONED; oauth): Use authorization code flow with PKCE S256, never plain.
- redirects (REASONED; oauth): Require exact-match redirect URIs.
- state-nonce (REASONED; oauth, oidc): Generate fresh state and nonce for each transaction, verify both and bind them to the initiating browser session.
- id-token-signature (REASONED; oidc): Validate ID-token signatures with provider JWKS and a pinned algorithm, never none.
- id-token-claims (REASONED; oidc): Validate ID-token issuer, audience and expiry before accepting the identity.
- token-lifecycle (REASONED; oauth): Use short-lived access tokens and refresh-token rotation; never put tokens in URLs.
- account-linking (REASONED; oidc): Link accounts by issuer plus subject, never by email alone.
- mfa-enforcement (REASONED; owasp, nist): Require MFA at the point of access in provider policy or the app; enrollment alone must not permit password-only access.
- control-plane (REASONED; owasp, nist): Require MFA on the Git host, cloud, DNS, deployment platform, secret manager and IdP administrator account.
- password-length (REASONED; nist): Require at least 8 password characters with enforced MFA, otherwise at least 15; allow long passphrases and all characters without composition or periodic-rotation rules.
- breached-passwords (REASONED; nist, owasp): Screen new and changed passwords against known breaches; a valid breached password defeats hashing and per-IP limits.
- recovery (REASONED; nist, owasp): Use random, single-use, short-lived, account-bound reset tokens and a pre-verified delivery channel; recovery must preserve MFA.
- recovery-reauth (REASONED; nist, owasp): Reauthenticate for recovery-address or MFA-factor changes and invalidate outstanding sessions and unused reset tokens on completion.
- verify-token-rejection (REASONED; oidc, oauth): Negative tests reject missing, expired, wrong-issuer and wrong-audience tokens.
- default-deny (REASONED; owasp, owasp-p1): Every endpoint that is not deliberately public must require authentication, applying OWASP's deny-by-default principle. Require authentication for APIs, health dashboards, admin panels, metrics, and message queues, and publish an explicit list of public paths (this guide's recommendation; the cited passage does not cover this).
- individual-credentials (REASONED; owasp, owasp-p1): Change or disable every vendor default account before exposure. Each human gets an individual account; each service gets its own credential. Never ship credentials in code, containers or documentation. OWASP notes that services sharing one secret make the source of a compromise or leak hard to identify; vendor default accounts, individual human and service credentials, and keeping credentials out of code, containers and documentation are this guide's recommendations.
- secret-generation (REASONED; owasp, openssl, python): Generate random secrets with openssl rand -base64 32 or Python secrets.token_urlsafe(32).
- secret-storage (REASONED; owasp, gitleaks-source, git, owasp-docs, owasp-p1): Prefer a secret manager (this guide's recommendation; OWASP lists secret managers as one option). For containers, OWASP advises environment variables only when mounted files or a secret-store fetch are not possible. Ignore .env before the first commit and scan for leaks before pushing. Rotate secrets exposed in a public repository, chat or log; deletion does not unpublish them.
- session-cookies (REASONED; owasp, owasp-docs, owasp-p1): Mark session cookies Secure, HttpOnly and SameSite Lax or Strict; signing them with a strong random secret is this guide's recommendation, not covered by the cited passage.
- session-timeouts (REASONED; owasp, owasp-docs): Enforce both idle and absolute session timeouts server-side; cookie expiry alone does not prevent replay.
- session-unissued (REASONED; owasp, owasp-docs): Reject session identifiers the server never issued to prevent session fixation.
- csrf (REASONED; owasp, owasp-docs): SameSite alone is not a complete CSRF defense: Lax permits a top-level state-changing GET and sibling subdomains can be same-site. Cookie-authenticated state changes need an anti-CSRF token or strict Origin/Sec-Fetch-Site check, and must not use safe methods such as GET.
- expensive-endpoint-limits (REASONED; owasp, api-security, owasp-docs): Bound inference, uploads and job submission with request-size, concurrency and timeout limits in addition to per-client rate limits; apply these limits to streaming and webhook transports too.
- fail2ban (REASONED; owasp, fail2ban-jail): For SSH on Linux hosts, enable the relevant fail2ban jail (guide requirement). fail2ban 1.1.1 ships sshd, nginx-http-auth and webmin-auth filters and jails, with jails disabled by default; enabling relevant jails with matching file-backend logpaths is guide advice, while panel coverage and setup ease remain unestablished (guide assessment).
- federated-allowlist (REASONED; oidc, google-oidc, entra-multitenant): After federated login, check the identity against an application allowlist of tenants, hosted domains, organization or group membership, or explicit users (this guide's recommendation); a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the hd claim in the validated ID token; an email domain or request hd parameter is insufficient. Microsoft common serves organizational and personal accounts; validate the token issuer, signing-key issuer and tid, then apply the application tenant allowlist. Vendor sources support the Google hd check and Microsoft token validation; the full allowlist and staff determination are this guide's recommendations.
- cloudflare-access (REASONED; cloudflare-access): Cloudflare Access can front a self-hosted web application published through Access with one-time PIN or SSO login; create the Access application before the tunnel route, or it is available to anyone on the Internet. Validate the Access JWT at the origin, verify Tunnel origin TLS, and use Full (strict) for a directly proxied HTTPS origin where applicable; unchanged any-application use is not established.
- browser-session (REASONED; owasp, owasp-docs): Prefer a server-side session in an HttpOnly cookie to tokens in browser storage.
- transport-authentication (REASONED; owasp, websocket-rfc, sse-spec, grpc-status, stripe-webhooks, owasp-docs, standard-webhooks, graphql-docs, grpc-auth): Guide requirements: WebSockets, SSE, GraphQL, gRPC, webhooks, inference/management APIs need their own authentication check, not HTML login; verify webhook signatures; reject replays, even in-window. Sources are guidance. Unestablished (guide assessment): GraphQL credentials/checks/non-HTTP auth, HTML-login and non-REST inference/management boundaries, full replay rejection, deployed protection.
- transport-authentication-sources (REASONED; graphql-docs, grpc-auth): Cited guidance: GraphQL docs say execution should begin after authentication middleware confirms user identity, which their example puts in request context, and that business logic should handle authorization; gRPC's guide separates channel credentials, such as SSL credentials, from call credentials, which can be combined. Applying gRPC credentials to inference/management APIs is guide inference.
- transport-authentication-browser (REASONED; websocket-rfc, owasp-docs, sse-spec): Documented: RFC 6455 leaves WebSocket handshake authentication to servers, which may use cookies, HTTP or TLS authentication, and site-restricted servers SHOULD verify Origin; OWASP says browsers send handshake cookies and to validate Origin by allowlist. Documented: WHATWG EventSource sets credentials mode include if withCredentials is true; whether endpoints check them is guide assessment.
- transport-authentication-graphql (REASONED; graphql-docs, graphql-over-http, apollo-server, hasura): Documented: graphql.org says to place GraphQL after all authentication middleware, sharing other HTTP handlers' session and user information; the GraphQL over HTTP draft lets a server forbid requests to require authentication and leaves authentication security out of scope. Apollo and Hasura are vendor examples only. Accepted credentials and middleware checks remain guide requirements.
- transport-authentication-grpc (REASONED; grpc-go-example, grpc-middleware, vllm, triton, tei-grpc): Cited example: the grpc-go authentication example's server verifies call credentials in an interceptor it installs. Source reading: go-grpc-middleware runs an application AuthFunc or service override per call; vLLM v0.30.0 gRPC has no interceptor; TEI checks authorization only with an API key; Triton checks configured restricted headers.
- transport-authentication-grpc-argo-cd (REASONED; argo-cd, grpc-middleware): Source reading: argocd-server's default gRPC auth function skips checks if auth is off, else tries the token; on a claims error it allows the call anonymously only if settings load with anonymous access on. Service overrides are excluded: go-grpc-middleware v2.3.3 (Argo CD's go.mod pin per gitops-controllers.md) runs them instead; that guide records overrides accepting some unauthenticated calls.
- offboarding (REASONED; owasp, oauth, owasp-docs, entra-docs, cloudflare-access, oauth2-proxy, authelia, oauth-revocation): When a person leaves, promptly revoke their provider membership, proxy sessions, application sessions, and personal tokens (this guide's recommendation). Entra documents blocking new sign-ins and revoking refresh tokens, while application-issued sessions require revocation by the application; its access-token lifetime varies, and CAE critical-event enforcement can take up to 15 minutes for supported services. Cloudflare Access documents per-user session revocation, but an active IdP profile can start a new session; after user logout, previously issued tokens stop being accepted in 20-30 seconds. OAuth2 Proxy and Authelia document session-cookie expiry, but these passages do not establish immediate per-user revocation for either proxy. RFC 7009 specifies immediate token invalidation with possible propagation delay and conditional access-token revocation support. The fetched sources do not establish a provider-membership removal mechanism or this deployment's measured maximum time-to-revoke. Measure each system's maximum time-to-revoke where immediate revocation is unavailable, and work to shrink it (this guide's recommendation; no delay was measured here). In a deployment test, first confirm that a matched request with each provider, proxy and application session and personal token succeeds against a protected resource. After revocation, replay each old credential at recorded intervals until it is refused and returns no protected data, and the elapsed time for every layer must not exceed its configured maximum time-to-revoke; these are test expectations, not observed results.
- verify-transports (REASONED; owasp, grpc-status, websocket-rfc, sse-spec): Use real protocol clients against every non-public path and transport: expect HTTP 401, 403 or a login redirect; gRPC UNAUTHENTICATED for missing or invalid credentials (PERMISSION_DENIED for an identified caller lacking permission); SSE refusal; and WebSocket upgrade rejection or protected-operation rejection, no protected data disclosure, and closure on first-message authentication failure. A bare curl GET does not test non-HTTP transports. These are test expectations, not observed responses.
- verify-secret-scan (REASONED; owasp, gitleaks-source, gitleaks-p3, git-log): A secret scanner must find no leaks in the working tree, staged changes and full history; Gitleaks v8.30.1 provides staged git-diff flags and `--log-opts`, so verify staged, all-ref and merge-commit coverage with the chosen scanner and configuration. Supplementary git log grep misses secrets without the search words, uncommitted files, some refs and merge-only changes; the historical fixture result is not a scan of this repository.
- verify-default-accounts (REASONED; owasp): Check that the user store has no admin, test or demo account with a known or empty password. This is the guide's recommendation; the OWASP Authentication Cheat Sheet does not list these account names (checked at commit 72865b1e).
- verify-wrong-tenant (REASONED; oidc, entra-multitenant): Expect a wrong-tenant token to be rejected in an application negative test after issuer and tid validation and the application tenant allowlist. Microsoft documents the validation rules; this guide recommends the allowlist and test, and no deployed rejection was observed.
- verify-cross-user (REASONED; owasp, owasp-p1): Verify that user A cannot read user B's resources. OWASP describes horizontal privilege escalation and object-specific access checks.
- verify-origin-isolation (REASONED; owasp, cloudflare-access, oauth2-proxy, authelia, google-iap, aws-alb): Expect the origin to be unreachable except through its fronting layer in a deployment negative test. Cloudflare describes Access policy enforcement, JWT validation and Tunnel access checks, and says a publicly routable origin needs its IP protected by other methods. OAuth2 Proxy documents upstream identity headers and warns that when `--reverse-proxy` is enabled and `--trusted-proxy-ip` is unset, a client that can reach OAuth2 Proxy directly may be able to spoof forwarded headers. Authelia uses session cookies to authorize protected websites. Google IAP says a bypassing attacker can forge unsigned identity headers; its signed-header how-to says to verify the JWT header, payload and signature to secure an app with the IAP JWT, and calls signed headers secondary security; AWS ALB requires verification of its signed claims header and signer ARN. These sources support the guide's origin-isolation test expectation but do not establish that a particular origin is unreachable.

````json
{
  "schema": 1,
  "checked": "2026-10-21",
  "documentation_checked": "2026-09",
  "body_sha256": "911dd4ec08794cdb314ae25177644ef41ce2369e7d66b2a09d5b6c2504add616",
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
        "sd6d35bd1b67d": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Denial_of_Service_Cheat_Sheet.md#L110-L113",
        "sb49221f05748": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L190-L198",
        "s0eccd394429a": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/GraphQL_Cheat_Sheet.md#L287-L290",
        "se53dcf51421a": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L35-L38",
        "s2cddbc943d5f": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/REST_Security_Cheat_Sheet.md#L167-L170",
        "s6d4b22f77307": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L118-L120",
        "sf288957942f5": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L128",
        "s5f89a38f97e4": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L74",
        "sf12da7bc5eb6": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/WebSocket_Security_Cheat_Sheet.md#L85"
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
      "basis": "unknown",
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
        "sbf4ecbd5ffc1": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L16-L37",
        "sf2dbab0fc574": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L159-L186",
        "sa0e3eb928f4a": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L190-L195",
        "scb7d48f64a99": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/index.mdx#L14-L18",
        "sd606ae12de33": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/generic-oidc.mdx#L15",
        "s9f8bead847d2": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15"
      }
    },
    "fail2ban-jail": {
      "name": "fail2ban",
      "basis": "1.1.1",
      "sources": {
        "se7c4e0af046f": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L152-L167",
        "sc1b6e6bc1f84": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L271-L279",
        "s9a6aaa273c73": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/sshd.conf#L104-L111",
        "sa43cf7ba22fb": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L370-L376",
        "s568ea00c2482": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-http-auth.conf#L9-L37",
        "s3c53dd330a7b": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L491-L495",
        "s099abd84ea19": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/webmin-auth.conf#L4-L20"
      }
    },
    "grpc-status": {
      "name": "gRPC",
      "basis": "v1.84.0",
      "sources": {
        "s595c3c297157": "https://github.com/grpc/grpc/blob/v1.84.0/doc/statuscodes.md#L13-L24"
      }
    },
    "websocket-rfc": {
      "name": "WebSocket RFC",
      "basis": "RFC 6455",
      "sources": {
        "s07f03be17365": "https://www.rfc-editor.org/rfc/rfc6455.html#section-1.3",
        "s559dc201b043": "https://www.rfc-editor.org/rfc/rfc6455.html#section-1.4",
        "s1cf26aa107f9": "https://www.rfc-editor.org/rfc/rfc6455.html#section-10.5",
        "s6b9238cd4790": "https://www.rfc-editor.org/rfc/rfc6455.html#section-10.2"
      }
    },
    "sse-spec": {
      "name": "WHATWG server-sent events",
      "basis": "unknown",
      "sources": {
        "sf47a21cc6a1c": "https://html.spec.whatwg.org/multipage/server-sent-events.html"
      }
    },
    "stripe-webhooks": {
      "name": "stripe-node",
      "basis": "v18.5.0",
      "sources": {
        "s42eea6a7e527": "https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L182-L216",
        "s90f21ad845ca": "https://github.com/stripe/stripe-node/blob/v18.5.0/src/Webhooks.ts#L357-L410"
      }
    },
    "git-log": {
      "name": "Git",
      "basis": "v2.56.0",
      "sources": {
        "s1cb7f677894d": "https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L127-L141",
        "sede4bb3fcdf3": "https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L102-L109",
        "s903a3c765e70": "https://github.com/git/git/blob/v2.56.0/Documentation/rev-list-options.adoc#L167-L169"
      }
    },
    "gitleaks-p3": {
      "name": "Gitleaks",
      "basis": "v8.30.1",
      "sources": {
        "se5afdb7c63d2": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L193-L215",
        "s685ae6ce9b3d": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L110-L134",
        "sfda707f0eb4f": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L14-L20",
        "s8511b8f313b7": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L64-L77"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra revocation model",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s983f45259faa": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62",
        "scb38e683ae3f": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L96-L106",
        "s9ff4d6ed4cfe": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/access-tokens.md#L54-L60",
        "sca6feea4b601": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/concept-continuous-access-evaluation.md#L21-L25"
      }
    },
    "oauth2-proxy": {
      "name": "OAuth2 Proxy",
      "basis": "v7.15.4",
      "sources": {
        "s32cedbc14f60": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L126-L130",
        "s17f0d3cc09b1": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L197",
        "s6de4892223d2": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L143-L151"
      }
    },
    "authelia": {
      "name": "Authelia",
      "basis": "v4.39.28",
      "sources": {
        "sc03548e2ed00": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L24-L25",
        "sc844fe82794f": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L220-L221"
      }
    },
    "oauth-revocation": {
      "name": "OAuth 2.0 Token Revocation RFC",
      "basis": "unknown",
      "sources": {
        "s3383c9f41cc2": "https://www.rfc-editor.org/rfc/rfc7009.html#section-2.1"
      }
    },
    "google-iap": {
      "name": "Google Identity-Aware Proxy",
      "basis": "unknown",
      "sources": {
        "s4513609280bb": "https://docs.cloud.google.com/iap/docs/signed-headers-howto#securing_iap_headers"
      }
    },
    "aws-alb": {
      "name": "AWS Application Load Balancer authentication",
      "basis": "unknown",
      "sources": {
        "sa198710d31f3": "https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html#user-claims-encoding"
      }
    },
    "standard-webhooks": {
      "name": "Standard Webhooks",
      "basis": "7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b",
      "sources": {
        "seaefbbec338e": "https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L133-L143",
        "s63e0d131d760": "https://github.com/standard-webhooks/standard-webhooks/blob/7537d2a2d3d52d8f2e0ecd12527af4a9307fd81b/spec/standard-webhooks.md#L233-L234"
      }
    },
    "graphql-docs": {
      "name": "GraphQL authorization and serving documentation",
      "basis": "be061651a39b9b85115bf3e430d516eab9610cee",
      "sources": {
        "s3df4f55b0bea": "https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L5",
        "s199bd5e58cf1": "https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L22",
        "sc5afee295dec": "https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/authorization.mdx#L89-L92",
        "s18851e342534": "https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L21",
        "s578f7bbdabd6": "https://github.com/graphql/graphql.github.io/blob/be061651a39b9b85115bf3e430d516eab9610cee/src/pages/learn/serving-over-http.mdx#L132"
      }
    },
    "grpc-auth": {
      "name": "gRPC authentication guide",
      "basis": "d90b5f947a481a063a6eae7043a8891c910762a8",
      "sources": {
        "s362a756f8895": "https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L23-L26",
        "sbc5e08ab0a2f": "https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L38-L46",
        "s95d08dc70fee": "https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L62-L74",
        "s82eaa71eceda": "https://github.com/grpc/grpc.io/blob/d90b5f947a481a063a6eae7043a8891c910762a8/content/en/docs/guides/auth.md#L122-L131"
      }
    },
    "graphql-over-http": {
      "name": "GraphQL over HTTP working draft",
      "basis": "d438b209d60fa3d34b0530b605e60d5640c7ef9b",
      "sources": {
        "s868371971ab7": "https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L115-L118",
        "sc0111d7924ae": "https://github.com/graphql/graphql-over-http/blob/d438b209d60fa3d34b0530b605e60d5640c7ef9b/spec/GraphQLOverHTTP.md#L705-L720"
      }
    },
    "apollo-server": {
      "name": "Apollo Server documentation",
      "basis": "0c22029c2af47d3829e730e9820c01cef0557627",
      "sources": {
        "s42ab6a721b3b": "https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L25-L62",
        "sca37b76cac23": "https://github.com/apollographql/apollo-server/blob/0c22029c2af47d3829e730e9820c01cef0557627/docs/source/security/authentication.mdx#L79-L135"
      }
    },
    "hasura": {
      "name": "Hasura GraphQL Engine documentation",
      "basis": "216ee9a960a54181dabc2257a2e7925a1fb87bbd",
      "sources": {
        "sbdbe33edb8ca": "https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/deployment/securing-graphql-endpoint.mdx#L14-L15",
        "s9a644965f6c1": "https://github.com/hasura/graphql-engine/blob/216ee9a960a54181dabc2257a2e7925a1fb87bbd/docs/docs/auth/overview.mdx#L63-L66"
      }
    },
    "grpc-go-example": {
      "name": "grpc-go authentication example",
      "basis": "v1.82.2",
      "sources": {
        "sf3a4641f924b": "https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/README.md#L49-L62",
        "s7e5cc4ea3d23": "https://github.com/grpc/grpc-go/blob/v1.82.2/examples/features/authentication/server/main.go#L57-L65"
      }
    },
    "grpc-middleware": {
      "name": "go-grpc-middleware",
      "basis": "v2.3.3",
      "sources": {
        "s9ec5783f5bab": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L26-L50",
        "s4413e7e06e93": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L52-L70"
      }
    },
    "vllm": {
      "name": "vLLM",
      "basis": "v0.30.0",
      "sources": {
        "sb6766a13ce4a": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/grpc_server.py#L87-L118"
      }
    },
    "triton": {
      "name": "Triton Inference Server",
      "basis": "546a78766fb112128aa0b10a70c55f4f39c3b1df",
      "sources": {
        "s2f7f38a83db9": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.cc#L194-L225"
      }
    },
    "argo-cd": {
      "name": "Argo CD",
      "basis": "c9c369efcc5b2a0bd720803f8d14a1c3eaddf579",
      "sources": {
        "s751b24797922": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L961-L985",
        "s2bf01b29602c": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1537-L1576",
        "s19e9d1a1d4d2": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L37"
      }
    },
    "tei-grpc": {
      "name": "Text Embeddings Inference",
      "basis": "1bb59202500e5f69dd8be63dd1604f7625124fbe",
      "sources": {
        "scaa009c6db41": "https://github.com/huggingface/text-embeddings-inference/blob/1bb59202500e5f69dd8be63dd1604f7625124fbe/router/src/grpc/server.rs#L1472-L1508"
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
    "authorization": {"text": "A federated identity still needs an application allowlist before access is granted. The allowlist is this guide's recommendation.", "components": ["oidc", "oauth"], "sources": ["oidc:scfd2790a544c", "oauth:s4e6d674bf887"], "status": "REASONED"},
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
    "fail2ban": {"text": "For SSH on Linux hosts, enable the relevant fail2ban jail (guide requirement). fail2ban 1.1.1 ships sshd, nginx-http-auth and webmin-auth filters and jails, with jails disabled by default; enabling relevant jails with matching file-backend logpaths is guide advice, while panel coverage and setup ease remain unestablished (guide assessment).", "components": ["owasp", "fail2ban-jail"], "sources": ["owasp:sc5f1b11d42f4", "fail2ban-jail:se7c4e0af046f", "fail2ban-jail:sc1b6e6bc1f84", "fail2ban-jail:s9a6aaa273c73", "fail2ban-jail:sa43cf7ba22fb", "fail2ban-jail:s568ea00c2482", "fail2ban-jail:s3c53dd330a7b", "fail2ban-jail:s099abd84ea19"], "status": "REASONED"},
    "federated-allowlist": {"text": "After federated login, check the identity against an application allowlist of tenants, hosted domains, organization or group membership, or explicit users (this guide's recommendation); a Google sign-in alone does not make someone staff. For Google Workspace or Cloud organizations, check the hd claim in the validated ID token; an email domain or request hd parameter is insufficient. Microsoft common serves organizational and personal accounts; validate the token issuer, signing-key issuer and tid, then apply the application tenant allowlist. Vendor sources support the Google hd check and Microsoft token validation; the full allowlist and staff determination are this guide's recommendations.", "components": ["oidc", "google-oidc", "entra-multitenant"], "sources": ["oidc:scfd2790a544c", "google-oidc:s4f815acc2976", "entra-multitenant:s5e0242f87cb7", "entra-multitenant:s95719206c226"], "status": "REASONED"},
    "cloudflare-access": {"text": "Cloudflare Access can front a self-hosted web application published through Access with one-time PIN or SSO login; create the Access application before the tunnel route, or it is available to anyone on the Internet. Validate the Access JWT at the origin, verify Tunnel origin TLS, and use Full (strict) for a directly proxied HTTPS origin where applicable; unchanged any-application use is not established.", "components": ["cloudflare-access"], "sources": ["cloudflare-access:sfddb92e438ca", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:s81e5dd28d3e5", "cloudflare-access:s65c224a2e655", "cloudflare-access:sa012410f91eb", "cloudflare-access:sbf4ecbd5ffc1", "cloudflare-access:scb7d48f64a99", "cloudflare-access:sd606ae12de33", "cloudflare-access:s9f8bead847d2"], "status": "REASONED"},
    "browser-session": {"text": "Prefer a server-side session in an HttpOnly cookie to tokens in browser storage.", "components": ["owasp", "owasp-docs"], "sources": ["owasp:sc5f1b11d42f4", "owasp-docs:s4f0aa80b1ef6"], "status": "REASONED"},
    "transport-authentication": {"text": "Guide requirements: WebSockets, SSE, GraphQL, gRPC, webhooks, inference/management APIs need their own authentication check, not HTML login; verify webhook signatures; reject replays, even in-window. Sources are guidance. Unestablished (guide assessment): GraphQL credentials/checks/non-HTTP auth, HTML-login and non-REST inference/management boundaries, full replay rejection, deployed protection.", "components": ["owasp", "websocket-rfc", "sse-spec", "grpc-status", "stripe-webhooks", "owasp-docs", "standard-webhooks", "graphql-docs", "grpc-auth"], "sources": ["owasp:sc5f1b11d42f4", "websocket-rfc:s07f03be17365", "websocket-rfc:s559dc201b043", "sse-spec:sf47a21cc6a1c", "grpc-status:s595c3c297157", "stripe-webhooks:s42eea6a7e527", "stripe-webhooks:s90f21ad845ca", "owasp-docs:sb49221f05748", "owasp-docs:s0eccd394429a", "owasp-docs:se53dcf51421a", "owasp-docs:s2cddbc943d5f", "owasp-docs:s6d4b22f77307", "owasp-docs:sf288957942f5", "standard-webhooks:seaefbbec338e", "standard-webhooks:s63e0d131d760", "graphql-docs:s3df4f55b0bea", "graphql-docs:s199bd5e58cf1", "graphql-docs:sc5afee295dec", "grpc-auth:s362a756f8895", "grpc-auth:sbc5e08ab0a2f", "grpc-auth:s95d08dc70fee", "grpc-auth:s82eaa71eceda"], "status": "REASONED"},
    "transport-authentication-sources": {"text": "Cited guidance: GraphQL docs say execution should begin after authentication middleware confirms user identity, which their example puts in request context, and that business logic should handle authorization; gRPC's guide separates channel credentials, such as SSL credentials, from call credentials, which can be combined. Applying gRPC credentials to inference/management APIs is guide inference.", "components": ["graphql-docs", "grpc-auth"], "sources": ["graphql-docs:s3df4f55b0bea", "graphql-docs:s199bd5e58cf1", "graphql-docs:sc5afee295dec", "grpc-auth:s362a756f8895", "grpc-auth:s95d08dc70fee"], "status": "REASONED"},
    "transport-authentication-browser": {"text": "Documented: RFC 6455 leaves WebSocket handshake authentication to servers, which may use cookies, HTTP or TLS authentication, and site-restricted servers SHOULD verify Origin; OWASP says browsers send handshake cookies and to validate Origin by allowlist. Documented: WHATWG EventSource sets credentials mode include if withCredentials is true; whether endpoints check them is guide assessment.", "components": ["websocket-rfc", "owasp-docs", "sse-spec"], "sources": ["websocket-rfc:s1cf26aa107f9", "websocket-rfc:s6b9238cd4790", "owasp-docs:s5f89a38f97e4", "owasp-docs:sf12da7bc5eb6", "sse-spec:sf47a21cc6a1c"], "status": "REASONED"},
    "transport-authentication-graphql": {"text": "Documented: graphql.org says to place GraphQL after all authentication middleware, sharing other HTTP handlers' session and user information; the GraphQL over HTTP draft lets a server forbid requests to require authentication and leaves authentication security out of scope. Apollo and Hasura are vendor examples only. Accepted credentials and middleware checks remain guide requirements.", "components": ["graphql-docs", "graphql-over-http", "apollo-server", "hasura"], "sources": ["graphql-docs:s18851e342534", "graphql-docs:s578f7bbdabd6", "graphql-over-http:s868371971ab7", "graphql-over-http:sc0111d7924ae", "apollo-server:s42ab6a721b3b", "apollo-server:sca37b76cac23", "hasura:sbdbe33edb8ca", "hasura:s9a644965f6c1"], "status": "REASONED"},
    "transport-authentication-grpc": {"text": "Cited example: the grpc-go authentication example's server verifies call credentials in an interceptor it installs. Source reading: go-grpc-middleware runs an application AuthFunc or service override per call; vLLM v0.30.0 gRPC has no interceptor; TEI checks authorization only with an API key; Triton checks configured restricted headers.", "components": ["grpc-go-example", "grpc-middleware", "vllm", "triton", "tei-grpc"], "sources": ["grpc-go-example:sf3a4641f924b", "grpc-go-example:s7e5cc4ea3d23", "grpc-middleware:s9ec5783f5bab", "grpc-middleware:s4413e7e06e93", "vllm:sb6766a13ce4a", "triton:s2f7f38a83db9", "tei-grpc:scaa009c6db41"], "status": "REASONED"},
    "transport-authentication-grpc-argo-cd": {"text": "Source reading: argocd-server's default gRPC auth function skips checks if auth is off, else tries the token; on a claims error it allows the call anonymously only if settings load with anonymous access on. Service overrides are excluded: go-grpc-middleware v2.3.3 (Argo CD's go.mod pin per gitops-controllers.md) runs them instead; that guide records overrides accepting some unauthenticated calls.", "components": ["argo-cd", "grpc-middleware"], "sources": ["argo-cd:s751b24797922", "argo-cd:s2bf01b29602c", "argo-cd:s19e9d1a1d4d2", "grpc-middleware:s9ec5783f5bab", "grpc-middleware:s4413e7e06e93"], "status": "REASONED"},
    "offboarding": {"text": "When a person leaves, promptly revoke their provider membership, proxy sessions, application sessions, and personal tokens (this guide's recommendation). Entra documents blocking new sign-ins and revoking refresh tokens, while application-issued sessions require revocation by the application; its access-token lifetime varies, and CAE critical-event enforcement can take up to 15 minutes for supported services. Cloudflare Access documents per-user session revocation, but an active IdP profile can start a new session; after user logout, previously issued tokens stop being accepted in 20-30 seconds. OAuth2 Proxy and Authelia document session-cookie expiry, but these passages do not establish immediate per-user revocation for either proxy. RFC 7009 specifies immediate token invalidation with possible propagation delay and conditional access-token revocation support. The fetched sources do not establish a provider-membership removal mechanism or this deployment's measured maximum time-to-revoke. Measure each system's maximum time-to-revoke where immediate revocation is unavailable, and work to shrink it (this guide's recommendation; no delay was measured here). In a deployment test, first confirm that a matched request with each provider, proxy and application session and personal token succeeds against a protected resource. After revocation, replay each old credential at recorded intervals until it is refused and returns no protected data, and the elapsed time for every layer must not exceed its configured maximum time-to-revoke; these are test expectations, not observed results.", "components": ["owasp", "oauth", "owasp-docs", "entra-docs", "cloudflare-access", "oauth2-proxy", "authelia", "oauth-revocation"], "sources": ["owasp:sc5f1b11d42f4", "oauth:s4e6d674bf887", "owasp-docs:seb866a1f94e9", "entra-docs:s983f45259faa", "entra-docs:scb38e683ae3f", "entra-docs:s9ff4d6ed4cfe", "entra-docs:sca6feea4b601", "cloudflare-access:sf2dbab0fc574", "cloudflare-access:sa0e3eb928f4a", "oauth2-proxy:s32cedbc14f60", "authelia:sc844fe82794f", "oauth-revocation:s3383c9f41cc2"], "status": "REASONED"},
    "verify-transports": {"text": "Use real protocol clients against every non-public path and transport: expect HTTP 401, 403 or a login redirect; gRPC UNAUTHENTICATED for missing or invalid credentials (PERMISSION_DENIED for an identified caller lacking permission); SSE refusal; and WebSocket upgrade rejection or protected-operation rejection, no protected data disclosure, and closure on first-message authentication failure. A bare curl GET does not test non-HTTP transports. These are test expectations, not observed responses.", "components": ["owasp", "grpc-status", "websocket-rfc", "sse-spec"], "sources": ["owasp:sc5f1b11d42f4", "grpc-status:s595c3c297157", "websocket-rfc:s07f03be17365", "websocket-rfc:s559dc201b043", "sse-spec:sf47a21cc6a1c"], "status": "REASONED"},
    "verify-secret-scan": {"text": "A secret scanner must find no leaks in the working tree, staged changes and full history; Gitleaks v8.30.1 provides staged git-diff flags and `--log-opts`, so verify staged, all-ref and merge-commit coverage with the chosen scanner and configuration. Supplementary git log grep misses secrets without the search words, uncommitted files, some refs and merge-only changes; the historical fixture result is not a scan of this repository.", "components": ["owasp", "gitleaks-source", "gitleaks-p3", "git-log"], "sources": ["owasp:sc5f1b11d42f4", "gitleaks-source:s44a3edaa543d", "gitleaks-p3:se5afdb7c63d2", "gitleaks-p3:s685ae6ce9b3d", "gitleaks-p3:sfda707f0eb4f", "gitleaks-p3:s8511b8f313b7", "git-log:s1cb7f677894d", "git-log:sede4bb3fcdf3", "git-log:s903a3c765e70"], "status": "REASONED"},
    "verify-default-accounts": {"text": "Check that the user store has no admin, test or demo account with a known or empty password. This is the guide's recommendation; the OWASP Authentication Cheat Sheet does not list these account names (checked at commit 72865b1e).", "components": ["owasp"], "sources": ["owasp:sc5f1b11d42f4"], "status": "REASONED"},
    "verify-wrong-tenant": {"text": "Expect a wrong-tenant token to be rejected in an application negative test after issuer and tid validation and the application tenant allowlist. Microsoft documents the validation rules; this guide recommends the allowlist and test, and no deployed rejection was observed.", "components": ["oidc", "entra-multitenant"], "sources": ["oidc:scfd2790a544c", "entra-multitenant:s95719206c226"], "status": "REASONED"},
    "verify-cross-user": {"text": "Verify that user A cannot read user B's resources. OWASP describes horizontal privilege escalation and object-specific access checks.", "components": ["owasp", "owasp-p1"], "sources": ["owasp:sc5f1b11d42f4", "owasp-p1:s5f5e10a9e4c2"], "status": "REASONED"},
    "verify-origin-isolation": {"text": "Expect the origin to be unreachable except through its fronting layer in a deployment negative test. Cloudflare describes Access policy enforcement, JWT validation and Tunnel access checks, and says a publicly routable origin needs its IP protected by other methods. OAuth2 Proxy documents upstream identity headers and warns that when `--reverse-proxy` is enabled and `--trusted-proxy-ip` is unset, a client that can reach OAuth2 Proxy directly may be able to spoof forwarded headers. Authelia uses session cookies to authorize protected websites. Google IAP says a bypassing attacker can forge unsigned identity headers; its signed-header how-to says to verify the JWT header, payload and signature to secure an app with the IAP JWT, and calls signed headers secondary security; AWS ALB requires verification of its signed claims header and signer ARN. These sources support the guide's origin-isolation test expectation but do not establish that a particular origin is unreachable.", "components": ["owasp", "cloudflare-access", "oauth2-proxy", "authelia", "google-iap", "aws-alb"], "sources": ["owasp:sc5f1b11d42f4", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:s81e5dd28d3e5", "cloudflare-access:sa012410f91eb", "oauth2-proxy:s6de4892223d2", "oauth2-proxy:s17f0d3cc09b1", "authelia:sc03548e2ed00", "google-iap:s4513609280bb", "aws-alb:sa198710d31f3"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
