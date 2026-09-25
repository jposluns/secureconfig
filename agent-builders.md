# Agent and workflow builders: Dify, Flowise, Langflow, LibreChat

Each of these tools stores your provider API keys (OpenAI, Anthropic, and the rest) and exposes both an editor UI and callable APIs, so an open instance is a secrets vault plus free compute for whoever finds it. All four ship with login of some kind; the exposure comes from skipping the first-run setup, leaving default secrets in place, and publishing the container port on every interface over plain HTTP. And because each one runs user-authored flows with custom-code and HTTP-request/tool nodes, the editor is effectively code-execution and server-side-request authority on the host, so authentication decides who gets in but does not contain what a flow can then run or reach (section 8, [egress-metadata.md](egress-metadata.md)). None of them offers a native second factor that this guide can rely on, so MFA comes from an OIDC provider (where the tool supports OIDC) or from the fronting layer ([mfa.md](mfa.md)).

## 1. Bind privately

Publish the container on loopback and let a proxy or tunnel be the only public listener ([docker.md](docker.md)). This belongs in the service's own Compose file. If you put it in an override file beside a vendor Compose file instead, it will not replace what that file publishes: an override `ports` list merges with the base list, so use the `!reset` form shown for Dify below.

```yaml
ports:
  - "127.0.0.1:3000:3000"    # Flowise (PORT defaults to 3000)
  - "127.0.0.1:7860:7860"    # Langflow (LANGFLOW_PORT defaults to 7860)
  - "127.0.0.1:3080:3080"    # LibreChat (PORT defaults to 3080)
```

