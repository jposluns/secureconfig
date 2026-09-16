# MLflow tracking server: no authentication by default

`mlflow server` serves the tracking UI and REST API at `http://127.0.0.1:5000` using the default application `mlflow.server:app`, which performs no authentication: anyone who can reach the port can read, alter, and delete experiments, runs, registered models, and (with artifact proxying on) the artifacts themselves. Authentication is opt-in through a separate app, and the server has no TLS option of its own; MLflow's tracking-server documentation recommends a reverse proxy or VPN for both.

## 1. Bind privately

The defaults are already loopback:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

The CLI help for `--host` says it plainly: "This is NOT a security setting". Do not switch to `--host 0.0.0.0` on a machine with a public interface. In Docker the two binds are different things: the host publishes on loopback (`-p 127.0.0.1:5000:5000`, which Docker's port-publishing docs say only the Docker host can reach, assuming a normal bridge-network NAT setup and a Docker version at or after 28.0.0; earlier releases could let hosts on the same layer-2 network reach a loopback-published port), while inside the container the server must listen on the container's own interface (`--host 0.0.0.0` there, private to the Compose network and the host), because a process bound to the container's `127.0.0.1` is not reachable through the published port at all. See [docker.md](docker.md). If the server must listen beyond loopback for a proxy on another host, set `--allowed-hosts mlflow.example.com` (the default allows localhost and private ranges only) and `--cors-allowed-origins https://mlflow.example.com`, and never use `--disable-security-middleware` outside a test.

## 2. TLS from a fronting proxy

`mlflow server` has no certificate flags. Terminate TLS in nginx or Caddy per [nginx.md](nginx.md)/[caddy.md](caddy.md) with `proxy_pass http://127.0.0.1:5000` or `reverse_proxy 127.0.0.1:5000`, a certificate from [free-certificates.md](free-certificates.md), and `--allowed-hosts` set to the public hostname; or use a tunnel or tailnet ([cloudflare.md](cloudflare.md), [tailscale.md](tailscale.md)). Point clients at `MLFLOW_TRACKING_URI=https://mlflow.example.com`, and never set `MLFLOW_TRACKING_INSECURE_TLS=true` in production (MLflow's own docs say the same).

## 3. Turn on the built-in basic auth

MLflow ships an HTTP basic-auth app that stores users and per-resource permissions in a database (as of September 2026 the current documentation page carries no experimental label; verify before relying on it). The client-side `MLFLOW_TRACKING_USERNAME`/`MLFLOW_TRACKING_PASSWORD` variables do nothing on their own; the server must run this app.

```bash
pip install 'mlflow[auth]'
export MLFLOW_FLASK_SERVER_SECRET_KEY="REPLACE_WITH_LONG_RANDOM_VALUE"   # CSRF key, required; same value on every replica
MLFLOW_AUTH_CONFIG_PATH=/etc/mlflow/basic_auth.ini mlflow server --app-name basic-auth
```

The first start creates an admin user named `admin` with password `password1234`. Set your own admin credentials in the configuration file before that first start so the default password never exists, or change it immediately:

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
curl -q -u admin:password1234 -X PATCH https://mlflow.example.com/api/2.0/mlflow/users/update-password \
     -H 'Content-Type: application/json' \
     -d '{"username":"admin","password":"REPLACE_WITH_LONG_RANDOM_VALUE"}'
```

Creating users requires admin credentials (UI at `/signup`, or `POST /api/2.0/mlflow/users/create`). Give humans individual accounts and CI its own low-permission user per [authentication.md](authentication.md); `~/.mlflow/credentials` stores passwords unencrypted, so prefer the environment variables injected at runtime. The documentation notes that the UI has no limit on login attempts, so rate-limit the login path at the proxy per [nginx.md](nginx.md); and because basic auth sends the password with every request ([authentication.md](authentication.md)), step 2 comes first.

MFA: the basic-auth app has none. Put an identity-aware layer in front (Cloudflare Access, Authelia, oauth2-proxy per [mfa.md](mfa.md)); MLflow clients can pass a proxy bearer token via `MLFLOW_TRACKING_TOKEN`.

## 4. Artifact store credentials

With `--serve-artifacts` (the default) and `--artifacts-destination s3://bucket`, the server proxies every artifact read and write, so it holds the storage credentials and clients need none. Supply them through the environment or an instance role, never in a compose file or the repository ([secrets.md](secrets.md), [object-storage.md](object-storage.md)). With `--no-serve-artifacts`, every client needs its own storage credentials and the tracking server's permissions no longer gate the artifacts.

## Verify

```bash
ss -tlnp   # read every listener; 127.0.0.1 only
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
         -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:5000/" ;;
  esac
)
# experiments/search is a POST endpoint, so each check posts a minimal body
curl -q -sS -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
  https://mlflow.example.com/api/2.0/mlflow/experiments/search                         # 401: no credentials
curl -q -sS -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
  -u admin https://mlflow.example.com/api/2.0/mlflow/experiments/search                # 200 with the new admin password
curl -q -sS -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{"max_results":1}' \
  -u admin:password1234 https://mlflow.example.com/api/2.0/mlflow/experiments/search   # must be 401: default password gone
```

An authenticated user without permission on a resource gets `403`; a missing or wrong credential gets `401`.

## Common mistakes

- Running `--host 0.0.0.0` "for the team" with no `--app-name basic-auth` and no proxy: the whole experiment history is world-writable.
- Leaving `admin` / `password1234` in place after the first start.
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
