---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "dc4314bb3d2cc1f37964cd7c5ebc24f09c20f21cd4cbc57fa6a294e286807c84",
  "components": {
    "mdn": {
      "name": "MDN HTTP documentation",
      "basis": "unknown",
      "sources": {
        "s40155272e6bf": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers",
        "s9166d803cf3a": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control",
        "s7f290c45ad37": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data",
        "s46957d9dc1d5": "https://developer.mozilla.org/en-US/docs/Glossary/bfcache"
      }
    },
    "scanner": {
      "name": "Security Headers scanner",
      "basis": "unknown",
      "sources": {
        "s7a94d0fcb6ad": "https://securityheaders.com/"
      }
    }
  },
  "claims": {
    "placement": {"text": "Set response headers at a proxy, in application middleware or in a static host's _headers file; stack-specific Sources entries and versions are not recorded.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED"},
    "hsts": {"text": "Use HSTS max-age=31536000 with includeSubDomains only after HTTPS works across the domain; every subdomain is committed to HTTPS and max-age=0 disables HSTS.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "hsts-preload": {"text": "Omit preload unless its commitment is understood; removal is slow, takes weeks and depends on browser list updates.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED"},
    "csp": {"text": "Start CSP at default-src 'self', tailor sources to the app and prefer script nonces or hashes over unsafe-inline; Verify requires an enforcing policy.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "csp-report-only": {"text": "Roll out Content-Security-Policy-Report-Only first on existing apps to find breakage; it enforces nothing and is not a substitute for enforcing CSP.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "nosniff": {"text": "Send X-Content-Type-Options: nosniff and verify that value on the final response.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "referrer": {"text": "Send Referrer-Policy: strict-origin-when-cross-origin and verify that final-response value.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "permissions": {"text": "Permissions-Policy disables camera, microphone and geolocation with empty allowlists; verify all three restrictions.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "framing": {"text": "X-Frame-Options: DENY or enforcing CSP frame-ancestors 'none' denies framing; supported frame-ancestors supersedes X-Frame-Options, and default-src does not cover it. frame-ancestors * overrides DENY.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "all-responses": {"text": "Send headers on every response, including errors; nginx add_header inheritance is mentioned through a local guide without a direct vendor Sources entry.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED"},
    "shared-cache": {"text": "Use Cache-Control: private for authenticated responses or no-store for sensitive ones; cache only public content unless authenticated caching is explicitly configured.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a"], "status": "REASONED"},
    "cache-key": {"text": "A URL-only shared cache can leak one user's response to another; explicitly vary authenticated cache entries on the cookie or authorization header.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a", "mdn:s40155272e6bf"], "status": "REASONED"},
    "browser-cache": {"text": "private still permits browser storage; no-store forbids private and shared storage and belongs on authenticated responses and responses setting session cookies.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a"], "status": "REASONED"},
    "history-cache": {"text": "no-cache does not prevent a Back navigation from restoring a back/forward-cache snapshot without revalidation.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a", "mdn:s46957d9dc1d5"], "status": "REASONED"},
    "logout-cache": {"text": "Send Clear-Site-Data on logout confirmation; cache clears browser cache and may clear back/forward cache depending on the browser.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37", "mdn:s46957d9dc1d5"], "status": "REASONED"},
    "logout-cookies": {"text": "Clear-Site-Data cookies clears cookies across the registered domain and all subdomains, plus HTTP authentication credentials; invalidate the server session separately.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "logout-storage": {"text": "Clear-Site-Data storage removes origin local/session storage, IndexedDB and service-worker registrations; understand effects on companion applications before clearing.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "logout-header": {"text": "The cited MDN logout example includes cache, cookies, storage, executionContexts, prefetchCache and prerenderCache.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "verify-fetch": {"text": "Fetch the final page with redirects restricted to HTTPS, bypass client proxies, discard the body and inspect the last response's headers and final status/URL; curl-specific Sources and version are absent.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "verify-values": {"text": "Judge header values on the final response, not presence on an earlier hop; missing final headers are findings and a failed fetch is inconclusive.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "verify-scanner": {"text": "Use the external Security Headers scanner for a second opinion; the guide states that it fetches with GET.", "components": ["scanner"], "sources": ["scanner:s7a94d0fcb6ad"], "status": "REASONED"},
    "verify-csp": {"text": "Unexpected console violations must be absent in normal use, but this alone is insufficient; confirm a deliberately disallowed resource is blocked while an allowed one loads.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED"},
    "verify-cache": {"text": "Warm an authenticated URL in the shared cache, then request it as user A, user B and anonymously; each response must belong only to its caller.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a"], "status": "REASONED"},
    "verify-logout": {"text": "After logout, Back must not restore authenticated content; verify a request to the login screen and inspect no-store and Clear-Site-Data separately in every supported browser.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a", "mdn:s7f290c45ad37", "mdn:s46957d9dc1d5"], "status": "REASONED"}
  }
}
---
# Security headers for your application

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| placement: Set response headers at a proxy, in application middleware or in a static host's _headers file; stack-specific Sources entries and versions are not recorded. | MDN HTTP documentation unknown | REASONED |
| hsts: Use HSTS max-age=31536000 with includeSubDomains only after HTTPS works across the domain; every subdomain is committed to HTTPS and max-age=0 disables HSTS. | MDN HTTP documentation unknown | REASONED |
| hsts-preload: Omit preload unless its commitment is understood; removal is slow, takes weeks and depends on browser list updates. | MDN HTTP documentation unknown | REASONED |
| csp: Start CSP at default-src 'self', tailor sources to the app and prefer script nonces or hashes over unsafe-inline; Verify requires an enforcing policy. | MDN HTTP documentation unknown | REASONED |
| csp-report-only: Roll out Content-Security-Policy-Report-Only first on existing apps to find breakage; it enforces nothing and is not a substitute for enforcing CSP. | MDN HTTP documentation unknown | REASONED |
| nosniff: Send X-Content-Type-Options: nosniff and verify that value on the final response. | MDN HTTP documentation unknown | REASONED |
| referrer: Send Referrer-Policy: strict-origin-when-cross-origin and verify that final-response value. | MDN HTTP documentation unknown | REASONED |
| permissions: Permissions-Policy disables camera, microphone and geolocation with empty allowlists; verify all three restrictions. | MDN HTTP documentation unknown | REASONED |
| framing: X-Frame-Options: DENY or enforcing CSP frame-ancestors 'none' denies framing; supported frame-ancestors supersedes X-Frame-Options, and default-src does not cover it. frame-ancestors * overrides DENY. | MDN HTTP documentation unknown | REASONED |
| all-responses: Send headers on every response, including errors; nginx add_header inheritance is mentioned through a local guide without a direct vendor Sources entry. | MDN HTTP documentation unknown | REASONED |
| shared-cache: Use Cache-Control: private for authenticated responses or no-store for sensitive ones; cache only public content unless authenticated caching is explicitly configured. | MDN HTTP documentation unknown | REASONED |
| cache-key: A URL-only shared cache can leak one user's response to another; explicitly vary authenticated cache entries on the cookie or authorization header. | MDN HTTP documentation unknown | REASONED |
| browser-cache: private still permits browser storage; no-store forbids private and shared storage and belongs on authenticated responses and responses setting session cookies. | MDN HTTP documentation unknown | REASONED |
| history-cache: no-cache does not prevent a Back navigation from restoring a back/forward-cache snapshot without revalidation. | MDN HTTP documentation unknown | REASONED |
| logout-cache: Send Clear-Site-Data on logout confirmation; cache clears browser cache and may clear back/forward cache depending on the browser. | MDN HTTP documentation unknown | REASONED |
| logout-cookies: Clear-Site-Data cookies clears cookies across the registered domain and all subdomains, plus HTTP authentication credentials; invalidate the server session separately. | MDN HTTP documentation unknown | REASONED |
| logout-storage: Clear-Site-Data storage removes origin local/session storage, IndexedDB and service-worker registrations; understand effects on companion applications before clearing. | MDN HTTP documentation unknown | REASONED |
| logout-header: The cited MDN logout example includes cache, cookies, storage, executionContexts, prefetchCache and prerenderCache. | MDN HTTP documentation unknown | REASONED |
| verify-fetch: Fetch the final page with redirects restricted to HTTPS, bypass client proxies, discard the body and inspect the last response's headers and final status/URL; curl-specific Sources and version are absent. | MDN HTTP documentation unknown | REASONED |
| verify-values: Judge header values on the final response, not presence on an earlier hop; missing final headers are findings and a failed fetch is inconclusive. | MDN HTTP documentation unknown | REASONED |
| verify-scanner: Use the external Security Headers scanner for a second opinion; the guide states that it fetches with GET. | Security Headers scanner unknown | REASONED |
| verify-csp: Unexpected console violations must be absent in normal use, but this alone is insufficient; confirm a deliberately disallowed resource is blocked while an allowed one loads. | MDN HTTP documentation unknown | REASONED |
| verify-cache: Warm an authenticated URL in the shared cache, then request it as user A, user B and anonymously; each response must belong only to its caller. | MDN HTTP documentation unknown | REASONED |
| verify-logout: After logout, Back must not restore authenticated content; verify a request to the login screen and inspect no-store and Clear-Site-Data separately in every supported browser. | MDN HTTP documentation unknown | REASONED |
<!-- version-basis:end -->

