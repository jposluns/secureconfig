# SQLite HTTP front-ends: Datasette and sqlite-web

An SQLite HTTP front-end turns a local file into a network service: **the port is the exposure**. Datasette allows anonymous browsing and read-only SQL by default; sqlite-web provides queries, imports, exports, row changes, and schema deletion. An unprotected, reachable instance exposes those capabilities. See Datasette permissions and sqlite-web features.

A reachable, unauthenticated, writable sqlite-web instance therefore permits compromise of the databases its process can modify. That is an inference from its documented capabilities, not a claim of automatic host compromise.

Use [sqlite.md](sqlite.md) for the files at rest and [web-exposure.md](web-exposure.md) for accidental file publication. Application-level SQL injection is outside this guide's scope; see the OWASP SQL Injection Prevention Cheat Sheet.

## Datasette

At the time of writing, the stable documentation lists 0.65.5, including a fix for a table-permission bypass. Use a supported release containing the security fixes; check the changelog when deploying.

**Bind privately and inspect the deployment path.** Bare `datasette` invokes `serve`, whose defaults are `127.0.0.1:8001`; `-h/--host` and `-p/--port` override them. The following baseline serves an unchanging snapshot on loopback, disables arbitrary SQL by default, and disables whole-file downloads. The pathname is an example. See the CLI reference and settings reference.

```bash
datasette serve \
  --host 127.0.0.1 --port 8001 \
  --immutable /var/lib/sqlite-http/published.db \
  --setting default_allow_sql off \
  --setting allow_download off
```

Use `--immutable` only when the file will remain unchanged while served. SQLite skips locking and change detection in immutable mode; changing the file can produce incorrect results or corruption errors. A live database written by another process does not meet that condition. See Datasette immutable mode and SQLite URI semantics.

Packaging can widen exposure:

- Datasette's documented Docker command binds `0.0.0.0:8001` inside the container and publishes `8001:8001`. Container binding and host publication are separate decisions.
- The inspected `make_dockerfile()` implementation selects `--host 0.0.0.0`, immutable database arguments, `--cors`, and `--port $PORT`. Review the generated command, not just its bind address.
- The inspected Cloud Run publisher uses `--allow-unauthenticated`. Cloud Run requires its ingress container to listen on `0.0.0.0`, supplies `PORT` with an ingress default of 8080, and terminates external TLS. That platform requirement does not supply application authorization.
- Review each `datasette-publish-*` plugin as another exposure path. For example, `datasette-publish-fly` documents an application hostname under `app.fly.dev`. No universal authentication default across publishing plugins was established.

Docker publishes to all host addresses by default when the mapping omits an address. For a proxy on the Docker host, use a mapping such as `-p 127.0.0.1:8001:8001`. Check direct routing and Docker's documented pre-28.0.0 localhost-publication caveat too; verify the resulting reachability.

**Configure authentication and authorization.** Requests have an actor; permissions decide what it may access. Metadata `allow` blocks cover instances, databases, tables, and canned queries. Authentication alone does not establish those restrictions.

Authentication plugins include datasette-auth-passwords and datasette-auth-github. The latter explicitly documents that anonymous access remains possible until permissions restrict it.

This illustrative metadata permits actor `analyst` and disables arbitrary SQL. It is authorization configuration, not a user database. Save it as `metadata.json` and add `--metadata metadata.json` to the launch command.

```json
{
  "allow": {"id": ["analyst"]},
  "allow_sql": false
}
```

`datasette --root` prints a one-use login URL that establishes the root actor through a cookie. It does not close anonymous access. Treat that URL as a credential per [secrets.md](secrets.md).

**Review every write capability.** The ordinary SQL interface is read-only. Writable canned queries use `"write": true`; plugins can provide further writes, rather than a global write mode.

For example, `datasette-write` adds `/db/-/write`, governed by the `datasette-write` permission and restricted to root by default. Installing it does not grant anonymous writes. Review other mutable plugins individually.

**Restrict SQL and exports separately.** The `?sql=` interface and its `.json?sql=` form expose arbitrary read queries. Read-only access still discloses data.

Table and view `allow` restrictions do not prevent arbitrary SQL from reading those objects; restrict SQL alongside table access. Metadata `allow_sql` can express actor-specific policy.

`--setting default_allow_sql off` changes the default `execute-sql` decision. There is no generic `--setting permissions` option in the stable settings reference.

Queries default to a one-second time limit and at most 1,000 returned rows at a time. Pagination can retrieve further rows, so the row limit is not a confidentiality boundary. Repeated expensive requests may still consume resources; that is an inference, not a demonstrated denial of service.

