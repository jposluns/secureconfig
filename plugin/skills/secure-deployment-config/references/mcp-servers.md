# MCP servers: exposing Model Context Protocol servers safely

MCP (Model Context Protocol) lets AI apps call outside tools; an MCP server provides them, locally or over the web. This guide helps your AI assistant expose one securely, including stdio for single-user workstation tools, narrow credentials, and for HTTP servers a loopback bind, Origin checks, TLS and authentication.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/mcp-servers.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against MCP 2026-07-28, MCP legacy 2025-11-25, and curl minimum 7.75.0; 3 further sources carry no recorded version. Metadata reviewed 2026-09-26; documentation checked September 2026. The guide records 39 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

An MCP server gives a model tools, and every tool it exposes runs with the credentials the server holds. The 2026-07-28 specification defines two transports. Over **stdio** the client launches the server as a subprocess and talks over stdin and stdout: there is no network listener, but the process runs as the launching user with every credential in its environment, so a malicious or careless server is a local compromise, not a network one. Over **Streamable HTTP** the server is a web service with a single endpoint accepting **POST**, and every rule in [authentication.md](authentication.md) applies to it. For a server supporting only this revision, the spec says GET or DELETE to that endpoint SHOULD receive `405 Method Not Allowed`; server-to-client change notifications now flow on a long-lived `subscriptions/listen` POST response stream rather than a standalone GET stream. The older HTTP with SSE transport (protocol version 2024-11-05) is deprecated; Streamable HTTP replaces it. See Streamable HTTP. The spec makes authorization OPTIONAL at the protocol level; this repository does not, so an HTTP MCP server reachable beyond loopback authenticates every request, either natively or through a fronting layer. See Authorization.

**Spec revision.** This guide is written against MCP **2026-07-28**, the **Current** revision. Current means ready for use and still able to receive backwards-compatible changes; it does not mean Final. See MCP versioning. Two distinct changes matter:

1. The `initialize`/`notifications/initialized` handshake is removed, and MCP is stateless. Every request MUST carry `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities` in `params._meta`; clients SHOULD also include `io.modelcontextprotocol/clientInfo`. This per-request metadata supplies the version and capabilities without prior connection state. See the Base protocol and Changelog. Every HTTP POST MUST include `MCP-Protocol-Version`, equal to the body's `_meta` protocol version. `Mcp-Method` MUST mirror `method` on all requests; `Mcp-Name` MUST mirror `params.name` or `params.uri` on `tools/call`, `resources/read`, and `prompts/get` only. Header names are case-insensitive. Missing or malformed required headers, or a header/body mismatch, require HTTP `400` with JSON-RPC `-32020 HeaderMismatch`. An unsupported protocol version requires HTTP `400` with `-32022 UnsupportedProtocolVersionError`. See Streamable HTTP; the Changelog records the error-code renumbering, including `HeaderMismatch` from the draft's `-32001` to `-32020`.
2. `server/discover` is added. Servers MUST implement it; clients MAY call it for up-front version selection or as a stdio compatibility probe. It does not replace negotiation and is not a mandatory first request: per-request `_meta` supplies the negotiation information, and a client can send another RPC directly and handle a version error. See Discovery.

Protocol-level sessions and `Mcp-Session-Id` are removed, as are the standalone GET stream and stream resumability via `Last-Event-ID`. For older-client traffic, a server supporting only 2026-07-28 SHOULD ignore those removed legacy headers and return `405` for GET/DELETE requests. See the Changelog and Streamable HTTP. Readers maintaining older deployments can consult the explicitly **legacy** 2025-11-25 transport reference, a handshake-based Final revision.

## 1. Prefer stdio, and keep HTTP on loopback

- For a single-user tool on a workstation, use the stdio transport. The spec's own guidance for local servers is to "use the `stdio` transport to limit access to just the MCP client" and, if HTTP is used anyway, to require an authorization token or use a Unix domain socket with restricted access. See Security Best Practices.
- Give a stdio server only the environment it needs: the API key for the one service it wraps, not a shell profile full of cloud credentials. Per the spec, stdio servers "retrieve credentials from the environment", which means that environment is the server's whole privilege set ([secrets.md](secrets.md)). See Authorization.
- For Streamable HTTP, the spec's Security Warning says: "When running locally, servers SHOULD bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)". Bind to `127.0.0.1` and publish only a fronting layer, exactly as [ollama.md](ollama.md) does for a model server. Check the SDK or framework you use for its bind-address option; do not assume its default is loopback. See Streamable HTTP.

## 2. Validate `Origin` (DNS rebinding)

The spec requires it: "Servers MUST validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks. If the `Origin` header is present and invalid, servers MUST respond with HTTP 403 Forbidden." The response body MAY be a JSON-RPC error with no `id`. Without this, "attackers could use DNS rebinding to interact with local MCP servers from remote websites": a page in the user's browser resolves its own hostname to `127.0.0.1` and drives the local server. See Streamable HTTP. Do the check in the server (most SDKs have an allowed-origins option; confirm yours is on). A reverse proxy can add a second check in front, using the nginx rewrite module's `if` directive with the nginx core module's `$http_origin` variable:

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

See the nginx map module for the mapping syntax. These proxy checks validate Origin only; the MCP server still performs the required mirror-header/body validation and returns `-32020` on a mismatch. A fronting proxy does not substitute for that validation. See Streamable HTTP, Server Validation.

## 3. TLS

In this guide's deployment pattern, the MCP server itself speaks plain HTTP on loopback. Terminate TLS at the proxy per [nginx.md](nginx.md) or [caddy.md](caddy.md) with a certificate from [free-certificates.md](free-certificates.md), or publish through [cloudflare.md](cloudflare.md) or [tailscale.md](tailscale.md). Bearer tokens cross the network with every request, so the spec requires HTTPS for all authorization server endpoints, and [authentication.md](authentication.md) requires it for every credential. See Authorization Security Considerations, Communication Security.

