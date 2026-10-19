# PaaS platforms: what the platform does, what stays yours

Render, Fly.io, Railway, Vercel, Heroku and Hugging Face Spaces host your app and handle parts of running it, such as HTTPS. This guide helps your AI assistant deploy securely, including what each platform's TLS covers, authentication that stays yours, and backend secrets kept server-side, never in a Static Space.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/paas.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Render documentation (no recorded version), Next.js pinned documentation v16.4.2, Next.js environment variables 15, Express request protocol 5.x, Django proxy security setting 6.1, and MySQL client connection options 8.4; 3 further sources are pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 22 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

TLS responsibilities depend on the platform and deployment mode:

- Render: the load balancer terminates HTTPS for web services and forwards HTTP to the app. Render automatically issues and renews certificates for added custom domains, including wildcards. Add the domain, configure DNS, and verify it in the dashboard. Wildcards require the root domain to point to Render and the prescribed wildcard, `_acme-challenge`, and `_cf-custom-hostname` CNAME records; existing CAA records must allow Let's Encrypt and Google Trust Services, with `issuewild` records for wildcards. At the time of writing, included custom-domain quotas depend on the workspace plan and additional domains cost extra.
- Fly.io: Fly Proxy's `tls` handler terminates TLS and forwards plaintext; without handlers, TCP passes through and the app can terminate TLS itself. Add the custom domain and configure DNS for automatic certificate issuance. Issuance and renewal require domain verification through an AAAA record pointing to the app, an `_acme-challenge` CNAME, or a `_fly-ownership` TXT record; wildcard certificates require DNS-01 with the `_acme-challenge` CNAME. These passages describe managed certificates and renewal prerequisites but do not explicitly establish automatic renewal. Imported certificates require ownership verification and take priority over a coexisting Fly-managed fallback.
- Railway: correctly configured custom domains receive automatically issued Let's Encrypt certificates, renewed with 30 days of their 90-day validity remaining; external certificates are unsupported. Both the supplied CNAME and ownership TXT records are required; wildcards also require the `_acme-challenge` CNAME, unproxied on Cloudflare. Root domains require CNAME flattening or dynamic ALIAS records. At the time of writing, custom-domain limits are one on Trial, two per service on Hobby and twenty per service by default on Pro, with increases available on request; Freenom domains are unsupported. For Cloudflare-proxied domains, issuance can fail and Railway can instead serve its default `*.up.railway.app` certificate; the docs require Full mode and warn that Full (Strict) will not work as intended. Cloudflare proxying below first-level subdomains requires Advanced Certificate Manager or switching those records to DNS Only. Railway's edge proxy (tcp-proxy) terminates TLS; traffic is then forwarded over Railway's internal network to the deployment ([request flow](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43)).
- Vercel: its CDN terminates TLS. Certificates for deployment URLs are generated and kept updated automatically. Custom-domain issuance requires successful validation after DNS propagation; non-wildcards use HTTP-01 reachable at Vercel, and wildcards require Vercel nameservers for DNS-01. Vercel automatically attempts renewal 14 to 30 days before expiry; correct DNS, proxy, and CAA configuration must still permit validation. At the time of writing, only Enterprise teams can configure custom SSL; uploaded certificates cannot be renewed automatically by Vercel. The `/.well-known` path is reserved and cannot be redirected or rewritten.
- Heroku: the HTTP routing page describes load-balancer SSL termination, with separate Private Spaces routers. At the time of writing, ACM is included free for all applications; enable it for automatic issuance and renewal one month before expiry, using the correct Heroku DNS target. Adding custom domains requires a verified Heroku account. Cedar Private Spaces require a running web dyno for validation and renewal, cannot use ACM with Trusted IPs blocking access, and cannot use ACM for wildcard domains. The page says customers must upload their own wildcard certificate for Private Space apps, but its limitations also say "For Generation Private Space apps" can use ACM with wildcards; Fir wildcard eligibility is therefore not established consistently here. Uploading a certificate disables ACM. CAA must permit Let's Encrypt, and DNS/CDN configuration must allow validation; ACM must be disabled if the app requires the platform-handled ACME challenge paths.

This guide's advice: where the platform terminates TLS and manages the required certificate, do not bolt certbot or an extra TLS reverse proxy onto the app, and do not apply this repository's server-TLS guides to that managed ingress. What stays yours:

## 1. Authentication: entirely yours

The platform does not authenticate your application's users. Some platforms protect the deployment itself: Vercel Deployment Protection, for example, can require a Vercel login to open preview and deployment URLs on every plan, and production domains too once the All Deployments scope is selected, which Vercel's changelog of 9 September 2026 made free on every plan including Hobby; Password Protection is not available on Hobby, is a paid add-on per protected project on Pro, and is included on Enterprise (at the time of writing). That gate keeps the public out of a preview; it is not your app's login. Every non-public endpoint still needs login or keys per [authentication.md](authentication.md), MFA where viable per [mfa.md](mfa.md), and a hosted provider makes both easy ([identity-providers.md](identity-providers.md)). "It is on Vercel" changes nothing about an open `/api/admin`.

## 2. Secrets: use the platform's store

Each platform provides environment/secret configuration. Set secrets there; never commit `.env` files ([secrets.md](secrets.md)). Rotate anything that ever appeared in the repository, build logs, or client bundles. Public frontend frameworks compile some env vars into the client (for example `NEXT_PUBLIC_`-prefixed values); only put genuinely public values in those.

