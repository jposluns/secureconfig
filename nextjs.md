# Next.js: authentication that actually gates Route Handlers, Server Actions, and data

A Next.js app has many entry points: pages, layouts, Route Handlers (`app/**/route.ts`), and every exported Server Action, which the Next.js docs describe as reachable by a direct POST whether or not your UI calls it. A check that lives only in a layout or in `proxy.ts` (the file Next.js 16 renamed from `middleware.ts`) leaves open the entry points it does not cover (a layout guards no Route Handler or Server Action; a `proxy.ts` matcher guards only the paths it matches), and authorization still belongs next to the data. Next.js supplies cookies and sessions as primitives, not a login system; the login is yours or a library's.

## 1. Bind privately; TLS comes from the platform or the proxy

On Vercel and similar platforms the platform terminates TLS; nothing to configure ([paas.md](paas.md)). Self-hosted, `next start` listens on every interface on port 3000 by default (as of v16.3.6 its `--port` defaults to 3000 and it passes no hostname to Node's `listen`, which binds `::` where IPv6 is available and `0.0.0.0` otherwise; its `-H` option's help text still says `(default: 0.0.0.0)`); bind to loopback and put a reverse proxy in front, which the Next.js self-hosting guide itself recommends, with TLS and headers per [nodejs.md](nodejs.md), [nginx.md](nginx.md), or [caddy.md](caddy.md).

```bash
next build && next start -H 127.0.0.1 -p 3000    # or PORT=3000; PORT cannot be set in .env
```

## 2. Put the check where the data is

The Next.js authentication guide's rule: create a Data Access Layer (DAL) with a `verifySession()` function and call it from every data request, Server Action, and Route Handler. Its reasons, paraphrased from the authentication and data-security guides:

- Layouts do not re-render on client navigation, so a session check there does not run on every route change, and a layout that returns `null` does not stop nested segments or Server Actions from running.
- Server Actions and Route Handlers get "the same security considerations as public-facing API endpoints"; a page-level check "does not extend to the Server Actions defined within it".
- Proxy "should not be your only line of defense": use it for optimistic redirects that read the cookie only, never database lookups. A `matcher` change can silently remove Proxy coverage from a Server Action.

```ts
// app/lib/dal.ts
import 'server-only'
import { cache } from 'react'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { decrypt } from '@/app/lib/session'

export const verifySession = cache(async () => {
  const session = await decrypt((await cookies()).get('session')?.value)
  if (!session?.userId) redirect('/login')
  return { isAuth: true, userId: session.userId, role: session.role }
})

// app/api/admin/route.ts: the handler checks for itself (return 401 here instead of redirecting if you prefer)
export async function GET() {
  const session = await verifySession()
  if (session.role !== 'admin') return new Response(null, { status: 403 })
}

// app/actions.ts: so does every Server Action; the page that renders the form does not count
'use server'
export async function deleteRecord(formData: FormData) {
  const session = await verifySession()
  if (session.role !== 'admin') return null
}
```

Also check ownership of the specific resource inside the DAL (authorization, not only authentication), and return only the fields the client needs. The snippets above are fragments: `session.role` must come from your trusted user store (not from the cookie alone for sensitive checks), and each handler still returns its real success response, so wire in your own imports and data calls.

## 3. Sessions: signed payload, hardened cookie

```bash
openssl rand -base64 32      # SESSION_SECRET, set in the environment; never with a NEXT_PUBLIC_ prefix
```

```ts
// app/lib/session.ts (the guide's stateless session, using jose)
import 'server-only'
import { SignJWT, jwtVerify } from 'jose'
import { cookies } from 'next/headers'
const key = new TextEncoder().encode(process.env.SESSION_SECRET)

export async function createSession(userId: string, role: string) {
  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
  const session = await new SignJWT({ userId, role, expiresAt })
    .setProtectedHeader({ alg: 'HS256' }).setIssuedAt().setExpirationTime('7d').sign(key)
  ;(await cookies()).set('session', session, { httpOnly: true, secure: true, expires: expiresAt, sameSite: 'lax', path: '/' })
}
```

`decrypt()` is `jwtVerify(session, key, { algorithms: ['HS256'] })`, returning the payload or `undefined`. Cookies can only be set or deleted in a Server Function or Route Handler; logout is `(await cookies()).delete('session')`. Keep the payload to the user ID and role, no PII. For sensitive operations the guide recommends database sessions verified against the store, not the cookie alone.

## 4. Keep secrets out of the client bundle