## 4. Authentication: native OAuth 2.1 or a fronting layer

**Option A, spec authorization.** The MCP server acts as an OAuth 2.1 resource server. See Authorization. The spec's requirements, in its own terms:

- MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC 9728), and the metadata MUST include `authorization_servers` with at least one authorization server. Servers MUST implement at least one discovery mechanism: a `WWW-Authenticate` header carrying `resource_metadata` on `401 Unauthorized` responses, or a well-known URI. Clients MUST support both, following `resource_metadata` when present and otherwise trying the endpoint-path-suffixed well-known URI first, then the root `/.well-known/oauth-protected-resource`. See Authorization Server Discovery.
- Clients "MUST implement PKCE", MUST use `S256` "when technically capable", and "MUST refuse to proceed" if the authorization server's metadata lacks `code_challenge_methods_supported`. See Authorization Security Considerations. Clients MUST send the RFC 8707 `resource` parameter in both authorization and token requests, naming the MCP server's canonical URI. See Authorization.
- Servers "MUST validate that access tokens were issued specifically for them as the intended audience"; invalid or expired tokens get `401`, insufficient scope gets `403`. Servers "MUST NOT accept or transit any other tokens": the token the client presents never travels on to an upstream API. See Authorization. If the server calls upstream APIs, "the access token used at the upstream API is a separate token, issued by the upstream authorization server". See Authorization Security Considerations.
- Tokens go in `Authorization: Bearer ...` on every request, never in the URL. See Authorization. The spec's Authorization, Access Token Usage example still shows a `GET /mcp` bearer request, which is stale under 2026-07-28 because the MCP endpoint is POST-only; this guide does not replicate it.
- MCP 2026-07-28 is stateless: protocol sessions and `Mcp-Session-Id` are removed. See the Changelog. Servers needing cross-call state mint explicit handles. Servers MUST NOT treat possession of a state handle as authentication; servers implementing authorization MUST verify every inbound request. They SHOULD use secure, non-deterministic handles and bind them server-side to the authenticated user, for example by keying state as `<user_id>:<handle>` with the user ID derived from the verified token. See Security Best Practices, State Handle Hijacking.
- **Scope hierarchy:** servers "MUST account for scope hierarchies, where a broader scope implies narrower ones, when deciding whether a token is sufficient" for an operation. Apply that rule in server-side token acceptance. See Authorization, Step-Up Authorization Flow.
- **Refresh tokens:** for public clients, the authorization server MUST rotate refresh tokens. This requirement already existed in 2025-11-25; it is not new in 2026-07-28. Treat it as an identity-provider selection criterion. The current requirement is in Authorization Security Considerations, Token Theft. The MCP server SHOULD NOT advertise `offline_access` in `WWW-Authenticate` scopes or Protected Resource Metadata `scopes_supported`, because refresh tokens are not a resource requirement. See Authorization, Refresh Tokens.

Pick an identity provider from [identity-providers.md](identity-providers.md) as the authorization server; the client-side hygiene in [oidc-integration.md](oidc-integration.md) applies. MCP 2026-07-28 deprecates Dynamic Client Registration in favour of Client ID Metadata Documents (HTTPS-URL client IDs); DCR remains available for compatibility, and clients using it MUST send an appropriate `application_type`. Check which mechanisms the identity provider supports. See Client Registration.

Azure App Service can serve the RFC 9728 document for an app behind its built-in authentication: set the `WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES` application setting to a comma-separated list of the required scopes, and the 401 challenge then carries the metadata URL and scopes. Microsoft marks this **preview** at the time of writing and says the configuration may change ([cloud-identity-proxies.md](cloud-identity-proxies.md) covers the rest of Easy Auth). See Azure App Service authentication.

Client-side authorization implementation details (authorization-response `iss` validation, discovery-metadata issuer identity, Client ID Metadata Documents, refresh-token confidentiality, and OAuth-discovery SSRF) are covered in [mcp-clients.md](mcp-clients.md). Section 6 covers proxying long-lived subscription streams and response caches, which the Origin examples above do not configure.

**Option B, a fronting layer.** Keep the server on loopback and authenticate at the edge: a reverse proxy bearer-token check (the nginx `if ($http_authorization ...)` block in [ollama.md](ollama.md)) or basic auth per [nginx.md](nginx.md)/[caddy.md](caddy.md); Cloudflare Access with a service token for machine clients per [cloudflare.md](cloudflare.md); or an identity-aware proxy per [cloud-identity-proxies.md](cloud-identity-proxies.md). Generate and rotate the token per [machine-auth.md](machine-auth.md).

Be clear about what Option B is. A static bearer token at the proxy is a fronting control, not MCP authorization: it serves no Protected Resource Metadata and no `WWW-Authenticate` challenge with `resource_metadata`, so an MCP client that expects the OAuth discovery flow will not negotiate it. Such clients need the token pre-configured (most clients accept static headers for a server), or Option A.

MFA: MCP has no login dialogue of its own. Under Option A, MFA is whatever the authorization server enforces; under Option B it comes from the identity provider behind Access or the identity-aware proxy. Enforce it there per [mfa.md](mfa.md).

## 5. The credentials the server holds

- Each tool's upstream API key is a secret the server holds on behalf of every caller. Load it from the environment or a secret manager, one key per server and environment, never from the repository ([secrets.md](secrets.md)).
- Least privilege per tool: a read-only tool gets a read-only key. A server that wraps a database, a cloud account, and a mail API with admin credentials turns every prompt injection into an administrator.
- Never forward the client's token upstream (spec: "Token passthrough" is an anti-pattern and "explicitly forbidden"). Log tool calls with the authenticated identity so an incident can be traced. See Security Best Practices.

## 6. Proxy long-lived subscription streams and response caches

The proxy configuration above handles short request/response calls. Two MCP surfaces need more from a fronting layer.

