# MCP clients: authorizing to Model Context Protocol servers safely

An MCP client authorizes to a remote server on a user's behalf, and a malicious or confused server can steer that authorization: it can name an attacker's authorization server, hand back a discovery document that points credentials the wrong way, or supply OAuth URLs that make the client reach inside its own network. The [mcp-servers.md](mcp-servers.md) guide covers the server operator's side and its fronting proxy; this guide covers the **client's** obligations under the MCP **2026-07-28** authorization flow, where a skipped check is not a style lapse but the difference between an authorization code reaching the honest token endpoint and reaching an attacker's. Everything here is a client-side control: it runs in the MCP client (a desktop app, a CLI, or a client deployed on a server), not in the server it talks to.

**Spec revision.** This guide is written against MCP **2026-07-28**, the **Current** revision, and every "MCP requires" below is quoted from that revision's authorization pages. Requirement levels (MUST, SHOULD, MAY) are reproduced as the source states them; where a control is a SHOULD in one document and a MUST in another for a narrower case, both are given rather than the stronger one alone. See MCP Authorization.

## 1. Validate the authorization-response `iss` before redeeming the code

When the authorization server redirects back with a code, an `iss` parameter may accompany it. RFC 9207 §2.4 requires a client that receives `iss` to decode it and compare it with the issuer it expected: "This comparison MUST use simple string comparison", and on a mismatch "clients MUST reject the authorization response and MUST NOT proceed with the authorization grant." MCP makes this validation apply **before the code is redeemed**: the client "MUST apply the validation" "before transmitting the authorization code to any token endpoint". A check performed on an ID token *after* the code is exchanged is too late, because the code has already left for a possibly attacker-controlled token endpoint, and for a public client the PKCE verifier can leave with it.

The handling is not "reject every response that has no `iss`". It depends on whether the authorization server advertised `authorization_response_iss_parameter_supported` and whether `iss` is present:

| AS advertises `authorization_response_iss_parameter_supported: true` | Response `iss` | Required handling |
|---|---|---|
| Yes | Present | Compare with the recorded issuer; reject on mismatch |
| Yes | Absent | Reject the response |
| No or omitted | Present | Compare with the recorded issuer; reject on mismatch |
| No or omitted | Absent | Proceed under this table (an `iss`-independent mix-up defence still applies) |

Record the issuer you selected from validated metadata (step 2) in the authorization transaction, bound to the same `state`/PKCE record, and compare `iss` against it with exact string comparison: do not normalize hostname case, port, a trailing slash, or percent-encoding, because RFC 9207's "simple string comparison" is defeated by any normalization an attacker can exploit. This defends the mix-up attack of RFC 9700 §4.4, where a client that trusts more than one authorization server is tricked into sending an honest server's code to an attacker's token endpoint; RFC 9700 requires that "clients MUST prevent mix-up attacks". Where `iss` is genuinely unavailable (the last table row), a client that talks to more than one authorization server still needs an applicable mix-up defence and cannot treat the absence as safe.

## 2. Validate discovery metadata identity: `issuer` (not `resource`)

Two different identifiers are validated in the discovery flow, and confusing them leaves a hole:

- **Authorization-server metadata** carries an `issuer`, and RFC 8414 §3.3 requires that "The \"issuer\" value returned MUST be identical" to the issuer identifier used to build the well-known URL, "including its issuer path", not merely the hostname and not the full metadata URL. "If these values are not identical, the data contained in the response MUST NOT be used." MCP restates it: "the `issuer` value in the document MUST be identical to the issuer identifier used to construct the well-known URL." Preserve the issuer you used to derive the discovery URL and compare the returned `issuer` to it exactly, before you use any endpoint from the document. When you discover through OpenID Connect instead, apply the equivalent OIDC provider-configuration validation of `issuer`.
- **Protected-resource metadata** carries a `resource`, and RFC 9728 §3.3 validates *that* against the resource identifier you intended to reach. This is a separate check from the `issuer` check above; RFC 9728 §3.3 is about `resource`, not `issuer`, so do both.

