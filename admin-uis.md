---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "f06b61afb03842d1626747e93b21a25a1255a39d656614ed04fda12562e7b8ff",
  "components": {
    "mongo": {
      "name": "mongo-express",
      "basis": "unknown",
      "sources": {
        "s69ec4eee2c85": "https://github.com/mongo-express/mongo-express"
      }
    },
    "grafana": {
      "name": "Grafana docs",
      "basis": "unknown",
      "sources": {
        "s7aa447405cc5": "https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/",
        "sc241e0772095": "https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/"
      }
    },
    "prometheus": {
      "name": "Prometheus docs",
      "basis": "unknown",
      "sources": {
        "scce074c47e9c": "https://prometheus.io/docs/guides/basic-auth/",
        "sc48b506cc29a": "https://prometheus.io/docs/guides/tls-encryption/"
      }
    },
    "phpmyadmin": {
      "name": "phpMyAdmin",
      "basis": "unknown",
      "sources": {
        "s5f6c8965c539": "https://www.phpmyadmin.net/docs/"
      }
    },
    "pgadmin": {
      "name": "pgAdmin",
      "basis": "unknown",
      "sources": {
        "s2f7e33714435": "https://www.pgadmin.org/docs/"
      }
    },
    "adminer": {
      "name": "Adminer",
      "basis": "unknown",
      "sources": {
        "sb5eda9397b18": "https://www.adminer.org/"
      }
    },
    "prometheus-pin": {
      "name": "Prometheus",
      "basis": "v3.14.0",
      "sources": {
        "s6d5f308b02a2": "https://github.com/prometheus/prometheus/blob/v3.14.0/cmd/prometheus/main.go#L424-L425"
      }
    },
    "grafana-pin": {
      "name": "Grafana",
      "basis": "v13.2.2",
      "sources": {
        "s2ade1bcff9aa": "https://github.com/grafana/grafana/blob/v13.2.2/conf/defaults.ini#L50",
        "sb00e234d0ddd": "https://github.com/grafana/grafana/blob/v13.2.2/pkg/api/http_server.go#L467-L469",
        "sf14b29976adb": "https://github.com/grafana/grafana/blob/v13.2.2/pkg/api/http_server.go#L568"
      }
    },
    "go": {
      "name": "Go net",
      "basis": "unknown",
      "sources": {
        "s37204ff1b27c": "https://pkg.go.dev/net#Listen"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep panels private; public front doors need proxy TLS, authentication and MFA. RedisInsight has no dedicated source here.", "components": ["grafana", "prometheus", "phpmyadmin", "pgadmin", "adminer"], "sources": ["grafana:s7aa447405cc5", "prometheus:scce074c47e9c", "phpmyadmin:s5f6c8965c539", "pgadmin:s2f7e33714435", "adminer:sb5eda9397b18"], "status": "REASONED"},
    "mongo-enable": {"text": "Recent login defaults off; current ENABLED and deprecated BASICAUTH fallback differ from some 1.0.x username-triggered builds. Set both flags and verify.", "components": ["mongo"], "sources": ["mongo:s69ec4eee2c85"], "status": "REASONED"},
    "mongo-credentials": {"text": "Set nonempty BASICAUTH_USERNAME/PASSWORD instead of admin/pass defaults.", "components": ["mongo"], "sources": ["mongo:s69ec4eee2c85"], "status": "REASONED"},
    "mongo-database": {"text": "Web Basic auth is separate from MongoDB credentials in ME_CONFIG_MONGODB_URL.", "components": ["mongo"], "sources": ["mongo:s69ec4eee2c85"], "status": "REASONED"},
    "grafana-admin": {"text": "First login uses admin/admin and prompts for replacement; use strong credentials and individual accounts.", "components": ["grafana"], "sources": ["grafana:s7aa447405cc5"], "status": "REASONED"},
    "grafana-anonymous": {"text": "Disable Grafana anonymous access if enabled.", "components": ["grafana"], "sources": ["grafana:s7aa447405cc5"], "status": "REASONED"},
    "grafana-mfa": {"text": "Prefer SSO with MFA at the identity provider.", "components": ["grafana"], "sources": ["grafana:s7aa447405cc5"], "status": "REASONED"},
    "grafana-bind": {"text": "Empty http_addr joins the port and binds all interfaces; set 127.0.0.1.", "components": ["grafana-pin", "go"], "sources": ["grafana-pin:s2ade1bcff9aa", "grafana-pin:sb00e234d0ddd", "grafana-pin:sf14b29976adb", "go:s37204ff1b27c"], "status": "REASONED"},
    "grafana-tls": {"text": "Native HTTPS uses server protocol=https, cert_file and cert_key.", "components": ["grafana"], "sources": ["grafana:s7aa447405cc5", "grafana:sc241e0772095"], "status": "REASONED"},
    "prometheus-auth": {"text": "Authentication defaults off; web.config.file supplies basic_auth_users with bcrypt hashes.", "components": ["prometheus"], "sources": ["prometheus:scce074c47e9c"], "status": "REASONED"},
    "prometheus-bcrypt": {"text": "Use htpasswd -nB -C 12; the guide's bare -B cost 5 versus OWASP minimum 10 lacks an OWASP citation here.", "components": ["prometheus"], "sources": ["prometheus:scce074c47e9c"], "status": "REASONED"},
    "prometheus-bind": {"text": "Default 0.0.0.0:9090; set --web.listen-address=127.0.0.1:9090.", "components": ["prometheus-pin"], "sources": ["prometheus-pin:s6d5f308b02a2"], "status": "REASONED"},
    "prometheus-tls": {"text": "web.yml tls_server_config cert_file/key_file enable TLS; validate with promtool check web-config.", "components": ["prometheus"], "sources": ["prometheus:sc48b506cc29a"], "status": "REASONED"},
    "database-panels": {"text": "Keep phpMyAdmin/pgAdmin behind proxy TLS/auth, restrict source IPs where supported and keep updated.", "components": ["phpmyadmin", "pgadmin"], "sources": ["phpmyadmin:s5f6c8965c539", "pgadmin:s2f7e33714435"], "status": "REASONED"},
    "pgadmin-login": {"text": "pgAdmin server mode has its own accounts/login.", "components": ["pgadmin"], "sources": ["pgadmin:s2f7e33714435"], "status": "REASONED"},
    "adminer-login": {"text": "Adminer uses database credentials, not a separate account store; server-side connections expose even private databases to login attempts.", "components": ["adminer"], "sources": ["adminer:sb5eda9397b18"], "status": "REASONED"},
    "adminer-file": {"text": "Renaming Adminer is no access control; require private access or proxy TLS/auth/MFA, updates and removal of unused copies.", "components": ["adminer"], "sources": ["adminer:sb5eda9397b18"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory sockets and Docker publications; a protected frontend or absent socket does not prove backend isolation.", "components": ["grafana-pin", "prometheus-pin"], "sources": ["grafana-pin:s2ade1bcff9aa", "prometheus-pin:s6d5f308b02a2"], "status": "REASONED", "verify": [1]},
    "verify-login": {"text": "Anonymous dashboard data is a finding; require denial or verified login challenge. Arbitrary redirects and DNS/TLS/proxy errors are inconclusive.", "components": ["mongo", "grafana", "prometheus", "phpmyadmin", "pgadmin", "adminer"], "sources": ["mongo:s69ec4eee2c85", "grafana:s7aa447405cc5", "prometheus:scce074c47e9c", "phpmyadmin:s5f6c8965c539", "pgadmin:s2f7e33714435", "adminer:sb5eda9397b18"], "status": "REASONED", "verify": [1]},
    "verify-data": {"text": "A 200 login shell proves nothing; require a known data route to succeed authorized and deny anonymous access; 404/server errors are inconclusive.", "components": ["mongo", "grafana", "prometheus", "phpmyadmin", "pgadmin", "adminer"], "sources": ["mongo:s69ec4eee2c85", "grafana:s7aa447405cc5", "prometheus:scce074c47e9c", "phpmyadmin:s5f6c8965c539", "pgadmin:s2f7e33714435", "adminer:sb5eda9397b18"], "status": "REASONED", "verify": [1]}
  }
}
---
# Admin panels: phpMyAdmin, pgAdmin, mongo-express, Grafana, Prometheus

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Keep panels private; public front doors need proxy TLS, authentication and MFA. RedisInsight has no dedicated source here. | Grafana docs unknown; Prometheus docs unknown; phpMyAdmin unknown; pgAdmin unknown; Adminer unknown | REASONED |
| mongo-enable: Recent login defaults off; current ENABLED and deprecated BASICAUTH fallback differ from some 1.0.x username-triggered builds. Set both flags and verify. | mongo-express unknown | REASONED |
| mongo-credentials: Set nonempty BASICAUTH_USERNAME/PASSWORD instead of admin/pass defaults. | mongo-express unknown | REASONED |
| mongo-database: Web Basic auth is separate from MongoDB credentials in ME_CONFIG_MONGODB_URL. | mongo-express unknown | REASONED |
| grafana-admin: First login uses admin/admin and prompts for replacement; use strong credentials and individual accounts. | Grafana docs unknown | REASONED |
| grafana-anonymous: Disable Grafana anonymous access if enabled. | Grafana docs unknown | REASONED |
| grafana-mfa: Prefer SSO with MFA at the identity provider. | Grafana docs unknown | REASONED |
| grafana-bind: Empty http_addr joins the port and binds all interfaces; set 127.0.0.1. | Grafana v13.2.2; Go net unknown | REASONED |
| grafana-tls: Native HTTPS uses server protocol=https, cert_file and cert_key. | Grafana docs unknown | REASONED |
| prometheus-auth: Authentication defaults off; web.config.file supplies basic_auth_users with bcrypt hashes. | Prometheus docs unknown | REASONED |
| prometheus-bcrypt: Use htpasswd -nB -C 12; the guide's bare -B cost 5 versus OWASP minimum 10 lacks an OWASP citation here. | Prometheus docs unknown | REASONED |
| prometheus-bind: Default 0.0.0.0:9090; set --web.listen-address=127.0.0.1:9090. | Prometheus v3.14.0 | REASONED |
| prometheus-tls: web.yml tls_server_config cert_file/key_file enable TLS; validate with promtool check web-config. | Prometheus docs unknown | REASONED |
| database-panels: Keep phpMyAdmin/pgAdmin behind proxy TLS/auth, restrict source IPs where supported and keep updated. | phpMyAdmin unknown; pgAdmin unknown | REASONED |
| pgadmin-login: pgAdmin server mode has its own accounts/login. | pgAdmin unknown | REASONED |
| adminer-login: Adminer uses database credentials, not a separate account store; server-side connections expose even private databases to login attempts. | Adminer unknown | REASONED |
| adminer-file: Renaming Adminer is no access control; require private access or proxy TLS/auth/MFA, updates and removal of unused copies. | Adminer unknown | REASONED |
| verify-listeners: Inventory sockets and Docker publications; a protected frontend or absent socket does not prove backend isolation. | Grafana v13.2.2; Prometheus v3.14.0 | REASONED |
| verify-login: Anonymous dashboard data is a finding; require denial or verified login challenge. Arbitrary redirects and DNS/TLS/proxy errors are inconclusive. | mongo-express unknown; Grafana docs unknown; Prometheus docs unknown; phpMyAdmin unknown; pgAdmin unknown; Adminer unknown | REASONED |
| verify-data: A 200 login shell proves nothing; require a known data route to succeed authorized and deny anonymous access; 404/server errors are inconclusive. | mongo-express unknown; Grafana docs unknown; Prometheus docs unknown; phpMyAdmin unknown; pgAdmin unknown; Adminer unknown | REASONED |
<!-- version-basis:end -->

Database and monitoring panels are the most-scanned targets on the internet, and several ship with known default credentials. One rule dominates everything tool-specific below: **an admin panel is never reachable from the public internet.** Bind it to loopback and reach it through SSH port forwarding, a VPN or tailnet ([tailscale.md](tailscale.md)), or Cloudflare Access ([cloudflare.md](cloudflare.md)); anything public sits behind a TLS proxy with its own authentication ([nginx.md](nginx.md), [caddy.md](caddy.md)) plus MFA ([mfa.md](mfa.md)).

## mongo-express

The web login is off by default on recent releases, and the enabling variable has changed across mongo-express versions: current releases read `ME_CONFIG_BASICAUTH_ENABLED` (the README marks the older `ME_CONFIG_BASICAUTH` deprecated but still honors it as a fallback), while some 1.0.x builds instead key the login off a non-empty `ME_CONFIG_BASICAUTH_USERNAME`. Rather than track the exact version boundary, set both flags, set your own non-empty credentials, and VERIFY that an unauthenticated request is rejected, because mongo-express can otherwise fall back to the widely-scanned `admin`:`pass`. Keep it private:

```
ME_CONFIG_BASICAUTH=true                       # older, now-deprecated enable flag, still honored as a fallback
ME_CONFIG_BASICAUTH_ENABLED=true               # the current enable flag; set both, then verify the login actually appears
ME_CONFIG_BASICAUTH_USERNAME=<your-admin>      # otherwise defaults to admin
ME_CONFIG_BASICAUTH_PASSWORD=<long random value>   # otherwise defaults to pass
```

These control only the web login; MongoDB credentials go in `ME_CONFIG_MONGODB_URL` ([mongodb.md](mongodb.md) hardens the database itself).

## Grafana

- First sign-in uses `admin`/`admin` and prompts for a new password; set a strong one immediately and create individual accounts for everyone else.
- Disable anonymous access if it was enabled, and prefer SSO with MFA enforced at the identity provider.
- Native HTTPS in `grafana.ini`:

```ini
[server]
protocol  = https
# bind loopback (Grafana's default http_addr is empty as of v13.2.2, which means all interfaces); reach it via a tunnel or proxy
http_addr = 127.0.0.1
cert_file = /etc/grafana/grafana.crt
cert_key  = /etc/grafana/grafana.key
```

## Prometheus

No authentication at all by default, and it listens on `0.0.0.0:9090` by default (as of v3.14.0). Give it a web configuration file and bind it to loopback, starting with `--web.listen-address=127.0.0.1:9090 --web.config.file=web.yml`:

```yaml
basic_auth_users:
  admin: $2b$12$REPLACE_WITH_BCRYPT_HASH    # htpasswd -nB -C 12 admin, hash part (bare -B is bcrypt cost 5, below OWASP 10)
```

The same file carries TLS (`tls_server_config` with `cert_file` and `key_file`; see the Prometheus TLS guide below). Validate with `promtool check web-config web.yml`. Exporters and Alertmanager need the same treatment; see [observability-components.md](observability-components.md).

## phpMyAdmin and pgAdmin

Neither belongs on a public vhost. Serve them only behind the proxy-level TLS and authentication of your web server guide, restrict by source IP where the proxy supports it, and keep them updated; both are perennial exploit targets. pgAdmin in server mode has its own login; treat its accounts per [authentication.md](authentication.md).

## Adminer

Adminer is database management in a single PHP file, and a filename like `adminer.php` or `adminer-<version>.php` is not an access control; renaming it or hiding the directory does not satisfy the never-public rule, since scanners enumerate those paths. It has no built-in account store of its own: by default the login form takes the database server's own address, username, and password, so an internet-reachable Adminer is a public interface for logging in to your database from the Adminer host. Because Adminer connects to the database server-side, that exposes the database to internet login attempts even when the database itself is not reachable from the internet, and older versions carry their own exploit history. The rule at the top of this guide applies without exception: keep it off a public vhost, reach it privately or behind the proxy's TLS, authentication, and MFA, restrict by source IP where you can, keep it updated, and delete the file (and any other copy) from the docroot when you are not using it.

## RedisInsight and similar tools

Keep them on loopback or a private network and reach them through the tunnels above. When in doubt, apply the generic pattern: loopback bind, TLS proxy, proxy or SSO authentication, MFA.

## Verify

REASONED: following block; panel sources below support the listener and anonymous front-page/data-route checks. No panel deployment or external test network is available here; no live run is recorded. The comments give expected denial, exposure and inconclusive outcomes.

```bash
# On the host: each panel listener should be loopback (127.0.0.1) or a deliberately chosen private address.
# Docker may publish to loopback OR install a NAT rule with no host listener, so also inspect the actual
# published addresses and ports (docker ps and the port mappings) and probe any public backend mapping too:
# a protected frontend does not prove a separately published backend port is closed.
ss -tlnp                                      # panel listeners: loopback or a private address only

# From OUTSIDE your network, with client proxies disabled so a proxy cannot answer for the panel. Read the
# BODY, not just the status: a login page and a dashboard can both be 200.
curl -q -g -sS --noproxy '*' -i 'https://panel.example.com/'
#   PASS: a denial from whatever protects this panel - the panel's own 401/403, the reverse proxy's, or a
#   Cloudflare Access challenge - or a redirect into that layer's login (which may be an external identity
#   provider). FINDING: a 200 that renders the dashboard or app content. An arbitrary redirect is inconclusive.
# SPA panels (Grafana, RedisInsight, a phpMyAdmin/Adminer login shell) return 200 for BOTH the login page and
# the dashboard, so also request a route you know returns real data when authorized, and require it be denied
# without credentials:
curl -q -g -sS --noproxy '*' -i 'https://panel.example.com/REPLACE_WITH_PROTECTED_PATH'   # keep the quotes; substitute inside them
#   Confirm that route returns data WITH valid auth first (a positive control); a 404, a server error, or an
#   unsubstituted placeholder is inconclusive, not a pass.
```

Run these from a second network against each panel's real hostname; a 200 that renders a dashboard, or any content past the login, without credentials is a finding, while a proxy, DNS, or TLS error is inconclusive, not a pass.

## Sources (checked September 2026)

- mongo-express README (defaults and variables): https://github.com/mongo-express/mongo-express
- Grafana configuration and HTTPS: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/ and https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/
- Prometheus basic auth and TLS guides: https://prometheus.io/docs/guides/basic-auth/ and https://prometheus.io/docs/guides/tls-encryption/
- phpMyAdmin documentation: https://www.phpmyadmin.net/docs/ and pgAdmin documentation: https://www.pgadmin.org/docs/
- Adminer, database management in a single PHP file (login uses the database server's own credentials): https://www.adminer.org/
- Prometheus `--web.listen-address` default `0.0.0.0:9090` (pinned tag v3.14.0): https://github.com/prometheus/prometheus/blob/v3.14.0/cmd/prometheus/main.go#L424-L425
- Grafana default `http_addr` is empty (pinned tag v13.2.2): https://github.com/grafana/grafana/blob/v13.2.2/conf/defaults.ini#L50
- Grafana joins `http_addr` with the port into the server address (pinned tag v13.2.2): https://github.com/grafana/grafana/blob/v13.2.2/pkg/api/http_server.go#L467-L469
- Grafana listens on that address with `net.Listen("tcp", ...)` (pinned tag v13.2.2): https://github.com/grafana/grafana/blob/v13.2.2/pkg/api/http_server.go#L568
- Go `net.Listen` with an empty host listens on all available unicast and anycast addresses of the local system: https://pkg.go.dev/net#Listen
