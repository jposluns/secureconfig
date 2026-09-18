# WebSockets, server-sent events, and webhooks: authenticating the non-page endpoints

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

These checks are reasoned, not demonstrated: no endpoint, WebSocket client, or event fixtures were supplied, so backlog row 2.35 tracks demonstrating them. Use Bash and curl 7.75.0 or newer. Substitute inside the single quotes and paste each complete block; a value containing an apostrophe needs proper shell escaping. Supply `AUDIT_COOKIE` through a protected environment as the complete Cookie header value, without the `Cookie:` prefix.

Run the first block with `ws` only for endpoints that require a session cookie during the handshake, and with `sse` for cookie-authenticated SSE endpoints. For WebSocket endpoints authenticated solely by a first-message token, use the application-client checks below: a cookie-free `101` is expected and does not by itself establish application authentication. Each negative uses the same URL and deployment as its successful control, and a failed positive control invalidates the comparison. For the handshake, require `101` with a valid cookie and allowed Origin, then a rejection (`401`/`403`, or a login redirect behind an identity-aware proxy, never `101`) without the cookie and for each invalid-Origin case. For SSE, require `200` with `text/event-stream` and the expected protected event with the cookie, then a rejection or login redirect without it. A login page, `404`, unrelated `403`, or server error proves nothing about the intended control, and a timeout alone is inconclusive (an observed `101` or protected event still counts even if curl then times out on the open stream).

```bash
(
  set +x
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
  case "${AUDIT_COOKIE-}" in
    ''|*REPLACE_WITH_*|*$'\r'*|*$'\n'*) echo 'load a valid Cookie header value into AUDIT_COOKIE'; exit 2 ;;
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

First-message-token and default-credential authentication need the application's real WebSocket client and message schema, so they stay reasoned until fixtures and an endpoint are available. Against the same endpoint, first demonstrate a valid token and an authorized protected operation, then repeat with no token, an invalid token, an expired token, and a protected operation attempted before authentication; require explicit rejection or an observed authentication-deadline close with no protected data or side effect (silence alone is inconclusive), test channel authorization by first demonstrating the operation on the target channel with an authorized user's token, then repeating the same operation on the same channel and endpoint with a valid token belonging to an unauthorized user, requiring authorization rejection with no protected data or side effect, and verify revocation on an already-open connection. For each installed component with documented default credentials, pair a successful legitimate login with the same request using the defaults, which must fail; do not infer this from a no-credential request, and do not invent a universal default username or password.

For the webhook route, use an isolated test endpoint and a fresh, valid JSON event fixture that produces an observable effect. Export its endpoint secret as `AUDIT_WEBHOOK_SECRET`, and for GitHub also export the fixture's event type as `AUDIT_GITHUB_EVENT`; these are probe inputs, not vendor configuration. The wrong-signature and unsigned requests must be rejected by signature validation with no effect, the correctly signed request must reach the handler and produce the effect, and its repetition must produce no second effect (a success acknowledgement for an already-processed event is fine). For this Stripe probe, confirm that the isolated receiver uses a 300-second tolerance and that the sender and receiver clocks are synchronized; the harness backdates the stale request by 600 seconds, so that request must fail timestamp validation. Confirm the rejecting component in the application logs; transport errors and timeouts are inconclusive. These endpoint outcomes are reasoned, not demonstrated here.

```bash
(
  set +x
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
  case "${AUDIT_WEBHOOK_SECRET-}" in
    ''|*REPLACE_WITH_*) echo 'export the test endpoint secret as AUDIT_WEBHOOK_SECRET'; exit 2 ;;
  esac
  python3 - "$1" "$2" "$3" <<'PY'
import hashlib, hmac, os, pathlib, subprocess, sys, time, uuid

body = pathlib.Path(sys.argv[2]).read_bytes()
if not os.environ.get("AUDIT_WEBHOOK_SECRET"):
    print("Export AUDIT_WEBHOOK_SECRET before running; skipped")
    raise SystemExit(2)
secret = os.environ["AUDIT_WEBHOOK_SECRET"].encode()
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
        ["curl", "-q", "-g", "-sS", "-i", "--noproxy", "*",
         "--connect-timeout", "5", "--max-time", "10",
         "-H", "Content-Type: application/json", "-H", "@-",
         "--data-binary", "@" + sys.argv[2],
         "-w", "\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n",
         sys.argv[1]], input=headers, check=False)
    if result.returncode:
        raise SystemExit("Transport failure: inconclusive")

for mode in (("wrong", "unsigned", "stale", "valid", "valid") if provider == "stripe"
             else ("wrong", "unsigned", "valid", "valid")):
    request(mode)
PY
)
```

Finally, authentication rejection is not evidence of network isolation, so test direct reachability of each listener. Inventory every application and management listener, including published container ports and IPv6, and for each HTTP listener set the connect-to mapping to `URL_HOST:URL_PORT:ACTUAL_ORIGIN_ADDRESS:ACTUAL_LISTENER_PORT` (bracket IPv6 addresses where curl requires them) while the URL keeps the intended Host and TLS server name. Run it first from an allowed location to establish that the origin answers, then from an external one against the same origin: any HTTP response (including `401`, `403` or `404`), or a TLS handshake or certificate error, proves external reachability, while a timeout, DNS error, or local socket error does not prove isolation and must be corroborated with the listener and network-policy configuration. Never use `-k`. This comparison stays reasoned until both vantage points and the real origin inventory are available.

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
