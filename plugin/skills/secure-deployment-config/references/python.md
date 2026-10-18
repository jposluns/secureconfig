---
version_basis: {
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "325223859acb920caba7e11658d3c3b87a9f7703faeab9e05b7641db8696fd48",
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
    },
    "stdlib-docs": {
      "name": "Python standard library documentation",
      "basis": "3.14",
      "sources": {
        "s971d128efc65": "https://docs.python.org/3.14/library/secrets.html",
        "sdad376a711c3": "https://docs.python.org/3.14/library/os.html#os.getenv"
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
    "cpython-ssl": {
      "name": "CPython ssl source and documentation",
      "basis": "v3.14.8",
      "sources": {
        "sbac049853cda": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L390-L405",
        "s6dcc06feaaaf": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L542-L548",
        "s4d7f143c9456": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L730-L736",
        "s4a1cd173d596": "https://github.com/python/cpython/blob/v3.14.8/Lib/ssl.py#L744-L754",
        "s79d6191e12eb": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L421-L433",
        "s82c72b9a971a": "https://github.com/python/cpython/blob/v3.14.8/Doc/library/ssl.rst#L1642-L1649"
      }
    },
    "openssl": {
      "name": "OpenSSL documentation",
      "basis": "openssl-4.0.3",
      "sources": {
        "s592eb65718de": "https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man3/SSL_CTX_load_verify_locations.pod#L39-L49"
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
        "sac1383056b65": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146"
      }
    },
    "argon-api": {
      "name": "argon2-cffi API example",
      "basis": "25.1.0",
      "sources": {
        "s193f86db0a79": "https://github.com/hynek/argon2-cffi/blob/25.1.0/README.md#L11-L28"
      }
    },
    "bcrypt-api": {
      "name": "Python bcrypt API example",
      "basis": "2b4ba9ac84df972e8e81311d09559af8dc82ef33",
      "sources": {
        "s340a2923b6da": "https://github.com/pyca/bcrypt/blob/2b4ba9ac84df972e8e81311d09559af8dc82ef33/README.rst#L62-L76"
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
    }
  },
  "claims": {
    "bind": {"text": "This guide advises loopback for same-host TLS proxies, no extra managed listeners, and wildcard only for authenticated direct TLS or private TLS ingress; app auth remains required. Rules vary (Fir Private Spaces: IPv6/dual-stack recommended; Fly without handlers: TCP passthrough); Railway address/injected port/TLS location and Cedar address remain uncited.", "components": ["gunicorn", "uvicorn", "render", "heroku", "fly-pinned", "railway"], "sources": ["gunicorn:s72daf362300c", "uvicorn:s02429a4a09d9", "render:s1820ac471b6c", "heroku:s370d4beec29a", "heroku:s211f5fe76042", "heroku:s0c5bf300cef4", "fly-pinned:s62fec91543a1", "fly-pinned:s61c1e50d2c11", "fly-pinned:s254c8c8a5edd", "fly-pinned:s32999aa4c58c", "railway:sac1383056b65"], "status": "REASONED"},
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
    "client-ca": {"text": "REQUESTS_CA_BUNDLE selects a requests CA. HTTPX 0.28.1's transport passes verify and trust_env to create_ssl_context, which reads SSL_CERT_FILE when verify=True and trust_env=True; its SSL guide contradicts that source. Its environment guide says environment variables are used by default but does not list SSL_CERT_FILE. CPython's ssl module reports OpenSSL default verify paths; with no CA specified and verification enabled, ssl.create_default_context() tries to load default CAs, which may fail silently. OpenSSL names SSL_CERT_FILE as an environment override for its default CA file; CPython's cited files do not name that variable, so whether a given ssl configuration uses it remains unverified. The export and explicit-context choices are this guide's advice.", "components": ["python", "requests", "httpx", "cpython-ssl", "openssl"], "sources": ["python:s8fae94406709", "requests:s21c6be6f6df4", "httpx:s52608d6c5e47", "httpx:sd33b79237122", "httpx:s3734fbccdf40", "httpx:s30dd14bf172e", "httpx:s4a1f3b43f184", "httpx:sc5a61a9b2f64", "cpython-ssl:sbac049853cda", "cpython-ssl:s6dcc06feaaaf", "cpython-ssl:s4d7f143c9456", "cpython-ssl:s79d6191e12eb", "cpython-ssl:s82c72b9a971a", "openssl:s592eb65718de"], "status": "REASONED"},
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

Metadata reviewed 2026-10-18; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- python: Python http.server documentation, 3.14.4
- gunicorn: Gunicorn documentation, unknown
- uvicorn: Uvicorn source, 5ac6265a01ff6dcadb0e4250152c3deaf8a168a9
- django: Django documentation, 6.1
- argon: argon2-cffi documentation, unknown
- werkzeug: Werkzeug documentation, unknown
- fastapi: FastAPI documentation, unknown
- oidc-stub: FastAPI OpenIdConnect source, 31bbb380748ccead62fc0f42dbf4273f11dadccf
- python-pin: Python http.server source, v3.14.4
- stdlib-docs: Python standard library documentation, 3.14
- pyotp: PyOTP, v2.9.0
- qrcode: qrcode, v8.2
- django-otp: django-otp, 1.6.1
- requests: Requests, v2.32.3
- slowapi: slowapi source, v0.1.10
- httpx: HTTPX source and documentation, 0.28.1
- cpython-ssl: CPython ssl source and documentation, v3.14.8
- openssl: OpenSSL documentation, openssl-4.0.3
- render: Render documentation, unknown
- heroku: Heroku documentation, unknown
- fly-pinned: Fly.io pinned documentation, 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9
- railway: Railway documentation, 72354493198302677fb6be6c692dd75c64cae2c6
- argon-api: argon2-cffi API example, 25.1.0
- bcrypt-api: Python bcrypt API example, 2b4ba9ac84df972e8e81311d09559af8dc82ef33
- cpython-secrets: CPython secrets documentation and source, v3.14.8

Claims (full source mapping in the front matter):

- bind (REASONED; gunicorn, uvicorn, render, heroku, fly-pinned, railway): This guide advises loopback for same-host TLS proxies, no extra managed listeners, and wildcard only for authenticated direct TLS or private TLS ingress; app auth remains required. Rules vary (Fir Private Spaces: IPv6/dual-stack recommended; Fly without handlers: TCP passthrough); Railway address/injected port/TLS location and Cedar address remain uncited.
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
- client-ca (REASONED; python, requests, httpx, cpython-ssl, openssl): REQUESTS_CA_BUNDLE selects a requests CA. HTTPX 0.28.1's transport passes verify and trust_env to create_ssl_context, which reads SSL_CERT_FILE when verify=True and trust_env=True; its SSL guide contradicts that source. Its environment guide says environment variables are used by default but does not list SSL_CERT_FILE. CPython's ssl module reports OpenSSL default verify paths; with no CA specified and verification enabled, ssl.create_default_context() tries to load default CAs, which may fail silently. OpenSSL names SSL_CERT_FILE as an environment override for its default CA file; CPython's cited files do not name that variable, so whether a given ssl configuration uses it remains unverified. The export and explicit-context choices are this guide's advice.
- http-server-bind (REASONED; python-pin): As of Python 3.14.4, http.server binds every interface by default; explicitly bind 127.0.0.1:8000.
- http-server-files (REASONED; python): http.server serves the current directory and follows symlinks outside it; it is unsuitable for production. Share only a non-private directory through an SSH tunnel.
- verify-tls (REASONED; gunicorn, uvicorn): Public HTTPS must succeed without -k; certificate, chain, hostname and trust failures need investigation.
- verify-auth (REASONED; django, fastapi): A real protected route denies no credentials with 401/403 and accepts valid file-supplied credentials with 2xx; logs or direct probing distinguish app from proxy enforcement.
- verify-bind (REASONED; gunicorn, uvicorn): Inspect every listener for loopback behind a same-host proxy or the required managed-ingress address and port.
<!-- version-basis:end -->

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
- Railway domains route to a detected or selected internal target port; the cited passage does not establish a required listener address, an injected `PORT` or the TLS termination location ([target ports](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146)).

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

HTTPX 0.28.1's SSL guide says `SSL_CERT_FILE` and `SSL_CERT_DIR` are not automatically used and shows an explicit context; its code path contradicts that: its sync and async transports pass `verify` and `trust_env` to `create_ssl_context`, which reads `SSL_CERT_FILE` when both are true. Its environment guide says environment variables are used by default but does not list `SSL_CERT_FILE`. This guide's advice: use the export above for that HTTPX code path; pass an explicit CA context for other configurations. With no CA specified and verification enabled, CPython's `ssl.create_default_context()` tries to load default CAs (CPython notes this may fail silently). `ssl.get_default_verify_paths()` reports OpenSSL's environment key for a CA file; OpenSSL names `SSL_CERT_FILE` as an override for its default CA file. CPython's cited files do not name `SSL_CERT_FILE`, so whether a given `ssl` configuration uses that override remains unverified.

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
- OpenSSL default CA file environment override (openssl-4.0.3, checked October 2026): https://github.com/openssl/openssl/blob/openssl-4.0.3/doc/man3/SSL_CTX_load_verify_locations.pod#L39-L49
- Requests verify=False disables certificate verification (v2.32.3, checked October 2026): https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L241-L243
- Render web-service listener and TLS termination (checked October 2026): https://render.com/docs/web-services
- Heroku HTTP routing (checked October 2026): https://devcenter.heroku.com/articles/http-routing
- Heroku web-process port assignment (checked October 2026): https://devcenter.heroku.com/articles/runtime-principles
- Heroku Fir Private Spaces networking and listener recommendation (checked October 2026): https://devcenter.heroku.com/articles/generations
- Fly TCP passthrough (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97
- Fly TLS termination (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176
- Fly public service binding (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42
- Fly IPv4 and IPv6 wildcard qualification (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92
- Railway target ports (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146
