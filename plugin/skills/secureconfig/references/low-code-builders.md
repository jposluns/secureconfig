# Low-code internal-tool builders: NocoDB, Baserow, Appsmith, Budibase, and Windmill

NocoDB, Baserow, Appsmith, Budibase and Windmill are low-code platforms for building internal tools and automations; Windmill also runs scripts. This guide helps your AI assistant deploy them securely, including private instances behind a login proxy, first admin accounts secured before exposure, sign-up restricted where open, and shipped default secrets replaced.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/low-code-builders.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against NocoDB 2026.09.0, Baserow 2.3.4, Appsmith v2.4.1, Budibase v3.50.0 and v3.46.0, Windmill v1.864.1, Docker CLI v27.2.0 and v27.1.2, Node.js v22.22.1, and CouchDB 3.5.2, plus 3 more recorded bases; 1 further source is pinned to a commit and 5 carry no recorded version. Metadata reviewed 2026-11-26; documentation checked September 2026. The guide records 101 claims: 1 demonstrated by a check that ran; 100 reasoned from cited sources and any earlier-form run (not a live demonstration of the shipped form).

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

These tools sit on top of your databases and APIs and let people build internal apps, forms and
automations quickly. That is also the exposure. Each one stores credentials for the systems it connects
to, and Windmill runs arbitrary code by design. Three first-run patterns recur. On a fresh instance, the
first visitor becomes the administrator. Open signup is on by default. And the vendor's own sample
configuration ships fixed secrets that too many deployments keep. Keep every one of them private
([docker.md](docker.md), [cloud-firewalls.md](cloud-firewalls.md), [tunnels.md](tunnels.md)), claim the
admin account before the instance is reachable, and front the web UI per
[fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md). Treat the database
behind each tool as a store of every connected system's credentials ([secrets.md](secrets.md)).
Versions checked: NocoDB 2026.09.0, Baserow 2.3.4, Appsmith v2.4.1, Budibase v3.50.0 and Windmill
v1.864.1.

