# MCP clients: authorizing to Model Context Protocol servers safely

An MCP client authorizes to a remote server on a user's behalf, and a malicious or confused server can steer that authorization: it can name an attacker's authorization server, hand back a discovery document that points credentials the wrong way, or supply OAuth URLs that make the client reach inside its own network. The [mcp-servers.md](mcp-servers.md) guide covers the server operator's side and its fronting proxy; this guide covers the **client's** obligations under the MCP **2026-07-28** authorization flow, where a skipped check is not a style lapse but the difference between an authorization code reaching the honest token endpoint and reaching an attacker's. Everything here is a client-side control: it runs in the MCP client (a desktop app, a CLI, or a client deployed on a server), not in the server it talks to.

**Spec revision.** This guide is written against MCP **2026-07-28**, the **Current** revision, and every "MCP requires" below is quoted from that revision's authorization and security pages. Requirement levels (MUST, SHOULD, MAY) are reproduced as the source states them; where a control is a SHOULD in one document and a MUST in another for a narrower case, both are given rather than the stronger one alone. See MCP Authorization.

## 1. Validate the authorization-response `iss` before redeeming the code

When the authorization server redirects back with a code, an `iss` parameter may accompany it. RFC 9207 section 2.4 requires a client that receives `iss` to decode it and compare it with the issuer it expected: "This comparison MUST use simple string comparison", and on a mismatch "clients MUST reject the authorization response and MUST NOT proceed with the authorization grant." MCP makes this validation apply **before the code is redeemed**: the client "MUST apply the validation" "before transmitting the authorization code to any token endpoint". A check performed on an ID token *after* the code is exchanged is too late, because the code has already left for a possibly attacker-controlled token endpoint, and for a public client the PKCE verifier can leave with it.

The handling is not "reject every response that has no `iss`". It depends on whether the authorization server advertised `authorization_response_iss_parameter_supported` and whether `iss` is present:

| AS advertises `authorization_response_iss_parameter_supported: true` | Response `iss` | Required handling |
|---|---|---|
| Yes | Present | Compare with the recorded issuer; reject on mismatch |
| Yes | Absent | Reject the response |
| No or omitted | Present | Compare with the recorded issuer; reject on mismatch |
| No or omitted | Absent | Proceed under this table (a multi-AS client still needs an `iss`-independent mix-up defence) |

Record the issuer you selected from validated metadata (step 2) in the authorization transaction, bound to the same `state`/PKCE record, and compare `iss` against it with exact string comparison: do not normalize hostname case, port, a trailing slash, or percent-encoding, because RFC 9207's "simple string comparison" is defeated by any normalization an attacker can exploit. This defends the mix-up attack of RFC 9700 section 4.4.2, where a client that trusts more than one authorization server is tricked into sending an honest server's code to an attacker's token endpoint; RFC 9700 requires that "clients MUST prevent mix-up attacks". Where `iss` is genuinely unavailable (the last table row), a client that talks to more than one authorization server still needs an applicable mix-up defence and cannot treat the absence as safe.

## 2. Validate discovery metadata identity: `issuer` (not `resource`)

Two different identifiers are validated in the discovery flow, and confusing them leaves a hole:

- **Authorization-server metadata** carries an `issuer`, and RFC 8414 section 3.3 requires that "The \"issuer\" value returned MUST be identical" to the issuer identifier used to build the well-known URL (which includes any issuer path component, not merely the hostname, and is not the full metadata URL). "If these values are not identical, the data contained in the response MUST NOT be used." MCP restates it: "the `issuer` value in the document MUST be identical to the issuer identifier used to construct the well-known URL." Preserve the issuer you used to derive the discovery URL and compare the returned `issuer` to it exactly, before you use any endpoint from the document. When you discover through OpenID Connect instead, apply the equivalent OIDC provider-configuration validation of `issuer`.
- **Protected-resource metadata** carries a `resource`, and RFC 9728 section 3.3 validates *that* against the resource identifier you intended to reach. This is a separate check from the `issuer` check above; RFC 9728 section 3.3 is about `resource`, not `issuer`, so do both.

Skipping the `issuer` check lets an attacker serve metadata from a location it controls while naming an honest issuer, associating that honest issuer with attacker-chosen endpoints and undermining the expected-issuer record that step 1's mix-up defence relies on.

## 3. Present the client identity safely: Client ID Metadata Documents, then DCR with an explicit `application_type`