Those three also ship an official Compose file that publishes the app port on all interfaces by default (`${PORT}:${PORT}` for Flowise and LibreChat, `7860:7860` for Langflow), and LibreChat's is meant to be extended through a `docker-compose.override.yaml` rather than edited; LibreChat's file also publishes an `admin-panel` on `${ADMIN_PANEL_PORT:-3000}:3000`, so treat that mapping the same way. An override `ports` list merges with the base list, so a loopback entry added beside a base `${PORT}:${PORT}` leaves the base publication in place; move a port to loopback by replacing the list with `ports: !override ["127.0.0.1:3000:3000"]` (using the tool's own port), which supersedes the base (`!override` needs Docker Compose 2.24.4 or newer and `!reset` a little earlier, so treat 2.24.4+ as the prerequisite for both; check `docker compose version`). The `!reset []` form used for Dify below does a different job: it clears a publication a service should not have at all, rather than moving one to loopback. Langflow's example Compose also publishes PostgreSQL on `5432:5432` beside the app; leave that backing store unpublished on the Compose network or loopback-scope it, as shown in [ai-infra-services.md](ai-infra-services.md).

Dify is different: its Compose file publishes nginx on `EXPOSE_NGINX_PORT=80` and `EXPOSE_NGINX_SSL_PORT=443` from `docker/.env`, plus the plugin daemon's `EXPOSE_PLUGIN_DEBUGGING_PORT=5003` (optional vector store profiles publish more). Do not hide a published port with the host firewall: Docker's NAT rules divert the traffic before it reaches the chains UFW uses, so a UFW deny on a published port does nothing ([docker.md](docker.md)). The plugin daemon's debugging port is only needed for remote plugin debugging, and no setting turns it off: the Compose file publishes `${EXPOSE_PLUGIN_DEBUGGING_PORT:-5003}` for `plugin_daemon` unconditionally, with no host address in the mapping, so it binds `0.0.0.0:5003`. `EXPOSE_PLUGIN_DEBUGGING_HOST=localhost` does not restrict that bind; it only tells the plugin client where to connect. Remove the publication with an override file (see below). Leave the backend services unpublished on the Compose network, and make Dify's nginx the only service with a public port: either as the TLS edge (section 2) or on loopback (`EXPOSE_NGINX_PORT=127.0.0.1:8080`) behind your own proxy. The Compose file publishes `EXPOSE_NGINX_SSL_PORT` as well, and unconditionally, so give that the same host address too. Turning `NGINX_HTTPS_ENABLED` off does not help: it stops nginx serving TLS, it does not remove Docker's publication, which is the same trap as the plugin daemon's port above. The same shape appears in other AI-infrastructure deployments, where an authenticated front door sits beside a published backing store; [ai-infra-services.md](ai-infra-services.md) documents it.

```yaml
# docker-compose.override.yaml, beside docker-compose.yaml; plain `docker compose up -d` picks it up
services:
  plugin_daemon:
    ports: !reset []   # an ordinary ports list would merge with the base file's list, not replace it
```

Confirm the result against the merged model with `docker compose config`, which must show no published port for `plugin_daemon`.

## 2. TLS

Flowise and LibreChat document no TLS of their own; their deployment guides put nginx with certbot in front (`proxy_pass http://localhost:3000` and `http://localhost:3080` respectively). Use [caddy.md](caddy.md) or [nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or [cloudflare.md](cloudflare.md) / [tailscale.md](tailscale.md) with no public port at all. Set `NUMBER_OF_PROXIES` (Flowise) and `TRUST_PROXY` (LibreChat, default `1`) to the number of proxy hops so rate limiting sees client addresses.

Langflow can terminate TLS itself with `LANGFLOW_SSL_CERT_FILE` and `LANGFLOW_SSL_KEY_FILE`; a fronting proxy remains the simpler place to add login and MFA. Behind HTTPS, also set `LANGFLOW_ACCESS_SECURE=true` and `LANGFLOW_REFRESH_SECURE=true`: both default to `false`, so the access and refresh session cookies are issued without the `Secure` flag until you do.

Dify's bundled nginx can terminate TLS. In `docker/.env`, per the certbot README in the Dify repository: set `NGINX_ENABLE_CERTBOT_CHALLENGE=true`, `CERTBOT_DOMAIN`, `CERTBOT_EMAIL`, `NGINX_SSL_CERT_FILENAME=fullchain.pem`, `NGINX_SSL_CERT_KEY_FILENAME=privkey.pem`; run `docker compose --profile certbot up --force-recreate -d` and `docker compose exec -it certbot /bin/sh /update-cert.sh`; then set `NGINX_HTTPS_ENABLED=true` (default `false`) and recreate nginx with `docker compose --profile certbot up -d --no-deps --force-recreate nginx`. `NGINX_SSL_PROTOCOLS` defaults to `TLSv1.2 TLSv1.3`. Set `CONSOLE_API_URL`, `CONSOLE_WEB_URL`, and `APP_WEB_URL` to the public `https://` URLs; per the Dify reference, `CONSOLE_API_URL` decides whether cookies are marked HTTPS-only.

## 3. Dify

```bash
cd dify/docker && cp .env.example .env
# edit .env now: INIT_PASSWORD, SECRET_KEY, the default service credentials (next bullet), the EXPOSE_* bindings (section 1), the public URLs (section 2)
docker compose up -d
```

- `INIT_PASSWORD=REPLACE_WITH_LONG_RANDOM_VALUE` goes into `.env` before the first `up`. It is empty by default; when set, the `/install` page demands it before anyone can create the admin account. Once the stack is up, open `https://dify.example.com/install` yourself, immediately.
- Set `SECRET_KEY` from `openssl rand -base64 42`. It signs session cookies and JWTs and encrypts stored OAuth credentials (left empty, Dify auto-generates one in its storage directory, per `.env.example`).
- Console self-registration is off by default (`ALLOW_REGISTER=false`); leave it false for an invite-only console and add members by invitation. This governs ordinary self-registration AFTER setup: workspace invitations and the `/install` setup wizard always work regardless, so the protection for an unclaimed install is still `INIT_PASSWORD` plus claiming `/install` privately (above), not this switch.
- Replace the shipped SERVICE credentials in `.env`, not just `SECRET_KEY`: `docker/.env.example` ships working defaults that authenticate Dify's internal services, and `SECRET_KEY` (empty, auto-generated) does not cover them. Change `DB_PASSWORD` and `REDIS_PASSWORD` (both `difyai123456`; `CELERY_BROKER_URL` embeds the Redis password, so update it in lockstep), the sandbox pair `CODE_EXECUTION_API_KEY`/`SANDBOX_API_KEY` (both `dify-sandbox`, keep them equal), `PLUGIN_DAEMON_KEY` and `PLUGIN_DIFY_INNER_API_KEY`, and the agent keys `DIFY_AGENT_API_TOKEN` and `DIFY_AGENT_SERVER_SECRET_KEY` (the last one's known default lets anyone forge agent tokens; replace it with unpadded base64url of 32 random bytes). If you enable the Weaviate vector store, also rotate `WEAVIATE_API_KEY` together with `WEAVIATE_AUTHENTICATION_APIKEY_ALLOWED_KEYS` and turn off `WEAVIATE_AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED`.
- App API keys are created inside each app and sent as `Authorization: Bearer <key>` to the service API. They are not console accounts, so tightening console login does nothing for a leaked key. Dify's guidance: call the API from your backend only; a key in frontend code can be extracted.

## 4. Flowise

- From v3.0.1 onwards Flowise uses email-and-password accounts with JWTs in HTTP-only cookies. `FLOWISE_USERNAME` / `FLOWISE_PASSWORD` are documented as deprecated; the docs use them only to migrate an older instance into a new admin account. Register the admin account before exposing the instance.
- Set random values for `JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`, `EXPRESS_SESSION_SECRET` (default `flowise`), and `TOKEN_HASH_SECRET`; set `APP_URL` to the public URL (default `http://localhost:3000`). `FLOWISE_SECRETKEY_OVERWRITE` sets the key that encrypts stored credentials; without it the key lives in a file under `SECRETKEY_PATH`.
- Prediction endpoints: a chatflow with no API key assigned is public to anyone who knows the chatflow ID. Create keys under **API Keys** (a `DefaultKey` is pre-created), assign one per chatflow, and clients send `Authorization: Bearer <key>`; the prediction API answers `401` without it.

## 5. Langflow

```
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=REPLACE_WITH_ADMIN_USERNAME
LANGFLOW_SUPERUSER_PASSWORD=REPLACE_WITH_LONG_RANDOM_VALUE
LANGFLOW_SECRET_KEY=REPLACE_WITH_LONG_RANDOM_VALUE
```

- `LANGFLOW_AUTO_LOGIN` defaults to `True` in the application (the official Docker images set it to `false`), which means no login at all; set it to `false` explicitly. The password is then required and cannot be the legacy default `langflow`; the username defaults to `langflow`.
- Generate the key with `python3 -c "from secrets import token_urlsafe; print(f'LANGFLOW_SECRET_KEY={token_urlsafe(32)}')"`. An auto-generated key is documented as unsuitable for production.
- `LANGFLOW_NEW_USER_IS_ACTIVE` defaults to `False`, so a new account waits for superuser activation, but public signup is still OPEN by default (`ENABLE_SIGNUP` is `True`), letting inactive accounts accumulate; set `LANGFLOW_ENABLE_SIGNUP=false` to close registration outright and keep `LANGFLOW_NEW_USER_IS_ACTIVE=False` as the backstop.
- With auto-login off, API calls (`POST /api/v1/run/<flow-id>`) need a Langflow API key in the `x-api-key` header, created under **Settings > Langflow API Keys** or with `langflow api-key`. `LANGFLOW_SKIP_AUTH_AUTO_LOGIN` (default `false`) only applies when auto-login is on and is slated for removal; leave it alone.
- `LANGFLOW_HOST` defaults to `localhost`, which is right only when Langflow runs directly on the host behind a same-host proxy; INSIDE a bridged Docker container `localhost` binds the container's own loopback, so a host proxy hitting the published port reaches nothing. In a container set `LANGFLOW_HOST=0.0.0.0` and publish to host loopback (`127.0.0.1:7860:7860`, section 1). These `LANGFLOW_*` settings must also be injected into the container through Compose (`env_file:` or `environment:`), not merely written to a `.env` the app never reads. Version note: checked against the 1.12.x docs.

## 6. LibreChat

- The first registered account becomes the admin. Register it, then set `ALLOW_REGISTRATION=false` so nobody else can create an email account. For SSO-only operation, also set `ALLOW_EMAIL_LOGIN=false` and enable `ALLOW_SOCIAL_REGISTRATION=true` deliberately, with the provider's allowlist deciding who may exist.
- `ALLOW_SOCIAL_LOGIN=true` enables the OAuth2 providers (Apple, Discord, Facebook, GitHub, Google) and OIDC through `OPENID_ISSUER`, `OPENID_CLIENT_ID`, `OPENID_CLIENT_SECRET`, `OPENID_SESSION_SECRET`, `OPENID_SCOPE="openid profile email"`, `OPENID_CALLBACK_URL=/oauth/openid/callback`, optionally `OPENID_REQUIRED_ROLE`. The docs cover Keycloak, Authentik, Authelia, Auth0, Cognito, and Entra; with OIDC in place, set `ALLOW_EMAIL_LOGIN=false` and enforce MFA at the provider ([identity-providers.md](identity-providers.md), [oidc-integration.md](oidc-integration.md)).
- `CREDS_KEY` is a 32-byte key (64 hexadecimal characters) and `CREDS_IV` a 16-byte IV (32 hexadecimal characters); `JWT_SECRET` and `JWT_REFRESH_SECRET` are unique random values of at least 32 bytes each. The docs point to the Credentials Generator. The current `.env.example` leaves these blank (a missing value makes LibreChat bootstrap a random key, persisted only if it can write and keep its credentials file, otherwise process-local and lost on restart), and it refuses to start if you paste a retired published `JWT_SECRET`/`JWT_REFRESH_SECRET` default; set your own permanent production values so the secrets are known, backed up, and stable across restarts.
- Set `DOMAIN_CLIENT` and `DOMAIN_SERVER` to the public `https://` URL. TLS comes from the fronting proxy (section 2).
- The v0.7.7 changelog lists two-factor authentication with backup codes and QR enrolment, but the authentication documentation we checked does not describe it, so do not count on it as the enforced control; MFA at the OIDC provider is the documented path.

## 7. MFA and stored secrets

None of the four documents instance-wide MFA enforcement. Where OIDC exists (LibreChat), enforce MFA at the provider; for Dify, Flowise, and Langflow put the editor behind Cloudflare Access or an identity layer per [mfa.md](mfa.md). Flowise's native SSO is Enterprise-plan only and Langflow documents external JWT/JWKS identity integration, but on the open-source editions the fronting layer is the dependable path. Every provider key pasted into these tools is a secret held by the tool; rotate any key that lived on an instance that was ever open ([secrets.md](secrets.md)).

## 8. Contain what the builder can execute and reach

Authentication decides who gets in; it does not limit what a flow does once inside. All four run
custom code and outbound HTTP from the flow itself, so treat the editor as code-execution and SSRF
authority and contain it at the infrastructure layer, not with login alone:

- **Isolate the runtime**: one container or VM per builder, a non-root user, a read-only root
  filesystem where the tool supports it, and no host mount it does not need ([docker.md](docker.md)).
- **Default-deny egress**: permit only DNS and the provider APIs the flows actually call, and block
  the cloud metadata address so a flow cannot mint the instance's cloud credentials
  ([egress-metadata.md](egress-metadata.md)).
- **Keep each tool's own guards on**: Flowise's `HTTP_SECURITY_CHECK` and `CUSTOM_MCP_SECURITY_CHECK`
  (the docs warn that disabling the MCP check "allows arbitrary command execution"); LibreChat
  Actions' domain allowlist, which you must CONFIGURE (`actions.allowedDomains` in `librechat.yaml`): left unset its built-in SSRF checks block private targets but every other domain is allowed, and only once you set the allowlist are unlisted domains denied (listing a private destination grants it an exception); Dify's
  SSRF proxy in front of the code-sandbox and HTTP-request nodes. An HTTP allowlist is not containment
  of an arbitrary local tool, so pair it with the egress and isolation controls above.

## Verify

```bash
ss -tlnp                                        # read the whole list: app ports on 127.0.0.1; 80/443
                                                # public only where Dify's own nginx is the TLS edge.
                                                # A container port published by DNAT need not appear
                                                # here at all, so this list cannot clear 5003 by itself
docker compose ps --format json                 # run in dify/docker: no Publishers entry on the
                                                # plugin_daemon service may map it to a host port.
                                                # Read the entries rather than the array's length:
                                                # a merely exposed container port can appear too. A grep for
                                                # "published" cannot say which service published it
(                                               # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nc -vz -w 3 "$1" 5003 ;;                # from an outside network, and the authority here:
  esac
)
                                                # EXPOSE_PLUGIN_DEBUGGING_PORT can move it, so the ps output above is the authority on which port to probe
# a refusal or timeout from YOUR address is the pass ONLY if your packets reach the host at all: as a
# positive control, nc -vz -w 3 the same address on a port you know is open (your TLS edge, 443) and
# confirm THAT succeeds; if the control also times out the path is filtered and the 5003 result is
# inconclusive (the port could still be open from another network). A local error, an unsupported
# option (BusyBox netcat rejects -v), or exit 1 with no output is inconclusive: nothing reached the network
# The curls below observe TRANSPORT and status; they cannot by themselves prove APPLICATION auth,
# because a reverse proxy in front of the app can return the same codes (or forward to an
# unauthenticated backend once its own check passes), and curl follows HTTP redirects but does not run a
# SPA's client-side login routing. Attribute an app-layer result by probing the BACKEND directly on its
# loopback address (section 1; the separate fronting proxy is out of the path, but see the Dify nginx caveat below) and confirm the editor/setup state in a browser.
# Each curl disables client proxies (--noproxy '*'), is bounded, -g-guards substituted values, and
# prints the exit code. Run each before and after locking down.
#
# Editor/console and Dify /install: confirm in a FRESH, UNAUTHENTICATED BROWSER SESSION, not by status
# code - all four are SPAs serving the same 200 + HTML shell logged in or not, so a curl of / cannot
# tell an open editor from a login page and it discards the /install form you must read. In the browser,
# an unauthenticated editor visit must land on a login route, and https://dify.example.com/install must
# show "already set up" or redirect to login, NEVER an open create-admin form (an open form means the
# first visitor owns the instance). The curl below is only a transport-reachability note:
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
  -o /dev/null -w 'builder final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' https://builder.example.com/
#
# App API auth, tested against the app on its LOOPBACK address so your fronting reverse proxy (section 2)
# is out of the path, one MATCHED pair per app: WITHOUT the key expect that app's OWN rejection, WITH a
# valid key expect a 2xx returning real output (the positive control). Note for Dify: 127.0.0.1:8080 is
# Dify's OWN bundled nginx, which forwards /v1 to the api service - part of Dify, not a separate fronting
# proxy, but to attribute a result strictly to the api service, probe it on the Compose network instead
# (docker compose exec api curl http://localhost:5001/v1/parameters ...). The pair below shows the body
# so you can read the evidence, and the guard refuses while a placeholder remains. WITHOUT the key Dify
# returns 401 with a message like "Authorization header must be provided and start with 'Bearer'"; a 400
# app_unavailable instead means the app is unavailable or misconfigured (the token identifies the app),
# not that the endpoint is open. WITH a valid app key, 200 returning the app's parameters JSON.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DIFY_APP_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Dify app key on the set -- line above; not probing"; exit ;; esac
  curl -q -g -sS -w '\ndify no-key=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/v1/parameters
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -g -sS -w '\ndify with-key=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 15 -H @- http://127.0.0.1:8080/v1/parameters
)
# Repeat the same guarded, paired pattern for Flowise (POST http://127.0.0.1:3000/api/v1/prediction/<id>
# on a chatflow you ASSIGNED a key to - a keyless chatflow is public by design - key in an
# 'Authorization: Bearer' header) and Langflow (POST http://127.0.0.1:7860/api/v1/run/<id>, key in the
# 'x-api-key' header), each with a JSON body, expecting the app's own rejection without the key and a
# real 2xx with it. A transport error (exit != 0), a validation error, or a redirect is inconclusive,
# never a pass.
```

## Common mistakes

- Starting Dify without `INIT_PASSWORD` on a reachable host: the first visitor to `/install` owns the instance.
- Running Langflow with the default `LANGFLOW_AUTO_LOGIN=True`, which is no login.
- A Flowise chatflow with no API key assigned: the prediction API is public to anyone with the ID.
- Leaving LibreChat registration open after the admin exists, or running with unset or placeholder `CREDS_KEY`/`JWT_SECRET` instead of your own permanent values.

## Sources (checked September 2026)

- Dify Docker Compose deployment (setup at `/install`): https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose
- Dify environment variables (`SECRET_KEY`, `INIT_PASSWORD`, `CONSOLE_API_URL`, `CONSOLE_WEB_URL`, `APP_WEB_URL`): https://docs.dify.ai/en/self-host/deploy/configuration/environments
- Dify `docker/.env.example` (`EXPOSE_NGINX_PORT`, `NGINX_HTTPS_ENABLED`, certificate variables): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/docker/.env.example ; `docker-compose.yaml` (which services publish ports): https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/docker/docker-compose.yaml
- Docker packet filtering and firewalls (published ports bypass UFW): https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Dify certbot README (HTTPS steps): https://github.com/langgenius/dify/blob/4c1ad40f8e8a6ee58a958330558f2178b7e47fa7/docker/certbot/README.md
- Dify API keys (Bearer, backend-only): https://docs.dify.ai/en/api-reference/guides/get-started
- Flowise app-level authentication (v3.0.1 accounts, deprecated username/password, JWT secrets): https://docs.flowiseai.com/configuration/authorization/app-level
- Flowise chatflow-level API keys: https://docs.flowiseai.com/configuration/authorization/chatflow-level
- Flowise environment variables (`PORT`, `NUMBER_OF_PROXIES`, `FLOWISE_SECRETKEY_OVERWRITE`): https://docs.flowiseai.com/configuration/environment-variables
- Flowise SSO (Enterprise-plan only): https://docs.flowiseai.com/configuration/sso
- Flowise prediction API (401 without key): https://docs.flowiseai.com/api-reference/prediction
- Flowise deployment with nginx and certbot: https://docs.flowiseai.com/configuration/deployment/digital-ocean
- Flowise Compose (publishes `${PORT}:${PORT}`): https://github.com/FlowiseAI/Flowise/blob/4ea391204a499fb6d19747104502362295b4dde3/docker/docker-compose.yml
- Langflow example Compose (publishes `7860:7860` and PostgreSQL `5432:5432`): https://github.com/langflow-ai/langflow/blob/c6dbca308dc85526d5cecb31211821ec4f5e1d05/docker_example/docker-compose.yml
- LibreChat Compose (publishes `${PORT}:${PORT}`; extended via a docker-compose.override.yaml): https://github.com/danny-avila/LibreChat/blob/1596df724a840f894831fc74f21de8d8df72fcb1/docker-compose.yml
- Langflow API keys and authentication: https://docs.langflow.org/api-keys-and-authentication
- Langflow environment variables (`LANGFLOW_HOST`, `LANGFLOW_PORT`, SSL files): https://docs.langflow.org/environment-variables
- Langflow production best practices (`LANGFLOW_SECRET_KEY` preflight): https://docs.langflow.org/deployment-prod-best-practices
- Langflow security model (the editor runs arbitrary Python with host/filesystem/network access): https://docs.langflow.org/security
- Langflow authentication overview (external identity, JWT/JWKS validation): https://docs.langflow.org/authentication-overview
- LibreChat `.env` reference: https://www.librechat.ai/docs/configuration/dotenv
- LibreChat authentication system: https://www.librechat.ai/docs/configuration/authentication
- LibreChat OAuth2 and OIDC overview: https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC
- LibreChat Keycloak setup (`OPENID_*` variables): https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC/keycloak
- LibreChat Docker install (port 3080, first account is admin): https://www.librechat.ai/docs/local/docker
- LibreChat nginx and TLS: https://www.librechat.ai/docs/remote/nginx
- LibreChat Actions (domain allowlist, built-in SSRF checks): https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/actions
- LibreChat v0.7.7 changelog (two-factor authentication): https://www.librechat.ai/changelog/v0.7.7
- Docker Compose merge rules (sequences merge rather than replace; the `!reset` tag): https://docs.docker.com/reference/compose-file/merge/
- Dify `docker/docker-compose.yaml` (`plugin_daemon` publishes `${EXPOSE_PLUGIN_DEBUGGING_PORT:-5003}` with no host address): https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/docker/docker-compose.yaml
- `docker compose ps` output fields (`Service`, `Publishers`, `PublishedPort`): https://docs.docker.com/reference/cli/docker/compose/ps/
