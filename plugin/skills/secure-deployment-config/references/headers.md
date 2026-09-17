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