**Subscriptions are a long-lived server-to-client stream.** A `subscriptions/listen` POST opens a `text/event-stream` (Server-Sent Events) response that "opens a long-lived notification stream" and "stays open and delivers notifications until the client cancels it". See Subscriptions. A reverse proxy can break it two ways, and a default nginx does: it buffers the response, so notifications arrive late or batched rather than as they happen, and it closes the upstream connection after an interval with no data. Caddy instead flushes a `text/event-stream` response immediately and sets no read timeout by default, so it needs neither adjustment. Under nginx, disable response buffering and raise the read timeout above the longest expected gap between events:

```nginx
location /mcp {
    proxy_pass http://127.0.0.1:3000;
    proxy_buffering off;          # deliver each event as it arrives, not held in a buffer
    proxy_read_timeout 3600s;     # above the longest idle gap; the 60s default drops a quiet stream
    # keep the Origin, TLS, and Authorization handling from the sections above
}
```

`proxy_buffering off` disables response buffering for the location, which nginx defaults to `on`. Alternatively an MCP server SHOULD send the `X-Accel-Buffering: no` response header, which nginx honours to disable buffering for that one response unless header processing is turned off with `proxy_ignore_headers X-Accel-Buffering;`. `proxy_read_timeout` defaults to 60 seconds and measures the gap between two successive reads, so a stream quieter than that is dropped; size it to the deployment's idle periods, and a server that sends frequent keep-alive comments can keep a shorter timeout. There is no required timeout value; match it to the traffic. Preserve the `text/event-stream` content type and event framing through every intermediary. See the nginx `proxy_buffering` and `proxy_read_timeout` reference, and MCP Streamable HTTP and Subscriptions.

**A shared response cache can cross authorization contexts.** MCP's caching utility carries a `cacheScope`, and the spec is explicit that, for a private-scope response, "Caches MUST NOT be shared across authorization contexts" and that an implementer "MUST NOT rely on `cacheScope` alone to prevent unauthorized access to primitives". See Caching. A fronting cache keyed only on the request path, or on the method and parameters without the caller's identity, will hand one caller's private tool result or filtered list to another. Do not put a generic response cache in front of an MCP server unless it implements MCP's rules: separate private authorization contexts, distinguish methods and result-affecting parameters, and keep the primitive access check independent of any cache hint. A `public`-scope result may be shared even when first obtained through an authenticated endpoint, so the server must classify visibility correctly rather than the cache guessing. For nginx, keep proxy caching off for the MCP location (`proxy_cache off;`). nginx caches nothing by default and caches only `GET`/`HEAD` unless `proxy_cache_methods` adds `POST`, so this hazard appears only where an operator deliberately turns on shared or POST caching in front of the POST-only endpoint. See the nginx `proxy_cache` and `proxy_cache_methods` reference, and MCP Caching.

## Verify

REASONED: following block; the ss listener inventory and the guarded direct-origin probe, per the guide's cited MCP specification 2026-07-28 Streamable HTTP entry (loopback binding) and curl manual entry (exitcode and errormsg, both added in curl 7.75.0). During marking review (October 2026), in the authoring environment, a real ss -tlnp reported `Cannot open netlink socket: Operation not permitted`; the listener inventory could not be established from that run. The direct-origin comparison requires an MCP 2026-07-28 server, fronting layer and second probe host, unavailable in the authoring environment, so neither the exposed result (any HTTP code from your address) nor the fixed one (a refusal or timeout reaching your address, or an answer only from the fronting layer) was observed. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0, then ran with stub ss and curl and no network: unchanged, it printed its substitute-your-own-address refusal; without its set -- line, the paste-the-whole-block refusal; with the set -- line shortened, or given a second value under IFS=0, the exactly-1-value refusal; with 198.51.100.7 substituted, the stub curl received http://198.51.100.7:3000/mcp. The direct-origin request below checks listener reachability, not MCP RPC success: any HTTP response, now typically `400`/`405`, proves that the port answered. Use curl 7.75.0 or newer for the `exitcode` and `errormsg` write-out variables. See the curl manual.

```bash
# REASONED: listener isolation follows the cited deployment guidance; no live MCP 2026-07-28 server is available.
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
    *) curl -q -g -s -o /dev/null --noproxy '*' -X POST --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/mcp" ;;
  esac
)
```

REASONED: preceding block; this Probe 1 paragraph and the listener block above it. Probe 1's expected 401 and exposed discovery result rest on the guide's cited MCP specification 2026-07-28 Authorization and Authorization Server Discovery entries, and the listener block on the entries named in the declaration before it, which also records that block's local runs; Probe 1's own local runs are recorded with the following block. **Probe 1 - REASONED, not demonstrated.** No live MCP 2026-07-28 server is available in the authoring environment. Fixed: the unauthenticated request receives the applicable `401` denial; exposed: it returns an actual discovery result without authentication. A login page, redirect, transport failure, or JSON-RPC error does not demonstrate an exposed MCP result. The expected denial and metadata-discovery alternatives follow Authorization and Authorization Server Discovery.

REASONED: the header shape of the three RPC probe blocks, per the guide's cited MCP specification 2026-07-28 Streamable HTTP entry (request headers, header/body validation) and Discovery entry (request shape). No MCP server is available in the authoring environment to answer a mismatched header with HTTP 400 and -32020, or a matching one without it. During marking review (October 2026) the four server/discover bodies in those blocks parsed as JSON, and in each the MCP-Protocol-Version header equalled the protocol version 2026-07-28 in `params._meta`, Mcp-Method equalled the body's method, clientCapabilities and clientInfo were present, and no Mcp-Name header appeared. `Mcp-Name` is deliberately absent: it is required only for `tools/call`, `resources/read`, and `prompts/get`, not `server/discover`. The `MCP-Protocol-Version` header must equal the body's `_meta` version; all three probes satisfy that requirement by construction. See Streamable HTTP and the Discovery request shape.

