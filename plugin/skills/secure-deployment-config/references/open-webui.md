# Open WebUI: signup control, TLS, and MFA

Open WebUI has account-based authentication built in; the risks are open signup on an exposed instance and running it on plain HTTP. It provides no TLS of its own, so encryption comes from a fronting layer.

At the time of writing, the pinned source identifies release **v0.11.3** at commit `0a7c15832fb30b1903753e83f81dc7d27e5b0944`; the environment reference labels itself current through **v0.11.1**. The controls below were checked against that commit and the linked vendor documentation in September 2026. Introduction versions are unverified unless stated. See the [release version](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/package.json) and [environment reference](https://docs.openwebui.com/reference/env-configuration/).

## 1. Control who can register

Environment variables (defaults per the Open WebUI reference):

```
ENABLE_SIGNUP=false          # default true; disable once your accounts exist (persisted, see below)
DEFAULT_USER_ROLE=pending    # the default; new accounts wait for admin approval
                             # other values: user, admin
```

`ENABLE_SIGNUP` is a persisted setting: the reference marks it a `ConfigVar`, which means the value is written to the database on first launch and on later starts the stored value wins over the environment, unless `ENABLE_PERSISTENT_CONFIG=false` (default `true`). On an instance that has already started, change signup in the Admin panel rather than in the environment, then confirm the change took effect (Verify below).

With signup left on, keep `DEFAULT_USER_ROLE=pending` so a stranger who registers gets no access until approved. An admin account can also be created at startup by setting `WEBUI_ADMIN_EMAIL` together with `WEBUI_ADMIN_PASSWORD` (supply the password via the environment, not a compose file in git; see [secrets.md](secrets.md)).

With normal persisted configuration, the first normal registration automatically disables signup; successful environment-based admin creation does too. On an existing installation, "signup left on" means signup has been explicitly re-enabled. `DEFAULT_USER_ROLE=user` automatically approves subsequent registrations; `admin` gives those registrations administrative privileges. Keep `pending`. See [registration and bootstrap behavior](https://docs.openwebui.com/getting-started/advanced-topics/hardening/).

The first account created becomes the administrator, whatever `DEFAULT_USER_ROLE` is set to; that role governs only the accounts that follow. Claim the admin account yourself while the instance is still bound to loopback, before anyone else can reach it, or preset it with `WEBUI_ADMIN_EMAIL` and `WEBUI_ADMIN_PASSWORD`. On an exposed instance with signup on, whoever registers first is the administrator.

**An empty database is exposed even with `ENABLE_SIGNUP=false` when the login form is enabled.** `/api/v1/auths/signup` does not apply that switch to the first account. `ENABLE_LOGIN_FORM` defaults to `true`. With the form disabled, `ENABLE_INITIAL_ADMIN_SIGNUP=true` permits first-admin bootstrap; its default is `false`, and it should remain off outside private bootstrap. See the [signup handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

For SSO, the reference documents OAuth/OIDC settings plus `ENABLE_PASSWORD_AUTH=false` to turn off password login once SSO works; enforcing MFA then happens at the identity provider ([mfa.md](mfa.md)).

That recommendation applies to **OAuth/OIDC-only login**. `/signin` checks `ENABLE_PASSWORD_AUTH` before trusted-header authentication, so setting it to `false` also blocks trusted-header signin. Ordinary signup refusal does not close OAuth or trusted-header provisioning; configure those separately in step 4. See the [signin handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

The database-over-environment rule also matters for the other `ConfigVar` settings below. On an existing installation, inspect and change their effective values in the Admin panel, or deliberately manage configuration through the environment with persistence disabled. Restarting with a different environment value alone is not proof that a persisted control changed.

## 2. Bind privately and add TLS in front

```bash
docker run -d -p 127.0.0.1:3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

The `-v open-webui:/app/backend/data` volume holds the accounts and the persisted config; the vendor requires it. Reuse the same volume whenever you replace the container (an upgrade starts a fresh one), or the database resets and, by the first-account rule above, the next account to register becomes the administrator. When you do start on an empty database, keep the public proxy route disabled until your admin account exists and signup is confirmed off.

Publish it through [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), through a [Cloudflare Tunnel with Access](cloudflare.md) in front, or over a [tailnet with Tailscale Serve](tailscale.md) (restricted by tailnet policy). Tailscale Funnel is public and adds no login of its own, so keep Open WebUI's own authentication on behind it. Never expose port 8080 directly: login forms over plain HTTP send passwords in cleartext.

Before publishing over HTTPS, set both `WEBUI_SESSION_COOKIE_SECURE=true` and `WEBUI_AUTH_COOKIE_SECURE=true` in the Open WebUI environment and restart. At this pin, the session setting defaults to `false`; the auth setting inherits it unless explicitly overridden. TLS termination alone does not set the cookies' `Secure` attribute, so an HTTP request can send a cookie before a redirect. See the [cookie defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py) and [signin cookie creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

The command above establishes the original private binding and data mount. Before publishing, inject the authentication, secret, and applicable controls below through the deployment configuration. For repeatable deployments, replace the mutable `:main` image reference with the release or digest you have tested.

## 3. Keep authentication on and persist the signing key

```
WEBUI_AUTH=true              # default true
JWT_EXPIRES_IN=24h           # example shorter lifetime; default 4w
```

Generate a strong `WEBUI_SECRET_KEY` with `openssl rand -hex 32`, store it in your secret manager, and inject the same persistent value into every replica. Do not commit it or put its value in command arguments. See [secrets.md](secrets.md), the [authentication defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py), and [token lifetime configuration](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

The container launcher otherwise generates `.webui_secret_key` **once when the file is absent**, then reads it on subsequent starts. It does not generate a new key on every restart. Its default location is `/app/backend/.webui_secret_key`, outside `/app/backend/data`, so replacing the container can lose it despite retaining the data volume. See the [launcher](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/start.sh) and [container working directory](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).

`WEBUI_SECRET_KEY` signs HS256 login tokens. Disclosure enables token forgery for existing users, including administrators. Without Redis, signout clears the browser session but does not revoke a copied JWT; it remains usable until expiry. Choose a finite lifetime suited to the deployment and use shared Redis when revocation must propagate across workers and replicas. See the [token signing and revocation implementation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

Direct backend startup rejects an empty signing key when authentication is enabled. Do not work around that refusal by disabling authentication. `WEBUI_JWT_SECRET_KEY` is the deprecated alias; use `WEBUI_SECRET_KEY`. Plan rotation deliberately: it invalidates existing login tokens, and the key also supplies defaults for OAuth encryption keys. See the [startup requirement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py) and [OAuth key configuration](https://docs.openwebui.com/features/authentication-access/auth/sso/).

## 4. Close alternative registration paths and protect trusted headers

For OAuth deployments that should not provision new users:

```
ENABLE_OAUTH_SIGNUP=false            # default false
OAUTH_ALLOWED_DOMAINS=example.com     # example approved email domain; default *
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=false   # default false
ENABLE_OAUTH_ROLE_MANAGEMENT=false   # default false
```

Replace `example.com` with your approved email domain or comma-separated domains. OAuth account creation checks its own `ENABLE_OAUTH_SIGNUP` switch, independently of `ENABLE_SIGNUP`. Keep email-based account merging off unless the provider's verified-email guarantees have been established, and leave role management off unless you have deliberately reviewed the claims that assign user and admin roles. See [OAuth configuration](https://docs.openwebui.com/features/authentication-access/auth/sso/) and the [pinned defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

`ENABLE_OAUTH_PERSISTENT_CONFIG` defaults to `false`: OAuth settings remain environment-authoritative, unlike ordinary persisted settings. With that default, the OAuth Admin panel is read-only. Enabling OAuth persistence allows database values to take precedence when general persistence is enabled. See [OAuth persistence](https://docs.openwebui.com/features/authentication-access/auth/sso/).

Leave `WEBUI_AUTH_TRUSTED_EMAIL_HEADER` unset unless a trusted authentication proxy supplies identity. If configured, the proxy **must strip client-supplied identity headers**, inject only authenticated values, and be the only route to the backend. Apply the same rule to configured name, role, and group headers. A forged email header can impersonate an existing administrator; trusted-header signin can also provision accounts independently of ordinary signup. See [trusted-header authentication](https://docs.openwebui.com/features/authentication-access/auth/sso/) and the [signin implementation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

For trusted-header deployments, retain `ENABLE_PASSWORD_AUTH=true` because of the `/signin` ordering described in step 1. Enforce MFA and admission at the authenticating proxy, and prevent direct backend access.

## 5. Restrict Tools, Functions, and code execution

If server-side Python plugins are unused:

```
ENABLE_PLUGINS=false                         # default true
USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=false # default false
USER_PERMISSIONS_WORKSPACE_TOOLS_IMPORT=false # default false
ENABLE_CODE_EXECUTION=false                  # default true
ENABLE_CODE_INTERPRETER=false                # default true
```

Creating or importing Tools and Functions loads submitted Python through `exec`. Top-level code runs during loading, with the Open WebUI process's access to secrets, files, database, and network. Treat permission to submit that code as server access, not as an ordinary chat feature. Function creation is administrative; workspace Tool creation is controlled by `workspace.tools`. See the vendor's [plugin-loader explanation](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/).

`ENABLE_PLUGINS=false` stops uploaded plugins loading and running. It is not a blanket authorization switch for every plugin-management endpoint, and it does **not** disable built-in tools, MCP/OpenAPI connections, or terminals. Review those connections and their access separately. The two code-execution switches are separate controls; their engines default to `pyodide`, and the code-execution reference describes the legacy execution path. Browser Pyodide execution is distinct from server-side Python plugins. See [plugin and code-execution controls](https://docs.openwebui.com/reference/env-configuration/).

Audit **every group**, including all memberships of each ordinary user. Group permissions are additive: a false default or a false permission in one group cannot cancel a true grant from another group. Remove unintended Tools Access and Import grants as well as setting the defaults above. Apply this audit to model-workspace access and API-key permissions too. See [group permission merging](https://docs.openwebui.com/features/authentication-access/rbac/groups/) and the [permission defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

## 6. Constrain models, connections, and administrative data access

```
BYPASS_MODEL_ACCESS_CONTROL=false             # default false
USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS=false # default false
ENABLE_DIRECT_CONNECTIONS=false               # default false
ENABLE_ADMIN_CHAT_ACCESS=false                # default true
ENABLE_ADMIN_EXPORT=false                     # default true
ENABLE_COMMUNITY_SHARING=false                # default true
ENV=prod                                     # backend default dev; official Docker default prod
```

Set each restricted model's **Access Control to Private**, then grant only the intended users or groups access. Workspace Models Access governs creation and editing, not which existing models a user may invoke. Inspect existing grants after changing visibility. Current resource payloads use `access_grants`; do not copy an older `access_control` JSON example into current configuration. See [resource access](https://docs.openwebui.com/features/authentication-access/rbac/groups/), [workspace permissions](https://docs.openwebui.com/features/authentication-access/rbac/permissions/), and the [access-grant schema](https://docs.openwebui.com/reference/database-schema/).

Ollama pull, create, copy, and delete routes already require an administrator. There is no `ENABLE_MODEL_*` switch for those operations: the boundary is the caller's role. Restrict admin membership and keep the Ollama service itself private so callers cannot bypass Open WebUI. See the [Ollama route dependencies](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py).

Pin the intended backend destinations in **Settings > Admin > Connections**. The initial OpenAI-compatible destination defaults to `https://api.openai.com/v1`; inspect every configured connection on an existing installation. These URLs specify where Open WebUI sends requests; they are **not an egress firewall**. Independently restrict outbound destinations, including metadata services and unintended internal networks, as described in [egress-metadata.md](egress-metadata.md). See [connection configuration](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/) and the [URL defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

Keep Direct Connections disabled unless required. They send inference requests **from the browser to the provider**, bypassing the backend inference proxy; this setting is not a server-side SSRF defense. See [Direct Connections](https://docs.openwebui.com/features/chat-conversations/direct-connections/).

For chat confidentiality, disable **both** administrative chat access and administrative export, then restart. Otherwise export can expose conversations through a second surface. These controls restrict the application's admin features; they do not conceal data from an operator with database or deployment access. See the [admin control reference](https://docs.openwebui.com/reference/env-configuration/) and [chat-list and export enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py).

`ENABLE_COMMUNITY_SHARING=false` removes community sharing buttons and discovery UI. It does not disable every local sharing or export operation. Review the separate sharing permissions and existing shares where confidentiality requires them. See the [community-sharing reference](https://docs.openwebui.com/reference/env-configuration/).

Interactive API documentation is controlled by `ENV`: `/docs` and `/openapi.json` are registered only in `dev`. The backend defaults to `dev`; the official Docker image sets `prod`. Keep `ENV=prod` in production rather than relying on an unverified `ENABLE_SWAGGER_UI` variable. This removes documentation, not the APIs. See [application initialization](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py), [backend defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py), and the [Dockerfile](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).

## 7. Keep API keys off unless needed

```
ENABLE_API_KEYS=false                    # default false
USER_PERMISSIONS_FEATURES_API_KEYS=false # default false
```

If API clients are required, enable the global switch and grant `features.api_keys` only to selected groups under **Admin Panel > Users > Groups**. Keep the default permission false. Administrators can create keys whenever the global switch is enabled; ordinary users need the feature permission too. Keys inherit the owner's authority, so use an ordinary account for an ordinary application. See [API-key setup and permissions](https://docs.openwebui.com/features/authentication-access/api-keys/).

For an enabled deployment, restrict the routes:

```
ENABLE_API_KEYS=true
ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS=true # default false
API_KEYS_ALLOWED_ENDPOINTS=/api/chat/completions,/api/models
```

The endpoint list is an example for inference and model discovery; remove anything the client does not need. It matches an exact path **and its slash-separated descendants**, not HTTP methods. For example, allowing `/api/models` also allows `/api/models/anything` through this particular check. Enforce narrower path-and-method rules at the proxy when required. The restrictions apply to API keys across the instance, not separately per key. See [API-key configuration](https://docs.openwebui.com/features/authentication-access/api-keys/) and [endpoint matching](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

Disabling the global switch rejects existing API keys as well as preventing creation; it does not delete those keys, and it does **not** disable JWT-authenticated APIs. See the [separate API-key and JWT authentication paths](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

`ENABLE_API_KEY`, `ENABLE_API_KEY_ENDPOINT_RESTRICTIONS`, and `API_KEY_ALLOWED_ENDPOINTS` are deprecated names. Use the plural names shown above; do not assume every deprecated name is still honored by every release. See the [environment reference](https://docs.openwebui.com/reference/env-configuration/).

## 8. Bound retrieval, network access, and resource use

```
ENABLE_LOCAL_WEB_FETCH=false          # default false
AIOHTTP_CLIENT_ALLOW_REDIRECTS=false  # default false
WEB_FETCH_FILTER_LIST=docs.example.com,!internal.example.com
ENABLE_WEB_SEARCH=false              # default false; keep off if unused
RAG_FILE_MAX_SIZE=10                  # example limit in MB; default unset
RAG_FILE_MAX_COUNT=5                  # example file count; default unset
USER_PERMISSIONS_CHAT_FILE_UPLOAD=false # default true
USER_PERMISSIONS_CHAT_WEB_UPLOAD=false  # default true
USER_PERMISSIONS_FEATURES_WEB_SEARCH=false # default true
```

Replace the filter domains with your intended policy. `WEB_FETCH_FILTER_LIST` is comma-separated: entries without `!` form an allowlist, while `!` entries deny destinations. Custom entries extend the built-in blocklist. Keep local fetch and redirects disabled to reduce SSRF paths into private networks and cloud metadata services; enforce network egress separately. `ENABLE_RAG_LOCAL_WEB_FETCH` is the deprecated alias of `ENABLE_LOCAL_WEB_FETCH`. See [web-fetch configuration](https://docs.openwebui.com/reference/env-configuration/), the [filter and alias definitions](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py), and the [redirect default](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).

Choose finite positive file limits for the available storage and processing capacity. They are not an aggregate storage quota or a general request quota. In the upload handler, the size check occurs after the storage upload has read the file, so also bound request bodies at the proxy. See the [upload handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py).

**The feature permissions above are not sufficient to prohibit direct ingestion requests.** `POST /api/v1/files/` and `POST /api/v1/retrieval/process/web` require a verified user, but their handlers do not check the corresponding file-upload or web-upload feature permission. A verified user means an authenticated `user` or `admin`, not a pending account. If uploads must be unavailable, deny `/api/v1/files/` and applicable ingestion routes at the proxy. If URL ingestion must be unavailable, deny `/api/v1/retrieval/process/web`, `/api/v1/retrieval/process/youtube` (the same handler), and `/api/v1/retrieval/process/url` (which fetches URLs and can invoke web processing or file ingestion). Audit group grants and prevent access around the proxy. See [file uploads](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py), [URL ingestion](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py), and [verified-user roles](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

The native password-signin limiter is **15 attempts per 180 seconds per email address**. It is not an inference quota. Add proxy rate and concurrency limits, plus provider or gateway spend limits, for authenticated requests as well as anonymous traffic. See the [signin limiter](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py), [nginx.md](nginx.md), and [litellm.md](litellm.md).

## 9. Verify

Service behavior in this replacement has not been demonstrated. The authoring environment has no Docker or Podman runtime or Docker socket, is read-only, and has no supplied live Open WebUI, second-host fixture, identity provider, or provider test credentials. The live comparisons below are therefore **REASONED**, with demonstration debt recorded as `OPENWEBUI-LIVE-1`.

Run exposed comparisons only on a private, disposable installation. Keep production bootstrap private. Use ordinary users as well as administrators: an administrator's successful request does not demonstrate an ordinary user's boundary.

### Private binding, TLS, and ordinary signup

**REASONED:** This needs a deployed container, TLS ingress, and a second LAN/VPC host, unavailable here. The original listener, TLS, feature-flag, and browser checks are retained below with guarded URL substitution. Substitute your actual HTTPS origin inside the quotes on the `set --` line. Paste the whole block; do not put credentials in URLs. Values containing a literal apostrophe require proper shell quoting rather than direct substitution.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://chat.example.com'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one HTTPS origin; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute your HTTPS origin inside the quotes; not probing"; exit 1 ;;
    https://*)
      ss -tlnp   # read every listener; the published mapping should be 127.0.0.1:3000 only, never 0.0.0.0 or ::.
                 # ss shows host listeners, not Docker's NAT: use Docker Engine 28.0+ for loopback publishing
                 # (older engines let a same-L2 host reach a localhost-published port), confirm the mapping is
                 # 127.0.0.1:3000->8080/tcp, and from another LAN/VPC host confirm nothing answers on port 3000.
      curl -q -g -sSI --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/"
                                           # serves over TLS without -k; --noproxy so a client proxy cannot answer
      # Signup state, programmatically: Open WebUI serves its feature flags at /api/config.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 "${1%/}/api/config"
                                           # JSON feature flags; confirm signup is disabled there (features.enable_signup: false)
      # In a private browser window, AFTER your admin account exists: the sign-up option is absent AND an actual
      # registration attempt is REFUSED (a missing button alone is not proof). With signup on, registering a new
      # account yields a pending/unapproved user, not access.
      ;;
    *) echo "use an HTTPS origin without credentials; not probing"; exit 1 ;;
  esac
)
```

The exposed comparison has a reachable backend publication or lacks working certificate-validated HTTPS. The fixed deployment serves HTTPS successfully and publishes only the intended loopback mapping. A certificate error, local socket error, or DNS failure is not proof that ingress is private. See [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/).

**REASONED:** From the separate LAN/VPC host, probe the actual Open WebUI host address. This second host is unavailable here. For IPv6, put the literal address in square brackets inside the quotes. A privately isolated exposed fixture should answer on port 3000; the fixed publication must not. Confirm that the intended HTTPS service still works and inspect the reported error before attributing a failure to the network boundary.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_OPENWEBUI_HOST_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one host address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute the actual host address inside the quotes; not probing"; exit 1 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/"
      ;;
  esac
)
```

### Protected requests for the comparisons below

Prepare a mode-0600 header file in a private directory containing `Authorization: Bearer ` followed by the disposable test JWT or API key. Use an empty file for anonymous requests. Put JSON request bodies, including signup passwords, in a separate protected file; use an empty body file for GET. For `UPLOAD`, the body file is the harmless file to upload.

Use the actual HTTPS endpoint, or `http://127.0.0.1:3000/...` on the backend host. Replace placeholders inside the quoted arguments. Responses are captured privately because signin, signup, API-key, and export responses can contain credentials or private data.

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
    https://*|http://127.0.0.1:3000/*)
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
        DELETE)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            --request DELETE \
            -H "@$3" -H 'Content-Type: application/json' --data-binary "@$4" \
            -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        UPLOAD)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -F "file=@$4" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        *) echo "use GET, POST, DELETE or UPLOAD; not probing"; exit 1 ;;
      esac
      ;;
    *) echo "use HTTPS or the loopback backend; not probing"; exit 1 ;;
  esac
)
```

The guard checks arguments, not file contents. Inspect request files before sending them, especially registration bodies and requests captured from administrative actions. Do not use a production credential for an exposed comparison. Remove test accounts, keys, uploads, and private response files after recording redacted evidence.

### Authentication and provisioning

**REASONED:** Cookie attributes need a running Open WebUI, HTTPS ingress, disposable login, and configured OAuth provider; no container runtime or live fixture is available here. With password signin enabled on the private fixture, use the protected helper to POST `/api/v1/auths/signin` with valid `email` and `password` fields; inspect the saved `headers` file for the `token` cookie. In a fresh browser, visit `/oauth/REPLACE_WITH_CONFIGURED_PROVIDER/login` with the provider substituted, complete login, and inspect `Set-Cookie` headers throughout the flow for `owui-session`. With both Secure settings false and no proxy cookie rewriting, issued cookies should lack `Secure`. After setting both true and restarting, repeat through public HTTPS: require `Secure` and `HttpOnly` on both cookies and check `SameSite` against the intended configuration (`lax` by default). A response that issues no relevant cookie is inconclusive; record unused flows as not applicable. Redact cookie values. See [auth cookie creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py), [session middleware](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py), and [cookie defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).

**REASONED:** These comparisons require a running disposable Open WebUI, controlled accounts, a trusted proxy, an identity provider, and optional shared Redis, unavailable here. Use the protected request block and the specified browser flows.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| Ordinary signup and first-admin exception | POST `/api/v1/auths/signup` anonymously with valid `name`, `email`, and `password` fields in the protected body. On an empty fixture with the login form enabled, even `ENABLE_SIGNUP=false` permits bootstrap. After bootstrap, explicitly enabled signup admits a pending account; disabled signup returns 403. See the [signup handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py). |
| OAuth provisioning | In a fresh browser, visit `/oauth/REPLACE_WITH_CONFIGURED_PROVIDER/login`, substituting the configured provider, and complete login with a new approved-domain identity. With OAuth signup enabled, provisioning can occur despite ordinary signup being off; with it disabled, the new identity must not be provisioned. An already-linked permitted account should still sign in. Separately try an excluded domain. See [OAuth signup and domain controls](https://docs.openwebui.com/features/authentication-access/auth/sso/). |
| Trusted identity and password-auth ordering | POST `/api/v1/auths/signin` with the fixture's configured identity header in the protected header file and a valid signin-shaped JSON body. An unstripped forged admin header can impersonate that admin; fixed ingress must reject it or replace it with the authenticated identity. Separately, `ENABLE_PASSWORD_AUTH=false` makes `/signin` return 403 before trusted-header handling. See the [signin handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py). |
| Key persistence and token lifecycle | Sign in and save the JWT privately. GET `/api/models` before and after recreating the disposable container with the same data volume and injected key, then against each replica: the unexpired token should continue working. A changed signing key rejects it. POST `/api/v1/auths/signout`, then repeat GET using the saved token: without Redis it remains usable until expiry; with working shared revocation it is refused on every worker. Check expiry separately. See [token validation and revocation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py). |

### Execution, models, connections, and data

**REASONED:** These comparisons need a running UI, disposable users and groups, reviewed harmless plugins, a working model backend, and controlled connection targets, unavailable here. Save any browser-generated request used for replay into protected files; do not put its credentials in command arguments.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| Plugin execution | With a reviewed canary Tool or Function enabled on the private fixture, submit a chat that invokes it and record its harmless marker. Disable plugins, restart, and repeat the same chat request: the plugin must no longer execute. GET `/api/v1/functions/` and `/api/v1/tools/` too; local plugins disappear, while external tool servers may remain. A management request being accepted does not by itself mean execution is enabled. See [plugin loading](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/) and [the switch's scope](https://docs.openwebui.com/reference/env-configuration/). |
| Additive group permissions | With plugins enabled only on the private fixture, give a test user a group Tools Access grant while the default remains false. Save a reviewed harmless Tool through the workspace. Remove the grant from every membership and repeat the same valid creation request: ordinary-user authorization must refuse it. A false grant in a second group must not be mistaken for a deny. See [permission merging](https://docs.openwebui.com/features/authentication-access/rbac/groups/). |
| Code execution | On the private fixture, compare execution of a harmless `print(1 + 1)` chat code block and a code-interpreter request before and after disabling their respective switches. Record browser and configured-engine activity separately; after disabling, those execution paths should be unavailable. This does not test terminals or server-side plugins. See [code-execution controls](https://docs.openwebui.com/getting-started/advanced-topics/hardening/). |
| Model access | GET `/api/models`, then POST a minimal valid chat to `/api/chat/completions` using a configured test model. Compare a user with a read grant and one without it after making the model Private. The authorized user must still obtain a completion; the excluded user must not invoke that model. Also confirm the excluded user cannot create workspace models. See [model access grants](https://docs.openwebui.com/features/authentication-access/rbac/groups/) and [API request examples](https://docs.openwebui.com/reference/api-endpoints/). |
| Ollama administration | On an isolated backend, capture valid pull, create, copy, and delete requests for disposable model resources. Use `DELETE /ollama/api/delete` for deletion (or `/ollama/api/delete/{url_idx}` with the actual backend index), selecting `DELETE` in the protected helper and putting the disposable model's `model` field in the protected JSON body. Replay each with an ordinary user's JWT, then an administrator's JWT. Ordinary users must receive authorization refusal before the backend operation; matched admin requests establish that the payload and backend work. Never test deletion against a production model. See [Ollama administrative routes](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py). |
| Connection destinations | Send a canary chat through each approved backend connection and inspect backend egress records. In a private fixture with disposable credentials, compare an approved destination with a controlled destination excluded by the network policy. The latter must receive no request while the approved destination works. If testing Direct Connections, browser network records should show browser-to-provider inference when enabled and its absence when disabled. See [Direct Connections](https://docs.openwebui.com/features/chat-conversations/direct-connections/) and [egress-metadata.md](egress-metadata.md). |
| Administrative chat access and export | As an admin, GET `/api/v1/chats/list/user/REPLACE_WITH_TEST_USER_ID` and `/api/v1/chats/all/db`, substituting the test user ID. With the controls enabled, the fixture exposes its canary chats. After disabling both controls and restarting, both requests must be refused; the chat owner must retain normal access. See [chat-list and export enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py). |
| Documentation and community UI | GET `/docs` and `/openapi.json` on the backend and public origin. Compare an isolated `ENV=dev` fixture with `ENV=prod`: Swagger and the OpenAPI schema must disappear. Inspect content, since a 200 response containing the application shell is not API documentation. With community sharing disabled, inspect the workspace discovery sections and community-share buttons; their disappearance does not demonstrate that local export or sharing is disabled. See [documentation registration](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py) and [community UI scope](https://docs.openwebui.com/reference/env-configuration/). |

### API keys, ingestion, and resource limits

**REASONED:** These comparisons require a live deployment, disposable API keys, controlled web destinations, proxy logs, and an approved bounded provider allowance, unavailable here.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| API-key enablement and scope | With a selected ordinary user's working key, GET `/api/models`. Disable the global key switch and repeat: the existing key must be refused while a valid JWT still works. Re-enable keys with the step 7 allowlist: `/api/models` remains permitted, while GET `/api/v1/auths/` is refused for the key. Remove the user's API-key permission from every group and repeat the permitted request: it must now fail. Use real existing routes when testing descendants and methods; a nonexistent route's 404 proves no scope boundary. See [key permissions](https://docs.openwebui.com/features/authentication-access/api-keys/) and [endpoint enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py). |
| Upload permission limitation and body limits | Use `UPLOAD` with `/api/v1/files/` and a small harmless document as a verified ordinary user. With the UI feature permission false but no proxy route block, the direct handler can still accept it. With the intended proxy restriction, it must be refused. Where uploads are allowed, compare files just below and above the chosen size limit, including multipart overhead in the proxy limit. Confirm the smaller upload works. Test the configured file count separately; it does not establish an aggregate quota. See [upload enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py). |
| URL ingestion and SSRF | POST `/api/v1/retrieval/process/web?process=false` with a JSON body containing `url` set to your controlled test page. Compare an allowed public destination, a controlled private destination, a filter-denied destination, and a redirect to the controlled private destination. Inspect destination and egress logs. Fixed controls must prevent forbidden contact while the allowed page succeeds. Where URL ingestion is prohibited, directly POST to each of `/api/v1/retrieval/process/web?process=false`, `/api/v1/retrieval/process/youtube?process=false`, and `/api/v1/retrieval/process/url?process=false` using a verified ordinary user's JWT and the protected JSON body containing the controlled public page's `url`. On the private fixture without proxy denial, establish that each request can fetch the page despite the disabled UI permission. With proxy denial, each must be refused before reaching its handler, with no destination contact; confirm this in proxy and destination logs. A malformed request or failed fetch does not demonstrate prohibition. Never probe real metadata services. See [URL ingestion](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py) and [outbound fetch protections](https://docs.openwebui.com/getting-started/advanced-topics/hardening/). |
| Search, rate, and spend | Compare a harmless search-enabled chat on the private fixture before and after disabling web search; check the controlled search provider for calls. Separately submit a bounded series of valid `/api/chat/completions` requests across the chosen proxy rate threshold and provider/gateway spend threshold. Under-limit controls must work; excess requests must be refused by the configured limiting layer without further provider work. The signin limiter is not evidence for either result. See [network-layer limits](https://docs.openwebui.com/getting-started/advanced-topics/hardening/), [nginx.md](nginx.md), and [litellm.md](litellm.md). |

### Demonstration backlog

This row carries the original probes and the new controls together. Configuration inspection alone does not close it. For `OPENWEBUI-LIVE-1`, explicitly record the DELETE model comparison, individual proxy refusal for all three URL-ingestion routes, and exposed/fixed authentication and session `Set-Cookie` attributes.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| OPENWEBUI-LIVE-1 | Demonstrate every REASONED comparison above on a recorded Open WebUI release and image digest, with disposable data, a second-host IPv4/IPv6 ingress fixture, controlled users/groups, OAuth and trusted-header fixtures, shared Redis and multiple workers, reviewed canary plugins, an Ollama test backend, controlled web destinations, and bounded provider credentials. Include first-admin signup with an empty database and signup disabled; bootstrap with the login form disabled; signup auto-disable and persistence; password-auth ordering; forged-header rejection; OAuth signup/domain boundaries; signing-key persistence across recreation and replicas; expiry and signout revocation; additive permissions; plugin and code-execution separation; model access and administrative operations; destination controls; admin chat/export refusal; documentation and community UI scope; API-key disablement and endpoint matching; direct ingestion despite UI permissions; file limits, SSRF and redirects; and proxy/provider rate and spend enforcement. Record commands, response content, positive controls, versions, propagation timing, costs, and cleanup. | Open; service behavior is reasoned, not demonstrated. |

## Sources (checked September 2026)

- Open WebUI environment configuration reference: https://docs.openwebui.com/reference/env-configuration
- Open WebUI FAQ (the first account created becomes the administrator): https://docs.openwebui.com/faq
- Open WebUI repository (the Docker Quick Start `-v open-webui:/app/backend/data` data volume): https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/README.md
- Docker port publishing (localhost publishing; releases older than 28.0.0 let a same-L2 host reach a localhost-published port): https://docs.docker.com/engine/network/port-publishing/
- [Open WebUI pinned release version](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/package.json).
- [Open WebUI configuration defaults: signup, permissions, OAuth, code execution, API keys, connections, retrieval limits, and web-fetch filters](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).
- [Open WebUI environment defaults: authentication, signing-key requirement, trusted headers, plugins, model bypass, admin chat access, redirects, and ENV](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).
- [Open WebUI launcher: persistent key-file generation and loading](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/start.sh).
- [Open WebUI Dockerfile: backend working directory and production environment](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).
- [Open WebUI auth routes: first-admin signup, auto-disable, password-auth ordering, trusted-header provisioning, signin limiter, and API-key creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).
- [Open WebUI authentication helpers: HS256 signing, Redis revocation, API-key enforcement, path matching, and verified-user roles](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).
- [Open WebUI application initialization: environment-based admin creation, API documentation, and OAuth routes](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py).
- [Open WebUI Ollama router: model access and administrator-only management operations](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py).
- [Open WebUI chat router: administrative chat access and export checks](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py).
- [Open WebUI file router: verified-user upload dependency and size enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py).
- [Open WebUI retrieval router: web and URL ingestion handlers](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py).
- [Open WebUI hardening: registration lifecycle, execution controls, network limits, and outbound protections](https://docs.openwebui.com/getting-started/advanced-topics/hardening/).
- [Open WebUI SSO: OAuth/OIDC, trusted headers, and OAuth persistence](https://docs.openwebui.com/features/authentication-access/auth/sso/).
- [Open WebUI plugin loader: exec and server-process authority](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/).
- [Open WebUI groups: additive permissions and private resource grants](https://docs.openwebui.com/features/authentication-access/rbac/groups/).
- [Open WebUI permissions: workspace and sharing controls](https://docs.openwebui.com/features/authentication-access/rbac/permissions/).
- [Open WebUI database schema: normalized access grants](https://docs.openwebui.com/reference/database-schema/).
- [Open WebUI API keys: global enablement, group permissions, and inherited authority](https://docs.openwebui.com/features/authentication-access/api-keys/).
- [Open WebUI Direct Connections: browser-to-provider inference](https://docs.openwebui.com/features/chat-conversations/direct-connections/).
- [Open WebUI OpenAI-compatible connections: administrative provider configuration](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/).
- [Open WebUI API endpoints: model discovery, chat requests, ingestion, and development documentation](https://docs.openwebui.com/reference/api-endpoints/).
