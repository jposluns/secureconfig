---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "a9994c70c664b12d544047fe092a7617fb7e8416ce5cb3ffd44c09a1abaab584",
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
    "verify-hostile": {"text": "The hostile-Origin probe should not return Access-Control-Allow-Origin echoing https://evil.example; no actual response is recorded.", "components": ["protocol", "express", "fastapi"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc"], "status": "REASONED", "verify": [1]},
    "verify-allowed": {"text": "The allowed-Origin probe should return the app origin, with Allow-Credentials only if cookies are used as stated in the guide; no actual response is recorded.", "components": ["protocol", "express", "fastapi"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc"], "status": "REASONED", "verify": [1]}
  }
}
---
# CORS: allow your origins, not everyone's

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| exact-origins: Allow exact browser origins, illustrated by Access-Control-Allow-Origin: https://app.example.com; keep environment-specific lists in configuration instead of production localhost entries. | MDN CORS documentation unknown | REASONED |
| wildcard-credentials: Browsers refuse wildcard Access-Control-Allow-Origin with credentials; the guide restricts wildcard use to public, unauthenticated, read-only resources. | MDN CORS documentation unknown | REASONED |
| origin-reflection: Reflect only origins checked against an explicit allowlist; reflecting arbitrary Origin values permits hostile sites to read credentialed responses. | MDN CORS documentation unknown | REASONED |
| authentication: CORS controls browsers rather than curl or other attackers, does not expose a port and does not replace endpoint authentication. | MDN CORS documentation unknown; Express cors middleware unknown | REASONED |
| express-origins: Express cors uses origin: ['https://app.example.com'] as the allowed origin list. | Express cors middleware unknown | REASONED |
| express-credentials: The Express example enables credentials with credentials: true. | Express cors middleware unknown | REASONED |
| fastapi-origins: FastAPI adds CORSMiddleware with allow_origins restricted to https://app.example.com. | FastAPI CORSMiddleware unknown | REASONED |
| fastapi-credentials: The FastAPI example enables allow_credentials=True. | FastAPI CORSMiddleware unknown | REASONED |
| fastapi-methods: The FastAPI example allows only GET and POST through allow_methods. | FastAPI CORSMiddleware unknown | REASONED |
| fastapi-headers: The FastAPI example allows Authorization and Content-Type through allow_headers. | FastAPI CORSMiddleware unknown | REASONED |
| verify-hostile: The hostile-Origin probe should not return Access-Control-Allow-Origin echoing https://evil.example; no actual response is recorded. | MDN CORS documentation unknown; Express cors middleware unknown; FastAPI CORSMiddleware unknown | REASONED |
| verify-allowed: The allowed-Origin probe should return the app origin, with Allow-Credentials only if cookies are used as stated in the guide; no actual response is recorded. | MDN CORS documentation unknown; Express cors middleware unknown; FastAPI CORSMiddleware unknown | REASONED |
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

**REASONED:** not demonstrated here: the authoring host forbids opening listeners without an isolated network namespace, and has none, so no deployed API or browser session could be run; this rests on the Fetch Standard and MDN's CORS guide (Sources). An exposed API echoes `https://evil.example` in `Access-Control-Allow-Origin`; the fixed API omits it for that origin and returns only your listed origin, with `Access-Control-Allow-Credentials: true` only where the browser must send credentials.

```bash
curl -q -s -o /dev/null -D - https://api.example.com/data -H "Origin: https://evil.example" | grep -i access-control
# expect: no Access-Control-Allow-Origin echoing the hostile origin
curl -q -s -o /dev/null -D - https://api.example.com/data -H "Origin: https://app.example.com" | grep -i access-control
# expect: your origin, and Allow-Credentials only if the browser must send credentials: cookies, HTTP authentication, or TLS client certificates
```

## Sources (checked September 2026)

- MDN: Cross-Origin Resource Sharing, for the protocol itself: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- Fetch Standard, definition of credentials: https://fetch.spec.whatwg.org/#credentials
- Express `cors` middleware, for the `origin` and `credentials` options used above: https://expressjs.com/en/resources/middleware/cors/
- FastAPI CORS, for `CORSMiddleware` and its parameters: https://fastapi.tiangolo.com/tutorial/cors/
