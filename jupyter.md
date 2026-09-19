# Jupyter: password and TLS

An exposed Jupyter server is remote code execution for whoever finds it. Jupyter Server (which also runs JupyterLab and Notebook 7) ships with authentication on (a random token) and binds to localhost; keep authentication enabled and the loopback bind when you change anything else. Setting a password (step 1) replaces the auto-generated token by default, so the requirement is that SOME native credential stays in force, not the token specifically; a token and a password can coexist as alternatives, but neither is a second factor. For multi-user or internet-facing use, prefer JupyterHub or access through [cloudflare.md](cloudflare.md) over exposing a single server directly.

## 1. Generate the config and set a password

```bash
jupyter server --generate-config     # writes ~/.jupyter/jupyter_server_config.py
jupyter server password              # prompts; stores the hashed password in jupyter_server_config.json
```

## 2. Enable TLS

Get a certificate per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md), then in `~/.jupyter/jupyter_server_config.py`:

```python
c.ServerApp.certfile = '/absolute/path/to/cert.pem'
c.ServerApp.keyfile  = '/absolute/path/to/key.pem'
```

Or per invocation:

```bash
jupyter lab --certfile=/path/cert.pem --keyfile=/path/key.pem
```

Once TLS is on, connect via `https://`; the server no longer answers plain `http://` usefully.

## 3. Exposure rules

- Do not set `c.ServerApp.ip = '0.0.0.0'` (or `--ip 0.0.0.0`) without the password from step 1 **and** TLS from step 2 in place.
- Never leave the server with neither a token nor a password: blanking both to make the login prompt go away is exactly the configuration internet scanners look for. Disabling the token when a password is set is fine (the password still authenticates); disabling both is not.
- A reverse proxy with its own auth ([nginx.md](nginx.md), [caddy.md](caddy.md)) or Cloudflare Access ([cloudflare.md](cloudflare.md)) in front of a loopback-bound Jupyter is a sound alternative to native TLS. It adds a second factor only if the Access policy or identity provider behind it is configured to require one; fronting alone does not.
- MFA: the Jupyter password is single-factor, so the fronting options above are where the second factor comes from; multi-user deployments on JupyterHub can delegate login to an OIDC/OAuth provider that enforces MFA. Options in [mfa.md](mfa.md).

## 4. Verify

```bash
# 1) TLS: the server answers over https and the certificate verifies. For a public-CA certificate use
# the normal trust store (drop --cacert); for a private CA pass that CA's bundle; for a self-signed
# certificate pass the cert from step 2. Request the host by the name the certificate carries. Never -k
# (it accepts any certificate, so the check would pass against a substituted one and prove nothing).
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null \
  -w 'tls=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --cacert /path/cert.pem https://jupyter.example.com:8888/
# 2) Auth: an https GET of / does not prove the API is protected (a fronting proxy can guard the UI while
# /api stays open, and an open server still serves /). Probe a PROTECTED API route both ways through the
# ACTUAL external URL. Native Jupyter answers a missing or invalid token on /api/kernels with 403 (not
# 401; a few routes such as /api/spec.yaml redirect to login instead); a valid token returns JSON. The
# token is fed to curl on stdin (-H @-); the one on the set -- line enters shell history, so use a
# short-lived token and clear that line after. A password-only server (step 1) issues NO token, so for
# this probe either configure one alongside the password (`c.IdentityProvider.token = '<random>'`, or
# `--IdentityProvider.token`), or run the positive control in the browser: log in with the password,
# then load /api/kernels and confirm it returns the kernel JSON.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_TOKEN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the token on the set -- line above; not probing"; exit 1 ;; esac
  u=https://jupyter.example.com:8888/api/kernels
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-token=%{http_code} exit=%{exitcode}\n' --cacert /path/cert.pem "$u"
  printf 'Authorization: token %s\n' "$1" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\nwith-token=%{http_code} exit=%{exitcode}\n' -H @- --cacert /path/cert.pem "$u"
)
# Expected: no-token => 403 (a 200 returning a kernel list is the finding: the API is open); with-token
# => 200 and a JSON kernel list (the positive control). A transport error (exit != 0) is inconclusive.
# In a clean browser profile (or a private window) with NO existing Jupyter cookies, and a URL that
# carries no ?token=, the server must demand the password or token before any notebook loads; an
# existing session cookie legitimately skips the prompt, so a reused window is not a valid test.
ss -tlnp   # a listener inventory in THIS namespace, not a firewall or forwarding check: the default
           # binds loopback (IPv4 127.0.0.1 and/or IPv6 ::1) and the port starts at 8888 but can differ
           # (config or a retry), so find the actual jupyter process and confirm no non-loopback bind,
           # then, since a reverse proxy in front can still publish it, probe the port from another host.
```

## Sources (checked September 2026)

- Jupyter Server public server guide: https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html
- Jupyter Server security (token/password authentication): https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- Jupyter Server API base handler (an unauthenticated request to a protected `/api` route is answered with 403 via `APIHandler.get_login_url`): https://github.com/jupyter-server/jupyter_server/blob/main/jupyter_server/base/handlers.py
- Jupyter Server configuration reference (`ServerApp`, `PasswordIdentityProvider.hashed_password`, `certfile`/`keyfile`, `ip`/`port`): https://jupyter-server.readthedocs.io/en/latest/other/full-config.html
- Migrating from the classic Notebook server (`NotebookApp` to `ServerApp`): https://jupyter-server.readthedocs.io/en/latest/operators/migrate-from-nbserver.html
- curl TLS verification (`--cacert`, hostname verification): https://curl.se/docs/sslcerts.html
