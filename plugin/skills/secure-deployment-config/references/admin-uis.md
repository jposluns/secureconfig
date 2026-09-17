# Admin panels: phpMyAdmin, pgAdmin, mongo-express, Grafana, Prometheus

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
# bind loopback (Grafana's default http_addr is empty = all interfaces); reach it via a tunnel or proxy
http_addr = 127.0.0.1
cert_file = /etc/grafana/grafana.crt
cert_key  = /etc/grafana/grafana.key
```

## Prometheus

No authentication at all by default, and it listens on `0.0.0.0:9090` by default. Give it a web configuration file and bind it to loopback, starting with `--web.listen-address=127.0.0.1:9090 --web.config.file=web.yml`:

```yaml
basic_auth_users:
  admin: $2b$12$REPLACE_WITH_BCRYPT_HASH    # htpasswd -nB -C 12 admin, hash part (bare -B is bcrypt cost 5, below OWASP 10)
```

The same file carries TLS (`tls_server_config` with `cert_file` and `key_file`; see the Prometheus TLS guide below). Validate with `promtool check web-config web.yml`. Exporters and Alertmanager need the same treatment.

## phpMyAdmin and pgAdmin

Neither belongs on a public vhost. Serve them only behind the proxy-level TLS and authentication of your web server guide, restrict by source IP where the proxy supports it, and keep them updated; both are perennial exploit targets. pgAdmin in server mode has its own login; treat its accounts per [authentication.md](authentication.md).

## Adminer

Adminer is database management in a single PHP file, and a filename like `adminer.php` or `adminer-<version>.php` is not an access control; renaming it or hiding the directory does not satisfy the never-public rule, since scanners enumerate those paths. It has no built-in account store of its own: by default the login form takes the database server's own address, username, and password, so an internet-reachable Adminer is a public interface for logging in to your database from the Adminer host. Because Adminer connects to the database server-side, that exposes the database to internet login attempts even when the database itself is not reachable from the internet, and older versions carry their own exploit history. The rule at the top of this guide applies without exception: keep it off a public vhost, reach it privately or behind the proxy's TLS, authentication, and MFA, restrict by source IP where you can, keep it updated, and delete the file (and any other copy) from the docroot when you are not using it.

## RedisInsight and similar tools

Keep them on loopback or a private network and reach them through the tunnels above. When in doubt, apply the generic pattern: loopback bind, TLS proxy, proxy or SSO authentication, MFA.

## Verify

```bash
# On the host: every panel listener must be loopback only. Under Docker a published port shows as
# docker-proxy on 0.0.0.0 (still exposed) and a NAT-only publish may not appear here, so treat the
# external probe below as authoritative, not this list.
ss -tlnp                                      # panels on 127.0.0.1 (or a private address) only

# From OUTSIDE your network, with client proxies disabled so a proxy cannot answer for the panel:
# 1) unauthenticated GET to the root: want the panel's OWN 401/403, never a 200 that serves the app
curl -q -sS --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://panel.example.com/
# 2) if it redirects, read the target: a pass ONLY if Location is the panel's own login/challenge
#    (e.g. /login); any other 3xx, or a 200 serving the app, is a finding
curl -q -sSI --noproxy '*' https://panel.example.com/
# 3) SPA panels (Grafana, RedisInsight, a phpMyAdmin/Adminer login shell) return 200 for BOTH the login
#    page and the dashboard, so also request a known protected route and require rejection (no data):
curl -q -sS --noproxy '*' -o /dev/null -w 'http=%{http_code}\n' https://panel.example.com/REPLACE_WITH_PROTECTED_PATH
```

Run these from a second network against each panel's real hostname; a 200 that renders a dashboard, or any content past the login, without credentials is a finding, while a proxy, DNS, or TLS error is inconclusive, not a pass.

## Sources (checked September 2026)

- mongo-express README (defaults and variables): https://github.com/mongo-express/mongo-express
- Grafana configuration and HTTPS: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/ and https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/
- Prometheus basic auth and TLS guides: https://prometheus.io/docs/guides/basic-auth/ and https://prometheus.io/docs/guides/tls-encryption/
- phpMyAdmin documentation: https://www.phpmyadmin.net/docs/ and pgAdmin documentation: https://www.pgadmin.org/docs/
- Adminer, database management in a single PHP file (login uses the database server's own credentials): https://www.adminer.org/
