---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "808963ba1a2f2fa2449413a34edaafcba712497f2b46e1c6e2670ea95e07d0a1",
  "components": {
    "adapter": {
      "name": "SvelteKit adapter-node",
      "basis": "@sveltejs/adapter-node@5.5.7",
      "sources": {
        "s011f4e44c91a": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/env.js#L46-L50",
        "s93f13e6b8d31": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/index.js#L10-L12",
        "sd23cac9a730f": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/index.js#L57-L60",
        "s200d6e800c74": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/index.js#L24-L38",
        "sf17c5646623c": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/index.js#L118",
        "s1ffeda9bbb37": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/handler.js#L69",
        "s8d4fa8e7426b": "https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/handler.js#L243"
      }
    },
    "svelte": {
      "name": "SvelteKit documentation",
      "basis": "unknown",
      "sources": {
        "sc183fdb68165": "https://svelte.dev/docs/kit/$env-static-public",
        "s59abf03bae6a": "https://svelte.dev/docs/kit/adapter-node",
        "s329dda89ba78": "https://svelte.dev/docs/kit/configuration",
        "se2fdc4fd5885": "https://svelte.dev/docs/kit/server-only-modules"
      }
    },
    "nuxt": {
      "name": "Nuxt documentation",
      "basis": "4.x",
      "sources": {
        "se2d1e4a2e433": "https://nuxt.com/docs/4.x/directory-structure/server",
        "s32e447cb5ef4": "https://nuxt.com/docs/4.x/guide/going-further/runtime-config"
      }
    },
    "vite-pin": {
      "name": "Vite bind source",
      "basis": "v8.3.1",
      "sources": {
        "s4b7c35b93a62": "https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/utils.ts#L1010-L1016",
        "s151e8dbf59a2": "https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/config.ts#L390",
        "s484948ac14b6": "https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/build.ts#L395"
      }
    },
    "vite": {
      "name": "Vite documentation",
      "basis": "unknown",
      "sources": {
        "sae9dd90908fc": "https://vite.dev/config/server-options",
        "s16927b810cff": "https://vite.dev/guide/cli",
        "s7c70a12e43ed": "https://vite.dev/config/build-options",
        "sba6dbfdd7590": "https://vite.dev/guide/ssr"
      }
    },
    "grep": {
      "name": "GNU grep",
      "basis": "unknown",
      "sources": {
        "sea43e82b0753": "https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html",
        "s2c1251092e66": "https://www.gnu.org/software/grep/manual/html_node/General-Output-Control.html",
        "sd00017f70dae": "https://www.gnu.org/software/grep/manual/html_node/Matching-Control.html"
      }
    },
    "nuxt-output": {
      "name": "Nuxt output source",
      "basis": "v4.0.0",
      "sources": {
        "s793a18962748": "https://github.com/nuxt/nuxt/blob/v4.0.0/packages/nuxt/src/core/nitro.ts#L167",
        "sdd39f0826f92": "https://github.com/nuxt/nuxt/blob/v4.0.0/packages/nuxt/src/core/nitro.ts#L657"
      }
    },
    "nitro-output": {
      "name": "Nitro output defaults",
      "basis": "2.12.0",
      "sources": {
        "sbe9fd1f61fe0": "https://cdn.jsdelivr.net/npm/nitropack@2.12.0/dist/core/index.mjs",
        "s47fff9b24fba": "https://nitro.build/config",
        "s51e38e411bfa": "https://nitro.build/docs/assets"
      }
    }
  },
  "claims": {
    "adapter-bind": {"text": "adapter-node defaults 0.0.0.0:3000 only with SOCKET_PATH unset/empty and no systemd socket; set HOST=127.0.0.1 PORT=3000.", "components": ["adapter", "svelte"], "sources": ["adapter:s011f4e44c91a", "adapter:s93f13e6b8d31", "adapter:sd23cac9a730f", "svelte:s59abf03bae6a"], "status": "REASONED"},
    "adapter-origin": {"text": "Set ORIGIN to external HTTPS origin; trust PROTOCOL_HEADER/HOST_HEADER only behind a trusted proxy.", "components": ["svelte"], "sources": ["svelte:s59abf03bae6a"], "status": "REASONED"},
    "adapter-ip": {"text": "ADDRESS_HEADER and XFF_DEPTH configure proxy-derived client IP and require trusted proxy handling.", "components": ["svelte"], "sources": ["svelte:s59abf03bae6a"], "status": "REASONED"},
    "csrf-check": {"text": "csrf.checkOrigin defaults true, deprecated; checks cross-origin POST/PUT/PATCH/DELETE form content types, not JSON/arbitrary content needing origin/session checks.", "components": ["svelte"], "sources": ["svelte:s329dda89ba78"], "status": "REASONED"},
    "csrf-trust": {"text": "csrf.trustedOrigins defaults empty; list specific form origins, with wildcard trust discouraged.", "components": ["svelte"], "sources": ["svelte:s329dda89ba78"], "status": "REASONED"},
    "svelte-public": {"text": "PUBLIC_ via env.publicPrefix exposes static public env values at build; keep secrets out.", "components": ["svelte"], "sources": ["svelte:sc183fdb68165", "svelte:s329dda89ba78"], "status": "REASONED"},
    "svelte-private": {"text": "Private env modules, .server.js and lib/server are server-only; client import chains, including dynamic imports, fail builds.", "components": ["svelte"], "sources": ["svelte:se2fdc4fd5885"], "status": "REASONED"},
    "svelte-routes": {"text": "Guide requires checks in page loads, form actions and endpoints rather than a layout; Sources omit a direct routing/auth citation.", "components": ["svelte"], "sources": ["svelte:s329dda89ba78"], "status": "REASONED"},
    "svelte-handle": {"text": "Guide requires handle to block, not merely attach locals or redirect page navigation, and resource checks near data; Sources omit hook semantics/calling-page qualification.", "components": ["svelte"], "sources": ["svelte:s329dda89ba78"], "status": "REASONED"},
    "nuxt-handlers": {"text": "Nuxt auto-registers server/api, server/routes and middleware; middleware runs first, but context.auth alone enforces nothing. Throw/end requests or check each handler.", "components": ["nuxt"], "sources": ["nuxt:se2d1e4a2e433"], "status": "REASONED"},
    "nuxt-auth": {"text": "Nuxt ships no built-in authentication; enforce access server-side, not with client redirects.", "components": ["nuxt"], "sources": ["nuxt:se2d1e4a2e433"], "status": "REASONED"},
    "nuxt-private": {"text": "Direct runtimeConfig keys are server-only with NUXT_ overrides; rendering or passing to useState can disclose them.", "components": ["nuxt"], "sources": ["nuxt:s32e447cb5ef4"], "status": "REASONED"},
    "nuxt-public": {"text": "runtimeConfig.public is client-exposed with NUXT_PUBLIC_ overrides, not proxy/cookie configuration.", "components": ["nuxt"], "sources": ["nuxt:s32e447cb5ef4"], "status": "REASONED"},
    "vite-production": {"text": "Vite dev/preview is development tooling; deploy dist through a production server, CDN or platform.", "components": ["vite"], "sources": ["vite:s16927b810cff"], "status": "REASONED"},
    "vite-bind": {"text": "Vite 8.3.1 server.host defaults localhost; true/0.0.0.0 exposes all addresses and should not remain beyond trusted-network tests.", "components": ["vite-pin", "vite"], "sources": ["vite-pin:s4b7c35b93a62", "vite:sae9dd90908fc"], "status": "REASONED"},
    "vite-hosts": {"text": "server.allowedHosts defaults empty with localhost, .localhost and IPs allowed; true disables protection and permits DNS rebinding. Prefer explicit names.", "components": ["vite"], "sources": ["vite:sae9dd90908fc"], "status": "REASONED"},
    "verify-private": {"text": "Guide expects anonymous /api/private 401; enforcement needs app/server handlers, not client redirects.", "components": ["nuxt", "svelte"], "sources": ["nuxt:se2d1e4a2e433", "svelte:s329dda89ba78"], "status": "REASONED", "verify": [1]},
    "verify-secret": {"text": "Scan browser-served output: adapter-node build/client and build/prerendered, Nuxt .output/public, Vite dist, scanned whole; only a result with every match under dist/server/ is reported as server output, else FINDING. Adjust paths for custom layouts/SSR; reject absence. Prompt full literal secret; grep stdin: 0 finding, 1 no match, others errors. Clean cannot rule out transformed secrets or runtime responses; input protects argv only.", "components": ["grep", "adapter", "nuxt-output", "nitro-output", "vite-pin", "vite"], "sources": ["grep:sea43e82b0753", "grep:s2c1251092e66", "grep:sd00017f70dae", "adapter:s200d6e800c74", "adapter:sf17c5646623c", "adapter:s1ffeda9bbb37", "adapter:s8d4fa8e7426b", "nuxt-output:s793a18962748", "nuxt-output:sdd39f0826f92", "nitro-output:sbe9fd1f61fe0", "nitro-output:s47fff9b24fba", "nitro-output:s51e38e411bfa", "vite-pin:s151e8dbf59a2", "vite-pin:s484948ac14b6", "vite:s7c70a12e43ed", "vite:sba6dbfdd7590"], "status": "REASONED", "verify": [1]},
    "verify-host": {"text": "Spoofed Host must not be trusted; supplied allowlist reference is Vite-specific.", "components": ["vite"], "sources": ["vite:sae9dd90908fc"], "status": "REASONED", "verify": [1]},
    "verify-proxy": {"text": "Check Secure cookies and HTTPS redirects with SvelteKit ORIGIN; verify Nuxt for its preset/platform, not NUXT_PUBLIC_.", "components": ["svelte", "nuxt"], "sources": ["svelte:s59abf03bae6a", "nuxt:s32e447cb5ef4"], "status": "REASONED", "verify": [1]}
  }
}
---
# Full-stack JS frameworks: SvelteKit, Nuxt, Vite

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| adapter-bind: adapter-node defaults 0.0.0.0:3000 only with SOCKET_PATH unset/empty and no systemd socket; set HOST=127.0.0.1 PORT=3000. | SvelteKit adapter-node @sveltejs/adapter-node@5.5.7; SvelteKit documentation unknown | REASONED |
| adapter-origin: Set ORIGIN to external HTTPS origin; trust PROTOCOL_HEADER/HOST_HEADER only behind a trusted proxy. | SvelteKit documentation unknown | REASONED |
| adapter-ip: ADDRESS_HEADER and XFF_DEPTH configure proxy-derived client IP and require trusted proxy handling. | SvelteKit documentation unknown | REASONED |
| csrf-check: csrf.checkOrigin defaults true, deprecated; checks cross-origin POST/PUT/PATCH/DELETE form content types, not JSON/arbitrary content needing origin/session checks. | SvelteKit documentation unknown | REASONED |
| csrf-trust: csrf.trustedOrigins defaults empty; list specific form origins, with wildcard trust discouraged. | SvelteKit documentation unknown | REASONED |
| svelte-public: PUBLIC_ via env.publicPrefix exposes static public env values at build; keep secrets out. | SvelteKit documentation unknown | REASONED |
| svelte-private: Private env modules, .server.js and lib/server are server-only; client import chains, including dynamic imports, fail builds. | SvelteKit documentation unknown | REASONED |
| svelte-routes: Guide requires checks in page loads, form actions and endpoints rather than a layout; Sources omit a direct routing/auth citation. | SvelteKit documentation unknown | REASONED |
| svelte-handle: Guide requires handle to block, not merely attach locals or redirect page navigation, and resource checks near data; Sources omit hook semantics/calling-page qualification. | SvelteKit documentation unknown | REASONED |
| nuxt-handlers: Nuxt auto-registers server/api, server/routes and middleware; middleware runs first, but context.auth alone enforces nothing. Throw/end requests or check each handler. | Nuxt documentation 4.x | REASONED |
| nuxt-auth: Nuxt ships no built-in authentication; enforce access server-side, not with client redirects. | Nuxt documentation 4.x | REASONED |
| nuxt-private: Direct runtimeConfig keys are server-only with NUXT_ overrides; rendering or passing to useState can disclose them. | Nuxt documentation 4.x | REASONED |
| nuxt-public: runtimeConfig.public is client-exposed with NUXT_PUBLIC_ overrides, not proxy/cookie configuration. | Nuxt documentation 4.x | REASONED |
| vite-production: Vite dev/preview is development tooling; deploy dist through a production server, CDN or platform. | Vite documentation unknown | REASONED |
| vite-bind: Vite 8.3.1 server.host defaults localhost; true/0.0.0.0 exposes all addresses and should not remain beyond trusted-network tests. | Vite bind source v8.3.1; Vite documentation unknown | REASONED |
| vite-hosts: server.allowedHosts defaults empty with localhost, .localhost and IPs allowed; true disables protection and permits DNS rebinding. Prefer explicit names. | Vite documentation unknown | REASONED |
| verify-private: Guide expects anonymous /api/private 401; enforcement needs app/server handlers, not client redirects. | Nuxt documentation 4.x; SvelteKit documentation unknown | REASONED |
| verify-secret: Scan browser-served output: adapter-node build/client and build/prerendered, Nuxt .output/public, Vite dist, scanned whole; only a result with every match under dist/server/ is reported as server output, else FINDING. Adjust paths for custom layouts/SSR; reject absence. Prompt full literal secret; grep stdin: 0 finding, 1 no match, others errors. Clean cannot rule out transformed secrets or runtime responses; input protects argv only. | GNU grep unknown; SvelteKit adapter-node @sveltejs/adapter-node@5.5.7; Nuxt output source v4.0.0; Nitro output defaults 2.12.0; Vite bind source v8.3.1; Vite documentation unknown | REASONED |
| verify-host: Spoofed Host must not be trusted; supplied allowlist reference is Vite-specific. | Vite documentation unknown | REASONED |
| verify-proxy: Check Secure cookies and HTTPS redirects with SvelteKit ORIGIN; verify Nuxt for its preset/platform, not NUXT_PUBLIC_. | SvelteKit documentation unknown; Nuxt documentation 4.x | REASONED |
<!-- version-basis:end -->

