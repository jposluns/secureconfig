# Jupyter: password and TLS

An unauthenticated Jupyter server gives anyone who can reach it arbitrary code execution with the permissions of its server and kernel processes. Running those processes with administrative privileges gives an authenticated attacker those privileges too. Jupyter Server ships with authentication on through a generated token; keep authentication enabled. Setting a password replaces the automatically generated token by default. A token and a password can coexist as alternatives, but neither is a second factor. [Jupyter Server security](https://jupyter-server.readthedocs.io/en/latest/operators/security.html).

Keep the default loopback bind when changing other settings. The Server examples below target Jupyter Server 2.18+, including the backend used by JupyterLab and Notebook 7. The multi-user examples target JupyterHub 5+ and belong in `jupyterhub_config.py`. Hub manages authentication for its single-user servers; the standalone password workflow below is for independently operated servers. [Server configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html), [Notebook configuration](https://jupyter-notebook.readthedocs.io/en/stable/configuring/config_overview.html), [Hub authenticators](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html).

## 1. Generate the config and set a password

Run these commands under the dedicated account that will operate the standalone server:

```bash
jupyter server --generate-config     # writes ~/.jupyter/jupyter_server_config.py
jupyter server password              # prompts; stores the hash in jupyter_server_config.json
```

The password command prompts without putting the password in process arguments. [Password setup](https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html).

### Require authentication for unclassified endpoints

**Tier 1; Jupyter Server 2.18+ baseline for this guide.**

An extension endpoint without an explicit authentication rule can expose functionality even when notebook and kernel routes require login. Add to `~/.jupyter/jupyter_server_config.py`:

```python
c.ServerApp.allow_unauthenticated_access = False
c.ServerApp.authenticate_prometheus = True
```

The first setting requires authentication for Jupyter handlers without an explicit public-access declaration. Explicitly public handlers remain public. Metrics have their own authentication setting. These controls do not establish that every third-party extension uses Jupyter's authentication machinery; review its routes separately. [Server API reference](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html#jupyter_server.serverapp.ServerApp.allow_unauthenticated_access).

At the time of writing, the configuration reference still lists `allow_unauthenticated_access` as `True`. Configure it explicitly. The changelog lists the feature under **2.13.0**, as well as repeating it under 2.18.0. Therefore, 2.18+ is this guide's conservative baseline, not the feature's introduction version. The configuration help's reference to a default in 2.0 is not a reliable introduction date. [Configuration reference](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html#ServerApp.allow_unauthenticated_access), [release history](https://jupyter-server.readthedocs.io/en/stable/other/changelog.html).

### Migration from older Notebook configurations

Existing examples in this guide already use `ServerApp`. When importing an older configuration, migrate the server settings and then apply the additional Server 2 authentication changes:

| Legacy setting | Current setting |
|---|---|
| `NotebookApp.ip`, `.certfile`, `.keyfile` | Corresponding `ServerApp.*` setting |
| `NotebookApp.password` / `ServerApp.password` | `PasswordIdentityProvider.hashed_password` |
| `NotebookApp.password_required` / `ServerApp.password_required` | `PasswordIdentityProvider.password_required` |
| `NotebookApp.token` / `ServerApp.token` | `IdentityProvider.token` |

Some vendor tutorials retain deprecated examples. Use the current reference for the final syntax. Supply credentials through the password prompt or protected configuration, never command-line arguments. [Notebook-server migration](https://jupyter-server.readthedocs.io/en/latest/operators/migrate-from-nbserver.html), [Server configuration reference](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html), [authentication API](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.auth.html).

## 2. Run the execution service without root privileges

**Tier 1; Jupyter Server. The root check applies on Unix-like systems.**

Run the standalone server and its local kernels under a dedicated, unprivileged operating-system account. In `~/.jupyter/jupyter_server_config.py`, keep root execution refused:

```python
c.ServerApp.allow_root = False
```

Do not bypass this with `--allow-root`. The setting refuses root startup; it does not change the process's account or sandbox notebook code. Grant the account only the filesystem and service access its notebooks require. Apply this privilege requirement to Hub user workloads separately from the privileges required by the selected spawner. [Server startup implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/serverapp.py).

If terminals are unnecessary, disable them:

```python
c.ServerApp.terminals_enabled = False
```

Notebook kernels can still execute shell commands. This removes an unused interface; it does not create an execution boundary. At the time of writing, the generated reference displays `False`, while the implementation dynamically defaults to `True`, subject to terminal availability. Configure it explicitly. [Terminal configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html#ServerApp.terminals_enabled), [implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/serverapp.py).

## 3. Enable TLS

Get a certificate per [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md), then in `~/.jupyter/jupyter_server_config.py`:

```python
c.ServerApp.certfile = '/absolute/path/to/cert.pem'
c.ServerApp.keyfile = '/absolute/path/to/key.pem'
```

Or per invocation:

```bash
jupyter server --certfile=/absolute/path/to/cert.pem --keyfile=/absolute/path/to/key.pem
```

Replace the paths with the actual certificate and private key. Once native TLS is enabled, connect using `https://`; that listener no longer serves ordinary plain HTTP. [Public-server TLS setup](https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html#using-ssl-for-encrypted-communication).

## 4. Exposure rules

- Do not set `c.ServerApp.ip = '0.0.0.0'` or use `--ip 0.0.0.0` without the password from step 1 and HTTPS from step 3 in place.
- Never leave the standalone server with neither a token nor a password. Disabling the token when a password is configured retains password authentication; disabling both removes native authentication.
- An **HTTPS reverse proxy with authentication** ([nginx.md](nginx.md), [caddy.md](caddy.md)) or HTTPS access through [cloudflare.md](cloudflare.md), in front of a loopback-bound server, is an alternative to native TLS. Authentication alone does not encrypt transport. [Jupyter HTTPS proxy example](https://jupyterhub.readthedocs.io/en/stable/howto/configuration/config-proxy.html).
- MFA: the Jupyter password is single-factor. Fronting authentication adds a second factor only when its policy or identity provider requires one. JupyterHub can delegate authentication to an appropriate provider that enforces MFA. Options are in [mfa.md](mfa.md).

### Preserve origin, XSRF, and Host checks

**Tier 1; Jupyter Server.**

Permissive browser-origin settings or disabled cross-site request forgery checks can let another website misuse an authenticated session. For a same-origin deployment, configure:

```python
c.ServerApp.allow_origin = ''
c.ServerApp.allow_origin_pat = ''
c.ServerApp.allow_credentials = False
c.ServerApp.disable_check_xsrf = False
```

Do not address browser or WebSocket errors by allowing every origin, using a permissive origin expression, or disabling XSRF checks. Cross-origin clients need a deliberately reviewed exception. [Server API reference](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html).

Preserve DNS-rebinding protection while allowing the deployment's actual hostname:

```python
c.ServerApp.allow_remote_access = False
c.ServerApp.local_hostnames = ['localhost', 'jupyter.example.com']
```

Replace `jupyter.example.com`. Setting `allow_remote_access = True` disables the Host check; adding a known hostname does not require it. This static hostname example is for a standalone server; Hub single-user servers need their actual generated hostnames accounted for. [Host-check configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html#ServerApp.allow_remote_access).

Token-authenticated requests bypass origin and XSRF checks by design. Use a cookie-authenticated session, without an authorization token, to test these browser-session protections. [Identity-provider implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/auth/identity.py), [request-handler implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/base/handlers.py).

## 5. Give Hub users individual identities and execution accounts

**Tier 1 for multi-user deployments; this example requires JupyterHub 5+ on Unix.**

A shared standalone credential lets users execute code with the same account's authority. Use JupyterHub with individual authentication and a separate single-user server for each account. A standalone server password does not provide user isolation. [Public-server scope](https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html).

For existing local Unix accounts, put this admission policy in `jupyterhub_config.py`:

```python
c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'
c.Authenticator.allow_all = False
c.Authenticator.allow_existing_users = False
c.Authenticator.allowed_users = {
    'REPLACE_WITH_USER_1',
    'REPLACE_WITH_USER_2',
}
c.PAMAuthenticator.allowed_groups = set()
c.JupyterHub.spawner_class = 'jupyterhub.spawner.LocalProcessSpawner'
```

Replace the user placeholders with actual Unix account names. Disabling `allow_existing_users` prevents historical Hub database membership from independently admitting users. An empty `allowed_groups` avoids another admission path through Unix group membership. Other authenticators can extend these rules and require their own review. [Authenticator API](https://jupyterhub.readthedocs.io/en/stable/reference/api/auth.html), [Hub 5 admission changes](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html#allowing-access).

`LocalProcessSpawner` requires matching local Unix accounts. Do not use `SimpleLocalProcessSpawner` in production: it provides no isolation between users. [Spawner API](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html), [Hub configuration reference](https://jupyterhub.readthedocs.io/en/stable/reference/config-reference.html).

Local processes are not containers, and `LocalProcessSpawner` does not enforce the generic CPU or memory limits. PAM does not automatically provide MFA; retain an explicitly configured MFA solution where required. [Spawner limitations](https://jupyterhub.readthedocs.io/en/stable/reference/spawners.html#spawners-resource-limits-and-guarantees-optional), [mfa.md](mfa.md).

## 6. Isolate Hub browser origins and protect server configuration

**Tier 1 for mutually untrusted users; JupyterHub. The combined example targets Hub 5+, and host-prefixed cookies require Hub 4.1+.**

Separate execution accounts do not separate browser origins. For mutually untrusted users, add to `jupyterhub_config.py`:

```python
c.JupyterHub.subdomain_host = 'https://jupyter.example.com'
c.JupyterHub.cookie_host_prefix_enabled = True
c.Spawner.disable_user_config = True
```

Replace the hostname. Provide DNS and valid HTTPS certificates for the Hub and every generated user hostname, commonly through wildcard DNS and suitable certificate coverage. Use a domain separated from sensitive applications. Hub documents no cross-user protection guarantee without per-user domains. Enable host-prefixed cookies with HTTPS and per-user domain separation. A default Hub is intended for semi-trusted users. [Hub security overview](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html), [cookie setting and version](https://jupyterhub.readthedocs.io/en/stable/reference/config-reference.html).

Keep the single-user server executable, Python environment, and launch path under administrator control. `disable_user_config` ignores user-home configuration, but users who can replace the server environment can circumvent it. Users may have separate writable kernel environments. These controls complement operating-system or container isolation. [Spawner API](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html#jupyterhub.spawner.LocalProcessSpawner.disable_user_config), [server environment isolation](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html#isolate-packages-in-a-read-only-environment).

## 7. Verify

**Service behaviour is REASONED, not demonstrated.** The authoring environment has no Jupyter Server, Notebook, or JupyterHub packages or executables, and no Docker or Podman. It has no available test deployment for the service checks below. These missing capabilities prevent exposed-versus-fixed demonstrations here; they do not waive local checks. Outstanding demonstrations are recorded in `JUPYTER-LIVE-1`.

Use an isolated test deployment for exposed configurations. Keep its versions, extensions, request paths, credentials, and test data consistent while changing the control under test. Never weaken a production deployment to create the exposed comparison. A rejection counts only when the positive control succeeds and the exposed comparison demonstrates that the request can reach the relevant functionality.

Paste complete Bash blocks. Substitute values **inside the single quotes** on each `set --` line; values containing a literal apostrophe require proper shell quoting. The guards assume genuine shell builtins. A fragment pasted below a guard is unguarded, and inherited arguments identical to the marker and expected values cannot be distinguished from a complete paste.

### TLS, anonymous access, and authenticated access

**REASONED: no Jupyter runtime or test deployment in the authoring environment.**

Use the actual external URL of `/api/kernels`, including any deployment prefix. The first request checks TLS and anonymous API access together. Use a URL without credentials or token query parameters.

Supply the actual CA bundle path: the system CA bundle for a public certificate, the private CA bundle for a private certificate, or the trusted certificate from step 3 for a self-signed deployment. Request the hostname covered by the certificate. Certificate verification must remain enabled. These commands use curl 7.75.0+ for `exitcode` and `errormsg`. [curl certificate verification](https://curl.se/docs/sslcerts.html), [curl options](https://curl.se/docs/manpage.html).

Leave the final value as `browser` for a password-only server. If a token is already configured, change it to `token`; Python prompts for it, and the shell feeds the authorization header to curl on stdin. Do not add a token merely to replace the password/browser positive control. The block disables shell tracing and avoids putting the token in shell history or curl arguments; it does not conceal credentials from the account owner or other session-recording mechanisms.

```bash
(
  set +x
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_HTTPS_URL' 'REPLACE_WITH_CA_BUNDLE' 'browser'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 1; }
  (
    while [ "$#" -gt 0 ]; do
      case "$1" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
        *[[:cntrl:]]*) echo "control character in input; not probing"; exit 1 ;;
      esac
      shift
    done
  ) || exit 1
  case "$1" in https://*) ;; *) echo "HTTPS URL required; not probing"; exit 1 ;; esac
  case "$1" in
    *'@'*|*'?'*|*'#'*|*' '*) echo "use a URL without credentials, query, fragment or spaces; not probing"; exit 1 ;;
  esac
  case "$2" in /*) ;; *) echo "absolute CA bundle path required; not probing"; exit 1 ;; esac
  [ -f "$2" ] || { echo "CA bundle is not a readable file; not probing"; exit 1; }
  [ -r "$2" ] || { echo "CA bundle is not a readable file; not probing"; exit 1; }
  case "$3" in browser|token) ;; *) echo "choose browser or token; not probing"; exit 1 ;; esac

  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
    *)
      # REASONED: no Jupyter runtime or test deployment in the authoring environment.
      # This request checks certificate validation AND anonymous API access.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" -w '\nanonymous=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"

      # Password-only deployments: perform the browser positive control described below.
      [ "$3" = token ] || exit 0
      set -- "$(python3 -c 'import getpass; print(getpass.getpass("Jupyter token: "))')" "$1" "$2"
      case "$1" in
        *REPLACE_WITH_*|*'<'*|*'>'*|"") echo "a real token is required; not probing"; exit 1 ;;
      esac
      case "$1" in
        *[[:cntrl:]]*) echo "token contains a control character; not probing"; exit 1 ;;
      esac
      # REASONED: no Jupyter runtime or test deployment in the authoring environment.
      printf 'Authorization: token %s\n' "$1" |
        curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
          --cacert "$3" --header @- \
          -w '\nauthenticated=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$2"

      # REASONED: no Jupyter runtime or test deployment in the authoring environment.
      # The deliberately wrong Host below is a non-secret test value, not the destination.
      printf 'Authorization: token %s\n' "$1" |
        curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
          --cacert "$3" --header @- --header 'Host: rebinding.example.com' \
          -w '\nwrong-host=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$2"
      ;;
  esac
)
```

**REASONED: no Jupyter runtime or browser session here.** In a clean browser profile, visit the same deployment without a token query or existing cookies. It must require authentication before loading a notebook. Log in with the configured password, then request the same `/api/kernels` URL: expect `200` with a JSON kernel list, including an empty list when no kernels are running. An existing session legitimately skips the login prompt. [Server authentication](https://jupyter-server.readthedocs.io/en/latest/operators/security.html), [kernels API](https://jupyter-server.readthedocs.io/en/stable/developers/rest-api.html).

Use these exposed-versus-fixed comparisons:

| Check | Exposed comparison | Fixed result and positive control |
|---|---|---|
| TLS | A known-running plaintext listener or a certificate failing trust/hostname validation cannot complete the validated HTTPS request. | HTTPS completes with `exit=0`. An HTTP error status can still accompany successful TLS. A connection failure alone proves no protection. |
| Native API authentication | With both native credentials absent in the isolated fixture, anonymous `GET /api/kernels` returns kernel JSON. | Anonymous access returns native `403`; authenticated access returns `200` and kernel JSON. |
| Fronting authentication | Demonstrate that the exposed external route returns kernel data anonymously. | Anonymous access yields no kernel data; a login redirect may replace native `403`. Complete all required login layers and obtain authenticated kernel JSON. |
| Host check | With `allow_remote_access = True` in the isolated fixture, the token-authenticated wrong-Host request reaches the kernel API. | With the step 4 settings, wrong Host is refused with native `403`, while the normal-Host token request succeeds. |

Native protected-API `403` and Host-check behaviour come from the [handler implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/base/handlers.py). If a fronting layer rejects the wrong Host in both states, that demonstrates its rejection only; the Server Host-check comparison remains outstanding.

### Metrics and extension routes

**REASONED: no Jupyter runtime, installed extension routes, or test deployment here.**

Repeat the guarded HTTPS block with the actual Server `/metrics` URL, then each installed extension's documented, read-only protected URL. Complete the authenticated positive control for every route. Metrics should return their expected metrics body after authentication, rather than kernel JSON. An absent route, login page, or generic error is not that positive control.

For the metrics comparison, set `authenticate_prometheus = False` only in the isolated exposed fixture: anonymous metrics should become available. Restore `True`: anonymous metrics should be refused and authenticated metrics should remain available. [Metrics handler](https://github.com/jupyter-server/jupyter_server/blob/main/jupyter_server/base/handlers.py).

To demonstrate `allow_unauthenticated_access`, identify an extension route using Jupyter's handler machinery without an explicit authentication decorator or public-access declaration. With `True`, its anonymous GET is permitted; with `False`, login is required and its authenticated response remains available. Record the actual route and expected body. If no such route is installed, this feature demonstration remains outstanding; testing an already protected kernel route does not replace it. Explicitly public routes require a separate review of whether their exposure is intentional. [Default authentication enforcement](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html#jupyter_server.serverapp.ServerApp.allow_unauthenticated_access).

### Cookie-session XSRF and origin checks

**REASONED: no Jupyter runtime, authenticated browser session, or test deployment here.**

Use a disposable standalone test server with a working default kernel. Authenticate through its password login and prepare two account-private files:

- A Netscape-format cookie jar containing that session's authentication and `_xsrf` cookies.
- A header file containing only `X-XSRFToken: ` followed by the matching `_xsrf` value.

Keep both files readable only by the testing account and remove them after testing. Do not put their contents on command lines. The header name is documented by [Tornado's XSRF protection](https://www.tornadoweb.org/en/stable/guide/security.html); curl supports cookie and header files. [curl options](https://curl.se/docs/manpage.html).

Set the base URL to the actual server URL, including any deployment prefix. Set the same-origin value to its scheme and authority, including a non-default port, with no path or trailing slash. Do not supply an authorization token: that would bypass the protection being tested.

```bash
(
  set +x
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SERVER_HTTPS_BASE_URL' 'REPLACE_WITH_CA_BUNDLE' \
    'REPLACE_WITH_COOKIE_JAR' 'REPLACE_WITH_XSRF_HEADER_FILE' 'REPLACE_WITH_SAME_ORIGIN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 5 ] || { echo "the set -- line needs exactly 5 values; not probing"; exit 1; }
  (
    while [ "$#" -gt 0 ]; do
      case "$1" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
        *[[:cntrl:]]*) echo "control character in input; not probing"; exit 1 ;;
      esac
      shift
    done
  ) || exit 1
  case "$1" in https://*) ;; *) echo "HTTPS base URL required; not probing"; exit 1 ;; esac
  case "$5" in https://*) ;; *) echo "HTTPS origin required; not probing"; exit 1 ;; esac
  case "$1$5" in
    *'@'*|*'?'*|*'#'*|*' '*) echo "use URLs without credentials, query, fragment or spaces; not probing"; exit 1 ;;
  esac
  case "$2" in /*) ;; *) echo "absolute CA bundle path required; not probing"; exit 1 ;; esac
  case "$3" in *'='*) echo "cookie file path must not contain =; not probing"; exit 1 ;; esac
  case "$3" in /*) ;; *) echo "absolute cookie file path required; not probing"; exit 1 ;; esac
  case "$4" in /*) ;; *) echo "absolute XSRF header file path required; not probing"; exit 1 ;; esac
  [ -f "$2" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  [ -r "$2" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  [ -f "$3" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  [ -r "$3" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  [ -f "$4" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  [ -r "$4" ] || { echo "a required file is unreadable; not probing"; exit 1; }
  set -- "${1%/}" "$2" "$3" "$4" "$5"

  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
    *)
      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Positive control: a live cookie session must retrieve kernel JSON.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" \
        -w '\ncookie-get=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Negative XSRF case: same session and origin, but no X-XSRFToken header.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" \
        --header 'Content-Type: application/json' --data-binary '{}' \
        -w '\nmissing-xsrf=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Positive XSRF control: creates a disposable kernel; record its returned id.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" --header "@$4" \
        --header 'Content-Type: application/json' --data-binary '{}' \
        -w '\nvalid-xsrf=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Wrong Origin, same authenticated session. This header is not a destination.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header 'Origin: https://cross-origin.example.com' \
        -w '\nwrong-origin=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"
      ;;
  esac
)
```

**REASONED: the same missing runtime and session prevent these comparisons here.**

| Check | Exposed comparison | Fixed result and positive control |
|---|---|---|
| XSRF | With `disable_check_xsrf = True` only in the isolated fixture, the same-origin POST without the XSRF header creates a kernel. | With `False`, missing XSRF produces `403`; the same session with the matching header creates a kernel with `201`. The cookie GET must also succeed. |
| Origin | With `allow_origin = '*'` only in the isolated fixture, the wrong-Origin cookie GET returns kernel JSON. | With the step 4 origin settings, the wrong-Origin API request is rejected; current native `APIHandler` uses `404`. The same-origin cookie GET returns `200` and kernel JSON. |

The POST body selects the default kernel, and successful creation returns `201`. [Kernel handler](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/services/kernels/handlers.py). XSRF and origin outcomes follow the [request-handler checks](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/base/handlers.py).

A `403` or `404` in both states proves nothing about the intended control. Inspect the response and server logs, and require the positive controls above. Curl does not enforce browser CORS rules: also inspect a cookie-authenticated browser request and confirm that the fixed deployment does not grant cross-origin access through `Access-Control-Allow-Origin` or `Access-Control-Allow-Credentials`. [Origin configuration](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html).

Record every kernel ID created in either state and shut down those disposable kernels through the authenticated UI. [JupyterLab kernel management](https://jupyterlab.readthedocs.io/en/stable/user/running.html).

### Execution privileges, terminals, and Hub separation

Each check below is **REASONED: Jupyter/JupyterHub runtimes and the required test accounts or browser sessions are unavailable here**.

| Check | Concrete demonstration to perform | Exposed versus fixed outcome |
|---|---|---|
| Execution account and root refusal | On an isolated Unix fixture, start `jupyter server` as UID 0 with the step 2 configuration. Compare with root execution explicitly allowed in that fixture. Start the fixed server under its unprivileged account. Inspect server/kernel ownership using `ps -eo pid,ppid,euid,egid,comm`; in a notebook evaluate `import os; print(os.geteuid())`. | The exposed root process can start; the fixed root launch refuses startup. The fixed unprivileged server starts and its local kernel has the intended nonzero UID. |
| Disabled terminals | With terminal support installed, request authenticated `/api/terminals` using the guarded HTTPS block before and after disabling terminals. Keep authenticated `/api/kernels` as the service positive control. | Enabled terminals provide their interface; disabled terminals do not. Kernel execution still works, including shell execution from notebook code. |
| Hub admission | Through `/hub/login`, test an allowed Unix account and a valid Unix account outside the allowlist, including an ordinary historical Hub database user. Establish the latter's valid credentials in the isolated permissive fixture. | Permissive admission accepts the extra account; the fixed policy refuses it while an allowed account can log in and start a server. |
| Hub execution accounts | Start servers for two admitted users. Compare their server process ownership and run `import os; print(os.geteuid())` in each local kernel. | A shared-account fixture uses the same authority; the fixed local-account deployment uses distinct intended Unix UIDs. |
| Hub browser origins and cookies | In each user's own server tab, inspect `location.origin`. Inspect Hub and single-user authentication cookies in browser developer tools. | A single-domain fixture shares an origin; fixed user servers have distinct HTTPS origins. Host-prefixed authentication cookies use the `__Host-` prefix, `Secure`, path `/`, and no `Domain` attribute. |
| Hub user configuration and environment | In a disposable user account, place `c.ServerApp.terminals_enabled = True` in its user configuration while the administrator disables terminals, then restart its server. Compare loading versus disabling user configuration. Check write permissions on the server executable, environment, and launch-path directories as that user. | The exposed fixture loads the user override or permits server replacement. The fixed deployment ignores the user configuration and denies writes to the administrator-controlled server environment; an ordinary notebook remains usable. |

Root refusal and terminal behaviour are documented in the [Server implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/serverapp.py). Hub comparisons follow its [admission rules](https://jupyterhub.readthedocs.io/en/stable/reference/api/auth.html), [local spawner behaviour](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html), [browser security requirements](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html), and [host-prefixed cookie configuration](https://jupyterhub.readthedocs.io/en/stable/reference/config-reference.html).

### Listener inventory and external reachability

**REASONED for the deployed service: no Jupyter runtime is available here.** The locally feasible inventory command was attempted, but the authoring sandbox reported `Cannot open netlink socket: Operation not permitted`. Its otherwise empty output is not evidence that no listeners exist.

```bash
ss -tlnp
```

Run this in the deployment's network namespace and identify the actual server listener. It inventories listeners; it does not test a firewall or forwarding. Confirm the intended loopback bind, then repeat the guarded HTTPS probe from another host against the actual external endpoint. In an exposed fixture, a listener published externally can answer; in the fixed private-backend arrangement, only the intended public entry point should be reachable. A backend timeout without a working public positive control is inconclusive.

The standalone port normally starts at 8888 but can change through configuration or port retries. Do not assume it from an example. [Server port implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/serverapp.py), [default port constant](https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/__init__.py).

### Verify the reverse-proxy path prefix

**REASONED:** no Jupyter Server, JupyterHub, or configurable-http-proxy is running in the authoring environment.

In an isolated fixture, compare the consistent-prefix configuration from section 8 against a deployment where only part of the stack carries the prefix. Request the prefixed application routes (for a standalone Server, `GET /jupyter/api/kernels`; for JupyterHub, `GET /jupyter/hub/login` and a spawned user's actual prefixed URL) and, separately, probe any unprefixed alias (`GET /api/kernels`, `GET /hub/login`). The fixed configuration keeps every application route behind the intended authentication and routing boundary and leaves no unprefixed alias serving the application, while a bare `404` proves neither authentication nor a working deployment, so confirm authenticated access and a working kernel WebSocket on the prefixed path as the positive control. See the [JupyterHub proxy configuration](https://jupyterhub.readthedocs.io/en/5.5.2/howto/configuration/config-proxy.html).

### Verify forwarded-header trust

**REASONED:** no Jupyter Server or JupyterHub behind a real ingress is available in the authoring environment.

Send separate and conflicting spoofed `X-Forwarded-For`/`X-Real-IP` and `X-Scheme`/`X-Forwarded-Proto` headers through the real ingress, and separately attempt to reach the backend directly from an untrusted network. Compare the request-derived client address in the logs, the redirect targets, and the cookie `Secure` attribute. In the exposed fixture (header trust enabled while the backend is reachable or the proxy passes headers through unchanged) the attacker-controlled address or scheme takes effect; in the fixed fixture (section 9: a private bind plus a sanitizing ingress) it does not, while a legitimate login and WebSocket still succeed. Include a spoofed `Forwarded: proto=http` header and compare the detected browser-facing scheme (the redirect target and any scheme-derived decision) between the sanitizing and the pass-through ingress. Because section 6 sets `cookie_host_prefix_enabled`, the single-user OAuth cookie stays `Secure` regardless, so a stripped-`Secure` cookie is demonstrable only in an isolated fixture with host-prefixed cookies disabled; with this guide's configuration, verify instead that the ingress removes or overwrites `Forwarded`. The host is a separate case: the forwarded-header machinery rewrites only the client address and scheme, not the host; the standalone Server's origin check reads the genuine `Host` header, and JupyterHub 5 ignores `X-Forwarded-Host` unconditionally (the `forwarded_host_header` trait is defined but no longer consumed), so confirm that a spoofed `X-Forwarded-Host` has no effect and test an unintended genuine `Host` value at the ingress instead. See the [JupyterHub configuration reference](https://jupyterhub.readthedocs.io/en/5.5.2/reference/config-reference.html) and the [Jupyter Server HTTP-server construction](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.18.0/jupyter_server/serverapp.py).

### Verify internal Hub TLS

**REASONED:** no JupyterHub, spawner, or single-user server is available in the authoring environment.

Keep the public HTTPS listener constant and compare internal TLS off against on (section 10). Inspect each actual internal connection (Hub to proxy API, proxy to Hub, proxy to single-user server, and Hub to single-user server): with internal TLS on, a request using the intended internal certificate authority and client certificate succeeds, while one presenting an untrusted certificate is rejected, and, on JupyterHub 5.4 or later (which enabled internal hostname verification by default), a connection under an incorrect server hostname is likewise rejected. Require a successful login, spawn, notebook execution, and kernel WebSocket exchange as positive controls. The single-user-server-to-kernel ZeroMQ connection must be observed separately and must not be counted as encrypted by this test, since `internal_ssl` does not cover it. See the [internal_ssl definition](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.2/jupyterhub/app.py) and the [Jupyter messaging protocol](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst).

### Verify NativeAuthenticator password and signup policy

**REASONED:** no JupyterHub with NativeAuthenticator installed, and no browser signup session, is available in the authoring environment. This check applies only to a Hub that uses NativeAuthenticator (section 11); a PAM deployment verifies its password policy on the host instead.

On an authorized Hub configured with the section 11 settings, exercise the signup form at `/hub/signup` and the login form, varying one control at a time. For the password rules, with the hardened configuration a signup password shorter than `minimum_password_length` or one present in the common-password list is rejected at the form, while with the shipped defaults (`minimum_password_length` and `seconds_before_next_try` effectively `0`, since their `.tag(default=...)` annotation is metadata rather than the trait default, and `check_common_password` `False`) even an empty password is accepted; confirm the rejection is the server's signup response, not a client-side hint. For lockout, after `allowed_failed_logins` consecutive failed logins for one account the next attempt within `seconds_before_next_try` is refused even with the correct password, whereas at the default `0` the attempts are never throttled. To exercise the approval hold in isolation from Hub admission, set `allow_all = True` with an empty `allowed_users` and sign up a fresh non-admin username: with `open_signup` off it is created unauthorized and cannot log in until an administrator approves it on `/hub/authorize`, whereas `open_signup = True` admits it at signup. Then confirm the reverse exposure by adding a not-yet-registered username to `allowed_users` and observing that its first signup is authorized immediately without approval. With `enable_signup = False`, a GET or an otherwise valid POST to the signup route is refused (HTTP 404) and creates no account, while with signup enabled the same form renders and accepts a valid registration. Inspect the stored record to confirm the password is held as a bcrypt hash, not reversible text. A wrong username, an unmigrated database, or a stale browser session is inconclusive. See the [NativeAuthenticator configuration](https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py).

### Local authoring checks and demonstration backlog

The following checks were run without editing files or running `tools/run_all_checks.sh`:

- All fifteen Python configuration blocks passed ASCII and Python syntax checks and loaded into `traitlets.Config`. This checks configuration-file construction, not Jupyter trait recognition or runtime enforcement.
- All five Bash blocks passed `bash -n` and ShellCheck.
- Both unchanged HTTP blocks refused their placeholders locally under `bash -u`.
- Eighty positional-guard cases passed, covering valid inputs, empty values, embedded placeholders, angle brackets, the example hostname, control characters, missing markers, wrong argument counts, and an altered `IFS` count case.
- Seven token-guard cases passed, including rejection of LF, CR, and tab characters before header construction.
- A local dummy-token argument harness confirmed that the authenticated curl invocation starts with `-q -g` and receives the token on stdin, not in its arguments. This harness made no HTTP request and simulated no Jupyter behaviour.
- The referenced local certificate, proxy, Cloudflare, and MFA guides exist. No `tls.md` link is used.

| ID | Status | Outstanding exposed-versus-fixed demonstrations |
|---|---|---|
| JUPYTER-LIVE-1 | Open; REASONED, not demonstrated. Requires Jupyter Server 2.18+, JupyterHub 5+, suitable Unix test accounts, TLS/DNS, browser sessions, terminal support, representative extension routes, and an authorized isolated deployment. | Demonstrate TLS and anonymous/authenticated API access; external reachability and listener inventory; metrics and unclassified extension authentication; cookie-session XSRF and origin checks; Host rejection with an authenticated positive control; root refusal and workload UIDs; terminal disabling; Hub admission including historical users; separate execution accounts and browser origins; host-prefixed cookies; ignored user configuration and protected server environments. Record versions, requests, responses, logs, positive controls, and cleanup. For the sections 8 to 10 controls: demonstrate a route reaching the application outside the intended prefix versus a consistent prefix; a spoofed forwarded IP and scheme taking effect with header trust misconfigured versus rejected behind a sanitizing ingress, a spoofed Forwarded header not changing the detected browser scheme behind the ingress, and a spoofed X-Forwarded-Host ignored unconditionally (the forwarded_host_header trait is inert across the 5.x range); and internal Hub traffic in plaintext versus TLS with client-certificate verification, keeping the kernel ZeroMQ transport excluded from the internal-TLS claim. For the section 11 NativeAuthenticator controls: demonstrate a sub-minimum-length or empty password rejected at signup versus accepted under the effective-zero defaults, a login refused after the configured failed-attempt threshold within the cooldown versus never throttled at the default of zero, a self-registered account held for administrator authorization on /hub/authorize (with allow_all set and allowed_users empty) versus admitted immediately under open_signup, a not-yet-registered allowed_users username claimed as an immediately-authorized account at its first signup, the signup route refusing GET and POST with 404 when enable_signup is False, and the stored password held as a bcrypt hash. |

## 8. Preserve the deployment path prefix through the reverse proxy

When a reverse proxy serves Jupyter under a path prefix such as `/jupyter/`, the application must be told the same prefix, or another route can reach the application outside the authentication and routing boundary the proxy establishes. Both the standalone Server and JupyterHub default their prefix to `/`.

For a standalone Jupyter Server behind a prefix, set it in `jupyter_server_config.py`:

```python
c.ServerApp.base_url = '/jupyter/'
```

The Server applies the prefix to its registered handlers. See the [Server 2.18.0 application definition](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.18.0/jupyter_server/serverapp.py).

For JupyterHub behind the same-host proxy, set the listener and base URL together in `jupyterhub_config.py`:

```python
c.JupyterHub.bind_url = 'http://127.0.0.1:8000/jupyter/'
```

This sets both the bind address and `JupyterHub.base_url`. Configure the prefix consistently on both sides of the proxy; do not combine a `bind_url` prefix with separate conflicting URL settings, and do not reach for the configurable-http-proxy `--no-include-prefix` or `--no-prepend-path` flags as a generic prefix fix, since neither establishes an authentication boundary. See the [JupyterHub proxy configuration](https://jupyterhub.readthedocs.io/en/5.5.2/howto/configuration/config-proxy.html) and the [configurable-http-proxy 5.3.0 command-line options](https://raw.githubusercontent.com/jupyterhub/configurable-http-proxy/5.3.0/bin/configurable-http-proxy).

## 9. Trust forwarded headers only behind a sanitizing ingress

A standalone Jupyter Server does not trust proxy-forwarded headers by default (`ServerApp.trust_xheaders` is `False`), while JupyterHub constructs its HTTP server with forwarded-header trust enabled. Trusting these headers while the backend can still be reached by an untrusted peer, or while the proxy passes client-supplied headers through unchanged, lets a client spoof its apparent address or scheme. Bind the backend privately and trust the headers only behind an ingress that overwrites them.

For a standalone Server behind a same-host TLS ingress, in `jupyter_server_config.py`:

```python
c.ServerApp.ip = '127.0.0.1'
c.ServerApp.trust_xheaders = True
```

Keep `trust_xheaders` at `False` unless a trusted ingress sets `X-Forwarded-For`/`X-Real-IP` and `X-Scheme`/`X-Forwarded-Proto` itself. See the [Server 2.18.0 HTTP-server construction](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.18.0/jupyter_server/serverapp.py).

For the same-host JupyterHub topology, in `jupyterhub_config.py`:

```python
c.JupyterHub.hub_ip = '127.0.0.1'
c.JupyterHub.trusted_downstream_ips = ['127.0.0.1']
c.JupyterHub.public_url = 'https://jupyter.example.com/jupyter/'
```

`trusted_downstream_ips` names the proxy hops that are trusted and skipped when Hub selects the client address from `X-Forwarded-For`; it controls address selection, not whether a connecting peer may supply headers, so it is not a substitute for an ingress that sanitizes them, and an empty list does not disable header trust. The ingress must normalize both forwarded-IP forms (`X-Forwarded-For`, `X-Real-IP`), both scheme forms (`X-Forwarded-Proto`, `X-Scheme`), and the standard RFC 7239 `Forwarded` header, and reject unintended `Host` values. JupyterHub reads the `Forwarded` header before the `X-` scheme forms when deciding the browser-facing scheme, so the ingress must own it too. In this guide's configuration `public_url` (this section) and `cookie_host_prefix_enabled` (section 6) already guard the scheme-derived redirect and single-user OAuth cookie paths, but leaving `Forwarded` unsanitized still lets a client-supplied value reach any scheme decision, so normalize it alongside the other forwarded headers. Binding to loopback excludes a remote peer but not other local processes. See the [JupyterHub configuration reference](https://jupyterhub.readthedocs.io/en/5.5.2/reference/config-reference.html).

## 10. Encrypt internal Hub communication

Public HTTPS (sections 3 and 4) protects only the browser-facing listener. By default JupyterHub leaves the internal traffic between the Hub, the proxy, and the single-user servers unencrypted (`internal_ssl` is `False`). Enable internal TLS in `jupyterhub_config.py`:

```python
c.JupyterHub.internal_ssl = True
c.JupyterHub.internal_certs_location = '/srv/jupyterhub/internal-ssl'
```

JupyterHub then generates an internal certificate authority and per-component certificates and enables TLS with client-certificate verification for the Hub-to-proxy API, the proxy-to-Hub and proxy-to-single-user connections, and the Hub-to-single-user connection used during spawn readiness. Treat the certificate directory as protected persistent state, and give the spawner the ability to deliver each server's key, certificate, and trust bundle (`LocalProcessSpawner` relocates them; a remote spawner needs its own `move_certs` support). Set `Spawner.ssl_alt_names` to the actual connection names when they are not the defaults, and never resolve a certificate error by disabling verification. Internal hostname verification is on by default from [JupyterHub 5.4](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.2/docs/source/reference/changelog.md) and is verified against 5.5.2; earlier 5.x releases left it disabled, so upgrade before relying on it. See the [internal_ssl definition](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.2/jupyterhub/app.py) and the [JupyterHub configuration reference](https://jupyterhub.readthedocs.io/en/5.5.2/reference/config-reference.html).

Internal TLS does not encrypt the single-user server's connection to its kernels. That link uses the Jupyter messaging protocol over ZeroMQ, whose HMAC signature authenticates messages but does not encrypt them. Local kernels bind loopback; a remote-kernel deployment needs a separately configured encrypted transport such as an SSH tunnel, which this guide does not configure. See the [Jupyter messaging protocol](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst) and the [kernel connection defaults](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/jupyter_client/connect.py).

## 11. Harden NativeAuthenticator password and signup policy

Section 5 configures `PAMAuthenticator`, which delegates credentials to the host's user accounts and so inherits the operating system's password and lockout policy. A deployment that instead keeps its own login names and passwords in the Hub, without host accounts, commonly reaches for the separate [NativeAuthenticator](https://native-authenticator.readthedocs.io/en/latest/quickstart.html) package (`c.JupyterHub.authenticator_class = 'native'`). It stores each password as a bcrypt hash in the Hub database and adds its own signup form, so the host no longer supplies a password policy and NativeAuthenticator's own settings become the only floor. Those defaults are permissive, and two of them are weaker than the package's own help text and documentation state, so set them explicitly. This section applies only when NativeAuthenticator is the authenticator; under `PAMAuthenticator` the operating system owns these controls.

In `jupyterhub_config.py`, set a password policy and a login-failure lockout:

```python
c.NativeAuthenticator.minimum_password_length = 12
c.NativeAuthenticator.check_common_password = True
c.NativeAuthenticator.allowed_failed_logins = 5
c.NativeAuthenticator.seconds_before_next_try = 1200
```

Set each of these explicitly, because the shipped runtime defaults are weaker than NativeAuthenticator's help text and documentation suggest. `minimum_password_length` and `seconds_before_next_try` are declared with a `.tag(default=1)` and `.tag(default=600)` annotation, but that tag is traitlets metadata, not the trait's default value: an `Integer` with no explicit default is `0`, so both effectively default to `0`. A `minimum_password_length` of `0` accepts even an empty password, since the check applied at signup is `len(password) >= minimum_password_length`; and a `seconds_before_next_try` of `0` leaves essentially no cooldown after a block. `check_common_password` defaults to `False`; enabling it rejects a new password found in the package's bundled common-password list (its 10,000-entry `common-credentials.txt`), a floor against the most obvious choices, not a breach-corpus check. `allowed_failed_logins` also defaults to `0`, which disables lockout, so the login endpoint can be brute-forced until it is set; pair it with `seconds_before_next_try` to bound repeated guesses after that many consecutive failures for one account. These password rules apply when an account is created at signup, so accounts that already exist keep whatever password they were given and are not re-checked against a newly raised policy. See the [NativeAuthenticator configuration](https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py).

Control who may register, and treat NativeAuthenticator's own approval as separate from the Hub's admission. The signup form is enabled by default (`enable_signup` is `True`), and a self-registered account is created unauthorized and cannot log in until it is authorized:

```python
c.NativeAuthenticator.open_signup = False
```

Keep `open_signup` at its default `False`: with it off, a pending account waits for an administrator to approve it on the Hub's authorization panel (`/hub/authorize`). Never set it to `True` on an internet-reachable Hub, where it would pre-authorize every self-registration, so anyone who reaches the signup form obtains an active account. One case authorizes an account at signup even with `open_signup` off: NativeAuthenticator pre-authorizes any username already present in the section 5 `allowed_users` or `admin_users` (its `create_user` sets `pre_authorized = self.open_signup or username in self.get_authed_users()`, and `get_authed_users` includes `allowed_users` and `admin_users`). Because JupyterHub's own admission (`check_allowed`) independently lets a user launch a server only when `allow_all` is set or the username is in `allowed_users`, the section 5 configuration in this guide (`allow_all = False` with a populated `allowed_users`) makes those two sets coincide: exactly the login-capable users are the pre-authorized ones, so the administrator-approval step never gates a usable account, and a listed username that has not yet registered can be claimed at the signup form, with a password of the claimant's choosing, by anyone who can reach it. Treat the signup form as reachable only by trusted users, register the `allowed_users` accounts deliberately, and if self-service registration is not wanted at all set `enable_signup = False`, which makes the signup route reject every request. Passwords are stored as bcrypt hashes in the Hub database, so protect that database and its backups as a credential store.

## Sources (checked September 2026)

- Jupyter Server public server guide and password/TLS setup: https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html
- Jupyter Server security and token/password authentication: https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- Jupyter Server API base handler, protected API responses, and metrics enforcement: https://github.com/jupyter-server/jupyter_server/blob/main/jupyter_server/base/handlers.py
- Jupyter Server configuration reference and authentication migrations: https://jupyter-server.readthedocs.io/en/latest/other/full-config.html
- Migrating from the classic Notebook server: https://jupyter-server.readthedocs.io/en/latest/operators/migrate-from-nbserver.html
- Jupyter Server API reference for authentication, origin, Host, root, and terminal controls: https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html
- Jupyter Server authentication API: https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.auth.html
- Jupyter Server release history, including endpoint authentication under 2.13.0 and 2.18.0: https://jupyter-server.readthedocs.io/en/stable/other/changelog.html
- Jupyter Server startup, dynamic defaults, and root refusal implementation: https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/serverapp.py
- Jupyter Server default port constant: https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/__init__.py
- Jupyter Server identity provider and token-authenticated origin exception: https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/auth/identity.py
- Jupyter Server Host, origin, XSRF, and default authentication implementation: https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/base/handlers.py
- Jupyter Server kernel API implementation: https://raw.githubusercontent.com/jupyter-server/jupyter_server/main/jupyter_server/services/kernels/handlers.py
- Jupyter Server REST API: https://jupyter-server.readthedocs.io/en/stable/developers/rest-api.html
- Notebook 7 configuration and Jupyter Server backend: https://jupyter-notebook.readthedocs.io/en/stable/configuring/config_overview.html
- JupyterLab kernel and terminal management: https://jupyterlab.readthedocs.io/en/stable/user/running.html
- JupyterHub authenticator API and PAM admission settings: https://jupyterhub.readthedocs.io/en/stable/reference/api/auth.html
- JupyterHub authenticators and Hub 5 admission changes: https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html
- JupyterHub configuration reference: https://jupyterhub.readthedocs.io/en/stable/reference/config-reference.html
- JupyterHub spawner API and user-configuration limitations: https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html
- JupyterHub spawner resource-limit support: https://jupyterhub.readthedocs.io/en/stable/reference/spawners.html
- JupyterHub browser security, per-user domains, cookies, and server environments: https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html
- JupyterHub HTTPS reverse-proxy example: https://jupyterhub.readthedocs.io/en/stable/howto/configuration/config-proxy.html
- Tornado XSRF cookies and request headers: https://www.tornadoweb.org/en/stable/guide/security.html
- curl TLS certificate and hostname verification: https://curl.se/docs/sslcerts.html
- curl options, stdin headers, cookie files, and diagnostic variables: https://curl.se/docs/manpage.html
- JupyterHub 5.5.2 proxy configuration and path prefix: https://jupyterhub.readthedocs.io/en/5.5.2/howto/configuration/config-proxy.html
- configurable-http-proxy 5.3.0 command-line options: https://raw.githubusercontent.com/jupyterhub/configurable-http-proxy/5.3.0/bin/configurable-http-proxy
- NativeAuthenticator configuration traits and password, lockout, and signup enforcement: https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py
- NativeAuthenticator quickstart and authenticator_class: https://native-authenticator.readthedocs.io/en/latest/quickstart.html
- JupyterHub 5.5.2 configuration reference (trusted_downstream_ips, public_url, internal_ssl): https://jupyterhub.readthedocs.io/en/5.5.2/reference/config-reference.html
- JupyterHub 5.4 changelog (internal-TLS hostname verification default): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.2/docs/source/reference/changelog.md
- Jupyter Server 2.18.0 application definition and HTTP-server construction: https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.18.0/jupyter_server/serverapp.py
- JupyterHub 5.5.2 application (internal_ssl and forwarded-header trust): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.2/jupyterhub/app.py
- Jupyter messaging protocol (jupyter_client 8.6.3): https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst
- Jupyter kernel connection defaults (jupyter_client 8.6.3): https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/jupyter_client/connect.py
