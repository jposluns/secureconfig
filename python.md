# Python web apps: TLS and authentication

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

`python -m http.server` is a common quick-share suggestion, and it is the wrong one on any reachable host. By default it binds every interface, and it serves the current directory: source, `.env`, private keys, and database dumps are all downloadable by anyone who can reach the port. It also follows symbolic links, so a link in that directory hands out files from outside it, and the Python docs mark the module as not suitable for production. If you have no alternative, bind loopback and serve a directory that holds only what you mean to share:

```bash
cd /path/to/a/directory/with/nothing/private || exit
python -m http.server -b 127.0.0.1 8000
```

Reach it through an SSH tunnel, including one that runs over your tailnet, never a public bind.

## 6. Verify

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

- Python `http.server` (binds all interfaces by default, serves the current directory, follows symlinks, not for production): https://docs.python.org/3/library/http.server.html
- Gunicorn documentation (settings reference: bind, certfile, keyfile, ca_certs): https://gunicorn.org/reference/settings/
- Uvicorn settings reference: https://github.com/Kludex/uvicorn/blob/5ac6265a01ff6dcadb0e4250152c3deaf8a168a9/docs/settings.md
- Django deployment checklist: https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/
- argon2-cffi: https://argon2-cffi.readthedocs.io/
- Werkzeug serving (`ssl_context="adhoc"` requires cryptography): https://werkzeug.palletsprojects.com/en/stable/serving/
- FastAPI security reference: https://fastapi.tiangolo.com/reference/security/ ; `OpenIdConnect` source (stub warning): https://github.com/fastapi/fastapi/blob/31bbb380748ccead62fc0f42dbf4273f11dadccf/fastapi/security/open_id_connect_url.py
