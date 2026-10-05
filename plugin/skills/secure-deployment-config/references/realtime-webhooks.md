---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "b4229dbd00c95e52e2daf9e9e298fe82193f7ca81d4814f63cae05d968c42a25",
  "components": {
    "browser": {
      "name": "Browser API and living standards",
      "basis": "unknown",
      "sources": {
        "sb2011b7b2751": "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket",
        "scc66a82750c7": "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events",
        "sf47a21cc6a1c": "https://html.spec.whatwg.org/multipage/server-sent-events.html",
        "s0fe3abea9d8d": "https://fetch.spec.whatwg.org/#append-a-request-origin-header"
      }
    },
    "websocket": {
      "name": "WebSocket protocol",
      "basis": "RFC 6455",
      "sources": {
        "sbdde15b3166d": "https://www.rfc-editor.org/rfc/rfc6455.html"
      }
    },
    "owasp": {
      "name": "OWASP guidance",
      "basis": "unknown",
      "sources": {
        "sfbb0cddfdc41": "https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html",
        "s7eb820e1e53b": "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
        "s10c2347db109": "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
        "sd95014c37d6f": "https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html",
        "s26a987a1053b": "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"
      }
    },
    "github": {
      "name": "GitHub webhooks documentation",
      "basis": "unknown",
      "sources": {
        "s54f0b41284b0": "https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries",
        "seccc4a52ea14": "https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks",
        "s31c140d2cfa9": "https://docs.github.com/en/webhooks/webhook-events-and-payloads"
      }
    },
    "stripe": {
      "name": "Stripe webhooks documentation",
      "basis": "unknown",
      "sources": {
        "s106b78b02797": "https://docs.stripe.com/webhooks#verify-official-libraries",
        "s197f8ab6b63f": "https://docs.stripe.com/webhooks/signature"
      }
    },
    "stripe-node": {
      "name": "stripe-node",
      "basis": "v18.5.0",
      "sources": {
        "s6cef5da6ee15": "https://raw.githubusercontent.com/stripe/stripe-node/v18.5.0/src/Webhooks.ts"
      }
    },
    "stripe-python": {
      "name": "stripe-python",
      "basis": "v12.5.0",
      "sources": {
        "sa38abcfb0132": "https://raw.githubusercontent.com/stripe/stripe-python/v12.5.0/stripe/_webhook.py"
      }
    },
    "node": {
      "name": "Node.js crypto documentation",
      "basis": "unknown",
      "sources": {
        "s215f593c0770": "https://nodejs.org/docs/latest-v22.x/api/crypto.html#cryptotimingsafeequala-b"
      }
    },
    "traefik": {
      "name": "Traefik timeout reference",
      "basis": "v3.5",
      "sources": {
        "sd6ad276040b7": "https://doc.traefik.io/traefik/v3.5/reference/install-configuration/entrypoints/",
        "scad09024d298": "https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/buffering/",
        "s5888553b0970": "https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/inflightreq/",
        "s437d7eb2ec16": "https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/ratelimit/"
      }
    },
    "proxy": {
      "name": "Caddy and nginx timeout documentation",
      "basis": "unknown",
      "sources": {
        "sf22449866dac": "https://caddyserver.com/docs/caddyfile/options#timeouts",
        "s7cc695452ecc": "https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "python": {
      "name": "Python os documentation",
      "basis": "unknown",
      "sources": {
        "s767fa9623dba": "https://docs.python.org/3/library/os.html#os.fdopen"
      }
    },
    "nginx-source": {
      "name": "nginx source",
      "basis": "release-1.26.3",
      "sources": {
        "s80c7f2e4622c": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_core_module.c#L348-L353",
        "s0ac063f54b7d": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_limit_conn_module.c#L100-L105",
        "s86004e697595": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_limit_req_module.c#L113-L118"
      }
    },
    "haproxy": {
      "name": "HAProxy",
      "basis": "3.0",
      "sources": {
        "se90dfdfcf910": "https://docs.haproxy.org/3.0/configuration.html#7.3.6-req.body_size"
      }
    }
  },
  "claims": {
    "private": {"text": "Restrict application origins to intended proxies; separately inventory containers, IPv6 and management endpoints.", "components": ["owasp"], "sources": ["owasp:sfbb0cddfdc41"], "status": "REASONED"},
    "tls": {"text": "Use WSS and HTTPS with certificate verification; protect untrusted proxy-to-app hops with authenticated TLS.", "components": ["websocket", "owasp", "github"], "sources": ["websocket:sbdde15b3166d", "owasp:sfbb0cddfdc41", "github:seccc4a52ea14"], "status": "REASONED"},
    "credentials": {"text": "Disable anonymous/default credentials and separate minimally scoped publisher, subscriber, sender and admin identities.", "components": ["owasp"], "sources": ["owasp:s10c2347db109", "owasp:s26a987a1053b"], "status": "REASONED"},
    "mfa": {"text": "Keep admin UIs private with IdP or fronting MFA; machine webhook deliveries use signatures.", "components": ["owasp", "github"], "sources": ["owasp:sd95014c37d6f", "github:s54f0b41284b0"], "status": "REASONED"},
    "ws-headers": {"text": "Browser WebSocket accepts a URL and protocols, with no custom Authorization-header argument.", "components": ["browser"], "sources": ["browser:sb2011b7b2751"], "status": "REASONED"},
    "ws-origin": {"text": "Eligible cookies may accompany handshakes; reject missing or non-allowlisted Origin before protected logic to prevent CSWSH.", "components": ["owasp", "websocket"], "sources": ["owasp:sfbb0cddfdc41", "websocket:sbdde15b3166d"], "status": "REASONED"},
    "ws-token": {"text": "Authenticate a short-lived first-message token before protected use; rotate it and keep credentials out of URLs and subprotocols.", "components": ["owasp", "browser"], "sources": ["owasp:sfbb0cddfdc41", "browser:sb2011b7b2751"], "status": "REASONED"},
    "ws-identity": {"text": "Origin is forgeable outside browsers; independently authenticate, and do not let a stolen cookie alone obtain the first-message token.", "components": ["owasp", "websocket"], "sources": ["owasp:sfbb0cddfdc41", "websocket:sbdde15b3166d"], "status": "REASONED"},
    "ws-deadline": {"text": "Allow no protected operation before authentication and impose a bounded authentication deadline.", "components": ["owasp"], "sources": ["owasp:sfbb0cddfdc41"], "status": "REASONED"},
    "authorization": {"text": "Authorize each channel, tenant and operation, including SSE subscriptions; revalidate and terminate expired or revoked long-lived access.", "components": ["owasp"], "sources": ["owasp:sfbb0cddfdc41", "owasp:s10c2347db109"], "status": "REASONED"},
    "sse": {"text": "EventSource uses GET without custom Authorization headers; eligible cookies and cross-origin withCredentials remain browser-policy dependent.", "components": ["browser"], "sources": ["browser:scc66a82750c7", "browser:sf47a21cc6a1c"], "status": "REASONED"},
    "sse-origin": {"text": "Authenticate subscriptions and allow only trusted credentialed CORS origins; legitimate same-origin GET may omit Origin.", "components": ["browser", "owasp"], "sources": ["browser:sf47a21cc6a1c", "browser:s0fe3abea9d8d", "owasp:s10c2347db109"], "status": "REASONED"},
    "sse-fetch": {"text": "Keep SSE GET side-effect free; use fetch with a ReadableStream when header tokens are needed.", "components": ["browser"], "sources": ["browser:scc66a82750c7", "browser:sf47a21cc6a1c"], "status": "REASONED"},
    "github-signature": {"text": "Verify raw-body HMAC-SHA256 using X-Hub-Signature-256 and constant-time comparison.", "components": ["github"], "sources": ["github:s54f0b41284b0"], "status": "REASONED"},
    "signature-shape": {"text": "Reject missing/malformed sha256= plus 64-hex signatures; timingSafeEqual needs equal buffer lengths and exceptions must fail closed.", "components": ["github", "node"], "sources": ["github:s54f0b41284b0", "node:s215f593c0770"], "status": "REASONED"},
    "stripe-signature": {"text": "Stripe signs timestamp, dot and raw body with the endpoint secret; use official verification libraries.", "components": ["stripe"], "sources": ["stripe:s106b78b02797", "stripe:s197f8ab6b63f"], "status": "REASONED"},
    "stripe-tolerance": {"text": "stripe-node v18.5.0 and stripe-python v12.5.0 default to 300 seconds; set a positive tolerance and test stale requests because zero handling differs.", "components": ["stripe-node", "stripe-python"], "sources": ["stripe-node:s6cef5da6ee15", "stripe-python:sa38abcfb0132"], "status": "REASONED"},
    "github-replay": {"text": "GitHub signs neither a timestamp nor X-GitHub-Delivery; changed delivery IDs retain valid signatures, so ID deduplication cannot establish freshness.", "components": ["github"], "sources": ["github:s54f0b41284b0", "github:s31c140d2cfa9"], "status": "REASONED"},
    "idempotency": {"text": "Use atomic durable idempotency from authenticated payload data; body-digest caches only suppress identical bodies during retention and can suppress legitimate repeats.", "components": ["github"], "sources": ["github:s54f0b41284b0", "github:seccc4a52ea14"], "status": "REASONED"},
    "stripe-replay": {"text": "A signed timestamp limits age, not replay inside the window; deduplicate authenticated event IDs after signature and timestamp validation.", "components": ["stripe"], "sources": ["stripe:s106b78b02797"], "status": "REASONED"},
    "raw-body": {"text": "Verify exact received bytes before JSON reserialization or handler effects.", "components": ["github", "stripe"], "sources": ["github:s54f0b41284b0", "stripe:s197f8ab6b63f"], "status": "REASONED"},
    "csrf": {"text": "Scope any webhook CSRF exemption to the one route and method.", "components": ["stripe"], "sources": ["stripe:s106b78b02797"], "status": "REASONED"},
    "webhook-secret": {"text": "Require a configured strong GitHub secret, reject unsigned delivery, and use distinct protected, rotated endpoint secrets kept out of URLs and logs.", "components": ["github", "owasp"], "sources": ["github:seccc4a52ea14", "owasp:s26a987a1053b"], "status": "REASONED"},
    "stripe-secrets": {"text": "Stripe test/live and Dashboard/CLI-forwarding endpoint secrets differ.", "components": ["stripe"], "sources": ["stripe:s197f8ab6b63f"], "status": "REASONED"},
    "sender-ip": {"text": "Provider IP allowlists supplement signatures; trust forwarded client addresses only through a configured proxy chain.", "components": ["github"], "sources": ["github:seccc4a52ea14"], "status": "REASONED"},
    "proxy-limits": {"text": "Bound HTTP body size, concurrency and timeouts separately; proxy capability summaries refer to local guides and need current vendor confirmation.", "components": ["traefik", "proxy", "nginx-source", "haproxy"], "sources": ["traefik:sd6ad276040b7", "proxy:sf22449866dac", "proxy:s7cc695452ecc", "nginx-source:s80c7f2e4622c", "nginx-source:s0ac063f54b7d", "nginx-source:s86004e697595", "traefik:scad09024d298", "traefik:s5888553b0970", "traefik:s437d7eb2ec16", "haproxy:se90dfdfcf910"], "status": "REASONED"},
    "message-limits": {"text": "After WebSocket upgrade, enforce per-message authorization and rate limits; connection limits do not bound messages or jobs.", "components": ["owasp"], "sources": ["owasp:sfbb0cddfdc41"], "status": "REASONED"},
    "ssrf": {"text": "Allowlist relay destinations and enforce worker egress for schemes, ports and resolved addresses; revalidate redirects and never forward inbound credentials.", "components": ["owasp"], "sources": ["owasp:s7eb820e1e53b"], "status": "REASONED"},
    "verify-handshake": {"text": "Cookie handshake positive is 101; missing cookie and disallowed/missing Origin must reject, never 101. Failed controls and unrelated errors are inconclusive.", "components": ["owasp", "websocket"], "sources": ["owasp:sfbb0cddfdc41", "websocket:sbdde15b3166d"], "status": "REASONED", "verify": [1]},
    "verify-sse": {"text": "With a cookie require 200, text/event-stream and the protected event; without it require rejection. A timeout alone proves nothing.", "components": ["browser", "owasp"], "sources": ["browser:scc66a82750c7", "owasp:s10c2347db109"], "status": "REASONED", "verify": [1]},
    "verify-messages": {"text": "Using the real client, compare valid, missing, invalid and expired tokens, pre-auth operations, cross-channel denial and revocation on an open connection.", "components": ["owasp"], "sources": ["owasp:sfbb0cddfdc41", "owasp:s10c2347db109"], "status": "REASONED"},
    "verify-defaults": {"text": "Pair a legitimate login with the deployed component default credentials; a no-credential request does not test defaults.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "verify-webhook": {"text": "Wrong/unsigned signatures must have no effect; valid events must act once and replay must not act twice, even with changed GitHub delivery IDs.", "components": ["github", "stripe"], "sources": ["github:s54f0b41284b0", "github:s31c140d2cfa9", "stripe:s106b78b02797"], "status": "REASONED", "verify": [2]},
    "verify-stale": {"text": "On a synchronized Stripe fixture with 300-second tolerance, a request backdated 600 seconds must fail timestamp validation.", "components": ["stripe-node", "stripe-python"], "sources": ["stripe-node:s6cef5da6ee15", "stripe-python:sa38abcfb0132"], "status": "REASONED", "verify": [2]},
    "verify-secrets": {"text": "Hidden prompts and stdin headers avoid new secret argv/history/environment exposure; Python reads and closes secret pipe fd 3. Process memory remains readable.", "components": ["curl", "python"], "sources": ["curl:s2b2686afaf41", "python:s767fa9623dba"], "status": "REASONED", "verify": [1, 2]},
    "verify-origin": {"text": "Compare allowed and external vantage points using connect-to and correct Host/TLS name; HTTP or TLS responses prove reachability, errors alone do not prove isolation.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [3]}
  }
}
---
# WebSockets, server-sent events, and webhooks: authenticating the non-page endpoints

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Restrict application origins to intended proxies; separately inventory containers, IPv6 and management endpoints. | OWASP guidance unknown | REASONED |
| tls: Use WSS and HTTPS with certificate verification; protect untrusted proxy-to-app hops with authenticated TLS. | WebSocket protocol RFC 6455; OWASP guidance unknown; GitHub webhooks documentation unknown | REASONED |
| credentials: Disable anonymous/default credentials and separate minimally scoped publisher, subscriber, sender and admin identities. | OWASP guidance unknown | REASONED |
| mfa: Keep admin UIs private with IdP or fronting MFA; machine webhook deliveries use signatures. | OWASP guidance unknown; GitHub webhooks documentation unknown | REASONED |
| ws-headers: Browser WebSocket accepts a URL and protocols, with no custom Authorization-header argument. | Browser API and living standards unknown | REASONED |
| ws-origin: Eligible cookies may accompany handshakes; reject missing or non-allowlisted Origin before protected logic to prevent CSWSH. | OWASP guidance unknown; WebSocket protocol RFC 6455 | REASONED |
| ws-token: Authenticate a short-lived first-message token before protected use; rotate it and keep credentials out of URLs and subprotocols. | OWASP guidance unknown; Browser API and living standards unknown | REASONED |
| ws-identity: Origin is forgeable outside browsers; independently authenticate, and do not let a stolen cookie alone obtain the first-message token. | OWASP guidance unknown; WebSocket protocol RFC 6455 | REASONED |
| ws-deadline: Allow no protected operation before authentication and impose a bounded authentication deadline. | OWASP guidance unknown | REASONED |
| authorization: Authorize each channel, tenant and operation, including SSE subscriptions; revalidate and terminate expired or revoked long-lived access. | OWASP guidance unknown | REASONED |
| sse: EventSource uses GET without custom Authorization headers; eligible cookies and cross-origin withCredentials remain browser-policy dependent. | Browser API and living standards unknown | REASONED |
| sse-origin: Authenticate subscriptions and allow only trusted credentialed CORS origins; legitimate same-origin GET may omit Origin. | Browser API and living standards unknown; OWASP guidance unknown | REASONED |
| sse-fetch: Keep SSE GET side-effect free; use fetch with a ReadableStream when header tokens are needed. | Browser API and living standards unknown | REASONED |
| github-signature: Verify raw-body HMAC-SHA256 using X-Hub-Signature-256 and constant-time comparison. | GitHub webhooks documentation unknown | REASONED |
| signature-shape: Reject missing/malformed sha256= plus 64-hex signatures; timingSafeEqual needs equal buffer lengths and exceptions must fail closed. | GitHub webhooks documentation unknown; Node.js crypto documentation unknown | REASONED |
| stripe-signature: Stripe signs timestamp, dot and raw body with the endpoint secret; use official verification libraries. | Stripe webhooks documentation unknown | REASONED |
| stripe-tolerance: stripe-node v18.5.0 and stripe-python v12.5.0 default to 300 seconds; set a positive tolerance and test stale requests because zero handling differs. | stripe-node v18.5.0; stripe-python v12.5.0 | REASONED |
| github-replay: GitHub signs neither a timestamp nor X-GitHub-Delivery; changed delivery IDs retain valid signatures, so ID deduplication cannot establish freshness. | GitHub webhooks documentation unknown | REASONED |
| idempotency: Use atomic durable idempotency from authenticated payload data; body-digest caches only suppress identical bodies during retention and can suppress legitimate repeats. | GitHub webhooks documentation unknown | REASONED |
| stripe-replay: A signed timestamp limits age, not replay inside the window; deduplicate authenticated event IDs after signature and timestamp validation. | Stripe webhooks documentation unknown | REASONED |
| raw-body: Verify exact received bytes before JSON reserialization or handler effects. | GitHub webhooks documentation unknown; Stripe webhooks documentation unknown | REASONED |
| csrf: Scope any webhook CSRF exemption to the one route and method. | Stripe webhooks documentation unknown | REASONED |
| webhook-secret: Require a configured strong GitHub secret, reject unsigned delivery, and use distinct protected, rotated endpoint secrets kept out of URLs and logs. | GitHub webhooks documentation unknown; OWASP guidance unknown | REASONED |
| stripe-secrets: Stripe test/live and Dashboard/CLI-forwarding endpoint secrets differ. | Stripe webhooks documentation unknown | REASONED |
| sender-ip: Provider IP allowlists supplement signatures; trust forwarded client addresses only through a configured proxy chain. | GitHub webhooks documentation unknown | REASONED |
| proxy-limits: Bound HTTP body size, concurrency and timeouts separately; proxy capability summaries refer to local guides and need current vendor confirmation. | Traefik timeout reference v3.5; Caddy and nginx timeout documentation unknown; nginx source release-1.26.3; HAProxy 3.0 | REASONED |
| message-limits: After WebSocket upgrade, enforce per-message authorization and rate limits; connection limits do not bound messages or jobs. | OWASP guidance unknown | REASONED |
| ssrf: Allowlist relay destinations and enforce worker egress for schemes, ports and resolved addresses; revalidate redirects and never forward inbound credentials. | OWASP guidance unknown | REASONED |
| verify-handshake: Cookie handshake positive is 101; missing cookie and disallowed/missing Origin must reject, never 101. Failed controls and unrelated errors are inconclusive. | OWASP guidance unknown; WebSocket protocol RFC 6455 | REASONED |
| verify-sse: With a cookie require 200, text/event-stream and the protected event; without it require rejection. A timeout alone proves nothing. | Browser API and living standards unknown; OWASP guidance unknown | REASONED |
| verify-messages: Using the real client, compare valid, missing, invalid and expired tokens, pre-auth operations, cross-channel denial and revocation on an open connection. | OWASP guidance unknown | REASONED |
| verify-defaults: Pair a legitimate login with the deployed component default credentials; a no-credential request does not test defaults. | OWASP guidance unknown | REASONED |
| verify-webhook: Wrong/unsigned signatures must have no effect; valid events must act once and replay must not act twice, even with changed GitHub delivery IDs. | GitHub webhooks documentation unknown; Stripe webhooks documentation unknown | REASONED |
| verify-stale: On a synchronized Stripe fixture with 300-second tolerance, a request backdated 600 seconds must fail timestamp validation. | stripe-node v18.5.0; stripe-python v12.5.0 | REASONED |
| verify-secrets: Hidden prompts and stdin headers avoid new secret argv/history/environment exposure; Python reads and closes secret pipe fd 3. Process memory remains readable. | curl minimum write-out version 7.75.0; Python os documentation unknown | REASONED |
| verify-origin: Compare allowed and external vantage points using connect-to and correct Host/TLS name; HTTP or TLS responses prove reachability, errors alone do not prove isolation. | curl minimum write-out version 7.75.0 | REASONED |
<!-- version-basis:end -->

Streaming an LLM response commonly rides a WebSocket or an SSE stream, and integrations commonly call back through a webhook. All three are transports, not authentication mechanisms, and each is routinely shipped wide open. [authentication.md](authentication.md) rule 15 already says each transport needs its own check; this guide is that check for these three.

## 1. Restrict listeners and encrypt each transport

Bind application listeners to loopback or a private network restricted to the intended proxy, and inventory container-published ports, IPv6 listeners, and management endpoints separately. Require `wss://` for browser WebSockets and HTTPS for SSE and webhook delivery, and keep webhook certificate verification on; a session cookie or first-message token sent over `ws://` or plain `http://` crosses the network in clear text. If a proxy-to-application hop crosses an untrusted network, protect that hop with authenticated TLS too, since TLS termination at the public proxy does not encrypt it.

Disable anonymous access and any vendor sample or default credentials on every deployed component, and give publishers, subscribers, webhook senders and administrators separate credentials with the smallest supported scopes; never hand an administrative API key to browser clients. Keep any admin UI private and require MFA through its identity provider or an authenticated fronting layer ([authentication.md](authentication.md)); machine webhook deliveries keep using signature authentication rather than interactive MFA.

## 2. WebSocket authentication

The browser `WebSocket()` constructor takes only a URL and an optional `protocols` list; it has no argument for request headers, so a page cannot attach `Authorization: Bearer ...` to the handshake (per MDN's WebSocket API reference). Two verified patterns fill the gap:

- **Cookie plus Origin check.** The handshake is still an HTTP request, so eligible session cookies can ride it automatically, subject to their domain, path, Secure and SameSite attributes and the browser's cookie policy. Where cookies accompany a cross-origin handshake, accepting the connection without validating Origin permits cross-site WebSocket hijacking (CSWSH). OWASP's WebSocket Security Cheat Sheet is explicit: validate the `Origin` header on every handshake against an allowlist, not a denylist, since wildcard or substring matching is error-prone. Reject the upgrade server-side before any application logic runs if `Origin` is missing or not on the list.
- **A token in the first message after the socket opens.** OWASP recommends token-based authentication as the stronger option for exactly this case: pass a short-lived token as a message right after the socket opens, verify it before treating the connection as authenticated, and rotate tokens on long-lived connections. Keep the token out of the URL query string and out of `Sec-WebSocket-Protocol` (the `protocols` argument, meant for subprotocol negotiation, not credentials); both are more likely than a message payload to end up in access logs or proxy logs.

Require authentication independently of Origin validation, because a non-browser client can forge `Origin`; a first-message token protects against cookie theft only if possession of the cookie alone cannot obtain the token. Permit no protected reads, subscriptions, publications or job submissions before authentication, enforce a bounded authentication deadline, authorize each channel, tenant and operation separately (including SSE subscriptions), and revalidate long-lived access, terminating it when the session or token expires or is revoked.

## 3. Server-sent events (SSE)

An `EventSource` performs an HTTP GET (confirmed on MDN) and exposes no option for an `Authorization` header, so a token-in-header scheme does not reach it. Same-origin requests can use eligible session cookies; cross-origin credentials require `withCredentials: true` and remain subject to the browser's cookie policy, and CORS controls browser access to the response. Authenticate and authorize the subscription server-side, and for credentialed cross-origin SSE allow only explicitly trusted origins through CORS. Do not copy the WebSocket missing-Origin rejection unchanged: a legitimate same-origin `EventSource` GET can omit `Origin`. Keep the GET side-effect free. If a client needs a header-based token, use `fetch()` with a `ReadableStream` reader instead of `EventSource`.

## 4. Webhooks: verify the sender, not just the shape of the payload

A webhook has no session and no browser to enforce Origin, so the check is a signature over the raw request body:

- **GitHub** signs deliveries with `X-Hub-Signature-256`: an HMAC-SHA256 hex digest of the payload using your webhook's secret, prefixed `sha256=`. Recompute it yourself and compare with a constant-time function (`crypto.timingSafeEqual` in Node.js, `secure_compare` in Ruby); a plain `==` leaks timing. Reject a missing or malformed signature header before comparing: in Node.js check the `sha256=` prefix and exactly 64 hexadecimal digits, decode the digest, and confirm equal buffer lengths before calling `crypto.timingSafeEqual` (which throws on unequal lengths), treating any validation exception as an authentication failure with no handler side effect.
- **Stripe** signs events with `Stripe-Signature`, formatted `t=<timestamp>,v1=<signature>`. The signed payload is the timestamp concatenated with `.` and the raw body, HMAC-SHA256 with the endpoint's `whsec_...` secret. Verify with an official library where one exists; reject if the timestamp is older than your tolerance (the default tolerance is 300 seconds in stripe-node v18.5.0 and stripe-python v12.5.0; configure a positive tolerance and test stale signed requests, since zero handling differs between SDKs and entry points).

Apply the shared lesson everywhere: use a distinct secret per endpoint (rotating one does not break every integration at once), and reject a request whose signature does not match before your handler touches it. Replay handling itself is provider specific, not a single universal timestamp check. GitHub's signed payload carries no timestamp, and `X-GitHub-Delivery` is not part of what the signature covers: `X-Hub-Signature-256` is computed over the raw body alone (per GitHub's guidance on validating webhook deliveries), so a captured signed request replayed with a different or reused delivery id still produces a valid signature. Deduplicating `X-GitHub-Delivery` catches repeated delivery ids, but an attacker can change that unsigned header, so use atomic, durable idempotency based on authenticated payload data where available. A cache of verified-body digests suppresses identical bodies only for its retention period and can also suppress legitimate identical deliveries; it does not establish freshness. GitHub's signature supplies no general timestamp-based freshness guarantee. Stripe's signed timestamp limits acceptance age, but replay within that window remains possible, so deduplicate authenticated event ids as well. Check signatures and timestamp policy before recording a delivery as processed. Both providers require the exact raw bytes; a framework that parses and re-serializes JSON before your verification code runs will break the check, so verify signatures against the body as received. Where a webhook route must be exempt from a site-wide CSRF filter, scope that exemption to that one route and method only, never to a whole controller or prefix. Configure a strong GitHub webhook secret explicitly; without one, GitHub omits the signature header, so refuse to start a protected receiver without its secret and reject unsigned deliveries. Load secrets from a secret manager or protected runtime environment, keep them out of URLs and logs, and rotate them; Stripe endpoint secrets differ between test and live modes and between Dashboard delivery and CLI forwarding. Allowlisting the provider's published sender IP ranges is a supplement, not a substitute, for signatures (every customer of the provider shares those addresses, so only the signature says who sent the payload), and behind a proxy derive the sender address only through a configured trusted-proxy chain, never from an arbitrary forwarded header.

## 5. Bound the expensive endpoints too

Inference, upload, and job-submission endpoints are usually the ones behind these transports, and an authenticated caller can still exhaust them. Two layers need separate limits. At the proxy in front of the app: a maximum request or body size, a connection concurrency cap per client, and a request timeout matched to realistic response time bound the HTTP connection itself; the [nginx](nginx.md), [Caddy](caddy.md), [HAProxy](haproxy.md) and [Traefik](traefik.md) guides here each have a "Bound the expensive endpoints" section covering what that proxy's guide documents natively: nginx's carries all four controls, Traefik's carries body size, concurrency and rate, HAProxy's carries timeouts and an aggregate connection cap with a header-based body check, and Caddy's carries body size (Caddy has no rate limiting in its standard build). Confirm the current timeout and rate options in each proxy's own documentation before relying on their absence. After a WebSocket upgrade, a single accepted connection can still carry unlimited messages or job submissions, which the connection-level limits above do not touch; OWASP's WebSocket Security Cheat Sheet calls for message-level authorization (checking that each individual message is allowed, not only the handshake) and message-level rate limiting (capping messages per connection per time window) as the separate control that applies once the socket is open. [authentication.md](authentication.md) covers the identity side these limits key off.

## 6. Restrict relay destinations

If a receiver fetches payload URLs or forwards webhooks to user-selected destinations, treat those URLs as an SSRF boundary. Prefer an explicit destination allowlist and enforce egress restrictions from the worker itself, permitting only required schemes and ports and blocking unintended loopback, private, link-local, IPv6-local and cloud-metadata destinations, including addresses reached through DNS aliases or redirects. Disable redirects unless each destination is revalidated, bind validation to the address actually used for the connection so a DNS change cannot bypass it, and never forward inbound credentials to another destination ([egress-metadata.md](egress-metadata.md)).

## Verify

These checks are REASONED from the cited vendor documentation, not demonstrated: no endpoint, WebSocket client, or event fixtures were supplied. Use Bash and curl 7.75.0 or newer. Substitute inside the single quotes and paste each complete block; a value containing an apostrophe needs proper shell escaping. Each secret-bearing block assumes a clean shell. Enter the complete Cookie header value at the hidden prompt, without the `Cookie:` prefix; do not export `AUDIT_COOKIE`. The block clears inherited attributes before reading, keeps the cookie in an unexported subshell variable, sends headers through curl stdin, and unsets the variable on exit. This avoids putting the new input in history, argv or the environment; it does not hide process memory from the same account or root, or erase an earlier export.

Run the first block with `ws` only for endpoints that require a session cookie during the handshake, and with `sse` for cookie-authenticated SSE endpoints. For WebSocket endpoints authenticated solely by a first-message token, use the application-client checks below: a cookie-free `101` is expected and does not by itself establish application authentication. Each negative uses the same URL and deployment as its successful control, and a failed positive control invalidates the comparison. For the handshake, require `101` with a valid cookie and allowed Origin, then a rejection (`401`/`403`, or a login redirect behind an identity-aware proxy, never `101`) without the cookie and for each invalid-Origin case. For SSE, require `200` with `text/event-stream` and the expected protected event with the cookie, then a rejection or login redirect without it. A login page, `404`, unrelated `403`, or server error proves nothing about the intended control, and a timeout alone is inconclusive (an observed `101` or protected event still counts even if curl then times out on the open stream).

```bash
# REASONED: WebSocket authentication and Origin outcomes follow the cited vendor guidance; no endpoint, client, or event fixtures were supplied.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_ENDPOINT' 'REPLACE_WITH_ALLOWED_HTTPS_ORIGIN' 'ws'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'expected endpoint, allowed Origin, and ws or sse'; exit 2; }
  case "$1|$2" in
    *REPLACE_WITH_*|*example.com*|*example.net*|*example.org*) echo 'replace placeholders'; exit 2 ;;
  esac
  case "$1" in https://?*) ;; *) echo 'HTTPS endpoint required'; exit 2 ;; esac
  case "$2" in https://?*) ;; *) echo 'HTTPS Origin required'; exit 2 ;; esac
  case "$3" in ws|sse) ;; *) echo 'choose ws or sse'; exit 2 ;; esac
  { unset -n AUDIT_COOKIE && unset -v AUDIT_COOKIE; } 2>/dev/null ||
    { echo 'cannot clear AUDIT_COOKIE in this shell'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell'; exit 2; }
  trap 'unset -v AUDIT_COOKIE' EXIT
  printf 'Cookie header value (input hidden): '
  IFS= read -r -s AUDIT_COOKIE || { printf '\n'; echo 'no secret read'; exit 2; }
  printf '\n'
  case "$AUDIT_COOKIE" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty secret, placeholder or control character'; exit 2 ;;
  esac
  probe() {
    if curl -q -g -sS -i -N --http1.1 --noproxy '*' \
      --connect-timeout 5 --max-time 10 \
      -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$@"; then
      :
    else
      printf 'curl exit=%s; inspect the response; timeout is not a security pass\n' "$?"
    fi
  }
  handshake() {
    probe -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
      -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' \
      -H 'Sec-WebSocket-Version: 13' "$@"
  }
  if [ "$3" = ws ]; then
    echo 'POSITIVE: valid cookie and allowed Origin'
    printf 'Cookie: %s\n' "$AUDIT_COOKIE" | handshake -H @- -H "Origin: $2" "$1"
    echo 'NEGATIVE: same endpoint and Origin, no cookie'
    handshake -H "Origin: $2" "$1"
    echo 'NEGATIVE: same endpoint and cookie, disallowed Origin'
    printf 'Cookie: %s\n' "$AUDIT_COOKIE" | handshake -H @- -H 'Origin: https://untrusted.example.com' "$1"
    echo 'NEGATIVE: same endpoint and cookie, missing Origin'
    printf 'Cookie: %s\n' "$AUDIT_COOKIE" | handshake -H @- "$1"
  else
    echo 'POSITIVE: valid cookie on the SSE endpoint'
    printf 'Cookie: %s\n' "$AUDIT_COOKIE" | probe -H @- "$1"
    echo 'NEGATIVE: same SSE endpoint, no cookie'
    probe "$1"
  fi
  echo 'Observations only: evaluate the paired results and application effects.'
)
```

First-message-token and default-credential authentication need the application's real WebSocket client and message schema, which were not supplied; the expected outcomes are REASONED from the cited authentication guidance. Against the same endpoint, first demonstrate a valid token and an authorized protected operation, then repeat with no token, an invalid token, an expired token, and a protected operation attempted before authentication; require explicit rejection or an observed authentication-deadline close with no protected data or side effect (silence alone is inconclusive), test channel authorization by first demonstrating the operation on the target channel with an authorized user's token, then repeating the same operation on the same channel and endpoint with a valid token belonging to an unauthorized user, requiring authorization rejection with no protected data or side effect, and verify revocation on an already-open connection. For each installed component with documented default credentials, pair a successful legitimate login with the same request using the defaults, which must fail; do not infer this from a no-credential request, and do not invent a universal default username or password.

For the webhook route, use an isolated test endpoint and a fresh, valid JSON event fixture that produces an observable effect. Enter its endpoint secret at the hidden prompt, and for GitHub export only the fixture's non-secret event type as `AUDIT_GITHUB_EVENT`; these are probe inputs, not vendor configuration. This block assumes a clean shell. It reads `AUDIT_WEBHOOK_SECRET` into an unexported subshell variable and unsets it on exit; Python reads the secret bytes from a pipe on file descriptor 3 and closes that descriptor before starting curl. Neither the secret nor the signed headers enter argv or the environment. The secret remains readable in process memory by the same account and root, and a previously exported value is not erased. The wrong-signature and unsigned requests must be rejected by signature validation with no effect, the correctly signed request must reach the handler and produce the effect, and its repetition must produce no second effect (a success acknowledgement for an already-processed event is fine). For this Stripe probe, confirm that the isolated receiver uses a 300-second tolerance and that the sender and receiver clocks are synchronized; the harness backdates the stale request by 600 seconds, so that request must fail timestamp validation. Confirm the rejecting component in the application logs; transport errors and timeouts are inconclusive. These endpoint outcomes are reasoned, not demonstrated here.

REASONED: following block; signature, replay and timestamp expectations follow the cited GitHub and Stripe sources; no endpoint or event fixtures were supplied.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_WEBHOOK_URL' 'REPLACE_WITH_RAW_BODY_FILE' 'github'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'expected URL, raw-body file, and github or stripe'; exit 2; }
  case "$1|$2" in
    *REPLACE_WITH_*|*example.com*|*example.net*|*example.org*) echo 'replace placeholders'; exit 2 ;;
  esac
  case "$1" in https://?*) ;; *) echo 'HTTPS required'; exit 2 ;; esac
  if [ -f "$2" ] && [ -r "$2" ]; then :; else echo 'readable raw-body file required'; exit 2; fi
  case "$3" in github|stripe) ;; *) echo 'choose github or stripe'; exit 2 ;; esac
  { unset -n AUDIT_WEBHOOK_SECRET && unset -v AUDIT_WEBHOOK_SECRET; } 2>/dev/null ||
    { echo 'cannot clear AUDIT_WEBHOOK_SECRET in this shell'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell'; exit 2; }
  trap 'unset -v AUDIT_WEBHOOK_SECRET' EXIT
  printf 'Webhook endpoint secret (input hidden): '
  IFS= read -r -s AUDIT_WEBHOOK_SECRET || { printf '\n'; echo 'no secret read'; exit 2; }
  printf '\n'
  case "$AUDIT_WEBHOOK_SECRET" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty secret, placeholder or control character'; exit 2 ;;
  esac
  python3 - "$1" "$2" "$3" 3< <(printf '%s' "$AUDIT_WEBHOOK_SECRET") <<'PY'
import hashlib, hmac, os, pathlib, subprocess, sys, time, uuid

body = pathlib.Path(sys.argv[2]).read_bytes()
with os.fdopen(3, "rb") as secret_input:
    secret = secret_input.read()
if not secret:
    print("No webhook secret received; skipped")
    raise SystemExit(2)
provider = sys.argv[3]
if provider == "github" and (not os.environ.get("AUDIT_GITHUB_EVENT") or
        any(c in os.environ["AUDIT_GITHUB_EVENT"] for c in "\r\n")):
    print("Export the fixture event type as AUDIT_GITHUB_EVENT; skipped")
    raise SystemExit(2)

def request(mode):
    timestamp = int(time.time()) - (600 if mode == "stale" else 0)
    signed = body if provider == "github" else str(timestamp).encode() + b"." + body
    digest = hmac.new(secret, signed, hashlib.sha256).hexdigest()
    if mode == "wrong":
        digest = ("0" if digest[0] != "0" else "1") + digest[1:]
    header = ("X-Hub-Signature-256: sha256=" + digest if provider == "github"
              else "Stripe-Signature: t=" + str(timestamp) + ",v1=" + digest)
    headers = b"" if mode == "unsigned" else (header + "\n").encode()
    if provider == "github":
        headers += ("X-GitHub-Event: " + os.environ["AUDIT_GITHUB_EVENT"] +
                    "\nX-GitHub-Delivery: " + str(uuid.uuid4()) + "\n").encode()
    print(mode.upper(), flush=True)
    result = subprocess.run(
        ("curl", "-q", "-g", "-sS", "-i", "--noproxy", "*",
         "--connect-timeout", "5", "--max-time", "10",
         "-H", "Content-Type: application/json", "-H", "@-",
         "--data-binary", "@" + sys.argv[2],
         "-w", "\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n",
         sys.argv[1]), input=headers, check=False)
    if result.returncode:
        raise SystemExit("Transport failure: inconclusive")

for mode in (("wrong", "unsigned", "stale", "valid", "valid") if provider == "stripe"
             else ("wrong", "unsigned", "valid", "valid")):
    request(mode)
PY
)
```

Finally, authentication rejection is not evidence of network isolation, so test direct reachability of each listener. Inventory every application and management listener, including published container ports and IPv6, and for each HTTP listener set the connect-to mapping to `URL_HOST:URL_PORT:ACTUAL_ORIGIN_ADDRESS:ACTUAL_LISTENER_PORT` (bracket IPv6 addresses where curl requires them) while the URL keeps the intended Host and TLS server name. Run it first from an allowed location to establish that the origin answers, then from an external one against the same origin: any HTTP response (including `401`, `403` or `404`), or a TLS handshake or certificate error, proves external reachability, while a timeout, DNS error, or local socket error does not prove isolation and must be corroborated with the listener and network-policy configuration. Never use `-k`. This comparison stays reasoned until both vantage points and the real origin inventory are available.

REASONED: following block; origin reachability follows the cited curl documentation; both vantage points and the real listener inventory are unavailable.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ORIGIN_URL' 'REPLACE_WITH_CONNECT_TO_MAPPING'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'expected URL and connect-to mapping'; exit 2; }
  case "$1|$2" in
    *REPLACE_WITH_*|*example.com*|*example.net*|*example.org*) echo 'replace placeholders'; exit 2 ;;
  esac
  [ -n "$2" ] || { echo 'connect-to mapping required'; exit 2; }
  case "$1" in http://?*|https://?*) ;; *) echo 'HTTP or HTTPS URL required'; exit 2 ;; esac
  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
    --connect-to "$2" \
    -w 'peer=%{remote_ip} http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

## Common mistakes

- Treating the page login as coverage for the WebSocket or SSE endpoint it opens; each needs its own check.
- Comparing webhook signatures with `==` instead of a constant-time comparison.
- Letting a framework's body parser touch the request before webhook signature verification runs, which breaks the raw-body check.

## Sources (checked September 2026)

Scope and revisions: browser behavior follows RFC 6455 and the HTML and Fetch living standards retrieved on 2026-09-18; SDK-specific tolerance behavior was checked against stripe-node v18.5.0 and stripe-python v12.5.0; the Verify diagnostics require curl 7.75.0 or newer; Traefik timeout syntax was checked against v3.5. Other linked live documentation was retrieved on 2026-09-18 without an available immutable revision, and these source checks do not demonstrate deployment behavior.

- MDN: WebSocket API, `WebSocket()` constructor (no header support, `protocols` argument): https://developer.mozilla.org/en-US/docs/Web/API/WebSocket/WebSocket
- MDN: Using server-sent events (`EventSource`, plain GET, `withCredentials`): https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
- OWASP WebSocket Security Cheat Sheet (Origin allowlisting, token-based authentication): https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html
- GitHub: Validating webhook deliveries (`X-Hub-Signature-256`, constant-time comparison): https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- Stripe: Verify webhook signatures (`Stripe-Signature`, timestamp tolerance, official libraries): https://docs.stripe.com/webhooks#verify-official-libraries
- RFC 6455, The WebSocket Protocol (Origin semantics, wire security): https://www.rfc-editor.org/rfc/rfc6455.html
- HTML standard, server-sent events (`EventSource` GET semantics): https://html.spec.whatwg.org/multipage/server-sent-events.html
- Fetch standard, request Origin-header algorithm: https://fetch.spec.whatwg.org/#append-a-request-origin-header
- Node.js crypto (`crypto.timingSafeEqual` throws on unequal lengths): https://nodejs.org/docs/latest-v22.x/api/crypto.html#cryptotimingsafeequala-b
- stripe-node v18.5.0 signature verification (`constructEvent`, default 300s tolerance): https://raw.githubusercontent.com/stripe/stripe-node/v18.5.0/src/Webhooks.ts
- stripe-python v12.5.0 signature verification: https://raw.githubusercontent.com/stripe/stripe-python/v12.5.0/stripe/_webhook.py
- GitHub: webhook best practices (require a secret; unsigned deliveries): https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
- GitHub: webhook delivery headers (`X-GitHub-Event`, `X-GitHub-Delivery`): https://docs.github.com/en/webhooks/webhook-events-and-payloads
- Stripe: signing-secret troubleshooting (test versus live modes, CLI forwarding): https://docs.stripe.com/webhooks/signature
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Multifactor Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Traefik v3.5 entryPoint timeouts: https://doc.traefik.io/traefik/v3.5/reference/install-configuration/entrypoints/
- Caddy server timeouts: https://caddyserver.com/docs/caddyfile/options#timeouts
- nginx `proxy_read_timeout`: https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout
- curl manual (`--connect-to`, `--noproxy`, write-out variables require 7.75.0+): https://curl.se/docs/manpage.html
- Python `os.fdopen`, for reading and closing the secret pipe: https://docs.python.org/3/library/os.html#os.fdopen
- nginx release-1.26.3 body-size, connection-limit and request-rate directives (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/ngx_http_core_module.c#L348-L353, https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_limit_conn_module.c#L100-L105, https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_limit_req_module.c#L113-L118
- Traefik v3.5 buffering, in-flight request limits and rate limits (checked October 2026): https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/buffering/, https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/inflightreq/, https://doc.traefik.io/traefik/v3.5/reference/routing-configuration/http/middlewares/ratelimit/
- HAProxy 3.0 configuration: timeouts, aggregate maxconn and req.body_size advertised-length semantics (checked October 2026): https://docs.haproxy.org/3.0/configuration.html#7.3.6-req.body_size
