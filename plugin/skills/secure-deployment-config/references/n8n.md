# n8n: binding, TLS, and MFA

n8n is a workflow automation tool with a web editor and webhook endpoints. This guide helps your AI assistant make sure it is configured securely: a private bind, TLS from a proxy or n8n itself, accounts with MFA, webhook authentication, and code-node execution isolated.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/n8n.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against n8n listener source n8n@2.40.6, n8n runtime source n8n@2.40.6, n8n environment policy minimum 2.18.0, n8n SSRF filter minimum 2.12.0, n8n 2.0 default exclusion source n8n@2.0.0, n8n 1.x default exclusion source n8n@1.123.85, and express-openapi-validator v5.5.3, plus 5 more recorded bases; 2 further sources are pinned to a commit and 2 carry no recorded version. Metadata reviewed 2026-10-21; documentation checked October 2026. The guide records 40 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

n8n includes user management (complete the owner setup on first run), but its network defaults deserve attention: `N8N_LISTEN_ADDRESS` defaults to `::` and `N8N_PORT` to `5678` (both as of n8n 2.40.6), so n8n listens on **all interfaces** over plain HTTP.

## 1. Bind privately

Behind a reverse proxy or tunnel (the recommended layout):

```
N8N_LISTEN_ADDRESS=127.0.0.1
N8N_PORT=5678
N8N_HOST=n8n.example.com
```

`N8N_LISTEN_ADDRESS=127.0.0.1` is right for n8n running directly on the host behind a same-host proxy. INSIDE a bridged Docker container it binds the container's own loopback, so a sibling proxy container or a published port cannot reach it: there, either put n8n and the proxy on a private Compose network with NO published n8n port, or publish to host loopback only (`127.0.0.1:5678:5678`). Keep the Postgres and task-runner broker ports unpublished either way. Publish only the proxy per [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or use [cloudflare.md](cloudflare.md)/[tailscale.md](tailscale.md).

Set the public URL fully, not just `N8N_HOST`: `N8N_PROTOCOL=https`, `N8N_WEBHOOK_URL=https://n8n.example.com/` (the external base for generated webhook URLs; it replaces the `WEBHOOK_URL` alias, deprecated from n8n 2.35.0 though the old name still works with a warning), and keep `N8N_SECURE_COOKIE=true` (its default). Behind a proxy also set the trusted proxy-hop count (`N8N_PROXY_HOPS`) so client IPs and rate limiting are read from the right forwarded header. Webhook endpoints are meant to be reachable by external services; that is no reason for the editor UI to be.

## 2. Or terminate TLS in n8n itself

```
N8N_PROTOCOL=https        # default is http
N8N_SSL_KEY=/path/to/privkey.pem
N8N_SSL_CERT=/path/to/fullchain.pem
```

## 3. Accounts and MFA

- Finish the owner-account setup before publication. At n8n 2.40.6, the owner setup handler skips authentication and issues the new owner a session cookie.
- Individual users can enable two-factor authentication on their accounts (verify availability for your version and licence).
- Instance-wide enforcement exists under **Settings > Security** ("Enforce two-factor authentication"), or via `N8N_MFA_ENFORCED_ENABLED=true` with `N8N_SECURITY_POLICY_MANAGED_BY_ENV=true` (the environment-managed policy is available from n8n 2.18.0, so confirm your version and that enforcement actually takes effect); per the n8n docs this enforcement requires a Business or Enterprise licence on self-hosted instances, and it does not apply to SSO logins (enforce MFA at the identity provider for those; [mfa.md](mfa.md)).
- Credentials stored in n8n (API keys for the services your workflows touch) make the instance a secrets vault; treat access to it accordingly ([secrets.md](secrets.md)). Those credentials are encrypted at rest with `N8N_ENCRYPTION_KEY`: leaving it unset does NOT mean plaintext (n8n generates a random key on first launch and saves it under `~/.n8n`), but losing that key while keeping the database makes every stored credential unrecoverable, and committing it hands the decryption secret to anyone who reads the repo. Set it explicitly, keep the same value across every worker/replica, back it up separately from the database, and keep it out of source control and images ([secrets.md](secrets.md)).

## 4. Webhook authentication

- A Webhook node left on **None** answers anyone who reaches its URL. For a webhook whose caller you control, set the node **Authentication** to **Basic auth**, **Header auth**, or **JWT auth** and attach the matching Webhook credential.
- Webhook authentication is configured per node and is separate from the instance login and the public API key (`X-N8N-API-KEY`). Hardening the editor or `/api/v1` does nothing for webhook endpoints, so audit every Webhook node individually.
- Where a third party must call the webhook and cannot present your credential, **None** is unavoidable at the node, so the workflow itself must authenticate the request: validate the provider's signature (for example an HMAC header) in the first node after the Webhook trigger and reject a missing or wrong signature before any further processing. A **None** webhook with no such check is open.

## 5. Code-node isolation and outbound requests

- Workflow editors can run code: the **Code** node executes JavaScript/Python and the **Execute Command** node runs the command through a shell in a child process of the n8n process executing the node. At n8n 2.40.6, `NODES_EXCLUDE` disables Execute Command by default; the commit-pinned n8n 2.0.0 and 2.43.8 defaults exclude Execute Command and Local File Trigger, while the commit-pinned n8n 1.123.85 default on the 1.x line is empty (excludes none). Commit a4757cf0 ("chore: Initial V2 changes", 2025-12-01) changed this default in `nodes.config.ts` from empty to those two node types; n8n 2.0.0-rc.0, the lowest-version 2.x tag, has that default, while n8n 1.123.0 keeps it empty, and the four later commits to `nodes.config.ts` through ea8417e2 do not change it. This guide's assessment of `nodes.config.ts` at each n8n tag, as of October 2026, is that the default stays empty at every 1.123.x tag and excludes both nodes at every 2.x tag from 2.0.0-rc.0 through 2.45.0, including the commit-pinned 2.45.0 file; releases after 2.45.0 are not covered and no release was run, so confirm the default on your installed version. The rolling 2.0 changes page, which is unversioned, also lists both nodes as disabled by default in n8n 2.0. Leave it off unless a workflow truly needs it. Run code on hardened EXTERNAL task runners rather than the internal mode, which the vendor calls insecure by design, and keep workflow `$env` access blocked (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`; at n8n 2.40.6 the `$env` proxy is blocked unless the variable is set to `false`). This guide's assessment is that this guard alone does not establish isolation of every node or Code `process.env`. Allow only the modules a workflow needs, narrowly, and set the allowlist where the RUNNER reads it, not just on the main n8n container (whose values the external launcher overrides): for the JavaScript runner, `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL` under `env-overrides` in the launcher's `/etc/n8n-task-runners.json`; for the Python runner, `N8N_RUNNERS_STDLIB_ALLOW` and `N8N_RUNNERS_EXTERNAL_ALLOW`. An unset-then-`*` allowlist gives arbitrary module access. Because these defaults have shifted across versions and one vendor table is stale, set each value explicitly and confirm it on your installed version.
- At n8n 2.40.6, the JS task runner builds a context with module resolution, console, workflow static data, selected native globals, the data proxy, RPC and additional properties. This guide reasons that no direct `process` binding appears in the explicit native list or context; imported modules and injected properties prevent treating that omission as complete `process.env` isolation.
- At n8n 2.40.6, the JS data proxy receives `envProviderState`; if absent, its fallback is `env: {}`, `isEnvAccessBlocked: false` and `isProcessAvailable: true`. This guide reasons that the fallback avoids using the runner environment for `$env`; the cited consumer does not establish the contents or production of incoming state.
- At n8n 2.40.6, JS all-items and per-item execution use `runInContext` in secure mode and `runDirectly` in insecure mode. This guide reasons that the latter, using `new Function` with `with(context)`, can resolve ambient `process.env` unless shadowed; this is not a live demonstration or proof of complete isolation in secure mode.
- At n8n 2.40.6, Python all-items and per-item execution clear `os.environ` before user code only if `runner_env_deny` is true; the runner sets it from `N8N_BLOCK_RUNNER_ENV_ACCESS`, read with default `True`, so by default they clear it, and when false, they do not clear the task process environment. This guide did not trace how `read_bool_env` parses the value or establish effective module access.
- At n8n 2.40.6, Python `read_env` reads `os.environ` first, otherwise a file named by the corresponding `_FILE` variable, or returns `None`. This guide assesses that this configuration reader does not itself establish which environment values user code can access.
- Launcher 1.5.1 prepares the runner environment from its own `LANG`, `PATH`, `TZ` and `TERM` plus names in `allowed-env`; `env-overrides` sets values directly. This guide advises keeping secrets out of `allowed-env` and keeping that list narrow, because listed values can enter the runner process environment.
- Launcher 1.5.1 sets the task broker URI, health-check enable flag and port, and legacy auto-shutdown and task timeouts. It removes inherited required runtime keys, including the grant token, and ignores their `env-overrides`; other overrides replace prior values, while grant-token insertion is not shown by this preparation function.
- This guide's assessment is that the cited n8n 2.40.6 runner and launcher 1.5.1 sources describe specific environment controls for external runners, not complete host/container isolation. Internal-mode runners, other nodes, other launcher versions, deployed configuration and complete Code `process.env` isolation remain unestablished.
- Outbound requests are a trust boundary too: a webhook or the **HTTP Request** node can be steered at internal services or the cloud metadata endpoint (SSRF). Enable n8n's own SSRF filter where available (`N8N_SSRF_PROTECTION_ENABLED=true`, from n8n 2.12.0) AND restrict the workload's egress so a request cannot reach your internal network or `169.254.169.254` ([egress-metadata.md](egress-metadata.md)); the app-level filter supplements a network control and does not contain arbitrary code- or command-node networking.

