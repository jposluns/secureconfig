---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "dbceaded521127743160805024b564c305e59f8e94a4a0385ef059ca2c8b8c72",
  "components": {
    "ds-container": {
      "name": "Datasette container generator",
      "basis": "caf238aac86ebe370959b25384d6e05f6a1e2359",
      "sources": {
        "s3c9be24424e0": "https://raw.githubusercontent.com/simonw/datasette/caf238aac86ebe370959b25384d6e05f6a1e2359/datasette/utils/__init__.py"
      }
    },
    "ds-cloud": {
      "name": "Datasette Cloud Run publisher",
      "basis": "e889403d3bbe143854262682161c98a57bdb6594",
      "sources": {
        "sf5859249ea9f": "https://github.com/simonw/datasette/blob/e889403d3bbe143854262682161c98a57bdb6594/datasette/publish/cloudrun.py"
      }
    },
    "fly": {
      "name": "Datasette Fly publishing plugin",
      "basis": "unknown",
      "sources": {
        "s2a2db4192225": "https://github.com/simonw/datasette-publish-fly"
      }
    },
    "passwords": {
      "name": "datasette-auth-passwords",
      "basis": "1.1.1",
      "sources": {
        "sb6597be5af67": "https://github.com/simonw/datasette-auth-passwords/blob/1.1.1/README.md"
      }
    },
    "github-auth": {
      "name": "datasette-auth-github",
      "basis": "unknown",
      "sources": {
        "s90107b903580": "https://github.com/simonw/datasette-auth-github"
      }
    },
    "write": {
      "name": "datasette-write",
      "basis": "0.4",
      "sources": {
        "s073e10d21091": "https://github.com/simonw/datasette-write/blob/0.4/README.md"
      }
    },
    "web": {
      "name": "sqlite-web package",
      "basis": "0.8.1",
      "sources": {
        "s91f8591a5f84": "https://github.com/coleifer/sqlite-web/blob/0.8.1/README.md"
      }
    },
    "web-source": {
      "name": "sqlite-web implementation",
      "basis": "825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2",
      "sources": {
        "s13d71c0a8cb2": "https://raw.githubusercontent.com/coleifer/sqlite-web/825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2/sqlite_web/sqlite_web.py"
      }
    },
    "web-image": {
      "name": "sqlite-web Dockerfile",
      "basis": "7f6658b012a789f0b9418cad543e7798ce850130",
      "sources": {
        "s4c81e6becc20": "https://raw.githubusercontent.com/coleifer/sqlite-web/7f6658b012a789f0b9418cad543e7798ce850130/docker/Dockerfile"
      }
    },
    "sqlite": {
      "name": "SQLite documentation",
      "basis": "unknown",
      "sources": {
        "s4e4e320abf5b": "https://www.sqlite.org/uri.html",
        "s2721da91f8d2": "https://www.sqlite.org/serverless.html",
        "sadf0431c1271": "https://www.sqlite.org/security.html"
      }
    },
    "docker": {
      "name": "Docker localhost-publication boundary",
      "basis": "28.0.0",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "cloudrun": {
      "name": "Cloud Run documentation",
      "basis": "unknown",
      "sources": {
        "sb90a6c13388a": "https://docs.cloud.google.com/run/docs/container-contract"
      }
    },
    "nginx": {
      "name": "nginx documentation",
      "basis": "unknown",
      "sources": {
        "s6a0728ca7609": "https://nginx.org/en/docs/http/configuring_https_servers.html",
        "sf32ce2956917": "https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html"
      }
    },
    "iap": {
      "name": "Google IAP documentation",
      "basis": "unknown",
      "sources": {
        "saafdfc163fce": "https://docs.cloud.google.com/iap/docs/concepts-overview"
      }
    },
    "access": {
      "name": "Cloudflare Access documentation",
      "basis": "unknown",
      "sources": {
        "sfe56578bedf4": "https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/",
        "s06747cf7388c": "https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/independent-mfa/"
      }
    },
    "tailscale": {
      "name": "Tailscale documentation",
      "basis": "unknown",
      "sources": {
        "s5b9a9b15ae80": "https://tailscale.com/docs/reference/tailscale-cli/serve"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "ss": {
      "name": "ss documentation",
      "basis": "unknown",
      "sources": {
        "sfc58f455acfa": "https://man7.org/linux/man-pages/man8/ss.8.html"
      }
    },
    "datasette-docs": {
      "name": "Datasette documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s3e64933fe2e9": "https://docs.datasette.io/en/stable/changelog.html",
        "sb0aae2446988": "https://docs.datasette.io/en/stable/cli-reference.html",
        "sca59b58c5c84": "https://docs.datasette.io/en/stable/performance.html",
        "s8f2fe7a13b3f": "https://docs.datasette.io/en/stable/installation.html",
        "se7cc29f79be8": "https://docs.datasette.io/en/stable/publish.html",
        "s878851fd8eac": "https://docs.datasette.io/en/stable/authentication.html",
        "s824eb176fda7": "https://docs.datasette.io/en/stable/sql_queries.html",
        "s406cc998a5da": "https://docs.datasette.io/en/stable/internals.html#csrf-protection",
        "se154b0fa47dd": "https://docs.datasette.io/en/stable/settings.html",
        "s96c8e6562139": "https://docs.datasette.io/en/stable/json_api.html",
        "s1e93b280c5af": "https://docs.datasette.io/en/stable/introspection.html",
        "sb1b30f98f026": "https://docs.datasette.io/en/stable/plugins.html#secret-configuration-values",
        "s53e84082f6d1": "https://docs.datasette.io/en/stable/deploying.html"
      }
    },
    "caddy-docs": {
      "name": "Caddy documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sbc2bd9599bd1": "https://caddyserver.com/docs/caddyfile/directives/basic_auth"
      }
    }
  },
  "claims": {
    "release": {"text": "The recorded stable Datasette documentation lists 0.65.5 with a table-permission bypass fix; deploy a supported release containing the security fixes.", "components": ["datasette-docs"], "sources": ["datasette-docs:s3e64933fe2e9"], "status": "REASONED"},
    "datasette-bind": {"text": "Bare datasette serve without host or port flags listened on 127.0.0.1:8001 in the recorded unprivileged local ss inventory.", "components": ["datasette-docs"], "sources": ["datasette-docs:sb0aae2446988"], "status": "DEMONSTRATED", "evidence": "bare `datasette serve` with no host or port flag listened on `127.0.0.1:8001`"},
    "immutable": {"text": "Use --immutable only for an unchanged snapshot; SQLite skips locking/change detection, so changing it can yield incorrect results or corruption errors.", "components": ["sqlite", "datasette-docs"], "sources": ["datasette-docs:sca59b58c5c84", "sqlite:s4e4e320abf5b"], "status": "REASONED"},
    "datasette-docker": {"text": "Documented Docker launch binds 0.0.0.0:8001 and publishes 8001:8001; container bind and host publication are separate.", "components": ["datasette-docs"], "sources": ["datasette-docs:s8f2fe7a13b3f"], "status": "REASONED"},
    "container-generator": {"text": "Inspected make_dockerfile selects --host 0.0.0.0, immutable databases, --cors and --port $PORT; inspect the generated command.", "components": ["ds-container"], "sources": ["ds-container:s3c9be24424e0"], "status": "REASONED"},
    "cloudrun": {"text": "Inspected publisher uses --allow-unauthenticated; Cloud Run requires 0.0.0.0 and PORT, ingress default 8080, with external TLS termination but no implied application authorization.", "components": ["ds-cloud", "cloudrun"], "sources": ["ds-cloud:sf5859249ea9f", "cloudrun:sb90a6c13388a"], "status": "REASONED"},
    "publish-plugins": {"text": "Review each publishing plugin and provider hostname; datasette-publish-fly documents app.fly.dev and no universal plugin authentication default was established.", "components": ["fly", "datasette-docs"], "sources": ["datasette-docs:se7cc29f79be8", "fly:s2a2db4192225"], "status": "REASONED"},
    "docker-publication": {"text": "Address-less Docker publication binds all host addresses; use explicit host loopback mappings for 8001 or 8080, and check direct routing and the pre-28.0.0 caveat externally.", "components": ["docker"], "sources": ["docker:s1e53417c513d"], "status": "REASONED"},
    "actor-policy": {"text": "Metadata allow blocks authorize actors at instance, database, table and canned-query scope; authentication alone does not restrict access. GitHub authentication explicitly leaves anonymous access until permissions restrict it.", "components": ["github-auth", "datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "github-auth:s90107b903580"], "status": "REASONED"},
    "root-url": {"text": "datasette --root issues a one-use root-cookie login URL, not an anonymous-access restriction; treat the URL as a credential.", "components": ["datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "datasette-docs:sb0aae2446988"], "status": "REASONED"},
    "canned-writes": {"text": "Ordinary SQL is read-only; canned queries enable writes with write:true and plugins may add further mutable routes, not a global write mode.", "components": ["datasette-docs"], "sources": ["datasette-docs:s824eb176fda7"], "status": "REASONED"},
    "write-plugin": {"text": "datasette-write adds /db/-/write governed by its own permission, root-only by default; installing it does not grant anonymous writes.", "components": ["write", "datasette-docs"], "sources": ["datasette-docs:s406cc998a5da", "write:s073e10d21091"], "status": "REASONED"},
    "sql-policy": {"text": "?sql= and .json?sql= allow arbitrary reads; table/view allow rules do not prevent SQL reading those objects. Set allow_sql policy or default_allow_sql off; no generic --setting permissions exists.", "components": ["datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "datasette-docs:se154b0fa47dd", "datasette-docs:s824eb176fda7"], "status": "REASONED"},
    "query-limits": {"text": "Queries default to a one-second time limit; repeated expensive requests may still consume resources, an inference rather than demonstrated denial of service.", "components": ["datasette-docs"], "sources": ["datasette-docs:se154b0fa47dd", "datasette-docs:s824eb176fda7"], "status": "REASONED"},
    "downloads": {"text": "allow_download defaults on for immutable file-backed databases; disabling it controls whole-file downloads, not ordinary exports. Local /published.db changed from 200 to 403.", "components": ["datasette-docs"], "sources": ["datasette-docs:se154b0fa47dd"], "status": "DEMONSTRATED", "evidence": "`/published.db` returned `403`; without `--setting allow_download off` it returned `200`."},
    "cors": {"text": "The local --cors run added Access-Control-Allow-Origin: *; the header was absent without the flag.", "components": ["datasette-docs"], "sources": ["datasette-docs:s96c8e6562139"], "status": "DEMONSTRATED", "evidence": "`--cors` added `Access-Control-Allow-Origin: *`, absent without it."},
    "introspection": {"text": "/-/metadata, /-/plugins, /-/versions, /-/settings and /-/databases, including JSON forms, expose instance details; permissions debugger separately requires root or its permission.", "components": ["datasette-docs"], "sources": ["datasette-docs:s1e93b280c5af", "datasette-docs:s878851fd8eac"], "status": "REASONED"},
    "hash-urls": {"text": "Core hash_urls was removed in 0.61; datasette-hashed-urls provides cache-oriented content hashes, not secrecy or authorization.", "components": ["datasette-docs"], "sources": ["datasette-docs:s3e64933fe2e9", "datasette-docs:sca59b58c5c84"], "status": "REASONED"},
    "csrf": {"text": "Datasette asgi-csrf compares ds_csrftoken cookie with csrftoken form field or x-csrftoken header; preserve it for writes and review skip_csrf plugins. It does not restrict anonymous reads.", "components": ["datasette-docs"], "sources": ["datasette-docs:s406cc998a5da"], "status": "REASONED"},
    "plugin-secrets": {"text": "The local analyst saw inline password hashes in metadata, but only $env references after environment indirection.", "components": ["passwords", "datasette-docs"], "sources": ["datasette-docs:sb1b30f98f026", "passwords:sb6597be5af67"], "status": "DEMONSTRATED", "evidence": "`/-/metadata.json` showed that analyst both users' password hashes when they were written inline in the plugin configuration, but only the `$env` references when they were supplied through environment variables."},
    "web-bind": {"text": "Bare sqlite_web listened on 127.0.0.1:8080 in the recorded unprivileged local ss inventory.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "bare `sqlite_web` on `127.0.0.1:8080`, as `ss -tlnp` run without `sudo` by the same account showed"},
    "web-capabilities": {"text": "sqlite-web supports queries, imports/exports, row changes and dropping schema objects; reachable unauthenticated write access implies database compromise, not automatic host compromise.", "components": ["web"], "sources": ["web:s91f8591a5f84"], "status": "REASONED"},
    "web-container": {"text": "sqlite-web Dockerfile starts -H 0.0.0.0 and exposes 8080; README publishes 8080:8080. Use explicit loopback publication for a same-host proxy.", "components": ["web-image", "web"], "sources": ["web-image:s4c81e6becc20", "web:s91f8591a5f84"], "status": "REASONED"},
    "web-password": {"text": "Local SQLITE_WEB_PASSWORD without -P left anonymous query access at 200; with -P the anonymous query redirected to /login/.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "`SQLITE_WEB_PASSWORD` set without `-P` left sqlite-web open (`200` anonymously), as the source reading above says; with `-P` the anonymous query GET got `302` to `/login/`."},
    "web-readonly": {"text": "In the local --read-only run the anonymous read still returned 200 while the insert changed nothing.", "components": ["web", "web-source", "sqlite"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2", "sqlite:s4e4e320abf5b"], "status": "DEMONSTRATED", "evidence": "with `--read-only` the read still returned `200` and the insert changed nothing."},
    "web-methods": {"text": "Inspected sqlite-web query handler permits read GETs; writes, scripts and drops require POST. A harmless query GET establishes anonymous read access.", "components": ["web-source"], "sources": ["web-source:s13d71c0a8cb2"], "status": "REASONED"},
    "web-tls": {"text": "sqlite-web documents native --ssl-cert and --ssl-key; this deployment baseline uses the shared TLS proxy.", "components": ["web"], "sources": ["web:s91f8591a5f84"], "status": "REASONED"},
    "web-csrf": {"text": "sqlite-web 0.8.1 loopback insert accepted an authenticated POST without a token and with foreign Origin; the form has no CSRF field. Prefer read-only behind the proxy.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "an authenticated `POST` insert with no token and a foreign `Origin` header wrote a row, and the insert form contains no CSRF field."},
    "web-cookie": {"text": "sqlite-web 0.8.1 set HttpOnly; Path=/ without SameSite or Secure even over TLS; cross-site cookie sending therefore depends on browser defaults.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "Its session cookie was set with `HttpOnly; Path=/` and no `SameSite` or `Secure` attribute, even over TLS"},
    "fronting": {"text": "Keep same-host origins on loopback and apply TLS and authentication to every UI, SQL, JSON, export, download and auxiliary route.", "components": ["nginx", "caddy-docs", "datasette-docs"], "sources": ["datasette-docs:s53e84082f6d1", "nginx:s6a0728ca7609", "nginx:sf32ce2956917", "caddy-docs:sbc2bd9599bd1"], "status": "REASONED"},
    "identity-proxy": {"text": "IAP and Cloudflare Access evaluate access before forwarding; no tenancy was available to demonstrate these routes.", "components": ["iap", "access"], "sources": ["iap:saafdfc163fce", "access:sfe56578bedf4"], "status": "REASONED"},
    "mfa": {"text": "Neither reviewed core authentication interface supplies native MFA; enforce it at the identity provider or through Cloudflare Access independent MFA.", "components": ["web", "access", "datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "web:s91f8591a5f84", "access:s06747cf7388c"], "status": "REASONED"},
    "tailnet": {"text": "Tailscale Serve shares inside the tailnet; Funnel publishes publicly. Verify which path is configured.", "components": ["tailscale"], "sources": ["tailscale:s5b9a9b15ae80"], "status": "REASONED"},
    "origin-bypass": {"text": "Inventory direct origins and provider hostnames so proxy login cannot be bypassed; IAP documents backend and Cloud Run hostname precautions.", "components": ["iap"], "sources": ["iap:saafdfc163fce"], "status": "REASONED"},
    "os-account": {"text": "Use a dedicated unprivileged account and curated snapshot whose file and parent it cannot modify; protect sidecars and temporary files under SQLite filesystem authority.", "components": ["sqlite"], "sources": ["sqlite:s2721da91f8d2", "sqlite:sadf0431c1271"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect complete listener table, IPv6 and unexpected ports; empty output after an error is inconclusive. Root ss, wildcard binds, Docker publication and managed ingress remain reasoned without sudo/container capability.", "components": ["web", "ss", "docker", "cloudrun", "datasette-docs"], "sources": ["datasette-docs:sb0aae2446988", "web:s91f8591a5f84", "ss:sfc58f455acfa", "docker:s1e53417c513d", "cloudrun:sb90a6c13388a"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "External origin/provider tests require a successful local control and actual deployment targets; any HTTP response proves reachability, while transport failures alone prove no isolation. No second network/provider deployment was available.", "components": ["web", "iap", "curl", "datasette-docs"], "sources": ["datasette-docs:s53e84082f6d1", "web:s91f8591a5f84", "iap:saafdfc163fce", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-anonymous": {"text": "UI, schema or row data without credentials is exposure; login pages, unexplained 404s and HTTP success alone do not establish protection. SQL-disabled tests also need an authorized browsing control.", "components": ["web", "datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "datasette-docs:s824eb176fda7", "web:s91f8591a5f84"], "status": "REASONED", "verify": [2]},
    "datasette-exposed": {"text": "Local bare Datasette returned listing and known SQL row with 200 and /-/versions.json anonymously with 200; baseline SQL returned 403 while table JSON still returned 200.", "components": ["datasette-docs"], "sources": ["datasette-docs:sb0aae2446988", "datasette-docs:se154b0fa47dd", "datasette-docs:s96c8e6562139", "datasette-docs:s1e93b280c5af"], "status": "DEMONSTRATED", "evidence": "Against the baseline command above, the SQL JSON route returned `403` while the table's JSON page still returned `200` (SQL disabled, browsing permitted)"},
    "web-exposed": {"text": "Local bare sqlite-web returned query GET 200 anonymously and accepted an anonymous insert into a disposable database.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "Bare `sqlite_web` answered the query GET with `200` anonymously, and an anonymous `POST` insert wrote a row to a disposable database"},
    "verify-authorized": {"text": "Private mode-0600 header file supplies credentials by path, not argv values; compare known authorized data with anonymous denial and repeat with an unauthorized actor. File guards establish readability/type, not privacy; identity-proxy scenarios lack a tenancy.", "components": ["web", "curl", "iap", "access", "datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "web:s91f8591a5f84", "curl:s2b2686afaf41", "iap:saafdfc163fce", "access:sfe56578bedf4"], "status": "REASONED", "verify": [3]},
    "actor-results": {"text": "Local password-plugin analyst cookie returned table rows with 200, anonymous and guest requests got 403, and analyst SQL got 403 under allow_sql:false.", "components": ["passwords", "datasette-docs"], "sources": ["datasette-docs:s878851fd8eac", "passwords:sb6597be5af67"], "status": "DEMONSTRATED", "evidence": "the block returned the table's rows to the `analyst` session cookie (`authorized http=200`) and `403` anonymously; an authenticated `guest` got `403`, the unauthorized outcome, and the analyst got `403` on SQL under `allow_sql: false`."},
    "web-auth-results": {"text": "Local sqlite-web -P session cookie returned the row with 200 and the anonymous request redirected to /login/.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "DEMONSTRATED", "evidence": "For sqlite-web with `-P`, the session cookie got the row with `200` and the anonymous request `302` to `/login/`."},
    "introspection-results": {"text": "Under the local metadata policy, all five auxiliary JSON routes returned 403 anonymously and 200 to a freshly logged-in analyst.", "components": ["passwords", "datasette-docs"], "sources": ["datasette-docs:s1e93b280c5af", "datasette-docs:s878851fd8eac", "passwords:sb6597be5af67"], "status": "DEMONSTRATED", "evidence": "Under the same metadata, `/-/versions.json`, `/-/metadata.json`, `/-/plugins.json`, `/-/settings.json` and `/-/databases.json` returned `403` anonymously and `200` to a freshly logged-in analyst"},
    "caddy-results": {"text": "Caddy v2.11.4 loopback TLS/Basic proxy denied anonymous UI, SQL, database download, versions and CSV with 401 and allowed credentials with 200; direct backend remained anonymous. Protection depends on backend isolation.", "components": ["caddy-docs", "datasette-docs"], "sources": ["caddy-docs:sbc2bd9599bd1", "datasette-docs:s53e84082f6d1"], "status": "DEMONSTRATED", "evidence": "Block C through the proxy gave `authorized http=200` with the rows and `anonymous http=401` with `www-authenticate: Basic realm=\"restricted\"`."},
    "local-checks": {"text": "Recorded bash parsing, metadata JSON parsing and 120 guard executions passed; curl argument recording tested guards separately from service outcomes.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "DEMONSTRATED", "evidence": "Local authoring checks passed: `bash -n` on all five shell blocks, parsing of the metadata JSON, and 120 guard executions covering 40 cases under ordinary Bash, `set -u`, and `set -u` with `IFS=0`."},
    "guard-limits": {"text": "Use Bash with real unshadowed builtins and curl 7.75.0 or newer; paste whole blocks, escape apostrophes, avoid credential URLs, and retain TLS verification. Partial pastes and inherited matching marker/arguments remain outside guard coverage.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED"},
    "datasette-cli": {"text": "Bare datasette invokes serve; -h/--host and -p/--port override its bind and port.", "components": ["datasette-docs"], "sources": ["datasette-docs:sb0aae2446988"], "status": "REASONED"},
    "web-cli": {"text": "sqlite-web -H/--host uses uppercase H and -p/--port overrides the port; the documented default is 127.0.0.1:8080.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "REASONED"},
    "write-test": {"text": "Local anonymous write and root write without CSRF were denied; root write with the token returned 302 and wrote the row.", "components": ["write", "datasette-docs"], "sources": ["datasette-docs:s406cc998a5da", "write:s073e10d21091"], "status": "DEMONSTRATED", "evidence": "With datasette-write on a disposable database, an anonymous write got `403`, a root write without the CSRF token `403`, and with the token `302`, and the row was written."},
    "secret-indirection": {"text": "Keep plugin secrets out of public metadata with documented environment or file indirection, and protect root login URLs and credential files.", "components": ["datasette-docs"], "sources": ["datasette-docs:sb1b30f98f026", "datasette-docs:s878851fd8eac"], "status": "REASONED"},
    "web-auth-config": {"text": "A nonempty shared password requires -P/--password; SQLITE_WEB_PASSWORD is read only inside that option branch. The shared login supplies no per-table roles.", "components": ["web", "web-source"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2"], "status": "REASONED"},
    "web-readonly-config": {"text": "--read-only opens SQLite with mode=ro and reduces exposure to reads; it does not authenticate callers.", "components": ["web", "web-source", "sqlite"], "sources": ["web:s91f8591a5f84", "web-source:s13d71c0a8cb2", "sqlite:s4e4e320abf5b"], "status": "REASONED"},
    "cors-policy": {"text": "--cors permits cross-origin JSON access and should be omitted unless intended; its absence does not authenticate requests.", "components": ["datasette-docs"], "sources": ["datasette-docs:s96c8e6562139"], "status": "REASONED"},
    "query-pages": {"text": "Queries return at most 1,000 rows at a time by default; pagination retrieves more, so that limit is not a confidentiality boundary.", "components": ["datasette-docs"], "sources": ["datasette-docs:se154b0fa47dd", "datasette-docs:s824eb176fda7"], "status": "REASONED"}
  }
}
---
# SQLite HTTP front-ends: Datasette and sqlite-web

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| release: The recorded stable Datasette documentation lists 0.65.5 with a table-permission bypass fix; deploy a supported release containing the security fixes. | Datasette documentation (rolling) unknown | REASONED |
| datasette-bind: Bare datasette serve without host or port flags listened on 127.0.0.1:8001 in the recorded unprivileged local ss inventory. | Datasette documentation (rolling) unknown | DEMONSTRATED |
| immutable: Use --immutable only for an unchanged snapshot; SQLite skips locking/change detection, so changing it can yield incorrect results or corruption errors. | SQLite documentation unknown; Datasette documentation (rolling) unknown | REASONED |
| datasette-docker: Documented Docker launch binds 0.0.0.0:8001 and publishes 8001:8001; container bind and host publication are separate. | Datasette documentation (rolling) unknown | REASONED |
| container-generator: Inspected make_dockerfile selects --host 0.0.0.0, immutable databases, --cors and --port $PORT; inspect the generated command. | Datasette container generator caf238aac86ebe370959b25384d6e05f6a1e2359 | REASONED |
| cloudrun: Inspected publisher uses --allow-unauthenticated; Cloud Run requires 0.0.0.0 and PORT, ingress default 8080, with external TLS termination but no implied application authorization. | Datasette Cloud Run publisher e889403d3bbe143854262682161c98a57bdb6594; Cloud Run documentation unknown | REASONED |
| publish-plugins: Review each publishing plugin and provider hostname; datasette-publish-fly documents app.fly.dev and no universal plugin authentication default was established. | Datasette Fly publishing plugin unknown; Datasette documentation (rolling) unknown | REASONED |
| docker-publication: Address-less Docker publication binds all host addresses; use explicit host loopback mappings for 8001 or 8080, and check direct routing and the pre-28.0.0 caveat externally. | Docker localhost-publication boundary 28.0.0 | REASONED |
| actor-policy: Metadata allow blocks authorize actors at instance, database, table and canned-query scope; authentication alone does not restrict access. GitHub authentication explicitly leaves anonymous access until permissions restrict it. | datasette-auth-github unknown; Datasette documentation (rolling) unknown | REASONED |
| root-url: datasette --root issues a one-use root-cookie login URL, not an anonymous-access restriction; treat the URL as a credential. | Datasette documentation (rolling) unknown | REASONED |
| canned-writes: Ordinary SQL is read-only; canned queries enable writes with write:true and plugins may add further mutable routes, not a global write mode. | Datasette documentation (rolling) unknown | REASONED |
| write-plugin: datasette-write adds /db/-/write governed by its own permission, root-only by default; installing it does not grant anonymous writes. | datasette-write 0.4; Datasette documentation (rolling) unknown | REASONED |
| sql-policy: ?sql= and .json?sql= allow arbitrary reads; table/view allow rules do not prevent SQL reading those objects. Set allow_sql policy or default_allow_sql off; no generic --setting permissions exists. | Datasette documentation (rolling) unknown | REASONED |
| query-limits: Queries default to a one-second time limit; repeated expensive requests may still consume resources, an inference rather than demonstrated denial of service. | Datasette documentation (rolling) unknown | REASONED |
| downloads: allow_download defaults on for immutable file-backed databases; disabling it controls whole-file downloads, not ordinary exports. Local /published.db changed from 200 to 403. | Datasette documentation (rolling) unknown | DEMONSTRATED |
| cors: The local --cors run added Access-Control-Allow-Origin: *; the header was absent without the flag. | Datasette documentation (rolling) unknown | DEMONSTRATED |
| introspection: /-/metadata, /-/plugins, /-/versions, /-/settings and /-/databases, including JSON forms, expose instance details; permissions debugger separately requires root or its permission. | Datasette documentation (rolling) unknown | REASONED |
| hash-urls: Core hash_urls was removed in 0.61; datasette-hashed-urls provides cache-oriented content hashes, not secrecy or authorization. | Datasette documentation (rolling) unknown | REASONED |
| csrf: Datasette asgi-csrf compares ds_csrftoken cookie with csrftoken form field or x-csrftoken header; preserve it for writes and review skip_csrf plugins. It does not restrict anonymous reads. | Datasette documentation (rolling) unknown | REASONED |
| plugin-secrets: The local analyst saw inline password hashes in metadata, but only $env references after environment indirection. | datasette-auth-passwords 1.1.1; Datasette documentation (rolling) unknown | DEMONSTRATED |
| web-bind: Bare sqlite_web listened on 127.0.0.1:8080 in the recorded unprivileged local ss inventory. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| web-capabilities: sqlite-web supports queries, imports/exports, row changes and dropping schema objects; reachable unauthenticated write access implies database compromise, not automatic host compromise. | sqlite-web package 0.8.1 | REASONED |
| web-container: sqlite-web Dockerfile starts -H 0.0.0.0 and exposes 8080; README publishes 8080:8080. Use explicit loopback publication for a same-host proxy. | sqlite-web Dockerfile 7f6658b012a789f0b9418cad543e7798ce850130; sqlite-web package 0.8.1 | REASONED |
| web-password: Local SQLITE_WEB_PASSWORD without -P left anonymous query access at 200; with -P the anonymous query redirected to /login/. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| web-readonly: In the local --read-only run the anonymous read still returned 200 while the insert changed nothing. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2; SQLite documentation unknown | DEMONSTRATED |
| web-methods: Inspected sqlite-web query handler permits read GETs; writes, scripts and drops require POST. A harmless query GET establishes anonymous read access. | sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | REASONED |
| web-tls: sqlite-web documents native --ssl-cert and --ssl-key; this deployment baseline uses the shared TLS proxy. | sqlite-web package 0.8.1 | REASONED |
| web-csrf: sqlite-web 0.8.1 loopback insert accepted an authenticated POST without a token and with foreign Origin; the form has no CSRF field. Prefer read-only behind the proxy. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| web-cookie: sqlite-web 0.8.1 set HttpOnly; Path=/ without SameSite or Secure even over TLS; cross-site cookie sending therefore depends on browser defaults. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| fronting: Keep same-host origins on loopback and apply TLS and authentication to every UI, SQL, JSON, export, download and auxiliary route. | nginx documentation unknown; Caddy documentation (rolling) unknown; Datasette documentation (rolling) unknown | REASONED |
| identity-proxy: IAP and Cloudflare Access evaluate access before forwarding; no tenancy was available to demonstrate these routes. | Google IAP documentation unknown; Cloudflare Access documentation unknown | REASONED |
| mfa: Neither reviewed core authentication interface supplies native MFA; enforce it at the identity provider or through Cloudflare Access independent MFA. | sqlite-web package 0.8.1; Cloudflare Access documentation unknown; Datasette documentation (rolling) unknown | REASONED |
| tailnet: Tailscale Serve shares inside the tailnet; Funnel publishes publicly. Verify which path is configured. | Tailscale documentation unknown | REASONED |
| origin-bypass: Inventory direct origins and provider hostnames so proxy login cannot be bypassed; IAP documents backend and Cloud Run hostname precautions. | Google IAP documentation unknown | REASONED |
| os-account: Use a dedicated unprivileged account and curated snapshot whose file and parent it cannot modify; protect sidecars and temporary files under SQLite filesystem authority. | SQLite documentation unknown | REASONED |
| verify-inventory: Inspect complete listener table, IPv6 and unexpected ports; empty output after an error is inconclusive. Root ss, wildcard binds, Docker publication and managed ingress remain reasoned without sudo/container capability. | sqlite-web package 0.8.1; ss documentation unknown; Docker localhost-publication boundary 28.0.0; Cloud Run documentation unknown; Datasette documentation (rolling) unknown | REASONED |
| verify-external: External origin/provider tests require a successful local control and actual deployment targets; any HTTP response proves reachability, while transport failures alone prove no isolation. No second network/provider deployment was available. | sqlite-web package 0.8.1; Google IAP documentation unknown; curl minimum write-out version 7.75.0; Datasette documentation (rolling) unknown | REASONED |
| verify-anonymous: UI, schema or row data without credentials is exposure; login pages, unexplained 404s and HTTP success alone do not establish protection. SQL-disabled tests also need an authorized browsing control. | sqlite-web package 0.8.1; Datasette documentation (rolling) unknown | REASONED |
| datasette-exposed: Local bare Datasette returned listing and known SQL row with 200 and /-/versions.json anonymously with 200; baseline SQL returned 403 while table JSON still returned 200. | Datasette documentation (rolling) unknown | DEMONSTRATED |
| web-exposed: Local bare sqlite-web returned query GET 200 anonymously and accepted an anonymous insert into a disposable database. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| verify-authorized: Private mode-0600 header file supplies credentials by path, not argv values; compare known authorized data with anonymous denial and repeat with an unauthorized actor. File guards establish readability/type, not privacy; identity-proxy scenarios lack a tenancy. | sqlite-web package 0.8.1; curl minimum write-out version 7.75.0; Google IAP documentation unknown; Cloudflare Access documentation unknown; Datasette documentation (rolling) unknown | REASONED |
| actor-results: Local password-plugin analyst cookie returned table rows with 200, anonymous and guest requests got 403, and analyst SQL got 403 under allow_sql:false. | datasette-auth-passwords 1.1.1; Datasette documentation (rolling) unknown | DEMONSTRATED |
| web-auth-results: Local sqlite-web -P session cookie returned the row with 200 and the anonymous request redirected to /login/. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | DEMONSTRATED |
| introspection-results: Under the local metadata policy, all five auxiliary JSON routes returned 403 anonymously and 200 to a freshly logged-in analyst. | datasette-auth-passwords 1.1.1; Datasette documentation (rolling) unknown | DEMONSTRATED |
| caddy-results: Caddy v2.11.4 loopback TLS/Basic proxy denied anonymous UI, SQL, database download, versions and CSV with 401 and allowed credentials with 200; direct backend remained anonymous. Protection depends on backend isolation. | Caddy documentation (rolling) unknown; Datasette documentation (rolling) unknown | DEMONSTRATED |
| local-checks: Recorded bash parsing, metadata JSON parsing and 120 guard executions passed; curl argument recording tested guards separately from service outcomes. | curl minimum write-out version 7.75.0 | DEMONSTRATED |
| guard-limits: Use Bash with real unshadowed builtins and curl 7.75.0 or newer; paste whole blocks, escape apostrophes, avoid credential URLs, and retain TLS verification. Partial pastes and inherited matching marker/arguments remain outside guard coverage. | curl minimum write-out version 7.75.0 | REASONED |
| datasette-cli: Bare datasette invokes serve; -h/--host and -p/--port override its bind and port. | Datasette documentation (rolling) unknown | REASONED |
| web-cli: sqlite-web -H/--host uses uppercase H and -p/--port overrides the port; the documented default is 127.0.0.1:8080. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | REASONED |
| write-test: Local anonymous write and root write without CSRF were denied; root write with the token returned 302 and wrote the row. | datasette-write 0.4; Datasette documentation (rolling) unknown | DEMONSTRATED |
| secret-indirection: Keep plugin secrets out of public metadata with documented environment or file indirection, and protect root login URLs and credential files. | Datasette documentation (rolling) unknown | REASONED |
| web-auth-config: A nonempty shared password requires -P/--password; SQLITE_WEB_PASSWORD is read only inside that option branch. The shared login supplies no per-table roles. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2 | REASONED |
| web-readonly-config: --read-only opens SQLite with mode=ro and reduces exposure to reads; it does not authenticate callers. | sqlite-web package 0.8.1; sqlite-web implementation 825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2; SQLite documentation unknown | REASONED |
| cors-policy: --cors permits cross-origin JSON access and should be omitted unless intended; its absence does not authenticate requests. | Datasette documentation (rolling) unknown | REASONED |
| query-pages: Queries return at most 1,000 rows at a time by default; pagination retrieves more, so that limit is not a confidentiality boundary. | Datasette documentation (rolling) unknown | REASONED |
<!-- version-basis:end -->

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

The service outcomes below were **demonstrated on loopback** against Datasette 0.65.5 (with datasette-auth-passwords 1.1.1 and datasette-write 0.4) and sqlite-web 0.8.1, installed from PyPI into a virtual environment, with every server on 127.0.0.1 and, for the HTTPS blocks, native TLS or a Caddy TLS proxy with certificates from a private test CA that curl trusted through `CURL_CA_BUNDLE`. Blocks B and C ran as printed with only their placeholders substituted. What those runs do not show is marked **REASONED** where it occurs, with its reason and basis in the cited vendor documentation.

Use Bash with real, unshadowed builtins and curl 7.75.0 or newer. Paste whole subshells and substitute inside the single quotes. A literal apostrophe requires proper shell escaping; do not simply paste it between those quotes. Use URLs without embedded credentials or signed tokens. Every curl begins with `-q -g`, disables environment proxies, and reports the error text. Do not add `-k` or redirect-following.

### A. Listener inventory

**The fixed bind demonstrated on loopback; a wildcard bind and container publications REASONED** (the host forbids binding every interface and has no container runtime). On the deployment host, inspect the complete listener table:

REASONED: following block; the cited ss and deployment documentation supplies the full inventory check; sudo, wildcard binding and container publication were unavailable. Only the unprivileged loopback inventory is recorded as demonstrated below.

```bash
sudo ss -tlnp
```

For the same-host examples, expect `127.0.0.1:8001` and/or `127.0.0.1:8080`, owned by the intended processes. A wildcard origin bind is the finding. Read IPv6 entries and unexpected ports too. An inspection error followed by an empty table is inconclusive. These example ports match the documented CLI defaults; substitute the actual configured ports when testing. On loopback, bare `datasette serve` with no host or port flag listened on `127.0.0.1:8001` and bare `sqlite_web` on `127.0.0.1:8080`, as `ss -tlnp` run without `sudo` by the same account showed (the authoring host has no `sudo`).

Inspect container publications separately: Docker forwarding can expose a port without a corresponding host listening process. A wildcard bind inside a container is distinct from a public host publication; managed ingress such as Cloud Run also has its own binding contract. Confirm those boundaries through configuration and external probes.

### B. Direct reachability and anonymous access

**Demonstrated on loopback against both tools; an external vantage and provider hostnames REASONED** (the host has no second network and no provider deployment). The same-host reverse proxy was demonstrated with Caddy (section C); identity-aware-proxy routes are REASONED, since no IAP or Cloudflare Access tenancy was available.

First obtain a successful local control against the running backend. Then run the block from an authorized external testing host against each direct origin and provider hostname, followed by the published HTTPS routes. For a protected route, establish section C's authorized positive control first. Use disposable databases for any local exposed-state reproduction.

REASONED: following block; the complete deployment scenario needs an external vantage and provider deployment, neither available. The cited route documentation supplies expectations; the separate loopback outcomes are recorded below.

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

REASONED: following block; the complete fronting-layer scenario includes IAP or Cloudflare Access, and no tenancy was available. The cited authentication documentation supplies expectations; native-TLS and Caddy loopback outcomes are recorded below.

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

**REASONED:** the cited vendor documentation is the basis for what the loopback runs could not show: a wildcard bind and container publications, an external vantage against direct origins and provider hostnames, the identity-aware-proxy pattern, and `ss` run as root.

## Sources (checked September 2026)

Applicability checked on 2026-09-18: Datasette stable documentation lists 0.65.5; Datasette packaging source was inspected on moving `main`. sqlite-web source was inspected on moving `master`, identifying itself as 0.8.1; the released 0.8.1 package matched it for the flags and routes the loopback runs exercised. Runtime confirmation used Datasette 0.65.5, datasette-auth-passwords 1.1.1, datasette-write 0.4 and sqlite-web 0.8.1 from PyPI.

Every URL listed below was fetched during authoring. This list also records the source-fetch review.

- Datasette CLI reference (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/cli-reference.html
- Datasette authentication and permissions (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/authentication.html
- Datasette settings (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/settings.html
- Datasette SQL queries and writable canned queries (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/sql_queries.html
- Datasette JSON API and CORS (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/json_api.html
- Datasette introspection routes (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/introspection.html
- Datasette Docker installation (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/installation.html
- Datasette proxy deployment (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/deploying.html
- Datasette publishing (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/publish.html
- Datasette container generator: https://raw.githubusercontent.com/simonw/datasette/caf238aac86ebe370959b25384d6e05f6a1e2359/datasette/utils/__init__.py
- Datasette Cloud Run publisher: https://github.com/simonw/datasette/blob/e889403d3bbe143854262682161c98a57bdb6594/datasette/publish/cloudrun.py
- Datasette Fly publishing plugin: https://github.com/simonw/datasette-publish-fly
- Datasette immutable mode and hashed URLs (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/performance.html
- Datasette CSRF protection (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/internals.html#csrf-protection
- Datasette plugin secret configuration (rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/plugins.html#secret-configuration-values
- Datasette changelog and security fixes (Datasette core hash_urls removed in 0.61; rolling documentation, checked September 2026): https://docs.datasette.io/en/stable/changelog.html
- Datasette password authentication plugin (datasette-auth-passwords 1.1.1 used in the loopback demonstrations): https://github.com/simonw/datasette-auth-passwords/blob/1.1.1/README.md
- Datasette GitHub authentication plugin: https://github.com/simonw/datasette-auth-github
- Datasette write plugin (datasette-write 0.4 used in the loopback demonstrations): https://github.com/simonw/datasette-write/blob/0.4/README.md
- sqlite-web README, features, options, and Docker usage (sqlite-web 0.8.1 from PyPI, tested on loopback): https://github.com/coleifer/sqlite-web/blob/0.8.1/README.md
- sqlite-web implementation: https://raw.githubusercontent.com/coleifer/sqlite-web/825b4a050fe2a04e6c6cf4b8ee1f56eaea4feef2/sqlite_web/sqlite_web.py
- sqlite-web Dockerfile: https://raw.githubusercontent.com/coleifer/sqlite-web/7f6658b012a789f0b9418cad543e7798ce850130/docker/Dockerfile
- SQLite security: https://www.sqlite.org/security.html
- SQLite serverless architecture and filesystem access: https://www.sqlite.org/serverless.html
- SQLite URI semantics: https://www.sqlite.org/uri.html
- Docker port publishing (Docker's pre-28.0.0 localhost-publication caveat): https://docs.docker.com/engine/network/port-publishing/
- Cloud Run container contract: https://docs.cloud.google.com/run/docs/container-contract
- nginx HTTPS configuration: https://nginx.org/en/docs/http/configuring_https_servers.html
- nginx Basic authentication: https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
- Caddy Basic authentication (rolling documentation, checked September 2026): https://caddyserver.com/docs/caddyfile/directives/basic_auth
- Google IAP overview and origin protection: https://docs.cloud.google.com/iap/docs/concepts-overview
- Cloudflare Access HTTP applications: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/
- Cloudflare independent MFA: https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/independent-mfa/
- Tailscale Serve and Funnel distinction: https://tailscale.com/docs/reference/tailscale-cli/serve
- curl manual (write-out variables `exitcode` and `errormsg` added in curl 7.75.0): https://curl.se/docs/manpage.html
- ss manual: https://man7.org/linux/man-pages/man8/ss.8.html
- OWASP SQL injection prevention: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
