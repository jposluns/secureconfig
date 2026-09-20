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
  [ -f "$2" ] && [ -r "$2" ] || { echo "CA bundle is not a readable file; not probing"; exit 1; }
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
  [ -f "$2" ] && [ -r "$2" ] && [ -f "$3" ] && [ -r "$3" ] &&
    [ -f "$4" ] && [ -r "$4" ] || { echo "a required file is unreadable; not probing"; exit 1; }
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

### Local authoring checks and demonstration backlog

The following checks were run without editing files or running `tools/run_all_checks.sh`:

- All eight Python configuration blocks passed ASCII and Python syntax checks and loaded into `traitlets.Config`. This checks configuration-file construction, not Jupyter trait recognition or runtime enforcement.
- All five Bash blocks passed `bash -n` and ShellCheck.
- Both unchanged HTTP blocks refused their placeholders locally under `bash -u`.
- Eighty positional-guard cases passed, covering valid inputs, empty values, embedded placeholders, angle brackets, the example hostname, control characters, missing markers, wrong argument counts, and an altered `IFS` count case.
- Seven token-guard cases passed, including rejection of LF, CR, and tab characters before header construction.
- A local dummy-token argument harness confirmed that the authenticated curl invocation starts with `-q -g` and receives the token on stdin, not in its arguments. This harness made no HTTP request and simulated no Jupyter behaviour.
- The referenced local certificate, proxy, Cloudflare, and MFA guides exist. No `tls.md` link is used.

| ID | Status | Outstanding exposed-versus-fixed demonstrations |
|---|---|---|
| JUPYTER-LIVE-1 | Open; REASONED, not demonstrated. Requires Jupyter Server 2.18+, JupyterHub 5+, suitable Unix test accounts, TLS/DNS, browser sessions, terminal support, representative extension routes, and an authorized isolated deployment. | Demonstrate TLS and anonymous/authenticated API access; external reachability and listener inventory; metrics and unclassified extension authentication; cookie-session XSRF and origin checks; Host rejection with an authenticated positive control; root refusal and workload UIDs; terminal disabling; Hub admission including historical users; separate execution accounts and browser origins; host-prefixed cookies; ignored user configuration and protected server environments. Record versions, requests, responses, logs, positive controls, and cleanup. |

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