MCP 2026-07-28 prefers **Client ID Metadata Documents** (CIMD, `draft-ietf-oauth-client-id-metadata-document-00`, dated 8 October 2025): the client uses an HTTPS URL as its `client_id`, and the authorization server fetches JSON client metadata from that URL instead of requiring prior registration. The draft requires that "Client identifier URLs MUST have an \"https\" scheme, MUST contain a path component", and that the document's own `client_id` "value MUST match the URL of the document" by simple string comparison. MCP states clients "SHOULD support OAuth Client ID Metadata Documents", and a client that supports several mechanisms SHOULD prefer an available pre-registration, then supported CIMD, then Dynamic Client Registration.

Dynamic Client Registration (DCR) remains a **MAY**, deprecated but kept for compatibility. When you fall back to it, MCP requires an explicit application type: "MCP clients MUST specify an appropriate `application_type` during Dynamic Client Registration." MCP's guidance is to use `native` (a SHOULD) for desktop, mobile, CLI, and localhost-hosted applications, and `web` (a SHOULD) for remotely hosted browser applications. This matters because the default is not neutral: OpenID Connect registration says "The default, if omitted, is `web`", and `web` implies redirect-URI constraints that can conflict with a native client's loopback or custom-scheme redirect, so under a provider policy that enforces them an omitted `application_type` can be rejected. Supply the type explicitly and handle a rejection by fixing the registration, never by loosening redirect validation to make it pass.

(Version boundary: MCP 2025-06-18 said its clients and authorization servers "SHOULD support the OAuth 2.0 Dynamic Client Registration Protocol"; the CIMD-before-DCR priority order was already present by 2025-11-25, so it is not new in 2026-07-28. Carry the revision label when you cite it.)

## 4. Keep refresh tokens confidential, and request `offline_access` correctly

A refresh token outlives the short-lived access token, so a stolen one buys continued access. OAuth 2.1 (draft-ietf-oauth-v2-1-14 section 4.3) requires that "Refresh tokens MUST be kept confidential in transit and storage" and restricts sharing to the issuing authorization server and the client that received the token; this binds **public** clients as much as confidential ones. In practice:

- When refreshing access, send a refresh token only to the issuing authorization server's token endpoint over authenticated TLS; to revoke one, send it only to that same server's revocation endpoint (RFC 7009 section 2) over authenticated TLS. Never send a refresh token to the MCP resource server.
- Keep it out of logs, URLs, source repositories, and any published client metadata.
- Store it in protected server-side storage or a native platform credential store; those are ways to satisfy the confidentiality requirement, not a specific product the spec mandates.

To obtain one, MCP says a client that wants refresh tokens "SHOULD include" `refresh_token` in `grant_types`, "MAY add" `offline_access` to its requested scopes when the authorization server advertises it in `scopes_supported`, and "MUST NOT assume" a refresh token will be issued. For an OpenID Connect authorization server, requesting `offline_access` has conditions: OIDC Core section 11 says "a `prompt` parameter value of `consent` MUST be used" (unless another condition already permits offline access), and the server "MUST ignore the `offline_access` request unless the Client is using a `response_type`" that returns an authorization code. So request `offline_access` with the code flow and normally `prompt=consent`, and handle the case where no refresh token comes back, since `offline_access` neither guarantees issuance nor is the only way a refresh token can be issued.

## 5. Defend OAuth discovery fetches against SSRF

A client that fetches OAuth-related URLs a server named (protected-resource metadata, authorization-server metadata, and every endpoint reached afterward) is fetching attacker-influenced URLs. RFC 9728 section 7.7 identifies exactly this surface and says "Clients SHOULD take appropriate precautions against SSRF attacks, such as blocking requests to internal IP address ranges." For a client that runs **on a server**, MCP raises it to a MUST: "MCP clients deployed to a server MUST consider SSRF risks and implement appropriate mitigations when fetching OAuth-related URLs."

The attack is a malicious server handing back discovery URLs aimed at a cloud metadata service, a loopback daemon, or a private administration endpoint; a redirect or DNS rebinding can turn an allowed destination into an internal one after the check, and later token-endpoint POSTs can reach internal services too. Apply destination controls to every fetched URL, not just the first:

- Restrict destinations to production HTTPS and block private/reserved address ranges (loopback, link-local including the `169.254.169.254` metadata address, and RFC 1918).
- Re-validate the target of every redirect to the same standard, and address the gap between validating a hostname and connecting to it (DNS can change in between): resolve-then-pin, or route through an egress proxy.
- Configure any genuinely required private-network exception explicitly rather than disabling the control.

For a deployment with a known set of providers, an issuer allowlist and an approved-destination list narrow the surface further. OWASP's SSRF guidance for this shape is to "Do not accept complete URLs from the user" and instead "Match the host against an allowlist, and build the request yourself." Treat those as sound deployment practice rather than a spec requirement: RFC 9728 deliberately accommodates previously unknown authorization and resource servers, so a dynamic client still needs the runtime SSRF controls above, and issuer-equality validation (step 2) alone does not establish that a destination is safe to fetch.

## 6. Carry the baseline OAuth 2.1 client hygiene through

The controls above are the MCP-specific additions; the client still owes the baseline that [oidc-integration.md](oidc-integration.md) covers, which MCP also mandates:

- **PKCE.** Clients "MUST implement PKCE", MUST use `S256` "when technically capable", and "MUST refuse to proceed" if the authorization server's metadata lacks `code_challenge_methods_supported`. See MCP Authorization Security Considerations.
- **Resource parameter.** Clients MUST send the RFC 8707 `resource` parameter in both the authorization and token requests, naming the MCP server's canonical URI, which requests an access token scoped to that resource. Preventing cross-resource replay then depends on the authorization server supporting audience binding and issuing an audience-restricted token, and on each resource server validating that it is the intended audience; sending the parameter alone does not guarantee it. See MCP Authorization.
- **HTTPS everywhere.** Every authorization-server endpoint is contacted over HTTPS, and every redirect URI is `localhost` or HTTPS (MCP Authorization Security Considerations). Bearer and access tokens never travel in a URL query string; they go in the `Authorization` header (MCP Authorization). The authorization code, by contrast, is returned in the registered redirect URI's query by the flow itself (OAuth 2.1 section 4.1.2), so it is protected instead by PKCE and the step 1 `iss` check, and the client keeps callback URLs out of logs and referrer headers (RFC 9700 section 4.2.4).

## Verify

These checks are client-behaviour checks. Standing up a full malicious-authorization-server harness to drive a specific MCP client is infrastructure this repository's authoring environment does not have, so the behavioural steps below are marked **reasoned**: each names the prerequisite that is unavailable, gives the concrete request or command, and states the exposed and fixed outcomes and the source passage that distinguishes them, per the contributing rule on Verify steps. The locally feasible checks (the SSRF address test and the config grep) are run as written. TODO row 1.86 tracks demonstrating the reasoned steps against a real client once a client-plus-authorization-server harness exists.

1. **`iss` mismatch is rejected before redemption (reasoned).** Prerequisite unavailable: a controllable authorization server and a target MCP client. Run two authorization-callback requests to the client's redirect URI that are identical except for `iss`, and run each from the SAME freshly restored pre-callback snapshot of the client and the authorization transaction (an unconsumed `state`, a valid unredeemed `code`, and the matching PKCE context), so that neither a consumed `state` nor a spent code, but only `iss`, can cause a rejection. This isolation matters because RFC 9700 section 4.2.4 says the `state` value "SHOULD be invalidated by the client after its first use at the redirection endpoint", so replaying the second callback against the same live transaction would let a client with no issuer validation reject it as a replay and mimic the fixed outcome. Restore the snapshot before each request. Control (must be accepted), carrying the recorded issuer: `GET /callback?code=SPLICED_AUTH_CODE&state=THE_RECORDED_STATE&iss=https%3A%2F%2Fas.example.com`. Test (must be rejected), differing only in `iss`: the same request with `iss=https%3A%2F%2Fevil.example.net`. Exposed (vulnerable) client: it proceeds to `POST` the code to a token endpoint in the test case. Fixed client: it accepts the control and rejects the test, sending no token request for the test. The distinguishing source is RFC 9207 section 2.4 ("clients MUST reject ... and MUST NOT proceed") applied before redemption per MCP Authorization ("before transmitting the authorization code to any token endpoint"). Observe the difference on the wire (a token request appears for the control but not for the test).

