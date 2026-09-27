---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "5c118a9f2288edac26fb3612182361d5951d9c5e7150c567d87bb3a2167fb468",
  "components": {
    "metabase-docs": {
      "name": "Metabase docs",
      "basis": "unknown",
      "sources": {
        "sefe12b1b495c": "https://www.metabase.com/docs/latest/",
        "s5e2251b3184d": "https://www.metabase.com/docs/latest/configuring-metabase/setting-up-metabase",
        "s521b3063e9f0": "https://www.metabase.com/docs/latest/embedding/public-links",
        "s02b7797b6ffe": "https://www.metabase.com/docs/latest/permissions/data",
        "s434abdb1aaef": "https://www.metabase.com/docs/latest/databases/users-roles-privileges"
      }
    },
    "metabase": {
      "name": "Metabase",
      "basis": "v0.63.18",
      "sources": {
        "s8df4cbf03036": "https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/config/core.clj#L54",
        "s7dbf92797642": "https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/config/core.clj#L76-L88",
        "s7e71ce4cff1b": "https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/server/instance.clj#L36-L41",
        "sed761829c85c": "https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L79",
        "sea59c4ef7f2e": "https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L164",
        "sabe1aa2cf0a9": "https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L195",
        "s18f6f2188fe9": "https://github.com/metabase/metabase/blob/v0.63.18/bin/docker/run_metabase.sh#L2-L5",
        "s9b0c73c666ff": "https://github.com/metabase/metabase/blob/v0.63.18/Dockerfile#L66-L69"
      }
    },
    "environ": {
      "name": "environ",
      "basis": "1.2.0",
      "sources": {
        "s37ed6de2d80d": "https://github.com/weavejester/environ/blob/1.2.0/environ/src/environ/core.cljc#L32-L43",
        "s9754f7c47384": "https://github.com/weavejester/environ/blob/1.2.0/environ/src/environ/core.cljc#L64-L79"
      }
    },
    "ring": {
      "name": "Ring Jetty adapter",
      "basis": "1.15.3",
      "sources": {
        "s0455b1b1fb12": "https://github.com/ring-clojure/ring/blob/1.15.3/ring-jetty-adapter/src/ring/adapter/jetty.clj#L202-L207"
      }
    },
    "jetty": {
      "name": "Jetty",
      "basis": "12.1.13",
      "sources": {
        "s95894f37ac5e": "https://github.com/jetty/jetty.project/blob/jetty-12.1.13/jetty-core/jetty-server/src/main/java/org/eclipse/jetty/server/ServerConnector.java#L338"
      }
    },
    "superset": {
      "name": "Superset docs",
      "basis": "unknown",
      "sources": {
        "se97be7353585": "https://superset.apache.org/admin-docs/security/"
      }
    },
    "superset-compose": {
      "name": "Superset Compose",
      "basis": "3d01094d231712e3470eb625be3f9925aeaeadb5",
      "sources": {
        "s0ceca7af7f79": "https://github.com/apache/superset/blob/3d01094d231712e3470eb625be3f9925aeaeadb5/docker-compose.yml"
      }
    },
    "redash-docs": {
      "name": "Redash docs",
      "basis": "unknown",
      "sources": {
        "s069a74340b65": "https://redash.io/help/",
        "s4c72252b5447": "https://redash.io/help/open-source/setup/",
        "sbaf5b44079a0": "https://redash.io/help/open-source/admin-guide/secrets/"
      }
    },
    "redash": {
      "name": "Redash",
      "basis": "v26.9.0",
      "sources": {
        "se93d7c47b037": "https://github.com/getredash/redash/blob/v26.9.0/bin/docker-entrypoint#L49-L50",
        "s9f1ef7237804": "https://github.com/getredash/redash/blob/v26.9.0/Dockerfile#L133-L134"
      }
    },
    "docker": {
      "name": "Docker publishing",
      "basis": "unknown",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep BI tools private with fronting MFA and least-privilege read-only DB accounts unless write-back is needed.", "components": ["redash-docs", "metabase-docs"], "sources": ["redash-docs:s4c72252b5447", "metabase-docs:s434abdb1aaef"], "status": "REASONED"},
    "metabase-setup": {"text": "First account is admin; finish setup before anyone else can reach it.", "components": ["metabase-docs"], "sources": ["metabase-docs:s5e2251b3184d"], "status": "REASONED"},
    "metabase-precedence": {"text": "Settings merge .lein-env, .boot-env, environment and JVM properties in order; later empty values mask earlier settings.", "components": ["metabase", "environ"], "sources": ["metabase:s8df4cbf03036", "metabase:s7dbf92797642", "environ:s37ed6de2d80d", "environ:s9754f7c47384"], "status": "REASONED"},
    "metabase-bind": {"text": "Final nonblank MB_JETTY_HOST sets the jar host; otherwise Ring passes no host and Jetty binds wildcard. Use loopback behind a local proxy.", "components": ["metabase", "ring", "jetty"], "sources": ["metabase:s7e71ce4cff1b", "metabase:sed761829c85c", "metabase:sea59c4ef7f2e", "metabase:sabe1aa2cf0a9", "ring:s0455b1b1fb12", "jetty:s95894f37ac5e"], "status": "REASONED"},
    "metabase-image": {"text": "Image exports MB_JETTY_HOST=0.0.0.0 when unset/empty; publish 127.0.0.1:3000:3000 before first start.", "components": ["metabase", "docker"], "sources": ["metabase:s18f6f2188fe9", "metabase:s9b0c73c666ff", "docker:s1e53417c513d"], "status": "REASONED"},
    "metabase-port": {"text": "Port defaults 3000 unless the final MB_JETTY_PORT is nonblank.", "components": ["metabase"], "sources": ["metabase:s8df4cbf03036", "metabase:s7dbf92797642", "metabase:s7e71ce4cff1b"], "status": "REASONED"},
    "metabase-sharing": {"text": "Public links/embeds default enabled and expose view-only question/dashboard/document results without login; disable unneeded sharing.", "components": ["metabase-docs"], "sources": ["metabase-docs:s521b3063e9f0"], "status": "REASONED"},
    "metabase-embed": {"text": "Public embed URLs are recoverable; embeds do not strengthen the public-link boundary.", "components": ["metabase-docs"], "sources": ["metabase-docs:s521b3063e9f0"], "status": "REASONED"},
    "metabase-sandbox": {"text": "Row/column security is Pro/Enterprise; free-tier sharing exposes the rows/columns the question queries.", "components": ["metabase-docs"], "sources": ["metabase-docs:s02b7797b6ffe"], "status": "REASONED"},
    "superset-secret": {"text": "Set a unique complex random SECRET_KEY before exposure; it signs session cookies.", "components": ["superset"], "sources": ["superset:se97be7353585"], "status": "REASONED"},
    "superset-admin": {"text": "Replace the first-run admin password before exposure.", "components": ["superset", "superset-compose"], "sources": ["superset:se97be7353585", "superset-compose:s0ceca7af7f79"], "status": "REASONED"},
    "superset-public": {"text": "Absent AUTH_ROLE_PUBLIC does not prove denial; inspect effective Public-role grants, which provide no data access by default.", "components": ["superset"], "sources": ["superset:se97be7353585"], "status": "REASONED"},
    "superset-copy": {"text": "PUBLIC_ROLE_LIKE copies permissions at superset init; broad roles grant access without scoping datasets/dashboards.", "components": ["superset"], "sources": ["superset:se97be7353585"], "status": "REASONED"},
    "superset-compose": {"text": "Example Compose is unsupported for production; use unique passwords/SECRET_KEY, not the example against production data.", "components": ["superset-compose"], "sources": ["superset-compose:s0ceca7af7f79"], "status": "REASONED"},
    "redash-setup": {"text": "Create the first-run admin before others reach setup.", "components": ["redash-docs"], "sources": ["redash-docs:s4c72252b5447"], "status": "REASONED"},
    "redash-https": {"text": "Enforce HTTPS and the private-access pattern.", "components": ["redash-docs"], "sources": ["redash-docs:s4c72252b5447"], "status": "REASONED"},
    "redash-cookie": {"text": "Use an instance-specific REDASH_COOKIE_SECRET; never commit or reuse it.", "components": ["redash-docs"], "sources": ["redash-docs:sbaf5b44079a0"], "status": "REASONED"},
    "redash-encryption": {"text": "REDASH_SECRET_KEY encrypts data-source credentials; use a strong unique value outside version control.", "components": ["redash-docs"], "sources": ["redash-docs:sbaf5b44079a0"], "status": "REASONED"},
    "redash-bind": {"text": "Default image server uses REDASH_GUNICORN_BIND or [::]:5000 when unset/empty; dual-stack may accept IPv4. Bind/publish privately.", "components": ["redash"], "sources": ["redash:se93d7c47b037", "redash:s9f1ef7237804"], "status": "REASONED"},
    "verify-credentials": {"text": "Confirm no default admin/admin or example credentials work.", "components": ["metabase-docs", "superset-compose", "redash-docs"], "sources": ["metabase-docs:s5e2251b3184d", "superset-compose:s0ceca7af7f79", "redash-docs:s4c72252b5447"], "status": "REASONED"},
    "verify-db": {"text": "Inspect effective/inherited DB grants; confirm reads and denied writes on a disposable object; scope needed write-back separately.", "components": ["metabase-docs"], "sources": ["metabase-docs:s434abdb1aaef"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory application/proxy sockets and Docker NAT publications; probe direct origins over IPv4/IPv6/LAN/VPC. Absent ss entries do not prove isolation.", "components": ["metabase", "superset-compose", "redash", "docker"], "sources": ["metabase:s8df4cbf03036", "superset-compose:s0ceca7af7f79", "redash:se93d7c47b037", "docker:s1e53417c513d"], "status": "REASONED", "verify": [1]},
    "verify-ports": {"text": "Verify lists Metabase/Superset/Redash defaults 3000/8088/5000, qualified as install-dependent.", "components": ["metabase", "superset-compose", "redash"], "sources": ["metabase:s8df4cbf03036", "superset-compose:s0ceca7af7f79", "redash:se93d7c47b037"], "status": "REASONED", "verify": [1]},
    "verify-data": {"text": "Authorized data is the control; anonymous data fails. Denial/verified login challenge passes; SPA shells, 404/errors and arbitrary redirects are inconclusive.", "components": ["metabase-docs", "superset", "redash-docs"], "sources": ["metabase-docs:s521b3063e9f0", "superset:se97be7353585", "redash-docs:s4c72252b5447"], "status": "REASONED", "verify": [1]},
    "verify-private": {"text": "For tunnel-only access, confirm public isolation separately and test authorization on the permitted private path.", "components": ["redash-docs", "docker"], "sources": ["redash-docs:s4c72252b5447", "docker:s1e53417c513d"], "status": "REASONED", "verify": [1]}
  }
}
---
# BI dashboards: Metabase, Superset, Redash

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Keep BI tools private with fronting MFA and least-privilege read-only DB accounts unless write-back is needed. | Redash docs unknown; Metabase docs unknown | REASONED |
| metabase-setup: First account is admin; finish setup before anyone else can reach it. | Metabase docs unknown | REASONED |
| metabase-precedence: Settings merge .lein-env, .boot-env, environment and JVM properties in order; later empty values mask earlier settings. | Metabase v0.63.18; environ 1.2.0 | REASONED |
| metabase-bind: Final nonblank MB_JETTY_HOST sets the jar host; otherwise Ring passes no host and Jetty binds wildcard. Use loopback behind a local proxy. | Metabase v0.63.18; Ring Jetty adapter 1.15.3; Jetty 12.1.13 | REASONED |
| metabase-image: Image exports MB_JETTY_HOST=0.0.0.0 when unset/empty; publish 127.0.0.1:3000:3000 before first start. | Metabase v0.63.18; Docker publishing unknown | REASONED |
| metabase-port: Port defaults 3000 unless the final MB_JETTY_PORT is nonblank. | Metabase v0.63.18 | REASONED |
| metabase-sharing: Public links/embeds default enabled and expose view-only question/dashboard/document results without login; disable unneeded sharing. | Metabase docs unknown | REASONED |
| metabase-embed: Public embed URLs are recoverable; embeds do not strengthen the public-link boundary. | Metabase docs unknown | REASONED |
| metabase-sandbox: Row/column security is Pro/Enterprise; free-tier sharing exposes the rows/columns the question queries. | Metabase docs unknown | REASONED |
| superset-secret: Set a unique complex random SECRET_KEY before exposure; it signs session cookies. | Superset docs unknown | REASONED |
| superset-admin: Replace the first-run admin password before exposure. | Superset docs unknown; Superset Compose 3d01094d231712e3470eb625be3f9925aeaeadb5 | REASONED |
| superset-public: Absent AUTH_ROLE_PUBLIC does not prove denial; inspect effective Public-role grants, which provide no data access by default. | Superset docs unknown | REASONED |
| superset-copy: PUBLIC_ROLE_LIKE copies permissions at superset init; broad roles grant access without scoping datasets/dashboards. | Superset docs unknown | REASONED |
| superset-compose: Example Compose is unsupported for production; use unique passwords/SECRET_KEY, not the example against production data. | Superset Compose 3d01094d231712e3470eb625be3f9925aeaeadb5 | REASONED |
| redash-setup: Create the first-run admin before others reach setup. | Redash docs unknown | REASONED |
| redash-https: Enforce HTTPS and the private-access pattern. | Redash docs unknown | REASONED |
| redash-cookie: Use an instance-specific REDASH_COOKIE_SECRET; never commit or reuse it. | Redash docs unknown | REASONED |
| redash-encryption: REDASH_SECRET_KEY encrypts data-source credentials; use a strong unique value outside version control. | Redash docs unknown | REASONED |
| redash-bind: Default image server uses REDASH_GUNICORN_BIND or [::]:5000 when unset/empty; dual-stack may accept IPv4. Bind/publish privately. | Redash v26.9.0 | REASONED |
| verify-credentials: Confirm no default admin/admin or example credentials work. | Metabase docs unknown; Superset Compose 3d01094d231712e3470eb625be3f9925aeaeadb5; Redash docs unknown | REASONED |
| verify-db: Inspect effective/inherited DB grants; confirm reads and denied writes on a disposable object; scope needed write-back separately. | Metabase docs unknown | REASONED |
| verify-listeners: Inventory application/proxy sockets and Docker NAT publications; probe direct origins over IPv4/IPv6/LAN/VPC. Absent ss entries do not prove isolation. | Metabase v0.63.18; Superset Compose 3d01094d231712e3470eb625be3f9925aeaeadb5; Redash v26.9.0; Docker publishing unknown | REASONED |
| verify-ports: Verify lists Metabase/Superset/Redash defaults 3000/8088/5000, qualified as install-dependent. | Metabase v0.63.18; Superset Compose 3d01094d231712e3470eb625be3f9925aeaeadb5; Redash v26.9.0 | REASONED |
| verify-data: Authorized data is the control; anonymous data fails. Denial/verified login challenge passes; SPA shells, 404/errors and arbitrary redirects are inconclusive. | Metabase docs unknown; Superset docs unknown; Redash docs unknown | REASONED |
| verify-private: For tunnel-only access, confirm public isolation separately and test authorization on the permitted private path. | Redash docs unknown; Docker publishing unknown | REASONED |
<!-- version-basis:end -->

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

Metabase binds a wildcard address by default (as of v0.63.18). It reads each `MB_` setting
from a `.lein-env` file in the working directory (and a `.boot-env` classpath resource), then the
environment, then JVM options such as `-Dmb.jetty.host`, each overriding the one before. The jar
leaves Jetty's host unset unless the last of those layers to set `MB_JETTY_HOST` gives it a non-blank
value (an empty value in a later layer masks an address in an earlier one), and Jetty binds the
wildcard address when no host is set; the official image's entrypoint instead exports
`MB_JETTY_HOST=0.0.0.0`, every IPv4 address, whenever the variable is unset or empty. The port is
3000 unless the last layer to set `MB_JETTY_PORT` gives it a non-blank value. For a jar behind a
local proxy set
`MB_JETTY_HOST=127.0.0.1`, and in Docker publish only to host loopback (`127.0.0.1:3000:3000`),
before the first start.

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

Redash's `server` command, which the official image runs by default, binds gunicorn to
`REDASH_GUNICORN_BIND`, or to `[::]:5000`, the IPv6 wildcard (which may also accept IPv4 on a dual-stack host), when that variable is unset or empty
(as of v26.9.0). Behind a local proxy set `REDASH_GUNICORN_BIND=127.0.0.1:5000`; in Docker, publish
only to host loopback.

## Verify

First, with valid authorization, confirm your chosen protected route returns actual dashboard DATA (a
real data or API route, not the SPA HTML shell or a health endpoint): that is the positive control.
Then, from OUTSIDE your network with no cookies, tokens, or Access credentials, run the whole block
(substitute inside the quotes):

REASONED: following block; Metabase, Superset, Redash and Docker sources below support socket/publication and anonymous data-route checks. No BI deployment or external test network is available here; no live run is recorded. Expected exposed, denied and inconclusive outcomes surround the block.

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
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute both URLs on the set -- line above; not probing"; exit; fi
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
- Metabase Jetty host and port (`:mb-jetty-port` default "3000", no host default, blank values treated as unset, nil values dropped from the Jetty options), ring-jetty-adapter 1.15.3 passing the host to `setHost`, Jetty 12.1.13 binding the wildcard address for a null host, environ 1.2.0 merging `.lein-env`, `.boot-env`, the environment and JVM properties in that order, keeping empty values, so the last layer to set a key wins, and the image entrypoint's `MB_JETTY_HOST=0.0.0.0` default (pinned tags v0.63.18, ring 1.15.3, jetty-12.1.13, environ 1.2.0): https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/config/core.clj#L54, https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/config/core.clj#L76-L88, https://github.com/metabase/metabase/blob/v0.63.18/src/metabase/server/instance.clj#L36-L41, https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L79, https://github.com/weavejester/environ/blob/1.2.0/environ/src/environ/core.cljc#L32-L43, https://github.com/weavejester/environ/blob/1.2.0/environ/src/environ/core.cljc#L64-L79, https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L164, https://github.com/metabase/metabase/blob/v0.63.18/deps.edn#L195, https://github.com/ring-clojure/ring/blob/1.15.3/ring-jetty-adapter/src/ring/adapter/jetty.clj#L202-L207, https://github.com/jetty/jetty.project/blob/jetty-12.1.13/jetty-core/jetty-server/src/main/java/org/eclipse/jetty/server/ServerConnector.java#L338, https://github.com/metabase/metabase/blob/v0.63.18/bin/docker/run_metabase.sh#L2-L5 and https://github.com/metabase/metabase/blob/v0.63.18/Dockerfile#L66-L69
- Superset security: https://superset.apache.org/admin-docs/security/
- Superset docker-compose.yml (production warning): https://github.com/apache/superset/blob/3d01094d231712e3470eb625be3f9925aeaeadb5/docker-compose.yml
- Redash help center: https://redash.io/help/
- Redash setting up a Redash instance: https://redash.io/help/open-source/setup/
- Redash `server` binding gunicorn to `${REDASH_GUNICORN_BIND:-[::]:5000}`, and the image's default `server` command (pinned tag v26.9.0): https://github.com/getredash/redash/blob/v26.9.0/bin/docker-entrypoint#L49-L50 and https://github.com/getredash/redash/blob/v26.9.0/Dockerfile#L133-L134
- Redash secret keys (cookie signing, data-source-credential encryption, do not reuse across instances or commit): https://redash.io/help/open-source/admin-guide/secrets/
- Metabase database users, roles, and privileges (a dedicated least-privilege read-only account): https://www.metabase.com/docs/latest/databases/users-roles-privileges
- Docker port publishing (a published container port is served through NAT/forwarding rules, so the host may show no matching listener): https://docs.docker.com/engine/network/port-publishing/