REASONED: following block; the unauthenticated server/discover probe and well-known metadata read in the following block, and the placeholder guards of all three RPC probe blocks, per the guide's cited MCP specification 2026-07-28 Authorization and Authorization Server Discovery entries. The authoring environment has no MCP server or authorization server, so neither the fixed 401 nor an exposed discovery result was observed. During marking review (October 2026) the three blocks passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 and ran with a stub curl and no network. Unchanged, each printed its substitute-the-MCP-HTTPS-URL refusal; without its set -- line, the paste-the-whole-block refusal; shortened, its exactly-N-values refusal; and an http:// URL drew the https:// refusal. In the following block an unsubstituted Origin drew the allowed-Origin refusal and a control character the control-character refusal, and with both values substituted the stub received one POST carrying the Origin, MCP-Protocol-Version, Mcp-Method, Content-Type and Accept headers; its illustrative well-known read sits outside the subshell and reached the stub in every run. Replace each RPC probe's placeholders inside the single quotes on its `set --` line, keeping the quotes, and paste the whole subshell block.

```bash
# REASONED: unauthenticated discovery follows MCP 2026-07-28 Authorization and Authorization Server Discovery; no live server is available.
# Unauthenticated server/discover: expect 401 (Option A: the WWW-Authenticate header MAY carry
# resource_metadata; if absent, use the well-known URL below) or the proxy's 401 (Option B).
# A 400 with JSON-RPC -32020 is a HEADER MISMATCH (missing/malformed Mcp-* headers or a
# header/body version disagreement), not an authentication verdict: fix the probe, do not
# read it as a pass or fail of the auth check.
# --noproxy '*' so a client HTTPS_PROXY cannot answer with its own 401/407 in place of the target.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MCP_HTTPS_URL' 'REPLACE_WITH_ALLOWED_ORIGIN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'the set -- line needs exactly 2 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the MCP HTTPS URL; not probing'; exit 2 ;; esac
  case "$1" in https://*) ;; *) echo 'use an https:// URL; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute the allowed Origin; not probing'; exit 2 ;; esac
  case "$1$2" in *[[:cntrl:]]*) echo 'control character in input; not probing'; exit 2 ;; esac
  curl -q -g -si --noproxy '*' -X POST --url "$1" -H "Origin: $2" \
    -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
    -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"check","version":"1.0.0"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
)
# Option A only: FOLLOW the resource_metadata URL from the 401's WWW-Authenticate header WHEN PRESENT
# (the spec permits well-known-only discovery; fall back to /.well-known/oauth-protected-resource/mcp,
# then the root below) and confirm it names your authorization server.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -s --noproxy '*' https://mcp.example.com/.well-known/oauth-protected-resource   # JSON with "authorization_servers"
```

REASONED: preceding block; this Probe 2 paragraph and the unauthenticated discovery block above it. Probe 2's expected 403 and exposed discovery result rest on the guide's cited MCP specification 2026-07-28 Streamable HTTP, Discovery and Caching entries; the block above rests on the entries named in the declaration before it, which also records its local runs, and Probe 2's own local runs are recorded with the following block. **Probe 2 - REASONED, not demonstrated.** No live MCP 2026-07-28 server and valid deployment credential are available in the authoring environment. Establish the allowed-Origin positive control before interpreting the negative request. Require a real `DiscoverResult`, including `resultType:"complete"`, `supportedVersions`, `capabilities`, and the `ttlMs`/`cacheScope` caching hints required for complete discovery results. See Discovery and Caching. Fixed: changing only Origin produces `403`; exposed: the disallowed Origin still receives a discovery result. A `403` counts as an Origin rejection only after the otherwise-identical positive control succeeds. See Streamable HTTP, Security & Endpoint.

REASONED: following block; the header-file handling and the allowed and disallowed Origin pair in the following block, per the guide's cited curl manual entry (header files) and MCP specification 2026-07-28 Streamable HTTP entry (Origin validation). The authoring environment has no MCP server or deployment credential, so neither the fixed 403 nor an exposed discovery result for the disallowed Origin was observed. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 and ran with a stub curl and no network: unchanged, without its set -- line, shortened or with an http:// URL, it printed the matching refusal and exited 2, and an unsubstituted or unreadable header-file path drew its own refusal. With a mode-0600 fixture header file, the stub received -H with @ and the file's path in both calls, the Origin changed from the allowed value to https://attacker.example, and the fixture token appeared in neither argument list. Header files keep credential values out of curl's argv; this does not protect a secret copied into shell history, exposed through tracing, or readable by the account owner. See [secrets.md](secrets.md) and the curl manual.

```bash
# REASONED: Origin rejection follows MCP 2026-07-28 Streamable HTTP security requirements; no live server or deployment credential is available.
# Origin control (DNS rebinding): a wrong Origin must be rejected even WITH a valid credential. Run the
# positive control first (ALLOWED Origin + a real server/discover body: require an actual discovery
# result - resultType:"complete", supportedVersions, capabilities, and ttlMs/cacheScope - not merely a 2xx
# status; a login page or a JSON-RPC error is not a positive control). Then the SAME request with only
# the Origin changed to a disallowed value (expect 403), so the 403 is attributable to the Origin check.
# A 401 here is an auth failure and a 400 -32020 is a header mismatch: neither is an Origin verdict.
# Keep the credential in a mode-0600 header file (secrets.md), never on the command line:
# REPLACE_WITH_AUTH_HEADER_FILE holds a line like "Authorization: Bearer <token>".
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MCP_HTTPS_URL' 'REPLACE_WITH_ALLOWED_ORIGIN' 'REPLACE_WITH_AUTH_HEADER_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'the set -- line needs exactly 3 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the MCP HTTPS URL; not probing'; exit 2 ;; esac
  case "$1" in https://*) ;; *) echo 'use an https:// URL; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute the allowed Origin; not probing'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*) echo 'substitute the mode-0600 auth-header file path on the set -- line above; not probing'; exit 2 ;; esac
  [ -r "$3" ] || { echo 'header file not readable; not probing'; exit 2; }
  case "$1$2$3" in *[[:cntrl:]]*) echo 'control character in input; not probing'; exit 2 ;; esac
  # Allowed Origin + valid credential: require a real DiscoverResult.
  curl -q -g -si --noproxy '*' -X POST --url "$1" -H "Origin: $2" \
    -H "@$3" \
    -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
    -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"check","version":"1.0.0"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
  # Only the Origin changed to a disallowed value: expect 403.
  curl -q -g -si --noproxy '*' -X POST --url "$1" -H 'Origin: https://attacker.example' \
    -H "@$3" \
    -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
    -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"check","version":"1.0.0"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
)
```

