---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7a0dd035a903f96ba717ae3d7ba16d963882ced1b646ddcf32b67711a79f9fde",
  "components": {
    "render": {
      "name": "Render documentation",
      "basis": "unknown",
      "sources": {
        "s213783ba6209": "https://render.com/docs",
        "se240afec8d2d": "https://render.com/docs/postgresql-creating-connecting"
      }
    },
    "fly": {
      "name": "Fly.io documentation",
      "basis": "unknown",
      "sources": {
        "s1b202c527f2e": "https://fly.io/docs"
      }
    },
    "vercel": {
      "name": "Vercel documentation",
      "basis": "unknown",
      "sources": {
        "s2b470a6bc853": "https://vercel.com/docs",
        "se6089d5c4e96": "https://vercel.com/docs/deployment-protection",
        "s7836e043434a": "https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan"
      }
    },
    "spaces": {
      "name": "Hugging Face Spaces documentation",
      "basis": "unknown",
      "sources": {
        "sda0c810c053d": "https://huggingface.co/docs/hub/spaces-overview",
        "sd5ec2b2772e0": "https://huggingface.co/docs/hub/spaces-config-reference"
      }
    }
  },
  "claims": {
    "managed-tls": {"text": "The guide assigns HTTPS termination and certificate management, including custom domains, to the PaaS and advises against adding certbot or a TLS proxy. Render/Fly.io/Vercel are cited; Railway and Heroku are named without their own sources.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "application-auth": {"text": "Deployment protection does not replace app login, endpoint keys or application MFA; non-public endpoints still need their own access controls.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "vercel-login": {"text": "Vercel login can gate preview/deployment URLs on every plan and production domains with All Deployments; the 9 September 2026 change made that scope free including Hobby.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:s7836e043434a"], "status": "REASONED"},
    "vercel-password": {"text": "At the recorded documentation date, Password Protection is unavailable on Hobby, a paid per-project add-on on Pro and included on Enterprise.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "secret-store": {"text": "Use platform environment/secret configuration, not committed .env files; rotate credentials exposed in repositories, build logs or client bundles.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "public-env": {"text": "Only public values belong in browser-compiled environment variables such as NEXT_PUBLIC_; the guide records no specific frontend compiler source here.", "components": ["vercel"], "sources": ["vercel:s2b470a6bc853"], "status": "REASONED"},
    "https-redirect": {"text": "Redirect HTTP to HTTPS with the platform toggle or application logic using the forwarded-protocol header; exact platform toggles are not supplied.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "proxy-awareness": {"text": "Configure Express trust proxy or Django SECURE_PROXY_SSL_HEADER so secure cookies and redirects work behind the platform; framework vendor sources are not recorded here.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "listener-port": {"text": "Bind only the platform-injected port, commonly PORT, and avoid extra listeners; exact platform binding requirements are not cited beyond documentation roots.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "database-identity": {"text": "Where supported, require TLS certificate/hostname verification with PostgreSQL sslmode=verify-full or MySQL --ssl-mode=VERIFY_IDENTITY; MySQL client syntax lacks a source here.", "components": ["render"], "sources": ["render:se240afec8d2d"], "status": "REASONED"},
    "render-internal-tls": {"text": "Render internal PostgreSQL TLS is optional and supports neither verify-ca nor verify-full; sslmode=require prevents plaintext fallback but is not identity verification.", "components": ["render"], "sources": ["render:se240afec8d2d"], "status": "REASONED"},
    "database-network": {"text": "Render Postgres external access is open to any IP by default; prefer private connectivity and disable or source-restrict external access. Keep database credentials in the secret store.", "components": ["render"], "sources": ["render:se240afec8d2d"], "status": "REASONED"},
    "spaces-creation": {"text": "Explicitly select and verify Space visibility: creation path and organization policy affect defaults and duplication defaults private. The organization private-by-default policy lacks a direct citation here.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-public": {"text": "Public Spaces expose both source and running app.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-protected": {"text": "Protected Spaces keep source private to owner/collaborators but expose the app via embed URL or custom domain; the recorded requirement is PRO for personal accounts or Team/Enterprise for organizations.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-private": {"text": "Private Spaces restrict both source and running app to the owner and collaborators.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-secrets": {"text": "Use Settings secrets for sensitive values, never repository/README metadata; variables remain publicly readable.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d", "spaces:sd5ec2b2772e0"], "status": "REASONED"},
    "spaces-static": {"text": "Static Spaces expose both variables and secrets to client JavaScript through window.huggingface.variables; keep backend/provider credentials in Docker/Gradio Spaces or another server-side service.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-dev": {"text": "Dev Mode opens SSH and VS Code access into the container; treat unattended sessions as admin exposure. The cited overview links Dev Mode but does not document these endpoints itself.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "verify-redirect": {"text": "A HEAD request to HTTP / should return 301/302/307/308 with an HTTPS Location; the guide names Vercel 308. This spot-check proves neither every route/method nor secure-cookie proxy awareness; the exact status lacks a direct citation here.", "components": ["vercel"], "sources": ["vercel:s2b470a6bc853"], "status": "REASONED", "verify": [1]},
    "verify-app-auth": {"text": "Disable deployment protection or use a Protection Bypass token to isolate app auth: anonymous protected requests should get the app's 401/403, then valid app credentials a 2xx. A platform SSO 401 is not app enforcement.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED", "verify": [1]},
    "verify-secrets": {"text": "Scan history, working tree and deployed client JS, source maps, generated config and runtime values for every credential type; no matches is evidence, not proof. The cited platform roots do not document this scan procedure.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED", "verify": [1]}
  }
}
---
# PaaS platforms: what the platform does, what stays yours

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| managed-tls: The guide assigns HTTPS termination and certificate management, including custom domains, to the PaaS and advises against adding certbot or a TLS proxy. Render/Fly.io/Vercel are cited; Railway and Heroku are named without their own sources. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
| application-auth: Deployment protection does not replace app login, endpoint keys or application MFA; non-public endpoints still need their own access controls. | Vercel documentation unknown | REASONED |
| vercel-login: Vercel login can gate preview/deployment URLs on every plan and production domains with All Deployments; the 9 September 2026 change made that scope free including Hobby. | Vercel documentation unknown | REASONED |
| vercel-password: At the recorded documentation date, Password Protection is unavailable on Hobby, a paid per-project add-on on Pro and included on Enterprise. | Vercel documentation unknown | REASONED |
| secret-store: Use platform environment/secret configuration, not committed .env files; rotate credentials exposed in repositories, build logs or client bundles. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
| public-env: Only public values belong in browser-compiled environment variables such as NEXT_PUBLIC_; the guide records no specific frontend compiler source here. | Vercel documentation unknown | REASONED |
| https-redirect: Redirect HTTP to HTTPS with the platform toggle or application logic using the forwarded-protocol header; exact platform toggles are not supplied. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
| proxy-awareness: Configure Express trust proxy or Django SECURE_PROXY_SSL_HEADER so secure cookies and redirects work behind the platform; framework vendor sources are not recorded here. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
| listener-port: Bind only the platform-injected port, commonly PORT, and avoid extra listeners; exact platform binding requirements are not cited beyond documentation roots. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
| database-identity: Where supported, require TLS certificate/hostname verification with PostgreSQL sslmode=verify-full or MySQL --ssl-mode=VERIFY_IDENTITY; MySQL client syntax lacks a source here. | Render documentation unknown | REASONED |
| render-internal-tls: Render internal PostgreSQL TLS is optional and supports neither verify-ca nor verify-full; sslmode=require prevents plaintext fallback but is not identity verification. | Render documentation unknown | REASONED |
| database-network: Render Postgres external access is open to any IP by default; prefer private connectivity and disable or source-restrict external access. Keep database credentials in the secret store. | Render documentation unknown | REASONED |
| spaces-creation: Explicitly select and verify Space visibility: creation path and organization policy affect defaults and duplication defaults private. The organization private-by-default policy lacks a direct citation here. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-public: Public Spaces expose both source and running app. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-protected: Protected Spaces keep source private to owner/collaborators but expose the app via embed URL or custom domain; the recorded requirement is PRO for personal accounts or Team/Enterprise for organizations. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-private: Private Spaces restrict both source and running app to the owner and collaborators. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-secrets: Use Settings secrets for sensitive values, never repository/README metadata; variables remain publicly readable. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-static: Static Spaces expose both variables and secrets to client JavaScript through window.huggingface.variables; keep backend/provider credentials in Docker/Gradio Spaces or another server-side service. | Hugging Face Spaces documentation unknown | REASONED |
| spaces-dev: Dev Mode opens SSH and VS Code access into the container; treat unattended sessions as admin exposure. The cited overview links Dev Mode but does not document these endpoints itself. | Hugging Face Spaces documentation unknown | REASONED |
| verify-redirect: A HEAD request to HTTP / should return 301/302/307/308 with an HTTPS Location; the guide names Vercel 308. This spot-check proves neither every route/method nor secure-cookie proxy awareness; the exact status lacks a direct citation here. | Vercel documentation unknown | REASONED |
| verify-app-auth: Disable deployment protection or use a Protection Bypass token to isolate app auth: anonymous protected requests should get the app's 401/403, then valid app credentials a 2xx. A platform SSO 401 is not app enforcement. | Vercel documentation unknown | REASONED |
| verify-secrets: Scan history, working tree and deployed client JS, source maps, generated config and runtime values for every credential type; no matches is evidence, not proof. The cited platform roots do not document this scan procedure. | Render documentation unknown; Fly.io documentation unknown; Vercel documentation unknown | REASONED |
<!-- version-basis:end -->

On Render, Fly.io, Railway, Vercel, Heroku, and similar platforms, TLS is not your problem: the platform terminates HTTPS and manages certificates, including for custom domains. Do not bolt certbot or a reverse proxy onto a PaaS app, and do not apply this repository's server-TLS guides there. What stays yours:

## 1. Authentication: entirely yours

The platform does not authenticate your application's users. Some platforms protect the deployment itself: Vercel Deployment Protection, for example, can require a Vercel login to open preview and deployment URLs on every plan, and production domains too once the All Deployments scope is selected, which Vercel's changelog of 9 September 2026 made free on every plan including Hobby; Password Protection is not available on Hobby, is a paid add-on per protected project on Pro, and is included on Enterprise (at the time of writing). That gate keeps the public out of a preview; it is not your app's login. Every non-public endpoint still needs login or keys per [authentication.md](authentication.md), MFA where viable per [mfa.md](mfa.md), and a hosted provider makes both easy ([identity-providers.md](identity-providers.md)). "It is on Vercel" changes nothing about an open `/api/admin`.

## 2. Secrets: use the platform's store

Each platform provides environment/secret configuration. Set secrets there; never commit `.env` files ([secrets.md](secrets.md)). Rotate anything that ever appeared in the repository, build logs, or client bundles. Public frontend frameworks compile some env vars into the client (for example `NEXT_PUBLIC_`-prefixed values); only put genuinely public values in those.

## 3. Enforce HTTPS and correct proxy awareness

- Redirect HTTP to HTTPS where the platform offers a toggle, or in the app (checking the platform's forwarded-protocol header).
- Behind the platform proxy, configure the framework accordingly (`trust proxy` in Express per [nodejs.md](nodejs.md), `SECURE_PROXY_SSL_HEADER` in Django per [python.md](python.md)) so secure cookies and redirects behave.
- Bind to the port the platform injects (commonly a `PORT` variable) and nothing else; do not open extra listeners.

## 4. Databases attached to PaaS apps

Managed databases from these platforms come with TLS endpoints, but check what the specific endpoint supports: require certificate and hostname verification with the client's own setting (`sslmode=verify-full` for PostgreSQL, `--ssl-mode=VERIFY_IDENTITY` for MySQL) per the database guides ([postgresql.md](postgresql.md), [mysql.md](mysql.md)) where the endpoint allows it, and note that some managed internal endpoints support encryption but not `verify-full` (Render's internal PostgreSQL connections, where TLS is optional, do not support `verify-ca`/`verify-full`); there, set `sslmode=require` to force encryption and prevent a plaintext fallback, and do not treat that encryption-only connection as identity-verified. Keep the credentials in the platform's secret store, and restrict the network too: many managed databases are reachable from any IP by default (Render's Postgres is), so prefer private connectivity and disable or source-restrict external access with the provider's database network controls, not TLS alone. Databases you run yourself elsewhere follow their own guides plus [cloud-firewalls.md](cloud-firewalls.md).

## 5. Hugging Face Spaces

A new Space's default visibility depends on the creation path and any organization policy (organizations can enforce private-by-default, and duplicating a Space defaults to private), so explicitly select and verify visibility when you create it; public visibility exposes both the source and the running app. Visibility can be changed to "protected" (the source stays private to the owner and collaborators, but the running app is still public through its embed URL or custom domain) or "private" (both the source and the running app are restricted to the owner and collaborators); protected visibility requires a paid plan, PRO for personal accounts or Team/Enterprise for organizations, at the time of writing. Space secrets belong in the Settings tab's secrets store, never in the repository or its README metadata; anything set as a "variable" instead of a "secret" is still publicly readable. That secrets store is not a safe place for backend or provider credentials on a Static Space: Hugging Face exposes both variables and secrets to client-side JavaScript there, through `window.huggingface.variables`, so anything placed in a Static Space's secrets still reaches the browser. Keep server-side credentials in a server-side service, such as a Docker or Gradio Space or a separate backend, instead. Dev Mode opens an SSH and VS Code endpoint straight into the running container, which is materially more access than the app itself, so treat an unattended Dev Mode session the same as any other exposed admin path. For serverless GPU platforms, see [gpu-clouds.md](gpu-clouds.md).

## 6. Verify

REASONED: HTTPS redirect, application-authentication and deployed-secret checks; no PaaS application, tenant credentials or deployed client bundle was supplied for this metadata review, and no run is recorded. The expected readings below follow the cited platform documentation and the guide's application-security reasoning; exact application behaviour remains deployment-specific.

```bash
# 1. Edge redirects HTTP->HTTPS. Spot-check on / only: it does not prove HTTPS on every route/method, nor that
#    the app's proxy-awareness (section 3) is set for secure cookies. --noproxy so a client proxy cannot answer.
curl -q -g -sI --noproxy '*' -w 'http=%{http_code}\n' http://app.example.com/          # expect an HTTP redirect (301/302/307/308; Vercel uses 308) with an https:// Location
# 2. Your APP's own auth must reject an unauthenticated request, NOT the platform deployment-protection gate,
#    which also returns 401 (its SSO challenge). Disable deployment protection (or use a Protection Bypass token)
#    so only application auth is in play:
curl -q -g -s --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://app.example.com/REPLACE_WITH_PROTECTED_PATH   # no creds: want the APP's own 401/403, not a platform SSO 401
#    Then repeat with a valid application credential (your app's session cookie or API token, supplied from a file with
#    -b or -H @file so it stays out of shell history) and require a 2xx: that positive control proves the endpoint is
#    reachable and that the app's own auth, not the platform gate, is what gates it.
# 3. Secrets: run secrets.md's history and working-tree scans AND grep the DEPLOYED client bundle (JS, source maps,
#    generated config, runtime-injected values) for every credential type, not just private keys. No matches is evidence, not proof.
```

## Sources (checked September 2026)

- Render: https://render.com/docs ; Fly.io: https://fly.io/docs ; Vercel: https://vercel.com/docs (each documents managed TLS and environment configuration; consult your platform's pages for the exact toggles)
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Vercel changelog, protect production deployments for free on every plan (9 September 2026): https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces-overview and https://huggingface.co/docs/hub/spaces-config-reference
- Render managed PostgreSQL (external access is open by default and can be restricted; internal connections do not support `sslmode=verify-ca`/`verify-full`): https://render.com/docs/postgresql-creating-connecting
