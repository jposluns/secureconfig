# Node.js and Express: TLS and authentication

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

Binding ports below 1024 needs root or `CAP_NET_BIND_SERVICE`; running the app as root is a bad trade, which is one more reason to prefer the proxy layout. The `listen(443)`/`listen(80)` above bind every interface, which is intended only for this Node-terminates-TLS layout. On a managed platform, do not add these listeners: bind the address and port the platform injects (`0.0.0.0` on `$PORT` for Render, Railway, and Heroku Cedar; `::` on `$PORT` for Heroku Fir; `0.0.0.0` matching `internal_port` for Fly) and let the platform terminate TLS at its ingress, so plain HTTP behind that protected ingress is fine and application authentication is still required ([paas.md](paas.md)).

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

API keys and tokens come from `process.env`, never from literals in the source. Generate them per [authentication.md](authentication.md) and compare with `crypto.timingSafeEqual` where you check them yourself.

MFA: add TOTP with [otplib](https://github.com/yeojz/otplib) plus the [qrcode](https://www.npmjs.com/package/qrcode) package for enrolment QR codes, or front the app with an identity layer; requirements and options in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

- Never set `NODE_TLS_REJECT_UNAUTHORIZED=0`, which disables certificate validation process-wide, and never pass `rejectUnauthorized: false`, which disables it for that connection and any connection sharing an agent configured with it.
- For an internal CA or self-signed server, point Node at the CA instead: `NODE_EXTRA_CA_CERTS=/path/ca.crt` (see [self-signed.md](self-signed.md)).

## 5. Verify

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
