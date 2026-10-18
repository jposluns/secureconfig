---
version_basis: {
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "e17c3af4fb92d40391435139ae145152d8827211b3ff71dbcec2a3a642b8eb67",
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
    "nginx-source": {
      "name": "nginx source",
      "basis": "release-1.26.3",
      "sources": {
        "s24b0a72bc894": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L110-L116",
        "s0ae4e9bc8d07": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L216-L218",
        "sedd333de1a8c": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L665-L690",
        "sf6eac8f6749d": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796",
        "s70d54f325a93": "https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L843-L849"
      }
    },
    "apache-source": {
      "name": "Apache HTTP Server",
      "basis": "2.4.69",
      "sources": {
        "s2f07cea83845": "https://github.com/apache/httpd/blob/2.4.69/docs/manual/mod/mod_headers.xml#L311-L328"
      }
    },
    "caddy-source": {
      "name": "Caddy source",
      "basis": "v2.11.4",
      "sources": {
        "s0fa8b969b205": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/headers/caddyfile.go#L27-L48"
      }
    },
    "cloudflare-pages": {
      "name": "Cloudflare Pages documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s38b6aa1f9566": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L14",
        "sba79d4023eca": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L26"
      }
    },
    "scanner": {
      "name": "Security Headers scanner",
      "basis": "unknown",
      "sources": {
        "s7a94d0fcb6ad": "https://securityheaders.com/"
      }
    },
    "helmet": {
      "name": "Helmet",
      "basis": "v8.1.0",
      "sources": {
        "sf42121cfc014": "https://github.com/helmetjs/helmet/blob/v8.1.0/README.md#L3"
      }
    },
    "django": {
      "name": "Django",
      "basis": "5.2",
      "sources": {
        "se79954c08919": "https://docs.djangoproject.com/en/5.2/ref/middleware/#module-django.middleware.security"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "8.23.0",
      "sources": {
        "s2278b86c08a6": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L18-L20",
        "s3b9e19f23f2d": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L19-L22",
        "s38391c89b58d": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/silent.md#L20-L25",
        "sc1670c4672b4": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/show-error.md#L19",
        "s891e2566ea41": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/location.md#L23-L26",
        "sd386dc0317da": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/proto-redir.md#L19-L20",
        "sf7e7834afa89": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/proto.md#L30-L33",
        "s508454c45cf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23",
        "s62990c766776": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/dump-header.md#L21-L23",
        "seb2e6bc373fe": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/output.md#L53-L55",
        "s3aefa5f74fd4": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L20-L29",
        "se50d33437ccf": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L112-L114",
        "sc8658f8a2e89": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L5",
        "s3dbfd02b9aa2": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L5",
        "s5b5b25c9a3fe": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/silent.md#L5",
        "s24da6d0f30ba": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/show-error.md#L5",
        "s6bee713841f0": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/location.md#L5",
        "se89c7271eda2": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/dump-header.md#L5",
        "s93be9b76f8e2": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/output.md#L6",
        "s3633dd0e6b3e": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L5",
        "s9a3d23bc00be": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L358-L360"
      }
    }
  },
  "claims": {
    "placement": {"text": "Set response headers at a proxy with nginx add_header, Apache Header or Caddy header, in application middleware, or in a Cloudflare Pages _headers file for static asset responses; Pages Functions responses will likely need headers set in Functions code. Applying the three proxy directives to all six listed headers is this guide's inference.", "components": ["mdn", "helmet", "django", "nginx-source", "apache-source", "caddy-source", "cloudflare-pages"], "sources": ["mdn:s40155272e6bf", "helmet:sf42121cfc014", "django:se79954c08919", "nginx-source:s24b0a72bc894", "nginx-source:sf6eac8f6749d", "apache-source:s2f07cea83845", "caddy-source:s0fa8b969b205", "cloudflare-pages:s38b6aa1f9566", "cloudflare-pages:sba79d4023eca"], "status": "REASONED"},
    "hsts": {"text": "Use HSTS max-age=31536000 with includeSubDomains only after HTTPS works across the domain; every subdomain is committed to HTTPS and max-age=0 disables HSTS.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "hsts-preload": {"text": "Omit preload unless its commitment is understood; removal is slow, takes weeks and depends on browser list updates.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED"},
    "csp": {"text": "Start CSP at default-src 'self', tailor sources to the app and prefer script nonces or hashes over unsafe-inline; Verify requires an enforcing policy.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "csp-report-only": {"text": "Roll out Content-Security-Policy-Report-Only first on existing apps to find breakage; it enforces nothing and is not a substitute for enforcing CSP.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "nosniff": {"text": "Send X-Content-Type-Options: nosniff and verify that value on the final response.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "referrer": {"text": "Send Referrer-Policy: strict-origin-when-cross-origin and verify that final-response value.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "permissions": {"text": "Permissions-Policy disables camera, microphone and geolocation with empty allowlists; verify all three restrictions.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "framing": {"text": "X-Frame-Options: DENY or enforcing CSP frame-ancestors 'none' denies framing; supported frame-ancestors supersedes X-Frame-Options, and default-src does not cover it. frame-ancestors * overrides DENY.", "components": ["mdn"], "sources": ["mdn:s40155272e6bf"], "status": "REASONED", "verify": [1]},
    "all-responses": {"text": "Send headers on every response, including errors; nginx add_header inherits parent headers only when the child has no header list, and always covers statuses outside its default set. This guide assesses setting headers only on 200 / as a common proxy misconfiguration.", "components": ["mdn", "nginx-source"], "sources": ["mdn:s40155272e6bf", "nginx-source:sedd333de1a8c", "nginx-source:sf6eac8f6749d", "nginx-source:s0ae4e9bc8d07", "nginx-source:s70d54f325a93"], "status": "REASONED"},
    "shared-cache": {"text": "Use Cache-Control: private for authenticated responses or no-store for sensitive ones; cache only public content unless authenticated caching is explicitly configured.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a"], "status": "REASONED"},
    "cache-key": {"text": "A URL-only shared cache can leak one user's response to another; explicitly vary authenticated cache entries on the cookie or authorization header.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a", "mdn:s40155272e6bf"], "status": "REASONED"},
    "browser-cache": {"text": "private still permits browser storage; no-store forbids private and shared storage and belongs on authenticated responses and responses setting session cookies.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a"], "status": "REASONED"},
    "history-cache": {"text": "no-cache does not prevent a Back navigation from restoring a back/forward-cache snapshot without revalidation.", "components": ["mdn"], "sources": ["mdn:s9166d803cf3a", "mdn:s46957d9dc1d5"], "status": "REASONED"},
    "logout-cache": {"text": "Send Clear-Site-Data on logout confirmation; cache clears browser cache and may clear back/forward cache depending on the browser.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37", "mdn:s46957d9dc1d5"], "status": "REASONED"},
    "logout-cookies": {"text": "Clear-Site-Data cookies clears cookies across the registered domain and all subdomains, plus HTTP authentication credentials; invalidate the server session separately.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "logout-storage": {"text": "Clear-Site-Data storage removes origin local/session storage, IndexedDB and service-worker registrations; understand effects on companion applications before clearing.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "logout-header": {"text": "The cited MDN logout example includes cache, cookies, storage, executionContexts, prefetchCache and prerenderCache.", "components": ["mdn"], "sources": ["mdn:s7f290c45ad37"], "status": "REASONED"},
    "verify-fetch": {"text": "Fetch the final page with redirects restricted to HTTPS, bypass client proxies, discard the body and inspect the last response's headers and final status/URL; curl 8.23.0 documents the command options and write-out fields, while `-D -` printing each response's header block, and selecting the last one, are this guide's assessment.", "components": ["mdn", "curl"], "sources": ["mdn:s40155272e6bf", "curl:s2278b86c08a6", "curl:s3b9e19f23f2d", "curl:s38391c89b58d", "curl:sc1670c4672b4", "curl:s891e2566ea41", "curl:sd386dc0317da", "curl:sf7e7834afa89", "curl:s508454c45cf1", "curl:s62990c766776", "curl:seb2e6bc373fe", "curl:s3aefa5f74fd4", "curl:se50d33437ccf", "curl:s9a3d23bc00be", "curl:sc8658f8a2e89", "curl:s3dbfd02b9aa2", "curl:s5b5b25c9a3fe", "curl:s24da6d0f30ba", "curl:s6bee713841f0", "curl:se89c7271eda2", "curl:s93be9b76f8e2", "curl:s3633dd0e6b3e"], "status": "REASONED", "verify": [1]},
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

Metadata reviewed 2026-10-17; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- mdn: MDN HTTP documentation, unknown
- nginx-source: nginx source, release-1.26.3
- apache-source: Apache HTTP Server, 2.4.69
- caddy-source: Caddy source, v2.11.4
- cloudflare-pages: Cloudflare Pages documentation, c896795b8e8bab68d05ae78d64c9cbcda1fdb104
- scanner: Security Headers scanner, unknown
- helmet: Helmet, v8.1.0
- django: Django, 5.2
- curl: curl, 8.23.0

Claims (full source mapping in the front matter):

- placement (REASONED; mdn, helmet, django, nginx-source, apache-source, caddy-source, cloudflare-pages): Set response headers at a proxy with nginx add_header, Apache Header or Caddy header, in application middleware, or in a Cloudflare Pages _headers file for static asset responses; Pages Functions responses will likely need headers set in Functions code. Applying the three proxy directives to all six listed headers is this guide's inference.
- hsts (REASONED; mdn): Use HSTS max-age=31536000 with includeSubDomains only after HTTPS works across the domain; every subdomain is committed to HTTPS and max-age=0 disables HSTS.
- hsts-preload (REASONED; mdn): Omit preload unless its commitment is understood; removal is slow, takes weeks and depends on browser list updates.
- csp (REASONED; mdn): Start CSP at default-src 'self', tailor sources to the app and prefer script nonces or hashes over unsafe-inline; Verify requires an enforcing policy.
- csp-report-only (REASONED; mdn): Roll out Content-Security-Policy-Report-Only first on existing apps to find breakage; it enforces nothing and is not a substitute for enforcing CSP.
- nosniff (REASONED; mdn): Send X-Content-Type-Options: nosniff and verify that value on the final response.
- referrer (REASONED; mdn): Send Referrer-Policy: strict-origin-when-cross-origin and verify that final-response value.
- permissions (REASONED; mdn): Permissions-Policy disables camera, microphone and geolocation with empty allowlists; verify all three restrictions.
- framing (REASONED; mdn): X-Frame-Options: DENY or enforcing CSP frame-ancestors 'none' denies framing; supported frame-ancestors supersedes X-Frame-Options, and default-src does not cover it. frame-ancestors * overrides DENY.
- all-responses (REASONED; mdn, nginx-source): Send headers on every response, including errors; nginx add_header inherits parent headers only when the child has no header list, and always covers statuses outside its default set. This guide assesses setting headers only on 200 / as a common proxy misconfiguration.
- shared-cache (REASONED; mdn): Use Cache-Control: private for authenticated responses or no-store for sensitive ones; cache only public content unless authenticated caching is explicitly configured.
- cache-key (REASONED; mdn): A URL-only shared cache can leak one user's response to another; explicitly vary authenticated cache entries on the cookie or authorization header.
- browser-cache (REASONED; mdn): private still permits browser storage; no-store forbids private and shared storage and belongs on authenticated responses and responses setting session cookies.
- history-cache (REASONED; mdn): no-cache does not prevent a Back navigation from restoring a back/forward-cache snapshot without revalidation.
- logout-cache (REASONED; mdn): Send Clear-Site-Data on logout confirmation; cache clears browser cache and may clear back/forward cache depending on the browser.
- logout-cookies (REASONED; mdn): Clear-Site-Data cookies clears cookies across the registered domain and all subdomains, plus HTTP authentication credentials; invalidate the server session separately.
- logout-storage (REASONED; mdn): Clear-Site-Data storage removes origin local/session storage, IndexedDB and service-worker registrations; understand effects on companion applications before clearing.
- logout-header (REASONED; mdn): The cited MDN logout example includes cache, cookies, storage, executionContexts, prefetchCache and prerenderCache.
- verify-fetch (REASONED; mdn, curl): Fetch the final page with redirects restricted to HTTPS, bypass client proxies, discard the body and inspect the last response's headers and final status/URL; curl 8.23.0 documents the command options and write-out fields, while &#96;-D -&#96; printing each response's header block, and selecting the last one, are this guide's assessment.
- verify-values (REASONED; mdn): Judge header values on the final response, not presence on an earlier hop; missing final headers are findings and a failed fetch is inconclusive.
- verify-scanner (REASONED; scanner): Use the external Security Headers scanner for a second opinion; the guide states that it fetches with GET.
- verify-csp (REASONED; mdn): Unexpected console violations must be absent in normal use, but this alone is insufficient; confirm a deliberately disallowed resource is blocked while an allowed one loads.
- verify-cache (REASONED; mdn): Warm an authenticated URL in the shared cache, then request it as user A, user B and anonymously; each response must belong only to its caller.
- verify-logout (REASONED; mdn): After logout, Back must not restore authenticated content; verify a request to the login screen and inspect no-store and Clear-Site-Data separately in every supported browser.
<!-- version-basis:end -->

TLS protects the transport; these response headers protect the page. Set them at the proxy ([`add_header`](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L110-L116) in [nginx.md](nginx.md), [`Header`](https://github.com/apache/httpd/blob/2.4.69/docs/manual/mod/mod_headers.xml#L311-L328) in [apache.md](apache.md), [`header`](https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/headers/caddyfile.go#L27-L48) in Caddy), in app middleware (helmet for Express per [nodejs.md](nodejs.md), Django's security settings per [python.md](python.md)), or in a [`_headers` file](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L14) for Cloudflare Pages static asset responses. Cloudflare Pages does not apply `_headers` to Pages Functions responses; set those headers in [Functions code](https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L26). Applying the three proxy directives to all six headers below is this guide's inference.

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
- Headers belong on every response, including error pages; this guide assesses setting them only on `200 /` as a common proxy misconfiguration. In nginx, `add_header` inherits the parent's headers only if a child has no header list ([merge](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L665-L690); [list creation](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796)), and [`always`](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L843-L849) covers statuses outside its default set ([status handling](https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L216-L218); [nginx.md](nginx.md)).

## Do not cache authenticated responses in a shared cache

A CDN or shared proxy that keys its cache on the URL alone can serve one user's authenticated response to another. Set `Cache-Control: private` on authenticated responses, or `no-store` on the most sensitive ones, and mark cacheable only what is truly public. If a shared cache must hold authenticated content, configure it explicitly to vary on the cookie or the authorization header rather than relying on its default URL-only key.

## Keep authenticated pages out of the browser's own cache

`private` stops a shared cache from holding a response, but it still lets the user's own browser store it: MDN defines `private` as a response the browser's local cache may keep. So the Back button can redisplay an authenticated page after logout, and a chat transcript can sit in the history of a shared machine. Set `Cache-Control: no-store` on any response that carries authenticated content or sets a session cookie; MDN defines `no-store` as "any caches of any kind (private or shared) should not store this response", which covers the browser too.

On logout, clear what the browser already holds. `Cache-Control: no-cache` does not cover this, because a history navigation such as the Back button can restore a back/forward-cache snapshot without revalidating. Send the `Clear-Site-Data` header on the logout-confirmation response instead: its `cache` directive clears the browser cache and, depending on the browser, the back/forward cache as well, and `cookies` clears the client-side session cookie (invalidate the server-side session separately, as part of logout). MDN's own logout example is `Clear-Site-Data: "cache", "cookies", "storage", "executionContexts", "prefetchCache", "prerenderCache"`. Know the scope before sending the full set: `"cookies"` clears cookies across the entire registered domain (all subdomains) and also clears HTTP authentication credentials, and `"storage"` removes origin local/session storage, IndexedDB, and service-worker registrations, so a shared parent domain or a companion app on a subdomain is affected too.

## Verify

REASONED: final-response header inspection follows the cited MDN header documentation; curl 8.23.0 documents the command options and write-out fields, while `-D -` printing each response's header block, and selecting the last one, are this guide's assessment. No deployment URL was supplied for live checks, and this guide records no run; the following block states the expected values and treats failed fetches as inconclusive.

```bash
# -q (first) skips curlrc, -g disables URL globbing, and -sS hides progress but shows errors.
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

REASONED: preceding block; final-response header values, external scanning and CSP discrimination, per the guide's cited MDN HTTP headers reference and Security header scanner. No deployed application or controlled browser application session is available, and network access is unavailable. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics; no HTTP response or browser outcome was observed. Exposed responses omit effective controls or allow the forbidden resource; fixed final responses carry the stated values and block the forbidden resource while permitting the allowed control. Then scan with https://securityheaders.com/ from outside for a second opinion (it fetches with GET). No UNEXPECTED CSP console violations during normal application use is necessary but not sufficient: a permissive CSP produces none, and a correct policy still logs a violation when it blocks something (the negative test below, an attack, or an unwanted load). Confirm the policy actually blocks by loading a page with a deliberately disallowed resource (an inline script the policy forbids, or an off-origin image) and checking it is refused while an allowed resource still loads.

REASONED: shared-cache caller separation, per the guide's cited MDN Cache-Control. No deployed shared cache or authenticated A/B accounts are available; this prose supplies no local command or configuration to execute. No response sequence was observed. Exposed caching replays a previous caller's private content; fixed responses after warming the same URL belong only to their current authenticated or anonymous caller. For an authenticated route behind a shared cache, request the same URL as user A, then as user B, then anonymously, after warming the cache; each response must reflect only its own caller, never the one before it.

REASONED: logout, browser history and response-header inspection, per the guide's cited MDN Cache-Control, MDN Clear-Site-Data and MDN back/forward cache. No application session or supported-browser deployment matrix is available; this prose supplies no local command or configuration to execute. No logout sequence was observed. Exposed history restores authenticated content after logout; the expected fixed outcome is a new request reaching login, with no-store and Clear-Site-Data checked independently in every supported browser. In a real browser, log in, open an authenticated page, then log out and press the Back button: the authenticated page must not reappear from history. The browser should re-request it and land on the login screen. That confirms the logout outcome, not which header produced it, so also inspect the authenticated and logout responses for the intended `no-store` and `Clear-Site-Data` headers. Because the back/forward-cache clearing is browser-dependent, run the check in each browser you support.

## Sources (checked September 2026)

- MDN HTTP headers reference (Strict-Transport-Security, Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, X-Frame-Options): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers
- MDN Cache-Control (`no-store` forbids any cache including the browser; `private` still permits the browser's local cache): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control
- MDN Clear-Site-Data (the `cache` directive clears the browser cache and, depending on the browser, the back/forward cache; the logout example): https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Clear-Site-Data
- MDN back/forward cache (a history navigation restores a snapshot without revalidating): https://developer.mozilla.org/en-US/docs/Glossary/bfcache
- Security header scanner: https://securityheaders.com/
- Helmet v8.1.0 response-header middleware (checked October 2026): https://github.com/helmetjs/helmet/blob/v8.1.0/README.md#L3
- Django 5.2 SecurityMiddleware (checked October 2026): https://docs.djangoproject.com/en/5.2/ref/middleware/#module-django.middleware.security
- nginx release-1.26.3 add_header directive (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L110-L116
- nginx release-1.26.3 add_header list creation (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L788-L796
- nginx release-1.26.3 header inheritance (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L665-L690
- nginx release-1.26.3 always status handling (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L216-L218
- nginx release-1.26.3 always option (checked October 2026): https://github.com/nginx/nginx/blob/release-1.26.3/src/http/modules/ngx_http_headers_filter_module.c#L843-L849
- Apache 2.4.69 Header response-header directive (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/docs/manual/mod/mod_headers.xml#L311-L328
- Caddy v2.11.4 header response-header directive (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/headers/caddyfile.go#L27-L48
- Cloudflare Pages _headers on static assets (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104) (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L14
- Cloudflare Pages _headers Pages Functions limit (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104) (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/pages/configuration/headers.mdx#L26
- curl 8.23.0 --disable (first argument skips curlrc) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L18-L20
- curl 8.23.0 --globoff (disables URL globbing) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L19-L22
- curl 8.23.0 --silent (quiet mode with --show-error) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/silent.md#L20-L25
- curl 8.23.0 --show-error (reports errors with --silent) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/show-error.md#L19
- curl 8.23.0 --location (follows redirects) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/location.md#L23-L26
- curl 8.23.0 --proto-redir (restricts redirect protocols) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/proto-redir.md#L19-L20
- curl 8.23.0 --proto (= permits only the named protocol) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/proto.md#L30-L33
- curl 8.23.0 --noproxy (* disables proxy use) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23
- curl 8.23.0 --dump-header (- writes headers to stdout) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/dump-header.md#L21-L23
- curl 8.23.0 --output (/dev/null discards the body) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/output.md#L53-L55
- curl 8.23.0 --write-out (format and variables) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L20-L29
- curl 8.23.0 --write-out http_code (last response code) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L112-L114
- curl 8.23.0 --write-out url_effective (last fetched URL) (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L358-L360
- curl 8.23.0 --disable short form -q (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/disable.md#L5
- curl 8.23.0 --globoff short form -g (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L5
- curl 8.23.0 --silent short form -s (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/silent.md#L5
- curl 8.23.0 --show-error short form -S (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/show-error.md#L5
- curl 8.23.0 --location short form -L (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/location.md#L5
- curl 8.23.0 --dump-header short form -D (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/dump-header.md#L5
- curl 8.23.0 --output short form -o (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/output.md#L6
- curl 8.23.0 --write-out short form -w (checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/write-out.md#L5
