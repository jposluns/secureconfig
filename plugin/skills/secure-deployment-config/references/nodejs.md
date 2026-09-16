# Node.js and Express: TLS and authentication

Preferred production layout: bind the Node app to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). Node can also terminate TLS itself, shown below. Get a certificate per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

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

// Port 80 exists only to redirect
require('node:http').createServer((req, res) => {
  res.writeHead(301, { Location: `https://${req.headers.host}${req.url}` });
  res.end();
}).listen(80);
```

Binding ports below 1024 needs root or `CAP_NET_BIND_SERVICE`; running the app as root is a bad trade, which is one more reason to prefer the proxy layout.

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

Password hashing (bcrypt; the `argon2` package is the equivalent alternative):

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

Rate-limit the login route (express-rate-limit v7):

```js
const rateLimit = require('express-rate-limit');
app.use('/login', rateLimit({ windowMs: 15 * 60 * 1000, limit: 20 }));
```

API keys and tokens come from `process.env`, never from literals in the source. Generate them per [authentication.md](authentication.md) and compare with `crypto.timingSafeEqual` where you check them yourself.

MFA: add TOTP with [otplib](https://github.com/yeojz/otplib) plus the [qrcode](https://www.npmjs.com/package/qrcode) package for enrolment QR codes, or front the app with an identity layer; requirements and options in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

- Never set `NODE_TLS_REJECT_UNAUTHORIZED=0` and never pass `rejectUnauthorized: false`; both disable certificate validation for every connection.
- For an internal CA or self-signed server, point Node at the CA instead: `NODE_EXTRA_CA_CERTS=/path/ca.crt` (see [self-signed.md](self-signed.md)).

## 5. Verify

```bash
curl -q -sI http://example.com/         # expect 301 with a https:// Location
curl -q -sI https://example.com/        # succeeds without -k; shows helmet's headers
curl -q -s  https://example.com/api     # expect 401/403 without credentials
ss -tlnp   # read every listener; node: behind a proxy: bound to 127.0.0.1 only
# trust proxy: add a temporary route that echoes req.ip, then remove it after this check
#   app.get('/whoami', (req, res) => res.send(req.ip))
curl -q -s -H 'X-Forwarded-For: 203.0.113.9' https://example.com/whoami
                                     # req.ip must be your real client IP, never 203.0.113.9: echoing the
                                     # forged value means `trust proxy` is too broad and trusts a
                                     # client-set header. This checks req.ip scoping only, not that the
                                     # proxy strips headers, and does not cover X-Forwarded-Host or -Proto
```

## Sources (checked September 2026)

- Node.js HTTPS module: https://nodejs.org/api/https.html
- Express behind proxies: https://expressjs.com/en/guide/behind-proxies.html
- express-session (MemoryStore warning, cookie.maxAge, compatible stores): https://expressjs.com/en/resources/middleware/session/
- helmet: https://helmet.js.org/