2. **Metadata `issuer` mismatch is rejected (reasoned).** Prerequisite unavailable: a controllable metadata endpoint. Serve two authorization-server metadata documents at the well-known URL built from the issuer `https://as.example.com` (that is, `https://as.example.com/.well-known/oauth-authorization-server`), identical except for `issuer`. Control (accepted): `{"issuer":"https://as.example.com","authorization_endpoint":"https://as.example.com/authorize","token_endpoint":"https://as.example.com/token","response_types_supported":["code"],"code_challenge_methods_supported":["S256"]}`. That is a metadata baseline complete enough for the client to proceed (RFC 8414 section 2 marks `response_types_supported` REQUIRED, and MCP refuses when `code_challenge_methods_supported` is absent), so a rejection is attributable to `issuer` rather than a missing required field. Test (rejected): the same body with only `"issuer":"https://evil.example.net"` changed. Exposed: the client uses the endpoints from the test document. Fixed: the client accepts the control and discards the test, contacting no endpoint named in it. Distinguishing source: RFC 8414 section 3.3 ("the data contained in the response MUST NOT be used").

3. **SSRF destinations are blocked (partially runnable).** The address-classification half is runnable now; the client-integration half is reasoned. Runnable: confirm the deny-list rejects the reserved and internal ranges a discovery URL might target, namely the cloud metadata address, loopback, and RFC 1918 space:

   ```bash
   (
     for ip in 169.254.169.254 127.0.0.1 10.0.0.1 192.168.0.1 172.16.0.1; do
       python3 -c 'import ipaddress,sys; a=ipaddress.ip_address(sys.argv[1]); print(sys.argv[1], "BLOCK" if (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved) else "ALLOW")' "$ip"
     done
   )
   ```

   Every line must print `BLOCK`; a printed `ALLOW` for any of these is an SSRF hole. Reasoned (prerequisite unavailable: a malicious server, the target client, and a controllable HTTPS discovery host that carries a valid, trusted TLS certificate and whose name resolves to an address you choose): keep the scheme HTTPS with valid TLS throughout and vary only the resolved address, so a refusal is attributable to the address policy rather than to HTTPS or TLS enforcement. Run the public-address control and the private-address test from the same fresh pre-discovery state, clearing any cached discovery metadata, DNS answers, and open connections between them, because otherwise a cached response would satisfy discovery with no fetch at all (RFC 9728 section 7.10 notes "Normal HTTP caching behaviors apply", and RFC 9111 section 4.2 has a fresh cached response served without contacting the origin). Establish the public-address control first: point the discovery URL at that host resolving to a routable public address and confirm the client fetches it. Then, from that cleared state and changing only the resolved address, point the same HTTPS host at the cloud metadata address (`169.254.169.254`) or another blocked range. Exposed (vulnerable) client: it fetches the URL and reaches the internal service. Fixed client: it resolves the test to the blocked address and refuses that destination before connecting. Require positive evidence of that resolve-and-reject, not the mere absence of a request, since a cache hit also produces no request. Distinguishing source: RFC 9728 section 7.7 and, for server-deployed clients, the MCP MUST in Security Best Practices.

4. **No refresh token or long-lived bearer token stored in cleartext (runnable, bounded heuristic).** This is a heuristic scan, not a proof: it searches the client's config and log paths for a refresh-token or bearer-token value in the clear, lists only the filenames (never the secret itself), and separates a clean scan from a scan error. Substitute the client's own path for the placeholder, inside the single quotes on the `set --` line:

   ```bash
   (
     set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLIENT_CONFIG_DIR'
     [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
     shift
     [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
     case "$1" in
       *REPLACE_WITH_*|"") echo "substitute the client's config/log directory inside the quotes above; not probing"; exit ;;
     esac
     [ -d "$1" ] || { echo "not a directory: $1; not probing"; exit; }
     grep -rlIE '"refresh_token"[[:space:]]*:[[:space:]]*"[^"]|refresh_token=[A-Za-z0-9._~+/-]|Bearer[[:space:]]+[A-Za-z0-9._-]{20,}' -- "$1"
     case $? in
       0) echo "FOUND: the file(s) listed above hold a token value in cleartext; move it to a protected credential store" ;;
       1) echo "clean: no cleartext token value found under $1" ;;
       *) echo "scan error: grep could not read part of $1; re-run with access before trusting a clean result" ;;
     esac
   )
   ```

   A listed file means a refresh or bearer token value sits in cleartext where OAuth 2.1 section 4.3 requires confidentiality; the fixed state keeps it in a protected credential store and the scan reports `clean`. The pattern matches a token value (a JSON `"refresh_token": "..."` pair, a `refresh_token=` assignment, or a `Bearer <token>` header), so the bare word `refresh_token` inside a `grant_types` list does not trip it, and it lists filenames rather than printing the secret. It cannot see a token that is encrypted, wrapped, or split across fields, so read a `clean` result as "nothing obvious", not "nothing present".