SvelteKit, Nuxt, and Vite-based apps built by AI assistants inherit the same traps as [nextjs.md](nextjs.md): a server bind that can default wide open (SvelteKit's Node adapter binds `0.0.0.0` as of adapter-node 5.5.7, though Vite's dev server defaults to `localhost` as of Vite 8.3.1), a proxy that has to be explicitly trusted before secure cookies and correct origins work, and a public-env prefix that ships anything given it straight to the browser. Each framework also has more than one server entry point (endpoints, server routes, load functions), and a check placed in only one of them leaves the others open, exactly as with Next.js layouts versus Server Actions.

## SvelteKit (`adapter-node`)

The built server "will accept connections on `0.0.0.0` using port 3000" by default (host and port as of adapter-node 5.5.7; the port default applies only when `SOCKET_PATH` is unset or empty, and none of this applies when systemd socket activation hands the process a socket); override with `HOST` and `PORT`:

```bash
HOST=127.0.0.1 PORT=3000 node build
```

Behind a reverse proxy, set `ORIGIN` (for example `ORIGIN=https://app.example.com`) so SvelteKit computes the correct origin for redirects and cookies. `PROTOCOL_HEADER` and `HOST_HEADER` (for example `x-forwarded-proto` and `x-forwarded-host`) let it read the real scheme and host from the proxy; the docs caution to set these only behind a trusted reverse proxy, since an untrusted client could otherwise spoof them. `ADDRESS_HEADER` and `XFF_DEPTH` do the same for the client's real IP.