Skipping the `issuer` check lets an attacker serve metadata from a location it controls while naming an honest issuer, associating that honest issuer with attacker-chosen endpoints and undermining the expected-issuer record that step 1's mix-up defence relies on.

## 3. Present the client identity safely: Client ID Metadata Documents, then DCR with an explicit `application_type`

MCP 2026-07-28 prefers **Client ID Metadata Documents** (CIMD, `draft-ietf-oauth-client-id-metadata-document-00`, dated 8 October 2025): the client uses an HTTPS URL as its `client_id`, and the authorization server fetches JSON client metadata from that URL instead of requiring prior registration. The draft requires that "Client identifier URLs MUST have an \"https\" scheme, MUST contain a path component", and that the document's own `client_id` "value MUST match the URL of the document" by simple string comparison. MCP states clients "SHOULD support OAuth Client ID Metadata Documents", and a client that supports several mechanisms SHOULD prefer an available pre-registration, then supported CIMD, then Dynamic Client Registration.

Dynamic Client Registration (DCR) remains a **MAY**, deprecated but kept for compatibility. When you fall back to it, MCP requires an explicit application type: "MCP clients MUST specify an appropriate `application_type` during Dynamic Client Registration." MCP's guidance is to use `native` (a SHOULD) for desktop, mobile, CLI, and localhost-hosted applications, and `web` (a SHOULD) for remotely hosted browser applications. This matters because the default is not neutral: OpenID Connect registration says "The default, if omitted, is `web`", and `web` applies redirect-URI constraints that a native client's loopback or custom-scheme redirect will fail, so an omitted `application_type` can get the registration rejected. Supply the type explicitly and handle a rejection by fixing the registration, never by loosening redirect validation to make it pass.

(Version boundary: MCP 2025-06-18 instead said servers and clients "SHOULD support the OAuth 2.0 Dynamic Client Registration Protocol". The CIMD-first preference is specific to 2026-07-28; carry the revision label when you cite it.)

## 4. Keep refresh tokens confidential, and request `offline_access` correctly

A refresh token outlives the short-lived access token, so a stolen one buys continued access. OAuth 2.1 (draft-ietf-oauth-v2-1-14 §4.3) requires that "Refresh tokens MUST be kept confidential in transit and storage" and restricts sharing to the issuing authorization server and the client that received the token; this binds **public** clients as much as confidential ones. In practice:

- Send a refresh token only to the issuing authorization server's token endpoint over authenticated TLS, never to the MCP resource server.
- Keep it out of logs, URLs, source repositories, and any published client metadata.
- Store it in protected server-side storage or a native platform credential store; those are ways to satisfy the confidentiality requirement, not a specific product the spec mandates.

To obtain one, MCP says a client that wants refresh tokens "SHOULD include" `refresh_token` in `grant_types`, "MAY add" `offline_access` to its requested scopes when the authorization server advertises it in `scopes_supported`, and "MUST NOT assume" a refresh token will be issued. For an OpenID Connect authorization server, requesting `offline_access` has conditions: OIDC Core §11 says "a `prompt` parameter value of `consent` MUST be used" (unless another condition already permits offline access), and the server "MUST ignore the `offline_access` request unless the Client is using a `response_type`" that returns an authorization code. So request `offline_access` with the code flow and normally `prompt=consent`, and handle the case where no refresh token comes back, since `offline_access` neither guarantees issuance nor is the only way a refresh token can be issued.

## 5. Defend OAuth discovery fetches against SSRF

A client that fetches OAuth-related URLs a server named (protected-resource metadata, authorization-server metadata, and every endpoint reached afterward) is fetching attacker-influenced URLs. RFC 9728 §7.7 identifies exactly this surface and says "Clients SHOULD take appropriate precautions against SSRF attacks, such as blocking requests to internal IP address ranges." For a client that runs **on a server**, MCP raises it to a MUST: "MCP clients deployed to a server MUST consider SSRF risks and implement appropriate mitigations when fetching OAuth-related URLs."

