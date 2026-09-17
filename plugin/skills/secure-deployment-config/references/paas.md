# PaaS platforms: what the platform does, what stays yours

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

Managed databases from these platforms come with TLS endpoints, but check what the specific endpoint supports: require certificate and hostname verification (`sslmode=verify-full`) per the database guides ([postgresql.md](postgresql.md), [mysql.md](mysql.md)) where the endpoint allows it, and note that some managed internal endpoints offer encryption but not `verify-full` (Render documents this for its internal connections), so do not treat an encryption-only connection as identity-verified. Keep the credentials in the platform's secret store, and restrict the network too: many managed databases are reachable from any IP by default (Render's Postgres is), so prefer private connectivity and disable or source-restrict external access with the provider's database network controls, not TLS alone. Databases you run yourself elsewhere follow their own guides plus [cloud-firewalls.md](cloud-firewalls.md).

## 5. Hugging Face Spaces

A new Space's default visibility depends on the creation path and any organization policy (organizations can enforce private-by-default, and duplicating a Space defaults to private), so explicitly select and verify visibility when you create it; public visibility exposes both the source and the running app. Visibility can be changed to "protected" (the source stays private to the owner and collaborators, but the running app is still public through its embed URL or custom domain) or "private" (both the source and the running app are restricted to the owner and collaborators); protected visibility requires a paid plan, PRO for personal accounts or Team/Enterprise for organizations, at the time of writing. Space secrets belong in the Settings tab's secrets store, never in the repository or its README metadata; anything set as a "variable" instead of a "secret" is still publicly readable. That secrets store is not a safe place for backend or provider credentials on a Static Space: Hugging Face exposes both variables and secrets to client-side JavaScript there, through `window.huggingface.variables`, so anything placed in a Static Space's secrets still reaches the browser. Keep server-side credentials in a server-side service, such as a Docker or Gradio Space or a separate backend, instead. Dev Mode opens an SSH and VS Code endpoint straight into the running container, which is materially more access than the app itself, so treat an unattended Dev Mode session the same as any other exposed admin path. For serverless GPU platforms, see [gpu-clouds.md](gpu-clouds.md).

## 6. Verify

```bash
# 1. Edge redirects HTTP->HTTPS. Spot-check on / only: it does not prove HTTPS on every route/method, nor that
#    the app's proxy-awareness (section 3) is set for secure cookies. --noproxy so a client proxy cannot answer.
curl -q -g -sI --noproxy '*' -w 'http=%{http_code}\n' http://app.example.com/          # expect a 301/302 to an https:// Location
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