CSRF: `csrf.checkOrigin` (default `true`, deprecated in the current reference) checks the `Origin` header for a POST, PUT, PATCH, or DELETE form submission whose `Content-Type` is `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain`, rejecting a mismatch with "Cross-site POST form submissions are forbidden." It does not inspect a JSON body or any other content type reaching a `+server.js` endpoint or form action, so those still need their own origin or session check. The docs point to `csrf.trustedOrigins` instead: an allowlist (default empty) of specific origins permitted to submit forms cross site; only `'*'` trusts every origin, and the docs call that generally not recommended.

Public env: only variables prefixed `PUBLIC_` (`env.publicPrefix`) are "statically injected into your bundle at build time" and reachable from `$env/static/public`; anything else throws if imported from client code. Keep secrets in modules SvelteKit treats as server-only, either `$env/static/private` / `$env/dynamic/private`, a `.server.js` filename, or anything under `$lib/server/` ([secrets.md](secrets.md)); SvelteKit statically traces import chains and fails the build if client code imports one, even through a dynamic `import()`.

None of this gates a request for you by default: a `+layout.server.js` guard does not protect a sibling `+page.server.js` load function, a form action, or a `+server.js` endpoint reached directly, so each needs its own session check, the same pattern as the Next.js Data Access Layer in [nextjs.md](nextjs.md). The `handle` hook in `hooks.server.js` can enforce access, since it runs on every request and may return a `Response` before `resolve` renders the route, but only when it actually checks the session and blocks; using it just to redirect an unauthenticated page navigation, or just to attach identity onto `event.locals` for other handlers to read, still leaves a directly reached `+server.js` endpoint or form action open. Inside `handle`, `event.url`, `route`, and `params` can reflect the calling page rather than the resource actually being requested, so do not rely on them alone to decide what is being authorized; checking the session there is necessary but not sufficient, since a session check alone does not authorize access to the specific resource, so also enforce that check at the point each resource is served. Wire real authentication with an identity provider or library per [oidc-integration.md](oidc-integration.md), not a client-side redirect alone.