Each tool's password login also needs a brute-force control. What the tools do themselves ranges from
nothing (NocoDB, Baserow), through Windmill's always-on global cap, which counts every client together,
with optional per-address and per-account limits, to Appsmith's per-username limit and Budibase's
per-email and per-address lockouts, as each section below says, so rate-limit the login endpoints at
the reverse proxy in front of the tool, keyed per client address.
[nginx.md](nginx.md#4-bound-the-expensive-endpoints) shows a per-address request limit, which answers
503 once its burst is spent. Caddy's standard build has no rate limiting
([caddy.md](caddy.md#4-bound-the-expensive-endpoints)), so do not assume the Caddy that Baserow,
Appsmith and Windmill bundle can do it: put the limit in a proxy that can, or check that the binary
carries the community module. A per-address key is only as good as the address the proxy sees: behind a
CDN or another proxy, recover the client address first, as nginx.md describes, or every client shares
one bucket. Item 9 of [authentication.md](authentication.md) also warns that per-client rate limits do
not stop distributed credential stuffing (valid breached passwords spread thin across many addresses),
so add account-aware and aggregate abuse controls alongside the per-address limit. Then add fail2ban on
the proxy's access log. That is this guide's advice: item 9 requires fail2ban for SSH and, beyond SSH,
says other login panels still require suitable filters and logs. The shipped jails it lists do not
cover these tools' login failures, so write a filter that matches each tool's login path and failure
status, treat the shipped entries as starting points, and check the filter against your own log so
that it matches failed logins and not successful ones (this guide's advice). Appsmith answers failed
and successful form logins alike with a redirect, so this guide gives no Appsmith filter. A per-account
lockout also lets anyone who knows a username lock that user out, so it does not replace the
per-address limit. Two checks under Verify, the login-limit block and the fail2ban block after it, test the proxy limit and then the fail2ban jail.

## NocoDB

NocoDB listens on port 8080 (`process.env.PORT || '8080'`), and its entry point calls `listen` with no
host. For an omitted host, Node "will accept connections on the unspecified IPv6 address (`::`) when IPv6
is available, or the unspecified IPv4 address (`0.0.0.0`) otherwise", so the server listens on every
interface; its code passes no host, so NocoDB offers no bind setting. Restrict it with the container
publication or a firewall. The first account to sign up gets the super-admin role, and later self-signups are allowed
unless invite-only signup is on; `invite_only_signup` defaults to `false`. Claim the admin account first,
or seed it with `NC_ADMIN_EMAIL` and `NC_ADMIN_PASSWORD`, then turn on invite-only signup.

Two secrets need your attention:

- **`NC_CONNECTION_ENCRYPT_KEY`.** When it is unset, the encryption helper returns the value unchanged,
  so the credentials of every external database you connect are stored in plaintext in NocoDB's meta
  database. Set it before connecting a data source; when it is set later, NocoDB encrypts the existing
  sources on startup.
- **`NC_AUTH_JWT_SECRET`.** When it is unset, NocoDB generates a UUID, stores it in the meta database
  as `nc_auth_jwt_secret` and uses it, which is fine. The README's Docker example hard-codes one literal
  value (`569a1821-0a93-45e8-87ab-eb857f20a010`), so everyone who copies that example signs sessions
  with the same key. Generate your own.

At 2026.09.0, [`rspack.timely.config.js`](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/rspack.timely.config.js) builds `docker/main.js`, which the [start script](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start.sh) runs, from [`src/run/timely.ts`](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/timely.ts). That file and the other [entry file](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts), `src/run/dockerEntry.ts`, both call `cors()` with no options before any NocoDB route, and the [cors middleware](https://github.com/expressjs/cors/blob/v2.8.5/lib/index.js) then defaults to the origin `*`. So every response that passes through the cors middleware, preflights included, carries `Access-Control-Allow-Origin: *` and no `Access-Control-Allow-Credentials`, whatever `Origin` the request sends; NocoDB's lockfile resolves cors only as 2.8.5. The pinned tree has no Dockerfile, so which script the published image runs was not verified.

NocoDB's [global guard](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/guards/global/global.guard.ts#L21) authenticates a request by the `xc-auth` header or the `nc_token` cookie, which the [cookie helper](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/helpers.ts#L34-L58) sets as `httpOnly` and `SameSite=Lax`, for the path `/api`. API tokens arrive in the `xc-token` or `Authorization: Bearer` header ([token strategy](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L17-L18)). Because the `*` comes without `Access-Control-Allow-Credentials`, browsers do not let a page on another site read a response to a request sent with credentials, as [cors.md](cors.md) explains, and such a page does not know a user's `xc-auth` or `xc-token` value to send (this guide's reading). What remains, by this guide's reading, is that a page on another site that a user visits can read, through that user's browser, NocoDB responses that need no credentials, which can include an instance on an internal network if that browser can reach it and lets the request through. Which other routes answer an unauthenticated guest, and whether cross-site requests that change data succeed, which is a CSRF question rather than a CORS one, are not traced here.

Since [cors.md](cors.md) keeps a wildcard for public, unauthenticated, read-only resources only, remove the header at the reverse proxy in front of NocoDB, and check the result with the NocoDB CORS block under Verify. NocoDB serves its own GUI from the same server ([`timely.ts`](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/timely.ts) mounts it with `express.static`), so that GUI needs no CORS header (this guide's reading). In nginx, `proxy_hide_header` "sets additional fields that will not be passed" from the proxied server's response to the client ([proxy module](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)); put it in the `location` that holds `proxy_pass`, as in [nginx.md](nginx.md):

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;               # NocoDB's port, published on loopback only
    proxy_hide_header Access-Control-Allow-Origin;  # drop NocoDB's "*" before the response reaches browsers
}
```

Put the `proxy_hide_header` line in every `location` that proxies to NocoDB, because the Verify block probes only the one path you give it.

In Caddy, the `reverse_proxy` subdirective `header_down` "deletes (with the `-` prefix)" a field "in a response header coming downstream from the backend" ([reverse_proxy directive](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)), in a site block like those in [caddy.md](caddy.md):

```caddyfile
nocodb.example.com {
    reverse_proxy 127.0.0.1:8080 {
        header_down -Access-Control-Allow-Origin   # drop NocoDB's "*"
    }
}
```

If one browser app on another origin must read NocoDB, keep the `proxy_hide_header` line and add `add_header Access-Control-Allow-Origin "https://app.example.com" always;` to that `location`, because `add_header` "Adds the specified field" rather than replacing NocoDB's. In Caddy, replace the deletion with `header_down Access-Control-Allow-Origin "https://app.example.com"`, which sets it. Nginx inherits `add_header` directives from the previous level "if and only if there are no `add_header` directives defined on the current level" ([headers module](https://nginx.org/en/docs/http/ngx_http_headers_module.html)), so repeat the server's own `add_header` lines, such as the HSTS line in [nginx.md](nginx.md), in that `location`. With `always`, the field "will be added regardless of the response code", per the same page.

Both entry files also enable Express's `trust proxy`, but startup then
resets that from [`NC_TRUST_PROXY`](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts), which trusts no proxy unless you set it; once a proxy is in front,
set it to that proxy's hop count or subnet, and never to `true` on a server clients can reach directly. The 2026.09.0 tag's README says binaries are only for quick local testing ([README, line 95](https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L95)).
The GitHub release API record listed no assets when checked in October 2026 ([release record](https://api.github.com/repos/nocodb/nocodb/releases/tags/2026.09.0)); this guide assesses that record as showing no 2026.09.0 GitHub release binary assets, without establishing what other download services provide. The tag carries NocoDB package version `0.301.3` ([package manifest](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/package.json#L3)); `2026.09.0` is the tag name, not that package version. The README documents the `nocodb/nocodb:latest` Docker image ([Docker examples](https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L56-L75)) and calls Auto-upstall a server production installation that generates Docker Compose ([Auto-upstall section](https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L77-L90)). For production, use the container image or the vendor's install script (this guide's advice based on those README paths). The README's Auto-upstall command fetches the script over plain `http://` and runs it with Bash ([README command](https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L82)); its source link points to the `develop` branch ([README source link](https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L90)). This guide advises fetching the script over HTTPS from a pinned, reviewed source and reading it before running it, rather than running the plain-HTTP response directly with Bash.

NocoDB does not limit login attempts itself. At 2026.09.0, the guard on its sign-in route,
`PublicApiLimiterGuard`, always lets a request through, and its comment says "Rate limiting is intentionally not enforced at the application layer.
Deployments are expected to apply rate limits at the network layer (reverse proxy, load balancer, WAF,
or API gateway)". Sign-in is served on four paths, `/auth/user/signin`, `/api/v1/db/auth/user/signin`,
`/api/v1/auth/user/signin` and `/api/v2/auth/user/signin`, so the proxy limit has to cover all four,
for example by matching the shared `/auth/user/signin` suffix. Its local sign-in strategy reads `email` and
`password` and answers bad credentials with a bad-request error. NocoDB's two-factor authentication page
says "Two-factor authentication is available on all NocoDB Cloud plans and on licensed self-hosted
deployments (Business plan and above)." That page is not tied to a release. It also says that after 5
failed verification attempts in a row, NocoDB locks the account for 15 minutes. At the 2026.09.0 tag, a
migration adds the `totp_secret`, `totp_enabled` and `totp_backup_codes` columns, but this guide's
search of `packages/nocodb/src` at the tag found no TOTP setup or verification endpoint;
whether the open build can enable two-factor authentication was not established. Without that licence, put MFA in front of NocoDB
([fronting-auth.md](fronting-auth.md)).

NocoDB's server sends webhooks to URLs that users configure. At 2026.09.0, a self-hosted build filters webhook requests with the `request-filtering-agent` library ([SSRF helper](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L2-L6)), whose filtering agents the webhook invoker attaches to each webhook request that has a URL ([webhook request agents](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L178)). When an invocation is set to throw on failure and the request error mentions a private IP address, NocoDB raises "Connection to a private network IP is blocked for security reasons", and it appends a hint to set `NC_ALLOW_LOCAL_HOOKS=true` only when `!isEE || isOnPrem` holds ([webhook error](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L738-L751)). Which callers set the throw option, and which builds those two flags match, were not traced here, so a failed webhook may not show this text or the hint (this guide's reading). The [SSRF switch](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L23-L49) keeps the filter on unless `NC_DISABLE_SSRF_PROTECTION` is `true`, which turns it off for every source, or, for webhooks only, `NC_ALLOW_LOCAL_HOOKS` or `NC_WEBHOOK_ALLOW_PRIVATE_NETWORK` is `true`. The same switch turns SSRF protection off for external-database sources when `NC_ALLOW_LOCAL_EXTERNAL_DBS` is `true` and for data imports when `NC_ALLOW_LOCAL_DATA_IMPORT` is `true`; where those two sources apply the switch was not traced here. Each variable is compared with the exact string `true`, and NocoDB Cloud ignores all five (this guide's reading of the switch). Leave all five unset, and remove them from every environment and Compose file the deployment uses (this guide's advice). The filter is not an egress policy: filter the server's outbound traffic at the network as well ([egress-metadata.md](egress-metadata.md); this guide's advice).

Shared views and shared bases give link holders access without a NocoDB account (this guide's reading: the shared-view controller carries only the `PublicApiLimiterGuard` guard ([shared-view routes](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L21-L31)), and what a shared base link reaches was not read). The public row routes of a shared view accept the view's password in an `xc-password` header ([public data controller](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L40)), and the password is optional, so a view shared without one is readable by anyone who has the link (this guide's reading). A base's shared link is removed through the base's `/shared` endpoint, whose action is `disableSharedBaseLink` ([shared base controller](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/shared-bases.controller.ts#L75-L80)). Where each view's share setting lives was not read, and this guide's search of `packages/nocodb/src` and `nocodb-sdk` at the tag for `NC_.*SHARE` and `DISABLE_.*SHARE` found no environment variable that turns sharing off for the whole instance. Before exposing the instance, review each base's shared views and shared base link, set a password on a view that must stay shared, and remove the links nobody needs (this guide's advice).

API tokens authenticate in the `xc-token` header or, when that header is absent, in `Authorization: Bearer` ([token header helper](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/apiHelpers.ts#L75-L94)). A token request never passes the sign-in route, so MFA at a fronting proxy covers it only if the proxy also requires its login on the `/api` paths (this guide's reading). A token minted for one base carries that base's `base_id` and is refused on requests that target another base, while a token with no `base_id` is account-wide; the check applies only to requests that resolve a base, and workspace or organization routes are left to the normal role checks ([base scope](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L29-L38)). A token acts with its creating user's roles ([token user](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L50-L69)), and an old token with no owning user gets the editor role ([legacy tokens](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L44-L46)). The token model has `permissions` and `expiry` fields ([token model](https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/models/ApiToken.ts#L26-L28)), but whether NocoDB enforces either was not traced here. So do not rely on an expiry to retire a token (this guide's advice). Prefer base-scoped tokens, though the scope does not narrow workspace or organization routes, and revoke every token that no one uses (this guide's advice).

## Baserow

Baserow's default [Compose file](https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml) publishes the bundled Caddy on 80 and 443 at
`${HOST_PUBLISH_IP:-0.0.0.0}`, so every interface unless you set `HOST_PUBLISH_IP`. The vendor's install
guide warns that "docker when exposing ports on 0.0.0.0 will bypass any ufw firewall rules", and
suggests `-p 127.0.0.1:80:80 -p 127.0.0.1:443:443` if public exposure is not intended. The first user
to sign up is made staff (`is_staff=not User.objects.exists()`), and new signups are allowed by default
(`allow_new_signups` defaults to `True`). Sign up first, then turn off new signups in the admin
settings; a refused signup then fails with "Sign up is disabled."

The Compose file refuses to start without `SECRET_KEY`, `DATABASE_PASSWORD` and `REDIS_PASSWORD`
(`${SECRET_KEY:?}`), and `.env.example` leaves them empty rather than shipping examples, so the secrets
are yours to generate. Baserow's core registers a TOTP two-factor authentication provider.

The login view, `ObtainJSONWebToken`, documents that an account protected by two-factor authentication
gets a temporary token with which to finish verification. Whether an administrator can require TOTP for
every account was not established, so do not rely on it as instance-wide MFA; put MFA in front of Baserow ([fronting-auth.md](fronting-auth.md)). The same view, served at
`/api/user/token-auth/`, reads `email` (or the deprecated `username`) and `password` through
`TokenObtainPairWithUserSerializer`. Neither the view nor that serializer sets a throttle of its own, a
failed-attempt counter or a captcha; Baserow checks a captcha only on sign-up. The view answers bad
credentials with 401 (`ERROR_INVALID_CREDENTIALS`). The optional throttle in Baserow's settings
(`BASEROW_MAX_CONCURRENT_USER_REQUESTS`, default `-1`, which is off) limits concurrent requests, and
it skips requests from anonymous users unless `BASEROW_THROTTLE_IP_ENABLED` is set; it does not count
failed logins or lock accounts. The proxy limit is therefore the only brute-force control in front of
Baserow's login (this guide's reading of the view, its serializer and the throttle).

Baserow's backend sends three kinds of outbound HTTP request whose targets users configure: webhooks, integration requests and data syncs, and at 2.3.4 each has its own private-address setting. Webhooks and integration requests go through the `advocate` library, which the code's comments say keeps the internal network out of reach, unless [`BASEROW_WEBHOOKS_ALLOW_PRIVATE_ADDRESS`](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1186-L1188) or [`BASEROW_INTEGRATIONS_ALLOW_PRIVATE_ADDRESS`](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1217-L1219) is on ([webhook request helper](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/webhooks/validators.py#L28-L38), [integration request helper](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/integrations/utils.py#L19-L22)). Both settings are read with `bool(os.getenv(...))`, so any non-empty value turns the allowance on, `false` and `0` included. The [configuration documentation](https://github.com/baserow/baserow/blob/2.3.4/docs/installation/configuration.md#L146-L149) says so for the webhook setting ("If set to any non empty value allows webhooks to access all addresses") and calls enabling it a security risk. Leave both unset rather than set to `false`, and remove them from every environment and Compose file the deployment uses (this guide's advice). For a webhook that must reach one internal host, the same documentation points to `BASEROW_WEBHOOKS_URL_REGEX_BLACKLIST`, `BASEROW_WEBHOOKS_IP_WHITELIST` and `BASEROW_WEBHOOKS_IP_BLACKLIST`, which it says are disabled once `BASEROW_WEBHOOKS_ALLOW_PRIVATE_ADDRESS` is set.

Data sync is exposed by default. [`BASEROW_DATA_SYNC_ALLOW_PRIVATE_ADDRESS`](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1220-L1222) defaults to `true`, and while it is true the [data sync request helper](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/data_sync/utils.py#L20-L32) sends with plain `requests` instead of `advocate`; its comment keeps that default "for backwards compatibility". So on a default install a data sync URL can reach Baserow's internal network, which that comment names SSRF (this guide's reading; not tested). Set the variable to a false value. It is parsed with `str_to_bool`, whose accepted spellings this guide did not read, so confirm on a test instance that a data sync to a private address is refused (this guide's advice). None of these settings is an egress policy: filter the backend's outbound traffic at the network as well ([egress-metadata.md](egress-metadata.md); this guide's advice).

A view becomes readable at a public URL when its `public` flag is set; the flag defaults to false, and an optional `public_view_password` guards the URL ([view model](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/views/models.py#L109-L122)). Before exposing the instance, review which views are public and set a password on any that must stay public (this guide's advice). Database tokens authenticate requests that carry an `Authorization: Token` header ([token authentication](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/api/tokens/authentications.py#L21-L23)) to the row create, read, update and delete endpoints ([token model](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L19-L21)). Each token's permissions cover one table, one database or every table in the token's workspace ([token permission model](https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L75-L82)). A token request never passes the login view, so MFA at a fronting proxy covers it only if the proxy also requires its login on the API paths (this guide's reading).

## Appsmith

Appsmith's Java server binds to `127.0.0.1` on 8080 by default (`APPSMITH_SERVER_ADDRESS`), inside a
container fronted by a bundled Caddy on port 80. The vendor's development Compose file publishes that
on host port 8080, and its AWS example on 80 and 443. Signup is enabled by default
(`APPSMITH_SIGNUP_DISABLED` defaults to `false`). On a fresh instance, the first user to sign up claims
the super-user slot while no users exist. Claim it before exposing the instance, then set
`APPSMITH_SIGNUP_DISABLED=true` or restrict signup with `APPSMITH_SIGNUP_ALLOWED_DOMAINS`; a refused
signup gets the `SIGNUP_DISABLED` error, "Signup is restricted on this instance of Appsmith".

Datasource credentials are encrypted with `APPSMITH_ENCRYPTION_PASSWORD` and
`APPSMITH_ENCRYPTION_SALT`. On first start, the image's entrypoint generates random 13-character values
for both. But the vendor's development Compose file sets both to `abcd`, and values passed from outside
override the generated ones. Anyone who copies that file encrypts every stored datasource credential
with a published key. Remove those two lines, or set long random values, before the first start. On an
instance that already stored credentials under `abcd`, changing the pair presumably leaves them
unreadable, so plan to re-enter them (inferred from the encryption design, not tested).

Appsmith limits form logins at `/api/v1/login` per submitted username: 5 attempts per day, after which
the login redirects to `/user/login?error=true` with a message instead of answering 429. Because the
limit is keyed on the username and not on the client, one client can try many usernames, and anyone
who knows a username can lock it out of form login for up to a day. This guide found no setting that
changes the limit. Rate-limit the login path per client address at the proxy as well. This guide's
search of the v2.4.1 server and client sources found no native MFA. The vendor's authentication
documentation lists Google, GitHub, OIDC and SAML sign-in besides form login; this guide has not
established which edition includes each. Put MFA in an identity provider that enforces it, or in front
of Appsmith ([fronting-auth.md](fronting-auth.md)).

At v2.4.1, Appsmith's server checks the targets of REST, GraphQL, SaaS and other WebClient-based plugins, the Elasticsearch plugin, Redis connections and the SMTP test email against a [restricted-host filter](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L21-L39). The filter is not applied to the JDBC plugins (Postgres, MySQL, MSSQL, Oracle, Redshift, Snowflake and Databricks), Mongo, ArangoDB or the SMTP send path. It refuses nine cloud-metadata hosts, among them `169.254.169.254` and `metadata.google.internal`, and the loopback literals `127.0.0.1` and `::1` ([blocked hosts](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L152-L177)). It also refuses loopback, any-local, link-local and multicast addresses, IPv6 unique local addresses (`fc00::/7`) and IPv6 forms that carry an IPv4 address in one of those classes ([address classes](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L705-L740)). Before the host check, IPv4-mapped, IPv4-compatible, IPv4-translated, NAT64 (`64:ff9b::/96`) and 6to4 forms are reduced to the IPv4 address they carry, so the host list also covers those forms of its IPv4 entries ([normalization](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L783-L835)). The check runs again on the address a hostname resolves to at connection time, so a name that resolves to a blocked address is refused too ([resolver check](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L671-L695)). Private IPv4 addresses (RFC 1918: `10.0.0.0/8`, `172.16.0.0/12` and `192.168.0.0/16`) are allowed by design, so that datasources and mail servers on private networks keep working ([datasource comment](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L105-L108), [mail server comment](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L401-L402)). For datasources, the filter still refuses the hosts of Appsmith's internal Redis and, on a best-effort basis, the instance's own address ([internal Redis](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L91-L93), [own address](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L109-L117)).

The server's code reads one environment-variable switch for the filter, `APPSMITH_DISABLE_SSRF_FILTER`: the filter is on unless that variable, or the JVM system property `appsmith.test.bypass.ssrf` that the test JVM sets, is `true`, in any letter case ([opt-out](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L53-L58), [test switch](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L60-L62), [switch](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L179-L182)). Set to `true`, it skips every check above at once ([disabled filter](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L67-L69)). The blocked list is a constant in the code ([blocked list](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L80)), and this guide found no environment variable that adds hosts to it or replaces it. Leave `APPSMITH_DISABLE_SSRF_FILTER` unset (this guide's advice). The filter allows private IPv4 addresses and skips the database plugins, so it is not an egress policy: filter the server's outbound traffic at the network as well ([egress-metadata.md](egress-metadata.md); this guide's advice).

Making an application public gives anonymous visitors read access to the application ([public view](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L567-L600)) and, through inherited policies, read access to its pages and theme and execute access, not read access, to its queries ([inherited policies](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L681-L713), [permission graph](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/acl/ce/PolicyGeneratorCE.java#L220-L244)). It also gives them execute access to the datasources its queries use, apart from datasources that other applications in the same workspace, readable by the same public role, already use ([datasource grant](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L602-L679)). That grant does not require the person who makes the application public to hold any permission on those datasources (this guide's reading of its code comment). The query execute endpoint accepts requests without a login ([public routes](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L285-L316)), and an anonymous caller can run only published queries ([view mode](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L555-L566), [published only](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L963-L972)). Each run of a query on a saved datasource loads the datasource's saved configuration ([datasource lookup](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L686-L695), [saved configuration](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/datasourcestorages/base/DatasourceStorageServiceCEImpl.java#L116-L127)), so anyone with the link can run the application's published queries with the datasource's saved credentials (this guide's reading). This guide did not establish whether a public application's responses reveal those credentials. Make an application public only when every query it publishes is safe for anyone to run, and give its datasources an account limited to what those queries need (this guide's advice).

This guide's search of the v2.4.1 server tree found no personal access token or general API key; the only bearer credential a user can create is an MCP token. A user creates, rotates, lists and revokes MCP tokens under `/api/v1/users/mcp-tokens` ([URL constant](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/UrlCE.java#L37)), and only from a signed-in session, not with a token ([token controller](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/controllers/ce/McpTokenControllerCE.java#L29-L85)). A token lasts 30, 60, 90, 180 or 365 days ([lifetimes](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L45-L46)), the Community Edition allows 2 live tokens per user ([per-user limit](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L73-L76)), and the server stores only a hash of each token ([hash and expiry](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L318-L320), [token record](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/domains/McpToken.java#L26-L27)). The server accepts an MCP token only when the request also carries an internal-marker header equal to the configured internal secret, and accepts none while that secret is unset; a code comment names the header `X-Appsmith-Mcp-Internal`, and a log message names the setting `APPSMITH_MCP_INTERNAL_SECRET` ([MCP bearer check](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/converters/McpTokenAuthenticationConverter.java#L35-L79)). A token acts as its owner, with the owner's permissions ([token sign-in](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/managers/McpTokenAuthenticationManager.java#L56-L72)). It works only on an allowlist of endpoints, which covers reading, importing (including partial import into an existing application) and publishing applications, creating, editing and deleting pages, queries and JS objects, editing page layouts and the application theme, listing and creating datasources, running queries and some Git branch and commit calls ([MCP allowlist](https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/filters/McpAllowlistWebFilter.java#L43-L90)). Treat each MCP token as its owner's login, keep the internal secret private, choose the shortest lifetime that works and revoke tokens nobody uses (this guide's advice).

## Budibase

Budibase's Compose file publishes its nginx proxy on `MAIN_PORT` (10000 in the sample `.env`) and its
LiteLLM service on `${LITELLM_PORT:-4000}`. The proxy forwards `/db/` to CouchDB (CouchDB upstream variable and proxy location sources below).
The sample `hosting/.env` sets `JWT_SECRET` and `API_ENCRYPTION_KEY` to `testsecret`, and the CouchDB, MinIO and
Redis passwords, `INTERNAL_API_KEY` and `LITELLM_MASTER_KEY` to `budibase`, under a comment that says
"These should be updated" (sample secret assignments source below).
This guide's October 2026 search of the full v3.46.0 tag with
`git grep -l testsecret v3.46.0` found exactly these five files:
`hosting/.env`, `hosting/digitalocean/files/var/lib/cloud/scripts/per-instance/001_onboot`,
`hosting/hosting.properties`, `packages/backend-core/tests/jestEnv.ts` and `scripts/dev/manage.js`.
This guide inspected those five files: sample assignments, first-boot substitution, test assignments
and development entries.
This guide's assessment is that those hits do not establish that production code never rejects the sample values;
no live safeguard test ran.
Compose maps `COUCH_DB_USER` and `COUCH_DB_PASSWORD` to the `COUCHDB_USER` and `COUCHDB_PASSWORD`
environment of `budibase/database:2.1.0`; the image version file also says `2.1.0`.
The Dockerfile installs the entrypoint and selects the runner, which invokes that entrypoint for CouchDB.
With both values non-empty, the entrypoint appends the admin credentials only if its existing-admin
check finds no entry for that name (CouchDB image and credential mapping, entrypoint installation,
runner command, image version file, runner call and conditional admin creation sources below).
With the sample file unchanged and that creation condition met, anyone who can reach the proxy can try
`budibase`/`budibase` against CouchDB through `/db/`.
Compose pins `docker.io/litellm/litellm:main-v1.83.10-stable.patch.3` and passes `LITELLM_MASTER_KEY`
(LiteLLM image and environment source below); acceptance of `budibase` by that image is not established.
This guide has not established that [litellm.md](litellm.md)'s pinned source
`6ef7b86748118ceecd95271727c2fa167ce55fec` corresponds to that image; no LiteLLM source for that image was fetched.
Replace every one of those values before the first start.

The first-run admin route `POST /api/global/users/init` is public (public init endpoint entry and
public authentication middleware chain sources below).
Its controller calls `checkAnyUserExists()` inside `tenancy.doInTenant(tenantId, ...)` using the request's
`tenantId`; a truthy result produces HTTP 403 with "You cannot initialise once an global user has been created."
(admin-init controller and refusal source below).
The helper is imported from `packages/worker/src/utilities/users.ts`, which was not fetched;
which users count and any multi-tenancy exception in that helper remain unestablished.
The route's `buildAdminInitValidation()` runs before `controller.adminUser`; it requires string `email`
and `tenantId` fields, allows an optional password and rejects unknown fields
(admin-init body validator and middleware order sources below).
This guide assesses this POST as unsafe for read-only claimed-state probing: invalid bodies can fail
validation in both states, while accepted initialization creates an admin.
Create the admin before exposure, manually or with `BB_ADMIN_USER_EMAIL` and `BB_ADMIN_USER_PASSWORD`
(this guide's advice; admin environment definitions and app-service mapping sources below).
Startup attempts seeding only when `SELF_HOSTED` is truthy, `MULTI_TENANCY` is falsy and both values are
non-empty; in the `tenancy.getTenantId()` context, it calls `createAdminUser` when
`!checklist?.adminUser?.checked || !exists`, where `exists` is `users.doesUserExist(bbAdminEmail)`.
That call sets `hashPassword`, `requirePassword` and `skipPasswordValidation` to `true`
(startup admin seeding conditions source below).

At v3.46.0, Budibase's login route, `/api/global/auth/:tenantId/login`, carries two lockouts; the same
files exist at v3.50.0 but were not compared. The route's validator accepts a body of only `username`
and `password` and rejects any other field before either lockout runs, so a client must send exactly
those two. After `LOGIN_MAX_FAILED_ATTEMPTS` failures (default 5) for one email, it locks that email
for `LOGIN_LOCKOUT_SECONDS` (default 900, so 15 minutes) and answers 403 "Account temporarily locked.
Try again later." with `Retry-After`. Once one client address (`ctx.ip`) has sent more than
`LOGIN_IP_LOCKOUT_LIMIT` login requests (default 10) in that window, it answers 429 "Too many login
attempts. Try again later."; that count includes every login request that passes the validator, not
only failures. The email lockout lets anyone who knows a user's email lock that user out, 15 minutes at
a time. How `ctx.ip` resolves behind the bundled nginx proxy was not verified: if it is the proxy's
address, every client shares one count, and 11 login requests from anyone would block every login for
up to 15 minutes (this guide's inference, not tested). This guide's search of the v3.46.0 packages and
of a v3.50.0 source tree found no native MFA. Put MFA in front of Budibase
([fronting-auth.md](fronting-auth.md)), or, if users sign in through an identity provider, have that
provider enforce it.

At v3.50.0, Budibase's outbound blacklist blocks these ranges by default: `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `100.64.0.0/10`, `169.254.0.0/16`, `0.0.0.0/8`, `::1/128`, `2001::/32`, `64:ff9b:1::/48`, `fc00::/7` and `fe80::/10` (blacklist defaults source below). It also checks the IPv4 address carried inside IPv4-compatible, NAT64 and 6to4 IPv6 addresses (blacklist check source below). At v3.50.0, REST datasource requests and the outgoing-webhook automation step call `fetchWithBlacklist`, which checks every address the host resolves to against the blacklist before each request, redirects included (REST request, outgoing webhook step and `fetchWithBlacklist` definition sources below). At v3.46.0 the IMAP email trigger's host check uses the blacklist too; that file was not read at v3.50.0 (IMAP host check source below). Other outbound paths, such as SMTP, the database datasources and file or URL imports, were not traced, so this guide does not treat the blacklist as covering all outbound traffic. When `SELF_HOSTED` is on, setting `BLACKLIST_IPS` replaces the default ranges instead of adding to them, and an empty value disables them, as the code's own comment says (blacklist replacement and blacklist build sources below). So on a self-hosted instance `BLACKLIST_IPS=203.0.113.0/24` leaves loopback, the RFC 1918 ranges and the `169.254.169.254` metadata address reachable on those paths (this guide's reading). Leave `BLACKLIST_IPS` unset, or, when you set it, list every default range above along with your own entries (this guide's advice); even then, by this guide's reading of the code, a set value makes the blacklist treat a host whose lookup fails other than on a parse error as not blocked, which weakens the IMAP host check (blacklist check source below). The blacklist is not an egress policy: filter Budibase's outbound traffic at the network as well ([egress-metadata.md](egress-metadata.md); this guide's advice).

At v3.46.0, Budibase's built-in PUBLIC role has the display name "Public user" and the description "Accessible to anyone" (PUBLIC role source below). Which tables, queries and screens an app grants to that role was not traced here, so review every resource assigned to PUBLIC before exposing the instance (this guide's advice). The automation webhook trigger route, `POST /api/webhooks/trigger/:instance/:id`, is registered under the comment "right now its always public" on the route group created with no middleware (webhook trigger route and public route group sources below). Whether the trigger's controller checks any token or secret was not traced, and these files were not read at v3.50.0. Treat each webhook trigger URL as a public endpoint that anyone who learns it can call without a secret, keep it out of logs and shared documents, and delete webhook automations nobody uses (this guide's advice).

At v3.46.0, each user has at most one API key: generating a key stores it in that user's developer-info record and replaces any earlier key (API key generation source below). Only builders can generate or fetch a key, because both routes sit in the worker's builder-only route group (API key routes and builder route group sources below). A valid key resolves to the user it belongs to, so a request made with it has that user's full rights, and a builder's key acts as a builder (API key check source below; this guide's reading). The code read shows no scope, expiry or per-app limit on a key: a new record the code read creates holds only its id, the user id and the key (API key generation source below). A key request does not pass the login route, so MFA at a fronting proxy covers it only if the proxy also requires its login on the API paths (this guide's reading). Treat each API key as its user's password, keep keys to accounts that need API access, and regenerate any key that may have leaked (this guide's advice).

## Windmill

Windmill runs scripts in Python, TypeScript, Go, Bash and more on its workers, so a Windmill login is
code execution on your worker hosts. The server listens on port 8000 on every interface by default
(`DEFAULT_SERVER_BIND_ADDR` is `0.0.0.0`; `SERVER_BIND_ADDR` changes it when you run the binary). In the
vendor's Compose file the server only `expose`s 8000 to the Compose network, and the bundled Caddy
publishes `80:80` and `25:25` on every host interface, so port 80 is where the login page is reachable.
A fresh database has one password user, `admin@windmill.dev`, a super admin whose password is
`changeme`; the README gives them as the default credentials.

On a v1.817.0 loopback run of the release binary with `SERVER_BIND_ADDR=127.0.0.1`, that was the only
password user in the fresh database, and it was a super admin. Logging in with `changeme` returned `200`
and a token, and `whoami` confirmed super-admin rights. After the password was changed, `changeme` got
`400` and the new password `200`. The server's only listener was on 127.0.0.1, at the test port the run
set. That run observed only the configured state: the default wildcard bind was not run, because the host forbids it, and none of this was re-run on v1.864.1. Change the password before anything else can reach the server. In Compose, bind Caddy's `ports:`
entries to `127.0.0.1` or a private address ([docker.md](docker.md)); `SERVER_BIND_ADDR=127.0.0.1` inside the
server container would presumably cut Caddy off from it (inferred, not tested).

The vendor's v1.864.1 [Compose file](https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L36) sets the Postgres password to `changeme`. Its [`.env`](https://github.com/windmill-labs/windmill/blob/v1.864.1/.env#L1) sets `DATABASE_URL=postgres://postgres:changeme@db/windmill?sslmode=disable`, which the Compose file passes to the server ([`DATABASE_URL` line](https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L55)). So the shipped connection both uses that well-known password and turns off TLS between Windmill and Postgres (`sslmode=disable`). Change the password in both files before the first start, keep the database on the Compose network or another private network, never on a public one, and if Postgres runs on another host, ask for TLS in `DATABASE_URL` instead of `sslmode=disable` (this guide's advice).

Windmill builds each workspace's cipher from a key that it reads from the `workspace_key` table of that same database ([key query](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L388-L396)). It appends the `SECRET_SALT` environment variable to that key only when the variable is set ([`SECRET_SALT`](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L26), [key handling](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L336-L357)). Without `SECRET_SALT`, a copy of the database or of its backups therefore holds both the encrypted values and the key their cipher is built from (this guide's inference; the cipher itself was not read). Set `SECRET_SALT` to a long random value on the server and every worker before any secret is stored, and keep it out of the database and its backups; setting or changing it later presumably leaves existing secrets unreadable (inferred from the key handling, not tested). Whenever a workspace has no cached cipher younger than 300 seconds, Windmill fetches its key and logs, at info level, a line that prints the first 8 characters of that key ([key handling](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L336-L357)). Treat Windmill's logs as sensitive: restrict who can read them and where they are shipped, as for any log that carries part of a secret (this guide's advice).

The worker sandbox is not on by default either. `DISABLE_NSJAIL` defaults to `true` in the [worker](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs), and
on that v1.817.0 loopback run, without nsjail installed, the worker logged "Nsjail sandboxing will NOT be
available". No run with nsjail enabled was made, so isolation was not observed, and none of this was re-run on v1.864.1. The vendor's [Compose file](https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml) runs the worker with `privileged: true` and publishes port 25 for
email triggers. Its debugger setting carries the vendor's warning: `REQUIRE_SIGNED_DEBUG_REQUESTS`
"Do NOT set to false on any internet-reachable deployment: it exposes an unauthenticated code-execution
debugger". Do not publish 25 unless you use email triggers. In that v1.864.1 [Compose file](https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L90-L99) the worker's volumes are its dependency cache and its logs, and the host Docker socket is not among them. The `/var/run/docker.sock` mount there is a commented-out line for the legacy full-compat `# docker` mode, which the file's own comment calls "trusted users only" and warns "grants user scripts full access to the host Docker daemon". Leave that line commented out, and if the legacy mode is required, treat every user who can write or deploy a script as having root on the host, as with any container that holds the Docker socket ([docker.md](docker.md)) (this guide's advice).

To turn the sandbox on, set `DISABLE_NSJAIL=false` on every worker: the worker's [sandbox check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1084-L1086) then returns true before it reads the instance's isolation setting, and the v1.864.1 [Dockerfile](https://github.com/windmill-labs/windmill/blob/v1.864.1/Dockerfile#L360) copies the `nsjail` binary into the image. Whether nsjail then works in the vendor's Compose worker, and whether it needs that worker's `privileged: true`, was not established from a pinned source, and no run with nsjail enabled was made. After the change, check that the worker no longer logs that nsjail sandboxing will not be available (this guide's advice). If it still logs that line, which it does at error level once `DISABLE_NSJAIL=false` is set, the worker could not run its test jail, did not find nsjail, or could not prepare or start the test jail ([other causes](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L586-L607)), and jobs that require nsjail then fail rather than run unsandboxed ([test jail](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L568-L584)). The vendor's [threat model](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/THREAT_MODEL.md#L140) at the tag says network isolation is an nsjail feature, "so outbound network from user code is unrestricted by default". Scripts therefore reach whatever the worker's network reaches, including a cloud metadata address unless the network blocks it (this guide's reading). The one exception at v1.864.1 is a script whose author adds the `no_network` annotation: nsjail then runs it without a network, and a worker that would not jail it refuses to run it rather than run it with the network ([no-network check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1094-L1122)). That annotation is a per-script opt-in, not an egress control (this guide's reading). Put workers on a network that reaches only what scripts need, and block the metadata address there ([egress-metadata.md](egress-metadata.md), [container-hardening.md](container-hardening.md)).

Windmill's login, `/api/auth/login`, is always under a global cap (`LOGIN_RATE_LIMIT_GLOBAL`, default
10000 login attempts a minute per server process), which counts every client together. A per-address
limit (`LOGIN_RATE_LIMIT_PER_IP`, default 120 a minute) and a per-account limit
(`LOGIN_RATE_LIMIT_PER_ACCOUNT`, default 30 failures a minute) apply only when `CLOUD_HOSTED` is on or
the variable is set to a number. Each of these minutes is the current clock minute, not a sliding 60
seconds, so a count starts again when the minute changes. The global and per-address limits also apply
to the login-link route, `/api/auth/login_link/{token}`. A wrong password gets 400 ("Invalid login");
only a login these limits reject gets 429 with "Too many login attempts. Please try again later." The per-address key comes from `X-Real-IP`,
else the first `X-Forwarded-For` entry, and without either there is no per-address limit. Set
`LOGIN_RATE_LIMIT_PER_IP` only behind a proxy that overwrites `X-Real-IP` with the peer address;
otherwise a client picks its own bucket by sending the header. This guide's search of the v1.864.1
backend and frontend sources found no native MFA. Put MFA in front of Windmill
([fronting-auth.md](fronting-auth.md)), or, if users sign in through an identity provider, have that
provider enforce it.

A Windmill app has one of four execution modes, `anonymous`, `guest`, `publisher` and `viewer`, and an app whose policy names none gets `publisher`, which requires a login ([execution modes](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L301-L319)). `anonymous` admits anyone without a login, and `guest` admits anyone the instance's identity provider signs in, workspace member or not ([access check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L381-L410)). In `anonymous`, `guest` and `publisher` mode the app's scripts and flows run with the publisher's permissions; only `viewer` mode runs them as the person viewing the app ([run identity](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4421-L4456)). The publisher is the identity in the app policy's `on_behalf_of`: the user who deployed the app, unless that user is allowed to preserve identities and either kept an earlier one or created the app in a folder that sets a default identity ([policy identity](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L6540-L6556), [identity on create](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2862-L2885), [identity on update](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3858-L3874)). A source deploy that sends no policy, and so claims no identity, and an update that changes only the mode both keep whoever the app already runs as ([identity kept](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3853-L3855), [policy carried over](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4036-L4047)). By default any user with write access can publish an app as `anonymous`: the `RestrictAnonymousAppDeployment` protection rule limits creating an anonymous app, or switching an app to `anonymous`, to admins and the rule's bypass users and groups, but only in a workspace where a ruleset enables it ([deployment rules](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L333-L342), [rule check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/workspaces.rs#L1442-L1475), [anonymous deployment test](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/tests/app_anonymous_execution_mode.rs#L3-L10)). The rule gates only a change into that mode: a user it restricts can still redeploy an app that is already `anonymous`, and `RestrictGuestAppDeployment` works the same way for `guest` ([redeploy gate](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4129-L4138)). So in a default workspace any writer can let anyone who reaches the instance run an app's scripts and flows with the publisher's rights (this guide's reading). An app's public link is the app's id encrypted under the workspace cipher, and it opens the app only for callers the app's mode admits ([public link](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2200-L2216), [link check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L1444-L1487)). The code read adds no random part and no expiry, so the link stays the same while the app and the workspace key do (this guide's reading). Enable `RestrictAnonymousAppDeployment`, and `RestrictGuestAppDeployment` for guest apps, in a workspace ruleset, and review the apps already set to `anonymous` or `guest`, which those rules leave as they are (this guide's advice). Publish an app as `anonymous` only when everything it runs is safe for anyone to run, from an account limited to what the app needs; and withdraw a public app by changing its mode, because its link does not change (this guide's advice).

An HTTP route serves a script or flow at `/api/r/<route path>` ([API prefix](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L675-L676), [route mount](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L1110-L1115)) with one of six authentication methods: `none`, `windmill`, `api_key`, `basic_http`, `custom_script` or `signature` ([authentication methods](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger-http/src/lib.rs#L104-L114)). The route handler checks a secret itself only for `api_key`, `basic_http` and `signature`, against a resource the route names ([method check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L541-L601)). With `windmill` it asks for a Windmill token that can read the route ([token check](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L408-L470)); with `custom_script` the handler checks nothing and the route's own script must do it, and with `none` nothing checks the caller (this guide's reading). Whatever the method, the job runs as the route's `permissioned_as` identity, not as the caller: that is the user who saved the route, unless a deployer allowed to do so kept an earlier identity ([run identity](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L475-L488), [identity rule](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger/src/types.rs#L214-L223)). So anyone who can reach a `none` route can run its script with that user's rights, and with `windmill` so can every caller who can read the route (this guide's reading). Never put a script that holds credentials, writes data or needs privileged rights behind a `none` route; use `api_key`, `basic_http` or `signature` for callers outside Windmill, save routes from an account limited to what the script needs, and block `/api/r/` at the proxy when no route has to be public (this guide's advice).

Windmill takes an API token from an `Authorization: Bearer` header, else from the session cookie, else from a `?token=` query parameter ([token sources](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L941-L971)), so a token can sit in a URL, where proxy logs, access logs and shared links keep it (this guide's reading). A token with no scopes has its user's full rights ([scope rule](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/lib.rs#L453-L457)). A token created through `POST /users/tokens/create` or `POST /users/tokens/impersonate` has no expiry unless its creator sets one or the instance sets `max_token_expiration_days`, which caps tokens those routes create afterwards but not tokens that service accounts own, so any workspace admin can still hold an uncapped token through one ([expiry ceiling](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L3218-L3273), [ceiling setting](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/global_settings.rs#L119-L157)). Tokens the server mints itself, such as webhook, app embed and session tokens, are outside that ceiling, because their lifetime is not one a caller picks ([ceiling setting](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/global_settings.rs#L119-L157)). When the server's `SUPERADMIN_SECRET` is set, which it is not by default, a request that presents its value as a token acts as an admin with no scopes and no expiry, which the server's help text calls a virtual superadmin token ([static admin token](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L788-L812), [server default](https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/src/main.rs#L469)). A token request does not pass the login route, so MFA at a fronting proxy covers it only if the proxy also requires its login on the API paths (this guide's reading). Give every token the narrowest scopes and an expiry, set `max_token_expiration_days`, review service-account tokens, send tokens in the header rather than in `?token=`, and leave `SUPERADMIN_SECRET` unset, or keep it in a secret store and rotate it like a root password (this guide's advice).

## Verify

REASONED: Historical run summary, not a demonstration. All six shell blocks passed bash -n, and ShellCheck 0.11.0 reported no findings. Local stubs exercised inventory, key-presence, login-request, TCP control and per-port paths; sample and replaced file fixtures printed a line beginning "FOUND vendor sample tokens:" and "no vendor sample tokens found". The inventory block had no guard refusal until its check for a missing `ss` was added, and the runs recorded here covered it in an earlier form, two top-level commands without a status of their own; for the five other blocks, the bash -n, ShellCheck, stub and fixture runs recorded here covered an earlier form, whose guard refusals ended with status 0. The current forms each end with one status for the whole fence: 2 for a guard refusal, 1 for a finding, 3 for a failed or inconclusive check and otherwise 0. The current forms passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0, except that the bash -n and local stub runs recorded here for the inventory block covered a form without its check for a missing `ss`; its current form is covered by the gate suite's bash -n and ShellCheck 0.11.0 passes and by local stub runs with `ss` passing, failing and missing. No deployment was available for this review; the authoring host forbids opening listeners without an isolated network namespace, and none was available. Exposed/fixed expectations below that no recorded run observed remain source reasoning, including the guide's cited Docker packet filtering (`DOCKER-USER`). The following host and run statements describe the earlier authoring environment, except the later current-form sample-token run they mention. Two checks here were run only on earlier forms of their blocks: the Windmill default-login pair and the TCP reachability probe's outcomes on loopback; the NocoDB key check's logic was exercised with a stand-in for `docker exec`. Those recorded runs and the stand-in run used earlier forms of their
blocks, whose guard refusals ended with status 0; those current forms, whose guard refusals exit with
status 2, have had no demonstration or stand-in run. The sample-token check was also run in an earlier form, and a later run ran its current form on the pinned vendor sample files and on copies with their sample tokens replaced, as recorded at that block. NocoDB 2026.09.0, Baserow,
Appsmith and Budibase ship for production as container images and the authoring host has no container
runtime. NocoDB also cannot run here outside a container: its server calls `listen` with no host, so it
can only bind every interface, which the host forbids; the same applies to Windmill's default bind.
The sample-token check is DEMONSTRATED at its block. The other checks in this section, including those named above, are REASONED from the cited vendor documentation and pinned source readings, with the recorded runs above as history. The Windmill loopback-bind and sandbox observations before this section are REASONED as well: they record a past run of the v1.817.0 release binary on loopback (the basis is v1.864.1) that observed only the configured state and was not re-run on v1.864.1.

REASONED: The inventory block passed bash -n; sudo and docker stubs printed wildcard and loopback publications. Those runs covered an earlier form of the block, two top-level commands without a status of their own; the current form is covered by the gate suite's bash -n and ShellCheck 0.11.0 passes and by local stub runs with `ss` passing, failing and missing. No deployment was available for inventory; the authoring host has no container runtime and forbids opening listeners without an isolated network namespace, and none was available. Expect wildcard addresses when exposed and loopback or private addresses when fixed, per the guide's cited Docker packet filtering (`DOCKER-USER`) and Docker CLI port display (`[::]:` from v27.2.0, `:::` through v27.1.2). On the host, list the listeners, then read Docker's own publications, because a port published through
Docker's NAT may have no host socket at all, so absence from `ss` is not proof of isolation:

REASONED: following block; pinned Compose and Docker sources support listener/publication inventory, and the `sudo` caveat below rests on the guide's cited sudo sudoers manual, secure_path entry. The recorded host has no container runtime and forbids wildcard binds; exposed/fixed expectations follow. After the runs above, bash -n and local stub runs covered a form of the block without its check for a missing `ss`; the current form is covered by the gate suite's bash -n and ShellCheck 0.11.0 passes and by local stub runs with `ss` passing, failing and missing, which exited 0, 3 and 2 while `docker ps` succeeded. Exposed, the reasoned expectation is a wildcard address, on the host or in a Docker publication, for any of the ports the block's comments list; fixed means a loopback or private address only. The block leaves both lists for you to judge, because a firewall rule can filter a wildcard publication, and it exits 3 if `ss` or `docker ps` fails, otherwise 2 if `ss` is not installed, and otherwise 0. Where sudoers sets `secure_path`, sudo looks `ss` up in that path instead of your PATH, so the `command -v ss` check can refuse although sudo would find `ss`, or pass and then end with status 3 when sudo cannot run it.

```bash
(                                       # one subshell, so one exit status covers both lists: 3 if either command fails, otherwise 2 if ss is not installed, otherwise 0
  set +e                                # errexit off here, so a failed command is recorded below instead of ending the block
  set -- 0                              # the block's status so far: 3 (inconclusive) outranks 2 (ss is not installed), which outranks 0
  if ! command -v ss >/dev/null; then
    echo "ss is not installed here; not listing sockets"; set -- 2
  elif sudo ss -tlnp; then :; else      # 8080 (NocoDB; Appsmith dev Compose), 80/443 (Baserow, Windmill Caddy), 10000 and 4000 (Budibase), 8000 and 25 (Windmill): loopback or private only
    echo "sudo ss -tlnp exit $?: the listener list did not print; inconclusive"; set -- 3
  fi
  if docker ps --format '{{.Names}}\t{{.Ports}}'; then :; else   # every "0.0.0.0:" or "[::]:" (":::" before Docker CLI 27.2) publication accepts connections on every host address: reachable from outside unless a firewall rule (for example in DOCKER-USER) filters it
    echo "docker ps exit $?: the publication list did not print; inconclusive"; set -- 3
  fi
  echo "block exit $1; the listeners and publications above are not classified, so judge them yourself"
  exit "$1"
)
```

DEMONSTRATED: following block; this block reads only a local file and needs no service. The current form, with only its file path substituted on the `set --` line, was run on the four pinned vendor files that Sources lists as the Budibase v3.46.0 sample environment, Appsmith v2.4.1 development Compose file, Windmill v1.864.1 Compose file and NocoDB 2026.09.0 README (Docker example JWT secret, Docker image, Auto-upstall and binaries note; checked October 2026), and exited 1 on each (exposed); on copies with the sample tokens replaced it printed "no vendor sample tokens found" and exited 0 (fixed). The sample hits and their absence after replacement were observed in that current-form run on all four pinned files, including the NocoDB 2026.09.0 README; they are not source reasoning. The vendor-file run did not reach the guard-refusal arms (status 2), the failed-read arms (status 3) or the unclassified-observation branch, in which a sample token found only outside a value position ends with status 0 and the unclassified-observation line. The current form's guard-refusal and failed-read arms were run locally under GNU bash 5.3.9 and GNU grep 3.12, changing only its `set --` line: a placeholder, an empty path, a missing file, two values and a removed marker each printed its refusal and exited 2, while `/proc/self/mem`, which grep failed to read in the whole-token search, and a sample hit whose value-position search failed under a stub grep each printed "grep could not read", the path, then "; not checked" and exited 3. The unclassified-observation branch rests on the local stub runs of the current form recorded after the block, in which such hits were printed but ended with status 0 and the unclassified-observation line. Before that vendor-file run, the file-check block passed bash -n; local sample and replaced fixtures printed a line beginning "FOUND vendor sample tokens:" and "no vendor sample tokens found"; a missing path printed "cannot read", the path, then "as a regular file; not checked". Placeholder, missing-marker, short-assignment and empty inputs stopped locally. The bash -n and fixture runs recorded here covered the file-check block in an earlier form, whose guard refusals and result arms ended with status 0, and were not repeated on the current form, which exits 2 for a guard refusal, 1 for a sample token in value position and 3 for a failed read. That earlier form found vendor values and syntax variants, found none in replaced copies and refused an unreadable path; its record does not give the vendor versions. The current form passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0. External environment values are outside this file check. Check each environment and Compose file the deployment uses for the vendor sample values: run the block
once per file, including every file an `env_file:` line names and the `.env` Compose reads for
variable substitution. Substitute the file path inside the
single quotes (a path containing an apostrophe needs other quoting), and paste the whole block. The
block prints every whole-token hit but exits 1 only when one sits in value position, after `=`, `:`,
`:-` or a quote and ending the value (followed by the line's end, whitespace, including a CRLF line's
carriage return, a quote or one of
`,;&@})`); hits only elsewhere, such as `image: budibase/apps`, end with status 0 and an
unclassified-observation line.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENV_OR_COMPOSE_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit 2 ;; esac
  { [ -f "$1" ] && [ -r "$1" ]; } || { echo "cannot read $1 as a regular file; not checked"; exit 2; }
  if grep -n -E '(^|[^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_])(testsecret|budibase|abcd|changeme|569a1821-0a93-45e8-87ab-eb857f20a010)([^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_]|$)' -- "$1"; then   # every whole-token hit
    if grep -q -E '(=|:-?|"|'"'"')[[:blank:]]*(testsecret|budibase|abcd|changeme|569a1821-0a93-45e8-87ab-eb857f20a010)($|[[:space:]]|"|'"'"'|,|;|&|@|\}|\))' -- "$1"; then   # a hit in value position: after =, :, :- or a quote, and ending the value
      echo "FOUND vendor sample tokens: inspect each line above; replace every secret still set to one"; exit 1
    else
      case "$?" in
        1) echo "no hit above is in a value position this search classifies; unclassified observation: inspect each line above"; exit 0 ;;
        *) echo "grep could not read $1; not checked"; exit 3 ;;
      esac
    fi
  else
    case "$?" in
      1) echo "no vendor sample tokens found" ;;
      *) echo "grep could not read $1; not checked"; exit 3 ;;
    esac
  fi
)
```

DEMONSTRATED: preceding block; this file check reads only a local file and needs no service. The current form, with only its file path substituted, printed a line beginning "FOUND vendor sample tokens:" and exited 1 on each of the pinned Budibase v3.46.0 sample environment, Appsmith v2.4.1 development Compose file, Windmill v1.864.1 Compose file and NocoDB 2026.09.0 README (Docker example JWT secret, Docker image, Auto-upstall and binaries note; checked October 2026), and printed "no vendor sample tokens found" and exited 0 on copies with their sample tokens replaced. The lines it printed before that finding were all eleven Budibase sample lines, Appsmith's two `abcd` lines, Windmill's `changeme` Postgres password and the README's `NC_AUTH_JWT_SECRET` sample secret line. The sample-token runs recorded below used an earlier form of the block, whose result arms ended with status 0, on vendor files whose versions that record does not give. The search matches each sample value as a whole token wherever it appears, so it cannot report a file
clean while one of them is still in it; the cost is that it also reports harmless lines such as `image:
budibase/apps`, so inspect each hit. Such a line alone ends with status 0 and an unclassified-observation
line, not with the finding's status 1. Values supplied from outside the files, such as the shell
environment Compose runs in, are beyond its reach. The runs recorded here used that earlier form. On Budibase's sample `hosting/.env` it
reported all eleven sample lines, on Appsmith's development Compose file the two `abcd` lines, and on
Windmill's Compose file its `changeme` Postgres password. It also reported Compose defaults
(`${JWT_SECRET:-testsecret}`), flow mappings and lists (`{COUCH_DB_PASSWORD: budibase, X: 1}`),
URL parameters (`&password=changeme&`) and trailing punctuation. On copies with the values replaced it printed "no
vendor sample tokens found", and on an unreadable path it reported that it did not check. In local stub runs of the current form, a flow mapping, a `:-` default and a URL parameter ended with status 1, while a list item such as `command: [redis-server, --requirepass, budibase]`, a Compose default without a colon such as `${JWT_SECRET-testsecret}` and a value followed by other punctuation, such as `changeme.`, were printed but ended with status 0 and the unclassified-observation line.

REASONED: The key-presence block passed bash -n; a docker stub executing the inner shell test printed "non-empty" for a set key, "EMPTY or unset" for empty and absent keys, and "not checked" for a missing container. Placeholder, missing-marker, short-assignment, empty and option-like inputs stopped locally. Later Bash stub runs also stopped tab, LF, CR and DEL inputs with "substitute the container name on the set -- line above; not checking", without calling docker. The bash -n and stub runs recorded here covered the key-presence block in an earlier form, whose guard refusals and result arms ended with status 0, and were not repeated on the current form, which exits 2 for a guard refusal, 1 for an empty or unset key and 3 for a failed check. The current form passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0. No deployed NocoDB container was available; the authoring host has no container runtime and forbids opening listeners without an isolated network namespace, and none was available. Expect "EMPTY or unset" when exposed and "non-empty" when fixed; this tests presence only, per the guide's cited Docker `docker exec` environment and NocoDB 2026.09.0 container start scripts. For NocoDB, check the encryption key in the container rather than in a file: Compose variable
substitution, `env_file:` precedence and YAML values all decide the value, and the container's
configured environment is their result. `docker exec` runs with that configured environment, not with
the server process's own, so the two differ if the image's startup changes the variable. NocoDB's
pinned start scripts, `docker/start.sh` and `docker/start-litestream.sh`, run `node docker/main.js`
without touching it, but the pinned tree has no Dockerfile, so which script the image runs was not
verified. The block reports only whether the key is non-empty and never prints it. Substitute the
container name inside the single quotes.

REASONED: Presence-check assumptions and limits, per the guide's cited Docker `docker exec` environment, NocoDB 2026.09.0 container start scripts and NocoDB 2026.09.0 credential encryption. The run history is recorded in the paragraph before this one. Process-environment visibility, image startup selection and encryption were not tested against a deployed container. This check assumes a clean host Bash shell, trusted container image and startup files, and a
container shell whose `[` is a builtin. It intentionally tests an existing container environment
value: prompting for a key or supplying a file would test that replacement, not the deployed
configuration. Docker's documented `exec`
environment inheritance and the pinned NocoDB startup scripts cited below are the trace for this
assumption. The host sends only the literal variable name and test program, never the key, in argv.
The container shell's builtin `[` tests the value without starting a child process with it in argv.
The key remains in the container's configured environment and is inherited by this extra shell;
the same account and root may read it through `/proc/<pid>/environ` for those processes' lifetimes,
and Docker-socket holders can read the configured value with `docker inspect`. This presence check
does not remove that exposure, prove encryption is working, or establish what the server process
actually received. Do not use `docker exec -e` to inject a key for this check.

REASONED: following block; Docker exec inheritance and pinned NocoDB start scripts support key-presence checking. No real container ran because the recorded host has no container runtime; only stand-in logic outcomes below were observed. Those stand-in runs covered an earlier form of the block, whose result arms ended with status 0; the current form, which reads docker's status through an if condition, passed bash -n and local stub runs, and the stand-in runs were not repeated on it.

```bash
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOCODB_CONTAINER_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit 2; }
  case "$1" in *REPLACE_WITH_*|""|-*|*[[:cntrl:]]*) echo "substitute the container name on the set -- line above; not checking"; exit 2 ;; esac
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand inside the container
  if docker exec "$1" sh -c 'set +x; if [ -n "${NC_CONNECTION_ENCRYPT_KEY-}" ]; then exit 0; else exit 3; fi'; then
    echo "NC_CONNECTION_ENCRYPT_KEY is non-empty in the container's configured environment"
  else
    case "$?" in
      3) echo "NC_CONNECTION_ENCRYPT_KEY is EMPTY or unset in the container's configured environment"; exit 1 ;;
      *) echo "could not run the check in container $1; not checked"; exit 3 ;;
    esac
  fi
)
```

REASONED: preceding block; Docker exec inheritance and pinned NocoDB start scripts support key-presence checking, and the block's run history is recorded in the paragraphs above it. The following stand-in account is the guide's earlier record. Exposed: "EMPTY or unset". Fixed: "non-empty". Anything else means the check did not run. With a
stand-in for `docker exec`, the block printed "non-empty" for a set key, "EMPTY or unset" for an empty
and an unset one, and "not checked" when the container was missing; it was not run against a real
NocoDB container (no container runtime on the authoring host).

REASONED: The login block passed bash -n, its JSON parsed, and a curl stub received the default credentials on stdin and the substituted /api/auth/login URL. Placeholder, missing-marker, short-assignment and empty inputs stopped locally. Later Bash stub runs also stopped tab, LF, CR and DEL inputs with "substitute the base URL on the set -- line above; not probing", without calling curl. The bash -n and stub runs recorded here covered the login block in an earlier form, whose guard refusals ended with status 0, and were not repeated on the current form, which exits 2 for a guard refusal, 1 for a `200`, 0 for a `400` and 3 otherwise. The current form passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0. No live Windmill deployment was available for credential rotation in this review; the authoring host forbids opening listeners without an isolated network namespace, and none was available. The guide's cited Windmill v1.864.1 README gives the default credentials, so a deployment that still has them accepts them (exposed) until they are rotated (fixed); precise HTTP observations below belong to the earlier recorded run. For Windmill, check whether the default login still works. The password below is the vendor's
published default, not a secret, so it is fine in the request body. Substitute the base URL (for
example the Caddy address on port 80) inside the single quotes.

REASONED: following block; no live Windmill deployment was available and the authoring host forbids opening a listener without an isolated network namespace, so the current form was not run against a service. Post the vendor's published default credentials (admin@windmill.dev with password changeme) to `/api/auth/login`. The guide's cited Windmill v1.864.1 README gives these default credentials, so a deployment that still has them accepts them (exposed) until they are rotated (fixed). The codes `200` with a token (exposed) and `400` (fixed) were observed only in the v1.817.0 loopback run of an earlier block form, recorded later in this paragraph; they are neither source reasoning nor a v1.864.1 fact, and no cited source gives the v1.864.1 fixed-state code. The current form exits 1 on a `200`, 0 on a `400` and 3 otherwise, so if v1.864.1 rejects a rotated default login with a code other than `400`, the block reports inconclusive (status 3, its `*)` arm) rather than a pass. An earlier form of the block, run against Windmill v1.817.0 on loopback rather than the cited v1.864.1, returned 200 for changeme before rotation, 400 afterwards and 200 for the replacement password; its result was curl's own exit status, it was not re-run on the current form, and it does not demonstrate external isolation. The current form passed bash -n, local stub runs and the gate suite's ShellCheck 0.11.0.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_WINDMILL_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the base URL on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$(if printf '%s' '{"email":"admin@windmill.dev","password":"changeme"}' | \
       curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
         -H 'Content-Type: application/json' --data-binary @- \
         -w 'default login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n%{http_code}' "$1/api/auth/login"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%$'\n'*}"        # the URL, curl's exit status, then its result line and HTTP code
  set -- "$1" "$2" "${3%$'\n'*}" "${3##*$'\n'}"   # the URL, curl's exit status, its result line, then the HTTP code
  printf '%s\n' "$3"
  case "$2:$4" in
    0:200) echo "FINDING: the default login was accepted with 200"; exit 1 ;;
    0:400) echo "the default login was refused with 400; log in once with your real credentials before trusting it, so that a dead service is not read as fixed"; exit 0 ;;
    *) echo "neither the 200 finding nor the 400 pass; inconclusive"; exit 3 ;;
  esac
)
```

REASONED: preceding block; no live Windmill deployment was available and the authoring host forbids opening a listener without an isolated network namespace, so the current form was not run against a service. The guide's cited Windmill v1.864.1 README gives the default credentials, so a deployment that still has them accepts them (exposed) until they are rotated (fixed). The HTTP codes below are not source reasoning and not a v1.864.1 fact: an earlier form of the block, run against Windmill v1.817.0 on loopback rather than the cited v1.864.1, observed them with its result being curl's own exit status; it was not re-run on the current form, and no cited source gives the v1.864.1 fixed-state code. Exposed, the default login gets `200` with a token; fixed, it gets `400` (both observed only with that earlier form of this block
on the v1.817.0 loopback run). Before trusting a `400`, log in once with your real credentials, so that a dead
service is not read as fixed. The block exits 1 on a `200`, 0 on a `400` and 3 on anything else, so a v1.864.1 rejection with a code other than `400` reports inconclusive rather than a pass.

REASONED: The two sample-value requests use Budibase v3.46.0 sample environment for the sample values and Budibase v3.50.0 proxy configuration (`/db/`) for the path. The Apache CouchDB 3.5.2 `/_session` reference supports the CouchDB 401 for a wrong password; the LiteLLM 401 for a non-`sk-` key when a database is connected and the 400 without one are supported by LiteLLM authentication source: non-`sk-` keys rejected with 401 when a database is connected; 400 without one (checked October 2026). These LiteLLM outcomes remain comparison expectations: this guide has not established that litellm.md's source pin `6ef7b86748118ceecd95271727c2fa167ce55fec` corresponds to Compose image `docker.io/litellm/litellm:main-v1.83.10-stable.patch.3` (LiteLLM image and environment source below); no source for that image was fetched. Exposed: either line 200; fixed: CouchDB 401, and LiteLLM returns a 401 (or a 400 if the proxy has no database), with real credentials still accepted. These are expectations, not live observations. The recorded host has no container runtime. A live Budibase or LiteLLM stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. For Budibase, two reasoned requests use the published sample values, which are not secrets. Substitute
the proxy URL (`http://HOST:10000` in the sample setup) and the LiteLLM URL inside the single quotes.

REASONED: following block; Budibase v3.46.0 sample environment supplies the sample values, and Budibase v3.50.0 proxy configuration (`/db/`) supplies the path. Apache CouchDB 3.5.2 `/_session` reference supports the CouchDB 401 for a wrong password. For the LiteLLM 401 with a database connected or 400 without one, see LiteLLM authentication source: non-`sk-` keys rejected with 401 when a database is connected; 400 without one (checked October 2026). These LiteLLM outcomes remain comparison expectations: this guide has not established that litellm.md's source pin `6ef7b86748118ceecd95271727c2fa167ce55fec` corresponds to Compose image `docker.io/litellm/litellm:main-v1.83.10-stable.patch.3` (LiteLLM image and environment source below); no source for that image was fetched. Exposed: either line 200; fixed: CouchDB 401, and LiteLLM returns a 401 (or a 400 if the proxy has no database), with real credentials still accepted. The exposed 200 outcomes still require live comparison. No Budibase/LiteLLM containers ran; the recorded host has no container runtime. A live Budibase or LiteLLM stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Local marking review (October 2026, Bash 5.3.9 and ShellCheck 0.11.0) checked syntax and guard fixtures with a curl stub; no service response was observed. Bash -n and ShellCheck 0.11.0 each exited 0 with no output. That local marking review covered an earlier form of the block, whose guard refusals ended with status 0; that review's bash -n, ShellCheck and guard fixtures were not repeated on the current form, whose guard refusals exit with status 2. The current form, which exits 2 for a guard refusal, 1 if either sample credential gets a `200`, 0 if CouchDB answers `401` and LiteLLM `401` or `400`, and 3 otherwise, passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0. In that local marking review, missing marker printed "paste the whole block, including its set -- line; not probing" (exit 0, 0 stub calls); missing set -- line printed "paste the whole block, including its set -- line; not probing" (exit 0, 0 stub calls). That local marking review's short assignment printed "the set -- line needs exactly 2 values; not probing" (exit 0, 0 stub calls); that review's long assignment printed "the set -- line needs exactly 2 values; not probing" (exit 0, 0 stub calls). Placeholder, first empty, second empty, first option-like, second option-like, first spaced, second spaced, embedded placeholder, tab, LF, CR and DEL each printed "substitute both URLs on the set -- line above; not probing" (each exit 0, 0 stub calls). The valid fixture exited 0 with 2 stub calls and printed, in order, `stub couchdb url=http://203.0.113.10:10000/db/_session?basic=true`, `couchdb sample login: http=200 exit=0 err=fixture ok`, `stub litellm url=http://203.0.113.11:4000/v1/models` and `litellm sample key: http=200 exit=0 err=fixture ok`.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BUDIBASE_PROXY_URL' 'REPLACE_WITH_LITELLM_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1|$2" in
    *REPLACE_WITH_*|"|"*|*"|"|-*|*'|-'*|*" "*|*[[:cntrl:]]*) echo "substitute both URLs on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$2" "$(if printf 'user = "budibase:budibase"\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
       --max-time 15 --config - -w 'couchdb sample login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n%{http_code}' \
       "$1/db/_session?basic=true"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3##*$'\n'}" "${3%$'\n'*}"        # the two URLs, curl's exit status, then its result line and HTTP code
  set -- "$1" "$2" "$3" "${4%$'\n'*}" "${4##*$'\n'}"   # the two URLs, curl's exit status, its result line, then the HTTP code
  printf '%s\n' "$4"
  case "$3:$5" in
    0:200) echo "FINDING: the CouchDB sample login was accepted with 200"; set -- "$1" "$2" 1 ;;
    0:401) set -- "$1" "$2" 0 ;;
    *) echo "the CouchDB sample login got neither the 200 finding nor the 401 pass; inconclusive"; set -- "$1" "$2" 3 ;;
  esac                                                  # the 3rd value is now the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  set -- "$1" "$2" "$3" "$(if printf 'Authorization: Bearer budibase\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
       --max-time 15 -H @- -w 'litellm sample key: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n%{http_code}' \
       "$2/v1/models"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "${4##*$'\n'}" "${4%$'\n'*}"        # the URLs, the status so far, curl's exit status, then its result line and HTTP code
  set -- "$1" "$2" "$3" "$4" "${5%$'\n'*}" "${5##*$'\n'}"   # the URLs, the status so far, curl's exit status, its result line, then the HTTP code
  printf '%s\n' "$5"
  case "$4:$6" in
    0:200) echo "FINDING: the LiteLLM sample key was accepted with 200"; set -- "$1" "$2" 1 ;;
    0:401|0:400) ;;
    *) echo "the LiteLLM sample key got neither the 200 finding nor a 401 or 400 pass; inconclusive"; [ "$3" = 1 ] || set -- "$1" "$2" 3 ;;
  esac
  echo "block exit $3; confirm that each service accepts your real credentials, the positive control this block does not run"
  exit "$3"
)
```

REASONED: Exposed and fixed outcomes below are expectations, not live observations. Budibase v3.46.0 sample environment supplies the sample values, and Budibase v3.50.0 proxy configuration (`/db/`) supplies the path. Apache CouchDB 3.5.2 `/_session` reference supports the CouchDB 401 for a wrong password. For the LiteLLM 401 with a database connected or 400 without one, see LiteLLM authentication source: non-`sk-` keys rejected with 401 when a database is connected; 400 without one (checked October 2026). These LiteLLM outcomes remain comparison expectations: this guide has not established that litellm.md's source pin `6ef7b86748118ceecd95271727c2fa167ce55fec` corresponds to Compose image `docker.io/litellm/litellm:main-v1.83.10-stable.patch.3` (LiteLLM image and environment source below); no source for that image was fetched. No Budibase/LiteLLM containers ran; the recorded host has no container runtime. A live Budibase or LiteLLM stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Exposed: either line 200; fixed: CouchDB 401, and LiteLLM returns a 401 (or a 400 if the proxy has no database), with real credentials still accepted. Exposed, either line gets `200`, which means the sample secret is live. Fixed, the CouchDB sample login
gets `401` ("Username or password wasn't recognized", per CouchDB's `/_session` reference) and the
LiteLLM sample key gets a 401 (or a 400 if the proxy has no database), per the LiteLLM authentication source; compare the `/v1/models` check in [litellm.md](litellm.md). Confirm each
service answers your real credentials as the positive control. This guide assesses Budibase's first-run
POST as unsafe for read-only claimed-state probing: the body validator precedes the controller's
tenant-context `checkAnyUserExists()` call (admin-init body validator, middleware order and controller
sources below); invalid bodies can fail validation in both states, while accepted initialization creates an admin.
The helper definition was not fetched, so which users count and any multi-tenancy exception remain unestablished.
Claim the admin yourself before the proxy is reachable (this guide's advice).

REASONED: Manual signup procedure, per the guide's cited NocoDB 2026.09.0 first user, signup and its refusal message, NocoDB 2026.09.0 app settings (`invite_only_signup`), Baserow 2.3.4 first user, signup and its refusal message, Baserow 2.3.4 settings model (`allow_new_signups`), Appsmith v2.4.1 server properties (bind address, signup) and Appsmith v2.4.1 `SIGNUP_DISABLED` error. No browser-accessible NocoDB, Baserow or Appsmith deployment was available for the account lifecycle checks; the authoring host has no container runtime and forbids opening listeners without an isolated network namespace, and none was available. This paragraph contains no shell or configuration fragment to execute locally. Expect account creation when exposed and backend refusal when fixed, with administrator login still working. For NocoDB, Baserow and Appsmith, check signup by hand, reasoned from source. In a private browser
window, open the instance's sign-up page and try to create an account with an address you control.
Exposed: the account is created, or, on a fresh instance, you become its administrator. Fixed: the
signup is refused. The backends' refusal messages are NocoDB's "Not allowed to signup, contact super
admin.", Baserow's "Sign up is disabled." and Appsmith's `SIGNUP_DISABLED` error ("Signup is restricted
on this instance of Appsmith"); the web UIs may word them differently. A hidden sign-up link is
inconclusive, because the frontend does not enforce the setting: check the backend setting itself
(NocoDB's `invite_only_signup` app setting, Baserow's `allow_new_signups` admin setting, Appsmith's
`APPSMITH_SIGNUP_DISABLED`). Delete any test account the exposed state let you create, then sign in as your
admin as the positive control.

REASONED: The TCP block passed bash -n; timeout stubs printed "connected" for the control and every tested port, while refusal, timeout and fixture error at the control stopped further probes. Later timeout stubs connected the control and exercised all seven tested ports in each branch: printed outcomes were "connected: reachable from this host", "timed out from this host", "refused from this host" and "inconclusive (not a connection, refusal or timeout): fixture error", each prefixed by the fixture IP address and tested port. Placeholder, missing-marker, short-assignment, empty, malformed-address and invalid-port inputs stopped locally. The bash -n and stub runs recorded here covered the TCP block in an earlier form, whose guard refusals, failed control and result arms ended with status 0, and were not repeated on the current form, which exits 2 for a guard refusal, 3 for a failed control, and after its probes 1 if any port connected, otherwise 3 if any port was inconclusive, otherwise 0. The current form passed bash -n and local stub runs and the gate suite's bash -n and ShellCheck 0.11.0. No public probing host or live deployment was available; the authoring host forbids opening listeners without an isolated network namespace, and none was available. Exposed means "connected"; refusal or timeout is only consistent with fixed, subject to the controls below, per the guide's cited Docker packet filtering (`DOCKER-USER`) and Baserow 2.3.4 install with Docker (ufw warning). Finally, from a host that should not have access, try a TCP connection to each published port. The
block uses bash's `/dev/tcp`, so it works for SMTP on 25 as well as the web ports. It takes one IP
address rather than a host name, so that a name with both IPv4 and IPv6 addresses cannot hide one
behind a timeout on the other: run it once for each public address of the host. It also takes a port you know
is open on that address from this host (for example SSH on 22) as the positive control, and stops if
the control does not connect. Substitute both inside the single quotes.

REASONED: following block; no public probing host and no live deployment were available in the authoring environment, so the current form was not run against a service, and public isolation remains source reasoning because the timeout fixture was not a firewall. From a host that should not have access, open a TCP connection to each published port: exposed means `connected`, while refusal or timeout is only consistent with fixed, per the guide's cited Docker packet filtering (`DOCKER-USER`) and Baserow 2.3.4 install with Docker (ufw warning). The current form exits 2 for a guard refusal, 3 for a failed control, then 1 if any port connected, otherwise 3 if any port was inconclusive, otherwise 0, and holds its values in positional parameters. An earlier form of the block, whose guard refusals, failed control and result arms ended with status 0, observed connected, refused, timeout on a full accept queue and failed-control stopping on loopback; it was not re-run on the current form. The current form passed bash -n, local stub runs and the gate suite's ShellCheck 0.11.0.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ONE_IP_ADDRESS' 'REPLACE_WITH_A_KNOWN_OPEN_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute one IP address on the set -- line above; not probing"; exit 2 ;; esac
  case "$1" in 0.0.0.0) echo "$1 reaches this host itself; give the public address of the service; not probing"; exit 2 ;; esac
  set -- "$1" "$2" '^((25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])[.]){3}(25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])$'   # the address, the control port, then the IPv4 pattern, held here rather than in a named variable
  case "$1" in
    *:*:*)
      case "$1" in *[!0123456789ABCDEFabcdef.:]*) echo "$1 is not an IPv6 address; not probing"; exit 2 ;; esac
      case "$1" in *.*) echo "give the IPv4 address itself rather than $1; not probing"; exit 2 ;; esac
      case "$1" in *[!0:]*) ;; *) echo "$1 is all zeros (this host itself, or not an address); give the public address of the service; not probing"; exit 2 ;; esac ;;
    *) [[ $1 =~ $3 ]] || { echo "give one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not probing"; exit 2; } ;;
  esac
  case "$2" in *[!0123456789]*|"") echo "substitute a known-open control port on the set -- line above; not probing"; exit 2 ;; esac
  { [ "$2" -ge 1 ] && [ "$2" -le 65535 ]; } 2>/dev/null || { echo "the control port must be 1 to 65535; not probing"; exit 2; }
  command -v timeout >/dev/null || { echo "timeout is not installed here; not probing"; exit 2; }
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
  set -- "$1" "$2" "$(if LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$2" 2>&1; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3%$'\n'*}" "${3##*$'\n'}"   # the address, the control port, the control's messages, then its exit status
  set -- "$1" "$2" "${3%$'\n'}" "$4"              # the messages without their final line break, as a plain capture prints them
  [ "$4" = 0 ] || { echo "control $1:$2 did not connect (${3:-timed out}); not probing"; exit 3; }
  echo "control $1:$2 connected"
  set -- "$1" 0 80 443 8080 10000 4000 8000 25   # the address, the block's status so far (1, a finding, outranks 3, inconclusive, which outranks 0), then the ports still to probe
  while [ "$#" -gt 2 ]; do
    # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
    set -- "$(if LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$3" 2>&1; then printf '\n0'; else printf '\n%s' "$?"; fi)" "$@"
    set -- "${1##*$'\n'}" "${1%$'\n'*}" "${@:2}"   # this port's exit status, its messages, the address, the status so far, this port, then the ports after it
    set -- "$1" "${2%$'\n'}" "${@:3}"             # the messages without their final line break
    case "$1:$2" in
      0:*) echo "$3:$5 connected: reachable from this host"; set -- "$1" "$2" "$3" 1 "${@:5}" ;;
      124:*) echo "$3:$5 timed out from this host" ;;
      *"Connection refused"*) echo "$3:$5 refused from this host" ;;
      *) echo "$3:$5 inconclusive (not a connection, refusal or timeout): ${2:-no message}"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 "${@:5}" ;;
    esac
    set -- "$3" "$4" "${@:6}"                     # the address, the status so far, then the ports still to probe
  done
  exit "$2"
)
```