TLS protects the transport; these response headers protect the page. Set them at the proxy (`add_header` in [nginx.md](nginx.md), `Header` in [apache.md](apache.md), `header` in Caddy), in app middleware (helmet for Express per [nodejs.md](nodejs.md), Django's security settings per [python.md](python.md)), or in a `_headers` file on static hosts.

## The set worth shipping

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
X-Frame-Options: DENY
```

Notes that keep these correct rather than decorative:

- **HSTS** only after HTTPS provably works everywhere on the domain; `includeSubDomains` commits every subdomain to HTTPS. Leave the `preload` token off unless you have read what preload-list inclusion means: removal is possible but slow (weeks, and browser-dependent as each browser ships an updated list), so treat inclusion as a long-lived commitment.
- **CSP** is the one that needs tailoring. Start from `default-src 'self'`, add the sources your app actually uses, and prefer nonces or hashes over `'unsafe-inline'` for scripts. Roll out with `Content-Security-Policy-Report-Only` first on an existing app so you see what would break before enforcing.
- **frame-ancestors** in CSP supersedes `X-Frame-Options` in browsers that support it. The modern equivalent of `X-Frame-Options: DENY` is `frame-ancestors 'none'` in the CSP; add it explicitly, because `default-src` does not cover framing. Sending both `X-Frame-Options` and `frame-ancestors` keeps older scanners content.
- Headers belong on every response, including error pages; setting them only on `200 /` is a common proxy misconfiguration (nginx `add_header` inheritance per [nginx.md](nginx.md)).

## Do not cache authenticated responses in a shared cache

A CDN or shared proxy that keys its cache on the URL alone can serve one user's authenticated response to another. Set `Cache-Control: private` on authenticated responses, or `no-store` on the most sensitive ones, and mark cacheable only what is truly public. If a shared cache must hold authenticated content, configure it explicitly to vary on the cookie or the authorization header rather than relying on its default URL-only key.

## Keep authenticated pages out of the browser's own cache

`private` stops a shared cache from holding a response, but it still lets the user's own browser store it: MDN defines `private` as a response the browser's local cache may keep. So the Back button can redisplay an authenticated page after logout, and a chat transcript can sit in the history of a shared machine. Set `Cache-Control: no-store` on any response that carries authenticated content or sets a session cookie; MDN defines `no-store` as "any caches of any kind (private or shared) should not store this response", which covers the browser too.

On logout, clear what the browser already holds. `Cache-Control: no-cache` does not cover this, because a history navigation such as the Back button can restore a back/forward-cache snapshot without revalidating. Send the `Clear-Site-Data` header on the logout-confirmation response instead: its `cache` directive clears the browser cache and, depending on the browser, the back/forward cache as well, and `cookies` clears the client-side session cookie (invalidate the server-side session separately, as part of logout). MDN's own logout example is `Clear-Site-Data: "cache", "cookies", "storage", "executionContexts", "prefetchCache", "prerenderCache"`. Know the scope before sending the full set: `"cookies"` clears cookies across the entire registered domain (all subdomains) and also clears HTTP authentication credentials, and `"storage"` removes origin local/session storage, IndexedDB, and service-worker registrations, so a shared parent domain or a companion app on a subdomain is affected too.

## Verify

REASONED: final-response header inspection follows the cited MDN header documentation; curl command-specific sources are not recorded. No deployment URL was supplied for live checks, and this guide records no run; the following block states the expected values and treats failed fetches as inconclusive.

```bash
# Fetch the FINAL page and read its response headers by eye. -L follows redirects (--proto-redir
# '=https' blocks an https-to-http downgrade) so you inspect the page a browser lands on, not a 302;
# --noproxy so no client proxy rewrites the headers; the body is discarded. -D - prints EVERY
# response's headers (a 103 Early Hints and each redirect hop, then the final one), and -w prints where
# you ended up, so read the block under the LAST "HTTP/.. <status>" line:
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' -D - -o /dev/null -w 'final: %{http_code} %{url_effective}\n' https://example.com/
# In that final response check VALUES, not just presence: Strict-Transport-Security with a large,
# non-zero max-age (max-age=0 disables HSTS); an ENFORCING Content-Security-Policy, not only
# Content-Security-Policy-Report-Only (which enforces nothing); X-Content-Type-Options nosniff;
# Referrer-Policy strict-origin-when-cross-origin; Permissions-Policy denying camera, microphone, and
# geolocation; and an effective deny-framing policy: CSP frame-ancestors 'none', or X-Frame-Options
# DENY with NO enforcing frame-ancestors overriding it (an enforcing frame-ancestors always wins over
# X-Frame-Options, so frame-ancestors * with X-Frame-Options: DENY still allows framing). A header
# missing from the final response, or present only on an earlier hop, is a finding; a failed fetch is
# inconclusive.
```

Then scan with https://securityheaders.com/ from outside for a second opinion (it fetches with GET). No UNEXPECTED CSP console violations during normal application use is necessary but not sufficient: a permissive CSP produces none, and a correct policy still logs a violation when it blocks something (the negative test below, an attack, or an unwanted load). Confirm the policy actually blocks by loading a page with a deliberately disallowed resource (an inline script the policy forbids, or an off-origin image) and checking it is refused while an allowed resource still loads.

For an authenticated route behind a shared cache, request the same URL as user A, then as user B, then anonymously, after warming the cache; each response must reflect only its own caller, never the one before it.

In a real browser, log in, open an authenticated page, then log out and press the Back button: the authenticated page must not reappear from history. The browser should re-request it and land on the login screen. That confirms the logout outcome, not which header produced it, so also inspect the authenticated and logout responses for the intended `no-store` and `Clear-Site-Data` headers. Because the back/forward-cache clearing is browser-dependent, run the check in each browser you support.

## Sources (checked September 2026)

- MDN HTTP headers reference (Strict-Transport-Security, Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-Frame-Options): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers
- MDN Cache-Control (`no-store` forbids any cache including the browser; `private` still permits the browser's local cache): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
- MDN Clear-Site-Data (the `cache` directive clears the browser cache and, depending on the browser, the back/forward cache; the logout example): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data
- MDN back/forward cache (a history navigation restores a snapshot without revalidating): https://developer.mozilla.org/en-US/docs/Glossary/bfcache
- Security header scanner: https://securityheaders.com/