- `NEXT_PUBLIC_*` variables are inlined into the JavaScript sent to the browser at `next build`; every other variable is server-only BY DEFAULT, but a variable placed in `next.config.js`'s `env` key is also inlined into the client bundle regardless of prefix, so never put a secret there. A secret with a `NEXT_PUBLIC_` prefix is published to every visitor ([secrets.md](secrets.md)). Only the DAL should read `process.env`; `.env*` files stay in `.gitignore`.
- More than one self-hosted instance: set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` (base64, 16, 24, or 32 decoded bytes) at build so all instances share the Server Action closure key. The docs say not to rely on that encryption to hide secrets.
- Server Actions abort when `Origin` does not match `Host` (or `X-Forwarded-Host`). Behind a proxy whose host differs from the public domain, list the public origins in `experimental.serverActions.allowedOrigins` in `next.config.js`.

## 5. Libraries

**Auth.js** (https://authjs.dev/): `AUTH_SECRET` is the one mandatory variable; `npx auth secret` writes it to `.env.local`.

```ts
// auth.ts
import NextAuth from "next-auth"
export const { handlers, signIn, signOut, auth } = NextAuth({ providers: [] })
// app/api/auth/[...nextauth]/route.ts
import { handlers } from "@/auth"
export const { GET, POST } = handlers
```

Providers are configured from `AUTH_<PROVIDER>_ID`, `AUTH_<PROVIDER>_SECRET`, and for OIDC `AUTH_<PROVIDER>_ISSUER`; provider setup and the allowlist check are in [oidc-integration.md](oidc-integration.md) and [identity-providers.md](identity-providers.md). Behind a reverse proxy set `AUTH_TRUST_HOST=true` (automatic on Vercel). Server code calls `const session = await auth()`. Wrapping a Route Handler with `auth(...)` only fills in `req.auth`; nothing refuses the request for you, so the handler must check the session, then authorize, then touch data:

```ts
// app/api/notes/route.ts
import { NextResponse } from "next/server"
import { auth } from "@/auth"
// isAllowed and loadNotes are your app's own functions
export const GET = auth(async function GET(req) {
  if (!req.auth) return NextResponse.json({ message: "Not authenticated" }, { status: 401 })  // no automatic 401
  if (!isAllowed(req.auth.user)) return NextResponse.json({ message: "Forbidden" }, { status: 403 })  // your allowlist
  return NextResponse.json(await loadNotes(req.auth.user))
})
```

`export { auth as proxy }` in `proxy.ts` is the optimistic layer, but with an empty `providers` and no `callbacks.authorized` it authorizes every request by default, so add an `authorized` callback (or a redirecting wrapper) if you use it to gate; Auth.js says not to rely on it exclusively regardless. MFA is not part of this configuration; enforce it at the identity provider ([mfa.md](mfa.md)).

**Better Auth** (https://better-auth.com/docs/introduction): `BETTER_AUTH_SECRET` (32+ characters, `openssl rand -base64 32`) and `BETTER_AUTH_URL`; the placeholder default secret throws in production.

```ts
// lib/auth.ts
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"
import { twoFactor } from "better-auth/plugins"
export const auth = betterAuth({
  baseURL: "https://app.example.com",             // set explicitly; the docs advise against request inference
  trustedOrigins: ["https://app.example.com"],    // scoped origin/CSRF + callbackURL validation; the general check skips GET/HEAD/OPTIONS (some endpoints still validate callbackURL on GET); NOT an app-route gate, so keep authn+authz per route
  emailAndPassword: { enabled: true },            // default false
  plugins: [twoFactor(), nextCookies()],          // nextCookies lets Server Actions set the session cookie
})
// app/api/auth/[...all]/route.ts
import { toNextJsHandler } from "better-auth/next-js"
export const { GET, POST } = toNextJsHandler(auth)
```

Server-side check: assign and REJECT - `const session = await auth.api.getSession({ headers: await headers() })`, then reject before authorizing. The rejection differs by surface: a Route Handler returns `new Response(null, { status: 401 })`; a Server Component redirects or throws; a Server Action redirects, throws, or returns a serializable error, since a `Response` is not a valid Server Component render result or Server Action return value. Do this in Route Handlers, Server Actions, and Server Components; calling `getSession` and discarding its result gates nothing. `getSessionCookie(request)` in `proxy.ts` only proves a cookie exists; Better Auth says to check in each page and route. `twoFactor()` makes TOTP (default), emailed or SMS OTP, and backup codes AVAILABLE, not enrolled or enforced: users must enroll, emailed or SMS OTP additionally needs `otpOptions.sendOTP`, and requiring 2FA for an operation is a separate check. Add `twoFactorClient()` from `better-auth/client/plugins` on the client and run the schema migration the plugin page documents before enabling it.

## 6. Vercel: Deployment Protection is not user authentication

Deployment Protection controls who can open a deployment URL: Vercel Authentication admits Vercel users with access to the project; Passport, Password Protection, and Trusted IPs are Enterprise or paid add-on options. Standard Protection covers previews and generated URLs but not production domains; selecting the All Deployments scope for Vercel Authentication extends it to production, and Vercel's changelog of 9 September 2026 makes that free on every plan including Hobby, where protecting production previously required a paid Advanced Deployment Protection add-on (at the time of writing). Availability is not activation: the production domain stays public until All Deployments is configured. It gates your team's previews; your users are not Vercel users, so production still needs section 2 ([paas.md](paas.md)).

## Verify

```bash
ss -tlnp   # read every listener; 3000 on 127.0.0.1 only when self-hosted. ss shows the BIND, not the
           # firewall or the platform ingress, so confirm external reachability separately
