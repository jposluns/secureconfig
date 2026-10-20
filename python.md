# Python web apps: TLS and authentication

Flask, FastAPI and Django are Python web frameworks, served by Uvicorn or Gunicorn. This guide helps your AI assistant deploy them securely, including loopback behind a TLS proxy or a managed platform's required listener, Django's HTTPS settings, authentication, and `http.server` only as a last resort, for curated files over SSH.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/python.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Django documentation 6.1, Python http.server documentation 3.14.4, Python http.server source v3.14.4, Python standard library documentation 3.14, CPython ssl source and documentation v3.14.8, CPython secrets documentation and source v3.14.8, PyOTP v2.9.0, and qrcode v8.2, plus 6 more recorded bases; 5 further sources are pinned to a commit and 6 carry no recorded version. Metadata reviewed 2026-10-20; documentation checked September 2026. The guide records 24 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Covers Flask, FastAPI/Uvicorn, Gunicorn, and Django. This guide's preferred production layout: bind the app server to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). For managed HTTP ingress, bind the listener required by your deployment; TLS termination depends on the platform and configuration described below ([paas.md](paas.md)). The app servers can also terminate TLS themselves, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

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

This guide's advice: Bind to `0.0.0.0` only when either (a) the process itself terminates TLS with authentication in place, or (b) a platform terminates TLS at its ingress and reaches your app over a private or container network. Otherwise, on a host you expose directly, keep `127.0.0.1` and terminate TLS in a reverse proxy.

This guide's advice for managed platforms: do not add extra listeners; bind only the listener required by your deployment. The documented HTTP ingress mappings are:

