---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "8933988c612e6a7a2db2a9e1dffec9aaa89de39b36908b3e51c268e8797d61bb",
  "components": {
    "docs": {
      "name": "LiteLLM documentation",
      "basis": "unknown",
      "sources": {
        "s135f0dce83d9": "https://docs.litellm.ai/docs/proxy/virtual_keys",
        "s66efd69f5587": "https://docs.litellm.ai/docs/proxy/master_key_rotations",
        "sf9c1840fffc9": "https://docs.litellm.ai/docs/proxy/config_settings",
        "sfe517a7be891": "https://docs.litellm.ai/docs/proxy/access_control",
        "s038950d49558": "https://docs.litellm.ai/docs/proxy/key_auth_arch",
        "seb5042b85a02": "https://docs.litellm.ai/docs/proxy/users",
        "sdc6aeba6f388": "https://docs.litellm.ai/docs/proxy/team_budgets",
        "s26fc2080e183": "https://docs.litellm.ai/docs/proxy/redis_requirements",
        "sdbe6ab7362a0": "https://docs.litellm.ai/docs/proxy/cli",
        "sc420b1851bf6": "https://docs.litellm.ai/docs/proxy/ip_address",
        "sb980affae79d": "https://docs.litellm.ai/docs/proxy/ui",
        "se991dc6f2424": "https://docs.litellm.ai/docs/proxy/security_best_practices",
        "sb3839a335288": "https://docs.litellm.ai/docs/proxy/public_routes",
        "sa6aaab9c250a": "https://docs.litellm.ai/docs/proxy/health",
        "sf84e8bdc2a9c": "https://docs.litellm.ai/docs/proxy/prometheus",
        "s629597256553": "https://docs.litellm.ai/docs/proxy/pass_through",
        "s1fceb11a6977": "https://docs.litellm.ai/docs/proxy/logging"
      }
    },
    "source": {
      "name": "LiteLLM source",
      "basis": "6ef7b86748118ceecd95271727c2fa167ce55fec",
      "sources": {
        "s7960d883e823": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/proxy_server.py",
        "sbe6fa0b81017": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/user_api_key_auth.py",
        "s6dca7e865d4f": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/_types.py",
        "s801396dd889f": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/key_management_endpoints.py",
        "s6632dfcab93a": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/route_checks.py",
        "scf988bc26d27": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/utils.py",
        "s4dac61a60fa2": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/pass_through_endpoints/pass_through_endpoints.py",
        "sd13121968bd0": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/management_endpoints/common_utils.py",
        "s2260325bd6b8": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/route_llm_request.py",
        "sc93fb1082e0c": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/main.py",
        "s6ce39f96b246": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/spend_tracking/spend_tracking_utils.py"
      }
    },
    "sso": {
      "name": "LiteLLM SSO allowance",
      "basis": "v1.76.0",
      "sources": {
        "s683431f972f9": "https://docs.litellm.ai/docs/proxy/admin_ui_sso"
      }
    },
    "metrics": {
      "name": "LiteLLM metrics default",
      "basis": "v1.85.0",
      "sources": {
        "s7ae2561db315": "https://raw.githubusercontent.com/BerriAI/litellm/v1.85.0/litellm/__init__.py"
      }
    },
    "cli": {
      "name": "LiteLLM CLI",
      "basis": "v1.102.1",
      "sources": {
        "s2c55655e39fd": "https://github.com/BerriAI/litellm/blob/v1.102.1/litellm/proxy/proxy_cli.py#L666-L667"
      }
    }
  },
  "claims": {
    "master-file": {"text": "Keep operator-only master_key in protected config.yaml, not argv/exported environment; YAML wins over environment and remains plaintext at rest.", "components": ["docs"], "sources": ["docs:s135f0dce83d9", "docs:s66efd69f5587"], "status": "REASONED"},
    "startup": {"text": "Current startup refuses missing, empty, whitespace-only or sk-1234 master keys; no first release is asserted.", "components": ["docs", "source"], "sources": ["docs:s66efd69f5587", "source:s7960d883e823"], "status": "REASONED"},
    "env-override": {"text": "LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true independently allows weak/keyless startup; retain refusal in production.", "components": ["docs", "source"], "sources": ["docs:s66efd69f5587", "source:s7960d883e823"], "status": "REASONED"},
    "yaml-override": {"text": "general_settings.dangerously_permit_weak_or_unset_master_key=true independently allows weak/keyless startup.", "components": ["docs", "source"], "sources": ["docs:s66efd69f5587", "source:s7960d883e823"], "status": "REASONED"},
    "database": {"text": "Virtual-key generation requires PostgreSQL via DATABASE_URL or general_settings.database_url, even with model storage disabled.", "components": ["docs"], "sources": ["docs:s135f0dce83d9", "docs:sf9c1840fffc9"], "status": "REASONED"},
    "virtual-keys": {"text": "Issue separate revocable application keys; default Authorization header is configurable via litellm_key_header_name.", "components": ["docs"], "sources": ["docs:s135f0dce83d9"], "status": "REASONED"},
    "salt": {"text": "Stored virtual keys are hashed; database provider credentials are encrypted with LITELLM_SALT_KEY, falling back to master key; preserve the salt.", "components": ["docs"], "sources": ["docs:sf9c1840fffc9"], "status": "REASONED"},
    "model-storage": {"text": "Leave store_model_in_db false unless required; protect database credentials, backups and plaintext configuration.", "components": ["docs"], "sources": ["docs:sf9c1840fffc9"], "status": "REASONED"},
    "ownership": {"text": "Use non-admin owners with team membership; keys inherit owner authority and master keys bypass application restrictions.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:sbe6fa0b81017", "docs:sfe517a7be891"], "status": "REASONED", "verify": [2]},
    "key-models": {"text": "Explicit key and team model lists intersect; models: [] means all models, not none.", "components": ["docs"], "sources": ["docs:s038950d49558"], "status": "REASONED", "verify": [2]},
    "key-budget": {"text": "max_budget is USD and defaults null, with no key-level cap; budget_duration resets spend and does not expire the key.", "components": ["docs", "source"], "sources": ["docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "expiry": {"text": "duration controls lifetime separately; compare finite-key success before expiry/refusal afterward against an unexpired control.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "rpm": {"text": "rpm_limit limits requests per minute; test its own window and successful under-limit control across workers.", "components": ["docs", "source"], "sources": ["docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "tpm": {"text": "tpm_limit limits tokens per minute; RPM results do not demonstrate this limit.", "components": ["docs", "source"], "sources": ["docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "parallel": {"text": "max_parallel_requests limits concurrent requests; overlap a bounded workload to distinguish it from rate limits.", "components": ["docs", "source"], "sources": ["docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "soft-budget": {"text": "soft_budget triggers configured alerts without blocking spending.", "components": ["docs", "source"], "sources": ["docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED"},
    "teams": {"text": "POST team/new and team/update set shared model/spend/throughput limits; attach every relevant key and add the intended owner with team/member_add.", "components": ["docs", "source"], "sources": ["docs:sdc6aeba6f388", "docs:seb5042b85a02", "source:s6dca7e865d4f"], "status": "REASONED", "verify": [2]},
    "shared-state": {"text": "Multiple workers, even in one container, require shared Redis for limits/revocation; configure router Redis and proxy caching, not variables alone.", "components": ["docs"], "sources": ["docs:s26fc2080e183"], "status": "REASONED"},
    "cache": {"text": "The shown Redis cache configuration also caches responses; absent content logs do not imply absent cached content.", "components": ["docs"], "sources": ["docs:s26fc2080e183", "docs:sf9c1840fffc9"], "status": "REASONED"},
    "fail-closed": {"text": "fail_closed_budget_enforcement=true returns 503 when spend cannot be verified; restore dependencies and confirm permitted work.", "components": ["docs"], "sources": ["docs:seb5042b85a02"], "status": "REASONED", "verify": [2]},
    "reservation": {"text": "Keep reservation enabled; batch/unestimable costs and delayed or concurrent charges mean budgets are not absolute provider-spend caps.", "components": ["docs"], "sources": ["docs:seb5042b85a02"], "status": "REASONED"},
    "delete": {"text": "POST /key/delete permanently revokes the listed keys; removing application configuration is not revocation.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:s801396dd889f"], "status": "REASONED", "verify": [2]},
    "block": {"text": "POST /key/block suspends and /key/unblock restores; compare each operation on every worker with replacement-key positive controls.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:s801396dd889f", "docs:s26fc2080e183"], "status": "REASONED", "verify": [2]},
    "rotation": {"text": "In-place /key/regenerate is Enterprise-gated; otherwise generate restricted replacement, deploy/test it, then delete old key while retaining team budget.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:s801396dd889f"], "status": "REASONED"},
    "bind": {"text": "CLI defaults 0.0.0.0:4000; use --host 127.0.0.1 --port 4000 --config config.yaml behind TLS.", "components": ["docs", "cli"], "sources": ["docs:sdbe6ab7362a0", "cli:s2c55655e39fd"], "status": "REASONED", "verify": [1]},
    "ip-filter": {"text": "allowed_ips is Enterprise; otherwise ingress filtering must be enforced independently.", "components": ["docs"], "sources": ["docs:sc420b1851bf6"], "status": "REASONED"},
    "ui-login": {"text": "UI_USERNAME defaults admin; without UI_PASSWORD the UI accepts the master key; remove fallback with disable_env_credential_login after personal login works.", "components": ["docs"], "sources": ["docs:sb980affae79d"], "status": "REASONED", "verify": [2]},
    "ui-cookie": {"text": "Set PROXY_BASE_URL to the actual HTTPS origin for Secure UI cookies and test in a fresh browser.", "components": ["docs"], "sources": ["docs:se991dc6f2424"], "status": "REASONED", "verify": [2]},
    "ui-disable": {"text": "DISABLE_ADMIN_UI=true removes an unused UI; authorized inference must still work.", "components": ["docs"], "sources": ["docs:sb980affae79d"], "status": "REASONED", "verify": [2]},
    "sso": {"text": "SSO is free for up to five users from v1.76.0; more require Enterprise and bootstrap credentials still need removal.", "components": ["sso"], "sources": ["sso:s683431f972f9"], "status": "REASONED"},
    "mfa": {"text": "Human UI MFA belongs at the fronting identity layer.", "components": ["docs", "sso"], "sources": ["docs:se991dc6f2424", "sso:s683431f972f9"], "status": "REASONED"},
    "routes": {"text": "allowed_routes admits named paths and slash descendants, not exact path/method pairs; narrow at ingress where required.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:s6632dfcab93a"], "status": "REASONED"},
    "admin-routes": {"text": "admin_only_routes uses exact matches, not /key/*; without Enterprise source logs an error and skips this additional check.", "components": ["docs", "source"], "sources": ["docs:sb3839a335288", "source:s6632dfcab93a"], "status": "REASONED", "verify": [2]},
    "health-live": {"text": "Liveliness/liveness and readiness are unauthenticated; their success proves no inference authentication.", "components": ["docs"], "sources": ["docs:sa6aaab9c250a"], "status": "REASONED", "verify": [2]},
    "health-paid": {"text": "/health is authenticated with key auth and runs potentially paid model probes; keep it private.", "components": ["docs"], "sources": ["docs:sa6aaab9c250a"], "status": "REASONED"},
    "docs": {"text": "Docs are public by default; clear DOCS_URL/REDOC_URL/OPENAPI_URL and set NO_DOCS/NO_REDOC/NO_OPENAPI in actual startup environment; explicit URLs win.", "components": ["source", "docs"], "sources": ["source:scf988bc26d27", "docs:sf9c1840fffc9"], "status": "REASONED", "verify": [2]},
    "metrics-proxy": {"text": "Proxy-port /metrics defaults authenticated, confirmed in v1.85.0; require_auth_for_metrics_endpoint=false reopens it.", "components": ["metrics", "docs"], "sources": ["metrics:s7ae2561db315", "docs:sf84e8bdc2a9c", "docs:sf9c1840fffc9"], "status": "REASONED", "verify": [2]},
    "metrics-port": {"text": "PROMETHEUS_METRICS_PORT can create a separate unauthenticated listener; proxy-port auth does not cover it, so isolate collectors.", "components": ["docs"], "sources": ["docs:sf84e8bdc2a9c"], "status": "REASONED", "verify": [2]},
    "passthrough-auth": {"text": "Docs call pass-through auth Enterprise, but pinned main attaches auth without a licence gate; verify the installed release.", "components": ["docs", "source"], "sources": ["docs:s629597256553", "source:s4dac61a60fa2"], "status": "REASONED"},
    "passthrough-authorization": {"text": "Non-admin callers also need allowed_passthrough_routes metadata; allowed_routes alone is insufficient and normal metadata provisioning is Enterprise-gated.", "components": ["source"], "sources": ["source:s6632dfcab93a", "source:s6dca7e865d4f", "source:sd13121968bd0"], "status": "REASONED"},
    "passthrough-policy": {"text": "Optional forwarder pins target, auth, GET-only, no subpaths and no wholesale incoming-header forwarding; omit unused forwarders.", "components": ["docs", "source"], "sources": ["docs:s629597256553", "source:s4dac61a60fa2"], "status": "REASONED", "verify": [2]},
    "destinations": {"text": "Pin api_base/target and control who changes them; caller api_base/base_url overrides still need trusted validation and independent egress controls.", "components": ["source"], "sources": ["source:s2260325bd6b8", "source:sc93fb1082e0c"], "status": "REASONED", "verify": [2]},
    "message-logging": {"text": "turn_off_message_logging suppresses content in supported integrations while retaining operational metadata; arbitrary callbacks need separate review.", "components": ["docs"], "sources": ["docs:s1fceb11a6977"], "status": "REASONED", "verify": [2]},
    "spend-logging": {"text": "Either store_prompts_in_spend_logs or STORE_PROMPTS_IN_SPEND_LOGS enables payload storage; YAML false does not override environment true.", "components": ["source"], "sources": ["source:s6ce39f96b246"], "status": "REASONED", "verify": [2]},
    "debug-logging": {"text": "Avoid detailed_debug and LITELLM_LOG=DEBUG; inspect process, error, callback and proxy logs with canaries and positive log controls.", "components": ["docs"], "sources": ["docs:sdbe6ab7362a0", "docs:sf9c1840fffc9", "docs:s1fceb11a6977"], "status": "REASONED", "verify": [2]},
    "verify-auth": {"text": "Probe backend directly: absent/wrong keys must get 401 and valid key a model list; public proxy responses alone cannot prove backend auth.", "components": ["docs", "source"], "sources": ["docs:s135f0dce83d9", "source:sbe6fa0b81017"], "status": "REASONED", "verify": [1]},
    "verify-network": {"text": "Inspect every listener and actual external backend reachability; refusal must be attributable to the intended remote path, not DNS/local errors.", "components": ["docs", "cli"], "sources": ["docs:sdbe6ab7362a0", "cli:s2c55655e39fd"], "status": "REASONED", "verify": [1]},
    "verify-spend": {"text": "Use bounded uncached provider calls; exhaust key and aggregate team budgets separately with successful controls and record overshoot.", "components": ["docs"], "sources": ["docs:seb5042b85a02", "docs:sdc6aeba6f388"], "status": "REASONED", "verify": [2]},
    "verify-admin": {"text": "Application key must fail a valid management request that operator credentials complete; licensed/unlicensed admin-route cases are separate.", "components": ["docs", "source"], "sources": ["docs:sfe517a7be891", "source:s6632dfcab93a"], "status": "REASONED", "verify": [2]},
    "verify-forwarding": {"text": "Require anonymous refusal and permitted authenticated GET; wrong method/subpath must not reach the controlled upstream.", "components": ["docs", "source"], "sources": ["docs:s629597256553", "source:s4dac61a60fa2"], "status": "REASONED", "verify": [2]},
    "verify-egress": {"text": "Compare api_base and base_url overrides separately against a controlled sink; no contact plus working pinned destination establishes the intended boundary.", "components": ["source"], "sources": ["source:s2260325bd6b8", "source:sc93fb1082e0c"], "status": "REASONED", "verify": [2]}
  }
}
---
# LiteLLM proxy: master key and virtual keys

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| master-file: Keep operator-only master_key in protected config.yaml, not argv/exported environment; YAML wins over environment and remains plaintext at rest. | LiteLLM documentation unknown | REASONED |
| startup: Current startup refuses missing, empty, whitespace-only or sk-1234 master keys; no first release is asserted. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| env-override: LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true independently allows weak/keyless startup; retain refusal in production. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| yaml-override: general_settings.dangerously_permit_weak_or_unset_master_key=true independently allows weak/keyless startup. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| database: Virtual-key generation requires PostgreSQL via DATABASE_URL or general_settings.database_url, even with model storage disabled. | LiteLLM documentation unknown | REASONED |
| virtual-keys: Issue separate revocable application keys; default Authorization header is configurable via litellm_key_header_name. | LiteLLM documentation unknown | REASONED |
| salt: Stored virtual keys are hashed; database provider credentials are encrypted with LITELLM_SALT_KEY, falling back to master key; preserve the salt. | LiteLLM documentation unknown | REASONED |
| model-storage: Leave store_model_in_db false unless required; protect database credentials, backups and plaintext configuration. | LiteLLM documentation unknown | REASONED |
| ownership: Use non-admin owners with team membership; keys inherit owner authority and master keys bypass application restrictions. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| key-models: Explicit key and team model lists intersect; models: [] means all models, not none. | LiteLLM documentation unknown | REASONED |
| key-budget: max_budget is USD and defaults null, with no key-level cap; budget_duration resets spend and does not expire the key. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| expiry: duration controls lifetime separately; compare finite-key success before expiry/refusal afterward against an unexpired control. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| rpm: rpm_limit limits requests per minute; test its own window and successful under-limit control across workers. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| tpm: tpm_limit limits tokens per minute; RPM results do not demonstrate this limit. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| parallel: max_parallel_requests limits concurrent requests; overlap a bounded workload to distinguish it from rate limits. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| soft-budget: soft_budget triggers configured alerts without blocking spending. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| teams: POST team/new and team/update set shared model/spend/throughput limits; attach every relevant key and add the intended owner with team/member_add. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| shared-state: Multiple workers, even in one container, require shared Redis for limits/revocation; configure router Redis and proxy caching, not variables alone. | LiteLLM documentation unknown | REASONED |
| cache: The shown Redis cache configuration also caches responses; absent content logs do not imply absent cached content. | LiteLLM documentation unknown | REASONED |
| fail-closed: fail_closed_budget_enforcement=true returns 503 when spend cannot be verified; restore dependencies and confirm permitted work. | LiteLLM documentation unknown | REASONED |
| reservation: Keep reservation enabled; batch/unestimable costs and delayed or concurrent charges mean budgets are not absolute provider-spend caps. | LiteLLM documentation unknown | REASONED |
| delete: POST /key/delete permanently revokes the listed keys; removing application configuration is not revocation. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| block: POST /key/block suspends and /key/unblock restores; compare each operation on every worker with replacement-key positive controls. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| rotation: In-place /key/regenerate is Enterprise-gated; otherwise generate restricted replacement, deploy/test it, then delete old key while retaining team budget. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| bind: CLI defaults 0.0.0.0:4000; use --host 127.0.0.1 --port 4000 --config config.yaml behind TLS. | LiteLLM documentation unknown; LiteLLM CLI v1.102.1 | REASONED |
| ip-filter: allowed_ips is Enterprise; otherwise ingress filtering must be enforced independently. | LiteLLM documentation unknown | REASONED |
| ui-login: UI_USERNAME defaults admin; without UI_PASSWORD the UI accepts the master key; remove fallback with disable_env_credential_login after personal login works. | LiteLLM documentation unknown | REASONED |
| ui-cookie: Set PROXY_BASE_URL to the actual HTTPS origin for Secure UI cookies and test in a fresh browser. | LiteLLM documentation unknown | REASONED |
| ui-disable: DISABLE_ADMIN_UI=true removes an unused UI; authorized inference must still work. | LiteLLM documentation unknown | REASONED |
| sso: SSO is free for up to five users from v1.76.0; more require Enterprise and bootstrap credentials still need removal. | LiteLLM SSO allowance v1.76.0 | REASONED |
| mfa: Human UI MFA belongs at the fronting identity layer. | LiteLLM documentation unknown; LiteLLM SSO allowance v1.76.0 | REASONED |
| routes: allowed_routes admits named paths and slash descendants, not exact path/method pairs; narrow at ingress where required. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| admin-routes: admin_only_routes uses exact matches, not /key/*; without Enterprise source logs an error and skips this additional check. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| health-live: Liveliness/liveness and readiness are unauthenticated; their success proves no inference authentication. | LiteLLM documentation unknown | REASONED |
| health-paid: /health is authenticated with key auth and runs potentially paid model probes; keep it private. | LiteLLM documentation unknown | REASONED |
| docs: Docs are public by default; clear DOCS_URL/REDOC_URL/OPENAPI_URL and set NO_DOCS/NO_REDOC/NO_OPENAPI in actual startup environment; explicit URLs win. | LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec; LiteLLM documentation unknown | REASONED |
| metrics-proxy: Proxy-port /metrics defaults authenticated, confirmed in v1.85.0; require_auth_for_metrics_endpoint=false reopens it. | LiteLLM metrics default v1.85.0; LiteLLM documentation unknown | REASONED |
| metrics-port: PROMETHEUS_METRICS_PORT can create a separate unauthenticated listener; proxy-port auth does not cover it, so isolate collectors. | LiteLLM documentation unknown | REASONED |
| passthrough-auth: Docs call pass-through auth Enterprise, but pinned main attaches auth without a licence gate; verify the installed release. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| passthrough-authorization: Non-admin callers also need allowed_passthrough_routes metadata; allowed_routes alone is insufficient and normal metadata provisioning is Enterprise-gated. | LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| passthrough-policy: Optional forwarder pins target, auth, GET-only, no subpaths and no wholesale incoming-header forwarding; omit unused forwarders. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| destinations: Pin api_base/target and control who changes them; caller api_base/base_url overrides still need trusted validation and independent egress controls. | LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| message-logging: turn_off_message_logging suppresses content in supported integrations while retaining operational metadata; arbitrary callbacks need separate review. | LiteLLM documentation unknown | REASONED |
| spend-logging: Either store_prompts_in_spend_logs or STORE_PROMPTS_IN_SPEND_LOGS enables payload storage; YAML false does not override environment true. | LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| debug-logging: Avoid detailed_debug and LITELLM_LOG=DEBUG; inspect process, error, callback and proxy logs with canaries and positive log controls. | LiteLLM documentation unknown | REASONED |
| verify-auth: Probe backend directly: absent/wrong keys must get 401 and valid key a model list; public proxy responses alone cannot prove backend auth. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| verify-network: Inspect every listener and actual external backend reachability; refusal must be attributable to the intended remote path, not DNS/local errors. | LiteLLM documentation unknown; LiteLLM CLI v1.102.1 | REASONED |
| verify-spend: Use bounded uncached provider calls; exhaust key and aggregate team budgets separately with successful controls and record overshoot. | LiteLLM documentation unknown | REASONED |
| verify-admin: Application key must fail a valid management request that operator credentials complete; licensed/unlicensed admin-route cases are separate. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| verify-forwarding: Require anonymous refusal and permitted authenticated GET; wrong method/subpath must not reach the controlled upstream. | LiteLLM documentation unknown; LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
| verify-egress: Compare api_base and base_url overrides separately against a controlled sink; no contact plus working pinned destination establishes the intended boundary. | LiteLLM source 6ef7b86748118ceecd95271727c2fa167ce55fec | REASONED |
<!-- version-basis:end -->

A LiteLLM proxy fronts paid model APIs, so an exposed, keyless instance spends your provider credits for whoever finds it. Authentication is built in and must be switched on before anything else.

## 1. Set the master key

Set `general_settings.master_key` in the `config.yaml` that LiteLLM reads. Provision that file with mode `0600`, owned by the service account, in a directory other accounts cannot modify. Merge this setting into the existing configuration rather than replacing its model and database settings:

```yaml
general_settings:
  master_key: sk-REPLACE_WITH_LONG_RANDOM_VALUE
```

The master key is the root credential for the proxy; it belongs to the operator only and never to client applications. Have your secret store generate 32 random bytes encoded as hex with an `sk-` prefix and write the value into the protected file, replacing the placeholder before startup. Do not paste the key into a shell command or export `LITELLM_MASTER_KEY`. LiteLLM reads the key from the file, keeping it out of launch argv and the process environment. The file is plaintext and remains readable by the service account, root and any backup that copies it; keep it and editor backups out of version control ([secrets.md](secrets.md)). When both the environment and `config.yaml` set the master key, the `config.yaml` value wins.

At the time of writing, current LiteLLM refuses to start when the resolved master key is unset, empty or whitespace-only, or `sk-1234`. Either `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true` or the YAML setting `general_settings.dangerously_permit_weak_or_unset_master_key: true` permits weak or keyless startup independently; keep both overrides absent or false in production. Older releases and overridden deployments can still operate without authentication, so the unauthenticated-deployment warning above remains relevant. A startup refusal is a protection to retain, not a reason to enable the override. No first release is asserted here. See [master-key startup protection](https://docs.litellm.ai/docs/proxy/master_key_rotations) and the [current startup enforcement call](https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/proxy_server.py).

## 2. Issue virtual keys per application

Virtual keys need a PostgreSQL database: set `DATABASE_URL=postgresql://user:password@host:5432/dbname` in the environment (or `database_url` under `general_settings`) before `/key/generate` will work.

The original alias-only request below illustrates issuance and attribution. It does not establish least privilege: use the restricted request body below for application keys. This block assumes a clean Bash shell. Substitute your actual HTTPS origin inside the single quotes (an apostrophe needs shell escaping), paste the whole block, and enter the master key at the hidden prompt. The key stays in an unexported subshell variable, is sent to curl on stdin, and is unset on exit; no ambient master key is used. The response contains the newly issued virtual key, so keep the output private.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -o pipefail
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_ORIGIN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'expected HTTPS origin'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*example.com*|*example.net*|*example.org*|*[[:cntrl:]]*) echo 'replace the origin placeholder'; exit 2 ;;
  esac
  case "$1" in https://?*) ;; *) echo 'HTTPS origin required'; exit 2 ;; esac
  { unset -n LITELLM_MASTER_KEY && unset -v LITELLM_MASTER_KEY; } 2>/dev/null ||
    { echo 'cannot clear LITELLM_MASTER_KEY in this shell'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell'; exit 2; }
  trap 'unset -v LITELLM_MASTER_KEY' EXIT
  printf 'LiteLLM master key (input hidden): '
  IFS= read -r -s LITELLM_MASTER_KEY || { printf '\n'; echo 'no secret read'; exit 2; }
  printf '\n'
  case "$LITELLM_MASTER_KEY" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty secret, placeholder or control character'; exit 2 ;;
  esac
  printf 'Authorization: Bearer %s\n' "$LITELLM_MASTER_KEY" | curl -q -g "$1/key/generate" \
    -H @- \
    -H "Content-Type: application/json" \
    -d '{"key_alias": "app-frontend"}'
)
```

Each app gets its own virtual key, which can be revoked or budgeted independently; LiteLLM's docs cover per-key models, budgets, and expiry. Clients send the virtual key in the `Authorization` header (the header name is configurable via `litellm_key_header_name`).

Putting the key in curl's `-H` argument would expose it through `/proc/<pid>/cmdline`. The prompt above and stdin header avoid that exposure and keep the entered key out of shell history and tracing. They do not hide process memory from the same account or root, or erase an earlier export. The Verify blocks below also pass headers on stdin. Virtual keys are stored hashed, but the provider API keys LiteLLM persists when `general_settings.store_model_in_db` is on are ENCRYPTED with `LITELLM_SALT_KEY` (which falls back to the master key when unset): set a permanent `LITELLM_SALT_KEY` BEFORE adding any credential, because changing it later strands what it encrypted, and protect the database and its backups as the store of those secrets. A credential written literally into `config.yaml` stays plaintext in that file, so keep it out of version control ([secrets.md](secrets.md)).

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

### Backend authentication and listener exposure (REASONED: cited LiteLLM auth and CLI behavior; no service or second-host fixture)

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

**REASONED:** following block; requests follow the cited LiteLLM endpoint documentation; the live service and test credentials are unavailable.

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

### REASONED service checks

The checks below remain REASONED from the cited LiteLLM documentation and pinned sources. Service behavior in this replacement is not demonstrated.

| Scope | Exposed/fixed checks and prerequisites | Status |
| --- | --- | --- |
| LiteLLM controls | Check every REASONED comparison above on a pinned LiteLLM release with PostgreSQL, shared Redis, at least two workers, approved provider test credentials, and a second-host ingress fixture. Cover backend authentication and actual inference; IPv4/IPv6 and container publication; key/team model intersections; key and aggregate team spend; RPM, TPM, and parallel limits; budget verification failures and batch/unestimable-route limitations; expiry, block/unblock, delete, and replacement across workers; application/admin separation and licensed/unlicensed route behavior; documentation URL overrides; health and both metrics listeners; UI fallback removal and Secure cookies; pass-through authentication, methods, subpaths, and headers; destination overrides and egress evidence; and prompt/response absence across spend, debug, error, and callback logs. Include isolated startup tests for unsafe master keys with both overrides absent or false, then with `LITELLM_DANGEROUSLY_PERMIT_WEAK_OR_UNSET_MASTER_KEY=true` and YAML `general_settings.dangerously_permit_weak_or_unset_master_key: true` enabled independently. Record versions, commands, diagnostics, positive controls, propagation timing, costs, and cleanup. Configuration inspection alone does not demonstrate service behavior. | REASONED from the cited documentation and pinned sources; service behavior is not demonstrated. |

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
- [LiteLLM proxy CLI `--host` default `0.0.0.0` (pinned tag v1.102.1)](https://github.com/BerriAI/litellm/blob/v1.102.1/litellm/proxy/proxy_cli.py#L666-L667)
