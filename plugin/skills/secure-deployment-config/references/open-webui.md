# Open WebUI: signup control, TLS, and MFA

Open WebUI has account-based authentication built in; the risks are open signup on an exposed instance and running it on plain HTTP. It provides no TLS of its own, so encryption comes from a fronting layer.

## 1. Control who can register

Environment variables (defaults per the Open WebUI reference):

```
ENABLE_SIGNUP=false          # default true; disable once your accounts exist (persisted, see below)
DEFAULT_USER_ROLE=pending    # the default; new accounts wait for admin approval
                             # other values: user, admin
```

`ENABLE_SIGNUP` is a persisted setting: the reference marks it a `ConfigVar`, which means the value is written to the database on first launch and on later starts the stored value wins over the environment, unless `ENABLE_PERSISTENT_CONFIG=false` (default `true`). On an instance that has already started, change signup in the Admin panel rather than in the environment, then confirm the change took effect (Verify below).

With signup left on, keep `DEFAULT_USER_ROLE=pending` so a stranger who registers gets no access until approved. An admin account can also be created at startup by setting `WEBUI_ADMIN_EMAIL` together with `WEBUI_ADMIN_PASSWORD` (supply the password via the environment, not a compose file in git; see [secrets.md](secrets.md)).

The first account created becomes the administrator, whatever `DEFAULT_USER_ROLE` is set to; that role governs only the accounts that follow. Claim the admin account yourself while the instance is still bound to loopback, before anyone else can reach it, or preset it with `WEBUI_ADMIN_EMAIL` and `WEBUI_ADMIN_PASSWORD`. On an exposed instance with signup on, whoever registers first is the administrator.

For SSO, the reference documents OAuth/OIDC settings plus `ENABLE_PASSWORD_AUTH=false` to turn off password login once SSO works; enforcing MFA then happens at the identity provider ([mfa.md](mfa.md)).

## 2. Bind privately and add TLS in front

```bash
docker run -d -p 127.0.0.1:3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

The `-v open-webui:/app/backend/data` volume holds the accounts and the persisted config; the vendor requires it. Reuse the same volume whenever you replace the container (an upgrade starts a fresh one), or the database resets and, by the first-account rule above, the next account to register becomes the administrator. When you do start on an empty database, keep the public proxy route disabled until your admin account exists and signup is confirmed off.

Publish it through [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), through a [Cloudflare Tunnel with Access](cloudflare.md) in front, or over a [tailnet with Tailscale Serve](tailscale.md) (restricted by tailnet policy). Tailscale Funnel is public and adds no login of its own, so keep Open WebUI's own authentication on behind it. Never expose port 8080 directly: login forms over plain HTTP send passwords in cleartext.

## 3. Verify

```bash
ss -tlnp   # read every listener; the published mapping should be 127.0.0.1:3000 only, never 0.0.0.0 or ::.
           # ss shows host listeners, not Docker's NAT: use Docker Engine 28.0+ for loopback publishing
           # (older engines let a same-L2 host reach a localhost-published port), confirm the mapping is
           # 127.0.0.1:3000->8080/tcp, and from another LAN/VPC host confirm nothing answers on port 3000.
curl -q -g -sSI --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' 'https://chat.example.com/'
                                     # serves over TLS without -k; --noproxy so a client proxy cannot answer
# Signup state, programmatically: Open WebUI serves its feature flags at /api/config.
curl -q -g -sS --noproxy '*' 'https://chat.example.com/api/config'
                                     # JSON feature flags; confirm signup is disabled there (features.enable_signup: false)
# In a private browser window, AFTER your admin account exists: the sign-up option is absent AND an actual
# registration attempt is REFUSED (a missing button alone is not proof). With signup on, registering a new
# account yields a pending/unapproved user, not access.
```

## Sources (checked September 2026)

- Open WebUI environment configuration reference: https://docs.openwebui.com/reference/env-configuration
- Open WebUI FAQ (the first account created becomes the administrator): https://docs.openwebui.com/faq
- Open WebUI repository (the Docker Quick Start `-v open-webui:/app/backend/data` data volume): https://github.com/open-webui/open-webui
- Docker port publishing (localhost publishing; releases older than 28.0.0 let a same-L2 host reach a localhost-published port): https://docs.docker.com/engine/network/port-publishing/