REASONED: preceding block; no public probing host and no live deployment were available in the authoring environment, so the current form was not run against a service, and the public-isolation outcomes below are source reasoning because the timeout fixture was not a firewall, per the guide's cited Docker packet filtering (`DOCKER-USER`) and Baserow 2.3.4 install with Docker (ufw warning). The loopback runs and refusals recorded below used an earlier form of the block, whose guard refusals, failed control and result arms ended with status 0, and were not re-run on the current form. Exposed, a port reports "connected"; a transparent proxy on the probing host's network can also
complete the handshake, so confirm a surprising "connected" with `ss` on the host. "refused" and
"timed out" show only that this host could not reach the port: a firewall in front of the service
produces either, but so can filtering on the probing host's own network (many providers block outbound
SMTP on 25), and the control proves only its own port. Treat them as consistent with fixed, and take
the `ss` and `docker ps` check on the host as the authority. "inconclusive" is any other result and
says nothing about the port. The block runs the probe in the C locale so that bash's refusal message
is matched in English. On loopback it printed "connected" for the control and an open port, "timed
out" for a port whose accept queue was full (standing in for a filtered one) and "refused" for a
closed port, and it stopped when the control was closed. It refused to run for the host names
`localhost`, `cafe.be`, `fe01`, `db1` and `face`, for `1.2.3.4.5`, `999.1.1.1`, `01.2.3.4` and
`1.2.3`, for `1.2.3.4:22`, `[::1]` and `[::1]:22`, for a leading space, for control ports `0` and
`65536`, and on a machine without `timeout`. It refuses `0.0.0.0` and any IPv6 value made only of
zeros and colons (measured: `::`, `::0`, `0::`, `0000::`, `0:0:0:0:0:0:0:0`), because those reach
the probing host itself or are not addresses, and any IPv6 value containing a dot (measured:
`::ffff:0.0.0.0`, `::ffff:127.0.0.1`, `::0.0.0.0`), asking for the IPv4 address instead. It does not
refuse every value that reaches the probing host: loopback addresses pass, and hex spellings such as
`::ffff:0:0` and `::ffff:7f00:1` passed and connected to a listener bound to 127.0.0.1, so give the
service's public address. Any other value with two or
more colons, made only of hex digits and colons, is passed on as IPv6, so a port appended without brackets changes the address: `2001:db8::1:22` is still a valid
address and was probed as that different address, while `2001:db8::1:10000` and `dead::beef::` are
not, and each failed the name lookup at the control and stopped. A "connected" on a port you did not
mean to publish is the finding.

REASONED: following block; the login paths, request bodies and outcomes follow the guide's cited NocoDB 2026.09.0 sign-in routes, sign-in route guards, public API limiter guard and local sign-in strategy, Baserow 2.3.4 login route, login view, login serializer and invalid-credentials error, Appsmith v2.4.1 login URL, form-login matcher and CSRF wiring, CSRF exemptions, login field names, login rate limit filter, login failure redirect and login success redirect, Budibase v3.46.0 login body validator and middleware order, login controller, email lockout and address lockout, and Windmill v1.864.1 API route nesting, login route and login handler, login body, wrong-password answer and login-link check, and login limits' 429 and global minute, and the limit statuses that [nginx.md](nginx.md) and the guide's cited nginx limit_req module documentation record. It was not run against any deployment: no deployment of these tools or of a fronting proxy was available to this review. On 2026-11-12 the block passed bash -n in bash 5.3.9 and ShellCheck 0.11.0, and it ran locally with a curl stub that logged each request and replayed curl's status and exit fields. Each tool got the body and headers described below. Placeholders, a missing marker or `set --` line, wrong value counts, an unknown tool, placeholder, empty, option-like, spaced and tab-bearing URLs, malformed or out-of-range counts and statuses, each status the block refuses as the tool's own, and no curl on PATH were refused with status 2 and no curl call. Every attempt getting the tool's own answer (NocoDB 400, Baserow 401, Appsmith 302 to `/user/login?error=true`, Budibase 403 and then its own 429, Windmill 400 and then its own 429) exited 1; a limit status other than 502, 503 or 504 after an application answer exited 0, also after an earlier 504; and 503 as the limit status after an application answer, a 502 or 503 midway that was not the limit status, the limit status before any application answer, one attempt failing to connect or timing out, a 404 for NocoDB, a 301 to https for NocoDB, an Appsmith 302 to a target other than its login error page, and Baserow selected while the answers were 400 exited 3. For the proxy login limit in the introduction, run it from a host that reaches the instance through the proxy, the way a user does. It sends the given number of failed logins, one after another, to one login URL, for a test account that should not exist, `no-such-user@example.invalid` (under the reserved `.invalid` top-level domain), with the password `not-a-real-password`, and prints each answer. The request follows each tool's own login: NocoDB, Baserow and Windmill get JSON with `email` and `password`; Budibase gets JSON with only `username` and `password`, because its validator rejects any other field before either lockout runs; Appsmith gets a form-encoded `username` and `password`, because its form login and its per-username limit act only on a form-encoded POST, with `X-Requested-By: Appsmith`, which exempts the request from Appsmith's CSRF token check. Never put a real account in it: Appsmith's per-username limit would suspend that username's form login for up to a day, and Budibase would lock it for 15 minutes; with the test account, only the test username is suspended or locked. Substitute, inside the single quotes, the tool (`nocodb`, `baserow`, `appsmith`, `budibase` or `windmill`), the full login URL, an attempt count above the burst your limit allows (at most 99), and the 4xx or 5xx status your proxy rejects login requests with. The login paths are NocoDB's `/api/v2/auth/user/signin` (run it once for each of the four sign-in paths), Baserow's `/api/user/token-auth/`, Appsmith's `/api/v1/login`, Budibase's `/api/global/auth/TENANT_ID/login` with your tenant ID, and Windmill's `/api/auth/login`. The block refuses, with status 2, a limit status the selected tool answers itself: NocoDB 400; Baserow 401, and as a precaution 400 and 429 (its serializer's validation error, and its optional throttle, which raises a subclass of REST framework's `Throttled`; those statuses are REST framework's and are not traced here); Budibase 403 and 429; Windmill 400 and 429. The block counts as the application's answer only the selected tool's own failed-login answer: NocoDB 400 (its local strategy raises a bad-request error for invalid credentials; the code that maps it to a status is not pinned here, so 400 is this guide's reading); Baserow 401 (`ERROR_INVALID_CREDENTIALS`); Appsmith a 3xx whose redirect target, as curl reports it without following it, ends in `/user/login?error=true` or contains `/user/login?error=true&`, whatever origin precedes that path (the redirect's status code is not traced here; with no `Origin` header and no state parameter, as this block sends, the guide's cited Appsmith v2.4.1 login failure redirect keeps the origin `/` and redirects to `//user/login?error=true`, which curl 8.18.0 reported for an http login URL as `http://user/login?error=true`, with the host `user`, and that still matches); Budibase 403 and 429; and Windmill 400 and 429. Any other status, such as a 404 from a wrong path, a redirect elsewhere (for example from http to https) or a fronting login's 401, does not count as an application answer: the block prints that status after its attempt line, and with no limit status after an application answer it exits 3 and says that the login URL's path or the tool on the `set --` line may be wrong. NocoDB and Windmill get the same request and, in this guide's reading, answer a failed login with the same 400, so the block cannot tell them apart and the tool on the `set --` line must match the login URL. Selecting `nocodb` against a Windmill instance counts Windmill's 400 as NocoDB's answer, and if one of Windmill's own limits (its global cap, or its per-address or per-account limit when on) answers 429, a limit status of 429 then reads that 429 as the proxy's limit and the block exits 0; with `windmill` selected, the block refuses 429. The block does not refuse 429 for NocoDB, because 429 is a common `limit_req_status`. Exposed, every attempt gets the application's own answer and the block exits 1: NocoDB a bad-request error for the invalid credentials; Baserow 401; Appsmith a redirect to its login error page, and the same page with a message once its limit has refused the test username; Budibase 403, then 403 "Account temporarily locked. Try again later." from the fifth attempt with the default settings, and 429 once more than 10 requests have come from one address; and Windmill 400 ("Invalid login"), then 429 if one of its own limits is on and spent. Fixed, the proxy's limit status appears after the application has answered and before the attempts run out. The limit status before any application answer, a failed request, an answer without a status, and a 502, 503 or 504 that is not the limit status, which means an unavailable or overloaded upstream, are inconclusive; with no limit status after an application answer, any of them makes the block exit 3: wait for the limit window and run it again. A 503 is not conclusive on its own, as nginx.md says: `limit_conn` also returns 503, and an upstream under load returns it too. So when the limit status is 502, 503 or 504, the block exits 3 even when that status follows an application answer, and it exits 0 only for another status. For a conclusive pass, set the limit's rejection status with nginx's `limit_req_status` to a status that nothing else on that path returns and the tool does not answer itself, and give that status here. Run from one host, the block cannot tell a per-address limit from one shared by every client (a global key, or a per-address key that sees a CDN's or proxy's address because the client address was not recovered); it shows only that some limit answered this host. The attempts go one after another, not concurrently, so a limit that refills faster than they arrive, such as nginx.md's example at 10 requests a second, may never answer, and the block then reports a finding; a FINDING therefore says only that the limit did not answer at this arrival rate. A fail2ban jail already watching the login path can ban the testing address partway through, and the failed requests that follow make the run inconclusive. On Budibase, every attempt counts toward its address lockout, which answers 429 once one address has sent more than 10 login requests within what this guide reads as a 15-minute window (the lockout passes `LOGIN_LOCKOUT_SECONDS` with each count, and whether each request extends the window is not traced here); if Budibase sees the proxy's address for every client (not verified), that blocks every user's login for up to 15 minutes (this guide's inference, not tested), so keep the count at 10 or below with a burst below it, or run it when that outage is acceptable. Once the limit window has passed, sign in with a real account as the positive control.

```bash
(
  set +e                                # errexit off here, so every attempt is recorded instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_TOOL' 'REPLACE_WITH_LOGIN_URL' 'REPLACE_WITH_ATTEMPTS' 'REPLACE_WITH_LIMIT_STATUS'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo "the set -- line needs exactly 4 values; not probing"; exit 2; }
  case "$1" in nocodb|baserow|appsmith|budibase|windmill) ;; *) echo "the tool must be nocodb, baserow, appsmith, budibase or windmill; not probing"; exit 2 ;; esac
  case "$2" in *REPLACE_WITH_*|""|-*|*" "*|*[[:cntrl:]]*) echo "substitute the login URL on the set -- line above; not probing"; exit 2 ;; esac
  case "$3" in ""|0*|*[!0123456789]*|???*) echo "the attempt count must be a whole number from 1 to 99; not probing"; exit 2 ;; esac
  case "$4" in [45][0123456789][0123456789]) ;; *) echo "the limit status must be a three-digit 4xx or 5xx HTTP status such as 503; not probing"; exit 2 ;; esac
  case "$1:$4" in nocodb:400|baserow:400|baserow:401|baserow:429|budibase:403|budibase:429|windmill:400|windmill:429)
    echo "$1 answers $4 itself (nocodb 400; baserow 401, and 400 and 429 as a precaution; budibase 403 and 429; windmill 400 and 429), so $4 cannot show the proxy's limit; reject with another status at the proxy; not probing"; exit 2 ;; esac
  command -v curl >/dev/null || { echo "curl must be installed here; not probing"; exit 2; }
  case "$1" in                          # then: the URL, the attempts left, the limit status, the outcomes so far, the tool, the body, the headers
    appsmith) set -- "$2" "$3" "$4" '' "$1" 'username=no-such-user%40example.invalid&password=not-a-real-password' \
                -H 'Content-Type: application/x-www-form-urlencoded' -H 'X-Requested-By: Appsmith' ;;
    budibase) set -- "$2" "$3" "$4" '' "$1" '{"username":"no-such-user@example.invalid","password":"not-a-real-password"}' -H 'Content-Type: application/json' ;;
    nocodb|baserow|windmill) set -- "$2" "$3" "$4" '' "$1" '{"email":"no-such-user@example.invalid","password":"not-a-real-password"}' -H 'Content-Type: application/json' ;;
  esac
  while [ "$2" -gt 0 ]; do
    set -- "$(printf '%s' "$6" | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 "${@:7}" --data-binary @- \
             -w 'attempt: http=%{http_code} exit=%{exitcode} redirect=%{redirect_url} err=%{errormsg}\n%{http_code} %{exitcode} %{redirect_url}' "$1")" "$@"
    printf '%s\n' "${1%$'\n'*}"
    case "${1##*$'\n'}" in                # outcomes: a, the tool's own failed-login answer; L, the limit status after that; w, another answer; i, inconclusive
      "$4 0 "*) case "$5" in *a*) set -- L "${@:2}" ;; *) set -- i "${@:2}" ;; esac ;;
      502" 0 "*|503" 0 "*|504" 0 "*) set -- i "${@:2}" ;;      # an unavailable or overloaded upstream, not an application answer
      [12345][0123456789][0123456789]" 0 "*)
        case "$6:${1##*$'\n'}" in         # the tool's own failed-login answer; Appsmith's is a redirect to its login error page, whatever origin precedes it
          nocodb:"400 0 "*|baserow:"401 0 "*|budibase:"403 0 "*|budibase:"429 0 "*|windmill:"400 0 "*|windmill:"429 0 "*) set -- a "${@:2}" ;;
          appsmith:3??" 0 "*'/user/login?error=true'|appsmith:3??" 0 "*'/user/login?error=true&'*) set -- a "${@:2}" ;;
          *) printf 'http %.3s is not the failed-login answer of %s\n' "${1##*$'\n'}" "$6"; set -- w "${@:2}" ;;
        esac ;;
      *) set -- i "${@:2}" ;;                                  # curl failed or gave no status
    esac
    set -- "$2" "$(($3 - 1))" "$4" "$5$1" "${@:6}"         # the outcome letter replaced the curl result as $1; append it to the outcomes so far
  done
  case "$4" in
    *L*) case "$3" in 502|503|504) echo "the proxy answered $3 after the application had answered, but limit_conn and an upstream under load also return $3, so this does not show that the login limit fired; set the limit's rejection status (nginx limit_req_status) to one nothing else on this path returns; inconclusive"; exit 3 ;; esac
         echo "the proxy answered $3 after the application had answered: this login path is rate limited here"; exit 0 ;;
    *w*) echo "no $3 followed an application answer, and at least one answer was not the failed-login answer of $5 (its status is shown above), so the login URL's path or the tool on the set -- line may be wrong; inconclusive"; exit 3 ;;
    *i*) echo "no $3 followed an application answer, and at least one attempt was inconclusive; inconclusive"; exit 3 ;;
  esac
  echo "FINDING: every attempt got the application's own answer and none got $3; the login limit did not answer at this arrival rate"; exit 1
)
```

