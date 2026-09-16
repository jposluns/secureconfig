# n8n: binding, TLS, and MFA

n8n includes user management (complete the owner setup on first run), but its network defaults deserve attention: `N8N_LISTEN_ADDRESS` defaults to `::`, which listens on **all interfaces**, on port `5678` over plain HTTP.

## 1. Bind privately

Behind a reverse proxy or tunnel (the recommended layout):

```
N8N_LISTEN_ADDRESS=127.0.0.1
N8N_PORT=5678
N8N_HOST=n8n.example.com
```

Publish only the proxy per [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or use [cloudflare.md](cloudflare.md)/[tailscale.md](tailscale.md). Webhook endpoints are meant to be reachable by external services; that is no reason for the editor UI to be.

## 2. Or terminate TLS in n8n itself

```
N8N_PROTOCOL=https        # default is http
N8N_SSL_KEY=/path/to/privkey.pem
N8N_SSL_CERT=/path/to/fullchain.pem
```

## 3. Accounts and MFA

- Finish the owner-account setup immediately after first start; an unclaimed n8n instance is open to whoever reaches it first.
- Individual users can enable two-factor authentication on their accounts (verify availability for your version and licence).
- Instance-wide enforcement exists under **Settings > Security** ("Enforce two-factor authentication"), or via `N8N_MFA_ENFORCED_ENABLED=true` with `N8N_SECURITY_POLICY_MANAGED_BY_ENV=true`; per the n8n docs this enforcement requires a Business or Enterprise licence on self-hosted instances, and it does not apply to SSO logins (enforce MFA at the identity provider for those; [mfa.md](mfa.md)).
- Credentials stored in n8n (API keys for the services your workflows touch) make the instance a secrets vault; treat access to it accordingly ([secrets.md](secrets.md)).

## 4. Webhook authentication

- A Webhook node left on **None** answers anyone who reaches its URL. For a webhook whose caller you control, set the node **Authentication** to **Basic auth**, **Header auth**, or **JWT auth** and attach the matching Webhook credential.
- Webhook authentication is configured per node and is separate from the instance login and the public API key (`X-N8N-API-KEY`). Hardening the editor or `/api/v1` does nothing for webhook endpoints, so audit every Webhook node individually.
- Where a third party must call the webhook and cannot present your credential, **None** is unavoidable at the node, so the workflow itself must authenticate the request: validate the provider's signature (for example an HMAC header) in the first node after the Webhook trigger and reject a missing or wrong signature before any further processing. A **None** webhook with no such check is open.

## 5. Verify

```bash
ss -tlnp   # read every listener; 127.0.0.1, not :: or 0.0.0.0
curl -q -sI https://n8n.example.com/       # TLS
curl -q -s -o /dev/null -w '%{http_code}\n' https://n8n.example.com/api/v1/workflows
                                        # 401 without an `X-N8N-API-KEY` header. Use a request that returns a body,
                                        # not `-I`: a HEAD response carries none, so it cannot tell a login page
                                        # from the editor
# webhook auth: the api/v1 check above does NOT prove a webhook is protected. Test a known production
# webhook with the method the node expects (POST shown); n8n shows the production URL in the node panel,
# with the default prefix /webhook/ (test uses /webhook-test/). Pick a workflow safe to trigger if the
# auth is misconfigured, and substitute your real path for REPLACE_WITH_WEBHOOK_PATH.
curl -q -g -s -o /dev/null -w '%{http_code}\n' -X POST "https://n8n.example.com/webhook/REPLACE_WITH_WEBHOOK_PATH"
                                        # node-level auth (Basic, Header, JWT): expect 401 or 403 with no
                                        # credential; 200 means the webhook is open; 404 means the workflow is
                                        # inactive, the method does not match, or the path is wrong, not that it
                                        # is protected. A
                                        # webhook that instead validates a signature in the workflow sets its own
                                        # response, so confirm there that an unsigned request runs no action.
                                        # Use the production prefix, never /webhook-test/
```

## Sources (checked September 2026)

- n8n deployment environment variables (N8N_LISTEN_ADDRESS, N8N_PROTOCOL, N8N_SSL_KEY, N8N_SSL_CERT, defaults): https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment.md
- n8n security policies (MFA enforcement, licensing, SSO exception): https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/manage-security-policies.md
- n8n SSL setup: https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/set-up-ssl.md
- n8n public API authentication (`/api/v1` base path, `X-N8N-API-KEY` header): https://docs.n8n.io/connect/n8n-api/authentication
- n8n Webhook node (Authentication options, production and test URLs, HTTP Method): https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/
- n8n Webhook credentials (Basic, Header, JWT auth): https://docs.n8n.io/integrations/builtin/credentials/webhook/