## 3. Enforce HTTPS and correct proxy awareness

- Redirect HTTP to HTTPS. This guide's advice: use the documented automatic redirect, enable the documented platform setting, or implement the redirect in the app with verified proxy trust:
  - Render's TLS page says all HTTP requests are automatically redirected to HTTPS; it does not state a status code.
  - Fly.io's pinned configuration reference documents `force_https = true` under `[http_service]` in `fly.toml` for apps managed by Fly Launch. The pinned services page says enabling `force_https` returns 301 for all HTTP requests; the option is only valid on HTTP handlers, and deployment fails if it is set on other handlers.
  - Railway's pinned public-networking specifications describe automatic HTTPS redirects for plain HTTP GET requests with 301, and HTTP POST redirects that convert the request to GET ([GET status and POST conversion](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/public-networking/specs-and-limits.md#L37-L38)). They do not establish a configurable redirect toggle, a POST status code, or the HEAD response used below.
  - Vercel's encryption page says its CDN automatically redirects HTTP requests to HTTPS with 308 and that this redirection cannot be disabled.
  - Heroku's cited HTTP routing page does not establish automatic HTTPS redirection, a redirect toggle, an application-only redirect contract, or a status code. This guide's advice: implement application-side redirection unless the deployed ingress is known to enforce it, and verify the result.

  For application-side handling, this guide's advice is to check the platform's forwarded-protocol header only after verifying the framework's proxy trust requirements. Fly's HTTP handler documents `X-Forwarded-Proto` as the original client protocol, `http` or `https`; Railway's public-networking specifications say it always indicates `https`. Heroku's routing page describes it as the originating protocol but explicitly warns that forwarded headers, including `X-Forwarded-Proto`, are not trusted because the order of pre-existing fields is unknown. These descriptions do not establish header sanitization; the cited Render and Vercel TLS pages do not establish a forwarded-protocol header contract. Keep the Express 5.x `trust proxy` and Django 6.1 `SECURE_PROXY_SSL_HEADER` trust requirements in view when implementing this guide's advice.
- Behind the platform proxy, configure the framework accordingly (`trust proxy` in Express per [nodejs.md](nodejs.md), `SECURE_PROXY_SSL_HEADER` in Django per [python.md](python.md)) so secure cookies and redirects behave.
- Bind the listener required by the deployment model. Render web services must bind `0.0.0.0`; Render recommends `PORT` (default port 10000, configurable), can usually detect another bound port, and requires the public HTTP server to use `PORT` when multiple ports are bound. Fly Proxy HTTP services must be reachable over IPv4: use `0.0.0.0` and match the service's configured `internal_port` to the app listener; IPv4-mapped IPv6 wildcard behaviour depends on the VM and runtime. Railway domains route to a detected or selected internal target port; its troubleshooting page says web servers should bind `0.0.0.0` and listen on the automatically injected `PORT` ([listener and port](https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51)). Heroku assigns web processes a `PORT` environment variable; for Fir, the Generations page says Private Spaces networking uses IPv6 by default, that IPv4-only assumptions do not bind properly, and recommends an IPv6 or dual-stack listener (typically `::`); the cited pages do not establish Cedar's listener address. Vercel runtimes transform code into Functions served by its CDN, including Node.js function entrypoints and Python ASGI/WSGI apps; that page establishes neither a universal injected port nor a required listener address. This guide's advice: bind nothing else and do not open extra listeners.

## 4. Databases attached to PaaS apps

Managed databases from these platforms come with TLS endpoints, but check what the specific endpoint supports: require certificate and hostname verification with the client's own setting (`sslmode=verify-full` for PostgreSQL, `--ssl-mode=VERIFY_IDENTITY` for MySQL) per the database guides ([postgresql.md](postgresql.md), [mysql.md](mysql.md)) where the endpoint allows it, and note that some managed internal endpoints support encryption but not `verify-full` (Render's internal PostgreSQL connections, where TLS is optional, do not support `verify-ca`/`verify-full`); there, set `sslmode=require` to force encryption and prevent a plaintext fallback, and do not treat that encryption-only connection as identity-verified. Keep the credentials in the platform's secret store, and restrict the network too: many managed databases are reachable from any IP by default (Render's Postgres is), so prefer private connectivity and disable or source-restrict external access with the provider's database network controls, not TLS alone. Databases you run yourself elsewhere follow their own guides plus [cloud-firewalls.md](cloud-firewalls.md).

## 5. Hugging Face Spaces

This guide's advice: explicitly select and verify visibility when you create a Space. The pinned docs describe public, protected, and private visibility; public visibility exposes both the source and the running app, and duplicating a Space defaults to private. At the time of writing, the pinned Advanced Security docs attach repository visibility controls to Team & Enterprise organizations: Public by default creates new repositories with public visibility; Private by default creates new repositories with private visibility, and changing that setting does not affect existing repositories; Private only enforces private visibility for all new repositories, with only organization admins able to change visibility settings. Those lines do not establish a general creation default or a retroactive conversion of existing repositories by Private only. Visibility can be changed to "protected" (the source stays private to the owner and collaborators, but the running app is still public through its embed URL or custom domain) or "private" (both the source and the running app are restricted to the owner and collaborators); protected visibility requires a paid plan, PRO for personal accounts or Team/Enterprise for organizations, at the time of writing. Space secrets belong in the Settings tab's secrets store, never in the repository or its README metadata; anything set as a "variable" instead of a "secret" is still publicly readable. That secrets store is not a safe place for backend or provider credentials on a Static Space: Hugging Face exposes both variables and secrets to client-side JavaScript there, through `window.huggingface.variables`, so anything placed in a Static Space's secrets still reaches the browser. Keep server-side credentials in a server-side service, such as a Docker or Gradio Space or a separate backend, instead.