`allow_download` defaults on for immutable, file-backed databases. Make an explicit download decision when using `--immutable`; `--setting allow_download off` disables whole-file downloads, not ordinary data exports.

**Review browser-facing and auxiliary routes.** `--cors` adds `Access-Control-Allow-Origin: *` to JSON endpoints. Omit it unless cross-origin access is intended; its absence does not authenticate requests. Remember that the generated Dockerfile adds it.

`/-/metadata`, `/-/plugins`, `/-/versions`, `/-/settings`, and `/-/databases`, including their `.json` forms, expose configuration or instance details. Review them explicitly. The permissions debugger is separately restricted to root or an actor granted its permission; "internal" is not one access class.

Core `hash_urls` was removed in 0.61. Its replacement, `datasette-hashed-urls`, provides content-hash URLs for caching, not secrecy or authorization; omit it from this private-data baseline.

Datasette uses `asgi-csrf`, comparing the `ds_csrftoken` cookie with a `csrftoken` form field or `x-csrftoken` header. Preserve that protection for write-capable routes and review plugins using `skip_csrf`. It does not restrict anonymous reads.

Keep plugin secrets out of public metadata through the documented environment or file indirection. Handle root login URLs and credential files per [secrets.md](secrets.md).

## sqlite-web

At the time of writing, sqlite-web defaults to `127.0.0.1:8080`. Overrides are `-H/--host`, with uppercase `H`, and `-p/--port`. Its UI supports arbitrary queries, imports and exports, row insert/update/delete, and dropping schema objects.

The project Dockerfile starts with `-H 0.0.0.0` and exposes 8080; the README publishes `8080:8080`. For a proxy on the Docker host, use an explicit loopback publication such as `-p 127.0.0.1:8080:8080`, then verify it externally.

Authentication requires a nonempty password. `-P/--password` prompts; the inspected implementation reads `SQLITE_WEB_PASSWORD` only inside that option's branch. The environment variable alone therefore does not enable authentication in this source. The browser login uses one shared password, without per-table roles.

For the shared proxy-authentication pattern below:

```bash
sqlite_web \
  --host 127.0.0.1 --port 8080 \
  --read-only /var/lib/sqlite-http/published.db
```

`--read-only` opens the database using SQLite `mode=ro`. It reduces exposure to reads; it does not authenticate callers. The path is an example.

The inspected query handler executes a read through GET, while writes and scripts require POST; the drop handler also deletes through POST. Use a harmless read GET to establish anonymous access.

sqlite-web documents native TLS through `--ssl-cert` and `--ssl-key`; the recommended deployment here still uses the shared TLS proxy.

sqlite-web 0.8.1 from PyPI showed no CSRF check on its insert route on loopback: an authenticated `POST` insert with no token and a foreign `Origin` header wrote a row, and the insert form contains no CSRF field. Its session cookie was set with `HttpOnly; Path=/` and no `SameSite` or `Secure` attribute, even over TLS, so whether a browser sends it on a cross-site request depends on that browser's default. Prefer `--read-only` behind the proxy. The flags and routes described here matched the installed 0.8.1 package for everything the loopback runs exercised.

## Fronting layer, TLS, and least privilege

For a same-host deployment, keep both origins on loopback and put the complete application behind TLS and authentication. Datasette documents reverse-proxy deployment. Follow [nginx.md](nginx.md) or [caddy.md](caddy.md), applying Basic authentication to every route, including SQL, JSON, exports, downloads, and auxiliary paths. See Datasette proxy deployment, nginx HTTPS, nginx Basic authentication, and Caddy Basic authentication.

For human access, use an identity-aware proxy: [cloud-identity-proxies.md](cloud-identity-proxies.md) covers Google IAP and [cloudflare.md](cloudflare.md) covers Cloudflare Access. Both evaluate access before forwarding requests.

Neither core tool supplies native MFA in the reviewed authentication interfaces. Enforce MFA at the identity provider per [mfa.md](mfa.md), or through Cloudflare Access independent MFA.

For private access, see [tailscale.md](tailscale.md). Serve shares within the tailnet; Funnel publishes to the internet. Verify which is configured.

A proxy login must not be bypassable through another published origin or provider hostname. Inventory and test those paths separately; IAP specifically documents direct-backend and Cloud Run hostname bypass precautions.

Run the service under a dedicated unprivileged OS account with access only to the intended databases. Prefer a curated snapshot whose file and parent directory the serving account cannot modify. This recommendation follows from SQLite's direct filesystem access and its warning about files writable across security boundaries. Reuse [sqlite.md](sqlite.md) section 3 for permissions, sidecars, and temporary files, adapting ownership for a read-only serving account.

