# BI dashboards: Metabase, Superset, Redash

These tools hold live connections to your production databases and cache query results in their own
storage. An exposed instance, or one still running default or example credentials, leaks both the
dashboards themselves and the databases behind them. One rule dominates everything tool-specific
below, the same as [admin-uis.md](admin-uis.md): **never public.** Reach it over SSH port
forwarding, a tailnet ([tailscale.md](tailscale.md)), or Cloudflare Access ([cloudflare.md](cloudflare.md)),
with MFA enforced at that fronting layer ([mfa.md](mfa.md)), and connect it to the database with a
least-privilege, read-only account wherever the dashboards do not need to write back.

## Metabase

The first account created during setup becomes the admin account, so an instance reachable on the
network before you finish the setup wizard lets whoever gets there first claim admin. Complete
setup before the instance is reachable from anywhere but you.

Public links and public embeds are enabled by default and let admins share a question, dashboard,
or document with anyone holding the URL; visitors get view-only results with no login. Metabase's
own docs warn that the public link URL is recoverable from a public embed, so an embed is not a
stronger boundary than a plain public link. Row and column security (per-user sandboxing of the
underlying data) is a Pro/Enterprise feature, not available on the open-source edition, so on the
free tier a public link or a shared question exposes whatever rows and columns the question already
queries. Disable public sharing in Admin Settings unless you specifically need it, and treat every
public link as a permanent, unauthenticated data release.

## Apache Superset

Superset ships a `SECRET_KEY` that signs session cookies; its own docs call it "very important to
keep the `SECRET_KEY` secret and set to a secure unique complex random value." Set it, and change
the admin password created at first run, before the instance is reachable by anyone else. Do not treat `AUTH_ROLE_PUBLIC` being absent from your config as proof that anonymous access is off;
confirm it from the effective Public-role permissions instead. What keeps anonymous visitors out of
your data is that the Public role grants no data access by default (Superset:
"Data access is still required by default"), so inspect that role and remove any anonymous dashboard
or dataset grants. `PUBLIC_ROLE_LIKE` copies another role's permissions to Public at `superset init`
(choosing a broad role such as `Gamma` grants access rather than restricting it), and it does not
scope access to particular datasets or dashboards, which stay separately controlled. Superset's own `docker-compose.yml` states
plainly that the stack is not supported for production and that a real deployment needs its own
environment file with unique passwords and `SECRET_KEY`; do not run the example or dev compose file
against a production database.

## Redash

Setup creates the admin account on first run: "it will ask you to create your admin account. Once
this is done, you can start using Redash." Redash's own setup guidance calls out both HTTPS and its signing secrets as things you must set:
"If this is a production setup, you should enforce HTTPS and make sure you set the cookie secret."
For a manual deployment set a strong, instance-specific `REDASH_COOKIE_SECRET` and
`REDASH_SECRET_KEY` (the latter encrypts stored data-source credentials), keep them out of version
control, and never reuse them across instances. Front it the same as the other tools here rather than
relying on anything Redash provides natively.

## Verify

First, with valid authorization, confirm your chosen protected route returns actual dashboard DATA (a
real data or API route, not the SPA HTML shell or a health endpoint): that is the positive control.
Then, from OUTSIDE your network with no cookies, tokens, or Access credentials, run the whole block
(substitute inside the quotes):

```bash
ss -tlnp   # every application AND proxy listener; Metabase/Superset/Redash default to 3000/8088/5000 (ports
           # vary by install). ss shows host listeners, not Docker's NAT: for a container also inspect the
           # published address/port and the forwarding rules, and probe each direct origin and backend port
           # from another host (IPv4, IPv6, LAN/VPC); absence from ss is not proof of isolation.
(
  set -- PASTE_WHOLE_BLOCK \
    'https://REPLACE_WITH_BI_HOST/' \
    'https://REPLACE_WITH_BI_HOST/REPLACE_WITH_KNOWN_PROTECTED_ROUTE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  [ -n "$1" ] && [ -n "$2" ] || { echo "substitute both URLs on the set -- line above; not probing"; exit; }
  case "$1$2" in
    *REPLACE_WITH_*|*example.com*) echo "substitute your own URLs on the set -- line above; not probing"; exit ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -i "$1"   # the tool's front page
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -i "$2"   # a known protected route
)
```

Accept an access denial from WHATEVER protects the route (the tool's or the reverse proxy's 401/403,
a Cloudflare Access challenge, or a verified redirect into that login layer), not only the tool's own
denial. Read the body, not just the status: a 200 login page or SPA shell proves nothing, and an
arbitrary redirect is inconclusive; the protected route returning dashboard data with no
authorization is a fail, and a 404, server error, or DNS/TLS/proxy error is inconclusive. For an
SSH-forward or tailnet-only deployment the public URL is unreachable by design, so confirm network
isolation separately and test the tool's own authorization over the permitted private path.

Also confirm no default `admin/admin` or example credentials still work, and that the database
principal each data source uses is genuinely least-privilege: identify the actual DB role, inspect
its EFFECTIVE grants and inherited roles at the database (a role named `readonly` can still hold
write, ownership, or admin privileges), confirm reads work while writes are denied (test with a
disposable object), and keep any needed write-back access separately scoped. Checking only the
connection string or the tool's own login is not enough.

## Sources (checked September 2026)

- Metabase documentation home: https://www.metabase.com/docs/latest/
- Metabase setting up Metabase (first account is admin): https://www.metabase.com/docs/latest/configuring-metabase/setting-up-metabase
- Metabase public links and embeds: https://www.metabase.com/docs/latest/embedding/public-links
- Metabase data permissions (row and column security is Pro/Enterprise): https://www.metabase.com/docs/latest/permissions/data
- Superset security: https://superset.apache.org/admin-docs/security/
- Superset docker-compose.yml (production warning): https://github.com/apache/superset/blob/master/docker-compose.yml
- Redash help center: https://redash.io/help/
- Redash setting up a Redash instance: https://redash.io/help/open-source/setup/
- Redash secret keys (cookie signing, data-source-credential encryption, do not reuse across instances or commit): https://redash.io/help/open-source/admin-guide/secrets/
- Metabase database users, roles, and privileges (a dedicated least-privilege read-only account): https://www.metabase.com/docs/latest/databases/users-roles-privileges
- Docker port publishing (a published container port is served through NAT/forwarding rules, so the host may show no matching listener): https://docs.docker.com/engine/network/port-publishing/