# Protected routes WITHOUT a cookie. This guide's verifySession() redirects to /login, so an unauthenticated
# Route Handler or page returns a 3xx to /login (or 401/403 if you chose the "return 401" variant); a
# streamed redirect can instead be a 200 whose body is a client-side redirect shell, not the protected content, so read the BODY, not the status
# alone. --noproxy so no client proxy answers. Save each body and confirm it carries NO protected payload:
curl -q -sS --noproxy '*' -o admin-nocookie.txt -w 'http=%{http_code} loc=%{redirect_url}\n' https://app.example.com/api/admin   # 3xx to /login, or 401/403; admin-nocookie.txt must hold no admin data
curl -q -sS --noproxy '*' -o dash-nocookie.txt  -w 'http=%{http_code} loc=%{redirect_url}\n' https://app.example.com/dashboard    # 3xx with loc=/login, or a 200 redirect shell; dash-nocookie.txt must NOT contain dashboard content (a streamed redirect saves a shell, not the login page)
# POSITIVE controls, so a denial above is the auth check firing and not a route broken for everyone. Put the
# cookie's NAME on the set -- line - this guide's example uses `session`, Better Auth uses
# `better-auth.session_token` (or `__Secure-better-auth.session_token` with secure cookies) - and paste a
# real, freshly issued cookie VALUE at each hidden prompt. Test the admin route with an admin AND a non-admin
# cookie (authorization, not only authentication), and confirm each success body is the real protected
# content, not a login page. Each cookie reaches curl on stdin (--header @-), never argv; that closes the argv
# channel only, not shell history, tracing, or your own account's view of the process. Paste this subshell by
# itself: without bracketed paste, lines pasted after its closing ) are read as the cookies instead.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'session'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value; not probing'; exit 2; }
  case "$1" in
    ''|*[!abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-]*) echo 'the set -- line takes the cookie NAME only (letters, digits, . _ -); not probing'; exit 2 ;;
  esac
  { unset -n cookie_value && unset -v cookie_value; } 2>/dev/null ||
    { echo 'cannot initialize cookie input; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'ADMIN session cookie VALUE (input hidden), then Enter: ' cookie_value < /dev/tty || exit 2
  printf '\n'
  case "$cookie_value" in
    ''|*[[:cntrl:]]*) echo 'a valid admin session cookie value is required; not probing'; exit 2 ;;
  esac
  printf 'Cookie: %s=%s\n' "$1" "$cookie_value" |
    curl -q -sS --noproxy '*' -o dash-auth.txt  -w 'http=%{http_code}\n' --header @- https://app.example.com/dashboard   # expect 200; dash-auth.txt is the dashboard, not /login
  printf 'Cookie: %s=%s\n' "$1" "$cookie_value" |
    curl -q -sS --noproxy '*' -o admin-auth.txt -w 'http=%{http_code}\n' --header @- https://app.example.com/api/admin    # admin cookie: 200
  IFS= read -r -s -p 'NON-ADMIN session cookie VALUE (input hidden), then Enter: ' cookie_value < /dev/tty || exit 2
  printf '\n'
  case "$cookie_value" in
    ''|*[[:cntrl:]]*) echo 'a valid non-admin session cookie value is required; not probing'; exit 2 ;;
  esac
  printf 'Cookie: %s=%s\n' "$1" "$cookie_value" |
    curl -q -sS --noproxy '*' -o admin-nonadmin.txt -w 'http=%{http_code} loc=%{redirect_url}\n' --header @- https://app.example.com/api/admin   # a non-admin cookie here must be 403 or a /login redirect, and admin-nonadmin.txt must hold no admin data; this means nothing unless the admin run got 200
)
# Secret scan of the client bundle: search the FULL secret (not a prefix), require the build to exist, and
# read grep's exit status separately (run inline under set -e, a clean grep's exit 1 would abort the block).
# Paste the session-signing secret at the hidden prompt; it reaches grep on stdin (-f - reads the patterns
# from stdin), never argv, with the same limits as above. Paste this subshell by itself too: without
# bracketed paste, a line pasted after its closing ) is searched for instead, and its clean result then means nothing.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n session_secret && unset -v session_secret; } 2>/dev/null ||
    { echo 'cannot initialize secret input; not scanning'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not scanning'; exit 2; }
  [ -d .next/static ] || { echo 'inconclusive: run next build first'; exit 2; }
  IFS= read -r -s -p 'SESSION_SECRET value (input hidden), then Enter: ' session_secret < /dev/tty || exit 2
  printf '\n'
  case "$session_secret" in
    ''|*[[:cntrl:]]*) echo 'inconclusive: the full secret is required; not scanning'; exit 2 ;;
  esac
  if printf '%s\n' "$session_secret" | grep -rIlF -f - -- .next/static; then rc=0; else rc=$?; fi
  case "$rc" in
    0) echo "FINDING: the secret is in the browser bundle" ;;
    1) echo "clean: secret not found in the bundle" ;;
    *) echo "error: grep exited $rc, result inconclusive" ;;
  esac
)
# a clean grep is evidence not proof (a bundler can split or encode a value); scan for your other secrets too.
# Server Action authorization: create a FRESH disposable record before EACH attempt (an authorized mutation
# changes the precondition - after a delete, a replay would 'not find' the record and look refused when it
# was merely gone). 1) authorized: run it and confirm the store changed (positive control). 2) recreate the
# record, replay the SAME request with no cookie, then as an unauthorized user - each must be refused by an
# authorization error (not not-found) with NO change to the store (check the store directly, not the UI).
```

## Common mistakes

- Checking the session in `app/layout.tsx` or `proxy.ts` only; a Server Action or `route.ts` outside its matcher coverage is still open.
- A Proxy `matcher` that excludes `/api`, with nothing in the Route Handlers themselves.
- Naming a secret `NEXT_PUBLIC_*`, or treating Vercel Authentication as production login.

## Sources (checked September 2026)

- Next.js authentication guide: https://nextjs.org/docs/app/guides/authentication ; data security guide: https://nextjs.org/docs/app/guides/data-security
- Next.js `proxy.js`: https://nextjs.org/docs/app/api-reference/file-conventions/proxy ; `route.js`: https://nextjs.org/docs/app/api-reference/file-conventions/route ; `cookies`: https://nextjs.org/docs/app/api-reference/functions/cookies
- Next.js environment variables: https://nextjs.org/docs/app/guides/environment-variables ; CLI (`next start` defaults): https://nextjs.org/docs/app/api-reference/cli/next ; self-hosting: https://nextjs.org/docs/app/guides/self-hosting
- Auth.js protecting resources (Route Handler `req.auth` check): https://authjs.dev/getting-started/session-management/protecting
- Auth.js installation: https://authjs.dev/getting-started/installation ; deployment (`AUTH_SECRET`, `AUTH_TRUST_HOST`, provider variables): https://authjs.dev/getting-started/deployment ; protecting resources: https://authjs.dev/getting-started/session-management/protecting
- Better Auth introduction: https://better-auth.com/docs/introduction ; installation: https://better-auth.com/docs/installation ; options: https://better-auth.com/docs/reference/options ; Next.js integration: https://better-auth.com/docs/integrations/next ; two-factor plugin: https://better-auth.com/docs/plugins/2fa
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Vercel changelog, protect production deployments for free on every plan (9 September 2026): https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan
- Next.js `next start` declares `-H, --hostname` with help text only and no default value, unlike `--port`'s `.default(3000)` just above it, both under `.command('start')` (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/src/bin/next.ts#L436-L458
- Next.js `next start` copies `options.hostname` into `hostname` unchanged (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/src/cli/next-start.ts#L44
- Next.js `next start` passes that `hostname` to `startServer({ ... hostname, ... })` (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/src/cli/next-start.ts#L84-L87
- Next.js `startServer` destructures `hostname` from `serverOptions` with no default (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/src/server/lib/start-server.ts#L187-L196
- Next.js calls `server.listen(port, hostname)` (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/src/server/lib/start-server.ts#L309
- Node.js `server.listen()` without a host binds the unspecified IPv6 address `::` when available, otherwise `0.0.0.0`: https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md
- Commander 12.1.0 (the version Next.js v16.3.6 pins): an option that takes a value is `undefined` unless specified on the command line: https://github.com/tj/commander.js/blob/v12.1.0/Readme.md#L203-L205
- Next.js v16.3.6 pins `commander` at `12.1.0` (pinned tag v16.3.6): https://github.com/vercel/next.js/blob/v16.3.6/packages/next/package.json#L246
- curl `--header @-` (header lines read from stdin): https://curl.se/docs/manpage.html#-H ; GNU grep `-f -` ("When file is '-', read patterns from standard input"), `-l` ("print the name of each input file from which output would normally have been printed") and its exit status (0 if a line is selected, 1 if none, 2 on error): https://www.gnu.org/software/grep/manual/html_node/Matching-Control.html , https://www.gnu.org/software/grep/manual/html_node/General-Output-Control.html and https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html