## Nuxt (Nitro server routes)

Files under `server/api/`, `server/routes/`, and `server/middleware/` are auto-registered Nitro handlers exported with `defineEventHandler()`, and a handler in `server/middleware/` runs before every other server route. Nuxt ships no built-in authentication. A middleware handler can enforce access if it throws (for example `createError` with a 401 or 403) or otherwise ends the request there; one that only attaches `event.context.auth` for other handlers to read has not enforced anything, and every handler that reads it still has to check it itself:

```ts
// server/api/admin.ts: the route checks for itself; the middleware only sets event.context.auth
export default defineEventHandler((event) => {
  if (!event.context.auth?.user) {
    event.node.res.statusCode = 401
    return { message: 'Not authenticated' }
  }
})
```

`runtimeConfig` splits the same way as Next's env prefix: keys directly on `runtimeConfig` are "only available within server-side"; keys under `runtimeConfig.public` are "also exposed to the client-side." Environment variables override both, using an uppercase `NUXT_` prefix with underscores between key segments: private keys just need `NUXT_` (for example `NUXT_API_SECRET`), public keys need `NUXT_PUBLIC_` (for example `NUXT_PUBLIC_API_BASE`). The docs warn not to "expose runtime config keys to the client-side by either rendering them or passing them to `useState`" even when they are private on the server.

