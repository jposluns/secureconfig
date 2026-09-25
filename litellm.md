# LiteLLM proxy: master key and virtual keys

A LiteLLM proxy fronts paid model APIs, so an exposed, keyless instance spends your provider credits for whoever finds it. Authentication is built in and must be switched on before anything else.

## 1. Set the master key

In `config.yaml` under `general_settings: master_key`, or via the environment (preferred; see [secrets.md](secrets.md)):

```bash
export LITELLM_MASTER_KEY="sk-REPLACE_WITH_LONG_RANDOM_VALUE"   # must start with sk-
```

The master key is the root credential for the proxy; it belongs to the operator only and never to client applications. Generate it with `openssl rand -hex 32` (kept behind the `sk-` prefix), and inject it from your secret store or a root-only environment file rather than typing the `export` above into an interactive shell, where it is captured in shell history and readable in `/proc/<pid>/environ` ([secrets.md](secrets.md)). When both the environment and `config.yaml` set the master key, the `config.yaml` value wins.

At the time of writing, current LiteLLM refuses to start when the resolved master key is unset, empty or whitespace-only, or `sk-1234`. Either `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true` or the YAML setting `general_settings.dangerously_permit_weak_or_unset_master_key: true` permits weak or keyless startup independently; keep both overrides absent or false in production. Older releases and overridden deployments can still operate without authentication, so the unauthenticated-deployment warning above remains relevant. A startup refusal is a protection to retain, not a reason to enable the override. No first release is asserted here. See [master-key startup protection](https://docs.litellm.ai/docs/proxy/master_key_rotations) and the [current startup enforcement call](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/proxy_server.py).

## 2. Issue virtual keys per application

Virtual keys need a PostgreSQL database: set `DATABASE_URL=postgresql://user:password@host:5432/dbname` in the environment (or `database_url` under `general_settings`) before `/key/generate` will work.

The original alias-only request below illustrates issuance and attribution. It does not establish least privilege: use the restricted request body below for application keys, and substitute your actual HTTPS origin.

```bash
printf 'Authorization: Bearer %s\n' "$LITELLM_MASTER_KEY" | curl -q https://llm.example.com/key/generate \
  -H @- \
  -H "Content-Type: application/json" \
  -d '{"key_alias": "app-frontend"}'
```

Each app gets its own virtual key, which can be revoked or budgeted independently; LiteLLM's docs cover per-key models, budgets, and expiry. Clients send the virtual key in the `Authorization` header (the header name is configurable via `litellm_key_header_name`).

Written the naive way, with the key in `-H "Authorization: Bearer $LITELLM_MASTER_KEY"` on curl's own arguments, it would be readable in `/proc/<pid>/cmdline` while it runs (shell history keeps the literal `$LITELLM_MASTER_KEY`, not its value); on a shared host feed the header to curl on stdin instead, as the request above and the Verify below do: `printf 'Authorization: Bearer %s\n' "$LITELLM_MASTER_KEY" | curl -H @- ...`. Virtual keys are stored hashed, but the provider API keys LiteLLM persists when `general_settings.store_model_in_db` is on are ENCRYPTED with `LITELLM_SALT_KEY` (which falls back to the master key when unset): set a permanent `LITELLM_SALT_KEY` BEFORE adding any credential, because changing it later strands what it encrypted, and protect the database and its backups as the store of those secrets. A credential written literally into `config.yaml` stays plaintext in that file, so keep it out of version control ([secrets.md](secrets.md)).

Keep `DATABASE_URL` in secret storage too: its password is a database credential. Leave `general_settings.store_model_in_db: false` unless database-managed models are needed. Disabling model storage does not remove the database requirement for virtual keys. See [configuration settings](https://docs.litellm.ai/docs/proxy/config_settings).

### Set spend, throughput, model access, and expiry together

Use this JSON body with `POST /key/generate`. The amounts are examples, not defaults. Replace the IDs, and use the exact `model_name` from your `model_list`; `app-chat` is the example name used below. The owner must already exist and have the appropriate team membership.

```json
{
  "key_alias": "app-frontend",
  "user_id": "REPLACE_WITH_NON_ADMIN_USER_ID",
  "team_id": "REPLACE_WITH_TEAM_ID",
  "models": ["app-chat"],
  "max_budget": 25,
  "budget_duration": "30d",
  "rpm_limit": 30,
  "tpm_limit": 50000,
  "max_parallel_requests": 4,
  "duration": "30d",
  "allowed_routes": [
    "/chat/completions",
    "/v1/chat/completions",
    "/models",
    "/v1/models"
  ]
}
```

`max_budget` is USD; its default is `null`, meaning no key-level spend limit. `budget_duration` controls spend resets. It does not expire the credential: `duration` controls key lifetime. `rpm_limit` limits requests per minute, `tpm_limit` limits tokens per minute, and `max_parallel_requests` limits concurrent requests. `soft_budget` only triggers configured alerts; it does not block spending. See [budgets and rate limits](https://docs.litellm.ai/docs/proxy/users) and the [request schemas and defaults](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/_types.py).

Set an explicit model allowlist on BOTH the key and its team. **`models: []` means ALL models, not no models.** A team-attached key must satisfy both lists. The master key bypasses model restrictions, so never use it to demonstrate an application's model boundary. See [model-access resolution](https://docs.litellm.ai/docs/proxy/key_auth_arch) and the [master-key authentication path](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/user_api_key_auth.py).

Create the shared spending boundary with `POST /team/new`:

```json
{
  "team_alias": "app-production",
  "models": ["app-chat"],
  "max_budget": 100,
  "budget_duration": "30d",
  "rpm_limit": 120,
  "tpm_limit": 200000
}
```

Use the returned `team_id` on every application key that should share those limits. For an existing team, send the fields to change plus its `team_id` to `POST /team/update`. Team spend and throughput limits aggregate the attached keys; independent per-key limits alone do not cap the application's combined use across multiple keys. Add the intended non-admin owner to the team with `POST /team/member_add` before issuing its key. See [team budgets](https://docs.litellm.ai/docs/proxy/team_budgets), [team rate limits](https://docs.litellm.ai/docs/proxy/users), and the [team-update schema](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/_types.py).

### Share enforcement state across workers and replicas

Shared Redis is REQUIRED for correct shared limits and revocation across multiple workers or replicas. A single container with multiple workers also needs it. Without shared state, workers can maintain separate counters and keep accepting a revoked key until their local cache expires. Configure both router Redis and proxy caching; merely exporting Redis variables is insufficient. See [What Needs Redis](https://docs.litellm.ai/docs/proxy/redis_requirements).

Merge these settings into the existing sections of `config.yaml`; do not create duplicate top-level YAML keys:

```yaml
router_settings:
  redis_host: os.environ/REDIS_HOST
  redis_port: os.environ/REDIS_PORT
  redis_password: os.environ/REDIS_PASSWORD

litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: os.environ/REDIS_HOST
    port: os.environ/REDIS_PORT
    password: os.environ/REDIS_PASSWORD

general_settings:
  fail_closed_budget_enforcement: true
```

Point every worker at the same shared Redis service and protect its credentials and network access. This configuration also enables response caching: keeping content out of logs does not mean content is absent from the cache.

`general_settings.fail_closed_budget_enforcement: true` rejects requests with 503 when current spend cannot be verified against Redis or the database. Keep budget reservation enabled. This is not an absolute provider-spend cap: batch submissions do not expose their full workload for estimation, and routes whose cost cannot be estimated can fall back to recorded-spend checks. Concurrent or delayed charges can therefore exceed a nominal budget. See [budget reservation, batch limitations, and fail-closed enforcement](https://docs.litellm.ai/docs/proxy/users).

### Expire, block, and revoke keys

Keep a finite `"duration": "30d"` on generation, and rotate before expiry. For permanent revocation, send `POST /key/delete` with this body:

```json
{
  "keys": ["REPLACE_WITH_VIRTUAL_KEY"]
}
```

For reversible suspension, send `POST /key/block`:

```json
{
  "key": "REPLACE_WITH_VIRTUAL_KEY"
}
```

`POST /key/unblock` accepts the same single-key body to restore a blocked key. Deletion and blocking are different operations; do not treat removing a key from an application's configuration as revocation.

At the time of writing, in-place virtual-key rotation through `/key/regenerate` is Enterprise-gated. Without it, generate a replacement with the same intended restrictions, deploy it to the application, confirm it works, then delete the old key. Preserve the shared team budget during replacement so issuing a new key does not create a fresh application-wide spending allowance. Test revocation on every worker; Redis coordination is not evidence that your particular deployment propagated it successfully. See [blocking and rotation](https://docs.litellm.ai/docs/proxy/virtual_keys) and the [delete and regenerate implementations](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/key_management_endpoints.py).

Key values in these JSON bodies are credentials. Supply them through a protected request file, as in Verify, rather than putting the JSON containing a real key in curl's arguments. Protect issuance responses too: they contain the new key.

## 3. Bind privately and add TLS in front

Run the proxy on loopback (or a private container network) and publish it only through a TLS layer: [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or [cloudflare.md](cloudflare.md)/[tailscale.md](tailscale.md) for no-open-port setups. The proxy's `--host` defaults to `0.0.0.0` (as of v1.102.1), so bind it explicitly: `litellm --host 127.0.0.1 --port 4000 --config config.yaml`. The Verify check below confirms it is on loopback. Bearer keys over plain HTTP are compromised on first use. For human access to the LiteLLM admin UI, add MFA at the fronting layer ([mfa.md](mfa.md)).

At the time of writing, LiteLLM's `allowed_ips` filtering is an Enterprise feature. Where it is unavailable, filter ingress independently with the firewall, private network, or fronting proxy; a configured but unavailable feature is not an access boundary. See [IP address filtering](https://docs.litellm.ai/docs/proxy/ip_address).

## 4. Admin UI, routes, and outbound destinations

The admin UI at `/ui` has its own login, separate from inference auth: `UI_USERNAME` defaults to `admin`, and with no `UI_PASSWORD` set the UI accepts the master key itself. Set individual admin logins or SSO, then set `general_settings.disable_env_credential_login: true` and restart so the shared bootstrap login (the env `UI_USERNAME`/master-key credential) stops working, since creating personal logins does not by itself disable it; or disable an unused UI entirely with `DISABLE_ADMIN_UI="True"`. Set `PROXY_BASE_URL` to the public `https://` origin so the UI's session cookies are marked `Secure` when TLS terminates at the proxy in front.

At the time of writing, SSO is free for up to five users from v1.76.0; more users require Enterprise. The username/password bootstrap fallback above still needs deliberate removal after personal login or SSO works. See [SSO licensing](https://docs.litellm.ai/docs/proxy/admin_ui_sso) and [disabling environment credential login](https://docs.litellm.ai/docs/proxy/ui).

### Separate application credentials from administrative authority

Never give application keys a `proxy_admin` owner. Management authority follows the owner's role, so a key intended for inference can otherwise carry administrative powers. Use `internal_user` for ordinary human users and reserve `proxy_admin` for operators. Keep application keys separate from human UI credentials. The `allowed_routes` entries in step 2 match the named paths and their slash-separated descendants: `/v1/models` also matches `/v1/models/anything`. This is a prefix allowlist, not an exact-path or per-HTTP-method allowlist. Enforce exact paths and methods at the ingress proxy where that is the intended boundary; remove model listing if the application does not need it. See [key ownership and inherited authority](https://docs.litellm.ai/docs/proxy/virtual_keys) and [RBAC roles](https://docs.litellm.ai/docs/proxy/access_control).

Where Enterprise is available, `general_settings.admin_only_routes` can further restrict individual management endpoints:

```yaml
general_settings:
  admin_only_routes:
    - /key/generate
    - /key/delete
    - /key/block
    - /key/unblock
    - /team/new
    - /team/update
```

This list is EXACT-MATCH: `/key/*` does not cover the key-management routes. List every route you intend to restrict. Without Enterprise, current source logs an error and skips this additional check; it does not turn the list into an enforced policy. Independently restrict management ingress and key ownership. See [route configuration](https://docs.litellm.ai/docs/proxy/public_routes) and [the licence check and exact comparison](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/route_checks.py).

### Remove public documentation and isolate health and metrics

Not every route sits behind the key. `/health/liveliness` (and `/health/liveness`) are unauthenticated worker checks, and the docs routes (`/`, `/redoc`, `/openapi.json`) are public by default, so a reply from any of them proves nothing about inference auth; `/health` is authenticated when key auth is on. `/metrics` on the proxy port is authenticated by default (confirmed in v1.85.0; `litellm_settings.require_auth_for_metrics_endpoint: false` reopens it) and exposes spend and operational labels, not provider keys. Restrict the routes you do not need at the fronting proxy.

`/health/readiness` is also unauthenticated. `/health` runs real model probes, which can incur provider charges; keep it private rather than using it as a public uptime check. See [health-route authentication and probe behavior](https://docs.litellm.ai/docs/proxy/health).

`PROMETHEUS_METRICS_PORT` can open a SEPARATE UNAUTHENTICATED metrics listener. `require_auth_for_metrics_endpoint` protects only `/metrics` on the proxy port. Keep the separate port private and allow only trusted collectors; inspect container publications and load-balancer listeners as well as the proxy socket. See [dedicated metrics-listener security](https://docs.litellm.ai/docs/proxy/prometheus) and the [v1.85.0 default](https://raw.githubusercontent.com/BerriAI/litellm/v1.85.0/litellm/__init__.py).

Disable unused documentation in the proxy's actual startup environment and restart:

```bash
unset DOCS_URL REDOC_URL OPENAPI_URL
export NO_DOCS=True NO_REDOC=True NO_OPENAPI=True
```

Explicit `DOCS_URL`, `REDOC_URL`, and `OPENAPI_URL` values override the corresponding disable flags. Remove those values from the service or container configuration too; unsetting them in an unrelated shell does not change the service. Disabling documentation does not disable the APIs it describes. See [environment-variable reference](https://docs.litellm.ai/docs/proxy/config_settings) and [URL-selection precedence](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/utils.py).

### Constrain destinations and pass-through routes

A model's `api_base` and any pass-through `target` are outbound destinations the proxy will call, so a config that lets the wrong person add them is an SSRF and egress path: restrict who may change destinations and constrain the proxy's egress ([egress-metadata.md](egress-metadata.md)); the documentation still labels pass-through route authentication as an Enterprise feature.

At the time of writing, current `main` disagrees with that documentation: `auth: true` attaches LiteLLM authentication without an Enterprise licence check. Caller authorization is separate: a non-admin caller must also be authorized through `allowed_passthrough_routes` in key or team metadata; adding the path to `allowed_routes` alone is insufficient. The normal top-level `allowed_passthrough_routes` setting is an Enterprise-gated metadata field. Consequently, treat this authenticated forwarder as effectively admin/master-key territory on non-Enterprise deployments and omit the optional `pass_through_endpoints` for application traffic. Verify the behavior and licensed provisioning support of your installed release; no first release is asserted here. Do not resolve a licence or startup failure by disabling authentication or giving applications an admin or master key. See the [pass-through documentation](https://docs.litellm.ai/docs/proxy/pass_through) and [current route registration](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/pass_through_endpoints/pass_through_endpoints.py).

Pin `model_list[].litellm_params.api_base` to the intended provider. For any required forwarder, use an explicit target, authentication, the narrowest methods, no arbitrary subpaths, and no wholesale forwarding of incoming headers:

```yaml
model_list:
  - model_name: app-chat
    litellm_params:
      model: openai/REPLACE_WITH_PROVIDER_MODEL
      api_base: https://api.example.com/v1
      api_key: os.environ/PROVIDER_API_KEY

general_settings:
  store_model_in_db: false
  pass_through_endpoints:
    - path: /vendor-status
      target: https://api.example.com/status
      auth: true
      methods: ["GET"]
      include_subpath: false
      forward_headers: false
```

Replace the provider model, origin, and target with endpoints you operate or have approved. Omit `pass_through_endpoints` entirely when no forwarder is needed. This example's upstream status endpoint requires no credential; if your target requires authentication, provision only its required upstream credentials through secret storage. `auth: true` authenticates the caller to LiteLLM. See [model configuration](https://docs.litellm.ai/docs/proxy/virtual_keys) and the [pass-through field reference](https://docs.litellm.ai/docs/proxy/pass_through).

**Pinning a model is NOT a destination allowlist.** Callers can supply `api_base` or `base_url` overrides on supported request paths. Enforce an egress allowlist independently and reject caller-supplied destination overrides at a trusted request-validation layer. Account for redirects and DNS resolution in that egress policy, and deny metadata and unintended internal destinations. See [request routing with `api_base`](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/route_llm_request.py), [`base_url` handling](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/main.py), and [egress-metadata.md](egress-metadata.md).

## 5. Keep request content out of logs

Merge these settings into the existing configuration:

```yaml
litellm_settings:
  turn_off_message_logging: true

general_settings:
  store_prompts_in_spend_logs: false
```

Keep the environment switch unset in the service's startup configuration:

```bash
unset STORE_PROMPTS_IN_SPEND_LOGS
```

`turn_off_message_logging` suppresses message and response content in supported logging integrations while retaining operational metadata such as spend. Spend-log payload storage has a separate switch: either `general_settings.store_prompts_in_spend_logs` or `STORE_PROMPTS_IN_SPEND_LOGS` enabling it is sufficient. A YAML value of `false` does not override an environment value of `true`. See [message redaction](https://docs.litellm.ai/docs/proxy/logging) and [the spend-log storage decision](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/spend_tracking/spend_tracking_utils.py).

Avoid production `--detailed_debug` and `LITELLM_LOG=DEBUG`; inspect the actual process arguments and deployment environment. These settings do not promise to sanitize arbitrary custom callbacks, application logging, or fronting-proxy body capture. Review each configured callback and log destination, including error paths. See [CLI debugging](https://docs.litellm.ai/docs/proxy/cli), [logging callbacks](https://docs.litellm.ai/docs/proxy/logging), and [logging environment settings](https://docs.litellm.ai/docs/proxy/config_settings).

## 6. Verify

### Backend authentication and listener exposure

**REASONED:** No live LiteLLM service, PostgreSQL/Redis deployment, provider credentials, or second-host network fixture is available in this read-only authoring environment; LiteLLM and a container runtime are not installed. The checks below have not been demonstrated against exposed and fixed deployments. Sources: [virtual-key authentication](https://docs.litellm.ai/docs/proxy/virtual_keys) and [CLI listener settings](https://docs.litellm.ai/docs/proxy/cli). Expected exposed and fixed outcomes are stated in the block.

Use a valid virtual key whose `allowed_routes` includes `/v1/models`. Substitute inside the single quotes and paste the whole block. Do not paste a value containing an apostrophe directly into a single-quoted substitution site. The stdin technique closes curl's argument exposure; it does not hide secrets from shell history, shell tracing, or the account owner.

```bash
# Test LiteLLM's OWN auth against the BACKEND directly on loopback, with no fronting proxy in the path,
# three ways: with no key and with a WRONG key LiteLLM must refuse (401); with a VALID virtual key it
# returns the model list. A gateway that answers 401 and then forwards a header-bearing request to a
# keyless proxy would pass a public-edge test, so probe the backend. The valid key is fed to curl on
# STDIN (-H @-) so it never enters curl's arguments, a temp file, or a shell variable; the guard refuses
# on a placeholder. (The key you substitute on the set -- line does enter your shell history, so use a
# short-lived key or clear that history line afterward.)
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VIRTUAL_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*) echo "substitute the virtual key on the set -- line above; not probing"; exit 1 ;;
    *)
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-key=%{http_code} exit=%{exitcode}\n' http://127.0.0.1:4000/v1/models
  # guard-conventions: allow deliberate bad-key negative control; sk-not-a-real-key is a dummy, not a live credential
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'bad-key=%{http_code} exit=%{exitcode}\n' -H 'Authorization: Bearer sk-not-a-real-key' http://127.0.0.1:4000/v1/models
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\ngood-key=%{http_code} exit=%{exitcode}\n' -H @- http://127.0.0.1:4000/v1/models
      ;;
  esac
)
# Expected: no-key and bad-key => 401 from LiteLLM; good-key => 200 with the model list (a 200 without a
# key is the finding). Then repeat the good-key request through the public https ingress to confirm the
# TLS front works. A transport error (exit != 0) is inconclusive, not a pass.
ss -tlnp   # a listener inventory in THIS network namespace, not a firewall/NAT/publication check:
           # confirm 4000 is loopback-only here, then from ANOTHER host confirm 4000 is refused
           # externally (a Docker DNAT publication need not appear in this list at all).
```

The `/v1/models` comparison tests authentication and listing, not successful inference or model authorization. Complete the inference comparisons below too. Inspect IPv4 and IPv6 reachability, published container ports, and any separate metrics listener.

### Protected requests for the comparisons

**REASONED:** The live deployment and test credentials described above are unavailable. Use this request block for the concrete comparisons below; a successful curl transport alone is never a pass. Inspect its private response body and headers for the specified LiteLLM result.

Before running it, provision a mode-0600 header file in a private directory containing `Authorization: Bearer ` followed by the appropriate test or administrative key. Use an empty header file for unauthenticated requests. Prepare the JSON body in another protected file, substituting its placeholders before use; `{}` suffices for GET, which ignores that file. Keep URLs free of credentials. The block captures responses privately because management responses can contain keys.

Use `http://127.0.0.1:4000/...` on the backend host, or your actual HTTPS endpoint. For each POST, use the endpoint and JSON specified in the comparison. Run destructive operations only against disposable test keys and teams.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENDPOINT_URL' 'POST' 'REPLACE_WITH_HEADER_FILE' 'REPLACE_WITH_JSON_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "provide endpoint, method, header file and JSON file; not probing"; exit 1; }
  case "|$1|$2|$3|$4|" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|*'||'*|*[[:cntrl:]]*)
      echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
  esac
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the endpoint; not probing"; exit 1 ;;
    https://*|http://127.0.0.1:4000/*)
      [ -r "$3" ] || { echo "header file is unreadable"; exit 1; }
      [ -r "$4" ] || { echo "JSON file is unreadable"; exit 1; }
      umask 077
      set -- "$@" "$(mktemp -d)" || exit 1
      [ -d "$5" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Private response directory: %s\n' "$5"
      case "$2" in
        POST)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -H 'Content-Type: application/json' \
            --data-binary "@$4" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        GET)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 \
            -H "@$3" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        *) echo "only GET and POST are supported; not probing"; exit 1 ;;
      esac
      ;;
    *) echo "use HTTPS or the loopback backend; not probing"; exit 1 ;;
  esac
)
```

This guard checks substituted arguments, not the contents of the input files. Inspect those files before a mutation. Delete the private response directories and test credential files after recording the necessary redacted evidence.

### Model access, limits, expiry, and revocation

**REASONED:** These comparisons need a running proxy, disposable database-backed keys and teams, shared Redis, and an approved provider test allowance, none of which is available here. Use the protected POST block with `/v1/chat/completions` and this body, choosing a configured chat model that supports the request:

```json
{
  "model": "app-chat",
  "messages": [
    {
      "role": "user",
      "content": "Reply with LITELLM-VERIFY-CANARY."
    }
  ],
  "max_tokens": 16
}
```

Use a distinct harmless marker for each paid request and confirm that the provider was actually called; cached responses do not demonstrate spend enforcement. Establish a successful permitted request before each negative comparison. A missing model, bad provider credential, timeout, or unrelated rate limit does not demonstrate the intended restriction.

| Control | Concrete comparison | Expected exposed and fixed outcomes |
| --- | --- | --- |
| Key and team model lists | Send the body for two configured models that both work with a suitably authorized control key. First exclude the second model only on the test key, then only on its team, using the generation body and `/team/update`. | With unrestricted lists, both models work. Each narrow-list case must reject the excluded model with a model-access error while `app-chat` still works. See [model-access resolution](https://docs.litellm.ai/docs/proxy/key_auth_arch). |
| Spend and team aggregation | Give a disposable key a small positive budget sufficient for one known-cost call. Repeat bounded requests until it is exhausted. Separately exhaust a small team budget using two attached keys that remain below their individual budgets. | Uncapped control keys continue; the fixed key or team returns a budget-exceeded rejection without another provider call. Record costs and any overshoot. See [budget enforcement](https://docs.litellm.ai/docs/proxy/users). |
| RPM, TPM, and parallel requests | Test one limit at a time. For RPM, use a test limit of 1 and send two requests in the same window. For TPM, use a known token workload above a small test limit. For parallel requests, use a limit of 1 and overlap two requests while the first remains active. | Without the tested limit, both requests can proceed. With it, excess work receives the corresponding limiter rejection, normally 429; an under-limit control still succeeds. Repeat across workers, not just one process. See [rate limits](https://docs.litellm.ai/docs/proxy/users) and [shared counters](https://docs.litellm.ai/docs/proxy/redis_requirements). |
| Finite lifetime | Generate a disposable key with `"duration": "1m"` and send the same permitted request before and after its returned expiry time. | A non-expiring control remains usable. The finite key works before expiry and is rejected afterward; a separate unexpired control still works. See [key lifetime](https://docs.litellm.ai/docs/proxy/virtual_keys). |
| Block, unblock, and delete | After proving the test key works, use administrative POST requests to `/key/block`, `/key/unblock`, and finally `/key/delete`, with the respective bodies from step 2. Repeat its inference request after each operation on every worker. | Block rejects; unblock restores access; delete rejects permanently. Continued acceptance on any worker is a finding. The replacement key must still work. See [key operations](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/key_management_endpoints.py) and [cache invalidation](https://docs.litellm.ai/docs/proxy/redis_requirements). |

Do not extrapolate the RPM result to TPM or concurrency: each needs its own matched workload. Bound the request count and provider spend before starting.

**REASONED:** Fail-closed testing additionally needs an isolated deployment where Redis/database failures can be injected without affecting production. Repeat the same budgeted inference request with spend verification unavailable and `fail_closed_budget_enforcement` enabled: expect 503 and no provider call. Restore the dependencies and confirm a below-budget request succeeds. Compare the flag-disabled state to identify any admission on unverifiable spend. Test batch and unestimable-cost routes separately; their successful admission does not establish an absolute cap. See [fail-closed enforcement and reservation limitations](https://docs.litellm.ai/docs/proxy/users).

### Administrative routes, public surfaces, destinations, and logs

**REASONED:** These comparisons require the deployed ingress, installed LiteLLM release, test identities, controlled upstream endpoints, and collected logs, which are unavailable here. Use the protected request block for the GET and POST requests below. Keep any deliberately exposed comparison private and isolated.

| Control | Concrete comparison | Expected exposed and fixed outcomes |
| --- | --- | --- |
| Application/admin separation | POST the restricted generation body to `/key/generate` with the application key, then with the operator credential in an isolated test deployment. | An overprivileged application credential may create a key. The fixed application key must receive an authorization rejection; the operator's matched valid request succeeds. Revoke any test keys created. See [key ownership](https://docs.litellm.ai/docs/proxy/virtual_keys) and [RBAC](https://docs.litellm.ai/docs/proxy/access_control). |
| Enterprise admin-only routes | With a non-admin identity otherwise allowed to create its own keys, POST a valid `/key/generate` request before and after enabling the exact route restriction on a licensed fixture. | The added restriction denies the non-admin request while the operator succeeds. An unlicensed fixture logs the feature error and skips this extra restriction; ingress and application-key restrictions must still hold. See [route-check implementation](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/route_checks.py). |
| Documentation and health | Make unauthenticated GET requests to `/`, `/redoc`, `/openapi.json`, and `/health/readiness` on the backend and public origin. Inspect `/health` ingress policy without repeatedly running paid probes. | Exposed docs return documentation/schema content. After disabling them, that content is absent, including at previously configured custom docs paths. Readiness can still answer without a key and proves no inference protection. Public `/health` must be blocked by the chosen ingress policy. See [docs URL precedence](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/utils.py) and [health checks](https://docs.litellm.ai/docs/proxy/health). |
| Metrics and ingress filtering | GET `/metrics` on the proxy port without a key and with an authorized collector credential. If a separate metrics port is configured, test it from both a collector network and an excluded network. | Proxy-port metrics reject unauthenticated access. A dedicated listener can return metrics without a key to its allowed collector network; the excluded network must not reach it. Collector success distinguishes filtering from a broken listener. See [metrics-listener security](https://docs.litellm.ai/docs/proxy/prometheus). |
| Pass-through boundary | For the optional `/vendor-status` example, GET it without a key and with a key explicitly allowed to use that route; also try POST `/vendor-status` and GET `/vendor-status/extra`. | An exposed forwarder can be reached anonymously or forward unintended requests. The fixed route rejects anonymous access, forwards the permitted authenticated GET, and does not forward the wrong method or subpath. Confirm at the controlled upstream. See [pass-through configuration](https://docs.litellm.ai/docs/proxy/pass_through). |
| Destination overrides | In an isolated fixture with disposable upstream credentials, add `"api_base": "https://REPLACE_WITH_CONTROLLED_SINK/v1"` to the inference JSON; repeat separately with `"base_url"` instead. Replace the sink placeholder in the file. | The exposed comparison may contact the controlled sink. The fixed request-validation/egress policy must prevent that contact while the normal pinned destination still works. Inspect sink and egress records; a provider error alone is inconclusive. Never use metadata services or unrelated internal systems as test targets. See [override routing](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/route_llm_request.py) and [`base_url` handling](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/main.py). |
| Content logging | Send the canary inference request, then repeat with a new marker after applying step 5. Inspect the matching request window in spend logs, process logs, and every configured callback destination, including a controlled error case. | The exposed comparison establishes that content can reach the tested sink. The fixed comparison retains the expected request/spend metadata while omitting prompt and response content. A missing log record is not proof of redaction; arbitrary callbacks require separate review. See [message redaction](https://docs.litellm.ai/docs/proxy/logging) and [spend-log storage](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/spend_tracking/spend_tracking_utils.py). |

**REASONED:** UI testing needs a live UI and configured personal-login or SSO identities. Open the actual HTTPS `/ui` in a fresh browser session: establish that the intended personal login works, then confirm the old environment login is refused after `disable_env_credential_login` and restart. Inspect the session cookie's `Secure` attribute. If the UI is disabled, confirm it no longer serves the admin interface while an authorized inference request still works. See [UI login settings](https://docs.litellm.ai/docs/proxy/ui), [SSO](https://docs.litellm.ai/docs/proxy/admin_ui_sso), and [cookie security](https://docs.litellm.ai/docs/proxy/security_best_practices).

### Demonstration backlog

This row carries the original probes and the new controls together. Service behavior in this replacement is not yet demonstrated.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| LITELLM-LIVE-1 | Demonstrate every REASONED comparison above on a pinned LiteLLM release with PostgreSQL, shared Redis, at least two workers, approved provider test credentials, and a second-host ingress fixture. Cover backend authentication and actual inference; IPv4/IPv6 and container publication; key/team model intersections; key and aggregate team spend; RPM, TPM, and parallel limits; budget verification failures and batch/unestimable-route limitations; expiry, block/unblock, delete, and replacement across workers; application/admin separation and licensed/unlicensed route behavior; documentation URL overrides; health and both metrics listeners; UI fallback removal and Secure cookies; pass-through authentication, methods, subpaths, and headers; destination overrides and egress evidence; and prompt/response absence across spend, debug, error, and callback logs. Include isolated startup tests for unsafe master keys with both overrides absent or false, then with `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true` and YAML `general_settings.dangerously_permit_weak_or_unset_master_key: true` enabled independently. Record versions, commands, diagnostics, positive controls, propagation timing, costs, and cleanup. Configuration inspection alone does not close this row. | Open; service behavior is reasoned, not demonstrated. |

## Sources (checked September 2026)

- LiteLLM proxy virtual keys (master_key, /key/generate, header name): https://docs.litellm.ai/docs/proxy/virtual_keys
- LiteLLM proxy CLI (`--host` default `0.0.0.0`, `--port` default `4000`): https://docs.litellm.ai/docs/proxy/cli
- LiteLLM admin UI (`UI_USERNAME`/`UI_PASSWORD`, master-key fallback, `DISABLE_ADMIN_UI`): https://docs.litellm.ai/docs/proxy/ui
- LiteLLM security best practices (route exposure, `PROXY_BASE_URL` and `Secure` cookies): https://docs.litellm.ai/docs/proxy/security_best_practices
- LiteLLM config settings (`store_model_in_db`, `LITELLM_SALT_KEY`, `require_auth_for_metrics_endpoint`): https://docs.litellm.ai/docs/proxy/config_settings
- LiteLLM Prometheus metrics (authenticated by default): https://docs.litellm.ai/docs/proxy/prometheus
- LiteLLM pass-through endpoints (`target`, Enterprise auth): https://docs.litellm.ai/docs/proxy/pass_through
- [LiteLLM budgets, throughput limits, reservation, batch limitations, and fail-closed enforcement](https://docs.litellm.ai/docs/proxy/users).
- [LiteLLM team budgets and shared spending](https://docs.litellm.ai/docs/proxy/team_budgets).
- [LiteLLM request schemas: key budget defaults, lifetime, throughput, soft budgets, and team updates](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/_types.py).
- [LiteLLM model-access resolution: empty lists and key/team intersections](https://docs.litellm.ai/docs/proxy/key_auth_arch).
- [LiteLLM authentication source: master-key authority](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/user_api_key_auth.py).
- [LiteLLM Redis requirements: configuration, shared limits, and revocation propagation](https://docs.litellm.ai/docs/proxy/redis_requirements).
- [LiteLLM key-management source: deletion, blocking, and Enterprise-gated virtual-key regeneration](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/key_management_endpoints.py).
- [LiteLLM role-based access control](https://docs.litellm.ai/docs/proxy/access_control).
- [LiteLLM public/private routes and exact-match admin-only lists](https://docs.litellm.ai/docs/proxy/public_routes).
- [LiteLLM route-check source: Enterprise error and skipped admin-only check](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/route_checks.py).
- [LiteLLM IP filtering and Enterprise requirement](https://docs.litellm.ai/docs/proxy/ip_address).
- [LiteLLM SSO: free allowance from v1.76.0](https://docs.litellm.ai/docs/proxy/admin_ui_sso).
- [LiteLLM health routes: unauthenticated readiness and paid model probes](https://docs.litellm.ai/docs/proxy/health).
- [LiteLLM v1.85.0 source: authenticated metrics default](https://raw.githubusercontent.com/BerriAI/litellm/v1.85.0/litellm/__init__.py).
- [LiteLLM utility source: explicit documentation URLs override disable flags](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/utils.py).
- [LiteLLM pass-through source: authentication without an Enterprise gate on current main](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/pass_through_endpoints/pass_through_endpoints.py).
- [LiteLLM request routing: caller-supplied api_base](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/route_llm_request.py).
- [LiteLLM completion source: base_url handling](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/main.py).
- [LiteLLM logging: message redaction and custom callbacks](https://docs.litellm.ai/docs/proxy/logging).
- [LiteLLM spend-log source: configuration/environment OR condition for payload storage](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/spend_tracking/spend_tracking_utils.py).
- [LiteLLM master-key documentation: unsafe-key startup refusal and configuration precedence](https://docs.litellm.ai/docs/proxy/master_key_rotations).
- [LiteLLM startup source: master-key boot enforcement and override hook](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/proxy_server.py).
- [LiteLLM pass-through authorization: required allowed_passthrough_routes for non-admin callers](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/route_checks.py).
- [LiteLLM premium metadata fields: allowed_passthrough_routes](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/_types.py).
- [LiteLLM metadata setter: Enterprise licence enforcement](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/common_utils.py).
- [LiteLLM proxy CLI `--host` default `0.0.0.0` (pinned tag v1.102.1)](https://github.com/BerriAI/litellm/blob/v1.102.1/litellm/proxy/proxy_cli.py#L666)
