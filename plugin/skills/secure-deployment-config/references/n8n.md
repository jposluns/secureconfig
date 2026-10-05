---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-10",
  "body_sha256": "c22b274f7193fd37358264d2c71e4df60bb0476cacf003435df72f8cf420f665",
  "components": {
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
    "server": {
      "name": "n8n listener source",
      "basis": "n8n@2.40.6",
      "sources": {
        "sd3ce4e1b39e5": "https://github.com/n8n-io/n8n/blob/n8n%402.40.6/packages/%40n8n/config/src/index.ts#L164-L171",
        "s1e4d79276a10": "https://raw.githubusercontent.com/n8n-io/n8n/n8n@2.40.6/packages/cli/BREAKING-CHANGES.md"
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
    "secure-cookie": {"text": "Retain N8N_SECURE_COOKIE=true, its default. Source gap: listed proxy page does not state this default.", "components": ["docs", "server"], "sources": ["docs:se9dd39628347", "server:s1e4d79276a10"], "status": "REASONED"},
    "proxy-hops": {"text": "Set N8N_PROXY_HOPS to the trusted hop count for forwarded client IPs and rate limiting; public webhooks do not require a public editor.", "components": ["docs"], "sources": ["docs:se9dd39628347"], "status": "REASONED"},
    "native-tls": {"text": "N8N_PROTOCOL=https with N8N_SSL_KEY/N8N_SSL_CERT enables native TLS.", "components": ["docs"], "sources": ["docs:s2f99613ed917", "docs:s695f877f7b28"], "status": "REASONED"},
    "owner": {"text": "Complete first-run owner setup before publication; an unclaimed instance can be claimed by its first visitor. Source gap: listed security-policy page does not document owner setup.", "components": ["docs"], "sources": ["docs:scb2b0578a5a2"], "status": "REASONED"},
    "user-mfa": {"text": "Individual users can enable two-factor authentication, subject to version/licence availability.", "components": ["docs"], "sources": ["docs:scb2b0578a5a2"], "status": "REASONED"},
    "mfa-enforcement": {"text": "Enforce MFA through Settings > Security or N8N_MFA_ENFORCED_ENABLED with N8N_SECURITY_POLICY_MANAGED_BY_ENV; env policy requires 2.18.0+ and self-hosted Business/Enterprise.", "components": ["policy"], "sources": ["policy:scb2b0578a5a2"], "status": "REASONED"},
    "sso-mfa": {"text": "Instance MFA enforcement excludes SSO logins; enforce their MFA at the identity provider.", "components": ["docs"], "sources": ["docs:scb2b0578a5a2"], "status": "REASONED"},
    "encryption": {"text": "Stored credentials are encrypted; unset N8N_ENCRYPTION_KEY generates a key under ~/.n8n, not plaintext; losing it makes retained credentials unrecoverable.", "components": ["docs"], "sources": ["docs:se8f5861891dc"], "status": "REASONED"},
    "key-custody": {"text": "Set the same encryption key across workers/replicas, back it up separately from the database and exclude it from source and images.", "components": ["docs"], "sources": ["docs:se8f5861891dc"], "status": "REASONED"},
    "webhook-auth": {"text": "Webhook None is open; controlled callers use per-node Basic, Header or JWT auth with the matching credential.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "auth-boundaries": {"text": "Editor sessions, /api/v1 with X-N8N-API-KEY and per-node webhook auth are separate boundaries.", "components": ["docs"], "sources": ["docs:s7ce8bf5b35e8", "docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "signature": {"text": "A None webhook must validate the provider signature before downstream processing when callers cannot supply native webhook credentials.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED"},
    "code-execution": {"text": "Code executes JavaScript/Python; Execute Command runs shell commands inside the container under Docker and is disabled by default from 2.0. Source gap: listed task-runner page supports Code, not the Execute Command default.", "components": ["docs", "v2-docs"], "sources": ["docs:s290535cad2ea", "v2-docs:s994d1a49cf93"], "status": "REASONED"},
    "runners": {"text": "Use hardened external task runners; vendor describes internal mode as insecure by design.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "environment": {"text": "Set N8N_BLOCK_ENV_ACCESS_IN_NODE=true to block node access to the service environment, including encryption material. Source gap: listed task-runner page does not document this variable.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "js-modules": {"text": "Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "python-modules": {"text": "Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation.", "components": ["docs"], "sources": ["docs:s290535cad2ea"], "status": "REASONED"},
    "ssrf": {"text": "Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking.", "components": ["ssrf"], "sources": ["ssrf:s907260f38eee"], "status": "REASONED"},
    "verify-inventory": {"text": "Confirm completed owner setup without creating an owner as a probe; ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately.", "components": ["docs"], "sources": ["docs:s2f99613ed917", "docs:s290535cad2ea"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS reachability tests TLS, not authentication.", "components": ["docs"], "sources": ["docs:s695f877f7b28"], "status": "REASONED", "verify": [1]},
    "verify-api": {"text": "At the same /api/v1/workflows URL, no key gives native 401 and valid key gives 200 workflow JSON; retain any proxy credentials and feed API key on stdin. Source gap: listed API page documents the header, not these exact status outcomes.", "components": ["docs"], "sources": ["docs:s7ce8bf5b35e8"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "Confirm editor session login at /rest/login separately; a protected public API does not prove editor protection. Source gap: listed API page does not document /rest/login.", "components": ["docs"], "sources": ["docs:s7ce8bf5b35e8"], "status": "REASONED", "verify": [1]},
    "verify-webhook": {"text": "Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; Basic/JWT missing is 401, Header missing is 403; verify actions, not status alone. Source gap: listed node/credential pages do not establish the exact refusal codes.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED", "verify": [1]},
    "verify-signature": {"text": "For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection.", "components": ["docs"], "sources": ["docs:sab23639d9b2a", "docs:sa18a30d563bd"], "status": "REASONED", "verify": [1]}
  }
}
---
# n8n: binding, TLS, and MFA

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-10 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| bind-default: n8n 2.40.6 defaults N8N_LISTEN_ADDRESS to :: and N8N_PORT to 5678, exposing all interfaces. | n8n listener source n8n@2.40.6 | REASONED |
| protocol-default: N8N_PROTOCOL defaults http; private deployment sets listener, port and host explicitly. | n8n documentation unknown | REASONED |
| container-bind: Host loopback is for a same-host proxy; container loopback blocks sibling/published access, so use a private network without publication or host-loopback 127.0.0.1:5678:5678. | n8n documentation unknown | REASONED |
| other-ports: Keep Postgres and task-runner broker ports unpublished and publish only the HTTPS proxy. | n8n documentation unknown | REASONED |
| public-url: Set N8N_PROTOCOL=https and the full N8N_WEBHOOK_URL; WEBHOOK_URL is deprecated from 2.35.0 but still warns and works. | n8n documentation unknown | REASONED |
| secure-cookie: Retain N8N_SECURE_COOKIE=true, its default. Source gap: listed proxy page does not state this default. | n8n documentation unknown; n8n listener source n8n@2.40.6 | REASONED |
| proxy-hops: Set N8N_PROXY_HOPS to the trusted hop count for forwarded client IPs and rate limiting; public webhooks do not require a public editor. | n8n documentation unknown | REASONED |
| native-tls: N8N_PROTOCOL=https with N8N_SSL_KEY/N8N_SSL_CERT enables native TLS. | n8n documentation unknown | REASONED |
| owner: Complete first-run owner setup before publication; an unclaimed instance can be claimed by its first visitor. Source gap: listed security-policy page does not document owner setup. | n8n documentation unknown | REASONED |
| user-mfa: Individual users can enable two-factor authentication, subject to version/licence availability. | n8n documentation unknown | REASONED |
| mfa-enforcement: Enforce MFA through Settings &gt; Security or N8N_MFA_ENFORCED_ENABLED with N8N_SECURITY_POLICY_MANAGED_BY_ENV; env policy requires 2.18.0+ and self-hosted Business/Enterprise. | n8n environment policy minimum 2.18.0 | REASONED |
| sso-mfa: Instance MFA enforcement excludes SSO logins; enforce their MFA at the identity provider. | n8n documentation unknown | REASONED |
| encryption: Stored credentials are encrypted; unset N8N_ENCRYPTION_KEY generates a key under ~/.n8n, not plaintext; losing it makes retained credentials unrecoverable. | n8n documentation unknown | REASONED |
| key-custody: Set the same encryption key across workers/replicas, back it up separately from the database and exclude it from source and images. | n8n documentation unknown | REASONED |
| webhook-auth: Webhook None is open; controlled callers use per-node Basic, Header or JWT auth with the matching credential. | n8n documentation unknown | REASONED |
| auth-boundaries: Editor sessions, /api/v1 with X-N8N-API-KEY and per-node webhook auth are separate boundaries. | n8n documentation unknown | REASONED |
| signature: A None webhook must validate the provider signature before downstream processing when callers cannot supply native webhook credentials. | n8n documentation unknown | REASONED |
| code-execution: Code executes JavaScript/Python; Execute Command runs shell commands inside the container under Docker and is disabled by default from 2.0. Source gap: listed task-runner page supports Code, not the Execute Command default. | n8n documentation unknown; n8n 2.0 breaking changes unknown | REASONED |
| runners: Use hardened external task runners; vendor describes internal mode as insecure by design. | n8n documentation unknown | REASONED |
| environment: Set N8N_BLOCK_ENV_ACCESS_IN_NODE=true to block node access to the service environment, including encryption material. Source gap: listed task-runner page does not document this variable. | n8n documentation unknown | REASONED |
| js-modules: Narrow NODE_FUNCTION_ALLOW_BUILTIN/NODE_FUNCTION_ALLOW_EXTERNAL in external launcher's /etc/n8n-task-runners.json env-overrides; main-container values are overridden. | n8n documentation unknown | REASONED |
| python-modules: Set N8N_RUNNERS_STDLIB_ALLOW/N8N_RUNNERS_EXTERNAL_ALLOW explicitly; wildcard grants broad module access and version-dependent defaults need confirmation. | n8n documentation unknown | REASONED |
| ssrf: Enable N8N_SSRF_PROTECTION_ENABLED from 2.12.0 and restrict network egress; the app filter does not contain arbitrary code/command networking. | n8n SSRF filter minimum 2.12.0 | REASONED |
| verify-inventory: Confirm completed owner setup without creating an owner as a probe; ss is local inventory, not firewall/NAT proof; check actual public IPv4/IPv6 paths separately. | n8n documentation unknown | REASONED |
| verify-tls: HTTPS reachability tests TLS, not authentication. | n8n documentation unknown | REASONED |
| verify-api: At the same /api/v1/workflows URL, no key gives native 401 and valid key gives 200 workflow JSON; retain any proxy credentials and feed API key on stdin. Source gap: listed API page documents the header, not these exact status outcomes. | n8n documentation unknown | REASONED |
| verify-editor: Confirm editor session login at /rest/login separately; a protected public API does not prove editor protection. Source gap: listed API page does not document /rest/login. | n8n documentation unknown | REASONED |
| verify-webhook: Use each production /webhook/ method and valid payload with missing/wrong/valid credentials; Basic/JWT missing is 401, Header missing is 403; verify actions, not status alone. Source gap: listed node/credential pages do not establish the exact refusal codes. | n8n documentation unknown | REASONED |
| verify-signature: For None plus workflow signature checks, unsigned calls must run no action; 404 from inactive/wrong path/method is not protection. | n8n documentation unknown | REASONED |
<!-- version-basis:end -->

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
# REASONED: listener, TLS, API and webhook comparisons have no recorded n8n run; no live n8n deployment is available in this read-only review. Expectations follow the listed sources, with sourcing gaps recorded in the claim table.
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
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
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