## Vite (dev and preview servers)

Both are development tooling, not a production server: the `vite preview` docs say plainly "do not use this as a production server as it's not designed for it." Deploy the built `dist/` behind a real server, CDN, or your platform's hosting per [paas.md](paas.md) instead.

`server.host` defaults to `'localhost'` (as of Vite 8.3.1); setting it to `true` or `0.0.0.0` makes the dev server listen on all addresses, including the LAN, which is fine for testing from a phone on a trusted network but should not be left on elsewhere. `server.allowedHosts` defaults to `[]`, which still auto-permits localhost, `.localhost`, and IP addresses; setting it to `true` disables the check entirely, and the docs warn this "allows any website to send requests to your dev server and download your source code and content" (DNS rebinding). Prefer an explicit hostname allowlist over `true`.

## Verify

Run from the project root after a production build. The paths below cover default SvelteKit adapter-node output (`build/client` plus the separate `build/prerendered`), Nuxt/Nitro public output (`.output/public`, including copied public assets and prerendered pages), and a plain Vite client build (`dist`, including copied public assets). They exclude adapter-node server output and Nitro `.output/server`.

Before running, adjust both path lists for your actual adapter, Nitro preset or configured output directories. The block always scans all of `dist`, so it never misses a browser-served file. In a Vite SSR layout, where `dist/server` holds the server build, a result whose matches are all under `dist/server/` is reported as server output rather than as a client leak, and any other match is a FINDING. Confirm that `dist/server` is server-only in your deployment before treating a server-output result as clean. Include any separately deployed static assets and prerendered HTML, and, apart from `dist` (scanned whole, as described above), never select a parent containing server-only output. This file scan does not inspect dynamically rendered HTML or API responses.

