---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "1ab4078e43ca8a5f60f429011121b3a68578a9252ac5d688dfbcd65f7b1ad6cd",
  "components": {
    "protocol": {
      "name": "MDN CORS documentation",
      "basis": "unknown",
      "sources": {
        "s6265cf028385": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS"
      }
    },
    "express": {
      "name": "Express cors middleware",
      "basis": "unknown",
      "sources": {
        "sb6448b9a443d": "https://expressjs.com/en/resources/middleware/cors/"
      }
    },
    "fastapi": {
      "name": "FastAPI CORSMiddleware",
      "basis": "unknown",
      "sources": {
        "s4f1cea92e7bc": "https://fastapi.tiangolo.com/tutorial/cors/"
      }
    },
    "fetch": {
      "name": "Fetch Standard credentials",
      "basis": "unknown",
      "sources": {
        "s028c38ebd452": "https://fetch.spec.whatwg.org/#credentials"
      }
    }
  },
  "claims": {
    "exact-origins": {"text": "Allow exact browser origins, illustrated by Access-Control-Allow-Origin: https://app.example.com; keep environment-specific lists in configuration instead of production localhost entries.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "wildcard-credentials": {"text": "Browsers refuse wildcard Access-Control-Allow-Origin with credentials; the guide restricts wildcard use to public, unauthenticated, read-only resources.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "origin-reflection": {"text": "Reflect only origins checked against an explicit allowlist; reflecting arbitrary Origin values permits hostile sites to read credentialed responses.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "authentication": {"text": "CORS controls browsers rather than curl or other attackers, does not expose a port and does not replace endpoint authentication.", "components": ["protocol", "express"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d"], "status": "REASONED"},
    "express-origins": {"text": "Express cors uses origin: ['https://app.example.com'] as the allowed origin list.", "components": ["express"], "sources": ["express:sb6448b9a443d"], "status": "REASONED"},
    "express-credentials": {"text": "The Express example enables credentials with credentials: true.", "components": ["express"], "sources": ["express:sb6448b9a443d"], "status": "REASONED"},
    "fastapi-origins": {"text": "FastAPI adds CORSMiddleware with allow_origins restricted to https://app.example.com.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-credentials": {"text": "The FastAPI example enables allow_credentials=True.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-methods": {"text": "The FastAPI example allows only GET and POST through allow_methods.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-headers": {"text": "The FastAPI example allows Authorization and Content-Type through allow_headers.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "verify-hostile": {"text": "The exposed API echoes https://evil.example in Access-Control-Allow-Origin; the fixed API omits that hostile origin. No deployed API or browser run is recorded.", "components": ["protocol", "express", "fastapi", "fetch"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc", "fetch:s028c38ebd452"], "status": "REASONED", "verify": [1]},
    "verify-allowed": {"text": "The allowed-Origin probe should return the listed app origin, with Allow-Credentials only where the browser must send cookies, HTTP authentication or TLS client certificates; no actual response is recorded.", "components": ["protocol", "express", "fastapi", "fetch"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc", "fetch:s028c38ebd452"], "status": "REASONED", "verify": [1]},
    "credential-types": {"text": "Browser credentials include cookies, HTTP authentication and TLS client certificates; Access-Control-Allow-Credentials: true is needed only where the browser must send credentials.", "components": ["fetch", "protocol"], "sources": ["fetch:s028c38ebd452", "protocol:s6265cf028385"], "status": "REASONED"}
  }
}
---
# CORS: allow your origins, not everyone's

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- protocol: MDN CORS documentation (unknown)
- express: Express cors middleware (unknown)
- fastapi: FastAPI CORSMiddleware (unknown)
- fetch: Fetch Standard credentials (unknown)

Claims (full source mapping in the front matter):

- exact-origins (REASONED; protocol): Allow exact browser origins, illustrated by Access-Control-Allow-Origin: https://app.example.com; keep environment-specific lists in configuration instead of production localhost entries.
- wildcard-credentials (REASONED; protocol): Browsers refuse wildcard Access-Control-Allow-Origin with credentials; the guide restricts wildcard use to public, unauthenticated, read-only resources.
- origin-reflection (REASONED; protocol): Reflect only origins checked against an explicit allowlist; reflecting arbitrary Origin values permits hostile sites to read credentialed responses.
- authentication (REASONED; protocol, express): CORS controls browsers rather than curl or other attackers, does not expose a port and does not replace endpoint authentication.
- express-origins (REASONED; express): Express cors uses origin: ['https://app.example.com'] as the allowed origin list.
- express-credentials (REASONED; express): The Express example enables credentials with credentials: true.
- fastapi-origins (REASONED; fastapi): FastAPI adds CORSMiddleware with allow_origins restricted to https://app.example.com.
- fastapi-credentials (REASONED; fastapi): The FastAPI example enables allow_credentials=True.
- fastapi-methods (REASONED; fastapi): The FastAPI example allows only GET and POST through allow_methods.
- fastapi-headers (REASONED; fastapi): The FastAPI example allows Authorization and Content-Type through allow_headers.
- verify-hostile (REASONED; protocol, express, fastapi, fetch): The exposed API echoes https://evil.example in Access-Control-Allow-Origin; the fixed API omits that hostile origin. No deployed API or browser run is recorded.
- verify-allowed (REASONED; protocol, express, fastapi, fetch): The allowed-Origin probe should return the listed app origin, with Allow-Credentials only where the browser must send cookies, HTTP authentication or TLS client certificates; no actual response is recorded.
- credential-types (REASONED; fetch, protocol): Browser credentials include cookies, HTTP authentication and TLS client certificates; Access-Control-Allow-Credentials: true is needed only where the browser must send credentials.
<!-- version-basis:end -->

CORS misconfiguration does not expose a port; it lets hostile websites use your users' browsers, cookies included, against your API. AI assistants reach for `Access-Control-Allow-Origin: *` the moment a browser console shows a CORS error; that is the wrong fix for any API that authenticates.

## Rules

1. **List exact origins.** `Access-Control-Allow-Origin` names the site(s) allowed to call the API from a browser:
   ```
   Access-Control-Allow-Origin: https://app.example.com
   ```
2. **Never combine `*` with credentials.** Browsers refuse `Access-Control-Allow-Origin: *` together with `Access-Control-Allow-Credentials: true`; configurations that "fix" this by reflecting whatever `Origin` header arrives recreate `*` for credentialed requests, which is worse. Reflect only origins checked against an explicit allow list.
3. **`*` is acceptable** only for genuinely public, unauthenticated, read-only resources.
4. **CORS is not authentication.** It controls browsers, not attackers with curl; every endpoint still authenticates per [authentication.md](authentication.md).

## Framework examples

Express (`cors` package):

```js
const cors = require('cors');
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
```

FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Keep the origin list in configuration per environment rather than hardcoding localhost origins into production.

## Verify

**REASONED:** not demonstrated against a deployed API: no Express or FastAPI deployment or browser session is available here, so which origins real CORS middleware echoes rests on the Fetch Standard and MDN's CORS guide (Sources). An exposed API echoes `https://evil.example` in `Access-Control-Allow-Origin`; the fixed API omits it for that origin and returns only your listed origin, with `Access-Control-Allow-Credentials: true` only where the browser must send credentials. For this change both pipelines ran with curl 8.18.0: against a loopback listener answering 200 with the listed origin's headers, each printed the status line with both Access-Control headers and exited 0; against a closed loopback port, each printed `curl: (7) Failed to connect ...` on stderr and its inconclusive line (the same pipelines without the pipefail subshell exited 1 with empty output, and silently under the old `-s`); and against a stub curl that printed `HTTP/1.1 200 OK`, wrote a transfer error to stderr and returned 18, the pipeline without pipefail exited 0 as if it had passed, while the `set -o pipefail` subshell (the convention litellm.md and search-engines.md use) exited 18, so its `|| echo` printed the inconclusive line. These runs record the pipelines' behaviour, not any deployed middleware's CORS decisions.

```bash
(set -o pipefail; curl -q -sS -o /dev/null -D - https://api.example.com/data -H "Origin: https://evil.example" | grep -iE 'HTTP/|access-control') || echo "inconclusive: the transfer failed or printed no status line; not a pass"
# expect: a 2xx status line matching the own-origin probe below, and no Access-Control-Allow-Origin echoing the hostile origin; any other status, a proxy's lone "HTTP/1.1 200 Connection established" line, the inconclusive line, or empty output is inconclusive, not a pass
(set -o pipefail; curl -q -sS -o /dev/null -D - https://api.example.com/data -H "Origin: https://app.example.com" | grep -iE 'HTTP/|access-control') || echo "inconclusive: the transfer failed or printed no status line; not a pass"
# expect: a 2xx status line, your origin in Access-Control-Allow-Origin, and Allow-Credentials only if the browser must send credentials: cookies, HTTP authentication, or TLS client certificates
```

## Sources (checked September 2026)

- MDN: Cross-Origin Resource Sharing, for the protocol itself: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- Fetch Standard, definition of credentials: https://fetch.spec.whatwg.org/#credentials
- Express `cors` middleware, for the `origin` and `credentials` options used above: https://expressjs.com/en/resources/middleware/cors/
- FastAPI CORS, for `CORSMiddleware` and its parameters: https://fastapi.tiangolo.com/tutorial/cors/