## Verify

The service outcomes below were **demonstrated on loopback** against Datasette 0.65.5 (with datasette-auth-passwords 1.1.1 and datasette-write 0.4) and sqlite-web 0.8.1, installed from PyPI into a virtual environment, with every server on 127.0.0.1 and, for the HTTPS blocks, native TLS or a Caddy TLS proxy with certificates from a private test CA that curl trusted through `CURL_CA_BUNDLE`. Blocks B and C ran as printed with only their placeholders substituted. What those runs do not show is marked **REASONED** where it occurs, with its reason; backlog row 1.118 tracks it.

Use Bash with real, unshadowed builtins and curl 7.75.0 or newer. Paste whole subshells and substitute inside the single quotes. A literal apostrophe requires proper shell escaping; do not simply paste it between those quotes. Use URLs without embedded credentials or signed tokens. Every curl begins with `-q -g`, disables environment proxies, and reports the error text. Do not add `-k` or redirect-following.

### A. Listener inventory

**The fixed bind demonstrated on loopback; a wildcard bind and container publications REASONED** (the host forbids binding every interface and has no container runtime). On the deployment host, inspect the complete listener table:

```bash
sudo ss -tlnp
```

For the same-host examples, expect `127.0.0.1:8001` and/or `127.0.0.1:8080`, owned by the intended processes. A wildcard origin bind is the finding. Read IPv6 entries and unexpected ports too. An inspection error followed by an empty table is inconclusive. These example ports match the documented CLI defaults; substitute the actual configured ports when testing. On loopback, bare `datasette serve` with no host or port flag listened on `127.0.0.1:8001` and bare `sqlite_web` on `127.0.0.1:8080`, as `ss -tlnp` run without `sudo` by the same account showed (the authoring host has no `sudo`).

Inspect container publications separately: Docker forwarding can expose a port without a corresponding host listening process. A wildcard bind inside a container is distinct from a public host publication; managed ingress such as Cloud Run also has its own binding contract. Confirm those boundaries through configuration and external probes.

### B. Direct reachability and anonymous access

**Demonstrated on loopback against both tools; an external vantage and provider hostnames REASONED** (the host has no second network and no provider deployment). The same-host reverse proxy was demonstrated with Caddy (section C); identity-aware-proxy routes are REASONED, since no IAP or Cloudflare Access tenancy was available.

First obtain a successful local control against the running backend. Then run the block from an authorized external testing host against each direct origin and provider hostname, followed by the published HTTPS routes. For a protected route, establish section C's authorized positive control first. Use disposable databases for any local exposed-state reproduction.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTP_OR_HTTPS_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'exactly one URL required; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*YOUR_PUBLIC_IP*) echo 'substitute the target URL; not probing'; exit 2 ;;
  esac
  case "$1" in http://?*|https://?*) ;; *) echo 'HTTP or HTTPS required; not probing'; exit 2 ;; esac
  case "$1" in *@*|*[[:cntrl:]]*) echo 'userinfo or control character rejected; not probing'; exit 2 ;; esac
  curl -q -g -sS -i --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --url "$1"
)
```

For a disposable `published.db` containing at least one table, these are local control examples:

| Tool | UI | Read query |
|---|---|---|
| Datasette | `http://127.0.0.1:8001/` | `http://127.0.0.1:8001/published.json?sql=SELECT+name+FROM+sqlite_master+LIMIT+1` |
| sqlite-web | `http://127.0.0.1:8080/` | `http://127.0.0.1:8080/query/?sql=SELECT+name+FROM+sqlite_master+LIMIT+1` |

Datasette's query and JSON interfaces are documented; sqlite-web's GET route was traced to the inspected source and confirmed for the 0.8.1 package on loopback.

For external testing, replace loopback with the actual deployment address, port, and path. Loopback on the testing machine cannot test the server's external exposure. Interpret the results as follows:

- **Reachability:** any HTTP response from a direct origin, including 401, 403, or 404, proves that path answered. A loopback-only origin should not answer externally. Refusal or timeout supports isolation only after confirming the target and a successful local control; DNS, TLS, and local socket errors are inconclusive.
- **Anonymous exposure:** a bare GET of the UI, a `?sql=` route, or a `.json` route returns a database listing, schema result, or protected rows without credentials. That is the finding. The schema query reveals a name; repeat with a known nonsensitive row endpoint to check row access.
- **Fixed:** a denial or the configured login redirect returns no protected data. A 200 login page is not query success, and an unexplained 404 does not prove authentication.
- **SQL disabled:** an authorized browsing account still reaches its permitted table page but receives no SQL result. Check that browsing positive control separately.
- **Proxy-only authentication (demonstrated with Caddy; see section C):** a loopback backend may intentionally return data without credentials. Exposure exists when an untrusted caller reaches it or bypasses the proxy.