5. **`application_type` is present on DCR (reasoned).** Prerequisite unavailable: the client's live DCR request. Capture the registration request body the client `POST`s to the DCR endpoint and confirm it includes `application_type` (`native` or `web` per step 3). A fixed native client's captured body looks like this (an illustrative shape, not a live capture):

   ```json
   {"redirect_uris":["http://localhost:3000/callback"],"grant_types":["authorization_code"],"response_types":["code"],"token_endpoint_auth_method":"none","application_type":"native"}
   ```

   Save the actual captured body as `dcr-request.json` and inspect it (this native client checks for `native`; a remotely-hosted browser client checks for `web` instead):

   ```bash
   python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("application_type") == "native" else 1)' < dcr-request.json
   ```

   Exposed: the field is absent and the server defaults it to `web` (OIDC Registration section 2), which under a provider policy that enforces the web redirect-URI constraints gets a native client's loopback or custom-scheme redirect rejected, so the command exits non-zero. Fixed: the field is present and matches the client's deployment, so the command exits zero. Distinguishing source: MCP's "MUST specify an appropriate `application_type`".

## Sources (checked September 2026)

- MCP Authorization, 2026-07-28 (`iss` validation timing, access-token query-string prohibition, `resource` parameter, refresh-token scope guidance): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- MCP Authorization Security Considerations, 2026-07-28 (PKCE MUSTs, HTTPS endpoints and redirect URIs): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations
- MCP Authorization Server Discovery, 2026-07-28 (`issuer` identity requirement): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery
- MCP Client Registration, 2026-07-28 (CIMD SHOULD, mechanism preference, DCR `application_type` MUST): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration
- MCP Security Best Practices, 2026-07-28 (SSRF MUST for server-deployed clients): https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
- RFC 9207 section 2.4, OAuth 2.0 Authorization Server Issuer Identification (`iss` simple string comparison, reject on mismatch): https://www.rfc-editor.org/rfc/rfc9207.html#section-2.4
- RFC 9700 section 4.2.4 and section 4.4.2, OAuth 2.0 Security Best Current Practice (single-use `state`; mix-up attacks): https://www.rfc-editor.org/rfc/rfc9700.html#section-4.2.4
- RFC 8414 section 3.3, OAuth 2.0 Authorization Server Metadata (`issuer` identity): https://www.rfc-editor.org/rfc/rfc8414.html#section-3.3
- RFC 9728 section 3.3, section 7.7, and section 7.10, OAuth 2.0 Protected Resource Metadata (`resource` validation; SSRF precautions; metadata caching): https://www.rfc-editor.org/rfc/rfc9728.html#section-7.7
- RFC 9111 section 4.2, HTTP Caching (a fresh cached response is served without contacting the origin): https://www.rfc-editor.org/rfc/rfc9111.html#section-4.2
- RFC 8707, Resource Indicators for OAuth 2.0 (`resource` parameter): https://www.rfc-editor.org/rfc/rfc8707.html
- RFC 7009 section 2, OAuth 2.0 Token Revocation (refresh-token revocation endpoint): https://www.rfc-editor.org/rfc/rfc7009.html#section-2
- OAuth 2.1 draft-ietf-oauth-v2-1-14 section 4.1.2 and section 4.3 (authorization code in the redirect query; refresh-token confidentiality): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-14#section-4.3
- OAuth Client ID Metadata Document draft-ietf-oauth-client-id-metadata-document-00 (HTTPS client-id URL, matching `client_id`): https://datatracker.ietf.org/doc/html/draft-ietf-oauth-client-id-metadata-document-00
- OpenID Connect Core 1.0 errata 2 section 11, Offline Access (`prompt=consent`, `response_type` condition): https://openid.net/specs/openid-connect-core-1_0-errata2.html#OfflineAccess
- OpenID Connect Dynamic Client Registration 1.0 errata 2 section 2 (`application_type` default is `web`): https://openid.net/specs/openid-connect-registration-1_0-errata2.html#ClientMetadata
- OWASP Server Side Request Forgery Prevention Cheat Sheet (host allowlist, build the request yourself): https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
