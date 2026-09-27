---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "41046bb0fcef51ea602f7107db5fe17b7eae9b951f130fee0d4d57ef324b6adb",
  "components": {
    "python": {
      "name": "Python http.server documentation",
      "basis": "3.14.4",
      "sources": {
        "s8fae94406709": "https://docs.python.org/3/library/http.server.html"
      }
    },
    "gunicorn": {
      "name": "Gunicorn documentation",
      "basis": "unknown",
      "sources": {
        "s72daf362300c": "https://gunicorn.org/reference/settings/"
      }
    },
    "uvicorn": {
      "name": "Uvicorn source",
      "basis": "5ac6265a01ff6dcadb0e4250152c3deaf8a168a9",
      "sources": {
        "s02429a4a09d9": "https://github.com/Kludex/uvicorn/blob/5ac6265a01ff6dcadb0e4250152c3deaf8a168a9/docs/settings.md"
      }
    },
    "django": {
      "name": "Django documentation",
      "basis": "6.1",
      "sources": {
        "s7289e1c111ae": "https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/"
      }
    },
    "argon": {
      "name": "argon2-cffi documentation",
      "basis": "unknown",
      "sources": {
        "sff2b9a487e67": "https://argon2-cffi.readthedocs.io/"
      }
    },
    "werkzeug": {
      "name": "Werkzeug documentation",
      "basis": "unknown",
      "sources": {
        "sd5066c63a3ca": "https://werkzeug.palletsprojects.com/en/stable/serving/"
      }
    },
    "fastapi": {
      "name": "FastAPI documentation",
      "basis": "unknown",
      "sources": {
        "s077aff608a5c": "https://fastapi.tiangolo.com/reference/security/"
      }
    },
    "oidc-stub": {
      "name": "FastAPI OpenIdConnect source",
      "basis": "31bbb380748ccead62fc0f42dbf4273f11dadccf",
      "sources": {
        "s876e3d51e7ac": "https://github.com/fastapi/fastapi/blob/31bbb380748ccead62fc0f42dbf4273f11dadccf/fastapi/security/open_id_connect_url.py"
      }
    },
    "python-pin": {
      "name": "Python http.server source",
      "basis": "v3.14.4",
      "sources": {
        "s0038729960a0": "https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1322-L1334",
        "sa3111578d65d": "https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1371-L1373"
      }
    }
  },
  "claims": {
    "bind": {"text": "Use loopback behind a same-host TLS proxy; wildcard is for authenticated direct TLS or private managed ingress. Platform-specific address/port mappings are cross-guide guidance without a listed platform source.", "components": ["gunicorn", "uvicorn"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9"], "status": "REASONED"},
    "flask-tls": {"text": "Flask development server binds 127.0.0.1:8443 with cert/key ssl_context; adhoc requires cryptography and remains development-only.", "components": ["werkzeug"], "sources": ["werkzeug:sd5066c63a3ca"], "status": "REASONED"},
    "gunicorn-tls": {"text": "Gunicorn binds 0.0.0.0:8443 with --certfile and --keyfile for direct TLS.", "components": ["gunicorn"], "sources": ["gunicorn:s72daf362300c"], "status": "REASONED"},
    "uvicorn-tls": {"text": "Uvicorn binds 0.0.0.0:8443 with --ssl-certfile and --ssl-keyfile for direct TLS.", "components": ["uvicorn"], "sources": ["uvicorn:s02429a4a09d9"], "status": "REASONED"},
    "django-redirect": {"text": "Set SECURE_SSL_REDIRECT=True.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-proxy": {"text": "Set SECURE_PROXY_SSL_HEADER only behind a trusted proxy that strips and replaces X-Forwarded-Proto; prevent direct bypass.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-cookies": {"text": "Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE true.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-hsts": {"text": "Begin HSTS at 3600 seconds and include-subdomains false; raise duration and scope only after valid HTTPS is confirmed.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "deploy-check": {"text": "Run manage.py check --deploy and fix its findings.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "password": {"text": "Keep Django built-in hashing; Flask/FastAPI require an application user store and argon2-cffi or bcrypt. PasswordHasher.verify raises on mismatch; bcrypt and user-store assertions lack listed sources.", "components": ["django", "argon"], "sources": ["django:s7289e1c111ae", "argon:sff2b9a487e67"], "status": "REASONED"},
    "secrets": {"text": "Generate secrets.token_urlsafe(32) and load secrets from the environment; the secrets API is not covered by listed Sources.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "credential-extraction": {"text": "FastAPI security helpers extract credentials and declare schemes; presence/scheme checks do not verify signature, issuer, audience or expiry.", "components": ["fastapi"], "sources": ["fastapi:s077aff608a5c"], "status": "REASONED"},
    "oidc": {"text": "OpenIdConnect is a stub and does not use its discovery URL; validate extracted tokens with an OIDC library and authorize separately.", "components": ["fastapi", "oidc-stub"], "sources": ["fastapi:s077aff608a5c", "oidc-stub:s876e3d51e7ac"], "status": "REASONED"},
    "login-limit": {"text": "Rate-limit login at the proxy or with slowapi; no listed source documents that limiter.", "components": ["fastapi"], "sources": ["fastapi:s077aff608a5c"], "status": "REASONED"},
    "mfa": {"text": "Use pyotp and qrcode, django-otp for Django, or linked MFA guidance; these packages lack listed Sources.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "client-validation": {"text": "Never ship requests/httpx verify=False or ssl._create_unverified_context; these client APIs lack listed Sources.", "components": ["python"], "sources": ["python:s8fae94406709"], "status": "REASONED"},
    "client-ca": {"text": "REQUESTS_CA_BUNDLE selects a requests CA and SSL_CERT_FILE selects an httpx/ssl CA; these variables lack listed Sources.", "components": ["python"], "sources": ["python:s8fae94406709"], "status": "REASONED"},
    "http-server-bind": {"text": "As of Python 3.14.4, http.server binds every interface by default; explicitly bind 127.0.0.1:8000.", "components": ["python-pin"], "sources": ["python-pin:s0038729960a0", "python-pin:sa3111578d65d"], "status": "REASONED"},
    "http-server-files": {"text": "http.server serves the current directory and follows symlinks outside it; it is unsuitable for production. Share only a non-private directory through an SSH tunnel.", "components": ["python"], "sources": ["python:s8fae94406709"], "status": "REASONED"},
    "verify-tls": {"text": "Public HTTPS must succeed without -k; certificate, chain, hostname and trust failures need investigation.", "components": ["gunicorn", "uvicorn"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "A real protected route denies no credentials with 401/403 and accepts valid file-supplied credentials with 2xx; logs or direct probing distinguish app from proxy enforcement.", "components": ["django", "fastapi"], "sources": ["django:s7289e1c111ae", "fastapi:s077aff608a5c"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for loopback behind a same-host proxy or the required managed-ingress address and port.", "components": ["gunicorn", "uvicorn"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9"], "status": "REASONED", "verify": [1]}
  }
}
---
# Python web apps: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| bind: Use loopback behind a same-host TLS proxy; wildcard is for authenticated direct TLS or private managed ingress. Platform-specific address/port mappings are cross-guide guidance without a listed platform source. | Gunicorn documentation unknown; Uvicorn source 5ac6265a01ff6dcadb0e4250152c3deaf8a168a9 | REASONED |
| flask-tls: Flask development server binds 127.0.0.1:8443 with cert/key ssl_context; adhoc requires cryptography and remains development-only. | Werkzeug documentation unknown | REASONED |
| gunicorn-tls: Gunicorn binds 0.0.0.0:8443 with --certfile and --keyfile for direct TLS. | Gunicorn documentation unknown | REASONED |
| uvicorn-tls: Uvicorn binds 0.0.0.0:8443 with --ssl-certfile and --ssl-keyfile for direct TLS. | Uvicorn source 5ac6265a01ff6dcadb0e4250152c3deaf8a168a9 | REASONED |
| django-redirect: Set SECURE_SSL_REDIRECT=True. | Django documentation 6.1 | REASONED |
| django-proxy: Set SECURE_PROXY_SSL_HEADER only behind a trusted proxy that strips and replaces X-Forwarded-Proto; prevent direct bypass. | Django documentation 6.1 | REASONED |
| django-cookies: Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE true. | Django documentation 6.1 | REASONED |
| django-hsts: Begin HSTS at 3600 seconds and include-subdomains false; raise duration and scope only after valid HTTPS is confirmed. | Django documentation 6.1 | REASONED |
| deploy-check: Run manage.py check --deploy and fix its findings. | Django documentation 6.1 | REASONED |
| password: Keep Django built-in hashing; Flask/FastAPI require an application user store and argon2-cffi or bcrypt. PasswordHasher.verify raises on mismatch; bcrypt and user-store assertions lack listed sources. | Django documentation 6.1; argon2-cffi documentation unknown | REASONED |
| secrets: Generate secrets.token_urlsafe(32) and load secrets from the environment; the secrets API is not covered by listed Sources. | Django documentation 6.1 | REASONED |
| credential-extraction: FastAPI security helpers extract credentials and declare schemes; presence/scheme checks do not verify signature, issuer, audience or expiry. | FastAPI documentation unknown | REASONED |
| oidc: OpenIdConnect is a stub and does not use its discovery URL; validate extracted tokens with an OIDC library and authorize separately. | FastAPI documentation unknown; FastAPI OpenIdConnect source 31bbb380748ccead62fc0f42dbf4273f11dadccf | REASONED |
| login-limit: Rate-limit login at the proxy or with slowapi; no listed source documents that limiter. | FastAPI documentation unknown | REASONED |
| mfa: Use pyotp and qrcode, django-otp for Django, or linked MFA guidance; these packages lack listed Sources. | Django documentation 6.1 | REASONED |
| client-validation: Never ship requests/httpx verify=False or ssl._create_unverified_context; these client APIs lack listed Sources. | Python http.server documentation 3.14.4 | REASONED |
| client-ca: REQUESTS_CA_BUNDLE selects a requests CA and SSL_CERT_FILE selects an httpx/ssl CA; these variables lack listed Sources. | Python http.server documentation 3.14.4 | REASONED |
| http-server-bind: As of Python 3.14.4, http.server binds every interface by default; explicitly bind 127.0.0.1:8000. | Python http.server source v3.14.4 | REASONED |
| http-server-files: http.server serves the current directory and follows symlinks outside it; it is unsuitable for production. Share only a non-private directory through an SSH tunnel. | Python http.server documentation 3.14.4 | REASONED |
| verify-tls: Public HTTPS must succeed without -k; certificate, chain, hostname and trust failures need investigation. | Gunicorn documentation unknown; Uvicorn source 5ac6265a01ff6dcadb0e4250152c3deaf8a168a9 | REASONED |
| verify-auth: A real protected route denies no credentials with 401/403 and accepts valid file-supplied credentials with 2xx; logs or direct probing distinguish app from proxy enforcement. | Django documentation 6.1; FastAPI documentation unknown | REASONED |
| verify-bind: Inspect every listener for loopback behind a same-host proxy or the required managed-ingress address and port. | Gunicorn documentation unknown; Uvicorn source 5ac6265a01ff6dcadb0e4250152c3deaf8a168a9 | REASONED |
<!-- version-basis:end -->

Covers Flask, FastAPI/Uvicorn, Gunicorn, and Django. Preferred production layout: bind the app server to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). On a managed platform the platform terminates TLS at its edge and you bind the address it requires ([paas.md](paas.md)). The app servers can also terminate TLS themselves, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. TLS per server

Flask's built-in server (development only; it is not a production server, TLS or not):

```python
app.run(host="127.0.0.1", port=8443, ssl_context=("cert.pem", "key.pem"))
# ssl_context="adhoc" generates a throwaway self-signed cert; requires the cryptography package
```

Gunicorn (Flask/Django/WSGI in production):

```bash
gunicorn --bind 0.0.0.0:8443 \
  --certfile /etc/ssl/certs/server.crt \
  --keyfile  /etc/ssl/private/server.key \
  app:app
```

Uvicorn (FastAPI/ASGI):

```bash
uvicorn main:app --host 0.0.0.0 --port 8443 \
  --ssl-certfile /etc/ssl/certs/server.crt \
  --ssl-keyfile  /etc/ssl/private/server.key
```

Bind to `0.0.0.0` only when either (a) the process itself terminates TLS with authentication in place, or (b) a platform terminates TLS at its ingress and reaches your app over a private or container network. On a managed platform you bind the address and port it requires (`0.0.0.0` on `$PORT` for Render, Railway, and Heroku Cedar; `::` on `$PORT` for Heroku Fir; `0.0.0.0` matching `internal_port` for Fly) and the platform handles TLS, so plain HTTP behind that protected ingress is fine and application authentication is still required ([paas.md](paas.md)). Otherwise, on a host you expose directly, keep `127.0.0.1` and terminate TLS in a reverse proxy.

## 2. Django settings for HTTPS

```python
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # only behind a proxy that STRIPS the client's value and sets its own
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600               # start small; raise to 31536000 (1 year) after HTTPS is confirmed working
SECURE_HSTS_INCLUDE_SUBDOMAINS = False   # True ONLY after every subdomain also serves valid HTTPS; the commitment is irreversible for SECURE_HSTS_SECONDS
```

`SECURE_PROXY_SSL_HEADER` must be set only when a proxy you control, or a managed platform that reliably guarantees this, strips any client-supplied `X-Forwarded-Proto` from every request and sets it itself from the real connection scheme; otherwise a client can spoof it and make Django treat plain HTTP as HTTPS. Leave it unset if you are not behind such a proxy, and confirm the app is reachable only through that proxy, not directly. Run `python manage.py check --deploy` and fix what it reports.

## 3. Authentication

Follow [authentication.md](authentication.md). Framework specifics:

- Django's built-in auth already hashes passwords correctly; do not replace it with custom code.
- Flask and FastAPI have no user store; hash passwords with `argon2-cffi` or `bcrypt`:

```python
from argon2 import PasswordHasher
ph = PasswordHasher()
hash_ = ph.hash(password)
ph.verify(hash_, password)   # raises on mismatch
```

- Generate tokens and secrets with the standard library, and load them from the environment:

```python
import secrets
token = secrets.token_urlsafe(32)
```

- FastAPI's `fastapi.security` classes (`HTTPBearer`, `APIKeyHeader`, `OAuth2AuthorizationCodeBearer`, and so on) extract the credential from the request and declare the OpenAPI security scheme; what they check varies by helper (an API-key helper checks only that a value is present; the HTTP and OAuth2 bearer helpers may also check the scheme), but none authenticate the credential (no signature, issuer, audience, or expiry check), and `OpenIdConnect` is documented as a stub that does not implement the scheme or use the discovery URL. Use them to extract the token, then validate it (signature, issuer, audience, expiry) with an OIDC library such as Authlib, and authorize per [oidc-integration.md](oidc-integration.md).
- Rate-limit login routes (for example with a proxy-level limit or a library such as slowapi for ASGI apps).
- MFA: add TOTP with [pyotp](https://github.com/pyauth/pyotp) plus the [qrcode](https://pypi.org/project/qrcode/) package for enrolment QR codes; [django-otp](https://pypi.org/project/django-otp/) integrates this into Django. Requirements and options in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

Never ship `verify=False` (requests/httpx) or `ssl._create_unverified_context`. For an internal CA, point the client at it instead:

```bash
export REQUESTS_CA_BUNDLE=/path/ca.crt   # requests
export SSL_CERT_FILE=/path/ca.crt        # httpx and the ssl module
```

## 5. Do not quick-share files with `http.server`

`python -m http.server` is a common quick-share suggestion, and it is the wrong one on any reachable host. By default it binds every interface (as of Python 3.14.4), and it serves the current directory: source, `.env`, private keys, and database dumps are all downloadable by anyone who can reach the port. It also follows symbolic links, so a link in that directory hands out files from outside it, and the Python docs mark the module as not suitable for production. If you have no alternative, bind loopback and serve a directory that holds only what you mean to share:

```bash
cd /path/to/a/directory/with/nothing/private || exit
python -m http.server -b 127.0.0.1 8000
```

Reach it through an SSH tunnel, including one that runs over your tailnet, never a public bind.

## 6. Verify (REASONED: TLS, authentication and listener expectations follow the Sources below and linked deployment guidance; no deployment run or outcome is recorded in this guide. This metadata-only review has no deployed Python application, proxy or managed ingress to test.)

```bash
curl -q -sSI --noproxy '*' https://example.com/        # public HTTPS endpoint: must succeed without -k; if not, investigate the cert, chain, hostname, or your client trust store, never -k
# An unauthenticated request to a real protected path must be REJECTED and a valid credential ACCEPTED. --noproxy
# disables YOUR client proxy, not a reverse proxy in front of the app, so if the app sits behind an auth proxy this
# pair cannot tell whether the app or the proxy enforced it: confirm the layer by probing the app directly or in its logs.
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' 'https://example.com/REPLACE_WITH_PROTECTED_PATH'        # no credentials: expect 401/403
curl -q -g -sS --noproxy '*' -H @cred.txt -o /dev/null -w '%{http_code}\n' 'https://example.com/REPLACE_WITH_PROTECTED_PATH'   # valid credential from a file (cred.txt holds a full header line, e.g. "Authorization: Bearer ..."): expect 2xx
ss -tlnp   # every listener: loopback for a same-host reverse proxy, or the platform's required address and port from section 1 on managed ingress
```

## Sources (checked September 2026)

- Python `http.server` (binds all interfaces by default, serves the current directory, follows symlinks, not for production) (Python 3.14.4): https://docs.python.org/3/library/http.server.html
- Gunicorn documentation (settings reference: bind, certfile, keyfile, ca_certs): https://gunicorn.org/reference/settings/
- Uvicorn settings reference: https://github.com/Kludex/uvicorn/blob/5ac6265a01ff6dcadb0e4250152c3deaf8a168a9/docs/settings.md
- Django deployment checklist: https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
- argon2-cffi: https://argon2-cffi.readthedocs.io/
- Werkzeug serving (`ssl_context="adhoc"` requires cryptography): https://werkzeug.palletsprojects.com/en/stable/serving/
- FastAPI security reference: https://fastapi.tiangolo.com/reference/security/ ; `OpenIdConnect` source (stub warning): https://github.com/fastapi/fastapi/blob/31bbb380748ccead62fc0f42dbf4273f11dadccf/fastapi/security/open_id_connect_url.py
- `http.server` binds with `bind=None` and `AI_PASSIVE`, the wildcard address (pinned tag v3.14.4): https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1322-L1334
- `python -m http.server`'s `-b/--bind` has no default value, and its help says "default: all interfaces" (pinned tag v3.14.4): https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1371-L1373