On loopback, block B against bare `datasette serve` returned the database listing, and the SQL JSON route returned the known row (`widget-canary`), both with `200`, and `/-/versions.json` answered `200` anonymously: the exposed state. Against the baseline command above, the SQL JSON route returned `403` while the table's JSON page still returned `200` (SQL disabled, browsing permitted), and `/published.db` returned `403`; without `--setting allow_download off` it returned `200`. `--cors` added `Access-Control-Allow-Origin: *`, absent without it. Bare `sqlite_web` answered the query GET with `200` anonymously, and an anonymous `POST` insert wrote a row to a disposable database; with `--read-only` the read still returned `200` and the insert changed nothing. `SQLITE_WEB_PASSWORD` set without `-P` left sqlite-web open (`200` anonymously), as the source reading above says; with `-P` the anonymous query GET got `302` to `/login/`.

### C. Authorized positive control versus anonymous access

**Demonstrated on loopback over native TLS; the same-host proxy demonstrated with Caddy; identity-aware-proxy headers REASONED, since no IAP or Cloudflare Access tenancy was available.**

Prepare a private mode-0600 header file per [secrets.md](secrets.md), containing the required Authorization, session Cookie, or fronting-layer headers. Only its path enters argv through `-H "@file"`. Keep credentials out of the URL, shell history, tracing, and shared output. The guard checks that the file is readable and regular; preparation must establish its privacy.

