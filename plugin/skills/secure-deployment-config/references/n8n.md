# n8n: binding, TLS, and MFA

n8n includes user management (complete the owner setup on first run), but its network defaults deserve attention: `N8N_LISTEN_ADDRESS` defaults to `::`, which listens on **all interfaces**, on port `5678` over plain HTTP.

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

- Finish the owner-account setup immediately after first start; an unclaimed n8n instance is open to whoever reaches it first.
- Individual users can enable two-factor authentication on their accounts (verify availability for your version and licence).
- Instance-wide enforcement exists under **Settings > Security** ("Enforce two-factor authentication"), or via `N8N_MFA_ENFORCED_ENABLED=true` with `N8N_SECURITY_POLICY_MANAGED_BY_ENV=true` (the environment-managed policy is available from n8n 2.18.0, so confirm your version and that enforcement actually takes effect); per the n8n docs this enforcement requires a Business or Enterprise licence on self-hosted instances, and it does not apply to SSO logins (enforce MFA at the identity provider for those; [mfa.md](mfa.md)).
- Credentials stored in n8n (API keys for the services your workflows touch) make the instance a secrets vault; treat access to it accordingly ([secrets.md](secrets.md)). Those credentials are encrypted at rest with `N8N_ENCRYPTION_KEY`: leaving it unset does NOT mean plaintext (n8n generates a random key on first launch and saves it under `~/.n8n`), but losing that key while keeping the database makes every stored credential unrecoverable, and committing it hands the decryption secret to anyone who reads the repo. Set it explicitly, keep the same value across every worker/replica, back it up separately from the database, and keep it out of source control and images ([secrets.md](secrets.md)).

## 4. Webhook authentication

- A Webhook node left on **None** answers anyone who reaches its URL. For a webhook whose caller you control, set the node **Authentication** to **Basic auth**, **Header auth**, or **JWT auth** and attach the matching Webhook credential.
- Webhook authentication is configured per node and is separate from the instance login and the public API key (`X-N8N-API-KEY`). Hardening the editor or `/api/v1` does nothing for webhook endpoints, so audit every Webhook node individually.
- Where a third party must call the webhook and cannot present your credential, **None** is unavoidable at the node, so the workflow itself must authenticate the request: validate the provider's signature (for example an HMAC header) in the first node after the Webhook trigger and reject a missing or wrong signature before any further processing. A **None** webhook with no such check is open.

## 5. Code-node isolation and outbound requests

- Workflow editors can run code: the **Code** node executes JavaScript/Python and the **Execute Command** node runs shell commands (under Docker, inside the n8n container). Execute Command is disabled by default from n8n 2.0; leave it off unless a workflow truly needs it. Run code on hardened EXTERNAL task runners rather than the internal mode, which the vendor calls insecure by design, and keep environment access blocked (`N8N_BLOCK_ENV_ACCESS_IN_NODE=true`, so a Code node cannot read the host/container environment, including `N8N_ENCRYPTION_KEY`). Allow only the modules a workflow needs, narrowly, and set the allowlist where the RUNNER reads it, not just on the main n8n container (whose values the external launcher overrides): for the JavaScript runner, `NODE_FUNCTION_ALLOW_BUILTIN` and `NODE_FUNCTION_ALLOW_EXTERNAL` under `env-overrides` in the launcher's `/etc/n8n-task-runners.json`; for the Python runner, `N8N_RUNNERS_STDLIB_ALLOW` and `N8N_RUNNERS_EXTERNAL_ALLOW`. An unset-then-`*` allowlist gives arbitrary module access. Because these defaults have shifted across versions and one vendor table is stale, set each value explicitly and confirm it on your installed version.
- Outbound requests are a trust boundary too: a webhook or the **HTTP Request** node can be steered at internal services or the cloud metadata endpoint (SSRF). Enable n8n's own SSRF filter where available (`N8N_SSRF_PROTECTION_ENABLED=true`, from n8n 2.12.0) AND restrict the workload's egress so a request cannot reach your internal network or `169.254.169.254` ([egress-metadata.md](egress-metadata.md)); the app-level filter supplements a network control and does not contain arbitrary code- or command-node networking.

## 6. Verify

```bash
# Owner setup must be COMPLETE before the instance is public: an unclaimed n8n hands admin to whoever
# reaches it first. Confirm the owner exists (the first-run setup wizard no longer appears); do NOT POST
# owner-creation data to a live instance as a "test".
ss -tlnp   # a listener inventory in THIS namespace, not a firewall/NAT check: n8n on 127.0.0.1 (or its
           # private container network), with the Postgres and task-runner ports NOT published. Loopback
           # can be 127.0.0.1 and/or ::1; also probe the real public IPv4/IPv6 path from another host.
# TLS reachability (proves TLS, not authentication):
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null \
  -w 'tls=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://n8n.example.com/
# Public API auth, matched pair against the same URL: without the key n8n returns 401, with a valid key
# it returns the workflow JSON (the positive control). The key is fed on stdin (-H @-), so it stays out
# of curl's argv; the one on the set -- line still enters shell history, so use a short-lived key and clear it.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_N8N_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the API key on the set -- line above; not probing"; exit 1 ;; esac
  u=https://n8n.example.com/api/v1/workflows
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-key=%{http_code} exit=%{exitcode}\n' "$u"
  printf 'X-N8N-API-KEY: %s\n' "$1" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\nwith-key=%{http_code} exit=%{exitcode}\n' -H @- "$u"
)
# no-key => 401 from n8n (if a fronting proxy also 401s, hold its credential constant and vary only the
# n8n key); with-key => 200 and the workflow JSON. The editor UI uses a SEPARATE session login
# (/rest/login), so also confirm the editor is not reachable unauthenticated, not just the public API.
# Webhook auth: the api/v1 check says NOTHING about webhooks. Test each PRODUCTION webhook (prefix
# /webhook/, never /webhook-test/) with the method the node expects and a valid payload, three ways: no
# credential, a WRONG credential, and the valid one. Basic/JWT node auth answers a missing credential
# 401, Header auth 403; the valid call must perform the expected action and the missing/wrong calls must
# not. A 200 alone is not proof (a workflow can respond 200 without acting); a 404 means inactive/wrong
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

## Sources (checked September 2026)

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
- n8n `N8N_LISTEN_ADDRESS` default `'::'` (pinned tag n8n@2.40.6): https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/index.ts#L169-L171
