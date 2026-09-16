# Gradio: launch() authentication and TLS

Gradio binds to `127.0.0.1` by default. Two launch choices create exposure: `server_name="0.0.0.0"` (all interfaces) and `share=True` (a public `*.gradio.live` URL through Gradio's relay). Neither is acceptable without authentication.

## 1. Require a login

`launch()` takes credentials directly:

```python
import os
demo.launch(
    auth=(os.environ["GRADIO_USER"], os.environ["GRADIO_PASS"]),
    auth_message="Authorized users only",
)
```

`auth` also accepts a list of `(user, password)` tuples or a callable `f(username, password) -> bool`, which lets you check hashed credentials per [authentication.md](authentication.md). Keep the credentials in environment variables, not in the script.

MFA: `auth` is single-factor. The callable form allows a TOTP step (for example, verify a [pyotp](https://github.com/pyauth/pyotp) code appended to the password); fronting the app with Cloudflare Access or an Authelia-protected proxy is the cleaner route. Options in [mfa.md](mfa.md).

## 2. Enable TLS

For a public deployment, prefer a reverse proxy or tunnel in front of a loopback-bound Gradio app: [caddy.md](caddy.md), [nginx.md](nginx.md), or [cloudflare.md](cloudflare.md). Gradio can also serve HTTPS itself with a certificate from [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md):

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=8443,
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

## 5. Verify

```bash
ss -tlnp   # read every listener; loopback unless deliberately exposed
curl -q -sI https://gradio.example.com/        # succeeds over TLS
# In a private browser window: the login form appears before the app.
```

While signed in, create two harmless marker files in a directory you added to `allowed_paths`, list one of them in `blocked_paths`, then request each over `/gradio_api/file=` (with any deployment URL prefix): the allowed marker returns and the blocked one is refused. Confirm both files exist first, since a missing file or a login prompt does not show that `blocked_paths` is enforcing.

## Sources (checked September 2026)

- Gradio Blocks.launch() parameters (auth, auth_message, ssl_certfile, ssl_keyfile, ssl_keyfile_password, ssl_verify, server_name, share): https://gradio.app/docs/gradio/blocks
- Gradio file access (the `/gradio_api/file=` route; the default set is `set_static_paths`, `allowed_paths`, and the cache, and a path the app returns is also served if it is in `allowed_paths`, the working directory, or the temp directory; `blocked_paths` precedence; the cache is shared across all users): https://www.gradio.app/guides/file-access