REASONED: following block; the wrong-audience probe in the following block, per the guide's cited MCP specification 2026-07-28 Authorization entry (audience validation, error codes). During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 and ran with a stub curl and no network: unchanged, without its set -- line, shortened, with an http:// URL, and with an unsubstituted or unreadable header-file path, it printed the matching refusal and exited 2; with a mode-0600 fixture header file, the stub received -H with @ and the file's path, and the fixture token did not appear in its arguments. **Probe 3 - REASONED, not demonstrated.** The authoring environment has no live authorization server with a second registered resource. Use an otherwise valid, unexpired token for that other resource, keeping the endpoint, allowed Origin, and request body unchanged. The audience-validation requirement and `401` outcome come from Authorization and Authorization Security Considerations.

```bash
# REASONED: wrong-audience check follows MCP 2026-07-28 Authorization and Authorization Security Considerations;
# no live authorization server with a second registered resource is available here.
# Wrong audience (Option A): a token issued for a DIFFERENT resource must fail with 401. Use an
# otherwise valid, unexpired token whose aud names another resource (a forged or expired token would
# fail for the wrong reason), in its own mode-0600 header file. Fixed: 401, the audience is rejected.
# Exposed: a real DiscoverResult returned for a token minted for another audience, which the spec's
# audience-validation MUST forbids. Require resultType:"complete", supportedVersions, capabilities,
# ttlMs, and cacheScope; a login page or JSON-RPC error, even with 2xx, is not acceptance.
# A 400 -32020 is a header mismatch, not an audience verdict.
# This step is reasoned, not demonstrated in the authoring environment: it needs a second resource
# registered at your authorization server.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MCP_HTTPS_URL' 'REPLACE_WITH_ALLOWED_ORIGIN' 'REPLACE_WITH_WRONG_AUDIENCE_HEADER_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'the set -- line needs exactly 3 values; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the MCP HTTPS URL; not probing'; exit 2 ;; esac
  case "$1" in https://*) ;; *) echo 'use an https:// URL; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute the allowed Origin; not probing'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*) echo 'substitute the mode-0600 wrong-audience file path on the set -- line above; not probing'; exit 2 ;; esac
  [ -r "$3" ] || { echo 'header file not readable; not probing'; exit 2; }
  case "$1$2$3" in *[[:cntrl:]]*) echo 'control character in input; not probing'; exit 2 ;; esac
  # Otherwise-valid token, wrong aud: require 401.
  curl -q -g -si --noproxy '*' -X POST --url "$1" -H "Origin: $2" \
    -H "@$3" \
    -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
    -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"check","version":"1.0.0"},"io.modelcontextprotocol/clientCapabilities":{}}}}'
)
```

## Common mistakes

- Binding the HTTP transport to `0.0.0.0` "for Docker" and leaving it there. Publish the container port on `127.0.0.1` only ([docker.md](docker.md)).
- Treating stdio as safe because it has no port: the server runs as you, with your environment.
- Accepting any token from your identity provider without checking the audience, so a token issued for another API also opens the MCP server.
- Passing the caller's token to the upstream API, which makes the upstream trust a token it never issued and loses the audit trail.
- Assuming the MCP endpoint still answers `GET` or carries an `Mcp-Session-Id`: under 2026-07-28 the endpoint is POST-only and protocol sessions are removed; a server supporting only this revision SHOULD return `405` for GET/DELETE. See Streamable HTTP.
- Treating possession of a state handle as authentication: the spec forbids it; verify every inbound request. See Security Best Practices.

## Sources (checked September 2026)

- MCP specification 2026-07-28, Transports, Streamable HTTP (POST endpoint, Origin validation, loopback binding, request headers, header/body validation, removed legacy mechanisms): https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http
- MCP specification 2026-07-28, Base protocol (per-request `_meta`, protocol version, client capabilities and identity): https://modelcontextprotocol.io/specification/2026-07-28/basic/index
- MCP specification 2026-07-28, Discovery, `server/discover` (server implementation requirement, optional client call, request and response shape): https://modelcontextprotocol.io/specification/2026-07-28/server/discover
- MCP specification 2026-07-28, Changelog (handshake and session removal, subscription streams, error-code renumbering): https://modelcontextprotocol.io/specification/2026-07-28/changelog
- MCP specification 2026-07-28, Authorization (OPTIONAL, OAuth resource server, credentials, `resource`, audience validation, error codes, scope hierarchy, `offline_access`): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- MCP specification 2026-07-28, Authorization Server Discovery (RFC 9728 metadata, `authorization_servers`, challenge and well-known discovery): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery
- MCP specification 2026-07-28, Authorization Security Considerations (PKCE, refresh-token rotation, HTTPS, separate upstream tokens): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations
- MCP specification 2026-07-28, Client Registration (DCR deprecation, Client ID Metadata Documents, `application_type`): https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration
- MCP specification 2026-07-28, Security Best Practices (local-server controls, state-handle hijacking, forbidden token passthrough): https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices
- MCP specification 2026-07-28, Caching (`ttlMs` and `cacheScope` required on complete discovery results): https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching
- MCP specification 2026-07-28, Subscriptions (`subscriptions/listen` long-lived SSE notification stream): https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions
- MCP specification 2025-11-25, Transports - **legacy** handshake/session shape, for deployments not yet on 2026-07-28: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- Azure App Service authentication (protected resource metadata preview, `WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES`, comma-separated scopes): https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization
- nginx rewrite module (`if` and `return` directives): https://nginx.org/en/docs/http/ngx_http_rewrite_module.html
- nginx core module (embedded `$http_name` variables): https://nginx.org/en/docs/http/ngx_http_core_module.html
- nginx map module (Origin allowlist map): https://nginx.org/en/docs/http/ngx_http_map_module.html
- nginx proxy module (`proxy_buffering`, `proxy_read_timeout`, `X-Accel-Buffering`, `proxy_cache`, `proxy_cache_methods`): https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- Caddy reverse_proxy directive (streaming: a `text/event-stream` response is flushed immediately; the HTTP transport `read_timeout` default is no timeout): https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- MCP specification versioning (2026-07-28 is the Current revision; 2025-11-25 and earlier are Final, handshake-based revisions): https://modelcontextprotocol.io/specification/versioning
- curl manual (leading `-q`, header files, `exitcode` and `errormsg`, both added in curl 7.75.0): https://curl.se/docs/manpage.html


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- mcp: MCP (2026-07-28)
- legacy: MCP legacy (2025-11-25)
- azure: Azure App Service (unknown)
- nginx: nginx (unknown)
- caddy: Caddy (unknown)
- curl: curl minimum (7.75.0)