At the time of writing, the pinned Dev Mode docs require PRO or Team & Enterprise. The Dev Mode Docker image starts the application as a subprocess and starts an SSH server for local editors and terminals and a VS Code server for in-product VS Code Web. Dev Mode exposes the running Space as a standard SSH host; clients use the Space subdomain shown in the Dev Mode controls as the username at ssh.hf.space, and local VS Code uses Remote - SSH to connect to the same host. SSH requires adding the machine's SSH public key to the user's Hugging Face account; these docs do not establish which users or roles may connect, or the access control for in-product VS Code Web. This guide's assessment: access into the running container is materially more access than the app itself, so treat an unattended Dev Mode session the same as any other exposed admin path. For serverless GPU platforms, see [gpu-clouds.md](gpu-clouds.md).

## 6. Verify

REASONED: HTTPS redirect, application-authentication and deployed-secret checks; no PaaS application, tenant credentials or deployed client bundle was supplied for this metadata review, and no run is recorded. The expected readings below follow the cited platform documentation and the guide's application-security reasoning; exact application behaviour remains deployment-specific.

```bash
# 1. This guide checks HTTP->HTTPS redirection. Spot-check on / only: it does not prove HTTPS on every route/method, nor that
#    the app's proxy-awareness (section 3) is set for secure cookies. --noproxy so a client proxy cannot answer.
#    Documented: Vercel 308; Fly HTTP handlers with force_https enabled 301. Render's code is unstated.
#    Railway documents GET 301 and POST-to-GET, not this HEAD response; Heroku's redirect policy is unestablished.
#    This guide's check: require 301/302/307/308 with an https:// Location; HTTP content without that redirect fails.
curl -q -g -sI --noproxy '*' -w 'http=%{http_code}\n' http://app.example.com/          # this guide's redirect check above
# 2. Your APP's own auth must reject an unauthenticated request, NOT the platform deployment-protection gate.
#    Vercel documents that Deployment Protection requires authentication for all requests, and that a valid
#    Protection Bypass for Automation token lets the request access the deployment without authentication,
#    sent as the x-vercel-protection-bypass HTTP header or query parameter carrying the project's generated
#    secret. Disable deployment protection (or use that bypass) so only application auth is in play. That
#    bypass is Vercel's; no Render or Fly equivalent is cited here, so do not assume one exists. If you use
#    the bypass secret, send it as the header, supplied from a file with -H @file per this guide's
#    conventions so it stays out of shell history; the query-parameter form writes it into history and logs.
#    The status codes below are this guide's expected reading; the cited pages state none, including for the
#    platform gate's own challenge (its SSO 401 below):
curl -q -g -s --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://app.example.com/REPLACE_WITH_PROTECTED_PATH   # no creds: want the APP's own 401/403, not a platform SSO 401
#    Then repeat with a valid application credential (your app's session cookie or API token, supplied from a file with
#    -b or -H @file so it stays out of shell history) and require a 2xx: that positive control proves the endpoint is
#    reachable and that the app's own auth, not the platform gate, is what gates it.
# 3. Secrets: run secrets.md's history and working-tree scans AND grep the DEPLOYED client bundle (JS, source maps,
#    generated config, runtime-injected values) for every credential type, not just private keys. No matches is evidence, not proof.
#    Why the deployed bundle: as the Next.js case, the pinned v16.4.2 docs say NEXT_PUBLIC_ values are inlined into
#    the JavaScript bundle delivered to the client at build time, and production browser source maps are disabled
#    unless productionBrowserSourceMaps opts in. What to grep and which credential types are this guide's procedure,
#    delegated to secrets.md, not taken from the cited pages.
```

## Sources (checked September 2026)

