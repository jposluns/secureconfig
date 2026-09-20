# Gradio: launch() authentication and TLS

Gradio binds to `127.0.0.1` by default. Two launch choices create exposure: `server_name="0.0.0.0"` (all interfaces) and `share=True` (a public `*.gradio.live` URL through Gradio's relay). Neither is acceptable without authentication.

At the time of writing, this guide targets **Gradio 6.28.0**, the recommended deployment baseline for these examples. Parameters and defaults were checked against the pinned source and vendor documentation in September 2026. Historical security fixes below explain why older minimum versions are insufficient. See the [6.28.0 release](https://github.com/gradio-app/gradio/releases/tag/gradio%406.28.0).

The launch examples are alternatives. Apply the relevant controls to your app's single `launch()` call, and configure its queue before launching.

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

For external authentication, `launch(auth_dependency=callback)` accepts a callback receiving a FastAPI request and returning a user ID for an authorized request or `None` to deny it. It cannot be combined with `auth`. Validate the identity provider's session or token in that callback; do not trust an identity header supplied directly by a caller. If a proxy supplies identity, it must remove caller-supplied identity headers, inject authenticated values, and be the only route to the backend. Enforce MFA, login throttling, lockout, and session lifetime at the identity provider or proxy. See the [launch reference](https://gradio.app/docs/gradio/blocks) and [authentication dependency and login handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

Native password login creates random bearer session tokens stored in the app process's memory. It issues an HttpOnly, Secure cookie and an HttpOnly insecure-cookie fallback; the server accepts either. There is **no server-side token expiry** in this native token store. Restarting the app clears its tokens, and the native `/logout` route revokes all sessions for the username by default (`all_session=True`). Browser cookie lifetime is not server-side revocation. Require HTTPS, prevent direct backend access, and enforce a finite session lifetime externally on every request; a copied native cookie must not bypass that external check. Inspect both cookies when configuring proxy cookie hardening. See the [native session implementation](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

## 2. Enable TLS

For a public deployment, prefer a reverse proxy or tunnel in front of a loopback-bound Gradio app: [caddy.md](caddy.md), [nginx.md](nginx.md), or [cloudflare.md](cloudflare.md). Gradio can also serve HTTPS itself with a certificate from [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md):

```python
import os
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

`ssl_keyfile_password` exists for encrypted keys. `ssl_verify=False` here affects how the launcher checks its own certificate; it is needed for self-signed certificates and unnecessary with a CA-issued one. Supply any key password through your secret manager or environment, not a literal in the script. See the [TLS parameters](https://gradio.app/docs/gradio/blocks) and [launcher certificate check](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py).

Behind a proxy, keep `server_name="127.0.0.1"` explicit. The argument defaults to `None`, resolving through `GRADIO_SERVER_NAME` to loopback when that variable is unset. If the proxy publishes the app beneath `/demo`, `root_path="/demo"` builds the corresponding URLs. It is **not an access control** and does not replace authentication or prevent direct access to the backend. See the [launch reference](https://gradio.app/docs/gradio/blocks).

## 3. share=True is publication

`share=True` publishes the app at a random public URL for anyone who obtains the link, with your machine executing the requests. Use it only for short demos, always combined with `auth`, and shut it down afterwards. It is not a deployment mechanism; for persistent authenticated remote access use [cloudflare.md](cloudflare.md).

Set `share=False` explicitly in the deployed launch call. When omitted, sharing can inherit `GRADIO_SHARE=True` or auto-enable in Colab and hosted notebooks. A loopback listener does not prove that a share tunnel is absent. See the [sharing defaults and launch behavior](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py).

## 4. Restrict file access

`launch()` serves files over a `/gradio_api/file=` route. By default it serves three things: static files you register with `gr.set_static_paths()`, the directories you list in `allowed_paths`, and Gradio's own cache. A path handed back through a file-based output component can be served too when it lies in `allowed_paths`, the current working directory, or the system temp directory; files Gradio caches this way are reachable by every user of the app, not only the one who produced it. Dotfiles in the working directory are excluded from automatic caching unless explicitly permitted. This exception does not justify storing secrets beside the app. See [file access](https://www.gradio.app/guides/file-access).

- The reliable boundary is a minimal filesystem available to the process, with narrowly scoped additional paths. `allowed_paths` **adds exposure**; it is not an exclusive sandbox. An empty list does not disable cache serving or eligible returned files. Launch from a directory that holds no `.env`, keys, or private source, and add only the directories users must download from to `allowed_paths` and `gr.set_static_paths()`, as absolute paths, each holding only public files, since a directory there exposes all of its files and subdirectories.
- `blocked_paths` takes precedence over the default set, `allowed_paths`, and `set_static_paths()`, but it is a blocklist: filesystem quirks, including case handling and NTFS alternate data streams, have enabled bypasses of path blocklists, so treat it as a backstop and keep Gradio on a current release.
- Never return untrusted user input through a file-based output component: Gradio can serve an eligible returned path that lies in the working or temp directory, so a crafted value can hand back a file you did not mean to expose. The working-directory dotfile exception does not protect other eligible files.
- Set `max_file_size` on `launch()` (bytes, or a string such as `"5mb"`); it defaults to `None`, which leaves uploads unlimited. It is a per-file limit, not a total-storage quota, so pair it with disk and rate controls at the proxy. **6.20.0 fixed missing enforcement on multipart `/component_server` uploads**; setting this argument on an older version is insufficient. Use the 6.28.0 baseline. See the [upload fix](https://github.com/gradio-app/gradio/releases/tag/gradio%406.20.0).

Both `allowed_paths` and `blocked_paths` default to `None` in 6.28.0. They fall back to the comma-separated `GRADIO_ALLOWED_PATHS` and `GRADIO_BLOCKED_PATHS` environment variables **even when passed `[]`**. Audit the environment of the actual service process. Remove unintended inherited values; when moving policy into explicit arguments, retain any required denies in `blocked_paths`. Do not assume an empty argument cleared an inherited grant or deny. See the [path resolution implementation](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py).

Set `GRADIO_TEMP_DIR` in the service environment before starting Gradio, for example:

```
GRADIO_TEMP_DIR=/srv/gradio-cache
```

Provision that absolute directory for the Gradio service account, with restrictive filesystem permissions such as mode `0700`, a storage quota, and an appropriate cleanup policy. Keep it separate from source, secrets, and other services' temporary data. This relocates Gradio's cache; it does **not** add per-user download authorization. Cached uploads and outputs remain readable by other app users who obtain their URLs. Filesystem permissions constrain other local accounts, not requests served by the Gradio process. See the [cache location and sharing rules](https://www.gradio.app/guides/file-access).

CVE-2023-51449, the historical `/file` traversal vulnerability, and the associated SSRF issue were fixed in **4.11.0**. That is a historical fix floor, not a deployment baseline. **6.16.0** includes FileExplorer traversal fixes. The case-handling advisory GHSA-j2jg-fq62-7c3h / CVE-2025-23042 remains a reason to distrust blocklists as the primary boundary; its patched-version records conflict, so this guide assigns it no precise fixed version. Use **6.28.0** as the baseline here. See the [historical traversal advisory](https://github.com/gradio-app/gradio/security/advisories/GHSA-6qm2-wpxq-7qh2), [case-handling advisory](https://github.com/gradio-app/gradio/security/advisories/GHSA-j2jg-fq62-7c3h), and [6.16.0 fixes](https://github.com/gradio-app/gradio/releases/tag/gradio%406.16.0).

## 5. Disable optional execution surfaces

Leave `GRADIO_VIBE_MODE` **unset** in production, and do not start the deployed app with `gradio --vibe`. Its default is the empty string, and the implementation tests string truthiness: **any non-empty value, including `"False"` or `"0"`, enables it**. The vibe-code handlers lack a native login check and allow source reading and modification; vibe mode permits arbitrary code execution on the host. Adding `auth` to ordinary app routes does not secure those handlers. See the [vibe-mode setting](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py), [vibe handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py), and [vendor development-only warning](https://gradio.app/guides/developing-faster-with-reload-mode).

Set `launch(mcp_server=False)` unless you deliberately publish MCP tools. Its default is `None`, which consults `GRADIO_MCP_SERVER`; that variable defaults to `"False"`. Enabling it exposes tools beneath `/gradio_api/mcp/`. If MCP is required, protect and test that surface separately. A 401 from `/gradio_api/info` does **not** establish MCP protection; this guide has not demonstrated MCP authentication behavior. See the [MCP setup implementation](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py) and [MCP documentation](https://gradio.app/guides/building-mcp-server-with-gradio).

API visibility is separate from authorization:

| Setting in Gradio 6.28.0 | Effect |
| --- | --- |
| `launch(footer_links=["gradio", "settings"])` | Omits the API documentation link. It does not disable the API. This replaces `launch(show_api=False)`. |
| Event listener `api_visibility="public"` | The default: documented and callable through Gradio clients. |
| Event listener `api_visibility="undocumented"` | Hides documentation while remaining callable. |
| Event listener `api_visibility="private"` | Hides documentation and blocks Gradio-client use. Direct HTTP requests can still invoke the function, subject to authentication and queue policy. |
| `api_name=None` | Derives an endpoint name from the function. It does not create an inaccessible endpoint. `api_name=False` is no longer a supported public argument. |

The migration guide's description of `"private"` as inaccessible must not be read as an HTTP authorization guarantee. The current reference describes the Gradio-client restriction, and the HTTP prediction handler checks login and queue policy separately. Native login checks protect `/config`, `/gradio_api/info`, prediction routes, and queue join/data routes when `auth` or `auth_dependency` is configured. Hiding a link or endpoint name does not replace those checks. See the [6.x migration guide](https://www.gradio.app/guides/gradio-6-migration-guide), [event reference](https://gradio.app/docs/gradio/button), and [HTTP handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

## 6. Bound queued work and close the direct-API bypass

Configure `demo.queue(api_open=False, default_concurrency_limit=1, max_size=20)` before launching, and set `max_threads=8` and `max_file_size="5mb"` on `launch()`. This complete, harmless example also applies the optional-surface and collection settings described in this guide:

```python
import os
import gradio as gr

def echo(text):
    return text

demo = gr.Interface(
    fn=echo,
    inputs="text",
    outputs="text",
    api_name="echo",
    flagging_mode="never",
    analytics_enabled=False,
)
demo.queue(api_open=False, default_concurrency_limit=1, max_size=20)
demo.launch(
    server_name="127.0.0.1",
    share=False,
    auth=(os.environ["GRADIO_USER"], os.environ["GRADIO_PASS"]),
    auth_message="Authorized users only",
    mcp_server=False,
    max_threads=8,
    max_file_size="5mb",
    run_history=False,
    footer_links=["gradio", "settings"],
)
```

Use the audited environment and isolated filesystem from sections 4 and 5, and publish through the authenticated HTTPS proxy from sections 1 and 2. Replace the echo function with the intended application.

At the time of writing, the 6.28.0 defaults and these illustrative limits are:

| Control | Default | Example |
| --- | --- | --- |
| `queue(api_open=...)` | Argument `None`; effective `True` off Hugging Face Spaces | `False` |
| `default_concurrency_limit` | `1` unless changed through `GRADIO_DEFAULT_CONCURRENCY_LIMIT` | `1` |
| `max_size` | `None`, no queue-size limit; ZeroGPU Spaces have a special default | `20` |
| `max_threads` | `40` | `8` |
| `max_file_size` | `None`, no upload-size limit | `"5mb"` |

`api_open=False` closes the direct `/gradio_api/run/` and `/gradio_api/api/` bypass **for queued functions**. It does not disable the queued API. Events configured with `queue=False` remain outside this boundary, so audit listener overrides. The default concurrency limit applies to listeners that use the default, not as one global request limit across every function; explicit listener concurrency settings can override it.

These numbers are illustrative capacity limits, not per-user quotas or rate limits. Apply request-rate, body-size, storage, and resource controls at the deployment layer as appropriate. A single authenticated caller can otherwise consume the available capacity. See the [queue and launch implementation](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py), [direct-request refusal](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py), and [launch reference](https://gradio.app/docs/gradio/blocks).

## 7. Restrict server-side URL fetching

Treat URL inputs as an outbound network surface. MCP file inputs accept URLs, and component processing can fetch remote resources. Gradio 6.28.0 has no general destination-allowlist argument covering every server-side fetch. Use deployment egress restrictions and application-controlled destination allowlists, including validation of redirects and resolved destinations. Do not let callers choose arbitrary remote apps or URLs for server-side fetching. Authentication limits who submits a URL; it does not make the destination safe. See the [MCP file behavior](https://gradio.app/guides/building-mcp-server-with-gradio), [component cache downloads](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py), and [launch reference](https://gradio.app/docs/gradio/blocks).

Current fetches are not all unprotected. **6.16.0** fixed SSRF in Image/Gallery SVG processing and Audio streaming processing. **6.20.0** changed `/gradio_api/file=<url>` from an open redirect to an SSRF-protected streaming proxy. Keep those protections and the 6.28.0 baseline; deployment egress policy provides the application-specific destination boundary. See the [6.16.0 fixes](https://github.com/gradio-app/gradio/releases/tag/gradio%406.16.0), [6.20.0 proxy change](https://github.com/gradio-app/gradio/releases/tag/gradio%406.20.0), and [current file route](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

For `gr.load(name, src=..., token=...)`, keep `name` and `src` under application control and load only trusted targets. The `token` can inherit `HF_TOKEN`; the current reference distinguishes model loading, which can also use a locally saved token, from Space loading. A token supplied to a loaded Space can be read by that Space. Do not pass a privileged token to an untrusted Space, and do not assume `token=None` universally means no credentials will be used. See the [load reference](https://gradio.app/docs/gradio/load).

## 8. Disable unnecessary persistent collection

Set `flagging_mode="never"` in **`gr.Interface(...)`**, as in section 6. This is the current spelling of `allow_flagging`; it is not a `launch()` argument. The default is resolved through `GRADIO_FLAGGING_MODE` and otherwise is `"manual"`. `"auto"` records every submission and its generated output. The default `CSVLogger` writes beneath `.gradio/flagged`, including saved file data for file-based components. Disable flagging when this collection is unnecessary, and apply an explicit retention and access policy where it is required. See the [Interface reference](https://gradio.app/docs/gradio/interface) and [flagging storage behavior](https://www.gradio.app/guides/flagging).

Consider `launch(run_history=False)`. In 6.28.0 its default is `None`, resolving through `GRADIO_RUN_HISTORY` to `True`. Run history stores runs privately in the browser by default; users can connect a Hugging Face bucket for subsequent runs. Disabling it stops recording, disables the history page, and removes previously saved browser history for that app. Do not assume this deletes separately retained bucket data or existing flagging files. See the [run-history reference](https://gradio.app/docs/gradio/blocks).

`analytics_enabled=False` belongs on `Blocks` or `Interface`, as shown in section 6. It disables basic telemetry and is separate from flagging and run history. Its default is `None`, resolving through `GRADIO_ANALYTICS_ENABLED` to `True`. This lower-priority privacy setting is not evidence that prediction inputs are sent as telemetry, and it does not establish that application logs or other integrations retain no inputs. See the [Blocks reference](https://gradio.app/docs/gradio/blocks) and [Interface reference](https://gradio.app/docs/gradio/interface).

## 9. Verify

These service checks are **reasoned, not demonstrated**. The authoring environment has no installed Gradio or container runtime, has restricted network access, and provides no authorized live Gradio deployment, second-host ingress fixture, or identity provider. Python syntax, Bash parsing, ShellCheck 0.11.0, and the repository's guard scan were checked locally; they do not demonstrate service behavior. `GRADIO-LIVE-1` below tracks the missing exposed/fixed comparisons.

Use a disposable private fixture for exposed comparisons, with harmless data and disposable credentials. Record the installed Gradio version, effective configuration, response content, and the layer issuing each refusal. Do not expose an unauthenticated or vibe-enabled comparison to the internet.

### Binding, sharing, TLS, and native login

**REASONED:** The deployment host and a live share-tunnel fixture are unavailable here. On the application host, inspect the listener and the current launch's complete startup output. An exposed fixture with `server_name="0.0.0.0"` should show an all-interface bind; the proxy-backed configuration should show loopback. A shared fixture should print its public URL and be reachable through it; the fixed fresh process must satisfy all three conditions below. See the [launch and sharing implementation](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py).

```bash
ss -tlnp   # With server_port=None, the port search starts at 7860 unless GRADIO_SERVER_PORT changes it.
           # Expect loopback unless deliberately exposed. ss shows a local BIND only, and it CANNOT detect
           # a share=True tunnel: that keeps the listener on loopback and opens an OUTBOUND frpc connection to
           # Gradio's relay publishing a *.gradio.live URL. Confirm share is off with all three checks, and if you
           # cannot confirm ALL THREE, treat it as UNKNOWN (not off): (1) the previous app process or
           # notebook kernel and its tunnel are terminated FIRST (a rerun with share=False in a persistent
           # kernel clears the URL but can leave the earlier tunnel connected), (2) share=False is set in
           # the launch() call, and (3) THIS fresh run's full startup output shows no "Running on public
           # URL: https://<name>.gradio.live" line (a shared run prints it in its startup output, so read the current
           # launch's output, not a stale log). If you know a former public URL, also confirm it is now
           # unreachable. Terminate any share tunnel after a demo.
```

**REASONED:** Native authentication and certificate checks require live HTTPS ingress and an outside client, unavailable here. A served login page does NOT prove the API is gated. Probe a protected API route WITHOUT a Gradio session cookie. With native authentication absent on the isolated comparison fixture, `/gradio_api/info` should return 200 with API information; with native authentication enabled, Gradio's own `login_check` should return 401. See the [protected info route and login check](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

Keep the request otherwise identical to a real client, including any fronting-proxy authorization, so the ONLY thing removed is the Gradio cookie - then a 401 can be attributed to Gradio's native auth, not the proxy. Supply proxy credentials from a protected header file using the helper below; never put them in command arguments. `auth_dependency` deployments need the separate external-auth comparison below.

Substitute the actual base URL inside the quotes. For a fronting proxy this might be `https://gradio.example.com`; for a direct section-2 TLS launch use the actual host with `:8443`. Include any `root_path` prefix, and use the SAME base URL (host, port, prefix) for `/login` below. Do not put credentials or signed URLs in the substitution. A literal apostrophe requires proper shell quoting. Paste whole blocks; the marker and count checks do not protect fragments pasted below their guards or shells with shadowed builtins.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_GRADIO_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one base URL; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute the actual base URL inside the quotes; not probing"; exit 1 ;;
    https://*)
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -D - -o /dev/null -w 'anon=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "${1%/}/gradio_api/info"
      ;;
    *) echo "use an HTTPS base URL; not probing"; exit 1 ;;
  esac
)
```

`--noproxy '*'` prevents a client proxy from answering. With a self-signed certificate from section 2, add `--cacert your-ca.pem` using your actual CA file, never `-k`. `-D -` shows status and headers rather than just the body. A TLS, DNS, or connection failure is not an authentication refusal.

Positive control: get a Gradio session cookie by POSTing your credentials to `/login` (form fields `username` and `password`), then re-request that same route WITH the cookie and confirm 200 with app content. Static assets are public, so test a protected route, not the home page. In a private browser the login form should appear before the app (necessary, not sufficient).

### Protected requests for the comparisons below

Prepare a mode-0600 header file in a private directory. For a signed-in request, include the native `Cookie:` header and any required proxy authorization. For the native anonymous comparison, retain proxy authorization and remove only Gradio's cookies. Use an empty file when no headers are required.

Prepare a separate protected body file: JSON for `POST`, URL-encoded `username` and `password` form fields for `LOGIN`, and an empty file for `GET`. Do not put credentials in shell history or enable shell tracing while handling them. The helper keeps response headers, bodies, and login cookies private because they can contain credentials.

**REASONED:** This helper's request outcomes require the live HTTPS fixture, unavailable here. Use it for the concrete exposed/fixed comparisons below. Its local parsing and guard checks do not establish those outcomes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENDPOINT_URL' 'GET' 'REPLACE_WITH_HEADER_FILE' 'REPLACE_WITH_BODY_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "provide endpoint, method, header file and body file; not probing"; exit 1; }
  case "|$1|$2|$3|$4|" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|*'||'*|*[[:cntrl:]]*)
      echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
  esac
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the endpoint; not probing"; exit 1 ;;
    https://*)
      [ -r "$3" ] || { echo "header file is unreadable"; exit 1; }
      [ -r "$4" ] || { echo "body file is unreadable"; exit 1; }
      umask 077
      set -- "$@" "$(mktemp -d)" || exit 1
      [ -d "$5" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Private response directory: %s\n' "$5"
      case "$2" in
        GET)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        POST)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -H 'Content-Type: application/json' --data-binary "@$4" \
            -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        LOGIN)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -H 'Content-Type: application/x-www-form-urlencoded' --data-binary "@$4" \
            -c "$5/cookies" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        *) echo "use GET, POST or LOGIN; not probing"; exit 1 ;;
      esac
      ;;
    *) echo "use HTTPS; not probing"; exit 1 ;;
  esac
)
```