REASONED: following block; private-route denial, client-secret scanning, Host handling and proxy cookies/redirects. No deployed framework application or run outcome is recorded here; expectations are reasoned from the guide and its cited framework and grep documentation.

```bash
curl -q -si https://app.example.com/api/private | head -1   # 401 with no session cookie, on all three frameworks
ls -d build/client build/prerendered .output/public dist 2>/dev/null  # confirm browser-served output paths
# Use the browser-served paths above; adapt both lists for custom output or SSR before running.
# Search client assets and prerendered pages for the literal secret with a fixed-string match. The secret is prompted
# (input hidden) and reaches grep on stdin (-f - reads the patterns from stdin), never grep's argv; -l prints only
# file names, so a finding does not echo the secret. Only the listed directories that exist are searched;
# adapter-node can produce two. The block refuses when none exists. grep's exit status is read separately, so an inherited
# `set -e` cannot abort on a clean result: 0 is a finding, 1 is clean, anything else is an error, with grep's own
# diagnostics left visible. Paste this subshell by itself: without bracketed paste, a line pasted after its closing )
# becomes the search value instead, and its clean result then means nothing.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set --
  for d in build/client build/prerendered .output/public dist; do [ -d "$d" ] && set -- "$@" "$d"; done
  [ "$#" -gt 0 ] || { echo 'inconclusive: no listed browser-served output directory here; build first and check the paths'; exit 2; }
  { unset -n client_secret && unset -v client_secret; } 2>/dev/null ||
    { echo 'cannot initialize secret input; not scanning'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not scanning'; exit 2; }
  IFS= read -r -s -p 'Secret value to search for (input hidden), then Enter: ' client_secret < /dev/tty || exit 2
  printf '\n'
  case "$client_secret" in
    ''|*[[:cntrl:]]*) echo 'the full secret value is required; not scanning'; exit 2 ;;
  esac
  # File names are not secret: capture them so matches under dist/server/ (a Vite SSR server build) are reported apart.
  if hits=$(printf '%s\n' "$client_secret" | grep -rlF -f - -- "$@"); then rc=0; else rc=$?; fi
  case "$rc" in
    0)
      # FINDING is the default; only a positively classified all-dist/server/ result is reported as server output.
      client_hits=$(printf '%s\n' "$hits" | grep -av '^dist/server/' || :)
      server_hits=$(printf '%s\n' "$hits" | grep -a '^dist/server/' || :)
      printf '%s\n' "$hits"
      if [ -z "$client_hits" ] && [ -n "$server_hits" ]; then
        echo "server output only: every match is under dist/server/, which a Vite SSR build does not serve to browsers; confirm dist/server is server-only in your deployment before treating this as clean"
      else
        echo "FINDING: the secret is in the built client output"
      fi
      ;;
    1) echo "clean: secret not found in $*" ;;
    *) echo "error: grep exited $rc, result inconclusive" ;;
  esac
)
curl -q -si https://app.example.com/ -H "Host: evil.example.com" | head -1   # a spoofed Host is not trusted
```

The prompt keeps the secret out of process argv only; it does not hide it from shell history, `set -x` tracing, or your own account's view of the process. A clean grep result here is evidence, not proof: it means the literal value did not match in the directories searched, not that the secret cannot be present in some other form. A bundler could split, encode, or otherwise transform it, so check the exit code and confirm the directory actually exists rather than reading silence alone as clean.

Behind a reverse proxy, confirm cookies still carry `Secure` and redirects use an `https://` `Location` once `ORIGIN` (SvelteKit) is set; without it, SvelteKit often builds an `http://` URL even though the browser connection is TLS. `NUXT_PUBLIC_...` is the public runtime-config prefix, exposed straight to the client bundle; it is not a trusted-proxy or secure-cookie setting and does nothing for this check. Nuxt's own trusted-proxy and origin handling come from its deployment preset and hosting platform rather than one documented app-level variable, so verify the equivalent behavior against whichever adapter you deploy with.

## Common mistakes

