# Security headers for your application

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

- **HSTS** only after HTTPS provably works everywhere on the domain; `includeSubDomains` commits every subdomain to HTTPS. Leave the `preload` token off unless you have read what preload-list inclusion means; it is effectively irreversible.
- **CSP** is the one that needs tailoring. Start from `default-src 'self'`, add the sources your app actually uses, and prefer nonces or hashes over `'unsafe-inline'` for scripts. Roll out with `Content-Security-Policy-Report-Only` first on an existing app so you see what would break before enforcing.
- **frame-ancestors** in CSP supersedes `X-Frame-Options`; sending both keeps older scanners content and costs nothing.
- Headers belong on every response, including error pages; setting them only on `200 /` is a common proxy misconfiguration (nginx `add_header` inheritance per [nginx.md](nginx.md)).

## Do not cache authenticated responses in a shared cache

A CDN or shared proxy that keys its cache on the URL alone can serve one user's authenticated response to another. Set `Cache-Control: private` on authenticated responses, or `no-store` on the most sensitive ones, and mark cacheable only what is truly public. If a shared cache must hold authenticated content, configure it explicitly to vary on the cookie or the authorization header rather than relying on its default URL-only key.

## Keep authenticated pages out of the browser's own cache

`private` stops a shared cache from holding a response, but it still lets the user's own browser store it: MDN defines `private` as a response the browser's local cache may keep. So the Back button can redisplay an authenticated page after logout, and a chat transcript can sit in the history of a shared machine. Set `Cache-Control: no-store` on any response that carries authenticated content or sets a session cookie; MDN defines `no-store` as "any caches of any kind (private or shared) should not store this response", which covers the browser too.

On logout, clear what the browser already holds. `Cache-Control: no-cache` does not cover this, because a history navigation such as the Back button restores a back/forward-cache snapshot without revalidating. Send the `Clear-Site-Data` header on the logout-confirmation response instead: its `cache` directive clears the browser cache including the back/forward cache, and `cookies` drops the session. MDN's own logout example is `Clear-Site-Data: "cache", "cookies", "storage", "executionContexts", "prefetchCache", "prerenderCache"`.

## Verify

```bash
curl -q -sI https://example.com/ | grep -iE 'strict-transport|content-security|x-content-type|referrer-policy|permissions-policy|x-frame'
```

Then scan with https://securityheaders.com/ from outside. A CSP that enforces without console errors on every page of the app is the finish line.

For an authenticated route behind a shared cache, request the same URL as user A, then as user B, then anonymously, after warming the cache; each response must reflect only its own caller, never the one before it.

In a real browser, log in, open an authenticated page, then log out and press the Back button: the authenticated page must not reappear from history. The browser should re-request it and land on the login screen, which is the observable proof that `no-store` and the logout `Clear-Site-Data` took effect.

## Sources (checked September 2026)

- MDN HTTP headers reference: https://developer.mozilla.org/en-US/docs/Web/HTTP
- MDN Cache-Control (`no-store` forbids any cache including the browser; `private` still permits the browser's local cache): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
- MDN Clear-Site-Data (the `cache` directive clears the browser and back/forward cache; the logout example): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data
- MDN back/forward cache (a history navigation restores a snapshot without revalidating): https://developer.mozilla.org/en-US/docs/Glossary/bfcache
- Security header scanner: https://securityheaders.com/