- Render: https://render.com/docs ; Fly.io: https://fly.io/docs ; Vercel: https://vercel.com/docs (each documents managed TLS and environment configuration; consult your platform's pages for the exact toggles)
- Vercel Deployment Protection: https://vercel.com/docs/deployment-protection
- Vercel changelog, protect production deployments for free on every plan (9 September 2026): https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan
- Vercel deployment protection bypass methods (checked October 2026): https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection
- Vercel Protection Bypass for Automation header and query parameter (checked October 2026): https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation
- Hugging Face Spaces: https://huggingface.co/docs/hub/spaces-overview and https://huggingface.co/docs/hub/spaces-config-reference
- Hugging Face Hub Space visibility choices and source/app access (checked October 2026; commit 6fb324369143cb76a723c88a592010514ac1095a): https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-overview.md#L29-L45
- Hugging Face Hub Space duplication visibility default (checked October 2026; commit 6fb324369143cb76a723c88a592010514ac1095a): https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-overview.md#L114-L118
- Hugging Face Hub organization visibility controls and plan scope (checked October 2026; commit 6fb324369143cb76a723c88a592010514ac1095a): https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/enterprise-advanced-security.md#L3-L27
- Hugging Face Hub Dev Mode plan requirement and servers (checked October 2026; commit 6fb324369143cb76a723c88a592010514ac1095a): https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-dev-mode.md#L3-L14
- Hugging Face Hub Dev Mode SSH, editor connection and SSH key requirement (checked October 2026; commit 6fb324369143cb76a723c88a592010514ac1095a): https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-dev-mode.md#L41-L78
- Render managed PostgreSQL (external access is open by default and can be restricted; internal connections do not support `sslmode=verify-ca`/`verify-full`): https://render.com/docs/postgresql-creating-connecting
- Next.js 15 environment variables (checked October 2026; `NEXT_PUBLIC_` values in browser JavaScript): https://nextjs.org/docs/15/app/guides/environment-variables
- Next.js v16.4.2 `NEXT_PUBLIC_` build-time inlining into client JavaScript (checked October 2026): https://github.com/vercel/next.js/blob/v16.4.2/docs/01-app/02-guides/environment-variables.mdx#L158-L164
- Next.js v16.4.2 production browser source maps default and opt-in serving (checked October 2026): https://github.com/vercel/next.js/blob/v16.4.2/docs/01-app/03-api-reference/05-config/01-next-config-js/productionBrowserSourceMaps.mdx#L8-L18
- Express 5.x request protocol (checked October 2026; `trust proxy` and `X-Forwarded-Proto`): https://expressjs.com/en/5x/api/request/#req.protocol
- Django 6.1 settings (checked October 2026; `SECURE_PROXY_SSL_HEADER` and trusted proxy requirements): https://docs.djangoproject.com/en/6.1/ref/settings/#secure-proxy-ssl-header
- MySQL 8.4 client connection options (checked October 2026; `--ssl-mode=VERIFY_IDENTITY` certificate and hostname verification): https://dev.mysql.com/doc/refman/8.4/en/connection-options.html#option_general_ssl-mode
- Render web-service listener and TLS termination (checked October 2026): https://render.com/docs/web-services
- Render managed TLS (checked October 2026): https://render.com/docs/tls
- Render custom-domain prerequisites (checked October 2026): https://render.com/docs/custom-domains
- Vercel TLS termination (checked October 2026): https://vercel.com/docs/cdn-security/encryption
- Vercel certificate validation and renewal (checked October 2026): https://vercel.com/docs/domains/working-with-ssl
- Vercel Functions runtimes (checked October 2026): https://vercel.com/docs/functions/runtimes
- Heroku certificate automation and limitations (checked October 2026): https://devcenter.heroku.com/articles/automated-certificate-management
- Heroku HTTP routing (checked October 2026): https://devcenter.heroku.com/articles/http-routing
- Heroku custom-domain prerequisites (checked October 2026): https://devcenter.heroku.com/articles/custom-domains
- Heroku web-process port assignment (checked October 2026): https://devcenter.heroku.com/articles/runtime-principles
- Heroku Fir Private Spaces networking and listener recommendation (checked October 2026): https://devcenter.heroku.com/articles/generations
- Fly TCP passthrough (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97
- Fly TLS termination (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176
- Fly domain verification for issuance and renewal (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L39-L44
- Fly wildcard validation and automatic issuance (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L64-L87
- Fly imported certificates and fallback (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L91-L102
- Fly public service binding (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42
- Fly IPv4 and IPv6 wildcard qualification (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92
- Railway custom-domain DNS and plan conditions (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L39-L122
- Railway certificate renewal and Cloudflare limitations (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L220-L247
- Railway root-domain DNS (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L150-L150
- Railway target ports (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146
- Railway web-server listener and injected port (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51
- Railway edge-proxy TLS termination and internal forwarding (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43
- Fly app configuration file (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/reference/configuration.mdx#L7-L7
- Fly HTTP service redirect setting (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/reference/configuration.mdx#L329-L350
- Fly redirect status and HTTP-handler restriction (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L229-L229
- Fly HTTP handler forwarded-protocol header (checked October 2026; commit 2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9): https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L117-L123
- Railway public-networking headers and request handling (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/public-networking/specs-and-limits.md#L16-L17
- Railway GET redirect status and POST conversion (checked October 2026; commit 72354493198302677fb6be6c692dd75c64cae2c6): https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/public-networking/specs-and-limits.md#L37-L38


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- render: Render documentation (unknown)
- fly: Fly.io documentation (unknown)
- fly-pinned: Fly.io pinned documentation (2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9)
- vercel: Vercel documentation (unknown)
- spaces: Hugging Face Spaces documentation (unknown)
- spaces-pinned: Hugging Face Hub documentation (6fb324369143cb76a723c88a592010514ac1095a)
- heroku: Heroku documentation (unknown)
- railway: Railway documentation (72354493198302677fb6be6c692dd75c64cae2c6)
- nextjs-pinned: Next.js pinned documentation (v16.4.2)
- nextjs: Next.js environment variables (15)
- express: Express request protocol (5.x)
- django: Django proxy security setting (6.1)
- mysql-client: MySQL client connection options (8.4)

Claims (full source mapping in the JSON block below):

- managed-tls (REASONED; render, fly, vercel, heroku, fly-pinned, railway): TLS and certificates depend on platform and deployment; Railway's edge proxy terminates TLS, then traffic crosses Railway's internal network; Fly passes TCP through without handlers; Fly automatic renewal and Heroku Fir wildcard eligibility remain unestablished. This guide's advice: no certbot or extra TLS proxy where the platform terminates TLS and manages the required certificate.
- application-auth (REASONED; vercel): Deployment protection does not replace app login, endpoint keys or application MFA; non-public endpoints still need their own access controls.
- vercel-login (REASONED; vercel): Vercel login can gate preview/deployment URLs on every plan and production domains with All Deployments; the 9 September 2026 change made that scope free including Hobby.
- vercel-password (REASONED; vercel): At the recorded documentation date, Password Protection is unavailable on Hobby, a paid per-project add-on on Pro and included on Enterprise.
- secret-store (REASONED; render, fly, vercel): Use platform environment/secret configuration, not committed .env files; rotate credentials exposed in repositories, build logs or client bundles.
- public-env (REASONED; vercel, nextjs): Only public values belong in browser-compiled environment variables such as NEXT_PUBLIC_.
- https-redirect (REASONED; render, fly, vercel, heroku, fly-pinned, railway, express, django): Enforce HTTPS: Render redirects automatically (code unstated), Vercel uses mandatory 308, Fly HTTP handlers use 301 with force_https, and Railway documents GET 301 and POST-to-GET, not HEAD. Heroku's redirect policy is unestablished and its forwarded headers are untrusted; this guide advises app handling with verified proxy trust, without assuming header sanitization.
- proxy-awareness (REASONED; render, fly, vercel, express, django): Configure Express trust proxy or Django SECURE_PROXY_SSL_HEADER so secure cookies and redirects work behind the platform.
- listener-port (REASONED; render, fly, vercel, heroku, fly-pinned, railway): Railway advises 0.0.0.0 on injected PORT; listener rules vary by deployment, with IPv6/dual-stack recommended for Heroku Fir Private Spaces. Cited pages do not establish Vercel Functions' listener/port contract or Heroku Cedar's listener address; this guide's advice: bind nothing else and do not open extra listeners.
- database-identity (REASONED; render, mysql-client): Where supported, require TLS certificate/hostname verification with PostgreSQL sslmode=verify-full or MySQL --ssl-mode=VERIFY_IDENTITY.
- render-internal-tls (REASONED; render): Render internal PostgreSQL TLS is optional and supports neither verify-ca nor verify-full; sslmode=require prevents plaintext fallback but is not identity verification.
- database-network (REASONED; render): Render Postgres external access is open to any IP by default; prefer private connectivity and disable or source-restrict external access. Keep database credentials in the secret store.
- spaces-creation (REASONED; spaces, spaces-pinned): This guide's advice: explicitly select and verify visibility when you create a Space. The pinned docs describe public, protected, and private visibility; public visibility exposes both the source and the running app, and duplicating a Space defaults to private. At the time of writing, the pinned Advanced Security docs attach repository visibility controls to Team &amp; Enterprise organizations: Public by default creates new repositories with public visibility; Private by default creates new repositories with private visibility, and changing that setting does not affect existing repositories; Private only enforces private visibility for all new repositories, with only organization admins able to change visibility settings. Those lines do not establish a general creation default or a retroactive conversion of existing repositories by Private only.
- spaces-public (REASONED; spaces): Public Spaces expose both source and running app.
- spaces-protected (REASONED; spaces): Protected Spaces keep source private to owner/collaborators but expose the app via embed URL or custom domain; the recorded requirement is PRO for personal accounts or Team/Enterprise for organizations.
- spaces-private (REASONED; spaces): Private Spaces restrict both source and running app to the owner and collaborators.
- spaces-secrets (REASONED; spaces): Use Settings secrets for sensitive values, never repository/README metadata; variables remain publicly readable.
- spaces-static (REASONED; spaces): Static Spaces expose both variables and secrets to client JavaScript through window.huggingface.variables; keep backend/provider credentials in Docker/Gradio Spaces or another server-side service.
- spaces-dev (REASONED; spaces, spaces-pinned): At the time of writing, the pinned Dev Mode docs require PRO or Team &amp; Enterprise. The Dev Mode Docker image starts the application as a subprocess and starts an SSH server for local editors and terminals and a VS Code server for in-product VS Code Web. Dev Mode exposes the running Space as a standard SSH host; clients use the Space subdomain shown in the Dev Mode controls as the username at ssh.hf.space, and local VS Code uses Remote - SSH to connect to the same host. SSH requires adding the machine's SSH public key to the user's Hugging Face account; these docs do not establish which users or roles may connect, or the access control for in-product VS Code Web. This guide's assessment: access into the running container is materially more access than the app itself, so treat an unattended Dev Mode session the same as any other exposed admin path.
- verify-redirect (REASONED; vercel, render, fly-pinned, railway, heroku): This guide's HTTP HEAD / check requires 301/302/307/308 with an HTTPS Location; Vercel documents 308 and Fly HTTP handlers 301 with force_https, but Render's code, Railway HEAD, and Heroku's redirect policy are unestablished. The spot-check proves neither every route/method nor secure-cookie proxy awareness.
- verify-app-auth (REASONED; vercel): Disable Vercel deployment protection or use its documented Protection Bypass for Automation, the x-vercel-protection-bypass header or query parameter carrying the project's generated secret, to isolate app auth; no Render or Fly equivalent is cited. This guide's expected reading: anonymous protected requests get the app's 401/403, valid app credentials a 2xx, and a platform SSO 401 is not app enforcement.
- verify-secrets (REASONED; render, fly, vercel, nextjs-pinned): Scan history, working tree and deployed client JS, source maps, generated config and runtime values for every credential type; no matches is evidence, not proof. The scan procedure is this guide's, delegated to secrets.md; the pinned Next.js v16.4.2 lines document only the NEXT_PUBLIC_ build-time inlining and off-by-default production browser source maps that motivate the bundle scan.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "b15b19ec1a2ecdc6d952996b240f9e17283d07f22eeac2a0dd7fee8f0c2eb06f",
  "components": {
    "render": {
      "name": "Render documentation",
      "basis": "unknown",
      "sources": {
        "s213783ba6209": "https://render.com/docs",
        "se240afec8d2d": "https://render.com/docs/postgresql-creating-connecting",
        "s1820ac471b6c": "https://render.com/docs/web-services",
        "s5b8400c2a2ba": "https://render.com/docs/tls",
        "s22963948fc90": "https://render.com/docs/custom-domains"
      }
    },
    "fly": {
      "name": "Fly.io documentation",
      "basis": "unknown",
      "sources": {
        "s1b202c527f2e": "https://fly.io/docs"
      }
    },
    "fly-pinned": {
      "name": "Fly.io pinned documentation",
      "basis": "2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9",
      "sources": {
        "s254c8c8a5edd": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L93-L97",
        "s32999aa4c58c": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L174-L176",
        "sf4105f79b22b": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L39-L44",
        "sea5560c14d13": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L64-L87",
        "sb935e8478a30": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/custom-domain.mdx#L91-L102",
        "s62fec91543a1": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L33-L42",
        "s61c1e50d2c11": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/app-services.mdx#L92-L92",
        "s6e9a7292860d": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/reference/configuration.mdx#L7-L7",
        "sa63b828c93df": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/reference/configuration.mdx#L329-L350",
        "s4324a02dbc42": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L229-L229",
        "scf2e6f3bce02": "https://github.com/superfly/docs/blob/2f68a40e09bb6ef4c4ac6f90c15c1cf5a176d7e9/networking/services.mdx#L117-L123"
      }
    },
    "vercel": {
      "name": "Vercel documentation",
      "basis": "unknown",
      "sources": {
        "s2b470a6bc853": "https://vercel.com/docs",
        "se6089d5c4e96": "https://vercel.com/docs/deployment-protection",
        "s7836e043434a": "https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan",
        "s3e7832fd3031": "https://vercel.com/docs/cdn-security/encryption",
        "se314aa4b7f1e": "https://vercel.com/docs/domains/working-with-ssl",
        "s22498401f5d0": "https://vercel.com/docs/functions/runtimes",
        "s845513031876": "https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection",
        "sc1588029e14e": "https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation"
      }
    },
    "spaces": {
      "name": "Hugging Face Spaces documentation",
      "basis": "unknown",
      "sources": {
        "sda0c810c053d": "https://huggingface.co/docs/hub/spaces-overview",
        "sd5ec2b2772e0": "https://huggingface.co/docs/hub/spaces-config-reference"
      }
    },
    "spaces-pinned": {
      "name": "Hugging Face Hub documentation",
      "basis": "6fb324369143cb76a723c88a592010514ac1095a",
      "sources": {
        "se2fb4e2a5c02": "https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-overview.md#L29-L45",
        "s9d332f0940e2": "https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-overview.md#L114-L118",
        "s969a28a4c44e": "https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/enterprise-advanced-security.md#L3-L27",
        "s5d393b019bad": "https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-dev-mode.md#L3-L14",
        "sd1ae2b703a70": "https://github.com/huggingface/hub-docs/blob/6fb324369143cb76a723c88a592010514ac1095a/docs/hub/spaces-dev-mode.md#L41-L78"
      }
    },
    "heroku": {
      "name": "Heroku documentation",
      "basis": "unknown",
      "sources": {
        "sa86eb06bbd4a": "https://devcenter.heroku.com/articles/automated-certificate-management",
        "s0c5bf300cef4": "https://devcenter.heroku.com/articles/http-routing",
        "sfbcf716168be": "https://devcenter.heroku.com/articles/custom-domains",
        "s370d4beec29a": "https://devcenter.heroku.com/articles/runtime-principles",
        "s211f5fe76042": "https://devcenter.heroku.com/articles/generations"
      }
    },
    "railway": {
      "name": "Railway documentation",
      "basis": "72354493198302677fb6be6c692dd75c64cae2c6",
      "sources": {
        "s93da6ccbfe58": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L39-L122",
        "s6d4dc8fb7784": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L220-L247",
        "s2bc94f13536b": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L150-L150",
        "sac1383056b65": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/domains/working-with-domains.md#L126-L146",
        "sbf08758c106a": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/public-networking/specs-and-limits.md#L16-L17",
        "s844d338bd121": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/public-networking/specs-and-limits.md#L37-L38",
        "s0462eef65b1b": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/troubleshooting/application-failed-to-respond.md#L46-L51",
        "sa9d326046a7f": "https://github.com/railwayapp/docs/blob/72354493198302677fb6be6c692dd75c64cae2c6/content/docs/networking/edge-networking.md#L40-L43"
      }
    },
    "nextjs-pinned": {
      "name": "Next.js pinned documentation",
      "basis": "v16.4.2",
      "sources": {
        "s0e3d2cd2248e": "https://github.com/vercel/next.js/blob/v16.4.2/docs/01-app/02-guides/environment-variables.mdx#L158-L164",
        "sf7cfdc553311": "https://github.com/vercel/next.js/blob/v16.4.2/docs/01-app/03-api-reference/05-config/01-next-config-js/productionBrowserSourceMaps.mdx#L8-L18"
      }
    },
    "nextjs": {
      "name": "Next.js environment variables",
      "basis": "15",
      "sources": {
        "s22e4b70dab8b": "https://nextjs.org/docs/15/app/guides/environment-variables"
      }
    },
    "express": {
      "name": "Express request protocol",
      "basis": "5.x",
      "sources": {
        "s5bc62e66824b": "https://expressjs.com/en/5x/api/request/#req.protocol"
      }
    },
    "django": {
      "name": "Django proxy security setting",
      "basis": "6.1",
      "sources": {
        "sb5e26f65fd91": "https://docs.djangoproject.com/en/6.1/ref/settings/#secure-proxy-ssl-header"
      }
    },
    "mysql-client": {
      "name": "MySQL client connection options",
      "basis": "8.4",
      "sources": {
        "s823c0bfaaafa": "https://dev.mysql.com/doc/refman/8.4/en/connection-options.html#option_general_ssl-mode"
      }
    }
  },
  "claims": {
    "managed-tls": {"text": "TLS and certificates depend on platform and deployment; Railway's edge proxy terminates TLS, then traffic crosses Railway's internal network; Fly passes TCP through without handlers; Fly automatic renewal and Heroku Fir wildcard eligibility remain unestablished. This guide's advice: no certbot or extra TLS proxy where the platform terminates TLS and manages the required certificate.", "components": ["render", "fly", "vercel", "heroku", "fly-pinned", "railway"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853", "render:s1820ac471b6c", "render:s5b8400c2a2ba", "render:s22963948fc90", "vercel:s3e7832fd3031", "vercel:se314aa4b7f1e", "heroku:sa86eb06bbd4a", "heroku:s0c5bf300cef4", "heroku:sfbcf716168be", "fly-pinned:s254c8c8a5edd", "fly-pinned:s32999aa4c58c", "fly-pinned:sf4105f79b22b", "fly-pinned:sea5560c14d13", "fly-pinned:sb935e8478a30", "railway:s93da6ccbfe58", "railway:s6d4dc8fb7784", "railway:s2bc94f13536b", "railway:sa9d326046a7f"], "status": "REASONED"},
    "application-auth": {"text": "Deployment protection does not replace app login, endpoint keys or application MFA; non-public endpoints still need their own access controls.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "vercel-login": {"text": "Vercel login can gate preview/deployment URLs on every plan and production domains with All Deployments; the 9 September 2026 change made that scope free including Hobby.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:s7836e043434a"], "status": "REASONED"},
    "vercel-password": {"text": "At the recorded documentation date, Password Protection is unavailable on Hobby, a paid per-project add-on on Pro and included on Enterprise.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "secret-store": {"text": "Use platform environment/secret configuration, not committed .env files; rotate credentials exposed in repositories, build logs or client bundles.", "components": ["render", "fly", "vercel"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853"], "status": "REASONED"},
    "public-env": {"text": "Only public values belong in browser-compiled environment variables such as NEXT_PUBLIC_.", "components": ["vercel", "nextjs"], "sources": ["vercel:s2b470a6bc853", "nextjs:s22e4b70dab8b"], "status": "REASONED"},
    "https-redirect": {"text": "Enforce HTTPS: Render redirects automatically (code unstated), Vercel uses mandatory 308, Fly HTTP handlers use 301 with force_https, and Railway documents GET 301 and POST-to-GET, not HEAD. Heroku's redirect policy is unestablished and its forwarded headers are untrusted; this guide advises app handling with verified proxy trust, without assuming header sanitization.", "components": ["render", "fly", "vercel", "heroku", "fly-pinned", "railway", "express", "django"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853", "render:s5b8400c2a2ba", "vercel:s3e7832fd3031", "heroku:s0c5bf300cef4", "express:s5bc62e66824b", "django:sb5e26f65fd91", "fly-pinned:s6e9a7292860d", "fly-pinned:sa63b828c93df", "fly-pinned:s4324a02dbc42", "fly-pinned:scf2e6f3bce02", "railway:sbf08758c106a", "railway:s844d338bd121"], "status": "REASONED"},
    "proxy-awareness": {"text": "Configure Express trust proxy or Django SECURE_PROXY_SSL_HEADER so secure cookies and redirects work behind the platform.", "components": ["render", "fly", "vercel", "express", "django"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853", "express:s5bc62e66824b", "django:sb5e26f65fd91"], "status": "REASONED"},
    "listener-port": {"text": "Railway advises 0.0.0.0 on injected PORT; listener rules vary by deployment, with IPv6/dual-stack recommended for Heroku Fir Private Spaces. Cited pages do not establish Vercel Functions' listener/port contract or Heroku Cedar's listener address; this guide's advice: bind nothing else and do not open extra listeners.", "components": ["render", "fly", "vercel", "heroku", "fly-pinned", "railway"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853", "render:s1820ac471b6c", "vercel:s22498401f5d0", "heroku:s370d4beec29a", "heroku:s211f5fe76042", "fly-pinned:s62fec91543a1", "fly-pinned:s61c1e50d2c11", "railway:sac1383056b65", "railway:s0462eef65b1b"], "status": "REASONED"},
    "database-identity": {"text": "Where supported, require TLS certificate/hostname verification with PostgreSQL sslmode=verify-full or MySQL --ssl-mode=VERIFY_IDENTITY.", "components": ["render", "mysql-client"], "sources": ["render:se240afec8d2d", "mysql-client:s823c0bfaaafa"], "status": "REASONED"},
    "render-internal-tls": {"text": "Render internal PostgreSQL TLS is optional and supports neither verify-ca nor verify-full; sslmode=require prevents plaintext fallback but is not identity verification.", "components": ["render"], "sources": ["render:se240afec8d2d"], "status": "REASONED"},
    "database-network": {"text": "Render Postgres external access is open to any IP by default; prefer private connectivity and disable or source-restrict external access. Keep database credentials in the secret store.", "components": ["render"], "sources": ["render:se240afec8d2d"], "status": "REASONED"},
    "spaces-creation": {"text": "This guide's advice: explicitly select and verify visibility when you create a Space. The pinned docs describe public, protected, and private visibility; public visibility exposes both the source and the running app, and duplicating a Space defaults to private. At the time of writing, the pinned Advanced Security docs attach repository visibility controls to Team & Enterprise organizations: Public by default creates new repositories with public visibility; Private by default creates new repositories with private visibility, and changing that setting does not affect existing repositories; Private only enforces private visibility for all new repositories, with only organization admins able to change visibility settings. Those lines do not establish a general creation default or a retroactive conversion of existing repositories by Private only.", "components": ["spaces", "spaces-pinned"], "sources": ["spaces:sda0c810c053d", "spaces-pinned:se2fb4e2a5c02", "spaces-pinned:s9d332f0940e2", "spaces-pinned:s969a28a4c44e"], "status": "REASONED"},
    "spaces-public": {"text": "Public Spaces expose both source and running app.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-protected": {"text": "Protected Spaces keep source private to owner/collaborators but expose the app via embed URL or custom domain; the recorded requirement is PRO for personal accounts or Team/Enterprise for organizations.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-private": {"text": "Private Spaces restrict both source and running app to the owner and collaborators.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-secrets": {"text": "Use Settings secrets for sensitive values, never repository/README metadata; variables remain publicly readable.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d", "spaces:sd5ec2b2772e0"], "status": "REASONED"},
    "spaces-static": {"text": "Static Spaces expose both variables and secrets to client JavaScript through window.huggingface.variables; keep backend/provider credentials in Docker/Gradio Spaces or another server-side service.", "components": ["spaces"], "sources": ["spaces:sda0c810c053d"], "status": "REASONED"},
    "spaces-dev": {"text": "At the time of writing, the pinned Dev Mode docs require PRO or Team & Enterprise. The Dev Mode Docker image starts the application as a subprocess and starts an SSH server for local editors and terminals and a VS Code server for in-product VS Code Web. Dev Mode exposes the running Space as a standard SSH host; clients use the Space subdomain shown in the Dev Mode controls as the username at ssh.hf.space, and local VS Code uses Remote - SSH to connect to the same host. SSH requires adding the machine's SSH public key to the user's Hugging Face account; these docs do not establish which users or roles may connect, or the access control for in-product VS Code Web. This guide's assessment: access into the running container is materially more access than the app itself, so treat an unattended Dev Mode session the same as any other exposed admin path.", "components": ["spaces", "spaces-pinned"], "sources": ["spaces:sda0c810c053d", "spaces-pinned:s5d393b019bad", "spaces-pinned:sd1ae2b703a70"], "status": "REASONED"},
    "verify-redirect": {"text": "This guide's HTTP HEAD / check requires 301/302/307/308 with an HTTPS Location; Vercel documents 308 and Fly HTTP handlers 301 with force_https, but Render's code, Railway HEAD, and Heroku's redirect policy are unestablished. The spot-check proves neither every route/method nor secure-cookie proxy awareness.", "components": ["vercel", "render", "fly-pinned", "railway", "heroku"], "sources": ["vercel:s2b470a6bc853", "vercel:s3e7832fd3031", "render:s5b8400c2a2ba", "fly-pinned:s4324a02dbc42", "railway:sbf08758c106a", "railway:s844d338bd121", "heroku:s0c5bf300cef4"], "status": "REASONED", "verify": [1]},
    "verify-app-auth": {"text": "Disable Vercel deployment protection or use its documented Protection Bypass for Automation, the x-vercel-protection-bypass header or query parameter carrying the project's generated secret, to isolate app auth; no Render or Fly equivalent is cited. This guide's expected reading: anonymous protected requests get the app's 401/403, valid app credentials a 2xx, and a platform SSO 401 is not app enforcement.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:s845513031876", "vercel:sc1588029e14e"], "status": "REASONED", "verify": [1]},
    "verify-secrets": {"text": "Scan history, working tree and deployed client JS, source maps, generated config and runtime values for every credential type; no matches is evidence, not proof. The scan procedure is this guide's, delegated to secrets.md; the pinned Next.js v16.4.2 lines document only the NEXT_PUBLIC_ build-time inlining and off-by-default production browser source maps that motivate the bundle scan.", "components": ["render", "fly", "vercel", "nextjs-pinned"], "sources": ["render:s213783ba6209", "fly:s1b202c527f2e", "vercel:s2b470a6bc853", "nextjs-pinned:s0e3d2cd2248e", "nextjs-pinned:sf7cfdc553311"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