- Treating a SvelteKit `handle` hook that only redirects an unauthenticated page navigation, or a Nuxt `server/middleware/` that only attaches `event.context.auth`, as if it already enforced access, while the `+server.js` endpoint, form action, or `server/api/` route trusts that it happened and skips its own check.
- Leaving `server.allowedHosts` at `true`, or `server.host` wide open, past a local demo.
- Naming a secret `PUBLIC_...` or `NUXT_PUBLIC_...` out of habit from a genuinely public value.

## Sources (checked September 2026)

- SvelteKit adapter-node output defaults and client and prerendered writes (pinned tag @sveltejs/adapter-node@5.5.7): https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/index.js#L24-L38
- SvelteKit adapter-node server chunks under build/server (pinned tag @sveltejs/adapter-node@5.5.7): https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/index.js#L118
- SvelteKit adapter-node serves the separate prerendered directory (pinned tag @sveltejs/adapter-node@5.5.7): https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/handler.js#L69
- SvelteKit adapter-node serves client files and prerendered pages before SSR (pinned tag @sveltejs/adapter-node@5.5.7): https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/handler.js#L243
- Nuxt 4.x public build assets passed to Nitro (additional source pin v4.0.0): https://github.com/nuxt/nuxt/blob/v4.0.0/packages/nuxt/src/core/nitro.ts#L167
- Nuxt static dist alias targets Nitro public output (additional source pin v4.0.0): https://github.com/nuxt/nuxt/blob/v4.0.0/packages/nuxt/src/core/nitro.ts#L657
- Nitro 2.12.0, the nitropack version Nuxt v4.0.0 pins, output defaults .output, .output/server and .output/public (published build, lines 67 to 69): https://cdn.jsdelivr.net/npm/nitropack@2.12.0/dist/core/index.mjs
- Nitro output defaults and prerender destination (supplementary, unversioned documentation): https://nitro.build/config
- Nitro public assets copied to production public output (supplementary, unversioned documentation): https://nitro.build/docs/assets
- Vite default build.outDir 'dist' (pinned tag v8.3.1): https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/build.ts#L395
- Vite public assets copied to build output (pinned tag v8.3.1): https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/config.ts#L390
- Vite build output directory and public-copy defaults: https://vite.dev/config/build-options
- Vite SSR uses separate client and server builds: https://vite.dev/guide/ssr
- SvelteKit adapter-node: https://svelte.dev/docs/kit/adapter-node
- SvelteKit server-only modules: https://svelte.dev/docs/kit/server-only-modules
- SvelteKit `$env/static/public`: https://svelte.dev/docs/kit/$env-static-public
- SvelteKit configuration (`csrf.checkOrigin`, `env.publicPrefix`): https://svelte.dev/docs/kit/configuration
- Nuxt runtime config: https://nuxt.com/docs/4.x/guide/going-further/runtime-config
- Nuxt server directory structure: https://nuxt.com/docs/4.x/directory-structure/server
- Vite server options (`server.host`, `server.allowedHosts`): https://vite.dev/config/server-options
- Vite CLI (`vite preview`): https://vite.dev/guide/cli
- Vite resolves an unset `server.host` to `'localhost'` (pinned tag v8.3.1): https://github.com/vitejs/vite/blob/v8.3.1/packages/vite/src/node/utils.ts#L1010-L1016
- SvelteKit adapter-node `host = env('HOST', '0.0.0.0')` and `port = env('PORT', !path && '3000')`, with `path = env('SOCKET_PATH', false)`, where `env()` returns a variable's value whenever it is present, even empty, and the socket-activation branch that listens on the passed descriptor instead (pinned tag @sveltejs/adapter-node@5.5.7): https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/index.js#L10-L12, https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/env.js#L46-L50 and https://github.com/sveltejs/kit/blob/%40sveltejs/adapter-node%405.5.7/packages/adapter-node/src/index.js#L57-L60
- GNU grep `-f -` ("When file is '-', read patterns from standard input"), `-l` ("print the name of each input file from which output would normally have been printed") and its exit status (0 if a line is selected, 1 if none, 2 on error): https://www.gnu.org/software/grep/manual/html_node/Matching-Control.html , https://www.gnu.org/software/grep/manual/html_node/General-Output-Control.html and https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html