REASONED: following block; the fail2ban jail check for the brute-force control in the introduction, reasoned from the fail2ban 1.1.1 client and server sources listed under Sources and from a local run of fail2ban 1.1.1 itself. No deployment was available: fail2ban is not installed on the authoring host, and no proxy or low-code tool was available to send real logins through, so the check has not run against a real jail with a real ban action. What ran, on 2026-11-11: fail2ban 1.1.1's own client and server from the 1.1.1 tag's source tarball, without root, on a Unix socket, with the shipped dummy ban action and a test jail reading a hand-written access log. Four failed-login lines from `198.51.100.7`, above the jail's maxretry of 3, got that address banned, and `fail2ban-client status JAIL` printed the forms this block matches. The block passed bash -n in bash 5.3.9 and ShellCheck 0.11.0, and it ran against that client through a pass-through sudo stub. A banned IPv4 and a banned IPv6 address exited 0. An address that was not banned, an empty list, `203.0.113.50` while `203.0.113.5` was banned, and a missing jail exited 1. A socket the account could not open and a stopped server exited 3. Stubs replaying the recorded output with one change each also exited 3: the missing-jail answer with status 0, the status with status 255, another jail's header, a trailing line, a space in place of the tab, no output, and a failing sudo. The guards refused, with status 2, placeholders, a missing marker, wrong value counts, jail names with a space or a leading hyphen or empty, `999.1.1.1`, `01.2.3.4`, `1.2.3.4:22`, a host name, uppercase, bracketed or dotted IPv6, and a missing sudo or fail2ban-client. Run it on the host where fail2ban runs, after a burst of failed logins from a test address: the previous block with an attempt count above the jail's maxretry (`sudo fail2ban-client get JAIL maxretry` prints it), or failed logins by hand. The previous block sends a real failed login in each tool's own format, so each attempt leaves an access-log line whose login path and status a filter for that tool can match: NocoDB's bad-request error for invalid credentials (the code that maps it to a status is not pinned here), Baserow's 401, Budibase's 403 (and its lockouts' 403 and 429) and Windmill's 400 (and 429 once one of its limits answers). Appsmith answers a failed form login, its login limit's refusal and a successful form login alike with a redirect, so a filter on the status alone cannot separate failed logins from successful ones there, and this guide gives no Appsmith filter. That block may end inconclusive once the ban takes effect, as its own paragraph says. The jail counts only the log lines its filter matches, and it bans an address once the failures counted for it reach maxretry, so if the proxy's limit answers before the application has refused that many attempts, send the failed logins by hand instead. Use a test address you can afford to have banned and that is not your only way in: depending on the jail's ban action, which this guide has not traced, the ban can cut that address off from the host. An address in the jail's ignoreip list, or one of the host's own while ignoreself is on, is never counted. fail2ban bans the address it reads from the proxy's access log, so behind a CDN or another proxy that log must carry the recovered client address, as the introduction says, or the jail sees the CDN's address instead; give the address as that log writes it. Substitute the jail name and the address inside the single quotes. The block runs `sudo fail2ban-client status JAIL`, because without access to the server's socket the client logs "Permission denied to socket" and "(you must be root)", as it did in the local run. sudo exits with the status of the command it ran, per the sudo manual's exit value section. Where sudoers sets `secure_path`, sudo looks `fail2ban-client` up in that path instead of your PATH, so the `command -v fail2ban-client` check can refuse although sudo would find it, or pass and then end with status 3 when sudo cannot run it, per the guide's cited sudo sudoers manual, secure_path entry. The client prints its answer on standard output, logs errors on standard error, and exits 0 when the server accepts the command and 255 otherwise. Exposed: the client exits 255 and prints "Sorry but the jail 'JAIL' does not exist" (the man page says a stopped jail is removed), or the jail's status does not list the test address on its last line, which holds `Banned IP list:`, a tab and the space-separated addresses; the block exits 1 for either. Fixed: the address is in that list, and the block exits 0. A server that is not running, a socket the account cannot open, a failed sudo and any output not in one of those forms end with status 3. fail2ban lists an IPv6 address in its compressed lowercase form (measured: `2001:DB8:0:0:0:0:0:6` was listed as `2001:db8::6`), so give it in that form; another spelling of the same address reports a finding. The list shows fail2ban's record: the jail records a ban before it runs the ban actions, and it only logs an action that fails, so confirm the ban took effect by checking that the test address can no longer reach the proxy. Lift the ban afterwards with `sudo fail2ban-client set JAIL unbanip ADDRESS`.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_JAIL_NAME' 'REPLACE_WITH_TEST_ADDRESS'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not checking"; exit 2; }
  case "$1" in *REPLACE_WITH_*|""|-*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo "substitute the jail name (letters, digits, dots, underscores and hyphens) on the set -- line above; not checking"; exit 2 ;; esac
  set -- "$1" "$2" '^((25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])[.]){3}(25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])$'   # the jail, the address, then the IPv4 pattern, held here rather than in a named variable
  case "$2" in
    *:*:*) case "$2" in *[!0123456789abcdef:]*) echo "give an IPv6 address in lowercase hex digits and colons only; not checking"; exit 2 ;; esac ;;
    *) [[ $2 =~ $3 ]] || { echo "substitute one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not checking"; exit 2; } ;;
  esac
  { command -v sudo && command -v fail2ban-client; } >/dev/null || { echo "sudo and fail2ban-client must both be installed here; run this on the host where fail2ban runs; not checking"; exit 2; }
  set -- "$1" "$2" "$(if sudo fail2ban-client status "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3##*$'\n'}" "${3%$'\n'*}"   # the jail, the address, the client's exit status, then its standard output
  set -- "$1" "$2" "$3" "${4%$'\n'}"              # the output without its final line break
  printf '%s\n' "$4"
  case "$3:$4" in
    "255:Sorry but the jail '$1' does not exist") echo "FINDING: fail2ban has no jail named $1"; exit 1 ;;
    "0:Status for the jail: $1"$'\n'*$'\n''`- Actions'$'\n''   |- Currently banned:'$'\t'*$'\n''   |- Total banned:'$'\t'*$'\n''   `- Banned IP list:'$'\t'*) ;;
    *) echo "fail2ban-client exit $3 without a jail status or missing-jail answer this block recognizes (see any message above); inconclusive"; exit 3 ;;
  esac
  case "${4##*$'\n'}" in '   `- Banned IP list:'$'\t'*) ;; *) echo "the status does not end with the jail's banned list; inconclusive"; exit 3 ;; esac
  case " ${4##*$'\t'} " in                        # the banned list: the text after the status's last tab, space-separated
    *" $2 "*) echo "$2 is in jail $1's banned list: fail2ban recorded the ban"; exit 0 ;;
    *) echo "FINDING: jail $1 exists but $2 is not in its banned list"; exit 1 ;;
  esac
)
```

REASONED: following block; this file check reads only a local file and needs no service. It rests on the guide's cited Windmill v1.864.1 Compose file, which sets `REQUIRE_SIGNED_DEBUG_REQUESTS=true` on the `windmill_extra` service that runs the debugger, and on the Windmill v1.864.1 debugger signed-request switch, under which only the exact value `false` turns signing off. Before it reads any line, and so whether or not a line names the variable, the block exits 3 with a message to check the file by hand when the file starts with the bytes FF FE or FE FF, as a UTF-16 file does, or holds a NUL byte, or its size cannot be measured, because grep reads a NUL byte as a line break. It also exits 3 there when the file holds a line break other than LF or CRLF: a carriage return with another byte after it or as the last byte of the file, or one of the Unicode line breaks NEL, LS and PS, at which grep does not end a line, so the block cannot tell which lines the file holds. Exposed, a line sets the variable to `false`, exactly and in lower case, after `=` or `:` and an optional quote, and, once the checks above pass, the block prints that line and exits 1, whatever the other lines hold. Fixed, the block exits 0 when no line names the variable, printing "is not set in this file", or when every line that names it is read as `true` or `1`, as the vendor's `=true` line is, provided in both cases that none of the following tests matches. On both of those paths it exits 3 instead, unless a line is the finding, when the file holds a backslash or a `!` anywhere, or a line that holds a `$` and is neither a comment, whose first non-blank character is `#`, nor of the one form this block accepts for a `$`. That form is optional leading blanks, an optional YAML list dash and blanks, a key of letters, digits, underscores and hyphens, then `=` with no blank around it or `:` with at least one blank after it, and a whole value that is exactly one `${NAME}` or `${NAME:-default}`. The hyphen, as in the vendor's `max-size`, is the one character the key may hold beyond those of a variable name; NAME holds only letters, digits and underscores, and the default holds no `$`, `{` or `}`. The value may have one quote character, `"` or `'`, before it and one after it, which the block does not require to match, and the line may end in whitespace, a CRLF end included. The block counts the lines that hold a `$` and the lines with a `$` that are such a comment or of that form, each with `grep -c`, and on both paths exits 3 unless the two counts are equal. It also exits 3 on both paths, whatever the lines hold, for a file that has a `$` anywhere and also holds anywhere any of the names `env_file`, `extends`, `include` or `project_directory`, with the message "this file loads other files and uses interpolation; check them by hand". That test is on the whole file, not on lines, because compose-go substitutes `${...}` before it loads the files those keys name, so a path can come from `.env` or the shell through a value on a later line, a block scalar, a multi-line or quoted value, an alias or a quoted or aliased key, and no line test was found to cover every such form. The names are matched in lower case, the only case Compose's schema accepts for them, and the pinned Compose file holds none of the four. A line of that form substitutes a value only: its `${...}` comes after the `=` or `:` that ends the key written before it, so it cannot build that key. A backslash is refused because an escaped spelling of the name, such as `\x52` or `\u0052` for its first letter in a quoted YAML or JSON string, cannot be ruled out. A `!` is refused because every YAML tag starts with one, and a tag such as `!!binary` can spell the name in base64. The `$` rule is there because compose-go substitutes `${...}` before it cuts a list item at its first `=`, so an interpolated list item such as `- REQUIRE_SIGNED_${X:-DEBUG}_REQUESTS`, or one whose `=` or part of whose name comes from `.env`, can build the variable's name, which compose-go takes from the item up to that `=`, or the whole item if it has none; this block expands no substitution. The lines the rule refuses include these `.env`-assisted and name-building shapes, such as `- ${P}_REQUESTS${E}false` with `P` and `E` set in `.env`, and `- REQUIRE_SIGNED_DEBUG_${B}`. When the `!` test, the `$` rule or the file-level test refuses a file, the message says to check the file by hand, except that the file-level message says to check them, the loaded files, by hand. The `!` test has no comment exemption and does not look at where the `!` sits, so a `!` in an unrelated line or in a comment also ends with status 3; a `$` in an unrelated line that is not a comment and not of that form, such as `URL=http://h/?a=$$b`, does too, and that file then needs the same check by hand. The pinned Compose file holds no backslash and no `!`, and each of its 12 lines with a `$`, such as `max-size: "${LOG_MAX_SIZE:-20m}"`, `image: ${WM_IMAGE}`, `- DATABASE_URL=${DATABASE_URL}` and the comment `#   image: ${WM_IMAGE}`, is of that form or a comment, so it still exits 0. A line is read that way only when it holds nothing but optional leading spaces, an optional YAML list dash and spaces, the variable name in optional quotes, `=` or `:` with optional blanks around it, `true` in any letter case or `1` in optional quotes, optional blanks, an optional comment that starts with `#` after a blank, and optional trailing whitespace, a CRLF end included. That comment may hold only printable ASCII characters and blanks, so a comment with any other byte, such as an em dash, ends with status 3. Any other line that names the variable ends with status 3 and a message that the block cannot read that value form, so check that line by hand: examples are a `${...}` substitution, a YAML anchor, alias or tag, a value on the next line, an empty value, a commented-out line, a longer name that contains this one and a case variant such as `False`. The block counts the lines that name the variable and the whole lines that match that form, each with `grep -c`, and exits 0 only when the two counts are equal. A commented-out line that sets it to `false` also reports, and so does a quoted `"false"`, even where the quotes would stay in the value, so inspect each hit. Run it once for each Compose and environment file the deployment uses, including every file an `env_file:` line names, the `.env` Compose reads for variable substitution, every file an `extends:` or `include:` entry names, and the override file it loads automatically. Compose loads one such file, the first it finds of `compose.override.yml`, `compose.override.yaml`, `docker-compose.override.yml` and `docker-compose.override.yaml`, so check each of those that exists. The block reads only the files you give it, so every file that a Compose file loads through `env_file:` (short or long form), `include:` (with its `project_directory:`) or `extends:` with `file:` must itself be given to the block, with its path resolved from `.env` and the shell where Compose interpolates it. So must every file chosen outside the Compose file: those listed in `COMPOSE_FILE`, set in `.env` or in the shell, those after `-f`, and an `--env-file`, or the files named in `COMPOSE_ENV_FILES`, used in place of `.env`. Docker's documentation lists `COMPOSE_ENV_FILES`; it is not in the compose-go v2.16.2 source this review read, so it was not checked by a run. A remote `include:` or `extends:` target, if your Compose version accepts one, must be fetched and checked the same way; the block cannot read it, and this guide has not checked which remote targets the Compose CLI accepts. Values supplied from outside the files, such as the shell environment Compose runs in, are beyond its reach. A command or entrypoint that sets the variable when the container starts, for example `sh -c "export ..."`, is outside what the block is built to read, which is Compose environment entries and env-file lines. Apart from its argument checks (the pasted `set --` line, its one value and the placeholder test), the `[ -f ]` and `[ -r ]` test that the path is a readable regular file, and its first-byte, size and last-byte checks, the block branches only on grep's exit status and on the counts `named`, `known`, `dl` and `wl`. It keeps grep's status in `bs` for the backslash test, in `ti` for the `!` test, in `ld` for the file-level test of the four names, in `ds` for `dl`, in `ws` for `wl` and in `rc` for `named` and `known`, and reads it directly for its other tests. It also sets `h`, a hyphen, which it never tests. For grep, status 0 means a line is selected, 1 that none is and above 1 an error, as the sample-token block's recorded runs under GNU grep 3.12 show, and a read error ends with status 3. No Windmill deployment was available for this review, and the check has not been run against one. The block passed bash -n and ShellCheck 0.11.0, and 452 local runs against fixture files, including a copy of the pinned Compose file, under GNU grep 3.12 ended with status 0, 1, 2 and 3 as stated above. Substitute the file path inside the single quotes, and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENV_OR_COMPOSE_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit 2 ;; esac
  { [ -f "$1" ] && [ -r "$1" ]; } || { echo "cannot read $1 as a regular file; not checked"; exit 2; }
  case "$(head -c 2 -- "$1" | od -A n -t x1 | tr -d ' \n')" in   # the first two bytes in hex: FF FE or FE FF starts a UTF-16 file
    fffe|feff) echo "$1 starts with a UTF-16 byte order mark, which grep does not read as text; cannot read this value form; check it by hand; not checked"; exit 3 ;;
  esac
  # grep reads a NUL byte as a line break, so a file holding one cannot be counted by line: compare its size with its size minus its NUL bytes
  [ "$(LC_ALL=C tr -d '\0' < "$1" | wc -c)" -eq "$(wc -c < "$1")" ] || { echo "$1 holds a NUL byte or could not be measured; cannot read this value form; check it by hand; not checked"; exit 3; }
  # grep does not end a line at a CR followed by another byte, NEL (C2 85), LS (E2 80 A8) or PS (E2 80 A9); one pattern per line below
  if LC_ALL=C grep -q -E -e "$(printf '\r.\n\302\205\n\342\200\250\n\342\200\251')" -- "$1"; then
    echo "$1 holds a line break other than LF or CRLF (a lone CR, NEL, LS or PS); cannot read this value form; check it by hand; not checked"; exit 3
  else
    case "$?" in
      1) ;;
      *) echo "grep could not read $1; not checked"; exit 3 ;;
    esac
  fi
  [ "$(tail -c 1 -- "$1" | od -A n -t x1 | tr -d ' \n')" != 0d ] || { echo "$1 ends with a CR and no LF after it; cannot read this value form; check it by hand; not checked"; exit 3; }
  LC_ALL=C grep -q -F -e "\\" -- "$1"; bs=$?   # 0 when the file holds a backslash, which can escape a letter of the name
  [ "$bs" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
  LC_ALL=C grep -q -F -e '!' -- "$1"; ti=$?   # 0 when the file holds a ! byte, which every YAML tag starts with
  [ "$ti" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
  dl=$(LC_ALL=C grep -c -F -e "\$" -- "$1"); ds=$?   # lines that hold a $
  [ "$ds" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
  h=-   # a hyphen, kept out of the bracket expressions below
  wl=$(LC_ALL=C grep -c -E -e "^[[:blank:]]*(#.*[$].*|(${h}[[:blank:]]+)?[[:alnum:]_${h}]+(=|:[[:blank:]]+)(\"|')?[$][{][[:alnum:]_]+(:${h}[^$}{]*)?\}(\"|')?[[:space:]]*)\$" -- "$1"); ws=$?   # lines with a $ that are a comment, or KEY=, KEY: and a blank, then a whole value of one ${NAME} or ${NAME:-default}, quotes optional
  [ "$ws" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
  LC_ALL=C grep -q -E -e 'env_file|extends|include|project_directory' -- "$1"; ld=$?   # 0 when the file holds the name of a key that loads other files, anywhere in it
  [ "$ld" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
  if LC_ALL=C grep -n -F 'REQUIRE_SIGNED_DEBUG_REQUESTS' -- "$1"; then   # every line that names the setting
    if LC_ALL=C grep -q -E "(^|[^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_])(\"|')?REQUIRE_SIGNED_DEBUG_REQUESTS(\"|')?[[:blank:]]*(=|:)[[:blank:]]*(\"|')?false(\$|[[:space:]]|\"|'|,|#|\})" -- "$1"; then   # set to false, in value position
      echo "FOUND REQUIRE_SIGNED_DEBUG_REQUESTS set to false: the debugger then accepts unsigned debug sessions; remove the line or set it to true"; exit 1
    else
      case "$?" in
        1) ;;
        *) echo "grep could not read $1; not checked"; exit 3 ;;
      esac
    fi
    named=$(LC_ALL=C grep -c -F 'REQUIRE_SIGNED_DEBUG_REQUESTS' -- "$1"); rc=$?   # lines that name the setting
    [ "$rc" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
    known=$(LC_ALL=C grep -c -E "^ *(- +)?(\"|')?REQUIRE_SIGNED_DEBUG_REQUESTS(\"|')?[[:blank:]]*(=|:)[[:blank:]]*(\"|')?([Tt][Rr][Uu][Ee]|1)(\"|')?([[:blank:]]+#[[:print:][:blank:]]*)?[[:space:]]*\$" -- "$1"); rc=$?   # whole lines that set it to true or 1
    [ "$rc" -le 1 ] || { echo "grep could not read $1; not checked"; exit 3; }
    [ "$named" = "$known" ] || { echo "cannot read this value form: a line above names REQUIRE_SIGNED_DEBUG_REQUESTS without setting it plainly to true or 1; check each such line by hand; not checked"; exit 3; }
    [ "$bs" -eq 1 ] || { echo "every line above sets it to true or 1, but $1 holds a backslash, so an escaped spelling of the name elsewhere in the file cannot be ruled out; check the file by hand; not checked"; exit 3; }
    { [ "$ti" -eq 1 ] && [ "$dl" -eq "$wl" ]; } || { echo "$1: cannot read this file with certainty (YAML tags or interpolated names); check it by hand; not checked"; exit 3; }
    { [ "$dl" -eq 0 ] || [ "$ld" -eq 1 ]; } || { echo "$1: this file loads other files and uses interpolation; check them by hand; not checked"; exit 3; }
    echo "every line above sets it to true or 1 in a form this block reads; the pinned debugger turns signing off only for the exact value false"; exit 0
  else
    case "$?" in
      1) [ "$bs" -eq 1 ] || { echo "no line names REQUIRE_SIGNED_DEBUG_REQUESTS, but $1 holds a backslash, so an escaped spelling of the name cannot be ruled out; check the file by hand; not checked"; exit 3; }
         { [ "$ti" -eq 1 ] && [ "$dl" -eq "$wl" ]; } || { echo "$1: cannot read this file with certainty (YAML tags or interpolated names); check it by hand; not checked"; exit 3; }
         { [ "$dl" -eq 0 ] || [ "$ld" -eq 1 ]; } || { echo "$1: this file loads other files and uses interpolation; check them by hand; not checked"; exit 3; }
         echo "REQUIRE_SIGNED_DEBUG_REQUESTS is not set in this file" ;;
      *) echo "grep could not read $1; not checked"; exit 3 ;;
    esac
  fi
)
```

REASONED: Manual Windmill worker Docker-socket check, per the guide's cited Windmill v1.864.1 Compose worker volumes; no Windmill deployment or container runtime was available, so it has not been run. On the Docker host, run `docker inspect --format '{{json .Mounts}}' CONTAINER` for each worker container; the vendor's file starts three `windmill_worker` replicas and one `windmill_worker_native` container, whose only volume there is its logs. Exposed: a mount whose source or destination ends in `docker.sock`, or is a directory above the file's commented-out socket path `/var/run/docker.sock`, that is `/var/run`, `/var` or the root `/`, or `/run` where `/var/run` links to it, because binding a parent directory carries the socket into the container (this guide's reasoning). Fixed: no such mount, on every worker container. A daemon configured with a socket at another path needs the same check against that path. The fields `docker inspect` prints are taken from Docker's own output format, not from a pinned Docker source this guide read. The check sees only mounts, not a daemon reached over TCP, so also read each worker's Compose `environment:` entries for `DOCKER_HOST` (this guide's reasoning).

REASONED: following block; this check reads NocoDB's proxy-trust setting from the container, per the guide's cited NocoDB 2026.09.0 proxy trust default (`NC_TRUST_PROXY`), NocoDB 2026.09.0 port default, JWT secret generation and proxy-trust reset, and Docker `docker exec` environment. No deployed NocoDB container was available, because the authoring host has no container runtime. At startup NocoDB replaces Express's `trust proxy` with the value it reads from `NC_TRUST_PROXY` after trimming whitespace: unset, empty or `false` in any letter case trusts no proxy, `true` in any letter case trusts all proxies in the words of its source comment, a whole number is a hop count, and anything else goes to Express as a subnet or keyword list. Per the guide's cited NocoDB 2026.09.0 lockfile, `packages/nocodb` uses Express 4.21.2, which uses proxy-addr 2.0.7, so the guide's cited proxy-addr 2.0.7 `index.js` and Express 4.21.2 `lib/utils.js` show how Express reads that value. Exposed, the value is `true`, and the block prints it and exits 1, because the NocoDB section says never to set `true` on a server clients can reach directly and gives a hop count or subnet as the setting behind a proxy. It also exits 1 when an item of the value, split on commas and trimmed of blanks as Express 4.21.2's `compileTrust` does for a string, ends in `/` and only zeros or in the netmask `/0.0.0.0`, an all-address range such as `0.0.0.0/0` or `::/0`. Such a value is invalid: Express hands the items to proxy-addr's `compile`, whose range parse in proxy-addr 2.0.7 runs `if (range <= 0 || range > max)` and throws, so the message says the value was meant to trust every address and asks for the address or hop count of the proxy in front. Fixed, the block prints the value and exits 0 only for a value that trusts nothing: unset, empty, `false` in any letter case, or a whole number made only of zeros, such as `0` or `00`, which reaches Express 4.21.2 as a hop count of 0 under its rule `return function(a, i){ return i < val }` and so trusts none of the addresses. Every other value exits 3, and 3 is the expected result for a correctly proxied deployment, whose setting is a hop count or the address or range of its proxy. Every such value that is a hop count or a list proxy-addr accepts trusts a client that connects directly in some topology, so this block, which cannot see whether clients reach NocoDB directly, cannot tell a proxied deployment from an exposed one, and its message asks you to confirm by hand that only the proxy is trusted. A value proxy-addr 2.0.7 rejects, such as `all` or `true,10.0.0.0/8`, makes Express throw at startup instead, because Express 4.21.2's `compileTrust` in `lib/utils.js` splits the value on commas and hands the items to proxy-addr's `compile`, and proxy-addr 2.0.7's `index.js` throws for an item that is neither an IP address nor one of its keywords. A hop count N of 1 or more trusts the nearest N addresses in the chain under that rule, the connecting address first, so a client that connects directly is itself trusted; the message states that rule, with N printed without its leading zeros, as NocoDB's `Number()` drops them, so confirm that clients reach NocoDB only through the proxies in front and that N matches their number. When N has more than 15 digits after its leading zeros, which `Number()` can round, since it is exact only up to 2^53, the message does not print N and says instead that the hop count is too large for this block to print as NocoDB reads it, and it asks for the same check by hand. An address, range or keyword trusts every address it covers, a keyword standing for the ranges proxy-addr 2.0.7 lists for it, and proxy-addr 2.0.7's `trustSingle` converts an IPv4 client address to its IPv4-mapped form before it matches an IPv6 range, so `::/1` also trusts every IPv4 client. The block does not parse addresses or ranges, so a list that covers every address with ranges proxy-addr accepts, such as `0.0.0.0/1,128.0.0.0/1`, and a value proxy-addr 2.0.7 rejects, such as `all` or `true,10.0.0.0/8`, also exit 3; confirm that the list is one proxy-addr accepts and names only the proxies in front. Before it classifies the value, the block exits 3 when the value holds any byte outside printable ASCII, a tab or line break included, because JavaScript's `trim()` may treat such a byte as whitespace; that message does not repeat the value, though the printed `NC_TRUST_PROXY=` line above it does. It exits 3 for a value with leading or trailing whitespace, and 3 when it cannot read the setting, for example from a missing container. Like the key-presence block, it reads the container's configured environment, which `docker exec` inherits, not the server process's own, and which start script the image runs was not verified. The value is not a secret, so the block prints it. Its in-container `printf` ends the value with `|` so that a trailing line break survives the capture, and any other output ends with status 3. That `docker exec` passes the command's standard output through is assumed here; the cited Docker page does not state it. The block passed bash -n and ShellCheck 0.11.0, and 94 local runs against a stub docker that ran the in-container script without a container ended with status 0, 1, 2 and 3 as stated above. Substitute the container name inside the single quotes, and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOCODB_CONTAINER_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit 2; }
  case "$1" in *REPLACE_WITH_*|""|-*|*[[:cntrl:]]*) echo "substitute the container name on the set -- line above; not checking"; exit 2 ;; esac
  command -v docker >/dev/null || { echo "docker is not installed here; not checking"; exit 2; }
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand inside the container
  set -- "$1" "$(docker exec "$1" sh -c 'if [ "${NC_TRUST_PROXY+set}" = set ]; then printf "nc-trust-proxy:set:%s|" "$NC_TRUST_PROXY"; else printf "nc-trust-proxy:unset|"; fi')"
  case "$2" in                          # the in-container printf ends with |, so a trailing line break in the value survives the capture
    'nc-trust-proxy:unset|') echo "NC_TRUST_PROXY is unset in the container's configured environment: NocoDB trusts no proxy, its default"; exit 0 ;;
    'nc-trust-proxy:set:'*'|') set -- "$1" "${2#nc-trust-proxy:set:}"; set -- "$1" "${2%|}" ;;
    *) echo "could not read NC_TRUST_PROXY in container $1; not checked"; exit 3 ;;
  esac
  printf 'NC_TRUST_PROXY=%s\n' "$2"
  if printf '%s' "$2" | LC_ALL=C grep -q -z -E '[^[:print:]]'; then   # -z reads the value as one record, so a line break in it is tested too
    echo "the value holds a byte outside printable ASCII, which JavaScript trim() may treat as whitespace, so this block cannot classify it; read it yourself; not checked"; exit 3
  else
    case "$?" in
      1) ;;
      *) echo "grep could not test the value; not checked"; exit 3 ;;
    esac
  fi
  case "$2" in
    "") echo "empty: NocoDB trusts no proxy"; exit 0 ;;
    [[:space:]]*|*[[:space:]]) echo "the value has leading or trailing whitespace, which NocoDB trims before reading it; inconclusive: read it yourself"; exit 3 ;;
    [Tt][Rr][Uu][Ee]) echo "FINDING: NC_TRUST_PROXY is true, so NocoDB trusts all proxies; set it to the hop count or subnet of the proxy in front"; exit 1 ;;
    [Ff][Aa][Ll][Ss][Ee]) echo "false: NocoDB trusts no proxy"; exit 0 ;;
    *[!0123456789]*) ;;                 # an address, range or keyword list, or a value proxy-addr rejects: tested for a range of 0 below, else status 3
    *[!0]*) z=${2%%[123456789]*}; n=${2#"$z"}   # the hop count with its leading zeros dropped, as JavaScript's Number() drops them
      case "$n" in
        ????????????????*) echo "NocoDB reads $2 as a hop count too large for this block to print as NocoDB reads it: it has more than 15 digits after its leading zeros, and JavaScript's Number() can round such a number. Express trusts the nearest addresses in the chain up to that count, the connecting address first, so a client that connects directly is trusted too; this block cannot see whether clients reach NocoDB directly, so confirm by hand that only the proxy is trusted: clients reach it only through the proxies in front; not checked"; exit 3 ;;   # 16 or more digits
        1) a=address; p=proxy ;;
        *) a=addresses; p=proxies ;;
      esac
      echo "NocoDB reads $2 as the hop count $n, and Express trusts the nearest $n $a in the chain, the connecting address first, so a client that connects directly is trusted too; this block cannot see whether clients reach NocoDB directly, so confirm by hand that only the proxy is trusted: clients reach it only through the $n $p in front; not checked"; exit 3 ;;
    *) echo "a hop count of 0: NocoDB passes the number 0 to Express, whose hop-count rule trusts none of the addresses, so no proxy is trusted"; exit 0 ;;
  esac
  if printf '%s' "$2" | LC_ALL=C grep -q -E '/(0+|0\.0\.0\.0)[[:blank:]]*(,|$)'; then   # an item ending in a range of 0, once Express splits on commas and trims
    echo "FINDING: NC_TRUST_PROXY contains an all-address range; proxy-addr 2.0.7, which NocoDB 2026.09.0's lockfile pins through Express 4.21.2, rejects a range of 0, so the value is invalid and was meant to trust every address; replace it with the address or hop count of the proxy in front"; exit 1
  else
    case "$?" in
      1) ;;
      *) echo "grep could not test the value; not checked"; exit 3 ;;
    esac
  fi
  echo "passed to Express as an address, range or keyword list; this block cannot see whether clients reach NocoDB directly or whether proxy-addr accepts the list, so confirm by hand that only the proxy is trusted: the list is valid and names only the proxies in front of NocoDB; not checked"; exit 3
)
```

REASONED: following block; the CORS check for the NocoDB section, reasoned from the guide's cited NocoDB 2026.09.0 Docker bundle entry (`timely.ts`), which calls `cors()` with no options, and the guide's cited expressjs/cors v2.8.5 `lib/index.js`, whose default origin `*` sets `Access-Control-Allow-Origin: *` on every response and preflight it handles, without `Access-Control-Allow-Credentials`. No NocoDB deployment and no fronting nginx or Caddy were available to this review (the authoring host has no container runtime, and opening network listeners on it is not permitted), so the block has not been run against a deployment, and nobody has yet observed its exposed or fixed outcome. On 2026-11-25 the block passed bash -n in bash 5.3.9 and ShellCheck 0.11.0, and 34 local runs with a stub curl that replayed header fixtures, without network access, ended with statuses 0, 1, 2 and 3 as stated below, 34 of 34 matching. Run it from a host that reaches NocoDB through its proxy, the way a user's browser does: it sends one GET with the header `Origin: https://evil.example`, a deliberately foreign origin under the reserved `.example` top-level domain, and prints each status line, each `Access-Control-Allow-Origin` line and curl's result line. The block judges only the final response, the last header block curl prints: the lines of an interim 1xx response, such as 100 Continue, are printed but not judged. Exposed, a line of the final response gives `*` or the probe origin, whatever the status and even after a failed transfer, and the block exits 1; that includes a proxy that adds your origin with nginx `add_header` without hiding NocoDB's `*`, since the answer then carries both. Fixed, on a 2xx answer, the header is absent, or appears once with exactly the allowed origin you give, and the block exits 0. A failed request or a missing status line, a non-2xx answer, which may come from the proxy rather than NocoDB (such as a 502 or a login redirect), the header more than once, any other value, or your origin when you gave `none` exits 3, and a missing curl or awk or a refused `set --` value exits 2. Give NocoDB's address with the path `/api/v1/health`: the guide's cited NocoDB 2026.09.0 health route declares no route guard and no `@Acl`, and its handler returns `message: 'OK'` with a timestamp and uptime. The only global guard, `ExtractIdsMiddleware` registered as `APP_GUARD`, returns true from `canActivate` once its `use()` step has run, and `GlobalGuard`, which authenticates, is attached with `@UseGuards` to other routes, not to this one. So by these sources a GET there without a login answers 2xx; that has not been run, and if it answers otherwise, give another NocoDB URL that answers 2xx. Behind a fronting login, which this guide advises, the request gets the login's answer, so the block exits 3 unless that path is reachable without logging in. A 2xx from a URL that does not reach NocoDB also passes, so give the address users reach NocoDB at; the block probes GET only, so a proxy rule limited to some methods is not tested, and a header line folded across lines is not parsed. Substitute, inside the single quotes, the NocoDB URL and your one allowed origin (scheme, host and any port, with no path) or `none`, then paste the whole block into a fresh shell.

```bash
(
  set +e                                # errexit off here, so curl's and awk's statuses are recorded below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOCODB_URL' 'REPLACE_WITH_ALLOWED_ORIGIN_OR_none'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|""|-*|*[[:space:][:cntrl:]]*) echo "substitute the NocoDB URL on the set -- line above; not probing"; exit 2 ;;
    http://?*|https://?*) ;;
    *) echo "the NocoDB URL must start with http:// or https://; not probing"; exit 2 ;;
  esac
  case "$2" in
    none) ;;
    *REPLACE_WITH_*|""|*[[:space:][:cntrl:]]*|https://evil.example) echo "substitute your own allowed origin, or none, on the set -- line above; not probing"; exit 2 ;;
    http://?*/*|https://?*/*) echo "an origin has no path: give its scheme, host and any port, or none, on the set -- line above; not probing"; exit 2 ;;
    http://?*|https://?*) ;;
    *) echo "the allowed origin must be none or start with http:// or https://; not probing"; exit 2 ;;
  esac
  { command -v curl && command -v awk; } >/dev/null || { echo "curl and awk must both be installed here; not probing"; exit 2; }
  # The probe origin https://evil.example is deliberately foreign; keep it as written.
  set -- "$1" "$2" "$(if curl -q -g -s -D - -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 -H 'Origin: https://evil.example' \
                        -w 'curl: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3##*$'\n'}" "${3%$'\n'*}"   # the URL, the allowed origin, curl's exit status, then the response headers and curl's result line
  set -- "$1" "$2" "$3" "$(if printf '%s\n' "$4" | awk '{ sub(/\r$/, "") } /^curl: http=/ || tolower($0) ~ /^http\/|^access-control-allow-origin:/ { print } /^HTTP\// { c = $2; n = 0; b = 0; v = "" } tolower(substr($0, 1, 28)) == "access-control-allow-origin:" { v = substr($0, 29); gsub(/^( |\t)+|( |\t)+$/, "", v); n++; if (v == "*" || v == "https://evil.example") b = 1 } END { printf "\n%s|%d|%d|%s", c, n, b, v }'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "${4##*$'\n'}" "${4%$'\n'*}"   # the URL, the allowed origin, curl's exit status, awk's exit status, then awk's output
  printf '%s' "${5%$'\n'*}"             # each status line, each Access-Control-Allow-Origin line and curl's result line
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}"           # then awk's summary: status code|header count|1 if * or the probe origin|last value
  set -- "$1" "$2" "$3" "$4" "${5%%|*}" "${5#*|}"
  set -- "$1" "$2" "$3" "$4" "$5" "${6%%|*}" "${6#*|}"
  set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7%%|*}" "${7#*|}"   # the URL, the allowed origin, curl's and awk's statuses, the HTTP status code, the header count, the bad flag, the last value
  [ "$4" = 0 ] || { echo "awk could not read the response headers; inconclusive"; exit 3; }
  [ "$7" != 1 ] || { echo "FINDING: Access-Control-Allow-Origin is * or echoes the probe origin https://evil.example; remove it at the proxy in front of NocoDB"; exit 1; }
  { [ "$3" = 0 ] && [ -n "$5" ]; } || { echo "curl exit $3: the request failed or printed no status line (see curl's result line above); inconclusive, not a pass"; exit 3; }
  case "$5" in 2??) ;; *) echo "HTTP $5 is not a 2xx answer, so it may not have come from NocoDB; give a URL NocoDB answers with 2xx through the proxy; inconclusive"; exit 3 ;; esac
  [ "$6" != 0 ] || { echo "no Access-Control-Allow-Origin for a foreign origin: pages on other sites cannot read this response"; exit 0; }
  { [ "$6" = 1 ] && [ "$2" != none ] && [ "$8" = "$2" ]; } && { echo "Access-Control-Allow-Origin names only your allowed origin $2"; exit 0; }
  echo "Access-Control-Allow-Origin lines: $6, last value: $8; neither absent nor exactly your allowed origin once; inconclusive: read the lines above"; exit 3
)
```

## Sources (checked September 2026)

The month in this heading is the month of the whole-guide documentation pass, and an item that carries its own later "checked" month was rechecked individually after that pass, so the later month applies to that item only.

- NocoDB 2026.09.0 port default, JWT secret generation and proxy-trust reset: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts
- NocoDB 2026.09.0 proxy trust default (`NC_TRUST_PROXY`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts
- NocoDB 2026.09.0 lockfile (pins Express 4.21.2 and proxy-addr 2.0.7 for `packages/nocodb`, and resolves cors only as 2.8.5; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/pnpm-lock.yaml
- proxy-addr 2.0.7 `index.js` as pinned by NocoDB 2026.09.0's lockfile (range parsing and hop trust): https://github.com/jshttp/proxy-addr/blob/v2.0.7/index.js
- Express 4.21.2 `lib/utils.js` as pinned by NocoDB 2026.09.0's lockfile (`compileTrust` for a number and a comma string): https://github.com/expressjs/express/blob/4.21.2/lib/utils.js
- NocoDB 2026.09.0 entry point (listen with no host, CORS): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts
- NocoDB 2026.09.0 Docker bundle build (`rspack.timely.config.js`: entry `src/run/timely.ts`, output `docker/main.js`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/rspack.timely.config.js
- NocoDB 2026.09.0 Docker bundle entry (`timely.ts`: `trust proxy`, `cors()` with no options, GUI mount; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/timely.ts
- NocoDB 2026.09.0 global guard (`xc-auth` header or `nc_token` cookie; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/guards/global/global.guard.ts#L21
- NocoDB 2026.09.0 auth cookies (`refresh_token` and `nc_token`, `httpOnly`, `SameSite=Lax`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/helpers.ts#L34-L58
- NocoDB 2026.09.0 API token strategy (`xc-token` or `Authorization: Bearer`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L17-L18
- NocoDB 2026.09.0 health route (`/api/v1/health`, no route guard; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/utils.controller.ts#L179-L182
- NocoDB 2026.09.0 global guard registration (`ExtractIdsMiddleware` as the only `APP_GUARD`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/app.module.ts#L45-L48
- NocoDB 2026.09.0 global guard check (`ExtractIdsMiddleware.canActivate` runs `use()` and returns `true`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/middlewares/extract-ids/extract-ids.middleware.ts#L473-L479
- NocoDB 2026.09.0 health handler (`appHealth` returns `message: 'OK'`, a timestamp and uptime; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/utils.service.ts#L131-L137
- expressjs/cors v2.8.5 `lib/index.js` (default origin `*`; Allow-Credentials only when `credentials` is `true`; checked November 2026): https://github.com/expressjs/cors/blob/v2.8.5/lib/index.js
- nginx proxy module (`proxy_hide_header`; rolling documentation, checked November 2026): https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- nginx headers module (`add_header`, `always` and inheritance; rolling documentation, checked November 2026): https://nginx.org/en/docs/http/ngx_http_headers_module.html
- Caddy `reverse_proxy` directive (`header_down`; rolling documentation, checked November 2026): https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- [curl curl-8_14_1 write-out fields and version requirements (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79).
- [curl curl-8_14_1 request headers (checked November 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- [curl curl-8_14_1 `dump-header` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/dump-header.md).
- [curl curl-8_14_1 `noproxy` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/noproxy.md).
- [curl curl-8_14_1 `globoff` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/globoff.md).
- [curl curl-8_14_1 `disable` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/disable.md).
- [curl curl-8_14_1 `silent` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/silent.md).
- [curl curl-8_14_1 `output` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/output.md).
- [curl curl-8_14_1 `max-time` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/max-time.md).
- [curl curl-8_14_1 `connect-timeout` option (checked November 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/connect-timeout.md).
- NocoDB 2026.09.0 first user, signup and its refusal message: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts
- NocoDB 2026.09.0 app settings (`invite_only_signup`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts
- NocoDB 2026.09.0 admin from environment (`NC_ADMIN_EMAIL`, `NC_ADMIN_PASSWORD`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initAdminFromEnv.ts
- NocoDB 2026.09.0 credential encryption: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts and https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initDataSourceEncryption.ts
- NocoDB 2026.09.0 container start scripts: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start.sh and https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start-litestream.sh
- Docker `docker exec` environment (rolling documentation, checked November 2026): https://docs.docker.com/reference/cli/docker/container/exec/
- Docker packet filtering (`DOCKER-USER`; rolling documentation, checked November 2026): https://docs.docker.com/engine/network/firewall-iptables/
- Docker CLI port display (`[::]:` from v27.2.0, `:::` through v27.1.2): https://github.com/docker/cli/blob/v27.2.0/cli/command/formatter/container.go and https://github.com/docker/cli/blob/v27.1.2/cli/command/formatter/container.go
- sudo SUDO_1_9_16p2 sudoers manual, secure_path (checked October 2026): https://github.com/sudo-project/sudo/blob/SUDO_1_9_16p2/docs/sudoers.man.in#L5650-L5655
- NocoDB 2026.09.0 README (Docker example JWT secret, Docker image, Auto-upstall and binaries note; checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md
- NocoDB 2026.09.0 README, Docker with SQLite and Docker with PG sections (checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L56-L75
- NocoDB 2026.09.0 README, Auto-upstall section (checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L77-L90
- NocoDB 2026.09.0 README, Auto-upstall command (checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L82
- NocoDB 2026.09.0 README, Auto-upstall script source link (checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L90
- NocoDB 2026.09.0 README, binaries note (checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L95
- NocoDB 2026.09.0 GitHub release API record (no assets listed when checked October 2026): https://api.github.com/repos/nocodb/nocodb/releases/tags/2026.09.0
- NocoDB 2026.09.0 tag package manifest (`0.301.3`; checked October 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/package.json#L3
- NocoDB 2026.09.0 sample environment without an encryption key: https://github.com/nocodb/nocodb/blob/2026.09.0/docker-compose/examples/external-postgres-and-redis/docker.env
- NocoDB 2026.09.0 sign-in routes (checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/modules/auth/auth.controller.ts#L83-L86
- NocoDB 2026.09.0 public API limiter guard on sign-in (always allows; rate limiting left to the network layer; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/guards/public-api-limiter.guard.ts#L4-L13
- NocoDB 2026.09.0 sign-in route guards (`PublicApiLimiterGuard` before the local strategy; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/modules/auth/auth.controller.ts#L88
- NocoDB 2026.09.0 local sign-in strategy (`email` and `password`; bad-request error for invalid credentials; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/local.strategy.ts#L18-L39
- NocoDB 2026.09.0 MFA columns migration (checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/meta/migrations/v0/nc_202603180000_user_mfa.ts
- NocoDB two-factor authentication documentation (licence requirement; rolling documentation not tied to a release, checked November 2026): https://nocodb.com/docs/product-docs/account-settings/authentication/two-factor-authentication
- NocoDB 2026.09.0 SSRF filter library (`request-filtering-agent`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L2-L6
- NocoDB 2026.09.0 SSRF switch (`isSsrfProtectionEnabled`: Cloud always on; `NC_DISABLE_SSRF_PROTECTION`, `NC_ALLOW_LOCAL_HOOKS`, `NC_WEBHOOK_ALLOW_PRIVATE_NETWORK`, `NC_ALLOW_LOCAL_EXTERNAL_DBS` and `NC_ALLOW_LOCAL_DATA_IMPORT`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L23-L49
- NocoDB 2026.09.0 webhook request agents (`getFilteredAgents` for `OperationSource.HOOKS`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L178
- NocoDB 2026.09.0 webhook private-address error (thrown only with `throwErrorOnFailure`; `NC_ALLOW_LOCAL_HOOKS=true` hint only when `!isEE || isOnPrem`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L738-L751
- NocoDB 2026.09.0 shared-view controller guard (`PublicApiLimiterGuard`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L21-L31
- NocoDB 2026.09.0 shared-view row routes (`xc-password` header; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L40
- NocoDB 2026.09.0 shared base link removal (`disableSharedBaseLink`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/shared-bases.controller.ts#L75-L80
- NocoDB 2026.09.0 API token header helper (`xc-token` first, then `Authorization: Bearer`; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/apiHelpers.ts#L75-L94
- NocoDB 2026.09.0 API token base scope (`base_id`; applies only when a request resolves a base; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L29-L38
- NocoDB 2026.09.0 legacy API tokens (a token with no owning user gets the editor role; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L44-L46
- NocoDB 2026.09.0 API token user (the token acts with its creating user's roles; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L50-L69
- NocoDB 2026.09.0 API token model (`permissions` and `expiry` fields; checked November 2026): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/models/ApiToken.ts#L26-L28
- Node.js v22 `server.listen` with an omitted host: https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md
- Baserow 2.3.4 Compose file: https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml
- Baserow 2.3.4 install with Docker (ufw warning): https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md
- Baserow 2.3.4 first user, signup and its refusal message: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py
- Baserow 2.3.4 settings model (`allow_new_signups`): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py
- Baserow 2.3.4 TOTP provider registration: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/apps.py
- Baserow 2.3.4 sample environment: https://github.com/baserow/baserow/blob/2.3.4/.env.example
- Baserow 2.3.4 login view (`ObtainJSONWebToken`: two-factor temporary token, no throttle, 401 for bad credentials; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/views.py
- Baserow 2.3.4 invalid-credentials error (`ERROR_INVALID_CREDENTIALS`, 401; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/errors.py#L41-L45
- Baserow 2.3.4 settings (`BASEROW_MAX_CONCURRENT_USER_REQUESTS` concurrency throttle; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py
- Baserow 2.3.4 login serializer (`email` or deprecated `username`, and `password`; no throttle, counter or captcha; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/serializers.py#L345-L389
- Baserow 2.3.4 sign-up captcha (captcha field on the sign-up serializer, checked on sign-up; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/serializers.py#L142-L185 and https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/views.py#L322-L323
- Baserow 2.3.4 login route (`/api/user/token-auth/`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/urls.py#L22, https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/urls.py#L46 and https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/urls.py#L33
- Baserow 2.3.4 throttle scope and rejection (anonymous requests skipped unless `BASEROW_THROTTLE_IP_ENABLED`; `ThrottledAPIException`, a subclass of REST framework's `Throttled`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/throttling/handler.py#L100-L140, https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/throttling/handler.py#L165-L190 and https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/exceptions.py#L47-L48
- Baserow 2.3.4 webhook private-address setting (`BASEROW_WEBHOOKS_ALLOW_PRIVATE_ADDRESS`, read with `bool(os.getenv(...))`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1186-L1188
- Baserow 2.3.4 integration private-address setting (`BASEROW_INTEGRATIONS_ALLOW_PRIVATE_ADDRESS`, read with `bool(os.getenv(...))`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1217-L1219
- Baserow 2.3.4 data sync private-address setting (`BASEROW_DATA_SYNC_ALLOW_PRIVATE_ADDRESS`, default `true`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1220-L1222
- Baserow 2.3.4 webhook request helper (`advocate` unless the webhook setting is true; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/webhooks/validators.py#L28-L38
- Baserow 2.3.4 integration request helper (`advocate` unless the integration setting is true; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/integrations/utils.py#L19-L22
- Baserow 2.3.4 data sync request helper (plain `requests` while the setting is true; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/data_sync/utils.py#L20-L32
- Baserow 2.3.4 configuration documentation, webhook address settings (checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/docs/installation/configuration.md#L146-L149
- Baserow 2.3.4 view model (`public`, `public_view_password`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/views/models.py#L109-L122
- Baserow 2.3.4 database token model and permissions (row endpoints; table, database or workspace scope; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L19-L21 and https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L75-L82
- Baserow 2.3.4 database token authentication (`Authorization: Token`; checked November 2026): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/api/tokens/authentications.py#L21-L23
- Appsmith v2.4.1 server properties (bind address, signup): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties
- Appsmith v2.4.1 first super user: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java
- Appsmith v2.4.1 `SIGNUP_DISABLED` error: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/exceptions/AppsmithError.java
- Appsmith v2.4.1 image entrypoint (generated encryption values): https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh
- Appsmith v2.4.1 development Compose file: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml
- Appsmith v2.4.1 AWS Compose example: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/aws_ami/docker-compose.yml
- Appsmith v2.4.1 login rate limit filter (per-username key, redirect when spent; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/filters/LoginRateLimitFilter.java
- Appsmith v2.4.1 login bucket (5 attempts a day; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/ratelimiting/RateLimitConfig.java#L40
- Appsmith v2.4.1 login rate limit wiring (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L322
- Appsmith v2.4.1 login URL (`/api/v1/login`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/UrlCE.java#L6-L9
- Appsmith v2.4.1 form-login matcher and CSRF wiring (POST to `/api/v1/login`, form-encoded only; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L329-L338 and https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L255
- Appsmith v2.4.1 CSRF exemptions (JSON, `X-Appsmith-Version`, `X-Requested-By: Appsmith`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/ce/CsrfConfigCE.java#L44-L54 and https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/ce/CsrfConfigCE.java#L81-L106
- Appsmith v2.4.1 login field names (`username`, `password`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/FieldNameCE.java#L5 and https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/FieldNameCE.java#L135
- Appsmith v2.4.1 login failure redirect (`/user/login?error=true`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/helpers/AuthenticationFailureRetryHandlerCEImpl.java#L30-L60 and https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/helpers/AuthenticationFailureRetryHandlerCEImpl.java#L106
- Appsmith v2.4.1 login success redirect (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/handlers/ce/AuthenticationSuccessHandlerCE.java#L124-L136 and https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/handlers/ce/AuthenticationSuccessHandlerCE.java#L186-L235
- Appsmith v2.4.1 restricted-host filter coverage (WebClient-based plugins, Elasticsearch, Redis connections and the SMTP test email; not JDBC, Mongo, ArangoDB or SMTP send; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L21-L39
- Appsmith v2.4.1 blocked hosts (nine cloud-metadata hosts, `127.0.0.1` and `::1`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L152-L177
- Appsmith v2.4.1 blocked address classes (loopback, any-local, link-local, multicast, `fc00::/7` and IPv6 forms carrying an IPv4 address in those classes; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L705-L740
- Appsmith v2.4.1 IPv4-in-IPv6 normalization (mapped, compatible, translated, NAT64 and 6to4 forms reduced to IPv4 before the host check; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L783-L835
- Appsmith v2.4.1 connection-time check of resolved addresses (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L671-L695
- Appsmith v2.4.1 private IPv4 addresses allowed for datasources (RFC 1918; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L105-L108
- Appsmith v2.4.1 private IPv4 ranges allowed for mail servers (`10/8`, `172.16/12`, `192.168/16`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L401-L402
- Appsmith v2.4.1 internal Redis hosts refused for datasources (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L91-L93
- Appsmith v2.4.1 instance's own address refused for datasources (best effort; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L109-L117
- Appsmith v2.4.1 SSRF filter opt-out (`APPSMITH_DISABLE_SSRF_FILTER`, default on; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L53-L58
- Appsmith v2.4.1 SSRF filter switch (`APPSMITH_DISABLE_SSRF_FILTER` or `appsmith.test.bypass.ssrf` set to `true`, in any letter case; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L179-L182
- Appsmith v2.4.1 test JVM switch (`appsmith.test.bypass.ssrf` system property; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L60-L62
- Appsmith v2.4.1 disabled filter skips every check (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L67-L69
- Appsmith v2.4.1 blocked-host constant (`DISALLOWED_HOSTS`, not an environment variable; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L80
- Appsmith v2.4.1 public application view (read on the application; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L567-L600
- Appsmith v2.4.1 public application inherited policies (pages, queries, JS objects and theme; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L681-L713
- Appsmith v2.4.1 permission graph (read on pages and themes, execute on queries; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/acl/ce/PolicyGeneratorCE.java#L220-L244
- Appsmith v2.4.1 public application datasource grant (execute on the datasources its queries use, apart from those used by other applications in the same workspace that the same public role can read; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L602-L679
- Appsmith v2.4.1 routes open without a login (query execute included; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L285-L316
- Appsmith v2.4.1 anonymous callers forced to view mode (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L555-L566
- Appsmith v2.4.1 anonymous callers limited to published queries (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L963-L972
- Appsmith v2.4.1 query execution datasource lookup (saved configuration; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L686-L695
- Appsmith v2.4.1 datasource storage lookup for execution (stored configuration; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/datasourcestorages/base/DatasourceStorageServiceCEImpl.java#L116-L127
- Appsmith v2.4.1 MCP token URL (`/api/v1/users/mcp-tokens`; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/UrlCE.java#L37
- Appsmith v2.4.1 MCP token controller (create, rotate, list and revoke from a signed-in session only; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/controllers/ce/McpTokenControllerCE.java#L29-L85
- Appsmith v2.4.1 MCP token lifetimes (30, 60, 90, 180 or 365 days; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L45-L46
- Appsmith v2.4.1 MCP token per-user limit (2 live on the Community Edition; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L73-L76
- Appsmith v2.4.1 MCP token hash and expiry (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L318-L320
- Appsmith v2.4.1 MCP token record (token hash only; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/domains/McpToken.java#L26-L27
- Appsmith v2.4.1 MCP bearer check (internal-secret header, named in a code comment and log message; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/converters/McpTokenAuthenticationConverter.java#L35-L79
- Appsmith v2.4.1 MCP token sign-in (the owner as principal; checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/managers/McpTokenAuthenticationManager.java#L56-L72
- Appsmith v2.4.1 MCP endpoint allowlist (checked November 2026): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/filters/McpAllowlistWebFilter.java#L43-L90
- Appsmith authentication documentation (sign-in methods; rolling documentation, checked November 2026): https://docs.appsmith.com/getting-started/setup/instance-configuration/authentication
- Budibase v3.46.0 sample environment: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env
- Budibase v3.50.0 Compose file: https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml
- Budibase v3.50.0 proxy configuration (`/db/`): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf
- Budibase v3.50.0 public worker routes: https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts
- Budibase v3.50.0 admin init: https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/controllers/global/users.ts
- Budibase v3.50.0 admin init route and its validation: https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts
- Budibase v3.46.0 sample secret assignments (checked October 2026): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env#L4-L16
- Budibase v3.50.0 CouchDB image and credential mapping (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L111-L120
- Budibase v3.50.0 LiteLLM image and environment (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L129-L144
- Budibase v3.50.0 CouchDB upstream variable (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf#L86
- Budibase v3.50.0 CouchDB proxy location (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf#L240-L243
- Budibase v3.50.0 public init endpoint entry (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts#L40-L43
- Budibase v3.50.0 public authentication middleware chain (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts#L133-L167
- Budibase v3.50.0 admin-init body validator (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts#L13-L28
- Budibase v3.50.0 admin-init middleware order (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts#L92-L96
- Budibase v3.50.0 admin-init controller and refusal (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/controllers/global/users.ts#L231-L289
- Budibase v3.50.0 startup admin seeding conditions (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/startup/index.ts#L226-L266
- Budibase v3.50.0 admin environment definitions (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/environment.ts#L267-L268
- Budibase v3.50.0 app-service admin environment mapping (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L27-L28
- Budibase v3.50.0 CouchDB entrypoint installation (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/Dockerfile#L89-L91
- Budibase v3.50.0 CouchDB runner command (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/Dockerfile#L151-L154
- Budibase v3.50.0 database image version file (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/VERSION#L1
- Budibase v3.50.0 runner calls CouchDB entrypoint (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/runner.sh#L165-L166
- Budibase v3.50.0 conditional CouchDB admin creation (checked October 2026): https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/docker-entrypoint.sh#L70-L75
- Budibase v3.46.0 hosting sample secrets (checked October 2026): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/hosting.properties#L4-L18
- Budibase v3.46.0 first-boot sample substitution (checked October 2026): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/digitalocean/files/var/lib/cloud/scripts/per-instance/001_onboot#L11-L15
- Budibase v3.46.0 test secret assignments (checked October 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/tests/jestEnv.ts#L9-L10
- Budibase v3.46.0 development secret entries (checked October 2026): https://github.com/Budibase/budibase/blob/v3.46.0/scripts/dev/manage.js#L11-L12
- Budibase v3.46.0 email lockout (checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/middleware/emailLockout.ts
- Budibase v3.46.0 address lockout (checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/middleware/ipLockout.ts
- Budibase v3.46.0 login route and its lockouts (checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L33-L36
- Budibase v3.46.0 lockout defaults (checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/environment.ts#L91-L95
- Budibase v3.46.0 login body validator and middleware order (only `username` and `password`, validated before both lockouts; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L7-L13 and https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L32-L38
- Budibase v3.46.0 login controller (failures counted per submitted username, 403 answers, lock at the limit; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L55-L71, https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L78-L93 and https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L111-L140
- Budibase v3.50.0 blacklist defaults (twelve ranges, `2001::/32` and `64:ff9b:1::/48` included; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L7-L20
- Budibase v3.50.0 blacklist replacement (self-hosted `BLACKLIST_IPS` replaces the defaults, an empty value disables them; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L27-L30
- Budibase v3.50.0 blacklist build (defaults only when not replaced, then `BLACKLIST_IPS` entries; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L134-L162
- Budibase v3.50.0 blacklist check (embedded IPv4 addresses checked too; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L164-L187
- Budibase v3.50.0 REST request (`fetchWithBlacklist`; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/integrations/rest.ts#L966
- Budibase v3.50.0 `fetchWithBlacklist` definition (checks every resolved address against the blacklist before each request and redirect hop; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/utils/outboundFetch.ts#L39-L53 and https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/utils/outboundFetch.ts#L172-L252
- Budibase v3.50.0 outgoing webhook step (imports `fetchWithBlacklist` from the steps `utils` and calls it; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/outgoingWebhook.ts#L1 and https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/outgoingWebhook.ts#L68
- Budibase v3.50.0 automation steps utils (`fetchWithBlacklist` calls the backend-core function; checked November 2026): https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/utils.ts#L28-L35
- Budibase v3.46.0 IMAP host check (email trigger; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/automations/email/utils/getClient.ts#L105-L107
- Budibase v3.46.0 PUBLIC role ("Accessible to anyone"; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/src/security/roles.ts#L172-L181
- Budibase v3.46.0 webhook trigger route ("right now its always public"; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/api/routes/webhook.ts#L16-L17
- Budibase v3.46.0 public route group (no middleware; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/api/routes/endpointGroups/standard.ts#L24-L25
- Budibase v3.46.0 API key routes (generate and fetch, builder routes; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/self.ts#L4-L6
- Budibase v3.46.0 builder route group (`auth.builderOnly`; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/endpointGroups/standard.ts#L11
- Budibase v3.46.0 API key generation (one key per user, regenerating replaces it; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/self.ts#L44-L68
- Budibase v3.46.0 API key check (a valid key resolves to its user; checked November 2026): https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/src/middleware/authenticated.ts#L72-L97
- Apache CouchDB 3.5.2 `/_session` reference: https://github.com/apache/couchdb/blob/3.5.2/src/docs/src/api/server/authn.rst
- LiteLLM authentication source: non-`sk-` keys rejected with 401 when a database is connected; 400 without one (checked October 2026): https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/user_api_key_auth.py
- Windmill v1.864.1 README (default credentials): https://github.com/windmill-labs/windmill/blob/v1.864.1/README.md
- Windmill v1.864.1 server defaults: https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/src/main.rs
- Windmill v1.864.1 worker (`DISABLE_NSJAIL`): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs
- Windmill v1.864.1 Compose file: https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml
- Windmill v1.864.1 worker sandbox check (`is_sandboxing_enabled`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1084-L1086
- Windmill v1.864.1 Dockerfile (`nsjail` binary copied into the image; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/Dockerfile#L360
- Windmill v1.864.1 threat model (outbound network from user code unrestricted by default; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/THREAT_MODEL.md#L140
- Windmill v1.864.1 Compose Postgres password (`POSTGRES_PASSWORD: changeme`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L36
- Windmill v1.864.1 Compose `DATABASE_URL` passed to the server (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L55
- Windmill v1.864.1 Compose worker volumes (no host Docker socket by default; the `/var/run/docker.sock` mount is commented out for the legacy `# docker` mode; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L90-L99
- Windmill v1.864.1 sample `.env` (`DATABASE_URL` with `changeme` and `sslmode=disable`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/.env#L1
- Windmill v1.864.1 `SECRET_SALT` read from the environment (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L26
- Windmill v1.864.1 workspace cipher cache, key log line and salt (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L336-L357
- Windmill v1.864.1 workspace key query (`workspace_key` table; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L388-L396
- Windmill v1.864.1 debugger signed-request switch (signing is off only when `REQUIRE_SIGNED_DEBUG_REQUESTS` is exactly `false`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/debugger/dap_debug_service.ts#L157 and https://github.com/windmill-labs/windmill/blob/v1.864.1/debugger/dap_websocket_server_bun.ts#L226
- Windmill v1.864.1 seeded-user migrations: https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/migrations/20220123221903_first.up.sql and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/migrations/20220816185849_remove_non_admin_users.up.sql
- Windmill v1.864.1 login rate limit (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs
- Windmill v1.864.1 login route and login handler (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs
- Windmill v1.864.1 API route nesting (`/api`, `/auth`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L675-L677 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L1079-L1082
- Windmill v1.864.1 login body, wrong-password answer and login-link check (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L170, https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L174, https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L338-L341, https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L2886, https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L2924 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L3842
- Windmill v1.864.1 per-minute counter (wall-clock minute, reset when the minute changes; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/per_minute_counter.rs#L14 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/per_minute_counter.rs#L56-L88
- Windmill v1.864.1 login limits' 429 and global minute (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs#L82-L86 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs#L119-L136
- Windmill v1.864.1 worker test jail (a worker that cannot jail logs "Nsjail sandboxing will NOT be available" and jobs that require nsjail fail, and the same line for other causes; checked November 2026). Sources for this item (1 of 2): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L568-L584. Sources for this item (2 of 2): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L586-L607
- Windmill v1.864.1 worker no-network check (`no_network` annotation refused without a jail; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1094-L1122
- Windmill v1.864.1 app execution modes (four modes, `publisher` when none is named; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L301-L319
- Windmill v1.864.1 app deployment rules (`RestrictAnonymousAppDeployment`, `RestrictGuestAppDeployment`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L333-L342
- Windmill v1.864.1 app redeploy gate (the rules gate only a switch into `anonymous` or `guest`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4129-L4138
- Windmill v1.864.1 app access check (anonymous admits anyone, guest anyone signed in; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L381-L410
- Windmill v1.864.1 app run identity (publisher's permissions except in viewer mode; the publisher is the policy's `on_behalf_of`; checked November 2026). Sources for this item (1 of 3): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4421-L4456 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L6540-L6556. Sources for this item (2 of 3): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2862-L2885 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3858-L3874. Sources for this item (3 of 3): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3853-L3855 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4036-L4047
- Windmill v1.864.1 app public link (app id encrypted under the workspace cipher; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2200-L2216
- Windmill v1.864.1 app public link check (the mode still decides access; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L1444-L1487
- Windmill v1.864.1 protection rule check (admins always pass; blocks only where a ruleset enables the rule; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/workspaces.rs#L1442-L1475
- Windmill v1.864.1 anonymous app deployment test (any writer by default; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/tests/app_anonymous_execution_mode.rs#L3-L10
- Windmill v1.864.1 HTTP route mount (`/api` prefix and `/r` mount; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L675-L676 and https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L1110-L1115
- Windmill v1.864.1 HTTP route authentication methods (six; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger-http/src/lib.rs#L104-L114
- Windmill v1.864.1 HTTP route method check (secrets checked only for `api_key`, `basic_http` and `signature`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L541-L601
- Windmill v1.864.1 HTTP route Windmill token check (checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L408-L470
- Windmill v1.864.1 HTTP route run identity (`permissioned_as`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L475-L488
- Windmill v1.864.1 trigger identity rule (the saving user unless an earlier identity is kept; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger/src/types.rs#L214-L223
- Windmill v1.864.1 token sources (Bearer header, session cookie, `?token=`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L941-L971
- Windmill v1.864.1 unscoped token rule (full rights of its user; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/lib.rs#L453-L457
- Windmill v1.864.1 token expiry ceiling (no expiry unless set; service accounts exempt; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L3218-L3273
- Windmill v1.864.1 token ceiling setting (`max_token_expiration_days`, token create and impersonate routes only, empty for no limit; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/global_settings.rs#L119-L157
- Windmill v1.864.1 static admin token (`SUPERADMIN_SECRET`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L788-L812
- Windmill v1.864.1 `SUPERADMIN_SECRET` server default (`None`; checked November 2026): https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/src/main.rs#L469
- nginx limit_req module documentation (`limit_req_status`, default 503; rolling documentation, checked November 2026): https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- fail2ban 1.1.1 client exit status and output streams (answers printed to standard output, errors logged to standard error, 0 on success and 255 otherwise; checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L85-L133, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L447-L458, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L510-L516, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2bancmdline.py#L35-L40 and https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2bancmdline.py#L219-L227
- fail2ban 1.1.1 client socket errors (server not running, permission denied; checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L135-L157
- fail2ban 1.1.1 jail status format (a tab after each field name, Banned IP list last; checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/beautifier.py#L80-L112, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/transmitter.py#L513-L522, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/server.py#L628-L629, https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/jail.py#L186-L197 and https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/actions.py#L721-L746
- fail2ban 1.1.1 missing-jail message and failed-command answer (checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/beautifier.py#L263-L272 and https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/transmitter.py#L54-L65
- fail2ban 1.1.1 ignore rules, failure counting and the maxretry ban (checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/filter.py#L593-L607 and https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/filter.py#L718-L738
- fail2ban 1.1.1 ban recorded before its actions run, action failures only logged (checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/actions.py#L502-L520
- fail2ban 1.1.1 client commands `status JAIL`, `stop JAIL` (jail removed) and `set JAIL unbanip` (checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/man/fail2ban-client.1#L214-L223, https://github.com/fail2ban/fail2ban/blob/1.1.1/man/fail2ban-client.1#L310-L311 and https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/protocol.py#L109
- fail2ban 1.1.1 `get JAIL maxretry` (checked November 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/protocol.py#L141
- sudo SUDO_1_9_16p2 sudo manual, exit value (checked November 2026): https://github.com/sudo-project/sudo/blob/SUDO_1_9_16p2/docs/sudo.man.in#L1168-L1173


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- nocodb: NocoDB (2026.09.0)
- baserow: Baserow (2.3.4)
- appsmith: Appsmith (v2.4.1)
- budibase: Budibase (v3.50.0)
- budibase-prev: Budibase (v3.46.0)
- windmill: Windmill (v1.864.1)
- nocodb-docs: NocoDB docs (unknown)
- appsmith-docs: Appsmith docs (unknown)
- docker: Docker docs (unknown)
- docker-new: Docker CLI (v27.2.0)
- docker-old: Docker CLI (v27.1.2)
- node: Node.js (v22.22.1)
- couchdb: CouchDB (3.5.2)
- litellm: LiteLLM authentication source (6ef7b86748118ceecd95271727c2fa167ce55fec)
- nginx-docs: nginx docs (unknown)
- fail2ban: fail2ban (1.1.1)
- cors: expressjs/cors (v2.8.5)
- curl: curl (curl-8_14_1)
- caddy-docs: Caddy docs (unknown)

Claims (full source mapping in the JSON block below):

- private (REASONED; nocodb, baserow, appsmith, budibase, windmill): Keep builders private with fronting auth, claim admin early and protect databases storing connected-system credentials.
- nocodb-bind (REASONED; nocodb, node): PORT defaults 8080; listen omits host, so Node binds unspecified IPv6/IPv4. No application bind setting; restrict publication/firewall.
- nocodb-first (REASONED; nocodb): First signup becomes super-admin; claim first or seed NC_ADMIN_EMAIL/NC_ADMIN_PASSWORD.
- nocodb-signup (REASONED; nocodb): invite_only_signup defaults false; enable to stop later self-signups.
- nocodb-encryption (REASONED; nocodb): Unset NC_CONNECTION_ENCRYPT_KEY stores external DB credentials unchanged; set before adding sources, or startup encrypts existing sources when added later.
- nocodb-jwt (REASONED; nocodb): Unset NC_AUTH_JWT_SECRET generates/stores a UUID as nc_auth_jwt_secret; replace README sample 569a1821-0a93-45e8-87ab-eb857f20a010.
- nocodb-cors (REASONED; nocodb, cors): At 2026.09.0, rspack.timely.config.js builds docker/main.js, which docker/start.sh runs, from timely.ts; it and dockerEntry.ts call cors() with no options, and cors 2.8.5, the lockfile's only cors, then sends Access-Control-Allow-Origin: * on every response and preflight passing through it, with no Allow-Credentials. No Dockerfile at the tag, so the image's script is unverified.
- nocodb-cors-risk (REASONED; nocodb, cors): Auth is the xc-auth header or the nc_token cookie (httpOnly, SameSite=Lax, path /api), or an xc-token or Bearer API token. With * and no Allow-Credentials, browsers expose no credentialed response cross-origin; the residual risk is pages on other sites reading, through a visitor's browser, responses that need no credentials (guide inference).
- nocodb-cors-proxy (REASONED; nginx-docs, caddy-docs): Remove the header at the proxy: nginx proxy_hide_header in every location proxying to NocoDB, or Caddy reverse_proxy header_down -Access-Control-Allow-Origin. For one exact origin, nginx also adds it with add_header (repeat inherited add_header lines such as HSTS there) and Caddy sets it with header_down (guide advice).
- nocodb-proxy (REASONED; nocodb): Startup resets trust proxy from NC_TRUST_PROXY, default no trust; restrict hops/subnets, never true with direct client access.
- nocodb-packaging (REASONED; nocodb): README marks binaries for quick local testing and documents Docker image and Auto-upstall paths; the October 2026 release API record lists no assets; the 2026.09.0 tag carries package version 0.301.3. Use the image or vendor install script for production (guide advice).
- nocodb-upstall-fetch (REASONED; nocodb): The README's Auto-upstall command fetches the script over plain HTTP and executes it with Bash; its source link points to develop. Fetch over HTTPS from a pinned, reviewed source and read before running (guide advice).
- nocodb-webhook-ssrf (REASONED; nocodb): At 2026.09.0, self-hosted NocoDB filters webhooks with request-filtering-agent; a throw-on-failure invocation reports a refused private address, with an NC_ALLOW_LOCAL_HOOKS=true hint only if !isEE &#124;&#124; isOnPrem. NC_ALLOW_LOCAL_HOOKS, NC_WEBHOOK_ALLOW_PRIVATE_NETWORK or NC_DISABLE_SSRF_PROTECTION set to exactly true disables it; leave them unset and filter egress at the network (guide advice).
- nocodb-ssrf-sources (REASONED; nocodb): The same switch turns SSRF protection off for external-database sources when NC_ALLOW_LOCAL_EXTERNAL_DBS is true and for data imports when NC_ALLOW_LOCAL_DATA_IMPORT is true; where those sources apply it was not traced. Cloud ignores all five variables. Leave both unset (guide advice).
- nocodb-share (REASONED; nocodb): Shared-view row routes take the view's optional password in an xc-password header, so a view shared without one is readable by link holders (guide reading); a base's shared link is removed by disableSharedBaseLink. A source search found no env var that turns sharing off instance-wide; review shares before exposure (guide advice).
- nocodb-token (REASONED; nocodb): API tokens in xc-token, or Authorization: Bearer as fallback, skip the sign-in route and act with the creating user's roles; a token with a base_id is refused for other bases on requests that resolve a base, and an old token with no user gets the editor role. Fronting MFA covers tokens only if the proxy also gates /api (guide reading). Expiry enforcement was not traced.
- baserow-bind (REASONED; baserow): Caddy publishes 80/443 on HOST_PUBLISH_IP default 0.0.0.0; set it or publish loopback. Docker wildcard publication bypasses UFW.
- baserow-first (REASONED; baserow): First signup becomes staff; claim before exposure.
- baserow-signup (REASONED; baserow): allow_new_signups defaults True; disable in admin settings, yielding Sign up is disabled.
- baserow-secrets (REASONED; baserow): Compose requires SECRET_KEY/DATABASE_PASSWORD/REDIS_PASSWORD; .env.example leaves them empty. Generate your own.
- baserow-mfa (REASONED; baserow): Core registers a TOTP provider.
- baserow-outbound-private (REASONED; baserow): Webhooks and integration requests go through advocate unless BASEROW_WEBHOOKS_ALLOW_PRIVATE_ADDRESS or BASEROW_INTEGRATIONS_ALLOW_PRIVATE_ADDRESS is on; both are read with bool(os.getenv(...)), so any non-empty value, false and 0 included, enables them. Leave both unset; for one internal webhook target, the docs point to the URL and IP lists instead.
- baserow-data-sync-private (REASONED; baserow): BASEROW_DATA_SYNC_ALLOW_PRIVATE_ADDRESS defaults to true, and while true data sync sends with plain requests instead of advocate, so a data sync URL can reach internal addresses by default (guide reading; not tested). Set it false; str_to_bool was not read, so confirm the refusal on a test instance, and filter egress at the network (guide advice).
- baserow-public-views (REASONED; baserow): A view's public flag (default false) makes it readable at a public URL, optionally behind public_view_password; review public views and password those that must stay public before exposure (guide advice).
- baserow-db-token (REASONED; baserow): Database tokens in an Authorization: Token header authenticate the row create, read, update and delete endpoints, with permissions on one table, one database or the whole workspace. They skip the login view, so fronting MFA covers them only if the proxy also gates the API paths (guide reading).
- appsmith-bind (REASONED; appsmith): Java defaults APPSMITH_SERVER_ADDRESS=127.0.0.1 and port 8080 inside the container.
- appsmith-publish (REASONED; appsmith): Bundled Caddy fronts port 80; development Compose publishes host 8080, AWS example 80/443.
- appsmith-first (REASONED; appsmith): First signup claims super-user while no users exist; claim before exposure.
- appsmith-signup (REASONED; appsmith): APPSMITH_SIGNUP_DISABLED defaults false; set true or restrict APPSMITH_SIGNUP_ALLOWED_DOMAINS. Refusal is SIGNUP_DISABLED.
- appsmith-encryption (REASONED; appsmith): Entrypoint generates 13-character encryption password/salt; external values override them. Development Compose sets both abcd; replace before first start.
- appsmith-rotation (REASONED; appsmith): Changing an existing abcd encryption pair presumably makes stored credentials unreadable; plan re-entry. Inferred, not tested.
- budibase-publish (REASONED; budibase, budibase-prev): Proxy publishes MAIN_PORT, sample 10000; LiteLLM publishes LITELLM_PORT default 4000.
- budibase-couchdb (REASONED; budibase, budibase-prev): Proxy /db/ reaches CouchDB. Compose maps COUCH_DB_USER/PASSWORD to COUCHDB_USER/PASSWORD; the image entrypoint adds that admin only when both are non-empty and its existing-admin check finds none for that name. With unchanged samples and that condition, anyone reaching the proxy can try budibase/budibase.
- budibase-secrets (REASONED; budibase, budibase-prev): Sample JWT_SECRET/API_ENCRYPTION_KEY are testsecret; service passwords, INTERNAL_API_KEY and LITELLM_MASTER_KEY are budibase. Replace all before first start. Compose pins docker.io/litellm/litellm:main-v1.83.10-stable.patch.3 and passes LITELLM_MASTER_KEY; acceptance of budibase by that image is not established.
- budibase-sample-check (REASONED; budibase-prev): This guide's October 2026 search of the full v3.46.0 tag with git grep -l testsecret v3.46.0 found exactly hosting/.env, hosting/digitalocean/files/var/lib/cloud/scripts/per-instance/001_onboot, hosting/hosting.properties, packages/backend-core/tests/jestEnv.ts and scripts/dev/manage.js. This guide inspected those hits.
- budibase-sample-safeguard (REASONED; budibase-prev): This guide's assessment is that the v3.46.0 testsecret search hits do not establish absence of production rejection; no live safeguard test ran.
- budibase-init (REASONED; budibase): POST /api/global/users/init is public; its body validator requires string email and tenantId fields, permits an optional password, rejects unknown fields and precedes adminUser. In the supplied tenant context, checkAnyUserExists() truthy causes 403 with the exact vendor error quoted in the body.
- budibase-init-probe (REASONED; budibase): The checkAnyUserExists() helper definition was not fetched, so which users count and any multi-tenancy exception remain unestablished. This guide assesses POST /api/global/users/init as unsafe for read-only claimed-state probing: invalid bodies can fail validation in both states, while accepted initialization creates an admin.
- budibase-seed (REASONED; budibase): Claim admin before exposure (guide advice), manually or with BB_ADMIN_USER_EMAIL/BB_ADMIN_USER_PASSWORD. Startup attempts seeding only with SELF_HOSTED truthy, MULTI_TENANCY falsy and both values non-empty; in tenancy.getTenantId() context, it calls createAdminUser when the admin checklist is not checked OR the email does not exist, with hashPassword/requirePassword/skipPasswordValidation true.
- windmill-code (REASONED; windmill): Workers execute user scripts; a login enables code execution on worker hosts.
- windmill-bind (REASONED; windmill): Default 0.0.0.0:8000; SERVER_BIND_ADDR changes binary binding. Default wildcard bind was not observed.
- windmill-compose (REASONED; windmill): Compose exposes server 8000 internally; Caddy publishes 80/25 on all host interfaces. Bind publications privately; container loopback cutting Caddy off is inferred.
- windmill-sandbox (REASONED; windmill): DISABLE_NSJAIL defaults true; sandboxing is not enabled by default.
- windmill-privileged (REASONED; windmill): Shipped worker uses privileged=true.
- windmill-smtp (REASONED; windmill): Port 25 serves email triggers; do not publish unless used.
- windmill-debugger (REASONED; windmill): Vendor warns REQUIRE_SIGNED_DEBUG_REQUESTS=false exposes an unauthenticated code-execution debugger on reachable deployments.
- windmill-sandbox-enable (REASONED; windmill): DISABLE_NSJAIL=false makes the worker's sandbox check return true before the instance isolation setting is read, and the v1.864.1 Dockerfile copies nsjail into the image. Whether nsjail works in the vendor Compose worker or needs privileged: true was not established; no run with nsjail enabled was made.
- windmill-egress (REASONED; windmill): The v1.864.1 threat model says network isolation is an nsjail feature and outbound network from user code is unrestricted by default; put workers on a network reaching only what scripts need and block the metadata address there (guide advice).
- windmill-db-secret (REASONED; windmill): The v1.864.1 Compose file sets POSTGRES_PASSWORD to changeme, and the sample .env sets DATABASE_URL with that password and sslmode=disable, which Compose passes to the server. Change the password before first start, keep the database off public networks and ask for TLS to a remote database (guide advice).
- windmill-workspace-key (REASONED; windmill): The workspace cipher key is read from the workspace_key table of the same database, with SECRET_SALT appended only when set; each fetch without a cipher cached in the last 300 s logs the key's first 8 characters at info level. Without SECRET_SALT a database copy holds the key (inference). Set SECRET_SALT before storing secrets and protect logs (guide advice).
- login-limit (REASONED; nocodb, baserow, appsmith, budibase-prev, windmill): Tool limits range from none (NocoDB, Baserow) through Windmill's global cap, with optional per-address and per-account limits, to Appsmith's per-username limit and Budibase's per-email and per-address lockouts, so rate-limit login endpoints per client address at the proxy, recovering it behind a CDN or second proxy, and add fail2ban filters per login path and status (guide advice).
- nocodb-login-limit (REASONED; nocodb): The sign-in route's PublicApiLimiterGuard always allows requests; its comment leaves rate limiting to the network layer. Sign-in is served on four paths ending in /auth/user/signin, so a proxy limit must cover all four. The local strategy answers bad credentials with a bad-request error.
- nocodb-mfa (REASONED; nocodb, nocodb-docs): Rolling vendor docs make two-factor authentication a Cloud or licensed self-hosted (Business plan and above) feature. The 2026.09.0 migration adds TOTP columns; this guide's search of packages/nocodb/src found no TOTP setup or verify endpoint, and whether the open build can enable it was not established. Front it with MFA (guide advice).
- baserow-totp-login (REASONED; baserow): The login view documents a temporary token for finishing verification on 2FA-protected accounts; whether TOTP can be required for every account was not established, so put MFA in front of Baserow (guide advice).
- baserow-login-limit (REASONED; baserow): The token-auth login view and its serializer (email or deprecated username, and password) have no throttle, failed-attempt counter or captcha; captcha is checked only on sign-up. Bad credentials get 401 ERROR_INVALID_CREDENTIALS. The optional throttle (default off) skips anonymous requests unless BASEROW_THROTTLE_IP_ENABLED, does not count failed logins and locks no account.
- appsmith-login-limit (REASONED; appsmith): Form login at /api/v1/login allows 5 attempts per submitted username per day, then redirects to /user/login?error=true instead of answering 429. Keyed per username, it lets one client try many usernames and anyone lock a known username out for up to a day. No setting for it was found.
- appsmith-mfa (REASONED; appsmith-docs): This guide's search of the v2.4.1 server and client sources found no native MFA. Rolling vendor docs list Google, GitHub, OIDC and SAML sign-in besides form login; edition availability was not established. Put MFA in an enforcing identity provider or fronting proxy (guide advice).
- appsmith-ssrf-filter (REASONED; appsmith): At v2.4.1 a restricted-host filter checks WebClient-based plugins (REST, GraphQL, SaaS), Elasticsearch, Redis connections and the SMTP test email, not JDBC, Mongo, ArangoDB or SMTP sends. It refuses nine metadata hosts, loopback, any-local, link-local, multicast and fc00::/7, also after DNS resolution, and allows most private IPv4 (RFC 1918); filter egress at the network too (guide advice).
- appsmith-ssrf-optout (REASONED; appsmith): APPSMITH_DISABLE_SSRF_FILTER set to true, in any letter case, skips every filter check at once. The blocked list is a constant in the code, and this guide found no environment variable that extends or replaces it. Leave the opt-out unset (guide advice).
- appsmith-make-public (REASONED; appsmith): Make public gives anonymous visitors read on the app, its pages and theme, execute on its queries, and execute on their datasources unless used by other apps in the workspace the public role can read, needing no datasource permission. Anonymous callers run only published queries, with the saved datasource credentials (guide reading). Whether responses reveal credentials was not established.
- appsmith-mcp-token (REASONED; appsmith): No personal access token was found; MCP tokens are the only user bearer credential. They are managed from a signed-in session only, last 30 to 365 days, are stored hashed, number at most 2 live per user on CE, need the configured internal secret in a header, and act as their owner on an endpoint allowlist. Revoke unused tokens (guide advice).
- budibase-login-limit (REASONED; budibase-prev): At v3.46.0, the login validator accepts only username and password and rejects other fields before the lockouts. Login locks an email for 900 s after 5 failures (403, Retry-After) and answers 429 once one ctx.ip exceeds 10 validated login requests in that window. Anyone knowing an email can lock that user out; ctx.ip behind the bundled proxy was not verified.
- budibase-mfa (REASONED; budibase-prev): This guide's search of v3.46.0 packages and a v3.50.0 source tree found no native MFA; put MFA in a fronting proxy or in the identity provider users sign in through (guide advice).
- budibase-blacklist (REASONED; budibase): At v3.50.0 the outbound blacklist defaults to loopback, RFC 1918, CGNAT, link-local, 0.0.0.0/8, ::1, 2001::/32, 64:ff9b:1::/48, fc00::/7 and fe80::/10, and checks embedded IPv4. With SELF_HOSTED on, any BLACKLIST_IPS value, empty included, replaces the defaults. Leave it unset, or list every default range with your own entries, and filter egress at the network (guide advice).
- budibase-blacklist-scope (REASONED; budibase, budibase-prev): At v3.50.0 REST datasource requests and the outgoing-webhook step call fetchWithBlacklist, which checks each resolved address against the blacklist before each request; at v3.46.0 the IMAP trigger host check uses it too, and that file was not read at v3.50.0. SMTP, database datasources and file or URL imports were not traced, so the blacklist is not treated as covering all outbound traffic.
- budibase-public (REASONED; budibase-prev): At v3.46.0 the PUBLIC role is described as Accessible to anyone, and POST /api/webhooks/trigger/:instance/:id sits on the no-middleware route group, commented always public; the trigger controller was not traced. Review what PUBLIC can reach and treat each trigger URL as a public endpoint callable without a secret (guide advice).
- budibase-api-key (REASONED; budibase-prev): At v3.46.0 each user has at most one API key, generated or fetched only through builder routes, and regenerating replaces it. A valid key resolves to its user, so it carries that user's full rights (guide reading); the code read shows no scope or expiry. Key requests skip the login route, so fronting MFA covers them only if the proxy gates the API paths (guide reading).
- windmill-login-limit (REASONED; windmill): /api/auth/login has an always-on global cap (default 10000/min per process); per-IP (120) and per-account (30 failures) limits apply only with CLOUD_HOSTED or when set. All count per clock minute; global and per-IP also guard login links. Per-IP trusts X-Real-IP (else X-Forwarded-For), so the proxy must overwrite it. A wrong password gets 400; only these limits answer 429.
- windmill-mfa (REASONED; windmill): This guide's search of v1.864.1 backend and frontend sources found no native MFA; put MFA in a fronting proxy or in the identity provider users sign in through (guide advice).
- windmill-nsjail-unavailable (REASONED; windmill): With DISABLE_NSJAIL=false, a worker that cannot run a test jail, or cannot find or start nsjail, logs an error that nsjail sandboxing will not be available, and jobs that require nsjail fail rather than run unsandboxed. A no_network annotation removes a script's network only under nsjail, and without a jail the script is refused; it is a per-script opt-in, not an egress control (guide reading).
- windmill-public-apps (REASONED; windmill): Apps have four execution modes; the default, publisher, needs a login. Anonymous admits anyone, guest anyone signed in; both run the app's scripts as the publisher. Any writer can make an app anonymous unless a ruleset enables RestrictAnonymousAppDeployment, which gates only creating it or switching to it; enable it and the guest rule, and review apps already anonymous or guest (guide advice).
- windmill-app-link (REASONED; windmill): An app's public link is its id encrypted under the workspace cipher, and it opens the app only for callers the app's mode admits. The code read adds no random part or expiry, so the link stays the same while the app and the workspace key do (guide reading); withdraw a public app by changing its mode (guide advice).
- windmill-http-routes (REASONED; windmill): HTTP routes at /api/r have six authentication methods; the handler checks a secret only for api_key, basic_http and signature, windmill needs a token that can read the route, and none checks nothing. Every route runs as its permissioned_as user, so a none route lets anyone run its script with that user's rights (guide reading). Keep privileged scripts off none routes (guide advice).
- windmill-tokens (REASONED; windmill): Tokens come from a Bearer header, the session cookie or ?token=; an unscoped one has its user's full rights. A token from the create or impersonate route has no expiry unless its creator or max_token_expiration_days sets one; service-account and server-minted tokens are outside that cap. Scope and expire tokens, avoid ?token= URLs, and require proxy login on API paths for MFA (guide advice).
- windmill-docker-socket (REASONED; windmill): At v1.864.1 the Compose worker does not mount the host Docker socket; its docker.sock line is commented out for the legacy full-compat # docker mode, which the file warns grants user scripts full access to the host Docker daemon. Leave it unmounted; if that mode is required, treat every user who can write or deploy a script as having root on the host (guide advice).
- windmill-superadmin-secret (REASONED; windmill): SUPERADMIN_SECRET is unset by default; when set, a request presenting its value as a token acts as an admin with no scopes and no expiry, a token the server calls a virtual superadmin token. Leave it unset, or keep it in a secret store and rotate it like a root password (guide advice).
- fail2ban-filter-status (REASONED; nocodb, baserow, appsmith, budibase-prev, windmill): Failed logins get a bad-request error from NocoDB, 401 from Baserow, 403 from Budibase and 400 from Windmill, which a fail2ban filter can match with the login path. Appsmith answers failed and successful form logins alike with a redirect, so a status-only filter cannot separate them; this guide gives no Appsmith filter.
- verify-login-limit (REASONED; nocodb, baserow, appsmith, budibase-prev, windmill, nginx-docs): Via the proxy, send failed logins for no-such-user@example.invalid in each tool's format (JSON; Appsmith form-encoded with X-Requested-By): exposed, every attempt gets the app's answer (exit 1); fixed, the limit status follows an app answer (exit 0; 3 if 502, 503 or 504). Sequential attempts can miss a fast-refilling limit. Never use a real account. Not run against any deployment.
- verify-fail2ban (REASONED; fail2ban): On the fail2ban host, after failed logins above the jail's maxretry from a test address, fail2ban-client status JAIL: exposed, no such jail or the address absent from its Banned IP list (exit 1); fixed, the address listed (exit 0); unrecognized output is inconclusive (3). A listed ban is fail2ban's record, not proof its action blocked the address. Not run against any deployment.
- verify-nocodb-signup (REASONED; nocodb): Controlled signup creation is exposed; invite-only refusal is fixed. Hidden links prove nothing; inspect backend setting and confirm admin login.
- verify-baserow-signup (REASONED; baserow): Controlled signup creation is exposed; Sign up is disabled is fixed. Inspect allow_new_signups and confirm admin login.
- verify-appsmith-signup (REASONED; appsmith): Controlled signup creation is exposed; SIGNUP_DISABLED is fixed. Inspect backend settings, confirm admin login and delete test accounts.
- verify-external (REASONED; baserow, budibase, windmill): Probe each public IP; control proves only its port, refusal/timeout may be local filtering, and unexpected connections need host confirmation.
- windmill-default-login (REASONED; windmill): Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1), with an earlier block form whose result was curl's own exit status: a fresh DB had only admin@windmill.dev as a password user/super-admin; changeme returned 200/token, then 400 after rotation while the new password returned 200. Not re-run on v1.864.1 or the current form.
- windmill-loopback (REASONED; windmill): Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1): with SERVER_BIND_ADDR=127.0.0.1 the release binary had only a loopback listener on the test port. Only that configured state was observed; the default wildcard bind was not run, as the host forbids it. Not re-run on v1.864.1.
- windmill-sandbox-run (REASONED; windmill): Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1): a worker without nsjail logged that nsjail sandboxing will not be available. No run with nsjail enabled was made, so isolation was not observed. Not re-run on v1.864.1.
- verify-inventory (REASONED; docker, baserow, appsmith, budibase, windmill): Inventory host sockets and Docker publications; NAT may have no socket, so absent ss entries do not establish isolation.
- verify-port-display (REASONED; docker, docker-new, docker-old): IPv6 wildcard displays [::]: from v27.2.0 versus ::: through v27.1.2; both mean all host addresses unless filtered.
- verify-sample-tokens (DEMONSTRATED; nocodb, appsmith, budibase-prev, windmill): The current form exited 1 on the pinned Budibase v3.46.0, Appsmith v2.4.1, Windmill v1.864.1 and NocoDB 2026.09.0 files, printing their sample-token lines, and 0 reporting none on token-replaced copies; its guard, failed-read and unclassified-observation (hit only outside value position) arms, unreached there, exited 2, 3 and 0 locally. Harmless matches and external environment values limit scope.
- verify-nocodb-key (REASONED; nocodb, docker): docker exec tests configured key presence without printing it or passing its value in argv; no real container run. Startup selection/process value remain unverified.
- nocodb-key-limits (REASONED; nocodb, docker): Trusted shells/startup assumed; environment remains readable to same-account/root or Docker-socket holders. Presence does not prove encryption; do not inject a replacement key.
- nocodb-key-logic (REASONED; docker): Recorded runs of an earlier form, whose result arms ended with status 0, exercised set/empty/unset/missing-container branches with a docker exec stand-in only; no NocoDB deployment demonstrated. The current form was not re-run.
- verify-windmill-control (REASONED; windmill): Before trusting default-login 400, confirm real credentials work so a dead service is not treated as fixed.
- verify-couchdb (REASONED; budibase, budibase-prev, couchdb): Sample login at /db/_session?basic=true should return 200 exposed and 401 after replacement; real credentials are the positive control.
- verify-litellm (REASONED; budibase, budibase-prev, litellm): Sample Bearer budibase at /v1/models should return 200 exposed; fixed, a 401 (or a 400 if the proxy has no database); confirm real credentials. The pinned authentication source rejects non-`sk-` keys with 401 when a database is connected and returns 400 without one; the exposed 200 still requires live comparison.
- verify-litellm-pin (REASONED; budibase, litellm): The LiteLLM outcomes remain comparison expectations: this guide has not established that litellm.md's source pin corresponds to Compose image docker.io/litellm/litellm:main-v1.83.10-stable.patch.3; no source for that image was fetched.
- verify-tcp-outcomes (REASONED; baserow, budibase, windmill): Recorded loopback runs of an earlier form, whose control and result arms ended with status 0, observed connected/open, timeout/full accept queue, refused/closed and failed-control stopping; no real firewall demonstrated. The current form was not re-run.
- verify-tcp-inputs (REASONED; baserow, budibase, windmill): Recorded guard tests of an earlier form, whose guard, control and result arms ended with status 0, rejected named hosts, malformed IPv4, zero/dotted IPv6, invalid ports and absent timeout; loopback/hex-mapped IPv6 passed, and the invalid hex values tested failed at the control. The current form was not re-run.
- verify-windmill-debugger (REASONED; windmill): File: NUL, UTF-16 BOM, lone CR, NEL, LS or PS exits 3; a line setting REQUIRE_SIGNED_DEBUG_REQUESTS to exactly false exits 1. A backslash, !, or $ line not a comment or plain K=${X} or K: ${X:-d}, or a $ with env_file, extends, include or project_directory anywhere in the file, exits 3, as does a naming line not true or 1; else 0. Loaded files and outside values go unread. Not run on a deployment.
- verify-nocodb-trust-proxy (REASONED; nocodb, docker): docker exec reads NC_TRUST_PROXY in the container's configured environment: true (any case) or a zero range such as /0 (proxy-addr 2.0.7 rejects it) is the finding (exit 1); unset, empty, false or all zeros exits 0 (no proxy trusted); anything else, such as a hop count or range, exits 3, expected behind a proxy, as the block cannot see if clients reach NocoDB directly. No real container run.
- verify-nocodb-cors (REASONED; nocodb, cors, curl): GET a NocoDB URL through the proxy with Origin: https://evil.example: Allow-Origin * or that origin in the final response's headers is the finding (exit 1), interim 1xx headers not judged; on a 2xx, no Allow-Origin or exactly the allowed origin once passes (0); anything else is inconclusive (3); a missing curl or awk or a refused value exits 2. Not run against a deployment.

````json
{
  "schema": 1,
  "checked": "2026-11-26",
  "documentation_checked": "2026-09",
  "body_sha256": "45f929022dcdb52f9516d3e3e814ebf25c9af611bef79bff414cde88bb45faa6",
  "components": {
    "nocodb": {
      "name": "NocoDB",
      "basis": "2026.09.0",
      "sources": {
        "sa19c6557b712": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts",
        "s635b35ce4689": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts",
        "sd74ca4df55b0": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts",
        "s5ea55dc5f0d9": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts",
        "sd0e9f451673f": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts",
        "s8a1de0bc97b0": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initAdminFromEnv.ts",
        "sca40040b40cc": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts",
        "saf056bb4ff37": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initDataSourceEncryption.ts",
        "sbfbf630008e1": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start.sh",
        "se5da9707c684": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start-litestream.sh",
        "s536899ecd4a5": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md",
        "sca0c9c0ecf24": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L56-L75",
        "sb4d5b659f7b8": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L77-L90",
        "s2769b9054778": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L82",
        "s2b16e2c93606": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L90",
        "s118384fa1d9f": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md#L95",
        "s9bee4adc612e": "https://api.github.com/repos/nocodb/nocodb/releases/tags/2026.09.0",
        "s3f296c702bc5": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/package.json#L3",
        "sdd5b3322fe9f": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/modules/auth/auth.controller.ts#L83-L86",
        "s31941e502c14": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/meta/migrations/v0/nc_202603180000_user_mfa.ts",
        "s50856563cb62": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/guards/public-api-limiter.guard.ts#L4-L13",
        "sbe0b751e6286": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/modules/auth/auth.controller.ts#L88",
        "s659b1179d0e5": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/local.strategy.ts#L18-L39",
        "se352e8e45038": "https://github.com/nocodb/nocodb/blob/2026.09.0/pnpm-lock.yaml",
        "s1174c56ebb50": "https://github.com/jshttp/proxy-addr/blob/v2.0.7/index.js",
        "s3af21c2530b7": "https://github.com/expressjs/express/blob/4.21.2/lib/utils.js",
        "sfa0f1d7f1be6": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/timely.ts",
        "sf6a63339341e": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/rspack.timely.config.js",
        "s512cac75f9fb": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/guards/global/global.guard.ts#L21",
        "s6af8fddcbdc7": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/helpers.ts#L34-L58",
        "se879dae3d563": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L17-L18",
        "s03a119ab46e6": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/utils.controller.ts#L179-L182",
        "s565f51c5c143": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/app.module.ts#L45-L48",
        "s52f6258ded32": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/middlewares/extract-ids/extract-ids.middleware.ts#L473-L479",
        "s7fc234b5a058": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/utils.service.ts#L131-L137",
        "s472d833bd66b": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L2-L6",
        "scc2c1474fe1a": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/ssrf.ts#L23-L49",
        "sa6b6a373e0ff": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L178",
        "sdbf149d571b4": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/webhook-invoker.ts#L738-L751",
        "s7db0b920da5a": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L21-L31",
        "s51ca09d692df": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/public-datas.controller.ts#L40",
        "s26c73fbba6b3": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/controllers/shared-bases.controller.ts#L75-L80",
        "s9b89db825243": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/apiHelpers.ts#L75-L94",
        "sfdb74b3b8564": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L29-L38",
        "s82a140cf2510": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L44-L46",
        "s1f0e06fcc373": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/strategies/authtoken.strategy/authtoken.strategy.ts#L50-L69",
        "sc6248503f82d": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/models/ApiToken.ts#L26-L28"
      }
    },
    "baserow": {
      "name": "Baserow",
      "basis": "2.3.4",
      "sources": {
        "s1b31314982f4": "https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml",
        "s3f61036aca03": "https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md",
        "s34b87f60dcc6": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py",
        "s4588448964a2": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py",
        "sd858f9ee45e0": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/apps.py",
        "s1a472d828699": "https://github.com/baserow/baserow/blob/2.3.4/.env.example",
        "s9de0cfbd461a": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/views.py",
        "s1973090f6cb9": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py",
        "s4d7f125ca2e6": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/serializers.py#L345-L389",
        "s2085d93a8d4e": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/serializers.py#L142-L185",
        "sbb08ecd2fe19": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/views.py#L322-L323",
        "s8f32b1811523": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/urls.py#L22",
        "s37f43ff193d5": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/urls.py#L46",
        "s40fedf30e4c8": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/urls.py#L33",
        "s36c52d0540aa": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/throttling/handler.py#L100-L140",
        "s522ee3d917aa": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/throttling/handler.py#L165-L190",
        "s2bb53845a946": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/exceptions.py#L47-L48",
        "s209db6950135": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/api/user/errors.py#L41-L45",
        "s577ac3bf7492": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1186-L1188",
        "s321553b515c7": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1217-L1219",
        "s6bbc17472387": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/config/settings/base.py#L1220-L1222",
        "s03b85ae8f0f4": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/webhooks/validators.py#L28-L38",
        "sd05478356bf3": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/integrations/utils.py#L19-L22",
        "s51f9f131dfd5": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/data_sync/utils.py#L20-L32",
        "s5cb708eebb43": "https://github.com/baserow/baserow/blob/2.3.4/docs/installation/configuration.md#L146-L149",
        "sbceea12c2b80": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/views/models.py#L109-L122",
        "s65d5b6ec3fb4": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L19-L21",
        "sb4e1c631bbd5": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/tokens/models.py#L75-L82",
        "s699ef6153a33": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/contrib/database/api/tokens/authentications.py#L21-L23"
      }
    },
    "appsmith": {
      "name": "Appsmith",
      "basis": "v2.4.1",
      "sources": {
        "s2650629933a1": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties",
        "sd1c55be91e30": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java",
        "se3cd894dc579": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/exceptions/AppsmithError.java",
        "sa68daf87cde7": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh",
        "s9fdcff5a28a4": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml",
        "sfa551c344e8b": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/aws_ami/docker-compose.yml",
        "se40e49cd9de3": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/filters/LoginRateLimitFilter.java",
        "s06eac9e0a51a": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/ratelimiting/RateLimitConfig.java#L40",
        "sc1f1abd600b0": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L322",
        "s3a9e231ca746": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/UrlCE.java#L6-L9",
        "sa8634927721d": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L329-L338",
        "s6d46c09f7792": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L255",
        "s7701866ee1a5": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/ce/CsrfConfigCE.java#L44-L54",
        "s6a53334cc4d2": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/ce/CsrfConfigCE.java#L81-L106",
        "sae91babcb5a4": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/FieldNameCE.java#L5",
        "s23e7c7d54ccb": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/FieldNameCE.java#L135",
        "sc070ba0137af": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/helpers/AuthenticationFailureRetryHandlerCEImpl.java#L30-L60",
        "sb4dc619c599a": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/helpers/AuthenticationFailureRetryHandlerCEImpl.java#L106",
        "sa558524c8bc9": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/handlers/ce/AuthenticationSuccessHandlerCE.java#L124-L136",
        "se19192d1489a": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/handlers/ce/AuthenticationSuccessHandlerCE.java#L186-L235",
        "s52eca71023ac": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L21-L39",
        "s9e4ca70d9dc0": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L152-L177",
        "sd0c549e0f54f": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L705-L740",
        "sdb0a35e74f82": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L671-L695",
        "sdd97bd5cc8bc": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L105-L108",
        "s06fbd7902eec": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L401-L402",
        "s1bac5ecd3691": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L53-L58",
        "s63b4dc6766f7": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L179-L182",
        "sffc958790b46": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L67-L69",
        "s45576ef2bb4e": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L80",
        "s1bde3f6a7588": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L567-L600",
        "sead11694fd57": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L602-L679",
        "s2bd203b4a9cd": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/configurations/SecurityConfig.java#L285-L316",
        "s60489a052bde": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L555-L566",
        "s000a728e94d9": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L963-L972",
        "s2f1e4c582d9a": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/ActionExecutionSolutionCEImpl.java#L686-L695",
        "s7e5a474dbd80": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/constants/ce/UrlCE.java#L37",
        "sfb11c4490069": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/controllers/ce/McpTokenControllerCE.java#L29-L85",
        "s4f6a62321409": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L45-L46",
        "s80bc1c82b4a9": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L73-L76",
        "sf3b41775b4ee": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/services/ce/McpTokenServiceCEImpl.java#L318-L320",
        "s3e90d004e4b4": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/converters/McpTokenAuthenticationConverter.java#L35-L79",
        "saf15fa4bec82": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/authentication/managers/McpTokenAuthenticationManager.java#L56-L72",
        "sa3be6497bf8f": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/filters/McpAllowlistWebFilter.java#L43-L90",
        "s0333f36f51e4": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L783-L835",
        "s7009c31f9850": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L91-L93",
        "sd1b7e1380fe1": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L109-L117",
        "scc550763055a": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-interfaces/src/main/java/com/appsmith/util/RestrictedHostFilter.java#L60-L62",
        "s15dac68e1f02": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/applications/base/ApplicationServiceCEImpl.java#L681-L713",
        "s8c014fcd6ba9": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/acl/ce/PolicyGeneratorCE.java#L220-L244",
        "s9554be69f39c": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/datasourcestorages/base/DatasourceStorageServiceCEImpl.java#L116-L127",
        "sab2d684262ab": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/domains/McpToken.java#L26-L27"
      }
    },
    "budibase": {
      "name": "Budibase",
      "basis": "v3.50.0",
      "sources": {
        "sb79f4a0be2f7": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml",
        "s30b88270dc9f": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf",
        "s431b2b2510f3": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts",
        "saef5b25a8f2f": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/controllers/global/users.ts",
        "s238169b73bfe": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts",
        "se3230a244c80": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L111-L120",
        "se33db249e0f0": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L129-L144",
        "se2e95745d7e3": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf#L86",
        "s8bc4e1bb1886": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/proxy/nginx.prod.conf#L240-L243",
        "s6df454728633": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts#L40-L43",
        "s976211545532": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/index.ts#L133-L167",
        "s8b1726b40dff": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts#L13-L28",
        "saabeb355a0a8": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/routes/global/users.ts#L92-L96",
        "s9f7bed6ebf05": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/worker/src/api/controllers/global/users.ts#L231-L289",
        "s764d9142f68c": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/startup/index.ts#L226-L266",
        "s7c48a35c5ba4": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/environment.ts#L267-L268",
        "sbe9669fee3b8": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/docker-compose.yaml#L27-L28",
        "s3acb06b0d0aa": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/Dockerfile#L89-L91",
        "sec078b6aaa63": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/Dockerfile#L151-L154",
        "sd85e57b83baf": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/VERSION#L1",
        "sdc52da3b46b6": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/runner.sh#L165-L166",
        "s53d6862b140c": "https://github.com/Budibase/budibase/blob/v3.50.0/hosting/couchdb/docker-entrypoint.sh#L70-L75",
        "s95d7f56c8fa4": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L7-L20",
        "s69ba40cb3daa": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L27-L30",
        "sf26430c2bdcb": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L134-L162",
        "sf2ef0bf4c23a": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/blacklist/blacklist.ts#L164-L187",
        "s5361cdba5d19": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/integrations/rest.ts#L966",
        "s4decb4890b8a": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/utils/outboundFetch.ts#L39-L53",
        "sa802f16ef95c": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/backend-core/src/utils/outboundFetch.ts#L172-L252",
        "s4e15f1068f65": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/outgoingWebhook.ts#L1",
        "sac356e797c47": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/outgoingWebhook.ts#L68",
        "s5f49eed852c5": "https://github.com/Budibase/budibase/blob/v3.50.0/packages/server/src/automations/steps/utils.ts#L28-L35"
      }
    },
    "budibase-prev": {
      "name": "Budibase",
      "basis": "v3.46.0",
      "sources": {
        "s735ead81ce9c": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env",
        "s5209f2549c9b": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env#L4-L16",
        "se993218560de": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/hosting.properties#L4-L18",
        "s6179ec0d9abd": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/digitalocean/files/var/lib/cloud/scripts/per-instance/001_onboot#L11-L15",
        "s9cc27222e133": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/tests/jestEnv.ts#L9-L10",
        "sbe7e0469e7a8": "https://github.com/Budibase/budibase/blob/v3.46.0/scripts/dev/manage.js#L11-L12",
        "s7a6a28283a3f": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/middleware/emailLockout.ts",
        "s5be4af8a88a0": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/middleware/ipLockout.ts",
        "s77630f32e4e1": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L33-L36",
        "sc8e055c73778": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/environment.ts#L91-L95",
        "s3e5500686e62": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L7-L13",
        "s66bd10ffda8a": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/auth.ts#L32-L38",
        "sc2a820ba2643": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L55-L71",
        "s3979e1c96123": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L78-L93",
        "sc510cb26c848": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/auth.ts#L111-L140",
        "s7fee026b936f": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/automations/email/utils/getClient.ts#L105-L107",
        "sd32e1885283d": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/src/security/roles.ts#L172-L181",
        "s396e27cd75b3": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/api/routes/webhook.ts#L16-L17",
        "se05491c9b380": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/server/src/api/routes/endpointGroups/standard.ts#L24-L25",
        "s0817280fc9db": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/self.ts#L4-L6",
        "sa94745819bf4": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/endpointGroups/standard.ts#L11",
        "s6b2f1a9247d1": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/self.ts#L44-L68",
        "se3edc17ada43": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/backend-core/src/middleware/authenticated.ts#L72-L97"
      }
    },
    "windmill": {
      "name": "Windmill",
      "basis": "v1.864.1",
      "sources": {
        "s3934703e8ba2": "https://github.com/windmill-labs/windmill/blob/v1.864.1/README.md",
        "s9186f1630378": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/src/main.rs",
        "s6a71d3938c7a": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs",
        "s6a7eeac413b7": "https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml",
        "sdcc9601405df": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/migrations/20220123221903_first.up.sql",
        "s8927ade6b336": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/migrations/20220816185849_remove_non_admin_users.up.sql",
        "s197472c83650": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs",
        "s95545eb64ae3": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs",
        "s8d6da1611d2b": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L675-L677",
        "s1fde2a9ce9df": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L1079-L1082",
        "s34c845279149": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L170",
        "sb45ede9395a3": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L174",
        "s90f76651f88f": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L338-L341",
        "s3f9840f794e2": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L2886",
        "s65690d38292c": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L2924",
        "sa053111d31e4": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L3842",
        "s3eb2272d2200": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/per_minute_counter.rs#L14",
        "sdfa139e2651c": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/per_minute_counter.rs#L56-L88",
        "s71d1aa24bd03": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs#L82-L86",
        "s7aeb84337b6c": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/login_rate_limit.rs#L119-L136",
        "s50609ebb7768": "https://github.com/windmill-labs/windmill/blob/v1.864.1/debugger/dap_debug_service.ts#L157",
        "s05c898fe1013": "https://github.com/windmill-labs/windmill/blob/v1.864.1/debugger/dap_websocket_server_bun.ts#L226",
        "sd4d405943f19": "https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L36",
        "s747ec7a3c3e6": "https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L55",
        "s959bedaeb3ac": "https://github.com/windmill-labs/windmill/blob/v1.864.1/docker-compose.yml#L90-L99",
        "sfed7f7955c95": "https://github.com/windmill-labs/windmill/blob/v1.864.1/.env#L1",
        "se768c5e12136": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L26",
        "sbdd62c72983b": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L336-L357",
        "s2ed0342f80b5": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/variables.rs#L388-L396",
        "sf1c0ec61b519": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1084-L1086",
        "s57e6db700775": "https://github.com/windmill-labs/windmill/blob/v1.864.1/Dockerfile#L360",
        "s57a8de182294": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/THREAT_MODEL.md#L140",
        "sb2e11acd0110": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L568-L584",
        "s806ce76b8583": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L586-L607",
        "s1eb5b817f20e": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-worker/src/worker.rs#L1094-L1122",
        "s77e95744ffe0": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L301-L319",
        "s3e2a5dc4067c": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L333-L342",
        "sbaee4570fdea": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4129-L4138",
        "s0dff47578f66": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L381-L410",
        "s8068c39d7ec0": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4421-L4456",
        "s4e3ad6e9ee91": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L6540-L6556",
        "s1babd0356780": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2862-L2885",
        "s00b4346cb147": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3858-L3874",
        "s72340c52c301": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L3853-L3855",
        "s0ffbb735ee67": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L4036-L4047",
        "s24d85c458bed": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L2200-L2216",
        "sb8e066237cc0": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/apps.rs#L1444-L1487",
        "sdac197bff60b": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/workspaces.rs#L1442-L1475",
        "s446c12c7fd99": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/tests/app_anonymous_execution_mode.rs#L3-L10",
        "sb16891a3b300": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L675-L676",
        "s8c7504a63c12": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/lib.rs#L1110-L1115",
        "s6f2958127ca6": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger-http/src/lib.rs#L104-L114",
        "sdb94d7f26de5": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L541-L601",
        "s9e60529985a7": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L408-L470",
        "s7534ce6dc02d": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api/src/triggers/http/handler.rs#L475-L488",
        "s36c83429dee9": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-trigger/src/types.rs#L214-L223",
        "safef5587ed44": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L941-L971",
        "s199e136efca8": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/lib.rs#L453-L457",
        "sa5e96c4c912f": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-users/src/users.rs#L3218-L3273",
        "sf0444f76ef81": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-common/src/global_settings.rs#L119-L157",
        "s98e94d1afd4e": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/windmill-api-auth/src/auth.rs#L788-L812",
        "s39703617a90a": "https://github.com/windmill-labs/windmill/blob/v1.864.1/backend/src/main.rs#L469"
      }
    },
    "nocodb-docs": {
      "name": "NocoDB docs",
      "basis": "unknown",
      "sources": {
        "sf5c4bcd686ad": "https://nocodb.com/docs/product-docs/account-settings/authentication/two-factor-authentication"
      }
    },
    "appsmith-docs": {
      "name": "Appsmith docs",
      "basis": "unknown",
      "sources": {
        "sab210f0928ea": "https://docs.appsmith.com/getting-started/setup/instance-configuration/authentication"
      }
    },
    "docker": {
      "name": "Docker docs",
      "basis": "unknown",
      "sources": {
        "sd34e76a09f6c": "https://docs.docker.com/reference/cli/docker/container/exec/",
        "s2fecb6db5480": "https://docs.docker.com/engine/network/firewall-iptables/"
      }
    },
    "docker-new": {
      "name": "Docker CLI",
      "basis": "v27.2.0",
      "sources": {
        "sca9a0e1e4b6a": "https://github.com/docker/cli/blob/v27.2.0/cli/command/formatter/container.go"
      }
    },
    "docker-old": {
      "name": "Docker CLI",
      "basis": "v27.1.2",
      "sources": {
        "sa202ad11d4ed": "https://github.com/docker/cli/blob/v27.1.2/cli/command/formatter/container.go"
      }
    },
    "node": {
      "name": "Node.js",
      "basis": "v22.22.1",
      "sources": {
        "sfb3e306c102d": "https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md"
      }
    },
    "couchdb": {
      "name": "CouchDB",
      "basis": "3.5.2",
      "sources": {
        "s34292991c4ec": "https://github.com/apache/couchdb/blob/3.5.2/src/docs/src/api/server/authn.rst"
      }
    },
    "litellm": {
      "name": "LiteLLM authentication source",
      "basis": "6ef7b86748118ceecd95271727c2fa167ce55fec",
      "sources": {
        "sbe6fa0b81017": "https://raw.githubusercontent.com/BerriAI/litellm/6ef7b86748118ceecd95271727c2fa167ce55fec/litellm/proxy/auth/user_api_key_auth.py"
      }
    },
    "nginx-docs": {
      "name": "nginx docs",
      "basis": "unknown",
      "sources": {
        "sb3bee9429629": "https://nginx.org/en/docs/http/ngx_http_limit_req_module.html",
        "sf3430c5a0b22": "https://nginx.org/en/docs/http/ngx_http_proxy_module.html",
        "sb3ce35ba8f3d": "https://nginx.org/en/docs/http/ngx_http_headers_module.html"
      }
    },
    "fail2ban": {
      "name": "fail2ban",
      "basis": "1.1.1",
      "sources": {
        "s305d56ee7f00": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L85-L133",
        "s0718dcd4c275": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L447-L458",
        "s95d03bfa0c4c": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L510-L516",
        "s435857e88b8a": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2bancmdline.py#L35-L40",
        "s5009ca00e04b": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2bancmdline.py#L219-L227",
        "sea0d79ea51a4": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/fail2banclient.py#L135-L157",
        "sb98177243103": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/beautifier.py#L80-L112",
        "sa1bc4a6810c8": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/transmitter.py#L513-L522",
        "s973481062b5f": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/server.py#L628-L629",
        "s68908eb140b3": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/jail.py#L186-L197",
        "s5e27812bcd29": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/actions.py#L721-L746",
        "s77d6a8606bc3": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/client/beautifier.py#L263-L272",
        "s103cd4af8836": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/transmitter.py#L54-L65",
        "s47cab52e5be8": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/filter.py#L593-L607",
        "s393413f9e190": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/filter.py#L718-L738",
        "sfa12cc939a5f": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/server/actions.py#L502-L520",
        "s6820347df7f0": "https://github.com/fail2ban/fail2ban/blob/1.1.1/man/fail2ban-client.1#L214-L223",
        "s3f7ddb23eb75": "https://github.com/fail2ban/fail2ban/blob/1.1.1/man/fail2ban-client.1#L310-L311",
        "sccaa39ad1045": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/protocol.py#L109",
        "s0fa658a17fef": "https://github.com/fail2ban/fail2ban/blob/1.1.1/fail2ban/protocol.py#L141"
      }
    },
    "cors": {
      "name": "expressjs/cors",
      "basis": "v2.8.5",
      "sources": {
        "s45d81d86a562": "https://github.com/expressjs/cors/blob/v2.8.5/lib/index.js"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s5e1383feef7d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79",
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md",
        "s343269d1c01c": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/dump-header.md",
        "s809185b389c5": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/noproxy.md",
        "s1222d47e1017": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/globoff.md",
        "sdd1aa884c51d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/disable.md",
        "s40cfe8ffa885": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/silent.md",
        "s820e85aa0636": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/output.md",
        "sc2e8fc82d74a": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/max-time.md",
        "sc103df7ca615": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/connect-timeout.md"
      }
    },
    "caddy-docs": {
      "name": "Caddy docs",
      "basis": "unknown",
      "sources": {
        "s3865a73ccda3": "https://caddyserver.com/docs/caddyfile/directives/reverse_proxy"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep builders private with fronting auth, claim admin early and protect databases storing connected-system credentials.", "components": ["nocodb", "baserow", "appsmith", "budibase", "windmill"], "sources": ["nocodb:sd74ca4df55b0", "baserow:s1b31314982f4", "appsmith:s9fdcff5a28a4", "budibase:sb79f4a0be2f7", "windmill:s6a7eeac413b7"], "status": "REASONED"},
    "nocodb-bind": {"text": "PORT defaults 8080; listen omits host, so Node binds unspecified IPv6/IPv4. No application bind setting; restrict publication/firewall.", "components": ["nocodb", "node"], "sources": ["nocodb:sa19c6557b712", "nocodb:sd74ca4df55b0", "node:sfb3e306c102d"], "status": "REASONED"},
    "nocodb-first": {"text": "First signup becomes super-admin; claim first or seed NC_ADMIN_EMAIL/NC_ADMIN_PASSWORD.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:s8a1de0bc97b0"], "status": "REASONED"},
    "nocodb-signup": {"text": "invite_only_signup defaults false; enable to stop later self-signups.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:sd0e9f451673f"], "status": "REASONED"},
    "nocodb-encryption": {"text": "Unset NC_CONNECTION_ENCRYPT_KEY stores external DB credentials unchanged; set before adding sources, or startup encrypts existing sources when added later.", "components": ["nocodb"], "sources": ["nocodb:sca40040b40cc", "nocodb:saf056bb4ff37"], "status": "REASONED"},
    "nocodb-jwt": {"text": "Unset NC_AUTH_JWT_SECRET generates/stores a UUID as nc_auth_jwt_secret; replace README sample 569a1821-0a93-45e8-87ab-eb857f20a010.", "components": ["nocodb"], "sources": ["nocodb:sa19c6557b712", "nocodb:s536899ecd4a5"], "status": "REASONED"},
    "nocodb-cors": {"text": "At 2026.09.0, rspack.timely.config.js builds docker/main.js, which docker/start.sh runs, from timely.ts; it and dockerEntry.ts call cors() with no options, and cors 2.8.5, the lockfile's only cors, then sends Access-Control-Allow-Origin: * on every response and preflight passing through it, with no Allow-Credentials. No Dockerfile at the tag, so the image's script is unverified.", "components": ["nocodb", "cors"], "sources": ["nocodb:sf6a63339341e", "nocodb:sbfbf630008e1", "nocodb:sfa0f1d7f1be6", "nocodb:sd74ca4df55b0", "nocodb:se352e8e45038", "cors:s45d81d86a562"], "status": "REASONED"},
    "nocodb-cors-risk": {"text": "Auth is the xc-auth header or the nc_token cookie (httpOnly, SameSite=Lax, path /api), or an xc-token or Bearer API token. With * and no Allow-Credentials, browsers expose no credentialed response cross-origin; the residual risk is pages on other sites reading, through a visitor's browser, responses that need no credentials (guide inference).", "components": ["nocodb", "cors"], "sources": ["nocodb:s512cac75f9fb", "nocodb:s6af8fddcbdc7", "nocodb:se879dae3d563", "cors:s45d81d86a562"], "status": "REASONED"},
    "nocodb-cors-proxy": {"text": "Remove the header at the proxy: nginx proxy_hide_header in every location proxying to NocoDB, or Caddy reverse_proxy header_down -Access-Control-Allow-Origin. For one exact origin, nginx also adds it with add_header (repeat inherited add_header lines such as HSTS there) and Caddy sets it with header_down (guide advice).", "components": ["nginx-docs", "caddy-docs"], "sources": ["nginx-docs:sf3430c5a0b22", "nginx-docs:sb3ce35ba8f3d", "caddy-docs:s3865a73ccda3"], "status": "REASONED"},
    "nocodb-proxy": {"text": "Startup resets trust proxy from NC_TRUST_PROXY, default no trust; restrict hops/subnets, never true with direct client access.", "components": ["nocodb"], "sources": ["nocodb:sa19c6557b712", "nocodb:s635b35ce4689", "nocodb:sd74ca4df55b0", "nocodb:sfa0f1d7f1be6"], "status": "REASONED"},
    "nocodb-packaging": {"text": "README marks binaries for quick local testing and documents Docker image and Auto-upstall paths; the October 2026 release API record lists no assets; the 2026.09.0 tag carries package version 0.301.3. Use the image or vendor install script for production (guide advice).", "components": ["nocodb"], "sources": ["nocodb:s536899ecd4a5", "nocodb:sca0c9c0ecf24", "nocodb:sb4d5b659f7b8", "nocodb:s118384fa1d9f", "nocodb:s9bee4adc612e", "nocodb:s3f296c702bc5"], "status": "REASONED"},
    "nocodb-upstall-fetch": {"text": "The README's Auto-upstall command fetches the script over plain HTTP and executes it with Bash; its source link points to develop. Fetch over HTTPS from a pinned, reviewed source and read before running (guide advice).", "components": ["nocodb"], "sources": ["nocodb:s2769b9054778", "nocodb:s2b16e2c93606"], "status": "REASONED"},
    "nocodb-webhook-ssrf": {"text": "At 2026.09.0, self-hosted NocoDB filters webhooks with request-filtering-agent; a throw-on-failure invocation reports a refused private address, with an NC_ALLOW_LOCAL_HOOKS=true hint only if !isEE || isOnPrem. NC_ALLOW_LOCAL_HOOKS, NC_WEBHOOK_ALLOW_PRIVATE_NETWORK or NC_DISABLE_SSRF_PROTECTION set to exactly true disables it; leave them unset and filter egress at the network (guide advice).", "components": ["nocodb"], "sources": ["nocodb:s472d833bd66b", "nocodb:sa6b6a373e0ff", "nocodb:scc2c1474fe1a", "nocodb:sdbf149d571b4"], "status": "REASONED"},
    "nocodb-ssrf-sources": {"text": "The same switch turns SSRF protection off for external-database sources when NC_ALLOW_LOCAL_EXTERNAL_DBS is true and for data imports when NC_ALLOW_LOCAL_DATA_IMPORT is true; where those sources apply it was not traced. Cloud ignores all five variables. Leave both unset (guide advice).", "components": ["nocodb"], "sources": ["nocodb:scc2c1474fe1a"], "status": "REASONED"},
    "nocodb-share": {"text": "Shared-view row routes take the view's optional password in an xc-password header, so a view shared without one is readable by link holders (guide reading); a base's shared link is removed by disableSharedBaseLink. A source search found no env var that turns sharing off instance-wide; review shares before exposure (guide advice).", "components": ["nocodb"], "sources": ["nocodb:s7db0b920da5a", "nocodb:s51ca09d692df", "nocodb:s26c73fbba6b3"], "status": "REASONED"},
    "nocodb-token": {"text": "API tokens in xc-token, or Authorization: Bearer as fallback, skip the sign-in route and act with the creating user's roles; a token with a base_id is refused for other bases on requests that resolve a base, and an old token with no user gets the editor role. Fronting MFA covers tokens only if the proxy also gates /api (guide reading). Expiry enforcement was not traced.", "components": ["nocodb"], "sources": ["nocodb:s9b89db825243", "nocodb:sfdb74b3b8564", "nocodb:s82a140cf2510", "nocodb:s1f0e06fcc373", "nocodb:sc6248503f82d"], "status": "REASONED"},
    "baserow-bind": {"text": "Caddy publishes 80/443 on HOST_PUBLISH_IP default 0.0.0.0; set it or publish loopback. Docker wildcard publication bypasses UFW.", "components": ["baserow"], "sources": ["baserow:s1b31314982f4", "baserow:s3f61036aca03"], "status": "REASONED"},
    "baserow-first": {"text": "First signup becomes staff; claim before exposure.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6"], "status": "REASONED"},
    "baserow-signup": {"text": "allow_new_signups defaults True; disable in admin settings, yielding Sign up is disabled.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6", "baserow:s4588448964a2"], "status": "REASONED"},
    "baserow-secrets": {"text": "Compose requires SECRET_KEY/DATABASE_PASSWORD/REDIS_PASSWORD; .env.example leaves them empty. Generate your own.", "components": ["baserow"], "sources": ["baserow:s1b31314982f4", "baserow:s1a472d828699"], "status": "REASONED"},
    "baserow-mfa": {"text": "Core registers a TOTP provider.", "components": ["baserow"], "sources": ["baserow:sd858f9ee45e0"], "status": "REASONED"},
    "baserow-outbound-private": {"text": "Webhooks and integration requests go through advocate unless BASEROW_WEBHOOKS_ALLOW_PRIVATE_ADDRESS or BASEROW_INTEGRATIONS_ALLOW_PRIVATE_ADDRESS is on; both are read with bool(os.getenv(...)), so any non-empty value, false and 0 included, enables them. Leave both unset; for one internal webhook target, the docs point to the URL and IP lists instead.", "components": ["baserow"], "sources": ["baserow:s577ac3bf7492", "baserow:s321553b515c7", "baserow:s03b85ae8f0f4", "baserow:sd05478356bf3", "baserow:s5cb708eebb43"], "status": "REASONED"},
    "baserow-data-sync-private": {"text": "BASEROW_DATA_SYNC_ALLOW_PRIVATE_ADDRESS defaults to true, and while true data sync sends with plain requests instead of advocate, so a data sync URL can reach internal addresses by default (guide reading; not tested). Set it false; str_to_bool was not read, so confirm the refusal on a test instance, and filter egress at the network (guide advice).", "components": ["baserow"], "sources": ["baserow:s6bbc17472387", "baserow:s51f9f131dfd5"], "status": "REASONED"},
    "baserow-public-views": {"text": "A view's public flag (default false) makes it readable at a public URL, optionally behind public_view_password; review public views and password those that must stay public before exposure (guide advice).", "components": ["baserow"], "sources": ["baserow:sbceea12c2b80"], "status": "REASONED"},
    "baserow-db-token": {"text": "Database tokens in an Authorization: Token header authenticate the row create, read, update and delete endpoints, with permissions on one table, one database or the whole workspace. They skip the login view, so fronting MFA covers them only if the proxy also gates the API paths (guide reading).", "components": ["baserow"], "sources": ["baserow:s699ef6153a33", "baserow:s65d5b6ec3fb4", "baserow:sb4e1c631bbd5"], "status": "REASONED"},
    "appsmith-bind": {"text": "Java defaults APPSMITH_SERVER_ADDRESS=127.0.0.1 and port 8080 inside the container.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1"], "status": "REASONED"},
    "appsmith-publish": {"text": "Bundled Caddy fronts port 80; development Compose publishes host 8080, AWS example 80/443.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4", "appsmith:sfa551c344e8b"], "status": "REASONED"},
    "appsmith-first": {"text": "First signup claims super-user while no users exist; claim before exposure.", "components": ["appsmith"], "sources": ["appsmith:sd1c55be91e30"], "status": "REASONED"},
    "appsmith-signup": {"text": "APPSMITH_SIGNUP_DISABLED defaults false; set true or restrict APPSMITH_SIGNUP_ALLOWED_DOMAINS. Refusal is SIGNUP_DISABLED.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1", "appsmith:sd1c55be91e30", "appsmith:se3cd894dc579"], "status": "REASONED"},
    "appsmith-encryption": {"text": "Entrypoint generates 13-character encryption password/salt; external values override them. Development Compose sets both abcd; replace before first start.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4"], "status": "REASONED"},
    "appsmith-rotation": {"text": "Changing an existing abcd encryption pair presumably makes stored credentials unreadable; plan re-entry. Inferred, not tested.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4"], "status": "REASONED"},
    "budibase-publish": {"text": "Proxy publishes MAIN_PORT, sample 10000; LiteLLM publishes LITELLM_PORT default 4000.", "components": ["budibase", "budibase-prev"], "sources": ["budibase-prev:s735ead81ce9c", "budibase:sb79f4a0be2f7"], "status": "REASONED"},
    "budibase-couchdb": {"text": "Proxy /db/ reaches CouchDB. Compose maps COUCH_DB_USER/PASSWORD to COUCHDB_USER/PASSWORD; the image entrypoint adds that admin only when both are non-empty and its existing-admin check finds none for that name. With unchanged samples and that condition, anyone reaching the proxy can try budibase/budibase.", "components": ["budibase", "budibase-prev"], "sources": ["budibase-prev:s735ead81ce9c", "budibase:s30b88270dc9f", "budibase-prev:s5209f2549c9b", "budibase:se3230a244c80", "budibase:se2e95745d7e3", "budibase:s8bc4e1bb1886", "budibase:s3acb06b0d0aa", "budibase:sec078b6aaa63", "budibase:sd85e57b83baf", "budibase:sdc52da3b46b6", "budibase:s53d6862b140c"], "status": "REASONED"},
    "budibase-secrets": {"text": "Sample JWT_SECRET/API_ENCRYPTION_KEY are testsecret; service passwords, INTERNAL_API_KEY and LITELLM_MASTER_KEY are budibase. Replace all before first start. Compose pins docker.io/litellm/litellm:main-v1.83.10-stable.patch.3 and passes LITELLM_MASTER_KEY; acceptance of budibase by that image is not established.", "components": ["budibase", "budibase-prev"], "sources": ["budibase-prev:s735ead81ce9c", "budibase:sb79f4a0be2f7", "budibase-prev:s5209f2549c9b", "budibase:se33db249e0f0"], "status": "REASONED"},
    "budibase-sample-check": {"text": "This guide's October 2026 search of the full v3.46.0 tag with git grep -l testsecret v3.46.0 found exactly hosting/.env, hosting/digitalocean/files/var/lib/cloud/scripts/per-instance/001_onboot, hosting/hosting.properties, packages/backend-core/tests/jestEnv.ts and scripts/dev/manage.js. This guide inspected those hits.", "components": ["budibase-prev"], "sources": ["budibase-prev:s735ead81ce9c", "budibase-prev:s5209f2549c9b", "budibase-prev:se993218560de", "budibase-prev:s6179ec0d9abd", "budibase-prev:s9cc27222e133", "budibase-prev:sbe7e0469e7a8"], "status": "REASONED"},
    "budibase-sample-safeguard": {"text": "This guide's assessment is that the v3.46.0 testsecret search hits do not establish absence of production rejection; no live safeguard test ran.", "components": ["budibase-prev"], "sources": ["budibase-prev:s735ead81ce9c", "budibase-prev:s5209f2549c9b", "budibase-prev:se993218560de", "budibase-prev:s6179ec0d9abd", "budibase-prev:s9cc27222e133", "budibase-prev:sbe7e0469e7a8"], "status": "REASONED"},
    "budibase-init": {"text": "POST /api/global/users/init is public; its body validator requires string email and tenantId fields, permits an optional password, rejects unknown fields and precedes adminUser. In the supplied tenant context, checkAnyUserExists() truthy causes 403 with the exact vendor error quoted in the body.", "components": ["budibase"], "sources": ["budibase:s431b2b2510f3", "budibase:saef5b25a8f2f", "budibase:s238169b73bfe", "budibase:s6df454728633", "budibase:s976211545532", "budibase:s8b1726b40dff", "budibase:saabeb355a0a8", "budibase:s9f7bed6ebf05"], "status": "REASONED"},
    "budibase-init-probe": {"text": "The checkAnyUserExists() helper definition was not fetched, so which users count and any multi-tenancy exception remain unestablished. This guide assesses POST /api/global/users/init as unsafe for read-only claimed-state probing: invalid bodies can fail validation in both states, while accepted initialization creates an admin.", "components": ["budibase"], "sources": ["budibase:saef5b25a8f2f", "budibase:s9f7bed6ebf05", "budibase:s8b1726b40dff", "budibase:saabeb355a0a8"], "status": "REASONED"},
    "budibase-seed": {"text": "Claim admin before exposure (guide advice), manually or with BB_ADMIN_USER_EMAIL/BB_ADMIN_USER_PASSWORD. Startup attempts seeding only with SELF_HOSTED truthy, MULTI_TENANCY falsy and both values non-empty; in tenancy.getTenantId() context, it calls createAdminUser when the admin checklist is not checked OR the email does not exist, with hashPassword/requirePassword/skipPasswordValidation true.", "components": ["budibase"], "sources": ["budibase:saef5b25a8f2f", "budibase:s7c48a35c5ba4", "budibase:sbe9669fee3b8", "budibase:s764d9142f68c"], "status": "REASONED"},
    "windmill-code": {"text": "Workers execute user scripts; a login enables code execution on worker hosts.", "components": ["windmill"], "sources": ["windmill:s3934703e8ba2", "windmill:s6a71d3938c7a"], "status": "REASONED"},
    "windmill-bind": {"text": "Default 0.0.0.0:8000; SERVER_BIND_ADDR changes binary binding. Default wildcard bind was not observed.", "components": ["windmill"], "sources": ["windmill:s9186f1630378"], "status": "REASONED"},
    "windmill-compose": {"text": "Compose exposes server 8000 internally; Caddy publishes 80/25 on all host interfaces. Bind publications privately; container loopback cutting Caddy off is inferred.", "components": ["windmill"], "sources": ["windmill:s6a7eeac413b7"], "status": "REASONED"},
    "windmill-sandbox": {"text": "DISABLE_NSJAIL defaults true; sandboxing is not enabled by default.", "components": ["windmill"], "sources": ["windmill:s6a71d3938c7a"], "status": "REASONED"},
    "windmill-privileged": {"text": "Shipped worker uses privileged=true.", "components": ["windmill"], "sources": ["windmill:s6a7eeac413b7"], "status": "REASONED"},
    "windmill-smtp": {"text": "Port 25 serves email triggers; do not publish unless used.", "components": ["windmill"], "sources": ["windmill:s6a7eeac413b7"], "status": "REASONED"},
    "windmill-debugger": {"text": "Vendor warns REQUIRE_SIGNED_DEBUG_REQUESTS=false exposes an unauthenticated code-execution debugger on reachable deployments.", "components": ["windmill"], "sources": ["windmill:s6a7eeac413b7"], "status": "REASONED"},
    "windmill-sandbox-enable": {"text": "DISABLE_NSJAIL=false makes the worker's sandbox check return true before the instance isolation setting is read, and the v1.864.1 Dockerfile copies nsjail into the image. Whether nsjail works in the vendor Compose worker or needs privileged: true was not established; no run with nsjail enabled was made.", "components": ["windmill"], "sources": ["windmill:sf1c0ec61b519", "windmill:s57e6db700775"], "status": "REASONED"},
    "windmill-egress": {"text": "The v1.864.1 threat model says network isolation is an nsjail feature and outbound network from user code is unrestricted by default; put workers on a network reaching only what scripts need and block the metadata address there (guide advice).", "components": ["windmill"], "sources": ["windmill:s57a8de182294"], "status": "REASONED"},
    "windmill-db-secret": {"text": "The v1.864.1 Compose file sets POSTGRES_PASSWORD to changeme, and the sample .env sets DATABASE_URL with that password and sslmode=disable, which Compose passes to the server. Change the password before first start, keep the database off public networks and ask for TLS to a remote database (guide advice).", "components": ["windmill"], "sources": ["windmill:sd4d405943f19", "windmill:s747ec7a3c3e6", "windmill:sfed7f7955c95"], "status": "REASONED"},
    "windmill-workspace-key": {"text": "The workspace cipher key is read from the workspace_key table of the same database, with SECRET_SALT appended only when set; each fetch without a cipher cached in the last 300 s logs the key's first 8 characters at info level. Without SECRET_SALT a database copy holds the key (inference). Set SECRET_SALT before storing secrets and protect logs (guide advice).", "components": ["windmill"], "sources": ["windmill:se768c5e12136", "windmill:sbdd62c72983b", "windmill:s2ed0342f80b5"], "status": "REASONED"},
    "login-limit": {"text": "Tool limits range from none (NocoDB, Baserow) through Windmill's global cap, with optional per-address and per-account limits, to Appsmith's per-username limit and Budibase's per-email and per-address lockouts, so rate-limit login endpoints per client address at the proxy, recovering it behind a CDN or second proxy, and add fail2ban filters per login path and status (guide advice).", "components": ["nocodb", "baserow", "appsmith", "budibase-prev", "windmill"], "sources": ["nocodb:s50856563cb62", "baserow:s9de0cfbd461a", "baserow:s1973090f6cb9", "appsmith:se40e49cd9de3", "budibase-prev:s7a6a28283a3f", "budibase-prev:s5be4af8a88a0", "windmill:s197472c83650"], "status": "REASONED"},
    "nocodb-login-limit": {"text": "The sign-in route's PublicApiLimiterGuard always allows requests; its comment leaves rate limiting to the network layer. Sign-in is served on four paths ending in /auth/user/signin, so a proxy limit must cover all four. The local strategy answers bad credentials with a bad-request error.", "components": ["nocodb"], "sources": ["nocodb:s50856563cb62", "nocodb:sdd5b3322fe9f", "nocodb:sbe0b751e6286", "nocodb:s659b1179d0e5"], "status": "REASONED"},
    "nocodb-mfa": {"text": "Rolling vendor docs make two-factor authentication a Cloud or licensed self-hosted (Business plan and above) feature. The 2026.09.0 migration adds TOTP columns; this guide's search of packages/nocodb/src found no TOTP setup or verify endpoint, and whether the open build can enable it was not established. Front it with MFA (guide advice).", "components": ["nocodb", "nocodb-docs"], "sources": ["nocodb:s31941e502c14", "nocodb-docs:sf5c4bcd686ad"], "status": "REASONED"},
    "baserow-totp-login": {"text": "The login view documents a temporary token for finishing verification on 2FA-protected accounts; whether TOTP can be required for every account was not established, so put MFA in front of Baserow (guide advice).", "components": ["baserow"], "sources": ["baserow:s9de0cfbd461a"], "status": "REASONED"},
    "baserow-login-limit": {"text": "The token-auth login view and its serializer (email or deprecated username, and password) have no throttle, failed-attempt counter or captcha; captcha is checked only on sign-up. Bad credentials get 401 ERROR_INVALID_CREDENTIALS. The optional throttle (default off) skips anonymous requests unless BASEROW_THROTTLE_IP_ENABLED, does not count failed logins and locks no account.", "components": ["baserow"], "sources": ["baserow:s9de0cfbd461a", "baserow:s4d7f125ca2e6", "baserow:s2085d93a8d4e", "baserow:sbb08ecd2fe19", "baserow:s1973090f6cb9", "baserow:s36c52d0540aa", "baserow:s8f32b1811523", "baserow:s37f43ff193d5", "baserow:s40fedf30e4c8", "baserow:s209db6950135"], "status": "REASONED"},
    "appsmith-login-limit": {"text": "Form login at /api/v1/login allows 5 attempts per submitted username per day, then redirects to /user/login?error=true instead of answering 429. Keyed per username, it lets one client try many usernames and anyone lock a known username out for up to a day. No setting for it was found.", "components": ["appsmith"], "sources": ["appsmith:se40e49cd9de3", "appsmith:s06eac9e0a51a", "appsmith:sc1f1abd600b0", "appsmith:s3a9e231ca746"], "status": "REASONED"},
    "appsmith-mfa": {"text": "This guide's search of the v2.4.1 server and client sources found no native MFA. Rolling vendor docs list Google, GitHub, OIDC and SAML sign-in besides form login; edition availability was not established. Put MFA in an enforcing identity provider or fronting proxy (guide advice).", "components": ["appsmith-docs"], "sources": ["appsmith-docs:sab210f0928ea"], "status": "REASONED"},
    "appsmith-ssrf-filter": {"text": "At v2.4.1 a restricted-host filter checks WebClient-based plugins (REST, GraphQL, SaaS), Elasticsearch, Redis connections and the SMTP test email, not JDBC, Mongo, ArangoDB or SMTP sends. It refuses nine metadata hosts, loopback, any-local, link-local, multicast and fc00::/7, also after DNS resolution, and allows most private IPv4 (RFC 1918); filter egress at the network too (guide advice).", "components": ["appsmith"], "sources": ["appsmith:s52eca71023ac", "appsmith:s9e4ca70d9dc0", "appsmith:sd0c549e0f54f", "appsmith:sdb0a35e74f82", "appsmith:sdd97bd5cc8bc", "appsmith:s06fbd7902eec", "appsmith:s7009c31f9850", "appsmith:sd1b7e1380fe1"], "status": "REASONED"},
    "appsmith-ssrf-optout": {"text": "APPSMITH_DISABLE_SSRF_FILTER set to true, in any letter case, skips every filter check at once. The blocked list is a constant in the code, and this guide found no environment variable that extends or replaces it. Leave the opt-out unset (guide advice).", "components": ["appsmith"], "sources": ["appsmith:s1bac5ecd3691", "appsmith:s63b4dc6766f7", "appsmith:sffc958790b46", "appsmith:s45576ef2bb4e"], "status": "REASONED"},
    "appsmith-make-public": {"text": "Make public gives anonymous visitors read on the app, its pages and theme, execute on its queries, and execute on their datasources unless used by other apps in the workspace the public role can read, needing no datasource permission. Anonymous callers run only published queries, with the saved datasource credentials (guide reading). Whether responses reveal credentials was not established.", "components": ["appsmith"], "sources": ["appsmith:s1bde3f6a7588", "appsmith:sead11694fd57", "appsmith:s2bd203b4a9cd", "appsmith:s60489a052bde", "appsmith:s000a728e94d9", "appsmith:s2f1e4c582d9a", "appsmith:s15dac68e1f02", "appsmith:s8c014fcd6ba9", "appsmith:s9554be69f39c"], "status": "REASONED"},
    "appsmith-mcp-token": {"text": "No personal access token was found; MCP tokens are the only user bearer credential. They are managed from a signed-in session only, last 30 to 365 days, are stored hashed, number at most 2 live per user on CE, need the configured internal secret in a header, and act as their owner on an endpoint allowlist. Revoke unused tokens (guide advice).", "components": ["appsmith"], "sources": ["appsmith:s7e5a474dbd80", "appsmith:sfb11c4490069", "appsmith:s4f6a62321409", "appsmith:s80bc1c82b4a9", "appsmith:sf3b41775b4ee", "appsmith:s3e90d004e4b4", "appsmith:saf15fa4bec82", "appsmith:sa3be6497bf8f", "appsmith:sab2d684262ab"], "status": "REASONED"},
    "budibase-login-limit": {"text": "At v3.46.0, the login validator accepts only username and password and rejects other fields before the lockouts. Login locks an email for 900 s after 5 failures (403, Retry-After) and answers 429 once one ctx.ip exceeds 10 validated login requests in that window. Anyone knowing an email can lock that user out; ctx.ip behind the bundled proxy was not verified.", "components": ["budibase-prev"], "sources": ["budibase-prev:s7a6a28283a3f", "budibase-prev:s5be4af8a88a0", "budibase-prev:s77630f32e4e1", "budibase-prev:sc8e055c73778", "budibase-prev:s3e5500686e62", "budibase-prev:s66bd10ffda8a", "budibase-prev:sc2a820ba2643"], "status": "REASONED"},
    "budibase-mfa": {"text": "This guide's search of v3.46.0 packages and a v3.50.0 source tree found no native MFA; put MFA in a fronting proxy or in the identity provider users sign in through (guide advice).", "components": ["budibase-prev"], "sources": ["budibase-prev:s77630f32e4e1"], "status": "REASONED"},
    "budibase-blacklist": {"text": "At v3.50.0 the outbound blacklist defaults to loopback, RFC 1918, CGNAT, link-local, 0.0.0.0/8, ::1, 2001::/32, 64:ff9b:1::/48, fc00::/7 and fe80::/10, and checks embedded IPv4. With SELF_HOSTED on, any BLACKLIST_IPS value, empty included, replaces the defaults. Leave it unset, or list every default range with your own entries, and filter egress at the network (guide advice).", "components": ["budibase"], "sources": ["budibase:s95d7f56c8fa4", "budibase:s69ba40cb3daa", "budibase:sf26430c2bdcb", "budibase:sf2ef0bf4c23a"], "status": "REASONED"},
    "budibase-blacklist-scope": {"text": "At v3.50.0 REST datasource requests and the outgoing-webhook step call fetchWithBlacklist, which checks each resolved address against the blacklist before each request; at v3.46.0 the IMAP trigger host check uses it too, and that file was not read at v3.50.0. SMTP, database datasources and file or URL imports were not traced, so the blacklist is not treated as covering all outbound traffic.", "components": ["budibase", "budibase-prev"], "sources": ["budibase:s5361cdba5d19", "budibase:s4e15f1068f65", "budibase:sac356e797c47", "budibase:s5f49eed852c5", "budibase:s4decb4890b8a", "budibase:sa802f16ef95c", "budibase-prev:s7fee026b936f"], "status": "REASONED"},
    "budibase-public": {"text": "At v3.46.0 the PUBLIC role is described as Accessible to anyone, and POST /api/webhooks/trigger/:instance/:id sits on the no-middleware route group, commented always public; the trigger controller was not traced. Review what PUBLIC can reach and treat each trigger URL as a public endpoint callable without a secret (guide advice).", "components": ["budibase-prev"], "sources": ["budibase-prev:sd32e1885283d", "budibase-prev:s396e27cd75b3", "budibase-prev:se05491c9b380"], "status": "REASONED"},
    "budibase-api-key": {"text": "At v3.46.0 each user has at most one API key, generated or fetched only through builder routes, and regenerating replaces it. A valid key resolves to its user, so it carries that user's full rights (guide reading); the code read shows no scope or expiry. Key requests skip the login route, so fronting MFA covers them only if the proxy gates the API paths (guide reading).", "components": ["budibase-prev"], "sources": ["budibase-prev:s0817280fc9db", "budibase-prev:sa94745819bf4", "budibase-prev:s6b2f1a9247d1", "budibase-prev:se3edc17ada43"], "status": "REASONED"},
    "windmill-login-limit": {"text": "/api/auth/login has an always-on global cap (default 10000/min per process); per-IP (120) and per-account (30 failures) limits apply only with CLOUD_HOSTED or when set. All count per clock minute; global and per-IP also guard login links. Per-IP trusts X-Real-IP (else X-Forwarded-For), so the proxy must overwrite it. A wrong password gets 400; only these limits answer 429.", "components": ["windmill"], "sources": ["windmill:s197472c83650", "windmill:s95545eb64ae3", "windmill:s71d1aa24bd03", "windmill:s7aeb84337b6c", "windmill:s3f9840f794e2", "windmill:s65690d38292c", "windmill:sb45ede9395a3", "windmill:sa053111d31e4", "windmill:s3eb2272d2200", "windmill:sdfa139e2651c", "windmill:s8d6da1611d2b", "windmill:s1fde2a9ce9df", "windmill:s34c845279149"], "status": "REASONED"},
    "windmill-mfa": {"text": "This guide's search of v1.864.1 backend and frontend sources found no native MFA; put MFA in a fronting proxy or in the identity provider users sign in through (guide advice).", "components": ["windmill"], "sources": ["windmill:s95545eb64ae3"], "status": "REASONED"},
    "windmill-nsjail-unavailable": {"text": "With DISABLE_NSJAIL=false, a worker that cannot run a test jail, or cannot find or start nsjail, logs an error that nsjail sandboxing will not be available, and jobs that require nsjail fail rather than run unsandboxed. A no_network annotation removes a script's network only under nsjail, and without a jail the script is refused; it is a per-script opt-in, not an egress control (guide reading).", "components": ["windmill"], "sources": ["windmill:sb2e11acd0110", "windmill:s806ce76b8583", "windmill:s1eb5b817f20e"], "status": "REASONED"},
    "windmill-public-apps": {"text": "Apps have four execution modes; the default, publisher, needs a login. Anonymous admits anyone, guest anyone signed in; both run the app's scripts as the publisher. Any writer can make an app anonymous unless a ruleset enables RestrictAnonymousAppDeployment, which gates only creating it or switching to it; enable it and the guest rule, and review apps already anonymous or guest (guide advice).", "components": ["windmill"], "sources": ["windmill:s77e95744ffe0", "windmill:s0dff47578f66", "windmill:s8068c39d7ec0", "windmill:s4e3ad6e9ee91", "windmill:s1babd0356780", "windmill:s00b4346cb147", "windmill:s72340c52c301", "windmill:s0ffbb735ee67", "windmill:s3e2a5dc4067c", "windmill:sbaee4570fdea", "windmill:sdac197bff60b", "windmill:s446c12c7fd99"], "status": "REASONED"},
    "windmill-app-link": {"text": "An app's public link is its id encrypted under the workspace cipher, and it opens the app only for callers the app's mode admits. The code read adds no random part or expiry, so the link stays the same while the app and the workspace key do (guide reading); withdraw a public app by changing its mode (guide advice).", "components": ["windmill"], "sources": ["windmill:s24d85c458bed", "windmill:sb8e066237cc0"], "status": "REASONED"},
    "windmill-http-routes": {"text": "HTTP routes at /api/r have six authentication methods; the handler checks a secret only for api_key, basic_http and signature, windmill needs a token that can read the route, and none checks nothing. Every route runs as its permissioned_as user, so a none route lets anyone run its script with that user's rights (guide reading). Keep privileged scripts off none routes (guide advice).", "components": ["windmill"], "sources": ["windmill:sb16891a3b300", "windmill:s8c7504a63c12", "windmill:s6f2958127ca6", "windmill:sdb94d7f26de5", "windmill:s9e60529985a7", "windmill:s7534ce6dc02d", "windmill:s36c83429dee9"], "status": "REASONED"},
    "windmill-tokens": {"text": "Tokens come from a Bearer header, the session cookie or ?token=; an unscoped one has its user's full rights. A token from the create or impersonate route has no expiry unless its creator or max_token_expiration_days sets one; service-account and server-minted tokens are outside that cap. Scope and expire tokens, avoid ?token= URLs, and require proxy login on API paths for MFA (guide advice).", "components": ["windmill"], "sources": ["windmill:safef5587ed44", "windmill:s199e136efca8", "windmill:sa5e96c4c912f", "windmill:sf0444f76ef81"], "status": "REASONED"},
    "windmill-docker-socket": {"text": "At v1.864.1 the Compose worker does not mount the host Docker socket; its docker.sock line is commented out for the legacy full-compat # docker mode, which the file warns grants user scripts full access to the host Docker daemon. Leave it unmounted; if that mode is required, treat every user who can write or deploy a script as having root on the host (guide advice).", "components": ["windmill"], "sources": ["windmill:s959bedaeb3ac"], "status": "REASONED"},
    "windmill-superadmin-secret": {"text": "SUPERADMIN_SECRET is unset by default; when set, a request presenting its value as a token acts as an admin with no scopes and no expiry, a token the server calls a virtual superadmin token. Leave it unset, or keep it in a secret store and rotate it like a root password (guide advice).", "components": ["windmill"], "sources": ["windmill:s98e94d1afd4e", "windmill:s39703617a90a"], "status": "REASONED"},
    "fail2ban-filter-status": {"text": "Failed logins get a bad-request error from NocoDB, 401 from Baserow, 403 from Budibase and 400 from Windmill, which a fail2ban filter can match with the login path. Appsmith answers failed and successful form logins alike with a redirect, so a status-only filter cannot separate them; this guide gives no Appsmith filter.", "components": ["nocodb", "baserow", "appsmith", "budibase-prev", "windmill"], "sources": ["nocodb:s659b1179d0e5", "baserow:s9de0cfbd461a", "budibase-prev:s3979e1c96123", "windmill:s3f9840f794e2", "appsmith:sc070ba0137af", "appsmith:sa558524c8bc9", "appsmith:se19192d1489a", "appsmith:se40e49cd9de3", "baserow:s209db6950135"], "status": "REASONED"},
    "verify-login-limit": {"text": "Via the proxy, send failed logins for no-such-user@example.invalid in each tool's format (JSON; Appsmith form-encoded with X-Requested-By): exposed, every attempt gets the app's answer (exit 1); fixed, the limit status follows an app answer (exit 0; 3 if 502, 503 or 504). Sequential attempts can miss a fast-refilling limit. Never use a real account. Not run against any deployment.", "components": ["nocodb", "baserow", "appsmith", "budibase-prev", "windmill", "nginx-docs"], "sources": ["nocodb:sdd5b3322fe9f", "nocodb:s659b1179d0e5", "baserow:s9de0cfbd461a", "baserow:s4d7f125ca2e6", "baserow:s8f32b1811523", "baserow:s37f43ff193d5", "baserow:s40fedf30e4c8", "appsmith:s3a9e231ca746", "appsmith:sa8634927721d", "appsmith:s6a53334cc4d2", "appsmith:s23e7c7d54ccb", "appsmith:se40e49cd9de3", "appsmith:sc070ba0137af", "budibase-prev:s3e5500686e62", "budibase-prev:s66bd10ffda8a", "budibase-prev:sc510cb26c848", "budibase-prev:s5be4af8a88a0", "budibase-prev:s7a6a28283a3f", "windmill:s90f76651f88f", "windmill:s65690d38292c", "windmill:s71d1aa24bd03", "nginx-docs:sb3bee9429629", "baserow:s522ee3d917aa", "baserow:s2bb53845a946", "appsmith:s6d46c09f7792", "appsmith:s7701866ee1a5", "appsmith:sae91babcb5a4", "appsmith:sb4dc619c599a", "baserow:s209db6950135"], "status": "REASONED", "verify": [7]},
    "verify-fail2ban": {"text": "On the fail2ban host, after failed logins above the jail's maxretry from a test address, fail2ban-client status JAIL: exposed, no such jail or the address absent from its Banned IP list (exit 1); fixed, the address listed (exit 0); unrecognized output is inconclusive (3). A listed ban is fail2ban's record, not proof its action blocked the address. Not run against any deployment.", "components": ["fail2ban"], "sources": ["fail2ban:s305d56ee7f00", "fail2ban:s0718dcd4c275", "fail2ban:s95d03bfa0c4c", "fail2ban:s435857e88b8a", "fail2ban:s5009ca00e04b", "fail2ban:sea0d79ea51a4", "fail2ban:sb98177243103", "fail2ban:sa1bc4a6810c8", "fail2ban:s973481062b5f", "fail2ban:s68908eb140b3", "fail2ban:s5e27812bcd29", "fail2ban:s77d6a8606bc3", "fail2ban:s103cd4af8836", "fail2ban:s47cab52e5be8", "fail2ban:s393413f9e190", "fail2ban:sfa12cc939a5f", "fail2ban:s6820347df7f0", "fail2ban:s3f7ddb23eb75", "fail2ban:sccaa39ad1045", "fail2ban:s0fa658a17fef"], "status": "REASONED", "verify": [8]},
    "verify-nocodb-signup": {"text": "Controlled signup creation is exposed; invite-only refusal is fixed. Hidden links prove nothing; inspect backend setting and confirm admin login.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:sd0e9f451673f"], "status": "REASONED"},
    "verify-baserow-signup": {"text": "Controlled signup creation is exposed; Sign up is disabled is fixed. Inspect allow_new_signups and confirm admin login.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6", "baserow:s4588448964a2"], "status": "REASONED"},
    "verify-appsmith-signup": {"text": "Controlled signup creation is exposed; SIGNUP_DISABLED is fixed. Inspect backend settings, confirm admin login and delete test accounts.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1", "appsmith:sd1c55be91e30", "appsmith:se3cd894dc579"], "status": "REASONED"},
    "verify-external": {"text": "Probe each public IP; control proves only its port, refusal/timeout may be local filtering, and unexpected connections need host confirmation.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:sb79f4a0be2f7", "windmill:s6a7eeac413b7"], "status": "REASONED"},
    "windmill-default-login": {"text": "Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1), with an earlier block form whose result was curl's own exit status: a fresh DB had only admin@windmill.dev as a password user/super-admin; changeme returned 200/token, then 400 after rotation while the new password returned 200. Not re-run on v1.864.1 or the current form.", "components": ["windmill"], "sources": ["windmill:s3934703e8ba2", "windmill:sdcc9601405df", "windmill:s8927ade6b336"], "status": "REASONED", "verify": [4]},
    "windmill-loopback": {"text": "Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1): with SERVER_BIND_ADDR=127.0.0.1 the release binary had only a loopback listener on the test port. Only that configured state was observed; the default wildcard bind was not run, as the host forbids it. Not re-run on v1.864.1.", "components": ["windmill"], "sources": ["windmill:s9186f1630378"], "status": "REASONED"},
    "windmill-sandbox-run": {"text": "Recorded past run on Windmill v1.817.0 loopback (the basis is v1.864.1): a worker without nsjail logged that nsjail sandboxing will not be available. No run with nsjail enabled was made, so isolation was not observed. Not re-run on v1.864.1.", "components": ["windmill"], "sources": ["windmill:s6a71d3938c7a"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory host sockets and Docker publications; NAT may have no socket, so absent ss entries do not establish isolation.", "components": ["docker", "baserow", "appsmith", "budibase", "windmill"], "sources": ["docker:s2fecb6db5480", "baserow:s1b31314982f4", "appsmith:s9fdcff5a28a4", "budibase:sb79f4a0be2f7", "windmill:s6a7eeac413b7"], "status": "REASONED", "verify": [1]},
    "verify-port-display": {"text": "IPv6 wildcard displays [::]: from v27.2.0 versus ::: through v27.1.2; both mean all host addresses unless filtered.", "components": ["docker", "docker-new", "docker-old"], "sources": ["docker:s2fecb6db5480", "docker-new:sca9a0e1e4b6a", "docker-old:sa202ad11d4ed"], "status": "REASONED", "verify": [1]},
    "verify-sample-tokens": {"text": "The current form exited 1 on the pinned Budibase v3.46.0, Appsmith v2.4.1, Windmill v1.864.1 and NocoDB 2026.09.0 files, printing their sample-token lines, and 0 reporting none on token-replaced copies; its guard, failed-read and unclassified-observation (hit only outside value position) arms, unreached there, exited 2, 3 and 0 locally. Harmless matches and external environment values limit scope.", "components": ["nocodb", "appsmith", "budibase-prev", "windmill"], "sources": ["nocodb:s536899ecd4a5", "appsmith:s9fdcff5a28a4", "budibase-prev:s735ead81ce9c", "windmill:s6a7eeac413b7"], "status": "DEMONSTRATED", "evidence": "The current form, with only its file path substituted, printed a line beginning \"FOUND vendor sample tokens:\" and exited 1 on each of the pinned Budibase v3.46.0 sample environment, Appsmith v2.4.1 development Compose file, Windmill v1.864.1 Compose file and NocoDB 2026.09.0 README (Docker example JWT secret, Docker image, Auto-upstall and binaries note; checked October 2026), and printed \"no vendor sample tokens found\" and exited 0 on copies with their sample tokens replaced.", "verify": [2]},
    "verify-nocodb-key": {"text": "docker exec tests configured key presence without printing it or passing its value in argv; no real container run. Startup selection/process value remain unverified.", "components": ["nocodb", "docker"], "sources": ["nocodb:sbfbf630008e1", "nocodb:se5da9707c684", "docker:sd34e76a09f6c"], "status": "REASONED", "verify": [3]},
    "nocodb-key-limits": {"text": "Trusted shells/startup assumed; environment remains readable to same-account/root or Docker-socket holders. Presence does not prove encryption; do not inject a replacement key.", "components": ["nocodb", "docker"], "sources": ["nocodb:sca40040b40cc", "nocodb:sbfbf630008e1", "nocodb:se5da9707c684", "docker:sd34e76a09f6c"], "status": "REASONED", "verify": [3]},
    "nocodb-key-logic": {"text": "Recorded runs of an earlier form, whose result arms ended with status 0, exercised set/empty/unset/missing-container branches with a docker exec stand-in only; no NocoDB deployment demonstrated. The current form was not re-run.", "components": ["docker"], "sources": ["docker:sd34e76a09f6c"], "status": "REASONED"},
    "verify-windmill-control": {"text": "Before trusting default-login 400, confirm real credentials work so a dead service is not treated as fixed.", "components": ["windmill"], "sources": ["windmill:s3934703e8ba2"], "status": "REASONED"},
    "verify-couchdb": {"text": "Sample login at /db/_session?basic=true should return 200 exposed and 401 after replacement; real credentials are the positive control.", "components": ["budibase", "budibase-prev", "couchdb"], "sources": ["budibase-prev:s735ead81ce9c", "budibase:s30b88270dc9f", "couchdb:s34292991c4ec", "budibase-prev:s5209f2549c9b", "budibase:se3230a244c80", "budibase:s8bc4e1bb1886", "budibase:s53d6862b140c"], "status": "REASONED", "verify": [5]},
    "verify-litellm": {"text": "Sample Bearer budibase at /v1/models should return 200 exposed; fixed, a 401 (or a 400 if the proxy has no database); confirm real credentials. The pinned authentication source rejects non-`sk-` keys with 401 when a database is connected and returns 400 without one; the exposed 200 still requires live comparison.", "components": ["budibase", "budibase-prev", "litellm"], "sources": ["budibase-prev:s735ead81ce9c", "budibase:sb79f4a0be2f7", "litellm:sbe6fa0b81017"], "status": "REASONED", "verify": [5]},
    "verify-litellm-pin": {"text": "The LiteLLM outcomes remain comparison expectations: this guide has not established that litellm.md's source pin corresponds to Compose image docker.io/litellm/litellm:main-v1.83.10-stable.patch.3; no source for that image was fetched.", "components": ["budibase", "litellm"], "sources": ["litellm:sbe6fa0b81017", "budibase:se33db249e0f0"], "status": "REASONED", "verify": [5]},
    "verify-tcp-outcomes": {"text": "Recorded loopback runs of an earlier form, whose control and result arms ended with status 0, observed connected/open, timeout/full accept queue, refused/closed and failed-control stopping; no real firewall demonstrated. The current form was not re-run.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:sb79f4a0be2f7", "windmill:s6a7eeac413b7"], "status": "REASONED", "verify": [6]},
    "verify-tcp-inputs": {"text": "Recorded guard tests of an earlier form, whose guard, control and result arms ended with status 0, rejected named hosts, malformed IPv4, zero/dotted IPv6, invalid ports and absent timeout; loopback/hex-mapped IPv6 passed, and the invalid hex values tested failed at the control. The current form was not re-run.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:sb79f4a0be2f7", "windmill:s6a7eeac413b7"], "status": "REASONED", "verify": [6]},
    "verify-windmill-debugger": {"text": "File: NUL, UTF-16 BOM, lone CR, NEL, LS or PS exits 3; a line setting REQUIRE_SIGNED_DEBUG_REQUESTS to exactly false exits 1. A backslash, !, or $ line not a comment or plain K=${X} or K: ${X:-d}, or a $ with env_file, extends, include or project_directory anywhere in the file, exits 3, as does a naming line not true or 1; else 0. Loaded files and outside values go unread. Not run on a deployment.", "components": ["windmill"], "sources": ["windmill:s6a7eeac413b7", "windmill:s50609ebb7768", "windmill:s05c898fe1013"], "status": "REASONED", "verify": [9]},
    "verify-nocodb-trust-proxy": {"text": "docker exec reads NC_TRUST_PROXY in the container's configured environment: true (any case) or a zero range such as /0 (proxy-addr 2.0.7 rejects it) is the finding (exit 1); unset, empty, false or all zeros exits 0 (no proxy trusted); anything else, such as a hop count or range, exits 3, expected behind a proxy, as the block cannot see if clients reach NocoDB directly. No real container run.", "components": ["nocodb", "docker"], "sources": ["nocodb:s635b35ce4689", "nocodb:sa19c6557b712", "nocodb:se352e8e45038", "nocodb:s1174c56ebb50", "nocodb:s3af21c2530b7", "docker:sd34e76a09f6c"], "status": "REASONED", "verify": [10]},
    "verify-nocodb-cors": {"text": "GET a NocoDB URL through the proxy with Origin: https://evil.example: Allow-Origin * or that origin in the final response's headers is the finding (exit 1), interim 1xx headers not judged; on a 2xx, no Allow-Origin or exactly the allowed origin once passes (0); anything else is inconclusive (3); a missing curl or awk or a refused value exits 2. Not run against a deployment.", "components": ["nocodb", "cors", "curl"], "sources": ["nocodb:s03a119ab46e6", "nocodb:s565f51c5c143", "nocodb:s52f6258ded32", "nocodb:s7fc234b5a058", "cors:s45d81d86a562", "curl:s3db522258e44", "curl:s5e1383feef7d", "curl:s343269d1c01c", "curl:s809185b389c5", "curl:s1222d47e1017", "curl:sdd1aa884c51d", "curl:s40cfe8ffa885", "curl:s820e85aa0636", "curl:sc2e8fc82d74a", "curl:sc103df7ca615"], "status": "REASONED", "verify": [11]}
  }
}
````
<!-- version-basis:end -->
