---
version_basis: {
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "2f828a1314a2c7c177fb7fc110019fe7deba2a85aa9f7c3a812d82fdf06be514",
  "components": {
    "node": {
      "name": "Node.js documentation",
      "basis": "unknown",
      "sources": {
        "s87db42190978": "https://nodejs.org/api/https.html",
        "sdb035b84e308": "https://nodejs.org/api/http.html"
      }
    },
    "linux-ip": {
      "name": "Linux ip(7) reference",
      "basis": "unversioned",
      "sources": {
        "s612fed1df1ed": "https://man7.org/linux/man-pages/man7/ip.7.html"
      }
    },
    "linux-capabilities": {
      "name": "Linux capabilities(7) reference",
      "basis": "unversioned",
      "sources": {
        "s3c3a13034c04": "https://man7.org/linux/man-pages/man7/capabilities.7.html"
      }
    },
    "express": {
      "name": "Express proxy documentation",
      "basis": "unknown",
      "sources": {
        "s2acbdbd05858": "https://expressjs.com/en/guide/behind-proxies.html"
      }
    },
    "session": {
      "name": "express-session documentation",
      "basis": "unknown",
      "sources": {
        "safd9f9d15304": "https://expressjs.com/en/resources/middleware/session/"
      }
    },
    "helmet": {
      "name": "Helmet documentation",
      "basis": "unknown",
      "sources": {
        "sc1865315478e": "https://helmet.js.org/"
      }
    },
    "rate": {
      "name": "express-rate-limit minimum",
      "basis": "v8",
      "sources": {
        "s303dcc57a0df": "https://express-rate-limit.mintlify.app/reference/changelog"
      }
    },
    "otplib": {
      "name": "otplib",
      "basis": "v12.0.1",
      "sources": {
        "sdb2cd721be64": "https://github.com/yeojz/otplib/blob/v12.0.1/README.md#L371-L372"
      }
    },
    "qrcode": {
      "name": "qrcode",
      "basis": "v1.5.4",
      "sources": {
        "sc505636608da": "https://github.com/soldair/node-qrcode/blob/v1.5.4/README.md#L125-L129"
      }
    },
    "node-v24": {
      "name": "Node.js API documentation",
      "basis": "v24.22.0",
      "sources": {
        "s670c858d43f0": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/process.md#L1563-L1581",
        "s2f3ecf558ce7": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/crypto.md#L6678-L6717",
        "s7fbb99765dc4": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3568-L3588",
        "sbfee17929443": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3940-L3944",
        "s684a71cf8b6e": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L1786-L1789",
        "sea85e903cce0": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L70-L103",
        "sd0e5679b6277": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L458-L472",
        "sd9044fe58c3e": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L533-L549"
      }
    }
  },
  "claims": {
    "tls": {"text": "Direct HTTPS uses a certificate plus chain and private key on all-interface 443.", "components": ["node"], "sources": ["node:s87db42190978"], "status": "REASONED"},
    "redirect": {"text": "All-interface 80 redirects with 301 to required PUBLIC_HOST; only origin-form request paths are appended.", "components": ["node"], "sources": ["node:sdb035b84e308"], "status": "REASONED"},
    "bind": {"text": "Same-host proxy uses 127.0.0.1; managed ingress uses platform-required addresses and ports with edge TLS and application auth. Platform mappings are cross-guide guidance, not covered by listed Sources.", "components": ["node", "express"], "sources": ["node:s87db42190978", "express:s2acbdbd05858"], "status": "REASONED"},
    "privilege": {"text": "On Linux, binding ports below 1024 requires root with CAP_NET_BIND_SERVICE or a non-root process with that capability in the user namespace governing the network namespace; this guide advises against running the app as root and prefers the proxy layout.", "components": ["node", "linux-ip", "linux-capabilities"], "sources": ["node:s87db42190978", "linux-ip:s612fed1df1ed", "linux-capabilities:s3c3a13034c04"], "status": "REASONED"},
    "proxy": {"text": "Trust loopback or an exact remote proxy address/subnet; true and variable-length hop paths permit forged client IP, host and scheme unless headers are overwritten.", "components": ["express"], "sources": ["express:s2acbdbd05858"], "status": "REASONED"},
    "headers": {"text": "Install helmet() for security headers including HSTS.", "components": ["helmet"], "sources": ["helmet:sc1865315478e"], "status": "REASONED"},
    "password": {"text": "Prefer argon2id for new apps; existing bcrypt systems use hash cost 12 and compare. Password-library APIs are not covered by listed Sources.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "session-secret": {"text": "Load a long random SESSION_SECRET from the environment.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "session-save": {"text": "Set resave=false and saveUninitialized=false.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "cookies": {"text": "Set Secure, HttpOnly, SameSite=lax and an eight-hour cookie maxAge in milliseconds.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "store": {"text": "Default MemoryStore is development-only, leaks memory and cannot scale past one process; supply a production store.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "expiry": {"text": "No cookie maximum age is set by default; set cookie.maxAge.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED"},
    "login-limit": {"text": "Use a 20-request, 15-minute login limit; v8 or newer defaults to IPv6 /56 grouping, closing the v7 rotation bypass; pair IP limits with account controls.", "components": ["rate"], "sources": ["rate:s303dcc57a0df"], "status": "REASONED"},
    "tokens": {"text": "This guide advises loading API keys and tokens from process.env, never from source literals, and comparing self-checked secret values with crypto.timingSafeEqual using equal-byte-length byte inputs; process.env exposes the user environment, while timingSafeEqual's input requirements and surrounding-code limit are documented.", "components": ["node", "node-v24"], "sources": ["node:s87db42190978", "node-v24:s670c858d43f0", "node-v24:s2f3ecf558ce7"], "status": "REASONED"},
    "mfa": {"text": "Use otplib plus qrcode for TOTP enrolment or a fronting identity layer; the fronting identity layer is not covered by listed Sources.", "components": ["session", "otplib", "qrcode"], "sources": ["session:safd9f9d15304", "otplib:sdb2cd721be64", "qrcode:sc505636608da"], "status": "REASONED"},
    "tls-validation": {"text": "This guide advises never setting NODE_TLS_REJECT_UNAUTHORIZED=0 for the Node.js process's TLS connections or rejectUnauthorized=false for a client TLS connection or an HTTPS agent whose requests use it; Node.js documents the TLS validation effects, and the agent reach is this guide's assessment of the documented options flow.", "components": ["node", "node-v24"], "sources": ["node:s87db42190978", "node-v24:sbfee17929443", "node-v24:s684a71cf8b6e", "node-v24:sea85e903cce0", "node-v24:sd0e5679b6277", "node-v24:sd9044fe58c3e"], "status": "REASONED"},
    "client-ca": {"text": "This guide advises setting NODE_EXTRA_CA_CERTS to a PEM file before launching Node.js for an internal CA or self-signed server; it extends well-known roots, is read only at launch, and is ignored when Node.js runs as setuid root or with Linux file capabilities; neither it nor the well-known roots is used by a TLS or HTTPS client or server given an explicit ca option.", "components": ["node", "node-v24"], "sources": ["node:s87db42190978", "node-v24:s7fbb99765dc4"], "status": "REASONED"},
    "verify-redirect": {"text": "HTTP should return 301 with an HTTPS Location.", "components": ["node"], "sources": ["node:sdb035b84e308"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS must succeed without -k and show Helmet headers.", "components": ["node", "helmet"], "sources": ["node:s87db42190978", "helmet:sc1865315478e"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "A real protected route denies anonymous requests with 401/403 and accepts a valid session with 200; either app or fronting auth may enforce the denial.", "components": ["session"], "sources": ["session:safd9f9d15304"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for loopback behind a same-host proxy or the managed platform address and port.", "components": ["node", "express"], "sources": ["node:s87db42190978", "express:s2acbdbd05858"], "status": "REASONED", "verify": [1]},
    "verify-proxy": {"text": "Temporary /whoami must not echo forged X-Forwarded-For; this checks req.ip only and an overwriting proxy can mask excessive trust.", "components": ["express"], "sources": ["express:s2acbdbd05858"], "status": "REASONED", "verify": [1]}
  }
}
---
# Node.js and Express: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-17; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls: Direct HTTPS uses a certificate plus chain and private key on all-interface 443. | Node.js documentation unknown | REASONED |
| redirect: All-interface 80 redirects with 301 to required PUBLIC_HOST; only origin-form request paths are appended. | Node.js documentation unknown | REASONED |
| bind: Same-host proxy uses 127.0.0.1; managed ingress uses platform-required addresses and ports with edge TLS and application auth. Platform mappings are cross-guide guidance, not covered by listed Sources. | Node.js documentation unknown; Express proxy documentation unknown | REASONED |
| privilege: On Linux, binding ports below 1024 requires root with CAP_NET_BIND_SERVICE or a non-root process with that capability in the user namespace governing the network namespace; this guide advises against running the app as root and prefers the proxy layout. | Node.js documentation unknown; Linux ip(7) reference unversioned; Linux capabilities(7) reference unversioned | REASONED |
| proxy: Trust loopback or an exact remote proxy address/subnet; true and variable-length hop paths permit forged client IP, host and scheme unless headers are overwritten. | Express proxy documentation unknown | REASONED |
| headers: Install helmet() for security headers including HSTS. | Helmet documentation unknown | REASONED |
| password: Prefer argon2id for new apps; existing bcrypt systems use hash cost 12 and compare. Password-library APIs are not covered by listed Sources. | express-session documentation unknown | REASONED |
| session-secret: Load a long random SESSION_SECRET from the environment. | express-session documentation unknown | REASONED |
| session-save: Set resave=false and saveUninitialized=false. | express-session documentation unknown | REASONED |
| cookies: Set Secure, HttpOnly, SameSite=lax and an eight-hour cookie maxAge in milliseconds. | express-session documentation unknown | REASONED |
| store: Default MemoryStore is development-only, leaks memory and cannot scale past one process; supply a production store. | express-session documentation unknown | REASONED |
| expiry: No cookie maximum age is set by default; set cookie.maxAge. | express-session documentation unknown | REASONED |
| login-limit: Use a 20-request, 15-minute login limit; v8 or newer defaults to IPv6 /56 grouping, closing the v7 rotation bypass; pair IP limits with account controls. | express-rate-limit minimum v8 | REASONED |
| tokens: This guide advises loading API keys and tokens from process.env, never from source literals, and comparing self-checked secret values with crypto.timingSafeEqual using equal-byte-length byte inputs; process.env exposes the user environment, while timingSafeEqual's input requirements and surrounding-code limit are documented. | Node.js documentation unknown; Node.js API documentation v24.22.0 | REASONED |
| mfa: Use otplib plus qrcode for TOTP enrolment or a fronting identity layer; the fronting identity layer is not covered by listed Sources. | express-session documentation unknown; otplib v12.0.1; qrcode v1.5.4 | REASONED |
| tls-validation: This guide advises never setting NODE_TLS_REJECT_UNAUTHORIZED=0 for the Node.js process's TLS connections or rejectUnauthorized=false for a client TLS connection or an HTTPS agent whose requests use it; Node.js documents the TLS validation effects, and the agent reach is this guide's assessment of the documented options flow. | Node.js documentation unknown; Node.js API documentation v24.22.0 | REASONED |
| client-ca: This guide advises setting NODE_EXTRA_CA_CERTS to a PEM file before launching Node.js for an internal CA or self-signed server; it extends well-known roots, is read only at launch, and is ignored when Node.js runs as setuid root or with Linux file capabilities; neither it nor the well-known roots is used by a TLS or HTTPS client or server given an explicit ca option. | Node.js documentation unknown; Node.js API documentation v24.22.0 | REASONED |
| verify-redirect: HTTP should return 301 with an HTTPS Location. | Node.js documentation unknown | REASONED |
| verify-tls: HTTPS must succeed without -k and show Helmet headers. | Node.js documentation unknown; Helmet documentation unknown | REASONED |
| verify-auth: A real protected route denies anonymous requests with 401/403 and accepts a valid session with 200; either app or fronting auth may enforce the denial. | express-session documentation unknown | REASONED |
| verify-bind: Inspect every listener for loopback behind a same-host proxy or the managed platform address and port. | Node.js documentation unknown; Express proxy documentation unknown | REASONED |
| verify-proxy: Temporary /whoami must not echo forged X-Forwarded-For; this checks req.ip only and an overwriting proxy can mask excessive trust. | Express proxy documentation unknown | REASONED |
<!-- version-basis:end -->

Preferred production layout: bind the Node app to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). On a managed platform the platform terminates TLS at its edge and you bind the address it requires, not `127.0.0.1` ([paas.md](paas.md)). Node can also terminate TLS itself, shown below. Get a certificate per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. HTTPS directly in Node

```js
const https = require('node:https');
const fs = require('node:fs');
const express = require('express');

const app = express();

const options = {
  key:  fs.readFileSync('/etc/ssl/private/server.key'),
  cert: fs.readFileSync('/etc/ssl/certs/server.crt'),   // certificate plus chain
};

https.createServer(options, app).listen(443);

// Port 80 exists only to redirect. Redirect to a FIXED canonical host; never reflect
// req.headers.host, which the client controls (a forged Host, or a cache in front of :80,
// would turn this into an open redirect). Set PUBLIC_HOST to your canonical hostname (no
// scheme or path); the app refuses to start without it rather than emit https://undefined/.
const CANONICAL_HOST = process.env.PUBLIC_HOST;
if (!CANONICAL_HOST) throw new Error('PUBLIC_HOST must be set to the canonical hostname');
require('node:http').createServer((req, res) => {
  // req.url is the raw request target; only an origin-form path is safe to append, so fall
  // back to '/' for absolute-form or asterisk-form (OPTIONS *) targets.
  const path = req.url.startsWith('/') ? req.url : '/';
  res.writeHead(301, { Location: `https://${CANONICAL_HOST}${path}` });
  res.end();
}).listen(80);
```

On Linux, binding ports below 1024 requires root with `CAP_NET_BIND_SERVICE` or a non-root process with that capability in the user namespace governing the network namespace ([ip(7)](https://man7.org/linux/man-pages/man7/ip.7.html), [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)); this guide advises against running the app as root and prefers the proxy layout. The `listen(443)`/`listen(80)` above bind every interface, which is intended only for this Node-terminates-TLS layout. On a managed platform, do not add these listeners: bind the address and port the platform injects (`0.0.0.0` on `$PORT` for Render, Railway, and Heroku Cedar; `::` on `$PORT` for Heroku Fir; `0.0.0.0` matching `internal_port` for Fly) and let the platform terminate TLS at its ingress, so plain HTTP behind that protected ingress is fine and application authentication is still required ([paas.md](paas.md)).

## 2. Behind a proxy: tell Express about it

```js
// The app binds to 127.0.0.1 behind a same-host reverse proxy (see caddy.md / nginx.md),
// so trust only loopback addresses. Never use a blanket `true`.
app.set('trust proxy', 'loopback');

// Remote proxy instead? Trust its exact address or subnet:
// app.set('trust proxy', '10.0.0.5');       // single proxy IP
// app.set('trust proxy', '10.0.0.0/24');    // proxy subnet
```

`trust proxy` controls how Express derives `req.ip`, `req.ips`, `req.hostname`/`req.host` (from `X-Forwarded-Host`), and `req.protocol`/`req.secure` (from `X-Forwarded-Proto`), so a forged header can fake the client IP (defeating rate limits and logging), the hostname, or the HTTPS status. Never set it to `true`: that trusts the leftmost `X-Forwarded-For` entry, which the client controls, so clients can forge all of these values unless the last trusted proxy strips or overwrites them. A hop count such as `1` is safe only if every path to the app crosses exactly that many proxies; if a shorter path exists, a client sitting fewer hops away can forge the same headers. Whichever value you use, configure the proxy itself to overwrite inbound `X-Forwarded-*` headers rather than pass them through.

Security headers, including Strict-Transport-Security, via helmet:

```js
const helmet = require('helmet');
app.use(helmet());
```

## 3. Authentication

Follow [authentication.md](authentication.md). The pieces most Node projects need:

Password hashing: prefer `argon2id` (the `argon2` package) for new applications; the `bcrypt` example below is acceptable and is the right choice for existing bcrypt systems, per [authentication.md](authentication.md):

```js
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(password, 12);
const ok   = await bcrypt.compare(password, hash);
```

Sessions with hardened cookies (express-session):

```js
const session = require('express-session');
app.use(session({
  secret: process.env.SESSION_SECRET,      // long random value from the environment
  resave: false,
  saveUninitialized: false,
  // store: a production session store (see below); the default MemoryStore is for development only
  cookie: { secure: true, httpOnly: true, sameSite: 'lax', maxAge: 8 * 60 * 60 * 1000 },   // milliseconds
}));
```

Express says the default `MemoryStore` is not designed for production (it leaks memory and does not scale past one process): pass `store:` a production store such as [connect-redis](https://www.npmjs.com/package/connect-redis) or [connect-pg-simple](https://www.npmjs.com/package/connect-pg-simple), and set `cookie.maxAge` so sessions expire, since no maximum age is set by default.

Rate-limit the login route with a current express-rate-limit (v8 or newer masks each IPv6 client to a `/56` subnet by default, closing a v7 bypass where a client rotated addresses within its own IPv6 allocation). An IP limit alone does not stop credential-stuffing from many addresses, so pair it with per-account controls ([authentication.md](authentication.md)):

```js
const rateLimit = require('express-rate-limit');
app.use('/login', rateLimit({ windowMs: 15 * 60 * 1000, limit: 20 }));
```

This guide advises: load API keys and tokens from `process.env`, never from literals in the source. Generate them per [authentication.md](authentication.md). Where you check them yourself, compare equal-byte-length byte inputs with `crypto.timingSafeEqual`; it accepts `ArrayBuffer`, `Buffer`, `TypedArray` or `DataView` inputs, throws on different byte lengths, and does not make surrounding code timing-safe. The use of `process.env` for secrets and the ban on source literals are this guide's advice; Node.js documents `process.env` as the user environment and the comparison API's input requirements.

MFA: add TOTP with [otplib](https://github.com/yeojz/otplib) plus the [qrcode](https://www.npmjs.com/package/qrcode) package for enrolment QR codes, or front the app with an identity layer; requirements and options in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

- This guide advises: never set `NODE_TLS_REJECT_UNAUTHORIZED=0`, which disables certificate validation for TLS connections in the Node.js process, and never pass `rejectUnauthorized: false`, which disables server-certificate verification for that client connection. Never configure an `https.Agent` with `rejectUnauthorized: false`: requests using that agent inherit its TLS option. The agent reach is this guide's assessment of Node.js's documented request, agent and TLS options.
- For an internal CA or self-signed server, this guide advises instead: set `NODE_EXTRA_CA_CERTS=/path/ca.crt` before starting Node.js, pointing at a PEM file of trusted certificates (see [self-signed.md](self-signed.md)). Node.js adds these to its well-known root CAs at launch; changing the variable at runtime has no effect on the current process. An explicit `ca` option prevents use of both the well-known and extra CAs for that TLS or HTTPS client or server, and Node.js ignores the variable when run as setuid root or with Linux file capabilities.

## 5. Verify (REASONED: TLS, headers, authentication, listener and proxy-header expectations follow the Sources below and linked deployment guidance; no deployment run or outcome is recorded in this guide. This metadata-only review has no deployed Node application, proxy or managed ingress to test.)

```bash
curl -q -g -sI --noproxy '*' http://example.com/    # expect 301 with an https:// Location
curl -q -g -sI --noproxy '*' https://example.com/   # succeeds without -k; shows helmet's headers

# Auth: probe a REAL protected route (not a placeholder like /api, which often 404s), show the
# status, and disable client proxies so a denial is attributable. A denial from ANY layer (the app,
# or a proxy/Access in front) is the pass; the positive control proves auth actually gates rather
# than the route being broken for everyone.
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' 'https://example.com/REPLACE_WITH_PROTECTED_PATH'
                                     # expect 401 or 403 with no credentials
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' \
  -b REPLACE_WITH_SESSION_COOKIE_FILE 'https://example.com/REPLACE_WITH_PROTECTED_PATH'
                                     # expect 200 with a valid session (cookie read from a file, not argv;
                                     # for a bearer-token route use -H @REPLACE_WITH_AUTH_HEADER_FILE instead of -b)

ss -tlnp   # read every listener; a same-host proxy layout binds 127.0.0.1 only, on managed
           # ingress the platform's required address and port from section 1
# trust proxy: add a temporary route that echoes req.ip, then remove it after this check
#   app.get('/whoami', (req, res) => res.send(req.ip))
curl -q -g -sS --noproxy '*' -H 'X-Forwarded-For: 203.0.113.9' https://example.com/whoami
                                     # req.ip must be your real client IP, never 203.0.113.9: echoing the
                                     # forged value means `trust proxy` is too broad and trusts a
                                     # client-set header. This checks req.ip scoping only, not that the
                                     # proxy strips headers, and does not cover X-Forwarded-Host or -Proto.
                                     # An overwriting proxy can also mask a too-broad setting, so a clean
                                     # result here does not prove the trust boundary by itself
```

## Sources (checked September 2026)

- Node.js HTTPS module: https://nodejs.org/api/https.html
- Express behind proxies: https://expressjs.com/en/guide/behind-proxies.html
- express-session (MemoryStore warning, cookie.maxAge, compatible stores): https://expressjs.com/en/resources/middleware/session/
- helmet: https://helmet.js.org/
- express-rate-limit changelog (v8 masks IPv6 clients to a `/56` subnet by default, closing the v7 subnet-rotation bypass; the `limit` option name): https://express-rate-limit.mintlify.app/reference/changelog
- Node HTTP `message.url` and the caution to validate a client-supplied `Host` header: https://nodejs.org/api/http.html
- otplib TOTP enrolment and QR-code generation (v12.0.1, checked October 2026): https://github.com/yeojz/otplib/blob/v12.0.1/README.md#L371-L372
- qrcode enrolment image generation (v1.5.4, checked October 2026): https://github.com/soldair/node-qrcode/blob/v1.5.4/README.md#L125-L129
- Node.js `process.env` (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/process.md#L1563-L1581
- Node.js `crypto.timingSafeEqual` (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/crypto.md#L6678-L6717
- Node.js `NODE_EXTRA_CA_CERTS` (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3568-L3588
- Node.js `NODE_TLS_REJECT_UNAUTHORIZED` (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3940-L3944
- Node.js `tls.connect` client `rejectUnauthorized` (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L1786-L1789
- Node.js `https.Agent` options (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L70-L103
- Node.js `https.request` TLS options (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L458-L472
- Node.js HTTPS agent example (v24.22.0, checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/https.md#L533-L549
- Linux ip(7) privileged-port rule (unversioned, checked October 2026): https://man7.org/linux/man-pages/man7/ip.7.html
- Linux capabilities(7) CAP_NET_BIND_SERVICE definition (unversioned, checked October 2026): https://man7.org/linux/man-pages/man7/capabilities.7.html