Choose a URL that returns known nonsensitive protected data. When arbitrary SQL is disabled, use a permitted table page or its JSON representation.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_DATA_URL' 'REPLACE_WITH_AUTH_HEADER_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'exactly one URL and one file required; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the data URL; not probing'; exit 2 ;; esac
  case "$1" in https://?*) ;; *) echo 'HTTPS required; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*) echo 'substitute the header file; not probing'; exit 2 ;; esac
  case "$1" in *@*) echo 'userinfo rejected; not probing'; exit 2 ;; esac
  case "$1$2" in *[[:cntrl:]]*) echo 'control character rejected; not probing'; exit 2 ;; esac
  [ -f "$2" ] || { echo 'regular header file required; not probing'; exit 2; }
  [ -r "$2" ] || { echo 'readable header file required; not probing'; exit 2; }

  curl -q -g -sS -i --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H "@$2" -w '\nauthorized http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --url "$1"
  curl -q -g -sS -i --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nanonymous http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --url "$1"
)
```

The authorized response must contain the expected data; HTTP success alone is insufficient. Only then assess whether the anonymous response withholds that result. If the control fails, the comparison is inconclusive. Repeat with an authenticated but unauthorized account where actor permissions apply.

On loopback, with the metadata above plus datasette-auth-passwords, the block returned the table's rows to the `analyst` session cookie (`authorized http=200`) and `403` anonymously; an authenticated `guest` got `403`, the unauthorized outcome, and the analyst got `403` on SQL under `allow_sql: false`. For sqlite-web with `-P`, the session cookie got the row with `200` and the anonymous request `302` to `/login/`. With datasette-write on a disposable database, an anonymous write got `403`, a root write without the CSRF token `403`, and with the token `302`, and the row was written. Under the same metadata, `/-/versions.json`, `/-/metadata.json`, `/-/plugins.json`, `/-/settings.json` and `/-/databases.json` returned `403` anonymously and `200` to a freshly logged-in analyst, and `/-/metadata.json` showed that analyst both users' password hashes when they were written inline in the plugin configuration, but only the `$env` references when they were supplied through environment variables.

Behind Caddy v2.11.4 (the release tarball, its SHA-256 equal to GitHub's published digest) on `127.0.0.1:8443` with `bind 127.0.0.1`, `auto_https off`, the admin API off and TLS files from the test CA, with [caddy.md](caddy.md)'s `basic_auth` in front of a Datasette that had no authentication of its own, `/`, the SQL JSON route, `/published.db`, `/-/versions.json` and `/published/items.csv` returned `401` anonymously and `200` with the Basic credential, while the loopback backend answered each of them directly with `200`: the proxy-only pattern, safe only while nothing untrusted reaches the backend. Block C through the proxy gave `authorized http=200` with the rows and `anonymous http=401` with `www-authenticate: Basic realm="restricted"`.

Local authoring checks passed: `bash -n` on all five shell blocks, parsing of the metadata JSON, and 120 guard executions covering 40 cases under ordinary Bash, `set -u`, and `set -u` with `IFS=0`. The cases included missing assignments or markers, shortened and extra arguments, embedded placeholders, invalid schemes, URL userinfo, control characters, invalid header-file paths, and valid argument forwarding. An isolated curl argument recorder measured guard behavior; the HTTP outcomes above were demonstrated separately on loopback.

Partial pastes beginning below the guards remain unguarded. An inherited marker with exactly the expected arguments is indistinguishable from a complete assignment. Paste whole blocks; these checks do not claim otherwise.

**Verification debt:** backlog row 1.118 tracks what the loopback runs could not show: a wildcard bind and container publications, an external vantage against direct origins and provider hostnames, the identity-aware-proxy pattern, and `ss` run as root.

## Sources (checked September 2026)

Applicability checked on 2026-09-18: Datasette stable documentation lists 0.65.5; Datasette packaging source was inspected on moving `main`. sqlite-web source was inspected on moving `master`, identifying itself as 0.8.1; the released 0.8.1 package matched it for the flags and routes the loopback runs exercised. Runtime confirmation used Datasette 0.65.5, datasette-auth-passwords 1.1.1, datasette-write 0.4 and sqlite-web 0.8.1 from PyPI.

Every URL listed below was fetched during authoring. This list also records the source-fetch review.

- Datasette CLI reference: https://docs.datasette.io/en/stable/cli-reference.html
- Datasette authentication and permissions: https://docs.datasette.io/en/stable/authentication.html
- Datasette settings: https://docs.datasette.io/en/stable/settings.html
- Datasette SQL queries and writable canned queries: https://docs.datasette.io/en/stable/sql_queries.html
- Datasette JSON API and CORS: https://docs.datasette.io/en/stable/json_api.html
- Datasette introspection routes: https://docs.datasette.io/en/stable/introspection.html
- Datasette Docker installation: https://docs.datasette.io/en/stable/installation.html
- Datasette proxy deployment: https://docs.datasette.io/en/stable/deploying.html
- Datasette publishing: https://docs.datasette.io/en/stable/publish.html
- Datasette container generator: https://raw.githubusercontent.com/simonw/datasette/caf238aac86ebe370959b25384d6e05f6a1e2359/datasette/utils/__init__.py
- Datasette Cloud Run publisher: https://github.com/simonw/datasette/blob/e889403d3bbe143854262682161c98a57bdb6594/datasette/publish/cloudrun.py
- Datasette Fly publishing plugin: https://github.com/simonw/datasette-publish-fly
- Datasette immutable mode and hashed URLs: https://docs.datasette.io/en/stable/performance.html
- Datasette CSRF protection: https://docs.datasette.io/en/stable/internals.html#csrf-protection
- Datasette plugin secret configuration: https://docs.datasette.io/en/stable/plugins.html#secret-configuration-values
- Datasette changelog and security fixes: https://docs.datasette.io/en/stable/changelog.html
- Datasette password authentication plugin: https://github.com/simonw/datasette-auth-passwords
- Datasette GitHub authentication plugin: https://github.com/simonw/datasette-auth-github
- Datasette write plugin: https://github.com/simonw/datasette-write
- sqlite-web README, features, options, and Docker usage: https://github.com/coleifer/sqlite-web
- sqlite-web implementation: https://raw.githubusercontent.com/coleifer/sqlite-web/825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2/sqlite_web/sqlite_web.py
- sqlite-web Dockerfile: https://raw.githubusercontent.com/coleifer/sqlite-web/7f6658b012a789f0b9418cad543e7798ce850130/docker/Dockerfile
- SQLite security: https://www.sqlite.org/security.html
- SQLite serverless architecture and filesystem access: https://www.sqlite.org/serverless.html
- SQLite URI semantics: https://www.sqlite.org/uri.html
- Docker port publishing: https://docs.docker.com/engine/network/port-publishing/
- Cloud Run container contract: https://docs.cloud.google.com/run/docs/container-contract
- nginx HTTPS configuration: https://nginx.org/en/docs/http/configuring_https_servers.html
- nginx Basic authentication: https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
- Caddy Basic authentication: https://caddyserver.com/docs/caddyfile/directives/basic_auth
- Google IAP overview and origin protection: https://docs.cloud.google.com/iap/docs/concepts-overview
- Cloudflare Access HTTP applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/
- Cloudflare independent MFA: https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/independent-mfa/
- Tailscale Serve and Funnel distinction: https://tailscale.com/docs/reference/tailscale-cli/serve
- curl manual: https://curl.se/docs/manpage.html
- ss manual: https://man7.org/linux/man-pages/man8/ss.8.html
- OWASP SQL injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