The attack is a malicious server handing back discovery URLs aimed at a cloud metadata service, a loopback daemon, or a private administration endpoint; a redirect or DNS rebinding can turn an allowed destination into an internal one after the check, and later token-endpoint POSTs can reach internal services too. Apply destination controls to every fetched URL, not just the first:

- Restrict destinations to production HTTPS and block private/reserved address ranges (loopback, link-local including the `169.254.169.254` metadata address, and RFC 1918).
- Re-validate the target of every redirect to the same standard, and address the gap between validating a hostname and connecting to it (DNS can change in between): resolve-then-pin, or route through an egress proxy.
- Configure any genuinely required private-network exception explicitly rather than disabling the control.

For a deployment with a known set of providers, an issuer allowlist and an approved-destination list narrow the surface further. OWASP's SSRF guidance for this shape is to "Do not accept complete URLs from the user" and instead "Match the host against an allowlist, and build the request yourself." Treat those as sound deployment practice rather than a spec requirement: RFC 9728 deliberately accommodates previously unknown authorization and resource servers, so a dynamic client still needs the runtime SSRF controls above, and issuer-equality validation (step 2) alone does not establish that a destination is safe to fetch.

## 6. Carry the baseline OAuth 2.1 client hygiene through

The controls above are the MCP-specific additions; the client still owes the baseline that [oidc-integration.md](oidc-integration.md) covers, which MCP also mandates:

- **PKCE.** Clients "MUST implement PKCE", MUST use `S256` "when technically capable", and "MUST refuse to proceed" if the authorization server's metadata lacks `code_challenge_methods_supported`. See MCP Authorization Security Considerations.
- **Resource parameter.** Clients MUST send the RFC 8707 `resource` parameter in both the authorization and token requests, naming the MCP server's canonical URI, so a token cannot be replayed at a different resource. See MCP Authorization.
- **HTTPS everywhere.** Every authorization-server endpoint is contacted over HTTPS; bearer tokens and codes never travel in cleartext or in a URL query string. See MCP Authorization Security Considerations.

## Verify

These checks are client-behaviour checks. Standing up a full malicious-authorization-server harness to drive a specific MCP client is infrastructure this repository's authoring environment does not have, so the behavioural steps below are marked **reasoned**: each names the prerequisite that is unavailable, gives the concrete request or command, and states the exposed and fixed outcomes and the source passage that distinguishes them, per the contributing rule on Verify steps. The locally feasible checks (the SSRF address test and the config greps) are run as written. A backlog row tracks demonstrating the reasoned steps against a real client once a client-plus-authorization-server harness exists.

1. **`iss` mismatch is rejected before redemption (reasoned).** Prerequisite unavailable: a controllable authorization server and a target MCP client. Drive an authorization response whose `iss` differs from the metadata issuer the client recorded (for example issuer `https://as.example.com` recorded, `iss=https://evil.example.net` returned). Exposed (vulnerable) client: it proceeds to `POST` the code to a token endpoint. Fixed client: it rejects the response and sends no token request. The distinguishing source is RFC 9207 §2.4 ("clients MUST reject ... and MUST NOT proceed") applied before redemption per MCP Authorization ("before transmitting the authorization code to any token endpoint"). Observe the difference on the wire (a token request appears only in the exposed case).

2. **Metadata `issuer` mismatch is rejected (reasoned).** Prerequisite unavailable: a controllable metadata endpoint. Serve authorization-server metadata whose `issuer` differs from the issuer identifier used to build the well-known URL. Exposed: the client uses the endpoints from that document. Fixed: the client discards it and does not contact those endpoints. Distinguishing source: RFC 8414 §3.3 ("the data contained in the response MUST NOT be used").

