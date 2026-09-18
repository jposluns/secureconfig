# Gradio: launch() authentication and TLS

Gradio binds to `127.0.0.1` by default. Two launch choices create exposure: `server_name="0.0.0.0"` (all interfaces) and `share=True` (a public `*.gradio.live` URL through Gradio's relay). Neither is acceptable without authentication.

## 1. Require a login

`launch()` takes credentials directly:

```python
import os
demo.launch(
    server_name="127.0.0.1",   # bind loopback explicitly; if omitted it can inherit GRADIO_SERVER_NAME
    share=False,                # if omitted, share can inherit GRADIO_SHARE=True or auto-enable in Colab/hosted notebooks
    auth=(os.environ["GRADIO_USER"], os.environ["GRADIO_PASS"]),
    auth_message="Authorized users only",
)
```

`auth` also accepts a list of `(user, password)` tuples or a callable `f(username, password) -> bool`, which lets you check hashed credentials per [authentication.md](authentication.md). Keep the credentials in environment variables, not in the script.

MFA: `auth` is single-factor, with no rate limiting, login throttling, or automatic lockout. The callable form allows a TOTP step (for example, verify a [pyotp](https://github.com/pyauth/pyotp) code appended to the password), but a bare verification callback is not enough on its own: it needs secure enrollment, secret storage, and replay rejection. Fronting the app with Cloudflare Access or an Authelia-protected proxy is the cleaner route, but configure that service's own brute-force controls (Authelia regulation, Cloudflare rate limiting) and disable or separately protect any Gradio login you keep behind it, since fronting does not add throttling or lockout to the built-in login. Options in [mfa.md](mfa.md).

## 2. Enable TLS

For a public deployment, prefer a reverse proxy or tunnel in front of a loopback-bound Gradio app: [caddy.md](caddy.md), [nginx.md](nginx.md), or [cloudflare.md](cloudflare.md). Gradio can also serve HTTPS itself with a certificate from [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md):

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=8443,
    share=False,        # even for a TLS deployment: never implicitly share via GRADIO_SHARE or Colab
    ssl_certfile="/path/cert.pem",
    ssl_keyfile="/path/key.pem",
    ssl_verify=False,   # only for self-signed certificates; skips validating your own cert
    auth=(os.environ["GRADIO_USER"], os.environ["GRADIO_PASS"]),
)
```

`ssl_keyfile_password` exists for encrypted keys. `ssl_verify=False` here affects how the launcher checks its own certificate; it is needed for self-signed certificates and unnecessary with a CA-issued one.

## 3. share=True is publication

`share=True` publishes the app at a random public URL for anyone who obtains the link, with your machine executing the requests. Use it only for short demos, always combined with `auth`, and shut it down afterwards. It is not a deployment mechanism; for persistent authenticated remote access use [cloudflare.md](cloudflare.md).

## 4. Restrict file access

`launch()` serves files over a `/gradio_api/file=` route. By default it serves three things: static files you register with `gr.set_static_paths()`, the directories you list in `allowed_paths`, and Gradio's own cache. A path handed back through a file-based output component can be served too when it lies in `allowed_paths`, the current working directory, or the system temp directory; files Gradio caches this way are reachable by every user of the app, not only the one who produced it.

- The reliable control is an allowlist, not a blocklist of secrets. Launch from a directory that holds no `.env`, keys, or private source, and add only the directories users must download from to `allowed_paths` and `gr.set_static_paths()`, as absolute paths, each holding only public files, since a directory there exposes all of its files and subdirectories.
- `blocked_paths` takes precedence over the default set, `allowed_paths`, and `set_static_paths()`, but it is a blocklist: filesystem quirks, including case handling and NTFS alternate data streams, have enabled bypasses of path blocklists, so treat it as a backstop and keep Gradio on a current release.
- Never return untrusted user input through a file-based output component: Gradio can serve a returned path that lies in the working or temp directory, so a crafted value can hand back a file you did not mean to expose.
- Set `max_file_size` on `launch()` (bytes, or a string such as `"5mb"`); it defaults to `None`, which leaves uploads unlimited. It is a per-file limit, not a total-storage quota, so pair it with disk and rate controls at the proxy.

## 5. Verify

```bash
ss -tlnp   # 7860 loopback unless deliberately exposed. ss shows a local BIND only, and it CANNOT detect
           # a share=True tunnel: that keeps 7860 on loopback and opens an OUTBOUND frpc connection to
           # Gradio's relay publishing a *.gradio.live URL. Confirm share is off two ways, and if you
           # cannot confirm ALL THREE, treat it as UNKNOWN (not off): (1) the previous app process or
           # notebook kernel and its tunnel are terminated FIRST (a rerun with share=False in a persistent
           # kernel clears the URL but can leave the earlier tunnel connected), (2) share=False is set in
           # the launch() call, and (3) THIS fresh run's full startup output shows no "Running on public
           # URL: https://<name>.gradio.live" line (a shared run prints it in its startup output, so read the current
           # launch's output, not a stale log). If you know a former public URL, also confirm it is now
           # unreachable. Terminate any share tunnel after a demo.
# Auth, from OUTSIDE the deployment network: a served login page does NOT prove the API is gated. Probe a
# PROTECTED API route WITHOUT a Gradio session cookie; Gradio's own login_check returns 401. Keep the
# request otherwise identical to a real client, including any fronting-proxy authorization, so the ONLY
# thing removed is the Gradio cookie - then a 401 is Gradio's native auth, not the proxy. --noproxy so no
# client proxy answers; on a self-signed cert (section 2) add --cacert your-ca.pem (never -k); -D - shows
# the status and headers, not just the body. This example targets a fronting proxy at
# https://gradio.example.com; for a DIRECT section-2 TLS launch use https://gradio.example.com:8443, add
# any root_path prefix, and use the SAME base URL (host, port, prefix) for /login below:
curl -q -g -sS --noproxy '*' -D - -o /dev/null -w 'anon=%{http_code}\n' 'https://gradio.example.com/gradio_api/info'   # expect 401 from Gradio, never 200 with the app config (replace inside the quotes)
# Positive control: get a Gradio session cookie by POSTing your credentials to /login (form fields
# username and password), then re-request that same route WITH the cookie and confirm 200 with app
# content. Static assets are public, so test a protected route, not the home page. In a private browser
# the login form should appear before the app (necessary, not sufficient).
```

While signed in, create two harmless marker files with recognizable contents in a directory you added to `allowed_paths`, then request each over `/gradio_api/file=` (with any deployment URL prefix) and confirm BOTH return their marker contents. Only then add one to `blocked_paths` and restart. After the restart, log in again for a fresh session cookie (a restart resets Gradio's session tokens, so the old cookie now returns 401, which is a session failure, not a blocklist result) and confirm BOTH files still exist on disk with their contents (a restart can also clear a temp or cache directory, and a file that vanished returns the same 403 as a blocklist refusal), then request each with the fresh cookie: the blocked one must return 403 while the other still returns its contents. For a stronger check, remove it from `blocked_paths`, restart again, and confirm it serves once more. Establishing that both served their contents first, and that the blocked one still exists after the restart, is what distinguishes a `blocked_paths` refusal from a missing file, a wrong path, a login prompt, or a proxy denial (the `/gradio_api/file=` route returns the same refusal for several of these).

## Sources (checked September 2026)

- Gradio Blocks.launch() parameters (auth, auth_message, ssl_certfile, ssl_keyfile, ssl_keyfile_password, ssl_verify, server_name, share): https://gradio.app/docs/gradio/blocks
- Gradio file access (the `/gradio_api/file=` route; the default set is `set_static_paths`, `allowed_paths`, and the cache, and a path the app returns is also served if it is in `allowed_paths`, the working directory, or the temp directory; `blocked_paths` precedence; the cache is shared across all users): https://www.gradio.app/guides/file-access
- Gradio security advisories (the `/file=` path traversal and SSRF fixed in 4.11.0; the case-handling blocklist bypass) - historical, showing why a current release and an allowlist matter: https://github.com/gradio-app/gradio/security/advisories/GHSA-6qm2-wpxq-7qh2 and https://github.com/gradio-app/gradio/security/advisories/GHSA-j2jg-fq62-7c3h