- Render web services must bind `0.0.0.0`. Render recommends the `PORT` environment variable (at the time of writing, default port 10000, configurable), can usually detect another bound port, and requires the public HTTP server to use `PORT` when multiple ports are bound ([web services](https://render.com/docs/web-services)).
- Heroku assigns each web process its port through `PORT` ([runtime principles](https://devcenter.heroku.com/articles/runtime-principles)). Fir Private Spaces networking uses IPv6 by default; Heroku warns that IPv4-only assumptions do not bind properly and recommends an IPv6 or dual-stack listener, typically `::` ([generations](https://devcenter.heroku.com/articles/generations)). These pages do not establish Cedar's listener address.
- Fly Proxy HTTP services must be reachable over IPv4: use `0.0.0.0` and match the configured `internal_port` to the app listener ([service binding](https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42)). IPv4-mapped IPv6 wildcard behaviour depends on the VM and runtime ([wildcard qualification](https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92)).
- Railway domains route to a detected or selected internal target port ([target ports](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146)). Railway says web servers should bind `0.0.0.0` and listen on the automatically injected `PORT` ([listener and port](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51)). Its edge proxy (tcp-proxy) terminates TLS; traffic is then forwarded over Railway's internal network to the deployment ([request flow](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43)).

Render's load balancer terminates inbound HTTPS and forwards HTTP to the web service ([web services](https://render.com/docs/web-services)). Heroku's HTTP routing page describes a load balancer offering SSL termination and routers forwarding HTTP to web dynos; it notes that both Private Spaces generations have different routers, so this is not a complete account of Private Spaces routing ([HTTP routing](https://devcenter.heroku.com/articles/http-routing)). Fly Proxy's `tls` handler terminates TLS and forwards plaintext ([TLS handler](https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176)); without handlers it passes TCP through, allowing the app to terminate TLS itself ([TCP passthrough](https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97)). This guide's advice: plain HTTP is acceptable only behind protected ingress that terminates TLS; application authentication is still required ([paas.md](paas.md)).

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

- Keep Django's built-in password hashing; do not replace it with custom code (this guide's advice).
- If your Flask or FastAPI application implements its own password accounts, provide its account storage and hash passwords with `argon2-cffi` or `bcrypt` (this guide's advice; follow the algorithm and legacy-bcrypt constraints in [authentication.md](authentication.md)):

```python
from argon2 import PasswordHasher
ph = PasswordHasher()
hash_ = ph.hash(password)
ph.verify(hash_, password)   # raises on mismatch
```

The [argon2-cffi 25.1.0 example](https://github.com/hynek/argon2-cffi/blob/25.1.0/README.md#L11-L28) documents these `PasswordHasher`, `hash` and `verify` calls and a `VerifyMismatchError` on mismatch. The [pinned bcrypt example](https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/README.rst#L62-L76) documents `hashpw(password, gensalt())` and `checkpw(password, hashed)`; these API examples do not establish framework user-store capabilities.

- Generate tokens and secrets with the standard library, and load them from the environment (this guide's advice):

```python
import secrets
token = secrets.token_urlsafe(32)
```

In [CPython v3.14.8](https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L91-L103), `token_urlsafe(nbytes=None)` returns URL-safe Base64 text from `nbytes` random bytes; the argument counts input bytes, not output characters. The explicit `32` above is this guide's example choice, not a size suitable for every secret. If the argument is omitted or `None`, it uses `DEFAULT_ENTROPY`, [32 bytes at this pin](https://github.com/python/cpython/blob/v3.14.8/Lib/secrets.py#L31-L45); the [documented default can change](https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L125-L130), including in maintenance releases.

- FastAPI's `fastapi.security` classes (`HTTPBearer`, `APIKeyHeader`, `OAuth2AuthorizationCodeBearer`, and so on) extract the credential from the request and declare the OpenAPI security scheme; what they check varies by helper (an API-key helper checks only that a value is present; the HTTP and OAuth2 bearer helpers may also check the scheme), but none authenticate the credential (no signature, issuer, audience, or expiry check), and `OpenIdConnect` is documented as a stub that does not implement the scheme or use the discovery URL. Use them to extract the token, then validate it (signature, issuer, audience, expiry) with an OIDC library such as Authlib, and authorize per [oidc-integration.md](oidc-integration.md).
- Rate-limit login routes (this guide's advice; for example with a proxy-level limit or a library such as slowapi for Starlette/FastAPI ASGI apps' HTTP endpoints; endpoints using slowapi's `limit` decorator must take an explicit `request` argument, and slowapi does not support WebSocket endpoints).
- MFA: add TOTP with [pyotp](https://github.com/pyauth/pyotp) plus the [qrcode](https://pypi.org/project/qrcode/) package for enrolment QR codes; [django-otp](https://pypi.org/project/django-otp/) integrates this into Django. Requirements and options in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

Never ship `verify=False` (requests/httpx) or `ssl._create_unverified_context` (this guide's advice). For an internal CA, point the client at it instead (this guide's advice):

```bash
export REQUESTS_CA_BUNDLE=/path/ca.crt   # requests
export SSL_CERT_FILE=/path/ca.crt        # HTTPX with verify=True and trust_env=True; OpenSSL default CA file for ssl when its default verify paths apply (see caveat below)
```

HTTPX 0.28.1's SSL guide says `SSL_CERT_FILE` and `SSL_CERT_DIR` are not automatically used and shows an explicit context; its code path contradicts that: its sync and async transports pass `verify` and `trust_env` to `create_ssl_context`, which reads `SSL_CERT_FILE` when both are true. Its environment guide says environment variables are used by default but does not list `SSL_CERT_FILE`. This guide's advice: use the export above for that HTTPX code path; pass an explicit CA context for other configurations. With no CA specified and verification enabled, CPython's `ssl.create_default_context()` tries to load default CAs (CPython notes this may fail silently). `ssl.get_default_verify_paths()` reports OpenSSL's default verify paths and environment-variable names.

At CPython v3.14.8, [`SSLContext.load_default_certs()`](https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L542-L548) calls `set_default_verify_paths()`, whose [`_ssl.c` implementation](https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L4607-L4626) calls OpenSSL's `SSL_CTX_set_default_verify_paths()`. [`get_default_verify_paths()` in `_ssl.c`](https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L5873-L5914) gets the file and directory environment-variable names from OpenSSL's `X509_get_default_cert_file_env()` and `X509_get_default_cert_dir_env()`; [`ssl.py`](https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L390-L405) returns those names and the resolved paths. [OpenSSL openssl-4.0.3](https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man3/SSL_CTX_load_verify_locations.pod#L39-L49) documents that `SSL_CTX_set_default_verify_paths()` honours both `SSL_CERT_FILE` and `SSL_CERT_DIR` for its default CA file and directory, subject to its environment rules: [these variables are security-sensitive for CA loading](https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L289-L298), and [security-sensitive environment variables are not consulted for set-user-ID or set-group-ID executables](https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L9-L13).

This guide's inference: that CPython default-path call uses those OpenSSL overrides when linked to a library with the cited behaviour, subject to the executable exclusions above. This guide's assessment: a CPython build may link a different OpenSSL release from `openssl-4.0.3`; these lines do not establish platform-specific default stores (including Windows or macOS builds) or whether a deployed configuration takes this path and loads its intended CAs.

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
- argon2-cffi PasswordHasher, hash and verify mismatch example (25.1.0, checked October 2026): https://github.com/hynek/argon2-cffi/blob/25.1.0/README.md#L11-L28
- Python bcrypt hashpw, gensalt and checkpw example (commit 2b4ba9ac84df972e8e81311d09559af8dc82ef33, checked October 2026): https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/README.rst#L62-L76
- Werkzeug serving (`ssl_context="adhoc"` requires cryptography): https://werkzeug.palletsprojects.com/en/stable/serving/
- FastAPI security reference: https://fastapi.tiangolo.com/reference/security/ ; `OpenIdConnect` source (stub warning): https://github.com/fastapi/fastapi/blob/31bbb380748ccead62fc0f42dbf4273f11dadccf/fastapi/security/open_id_connect_url.py
- `http.server` binds with `bind=None` and `AI_PASSIVE`, the wildcard address (pinned tag v3.14.4): https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1322-L1334
- `python -m http.server`'s `-b/--bind` has no default value, and its help says "default: all interfaces" (pinned tag v3.14.4): https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1371-L1373
- Python 3.14 secrets.token_urlsafe (series documentation, checked October 2026): https://docs.python.org/3.14/library/secrets.html
- CPython token_urlsafe input bytes and Base64 output (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L91-L103
- CPython secrets default entropy and token_bytes fallback (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Lib/secrets.py#L31-L45
- CPython secrets default may change in maintenance releases (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L125-L130
- Python 3.14 os.getenv environment loading (series documentation, checked October 2026): https://docs.python.org/3.14/library/os.html#os.getenv
- PyOTP one-time passwords and MFA (v2.9.0, checked October 2026): https://github.com/pyauth/pyotp/blob/v2.9.0/README.rst#L4-L5
- qrcode enrolment image generation (v8.2, checked October 2026): https://github.com/lincolnloop/python-qrcode/blob/v8.2/README.rst#L41-L44
- django-otp Django authentication integration (1.6.1, checked October 2026): https://pypi.org/project/django-otp/1.6.1/
- Requests REQUESTS_CA_BUNDLE trust roots (v2.32.3, checked October 2026): https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L238-L239
- slowapi Starlette/FastAPI scope (v0.1.10, checked October 2026): https://github.com/laurentS/slowapi/blob/v0.1.10/README.md#L1-L3
- slowapi limit decorator, endpoint request argument and WebSocket limitation (v0.1.10, checked October 2026): https://github.com/laurentS/slowapi/blob/v0.1.10/README.md#L24-L50
- HTTPX environment-variable default and trust_env (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/docs/environment_variables.md#L3-L7
- HTTPX environment guide variable list, which omits SSL_CERT_FILE (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/docs/environment_variables.md#L9-L53
- HTTPX SSL guide, verify=False example (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/docs/advanced/ssl.md#L12-L17
- HTTPX SSL guide, conflicting SSL_CERT_FILE statement (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/docs/advanced/ssl.md#L72-L86
- HTTPX SSL context selection with verify=True and trust_env=True (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/httpx/_config.py#L23-L40
- HTTPX sync transport passes verify and trust_env to create_ssl_context (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/default.py#L133-L154
- HTTPX async transport passes verify and trust_env to create_ssl_context (0.28.1, checked October 2026): https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/default.py#L278-L298
- CPython ssl get_default_verify_paths (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L390-L405
- CPython ssl load_default_certs (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L542-L548
- CPython ssl create_default_context conditional default-CA load (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L730-L736
- CPython ssl _create_unverified_context (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L744-L754
- CPython ssl documentation for default verify paths and OpenSSL environment keys (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L421-L433
- CPython ssl documentation for default CAs and silent failure (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L1642-L1649
- CPython ssl set_default_verify_paths calls OpenSSL SSL_CTX_set_default_verify_paths (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L4607-L4626
- CPython ssl default CA paths and environment-variable names from OpenSSL (v3.14.8, checked October 2026): https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L5873-L5914
- OpenSSL default CA file and directory environment overrides (openssl-4.0.3, checked October 2026): https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man3/SSL_CTX_load_verify_locations.pod#L39-L49
- OpenSSL security-sensitive environment variables excluded for set-user-ID or set-group-ID executables (openssl-4.0.3, checked October 2026): https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L9-L13
- OpenSSL SSL_CERT_FILE and SSL_CERT_DIR security-sensitive classification, with the openssl-rehash exception for SSL_CERT_DIR (openssl-4.0.3, checked October 2026): https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L289-L298
- Requests verify=False disables certificate verification (v2.32.3, checked October 2026): https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L241-L243
- Render web-service listener and TLS termination (checked October 2026): https://render.com/docs/web-services
- Heroku HTTP routing (checked October 2026): https://devcenter.heroku.com/articles/http-routing
- Heroku web-process port assignment (checked October 2026): https://devcenter.heroku.com/articles/runtime-principles
- Heroku Fir Private Spaces networking and listener recommendation (checked October 2026): https://devcenter.heroku.com/articles/generations. The article states: "Fir utilizes IPv6 as the default and recommended connection protocol for networking within Heroku Private Spaces." It warns: "If you designed your application, its dependencies, or connected services within a space assuming only IPv4 connectivity, they don’t bind properly on Fir." It recommends: "Ensure IPv6 compatibility by correctly binding to an IPv6 listener or the dual-stack address listener in your app’s language (typically ::) to leverage Fir’s networking configuration." This guide's assessment: these sentences concern networking within Heroku Private Spaces; they do not establish Cedar's listener address or a deployed application's listener configuration.
- Fly TCP passthrough (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97
- Fly TLS termination (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176
- Fly public service binding (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42
- Fly IPv4 and IPv6 wildcard qualification (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92
- Railway target ports (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146
- Railway web-server listener and injected port (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51
- Railway edge-proxy TLS termination and internal forwarding (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- django: Django documentation (6.1)
- python: Python http.server documentation (3.14.4)
- python-pin: Python http.server source (v3.14.4)
- stdlib-docs: Python standard library documentation (3.14)
- cpython-ssl: CPython ssl source and documentation (v3.14.8)
- cpython-secrets: CPython secrets documentation and source (v3.14.8)
- gunicorn: Gunicorn documentation (unknown)
- uvicorn: Uvicorn source (5ac6265a01ff6dcadb0e4250152c3deaf8a168a9)
- fastapi: FastAPI documentation (unknown)
- oidc-stub: FastAPI OpenIdConnect source (31bbb380748ccead62fc0f42dbf4273f11dadccf)
- bcrypt-api: Python bcrypt API example (2b4ba9ac84df972e8e81311d09559af8dc82ef33)
- werkzeug: Werkzeug documentation (unknown)
- argon: argon2-cffi documentation (unknown)
- pyotp: PyOTP (v2.9.0)
- qrcode: qrcode (v8.2)
- django-otp: django-otp (1.6.1)
- requests: Requests (v2.32.3)
- slowapi: slowapi source (v0.1.10)
- httpx: HTTPX source and documentation (0.28.1)
- openssl: OpenSSL documentation (openssl-4.0.3)
- argon-api: argon2-cffi API example (25.1.0)
- render: Render documentation (unknown)
- heroku: Heroku documentation (unknown)
- fly-pinned: Fly.io pinned documentation (2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9)
- railway: Railway documentation (72354493198302677fb6be6c692dd75c64cae2c6)

Claims (full source mapping in the JSON block below):

- bind (REASONED; gunicorn, uvicorn, render, heroku, fly-pinned, railway): This guide advises loopback for same-host TLS proxies, no extra managed listeners, and wildcard only for authenticated direct TLS or private TLS ingress; app auth remains required. Railway advises 0.0.0.0 on injected PORT; its edge proxy terminates TLS. Rules vary by deployment (Fir Private Spaces: IPv6/dual-stack recommended; Fly without handlers: TCP passthrough); Cedar's address is not established.
- flask-tls (REASONED; werkzeug): Flask development server binds 127.0.0.1:8443 with cert/key ssl_context; adhoc requires cryptography and remains development-only.
- gunicorn-tls (REASONED; gunicorn): Gunicorn binds 0.0.0.0:8443 with --certfile and --keyfile for direct TLS.
- uvicorn-tls (REASONED; uvicorn): Uvicorn binds 0.0.0.0:8443 with --ssl-certfile and --ssl-keyfile for direct TLS.
- django-redirect (REASONED; django): Set SECURE_SSL_REDIRECT=True.
- django-proxy (REASONED; django): Set SECURE_PROXY_SSL_HEADER only behind a trusted proxy that strips and replaces X-Forwarded-Proto; prevent direct bypass.
- django-cookies (REASONED; django): Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE true.
- django-hsts (REASONED; django): Begin HSTS at 3600 seconds and include-subdomains false; raise duration and scope only after valid HTTPS is confirmed.
- deploy-check (REASONED; django): Run manage.py check --deploy and fix its findings.
- password (REASONED; django, argon, argon-api, bcrypt-api): Keep Django's built-in hashing; do not replace it with custom code (guide advice). For Flask/FastAPI apps implementing local password accounts, this guide advises account storage and argon2-cffi or bcrypt under authentication.md's constraints; argon2-cffi 25.1.0's PasswordHasher.verify raises VerifyMismatchError on mismatch, and these APIs do not establish framework user-store capabilities.
- secrets (REASONED; django, stdlib-docs, cpython-secrets): Generate secrets.token_urlsafe(32) and load secrets from the environment (guide advice); 32 counts random input bytes and is this guide's example choice, not a universal size. CPython v3.14.8 uses DEFAULT_ENTROPY (32 bytes) when omitted or None, but that default may change, including in maintenance releases.
- credential-extraction (REASONED; fastapi): FastAPI security helpers extract credentials and declare schemes; presence/scheme checks do not verify signature, issuer, audience or expiry.
- oidc (REASONED; fastapi, oidc-stub): OpenIdConnect is a stub and does not use its discovery URL; validate extracted tokens with an OIDC library and authorize separately.
- login-limit (REASONED; fastapi, slowapi): Rate-limiting login routes and a proxy-level limit are this guide's advice. slowapi v0.1.10 documents limits for Starlette/FastAPI HTTP endpoints; endpoints using its limit decorator must take an explicit request argument, and WebSocket endpoints are not supported.
- mfa (REASONED; django, pyotp, qrcode, django-otp): Use pyotp and qrcode, django-otp for Django, or linked MFA guidance.
- client-validation (REASONED; python, requests, httpx, cpython-ssl): Never ship requests/httpx verify=False or ssl._create_unverified_context; HTTPX documents verify=False and CPython defines _create_unverified_context. The prohibition is this guide's advice.
- client-ca (REASONED; cpython-ssl, openssl): CPython's ssl reports OpenSSL default verify paths and environment-variable names. With no CA specified and verification enabled, create_default_context tries default CAs; loading may fail silently. This guide's inference: the call uses SSL_CERT_FILE/SSL_CERT_DIR if OpenSSL behaves as cited. This guide's assessment: linked OpenSSL may differ; platform stores and deployed use remain unverified.
- client-ca-httpx (REASONED; httpx): HTTPX 0.28.1's transport passes verify and trust_env to create_ssl_context, which reads SSL_CERT_FILE when verify=True and trust_env=True; its SSL guide contradicts that source. Its environment guide says environment variables are used by default but does not list SSL_CERT_FILE.
- client-ca-advice (REASONED; requests, httpx, cpython-ssl, openssl): REQUESTS_CA_BUNDLE selects a requests CA. OpenSSL openssl-4.0.3 honours SSL_CERT_FILE/SSL_CERT_DIR for its default CA file/directory except in set-user-ID/set-group-ID executables. This guide's advice: use the exports for requests, the stated HTTPX path and CPython's qualified default-path call, or an explicit context for other configurations.
- http-server-bind (REASONED; python-pin): As of Python 3.14.4, http.server binds every interface by default; explicitly bind 127.0.0.1:8000.
- http-server-files (REASONED; python): http.server serves the current directory and follows symlinks outside it; it is unsuitable for production. Share only a non-private directory through an SSH tunnel.
- verify-tls (REASONED; gunicorn, uvicorn): Public HTTPS must succeed without -k; certificate, chain, hostname and trust failures need investigation.
- verify-auth (REASONED; django, fastapi): A real protected route denies no credentials with 401/403 and accepts valid file-supplied credentials with 2xx; logs or direct probing distinguish app from proxy enforcement.
- verify-bind (REASONED; gunicorn, uvicorn): Inspect every listener for loopback behind a same-host proxy or the required managed-ingress address and port.

````json
{
  "schema": 1,
  "checked": "2026-10-20",
  "documentation_checked": "2026-09",
  "body_sha256": "e21376e7db41e8ea39732f7cefcb6bb6afd1f25d9078ecff86a3884562de704b",
  "components": {
    "django": {
      "name": "Django documentation",
      "basis": "6.1",
      "sources": {
        "s7289e1c111ae": "https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/"
      }
    },
    "python": {
      "name": "Python http.server documentation",
      "basis": "3.14.4",
      "sources": {
        "s8fae94406709": "https://docs.python.org/3/library/http.server.html"
      }
    },
    "python-pin": {
      "name": "Python http.server source",
      "basis": "v3.14.4",
      "sources": {
        "s0038729960a0": "https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1322-L1334",
        "sa3111578d65d": "https://github.com/python/cpython/blob/v3.14.4/Lib/http/server.py#L1371-L1373"
      }
    },
    "stdlib-docs": {
      "name": "Python standard library documentation",
      "basis": "3.14",
      "sources": {
        "s971d128efc65": "https://docs.python.org/3.14/library/secrets.html",
        "sdad376a711c3": "https://docs.python.org/3.14/library/os.html#os.getenv"
      }
    },
    "cpython-ssl": {
      "name": "CPython ssl source and documentation",
      "basis": "v3.14.8",
      "sources": {
        "sbac049853cda": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L390-L405",
        "s6dcc06feaaaf": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L542-L548",
        "s4d7f143c9456": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L730-L736",
        "s4a1cd173d596": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L744-L754",
        "s79d6191e12eb": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L421-L433",
        "s82c72b9a971a": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L1642-L1649",
        "sdf61ba8e79a7": "https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L4607-L4626",
        "s2d42808e6cad": "https://github.com/python/cpython/blob/v3.14.8/Modules/_ssl.c#L5873-L5914"
      }
    },
    "cpython-secrets": {
      "name": "CPython secrets documentation and source",
      "basis": "v3.14.8",
      "sources": {
        "s31e1a792a6b1": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L91-L103",
        "s7cc14a5ebfa0": "https://github.com/python/cpython/blob/v3.14.8/Lib/secrets.py#L31-L45",
        "sdef0e1600064": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/secrets.rst#L125-L130"
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
    "bcrypt-api": {
      "name": "Python bcrypt API example",
      "basis": "2b4ba9ac84df972e8e81311d09559af8dc82ef33",
      "sources": {
        "s340a2923b6da": "https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/README.rst#L62-L76"
      }
    },
    "werkzeug": {
      "name": "Werkzeug documentation",
      "basis": "unknown",
      "sources": {
        "sd5066c63a3ca": "https://werkzeug.palletsprojects.com/en/stable/serving/"
      }
    },
    "argon": {
      "name": "argon2-cffi documentation",
      "basis": "unknown",
      "sources": {
        "sff2b9a487e67": "https://argon2-cffi.readthedocs.io/"
      }
    },
    "pyotp": {
      "name": "PyOTP",
      "basis": "v2.9.0",
      "sources": {
        "sc118b8ed3bdd": "https://github.com/pyauth/pyotp/blob/v2.9.0/README.rst#L4-L5"
      }
    },
    "qrcode": {
      "name": "qrcode",
      "basis": "v8.2",
      "sources": {
        "s8247ddfed3d3": "https://github.com/lincolnloop/python-qrcode/blob/v8.2/README.rst#L41-L44"
      }
    },
    "django-otp": {
      "name": "django-otp",
      "basis": "1.6.1",
      "sources": {
        "sa5c0f7097219": "https://pypi.org/project/django-otp/1.6.1/"
      }
    },
    "requests": {
      "name": "Requests",
      "basis": "v2.32.3",
      "sources": {
        "s21c6be6f6df4": "https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L238-L239",
        "s17c5a0a7ffb2": "https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L241-L243"
      }
    },
    "slowapi": {
      "name": "slowapi source",
      "basis": "v0.1.10",
      "sources": {
        "sf150aa58aa31": "https://github.com/laurentS/slowapi/blob/v0.1.10/README.md#L1-L3",
        "s4ca3e1e80817": "https://github.com/laurentS/slowapi/blob/v0.1.10/README.md#L24-L50"
      }
    },
    "httpx": {
      "name": "HTTPX source and documentation",
      "basis": "0.28.1",
      "sources": {
        "s52608d6c5e47": "https://github.com/encode/httpx/blob/0.28.1/docs/environment_variables.md#L3-L7",
        "sd33b79237122": "https://github.com/encode/httpx/blob/0.28.1/docs/environment_variables.md#L9-L53",
        "s928d85a8d13e": "https://github.com/encode/httpx/blob/0.28.1/docs/advanced/ssl.md#L12-L17",
        "s3734fbccdf40": "https://github.com/encode/httpx/blob/0.28.1/docs/advanced/ssl.md#L72-L86",
        "s30dd14bf172e": "https://github.com/encode/httpx/blob/0.28.1/httpx/_config.py#L23-L40",
        "s4a1f3b43f184": "https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/default.py#L133-L154",
        "sc5a61a9b2f64": "https://github.com/encode/httpx/blob/0.28.1/httpx/_transports/default.py#L278-L298"
      }
    },
    "openssl": {
      "name": "OpenSSL documentation",
      "basis": "openssl-4.0.3",
      "sources": {
        "s592eb65718de": "https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man3/SSL_CTX_load_verify_locations.pod#L39-L49",
        "sfd19784d8a21": "https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L9-L13",
        "s42c9a65f2ad7": "https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man7/openssl-env.pod#L289-L298"
      }
    },
    "argon-api": {
      "name": "argon2-cffi API example",
      "basis": "25.1.0",
      "sources": {
        "s193f86db0a79": "https://github.com/hynek/argon2-cffi/blob/25.1.0/README.md#L11-L28"
      }
    },
    "render": {
      "name": "Render documentation",
      "basis": "unknown",
      "sources": {
        "s1820ac471b6c": "https://render.com/docs/web-services"
      }
    },
    "heroku": {
      "name": "Heroku documentation",
      "basis": "unknown",
      "sources": {
        "s370d4beec29a": "https://devcenter.heroku.com/articles/runtime-principles",
        "s211f5fe76042": "https://devcenter.heroku.com/articles/generations",
        "s0c5bf300cef4": "https://devcenter.heroku.com/articles/http-routing"
      }
    },
    "fly-pinned": {
      "name": "Fly.io pinned documentation",
      "basis": "2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9",
      "sources": {
        "s62fec91543a1": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42",
        "s61c1e50d2c11": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92",
        "s254c8c8a5edd": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97",
        "s32999aa4c58c": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176"
      }
    },
    "railway": {
      "name": "Railway documentation",
      "basis": "72354493198302677fb6be6c692dd75c64cae2c6",
      "sources": {
        "sac1383056b65": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146",
        "s0462eef65b1b": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51",
        "sa9d326046a7f": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43"
      }
    }
  },
  "claims": {
    "bind": {"text": "This guide advises loopback for same-host TLS proxies, no extra managed listeners, and wildcard only for authenticated direct TLS or private TLS ingress; app auth remains required. Railway advises 0.0.0.0 on injected PORT; its edge proxy terminates TLS. Rules vary by deployment (Fir Private Spaces: IPv6/dual-stack recommended; Fly without handlers: TCP passthrough); Cedar's address is not established.", "components": ["gunicorn", "uvicorn", "render", "heroku", "fly-pinned", "railway"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9", "render:s1820ac471b6c", "heroku:s370d4beec29a", "heroku:s211f5fe76042", "heroku:s0c5bf300cef4", "fly-pinned:s62fec91543a1", "fly-pinned:s61c1e50d2c11", "fly-pinned:s254c8c8a5edd", "fly-pinned:s32999aa4c58c", "railway:sac1383056b65", "railway:s0462eef65b1b", "railway:sa9d326046a7f"], "status": "REASONED"},
    "flask-tls": {"text": "Flask development server binds 127.0.0.1:8443 with cert/key ssl_context; adhoc requires cryptography and remains development-only.", "components": ["werkzeug"], "sources": ["werkzeug:sd5066c63a3ca"], "status": "REASONED"},
    "gunicorn-tls": {"text": "Gunicorn binds 0.0.0.0:8443 with --certfile and --keyfile for direct TLS.", "components": ["gunicorn"], "sources": ["gunicorn:s72daf362300c"], "status": "REASONED"},
    "uvicorn-tls": {"text": "Uvicorn binds 0.0.0.0:8443 with --ssl-certfile and --ssl-keyfile for direct TLS.", "components": ["uvicorn"], "sources": ["uvicorn:s02429a4a09d9"], "status": "REASONED"},
    "django-redirect": {"text": "Set SECURE_SSL_REDIRECT=True.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-proxy": {"text": "Set SECURE_PROXY_SSL_HEADER only behind a trusted proxy that strips and replaces X-Forwarded-Proto; prevent direct bypass.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-cookies": {"text": "Set SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE true.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "django-hsts": {"text": "Begin HSTS at 3600 seconds and include-subdomains false; raise duration and scope only after valid HTTPS is confirmed.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "deploy-check": {"text": "Run manage.py check --deploy and fix its findings.", "components": ["django"], "sources": ["django:s7289e1c111ae"], "status": "REASONED"},
    "password": {"text": "Keep Django's built-in hashing; do not replace it with custom code (guide advice). For Flask/FastAPI apps implementing local password accounts, this guide advises account storage and argon2-cffi or bcrypt under authentication.md's constraints; argon2-cffi 25.1.0's PasswordHasher.verify raises VerifyMismatchError on mismatch, and these APIs do not establish framework user-store capabilities.", "components": ["django", "argon", "argon-api", "bcrypt-api"], "sources": ["django:s7289e1c111ae", "argon:sff2b9a487e67", "argon-api:s193f86db0a79", "bcrypt-api:s340a2923b6da"], "status": "REASONED"},
    "secrets": {"text": "Generate secrets.token_urlsafe(32) and load secrets from the environment (guide advice); 32 counts random input bytes and is this guide's example choice, not a universal size. CPython v3.14.8 uses DEFAULT_ENTROPY (32 bytes) when omitted or None, but that default may change, including in maintenance releases.", "components": ["django", "stdlib-docs", "cpython-secrets"], "sources": ["django:s7289e1c111ae", "stdlib-docs:s971d128efc65", "stdlib-docs:sdad376a711c3", "cpython-secrets:s31e1a792a6b1", "cpython-secrets:s7cc14a5ebfa0", "cpython-secrets:sdef0e1600064"], "status": "REASONED"},
    "credential-extraction": {"text": "FastAPI security helpers extract credentials and declare schemes; presence/scheme checks do not verify signature, issuer, audience or expiry.", "components": ["fastapi"], "sources": ["fastapi:s077aff608a5c"], "status": "REASONED"},
    "oidc": {"text": "OpenIdConnect is a stub and does not use its discovery URL; validate extracted tokens with an OIDC library and authorize separately.", "components": ["fastapi", "oidc-stub"], "sources": ["fastapi:s077aff608a5c", "oidc-stub:s876e3d51e7ac"], "status": "REASONED"},
    "login-limit": {"text": "Rate-limiting login routes and a proxy-level limit are this guide's advice. slowapi v0.1.10 documents limits for Starlette/FastAPI HTTP endpoints; endpoints using its limit decorator must take an explicit request argument, and WebSocket endpoints are not supported.", "components": ["fastapi", "slowapi"], "sources": ["fastapi:s077aff608a5c", "slowapi:sf150aa58aa31", "slowapi:s4ca3e1e80817"], "status": "REASONED"},
    "mfa": {"text": "Use pyotp and qrcode, django-otp for Django, or linked MFA guidance.", "components": ["django", "pyotp", "qrcode", "django-otp"], "sources": ["django:s7289e1c111ae", "pyotp:sc118b8ed3bdd", "qrcode:s8247ddfed3d3", "django-otp:sa5c0f7097219"], "status": "REASONED"},
    "client-validation": {"text": "Never ship requests/httpx verify=False or ssl._create_unverified_context; HTTPX documents verify=False and CPython defines _create_unverified_context. The prohibition is this guide's advice.", "components": ["python", "requests", "httpx", "cpython-ssl"], "sources": ["python:s8fae94406709", "requests:s17c5a0a7ffb2", "httpx:s928d85a8d13e", "cpython-ssl:s4a1cd173d596"], "status": "REASONED"},
    "client-ca": {"text": "CPython's ssl reports OpenSSL default verify paths and environment-variable names. With no CA specified and verification enabled, create_default_context tries default CAs; loading may fail silently. This guide's inference: the call uses SSL_CERT_FILE/SSL_CERT_DIR if OpenSSL behaves as cited. This guide's assessment: linked OpenSSL may differ; platform stores and deployed use remain unverified.", "components": ["cpython-ssl", "openssl"], "sources": ["cpython-ssl:sbac049853cda", "cpython-ssl:s6dcc06feaaaf", "cpython-ssl:s4d7f143c9456", "cpython-ssl:s79d6191e12eb", "cpython-ssl:s82c72b9a971a", "cpython-ssl:sdf61ba8e79a7", "cpython-ssl:s2d42808e6cad", "openssl:s592eb65718de", "openssl:sfd19784d8a21", "openssl:s42c9a65f2ad7"], "status": "REASONED"},
    "client-ca-httpx": {"text": "HTTPX 0.28.1's transport passes verify and trust_env to create_ssl_context, which reads SSL_CERT_FILE when verify=True and trust_env=True; its SSL guide contradicts that source. Its environment guide says environment variables are used by default but does not list SSL_CERT_FILE.", "components": ["httpx"], "sources": ["httpx:s52608d6c5e47", "httpx:sd33b79237122", "httpx:s3734fbccdf40", "httpx:s30dd14bf172e", "httpx:s4a1f3b43f184", "httpx:sc5a61a9b2f64"], "status": "REASONED"},
    "client-ca-advice": {"text": "REQUESTS_CA_BUNDLE selects a requests CA. OpenSSL openssl-4.0.3 honours SSL_CERT_FILE/SSL_CERT_DIR for its default CA file/directory except in set-user-ID/set-group-ID executables. This guide's advice: use the exports for requests, the stated HTTPX path and CPython's qualified default-path call, or an explicit context for other configurations.", "components": ["requests", "httpx", "cpython-ssl", "openssl"], "sources": ["requests:s21c6be6f6df4", "httpx:s3734fbccdf40", "httpx:s30dd14bf172e", "httpx:s4a1f3b43f184", "httpx:sc5a61a9b2f64", "cpython-ssl:s6dcc06feaaaf", "cpython-ssl:s4d7f143c9456", "cpython-ssl:sdf61ba8e79a7", "openssl:s592eb65718de", "openssl:sfd19784d8a21", "openssl:s42c9a65f2ad7"], "status": "REASONED"},
    "http-server-bind": {"text": "As of Python 3.14.4, http.server binds every interface by default; explicitly bind 127.0.0.1:8000.", "components": ["python-pin"], "sources": ["python-pin:s0038729960a0", "python-pin:sa3111578d65d"], "status": "REASONED"},
    "http-server-files": {"text": "http.server serves the current directory and follows symlinks outside it; it is unsuitable for production. Share only a non-private directory through an SSH tunnel.", "components": ["python"], "sources": ["python:s8fae94406709"], "status": "REASONED"},
    "verify-tls": {"text": "Public HTTPS must succeed without -k; certificate, chain, hostname and trust failures need investigation.", "components": ["gunicorn", "uvicorn"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "A real protected route denies no credentials with 401/403 and accepts valid file-supplied credentials with 2xx; logs or direct probing distinguish app from proxy enforcement.", "components": ["django", "fastapi"], "sources": ["django:s7289e1c111ae", "fastapi:s077aff608a5c"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for loopback behind a same-host proxy or the required managed-ingress address and port.", "components": ["gunicorn", "uvicorn"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