Claims (full source mapping in the JSON block below):

- revision (REASONED; mcp, legacy): Current revision can receive compatible changes; legacy 2025-11-25 is Final and handshake-based.
- stdio (REASONED; mcp): Prefer local stdio; subprocess inherits user privileges and supplied environment credentials; restrict that environment.
- http (REASONED; mcp): Streamable HTTP uses one POST endpoint; 2024-11-05 HTTP+SSE is deprecated.
- metadata (REASONED; mcp): No initialize handshake; each request needs protocolVersion and clientCapabilities in params._meta; clientInfo is recommended.
- headers (REASONED; mcp): MCP-Protocol-Version mirrors body version; Mcp-Method mirrors method; Mcp-Name is required only for tools/call, resources/read and prompts/get.
- header-error (REASONED; mcp): Missing/malformed required headers or body mismatch require HTTP 400 and -32020; unsupported version requires 400 and -32022.
- discover (REASONED; mcp): Servers MUST implement server/discover; clients MAY call it, without a mandatory first-call requirement.
- legacy-removal (REASONED; mcp): Sessions, Mcp-Session-Id, GET stream and Last-Event-ID resumability are removed; revision-only servers SHOULD ignore legacy headers and return GET/DELETE 405.
- bind (REASONED; mcp): Local HTTP SHOULD bind localhost; explicitly bind 127.0.0.1 and expose only the fronting layer, checking framework options.
- origin (REASONED; mcp): Validate Origin; a present invalid value requires 403, optionally a JSON-RPC error without id.
- origin-proxy (REASONED; nginx): nginx /mcp forwards to 127.0.0.1:3000; the if rule rejects missing Origin, while the map variant allows it and rejects wrong origins.
- origin-limits (REASONED; mcp): Proxy Origin checks do not replace server mirror-header/body validation.
- tls (REASONED; mcp): Use loopback HTTP with TLS ingress; authorization-server endpoints require HTTPS.
- auth (REASONED; mcp): Protocol authorization is optional; this guide requires authentication beyond loopback, with OAuth 2.1 resource-server or fronting controls.
- resource-metadata (REASONED; mcp): RFC 9728 metadata must name at least one authorization server; server supports challenge or well-known discovery, client both, path-suffixed then root fallback.
- pkce (REASONED; mcp): Clients require PKCE, S256 when capable, and refuse metadata lacking code_challenge_methods_supported.
- resource (REASONED; mcp): Clients send canonical MCP resource URI in authorization and token requests.
- audience (REASONED; mcp): Validate intended audience; invalid/expired tokens receive 401 and insufficient scope 403.
- upstream (REASONED; mcp): Never pass caller tokens upstream; use separate upstream tokens, least-privilege keys and identity-attributed tool logs.
- bearer (REASONED; mcp): Bearer token goes in Authorization on every request, never the URL; the authorization GET /mcp example is identified as stale.
- handles (REASONED; mcp): State handles are not authentication; verify every request, use unpredictable handles and bind them to the verified user.
- scopes (REASONED; mcp): Server token acceptance MUST account for broader scopes implying narrower ones.
- refresh (REASONED; mcp): Public-client refresh tokens MUST rotate; servers SHOULD NOT advertise offline_access as a resource scope.
- registration (REASONED; mcp): CIMD is preferred over deprecated DCR; DCR remains compatible and requires appropriate application_type.
- azure-prm (REASONED; azure): Preview WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES takes comma-separated scopes and adds metadata URL/scopes to the 401 challenge.
- fronting (REASONED; mcp): Static proxy bearer auth requires preconfigured client headers; it does not implement MCP OAuth metadata negotiation.
- mfa (REASONED; mcp): Enforce human MFA at the authorization server or fronting identity provider; MCP has no login dialogue.
- secrets (REASONED; mcp): Supply separate upstream keys per server/environment from environment or secret storage, with least privilege.
- subscriptions (REASONED; mcp): subscriptions/listen POST opens a long-lived text/event-stream until cancelled; preserve framing and content type.
- nginx-buffer (REASONED; nginx, mcp): nginx buffers by default; proxy_buffering off or honored X-Accel-Buffering: no permits immediate events.
- nginx-timeout (REASONED; nginx, mcp): proxy_read_timeout defaults to 60s between reads; example 3600s must exceed expected idle gaps, with keep-alives as an alternative.
- caddy-stream (REASONED; caddy): Caddy flushes text/event-stream immediately and defaults to no read timeout.
- cache (REASONED; mcp): Private caches must separate authorization contexts and result-affecting inputs; cacheScope never replaces access checks; public results may be shared.
- nginx-cache (REASONED; nginx): proxy_cache off keeps caching disabled; default methods are GET/HEAD, and POST caching needs explicit configuration.
- verify-network (REASONED; mcp, curl): Inventory listeners and probe actual direct origin; any HTTP response proves reachability, local errors and unexplained timeouts are inconclusive.
- verify-anonymous (REASONED; mcp): Unauthenticated discovery should get 401; actual discovery data is exposure, while redirects, login pages and RPC/transport errors are inconclusive.
- verify-origin (REASONED; mcp): Require valid-credential allowed-Origin DiscoverResult, including complete/version/capabilities/cache hints; changing only Origin should yield 403.
- verify-audience (REASONED; mcp): Otherwise-valid token for another resource should get 401, not DiscoverResult; no second-resource authorization server was available.
- verify-credential-file (REASONED; curl): Mode-0600 header files keep credentials out of curl argv, without protecting history, tracing or account-owner access.

