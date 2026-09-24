# MLflow tracking server: no authentication by default

`mlflow server` serves the tracking UI and REST API at `http://127.0.0.1:5000` (unless `MLFLOW_HOST` or `MLFLOW_PORT` is set) and performs no authentication: anyone who can reach the port can read, alter, and delete experiments, runs, registered models, and (with artifact proxying on) the artifacts themselves. Authentication is opt-in through a separate app, and the server has no dedicated TLS flags (though `mlflow server --uvicorn-opts` can forward `--ssl-keyfile`/`--ssl-certfile` to the default Uvicorn server); MLflow's tracking-server documentation recommends a reverse proxy or VPN for both.

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

```bash
pip install 'mlflow[auth]'
export MLFLOW_FLASK_SERVER_SECRET_KEY="REPLACE_WITH_LONG_RANDOM_VALUE"   # CSRF key, required; same value on every replica
MLFLOW_AUTH_CONFIG_PATH=/etc/mlflow/basic_auth.ini mlflow server --app-name basic-auth
```

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

An authenticated user without permission on a resource gets `403`; a missing or wrong credential gets `401`. The backend authentication and authorization checks above ship marked reasoned, not demonstrated: the authoring environment has no running MLflow basic-auth server, so the exposed and fixed states (anonymous `experiments/search` open versus `401`, and the admin `200` versus low-permission `403` on a real experiment) are not observed here. Backlog row 1.76 tracks demonstrating them against a live server.

## Common mistakes

- Running `--host 0.0.0.0` "for the team" with no `--app-name basic-auth` and no proxy: the whole experiment history is world-writable.
- Bootstrapping the admin account with a weak or shared password (MLflow now requires at least 12 characters and rejects `password1234`, but a guessable value is still a risk).
- Setting `MLFLOW_TRACKING_USERNAME` in CI and assuming the server checks it; without the auth app it is ignored.
- Committing `basic_auth.ini` with `admin_password` or a database password inside it.

## Sources (checked September 2026)

- MLflow authentication with username and password (`--app-name basic-auth`, default admin credentials, `basic_auth.ini` keys, `MLFLOW_AUTH_CONFIG_PATH`, `MLFLOW_FLASK_SERVER_SECRET_KEY`, client variables, 403 on missing permission): https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/
- MLflow authentication REST API (`2.0/mlflow/users/update-password` request fields): https://mlflow.org/docs/latest/api_reference/auth/rest-api.html
- `mlflow server` CLI reference (`--host` default 127.0.0.1, `--port` 5000, `--app-name`, `--allowed-hosts`, `--cors-allowed-origins`, `--serve-artifacts`): https://mlflow.org/docs/latest/api_reference/cli.html
- MLflow tracking server (default address, reverse proxy or VPN for TLS and auth, `MLFLOW_TRACKING_TOKEN`, `MLFLOW_TRACKING_INSECURE_TLS`, artifact proxying): https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server
- MLflow REST API, Search Experiments (`POST 2.0/mlflow/experiments/search`): https://mlflow.org/docs/latest/api_reference/rest-api.html
- Docker, port publishing (loopback publishing): https://docs.docker.com/engine/network/port-publishing/
- curl manual (`--connect-timeout` bounds the connection phase only; the `time_connect`, `exitcode`, and `errormsg` write-out variables, the last two added in curl 7.75.0): https://curl.se/docs/manpage.html
- MLflow `--host` option, default `127.0.0.1`, and `--port`, default `5000`, which the `MLFLOW_HOST` and `MLFLOW_PORT` environment variables override (pinned tag v3.16.1): https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/utils/cli_args.py#L162-L180
- MLflow's tracking-server command, `def server`, takes those `--host` and `--port` options (pinned tag v3.16.1): https://github.com/mlflow/mlflow/blob/v3.16.1/mlflow/cli/__init__.py#L369-L541
