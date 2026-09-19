# MCP servers: exposing Model Context Protocol servers safely

An MCP server gives a model tools, and every tool it exposes runs with the credentials the server holds. The 2025-11-25 specification defines two transports. Over **stdio** the client launches the server as a subprocess and talks over stdin and stdout: there is no network listener, but the process runs as the launching user with every credential in its environment, so a malicious or careless server is a local compromise, not a network one. Over **Streamable HTTP** the server is a web service with a single endpoint accepting POST and GET, and every rule in [authentication.md](authentication.md) applies to it. The older HTTP with SSE transport (protocol version 2024-11-05) is deprecated; Streamable HTTP replaces it. The spec makes authorization OPTIONAL at the protocol level; this repository does not, so an HTTP MCP server reachable beyond loopback authenticates every request, either natively or through a fronting layer.

**Spec revision.** This guide is written against MCP **2025-11-25** (a Final revision). The current revision is **2026-07-28**, and every security control below carries over to it unchanged: Origin validation, loopback binding, and the OAuth 2.1 / RFC 9728 / PKCE / RFC 8707 / audience-validation / no-token-passthrough rules are all the same. What 2026-07-28 changes is the transport shape: it removes protocol-level sessions and the `MCP-Session-Id` header, removes the standalone GET stream, and replaces the `initialize`-handshake version negotiation with a per-request `_meta` protocol-version field, an `MCP-Protocol-Version` header, and a mandatory `server/discover` RPC. If you deploy against 2026-07-28, treat the `MCP-Session-Id` note in section 4 and the `initialize` probe in Verify as the legacy shape and follow the [current specification](https://modelcontextprotocol.io/specification/2026-07-28/) for those mechanics; the hardening in this guide still applies, though 2026-07-28 may add authorization requirements of its own beyond this guide's scope.

## 1. Prefer stdio, and keep HTTP on loopback

- For a single-user tool on a workstation, use the stdio transport. The spec's own guidance for local servers is to "use the `stdio` transport to limit access to just the MCP client" and, if HTTP is used anyway, to require an authorization token or use a Unix domain socket with restricted access.
- Give a stdio server only the environment it needs: the API key for the one service it wraps, not a shell profile full of cloud credentials. Per the spec, stdio servers "retrieve credentials from the environment", which means that environment is the server's whole privilege set ([secrets.md](secrets.md)).
- For Streamable HTTP, the spec's Security Warning says: "When running locally, servers SHOULD bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)". Bind to `127.0.0.1` and publish only a fronting layer, exactly as [ollama.md](ollama.md) does for a model server. Check the SDK or framework you use for its bind-address option; do not assume its default is loopback.

## 2. Validate `Origin` (DNS rebinding)

The spec requires it: "Servers MUST validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks. If the `Origin` header is present and invalid, servers MUST respond with HTTP 403 Forbidden." Without this, "attackers could use DNS rebinding to interact with local MCP servers from remote websites": a page in the user's browser resolves its own hostname to `127.0.0.1` and drives the local server. Do the check in the server (most SDKs have an allowed-origins option; confirm yours is on). A reverse proxy can add a second check in front, using the nginx `if` directive with the `$http_origin` variable:

```nginx
    location /mcp {
        if ($http_origin !~ "^https://mcp\.example\.com$") { return 403; }
        proxy_pass http://127.0.0.1:3000;
    }
```

Non-browser clients often send no `Origin` at all; the spec's requirement is about a present and invalid header, so decide deliberately whether a missing header is accepted (the nginx test above rejects it) and document the choice.

To accept requests that carry no `Origin` while still rejecting a wrong one, use a `map` in the `http` block (an empty string key matches a missing header) and test the variable in the location:

```nginx
map $http_origin $bad_origin {
    default                   1;
    ""                        0;    # no Origin header: a non-browser MCP client
    "https://mcp.example.com" 0;
}
```

```nginx
    location /mcp {
        if ($bad_origin) { return 403; }
        proxy_pass http://127.0.0.1:3000;
    }
```

## 3. TLS

The MCP server itself speaks plain HTTP on loopback. Terminate TLS at the proxy per [nginx.md](nginx.md) or [caddy.md](caddy.md) with a certificate from [free-certificates.md](free-certificates.md), or publish through [cloudflare.md](cloudflare.md) or [tailscale.md](tailscale.md). Bearer tokens cross the network with every request, so the spec requires HTTPS for all authorization server endpoints, and [authentication.md](authentication.md) requires it for every credential.

## 4. Authentication: native OAuth 2.1 or a fronting layer

**Option A, spec authorization.** The MCP server acts as an OAuth 2.1 resource server. The spec's requirements, in its own terms:

- MCP servers "MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728)", and the metadata "MUST include the `authorization_servers` field". Discovery is either a `WWW-Authenticate` header carrying `resource_metadata` on `401 Unauthorized` responses, or the well-known URI (`/.well-known/oauth-protected-resource`, optionally suffixed with the endpoint path); clients must support both.
- Clients "MUST implement PKCE" with the `S256` method and "MUST refuse to proceed" if the authorization server's metadata lacks `code_challenge_methods_supported`. Clients MUST send the RFC 8707 `resource` parameter naming the MCP server's canonical URI.
- Servers "MUST validate that access tokens were issued specifically for them as the intended audience"; invalid or expired tokens get `401`, insufficient scope gets `403`. Servers "MUST NOT accept or transit any other tokens": the token the client presents never travels on to an upstream API. If the server calls upstream APIs, "the access token used at the upstream API is a separate token, issued by the upstream authorization server".
- Tokens go in `Authorization: Bearer ...` on every request, never in the URL. Sessions are not authentication: servers "MUST NOT use sessions for authentication", and the `MCP-Session-Id` must be a secure, non-deterministic value.

Pick an identity provider from [identity-providers.md](identity-providers.md) as the authorization server; the client-side hygiene in [oidc-integration.md](oidc-integration.md) applies. Azure App Service can serve the RFC 9728 document for an app behind its built-in authentication: set the `WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES` application setting to the required scopes, and the 401 challenge then carries the metadata URL and scopes. Microsoft marks this **preview** at the time of writing and says the configuration may change ([cloud-identity-proxies.md](cloud-identity-proxies.md) covers the rest of Easy Auth).

**Option B, a fronting layer.** Keep the server on loopback and authenticate at the edge: a reverse proxy bearer-token check (the nginx `if ($http_authorization ...)` block in [ollama.md](ollama.md)) or basic auth per [nginx.md](nginx.md)/[caddy.md](caddy.md); Cloudflare Access with a service token for machine clients per [cloudflare.md](cloudflare.md); or an identity-aware proxy per [cloud-identity-proxies.md](cloud-identity-proxies.md). Generate and rotate the token per [machine-auth.md](machine-auth.md).

Be clear about what Option B is. A static bearer token at the proxy is a fronting control, not MCP authorization: it serves no Protected Resource Metadata and no `WWW-Authenticate` challenge with `resource_metadata`, so an MCP client that expects the OAuth discovery flow will not negotiate it. Such clients need the token pre-configured (most clients accept static headers for a server), or Option A.

MFA: MCP has no login dialogue of its own. Under Option A, MFA is whatever the authorization server enforces; under Option B it comes from the identity provider behind Access or the identity-aware proxy. Enforce it there per [mfa.md](mfa.md).

## 5. The credentials the server holds

- Each tool's upstream API key is a secret the server holds on behalf of every caller. Load it from the environment or a secret manager, one key per server and environment, never from the repository ([secrets.md](secrets.md)).
- Least privilege per tool: a read-only tool gets a read-only key. A server that wraps a database, a cloud account, and a mail API with admin credentials turns every prompt injection into an administrator.
- Never forward the client's token upstream (spec: "Token passthrough" is an anti-pattern and "explicitly forbidden"). Log tool calls with the authenticated identity so an incident can be traced.

## Verify

```bash
ss -tlnp   # read every listener; 127.0.0.1:3000 only, never 0.0.0.0 or ::
# From another host: refused at the origin, or answered only by the fronting layer.
# read err, not the number: it must name a refusal or timeout reaching YOUR address. An HTTP code
# means the port answered. A resolver failure, a local socket error, or a timeout that did not come
# from the remote address is inconclusive, never a pass.
(                                                      # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/mcp" ;;
  esac
)

# Unauthenticated initialize: 401 with a WWW-Authenticate header (Option A) or the proxy's 401 (Option B).
# --noproxy '*' so a client HTTPS_PROXY cannot answer with its own 401/407 in place of the target.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -si --noproxy '*' -X POST https://mcp.example.com/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"check","version":"1.0.0"}}}'
# Option A only: FOLLOW the resource_metadata URL from that 401's WWW-Authenticate header (a deployment may
# advertise a path-specific document; fall back to /.well-known/oauth-protected-resource/mcp, then the root
# below) and confirm it names your authorization server; do not assume the root path is the advertised one.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -s --noproxy '*' https://mcp.example.com/.well-known/oauth-protected-resource   # JSON with "authorization_servers"

# Origin control (DNS rebinding): a wrong Origin must be rejected even WITH a valid credential. Run a
# positive control first (ALLOWED Origin + a real initialize body: expect a 2xx MCP result), then the SAME
# request with only the Origin changed to a disallowed value (expect 403), so the 403 is attributable to the
# Origin check and not to an unrelated auth or scope failure. Keep the credential in a mode-0600 header file
# (secrets.md), never on the command line: REPLACE_WITH_AUTH_HEADER_FILE holds a line like
# "Authorization: Bearer <token>".
(
set -- REPLACE_WITH_AUTH_HEADER_FILE
case "$1" in ""|*REPLACE_WITH_*) echo 'substitute the mode-0600 auth-header file path on the set -- line above; not probing'; exit 2 ;; esac
[ -r "$1" ] || { echo 'auth-header file not readable; not probing'; exit 2; }
init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"check","version":"1.0.0"}}}'
curl -q -g -si --noproxy '*' -X POST https://mcp.example.com/mcp -H 'Origin: https://mcp.example.com' \
  -H "@$1" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d "$init"
                                     # allowed Origin + valid credential: expect a 2xx MCP result
curl -q -g -si --noproxy '*' -X POST https://mcp.example.com/mcp -H 'Origin: https://attacker.example' \
  -H "@$1" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d "$init"
                                     # only the Origin changed to a disallowed value: expect 403
)
```

A token issued for a different resource (wrong audience) must also fail with `401` under Option A: repeat the initialize POST above with `-H @` a header file holding an otherwise valid, unexpired token whose `aud` names a DIFFERENT resource (a forged or expired token would fail for the wrong reason), and require `401`. This step is reasoned, not demonstrated in the authoring environment: it needs a second resource registered at your authorization server, which is not available here. Fixed: `401`, the audience is rejected; exposed: any `2xx`, meaning the server accepted a token minted for another audience, which the spec's audience-validation MUST forbids. Backlog row 1.75 tracks demonstrating it in the exposed and fixed states.

## Common mistakes

- Binding the HTTP transport to `0.0.0.0` "for Docker" and leaving it there. Publish the container port on `127.0.0.1` only ([docker.md](docker.md)).
- Treating stdio as safe because it has no port: the server runs as you, with your environment.
- Accepting any token from your identity provider without checking the audience, so a token issued for another API also opens the MCP server.
- Passing the caller's token to the upstream API, which makes the upstream trust a token it never issued and loses the audit trail.

## Sources (checked September 2026)

- MCP specification 2025-11-25, Transports (stdio, Streamable HTTP, Security Warning, deprecated HTTP+SSE, `MCP-Session-Id`): https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- MCP specification 2025-11-25, Authorization (OPTIONAL, RFC 9728, PKCE, `resource`, audience validation, error codes): https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- MCP specification 2025-11-25, Security Best Practices (token passthrough, session hijacking, local server compromise): https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices
- MCP specification 2025-11-25, Lifecycle (`initialize` request shape): https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle
- Azure App Service authentication (protected resource metadata preview, `WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES`): https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization
- nginx `if` and `return` directives: https://nginx.org/en/docs/http/ngx_http_rewrite_module.html
- nginx embedded variables (`$http_name`): https://nginx.org/en/docs/http/ngx_http_core_module.html
- nginx ngx_http_map_module (Origin allowlist map): https://nginx.org/en/docs/http/ngx_http_map_module.html
- MCP specification versioning (2026-07-28 is the current revision; 2025-11-25 is a Final, handshake-based revision): https://modelcontextprotocol.io/specification/versioning
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