````json
{
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "107daa3cbc37b9666249b278fb96792e7ba3ed712bbb07018b6393d15a17f36a",
  "components": {
    "mcp": {
      "name": "MCP",
      "basis": "2026-07-28",
      "sources": {
        "s6e1c66cfb825": "https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http",
        "se8d957787d4b": "https://modelcontextprotocol.io/specification/2026-07-28/basic/index",
        "s1d962c091f09": "https://modelcontextprotocol.io/specification/2026-07-28/server/discover",
        "sa739f7343f18": "https://modelcontextprotocol.io/specification/2026-07-28/changelog",
        "s34fabf499cb7": "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization",
        "s117c3edbfcd7": "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery",
        "s4b9b953ca683": "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations",
        "s5655f61af2a0": "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration",
        "s4903497743e8": "https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices",
        "s047fe3fd0dc0": "https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching",
        "s7345b33e447b": "https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions",
        "sa55ad56b64e9": "https://modelcontextprotocol.io/specification/versioning"
      }
    },
    "legacy": {
      "name": "MCP legacy",
      "basis": "2025-11-25",
      "sources": {
        "s937fae6437b3": "https://modelcontextprotocol.io/specification/2025-11-25/basic/transports"
      }
    },
    "azure": {
      "name": "Azure App Service",
      "basis": "unknown",
      "sources": {
        "s5c4dc1862d97": "https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization"
      }
    },
    "nginx": {
      "name": "nginx",
      "basis": "unknown",
      "sources": {
        "sf0bc2adae8cb": "https://nginx.org/en/docs/http/ngx_http_rewrite_module.html",
        "s40bdf1af1596": "https://nginx.org/en/docs/http/ngx_http_core_module.html",
        "s75350e9e4e15": "https://nginx.org/en/docs/http/ngx_http_map_module.html",
        "sf3430c5a0b22": "https://nginx.org/en/docs/http/ngx_http_proxy_module.html"
      }
    },
    "caddy": {
      "name": "Caddy",
      "basis": "unknown",
      "sources": {
        "s3865a73ccda3": "https://caddyserver.com/docs/caddyfile/directives/reverse_proxy"
      }
    },
    "curl": {
      "name": "curl minimum",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "revision": {"text": "Current revision can receive compatible changes; legacy 2025-11-25 is Final and handshake-based.", "components": ["mcp", "legacy"], "sources": ["mcp:sa55ad56b64e9", "legacy:s937fae6437b3"], "status": "REASONED"},
    "stdio": {"text": "Prefer local stdio; subprocess inherits user privileges and supplied environment credentials; restrict that environment.", "components": ["mcp"], "sources": ["mcp:s4903497743e8", "mcp:s34fabf499cb7"], "status": "REASONED"},
    "http": {"text": "Streamable HTTP uses one POST endpoint; 2024-11-05 HTTP+SSE is deprecated.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825"], "status": "REASONED"},
    "metadata": {"text": "No initialize handshake; each request needs protocolVersion and clientCapabilities in params._meta; clientInfo is recommended.", "components": ["mcp"], "sources": ["mcp:se8d957787d4b", "mcp:sa739f7343f18"], "status": "REASONED"},
    "headers": {"text": "MCP-Protocol-Version mirrors body version; Mcp-Method mirrors method; Mcp-Name is required only for tools/call, resources/read and prompts/get.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825"], "status": "REASONED"},
    "header-error": {"text": "Missing/malformed required headers or body mismatch require HTTP 400 and -32020; unsupported version requires 400 and -32022.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825", "mcp:sa739f7343f18"], "status": "REASONED"},
    "discover": {"text": "Servers MUST implement server/discover; clients MAY call it, without a mandatory first-call requirement.", "components": ["mcp"], "sources": ["mcp:s1d962c091f09"], "status": "REASONED"},
    "legacy-removal": {"text": "Sessions, Mcp-Session-Id, GET stream and Last-Event-ID resumability are removed; revision-only servers SHOULD ignore legacy headers and return GET/DELETE 405.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825", "mcp:sa739f7343f18"], "status": "REASONED"},
    "bind": {"text": "Local HTTP SHOULD bind localhost; explicitly bind 127.0.0.1 and expose only the fronting layer, checking framework options.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825", "mcp:s4903497743e8"], "status": "REASONED"},
    "origin": {"text": "Validate Origin; a present invalid value requires 403, optionally a JSON-RPC error without id.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825"], "status": "REASONED"},
    "origin-proxy": {"text": "nginx /mcp forwards to 127.0.0.1:3000; the if rule rejects missing Origin, while the map variant allows it and rejects wrong origins.", "components": ["nginx"], "sources": ["nginx:sf0bc2adae8cb", "nginx:s40bdf1af1596", "nginx:s75350e9e4e15"], "status": "REASONED"},
    "origin-limits": {"text": "Proxy Origin checks do not replace server mirror-header/body validation.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825"], "status": "REASONED"},
    "tls": {"text": "Use loopback HTTP with TLS ingress; authorization-server endpoints require HTTPS.", "components": ["mcp"], "sources": ["mcp:s4b9b953ca683"], "status": "REASONED"},
    "auth": {"text": "Protocol authorization is optional; this guide requires authentication beyond loopback, with OAuth 2.1 resource-server or fronting controls.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s4903497743e8"], "status": "REASONED"},
    "resource-metadata": {"text": "RFC 9728 metadata must name at least one authorization server; server supports challenge or well-known discovery, client both, path-suffixed then root fallback.", "components": ["mcp"], "sources": ["mcp:s117c3edbfcd7"], "status": "REASONED"},
    "pkce": {"text": "Clients require PKCE, S256 when capable, and refuse metadata lacking code_challenge_methods_supported.", "components": ["mcp"], "sources": ["mcp:s4b9b953ca683"], "status": "REASONED"},
    "resource": {"text": "Clients send canonical MCP resource URI in authorization and token requests.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7"], "status": "REASONED"},
    "audience": {"text": "Validate intended audience; invalid/expired tokens receive 401 and insufficient scope 403.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7"], "status": "REASONED"},
    "upstream": {"text": "Never pass caller tokens upstream; use separate upstream tokens, least-privilege keys and identity-attributed tool logs.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s4b9b953ca683", "mcp:s4903497743e8"], "status": "REASONED"},
    "bearer": {"text": "Bearer token goes in Authorization on every request, never the URL; the authorization GET /mcp example is identified as stale.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s6e1c66cfb825"], "status": "REASONED"},
    "handles": {"text": "State handles are not authentication; verify every request, use unpredictable handles and bind them to the verified user.", "components": ["mcp"], "sources": ["mcp:s4903497743e8"], "status": "REASONED"},
    "scopes": {"text": "Server token acceptance MUST account for broader scopes implying narrower ones.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7"], "status": "REASONED"},
    "refresh": {"text": "Public-client refresh tokens MUST rotate; servers SHOULD NOT advertise offline_access as a resource scope.", "components": ["mcp"], "sources": ["mcp:s4b9b953ca683", "mcp:s34fabf499cb7"], "status": "REASONED"},
    "registration": {"text": "CIMD is preferred over deprecated DCR; DCR remains compatible and requires appropriate application_type.", "components": ["mcp"], "sources": ["mcp:s5655f61af2a0"], "status": "REASONED"},
    "azure-prm": {"text": "Preview WEBSITE_AUTH_PRM_DEFAULT_WITH_SCOPES takes comma-separated scopes and adds metadata URL/scopes to the 401 challenge.", "components": ["azure"], "sources": ["azure:s5c4dc1862d97"], "status": "REASONED"},
    "fronting": {"text": "Static proxy bearer auth requires preconfigured client headers; it does not implement MCP OAuth metadata negotiation.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s117c3edbfcd7"], "status": "REASONED"},
    "mfa": {"text": "Enforce human MFA at the authorization server or fronting identity provider; MCP has no login dialogue.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7"], "status": "REASONED"},
    "secrets": {"text": "Supply separate upstream keys per server/environment from environment or secret storage, with least privilege.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s4903497743e8"], "status": "REASONED"},
    "subscriptions": {"text": "subscriptions/listen POST opens a long-lived text/event-stream until cancelled; preserve framing and content type.", "components": ["mcp"], "sources": ["mcp:s7345b33e447b", "mcp:s6e1c66cfb825"], "status": "REASONED"},
    "nginx-buffer": {"text": "nginx buffers by default; proxy_buffering off or honored X-Accel-Buffering: no permits immediate events.", "components": ["nginx", "mcp"], "sources": ["nginx:sf3430c5a0b22", "mcp:s6e1c66cfb825"], "status": "REASONED"},
    "nginx-timeout": {"text": "proxy_read_timeout defaults to 60s between reads; example 3600s must exceed expected idle gaps, with keep-alives as an alternative.", "components": ["nginx", "mcp"], "sources": ["nginx:sf3430c5a0b22", "mcp:s6e1c66cfb825"], "status": "REASONED"},
    "caddy-stream": {"text": "Caddy flushes text/event-stream immediately and defaults to no read timeout.", "components": ["caddy"], "sources": ["caddy:s3865a73ccda3"], "status": "REASONED"},
    "cache": {"text": "Private caches must separate authorization contexts and result-affecting inputs; cacheScope never replaces access checks; public results may be shared.", "components": ["mcp"], "sources": ["mcp:s047fe3fd0dc0"], "status": "REASONED"},
    "nginx-cache": {"text": "proxy_cache off keeps caching disabled; default methods are GET/HEAD, and POST caching needs explicit configuration.", "components": ["nginx"], "sources": ["nginx:sf3430c5a0b22"], "status": "REASONED"},
    "verify-network": {"text": "Inventory listeners and probe actual direct origin; any HTTP response proves reachability, local errors and unexplained timeouts are inconclusive.", "components": ["mcp", "curl"], "sources": ["mcp:s6e1c66cfb825", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-anonymous": {"text": "Unauthenticated discovery should get 401; actual discovery data is exposure, while redirects, login pages and RPC/transport errors are inconclusive.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s117c3edbfcd7", "mcp:s1d962c091f09"], "status": "REASONED", "verify": [2]},
    "verify-origin": {"text": "Require valid-credential allowed-Origin DiscoverResult, including complete/version/capabilities/cache hints; changing only Origin should yield 403.", "components": ["mcp"], "sources": ["mcp:s6e1c66cfb825", "mcp:s1d962c091f09", "mcp:s047fe3fd0dc0"], "status": "REASONED", "verify": [3]},
    "verify-audience": {"text": "Otherwise-valid token for another resource should get 401, not DiscoverResult; no second-resource authorization server was available.", "components": ["mcp"], "sources": ["mcp:s34fabf499cb7", "mcp:s4b9b953ca683", "mcp:s1d962c091f09", "mcp:s047fe3fd0dc0"], "status": "REASONED", "verify": [4]},
    "verify-credential-file": {"text": "Mode-0600 header files keep credentials out of curl argv, without protecting history, tracing or account-owner access.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [3, 4]}
  }
}
````
<!-- version-basis:end -->