## 6. Verify

REASONED: n8n 2.40.6's registry returns the first non-null strategy result, or `false` if all abstain; `ApiKeyAuth`, `BearerAuth` and `CookieAuth` return that result. Its pinned express-openapi-validator 5.5.3 calls `AuthValidator.validate()` before the handler ([lines 165-174](https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L165-L174)); for a header `apiKey` scheme, a missing header throws an `Error` without a status ([lines 265-271](https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L265-L271)). This guide's assessment: a false result or a thrown error without a status gets fallback status 401 ([lines 142-185](https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L142-L185)); when security fails and that failure is selected, the validator forwards an `HttpError` with that status, while exceptions can supply other statuses. The source `openapi.yml` declares `ApiKeyAuth` as a header `apiKey` scheme named `X-N8N-API-KEY`, `BearerAuth` as a bearer JWT scheme and `CookieAuth` as an `apiKey` cookie named `n8n-auth`, each as a separate global security requirement ([lines 167-185](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L167-L185)). n8n serializes `HttpError` as a message object with its status (400 if falsy); `Unauthorized` with a session cookie gets 401 and message `Unauthorized`.

REASONED: source limits and guide advice for the API probes below; no live n8n deployment is available and no API outcome was observed. The cited `workflows.handler.ts` lines implement only `getWorkflowVersion`: success returns version JSON without `autosaved` and no explicit status. Public controllers precede the validator, so a controller-owned route can respond before the validator's security check ([ownership, lines 154-155](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L154-L155), [controller activation, lines 232-236](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L232-L236), [mount order, lines 374-380](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L374-L380)). The registry mounts each public controller's router at its base path ([registry activation, lines 55-67](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L55-L67)); `v1/controllers/index.ts` imports the workflows controller so its decorator metadata is registered ([lines 1-16](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/index.ts#L1-L16)), and that controller is `@PublicApiController('/workflows')` with `getWorkflows` on `@Get('/')` and `@ApiKeyScope('workflow:list')` ([lines 205-206](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L205-L206), [lines 229-235](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L229-L235)). This guide has not traced the decorators' implementation or the public API endpoint wiring. The registry applies authentication middleware to every controller route and returns 401 `Unauthorized` when the auth registry does not authenticate ([controller authentication, lines 120-168](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L120-L168)); on a route with an API key scope, the next middleware returns 403 `Forbidden` when the request has no token grant or its key scopes do not satisfy that scope ([scope check, lines 188-199](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L188-L199)). This guide's inference concerns ordering relative to the validator, not skipping authentication. On success, `getWorkflows` returns an object with a `data` array of workflows and a `nextCursor` ([lines 277-302](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L277-L302)); the registry sends a defined result, parsed by the route's response DTO when it has one, as JSON with the status that `resolveSuccessStatus` returns, unless that status is 204, and this guide has not traced that function's source ([lines 77-81](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L77-L81), [lines 106-117](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L106-L117)). The source `openapi.yml` lists no `/workflows` list path, only `/workflows/{id}/...` sub-paths ([lines 79-159](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L79-L159)); the generated `getWorkflows` spec records scope `workflow:list` and declares 200 with required `data` and `nextCursor`, 400, 401 and 403 ([lines 1-6](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L1-L6), [lines 43-47](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L43-L47), [lines 562-573](https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L562-L573)). This guide's assessment: a request without credentials gets 401 `Unauthorized` from the route's authentication middleware if no auth strategy authenticates it; the strategies' handling of such a request is not traced. Compare no `X-N8N-API-KEY` with a valid key at that same URL, keeping proxy credentials constant and feeding the key on stdin; rejection (for example 401) and 200 workflow JSON remain expectations to observe, and a fronting proxy can alter the status.

```bash
# REASONED: listener, TLS, API and webhook comparisons have no recorded n8n run; no live n8n deployment is available in this read-only review. Expected API status outcomes require a live check; the assessment above traces conditional public-API refusal and the workflows list route's middleware and response body, and leaves its success status untraced; pinned source still establishes the Webhook refusal codes.
# On 2026-10-13 (UTC), against a stub curl, the placeholder was refused with the substitute message and a line feed, carriage return, tab or DEL with the control-character message, before any curl call; a valid dummy key let both curl calls run and reached only the with-key call, on its stdin.
# Owner setup must be COMPLETE before the instance is public: the pinned owner setup handler
# skips authentication and issues an owner session cookie. Confirm the owner exists; do NOT POST
# owner-creation data to a live instance as a "test".
ss -tlnp   # a listener inventory in THIS namespace, not a firewall/NAT check: n8n on 127.0.0.1 (or its
           # private container network), with the Postgres and task-runner ports NOT published. Loopback
           # can be 127.0.0.1 and/or ::1; also probe the real public IPv4/IPv6 path from another host.
# TLS reachability (proves TLS, not authentication):
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null \
  -w 'tls=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://n8n.example.com/
# Public API auth, matched pair against the same URL: expect rejection without the n8n key
# (for example 401) and 200 workflow JSON with a valid key; verify both outcomes on your instance.
# The key is fed on stdin (-H @-), so it stays out of curl's argv; the one on the set -- line still enters shell history, so use a short-lived key and clear it.
# Stdin closes the argv channel only: it does not hide the key from set -x tracing or your own
# account's view of the process.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_N8N_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the API key on the set -- line above; not probing"; exit 1 ;; esac
  case "$1" in *[[:cntrl:]]*) echo "the API key must be one line with no control characters; not probing"; exit 1 ;; esac
  u=https://n8n.example.com/api/v1/workflows
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-key=%{http_code} exit=%{exitcode}\n' "$u"
  printf 'X-N8N-API-KEY: %s\n' "$1" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\nwith-key=%{http_code} exit=%{exitcode}\n' -H @- "$u"
)
# no-key => expect rejection by n8n; check the observed status (a fronting proxy can also 401, so hold its
# credential constant and vary only the n8n key). With-key => expect 200 and workflow JSON.
# The editor login is POST /rest/login with the default REST prefix; confirm editor access separately.
# Webhook auth: the api/v1 check says NOTHING about webhooks. Test each PRODUCTION webhook (prefix
# /webhook/, never /webhook-test/) with the method the node expects and a valid payload, three ways: no
# credential, a WRONG credential, and the valid one. With configured node credentials, missing
# Basic/JWT auth returns 401 and missing Header auth returns 403 in the pinned handler.
# Valid calls must perform the expected action; missing/wrong calls must not. A 200 alone is not proof (a workflow can respond 200 without acting); a 404 means inactive/wrong
# method/wrong path, not protected. For a None webhook that validates a signature in the workflow,
# confirm an unsigned request runs no action. Pick a workflow safe to trigger, and substitute your path.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_WEBHOOK_PATH'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the webhook path on the set -- line above; not probing"; exit 1 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-cred=%{http_code} exit=%{exitcode}\n' -X POST "https://n8n.example.com/webhook/$1"
)
```

## Sources (checked October 2026)

- n8n deployment environment variables (N8N_LISTEN_ADDRESS, N8N_PROTOCOL, N8N_SSL_KEY, N8N_SSL_CERT, defaults): https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment
- n8n security policies (MFA enforcement 2.18.0+, licensing, SSO exception): https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/manage-security-policies
- n8n SSL setup: https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/set-up-ssl
- n8n encryption key (`N8N_ENCRYPTION_KEY`, auto-generated, `~/.n8n`, back it up): https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/set-a-custom-encryption-key
- n8n task runners (external runners, `NODE_FUNCTION_ALLOW_BUILTIN`/`NODE_FUNCTION_ALLOW_EXTERNAL`, `N8N_BLOCK_ENV_ACCESS_IN_NODE`): https://docs.n8n.io/deploy/host-n8n/configure-n8n/set-up-task-runners
- n8n SSRF protection (`N8N_SSRF_PROTECTION_ENABLED`, from 2.12.0): https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection
- n8n reverse-proxy webhook URLs (`N8N_WEBHOOK_URL`, proxy hops, `N8N_SECURE_COOKIE`): https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-webhook-urls-with-reverse-proxy
- n8n public API authentication (`/api/v1` base path, `X-N8N-API-KEY` header): https://docs.n8n.io/connect/n8n-api/authentication
- n8n Webhook node (Authentication options, production and test URLs, HTTP Method): https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- n8n Webhook credentials (Basic, Header, JWT auth): https://docs.n8n.io/integrations/builtin/credentials/webhook/
- n8n `N8N_PORT` default `5678` and `N8N_LISTEN_ADDRESS` default `'::'` (pinned tag n8n@2.40.6): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/index.ts#L164-L171
- n8n auth cookie Secure default, recorded in the 1.32.0 changes (pinned tag n8n@2.40.6): https://raw.githubusercontent.com/n8n-io/n8n/n8n@2.40.6/packages/cli/BREAKING-CHANGES.md
- n8n 2.0 changes, ExecuteCommand and LocalFileTrigger disabled by default (rolling documentation, checked October 2026): https://docs.n8n.io/changelog/v20-breaking-changes
- n8n pinned tag n8n@2.0.0 `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/n8n%402.0.0/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36
- n8n pinned tag n8n@1.123.85 `NODES_EXCLUDE` default excludes none (checked October 2026): https://github.com/n8n-io/n8n/blob/n8n%401.123.85/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31
- n8n@1.123.85 commit-pinned `NODES_EXCLUDE` default excludes none (checked October 2026): https://github.com/n8n-io/n8n/blob/8ea1ccdf82fd040f2568a6255ed663f32f0fc41d/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31
- n8n@2.0.0 commit-pinned `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/a8ecda44f7627630bc8b78cf671405157ad41c4f/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36
- n8n@2.43.8 commit-pinned `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/bf8e523d409b74bceb990a37e9a2dc7ffe1507d7/packages/%40n8n/config/src/configs/nodes.config.ts#L38-L39
- n8n pinned tag n8n@2.0.0-rc.0, the lowest-version 2.x tag, `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/n8n%402.0.0-rc.0/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36
- n8n@2.0.0-rc.0 commit-pinned `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/84148c1774ab85163465dbe062e2e304aa85edac/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36
- n8n pinned tag n8n@1.123.0 `NODES_EXCLUDE` default excludes none (checked October 2026): https://github.com/n8n-io/n8n/blob/n8n%401.123.0/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31
- n8n@1.123.0 commit-pinned `NODES_EXCLUDE` default excludes none (checked October 2026): https://github.com/n8n-io/n8n/blob/6d67db4449db7ab8a5f8d413461ffc46f57d50bb/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31
- n8n@2.45.0 commit-pinned `NODES_EXCLUDE` default excludes Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/blob/7c79fd09a04e256a6b14bf29a40355a73a17d79d/packages/%40n8n/config/src/configs/nodes.config.ts#L38-L39
- n8n commit a4757cf009839a951e8cd5295cd9d549a21f5714 ("chore: Initial V2 changes (#22553)", 2025-12-01) changes the `NODES_EXCLUDE` default from none to Execute Command and Local File Trigger (checked October 2026): https://github.com/n8n-io/n8n/commit/a4757cf009839a951e8cd5295cd9d549a21f5714 and https://github.com/n8n-io/n8n/blob/a4757cf009839a951e8cd5295cd9d549a21f5714/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36
- n8n later `nodes.config.ts` commits through ea8417e29ad6f8b981d9a04b17283d5d77f2b5bb, none changing the `NODES_EXCLUDE` default (checked October 2026): https://github.com/n8n-io/n8n/commit/5ec61a6a1742208bf07e9f717ba2ff4888647d17 and https://github.com/n8n-io/n8n/commit/9e4b4beed92e1df8ca79b9e285efe123e6d4dd31 and https://github.com/n8n-io/n8n/commit/5e376b69edf3eb10dfa7f4a735ddf36a5cb027bf and https://github.com/n8n-io/n8n/commit/ea8417e29ad6f8b981d9a04b17283d5d77f2b5bb
- n8n pinned tag n8n@2.40.6 owner setup handler (`skipAuth`, owner cookie): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/controllers/owner.controller.ts#L22-L29
- n8n pinned tag n8n@2.40.6 default REST endpoint (`rest`): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/configs/endpoints.config.ts#L153-L155
- n8n pinned tag n8n@2.40.6 login controller (`POST /login`): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/controllers/auth.controller.ts#L38-L54
- n8n pinned tag n8n@2.40.6 excluded nodes (`NODES_EXCLUDE`): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/configs/nodes.config.ts#L31-L38
- n8n pinned tag n8n@2.40.6 Execute Command shell spawn: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/ExecuteCommand/ExecuteCommand.node.ts#L42-L48
- n8n pinned tag n8n@2.40.6 workflow `$env` guard and denial: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/workflow/src/workflow-data-proxy-env-provider.ts#L13-L25 and https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/workflow/src/workflow-data-proxy-env-provider.ts#L53-L71
- n8n pinned tag n8n@2.40.6 public API auth registry and handler: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/public-api/index.ts#L253-L275 and https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/public-api/index.ts#L321-L328
- n8n pinned tag n8n@2.40.6 Webhook Basic, Header, JWT refusal branches: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L275-L304 and https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L324-L346 and https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L359-L388
- n8n pinned tag n8n@2.40.6 Webhook authorization error code and message mapping: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/error.ts#L1-L18
- n8n pinned tag n8n@2.40.6 Webhook authorization HTTP response write: https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/Webhook.node.ts#L267-L272
- n8n auth registry result (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/services/auth-strategy.registry.ts#L49-L58
- n8n validator dependency (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/package.json#L212-L212
- n8n public API middleware and error dispatch (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L374-L393
- n8n public API error response (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/public-api-error-response.ts#L11-L19
- n8n validator error classification (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/errors/http-error-classifier.ts#L91-L103
- n8n public API HttpError serialization (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/errors/http-error-serializers.ts#L64-L68
- n8n workflow-version handler, not the workflows list handler (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/workflows.handler.ts#L17-L52
- express-openapi-validator security result selection and error forwarding (pinned v5.5.3): https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L27-L108
- express-openapi-validator handler evaluation and fallback status (pinned v5.5.3): https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L125-L191
- n8n controller ownership and ordering (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L154-L155
- n8n controller activation (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L232-L236
- n8n controller route authentication (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L120-L168
- n8n public controller activation and base-path mount (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L55-L67
- n8n controller route success status and JSON response (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L77-L81 and https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L106-L117
- n8n controller API key scope middleware (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L188-L199
- n8n public controller imports (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/index.ts#L1-L16
- n8n workflows public controller and list route (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L205-L206 and https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L229-L235
- n8n workflows list response body (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L277-L302
- n8n public API spec paths, security schemes and global security (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L79-L159 and https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L167-L185
- n8n generated workflows list spec, scope and responses (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L1-L6 and https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L43-L47 and https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L562-L573
- n8n controller ownership and ordering (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L374-L380
- express-openapi-validator pre-handler check and fallback status (pinned v5.5.3): https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L165-L174
- express-openapi-validator pre-handler check and fallback status (pinned v5.5.3): https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L265-L271
- express-openapi-validator pre-handler check and fallback status (pinned v5.5.3): https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L142-L185
- n8n JS runner native globals (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L258-L278
- n8n JS all-items context and secure/insecure dispatch (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L331-L355
- n8n JS per-item context and secure/insecure dispatch (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L401-L430
- n8n JS data-proxy environment state and empty fallback (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L481-L512
- n8n JS context bindings (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L639-L656
- n8n JS insecure direct execution (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L690-L698
- n8n Python all-items conditional environment clearing and execution (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_executor.py#L310-L332
- n8n Python per-item conditional environment clearing and execution (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_executor.py#L352-L378
- n8n Python environment reader (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/env.py#L5-L19
- n8n Python `N8N_BLOCK_RUNNER_ENV_ACCESS` variable name (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/constants.py#L79-L79
- n8n Python `env_deny` read with default `True` (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/config/task_runner_config.py#L129-L129
- n8n Python `env_deny` passed as `runner_env_deny` (pinned n8n@2.40.6): https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_runner.py#L96-L96
- n8n launcher environment filtering, runtime values and overrides (pinned 1.5.1): https://github.com/n8n-io/task-runner-launcher/blob/871cb76bc35c990f368eaa788f0b4ce7b145e143/internal/env/env.go#L13-L142
- n8n launcher allowed-env and env-overrides fields (pinned 1.5.1): https://github.com/n8n-io/task-runner-launcher/blob/871cb76bc35c990f368eaa788f0b4ce7b145e143/internal/config/config.go#L95-L99


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- server: n8n listener source (n8n@2.40.6)
- runtime: n8n runtime source (n8n@2.40.6)
- policy: n8n environment policy minimum (2.18.0)
- ssrf: n8n SSRF filter minimum (2.12.0)
- v2-default: n8n 2.0 default exclusion source (n8n@2.0.0)
- v1-default: n8n 1.x default exclusion source (n8n@1.123.85)
- docs: n8n documentation (unknown)
- v2-docs: n8n 2.0 breaking changes (unknown)
- validator: express-openapi-validator (v5.5.3)
- v2-later-default: n8n later 2.x default exclusion source (n8n@2.43.8)
- launcher: n8n task-runner launcher (1.5.1)
- v2-first-default: n8n lowest-version 2.x tag default exclusion source (n8n@2.0.0-rc.0)
- v1-first-default: n8n 1.123.0 default exclusion source (n8n@1.123.0)
- v2-change: n8n default exclusion change commit (a4757cf009839a951e8cd5295cd9d549a21f5714)
- v2-later-commits: n8n later nodes config commits (ea8417e29ad6f8b981d9a04b17283d5d77f2b5bb)
- v2-last-tag-default: n8n 2.45.0 default exclusion source (n8n@2.45.0)

Claims (full source mapping in the JSON block below):

- bind-default (REASONED; server): n8n 2.40.6 defaults N8N_LISTEN_ADDRESS to :: and N8N_PORT to 5678, exposing all interfaces.
- protocol-default (REASONED; docs): N8N_PROTOCOL defaults http; private deployment sets listener, port and host explicitly.
- container-bind (REASONED; docs): Host loopback is for a same-host proxy; container loopback blocks sibling/published access, so use a private network without publication or host-loopback 127.0.0.1:5678:5678.
- other-ports (REASONED; docs): Keep Postgres and task-runner broker ports unpublished and publish only the HTTPS proxy.
- public-url (REASONED; docs): Set N8N_PROTOCOL=https and the full N8N_WEBHOOK_URL; WEBHOOK_URL is deprecated from 2.35.0 but still warns and works.
- secure-cookie (REASONED; docs, server): Retain N8N_SECURE_COOKIE=true, its default.
- proxy-hops (REASONED; docs): Set N8N_PROXY_HOPS to the trusted hop count for forwarded client IPs and rate limiting; public webhooks do not require a public editor.
- native-tls (REASONED; docs): N8N_PROTOCOL=https with N8N_SSL_KEY/N8N_SSL_CERT enables native TLS.
- owner (REASONED; runtime): Finish first-run owner setup before publication. The pinned owner setup handler skips authentication and issues an owner session cookie.
- user-mfa (REASONED; docs): Individual users can enable two-factor authentication, subject to version/licence availability.
- mfa-enforcement (REASONED; policy): Enforce MFA through Settings &gt; Security or N8N_MFA_ENFORCED_ENABLED with N8N_SECURITY_POLICY_MANAGED_BY_ENV; env policy requires 2.18.0+ and self-hosted Business/Enterprise.
- sso-mfa (REASONED; docs): Instance MFA enforcement excludes SSO logins; enforce their MFA at the identity provider.
- encryption (REASONED; docs): Stored credentials are encrypted; unset N8N_ENCRYPTION_KEY generates a key under ~/.n8n, not plaintext; losing it makes retained credentials unrecoverable.
- key-custody (REASONED; docs): Set the same encryption key across workers/replicas, back it up separately from the database and exclude it from source and images.
- webhook-auth (REASONED; docs): Webhook None is open; controlled callers use per-node Basic, Header or JWT auth with the matching credential.
- auth-boundaries (REASONED; docs): Editor sessions, /api/v1 with X-N8N-API-KEY and per-node webhook auth are separate boundaries.
- signature (REASONED; docs): A None webhook must validate the provider signature before downstream processing when callers cannot supply native webhook credentials.
- code-execution (REASONED; docs, v2-docs, runtime, v2-default, v1-default, v2-later-default): Code runs JavaScript/Python and Execute Command a shell child of n8n; NODES_EXCLUDE turns Execute Command off by default at 2.40.6, and with Local File Trigger at 2.0.0 and 2.43.8, while 1.123.85 (1.x line) excludes none. The unversioned rolling 2.0 changes page also lists both as disabled by default in 2.0.
- code-execution-introduced (REASONED; v2-change, v2-later-commits, v2-first-default, v1-first-default, v1-default): Commit a4757cf0 (2025-12-01) changed the n8n NODES_EXCLUDE default in nodes.config.ts from none to Execute Command and Local File Trigger; 2.0.0-rc.0, the lowest-version 2.x tag, excludes both, 1.123.0 and 1.123.85 exclude none, and four later nodes.config.ts commits through ea8417e2 keep the default.
- code-execution-tags (REASONED; v1-first-default, v1-default, v2-first-default, v2-last-tag-default): This guide's assessment of n8n nodes.config.ts at each tag, as of October 2026: the NODES_EXCLUDE default is empty at every 1.123.x tag and excludes Execute Command and Local File Trigger at every 2.x tag from 2.0.0-rc.0 through 2.45.0. Releases after 2.45.0 are not covered, and no release was run.
- runners (REASONED; docs): Use hardened external task runners; vendor describes internal mode as insecure by design.
- environment (REASONED; runtime): At n8n 2.40.6, keep workflow `$env` access blocked with `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`; the proxy is blocked unless it is `false`. This guide's assessment is that this guard alone does not establish isolation of every node or Code `process.env`.
- environment-js-context (REASONED; runtime): At n8n 2.40.6, the JS task runner builds a context with module resolution, console, workflow static data, selected native globals, the data proxy, RPC and additional properties. This guide reasons that no direct `process` binding appears in the explicit native list or context; imported modules and injected properties prevent treating that omission as complete `process.env` isolation.
- environment-js-state (REASONED; runtime): At n8n 2.40.6, the JS data proxy receives `envProviderState`; if absent, its fallback is `env: {}`, `isEnvAccessBlocked: false` and `isProcessAvailable: true`. This guide reasons that the fallback avoids using the runner environment for `$env`; the cited consumer does not establish the contents or production of incoming state.
- environment-js-execution (REASONED; runtime): At n8n 2.40.6, JS all-items and per-item execution use `runInContext` in secure mode and `runDirectly` in insecure mode. This guide reasons that the latter, using `new Function` with `with(context)`, can resolve ambient `process.env` unless shadowed; this is not a live demonstration or proof of complete isolation in secure mode.
- environment-python (REASONED; runtime): At n8n 2.40.6, Python all-items and per-item execution clear `os.environ` before user code only if `runner_env_deny` is true; the runner sets it from `N8N_BLOCK_RUNNER_ENV_ACCESS`, read with default `True`, so by default they clear it, and when false, they do not clear the task process environment. This guide did not trace how `read_bool_env` parses the value or establish effective module access.
- environment-python-reader (REASONED; runtime): At n8n 2.40.6, Python `read_env` reads `os.environ` first, otherwise a file named by the corresponding `_FILE` variable, or returns `None`. This guide assesses that this configuration reader does not itself establish which environment values user code can access.
- environment-launcher (REASONED; launcher): Launcher 1.5.1 prepares the runner environment from its own `LANG`, `PATH`, `TZ` and `TERM` plus names in `allowed-env`; `env-overrides` sets values directly. This guide advises keeping secrets out of `allowed-env` and keeping that list narrow, because listed values can enter the runner process environment.
- environment-launcher-runtime (REASONED; launcher): Launcher 1.5.1 sets the task broker URI, health-check enable flag and port, and legacy auto-shutdown and task timeouts. It removes inherited required runtime keys, including the grant token, and ignores their `env-overrides`; other overrides replace prior values, while grant-token insertion is not shown by this preparation function.
- environment-limits (REASONED; runtime, launcher): This guide's assessment is that the cited n8n 2.40.6 runner and launcher 1.5.1 sources describe specific environment controls for external runners, not complete host/container isolation. Internal-mode runners, other nodes, other launcher versions, deployed configuration and complete Code `process.env` isolation remain unestablished.
- js-modules (REASONED; docs): Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden.
- python-modules (REASONED; docs): Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation.
- ssrf (REASONED; ssrf): Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking.
- verify-inventory (REASONED; docs, runtime): Confirm completed owner setup without creating an owner as a probe; the pinned setup handler skips authentication. ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately.
- verify-tls (REASONED; docs): HTTPS reachability tests TLS, not authentication.
- public-controller-order (REASONED; runtime): At n8n 2.40.6, public controllers precede the lazy validator; every controller route gets auth middleware (401 Unauthorized if the auth registry does not authenticate), and GET /workflows then requires API key scope workflow:list (403 Forbidden if no token grant satisfies it). This guide infers a controller can respond before the validator's security check, not skip authentication.
- verify-api (REASONED; docs, runtime, validator): At /api/v1/workflows, compare no X-N8N-API-KEY and a valid key (fixed proxy credentials, key on stdin); on success n8n 2.40.6 returns data and nextCursor JSON (spec: 200). This guide assesses 401 if no auth strategy authenticates a keyless call, or a selected express-openapi-validator 5.5.3 security failure lacks a status; rejection and 200 stay unobserved expectations; proxies can alter status.
- verify-editor (REASONED; runtime): Confirm editor session login at /rest/login separately; the pinned login controller registers POST /login under the default rest endpoint, which is configurable. A protected public API does not prove editor protection.
- verify-webhook (REASONED; docs, runtime): Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; the pinned Webhook handler returns 401 for missing Basic/JWT credentials and 403 for missing Header credentials when node credentials are configured. Verify actions, not status alone.
- verify-signature (REASONED; docs): For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection.

````json
{
  "schema": 1,
  "checked": "2026-10-21",
  "documentation_checked": "2026-10",
  "body_sha256": "fb1d449add17e85932d3b1112c14a06bab23f59128afe17966fcf3803ed55b4d",
  "components": {
    "server": {
      "name": "n8n listener source",
      "basis": "n8n@2.40.6",
      "sources": {
        "sd3ce4e1b39e5": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/index.ts#L164-L171",
        "s1e4d79276a10": "https://raw.githubusercontent.com/n8n-io/n8n/n8n@2.40.6/packages/cli/BREAKING-CHANGES.md"
      }
    },
    "runtime": {
      "name": "n8n runtime source",
      "basis": "n8n@2.40.6",
      "sources": {
        "sc22e435cab62": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/controllers/owner.controller.ts#L22-L29",
        "s3bfd6e00f52b": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/configs/nodes.config.ts#L31-L38",
        "s42b6fad131ec": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/ExecuteCommand/ExecuteCommand.node.ts#L42-L48",
        "se407529f282f": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/workflow/src/workflow-data-proxy-env-provider.ts#L13-L25",
        "sa8c51cda4320": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/workflow/src/workflow-data-proxy-env-provider.ts#L53-L71",
        "sb97647f7fcce": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/controllers/auth.controller.ts#L38-L54",
        "s5d8dc0d1f235": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/configs/endpoints.config.ts#L153-L155",
        "s3036202ca2bb": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/public-api/index.ts#L253-L275",
        "s1f6c80c34ae4": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/cli/src/public-api/index.ts#L321-L328",
        "s475cc9182a7a": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L275-L304",
        "s07bb616d396d": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L324-L346",
        "s4d8fc5553b56": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/utils.ts#L359-L388",
        "s7a5b5df355c6": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/error.ts#L1-L18",
        "s2fc1bd6b7634": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/Webhook.node.ts#L267-L272",
        "s7a685c70d38b": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/services/auth-strategy.registry.ts#L49-L58",
        "s7a5a33c2d969": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/package.json#L212-L212",
        "s5bc5f889e34f": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L374-L393",
        "s3bec46cee679": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/public-api-error-response.ts#L11-L19",
        "sc47bb251d1a8": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/errors/http-error-classifier.ts#L91-L103",
        "s2a7bf000586e": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/errors/http-error-serializers.ts#L64-L68",
        "sb56a3059769a": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/workflows.handler.ts#L17-L52",
        "s36fc02fa718a": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L154-L155",
        "s06f41bd8411f": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L232-L236",
        "sa7664370234c": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L120-L168",
        "s2d9fd6635fbf": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/index.ts#L374-L380",
        "saec4f605977b": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L55-L67",
        "sb0d44f195f2b": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L77-L81",
        "s30e4c954e008": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L106-L117",
        "s9bf67f0a7741": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/public-api-controller.registry.ts#L188-L199",
        "s160b6cfac434": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/index.ts#L1-L16",
        "scba57e29a2e0": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L205-L206",
        "sd20d9418a167": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L229-L235",
        "s0b99491fb492": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/controllers/workflows.public.controller.ts#L277-L302",
        "s64c7fad8e9b8": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L79-L159",
        "seeadaac62b26": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/openapi.yml#L167-L185",
        "sefedd6e89959": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L1-L6",
        "sc2d6d5f9631a": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L43-L47",
        "sb3d5f5fd5d13": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/cli/src/public-api/v1/handlers/workflows/spec/paths/getWorkflows.generated.yml#L562-L573",
        "saa627175e459": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L258-L278",
        "sd15d7071c6bd": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L331-L355",
        "s69054c1789a2": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L401-L430",
        "sdd4f32a1646b": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L481-L512",
        "s873900e97684": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L639-L656",
        "s375af3773710": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts#L690-L698",
        "s3bcd987aa2ae": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_executor.py#L310-L332",
        "se2cd0ce17671": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_executor.py#L352-L378",
        "sb1324fc02bd6": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/env.py#L5-L19",
        "s43c6d04f0116": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/constants.py#L79-L79",
        "sb6ebe4a8cb3f": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/config/task_runner_config.py#L129-L129",
        "se6c792fa6ca0": "https://github.com/n8n-io/n8n/blob/024ee46bdc6d57e5c47ef2c26bcac2b3a9efd827/packages/@n8n/task-runner-python/src/task_runner.py#L96-L96"
      }
    },
    "policy": {
      "name": "n8n environment policy minimum",
      "basis": "2.18.0",
      "sources": {
        "scb2b0578a5a2": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/manage-security-policies"
      }
    },
    "ssrf": {
      "name": "n8n SSRF filter minimum",
      "basis": "2.12.0",
      "sources": {
        "s907260f38eee": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection"
      }
    },
    "v2-default": {
      "name": "n8n 2.0 default exclusion source",
      "basis": "n8n@2.0.0",
      "sources": {
        "s0b6707ff8f67": "https://github.com/n8n-io/n8n/blob/n8n%402.0.0/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36",
        "sed9acc6f59f6": "https://github.com/n8n-io/n8n/blob/a8ecda44f7627630bc8b78cf671405157ad41c4f/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36"
      }
    },
    "v1-default": {
      "name": "n8n 1.x default exclusion source",
      "basis": "n8n@1.123.85",
      "sources": {
        "s10f7d5ae15e5": "https://github.com/n8n-io/n8n/blob/n8n%401.123.85/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31",
        "scd888024007a": "https://github.com/n8n-io/n8n/blob/8ea1ccdf82fd040f2568a6255ed663f32f0fc41d/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31"
      }
    },
    "docs": {
      "name": "n8n documentation",
      "basis": "unknown",
      "sources": {
        "s2f99613ed917": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment",
        "s695f877f7b28": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/set-up-ssl",
        "se8f5861891dc": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/set-a-custom-encryption-key",
        "s290535cad2ea": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/set-up-task-runners",
        "se9dd39628347": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-webhook-urls-with-reverse-proxy",
        "s7ce8bf5b35e8": "https://docs.n8n.io/connect/n8n-api/authentication",
        "sab23639d9b2a": "https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/",
        "sa18a30d563bd": "https://docs.n8n.io/integrations/builtin/credentials/webhook/",
        "scb2b0578a5a2": "https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/manage-security-policies"
      }
    },
    "v2-docs": {
      "name": "n8n 2.0 breaking changes",
      "basis": "unknown",
      "sources": {
        "s994d1a49cf93": "https://docs.n8n.io/changelog/v20-breaking-changes"
      }
    },
    "validator": {
      "name": "express-openapi-validator",
      "basis": "v5.5.3",
      "sources": {
        "s98d84eff0a82": "https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L27-L108",
        "s1cdc721af10e": "https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L125-L191",
        "s80197403fe11": "https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L165-L174",
        "sd316616a548a": "https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L265-L271",
        "s35d0eaba3dad": "https://github.com/cdimascio/express-openapi-validator/blob/5c204614a5ccb04ddc64f68e8a282e8f661dfb47/src/middlewares/openapi.security.ts#L142-L185"
      }
    },
    "v2-later-default": {
      "name": "n8n later 2.x default exclusion source",
      "basis": "n8n@2.43.8",
      "sources": {
        "sa172b5ee013d": "https://github.com/n8n-io/n8n/blob/bf8e523d409b74bceb990a37e9a2dc7ffe1507d7/packages/%40n8n/config/src/configs/nodes.config.ts#L38-L39"
      }
    },
    "launcher": {
      "name": "n8n task-runner launcher",
      "basis": "1.5.1",
      "sources": {
        "s0354dcddb708": "https://github.com/n8n-io/task-runner-launcher/blob/871cb76bc35c990f368eaa788f0b4ce7b145e143/internal/env/env.go#L13-L142",
        "s6a7cebb18624": "https://github.com/n8n-io/task-runner-launcher/blob/871cb76bc35c990f368eaa788f0b4ce7b145e143/internal/config/config.go#L95-L99"
      }
    },
    "v2-first-default": {
      "name": "n8n lowest-version 2.x tag default exclusion source",
      "basis": "n8n@2.0.0-rc.0",
      "sources": {
        "saa97fedeb022": "https://github.com/n8n-io/n8n/blob/n8n%402.0.0-rc.0/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36",
        "sad53656aa702": "https://github.com/n8n-io/n8n/blob/84148c1774ab85163465dbe062e2e304aa85edac/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36"
      }
    },
    "v1-first-default": {
      "name": "n8n 1.123.0 default exclusion source",
      "basis": "n8n@1.123.0",
      "sources": {
        "sb99e9bb32834": "https://github.com/n8n-io/n8n/blob/n8n%401.123.0/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31",
        "s71dd7eaad4e5": "https://github.com/n8n-io/n8n/blob/6d67db4449db7ab8a5f8d413461ffc46f57d50bb/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31"
      }
    },
    "v2-change": {
      "name": "n8n default exclusion change commit",
      "basis": "a4757cf009839a951e8cd5295cd9d549a21f5714",
      "sources": {
        "sd5273e65f9ae": "https://github.com/n8n-io/n8n/commit/a4757cf009839a951e8cd5295cd9d549a21f5714",
        "s32c46ff8799b": "https://github.com/n8n-io/n8n/blob/a4757cf009839a951e8cd5295cd9d549a21f5714/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36"
      }
    },
    "v2-later-commits": {
      "name": "n8n later nodes config commits",
      "basis": "ea8417e29ad6f8b981d9a04b17283d5d77f2b5bb",
      "sources": {
        "s5781e44679c8": "https://github.com/n8n-io/n8n/commit/5ec61a6a1742208bf07e9f717ba2ff4888647d17",
        "s879c80d47bb5": "https://github.com/n8n-io/n8n/commit/9e4b4beed92e1df8ca79b9e285efe123e6d4dd31",
        "s031c835d5cd3": "https://github.com/n8n-io/n8n/commit/5e376b69edf3eb10dfa7f4a735ddf36a5cb027bf",
        "se440fd8c8db4": "https://github.com/n8n-io/n8n/commit/ea8417e29ad6f8b981d9a04b17283d5d77f2b5bb"
      }
    },
    "v2-last-tag-default": {
      "name": "n8n 2.45.0 default exclusion source",
      "basis": "n8n@2.45.0",
      "sources": {
        "s0f6265beb7d9": "https://github.com/n8n-io/n8n/blob/7c79fd09a04e256a6b14bf29a40355a73a17d79d/packages/%40n8n/config/src/configs/nodes.config.ts#L38-L39"
      }
    }
  },
  "claims": {
    "bind-default": {"text": "n8n 2.40.6 defaults N8N_LISTEN_ADDRESS to :: and N8N_PORT to 5678, exposing all interfaces.", "components": ["server"], "sources": ["server:sd3ce4e1b39e5"], "status": "REASONED"},
    "protocol-default": {"text": "N8N_PROTOCOL defaults http; private deployment sets listener, port and host explicitly.", "components": ["docs"], "sources": ["docs:s2f99613ed917"], "status": "REASONED"},
    "container-bind": {"text": "Host loopback is for a same-host proxy; container loopback blocks sibling/published access, so use a private network without publication or host-loopback 127.0.0.1:5678:5678.", "components": ["docs"], "sources": ["docs:s2f99613ed917", "docs:s695f877f7b28"], "status": "REASONED"},
    "other-ports": {"text": "Keep Postgres and task-runner broker ports unpublished and publish only the HTTPS proxy.", "components": ["docs"], "sources": ["docs:s695f877f7b28", "docs:s290535cad2ea"], "status": "REASONED"},
    "public-url": {"text": "Set N8N_PROTOCOL=https and the full N8N_WEBHOOK_URL; WEBHOOK_URL is deprecated from 2.35.0 but still warns and works.", "components": ["docs"], "sources": ["docs:se9dd39628347"], "status": "REASONED"},
    "secure-cookie": {"text": "Retain N8N_SECURE_COOKIE=true, its default.", "components": ["docs", "server"], "sources": ["docs:se9dd39628347", "server:s1e4d79276a10"], "status": "REASONED"},
    "proxy-hops": {"text": "Set N8N_PROXY_HOPS to the trusted hop count for forwarded client IPs and rate limiting; public webhooks do not require a public editor.", "components": ["docs"], "sources": ["docs:se9dd39628347"], "status": "REASONED"},
    "native-tls": {"text": "N8N_PROTOCOL=https with N8N_SSL_KEY/N8N_SSL_CERT enables native TLS.", "components": ["docs"], "sources": ["docs:s2f99613ed917", "docs:s695f877f7b28"], "status": "REASONED"},
    "owner": {"text": "Finish first-run owner setup before publication. The pinned owner setup handler skips authentication and issues an owner session cookie.", "components": ["runtime"], "sources": ["runtime:sc22e435cab62"], "status": "REASONED"},
    "user-mfa": {"text": "Individual users can enable two-factor authentication, subject to version/licence availability.", "components": ["docs"], "sources": ["docs:scb2b0578a5a2"], "status": "REASONED"},
    "mfa-enforcement": {"text": "Enforce MFA through Settings > Security or N8N_MFA_ENFORCED_ENABLED with N8N_SECURITY_POLICY_MANAGED_BY_ENV; env policy requires 2.18.0+ and self-hosted Business/Enterprise.", "components": ["policy"], "sources": ["policy:scb2b0578a5a2"], "status": "REASONED"},
    "sso-mfa": {"text": "Instance MFA enforcement excludes SSO logins; enforce their MFA at the identity provider.", "components": ["docs"], "sources": ["docs:scb2b0578a5a2"], "status": "REASONED"},
    "encryption": {"text": "Stored credentials are encrypted; unset N8N_ENCRYPTION_KEY generates a key under ~/.n8n, not plaintext; losing it makes retained credentials unrecoverable.", "components": ["docs"], "sources": ["docs:se8f5861891dc"], "status": "REASONED"},
    "key-custody": {"text": "Set the same encryption key across workers/replicas, back it up separately from the database and exclude it from source and images.", "components": ["docs"], "sources": ["docs:se8f5861891dc"], "status": "REASONED"},
    "webhook-auth": {"text": "Webhook None is open; controlled callers use per-node Basic, Header or JWT auth with the matching credential.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "auth-boundaries": {"text": "Editor sessions, /api/v1 with X-N8N-API-KEY and per-node webhook auth are separate boundaries.", "components": ["docs"], "sources": ["docs:s7ce8bf5b35e8", "docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "signature": {"text": "A None webhook must validate the provider signature before downstream processing when callers cannot supply native webhook credentials.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "code-execution": {"text": "Code runs JavaScript/Python and Execute Command a shell child of n8n; NODES_EXCLUDE turns Execute Command off by default at 2.40.6, and with Local File Trigger at 2.0.0 and 2.43.8, while 1.123.85 (1.x line) excludes none. The unversioned rolling 2.0 changes page also lists both as disabled by default in 2.0.", "components": ["docs", "v2-docs", "runtime", "v2-default", "v1-default", "v2-later-default"], "sources": ["docs:s290535cad2ea", "v2-docs:s994d1a49cf93", "runtime:s42b6fad131ec", "runtime:s3bfd6e00f52b", "v2-default:s0b6707ff8f67", "v1-default:s10f7d5ae15e5", "v1-default:scd888024007a", "v2-default:sed9acc6f59f6", "v2-later-default:sa172b5ee013d"], "status": "REASONED"},
    "code-execution-introduced": {"text": "Commit a4757cf0 (2025-12-01) changed the n8n NODES_EXCLUDE default in nodes.config.ts from none to Execute Command and Local File Trigger; 2.0.0-rc.0, the lowest-version 2.x tag, excludes both, 1.123.0 and 1.123.85 exclude none, and four later nodes.config.ts commits through ea8417e2 keep the default.", "components": ["v2-change", "v2-later-commits", "v2-first-default", "v1-first-default", "v1-default"], "sources": ["v2-change:sd5273e65f9ae", "v2-change:s32c46ff8799b", "v2-later-commits:s5781e44679c8", "v2-later-commits:s879c80d47bb5", "v2-later-commits:s031c835d5cd3", "v2-later-commits:se440fd8c8db4", "v2-first-default:saa97fedeb022", "v2-first-default:sad53656aa702", "v1-first-default:sb99e9bb32834", "v1-first-default:s71dd7eaad4e5", "v1-default:s10f7d5ae15e5", "v1-default:scd888024007a"], "status": "REASONED"},
    "code-execution-tags": {"text": "This guide's assessment of n8n nodes.config.ts at each tag, as of October 2026: the NODES_EXCLUDE default is empty at every 1.123.x tag and excludes Execute Command and Local File Trigger at every 2.x tag from 2.0.0-rc.0 through 2.45.0. Releases after 2.45.0 are not covered, and no release was run.", "components": ["v1-first-default", "v1-default", "v2-first-default", "v2-last-tag-default"], "sources": ["v1-first-default:sb99e9bb32834", "v1-first-default:s71dd7eaad4e5", "v1-default:s10f7d5ae15e5", "v1-default:scd888024007a", "v2-first-default:saa97fedeb022", "v2-first-default:sad53656aa702", "v2-last-tag-default:s0f6265beb7d9"], "status": "REASONED"},
    "runners": {"text": "Use hardened external task runners; vendor describes internal mode as insecure by design.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "environment": {"text": "At n8n 2.40.6, keep workflow `$env` access blocked with `N8N_BLOCK_ENV_ACCESS_IN_NODE=true`; the proxy is blocked unless it is `false`. This guide's assessment is that this guard alone does not establish isolation of every node or Code `process.env`.", "components": ["runtime"], "sources": ["runtime:se407529f282f", "runtime:sa8c51cda4320"], "status": "REASONED"},
    "environment-js-context": {"text": "At n8n 2.40.6, the JS task runner builds a context with module resolution, console, workflow static data, selected native globals, the data proxy, RPC and additional properties. This guide reasons that no direct `process` binding appears in the explicit native list or context; imported modules and injected properties prevent treating that omission as complete `process.env` isolation.", "components": ["runtime"], "sources": ["runtime:saa627175e459", "runtime:s873900e97684"], "status": "REASONED"},
    "environment-js-state": {"text": "At n8n 2.40.6, the JS data proxy receives `envProviderState`; if absent, its fallback is `env: {}`, `isEnvAccessBlocked: false` and `isProcessAvailable: true`. This guide reasons that the fallback avoids using the runner environment for `$env`; the cited consumer does not establish the contents or production of incoming state.", "components": ["runtime"], "sources": ["runtime:sdd4f32a1646b"], "status": "REASONED"},
    "environment-js-execution": {"text": "At n8n 2.40.6, JS all-items and per-item execution use `runInContext` in secure mode and `runDirectly` in insecure mode. This guide reasons that the latter, using `new Function` with `with(context)`, can resolve ambient `process.env` unless shadowed; this is not a live demonstration or proof of complete isolation in secure mode.", "components": ["runtime"], "sources": ["runtime:sd15d7071c6bd", "runtime:s69054c1789a2", "runtime:s375af3773710", "runtime:s873900e97684"], "status": "REASONED"},
    "environment-python": {"text": "At n8n 2.40.6, Python all-items and per-item execution clear `os.environ` before user code only if `runner_env_deny` is true; the runner sets it from `N8N_BLOCK_RUNNER_ENV_ACCESS`, read with default `True`, so by default they clear it, and when false, they do not clear the task process environment. This guide did not trace how `read_bool_env` parses the value or establish effective module access.", "components": ["runtime"], "sources": ["runtime:s3bcd987aa2ae", "runtime:se2cd0ce17671", "runtime:s43c6d04f0116", "runtime:sb6ebe4a8cb3f", "runtime:se6c792fa6ca0"], "status": "REASONED"},
    "environment-python-reader": {"text": "At n8n 2.40.6, Python `read_env` reads `os.environ` first, otherwise a file named by the corresponding `_FILE` variable, or returns `None`. This guide assesses that this configuration reader does not itself establish which environment values user code can access.", "components": ["runtime"], "sources": ["runtime:sb1324fc02bd6"], "status": "REASONED"},
    "environment-launcher": {"text": "Launcher 1.5.1 prepares the runner environment from its own `LANG`, `PATH`, `TZ` and `TERM` plus names in `allowed-env`; `env-overrides` sets values directly. This guide advises keeping secrets out of `allowed-env` and keeping that list narrow, because listed values can enter the runner process environment.", "components": ["launcher"], "sources": ["launcher:s0354dcddb708", "launcher:s6a7cebb18624"], "status": "REASONED"},
    "environment-launcher-runtime": {"text": "Launcher 1.5.1 sets the task broker URI, health-check enable flag and port, and legacy auto-shutdown and task timeouts. It removes inherited required runtime keys, including the grant token, and ignores their `env-overrides`; other overrides replace prior values, while grant-token insertion is not shown by this preparation function.", "components": ["launcher"], "sources": ["launcher:s0354dcddb708"], "status": "REASONED"},
    "environment-limits": {"text": "This guide's assessment is that the cited n8n 2.40.6 runner and launcher 1.5.1 sources describe specific environment controls for external runners, not complete host/container isolation. Internal-mode runners, other nodes, other launcher versions, deployed configuration and complete Code `process.env` isolation remain unestablished.", "components": ["runtime", "launcher"], "sources": ["runtime:saa627175e459", "runtime:sdd4f32a1646b", "runtime:s873900e97684", "runtime:s375af3773710", "runtime:s3bcd987aa2ae", "runtime:se2cd0ce17671", "launcher:s0354dcddb708"], "status": "REASONED"},
    "js-modules": {"text": "Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "python-modules": {"text": "Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "ssrf": {"text": "Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking.", "components": ["ssrf"], "sources": ["ssrf:s907260f38eee"], "status": "REASONED"},
    "verify-inventory": {"text": "Confirm completed owner setup without creating an owner as a probe; the pinned setup handler skips authentication. ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately.", "components": ["docs", "runtime"], "sources": ["docs:s2f99613ed917", "docs:s290535cad2ea", "runtime:sc22e435cab62"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS reachability tests TLS, not authentication.", "components": ["docs"], "sources": ["docs:s695f877f7b28"], "status": "REASONED", "verify": [1]},
    "public-controller-order": {"text": "At n8n 2.40.6, public controllers precede the lazy validator; every controller route gets auth middleware (401 Unauthorized if the auth registry does not authenticate), and GET /workflows then requires API key scope workflow:list (403 Forbidden if no token grant satisfies it). This guide infers a controller can respond before the validator's security check, not skip authentication.", "components": ["runtime"], "sources": ["runtime:s06f41bd8411f", "runtime:s2d9fd6635fbf", "runtime:sa7664370234c", "runtime:saec4f605977b", "runtime:s9bf67f0a7741", "runtime:s160b6cfac434", "runtime:scba57e29a2e0", "runtime:sd20d9418a167"], "status": "REASONED"},
    "verify-api": {"text": "At /api/v1/workflows, compare no X-N8N-API-KEY and a valid key (fixed proxy credentials, key on stdin); on success n8n 2.40.6 returns data and nextCursor JSON (spec: 200). This guide assesses 401 if no auth strategy authenticates a keyless call, or a selected express-openapi-validator 5.5.3 security failure lacks a status; rejection and 200 stay unobserved expectations; proxies can alter status.", "components": ["docs", "runtime", "validator"], "sources": ["docs:s7ce8bf5b35e8", "runtime:s3036202ca2bb", "runtime:s1f6c80c34ae4", "runtime:s7a685c70d38b", "runtime:s7a5a33c2d969", "runtime:s5bc5f889e34f", "runtime:s3bec46cee679", "runtime:sc47bb251d1a8", "runtime:s2a7bf000586e", "runtime:sb56a3059769a", "validator:s98d84eff0a82", "validator:s1cdc721af10e", "runtime:s36fc02fa718a", "runtime:s2d9fd6635fbf", "validator:s80197403fe11", "validator:sd316616a548a", "validator:s35d0eaba3dad", "runtime:sa7664370234c", "runtime:sb0d44f195f2b", "runtime:s30e4c954e008", "runtime:s0b99491fb492", "runtime:s64c7fad8e9b8", "runtime:seeadaac62b26", "runtime:sefedd6e89959", "runtime:sc2d6d5f9631a", "runtime:sb3d5f5fd5d13"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "Confirm editor session login at /rest/login separately; the pinned login controller registers POST /login under the default rest endpoint, which is configurable. A protected public API does not prove editor protection.", "components": ["runtime"], "sources": ["runtime:sb97647f7fcce", "runtime:s5d8dc0d1f235"], "status": "REASONED", "verify": [1]},
    "verify-webhook": {"text": "Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; the pinned Webhook handler returns 401 for missing Basic/JWT credentials and 403 for missing Header credentials when node credentials are configured. Verify actions, not status alone.", "components": ["docs", "runtime"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd", "runtime:s475cc9182a7a", "runtime:s07bb616d396d", "runtime:s4d8fc5553b56", "runtime:s7a5b5df355c6", "runtime:s2fc1bd6b7634"], "status": "REASONED", "verify": [1]},
    "verify-signature": {"text": "For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
