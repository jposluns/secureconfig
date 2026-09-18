# LiteLLM proxy: master key and virtual keys

A LiteLLM proxy fronts paid model APIs, so an exposed, keyless instance spends your provider credits for whoever finds it. Authentication is built in and must be switched on before anything else.

## 1. Set the master key

In `config.yaml` under `general_settings: master_key`, or via the environment (preferred; see [secrets.md](secrets.md)):

```bash
export LITELLM_MASTER_KEY="sk-REPLACE_WITH_LONG_RANDOM_VALUE"   # must start with sk-
```

The master key is the root credential for the proxy; it belongs to the operator only and never to client applications. Generate it with `openssl rand -hex 32` (kept behind the `sk-` prefix), and inject it from your secret store or a root-only environment file rather than typing the `export` above into an interactive shell, where it is captured in shell history and readable in `/proc/<pid>/environ` ([secrets.md](secrets.md)). When both the environment and `config.yaml` set the master key, the `config.yaml` value wins.

## 2. Issue virtual keys per application

Virtual keys need a PostgreSQL database: set `DATABASE_URL=postgresql://user:password@host:5432/dbname` in the environment (or `database_url` under `general_settings`) before `/key/generate` will work.

```bash
printf 'Authorization: Bearer %s\n' "$LITELLM_MASTER_KEY" | curl -q https://llm.example.com/key/generate \
  -H @- \
  -H "Content-Type: application/json" \
  -d '{"key_alias": "app-frontend"}'
```

Each app gets its own virtual key, which can be revoked or budgeted independently; LiteLLM's docs cover per-key models, budgets, and expiry. Clients send the virtual key in the `Authorization` header (the header name is configurable via `litellm_key_header_name`).

The `$LITELLM_MASTER_KEY` in the request above is expanded into curl's arguments, where it is readable in `/proc/<pid>/cmdline` while it runs (shell history keeps the literal `$LITELLM_MASTER_KEY`, not its value); on a shared host feed the header to curl on stdin instead, as the request above and the Verify below do: `printf 'Authorization: Bearer %s\n' "$LITELLM_MASTER_KEY" | curl -H @- ...`. Virtual keys are stored hashed, but the provider API keys LiteLLM persists when `general_settings.store_model_in_db` is on are ENCRYPTED with `LITELLM_SALT_KEY` (which falls back to the master key when unset): set a permanent `LITELLM_SALT_KEY` BEFORE adding any credential, because changing it later strands what it encrypted, and protect the database and its backups as the store of those secrets. A credential written literally into `config.yaml` stays plaintext in that file, so keep it out of version control ([secrets.md](secrets.md)).

## 3. Bind privately and add TLS in front

Run the proxy on loopback (or a private container network) and publish it only through a TLS layer: [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or [cloudflare.md](cloudflare.md)/[tailscale.md](tailscale.md) for no-open-port setups. The proxy's `--host` defaults to `0.0.0.0`, so bind it explicitly: `litellm --host 127.0.0.1 --port 4000 --config config.yaml`. The Verify check below confirms it is on loopback. Bearer keys over plain HTTP are compromised on first use. For human access to the LiteLLM admin UI, add MFA at the fronting layer ([mfa.md](mfa.md)).

## 4. Admin UI, routes, and outbound destinations

The admin UI at `/ui` has its own login, separate from inference auth: `UI_USERNAME` defaults to `admin`, and with no `UI_PASSWORD` set the UI accepts the master key itself. Set individual admin logins or SSO, then set `general_settings.disable_env_credential_login: true` and restart so the shared bootstrap login (the env `UI_USERNAME`/master-key credential) stops working, since creating personal logins does not by itself disable it; or disable an unused UI entirely with `DISABLE_ADMIN_UI="True"`. Set `PROXY_BASE_URL` to the public `https://` origin so the UI's session cookies are marked `Secure` when TLS terminates at the proxy in front.

Not every route sits behind the key. `/health/liveliness` (and `/health/liveness`) are unauthenticated worker checks, and the docs routes (`/`, `/redoc`, `/openapi.json`) are public by default, so a reply from any of them proves nothing about inference auth; `/health` is authenticated when key auth is on. `/metrics` is authenticated by default since v1.85.0 (only `litellm_settings.require_auth_for_metrics_endpoint: false` reopens it) and exposes spend and operational labels, not provider keys. Restrict the routes you do not need at the fronting proxy.

A model's `api_base` and any pass-through `target` are outbound destinations the proxy will call, so a config that lets the wrong person add them is an SSRF and egress path: restrict who may change destinations and constrain the proxy's egress ([egress-metadata.md](egress-metadata.md)); pass-through route authentication is an Enterprise feature.

## 5. Verify

```bash
# Test LiteLLM's OWN auth against the BACKEND directly on loopback, with no fronting proxy in the path,
# three ways: with no key and with a WRONG key LiteLLM must refuse (401); with a VALID virtual key it
# returns the model list. A gateway that answers 401 and then forwards a header-bearing request to a
# keyless proxy would pass a public-edge test, so probe the backend. The valid key is fed to curl on
# STDIN (-H @-) so it never enters curl's arguments, a temp file, or a shell variable; the guard refuses
# on a placeholder. (The key you substitute on the set -- line does enter your shell history, so use a
# short-lived key or clear that history line afterward.)
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VIRTUAL_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the virtual key on the set -- line above; not probing"; exit 1 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'no-key=%{http_code} exit=%{exitcode}\n' http://127.0.0.1:4000/v1/models
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'bad-key=%{http_code} exit=%{exitcode}\n' -H 'Authorization: Bearer sk-not-a-real-key' http://127.0.0.1:4000/v1/models
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -w '\ngood-key=%{http_code} exit=%{exitcode}\n' -H @- http://127.0.0.1:4000/v1/models
)
# Expected: no-key and bad-key => 401 from LiteLLM; good-key => 200 with the model list (a 200 without a
# key is the finding). Then repeat the good-key request through the public https ingress to confirm the
# TLS front works. A transport error (exit != 0) is inconclusive, not a pass.
ss -tlnp   # a listener inventory in THIS network namespace, not a firewall/NAT/publication check:
           # confirm 4000 is loopback-only here, then from ANOTHER host confirm 4000 is refused
           # externally (a Docker DNAT publication need not appear in this list at all).
```

## Sources (checked September 2026)

- LiteLLM proxy virtual keys (master_key, /key/generate, header name): https://docs.litellm.ai/docs/proxy/virtual_keys
- LiteLLM proxy CLI (`--host` default `0.0.0.0`, `--port` default `4000`): https://docs.litellm.ai/docs/proxy/cli
- LiteLLM admin UI (`UI_USERNAME`/`UI_PASSWORD`, master-key fallback, `DISABLE_ADMIN_UI`): https://docs.litellm.ai/docs/proxy/ui
- LiteLLM security best practices (route exposure, `PROXY_BASE_URL` and `Secure` cookies): https://docs.litellm.ai/docs/proxy/security_best_practices
- LiteLLM config settings (`store_model_in_db`, `LITELLM_SALT_KEY`, `require_auth_for_metrics_endpoint`): https://docs.litellm.ai/docs/proxy/config_settings
- LiteLLM Prometheus metrics (authenticated by default): https://docs.litellm.ai/docs/proxy/prometheus
- LiteLLM pass-through endpoints (`target`, Enterprise auth): https://docs.litellm.ai/docs/proxy/pass_through