3. **SSRF destinations are blocked (partially runnable).** The address-classification half is runnable now; the client-integration half is reasoned. Runnable: confirm the deny-list rejects the reserved and internal ranges a discovery URL might target, namely the cloud metadata address and RFC 1918 space:

   ```bash
   (
     for ip in 169.254.169.254 127.0.0.1 10.0.0.1 192.168.0.1 172.16.0.1; do
       python3 -c 'import ipaddress,sys; a=ipaddress.ip_address(sys.argv[1]); print(sys.argv[1], "BLOCK" if (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved) else "ALLOW")' "$ip"
     done
   )
   ```

   Every line must print `BLOCK`; a printed `ALLOW` for any of these is an SSRF hole. Reasoned (prerequisite unavailable: a malicious server plus the target client): a discovery URL resolving to one of these addresses is refused by the client before the fetch, per RFC 9728 §7.7 and, for server-deployed clients, the MCP MUST in Security Best Practices.

4. **No refresh token or long-lived secret in client logs or config (runnable).** Grep the client's configuration and log locations for a stored refresh token or bearer token written in the clear. Substitute the client's own paths for the placeholder:

   ```bash
   (
     set -- REPLACE_WITH_CLIENT_CONFIG_DIR
     case "$1" in
       *REPLACE_WITH_*|"") echo "substitute the client's config/log directory above; not probing"; exit ;;
     esac
     grep -rInE 'refresh_token|Bearer [A-Za-z0-9._-]{20,}' "$1" 2>/dev/null \
       && echo "FOUND a token in cleartext; investigate" \
       || echo "no cleartext token found under $1"
   )
   ```

   A match means a refresh or bearer token is sitting in cleartext where OAuth 2.1 §4.3 requires confidentiality; the fixed state stores it in a protected credential store instead and this grep finds nothing.

5. **`application_type` is present on DCR (reasoned).** Prerequisite unavailable: the client's live DCR request. Capture the registration request body the client sends and confirm it includes `application_type` (`native` or `web` per step 3). Exposed: the field is absent and the server defaults it to `web` (OIDC Registration §2), breaking a native client's redirect. Fixed: the field is present and matches the client's deployment. Distinguishing source: MCP's "MUST specify an appropriate `application_type`".

## Sources (checked September 2026)

- MCP Authorization, 2026-07-28 (`iss` validation timing, PKCE, `resource` parameter, refresh-token scope guidance): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- MCP Authorization Server Discovery, 2026-07-28 (`issuer` identity requirement): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery
- MCP Client Registration, 2026-07-28 (CIMD SHOULD, mechanism preference, DCR `application_type` MUST): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration
- MCP Security Best Practices, 2026-07-28 (SSRF MUST for server-deployed clients): https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
- RFC 9207 §2.4, OAuth 2.0 Authorization Server Issuer Identification (`iss` simple string comparison, reject on mismatch): https://www.rfc-editor.org/rfc/rfc9207.html#section-2.4
- RFC 9700 §4.4, OAuth 2.0 Security Best Current Practice (mix-up attacks): https://www.rfc-editor.org/rfc/rfc9700.html#section-4.4
- RFC 8414 §3.3, OAuth 2.0 Authorization Server Metadata (`issuer` identity): https://www.rfc-editor.org/rfc/rfc8414.html#section-3.3
- RFC 9728 §3.3 and §7.7, OAuth 2.0 Protected Resource Metadata (`resource` validation; SSRF precautions): https://www.rfc-editor.org/rfc/rfc9728.html#section-7.7
- RFC 8707, Resource Indicators for OAuth 2.0 (`resource` parameter): https://www.rfc-editor.org/rfc/rfc8707.html
- OAuth 2.1 draft-ietf-oauth-v2-1-14 §4.3 (refresh-token confidentiality): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-14#section-4.3
- OAuth Client ID Metadata Document draft-ietf-oauth-client-id-metadata-document-00 (HTTPS client-id URL, matching `client_id`): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00
- OpenID Connect Core 1.0 errata 2 §11, Offline Access (`prompt=consent`, `response_type` condition): https://openid.net/specs/openid-connect-core-1_0-errata2.html#OfflineAccess
- OpenID Connect Dynamic Client Registration 1.0 errata 2 §2 (`application_type` default is `web`): https://openid.net/specs/openid-connect-registration-1_0-errata2.html#ClientMetadata
- OWASP Server Side Request Forgery Prevention Cheat Sheet (host allowlist, build the request yourself): https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
