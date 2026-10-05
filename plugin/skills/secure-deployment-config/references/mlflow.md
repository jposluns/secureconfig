---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "580906eef700b827600cbfb61873eccc074b864216a9f8f5e1dc9293b22188ff",
  "components": {
    "docs": {
      "name": "MLflow documentation",
      "basis": "unknown",
      "sources": {
        "scbbc07258943": "https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/",
        "sc3a2d70cabf9": "https://mlflow.org/docs/latest/api_reference/auth/rest-api.html",
        "s5b79d1871e0b": "https://mlflow.org/docs/latest/api_reference/cli.html",
        "s2517159af609": "https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server",
        "s996e587e947a": "https://mlflow.org/docs/latest/api_reference/rest-api.html",
        "s559e7a8271b9": "https://mlflow.org/docs/latest/api_reference/cli.html#mlflow"
      }
    },
    "source": {
      "name": "MLflow pinned source",
      "basis": "v3.16.1",
      "sources": {
        "sf7285d252e29": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/utils/cli_args.py#L162-L180",
        "sa3993a9b625f": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L369-L541",
        "sd775f10c4d07": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/server/auth/__init__.py#L6008-L6021",
        "s349a81b9478e": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/server/__init__.py#L401-L402",
        "s99d30948902f": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L85-L86",
        "s687f1c9977cd": "https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L94-L105"
      }
    },
    "middleware-min": {
      "name": "MLflow security middleware minimum",
      "basis": "3.5.0",
      "sources": {
        "s2517159af609": "https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server"
      }
    },
    "docker": {
      "name": "Docker Engine loopback publication minimum",
      "basis": "28.0.0",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "nginx": {
      "name": "nginx proxy implementation",
      "basis": "release-1.28.0",
      "sources": {
        "s6dfa81e36717": "https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_proxy_module.c#L305-L310"
      }
    },
    "caddy": {
      "name": "Caddy reverse proxy parser",
      "basis": "v2.11.4",
      "sources": {
        "s52039756d4f4": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L40",
        "s9dde4a2bda4c": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L58-L62"
      }
    },
    "iproute2": {
      "name": "iproute2 ss manual",
      "basis": "v6.12.0",
      "sources": {
        "s2afc4764d5bb": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L33-L34",
        "sfaa932c2ca13": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L43-L44",
        "sd295f82d643f": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L162-L163",
        "s65278ee45850": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L374-L375"
      }
    }
  },
  "claims": {
    "default-host": {"text": "v3.16.1 defaults to 127.0.0.1 unless MLFLOW_HOST overrides it; explicitly bind privately and do not treat --host as an authentication setting.", "components": ["source"], "sources": ["source:sf7285d252e29", "source:sa3993a9b625f"], "status": "REASONED"},
    "default-port": {"text": "v3.16.1 serves the tracking UI and REST API on port 5000 unless MLFLOW_PORT overrides it.", "components": ["source"], "sources": ["source:sf7285d252e29", "source:sa3993a9b625f"], "status": "REASONED"},
    "default-auth": {"text": "Authentication is opt-in; a reachable server without the auth app permits reading, changing and deleting tracking resources and proxied artifacts.", "components": ["docs"], "sources": ["docs:scbbc07258943", "docs:s2517159af609"], "status": "REASONED"},
    "container-bind": {"text": "Normal bridge NAT requires host loopback publication 127.0.0.1:5000:5000 and --host 0.0.0.0 inside the container; container loopback cannot serve the publication. Before Docker 28.0.0, same-layer-2 hosts could reach loopback-published ports.", "components": ["docker", "docs"], "sources": ["docker:s1e53417c513d", "docs:s5b79d1871e0b"], "status": "REASONED"},
    "middleware-scope": {"text": "Security middleware requires MLflow 3.5.0 or newer and the default Uvicorn server; --gunicorn-opts and --waitress-opts do not use it.", "components": ["middleware-min", "docs"], "sources": ["middleware-min:s2517159af609", "docs:s5b79d1871e0b", "docs:s2517159af609"], "status": "REASONED"},
    "host-allowlist": {"text": "Set --allowed-hosts mlflow.example.com for access beyond loopback; defaults admit localhost, 127.0.0.1, [::1], 0.0.0.0 and private ranges as Host headers, not client-source firewall rules.", "components": ["docs"], "sources": ["docs:s5b79d1871e0b", "docs:s2517159af609"], "status": "REASONED"},
    "cors": {"text": "Set --cors-allowed-origins https://mlflow.example.com for the intended browser origin.", "components": ["docs"], "sources": ["docs:s5b79d1871e0b", "docs:s2517159af609"], "status": "REASONED"},
    "middleware-disable": {"text": "Do not use --disable-security-middleware outside a test.", "components": ["docs"], "sources": ["docs:s5b79d1871e0b", "docs:s2517159af609"], "status": "REASONED"},
    "tls": {"text": "There are no dedicated server TLS flags; --uvicorn-opts can forward --ssl-keyfile/--ssl-certfile. Use a TLS proxy to 127.0.0.1:5000 or a tunnel/tailnet and set the allowed public hostname.", "components": ["docs", "nginx", "caddy"], "sources": ["docs:s5b79d1871e0b", "docs:s2517159af609", "nginx:s6dfa81e36717", "caddy:s52039756d4f4", "caddy:s9dde4a2bda4c"], "status": "REASONED"},
    "client-tls": {"text": "Use MLFLOW_TRACKING_URI=https://mlflow.example.com and never enable MLFLOW_TRACKING_INSECURE_TLS in production.", "components": ["docs"], "sources": ["docs:s2517159af609"], "status": "REASONED"},
    "auth-app": {"text": "Install mlflow[auth] and run --app-name basic-auth; client username/password variables alone enable no server authentication. The September 2026 documentation has no experimental label.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "csrf-key": {"text": "Provision a long random MLFLOW_FLASK_SERVER_SECRET_KEY identical on every replica through a protected server.env file, mode 0600, with protected directories and no other-account ACL access; keep file and backups out of source control.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "env-file": {"text": "Global --env-file loads dotenv before the server command without overriding existing environment; clear inherited key/config-path variables and require a readable regular non-symlink file before launching.", "components": ["docs", "source"], "sources": ["docs:s559e7a8271b9", "source:s99d30948902f", "source:s687f1c9977cd"], "status": "REASONED"},
    "key-exposure": {"text": "Only the file path reaches the launch command; MLflow v3.16.1 loads the key into its environment and forwards it to workers, retaining same-account/root memory and inheriting-process environment exposure.", "components": ["source", "docs"], "sources": ["source:sd775f10c4d07", "source:s349a81b9478e", "docs:s559e7a8271b9", "source:s99d30948902f", "source:s687f1c9977cd"], "status": "REASONED"},
    "admin-bootstrap": {"text": "No default admin password: first start requires at least 12 characters from MLFLOW_AUTH_ADMIN_PASSWORD or admin_password, rejects password1234 and fails without a password; an already-bootstrapped admin needs no resupply.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "default-permission": {"text": "default_permission is READ on every resource; set NO_PERMISSIONS in the auth configuration to remove that default grant.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "auth-database": {"text": "database_uri defaults to basic_auth.db in the working directory; use a central database for multiple nodes, as in the PostgreSQL auth-database example.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "auth-config": {"text": "MLFLOW_AUTH_CONFIG_PATH selects basic_auth.ini; authorization_function accepts module:function for custom authentication, while the shipped scheme is HTTP Basic.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "password-rotation": {"text": "PATCH /api/2.0/mlflow/users/update-password takes username and password; the example feeds current and new passwords through curl config stdin with JSON/config escaping.", "components": ["docs", "curl"], "sources": ["docs:sc3a2d70cabf9", "curl:s2b2686afaf41"], "status": "REASONED"},
    "user-creation": {"text": "User creation requires admin credentials at /signup or POST /api/2.0/mlflow/users/create; give humans individual accounts and CI a separate low-permission user.", "components": ["docs"], "sources": ["docs:scbbc07258943", "docs:sc3a2d70cabf9"], "status": "REASONED"},
    "client-credentials": {"text": "~/.mlflow/credentials stores passwords unencrypted; prefer runtime-injected MLFLOW_TRACKING_USERNAME/MLFLOW_TRACKING_PASSWORD.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "rate-limit": {"text": "The UI has no login-attempt limit and Basic auth is checked on every protected API request; rate-limit all authentication-bearing routes at the proxy and protect password transport with TLS.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "mfa": {"text": "The Basic-auth app has no MFA; front it with an identity-aware layer. The guide names external proxy options without recording their vendor sources here.", "components": ["docs"], "sources": ["docs:scbbc07258943"], "status": "REASONED"},
    "proxy-token": {"text": "MLFLOW_TRACKING_TOKEN supplies a proxy bearer token, but Basic credentials take precedence; confirm both auth layers survive, including proxies needing separate service-token headers. Cloudflare header syntax is not sourced here.", "components": ["docs"], "sources": ["docs:s2517159af609"], "status": "REASONED"},
    "artifact-proxy": {"text": "--serve-artifacts defaults on; --artifacts-destination s3://bucket lets the server proxy reads/writes for proxied experiments, holding storage credentials so clients need none.", "components": ["docs"], "sources": ["docs:s5b79d1871e0b", "docs:s2517159af609"], "status": "REASONED"},
    "artifact-existing": {"text": "Pre-existing experiments and explicit direct artifact locations retain their locations outside tracking-server permission enforcement; inspect locations and apply storage IAM directly.", "components": ["docs"], "sources": ["docs:s2517159af609"], "status": "REASONED"},
    "artifact-direct": {"text": "With --no-serve-artifacts every client needs storage credentials and tracking-server permissions no longer gate artifacts; use environment or instance-role credentials, not repository/Compose secrets.", "components": ["docs"], "sources": ["docs:s2517159af609"], "status": "REASONED"},
    "verify-bind": {"text": "Read every listener and require 5000 on 127.0.0.1; ss itself has no vendor citation here.", "components": ["source", "iproute2"], "sources": ["source:sf7285d252e29", "source:sa3993a9b625f", "iproute2:s2afc4764d5bb", "iproute2:sfaa932c2ca13", "iproute2:sd295f82d643f", "iproute2:s65278ee45850"], "status": "REASONED", "verify": [1]},
    "verify-network": {"text": "Outside :5000 must form no TCP connection: time_connect stays 0.000000 with a connection-level failure. A handshake or HTTP response means exposure; DNS/local socket errors are inconclusive.", "components": ["curl", "docs"], "sources": ["curl:s2b2686afaf41", "docs:s5b79d1871e0b"], "status": "REASONED", "verify": [1]},
    "verify-public-auth": {"text": "POST experiments/search with a minimal body: anonymous and wrong-password requests should return 401, valid admin 200; an open backend returns anonymous 200. Proxy credentials may also be needed; shell success is not a pass.", "components": ["docs", "curl"], "sources": ["docs:scbbc07258943", "docs:s996e587e947a", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-backend-auth": {"text": "Repeat anonymous 401/admin 200 directly on loopback with Host: mlflow.example.com; an allowlist Host rejection is 403 before auth, and a proxy-only denial proves no backend enforcement.", "components": ["docs"], "sources": ["docs:scbbc07258943", "docs:s5b79d1871e0b", "docs:s996e587e947a"], "status": "REASONED", "verify": [1]},
    "verify-authorization": {"text": "Search filters visible experiments and does not prove authorization denial. First GET a real experiment as admin for 200, then the same backend resource as a low-permission user for 403; 401 means bad credentials and a failed admin control is inconclusive.", "components": ["docs"], "sources": ["docs:scbbc07258943", "docs:s996e587e947a"], "status": "REASONED", "verify": [1]}
  }
}
---
# MLflow tracking server: no authentication by default

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| default-host: v3.16.1 defaults to 127.0.0.1 unless MLFLOW_HOST overrides it; explicitly bind privately and do not treat --host as an authentication setting. | MLflow pinned source v3.16.1 | REASONED |
| default-port: v3.16.1 serves the tracking UI and REST API on port 5000 unless MLFLOW_PORT overrides it. | MLflow pinned source v3.16.1 | REASONED |
| default-auth: Authentication is opt-in; a reachable server without the auth app permits reading, changing and deleting tracking resources and proxied artifacts. | MLflow documentation unknown | REASONED |
| container-bind: Normal bridge NAT requires host loopback publication 127.0.0.1:5000:5000 and --host 0.0.0.0 inside the container; container loopback cannot serve the publication. Before Docker 28.0.0, same-layer-2 hosts could reach loopback-published ports. | Docker Engine loopback publication minimum 28.0.0; MLflow documentation unknown | REASONED |
| middleware-scope: Security middleware requires MLflow 3.5.0 or newer and the default Uvicorn server; --gunicorn-opts and --waitress-opts do not use it. | MLflow security middleware minimum 3.5.0; MLflow documentation unknown | REASONED |
| host-allowlist: Set --allowed-hosts mlflow.example.com for access beyond loopback; defaults admit localhost, 127.0.0.1, [::1], 0.0.0.0 and private ranges as Host headers, not client-source firewall rules. | MLflow documentation unknown | REASONED |
| cors: Set --cors-allowed-origins https://mlflow.example.com for the intended browser origin. | MLflow documentation unknown | REASONED |
| middleware-disable: Do not use --disable-security-middleware outside a test. | MLflow documentation unknown | REASONED |
| tls: There are no dedicated server TLS flags; --uvicorn-opts can forward --ssl-keyfile/--ssl-certfile. Use a TLS proxy to 127.0.0.1:5000 or a tunnel/tailnet and set the allowed public hostname. | MLflow documentation unknown; nginx proxy implementation release-1.28.0; Caddy reverse proxy parser v2.11.4 | REASONED |
| client-tls: Use MLFLOW_TRACKING_URI=https://mlflow.example.com and never enable MLFLOW_TRACKING_INSECURE_TLS in production. | MLflow documentation unknown | REASONED |
| auth-app: Install mlflow[auth] and run --app-name basic-auth; client username/password variables alone enable no server authentication. The September 2026 documentation has no experimental label. | MLflow documentation unknown | REASONED |
| csrf-key: Provision a long random MLFLOW_FLASK_SERVER_SECRET_KEY identical on every replica through a protected server.env file, mode 0600, with protected directories and no other-account ACL access; keep file and backups out of source control. | MLflow documentation unknown | REASONED |
| env-file: Global --env-file loads dotenv before the server command without overriding existing environment; clear inherited key/config-path variables and require a readable regular non-symlink file before launching. | MLflow documentation unknown; MLflow pinned source v3.16.1 | REASONED |
| key-exposure: Only the file path reaches the launch command; MLflow v3.16.1 loads the key into its environment and forwards it to workers, retaining same-account/root memory and inheriting-process environment exposure. | MLflow pinned source v3.16.1; MLflow documentation unknown | REASONED |
| admin-bootstrap: No default admin password: first start requires at least 12 characters from MLFLOW_AUTH_ADMIN_PASSWORD or admin_password, rejects password1234 and fails without a password; an already-bootstrapped admin needs no resupply. | MLflow documentation unknown | REASONED |
| default-permission: default_permission is READ on every resource; set NO_PERMISSIONS in the auth configuration to remove that default grant. | MLflow documentation unknown | REASONED |
| auth-database: database_uri defaults to basic_auth.db in the working directory; use a central database for multiple nodes, as in the PostgreSQL auth-database example. | MLflow documentation unknown | REASONED |
| auth-config: MLFLOW_AUTH_CONFIG_PATH selects basic_auth.ini; authorization_function accepts module:function for custom authentication, while the shipped scheme is HTTP Basic. | MLflow documentation unknown | REASONED |
| password-rotation: PATCH /api/2.0/mlflow/users/update-password takes username and password; the example feeds current and new passwords through curl config stdin with JSON/config escaping. | MLflow documentation unknown; curl minimum write-out version 7.75.0 | REASONED |
| user-creation: User creation requires admin credentials at /signup or POST /api/2.0/mlflow/users/create; give humans individual accounts and CI a separate low-permission user. | MLflow documentation unknown | REASONED |
| client-credentials: ~/.mlflow/credentials stores passwords unencrypted; prefer runtime-injected MLFLOW_TRACKING_USERNAME/MLFLOW_TRACKING_PASSWORD. | MLflow documentation unknown | REASONED |
| rate-limit: The UI has no login-attempt limit and Basic auth is checked on every protected API request; rate-limit all authentication-bearing routes at the proxy and protect password transport with TLS. | MLflow documentation unknown | REASONED |
| mfa: The Basic-auth app has no MFA; front it with an identity-aware layer. The guide names external proxy options without recording their vendor sources here. | MLflow documentation unknown | REASONED |
| proxy-token: MLFLOW_TRACKING_TOKEN supplies a proxy bearer token, but Basic credentials take precedence; confirm both auth layers survive, including proxies needing separate service-token headers. Cloudflare header syntax is not sourced here. | MLflow documentation unknown | REASONED |
| artifact-proxy: --serve-artifacts defaults on; --artifacts-destination s3://bucket lets the server proxy reads/writes for proxied experiments, holding storage credentials so clients need none. | MLflow documentation unknown | REASONED |
| artifact-existing: Pre-existing experiments and explicit direct artifact locations retain their locations outside tracking-server permission enforcement; inspect locations and apply storage IAM directly. | MLflow documentation unknown | REASONED |
| artifact-direct: With --no-serve-artifacts every client needs storage credentials and tracking-server permissions no longer gate artifacts; use environment or instance-role credentials, not repository/Compose secrets. | MLflow documentation unknown | REASONED |
| verify-bind: Read every listener and require 5000 on 127.0.0.1; ss itself has no vendor citation here. | MLflow pinned source v3.16.1; iproute2 ss manual v6.12.0 | REASONED |
| verify-network: Outside :5000 must form no TCP connection: time_connect stays 0.000000 with a connection-level failure. A handshake or HTTP response means exposure; DNS/local socket errors are inconclusive. | curl minimum write-out version 7.75.0; MLflow documentation unknown | REASONED |
| verify-public-auth: POST experiments/search with a minimal body: anonymous and wrong-password requests should return 401, valid admin 200; an open backend returns anonymous 200. Proxy credentials may also be needed; shell success is not a pass. | MLflow documentation unknown; curl minimum write-out version 7.75.0 | REASONED |
| verify-backend-auth: Repeat anonymous 401/admin 200 directly on loopback with Host: mlflow.example.com; an allowlist Host rejection is 403 before auth, and a proxy-only denial proves no backend enforcement. | MLflow documentation unknown | REASONED |
| verify-authorization: Search filters visible experiments and does not prove authorization denial. First GET a real experiment as admin for 200, then the same backend resource as a low-permission user for 403; 401 means bad credentials and a failed admin control is inconclusive. | MLflow documentation unknown | REASONED |
<!-- version-basis:end -->

`mlflow server` serves the tracking UI and REST API at `http://127.0.0.1:5000` (as of v3.16.1, unless `MLFLOW_HOST` or `MLFLOW_PORT` is set) and performs no authentication: anyone who can reach the port can read, alter, and delete experiments, runs, registered models, and (with artifact proxying on) the artifacts themselves. Authentication is opt-in through a separate app, and the server has no dedicated TLS flags (though `mlflow server --uvicorn-opts` can forward `--ssl-keyfile`/`--ssl-certfile` to the default Uvicorn server); MLflow's tracking-server documentation recommends a reverse proxy or VPN for both.

## 1. Bind privately

The defaults are already loopback:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

The CLI help for `--host` says it plainly: "This is NOT a security setting". Do not switch to `--host 0.0.0.0` on a machine with a public interface. In Docker the two binds are different things: the host publishes on loopback (`-p 127.0.0.1:5000:5000`, which Docker's port-publishing docs say only the Docker host can reach, assuming a normal bridge-network NAT setup and a Docker version at or after 28.0.0; earlier releases could let hosts on the same layer-2 network reach a loopback-published port), while inside the container the server must listen on the container's own interface (`--host 0.0.0.0` there, private to the Compose network and the host), because a process bound to the container's `127.0.0.1` is not reachable through the published port at all. See [docker.md](docker.md). If the server must listen beyond loopback for a proxy on another host, set `--allowed-hosts mlflow.example.com` (these security-middleware flags need MLflow 3.5.0 or newer and the default Uvicorn server, not `--gunicorn-opts`/`--waitress-opts`; the default validates the request's Host header against localhost, `127.0.0.1`, `[::1]`, `0.0.0.0`, and private ranges, which is a Host-header check, not a client-source firewall) and `--cors-allowed-origins https://mlflow.example.com`, and never use `--disable-security-middleware` outside a test.

## 2. TLS from a fronting proxy

`mlflow server` has no dedicated certificate flags (though `--uvicorn-opts` can forward `--ssl-keyfile`/`--ssl-certfile` to Uvicorn). Terminate TLS in nginx or Caddy per [nginx.md](nginx.md)/[caddy.md](caddy.md) with `proxy_pass http://127.0.0.1:5000` or `reverse_proxy 127.0.0.1:5000`, a certificate from [free-certificates.md](free-certificates.md), and `--allowed-hosts` set to the public hostname; or use a tunnel or tailnet ([cloudflare.md](cloudflare.md), [tailscale.md](tailscale.md)). Point clients at `MLFLOW_TRACKING_URI=https://mlflow.example.com`, and never set `MLFLOW_TRACKING_INSECURE_TLS=true` in production (MLflow's own docs say the same).

## 3. Turn on the built-in basic auth

MLflow ships an HTTP basic-auth app that stores users and per-resource permissions in a database (as of September 2026 the current documentation page carries no experimental label; verify before relying on it). The client-side `MLFLOW_TRACKING_USERNAME`/`MLFLOW_TRACKING_PASSWORD` variables do nothing on their own; the server must run this app.

Provision `/etc/mlflow/server.env` through your secret manager as a regular file owned by the server account, mode `0600`, in a directory other accounts cannot traverse, write to or replace, with no ACL granting them access. It must contain a dotenv assignment for `MLFLOW_FLASK_SERVER_SECRET_KEY` with a long random value, identical on every replica. Keep the file and its backups out of source control. The block assumes this file and the auth configuration below are provisioned before startup and a fresh, trusted shell.

The global `mlflow --env-file` option loads the file before executing the server command and does not override existing environment values. Clear inherited values first so the file supplies the key:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n MLFLOW_FLASK_SERVER_SECRET_KEY MLFLOW_AUTH_CONFIG_PATH &&
    unset -v MLFLOW_FLASK_SERVER_SECRET_KEY MLFLOW_AUTH_CONFIG_PATH; } 2>/dev/null ||
    { echo 'cannot clear MLflow launch variables in this shell; not starting'; exit 2; }
  if [ ! -f /etc/mlflow/server.env ] || [ -L /etc/mlflow/server.env ] || [ ! -r /etc/mlflow/server.env ]; then
    echo 'need a readable regular /etc/mlflow/server.env file, not a symlink; not starting'; exit 2
  fi
  pip install 'mlflow[auth]' || exit 2
  MLFLOW_AUTH_CONFIG_PATH=/etc/mlflow/basic_auth.ini \
    mlflow --env-file /etc/mlflow/server.env server --app-name basic-auth
)
```

Only the file path reaches the launch command; the shell never reads or exports the key. MLflow loads it into its own environment and forwards it to workers (traced at v3.16.1 in the sources below), so it remains exposed to the same account and root in process memory and, for inheriting processes, `/proc/<pid>/environ` throughout their lifetimes. A protected file does not remove that server-side exposure.

Current MLflow has no default admin password: the first start requires an admin password of at least 12 characters, supplied as `MLFLOW_AUTH_ADMIN_PASSWORD` or as `admin_password` in the configuration file, and it rejects the legacy `password1234`, so startup fails without one. Set a strong password before that first start (an already-bootstrapped server does not need it re-supplied on later restarts):

```ini
# /etc/mlflow/basic_auth.ini
[mlflow]
# default is READ on every resource
default_permission = NO_PERMISSIONS
database_uri = postgresql://mlflow_auth:REPLACE_WITH_LONG_RANDOM_VALUE@127.0.0.1:5432/mlflow_auth
admin_username = admin
admin_password = REPLACE_WITH_LONG_RANDOM_VALUE
```

`database_uri` defaults to a SQLite file `basic_auth.db` in the working directory; MLflow recommends a central database for multi-node deployments. The same file can name an `authorization_function` (`module:function`) for a custom scheme, but the shipped one is basic auth. To rotate the admin password on a running server:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # Both passwords you substitute on the set -- line enter shell history.
  # Clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CURRENT_ADMIN_PASSWORD' 'REPLACE_WITH_LONG_RANDOM_VALUE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the current admin password on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the new password on the set -- line above; not probing"; exit ;; esac
  # Both passwords reach curl on stdin via a config file (curl --config -), never
  # argv: -u admin:PASSWORD and the -d body are world-readable in /proc/<pid>/cmdline.
  # Escape backslashes then quotes for the config; the new password is JSON-escaped
  # first, then the whole JSON body is config-escaped.
  set -- "${1//\\/\\\\}" "${2//\\/\\\\}"
  set -- "${1//\"/\\\"}" "${2//\"/\\\"}"
  set -- "$1" "{\"username\":\"admin\",\"password\":\"$2\"}"
  set -- "$1" "${2//\\/\\\\}"
  set -- "$1" "${2//\"/\\\"}"
  printf 'user = "admin:%s"\ndata-binary = "%s"\n' "$1" "$2" | curl -q -sS --config - -X PATCH -H 'Content-Type: application/json' https://mlflow.example.com/api/2.0/mlflow/users/update-password
)
```

Creating users requires admin credentials (UI at `/signup`, or `POST /api/2.0/mlflow/users/create`). Give humans individual accounts and CI its own low-permission user per [authentication.md](authentication.md); `~/.mlflow/credentials` stores passwords unencrypted, so prefer the environment variables injected at runtime. The documentation notes that the UI has no limit on login attempts, and basic auth is checked on every protected API request, so rate-limit the authentication-bearing routes at the proxy (not only the login path) per [nginx.md](nginx.md); and because basic auth sends the password with every request ([authentication.md](authentication.md)), step 2 comes first.

MFA: the basic-auth app has none. Put an identity-aware layer in front (Cloudflare Access, Authelia, oauth2-proxy per [mfa.md](mfa.md)); MLflow clients can pass a proxy bearer token via `MLFLOW_TRACKING_TOKEN`, but MLflow's own basic-auth credentials take precedence over it, and some proxies (Cloudflare Access service tokens) expect their own client-ID/secret headers rather than a bearer, so confirm the chosen combination preserves both the proxy and the MLflow auth layers.

## 4. Artifact store credentials

With `--serve-artifacts` (the default) and `--artifacts-destination s3://bucket`, the server proxies every artifact read and write for experiments recorded under the proxied store, so it holds the storage credentials and clients need none. Experiments created before proxying, or with an explicit direct artifact location, keep that location and stay reachable independently of the tracking server's permissions, so apply storage IAM directly and inspect existing experiment locations rather than assuming proxying covers them. Supply them through the environment or an instance role, never in a compose file or the repository ([secrets.md](secrets.md), [object-storage.md](object-storage.md)). With `--no-serve-artifacts`, every client needs its own storage credentials and the tracking server's permissions no longer gate the artifacts.

## Verify

```bash
# REASONED: listener and authentication checks follow the cited MLflow documentation; no running basic-auth server is available.
ss -tlnp   # read every listener; 5000: 127.0.0.1 only
# from another machine, checking the port is unreachable from outside. The pass is that no TCP
# connection formed: time_connect stays 0.000000 and err names a connection-level failure (refused, no
# route, or a filtered-port connect timeout). A non-zero time_connect, or any http code, means the
# handshake completed and the port answered. A name-resolution or local socket error is inconclusive.
(                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVER_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the server's public address on the set -- line above; not probing" ;;
    *) curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:5000/" || true ;;
  esac
)
# experiments/search is a POST endpoint, so each check posts a minimal body. --noproxy so no client
# proxy answers. A 401 at mlflow.example.com can come from the fronting proxy OR from MLflow's own basic
# auth, so the backend check below proves MLflow itself enforces it, not just the proxy. These are
# MANUAL checks: each command prints its HTTP status for you to compare with the comment; curl exits 0
# for 401/403/404 too, so shell success is NOT a pass, and an open MLflow backend answers the anonymous
# search with 200. If you front MLflow with an identity-aware proxy (Cloudflare Access etc., the MFA
# option in step 3) instead of plain basic auth, the public https probes also need that proxy's own
# credentials (its service-token headers), and a denial from that proxy is distinct from MLflow's own
# backend 401/403. The credentials below reach curl through a config file on stdin (curl --config -),
# never argv, because -u user:password is world-readable via ps / /proc/<pid>/cmdline; stdin protects
# the argv channel only, not shell history or set -x tracing. Substitute each password INSIDE the
# single quotes on the set -- line; a password containing a literal apostrophe must be written '\'' there.
(
  # Each credential reaches curl on stdin via a config file (curl --config -), never
  # argv; -u user:password is world-readable in /proc/<pid>/cmdline on a shared host.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ADMIN_PASSWORD' 'REPLACE_WITH_LOWPERM_USER' 'REPLACE_WITH_LOWPERM_PASSWORD' 'REPLACE_WITH_A_REAL_EXPERIMENT_ID'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 4 ] || { echo "the set -- line needs exactly 4 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the admin password on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the low-permission user on the set -- line above; not probing"; exit ;; esac
  case "$3" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the low-permission password on the set -- line above; not probing"; exit ;; esac
  case "$4" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute a real experiment id on the set -- line above; not probing"; exit ;; esac
  set -- "${1//\\/\\\\}" "${2//\\/\\\\}" "${3//\\/\\\\}" "$4"
  set -- "${1//\"/\\\"}" "${2//\"/\\\"}" "${3//\"/\\\"}" "$4"
  curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
    https://mlflow.example.com/api/2.0/mlflow/experiments/search   # 401: no credentials
  printf 'user = "admin:%s"\n' "$1" | curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
    --config - https://mlflow.example.com/api/2.0/mlflow/experiments/search   # positive control: 200 with the admin password
  printf 'user = "admin:not-the-real-password"\n' | curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
    --config - https://mlflow.example.com/api/2.0/mlflow/experiments/search   # 401: a wrong password is refused (MLflow rejects the legacy password1234 by design, so there is no default to "remove")
  # On the MLflow host, the same no-credential POST must ALSO be 401 - a 401 only at the proxy would leave
  # MLflow open behind it. On the host, --allowed-hosts rejects a bare 127.0.0.1 Host with 403 before auth,
  # so send the allowed Host header:
  curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -X POST -H 'Host: mlflow.example.com' -H 'Content-Type: application/json' -d '{"max_results":1}' \
    http://127.0.0.1:5000/api/2.0/mlflow/experiments/search   # 401: no credentials, on the backend
  printf 'user = "admin:%s"\n' "$1" | curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -X POST -H 'Host: mlflow.example.com' -H 'Content-Type: application/json' -d '{"max_results":1}' \
    --config - http://127.0.0.1:5000/api/2.0/mlflow/experiments/search   # backend positive control: 200 with the admin password
  # Authorization, not just authentication: experiments/search only returns results the caller may see, so
  # it tests authn, not authz. Pick a REAL experiment id (not the placeholder), confirm admin can GET it,
  # then confirm a low-permission user is refused THERE - a 403 from MLflow on the backend, not the proxy:
  printf 'user = "admin:%s"\n' "$1" | curl -q -g -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -H 'Host: mlflow.example.com' \
    --config - "http://127.0.0.1:5000/api/2.0/mlflow/experiments/get?experiment_id=$4"   # do this admin check FIRST: 200 means the experiment exists and admin may read it; a 401/403/404 here means a wrong id or wrong admin credentials, so fix that before trusting the next line
  printf 'user = "%s:%s"\n' "$2" "$3" | curl -q -g -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' -H 'Host: mlflow.example.com' \
    --config - "http://127.0.0.1:5000/api/2.0/mlflow/experiments/get?experiment_id=$4"   # 403: authenticated but not permitted, same real experiment from MLflow (a 401 here means the low-permission credentials are wrong, not authz)
)
```

REASONED: preceding block; listener inventory, external TCP reachability, proxy/backend authentication and experiment authorization follow the cited MLflow host/binding and authentication documentation and curl connection/error write-out reference. No deployed server, external test path, credentials or experiment-permission fixture is available. An authenticated user without permission on a resource gets `403`; a missing or wrong credential gets `401`. The backend authentication and authorization checks above ship marked reasoned, not demonstrated: the authoring environment has no running MLflow basic-auth server, so the exposed and fixed states (anonymous `experiments/search` open versus `401`, and the admin `200` versus low-permission `403` on a real experiment) are not observed here. The expected outcomes are REASONED from the cited MLflow authentication documentation.

## Common mistakes

- Running `--host 0.0.0.0` "for the team" with no `--app-name basic-auth` and no proxy: the whole experiment history is world-writable.
- Bootstrapping the admin account with a weak or shared password (MLflow now requires at least 12 characters and rejects `password1234`, but a guessable value is still a risk).
- Setting `MLFLOW_TRACKING_USERNAME` in CI and assuming the server checks it; without the auth app it is ignored.
- Committing `basic_auth.ini` with `admin_password` or a database password inside it.

## Sources (checked September 2026)

- MLflow CSRF-key file input: [global `--env-file` option and existing-environment precedence](https://mlflow.org/docs/latest/api_reference/cli.html#mlflow), [v3.16.1 auth factory](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/server/auth/__init__.py#L6008-L6021), and [v3.16.1 worker environment](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/server/__init__.py#L401-L402).
- MLflow authentication with username and password (`--app-name basic-auth`, default admin credentials, `basic_auth.ini` keys, `MLFLOW_AUTH_CONFIG_PATH`, `MLFLOW_FLASK_SERVER_SECRET_KEY`, client variables, 403 on missing permission): https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/
- MLflow authentication REST API (`2.0/mlflow/users/update-password` request fields): https://mlflow.org/docs/latest/api_reference/auth/rest-api.html
- `mlflow server` CLI reference (`--host` default 127.0.0.1, `--port` 5000, `--app-name`, `--allowed-hosts`, `--cors-allowed-origins`, `--serve-artifacts`): https://mlflow.org/docs/latest/api_reference/cli.html
- MLflow tracking server (default address, reverse proxy or VPN for TLS and auth, `MLFLOW_TRACKING_TOKEN`, `MLFLOW_TRACKING_INSECURE_TLS`, artifact proxying) (security-middleware flags need MLflow 3.5.0 or newer): https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server
- MLflow REST API, Search Experiments (`POST 2.0/mlflow/experiments/search`): https://mlflow.org/docs/latest/api_reference/rest-api.html
- Docker, port publishing (loopback publishing) (loopback-only reach assumes Docker 28.0.0 or later): https://docs.docker.com/engine/network/port-publishing/
- curl manual (`--connect-timeout` bounds the connection phase only; the `time_connect`, `exitcode`, and `errormsg` write-out variables, the last two added in curl 7.75.0): https://curl.se/docs/manpage.html
- MLflow `--host` option, default `127.0.0.1`, and `--port`, default `5000`, which the `MLFLOW_HOST` and `MLFLOW_PORT` environment variables override (pinned tag v3.16.1): https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/utils/cli_args.py#L162-L180
- MLflow's tracking-server command, `def server`, takes those `--host` and `--port` options (pinned tag v3.16.1): https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L369-L541
- nginx release-1.28.0 proxy directive registration (checked October 2026; `proxy_pass` takes one upstream argument): https://github.com/nginx/nginx/blob/release-1.28.0/src/http/modules/ngx_http_proxy_module.c#L305-L310
- Caddy v2.11.4 `reverse_proxy` parser (checked October 2026): [directive registration](https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L40) and [upstream syntax](https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go#L58-L62).
- iproute2 v6.12.0 `ss` manual (checked October 2026): [numeric output](https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L33-L34), [listening sockets](https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L43-L44), [process display](https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L162-L163), and [TCP sockets](https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L374-L375).
- MLflow v3.16.1 dotenv loader (checked October 2026): [existing-environment precedence](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L85-L86) and [global eager `--env-file` option](https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L94-L105).
