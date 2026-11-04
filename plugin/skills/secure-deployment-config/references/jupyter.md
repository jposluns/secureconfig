# Jupyter: password and TLS

Jupyter lets people write and run code in browser-based notebooks, and JupyterHub hosts notebook servers for many users. This guide helps your AI assistant configure a deployment securely, including passwords on standalone servers, TLS, origin and Host checks kept on, and separate identities and system accounts for Hub users.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/jupyter.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Jupyter Server v2.21.1, JupyterHub 6.1.1 and 5.5.4, jupyter_client 8.6.3, configurable-http-proxy 5.3.0, and NativeAuthenticator 1.3.0; 7 further sources carry no recorded version. Metadata reviewed 2026-11-04; documentation checked September 2026. The guide records 69 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

An unauthenticated Jupyter server gives anyone who can reach it arbitrary code execution with the permissions of its server and kernel processes. Running those processes with administrative privileges gives an authenticated attacker those privileges too. Jupyter Server ships with authentication on through a generated token; keep authentication enabled. Setting a password replaces the automatically generated token by default. A token and a password can coexist as alternatives, but neither is a second factor. [Jupyter Server security](https://jupyter-server.readthedocs.io/en/latest/operators/security.html).

Keep the default loopback bind when changing other settings. The Server examples below target Jupyter Server 2.18+, including the backend used by JupyterLab and Notebook 7, and were checked against v2.21.1. The multi-user examples belong in `jupyterhub_config.py` and were checked against two JupyterHub releases: 6.1.1, the latest, and 5.5.4, the last 5.x release. A statement given for 6.1.1 alone was not established for 5.5.4; where the two releases differ, the guide gives both. Hub manages authentication for its single-user servers; the standalone password workflow below is for independently operated servers. [Server configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html), [Notebook configuration](https://jupyter-notebook.readthedocs.io/en/stable/configuring/config_overview.html), [Hub authenticators](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html).

Run JupyterHub 6.1.0 or later, or 5.5.3 or later on 5.x. GHSA-5jhc-4h3c-q97h, which section 5 quotes, lists every release up to 5.5.2, and 6.0.0 up to but not including 6.1.0, as affected. 5 further advisories name the same patched releases, 5.5.3 and 6.1.0, for all or part of those ranges. Section 11 quotes one of them, GHSA-93gc-h923-mp36. The 6.1.0 changelog says of another, GHSA-hx46-2cv3-mh6g, denial of service via invalid spawner options, "Only this one affects most deployments", and its advisory says "Denial of Service via certain invalid user input in spawner options could prevent subsequent JupyterHub launches and require manual database intervention to remove invalid data." That advisory lists 6.1.0 and 5.5.3 as patched, so this guide's floor includes its fix. As this guide's assessment, the other 3, GHSA-pvm9-48cg-w76j, GHSA-r764-xgvf-jrfj and GHSA-x7xh-7hc7-9436, which concern token expiry limits, SharedPasswordAuthenticator and the user rename API, bear on no setting this guide gives. The 6.1.1 and 5.5.4 changelog entries name no advisory: each fixes the regression in 6.1.0 and 5.5.3 that rejected 64-character tokens. 4 earlier advisories, GHSA-p43p-whwx-q52h, GHSA-c4gm-pwx9-9w8j, GHSA-69wv-m5fw-2fhp and GHSA-mj6q-mp44-53v8, fixed in 5.5.0 to 5.5.2, list no 6.x range as affected; that 6.0.0 and later contain those fixes is not established here from source. [JupyterHub 6.1.1 changelog](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md), [JupyterHub 5.5.4 changelog](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/docs/source/reference/changelog.md), [GHSA-5jhc-4h3c-q97h](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-5jhc-4h3c-q97h), [GHSA-hx46-2cv3-mh6g](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-hx46-2cv3-mh6g), [GHSA-pvm9-48cg-w76j](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-pvm9-48cg-w76j), [GHSA-r764-xgvf-jrfj](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-r764-xgvf-jrfj), [GHSA-x7xh-7hc7-9436](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-x7xh-7hc7-9436).

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

Do not bypass this with `--allow-root`. The setting refuses root startup; it does not change the process's account or sandbox notebook code. Grant the account only the filesystem and service access its notebooks require. Apply this privilege requirement to Hub user workloads separately from the privileges required by the selected spawner. [Server startup implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (v2.21.1, lines 1000 to 1004 and 3116 to 3126).

If terminals are unnecessary, disable them:

```python
c.ServerApp.terminals_enabled = False
```

Notebook kernels can still execute shell commands. This removes an unused interface; it does not create an execution boundary. At the time of writing, the generated reference displays `False`, while the implementation dynamically defaults to `True`, subject to terminal availability. Configure it explicitly. [Terminal configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html#ServerApp.terminals_enabled), [implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (v2.21.1, lines 1984 to 2000).

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
- An **HTTPS reverse proxy with authentication** ([nginx.md](nginx.md), [caddy.md](caddy.md)) or HTTPS access through [cloudflare.md](cloudflare.md), in front of a loopback-bound server, is an alternative to native TLS. Authentication alone does not encrypt transport. [Jupyter HTTPS proxy example](https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html) (the 5.5.4 page has the same examples).
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

Jupyter Server 2.18.0 fixed GHSA-24qx-w28j-9m6p (CVE-2026-40110), "Jupyter Server has a  CORS Origin Validation Bypass via `re.match()` in `allow_origin_pat`" (high; affected `<= 2.17.0`, patched `2.18.0`), so both this guide's 2.18+ target and v2.21.1 are outside its affected range. At v2.21.1, `origin_matches_pat` returns `False` for an empty pattern and otherwise accepts an origin only on `re.fullmatch`, warning when a pattern matched only as a prefix (`utils.py` lines 46 to 65). The empty `allow_origin_pat` above therefore matches no origin. [GHSA-24qx-w28j-9m6p](https://github.com/advisories/GHSA-24qx-w28j-9m6p), [origin pattern check](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/utils.py).

Preserve DNS-rebinding protection while allowing the deployment's actual hostname:

```python
c.ServerApp.allow_remote_access = False
c.ServerApp.local_hostnames = ['localhost', 'jupyter.example.com']
```

Replace `jupyter.example.com`. Setting `allow_remote_access = True` disables the Host check; adding a known hostname does not require it. This static hostname example is for a standalone server; Hub single-user servers need their actual generated hostnames accounted for. [Host-check configuration](https://jupyter-server.readthedocs.io/en/latest/other/full-config.html#ServerApp.allow_remote_access).

Token-authenticated requests bypass origin and XSRF checks by design. Use a cookie-authenticated session, without an authorization token, to test these browser-session protections. [Identity-provider implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/auth/identity.py) (v2.21.1, lines 533 to 555), [request-handler implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/base/handlers.py) (v2.21.1, lines 403 to 408 and 530 to 554).

## 5. Give Hub users individual identities and execution accounts

**Tier 1 for multi-user deployments; this example requires JupyterHub 6.1.0 or later, or 5.5.3 or later on 5.x, on Unix, and was checked against 6.1.1 and 5.5.4.**

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

Replace the user placeholders with actual Unix account names. Disabling `allow_existing_users` prevents historical Hub database membership from independently admitting users. An empty `allowed_groups` avoids another admission path through Unix group membership. Other authenticators can extend these rules and require their own review. The 6.1.1 and 5.5.4 authenticator API pages document the same `allow_all`, `allow_existing_users` and `allowed_groups` settings. [Authenticator API 6.1.1](https://jupyterhub.readthedocs.io/en/6.1.1/reference/api/auth.html), [Authenticator API 5.5.4](https://jupyterhub.readthedocs.io/en/5.5.4/reference/api/auth.html), [Hub 5 admission changes](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html#allowing-access).

`LocalProcessSpawner` requires matching local Unix accounts. Do not use `SimpleLocalProcessSpawner` in production: it provides no isolation between users. [Spawner API](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html), [Hub configuration reference](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html) (the 5.5.4 reference carries the same warning).

Run a release with the `LocalProcessSpawner` privilege-drop fix. GHSA-5jhc-4h3c-q97h, "Incomplete privilege drop in LocalProcessSpawner when setgroups() fails" (medium; affected `>=6.0.0, <6.1.0` and `<=5.5.2`, patched `6.1.0` and `5.5.3`), says that "When the `setgroups` syscall fails (rare), supplemental groups may be inherited from the Hub parent process." At 6.1.1, when setting the user's groups fails, the spawner's pre-exec function attempts to clear the supplemental groups with `os.setgroups([])`, a call its comment says "might fail", and only prints `Failed to clear groups` if it does. After `os.setuid(uid)` it then aborts with `PermissionError(f"Failed to drop groups: {extra_groups}")` if a group outside the user's remains (`spawner.py` lines 1906 to 1931, the clearing attempt and check at lines 1915 to 1931). 5.5.4 carries the same code at lines 1839 to 1864, the clearing attempt and check at lines 1848 to 1864. [GHSA-5jhc-4h3c-q97h](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-5jhc-4h3c-q97h), [6.1.1 spawner](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/spawner.py), [5.5.4 spawner](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/spawner.py).

Local processes are not containers, and `LocalProcessSpawner` does not enforce the generic CPU or memory limits. PAM does not automatically provide MFA; retain an explicitly configured MFA solution where required. [Spawner limitations](https://jupyterhub.readthedocs.io/en/6.1.1/reference/spawners.html#spawners-resource-limits-and-guarantees-optional) (the 5.5.4 page says the same), [mfa.md](mfa.md).

### Moving from JupyterHub 5.5.4 to 6.1.1

These 6.x changes bear on this guide's configuration. JupyterHub 6 requires Python 3.10 and includes a database schema upgrade, so back up the database and run `jupyterhub upgrade-db` before starting 6.1.1. 6.1 adds `Authenticator.auth_refresh_strict`, `False` by default; its documentation says "Prior to 6.1, the behavior was the same as Authenticator.auth_refresh_strict = True". With `True`, when a user's auth state is stale and cannot be refreshed, admin spawns for other users and API requests from that user's own servers fail until the user completes a fresh login. This guide configures no auth refresh, and the 5.5.4 authenticator API page has no such setting. [Upgrading to JupyterHub 6](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md), [Authenticator API 6.1.1](https://jupyterhub.readthedocs.io/en/6.1.1/reference/api/auth.html), [Authenticator API 5.5.4](https://jupyterhub.readthedocs.io/en/5.5.4/reference/api/auth.html).

JupyterHub 6 adds PKCE to its internal OAuth and the `JupyterHub.oauth_require_pkce` setting, `False` by default for backward compatibility (6.1.1 `app.py` lines 451 to 463); the 5.5.4 `app.py` has no such setting. Its help text says `versionadded:: 6.0`, but the 6.1.0 changelog lists "Tag `oauth_require_pkce` with `config`" (#5533), so as this guide's reading the setting is configurable from 6.1.0, which is this guide's 6.x floor. The upgrade notes say that setting it to `True` "will prevent any OAuth client that does not send PKCE arguments (such as those using OAuth implementations from JupyterHub 5 or before) from completing OAuth." As this guide's inference, enable it only once every single-user server and OAuth service runs a client that sends PKCE. From 6.0, spawn options passed as GET query parameters should take an `opt-` prefix, which the 6.0.0 changelog lists as a breaking change. The upgrade notes say "Passing parameters without the `opt-` prefix will continue to work in most cases", with exceptions: `display_name` is now used by JupyterHub and removed from the spawner's options, so pass `opt-display_name`, and an existing `opt-a` parameter is converted to `a`, so pass `opt-opt-a`. They also say "If any parameter is passed using the `opt-` prefix all parameters must, others will be ignored." and "Other parameters may be used by JupyterHub in future releases. These will not be treated as a breaking change." For `POST /api/users/:username/servers/:servername`, the upgrade notes say the whole JSON body was passed as `user_options` before JupyterHub 6, and JupyterHub 6 moves this to a `user_options` key. This guide sets no spawn options. Section 8 covers the Unix-socket proxy support and section 10 the new internal HTTP client. [Upgrading to JupyterHub 6](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md), [6.1.1 application](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py), [6.1.1 changelog](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md).

## 6. Isolate Hub browser origins and protect server configuration

**Tier 1 for mutually untrusted users; JupyterHub. The combined example targets Hub 6.1.0 or later, or 5.5.3 or later on 5.x, and host-prefixed cookies require Hub 4.1+.**

Separate execution accounts do not separate browser origins. For mutually untrusted users, add to `jupyterhub_config.py`:

```python
c.JupyterHub.subdomain_host = 'https://jupyter.example.com'
c.JupyterHub.cookie_host_prefix_enabled = True
c.Spawner.disable_user_config = True
```

Replace the hostname. Provide DNS and valid HTTPS certificates for the Hub and every generated user hostname, commonly through wildcard DNS and suitable certificate coverage. Use a domain separated from sensitive applications. Hub documents no cross-user protection guarantee without per-user domains. Enable host-prefixed cookies with HTTPS and per-user domain separation. A default Hub is intended for semi-trusted users. [Hub security overview](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html), [cookie setting and version](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html) (the 5.5.4 reference gives the same setting and version).

Keep the single-user server executable, Python environment, and launch path under administrator control. `disable_user_config` ignores user-home configuration, but users who can replace the server environment can circumvent it. Users may have separate writable kernel environments. These controls complement operating-system or container isolation. [Spawner API](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html#jupyterhub.spawner.LocalProcessSpawner.disable_user_config), [server environment isolation](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html#isolate-packages-in-a-read-only-environment).

## 7. Verify

REASONED: Verification preparation; a live Jupyter Server or JupyterHub stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local marking review ran all five Bash blocks through bash -n and ShellCheck 0.11.0 with exit 0 and no output, and all fifteen Python configuration blocks passed ASCII, AST and traitlets.Config loading. The bash -n and ShellCheck runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and the listener inventory as a bare ss -tlnp, and those local runs were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. Exposed anonymous kernel access must contrast with fixed authentication and a working positive control, per the guide's cited Jupyter Server security and token/password authentication (rolling documentation, checked September 2026). **Service behaviour is REASONED, not demonstrated.** The authoring environment has no Jupyter Server, Notebook, or JupyterHub packages or executables, and no Docker or Podman. It has no available test deployment for the service checks below. These missing capabilities prevent exposed-versus-fixed demonstrations here; they do not waive local checks. Expected service outcomes rest on the cited vendor documentation and pinned implementations.

REASONED: Isolated comparison discipline; no live test deployment was exercised, because a live Jupyter Server or JupyterHub stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local HTTP stub fixtures returned CURL_STUB for substituted inputs and refused written placeholders with exit 1 and "substitute every placeholder inside the quotes; not probing". Those stub runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current forms, whose guard refusals exit with status 2 and which exit 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover them. These are argument checks, not exposed/fixed service comparisons; per the guide's cited Jupyter Server Host, origin, XSRF, and default authentication implementation, exposed access must become fixed rejection while authenticated positive controls still succeed. Use an isolated test deployment for exposed configurations. Keep its versions, extensions, request paths, credentials, and test data consistent while changing the control under test. Never weaken a production deployment to create the exposed comparison. A rejection counts only when the positive control succeeds and the exposed comparison demonstrates that the request can reach the relevant functionality.

REASONED: Complete-paste and substitution assumptions; a live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. bash -n and ShellCheck 0.11.0 returned 0 without output for both HTTP blocks. Stubbed bash -u runs rejected written placeholders with "substitute every placeholder inside the quotes; not probing", bad markers with "paste the whole block, including its set -- line; not probing", and short value lists with the corresponding exact-value-count refusal, all exit 1 before curl; valid browser and cookie inputs printed one and four CURL_STUB lines with exit 0. These bash -n, ShellCheck and stub runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and the stub runs were not repeated on the current forms, whose guard refusals exit with status 2 and which exit 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover them. These checks do not test a fragment starting below the guards or a caller already holding the expected marker and values; per the guide's cited curl options, stdin headers, cookie files, and diagnostic variables, the guarded requests still require a live deployment for exposed access versus fixed rejection. Paste complete Bash blocks. Substitute values **inside the single quotes** on each `set --` line; values containing a literal apostrophe require proper shell quoting. The guards assume genuine shell builtins. A fragment pasted below a guard is unguarded, and inherited arguments identical to the marker and expected values cannot be distinguished from a complete paste.

### TLS, anonymous access, and authenticated access (REASONED: TLS, anonymous and authenticated API access, token stdin handling, browser login and wrong Host. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local marking review ran all five Bash blocks through bash -n and ShellCheck 0.11.0: exit 0 with no output; all fifteen Python configuration blocks passed ASCII, AST and traitlets.Config loading. With external commands stubbed, both written HTTP placeholders exited 1 with "substitute every placeholder inside the quotes; not probing"; valid browser and cookie fixtures exited 0 with one and four CURL_STUB lines respectively. Invalid marker, count, empty, placeholder, angle-bracket, example-host, control-character, scheme, URL and file fixtures exited 1 before curl. Seven token fixtures produced three CURL_STUB lines for the valid dummy token; empty, placeholder and angle-bracket tokens printed "a real token is required; not probing", and LF, CR and tab tokens printed "token contains a control character; not probing", after only the anonymous stub call. The valid token was absent from argv and present in stdin headers. These bash -n, ShellCheck and stub runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, the bash -n and ShellCheck runs also covered the listener inventory as a bare ss -tlnp, and the stub runs were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. Local openssl certificate verification printed OK for localhost and error 62, hostname mismatch, for wrong.internal; this does not test curl or Jupyter TLS. Browser sessions and a live fronting authentication route remain untested; expected exposed access and fixed TLS/authentication/Host outcomes are the comparisons in this subsection, per the guide's cited sources this declaration lists in two parts. The guide's cited sources this declaration lists (1 of 2): Jupyter Server public server guide and password/TLS setup (rolling documentation, checked September 2026); Jupyter Server security and token/password authentication (rolling documentation, checked September 2026); Jupyter Server Host, origin, XSRF, and default authentication implementation. The guide's cited sources this declaration lists (2 of 2): Jupyter Server REST API (rolling documentation, checked September 2026); curl TLS certificate and hostname verification; curl options, stdin headers, cookie files, and diagnostic variables.)

**REASONED: no Jupyter runtime or test deployment in the authoring environment.**

Use the actual external URL of `/api/kernels`, including any deployment prefix. The first request checks TLS and anonymous API access together. Use a URL without credentials or token query parameters.

Supply the actual CA bundle path: the system CA bundle for a public certificate, the private CA bundle for a private certificate, or the trusted certificate from step 3 for a self-signed deployment. Request the hostname covered by the certificate. Certificate verification must remain enabled. These commands use curl 7.75.0+ for `exitcode` and `errormsg`. [curl certificate verification](https://curl.se/docs/sslcerts.html), [curl options](https://curl.se/docs/manpage.html).

Leave the final value as `browser` for a password-only server. If a token is already configured, change it to `token`; Python prompts for it, and the shell feeds the authorization header to curl on stdin. Do not add a token merely to replace the password/browser positive control. The block disables shell tracing and avoids putting the token in shell history or curl arguments; it does not conceal credentials from the account owner or other session-recording mechanisms.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x
  set +e                   # errexit off here, so each result below is recorded instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_HTTPS_URL' 'REPLACE_WITH_CA_BUNDLE' 'browser'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  (
    while [ "$#" -gt 0 ]; do
      case "$1" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
        *[[:cntrl:]]*) echo "control character in input; not probing"; exit 2 ;;
      esac
      shift
    done
  ) || exit 2
  case "$1" in https://*) ;; *) echo "HTTPS URL required; not probing"; exit 2 ;; esac
  case "$1" in
    *'@'*|*'?'*|*'#'*|*' '*) echo "use a URL without credentials, query, fragment or spaces; not probing"; exit 2 ;;
  esac
  case "$2" in /*) ;; *) echo "absolute CA bundle path required; not probing"; exit 2 ;; esac
  [ -f "$2" ] || { echo "CA bundle is not a readable file; not probing"; exit 2; }
  [ -r "$2" ] || { echo "CA bundle is not a readable file; not probing"; exit 2; }
  case "$3" in browser|token) ;; *) echo "choose browser or token; not probing"; exit 2 ;; esac
  case "$3" in
    token) command -v python3 > /dev/null || { echo "python3 is required for the token prompt; not probing"; exit 2; } ;;
  esac

  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      set -- "$1" "$2" "$3" 0   # the 4th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 2 (a refused token), which outranks 0
      # REASONED: no Jupyter runtime or test deployment in the authoring environment.
      # This request checks certificate validation AND anonymous API access.
      set -- "$1" "$2" "$3" "$4" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" -w '\nanonymous=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
      set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # curl's exit status, then its output
      printf '%s' "$6"
      case "$5:$6" in
        0:*'anonymous=403 '*) ;;
        0:*'anonymous=2'??' '*) echo "FINDING: the anonymous request was answered with a 2xx, so this URL is reachable without credentials"; set -- "$1" "$2" "$3" 1 ;;
        0:*'anonymous=3'??' '*|0:*'anonymous=401 '*) echo "unclassified observation: a redirect or 401 challenge, which is the fixed result only if it comes from your login layer; judge it" ;;
        0:*) echo "the anonymous request was answered with neither the native 403 nor a login redirect; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
        *) echo "curl exit $5: the validated HTTPS request did not complete; a plaintext listener, a certificate that fails validation and a connection failure all end this way, so read err= above; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
      esac

      # Password-only deployments: perform the browser positive control described below.
      if [ "$3" = token ]; then
        (
          set -- "$(if python3 -c 'import getpass; print(getpass.getpass("Jupyter token: "))'; then printf '\n0'; else printf '\n%s' "$?"; fi)" "$1" "$2"
          set -- "${1%$'\n'*}" "$2" "$3" "${1##*$'\n'}"
          set -- "${1%$'\n'}" "$2" "$3" "$4"   # the token without print's line ending, the URL, the CA bundle, then python3's exit status
          [ "$4" = 0 ] || { echo "the token prompt failed (python3 exit $4), so the token requests did not run; inconclusive"; exit 3; }
          case "$1" in
            *REPLACE_WITH_*|*'<'*|*'>'*|"") echo "a real token is required; not probing"; exit 2 ;;
          esac
          case "$1" in
            *[[:cntrl:]]*) echo "token contains a control character; not probing"; exit 2 ;;
          esac
          set -- "$1" "$2" "$3" 0   # the 4th value is now this part's status so far, ranked as above
          # REASONED: no Jupyter runtime or test deployment in the authoring environment.
          set -- "$1" "$2" "$3" "$4" "$(if printf 'Authorization: token %s\n' "$1" |
            curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
              --cacert "$3" --header @- \
              -w '\nauthenticated=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$2"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
          set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"
          printf '%s' "$6"
          case "$5:$6" in
            0:*'authenticated=200 '*) ;;
            0:*) echo "the token request did not return 200, so the authenticated positive control failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
            *) echo "curl exit $5: the token request failed, so the authenticated positive control failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
          esac

          # REASONED: no Jupyter runtime or test deployment in the authoring environment.
          # The deliberately wrong Host below is a non-secret test value, not the destination.
          set -- "$1" "$2" "$3" "$4" "$(if printf 'Authorization: token %s\n' "$1" |
            curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
              --cacert "$3" --header @- --header 'Host: rebinding.example.com' \
              -w '\nwrong-host=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$2"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
          set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"
          printf '%s' "$6"
          case "$5:$6" in
            0:*'wrong-host=403 '*) ;;
            0:*'wrong-host=2'??' '*) echo "FINDING: the token request with a wrong Host reached the API"; set -- "$1" "$2" "$3" 1 ;;
            0:*) echo "the wrong-Host request was answered with neither the native 403 nor a 2xx; a fronting layer's rejection shows only its own rejection; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
            *) echo "curl exit $5: the wrong-Host request failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
          esac
          exit "$4"
        )
        case "$?:$4" in 0:*) ;; 1:*) set -- "$1" "$2" "$3" 1 ;; 2:0) set -- "$1" "$2" "$3" 2 ;; 2:*|*:1) ;; *) set -- "$1" "$2" "$3" 3 ;; esac   # fold the token part's status into the block's, ranked as above
      fi
      echo "block exit $4; the response bodies, any login redirect or challenge and, without a token, the browser positive control described below are not classified, so judge them yourself"
      exit "$4"
      ;;
  esac
)
```

**No Jupyter runtime or browser session here.** In a clean browser profile, visit the same deployment without a token query or existing cookies. It must require authentication before loading a notebook. Log in with the configured password, then request the same `/api/kernels` URL: expect `200` with a JSON kernel list, including an empty list when no kernels are running. An existing session legitimately skips the login prompt. [Server authentication](https://jupyter-server.readthedocs.io/en/latest/operators/security.html), [kernels API](https://jupyter-server.readthedocs.io/en/stable/developers/rest-api.html).

Use these exposed-versus-fixed comparisons:

| Check | Exposed comparison | Fixed result and positive control |
|---|---|---|
| TLS | A known-running plaintext listener or a certificate failing trust/hostname validation cannot complete the validated HTTPS request. | HTTPS completes with `exit=0`. An HTTP error status can still accompany successful TLS. A connection failure alone proves no protection. |
| Native API authentication | With both native credentials absent in the isolated fixture, anonymous `GET /api/kernels` returns kernel JSON. | Anonymous access returns native `403`; authenticated access returns `200` and kernel JSON. |
| Fronting authentication | Demonstrate that the exposed external route returns kernel data anonymously. | Anonymous access yields no kernel data; a login redirect may replace native `403`. Complete all required login layers and obtain authenticated kernel JSON. |
| Host check | With `allow_remote_access = True` in the isolated fixture, the token-authenticated wrong-Host request reaches the kernel API. | With the step 4 settings, wrong Host is refused with native `403`, while the normal-Host token request succeeds. |

Native protected-API `403` and Host-check behaviour come from the [handler implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/base/handlers.py) (v2.21.1, lines 598 to 658 and 782 to 789). If a fronting layer rejects the wrong Host in both states, that demonstrates its rejection only; the Server Host-check comparison remains REASONED from that implementation, not demonstrated.

### Metrics and extension routes (REASONED: Metrics and unclassified extension routes. A live stand-up of Jupyter Server with representative extensions opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The reused HTTPS block passed bash -n and ShellCheck 0.11.0 without output; stub fixtures rejected placeholders with exit 1 and reached curl for substituted input. Those runs covered the TLS and API access block in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current form, whose guard refusals exit with status 2 and which exits 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. No installed extension route or authenticated deployment was exercised. Expect anonymous metrics with authenticate_prometheus False, refusal with True and an authenticated metrics body; expect an otherwise unclassified route to require login only with allow_unauthenticated_access False, retaining its authenticated body. Explicitly public routes need separate review, per the guide's cited Jupyter Server API base handler, protected API responses, and metrics enforcement; Jupyter Server API reference for authentication, origin, Host, root, and terminal controls (rolling documentation, checked September 2026); curl options, stdin headers, cookie files, and diagnostic variables.)

**REASONED: no Jupyter runtime, installed extension routes, or test deployment here.**

Repeat the guarded HTTPS block with the actual Server `/metrics` URL, then each installed extension's documented, read-only protected URL. Complete the authenticated positive control for every route. Metrics should return their expected metrics body after authentication, rather than kernel JSON. An absent route, login page, or generic error is not that positive control.

For the metrics comparison, set `authenticate_prometheus = False` only in the isolated exposed fixture: anonymous metrics should become available. Restore `True`: anonymous metrics should be refused and authenticated metrics should remain available. [Metrics handler](https://github.com/jupyter-server/jupyter_server/blob/v2.21.1/jupyter_server/base/handlers.py) (v2.21.1, lines 1202 to 1214).

To demonstrate `allow_unauthenticated_access`, identify an extension route using Jupyter's handler machinery without an explicit authentication decorator or public-access declaration. With `True`, its anonymous GET is permitted; with `False`, login is required and its authenticated response remains available. Record the actual route and expected body. If no such route is installed, this feature check remains REASONED from the cited authentication-enforcement documentation; testing an already protected kernel route does not replace it. Explicitly public routes require a separate review of whether their exposure is intentional. [Default authentication enforcement](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html#jupyter_server.serverapp.ServerApp.allow_unauthenticated_access).

### Cookie-session XSRF and origin checks (REASONED: Cookie/header preparation, cookie GET, XSRF POST, origin/CORS comparisons and kernel cleanup. A live stand-up of Jupyter Server with a disposable default kernel opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. No authenticated browser session was exercised. Local marking review ran all five Bash blocks through bash -n and ShellCheck 0.11.0: exit 0 with no output; all fifteen Python configuration blocks passed ASCII, AST and traitlets.Config loading. With external commands stubbed, both written HTTP placeholders exited 1 with "substitute every placeholder inside the quotes; not probing"; valid browser and cookie fixtures exited 0 with one and four CURL_STUB lines respectively. Invalid marker, count, empty, placeholder, angle-bracket, example-host, control-character, scheme, URL and file fixtures exited 1 before curl. These bash -n, ShellCheck and stub runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, the bash -n and ShellCheck runs also covered the listener inventory as a bare ss -tlnp, and the stub runs were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. Python json.loads parsed the POST body as an empty object; dummy Netscape cookie and X-XSRFToken files exercised file arguments only. Expected exposed POST creates a kernel without XSRF and wrong-origin GET returns data; fixed missing XSRF gives 403, valid XSRF gives 201, wrong-origin GET gives 404 and same-origin GET gives 200. Browser CORS and authenticated UI cleanup require the live session, per the guide's cited sources this declaration lists in two parts. The guide's cited sources this declaration lists (1 of 2): Jupyter Server identity provider and token-authenticated origin exception; Jupyter Server Host, origin, XSRF, and default authentication implementation; Jupyter Server kernel API implementation. The guide's cited sources this declaration lists (2 of 2): JupyterLab kernel and terminal management; Tornado XSRF cookies and request headers; curl options, stdin headers, cookie files, and diagnostic variables.)

**REASONED: no Jupyter runtime, authenticated browser session, or test deployment here.**

Use a disposable standalone test server with a working default kernel. Authenticate through its password login and prepare two account-private files:

- A Netscape-format cookie jar containing that session's authentication and `_xsrf` cookies.
- A header file containing only `X-XSRFToken: ` followed by the matching `_xsrf` value.

Keep both files readable only by the testing account and remove them after testing. Do not put their contents on command lines. The header name is documented by [Tornado's XSRF protection](https://www.tornadoweb.org/en/stable/guide/security.html); curl supports cookie and header files. [curl options](https://curl.se/docs/manpage.html).

Set the base URL to the actual server URL, including any deployment prefix. Set the same-origin value to its scheme and authority, including a non-default port, with no path or trailing slash. Do not supply an authorization token: that would bypass the protection being tested.

```bash
(
  set +x
  set +e                   # errexit off here, so each result below is recorded instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SERVER_HTTPS_BASE_URL' 'REPLACE_WITH_CA_BUNDLE' \
    'REPLACE_WITH_COOKIE_JAR' 'REPLACE_WITH_XSRF_HEADER_FILE' 'REPLACE_WITH_SAME_ORIGIN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 5 ] || { echo "the set -- line needs exactly 5 values; not probing"; exit 2; }
  (
    while [ "$#" -gt 0 ]; do
      case "$1" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
        *[[:cntrl:]]*) echo "control character in input; not probing"; exit 2 ;;
      esac
      shift
    done
  ) || exit 2
  case "$1" in https://*) ;; *) echo "HTTPS base URL required; not probing"; exit 2 ;; esac
  case "$5" in https://*) ;; *) echo "HTTPS origin required; not probing"; exit 2 ;; esac
  case "$1$5" in
    *'@'*|*'?'*|*'#'*|*' '*) echo "use URLs without credentials, query, fragment or spaces; not probing"; exit 2 ;;
  esac
  case "$2" in /*) ;; *) echo "absolute CA bundle path required; not probing"; exit 2 ;; esac
  case "$3" in *'='*) echo "cookie file path must not contain =; not probing"; exit 2 ;; esac
  case "$3" in /*) ;; *) echo "absolute cookie file path required; not probing"; exit 2 ;; esac
  case "$4" in /*) ;; *) echo "absolute XSRF header file path required; not probing"; exit 2 ;; esac
  [ -f "$2" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  [ -r "$2" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  [ -f "$3" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  [ -r "$3" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  [ -f "$4" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  [ -r "$4" ] || { echo "a required file is unreadable; not probing"; exit 2; }
  set -- "${1%/}" "$2" "$3" "$4" "$5"

  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      set -- "$1" "$2" "$3" "$4" "$5" 0   # the 6th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Positive control: a live cookie session must retrieve kernel JSON.
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" \
        -w '\ncookie-get=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7##*$'\n'}" "${7%$'\n'*}"   # curl's exit status, then its output
      printf '%s' "$8"
      case "$7:$8" in
        0:*'cookie-get=200 '*) ;;
        0:*) echo "the cookie GET did not return 200, so the session positive control failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
        *) echo "curl exit $7: the cookie GET failed, so the session positive control failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
      esac

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Negative XSRF case: same session and origin, but no X-XSRFToken header.
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" \
        --header 'Content-Type: application/json' --data-binary '{}' \
        -w '\nmissing-xsrf=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7##*$'\n'}" "${7%$'\n'*}"
      printf '%s' "$8"
      case "$7:$8" in
        0:*'missing-xsrf=403 '*) ;;
        0:*'missing-xsrf=2'??' '*) echo "FINDING: the POST without an XSRF header was accepted; record and shut down any kernel it created"; set -- "$1" "$2" "$3" "$4" "$5" 1 ;;
        0:*) echo "the POST without an XSRF header was answered with neither 403 nor a 2xx; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
        *) echo "curl exit $7: the POST without an XSRF header failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
      esac

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Positive XSRF control: creates a disposable kernel; record its returned id.
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header "Origin: $5" --header "@$4" \
        --header 'Content-Type: application/json' --data-binary '{}' \
        -w '\nvalid-xsrf=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7##*$'\n'}" "${7%$'\n'*}"
      printf '%s' "$8"
      case "$7:$8" in
        0:*'valid-xsrf=201 '*) ;;
        0:*) echo "the POST with the matching XSRF header did not return 201, so the XSRF positive control failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
        *) echo "curl exit $7: the POST with the matching XSRF header failed, so the XSRF positive control failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
      esac

      # REASONED: no Jupyter runtime, browser session or test deployment here.
      # Wrong Origin, same authenticated session. This header is not a destination.
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$2" --cookie "$3" --header 'Origin: https://cross-origin.example.com' \
        -w '\nwrong-origin=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/kernels"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
      set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7##*$'\n'}" "${7%$'\n'*}"
      printf '%s' "$8"
      case "$7:$8" in
        0:*'wrong-origin=404 '*) ;;
        0:*'wrong-origin=2'??' '*) echo "FINDING: the wrong-Origin cookie GET was answered with a 2xx"; set -- "$1" "$2" "$3" "$4" "$5" 1 ;;
        0:*) echo "the wrong-Origin cookie GET was answered with neither the native 404 nor a 2xx; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
        *) echo "curl exit $7: the wrong-Origin cookie GET failed; inconclusive"; [ "$6" = 1 ] || set -- "$1" "$2" "$3" "$4" "$5" 3 ;;
      esac
      echo "block exit $6; the response bodies, the kernel ids to record and shut down, and the browser CORS headers are not classified, so judge them yourself"
      exit "$6"
      ;;
  esac
)
```

**The same missing runtime and session prevent these comparisons here.**

| Check | Exposed comparison | Fixed result and positive control |
|---|---|---|
| XSRF | With `disable_check_xsrf = True` only in the isolated fixture, the same-origin POST without the XSRF header creates a kernel. | With `False`, missing XSRF produces `403`; the same session with the matching header creates a kernel with `201`. The cookie GET must also succeed. |
| Origin | With `allow_origin = '*'` only in the isolated fixture, the wrong-Origin cookie GET returns kernel JSON. | With the step 4 origin settings, the wrong-Origin API request is rejected; current native `APIHandler` uses `404`. The same-origin cookie GET returns `200` and kernel JSON. |

The POST body selects the default kernel, and successful creation returns `201`. [Kernel handler](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/handlers.py) (v2.21.1, lines 44 to 66). XSRF and origin outcomes follow the [request-handler checks](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/base/handlers.py) (v2.21.1, lines 530 to 554 and 751 to 758).

A `403` or `404` in both states proves nothing about the intended control. Inspect the response and server logs, and require the positive controls above. Curl does not enforce browser CORS rules: also inspect a cookie-authenticated browser request and confirm that the fixed deployment does not grant cross-origin access through `Access-Control-Allow-Origin` or `Access-Control-Allow-Credentials`. [Origin configuration](https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html).

Record every kernel ID created in either state and shut down those disposable kernels through the authenticated UI. [JupyterLab kernel management](https://jupyterlab.readthedocs.io/en/stable/user/running.html).

### Execution privileges, terminals, and Hub separation (REASONED: Root refusal, terminal availability, Hub admission, distinct execution accounts, browser origins/cookies and protected user configuration. A live Jupyter Server or JupyterHub stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Separate Unix test accounts and browser sessions were not exercised. All fifteen Python configuration blocks passed ASCII, AST and traitlets.Config loading; this does not validate runtime traits. The reusable HTTPS block passed bash -n and ShellCheck 0.11.0 without output and its written placeholders exited 1 without calling curl. Those runs covered the TLS and API access block in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current form, whose guard refusals exit with status 2 and which exits 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Expected permissive root startup, terminals, extra users, shared UIDs/origins and writable user overrides contrast with the fixed refusal, disabled terminals, admission allowlist, distinct UIDs/origins, host-prefixed cookies and protected configuration, retaining the positive controls in each row, per the guide's cited sources this declaration lists in two parts. The guide's cited sources this declaration lists (1 of 2): Jupyter Server startup, dynamic defaults, and root refusal implementation; JupyterHub 6.1.1 authenticator API and PAM admission settings; JupyterHub 6.1.1 configuration reference. The guide's cited sources this declaration lists (2 of 2): JupyterHub spawner API and user-configuration limitations (rolling documentation, checked September 2026); JupyterHub browser security, per-user domains, cookies, and server environments (rolling documentation, checked September 2026); curl options, stdin headers, cookie files, and diagnostic variables.)

Each check below is **REASONED: Jupyter/JupyterHub runtimes and the required test accounts or browser sessions are unavailable here**.

| Check | Concrete demonstration to perform | Exposed versus fixed outcome |
|---|---|---|
| Execution account and root refusal | On an isolated Unix fixture, start `jupyter server` as UID 0 with the step 2 configuration. Compare with root execution explicitly allowed in that fixture. Start the fixed server under its unprivileged account. Inspect server/kernel ownership using `ps -eo pid,ppid,euid,egid,comm`; in a notebook evaluate `import os; print(os.geteuid())`. | The exposed root process can start; the fixed root launch refuses startup. The fixed unprivileged server starts and its local kernel has the intended nonzero UID. |
| Disabled terminals | With terminal support installed, request authenticated `/api/terminals` using the guarded HTTPS block before and after disabling terminals. Keep authenticated `/api/kernels` as the service positive control. | Enabled terminals provide their interface; disabled terminals do not. Kernel execution still works, including shell execution from notebook code. |
| Hub admission | Through `/hub/login`, test an allowed Unix account and a valid Unix account outside the allowlist, including an ordinary historical Hub database user. Establish the latter's valid credentials in the isolated permissive fixture. | Permissive admission accepts the extra account; the fixed policy refuses it while an allowed account can log in and start a server. |
| Hub execution accounts | Start servers for two admitted users. Compare their server process ownership and run `import os; print(os.geteuid())` in each local kernel. | A shared-account fixture uses the same authority; the fixed local-account deployment uses distinct intended Unix UIDs. |
| Hub browser origins and cookies | In each user's own server tab, inspect `location.origin`. Inspect Hub and single-user authentication cookies in browser developer tools. | A single-domain fixture shares an origin; fixed user servers have distinct HTTPS origins. Host-prefixed authentication cookies use the `__Host-` prefix, `Secure`, path `/`, and no `Domain` attribute. |
| Hub user configuration and environment | In a disposable user account, place `c.ServerApp.terminals_enabled = True` in its user configuration while the administrator disables terminals, then restart its server. Compare loading versus disabling user configuration. Check write permissions on the server executable, environment, and launch-path directories as that user. | The exposed fixture loads the user override or permits server replacement. The fixed deployment ignores the user configuration and denies writes to the administrator-controlled server environment; an ordinary notebook remains usable. |

Root refusal and terminal behaviour are documented in the [Server implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (v2.21.1, lines 1984 to 2000 and 3116 to 3126). Hub comparisons follow its [admission rules](https://jupyterhub.readthedocs.io/en/6.1.1/reference/api/auth.html), [local spawner behaviour](https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html), [browser security requirements](https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html), and [host-prefixed cookie configuration](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html), and the 5.5.4 [authenticator API](https://jupyterhub.readthedocs.io/en/5.5.4/reference/api/auth.html) and [configuration reference](https://jupyterhub.readthedocs.io/en/5.5.4/reference/config-reference.html) carry the same settings.

### Listener inventory and external reachability (REASONED: Listener inventory, port selection and external reachability. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local bash -n and ShellCheck 0.11.0 returned 0 without output for ss -tlnp; executing ss -tlnp returned 0 but printed "Cannot open netlink socket: Operation not permitted" and the inventory header. That denied inventory was not retried and proves no listener state. Those runs covered an earlier form of the block, a bare ss -tlnp that ended with ss's own status; the current form, which exits 2 when ss is not installed, 3 when ss fails and otherwise prints a closing line and exits 0, was run only with ss replaced by stubs, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Stub runs of the current form (October 2026, bash 5.3.9, under inherited set -e, a readonly variable and a declare -i variable) exited 0 with a stub ss that passed, 3 with one that failed, and 2 with no ss on PATH, printing "ss is not installed here; not listing sockets". A second host and working external endpoint were not exercised. Expect the exposed published backend to answer and the fixed loopback backend to be private while the public positive control answers; actual ports must be inventoried rather than assumed, per the guide's cited Jupyter Server startup, dynamic defaults, and root refusal implementation; Jupyter Server default port constant; curl options, stdin headers, cookie files, and diagnostic variables.)

**REASONED for the deployed service: no Jupyter runtime is available here.** The locally feasible inventory command was attempted, but the authoring sandbox reported `Cannot open netlink socket: Operation not permitted`. Its otherwise empty output is not evidence that no listeners exist.

```bash
# Deployed listener inventory; no Jupyter runtime here, and the recorded netlink attempt was denied. Expected binds and external controls follow the cited Server sources.
(          # a subshell, so the exit below ends only the subshell; its status is this check's alone: 2 if ss is not installed, 3 if ss fails, otherwise 0
  command -v ss >/dev/null || { echo "ss is not installed here; not listing sockets"; exit 2; }
  ss -tlnp ||   # read every listener; identify the actual Jupyter Server listener and its intended loopback bind
    { echo "ss -tlnp exit $?: the listener inventory failed; inconclusive"; exit 3; }
  echo "unclassified observation: read every listener in the table above, identify the actual Jupyter Server listener and confirm its intended loopback bind; this inventory tests no firewall or forwarding"
  exit 0
)
```

Run this in the deployment's network namespace and identify the actual server listener. It inventories listeners; it does not test a firewall or forwarding. Confirm the intended loopback bind, then repeat the guarded HTTPS probe from another host against the actual external endpoint. In an exposed fixture, a listener published externally can answer; in the fixed private-backend arrangement, only the intended public entry point should be reachable. A backend timeout without a working public positive control is inconclusive.

The standalone port normally starts at 8888 but can change through configuration or port retries. Do not assume it from an example. [Server port implementation](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (v2.21.1, lines 1062 to 1087 and 2721 to 2739), [default port constant](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/__init__.py) (v2.21.1, line 12).

### Verify the reverse-proxy path prefix (REASONED: Prefixed Server and Hub routes, unprefixed aliases and authenticated WebSocket positive controls. A live stand-up of Jupyter Server or JupyterHub with configurable-http-proxy opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The base_url and bind_url Python blocks parsed and loaded into traitlets.Config; output was PASS. No proxy or spawned user session was exercised. Expect the inconsistent fixture to expose an alias outside the prefix, and the fixed fixture to retain only intended prefixed application access with working authentication and WebSockets, per the guide's cited JupyterHub 6.1.1 proxy configuration and path prefix; configurable-http-proxy 5.3.0 command-line options; Jupyter Server v2.21.1 application definition and HTTP-server construction.)

**REASONED:** no Jupyter Server, JupyterHub, or configurable-http-proxy is running in the authoring environment.

In an isolated fixture, compare the consistent-prefix configuration from section 8 against a deployment where only part of the stack carries the prefix. Request the prefixed application routes (for a standalone Server, `GET /jupyter/api/kernels`; for JupyterHub, `GET /jupyter/hub/login` and a spawned user's actual prefixed URL) and, separately, probe any unprefixed alias (`GET /api/kernels`, `GET /hub/login`). The fixed configuration keeps every application route behind the intended authentication and routing boundary and leaves no unprefixed alias serving the application, while a bare `404` proves neither authentication nor a working deployment, so confirm authenticated access and a working kernel WebSocket on the prefixed path as the positive control. See the [JupyterHub proxy configuration](https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html).

### Verify forwarded-header trust (REASONED: Spoofed forwarded address/scheme/Forwarded headers, genuine Host and a spoofed X-Forwarded-Host, direct backend access and login/WebSocket controls. A live stand-up of Jupyter Server or JupyterHub behind a real ingress opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Python ingress-related configuration parsed and loaded into traitlets.Config; output was PASS. No real ingress, external network vantage or browser cookie session was exercised. Expect spoofed address/scheme to take effect with pass-through headers or reachable trusted backends, but not behind the private sanitizing ingress; host-prefixed cookies remain Secure unless cookie_options overrides them, except the single-user OAuth state cookie, whose Secure flag follows JUPYTERHUB_PUBLIC_URL or the detected scheme or, when neither sets it, a cookie_options entry. A spoofed X-Forwarded-Host needs its own check, because its handling is not established at 6.1.1 or 5.5.4, and genuine Host needs its own rejection check, per the guide's cited sources this declaration lists in two parts. The guide's cited sources this declaration lists (1 of 2): JupyterHub 6.1.1 configuration reference; JupyterHub 6.1.1 configuration reference (trusted_downstream_ips, public_url, internal_ssl); Jupyter Server v2.21.1 application definition and HTTP-server construction. The guide's cited sources this declaration lists (2 of 2): JupyterHub 6.1.1 application (internal_ssl and forwarded-header trust); JupyterHub 6.1.1 and 5.5.4 forwarded-scheme detection, Hub cookie attributes and single-user OAuth cookie.)

**REASONED:** no Jupyter Server or JupyterHub behind a real ingress is available in the authoring environment.

Send separate and conflicting spoofed `X-Forwarded-For`/`X-Real-IP` and `X-Scheme`/`X-Forwarded-Proto` headers through the real ingress, and separately attempt to reach the backend directly from an untrusted network. Compare the request-derived client address in the logs, the redirect targets, and the cookie `Secure` attribute. In the exposed fixture (header trust enabled while the backend is reachable or the proxy passes headers through unchanged) the attacker-controlled address or scheme takes effect; in the fixed fixture (section 9: a private bind plus a sanitizing ingress) it does not, while a legitimate login and WebSocket still succeed. Include a spoofed `Forwarded: proto=http` header and compare the detected browser-facing scheme (the redirect target and any scheme-derived decision) between the sanitizing and the pass-through ingress. Because section 6 sets `cookie_host_prefix_enabled`, the single-user OAuth cookie that records the login is set `Secure` whatever scheme is detected, so for that cookie a stripped-`Secure` result is demonstrable only in an isolated fixture with host-prefixed cookies disabled; with this guide's configuration, verify instead that the ingress removes or overwrites `Forwarded`. That code applies `cookie_options` after setting `Secure` (6.1.1 `services/auth.py` lines 1289 to 1298, 5.5.4 lines 1248 to 1257), so never set `secure` to false in a `cookie_options` override. The `cookie_options` help text suggests `secure=True` "if served on HTTPS and default HTTPS discovery fails (e.g. behind some proxies)" (6.1.1 `services/auth.py` lines 410 to 415, 5.5.4 lines 409 to 416). The single-user OAuth state cookie differs: under the same setting its name is the `__Host-` prefixed cookie name plus `-oauth-state` (6.1.1 `services/auth.py` lines 912 to 923), but the code that sets it does not take `Secure` from that prefix. It is set `Secure` when `JUPYTERHUB_PUBLIC_URL` has the `https` scheme or, with that variable empty or unset, when `get_browser_protocol` returns `https` (lines 1211 to 1217). When neither applies, a `cookie_options` entry that sets `secure` to true adds it, but no `cookie_options` entry can remove it once one of those conditions has set it (lines 1219 to 1226). 5.5.4 has the same code (lines 903 to 914, 1175 to 1181 and 1183 to 1190). The spawner passes `Spawner.public_url` as `JUPYTERHUB_PUBLIC_URL` (6.1.1 `spawner.py` line 1380, 5.5.4 line 1324), but no file read here sets `Spawner.public_url`, and `user.py` was not read, so whether that variable is set is not established at 6.1.1 or 5.5.4. As this guide's inference, without that variable or a `cookie_options` entry that sets `secure`, a spoofed `Forwarded: proto=http` that reaches the server can make the server send the state cookie without `Secure`, which browsers that enforce the `__Host-` prefix may reject, so inspect that cookie's `Set-Cookie` header in both fixtures too. The Hub's own cookie code forces `Secure` and path `/` on a `__Host-` cookie after applying `cookie_options` (6.1.1 `handlers/base.py` lines 711 to 717, 5.5.4 lines 679 to 685). The host is a separate case: the forwarded-header machinery rewrites only the client address and scheme, not the host. The standalone Server's origin check reads the genuine `Host` header. In the JupyterHub 6.1.1 and 5.5.4 files read here (`app.py`, `handlers/base.py`, `services/auth.py`, `utils.py` and `proxy.py`), `forwarded_host_header` appears only in its trait definition (6.1.1 `app.py` lines 1027 to 1035, 5.5.4 lines 982 to 990), and the Hub's Host checks read `self.request.host`. Whether another file, such as the `_xsrf_utils.py` module those handlers import, consumes `forwarded_host_header` or `X-Forwarded-Host` is not established at 6.1.1 or 5.5.4. Test, therefore, that a spoofed `X-Forwarded-Host` has no effect, and test an unintended genuine `Host` value at the ingress as well. See the [JupyterHub configuration reference](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html), the [6.1.1 single-user OAuth cookie](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/services/auth.py) and [5.5.4 single-user OAuth cookie](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/services/auth.py), the [6.1.1 Hub cookie attributes](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/handlers/base.py) and [5.5.4 Hub cookie attributes](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/handlers/base.py), and the [Jupyter Server HTTP-server construction](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py). The spawner environment is in the [6.1.1 spawner](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/spawner.py) and [5.5.4 spawner](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/spawner.py).

### Verify internal Hub TLS (REASONED: Each internal Hub connection, client trust, hostname verification and the excluded kernel ZeroMQ transport. A live stand-up of JupyterHub with a spawner and single-user server opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Internal SSL configuration parsed and loaded into traitlets.Config; output was PASS. Local openssl generated a certificate, printed OK for trusted localhost verification and error 62, hostname mismatch, for wrong.internal. This tests local certificate verification only, not mutual TLS or Hub connections. Expect plaintext with internal TLS off, trusted client success and untrusted client/wrong-hostname rejection with it on at Hub 5.4+, at 6.1.1 through the aiohttp client context and at 5.5.4 through Tornado's client, retaining login, spawn, notebook and WebSocket controls; kernel ZeroMQ encryption remains a separate check, per the guide's cited sources this declaration lists in two parts. The guide's cited sources this declaration lists (1 of 2): JupyterHub 6.1.1 configuration reference (trusted_downstream_ips, public_url, internal_ssl); JupyterHub 6.1.1 changelog (internal hostname verification from 5.4); JupyterHub 6.1.1 application (internal_ssl and forwarded-header trust); JupyterHub 6.1.1 internal HTTP client. The guide's cited sources this declaration lists (2 of 2): JupyterHub 6.1.1 and 5.5.4 internal TLS context; JupyterHub 5.5.4 application; Jupyter messaging protocol (jupyter_client 8.6.3); Jupyter kernel connection defaults (jupyter_client 8.6.3).)

**REASONED:** no JupyterHub, spawner, or single-user server is available in the authoring environment.

Keep the public HTTPS listener constant and compare internal TLS off against on (section 10). Inspect each actual internal connection (Hub to proxy API, proxy to Hub, proxy to single-user server, and Hub to single-user server): with internal TLS on, a request using the intended internal certificate authority and client certificate succeeds, while one presenting an untrusted certificate is rejected. A connection under an incorrect server hostname is likewise expected to be rejected on JupyterHub 5.4 or later (which enabled internal hostname verification by default), with internal TLS on; section 10 says which Hub connections that rests on at 6.1.1 and 5.5.4 and which are not established. Also present a certificate from a publicly trusted CA that is not the internal CA, since both releases' internal TLS context also loads the system's default CA certificates. Require a successful login, spawn, notebook execution, and kernel WebSocket exchange as positive controls. The single-user-server-to-kernel ZeroMQ connection must be observed separately and must not be counted as encrypted by this test, since `internal_ssl` does not cover it. See the [internal_ssl definition](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py) and the [Jupyter messaging protocol](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst).

### Verify NativeAuthenticator password and signup policy (REASONED: NativeAuthenticator password length/common-password checks, threshold/cooldown, pending-account oracle, approval/admission, signup disabling and bcrypt storage; PAM remains a host-policy case. A live stand-up of JupyterHub with NativeAuthenticator opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. No browser signup session or Hub database was exercised. Python password and signup configuration parsed and loaded into traitlets.Config; output was PASS. Expected exposed empty/weak-password acceptance, disabled or zero-cooldown lockout and open/preauthorized signup contrast with the configured rejection, delayed login, approval hold and disabled-route 404; the pending-account oracle and first-signup allowlist exception remain exposed as described, and stored passwords must be bcrypt hashes, per the guide's cited sources this declaration lists. The guide's cited sources this declaration lists: NativeAuthenticator configuration traits and password, lockout, and signup enforcement; NativeAuthenticator quickstart and authenticator_class; NativeAuthenticator request handlers (signup 404 when signup is disabled, and the authorization panel).)

**REASONED:** no JupyterHub with NativeAuthenticator installed, and no browser signup session, is available in the authoring environment. This check applies only to a Hub that uses NativeAuthenticator (section 11); a PAM deployment verifies its password policy on the host instead.

On an authorized Hub configured with the section 11 settings, exercise the signup form at `/hub/signup` and the login form (these Hub paths sit under `JupyterHub.base_url`, so a section 8 prefix makes them `/jupyter/hub/...`), varying one control at a time. Test the length floor and the common-password check separately, because under the section 11 settings NativeAuthenticator accepts a signup password only when it clears both (its `is_password_strong` requires `len(password) >= minimum_password_length` and, when `check_common_password` is on, that the password is not in the list). A password that meets the length floor but appears in the common-password list is rejected only when `check_common_password` is on and accepted when it is off, which isolates that control (lower `minimum_password_length` for this case if no listed password is long enough), while a password below the floor is rejected on length alone. Even an empty password is accepted with the shipped defaults (`minimum_password_length` effectively `0` since its `.tag(default=1)` annotation is metadata rather than the trait default, and `check_common_password` `False`). Confirm each rejection is the server's signup response, not a client-side hint. For lockout, verify the failure threshold and the cooldown length separately, because a zero cooldown is not the same as a disabled lockout: with `allowed_failed_logins = 0` the account is never throttled, while with a positive threshold the account is blocked after that many consecutive failures. An immediate retry, within the same second as the last failure, is refused at both `0` and `1200`, so it does not distinguish them; instead submit the correct password about two seconds after the last failure, when it is accepted at the effective-`0` default but still refused at `seconds_before_next_try = 1200`. The lockout also does not stop password guessing against a not-yet-approved account: while such an account is blocked, the login handler still returns a distinct authorization-pending message for a correct password and the generic error for a wrong one, a password-confirmation oracle the lockout leaves open. To exercise the approval hold in isolation from Hub admission, set `allow_all = True` with an empty `allowed_users` and sign up a fresh non-admin username: with `open_signup` off it is created unauthorized and cannot log in until an administrator approves it on `/hub/authorize`, whereas `open_signup = True` admits it at signup. Then confirm the reverse exposure by adding a not-yet-registered username to `allowed_users` and observing that its first signup is authorized immediately without approval. With `enable_signup = False`, a GET or an otherwise valid POST to the signup route is refused (HTTP 404) and creates no account, while with signup enabled the same form renders and accepts a valid registration. Read the stored credential directly (the `password` column of NativeAuthenticator's `users_info` table in the Hub database) to confirm it is a bcrypt hash, not reversible text. A wrong username, an unmigrated database, or a stale browser session is inconclusive. See the [NativeAuthenticator configuration](https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py) and the [signup and authorization handlers](https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/handlers.py).

### Local authoring checks and REASONED service checks

REASONED: Earlier local authoring inventory. Local marking review (October 2026, bash 5.3.9) ran five Bash blocks through bash -n and ShellCheck 0.11.0 (exit 0, no output) and fifteen Python blocks through ASCII, ast.parse and traitlets.Config checks (15 PASS). The bash -n and ShellCheck runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and the listener inventory as a bare ss -tlnp, and those local runs were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The following checks were run without editing files or running `tools/run_all_checks.sh`:

- REASONED: Python configuration construction only. Local marking review (October 2026, bash 5.3.9) loaded all fifteen ASCII, ast.parse-valid blocks into traitlets.Config and printed 15 PASS; Jupyter trait recognition was not tested. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Trait recognition awaits an isolated Jupyter runtime, per the guide's cited Jupyter Server configuration reference and authentication migrations (rolling documentation, checked September 2026) and JupyterHub 6.1.1 configuration reference. All fifteen Python configuration blocks passed ASCII and Python syntax checks and loaded into `traitlets.Config`. This checks configuration-file construction, not Jupyter trait recognition or runtime enforcement.
- REASONED: Bash syntax and lint only. Local marking review (October 2026, bash 5.3.9) ran bash -n and ShellCheck 0.11.0 with Bash source mode on all five blocks; each exited 0 with no output. Those runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and the listener inventory as a bare ss -tlnp, and they were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. All five Bash blocks passed `bash -n` and ShellCheck.
- REASONED: Written-placeholder guard only. Local marking review (October 2026, bash 5.3.9) ran both HTTP blocks under bash -u with curl and python3 stubbed; each exited 1 with "substitute every placeholder inside the quotes; not probing" before any CURL_STUB call. Those runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current forms, whose guard refusals exit with status 2 and which exit 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover them. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The substituted browser and cookie fixtures printed one and four CURL_STUB lines, respectively; local argument handling follows the guide's cited curl options, stdin headers, cookie files, and diagnostic variables. Both HTTP blocks, in their earlier form, refused their placeholders locally under `bash -u`.
- REASONED: Positional and input guards only. Local marking review (October 2026, bash 5.3.9) ran an 80-case bash -u matrix: 72 refusals from eight positions times nine inputs (empty, REPLACE_WITH_, <, >, example.com, LF, CR, tab and SOH), plus valid browser and cookie cases, two bad markers, two short counts and two IFS=0 count cases. The 72 refused before curl; valid cases printed one and four CURL_STUB lines; marker and count cases exited 1 with their explicit messages. With IFS=0, quoted guards refused 30 and 50 values with exact-count messages, while unquoted controls reached one and four CURL_STUB calls. Separate branches exited 1 with "choose browser or token; not probing", "cookie file path must not contain =; not probing" and "CA bundle is not a readable file; not probing". These runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current forms, whose guard refusals exit with status 2 and which exit 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover them. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local curl argument handling follows the guide's cited curl options, stdin headers, cookie files, and diagnostic variables. Eighty positional-guard cases passed, covering valid inputs, empty values, embedded placeholders, angle brackets, the example hostname, control characters, missing markers, wrong argument counts, and an altered `IFS` count case.
- REASONED: Token guard only. Local marking review (October 2026, bash 5.3.9) ran seven bash -u cases with python3 and curl stubbed: the valid dummy token printed three CURL_STUB lines and exited 0; empty, REPLACE_WITH_ and angle-bracket tokens printed "a real token is required; not probing"; LF, CR and tab printed "token contains a control character; not probing"; each refusal exited 1 after one anonymous CURL_STUB line. These runs covered the TLS and API access block in an earlier form, whose guard refusals exited with status 1, and were not repeated on the current form, whose guard refusals exit with status 2 and which exits 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Header input behaviour follows the guide's cited curl options, stdin headers, cookie files, and diagnostic variables. Seven token-guard cases passed, including rejection of LF, CR, and tab characters before header construction.
- REASONED: Dummy-token transport only. Local marking review (October 2026, bash 5.3.9) ran the token path with python3 and curl stubbed; it exited 0 with three CURL_STUB lines. That run covered the TLS and API access block in an earlier form, whose guard refusals exited with status 1, and was not repeated on the current form, whose guard refusals exit with status 2 and which exits 1 for a finding and 3 for an inconclusive result; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Captured curl arguments began -q and -g and omitted DUMMY_TOKEN; stdin held two "Authorization: token DUMMY_TOKEN" headers. No HTTP request ran. A live Jupyter Server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Header stdin handling follows the guide's cited curl options, stdin headers, cookie files, and diagnostic variables. A local dummy-token argument harness confirmed that the authenticated curl invocation starts with `-q -g` and receives the token on stdin, not in its arguments. This harness made no HTTP request and simulated no Jupyter behaviour.
- DEMONSTRATED: Local guide-link resolution only. Local marking review (October 2026) checked a scratch copy with a free-certificates.md link replaced by tls.md: that target was absent; in the fixed guide, all six distinct local targets resolved and no tls.md link remained. The referenced local certificate, proxy, Cloudflare, and MFA guides exist. No `tls.md` link is used.

| Scope | Status | Exposed-versus-fixed checks |
|---|---|---|
| Jupyter controls | REASONED: This table inventories the live comparisons, not observed results. A live Jupyter Server or JupyterHub stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local marking review ran all five Bash blocks through bash -n and ShellCheck 0.11.0: exit 0 with no output; all fifteen Python configuration blocks passed ASCII, AST and traitlets.Config loading. With external commands stubbed, both written HTTP placeholders exited 1 with "substitute every placeholder inside the quotes; not probing"; valid browser and cookie fixtures exited 0 with one and four CURL_STUB lines respectively. Invalid marker, count, empty, placeholder, angle-bracket, example-host, control-character, scheme, URL and file fixtures exited 1 before curl. These bash -n, ShellCheck and stub runs covered the two guarded HTTP blocks in an earlier form, whose guard refusals exited with status 1, the bash -n and ShellCheck runs also covered the listener inventory as a bare ss -tlnp, and the stub runs were not repeated on the current forms. In the current forms the HTTP blocks' guard refusals exit with status 2, those blocks exit 1 for a finding and 3 for an inconclusive result, the inventory exits 2 when ss is not installed and 3 when ss fails, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three; stub runs of the inventory's current form are recorded at its heading. Local openssl verification printed OK for trusted localhost and error 62 for a wrong hostname. These runs do not establish the exposed-versus-fixed service outcomes listed in the table. The required versions, Unix accounts, TLS/DNS, browser sessions, terminal support, extension routes, second-host vantage, real ingress, spawner and NativeAuthenticator database remain prerequisites for those comparisons, per the guide's cited sources, which this cell lists in six parts. The guide's cited sources (1 of 6): Jupyter Server public server guide and password/TLS setup (rolling documentation, checked September 2026); Jupyter Server security and token/password authentication (rolling documentation, checked September 2026); Jupyter Server API base handler, protected API responses, and metrics enforcement. The guide's cited sources (2 of 6): Jupyter Server API reference for authentication, origin, Host, root, and terminal controls (rolling documentation, checked September 2026); Jupyter Server startup, dynamic defaults, and root refusal implementation; Jupyter Server default port constant; Jupyter Server identity provider and token-authenticated origin exception. The guide's cited sources (3 of 6): Jupyter Server Host, origin, XSRF, and default authentication implementation; Jupyter Server kernel API implementation; JupyterLab kernel and terminal management; JupyterHub 6.1.1 authenticator API and PAM admission settings; JupyterHub 6.1.1 configuration reference. The guide's cited sources (4 of 6): JupyterHub spawner API and user-configuration limitations (rolling documentation, checked September 2026); JupyterHub browser security, per-user domains, cookies, and server environments (rolling documentation, checked September 2026); curl options, stdin headers, cookie files, and diagnostic variables. The guide's cited sources (5 of 6): JupyterHub 6.1.1 proxy configuration and path prefix; configurable-http-proxy 5.3.0 command-line options; NativeAuthenticator configuration traits and password, lockout, and signup enforcement; NativeAuthenticator request handlers (signup 404 when signup is disabled, and the authorization panel). The guide's cited sources (6 of 6): JupyterHub 6.1.1 configuration reference (trusted_downstream_ips, public_url, internal_ssl); JupyterHub 6.1.1 changelog (internal hostname verification from 5.4); Jupyter Server v2.21.1 application definition and HTTP-server construction; JupyterHub 6.1.1 application (internal_ssl and forwarded-header trust); Jupyter messaging protocol (jupyter_client 8.6.3). REASONED from the cited vendor documentation and pinned implementations, not demonstrated. Requires Jupyter Server 2.18+, JupyterHub 6.1.0 or later or 5.5.3 or later, suitable Unix test accounts, TLS/DNS, browser sessions, terminal support, representative extension routes, and an authorized isolated deployment. | Check TLS and anonymous/authenticated API access; external reachability and listener inventory; metrics and unclassified extension authentication; cookie-session XSRF and origin checks; Host rejection with an authenticated positive control; root refusal and workload UIDs (items, part 1 of 2). The items to check (part 2 of 2): terminal disabling; Hub admission including historical users; separate execution accounts and browser origins; host-prefixed cookies; ignored user configuration and protected server environments. Record versions, requests, responses, logs, positive controls, and cleanup. For the sections 8 to 10 controls, check a route reaching the application outside the intended prefix versus a consistent prefix (items, part 1 of 3). The items to check for the sections 8 to 10 controls (part 2 of 3): a spoofed forwarded IP and scheme taking effect with header trust misconfigured versus rejected behind a sanitizing ingress, a spoofed Forwarded header not changing the detected browser scheme behind the ingress, and a spoofed X-Forwarded-Host having no effect (its handling is not established at 6.1.1 or 5.5.4). The items to check for the sections 8 to 10 controls (part 3 of 3): internal Hub traffic in plaintext versus TLS with client-certificate verification, keeping the kernel ZeroMQ transport excluded from the internal-TLS claim. For the section 11 NativeAuthenticator controls, check a sub-minimum-length or empty password rejected at signup versus accepted under the effective-zero defaults, a login refused after the configured failed-attempt threshold (items, part 1 of 4). The items to check for the section 11 NativeAuthenticator controls (part 2 of 4): the cooldown length confirmed by a correct password refused about two seconds after the last failure at seconds_before_next_try 1200 versus accepted at the effective-zero cooldown, the lockout disabled entirely at allowed_failed_logins 0. The items to check for the section 11 NativeAuthenticator controls (part 3 of 4): the pending-account password-confirmation oracle (a distinct awaiting-authorization message for a correct password during lockout), a self-registered account held for administrator authorization on /hub/authorize (with allow_all set and allowed_users empty) versus admitted immediately under open_signup. The items to check for the section 11 NativeAuthenticator controls (part 4 of 4): a not-yet-registered allowed_users username claimed as an immediately-authorized account at its first signup, the signup route refusing GET and POST with 404 when enable_signup is False, and the stored password held as a bcrypt hash. |

## 8. Preserve the deployment path prefix through the reverse proxy

When a reverse proxy serves Jupyter under a path prefix such as `/jupyter/`, the application must be told the same prefix, or another route can reach the application outside the authentication and routing boundary the proxy establishes. Both the standalone Server and JupyterHub default their prefix to `/`.

For a standalone Jupyter Server behind a prefix, set it in `jupyter_server_config.py`:

```python
c.ServerApp.base_url = '/jupyter/'
```

The Server applies the prefix to its registered handlers. See the [Server v2.21.1 application definition](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (lines 534 to 539 and 1531 to 1548).

For JupyterHub behind the same-host proxy, set the listener and base URL together in `jupyterhub_config.py`:

```python
c.JupyterHub.bind_url = 'http://127.0.0.1:8000/jupyter/'
```

This sets both the bind address and `JupyterHub.base_url`. Configure the prefix consistently on both sides of the proxy; do not combine a `bind_url` prefix with separate conflicting URL settings, and do not reach for the configurable-http-proxy `--no-include-prefix` or `--no-prepend-path` flags as a generic prefix fix, since neither establishes an authentication boundary. The 6.1.1 and 5.5.4 proxy configuration pages give the same `bind_url` example, which "Sets protocol, IP, base_url", and the 6.1.1 `bind_url` and `base_url` definitions are at `app.py` lines 728 to 775 (5.5.4: lines 695 to 738). See the [JupyterHub 6.1.1 proxy configuration](https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html), the [JupyterHub 5.5.4 proxy configuration](https://jupyterhub.readthedocs.io/en/5.5.4/howto/configuration/config-proxy.html) and the [configurable-http-proxy 5.3.0 command-line options](https://raw.githubusercontent.com/jupyterhub/configurable-http-proxy/5.3.0/bin/configurable-http-proxy).

JupyterHub 6 adds Unix-socket support between the Hub and configurable-http-proxy. At 6.1.1, `bind_url` also accepts an `http+unix://` URL holding the URL-encoded socket path, and the Hub then starts the proxy with `--socket` (and `--api-socket` for a socket API URL) in place of `--ip` and `--port` (`proxy.py` lines 736 to 762). The 5.5.4 `proxy.py` always passes `--ip`, `--port`, `--api-ip` and `--api-port` (lines 720 to 732). 6.1.1 also carries the 6.0.1 fix listed as "fix proxy binding on all interfaces". This section's loopback `bind_url` uses neither feature. The 5.3.0 option list defines `--socket` and `--api-socket`, but whether configurable-http-proxy 5.3.0 works with JupyterHub 6.1.1 is not established here: no compatibility statement was found and nothing was run. [Upgrading to JupyterHub 6](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md), [6.1.1 proxy launch](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/proxy.py), [5.5.4 proxy launch](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/proxy.py), [6.1.1 changelog](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md).

## 9. Trust forwarded headers only behind a sanitizing ingress

A standalone Jupyter Server does not trust proxy-forwarded headers by default (`ServerApp.trust_xheaders` is `False`), while JupyterHub constructs its HTTP server with forwarded-header trust enabled. Trusting these headers while the backend can still be reached by an untrusted peer, or while the proxy passes client-supplied headers through unchanged, lets a client spoof its apparent address or scheme. Bind the backend privately and trust the headers only behind an ingress that overwrites them. The Hub builds its HTTP server with `xheaders=True` and `trusted_downstream=self.trusted_downstream_ips` at 6.1.1 (`app.py` lines 3889 to 3894) and at 5.5.4 (lines 3745 to 3750). [JupyterHub 6.1.1 application](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py), [JupyterHub 5.5.4 application](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/app.py).

For a standalone Server behind a same-host TLS ingress, in `jupyter_server_config.py`:

```python
c.ServerApp.ip = '127.0.0.1'
c.ServerApp.trust_xheaders = True
```

Keep `trust_xheaders` at `False` unless a trusted ingress sets `X-Forwarded-For`/`X-Real-IP` and `X-Scheme`/`X-Forwarded-Proto` itself. See the [Server v2.21.1 HTTP-server construction](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py) (lines 1744 to 1753 and 2659 to 2665).

For the same-host JupyterHub topology, in `jupyterhub_config.py`:

```python
c.JupyterHub.hub_ip = '127.0.0.1'
c.JupyterHub.trusted_downstream_ips = ['127.0.0.1']
c.JupyterHub.public_url = 'https://jupyter.example.com/jupyter/'
```

`trusted_downstream_ips` names the proxy hops that are trusted and skipped when Hub selects the client address from `X-Forwarded-For`; it controls address selection, not whether a connecting peer may supply headers, so it is not a substitute for an ingress that sanitizes them, and an empty list does not disable header trust. The ingress must normalize both forwarded-IP forms (`X-Forwarded-For`, `X-Real-IP`), both scheme forms (`X-Forwarded-Proto`, `X-Scheme`), and the standard RFC 7239 `Forwarded` header, and reject unintended `Host` values. JupyterHub reads the `Forwarded` header before the `X-` scheme forms when deciding the browser-facing scheme, so the ingress must own it too: `get_browser_protocol` takes `proto` from the first `Forwarded` entry as its "first choice" and only then `X-Scheme` or `X-Forwarded-Proto` (6.1.1 `utils.py` lines 819 to 844, 5.5.4 lines 788 to 813). In this guide's configuration `public_url` (this section) and `cookie_host_prefix_enabled` (section 6) already guard the scheme-derived redirect and single-user OAuth cookie paths, but leaving `Forwarded` unsanitized still lets a client-supplied value reach any scheme decision, so normalize it alongside the other forwarded headers. Binding to loopback excludes a remote peer but not other local processes. The 6.1.1 and 5.5.4 configuration references document the same `trusted_downstream_ips`, `public_url` and `hub_ip` settings. See the [JupyterHub 6.1.1 configuration reference](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html), the [JupyterHub 5.5.4 configuration reference](https://jupyterhub.readthedocs.io/en/5.5.4/reference/config-reference.html), and the [6.1.1 forwarded-scheme detection](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/utils.py) and [5.5.4 forwarded-scheme detection](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/utils.py).

## 10. Encrypt internal Hub communication

Public HTTPS (sections 3 and 4) protects only the browser-facing listener. By default JupyterHub leaves the internal traffic between the Hub, the proxy, and the single-user servers unencrypted (`internal_ssl` is `False`). Enable internal TLS in `jupyterhub_config.py`:

```python
c.JupyterHub.internal_ssl = True
c.JupyterHub.internal_certs_location = '/srv/jupyterhub/internal-ssl'
```

JupyterHub then generates an internal certificate authority and per-component certificates and enables TLS with client-certificate verification for the Hub-to-proxy API, the proxy-to-Hub and proxy-to-single-user connections, and the Hub-to-single-user connection used during spawn readiness. Treat the certificate directory as protected persistent state, and give the spawner the ability to deliver each server's key, certificate, and trust bundle (`LocalProcessSpawner` relocates them; a remote spawner needs its own `move_certs` support). Set `Spawner.ssl_alt_names` to the actual connection names when they are not the defaults, and never resolve a certificate error by disabling verification. Internal hostname verification is on by default from [JupyterHub 5.4](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md), whose changelog entry reads "Fix internal ssl: do not disable hostname verification by default" (6.1.1 changelog line 570, [5.5.4 changelog](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/docs/source/reference/changelog.md) line 334); earlier 5.x releases left it disabled, so upgrade before relying on it. The `internal_ssl` and `internal_certs_location` definitions are at 6.1.1 `app.py` lines 600 to 616 and 5.5.4 lines 567 to 583. See the [internal_ssl definition](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py) and the JupyterHub [6.1.1](https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html) and [5.5.4](https://jupyterhub.readthedocs.io/en/5.5.4/reference/config-reference.html) configuration references.

The Hub's own internal client differs between the two releases. JupyterHub 6.0 replaced Tornado's HTTP client with aiohttp for internal requests ("use aiohttp for internal http requests", #5447). At 6.1.1 the Hub builds its internal client context with `make_ssl_context` and its default `purpose=ssl.Purpose.SERVER_AUTH` (`app.py` lines 2022 to 2034), which sets `ssl_context.verify_mode = ssl.CERT_REQUIRED` and `ssl_context.check_hostname = True` (`utils.py` lines 155 to 204). `JupyterHubHTTPClient` applies that context after any `connector_options` a deployment sets, so configuration cannot replace it (`httpclient.py` lines 114 to 118). At 5.5.4 the Hub instead configures Tornado's `AsyncHTTPClient` with the internal CA bundle, client key and certificate and `validate_cert=True` (`app.py` lines 1993 to 2004). As this guide's inference, Tornado then checks hostnames and aiohttp uses the passed context as given; neither library's source was read here. Both releases' `make_ssl_context` also calls `ssl_context.load_default_certs()` after loading the internal CA (6.1.1 line 199, 5.5.4 line 170), so as this guide's inference from Python's `ssl` documentation, not read here, the context may also trust the system's default CAs. Not established at 6.1.1 or 5.5.4: whether the spawn-readiness request uses the client context above, since `user.py` was not read at either release and the 5.5.4 `wait_for_http_server` takes its SSL context per call (`utils.py` lines 294 to 296), and how configurable-http-proxy checks hostnames on its proxy-to-Hub and proxy-to-single-user connections. [6.1.1 internal TLS context](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/utils.py), [6.1.1 internal HTTP client](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/httpclient.py), [5.5.4 application](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/app.py), [5.5.4 internal TLS context](https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/utils.py), [Upgrading to JupyterHub 6](https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md).

Internal TLS does not encrypt the single-user server's connection to its kernels. That link uses the Jupyter messaging protocol over ZeroMQ, whose HMAC signature authenticates messages but does not encrypt them. Local kernels bind loopback; a remote-kernel deployment needs a separately configured encrypted transport such as an SSH tunnel, which this guide does not configure. See the [Jupyter messaging protocol](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst) and the [kernel connection defaults](https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/jupyter_client/connect.py).

Jupyter Server 2.20.0 added an optional kernel transport encryption policy ("Add a toggle to enable curve encryption for all kernels that support it", #1638). At v2.21.1, `MappingKernelManager.transport_encryption` takes `'disabled'`, `'auto'` or `'required'`, defaults to `'disabled'`, and its help text says "'disabled' (default) does not provision Curve credentials, 'auto' provisions when the kernelspec declares support, and 'required' enforces provisioning and fails kernel startup if encryption cannot be applied." (`kernelmanager.py` lines 71 to 81). The Server passes any value other than `'disabled'` on to jupyter_client's kernel start (lines 220 to 225, 254 and 260). As this guide's inference, it therefore needs a jupyter_client release that accepts `transport_encryption`, and for `'auto'` a kernelspec that declares support. The cited jupyter_client 8.6.3 files do not mention Curve encryption, and whether 8.6.3 supports this policy, and which jupyter_client release v2.21.1 requires, are not established here. This guide does not configure the policy, so its default leaves the kernel link unencrypted, as above. [Kernel transport encryption policy](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/kernelmanager.py), [Server v2.21.1 changelog](https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/CHANGELOG.md).

## 11. Harden NativeAuthenticator password and signup policy

Section 5 configures `PAMAuthenticator`, which delegates credentials to the host's user accounts and so inherits the operating system's password and lockout policy. A deployment that instead manages its own login names and passwords in the Hub, rather than authenticating against host accounts, commonly reaches for the separate [NativeAuthenticator](https://native-authenticator.readthedocs.io/en/1.3.0/quickstart.html) package (`c.JupyterHub.authenticator_class = 'native'`). It stores each password as a bcrypt hash in the Hub database and adds its own signup form, so the host no longer supplies the login password policy and NativeAuthenticator's own settings become the only floor. NativeAuthenticator replaces the host only as the credential store for login; a spawner such as section 5's `LocalProcessSpawner` may still require a matching Unix account to run each user's server. Those defaults are permissive, and two of them are weaker than the defaults their own source declarations annotate, so set them explicitly. This section applies only when NativeAuthenticator is the authenticator; under `PAMAuthenticator` the operating system owns these controls.

In `jupyterhub_config.py`, set a password policy and a login-failure lockout:

```python
c.NativeAuthenticator.minimum_password_length = 12
c.NativeAuthenticator.check_common_password = True
c.NativeAuthenticator.allowed_failed_logins = 5
c.NativeAuthenticator.seconds_before_next_try = 1200
```

Set each of these explicitly; for two of them the shipped runtime defaults are weaker than the `.tag(default=...)` annotations in their source declarations suggest. `minimum_password_length` and `seconds_before_next_try` are declared as `Integer(...).tag(default=1)` and `.tag(default=600)`, but that tag is traitlets metadata, not the trait's default value: an `Integer` with no explicit default is `0`, so both effectively default to `0`. For `seconds_before_next_try` the package's own help text and documentation also state the 600-second default that the code does not implement; for `minimum_password_length` the documentation is accurate that there is no strength check by default. A `minimum_password_length` of `0` accepts even an empty password, since the check applied when a password is set is `len(password) >= minimum_password_length`; and a `seconds_before_next_try` of `0` leaves essentially no cooldown after a block. `check_common_password` and `allowed_failed_logins` instead default to the permissive values their declarations annotate (`False` and `0`): with common-password checking off any listed password is allowed, and with `allowed_failed_logins` at `0` lockout is disabled and the login endpoint can be brute-forced until it is set. Enabling `check_common_password` rejects a new password found in the package's bundled common-password list (its 10,000-entry `common-credentials.txt`), a floor against the most obvious choices, not a breach-corpus check. Pair `allowed_failed_logins` with `seconds_before_next_try` to throttle repeated login attempts after that many consecutive failures for one account. Some limits are worth knowing: the failure counters are held in memory, so restarting the Hub clears them; the wait compares whole elapsed seconds with `timedelta.seconds`, which ignores elapsed days, so an uncleared counter can re-block a returning user for the wait period at each 24-hour multiple until a successful login or a restart clears it. Another limit is that the lockout throttles the login itself, not password guessing against a not-yet-approved account, because the login handler still returns a distinct authorization-pending message, rather than the generic error, when a pending account's password is correct. Where password guessing against a not-yet-approved account matters, rate-limit the login endpoint at the proxy or ingress, matching the endpoint's actual path: `/hub/login`, or the prefixed form such as `/jupyter/hub/login` when `JupyterHub.base_url` sets a prefix as in section 8. These password rules are applied whenever a password is set, at signup or through a password change, so an account keeps a previously accepted password until it is changed and existing passwords are not re-checked against a newly raised policy. See the [NativeAuthenticator configuration](https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py).

Control who may register, and treat NativeAuthenticator's own approval as separate from the Hub's admission. The signup form is enabled by default (`enable_signup` is `True`), and a self-registered account is created unauthorized and cannot log in until it is authorized:

```python
c.NativeAuthenticator.open_signup = False
```

Keep `open_signup` at its default `False`: with it off, a pending account waits for an administrator to approve it on the Hub's authorization panel (`/hub/authorize`; these `/hub/...` paths sit under `JupyterHub.base_url`, so a section 8 prefix makes them `/jupyter/hub/...`). Never set it to `True` on an internet-reachable Hub, where it would pre-authorize every self-registration, so anyone who reaches the signup form obtains a pre-authorized account (its login is still subject to the Hub's `check_allowed`). One case authorizes an account at signup even with `open_signup` off: NativeAuthenticator pre-authorizes any username already present in the section 5 `allowed_users` or `admin_users` (its `create_user` sets `pre_authorized = self.open_signup or username in self.get_authed_users()`, and `get_authed_users` includes `allowed_users` and `admin_users`). JupyterHub's own admission (`check_allowed`) independently lets a user log in only when `allow_all` is set or the username is in `allowed_users`. A listed username that has not yet registered can therefore, under the section 5 configuration in this guide (`allow_all = False` with a populated `allowed_users`), be claimed at the signup form, with a password of the claimant's choosing, by anyone who can reach it, arriving immediately authorized without the approval step ever running. Approval still gates an account that registered before its name was listed, since adding a name to `allowed_users` does not retroactively authorize an existing pending record, and an administrator can revoke an account's authorization. Treat the signup form as reachable only by trusted users, register the `allowed_users` accounts deliberately, and if self-service registration is not wanted at all set `enable_signup = False`, which makes the signup route reject every request. Passwords are stored as bcrypt hashes in the Hub database, so protect that database and its backups as a credential store.

Self-service signup lets users choose their own usernames, which GHSA-93gc-h923-mp36 concerns: "Insufficient validation of user and service names in URL components" (medium; affected `< 5.5.3` and `>=6.0.0,<6.1.0`, patched `5.5.3` and `6.1.0`). Its description says "In deployments where users can signup with arbitrary usernames (not most deployments), certain malicious usernames could interfere with URL handling." and gives the workaround "Set `Authenticator.username_regex` to a reasonable pattern." With signup enabled, run JupyterHub 6.1.0 or later, or 5.5.3 or later. Whether NativeAuthenticator 1.3.0 works with JupyterHub 6.1.1, or with 5.5.4, is not established here: no compatibility statement was found and nothing was run. [GHSA-93gc-h923-mp36](https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-93gc-h923-mp36).

## Sources (checked September 2026)

- Jupyter Server public server guide and password/TLS setup (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html
- Jupyter Server security and token/password authentication (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- Jupyter Server API base handler, protected API responses, and metrics enforcement (v2.21.1, checked November 2026): https://github.com/jupyter-server/jupyter_server/blob/v2.21.1/jupyter_server/base/handlers.py
- Jupyter Server configuration reference and authentication migrations (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/latest/other/full-config.html
- Migrating from the classic Notebook server (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/latest/operators/migrate-from-nbserver.html
- Jupyter Server API reference for authentication, origin, Host, root, and terminal controls (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html
- Jupyter Server authentication API (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.auth.html
- Jupyter Server release history, including endpoint authentication under 2.13.0 and 2.18.0 (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/stable/other/changelog.html
- Jupyter Server startup, dynamic defaults, and root refusal implementation (v2.21.1, checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py
- Jupyter Server default port constant (v2.21.1, checked November 2026): <https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/__init__.py>
- Jupyter Server identity provider and token-authenticated origin exception (v2.21.1, checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/auth/identity.py
- Jupyter Server Host, origin, XSRF, and default authentication implementation (v2.21.1, checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/base/handlers.py
- Jupyter Server kernel API implementation (v2.21.1, checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/handlers.py
- Jupyter Server REST API (rolling documentation, checked September 2026): https://jupyter-server.readthedocs.io/en/stable/developers/rest-api.html
- Notebook 7 configuration and Jupyter Server backend (rolling documentation, checked September 2026): https://jupyter-notebook.readthedocs.io/en/stable/configuring/config_overview.html
- JupyterLab kernel and terminal management: https://jupyterlab.readthedocs.io/en/stable/user/running.html
- JupyterHub 6.1.1 authenticator API and PAM admission settings, including auth_refresh_strict (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/reference/api/auth.html
- JupyterHub authenticators and Hub 5 admission changes (rolling documentation, checked September 2026): https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html
- JupyterHub 6.1.1 configuration reference (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html
- JupyterHub spawner API and user-configuration limitations (rolling documentation, checked September 2026): https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html
- JupyterHub 6.1.1 spawner resource-limit support (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/reference/spawners.html
- JupyterHub browser security, per-user domains, cookies, and server environments (rolling documentation, checked September 2026): https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html
- JupyterHub 6.1.1 HTTPS reverse-proxy example (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html
- Tornado XSRF cookies and request headers: https://www.tornadoweb.org/en/stable/guide/security.html
- curl TLS certificate and hostname verification: https://curl.se/docs/sslcerts.html
- curl options, stdin headers, cookie files, and diagnostic variables: https://curl.se/docs/manpage.html
- JupyterHub 6.1.1 proxy configuration and path prefix (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html
- configurable-http-proxy 5.3.0 command-line options: https://raw.githubusercontent.com/jupyterhub/configurable-http-proxy/5.3.0/bin/configurable-http-proxy
- NativeAuthenticator configuration traits and password, lockout, and signup enforcement: https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py
- NativeAuthenticator quickstart and authenticator_class: https://native-authenticator.readthedocs.io/en/1.3.0/quickstart.html
- NativeAuthenticator request handlers (signup 404 when signup is disabled, and the authorization panel): https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/handlers.py
- JupyterHub 6.1.1 configuration reference (trusted_downstream_ips, public_url, internal_ssl) (checked November 2026): https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html
- JupyterHub 6.1.1 changelog (internal hostname verification from 5.4, 6.0 and 6.1 changes, 6.1.0 security fixes and the 6.1.1 token-length fix) (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md
- Jupyter Server v2.21.1 application definition and HTTP-server construction (checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py
- JupyterHub 6.1.1 application (internal_ssl and forwarded-header trust) (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py
- JupyterHub 6.1.1 forwarded-scheme detection and internal TLS context (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/utils.py
- JupyterHub 6.1.1 internal HTTP client (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/httpclient.py
- JupyterHub 6.1.1 Hub cookie attributes and Host handling (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/handlers/base.py
- JupyterHub 6.1.1 single-user OAuth cookie (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/services/auth.py
- JupyterHub 6.1.1 LocalProcessSpawner privilege drop (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/spawner.py
- JupyterHub 6.1.1 proxy launch options, including Unix sockets (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/proxy.py
- JupyterHub 6.1.1 upgrade notes (Python, database, Unix sockets, PKCE, spawn options and internal HTTP client) (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md
- JupyterHub 5.5.4 authenticator API and PAM admission settings (checked November 2026): https://jupyterhub.readthedocs.io/en/5.5.4/reference/api/auth.html
- JupyterHub 5.5.4 configuration reference (checked November 2026): https://jupyterhub.readthedocs.io/en/5.5.4/reference/config-reference.html
- JupyterHub 5.5.4 spawner resource-limit support (checked November 2026): https://jupyterhub.readthedocs.io/en/5.5.4/reference/spawners.html
- JupyterHub 5.5.4 HTTPS reverse-proxy example, proxy configuration and path prefix (checked November 2026): https://jupyterhub.readthedocs.io/en/5.5.4/howto/configuration/config-proxy.html
- JupyterHub 5.5.4 changelog (internal hostname verification from 5.4, 5.5.3 security fixes and the 5.5.4 token-length fix) (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/docs/source/reference/changelog.md
- JupyterHub 5.5.4 application (internal_ssl, Tornado internal client and forwarded-header trust) (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/app.py
- JupyterHub 5.5.4 forwarded-scheme detection and internal TLS context (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/utils.py
- JupyterHub 5.5.4 Hub cookie attributes and Host handling (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/handlers/base.py
- JupyterHub 5.5.4 single-user OAuth cookie (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/services/auth.py
- JupyterHub 5.5.4 LocalProcessSpawner privilege drop (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/spawner.py
- JupyterHub 5.5.4 proxy launch options (checked November 2026): https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/proxy.py
- Jupyter Server v2.21.1 origin pattern check (checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/utils.py
- Jupyter Server v2.21.1 kernel transport encryption policy (checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/kernelmanager.py
- Jupyter Server v2.21.1 changelog (2.20.0 kernel transport encryption toggle) (checked November 2026): https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/CHANGELOG.md
- JupyterHub advisory GHSA-5jhc-4h3c-q97h, "Incomplete privilege drop in LocalProcessSpawner when setgroups() fails" (medium; affected `>=6.0.0, <6.1.0` and `<=5.5.2`, patched `6.1.0` and `5.5.3`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-5jhc-4h3c-q97h
- JupyterHub advisory GHSA-93gc-h923-mp36, "Insufficient validation of user and service names in URL components" (medium; affected `< 5.5.3` and `>=6.0.0,<6.1.0`, patched `5.5.3` and `6.1.0`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-93gc-h923-mp36
- JupyterHub advisory GHSA-hx46-2cv3-mh6g, "Denial of Service via invalid spawner options" (medium; affected `>=6.0.0, <6.1.0` and `<5.5.3`, patched `6.1.0` and `5.5.3`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-hx46-2cv3-mh6g
- JupyterHub advisory GHSA-pvm9-48cg-w76j, "token_expires_in_max_seconds not properly enforced" (medium; affected `>= 5.1.0, <5.5.3` and `>=6.0.0, <6.1.0`, patched `5.5.3` and `6.1.0`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-pvm9-48cg-w76j
- JupyterHub advisory GHSA-r764-xgvf-jrfj, "SharedPasswordAuthenticator: missing username normalization" (medium; affected `>=5.3.0,<5.5.3` and `>=6.0.0, <6.1.0`, patched `5.5.3` and `6.1.0`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-r764-xgvf-jrfj
- JupyterHub advisory GHSA-x7xh-7hc7-9436, "Missing validation on user rename admin API" (medium; affected `< 5.5.3` and `>=6.0.0, <6.1.0`, patched `5.5.3` and `6.1.0`) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-x7xh-7hc7-9436
- JupyterHub advisory GHSA-p43p-whwx-q52h (CVE-2026-54338), "JupyterHub has Unauthenticated Denial of Service via Unbounded Username Logging on Failed Login" (medium; affected `< 5.5.0`, patched `5.5.0`; no 6.x range listed) (checked November 2026): https://github.com/advisories/GHSA-p43p-whwx-q52h
- JupyterHub advisory GHSA-c4gm-pwx9-9w8j, "Reflected XSS in /hub/accept-share" (high; affected `>= 5.0.0,<5.5.1`, patched `5.5.1`; no 6.x range listed) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-c4gm-pwx9-9w8j
- JupyterHub advisory GHSA-69wv-m5fw-2fhp, "improper scope enforcement for limited admins of users and groups" (low; affected `>=2.0.0,<=5.5.0`, patched `5.5.1`; no 6.x range listed) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-69wv-m5fw-2fhp
- JupyterHub advisory GHSA-mj6q-mp44-53v8, "Share scopes do not follow user renames" (low; affected `>=5.0.0,<5.5.2`, patched `5.5.2`; no 6.x range listed) (checked November 2026): https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-mj6q-mp44-53v8
- Jupyter Server advisory GHSA-24qx-w28j-9m6p (CVE-2026-40110), "Jupyter Server has a  CORS Origin Validation Bypass via `re.match()` in `allow_origin_pat`" (high; affected `<= 2.17.0`, patched `2.18.0`) (checked November 2026): https://github.com/advisories/GHSA-24qx-w28j-9m6p
- Jupyter messaging protocol (jupyter_client 8.6.3): https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst
- Jupyter kernel connection defaults (jupyter_client 8.6.3): https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/jupyter_client/connect.py


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- server: Jupyter Server (v2.21.1)
- hub: JupyterHub (6.1.1)
- hub-5: JupyterHub (5.5.4)
- client: jupyter_client (8.6.3)
- lab: JupyterLab documentation (unknown)
- server-docs: Jupyter Server documentation (rolling) (unknown)
- notebook-docs: Notebook documentation (rolling) (unknown)
- hub-docs: JupyterHub documentation (rolling) (unknown)
- proxy: configurable-http-proxy (5.3.0)
- native: NativeAuthenticator (1.3.0)
- tornado: Tornado documentation (unknown)
- curl: curl documentation (unknown)
- advisories: JupyterHub and Jupyter Server security advisories (unknown)

Claims (full source mapping in the JSON block below):

- native-auth (REASONED; server-docs): Generated tokens enable authentication by default; a password replaces the generated token by default, and configured token/password alternatives are not MFA.
- password (REASONED; server-docs): Standalone Server password prompt stores a hash in jupyter_server_config.json; generate-config writes jupyter_server_config.py under the operating account.
- endpoint-auth (REASONED; server-docs, server): Set allow_unauthenticated_access=False for unclassified Jupyter handlers; explicitly public handlers and third-party authentication need separate review.
- endpoint-default (REASONED; server-docs): Reference lists allow_unauthenticated_access=True; feature appears under 2.13.0 and 2.18.0, with 2.18+ the guide baseline, not introduction date.
- metrics-auth (REASONED; server, server-docs): authenticate_prometheus=True independently requires authentication for metrics.
- migration (REASONED; server-docs, notebook-docs): Notebook 7 uses Server; migrate NotebookApp to ServerApp and Server 2 password/token traits to PasswordIdentityProvider and IdentityProvider; avoid credential argv.
- root (REASONED; server): allow_root=False refuses Unix root startup; use a dedicated unprivileged account for server and kernels; it neither changes UID nor sandboxes execution.
- terminals (REASONED; server-docs, server): terminals_enabled=False removes terminals but not kernel shell execution; reference False differs from the implementation's dynamic True subject to availability.
- native-tls (REASONED; server-docs, server): certfile/keyfile or --certfile/--keyfile enable native HTTPS; that listener no longer serves ordinary plaintext HTTP.
- private-bind (REASONED; server-docs): Retain loopback; do not expose 0.0.0.0 without authentication and HTTPS; disabling both password and token removes native authentication.
- proxy-tls (REASONED; hub, hub-5): An authenticated HTTPS proxy before a loopback server can replace native TLS; authentication alone does not encrypt transport.
- mfa (REASONED; server-docs, hub-docs): Standalone password is single-factor; fronting authentication or a Hub provider adds MFA only when explicitly enforced.
- origins (REASONED; server-docs): Same-origin settings keep allow_origin and allow_origin_pat empty and allow_credentials=False; cross-origin clients require reviewed exceptions.
- origin-cve (REASONED; server, advisories): Server 2.18.0 fixed GHSA-24qx-w28j-9m6p (CVE-2026-40110, high; affected up to 2.17.0); at v2.21.1 origin_matches_pat returns False for an empty pattern and otherwise requires re.fullmatch, so the empty allow_origin_pat matches no origin.
- xsrf (REASONED; server-docs, server): Keep disable_check_xsrf=False; disabling it removes browser-session request-forgery protection.
- host (REASONED; server-docs, server): allow_remote_access=False retains Host checks; local_hostnames permits actual standalone hostnames; Hub servers need their generated hostnames.
- token-exception (REASONED; server): Token-authenticated requests bypass origin and XSRF checks; test browser protections with a cookie session and no token.
- hub-admission (REASONED; hub, hub-5, hub-docs): Hub 6.1.0+ or 5.5.3+ PAM example disables allow_all and allow_existing_users, lists allowed_users and empties allowed_groups; the 6.1.1 and 5.5.4 authenticator API pages match; other authenticators need separate review.
- hub-floor (REASONED; hub, hub-5, advisories): Run Hub 6.1.0+ or 5.5.3+: GHSA-5jhc-4h3c-q97h lists up to 5.5.2 and 6.0.0 to before 6.1.0 as affected, and 5 more advisories share those patched releases; 6.1.1 and 5.5.4 fix a token-length regression, no advisory; that 6.x carries the 5.5.0 to 5.5.2 fixes is not established.
- hub-accounts (REASONED; server-docs, hub-docs, hub, hub-5): LocalProcessSpawner needs matching Unix accounts; use separate users/servers, and avoid SimpleLocalProcessSpawner, which provides no user isolation.
- hub-privilege-drop (REASONED; advisories, hub, hub-5): GHSA-5jhc-4h3c-q97h (medium; patched 6.1.0 and 5.5.3): a failed setgroups could leave Hub groups; the 6.1.1 and 5.5.4 LocalProcessSpawner then attempts to clear supplemental groups and, after setuid, raises PermissionError if extra groups remain.
- hub-limits (REASONED; hub-docs, hub, hub-5): Local processes are not containers; LocalProcessSpawner does not enforce generic CPU/memory limits, and PAM does not automatically provide MFA.
- hub-6-upgrade (REASONED; hub, hub-5): Hub 6 needs Python 3.10 and jupyterhub upgrade-db; 6.1 adds auth_refresh_strict (default False, True before 6.1); oauth_require_pkce (default False) is marked 6.0, config-tagged in 6.1.0; 5.5.4 has neither; unprefixed GET spawn options mostly work, except display_name, opt-a (pass opt-opt-a), mixing with opt- and future Hub parameters; POST spawn options move to a user_options key.
- hub-domains (REASONED; hub-docs, hub): For mutually untrusted Hub users, subdomain_host separates browser origins; provide HTTPS/DNS for every user domain on a separate application domain.
- hub-cookies (REASONED; hub, hub-5, hub-docs): cookie_host_prefix_enabled requires Hub 4.1+, HTTPS and per-user domains; the combined example targets Hub 6.1.0+ or 5.5.3+, and the 6.1.1 and 5.5.4 references document the setting.
- hub-user-config (REASONED; hub-docs): disable_user_config ignores home configuration; administrator-controlled server executables, environments and launch paths prevent replacement; kernel environments may remain writable.
- server-prefix (REASONED; server): Server base_url defaults to /; configure /jupyter/ consistently with the proxy so registered routes remain within the intended boundary.
- hub-prefix (REASONED; hub, proxy, hub-5): Hub prefix defaults to /; bind_url=http://127.0.0.1:8000/jupyter/ sets both listener and base_url at 6.1.1 and 5.5.4; conflicting URL settings or proxy prefix flags are not an auth boundary.
- hub-unix-sockets (REASONED; hub, hub-5, proxy): At 6.1.1 bind_url accepts http+unix:// and the Hub passes --socket/--api-socket to configurable-http-proxy; 5.5.4 passes only --ip/--port and --api-ip/--api-port; the loopback bind_url uses neither; configurable-http-proxy 5.3.0 compatibility with 6.1.1 is not established.
- server-headers (REASONED; server): Server trust_xheaders defaults False; enable only behind a private, sanitizing ingress owning forwarded address and scheme headers.
- hub-headers (REASONED; hub, hub-5): Hub enables forwarded-header trust at 6.1.1 and 5.5.4; hub_ip and trusted_downstream_ips constrain address selection, not which peers may send headers; empty trusted hops do not disable trust.
- forwarded-scheme (REASONED; hub, hub-5): Ingress must normalize Forwarded and both X- address/scheme forms and reject unintended Host values; at 6.1.1 and 5.5.4 get_browser_protocol reads Forwarded first; public_url and host-prefixed cookies guard specified scheme paths.
- forwarded-host (REASONED; hub, hub-5): Forwarded-header handling rewrites address/scheme, not Host; in the 6.1.1 and 5.5.4 files read, forwarded_host_header appears only as its trait definition; whether another file consumes X-Forwarded-Host is not established, so test it.
- internal-tls (REASONED; hub, hub-5): internal_ssl defaults False; enable it with protected persistent internal_certs_location for mutual TLS on Hub/proxy/single-user and spawn-readiness connections.
- internal-certs (REASONED; hub-docs, hub): Spawners must deliver certificates and trust bundles; LocalProcessSpawner relocates them, remote spawners need move_certs, and ssl_alt_names must match connection names.
- internal-hostnames (REASONED; hub, hub-5): Internal hostname verification defaults on from Hub 5.4; at 6.1.1 the aiohttp client context sets CERT_REQUIRED and check_hostname=True; 5.5.4 sets Tornado validate_cert=True, its hostname check inferred; spawn-readiness and proxy-side checks are not established at 6.1.1 or 5.5.4.
- kernel-transport (REASONED; client, server): Hub internal_ssl excludes server-to-kernel ZeroMQ; HMAC authenticates without encryption; Server 2.20+ transport_encryption defaults to disabled and needs jupyter_client support not established for 8.6.3; local kernels bind loopback; remote kernels need separate encrypted transport.
- native-store (REASONED; hub-docs, native): NativeAuthenticator replaces PAM credentials with bcrypt hashes in the Hub database, not the spawner's Unix account requirement; protect database/backups.
- native-length (REASONED; native): minimum_password_length effectively defaults 0 despite tag(default=1); set 12; zero admits empty passwords.
- native-common (REASONED; native): check_common_password defaults False; True checks the bundled 10,000-entry list, not a breach corpus.
- native-lockout (REASONED; native): allowed_failed_logins defaults 0, disabling lockout; set 5 consecutive failures per account.
- native-cooldown (REASONED; native): seconds_before_next_try effectively defaults 0 despite the 600 annotation/help; set 1200 and distinguish by a correct password about two seconds after failure.
- native-counters (REASONED; native): Failure counters are in memory and reset on restart; timedelta.seconds ignores days and can re-block at 24-hour multiples until success or restart.
- native-oracle (REASONED; native): Pending accounts still disclose a distinct correct-password authorization-pending message during lockout; rate-limit the actual prefixed /hub/login route.
- native-policy-scope (REASONED; native): Password strength applies at signup/password change; raising policy does not recheck existing passwords.
- native-approval (REASONED; native): open_signup defaults False; new pending users need /hub/authorize approval; True pre-authorizes signup, still subject to Hub admission.
- native-preauthorization (REASONED; native): allowed_users/admin_users names are pre-authorized at first signup even with open_signup=False; deliberate registration is required; later allowlisting does not approve an existing pending record.
- native-signup (REASONED; native): enable_signup defaults True; False refuses signup GET/POST with 404; restrict signup to trusted users.
- native-usernames (REASONED; advisories, native): Self-service signup bears on GHSA-93gc-h923-mp36 (medium; patched 5.5.3 and 6.1.0), whose workaround is Authenticator.username_regex; whether NativeAuthenticator 1.3.0 works with Hub 6.1.1 or 5.5.4 is not established.
- verify-tls (REASONED; curl): Validated HTTPS must complete with exit=0; transport failures alone prove nothing; use real hostname and CA, retaining certificate validation.
- verify-api (REASONED; server-docs, server): Anonymous /api/kernels returns native 403 with auth, authenticated kernel JSON returns 200; fronting login may redirect, and password-only deployments need a browser positive control.
- verify-host (REASONED; server): Wrong-Host token request is refused with native 403 while normal Host succeeds; a fronting rejection alone does not demonstrate Server Host checks.
- verify-metrics (REASONED; server): Compare anonymous metrics with authenticate_prometheus off/on and authenticated metrics content; absent routes or generic errors are inconclusive.
- verify-extension (REASONED; server-docs, server): Compare an actual unclassified extension route with allow_unauthenticated_access True/False and its authenticated content; protected kernel routes do not substitute.
- verify-xsrf (REASONED; server, tornado): Cookie-session same-origin POST without XSRF creates a kernel when checks are disabled; fixed missing header gives 403, matching header gives 201 with successful cookie GET.
- verify-origin (REASONED; server-docs, server): Wrong-Origin cookie GET returns kernel JSON with allow_origin=*; fixed APIHandler rejects with 404 while same-origin returns 200; also inspect browser CORS headers.
- verify-cleanup (REASONED; lab): Record and shut down every disposable kernel created in either state through the authenticated UI.
- verify-root (REASONED; server): Compare allowed versus refused root startup and inspect server/kernel ownership; fixed unprivileged execution must retain its intended nonzero UID.
- verify-terminals (REASONED; server-docs, server): Compare authenticated /api/terminals enabled/disabled, retaining a working /api/kernels positive control and kernel shell execution.
- verify-hub-admission (REASONED; hub, hub-5, hub-docs): Compare valid extra and historical users against the allowlist, with allowed-user login and spawn as positive controls.
- verify-hub-accounts (REASONED; hub-docs): Two users' server/kernel UIDs must differ as intended, compared with a shared-account fixture.
- verify-hub-origins (REASONED; hub, hub-5, hub-docs): Compare shared versus distinct user origins and inspect __Host- cookies for Secure, path / and no Domain attribute.
- verify-hub-config (REASONED; hub-docs): Compare a user terminal override loading versus being ignored, deny server-environment writes, and retain a working notebook.
- verify-listeners (REASONED; server): ss inventories local binds, not firewall/NAT; confirm actual private listener and external entry point with a working positive control; failed netlink inventory proves no absence.
- port-default (REASONED; server): Standalone port starts at 8888 but configuration and retries can change it; inventory the actual listener.
- verify-prefix (REASONED; hub, server): Probe prefixed and unprefixed Server/Hub routes; require no application alias outside the boundary and working authenticated prefixed access and kernel WebSocket.
- verify-headers (REASONED; hub, server, hub-5): Compare spoofed address/scheme/Forwarded headers through real ingress and direct backend access; inspect logs, redirects and cookies with login/WebSocket controls, and the OAuth state cookie's Set-Cookie, whose Secure comes from JUPYTERHUB_PUBLIC_URL, the scheme or, failing both, cookie_options; test a spoofed X-Forwarded-Host and real Host separately.
- verify-internal-tls (REASONED; hub, hub-5, client): Compare each internal connection with TLS off/on; trusted client certificates succeed, untrusted certificates and wrong hostnames are expected to fail on Hub 5.4+; also try a system-trusted non-internal CA; keep kernel ZeroMQ excluded.
- verify-native (REASONED; native): Test length/common-password, threshold/cooldown and pending-account oracle independently; compare approval with allow_all and empty allowed_users, first-signup preauthorization, disabled signup and stored bcrypt.

````json
{
  "schema": 1,
  "checked": "2026-11-04",
  "documentation_checked": "2026-09",
  "body_sha256": "6bfe7760f795b67377c61622fe559d503b9036d3766f4f40c83be6f59b3dfff8",
  "components": {
    "server": {
      "name": "Jupyter Server",
      "basis": "v2.21.1",
      "sources": {
        "sbb1ed2d8d382": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/serverapp.py",
        "sb273e7f052ec": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/__init__.py",
        "s8bbaa48f00fd": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/auth/identity.py",
        "s70c18acec73c": "https://github.com/jupyter-server/jupyter_server/blob/v2.21.1/jupyter_server/base/handlers.py",
        "sf3aa08d40bb0": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/base/handlers.py",
        "s52319d21e10e": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/handlers.py",
        "s3d4d1ac80620": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/services/kernels/kernelmanager.py",
        "sb03775f88157": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/jupyter_server/utils.py",
        "sa4b4df42d17e": "https://raw.githubusercontent.com/jupyter-server/jupyter_server/v2.21.1/CHANGELOG.md"
      }
    },
    "hub": {
      "name": "JupyterHub",
      "basis": "6.1.1",
      "sources": {
        "s6496de8a4a2b": "https://jupyterhub.readthedocs.io/en/6.1.1/howto/configuration/config-proxy.html",
        "scea924dc126d": "https://jupyterhub.readthedocs.io/en/6.1.1/reference/config-reference.html",
        "s5223de1d1c52": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/reference/changelog.md",
        "sa4d711f216d2": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/app.py",
        "s8c0735472b37": "https://jupyterhub.readthedocs.io/en/6.1.1/reference/api/auth.html",
        "s9a4c8810efd9": "https://jupyterhub.readthedocs.io/en/6.1.1/reference/spawners.html",
        "s3702ddd25f90": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/utils.py",
        "s4c7ed88a196a": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/httpclient.py",
        "s11e2575c9dce": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/handlers/base.py",
        "s14ad5e388797": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/services/auth.py",
        "s154792fff6d8": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/spawner.py",
        "s84c17235a8e9": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/jupyterhub/proxy.py",
        "sd7c0a6706c5e": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/6.1.1/docs/source/howto/upgrading-v6.md"
      }
    },
    "hub-5": {
      "name": "JupyterHub",
      "basis": "5.5.4",
      "sources": {
        "s990f07ad02f9": "https://jupyterhub.readthedocs.io/en/5.5.4/howto/configuration/config-proxy.html",
        "sf345a9b5625c": "https://jupyterhub.readthedocs.io/en/5.5.4/reference/config-reference.html",
        "s5ed3cb4eb46f": "https://jupyterhub.readthedocs.io/en/5.5.4/reference/api/auth.html",
        "sa8550f5341c5": "https://jupyterhub.readthedocs.io/en/5.5.4/reference/spawners.html",
        "s3321140c549e": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/docs/source/reference/changelog.md",
        "s5ceda59ed3ff": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/app.py",
        "s440606cd14bb": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/utils.py",
        "s0504cd8b3582": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/handlers/base.py",
        "s956c06acb323": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/services/auth.py",
        "s30f15c6f9d58": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/spawner.py",
        "sa88c0e40076d": "https://raw.githubusercontent.com/jupyterhub/jupyterhub/5.5.4/jupyterhub/proxy.py"
      }
    },
    "client": {
      "name": "jupyter_client",
      "basis": "8.6.3",
      "sources": {
        "s254bb75e8fcd": "https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/docs/messaging.rst",
        "s4a4cbff2fc52": "https://raw.githubusercontent.com/jupyter/jupyter_client/v8.6.3/jupyter_client/connect.py"
      }
    },
    "lab": {
      "name": "JupyterLab documentation",
      "basis": "unknown",
      "sources": {
        "s8021535e4b8f": "https://jupyterlab.readthedocs.io/en/stable/user/running.html"
      }
    },
    "server-docs": {
      "name": "Jupyter Server documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s7e2219e89598": "https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html",
        "sc703a8030c8f": "https://jupyter-server.readthedocs.io/en/latest/operators/security.html",
        "se96d81c5de5a": "https://jupyter-server.readthedocs.io/en/latest/other/full-config.html",
        "s030744ca2941": "https://jupyter-server.readthedocs.io/en/latest/operators/migrate-from-nbserver.html",
        "s3036d65c135e": "https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.html",
        "s0d0d3fa341e9": "https://jupyter-server.readthedocs.io/en/stable/api/jupyter_server.auth.html",
        "s2e77936fa221": "https://jupyter-server.readthedocs.io/en/stable/developers/rest-api.html",
        "s3f8d489dcf1a": "https://jupyter-server.readthedocs.io/en/stable/other/changelog.html"
      }
    },
    "notebook-docs": {
      "name": "Notebook documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s0650d57213a3": "https://jupyter-notebook.readthedocs.io/en/stable/configuring/config_overview.html"
      }
    },
    "hub-docs": {
      "name": "JupyterHub documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s1a8d05a8cf13": "https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html",
        "s06a88ed8ee36": "https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html",
        "sad07061feaf6": "https://jupyterhub.readthedocs.io/en/stable/reference/api/spawner.html"
      }
    },
    "proxy": {
      "name": "configurable-http-proxy",
      "basis": "5.3.0",
      "sources": {
        "sd16e1a3c1c99": "https://raw.githubusercontent.com/jupyterhub/configurable-http-proxy/5.3.0/bin/configurable-http-proxy"
      }
    },
    "native": {
      "name": "NativeAuthenticator",
      "basis": "1.3.0",
      "sources": {
        "s7e8115fc47c7": "https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/nativeauthenticator.py",
        "s1cc87f8d9e78": "https://native-authenticator.readthedocs.io/en/1.3.0/quickstart.html",
        "s0bd461b12e33": "https://raw.githubusercontent.com/jupyterhub/nativeauthenticator/1.3.0/nativeauthenticator/handlers.py"
      }
    },
    "tornado": {
      "name": "Tornado documentation",
      "basis": "unknown",
      "sources": {
        "s0f3c220a61fa": "https://www.tornadoweb.org/en/stable/guide/security.html"
      }
    },
    "curl": {
      "name": "curl documentation",
      "basis": "unknown",
      "sources": {
        "s0dc5c76f65b4": "https://curl.se/docs/sslcerts.html",
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "advisories": {
      "name": "JupyterHub and Jupyter Server security advisories",
      "basis": "unknown",
      "sources": {
        "s158f4f874e25": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-5jhc-4h3c-q97h",
        "s6b64492f0407": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-93gc-h923-mp36",
        "se4b58a1cb487": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-hx46-2cv3-mh6g",
        "s47f46c11fe5a": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-pvm9-48cg-w76j",
        "scbb5f6fa0fbf": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-r764-xgvf-jrfj",
        "s108c721e1a63": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-x7xh-7hc7-9436",
        "sb2ca96572698": "https://github.com/advisories/GHSA-p43p-whwx-q52h",
        "scea3747ff64d": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-c4gm-pwx9-9w8j",
        "s2f69570e8f35": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-69wv-m5fw-2fhp",
        "s7cf89b38a85e": "https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-mj6q-mp44-53v8",
        "s6bc6c920eb04": "https://github.com/advisories/GHSA-24qx-w28j-9m6p"
      }
    }
  },
  "claims": {
    "native-auth": {"text": "Generated tokens enable authentication by default; a password replaces the generated token by default, and configured token/password alternatives are not MFA.", "components": ["server-docs"], "sources": ["server-docs:sc703a8030c8f"], "status": "REASONED"},
    "password": {"text": "Standalone Server password prompt stores a hash in jupyter_server_config.json; generate-config writes jupyter_server_config.py under the operating account.", "components": ["server-docs"], "sources": ["server-docs:s7e2219e89598", "server-docs:se96d81c5de5a"], "status": "REASONED"},
    "endpoint-auth": {"text": "Set allow_unauthenticated_access=False for unclassified Jupyter handlers; explicitly public handlers and third-party authentication need separate review.", "components": ["server-docs", "server"], "sources": ["server-docs:s3036d65c135e", "server:sf3aa08d40bb0"], "status": "REASONED"},
    "endpoint-default": {"text": "Reference lists allow_unauthenticated_access=True; feature appears under 2.13.0 and 2.18.0, with 2.18+ the guide baseline, not introduction date.", "components": ["server-docs"], "sources": ["server-docs:se96d81c5de5a", "server-docs:s3f8d489dcf1a"], "status": "REASONED"},
    "metrics-auth": {"text": "authenticate_prometheus=True independently requires authentication for metrics.", "components": ["server", "server-docs"], "sources": ["server:s70c18acec73c", "server-docs:s3036d65c135e"], "status": "REASONED"},
    "migration": {"text": "Notebook 7 uses Server; migrate NotebookApp to ServerApp and Server 2 password/token traits to PasswordIdentityProvider and IdentityProvider; avoid credential argv.", "components": ["server-docs", "notebook-docs"], "sources": ["server-docs:s030744ca2941", "server-docs:s0d0d3fa341e9", "notebook-docs:s0650d57213a3"], "status": "REASONED"},
    "root": {"text": "allow_root=False refuses Unix root startup; use a dedicated unprivileged account for server and kernels; it neither changes UID nor sandboxes execution.", "components": ["server"], "sources": ["server:sbb1ed2d8d382"], "status": "REASONED"},
    "terminals": {"text": "terminals_enabled=False removes terminals but not kernel shell execution; reference False differs from the implementation's dynamic True subject to availability.", "components": ["server-docs", "server"], "sources": ["server-docs:se96d81c5de5a", "server:sbb1ed2d8d382"], "status": "REASONED"},
    "native-tls": {"text": "certfile/keyfile or --certfile/--keyfile enable native HTTPS; that listener no longer serves ordinary plaintext HTTP.", "components": ["server-docs", "server"], "sources": ["server-docs:s7e2219e89598", "server:sbb1ed2d8d382"], "status": "REASONED"},
    "private-bind": {"text": "Retain loopback; do not expose 0.0.0.0 without authentication and HTTPS; disabling both password and token removes native authentication.", "components": ["server-docs"], "sources": ["server-docs:s7e2219e89598", "server-docs:sc703a8030c8f", "server-docs:se96d81c5de5a"], "status": "REASONED"},
    "proxy-tls": {"text": "An authenticated HTTPS proxy before a loopback server can replace native TLS; authentication alone does not encrypt transport.", "components": ["hub", "hub-5"], "sources": ["hub:s6496de8a4a2b", "hub-5:s990f07ad02f9"], "status": "REASONED"},
    "mfa": {"text": "Standalone password is single-factor; fronting authentication or a Hub provider adds MFA only when explicitly enforced.", "components": ["server-docs", "hub-docs"], "sources": ["server-docs:sc703a8030c8f", "hub-docs:s1a8d05a8cf13"], "status": "REASONED"},
    "origins": {"text": "Same-origin settings keep allow_origin and allow_origin_pat empty and allow_credentials=False; cross-origin clients require reviewed exceptions.", "components": ["server-docs"], "sources": ["server-docs:s3036d65c135e"], "status": "REASONED"},
    "origin-cve": {"text": "Server 2.18.0 fixed GHSA-24qx-w28j-9m6p (CVE-2026-40110, high; affected up to 2.17.0); at v2.21.1 origin_matches_pat returns False for an empty pattern and otherwise requires re.fullmatch, so the empty allow_origin_pat matches no origin.", "components": ["server", "advisories"], "sources": ["server:sb03775f88157", "advisories:s6bc6c920eb04"], "status": "REASONED"},
    "xsrf": {"text": "Keep disable_check_xsrf=False; disabling it removes browser-session request-forgery protection.", "components": ["server-docs", "server"], "sources": ["server-docs:s3036d65c135e", "server:sf3aa08d40bb0"], "status": "REASONED"},
    "host": {"text": "allow_remote_access=False retains Host checks; local_hostnames permits actual standalone hostnames; Hub servers need their generated hostnames.", "components": ["server-docs", "server"], "sources": ["server-docs:se96d81c5de5a", "server:sf3aa08d40bb0"], "status": "REASONED"},
    "token-exception": {"text": "Token-authenticated requests bypass origin and XSRF checks; test browser protections with a cookie session and no token.", "components": ["server"], "sources": ["server:s8bbaa48f00fd", "server:sf3aa08d40bb0"], "status": "REASONED"},
    "hub-admission": {"text": "Hub 6.1.0+ or 5.5.3+ PAM example disables allow_all and allow_existing_users, lists allowed_users and empties allowed_groups; the 6.1.1 and 5.5.4 authenticator API pages match; other authenticators need separate review.", "components": ["hub", "hub-5", "hub-docs"], "sources": ["hub:s8c0735472b37", "hub-5:s5ed3cb4eb46f", "hub-docs:s1a8d05a8cf13"], "status": "REASONED"},
    "hub-floor": {"text": "Run Hub 6.1.0+ or 5.5.3+: GHSA-5jhc-4h3c-q97h lists up to 5.5.2 and 6.0.0 to before 6.1.0 as affected, and 5 more advisories share those patched releases; 6.1.1 and 5.5.4 fix a token-length regression, no advisory; that 6.x carries the 5.5.0 to 5.5.2 fixes is not established.", "components": ["hub", "hub-5", "advisories"], "sources": ["hub:s5223de1d1c52", "hub-5:s3321140c549e", "advisories:s158f4f874e25", "advisories:s6b64492f0407", "advisories:se4b58a1cb487", "advisories:s47f46c11fe5a", "advisories:scbb5f6fa0fbf", "advisories:s108c721e1a63", "advisories:sb2ca96572698", "advisories:scea3747ff64d", "advisories:s2f69570e8f35", "advisories:s7cf89b38a85e"], "status": "REASONED"},
    "hub-accounts": {"text": "LocalProcessSpawner needs matching Unix accounts; use separate users/servers, and avoid SimpleLocalProcessSpawner, which provides no user isolation.", "components": ["server-docs", "hub-docs", "hub", "hub-5"], "sources": ["server-docs:s7e2219e89598", "hub-docs:sad07061feaf6", "hub:scea924dc126d", "hub-5:sf345a9b5625c"], "status": "REASONED"},
    "hub-privilege-drop": {"text": "GHSA-5jhc-4h3c-q97h (medium; patched 6.1.0 and 5.5.3): a failed setgroups could leave Hub groups; the 6.1.1 and 5.5.4 LocalProcessSpawner then attempts to clear supplemental groups and, after setuid, raises PermissionError if extra groups remain.", "components": ["advisories", "hub", "hub-5"], "sources": ["advisories:s158f4f874e25", "hub:s154792fff6d8", "hub-5:s30f15c6f9d58"], "status": "REASONED"},
    "hub-limits": {"text": "Local processes are not containers; LocalProcessSpawner does not enforce generic CPU/memory limits, and PAM does not automatically provide MFA.", "components": ["hub-docs", "hub", "hub-5"], "sources": ["hub-docs:s1a8d05a8cf13", "hub:s9a4c8810efd9", "hub-5:sa8550f5341c5"], "status": "REASONED"},
    "hub-6-upgrade": {"text": "Hub 6 needs Python 3.10 and jupyterhub upgrade-db; 6.1 adds auth_refresh_strict (default False, True before 6.1); oauth_require_pkce (default False) is marked 6.0, config-tagged in 6.1.0; 5.5.4 has neither; unprefixed GET spawn options mostly work, except display_name, opt-a (pass opt-opt-a), mixing with opt- and future Hub parameters; POST spawn options move to a user_options key.", "components": ["hub", "hub-5"], "sources": ["hub:sd7c0a6706c5e", "hub:s8c0735472b37", "hub:sa4d711f216d2", "hub:s5223de1d1c52", "hub-5:s5ed3cb4eb46f", "hub-5:s5ceda59ed3ff"], "status": "REASONED"},
    "hub-domains": {"text": "For mutually untrusted Hub users, subdomain_host separates browser origins; provide HTTPS/DNS for every user domain on a separate application domain.", "components": ["hub-docs", "hub"], "sources": ["hub-docs:s06a88ed8ee36", "hub:scea924dc126d"], "status": "REASONED"},
    "hub-cookies": {"text": "cookie_host_prefix_enabled requires Hub 4.1+, HTTPS and per-user domains; the combined example targets Hub 6.1.0+ or 5.5.3+, and the 6.1.1 and 5.5.4 references document the setting.", "components": ["hub", "hub-5", "hub-docs"], "sources": ["hub:scea924dc126d", "hub-5:sf345a9b5625c", "hub-docs:s06a88ed8ee36"], "status": "REASONED"},
    "hub-user-config": {"text": "disable_user_config ignores home configuration; administrator-controlled server executables, environments and launch paths prevent replacement; kernel environments may remain writable.", "components": ["hub-docs"], "sources": ["hub-docs:sad07061feaf6", "hub-docs:s06a88ed8ee36"], "status": "REASONED"},
    "server-prefix": {"text": "Server base_url defaults to /; configure /jupyter/ consistently with the proxy so registered routes remain within the intended boundary.", "components": ["server"], "sources": ["server:sbb1ed2d8d382"], "status": "REASONED"},
    "hub-prefix": {"text": "Hub prefix defaults to /; bind_url=http://127.0.0.1:8000/jupyter/ sets both listener and base_url at 6.1.1 and 5.5.4; conflicting URL settings or proxy prefix flags are not an auth boundary.", "components": ["hub", "proxy", "hub-5"], "sources": ["hub:s6496de8a4a2b", "proxy:sd16e1a3c1c99", "hub:scea924dc126d", "hub:sa4d711f216d2", "hub-5:s990f07ad02f9", "hub-5:s5ceda59ed3ff"], "status": "REASONED"},
    "hub-unix-sockets": {"text": "At 6.1.1 bind_url accepts http+unix:// and the Hub passes --socket/--api-socket to configurable-http-proxy; 5.5.4 passes only --ip/--port and --api-ip/--api-port; the loopback bind_url uses neither; configurable-http-proxy 5.3.0 compatibility with 6.1.1 is not established.", "components": ["hub", "hub-5", "proxy"], "sources": ["hub:s84c17235a8e9", "hub:sa4d711f216d2", "hub:sd7c0a6706c5e", "hub:s5223de1d1c52", "hub-5:sa88c0e40076d", "proxy:sd16e1a3c1c99"], "status": "REASONED"},
    "server-headers": {"text": "Server trust_xheaders defaults False; enable only behind a private, sanitizing ingress owning forwarded address and scheme headers.", "components": ["server"], "sources": ["server:sbb1ed2d8d382"], "status": "REASONED"},
    "hub-headers": {"text": "Hub enables forwarded-header trust at 6.1.1 and 5.5.4; hub_ip and trusted_downstream_ips constrain address selection, not which peers may send headers; empty trusted hops do not disable trust.", "components": ["hub", "hub-5"], "sources": ["hub:scea924dc126d", "hub:sa4d711f216d2", "hub-5:sf345a9b5625c", "hub-5:s5ceda59ed3ff"], "status": "REASONED"},
    "forwarded-scheme": {"text": "Ingress must normalize Forwarded and both X- address/scheme forms and reject unintended Host values; at 6.1.1 and 5.5.4 get_browser_protocol reads Forwarded first; public_url and host-prefixed cookies guard specified scheme paths.", "components": ["hub", "hub-5"], "sources": ["hub:scea924dc126d", "hub:s3702ddd25f90", "hub-5:s440606cd14bb", "hub-5:sf345a9b5625c"], "status": "REASONED"},
    "forwarded-host": {"text": "Forwarded-header handling rewrites address/scheme, not Host; in the 6.1.1 and 5.5.4 files read, forwarded_host_header appears only as its trait definition; whether another file consumes X-Forwarded-Host is not established, so test it.", "components": ["hub", "hub-5"], "sources": ["hub:scea924dc126d", "hub:sa4d711f216d2", "hub:s11e2575c9dce", "hub-5:s5ceda59ed3ff", "hub-5:s0504cd8b3582"], "status": "REASONED"},
    "internal-tls": {"text": "internal_ssl defaults False; enable it with protected persistent internal_certs_location for mutual TLS on Hub/proxy/single-user and spawn-readiness connections.", "components": ["hub", "hub-5"], "sources": ["hub:scea924dc126d", "hub:sa4d711f216d2", "hub-5:sf345a9b5625c", "hub-5:s5ceda59ed3ff"], "status": "REASONED"},
    "internal-certs": {"text": "Spawners must deliver certificates and trust bundles; LocalProcessSpawner relocates them, remote spawners need move_certs, and ssl_alt_names must match connection names.", "components": ["hub-docs", "hub"], "sources": ["hub-docs:sad07061feaf6", "hub:scea924dc126d"], "status": "REASONED"},
    "internal-hostnames": {"text": "Internal hostname verification defaults on from Hub 5.4; at 6.1.1 the aiohttp client context sets CERT_REQUIRED and check_hostname=True; 5.5.4 sets Tornado validate_cert=True, its hostname check inferred; spawn-readiness and proxy-side checks are not established at 6.1.1 or 5.5.4.", "components": ["hub", "hub-5"], "sources": ["hub:s5223de1d1c52", "hub:sa4d711f216d2", "hub:s3702ddd25f90", "hub:s4c7ed88a196a", "hub:sd7c0a6706c5e", "hub-5:s3321140c549e", "hub-5:s5ceda59ed3ff", "hub-5:s440606cd14bb"], "status": "REASONED"},
    "kernel-transport": {"text": "Hub internal_ssl excludes server-to-kernel ZeroMQ; HMAC authenticates without encryption; Server 2.20+ transport_encryption defaults to disabled and needs jupyter_client support not established for 8.6.3; local kernels bind loopback; remote kernels need separate encrypted transport.", "components": ["client", "server"], "sources": ["client:s254bb75e8fcd", "client:s4a4cbff2fc52", "server:s3d4d1ac80620", "server:sa4b4df42d17e"], "status": "REASONED"},
    "native-store": {"text": "NativeAuthenticator replaces PAM credentials with bcrypt hashes in the Hub database, not the spawner's Unix account requirement; protect database/backups.", "components": ["hub-docs", "native"], "sources": ["hub-docs:sad07061feaf6", "native:s7e8115fc47c7", "native:s1cc87f8d9e78"], "status": "REASONED"},
    "native-length": {"text": "minimum_password_length effectively defaults 0 despite tag(default=1); set 12; zero admits empty passwords.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-common": {"text": "check_common_password defaults False; True checks the bundled 10,000-entry list, not a breach corpus.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-lockout": {"text": "allowed_failed_logins defaults 0, disabling lockout; set 5 consecutive failures per account.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-cooldown": {"text": "seconds_before_next_try effectively defaults 0 despite the 600 annotation/help; set 1200 and distinguish by a correct password about two seconds after failure.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-counters": {"text": "Failure counters are in memory and reset on restart; timedelta.seconds ignores days and can re-block at 24-hour multiples until success or restart.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-oracle": {"text": "Pending accounts still disclose a distinct correct-password authorization-pending message during lockout; rate-limit the actual prefixed /hub/login route.", "components": ["native"], "sources": ["native:s7e8115fc47c7", "native:s0bd461b12e33"], "status": "REASONED"},
    "native-policy-scope": {"text": "Password strength applies at signup/password change; raising policy does not recheck existing passwords.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-approval": {"text": "open_signup defaults False; new pending users need /hub/authorize approval; True pre-authorizes signup, still subject to Hub admission.", "components": ["native"], "sources": ["native:s7e8115fc47c7", "native:s0bd461b12e33"], "status": "REASONED"},
    "native-preauthorization": {"text": "allowed_users/admin_users names are pre-authorized at first signup even with open_signup=False; deliberate registration is required; later allowlisting does not approve an existing pending record.", "components": ["native"], "sources": ["native:s7e8115fc47c7"], "status": "REASONED"},
    "native-signup": {"text": "enable_signup defaults True; False refuses signup GET/POST with 404; restrict signup to trusted users.", "components": ["native"], "sources": ["native:s7e8115fc47c7", "native:s0bd461b12e33"], "status": "REASONED"},
    "native-usernames": {"text": "Self-service signup bears on GHSA-93gc-h923-mp36 (medium; patched 5.5.3 and 6.1.0), whose workaround is Authenticator.username_regex; whether NativeAuthenticator 1.3.0 works with Hub 6.1.1 or 5.5.4 is not established.", "components": ["advisories", "native"], "sources": ["advisories:s6b64492f0407", "native:s7e8115fc47c7"], "status": "REASONED"},
    "verify-tls": {"text": "Validated HTTPS must complete with exit=0; transport failures alone prove nothing; use real hostname and CA, retaining certificate validation.", "components": ["curl"], "sources": ["curl:s0dc5c76f65b4", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-api": {"text": "Anonymous /api/kernels returns native 403 with auth, authenticated kernel JSON returns 200; fronting login may redirect, and password-only deployments need a browser positive control.", "components": ["server-docs", "server"], "sources": ["server-docs:sc703a8030c8f", "server:sf3aa08d40bb0", "server-docs:s2e77936fa221"], "status": "REASONED", "verify": [1]},
    "verify-host": {"text": "Wrong-Host token request is refused with native 403 while normal Host succeeds; a fronting rejection alone does not demonstrate Server Host checks.", "components": ["server"], "sources": ["server:sf3aa08d40bb0"], "status": "REASONED", "verify": [1]},
    "verify-metrics": {"text": "Compare anonymous metrics with authenticate_prometheus off/on and authenticated metrics content; absent routes or generic errors are inconclusive.", "components": ["server"], "sources": ["server:s70c18acec73c"], "status": "REASONED", "verify": [1]},
    "verify-extension": {"text": "Compare an actual unclassified extension route with allow_unauthenticated_access True/False and its authenticated content; protected kernel routes do not substitute.", "components": ["server-docs", "server"], "sources": ["server-docs:s3036d65c135e", "server:sf3aa08d40bb0"], "status": "REASONED", "verify": [1]},
    "verify-xsrf": {"text": "Cookie-session same-origin POST without XSRF creates a kernel when checks are disabled; fixed missing header gives 403, matching header gives 201 with successful cookie GET.", "components": ["server", "tornado"], "sources": ["server:sf3aa08d40bb0", "server:s52319d21e10e", "tornado:s0f3c220a61fa"], "status": "REASONED", "verify": [2]},
    "verify-origin": {"text": "Wrong-Origin cookie GET returns kernel JSON with allow_origin=*; fixed APIHandler rejects with 404 while same-origin returns 200; also inspect browser CORS headers.", "components": ["server-docs", "server"], "sources": ["server-docs:s3036d65c135e", "server:sf3aa08d40bb0"], "status": "REASONED", "verify": [2]},
    "verify-cleanup": {"text": "Record and shut down every disposable kernel created in either state through the authenticated UI.", "components": ["lab"], "sources": ["lab:s8021535e4b8f"], "status": "REASONED"},
    "verify-root": {"text": "Compare allowed versus refused root startup and inspect server/kernel ownership; fixed unprivileged execution must retain its intended nonzero UID.", "components": ["server"], "sources": ["server:sbb1ed2d8d382"], "status": "REASONED"},
    "verify-terminals": {"text": "Compare authenticated /api/terminals enabled/disabled, retaining a working /api/kernels positive control and kernel shell execution.", "components": ["server-docs", "server"], "sources": ["server-docs:se96d81c5de5a", "server:sbb1ed2d8d382"], "status": "REASONED"},
    "verify-hub-admission": {"text": "Compare valid extra and historical users against the allowlist, with allowed-user login and spawn as positive controls.", "components": ["hub", "hub-5", "hub-docs"], "sources": ["hub:s8c0735472b37", "hub-5:s5ed3cb4eb46f", "hub-docs:s1a8d05a8cf13"], "status": "REASONED"},
    "verify-hub-accounts": {"text": "Two users' server/kernel UIDs must differ as intended, compared with a shared-account fixture.", "components": ["hub-docs"], "sources": ["hub-docs:sad07061feaf6"], "status": "REASONED"},
    "verify-hub-origins": {"text": "Compare shared versus distinct user origins and inspect __Host- cookies for Secure, path / and no Domain attribute.", "components": ["hub", "hub-5", "hub-docs"], "sources": ["hub:scea924dc126d", "hub-5:sf345a9b5625c", "hub-docs:s06a88ed8ee36"], "status": "REASONED"},
    "verify-hub-config": {"text": "Compare a user terminal override loading versus being ignored, deny server-environment writes, and retain a working notebook.", "components": ["hub-docs"], "sources": ["hub-docs:sad07061feaf6", "hub-docs:s06a88ed8ee36"], "status": "REASONED"},
    "verify-listeners": {"text": "ss inventories local binds, not firewall/NAT; confirm actual private listener and external entry point with a working positive control; failed netlink inventory proves no absence.", "components": ["server"], "sources": ["server:sbb1ed2d8d382", "server:sb273e7f052ec"], "status": "REASONED", "verify": [3]},
    "port-default": {"text": "Standalone port starts at 8888 but configuration and retries can change it; inventory the actual listener.", "components": ["server"], "sources": ["server:sbb1ed2d8d382", "server:sb273e7f052ec"], "status": "REASONED"},
    "verify-prefix": {"text": "Probe prefixed and unprefixed Server/Hub routes; require no application alias outside the boundary and working authenticated prefixed access and kernel WebSocket.", "components": ["hub", "server"], "sources": ["hub:s6496de8a4a2b", "server:sbb1ed2d8d382"], "status": "REASONED"},
    "verify-headers": {"text": "Compare spoofed address/scheme/Forwarded headers through real ingress and direct backend access; inspect logs, redirects and cookies with login/WebSocket controls, and the OAuth state cookie's Set-Cookie, whose Secure comes from JUPYTERHUB_PUBLIC_URL, the scheme or, failing both, cookie_options; test a spoofed X-Forwarded-Host and real Host separately.", "components": ["hub", "server", "hub-5"], "sources": ["hub:scea924dc126d", "server:sbb1ed2d8d382", "hub:sa4d711f216d2", "hub:s14ad5e388797", "hub:s11e2575c9dce", "hub:s154792fff6d8", "hub-5:s956c06acb323", "hub-5:s0504cd8b3582", "hub-5:s30f15c6f9d58"], "status": "REASONED"},
    "verify-internal-tls": {"text": "Compare each internal connection with TLS off/on; trusted client certificates succeed, untrusted certificates and wrong hostnames are expected to fail on Hub 5.4+; also try a system-trusted non-internal CA; keep kernel ZeroMQ excluded.", "components": ["hub", "hub-5", "client"], "sources": ["hub:s5223de1d1c52", "hub:sa4d711f216d2", "hub:s3702ddd25f90", "hub-5:s440606cd14bb", "client:s254bb75e8fcd"], "status": "REASONED"},
    "verify-native": {"text": "Test length/common-password, threshold/cooldown and pending-account oracle independently; compare approval with allow_all and empty allowed_users, first-signup preauthorization, disabled signup and stored bcrypt.", "components": ["native"], "sources": ["native:s7e8115fc47c7", "native:s0bd461b12e33"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