The guard checks arguments, not file contents. Inspect request files before sending them. For the login positive control, use `LOGIN` against `/login`, then place the returned session cookie in the protected header file and use `GET` against `/gradio_api/info`. Add the actual CA file to these curl invocations when using a private CA. Preserve redacted evidence, then remove disposable accounts, uploads, credentials, and response files.

### File access and upload limits

**REASONED:** This requires a running Gradio with writable disposable marker directories and authenticated file downloads, unavailable here. Use the protected helper for each GET. The exposed and fixed outcomes follow the [file access rules](https://www.gradio.app/guides/file-access) and [authenticated file route](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py).

While signed in, create two harmless marker files with recognizable contents in a directory you added to `allowed_paths`, then request each over `/gradio_api/file=` (with any deployment URL prefix) and confirm BOTH return their marker contents. Only then add one to `blocked_paths` and restart. After the restart, log in again for a fresh session cookie (a restart resets Gradio's session tokens, so the old cookie now returns 401, which is a session failure, not a blocklist result) and confirm BOTH files still exist on disk with their contents (a restart can also clear a temp or cache directory, and a file that vanished returns the same 403 as a blocklist refusal), then request each with the fresh cookie: the blocked one must return 403 while the other still returns its contents. For a stronger check, remove it from `blocked_paths`, restart again, and confirm it serves once more. Establishing that both served their contents first, and that the blocked one still exists after the restart, is what distinguishes a `blocked_paths` refusal from a missing file, a wrong path, a login prompt, or a proxy denial (the `/gradio_api/file=` route returns the same refusal for several of these).

| Comparison | Request and expected exposed/fixed outcomes |
| --- | --- |
| Environment fallback and cache isolation | **REASONED:** Requires a live app, two test users, and disposable directories, unavailable here. Put a harmless directory outside the working, system-temp, and cache directories in `GRADIO_ALLOWED_PATHS`; with `allowed_paths=[]`, GET its marker through `/gradio_api/file=` and expect its contents. Unset that environment grant, restart, log in again, and require refusal while an intentionally allowed marker still serves. Separately upload a harmless file as user A, then GET its returned cache URL as user B. Moving `GRADIO_TEMP_DIR` should change storage location, but user B can still read the cached file. Inspect filesystem ownership and quota separately; cache relocation is not user isolation. See [path fallback](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py) and [shared cache](https://www.gradio.app/guides/file-access). |
| Upload size | **REASONED:** Requires a live file component and a component that sends multipart `/gradio_api/component_server` requests, unavailable here. Through the browser, upload valid harmless files below and above 5 MB and inspect the requests to `/gradio_api/upload` and, separately, `/gradio_api/component_server`. With `max_file_size=None`, both sizes should reach the applicable handler. With `"5mb"` on 6.28.0, the smaller file must still work and the larger must be refused for size. A malformed multipart body, absent component handler, or proxy rejection does not demonstrate Gradio's limit. Record the valid multipart fields from the actual component request. See the [6.20.0 enforcement fix](https://github.com/gradio-app/gradio/releases/tag/gradio%406.20.0) and [multipart handler](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py). |

### Optional surfaces, authorization, capacity, and collection

Use the protected request helper and the specified browser or MCP operations. Include the actual deployment prefix in every route.

| Comparison | Request and expected exposed/fixed outcomes |
| --- | --- |
| Vibe mode | **REASONED:** Requires a disposable development app with a readable demo source file, unavailable here. Without a Gradio cookie, GET `/gradio_api/vibe-code`. On an isolated fixture with `GRADIO_VIBE_MODE="False"`, the non-empty value enables the handler and it should return the source. Unset the variable, recreate the process, and require the handler's 403 response. A missing demo file is not evidence that vibe mode is disabled. Record the disabled setting for the write handlers too; do not probe source modification on the deployed app. See the [setting](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py) and [vibe handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py). |
| MCP | **REASONED:** Requires a working MCP client, Gradio's MCP dependency, and a harmless tool fixture, unavailable here. With MCP deliberately enabled on the private fixture, connect to `/gradio_api/mcp/`, list tools, and invoke the harmless tool successfully. Restart with `mcp_server=False`; that same connection must no longer list or invoke tools while ordinary authenticated app use still works. If publishing MCP, repeat with and without the intended authorization and require anonymous tool calls to be refused by the chosen protecting layer. `/gradio_api/info` is not this test. See [MCP operations](https://gradio.app/guides/building-mcp-server-with-gradio) and [conditional MCP setup](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py). |
| Visibility and native authorization | **REASONED:** Requires the live echo fixture, unavailable here. On the private comparison fixture, set `api_open=True` and POST `{"data":["GRADIO-LIVE marker"]}` to `/gradio_api/run/echo`. Changing visibility from `"public"` to `"undocumented"` or `"private"` must not be treated as HTTP denial: direct requests can still return the marker. Then require native auth and repeat without its cookie: expect 401. With a fresh cookie, require the marker again. Also compare GET `/config` and `/gradio_api/info`, and replay a valid browser `/gradio_api/queue/join` request with and without the native cookie. Malformed input is not an auth test. See the [event reference](https://gradio.app/docs/gradio/button) and [protected handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py). |
| Direct queue bypass and capacity | **REASONED:** Requires a live queued fixture and observable handler execution, unavailable here. With native authentication satisfied, POST the same echo JSON to `/gradio_api/run/echo` and `/gradio_api/api/echo`: with `api_open=True`, expect the marker; with `False` and the function queued, expect Gradio's direct-request refusal, HTTP 404. POST it to `/gradio_api/call/echo` and retrieve `/gradio_api/call/echo/EVENT_ID`, substituting the returned event ID, to confirm queued work still completes. For capacity, use a bounded slow harmless handler, keep one call running, and submit enough valid queued calls to fill 20 waiting slots; excess submissions should receive a queue-full refusal. Compare with the private fixture's unlimited queue, and record handler overlap with concurrency 1 versus a deliberately higher listener limit. Inspect `max_threads=8` and listener overrides separately; a queue-full response does not demonstrate a per-user quota or the thread ceiling. See [queue controls](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py) and [queue/direct handlers](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py). |
| External auth, prefix, and session lifetime | **REASONED:** Requires HTTPS ingress, a trusted proxy/IdP, two native sessions for one test username, and a second-host backend-access fixture, unavailable here. GET `/config` beneath the deployment prefix: an external-auth callback returning a user ID should permit it; a callback returning `None` should produce 401. Forged identity headers and direct backend access must not bypass the chosen boundary. For native auth, create two sessions using POST `/login`, confirm both can GET `/gradio_api/info`, then GET `/logout` with one session: both old cookies must subsequently fail. Recreate sessions and restart to check token invalidation separately. Inspect both login cookies' attributes. Before external lifetime enforcement, a retained native token has no server expiry; after the configured external lifetime, the same public request must be denied by that external layer until reauthentication, while a fresh authorized session works. Test the configured login-throttling threshold with disposable credentials and proxy/IdP logs. `root_path` only changes the request prefix. See [native sessions and callback handling](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py) and [root_path](https://gradio.app/docs/gradio/blocks). |
| Outbound destinations | **REASONED:** Requires controlled allowed and denied destination servers, egress logs, and the relevant file/MCP components, unavailable here. Submit a valid allowed URL through each used fetch surface, including GET `/gradio_api/file=` followed by its encoded URL, and require the expected marker bytes. Repeat with a controlled destination outside the application's allowlist and with a redirect to it. Before application-specific restrictions, a controlled public destination can be fetched; after enforcement it must receive no request, while the allowed control still succeeds. Inspect destination and egress logs, not just HTTP errors. For MCP, invoke the actual file-input tool with those URLs. Never use real metadata services as probes. These comparisons test application destination policy, not a claim that current Gradio fetches lack SSRF protection. See [MCP URL inputs](https://gradio.app/guides/building-mcp-server-with-gradio), [component fetch fixes](https://github.com/gradio-app/gradio/releases/tag/gradio%406.16.0), and [file proxy](https://github.com/gradio-app/gradio/releases/tag/gradio%406.20.0). |
| Flagging, history, and telemetry | **REASONED:** Requires a live Interface, disposable browser profile, file components, and observable storage/network activity, unavailable here. Submit a unique harmless marker. With `"manual"`, click Flag and require a CSV entry; with `"auto"`, require an entry without clicking, including saved file data where applicable. With `"never"`, require no new flagging record from the same submission. With `run_history=True`, make a browser submission and inspect `/gradio_api/runs`; after `False`, require recording and the history page to be disabled, while prediction still works. Inspect previous files and any connected bucket separately. Compare basic telemetry with `analytics_enabled=True` and `False`; do not infer prediction-input transmission from telemetry alone. See [flagging](https://gradio.app/docs/gradio/interface), [file storage](https://www.gradio.app/guides/flagging), and [history and analytics](https://gradio.app/docs/gradio/blocks). |

### Demonstration backlog

This row carries the original checks and the new controls together. Configuration inspection and local syntax checks do not close it.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| GRADIO-LIVE-1 | Demonstrate every REASONED comparison above on Gradio 6.28.0 with recorded dependency versions, disposable data, HTTPS ingress, a second host, native test users, proxy/IdP fixtures, an isolated vibe fixture, MCP tools, queued handlers, multipart components, controlled outbound destinations, and observable browser/server storage. Include share-tunnel termination; native versus proxy refusals; file-marker positive controls across restarts; environment fallback; shared-cache access; both upload routes; visibility versus HTTP authorization; direct queue bypass; capacity and thread behavior; external lifetime and logout/restart revocation; egress restrictions; flagging, history, and telemetry. Record requests, response content, positive controls, effective configuration, timestamps, and cleanup. | Open; service behavior is reasoned, not demonstrated. |

## Sources (checked September 2026)

- [Gradio Blocks.launch() parameters](https://gradio.app/docs/gradio/blocks): auth, auth_message, ssl_certfile, ssl_keyfile, ssl_keyfile_password, ssl_verify, server_name, and share; also auth_dependency, root_path, queue/launch limits, footer_links, run_history, and analytics.
- [Gradio file access](https://www.gradio.app/guides/file-access): the `/gradio_api/file=` route; the default set is `set_static_paths`, `allowed_paths`, and the cache; eligible returned paths in `allowed_paths`, the working directory, or the temp directory; working-directory dotfile exclusion; `blocked_paths` precedence; cache sharing across users; and `GRADIO_TEMP_DIR`.
- Gradio security advisories: [the `/file` traversal and SSRF fixed in 4.11.0](https://github.com/gradio-app/gradio/security/advisories/GHSA-6qm2-wpxq-7qh2) and [the case-handling blocklist bypass](https://github.com/gradio-app/gradio/security/advisories/GHSA-j2jg-fq62-7c3h). Historical evidence for keeping a current release and minimizing the process filesystem and additional allowed paths; no precise fix version is assigned here to the case-handling advisory.
- [Gradio 6.28.0 release](https://github.com/gradio-app/gradio/releases/tag/gradio%406.28.0).
- [Gradio 6.28.0 Blocks source](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/blocks.py): launch and queue signatures/defaults, off-Spaces api_open default, vibe-mode truthiness, path environment fallback, sharing behavior, component cache downloads, API names, and history settings.
- [Gradio 6.28.0 routes source](https://raw.githubusercontent.com/gradio-app/gradio/gradio%406.28.0/gradio/routes.py): login checks, native tokens/cookies/logout, auth_dependency, vibe handlers, conditional MCP setup, direct queue-bypass refusal, multipart limits, and SSRF-protected file streaming.
- [Gradio event reference](https://gradio.app/docs/gradio/button): api_visibility, api_name, queue, and listener concurrency.
- [Gradio 6 migration guide](https://www.gradio.app/guides/gradio-6-migration-guide): footer_links and the replacement event visibility API; read its visibility wording with the current reference and HTTP source.
- [Gradio development and vibe-mode warning](https://gradio.app/guides/developing-faster-with-reload-mode).
- [Gradio MCP server documentation](https://gradio.app/guides/building-mcp-server-with-gradio): tool publication, `/gradio_api/mcp/`, and URL file inputs.
- [Gradio 6.16.0 release](https://github.com/gradio-app/gradio/releases/tag/gradio%406.16.0): FileExplorer traversal and Image/Gallery SVG and Audio streaming SSRF fixes.
- [Gradio 6.20.0 release](https://github.com/gradio-app/gradio/releases/tag/gradio%406.20.0): multipart `/component_server` max_file_size enforcement and the SSRF-protected file streaming proxy.
- [Gradio load reference](https://gradio.app/docs/gradio/load): trusted targets, src, token, HF_TOKEN inheritance, and loaded-Space token disclosure.
- [Gradio Interface reference](https://gradio.app/docs/gradio/interface): flagging_mode, GRADIO_FLAGGING_MODE, CSVLogger, `.gradio/flagged`, and analytics_enabled.
- [Gradio flagging guide](https://www.gradio.app/guides/flagging): persistence of flagged inputs, outputs, and file data.
