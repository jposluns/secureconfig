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

Written against n8n listener source n8n@2.40.6, n8n runtime source n8n@2.40.6, n8n environment policy minimum 2.18.0, n8n SSRF filter minimum 2.12.0, n8n 2.0 default exclusion source n8n@2.0.0, and n8n 1.x default exclusion source n8n@1.123.85; 2 further sources carry no recorded version. Metadata reviewed 2026-10-17; documentation checked October 2026. The guide records 29 claims, all reasoned from cited sources.

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

- Workflow editors can run code: the **Code** node executes JavaScript/Python and the **Execute Command** node runs the command through a shell in a child process of the n8n process executing the node. At n8n 2.40.6 and 2.0.0, `NODES_EXCLUDE` disables Execute Command by default (at 2.0.0, Local File Trigger as well); at n8n 1.123.85 on the 1.x line, it excludes none. This guide infers a 2.0 default boundary from the pinned snapshots; the rolling 2.0 changes page, which is unversioned, dates this default to n8n 2.0, and the first introducing release is unverified. Leave it off unless a workflow truly needs it. Run code on hardened EXTERNAL task runners rather than the internal mode, which the vendor calls insecure by design, and keep workflow `$env` access blocked (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`; at n8n 2.40.6 the `$env` proxy is blocked unless the variable is set to `false`). This guard alone does not establish isolation of every node or Code `process.env`. Allow only the modules a workflow needs, narrowly, and set the allowlist where the RUNNER reads it, not just on the main n8n container (whose values the external launcher overrides): for the JavaScript runner, `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL` under `env-overrides` in the launcher's `/etc/n8n-task-runners.json`; for the Python runner, `N8N_RUNNERS_STDLIB_ALLOW` and `N8N_RUNNERS_EXTERNAL_ALLOW`. An unset-then-`*` allowlist gives arbitrary module access. Because these defaults have shifted across versions and one vendor table is stale, set each value explicitly and confirm it on your installed version.
- Outbound requests are a trust boundary too: a webhook or the **HTTP Request** node can be steered at internal services or the cloud metadata endpoint (SSRF). Enable n8n's own SSRF filter where available (`N8N_SSRF_PROTECTION_ENABLED=true`, from n8n 2.12.0) AND restrict the workload's egress so a request cannot reach your internal network or `169.254.169.254` ([egress-metadata.md](egress-metadata.md)); the app-level filter supplements a network control and does not contain arbitrary code- or command-node networking.

## 6. Verify

```bash
# REASONED: listener, TLS, API and webhook comparisons have no recorded n8n run; no live n8n deployment is available in this read-only review. Expected API status outcomes require a live check; pinned source establishes public API authentication and Webhook refusal codes.
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
# no-key => rejected by n8n; check the observed status (a fronting proxy can also 401, so hold its
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
- code-execution (REASONED; docs, v2-docs, runtime, v2-default, v1-default): Code executes JavaScript/Python; Execute Command runs the command through a shell in a child process of the n8n process executing the node and is excluded by default at n8n 2.40.6. The pinned n8n 2.0.0 default excludes Execute Command and Local File Trigger; the pinned 1.x line at n8n 1.123.85 excludes none. This guide infers a 2.0 default boundary from those snapshots; the rolling 2.0 changes page dates the default to 2.0. Source gap: the rolling 2.0 changes page is unversioned and the first introducing release is unverified.
- runners (REASONED; docs): Use hardened external task runners; vendor describes internal mode as insecure by design.
- environment (REASONED; runtime): N8N_BLOCK_ENV_ACCESS_IN_NODE blocks the workflow $env data proxy unless set to false; this source does not establish isolation of every node or Code process.env.
- js-modules (REASONED; docs): Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden.
- python-modules (REASONED; docs): Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation.
- ssrf (REASONED; ssrf): Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking.
- verify-inventory (REASONED; docs, runtime): Confirm completed owner setup without creating an owner as a probe; the pinned setup handler skips authentication. ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately.
- verify-tls (REASONED; docs): HTTPS reachability tests TLS, not authentication.
- verify-api (REASONED; docs, runtime): At the same /api/v1/workflows URL, test without and with X-N8N-API-KEY; n8n authenticates the public API through its auth registry. Treat 401 without a key and 200 workflow JSON with a valid key as expected results to verify, not sourced native status guarantees; retain proxy credentials and feed the key on stdin.
- verify-editor (REASONED; runtime): Confirm editor session login at /rest/login separately; the pinned login controller registers POST /login under the default rest endpoint, which is configurable. A protected public API does not prove editor protection.
- verify-webhook (REASONED; docs, runtime): Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; the pinned Webhook handler returns 401 for missing Basic/JWT credentials and 403 for missing Header credentials when node credentials are configured. Verify actions, not status alone.
- verify-signature (REASONED; docs): For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection.

````json
{
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-10",
  "body_sha256": "b2a8d012fa5a0129e243d83f2e6d5421340f05ecb83225898b1bb9b2e9132961",
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
        "s2fc1bd6b7634": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/nodes-base/nodes/Webhook/Webhook.node.ts#L267-L272"
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
        "s0b6707ff8f67": "https://github.com/n8n-io/n8n/blob/n8n%402.0.0/packages/%40n8n/config/src/configs/nodes.config.ts#L35-L36"
      }
    },
    "v1-default": {
      "name": "n8n 1.x default exclusion source",
      "basis": "n8n@1.123.85",
      "sources": {
        "s10f7d5ae15e5": "https://github.com/n8n-io/n8n/blob/n8n%401.123.85/packages/%40n8n/config/src/configs/nodes.config.ts#L30-L31"
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
    "code-execution": {"text": "Code executes JavaScript/Python; Execute Command runs the command through a shell in a child process of the n8n process executing the node and is excluded by default at n8n 2.40.6. The pinned n8n 2.0.0 default excludes Execute Command and Local File Trigger; the pinned 1.x line at n8n 1.123.85 excludes none. This guide infers a 2.0 default boundary from those snapshots; the rolling 2.0 changes page dates the default to 2.0. Source gap: the rolling 2.0 changes page is unversioned and the first introducing release is unverified.", "components": ["docs", "v2-docs", "runtime", "v2-default", "v1-default"], "sources": ["docs:s290535cad2ea", "v2-docs:s994d1a49cf93", "runtime:s42b6fad131ec", "runtime:s3bfd6e00f52b", "v2-default:s0b6707ff8f67", "v1-default:s10f7d5ae15e5"], "status": "REASONED"},
    "runners": {"text": "Use hardened external task runners; vendor describes internal mode as insecure by design.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "environment": {"text": "N8N_BLOCK_ENV_ACCESS_IN_NODE blocks the workflow $env data proxy unless set to false; this source does not establish isolation of every node or Code process.env.", "components": ["runtime"], "sources": ["runtime:se407529f282f", "runtime:sa8c51cda4320"], "status": "REASONED"},
    "js-modules": {"text": "Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "python-modules": {"text": "Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "ssrf": {"text": "Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking.", "components": ["ssrf"], "sources": ["ssrf:s907260f38eee"], "status": "REASONED"},
    "verify-inventory": {"text": "Confirm completed owner setup without creating an owner as a probe; the pinned setup handler skips authentication. ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately.", "components": ["docs", "runtime"], "sources": ["docs:s2f99613ed917", "docs:s290535cad2ea", "runtime:sc22e435cab62"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS reachability tests TLS, not authentication.", "components": ["docs"], "sources": ["docs:s695f877f7b28"], "status": "REASONED", "verify": [1]},
    "verify-api": {"text": "At the same /api/v1/workflows URL, test without and with X-N8N-API-KEY; n8n authenticates the public API through its auth registry. Treat 401 without a key and 200 workflow JSON with a valid key as expected results to verify, not sourced native status guarantees; retain proxy credentials and feed the key on stdin.", "components": ["docs", "runtime"], "sources": ["docs:s7ce8bf5b35e8", "runtime:s3036202ca2bb", "runtime:s1f6c80c34ae4"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "Confirm editor session login at /rest/login separately; the pinned login controller registers POST /login under the default rest endpoint, which is configurable. A protected public API does not prove editor protection.", "components": ["runtime"], "sources": ["runtime:sb97647f7fcce", "runtime:s5d8dc0d1f235"], "status": "REASONED", "verify": [1]},
    "verify-webhook": {"text": "Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; the pinned Webhook handler returns 401 for missing Basic/JWT credentials and 403 for missing Header credentials when node credentials are configured. Verify actions, not status alone.", "components": ["docs", "runtime"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd", "runtime:s475cc9182a7a", "runtime:s07bb616d396d", "runtime:s4d8fc5553b56", "runtime:s7a5b5df355c6", "runtime:s2fc1bd6b7634"], "status": "REASONED", "verify": [1]},
    "verify-signature": {"text": "For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
